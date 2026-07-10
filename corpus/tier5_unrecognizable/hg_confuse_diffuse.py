def _subkeys(key):
    tab = list(range(256))
    j = 0
    for r in range(2):
        for i in range(256):
            j = (j + tab[i] + key[i % len(key)]) & 0xFF
            tab[i], tab[j] = tab[j], tab[i]
    inv = [0] * 256
    for i, v in enumerate(tab):
        inv[v] = i
    rots = [(key[i % len(key)] ^ (i * 7 + 1)) & 7 for i in range(16)]
    return tab, inv, rots


def _rotl(b, n):
    return ((b << n) | (b >> (8 - n))) & 0xFF


def _rotr(b, n):
    return ((b >> n) | (b << (8 - n))) & 0xFF


def forward(data, key):
    tab, _inv, rots = _subkeys(key)
    out = bytearray(data)
    prev = 0xA5
    for i in range(len(out)):
        v = tab[out[i]]
        v = _rotl(v, rots[i % 16])
        v ^= prev
        out[i] = v
        prev = (v + i) & 0xFF
    return bytes(out)


def backward(data, key):
    _tab, inv, rots = _subkeys(key)
    out = bytearray(data)
    prev = 0xA5
    for i in range(len(out)):
        cur = out[i]
        v = cur ^ prev
        v = _rotr(v, rots[i % 16])
        out[i] = inv[v]
        prev = (cur + i) & 0xFF
    return bytes(out)


if __name__ == "__main__":
    k = b"toy-key-material"
    m = b"the quick brown fox jumps"
    c = forward(m, k)
    assert backward(c, k) == m
