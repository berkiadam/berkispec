#!/usr/bin/env python3
"""Teszt-tartalom kapu — vacuous teszt-törzs (TB1) és szelektor-létezés (TB2).

Miért kell: egy éles ciklusban (`cycle-30`) a `[RED]` taskok „megírt" E2E
tesztjeinek törzse `assert True` volt. A suite `26 passed / 0 failed`-et
jelentett, a `dod-check.py` a bizonyítékot a teszt **nevére** illesztette, a
`07-validate` pedig `PASS`-ra zárt — anélkül, hogy bármit ellenőriztünk volna.
Ugyanabban a ciklusban három `[CHECK]` parancs olyan teszt-függvényre
hivatkozott, amelyet az implementáció közben **átneveztek**; mivel a `06`
egyetlen összevont futást csinált szelektor nélkül, ez sem derült ki.

Két check, egy scriptben (ugyanazokat a fájlokat olvassa mindkettő):

  TB1 — vacuous teszt-törzs. A vizsgált fájlok listája a `plan.md` `TA1`
        adatlapjaiból jön (a `<sec:unit_tests>` / `<sec:integration_tests>` /
        `<sec:e2e_tests>` szekciók `#### <path>` fejlécei) — NEM `git diff`-ből,
        mert az branch-név-függő és a fix-körökben elcsúszik.
        KONZERVATÍV mintakészlet (a hamis pozitív itt drágább, mint egy
        kihagyott eset): csak a bizonyosan üres alakokat fogja meg. Nem
        vizsgálunk coverage-t, asszertáció-darabszámot, mutation scoret, és nem
        minősítjük az asszertáció tartalmát — az LLM-ítélet, nem kapu.

  TB2 — szelektor-létezés. A `tasks.md` `[CHECK]` taskjainak parancsaiból
        kigyűjtött teszt-szelektorok (`::<fn>`, `-t "<név>"`, `-k <minta>`)
        tényleg léteznek-e a hivatkozott tesztfájlban. Egyszerű szöveges
        keresés, nem AST: egy átnevezés így is kiderül, és nincs
        nyelv-specifikus törékenység.

Kilépő kód: 0 = nincs találat (vagy nincs mit vizsgálni)
            1 = van vacuous teszt vagy nem létező szelektor (Must Fix)
            2 = használati hiba (nincs ciklus-mappa vagy nincs plan.md)
"""
import argparse
import re
import sys
from pathlib import Path

from lang_keys import sec

TEST_SECTIONS = ("unit_tests", "integration_tests", "e2e_tests")
HEADING_RE = re.compile(r"^(#{2,5})\s+(.*)$")
# A TA1 adatlap fejléce: `#### \`test/unit/foo.test.ts\` (új)` — az útvonal backtickben.
TA1_HEADING_RE = re.compile(r"^#{3,5}\s+.*?`([^`]+\.[A-Za-z0-9]{1,6})`")

PY_EXT = {".py"}
JS_EXT = {".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx"}

# ── BD4 — a tiltott (bizonyosan vacuous) törzs-alakok ────────────────────────
TRIVIAL_LINE_RE = re.compile(
    r"^(?:"
    r"assert\s+True|assert\s+1\s*==\s*1|assert\s+not\s+False|"
    r"assert\.ok\(\s*true\s*\)|expect\(\s*true\s*\)\.(?:to)?[Bb]e(?:Truthy)?\(\s*true?\s*\)|"
    r"pass|\.\.\.|return(?:\s+None)?|true"
    r")\s*;?\s*$"
)
ASSERT_TOKEN_RE = re.compile(
    r"\bassert\b|\bassert[.(]|\bself\.assert|pytest\.raises|pytest\.fail|"
    r"\bexpect\s*\(|\.should\b|should\.|\braise\b|\bthrow\b|"
    r"assertThat|\bfail\s*\(",
    re.IGNORECASE,
)
SKIP_RE = re.compile(r"pytest\.skip|mark\.skip|\.skip\s*\(|@unittest\.skip|xfail")


