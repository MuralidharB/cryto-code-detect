BLOCK = 16


def _dbl(x):
    x <<= 1
    if x & 0x100:
        x ^= 0x11B
    return x & 0xFF


def _mul(a, b):
    r = 0
    for _ in range(8):
        if b & 1:
            r ^= a
        b >>= 1
        a = _dbl(a)
    return r


def mix(state):
    out = bytearray(BLOCK)
    for c in range(0, BLOCK, 4):
        a0, a1, a2, a3 = state[c], state[c + 1], state[c + 2], state[c + 3]
        out[c] = _mul(a0, 2) ^ _mul(a1, 3) ^ a2 ^ a3
        out[c + 1] = a0 ^ _mul(a1, 2) ^ _mul(a2, 3) ^ a3
        out[c + 2] = a0 ^ a1 ^ _mul(a2, 2) ^ _mul(a3, 3)
        out[c + 3] = _mul(a0, 3) ^ a1 ^ a2 ^ _mul(a3, 2)
    return bytes(out)


def unmix(state):
    out = bytearray(BLOCK)
    for c in range(0, BLOCK, 4):
        a0, a1, a2, a3 = state[c], state[c + 1], state[c + 2], state[c + 3]
        out[c] = _mul(a0, 14) ^ _mul(a1, 11) ^ _mul(a2, 13) ^ _mul(a3, 9)
        out[c + 1] = _mul(a0, 9) ^ _mul(a1, 14) ^ _mul(a2, 11) ^ _mul(a3, 13)
        out[c + 2] = _mul(a0, 13) ^ _mul(a1, 9) ^ _mul(a2, 14) ^ _mul(a3, 11)
        out[c + 3] = _mul(a0, 11) ^ _mul(a1, 13) ^ _mul(a2, 9) ^ _mul(a3, 14)
    return bytes(out)
