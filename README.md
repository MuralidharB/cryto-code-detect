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
| neg | Crypto-*looking* non-crypto (djb2 hashmap hash, base64, bignum DSP) | should NOT flag | should NOT flag |

Tier `neg` is not optional. A detector that flags everything has perfect recall and zero value.
Negatives measure **precision**, which is the honest other half of the story.

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
filepath,language,is_crypto,primary_algorithm,family,quantum_vulnerable,tier,split,source,notes
```
`family` ∈ {symmetric, asymmetric, hash, kdf, mac, rng, none}
`quantum_vulnerable` ∈ {yes, no, na}   (yes = Shor-breakable asymmetric: RSA/DSA/DH/ECC)

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

The single most important discipline: **the wedge claim must be made on the `novel` split.**
"We catch what IBM QSE misses" is only true if the crypto we catch is crypto the model couldn't
have memorised.

---

## How to run

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-...

# 1. (optional) expand the seed corpus — see CLAUDE.md for the build-out task
python generate/mutate.py            # derives novel variants from public seeds

# 2. run the detectors over the corpus
python run.py --detector regex       # signature baseline (fast, free)
python run.py --detector llm         # LLM semantic detector (needs API key)
python run.py --detector hybrid      # regex prescreen + LLM (the architecture under test)

# 3. score and report
python eval/score.py                 # precision/recall/F1 per tier and split → results/scores.json
python eval/contamination.py         # public-vs-novel delta + memorisation canary
python eval/report.py                # human-readable results/report.md with the two curves
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

## What this does NOT tell you
The fraction of *real* enterprise crypto that is library-less. This harness measures detector
behaviour on a corpus you control; it does not measure the wild distribution. Closing that needs
2–3 real design-partner codebases (see the venture notes). Treat strong results here as
*necessary, not sufficient* — they justify pursuing a design partner, not skipping one.
