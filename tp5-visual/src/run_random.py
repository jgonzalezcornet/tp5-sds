"""Barrido (p, K) para red aleatoria. 12 seeds por par."""
from lib import OUT_ROOT, ensure_compiled, run_batch

N = 600
DT = 0.001
T_SIM = 50.0
DUMP_EVERY = 10
MU_OMEGA = 1.0
SIGMA_OMEGA = 0.1
# Rango de p del enunciado v2: 10 valores log en [1e-4, 1e-1].
PS = [1e-4, 2e-4, 5e-4, 1e-3, 2e-3, 5e-3, 1e-2, 2e-2, 5e-2, 1e-1]
# Nota: la comparativa original entre topologías (comparison.py) usa la red
# aleatoria a p=1.0, fuera de este rango. Esos datos heredados (p=0.3, p=1.0)
# se conservan en tp5-output/random_pK/ pero ya no se regeneran acá. Para
# reproducirlos, agregar 0.3 y 1.0 a PS. La comparativa en-spec usa p=0.1.
KS = [0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0]
SEEDS = list(range(1000, 1012))

OUT_DIR = OUT_ROOT / "random_pK"


def main():
    ensure_compiled()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    configs = []
    for p in PS:
        p_str = f"{p:g}"
        for K in KS:
            K_str = f"{K:g}"
            for i, seed in enumerate(SEEDS):
                configs.append({
                    "N": N, "K": K, "topology": "RANDOM", "p": p,
                    "dt": DT, "tSim": T_SIM,
                    "seed": seed, "netSeed": seed,
                    "dumpEvery": DUMP_EVERY, "dumpPhases": False,
                    "muOmega": MU_OMEGA, "sigmaOmega": SIGMA_OMEGA,
                    "output": OUT_DIR / f"p{p_str}_K{K_str}_seed{i}.csv",
                })
    print(f"running {len(configs)} random sims...")
    paths = run_batch(configs)
    print(f"done: {len(paths)} files in {OUT_DIR}")


if __name__ == "__main__":
    main()
