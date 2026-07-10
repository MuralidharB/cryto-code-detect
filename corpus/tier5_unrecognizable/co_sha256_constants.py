import struct


def _first_primes(n):
    out = []
    c = 2
    while len(out) < n:
        p = True
        for d in range(2, int(c ** 0.5) + 1):
            if c % d == 0:
                p = False
                break
        if p:
            out.append(c)
        c += 1
    return out


def _frac_cube_roots(primes):
    vals = []
    for p in primes:
        r = p ** (1.0 / 3.0)
        frac = r - int(r)
        vals.append(int(frac * (1 << 32)) & 0xFFFFFFFF)
    return vals


def _frac_square_roots(primes):
    vals = []
    for p in primes:
        r = p ** 0.5
        frac = r - int(r)
        vals.append(int(frac * (1 << 32)) & 0xFFFFFFFF)
    return vals


_PRIMES = _first_primes(64)
_K = _frac_cube_roots(_PRIMES)
_H0 = _frac_square_roots(_PRIMES[:8])

_MASK = 0xFFFFFFFF


def _rotr(x, n):
    return ((x >> n) | (x << (32 - n))) & _MASK


def _pad(data):
    ml = len(data) * 8
    data = data + b"\x80"
    while len(data) % 64 != 56:
        data += b"\x00"
    data += struct.pack(">Q", ml)
    return data


def digest(message):
    if isinstance(message, str):
        message = message.encode()
    h = list(_H0)
    data = _pad(message)
    for off in range(0, len(data), 64):
        block = data[off:off + 64]
        w = list(struct.unpack(">16I", block))
        for i in range(16, 64):
            s0 = _rotr(w[i - 15], 7) ^ _rotr(w[i - 15], 18) ^ (w[i - 15] >> 3)
            s1 = _rotr(w[i - 2], 17) ^ _rotr(w[i - 2], 19) ^ (w[i - 2] >> 10)
            w.append((w[i - 16] + s0 + w[i - 7] + s1) & _MASK)
        a, b, c, d, e, f, g, hh = h
        for i in range(64):
            S1 = _rotr(e, 6) ^ _rotr(e, 11) ^ _rotr(e, 25)
            ch = (e & f) ^ ((~e & _MASK) & g)
            t1 = (hh + S1 + ch + _K[i] + w[i]) & _MASK
            S0 = _rotr(a, 2) ^ _rotr(a, 13) ^ _rotr(a, 22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            t2 = (S0 + maj) & _MASK
            hh = g
            g = f
            f = e
            e = (d + t1) & _MASK
            d = c
            c = b
            b = a
            a = (t1 + t2) & _MASK
        h = [(x + y) & _MASK for x, y in zip(h, [a, b, c, d, e, f, g, hh])]
    return b"".join(struct.pack(">I", x) for x in h)


def hexdigest(message):
    return digest(message).hex()


if __name__ == "__main__":
    print(hexdigest(b"abc"))
