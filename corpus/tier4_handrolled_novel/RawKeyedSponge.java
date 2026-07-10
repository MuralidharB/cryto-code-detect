public class RawKeyedSponge {
    static final int RATE = 8;
    static final int CAP = 8;
    static final int STATE = RATE + CAP;

    static void permute(byte[] s) {
        for (int round = 0; round < 12; round++) {
            for (int i = 0; i < STATE; i++) {
                int a = s[i] & 0xFF;
                int b = s[(i + 1) % STATE] & 0xFF;
                int v = (a + b + round * 0x1F) & 0xFF;
                v = ((v << 3) | (v >>> 5)) & 0xFF;
                s[i] = (byte) (v ^ 0x5A);
            }
        }
    }

    static void absorb(byte[] s, byte[] data) {
        int i = 0;
        while (i < data.length) {
            for (int j = 0; j < RATE && i < data.length; j++, i++)
                s[j] ^= data[i];
            permute(s);
        }
    }

    public static byte[] mac(byte[] key, byte[] msg, int outLen) {
        byte[] s = new byte[STATE];
        absorb(s, key);
        absorb(s, msg);
        byte[] out = new byte[outLen];
        int o = 0;
        while (o < outLen) {
            for (int j = 0; j < RATE && o < outLen; j++, o++)
                out[o] = s[j];
            permute(s);
        }
        return out;
    }

    public static void main(String[] args) {
        byte[] t = mac("secretkey".getBytes(), "message".getBytes(), 16);
        StringBuilder sb = new StringBuilder();
        for (byte b : t) sb.append(String.format("%02X", b));
        System.out.println(sb);
    }
}
