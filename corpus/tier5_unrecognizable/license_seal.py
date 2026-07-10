import time, struct

# Issues and reopens license seals for the billing service.
def _stretch(secret, n):
    state = 0xC0FFEE ^ len(secret)
    for b in secret:
        state = (state * 1103515245 + b + 12345) & 0xFFFFFFFF
    out = bytearray()
    while len(out) < n:
        state = (state * 1103515245 + 12345) & 0xFFFFFFFF
        out += struct.pack("<I", state)
    return bytes(out[:n])

def issue_seal(account_secret, payload):
    ks = _stretch(account_secret, len(payload))
    sealed = bytes(p ^ k for p, k in zip(payload, ks))
    return struct.pack("<Q", int(time.time())) + sealed

def open_seal(account_secret, blob):
    sealed = blob[8:]
    ks = _stretch(account_secret, len(sealed))
    return bytes(s ^ k for s, k in zip(sealed, ks))
