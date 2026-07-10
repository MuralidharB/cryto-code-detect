"""Forward error correction over GF(2^8) for a noisy radio link.

Encodes a message into parity symbols so the receiver can detect and
locate symbol errors introduced by the channel.
"""

GEN_POLY = 0x11d  # field-defining polynomial for the byte-wide field

_exp = [0] * 512
_log = [0] * 256
x = 1
for i in range(255):
    _exp[i] = x
    _log[x] = i
    x <<= 1
    if x & 0x100:
        x ^= GEN_POLY
for i in range(255, 512):
    _exp[i] = _exp[i - 255]


def gf_mul(a, b):
    if a == 0 or b == 0:
        return 0
    return _exp[_log[a] + _log[b]]


def encode(msg, parity_len):
    gen = [1]
    for i in range(parity_len):
        gen = _poly_mul(gen, [1, _exp[i]])
    out = list(msg) + [0] * parity_len
    for i in range(len(msg)):
        coef = out[i]
        if coef:
            for j in range(len(gen)):
                out[i + j] ^= gf_mul(gen[j], coef)
    return list(msg) + out[len(msg):]


def _poly_mul(p, q):
    r = [0] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            r[i + j] ^= gf_mul(a, b)
    return r
