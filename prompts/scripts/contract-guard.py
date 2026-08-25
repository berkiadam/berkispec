#!/usr/bin/env python3
"""VD3a szerződés-integritás kapu — determinisztikusan, LLM nélkül (07-validate).

Miért kell: a fixer visszatérése után az orchestrátornak ellenőriznie kell,
hogy a javítás a KÓDOT igazította-e a szerződéshez (teszt / DoD / review-finding),
és nem fordítva. Ma ehhez minden iterációban be kell olvasnia a teljes `git diff`-et
— ez a hurok egyik legdrágább, ugyanakkor nagyrészt gépi lépése.

Mit néz:
  1. **Érintett-e védett útvonal:** tesztfájlok/mappák, `spec.md`,
     `test-report/code-review.md`, Sonar-/lint-konfig.
  2. **Klasszikus csalás-minták a HOZZÁADOTT sorokban:** `.skip(`, `xit(`,
     `xdescribe(`, `@pytest.mark.skip`, `pytest.skip(`, `@Disabled`, `@Ignore`,
     `t.Skip(`, `NOSONAR`, `eslint-disable`, `@ts-ignore`, `@ts-expect-error`,
     `// nosonar`, `#pragma warning disable`.
  3. **Eltávolított assertionök:** törölt sorok, amelyek `expect(` / `assert` /
     `Assert.` / `should.` mintát tartalmaznak (assertion-gyengítés jele).
  4. **Elnémított review-finding:** a `code-review.md`-ből eltűnt vagy `[x]`-re
     állított `- [ ] **MF-NN**` sor — a fixer nem zárhat le findingot magától.
  5. **Leszállított DoD:** a `spec.md`-ből törölt vagy átírt `DoD-NN` sor
     (a `[ ]` → `[x]` pipálás legitim, a szöveg megváltoztatása nem).

Kimenet: egy `VERDICT:` sor + a találatok fájl:sor szinten.
  VERDICT: CLEAN    → egyetlen védett útvonal sem változott → az orchestrátor
                      EL SEM OLVASSA a diffet, mehet az újra-validálás
  VERDICT: REVIEW   → védett útvonal változott, de csalás-mintát nem találtam
                      → az orchestrátor nézze át a felsorolt hunkokat
  VERDICT: SUSPECT  → csalás-mintát találtam → STOP-jelölt: visszaállítás
                      (`git checkout --`) + VD5 eszkaláció

Kilépő kód: 0 = CLEAN
            1 = REVIEW vagy SUSPECT (a `VERDICT:` sor mondja meg, melyik)
            2 = használati hiba (nincs git / nem létező ciklusmappa)

A tesztútvonalakat a `conventions.md` `## Teszt struktúra` szekciójából próbálja
kiolvasni; ami onnan nem jön, azt beépített heurisztika pótolja (`test/`,
`tests/`, `spec/`, `__tests__/`, `*.test.*`, `*.spec.*`, `*_test.py`, `*Test.java`).
Extra útvonalat a `--test-path` / `--config-path` kapcsolóval adhatsz meg.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

from lang_keys import sec

CHEAT_PATTERNS = [
    (r"\.skip\s*\(", "teszt kihagyása (.skip)"),
    (r"\bxit\s*\(|\bxdescribe\s*\(|\bfit\s*\(\s*$", "kihagyott/kizárt teszt (xit/xdescribe)"),
    (r"@pytest\.mark\.skip|pytest\.skip\s*\(", "pytest skip"),
    (r"@Disabled|@Ignore\b", "JUnit/TestNG kikapcsolt teszt"),
    (r"\bt\.Skip\s*\(", "Go teszt skip"),
    (r"NOSONAR|//\s*nosonar", "Sonar-szabály elnémítása"),
    (r"eslint-disable", "ESLint szabály kikapcsolása"),
    (r"@ts-ignore|@ts-expect-error", "TypeScript hibaelnyomás"),
    (r"#pragma warning disable", "fordítói figyelmeztetés elnyomása"),
    (r"\.only\s*\(", "teszt-készlet szűkítése (.only)"),
]
ASSERTION_RE = re.compile(r"\bexpect\s*\(|\bassert\b|Assert\.|should\.|\.should\b|EXPECT_")
TEST_PATH_HINTS = ["test/", "tests/", "spec/", "specs/__tests__/", "__tests__/", "e2e/", "it/"]
TEST_FILE_RE = re.compile(r"(\.test\.|\.spec\.|_test\.py$|_test\.go$|Test\.java$|Tests?\.cs$|test_.*\.py$)")
CONFIG_HINTS = ["sonar-project.properties", "sonar-project.js", ".eslintrc", "eslint.config",
                "ruff.toml", ".flake8", "pyproject.toml", "tslint.json", "checkstyle.xml",
                "sonar.properties", ".sonarcloud.properties"]


def git(args, cwd=None):
    try:
        out = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True,
                             encoding='utf-8', errors='replace', check=False)
    except FileNotFoundError:
        return None
    if out.returncode != 0:
        return None
    return out.stdout


def parse_test_paths(conventions):
    """A `## Teszt struktúra` szekcióból backtickes útvonalak kiszedése."""
    text = None
    try:
        text = Path(conventions).read_text(encoding="utf-8")
    except Exception:
        return []
    m = re.search(r"^#+\s*" + re.escape(sec("cv_test_structure")) + r".*$",
                  text, re.MULTILINE | re.IGNORECASE)
    if not m:
        return []
    tail = text[m.end():]
    nxt = re.search(r"^#+\s", tail, re.MULTILINE)
    block = tail[: nxt.start()] if nxt else tail
    paths = re.findall(r"`([^`]+)`", block)
    return [p.strip() for p in paths if "/" in p or p.startswith(".")]


def is_test_file(path, extra_paths):
    low = path.lower()
    if TEST_FILE_RE.search(path):
        return True
    for hint in TEST_PATH_HINTS + [p.lower() for p in extra_paths]:
        h = hint.lower().strip("/")
        if h and (low.startswith(h + "/") or f"/{h}/" in low):
            return True
    return False


def classify(path, cycle_rel, extra_tests, extra_configs):
    if path.endswith("spec.md") and cycle_rel in path:
        return "spec.md (DoD — szerződés)"
    if path.endswith("code-review.md"):
        return "code-review.md (review-findingok)"
    for hint in CONFIG_HINTS + extra_configs:
        if path.endswith(hint) or hint in path:
            return "Sonar/lint konfiguráció"
    if is_test_file(path, extra_tests):
        return "tesztfájl"
    return None


DOD_ID_RE = re.compile(r"DoD-\d+")


def _dod_key(line):
    """A DoD-sor azonosítója és a checkbox-tól megtisztított szövege."""
    m = DOD_ID_RE.search(line)
    if not m:
        return None, None
    text = re.sub(r"^\s*- \[[ xX]\]\s*", "", line).strip()
    return m.group(0), text


def compare_dod(removed, added):
    """Csak a TÉNYLEGES szövegváltozás vagy törlés gyanús — a `[ ] → [x]`
    pipálás legitim (azt a 07 orchestrátora és a `dod-check.py --apply` végzi)."""
    add_map = {}
    for _path, line in added:
        key, text = _dod_key(line)
        if key:
            add_map.setdefault(key, []).append(text)
    out = []
    for path, line in removed:
        key, text = _dod_key(line)
        if not key:
            continue
        if key not in add_map:
            out.append((path, f"TÖRÖLVE: {line.strip()[:120]}"))
        elif text not in add_map[key]:
            out.append((path, f"ÁTÍRVA: {line.strip()[:120]}"))
    return out


def _force_utf8_output():
    """Windows-kompatibilitás: a konzol örökölt kódlapja (cp852 / cp1250 / cp1252)
    nem tudja megjeleníteni a kimenet tipográfiai és ékezetes karaktereit (✓, ✗, —, ő),
    és a `print()` ilyenkor `UnicodeEncodeError`-t dob. Ez azért veszélyes, mert a
    kivétel AZUTÁN keletkezne, hogy a szkript a fájlműveletet már elvégezte: a hívó
    ágens hibás kilépő kódot látna egy sikeres művelet után. Ezért a kimenetet
    UTF-8-ra kapcsoljuk, hibatűrő módban (Python 3.7+; régebbin csendben kimarad)."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

