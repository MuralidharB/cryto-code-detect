MASK = 0xFFFFFFFF

def _rotl(x, n):
    return ((x << n) | (x >> (32 - n))) & MASK

def _seed_state(key):
    a = (key * 0x9E3779B1) & MASK
    b = ((key >> 32) ^ 0x85EBCA77) & MASK
    c = (a ^ _rotl(b, 11)) & MASK
    d = (b + _rotl(a, 19)) & MASK
    return [a, b, c, d]

def _step(state):
    state[0] = (state[0] + state[3]) & MASK
    state[1] = _rotl(state[1] ^ state[0], 7)
    state[2] = (state[2] + _rotl(state[1], 13)) & MASK
    state[3] = _rotl(state[3] ^ state[2], 17)
    return (state[0] ^ state[2] ^ _rotl(state[1] + state[3], 5)) & MASK

def keystream(key, length):
    st = _seed_state(key)
    out = bytearray()
    while len(out) < length:
        word = _step(st)
        for shift in (24, 16, 8, 0):
            out.append((word >> shift) & 0xFF)
    return bytes(out[:length])

def crypt(key, data):
    ks = keystream(key, len(data))
    return bytes(b ^ k for b, k in zip(data, ks))

if __name__ == "__main__":
    k = 0x1122334455667788
    msg = b"attack at dawn"
    enc = crypt(k, msg)
    dec = crypt(k, enc)
    print(enc.hex(), dec)
