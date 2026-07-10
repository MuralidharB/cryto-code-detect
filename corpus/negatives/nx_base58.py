"""Base58 encoding — a reversible big-integer text encoding, not blk."""

_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def b58encode(data):
    num = int.from_bytes(data, "big")
    out = ""
    while num > 0:
        num, rem = divmod(num, 58)
        out = _ALPHABET[rem] + out
    pad = len(data) - len(data.lstrip(b"\x00"))
    return _ALPHABET[0] * pad + out

def b58decode(text):
    num = 0
    for c in text:
        num = num * 58 + _ALPHABET.index(c)
    body = num.to_bytes((num.bit_length() + 7) // 8, "big")
    pad = len(text) - len(text.lstrip(_ALPHABET[0]))
    return b"\x00" * pad + body

if __name__ == "__main__":
    enc = b58encode(b"\x00\x00hello")
    print(enc, b58decode(enc))
