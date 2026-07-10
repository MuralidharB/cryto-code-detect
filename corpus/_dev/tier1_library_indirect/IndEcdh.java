import java.security.PrivateKey;
import java.security.PublicKey;
import javax.crypto.KeyAgreement;

public class IndEcdh {
    private final String scheme;

    public IndEcdh() {
        this.scheme = "ECDH";
    }

    private KeyAgreement agreement(PrivateKey priv) throws Exception {
        KeyAgreement ka = KeyAgreement.getInstance(scheme);
        ka.init(priv);
        return ka;
    }

    public byte[] sharedSecret(PrivateKey priv, PublicKey peer) throws Exception {
        KeyAgreement ka = agreement(priv);
        ka.doPhase(peer, true);
        return ka.generateSecret();
    }
}
