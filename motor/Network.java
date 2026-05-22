import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class Network {

    public enum Topology { COMPLETE, RANDOM, RING }

    public static int[][] build(int N, Topology topo, double p, int v, Random rng) {
        switch (topo) {
            case COMPLETE: return complete(N);
            case RANDOM:   return random(N, p, rng);
            case RING:     return ring(N, v);
            default: throw new IllegalArgumentException("Unknown topology: " + topo);
        }
    }

    private static int[][] complete(int N) {
        int[][] nbr = new int[N][N - 1];
        for (int i = 0; i < N; i++) {
            int idx = 0;
            for (int j = 0; j < N; j++) if (j != i) nbr[i][idx++] = j;
        }
        return nbr;
    }

    private static int[][] random(int N, double p, Random rng) {
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
        int[][] nbr = new int[N][];
        for (int i = 0; i < N; i++) {
            List<Integer> li = tmp.get(i);
            int[] arr = new int[li.size()];
            for (int j = 0; j < li.size(); j++) arr[j] = li.get(j);
            nbr[i] = arr;
        }
        return nbr;
    }

    private static int[][] ring(int N, int v) {
        int[][] nbr = new int[N][2 * v];
        for (int i = 0; i < N; i++) {
            int idx = 0;
            for (int d = 1; d <= v; d++) {
                nbr[i][idx++] = ((i - d) % N + N) % N;
                nbr[i][idx++] = (i + d) % N;
            }
        }
        return nbr;
    }
}
