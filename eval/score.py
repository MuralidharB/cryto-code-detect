"""
Score detector output against the frozen manifest.

Reads corpus/manifest.csv (ground truth) and results/<detector>.jsonl (findings), aligns by
filepath, and computes binary is_crypto precision/recall/F1 per tier and per split, with bootstrap
95% CIs. Writes results/scores.json.

The scorer is mechanical and label-blind: it only compares is_crypto against the manifest. It never
sees tier/split while a detector runs (detectors don't receive the manifest), preserving the guard
that nobody tuned to the labels.
"""
import csv, json, sys, random, statistics
from pathlib import Path
from collections import defaultdict

def load_manifest(p="corpus/manifest.csv"):
    rows = {}
    with open(p) as f:
        for r in csv.DictReader(f):
            rows[r["filepath"]] = r
    return rows

def load_findings(p):
    out = {}
    for line in Path(p).read_text().splitlines():
        if line.strip():
            d = json.loads(line)
            out[d["filepath"]] = d
    return out

def prf(pairs):
    # pairs: list of (truth_bool, pred_bool)
    tp = sum(1 for t, p in pairs if t and p)
    fp = sum(1 for t, p in pairs if not t and p)
    fn = sum(1 for t, p in pairs if t and not p)
    prec = tp / (tp + fp) if tp + fp else None
    rec = tp / (tp + fn) if tp + fn else None
    f1 = (2 * prec * rec / (prec + rec)) if prec and rec else None
    return {"tp": tp, "fp": fp, "fn": fn, "precision": prec, "recall": rec, "f1": f1, "n": len(pairs)}

def bootstrap_recall(pairs, iters=2000):
    pos = [p for t, p in pairs if t]
    if not pos:
        return None
    samples = []
    for _ in range(iters):
        s = [random.choice(pos) for _ in pos]
        samples.append(sum(s) / len(s))
    samples.sort()
    lo, hi = samples[int(0.025 * iters)], samples[int(0.975 * iters)]
    return [round(lo, 3), round(hi, 3)]

def _norm(s):
    import re
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def _algo_match(truth, pred):
    t, p = _norm(truth), _norm(pred)
    return bool(t) and (t in p or p in t or (len(t) >= 3 and t[:3] == p[:3]))


def tier5_metrics(man, fin):
    """Tier-5 reports THREE diverging numbers + decoy precision + compose file-vs-group recall.

    Per the tier-5 spec: is_crypto recall, family accuracy, and algorithm accuracy (the last only on
    the recognizable subset, expect_algorithm_match=true). They diverge, and the divergence is the finding."""
    rows = {fp: r for fp, r in man.items() if r.get("tier") == "5"}
    if not rows:
        return None
    pos = [(fp, r) for fp, r in rows.items() if r["is_crypto"] == "true"]
    def flagged(fp):
        f = fin.get(fp)
        return bool(f and f.get("is_crypto"))
    detected = [(fp, r) for fp, r in pos if flagged(fp)]
    is_crypto_recall = len(detected) / len(pos) if pos else None
    fam_ok = sum(1 for fp, r in detected if _norm(fin[fp].get("family")) == _norm(r["family"]))
    fam_acc = fam_ok / len(detected) if detected else None
    reco = [(fp, r) for fp, r in detected if r.get("expect_algorithm_match") == "true"]
    algo_ok = sum(1 for fp, r in reco if _algo_match(r["primary_algorithm"], fin[fp].get("primary_algorithm")))
    algo_acc = algo_ok / len(reco) if reco else None
    # per-subclass is_crypto recall (which subclass broke it)
    from collections import defaultdict
    sub = defaultdict(lambda: [0, 0])
    for fp, r in pos:
        sub[r.get("subclass", "?")][1] += 1
        sub[r.get("subclass", "?")][0] += int(flagged(fp))
    by_sub = {s: {"recall": h / n if n else None, "n": n} for s, (h, n) in sorted(sub.items())}
    # decoys (is_crypto=false, subclass=decoy): over-flag rate
    decoys = [fp for fp, r in rows.items() if r["is_crypto"] == "false" and r.get("subclass") == "decoy"]
    decoy_fp = sum(1 for fp in decoys if flagged(fp))
    # compose groups: file-level vs group-level recall (group detected if ANY member flagged)
    groups = defaultdict(list)
    for fp, r in rows.items():
        if r.get("compose_group"):
            groups[r["compose_group"]].append(fp)
    file_lvl = [flagged(fp) for m in groups.values() for fp in m]
    grp_lvl = [any(flagged(fp) for fp in m) for m in groups.values()]
    return {
        "is_crypto_recall": is_crypto_recall, "n_positive": len(pos),
        "family_accuracy": fam_acc, "algorithm_accuracy_recognizable": algo_acc, "n_recognizable": len(reco),
        "by_subclass_recall": by_sub,
        "decoys": {"n": len(decoys), "false_positives": decoy_fp,
                   "precision_fp_rate": decoy_fp / len(decoys) if decoys else None},
        "compose_groups": {"n_groups": len(groups),
                           "file_level_recall": sum(file_lvl) / len(file_lvl) if file_lvl else None,
                           "group_level_recall": sum(grp_lvl) / len(grp_lvl) if grp_lvl else None},
    }


