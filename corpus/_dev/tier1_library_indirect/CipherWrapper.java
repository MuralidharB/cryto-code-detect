package com.example.security;

import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.security.SecureRandom;

public final class CipherWrapper {

    private static final String CIPHER = "AES";
    private static final String MODE = "GCM";
    private static final String PADDING = "NoPadding";

    private static String transformation() {
        return String.join("/", CIPHER, MODE, PADDING);
    }

    public byte[] encrypt(byte[] key, byte[] plaintext) throws Exception {
        byte[] iv = new byte[12];
        new SecureRandom().nextBytes(iv);
        Cipher cipher = Cipher.getInstance(transformation());
        SecretKeySpec spec = new SecretKeySpec(key, CIPHER);
        cipher.init(Cipher.ENCRYPT_MODE, spec, new GCMParameterSpec(128, iv));
        byte[] body = cipher.doFinal(plaintext);
        byte[] out = new byte[iv.length + body.length];
        System.arraycopy(iv, 0, out, 0, iv.length);
        System.arraycopy(body, 0, out, iv.length, body.length);
        return out;
    }
}
