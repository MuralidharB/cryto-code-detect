public class Base64Codec {
    private static final String ALPHABET =
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

    public static String encode(byte[] data) {
        StringBuilder sb = new StringBuilder();
        int i = 0;
        while (i < data.length) {
            int b0 = data[i++] & 0xFF;
            int b1 = i < data.length ? data[i++] & 0xFF : -1;
            int b2 = i < data.length ? data[i++] & 0xFF : -1;
            sb.append(ALPHABET.charAt(b0 >> 2));
            sb.append(ALPHABET.charAt(((b0 & 0x3) << 4) | (b1 < 0 ? 0 : b1 >> 4)));
            sb.append(b1 < 0 ? '=' : ALPHABET.charAt(((b1 & 0xF) << 2) | (b2 < 0 ? 0 : b2 >> 6)));
            sb.append(b2 < 0 ? '=' : ALPHABET.charAt(b2 & 0x3F));
        }
        return sb.toString();
    }

    public static byte[] decode(String text) {
        java.io.ByteArrayOutputStream out = new java.io.ByteArrayOutputStream();
        int buffer = 0, bits = 0;
        for (int i = 0; i < text.length(); i++) {
            char c = text.charAt(i);
            if (c == '=') break;
            int v = ALPHABET.indexOf(c);
            if (v < 0) continue;
            buffer = (buffer << 6) | v;
            bits += 6;
            if (bits >= 8) {
                bits -= 8;
                out.write((buffer >> bits) & 0xFF);
            }
        }
        return out.toByteArray();
    }

    public static void main(String[] args) {
        String e = encode("hello".getBytes());
        System.out.println(e);
        System.out.println(new String(decode(e)));
    }
}
