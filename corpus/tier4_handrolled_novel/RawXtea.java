public class RawXtea {
    static final int ROUNDS = 32;
    static final int DELTA = 0x9E3779B9;

    public static int[] encrypt(int[] v, int[] key) {
        int v0 = v[0], v1 = v[1], sum = 0;
        for (int i = 0; i < ROUNDS; i++) {
            v0 += (((v1 << 4) ^ (v1 >>> 5)) + v1) ^ (sum + key[sum & 3]);
            sum += DELTA;
            v1 += (((v0 << 4) ^ (v0 >>> 5)) + v0) ^ (sum + key[(sum >>> 11) & 3]);
        }
        return new int[]{v0, v1};
    }

    public static int[] decrypt(int[] v, int[] key) {
        int v0 = v[0], v1 = v[1], sum = DELTA * ROUNDS;
        for (int i = 0; i < ROUNDS; i++) {
            v1 -= (((v0 << 4) ^ (v0 >>> 5)) + v0) ^ (sum + key[(sum >>> 11) & 3]);
            sum -= DELTA;
            v0 -= (((v1 << 4) ^ (v1 >>> 5)) + v1) ^ (sum + key[sum & 3]);
        }
        return new int[]{v0, v1};
    }

    public static void main(String[] args) {
        int[] key = {0x01234567, 0x89ABCDEF, 0xFEDCBA98, 0x76543210};
        int[] block = {0xDEADBEEF, 0xCAFEF00D};
        int[] ct = encrypt(block, key);
        int[] pt = decrypt(ct, key);
        System.out.printf("ct=%08X%08X pt=%08X%08X%n", ct[0], ct[1], pt[0], pt[1]);
    }
}
