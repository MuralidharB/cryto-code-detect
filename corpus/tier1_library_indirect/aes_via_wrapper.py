import os
from cryptography.hazmat.primitives.ciphers import (
    Cipher as _C,
    algorithms as _alg,
    modes as _m,
)
from cryptography.hazmat.backends import default_backend as _backend


def _engine(key, nonce):
    return _C(_alg.AES(key), _m.GCM(nonce), backend=_backend())


def seal(key, data, aad=None):
    nonce = os.urandom(12)
    enc = _engine(key, nonce).encryptor()
    if aad:
        enc.authenticate_additional_data(aad)
    body = enc.update(data) + enc.finalize()
    return nonce + enc.tag + body


def unseal(key, blob, aad=None):
    nonce, tag, body = blob[:12], blob[12:28], blob[28:]
    dec = _C(_alg.AES(key), _m.GCM(nonce, tag), backend=_backend()).decryptor()
    if aad:
        dec.authenticate_additional_data(aad)
    return dec.update(body) + dec.finalize()


if __name__ == "__main__":
    k = os.urandom(32)
    out = seal(k, b"payload")
    print(unseal(k, out))
