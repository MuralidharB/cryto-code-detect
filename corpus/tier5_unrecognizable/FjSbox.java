public class FjSbox {
    public static final int BLOCK = 16;

    public static int[] buildTable(int seed) {
        int[] table = new int[256];
        for (int i = 0; i < 256; i++) table[i] = i;
        int acc = (seed & 0xFF);
        if (acc == 0) acc = 1;
        for (int i = 0; i < 256; i++) {
            acc = (acc * 7 + 0x1B) & 0xFF;
            int j = (acc ^ (acc >> 4) ^ i) & 0xFF;
            int t = table[i];
            table[i] = table[j];
            table[j] = t;
        }
        return table;
    }

    public static void applyTable(int[] state, int[] table) {
        for (int i = 0; i < state.length; i++) state[i] = table[state[i] & 0xFF];
    }
}
