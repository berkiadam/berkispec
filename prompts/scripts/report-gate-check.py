#!/usr/bin/env python3
"""TR3 kapu — a ciklus `test-report/` mappájában kötelező teszt-riportok
determinisztikus ellenőrzése (07-validate).

Miért kell: a teszt-futtatás eredménye a chatben él, a chat pedig `/clear`
után nincs. A projekt teszt-eszközének SAJÁT riportja (Allure, Playwright
HTML, pytest-html, JUnit XML, coverage) az egyetlen utólag megnyitható
bizonyíték arról, mi futott le és hogyan — ezért minden ciklusban ott kell
lennie a `specs/cycle-NN-<name>/test-report/` mappában.

Hol keresi (TR5): a riportok KÖRÖNKÉNTI almappákban élnek, hogy egy önjavító
hurok minden körének megmaradjon a saját bizonyítéka:

  specs/cycle-NN-<name>/test-report/
  ├── validation-report.md            (a 07 naplója — nem a kapu dolga)
  ├── implement/check-log.md          (a 06 [CHECK]-naplója — nem a kapu dolga)
  ├── validate/round-01/ round-02/    (a 07 validálási körei)

A vizsgált mappát a hívó adja meg a `--report-subdir` kapcsolóval, pl.
`--report-subdir test-report/validate/round-02`. Az alapérték (`test-report`)
csak visszafelé kompatibilitás a körönkénti bontás bevezetése előtti
ciklusokhoz — új futásban MINDIG add meg a kör-mappát.

Mit ellenőriz: a `conventions.md` `## Teszt-riportolás` szekciójának
táblázatában DEKLARÁLT artefaktumok tényleg léteznek-e a megadott
kör-mappában, és nem üresek-e. A táblázat a single source of truth (a
00-init a felhasználóval együtt tölti ki) — a script nem találgat eszközt,
csak azt kéri számon, amit a projekt maga vállalt.

Mikor hívd: csak TELJES körben. Könnyű körben (VD10) szándékosan nem fut
minden tesztkategória, így a teljes tábla nem is teljesíthető — ott a kapu
kimarad (a 07 skill szabálya).

A táblázat várt formája (a fejléc szövege nem számít, az OSZLOPSORREND igen):

  ## Teszt-riportolás

  **Riport-generálás kötelező:** igen

  | Teszt-kategória | Eszköz | Riport-generáló parancs | Artefaktum a kör-mappában |
  |---|---|---|---|
  | E2E | Playwright + Allure | `npm run e2e:report` | `allure-report.html` |
  | Unit | Vitest | `npm run test:report` | `unit-report.html` |

Az utolsó oszlop a vizsgált KÖR-MAPPÁHOZ képest relatív útvonal (fájl vagy
mappa). A `-` / `N/A` / üres érték = nincs artefaktum ehhez a
sorhoz (kihagyva). Ha a szekcióban `**Riport-generálás kötelező:** nem`
szerepel, a kapu tudatos projekt-döntés alapján kihagyódik (exit 0).

MIGRÁCIÓS ŐR (TR5/b) — az utolsó oszlop JELENTÉSE 2026-08-07-én megváltozott:
korábban a ciklus `test-report/` gyökeréhez, ma a KÖR-MAPPÁHOZ képest relatív.
A formátum nem változott, ezért egy régi tábla csendben félreértelmeződik. Emiatt
a szekcióban KÖTELEZŐ egy jelölő, ami kimondja, mihez képest relatív az oszlop:

  **Artefaktum-útvonal alapja:** kör-mappa        ← mai (TR5) séma
  **Artefaktum-útvonal alapja:** test-report      ← régi, flat séma (támogatott)

Ha a jelölő hiányzik, a kapu NEM találgat: exit 2, és kiírja a pótlandó sort.
Ha `test-report`, a kapu a ciklus `test-report/` mappájához oldja fel az
útvonalakat (a `--report-subdir` ilyenkor csak tájékoztató) — így egy régi
projekt a migráció előtt sem kap hamis bukást.

Kilépő kód: 0 = minden deklarált artefaktum megvan (vagy a kapu kihagyva)
            1 = hiányzó vagy üres artefaktum → a validálás NEM zárható PASS-ra
            2 = használati hiba (nem létező conventions.md / ciklusmappa,
                vagy hiányzó `## Teszt-riportolás` szekció)
"""
import argparse
import re
import sys
from pathlib import Path


