import dp_sub
import dp_key
import dp_perm

BLOCK = 8
ROUNDS = 4


def _xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def transform_block(block, master):
    table = dp_sub.build_table(master[0] if master else 1)
    subkeys = dp_key.expand(master)
    state = _xor(block, subkeys[0])
    for r in range(1, ROUNDS + 1):
        state = dp_sub.apply_table(state, table)
        state = dp_perm.permute(state)
        state = _xor(state, subkeys[r])
    return state


def run(data, master):
    out = bytearray()
    prev = bytes(BLOCK)
    for off in range(0, len(data), BLOCK):
        chunk = bytes(data[off:off + BLOCK]).ljust(BLOCK, b"\x00")
        chunk = _xor(chunk, prev)
        prev = transform_block(chunk, master)
        out += prev
    return bytes(out)
