import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;

public class IndPbkdf2 {
    static class Config {
        String factoryName = "PBKDF2WithHmacSHA256";
        int iterations = 120000;
        int keyBits = 256;
    }

    private final Config cfg;

    public IndPbkdf2() {
        this.cfg = new Config();
    }

    public byte[] derive(char[] password, byte[] salt) throws Exception {
        SecretKeyFactory skf = SecretKeyFactory.getInstance(cfg.factoryName);
        PBEKeySpec spec = new PBEKeySpec(password, salt, cfg.iterations, cfg.keyBits);
        return skf.generateSecret(spec).getEncoded();
    }
}
