package corpus.tier5_unrecognizable;

/**
 * Rotate-and-add running checksum for verifying that a firmware image
 * transferred without corruption. Order-sensitive so a swapped block is
 * caught, but keyless and not collision-resistant.
 */
public final class DcRotChecksum {

    public static int checksum(byte[] data) {
        int acc = 0x1505;
        for (int i = 0; i < data.length; i++) {
            acc = Integer.rotateLeft(acc, 7);
            acc += (data[i] & 0xFF) * 0x9E37;
            acc ^= acc >>> 15;
        }
        return acc;
    }

    public static boolean verify(byte[] data, int expected) {
        return checksum(data) == expected;
    }
}
