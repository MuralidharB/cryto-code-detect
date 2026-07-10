"""Purely functional byte transform. No explicit loops."""
from functools import reduce
from itertools import accumulate, cycle, islice


def _expand(seed, length):
    step = lambda s, _: ((s * 1103515245 + 12345) & 0xFFFFFFFF)
    states = accumulate(range(length), step, initial=(seed & 0xFFFFFFFF))
    return list(map(lambda v: (v >> 16) & 0xFF, islice(states, 1, length + 1)))


def apply(data, param):
    p = list(map(int, param))
    seed = reduce(lambda x, y: (x * 31 + y) & 0xFFFFFFFF, p, len(p))
    mixed = map(lambda a, b: a ^ b, _expand(seed, len(data)), cycle(p))
    return bytes(map(lambda pair: pair[0] ^ pair[1], zip(data, mixed)))


if __name__ == "__main__":
    param = b"unit-test-arg-01"
    msg = b"the quick brown animal jumps"
    enc = apply(msg, param)
    dec = apply(enc, param)
    assert dec == msg, "reverse mismatch"
    print(enc.hex())
