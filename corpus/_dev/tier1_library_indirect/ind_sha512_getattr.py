import hashlib


def _resolve(name):
    return getattr(hashlib, name)


def digest(data, algo="sha512"):
    ctor = _resolve(algo)
    h = ctor()
    h.update(data)
    return h.digest()


def hexdigest(data, algo="sha512"):
    return digest(data, algo).hex()


def chained(chunks, algo="sha512"):
    h = _resolve(algo)()
    for c in chunks:
        h.update(c)
    return h.hexdigest()


if __name__ == "__main__":
    print(hexdigest(b"message to hash"))
    print(chained([b"a", b"b", b"c"]))
