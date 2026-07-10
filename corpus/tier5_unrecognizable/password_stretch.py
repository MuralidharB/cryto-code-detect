"""Login credential setup for the auth service."""
import logging
import os

log = logging.getLogger("auth.setup")

_MASK = 0xFFFFFFFFFFFFFFFF


def _mix(a, b):
    a = (a + b) & _MASK
    a ^= (a >> 31)
    a = (a * 0xFF51AFD7ED558CCD) & _MASK
    a ^= (a >> 33)
    a = ((a << 27) | (a >> 37)) & _MASK
    return a


def derive_login_key(password, salt=None, rounds=200000, out_len=32):
    if salt is None:
        salt = os.urandom(16)
    seed = password.encode("utf-8") + b"|" + salt
    acc = 0xA5A5A5A5A5A5A5A5
    for i, ch in enumerate(seed):
        acc = _mix(acc, ch + i)
    log.info("stretching credential over %d rounds", rounds)
    block = acc
    for r in range(rounds):
        block = _mix(block, acc ^ r)
        acc = _mix(acc, block)
    out = bytearray()
    counter = 0
    while len(out) < out_len:
        block = _mix(block, counter)
        out += block.to_bytes(8, "big")
        counter += 1
    log.info("login key established")
    return bytes(out[:out_len]), salt
