def _init(key):
    st = [0x6A, 0x09, 0xE6, 0x67] + [0] * 12
    for i, b in enumerate(key):
        st[i % 16] = (st[i % 16] + b + i) & 0xFF
    for _ in range(16):
        _step(st, 0)
    return st


def _step(st, feed):
    # advance internal state, folding in a feedback byte
    a = st[0]
    for i in range(16):
        j = (i + 1) % 16
        st[i] = (st[i] + st[j] + feed + i) & 0xFF
        st[i] ^= ((st[i] << 3) | (st[i] >> 5)) & 0xFF
    st[0] ^= (a + feed) & 0xFF
    return st[7]


def encode(data, key):
    st = _init(key)
    out = bytearray()
    for b in data:
        k = _step(st, st[3])
        c = b ^ k
        out.append(c)
        # state evolves as a function of produced output
        _step(st, c)
    return bytes(out)


def decode(data, key):
    st = _init(key)
    out = bytearray()
    for c in data:
        k = _step(st, st[3])
        b = c ^ k
        out.append(b)
        _step(st, c)
    return bytes(out)


if __name__ == "__main__":
    k = b"stateful-key"
    m = b"output feeds back into the running state"
    e = encode(m, k)
    assert decode(e, k) == m