SECTION_RE = re.compile(r"^##\s+Teszt-riportolás\s*$", re.IGNORECASE)
NEXT_SECTION_RE = re.compile(r"^##\s+")
REQUIRED_FLAG_RE = re.compile(r"\*\*Riport-generálás kötelező:\*\*\s*(\w+)", re.IGNORECASE)
SEPARATOR_ROW_RE = re.compile(r"^\|[\s:|-]+\|$")
PATH_BASE_RE = re.compile(r"\*\*Artefaktum-útvonal alapja:\*\*\s*([\w-]+)", re.IGNORECASE)
BASE_ROUND = {"kör-mappa", "kor-mappa", "körmappa", "round", "kör"}
BASE_FLAT = {"test-report", "testreport", "flat", "gyökér", "gyoker"}
EMPTY_VALUES = {"", "-", "–", "—", "n/a", "na", "nincs"}


def extract_section(text):
    """A `## Teszt-riportolás` szekció sorai (a következő `## ` fejlécig)."""
    lines = text.splitlines()
    out, inside = [], False
    for line in lines:
        if SECTION_RE.match(line):
            inside = True
            continue
        if inside and NEXT_SECTION_RE.match(line):
            break
        if inside:
            out.append(line)
    return out if inside else None


def parse_rows(section_lines):
    """A táblázat adatsorai → [(kategória, eszköz, parancs, artefaktum), ...].
    A fejlécsort és az elválasztó sort kihagyja."""
    rows = []
    seen_separator = False
    for line in section_lines:
        s = line.strip()
        if not s.startswith("|"):
            continue
        if SEPARATOR_ROW_RE.match(s):
            seen_separator = True
            continue
        if not seen_separator:
            continue  # fejlécsor
        cells = [c.strip().strip("`").strip() for c in s.strip("|").split("|")]
        if len(cells) < 4:
            continue
        rows.append((cells[0], cells[1], cells[2], cells[-1]))
    return rows


