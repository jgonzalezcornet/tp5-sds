"""Animador estilo anillo: nodos en un círculo, aristas dibujadas, color = fase."""
import argparse
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.animation import FuncAnimation, PillowWriter

import style  # noqa: F401
from lib import load_phases, parse_header


def ring_positions(N, R=1.0):
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False)
    return R * np.cos(angles), R * np.sin(angles)


def build_edges(N, topology, p, v, net_seed=0, max_edges_complete=8000, max_edges_random=3000):
    """Return list of (i, j) edges to draw."""
    if topology == "COMPLETE":
        rng = np.random.default_rng(net_seed)
        total = N * (N - 1) // 2
        if total <= max_edges_complete:
            return [(i, j) for i in range(N) for j in range(i + 1, N)]
        flat_idx = rng.choice(total, size=max_edges_complete, replace=False)
        edges = []
        for k in flat_idx:
            i = int(np.floor((-1 + np.sqrt(1 + 8 * k)) / 2)) + 1
            while i * (i - 1) // 2 > k:
                i -= 1
            while (i + 1) * i // 2 <= k:
                i += 1
            j = k - i * (i - 1) // 2
            if j >= i:
                continue
            edges.append((int(j), int(i)))
        if not edges:
            return [(i, j) for i in range(N) for j in range(i + 1, N)][:max_edges_complete]
        return edges
    if topology == "RANDOM":
        rng = np.random.default_rng(net_seed)
        edges = []
        for i in range(N):
            for j in range(i + 1, N):
                if rng.random() < p:
                    edges.append((i, j))
        if len(edges) > max_edges_random:
            idx = rng.choice(len(edges), size=max_edges_random, replace=False)
            edges = [edges[k] for k in idx]
        return edges
    if topology == "RING":
        edges = []
        for i in range(N):
            for d in range(1, v + 1):
                j = (i + d) % N
                edges.append((i, j))
        return edges
    return []


def edge_alpha(topology, n_edges):
    if topology == "COMPLETE":
        return 0.22
    if topology == "RANDOM":
        return 0.14
    return 0.6


def edge_linewidth(topology):
    if topology == "COMPLETE":
        return 1.0
    if topology == "RANDOM":
        return 1.0
    return 1.4


def make_ring_animation(csv_path, out_path=None, fps=20, max_frames=200, t_max=None):
    csv_path = Path(csv_path)
    t, r, theta = load_phases(csv_path)
    if theta is None:
        raise ValueError("El CSV no contiene fases (corré el motor con --dumpPhases true).")

    N = theta.shape[1]
    hdr = parse_header(csv_path)
    topology = hdr.get("topology", "COMPLETE")
    p = float(hdr.get("p", "0.5"))
    v = int(hdr.get("v", "1"))
    net_seed = int(hdr.get("netSeed", "0"))
    K = float(hdr.get("K", "0"))

    if t_max is not None:
        mask = t <= t_max
        t, r, theta = t[mask], r[mask], theta[mask]
    if len(t) > max_frames:
        idx = np.linspace(0, len(t) - 1, max_frames).astype(int)
        t, r, theta = t[idx], r[idx], theta[idx]
    n_frames = len(t)

    xs, ys = ring_positions(N)
    edges = build_edges(N, topology, p, v, net_seed)
    segments = np.array([[(xs[i], ys[i]), (xs[j], ys[j])] for (i, j) in edges]) \
        if edges else np.empty((0, 2, 2))

    fig, ax_net = plt.subplots(figsize=(16, 16), dpi=80)
    fig.subplots_adjust(left=0.02, right=0.88, top=0.94, bottom=0.02)

    ax_net.set_xlim(-1.22, 1.22)
    ax_net.set_ylim(-1.22, 1.22)
    ax_net.set_aspect("equal")
    ax_net.set_xticks([])
    ax_net.set_yticks([])
    for spine in ax_net.spines.values():
        spine.set_visible(False)

    if len(segments) > 0:
        lc = LineCollection(segments, colors=("0.3",),
                            linewidths=edge_linewidth(topology),
                            alpha=edge_alpha(topology, len(segments)),
                            antialiaseds=False,
                            zorder=1)
        ax_net.add_collection(lc)

    marker_size = max(280, int(80000 / N))
    scat = ax_net.scatter(xs, ys, c=theta[0] % (2 * np.pi),
                          cmap="hsv", vmin=0, vmax=2 * np.pi,
                          s=marker_size, edgecolors="black", linewidths=0.4,
                          zorder=2)

    cbar = fig.colorbar(scat, ax=ax_net, fraction=0.05, pad=0.04,
                        ticks=[0, np.pi, 2 * np.pi])
    cbar.ax.set_yticklabels(["0", "π", "2π"])
    cbar.set_label("fase", labelpad=18, fontsize=28)
    cbar.ax.tick_params(labelsize=26)

    info = ax_net.text(0.02, 0.98, "", transform=ax_net.transAxes,
                       verticalalignment="top", horizontalalignment="left",
                       fontsize=28,
                       bbox=dict(boxstyle="round,pad=0.5", facecolor="white",
                                 alpha=0.92, edgecolor="lightgray"))

    def update(i):
        scat.set_array(theta[i] % (2 * np.pi))
        info.set_text(f"t = {float(t[i]):.2f}    r = {float(r[i]):.3f}")
        return scat, info

    anim = FuncAnimation(fig, update, frames=n_frames,
                         interval=1000 / fps, blit=False)

    if out_path is None:
        out_path = csv_path.with_suffix(".gif")
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    anim.save(out_path, writer=PillowWriter(fps=fps))
    plt.close(fig)
    print(f"animación: {out_path}")
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("-o", "--output", default=None)
    ap.add_argument("--fps", type=int, default=20)
    ap.add_argument("--max-frames", type=int, default=200)
    ap.add_argument("--t-max", type=float, default=None)
    args = ap.parse_args()
    make_ring_animation(args.csv, args.output, args.fps, args.max_frames, args.t_max)


if __name__ == "__main__":
    main()
