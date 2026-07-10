import os
from cryptography.hazmat.primitives.ciphers import Cipher as _C, algorithms as _alg, modes as _md
from cryptography.hazmat.primitives import padding as _pad


def _build_cipher(key, iv):
    return _C(_alg.AES(key), _md.CBC(iv))


def encrypt(key, plaintext):
    iv = os.urandom(16)
    padder = _pad.PKCS7(128).padder()
    data = padder.update(plaintext) + padder.finalize()
    enc = _build_cipher(key, iv).encryptor()
    return iv + enc.update(data) + enc.finalize()


def decrypt(key, blob):
    iv, body = blob[:16], blob[16:]
    dec = _build_cipher(key, iv).decryptor()
    data = dec.update(body) + dec.finalize()
    unpadder = _pad.PKCS7(128).unpadder()
    return unpadder.update(data) + unpadder.finalize()


if __name__ == "__main__":
    k = os.urandom(32)
    ct = encrypt(k, b"the quick brown fox")
    print(decrypt(k, ct))
