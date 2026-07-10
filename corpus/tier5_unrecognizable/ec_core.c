#include <stdint.h>

#define BLOCK 8
#define ROUNDS 4

void build_table(uint8_t seed, uint8_t table[256]);
void apply_table(uint8_t *state, const uint8_t table[256]);
void expand(const uint8_t *master, int mlen, uint8_t subkeys[ROUNDS + 1][BLOCK]);
void mix(uint8_t *state);

void transform_block(uint8_t *block, const uint8_t *master, int mlen) {
    uint8_t table[256];
    uint8_t subkeys[ROUNDS + 1][BLOCK];
    build_table(mlen ? master[0] : 1, table);
    expand(master, mlen, subkeys);

    for (int i = 0; i < BLOCK; i++) block[i] ^= subkeys[0][i];
    for (int r = 1; r <= ROUNDS; r++) {
        apply_table(block, table);
        mix(block);
        for (int i = 0; i < BLOCK; i++) block[i] ^= subkeys[r][i];
    }
}

void run(const uint8_t *in, int len, const uint8_t *master, int mlen, uint8_t *out) {
    uint8_t prev[BLOCK] = {0};
    for (int off = 0; off < len; off += BLOCK) {
        uint8_t chunk[BLOCK] = {0};
        for (int i = 0; i < BLOCK && off + i < len; i++) chunk[i] = in[off + i];
        for (int i = 0; i < BLOCK; i++) chunk[i] ^= prev[i];
        transform_block(chunk, master, mlen);
        for (int i = 0; i < BLOCK; i++) { out[off + i] = chunk[i]; prev[i] = chunk[i]; }
    }
}