def strip_comments(body, kind):
    """Kommentek és docstringek nélküli törzs (a BD4 harmadik alakjához)."""
    if kind == "py":
        body = re.sub(r'("""|\'\'\')(?:.|\n)*?\1', "", body)
        body = re.sub(r"(?m)#.*$", "", body)
    else:
        body = re.sub(r"/\*(?:.|\n)*?\*/", "", body)
        body = re.sub(r"(?m)//.*$", "", body)
    return body


def meaningful_lines(body, kind):
    return [l.strip() for l in strip_comments(body, kind).splitlines() if l.strip()]


def judge(body, kind, skipped=False):
    """(hibás-e, melyik minta) — a BD4 tábla szerint, konzervatívan."""
    if skipped or SKIP_RE.search(body):
        return None, None                     # kihagyott teszt — nem ítélünk
    lines = meaningful_lines(body, kind)
    if not lines:
        return True, "a törzs üres (csak komment vagy semmi)"
    if all(TRIVIAL_LINE_RE.match(l) for l in lines):
        return True, "a törzs kizárólag triviális állítás/üres váz (`" + "`, `".join(lines[:3]) + "`)"
    if not ASSERT_TOKEN_RE.search(strip_comments(body, kind)):
        return True, "a törzsben egyetlen asszertáció (assert/expect) és `raise`/`throw` sincs"
    return None, None


def py_functions(text):
    """[(függvénynév, sor, törzs, kihagyott-e)] — `def test_*` / `async def test_*`.

    A dekorátorok (`@pytest.mark.skip`) a fejléc FÖLÖTT állnak, ezért külön
    vizsgáljuk őket: a törzsbe fűzve elrontanák a „csak triviális sor" ítéletet.
    """
    lines = text.splitlines()
    out = []
    for i, line in enumerate(lines):
        m = re.match(r"^(\s*)(?:async\s+)?def\s+(test_\w+)\s*\(", line)
        if not m:
            continue
        indent, name = len(m.group(1)), m.group(2)
        body = []
        for nxt in lines[i + 1:]:
            if nxt.strip() and (len(nxt) - len(nxt.lstrip())) <= indent:
                break
            body.append(nxt)
        deco = "\n".join(lines[max(0, i - 3):i])
        out.append((name, i + 1, "\n".join(body), bool(SKIP_RE.search(deco))))
    return out


