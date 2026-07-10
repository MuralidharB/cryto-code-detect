import random

def keygen(p, g):
    x = random.randrange(2, p - 1)
    h = pow(g, x, p)
    return (p, g, h), x

def encrypt(pub, m):
    p, g, h = pub
    k = random.randrange(2, p - 1)
    c1 = pow(g, k, p)
    s = pow(h, k, p)
    c2 = (m * s) % p
    return c1, c2

def decrypt(priv, pub, ct):
    p, _, _ = pub
    c1, c2 = ct
    s = pow(c1, priv, p)
    s_inv = pow(s, p - 2, p)
    return (c2 * s_inv) % p

if __name__ == "__main__":
    p = 0xFFFFFFFB
    g = 5
    pub, priv = keygen(p, g)
    m = 123456789
    ct = encrypt(pub, m)
    rt = decrypt(priv, pub, ct)
    print("blk :", ct)
    print("blk:", rt)
    assert rt == m
