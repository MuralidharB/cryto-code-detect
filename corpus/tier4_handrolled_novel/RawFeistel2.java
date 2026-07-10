public class RawFeistel2 {
    static int roundFn(int half, int rk) {
        int x = (half + rk) & 0xFFFFFFFF;
        x ^= (x << 7) | (x >>> 25);
        x = (x * 0x9E3779B1);
        x ^= (x >>> 15);
        return x & 0xFFFFFFFF;
    }

    static int[] keySchedule(long key) {
        int[] rk = new int[8];
        for (int i = 0; i < 8; i++) {
            rk[i] = (int) ((key >>> (i * 5)) ^ (0xA5A5A5A5L * (i + 1)));
            key = ((key << 11) | (key >>> 53));
        }
        return rk;
    }

    public static long encrypt(long block, long key) {
        int left = (int) (block >>> 32);
        int right = (int) block;
        int[] rk = keySchedule(key);
        for (int r = 0; r < 8; r++) {
            int t = left ^ roundFn(right, rk[r]);
            left = right;
            right = t;
        }
        return ((long) right << 32) | (left & 0xFFFFFFFFL);
    }

    public static long decrypt(long block, long key) {
        int right = (int) (block >>> 32);
        int left = (int) block;
        int[] rk = keySchedule(key);
        for (int r = 7; r >= 0; r--) {
            int t = right ^ roundFn(left, rk[r]);
            right = left;
            left = t;
        }
        return ((long) left << 32) | (right & 0xFFFFFFFFL);
    }

    public static void main(String[] args) {
        long key = 0x0123456789ABCDEFL;
        long ct = encrypt(0xDEADBEEFCAFEF00DL, key);
        System.out.printf("ct=%016X pt=%016X%n", ct, decrypt(ct, key));
    }
}
