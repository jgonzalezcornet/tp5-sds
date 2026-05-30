import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Random;

public class KuramotoSim {

    public static void main(String[] args) throws IOException {
        Config c = Config.fromArgs(args);

        Random rng = new Random(c.seed());
        Random netRng = new Random(c.netSeed());

        double[] omega = new double[c.N()];
        double[] theta = new double[c.N()];
        for (int i = 0; i < c.N(); i++) {
            omega[i] = c.muOmega() + c.sigmaOmega() * rng.nextGaussian();
            theta[i] = 2.0 * Math.PI * rng.nextDouble();
        }

        int[][] nbr = Network.build(c.N(), c.topo(), c.p(), c.v(), netRng);
        Integrator rk4 = new Integrator(c.N());

        try (BufferedWriter out = new BufferedWriter(new FileWriter(c.output()))) {
            Output.writeHeader(out, c);

            int steps = (int) Math.round(c.tSim() / c.dt());
            for (int step = 0; step <= steps; step++) {
                if (step % c.dumpEvery() == 0) {
                    Output.writeRow(out, step * c.dt(), theta, c.dumpPhases());
                }
                rk4.step(theta, omega, nbr, c.K(), c.dt());
            }
        }
    }
}
