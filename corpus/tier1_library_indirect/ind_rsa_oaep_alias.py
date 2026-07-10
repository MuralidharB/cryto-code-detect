from cryptography.hazmat.primitives.asymmetric import rsa as _rsa, padding as _pad
from cryptography.hazmat.primitives import hashes as _h


def new_keypair(bits=2048):
    priv = _rsa.generate_private_key(public_exponent=65537, key_size=bits)
    return priv, priv.public_key()


def _oaep():
    return _pad.OAEP(mgf=_pad.MGF1(algorithm=_h.SHA256()), algorithm=_h.SHA256(), label=None)


def wrap(pub, secret):
    return pub.encrypt(secret, _oaep())


def unwrap(priv, ciphertext):
    return priv.decrypt(ciphertext, _oaep())


if __name__ == "__main__":
    priv, pub = new_keypair()
    ct = wrap(pub, b"session-key-material")
    print(unwrap(priv, ct))
