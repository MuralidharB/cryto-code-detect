import javax.crypto.Cipher;
import java.security.PublicKey;

public class LibRsaCipher {
    public static byte[] encrypt(PublicKey pub, byte[] plaintext) throws Exception {
        Cipher cipher = Cipher.getInstance("RSA/ECB/OAEPWithSHA-256AndMGF1Padding");
        cipher.init(Cipher.ENCRYPT_MODE, pub);
        return cipher.doFinal(plaintext);
    }
}
