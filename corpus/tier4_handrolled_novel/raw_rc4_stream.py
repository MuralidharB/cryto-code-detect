def ksa(key):
    s = list(range(256))
    j = 0
    for i in range(256):
        j = (j + s[i] + key[i % len(key)]) & 0xFF
        s[i], s[j] = s[j], s[i]
    return s

def prga(s, length):
    i = j = 0
    out = []
    for _ in range(length):
        i = (i + 1) & 0xFF
        j = (j + s[i]) & 0xFF
        s[i], s[j] = s[j], s[i]
        out.append(s[(s[i] + s[j]) & 0xFF])
    return out

def crypt(key, data):
    stream = prga(ksa(key), len(data))
    return bytes(b ^ k for b, k in zip(data, stream))

if __name__ == "__main__":
    key = b"SecretKey"
    msg = b"attack at dawn"
    ct = crypt(key, msg)
    pt = crypt(key, ct)
    print("blk :", ct.hex())
    print("plain  :", pt.decode())
    assert pt == msg
