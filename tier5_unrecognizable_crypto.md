# Task: Tier 5 — "unrecognizable crypto" corpus

## Why this tier exists
The validated run showed LLM recall pinned at 1.00 across tiers 0–4. A capability you can't break
in testing isn't validated — it's unmeasured. Tiers 0–4 contain *recognizable, canonical* hand-rolled
crypto (named constructions: Feistel, ARX, LFSR, SPN, sponge, Merkle–Damgård). The model nailing those
is expected — it's pattern-matching forms it has seen thousands of times. The real-world hard case, and
the one your wedge actually claims, is crypto that maps to **no named construction**: partial, fused into
business logic, homegrown, obfuscated-by-construction, or subtly broken.

Tier 5 is built to **drive LLM recall below 100%** on purpose. Its job is to find the failure boundary,
not to flatter the model. If the LLM still scores 1.00 on a well-built tier 5, escalate hardness until it
doesn't — the boundary is the deliverable.

**Bonus (kills the contamination ceiling effect):** homegrown/novel fixtures never existed publicly, so
they are un-memorisable by construction. A hard tier 5 simultaneously (a) finds the failure boundary and
(b) supplies clean `novel`-split fixtures with sub-100% recall, which is the *prerequisite* for the
public-vs-novel contamination delta to carry any information at all. Build tier 5 mostly as `split=novel`.

## The one design rule that keeps the labels trustworthy
**Hardness must come from surface form and non-canonical structure — NEVER from genuine ambiguity about
whether the code is cryptographic.** A careful human crypto expert must still be able to label every
scored fixture confidently. The LLM should struggle because it can't pattern-match, not because the
answer is genuinely unclear.

