package corpus.tier5_unrecognizable;

/**
 * HyperLogLog distinct-count estimator for approximating the number of
 * unique visitors in a stream using fixed memory. A fast mixing function
 * spreads items across registers; the harmonic mean of leading-zero
 * runs yields the cardinality estimate.
 */
public final class DcHyperLogLog {

    private final byte[] registers;
    private final int p;

    public DcHyperLogLog(int p) {
        this.p = p;
        this.registers = new byte[1 << p];
    }

    private static long mix(long x) {
        x ^= x >>> 33;
        x *= 0xff51afd7ed558ccdL;
        x ^= x >>> 33;
        x *= 0xc4ceb9fe1a85ec53L;
        x ^= x >>> 33;
        return x;
    }

    public void add(long item) {
        long h = mix(item);
        int idx = (int) (h >>> (64 - p));
        long w = (h << p) | (1L << (p - 1));
        byte rank = (byte) (Long.numberOfLeadingZeros(w) + 1);
        if (rank > registers[idx]) registers[idx] = rank;
    }

    public double estimate() {
        int m = registers.length;
        double sum = 0.0;
        for (byte r : registers) sum += Math.pow(2.0, -r);
        double alpha = 0.7213 / (1.0 + 1.079 / m);
        return alpha * m * m / sum;
    }
}
