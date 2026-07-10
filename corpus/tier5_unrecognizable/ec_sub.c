#include <stdint.h>

#define BLOCK 8

void build_table(uint8_t seed, uint8_t table[256]) {
    for (int i = 0; i < 256; i++) table[i] = (uint8_t)i;
    uint8_t acc = seed ? seed : 1;
    for (int i = 0; i < 256; i++) {
        acc = (uint8_t)(acc * 5 + 0x3D);
        uint8_t j = acc ^ (acc >> 3);
        uint8_t t = table[i];
        table[i] = table[j];
        table[j] = t;
    }
}

void apply_table(uint8_t *state, const uint8_t table[256]) {
    for (int i = 0; i < BLOCK; i++) state[i] = table[state[i]];
}
