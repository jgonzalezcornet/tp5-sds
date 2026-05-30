import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Random;

public class NetworkDump {
    public static void main(String[] args) throws IOException {
        Config c = Config.fromArgs(args);
        Random netRng = new Random(c.netSeed());
        int[][] nbr = Network.build(c.N(), c.topo(), c.p(), c.v(), netRng);
        try (BufferedWriter out = new BufferedWriter(new FileWriter(c.output()))) {
            for (int i = 0; i < c.N(); i++) {
                for (int j : nbr[i]) {
                    if (j > i) out.write(i + "," + j + "\n");
                }
            }
        }
    }
}
