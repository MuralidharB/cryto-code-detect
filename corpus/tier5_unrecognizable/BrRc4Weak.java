public class BrRc4Weak {

    public static byte[] transform(byte[] key, byte[] data) {
        int[] s = new int[256];
        for (int i = 0; i < 256; i++) {
            s[i] = i;
        }
        int j = 0;
        for (int i = 0; i < 256; i++) {
            j = (j + s[i] + (key[i % key.length] & 0xff)) & 0xff;
            int t = s[i];
            s[i] = s[j];
            s[j] = t;
        }
        byte[] out = new byte[data.length];
        int a = 0, b = 0;
        for (int k = 0; k < data.length; k++) {
            a = (a + 1) & 0xff;
            b = (b + s[a]) & 0xff;
            int t = s[a];
            s[a] = s[b];
            s[b] = t;
            int ks = s[(s[a] + s[b]) & 0xff];
            out[k] = (byte) (data[k] ^ ks);
        }
        return out;
    }

    public static void main(String[] args) {
        byte[] c = transform("mykey".getBytes(), "hello world".getBytes());
        StringBuilder sb = new StringBuilder();
        for (byte x : c) {
            sb.append(String.format("%02x", x));
        }
        System.out.println(sb);
    }
}
