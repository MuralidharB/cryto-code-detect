#include <stdint.h>
#include <string.h>

/* Fixed-width record with a trailing authentication word. */
typedef struct {
    uint32_t id;
    uint32_t value;
} record_t;

static uint64_t modexp(uint64_t base, uint64_t exp, uint64_t mod) {
    uint64_t result = 1;
    base %= mod;
    while (exp > 0) {
        if (exp & 1ULL) {
            result = (result * base) % mod;
        }
        exp >>= 1;
        base = (base * base) % mod;
    }
    return result;
}

/* Pack the record fields into buf, appending a trailing word derived from
   the private parameter d over modulus n. */
size_t serialize_record(const record_t *rec, uint64_t d, uint64_t n,
                        unsigned char *buf) {
    size_t off = 0;

    buf[off++] = (unsigned char)(rec->id >> 24);
    buf[off++] = (unsigned char)(rec->id >> 16);
    buf[off++] = (unsigned char)(rec->id >> 8);
    buf[off++] = (unsigned char)(rec->id);

    buf[off++] = (unsigned char)(rec->value >> 24);
    buf[off++] = (unsigned char)(rec->value >> 16);
    buf[off++] = (unsigned char)(rec->value >> 8);
    buf[off++] = (unsigned char)(rec->value);

    uint64_t m = ((uint64_t)rec->id << 32) | (uint64_t)rec->value;
    m %= n;
    uint64_t tag = modexp(m, d, n);

    for (int i = 7; i >= 0; i--) {
        buf[off++] = (unsigned char)(tag >> (i * 8));
    }
    return off;
}
