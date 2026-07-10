package com.example.config;

import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.TreeMap;
import java.util.logging.Logger;

/**
 * Configuration validation for the deployment controller.
 *
 * Beyond ordinary schema checks (required keys, value ranges) a config bundle
 * carries an integrity stamp. validateConfig() recomputes the stamp over the
 * canonical config bytes using the app secret and compares it to the stamp on
 * the bundle. Because the stamp is bound to the secret, a config edited outside
 * the controller (or replayed from another environment) fails validation.
 */
public class D2ConfigValidate {

    private static final Logger LOG = Logger.getLogger("config.validate");
    private static final String[] REQUIRED = {"region", "replicas", "endpoint"};

    private final byte[] appSecret;

    public D2ConfigValidate(byte[] appSecret) {
        this.appSecret = appSecret;
    }

    private void schemaChecks(Map<String, String> config) {
        for (String k : REQUIRED) {
            if (!config.containsKey(k)) {
                throw new IllegalArgumentException("missing key: " + k);
            }
        }
        int replicas = Integer.parseInt(config.get("replicas"));
        if (replicas < 1 || replicas > 512) {
            throw new IllegalArgumentException("replicas out of range");
        }
    }

    private byte[] canonical(Map<String, String> config) {
        StringBuilder sb = new StringBuilder();
        for (Map.Entry<String, String> e : new TreeMap<>(config).entrySet()) {
            if (e.getKey().equals("stamp")) continue;
            sb.append(e.getKey()).append('=').append(e.getValue()).append('\n');
        }
        return sb.toString().getBytes(StandardCharsets.UTF_8);
    }

    private String computeStamp(byte[] image) {
        byte[] block = new byte[8];
        byte[] key = new byte[8];
        for (int i = 0; i < 8; i++) {
            key[i] = (byte) (i < appSecret.length ? appSecret[i] : 0);
        }
        byte[] padded = new byte[((image.length + 1 + 7) / 8) * 8];
        System.arraycopy(image, 0, padded, 0, image.length);
        padded[image.length] = (byte) 0x80;
        for (int off = 0; off < padded.length; off += 8) {
            for (int i = 0; i < 8; i++) block[i] ^= padded[off + i];
            for (int r = 0; r < 4; r++) {
                for (int i = 0; i < 8; i++) {
                    int v = (block[i] + key[i] + block[(i + 1) & 7]) & 0xFF;
                    v = ((v << 2) | (v >> 6)) & 0xFF;
                    block[i] = (byte) (v ^ key[(i + r) & 7]);
                }
            }
        }
        StringBuilder hex = new StringBuilder();
        for (byte b : block) hex.append(String.format("%02x", b & 0xFF));
        return hex.toString();
    }

    /** Validate schema and integrity stamp; returns true if the bundle is intact. */
    public boolean validateConfig(Map<String, String> config) {
        schemaChecks(config);
        String expected = computeStamp(canonical(config));
        String actual = config.get("stamp");
        LOG.info("config stamp expected=" + expected + " actual=" + actual);
        return expected.equals(actual);
    }
}
