"""Returns on a minority (3-10%) private-equity stake under the NFL's 2024 rules."""
import pandas as pd
from .inputs import Inputs


def pe_case(inp: Inputs, appreciation: float, fcf_2026_2031_sum: float) -> dict:
    """One scenario. Returns entry, exit, distributions, MOIC and an exit-weighted IRR."""
    equity = inp.equity_value
    entry = equity * (1 - inp.lp_discount) * inp.stake
    exit_equity = equity * (1 + appreciation) ** inp.hold_years
    exit_proceeds = exit_equity * (1 - inp.exit_discount) * inp.stake
    distributions = fcf_2026_2031_sum * inp.stake * inp.distribution_share
    moic = (exit_proceeds + distributions) / entry
    irr = moic ** (1 / inp.hold_years) - 1
    return dict(appreciation=appreciation, entry=entry, exit_equity_100pct=exit_equity, exit_proceeds=exit_proceeds,
                distributions=distributions, moic=moic, irr=irr, clears_hurdle=irr >= inp.target_irr)


def pe_table(inp: Inputs, fcf_2026_2031_sum: float) -> pd.DataFrame:
    return pd.DataFrame({k: pe_case(inp, g, fcf_2026_2031_sum) for k, g in inp.appreciation.items()})


def breakeven_growth(inp: Inputs) -> float:
    """Annual appreciation needed to hit the target IRR, ignoring distributions."""
    equity = inp.equity_value
    entry = equity * (1 - inp.lp_discount) * inp.stake
    needed = (1 + inp.target_irr) ** inp.hold_years * entry
    return (needed / ((1 - inp.exit_discount) * inp.stake * equity)) ** (1 / inp.hold_years) - 1


def breakeven_discount(inp: Inputs, appreciation: float, fcf_2026_2031_sum: float) -> float:
    """Entry LP discount needed to hit the target IRR at a given appreciation rate."""
    equity = inp.equity_value
    exit_proceeds = equity * (1 + appreciation) ** inp.hold_years * (1 - inp.exit_discount) * inp.stake
    distributions = fcf_2026_2031_sum * inp.stake * inp.distribution_share
    max_entry = (exit_proceeds + distributions) / (1 + inp.target_irr) ** inp.hold_years
    return 1 - max_entry / (equity * inp.stake)
