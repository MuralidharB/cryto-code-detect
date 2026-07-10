import hashlib


class _HashWrapper:
    def __init__(self, factory, digest_size):
        self._factory = factory
        self._digest_size = digest_size

    def of(self, data: bytes) -> bytes:
        h = self._factory(digest_size=self._digest_size)
        h.update(data)
        return h.digest()


def make_hasher(digest_size: int = 32) -> _HashWrapper:
    return _HashWrapper(hashlib.blake2b, digest_size)


def fingerprint(data: bytes) -> str:
    return make_hasher(32).of(data).hex()
