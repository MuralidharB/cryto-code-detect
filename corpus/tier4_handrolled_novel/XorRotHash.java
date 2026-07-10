public class XorRotHash {

    private static long rotl(long x, int n) {
        return (x << n) | (x >>> (64 - n));
    }

    public static long mac(byte[] key, byte[] message) {
        long acc = 0xA5A5A5A5A5A5A5A5L;
        for (int i = 0; i < key.length; i++) {
            acc ^= ((long) (key[i] & 0xFF)) << ((i % 8) * 8);
            acc = rotl(acc, 7);
        }
        long inner = acc;
        for (int i = 0; i < message.length; i++) {
            long k = key[i % key.length] & 0xFF;
            acc ^= (message[i] & 0xFF) + k;
            acc = rotl(acc, 11);
            acc += inner ^ rotl(acc, 23);
        }
        acc ^= (long) message.length * 0x9E3779B97F4A7C15L;
        acc = rotl(acc, 17) ^ inner;
        return acc;
    }

    public static void main(String[] args) {
        byte[] key = "s3cr3tk".getBytes();
        byte[] msg = "authenticate me".getBytes();
        System.out.printf("%016x%n", mac(key, msg));
    }
}
