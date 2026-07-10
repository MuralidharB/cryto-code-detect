#include <stdio.h>
#include <stdint.h>

uint32_t djb2(const char *str) {
    uint32_t hash = 5381;
    int c;
    while ((c = (unsigned char)*str++)) {
        hash = ((hash << 5) + hash) + c; 
    }
    return hash;
}

int main(void) {
    const char *keys[] = {"alpha", "beta", "gamma"};
    for (int i = 0; i < 3; i++) {
        printf("%-6s -> %u\n", keys[i], djb2(keys[i]));
    }
    return 0;
}
