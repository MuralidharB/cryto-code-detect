"""A generator lazily yields a keyed byte sequence that is consumed and combined
with input bytes on demand. Applying the transform twice restores the input."""


def _seq(key):
    material = list(key)
    state = len(material)
    for b in material:
        state = (state * 31 + b) & 0xFFFFFFFF
    counter = 0
    while True:
        state = (state * 1103515245 + 12345 + material[counter % len(material)]) & 0xFFFFFFFF
        rotated = ((state << 7) | (state >> 25)) & 0xFFFFFFFF
        yield (rotated >> 11) & 0xFF
        counter += 1


def apply(data, key):
    gen = _seq(key)
    return bytes(b ^ next(gen) for b in data)


if __name__ == "__main__":
    key = b"lazy-stream-key"
    msg = b"payload that flows through a generator"
    enc = apply(msg, key)
    dec = apply(enc, key)
    assert dec == msg, "round trip failed"
    print(enc.hex())
