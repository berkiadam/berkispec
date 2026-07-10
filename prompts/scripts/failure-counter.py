#!/usr/bin/env python3
"""Determinisztikus futás-napló + per-item egymást-követő-bukás számláló a
07-validate (`# Validation History`) és a 09-review (`# Review History`)
önjavító hurkaihoz.

A fő ágens eddig kézzel parse-olta a History-t és inkrementálta a
`Consecutive Failures for this item` értéket — ez a törékeny lépés (egy
elgépelt/parafrazeált item-név csendben elronthatja a 3-próba leállást).
Ez a szkript ezt determinisztikussá teszi: beolvassa a meglévő naplót,
hozzáfűz egy új futás-bejegyzést a dokumentált formátumban, és minden
bukott itemhez kiszámolja, hányadik egymást követő futásban bukott
(a legfrissebb futásoktól visszafelé, az első nem-bukásig).

Kilépő kód:
  0  — naplózva, egyetlen item sem érte el a küszöböt (a hurok folytatható)
  3  — naplózva, legalább egy item elérte a küszöböt (a huroknak MEG KELL állnia)
  1  — hiba (pl. rossz argumentum)
"""
import argparse
import re
import sys
from pathlib import Path


RUN_HEADER_RE = re.compile(r"^\s*-\s*\*\*Run\s+(\d+)\s*\(([^)]*)\)\s*-\s*(PASS|FAIL)\*\*", re.IGNORECASE)
FAILED_ITEM_RE = re.compile(r"^\s*-\s*\*\*Failed Item:\*\*\s*(.+?)\s*$")


def parse_history(text):
    """A meglévő napló futásait adja vissza időrendben (legrégebbi elöl):
    [{"num": int, "result": "PASS"|"FAIL", "items": [str, ...]}, ...].
    Egy futás több bukott itemet is tartalmazhat (több 'Failed Item:' sor)."""
    runs = []
    current = None
    for line in text.splitlines():
        m = RUN_HEADER_RE.match(line)
        if m:
            current = {"num": int(m.group(1)), "result": m.group(3).upper(), "items": []}
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("history_file", help="a napló fájl útvonala (validate-decision.md vagy code-review.md)")
    parser.add_argument("--result", required=True, choices=["PASS", "FAIL"], help="a mostani futás eredménye")
    parser.add_argument("--failed-item", action="append", default=[], metavar="NÉV",
                        help="egy bukott item pontos neve (FAIL esetén ismételhető; test-runner szó szerinti neveivel)")
    parser.add_argument("--details", default="", help="rövid hibaleírás a FAIL bejegyzéshez")
    parser.add_argument("--timestamp", required=True, metavar="YYYY-MM-DD HH:MM",
                        help="a futás időbélyege (a hívó adja meg — a szkript nem olvas rendszeridőt a determinizmus végett)")
    parser.add_argument("--header", default="Validation History",
                        help="a napló szekció címe (alap: 'Validation History'; a 09-nél 'Review History')")
    parser.add_argument("--threshold", type=int, default=3, help="egymást követő bukás küszöb (alap: 3)")
    args = parser.parse_args()

    if args.result == "FAIL" and not args.failed_item:
        print("HIBA: FAIL eredményhez legalább egy --failed-item kell.", file=sys.stderr)
        return 1

    path = Path(args.history_file)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""

    if f"# {args.header}" not in existing:
        prefix = existing.rstrip()
        existing = (prefix + "\n\n" if prefix else "") + f"# {args.header}\n"

    prior_runs = parse_history(existing)
    run_num = (max((r["num"] for r in prior_runs), default=0)) + 1

    lines = []
    threshold_items = []
    if args.result == "PASS":
        lines.append(f"- **Run {run_num} ({args.timestamp}) - PASS**")
    else:
        lines.append(f"- **Run {run_num} ({args.timestamp}) - FAIL**")
        for item in args.failed_item:
            n = consecutive_count(prior_runs, item) + 1
            lines.append(f"  - **Failed Item:** {item}")
            lines.append(f"  - **Consecutive Failures for this item:** {n}")
            if args.details:
                lines.append(f"  - **Details:** {args.details}")
            if n >= args.threshold:
                threshold_items.append((item, n))

    new_entry = "\n".join(lines)
    updated = existing.rstrip() + "\n" + new_entry + "\n"
    path.write_text(updated, encoding="utf-8")

    print(f"Naplózva: Run {run_num} — {args.result} → {path}")
    if args.result == "FAIL":
        for item in args.failed_item:
            n = consecutive_count(prior_runs, item) + 1
            print(f"  - {item}: {n}/{args.threshold} egymást követő bukás")
    if threshold_items:
        names = ", ".join(f"'{i}' ({n})" for i, n in threshold_items)
        print(f"KÜSZÖB ELÉRVE ({args.threshold}): {names} — a hurok MEGÁLL.")
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
