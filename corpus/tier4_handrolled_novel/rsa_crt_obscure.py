def _xgcd(aa, bb):
    o0, o1 = 1, 0
    r0, r1 = aa, bb
    while r1:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        o0, o1 = o1, o0 - q * o1
    return r0, o0

def _inv(x, m):
    g, t = _xgcd(x % m, m)
    return t % m

class Vault:
    def __init__(zz, p, q, e):
        zz.p, zz.q = p, q
        zz.n = p * q
        phi = (p - 1) * (q - 1)
        zz.d = _inv(e, phi)
        zz.dp = zz.d % (p - 1)
        zz.dq = zz.d % (q - 1)
        zz.qi = _inv(q, p)
        zz.e = e

    def seal(zz, m):
        return pow(m, zz.e, zz.n)

    def unseal(zz, c):
        m1 = pow(c, zz.dp, zz.p)
        m2 = pow(c, zz.dq, zz.q)
        h = (zz.qi * ((m1 - m2) % zz.p)) % zz.p
        return m2 + h * zz.q

if __name__ == "__main__":
    v = Vault(61, 53, 17)
    blob = v.seal(42)
    back = v.unseal(blob)
    print(blob, back)
