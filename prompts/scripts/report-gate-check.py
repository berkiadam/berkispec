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

RIPORT-FÁZISOK (TR6) — a `**Riport-fázisok:**` mező sorolja fel, MELY fázisok
kötelesek a teljes artefaktum-készletet előállítani. Elfogadott értékek:
`implement` (a 06-implement záró állapota) és `validate` (a 07 teljes körei).
A mező hiányában az alapérték `validate` — ez a korábbi viselkedés. Ha a kapu
olyan fázis-mappára fut, amit a mező nem sorol fel, a kapu **kihagyja magát**
(exit 0, magyarázó sorral): így a hívó fázis feltétel nélkül meghívhatja.

A `--phases` mód csak kiírja a deklarált riport-fázisokat és kilép (exit 0) —
ebből tudja a 06-implement, hogy kell-e neki riportot generálnia.

ÚTVONAL-ALAKOK (TR5/c) — ugyanannak a kör-/fázis-mappának három alakja van a
rendszerben, és a leggyakoribb hiba a bázisok összekeverése (a másik alak
beragasztása egy harmadik bázisra rekurzív `test-report/test-report/…` és
`test-report/specs/…` fákat hoz létre). A kapu ezért **mind a hármat elfogadja**
a `--report-subdir`-ben, és normalizál:

  specs/cycle-NN-<name>/test-report/validate/round-02   (repó-gyökér bázis)
  test-report/validate/round-02                         (ciklus-mappa bázis)
  validate/round-02                                     (test-report bázis)

LAYOUT-ŐR (TR5/c) — a kapu ellenőrzi a ciklus `test-report/` mappájának felső
szintjét is: ott csak `implement/`, `validate/`, (legacy) `review/` mappa lehet,
a `validate/` alatt pedig csak `round-NN/`. Bármi más útvonal-hiba (elrontott
bázis), nem megőrzendő bizonyíték → exit 1, a mappa nevéből következtetett okkal.

Kilépő kód: 0 = minden deklarált artefaktum megvan (vagy a kapu kihagyva)
            1 = hiányzó vagy üres artefaktum, vagy idegen mappa a
                `test-report/` alatt → a validálás NEM zárható PASS-ra
            2 = használati hiba (nem létező conventions.md / ciklusmappa,
                vagy hiányzó `## Teszt-riportolás` szekció)
