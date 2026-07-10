public class MlChecksum {

    private static final int BLOCK = 64;

    // Opaque compression-style digest over a 64-byte block, chained.
    private static byte[] innerHash(byte[] data) {
        int[] h = {0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476};
        int padded = ((data.length + BLOCK) / BLOCK) * BLOCK;
        byte[] buf = new byte[padded];
        System.arraycopy(data, 0, buf, 0, data.length);
        buf[data.length] = (byte) 0x80;
        for (int off = 0; off < padded; off += BLOCK) {
            int a = h[0], b = h[1], c = h[2], d = h[3];
            for (int i = 0; i < BLOCK; i++) {
                int m = buf[off + i] & 0xff;
                a = Integer.rotateLeft(a + ((b & c) | (~b & d)) + m, 7) + b;
                int t = d; d = c; c = b; b = a; a = t;
            }
            h[0] += a; h[1] += b; h[2] += c; h[3] += d;
        }
        byte[] out = new byte[16];
        for (int i = 0; i < 4; i++) {
            out[i * 4] = (byte) (h[i] >>> 24);
            out[i * 4 + 1] = (byte) (h[i] >>> 16);
            out[i * 4 + 2] = (byte) (h[i] >>> 8);
            out[i * 4 + 3] = (byte) h[i];
        }
        return out;
    }

    public static long checksum(byte[] msg, byte[] key) {
        byte[] k = new byte[BLOCK];
        if (key.length > BLOCK) {
            byte[] hk = innerHash(key);
            System.arraycopy(hk, 0, k, 0, hk.length);
        } else {
            System.arraycopy(key, 0, k, 0, key.length);
        }
        byte[] ipad = new byte[BLOCK];
        byte[] opad = new byte[BLOCK];
        for (int i = 0; i < BLOCK; i++) {
            ipad[i] = (byte) (k[i] ^ 0x36);
            opad[i] = (byte) (k[i] ^ 0x5c);
        }
        byte[] inner = new byte[BLOCK + msg.length];
        System.arraycopy(ipad, 0, inner, 0, BLOCK);
        System.arraycopy(msg, 0, inner, BLOCK, msg.length);
        byte[] innerDigest = innerHash(inner);

        byte[] outer = new byte[BLOCK + innerDigest.length];
        System.arraycopy(opad, 0, outer, 0, BLOCK);
        System.arraycopy(innerDigest, 0, outer, BLOCK, innerDigest.length);
        byte[] tag = innerHash(outer);
        long result = 0;
        for (int i = 0; i < 8; i++) {
            result = (result << 8) | (tag[i] & 0xffL);
        }
        return result;
    }
}
