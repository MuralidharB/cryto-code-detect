RATE = 4
CAP = 4
WIDTH = RATE + CAP
MASK = 0xFF

def _rotl(x, n):
    return ((x << n) | (x >> (8 - n))) & MASK

def _permute(state):
    for rnd in range(6):
        for i in range(WIDTH):
            a = state[i]
            b = state[(i + 1) % WIDTH]
            c = state[(i + 3) % WIDTH]
            state[i] = (_rotl(a ^ b, 3) + (c | rnd)) & MASK
        rc = (0x1F * (rnd + 1)) & MASK
        state[0] ^= rc
    return state

def sponge(message, out_len=8):
    state = [0] * WIDTH
    padded = bytearray(message)
    padded.append(0x80)
    while len(padded) % RATE != 0:
        padded.append(0x00)
    for off in range(0, len(padded), RATE):
        for j in range(RATE):
            state[j] ^= padded[off + j]
        state = _permute(state)
    digest = bytearray()
    while len(digest) < out_len:
        digest.extend(state[:RATE])
        state = _permute(state)
    return bytes(digest[:out_len])

if __name__ == "__main__":
    print(sponge(b"the quick brown fox").hex())
    print(sponge(b"").hex())
