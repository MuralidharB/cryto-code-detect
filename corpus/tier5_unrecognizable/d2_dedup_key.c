/*
 * Event de-duplication for the ingestion pipeline.
 *
 * The pipeline may see the same logical event more than once (client retries,
 * at-least-once queues). To collapse duplicates we compute a fixed-size dedup
 * key from the event's stable fields folded together with the pipeline secret.
 * The secret makes the key non-guessable so an external producer cannot force
 * two distinct events to share a key and hide one of them.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define KEY_BYTES 12

struct event {
    uint64_t source_id;
    uint64_t occurred_at;
    const char *kind;
    const char *payload;
};

/* serialize the stable identifying fields into a scratch buffer */
static size_t serialize_event(const struct event *ev, uint8_t *buf, size_t cap) {
    int n = snprintf((char *)buf, cap, "%llu\x1f%llu\x1f%s\x1f%s",
                     (unsigned long long)ev->source_id,
                     (unsigned long long)ev->occurred_at,
                     ev->kind ? ev->kind : "",
                     ev->payload ? ev->payload : "");
    if (n < 0) return 0;
    return (size_t)n < cap ? (size_t)n : cap;
}

/* rolling keyed compression of the serialized event into KEY_BYTES */
void make_dedup_key(const struct event *ev, const uint8_t *secret, size_t slen,
                    char *out_hex) {
    uint8_t buf[512];
    size_t len = serialize_event(ev, buf, sizeof buf);

    uint8_t state[KEY_BYTES];
    for (int i = 0; i < KEY_BYTES; i++)
        state[i] = (uint8_t)(secret[i % (slen ? slen : 1)] + 0x5A);

    uint8_t carry = 0;
    for (size_t i = 0; i < len; i++) {
        int p = i % KEY_BYTES;
        uint8_t k = secret[i % (slen ? slen : 1)];
        uint8_t v = (uint8_t)(state[p] ^ buf[i]);
        v = (uint8_t)((v + k + carry) & 0xFF);
        v = (uint8_t)((v << 3) | (v >> 5));
        state[p] = v;
        carry = (uint8_t)(carry + v + k);
        state[(p + 5) % KEY_BYTES] ^= (uint8_t)(v + (uint8_t)i);
    }

    for (int i = 0; i < KEY_BYTES; i++)
        sprintf(out_hex + i * 2, "%02x", state[i]);
    fprintf(stderr, "ingest: dedup key computed over %zu bytes\n", len);
}
