#!/usr/bin/env python3
"""Determinisztikus futás-napló + per-item bukás-számláló a 07-validate
(`# Validation History`) és a 05-analyze (`# Hurok-napló`) önjavító
hurkaihoz.

A fő ágens eddig kézzel parse-olta a History-t és inkrementálta a
`Consecutive Failures for this item` értéket — ez a törékeny lépés (egy
elgépelt/parafrazeált item-név csendben elronthatja a 3-próba leállást).
Ez a szkript ezt determinisztikussá teszi: beolvassa a meglévő naplót,
hozzáfűz egy új futás-bejegyzést a dokumentált formátumban, és minden
bukott itemhez kiszámolja, hányadik egymást követő futásban bukott
(a legfrissebb futásoktól visszafelé, az első nem-bukásig).

**Egy VALIDÁLÁSI KÖR = EGY futás-bejegyzés.** Részeredményt (pl. „a gyors
tesztek zöldek, a nehezek még nem futottak") TILOS külön `Run`-ként
naplózni: egy közbeiktatott PASS-bejegyzés megszakítja az egymást követő
bukások láncát, és a 3-próba leállás soha nem lépne életbe. A kör
eredményét a kör VÉGÉN naplózd, egyszer, az összes bukott itemmel.

Három, egymást kiegészítő leállási korlát (bármelyik → exit 3):
  1. per-item egymást követő bukás  (--threshold, alap 3)   — a klasszikus 3-próba
  2. per-item ÖSSZES bukás a naplóban (--max-item-total, alap 5)
       → megfogja azt is, ha közbeiktatott PASS-ok tördelik a láncot
  3. egymást követő FAIL-futások száma (--max-fail-runs, alap 5)
       → globális backstop, ha körönként MÁS item bukik (a hurok divergál)

Kilépő kód:
  0  — naplózva, egyetlen korlát sem érte el a küszöböt (a hurok folytatható)
  3  — naplózva, legalább egy korlát elérte a küszöböt (a huroknak MEG KELL állnia)
  1  — hiba (pl. rossz argumentum, írási hiba) — ilyenkor a napló NEM módosult,
       a hívó NE naplózzon kézzel, hanem javítsa a hívást és futtassa újra
"""
import argparse
import re
import sys
from pathlib import Path


RUN_HEADER_RE = re.compile(r"^\s*-\s*\*\*Run\s+(\d+)\s*\(([^)]*)\)\s*-\s*(PASS|FAIL)\*\*", re.IGNORECASE)
FAILED_ITEM_RE = re.compile(r"^\s*-\s*\*\*Failed Item:\*\*\s*(.+?)\s*$")


def parse_history(text):
    """A meglévő napló futásait adja vissza időrendben (legrégebbi elöl):
    [{"num": int, "ts": str, "result": "PASS"|"FAIL", "items": [str, ...]}, ...].
    Egy futás több bukott itemet is tartalmazhat (több 'Failed Item:' sor)."""
    runs = []
    current = None
    for line in text.splitlines():
        m = RUN_HEADER_RE.match(line)
        if m:
            current = {"num": int(m.group(1)), "ts": m.group(2).strip(),
                       "result": m.group(3).upper(), "items": []}
            runs.append(current)
            continue
        mi = FAILED_ITEM_RE.match(line)
        if mi and current is not None:
            item = mi.group(1).strip()
            if item and item not in current["items"]:
                current["items"].append(item)
    return runs


def consecutive_count(prior_runs, item):
    """Hány egymást követő (legfrissebb felé) korábbi futásban szerepelt az
    item bukottként, megszakítás nélkül. A mostani futás nincs benne."""
    count = 0
    for run in reversed(prior_runs):
        if run["result"] == "FAIL" and item in run["items"]:
            count += 1
        else:
            break
    return count


def total_count(prior_runs, item):
    """Hányszor bukott az item ÖSSZESEN a naplóban (a láncot megszakító
    PASS-bejegyzésektől függetlenül). A mostani futás nincs benne."""
    return sum(1 for run in prior_runs if run["result"] == "FAIL" and item in run["items"])


def consecutive_fail_runs(prior_runs):
    """Hány egymást követő FAIL-futás áll a napló végén (item-től függetlenül)."""
    count = 0
    for run in reversed(prior_runs):
        if run["result"] == "FAIL":
            count += 1
        else:
            break
    return count


