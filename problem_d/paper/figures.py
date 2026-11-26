"""Shared manuscript style and plots derived from the saved screening runs."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
FIG = HERE / "figures"
FIG.mkdir(exist_ok=True)
INK, PAPER, GRID = "#3F4543", "#FFFFFF", "#EEECE7"
SAGE, MIST, BLUE = "#567367", "#AABDB1", "#5D7187"
GRAY, CLAY, OCHRE, PLUM = "#787169", "#9C6963", "#9A8164", "#84738B"
MODELS = (("mixture", "Mixture", SAGE, "o"), ("direct", "Direct", BLUE, "s"))
FAMILIES = ["O3", "NO2", "FO2"]
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.titlesize": 11,
    "axes.titleweight": "semibold", "axes.titlelocation": "left",
    "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": GRAY,
    "axes.labelcolor": INK, "text.color": INK, "xtick.color": INK, "ytick.color": INK,
    "axes.axisbelow": True, "grid.color": GRID, "grid.linewidth": .8,
    "legend.frameon": False, "pdf.fonttype": 42, "mathtext.fontset": "dejavusans",
    "axes.facecolor": PAPER, "figure.facecolor": PAPER,
})


def save(fig, name):
    fig.savefig(FIG / (name + ".pdf"), metadata={"CreationDate": None})
    plt.close(fig)


def budget():
    """Supplementary curves for every pool and both training seeds."""
    fig, axes = plt.subplots(1, 3, figsize=(8, 2.95), layout="constrained")
    for seed in (26, 42):
        records = pd.read_csv(RESULTS / f"validation_seed{seed}.csv")
        pools = (records, records[records.X.eq("NO2")], records[records.X.isin(FAMILIES)])
        for ax, pool, title in zip(axes, pools, ("All families", "Q2: fixed family", "Q3: three families")):
            for key, name, color, marker in MODELS:
                hits = pool.sort_values([key, "id"]).V.iloc[:100].lt(1).cumsum()
                ax.step(np.arange(101), np.r_[0, hits], where="post", color=color,
                        lw=1.5, ls="-" if seed == 26 else "--", marker=marker,
                        markevery=[20, 50, 100], ms=3)
            if seed == 26:
                ax.plot([0, 100], [0, 100 * pool.V.lt(1).mean()], color=GRAY, ls=":")
            ax.set(title=title, xlim=(0, 100), xticks=[0, 20, 50, 100], xlabel="Checks")
            ax.yaxis.get_major_locator().set_params(integer=True)
            ax.grid(axis="y")
    for ax in axes:
        ax.set_ylim(bottom=0)
    handles = [Line2D([], [], color=color, marker=marker, label=name)
               for _, name, color, marker in MODELS]
    handles.extend(Line2D([], [], color=GRAY, ls=style, label=label)
                   for style, label in (("-", "Seed 26"), ("--", "Seed 42"), (":", "Random")))
    fig.legend(handles=handles, loc="outside lower center", ncols=5, fontsize=8.5,
               handlelength=1.6, columnspacing=1.25)
    axes[0].set_ylabel("Cumulative hits ($V<1$)")
    save(fig, "screening")


def single_or_shortlist():
    records = pd.read_csv(RESULTS / "validation_seed26.csv")
    pool = records[records.X.isin(FAMILIES)]
    target_count = int(pool.V.lt(1).sum())
    fig, axes = plt.subplots(1, 2, figsize=(6.3, 2.05), layout="constrained")
    for ax, title, xlabel, limit, ticks in zip(
        axes, ("a   First 50 candidates", "b   First candidate"),
        (f"Near-targets found (of {target_count})", "Regret in observed violation"),
        (6.0, 15.7), ([0, 1, 2, 3, 4, 5], [0, 4, 8, 12])):
        ax.set(title=title, xlabel=xlabel, xlim=(0, limit), xticks=ticks,
               yticks=[1, 0], yticklabels=["Mixture", "Direct"], ylim=(-.55, 1.55))
        ax.grid(axis="x")
        ax.spines["left"].set_visible(False)
        ax.tick_params(axis="y", length=0)
    for y, (key, name, color, marker) in zip([1, 0], MODELS):
        ranked = pool.sort_values([key, "id"])
        hits = ranked.head(50).V.lt(1).sum()
        regret = ranked.iloc[0].V - pool.V.min()
        for ax, value, label in zip(axes, (hits, regret), (str(hits), f"{regret:.5f}")):
            ax.hlines(y, 0, value, color=color, lw=1.6)
            ax.plot(value, y, marker=marker, ms=7, color=color, clip_on=False)
            ax.annotate(label, (value, y), (5, 0), textcoords="offset points",
                        va="center", fontsize=9, color=INK)
    save(fig, "q3_budget")


def precision():
    frame = pd.read_csv(RESULTS / "sdk_precision_audit.csv").query("model == 'mixture'")
    fig, ax = plt.subplots(figsize=(6.4, 2.9), layout="constrained")
    ticks, names = [], []
    for y, row in zip(range(len(frame), 0, -1), frame.itertuples()):
        ax.plot([row.best_original_gap, row.worst_original_gap], [y, y], color=GRAY, lw=2)
        ax.scatter(row.worst_original_gap, y, marker="s", facecolors=PAPER, edgecolors=CLAY, zorder=3)
        ax.scatter(row.best_original_gap, y, color=BLUE, s=20, zorder=4)
        ticks.append(y)
        names.append(("Full range" if row.cap_quantile == 1 else "10th pct. cap") + f", P = {row.penalty:g}")
    winner = pd.read_csv(HERE / "artifacts" / "selections.csv").query("problem == 'Q3'").iloc[0]
    ax.scatter(winner.enum_gap, 0, marker="D", color=SAGE, s=36)
    ax.set(yticks=ticks+[0], yticklabels=names+["Blocks, ties resolved"], xlim=(-.6, 20),
           xlabel="Excess predicted violation on the original Q3 table")
    ax.grid(axis="x")
    ax.legend(handles=[Line2D([], [], marker="o", lw=0, color=BLUE, label="Best tied state"),
                       Line2D([], [], marker="s", lw=0, color=CLAY, markerfacecolor=PAPER,
                              label="Worst tied state")], loc="lower right", fontsize=9)
    save(fig, "precision")


if __name__ == "__main__":
    budget()
    single_or_shortlist()
    precision()
