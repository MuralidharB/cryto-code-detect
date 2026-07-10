MASK = 0xFFFFFFFF
DELTA = 0x9E3779B9

def _block_encrypt(v0, v1, key):
    s = 0
    k0, k1, k2, k3 = key
    for _ in range(16):
        s = (s + DELTA) & MASK
        v0 = (v0 + (((v1 << 4) + k0) ^ (v1 + s) ^ ((v1 >> 5) + k1))) & MASK
        v1 = (v1 + (((v0 << 4) + k2) ^ (v0 + s) ^ ((v0 >> 5) + k3))) & MASK
    return v0, v1

def cbc_mac(key, blocks):
    c0, c1 = 0, 0
    for b0, b1 in blocks:
        c0, c1 = _block_encrypt(c0 ^ b0, c1 ^ b1, key)
    return (c0 << 32) | c1

if __name__ == "__main__":
    key = (0x11111111, 0x22222222, 0x33333333, 0x44444444)
    msg = [(0xAAAAAAAA, 0xBBBBBBBB), (0xCCCCCCCC, 0xDDDDDDDD), (0x01010101, 0x02020202)]
    tag = cbc_mac(key, msg)
    print("tag:", hex(tag))
