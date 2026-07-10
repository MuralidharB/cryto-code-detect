public class SpnBlock {

    private static final int[] SBOX = {
        0xE, 0x4, 0xD, 0x1, 0x2, 0xF, 0xB, 0x8,
        0x3, 0xA, 0x6, 0xC, 0x5, 0x9, 0x0, 0x7
    };

    private static final int[] PERM = {
        0, 4, 8, 12, 1, 5, 9, 13,
        2, 6, 10, 14, 3, 7, 11, 15
    };

    private static int substitute(int block) {
        int out = 0;
        for (int nib = 0; nib < 4; nib++) {
            int v = (block >>> (4 * nib)) & 0xF;
            out |= SBOX[v] << (4 * nib);
        }
        return out;
    }

    private static int permute(int block) {
        int out = 0;
        for (int bit = 0; bit < 16; bit++) {
            if (((block >>> bit) & 1) != 0) {
                out |= 1 << PERM[bit];
            }
        }
        return out;
    }

    public static int encrypt(int block, int key) {
        int state = block & 0xFFFF;
        for (int round = 0; round < 4; round++) {
            int rk = (key + round * 0x2545) & 0xFFFF;
            state ^= rk;
            state = substitute(state);
            state = permute(state);
        }
        return state ^ (key & 0xFFFF);
    }

    public static void main(String[] args) {
        int pt = 0x1234;
        int key = 0xBEEF;
        int ct = encrypt(pt, key);
        System.out.printf("pt=%04x key=%04x ct=%04x%n", pt, key, ct);
    }
}
