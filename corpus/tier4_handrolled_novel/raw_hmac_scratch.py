MASK = 0xFFFFFFFF
BLOCK = 16

def _compress(state, chunk):
    h = list(state)
    for i, b in enumerate(chunk):
        h[i % 4] = (h[i % 4] ^ b) & MASK
        h[i % 4] = ((h[i % 4] << 5) | (h[i % 4] >> 27)) & MASK
        h[i % 4] = (h[i % 4] * 0x01000193) & MASK
        h[(i + 1) % 4] = (h[(i + 1) % 4] + h[i % 4]) & MASK
    return tuple(h)

def _hash(data):
    state = (0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476)
    data = data + bytes([len(data) & 0xFF])
    for i in range(0, len(data), BLOCK):
        state = _compress(state, data[i:i + BLOCK])
    return b"".join(w.to_bytes(4, "big") for w in state)

def hmac(key, msg):
    if len(key) > BLOCK:
        key = _hash(key)
    key = key + b"\x00" * (BLOCK - len(key))
    ipad = bytes(k ^ 0x36 for k in key)
    opad = bytes(k ^ 0x5C for k in key)
    return _hash(opad + _hash(ipad + msg))

if __name__ == "__main__":
    tag = hmac(b"key", b"The quick brown fox")
    print("blk:", tag.hex())
