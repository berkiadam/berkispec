#!/usr/bin/env python3
"""07-validate gyűjtőkapu — a fázis apró, determinisztikus ellenőrzései egyben.

Miért kell: ezek mind tiszta regex-kérdések, mégis ma mindegyikért be kell
olvasni egy-egy fájlt a fő kontextusba (spec.md, tasks.md, code-review.md,
validate-input-from-prev.md, validation-report.md). Egyetlen szkript-hívás
kiváltja mindet, és tíz sorban válaszol.

Két szakasz:

  --stage start   (a fázis elején, az Előfeltétel lépéshez)
    · tasks.md státusza `Validálásra kész` (vagy `[validate-loop]` markeres
      folytatás), plan.md / spec.md státusza elfogadható értéken áll
    · a `[validate-loop]` marker jelenléte → megszakadt hurok jelzése
    · nyitott `validate-input-from-prev.md` tételek felsorolása (IP1, INFO)

  --stage close   (alapértelmezett — a kör lezárása / PASS előtt)
    · tasks.md: nincs nyitott `- [ ]` (a javító-szekciókat külön jelzi)
    · check-log.md: a `[CHECK]` parancsok szó szerint, taskonként futottak (CK1) —
      egy naplósor = egy task-azonosító, és a naplózott parancs hordozza a task
      teszt-szűrőjét (`CK-DEVIATION:` sorral felmenthető)
    · check-log.md: minden `[RED]` taskhoz van bukott (`✗`) futás (RED1) —
      `RED-EXEMPT:` sorral felmenthető
    · spec.md: minden DoD-pontnak van `DoD-NN` azonosítója, egyediek,
      és nincs köztük nyitott `- [ ]` (DI1)
    · validate-input-from-prev.md: nincs nyitott `[ ]` tétel (IP1)
    · test-report/code-review.md: a jelentés befejezett (a fejléc státusza nem
      `Folyamatban` — RV-INC), és nincs benne nyitott `- [ ] **MF-NN**` (RV1)
    · validation-report.md: van legalább egy `## Kör N` blokk, a körök száma
      nem kevesebb a `# Validation History` futásainál (VD9-guard), és
      minden körhöz létezik a `validate/round-NN/` mappa (TR5)
    · kör-lefedettség (RUN1): minden TELJES kör `results.json`-ja tartalmazza a
      plan gépi futtatási táblájának minden `validate`-fázisú kategóriáját —
      hiányzó `results.json` = a kört nem a táblából hajtották
      (`RUN-EXEMPT: <kategória> — <indok>` sorral felmenthető, a kör blokkjában)
    · skip-bizonyíték (SK1): az utolsó kör JUnit XML-jeiben nincs olyan `skipped`
      eset, amelyet a plan adatlapja `TC-NN` bizonyítékként jelöl
      (`SKIP-EXEMPT: <teszt> — <indok>` sorral felmenthető)
    · REST-napló hatóköre (RL1): az utolsó kör
      `rest-logs/<local|remote>/<teszt>/` mappái közül a `remote/` alattiak
      tartalmaznak-e valóban nem-lokális címet (a `local/` alattiak pedig nem
      csak távolit) — a `Környezetek és végpontok` tábla `remote` sorainak
      lokálisnak látszó címei (port-forward) felmentettek
    · címke ↔ bizonyíték join (RL2): minden `[remote]`-nak jelölt `TS-NN`
      forgatókönyv teszt-függvényéhez van-e `rest-logs/remote/<teszt>/` napló
      ebben a körben (`SCOPE-EXEMPT: <teszt> — <indok>` sorral felmenthető)

Kilépő kód: 0 = minden vizsgált kapu rendben
            1 = legalább egy kapu bukott (a kör nem zárható PASS-ra)
            2 = használati hiba (nem létező ciklusmappa)

A `--require-review` nélkül a hiányzó `code-review.md` csak INFO (pl. az első,
tesztekre bukó körben a review el sem indult). PASS előtt add meg — akkor a
hiánya bukás.
"""
import argparse
import json
import re
import sys
from pathlib import Path

from lang_keys import fld, sec, st

FIX_SECTIONS = (f"## {sec('validation_fixes')}", f"## {sec('review_fixes')}")


def read(path):
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def get_status(path):
    text = read(path)
    if text is None:
        return None
    for line in text.splitlines():
        clean = line.strip().lstrip("-").strip().replace("**", "").replace("*", "").replace("`", "").strip()
        if re.match(r"^" + re.escape(fld("f_status")) + r"\s*:", clean, re.IGNORECASE):
            return clean.split(":", 1)[1].strip().lower()
    return None


class Report:
    def __init__(self):
        self.failed = False

    def ok(self, msg):
        print(f"  ✓ {msg}")

    def info(self, msg):
        print(f"  · {msg}")

    def bad(self, msg):
        print(f"  ✗ {msg}")
        self.failed = True


def split_sections(text):
    """(fő rész, javító-szekciók szövege) a tasks.md-ből."""
    idx = len(text)
    for marker in FIX_SECTIONS:
        pos = text.find(marker)
        if pos != -1:
            idx = min(idx, pos)
    return text[:idx], text[idx:]


def check_tasks(cycle, rep, stage):
    path = cycle / "tasks.md"
    text = read(path)
    if text is None:
        rep.bad("tasks.md nem található")
        return
    status = get_status(path) or "—"
    if stage == "start":
        if st("ready_for_validate").lower() in status:
            rep.ok(f"tasks.md státusz: {status}")
        else:
            rep.bad(f"tasks.md státusz: '{status}' — a 07 "
                    f"`{st('ready_for_validate')}`-t vár (vissza a 06-ra)")
        if "[validate-loop]" in status:
            rep.info("`[validate-loop]` marker → megszakadt önjavító hurok folytatása")
        return
    main, fixes = split_sections(text)
    open_main = len(re.findall(r"^\s*- \[ \]", main, re.MULTILINE))
    open_fix = len(re.findall(r"^\s*- \[ \]", fixes, re.MULTILINE))
    if open_main == 0:
        rep.ok("tasks.md: minden alap-task `[x]`")
    else:
        rep.bad(f"tasks.md: {open_main} nyitott task a fő szekciókban")
    if open_fix:
        rep.bad(f"tasks.md: {open_fix} nyitott javító-task ({' / '.join(FIX_SECTIONS)})")
    if "[validate-loop]" in (status or ""):
        rep.info("`[validate-loop]` marker még fent van (PASS-nál le kell venni)")


TASK_ID_RE = re.compile(r"\bT[A-Z]*\d+[a-z]?\b")
TASK_LINE_RE = re.compile(r"^\s*- \[[ xX]\]\s+(T[A-Z]*\d+[a-z]?)\s+\[(RED|GREEN|CHECK|OPS)\]")


def parse_task_markers(text):
    """[(task-azonosító, marker, parancs)] a tasks.md sorai alapján.

    A parancs a sor ELSŐ backtickes szakasza (a sablon szerint:
    `- [ ] T004 [CHECK] Futtasd: \\`<parancs>\\` — plan [P-…] — test [TC-01]`).
    """
    out = []
    for line in text.splitlines():
        m = TASK_LINE_RE.match(line)
        if not m:
            continue
        cmd = re.search(r"`([^`]+)`", line)
        out.append((m.group(1), m.group(2), cmd.group(1).strip() if cmd else ""))
    return out


