#include <stdint.h>

#define BLOCK 16

void build_table(uint8_t seed, uint8_t table[256]) {
    for (int i = 0; i < 256; i++) table[i] = (uint8_t)i;
    uint8_t acc = seed ? seed : 1;
    for (int i = 0; i < 256; i++) {
        acc = (uint8_t)(acc * 7 + 0x1B);
        uint8_t j = acc ^ (acc >> 4) ^ (uint8_t)i;
        uint8_t t = table[i];
        table[i] = table[j];
        table[j] = t;
    }
}

void apply_table(uint8_t *state, const uint8_t table[256]) {
    for (int i = 0; i < BLOCK; i++) state[i] = table[state[i]];
}
