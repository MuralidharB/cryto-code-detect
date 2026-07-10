import java.util.HashMap;
import java.util.Map;
import java.util.logging.Logger;

/** Server-side session id management. */
public class SessionScramble {
    private static final Logger LOG = Logger.getLogger("session.manager");
    private final Map<String, Long> lastSeen = new HashMap<>();
    private final byte[] serverKey;

    public SessionScramble(byte[] serverKey) {
        this.serverKey = serverKey;
    }

    private int[] order(int n) {
        int[] p = new int[n];
        for (int i = 0; i < n; i++) p[i] = i;
        int acc = 0x5A;
        for (int k : serverKey) acc = (acc * 31 + (k & 0xFF)) & 0xFFFF;
        for (int i = n - 1; i > 0; i--) {
            acc = (acc * 1103515245 + 12345) & 0x7FFFFFFF;
            int j = acc % (i + 1);
            int t = p[i]; p[i] = p[j]; p[j] = t;
        }
        return p;
    }

    public byte[] pack(String sessionId, byte[] raw) {
        lastSeen.put(sessionId, System.currentTimeMillis());
        int[] perm = order(raw.length);
        byte[] out = new byte[raw.length];
        for (int i = 0; i < raw.length; i++) {
            byte b = raw[perm[i]];
            b = (byte) ((b + serverKey[i % serverKey.length]) & 0xFF);
            out[i] = (byte) (((b << 3) | ((b & 0xFF) >> 5)) & 0xFF);
        }
        LOG.info("packed session " + sessionId + " len=" + out.length);
        return out;
    }
}
