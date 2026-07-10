#include <stdint.h>

#define BLOCK 8
#define ROUNDS 4

void expand(const uint8_t *master, int mlen, uint8_t subkeys[ROUNDS + 1][BLOCK]) {
    uint8_t words[BLOCK];
    for (int i = 0; i < BLOCK; i++)
        words[i] = (i < mlen) ? master[i] : (uint8_t)i;
    uint8_t rc = 1;
    for (int r = 0; r <= ROUNDS; r++) {
        for (int i = 0; i < BLOCK; i++) {
            words[i] = (uint8_t)(words[i] + words[(i + 1) % BLOCK] + rc);
            words[i] = (uint8_t)((words[i] << 1) | (words[i] >> 7));
        }
        for (int i = 0; i < BLOCK; i++) subkeys[r][i] = words[i];
        rc = (uint8_t)(rc * 3 + 1);
    }
}
