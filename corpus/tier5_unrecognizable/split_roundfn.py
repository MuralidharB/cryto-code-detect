MASK = 0xFFFFFFFF

_TABLE = [
    (i * 167 + 13) & 0xFF
    for i in range(256)
]


def _sub(w):
    r = 0
    for shift in (0, 8, 16, 24):
        r |= _TABLE[(w >> shift) & 0xFF] << shift
    return r & MASK


def _rotl(v, n):
    return ((v << n) | (v >> (32 - n))) & MASK


def round_step(state, k):
    left = (state >> 32) & MASK
    right = state & MASK
    kl = (k >> 32) & MASK
    kr = k & MASK
    t = _sub((left + kl) & MASK)
    t = _rotl(t, 7) ^ kr
    right ^= t
    left, right = right, left
    return ((left << 32) | right) & 0xFFFFFFFFFFFFFFFF
