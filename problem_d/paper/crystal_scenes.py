"""Explain the validation gate and read back the winning QUBO state."""
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd

from figures import BLUE, CLAY, GRAY, GRID, HERE, INK, MIST, PAPER, SAGE, save

ART = HERE / "artifacts"


def gate():
    components = pd.read_csv(ART / "gate_components.csv")
    row = components.loc[components.id.eq(16911)].iloc[0]
    terms = [(1-row.p_gap)*row.metal_score, row.p_gap*row.gapped_score]
    np.testing.assert_allclose(sum(terms), row.soft)
    fig,(ax,bx) = plt.subplots(1,2,figsize=(6.4,2.03),layout="constrained")
    ax.set(title="a   Weighted branches", xlabel="Contribution to predicted violation",
           yticks=[1,0], yticklabels=["Zero gap","Positive gap"], ylim=(-.55,1.58), xlim=(0,7.5))
    for y,value,weight,color in ((1,terms[0],1-row.p_gap,BLUE),(0,terms[1],row.p_gap,SAGE)):
        ax.barh(y,value,height=.28,color=color)
        ax.text(value+.15,y,f"{value:.2f}",va="center",fontsize=9)
        ax.text(.03,y+.20,f"weight {weight:.4f}",va="bottom",fontsize=8.5,color=GRAY)
    bx.set(title="b   InTiO\u2083, ID 16911", xlabel="Violation",yticks=[1,0],
           yticklabels=["Predicted","Observed"],ylim=(-.55,1.58),xlim=(0,15))
    for y,val,color,marker in ((1,row.soft,SAGE,"o"),(0,row.V,CLAY,"D")):
        bx.hlines(y,0,val,color=color,lw=2)
        bx.plot(val,y,marker,color=color)
        bx.annotate(f"{val:.2f}",(val,y),(4,0),textcoords="offset points",va="center",fontsize=9)
    for axis in (ax,bx):
        axis.grid(axis="x")
        axis.spines["left"].set_visible(False)
        axis.tick_params(axis="y", length=0)
    save(fig,"gate_mechanism")


def decode():
    scores = pd.read_csv(ART / "q23_full.csv")
    winner = pd.read_csv(ART / "selections.csv").query("problem == 'Q3'").iloc[0]
    blocks = pd.read_csv(ART / "block_runs.csv").query("problem == 'Q3'")
    block = blocks.loc[blocks.id.eq(winner.id)].iloc[0]
    fig,ax = plt.subplots(figsize=(6.2,1.55),layout="constrained")
    ax.set(xlim=(0,10),ylim=(-.3,2.45))
    ax.axis("off")
    for y,site,group in ((1.12,"A",block.block_a),(.19,"B",block.block_b)):
        elements = sorted(scores[site].unique())[4*int(group):4*int(group)+4]
        ax.text(.05,y+.33,f"{site} site",va="center",weight="bold")
        for j,el in enumerate(elements):
            x = 1.15+j*.81
            selected = el == winner[site]
            ax.add_patch(Rectangle((x,y),.68,.62,fc=MIST if selected else GRID,
                                   ec=INK if selected else PAPER,lw=1))
            ax.text(x+.34,y+.34,f"{el} · {int(selected)}",ha="center",va="center",fontsize=9)
    ax.annotate("",xy=(5.4,1),xytext=(4.55,1),arrowprops={"arrowstyle":"->","color":GRAY})
    ax.text(5.65,1.54,f"({winner.A}, {winner.B}, {winner.X})",fontsize=12,weight="bold")
    ax.text(5.65,.94,f"ID {winner.id}    {winner.formula.replace('3','\u2083')}",fontsize=11)
    ax.text(5.65,.34,f"Predicted violation  {winner.V_hat:.6f}",fontsize=9)
    save(fig,"qubo_decode")


if __name__ == "__main__":
    gate()
    decode()
