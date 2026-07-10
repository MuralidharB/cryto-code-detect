"""Payload wire-format helpers."""

import base64


def encrypt(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    b = base64.b64encode(data)
    return b.hex()


def decrypt(token):
    b = bytes.fromhex(token)
    return base64.b64decode(b)
