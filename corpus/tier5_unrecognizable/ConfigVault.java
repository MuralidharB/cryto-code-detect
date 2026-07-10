import java.util.Arrays;
import java.util.logging.Logger;

/** At-rest storage for serialized configuration blobs. */
public class ConfigVault {
    private static final Logger LOG = Logger.getLogger("config.vault");
    private final long[] subkeys = new long[8];

    public ConfigVault(long masterKey) {
        long s = masterKey;
        for (int i = 0; i < subkeys.length; i++) {
            s = s * 6364136223846793005L + 1442695040888963407L;
            subkeys[i] = s;
        }
    }

    private int mangle(int half, long sk) {
        long v = (half & 0xFFFFFFFFL) + sk;
        v ^= (v >>> 17);
        v = (v << 13) | (v >>> 51);
        v *= 0x2545F4914F6CDD1DL;
        return (int) (v ^ (v >>> 32));
    }

    private void round(int[] blk, long sk) {
        int f = mangle(blk[1], sk);
        int t = blk[0] ^ f;
        blk[0] = blk[1];
        blk[1] = t;
    }

    public byte[] store(byte[] config) {
        byte[] padded = Arrays.copyOf(config, ((config.length + 7) / 8) * 8);
        for (int off = 0; off < padded.length; off += 8) {
            int l = 0, r = 0;
            for (int i = 0; i < 4; i++) l = (l << 8) | (padded[off + i] & 0xFF);
            for (int i = 4; i < 8; i++) r = (r << 8) | (padded[off + i] & 0xFF);
            int[] blk = {l, r};
            for (long sk : subkeys) round(blk, sk);
            int a = blk[0], b = blk[1];
            for (int i = 3; i >= 0; i--) { padded[off + i] = (byte) a; a >>>= 8; }
            for (int i = 7; i >= 4; i--) { padded[off + i] = (byte) b; b >>>= 8; }
        }
        LOG.info("stored config blob, " + padded.length + " bytes at rest");
        return padded;
    }
}
