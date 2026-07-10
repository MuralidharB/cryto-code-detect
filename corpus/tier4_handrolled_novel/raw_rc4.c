#include <stdio.h>
#include <stdint.h>
#include <string.h>

typedef struct { uint8_t s[256]; int i, j; } rc4_state;

void rc4_init(rc4_state *st, const uint8_t *key, int keylen) {
    for (int i = 0; i < 256; i++) st->s[i] = (uint8_t) i;
    int j = 0;
    for (int i = 0; i < 256; i++) {
        j = (j + st->s[i] + key[i % keylen]) & 0xFF;
        uint8_t t = st->s[i]; st->s[i] = st->s[j]; st->s[j] = t;
    }
    st->i = 0; st->j = 0;
}

void rc4_crypt(rc4_state *st, const uint8_t *in, uint8_t *out, int len) {
    for (int n = 0; n < len; n++) {
        st->i = (st->i + 1) & 0xFF;
        st->j = (st->j + st->s[st->i]) & 0xFF;
        uint8_t t = st->s[st->i]; st->s[st->i] = st->s[st->j]; st->s[st->j] = t;
        uint8_t k = st->s[(st->s[st->i] + st->s[st->j]) & 0xFF];
        out[n] = in[n] ^ k;
    }
}

int main(void) {
    rc4_state st;
    const uint8_t key[] = "Secret";
    const char *msg = "Attack at dawn";
    uint8_t buf[64];
    rc4_init(&st, key, 6);
    rc4_crypt(&st, (const uint8_t *) msg, buf, strlen(msg));
    for (size_t i = 0; i < strlen(msg); i++) printf("%02X", buf[i]);
    printf("\n");
    return 0;
}
