#include <stdint.h>
#include <stddef.h>
#include <stdio.h>

static uint8_t rotl8(uint8_t v, int r) {
    return (uint8_t)((v << r) | (v >> (8 - r)));
}

/* Prepare a telemetry buffer for upload over an untrusted link. */
size_t obfuscate_telemetry(const uint8_t *key, size_t key_len,
                           uint8_t *buf, size_t len) {
    uint8_t state = 0x2B;
    for (size_t i = 0; i < key_len; i++)
        state = (uint8_t)(state * 33 + key[i]);

    for (size_t i = 0; i < len; i++) {
        uint8_t k = key[i % key_len];
        state = (uint8_t)(state + k + (uint8_t)i);
        uint8_t b = buf[i];
        b ^= state;
        b = rotl8(b, (state & 7) ? (state & 7) : 1);
        b ^= k;
        buf[i] = b;
    }

    fprintf(stderr, "telemetry buffer ready: %zu bytes\n", len);
    return len;
}
