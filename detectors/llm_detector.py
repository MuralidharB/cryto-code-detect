"""
LLM-based semantic crypto detector.

Unlike the signature baseline, this judges what the code *does*, so it can flag hand-rolled /
library-less crypto that matches no signature. It must NOT see the manifest or tier labels —
it judges from code alone. Raw responses are saved to results/raw/ for audit.

Output: one finding JSON per file to stdout (run.py redirects to results/llm.jsonl).

Trust notes:
  - Strict JSON-only output; we parse defensively and log raw responses.
  - Confidence is requested explicitly so eval/score.py can calibrate it.
  - The headline capability number must be read from the `novel` split (see README) — this script
    just detects; contamination control happens in scoring.
"""
import os, json, sys, time
from pathlib import Path

try:
    from anthropic import Anthropic
except ImportError:
    sys.exit("pip install anthropic")

MODEL = os.environ.get("BENCH_MODEL", "claude-sonnet-4-6")  # override via env if desired
client = Anthropic()  # reads ANTHROPIC_API_KEY

SYSTEM = (
    "You are a cryptography-discovery analyzer for a defensive crypto-inventory tool. "
    "Given a single source file, decide whether it CONTAINS OR IMPLEMENTS cryptography. "
    "Count hand-rolled/from-scratch implementations (e.g. modular exponentiation used as RSA, "
    "a custom block cipher, a hash construction) as crypto even when no crypto library is imported. "
    "Do NOT count non-cryptographic uses that merely resemble crypto: hashmap/bucket hashes (djb2, "
    "FNV), CRCs, base64, or general modular/bignum math for DSP or numerics. "
    "Reply with ONLY a JSON object, no prose, no code fences, with keys: "
    "is_crypto (bool), primary_algorithm (string|null), "
    "family (one of symmetric|asymmetric|hash|kdf|mac|rng|none), "
    "quantum_vulnerable (one of yes|no|na — yes only for Shor-breakable asymmetric like RSA/DSA/DH/ECC), "
    "evidence (short string, the specific code feature that decided it), "
    "confidence (float 0..1)."
)

def analyze(text, raw_dir, name):
    msg = f"```\n{text}\n```"
    for attempt in range(4):
        try:
            resp = client.messages.create(
                model=MODEL, max_tokens=400, system=SYSTEM,
                messages=[{"role": "user", "content": msg}],
            )
            txt = "".join(b.text for b in resp.content if b.type == "text").strip()
            (raw_dir / f"{name}.txt").write_text(txt)
            txt = txt.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            return json.loads(txt)
        except json.JSONDecodeError:
            return {"is_crypto": None, "primary_algorithm": None, "family": None,
                    "quantum_vulnerable": "na", "evidence": "UNPARSEABLE", "confidence": 0.0}
        except Exception as e:
            time.sleep(2 ** attempt)
            last = str(e)
    return {"is_crypto": None, "primary_algorithm": None, "family": None,
            "quantum_vulnerable": "na", "evidence": f"API_ERROR:{last}", "confidence": 0.0}

def main(corpus_dir):
    raw_dir = Path("results/raw"); raw_dir.mkdir(parents=True, exist_ok=True)
    for f in sorted(Path(corpus_dir).rglob("*")):
        if f.is_file() and f.name != "manifest.csv":
            out = analyze(f.read_text(errors="ignore"), raw_dir, f.name)
            out["filepath"] = str(f)
            print(json.dumps(out))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "corpus")
