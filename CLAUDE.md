# CLAUDE.md — build spec for Claude Code

This repo is a benchmark harness. The skeleton is runnable on the seed corpus; your job is to
expand it into a statistically meaningful experiment **without compromising the trustworthiness
guards in README.md**. Read the README first — the guards are the point of the project.

## Context
We are evaluating whether an LLM-based crypto-discovery approach catches code-level cryptography
that signature/library-based scanners (IBM Quantum Safe Explorer, IBM Sonar Cryptography) miss —
specifically hand-rolled / library-less crypto. This is defensive security tooling (cryptographic
inventory for post-quantum migration). All fixtures are standard, benign algorithm implementations
used as detection targets — never exploits or malware.

## Tasks, in priority order

1. **Expand the corpus to statistical significance.**
   - Target ≥ 40 fixtures per tier (0–4) and ≥ 40 negatives, balanced across languages
     (Python, Java, C, Go to start). Currently there are only a few seed fixtures per tier.
   - For every fixture, add a row to `corpus/manifest.csv` BEFORE it is scored. The manifest is
     the frozen ground truth — never edit a label to match a detector's output.
   - Keep a strict **dev/test split**: put ~20% in `corpus/_dev/` for prompt tuning, keep the rest
     untouched as test. Do not inspect test fixtures while iterating on the LLM prompt.

2. **Build the contamination splits correctly.**
   - `public`: real crypto code copied verbatim from named public repos. Record the URL in `source`.
   - `novel`: take a public seed and apply `generate/mutate.py` transformations (rename identifiers,
     reorder independent statements, change numeric-literal representation, translate to another
     language) so the exact bytes never existed publicly. The algorithm label is preserved; the text
     is new. Record `source` = the seed it derived from.
   - Each `novel` fixture should have a matched-difficulty `public` counterpart so the contamination
     delta is apples-to-apples.

3. **Wire up the real incumbent baseline (Sonar Cryptography).**
   - `detectors/sonar_baseline/` currently has only setup notes. Implement a runner that invokes
     IBM's open-source Sonar Cryptography SonarQube plugin over the corpus and normalises its output
     to the standard finding schema (below). This is the *real* incumbent proxy; the regex baseline
     is only a quick stand-in. Document any fixtures Sonar can't process (e.g. unsupported language).

4. **Harden the LLM detector.**
   - Keep output strictly structured JSON (schema below). Add ret/backoff on API errors.
   - Save every raw response to `results/raw/` for audit.
   - Do NOT let the detector see the manifest or tier labels — it must judge from code alone.

5. **Strengthen scoring.**
   - Add bootstrap 95% confidence intervals on recall/precision per tier (resample fixtures).
   - Add algorithm-level accuracy (not just binary is_crypto) for true positives.
   - Add confidence calibration: bucket LLM findings by reported confidence, plot empirical accuracy
     per bucket. Well-calibrated confidence is what lets the hybrid detector trust/verify thresholds.

## Finding schema (every detector emits this, one JSON object per line, to results/<name>.jsonl)
```json
{"filepath": "corpus/tier2_handrolled_textbook/rsa_scratch.py",
 "is_crypto": true,
 "primary_algorithm": "RSA",
 "family": "asymmetric",
 "quantum_vulnerable": "yes",
 "evidence": "modular exponentiation pow(m, e, n) with public exponent",
 "confidence": 0.82}
```
`is_crypto` is the only required field for binary scoring; the rest enrich algorithm-level metrics.

## Acceptance criteria
- `python run.py --detector regex|llm|hybrid` runs clean over the corpus and writes valid jsonl.
- `python eval/score.py` produces per-tier, per-split precision/recall/F1 with CIs.
- `python eval/contamination.py` reports recall(public) − recall(novel) and a memorisation canary result.
- `python eval/report.py` produces `results/report.md` containing the miss-rate-by-tier table and
  the contamination delta, with a one-paragraph plain-language reading at the top.
- No label in `corpus/manifest.csv` was changed after a detector ran. (If you regenerate the corpus,
  regenerate the manifest first, then re-run detectors.)

## Hard guardrails
- Never tune prompts on the test split. Dev split only.
- Never report a wedge/capability number from the `public` split alone — headline numbers come from `novel`.
- Fixtures are benign algorithm implementations only. Do not add working exploit code, malware, or
  anything whose purpose is offensive; this is an inventory/detection benchmark.
