import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

public class KuramotoSim {

    enum Topology { COMPLETE, RANDOM, RING }

    public static void main(String[] args) throws IOException {
        Map<String, String> a = parseArgs(args);
        int N = i(a, "N", 500);
        double K = d(a, "K", 1.0);
        Topology topo = Topology.valueOf(a.getOrDefault("topology", "complete").toUpperCase());
        double p = d(a, "p", 0.5);
        int v = i(a, "v", 1);
        double muOmega = d(a, "muOmega", 1.0);
        double sigmaOmega = d(a, "sigmaOmega", 0.1);
        double dt = d(a, "dt", 0.01);
        double tSim = d(a, "tSim", 100.0);
        long seed = Long.parseLong(a.getOrDefault("seed", "42"));
        long netSeed = Long.parseLong(a.getOrDefault("netSeed", String.valueOf(seed)));
        int dumpEvery = i(a, "dumpEvery", 1);
        String output = a.getOrDefault("output", "kuramoto.csv");
        boolean dumpPhases = Boolean.parseBoolean(a.getOrDefault("dumpPhases", "true"));

        Random rng = new Random(seed);
        Random netRng = new Random(netSeed);

        double[] omega = new double[N];
        double[] theta = new double[N];
        for (int i = 0; i < N; i++) {
            omega[i] = muOmega + sigmaOmega * rng.nextGaussian();
            theta[i] = 2.0 * Math.PI * rng.nextDouble();
        }

        int[][] nbr = buildNeighbors(N, topo, p, v, netRng);

        try (BufferedWriter out = new BufferedWriter(new FileWriter(output))) {
            out.write(String.format(
                "# N=%d K=%.6f dt=%.6f tSim=%.6f topology=%s p=%.6f v=%d muOmega=%.6f sigmaOmega=%.6f seed=%d netSeed=%d dumpEvery=%d%n",
                N, K, dt, tSim, topo, p, v, muOmega, sigmaOmega, seed, netSeed, dumpEvery));
            out.write("t,r");
            if (dumpPhases) for (int i = 0; i < N; i++) out.write(",theta_" + i);
            out.write("\n");

            double[] k1 = new double[N], k2 = new double[N], k3 = new double[N], k4 = new double[N];
            double[] tmp = new double[N];

            int steps = (int) Math.round(tSim / dt);
            for (int step = 0; step <= steps; step++) {
                double t = step * dt;
                if (step % dumpEvery == 0) writeRow(out, t, theta, dumpPhases);
                deriv(theta, omega, nbr, K, k1);
                for (int i = 0; i < N; i++) tmp[i] = theta[i] + 0.5 * dt * k1[i];
                deriv(tmp, omega, nbr, K, k2);
                for (int i = 0; i < N; i++) tmp[i] = theta[i] + 0.5 * dt * k2[i];
                deriv(tmp, omega, nbr, K, k3);
                for (int i = 0; i < N; i++) tmp[i] = theta[i] + dt * k3[i];
                deriv(tmp, omega, nbr, K, k4);
                for (int i = 0; i < N; i++) {
                    theta[i] += dt / 6.0 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]);
                }
            }
        }
    }

    static void deriv(double[] theta, double[] omega, int[][] nbr, double K, double[] out) {
        int N = theta.length;
        for (int i = 0; i < N; i++) {
            double ti = theta[i];
            int[] nb = nbr[i];
            double sum = 0.0;
            for (int idx = 0; idx < nb.length; idx++) sum += Math.sin(theta[nb[idx]] - ti);
            out[i] = omega[i] + K * sum;
        }
    }

    static int[][] buildNeighbors(int N, Topology topo, double p, int v, Random rng) {
        int[][] nbr = new int[N][];
        switch (topo) {
            case COMPLETE:
                for (int i = 0; i < N; i++) {
                    int[] arr = new int[N - 1];
                    int idx = 0;
                    for (int j = 0; j < N; j++) if (j != i) arr[idx++] = j;
                    nbr[i] = arr;
                }
                break;
            case RANDOM:
                List<List<Integer>> tmp = new ArrayList<>(N);
                for (int i = 0; i < N; i++) tmp.add(new ArrayList<>());
                for (int i = 0; i < N; i++) {
                    for (int j = i + 1; j < N; j++) {
                        if (rng.nextDouble() < p) {
                            tmp.get(i).add(j);
                            tmp.get(j).add(i);
                        }
                    }
                }
                for (int i = 0; i < N; i++) {
                    List<Integer> li = tmp.get(i);
                    int[] arr = new int[li.size()];
                    for (int j = 0; j < li.size(); j++) arr[j] = li.get(j);
                    nbr[i] = arr;
                }
                break;
            case RING:
                for (int i = 0; i < N; i++) {
                    int[] arr = new int[2 * v];
                    int idx = 0;
                    for (int dd = 1; dd <= v; dd++) {
                        arr[idx++] = ((i - dd) % N + N) % N;
                        arr[idx++] = (i + dd) % N;
                    }
                    nbr[i] = arr;
                }
                break;
        }
        return nbr;
    }

    static void writeRow(BufferedWriter out, double t, double[] theta, boolean dumpPhases) throws IOException {
        int N = theta.length;
        double cx = 0.0, cy = 0.0;
        for (int i = 0; i < N; i++) {
            cx += Math.cos(theta[i]);
            cy += Math.sin(theta[i]);
        }
        cx /= N;
        cy /= N;
        double r = Math.sqrt(cx * cx + cy * cy);
        StringBuilder sb = new StringBuilder();
        sb.append(t).append(',').append(r);
        if (dumpPhases) for (int i = 0; i < N; i++) sb.append(',').append(theta[i]);
        sb.append('\n');
        out.write(sb.toString());
    }

    static Map<String, String> parseArgs(String[] args) {
        Map<String, String> m = new HashMap<>();
        for (int i = 0; i < args.length; i++) {
            if (args[i].startsWith("--") && i + 1 < args.length) {
                m.put(args[i].substring(2), args[i + 1]);
                i++;
            }
        }
        return m;
    }

    static int i(Map<String, String> m, String k, int d) {
        return m.containsKey(k) ? Integer.parseInt(m.get(k)) : d;
    }

    static double d(Map<String, String> m, String k, double d) {
        return m.containsKey(k) ? Double.parseDouble(m.get(k)) : d;
    }
}
