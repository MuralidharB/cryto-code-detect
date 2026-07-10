"""
mutate.py — derive `novel` fixtures from `public` seeds for the contamination axis.

A `novel` fixture must satisfy two properties:
  1. byte-novel: the exact text never existed publicly, so the model cannot have memorised it;
  2. label-preserving: it is still a correct implementation of the SAME algorithm, so the manifest
     label carried over from the seed remains true.

To guarantee (2) we use only SEMANTICS-PRESERVING transforms, and we only ever rewrite *code*
regions — never the inside of a string or comment literal (a string/comment-aware scanner enforces
this, so e.g. an integer that appears inside a printed message is left alone).

Transforms (all reversible-in-meaning, none change behaviour):
  - rename_defs:   consistently rename the file's OWN defined symbols (functions/classes/top-level
                   vars). These are safe to rename because they are defined and used within the file.
  - rebase_ints:   rewrite integer literals between decimal and hex (5 <-> 0x5). Pure notation.
  - strip_comments:remove comments. (Whitespace/comment-only change.)
  - shuffle_imports: reorder a run of consecutive top-level import lines (order-independent).

Levels:
  - "light"  (tier-2 novel): rename_defs + rebase_ints. Keeps textbook structure & comments, so it
              is a MATCHED-DIFFICULTY counterpart to the tier-2 public seed (this is what the
              contamination delta compares — public vs novel at the same difficulty).
  - "heavy"  (tier-3 obfuscated): light + strip_comments + shuffle_imports. Same algorithm, harder
              to recognise: no comments, renamed symbols, mixed literal bases.

NOT IMPLEMENTED: cross-language translation. The README lists it as a possible mutation, but doing
it with text transforms cannot guarantee property (2) (a mistranslated cipher is a different or
broken algorithm), which would silently corrupt ground truth. We instead achieve language coverage
by sourcing seeds in multiple languages directly. Translation is left to a future, compiler-grade
implementation.

API:   mutate(text, lang, level="light", seed=0) -> str
CLI:   python generate/mutate.py    # regenerates the novel split from the tier-2 public seeds
"""
from __future__ import annotations

import random
import re
import sys
from pathlib import Path

LANG_BY_EXT = {".py": "python", ".c": "c", ".h": "c", ".go": "go", ".java": "java"}

# Tokens we must never rename even if they appear as a "definition" by our coarse rules.
KEYWORDS = {
    "python": {"def", "class", "return", "if", "else", "elif", "for", "while", "in", "and", "or",
               "not", "import", "from", "as", "with", "lambda", "True", "False", "None", "range",
               "len", "int", "str", "bytes", "print", "pow", "self", "global"},
    "go": {"func", "package", "import", "var", "const", "type", "struct", "return", "if", "else",
           "for", "range", "make", "len", "append", "byte", "int", "uint32", "uint64", "string",
           "main", "nil", "true", "false"},
    "c": {"int", "char", "void", "return", "if", "else", "for", "while", "unsigned", "static",
          "const", "struct", "typedef", "sizeof", "include", "define", "main", "long", "short"},
    "java": {"public", "private", "static", "final", "class", "void", "return", "if", "else",
             "for", "while", "new", "int", "long", "byte", "String", "import", "package", "this",
             "main", "true", "false", "null", "BigInteger"},
}


# --------------------------------------------------------------------------- scanner
def scan_spans(text: str, lang: str):
    """Yield (is_code, substring) covering text. Strings/chars/comments are is_code=False."""
    i, n = 0, len(text)
    buf = []  # accumulating code chars
    out = []

    def flush_code():
        if buf:
            out.append((True, "".join(buf)))
            buf.clear()

    line_comment = "#" if lang == "python" else "//"
    while i < n:
        c = text[i]
        two = text[i:i + 2]
        # comments
        if text.startswith(line_comment, i):
            flush_code()
            j = text.find("\n", i)
            j = n if j == -1 else j
            out.append((False, text[i:j]))
            i = j
            continue
        if lang != "python" and two == "/*":
            flush_code()
            j = text.find("*/", i + 2)
            j = n if j == -1 else j + 2
            out.append((False, text[i:j]))
            i = j
            continue
        # strings
        if lang == "python" and (text.startswith('"""', i) or text.startswith("'''", i)):
            q = text[i:i + 3]
            flush_code()
            j = text.find(q, i + 3)
            j = n if j == -1 else j + 3
            out.append((False, text[i:j]))
            i = j
            continue
        if lang == "go" and c == "`":
            flush_code()
            j = text.find("`", i + 1)
            j = n if j == -1 else j + 1
            out.append((False, text[i:j]))
            i = j
            continue
        if c in "\"'":
            flush_code()
            j = i + 1
            while j < n:
                if text[j] == "\\":
                    j += 2
                    continue
                if text[j] == c:
                    j += 1
                    break
                j += 1
            out.append((False, text[i:j]))
            i = j
            continue
        buf.append(c)
        i += 1
    flush_code()
    return out