def main():
    _force_utf8_output()
    parser = argparse.ArgumentParser(description="VD3a szerződés-integritás kapu.")
    parser.add_argument("cycle_dir", help="a ciklus mappája (specs/cycle-NN-<name>)")
    parser.add_argument("--conventions", default="conventions.md")
    parser.add_argument("--base", default=None,
                        help="összehasonlítási alap (alap: a munkafa a HEAD-hez képest)")
    parser.add_argument("--test-path", action="append", default=[])
    parser.add_argument("--config-path", action="append", default=[])
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()

    cycle = Path(args.cycle_dir)
    if not cycle.is_dir():
        print(f"HIBA: nincs ilyen ciklusmappa: {cycle}", file=sys.stderr)
        return 2
    if git(["rev-parse", "--git-dir"], cwd=args.repo) is None:
        print("HIBA: nem git repó (vagy nincs git) — a VD3a kapu nem futtatható.", file=sys.stderr)
        return 2

    diff_args = ["diff", "--unified=0"]
    if args.base:
        diff_args.append(args.base)
    else:
        diff_args.append("HEAD")
    diff = git(diff_args, cwd=args.repo)
    if diff is None:
        diff = git(["diff", "--unified=0"], cwd=args.repo) or ""

    extra_tests = parse_test_paths(args.conventions) + args.test_path
    cycle_rel = cycle.as_posix()

    current = None
    kind = None
    touched = {}
    suspects = []
    removed_asserts = {}
    removed_findings = []
    removed_dod = []
    added_dod = []

    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            current = line[6:].strip()
            kind = classify(current, cycle_rel, extra_tests, args.config_path)
            if kind:
                touched.setdefault(current, kind)
            continue
        if not current or not kind:
            continue
        if line.startswith("+") and not line.startswith("+++"):
            body = line[1:]
            if current.endswith("spec.md") and re.search(r"DoD-\d+", body):
                added_dod.append((current, body))
            for pat, label in CHEAT_PATTERNS:
                if re.search(pat, body):
                    suspects.append((current, label, body.strip()[:120]))
        elif line.startswith("-") and not line.startswith("---"):
            body = line[1:]
            if ASSERTION_RE.search(body):
                removed_asserts[current] = removed_asserts.get(current, 0) + 1
            if current.endswith("code-review.md") and re.search(r"- \[ \].*MF-\d+", body):
                removed_findings.append((current, body.strip()[:120]))
            if current.endswith("spec.md") and re.search(r"DoD-\d+", body):
                removed_dod.append((current, body))

    changed_dod = compare_dod(removed_dod, added_dod)

    print(f"VD3a szerződés-integritás kapu — {cycle}")
    if not touched:
        print("  ✓ egyetlen védett útvonal sem változott")
        print("VERDICT: CLEAN")
        return 0

    print("  Érintett védett útvonalak:")
    for path, k in sorted(touched.items()):
        print(f"    · {path}  [{k}]")

    for path, label, body in suspects:
        print(f"  ✗ CSALÁS-MINTA — {path}: {label}\n      + {body}")
    for path, count in removed_asserts.items():
        print(f"  ✗ ELTÁVOLÍTOTT ASSERTION — {path}: {count} sor")
    for path, body in removed_findings:
        print(f"  ✗ ELNÉMÍTOTT FINDING — {path}\n      - {body}")
    for path, body in changed_dod:
        print(f"  ✗ MEGVÁLTOZTATOTT DoD-SOR — {path}\n      - {body}")

    if suspects or removed_asserts or removed_findings or changed_dod:
        print("VERDICT: SUSPECT")
        print("Teendő: `git checkout -- <fájl>` visszaállítás, majd VD5 eszkalációs ág — "
              "ne indíts újabb fixert ugyanarra az itemre.")
        return 1

    print("  · csalás-mintát nem találtam — nézd át a fenti fájlok diffjét "
          "(legitim lehet: új teszt a hibához, DoD-pipálás, MF-NN pótlás)")
    print("VERDICT: REVIEW")
    return 1


if __name__ == "__main__":
    sys.exit(main())
