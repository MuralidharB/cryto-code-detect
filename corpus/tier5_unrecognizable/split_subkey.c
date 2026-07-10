#include <stdint.h>

#define BLK 16
#define STEPS 10

void expand_key(const uint8_t *key, uint8_t rk[STEPS + 1][BLK]) {
    for (int i = 0; i < BLK; i++) {
        rk[0][i] = key[i];
    }
    for (int s = 1; s <= STEPS; s++) {
        uint8_t carry = rk[s - 1][BLK - 1];
        for (int i = 0; i < BLK; i++) {
            uint8_t prev = rk[s - 1][i];
            uint8_t t = (uint8_t)((carry << 2) | (carry >> 6));
            rk[s][i] = (uint8_t)(prev ^ t ^ (uint8_t)(s * 0x1B + i));
            carry = prev;
        }
    }
}
