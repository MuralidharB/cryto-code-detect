# crypto-discovery-bench

A measurement harness that answers two questions with numbers instead of intuition:

1. **Sizing the wedge.** How much real cryptography do signature/library-based scanners
   (the incumbent approach — IBM Quantum Safe Explorer, IBM Sonar Cryptography) *miss*,
   especially hand-rolled / library-less crypto? That miss rate is your addressable gap.
2. **Trusting the LLM numbers.** Does an LLM-based detector's accuracy on *public* crypto
   code (which the model may have memorized) overstate its accuracy on *novel* code it has
   never seen? That gap is contamination, and it's the thing that makes naive LLM benchmarks lie.

Everything here exists to make those two numbers defensible. If you only read one section,
read **Trustworthiness guards** below — it's the point.

---

## The core experimental variables

### Difficulty tiers (the recall axis)
Every crypto fixture is labelled with a difficulty tier. The whole thesis predicts a specific
shape: signature scanners hold up through Tier 1 and fall off a cliff after it; an LLM degrades
gracefully across all tiers. The **gap between those two curves is the wedge**, measured.

| Tier | What it is | Signature scanner should… | LLM should… |
|------|------------|---------------------------|-------------|
| 0 | Idiomatic library calls (`from cryptography... import rsa`) | catch ~all | catch ~all |
| 1 | Library calls via indirection (aliased imports, wrapper fns, dynamic dispatch) | mostly catch | catch |
| 2 | Hand-rolled but textbook (recognisable names, standard structure) | start missing | catch most |
| 3 | Hand-rolled + obfuscated (renamed vars, inlined constants, split across fns) | miss most | catch many |
| 4 | Hand-rolled, library-less, unusual idioms (the messy-enterprise-tail proxy) | miss ~all | the real test |
| 5 | **Unrecognisable** — crypto that maps to no named construction: partial primitives, fused into business logic, homegrown, constant-obfuscated, mislabelled, split across files (see `tier5_unrecognizable_crypto.md`) | miss ~all | **the failure boundary** |
| neg | Crypto-*looking* non-crypto (djb2 hashmap hash, base64, bignum DSP) | should NOT flag | should NOT flag |

Tier `neg` is not optional. A detector that flags everything has perfect recall and zero value.
Negatives measure **precision**, which is the honest other half of the story.

**Tier 5** exists because the LLM pinned at ~1.00 recall on tiers 0–4 (a capability you can't break in
testing is unmeasured, not validated). Its hardness comes only from surface form / non-canonical
structure — never from genuine ambiguity about whether the code is cryptographic. It adds metadata
columns (`subclass`, `expect_algorithm_match`, `compose_group`) and a required `label_rationale`, and
reports three diverging numbers: is_crypto recall, family accuracy, and algorithm accuracy (on the
recognizable subset only). Its findings are the answer to *"where does the LLM actually go blind?"*

### A third label: `crypto_adjacent_review`
Non-cryptographic PRNGs (Mersenne Twister, xorshift, LCG, PCG) are genuinely contestable for a
crypto-*posture* tool — it arguably SHOULD surface them ("verify this isn't seeding keys/IVs/nonces").
Rather than force them into crypto/non-crypto, they carry `is_crypto=review`: excluded from binary
precision/recall and reported separately (how often each detector surfaces them).

### Provenance splits (the contamination axis)
Every fixture is also labelled with a `split`:

- `public` — lifted verbatim from well-known public repos. Likely in the model's training data.
- `novel` — generated/mutated so the exact text never existed before the model's cutoff.
- `synth` — fully synthesised fixtures (also novel, but not derived from a public seed).

