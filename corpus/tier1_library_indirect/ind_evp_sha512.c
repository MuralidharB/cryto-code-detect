#include <openssl/evp.h>
#include <string.h>

typedef const EVP_MD *(*md_provider)(void);

static const EVP_MD *select_md(const char *name) {
    md_provider p = EVP_sha512;
    if (strcmp(name, "sha384") == 0)
        p = EVP_sha384;
    return p();
}

int hash_digest(const char *algo, const unsigned char *data, size_t len,
                unsigned char *out, unsigned int *out_len) {
    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    if (!ctx)
        return 0;
    int ok = EVP_DigestInit_ex(ctx, select_md(algo), NULL) &&
             EVP_DigestUpdate(ctx, data, len) &&
             EVP_DigestFinal_ex(ctx, out, out_len);
    EVP_MD_CTX_free(ctx);
    return ok;
}
