#include <stdio.h>
#include <stdint.h>

#define ROUNDS 32
#define DELTA 0x9E3779B9

void tea_encrypt(uint32_t v[2], const uint32_t k[4]) {
    uint32_t v0 = v[0], v1 = v[1], sum = 0;
    for (int i = 0; i < ROUNDS; i++) {
        sum += DELTA;
        v0 += ((v1 << 4) + k[0]) ^ (v1 + sum) ^ ((v1 >> 5) + k[1]);
        v1 += ((v0 << 4) + k[2]) ^ (v0 + sum) ^ ((v0 >> 5) + k[3]);
    }
    v[0] = v0; v[1] = v1;
}

void tea_decrypt(uint32_t v[2], const uint32_t k[4]) {
    uint32_t v0 = v[0], v1 = v[1], sum = (uint32_t)(DELTA * ROUNDS);
    for (int i = 0; i < ROUNDS; i++) {
        v1 -= ((v0 << 4) + k[2]) ^ (v0 + sum) ^ ((v0 >> 5) + k[3]);
        v0 -= ((v1 << 4) + k[0]) ^ (v1 + sum) ^ ((v1 >> 5) + k[1]);
        sum -= DELTA;
    }
    v[0] = v0; v[1] = v1;
}

int main(void) {
    uint32_t k[4] = {0xA56BABCD, 0x00000000, 0xFFFFFFFF, 0xABCDEF01};
    uint32_t v[2] = {0x01234567, 0x89ABCDEF};
    tea_encrypt(v, k);
    printf("ct=%08X%08X\n", v[0], v[1]);
    tea_decrypt(v, k);
    printf("pt=%08X%08X\n", v[0], v[1]);
    return 0;
}
