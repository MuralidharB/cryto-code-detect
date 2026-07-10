public class DjPerm {
    static final int[] ORDER = {2, 5, 0, 7, 4, 1, 6, 3};

    public static void permute(int[] state) {
        int[] tmp = new int[DjSub.BLOCK];
        for (int i = 0; i < DjSub.BLOCK; i++) tmp[i] = state[ORDER[i]];
        for (int i = 0; i < DjSub.BLOCK; i++) {
            int n = tmp[(i + 1) % DjSub.BLOCK];
            tmp[i] = (tmp[i] ^ ((n << 3) | (n >> 5))) & 0xFF;
        }
        System.arraycopy(tmp, 0, state, 0, DjSub.BLOCK);
    }
}
