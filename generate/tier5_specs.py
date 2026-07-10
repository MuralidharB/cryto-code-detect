"""
tier5_specs.py — single source of truth for the TIER-5 "unrecognizable crypto" fixtures.

Tier 5 exists to drive LLM is_crypto recall below 100% (find the failure boundary) using hardness
that comes ONLY from surface form / non-canonical structure — never from genuine ambiguity about
whether the code is cryptographic (see tier5_unrecognizable_crypto.md). Every scored fixture is
confidently expert-labelable; a one-line label_rationale is REQUIRED.

Each row fixes the LABEL (decided by us, never by the author-agent or a detector) plus tier-5 metadata:
  subclass, split, expect_algo, compose_group, is_crypto (true/false/review), family, qv, rationale, hint.
Generation rule enforced downstream: NO algorithm names or crypto words in comments/strings/identifiers
(neutral identifiers only) — hardness must be structural.

split convention (per approved decision): derived-from-a-real-algorithm subclasses (#1 partial,
#4 constant-obfuscated, #7 broken) = split=novel (they pair with tier-2 public for the contamination
delta); invented/homegrown (#2 fused, #3 homegrown, #6 unusual) = split=synth. Both are un-memorisable.
"""
from __future__ import annotations
from pathlib import Path

DIR = "corpus/tier5_unrecognizable"
T5: list[dict] = []


def t5(sub, lang, base, is_crypto, algo, family, qv, split, expect_algo, group, rationale, hint):
    T5.append(dict(path=f"{DIR}/{base}", subclass=sub, lang=lang, is_crypto=is_crypto, algo=algo,
                   family=family, qv=qv, split=split, expect_algo=expect_algo, compose_group=group,
                   rationale=rationale, hint=hint))


A, S, H, M, K = "asymmetric", "symmetric", "hash", "mac", "kdf"

# ---- subclass 1: partial / extracted primitive (8, novel, expect_algo=false) --------------------
# Fragments a crypto expert confidently calls crypto (a key schedule, a round fn, a mode wrapper).
t5(1, "java", "T5KeyExpand.java", True, "key-schedule", S, "no", "novel", False, "",
   "expands a short key into many round subkeys via rotate+sbox+rcon — unmistakably a block-cipher key schedule",
   "AES-style key expansion ONLY (no encrypt). rotate word, sub bytes via a computed table, xor round const. neutral names.")
t5(1, "c", "t5_block_decrypt.c", True, "block-decrypt", S, "no", "novel", False, "",
   "inverse round function with inverse sbox and key subtraction — a block cipher decrypt path",
   "decrypt-only routine of a 128-bit block cipher: inverse sbox, inverse mix, round-key xor, reversed rounds.")
t5(1, "python", "t5_cipher_round.py", True, "cipher-round", S, "no", "novel", False, "",
   "one substitution-permutation round: sbox, bit permutation, subkey add — a cipher primitive",
   "a single SPN round applied to a 16-byte state: sbox lookup, fixed bit-permutation, xor subkey.")
t5(1, "go", "t5_cbc_wrap.go", True, "CBC-mode", S, "no", "novel", False, "",
   "chains fixed-size blocks with xor feedback around an opaque block transform — CBC mode of operation",
   "CBC-mode wrapper: xor prev ciphertext into plaintext block, call an opaque block() fn, chain. no key literals.")
t5(1, "c", "t5_poly_mac_step.c", True, "poly-mac-step", M, "no", "novel", False, "",
   "multiply-accumulate of message blocks in a binary field under a secret point — a polynomial MAC core",
   "GHASH-like polynomial MAC step: for each block, xor into accumulator then multiply in GF(2^128) by H.")
t5(1, "python", "t5_ctr_keystream.py", True, "CTR-keystream", S, "no", "novel", False, "",
   "generates a keystream by encrypting an incrementing counter, then xors — CTR mode",
   "CTR keystream: encrypt counter blocks with an opaque block fn, concatenate, xor with data.")
t5(1, "go", "t5_ipad_opad.go", True, "hmac-construction", M, "no", "novel", False, "",
   "wraps an opaque hash with inner/outer key-pad passes — the HMAC construction",
   "HMAC construction over an opaque hash(): key xor ipad then message, then key xor opad then that digest.")
