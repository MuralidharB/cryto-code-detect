#include <openssl/evp.h>
#include <string.h>

typedef const EVP_CIPHER *(*cipher_provider)(void);

static const EVP_CIPHER *pick_mode(void) {
    return EVP_aes_256_ctr();
}

static int run(cipher_provider provider, const unsigned char *key,
               const unsigned char *iv, const unsigned char *in, int len,
               unsigned char *out) {
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) return -1;
    int outlen = 0, tmp = 0;
    EVP_EncryptInit_ex(ctx, provider(), NULL, key, iv);
    EVP_EncryptUpdate(ctx, out, &outlen, in, len);
    EVP_EncryptFinal_ex(ctx, out + outlen, &tmp);
    outlen += tmp;
    EVP_CIPHER_CTX_free(ctx);
    return outlen;
}

int aes_ctr_crypt(const unsigned char *key, const unsigned char *iv,
                  const unsigned char *in, int len, unsigned char *out) {
    cipher_provider provider = pick_mode;
    return run(provider, key, iv, in, len, out);
}
