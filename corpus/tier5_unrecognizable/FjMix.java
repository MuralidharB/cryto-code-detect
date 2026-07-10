public class FjMix {
    static int gdouble(int x) {
        int h = x & 0x80;
        x = (x << 1) & 0xFF;
        if (h != 0) x ^= 0x1B;
        return x & 0xFF;
    }

    static int gmul(int a, int b) {
        int r = 0;
        for (int i = 0; i < 8; i++) {
            if ((b & 1) != 0) r ^= a;
            b >>= 1;
            a = gdouble(a);
        }
        return r & 0xFF;
    }

    public static void mix(int[] state) {
        for (int c = 0; c < FjSbox.BLOCK; c += 4) {
            int a0 = state[c], a1 = state[c + 1], a2 = state[c + 2], a3 = state[c + 3];
            state[c]     = gmul(a0, 2) ^ gmul(a1, 3) ^ a2 ^ a3;
            state[c + 1] = a0 ^ gmul(a1, 2) ^ gmul(a2, 3) ^ a3;
            state[c + 2] = a0 ^ a1 ^ gmul(a2, 2) ^ gmul(a3, 3);
            state[c + 3] = gmul(a0, 3) ^ a1 ^ a2 ^ gmul(a3, 2);
        }
    }

    public static void unmix(int[] state) {
        for (int c = 0; c < FjSbox.BLOCK; c += 4) {
            int a0 = state[c], a1 = state[c + 1], a2 = state[c + 2], a3 = state[c + 3];
            state[c]     = gmul(a0, 14) ^ gmul(a1, 11) ^ gmul(a2, 13) ^ gmul(a3, 9);
            state[c + 1] = gmul(a0, 9) ^ gmul(a1, 14) ^ gmul(a2, 11) ^ gmul(a3, 13);
            state[c + 2] = gmul(a0, 13) ^ gmul(a1, 9) ^ gmul(a2, 14) ^ gmul(a3, 11);
            state[c + 3] = gmul(a0, 11) ^ gmul(a1, 13) ^ gmul(a2, 9) ^ gmul(a3, 14);
        }
    }
}
