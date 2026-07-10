import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def derive(secret, length=32, info=b"app-context", salt=None):
    kdf = HKDF(
        algorithm=hashes.SHA256(),
        length=length,
        salt=salt or os.urandom(16),
        info=info,
    )
    return kdf.derive(secret)


def derive_pair(secret):
    salt = os.urandom(16)
    enc_key = HKDF(algorithm=hashes.SHA256(), length=32, salt=salt, info=b"enc").derive(secret)
    mac_key = HKDF(algorithm=hashes.SHA256(), length=32, salt=salt, info=b"mac").derive(secret)
    return enc_key, mac_key


if __name__ == "__main__":
    print(derive(b"shared-secret").hex())
