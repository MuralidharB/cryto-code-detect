import java.security.MessageDigest;
import java.nio.charset.StandardCharsets;

public class LibSha256 {
    public static byte[] digest(String input) throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        return md.digest(input.getBytes(StandardCharsets.UTF_8));
    }

    public static void main(String[] args) throws Exception {
        byte[] out = digest("hello");
        System.out.println(out.length + " bytes");
    }
}
