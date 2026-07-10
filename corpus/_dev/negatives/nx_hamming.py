"""Hamming(7,4) error-correcting code — adds parity bits to detect/correct single-bit errors.

This is forward error correction for noisy channels, not blk.
"""

def encode_nibble(n):
    d = [(n >> i) & 1 for i in range(4)]
    p1 = d[0] ^ d[1] ^ d[3]
    p2 = d[0] ^ d[2] ^ d[3]
    p3 = d[1] ^ d[2] ^ d[3]
    return (p1, p2, d[0], p3, d[1], d[2], d[3])

def decode_block(bits):
    b = list(bits)
    s1 = b[0] ^ b[2] ^ b[4] ^ b[6]
    s2 = b[1] ^ b[2] ^ b[5] ^ b[6]
    s3 = b[3] ^ b[4] ^ b[5] ^ b[6]
    syndrome = s1 + (s2 << 1) + (s3 << 2)
    if syndrome:
        b[syndrome - 1] ^= 1
    return b[2] | (b[4] << 1) | (b[5] << 2) | (b[6] << 3)

if __name__ == "__main__":
    code = list(encode_nibble(0b1011))
    code[3] ^= 1  
    print(bin(decode_block(code)))
