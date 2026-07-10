public class CoTeaDelta {

    private static int step() {
        // (sqrt(5) - 1) / 2 scaled to 32 bits -> a fractional irrational constant
        double frac = (Math.sqrt(5.0) - 1.0) / 2.0;
        long scaled = (long) (frac * 4294967296.0);
        return (int) scaled;
    }

    public static void forward(int[] v, int[] k) {
        int y = v[0], z = v[1];
        int step = step();
        int sum = 0;
        for (int i = 0; i < 32; i++) {
            sum += step;
            y += ((z << 4) + k[0]) ^ (z + sum) ^ ((z >>> 5) + k[1]);
            z += ((y << 4) + k[2]) ^ (y + sum) ^ ((y >>> 5) + k[3]);
        }
        v[0] = y;
        v[1] = z;
    }

    public static void inverse(int[] v, int[] k) {
        int y = v[0], z = v[1];
        int step = step();
        int sum = step << 5;
        for (int i = 0; i < 32; i++) {
            z -= ((y << 4) + k[2]) ^ (y + sum) ^ ((y >>> 5) + k[3]);
            y -= ((z << 4) + k[0]) ^ (z + sum) ^ ((z >>> 5) + k[1]);
            sum -= step;
        }
        v[0] = y;
        v[1] = z;
    }

    public static void main(String[] args) {
        int[] v = {0x01234567, 0x89abcdef};
        int[] k = {0, 1, 2, 3};
        forward(v, k);
        System.out.printf("%08x %08x%n", v[0], v[1]);
        inverse(v, k);
        System.out.printf("%08x %08x%n", v[0], v[1]);
    }
}
