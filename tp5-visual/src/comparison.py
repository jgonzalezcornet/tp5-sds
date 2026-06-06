"""Comparación de τ(K) entre las tres topologías."""
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import style  # noqa: F401
from lib import (ORDER_THRESHOLD, OUT_ROOT, load_rt, min_sync_count,
                 r_stationary, tau_sync)

OUT_DIR = Path(__file__).resolve().parent.parent / "graphs"


def collect_tau(files_by_K):
    Ks = sorted(files_by_K.keys())
    Ks_plot, tau_mean, tau_std = [], [], []
    for K in Ks:
        taus = []
        for f in files_by_K[K]:
            t, r = load_rt(f)
            tau = tau_sync(t, r)
            if tau is not None and r_stationary(r) > ORDER_THRESHOLD:
                taus.append(tau)
        if len(taus) >= min_sync_count(len(files_by_K[K])):
            Ks_plot.append(K)
            tau_mean.append(np.mean(taus))
            tau_std.append(np.std(taus))
    return np.array(Ks_plot), np.array(tau_mean), np.array(tau_std)


def load_complete():
    files = sorted((OUT_ROOT / "complete_Ksweep").glob("K*_seed*.csv"))
    by_K = {}
    for f in files:
        m = re.match(r"K([0-9.]+)_seed\d+\.csv", f.name)
        if m:
            by_K.setdefault(float(m.group(1)), []).append(f)
    return by_K


def load_random_at_p(p_target=1.0):
    files = sorted((OUT_ROOT / "random_pK").glob(f"p{p_target:g}_K*_seed*.csv"))
    by_K = {}
    for f in files:
        m = re.match(r"p[0-9.]+_K([0-9.]+)_seed\d+\.csv", f.name)
        if m:
            by_K.setdefault(float(m.group(1)), []).append(f)
    return by_K


def load_ring_at_v(v_target=10):
    files = sorted((OUT_ROOT / "ring_vK").glob(f"v{v_target}_K*_seed*.csv"))
    by_K = {}
    for f in files:
        m = re.match(r"v\d+_K([0-9.]+)_seed\d+\.csv", f.name)
        if m:
            by_K.setdefault(float(m.group(1)), []).append(f)
    return by_K


def plot_comparison(p_random, random_label, out_name):
    fig, ax = plt.subplots()

    K_c, t_c, s_c = collect_tau(load_complete())
    ax.errorbar(K_c, t_c, yerr=s_c, fmt="o-", color="C0", capsize=5,
                label="Completa")

    K_r, t_r, s_r = collect_tau(load_random_at_p(p_random))
    ax.errorbar(K_r, t_r, yerr=s_r, fmt="s-", color="C1", capsize=5,
                label=random_label)

    K_g, t_g, s_g = collect_tau(load_ring_at_v(10))
    ax.errorbar(K_g, t_g, yerr=s_g, fmt="^-", color="C2", capsize=5,
                label="Anillo (v=10)")

    ax.set_xlabel("K")
    ax.set_ylabel("τ (s)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.legend(loc="best")

    out = OUT_DIR / out_name
    fig.savefig(out)
    plt.close(fig)
    print(f"saved -> {out}")


def main():
    # Comparativa original (p=1, el régimen más conectado de la red aleatoria).
    plot_comparison(1.0, "Aleatoria (p=1)", "tau_comparison.png")
    # Comparativa dentro del rango del enunciado v2 (p ∈ [1e-4, 1e-1]): el régimen
    # más conectado en especificación es p=0.1.
    plot_comparison(0.1, "Aleatoria (p=0.1)", "tau_comparison_p0.1.png")


if __name__ == "__main__":
    main()
