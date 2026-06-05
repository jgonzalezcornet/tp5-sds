"""Red totalmente conectada: r(t), r∞(K), τ(K)."""
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import style  # noqa: F401
from lib import OUT_ROOT, load_rt, r_stationary, tau_sync

DATA_DIR = OUT_ROOT / "complete_Ksweep"
FINE_DIR = OUT_ROOT / "complete_Ksweep_fine"
OUT_DIR = Path(__file__).resolve().parent.parent / "graphs" / "complete"

# Ventana de r_inf usada para ajustar K_c (region de escaleo: por encima del
# piso incoherente ~1/sqrt(N) y por debajo de la saturacion).
R_FIT_LO, R_FIT_HI = 0.15, 0.8


def load_by_K(data_dir=DATA_DIR):
    files = sorted(data_dir.glob("K*_seed*.csv"))
    by_K = {}
    for f in files:
        m = re.match(r"K([0-9.]+)_seed\d+\.csv", f.name)
        if not m:
            continue
        K = float(m.group(1))
        by_K.setdefault(K, []).append(f)
    return by_K


def plot_rt(by_K):
    Ks = sorted(by_K.keys())
    fig, ax = plt.subplots()
    cmap = plt.colormaps["viridis"]
    n_seeds = min(len(v) for v in by_K.values())
    for i, K in enumerate(Ks):
        traces = [load_rt(f) for f in by_K[K]]
        t = traces[0][0]
        rs = np.stack([r for _, r in traces])
        r_mean = rs.mean(axis=0)
        color = cmap(i / max(1, len(Ks) - 1))
        ax.plot(t, r_mean, color=color, label=f"K = {K:g}")
    ax.set_xlabel("t (s)")
    ax.set_ylabel("r")
    ax.set_ylim(0, 1.05)
    ax.legend(loc="lower right", fontsize=14, ncol=2)
    out = OUT_DIR / "rt.png"
    fig.savefig(out)
    plt.close(fig)
    return out, n_seeds


def plot_rK(by_K):
    Ks = sorted(by_K.keys())
    r_inf_mean = np.zeros(len(Ks))
    r_inf_std = np.zeros(len(Ks))
    for i, K in enumerate(Ks):
        vals = []
        for f in by_K[K]:
            _, r = load_rt(f)
            vals.append(r_stationary(r, late_frac=0.2))
        r_inf_mean[i] = np.mean(vals)
        r_inf_std[i] = np.std(vals)
    fig, ax = plt.subplots()
    Ks_arr = np.array(Ks)
    pos = Ks_arr > 0
    ax.errorbar(Ks_arr[pos], r_inf_mean[pos], yerr=r_inf_std[pos],
                fmt="o-", color="C0", capsize=5)

    # --- K_c por escaleo del parametro de orden ---
    # Cerca del umbral r_inf ~ sqrt((K - K_c)/K_c), es decir r_inf^2 es lineal
    # en K. Se ajusta una recta a r_inf^2 vs K en la region de subida y K_c es
    # su raiz (donde r^2 -> 0): el acoplamiento en que emerge la sincronizacion.
    Ks_pos = Ks_arr[pos]
    r_pos = r_inf_mean[pos]
    band = (r_pos >= R_FIT_LO) & (r_pos <= R_FIT_HI)
    Kc = None
    if band.sum() >= 2:
        Kfit = Ks_pos[band]
        slope, intercept = np.polyfit(Kfit, r_pos[band] ** 2, 1)
        Kc = -intercept / slope
        Kline = np.linspace(Kc, Kfit.max(), 100)
        ax.plot(Kline, np.sqrt(np.clip(slope * (Kline - Kc), 0, None)),
                color="C3", linestyle=":", linewidth=1.5, zorder=3)

    if Kc is not None:
        ax.axvline(Kc, color="C3", linestyle="--", linewidth=1.5, zorder=3)
        ax.text(
            Kc, 0.5, f"  $K_c = {Kc:.2g}$",
            fontsize=20, color="C3",
            verticalalignment="center",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor="C3", alpha=0.9),
            zorder=4,
        )

    ax.set_xscale("log")
    ax.set_xlabel("K")
    ax.set_ylabel("r")
    ax.set_ylim(0, 1.05)
    out = OUT_DIR / "rK.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def plot_tauK(by_K):
    Ks = sorted(by_K.keys())
    tau_mean = []
    tau_std = []
    Ks_plot = []
    for K in Ks:
        taus = []
        for f in by_K[K]:
            t, r = load_rt(f)
            tau = tau_sync(t, r, frac=0.95, late_frac=0.2, smooth_pts=20)
            r_late = float(np.mean(r[int(len(r) * 0.8):]))
            if tau is not None and r_late > 0.5:
                taus.append(tau)
        if len(taus) >= 3:
            tau_mean.append(np.mean(taus))
            tau_std.append(np.std(taus))
            Ks_plot.append(K)
    fig, ax = plt.subplots()
    ax.errorbar(Ks_plot, tau_mean, yerr=tau_std, fmt="s-", color="C1", capsize=5)
    ax.set_xscale("log")
    ax.set_xlabel("K")
    ax.set_ylabel("τ (s)")
    out = OUT_DIR / "tauK.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    by_K = load_by_K()
    out_rt, n_seeds = plot_rt(by_K)
    by_K_rK = {**by_K}
    if FINE_DIR.exists():
        for K, files in load_by_K(FINE_DIR).items():
            by_K_rK.setdefault(K, []).extend(files)
    out_rK = plot_rK(by_K_rK)
    out_tauK = plot_tauK(by_K)
    print(f"saved -> {out_rt} (promedio sobre {n_seeds} realizaciones)")
    print(f"saved -> {out_rK}")
    print(f"saved -> {out_tauK}")


if __name__ == "__main__":
    main()
