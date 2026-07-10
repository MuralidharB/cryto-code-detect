public class FjKey {
    public static final int ROUNDS = 6;

    public static int[][] expand(int[] master) {
        int n = master.length > 0 ? master.length : 1;
        int[] data = new int[n];
        for (int i = 0; i < n; i++) data[i] = master.length > 0 ? (master[i] & 0xFF) : 1;
        int total = FjSbox.BLOCK * (ROUNDS + 1);
        int[] words = new int[total];
        int filled = 0;
        while (filled < total) {
            for (int i = 0; i < n; i++) {
                data[i] = (data[i] + data[(i + 1) % n] + (filled + 1)) & 0xFF;
                data[i] = ((data[i] << 1) | (data[i] >> 7)) & 0xFF;
            }
            for (int i = 0; i < n && filled < total; i++) words[filled++] = data[i];
        }
        int[][] out = new int[ROUNDS + 1][FjSbox.BLOCK];
        for (int r = 0; r <= ROUNDS; r++)
            for (int i = 0; i < FjSbox.BLOCK; i++) out[r][i] = words[r * FjSbox.BLOCK + i];
        return out;
    }
}
