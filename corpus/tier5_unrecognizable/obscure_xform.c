#include <stdint.h>
#include <stddef.h>

/* Transforms a buffer in place under a key; the same call with the same key restores it. */
static uint8_t sub(uint8_t x, uint8_t k) {
    x = (uint8_t)((x << 3) | (x >> 5));
    x ^= (uint8_t)(k + 0x5B);
    return (uint8_t)(x * 167u);           /* 167 is odd => invertible mod 256 */
}

void scramble(uint8_t *buf, size_t n, const uint8_t *key, size_t klen) {
    uint8_t carry = 0xA7;
    for (size_t i = 0; i < n; i++) {
        uint8_t k = key[i % klen];
        buf[i] = sub((uint8_t)(buf[i] ^ carry), k);
        carry = (uint8_t)(buf[i] + k);     /* chaining: each byte feeds the next */
    }
}
