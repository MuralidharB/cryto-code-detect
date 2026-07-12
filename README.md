<h1 align="center">🔎 crypto-discovery-bench</h1>

<p align="center"><b>Find the cryptography hiding in your source code — even when it doesn't call a crypto library.</b></p>

<p align="center">
  <img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-blue.svg">
  <img alt="Python 3.12+" src="https://img.shields.io/badge/python-3.12%2B-blue.svg">
  <img alt="LLM: Claude" src="https://img.shields.io/badge/detection-LLM%20semantic-8A2BE2.svg">
  <img alt="catches hand-rolled crypto" src="https://img.shields.io/badge/catches-hand--rolled%20crypto-brightgreen.svg">
  <img alt="PRs welcome" src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg">
</p>

An open-source toolkit for discovering embedded cryptography in a codebase: RSA, AES, hashes, MACs,
key exchange — including the **hand-rolled, library-less, obfuscated, or business-logic-fused** crypto
that ordinary signature/library scanners walk right past. It ships reference detectors you can point at
your own code, and a rigorous benchmark that proves the detection actually works.

Useful when you need a real cryptographic inventory: **post-quantum migration** (find everything
Shor-breakable), security review, or generating a CBOM for compliance.

## Install

```bash
git clone https://github.com/MuralidharB/cryto-code-detect && cd cryto-code-detect && pip install -r requirements.txt
```

## Quick example

```console
$ export ANTHROPIC_API_KEY=sk-...
$ python run.py --detector llm --corpus ./src
[run] llm over ./src -> results/llm.jsonl
[done] llm: 3 findings

$ cat results/llm.jsonl
{"filepath":"src/util/pack.go","is_crypto":false,"primary_algorithm":null,"evidence":"length-prefix framing, no key — serialization, not crypto","confidence":0.95}
{"filepath":"src/auth/seal.py","is_crypto":true,"primary_algorithm":"custom-stream-cipher","family":"symmetric","quantum_vulnerable":"no","evidence":"payload XORed with a key-derived keystream — homegrown cipher, no library import","confidence":0.9}
{"filepath":"src/billing/license.py","is_crypto":true,"primary_algorithm":"RSA","family":"asymmetric","quantum_vulnerable":"yes","evidence":"modular exponentiation pow(m, e, n) — textbook RSA, no library","confidence":0.97}
```

A signature/library scanner flags **none** of these — there are no crypto imports. The LLM catches the
homegrown stream cipher and the library-less RSA from what the code *does*, and marks the RSA
`quantum_vulnerable` for your migration list.

---

## Why LLM-based scanning — depth, not just pattern-matching

Signature/library scanners (IBM Sonar Cryptography, IBM Quantum Safe Explorer, or the regex stand-in
here) detect crypto by matching **known imports and API calls**. That works for idiomatic library use
and fails the moment the crypto is written by hand — a homegrown cipher, an RSA built from
`pow(m, e, n)` with no import, a keyed MAC disguised as a "checksum" inside business logic.

An LLM detector reads **what the code does**, not what it imports — so it keeps finding crypto as it
gets harder to recognise. Measured on this benchmark (recall = fraction of real crypto caught):

| difficulty | example | signature scanner | **LLM detector** |
|---|---|---:|---:|
| idiomatic library call | `hashlib.sha256(...)` | 0.83 | **1.00** |
| library call, indirected | aliased import / factory / reflection | 0.78 | **1.00** |
| hand-rolled, textbook | RSA/SHA from scratch | 0.25 | **1.00** |
| hand-rolled, obfuscated | renamed vars, computed constants | 0.13 | **1.00** |
| hand-rolled, library-less | bespoke cipher, no stdlib crypto | 0.00 | **1.00** |
| unrecognisable / fragmented | crypto fused into business logic or split across files | 0.00 | **0.94** |

The signature approach falls off a cliff; the LLM degrades gracefully. **That depth is the point of
this project** — and it's measured, not asserted (see [The benchmark](#the-benchmark-how-we-know-the-depth-is-real)).

