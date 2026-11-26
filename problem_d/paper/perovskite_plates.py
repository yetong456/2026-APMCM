"""Use ideal fractional coordinates for geometry and archived records for properties."""
from itertools import combinations, product

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.markers import MarkerStyle
from matplotlib.patches import Circle, PathPatch, Polygon, Rectangle
from matplotlib.transforms import Affine2D
import numpy as np
import pandas as pd

from figures import (BLUE, CLAY, GRAY, GRID, HERE, INK, MIST, OCHRE, PAPER,
                     PLUM, SAGE, save)

DATA = HERE.parent / "date"
ELEMENT = {"Sn": BLUE, "Ti": OCHRE, "O": CLAY, "N": PLUM, "F": SAGE}


SITE_MARKER = {"Sn": "s", "Ti": "D", "O": "o"}


def draw_site(ax, x, y, radius, element, depth=3):
    marker = MarkerStyle(SITE_MARKER[element])
    path = marker.get_path().transformed(marker.get_transform())
    position = Affine2D().scale(2 * radius).translate(x, y) + ax.transData
    ax.add_patch(PathPatch(path, transform=position, facecolor=ELEMENT[element],
                           edgecolor=INK, linewidth=.55, zorder=depth))


def project(points):
    yaw, elevation = np.radians([32, 19])
    right = np.array([np.cos(yaw), -np.sin(yaw), 0])
    forward = np.array([np.sin(yaw), np.cos(yaw), 0])
    up = np.array([0, 0, 1])
    basis = [right, up*np.cos(elevation)-forward*np.sin(elevation),
             forward*np.cos(elevation)+up*np.sin(elevation)]
    return np.asarray(points) @ np.array(basis).T


def cell(ax):
    corners = np.array(list(product([-.5,.5], repeat=3)))
    faces = np.vstack([np.eye(3), -np.eye(3)])*.5
    center = np.zeros(3)
    for a, b in combinations(corners, 2):
        if np.isclose(np.linalg.norm(a-b), 1):
            pts = project([a,b])
            ax.plot(*pts[:,:2].T, color=GRAY, lw=.9, zorder=5+pts[:,2].mean())
    for signs in product([-1,1], repeat=3):
        pts = project(np.diag(signs)*.5)
        ax.add_patch(Polygon(pts[:,:2], fc=MIST, ec=GRAY, lw=.4, alpha=.25,
                             zorder=5+pts[:,2].mean()))
    for p in faces:
        pts = project([center,p])
        ax.plot(*pts[:,:2].T, color=GRAY, lw=.85, zorder=5+pts[:,2].mean())
    for sites, el, radius in ((corners,"Sn",.078),(faces,"O",.060),([center],"Ti",.096)):
        for x, y, depth in project(sites):
            draw_site(ax, x, y, radius, el, 5.1 + depth)
    ax.set(xlim=(-.93,.93),ylim=(-.89,.89),aspect="equal")
    ax.axis("off")


def crystal_and_exchange(public):
    fig = plt.figure(figsize=(6.45,2.85), layout="constrained")
    grid = fig.add_gridspec(2,2, height_ratios=[5,1], width_ratios=[.85,1.48])
    ax, bx, legend = fig.add_subplot(grid[0,0]), fig.add_subplot(grid[0,1]), fig.add_subplot(grid[1,:])
    ax.set_title("a   Ideal SnTiO\u2083 cell")
    cell(ax)
    bx.set(title="b   Exchange the two cations", xlim=(0,2), ylim=(-.48,1.4), aspect="equal")
    bx.axis("off")
    for x, formula in enumerate(("SnTiO3","TiSnO3")):
        r = public.loc[public.formula.eq(formula) & public.X.eq("O3")].squeeze()
        assert isinstance(r, pd.Series)
        cx, cy, half = x+.5, .63, .25
        bx.text(cx,1.24,formula.replace("3","\u2083"),ha="center",weight="bold")
        bx.text(cx,1.04,f"A={r.A}   B={r.B}",ha="center",fontsize=9)
        bx.add_patch(Rectangle((cx-half,cy-half),2*half,2*half,fc=GRID,ec=GRAY,lw=.8))
        # Project onto (001). The central B site lies in the plane at z = 1/2.
        for dx,dy in product([-half,half],repeat=2):
            draw_site(bx, cx + dx, cy + dy, .069, r.A)
        for dx,dy in ((0,half),(0,-half),(half,0),(-half,0)):
            draw_site(bx, cx + dx, cy + dy, .047, "O")
        draw_site(bx, cx, cy, .09, r.B)
        bx.text(cx,.11,f"Gap  {r.gap:.2f} eV",ha="center",fontsize=9)
        bx.text(cx,-.11,f"V  {r.V:.6f}",ha="center",fontsize=9)
    legend.axis("off")
    handles = [Line2D([],[],marker=SITE_MARKER[e],lw=0,markerfacecolor=ELEMENT[e],markeredgecolor=INK,
                      markeredgewidth=.6,label=e) for e in ("Sn","Ti","O")]
    legend.legend(handles=handles,loc="center",ncol=3,handletextpad=.15,columnspacing=1.6)
    save(fig,"crystal_sites")


