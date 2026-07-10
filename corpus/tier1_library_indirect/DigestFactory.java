package com.example.security;

import java.security.MessageDigest;
import java.util.HashMap;
import java.util.Map;

public final class DigestFactory {

    private static final Map<String, String> ALGOS = new HashMap<>();

    static {
        ALGOS.put("default", "SHA-256");
        ALGOS.put("strong", "SHA-512");
    }

    public static MessageDigest create(String profile) throws Exception {
        String algName = ALGOS.getOrDefault(profile, "SHA-256");
        return MessageDigest.getInstance(algName);
    }

    public static byte[] hash(String profile, byte[] data) throws Exception {
        MessageDigest md = create(profile);
        md.update(data);
        return md.digest();
    }

    public static byte[] hash(byte[] data) throws Exception {
        return hash("default", data);
    }
}
