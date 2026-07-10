public class DjKey {
    public static final int ROUNDS = 4;

    public static int[][] expand(int[] master) {
        int[] words = new int[DjSub.BLOCK];
        for (int i = 0; i < DjSub.BLOCK; i++)
            words[i] = i < master.length ? (master[i] & 0xFF) : i;
        int[][] subkeys = new int[ROUNDS + 1][DjSub.BLOCK];
        int rc = 1;
        for (int r = 0; r <= ROUNDS; r++) {
            for (int i = 0; i < DjSub.BLOCK; i++) {
                words[i] = (words[i] + words[(i + 1) % DjSub.BLOCK] + rc) & 0xFF;
                words[i] = ((words[i] << 1) | (words[i] >> 7)) & 0xFF;
            }
            System.arraycopy(words, 0, subkeys[r], 0, DjSub.BLOCK);
            rc = (rc * 3 + 1) & 0xFF;
        }
        return subkeys;
    }
}
