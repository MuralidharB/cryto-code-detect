public class NxLcg {
    private long state;
    private static final long A = 6364136223846793005L;
    private static final long C = 1442695040888963407L;

    public NxLcg(long seed) {
        this.state = seed;
    }

    public long next() {
        state = A * state + C;
        return state;
    }

    public int nextInt(int bound) {
        long r = next() >>> 33;
        return (int) (r % bound);
    }

    public static void main(String[] args) {
        NxLcg rng = new NxLcg(42);
        for (int i = 0; i < 5; i++) {
            System.out.println(rng.nextInt(100));
        }
    }
}
