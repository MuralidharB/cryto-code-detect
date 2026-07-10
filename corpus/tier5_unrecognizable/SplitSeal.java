public final class SplitSeal {

    static final int WIDTH = 4;

    private SplitSeal() {
    }

    static int[] genBlock(int[][] rk, int counter) {
        int[] state = new int[WIDTH];
        for (int i = 0; i < WIDTH; i++) {
            state[i] = counter + i * 0x61C88647;
        }
        for (int s = 0; s < rk.length; s++) {
            SplitBlockMix.transform(state, rk[s]);
        }
        return state;
    }

    public static byte[] apply(byte[] data, int[] key, int seed) {
        int[][] rk = SplitKeyDeriv.derive(key);
        byte[] out = new byte[data.length];
        int counter = seed;
        int[] stream = null;
        int pos = 16;
        for (int i = 0; i < data.length; i++) {
            if (pos == 16) {
                stream = genBlock(rk, counter++);
                pos = 0;
            }
            int word = stream[pos >>> 2];
            int shift = (pos & 3) * 8;
            out[i] = (byte) (data[i] ^ (word >>> shift));
            pos++;
        }
        return out;
    }
}