def electronic(public):
    sn, ca = (public.loc[public.id.eq(i)].iloc[0] for i in (8760,8811))
    pred = pd.read_csv(HERE.parent/"results"/"physical_seed26.csv").query("id == 8811").iloc[0]
    fig, (ax,bx) = plt.subplots(1,2, figsize=(6.55,2.75), layout="constrained")
    ax.set(title="a   Band edges",xlim=(-.5,2.5),ylim=(9,1),ylabel="Reported edge (eV)",
           xticks=[0,1,2],xticklabels=["SnTiO\u2083\nDFT","CaZrO\u2083\nmodel","CaZrO\u2083\nDFT"])
    ax.grid(axis="y")
    for val,color,marker,label in ((4.50,SAGE,"o","CBM"),(5.73,PLUM,"s","VBM")):
        ax.axhline(val,ls=":",color=color,lw=1.1)
        levels = [sn.cbm,pred.pred_cbm,ca.cbm] if label=="CBM" else [sn.vbm,pred.pred_vbm,ca.vbm]
        ax.plot(range(3),levels,ls="none",marker=marker,color=color,label=label,ms=6)
    ax.legend(ncol=2,loc="upper center",fontsize=8.5,handletextpad=.1,columnspacing=.9)
    bx.set(title="b   CaZrO\u2083 band gap",xlim=(0,8.2),ylim=(-.62,1.65),
           yticks=[1,0],yticklabels=["Model","DFT"],xlabel="GLLB-SC gap (eV)")
    bx.axvspan(1.4,3.1,color=GRID)
    bx.axvline(3.1,color=GRAY,lw=.9,ls=":")
    bx.text(3.2,1.41,"3.10 eV limit",ha="left",va="center",fontsize=8.5)
    for y, value, color, marker in ((1,pred.pred_gap,BLUE,"s"),(0,ca.gap,CLAY,"o")):
        bx.hlines(y,0,value,color=color,lw=1.8)
        bx.plot(value,y,marker=marker,color=color,ms=6)
        bx.annotate(f"{value:.2f}",(value,y),(5,0),textcoords="offset points",va="center",fontsize=9)
    save(fig,"band_edges")


def anions(scores):
    pair = scores[scores.A.eq("La") & scores.B.eq("Ti")].set_index("X")
    fig, (ax,bx) = plt.subplots(1,2,figsize=(6.15,2.0),layout="constrained")
    families = [("NO2","LaTiO\u2082N","N"),("FO2","LaTiO\u2082F","F"),("O3","LaTiO\u2083","O")]
    ax.set(title="a   Anion counts",xlim=(-.2,2.7),ylim=(-.6,2.6),aspect="equal")
    bx.set(title="b   Frozen prediction",xlim=(0,14.6),ylim=(-.6,2.6),xlabel="Predicted violation")
    for y,(key,formula,last) in zip([2,1,0],families):
        for x,el in enumerate(("O","O",last)):
            ax.add_patch(Circle((x*.65+.4,y),.23,fc=ELEMENT[el],ec=INK,lw=.6))
            ax.text(x*.65+.4,y,el,ha="center",va="center",color=PAPER,fontsize=8,weight="bold")
        val = pair.loc[key,"V_hat"]
        bx.hlines(y,0,val,color=ELEMENT[last],lw=2)
        bx.plot(val,y,"o",color=ELEMENT[last])
        bx.annotate(f"{val:.4f}",(val,y),(4,0),textcoords="offset points",va="center",fontsize=9)
    ax.set_yticks([2,1,0], [f[1] for f in families])
    ax.set_xticks([])
    ax.spines[:].set_visible(False)
    ax.tick_params(length=0)
    bx.set_yticks([])
    bx.grid(axis="x")
    save(fig,"anion_substitution")


if __name__ == "__main__":
    public = pd.concat(pd.read_csv(next(DATA.glob(p+"_*.csv"))) for p in ("02","03"))
    crystal_and_exchange(public)
    electronic(public)
    anions(pd.read_csv(HERE/"artifacts"/"q23_full.csv"))
