"""Checks that the Python model reproduces the Excel model (Panthers_Valuation_Model.xlsx) to within rounding."""
import pytest
from panthers_valuation import Inputs, project, dcf_value, load_comps, comps_summary
from panthers_valuation.pe_stake import pe_table, breakeven_growth

inp = Inputs()
df = project(inp)


def test_revenue_split_reconciles():
    assert inp.local_rev_2025 + inp.national_rev_2025 == inp.revenue_2025
    assert df.loc[2025, "ebitda"] == pytest.approx(inp.ebitda_2025)


def test_projection_matches_excel():
    assert df.loc[2035, "revenue"] == pytest.approx(1155, abs=1)
    assert df.loc[2035, "ebitda"] == pytest.approx(241, abs=1)
    assert df.loc[2030, "fcf"] == pytest.approx(115, abs=1)


def test_dcf_matches_excel():
    v = dcf_value(inp, df)
    assert v["ev_exit"] == pytest.approx(6980, abs=5)
    assert v["ev_gordon"] == pytest.approx(2163, abs=5)
    assert v["scarcity_premium"] == pytest.approx(3.74, abs=0.02)


def test_comps_match_excel():
    s = comps_summary(load_comps())
    assert s["median"] == pytest.approx(12.71, abs=0.01)
    assert s["low"] == pytest.approx(8.84, abs=0.01)
    assert s["high"] == pytest.approx(17.32, abs=0.01)


def test_pe_matches_excel():
    fcf_6 = df.loc[2026:2031, "fcf"].sum()
    pe = pe_table(inp, fcf_6)
    assert pe["Base"]["entry"] == pytest.approx(635.04, abs=0.1)
    assert pe["Base"]["irr"] == pytest.approx(0.1248, abs=0.001)
    assert pe["Bear"]["irr"] == pytest.approx(0.0746, abs=0.001)
    assert pe["Bull"]["irr"] == pytest.approx(0.1752, abs=0.001)
    assert breakeven_growth(inp) == pytest.approx(0.1276, abs=0.001)


def test_inputs_move_the_answer():
    base = dcf_value(inp)["ev_exit"]
    no_media = dcf_value(Inputs(media_uplift_2030=0.0))["ev_exit"]
    assert no_media < base
    assert dcf_value(Inputs(discount_rate=0.10))["ev_exit"] < base
