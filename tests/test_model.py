import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import integrity_checks as ic  # noqa: E402
import model  # noqa: E402


@pytest.fixture(scope="module")
def r():
    return model.run_all()


def test_projected_balance_sheet_balances(r):
    # Opening data is rounded to 2 decimals, so allow a few cents.
    assert r["proj"]["balance_check"].abs().max() < 0.5


def test_revenue_grows_at_assumed_rate(r):
    hist_last = r["hist"].revenue.iloc[-1]
    assert r["proj"].revenue.iloc[0] == pytest.approx(hist_last * 1.085)


def test_dcf_adds_up(r):
    d = r["dcf"]
    assert d["enterprise_value"] == pytest.approx(d["pv_fcf"] + d["pv_terminal"])
    assert d["equity_value"] == pytest.approx(d["enterprise_value"] - d["net_debt"])


def test_higher_wacc_lowers_value(r):
    s = r["sens"]
    assert (s.diff().dropna() < 0).all().all()


def test_higher_growth_raises_value(r):
    s = r["sens"]
    assert (s.diff(axis=1).dropna(axis=1) > 0).all().all()


def test_wacc_must_exceed_growth(r):
    with pytest.raises(ValueError):
        model.dcf(r["proj"], r["hist"], r["a"], wacc=0.04, g=0.05)


def test_clean_data_has_no_red_flags():
    df = model.load_history()
    res = ic.run_checks(df)
    assert res.balance_ok.all() and res.cash_ties.all() and res.re_ok.all()
    assert (res.red_flags == 0).all()


def test_invented_sales_are_caught():
    df = model.load_history("sample_company_financials_flagged.csv")
    res = ic.run_checks(df)
    assert res.loc[2025, "dso_flag"]
    assert res.loc[2025, "conversion_flag"]
    assert res.loc[2025, "red_flags"] >= 2
    assert res.loc[:2024, "red_flags"].sum() == 0


def test_football_field_ranges_are_ordered(r):
    ff = r["ff"]
    assert (ff.ev_low < ff.ev_high).all()
