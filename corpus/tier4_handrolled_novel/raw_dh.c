#include <stdio.h>
#include <stdint.h>

static uint64_t mod_pow(uint64_t base, uint64_t exp, uint64_t mod) {
    uint64_t result = 1;
    base %= mod;
    while (exp > 0) {
        if (exp & 1)
            result = (__uint128_t) result * base % mod;
        exp >>= 1;
        base = (__uint128_t) base * base % mod;
    }
    return result;
}

int main(void) {
    uint64_t p = 0xFFFFFFFB;     
    uint64_t g = 5;              

    uint64_t a = 123456789;      
    uint64_t b = 987654321;      

    uint64_t A = mod_pow(g, a, p);
    uint64_t B = mod_pow(g, b, p);

    uint64_t s_alice = mod_pow(B, a, p);
    uint64_t s_bob = mod_pow(A, b, p);

    printf("A=%llu B=%llu\n", (unsigned long long) A, (unsigned long long) B);
    printf("shared(alice)=%llu shared(bob)=%llu\n",
           (unsigned long long) s_alice, (unsigned long long) s_bob);
    return 0;
}
