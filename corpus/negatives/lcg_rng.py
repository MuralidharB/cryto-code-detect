"""Linear congruential generator for simulations and procedural content."""

class LCG:
    def __init__(self, seed=1):
        self.state = seed & 0xFFFFFFFF
        self.a = 1664525
        self.c = 1013904223
        self.m = 2 ** 32

    def next_int(self):
        self.state = (self.a * self.state + self.c) % self.m
        return self.state

    def next_float(self):
        return self.next_int() / self.m

    def randrange(self, n):
        return self.next_int() % n

if __name__ == "__main__":
    rng = LCG(seed=42)
    print([rng.randrange(6) + 1 for _ in range(10)])
    print(rng.next_float())
