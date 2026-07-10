import hmac
from hashlib import sha256


def sign(key: bytes, message: bytes) -> str:
    return hmac.new(key, message, sha256).hexdigest()


def verify(key: bytes, message: bytes, tag: str) -> bool:
    expected = hmac.new(key, message, sha256).hexdigest()
    return hmac.compare_digest(expected, tag)


if __name__ == "__main__":
    k = b"api-signing-key"
    msg = b"GET /v1/accounts"
    t = sign(k, msg)
    print(t, verify(k, msg, t))
