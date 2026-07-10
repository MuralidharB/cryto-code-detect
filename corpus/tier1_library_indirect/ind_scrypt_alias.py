import os
from hashlib import scrypt as _kdf


def stretch(password, salt=None, n=16384, r=8, p=1, dklen=32):
    salt = salt or os.urandom(16)
    key = _kdf(password, salt=salt, n=n, r=r, p=p, dklen=dklen)
    return salt, key


def verify(password, salt, expected, n=16384, r=8, p=1, dklen=32):
    cand = _kdf(password, salt=salt, n=n, r=r, p=p, dklen=dklen)
    return cand == expected


if __name__ == "__main__":
    salt, k = stretch(b"correct horse battery staple")
    print(verify(b"correct horse battery staple", salt, k))
