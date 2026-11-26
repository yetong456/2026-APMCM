"""Draw physical, validation and finite-precision diagnostics from the archived runs."""
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, LogNorm
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd

from figures import (BLUE, CLAY, FAMILIES, GRAY, GRID, HERE, INK, MIST, OCHRE,
                     PAPER, RESULTS, SAGE, save)

DATA = HERE.parent / "date"
ART = HERE / "artifacts"
FAMILY_LABELS = [r"$\mathrm{O_3}$", r"$\mathrm{NO_2}$", r"$\mathrm{FO_2}$"]
DENSITY = LinearSegmentedColormap.from_list("sage_scale", [GRID, MIST, SAGE])


def physical(public):
    metal = public[public.gap.eq(0)]
    assert (metal.vbm == metal.cbm).all()
    fig, ax = plt.subplots(figsize=(6.3, 2.35), layout="constrained")
    cells = ax.hexbin(metal.vbm, metal.V, gridsize=(48, 21), extent=(3.5, 6.8, 6, 60),
                      mincnt=1, norm=LogNorm(), cmap=DENSITY, linewidths=0)
    colorbar = fig.colorbar(cells, ax=ax, pad=.025, label="Records per hexagon")
    colorbar.solids.set_rasterized(False)
    t = np.linspace(3.5, 6.8, 301)
    lower = 7.84 + (np.maximum(5.73-t, 0)/.5)**2 + (np.maximum(t-4.50, 0)/.5)**2
    ax.plot(t, lower, color=CLAY, lw=1.8, label="Zero formation penalty")
    ax.plot(5.115, 10.8658, marker="D", ms=5, color=INK)
    ax.annotate("Minimum 10.8658", (5.115, 10.8658), (5.5, 31), color=INK,
                arrowprops={"arrowstyle":"-", "color":INK, "lw":.8})
    ax.set(xlim=(3.5, 6.8), ylim=(6, 60), xlabel="Coincident band edge (eV)",
           ylabel="Observed violation $V$")
    ax.legend(loc="upper left", fontsize=9)
    save(fig, "physical_regimes")


def site_pair_audit(public):
    swapped = public[["A","B","X","V"]].rename(columns={"A":"B","B":"A","V":"reversed"})
    pairs = public.merge(swapped, on=["A","B","X"], validate="one_to_one").query("A < B")
    diff = np.abs(pairs.V - pairs.reversed)
    print("Site-exchange pairs", len(pairs), "quartiles", diff.quantile([.25,.5,.75]).to_list(),
          "site-invariant MAE floor", diff.mean()/2)


def stability():
    # Paired cluster bootstrap, conditional on the two fitted seed-26 models.
    base=pd.read_csv(RESULTS/"validation_seed26.csv")
    second=pd.read_csv(RESULTS/"validation_seed42.csv")
    frame=base.merge(second[["id","mixture"]].rename(columns={"mixture":"other_seed"}),
                     on="id",validate="one_to_one")
    groups=frame.groupby(["A","B"],sort=True).ngroup()
    frame=frame.assign(group=groups)
    n=groups.nunique()
    counts=np.random.default_rng(2601).multinomial(n,np.full(n,1/n),size=2000)
    fig,(ax,bx)=plt.subplots(1,2,figsize=(6.6,2.65),layout="constrained")
    records=[]
    for i,(name,pool) in enumerate([("All",frame),("Q2",frame[frame.X.eq("NO2")]),
                                     ("Q3",frame[frame.X.isin(FAMILIES)])]):
        scores={}
        for model in ["direct","mixture"]:
            ranked=pool.sort_values([model,"id"])
            # Keep multiplicities when spending a fixed budget on a bootstrap sample.
            weights=counts[:,ranked.group.to_numpy()]
            remaining=50-(np.cumsum(weights,axis=1)-weights)
            used=np.minimum(weights,np.maximum(remaining,0))
            scores[model]=used @ (ranked.V.to_numpy()<1)
        delta=scores["mixture"]-scores["direct"]
        lo,hi=np.percentile(delta,[2.5,97.5],method="nearest")
        observed=sum(pool.nsmallest(50,"mixture").V<1)-sum(pool.nsmallest(50,"direct").V<1)
        ax.plot([lo,hi],[i,i],color=GRAY,lw=2)
        ax.scatter(observed,i,s=42,color=SAGE,zorder=3)
        ax.text(hi+.35,i,f"[{lo}, {hi}]",va="center",fontsize=8)
        ranks=[pool.sort_values([s,"id"]).id for s in ["mixture","other_seed"]]
        budgets=[1,10,20,50]
        overlap=[len(set(ranks[0].head(k)) & set(ranks[1].head(k))) for k in budgets]
        bx.plot(budgets,np.array(overlap)/budgets,marker=["o","s","^"][i],
                color=[GRAY,OCHRE,BLUE][i],label=name)
        records.append(dict(pool=name,delta_hits50=observed,p025=lo,p975=hi,
                            **{f"overlap{k}":v for k,v in zip(budgets,overlap)}))
    ax.axvline(0,color=GRAY,lw=.9,ls="--")
    ax.set(xlim=(-9,22),ylim=(-.6,2.6),yticks=[0,1,2],yticklabels=["All","Q2","Q3"],
           xlabel="Additional hits in 50 checks",title="Pair-resampling sensitivity")
    bx.set(xlabel="Shortlist size",ylabel="Shared fraction",title="Agreement across seeds",
           xticks=budgets,ylim=(-.05,1.05))
    bx.legend(frameon=False,loc="lower right",fontsize=8)
    save(fig, "validation_stability")
    pd.DataFrame(records).to_csv(ART/"shortlist_sensitivity.csv",index=False, lineterminator="\r\n")


