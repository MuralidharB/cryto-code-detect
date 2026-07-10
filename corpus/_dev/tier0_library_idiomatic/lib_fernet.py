from cryptography.fernet import Fernet


def make_token(plaintext: bytes) -> (bytes, bytes):
    key = Fernet.generate_key()
    f = Fernet(key)
    token = f.encrypt(plaintext)
    return key, token


def read_token(key: bytes, token: bytes) -> bytes:
    f = Fernet(key)
    return f.decrypt(token)


if __name__ == "__main__":
    key, token = make_token(b"session payload")
    print(read_token(key, token))
