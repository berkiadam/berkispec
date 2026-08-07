#!/usr/bin/env python3
"""Analyze mechanikus kapu — a ciklus tervezési dokumentumainak GÉPIESEN
eldönthető konzisztencia-ellenőrzései (05-analyze).

Miért kell: az `analyzer` subagent hat kategóriája közül több ellenőrzés
tisztán szöveg-mintázat kérdése (hivatkozás-egyeztetés, marker-jelenlét,
azonosító-duplikáció, kötelező táblák megléte). Ezeket LLM-mel futtatni
drága ÉS megbízhatatlan: egy olcsóbb modell hol kihagy, hol hamisan riaszt.
Ez a szkript ezt a réteget determinisztikussá teszi, így az analyzer a
SZEMANTIKAI kategóriákra koncentrálhat (ambiguitás, alulspecifikáció,
lefedettségi értelmezés, végrehajthatóság).

Mit ellenőriz:

  P1  plan-ID formátum és egyediség  — `[P-...]` a plan címsoraiban
  P2  task → plan hivatkozás megléte — minden `- [ ] Tnnn ...` sor végén `plan [P-...]`
  P3  task → nem létező plan-ID      — hivatkozás, amihez nincs plan-szekció
  P4  plan-ID → nincs hivatkozó task — és a `Plan-lefedettség` tábla sem említi
  P5  sorszámos hivatkozás           — `plan.md § 3.1` stílus `[P-...]` helyett
  T1  marker minden taskon           — `[RED]`/`[GREEN]`/`[CHECK]`/`[OPS]`
  T2  `[OPS]` fájl-útvonallal        — repo-fájlt szerkesztő task rossz markerrel
  T3  státusz-frissítő task          — spec/plan/tasks státuszát állító task
  T4  `⟂` szimmetria                 — `T012 ⟂ T013`, de `T013` nem hivatkozik vissza
  D1  `DoD-NN` azonosítók            — hiányzó vagy duplikált azonosító a specben
  D2  `DoD-NNb` alakú azonosító      — utólagos beszúrás betűs utótaggal (DI1 megsértése)
  S1  kötelező plan-táblák           — `Spec-lefedettség`, `Fordított lefedettség`
  S2  kötelező tasks-tábla           — `Plan-lefedettség`

Amit NEM csinál: nem értelmez, nem dönt fázist, nem javít. A kimenete egy
megállapítás-lista, amit az 05-analyze orchestrátor a `Must Fix` listába emel
(a célfázissal együtt, amit a szkript minden tételnél kiír).

Használat:
  analyze-gate-check.py specs/cycle-NN-<name>

Kilépő kód: 0 = nincs megállapítás
            1 = van megállapítás (a lista a stdout-on, gépiesen olvasható)
            2 = használati hiba (hiányzó mappa vagy dokumentum)
"""
import argparse
import re
import sys
from pathlib import Path


PLAN_ID_IN_HEADING_RE = re.compile(r"^#{2,4}\s+.*?\[(P-[A-Za-z0-9][A-Za-z0-9-]*)\]", re.MULTILINE)
PLAN_ID_TOKEN_RE = re.compile(r"\[(P-[A-Za-z0-9][A-Za-z0-9-]*)\]")
BAD_PLAN_ID_RE = re.compile(r"\[(P-[^\]]*)\]")
TASK_LINE_RE = re.compile(r"^\s*-\s*\[[ xX]\]\s+(T[A-Z]*\d+)\b(.*)$")
GROUP_HEADING_RE = re.compile(r"^##\s+(.+)$")
MARKER_RE = re.compile(r"\[(RED|GREEN|CHECK|OPS)\]")
SECTION_REF_RE = re.compile(r"§\s*\d|plan\.md\s*§|plan\s*§")
PARALLEL_RE = re.compile(r"⟂\s*(T[A-Z]*\d+)")
FILE_PATH_RE = re.compile(r"`[^`]*\.[A-Za-z0-9]{1,5}`|\]\(file://[^)]+\)")
DOD_RE = re.compile(r"DoD-(\d+[a-z]?)")
DOD_BULLET_RE = re.compile(r"^\s*-\s*\[[ xX]\]\s*(.+)$")
STATUS_TASK_RE = re.compile(
    r"(állítsd|állítsa|frissítsd|frissítse|váltsd|váltsa).{0,60}"
    r"(státusz|statusz|állapot).{0,40}"
    r"|(spec|plan|tasks)\.md.{0,30}(státusz|statusz).{0,30}(kész|készre)",
    re.IGNORECASE | re.DOTALL,
)

