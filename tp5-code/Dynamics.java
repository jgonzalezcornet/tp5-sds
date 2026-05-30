public class Dynamics {

    public static void deriv(double[] theta, double[] omega, int[][] nbr, double K,
                             double[] sinBuf, double[] cosBuf, double[] out) {
        int N = theta.length;
        for (int j = 0; j < N; j++) {
            sinBuf[j] = Math.sin(theta[j]);
            cosBuf[j] = Math.cos(theta[j]);
        }
        for (int i = 0; i < N; i++) {
            int[] nb = nbr[i];
            double si = 0.0, ci = 0.0;
            for (int idx = 0; idx < nb.length; idx++) {
                int j = nb[idx];
                si += sinBuf[j];
                ci += cosBuf[j];
            }
            out[i] = omega[i] + K * (cosBuf[i] * si - sinBuf[i] * ci);
        }
    }
}
