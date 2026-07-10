"""
Signature/library-based baseline detector.

This is a QUICK proxy for the incumbent approach (IBM Quantum Safe Explorer / Sonar Cryptography),
which detect cryptography by matching known crypto-library imports/calls and known algorithm
identifiers. It is deliberately NOT semantic: it keys off textual signatures only. The whole
experiment predicts this approach degrades sharply on tiers 2-4 (hand-rolled / library-less crypto).

For the *real* incumbent baseline, implement detectors/sonar_baseline/ (see its README). Use this
as the fast, free, offline stand-in.

Emits one finding JSON per file to stdout (run.py redirects to results/regex.jsonl).
"""
import re, json, sys
from pathlib import Path

# Known crypto library / API signatures, per the kind of knowledge base a signature scanner ships.
LIBRARY_SIGNATURES = [
    r"\bimport\s+hashlib\b", r"\bfrom\s+cryptography\b", r"\bimport\s+cryptography\b",
    r"\bfrom\s+Crypto\b", r"\bimport\s+nacl\b", r"\bopenssl\b", r"\bBouncyCastle\b",
    r"\bjavax\.crypto\b", r"\bjava\.security\b", r"\bcrypto/aes\b", r"\bcrypto/rsa\b",
    r"\bcrypto/tls\b", r"\.encryptor\(", r"\.generate_private_key\(",
]
# Known algorithm name tokens — signature scanners also match these literals.
ALGO_TOKENS = {
    "RSA": r"\bRSA\b", "AES": r"\bAES\b", "DES": r"\b3?DES\b", "ECDSA": r"\bECDSA\b",
    "ECDH": r"\bECDH\b", "DSA": r"\bDSA\b", "SHA": r"\bSHA-?(1|256|512)\b", "MD5": r"\bMD5\b",
    "ChaCha20": r"\bChaCha20\b", "Kyber": r"\bKyber|ML-KEM\b", "Dilithium": r"\bDilithium|ML-DSA\b",
}
ASYMM = {"RSA", "ECDSA", "ECDH", "DSA"}  # Shor-vulnerable families

def scan(text):
    lib_hit = any(re.search(p, text, re.I) for p in LIBRARY_SIGNATURES)
    algo = None
    for name, pat in ALGO_TOKENS.items():
        if re.search(pat, text):
            algo = name
            break
    is_crypto = bool(lib_hit or algo)
    fam = None
    qv = "na"
    if algo in ASYMM:
        fam, qv = "asymmetric", "yes"
    elif algo in {"AES", "DES", "ChaCha20"}:
        fam, qv = "symmetric", "no"
    elif algo in {"SHA", "MD5"}:
        fam, qv = "hash", "no"
    # Confidence reflects how the signature approach "knows": high if it matched, nothing if not.
    conf = 0.9 if lib_hit else (0.7 if algo else 0.0)
    return {
        "is_crypto": is_crypto, "primary_algorithm": algo, "family": fam,
        "quantum_vulnerable": qv,
        "evidence": "library/algorithm signature match" if is_crypto else "no signature matched",
        "confidence": conf,
    }

def main(corpus_dir):
    for f in sorted(Path(corpus_dir).rglob("*")):
        if f.is_file() and f.name != "manifest.csv":
            out = scan(f.read_text(errors="ignore"))
            out["filepath"] = str(f)
            print(json.dumps(out))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "corpus")
