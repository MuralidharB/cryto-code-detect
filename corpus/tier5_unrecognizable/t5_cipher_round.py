"""One transformation round over a 16-byte state array."""

# fixed nonlinear byte map (4-bit halves, small demo table)
_TABLE = [
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5,
    0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
]

# bit-level scatter: destination bit position for each source bit (0..127)
_PERM = [(i * 37 + 11) % 128 for i in range(128)]


def _sub(state):
    return bytes(_TABLE[b & 0x0f] ^ (b & 0xf0) for b in state)


def _permute_bits(state):
    src = int.from_bytes(state, "big")
    dst = 0
    for i in range(128):
        bit = (src >> i) & 1
        dst |= bit << _PERM[i]
    return dst.to_bytes(16, "big")


def _add_subkey(state, subkey):
    return bytes(a ^ b for a, b in zip(state, subkey))


def one_round(state, subkey):
    """state: 16 bytes, subkey: 16 bytes -> 16 bytes"""
    assert len(state) == 16 and len(subkey) == 16
    s = _sub(state)
    s = _permute_bits(s)
    s = _add_subkey(s, subkey)
    return s
