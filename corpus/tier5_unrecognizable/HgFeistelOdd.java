public final class HgFeistelOdd {
    // unbalanced source-heavy split: left = 3 bytes, right = 5 bytes, 9 rounds.
    private final int[] rk = new int[9];

    public HgFeistelOdd(long key) {
        long s = key + 0x9E3779B97F4A7C15L;
        for (int i = 0; i < 9; i++) {
            s ^= s >>> 30;
            s *= 0xBF58476D1CE4E5B9L;
            s ^= s >>> 27;
            rk[i] = (int) (s & 0xFFFFFFFFL);
        }
    }

    // maps a 5-byte value + subkey down to a 3-byte value
    private long roundFn(long r, int k) {
        long x = r ^ (k & 0xFFFFFFFFL);
        x += (x << 21);
        x ^= (x >>> 17) | (x << 47);
        x *= 0x2545F4914F6CDD1DL;
        x ^= x >>> 29;
        return x & 0xFFFFFF;
    }

    public long forward(long block) {
        long l = (block >>> 40) & 0xFFFFFF;    // 3 bytes
        long r = block & 0xFFFFFFFFFFL;         // 5 bytes
        for (int i = 0; i < 9; i++) {
            long nl = (l ^ roundFn(r, rk[i])) & 0xFFFFFF;
            long nr = r;
            // rotate the 8-byte word: new left = old right's top 3 bytes region
            long combined = (nl << 40) | nr;      // 3 | 5
            // cyclic byte reshuffle: bring low 3 bytes up to left slot
            l = combined & 0xFFFFFF;
            r = (combined >>> 24) & 0xFFFFFFFFFFL;
        }
        return (l << 40) | r;
    }

    public long backward(long block) {
        long l = (block >>> 40) & 0xFFFFFF;
        long r = block & 0xFFFFFFFFFFL;
        for (int i = 8; i >= 0; i--) {
            long combined = (r << 24) | l;         // invert the byte reshuffle
            long nl = (combined >>> 40) & 0xFFFFFF;
            long nr = combined & 0xFFFFFFFFFFL;
            l = (nl ^ roundFn(nr, rk[i])) & 0xFFFFFF;
            r = nr;
        }
        return (l << 40) | r;
    }

    public static void main(String[] a) {
        HgFeistelOdd t = new HgFeistelOdd(0xCAFEL);
        long b = 0x0102030405060708L & 0xFFFFFFFFFFFFFFL;
        long e = t.forward(b);
        if (t.backward(e) != b) throw new IllegalStateException("mismatch");
    }
}