"""
import argparse
import re
import sys
from pathlib import Path

from lang_keys import fld, sec

_SEC_REPORTING = sec("cv_test_reporting")
_F_REQUIRED = fld("f_report_required")
_F_PATH_BASE = fld("f_artifact_path_base")
_F_PHASES = fld("f_report_phases")

SECTION_RE = re.compile(r"^##\s+" + re.escape(_SEC_REPORTING) + r"\s*$", re.IGNORECASE)
NEXT_SECTION_RE = re.compile(r"^##\s+")
REQUIRED_FLAG_RE = re.compile(r"\*\*" + re.escape(_F_REQUIRED) + r":\*\*\s*(\w+)",
                              re.IGNORECASE)
SEPARATOR_ROW_RE = re.compile(r"^\|[\s:|-]+\|$")
PATH_BASE_RE = re.compile(r"\*\*" + re.escape(_F_PATH_BASE) + r":\*\*\s*([\w-]+)",
                          re.IGNORECASE)
BASE_ROUND = {"kör-mappa", "kor-mappa", "körmappa", "round", "kör",
              "round-folder", "roundfolder"}
BASE_FLAT = {"test-report", "testreport", "flat", "gyökér", "gyoker"}
EMPTY_VALUES = {"", "-", "–", "—", "n/a", "na", "nincs", "none"}
PHASES_RE = re.compile(r"\*\*" + re.escape(_F_PHASES) + r":\*\*\s*(.+)")
DEFAULT_PHASES = ("validate",)
KNOWN_PHASES = {"implement", "validate"}

# TR5/c — a `test-report/` felső szintjén megengedett mappák, és a `validate/`
# alatt megengedett mappanév. A `review/` legacy: régi ciklusok 09-review köre.
ALLOWED_ROOT_DIRS = {"implement", "validate", "review"}
ROUND_DIR_RE = re.compile(r"^round-\d{2,}$")


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


def parse_phases(section_lines):
    """A deklarált riport-fázisok (TR6). Hiányzó mező → alapérték: `validate`."""
    m = PHASES_RE.search("\n".join(section_lines))
    if not m:
        return list(DEFAULT_PHASES), False
    raw = m.group(1).strip().strip("`")
    parts = [w.strip().strip("`").lower() for w in re.split(r"[,;/ ]+", raw) if w.strip()]
    return [w for w in parts if w in KNOWN_PHASES], True


def normalize_subdir(raw, cycle):
    """A kör-/fázis-mappa háromféle alakját EGY ciklus-relatív alakra hozza (TR5/c).

    Elfogadja a repó-gyökérhez relatív teljes útvonalat, a ciklus-mappához
    relatív `test-report/...` alakot és a puszta fázis-mappát (`validate/round-02`,
    `implement`). Visszaadja: (normalizált, eredeti-volt-e már jó)."""
    parts = [x for x in str(raw).replace("\\", "/").strip("/").split("/") if x and x != "."]
    if cycle.name in parts:                      # repó-gyökér bázis
        parts = parts[parts.index(cycle.name) + 1:]
    if not parts:
        parts = ["test-report"]
    if parts[0] != "test-report":                # test-report bázis (fázis-mappa)
        parts = ["test-report"] + parts
    norm = "/".join(parts)
    return norm, norm == str(raw).replace("\\", "/").strip("/")


def phase_of(report_subdir):
    """A normalizált ciklus-relatív útvonalból a fázis neve (`implement`/`validate`)."""
    parts = report_subdir.split("/")
    return parts[1] if len(parts) > 1 else None


def check_layout(cycle):
    """Idegen mappák a `test-report/` alatt (TR5/c) → [(útvonal, ok), ...].

    Egy idegen mappa sosem elfelejtett bizonyíték, hanem elrontott útvonal-bázis:
    a `test-report/` és a `specs/` nevű gyerek pont a másik két alak beragasztása."""
    root = cycle / "test-report"
    problems = []
    if not root.is_dir():
        return problems
    for entry in sorted(root.iterdir()):
        if entry.is_dir() and entry.name not in ALLOWED_ROOT_DIRS:
            problems.append((entry, _layout_reason(entry.name)))
    vdir = root / "validate"
    if vdir.is_dir():
        for entry in sorted(vdir.iterdir()):
            if entry.is_dir() and not ROUND_DIR_RE.match(entry.name):
                problems.append((entry, _layout_reason(entry.name)))
    return problems


def _layout_reason(name):
    if name == "test-report":
        return ("dupla prefix — a ciklus-mappa bázisú alak (`test-report/validate/round-NN`) "
                "került egy `test-report/` bázist váró paraméterbe")
    if name == "specs":
        return ("dupla prefix — a repó-gyökér bázisú teljes útvonal "
                "(`specs/cycle-NN-<name>/test-report/…`) került egy `test-report/` bázist "
                "váró paraméterbe")
    return "nem ismert fázis-mappa"


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
                             "— csak régi, körönkénti bontás előtti ciklusokhoz. "
                             "Mind a három útvonal-alak elfogadott (TR5/c), a kapu "
                             "normalizál")
    parser.add_argument("--phases", action="store_true",
                        help="csak a deklarált riport-fázisokat írja ki (TR6) és kilép")
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
        print(f"HIBA: a {conv} nem tartalmaz `## {_SEC_REPORTING}` szekciót. "
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
            f"HIBA (TR5/b migrációs őr): a `## {_SEC_REPORTING}` szekcióból hiányzik az\n"
            f"  **{_F_PATH_BASE}:** mező.\n\n"
            "Az utolsó oszlop jelentése 2026-08-07-én megváltozott (test-report/ gyökér →\n"
            "kör-mappa), a formátum viszont nem — ezért a kapu nem találgat. Írd be a\n"
            f"`{conv}` `## {_SEC_REPORTING}` szekciójába a **{_F_REQUIRED}:**\n"
            "mező mellé az alábbiak közül a helyeset:\n\n"
            f"  **{_F_PATH_BASE}:** kör-mappa     (mai séma: test-report/validate/round-NN/)\n"
            f"  **{_F_PATH_BASE}:** test-report    (régi, flat séma)\n\n"
            "Ha a ciklus most tér át a mai sémára, a `conventions.md` frissítése a ciklus\n"
            "része (kell rá task) — lásd a 03-write-plan „Kapu-konfiguráció együtt mozog\" szabályát.",
            file=sys.stderr,
        )
        return 2
    phases, phases_declared = parse_phases(section)
    if args.phases:
        print(" ".join(phases) if phases else "(nincs riport-fázis)")
        if not phases_declared:
            print(f"MEGJEGYZÉS: a conventions.md nem deklarál `**{_F_PHASES}:**` mezőt "
                  f"(TR6) — alapérték: {' '.join(DEFAULT_PHASES)}.")
        return 0

    subdir, unchanged = normalize_subdir(args.report_subdir, cycle)
    if not unchanged:
        print(f"MEGJEGYZÉS (TR5/c): a --report-subdir értéke `{args.report_subdir}` volt, "
              f"a kapu ciklus-relatív alakra normalizálta: `{subdir}`.")
    args.report_subdir = subdir

    if base_value in BASE_FLAT:
        args.report_subdir = "test-report"
        print("MEGJEGYZÉS: a conventions.md a RÉGI, flat sémát deklarálja "
              f"(`{_F_PATH_BASE}: test-report`) — a kapu a ciklus "
              "`test-report/` mappájához oldja fel az útvonalakat, a --report-subdir "
              "értékét figyelmen kívül hagyja.")
    elif base_value not in BASE_ROUND:
        print(f"HIBA: ismeretlen `{_F_PATH_BASE}:` érték: `{base_value}`. "
              f"Elfogadott: `kör-mappa` vagy `test-report`.", file=sys.stderr)
        return 2

    phase = phase_of(args.report_subdir)
    if base_value in BASE_ROUND and phase and phase not in phases:
        print(f"A kapu kihagyva: a `{phase}` nem riport-fázis ebben a projektben "
              f"(`**{_F_PHASES}:** {' '.join(phases) or '—'}`, TR6). "
              f"Az artefaktum-készletet nem ez a fázis állítja elő.")
        return 0

    rows = parse_rows(section)
    if not rows:
        print(f"HIBA: a `## {_SEC_REPORTING}` szekcióban nincs kitöltött táblázat. "
              f"Vagy deklarálj artefaktumokat, vagy írd be explicit: "
              f"`**{_F_REQUIRED}:** nem` + indoklás.", file=sys.stderr)
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
              f"`**{_F_REQUIRED}:**` mezőt `nem`-re, indoklással.", file=sys.stderr)
        return 2

    layout = check_layout(cycle) if base_value in BASE_ROUND else []
    if layout:
        print("\nIDEGEN MAPPA a test-report/ alatt (TR5/c) — útvonal-hiba, "
              "NEM megőrzendő bizonyíték:")
        for path, reason in layout:
            print(f"  ✗ {path}  ← {reason}")
        print("Töröld a fát, és ismételd meg a futtatást a helyes bázissal. "
              "A takarítási tilalom csak a `validate/round-NN/` mappákra vonatkozik.")

    if failures:
        print("\nKAPU BUKOTT — hiányzó teszt-riport(ok):")
        for kategoria, eszkoz, artefakt in failures:
            print(f"  ✗ {kategoria} ({eszkoz}) → {artefakt}")
        print("A validálás NEM zárható PASS-ra. Futtasd a conventions.md "
              f"`## {_SEC_REPORTING}` táblájában megadott riport-generáló parancsot, "
              f"és másold az artefaktumot ebbe a kör-mappába: {report_dir}")
        return 1
    if layout:
        return 1

    print(f"\nKAPU OK — mind a {checked} deklarált riport-artefaktum megvan, "
          "és a test-report/ layoutja tiszta.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
