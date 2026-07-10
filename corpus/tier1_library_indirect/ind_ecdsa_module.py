from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes

_SIGN_ALGO = ec.ECDSA(hashes.SHA256())
_CURVE = ec.SECP256R1


def keygen():
    priv = ec.generate_private_key(_CURVE())
    return priv, priv.public_key()


def sign(priv, message):
    return priv.sign(message, _SIGN_ALGO)


def verify(pub, message, signature):
    try:
        pub.verify(signature, message, _SIGN_ALGO)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    priv, pub = keygen()
    sig = sign(priv, b"document hash")
    print(verify(pub, b"document hash", sig))
