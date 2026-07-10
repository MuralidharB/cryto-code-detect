"""
Hybrid detector — the architecture argued for in the venture analysis:
deterministic base (regex/signature) + LLM semantic layer, merged.

Rule: a file is crypto if EITHER the signature baseline OR the LLM flags it. The signature layer
guarantees the easy/auditable cases deterministically; the LLM adds the hand-rolled tail. The merged
finding keeps the higher-confidence algorithm attribution and records which layer fired, so a
compliance system of record can later DETERMINISTICALLY VERIFY the LLM-only flags before trusting them.

This is what you'd actually ship; regex-only and llm-only are run separately to attribute the lift.
"""
import json, sys
from pathlib import Path
import regex_baseline, llm_detector

def main(corpus_dir):
    raw_dir = Path("results/raw"); raw_dir.mkdir(parents=True, exist_ok=True)
    for f in sorted(Path(corpus_dir).rglob("*")):
        if not (f.is_file() and f.name != "manifest.csv"):
            continue
        text = f.read_text(errors="ignore")
        sig = regex_baseline.scan(text)
        llm = llm_detector.analyze(text, raw_dir, f.name)
        sig_hit, llm_hit = bool(sig["is_crypto"]), bool(llm.get("is_crypto"))
        # prefer the layer with higher confidence for attribution detail
        primary = sig if sig["confidence"] >= (llm.get("confidence") or 0) else llm
        out = {
            "filepath": str(f),
            "is_crypto": sig_hit or llm_hit,
            "primary_algorithm": primary.get("primary_algorithm"),
            "family": primary.get("family"),
            "quantum_vulnerable": primary.get("quantum_vulnerable", "na"),
            "evidence": primary.get("evidence"),
            "confidence": max(sig["confidence"], llm.get("confidence") or 0),
            "fired_by": ("both" if sig_hit and llm_hit else "signature" if sig_hit
                         else "llm" if llm_hit else "neither"),
        }
        print(json.dumps(out))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "corpus")