def _log_table_rows(text):
    """A check-log.md tábla adatsorai: [(sorszám, task-cella, parancs-cella, eredmény-cella)].

    A fejléc `Task` cellájából olvassuk ki a task-oszlop indexét (ez a szó mindkét
    nyelvi fán ugyanaz); ha nincs fejléc, a sablon szerinti 2. cella. A parancs- és
    eredmény-cellát TARTALOM alapján ismerjük fel (backtick, ill. ✓/✗), hogy a
    nyelvfüggő fejlécnevekre ne kelljen támaszkodni.
    """
    rows, task_idx = [], None
    for lineno, line in enumerate(text.splitlines(), start=1):
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        lowered = [c.lower() for c in cells]
        if "task" in lowered and not any(TASK_ID_RE.search(c) for c in cells):
            task_idx = lowered.index("task")
            continue
        if all(set(c) <= {"-", ":", " "} for c in cells):
            continue
        idx = task_idx if task_idx is not None and task_idx < len(cells) else 1
        cmd = next((c for c in cells[idx + 1:] if "`" in c), "")
        result = next((c for c in cells[idx + 1:] if "✓" in c or "✗" in c), "")
        rows.append((lineno, cells[idx], cmd, result))
    return rows


def _selector(cmd):
    """A parancs TESZT-SZŰRŐ része, vagy None. Csak literál mintát ítélünk (CK1/TB2)."""
    m = re.search(r"::[\w:.\[\]-]+", cmd)
    if m:
        return m.group(0)
    m = re.search(r"(?:-t|--test-name-pattern|--testNamePattern)\s+(\"[^\"]+\"|'[^']+'|\S+)", cmd)
    if m:
        return m.group(1).strip("\"'")
    m = re.search(r"-k\s+(\"[^\"]+\"|'[^']+'|\S+)", cmd)
    if m:
        pattern = m.group(1).strip("\"'")
        if re.search(r"\b(and|or|not)\b", pattern):
            return None          # logikai kifejezés — nem ítélünk (BD10)
        return pattern
    return None


def _norm(text):
    return re.sub(r"\s+", " ", text.replace("`", "").replace('"', "").replace("'", "")).strip().lower()


def _exemptions(text, prefix, key_re=r"T[A-Z]*\d+[a-z]?"):
    """{kulcs: indok} a `<PREFIX>: <kulcs> — <indok>` alakú felmentő sorokból.

    A `key_re` alapértéke a TASK-azonosító (`CK-DEVIATION`, `RED-EXEMPT`) —
    ezekre a hívásokra a viselkedés változatlan. A `RUN-EXEMPT` KATEGÓRIA-nevet,
    a `SKIP-EXEMPT` TESZT-függvénynevet kulcsol; azok saját mintát adnak.
    Szándékosan EGY parser marad: három külön felmentés-értelmező csendben
    szétcsúszna egymástól."""
    out = {}
    for m in re.finditer(prefix + r":\s*\**\s*`?(" + key_re + r")`?\s*\**\s*[—–-]+\s*(\S.*)", text):
        out[m.group(1)] = m.group(2).strip()
    return out


def _check_log(cycle):
    return cycle / "test-report" / "implement" / "check-log.md"


def check_command_integrity(cycle, rep, stage):
    """CK1 — a [CHECK] taskok parancsai szó szerint, egyenként futottak-e.

    1. a check-log.md minden sorának `Task` cellája PONTOSAN egy azonosító
       (intervallum/felsorolás → rep.bad);
    2. minden `[CHECK]` taskhoz van legalább egy naplósor a saját azonosítójával;
    3. a naplósor `Parancs` cellája tartalmazza a task parancsának TESZT-SZŰRŐ
       részét (`::<fn>`, `-t "<név>"`, `-k <minta>`), ha a task parancsában van
       ilyen — különben összevont/szűrő nélküli futás.

    Miért kell: egy éles ciklusban nyolc `[CHECK]` task helyett egyetlen, szűrő
    nélküli futás került a naplóba, a `Task` cellájában intervallummal — így sem a
    `tasks.md` és a kód szétcsúszása, sem a `[RED]` taskok zöldsége nem derült ki.
    Eltérés-ág: a jegyzet-szekció `CK-DEVIATION: <task> — <indok>` sora felmenti.
    """
    if stage != "close":
        return
    tasks_text = read(cycle / "tasks.md")
    log_path = _check_log(cycle)
    log_text = read(log_path)
    if log_text is None:
        rep.info("check-log.md: nincs (a CK1 join kimarad — régi ciklusban nem feltétlenül van napló)")
        return
    if tasks_text is None:
        return                      # a check_tasks már jelezte
    rows = _log_table_rows(log_text)
    if not rows:
        rep.info("check-log.md: nincs értelmezhető tábla-sor (a CK1 join kimarad)")
        return

    row_map, sloppy = {}, []
    for lineno, task_cell, cmd_cell, _result in rows:
        ids = TASK_ID_RE.findall(task_cell)
        if len(ids) != 1:
            sloppy.append(f"{lineno}. sor: `{task_cell}`")
            continue
        row_map.setdefault(ids[0], []).append(cmd_cell)
    if sloppy:
        rep.bad(f"check-log.md: {len(sloppy)} sor `Task` cellája nem PONTOSAN egy azonosító "
                f"(intervallum/felsorolás tilos — CK1): " + " · ".join(sloppy[:5]))
    else:
        rep.ok(f"check-log.md: mind a {len(rows)} sor egyetlen task-azonosítóhoz tartozik (CK1)")

    exempt = _exemptions(log_text, "CK-DEVIATION")
    checks = [(tid, cmd) for tid, marker, cmd in parse_task_markers(tasks_text) if marker == "CHECK"]
    if not checks:
        rep.info("tasks.md: nincs `[CHECK]` task (a CK1 join kimarad)")
        return
    missing, unfiltered = [], []
    for tid, cmd in checks:
        if tid in exempt:
            continue
        logged = row_map.get(tid)
        if not logged:
            missing.append(tid)
            continue
        sel = _selector(cmd)
        if sel and not any(_norm(sel) in _norm(c) for c in logged):
            unfiltered.append(f"{tid} (`{sel}`)")
    if missing:
        rep.bad(f"check-log.md: {len(missing)} `[CHECK]` taskhoz nincs saját naplósor (CK1): "
                + ", ".join(missing[:10])
                + " — futtasd egyenként, vagy indokolj `CK-DEVIATION:` sorral")
    if unfiltered:
        rep.bad(f"check-log.md: {len(unfiltered)} `[CHECK]` naplósora nem tartalmazza a task "
                f"parancsának teszt-szűrőjét (összevont/szűrő nélküli futás — CK1): "
                + ", ".join(unfiltered[:10]))
    if not missing and not unfiltered:
        rep.ok(f"minden `[CHECK]` task ({len(checks)}) szó szerint, egyenként futott (CK1)")
    if exempt:
        rep.info(f"CK-DEVIATION felmentés: {', '.join(sorted(exempt))}")


