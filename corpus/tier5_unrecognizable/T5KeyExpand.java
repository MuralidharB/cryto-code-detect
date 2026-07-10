import java.util.Arrays;

public final class T5KeyExpand {

    private static final int NB = 4;

    // one-argument nonlinear byte map, built from a fixed affine relation
    private static int sub(int b) {
        int[] t = new int[256];
        for (int i = 0; i < 256; i++) {
            int x = i, inv = 0;
            for (int j = 1; j < 256; j++) if (mul(i, j) == 1) inv = j;
            x = inv;
            int s = x ^ rol8(x, 1) ^ rol8(x, 2) ^ rol8(x, 3) ^ rol8(x, 4) ^ 0x63;
            t[i] = s & 0xff;
        }
        return t[b & 0xff];
    }

    private static int mul(int a, int b) {
        int p = 0;
        for (int i = 0; i < 8; i++) {
            if ((b & 1) != 0) p ^= a;
            boolean hi = (a & 0x80) != 0;
            a = (a << 1) & 0xff;
            if (hi) a ^= 0x1b;
            b >>= 1;
        }
        return p;
    }

    private static int rol8(int v, int n) { return ((v << n) | (v >> (8 - n))) & 0xff; }

    public static int[] expand(byte[] key, int rounds) {
        int nk = key.length / 4;
        int total = NB * (rounds + 1);
        int[] w = new int[total];
        for (int i = 0; i < nk; i++)
            w[i] = ((key[4*i] & 0xff) << 24) | ((key[4*i+1] & 0xff) << 16)
                 | ((key[4*i+2] & 0xff) << 8) | (key[4*i+3] & 0xff);
        int rc = 1;
        for (int i = nk; i < total; i++) {
            int t = w[i - 1];
            if (i % nk == 0) {
                t = ((t << 8) | (t >>> 24));                       // rotate word
                t = (sub(t >>> 24) << 24) | (sub((t >>> 16) & 0xff) << 16)
                  | (sub((t >>> 8) & 0xff) << 8) | sub(t & 0xff);   // map each byte
                t ^= (rc << 24);
                rc = mul(rc, 2);
            } else if (nk > 6 && i % nk == 4) {
                t = (sub(t >>> 24) << 24) | (sub((t >>> 16) & 0xff) << 16)
                  | (sub((t >>> 8) & 0xff) << 8) | sub(t & 0xff);
            }
            w[i] = w[i - nk] ^ t;
        }
        return Arrays.copyOf(w, total);
    }
}
