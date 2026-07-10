MASK = 0xFFFFFFFF
DELTA = 0x9E3779B9
ROUNDS = 32

def encrypt_block(v0, v1, key):
    s = 0
    for _ in range(ROUNDS):
        v0 = (v0 + ((((v1 << 4) ^ (v1 >> 5)) + v1) ^ (s + key[s & 3]))) & MASK
        s = (s + DELTA) & MASK
        v1 = (v1 + ((((v0 << 4) ^ (v0 >> 5)) + v0) ^ (s + key[(s >> 11) & 3]))) & MASK
    return v0, v1

def decrypt_block(v0, v1, key):
    s = (DELTA * ROUNDS) & MASK
    for _ in range(ROUNDS):
        v1 = (v1 - ((((v0 << 4) ^ (v0 >> 5)) + v0) ^ (s + key[(s >> 11) & 3]))) & MASK
        s = (s - DELTA) & MASK
        v0 = (v0 - ((((v1 << 4) ^ (v1 >> 5)) + v1) ^ (s + key[s & 3]))) & MASK
    return v0, v1

if __name__ == "__main__":
    key = [0x01234567, 0x89ABCDEF, 0xFEDCBA98, 0x76543210]
    pt = (0x41424344, 0x45464748)
    ct = encrypt_block(pt[0], pt[1], key)
    rt = decrypt_block(ct[0], ct[1], key)
    print("blk :", [hex(x) for x in ct])
    assert rt == pt
