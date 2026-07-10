#include <stdint.h>
#include <stdio.h>

static uint64_t state = 88172645463325252ULL;

uint64_t xorshift64(void) {
    uint64_t x = state;
    x ^= x << 13;
    x ^= x >> 7;
    x ^= x << 17;
    state = x;
    return x;
}

double next_unit(void) {
    return (xorshift64() >> 11) * (1.0 / 9007199254740992.0);
}

int main(void) {
    state = 12345ULL;
    for (int i = 0; i < 5; i++) {
        printf("%llu\n", (unsigned long long)xorshift64());
    }
    printf("%f\n", next_unit());
    return 0;
}
