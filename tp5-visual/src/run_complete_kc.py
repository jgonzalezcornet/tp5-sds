"""Barrido fino de K en la transicion (red completa) para ajustar K_c.
Dataset aparte (no toca complete_Ksweep) usado solo por plot_rK."""
from lib import OUT_ROOT, ensure_compiled, run_batch

N = 600
DT = 0.001
T_SIM = 50.0
DUMP_EVERY = 10
MU_OMEGA = 1.0
SIGMA_OMEGA = 0.1
# Puntos extra dentro de la zona de transicion (~K_c teorico 2.7e-4),
# complementan los 1e-4/3e-4/5e-4 del barrido principal.
KS = [0.0002, 0.00025, 0.00035, 0.0004, 0.00045, 0.0006]
SEEDS = list(range(1000, 1012))

OUT_DIR = OUT_ROOT / "complete_Ksweep_fine"


def main():
    ensure_compiled()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    configs = []
    for K in KS:
        K_str = f"{K:g}"
        for i, seed in enumerate(SEEDS):
            configs.append({
                "N": N, "K": K, "topology": "COMPLETE",
                "dt": DT, "tSim": T_SIM,
                "seed": seed, "netSeed": seed,
                "dumpEvery": DUMP_EVERY, "dumpPhases": False,
                "muOmega": MU_OMEGA, "sigmaOmega": SIGMA_OMEGA,
                "output": OUT_DIR / f"K{K_str}_seed{i}.csv",
            })
    print(f"running {len(configs)} complete sims (fine K sweep)...")
    paths = run_batch(configs)
    print(f"done: {len(paths)} files in {OUT_DIR}")


if __name__ == "__main__":
    main()
