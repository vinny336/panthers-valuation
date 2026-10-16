"""Charts for the write-up. Each function saves a PNG and returns the path."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd
from .inputs import Inputs

NAVY, GOLD, GREY, LIGHT = "#1F3864", "#C9A227", "#595959", "#8EA9DB"
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
_bn = FuncFormatter(lambda x, _: f"${x/1000:.0f}bn")


def football_field(ranges: list[tuple[str, float, float]], inp: Inputs, my_range: tuple[float, float], out: Path) -> Path:
    fig, ax = plt.subplots(figsize=(11, 5.6), dpi=150)
    ys = list(range(len(ranges)))[::-1]
    for y, (name, lo, hi) in zip(ys, ranges):
        w = max(hi - lo, 120)
        ax.barh(y, w, left=lo, height=0.55, color=GOLD if "perpetuity" in name else NAVY)
        ax.text(lo - 120, y, f"${lo/1000:.1f}bn", va="center", ha="right", fontsize=9.5, color=GREY)
        ax.text(lo + w + 120, y, f"${hi/1000:.1f}bn", va="center", ha="left", fontsize=9.5, color=GREY)
    ax.axvline(inp.forbes_value, color="#C00000", ls="--", lw=1.3)
    ax.text(inp.forbes_value + 150, len(ranges) - 0.45, f"Forbes ${inp.forbes_value/1000:.1f}bn", color="#C00000", fontsize=9.5)
    ax.axvspan(*my_range, color=LIGHT, alpha=0.25)
    ax.text(my_range[0] - 100, len(ranges) - 0.45, f"My range ${my_range[0]/1000:.1f}–{my_range[1]/1000:.1f}bn", ha="right", fontsize=9.5, color=NAVY)
    ax.set_yticks(ys); ax.set_yticklabels([r[0] for r in ranges], fontsize=10)
    ax.xaxis.set_major_formatter(_bn); ax.set_xlim(0, 12500); ax.set_ylim(-0.6, len(ranges) - 0.1)
    ax.set_title("Carolina Panthers: enterprise value by method", loc="left", fontsize=14, fontweight="bold", color=NAVY)
    plt.tight_layout(); fig.savefig(out); plt.close(fig); return out


def history(hist: pd.DataFrame, out: Path) -> Path:
    fig, ax = plt.subplots(figsize=(11, 5), dpi=150)
    yrs = hist.season.astype(str)
    ax.bar(yrs, hist.value_mm, color=NAVY, width=0.6, label="Team value (Forbes)")
    ax2 = ax.twinx(); ax2.plot(yrs, hist.revenue_mm, color=GOLD, marker="o", lw=2.5, label="Revenue"); ax2.spines["top"].set_visible(False)
    ax.yaxis.set_major_formatter(_bn); ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"${x:.0f}mm")); ax2.set_ylim(0, 900)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels(); ax.legend(h1 + h2, l1 + l2, loc="upper left", frameon=False)
    ax.set_title("Value compounded ~17%/yr while revenue grew ~6%/yr", loc="left", fontsize=13, fontweight="bold", color=NAVY)
    plt.tight_layout(); fig.savefig(out); plt.close(fig); return out


def pe_irr(table: pd.DataFrame, inp: Inputs, out: Path) -> Path:
    fig, ax = plt.subplots(figsize=(11, 5), dpi=150)
    labels = [f"{k}\n{v:.0%}/yr value growth" for k, v in inp.appreciation.items()]
    irr = [table[k]["irr"] * 100 for k in inp.appreciation]
    bars = ax.bar(labels, irr, color=[GREY, NAVY, GOLD], width=0.5)
    for b, x, k in zip(bars, irr, inp.appreciation):
        ax.text(b.get_x() + b.get_width() / 2, x + 0.5, f"{x:.1f}% IRR\n{table[k]['moic']:.1f}x MOIC", ha="center", fontsize=10.5, fontweight="bold")
    ax.axhline(inp.target_irr * 100, color="#C00000", ls="--", lw=1.3); ax.text(2.35, inp.target_irr * 100 + 0.4, f"{inp.target_irr:.0%} PE hurdle", color="#C00000", ha="right", fontsize=9.5)
    ax.set_ylim(0, max(irr) + 5); ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax.set_title(f"A {inp.stake:.0%} PE stake: IRR by appreciation scenario", loc="left", fontsize=13, fontweight="bold", color=NAVY)
    plt.tight_layout(); fig.savefig(out); plt.close(fig); return out


def sensitivity_heatmap(grid: pd.DataFrame, title: str, col_fmt: str, out: Path) -> Path:
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=150)
    im = ax.imshow(grid.values / 1000, cmap="Blues", aspect="auto")
    ax.set_xticks(range(len(grid.columns))); ax.set_xticklabels([col_fmt.format(c) for c in grid.columns])
    ax.set_yticks(range(len(grid.index))); ax.set_yticklabels([f"{r:.0%}" for r in grid.index]); ax.set_ylabel("Discount rate")
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            v = grid.values[i, j] / 1000
            ax.text(j, i, f"${v:.1f}bn", ha="center", va="center", fontsize=9, color="white" if v > grid.values.max() / 1000 * 0.75 else "black")
    ax.set_title(title, loc="left", fontsize=12, fontweight="bold", color=NAVY)
    for s in ax.spines.values(): s.set_visible(False)
    plt.tight_layout(); fig.savefig(out); plt.close(fig); return out
