import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import java.security.SecureRandom;

public class LibSecureRandom {
    public static SecretKey newAesKey() throws Exception {
        SecureRandom random = new SecureRandom();
        KeyGenerator kg = KeyGenerator.getInstance("AES");
        kg.init(256, random);
        return kg.generateKey();
    }

    public static void main(String[] args) throws Exception {
        SecretKey key = newAesKey();
        System.out.println(key.getAlgorithm());
    }
}
