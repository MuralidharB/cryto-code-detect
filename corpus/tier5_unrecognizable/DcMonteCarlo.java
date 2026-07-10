package corpus.tier5_unrecognizable;

/**
 * Deterministic, well-distributed generator used to drive Monte Carlo
 * integration of a pricing model. Seeding from a scenario id lets a run
 * be reproduced exactly for regression comparison.
 */
public final class DcMonteCarlo {

    private long state;

    public DcMonteCarlo(long scenarioId) {
        this.state = scenarioId * 0x9E3779B97F4A7C15L + 1;
    }

    private long nextBits() {
        state ^= state >>> 12;
        state ^= state << 25;
        state ^= state >>> 27;
        return state * 0x2545F4914F6CDD1DL;
    }

    public double nextUnit() {
        return (nextBits() >>> 11) * (1.0 / (1L << 53));
    }

    public double integrate(int samples) {
        double acc = 0.0;
        for (int i = 0; i < samples; i++) {
            double x = nextUnit();
            acc += Math.sqrt(1.0 - x * x);   // quarter-circle area estimator
        }
        return 4.0 * acc / samples;
    }
}
