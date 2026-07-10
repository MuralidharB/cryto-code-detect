/* Fill a salt buffer using the C standard library pseudo-random generator. */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void fill_salt(unsigned char *salt, int length, unsigned int seed) {
    srand(seed);
    for (int i = 0; i < length; i++) {
        salt[i] = (unsigned char)(rand() & 0xFF);
    }
}

int main(void) {
    unsigned char salt[16];
    fill_salt(salt, sizeof(salt), (unsigned int)time(NULL));
    for (int i = 0; i < (int)sizeof(salt); i++) {
        printf("%02x", salt[i]);
    }
    printf("\n");
    return 0;
}
