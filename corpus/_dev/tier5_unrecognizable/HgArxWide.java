public final class HgArxWide {
    private final int[] sub = new int[8];

    public HgArxWide(long seed) {
        long s = seed ^ 0x9E3779B97F4A7C15L;
        for (int i = 0; i < 8; i++) {
            s ^= s << 13;
            s ^= s >>> 7;
            s ^= s << 17;
            sub[i] = (int) (s & 0xFFFFFFFFL);
        }
    }

    private static int rotl(int v, int n) {
        return (v << n) | (v >>> (32 - n));
    }

    private static int rotr(int v, int n) {
        return (v >>> n) | (v << (32 - n));
    }

    public void forward(int[] b) {
        for (int r = 0; r < 12; r++) {
            for (int i = 0; i < 8; i++) {
                int j = (i + 1) & 7;
                b[i] += sub[(i + r) & 7];
                b[i] ^= b[j];
                b[i] = rotl(b[i], ((r * 3 + i) & 15) + 1);
                b[j] += b[i];
            }
        }
    }

    public void backward(int[] b) {
        for (int r = 11; r >= 0; r--) {
            for (int i = 7; i >= 0; i--) {
                int j = (i + 1) & 7;
                b[j] -= b[i];
                b[i] = rotr(b[i], ((r * 3 + i) & 15) + 1);
                b[i] ^= b[j];
                b[i] -= sub[(i + r) & 7];
            }
        }
    }

    public static void main(String[] a) {
        HgArxWide t = new HgArxWide(0x1234L);
        int[] blk = {1, 2, 3, 4, 5, 6, 7, 8};
        int[] copy = blk.clone();
        t.forward(blk);
        t.backward(blk);
        for (int i = 0; i < 8; i++) {
            if (blk[i] != copy[i]) throw new IllegalStateException("mismatch");
        }
    }
}
