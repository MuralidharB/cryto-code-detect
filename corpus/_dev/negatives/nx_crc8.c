#include <stdio.h>
#include <stdint.h>
#include <stddef.h>

#define CRC8_POLY 0x07

uint8_t crc8(const uint8_t *data, size_t len) {
    uint8_t crc = 0x00;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (int b = 0; b < 8; b++) {
            if (crc & 0x80)
                crc = (uint8_t)((crc << 1) ^ CRC8_POLY);
            else
                crc <<= 1;
        }
    }
    return crc;
}

int main(void) {
    uint8_t frame[] = {0x01, 0x02, 0x03, 0x04};
    printf("CRC-8 = 0x%02X\n", crc8(frame, sizeof(frame)));
    return 0;
}
