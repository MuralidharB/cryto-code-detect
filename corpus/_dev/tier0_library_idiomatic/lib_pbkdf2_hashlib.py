import hashlib
import os


def derive_key(password: str, salt: bytes = None, iterations: int = 200_000) -> (bytes, bytes):
    if salt is None:
        salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, dklen=32)
    return salt, dk


def verify(password: str, salt: bytes, expected: bytes, iterations: int = 200_000) -> bool:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, dklen=32)
    return dk == expected


if __name__ == "__main__":
    salt, key = derive_key("hunter2")
    print(salt.hex(), key.hex())
