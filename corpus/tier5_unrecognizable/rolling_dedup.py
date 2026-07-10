# Rolling window fingerprint for content-defined chunking in a backup deduplicator:
# splits byte streams into stable chunks at reproducible boundaries.
BASE, MOD = 257, (1 << 61) - 1

def chunk_boundaries(data, window=48, mask=0x1FFF):
    h, boundaries = 0, []
    for i, b in enumerate(data):
        h = (h * BASE + b) % MOD
        if i >= window and (h & mask) == 0:
            boundaries.append(i)
    return boundaries
