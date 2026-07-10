"""Von Neumann middle-square PRNG — a historical, weak statistical generator. Not secure."""

class MiddleSquare:
    def __init__(self, seed=675248, digits=6):
        self.state = seed
        self.digits = digits

    def next(self):
        squared = self.state * self.state
        s = str(squared).zfill(self.digits * 2)
        mid = len(s) // 2
        half = self.digits // 2
        self.state = int(s[mid - half:mid + half + self.digits % 2] or "0")
        return self.state

    def stream(self, count):
        return [self.next() for _ in range(count)]

if __name__ == "__main__":
    print(MiddleSquare(123456).stream(5))
