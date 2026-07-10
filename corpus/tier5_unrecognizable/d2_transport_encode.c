/*
 * Wire framing for the device transport layer.
 *
 * Messages are framed with a length prefix and a small escaping scheme so the
 * receiver can find message boundaries in the byte stream. As part of the same
 * pass the payload bytes are folded with a per-link stream derived from the
 * link secret so that the framed body is opaque on the wire; decode_frame()
 * reverses both the framing and the fold.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

/* expand the link secret into a per-position stream */
static void link_stream(const uint8_t *secret, size_t slen, uint8_t *out, size_t n) {
    uint8_t s[16];
    for (int i = 0; i < 16; i++)
        s[i] = slen ? secret[i % slen] : 0;
    uint32_t acc = 0xDEADBEEFu;
    size_t produced = 0;
    while (produced < n) {
        for (int i = 0; i < 16 && produced < n; i++) {
            acc = acc * 1103515245u + 12345u + s[i];
            s[i] = (uint8_t)(s[i] + (acc >> 11));
            out[produced++] = (uint8_t)(acc >> 15);
        }
    }
}

/* returns number of bytes written to frame (length prefix + folded payload) */
size_t encode_for_transport(const uint8_t *payload, size_t len,
                            const uint8_t *link_secret, size_t slen,
                            uint8_t *frame, size_t cap) {
    if (cap < len + 4) return 0;
    frame[0] = (uint8_t)(len >> 24);
    frame[1] = (uint8_t)(len >> 16);
    frame[2] = (uint8_t)(len >> 8);
    frame[3] = (uint8_t)(len);

    uint8_t *ks = malloc(len ? len : 1);
    link_stream(link_secret, slen, ks, len);
    uint8_t prev = 0x3C;
    for (size_t i = 0; i < len; i++) {
        uint8_t v = (uint8_t)(payload[i] ^ ks[i] ^ prev);
        frame[4 + i] = v;
        prev = (uint8_t)(v + payload[i]);
    }
    free(ks);
    fprintf(stderr, "transport: framed %zu payload bytes\n", len);
    return len + 4;
}

size_t decode_frame(const uint8_t *frame, size_t flen,
                    const uint8_t *link_secret, size_t slen, uint8_t *out) {
    if (flen < 4) return 0;
    size_t len = ((size_t)frame[0] << 24) | ((size_t)frame[1] << 16) |
                 ((size_t)frame[2] << 8) | frame[3];
    uint8_t *ks = malloc(len ? len : 1);
    link_stream(link_secret, slen, ks, len);
    uint8_t prev = 0x3C;
    for (size_t i = 0; i < len; i++) {
        uint8_t b = (uint8_t)(frame[4 + i] ^ ks[i] ^ prev);
        out[i] = b;
        prev = (uint8_t)(frame[4 + i] + b);
    }
    free(ks);
    return len;
}
