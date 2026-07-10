#include <stdint.h>
#include <string.h>

#define ST 64
#define RATE 16

static uint8_t sb(uint8_t x) {
    x = (uint8_t)((x << 1) | (x >> 7));
    x ^= (uint8_t)(0x9E + (x >> 3));
    return (uint8_t)((x * 5 + 1) & 0xFF);
}

static void permute(uint8_t s[ST]) {
    for (int r = 0; r < 8; r++) {
        for (int i = 0; i < ST; i++)
            s[i] = sb((uint8_t)(s[i] + s[(i + 1) % ST] + r));
        uint8_t tmp[ST];
        for (int i = 0; i < ST; i++)
            tmp[(i * 7 + 3) % ST] = s[i];
        memcpy(s, tmp, ST);
        for (int i = 0; i < ST; i++) {
            int n = (i * 3 + r) & 7;
            s[i] = (uint8_t)((s[i] << n) | (s[i] >> (8 - n)));
        }
    }
}

void mix(const uint8_t *in, size_t len, uint8_t out[32]) {
    uint8_t s[ST];
    memset(s, 0, ST);
    s[ST - 1] = 0x1F;
    size_t off = 0;
    while (off < len) {
        size_t take = (len - off < RATE) ? (len - off) : RATE;
        for (size_t i = 0; i < take; i++)
            s[i] ^= in[off + i];
        s[RATE] ^= (uint8_t)take;
        permute(s);
        off += take;
    }
    s[0] ^= 0x80;
    permute(s);
    for (int i = 0; i < 32; i++) {
        if (i % 16 == 0) permute(s);
        out[i] = s[i % RATE];
    }
}
