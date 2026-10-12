"""Generate the synthetic sample data used by the model.

Savanna Foods Ltd is a made-up company. Every number comes from the rules in this
file, not from a real business. Amounts are in KES millions.

Two files are written:
  data/sample_company_financials.csv          clean history, FY2020 to FY2025
  data/sample_company_financials_flagged.csv  same company, but FY2025 contains
                                              350 of invented sales booked to
                                              receivables. Used to show the
                                              integrity checks catching it.
"""
from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parent.parent / "data"

YEARS = list(range(2020, 2026))
REV_2019 = 3500.0
GROWTH = {2020: 0.086, 2021: 0.11, 2022: 0.09, 2023: 0.12, 2024: 0.08, 2025: 0.09}
COGS_PCT = {2020: 0.630, 2021: 0.620, 2022: 0.625, 2023: 0.615, 2024: 0.620, 2025: 0.612}
SGA_PCT = {2020: 0.170, 2021: 0.172, 2022: 0.168, 2023: 0.170, 2024: 0.166, 2025: 0.165}
DSO = {2019: 45, 2020: 44, 2021: 46, 2022: 45, 2023: 47, 2024: 45, 2025: 44}
DIO, DPO = 60, 50
DEP_RATE, CAPEX_PCT = 0.06, 0.06
TAX, INT_RATE, PAYOUT = 0.30, 0.09, 0.30
OTHER_ASSETS, SHARE_CAPITAL = 150.0, 500.0
DEBT_2019, REPAY, CASH_2019, PPE_2019 = 800.0, 40.0, 300.0, 1000.0


def build(fake_sales: float = 0.0) -> pd.DataFrame:
    rows = []
    rev_prev = REV_2019
    cogs_2019 = rev_prev * 0.63
    ar_prev = rev_prev * DSO[2019] / 365
    inv_prev = cogs_2019 * DIO / 365
    ap_prev = cogs_2019 * DPO / 365
    ppe_prev, debt_prev, cash_prev = PPE_2019, DEBT_2019, CASH_2019
    assets_2019 = cash_prev + ar_prev + inv_prev + ppe_prev + OTHER_ASSETS
    re_prev = assets_2019 - ap_prev - debt_prev - SHARE_CAPITAL

    for y in YEARS:
        base_rev = rev_prev * (1 + GROWTH[y])
        fake = fake_sales if y == YEARS[-1] else 0.0
        rev = base_rev + fake
        cogs = base_rev * COGS_PCT[y]
        sga = base_rev * SGA_PCT[y]
        dep = DEP_RATE * ppe_prev
        ebit = rev - cogs - sga - dep
        interest = INT_RATE * debt_prev
        ebt = ebit - interest
        tax = TAX * ebt
        ni = ebt - tax
        ar = base_rev * DSO[y] / 365 + fake
        inv = cogs * DIO / 365
        ap = cogs * DPO / 365
        capex = CAPEX_PCT * base_rev
        ppe = ppe_prev + capex - dep
        debt = debt_prev - REPAY
        div = PAYOUT * ni
        cfo = ni + dep - (ar - ar_prev) - (inv - inv_prev) + (ap - ap_prev)
        cfi = -capex
        cff = -REPAY - div
        cash = cash_prev + cfo + cfi + cff
        re = re_prev + ni - div
        rows.append(
            dict(
                fiscal_year=y, revenue=rev, cogs=cogs, sga=sga, depreciation=dep,
                interest_expense=interest, tax_expense=tax, net_income=ni,
                cash=cash, receivables=ar, inventory=inv, ppe_net=ppe,
                other_assets=OTHER_ASSETS, payables=ap, long_term_debt=debt,
                share_capital=SHARE_CAPITAL, retained_earnings=re,
                capex=capex, dividends=div, debt_repayment=REPAY,
                cfo=cfo, cfi=cfi, cff=cff,
            )
        )
        rev_prev, ar_prev, inv_prev, ap_prev = base_rev, ar, inv, ap
        ppe_prev, debt_prev, cash_prev, re_prev = ppe, debt, cash, re
    df = pd.DataFrame(rows)
    return df.round(2)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    build().to_csv(OUT / "sample_company_financials.csv", index=False)
    build(fake_sales=350.0).to_csv(OUT / "sample_company_financials_flagged.csv", index=False)
    print("wrote", OUT)
