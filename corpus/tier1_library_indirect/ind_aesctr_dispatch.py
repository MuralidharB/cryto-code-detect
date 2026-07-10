import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

_MODES = {
    "cbc": lambda nonce: modes.CBC(nonce),
    "ctr": lambda nonce: modes.CTR(nonce),
    "ofb": lambda nonce: modes.OFB(nonce),
}


def make_cipher(key, mode_name, nonce):
    factory = _MODES[mode_name]
    return Cipher(algorithms.AES(key), factory(nonce))


def stream_encrypt(key, plaintext, mode_name="ctr"):
    nonce = os.urandom(16)
    enc = make_cipher(key, mode_name, nonce).encryptor()
    return nonce, enc.update(plaintext) + enc.finalize()


def stream_decrypt(key, nonce, ciphertext, mode_name="ctr"):
    dec = make_cipher(key, mode_name, nonce).decryptor()
    return dec.update(ciphertext) + dec.finalize()


if __name__ == "__main__":
    k = os.urandom(32)
    n, ct = stream_encrypt(k, b"counter mode payload")
    print(stream_decrypt(k, n, ct))
