"""Red aleatoria: r(p) a K=0.1, mapas 2D r∞(p,K) y τ(p,K)."""
import re
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import style  # noqa: F401
from lib import (ORDER_THRESHOLD, OUT_ROOT, cell_edges, load_rt, min_sync_count,
                 parse_header, r_stationary, tau_sync)

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


def random_component_count(N, p, net_seed):
    parent = list(range(N))
    rng = np.random.default_rng(net_seed)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(N):
        for j in range(i + 1, N):
            if rng.random() < p:
                ri, rj = find(i), find(j)
                if ri != rj:
                    parent[ri] = rj
    return len({find(i) for i in range(N)})


def load_unique_random_networks():
    files = sorted(DATA_DIR.glob("p*_K*_seed*.csv"))
    by_p = defaultdict(dict)
    for f in files:
        m = re.match(r"p([0-9.]+)_K([0-9.]+)_seed\d+\.csv", f.name)
        if not m:
            continue
        p = float(m.group(1))
        if p > P_MAX * 1.0001:
            continue
        hdr = parse_header(f)
        net_seed = int(hdr.get("netSeed", hdr.get("seed", "0")))
        if net_seed in by_p[p]:
            continue
        by_p[p][net_seed] = {
            "N": int(hdr.get("N", "600")),
            "p": p,
            "net_seed": net_seed,
        }
    return {p: list(cfgs.values()) for p, cfgs in by_p.items()}


def plot_components_vs_p():
    networks_by_p = load_unique_random_networks()
    ps = sorted(networks_by_p)
    comp_mean = np.zeros(len(ps))
    comp_std = np.zeros(len(ps))
    counts = []

    for i, p in enumerate(ps):
        vals = [random_component_count(cfg["N"], cfg["p"], cfg["net_seed"])
                for cfg in networks_by_p[p]]
        counts.append(len(vals))
        comp_mean[i] = np.mean(vals)
        comp_std[i] = np.std(vals)

    fig, ax = plt.subplots()
    ax.errorbar(ps, comp_mean, yerr=comp_std, fmt="o-", color="C3", capsize=5)
    ax.set_xscale("log")
    ax.set_xlabel("p")
    ax.set_ylabel("cantidad de componentes")
    y_min, y_max = ax.get_ylim()
    ticks = ax.get_yticks()
    ticks = np.unique(np.concatenate((ticks, [1.0])))
    ticks = ticks[~np.isclose(ticks, 0.0)]
    ticks = ticks[(ticks >= y_min) & (ticks <= y_max)]
    ax.set_yticks(ticks)
    ax.set_ylim(y_min, y_max)
    out = OUT_DIR / "components_vs_p.png"
    fig.savefig(out)
    plt.close(fig)
    return out, min(counts)


def plot_rp_Kcut(by_pK):
    ps = sorted({p for (p, K) in by_pK if K == K_CUT})
    r_mean = np.zeros(len(ps))
    r_std = np.zeros(len(ps))
    for i, p in enumerate(ps):
        vals = [r_stationary(load_rt(f)[1])
                for f in by_pK[(p, K_CUT)]]
        r_mean[i] = np.mean(vals)
        r_std[i] = np.std(vals)
    fig, ax = plt.subplots()
    ax.errorbar(ps, r_mean, yerr=r_std, fmt="o-", color="C0", capsize=5)
    ax.set_xscale("log")
    ax.set_xlabel("p")
    ax.set_ylabel(r"$r_\infty$")
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
    ax.set_xlabel("p")
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
                r_inf = r_stationary(r)
                r_vals.append(r_inf)
                tau = tau_sync(t, r)
                if tau is not None and r_inf > ORDER_THRESHOLD:
                    tau_vals.append(tau)
            r_grid[i, j] = np.mean(r_vals)
            if len(tau_vals) >= min_sync_count(len(files)):
                tau_grid[i, j] = np.mean(tau_vals)
    out_r = heatmap(r_grid, ps, Ks, r"$r_\infty$", "heatmap_rpK.png")
    out_tau = heatmap(tau_grid, ps, Ks, "τ (s)",
                      "heatmap_taupK.png", cmap="plasma")
    return out_r, out_tau


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    by_pK = load_by_pK()
    n_seeds = min(len(v) for v in by_pK.values())
    out_comp, n_nets = plot_components_vs_p()
    out_rp = plot_rp_Kcut(by_pK)
    out_r, out_tau = plot_heatmaps(by_pK)
    print(f"saved -> {out_comp} (promedio sobre {n_nets} redes por p)")
    print(f"saved -> {out_rp} (promedio sobre {n_seeds} realizaciones)")
    print(f"saved -> {out_r}")
    print(f"saved -> {out_tau}")


if __name__ == "__main__":
    main()
