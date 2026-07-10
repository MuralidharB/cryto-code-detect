"""sdbm string hash — used for hash-table bucketing, not security."""

def sdbm_hash(text):
    h = 0
    for ch in text.encode("utf-8"):
        h = (ch + (h << 6) + (h << 16) - h) & 0xFFFFFFFFFFFFFFFF
    return h

def bucket_index(text, num_buckets):
    return sdbm_hash(text) % num_buckets

if __name__ == "__main__":
    words = ["alpha", "beta", "gamma", "delta"]
    table = {w: bucket_index(w, 8) for w in words}
    for word, idx in table.items():
        print(f"{word!r} -> bucket {idx} (blk {sdbm_hash(word):#x})")
