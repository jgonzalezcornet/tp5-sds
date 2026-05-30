"""Red aleatoria: r(p) a K=0.1, mapas 2D r∞(p,K) y τ(p,K)."""
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import style  # noqa: F401
from lib import OUT_ROOT, cell_edges, load_rt, r_stationary, tau_sync

DATA_DIR = OUT_ROOT / "random_pK"
OUT_DIR = Path(__file__).resolve().parent.parent / "graphs" / "random"

# Rango de p en especificación (enunciado v2): p ∈ [1e-4, 1e-1] log.
P_MAX = 0.1
# Corte de sincronización vs p fijado por el enunciado v2.
K_CUT = 0.1


def load_by_pK():
    files = sorted(DATA_DIR.glob("p*_K*_seed*.csv"))
    by_pK = {}
    for f in files:
        m = re.match(r"p([0-9.]+)_K([0-9.]+)_seed\d+\.csv", f.name)
        if not m:
            continue
        p = float(m.group(1))
        K = float(m.group(2))
        # El enunciado v2 acota el análisis de la red aleatoria a p ∈ [1e-4, 1e-1].
        # Se descartan los p heredados fuera de rango (p=0.3, p=1.0); esos archivos
        # se conservan en disco sólo para la comparativa de topologías a p=1.
        if p > P_MAX * 1.0001:
            continue
        by_pK.setdefault((p, K), []).append(f)
    return by_pK


def plot_rp_Kcut(by_pK):
    ps = sorted({p for (p, K) in by_pK if K == K_CUT})
    r_mean = np.zeros(len(ps))
    r_std = np.zeros(len(ps))
    for i, p in enumerate(ps):
        vals = [r_stationary(load_rt(f)[1], late_frac=0.2)
                for f in by_pK[(p, K_CUT)]]
        r_mean[i] = np.mean(vals)
        r_std[i] = np.std(vals)
    fig, ax = plt.subplots()
    ax.errorbar(ps, r_mean, yerr=r_std, fmt="o-", color="C0", capsize=5)
    ax.set_xscale("log")
    ax.set_xlabel("Probabilidad de conexión")
    ax.set_ylabel("r")
    ax.set_ylim(0, 1.05)
    out = OUT_DIR / "rp_Kcut.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def heatmap(values, ps, Ks, label, out_name, cmap="viridis"):
    p_edges = cell_edges(np.array(ps), log=True)
    K_edges = cell_edges(np.array(Ks), log=True)
    fig, ax = plt.subplots()
    mesh = ax.pcolormesh(p_edges, K_edges, values.T, cmap=cmap, shading="auto")
    cb = fig.colorbar(mesh, ax=ax)
    cb.set_label(label)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Probabilidad de conexión")
    ax.set_ylabel("K")
    out = OUT_DIR / out_name
    fig.savefig(out)
    plt.close(fig)
    return out


def plot_heatmaps(by_pK):
    ps = sorted({p for (p, K) in by_pK})
    Ks = sorted({K for (p, K) in by_pK})
    r_grid = np.zeros((len(ps), len(Ks)))
    tau_grid = np.full((len(ps), len(Ks)), np.nan)
    for i, p in enumerate(ps):
        for j, K in enumerate(Ks):
            files = by_pK.get((p, K), [])
            if not files:
                continue
            r_vals = []
            tau_vals = []
            for f in files:
                t, r = load_rt(f)
                r_vals.append(r_stationary(r, late_frac=0.2))
                tau = tau_sync(t, r, frac=0.95, late_frac=0.2, smooth_pts=20)
                r_late = float(np.mean(r[int(len(r) * 0.8):]))
                if tau is not None and r_late > 0.5:
                    tau_vals.append(tau)
            r_grid[i, j] = np.mean(r_vals)
            if len(tau_vals) >= 3:
                tau_grid[i, j] = np.mean(tau_vals)
    out_r = heatmap(r_grid, ps, Ks, "r", "heatmap_rpK.png")
    out_tau = heatmap(tau_grid, ps, Ks, "τ (s)",
                      "heatmap_taupK.png", cmap="plasma")
    return out_r, out_tau


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    by_pK = load_by_pK()
    n_seeds = min(len(v) for v in by_pK.values())
    out_rp = plot_rp_Kcut(by_pK)
    out_r, out_tau = plot_heatmaps(by_pK)
    print(f"saved -> {out_rp} (promedio sobre {n_seeds} realizaciones)")
    print(f"saved -> {out_r}")
    print(f"saved -> {out_tau}")


if __name__ == "__main__":
    main()
