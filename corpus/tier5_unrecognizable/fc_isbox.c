#include <stdint.h>

#define BLOCK 16

void build_inverse(const uint8_t table[256], uint8_t inv[256]) {
    for (int i = 0; i < 256; i++) inv[table[i]] = (uint8_t)i;
}

void apply_inverse(uint8_t *state, const uint8_t inv[256]) {
    for (int i = 0; i < BLOCK; i++) state[i] = inv[state[i]];
}
