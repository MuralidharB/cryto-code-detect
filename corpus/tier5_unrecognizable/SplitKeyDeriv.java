public final class SplitKeyDeriv {

    static final int WIDTH = 4;
    static final int STEPS = 10;

    private SplitKeyDeriv() {
    }

    static int rotl(int v, int n) {
        return (v << n) | (v >>> (32 - n));
    }

    public static int[][] derive(int[] key) {
        int[][] rk = new int[STEPS + 1][WIDTH];
        System.arraycopy(key, 0, rk[0], 0, WIDTH);
        int c = 0x9E3779B9;
        for (int s = 1; s <= STEPS; s++) {
            c += 0x7F4A7C15;
            for (int i = 0; i < WIDTH; i++) {
                int prev = rk[s - 1][i];
                int nb = rk[s - 1][(i + 1) % WIDTH];
                rk[s][i] = rotl(prev + c, 3) ^ nb ^ (s * 0x100 + i);
            }
        }
        return rk;
    }
}
