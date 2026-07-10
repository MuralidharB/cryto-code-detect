#include <stdio.h>
#include <stdint.h>
#include <string.h>

static uint32_t lfsr_next(uint32_t *reg)
{
    uint32_t out = 0;
    for (int i = 0; i < 8; i++) {
        uint32_t lsb = *reg & 1u;
        *reg >>= 1;
        if (lsb) {
            *reg ^= 0xB4BCD35Cu; 
        }
        out = (out << 1) | (*reg & 1u);
    }
    return out & 0xFFu;
}

static void lfsr_crypt(uint32_t seed, const uint8_t *in, uint8_t *out, size_t n)
{
    uint32_t reg = seed ? seed : 0xACE1u;
    for (size_t i = 0; i < n; i++) {
        uint8_t ks = (uint8_t)lfsr_next(&reg);
        out[i] = in[i] ^ ks;
    }
}

int main(void)
{
    const char *msg = "hello blk";
    size_t n = strlen(msg);
    uint8_t enc[64], dec[64];
    lfsr_crypt(0x1234ABCDu, (const uint8_t *)msg, enc, n);
    lfsr_crypt(0x1234ABCDu, enc, dec, n);
    for (size_t i = 0; i < n; i++)
        printf("%02x", enc[i]);
    printf("\n%.*s\n", (int)n, dec);
    return 0;
}
