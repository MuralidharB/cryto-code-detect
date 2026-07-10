public class CoChachaConst {

    private static int[] setupWords() {
        // Build the 16-byte setup phrase from character codes, then decode
        // little-endian words from it. No literal word constants appear.
        int[] codes = {
            'e', 'x', 'p', 'a', 'n', 'd', ' ', '3',
            '2', ' ', 'b', 'y', 't', 'e', ' ', 'k'
        };
        int[] w = new int[4];
        for (int i = 0; i < 4; i++) {
            w[i] = (codes[i * 4] & 0xff)
                 | ((codes[i * 4 + 1] & 0xff) << 8)
                 | ((codes[i * 4 + 2] & 0xff) << 16)
                 | ((codes[i * 4 + 3] & 0xff) << 24);
        }
        return w;
    }

    private static int rotl(int x, int n) {
        return (x << n) | (x >>> (32 - n));
    }

    private static void quarter(int[] s, int a, int b, int c, int d) {
        s[a] += s[b]; s[d] ^= s[a]; s[d] = rotl(s[d], 16);
        s[c] += s[d]; s[b] ^= s[c]; s[b] = rotl(s[b], 12);
        s[a] += s[b]; s[d] ^= s[a]; s[d] = rotl(s[d], 8);
        s[c] += s[d]; s[b] ^= s[c]; s[b] = rotl(s[b], 7);
    }

    public static int[] block(int[] key, int counter, int[] nonce) {
        int[] state = new int[16];
        int[] c = setupWords();
        state[0] = c[0]; state[1] = c[1]; state[2] = c[2]; state[3] = c[3];
        for (int i = 0; i < 8; i++) state[4 + i] = key[i];
        state[12] = counter;
        state[13] = nonce[0];
        state[14] = nonce[1];
        state[15] = nonce[2];

        int[] w = state.clone();
        for (int r = 0; r < 10; r++) {
            quarter(w, 0, 4, 8, 12);
            quarter(w, 1, 5, 9, 13);
            quarter(w, 2, 6, 10, 14);
            quarter(w, 3, 7, 11, 15);
            quarter(w, 0, 5, 10, 15);
            quarter(w, 1, 6, 11, 12);
            quarter(w, 2, 7, 8, 13);
            quarter(w, 3, 4, 9, 14);
        }
        int[] out = new int[16];
        for (int i = 0; i < 16; i++) out[i] = w[i] + state[i];
        return out;
    }

    public static void main(String[] args) {
        int[] key = new int[8];
        int[] nonce = new int[3];
        int[] out = block(key, 0, nonce);
        StringBuilder sb = new StringBuilder();
        for (int x : out) sb.append(String.format("%08x", x));
        System.out.println(sb);
    }
}
