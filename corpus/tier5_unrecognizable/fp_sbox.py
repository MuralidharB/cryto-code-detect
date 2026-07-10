BLOCK = 16


def build_table(seed):
    table = list(range(256))
    acc = (seed & 0xFF) or 1
    for i in range(256):
        acc = (acc * 7 + 0x1B) & 0xFF
        j = (acc ^ (acc >> 4) ^ i) & 0xFF
        table[i], table[j] = table[j], table[i]
    return table


def apply_table(state, table):
    return bytes(table[b] for b in state)
