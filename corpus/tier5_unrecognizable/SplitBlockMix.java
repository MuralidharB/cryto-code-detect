public final class SplitBlockMix {

    static final int WIDTH = 4;

    private SplitBlockMix() {
    }

    static int nonlinear(int w) {
        int r = 0;
        for (int shift = 0; shift < 32; shift += 8) {
            int b = (w >>> shift) & 0xFF;
            b = (b * 0xF5 + 0x63) & 0xFF;
            r |= b << shift;
        }
        return r;
    }

    public static void transform(int[] block, int[] rk) {
        for (int i = 0; i < WIDTH; i++) {
            block[i] = nonlinear(block[i] ^ rk[i]);
        }
        int t = block[0];
        for (int i = 0; i < WIDTH; i++) {
            int nxt = block[(i + 1) % WIDTH];
            block[i] = SplitKeyDeriv.rotl(block[i] + nxt, 7) ^ t;
        }
    }
}
