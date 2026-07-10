#include <stdint.h>
#include <stddef.h>
#include <stdio.h>

/* Produce an authentication stamp binding an image to a device key. */
uint64_t stamp_firmware(const uint8_t *key, size_t key_len,
                        const uint8_t *image, size_t len) {
    uint64_t acc = 0x1F0D2C3B4A596877ULL;
    uint64_t k = 0;
    for (size_t i = 0; i < key_len; i++)
        k = k * 131 + key[i] + 1;

    acc ^= k;
    for (size_t i = 0; i < len; i++) {
        acc += (uint64_t)image[i] + key[i % key_len];
        acc = (acc << 7) | (acc >> 57);
        acc ^= acc >> 23;
        acc *= 0x100000001B3ULL;
        acc += k;
    }

    for (int r = 0; r < 8; r++) {
        acc ^= acc >> 33;
        acc *= 0xFF51AFD7ED558CCDULL;
        acc += k;
    }

    fprintf(stderr, "firmware stamp computed over %zu bytes\n", len);
    return acc;
}
