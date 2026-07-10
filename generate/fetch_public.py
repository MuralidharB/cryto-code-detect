"""
Fetch verbatim public crypto implementations for the `public` contamination split.

The `public` split must be code the model could plausibly have MEMORISED — i.e. real source that
existed publicly before the model's cutoff. We therefore pull it from the live web rather than
hand-writing it (hand-written "public" code defeats the contamination measurement, because the
model may never have seen it). Two source kinds:

  - rosetta: a RosettaCode task page, from which we extract one language's first code block. The
    same textbook algorithm appears in many languages, giving matched-difficulty fixtures across
    Python/Java/C/Go.
  - raw: a raw file URL (e.g. a famous single-file reference implementation on GitHub).

Every fixture records a stable source URL, printed (filepath<TAB>source_url<TAB>bytes) to stderr so
the manifest can be regenerated deterministically. This script only WRITES FIXTURE FILES; it never
touches corpus/manifest.csv — the manifest is authored and frozen separately (CLAUDE.md guardrails).

Usage:  python generate/fetch_public.py
"""
import html
import re
import sys
import urllib.request
from pathlib import Path

ROSETTA_RAW = "https://rosettacode.org/w/index.php?title={page}&action=raw"
ROSETTA_HUMAN = "https://rosettacode.org/wiki/{page}"
HEADER_NAME = {"python": "Python", "c": "C", "go": "Go", "java": "Java"}


def _get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "crypto-discovery-bench/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def extract_rosetta(wikitext: str, lang: str) -> str | None:
    """Return the first highlighted code block under the given language's header, verbatim."""
    header = re.escape(f"{{{{header|{HEADER_NAME[lang]}}}}}")
    m = re.search(rf"=+\s*{header}\s*=+(.*?)(?:\n=+\s*\{{\{{header\||\Z)", wikitext, re.S)
    if not m:
        return None
    section = m.group(1)
    block = re.search(r"<syntaxhighlight\b[^>]*>(.*?)</syntaxhighlight>", section, re.S) or re.search(
        r"<lang\b[^>]*>(.*?)</lang>", section, re.S
    )
    if not block:
        return None
    return html.unescape(block.group(1)).strip("\n") + "\n"


# Each seed: (kind, locator, lang_or_None, dest). Tier is implied by the destination directory.
# Classification (library-call -> tier0 idiomatic, from-scratch -> tier2 hand-rolled) was verified
# by inspecting each block; see notes in corpus/manifest.csv.
SEEDS = [
    # ---- tier 0: idiomatic library calls (verbatim public) ----
    ("rosetta", "SHA-1", "python", "corpus/tier0_library_idiomatic/sha1_hashlib.py"),
    ("rosetta", "SHA-256", "go", "corpus/tier0_library_idiomatic/sha256_stdlib.go"),
    ("rosetta", "SHA-1", "c", "corpus/tier0_library_idiomatic/sha1_openssl.c"),
    ("rosetta", "MD4", "java", "corpus/tier0_library_idiomatic/Md4Bouncy.java"),
    ("rosetta", "MD4", "go", "corpus/tier0_library_idiomatic/md4_xcrypto.go"),
    ("raw", "https://raw.githubusercontent.com/golang/go/master/src/crypto/cipher/example_test.go",
     None, "corpus/tier0_library_idiomatic/aes_gcm_examples.go"),
    # ---- tier 2: hand-rolled textbook (verbatim public; these also seed the novel split) ----
    ("rosetta", "RSA_code", "python", "corpus/tier2_handrolled_textbook/rsa_textbook.py"),
    ("rosetta", "RSA_code", "c", "corpus/tier2_handrolled_textbook/rsa_textbook.c"),
    ("rosetta", "RSA_code", "go", "corpus/tier2_handrolled_textbook/rsa_textbook.go"),
    ("rosetta", "RSA_code", "java", "corpus/tier2_handrolled_textbook/RsaTextbook.java"),
    ("rosetta", "MD5/Implementation", "python", "corpus/tier2_handrolled_textbook/md5_scratch.py"),
    ("rosetta", "MD5/Implementation", "go", "corpus/tier2_handrolled_textbook/md5_scratch.go"),
    ("rosetta", "SHA-1", "java", "corpus/tier2_handrolled_textbook/Sha1Scratch.java"),
    ("rosetta", "SHA-256", "java", "corpus/tier2_handrolled_textbook/Sha256Scratch.java"),
    ("rosetta", "MD4", "c", "corpus/tier2_handrolled_textbook/md4_scratch.c"),
    ("raw", "https://raw.githubusercontent.com/B-Con/crypto-algorithms/master/sha256.c",
     None, "corpus/tier2_handrolled_textbook/sha256_bcon.c"),
    ("raw", "https://raw.githubusercontent.com/B-Con/crypto-algorithms/master/des.c",
     None, "corpus/tier2_handrolled_textbook/des_bcon.c"),
    ("raw", "https://raw.githubusercontent.com/B-Con/crypto-algorithms/master/aes.c",
     None, "corpus/tier2_handrolled_textbook/aes_bcon.c"),
    ("raw", "https://raw.githubusercontent.com/B-Con/crypto-algorithms/master/arcfour.c",
     None, "corpus/tier2_handrolled_textbook/rc4_bcon.c"),
    ("raw", "https://raw.githubusercontent.com/B-Con/crypto-algorithms/master/blowfish.c",
     None, "corpus/tier2_handrolled_textbook/blowfish_bcon.c"),
    ("raw", "https://raw.githubusercontent.com/B-Con/crypto-algorithms/master/md2.c",
     None, "corpus/tier2_handrolled_textbook/md2_bcon.c"),
    ("raw", "https://raw.githubusercontent.com/B-Con/crypto-algorithms/master/md5.c",
     None, "corpus/tier2_handrolled_textbook/md5_bcon.c"),
    ("raw", "https://raw.githubusercontent.com/B-Con/crypto-algorithms/master/sha1.c",
     None, "corpus/tier2_handrolled_textbook/sha1_bcon.c"),
]


def source_for(kind: str, locator: str) -> str:
    return ROSETTA_HUMAN.format(page=locator) if kind == "rosetta" else locator


def main() -> None:
    cache: dict[str, str] = {}
    for kind, locator, lang, dest in SEEDS:
        if kind == "rosetta":
            if locator not in cache:
                cache[locator] = _get(ROSETTA_RAW.format(page=locator))
            code = extract_rosetta(cache[locator], lang)
        else:
            code = _get(locator)
        if not code:
            print(f"MISSING\t{kind}:{locator}:{lang}\t-> {dest}", file=sys.stderr)
            continue
        p = Path(dest)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(code)
        print(f"{dest}\t{source_for(kind, locator)}\t{len(code)}B", file=sys.stderr)


if __name__ == "__main__":
    main()
