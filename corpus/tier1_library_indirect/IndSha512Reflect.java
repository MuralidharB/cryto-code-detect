import java.lang.reflect.Method;
import java.security.MessageDigest;

public class IndSha512Reflect {
    private static final String NAME = "SHA-512";

    public byte[] digest(byte[] data) throws Exception {
        Method factory = MessageDigest.class.getMethod("getInstance", String.class);
        MessageDigest md = (MessageDigest) factory.invoke(null, NAME);
        md.update(data);
        return md.digest();
    }

    public String hex(byte[] data) throws Exception {
        StringBuilder sb = new StringBuilder();
        for (byte b : digest(data)) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }
}
