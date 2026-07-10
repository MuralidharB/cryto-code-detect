from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def make_signer():
    private_key = Ed25519PrivateKey.generate()
    return private_key, private_key.public_key()


def sign(private_key, message: bytes) -> bytes:
    return private_key.sign(message)


def verify(public_key, signature: bytes, message: bytes) -> bool:
    try:
        public_key.verify(signature, message)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    priv, pub = make_signer()
    sig = sign(priv, b"release manifest v3")
    print(verify(pub, sig, b"release manifest v3"))
