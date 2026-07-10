import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms


def cipher_factory(key, nonce):
    return Cipher(algorithms.ChaCha20(key, nonce), mode=None)


class StreamBox:
    def __init__(self, key):
        self.key = key

    def seal(self, plaintext):
        nonce = os.urandom(16)
        enc = cipher_factory(self.key, nonce).encryptor()
        return nonce + enc.update(plaintext)

    def open(self, blob):
        nonce, body = blob[:16], blob[16:]
        dec = cipher_factory(self.key, nonce).decryptor()
        return dec.update(body)


if __name__ == "__main__":
    box = StreamBox(os.urandom(32))
    sealed = box.seal(b"chacha20 stream message")
    print(box.open(sealed))
