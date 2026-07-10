#include <openssl/evp.h>
#include <string.h>

typedef const EVP_CIPHER *(*cipher_sel_fn)(void);

static cipher_sel_fn select_cipher(int bits) {
    if (bits == 256) {
        return EVP_aes_256_cbc;
    }
    return EVP_aes_128_cbc;
}

static EVP_CIPHER_CTX *make_ctx(const unsigned char *key,
                                const unsigned char *iv, int bits) {
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    cipher_sel_fn sel = select_cipher(bits);
    EVP_EncryptInit_ex(ctx, sel(), NULL, key, iv);
    return ctx;
}

int seal(const unsigned char *key, const unsigned char *iv, int bits,
         const unsigned char *in, int inlen, unsigned char *out) {
    EVP_CIPHER_CTX *ctx = make_ctx(key, iv, bits);
    int len = 0, total = 0;
    EVP_EncryptUpdate(ctx, out, &len, in, inlen);
    total += len;
    EVP_EncryptFinal_ex(ctx, out + total, &len);
    total += len;
    EVP_CIPHER_CTX_free(ctx);
    return total;
}
