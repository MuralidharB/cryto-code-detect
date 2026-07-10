def _mix(state, label, tweak):
    s = bytearray(state)
    for i in range(len(s)):
        s[i] ^= label[i % len(label)]
    acc = 0x811C9DC5
    for r in range(3):
        for i in range(len(s)):
            acc = ((acc ^ s[i]) * 0x01000193) & 0xFFFFFFFF
            s[i] = (s[i] + ((acc >> (i % 24)) & 0xFF) + tweak) & 0xFF
            s[i] ^= ((s[i] << 3) | (s[i] >> 5)) & 0xFF
        s = s[-1:] + s[:-1]
    return bytes(s)


def derive(master, path):
    """path: iterable of 0/1 bits selecting left/right child."""
    node = _mix(master, b"root", 0)
    for depth, bit in enumerate(path):
        label = b"L" if bit == 0 else b"R"
        node = _mix(node, label, depth + 1)
    return node


def subkeys(master, count):
    keys = []
    n = 0
    bits_needed = max(1, (count - 1).bit_length())
    while len(keys) < count:
        path = [(n >> i) & 1 for i in range(bits_needed)]
        keys.append(derive(master, path))
        n += 1
    return keys


if __name__ == "__main__":
    m = b"master-secret-material-32-bytes!"
    ks = subkeys(m, 8)
    assert len(set(ks)) == 8
    assert derive(m, [0, 1, 1]) == derive(m, [0, 1, 1])
