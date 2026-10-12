"""Write outputs/valuation_summary.md from the model."""
from pathlib import Path

from model import run_all

ROOT = Path(__file__).resolve().parent.parent


def fmt(x, d=0):
    return f"{x:,.{d}f}"


def md_table(df, d=0, index_name=""):
    cols = list(df.columns)
    lines = [f"| {index_name} | " + " | ".join(str(c) for c in cols) + " |",
             "|---|" + "---|" * len(cols)]
    for idx, row in df.iterrows():
        lines.append(f"| {idx} | " + " | ".join(fmt(v, d) for v in row.values) + " |")
    return "\n".join(lines)


def build() -> str:
    r = run_all()
    p, d, a = r["proj"], r["dcf"], r["a"]
    show = p[["revenue", "ebitda", "ebit", "net_income", "ufcf", "cash"]].round(0)
    show.columns = ["Revenue", "EBITDA", "EBIT", "Net income", "Unlevered FCF", "Cash"]
    c = r["comps"]
    ff = r["ff"]
    lines = [
        "# Savanna Foods Ltd (fictional): valuation summary", "",
        "All figures are KES millions unless stated. The company and peers are made up.", "",
        "## Projections", "", md_table(show.T, 0, "FY"), "",
        "## DCF", "",
        f"- WACC {a.wacc:.1%}, terminal growth {a.terminal_growth:.1%}",
        f"- Enterprise value: {fmt(d['enterprise_value'])}",
        f"- Net debt (negative means net cash): {fmt(d['net_debt'])}",
        f"- Equity value: {fmt(d['equity_value'])}",
        f"- Value per share: KES {fmt(d['per_share'], 2)}",
        f"- Terminal value is {d['tv_share_of_ev']:.0%} of enterprise value, so the answer leans on the terminal assumptions.", "",
        "## Sensitivity: enterprise value", "", md_table(r["sens"], 0, "WACC \\ g"), "",
        "## Trading comps (fictional peers)", "",
        f"- Median EV/EBITDA {c['peers'].ev_ebitda.median():.1f}x, median EV/Revenue {c['peers'].ev_revenue.median():.2f}x",
        f"- FY2025 EBITDA {fmt(c['ltm_ebitda'])}", "",
        "## Football field", "",
        "| Method | EV low | EV high | Per share low | Per share high |", "|---|---|---|---|---|",
    ]
    for _, row in ff.iterrows():
        lines.append(f"| {row.method} | {fmt(row.ev_low)} | {fmt(row.ev_high)} | "
                     f"{fmt(row.per_share_low, 1)} | {fmt(row.per_share_high, 1)} |")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    text = build()
    (ROOT / "outputs").mkdir(exist_ok=True)
    (ROOT / "outputs" / "valuation_summary.md").write_text(text)
    print(text)
