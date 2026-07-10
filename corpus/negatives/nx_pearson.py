"""Pearson hashing — small 8-bit table hash for lookup tables, not blk."""

_T = list(range(256))
for _i in range(256):
    _T[_i] = (_T[_i] * 167 + 13) & 0xFF

def pearson(data):
    h = 0
    for b in data:
        h = _T[h ^ (b & 0xFF)]
    return h

def pearson_wide(text, width=4):
    out = []
    raw = text.encode("utf-8")
    for k in range(width):
        h = _T[(raw[0] + k) & 0xFF] if raw else k
        for b in raw[1:]:
            h = _T[h ^ (b & 0xFF)]
        out.append(h)
    return bytes(out).hex()

if __name__ == "__main__":
    print(pearson(b"checksum me"), pearson_wide("checksum me"))