t5(1, "java", "T5RoundLoop.java", True, "round-loop", S, "no", "novel", False, "",
   "iterates key-whitening + nonlinear round over a state array — the body of a block cipher",
   "block-cipher round loop: initial key whitening, N rounds of sbox+shift+mixadd, final round. opaque subkeys.")

# ---- subclass 2: fused into business logic (10, synth, expect_algo=false) ------------------------
for lang, base, fam, rn, hint in [
    ("python", "invoice_token.py", S, "keyed stream xor disguised as invoice-token issuance",
     "issue_invoice_token(): builds an invoice dict, serializes, then XORs payload with a keystream derived from an account secret; logs + returns base64. crypto is the keystream xor."),
    ("java", "SessionScramble.java", S, "keyed block permutation inside session management",
     "SessionManager.pack(): reorders + substitutes session-id bytes under a server key (a real keyed permutation cipher) amid map/DB bookkeeping."),
    ("go", "license_seal.go", S, "homegrown keyed stream cipher named as license sealing",
     "IssueSeal(): timestamp + XOR payload with a key-stretched keystream; framed as license issuance for a billing service."),
    ("python", "audit_tag.py", M, "CBC-MAC over log lines presented as an audit checksum",
     "tag_audit_batch(): iterates log records, CBC-MAC-style chains each through a keyed block fn to a final tag; framed as tamper-evidence."),
    ("java", "ConfigVault.java", S, "Feistel over a config blob framed as config storage",
     "ConfigVault.store(): runs a keyed Feistel network over serialized config bytes before persisting; framed as at-rest protection."),
    ("go", "coupon_signer.go", M, "homemade keyed hash presented as coupon validation",
     "SignCoupon(): mixes coupon fields with a secret via a keyed compression loop to a short tag; framed as anti-forgery."),
    ("c", "telemetry_obf.c", S, "xor+rotate keyed transform inside a telemetry uploader",
     "obfuscate_telemetry(): keyed xor+rotate over a telemetry buffer before send; interleaved with buffer/length bookkeeping."),
    ("python", "password_stretch.py", K, "iterated salted KDF inside an auth service",
     "derive_login_key(): thousands of iterations of salted mixing to stretch a password into a key; framed as auth setup."),
    ("go", "cookie_seal.go", S, "keyed transform on cookies framed as cookie management",
     "SealCookie(): keyed reversible byte transform over cookie value, plus attributes/expiry handling."),
    ("c", "firmware_stamp.c", M, "keyed checksum-as-MAC in a firmware updater",
     "stamp_firmware(): keyed rolling compression over the image producing an authentication tag; framed as integrity stamp."),
]:
    t5(2, lang, base, True, "custom-"+("mac" if fam == M else ("kdf" if fam == K else "cipher")), fam, "no",
       "synth", False, "", rn, hint)

# ---- subclass 3: homegrown / non-canonical (12, synth, expect_algo=false) — the purest test ------
for lang, base, fam, rn, hint in [
    ("python", "hg_confuse_diffuse.py", S, "invented keyed confusion-diffusion cipher, no textbook match",
     "a reversible keyed block transform: key-derived byte substitution then a data-dependent rotation network. invented, not any named cipher."),
    ("java", "HgArxWide.java", S, "invented wide-block ARX cipher",
     "256-bit ARX permutation with an unusual add/rotate/xor schedule keyed by subkeys; invented structure."),
    ("go", "hg_perm_stream.go", S, "invented stream cipher from a key-derived permutation walk",
     "keystream generated by walking a key-seeded permutation table (RC4-unlike schedule); xored with data."),
    ("c", "hg_sponge_mix.c", H, "invented sponge hash with a bespoke permutation",
     "sponge absorb/squeeze over a custom 64-byte-state permutation (mix of add/rotate/sbox), no known constants."),
    ("python", "hg_chaotic_stream.py", S, "keystream from a chaotic map, keyed seed",
     "logistic/tent-map iteration seeded by the key produces a keystream xored with plaintext; invented."),
    ("java", "HgKeyedMix.java", M, "invented keyed hash / MAC",
     "keyed compression: fold message blocks into a state with key-dependent multiply-rotate-xor; output tag."),
    ("go", "hg_lai_massey_ish.go", S, "invented Lai-Massey-flavored cipher (do not name it)",
     "a keyed round mixing two halves through a nonlinear orthomorphism; invented, no textbook name in code."),
    ("c", "hg_double_mix.c", S, "invented two-layer substitution-rotation cipher",
     "two interleaved keyed layers: nibble substitution then whole-block rotation by a key-derived amount; reversible."),
    ("python", "hg_kdf_tree.py", K, "invented tree-structured KDF",
     "derives many subkeys from a master secret via a binary tree of keyed mixing; invented KDF."),
    ("java", "HgFeistelOdd.java", S, "invented Feistel with a nonstandard round fn and count",
     "unbalanced Feistel with a key-dependent round function and odd split; invented."),
    ("go", "hg_wideblock.go", S, "invented wide-block mixing cipher",
     "processes a 1KB block with a keyed pseudo-Hadamard mixing pass then substitution; invented."),
    ("python", "hg_stateful_stream.py", S, "invented self-modifying stream cipher",
     "keystream whose internal state is updated by the ciphertext (self-synchronizing-ish), invented schedule."),
]:
    t5(3, lang, base, True, "custom-"+("mac" if fam == M else ("kdf" if fam == K else ("hash" if fam == H else "cipher"))),
       fam, "no", "synth", False, "", rn, hint)

