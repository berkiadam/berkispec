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
    · spec.md: minden DoD-pontnak van `DoD-NN` azonosítója, egyediek,
      és nincs köztük nyitott `- [ ]` (DI1)
    · validate-input-from-prev.md: nincs nyitott `[ ]` tétel (IP1)
    · test-report/code-review.md: nincs nyitott `- [ ] **MF-NN**` (RV1)
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

FIX_SECTIONS = ("## Validációs javítások", "## Review javítások")


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
        if re.match(r"^[Ss]tátusz\s*:", clean):
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
        if "validálásra kész" in status:
            rep.ok(f"tasks.md státusz: {status}")
        else:
            rep.bad(f"tasks.md státusz: '{status}' — a 07 `Validálásra kész`-t vár (vissza a 06-ra)")
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
        m = re.search(r"^#+\s*Definition of done.*$", text, re.MULTILINE | re.IGNORECASE)
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
    rounds = re.findall(r"^## Kör (\d+) —", text, re.MULTILINE)
    runs = re.findall(r"^\s*- \*\*Run \d+", text, re.MULTILINE)
    if not rounds:
        rep.bad("validation-report.md: nincs `## Kör N` blokk — a riport üres (VD9-guard)")
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
    elif plan in ("task írásra kész", "kész"):
        rep.ok(f"plan.md státusz: {plan}")
    else:
        rep.bad(f"plan.md státusz: '{plan}' — várt: `Task írásra kész` vagy `Kész`")
    if spec is None:
        rep.info("spec.md: nincs státusz-sor")
    elif spec in ("tervezésre kész", "kész"):
        rep.ok(f"spec.md státusz: {spec}")
    else:
        rep.bad(f"spec.md státusz: '{spec}' — várt: `Tervezésre kész` vagy `Kész`")


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
    check_dod(cycle, rep, args.stage)
    check_input_from_prev(cycle, rep, args.stage)
    check_review(cycle, rep, args.stage, args.require_review)
    check_report(cycle, rep, args.stage)

    print("EREDMÉNY: " + ("BUKOTT — a fenti ✗ pontokat rendezd" if rep.failed else "OK"))
    return 1 if rep.failed else 0


if __name__ == "__main__":
    sys.exit(main())