def check_red_proof(cycle, rep, stage):
    """RED1 — minden [RED] taskhoz van bukott futás a check-log.md-ben.

    Egy `assert True` stub fizikailag nem tud vörös lenni: ez az egyetlen
    NEM ítélet-igényes jel arra, hogy a teszt ellenőriz valamit. A join a
    `tasks.md` `[RED]` markereit veti össze a napló `✗` sorainak
    task-azonosítóival; a `RED-EXEMPT: <task> — <indok>` sorok felmentenek
    (meglévő tesztet frissítő, joggal zöld regressziós task).

    A `Task` cella szigorú, egy-azonosítós parse-olása a CK1 dolga
    (`check_command_integrity`) — e nélkül ez a join egyetlen összevont
    futással megetethető lenne.
    """
    if stage != "close":
        return
    tasks_text = read(cycle / "tasks.md")
    log_text = read(_check_log(cycle))
    if log_text is None:
        rep.info("check-log.md: nincs (a RED1 join kimarad)")
        return
    if tasks_text is None:
        return
    reds = [tid for tid, marker, _cmd in parse_task_markers(tasks_text) if marker == "RED"]
    if not reds:
        rep.info("tasks.md: nincs `[RED]` task (a RED1 join kimarad)")
        return
    failing = set()
    for _lineno, task_cell, _cmd, result in _log_table_rows(log_text):
        ids = TASK_ID_RE.findall(task_cell)
        if len(ids) == 1 and "✗" in result:
            failing.add(ids[0])
    exempt = _exemptions(log_text, "RED-EXEMPT")
    missing = [t for t in reds if t not in failing and t not in exempt]
    if missing:
        rep.bad(f"check-log.md: {len(missing)} `[RED]` taskhoz nincs bukott (`✗`) futás (RED1): "
                + ", ".join(missing[:10])
                + " — a tesztnek BUKNIA kell, mielőtt a task lezárul; ha nem tud bukni, "
                  "`RED-EXEMPT: <task> — <indok>` sor a napló jegyzet-szekciójában")
    else:
        rep.ok(f"minden `[RED]` task ({len(reds)}) bukás-bizonyítékkal zárult (RED1)")
    if exempt:
        rep.info(f"RED-EXEMPT felmentés: {', '.join(sorted(exempt))}")


def check_dod(cycle, rep, stage):
    path = cycle / "spec.md"
    text = read(path)
    if text is None:
        rep.bad("spec.md nem található")
        return
    lines = [l for l in text.splitlines() if re.search(r"\bDoD-\d+", l)]
    ids = re.findall(r"\bDoD-(\d+)\b", text)
    if not ids:
        # van-e egyáltalán DoD szekció checkboxokkal?
        m = re.search(r"^#+\s*" + re.escape(sec("definition_of_done")) + r".*$",
                      text, re.MULTILINE | re.IGNORECASE)
        if m:
            tail = text[m.end():]
            nxt = re.search(r"^#+\s", tail, re.MULTILINE)
            block = tail[: nxt.start()] if nxt else tail
            if re.search(r"^\s*- \[[ x]\]", block, re.MULTILINE):
                rep.bad("spec.md: a DoD-pontoknak nincs `DoD-NN` azonosítójuk (DI1) — pótold, "
                        "mielőtt naplózol (a számláló szó szerinti névegyezésre épül)")
                return
        rep.info("spec.md: nem találtam `DoD-NN` azonosítót")
        return
    dupes = {i for i in ids if ids.count(i) > 2}   # a hivatkozások miatt >2 a gyanús
    if dupes:
        rep.info(f"spec.md: `DoD-{'/'.join(sorted(dupes))}` többször szerepel (hivatkozás vagy duplikátum)")
    rep.ok(f"spec.md: {len(set(ids))} DoD-pont, mind azonosítóval (DI1)")
    if stage == "close":
        open_dod = [l.strip() for l in lines if re.match(r"^\s*- \[ \]", l)]
        if open_dod:
            rep.bad(f"spec.md: {len(open_dod)} DoD-pont még nincs kipipálva: "
                    + ", ".join(re.search(r"DoD-\d+", l).group(0) for l in open_dod))
        else:
            rep.ok("spec.md: minden DoD-pont `[x]`")


def check_input_from_prev(cycle, rep, stage):
    path = cycle / "validate-input-from-prev.md"
    text = read(path)
    if text is None:
        rep.info("validate-input-from-prev.md: nincs (nem hiba)")
        return
    open_items = re.findall(r"^\s*- \[ \].*$", text, re.MULTILINE)
    if not open_items:
        rep.ok("validate-input-from-prev.md: minden tétel lezárva (IP1)")
    elif stage == "start":
        rep.info(f"validate-input-from-prev.md: {len(open_items)} nyitott tétel — "
                 "dolgozd fel a test-runner indítása ELŐTT:")
        for item in open_items[:10]:
            print(f"      {item.strip()}")
    else:
        rep.bad(f"validate-input-from-prev.md: {len(open_items)} nyitott tétel (IP1) — "
                "PASS előtt mindet le kell zárni")


def check_review(cycle, rep, stage, require_review):
    if stage == "start":
        return
    path = cycle / "test-report" / "code-review.md"
    legacy = cycle / "code-review.md"
    if not path.exists() and legacy.exists():
        path = legacy
    text = read(path)
    if text is None:
        if require_review:
            rep.bad("test-report/code-review.md nem található — a review-kapu (RV1) nem futott le")
        else:
            rep.info("test-report/code-review.md: még nincs (a review nem futott ebben a körben)")
        return
    status = get_status(path)
    if status is not None:
        head = status.split("|")[0].strip()
        if head == st("in_progress").lower():
            rep.bad(f"code-review.md: a jelentés befejezetlen ({fld('f_status')}: "
                    f"{st('in_progress')}) — a reviewer futása megszakadt, a review-kapu "
                    "(RV1) nem zárható le vele; a kiírt findingok részlegesek (RV-INC)")
            return
    open_mf = re.findall(r"^\s*- \[ \].*$", text, re.MULTILINE)
    if open_mf:
        ids = [m.group(0) for l in open_mf for m in [re.search(r"MF-\d+", l)] if m]
        label = ", ".join(ids) if ids else f"{len(open_mf)} db"
        rep.bad(f"code-review.md: nyitott Must Fix — {label}")
    else:
        rep.ok("code-review.md: nincs nyitott Must Fix (RV1)")


def check_report(cycle, rep, stage):
    if stage == "start":
        return
    path = cycle / "test-report" / "validation-report.md"
    text = read(path)
    if text is None:
        rep.bad("test-report/validation-report.md nem található (VD9)")
        return
    rounds = re.findall(r"^## " + re.escape(sec("round")) + r" (\d+) —", text, re.MULTILINE)
    runs = re.findall(r"^\s*- \*\*Run \d+", text, re.MULTILINE)
    if not rounds:
        rep.bad(f"validation-report.md: nincs `## {sec('round')} N` blokk — "
                f"a riport üres (VD9-guard)")
    elif len(rounds) < len(runs):
        rep.bad(f"validation-report.md: {len(rounds)} kör-blokk, de {len(runs)} futás a History-ban "
                "— hiányzó kör-blokk(ok)")
    else:
        rep.ok(f"validation-report.md: {len(rounds)} kör-blokk, {len(runs)} History-futás")
    missing = [n for n in rounds if not (cycle / "test-report" / "validate" / f"round-{int(n):02d}").is_dir()]
    if missing:
        rep.bad("hiányzó kör-mappa: " + ", ".join(f"validate/round-{int(n):02d}" for n in missing) + " (TR5)")
    elif rounds:
        rep.ok("minden körhöz létezik a `validate/round-NN/` mappa (TR5)")
    if "— folyamatban" in text:
        rep.info("van még nyitott (`folyamatban`) kör-blokk — a `round-log.py close` nem futott le")