Genuinely ambiguous cases (is a PRNG crypto? is a CRC crypto? is Reed–Solomon's GF math crypto?) do NOT
go in the scored set. They go in `corpus/tier5_unrecognizable/_adjudication/` with a written rationale,
and are reported separately as a "labeling-philosophy" appendix. Mixing contestable labels into the
scored set destroys the benchmark.

## Subclasses to build (target ≥ 8 fixtures each, balanced across Python/Java/C/Go/Rust)

1. **Partial / extracted primitive.** Only a fragment of an algorithm: a key schedule with no encrypt
   call, a lone round function, a GF(2^8) multiply, a padding routine, decrypt-only. *Probes:* can the
   model recognise crypto from an incomplete piece? *Label:* is_crypto=true, family by the primitive,
   primary_algorithm often null/"fragment".

2. **Fused into business logic.** The crypto op is interleaved with serialization, logging, DB calls;
   identifiers are domain names (`invoiceToken`, `sessionScramble`, `licenseSeal`). *Probes:* semantic
   recognition under non-crypto surface noise. *Label:* by the actual operation.

3. **Homegrown / non-canonical scheme.** A genuinely cryptographic keyed transform that matches no
   textbook algorithm — invented cipher/MAC/KDF. *Probes:* first-principles reasoning ("keyed reversible
   transform meant to obscure data ⇒ crypto") with no named pattern to lean on. *This is the purest test.*
   *Label:* is_crypto=true, family=symmetric/mac/kdf, primary_algorithm="custom-<type>",
   expect_algorithm_match=false.

4. **Constant-obfuscated.** The giveaway magic numbers (AES S-box, SHA round constants, 0x9E3779B9) are
   computed at runtime, table-generated, or split/encoded rather than present as literals. *Probes:*
   does detection survive when constant-matching fails? *Label:* by the real algorithm.

5. **Mislabeled / lying comments & names.** A `compress()` / `encode()` / `checksum()` that actually does
   keyed encryption (recall test), AND an `encrypt()` that merely base64s (precision test). *Probes:*
   does the model read code or labels?

6. **Unusual paradigm/language.** Functional-style, bitsliced/vectorised, SQL/PLSQL stored proc, shell
   xor, assembly. *Probes:* robustness to forms unlike the textbook loop.

7. **Subtly broken crypto.** Real algorithm with a bug (ECB-instead-of-CBC, reused nonce, truncated key,
   wrong round count). Still crypto, arguably *more* important to inventory. *Probes:* recall on
   non-pristine code; bonus credit if `evidence` notes the weakness. *Label:* is_crypto=true by intent.

8. **Split across files (composition-only).** Crypto whose pieces live in separate files; no single file
   is recognisable, only the composition. *Probes:* the genuine limit of per-file detection — expected to
   FAIL, and that's a real, honest finding about the product's discovery granularity. Label each file by
   its fragment; add a `compose_group` id so scoring can report file-level vs group-level detection.

### High-fidelity decoys (tier-5 negatives — ≥ 10)
Closer to crypto than djb2/CRC: a non-crypto checksum using an S-box-like table; Reed–Solomon GF
arithmetic (ECC-the-error-correction, not ECC-the-curve); a simulation PRNG explicitly seeded for Monte
Carlo; a rolling hash for rsync-style dedup; a bloom-filter hash bank. *Probes:* the precision boundary
where the model is most tempted to over-flag.

> Note on PRNGs: the prior run flagged MersenneTwister/xorshift as crypto. Before counting such hits as
> errors, decide the labeling philosophy explicitly and record it. A *crypto-posture* tool arguably
> SHOULD surface PRNGs as "verify not used for keys/IVs/nonces." Consider a third class
> `crypto_adjacent_review` rather than forcing PRNGs into crypto/non-crypto, and report it separately.

## Manifest extensions (add these columns; update eval/score.py to read them, defaulting gracefully)
```
subclass            # one of the 8 names above, or "decoy"
label_rationale     # one sentence: why this label is defensible to an expert (REQUIRED at tier 5)
expect_algorithm_match  # true/false — false for homegrown; score.py skips algo-name match when false
compose_group       # id linking split-across-files fixtures; empty otherwise
labeler_a,labeler_b # two independent labels; only fixtures where they AGREE enter the scored set
```

## Labeling protocol (trust-critical at this tier)
1. Two independent labels per fixture (you + co-founder, or two separate passes/models with no shared
   prompt). Record both.
2. **Agreement gate:** only fixtures where labeler_a == labeler_b on `is_crypto` enter the scored set.
   Disagreements move to `_adjudication/` with rationale and are reported, not scored.
3. Every scored fixture carries a one-sentence `label_rationale`. If you can't write a confident
   rationale, the fixture is ambiguous → adjudication bucket, not scored set.
4. The manifest stays frozen before detectors run. Generate → label → freeze → detect → score.

## Scoring changes (eval/score.py)
- When `expect_algorithm_match=false`, score is_crypto + family only; do not penalise primary_algorithm.
- Report three separate numbers at tier 5: **is_crypto recall**, **family accuracy**, **algorithm
  accuracy (recognizable subset only)** — they will diverge, and the divergence is the finding.
- Track precision on the high-fidelity decoys as its own line (this is where over-flagging shows up).
- For `compose_group` fixtures, report file-level recall AND group-level recall (detected if ANY member
  flagged) — the gap quantifies the per-file granularity limit.

## Success criterion
You have succeeded when LLM **is_crypto recall drops below 100%** on the scored tier-5 set with
reasonable n. Then:
- Which subclasses broke it? (Expect: homegrown #3, split-across-files #8, maybe constant-obfuscated #4.)
- Does recall(public) now exceed recall(novel)? If yes → contamination is real; report novel-only.
- Where does precision crack on the high-fidelity decoys?

If recall stays at 100%, the corpus is still too easy — escalate (more #3 homegrown, longer fused #2,
deeper composition #8) until it breaks. A model you cannot break in testing is a claim you cannot defend.

## Guardrail
All fixtures are benign detection targets — algorithm implementations and crypto-shaped code used to
test a discovery tool. No working exploits, no malware, nothing whose purpose is offensive. "Broken
crypto" fixtures (#7) illustrate a bug for detection purposes and should be minimal, not weaponisable.

## Seed fixtures already in this repo (extend from these)
- `corpus/tier5_unrecognizable/license_seal.py` — subclass #2 (fused into business logic), homegrown
  keyed transform disguised as license-token generation. split=novel.
- `corpus/tier5_unrecognizable/obscure_xform.c` — subclass #3 (homegrown non-canonical cipher),
  no named algorithm. split=novel, expect_algorithm_match=false.
- `corpus/tier5_unrecognizable/rolling_dedup.py` — tier-5 decoy: a rolling hash for dedup that looks
  crypto-ish but isn't. Tests the precision boundary.
