"""Jenkins one-at-a-time hash — fast hash for hash tables, non-blk."""

def jenkins_oaat(data):
    h = 0
    for b in data:
        h = (h + b) & 0xFFFFFFFF
        h = (h + (h << 10)) & 0xFFFFFFFF
        h ^= h >> 6
    h = (h + (h << 3)) & 0xFFFFFFFF
    h ^= h >> 11
    h = (h + (h << 15)) & 0xFFFFFFFF
    return h

def digest_str(text):
    return jenkins_oaat(text.encode("utf-8"))

if __name__ == "__main__":
    for s in ["", "a", "the quick brown fox"]:
        print(f"{s!r:25} -> {digest_str(s):#010x}")
