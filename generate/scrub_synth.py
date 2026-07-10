"""
scrub_synth.py — comment-leak hygiene for AUTHORED hand-rolled fixtures (tier 4 + negatives).

The wedge measures whether a detector finds crypto from CODE STRUCTURE, not from a comment that
names the algorithm. A tier-4 comment saying "Rabin cryptosystem" lets the signature baseline score
a free hit (understating the wedge) and hands the LLM the answer; a negative's "…not cryptographic"
disclaimer tells the model the answer (inflating precision). This strips comments and neutralizes
algorithm names inside string literals for those two tiers, in place and idempotently.

NOT scrubbed: tier 0/1 (idiomatic library code — naming a library algorithm is correct there) and
tier 2 public (verbatim provenance must be preserved). tier 2-novel / tier 3 are handled by mutate.py.

Usage:  python generate/scrub_synth.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mutate import LANG_BY_EXT, neutralize_strings, strip_comments

ROOT = Path(__file__).resolve().parent.parent
DIRS = ["corpus/tier4_handrolled_novel", "corpus/_dev/tier4_handrolled_novel",
        "corpus/negatives", "corpus/_dev/negatives"]


def main() -> None:
    n = 0
    for d in DIRS:
        for f in sorted((ROOT / d).glob("*")):
            lang = LANG_BY_EXT.get(f.suffix)
            if not f.is_file() or not lang:
                continue
            before = f.read_text(errors="ignore")
            after = strip_comments(neutralize_strings(before, lang), lang)
            if after != before:
                f.write_text(after)
                n += 1
    print(f"scrubbed {n} authored fixtures (tier4 + negatives)")


if __name__ == "__main__":
    main()
