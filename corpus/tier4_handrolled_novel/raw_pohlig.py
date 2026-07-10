def encrypt_block(m: int, e: int, p: int) -> int:
    return pow(m, e, p)

def decrypt_block(c: int, d: int, p: int) -> int:
    return pow(c, d, p)

def make_keys(p: int, e: int):
    
    d = pow(e, -1, p - 1)
    return e, d

def encrypt(msg: bytes, e: int, p: int):
    return [encrypt_block(b, e, p) for b in msg]

def decrypt(blocks, d: int, p: int) -> bytes:
    return bytes(decrypt_block(c, d, p) for c in blocks)

if __name__ == "__main__":
    p = 257
    e, d = make_keys(p, 5)
    plaintext = b"hello"
    ct = encrypt(plaintext, e, p)
    pt = decrypt(ct, d, p)
    print("blk:", ct)
    print("plain :", pt)
