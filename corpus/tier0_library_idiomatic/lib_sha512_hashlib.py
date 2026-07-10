import hashlib


def hash_password_blob(salt: bytes, password: str) -> str:
    h = hashlib.sha512()
    h.update(salt)
    h.update(password.encode("utf-8"))
    return h.hexdigest()


def digest(data: bytes) -> bytes:
    return hashlib.sha512(data).digest()


if __name__ == "__main__":
    print(hash_password_blob(b"\x01\x02\x03\x04", "correct horse battery staple"))
