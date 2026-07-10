#include <stdint.h>

#define BLOCK 8

static uint8_t xtime(uint8_t x) {
    return (uint8_t)((x << 1) ^ ((x >> 7) * 0x1B));
}

void mix(uint8_t *state) {
    for (int base = 0; base < BLOCK; base += 4) {
        uint8_t a = state[base], b = state[base + 1];
        uint8_t c = state[base + 2], d = state[base + 3];
        state[base]     = xtime(a) ^ (xtime(b) ^ b) ^ c ^ d;
        state[base + 1] = a ^ xtime(b) ^ (xtime(c) ^ c) ^ d;
        state[base + 2] = a ^ b ^ xtime(c) ^ (xtime(d) ^ d);
        state[base + 3] = (xtime(a) ^ a) ^ b ^ c ^ xtime(d);
    }
}
