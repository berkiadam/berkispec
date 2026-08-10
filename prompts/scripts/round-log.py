#!/usr/bin/env python3
"""Validálási kör-napló kezelése — a `validation-report.md` `## Kör N` blokkjai
determinisztikusan, LLM nélkül (07-validate, VD9).

Miért kell: a kör-blokk 90%-a mechanikus (sorszám, időbélyeg, kör-típus,
riport-mappa, lépés-tábla a parancsokkal és darabszámokkal, kapu-exitkódok).
Ha ezt az orchestrátor írja kézzel, az (a) körönként 1-1,5k output token,
(b) instrukció-követésen múlik, hogy egyáltalán elkészül-e, és (c) a teljes
fájl újraírásakor korábbi körök vesznek el. Ez a szkript mindhármat megoldja:
csak beszúr és a NYITOTT blokkot módosítja, a lezárt köröket és a
`# Validation History` szekciót soha nem érinti.

Munkamegosztás:
  - `open`  → a kör ELEJÉN (a tesztek indítása előtt): létrehozza a fájlt, ha
              nincs, megnyitja a `## Kör N` blokkot a `# Validation History`
              fejléc ELÉ, és létrehozza a hozzá tartozó `round-NN/` mappát
              (a sorszám így strukturálisan nem tud elcsúszni — TR5).
  - `step`  → menet közben: egy sort fűz a lépés-táblához (idempotens
              szerkesztés, a blokk többi része érintetlen).
  - `close` → a kör VÉGÉN, a `failure-counter.py` ELŐTT: lezárja a blokkot
              (eredmény, bukott elemek, DoD-tábla, review, döntés), és
              frissíti a fájl fejlécét.

Amit az LLM ad hozzá: a szabad szöveges mezők (kör döntése, DoD-indoklás) —
minden más gépi forrásból (`run-tests.py --json`, kapu-exitkódok) jön.

Kilépő kód: 0 = rendben
            1 = használati hiba (hiányzó fájl, nincs nyitott kör, rossz típus)
"""
import argparse
import re
import sys
from pathlib import Path

HISTORY_HEADER = "# Validation History"
ROUND_RE = re.compile(r"^## Kör (\d+) —", re.MULTILINE)
STEP_TABLE_HEADER = "| # | Idő | Lépés | Mit futtatott | Eredmény |"
STEP_TABLE_SEP = "|---|---|---|---|---|"


def split_history(text):
    """(fej, history) — a history a `# Validation History` fejléctől a végéig."""
    idx = text.find(HISTORY_HEADER)
    if idx == -1:
        return text.rstrip("\n") + "\n", ""
    return text[:idx], text[idx:]


def new_file_header(cycle_name, timestamp):
    return (
        f"# Validálási riport — {cycle_name}\n\n"
        "**Jelenlegi státusz:** folyamatban\n"
        "**Körök száma:** 0\n"
        f"**Utolsó frissítés:** {timestamp}\n\n"
        "---\n\n"
    )


def read_report(path, cycle_name, timestamp):
    if path.exists():
        return path.read_text(encoding="utf-8")
    return new_file_header(cycle_name, timestamp) + HISTORY_HEADER + "\n"


def round_numbers(head):
    return [int(m.group(1)) for m in ROUND_RE.finditer(head)]


def last_round_span(head):
    """(start, end) az UTOLSÓ `## Kör N` blokkra a fejben, vagy None."""
    matches = list(ROUND_RE.finditer(head))
    if not matches:
        return None
    return matches[-1].start(), len(head)


def normalize_type(value):
    v = (value or "").strip().upper()
    if v in ("TELJES", "FULL"):
        return "TELJES"
    if v in ("KÖNNYŰ", "KONNYU", "KONNYŰ", "LIGHT"):
        return "KÖNNYŰ"
    return None


def update_header(head, status=None, rounds=None, timestamp=None):
    if status is not None:
        head = re.sub(r"^\*\*Jelenlegi státusz:\*\*.*$",
                      f"**Jelenlegi státusz:** {status}", head, count=1, flags=re.MULTILINE)
    if rounds is not None:
        head = re.sub(r"^\*\*Körök száma:\*\*.*$",
                      f"**Körök száma:** {rounds}", head, count=1, flags=re.MULTILINE)
    if timestamp is not None:
        head = re.sub(r"^\*\*Utolsó frissítés:\*\*.*$",
                      f"**Utolsó frissítés:** {timestamp}", head, count=1, flags=re.MULTILINE)
    return head


