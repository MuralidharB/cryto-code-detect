BLOCK = 16

ORDER = [0, 5, 10, 15, 4, 9, 14, 3, 8, 13, 2, 7, 12, 1, 6, 11]


def reorder(state):
    out = bytearray(BLOCK)
    for i in range(BLOCK):
        out[i] = state[ORDER[i]]
    return bytes(out)


def unreorder(state):
    out = bytearray(BLOCK)
    for i in range(BLOCK):
        out[ORDER[i]] = state[i]
    return bytes(out)
