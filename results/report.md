# crypto-discovery-bench — results

## Reading

> At tier 4 (hand-rolled, library-less), the signature baseline catches 0% of the crypto while the LLM catches 100% — that gap is the wedge. The LLM trades some precision for that recall (1.00 overall, i.e. it false-positives on some crypto-looking non-crypto), which is why the shippable system pairs it with deterministic verification rather than trusting it raw. At matched difficulty the public−novel recall delta is +0.00: little sign of contamination — but if recall is saturated near 100%, this delta is a ceiling effect and cannot rule contamination in or out.

## Findings — tier-5 escalation experiment

Tier 5 was built to drive LLM recall below 100% and locate the failure boundary. We ran three rounds, each targeting the forms that broke detection in the previous one:

| round | what was added | tier-5 is_crypto recall | subclass-8 file-level | group-level |
|---|---|---|---|---|
| 1 (base) | 8 subclasses + decoys | 0.97 | 0.92 | 1.00 |
| 2 (deeper) | deep business-logic fusion (#2) + finer splits (#8) | 0.96 | 0.89 | 1.00 |
| 3 (finer) | ciphers split into isolated sub/perm/mix fragments | 0.94 | 0.88 | 1.00 |

**Converged conclusion.** Recall fell monotonically (0.97 → 0.96 → 0.94), and every incremental miss is a **cryptographic primitive isolated below the level where a single file carries intent** — specifically a bare substitution-table (S-box / inverse-S-box) builder, which is indistinguishable from any lookup table without its cipher. The LLM was **not** fooled by unfamiliar/homegrown constructions, runtime-computed constants, business-logic fusion, lying function names, subtly-broken variants, or unusual languages (all ≈0.95–1.00). Because **group-level recall stays 1.00** (every split cipher is caught by at least one of its fragments), the product implication is precise: per-file scanning has a floor at fragmented ciphers, but repo/group-aware scanning closes it. Pushing recall lower would require naked S-box files with no group — which correctly fail the two-labeler agreement gate as genuinely ambiguous and land in _adjudication, not the scored set. This is the real per-file floor for confidently-labelable fixtures.

## Miss rate by tier (the wedge)

Recall = fraction of crypto caught; miss = 1 − recall. The thesis: signatures fall off a cliff after tier 1; the LLM degrades gracefully.

| tier | what | regex recall | llm recall | hybrid recall | regex miss | llm miss | hybrid miss |
|---|---|---|---|---|---|---|---|
| 0 | idiomatic library | 0.82 | 1.00 | 1.00 | 18% | 0% | 0% |
| 1 | library via indirection | 0.78 | 1.00 | 1.00 | 22% | 0% | 0% |
| 2 | hand-rolled textbook | 0.25 | 1.00 | 1.00 | 75% | 0% | 0% |
| 3 | hand-rolled obfuscated | 0.12 | 1.00 | 1.00 | 88% | 0% | 0% |
| 4 | hand-rolled, library-less | 0.00 | 1.00 | 1.00 | 100% | 0% | 0% |
| 5 | unrecognizable (tier 5) | 0.00 | 0.94 | 0.92 | 100% | 6% | 8% |

## Precision & F1 (the honest other half)

| detector | precision | recall | F1 | false positives on negatives |
|---|---|---|---|---|
| regex | 1.00 | 0.25 | 0.40 | 0 |
| llm | 1.00 | 0.98 | 0.99 | 0 |
| hybrid | 1.00 | 0.97 | 0.98 | 0 |

## crypto_adjacent_review (PRNGs — reported, not scored)

PRNGs are excluded from binary precision/recall; a posture tool may legitimately surface them for review. Numbers = how often each detector flagged a review item.

| detector | regex | llm | hybrid |
|---|---|---|---|
| surfaced | 0/14 | 13/14 | 13/14 |

## Tier 5 — unrecognizable crypto (the failure-boundary tier)

Three numbers that diverge by design: is_crypto recall (did it spot crypto at all), family accuracy, algorithm accuracy (recognizable subset only).

| detector | is_crypto recall | family acc | algo acc (reco) | decoy FP rate | file-lvl | group-lvl |
|---|---|---|---|---|---|---|
| regex | 0.00 (n=115) | — | — | 0.00 (0/13) | 0.00 | 0.00 |
| llm | 0.94 (n=115) | 0.99 | 0.90 | 0.08 (1/13) | 0.88 | 1.00 |
| hybrid | 0.92 (n=115) | 0.99 | 0.90 | 0.08 (1/13) | 0.85 | 1.00 |

**llm is_crypto recall by subclass** (which forms break detection):

| subclass | recall | n |
|---|---|---|
| 1 | 1.00 | 8 |
| 2 | 0.95 | 19 |
| 3 | 1.00 | 13 |
| 4 | 1.00 | 8 |
| 5 | 1.00 | 4 |
| 6 | 1.00 | 7 |
| 7 | 1.00 | 8 |
| 8 | 0.88 | 48 |

## Contamination (read at matched difficulty)

- **Matched-difficulty delta (public − novel recall): +0.000**
- Aggregate delta: +0.000 — *do not quote*; conflates contamination with difficulty imbalance between splits.

| tier | public recall (n) | novel recall (n) | delta |
|---|---|---|---|
| 2 | 1.00 (17) | 1.00 (23) | +0.000 |

- **Memorisation canary**: mean verbatim overlap 0.17, max 0.67 over 20 public fixtures (>~0.6 suggests the exact file is memorised).

## Corpus composition

- **377 fixtures** | tiers: 0=40, 1=40, 2=40, 3=40, 4=41, 5=136, neg=40 | splits: novel=87, public=23, synth=267 | langs: awk=1, c=90, go=93, java=86, python=105, shell=1, sql=1
- dev held-out (prompt tuning only): 65 (17%)
