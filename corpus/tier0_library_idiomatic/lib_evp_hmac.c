#include <stdio.h>
#include <string.h>
#include <openssl/hmac.h>
#include <openssl/evp.h>

int main(void) {
    const unsigned char key[] = "api-signing-key";
    const char *msg = "GET /v1/accounts";
    unsigned char mac[EVP_MAX_MD_SIZE];
    unsigned int mac_len = 0;

    if (HMAC(EVP_sha256(), key, (int)(sizeof(key) - 1),
             (const unsigned char *)msg, strlen(msg), mac, &mac_len) == NULL) {
        fprintf(stderr, "hmac failed\n");
        return 1;
    }

    for (unsigned int i = 0; i < mac_len; i++) {
        printf("%02x", mac[i]);
    }
    printf("\n");
    return 0;
}
