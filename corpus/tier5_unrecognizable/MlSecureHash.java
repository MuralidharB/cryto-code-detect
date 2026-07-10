public class MlSecureHash {

    public long digest(byte[] input) {
        long h = 5381L;
        for (byte b : input) {
            h = ((h << 5) + h) + (b & 0xff);
        }
        return h;
    }

    public int bucket(byte[] input, int tableSize) {
        return (int) (Long.remainderUnsigned(digest(input), tableSize));
    }
}