def landscapes(scores):
    fig, axes = plt.subplots(1, 3, figsize=(7.1, 2.75), layout="constrained")
    low, high = scores.V_hat.min(), scores.V_hat.max()
    for ax, family, title in zip(axes, FAMILIES, FAMILY_LABELS):
        group = scores[scores.X.eq(family)]
        table = group.pivot(index="A", columns="B", values="V_hat").sort_index().sort_index(axis=1)
        assert table.shape == (52, 52) and table.notna().all().all()
        mesh = ax.pcolormesh(table.to_numpy(), cmap=DENSITY, vmin=low, vmax=high,
                             shading="flat", linewidth=0, rasterized=False)
        best = group.sort_values(["V_hat","id"]).iloc[0]
        row, col = table.index.get_loc(best.A), table.columns.get_loc(best.B)
        ax.scatter(col+.5, row+.5, marker="D", s=36, facecolors=PAPER, edgecolors=INK)
        ticks = np.array([0, 13, 26, 39, 51])
        ax.set(xticks=ticks+.5, xticklabels=table.columns[ticks], yticks=ticks+.5,
               yticklabels=table.index[ticks], xlim=(0, 52), ylim=(52, 0), title=title,
               aspect="equal", xlabel=f"B site\n{best.A}–{best.B}: {best.V_hat:.2f}")
    axes[0].set_ylabel("A site")
    cb = fig.colorbar(mesh, ax=axes, shrink=.78, label="Predicted violation")
    cb.solids.set_rasterized(False)
    save(fig,"family_landscapes")


def tied_block(scores):
    ledger = pd.read_csv(ART/"block_runs.csv").query("problem == 'Q3'")
    record = ledger.loc[(ledger.worst_tied-ledger.score).idxmax()]
    envelope = scores.groupby(["A","B"]).V_hat.min().unstack()
    a, b = int(record.block_a)*4, int(record.block_b)*4
    tile = envelope.iloc[a:a+4, b:b+4]
    values = tile.to_numpy()
    bins = np.rint(15*values/values.max()).astype(int)
    ties = bins == bins.min()
    best = np.unravel_index(values.argmin(), values.shape)
    np.testing.assert_allclose([values[ties].min(), values[ties].max()],
                               [record.score, record.worst_tied])
    assert ties.sum() == record.ties
    fig, axes = plt.subplots(1, 2, figsize=(6.0, 2.8), layout="constrained")
    for ax, table, title, decimals in zip(axes, (values,bins),
            ("a   Original pair minima", "b   Rounded integer costs"), (2,0)):
        for i, j in np.ndindex(4, 4):
            face = MIST if ties[i,j] else PAPER
            ax.add_patch(Rectangle((j-.5,i-.5),1,1,fc=face,ec=GRID,lw=1))
            ax.text(j,i,f"{table[i,j]:.{decimals}f}",ha="center",va="center",
                    color=INK, weight="bold" if ties[i,j] else "normal")
        i, j = best
        ax.add_patch(Rectangle((j-.47,i-.47),.94,.94,fc="none",ec=INK,lw=2.0))
        ax.set(xticks=range(4), xticklabels=tile.columns, yticks=range(4),
               yticklabels=tile.index, xlim=(-.5,3.5), ylim=(3.5,-.5), aspect="equal",
               ylabel="A site", xlabel="B site", title=title)
        ax.spines[:].set_visible(False)
        ax.tick_params(length=0)
    save(fig, "tied_block")


if __name__ == "__main__":
    public = pd.concat(pd.read_csv(next(DATA.glob(prefix+"_*.csv"))) for prefix in ("02","03"))
    scores = pd.read_csv(ART/"q23_full.csv")
    site_pair_audit(public)
    physical(public)
    stability()
    landscapes(scores)
    tied_block(scores)
