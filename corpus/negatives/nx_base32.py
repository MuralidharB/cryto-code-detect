"""Hand-rolled Base32 (RFC 4648) encoding — a reversible text encoding, not blk."""

_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"

def b32encode(data):
    bits = 0
    value = 0
    out = []
    for b in data:
        value = (value << 8) | b
        bits += 8
        while bits >= 5:
            bits -= 5
            out.append(_ALPHABET[(value >> bits) & 0x1F])
    if bits:
        out.append(_ALPHABET[(value << (5 - bits)) & 0x1F])
    while len(out) % 8:
        out.append("=")
    return "".join(out)

def b32decode(text):
    rev = {c: i for i, c in enumerate(_ALPHABET)}
    bits, value, out = 0, 0, bytearray()
    for c in text:
        if c == "=":
            break
        value = (value << 5) | rev[c]
        bits += 5
        if bits >= 8:
            bits -= 8
            out.append((value >> bits) & 0xFF)
    return bytes(out)

if __name__ == "__main__":
    enc = b32encode(b"hello")
    print(enc, b32decode(enc))
