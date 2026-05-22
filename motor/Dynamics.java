public class Dynamics {

    public static void deriv(double[] theta, double[] omega, int[][] nbr, double K, double[] out) {
        int N = theta.length;
        for (int i = 0; i < N; i++) {
            double ti = theta[i];
            int[] nb = nbr[i];
            double sum = 0.0;
            for (int idx = 0; idx < nb.length; idx++) {
                sum += Math.sin(theta[nb[idx]] - ti);
            }
            out[i] = omega[i] + K * sum;
        }
    }
}
