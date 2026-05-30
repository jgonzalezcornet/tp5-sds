public class Integrator {

    private final int N;
    private final double[] k1, k2, k3, k4, tmp, sinBuf, cosBuf;

    public Integrator(int N) {
        this.N = N;
        this.k1 = new double[N];
        this.k2 = new double[N];
        this.k3 = new double[N];
        this.k4 = new double[N];
        this.tmp = new double[N];
        this.sinBuf = new double[N];
        this.cosBuf = new double[N];
    }

    public void step(double[] theta, double[] omega, int[][] nbr, double K, double dt) {
        Dynamics.deriv(theta, omega, nbr, K, sinBuf, cosBuf, k1);
        for (int i = 0; i < N; i++) tmp[i] = theta[i] + 0.5 * dt * k1[i];
        Dynamics.deriv(tmp, omega, nbr, K, sinBuf, cosBuf, k2);
        for (int i = 0; i < N; i++) tmp[i] = theta[i] + 0.5 * dt * k2[i];
        Dynamics.deriv(tmp, omega, nbr, K, sinBuf, cosBuf, k3);
        for (int i = 0; i < N; i++) tmp[i] = theta[i] + dt * k3[i];
        Dynamics.deriv(tmp, omega, nbr, K, sinBuf, cosBuf, k4);
        for (int i = 0; i < N; i++) {
            theta[i] += dt / 6.0 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]);
        }
    }
}
