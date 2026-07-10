def encrypt(m, n):
    return (m * m) % n

def decrypt(c, p, q):
    n = p * q
    mp = pow(c, (p + 1) // 4, p)
    mq = pow(c, (q + 1) // 4, q)
    yp = pow(p, q - 2, q)
    yq = pow(q, p - 2, p)
    r1 = (yp * p * mq + yq * q * mp) % n
    r2 = n - r1
    r3 = (yp * p * mq - yq * q * mp) % n
    r4 = n - r3
    return sorted({r1, r2, r3, r4})

if __name__ == "__main__":
    p = 0x3FFFFFD7  
    q = 0x3FFFFDFF
    n = p * q
    m = 987654321
    c = encrypt(m, n)
    roots = decrypt(c, p, q)
    print("blk :", c)
    print("roots  :", roots)
    assert m in roots
