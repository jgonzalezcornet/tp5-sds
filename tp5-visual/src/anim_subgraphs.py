"""Animador con subgrafos: anillo principal + componentes no gigantes al costado."""
import argparse
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.animation import FuncAnimation, PillowWriter

import style  # noqa: F401
from lib import load_phases, parse_header


def load_edges(edges_path):
    edges = []
    with open(edges_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            i, j = map(int, line.split(","))
            edges.append((i, j))
    return edges


def connected_components(N, edges):
    parent = list(range(N))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i, j in edges:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj
    groups = {}
    for x in range(N):
        groups.setdefault(find(x), []).append(x)
    return sorted(groups.values(), key=len, reverse=True)


def ring_layout(n, R=1.0):
    if n == 1:
        return np.array([0.0]), np.array([0.0])
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return R * np.cos(angles), R * np.sin(angles)


def make_subgraph_animation(csv_path, edges_path, out_path, fps=20, max_frames=200):
    csv_path = Path(csv_path)
    t, r, theta = load_phases(csv_path)
    N = theta.shape[1]
    edges = load_edges(edges_path)

    if len(t) > max_frames:
        idx = np.linspace(0, len(t) - 1, max_frames).astype(int)
        t, r, theta = t[idx], r[idx], theta[idx]
    n_frames = len(t)

    comps = connected_components(N, edges)
    giant = comps[0]
    others = comps[1:]
    pairs = [c for c in others if len(c) > 1]
    singletons = [c[0] for c in others if len(c) == 1]

    xs_main, ys_main = ring_layout(N, R=1.0)
    main_segments = (np.array([[(xs_main[i], ys_main[i]),
                                (xs_main[j], ys_main[j])] for (i, j) in edges])
                     if edges else np.empty((0, 2, 2)))

    fig = plt.figure(figsize=(22, 14), dpi=80)
    n_side = len(pairs) + (1 if singletons else 0)
    if n_side == 0:
        rows, cols = 1, 1
    elif n_side <= 2:
        rows, cols = 1, 2
    elif n_side <= 4:
        rows, cols = 2, 2
    else:
        rows, cols = 2, 3

    gs = fig.add_gridspec(1, 2, width_ratios=[1.55, 1.0], wspace=0.05)
    ax_main = fig.add_subplot(gs[0])
    gs_side = gs[1].subgridspec(rows, cols, hspace=0.3, wspace=0.18)
    side_axes = []
    for r_i in range(rows):
        for c_i in range(cols):
            if len(side_axes) < n_side:
                side_axes.append(fig.add_subplot(gs_side[r_i, c_i]))

    ax_main.set_xlim(-1.22, 1.22)
    ax_main.set_ylim(-1.22, 1.22)
    ax_main.set_aspect("equal")
    ax_main.set_xticks([])
    ax_main.set_yticks([])
    for s in ax_main.spines.values():
        s.set_visible(False)

    if len(main_segments) > 0:
        lc_main = LineCollection(main_segments, colors=("0.3",), linewidths=1.0,
                                 alpha=0.22, antialiaseds=False, zorder=1)
        ax_main.add_collection(lc_main)

    marker_size = max(280, int(80000 / N))
    scat_main = ax_main.scatter(xs_main, ys_main, c=theta[0] % (2 * np.pi),
                                cmap="hsv", vmin=0, vmax=2 * np.pi,
                                s=marker_size, edgecolors="black", linewidths=0.4,
                                zorder=2)

    cbar = fig.colorbar(scat_main, ax=ax_main, fraction=0.04, pad=0.02,
                        ticks=[0, np.pi, 2 * np.pi])
    cbar.ax.set_yticklabels(["0", "π", "2π"])
    cbar.set_label("fase", labelpad=12, fontsize=24)
    cbar.ax.tick_params(labelsize=22)

    info = ax_main.text(0.02, 0.98, "", transform=ax_main.transAxes,
                        verticalalignment="top", fontsize=22,
                        bbox=dict(boxstyle="round,pad=0.4",
                                  facecolor="white", alpha=0.92,
                                  edgecolor="lightgray"))

    ax_main.text(0.02, 0.02, f"componente gigante: {len(giant)} nodos",
                 transform=ax_main.transAxes,
                 verticalalignment="bottom", fontsize=20,
                 bbox=dict(boxstyle="round,pad=0.4",
                           facecolor="white", alpha=0.92,
                           edgecolor="lightgray"))

    sub_scatters = []
    for k, ax in enumerate(side_axes):
        if k < len(pairs):
            comp = pairs[k]
            label = f"par #{k+1}  ({len(comp)} nodos)"
            xs_sub, ys_sub = ring_layout(len(comp))
            comp_set = set(comp)
            comp_idx = {nd: i for i, nd in enumerate(comp)}
            sub_edges = [(comp_idx[a], comp_idx[b]) for (a, b) in edges
                         if a in comp_set and b in comp_set]
            sub_segs = (np.array([[(xs_sub[i], ys_sub[i]),
                                   (xs_sub[j], ys_sub[j])] for (i, j) in sub_edges])
                        if sub_edges else np.empty((0, 2, 2)))
            if len(sub_segs) > 0:
                lc = LineCollection(sub_segs, colors=("0.3",), linewidths=3.0,
                                    alpha=0.9, antialiaseds=False, zorder=1)
                ax.add_collection(lc)
            scat = ax.scatter(xs_sub, ys_sub, c=theta[0, comp] % (2 * np.pi),
                              cmap="hsv", vmin=0, vmax=2 * np.pi,
                              s=900, edgecolors="black", linewidths=0.6, zorder=2)
            sub_scatters.append((scat, comp))
        else:
            label = f"{len(singletons)} singletons (sin conexión)"
            xs_sub, ys_sub = ring_layout(len(singletons), R=0.95)
            scat = ax.scatter(xs_sub, ys_sub,
                              c=theta[0, singletons] % (2 * np.pi),
                              cmap="hsv", vmin=0, vmax=2 * np.pi,
                              s=180, edgecolors="black", linewidths=0.4,
                              zorder=2)
            sub_scatters.append((scat, singletons))

        ax.set_xlim(-1.3, 1.3)
        ax.set_ylim(-1.3, 1.3)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_visible(False)
        ax.set_title(label, fontsize=18, pad=6)

    def update(i):
        scat_main.set_array(theta[i] % (2 * np.pi))
        for scat, nodes in sub_scatters:
            scat.set_array(theta[i, nodes] % (2 * np.pi))
        info.set_text(f"t = {float(t[i]):.2f}    r = {float(r[i]):.3f}")
        return (scat_main, info) + tuple(s for s, _ in sub_scatters)

    anim = FuncAnimation(fig, update, frames=n_frames,
                         interval=1000 / fps, blit=False)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    anim.save(out_path, writer=PillowWriter(fps=fps))
    plt.close(fig)
    print(f"animación: {out_path}")
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("edges")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--fps", type=int, default=20)
    ap.add_argument("--max-frames", type=int, default=200)
    args = ap.parse_args()
    make_subgraph_animation(args.csv, args.edges, args.output,
                            args.fps, args.max_frames)


if __name__ == "__main__":
    main()
