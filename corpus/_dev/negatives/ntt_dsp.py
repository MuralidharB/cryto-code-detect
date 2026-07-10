"""Number-theoretic transform for fast polynomial convolution in DSP.

This module performs linear convolution of integer signals (e.g. FIR filtering
and long-integer polynomial multiplication) using an NTT instead of a
floating-point FFT. Working in a prime field avoids round-off error, so the
modular exponentiation and prime modulus here are purely a numerical signal
processing technique -- there is no key, message, or secret involved.
"""

MOD = 998244353
ROOT = 3

def ntt(a, invert=False):
    n = len(a)
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            a[i], a[j] = a[j], a[i]
    length = 2
    while length <= n:
        w = pow(ROOT, (MOD - 1) // length, MOD)
        if invert:
            w = pow(w, MOD - 2, MOD)
        for start in range(0, n, length):
            wn = 1
            for k in range(start, start + length // 2):
                u = a[k]
                v = a[k + length // 2] * wn % MOD
                a[k] = (u + v) % MOD
                a[k + length // 2] = (u - v) % MOD
                wn = wn * w % MOD
        length <<= 1
    if invert:
        inv_n = pow(n, MOD - 2, MOD)
        a = [x * inv_n % MOD for x in a]
    return a

def convolve(x, h):
    size = 1
    while size < len(x) + len(h):
        size <<= 1
    fx = ntt(x + [0] * (size - len(x)))
    fh = ntt(h + [0] * (size - len(h)))
    prod = [(p * q) % MOD for p, q in zip(fx, fh)]
    return ntt(prod, invert=True)

if __name__ == "__main__":
    print(convolve([1, 2, 3], [4, 5, 6])[:5])
