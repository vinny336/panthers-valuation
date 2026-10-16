"""Ten-year owner cash-flow projection and valuation (2026-2035)."""
import numpy as np
import pandas as pd
from .inputs import Inputs

YEARS = list(range(2026, 2036))


def project(inp: Inputs) -> pd.DataFrame:
    """Return a year-indexed DataFrame of the projection, 2025A through 2035E, in $mm."""
    rows = []
    nat, loc = inp.national_rev_2025, inp.local_rev_2025
    ply, opx = inp.player_costs_2025, inp.other_opex_2025
    rows.append(dict(year=2025, national=nat, local=loc, player=-ply, other_opex=-opx))
    for y in YEARS:
        g = inp.national_growth_early if y <= 2029 else inp.national_growth_late
        nat = nat * (1 + g) * (1 + (inp.media_uplift_2030 if y == 2030 else 0))
        loc = loc * (1 + inp.local_growth) * (1 + (inp.renovation_uplift if y == inp.renovation_year else 0))
        ply = ply * (1 + inp.national_growth_early)  # player costs track the salary cap (same as the Excel model)
        opx = opx * (1 + inp.other_opex_growth)
        rows.append(dict(year=y, national=nat, local=loc, player=-ply, other_opex=-opx))
    df = pd.DataFrame(rows).set_index("year")
    df["revenue"] = df.national + df.local
    df["ebitda"] = df.revenue + df.player + df.other_opex
    df["margin"] = df.ebitda / df.revenue
    df["tax"] = -np.maximum(df.ebitda, 0) * inp.tax_rate
    df["maint_capex"] = -inp.maint_capex
    df["stadium_capex"] = [-(inp.stadium_capex_2026_2029 if y <= 2029 else inp.stadium_capex_2030_2035) for y in df.index]
    df.loc[2025, ["tax", "maint_capex", "stadium_capex"]] = 0.0
    df["fcf"] = df.ebitda + df.tax + df.maint_capex + df.stadium_capex
    df.loc[2025, "fcf"] = np.nan
    df["t"] = df.index - 2025
    return df


def dcf_value(inp: Inputs, df: pd.DataFrame | None = None, rate: float | None = None,
              exit_multiple: float | None = None, terminal_growth: float | None = None) -> dict:
    """Enterprise value under both terminal methods. Returns a dict of the pieces."""
    df = project(inp) if df is None else df
    r = inp.discount_rate if rate is None else rate
    m = inp.exit_multiple if exit_multiple is None else exit_multiple
    g = inp.terminal_growth if terminal_growth is None else terminal_growth
    proj = df.loc[YEARS]
    disc = 1 / (1 + r) ** proj.t
    pv_fcf = float((proj.fcf * disc).sum())
    rev_n, fcf_n, disc_n = proj.revenue.iloc[-1], proj.fcf.iloc[-1], disc.iloc[-1]
    tv_exit = rev_n * m
    tv_gordon = fcf_n * (1 + g) / (r - g)
    ev_exit = pv_fcf + tv_exit * disc_n
    ev_gordon = pv_fcf + tv_gordon * disc_n
    return dict(pv_fcf=pv_fcf, tv_exit=tv_exit, ev_exit=ev_exit, tv_gordon=tv_gordon, ev_gordon=ev_gordon,
                ev_exit_multiple_of_2025_rev=ev_exit / inp.revenue_2025,
                scarcity_premium=inp.forbes_value / ev_gordon)


def sensitivity(inp: Inputs, rates=(0.07, 0.08, 0.09, 0.10), multiples=(10, 11, 12, 13, 14),
                growths=(0.03, 0.035, 0.04, 0.045, 0.05)) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Two grids of enterprise value: (discount rate x exit multiple) and (discount rate x terminal growth)."""
    df = project(inp)
    ex = pd.DataFrame({m: [dcf_value(inp, df, r, exit_multiple=m)["ev_exit"] for r in rates] for m in multiples}, index=rates)
    go = pd.DataFrame({g: [dcf_value(inp, df, r, terminal_growth=g)["ev_gordon"] for r in rates] for g in growths}, index=rates)
    ex.index.name = go.index.name = "discount_rate"
    return ex, go
