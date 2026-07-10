import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;

public class LibPbkdf2 {
    public static byte[] deriveKey(char[] password, byte[] salt) throws Exception {
        PBEKeySpec spec = new PBEKeySpec(password, salt, 100000, 256);
        SecretKeyFactory skf = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
        return skf.generateSecret(spec).getEncoded();
    }

    public static void main(String[] args) throws Exception {
        byte[] key = deriveKey("pass".toCharArray(), "saltsalt".getBytes());
        System.out.println(key.length + " bytes");
    }
}
