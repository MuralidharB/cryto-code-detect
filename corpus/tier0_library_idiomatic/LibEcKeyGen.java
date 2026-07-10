import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.spec.ECGenParameterSpec;

public class LibEcKeyGen {
    public static KeyPair generate() throws Exception {
        KeyPairGenerator kpg = KeyPairGenerator.getInstance("EC");
        kpg.initialize(new ECGenParameterSpec("secp256r1"));
        return kpg.generateKeyPair();
    }

    public static void main(String[] args) throws Exception {
        KeyPair kp = generate();
        System.out.println(kp.getPublic().getAlgorithm());
    }
}
