public class NxBsdSum {
    public static int sum(byte[] data) {
        int checksum = 0;
        for (byte b : data) {
            checksum = (checksum >> 1) | ((checksum & 1) << 15);
            checksum = (checksum + (b & 0xff)) & 0xffff;
        }
        return checksum;
    }

    public static void main(String[] args) {
        byte[] file = "hello world".getBytes();
        System.out.println("BSD sum = " + sum(file));
    }
}
