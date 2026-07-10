BLOCK = 8

ORDER = [2, 5, 0, 7, 4, 1, 6, 3]


def permute(state):
    out = bytearray(BLOCK)
    for i in range(BLOCK):
        out[i] = state[ORDER[i]]
    for i in range(BLOCK):
        out[i] ^= ((out[(i + 1) % BLOCK] << 3) | (out[(i + 1) % BLOCK] >> 5)) & 0xFF
    return bytes(out)


def unpermute(state):
    tmp = bytearray(state)
    for i in range(BLOCK - 1, -1, -1):
        tmp[i] ^= ((tmp[(i + 1) % BLOCK] << 3) | (tmp[(i + 1) % BLOCK] >> 5)) & 0xFF
    out = bytearray(BLOCK)
    for i in range(BLOCK):
        out[ORDER[i]] = tmp[i]
    return bytes(out)
