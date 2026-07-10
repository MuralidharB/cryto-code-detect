import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;

public class IndAesCtr {
    private static final String ALGO = "AES";
    private static final String MODE = "CTR";
    private static final String PAD = "NoPadding";

    private static String transform() {
        return ALGO + "/" + MODE + "/" + PAD;
    }

    private Cipher build(int opmode, byte[] key, byte[] iv) throws Exception {
        Cipher c = Cipher.getInstance(transform());
        SecretKeySpec ks = new SecretKeySpec(key, ALGO);
        c.init(opmode, ks, new IvParameterSpec(iv));
        return c;
    }

    public byte[] encrypt(byte[] key, byte[] iv, byte[] data) throws Exception {
        return build(Cipher.ENCRYPT_MODE, key, iv).doFinal(data);
    }

    public byte[] decrypt(byte[] key, byte[] iv, byte[] data) throws Exception {
        return build(Cipher.DECRYPT_MODE, key, iv).doFinal(data);
    }
}
