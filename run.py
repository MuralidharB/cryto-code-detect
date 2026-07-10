"""
Orchestrator: run a detector over the corpus and write results/<detector>.jsonl

  python run.py --detector regex     # signature baseline (offline, free)
  python run.py --detector llm       # LLM semantic detector (needs ANTHROPIC_API_KEY)
  python run.py --detector hybrid    # regex prescreen + LLM merged
  python run.py --detector all       # all three

Add --corpus PATH to point at a different corpus dir (default: corpus).
"""
import argparse, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "detectors"))

def run_one(name, corpus):
    module = {"regex": "regex_baseline", "llm": "llm_detector", "hybrid": "hybrid_detector"}[name]
    out = Path(f"results/{name}.jsonl")
    out.parent.mkdir(exist_ok=True)
    print(f"[run] {name} over {corpus} -> {out}")
    with out.open("w") as fh:
        subprocess.run([sys.executable, f"detectors/{module}.py", corpus], stdout=fh, check=True)
    print(f"[done] {name}: {sum(1 for _ in out.open())} findings")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--detector", required=True, choices=["regex", "llm", "hybrid", "all"])
    ap.add_argument("--corpus", default="corpus")
    a = ap.parse_args()
    names = ["regex", "llm", "hybrid"] if a.detector == "all" else [a.detector]
    for n in names:
        run_one(n, a.corpus)
