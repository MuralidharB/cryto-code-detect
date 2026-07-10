public class NxCrc8 {
    private static final int POLY = 0x07;

    public static int crc8(byte[] data) {
        int crc = 0x00;
        for (byte b : data) {
            crc ^= (b & 0xff);
            for (int i = 0; i < 8; i++) {
                if ((crc & 0x80) != 0) {
                    crc = (crc << 1) ^ POLY;
                } else {
                    crc <<= 1;
                }
                crc &= 0xff;
            }
        }
        return crc;
    }

    public static void main(String[] args) {
        byte[] frame = {0x01, 0x02, 0x03, 0x04};
        System.out.printf("CRC-8 = 0x%02X%n", crc8(frame));
    }
}
