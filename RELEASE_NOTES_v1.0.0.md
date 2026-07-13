# v1.0.0 — first release 🔎

**crypto-discovery-bench** finds the cryptography hiding in source code — including the hand-rolled,
library-less, obfuscated, and business-logic-fused crypto that signature/library scanners miss — and
backs the claim with a rigorous, contamination-controlled benchmark.

## Highlights
- **LLM semantic detection with real depth.** Where a signature scanner's recall collapses from 0.82
  (idiomatic library) to **0.00** on library-less crypto, the LLM detector holds at **1.00** through
  tier 4 and ~0.92 on deliberately-unrecognisable code — while staying precise (0.997).
- **Point it at your own code:** `python run.py --detector llm --corpus /path/to/your/code`.
- **The real incumbent, wired up:** a runner for the IBM Sonar Cryptography SonarQube plugin (parses
  its CycloneDX CBOM), with honest coverage handling for languages it can't analyse.
- **Trust, not vibes:** frozen ground truth, dev/test split, a no-answer-leak scanner, a tier-5
  two-labeler agreement gate, contamination measurement, and confidence calibration.

## What's inside
- **Corpus — 377 scored fixtures**, balanced across Python (105), C (90), Go (93), Java (86) + a few
  SQL/shell/AWK at tier 5. Difficulty tiers 0–5 + negatives; provenance splits `public` (verbatim) /
  `novel` (semantics-preserving mutations) / `synth` (authored).
  - Tiers: `{0:40, 1:40, 2:40, 3:40, 4:41, 5:136, neg:40}`.
  - **Tier 5 ("unrecognisable")** — 8 subclasses (partial primitives, fused-into-business-logic,
    homegrown, constant-obfuscated, mislabelled, unusual-language, subtly-broken, split-across-files)
    + high-fidelity decoys + a `crypto_adjacent_review` class for PRNGs.
- **Detectors:** `regex` (offline signature stand-in), `sonar` (real IBM plugin, Docker),
  `llm` (semantic), `hybrid` (deterministic base + LLM, confidence-gated).
- **Evaluation:** per-tier/split precision/recall/F1 with bootstrap 95% CIs, algorithm-level accuracy,
  tier-5 metrics (is_crypto vs family vs algorithm + file-vs-group recall), contamination delta +
  memorisation canary, and confidence calibration (reliability bins, ECE, trust threshold).
- **Reproducible generation:** `generate/{fetch_public,mutate,scrub_synth,synth_specs,tier5_specs,
  build_manifest}.py` regenerate the corpus and frozen manifest from three label sources.

## Headline results
| tier | what | regex recall | LLM recall |
|---|---|---:|---:|
| 0 | idiomatic library | 0.82 | 1.00 |
| 1 | library via indirection | 0.78 | 1.00 |
| 2 | hand-rolled textbook | 0.25 | 1.00 |
| 3 | hand-rolled obfuscated | 0.12 | 1.00 |
| 4 | hand-rolled, library-less | 0.00 | 1.00 |
| 5 | unrecognisable | 0.00 | 0.92 |

- **Precision:** regex 1.000 · llm 0.997 · hybrid 0.997
- **Contamination:** matched-difficulty public−novel delta **0.00** (recall-saturated; canary is the
  live memorisation signal, mean overlap ~0.16)
- **Calibration:** ECE **0.030** (well-calibrated) — crypto flags reach ≥98% precision at
  **confidence ≥ 0.72**, the hybrid's trust/verify threshold
- **Tier-5 finding:** three escalation rounds drove LLM recall 0.97 → ~0.92; the only reliable blind
  spot is a crypto primitive isolated below the level where one file carries intent (a bare S-box
  builder), and group/repo-aware scanning closes it (group-level recall 1.00)

## Quickstart
```bash
git clone https://github.com/MuralidharB/cryto-code-detect && cd cryto-code-detect && pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-...
python run.py --detector llm --corpus /path/to/your/code   # findings → results/llm.jsonl
```

## Known limitations
- Measures detector behaviour on a controlled corpus, not the real-world distribution of library-less
  crypto — strong results justify running on real codebases, not skipping that step.
- LLM detection is per-file; crypto split across files needs repo/group-aware scanning.
- The `sonar` baseline needs Docker + a host where Elasticsearch can start (`vm.max_map_count ≥ 262144`)
  and analyses only Java/Python/Go (C/other → reported unsupported, never counted as misses).
- All fixtures are benign, standard algorithm implementations used as detection targets.

## Changelog
- Full corpus + tier-5 failure-boundary experiment
- Real IBM Sonar Cryptography baseline runner (task 3)
- Confidence calibration (task 5)
- Tracked artifacts (report.md / scores.json / contamination.json / calibration.json)
- Open-source README (header, badges, one-line install, quick example)
- Full benchmark rerun on master + final comment-leak hygiene
