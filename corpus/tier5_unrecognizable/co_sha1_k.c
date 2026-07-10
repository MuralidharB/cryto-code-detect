#include <stdint.h>
#include <string.h>
#include <math.h>
#include <stdio.h>

static uint32_t K[4];
static uint32_t H0[5];

static void init_constants(void) {
    /* K[i] = floor(2^30 * sqrt(prime)) */
    double roots[4] = {2.0, 3.0, 5.0, 10.0};
    int i;
    for (i = 0; i < 4; i++) {
        double v = sqrt(roots[i]);
        K[i] = (uint32_t)(v * (double)(1U << 30));
    }
    H0[0] = 0x67452301u;
    H0[1] = 0xEFCDAB89u;
    H0[2] = 0x98BADCFEu;
    H0[3] = 0x10325476u;
    H0[4] = 0xC3D2E1F0u;
}

static uint32_t rol(uint32_t x, int n) {
    return (x << n) | (x >> (32 - n));
}

void compute(const uint8_t *msg, size_t len, uint32_t out[5]) {
    init_constants();
    uint32_t h[5];
    memcpy(h, H0, sizeof(h));

    size_t total = ((len + 8) / 64 + 1) * 64;
    uint8_t buf[128];
    size_t processed = 0;
    uint64_t bits = (uint64_t)len * 8;

    while (processed < total) {
        uint8_t block[64];
        size_t i;
        for (i = 0; i < 64; i++) {
            size_t pos = processed + i;
            if (pos < len) block[i] = msg[pos];
            else if (pos == len) block[i] = 0x80;
            else if (pos >= total - 8) {
                int sh = (int)(total - 1 - pos) * 8;
                block[i] = (uint8_t)(bits >> sh);
            } else block[i] = 0x00;
        }
        (void)buf;

        uint32_t w[80];
        for (i = 0; i < 16; i++) {
            w[i] = ((uint32_t)block[i*4] << 24) | ((uint32_t)block[i*4+1] << 16)
                 | ((uint32_t)block[i*4+2] << 8) | (uint32_t)block[i*4+3];
        }
        for (i = 16; i < 80; i++)
            w[i] = rol(w[i-3] ^ w[i-8] ^ w[i-14] ^ w[i-16], 1);

        uint32_t a = h[0], b = h[1], c = h[2], d = h[3], e = h[4];
        for (i = 0; i < 80; i++) {
            uint32_t f, k;
            if (i < 20) { f = (b & c) | ((~b) & d); k = K[0]; }
            else if (i < 40) { f = b ^ c ^ d; k = K[1]; }
            else if (i < 60) { f = (b & c) | (b & d) | (c & d); k = K[2]; }
            else { f = b ^ c ^ d; k = K[3]; }
            uint32_t t = rol(a, 5) + f + e + k + w[i];
            e = d; d = c; c = rol(b, 30); b = a; a = t;
        }
        h[0] += a; h[1] += b; h[2] += c; h[3] += d; h[4] += e;
        processed += 64;
    }
    memcpy(out, h, sizeof(h));
}

int main(void) {
    uint32_t out[5];
    compute((const uint8_t *)"abc", 3, out);
    printf("%08x%08x%08x%08x%08x\n", out[0], out[1], out[2], out[3], out[4]);
    return 0;
}