def cmd_open(args):
    path = Path(args.report_file)
    cycle_dir = path.parent.parent          # <cycle>/test-report/x.md → <cycle>
    cycle_name = args.cycle_name or cycle_dir.name
    rtype = normalize_type(args.type)
    if rtype is None:
        print("HIBA: a --type értéke TELJES vagy KÖNNYŰ lehet.", file=sys.stderr)
        return 1

    text = read_report(path, cycle_name, args.timestamp)
    head, history = split_history(text)

    numbers = round_numbers(head)
    if numbers and args.reuse_open and "— folyamatban" in head[last_round_span(head)[0]:]:
        n = numbers[-1]
        print(f"Kör {n} már nyitva — újranyitás kihagyva.")
    else:
        n = (max(numbers) if numbers else 0) + 1
        block = (
            f"## Kör {n} — {args.timestamp} — {rtype} — folyamatban\n\n"
            f"**Indító:** {args.trigger}\n"
            f"**Riport-mappa:** `test-report/{args.round_base}/round-{n:02d}/`\n\n"
            "### Lépések (végrehajtási sorrendben)\n\n"
            f"{STEP_TABLE_HEADER}\n{STEP_TABLE_SEP}\n\n"
        )
        head = head.rstrip("\n") + "\n\n" + block
        head = update_header(head, status="folyamatban", rounds=n, timestamp=args.timestamp)

    round_dir = path.parent / args.round_base / f"round-{n:02d}"
    round_dir.mkdir(parents=True, exist_ok=True)

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(head + history)

    print(f"Kör {n} megnyitva ({rtype}).")
    print(f"Riport-mappa: {round_dir}")
    print(f"round-subdir: test-report/{args.round_base}/round-{n:02d}")
    return 0


def parse_step(raw):
    """'10:32|test-runner — gyors tesztek|npm test|✓ 43 passed' → 4 mező."""
    parts = [p.strip() for p in raw.split("|")]
    while len(parts) < 4:
        parts.append("—")
    return parts[:4]


def append_steps(block, steps):
    if not steps:
        return block
    lines = block.split("\n")
    try:
        sep_idx = lines.index(STEP_TABLE_SEP)
    except ValueError:
        print("HIBA: a nyitott körben nincs lépés-tábla (sérült blokk).", file=sys.stderr)
        return None
    end = sep_idx + 1
    while end < len(lines) and lines[end].startswith("|"):
        end += 1
    existing = end - sep_idx - 1
    rows = []
    for i, raw in enumerate(steps, start=existing + 1):
        t, name, cmd, result = parse_step(raw)
        cmd = f"`{cmd}`" if cmd not in ("—", "") and not cmd.startswith("`") else cmd
        rows.append(f"| {i} | {t} | {name} | {cmd} | {result} |")
    lines[end:end] = rows
    return "\n".join(lines)


def cmd_step(args):
    path = Path(args.report_file)
    if not path.exists():
        print(f"HIBA: nincs ilyen fájl: {path}", file=sys.stderr)
        return 1
    head, history = split_history(path.read_text(encoding="utf-8"))
    span = last_round_span(head)
    if span is None:
        print("HIBA: nincs megnyitott kör — előbb futtasd az `open` alparancsot.", file=sys.stderr)
        return 1
    start, end = span
    block = append_steps(head[start:end], args.step)
    if block is None:
        return 1
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(head[:start] + block + history)
    print(f"{len(args.step)} lépés-sor hozzáfűzve.")
    return 0


def build_sections(args):
    out = []
    if args.failed_item:
        out.append("### Bukott elemek\n")
        for item in args.failed_item:
            out.append(f"- `{item}`")
        out.append("")
    if args.dod:
        out.append("### Definition of done\n")
        out.append("| ID | Eredmény | Indoklás |")
        out.append("|---|---|---|")
        for raw in args.dod:
            parts = [p.strip() for p in raw.split("|")]
            while len(parts) < 3:
                parts.append("—")
            out.append(f"| {parts[0]} | {parts[1]} | {parts[2]} |")
        out.append("")
    if args.review:
        out.append("### Kódreview (RV1)\n")
        for line in args.review:
            out.append(f"- {line}")
        out.append("")
    if args.note:
        out.append("### Megjegyzések\n")
        for line in args.note:
            out.append(f"- {line}")
        out.append("")
    out.append("### A kör döntése\n")
    out.append(args.decision or "—")
    out.append("")
    return "\n".join(out)


