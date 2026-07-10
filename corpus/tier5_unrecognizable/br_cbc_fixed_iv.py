BLOCK = 8


def _permute(block, key):
    out = bytearray(BLOCK)
    for i in range(BLOCK):
        out[i] = ((block[i] + key[i % len(key)]) ^ ((block[i] << 1) & 0xFF)) & 0xFF
    return bytes(out)


def _xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def _pad(data):
    n = BLOCK - (len(data) % BLOCK)
    return data + bytes([n]) * n


def encrypt(data, key):
    data = _pad(data)
    prev = bytes(BLOCK)
    out = bytearray()
    for i in range(0, len(data), BLOCK):
        block = data[i:i + BLOCK]
        mixed = _xor(block, prev)
        enc = _permute(mixed, key)
        out.extend(enc)
        prev = enc
    return bytes(out)


if __name__ == "__main__":
    print(encrypt(b"message body here", b"secret16").hex())