# ---- subclass 4: constant-obfuscated (8, novel, expect_algo=true) --------------------------------
for lang, base, algo, fam, qv, rn, hint in [
    ("c", "co_aes_sbox_runtime.c", "AES", S, "no", "AES whose S-box is computed at runtime, not a literal table",
     "AES round(s) but the S-box is generated via GF(2^8) inverse + affine at startup instead of a literal 256-byte table."),
    ("python", "co_sha256_constants.py", "SHA-256", H, "no", "SHA-256 with round constants computed from prime cube roots",
     "SHA-256 compression but K[] is computed from fractional cube roots of primes at runtime, not literals."),
    ("go", "co_md5_ttable.go", "MD5", H, "no", "MD5 with its T-table generated from sin() at runtime",
     "MD5 but T[i] = floor(2^32*abs(sin(i+1))) computed at runtime instead of the literal table."),
    ("java", "CoTeaDelta.java", "TEA", S, "no", "TEA whose delta constant is assembled arithmetically",
     "TEA where 0x9E3779B9 is built from arithmetic (golden-ratio derivation) rather than appearing as a literal."),
    ("c", "co_sha1_k.c", "SHA-1", H, "no", "SHA-1 whose four K constants are computed, not literal",
     "SHA-1 but K values derived from sqrt(2),sqrt(3),sqrt(5),sqrt(10) scaling at runtime."),
    ("python", "co_blowfish_pi.py", "Blowfish", S, "no", "Blowfish P-array seeded from pi digits at runtime",
     "Blowfish-style with P-array/S-boxes initialized from computed pi fractional bits rather than literal tables."),
    ("go", "co_rc4_ksa.go", "RC4", S, "no", "RC4 key schedule with no identifying literal",
     "RC4 KSA/PRGA with only the algorithm's structure (256-entry permutation swap loop); no naming, no magic literal."),
    ("java", "CoChachaConst.java", "ChaCha20", S, "no", "ChaCha with its 'expand 32-byte k' constant encoded",
     "ChaCha quarter-round permutation where the four setup constants are byte-decoded from an integer, not literal ASCII."),
]:
    t5(4, lang, base, True, algo, fam, qv, "novel", True, "", rn, hint)

# ---- subclass 5: mislabeled / lying (8) — 4 recall (crypto under benign name) + 4 precision ------
for lang, base, algo, fam, qv, ea, rn, hint in [
    ("python", "ml_compress.py", "AES-CBC", S, "no", True, "function named compress() actually AES-CBC encrypts",
     "def compress(data,key): actually runs AES-CBC (hand-rolled) — the name lies; it is encryption."),
    ("go", "ml_encode.go", "RC4", S, "no", True, "Encode() actually runs an RC4-style stream cipher",
     "func Encode() applies a keyed RC4-like stream cipher; named as encoding."),
    ("java", "MlChecksum.java", "HMAC", M, "no", True, "checksum() is actually a keyed HMAC",
     "long checksum(byte[] msg,byte[] key): computes an HMAC over an opaque hash; named as a checksum."),
    ("c", "ml_serialize.c", "RSA", A, "yes", True, "serialize() actually performs an RSA signature",
     "serialize_record(): does modular exponentiation with a private exponent (RSA signing) amid field packing."),
]:
    t5(5, lang, base, True, algo, fam, qv, "synth", ea, "", rn, hint)
