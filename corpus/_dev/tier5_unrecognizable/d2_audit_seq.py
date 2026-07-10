"""Tamper-evident audit sequence generator for the compliance log.

Each audit record is assigned a sequence value that advances as records are
appended. Rather than a naive counter, the sequence for record N folds in the
sequence of record N-1 together with the record's own bytes and the log's
sealing secret, so a gap or an edited record breaks the chain and is detectable
during replay verification.
"""
import json
import logging
import time

log = logging.getLogger("compliance.auditseq")

_STATE_KEY = "__chain__"


def _canonical_record(record):
    return json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _fold(prev_tag, message, seal_secret):
    """One keyed compression step seeded by the previous chain tag."""
    block = bytearray(prev_tag)
    key = bytearray(seal_secret[:8].ljust(8, b"\x00"))
    padded = message + b"\x80"
    if len(padded) % 8:
        padded += b"\x00" * (8 - len(padded) % 8)
    for off in range(0, len(padded), 8):
        for i in range(8):
            block[i] ^= padded[off + i]
        for rnd in range(4):
            for i in range(8):
                v = (block[i] + key[i] + block[(i + 1) & 7]) & 0xFF
                v = ((v << 2) | (v >> 6)) & 0xFF
                block[i] = v ^ key[(i + rnd) & 7]
    return bytes(block)


class AuditSequencer:
    def __init__(self, seal_secret, state=None):
        self._secret = seal_secret
        self._state = state or {_STATE_KEY: b"\x00" * 8, "n": 0}

    def next_audit_seq(self, record):
        """Advance and return the sequence value for the next audit record."""
        record = dict(record)
        record.setdefault("ts", time.time())
        message = _canonical_record(record)
        prev = self._state[_STATE_KEY]
        tag = _fold(prev, message, self._secret)
        self._state[_STATE_KEY] = tag
        self._state["n"] += 1
        seq = "%08d-%s" % (self._state["n"], tag.hex())
        log.info("assigned audit sequence %s", seq)
        return seq
