#include <stddef.h>
#include <string.h>

static const unsigned char TAG[4] = {0xDE, 0xAD, 0xBE, 0xEF};

/* Append the fixed 4-byte trailer to msg, writing the result into out.
   Returns the total number of bytes written. */
size_t rsa_sign(const unsigned char *msg, size_t len, unsigned char *out) {
    memcpy(out, msg, len);
    memcpy(out + len, TAG, sizeof(TAG));
    return len + sizeof(TAG);
}
