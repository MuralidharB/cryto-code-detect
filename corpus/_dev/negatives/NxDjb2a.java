public class NxDjb2a {
    public static long hash(byte[] data) {
        long h = 5381L;
        for (byte b : data) {
            h = ((h * 33) ^ (b & 0xff)) & 0xffffffffL;
        }
        return h;
    }

    public static int bucket(byte[] data, int slots) {
        return (int) (hash(data) % slots);
    }

    public static void main(String[] args) {
        byte[] key = "table-lookup".getBytes();
        System.out.println("djb2a=" + hash(key));
        System.out.println("slot=" + bucket(key, 1024));
    }
}
