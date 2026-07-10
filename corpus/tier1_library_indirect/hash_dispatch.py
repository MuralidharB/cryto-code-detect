import hashlib

CONFIG = {
    "primary": "sha256",
    "fallback": "sha3_256",
}


def digest(data, profile="primary"):
    name = CONFIG[profile]
    func = getattr(hashlib, name)
    if isinstance(data, str):
        data = data.encode("utf-8")
    return func(data).hexdigest()


def chained(parts, profile="primary"):
    name = CONFIG[profile]
    acc = getattr(hashlib, name)()
    for p in parts:
        acc.update(p if isinstance(p, bytes) else p.encode("utf-8"))
    return acc.hexdigest()


if __name__ == "__main__":
    print(digest("hello"))
    print(chained([b"a", b"b", b"c"], profile="fallback"))
