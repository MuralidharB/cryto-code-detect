public final class T5RoundLoop {

    private static int gmul(int a, int b) {
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

    private static void whiten(int[] s, int[] rk, int off) {
        for (int i = 0; i < 16; i++) s[i] ^= rk[off + i];
    }

    private static void sub(int[] s, int[] table) {
        for (int i = 0; i < 16; i++) s[i] = table[s[i] & 0xff];
    }

    private static void shift(int[] s) {
        int[] t = new int[16];
        int[] perm = {0,5,10,15,4,9,14,3,8,13,2,7,12,1,6,11};
        for (int i = 0; i < 16; i++) t[i] = s[perm[i]];
        System.arraycopy(t, 0, s, 0, 16);
    }

    private static void mix(int[] s) {
        for (int c = 0; c < 4; c++) {
            int a0 = s[4*c], a1 = s[4*c+1], a2 = s[4*c+2], a3 = s[4*c+3];
            s[4*c]   = gmul(a0,2)^gmul(a1,3)^a2^a3;
            s[4*c+1] = a0^gmul(a1,2)^gmul(a2,3)^a3;
            s[4*c+2] = a0^a1^gmul(a2,2)^gmul(a3,3);
            s[4*c+3] = gmul(a0,3)^a1^a2^gmul(a3,2);
        }
    }

    public static void transform(int[] state, int[] subkeys, int[] table, int rounds) {
        whiten(state, subkeys, 0);
        for (int r = 1; r < rounds; r++) {
            sub(state, table);
            shift(state);
            mix(state);
            whiten(state, subkeys, r * 16);
        }
        sub(state, table);
        shift(state);
        whiten(state, subkeys, rounds * 16);
    }
}
