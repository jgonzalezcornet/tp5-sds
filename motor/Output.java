import java.io.BufferedWriter;
import java.io.IOException;

public class Output {

    public static void writeHeader(BufferedWriter out, Config c) throws IOException {
        out.write(String.format(
            "# N=%d K=%.6f dt=%.6f tSim=%.6f topology=%s p=%.6f v=%d muOmega=%.6f sigmaOmega=%.6f seed=%d netSeed=%d dumpEvery=%d%n",
            c.N(), c.K(), c.dt(), c.tSim(), c.topo(), c.p(), c.v(),
            c.muOmega(), c.sigmaOmega(), c.seed(), c.netSeed(), c.dumpEvery()));
        out.write("t,r");
        if (c.dumpPhases()) {
            for (int i = 0; i < c.N(); i++) out.write(",theta_" + i);
        }
        out.write("\n");
    }

    public static void writeRow(BufferedWriter out, double t, double[] theta, boolean dumpPhases) throws IOException {
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
        if (dumpPhases) {
            for (int i = 0; i < N; i++) sb.append(',').append(theta[i]);
        }
        sb.append('\n');
        out.write(sb.toString());
    }
}
