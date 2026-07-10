"""
detect_incremental.py — append findings for NEW manifest files only (avoids re-running detectors
over unchanged fixtures). The existing 332 fixtures are byte-identical to the last run, so their
findings in results/<det>.jsonl remain valid; only newly-added files need scoring.

Usage (from repo root, with the venv + ANTHROPIC_API_KEY for llm/hybrid):
    python eval/detect_incremental.py regex llm hybrid
"""
import csv, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "detectors"))
import regex_baseline  # noqa: E402


def have(path):
    p = Path(path)
    return {json.loads(l)["filepath"] for l in p.read_text().splitlines() if l.strip()} if p.exists() else set()


def main(dets):
    man = [r["filepath"] for r in csv.DictReader(open("corpus/manifest.csv"))]
    raw = Path("results/raw"); raw.mkdir(parents=True, exist_ok=True)
    llm = None
    if any(d in ("llm", "hybrid") for d in dets):
        import llm_detector as llm
    for det in dets:
        path = f"results/{det}.jsonl"
        todo = [fp for fp in man if fp not in have(path)]
        print(f"{det}: {len(todo)} new files to score")
        with open(path, "a") as fh:
            for fp in todo:
                text = Path(fp).read_text(errors="ignore")
                name = Path(fp).name
                if det == "regex":
                    out = regex_baseline.scan(text)
                elif det == "llm":
                    out = llm.analyze(text, raw, name)
                else:  # hybrid: signature OR llm, keep higher-confidence attribution
                    sig = regex_baseline.scan(text)
                    lm = llm.analyze(text, raw, name)
                    sh, lh = bool(sig["is_crypto"]), bool(lm.get("is_crypto"))
                    primary = sig if sig["confidence"] >= (lm.get("confidence") or 0) else lm
                    out = {"is_crypto": sh or lh, "primary_algorithm": primary.get("primary_algorithm"),
                           "family": primary.get("family"), "quantum_vulnerable": primary.get("quantum_vulnerable", "na"),
                           "evidence": primary.get("evidence"),
                           "confidence": max(sig["confidence"], lm.get("confidence") or 0),
                           "fired_by": ("both" if sh and lh else "signature" if sh else "llm" if lh else "neither")}
                out["filepath"] = fp
                fh.write(json.dumps(out) + "\n")


if __name__ == "__main__":
    main(sys.argv[1:] or ["regex", "llm", "hybrid"])
