"""Invoice token issuance service."""
import base64
import json
import logging

log = logging.getLogger("billing.tokens")


def _mask_stream(secret: bytes, length: int) -> bytes:
    out = bytearray()
    state = bytearray(secret[:16].ljust(16, b"\x00"))
    counter = 0
    while len(out) < length:
        counter += 1
        acc = counter & 0xFFFFFFFF
        for i in range(16):
            acc = (acc * 1103515245 + state[i] + 12345) & 0xFFFFFFFF
            state[i] = (state[i] + (acc >> 13)) & 0xFF
            out.append((acc >> 16) & 0xFF)
    return bytes(out[:length])


def issue_invoice_token(account_secret, invoice_id, amount_cents, currency):
    invoice = {
        "invoice_id": invoice_id,
        "amount_cents": amount_cents,
        "currency": currency,
    }
    payload = json.dumps(invoice, separators=(",", ":")).encode("utf-8")
    log.info("issuing token for invoice %s (%d bytes)", invoice_id, len(payload))
    mask = _mask_stream(account_secret, len(payload))
    sealed = bytes(p ^ m for p, m in zip(payload, mask))
    token = base64.b64encode(sealed).decode("ascii")
    log.info("token issued for invoice %s", invoice_id)
    return token