def js_functions(text):
    """[(teszt-név, sor, törzs, kihagyott-e)] — `it("…", …)` / `test("…", …)` callbackek."""
    out = []
    for m in re.finditer(r"\b(?:it|test)(\.\w+)?\s*\(\s*(['\"`])(.+?)\2\s*,", text):
        name = m.group(3)
        skipped = bool(m.group(1) and re.search(r"skip|todo", m.group(1)))
        brace = text.find("{", m.end())
        if brace == -1:
            continue
        depth, end = 0, None
        for i in range(brace, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    end = i
                    break
        if end is None:
            continue
        line = text.count("\n", 0, m.start()) + 1
        out.append((name, line, text[brace + 1:end], skipped))
    return out


def plan_test_files(plan_text):
    """A `TA1` adatlapok tesztfájl-útvonalai a három teszt-szekcióból."""
    paths, in_section, level = [], False, 0
    for line in plan_text.splitlines():
        h = HEADING_RE.match(line)
        if h:
            title, depth = h.group(2), len(h.group(1))
            if any(sec(k) in title for k in TEST_SECTIONS):
                in_section, level = True, depth
                continue
            if in_section and depth <= level:
                in_section = False
        if not in_section:
            continue
        m = TA1_HEADING_RE.match(line)
        if m:
            paths.append(re.sub(r"\s*\(.*\)\s*$", "", m.group(1)).strip())
    seen, out = set(), []
    for p in paths:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def planned_paths(plan_text):
    """A `<sec:planned_changes>` szekcióban szereplő fájl-útvonalak.

    Guard-halmaz: egy még nem létező fájl, amelyet a terv **tervez**, nem hiba —
    a `06` egyszerűen nem futott le (vagy még nem ért oda). Az ilyen eset `info`,
    nem `✗` (23.5 guard).
    """
    body, in_section, level = [], False, 0
    for line in plan_text.splitlines():
        h = HEADING_RE.match(line)
        if h:
            title, depth = h.group(2), len(h.group(1))
            if sec("planned_changes") in title:
                in_section, level = True, depth
                continue
            if in_section and depth <= level:
                in_section = False
        if in_section:
            body.append(line)
    text = "\n".join(body)
    return {p for p in re.findall(r"(?<![\w/.-])([\w./-]+\.[A-Za-z0-9]{1,6})", text)}


# ── TB2 — a `[CHECK]` parancsok szelektorai ─────────────────────────────────
CHECK_TASK_RE = re.compile(r"^\s*- \[[ xX]\]\s+(T[A-Z]*\d+[a-z]?)\s+\[CHECK\]")


def task_selectors(tasks_text):
    """[(task, fájl-útvonal|None, szelektor, alak)] a `[CHECK]` parancsokból."""
    out = []
    for line in tasks_text.splitlines():
        m = CHECK_TASK_RE.match(line)
        if not m:
            continue
        task = m.group(1)
        cmd_m = re.search(r"`([^`]+)`", line)
        if not cmd_m:
            continue
        cmd = cmd_m.group(1)
        files = re.findall(r"(?<![\w/.-])([\w./-]+\.(?:py|ts|tsx|js|mjs|cjs|jsx))", cmd)
        target = files[0] if files else None
        sel = re.search(r"::([\w]+)", cmd)
        if sel:
            out.append((task, target, sel.group(1), "::<függvény>"))
            continue
        sel = re.search(r"(?:-t|--test-name-pattern|--testNamePattern)\s+(\"[^\"]+\"|'[^']+'|\S+)", cmd)
        if sel:
            out.append((task, target, sel.group(1).strip("\"'"), '-t "<név>"'))
            continue
        sel = re.search(r"-k\s+(\"[^\"]+\"|'[^']+'|\S+)", cmd)
        if sel:
            pattern = sel.group(1).strip("\"'")
            if re.search(r"\b(and|or|not)\b", pattern):
                out.append((task, target, None, f"-k logikai kifejezés (`{pattern}`) — nem ítélünk"))
            else:
                out.append((task, target, pattern, "-k <minta>"))
    return out


def _force_utf8_output():
    """Windows-kompatibilitás: az örökölt konzol-kódlap (cp852/cp1250) nem tudja
    kiírni a `✓`/`✗`/`—` karaktereket, és a `print()` `UnicodeEncodeError`-t
    dobna — a hívó ágens hibás kilépő kódot látna egy lefutott ellenőrzés után."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def check_substance(files, repo_root, planned_new):
    """TB1 — [(fájl, sor, függvény, minta)] találatok + info-sorok."""
    findings, infos = [], []
    for rel in files:
        path = (repo_root / rel)
        if not path.exists():
            if rel in planned_new:
                infos.append(f"`{rel}` még nem létezik (a plan új fájlként tervezi) — kimarad")
            else:
                infos.append(f"`{rel}` nem található a `{repo_root}` alatt — kimarad")
            continue
        ext = path.suffix.lower()
        if ext in PY_EXT:
            kind, funcs = "py", py_functions(path.read_text(encoding="utf-8", errors="replace"))
        elif ext in JS_EXT:
            kind, funcs = "js", js_functions(path.read_text(encoding="utf-8", errors="replace"))
        else:
            infos.append(f"`{rel}`: a `{ext}` kiterjesztéshez nincs konzervatív "
                         "függvény-felismerő — kimarad (nem találgatunk)")
            continue
        if not funcs:
            infos.append(f"`{rel}`: nem találtam teszt-függvényt — kimarad")
            continue
        for name, line, body, skipped in funcs:
            bad, why = judge(body, kind, skipped)
            if bad:
                findings.append((rel, line, name, why))
    return findings, infos


def main():
    _force_utf8_output()
    ap = argparse.ArgumentParser(description="Teszt-tartalom kapu (TB1) és szelektor-létezés (TB2).")
    ap.add_argument("cycle_dir", help="a ciklus mappája (specs/cycle-NN-<name>)")
    ap.add_argument("--repo-root", default=".", help="a projekt gyökere (alap: .)")
    ap.add_argument("--files", nargs="*", help="célzott futtatás: csak ezek a fájlok (TB1)")
    ap.add_argument("--tasks", help="a tasks.md útvonala (alap: a ciklus-mappa tasks.md-je)")
    ap.add_argument("--selectors-only", action="store_true",
                    help="csak a TB2 (szelektor-létezés) fut — a 07 INDULÁSÁHOZ")
    args = ap.parse_args()

    cycle = Path(args.cycle_dir)
    if not cycle.is_dir():
        print(f"HIBA: nincs ilyen ciklusmappa: {cycle}", file=sys.stderr)
        return 2
    repo_root = Path(args.repo_root)
    plan_path = cycle / "plan.md"
    plan_text = plan_path.read_text(encoding="utf-8") if plan_path.exists() else None
    if plan_text is None and not args.files:
        print(f"HIBA: nincs plan.md a(z) {cycle} alatt (és nincs --files sem)", file=sys.stderr)
        return 2

    print(f"TESZT-TARTALOM KAPU — {cycle}")
    failed = False

    planned_new = planned_paths(plan_text) if plan_text else set()

    if not args.selectors_only:
        files = args.files if args.files else plan_test_files(plan_text)
        if not files:
            print("  · a plan teszt-szekcióiban nincs `#### <tesztfájl>` adatlap — a TB1 kimarad")
        else:
            findings, infos = check_substance(files, repo_root, planned_new)
            for msg in infos:
                print(f"  · {msg}")
            if findings:
                failed = True
                print(f"  ✗ {len(findings)} vacuous teszt-törzs (TB1) — a teszt zöld, de nem bizonyít semmit:")
                for rel, line, name, why in findings:
                    print(f"      ✗ {rel}:{line} {name} — {why}")
            else:
                print(f"  ✓ a vizsgált {len(files)} tesztfájlban nincs vacuous teszt-törzs (TB1)")

    tasks_path = Path(args.tasks) if args.tasks else cycle / "tasks.md"
    tasks_text = tasks_path.read_text(encoding="utf-8") if tasks_path.exists() else None
    if tasks_text is None:
        print(f"  · nincs {tasks_path} — a TB2 kimarad")
    else:
        selectors = task_selectors(tasks_text)
        if not selectors:
            print("  · a `[CHECK]` parancsokban nincs teszt-szelektor — a TB2 kimarad")
        else:
            missing = []
            for task, rel, sel, shape in selectors:
                if sel is None:
                    print(f"  · {task}: {shape}")
                    continue
                if rel is None:
                    print(f"  · {task}: a parancsból nem azonosítható tesztfájl (`{sel}`) — kimarad")
                    continue
                path = repo_root / rel
                if not path.exists():
                    if rel in planned_new:
                        print(f"  · {task}: a(z) `{rel}` még nem létezik (a plan új fájlként "
                              "tervezi, a 06 még nem futott) — kimarad")
                    else:
                        missing.append(f"{task} — a(z) `{rel}` fájl nem létezik")
                    continue
                if sel not in path.read_text(encoding="utf-8", errors="replace"):
                    missing.append(f"{task} — a(z) `{rel}` nem tartalmazza a `{sel}` tesztet")
            if missing:
                failed = True
                print(f"  ✗ {len(missing)} `[CHECK]` szelektor nem létezik (TB2) — a parancs "
                      "futtatáskor hibával állna le:")
                for msg in missing:
                    print(f"      ✗ {msg}")
            else:
                print(f"  ✓ mind a {len(selectors)} `[CHECK]` szelektor létezik a tesztfájlban (TB2)")

    print("EREDMÉNY: " + ("BUKOTT — a fenti ✗ pontokat rendezd" if failed else "OK"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
