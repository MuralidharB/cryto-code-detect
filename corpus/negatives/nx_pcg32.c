#include <stdio.h>
#include <stdint.h>

static uint64_t pcg_state = 0x853c49e6748fea9bULL;
static const uint64_t PCG_MULT = 6364136223846793005ULL;
static const uint64_t PCG_INC  = 1442695040888963407ULL;

uint32_t pcg32_next(void) {
    uint64_t old = pcg_state;
    pcg_state = old * PCG_MULT + PCG_INC;
    uint32_t xorshifted = (uint32_t)(((old >> 18u) ^ old) >> 27u);
    uint32_t rot = (uint32_t)(old >> 59u);
    return (xorshifted >> rot) | (xorshifted << ((-rot) & 31));
}

int main(void) {
    for (int i = 0; i < 5; i++) {
        printf("%u\n", pcg32_next());
    }
    return 0;
}