for lang, base, rn, hint in [
    ("python", "ml_encrypt_nop.py", "encrypt() only base64+hex-encodes; no key, reversible, not crypto",
     "def encrypt(data): returns hex(base64(data)). Named 'encrypt' but it is pure reversible encoding — NOT cryptography."),
    ("java", "MlSecureHash.java", "SecureHash class is just djb2; non-crypto hash",
     "class SecureHash with digest() computing djb2 — a non-cryptographic hash-table hash despite the name."),
    ("go", "ml_cipher_text.go", "CipherText() is run-length encoding; not crypto",
     "func CipherText() run-length-encodes its input; the name lies, it is compression."),
    ("c", "ml_rsa_sign.c", "rsa_sign() just appends a constant tag; not crypto",
     "rsa_sign(): concatenates a fixed static byte tag to the message. No math, no key — NOT cryptography despite the name."),
]:
    t5(5, lang, base, False, "", "none", "na", "synth", False, "", rn, hint)

# ---- subclass 6: unusual paradigm / language (8, synth, mostly expect_algo=false) ----------------
for lang, base, is_c, algo, fam, qv, ea, rn, hint in [
    ("python", "up_fold_xor.py", True, "custom-cipher", S, "no", False, "functional-style keyed stream cipher via reduce/lambdas",
     "purely functional: keystream via itertools/reduce, xored with data through map; no loops. still a keyed cipher."),
    ("c", "up_bitsliced_sbox.c", True, "custom-cipher", S, "no", False, "bitsliced substitution layer of a cipher",
     "bitsliced 8-bit sbox applied across a word in parallel via boolean gates; a cipher substitution layer."),
    ("sql", "up_proc_seal.sql", True, "custom-cipher", S, "no", False, "SQL stored procedure doing a keyed byte transform",
     "a PL/pgSQL stored procedure that XOR+rotates a bytea column under a key parameter; keyed reversible transform."),
    ("shell", "up_xor_stream.sh", True, "custom-cipher", S, "no", False, "POSIX shell keyed xor cipher",
     "a shell script that xors stdin with a repeating key via od/printf; a keyed stream cipher."),
    ("go", "up_table_driven.go", True, "custom-cipher", S, "no", False, "table-driven vectorised cipher",
     "processes 8 lanes in parallel with precomputed keyed substitution tables; a block cipher, unusual shape."),
    ("java", "UpRecursiveHash.java", True, "custom-hash", H, "no", False, "recursive/continuation-style compression hash",
     "a hash whose compression is expressed recursively over blocks with an accumulator; unusual control flow."),
    ("awk", "up_stream.awk", True, "custom-cipher", S, "no", False, "AWK keyed stream cipher",
     "an awk script that keystreams input bytes under a key; a stream cipher in an unusual language."),
    ("python", "up_coroutine_ks.py", True, "custom-cipher", S, "no", False, "generator/coroutine keystream cipher",
     "a Python generator yields a keyed keystream consumed lazily and xored; unusual paradigm."),
]:
    t5(6, lang, base, is_c, algo, fam, qv, "synth", ea, "", rn, hint)

