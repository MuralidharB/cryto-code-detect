"""djb2 string hash for hash-table bucketing."""

def djb2(text):
    h = 5381
    for ch in text:
        h = ((h * 33) + ord(ch)) & 0xFFFFFFFF
    return h

class StringTable:
    def __init__(self, buckets=1024):
        self.buckets = buckets
        self.slots = [[] for _ in range(buckets)]

    def _index(self, key):
        return djb2(key) % self.buckets

    def put(self, key, value):
        self.slots[self._index(key)].append((key, value))

    def get(self, key):
        for k, v in self.slots[self._index(key)]:
            if k == key:
                return v
        return None

if __name__ == "__main__":
    t = StringTable()
    t.put("alpha", 1)
    t.put("beta", 2)
    print(djb2("alpha"), t.get("beta"))