The headline contamination number is **LLM recall(public) − LLM recall(novel)** at matched
difficulty. Small delta ⇒ your LLM numbers generalise to private customer code. Large delta ⇒
public benchmarks (including most you'll see quoted by vendors) are inflated, and you must report
novel-split numbers only.

---

## Ground truth by construction

Crypto code is unusually honest to label: if you generate code that implements RSA, you *know*
it's RSA — no human annotator, no guesswork. `corpus/manifest.csv` is the **frozen source of
truth**. It is written *before* any detector runs and never edited to match detector output.
Detectors are scored against it blind.

Manifest columns:
```
filepath,language,is_crypto,primary_algorithm,family,quantum_vulnerable,tier,split,source,notes,
subclass,label_rationale,expect_algorithm_match,compose_group,labeler_a,labeler_b
```
`is_crypto` ∈ {true, false, review}   (`review` = crypto-adjacent PRNG, reported not scored)
`family` ∈ {symmetric, asymmetric, hash, kdf, mac, rng, none}
`quantum_vulnerable` ∈ {yes, no, na}   (yes = Shor-breakable asymmetric: RSA/DSA/DH/ECC)

The last six columns are tier-5 only (empty for tiers 0–4/neg): `subclass` (the tier-5 subclass),
`label_rationale` (one sentence an expert would sign — required at tier 5), `expect_algorithm_match`
(false for homegrown; scoring then skips algorithm-name match), `compose_group` (links
split-across-files fixtures so scoring reports file-level vs group-level recall), and `labeler_a`/
`labeler_b` (the two independent blind labels — see guard 8).

The whole corpus (tiers 0–5 + negatives) is regenerated by `generate/build_manifest.py`, which assembles
labels from three sources: verbatim public seeds (`generate/fetch_public.py`), novel mutations
(`generate/mutate.py`), and authored `synth`/tier-5 specs (`generate/synth_specs.py`,
`generate/tier5_specs.py`) — the single sources of truth for authored-fixture labels.

---

## Trustworthiness guards (read this)

These are the design choices that separate a number you can put in a deck from a number that
will embarrass you in diligence:

1. **Pre-registered labels.** The manifest is the spec. Generate it first, freeze it, score against it.
2. **Dev/test separation.** Tune LLM prompts only on `corpus/_dev/` fixtures. Never look at the
   test split while iterating prompts, or you're fitting the test set and your recall is fiction.
3. **Contamination is measured, not assumed.** The `novel` split + the canary probe
   (`eval/contamination.py`) quantify memorisation directly. Report it; don't hand-wave it.
4. **Negatives carry equal weight.** Precision is reported alongside recall, per tier. No cherry-picking recall.
5. **Same corpus for every detector.** The signature baseline and the LLM see byte-identical files.
6. **Deterministic scoring.** Detector output → `results/<name>.jsonl` in a fixed schema; `eval/score.py`
   aligns to the manifest mechanically. The scorer never sees which detector produced which file.
7. **Everything logged.** Raw model responses are saved to `results/raw/` so any number can be audited
   back to its source.
8. **Two-labeler agreement gate (tier 5).** Every scored tier-5 fixture is blind-labelled twice by
   independent models (`eval/label_tier5.py`, Opus + Haiku, prompts distinct from the detector's).
   Only fixtures where the two labels AGREE on is_crypto enter the scored set; disagreements are moved
   to `corpus/tier5_unrecognizable/_adjudication/` and reported, not scored. This keeps the hardest
   tier honest — a fixture nobody can confidently label doesn't get to count.
9. **No answer-leaks.** Hand-rolled/tier-5 fixtures must be detectable from code STRUCTURE, not from a
   comment or string naming the algorithm (which would hand both detectors the answer and shrink the
   measured wedge). A leak scanner enforces this; `generate/mutate.py` and `generate/scrub_synth.py`
   strip comments and neutralise algorithm names in string literals. (Removing these leaks dropped the
   regex baseline's tier-2 recall from 0.38 to 0.25 — the leaks had been inflating it.)

The single most important discipline: **the wedge claim must be made on the `novel` split.**
"We catch what IBM QSE misses" is only true if the crypto we catch is crypto the model couldn't
have memorised.

---

## How to run

```bash
pip install -r requirements.txt          # runtime dep is just `anthropic` (rest is stdlib)
export ANTHROPIC_API_KEY=sk-...

# 1. (re)generate the corpus + frozen manifest  (regenerate manifest FIRST, then detect)
python generate/fetch_public.py          # verbatim public seeds (RosettaCode, B-Con, Go stdlib)
python generate/mutate.py                # novel light/heavy mutations of the public seeds
python generate/scrub_synth.py           # comment-leak hygiene on authored tier-4/negatives
python generate/build_manifest.py        # write corpus/manifest.csv (all label sources + dev split)

# 2. (tier 5 only) two-labeler agreement gate, then re-freeze
python eval/label_tier5.py               # blind Opus+Haiku labels → results/tier5_labels.json
python generate/build_manifest.py        # applies the gate; disagreements → _adjudication/

# 3. run the detectors over the corpus
python run.py --detector regex           # signature stand-in (fast, free, offline)
python run.py --detector sonar           # REAL incumbent: IBM Sonar Cryptography plugin (needs Docker)
python run.py --detector llm             # LLM semantic detector (needs API key)
python run.py --detector hybrid          # regex prescreen + LLM (the architecture under test)

# 4. score and report
python eval/score.py regex sonar llm hybrid   # P/R/F1 + bootstrap CIs per tier/split, tier-5 metrics
python eval/contamination.py --detector llm --canary   # public-vs-novel delta + memorisation canary
python eval/calibration.py                    # confidence buckets → empirical accuracy, ECE, trust threshold
python eval/report.py                         # human-readable results/report.md
```

## How to read the output

- **`results/report.md` → "miss rate by tier" table.** The regex/Sonar column climbing toward
  100% missed as tier increases *is* your opportunity, quantified. If it doesn't climb, the wedge
  is smaller than hypothesised — that's a real (and cheap) finding too.
- **Contamination delta.** If LLM recall(novel) ≈ recall(public), trust the capability number.
  If novel is much worse, your true capability is the novel number — use only that externally.
- **Negatives / precision.** If LLM precision is poor (flags non-crypto), the wedge needs the
  hybrid architecture (deterministic verification of LLM flags) before it's a compliance-grade
  system of record.
- **Tier 5 → the failure boundary.** Three numbers diverge on purpose (is_crypto recall / family /
  algorithm accuracy). The per-subclass table shows *which* forms break detection, and the
  file-level vs group-level recall gap quantifies the per-file detection limit for split-across-files
  crypto (group-aware scanning closes it).
- **Confidence calibration.** The ECE and reliability bins say whether reported confidence can be
  trusted; the **trust threshold** is the confidence above which is_crypto=true flags are precise
  enough for the hybrid to auto-trust (verify below it).
- **Sonar coverage.** The real incumbent only analyses Java/Python/Go — C and exotic-language files
  are `unsupported` (no verdict, excluded from its P/R and reported as `coverage`). Low coverage is
  itself part of the incumbent-miss story: it can't even look at those files.

## What this does NOT tell you
The fraction of *real* enterprise crypto that is library-less. This harness measures detector
behaviour on a corpus you control; it does not measure the wild distribution. Closing that needs
2–3 real design-partner codebases (see the venture notes). Treat strong results here as
*necessary, not sufficient* — they justify pursuing a design partner, not skipping one.