# ---- subclass 7: subtly broken (8, novel, expect_algo=true) — minimal bug, not weaponizable ------
for lang, base, algo, fam, qv, rn, hint in [
    ("c", "br_ecb_mode.c", "AES", S, "no", "AES used in ECB where CBC was intended — still AES, a mode weakness",
     "hand-rolled AES encrypting each block independently (ECB) with a comment-free note the design wanted chaining. still crypto."),
    ("go", "br_ctr_reuse.go", "AES-CTR", S, "no", "CTR keystream with a counter that resets each call (nonce reuse)",
     "AES-CTR-style where the counter is re-initialized to 0 every call, reusing keystream. still crypto, subtly broken."),
    ("python", "br_rsa_e_one.py", "RSA", A, "yes", "RSA with public exponent 1 (no real encryption) — still the RSA construction",
     "textbook RSA modexp but e=1 so ciphertext==plaintext; recognizably RSA, subtly broken."),
    ("java", "BrHmacTrunc.java", "HMAC", M, "no", "HMAC keyed with only the first byte of the key",
     "HMAC construction but the key is truncated to 1 byte before use; still HMAC, weakened."),
    ("python", "br_cbc_fixed_iv.py", "AES-CBC", S, "no", "CBC with a hardcoded zero IV",
     "hand-rolled CBC using a fixed all-zero IV every message; still CBC encryption, subtly broken."),
    ("c", "br_sha_rounds.c", "SHA-256", H, "no", "SHA-256 with 56 rounds instead of 64",
     "SHA-256 compression truncated to 56 rounds; recognizably SHA-256, subtly broken."),
    ("go", "br_dh_small.go", "DH", A, "yes", "Diffie-Hellman with a tiny modulus",
     "finite-field DH key exchange using a 32-bit modulus; recognizably DH, insecure by parameter."),
    ("java", "BrRc4Weak.java", "RC4", S, "no", "RC4 with no key-stream drop (weak KSA start)",
     "RC4 KSA/PRGA that uses the first output bytes (no drop-N); still RC4, subtly broken."),
]:
    t5(7, lang, base, True, algo, fam, qv, "novel", True, "", rn, hint)

# ---- subclass 8: split across files (12 = 4 groups x 3), compose_group set ------------------------
# Labeled BY CONSTRUCTION (an expert who sees the group knows each file's role) and EXEMPT from the
# blind per-file agreement gate — because blind per-file labeling failing is exactly the finding.
GROUPS = {
    "g_py_cipher": ("python", [
        ("split_keysched.py", "key-schedule", "derives round subkeys from a master key — a cipher key schedule"),
        ("split_roundfn.py", "cipher-round", "one keyed substitution-permutation round over a state"),
        ("split_driver.py", "CBC-mode", "drives the round fn across blocks with CBC chaining")]),
    "g_go_cipher": ("go", [
        ("split_sbox_gen.go", "sbox", "builds a nonlinear substitution box from a keyed process"),
        ("split_permute.go", "permutation", "applies the cipher's diffusion permutation to a block"),
        ("split_encrypt_loop.go", "round-loop", "runs whitening + N rounds using the other two pieces")]),
    "g_c_cipher": ("c", [
        ("split_mix.c", "diffusion", "linear mixing layer (MixColumns-like) of a block cipher"),
        ("split_subkey.c", "key-schedule", "expands the cipher key into round keys"),
        ("split_cipher_main.c", "block-encrypt", "assembles mixing + subkeys into a full block encrypt")]),
    "g_java_cipher": ("java", [
        ("SplitKeyDeriv.java", "key-schedule", "derives round keys for the cipher"),
        ("SplitBlockMix.java", "cipher-round", "nonlinear + linear round transform on a block"),
        ("SplitSeal.java", "CTR-mode", "produces a keystream from the round transform and xors data")]),
}
for gid, (lang, files) in GROUPS.items():
    for base, prim, rn in files:
        t5(8, lang, base, True, prim, S, "no", "synth", False, gid,
           f"fragment of composed cipher group {gid}: {rn}",
           f"[compose_group {gid}] {rn}. Neutral names; this file alone is NOT recognizable as a full cipher — that is the point.")

