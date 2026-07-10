public class NxXorshift32 {
    private int state;

    public NxXorshift32(int seed) {
        this.state = (seed == 0) ? 0x1a2b3c4d : seed;
    }

    public int next() {
        int x = state;
        x ^= x << 13;
        x ^= x >>> 17;
        x ^= x << 5;
        state = x;
        return x;
    }

    public double nextDouble() {
        return (next() & 0xffffffffL) / 4294967296.0;
    }

    public static void main(String[] args) {
        NxXorshift32 rng = new NxXorshift32(12345);
        for (int i = 0; i < 5; i++) {
            System.out.println(rng.next());
        }
    }
}
