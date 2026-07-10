"""
calibration.py — is the LLM's reported confidence trustworthy?

Buckets scored findings by reported `confidence` and measures EMPIRICAL accuracy per bucket. A
well-calibrated detector has accuracy ≈ mean-confidence in every bucket; the gap is calibration
error. This is what lets the hybrid detector set a TRUST/VERIFY threshold: above some confidence its
crypto flags are precise enough to auto-trust, below it they must be deterministically verified.

Two views:
  1. Reliability bins (fixed width 0.1): n, mean confidence, accuracy(pred==truth), gap. Reported with
     ECE (expected calibration error, support-weighted mean gap) and MCE (max gap).
  2. Positive-flag precision by confidence + a trust-threshold hint: the lowest confidence above which
     is_crypto=TRUE flags reach the target precision (default 0.98) — the number the hybrid needs.

Only binary-scored fixtures count (manifest is_crypto true/false; review/unsupported excluded, and
findings with a null/no-verdict is_crypto are skipped). Writes results/calibration.json.

Usage:  python eval/calibration.py [detector...]   (default: llm hybrid)
"""
import csv, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(det):
    man = {r["filepath"]: r for r in csv.DictReader((ROOT / "corpus/manifest.csv").open())}
    fin = {}
    p = ROOT / f"results/{det}.jsonl"
    if not p.exists():
        return None
    for line in p.read_text().splitlines():
        if line.strip():
            d = json.loads(line); fin[d["filepath"]] = d
    rows = []  # (confidence, correct, pred, truth)
    for fp, m in man.items():
        if m["is_crypto"] not in ("true", "false"):
            continue
        f = fin.get(fp)
        if not f or f.get("is_crypto") is None:
            continue
        c = f.get("confidence")
        if not isinstance(c, (int, float)):
            continue
        pred, truth = bool(f.get("is_crypto")), m["is_crypto"] == "true"
        rows.append((float(c), pred == truth, pred, truth))
    return rows


def calibrate(rows, nbins=10):
    bins = []
    N = len(rows)
    ece = mce = 0.0
    for i in range(nbins):
        lo, hi = i / nbins, (i + 1) / nbins
        b = [r for r in rows if (lo <= r[0] < hi) or (hi == 1.0 and r[0] == 1.0)]
        if not b:
            bins.append({"lo": round(lo, 2), "hi": round(hi, 2), "n": 0,
                         "mean_conf": None, "accuracy": None, "gap": None})
            continue
        mc = sum(r[0] for r in b) / len(b)
        acc = sum(1 for r in b if r[1]) / len(b)
        gap = abs(acc - mc)
        ece += (len(b) / N) * gap
        mce = max(mce, gap)
        bins.append({"lo": round(lo, 2), "hi": round(hi, 2), "n": len(b),
                     "mean_conf": round(mc, 3), "accuracy": round(acc, 3), "gap": round(gap, 3)})
    return bins, round(ece, 4), round(mce, 4)


def positive_flag_precision(rows, nbins=10, target=0.98):
    """Precision of is_crypto=TRUE flags per confidence bin + the trust threshold for `target`."""
    pos = [r for r in rows if r[2]]  # pred == True
    by = []
    for i in range(nbins):
        lo, hi = i / nbins, (i + 1) / nbins
        b = [r for r in pos if (lo <= r[0] < hi) or (hi == 1.0 and r[0] == 1.0)]
        if b:
            prec = sum(1 for r in b if r[3]) / len(b)  # truth==True among positive flags
            by.append({"lo": round(lo, 2), "hi": round(hi, 2), "n": len(b), "precision": round(prec, 3)})
    # lowest threshold T such that flags with conf >= T have precision >= target
    thr = None
    for r in sorted(pos, key=lambda x: x[0]):
        above = [p for p in pos if p[0] >= r[0]]
        if above and sum(1 for p in above if p[3]) / len(above) >= target:
            thr = round(r[0], 3); break
    return {"n_positive_flags": len(pos), "target_precision": target,
            "trust_threshold": thr, "by_conf": by}


def main(dets):
    out = {}
    for det in dets:
        rows = load(det)
        if not rows:
            continue
        bins, ece, mce = calibrate(rows)
        out[det] = {"n_scored": len(rows), "ece": ece, "mce": mce, "bins": bins,
                    "positive_flags": positive_flag_precision(rows),
                    "reading": ("well-calibrated" if ece < 0.05 else
                                "over-confident" if sum(r[0] for r in rows) / len(rows) >
                                sum(1 for r in rows if r[1]) / len(rows) else "under-confident")}
    (ROOT / "results/calibration.json").write_text(json.dumps(out, indent=2))
    for det, c in out.items():
        print(f"\n=== {det} calibration (n={c['n_scored']}, ECE={c['ece']}, MCE={c['mce']}, {c['reading']}) ===")
        print(f"{'conf bin':<12}{'n':>5}{'mean_conf':>11}{'accuracy':>10}{'gap':>7}")
        for b in c["bins"]:
            if b["n"]:
                print(f"[{b['lo']:.1f},{b['hi']:.1f}){b['n']:>6}{b['mean_conf']:>11}{b['accuracy']:>10}{b['gap']:>7}")
        pf = c["positive_flags"]
        print(f"positive-flag trust threshold (>= {pf['target_precision']} precision): "
              f"conf >= {pf['trust_threshold']}")
    print("\nwrote results/calibration.json")


if __name__ == "__main__":
    main(sys.argv[1:] or ["llm", "hybrid"])