# ---- high-fidelity decoys (12, is_crypto=false) --------------------------------------------------
for lang, base, algo, rn, hint in [
    ("c", "dc_sbox_checksum.c", "table checksum", "checksum using an S-box-like table but keyless, not collision-resistant, not crypto",
     "a checksum that indexes a 256-entry table (looks like an sbox) and accumulates; keyless integrity check, NOT crypto."),
    ("python", "dc_reed_solomon.py", "Reed-Solomon", "error-correcting code over GF(256): coding theory, not cryptography",
     "Reed-Solomon encode/syndrome over GF(2^8): forward error correction for noisy channels. Not encryption/keys."),
    ("java", "DcMonteCarlo.java", "simulation PRNG", "PRNG explicitly for Monte Carlo simulation, not security",
     "a well-distributed PRNG seeded from a scenario id, used to drive a Monte Carlo integration; simulation only."),
    ("python", "dc_rolling_dedup.py", "rolling hash", "content-defined chunking rolling hash for dedup; keyless, collisions fine",
     "a polynomial rolling hash over a sliding window to pick chunk boundaries for a backup deduplicator. Not crypto."),
    ("go", "dc_bloom.go", "bloom filter", "bloom-filter hash bank for set membership; non-crypto hashes",
     "several cheap non-crypto hashes combined for a bloom filter membership test. Not cryptography."),
    ("c", "dc_crc_table.c", "CRC-32 table", "table-driven CRC error-detection checksum",
     "table-driven CRC-32 over a buffer; error detection, keyless, NOT crypto."),
    ("go", "dc_consistent_hash.go", "consistent hashing", "hash ring for shard placement; non-crypto",
     "maps keys onto a ring of nodes using a fast non-crypto hash for sharding. Not cryptography."),
    ("python", "dc_dhash.py", "perceptual hash", "image difference-hash for similarity; not crypto",
     "computes a dHash perceptual fingerprint of a small grayscale matrix for near-duplicate image detection."),
    ("java", "DcRotChecksum.java", "rotating checksum", "keyless rotate-add checksum that looks MAC-like",
     "a rotate-and-add running checksum over bytes; resembles a MAC loop but is keyless integrity only."),
    ("go", "dc_cas_key.go", "content hash", "content-addressable store key via non-crypto hash",
     "derives a storage key by hashing content with a fast non-crypto hash for a CAS cache. Not crypto."),
    ("python", "dc_geohash.py", "geohash", "interleaves lat/long bits into a base32 locator; encoding",
     "geohash encoding of coordinates: bit interleaving + base32. A spatial encoding, not cryptography."),
    ("java", "DcHyperLogLog.java", "HyperLogLog", "cardinality estimation using a non-crypto hash",
     "HyperLogLog distinct-count estimator using a fast hash of items; probabilistic counting, not crypto."),
]:
    t5("decoy", lang, base, False, algo, "none", "na", "synth", False, "", rn, hint)

# ---- crypto_adjacent_review (4): non-crypto PRNGs used to source keys/nonces (is_crypto="review") -
for lang, base, algo, rn, hint in [
    ("python", "rv_prng_keygen.py", "LCG", "non-crypto LCG used to generate a 'session key' — surface for review",
     "uses a linear congruential generator to produce bytes labeled a session key. PRNG is non-crypto; usage is review-worthy."),
    ("go", "rv_nonce_gen.go", "xorshift", "xorshift used to make nonces — review, not crypto itself",
     "xorshift PRNG producing values used as nonces. PRNG is non-crypto; flag for 'verify not security-critical'."),
    ("java", "RvIvSource.java", "Mersenne Twister", "MT19937 used to make IVs — review",
     "Mersenne Twister producing IV bytes. Non-crypto generator; review because used for an IV."),
    ("c", "rv_salt_maker.c", "rand()", "libc rand() used to make a salt — review",
     "uses rand() to fill a salt buffer. Non-crypto RNG; review-worthy given the security-adjacent use."),
]:
    t5("review", lang, base, "review", algo, "rng", "na", "synth", False, "", rn, hint)


# ---- provided seed fixtures (reworded leak-free, placed by hand — generation skips existing files) --
t5(2, "python", "license_seal.py", True, "custom-cipher", S, "no", "synth", False, "",
   "keyed stream cipher (payload XOR key-derived keystream) disguised as billing license-seal issuance",
   "[seed] homegrown keyed stream cipher fused into a billing license-seal API.")
t5(3, "c", "obscure_xform.c", True, "custom-cipher", S, "no", "synth", False, "",
   "invented keyed substitution + byte-chaining transform, reversible with the key, matching no textbook cipher",
   "[seed] homegrown non-canonical reversible keyed byte transform.")
t5("decoy", "python", "rolling_dedup.py", False, "rolling hash", "none", "na", "synth", False, "",
   "keyless polynomial rolling fingerprint for dedup chunking — modular arithmetic that resembles crypto but has no key or security goal",
   "[seed] non-crypto rolling hash for content-defined chunking.")

# =================================================================== ESCALATION ROUND ============
# Targets the two forms that broke detection last run: fused-into-business-logic (#2) and
# split-across-files (#8). Deeper fusion / finer fragmentation to push LLM recall lower.