def check_artifact(report_dir, rel):
    """(ok, üzenet) — létezik-e és nem üres-e az artefaktum."""
    target = report_dir / rel
    if not target.exists():
        return False, f"HIÁNYZIK: {target}"
    if target.is_dir():
        files = [p for p in target.rglob("*") if p.is_file() and p.stat().st_size > 0]
        if not files:
            return False, f"ÜRES MAPPA: {target}"
        total = sum(p.stat().st_size for p in files)
        return True, f"ok: {target}/ ({len(files)} fájl, {total // 1024} KB)"
    if target.stat().st_size == 0:
        return False, f"ÜRES FÁJL: {target}"
    return True, f"ok: {target} ({target.stat().st_size // 1024} KB)"



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
    parser.add_argument("conventions", help="a projekt gyökerében lévő conventions.md útvonala")
    parser.add_argument("cycle_dir", help="a ciklus mappája (specs/cycle-NN-<name>)")
    parser.add_argument("--report-subdir", default="test-report",
                        help="a vizsgált kör-mappa a cikluson belül, pl. "
                             "'test-report/validate/round-02' vagy "
                             "'test-report/review/round-01' (TR5). Alap: 'test-report' "
                             "— csak régi, körönkénti bontás előtti ciklusokhoz")
    args = parser.parse_args()

    conv = Path(args.conventions)
    if not conv.exists():
        print(f"HIBA: nincs ilyen fájl: {conv}", file=sys.stderr)
        return 2
    cycle = Path(args.cycle_dir)
    if not cycle.is_dir():
        print(f"HIBA: nincs ilyen ciklusmappa: {cycle}", file=sys.stderr)
        return 2

    section = extract_section(conv.read_text(encoding="utf-8"))
    if section is None:
        print(f"HIBA: a {conv} nem tartalmaz `## Teszt-riportolás` szekciót. "
              f"Ez a 00-init kötelező szekciója — pótold a felhasználóval egyeztetve, "
              f"mielőtt a validálás lezárul.", file=sys.stderr)
        return 2

    flag = REQUIRED_FLAG_RE.search("\n".join(section))
    if flag and flag.group(1).lower() in {"nem", "no", "false"}:
        print("A kapu kihagyva: a conventions.md szerint a riport-generálás "
              "nem kötelező ebben a projektben (tudatos döntés).")
        return 0

    base = PATH_BASE_RE.search("\n".join(section))
    base_value = base.group(1).lower() if base else None
    if base_value is None:
        print(
            "HIBA (TR5/b migrációs őr): a `## Teszt-riportolás` szekcióból hiányzik az\n"
            "  **Artefaktum-útvonal alapja:** mező.\n\n"
            "Az utolsó oszlop jelentése 2026-08-07-én megváltozott (test-report/ gyökér →\n"
            "kör-mappa), a formátum viszont nem — ezért a kapu nem találgat. Írd be a\n"
            f"`{conv}` `## Teszt-riportolás` szekciójába a **Riport-generálás kötelező:**\n"
            "mező mellé az alábbiak közül a helyeset:\n\n"
            "  **Artefaktum-útvonal alapja:** kör-mappa     (mai séma: test-report/validate/round-NN/)\n"
            "  **Artefaktum-útvonal alapja:** test-report    (régi, flat séma)\n\n"
            "Ha a ciklus most tér át a mai sémára, a `conventions.md` frissítése a ciklus\n"
            "része (kell rá task) — lásd a 03-write-plan „Kapu-konfiguráció együtt mozog\" szabályát.",
            file=sys.stderr,
        )
        return 2
    if base_value in BASE_FLAT:
        args.report_subdir = "test-report"
        print("MEGJEGYZÉS: a conventions.md a RÉGI, flat sémát deklarálja "
              "(`Artefaktum-útvonal alapja: test-report`) — a kapu a ciklus "
              "`test-report/` mappájához oldja fel az útvonalakat, a --report-subdir "
              "értékét figyelmen kívül hagyja.")
    elif base_value not in BASE_ROUND:
        print(f"HIBA: ismeretlen `Artefaktum-útvonal alapja:` érték: `{base_value}`. "
              f"Elfogadott: `kör-mappa` vagy `test-report`.", file=sys.stderr)
        return 2

    rows = parse_rows(section)
    if not rows:
        print(f"HIBA: a `## Teszt-riportolás` szekcióban nincs kitöltött táblázat. "
              f"Vagy deklarálj artefaktumokat, vagy írd be explicit: "
              f"`**Riport-generálás kötelező:** nem` + indoklás.", file=sys.stderr)
        return 2

    report_dir = cycle / args.report_subdir
    print(f"Riport-kapu (TR3) — {report_dir}")
    failures = []
    checked = 0
    for kategoria, eszkoz, _parancs, artefakt in rows:
        if artefakt.lower() in EMPTY_VALUES:
            print(f"  - {kategoria} ({eszkoz}): nincs deklarált artefaktum — kihagyva")
            continue
        checked += 1
        ok, msg = check_artifact(report_dir, artefakt)
        print(f"  - {kategoria} ({eszkoz}): {msg}")
        if not ok:
            failures.append((kategoria, eszkoz, artefakt))

    if not checked:
        print("HIBA: a táblázat minden sora üres artefaktumot deklarál — "
              "így a kapu nem ellenőriz semmit. Töltsd ki, vagy állítsd a "
              "`**Riport-generálás kötelező:**` mezőt `nem`-re, indoklással.", file=sys.stderr)
        return 2

    if failures:
        print("\nKAPU BUKOTT — hiányzó teszt-riport(ok):")
        for kategoria, eszkoz, artefakt in failures:
            print(f"  ✗ {kategoria} ({eszkoz}) → {artefakt}")
        print("A validálás NEM zárható PASS-ra. Futtasd a conventions.md "
              "`## Teszt-riportolás` táblájában megadott riport-generáló parancsot, "
              f"és másold az artefaktumot ebbe a kör-mappába: {report_dir}")
        return 1

    print(f"\nKAPU OK — mind a {checked} deklarált riport-artefaktum megvan.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
