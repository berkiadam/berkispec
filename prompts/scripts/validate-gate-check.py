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

Kilépő kód: 0 = minden vizsgált kapu rendben
            1 = legalább egy kapu bukott (a kör nem zárható PASS-ra)
            2 = használati hiba (nem létező ciklusmappa)

A `--require-review` nélkül a hiányzó `code-review.md` csak INFO (pl. az első,
tesztekre bukó körben a review el sem indult). PASS előtt add meg — akkor a
hiánya bukás.
"""
import argparse
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


def _exemptions(text, prefix):
    """{task: indok} a napló jegyzet-szekciójának `<PREFIX>: <task> — <indok>` sorai alapján."""
    out = {}
    for m in re.finditer(prefix + r":\s*\**\s*(T[A-Z]*\d+[a-z]?)\s*\**\s*[—–-]+\s*(\S.*)", text):
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

    print("EREDMÉNY: " + ("BUKOTT — a fenti ✗ pontokat rendezd" if rep.failed else "OK"))
    return 1 if rep.failed else 0


if __name__ == "__main__":
    sys.exit(main())
