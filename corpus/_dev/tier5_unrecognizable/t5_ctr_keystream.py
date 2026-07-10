"""Generate a masking stream from an incrementing counter and fold it into data."""


def _incr(counter):
    v = int.from_bytes(counter, "big") + 1
    return (v & ((1 << (len(counter) * 8)) - 1)).to_bytes(len(counter), "big")


def _stream(nonce, nblocks, block):
    """block: callable(16 bytes)->16 bytes. Produces nblocks*16 bytes."""
    ctr = bytes(nonce)
    out = bytearray()
    for _ in range(nblocks):
        out.extend(block(ctr))
        ctr = _incr(ctr)
    return bytes(out)


def apply(data, nonce, block):
    n = (len(data) + 15) // 16
    mask = _stream(nonce, n, block)
    return bytes(a ^ b for a, b in zip(data, mask))
