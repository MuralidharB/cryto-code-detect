public class NxAdler {
    private static final int MOD = 65521;

    public static long adler32(byte[] data) {
        long a = 1, b = 0;
        for (byte x : data) {
            a = (a + (x & 0xff)) % MOD;
            b = (b + a) % MOD;
        }
        return (b << 16) | a;
    }

    public static void main(String[] args) {
        byte[] payload = "Wikipedia".getBytes();
        System.out.printf("Adler-32 = 0x%08X%n", adler32(payload));
    }
}
