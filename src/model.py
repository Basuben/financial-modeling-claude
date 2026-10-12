"""Three-statement-lite projection, DCF, sensitivity and trading comps.

Everything runs on the synthetic Savanna Foods Ltd data in /data. Amounts are
KES millions. The logic is deliberately plain so each line can be traced.
"""
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


@dataclass
class Assumptions:
    growth: list = field(default_factory=lambda: [0.085, 0.080, 0.075, 0.070, 0.065])
    cogs_pct: list = field(default_factory=lambda: [0.610, 0.608, 0.606, 0.604, 0.602])
    sga_pct: list = field(default_factory=lambda: [0.165, 0.164, 0.163, 0.162, 0.161])
    dep_rate: float = 0.06        # of opening net PPE
    capex_pct: float = 0.06       # of revenue
    dso: float = 45.0
    dio: float = 60.0
    dpo: float = 50.0
    tax_rate: float = 0.30
    debt_repayment: float = 40.0
    interest_rate: float = 0.09   # on opening debt
    payout: float = 0.30
    wacc: float = 0.13
    terminal_growth: float = 0.05
    shares_m: float = 100.0


def load_history(name: str = "sample_company_financials.csv") -> pd.DataFrame:
    return pd.read_csv(DATA / name).set_index("fiscal_year")


def project(hist: pd.DataFrame, a: Assumptions) -> pd.DataFrame:
    """Project five years forward from the last historical year."""
    last = hist.iloc[-1]
    year0 = int(hist.index[-1])
    prev = dict(
        revenue=last.revenue, ppe=last.ppe_net, debt=last.long_term_debt,
        cash=last.cash, re=last.retained_earnings,
        ar=last.receivables, inv=last.inventory, ap=last.payables,
    )
    rows = []
    for i in range(5):
        rev = prev["revenue"] * (1 + a.growth[i])
        cogs = rev * a.cogs_pct[i]
        sga = rev * a.sga_pct[i]
        ebitda = rev - cogs - sga
        dep = a.dep_rate * prev["ppe"]
        ebit = ebitda - dep
        interest = a.interest_rate * prev["debt"]
        ebt = ebit - interest
        tax = a.tax_rate * ebt
        ni = ebt - tax
        ar = rev * a.dso / 365
        inv = cogs * a.dio / 365
        ap = cogs * a.dpo / 365
        d_nwc = (ar + inv - ap) - (prev["ar"] + prev["inv"] - prev["ap"])
        capex = a.capex_pct * rev
        ppe = prev["ppe"] + capex - dep
        debt = prev["debt"] - a.debt_repayment
        div = a.payout * ni
        cfo = ni + dep - d_nwc
        cash = prev["cash"] + cfo - capex - a.debt_repayment - div
        re = prev["re"] + ni - div
        ufcf = ebit * (1 - a.tax_rate) + dep - capex - d_nwc
        assets = cash + ar + inv + ppe + float(last.other_assets)
        liab_eq = ap + debt + float(last.share_capital) + re
        rows.append(
            dict(
                fiscal_year=year0 + i + 1, revenue=rev, cogs=cogs, sga=sga,
                ebitda=ebitda, depreciation=dep, ebit=ebit, interest=interest,
                ebt=ebt, tax=tax, net_income=ni, receivables=ar, inventory=inv,
                payables=ap, change_nwc=d_nwc, capex=capex, ppe_net=ppe,
                long_term_debt=debt, dividends=div, cfo=cfo, cash=cash,
                retained_earnings=re, ufcf=ufcf,
                balance_check=assets - liab_eq,
            )
        )
        prev = dict(revenue=rev, ppe=ppe, debt=debt, cash=cash, re=re, ar=ar, inv=inv, ap=ap)
    return pd.DataFrame(rows).set_index("fiscal_year")


