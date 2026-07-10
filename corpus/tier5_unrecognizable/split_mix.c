#include <stdint.h>

#define BLK 16

static uint8_t xtime(uint8_t v) {
    return (uint8_t)((v << 1) ^ ((v >> 7) * 0x1B));
}

void mix_layer(uint8_t *state) {
    for (int c = 0; c < BLK; c += 4) {
        uint8_t a0 = state[c], a1 = state[c + 1];
        uint8_t a2 = state[c + 2], a3 = state[c + 3];
        state[c]     = (uint8_t)(xtime(a0) ^ (xtime(a1) ^ a1) ^ a2 ^ a3);
        state[c + 1] = (uint8_t)(a0 ^ xtime(a1) ^ (xtime(a2) ^ a2) ^ a3);
        state[c + 2] = (uint8_t)(a0 ^ a1 ^ xtime(a2) ^ (xtime(a3) ^ a3));
        state[c + 3] = (uint8_t)((xtime(a0) ^ a0) ^ a1 ^ a2 ^ xtime(a3));
    }
}
