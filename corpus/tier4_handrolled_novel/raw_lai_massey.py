MASK = 0xFFFFFFFF
ROUNDS = 8

def _round_fn(x, rk):
    x = (x + rk) & MASK
    x ^= (x << 7) & MASK
    x = (x + ((x >> 3) | (x << 29))) & MASK
    return x & MASK

def _orthomorphism(x):
    
    return (((x << 1) | (x >> 31)) ^ x) & MASK

def encrypt_block(l, r, subkeys):
    for rk in subkeys:
        d = (l - r) & MASK
        t = _round_fn(d, rk)
        l = _orthomorphism((l + t) & MASK)
        r = (r + t) & MASK
    return l, r

if __name__ == "__main__":
    subkeys = [(0x1000 * (i + 1)) & MASK for i in range(ROUNDS)]
    l, r = 0xCAFEBABE, 0xDEADBEEF
    ct = encrypt_block(l, r, subkeys)
    print("blk:", [hex(x) for x in ct])
