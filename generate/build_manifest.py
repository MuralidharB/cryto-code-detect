"""
build_manifest.py — write corpus/manifest.csv, the FROZEN ground truth, from three label sources:

  1. PUBLIC_SEED   — verbatim public fixtures (fetch_public.py), labelled here with a source URL.
  2. mutate.DERIVATIONS — each novel fixture inherits its seed's algorithm label; tier comes from
     the mutation level (light -> tier 2 matched-difficulty, heavy -> tier 3 obfuscated).
  3. synth_specs.SYNTH  — authored fixtures; labels were fixed by us at spec time, never by the
     author-agents and never by a detector.

Ground truth is honest by construction (we generated/sourced every fixture). Per CLAUDE.md:
regenerate the manifest FIRST, then run detectors; never edit a label to match detector output.

It also owns the dev/test split (idempotent, path-based): ~20% per tier held out under corpus/_dev/,
NEVER a mutation seed (so re-running fetch->mutate->build stays correct).

Columns: filepath,language,is_crypto,primary_algorithm,family,quantum_vulnerable,tier,split,source,notes
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mutate          # for DERIVATIONS (novel) and SEEDS (protected from dev)
import synth_specs     # for SYNTH (authored labels)
import tier5_specs     # for T5 (tier-5 authored labels + metadata)

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "corpus"
TIER_DIR = {
    "0": "tier0_library_idiomatic", "1": "tier1_library_indirect", "2": "tier2_handrolled_textbook",
    "3": "tier3_handrolled_obfuscated", "4": "tier4_handrolled_novel", "neg": "negatives",
    "5": "tier5_unrecognizable",
}
EXT_LANG = {".py": "python", ".c": "c", ".h": "c", ".go": "go", ".java": "java",
            ".sql": "sql", ".sh": "shell", ".awk": "awk"}
# tier-5 extra columns (empty for tiers 0-4/neg so the CSV stays rectangular)
T5_COLS = ["subclass", "label_rationale", "expect_algorithm_match", "compose_group", "labeler_a", "labeler_b"]
LABELS_FILE = ROOT / "results/tier5_labels.json"
A, S, H = "asymmetric", "symmetric", "hash"
RC = "https://rosettacode.org/wiki/{}"
GH = "https://raw.githubusercontent.com/{}"

# basename -> (algo, family, quantum_vulnerable, tier, source_url). The 17 tier-2 entries are also the
# mutation seeds, so the novel split inherits these algorithm labels.
PUBLIC_SEED = {
    # tier 0 (idiomatic library)
    "sha1_hashlib.py": ("SHA-1", H, "no", "0", RC.format("SHA-1")),
    "sha256_stdlib.go": ("SHA-256", H, "no", "0", RC.format("SHA-256")),
    "sha1_openssl.c": ("SHA-1", H, "no", "0", RC.format("SHA-1")),
    "Md4Bouncy.java": ("MD4", H, "no", "0", RC.format("MD4")),
    "md4_xcrypto.go": ("MD4", H, "no", "0", RC.format("MD4")),
    "aes_gcm_examples.go": ("AES-GCM", S, "no", "0", GH.format("golang/go/master/src/crypto/cipher/example_test.go")),
    # tier 2 (hand-rolled textbook) — the mutation seeds
    "rsa_textbook.py": ("RSA", A, "yes", "2", RC.format("RSA_code")),
    "rsa_textbook.c": ("RSA", A, "yes", "2", RC.format("RSA_code")),
    "rsa_textbook.go": ("RSA", A, "yes", "2", RC.format("RSA_code")),
    "RsaTextbook.java": ("RSA", A, "yes", "2", RC.format("RSA_code")),
    "md5_scratch.py": ("MD5", H, "no", "2", RC.format("MD5/Implementation")),
    "md5_scratch.go": ("MD5", H, "no", "2", RC.format("MD5/Implementation")),
    "Sha1Scratch.java": ("SHA-1", H, "no", "2", RC.format("SHA-1")),
    "Sha256Scratch.java": ("SHA-256", H, "no", "2", RC.format("SHA-256")),
    "md4_scratch.c": ("MD4", H, "no", "2", RC.format("MD4")),
    "sha256_bcon.c": ("SHA-256", H, "no", "2", GH.format("B-Con/crypto-algorithms/master/sha256.c")),
    "des_bcon.c": ("DES", S, "no", "2", GH.format("B-Con/crypto-algorithms/master/des.c")),
    "aes_bcon.c": ("AES", S, "no", "2", GH.format("B-Con/crypto-algorithms/master/aes.c")),
    "rc4_bcon.c": ("RC4", S, "no", "2", GH.format("B-Con/crypto-algorithms/master/arcfour.c")),
    "blowfish_bcon.c": ("Blowfish", S, "no", "2", GH.format("B-Con/crypto-algorithms/master/blowfish.c")),
    "md2_bcon.c": ("MD2", H, "no", "2", GH.format("B-Con/crypto-algorithms/master/md2.c")),
    "md5_bcon.c": ("MD5", H, "no", "2", GH.format("B-Con/crypto-algorithms/master/md5.c")),
    "sha1_bcon.c": ("SHA-1", H, "no", "2", GH.format("B-Con/crypto-algorithms/master/sha1.c")),
}
PROTECTED = set(mutate.SEEDS)  # never move these to _dev (mutate reads them in place)


def make_labels() -> dict[str, dict]:
    """basename -> label row (without filepath/language, filled at placement)."""
    L: dict[str, dict] = {}
    for name, (algo, fam, qv, tier, url) in PUBLIC_SEED.items():
        L[name] = dict(is_crypto="true", algo=algo, fam=fam, qv=qv, tier=tier, split="public",
                       source=url, note="verbatim public seed")
    for seed_rel, dest_rel, level in mutate.DERIVATIONS:
        sb = Path(seed_rel).name
        algo, fam, qv, _t, _u = PUBLIC_SEED[sb]
        tier = "2" if level == "light" else "3"
        L[Path(dest_rel).name] = dict(is_crypto="true", algo=algo, fam=fam, qv=qv, tier=tier,
                                      split="novel", source=f"derived:{sb}", note=f"{level} mutation")
    for s in synth_specs.SYNTH:
        ic = s["is_crypto"]
        ic_str = "review" if ic == "review" else ("true" if ic else "false")
        L[Path(s["path"]).name] = dict(is_crypto=ic_str, algo=s["algo"], fam=s["family"], qv=s["qv"],
                                       tier=s["tier"], split="synth", source="authored", note=s["hint"])
    for r in tier5_specs.T5:
        ic = r["is_crypto"]
        ic_str = "review" if ic == "review" else ("true" if ic else "false")
        src = f"derived:{r['algo']}" if r["split"] == "novel" else "authored"
        L[Path(r["path"]).name] = dict(
            is_crypto=ic_str, algo=r["algo"], fam=r["family"], qv=r["qv"], tier="5", split=r["split"],
            source=src, note=r["rationale"],
            subclass=str(r["subclass"]), label_rationale=r["rationale"],
            expect_algorithm_match=("true" if r["expect_algo"] else "false"),
            compose_group=r["compose_group"])
    return L


def choose_dev(labels: dict[str, dict]) -> set[str]:
    """~20% per tier held out, deterministic, skipping protected mutation seeds."""
    by_tier: dict[str, list[str]] = {}
    for name, lab in labels.items():
        by_tier.setdefault(lab["tier"], []).append(name)
    dev = set()
    for tier, names in by_tier.items():
        # never hold out a mutation seed, and keep compose_group members together in test
        eligible = sorted(n for n in names if n not in PROTECTED and not labels[n].get("compose_group"))
        dev.update(eligible[::5])  # every 5th -> ~20%
    return dev


def canonical_path(name: str, tier: str, dev: set[str]) -> Path:
    return CORPUS / ("_dev" if name in dev else ".") / TIER_DIR[tier] / name


def locate_and_place(name: str, tier: str, dev: set[str]) -> Path | None:
    canon = canonical_path(name, tier, dev)
    other = (CORPUS / TIER_DIR[tier] / name) if name in dev else (CORPUS / "_dev" / TIER_DIR[tier] / name)
    if canon.exists():
        if other.exists() and other != canon:
            other.unlink()  # self-heal a test/_dev duplicate; canonical copy wins
        return canon
    if other.exists():
        canon.parent.mkdir(parents=True, exist_ok=True)
        other.replace(canon)
        return canon
    return None


def load_blind_labels() -> dict:
    """Optional {basename: {"a": bool, "b": bool}} from the two-labeler pass (results/tier5_labels.json)."""
    if LABELS_FILE.exists():
        return json.loads(LABELS_FILE.read_text())
    return {}


def main() -> int:
    labels = make_labels()
    dev = choose_dev(labels)
    blind = load_blind_labels()
    rows, missing, adjudicated = [], [], []
    for name, lab in labels.items():
        la = blind.get(name, {})
        a, b = la.get("a"), la.get("b")
        # Agreement gate (tier 5 only): scored fixtures need labeler_a == labeler_b on is_crypto.
        # Exempt: review items (not binary) and compose_group files (labelled by construction).
        disagree = (lab["tier"] == "5" and lab["is_crypto"] != "review" and not lab.get("compose_group")
                    and a is not None and b is not None and a != b)
        if disagree:
            adj = CORPUS / TIER_DIR["5"] / "_adjudication" / name
            src = locate_and_place(name, lab["tier"], dev)  # None if already in _adjudication
            if src is not None:
                adj.parent.mkdir(parents=True, exist_ok=True)
                src.replace(adj)
            adjudicated.append(name)
            continue
        path = locate_and_place(name, lab["tier"], dev)
        if path is None:
            missing.append(name)
            continue
        row = {
            "filepath": path.relative_to(ROOT).as_posix(),
            "language": EXT_LANG[path.suffix],
            "is_crypto": lab["is_crypto"], "primary_algorithm": lab["algo"], "family": lab["fam"],
            "quantum_vulnerable": lab["qv"], "tier": lab["tier"], "split": lab["split"],
            "source": lab["source"], "notes": lab["note"],
        }
        for c in T5_COLS:
            row[c] = lab.get(c, "")
        if a is not None:
            row["labeler_a"] = "true" if a else "false"
        if b is not None:
            row["labeler_b"] = "true" if b else "false"
        rows.append(row)

    on_disk = {p.name for p in CORPUS.rglob("*") if p.is_file() and p.name != "manifest.csv"
               and "_adjudication" not in p.parts}
    orphans = sorted(on_disk - set(labels))

    rows.sort(key=lambda r: (r["tier"], r["split"], r["filepath"]))
    out = CORPUS / "manifest.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"wrote {out.relative_to(ROOT)} : {len(rows)} scored fixtures ({len(dev)} dev held-out)")
    if adjudicated:
        print(f"moved {len(adjudicated)} tier-5 fixtures to _adjudication (labeler_a != labeler_b): {sorted(adjudicated)}")
    if missing:
        print(f"WARNING: {len(missing)} labeled fixtures missing on disk: {sorted(missing)}", file=sys.stderr)
    if orphans:
        print(f"WARNING: {len(orphans)} files on disk have NO label: {orphans}", file=sys.stderr)
    return 1 if (missing or orphans) else 0


if __name__ == "__main__":
    sys.exit(main())