# ── SK1 — A NÉMA SKIP NEM BIZONYÍTÉK ────────────────────────────────────────
# Miért kell: egy éles ciklus egyetlen NEM vacuous tesztje `pytest.skip(...)`-pel
# lépett ki (`RUN_DEV_E2E != "true"`), a JUnit XML-ben `skipped` esetként. A
# `dod-check.py` viszont a `<skipped>` esetet `PASS`-ként indexelte — vagyis egy
# némán kihagyott dev-teszt szolgált `DoD-NN` BIZONYÍTÉKKÉNT. A javítás két
# helyen történik: a `dod-check.py`-ban a skip önálló állapot lett (nem
# bizonyíték), itt pedig bukik a kör, ha egy kihagyott teszt a plan lefedettségi
# leképezésében bizonyítékként szerepel.
#
# A join kulcsa a `03b` tesztfájl-adatlapjának `f_test_cases` mezősora:
# `**Teszt-esetek:** \`<teszt-függvény>\` → \`TC-01\` · …`
TEST_CASE_MAP_RE = re.compile(r"`([^`]{4,})`\s*(?:→|->|=>)\s*`?(T[CS]-\d+)`?")
JUNIT_SUITE_TAGS = ("testsuite",)


def _plan_test_case_map(plan_text):
    """{teszt-függvény neve: [TC-ID, …]} a plan adatlapjainak `f_test_cases` soraiból."""
    field = fld("f_test_cases")
    out = {}
    for line in plan_text.splitlines():
        clean = line.strip()
        if field.lower() not in clean.lower():
            continue
        if clean.lstrip("*_ ").lower().startswith("_<"):
            continue                # a sablon dőlt helyőrző-sora, nem adat
        for name, tid in TEST_CASE_MAP_RE.findall(clean):
            name = name.strip().strip("`*_")
            if len(name) < 4 or name.startswith("<"):
                continue
            out.setdefault(name, []).append(tid)
    return out


def _skipped_cases(round_dir):
    """[(teszt-kulcs, forrás-fájl)] a kör-mappa JUnit XML-jeinek `skipped` eseteiből."""
    import xml.etree.ElementTree as ET
    out = []
    for xml in sorted(Path(round_dir).rglob("*.xml")):
        try:
            root = ET.parse(xml).getroot()
        except Exception:
            continue
        suites = [root] if root.tag in JUNIT_SUITE_TAGS else root.iter("testsuite")
        for suite in suites:
            for case in suite.iter("testcase"):
                if case.find("skipped") is None:
                    continue
                cls = case.get("classname", "")
                name = case.get("name", "")
                out.append((f"{cls} > {name}".strip(" >") or name, xml.name))
    return out


def _last_round_dir(cycle):
    base = cycle / "test-report" / "validate"
    if not base.is_dir():
        return None
    dirs = sorted((d for d in base.iterdir()
                   if d.is_dir() and re.fullmatch(r"round-\d+", d.name)),
                  key=lambda d: int(d.name.split("-")[1]))
    return dirs[-1] if dirs else None


def check_skipped_evidence(cycle, rep, stage):
    """SK1 — a plan által bizonyítéknak jelölt teszt nem lehet `skipped`.

    A kihagyott teszt nem ellenőriz semmit: egyetlen `pytest.skip` / `it.skip` /
    `@Disabled` a teszt elején elég lenne ahhoz, hogy a `DoD-NN` „bizonyítékot"
    kapjon. A join a plan adatlapjainak `teszt-függvény → TC-NN` leképezését veti
    össze az UTOLSÓ kör JUnit XML-jeinek `skipped` eseteivel.
    Felmentés: `SKIP-EXEMPT: <teszt-név> — <indok>` a `check-log.md`
    jegyzet-szekciójában (a `RED-EXEMPT` mintájára).
    """
    if stage != "close":
        return
    plan_text = read(cycle / "plan.md")
    if plan_text is None:
        return
    round_dir = _last_round_dir(cycle)
    if round_dir is None:
        return                      # a hiányzó kör-mappát a check_report (TR5) méri
    skipped = _skipped_cases(round_dir)
    if not skipped:
        return                      # nincs kihagyott eset — nincs mit ítélni
    case_map = _plan_test_case_map(plan_text)
    if not case_map:
        rep.info(f"a plan adatlapjaiban nincs `{fld('f_test_cases')}` leképezés "
                 f"(teszt-függvény → `TC-NN`) — az SK1 join kimarad, pedig a "
                 f"`{round_dir.name}` körben {len(skipped)} `skipped` eset van (TA1)")
        return

    log_text = read(_check_log(cycle)) or ""
    exempt = _exemptions(log_text, "SKIP-EXEMPT", key_re=r"[\w./:\[\]>-]+(?:[ \t][\w./:\[\]>-]+)*")
    exempt_norm = {_norm(k) for k in exempt}

    hits, excused = [], []
    for case_key, source in skipped:
        key_norm = _norm(case_key)
        for name, ids in case_map.items():
            if _norm(name) not in key_norm:
                continue
            label = f"`{case_key}` → {', '.join(sorted(set(ids)))} ({source})"
            if any(e in key_norm or _norm(name) in e for e in exempt_norm):
                excused.append(label)
            else:
                hits.append(label)
            break

    for label in hits:
        rep.bad(f"a {label} eset a `{round_dir.name}` körben `skipped` volt, de a plan "
                f"bizonyítéknak jelöli (SK1) — a kihagyott teszt nem bizonyíték: nem "
                f"ellenőriz semmit, mégis zöldnek látszik. Futtasd le (állítsd be a "
                f"kihagyás feltételét adó env-változót), vagy írj "
                f"`SKIP-EXEMPT: <teszt> — <miért nem futtatható ebben a körben>` sort a "
                f"`check-log.md` `## {sec('notes')}` szekciójába")
    if excused:
        rep.info("SKIP-EXEMPT felmentés: " + ", ".join(excused))
    if not hits:
        rep.ok(f"`{round_dir.name}`: a {len(skipped)} `skipped` eset egyike sem szolgál "
               f"plan-beli bizonyítékként (SK1)"
               + (f" — {len(excused)} `SKIP-EXEMPT` felmentéssel" if excused else ""))