def score(detector):
    man = load_manifest()
    fin = load_findings(f"results/{detector}.jsonl")
    by_tier, by_split, overall = defaultdict(list), defaultdict(list), []
    missing = []
    review = {"n": 0, "flagged": 0}  # crypto_adjacent_review (PRNGs): excluded from binary, reported apart
    not_covered = 0  # detector gave NO verdict (is_crypto=null), e.g. Sonar unsupported-language/not-run
    for fp, row in man.items():
        ic = row["is_crypto"].strip().lower()
        f = fin.get(fp)
        if f is None:
            missing.append(fp); continue
        if f.get("is_crypto") is None:  # no-verdict finding — do not score as a miss
            not_covered += 1; continue
        pred = bool(f.get("is_crypto"))
        if ic == "review":  # not scored as crypto or non-crypto; only surfaced for review
            review["n"] += 1
            review["flagged"] += int(pred)
            continue
        truth = ic == "true"
        pair = (truth, pred)
        overall.append(pair)
        by_tier[row["tier"]].append(pair)
        by_split[row["split"]].append(pair)
    result = {
        "detector": detector,
        "overall": prf(overall),
        "by_tier": {t: {**prf(v), "recall_ci95": bootstrap_recall(v)} for t, v in sorted(by_tier.items())},
        "by_split": {s: {**prf(v), "recall_ci95": bootstrap_recall(v)} for s, v in sorted(by_split.items())},
        "crypto_adjacent_review": {**review, "surfaced_rate": (review["flagged"] / review["n"]) if review["n"] else None},
        "not_covered": not_covered,  # no-verdict findings (Sonar unsupported-language / not-run)
        "coverage": round(len(overall) / (len(overall) + not_covered), 3) if (len(overall) + not_covered) else None,
        "files_missing_from_findings": missing,
    }
    t5 = tier5_metrics(man, fin)
    if t5:
        result["tier5"] = t5
    return result

if __name__ == "__main__":
    detectors = sys.argv[1:] or ["regex", "llm", "hybrid"]
    all_scores = {}
    for d in detectors:
        if Path(f"results/{d}.jsonl").exists():
            all_scores[d] = score(d)
    Path("results/scores.json").write_text(json.dumps(all_scores, indent=2))
    # console summary: the miss-rate-by-tier table, which is the wedge sizing
    print(f"{'tier':<6}" + "".join(f"{d+' recall':<18}" for d in all_scores))
    tiers = sorted({t for s in all_scores.values() for t in s["by_tier"]})
    for t in tiers:
        line = f"{t:<6}"
        for d in all_scores:
            r = all_scores[d]["by_tier"].get(t, {}).get("recall")
            line += f"{(f'{r:.2f}' if r is not None else '-'):<18}"
        print(line)
    print("\nwrote results/scores.json")
