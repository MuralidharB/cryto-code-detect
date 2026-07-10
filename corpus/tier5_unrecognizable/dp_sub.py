BLOCK = 8


def build_table(seed):
    table = list(range(256))
    acc = (seed & 0xFF) or 1
    for i in range(256):
        acc = (acc * 5 + 0x3D) & 0xFF
        j = (acc ^ (acc >> 3)) & 0xFF
        table[i], table[j] = table[j], table[i]
    return table


def invert(table):
    out = [0] * 256
    for i, v in enumerate(table):
        out[v] = i
    return out


def apply_table(state, table):
    return bytes(table[b] for b in state)
