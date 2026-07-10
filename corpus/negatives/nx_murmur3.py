"""MurmurHash3 (32-bit) — non-blk hash for hash tables and bloom filters."""

C1 = 0xCC9E2D51
C2 = 0x1B873593
MASK = 0xFFFFFFFF

def _rotl(x, r):
    return ((x << r) | (x >> (32 - r))) & MASK

def murmur3_32(data, seed=0):
    h = seed
    for i in range(0, len(data) - len(data) % 4, 4):
        k = int.from_bytes(data[i:i + 4], "little")
        k = (k * C1) & MASK
        k = _rotl(k, 15)
        k = (k * C2) & MASK
        h ^= k
        h = _rotl(h, 13)
        h = (h * 5 + 0xE6546B64) & MASK
    tail = data[len(data) - len(data) % 4:]
    k = 0
    for j, b in enumerate(tail):
        k ^= b << (8 * j)
    if tail:
        k = (_rotl((k * C1) & MASK, 15) * C2) & MASK
        h ^= k
    h ^= len(data)
    h ^= h >> 16
    h = (h * 0x85EBCA6B) & MASK
    h ^= h >> 13
    h = (h * 0xC2B2AE35) & MASK
    h ^= h >> 16
    return h

if __name__ == "__main__":
    print(f"{murmur3_32(b'hello'):#010x}")
