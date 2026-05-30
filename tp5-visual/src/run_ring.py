"""Barrido (v, K) para red anillo. 12 seeds por par. tSim grande por transitorios largos."""
from lib import OUT_ROOT, ensure_compiled, run_batch

N = 600
DT = 0.001
T_SIM = 1500.0
DUMP_EVERY = 100
MU_OMEGA = 1.0
SIGMA_OMEGA = 0.1
VS = list(range(1, 11))
KS = [0.01, 0.03, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0]
SEEDS = list(range(1000, 1012))

OUT_DIR = OUT_ROOT / "ring_vK"


def main():
    ensure_compiled()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    configs = []
    for v in VS:
        for K in KS:
            K_str = f"{K:g}"
            for i, seed in enumerate(SEEDS):
                configs.append({
                    "N": N, "K": K, "topology": "RING", "v": v,
                    "dt": DT, "tSim": T_SIM,
                    "seed": seed, "netSeed": seed,
                    "dumpEvery": DUMP_EVERY, "dumpPhases": False,
                    "muOmega": MU_OMEGA, "sigmaOmega": SIGMA_OMEGA,
                    "output": OUT_DIR / f"v{v}_K{K_str}_seed{i}.csv",
                })
    print(f"running {len(configs)} ring sims...")
    paths = run_batch(configs)
    print(f"done: {len(paths)} files in {OUT_DIR}")


if __name__ == "__main__":
    main()