def print_status(runs, threshold, max_item_total, max_fail_runs):
    """Read-only állapotjelentés: mit mond a napló MOST, naplózás nélkül.
    A hívó ebből tudja a hurok-eleji korai figyelmeztetést megfogalmazni."""
    if not runs:
        print("A napló üres (még nem volt futás).")
        return 0
    last = runs[-1]
    print(f"Utolsó futás: Run {last['num']} ({last['ts']}) - {last['result']}")
    if last["result"] == "FAIL":
        prior = runs[:-1]
        for item in last["items"]:
            c = consecutive_count(prior, item) + 1
            t = total_count(prior, item) + 1
            print(f"  - {item}: {c}/{threshold} egymást követő, {t}/{max_item_total} összes bukás")
    print(f"Egymást követő FAIL-futások: {consecutive_fail_runs(runs)}/{max_fail_runs}")
    return 0



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
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("history_file", help="a napló fájl útvonala (validation-report.md vagy code-review.md)")
    parser.add_argument("--result", choices=["PASS", "FAIL"],
                        help="a mostani VALIDÁLÁSI KÖR eredménye (kötelező, ha nem --status)")
    parser.add_argument("--failed-item", action="append", default=[], metavar="NÉV",
                        help="egy bukott item pontos neve (FAIL esetén ismételhető; test-runner szó szerinti neveivel, DoD esetén a DoD-NN azonosítóval)")
    parser.add_argument("--details", default="", help="rövid hibaleírás a FAIL bejegyzéshez (a futás szintjén jelenik meg)")
    parser.add_argument("--timestamp", metavar="YYYY-MM-DD HH:MM",
                        help="a futás időbélyege (a hívó adja meg — a szkript nem olvas rendszeridőt a determinizmus végett); kötelező, ha nem --status")
    parser.add_argument("--header", default="Validation History",
                        help="a napló szekció címe (alap: 'Validation History')")
    parser.add_argument("--threshold", type=int, default=3,
                        help="per-item egymást követő bukás küszöb (alap: 3)")
    parser.add_argument("--max-item-total", type=int, default=5,
                        help="per-item ÖSSZES bukás küszöb a naplóban (alap: 5) — a megszakított láncot is megfogja")
    parser.add_argument("--max-fail-runs", type=int, default=5,
                        help="egymást követő FAIL-futások küszöbe (alap: 5) — globális backstop divergáló hurokra")
    parser.add_argument("--status", action="store_true",
                        help="read-only: kiírja a napló jelenlegi állapotát (utolsó futás + számlálók), NEM naplóz")
    args = parser.parse_args()

    path = Path(args.history_file)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""

    if args.status:
        return print_status(parse_history(existing), args.threshold,
                            args.max_item_total, args.max_fail_runs)

    if not args.result:
        print("HIBA: --result kötelező (vagy használd a --status módot).", file=sys.stderr)
        return 1
    if not args.timestamp:
        print("HIBA: --timestamp kötelező (formátum: 'YYYY-MM-DD HH:MM').", file=sys.stderr)
        return 1
    if args.result == "FAIL" and not args.failed_item:
        print("HIBA: FAIL eredményhez legalább egy --failed-item kell.", file=sys.stderr)
        return 1
    if args.result == "PASS" and args.failed_item:
        print("HIBA: PASS eredményhez nem adható --failed-item. Egy validálási kör "
              "eredménye vagy teljesen zöld (PASS), vagy FAIL a bukott itemekkel.", file=sys.stderr)
        return 1

    if f"# {args.header}" not in existing:
        prefix = existing.rstrip()
        existing = (prefix + "\n\n" if prefix else "") + f"# {args.header}\n"

    prior_runs = parse_history(existing)
    run_num = (max((r["num"] for r in prior_runs), default=0)) + 1

    lines = []
    stop_reasons = []
    warnings = []
    if args.result == "PASS":
        lines.append(f"- **Run {run_num} ({args.timestamp}) - PASS**")
    else:
        lines.append(f"- **Run {run_num} ({args.timestamp}) - FAIL**")
        if args.details:
            lines.append(f"  - **Details:** {args.details}")
        for item in args.failed_item:
            n = consecutive_count(prior_runs, item) + 1
            t = total_count(prior_runs, item) + 1
            lines.append(f"  - **Failed Item:** {item}")
            lines.append(f"  - **Consecutive Failures for this item:** {n}")
            lines.append(f"  - **Total Failures for this item:** {t}")
            if n >= args.threshold:
                stop_reasons.append(f"'{item}' — {n} egymást követő bukás (küszöb: {args.threshold})")
            elif t >= args.max_item_total:
                stop_reasons.append(f"'{item}' — összesen {t} bukás a naplóban (küszöb: {args.max_item_total})")
            elif t > n:
                warnings.append(
                    f"'{item}' korábban is bukott (összesen {t}×), de egy közbeeső PASS-bejegyzés "
                    f"megszakította a láncot (most {n}). Ha ugyanabban a validálási körben naplóztál "
                    f"részeredményt (pl. külön a gyors teszteket), az HIBÁS — körönként egyetlen "
                    f"futás-bejegyzés készülhet, a kör végén.")

    fail_runs = consecutive_fail_runs(prior_runs) + (1 if args.result == "FAIL" else 0)
    if args.result == "FAIL" and fail_runs >= args.max_fail_runs:
        stop_reasons.append(
            f"{fail_runs} egymást követő FAIL-futás (küszöb: {args.max_fail_runs}) — a hurok divergál")

    new_entry = "\n".join(lines)
    updated = existing.rstrip() + "\n" + new_entry + "\n"
    try:
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(updated)
    except OSError as exc:
        print(f"HIBA: a napló nem írható ({exc}).", file=sys.stderr)
        return 1

    print(f"Naplózva: Run {run_num} — {args.result} → {path}")
    if args.result == "FAIL":
        for item in args.failed_item:
            n = consecutive_count(prior_runs, item) + 1
            t = total_count(prior_runs, item) + 1
            print(f"  - {item}: {n}/{args.threshold} egymást követő, {t}/{args.max_item_total} összes bukás")
        print(f"  - egymást követő FAIL-futások: {fail_runs}/{args.max_fail_runs}")
    for w in warnings:
        print(f"FIGYELEM: {w}")
    if stop_reasons:
        print("KÜSZÖB ELÉRVE — a hurok MEGÁLL: " + "; ".join(stop_reasons))
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
