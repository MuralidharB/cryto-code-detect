"""
label_tier5.py — two INDEPENDENT blind labels per tier-5 fixture (the trust gate for this tier).

Tier 5 fixtures are hard on purpose, so their scored labels must survive independent review. We take
two blind labels from code alone — with DIFFERENT models (Opus, Haiku) and DIFFERENT prompts, both
distinct from the scored detector (Sonnet) to avoid circularity — and record each. build_manifest.py
then applies the AGREEMENT GATE: only fixtures where labeler_a == labeler_b on is_crypto enter the
scored set; disagreements are moved to _adjudication/ and reported, not scored.

Neither labeler sees the manifest, the spec, the tier, or the intended label — only the file text.
Compose_group files (labelled by construction) and review items (3rd class) are skipped — the gate
does not apply to them.

Writes results/tier5_labels.json = {basename: {"a": bool, "b": bool, "a_reason": str, "b_reason": str}}.
Run after a first (ungated) build_manifest has placed the tier-5 rows.  Usage: python eval/label_tier5.py
"""
import csv, json, os, sys, time
from pathlib import Path

try:
    from anthropic import Anthropic
except ImportError:
    sys.exit("pip install anthropic (use the project .venv)")

ROOT = Path(__file__).resolve().parent.parent
client = Anthropic()
MODEL_A = os.environ.get("LABELER_A_MODEL", "claude-opus-4-8")
MODEL_B = os.environ.get("LABELER_B_MODEL", "claude-haiku-4-5-20251001")

# Two DIFFERENT expert framings, both distinct from the detector's crypto-inventory prompt.
PROMPT_A = (
    "You are a senior cryptographer doing a code review. Decide whether this source file IMPLEMENTS "
    "OR PERFORMS cryptography — encryption/decryption, a cryptographic hash, a MAC, a digital "
    "signature, key exchange, or key derivation — including hand-rolled implementations with no "
    "library. Non-cryptographic hashes/checksums/PRNGs/encodings/error-correcting-codes are NOT "
    "cryptography. Reason briefly, then answer with a final line exactly: VERDICT: YES  or  VERDICT: NO."
)
PROMPT_B = (
    "Classification task. Does the following code have a CRYPTOGRAPHIC PURPOSE (protecting "
    "confidentiality/integrity/authenticity: ciphers, secure hashes, MACs, signatures, key "
    "exchange/derivation), even if written from scratch? Plain checksums, table/hash-table hashes, "
    "ordinary PRNGs, base-N encodings, and error-correcting codes are NOT cryptographic. "
    "End your reply with a line: VERDICT: YES or VERDICT: NO."
)


def ask(model, prompt, code):
    for attempt in range(4):
        try:
            r = client.messages.create(model=model, max_tokens=500, system=prompt,
                                       messages=[{"role": "user", "content": f"```\n{code}\n```"}])
            txt = "".join(b.text for b in r.content if b.type == "text")
            v = txt.upper().rsplit("VERDICT:", 1)[-1].strip()[:4] if "VERDICT:" in txt.upper() else ""
            return ("YES" in v), txt.strip().replace("\n", " ")[-200:]
        except Exception as e:
            time.sleep(2 ** attempt); last = str(e)
    return None, f"API_ERROR:{last}"


def main():
    man = list(csv.DictReader((ROOT / "corpus/manifest.csv").open()))
    labelable = [r for r in man if r.get("tier") == "5" and r.get("is_crypto") in ("true", "false")
                 and not r.get("compose_group")]
    out_path = ROOT / "results/tier5_labels.json"
    out = json.loads(out_path.read_text()) if out_path.exists() else {}  # incremental: keep prior labels
    todo = [r for r in labelable if Path(r["filepath"]).name not in out]
    print(f"{len(out)} already labeled; labeling {len(todo)} new fixtures", file=sys.stderr)
    for i, r in enumerate(todo, 1):
        code = (ROOT / r["filepath"]).read_text(errors="ignore")
        a, ar = ask(MODEL_A, PROMPT_A, code)
        b, br = ask(MODEL_B, PROMPT_B, code)
        name = Path(r["filepath"]).name
        out[name] = {"a": a, "b": b, "a_reason": ar, "b_reason": br}
        agree = "=" if a == b else "≠ DISAGREE"
        print(f"[{i}/{len(todo)}] {name:32} a={a} b={b} {agree}", file=sys.stderr)
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results/tier5_labels.json").write_text(json.dumps(out, indent=2))
    dis = [n for n, v in out.items() if v["a"] != v["b"]]
    print(f"\nlabeled {len(out)} fixtures; {len(dis)} disagreements -> adjudication: {dis}", file=sys.stderr)


if __name__ == "__main__":
    main()
