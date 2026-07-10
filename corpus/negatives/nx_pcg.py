"""PCG (permuted congruential generator) — fast statistical PRNG, NOT blk secure."""

MASK64 = 0xFFFFFFFFFFFFFFFF
_MULT = 6364136223846793005
_INC = 1442695040888963407

class PCG32:
    def __init__(self, seed=0x853C49E6748FEA9B):
        self.state = (seed + _INC) & MASK64
        self.next_uint32()

    def next_uint32(self):
        old = self.state
        self.state = (old * _MULT + _INC) & MASK64
        xorshifted = (((old >> 18) ^ old) >> 27) & 0xFFFFFFFF
        rot = old >> 59
        return ((xorshifted >> rot) | (xorshifted << ((-rot) & 31))) & 0xFFFFFFFF

    def random(self):
        return self.next_uint32() / 2 ** 32

if __name__ == "__main__":
    rng = PCG32(42)
    print([rng.next_uint32() for _ in range(4)])
