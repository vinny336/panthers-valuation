"""Every assumption in one place. Values are $ millions unless stated. Each field notes its source."""
from dataclasses import dataclass, field, asdict


@dataclass
class Inputs:
    # --- Market data, 2025 season (Forbes, Sept 2026) ---
    forbes_value: float = 8100.0       # Forbes NFL Team Valuations 2026, #26 of 32
    sportico_value: float = 8070.0     # Sportico 2026 via Charlotte Business Journal
    revenue_2025: float = 646.0        # Forbes; net of stadium debt service, excludes playoffs
    ebitda_2025: float = 88.0          # Forbes operating income
    player_costs_2025: float = 366.0   # Forbes; includes benefits and bonuses
    debt_pct_of_value: float = 0.02    # Forbes
    tepper_price_2018: float = 2280.0  # Forbes
    league_avg_value: float = 9500.0   # Forbes 2026 average
    league_avg_ev_rev: float = 13.4    # Forbes 2026 average EV / trailing revenue

    # --- Revenue split (assumption) ---
    national_rev_2025: float = 455.0   # Sportico: ">$450mm" per team in 2025. ASSUMPTION

    # --- Growth ---
    national_growth_early: float = 0.06    # 2026-2029; current media deal steps up ~5-7%/yr
    media_uplift_2030: float = 0.10        # one-time step-up after the 2029 opt-out. ASSUMPTION
    national_growth_late: float = 0.05     # 2030-2035
    local_growth: float = 0.03
    renovation_uplift: float = 0.20        # one-time lift to local revenue. ASSUMPTION
    renovation_year: int = 2028
    other_opex_growth: float = 0.03

    # --- Cash flow & discounting ---
    tax_rate: float = 0.25                 # owner-level approximation. ASSUMPTION
    maint_capex: float = 10.0
    stadium_capex_2026_2029: float = 37.5  # $150mm over four years (WFAE, June 2024)
    stadium_capex_2030_2035: float = 38.0  # ~$420mm committed 2029-2039 (WFAE)
    discount_rate: float = 0.08            # ASSUMPTION; range 7-10%
    exit_multiple: float = 12.0            # EV / revenue; below the 13.4x league average
    terminal_growth: float = 0.04

    # --- PE stake case ---
    stake: float = 0.10                    # NFL maximum PE stake
    lp_discount: float = 0.20              # ASSUMPTION; reported 15-30%
    hold_years: int = 6                    # NFL minimum hold
    appreciation: dict = field(default_factory=lambda: {"Bear": 0.05, "Base": 0.10, "Bull": 0.15})
    exit_discount: float = 0.10            # ASSUMPTION: discount narrows at exit
    distribution_share: float = 0.5        # share of FCF paid out during the hold. ASSUMPTION
    target_irr: float = 0.15

    # --- Derived ---
    @property
    def local_rev_2025(self) -> float:
        return self.revenue_2025 - self.national_rev_2025

    @property
    def other_opex_2025(self) -> float:
        return self.revenue_2025 - self.player_costs_2025 - self.ebitda_2025

    @property
    def equity_value(self) -> float:
        return self.forbes_value * (1 - self.debt_pct_of_value)

    def to_dict(self) -> dict:
        return asdict(self)
