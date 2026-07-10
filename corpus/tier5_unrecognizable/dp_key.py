BLOCK = 8
ROUNDS = 4


def expand(master):
    data = bytearray(master)
    while len(data) < BLOCK:
        data.append(len(data) & 0xFF)
    words = list(data[:BLOCK])
    subkeys = []
    rc = 1
    for r in range(ROUNDS + 1):
        for i in range(BLOCK):
            words[i] = (words[i] + words[(i + 1) % BLOCK] + rc) & 0xFF
            words[i] = ((words[i] << 1) | (words[i] >> 7)) & 0xFF
        subkeys.append(bytes(words))
        rc = (rc * 3 + 1) & 0xFF
    return subkeys
