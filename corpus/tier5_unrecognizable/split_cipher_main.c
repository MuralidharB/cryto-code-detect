#include <stdint.h>

#define BLK 16
#define STEPS 10

void mix_layer(uint8_t *state);
void expand_key(const uint8_t *key, uint8_t rk[STEPS + 1][BLK]);

static uint8_t map_byte(uint8_t v) {
    return (uint8_t)((v * 0xF5 + 0x63) & 0xFF);
}

void transform_state(const uint8_t *in, const uint8_t *key, uint8_t *out) {
    uint8_t rk[STEPS + 1][BLK];
    uint8_t state[BLK];
    expand_key(key, rk);
    for (int i = 0; i < BLK; i++) {
        state[i] = in[i] ^ rk[0][i];
    }
    for (int s = 1; s <= STEPS; s++) {
        for (int i = 0; i < BLK; i++) {
            state[i] = map_byte(state[i]);
        }
        mix_layer(state);
        for (int i = 0; i < BLK; i++) {
            state[i] ^= rk[s][i];
        }
    }
    for (int i = 0; i < BLK; i++) {
        out[i] = state[i];
    }
}
