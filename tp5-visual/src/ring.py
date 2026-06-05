"""Red anillo: r(v) a K=0.1, mapas 2D r∞(v,K) y τ(v,K)."""
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import style  # noqa: F401
from lib import OUT_ROOT, cell_edges, load_rt, r_stationary, tau_sync

DATA_DIR = OUT_ROOT / "ring_vK"
OUT_DIR = Path(__file__).resolve().parent.parent / "graphs" / "ring"

# Corte de sincronización vs v fijado por el enunciado v2.
K_CUT = 0.1


def load_by_vK():
    files = sorted(DATA_DIR.glob("v*_K*_seed*.csv"))
    by_vK = {}
    for f in files:
        m = re.match(r"v(\d+)_K([0-9.]+)_seed\d+\.csv", f.name)
        if not m:
            continue
        v = int(m.group(1))
        K = float(m.group(2))
        by_vK.setdefault((v, K), []).append(f)
    return by_vK


def plot_rv_Kcut(by_vK):
    vs = sorted({v for (v, K) in by_vK if K == K_CUT})
    r_mean = np.zeros(len(vs))
    r_std = np.zeros(len(vs))
    for i, v in enumerate(vs):
        vals = [r_stationary(load_rt(f)[1])
                for f in by_vK[(v, K_CUT)]]
        r_mean[i] = np.mean(vals)
        r_std[i] = np.std(vals)
    fig, ax = plt.subplots()
    ax.errorbar(vs, r_mean, yerr=r_std, fmt="o-", color="C0", capsize=5)
    ax.set_xlabel("v")
    ax.set_ylabel("r")
    ax.set_ylim(0, 1.05)
    out = OUT_DIR / "rv_Kcut.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def heatmap(values, vs, Ks, label, out_name, cmap="viridis"):
    v_edges = cell_edges(np.array(vs, dtype=float))
    K_edges = cell_edges(np.array(Ks), log=True)
    fig, ax = plt.subplots()
    mesh = ax.pcolormesh(v_edges, K_edges, values.T, cmap=cmap, shading="auto")
    cb = fig.colorbar(mesh, ax=ax)
    cb.set_label(label)
    ax.set_yscale("log")
    ax.set_xlabel("v")
    ax.set_ylabel("K")
    out = OUT_DIR / out_name
    fig.savefig(out)
    plt.close(fig)
    return out


def plot_heatmaps(by_vK):
    vs = sorted({v for (v, K) in by_vK})
    Ks = sorted({K for (v, K) in by_vK})
    r_grid = np.zeros((len(vs), len(Ks)))
    tau_grid = np.full((len(vs), len(Ks)), np.nan)
    for i, v in enumerate(vs):
        for j, K in enumerate(Ks):
            files = by_vK.get((v, K), [])
            if not files:
                continue
            r_vals = []
            tau_vals = []
            for f in files:
                t, r = load_rt(f)
                r_inf = r_stationary(r)
                r_vals.append(r_inf)
                tau = tau_sync(t, r)
                if tau is not None and r_inf > 0.5:
                    tau_vals.append(tau)
            r_grid[i, j] = np.mean(r_vals)
            if len(tau_vals) >= 3:
                tau_grid[i, j] = np.mean(tau_vals)
    out_r = heatmap(r_grid, vs, Ks, "r", "heatmap_rvK.png")
    out_tau = heatmap(tau_grid, vs, Ks, "τ (s)",
                      "heatmap_tauvK.png", cmap="plasma")
    return out_r, out_tau


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    by_vK = load_by_vK()
    n_seeds = min(len(v) for v in by_vK.values())
    out_rv = plot_rv_Kcut(by_vK)
    out_r, out_tau = plot_heatmaps(by_vK)
    print(f"saved -> {out_rv} (promedio sobre {n_seeds} realizaciones)")
    print(f"saved -> {out_r}")
    print(f"saved -> {out_tau}")


if __name__ == "__main__":
    main()
