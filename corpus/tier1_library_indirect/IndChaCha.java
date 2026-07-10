import javax.crypto.Cipher;
import javax.crypto.spec.ChaCha20ParameterSpec;
import javax.crypto.spec.SecretKeySpec;

public class IndChaCha {
    private Cipher helper(int opmode, byte[] key, byte[] nonce, int counter) throws Exception {
        Cipher cipher = Cipher.getInstance("ChaCha20");
        SecretKeySpec keySpec = new SecretKeySpec(key, "ChaCha20");
        ChaCha20ParameterSpec params = new ChaCha20ParameterSpec(nonce, counter);
        cipher.init(opmode, keySpec, params);
        return cipher;
    }

    public byte[] encrypt(byte[] key, byte[] nonce, byte[] plain) throws Exception {
        return helper(Cipher.ENCRYPT_MODE, key, nonce, 1).doFinal(plain);
    }

    public byte[] decrypt(byte[] key, byte[] nonce, byte[] ct) throws Exception {
        return helper(Cipher.DECRYPT_MODE, key, nonce, 1).doFinal(ct);
    }
}