REQUIRED_PLAN_TABLES = [
    ("Spec-lefedettség", "03", "a spec tesztesetei és DoD-pontjai leképezésének táblája (TP1)"),
    ("Fordított lefedettség", "03", "a plan-képességek spec-forrásának táblája (SC1)"),
]
REQUIRED_TASKS_TABLES = [
    ("Plan-lefedettség", "04", "a plan-szekció → task fordított tábla (PID1)"),
]


class Findings:
    def __init__(self):
        self.items = []

    def add(self, code, phase, message):
        self.items.append((code, phase, message))

    def __len__(self):
        return len(self.items)


def read(path):
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"HIBA: {path} nem olvasható ({exc})", file=sys.stderr)
        sys.exit(2)


def plan_ids(plan_text):
    """A plan címsoraiban kiadott `[P-...]` azonosítók, megjelenési sorrendben."""
    return PLAN_ID_IN_HEADING_RE.findall(plan_text)


def task_lines(tasks_text):
    """(sorszám, task-id, sor) hármasok a tasks.md task-sorairól."""
    out = []
    for lineno, line in enumerate(tasks_text.splitlines(), start=1):
        m = TASK_LINE_RE.match(line)
        if m:
            out.append((lineno, m.group(1), line))
    return out


def check_plan_ids(plan_text, f):
    ids = plan_ids(plan_text)
    seen = {}
    for pid in ids:
        seen[pid] = seen.get(pid, 0) + 1
    for pid, count in seen.items():
        if count > 1:
            f.add("P1", "03", f"a `[{pid}]` plan-azonosító {count} címsorban szerepel — az ID-nak egyedinek kell lennie")
    for raw in BAD_PLAN_ID_RE.findall(plan_text):
        if not re.fullmatch(r"P-[A-Za-z0-9][A-Za-z0-9-]*", raw):
            f.add("P1", "03", f"hibás formátumú plan-azonosító: `[{raw}]` (várt: `[P-NEV]`, nagybetűs, kötőjeles)")
    if not ids:
        f.add("P1", "03", "a plan egyetlen címsora sem visel `[P-...]` azonosítót (PID1) — a tasks.md nem tud rá stabilan hivatkozni")
    return set(ids)


def check_task_references(tasks_text, known_ids, f):
    referenced = set()
    for lineno, tid, line in task_lines(tasks_text):
        refs = PLAN_ID_TOKEN_RE.findall(line)
        if not refs:
            if SECTION_REF_RE.search(line):
                f.add("P5", "04", f"tasks.md:{lineno} `{tid}` sorszámos plan-hivatkozást használ `[P-...]` helyett — a sorszám elcsúszik, ha a plan bővül")
            else:
                f.add("P2", "04", f"tasks.md:{lineno} `{tid}` nem hivatkozik plan-szekcióra (hiányzik a `— plan [P-...]`)")
            continue
        for ref in refs:
            referenced.add(ref)
            if ref not in known_ids:
                f.add("P3", "04", f"tasks.md:{lineno} `{tid}` a `[{ref}]` azonosítóra hivatkozik, ami a plan-ben nem létezik (elgépelés vagy törölt szekció)")
    return referenced


def check_plan_coverage(tasks_text, known_ids, referenced, f):
    """P4 — plan-ID, amire egy task sem hivatkozik. A `Plan-lefedettség` tábla
    említése (indoklással) elfogadható mentesítés."""
    coverage_mentions = set()
    inside = False
    for line in tasks_text.splitlines():
        if line.startswith("## "):
            inside = "Plan-lefedettség" in line
            continue
        if inside:
            coverage_mentions.update(PLAN_ID_TOKEN_RE.findall(line))
    for pid in sorted(known_ids - referenced):
        if pid in coverage_mentions:
            continue
        f.add("P4", "04", f"a plan `[{pid}]` szekciójára egyetlen task sem hivatkozik, és a `Plan-lefedettség` tábla sem indokolja meg")


def check_markers(tasks_text, f):
    for lineno, tid, line in task_lines(tasks_text):
        m = MARKER_RE.search(line)
        if not m:
            f.add("T1", "04", f"tasks.md:{lineno} `{tid}` nem visel markert (`[RED]`/`[GREEN]`/`[CHECK]`/`[OPS]`)")
            continue
        if m.group(1) == "OPS" and FILE_PATH_RE.search(line):
            f.add("T2", "04", f"tasks.md:{lineno} `{tid}` `[OPS]` markerrel repo-fájlt szerkeszt — `[RED]`/`[GREEN]` a helyes marker")
        if STATUS_TASK_RE.search(line) and re.search(r"(spec|plan|tasks)\.md", line, re.IGNORECASE):
            f.add("T3", "04", f"tasks.md:{lineno} `{tid}` státusz-frissítő tasknak tűnik — a státusz-életciklus a 07-validate gépezete")