def rebuild_summary(head):
    """`## Összegzés` újragenerálása a körök fejléceiből (gépi adat)."""
    rounds = re.findall(r"^## Kör (\d+) — .* — (TELJES|KÖNNYŰ) — (\S+)$", head, re.MULTILINE)
    if not rounds:
        return head
    total = len(rounds)
    full = sum(1 for r in rounds if r[1] == "TELJES")
    light = total - full
    last = rounds[-1][2]
    summary = (
        "## Összegzés\n\n"
        f"- **Végeredmény:** {last} — {total} kör után\n"
        f"- **Körök:** {total} összesen — ebből {full} teljes, {light} könnyű _(VD10)_\n"
    )
    head = re.sub(r"\n## Összegzés\n.*?(?=\n## |\Z)", "\n", head, flags=re.DOTALL)
    # A lezárt kör-blokk már `---`-re végződik: ne tegyünk elé még egyet.
    head = head.rstrip("\n")
    if head.endswith("---"):
        head = head[:-3].rstrip("\n")
    return head + "\n\n---\n\n" + summary + "\n"


def cmd_close(args):
    path = Path(args.report_file)
    if not path.exists():
        print(f"HIBA: nincs ilyen fájl: {path}", file=sys.stderr)
        return 1
    head, history = split_history(path.read_text(encoding="utf-8"))
    span = last_round_span(head)
    if span is None:
        print("HIBA: nincs megnyitott kör — a `## Kör N` blokk hiányzik.", file=sys.stderr)
        return 1
    start, end = span
    block = head[start:end]
    if "— folyamatban" not in block.split("\n")[0]:
        print("FIGYELEM: az utolsó kör már le van zárva — a blokk felülírás nélkül marad.",
              file=sys.stderr)
        return 1

    block = append_steps(block, args.step) if args.step else block
    if block is None:
        return 1
    lines = block.split("\n")
    lines[0] = re.sub(r"— folyamatban$", f"— {args.result}", lines[0])
    block = "\n".join(lines).rstrip("\n") + "\n\n" + build_sections(args) + "\n---\n"

    head = head[:start] + block
    n = round_numbers(head)[-1]
    status = {"PASS": "PASS", "FAIL": "folyamatban"}.get(args.result, args.result)
    if args.final:
        status = args.final
    head = update_header(head, status=status, rounds=n, timestamp=args.timestamp)
    if args.summary or args.result == "PASS" or args.final:
        head = rebuild_summary(head)

    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(head.rstrip("\n") + "\n\n" + history)
    print(f"Kör {n} lezárva — {args.result}.")
    return 0


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
        description="A validation-report.md kör-blokkjainak determinisztikus kezelése (VD9).")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_open = sub.add_parser("open", help="új kör megnyitása + round-NN mappa létrehozása")
    p_open.add_argument("report_file")
    p_open.add_argument("--type", required=True, help="TELJES | KÖNNYŰ")
    p_open.add_argument("--timestamp", required=True, help="YYYY-MM-DD HH:MM")
    p_open.add_argument("--trigger", default="07-validate futás",
                        help="mi indította a kört (első futás / hurok N. iterációja / megerősítő kör)")
    p_open.add_argument("--round-base", default="validate", help="alap: validate")
    p_open.add_argument("--cycle-name", default=None)
    p_open.add_argument("--reuse-open", action="store_true",
                        help="ha az utolsó kör még nyitva van, ne nyisson újat (folytatás)")
    p_open.set_defaults(func=cmd_open)

    p_step = sub.add_parser("step", help="lépés-sor hozzáfűzése a nyitott körhöz")
    p_step.add_argument("report_file")
    p_step.add_argument("--step", action="append", required=True,
                        help="'idő|lépés|parancs|eredmény' — többször megadható")
    p_step.set_defaults(func=cmd_step)

    p_close = sub.add_parser("close", help="a nyitott kör lezárása")
    p_close.add_argument("report_file")
    p_close.add_argument("--result", required=True, choices=["PASS", "FAIL"])
    p_close.add_argument("--timestamp", required=True)
    p_close.add_argument("--step", action="append", default=[])
    p_close.add_argument("--failed-item", action="append", default=[])
    p_close.add_argument("--dod", action="append", default=[],
                         help="'DoD-01|✓|indoklás'")
    p_close.add_argument("--review", action="append", default=[])
    p_close.add_argument("--note", action="append", default=[])
    p_close.add_argument("--decision", default=None)
    p_close.add_argument("--summary", action="store_true", help="`## Összegzés` újragenerálása")
    p_close.add_argument("--final", default=None,
                         help="a fázis végállapota a fejlécbe: 'PASS' | 'FAIL (megállt)' | 'eszkalálva'")
    p_close.set_defaults(func=cmd_close)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
