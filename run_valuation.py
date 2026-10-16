"""Run the full valuation and write tables + charts to ./output. Usage: python run_valuation.py"""
from pathlib import Path
import pandas as pd
from panthers_valuation import Inputs, project, dcf_value, sensitivity, load_comps, comps_summary, implied_values
from panthers_valuation.pe_stake import pe_table, breakeven_growth, breakeven_discount
from panthers_valuation import charts

OUT = Path(__file__).parent / "output"; OUT.mkdir(exist_ok=True)
pd.set_option("display.float_format", lambda x: f"{x:,.1f}")


def main(inp: Inputs = Inputs()) -> dict:
    df = project(inp)
    val = dcf_value(inp, df)
    ex, go = sensitivity(inp)
    comps = load_comps(); summ = comps_summary(comps); implied = implied_values(inp, summ)
    fcf_6 = df.loc[2026:2031, "fcf"].sum()
    pe = pe_table(inp, fcf_6)
    be_g = breakeven_growth(inp); be_d = breakeven_discount(inp, inp.appreciation["Base"], fcf_6)
    hist = pd.read_csv(Path(__file__).parent / "data" / "panthers_history.csv")

    ranges = [
        ("Published valuations\n(Forbes / Sportico)", inp.sportico_value, inp.forbes_value),
        ("Precedent deals\n(min – median)", implied.loc["low", "implied_ev_mm"], implied.loc["median", "implied_ev_mm"]),
        ("Precedent deals\n(median – max)", implied.loc["median", "implied_ev_mm"], implied.loc["high", "implied_ev_mm"]),
        ("DCF, exit multiple\n(7–10%, 10–14x)", ex.values.min(), ex.values.max()),
        ("DCF, perpetuity growth\n(cash flows only)", go.values.min(), go.values.max()),
        ("PE entry price\n(after LP discount)", inp.equity_value * (1 - inp.lp_discount), inp.equity_value),
    ]
    charts.football_field(ranges, inp, (7100, 8300), OUT / "football_field.png")
    charts.history(hist, OUT / "history.png")
    charts.pe_irr(pe, inp, OUT / "pe_irr.png")
    charts.sensitivity_heatmap(ex, "EV ($bn): discount rate × exit multiple", "{:.0f}x", OUT / "sens_exit.png")
    charts.sensitivity_heatmap(go, "EV ($bn): discount rate × terminal growth", "{:.1%}", OUT / "sens_gordon.png")

    df.to_csv(OUT / "projection.csv"); comps.to_csv(OUT / "comps.csv", index=False); pe.to_csv(OUT / "pe_scenarios.csv")
    ex.to_csv(OUT / "sensitivity_exit_multiple.csv"); go.to_csv(OUT / "sensitivity_gordon.csv")

    print("=== Carolina Panthers valuation (all $mm) ===")
    print(f"Forbes value                 {inp.forbes_value:>10,.0f}")
    print(f"DCF, exit multiple ({inp.exit_multiple:.0f}x)     {val['ev_exit']:>10,.0f}   ({val['ev_exit_multiple_of_2025_rev']:.1f}x 2025 revenue)")
    print(f"DCF, perpetuity growth       {val['ev_gordon']:>10,.0f}   (market pays {val['scarcity_premium']:.1f}x cash-flow value)")
    print(f"Comps median multiple        {summ['median']:>10.1f}x  -> implied {implied.loc['median','implied_ev_mm']:,.0f}")
    print("\n=== 10% PE stake ===")
    print(pe.loc[["entry", "exit_proceeds", "moic", "irr", "clears_hurdle"]].T.to_string())
    print(f"\nBreak-even appreciation for {inp.target_irr:.0%} IRR: {be_g:.1%}/yr")
    print(f"Break-even entry discount at {inp.appreciation['Base']:.0%}/yr growth: {be_d:.0%}")
    print(f"\nCharts and CSVs written to {OUT}")
    return dict(projection=df, valuation=val, sens_exit=ex, sens_gordon=go, comps=comps, implied=implied, pe=pe,
                breakeven_growth=be_g, breakeven_discount=be_d)


if __name__ == "__main__":
    main()