# ---- deep subclass 2: keyed crypto that MIMICS a mundane op, buried in heavy domain code ---------
for lang, base, fam, rn, hint in [
    ("python", "d2_row_version.py", "mac",
     "keyed MAC over DB row bytes presented as a plain 'row version checksum' amid ORM bookkeeping",
     "compute_row_version(): heavy ORM-ish code (field extraction, type coercion, logging) that folds row bytes with a server secret through a keyed compression to a tag returned as a 'version'. The key makes it a MAC."),
    ("go", "d2_idempotency.go", "mac",
     "keyed request MAC framed as an 'idempotency key' inside an HTTP handler",
     "IdempotencyKey(): canonicalizes an HTTP request (method/path/body/headers) then keys a compression with a service secret to produce the 'key'. Surrounded by routing/validation noise."),
    ("java", "D2ColumnPack.java", "symmetric",
     "keyed stream transform over an export blob framed as 'column packing / serialization'",
     "packColumns(): serializes rows into a byte buffer, then applies a key-derived keystream XOR over the packed bytes before returning; framed purely as an export/serialization step."),
    ("c", "d2_dedup_key.c", "mac",
     "keyed hash over an event framed as a 'dedup key' in an ingestion pipeline",
     "make_dedup_key(): parses an event struct, then mixes its bytes with a pipeline secret through a keyed rolling compression to a fixed-size key; framed as deduplication."),
    ("python", "d2_precompress.py", "symmetric",
     "keyed reversible transform framed as a 'compression preprocessing' pass",
     "preprocess(): claims to improve compression ratio by 'decorrelating' bytes, but actually applies a key-derived reversible byte transform (keyed) with a matching restore(); it is a cipher."),
    ("go", "d2_cache_salt.go", "kdf",
     "keyed derivation framed as 'cache key salting' in a caching layer",
     "saltedCacheKey(): stretches a tenant secret + item id through an iterated keyed mixing (a KDF) to derive the cache key; wrapped in cache get/set plumbing."),
    ("java", "D2ConfigValidate.java", "mac",
     "keyed integrity tag over config framed as a 'config validation checksum'",
     "validateConfig(): after schema checks, computes a keyed tag over the config bytes with an app secret and compares; framed as validation, but the keyed tag is a MAC."),
    ("c", "d2_transport_encode.c", "symmetric",
     "keyed stream framed as 'message encoding for transport'",
     "encode_for_transport(): frames a message (length prefix, escaping) then applies a key-derived keystream over the payload; framed as an encoding/framing step."),
    ("python", "d2_audit_seq.py", "mac",
     "keyed chained MAC framed as an 'audit sequence number' generator",
     "next_audit_seq(): chains each audit record through a keyed block-ish compression seeded by the previous tag (a keyed chained MAC) but returns it as a monotonic-looking 'sequence'."),
    ("go", "d2_token_format.go", "symmetric",
     "keyed transform framed as 'session token formatting'",
     "formatSessionToken(): assembles session claims, then applies a keyed reversible mixing over the claim bytes before base32 framing; framed as formatting, but it is keyed encryption."),
]:
    t5(2, lang, base, True, "custom-"+("mac" if fam == "mac" else ("kdf" if fam == "kdf" else "cipher")),
       fam, "no", "synth", False, "", rn, hint)

# ---- deep subclass 8: finer fragmentation — one cipher split into 4 tiny files per group ----------
DEEP_GROUPS = {
    "gg_py": ("python", [
        ("dp_sub.py", "sbox", "builds a nonlinear byte-substitution table from a seed"),
        ("dp_key.py", "key-schedule", "expands a master key into round subkeys"),
        ("dp_perm.py", "permutation", "applies a fixed bit/byte diffusion permutation to a block"),
        ("dp_core.py", "block-encrypt", "assembles substitution + subkeys + permutation into round-based block processing")]),
    "gg_go": ("go", [
        ("dg_sub.go", "sbox", "generates a substitution table"),
        ("dg_key.go", "key-schedule", "derives round keys"),
        ("dg_perm.go", "permutation", "diffusion/mixing layer over a block"),
        ("dg_core.go", "round-loop", "whitening + rounds using the sibling pieces")]),
    "gg_c": ("c", [
        ("ec_sub.c", "sbox", "fills a substitution table"),
        ("ec_key.c", "key-schedule", "expands round keys"),
        ("ec_perm.c", "diffusion", "linear mixing over the state"),
        ("ec_core.c", "block-encrypt", "combines the pieces into a block transform")]),
    "gg_java": ("java", [
        ("DjSub.java", "sbox", "constructs a substitution table"),
        ("DjKey.java", "key-schedule", "derives round keys"),
        ("DjPerm.java", "permutation", "diffusion permutation over a block"),
        ("DjCore.java", "block-encrypt", "assembles the round-based cipher")]),
}
for gid, (lang, files) in DEEP_GROUPS.items():
    for base, prim, rn in files:
        t5(8, lang, base, True, prim, S, "no", "synth", False, gid,
           f"fragment of composed cipher group {gid}: {rn}",
           f"[compose_group {gid}] {rn}. Neutral names; individually innocuous, only the group is a cipher.")


