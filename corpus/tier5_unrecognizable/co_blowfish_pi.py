import struct

_MASK = 0xFFFFFFFF


def _frac_words(nwords):
    # Digit-extraction of the fractional hex expansion of a well-known
    # circle-related constant via the Bailey-Borwein-Plouffe series.
    words = []
    # Compute hex digits 8 at a time using the digit-extraction formula.
    def _s(j, d):
        # sum_{k=0}^{d} 16^(d-k) mod (8k+j) / (8k+j)  +  tail
        total = 0.0
        for k in range(d + 1):
            denom = 8 * k + j
            total += pow(16, d - k, denom) / denom
            total = total - int(total)
        p = 1.0 / 16.0
        k = d + 1
        while True:
            term = p / (8 * k + j)
            if term < 1e-17:
                break
            total += term
            p /= 16.0
            k += 1
        return total - int(total)

    def _hexdigit(d):
        x = 4 * _s(1, d) - 2 * _s(4, d) - _s(5, d) - _s(6, d)
        x = x - int(x)
        if x < 0:
            x += 1.0
        return int(x * 16) & 0xF

    total_digits = nwords * 8
    digits = [_hexdigit(d) for d in range(total_digits)]
    for i in range(nwords):
        w = 0
        for j in range(8):
            w = (w << 4) | digits[i * 8 + j]
        words.append(w & _MASK)
    return words


class Transform:
    def __init__(self, key):
        seed = _frac_words(18 + 4 * 256)
        self.P = seed[:18]
        self.S = [seed[18 + i * 256:18 + (i + 1) * 256] for i in range(4)]
        klen = len(key)
        j = 0
        for i in range(18):
            k = 0
            for _ in range(4):
                k = ((k << 8) | key[j % klen]) & _MASK
                j += 1
            self.P[i] ^= k
        l = r = 0
        for i in range(0, 18, 2):
            l, r = self._round(l, r)
            self.P[i] = l
            self.P[i + 1] = r
        for box in range(4):
            for i in range(0, 256, 2):
                l, r = self._round(l, r)
                self.S[box][i] = l
                self.S[box][i + 1] = r

    def _f(self, x):
        a = (x >> 24) & 0xFF
        b = (x >> 16) & 0xFF
        c = (x >> 8) & 0xFF
        d = x & 0xFF
        y = (self.S[0][a] + self.S[1][b]) & _MASK
        y ^= self.S[2][c]
        y = (y + self.S[3][d]) & _MASK
        return y

    def _round(self, l, r):
        for i in range(16):
            l ^= self.P[i]
            r ^= self._f(l)
            l, r = r, l
        l, r = r, l
        r ^= self.P[16]
        l ^= self.P[17]
        return l & _MASK, r & _MASK

    def apply_block(self, block8):
        l, r = struct.unpack(">II", block8)
        l, r = self._round(l, r)
        return struct.pack(">II", l, r)


if __name__ == "__main__":
    c = Transform(b"TESTKEY")
    print(c.apply_block(b"12345678").hex())