def dcf(proj: pd.DataFrame, hist: pd.DataFrame, a: Assumptions,
        wacc: float = None, g: float = None) -> dict:
    wacc = a.wacc if wacc is None else wacc
    g = a.terminal_growth if g is None else g
    if wacc <= g:
        raise ValueError("WACC must be above terminal growth")
    t = np.arange(1, len(proj) + 1)
    pv_fcf = (proj["ufcf"].values / (1 + wacc) ** t).sum()
    tv = proj["ufcf"].values[-1] * (1 + g) / (wacc - g)
    pv_tv = tv / (1 + wacc) ** t[-1]
    ev = pv_fcf + pv_tv
    last = hist.iloc[-1]
    net_debt = last.long_term_debt - last.cash
    equity = ev - net_debt
    return dict(
        pv_fcf=pv_fcf, terminal_value=tv, pv_terminal=pv_tv, enterprise_value=ev,
        net_debt=net_debt, equity_value=equity, per_share=equity / a.shares_m,
        tv_share_of_ev=pv_tv / ev,
    )


def sensitivity(proj, hist, a, waccs=None, gs=None) -> pd.DataFrame:
    waccs = waccs if waccs is not None else [0.11, 0.12, 0.13, 0.14, 0.15]
    gs = gs if gs is not None else [0.04, 0.045, 0.05, 0.055, 0.06]
    grid = pd.DataFrame(
        [[dcf(proj, hist, a, w, g)["enterprise_value"] for g in gs] for w in waccs],
        index=[f"{w:.1%}" for w in waccs], columns=[f"{g:.1%}" for g in gs],
    )
    grid.index.name = "WACC \\ g"
    return grid


def comps(hist: pd.DataFrame, a: Assumptions) -> dict:
    peers = pd.read_csv(DATA / "peer_comps.csv")
    peers["ev_ebitda"] = peers.enterprise_value / peers.ebitda
    peers["ev_revenue"] = peers.enterprise_value / peers.revenue
    last = hist.iloc[-1]
    ebitda = last.revenue - last.cogs - last.sga
    net_debt = last.long_term_debt - last.cash

    def implied(metric, base):
        lo, med, hi = np.percentile(peers[metric], [25, 50, 75])
        return {k: v * base for k, v in dict(low=lo, median=med, high=hi).items()}

    ev_e = implied("ev_ebitda", ebitda)
    ev_r = implied("ev_revenue", last.revenue)
    return dict(
        peers=peers, ltm_ebitda=ebitda, net_debt=net_debt,
        ev_ebitda=ev_e, ev_revenue=ev_r,
        per_share={k: (v - net_debt) / a.shares_m for k, v in ev_e.items()},
    )


def football_field(proj, hist, a) -> pd.DataFrame:
    s = sensitivity(proj, hist, a, [a.wacc - 0.01, a.wacc, a.wacc + 0.01],
                    [a.terminal_growth - 0.005, a.terminal_growth, a.terminal_growth + 0.005])
    c = comps(hist, a)
    nd = c["net_debt"]
    rows = [
        ("DCF (WACC +/-1pt, g +/-0.5pt)", s.values.min(), s.values.max()),
        ("EV/EBITDA peers (25th to 75th pct)", c["ev_ebitda"]["low"], c["ev_ebitda"]["high"]),
        ("EV/Revenue peers (25th to 75th pct)", c["ev_revenue"]["low"], c["ev_revenue"]["high"]),
    ]
    df = pd.DataFrame(rows, columns=["method", "ev_low", "ev_high"])
    df["equity_low"] = df.ev_low - nd
    df["equity_high"] = df.ev_high - nd
    df["per_share_low"] = df.equity_low / a.shares_m
    df["per_share_high"] = df.equity_high / a.shares_m
    return df.round(1)


def run_all() -> dict:
    a = Assumptions()
    hist = load_history()
    proj = project(hist, a)
    return dict(a=a, hist=hist, proj=proj, dcf=dcf(proj, hist, a),
                sens=sensitivity(proj, hist, a), comps=comps(hist, a),
                ff=football_field(proj, hist, a))


if __name__ == "__main__":
    r = run_all()
    print(r["proj"].round(1).T)
    print({k: round(v, 3) for k, v in r["dcf"].items()})
    print(r["sens"].round(0))
    print(r["ff"])
