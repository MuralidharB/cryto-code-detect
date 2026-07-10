from split_keysched import subkeys, ROUNDS
from split_roundfn import round_step

BLOCK = 8


def _to_int(chunk):
    v = 0
    for byte in chunk:
        v = (v << 8) | byte
    return v


def _to_bytes(v):
    return bytes((v >> (8 * i)) & 0xFF for i in range(BLOCK - 1, -1, -1))


def _transform(value, ks):
    for k in ks:
        value = round_step(value, k)
    return value


def process(data, master, seed):
    ks = subkeys(master)
    prev = seed & 0xFFFFFFFFFFFFFFFF
    out = bytearray()
    for off in range(0, len(data), BLOCK):
        chunk = data[off:off + BLOCK].ljust(BLOCK, b"\x00")
        cur = _to_int(chunk) ^ prev
        cur = _transform(cur, ks)
        out.extend(_to_bytes(cur))
        prev = cur
    return bytes(out)
