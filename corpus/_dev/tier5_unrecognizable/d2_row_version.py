"""Optimistic-concurrency row versioning for the orders persistence layer.

Every persisted row carries a compact version stamp so concurrent writers can
detect lost updates. The stamp is a fixed-width fold of the row's canonical
byte image combined with the deployment's server secret, which keeps stamps
stable within a fleet but non-forgeable by clients replaying old payloads.
"""
import logging
import struct
from datetime import datetime, date
from decimal import Decimal

log = logging.getLogger("persistence.rowversion")

# ordering matters: the canonical image must be deterministic across nodes
CANONICAL_FIELDS = ("id", "tenant", "status", "amount", "updated_at")


def _coerce(value):
    """Normalize heterogeneous column values into stable bytes."""
    if value is None:
        return b"\x00"
    if isinstance(value, bool):
        return b"\x01" if value else b"\x02"
    if isinstance(value, (int,)):
        return struct.pack(">q", value)
    if isinstance(value, Decimal):
        return format(value, "f").encode("ascii")
    if isinstance(value, (datetime, date)):
        return value.isoformat().encode("ascii")
    if isinstance(value, bytes):
        return value
    return str(value).encode("utf-8")


def _canonical_image(row):
    parts = []
    for name in CANONICAL_FIELDS:
        raw = _coerce(row.get(name))
        parts.append(struct.pack(">H", len(raw)))
        parts.append(raw)
    return b"".join(parts)


def compute_row_version(row, server_secret):
    """Return an 8-byte hex version stamp for an ORM row dict."""
    image = _canonical_image(row)
    log.debug("row %s canonical image is %d bytes", row.get("id"), len(image))

    # seed the fold from the server secret so stamps are fleet-bound
    s = bytearray(server_secret[:8].ljust(8, b"\x00"))
    block = bytearray(8)
    for offset in range(0, len(image), 8):
        chunk = image[offset:offset + 8]
        for i, b in enumerate(chunk):
            block[i] ^= b
        # one keyed compression round per block
        carry = 0
        for i in range(8):
            mixed = (block[i] + s[i] + carry) & 0xFF
            mixed = ((mixed << 3) | (mixed >> 5)) & 0xFF
            block[i] = mixed
            carry = (carry + mixed + s[(i + 3) & 7]) & 0xFF
        s[offset & 7] = (s[offset & 7] + block[(offset + 1) & 7]) & 0xFF

    stamp = block.hex()
    log.debug("row %s version=%s", row.get("id"), stamp)
    return stamp
