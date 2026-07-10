import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

public class IndHmac512 {
    private static final String ALG = "HmacSHA512";

    private Mac primed(byte[] key) throws Exception {
        Mac mac = Mac.getInstance(ALG);
        mac.init(new SecretKeySpec(key, ALG));
        return mac;
    }

    public byte[] authenticate(byte[] key, byte[] msg) throws Exception {
        return primed(key).doFinal(msg);
    }

    public boolean verify(byte[] key, byte[] msg, byte[] tag) throws Exception {
        byte[] got = authenticate(key, msg);
        return java.util.Arrays.equals(got, tag);
    }
}
