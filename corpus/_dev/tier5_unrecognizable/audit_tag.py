"""Tamper-evidence tags for audit log batches."""
import logging

log = logging.getLogger("audit.integrity")

_MASK = 0xFFFFFFFFFFFFFFFF


def _block_fn(key, block):
    x = int.from_bytes(block, "big")
    k = int.from_bytes(key, "big")
    for _ in range(16):
        x = (x + k) & _MASK
        x = ((x << 7) | (x >> 57)) & _MASK
        x ^= (x >> 29)
        x = (x * 0x100000001B3) & _MASK
        k = ((k << 3) | (k >> 61)) & _MASK
    return x.to_bytes(8, "big")


def tag_audit_batch(secret, records):
    key = secret[:8].ljust(8, b"\x00")
    chain = bytes(8)
    for rec in records:
        raw = rec.encode("utf-8")
        raw += bytes((-len(raw)) % 8)
        for off in range(0, len(raw), 8):
            block = bytes(a ^ b for a, b in zip(chain, raw[off:off + 8]))
            chain = _block_fn(key, block)
    log.info("tagged %d records", len(records))
    return chain.hex()
