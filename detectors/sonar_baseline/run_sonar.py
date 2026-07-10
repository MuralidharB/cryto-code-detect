"""
Sonar Cryptography baseline — the REAL incumbent proxy (IBM Sonar Cryptography SonarQube plugin).

Unlike detectors/regex_baseline.py (a quick textual stand-in), this drives the actual IBM plugin
(https://github.com/IBM/sonar-cryptography), which does AST-based detection of crypto *library/API*
usage inside SonarQube and emits a CycloneDX CBOM (cbom.json). We run it, map the CBOM's crypto-asset
occurrences back to corpus files, and normalise to the standard finding schema (one JSON per line).

WHAT THE PLUGIN CAN AND CANNOT SEE (documented, and load-bearing for the benchmark):
  - Languages analysed: Java (JCA + BouncyCastle), Python (pyca/cryptography), Go (stdlib crypto).
  - NOT analysed: C, and the tier-5 unusual-language fixtures (sql/shell/awk). Those files are emitted
    with is_crypto=null and evidence "unsupported-language:<lang>" — a NO-VERDICT, excluded from the
    detector's precision/recall (eval/score.py skips null findings and reports coverage separately).
    Never scored as a miss: penalising Sonar for a language it doesn't support would be dishonest.
  - Detection is library/API only — it will miss all hand-rolled/library-less crypto (tiers 2-5),
    which is exactly the wedge this benchmark measures.

ORCHESTRATION (default): boot SonarQube + the plugin in Docker, run sonar-scanner over the corpus,
retrieve cbom.json, parse it. Requires Docker and network (to pull images + the plugin release).
If the toolchain/boot is unavailable, every SUPPORTED file is emitted with is_crypto=null and
evidence "sonar-not-run:<reason>" so `python run.py --detector sonar` still completes cleanly and the
gap is visible rather than silently wrong. Set SONAR_SKIP_RUN=1 to force partition-only (no Docker).

Emits one finding JSON per file to stdout (run.py redirects to results/sonar.jsonl).
Diagnostics go to stderr so they never contaminate the JSONL.
"""
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

EXT_LANG = {".py": "python", ".java": "java", ".go": "go", ".c": "c", ".h": "c",
            ".sql": "sql", ".sh": "shell", ".awk": "awk"}
SUPPORTED = {"python", "java", "go"}          # languages the IBM plugin analyses
SONAR_IMAGE = os.environ.get("SONAR_IMAGE", "sonarqube:9.9-community")
SCANNER_IMAGE = os.environ.get("SONAR_SCANNER_IMAGE", "sonarsource/sonar-scanner-cli:latest")
PLUGIN_RELEASE_API = "https://api.github.com/repos/IBM/sonar-cryptography/releases/latest"
HOST = "http://localhost:9000"


def log(*a):
    print("[sonar]", *a, file=sys.stderr, flush=True)


def emit(fp, is_crypto, evidence, algo=None, family=None, qv="na", conf=0.0):
    print(json.dumps({"filepath": fp, "is_crypto": is_crypto, "primary_algorithm": algo,
                      "family": family, "quantum_vulnerable": qv, "evidence": evidence,
                      "confidence": conf}))


# --------------------------------------------------------------------------- CBOM parsing
def cbom_crypto_files(cbom: dict, corpus_root: Path) -> set[str]:
    """Return the set of corpus-relative filepaths the CBOM flags as containing a crypto asset.

    CycloneDX CBOM: components[] of type 'cryptographic-asset'; each carries evidence.occurrences[]
    with a 'location' (source file path). We normalise those paths back to corpus-relative form."""
    hit = set()
    for comp in cbom.get("components", []):
        if comp.get("type") not in ("cryptographic-asset", "crypto-asset"):
            continue
        occ = (comp.get("evidence") or {}).get("occurrences") or []
        for o in occ:
            loc = o.get("location") or o.get("line") or ""
            if not loc:
                continue
            # location may be absolute (container path) or project-relative; keep the corpus/... tail
            loc = loc.replace("\\", "/")
            idx = loc.find("corpus/")
            hit.add(loc[idx:] if idx >= 0 else loc.lstrip("/"))
    return hit


# --------------------------------------------------------------------------- Docker orchestration
def _docker_ok() -> bool:
    try:
        subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       check=True, timeout=30)
        return True
    except Exception:
        return False


def _get(url, data=None, auth=None, timeout=30):
    req = urllib.request.Request(url, data=data)
    if auth:
        import base64
        req.add_header("Authorization", "Basic " + base64.b64encode(auth.encode()).decode())
    return urllib.request.urlopen(req, timeout=timeout).read()


