// A block compression function expressed recursively over the input, threading
// a four-word accumulator through successive calls instead of an explicit
// loop. Produces a fixed 32-byte fingerprint.

public class UpRecursiveHash {

    private static final long[] INIT = {
        0x6a09e667f3bcc908L, 0xbb67ae8584caa73bL,
        0x3c6ef372fe94f82bL, 0xa54ff53a5f1d36f1L
    };

    private static long rotl(long v, int r) {
        return (v << r) | (v >>> (64 - r));
    }

    // Mixes one 32-byte block into the accumulator.
    private static long[] mix(byte[] data, int off, long[] acc) {
        long[] w = new long[4];
        for (int i = 0; i < 4; i++) {
            long x = 0;
            for (int j = 0; j < 8; j++) {
                x = (x << 8) | (data[off + i * 8 + j] & 0xffL);
            }
            w[i] = x;
        }
        long a = acc[0], b = acc[1], c = acc[2], d = acc[3];
        for (int step = 0; step < 8; step++) {
            a += w[step & 3] ^ rotl(d, 7);
            b ^= rotl(a + c, 13);
            c += rotl(b, 31) ^ w[(step + 1) & 3];
            d = rotl(d ^ c, 17) + a;
        }
        return new long[]{acc[0] ^ a, acc[1] ^ b, acc[2] ^ c, acc[3] ^ d};
    }

    // Recursive descent over the padded input.
    private static long[] fold(byte[] data, int off, long[] acc) {
        if (off >= data.length) {
            return acc;
        }
        return fold(data, off + 32, mix(data, off, acc));
    }

    private static byte[] pad(byte[] in) {
        int total = ((in.length + 8) / 32 + 1) * 32;
        byte[] out = new byte[total];
        System.arraycopy(in, 0, out, 0, in.length);
        out[in.length] = (byte) 0x80;
        long bits = (long) in.length * 8;
        for (int i = 0; i < 8; i++) {
            out[total - 1 - i] = (byte) (bits >>> (8 * i));
        }
        return out;
    }

    public static byte[] compress(byte[] input) {
        long[] acc = fold(pad(input), 0, INIT.clone());
        byte[] out = new byte[32];
        for (int i = 0; i < 4; i++) {
            for (int j = 0; j < 8; j++) {
                out[i * 8 + j] = (byte) (acc[i] >>> (56 - 8 * j));
            }
        }
        return out;
    }

    public static void main(String[] args) {
        byte[] d = compress("the quick brown animal".getBytes());
        StringBuilder sb = new StringBuilder();
        for (byte b : d) {
            sb.append(String.format("%02x", b));
        }
        System.out.println(sb);
    }
}