def check_parallel_symmetry(tasks_text, f):
    parallel = {}
    for lineno, tid, line in task_lines(tasks_text):
        peers = PARALLEL_RE.findall(line)
        if peers:
            parallel[tid] = (lineno, set(peers))
    for tid, (lineno, peers) in parallel.items():
        for peer in peers:
            back = parallel.get(peer)
            if back is None or tid not in back[1]:
                f.add("T4", "04", f"tasks.md:{lineno} `{tid} ⟂ {peer}`, de `{peer}` nem jelöli vissza `{tid}`-t — a párhuzamosítás egyoldalú jelölése hibás")


def check_dod(spec_text, f):
    inside = False
    numbers = []
    unlabeled = 0
    for line in spec_text.splitlines():
        if line.startswith("## "):
            inside = "Definition of done" in line
            continue
        if not inside:
            continue
        m = DOD_BULLET_RE.match(line)
        if not m:
            continue
        found = DOD_RE.search(m.group(1))
        if found:
            numbers.append(found.group(1))
        else:
            unlabeled += 1
    if unlabeled:
        f.add("D1", "02", f"{unlabeled} DoD-pontnak nincs `DoD-NN` azonosítója — a 07-validate per-item leállító számlálója erre épül")
    seen = {}
    for n in numbers:
        seen[n] = seen.get(n, 0) + 1
    for n, count in sorted(seen.items()):
        if count > 1:
            f.add("D1", "02", f"`DoD-{n}` azonosító {count}-szor szerepel — az azonosítónak egyedinek kell lennie")
    for n in sorted(x for x in seen if not x.isdigit()):
        f.add("D2", "02", f"`DoD-{n}` betűs utótagot visel — utólag beszúrt DoD-pont a KÖVETKEZŐ SZABAD SZÁMOT kapja (DI1), nem `NNb` alakot; a 07 per-item számlálója így marad követhető")


def check_required_tables(text, required, f, doc):
    for title, phase, why in required:
        if title not in text:
            f.add("S1" if doc == "plan.md" else "S2", phase, f"a(z) `{doc}`-ból hiányzik a kötelező `{title}` szekció — {why}")



def _force_utf8_output():
    """Windows-kompatibilitás: a konzol örökölt kódlapja (cp852 / cp1250 / cp1252)
    nem tudja megjeleníteni a kimenet tipográfiai és ékezetes karaktereit (—, →, ő, ű),
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
    parser = argparse.ArgumentParser(description="Analyze mechanikus kapu (05-analyze)")
    parser.add_argument("cycle_dir", help="a ciklus mappája, pl. specs/cycle-25-dynamic-routing")
    args = parser.parse_args()

    cycle = Path(args.cycle_dir)
    if not cycle.is_dir():
        print(f"HIBA: {cycle} nem létező könyvtár", file=sys.stderr)
        return 2

    spec_path, plan_path, tasks_path = cycle / "spec.md", cycle / "plan.md", cycle / "tasks.md"
    for p in (spec_path, plan_path, tasks_path):
        if not p.is_file():
            print(f"HIBA: {p} nem található — a kapu a három tervezési dokumentumot igényli", file=sys.stderr)
            return 2

    spec_text, plan_text, tasks_text = read(spec_path), read(plan_path), read(tasks_path)
    f = Findings()

    known_ids = check_plan_ids(plan_text, f)
    referenced = check_task_references(tasks_text, known_ids, f)
    check_plan_coverage(tasks_text, known_ids, referenced, f)
    check_markers(tasks_text, f)
    check_parallel_symmetry(tasks_text, f)
    check_dod(spec_text, f)
    check_required_tables(plan_text, REQUIRED_PLAN_TABLES, f, "plan.md")
    check_required_tables(tasks_text, REQUIRED_TASKS_TABLES, f, "tasks.md")

    if not f:
        print("ANALYZE-GATE: OK — nincs mechanikus megállapítás")
        return 0

    print(f"ANALYZE-GATE: {len(f)} megállapítás\n")
    for code, phase, message in f.items:
        print(f"[{code}] (célfázis: {phase}) {message}")
    print("\nMindegyik Must Fix a megadott célfázissal — az analyzer szemantikai megállapításai mellé.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
