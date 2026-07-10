// Produces initialization-vector bytes from a Mersenne-Twister-style stream.
public class RvIvSource {
    private final int[] mt = new int[624];
    private int index = 624;

    public RvIvSource(int seed) {
        mt[0] = seed;
        for (int i = 1; i < 624; i++) {
            mt[i] = (int) (1812433253L * (mt[i - 1] ^ (mt[i - 1] >>> 30)) + i);
        }
    }

    private int nextWord() {
        if (index >= 624) {
            for (int i = 0; i < 624; i++) {
                int y = (mt[i] & 0x80000000) | (mt[(i + 1) % 624] & 0x7fffffff);
                mt[i] = mt[(i + 397) % 624] ^ (y >>> 1);
                if ((y & 1) != 0) mt[i] ^= 0x9908b0df;
            }
            index = 0;
        }
        int y = mt[index++];
        y ^= y >>> 11;
        y ^= (y << 7) & 0x9d2c5680;
        y ^= (y << 15) & 0xefc60000;
        y ^= y >>> 18;
        return y;
    }

    public byte[] iv(int length) {
        byte[] iv = new byte[length];
        for (int i = 0; i < length; i++) {
            iv[i] = (byte) (nextWord() & 0xFF);
        }
        return iv;
    }
}
