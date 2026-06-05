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

# Umbral para K_c: minimo K con r_inf >= R_C. En r=0.5 el sistema queda mas
# cerca de la sincronizacion (r=1) que del desorden (r=0).
R_C = 0.5

# Subconjunto de K mostrado en r(t): incoherente -> critico -> sincronizacion
# cada vez mas rapida. Se omiten los K altos redundantes (todos suben a 1 al
# instante y dan curvas casi identicas).
RT_SHOW = {"0", "0.0003", "0.0005", "0.001", "0.003", "0.1"}


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
    Ks = [K for K in sorted(by_K) if f"{K:g}" in RT_SHOW]
    fig, ax = plt.subplots()
    cmap = plt.colormaps["viridis"]
    n_seeds = min(len(by_K[K]) for K in Ks)
    for i, K in enumerate(Ks):
        traces = [load_rt(f) for f in by_K[K]]
        t = traces[0][0]
        r_mean = np.stack([r for _, r in traces]).mean(axis=0)
        color = cmap(i / max(1, len(Ks) - 1))
        ax.plot(t, r_mean, color=color, label=f"K = {K:g}")
    ax.set_xlabel("t (s)")
    ax.set_ylabel("r")
    ax.set_ylim(0, 1.05)
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=16)
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
            vals.append(r_stationary(r))
        r_inf_mean[i] = np.mean(vals)
        r_inf_std[i] = np.std(vals)
    fig, ax = plt.subplots()
    Ks_arr = np.array(Ks)
    pos = Ks_arr > 0
    ax.errorbar(Ks_arr[pos], r_inf_mean[pos], yerr=r_inf_std[pos],
                fmt="o-", color="C0", capsize=5)

    # --- K_c: minimo K con r_inf >= 0.5 (el sistema queda mas cerca de la
    # sincronizacion que del desorden). Se interpola el cruce en escala log-K. ---
    Ks_pos = Ks_arr[pos]
    r_pos = r_inf_mean[pos]
    Kc = None
    for j in range(len(r_pos)):
        if r_pos[j] >= R_C:
            if j == 0:
                Kc = Ks_pos[0]
            else:
                logK0, logK1 = np.log10(Ks_pos[j - 1]), np.log10(Ks_pos[j])
                frac = (R_C - r_pos[j - 1]) / (r_pos[j] - r_pos[j - 1])
                Kc = 10 ** (logK0 + frac * (logK1 - logK0))
            break

    if Kc is not None:
        ax.axhline(R_C, color="0.6", linestyle=":", linewidth=1, zorder=2)
        ax.axvline(Kc, color="C3", linestyle="--", linewidth=1.5, zorder=3)
        ax.text(
            Kc, 0.04, f"  $K_c = {Kc:.2g}$",
            fontsize=18, color="C3",
            ha="left", va="bottom",
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
            tau = tau_sync(t, r)
            if tau is not None and r_stationary(r) > 0.5:
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
