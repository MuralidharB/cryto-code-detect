public class DjCore {
    static int[] transformBlock(int[] block, int[] master) {
        int[] table = DjSub.buildTable(master.length > 0 ? master[0] : 1);
        int[][] subkeys = DjKey.expand(master);
        int[] state = new int[DjSub.BLOCK];
        for (int i = 0; i < DjSub.BLOCK; i++) state[i] = block[i] ^ subkeys[0][i];
        for (int r = 1; r <= DjKey.ROUNDS; r++) {
            DjSub.applyTable(state, table);
            DjPerm.permute(state);
            for (int i = 0; i < DjSub.BLOCK; i++) state[i] = (state[i] ^ subkeys[r][i]) & 0xFF;
        }
        return state;
    }

    public static byte[] run(byte[] data, int[] master) {
        int n = ((data.length + DjSub.BLOCK - 1) / DjSub.BLOCK) * DjSub.BLOCK;
        byte[] out = new byte[n];
        int[] prev = new int[DjSub.BLOCK];
        for (int off = 0; off < n; off += DjSub.BLOCK) {
            int[] chunk = new int[DjSub.BLOCK];
            for (int i = 0; i < DjSub.BLOCK; i++) {
                int idx = off + i;
                chunk[i] = ((idx < data.length ? data[idx] : 0) & 0xFF) ^ prev[i];
            }
            prev = transformBlock(chunk, master);
            for (int i = 0; i < DjSub.BLOCK; i++) out[off + i] = (byte) prev[i];
        }
        return out;
    }
}
