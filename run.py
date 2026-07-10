"""
Orchestrator: run a detector over the corpus and write results/<detector>.jsonl

  python run.py --detector regex     # signature baseline (offline, free)
  python run.py --detector sonar     # REAL incumbent: IBM Sonar Cryptography plugin (needs Docker)
  python run.py --detector llm       # LLM semantic detector (needs ANTHROPIC_API_KEY)
  python run.py --detector hybrid    # regex prescreen + LLM merged
  python run.py --detector all       # regex + llm + hybrid (sonar run separately; heavy toolchain)

Add --corpus PATH to point at a different corpus dir (default: corpus).
"""
import argparse, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "detectors"))

# detector -> script path (relative to repo root)
SCRIPTS = {
    "regex": "detectors/regex_baseline.py",
    "sonar": "detectors/sonar_baseline/run_sonar.py",
    "llm": "detectors/llm_detector.py",
    "hybrid": "detectors/hybrid_detector.py",
}

def run_one(name, corpus):
    out = Path(f"results/{name}.jsonl")
    out.parent.mkdir(exist_ok=True)
    print(f"[run] {name} over {corpus} -> {out}")
    with out.open("w") as fh:
        subprocess.run([sys.executable, SCRIPTS[name], corpus], stdout=fh, check=True)
    print(f"[done] {name}: {sum(1 for _ in out.open())} findings")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--detector", required=True, choices=["regex", "sonar", "llm", "hybrid", "all"])
    ap.add_argument("--corpus", default="corpus")
    a = ap.parse_args()
    names = ["regex", "llm", "hybrid"] if a.detector == "all" else [a.detector]
    for n in names:
        run_one(n, a.corpus)
