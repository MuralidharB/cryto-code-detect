#include <stdint.h>
#include <string.h>
#include <stdio.h>

static uint8_t SBOX[256];
static uint8_t RCON[11];

static uint8_t gmul(uint8_t a, uint8_t b) {
    uint8_t p = 0;
    int i;
    for (i = 0; i < 8; i++) {
        if (b & 1) p ^= a;
        uint8_t hi = a & 0x80;
        a <<= 1;
        if (hi) a ^= 0x1B;
        b >>= 1;
    }
    return p;
}

static uint8_t ginv(uint8_t a) {
    if (a == 0) return 0;
    int i;
    uint8_t r = 1;
    /* inverse = a^254 in the field */
    for (i = 0; i < 254; i++) r = gmul(r, a);
    return r;
}

static uint8_t rotl8(uint8_t x, int n) {
    return (uint8_t)((x << n) | (x >> (8 - n)));
}

static void build_tables(void) {
    int i;
    for (i = 0; i < 256; i++) {
        uint8_t inv = ginv((uint8_t)i);
        uint8_t s = inv ^ rotl8(inv, 1) ^ rotl8(inv, 2) ^ rotl8(inv, 3) ^ rotl8(inv, 4) ^ 0x63;
        SBOX[i] = s;
    }
    uint8_t c = 1;
    RCON[0] = 0;
    for (i = 1; i <= 10; i++) {
        RCON[i] = c;
        c = gmul(c, 2);
    }
}

static void expand_key(const uint8_t key[16], uint8_t rk[176]) {
    memcpy(rk, key, 16);
    int i = 16;
    uint8_t t[4];
    int rc = 1;
    while (i < 176) {
        memcpy(t, rk + i - 4, 4);
        if (i % 16 == 0) {
            uint8_t tmp = t[0];
            t[0] = SBOX[t[1]] ^ RCON[rc++];
            t[1] = SBOX[t[2]];
            t[2] = SBOX[t[3]];
            t[3] = SBOX[tmp];
        }
        int j;
        for (j = 0; j < 4; j++) {
            rk[i] = rk[i - 16] ^ t[j];
            i++;
        }
    }
}

static void add_rk(uint8_t s[16], const uint8_t *rk) {
    int i;
    for (i = 0; i < 16; i++) s[i] ^= rk[i];
}

static void sub_bytes(uint8_t s[16]) {
    int i;
    for (i = 0; i < 16; i++) s[i] = SBOX[s[i]];
}

static void shift_rows(uint8_t s[16]) {
    uint8_t t[16];
    int r, c;
    for (r = 0; r < 4; r++)
        for (c = 0; c < 4; c++)
            t[r + 4 * c] = s[r + 4 * ((c + r) % 4)];
    memcpy(s, t, 16);
}

static void mix_columns(uint8_t s[16]) {
    int c;
    for (c = 0; c < 4; c++) {
        uint8_t *p = s + 4 * c;
        uint8_t a0 = p[0], a1 = p[1], a2 = p[2], a3 = p[3];
        p[0] = gmul(a0, 2) ^ gmul(a1, 3) ^ a2 ^ a3;
        p[1] = a0 ^ gmul(a1, 2) ^ gmul(a2, 3) ^ a3;
        p[2] = a0 ^ a1 ^ gmul(a2, 2) ^ gmul(a3, 3);
        p[3] = gmul(a0, 3) ^ a1 ^ a2 ^ gmul(a3, 2);
    }
}

void encrypt_block(const uint8_t in[16], const uint8_t key[16], uint8_t out[16]) {
    build_tables();
    uint8_t rk[176];
    expand_key(key, rk);
    uint8_t s[16];
    memcpy(s, in, 16);
    add_rk(s, rk);
    int round;
    for (round = 1; round < 10; round++) {
        sub_bytes(s);
        shift_rows(s);
        mix_columns(s);
        add_rk(s, rk + 16 * round);
    }
    sub_bytes(s);
    shift_rows(s);
    add_rk(s, rk + 160);
    memcpy(out, s, 16);
}

int main(void) {
    uint8_t key[16] = {0}, in[16] = {0}, out[16];
    encrypt_block(in, key, out);
    int i;
    for (i = 0; i < 16; i++) printf("%02x", out[i]);
    printf("\n");
    return 0;
}
