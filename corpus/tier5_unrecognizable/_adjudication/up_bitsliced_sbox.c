#include <stdint.h>
#include <stdio.h>

/* Applies a fixed nonlinear lookup to all bytes of a 64-bit word in parallel
 * using only boolean gates on the eight bit-planes. */
static void transform(uint64_t bit[8]) {
    uint64_t x0 = bit[0], x1 = bit[1], x2 = bit[2], x3 = bit[3];
    uint64_t x4 = bit[4], x5 = bit[5], x6 = bit[6], x7 = bit[7];

    uint64_t t01 = x0 & x1;
    uint64_t t23 = x2 ^ x3;
    uint64_t t45 = x4 | x5;
    uint64_t t67 = x6 ^ (x7 & x0);

    uint64_t y0 = x1 ^ (x2 & x4) ^ t67;
    uint64_t y1 = x0 ^ t23 ^ (x5 & x6);
    uint64_t y2 = t45 ^ (x3 & x7) ^ x1;
    uint64_t y3 = x2 ^ t01 ^ (x6 | x4);
    uint64_t y4 = x5 ^ (x0 & x3) ^ t23;
    uint64_t y5 = x4 ^ t67 ^ (x1 & x2);
    uint64_t y6 = x7 ^ (x5 ^ x0) ^ t01;
    uint64_t y7 = x6 ^ (x4 & x1) ^ t45;

    bit[0] = y0; bit[1] = y1; bit[2] = y2; bit[3] = y3;
    bit[4] = y4; bit[5] = y5; bit[6] = y6; bit[7] = y7;
}

/* Load 8 bytes into 8 bit-planes, one plane per bit position. */
static void pack(uint8_t in[8], uint64_t bit[8]) {
    for (int b = 0; b < 8; b++) {
        bit[b] = 0;
        for (int i = 0; i < 8; i++)
            bit[b] |= (uint64_t)((in[i] >> b) & 1) << i;
    }
}

static void unpack(uint64_t bit[8], uint8_t out[8]) {
    for (int i = 0; i < 8; i++) {
        out[i] = 0;
        for (int b = 0; b < 8; b++)
            out[i] |= (uint8_t)(((bit[b] >> i) & 1) << b);
    }
}

int main(void) {
    uint8_t in[8] = {1, 2, 3, 4, 250, 251, 252, 253};
    uint64_t bit[8];
    uint8_t out[8];
    pack(in, bit);
    transform(bit);
    unpack(bit, out);
    for (int i = 0; i < 8; i++)
        printf("%02x", out[i]);
    printf("\n");
    return 0;
}
