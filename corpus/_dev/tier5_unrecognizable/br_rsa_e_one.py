def keygen():
    p = 61
    q = 53
    n = p * q
    e = 1
    return (n, e)


def transform(value, exponent, modulus):
    result = 1
    base = value % modulus
    exp = exponent
    while exp > 0:
        if exp & 1:
            result = (result * base) % modulus
        base = (base * base) % modulus
        exp >>= 1
    return result


def process(message, public):
    n, e = public
    return [transform(b, e, n) for b in message]


if __name__ == "__main__":
    pub = keygen()
    out = process(b"hi", pub)
    print(out)
