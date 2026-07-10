def _seed(key):
    h = 0x2545F4914F6CDD1D
    for b in key:
        h ^= b
        h = (h * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    x = ((h & 0xFFFFFFFF) / 0x100000000) * 0.98 + 0.01
    mu = 1.90 + ((h >> 40) & 0xFF) / 256.0 * 0.099
    return x, mu


def _seq(key, n):
    x, mu = _seed(key)
    out = bytearray()
    while len(out) < n:
        for _ in range(4):
            if x < 0.5:
                x = mu * x
            else:
                x = mu * (1.0 - x)
            x = 3.999 * x * (1.0 - x)
            if x <= 0.0 or x >= 1.0:
                x = 0.5
        out.append(int(x * 256) & 0xFF)
    return bytes(out[:n])


def apply(data, key):
    ks = _seq(key, len(data))
    return bytes(a ^ b for a, b in zip(data, ks))


if __name__ == "__main__":
    k = b"chaos-seed-9"
    m = b"iterated map driven mask over data"
    c = apply(m, k)
    assert apply(c, k) == m
