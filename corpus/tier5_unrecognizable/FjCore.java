public class FjCore {
    static int[] transformBlock(int[] block, int[] master) {
        int[] table = FjSbox.buildTable(master.length > 0 ? master[0] : 1);
        int[][] subkeys = FjKey.expand(master);
        int[] state = new int[FjSbox.BLOCK];
        for (int i = 0; i < FjSbox.BLOCK; i++) state[i] = (block[i] ^ subkeys[0][i]) & 0xFF;
        for (int r = 1; r <= FjKey.ROUNDS; r++) {
            FjSbox.applyTable(state, table);
            FjPerm.reorder(state);
            FjMix.mix(state);
            for (int i = 0; i < FjSbox.BLOCK; i++) state[i] = (state[i] ^ subkeys[r][i]) & 0xFF;
        }
        return state;
    }

    public static byte[] run(byte[] data, int[] master) {
        int n = ((data.length + FjSbox.BLOCK - 1) / FjSbox.BLOCK) * FjSbox.BLOCK;
        byte[] out = new byte[n];
        int[] prev = new int[FjSbox.BLOCK];
        for (int off = 0; off < n; off += FjSbox.BLOCK) {
            int[] chunk = new int[FjSbox.BLOCK];
            for (int i = 0; i < FjSbox.BLOCK; i++) {
                int idx = off + i;
                chunk[i] = ((idx < data.length ? data[idx] : 0) & 0xFF) ^ prev[i];
            }
            prev = transformBlock(chunk, master);
            for (int i = 0; i < FjSbox.BLOCK; i++) out[off + i] = (byte) prev[i];
        }
        return out;
    }
}
