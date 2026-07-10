# Sonar Cryptography baseline (real incumbent)

`run_sonar.py` drives the **IBM Sonar Cryptography** SonarQube plugin
(<https://github.com/IBM/sonar-cryptography>) over the corpus and normalises its output to the
standard finding schema (`results/sonar.jsonl`, one JSON per file). This is the *real* incumbent
proxy; `detectors/regex_baseline.py` is only the quick offline stand-in.

## What it detects (and what it can't)
- **Analysed languages:** Java (JCA + BouncyCastle), Python (pyca/cryptography), Go (stdlib `crypto`).
- **Not analysed:** C, and the tier-5 unusual-language fixtures (`.sql` / `.sh` / `.awk`). These are
  emitted with `is_crypto: null` and evidence `unsupported-language:<lang>` — a **no-verdict**, which
  `eval/score.py` excludes from precision/recall and reports as coverage (never counted as a miss).
- **Library/API only:** it recognises known crypto API calls; it does **not** detect hand-rolled /
  library-less crypto (tiers 2–5). That blind spot is exactly the wedge this benchmark measures.

Because ~1/4 of the corpus is C/exotic, Sonar's *coverage* is itself a headline: it cannot even look
at those files, independent of detection quality.

## Running it
`python run.py --detector sonar` orchestrates everything via **Docker** (default):
1. downloads the latest plugin JAR from the IBM releases,
2. boots `sonarqube:9.9-community`, installs the plugin, restarts,
3. runs `sonarsource/sonar-scanner-cli` over the corpus,
4. retrieves the plugin's `cbom.json` (CycloneDX CBOM) and maps `cryptographic-asset` occurrences
   back to files.

Requirements: Docker + network. SonarQube embeds Elasticsearch, which needs
`sysctl -w vm.max_map_count=262144` on the host (common failure in sandboxes). If the toolchain or
boot is unavailable, supported files are emitted with `is_crypto: null` and evidence
`sonar-not-run:<reason>` so the pipeline still completes and the gap is explicit.

Env knobs: `SONAR_SKIP_RUN=1` (partition only, no Docker), `SONAR_IMAGE`, `SONAR_SCANNER_IMAGE`.

## Manual setup (no Docker)
Install SonarQube 9.9 LTS+, copy the plugin JAR into `$SONARQUBE_HOME/extensions/plugins`, restart,
run `sonar-scanner` over `corpus/`, then point `run_sonar.py` at the produced `cbom.json`.
