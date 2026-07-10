import java.security.Key;
import javax.crypto.Cipher;

public class IndRsaFactory {
    private static final String SPEC = "RSA/ECB/OAEPWithSHA-256AndMGF1Padding";

    static Cipher cipherFor(int opmode, Key key) throws Exception {
        Cipher cipher = Cipher.getInstance(SPEC);
        cipher.init(opmode, key);
        return cipher;
    }

    public byte[] wrap(Key pub, byte[] message) throws Exception {
        return cipherFor(Cipher.ENCRYPT_MODE, pub).doFinal(message);
    }

    public byte[] unwrap(Key priv, byte[] ct) throws Exception {
        return cipherFor(Cipher.DECRYPT_MODE, priv).doFinal(ct);
    }
}
