MASK = 0xFFFFFFFF
DELTA = 0x9E3779B9

def encrypt_block(v0, v1, key):
    s = 0
    k0, k1, k2, k3 = key
    for _ in range(32):
        s = (s + DELTA) & MASK
        v0 = (v0 + (((v1 << 4) + k0) ^ (v1 + s) ^ ((v1 >> 5) + k1))) & MASK
        v1 = (v1 + (((v0 << 4) + k2) ^ (v0 + s) ^ ((v0 >> 5) + k3))) & MASK
    return v0, v1

def decrypt_block(v0, v1, key):
    k0, k1, k2, k3 = key
    s = (DELTA * 32) & MASK
    for _ in range(32):
        v1 = (v1 - (((v0 << 4) + k2) ^ (v0 + s) ^ ((v0 >> 5) + k3))) & MASK
        v0 = (v0 - (((v1 << 4) + k0) ^ (v1 + s) ^ ((v1 >> 5) + k1))) & MASK
        s = (s - DELTA) & MASK
    return v0, v1

if __name__ == "__main__":
    key = (0x01234567, 0x89ABCDEF, 0xFEDCBA98, 0x76543210)
    pt = (0xDEADBEEF, 0x0BADF00D)
    ct = encrypt_block(pt[0], pt[1], key)
    rt = decrypt_block(ct[0], ct[1], key)
    print("plain  :", [hex(x) for x in pt])
    print("blk :", [hex(x) for x in ct])
    print("blk:", [hex(x) for x in rt])
    assert rt == pt
