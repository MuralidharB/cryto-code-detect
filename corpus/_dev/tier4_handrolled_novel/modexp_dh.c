#include <stdio.h>

static unsigned long long modpow(unsigned long long base,
                                 unsigned long long exp,
                                 unsigned long long mod)
{
    unsigned long long result = 1ULL;
    base %= mod;
    while (exp > 0ULL) {
        if (exp & 1ULL) {
            result = (result * base) % mod;
        }
        base = (base * base) % mod;
        exp >>= 1ULL;
    }
    return result;
}

int main(void)
{
    unsigned long long p = 0x7FFFFFFFULL; 
    unsigned long long g = 5ULL;          

    unsigned long long a = 1234567ULL;    
    unsigned long long b = 7654321ULL;    

    unsigned long long A = modpow(g, a, p);
    unsigned long long B = modpow(g, b, p);

    unsigned long long sa = modpow(B, a, p);
    unsigned long long sb = modpow(A, b, p);

    printf("A=%llu B=%llu\n", A, B);
    printf("shared(Alice)=%llu shared(Bob)=%llu\n", sa, sb);
    printf("agree=%d\n", sa == sb);
    return 0;
}
