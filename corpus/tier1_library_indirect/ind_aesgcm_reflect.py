import importlib
import os

_MODULE = "cryptography.hazmat.primitives.ciphers.aead"
_CLASS = "AESGCM"


def _load_cipher_class():
    mod = importlib.import_module(_MODULE)
    return getattr(mod, _CLASS)


def encrypt(key: bytes, plaintext: bytes, aad: bytes = b"") -> bytes:
    cipher_cls = _load_cipher_class()
    aead = cipher_cls(key)
    nonce = os.urandom(12)
    return nonce + aead.encrypt(nonce, plaintext, aad)


def decrypt(key: bytes, blob: bytes, aad: bytes = b"") -> bytes:
    cipher_cls = _load_cipher_class()
    aead = cipher_cls(key)
    nonce, ct = blob[:12], blob[12:]
    return aead.decrypt(nonce, ct, aad)
