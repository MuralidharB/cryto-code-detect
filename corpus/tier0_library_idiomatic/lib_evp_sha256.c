#include <stdio.h>
#include <string.h>
#include <openssl/evp.h>

int main(void) {
    const char *msg = "the quick brown fox";
    unsigned char digest[EVP_MAX_MD_SIZE];
    unsigned int digest_len = 0;

    if (EVP_Digest(msg, strlen(msg), digest, &digest_len, EVP_sha256(), NULL) != 1) {
        fprintf(stderr, "digest failed\n");
        return 1;
    }

    for (unsigned int i = 0; i < digest_len; i++) {
        printf("%02x", digest[i]);
    }
    printf("\n");
    return 0;
}
