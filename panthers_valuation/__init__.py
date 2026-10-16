"""Carolina Panthers valuation: DCF, precedent transactions, and private-equity stake returns.

Author: Vincent Huang, UNC Charlotte (BSBA Finance '29).
All team-level financials are Forbes estimates; NFL teams are private.
"""
from .inputs import Inputs
from .dcf import project, dcf_value, sensitivity
from .comps import load_comps, comps_summary, implied_values
from .pe_stake import pe_case, breakeven_growth, breakeven_discount

__all__ = ["Inputs", "project", "dcf_value", "sensitivity", "load_comps", "comps_summary",
           "implied_values", "pe_case", "breakeven_growth", "breakeven_discount"]