def _map_code(text, lang, fn):
    """Apply fn to code spans only; leave string/comment spans untouched."""
    return "".join(s if not is_code else fn(s) for is_code, s in scan_spans(text, lang))


# --------------------------------------------------------------------------- transforms
DEF_PATTERNS = {
    "python": [r"\bdef\s+(\w+)", r"\bclass\s+(\w+)", r"(?m)^\s*(\w+)\s*="],
    "go": [r"\bfunc\s+(\w+)", r"\b(\w+)\s*:="],
    "c": [r"\b(\w+)\s*\([^;]*\)\s*\{"],  # function definitions (decl followed by body)
    "java": [r"\b(?:void|int|long|byte\[\]|String|BigInteger|static\s+\w+)\s+(\w+)\s*\("],
}


def _renamable(code_only: str, lang: str) -> list[str]:
    names: list[str] = []
    seen = set()
    for pat in DEF_PATTERNS.get(lang, []):
        for m in re.finditer(pat, code_only):
            name = m.group(1)
            if (name in KEYWORDS[lang]) or name in seen or len(name) < 2 or name.isupper():
                continue
            seen.add(name)
            names.append(name)
    return names


def rename_defs(text: str, lang: str, rng: random.Random) -> str:
    code_only = "".join(s for is_code, s in scan_spans(text, lang) if is_code)
    names = _renamable(code_only, lang)
    if not names:
        return text
    pool = ["v", "x", "tmp", "buf", "acc", "st", "rnd", "blk", "kx", "q", "z", "w", "h0", "r"]
    rng.shuffle(pool)
    mapping = {}
    for k, name in enumerate(names):
        mapping[name] = f"{pool[k % len(pool)]}{k}"

    def sub(code: str) -> str:
        for old, new in mapping.items():
            code = re.sub(rf"\b{re.escape(old)}\b", new, code)
        return code

    return _map_code(text, lang, sub)


def rebase_ints(text: str, lang: str, rng: random.Random, prob: float = 0.6) -> str:
    def sub(code: str) -> str:
        def repl(m: re.Match) -> str:
            tok = m.group(0)
            if rng.random() > prob:
                return tok
            try:
                val = int(tok, 16) if tok.lower().startswith("0x") else int(tok)
            except ValueError:
                return tok
            # flip representation: hex<->decimal
            return str(val) if tok.lower().startswith("0x") else hex(val)

        # integer literals not glued to an identifier (avoid foo2 -> foo0x2)
        return re.sub(r"(?<![\w.])(0[xX][0-9a-fA-F]+|\d+)(?![\w.])", repl, code)

    return _map_code(text, lang, sub)


def strip_comments(text: str, lang: str) -> str:
    line_c = "#" if lang == "python" else "//"
    out = []
    for is_code, s in scan_spans(text, lang):
        if is_code:
            out.append(s)
        elif s.startswith(line_c) or s.startswith("/*"):
            continue  # drop comment
        else:
            out.append(s)  # keep strings
    text = "".join(out)
    return re.sub(r"\n[ \t]*\n[ \t]*\n+", "\n\n", text)  # collapse blank runs left behind


# Algorithm-name tokens that must never appear in a novel fixture's STRING literals (comments are
# dropped entirely). Leaving them in would (a) let the signature baseline score a free hit from a
# printed label / #include filename and (b) hand the LLM the answer — both understate the wedge.
_NEUTRAL_RX = re.compile(
    r"\b(?:Blowfish|Twofish|Serpent|ARCFOUR|RC4|ChaCha\d*|Salsa\d*|Poly1305|Kyber|Dilithium|ElGamal|"
    r"Rabin|Paillier|Feistel|Speck|LFSR|Keccak|Merkle|Damg\w*|HMAC|CMAC|PBKDF2|scrypt|Argon2|bcrypt|"
    r"Ed25519|X25519|Curve25519|Diffie|Hellman|secp\w*|Camellia|RIPEMD|Whirlpool|BLAKE\w*|Pohlig|"
    r"Lai-?Massey|XX?TEA|RSA|AES|Rijndael|ECDSA|ECDH|MD[245]|3?DES|SHA-?\d*|cipher|encrypt\w*|"
    r"decrypt\w*|crypto\w*|digest)\b", re.I)


