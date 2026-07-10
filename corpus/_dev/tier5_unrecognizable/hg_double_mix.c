#include <stdint.h>
#include <stddef.h>

static void nib_tables(const uint8_t *key, size_t klen, uint8_t f[16], uint8_t inv[16]) {
    for (int i = 0; i < 16; i++) f[i] = (uint8_t)i;
    int j = 0;
    for (int r = 0; r < 3; r++)
        for (int i = 0; i < 16; i++) {
            j = (j + f[i] + key[(i + r) % klen]) & 15;
            uint8_t t = f[i]; f[i] = f[j]; f[j] = t;
        }
    for (int i = 0; i < 16; i++) inv[f[i]] = (uint8_t)i;
}

static void sub_layer(uint8_t *buf, size_t n, const uint8_t t[16]) {
    for (size_t i = 0; i < n; i++)
        buf[i] = (uint8_t)((t[buf[i] >> 4] << 4) | t[buf[i] & 15]);
}

static void rot_layer(uint8_t *buf, size_t n, int amt) {
    amt %= (int)(n * 8);
    if (amt < 0) amt += (int)(n * 8);
    int bytes = amt / 8, bits = amt % 8;
    uint8_t tmp[512];
    for (size_t i = 0; i < n; i++) tmp[i] = buf[i];
    for (size_t i = 0; i < n; i++) {
        size_t src = (i + n - bytes) % n;
        size_t prev = (src + n - 1) % n;
        buf[i] = (uint8_t)((tmp[src] >> bits) | (tmp[prev] << (8 - bits)));
    }
}

void forward(uint8_t *buf, size_t n, const uint8_t *key, size_t klen) {
    uint8_t f[16], inv[16];
    nib_tables(key, klen, f, inv);
    int amt = 0;
    for (size_t i = 0; i < klen; i++) amt += key[i];
    sub_layer(buf, n, f);
    rot_layer(buf, n, amt);
    sub_layer(buf, n, f);
}

void backward(uint8_t *buf, size_t n, const uint8_t *key, size_t klen) {
    uint8_t f[16], inv[16];
    nib_tables(key, klen, f, inv);
    int amt = 0;
    for (size_t i = 0; i < klen; i++) amt += key[i];
    sub_layer(buf, n, inv);
    rot_layer(buf, n, -amt);
    sub_layer(buf, n, inv);
}
