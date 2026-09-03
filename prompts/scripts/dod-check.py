#!/usr/bin/env python3
"""DoD ↔ bizonyíték összevetés — a Definition of done gépi kiértékelése
(07-validate, DI1).

Miért kell: a DoD-pontok teljesülése ma a 07 egyetlen olyan lépése, ahol az
orchestrátornak „bele kell néznie" a megvalósításba. Ha viszont a `spec.md`
DoD-pontja megnevezi a **bizonyítékát** (egy teszt vagy egy parancs), akkor a
kiértékelés egy join a kör futási eredményeivel — LLM nélkül, és sokkal
megbízhatóbban, mint egy emlékezetből adott ✓.

A spec.md várt alakja (a `· _bizonyíték:_` rész opcionális, de PASS-hoz ajánlott):

  - [ ] **DoD-01** — a token-csere 200-at ad a `<scope>` scope-pal
        · _bizonyíték:_ `auth.spec.ts > token exchange`
  - [ ] **DoD-02** — a /verify válasz tartalmaz correlationId-t
        · _bizonyíték:_ `cmd: npm run smoke:verify`
  - [ ] **DoD-03** — a hibaüzenet magyar nyelvű a UI-on
        · _bizonyíték:_ `manual: kézi ellenőrzés a UI-on`

Bizonyíték-típusok:
  · **tesztnév** (alap) — a kör-mappa JUnit XML-jeiben keresi (részszöveg,
    kis/nagybetű-érzéketlen). Megvan és zöld → ✓; megvan és bukott → ✗;
    megvan, de `skipped` → `?` (SK1: a némán kihagyott teszt NEM bizonyíték —
    a pont bizonyíték nélkül marad); nincs ilyen teszt → ✗ (a spec olyan
    tesztre hivatkozik, ami nem futott).
  · **`cmd: <parancs>`** — a `results.json`-ban keresi a kategóriát/parancsot;
    zöld futás → ✓.
  · **`manual: <mit>`** — szándékosan kézi: `?`, az orchestrátor ítéli meg.
  · **nincs bizonyíték** — `?`, az orchestrátor ítéli meg (és ez egyben
    spec-minőségi jelzés a 02/05 felé).

Kilépő kód: 0 = minden bizonyítékkal bíró DoD-pont ✓, és nincs `?`
            1 = legalább egy DoD-pont ✗ (a kör FAIL — a `--failed-item`
                értéke pontosan a kiírt `DoD-NN`)
            3 = nincs ✗, de van `?` (kézi ítélet szükséges) — a hívó dönt
            2 = használati hiba (nincs spec.md / DoD-pont)

`--apply` esetén a bizonyítottan ✓ pontokat kipipálja a `spec.md`-ben
(`- [ ]` → `- [x]`) — a ✗ és `?` pontokhoz nem nyúl.
"""
import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

DOD_LINE_RE = re.compile(r"^(?P<prefix>\s*- \[)(?P<mark>[ xX])(?P<mid>\]\s*\**\s*)(?P<id>DoD-\d+)",
                         re.MULTILINE)
EVIDENCE_RE = re.compile(r"_?bizonyíték:?_?\s*[:：]?\s*`([^`]+)`", re.IGNORECASE)


def collect_dod(text):
    """[(DoD-NN, kipipálva?, sorindex, bizonyíték|None)] a spec.md-ből."""
    lines = text.splitlines()
    items = []
    for idx, line in enumerate(lines):
        m = DOD_LINE_RE.match(line)
        if not m:
            continue
        dod_id = m.group("id")
        checked = m.group("mark").lower() == "x"
        # a bizonyíték a saját sorában vagy a következő behúzott sorokban lehet
        chunk = line
        j = idx + 1
        while j < len(lines) and lines[j].strip() and not DOD_LINE_RE.match(lines[j]) \
                and (lines[j].startswith(" ") or lines[j].startswith("\t")):
            chunk += "\n" + lines[j]
            j += 1
        ev = EVIDENCE_RE.search(chunk)
        items.append((dod_id, checked, idx, ev.group(1).strip() if ev else None))
    return items


# A teszt-eset HÁROM állapotú, nem kettő (SK1). A `<skipped>` eset korábban
# `PASS`-ként került az indexbe — így egy `pytest.skip(...)` a teszt elejére
# elég volt ahhoz, hogy a `DoD-NN` bizonyítékot kapjon. A rangsor: a rosszabb
# nyer (`FAIL` > `SKIP` > `PASS`), és a `SKIP` NEM bizonyíték.
_STATE_RANK = {"PASS": 0, "SKIP": 1, "FAIL": 2}


def _worse(a, b):
    return a if _STATE_RANK[a] >= _STATE_RANK[b] else b


def index_tests(round_dir):
    """{tesztnév: 'PASS'|'SKIP'|'FAIL'} a kör-mappa JUnit XML-jeiből (SK1)."""
    index = {}
    for xml in sorted(Path(round_dir).rglob("*.xml")):
        try:
            root = ET.parse(xml).getroot()
        except Exception:
            continue
        suites = [root] if root.tag == "testsuite" else root.iter("testsuite")
        for suite in suites:
            for case in suite.iter("testcase"):
                cls = case.get("classname", "")
                name = case.get("name", "")
                failed = case.find("failure") is not None or case.find("error") is not None
                skipped = case.find("skipped") is not None
                state = "FAIL" if failed else ("SKIP" if skipped else "PASS")
                for key in filter(None, [name, f"{cls} > {name}".strip(" >"), cls]):
                    prev = index.get(key)
                    index[key] = state if prev is None else _worse(prev, state)
    return index


