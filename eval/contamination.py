"""
Contamination analysis — the guard that keeps LLM numbers honest.

Two outputs:

1. CONTAMINATION DELTA: LLM recall on `public` (possibly-memorised) crypto minus recall on
   `novel` (un-memorisable) crypto, ideally at matched difficulty. A large positive delta means
   public-split accuracy is inflated by memorisation and you must report only the novel-split number.

2. MEMORISATION CANARY: for each `public` fixture, show the model the first few lines and ask it to
   continue. High verbatim overlap with the real continuation is direct evidence the file is in the
   model's training data — i.e. that fixture's detection result can't be trusted as "generalisation".

Run after results/<detector>.jsonl exists. Writes results/contamination.json.

Usage:
    python eval/contamination.py                      # default: analyse results/llm.jsonl
    python eval/contamination.py --detector regex     # analyse a different detector's output
    python eval/contamination.py --canary             # also run the memorisation canary (needs API)

The contamination delta is only a meaningful CAPABILITY claim for the LLM detector; running it on
the regex baseline is a useful SANITY CHECK — a non-memorising detector should show a ~0 delta.
"""
import argparse, csv, json, os, sys, difflib
from pathlib import Path
from collections import defaultdict

def load_manifest(p="corpus/manifest.csv"):
    with open(p) as f:
        return {r["filepath"]: r for r in csv.DictReader(f)}

def load_findings(p="results/llm.jsonl"):
    out = {}
    for line in Path(p).read_text().splitlines():
        if line.strip():
            d = json.loads(line); out[d["filepath"]] = d
    return out

def recall_by_split(man, fin, tier=None):
    agg = defaultdict(lambda: [0, 0])  # split -> [hits, positives]
    for fp, row in man.items():
        if row["is_crypto"].strip().lower() != "true":
            continue
        if tier is not None and row["tier"] != tier:
            continue
        f = fin.get(fp)
        if not f:
            continue
        agg[row["split"]][1] += 1
        if f.get("is_crypto"):
            agg[row["split"]][0] += 1
    return {s: (h / n if n else None, n) for s, (h, n) in agg.items()}

def canary(man, n_lines=4, max_files=20):
    """Probe memorisation by asking the model to continue public fixtures from a prefix."""
    try:
        from anthropic import Anthropic
    except ImportError:
        return {"skipped": "anthropic not installed"}
    client = Anthropic()
    model = os.environ.get("BENCH_MODEL", "claude-sonnet-4-6")
    results = {}
    pubs = [fp for fp, r in man.items() if r["split"] == "public" and r["is_crypto"].lower() == "true"]
    for fp in pubs[:max_files]:
        text = Path(fp).read_text(errors="ignore")
        lines = text.splitlines()
        if len(lines) <= n_lines:
            continue
        prefix, real = "\n".join(lines[:n_lines]), "\n".join(lines[n_lines:])
        try:
            resp = client.messages.create(
                model=model, max_tokens=300,
                system="Continue this source file exactly as you believe it appears. Output only code.",
                messages=[{"role": "user", "content": f"```\n{prefix}\n```"}],
            )
            guess = "".join(b.text for b in resp.content if b.type == "text")
            ratio = difflib.SequenceMatcher(None, guess, real).ratio()
            results[fp] = round(ratio, 3)  # ~>0.6 strongly suggests memorisation
        except Exception as e:
            results[fp] = f"error:{e}"
    return results

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--detector", default="llm")
    ap.add_argument("--canary", action="store_true")
    a = ap.parse_args()
    man, fin = load_manifest(), load_findings(f"results/{a.detector}.jsonl")
    rbs = recall_by_split(man, fin)

    # MATCHED-DIFFICULTY delta: only compare public vs novel WITHIN tiers that contain both, so a
    # difficulty imbalance between the splits cannot masquerade as contamination (see README: the
    # delta must be measured at matched difficulty). Tier 2 is built with matched public/novel pairs.
    matched = {}
    for t in sorted({row["tier"] for row in man.values()}):
        rt = recall_by_split(man, fin, tier=t)
        if "public" in rt and "novel" in rt:
            p, n = rt["public"][0], rt["novel"][0]
            matched[t] = {"public": rt["public"], "novel": rt["novel"], "delta": round(p - n, 4)}
    matched_deltas = [m["delta"] for m in matched.values()]
    matched_delta = round(sum(matched_deltas) / len(matched_deltas), 4) if matched_deltas else None

    pub = rbs.get("public", (None,))[0]
    nov = rbs.get("novel", (None,))[0]
    delta = (pub - nov) if (pub is not None and nov is not None) else None
    out = {
        "recall_by_split": {s: {"recall": r, "n": n} for s, (r, n) in rbs.items()},
        "contamination_delta_public_minus_novel_AGGREGATE": delta,
        "aggregate_warning": ("AGGREGATE delta conflates contamination with difficulty imbalance "
                              "between splits; use the matched-difficulty delta below for any claim."),
        "matched_difficulty_by_tier": {t: {"public_recall": m["public"][0], "n_public": m["public"][1],
                                           "novel_recall": m["novel"][0], "n_novel": m["novel"][1],
                                           "delta": m["delta"]} for t, m in matched.items()},
        "contamination_delta_matched_difficulty": matched_delta,
        "reading": ("report NOVEL-split recall as the true capability; public is inflated"
                    if (matched_delta or 0) > 0.05 else "public and novel comparable at matched "
                    "difficulty — low contamination"),
        "detector": a.detector,
        "memorisation_canary_overlap": canary(man) if a.canary else "pass --canary to run",
    }
    Path("results/contamination.json").write_text(json.dumps(out, indent=2))
    print(json.dumps({k: v for k, v in out.items() if k != "memorisation_canary_overlap"}, indent=2))
    print("\nwrote results/contamination.json")
