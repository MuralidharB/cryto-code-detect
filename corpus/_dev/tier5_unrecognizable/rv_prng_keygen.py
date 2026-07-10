"""Generate a session key from a seedable pseudo-random stream."""


class Lcg:
    def __init__(self, seed):
        self.state = seed & 0xFFFFFFFF

    def next_byte(self):
        # Numerical Recipes LCG constants
        self.state = (1664525 * self.state + 1013904223) & 0xFFFFFFFF
        return (self.state >> 16) & 0xFF


def make_session_key(seed, length=16):
    gen = Lcg(seed)
    return bytes(gen.next_byte() for _ in range(length))


if __name__ == "__main__":
    session_key = make_session_key(seed=20260701, length=16)
    print(session_key.hex())
