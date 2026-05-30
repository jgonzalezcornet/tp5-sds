"""
Animador del modelo de Kuramoto.

Cada neurona es un punto en una grilla 2D, coloreado por su fase actual.
Cuando todos los puntos tienen el mismo color, las neuronas están sincronizadas.
Panel inferior: parámetro de orden r(t) creciendo en tiempo real.

Entrada: CSV con fases (motor con --dumpPhases true).
Salida: GIF (Pillow) o MP4 (si hay ffmpeg).
"""
import argparse
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
try:
    from matplotlib.animation import FFMpegWriter
    HAS_FFMPEG = True
except Exception:
    HAS_FFMPEG = False

import style  # noqa: F401
from lib import load_phases


def grid_positions(N):
    """Return (xs, ys) for N points laid out as an as-square-as-possible grid."""
    cols = int(np.ceil(np.sqrt(N)))
    rows = int(np.ceil(N / cols))
    idx = np.arange(N)
    xs = idx % cols
    ys = idx // cols
    return xs.astype(float), ys.astype(float), cols, rows


def make_animation(csv_path, out_path=None, fps=20, max_frames=200, t_max=None):
    csv_path = Path(csv_path)
    t, r, theta = load_phases(csv_path)
    if theta is None:
        raise ValueError("El CSV no contiene fases (corré el motor con --dumpPhases true).")

    N = theta.shape[1]

    if t_max is not None:
        mask = t <= t_max
        t, r, theta = t[mask], r[mask], theta[mask]

    if len(t) > max_frames:
        idx = np.linspace(0, len(t) - 1, max_frames).astype(int)
        t, r, theta = t[idx], r[idx], theta[idx]
    n_frames = len(t)

    xs, ys, cols, rows = grid_positions(N)

    fig = plt.figure(figsize=(11, 9))
    gs = fig.add_gridspec(2, 1, height_ratios=[3.2, 1.0], hspace=0.35)
    ax_net = fig.add_subplot(gs[0])
    ax_r = fig.add_subplot(gs[1])

    # top: grid of nodes coloured by phase
    ax_net.set_xlim(-0.5, cols - 0.5)
    ax_net.set_ylim(rows - 0.5, -0.5)  # invert y so first row is on top
    ax_net.set_aspect("equal")
    ax_net.set_xticks([])
    ax_net.set_yticks([])
    for spine in ax_net.spines.values():
        spine.set_visible(False)

    marker_size = max(20, int(8000 / max(cols, rows)))
    scat = ax_net.scatter(xs, ys, c=theta[0] % (2 * np.pi),
                          cmap="hsv", vmin=0, vmax=2 * np.pi,
                          s=marker_size, edgecolors="none", marker="s")
    cbar = fig.colorbar(scat, ax=ax_net, fraction=0.04, pad=0.08,
                        ticks=[0, np.pi, 2 * np.pi])
    cbar.ax.set_yticklabels(["0", "π", "2π"])
    cbar.ax.yaxis.set_label_position("left")
    cbar.set_label("fase", labelpad=15)
    cbar.ax.tick_params(labelsize=18)

    # bottom: r(t)
    ax_r.set_xlim(0, float(t[-1]))
    ax_r.set_ylim(-0.02, 1.05)
    ax_r.set_xlabel("tiempo (s)")
    ax_r.set_ylabel("r")
    ax_r.tick_params(axis="x", rotation=0)
    ax_r.tick_params(axis="y", rotation=0)
    ax_r.grid(alpha=0.3)
    line_r, = ax_r.plot([], [], color="C0", lw=2.5)

    info = ax_net.text(0.01, 1.02, "", transform=ax_net.transAxes,
                       verticalalignment="bottom", fontsize=20,
                       bbox=dict(boxstyle="round", facecolor="white",
                                 alpha=0.9, edgecolor="lightgray"))

    def update(i):
        scat.set_array(theta[i] % (2 * np.pi))
        line_r.set_data(t[:i + 1], r[:i + 1])
        info.set_text(f"t = {float(t[i]):.2f}    r = {float(r[i]):.3f}")
        return scat, line_r, info

    anim = FuncAnimation(fig, update, frames=n_frames,
                         interval=1000 / fps, blit=False)

    if out_path is None:
        out_path = csv_path.with_suffix(".gif")
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if out_path.suffix.lower() == ".mp4" and HAS_FFMPEG:
        anim.save(out_path, writer=FFMpegWriter(fps=fps, bitrate=1800))
    else:
        if out_path.suffix.lower() != ".gif":
            out_path = out_path.with_suffix(".gif")
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
    ap.add_argument("--t-max", type=float, default=None,
                    help="recortar la animación a t <= t_max")
    args = ap.parse_args()
    make_animation(args.csv, args.output, args.fps, args.max_frames, args.t_max)


if __name__ == "__main__":
    main()
