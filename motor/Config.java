import java.util.HashMap;
import java.util.Map;

public record Config(
    int N,
    double K,
    Network.Topology topo,
    double p,
    int v,
    double muOmega,
    double sigmaOmega,
    double dt,
    double tSim,
    long seed,
    long netSeed,
    int dumpEvery,
    boolean dumpPhases,
    String output
) {

    public static Config fromArgs(String[] args) {
        Map<String, String> a = parse(args);
        String seedStr = a.getOrDefault("seed", "42");
        return new Config(
            i(a, "N", 500),
            d(a, "K", 1.0),
            Network.Topology.valueOf(a.getOrDefault("topology", "complete").toUpperCase()),
            d(a, "p", 0.5),
            i(a, "v", 1),
            d(a, "muOmega", 1.0),
            d(a, "sigmaOmega", 0.1),
            d(a, "dt", 0.01),
            d(a, "tSim", 100.0),
            Long.parseLong(seedStr),
            Long.parseLong(a.getOrDefault("netSeed", seedStr)),
            i(a, "dumpEvery", 1),
            Boolean.parseBoolean(a.getOrDefault("dumpPhases", "true")),
            a.getOrDefault("output", "kuramoto.csv")
        );
    }

    private static Map<String, String> parse(String[] args) {
        Map<String, String> m = new HashMap<>();
        for (int i = 0; i < args.length; i++) {
            if (args[i].startsWith("--") && i + 1 < args.length) {
                m.put(args[i].substring(2), args[i + 1]);
                i++;
            }
        }
        return m;
    }

    private static int i(Map<String, String> m, String k, int def) {
        return m.containsKey(k) ? Integer.parseInt(m.get(k)) : def;
    }

    private static double d(Map<String, String> m, String k, double def) {
        return m.containsKey(k) ? Double.parseDouble(m.get(k)) : def;
    }
}
