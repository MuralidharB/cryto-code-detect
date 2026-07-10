package com.example.security;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

public final class MacHelper {

    private static final String ALG = "Hmac" + "SHA256";

    private Mac instance(byte[] key) throws Exception {
        Mac m = Mac.getInstance(ALG);
        m.init(new SecretKeySpec(key, ALG));
        return m;
    }

    public byte[] mac(byte[] key, byte[] data) throws Exception {
        return instance(key).doFinal(data);
    }

    public boolean verify(byte[] key, byte[] data, byte[] expected) throws Exception {
        byte[] actual = mac(key, data);
        if (actual.length != expected.length) {
            return false;
        }
        int diff = 0;
        for (int i = 0; i < actual.length; i++) {
            diff |= actual[i] ^ expected[i];
        }
        return diff == 0;
    }
}
