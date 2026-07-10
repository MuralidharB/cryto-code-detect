#include <stdio.h>
#include <stdint.h>
#include <stddef.h>

uint16_t fletcher16(const uint8_t *data, size_t len) {
    uint16_t sum1 = 0, sum2 = 0;
    for (size_t i = 0; i < len; i++) {
        sum1 = (sum1 + data[i]) % 255;
        sum2 = (sum2 + sum1) % 255;
    }
    return (uint16_t)((sum2 << 8) | sum1);
}

int main(void) {
    const char *msg = "abcde";
    printf("Fletcher-16 = 0x%04X\n",
           fletcher16((const uint8_t *)msg, 5));
    return 0;
}
