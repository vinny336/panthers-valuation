"""Precedent NFL transactions, 2022-2026, and the Panthers values they imply."""
from pathlib import Path
import pandas as pd
from .inputs import Inputs

DATA = Path(__file__).resolve().parent.parent / "data" / "nfl_transactions.csv"


def load_comps(path: Path = DATA) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["ev_rev"] = df.implied_value_mm / df.trailing_revenue_mm
    return df


def comps_summary(df: pd.DataFrame) -> pd.Series:
    minority = df[df.type.str.contains("inority")]
    return pd.Series({
        "control_mean": df[df.type == "Control"].ev_rev.mean(),
        "minority_pe_mean": minority.ev_rev.mean(),
        "median": df.ev_rev.median(),
        "low": df.ev_rev.min(),
        "high": df.ev_rev.max(),
    })


def implied_values(inp: Inputs, summary: pd.Series) -> pd.DataFrame:
    rows = {k: v * inp.revenue_2025 for k, v in summary.items()}
    rows["league_average"] = inp.league_avg_ev_rev * inp.revenue_2025
    out = pd.DataFrame({"ev_rev": {**summary.to_dict(), "league_average": inp.league_avg_ev_rev}, "implied_ev_mm": rows})
    out["equity_mm"] = out.implied_ev_mm * (1 - inp.debt_pct_of_value)
    out["vs_forbes"] = out.implied_ev_mm / inp.forbes_value - 1
    return out
