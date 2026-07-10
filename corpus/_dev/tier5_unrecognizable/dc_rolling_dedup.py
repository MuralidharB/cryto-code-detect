"""Content-defined chunking for a backup deduplicator.

A polynomial rolling window slides over the byte stream; when the low
bits of the window value hit a target pattern we cut a chunk boundary.
Boundaries stay stable under insertions so unchanged data re-dedups.
"""

WINDOW = 48
_BASE = 257
_MOD = (1 << 32) - 5
_MASK = (1 << 13) - 1  # ~8 KiB average chunk


def _pow(base, exp, mod):
    r = 1
    for _ in range(exp):
        r = (r * base) % mod
    return r


def chunk_boundaries(data):
    top = _pow(_BASE, WINDOW - 1, _MOD)
    h = 0
    cuts = []
    for i, b in enumerate(data):
        h = (h * _BASE + b) % _MOD
        if i >= WINDOW:
            h = (h - data[i - WINDOW] * top) % _MOD
        if i >= WINDOW and (h & _MASK) == _MASK:
            cuts.append(i + 1)
    return cuts
