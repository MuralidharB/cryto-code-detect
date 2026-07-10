public final class HgKeyedMix {

    private static long rotl(long v, int n) {
        return (v << n) | (v >>> (64 - n));
    }

    public static byte[] tag(byte[] msg, byte[] key) {
        long k0 = 0x243F6A8885A308D3L;
        long k1 = 0x13198A2E03707344L;
        for (int i = 0; i < key.length; i++) {
            k0 ^= ((long) (key[i] & 0xFF)) << ((i & 7) * 8);
            k1 = rotl(k1, 5) + (key[i] & 0xFF);
        }
        long s0 = k0 ^ 0xA5A5A5A5A5A5A5A5L;
        long s1 = k1 ^ 0x5A5A5A5A5A5A5A5AL;

        byte[] p = new byte[msg.length + (8 - (msg.length % 8)) % 8 + 8];
        System.arraycopy(msg, 0, p, 0, msg.length);
        p[msg.length] = (byte) 0x80;
        long bits = (long) msg.length * 8;
        for (int i = 0; i < 8; i++) p[p.length - 8 + i] = (byte) (bits >>> (8 * i));

        for (int off = 0; off < p.length; off += 8) {
            long blk = 0;
            for (int i = 0; i < 8; i++) blk |= ((long) (p[off + i] & 0xFF)) << (8 * i);
            s0 ^= blk;
            s0 *= k1 | 1L;
            s0 = rotl(s0, 23);
            s1 += s0 ^ k0;
            s1 = rotl(s1, 41) ^ blk;
            long t = s0; s0 = s1; s1 = t + k0;
        }
        s0 ^= rotl(s1, 32) + k1;
        s0 *= 0xFF51AFD7ED558CCDL;
        s0 ^= s0 >>> 33;

        byte[] out = new byte[8];
        for (int i = 0; i < 8; i++) out[i] = (byte) (s0 >>> (8 * i));
        return out;
    }

    public static void main(String[] a) {
        byte[] t1 = tag("hello".getBytes(), "k".getBytes());
        byte[] t2 = tag("hellp".getBytes(), "k".getBytes());
        boolean diff = false;
        for (int i = 0; i < 8; i++) if (t1[i] != t2[i]) diff = true;
        if (!diff) throw new IllegalStateException("no diffusion");
    }
}