The LLM also stays **precise** (0.997 on this corpus — it doesn't just flag everything) and its
reported **confidence is well-calibrated** (ECE 0.029), so the hybrid detector can auto-trust
high-confidence flags and deterministically verify the rest.

---

## Scan your own code

```bash
pip install -r requirements.txt          # runtime dep is just `anthropic`
export ANTHROPIC_API_KEY=sk-...

# semantic scan — finds hand-rolled crypto with no library import
python run.py --detector llm    --corpus /path/to/your/code

# hybrid — deterministic signature base + LLM semantic layer (what you'd ship)
python run.py --detector hybrid --corpus /path/to/your/code
```

Each detector writes one JSON finding per file to `results/<detector>.jsonl`:

```json
{"filepath": "src/auth/token.py", "is_crypto": true, "primary_algorithm": "AES-GCM",
 "family": "symmetric", "quantum_vulnerable": "no",
 "evidence": "AES-GCM via aliased import behind a seal() wrapper", "confidence": 0.94}
```

`quantum_vulnerable: "yes"` marks Shor-breakable asymmetric crypto (RSA/DSA/DH/ECC) — the migration
priority list.

### Detectors

| detector | what it is | needs |
|---|---|---|
| `regex` | fast offline signature/keyword stand-in | nothing |
| `sonar` | the **real** IBM Sonar Cryptography plugin (Java/Python/Go) | Docker |
| `llm`   | LLM semantic detection — the depth on hand-rolled crypto | `ANTHROPIC_API_KEY` |
| `hybrid`| deterministic base + LLM, confidence-gated trust/verify | `ANTHROPIC_API_KEY` |

The LLM detector never sees any labels — it judges from code alone — and every raw response is saved
to `results/raw/` so any finding can be audited back to its source.

---

## The benchmark (how we know the depth is real)

A detector that claims to "catch hand-rolled crypto" is easy to say and hard to trust. This repo backs
it with a controlled corpus and honest scoring, so the numbers above survive scrutiny.

### Difficulty tiers (the recall axis)
Every fixture is labelled with a difficulty tier 0–5 (idiomatic library → unrecognisable), plus `neg`
for **crypto-*looking* non-crypto** (djb2, base64, checksums, PRNGs) that a good detector must NOT
flag. Negatives measure **precision** — the honest other half of recall.

**Tier 5 ("unrecognisable")** exists to find where the LLM actually goes blind: crypto that maps to no
named construction — partial primitives, homegrown schemes, constant-obfuscated, mislabelled, or split
across files. Its hardness comes only from surface form, never from genuine ambiguity about whether the
code is cryptographic. Findings so far: the LLM resists homegrown/obfuscated/fused/mislabelled crypto,
and its one reliable blind spot is a cryptographic primitive **isolated below the level where a single
file carries intent** (e.g. a bare S-box builder). Group-aware (repo-level) scanning closes that gap.

### Provenance splits (the contamination axis)
An LLM can look good on *public* crypto simply because it memorised it. Each fixture also has a `split`:
`public` (verbatim from known repos), `novel` (semantics-preserving mutations so the exact text never
existed), and `synth` (fully authored). `eval/contamination.py` reports **recall(public) − recall(novel)
at matched difficulty** plus a memorisation-canary probe, so the capability number reflects code the
model couldn't have seen.

### Trustworthiness guards
- **Frozen ground truth.** `corpus/manifest.csv` is written *before* any detector runs and never
  edited to match output; detectors are scored against it blind.
- **Same corpus for every detector**, byte-identical.
- **Dev/test split.** Prompts are tuned only on `corpus/_dev/` (~20%), never the test set.
- **No answer-leaks.** Hand-rolled fixtures are detectable from code *structure*, not from a comment or
  string naming the algorithm; a leak scanner enforces this (removing leaks dropped the signature
  baseline's tier-2 recall from 0.38 to 0.25 — the leaks had been inflating it).
- **Two-labeler agreement gate (tier 5).** Every scored tier-5 fixture is blind-labelled twice by
  independent models; disagreements go to `_adjudication/` and are reported, not scored.
- **PRNGs as a third class.** Non-crypto PRNGs carry `is_crypto=review` (a posture tool arguably
  *should* surface them) — excluded from binary precision/recall, reported separately.
- **Deterministic scoring** with bootstrap 95% CIs, algorithm-level accuracy, and confidence calibration.

### Reproduce it

```bash
# 1. (re)generate the corpus + frozen manifest  (regenerate manifest FIRST, then detect)
python generate/fetch_public.py      # verbatim public seeds (RosettaCode, B-Con, Go stdlib)
python generate/mutate.py            # novel light/heavy mutations of the public seeds
python generate/scrub_synth.py       # comment-leak hygiene on authored fixtures
python generate/build_manifest.py    # write corpus/manifest.csv

# 2. tier-5 two-labeler gate, then re-freeze
python eval/label_tier5.py           # blind Opus+Haiku labels
python generate/build_manifest.py    # applies the gate; disagreements -> _adjudication/

# 3. run detectors
python run.py --detector regex
python run.py --detector llm
python run.py --detector hybrid

# 4. score + report
python eval/score.py regex llm hybrid       # P/R/F1 + bootstrap CIs, tier-5 metrics
python eval/contamination.py --detector llm --canary
python eval/calibration.py                  # confidence -> empirical accuracy, ECE, trust threshold
python eval/report.py                       # human-readable results/report.md
```

The corpus is 377 scored fixtures balanced across Python/Java/C/Go (tier 5 also uses SQL/shell/AWK).
See `results/report.md` for the full run and `tier5_unrecognizable_crypto.md` for the tier-5 design.

---

## Scope and limitations
- This measures **detector behaviour on a corpus you control** — not the real-world distribution of
  how much enterprise crypto is library-less. Strong results here justify running it on real
  codebases, not skipping that step.
- The LLM detector is per-file; crypto split across files needs repo/group-aware scanning to catch
  every fragment (the benchmark quantifies this file-vs-group gap).
- The `sonar` baseline needs Docker and a host where its embedded Elasticsearch can start
  (`vm.max_map_count ≥ 262144`); it only analyses Java/Python/Go, so C/other files are reported as
  unsupported (no verdict), never counted as misses.
- All fixtures are benign, standard algorithm implementations used as detection targets — never
  exploits or malware.
