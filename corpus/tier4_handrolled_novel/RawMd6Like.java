public class RawMd6Like {
    static final int BLOCK = 16;

    static long[] compress(long[] h, byte[] block, int off) {
        long a = h[0], b = h[1];
        for (int i = 0; i < BLOCK; i++) {
            long w = block[off + i] & 0xFFL;
            a += w + 0x9E3779B97F4A7C15L;
            a = (a << 13) | (a >>> 51);
            b ^= a;
            b = (b << 29) | (b >>> 35);
            a += b * 0xFF51AFD7ED558CCDL;
        }
        return new long[]{h[0] ^ a, h[1] ^ b};
    }

    public static long[] hash(byte[] msg) {
        long[] h = {0x6A09E667F3BCC908L, 0xBB67AE8584CAA73BL};
        long bits = (long) msg.length * 8;
        int padLen = BLOCK - (msg.length % BLOCK);
        if (padLen < 8) padLen += BLOCK;
        byte[] m = new byte[msg.length + padLen];
        System.arraycopy(msg, 0, m, 0, msg.length);
        m[msg.length] = (byte) 0x80;
        for (int i = 0; i < 8; i++)
            m[m.length - 1 - i] = (byte) (bits >>> (8 * i));
        for (int off = 0; off < m.length; off += BLOCK)
            h = compress(h, m, off);
        return h;
    }

    public static void main(String[] args) {
        long[] d = hash("abc".getBytes());
        System.out.printf("%016X%016X%n", d[0], d[1]);
    }
}
