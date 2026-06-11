"""Utilities: CSV loading, tau_s detection, parallel sim runner."""
import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROJECT = ROOT.parent
MOTOR_DIR = PROJECT / "tp5-code"
OUT_ROOT = PROJECT / "tp5-output"


def load_rt(path):
    df = pd.read_csv(path, comment="#")
    return df["t"].to_numpy(), df["r"].to_numpy()


def load_phases(path):
    df = pd.read_csv(path, comment="#")
    t = df["t"].to_numpy()
    r = df["r"].to_numpy()
    theta_cols = [c for c in df.columns if c.startswith("theta_")]
    theta = df[theta_cols].to_numpy() if theta_cols else None
    return t, r, theta


def parse_header(path):
    with open(path) as f:
        first = f.readline().strip()
    if not first.startswith("#"):
        return {}
    out = {}
    for tok in first.lstrip("# ").split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            out[k] = v
    return out


def stationary_start(r, delta=0.02, smooth_frac=0.02, tail_frac=0.1, min_win=0.05):
    """Settling time (as an index): primer indice a partir del cual r(t) se queda
    dentro de una banda +-delta de su valor de regimen. `delta=0.02` es la banda
    del 2% (convencion estandar de settling time); r esta acotado en [0,1]. La
    ventana se adapta al transitorio real en vez de usar un corte fijo.
    `min_win` garantiza una ventana minima para casos que no llegan a regimen."""
    n = len(r)
    if n == 0:
        return 0
    w = max(1, int(n * smooth_frac))
    r_smooth = pd.Series(r).rolling(w, center=True, min_periods=1).mean().to_numpy()
    r_ss = float(r_smooth[int(n * (1 - tail_frac)):].mean())
    outside = np.where(np.abs(r_smooth - r_ss) > delta)[0]
    i = 0 if len(outside) == 0 else int(outside[-1]) + 1
    return min(i, int(n * (1 - min_win)))


def r_stationary(r, **kw):
    """Valor estacionario de r: promedio temporal sobre la ventana establecida
    [t_est, t_f] (ver `stationary_start`)."""
    return float(np.mean(r[stationary_start(r, **kw):]))


def tau_sync(t, r):
    """Tiempo de sincronizacion (= llegada al estado estacionario): el settling
    time, el mismo instante que define el inicio de la ventana de r_inf. Es decir,
    tau y t_est son la misma magnitud (ver `stationary_start`)."""
    n = len(t)
    if n == 0:
        return None
    return float(t[stationary_start(r)])


MIN_SYNC_FRAC = 0.25  # fraccion de realizaciones que deben llegar a un estado
                      # estacionario ordenado para colorear la celda (piso de 3).
ORDER_THRESHOLD = 0.2  # r_inf por encima del cual una realizacion se considera
                       # que desarrollo orden (no se quedo en el piso ~1/sqrt(N)).
                       # Umbral del filtro de los mapas de tau (NO el de K_c).


def min_sync_count(n):
    """Cantidad minima de realizaciones que deben sincronizar (r_inf > 0.5) para
    promediar tau en una celda. Es el 25% de n, con un piso estadistico de 3.
    Asi el criterio escala con la cantidad de seeds: 12 -> 3, 50 -> 13."""
    return max(3, int(np.ceil(MIN_SYNC_FRAC * n)))


def run_one(N, K, topology, dt, tSim, seed, output,
            netSeed=None, p=None, v=None, dumpEvery=None, dumpPhases=False,
            muOmega=None, sigmaOmega=None):
    """Run one Kuramoto sim. Returns path to output CSV."""
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    cmd = ["java", "KuramotoSim",
           "--N", str(N), "--K", str(K), "--topology", topology,
           "--dt", str(dt), "--tSim", str(tSim),
           "--seed", str(seed), "--output", str(output)]
    if netSeed is not None:
        cmd += ["--netSeed", str(netSeed)]
    if p is not None:
        cmd += ["--p", str(p)]
    if v is not None:
        cmd += ["--v", str(v)]
    if dumpEvery is not None:
        cmd += ["--dumpEvery", str(dumpEvery)]
    cmd += ["--dumpPhases", "true" if dumpPhases else "false"]
    if muOmega is not None:
        cmd += ["--muOmega", str(muOmega)]
    if sigmaOmega is not None:
        cmd += ["--sigmaOmega", str(sigmaOmega)]
    res = subprocess.run(cmd, cwd=MOTOR_DIR, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"sim failed: {res.stderr or res.stdout}")
    return Path(output)


def run_batch(configs, max_workers=None):
    """Run a list of run_one(**cfg) calls in parallel. Returns list of paths."""
    if max_workers is None:
        max_workers = max(1, os.cpu_count() - 1)
    paths = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {ex.submit(run_one, **cfg): cfg for cfg in configs}
        for fut in as_completed(futs):
            paths.append(fut.result())
    return paths


def add_param_box(fig, lines, x=0.97, y=0.5):
    """Add a parameter side panel to a figure (Guia 1.7)."""
    fig.text(x, y, "\n".join(lines), fontsize=16,
             verticalalignment="center", horizontalalignment="right",
             bbox=dict(boxstyle="round", facecolor="white", edgecolor="gray"))


def fmt_num(s):
    """Format a numeric string from CSV header (e.g., '0.500000') nicely."""
    try:
        x = float(s)
        if x == int(x):
            return str(int(x))
        return f"{x:g}"
    except (TypeError, ValueError):
        return str(s)


def cell_edges(centers, log=False):
    """Convert an array of cell centers to cell edges suitable for pcolormesh.
    For log axes, midpoints are computed in log space."""
    c = np.asarray(centers, dtype=float)
    if log:
        lc = np.log(c)
        edges_log = np.concatenate([
            [lc[0] - 0.5 * (lc[1] - lc[0])],
            0.5 * (lc[:-1] + lc[1:]),
            [lc[-1] + 0.5 * (lc[-1] - lc[-2])],
        ])
        return np.exp(edges_log)
    edges = np.concatenate([
        [c[0] - 0.5 * (c[1] - c[0])],
        0.5 * (c[:-1] + c[1:]),
        [c[-1] + 0.5 * (c[-1] - c[-2])],
    ])
    return edges


def ensure_compiled():
    """Compile the Java sources if class files are missing or stale."""
    classes = list(MOTOR_DIR.glob("*.class"))
    sources = list(MOTOR_DIR.glob("*.java"))
    needs = (len(classes) < len(sources)) or any(
        s.stat().st_mtime > max((c.stat().st_mtime for c in classes), default=0)
        for s in sources
    )
    if needs:
        subprocess.run(["javac"] + [s.name for s in sources],
                       cwd=MOTOR_DIR, check=True)
