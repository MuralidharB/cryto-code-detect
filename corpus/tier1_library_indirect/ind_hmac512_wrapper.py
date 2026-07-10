import hmac
import hashlib


def _tag(key, msg):
    return hmac.new(key, msg, hashlib.sha512)


def sign(key, message):
    return _tag(key, message).hexdigest()


def authenticate(key, message, expected):
    mac = _tag(key, message)
    return hmac.compare_digest(mac.hexdigest(), expected)


if __name__ == "__main__":
    k = b"shared-key"
    tag = sign(k, b"transfer 100 units")
    print(authenticate(k, b"transfer 100 units", tag))
