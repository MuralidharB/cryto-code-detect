public class FjPerm {
    static final int[] ORDER = {0, 5, 10, 15, 4, 9, 14, 3, 8, 13, 2, 7, 12, 1, 6, 11};

    public static void reorder(int[] state) {
        int[] tmp = new int[FjSbox.BLOCK];
        for (int i = 0; i < FjSbox.BLOCK; i++) tmp[i] = state[ORDER[i]];
        System.arraycopy(tmp, 0, state, 0, FjSbox.BLOCK);
    }

    public static void unreorder(int[] state) {
        int[] tmp = new int[FjSbox.BLOCK];
        for (int i = 0; i < FjSbox.BLOCK; i++) tmp[ORDER[i]] = state[i];
        System.arraycopy(tmp, 0, state, 0, FjSbox.BLOCK);
    }
}
