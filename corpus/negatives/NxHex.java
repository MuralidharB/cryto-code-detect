public class NxHex {
    private static final char[] DIGITS = "0123456789abcdef".toCharArray();

    public static String encode(byte[] data) {
        StringBuilder sb = new StringBuilder(data.length * 2);
        for (byte b : data) {
            sb.append(DIGITS[(b >> 4) & 0xf]);
            sb.append(DIGITS[b & 0xf]);
        }
        return sb.toString();
    }

    public static byte[] decode(String hex) {
        int n = hex.length() / 2;
        byte[] out = new byte[n];
        for (int i = 0; i < n; i++) {
            int hi = Character.digit(hex.charAt(i * 2), 16);
            int lo = Character.digit(hex.charAt(i * 2 + 1), 16);
            out[i] = (byte) ((hi << 4) | lo);
        }
        return out;
    }

    public static void main(String[] args) {
        String h = encode("hi".getBytes());
        System.out.println(h + " -> " + new String(decode(h)));
    }
}
