"""
Red totalmente conectada (Sistema 1, parte a).

Lo que pide el enunciado:
- Animación
- r(t) para distintos K, promediado sobre >10 realizaciones
- r(K) estacionario (con barras de error)
- τ_sync(K)
"""
import argparse
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

import style  # noqa: F401
from lib import (OUT_ROOT, add_param_box, ensure_compiled, load_rt,
                 r_stationary, run_batch, tau_sync)

PARAMS = ["N = 600", "dt = 10⁻³", "topología: completa", "realizaciones: 10"]

OUT_DIR = OUT_ROOT / "complete_Ksweep"
FIG_DIR = Path(__file__).parent / "figs" / "complete"


def run_sweep(Ks, n_realizations=10, N=600, dt=1e-3, tSim=50, base_seed=1000):
    """Run K-sweep for the complete topology."""
    ensure_compiled()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    configs = []
    for K in Ks:
        for s in range(n_realizations):
            output = OUT_DIR / f"K{K:g}_seed{s}.csv"
            if output.exists():
                continue
            configs.append(dict(N=N, K=K, topology="complete", dt=dt, tSim=tSim,
                                seed=base_seed + s, output=str(output),
                                dumpEvery=10, dumpPhases=False))
    if configs:
        print(f"Running {len(configs)} configs for complete topology...")
        run_batch(configs)
    print(f"All outputs ready in {OUT_DIR}")


def load_grouped(Ks=None):
    """Group CSVs by K. Returns dict K -> list of (t, r)."""
    data = {}
    for f in OUT_DIR.glob("K*_seed*.csv"):
        try:
            K = float(f.stem.split("_")[0].lstrip("K"))
        except ValueError:
            continue
        if Ks is not None and K not in Ks:
            continue
        data.setdefault(K, []).append(load_rt(f))
    return data


def plot_rt(data, fig_path, K_subset=None):
    """r(t) overlay for a subset of K values (defaults to a few representative)."""
    fig, ax = plt.subplots(figsize=(10, 6.5))
    Ks = sorted(data.keys())
    if K_subset is not None:
        Ks = [K for K in Ks if K in K_subset]
    cmap = plt.cm.viridis(np.linspace(0.0, 0.9, max(2, len(Ks))))
    for K, c in zip(Ks, cmap):
        runs = data[K]
        t = runs[0][0]
        rs = np.stack([r for _, r in runs])
        mean = rs.mean(axis=0)
        std = rs.std(axis=0)
        ax.plot(t, mean, color=c, lw=2.5, label=f"K = {K:g}")
        ax.fill_between(t, mean - std, mean + std, color=c, alpha=0.18)
    ax.set_xlabel("tiempo")
    ax.set_ylabel("parámetro de orden")
    ax.set_ylim(-0.02, 1.08)
    ax.legend(loc="center left", bbox_to_anchor=(0.05, 0.5),
              framealpha=0.92)
    ax.tick_params(axis="x", rotation=0)
    ax.tick_params(axis="y", rotation=0)
    fig.set_size_inches(11, 6.5)
    fig.subplots_adjust(right=0.74)
    add_param_box(fig, PARAMS, x=0.98, y=0.5)
    fig.savefig(fig_path)
    plt.close(fig)
    print(f"  {fig_path.name}")


def plot_rK(data, fig_path):
    Ks = sorted(data.keys())
    means, errs = [], []
    for K in Ks:
        vals = [r_stationary(r) for _, r in data[K]]
        means.append(float(np.mean(vals)))
        errs.append(float(np.std(vals, ddof=1) / np.sqrt(len(vals))) if len(vals) > 1 else 0.0)
    fig, ax = plt.subplots(figsize=(10, 6.5))
    ax.errorbar(Ks, means, yerr=errs, fmt="o", capsize=5, lw=1.5, ms=12,
                color="C0", markerfacecolor="C0", markeredgecolor="black")
    ax.set_xlabel("intensidad de acoplamiento")
    ax.set_ylabel("parámetro de orden estacionario")
    ax.set_ylim(-0.02, 1.08)
    ax.set_xlim(min(Ks) - 0.05, max(Ks) + 0.05)
    ax.tick_params(axis="x", rotation=0)
    ax.tick_params(axis="y", rotation=0)
    fig.set_size_inches(11, 6.5)
    fig.subplots_adjust(right=0.74)
    add_param_box(fig, PARAMS, x=0.98, y=0.5)
    fig.savefig(fig_path)
    plt.close(fig)
    print(f"  {fig_path.name}")


def plot_tauK(data, fig_path):
    Ks = sorted(data.keys())
    means, errs = [], []
    for K in Ks:
        vals = [tau_sync(t, r) for t, r in data[K]]
        vals = [v for v in vals if v is not None]
        if vals:
            means.append(float(np.mean(vals)))
            errs.append(float(np.std(vals, ddof=1) / np.sqrt(len(vals))) if len(vals) > 1 else 0.0)
        else:
            means.append(np.nan)
            errs.append(0.0)
    fig, ax = plt.subplots(figsize=(10, 6.5))
    ax.errorbar(Ks, means, yerr=errs, fmt="s", capsize=5, lw=1.5, ms=12,
                color="C3", markerfacecolor="C3", markeredgecolor="black")
    ax.set_xlabel("intensidad de acoplamiento")
    ax.set_ylabel("tiempo de sincronización")
    ax.set_xlim(min(Ks) - 0.05, max(Ks) + 0.05)
    ax.tick_params(axis="x", rotation=0)
    ax.tick_params(axis="y", rotation=0)
    fig.set_size_inches(11, 6.5)
    fig.subplots_adjust(right=0.74)
    add_param_box(fig, PARAMS, x=0.98, y=0.5)
    fig.savefig(fig_path)
    plt.close(fig)
    print(f"  {fig_path.name}")


def plot_all():
    data = load_grouped()
    if not data:
        print(f"No data in {OUT_DIR}. Run --run first.")
        return
    print(f"Loaded {sum(len(v) for v in data.values())} runs ({len(data)} K values).")
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    # subset of K for r(t) plot — too many lines saturate the plot
    K_subset = {0.0, 0.1, 0.5, 1.0}
    plot_rt(data, FIG_DIR / "rt.png", K_subset=K_subset)
    plot_rK(data, FIG_DIR / "rK.png")
    plot_tauK(data, FIG_DIR / "tauK.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true", help="Correr las simulaciones primero")
    ap.add_argument("--n-real", type=int, default=10)
    ap.add_argument("--N", type=int, default=600)
    ap.add_argument("--tSim", type=float, default=50)
    args = ap.parse_args()

    Ks = [0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 0.7, 1.0]
    if args.run:
        run_sweep(Ks, n_realizations=args.n_real, N=args.N, tSim=args.tSim)
    plot_all()


if __name__ == "__main__":
    main()