# ── RUN1 — KÖR-LEFEDETTSÉG ───────────────────────────────────────────────────
# Miért kell: egy éles ciklus PASS-ra zárt úgy, hogy a plan gépi futtatási
# táblájában deklarált `dev` kategória SOHA nem futott le — se nem íródott meg
# a dev-módja. Két ágens is elemezte a validálási problémákat, egyik sem vette
# észre, mert ez HIÁNY-állítás („egy deklarált kategória nem futott le"), amit
# egy LLM-review szerkezetileg rosszul lát. Determinisztikusan viszont triviális:
# a plan táblája ↔ a kör `results.json`-ja join.
#
# A `run-tests.py` a TÁBLÁBÓL futtat és a kör-mappába írja a `results.json`-t.
# Ha a mappában nincs `results.json`, akkor a kört NEM a táblából hajtották,
# hanem ad-hoc kézi parancsokból — és onnantól egyetlen `EV` kapu sem fut le,
# és nincs gépi nyoma, melyik kategória futott.

_RUN_TESTS_MODULE = None


def _load_run_tests_module():
    """A `run-tests.py` betöltése modulként (a kötőjeles név miatt importlib).

    A tábla parse-olója (`parse_matrix`) és a fázis-értelmezője (`row_phases`)
    ott él; SZÁNDÉKOSAN nem írjuk meg másodszor — egy harmadik tábla-értelmezés
    a kapu és a futtató csendes szétcsúszását adná (a `run-tests.py` maga is így
    emeli be a `report-gate-check.py`-t)."""
    global _RUN_TESTS_MODULE
    if _RUN_TESTS_MODULE is not None:
        return _RUN_TESTS_MODULE or None
    import importlib.util
    path = Path(__file__).resolve().parent / "run-tests.py"
    if not path.exists():
        _RUN_TESTS_MODULE = False
        return None
    spec = importlib.util.spec_from_file_location("_run_tests", path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception:
        _RUN_TESTS_MODULE = False
        return None
    _RUN_TESTS_MODULE = module
    return module


def _norm_category(value):
    """Kategória-név normalizálás a joinhoz: a plan celláiban `` `R06` `` és
    `**e2e**` alak is előfordul, a `results.json`-ban a nyers név áll."""
    return (value or "").strip().strip("`*_").strip().lower()


def check_run_coverage(cycle, rep, stage):
    """RUN1 — TELJES körben lefutott-e a plan MINDEN `validate`-fázisú kategóriája.

    Csak TELJES körre mér (D3): a könnyű kör (VD10) SZÁNDÉKOSAN futtat
    részhalmazt, ott a check minden javító körben hamis pozitívot adna.
    Ha a planban nincs gépi tábla, a check kimarad (`info`) — a régi, lezárt
    ciklusokat bukató kapu használhatatlan, és a tábla hiányát az `S1` amúgy is
    méri a `03b` lezárásakor.
    Felmentés: `RUN-EXEMPT: <kategória> — <indok>` sor az ADOTT kör blokkjában.
    """
    if stage != "close":
        return
    plan_text = read(cycle / "plan.md")
    if plan_text is None:
        return                      # a hiányzó plant a fázis-belépő kapu méri
    rt = _load_run_tests_module()
    if rt is None:
        rep.info("run-tests.py nem tölthető be a scriptek mellől — a RUN1 join kimarad")
        return
    try:
        matrix = rt.parse_matrix(plan_text)
    except Exception as exc:
        rep.info(f"a plan gépi futtatási táblája nem értelmezhető ({exc}) — a RUN1 join kimarad")
        return
    if not matrix:
        rep.info(f"plan.md: nincs `{sec('machine_run_table')}` szekció — a RUN1 join kimarad "
                 "(a tábla hiányát a `03b` `S1` kapuja méri)")
        return

    expected = []
    for row in matrix:
        if "validate" in rt.row_phases(row):
            expected.append(row["kategoria"])
    if not expected:
        rep.info(f"a gépi futtatási tábla egyetlen sora sem fut a "
                 f"`{st('phase_validate')}` fázisban — a RUN1 join kimarad (ezt a PH1 méri)")
        return

    report_text = read(cycle / "test-report" / "validation-report.md")
    if report_text is None:
        return                      # a check_report már jelezte

    # A kör-blokkok: `## <Kör> N — <dátum> — TELJES|KÖNNYŰ — <státusz>`.
    # A típus-literált NEM írjuk be: `st("round_type_full")`. A `round-log.py`
    # a régebbi, más nyelven nyitott riportokat is felismeri, ezért itt is
    # mindkét nyelv szavát elfogadjuk.
    full_words = list(dict.fromkeys([st("round_type_full"), "TELJES", "FULL"]))
    light_words = list(dict.fromkeys([st("round_type_light"), "KÖNNYŰ", "LIGHT"]))
    types = "|".join(re.escape(w) for w in full_words + light_words)
    round_re = re.compile(r"^## " + re.escape(sec("round")) + r" (\d+) — .* — (" + types + r")\b",
                          re.MULTILINE)
    matches = list(round_re.finditer(report_text))
    full_rounds = [(m, m.group(1), m.group(2)) for m in matches if m.group(2) in full_words]
    if not full_rounds:
        rep.info(f"validation-report.md: nincs `{st('round_type_full')}` kör-blokk — "
                 "a RUN1 join kimarad (PASS csak teljes körből adható — VD10/1)")
        return

    # A MEGSZAKADT és a még NYITOTT kör kimarad: a 07 szerint a megszakadt kört
    # nem írjuk felül, hanem `**Megszakadt**` sorral lezárjuk és új kört nyitunk
    # — egy ilyen, részleges bizonyítékú kört visszamenőleg bukatni hamis pozitív
    # lenne (a fejlesztő nem tudja utólag lefuttatni). A nyitott (`folyamatban`)
    # blokkot a `check_report` amúgy is jelzi.
    interrupted_words = [w.lower() for w in dict.fromkeys(["megszakadt", "interrupted"])]
    in_progress_word = st("in_progress").lower()

    covered_rounds, excused_total, ignored = 0, 0, []
    for m, number, _rtype in full_rounds:
        # a kör blokkja: a fejlécétől a KÖVETKEZŐ kör-fejlécig (a felmentő sorok
        # kereséséhez — a felmentés a saját körére szól, nem az egész riportra)
        nxt = next((x.start() for x in matches if x.start() > m.start()), len(report_text))
        block = report_text[m.start():nxt]
        header_line = block.splitlines()[0].lower()
        block_low = block.lower()
        if in_progress_word in header_line or any(w in block_low for w in interrupted_words):
            ignored.append(number)
            continue
        exempt = {_norm_category(k): v
                  for k, v in _exemptions(block, "RUN-EXEMPT",
                                          key_re=r"[^\s—–]+(?:[ \t][^\s—–]+)*").items()}
        n = int(number)
        results_path = cycle / "test-report" / "validate" / f"round-{n:02d}" / "results.json"
        if not results_path.exists():
            rep.bad(f"a `round-{n:02d}` {st('round_type_full')} kör, de nincs `results.json` "
                    f"(RUN1) — a kört NEM a plan gépi futtatási táblájából hajtották. A `07` a "
                    f"`run-tests.py`-jal futtat, és az írja a `results.json`-t; kézi "
                    f"parancsokból nincs gépi nyoma, mely kategória futott le — és egyetlen "
                    f"`EV` kapu sem fut le. Futtasd a kört a `run-tests.py`-jal")
            continue
        try:
            entries = json.loads(results_path.read_text(encoding="utf-8")).get("results", [])
        except Exception as exc:
            rep.bad(f"a `round-{n:02d}` `results.json`-ja nem olvasható ({exc}) — RUN1")
            continue
        ran = {_norm_category(e.get("kategoria")) for e in entries}
        missing, excused = [], []
        for cat in expected:
            key = _norm_category(cat)
            if key in ran:
                continue
            (excused if key in exempt else missing).append(cat)
        for cat in missing:
            rep.bad(f"a `round-{n:02d}` {st('round_type_full')} körből hiányzik a `{cat}` "
                    f"kategória (RUN1) — a plan a `{st('phase_validate')}` fázisra írja elő, "
                    f"de a kör `results.json`-jában nem szerepel. Vagy futtasd le "
                    f"(`run-tests.py --phase validate`), vagy — ha ebben a körben tudatosan "
                    f"nem futtatható — írj `RUN-EXEMPT: {cat} — <miért>` sort a kör blokkjába")
        if excused:
            excused_total += len(excused)
            rep.info(f"`round-{n:02d}` RUN-EXEMPT felmentés: " + ", ".join(excused))
        if not missing:
            covered_rounds += 1
    if ignored:
        rep.info("RUN1: kihagyott kör(ök) — megszakadt vagy még nyitott blokk: "
                 + ", ".join(f"round-{int(n):02d}" for n in ignored))
    if covered_rounds == len(full_rounds) - len(ignored):
        rep.ok(f"minden lezárt {st('round_type_full')} kör ({len(full_rounds) - len(ignored)}) lefedi a plan "
               f"{len(expected)} `{st('phase_validate')}`-fázisú kategóriáját (RUN1)"
               + (f" — ebből {excused_total} `RUN-EXEMPT` felmentéssel" if excused_total else ""))


# ── RL1/RL2 — A REST-NAPLÓ SZERKEZETE ÉS A CÍMKE ↔ BIZONYÍTÉK JOIN ──────────
# Miért kell: az eddigi bizonyítékok mind KATEGÓRIA-szemcsések. A `results.json`
# a DEKLARÁLT környezetet írja, az `EV6` a körben keletkezett napló tartalmát nézi
# kategória-szinten, a JUnit XML pedig hostot nem rögzít. Azt, hogy egy KONKRÉT
# teszt hol futott, semmi nem mondta meg — a `rest-logs/` egy LAPOS HALOM volt.
# Egy éles ciklusban 50 naplófájl állt egy mappában, mind egy korábbi körből
# örökölt és `127.0.0.1`-es: a mappa TELINEK LÁTSZOTT.
#
# A `03b` oldalán a `TS-NN` fejléce `[local]`/`[remote]` címkét kap (SZÁNDÉK —
# `EV8`/`EV9`/`EV10`); itt a napló teszt-szerinti almappába kerül (BIZONYÍTÉK):
#
#     <kör-mappa>/<kategória>/rest-logs/<local|remote>/<teszt-név>/
#
# Az érték a kettő JOINJÁBAN van:
#   RL1 — útvonal ↔ TARTALOM: a `remote/` alatti napló tartalmaz-e valóban
#         nem-lokális címet (és a `local/` alatti nem csak távolit).
#   RL2 — címke ↔ BIZONYÍTÉK: minden `[remote]`-nak jelölt forgatókönyv tesztje
#         termelt-e egyáltalán remote naplót ebben a körben.
# Egy `[remote]`-nak jelölt teszt, amelynek naplói `local/` alá kerültek — vagy
# amelynek egyáltalán nincs naplója — ÖNELLENTMONDÁS.
#
# A besorolás NEM a hívott címből jön (azt a naplózó fixture a teszt SAJÁT
# jelöléséből választja), mert a cím mindkét irányban téved: egy `oc port-forward`
# mögötti `127.0.0.1` remote, egy compose service-név pedig local. Ezért az
# ÚTVONAL önmagában nem bizonyíték — a bizonyíték a mappa TARTALMA (RL1) —, a
# port-forward pedig DEKLARÁLT: a `Környezetek és végpontok` tábla `remote`
# környezetű sorainak lokálisnak látszó címei a felmentett címek.
#
# Régi ciklus nem bukhat (D9): ha a kör-mappában nincs `local/`/`remote/` alszint,
# a konvenció nincs használatban — `info`, nem bukás.

_ANALYZE_MODULE = None


def _load_analyze_module():
    """Az `analyze-gate-check.py` betöltése modulként (a kötőjeles név miatt importlib).

    A `TS-NN` fejléc-parser (`parse_ts_blocks`, benne a `scope` mezővel) ott él;
    SZÁNDÉKOSAN nem írjuk meg harmadszor — a `03b` kapuja és a `07` kapuja
    ugyanabból az EGY parse-olóból dolgozik, különben a címke-értelmezésük
    csendben szétcsúszhatna. A fájl importálható: minden futtatható kódja
    `main()`-ben és `if __name__ == "__main__":` alatt van."""
    global _ANALYZE_MODULE
    if _ANALYZE_MODULE is not None:
        return _ANALYZE_MODULE or None
    import importlib.util
    path = Path(__file__).resolve().parent / "analyze-gate-check.py"
    if not path.exists():
        _ANALYZE_MODULE = False
        return None
    spec = importlib.util.spec_from_file_location("_analyze_gate", path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception:
        _ANALYZE_MODULE = False
        return None
    _ANALYZE_MODULE = module
    return module


# A `03b` sablonja SZÓ SZERINT ezt a szabályt írja elő a célprojektnek
# (`00-init-project.md`, TR3 kitöltési szabályok) — a két oldalnak UGYANÚGY kell
# normalizálnia, különben az RL2 néma hamis pozitívokat ad.
def _scope_dir_name(name):
    """Teszt-függvénynév → útvonal-biztos mappanév.

    `[^A-Za-z0-9._-]` → `-`, a széleken lévő `-` levágva, kisbetűsítés NINCS.
    Paraméterezett teszt: `test_foo[dsp01]` → `test_foo-dsp01` (EGY szint marad,
    a paraméter nem lesz külön alkönyvtár — a függvénynév-prefix így is megmarad,
    és a `_plan_test_case_map()` a függvénynévre joinol)."""
    return re.sub(r"[^A-Za-z0-9._-]", "-", (name or "").strip()).strip("-")


# `` `test_foo` → `TC-01` [remote] `` — a függvény szintjén FELÜLÍRT hatókör
# (vegyes hatókörű tesztfájlnál; a `03b` sablonja ezt engedi meg).
FUNC_SCOPE_RE = re.compile(r"`([^`]{4,})`\s*(?:→|->|=>)\s*`?T[CS]-\d+`?\s*\[(local|remote)\]",
                           re.IGNORECASE)


def _plan_func_scopes(plan_text):
    """{teszt-függvény: 'local'|'remote'} a `f_test_cases` sorok EXPLICIT címkéiből."""
    field = fld("f_test_cases")
    out = {}
    for line in plan_text.splitlines():
        clean = line.strip()
        if field.lower() not in clean.lower():
            continue
        for name, scope in FUNC_SCOPE_RE.findall(clean):
            out[name.strip().strip("`*_")] = scope.lower()
    return out


def _declared_local_looking_hosts(texts, agc, rt):
    """A DEKLARÁLT port-forward címek: a `remote` környezetű táblasorok
    lokálisnak látszó címei (`| remote | keycloak (port-forward → …) |
    \\`http://127.0.0.1:8080\\` | … |`).

    Nem találgat: a sor ALAKJÁBÓL dolgozik — nem-lokális `Környezet` cella +
    lokálisnak látszó URL. Ez az egyetlen hely, ahol egyáltalán LÁTSZIK, hogy egy
    „lokális" cím mögött osztott klaszter van."""
    out = set()
    for text in texts:
        for line in (text or "").splitlines():
            stripped = line.strip()
            if not stripped.startswith("|"):
                continue
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if len(cells) < 3 or agc._env_is_local(cells[0]):
                continue
            for host in rt.HOST_RE.findall(stripped):
                if rt.LOCAL_HOST_RE.search(host):
                    out.add(host)
    return out


def _scope_units(scope_dir):
    """A hatókör-mappa vizsgálati egységei: a `<teszt-név>/` alkönyvtárak.

    Ha nincs alkönyvtár, de vannak közvetlen fájlok, MAGA a mappa az egység —
    így a „scope-olt, de teszt-szerint nem bontott" napló is ítélet alá kerül,
    ahelyett hogy csendben kimaradna."""
    subs = sorted(d for d in scope_dir.iterdir() if d.is_dir())
    if subs:
        return [(d.name, d) for d in subs]
    if any(p.is_file() for p in scope_dir.iterdir()):
        return [("(közvetlen fájlok)", scope_dir)]
    return []


def _logged_hosts(unit_dir, rt):
    """Az egység szöveges naplófájljaiban szereplő hostok."""
    hosts = set()
    for path in sorted(unit_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in rt.AUDIT_TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        hosts |= set(rt.HOST_RE.findall(text))
    return hosts


def check_rest_log_scope(cycle, rep, stage, conventions_path=None):
    """RL1/RL2 — a REST-napló hatóköre: útvonal ↔ tartalom, és címke ↔ bizonyíték."""
    if stage != "close":
        return
    round_dir = _last_round_dir(cycle)
    if round_dir is None:
        return                      # a hiányzó kör-mappát a check_report (TR5) méri

    # A `local`/`remote` szint egy NAPLÓ-mappa alatt áll (`rest-logs`, `audit-logs`, …).
    # A szűkítés szándékos: egy máshova tartozó, `local`/`remote` nevű könyvtár ne
    # kerüljön ítélet alá.
    scope_dirs = [d for d in sorted(round_dir.rglob("*"))
                  if d.is_dir() and d.name in ("local", "remote")
                  and "log" in d.parent.name.lower()]
    if not scope_dirs:
        rep.info(f"`{round_dir.name}`: nincs `rest-logs/<local|remote>/` alszint — az RL1/RL2 "
                 "kimarad (a teszt-szerinti napló-konvenció nincs használatban ebben a "
                 "projektben; a bevezetését a `conventions.md` TR3 kitöltési szabályai írják le)")
        return

    rt = _load_run_tests_module()
    if rt is None:
        rep.info("run-tests.py nem tölthető be a scriptek mellől — az RL1 tartalom-vizsgálata "
                 "kimarad (onnan jön a host-értelmezés és a szöveges kiterjesztés-lista)")
        return
    agc = _load_analyze_module()
    if agc is None:
        rep.info("analyze-gate-check.py nem tölthető be a scriptek mellől — az RL1/RL2 kimarad "
                 "(onnan jön a `TS-NN` fejléc-parser a hatókör-címkével)")
        return

    # ── A port-forward FELMENTÉS bemenete ────────────────────────────────────
    # A `Környezetek és végpontok` tábla a `specs/test-conventions.md` koordináta-
    # regiszterében áll (TC1/c), de projektenként a `conventions.md`-ben is lehet —
    # ezért MINDKETTŐT beolvassuk. Ha egyik sem elérhető, a check FUT TOVÁBB, csak a
    # felmentés nem alkalmazható; az üzenet ezt kimondja.
    decl_texts, decl_sources = [], []
    for label, path in (("conventions.md", Path(conventions_path) if conventions_path else None),
                        ("test-conventions.md", cycle.parent / "test-conventions.md")):
        if path is not None and path.is_file():
            decl_texts.append(read(path) or "")
            decl_sources.append(label)
    exempt_hosts = _declared_local_looking_hosts(decl_texts, agc, rt)
    no_decl_hint = ("" if decl_sources else
                    " (a `conventions.md` / `specs/test-conventions.md` nem elérhető, ezért a "
                    "port-forward felmentés nem alkalmazható — add meg a `--conventions` kapcsolóval)")

    # ── RL1 — útvonal ↔ tartalom ─────────────────────────────────────────────
    # A bukást LOKÁLISAN tartjuk számon: a `rep.failed` az egész futásra vonatkozik,
    # abból nem derülne ki, hogy az RL1 maga rendben volt-e.
    checked, excused, rl1_failed = 0, [], False
    for scope_dir in scope_dirs:
        for unit_name, unit_dir in _scope_units(scope_dir):
            checked += 1
            hosts = _logged_hosts(unit_dir, rt)
            remote_hosts = {h for h in hosts if not rt.LOCAL_HOST_RE.search(h)}
            rel = unit_dir.relative_to(round_dir)
            if scope_dir.name == "remote":
                if remote_hosts:
                    continue
                if hosts & exempt_hosts:
                    excused.append(f"`{rel}` (deklarált port-forward: "
                                   f"{', '.join(sorted(hosts & exempt_hosts))})")
                    continue
                rl1_failed = True
                rep.bad(f"a `{unit_name}` teszt naplói a `remote/` mappában állnak "
                        f"(`{rel}`), de egyik sem tartalmaz nem-lokális címet (RL1) — a "
                        f"„remote\" futás LOKÁLIS futás volt. Ez pontosan az a hibaosztály, "
                        f"ahol minden teszt zöld lesz, miközben a TELEPÍTETT komponenst senki "
                        f"nem szólította meg. Ha `port-forward` mögött fut, vedd fel a "
                        f"`Környezetek és végpontok` táblába `remote` környezetű sorként, a "
                        f"lokálisnak látszó címmel{no_decl_hint}")
            elif hosts and not (hosts - remote_hosts):
                rl1_failed = True
                rep.bad(f"a `{unit_name}` teszt naplói a `local/` mappában állnak (`{rel}`), de "
                        f"MINDEN logolt cím nem-lokális ({', '.join(sorted(remote_hosts))}) — RL1. "
                        f"Fordított tévedés: a teszt valójában `remote`, de `local`-nak jelölték. "
                        f"Javítsd a teszt jelölését ÉS a plan `TS-NN` fejlécének hatókör-címkéjét "
                        f"— különben a `[remote]` forgatókönyvek bizonyítéka hiányozni fog")

    if not rl1_failed:
        rep.ok(f"`{round_dir.name}`: {len(scope_dirs)} hatókör-mappa, {checked} teszt-napló — "
               f"az útvonal és a tartalom nem mond ellent (RL1)"
               + (f" — {len(excused)} deklarált port-forward felmentéssel" if excused else ""))
    if excused:
        rep.info("RL1 port-forward felmentés: " + ", ".join(excused))

    # ── RL2 — címke ↔ bizonyíték join ────────────────────────────────────────
    plan_text = read(cycle / "plan.md")
    if plan_text is None:
        return                      # a hiányzó plant a fázis-belépő kapu méri
    try:
        blocks = agc.parse_ts_blocks(plan_text)
    except Exception as exc:
        rep.info(f"a plan `TS-NN` blokkjai nem értelmezhetők ({exc}) — az RL2 join kimarad")
        return
    remote_ids = {b["id"] for b in blocks if b.get("scope") == "remote"}
    explicit = _plan_func_scopes(plan_text)
    if not remote_ids and "remote" not in explicit.values():
        rep.info("a plan egyetlen `[remote]` forgatókönyvet sem tartalmaz — az RL2 join kimarad "
                 "(a remote-lefedettséget a `03b` `EV9` kapuja méri)")
        return

    case_map = _plan_test_case_map(plan_text)
    # A leképezés `TC-NN`/`TS-NN`-re mutat, a hatókör viszont a `TS-NN`-en van. Ha egy
    # függvény CSAK `TC-NN`-re hivatkozik (unit-eset), az definíció szerint izolált,
    # tehát `local` — nem hiányzó remote, kimarad az RL2-ből.
    remote_funcs = {name for name, ids in case_map.items() if set(ids) & remote_ids}
    remote_funcs |= {name for name, sc in explicit.items() if sc == "remote"}
    remote_funcs -= {name for name, sc in explicit.items() if sc == "local"}
    if not remote_funcs:
        rep.info(f"a plan `{fld('f_test_cases')}` leképezéseiből egyetlen teszt-függvény sem "
                 f"köthető `[remote]` forgatókönyvhöz — az RL2 join kimarad (a leképezés hiányát "
                 f"a `TA1` méri a `03b` lezárásakor)")
        return

    have = set()
    for scope_dir in scope_dirs:
        if scope_dir.name != "remote":
            continue
        have |= {d.name for d in scope_dir.iterdir() if d.is_dir()}

    log_text = read(_check_log(cycle)) or ""
    scope_exempt = _exemptions(log_text, "SCOPE-EXEMPT", key_re=r"[\w./:\[\]-]+")
    exempt_dirs = {_scope_dir_name(k) for k in scope_exempt}

    missing, rl2_excused = [], []
    for name in sorted(remote_funcs):
        want = _scope_dir_name(name)
        # PREFIX-illesztés: a plan `test_foo` bejegyzése illeszkedik a paraméterezett
        # `test_foo-dsp01` mappára is — enélkül minden paraméterezett teszt hamisan
        # hiányzónak látszana.
        if any(d == want or d.startswith(want) for d in have):
            continue
        if want in exempt_dirs or any(want.startswith(e) or e.startswith(want) for e in exempt_dirs):
            rl2_excused.append(name)
            continue
        missing.append(name)

    for name in missing:
        ids = ", ".join(sorted(set(case_map.get(name, [])) & remote_ids)) or "[remote]"
        rep.bad(f"a `{name}` teszt a plan {ids} `[remote]` forgatókönyvéhez tartozik, de a "
                f"`{round_dir.name}` körben nincs `rest-logs/remote/{_scope_dir_name(name)}/` "
                f"naplója (RL2) — vagy nem futott le, vagy nem indított forgalmat. A címke "
                f"SZÁNDÉK, a napló BIZONYÍTÉK: a kettő együtt mondja meg, hogy a teszt tényleg "
                f"a telepített komponenst szólította meg. Felmentés: "
                f"`SCOPE-EXEMPT: {name} — <indok>` a `check-log.md` `## {sec('notes')}` "
                f"szekciójában")
    if rl2_excused:
        rep.info("RL2 SCOPE-EXEMPT felmentés: " + ", ".join(rl2_excused))
    if not missing:
        rep.ok(f"`{round_dir.name}`: mind a {len(remote_funcs)} `[remote]` teszt-függvényhez van "
               f"`rest-logs/remote/` napló (RL2)"
               + (f" — ebből {len(rl2_excused)} `SCOPE-EXEMPT` felmentéssel" if rl2_excused else ""))


def check_start_statuses(cycle, rep):
    plan = get_status(cycle / "plan.md")
    spec = get_status(cycle / "spec.md")
    if plan is None:
        rep.info("plan.md: nincs státusz-sor")
    elif plan in (st("ready_for_tasks").lower(), st("done").lower()):
        rep.ok(f"plan.md státusz: {plan}")
    else:
        rep.bad(f"plan.md státusz: '{plan}' — várt: "
                f"`{st('ready_for_tasks')}` vagy `{st('done')}`")
    if spec is None:
        rep.info("spec.md: nincs státusz-sor")
    elif spec in (st("ready_for_plan").lower(), st("done").lower()):
        rep.ok(f"spec.md státusz: {spec}")
    else:
        rep.bad(f"spec.md státusz: '{spec}' — várt: "
                f"`{st('ready_for_plan')}` vagy `{st('done')}`")


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
    parser = argparse.ArgumentParser(description="07-validate determinisztikus gyűjtőkapu.")
    parser.add_argument("cycle_dir", help="a ciklus mappája (specs/cycle-NN-<name>)")
    parser.add_argument("--stage", choices=["start", "close"], default="close")
    parser.add_argument("--require-review", action="store_true",
                        help="a code-review.md hiánya bukás (PASS előtt kötelező)")
    parser.add_argument("--conventions", default="conventions.md",
                        help="a projekt conventions.md-je — az RL1 port-forward felmentéséhez. "
                             "A `Környezetek és végpontok` táblát a kapu a "
                             "`specs/test-conventions.md`-ben is keresi (TC1/c szerint az a "
                             "koordináta-regiszter). Ha egyik sem létezik, a felmentés nem "
                             "alkalmazható — a check attól még fut")
    args = parser.parse_args()

    cycle = Path(args.cycle_dir)
    if not cycle.is_dir():
        print(f"HIBA: nincs ilyen ciklusmappa: {cycle}", file=sys.stderr)
        return 2

    rep = Report()
    print(f"07-validate kapu — {cycle} — szakasz: {args.stage}")
    if args.stage == "start":
        check_start_statuses(cycle, rep)
    check_tasks(cycle, rep, args.stage)
    check_command_integrity(cycle, rep, args.stage)
    check_red_proof(cycle, rep, args.stage)
    check_dod(cycle, rep, args.stage)
    check_input_from_prev(cycle, rep, args.stage)
    check_review(cycle, rep, args.stage, args.require_review)
    check_report(cycle, rep, args.stage)
    check_run_coverage(cycle, rep, args.stage)
    check_skipped_evidence(cycle, rep, args.stage)
    check_rest_log_scope(cycle, rep, args.stage, conventions_path=args.conventions)

    print("EREDMÉNY: " + ("BUKOTT — a fenti ✗ pontokat rendezd" if rep.failed else "OK"))
    return 1 if rep.failed else 0


if __name__ == "__main__":
    sys.exit(main())