def neutralize_strings(text: str, lang: str) -> str:
    """Replace algorithm-name tokens INSIDE string literals with a neutral token (keeps the code
    running — only printed labels / include filenames change). Comments are handled by strip_comments."""
    def repl_span(is_code, s):
        if is_code:
            return s
        if s.startswith(("#", "//", "/*")):  # comment — left for strip_comments to drop
            return s
        return _NEUTRAL_RX.sub("blk", s)  # string / char literal
    return "".join(repl_span(c, s) for c, s in scan_spans(text, lang))


def shuffle_imports(text: str, lang: str, rng: random.Random) -> str:
    lines = text.splitlines(keepends=True)
    is_imp = (lambda ln: ln.lstrip().startswith(("import ", "from ", "#include")))
    i = 0
    while i < len(lines):
        if is_imp(lines[i]):
            j = i
            while j < len(lines) and is_imp(lines[j]):
                j += 1
            if j - i > 1:
                block = lines[i:j]
                rng.shuffle(block)
                lines[i:j] = block
            i = j
        else:
            i += 1
    return "".join(lines)


def mutate(text: str, lang: str, level: str = "light", seed: int = 0) -> str:
    rng = random.Random(seed)
    text = rename_defs(text, lang, rng)
    text = rebase_ints(text, lang, rng, prob=0.5 if level == "light" else 0.85)
    # Hygiene: novel fixtures must not leak the algorithm via comments or string literals. Both modes
    # now strip comments and neutralize string names — hardness must come from structure, not labels.
    text = neutralize_strings(text, lang)
    text = strip_comments(text, lang)
    if level == "heavy":
        text = shuffle_imports(text, lang, rng)
    return text


# --------------------------------------------------------------------------- corpus generation
# Public tier-2 seeds (from-scratch, library-less). Every novel fixture derives from one of these,
# inheriting its algorithm label (build_manifest reads SEEDS+DERIVATIONS to label the novel split).
T2 = "corpus/tier2_handrolled_textbook"
SEEDS = [
    "rsa_textbook.py", "md5_scratch.py",                       # python
    "rsa_textbook.go", "md5_scratch.go",                       # go
    "RsaTextbook.java", "Sha1Scratch.java", "Sha256Scratch.java",  # java
    "rsa_textbook.c", "md4_scratch.c", "sha256_bcon.c", "des_bcon.c", "aes_bcon.c",
    "rc4_bcon.c", "blowfish_bcon.c", "md2_bcon.c", "md5_bcon.c", "sha1_bcon.c",  # c
]


def _dest(stem: str, ext: str, lang: str, tag: str) -> str:
    """Novel filename: keep it plausibly-renamed, and (java) keep stem CamelCase for the class match."""
    if lang == "java":
        return f"{stem}{tag.upper()}{ext}"      # e.g. RsaTextbook + N1
    return f"{stem}_{tag}{ext}"                 # e.g. rsa_textbook + _n1


def _gen_derivations():
    """light variants -> tier-2 novel (matched difficulty); heavy variants -> tier-3 obfuscated.

    23 light + 40 heavy across the 17 seeds; the first 6 seeds get an extra variant each so the
    tier counts land on 40. Each variant uses a distinct mutation seed, so variants differ from
    each other, not just from the public original."""
    out = []
    for k, name in enumerate(SEEDS):
        src = Path(T2) / name
        stem, ext = src.stem, src.suffix
        lang = LANG_BY_EXT[ext]
        n_light = 2 if k < 6 else 1            # -> 6*2 + 11*1 = 23 tier-2 novel
        n_heavy = 3 if k < 6 else 2            # -> 6*3 + 11*2 = 40 tier-3 obfuscated
        for i in range(1, n_light + 1):
            out.append((str(src), f"{T2}/{_dest(stem, ext, lang, f'n{i}')}", "light"))
        for i in range(1, n_heavy + 1):
            out.append((str(src),
                        f"corpus/tier3_handrolled_obfuscated/{_dest(stem, ext, lang, f'h{i}')}", "heavy"))
    return out


DERIVATIONS = _gen_derivations()


def main() -> None:
    for k, (seed_rel, dest_rel, level) in enumerate(DERIVATIONS):
        src = Path(seed_rel)
        if not src.exists():
            print(f"MISSING SEED\t{seed_rel}", file=sys.stderr)
            continue
        lang = LANG_BY_EXT[src.suffix]
        out = mutate(src.read_text(), lang, level=level, seed=1000 + k)
        dst = Path(dest_rel)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(out)
        print(f"{dest_rel}\tderived:{src.name}\t{level}\t{len(out)}B", file=sys.stderr)


if __name__ == "__main__":
    main()
