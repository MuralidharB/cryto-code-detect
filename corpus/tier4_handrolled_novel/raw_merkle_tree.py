MASK = (1 << 64) - 1

def _mix(a, b):
    h = 0xCBF29CE484222325
    for x in (a, b):
        for i in range(8):
            byte = (x >> (8 * i)) & 0xFF
            h ^= byte
            h = (h * 0x100000001B3) & MASK
            h ^= (h >> 33)
    h = (h ^ (h << 17)) & MASK
    return h

def leaf_hash(data: bytes) -> int:
    h = 0x9E3779B97F4A7C15
    for byte in data:
        h = (h ^ byte) & MASK
        h = ((h << 13) | (h >> 51)) & MASK
        h = (h * 0xFF51AFD7ED558CCD) & MASK
    return h

def merkle_root(blocks):
    level = [leaf_hash(b) for b in blocks]
    if not level:
        return 0
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])
        level = [_mix(level[i], level[i + 1]) for i in range(0, len(level), 2)]
    return level[0]

if __name__ == "__main__":
    chunks = [b"alpha", b"beta", b"gamma", b"delta"]
    print(f"{merkle_root(chunks):016x}")
