#include <stdint.h>

#define BLOCK 16

static const int order[BLOCK] = {0, 5, 10, 15, 4, 9, 14, 3, 8, 13, 2, 7, 12, 1, 6, 11};

void reorder(uint8_t *state) {
    uint8_t tmp[BLOCK];
    for (int i = 0; i < BLOCK; i++) tmp[i] = state[order[i]];
    for (int i = 0; i < BLOCK; i++) state[i] = tmp[i];
}

void unreorder(uint8_t *state) {
    uint8_t tmp[BLOCK];
    for (int i = 0; i < BLOCK; i++) tmp[order[i]] = state[i];
    for (int i = 0; i < BLOCK; i++) state[i] = tmp[i];
}
