#include <stdint.h>
#include <string.h>

/* inverse nonlinear byte map (precomputed elsewhere, passed in) */
static void inv_sub(uint8_t s[16], const uint8_t inv_tab[256]) {
    for (int i = 0; i < 16; i++) s[i] = inv_tab[s[i]];
}

/* inverse of the row-wise byte rotation */
static void inv_shift(uint8_t s[16]) {
    uint8_t t[16];
    static const int perm[16] = {0,13,10,7,4,1,14,11,8,5,2,15,12,9,6,3};
    for (int i = 0; i < 16; i++) t[i] = s[perm[i]];
    memcpy(s, t, 16);
}

static uint8_t gmul(uint8_t a, uint8_t b) {
    uint8_t p = 0;
    for (int i = 0; i < 8; i++) {
        if (b & 1) p ^= a;
        uint8_t hi = a & 0x80;
        a <<= 1;
        if (hi) a ^= 0x1b;
        b >>= 1;
    }
    return p;
}

/* inverse of the column mixing step */
static void inv_mix(uint8_t s[16]) {
    for (int c = 0; c < 4; c++) {
        uint8_t *p = s + 4 * c;
        uint8_t a0 = p[0], a1 = p[1], a2 = p[2], a3 = p[3];
        p[0] = gmul(a0,14)^gmul(a1,11)^gmul(a2,13)^gmul(a3,9);
        p[1] = gmul(a0,9)^gmul(a1,14)^gmul(a2,11)^gmul(a3,13);
        p[2] = gmul(a0,13)^gmul(a1,9)^gmul(a2,14)^gmul(a3,11);
        p[3] = gmul(a0,11)^gmul(a1,13)^gmul(a2,9)^gmul(a3,14);
    }
}

void inverse_transform(uint8_t s[16], const uint32_t *subkeys, int rounds,
                       const uint8_t inv_tab[256]) {
    const uint8_t *rk = (const uint8_t *)subkeys;
    for (int i = 0; i < 16; i++) s[i] ^= rk[rounds * 16 + i];   /* strip final key */
    for (int r = rounds - 1; r >= 1; r--) {
        inv_shift(s);
        inv_sub(s, inv_tab);
        for (int i = 0; i < 16; i++) s[i] ^= rk[r * 16 + i];
        inv_mix(s);
    }
    inv_shift(s);
    inv_sub(s, inv_tab);
    for (int i = 0; i < 16; i++) s[i] ^= rk[i];
}
