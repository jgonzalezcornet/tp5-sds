"""Genera las tres animaciones estilo anillo (completa, aleatoria, anillo)."""
from pathlib import Path

from lib import OUT_ROOT, ensure_compiled, run_one
from anim_ring import make_ring_animation

OUT_CSV = OUT_ROOT / "anim_ring_csv"
OUT_GIF = Path(__file__).resolve().parent.parent / "animations" / "ring_style"

N = 600
DT = 0.001
MU_OMEGA = 1.0
SIGMA_OMEGA = 0.1
SEED = 1000

CONFIGS = [
    {
        "label": "complete_K0.5",
        "topology": "COMPLETE", "K": 0.5, "tSim": 10.0, "dumpEvery": 50,
    },
    {
        "label": "random_p0.05_K0.5",
        "topology": "RANDOM", "p": 0.05, "K": 0.5, "tSim": 10.0, "dumpEvery": 50,
    },
    {
        # Mismo p, al K del corte de análisis (enunciado v2): sincroniza más lento.
        "label": "random_p0.05_K0.1",
        "topology": "RANDOM", "p": 0.05, "K": 0.1, "tSim": 10.0, "dumpEvery": 50,
    },
    {
        "label": "ring_v5_K1",
        "topology": "RING", "v": 5, "K": 1.0, "tSim": 30.0, "dumpEvery": 150,
    },
]


def main():
    ensure_compiled()
    OUT_CSV.mkdir(parents=True, exist_ok=True)
    OUT_GIF.mkdir(parents=True, exist_ok=True)

    for cfg in CONFIGS:
        label = cfg["label"]
        csv_path = OUT_CSV / f"{label}.csv"
        gif_path = OUT_GIF / f"ring_anim_{label}.gif"

        run_one(
            N=N, K=cfg["K"], topology=cfg["topology"],
            dt=DT, tSim=cfg["tSim"],
            seed=SEED, netSeed=SEED,
            output=csv_path,
            p=cfg.get("p"), v=cfg.get("v"),
            dumpEvery=cfg["dumpEvery"], dumpPhases=True,
            muOmega=MU_OMEGA, sigmaOmega=SIGMA_OMEGA,
        )
        make_ring_animation(csv_path, out_path=gif_path,
                            fps=20, max_frames=200)


if __name__ == "__main__":
    main()
