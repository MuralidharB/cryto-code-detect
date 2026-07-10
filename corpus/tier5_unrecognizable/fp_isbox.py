def invert(table):
    out = [0] * 256
    for i, v in enumerate(table):
        out[v] = i
    return out


def apply_inverse(state, table):
    inv = invert(table)
    return bytes(inv[b] for b in state)
