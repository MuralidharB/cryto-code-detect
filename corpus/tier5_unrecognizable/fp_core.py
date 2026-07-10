import fp_sbox
import fp_isbox
import fp_perm
import fp_mix

BLOCK = 16
ROUNDS = 6


def _xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def _expand(master):
    data = bytearray(master) or bytearray(b"\x01")
    words = bytearray()
    while len(words) < BLOCK * (ROUNDS + 1):
        for i in range(len(data)):
            data[i] = (data[i] + data[(i + 1) % len(data)] + len(words) + 1) & 0xFF
            data[i] = ((data[i] << 1) | (data[i] >> 7)) & 0xFF
        words += data
    return [bytes(words[r * BLOCK:(r + 1) * BLOCK]) for r in range(ROUNDS + 1)]


def transform_block(block, master):
    table = fp_sbox.build_table(master[0] if master else 1)
    subkeys = _expand(master)
    state = _xor(block, subkeys[0])
    for r in range(1, ROUNDS + 1):
        state = fp_sbox.apply_table(state, table)
        state = fp_perm.reorder(state)
        state = fp_mix.mix(state)
        state = _xor(state, subkeys[r])
    return state


def inverse_block(block, master):
    table = fp_sbox.build_table(master[0] if master else 1)
    subkeys = _expand(master)
    state = bytes(block)
    for r in range(ROUNDS, 0, -1):
        state = _xor(state, subkeys[r])
        state = fp_mix.unmix(state)
        state = fp_perm.unreorder(state)
        state = fp_isbox.apply_inverse(state, table)
    return _xor(state, subkeys[0])


def run(data, master):
    out = bytearray()
    prev = bytes(BLOCK)
    for off in range(0, len(data), BLOCK):
        chunk = bytes(data[off:off + BLOCK]).ljust(BLOCK, b"\x00")
        chunk = _xor(chunk, prev)
        prev = transform_block(chunk, master)
        out += prev
    return bytes(out)