# =================================================================== ESCALATION ROUND 2 ==========
# The escalation showed the LLM's blind spot is split-cipher SUBSTITUTION / PERMUTATION / MIX
# fragments (the sub/perm pieces missed; key/core were caught). This round isolates those fragment
# types into their own tiny files — 5 fragments per group, 3 of them the blind-spot kinds — to push
# file-level recall lower. Labelled by construction (compose_group, gate-exempt), expect_algo=false.
FINER_GROUPS = {
    "fg_py": ("python", [
        ("fp_sbox.py", "sbox", "builds a nonlinear byte-substitution table from a seed value"),
        ("fp_isbox.py", "inverse-sbox", "builds the inverse of the substitution table"),
        ("fp_perm.py", "permutation", "reorders the bytes of a block by a fixed pattern"),
        ("fp_mix.py", "diffusion", "linear inter-byte mixing pass over a block"),
        ("fp_core.py", "block-encrypt", "assembles table + permute + mix + subkeys into rounds")]),
    "fg_go": ("go", [
        ("fg_sbox.go", "sbox", "generates a substitution table"),
        ("fg_perm.go", "permutation", "applies a fixed byte-reordering to a block"),
        ("fg_mix.go", "diffusion", "linear mixing layer over the block state"),
        ("fg_key.go", "key-schedule", "expands a key into round values"),
        ("fg_core.go", "round-loop", "runs whitening + rounds using the siblings")]),
    "fg_c": ("c", [
        ("fc_sbox.c", "sbox", "fills a substitution table"),
        ("fc_isbox.c", "inverse-sbox", "fills the inverse substitution table"),
        ("fc_perm.c", "permutation", "reorders state bytes"),
        ("fc_mix.c", "diffusion", "xtime-based linear mixing of the state"),
        ("fc_core.c", "block-encrypt", "combines the pieces into a block transform")]),
    "fg_java": ("java", [
        ("FjSbox.java", "sbox", "constructs a substitution table"),
        ("FjPerm.java", "permutation", "reorders block bytes"),
        ("FjMix.java", "diffusion", "linear mixing over a block"),
        ("FjKey.java", "key-schedule", "derives round values"),
        ("FjCore.java", "block-encrypt", "assembles the round-based transform")]),
}
for gid, (lang, files) in FINER_GROUPS.items():
    for base, prim, rn in files:
        t5(8, lang, base, True, prim, S, "no", "synth", False, gid,
           f"fragment of composed cipher group {gid}: {rn}",
           f"[compose_group {gid}] {rn}. Neutral names; individually innocuous, only the group is a cipher.")


BATCH_OF = lambda sub: f"s{sub}"  # subclass id used as the generation batch


def by_subclass(sub):
    return [r for r in T5 if str(r["subclass"]) == str(sub)]


if __name__ == "__main__":
    import collections
    print("tier5 total:", len(T5))
    print("by subclass:", dict(collections.Counter(str(r["subclass"]) for r in T5)))
    print("by lang    :", dict(collections.Counter(r["lang"] for r in T5)))
    print("by split   :", dict(collections.Counter(r["split"] for r in T5)))
    print("is_crypto  :", dict(collections.Counter(str(r["is_crypto"]) for r in T5)))
    print("compose groups:", sorted({r["compose_group"] for r in T5 if r["compose_group"]}))
    # rationale required on every row
    miss = [r["path"] for r in T5 if not r["rationale"]]
    print("rows missing rationale:", miss or "none")
