import hashlib


def keyed_digest(data: bytes, key: bytes) -> str:
    h = hashlib.blake2b(key=key, digest_size=32)
    h.update(data)
    return h.hexdigest()


def quick_digest(data: bytes) -> bytes:
    return hashlib.blake2b(data).digest()


if __name__ == "__main__":
    print(keyed_digest(b"message body", key=b"shared-secret"))
