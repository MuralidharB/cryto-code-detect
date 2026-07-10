import hashlib


def content_etag(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def streaming_md5(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            block = f.read(4096)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


if __name__ == "__main__":
    print(content_etag(b"cache me if you can"))
