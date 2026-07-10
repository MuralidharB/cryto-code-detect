public class RawStreamArx {
    static int rotl(int x, int n) { return (x << n) | (x >>> (32 - n)); }

    static int[] block(int[] state) {
        int[] w = state.clone();
        for (int r = 0; r < 10; r++) {
            w[0] += w[1]; w[3] ^= w[0]; w[3] = rotl(w[3], 16);
            w[2] += w[3]; w[1] ^= w[2]; w[1] = rotl(w[1], 12);
            w[0] += w[1]; w[3] ^= w[0]; w[3] = rotl(w[3], 8);
            w[2] += w[3]; w[1] ^= w[2]; w[1] = rotl(w[1], 7);
        }
        for (int i = 0; i < 4; i++) w[i] += state[i];
        return w;
    }

    public static byte[] crypt(int[] key, int nonce, byte[] data) {
        byte[] out = new byte[data.length];
        int counter = 0;
        for (int pos = 0; pos < data.length; pos += 16) {
            int[] state = {key[0] ^ 0x61707865, key[1], key[2], nonce ^ (counter++)};
            int[] ks = block(state);
            for (int i = 0; i < 16 && pos + i < data.length; i++) {
                int kb = (ks[i / 4] >>> (8 * (i % 4))) & 0xFF;
                out[pos + i] = (byte) (data[pos + i] ^ kb);
            }
        }
        return out;
    }

    public static void main(String[] args) {
        int[] key = {0xDEADBEEF, 0x12345678, 0xCAFEF00D};
        byte[] pt = "stream blk test".getBytes();
        byte[] ct = crypt(key, 0xABCD, pt);
        byte[] back = crypt(key, 0xABCD, ct);
        System.out.println(new String(back));
    }
}
