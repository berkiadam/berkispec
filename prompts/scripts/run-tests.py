#!/usr/bin/env python3
"""Teszt-futtató a plan.md gépi táblájából — a nyers teszt-log soha nem kerül
LLM-kontextusba (07-validate, TR1/TR2).

Miért kell: ma a `test-runner` subagent minden körben újraolvassa a `plan.md`-t
(több száz sor) ÉS a nyers teszt-kimenetet (E2E-nél tíz-százezres nagyságrend),
hogy a végén egyetlen `X passed / Y failed / Z skipped` sort adjon vissza.
A futtatás és a számlálás gépi munka: ez a szkript elvégzi, és 10-20 sorban
válaszol. A bizonyíték (JUnit XML, HTML-riport) a kör-mappába kerül.

A parancsok forrása a `plan.md` `## Tesztelési stratégia` szekciójában lévő
**gépi futtatási tábla** — a próza megmarad embernek, ez a szkriptnek:

  ### Gépi futtatási tábla (run-tests.py)

  | Kategória | Típus | Előfeltétel | Parancs | Eredményfájl | Formátum | Takarítás |
  |---|---|---|---|---|---|---|
  | unit | gyors | — | `npm test -- --run --reporter=junit --outputFile=junit.xml` | `junit.xml` | junit | — |
  | e2e  | nehéz | `docker compose -f docker-compose.e2e.yml up -d --wait` | `npx playwright test --reporter=junit` | `results.xml` | junit | `docker compose ... down -v` |

  · **Típus:** `gyors` (unit/integration/typecheck — könnyű körben is fut) vagy
    `nehéz` (E2E/regresszió — csak teljes körben, VD10).
  · **Előfeltétel / Takarítás:** `;`-vel több parancs is megadható. A takarítás
    akkor is lefut, ha a futtatás elszállt.
  · **Eredményfájl:** a repóhoz képest relatív; a szkript a kör-mappába másolja.
  · **Formátum:** `junit` (alap) vagy `text` (a stdout-ból regexszel számol).
  · A `{round}` helyőrző a parancsban és az eredményfájlban a kör-mappára cserélődik.

Mit ad vissza: kategóriánként a **ténylegesen kiadott parancs** és a
`X passed / Y failed / Z skipped` darabszámok + a bukott tesztek nevei — pont
az, amit a TR1 bizonyíték-kötelezettség megkövetel, és amit a
`failure-counter.py --failed-item` szó szerint vár. A `--json` a `round-log.py`
és a hurok további lépéseinek gépi bemenete.

Kilépő kód: 0 = minden futtatott kategória zöld
            1 = legalább egy kategória bukott (vagy 0 tesztet futtatott — TR2)
            2 = használati hiba: nincs gépi tábla a planban, vagy a megadott
                kategória nem szerepel benne → **ilyenkor a hívó a `test-runner`
                subagentre esik vissza**, és jelzi a 03-nak a hiányzó táblát
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

TABLE_ROW_RE = re.compile(r"^\|(?!\s*-)(.+)\|\s*$")
EMPTY = ("", "-", "—", "n/a", "na", "nincs")


def strip_cell(cell):
    return cell.strip().strip("`").strip()


def parse_matrix(plan_text):
    """A gépi futtatási tábla sorai dict-ként. Üres lista = nincs tábla."""
    m = re.search(r"^#+\s*Gépi futtatási tábla.*$", plan_text, re.MULTILINE | re.IGNORECASE)
    if not m:
        return []
    tail = plan_text[m.end():]
    nxt = re.search(r"^#+\s", tail, re.MULTILINE)
    block = tail[: nxt.start()] if nxt else tail

    rows = []
    for line in block.splitlines():
        mm = TABLE_ROW_RE.match(line.strip())
        if not mm:
            continue
        cells = [strip_cell(c) for c in mm.group(1).split("|")]
        if not cells or cells[0].lower() in ("kategória", "kategoria"):
            continue
        while len(cells) < 7:
            cells.append("")
        rows.append({
            "kategoria": cells[0],
            "tipus": cells[1].lower(),
            "elofeltetel": cells[2],
            "parancs": cells[3],
            "eredmeny": cells[4],
            "formatum": (cells[5] or "junit").lower(),
            "takaritas": cells[6],
        })
    return [r for r in rows if r["kategoria"] and r["parancs"] not in EMPTY]


def is_empty(value):
    return (value or "").strip().lower() in EMPTY


def subst(value, round_dir):
    return (value or "").replace("{round}", str(round_dir))


def run_shell(cmd, cwd, timeout):
    started = time.time()
    try:
        # Az explicit utf-8 + errors='replace' azért kell, mert Windowson a
        # text=True a konzol kódlapjával dekódolna: egy UTF-8-at kiíró teszt-
        # futtató kimenete vagy elromlana, vagy UnicodeDecodeError-t dobna.
        proc = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True,
                              text=True, encoding='utf-8', errors='replace',
                              timeout=timeout)
        return proc.returncode, proc.stdout + proc.stderr, time.time() - started
    except subprocess.TimeoutExpired:
        return 124, f"IDŐTÚLLÉPÉS ({timeout}s) — a parancs nem fejeződött be.", time.time() - started


def parse_junit(path):
    """(passed, failed, skipped, [bukott tesztnevek]) egy JUnit XML-ből."""
    try:
        root = ET.parse(path).getroot()
    except Exception:
        return None
    suites = [root] if root.tag == "testsuite" else root.iter("testsuite")
    total = failures = errors = skipped = 0
    failed_names = []
    for suite in suites:
        total += int(suite.get("tests", 0) or 0)
        failures += int(suite.get("failures", 0) or 0)
        errors += int(suite.get("errors", 0) or 0)
        skipped += int(suite.get("skipped", 0) or 0)
        for case in suite.iter("testcase"):
            if case.find("failure") is not None or case.find("error") is not None:
                cls = case.get("classname", "")
                name = case.get("name", "")
                failed_names.append(f"{cls} > {name}".strip(" >") if cls else name)
    failed = failures + errors
    passed = max(total - failed - skipped, 0)
    return passed, failed, skipped, failed_names


TEXT_PATTERNS = [
    (r"(\d+)\s+passed", "passed"),
    (r"(\d+)\s+failed", "failed"),
    (r"(\d+)\s+skipped", "skipped"),
    (r"Tests run:\s*(\d+)", "total"),
    (r"Failures:\s*(\d+)", "failed"),
    (r"ok\s+(\d+)", None),
]


def parse_text(output):
    got = {}
    for pattern, kind in TEXT_PATTERNS:
        if not kind:
            continue
        m = re.search(pattern, output, re.IGNORECASE)
        if m:
            got[kind] = int(m.group(1))
    if "total" in got and "passed" not in got:
        got["passed"] = got["total"] - got.get("failed", 0) - got.get("skipped", 0)
    if not got:
        return None
    return got.get("passed", 0), got.get("failed", 0), got.get("skipped", 0), []


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
    parser = argparse.ArgumentParser(
        description="Tesztek futtatása a plan.md gépi táblájából, gépi összegzéssel.")
    parser.add_argument("plan_file", help="specs/cycle-NN-<name>/plan.md")
    parser.add_argument("--round-dir", required=True,
                        help="a kör riport-mappája (test-report/validate/round-NN)")
    parser.add_argument("--type", default="all", choices=["gyors", "nehez", "all"],
                        help="mely típusú kategóriák fussanak (VD10 kör-típus)")
    parser.add_argument("--only", action="append", default=[],
                        help="csak ezek a kategóriák fussanak (könnyű körben a bukott item)")
    parser.add_argument("--repo", default=".", help="a parancsok futtatási könyvtára")
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--json", default=None, help="gépi eredmény ide (alap: <round-dir>/results.json)")
    parser.add_argument("--dry-run", action="store_true", help="csak a futtatandó parancsokat listázza")
    args = parser.parse_args()

    plan = Path(args.plan_file)
    if not plan.exists():
        print(f"HIBA: nincs ilyen plan: {plan}", file=sys.stderr)
        return 2
    matrix = parse_matrix(plan.read_text(encoding="utf-8"))
    if not matrix:
        print("HIBA: a plan.md nem tartalmaz `### Gépi futtatási tábla` szekciót (TR4). "
              "Ez a 03 fázis hiánya — essen vissza a hívó a `test-runner` subagentre, "
              "és jelezze a plan kiegészítésének igényét.", file=sys.stderr)
        return 2

    selected = matrix
    if args.only:
        wanted = {o.lower() for o in args.only}
        selected = [r for r in matrix if r["kategoria"].lower() in wanted]
        missing = wanted - {r["kategoria"].lower() for r in matrix}
        if missing:
            print(f"HIBA: ismeretlen kategória a táblában: {', '.join(sorted(missing))}",
                  file=sys.stderr)
            return 2
    elif args.type != "all":
        want = "gyors" if args.type == "gyors" else "nehéz"
        selected = [r for r in matrix
                    if r["tipus"].startswith(want[:4]) or r["tipus"].startswith("nehe" if want == "nehéz" else "gyor")]
    if not selected:
        print(f"HIBA: a táblában nincs `{args.type}` típusú kategória.", file=sys.stderr)
        return 2

    round_dir = Path(args.round_dir)
    round_dir.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        for row in selected:
            print(f"{row['kategoria']} [{row['tipus']}]: {subst(row['parancs'], round_dir)}")
        return 0

    results = []
    any_fail = False
    for row in selected:
        cat = row["kategoria"]
        cmd = subst(row["parancs"], round_dir)
        entry = {"kategoria": cat, "tipus": row["tipus"], "parancs": cmd,
                 "passed": 0, "failed": 0, "skipped": 0, "failed_items": [],
                 "eredmeny": None, "status": "FAIL"}

        if not is_empty(row["elofeltetel"]):
            for pre in row["elofeltetel"].split(";"):
                pre = subst(pre.strip(), round_dir)
                if not pre:
                    continue
                code, out, _ = run_shell(pre, args.repo, args.timeout)
                if code != 0:
                    entry["status"] = "FAIL"
                    entry["failed_items"] = [f"{cat}: előfeltétel-parancs bukott (`{pre}`)"]
                    entry["log_tail"] = out[-800:]
                    results.append(entry)
                    any_fail = True
                    break
            if entry["failed_items"]:
                continue

        code, output, elapsed = run_shell(cmd, args.repo, args.timeout)
        entry["exit_code"] = code
        entry["elapsed_s"] = round(elapsed, 1)

        parsed = None
        result_file = subst(row["eredmeny"], round_dir)
        if not is_empty(result_file):
            src = Path(args.repo) / result_file
            if not src.exists():
                src = Path(result_file)
            if src.exists():
                dest = round_dir / Path(result_file).name
                if src.resolve() != dest.resolve():
                    try:
                        shutil.copy(src, dest)
                    except Exception:
                        dest = src
                entry["eredmeny"] = str(dest)
                if row["formatum"].startswith("junit"):
                    parsed = parse_junit(dest)
        if parsed is None:
            parsed = parse_text(output)

        if parsed is None:
            entry["status"] = "PASS" if code == 0 else "FAIL"
            entry["megjegyzes"] = ("nem sikerült darabszámot kinyerni — "
                                   "csak a kilépő kód áll rendelkezésre (TR1 gyenge bizonyíték)")
            if code != 0:
                entry["failed_items"] = [f"{cat}: a parancs {code} kilépő kóddal bukott"]
        else:
            passed, failed, skipped, names = parsed
            entry.update(passed=passed, failed=failed, skipped=skipped, failed_items=names)
            if passed + failed + skipped == 0:
                entry["status"] = "FAIL"
                entry["failed_items"] = [f"{cat}: 0 teszt futott"]
                entry["megjegyzes"] = "TR2 — a 0 futtatott teszt FAIL, nem PASS"
            elif failed > 0 or code != 0:
                entry["status"] = "FAIL"
                if not names:
                    entry["failed_items"] = [f"{cat}: {failed} teszt bukott"]
            else:
                entry["status"] = "PASS"

        if entry["status"] == "FAIL":
            any_fail = True
            entry["log_tail"] = output[-1500:]

        if not is_empty(row["takaritas"]):
            for post in row["takaritas"].split(";"):
                post = subst(post.strip(), round_dir)
                if post:
                    run_shell(post, args.repo, args.timeout)

        results.append(entry)

    out_json = Path(args.json) if args.json else round_dir / "results.json"
    with open(out_json, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"results": results}, fh, ensure_ascii=False, indent=2)

    print(f"Teszt-futtatás — kör-mappa: {round_dir}")
    for e in results:
        mark = "✓" if e["status"] == "PASS" else "✗"
        print(f"  {mark} {e['kategoria']} [{e['tipus']}] — `{e['parancs']}` → "
              f"{e['passed']} passed / {e['failed']} failed / {e['skipped']} skipped"
              + (f"  ({e['elapsed_s']}s)" if e.get("elapsed_s") else ""))
        if e.get("megjegyzes"):
            print(f"      megjegyzés: {e['megjegyzes']}")
        for name in e["failed_items"][:15]:
            print(f"      ✗ {name}")
    print(f"  results.json: {out_json}")
    print("VERDICT: " + ("FAIL" if any_fail else "PASS"))
    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main())
