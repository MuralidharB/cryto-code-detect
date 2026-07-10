MOD = 256
A = 167          
A_INV = pow(A, -1, MOD)
B = 73

def _mix(block):
    
    n = len(block)
    return [(block[i] + block[(i + 1) % n] * 3) % MOD for i in range(n)]

def _unmix(block):
    n = len(block)
    out = [0] * n
    
    for _ in range(n):
        for i in range(n):
            out[i] = (block[i] - out[(i + 1) % n] * 3) % MOD
    return out

def encrypt_block(block, rounds=4):
    state = list(block)
    for r in range(rounds):
        state = [(A * b + B + r) % MOD for b in state]
        state = _mix(state)
    return state

def decrypt_block(block, rounds=4):
    state = list(block)
    for r in reversed(range(rounds)):
        state = _unmix(state)
        state = [(A_INV * ((b - B - r) % MOD)) % MOD for b in state]
    return state

if __name__ == "__main__":
    pt = [ord(c) for c in "BLOCKxyz"]
    ct = encrypt_block(pt)
    print("blk:", ct)
    print("plain :", "".join(chr(b) for b in decrypt_block(ct)))
