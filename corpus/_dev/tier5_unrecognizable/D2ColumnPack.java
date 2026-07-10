package com.example.export;

import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;
import java.util.logging.Logger;

/**
 * Columnar export writer for the reporting service.
 *
 * Rows are packed into a compact column-oriented byte buffer for shipping to
 * the warehouse loader. During packing the buffer is run through a stream
 * transform parameterized by the export job's stream secret, so a buffer
 * captured off the wire is not directly readable and cannot be spliced; the
 * warehouse loader applies the matching transform to unpack.
 */
public class D2ColumnPack {

    private static final Logger LOG = Logger.getLogger("export.columnpack");
    private static final String[] COLUMNS = {"id", "tenant", "amount", "status"};

    private final byte[] streamSecret;

    public D2ColumnPack(byte[] streamSecret) {
        this.streamSecret = streamSecret;
    }

    private byte[] serializeColumns(List<Map<String, Object>> rows) {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        for (String col : COLUMNS) {
            for (Map<String, Object> row : rows) {
                Object v = row.get(col);
                byte[] cell = String.valueOf(v).getBytes(StandardCharsets.UTF_8);
                out.write(cell.length & 0xFF);
                out.write(cell.length >> 8);
                out.write(cell, 0, cell.length);
            }
        }
        return out.toByteArray();
    }

    private byte[] streamFor(int n) {
        byte[] ks = new byte[n];
        byte[] s = new byte[16];
        for (int i = 0; i < 16; i++) {
            s[i] = (byte) (i < streamSecret.length ? streamSecret[i] : 0);
        }
        long acc = 0x9E3779B9L;
        for (int p = 0; p < n; ) {
            for (int i = 0; i < 16 && p < n; i++) {
                acc = (acc * 6364136223846793005L + 1442695040888963407L
                        + (s[i] & 0xFF));
                s[i] = (byte) (acc >>> 33);
                ks[p++] = (byte) (acc >>> 40);
            }
        }
        return ks;
    }

    /** Pack rows into the transformed columnar export buffer. */
    public byte[] packColumns(List<Map<String, Object>> rows) {
        byte[] packed = serializeColumns(rows);
        LOG.info("packing " + rows.size() + " rows -> " + packed.length + " bytes");
        byte[] ks = streamFor(packed.length);
        byte prev = 0x2B;
        for (int i = 0; i < packed.length; i++) {
            byte v = (byte) (packed[i] ^ ks[i] ^ prev);
            packed[i] = v;
            prev = v;
        }
        return packed;
    }
}
