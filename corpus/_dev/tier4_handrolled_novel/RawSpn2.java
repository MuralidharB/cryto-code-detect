public class RawSpn2 {
    static final int[] SBOX = {
        0x9, 0x4, 0xA, 0xB, 0xD, 0x1, 0x8, 0x5,
        0x6, 0x2, 0x0, 0x3, 0xC, 0xE, 0xF, 0x7
    };
    static final int[] INV_SBOX = new int[16];
    static { for (int i = 0; i < 16; i++) INV_SBOX[SBOX[i]] = i; }

    static int substitute(int state) {
        int out = 0;
        for (int n = 0; n < 4; n++) {
            int nib = (state >>> (4 * n)) & 0xF;
            out |= SBOX[nib] << (4 * n);
        }
        return out;
    }

    static int permute(int x) {
        int out = 0;
        for (int i = 0; i < 16; i++) {
            int bit = (x >>> i) & 1;
            int pos = (i * 5 + 3) & 15;
            out |= bit << pos;
        }
        return out;
    }

    static int[] keySchedule(int master) {
        int[] rk = new int[5];
        for (int r = 0; r < 5; r++) {
            rk[r] = (master ^ (0x3A5C * (r + 1))) & 0xFFFF;
            master = ((master << 3) | (master >>> 13)) & 0xFFFF;
        }
        return rk;
    }

    public static int encrypt(int block, int master) {
        int[] rk = keySchedule(master);
        int state = block & 0xFFFF;
        for (int r = 0; r < 4; r++) {
            state ^= rk[r];
            state = substitute(state);
            state = permute(state);
        }
        state ^= rk[4];
        return state & 0xFFFF;
    }

    public static void main(String[] args) {
        int c = encrypt(0xBEEF, 0x1234);
        System.out.printf("blk=%04X%n", c);
    }
}
