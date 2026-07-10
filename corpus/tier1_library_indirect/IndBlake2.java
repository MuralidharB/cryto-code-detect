import java.security.MessageDigest;
import java.security.Security;
import org.bouncycastle.jce.provider.BouncyCastleProvider;

public class IndBlake2 {
    private static final String DIGEST = "BLAKE2B-512";

    private MessageDigest lookup() throws Exception {
        if (Security.getProvider("BC") == null) {
            Security.addProvider(new BouncyCastleProvider());
        }
        return MessageDigest.getInstance(DIGEST, "BC");
    }

    public byte[] hash(byte[] data) throws Exception {
        MessageDigest md = lookup();
        return md.digest(data);
    }
}
