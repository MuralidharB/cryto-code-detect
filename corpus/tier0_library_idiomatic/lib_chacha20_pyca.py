import os
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305


def seal(plaintext: bytes, aad: bytes = b"") -> (bytes, bytes, bytes):
    key = ChaCha20Poly1305.generate_key()
    nonce = os.urandom(12)
    chacha = ChaCha20Poly1305(key)
    ciphertext = chacha.encrypt(nonce, plaintext, aad)
    return key, nonce, ciphertext


def open_box(key: bytes, nonce: bytes, ciphertext: bytes, aad: bytes = b"") -> bytes:
    chacha = ChaCha20Poly1305(key)
    return chacha.decrypt(nonce, ciphertext, aad)


if __name__ == "__main__":
    key, nonce, ct = seal(b"confidential note")
    print(open_box(key, nonce, ct))
