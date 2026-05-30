"""Frame estático del animador (mismo formato visual). Para los PDFs."""
import argparse
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

import style  # noqa: F401
from lib import load_phases
from animate import grid_positions


def make_frame(csv_path, out_path=None, t_target=None, frac=0.5):
    csv_path = Path(csv_path)
    t, r, theta = load_phases(csv_path)
    N = theta.shape[1]

    if t_target is None:
        idx = int(len(t) * frac)
    else:
        idx = int(np.argmin(np.abs(t - t_target)))

    xs, ys, cols, rows = grid_positions(N)

    fig = plt.figure(figsize=(11, 9))
    gs = fig.add_gridspec(2, 1, height_ratios=[3.2, 1.0], hspace=0.35)
    ax_net = fig.add_subplot(gs[0])
    ax_r = fig.add_subplot(gs[1])

    ax_net.set_xlim(-0.5, cols - 0.5)
    ax_net.set_ylim(rows - 0.5, -0.5)
    ax_net.set_aspect("equal")
    ax_net.set_xticks([])
    ax_net.set_yticks([])
    for spine in ax_net.spines.values():
        spine.set_visible(False)

    th = theta[idx]
    marker_size = max(20, int(8000 / max(cols, rows)))
    scat = ax_net.scatter(xs, ys, c=th % (2 * np.pi),
                          cmap="hsv", vmin=0, vmax=2 * np.pi,
                          s=marker_size, edgecolors="none", marker="s")
    cbar = fig.colorbar(scat, ax=ax_net, fraction=0.04, pad=0.08,
                        ticks=[0, np.pi, 2 * np.pi])
    cbar.ax.set_yticklabels(["0", "π", "2π"])
    cbar.ax.yaxis.set_label_position("left")
    cbar.set_label("fase", labelpad=15)
    cbar.ax.tick_params(labelsize=18)

    ax_r.set_xlim(0, float(t[-1]))
    ax_r.set_ylim(-0.02, 1.05)
    ax_r.set_xlabel("tiempo (s)")
    ax_r.set_ylabel("r")
    ax_r.plot(t[:idx + 1], r[:idx + 1], color="C0", lw=2.5)
    ax_r.tick_params(axis="x", rotation=0)
    ax_r.tick_params(axis="y", rotation=0)
    ax_r.grid(alpha=0.3)

    ax_net.text(0.01, 1.02,
                f"t = {float(t[idx]):.2f}    r = {float(r[idx]):.3f}",
                transform=ax_net.transAxes, verticalalignment="bottom",
                fontsize=20,
                bbox=dict(boxstyle="round", facecolor="white",
                          alpha=0.9, edgecolor="lightgray"))

    if out_path is None:
        out_path = csv_path.with_suffix(".png")
    fig.savefig(out_path)
    plt.close(fig)
    print(f"frame: {out_path}")
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("-o", "--output", default=None)
    ap.add_argument("-t", type=float, default=None)
    ap.add_argument("--frac", type=float, default=0.5)
    args = ap.parse_args()
    make_frame(args.csv, args.output, args.t, args.frac)


if __name__ == "__main__":
    main()
