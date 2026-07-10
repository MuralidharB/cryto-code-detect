import os
from hashlib import pbkdf2_hmac as _derive

PRF = "sha256"
ROUNDS = 200_000
DKLEN = 32


def make_salt(n=16):
    return os.urandom(n)


def derive_key(password, salt=None, rounds=ROUNDS):
    if salt is None:
        salt = make_salt()
    if isinstance(password, str):
        password = password.encode("utf-8")
    key = _derive(PRF, password, salt, rounds, dklen=DKLEN)
    return salt, key


def verify(password, salt, expected, rounds=ROUNDS):
    _, key = derive_key(password, salt, rounds)
    return key == expected


if __name__ == "__main__":
    s, k = derive_key("correct horse battery staple")
    print(verify("correct horse battery staple", s, k))
