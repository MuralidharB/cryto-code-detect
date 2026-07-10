#include <stdint.h>
#include <string.h>

/* 128-bit value held as two big-endian 64-bit halves */
typedef struct { uint64_t hi, lo; } val128;

/* carry-less multiply in the field defined by x^128 + x^7 + x^2 + x + 1,
   reduction bit placed at the top per the big-endian bit convention */
static val128 field_mul(val128 x, val128 y) {
    val128 z = {0, 0};
    val128 v = x;
    for (int i = 0; i < 128; i++) {
        uint64_t bit = (i < 64) ? (y.hi >> (63 - i)) & 1
                                : (y.lo >> (127 - i)) & 1;
        if (bit) { z.hi ^= v.hi; z.lo ^= v.lo; }
        uint64_t lsb = v.lo & 1;
        v.lo = (v.lo >> 1) | (v.hi << 63);
        v.hi = v.hi >> 1;
        if (lsb) v.hi ^= 0xe100000000000000ULL;
    }
    return z;
}

static val128 load(const uint8_t b[16]) {
    val128 r;
    r.hi = r.lo = 0;
    for (int i = 0; i < 8; i++) r.hi = (r.hi << 8) | b[i];
    for (int i = 8; i < 16; i++) r.lo = (r.lo << 8) | b[i];
    return r;
}

/* fold one block into the running accumulator under the secret point h */
void mac_step(val128 *acc, const uint8_t block[16], val128 h) {
    val128 in = load(block);
    acc->hi ^= in.hi;
    acc->lo ^= in.lo;
    *acc = field_mul(*acc, h);
}

void mac_finish(const val128 *acc, uint8_t out[16]) {
    for (int i = 0; i < 8; i++) out[i]     = (acc->hi >> (56 - 8 * i)) & 0xff;
    for (int i = 0; i < 8; i++) out[8 + i] = (acc->lo >> (56 - 8 * i)) & 0xff;
}