def load_results(round_dir, explicit):
    path = Path(explicit) if explicit else Path(round_dir) / "results.json"
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("results", [])
    except Exception:
        return []


def match_test(evidence, index):
    ev = evidence.lower()
    exact = [k for k in index if k.lower() == ev]
    if exact:
        return exact[0], index[exact[0]]
    partial = [k for k in index if ev in k.lower()]
    if partial:
        worst = "PASS"
        for k in partial:
            worst = _worse(worst, index[k])
        return partial[0] + (f" (+{len(partial)-1} egyező)" if len(partial) > 1 else ""), worst
    return None, None


def match_cmd(evidence, results):
    needle = evidence.lower().strip()
    for r in results:
        if needle in (r.get("parancs", "") or "").lower() or needle == (r.get("kategoria", "") or "").lower():
            return r.get("parancs", r.get("kategoria", "")), r.get("status", "FAIL")
    return None, None


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
    parser = argparse.ArgumentParser(description="DoD ↔ bizonyíték join (DI1).")
    parser.add_argument("cycle_dir")
    parser.add_argument("--round-dir", required=True,
                        help="a kör riport-mappája (itt keresi a JUnit XML-eket és a results.json-t)")
    parser.add_argument("--results", default=None)
    parser.add_argument("--apply", action="store_true",
                        help="a bizonyítottan ✓ pontok kipipálása a spec.md-ben")
    args = parser.parse_args()

    cycle = Path(args.cycle_dir)
    spec = cycle / "spec.md"
    if not spec.exists():
        print(f"HIBA: nincs spec.md: {spec}", file=sys.stderr)
        return 2
    text = spec.read_text(encoding="utf-8")
    items = collect_dod(text)
    if not items:
        print("HIBA: a spec.md-ben nincs `DoD-NN` azonosítójú Definition of done pont (DI1). "
              "Pótold az azonosítókat, mielőtt naplózol.", file=sys.stderr)
        return 2

    index = index_tests(args.round_dir)
    results = load_results(args.round_dir, args.results)

    print(f"DoD-kiértékelés — {cycle}  (kör-mappa: {args.round_dir}, "
          f"{len(index)} teszt-azonosító, {len(results)} futtatott kategória)")
    print("| ID | Eredmény | Bizonyíték |")
    print("|---|---|---|")

    failed, manual, ok_ids = [], [], []
    for dod_id, checked, _idx, evidence in items:
        if evidence is None:
            manual.append(dod_id)
            print(f"| {dod_id} | ? | — nincs megadott bizonyíték, kézi ítélet |")
            continue
        low = evidence.lower()
        if low.startswith("manual:"):
            manual.append(dod_id)
            print(f"| {dod_id} | ? | kézi: {evidence.split(':', 1)[1].strip()} |")
            continue
        if low.startswith("cmd:"):
            needle = evidence.split(":", 1)[1].strip()
            found, status = match_cmd(needle, results)
            label = f"parancs: `{found}`" if found else f"parancs nem futott: `{needle}`"
        else:
            found, status = match_test(evidence, index)
            label = f"teszt: `{found}`" if found else f"nincs ilyen teszt: `{evidence}`"
        if status == "PASS":
            ok_ids.append(dod_id)
            print(f"| {dod_id} | ✓ | {label} |")
        elif status == "SKIP":
            # SK1 — a némán kihagyott teszt NEM bizonyíték. Nem ✗ (a teszt nem
            # bukott), de nem is ✓: a pont bizonyíték NÉLKÜL marad, kézi ítéletre.
            manual.append(dod_id)
            print(f"| {dod_id} | ? | {label} — a hivatkozott teszt lefutott, de "
                  f"`skipped` volt: nem bizonyíték (SK1) |")
        else:
            failed.append(dod_id)
            print(f"| {dod_id} | ✗ | {label} |")

    if args.apply and ok_ids:
        lines = text.splitlines()
        changed = 0
        for dod_id, checked, idx, _ev in items:
            if dod_id in ok_ids and not checked:
                lines[idx] = DOD_LINE_RE.sub(
                    lambda m: m.group("prefix") + "x" + m.group("mid") + m.group("id"),
                    lines[idx], count=1)
                changed += 1
        if changed:
            with open(spec, "w", encoding="utf-8", newline="\n") as fh:
                fh.write("\n".join(lines) + ("\n" if text.endswith("\n") else ""))
            print(f"  → {changed} DoD-pont kipipálva a spec.md-ben")

    print(f"Összegzés: {len(ok_ids)} ✓ / {len(failed)} ✗ / {len(manual)} ?")
    if failed:
        print("VERDICT: FAIL — a --failed-item értékei: " + " ".join(failed))
        return 1
    if manual:
        print("VERDICT: MANUAL — bizonyíték nélküli pont(ok): " + " ".join(manual)
              + "  (az orchestrátor ítéli meg; a hiányzó bizonyíték egyben spec-minőségi jelzés. "
                "A `skipped` teszttel jelölt pontnál a teszt LEFUTTATÁSA a megoldás — SK1)")
        return 3
    print("VERDICT: PASS — minden DoD-pont bizonyítottan teljesül")
    return 0


if __name__ == "__main__":
    sys.exit(main())