def _wait_up(timeout=300) -> bool:
    start = time.monotonic()
    while time.monotonic() - start < timeout:
        try:
            st = json.loads(_get(f"{HOST}/api/system/status"))
            if st.get("status") == "UP":
                return True
            log("SonarQube status:", st.get("status"))
        except Exception:
            pass
        time.sleep(5)
    return False


def download_plugin(dest: Path) -> Path | None:
    try:
        rel = json.loads(_get(PLUGIN_RELEASE_API))
        jar = next(a["browser_download_url"] for a in rel["assets"] if a["name"].endswith(".jar"))
        log("downloading plugin", jar)
        dest.write_bytes(_get(jar, timeout=120))
        return dest
    except Exception as e:
        log("plugin download failed:", e)
        return None


def run_full(corpus_root: Path) -> tuple[set[str], str | None]:
    """Boot SonarQube+plugin, scan the corpus, return (set of crypto files, error-or-None)."""
    if os.environ.get("SONAR_SKIP_RUN"):
        return set(), "SONAR_SKIP_RUN set"
    if not _docker_ok():
        return set(), "docker unavailable"
    work = corpus_root.parent / ".sonar_work"
    work.mkdir(exist_ok=True)
    plugin = download_plugin(work / "sonar-cryptography.jar")
    if not plugin:
        return set(), "plugin unavailable"
    try:
        subprocess.run(["docker", "rm", "-f", "sqbench"], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        log("starting", SONAR_IMAGE)
        subprocess.run(["docker", "run", "-d", "--name", "sqbench", "-p", "9000:9000",
                        "-e", "SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true", SONAR_IMAGE],
                       check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["docker", "cp", str(plugin),
                        "sqbench:/opt/sonarqube/extensions/plugins/"], check=True,
                       stdout=subprocess.DEVNULL)
        subprocess.run(["docker", "restart", "sqbench"], check=True, stdout=subprocess.DEVNULL)
        if not _wait_up():
            return set(), "SonarQube did not reach status=UP (often ES vm.max_map_count in sandboxes)"
        # first-run forces a password change for admin/admin; then use basic auth for the scan
        try:
            _get(f"{HOST}/api/users/change_password",
                 data=b"login=admin&previousPassword=admin&password=benchAdmin1!", auth="admin:admin")
        except Exception:
            pass
        log("running scanner over", corpus_root)
        scan = subprocess.run(
            ["docker", "run", "--rm", "--network", "host", "-v", f"{corpus_root}:/usr/src",
             SCANNER_IMAGE, "-Dsonar.projectKey=cryptobench", "-Dsonar.sources=.",
             f"-Dsonar.host.url={HOST}", "-Dsonar.login=admin", "-Dsonar.password=benchAdmin1!"],
            capture_output=True, text=True, timeout=1200)
        if scan.returncode != 0:
            return set(), f"scanner failed: {scan.stderr[-400:]}"
        cbom_path = next(corpus_root.rglob("cbom.json"), None) or (work / "cbom.json")
        if not cbom_path.exists():
            return set(), "cbom.json not produced by the plugin"
        return cbom_crypto_files(json.loads(cbom_path.read_text()), corpus_root), None
    except subprocess.TimeoutExpired:
        return set(), "scan timed out"
    except Exception as e:
        return set(), f"orchestration error: {e}"
    finally:
        subprocess.run(["docker", "rm", "-f", "sqbench"], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)


def main(corpus_dir):
    root = Path(corpus_dir).resolve()
    files = [f for f in sorted(root.rglob("*"))
             if f.is_file() and f.name != "manifest.csv" and "_adjudication" not in f.parts]
    supported = [f for f in files if EXT_LANG.get(f.suffix) in SUPPORTED]
    log(f"{len(files)} files; {len(supported)} in Sonar-supported languages (java/python/go)")

    crypto_files, err = run_full(root) if supported else (set(), "no supported files")
    if err:
        log("NO LIVE VERDICT for supported files:", err)

    for f in files:
        rel = f.relative_to(root.parent).as_posix() if (root.parent / "corpus") in [root, *root.parents] \
            else f.as_posix()
        # normalise to the same corpus/... form the manifest uses
        rp = f.as_posix()
        idx = rp.find("corpus/")
        rel = rp[idx:] if idx >= 0 else rp
        lang = EXT_LANG.get(f.suffix, "other")
        if lang not in SUPPORTED:
            emit(rel, None, f"unsupported-language:{lang}")            # no verdict, excluded from scoring
        elif err:
            emit(rel, None, f"sonar-not-run:{err[:60]}")               # no verdict (toolchain absent)
        elif rel in crypto_files or any(rel.endswith(c) or c.endswith(rel) for c in crypto_files):
            emit(rel, True, "sonar-cryptography CBOM crypto-asset occurrence", conf=0.9)
        else:
            emit(rel, False, "no crypto-asset in CBOM (library/API not detected)", conf=0.9)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "corpus")
