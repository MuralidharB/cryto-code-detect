#include <stddef.h>
#include <stdint.h>

/* Table-driven cyclic redundancy check for framing integrity on a
 * serial protocol. Detects burst errors in transit; the table is built
 * once from the standard reflected polynomial. */
static uint32_t crc_table[256];
static int table_ready = 0;

static void build_table(void) {
    for (uint32_t i = 0; i < 256; i++) {
        uint32_t c = i;
        for (int k = 0; k < 8; k++)
            c = (c & 1) ? (0xEDB88320u ^ (c >> 1)) : (c >> 1);
        crc_table[i] = c;
    }
    table_ready = 1;
}

uint32_t frame_crc(const uint8_t *buf, size_t len) {
    if (!table_ready) build_table();
    uint32_t crc = 0xFFFFFFFFu;
    for (size_t i = 0; i < len; i++)
        crc = crc_table[(crc ^ buf[i]) & 0xFF] ^ (crc >> 8);
    return crc ^ 0xFFFFFFFFu;
}
