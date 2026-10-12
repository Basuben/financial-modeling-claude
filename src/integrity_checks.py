"""Integrity checks on a set of financial statements.

These are screening tests, the same kind of questions a fraud analyst asks of a
transaction file, pointed at a model's inputs. A flag means "look closer", not
"this is fraud".

Checks, per fiscal year:
  1. Balance sheet balances.
  2. Cash flow statement ties to the movement in cash.
  3. Retained earnings roll forward correctly.
  4. Days sales outstanding (DSO) jump versus the prior year.
  5. Cash conversion: operating cash flow against net income.
  6. Beneish M-score (8 variable version). Above -1.78 is a common flag level.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
TOL = 0.5            # KES millions, covers rounding in the CSV
DSO_JUMP = 0.15      # flag if DSO rises more than 15% in a year
CASH_CONVERSION_MIN = 0.80
M_SCORE_FLAG = -1.78


def beneish(df: pd.DataFrame) -> pd.Series:
    """Eight variable Beneish M-score. Needs a prior year, so the first year is NaN."""
    d = df.copy()
    d["ca"] = d.cash + d.receivables + d.inventory
    d["ta"] = d.ca + d.ppe_net + d.other_assets
    d["cl"] = d.payables
    p = d.shift(1)
    dsri = (d.receivables / d.revenue) / (p.receivables / p.revenue)
    gm = (d.revenue - d.cogs) / d.revenue
    gm_p = (p.revenue - p.cogs) / p.revenue
    gmi = gm_p / gm
    aq = 1 - (d.ca + d.ppe_net) / d.ta
    aq_p = 1 - (p.ca + p.ppe_net) / p.ta
    aqi = aq / aq_p
    sgi = d.revenue / p.revenue
    depi = (p.depreciation / (p.depreciation + p.ppe_net)) / (d.depreciation / (d.depreciation + d.ppe_net))
    sgai = (d.sga / d.revenue) / (p.sga / p.revenue)
    lvgi = ((d.cl + d.long_term_debt) / d.ta) / ((p.cl + p.long_term_debt) / p.ta)
    tata = (d.net_income - d.cfo) / d.ta
    m = (-4.84 + 0.920 * dsri + 0.528 * gmi + 0.404 * aqi + 0.892 * sgi
         + 0.115 * depi - 0.172 * sgai + 4.679 * tata - 0.327 * lvgi)
    return m.rename("m_score")


def run_checks(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    out = pd.DataFrame(index=d.index)
    assets = d.cash + d.receivables + d.inventory + d.ppe_net + d.other_assets
    liab_eq = d.payables + d.long_term_debt + d.share_capital + d.retained_earnings
    out["balance_gap"] = (assets - liab_eq).round(2)
    out["balance_ok"] = out.balance_gap.abs() <= TOL

    cash_move = d.cash.diff()
    cf_total = d.cfo + d.cfi + d.cff
    out["cash_gap"] = (cash_move - cf_total).round(2)
    out["cash_ties"] = out.cash_gap.abs().le(TOL) | cash_move.isna()

    re_roll = d.retained_earnings.shift(1) + d.net_income - d.dividends
    out["re_gap"] = (d.retained_earnings - re_roll).round(2)
    out["re_ok"] = out.re_gap.abs().le(TOL) | re_roll.isna()

    dso = d.receivables / d.revenue * 365
    out["dso"] = dso.round(1)
    out["dso_change"] = dso.pct_change().round(3)
    out["dso_flag"] = out.dso_change > DSO_JUMP

    out["cash_conversion"] = (d.cfo / d.net_income).round(2)
    out["conversion_flag"] = out.cash_conversion < CASH_CONVERSION_MIN

    out["m_score"] = beneish(d).round(2)
    out["m_flag"] = out.m_score > M_SCORE_FLAG
    flags = ["dso_flag", "conversion_flag", "m_flag"]
    out["red_flags"] = out[flags].sum(axis=1)
    return out


def report(name: str, df: pd.DataFrame) -> str:
    r = run_checks(df)
    cols = ["balance_ok", "cash_ties", "re_ok", "dso", "dso_change",
            "cash_conversion", "m_score", "red_flags"]
    lines = [f"### {name}", "", "| FY | " + " | ".join(cols) + " |",
             "|---|" + "---|" * len(cols)]
    for fy, row in r[cols].iterrows():
        cells = ["" if pd.isna(v) else str(v) for v in row.values]
        lines.append(f"| {fy} | " + " | ".join(cells) + " |")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    data = ROOT / "data"
    clean = pd.read_csv(data / "sample_company_financials.csv").set_index("fiscal_year")
    flagged = pd.read_csv(data / "sample_company_financials_flagged.csv").set_index("fiscal_year")
    text = "\n".join([
        "# Integrity check report", "",
        "Screening tests only. A flag means look closer, not that fraud occurred.", "",
        report("Clean sample", clean), report("Sample with 350 of invented FY2025 sales", flagged),
    ])
    (ROOT / "outputs").mkdir(exist_ok=True)
    (ROOT / "outputs" / "integrity_report.md").write_text(text)
    print(text)
