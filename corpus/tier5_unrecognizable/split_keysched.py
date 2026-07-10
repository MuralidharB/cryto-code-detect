MASK = 0xFFFFFFFF
ROUNDS = 16


def _rotl(v, n):
    return ((v << n) | (v >> (32 - n))) & MASK


def subkeys(master):
    a = master & MASK
    b = (master >> 32) & MASK
    out = []
    delta = 0x9E3779B9
    acc = 0
    for i in range(ROUNDS):
        acc = (acc + delta) & MASK
        a = _rotl((a + acc) & MASK, 5) ^ b
        b = _rotl((b ^ acc) & MASK, 11) ^ a
        out.append(((a << 32) | b) & 0xFFFFFFFFFFFFFFFF)
    return out
