"""Perceptual difference-hash for near-duplicate image detection.

The image is reduced to a tiny grayscale grid; each output bit records
whether a pixel is brighter than its right neighbour. Similar images
produce fingerprints with small Hamming distance.
"""


def _downscale(matrix, w, h):
    rows = len(matrix)
    cols = len(matrix[0])
    out = []
    for r in range(h):
        line = []
        for c in range(w):
            sr = r * rows // h
            sc = c * cols // w
            line.append(matrix[sr][sc])
        out.append(line)
    return out


def dhash(matrix, side=8):
    small = _downscale(matrix, side + 1, side)
    bits = 0
    n = 0
    for r in range(side):
        for c in range(side):
            bits <<= 1
            if small[r][c] > small[r][c + 1]:
                bits |= 1
            n += 1
    return bits


def hamming(a, b):
    return bin(a ^ b).count("1")
