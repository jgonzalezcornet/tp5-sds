"""Barrido de K para red totalmente conectada. 12 seeds por K."""
from lib import OUT_ROOT, ensure_compiled, run_batch

N = 600
DT = 0.001
T_SIM = 50.0
DUMP_EVERY = 10
MU_OMEGA = 1.0
SIGMA_OMEGA = 0.1
KS = [0, 0.0001, 0.0003, 0.0005, 0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1]
SEEDS = list(range(1000, 1012))

OUT_DIR = OUT_ROOT / "complete_Ksweep"


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
    print(f"running {len(configs)} complete sims...")
    paths = run_batch(configs)
    print(f"done: {len(paths)} files in {OUT_DIR}")


if __name__ == "__main__":
    main()
