#!/usr/bin/env python3
"""LD5 kapu — determinisztikus, LLM-ítélet nélküli ellenőrzések a
`docs-generated/test-description.md` teszt-leltárra (08-doc-sync fázis).

Miért kell: a `specs/test-conventions.md` (TC1–TC11) **promóció-alapú** — csak
az kerül bele, amit a felhasználó jóváhagy —, és arra válaszol, hogy „hogyan
futtatom". A `plan.md` `TS-NN` blokkjai és a `manual-test-plan.md` `TG-NN`
csoportjai **per-ciklus** élnek. Következmény: nincs egyetlen hely, ahol egy friss
kontextusú ágens vagy egy új kolléga végig tudja olvasni, MILYEN tesztek vannak
és MIT bizonyítanak. A teszt-leltár ez a hely, és mivel egy leltár értéke a
TELJESSÉGE, prompt-szintű ígéret helyett kemény kapu védi (D5).

A leltár hatóköre a `conventions.md` `## <Teszt-futtatás>` szekciójának
`### Tesztfájl-helyek` tábláját követi — ez az EGYETLEN szabályozott kiskapu:
`TL-EXEMPT` felmentő lista NINCS. Amit a projekt ott glob-bal deklarál, arra a
kapu leltár-tételt követel; amit nem deklarál, azt nem is keresi.

A hét check:

  1. Felderítés ↔ leltár halmaz-egyezés (LD5/1) — a deklarált globokkal
     összeszedett minden tesztfájlhoz tartozik legalább egy `TL-NNN` tétel, és
     minden nem-`retired` tétel `Futtató parancs`-a létező fájlra mutat.
  2. Hézagmentes, egyedi `TL-NNN` (LD5/2, a TS6 mintája) — a sorszám globális,
     soha nem újrahasznosított és soha nem átírt (D4), tehát a hézag azt jelenti,
     hogy egy tétel eltűnt a fájlból (`retired` jelölés helyett).
  3. Kötelező mezők (LD5/3, LD2) — a tétel adatlapja hiánytalan.
  4. Kategória-érvényesség (LD5/4, D6) — a tétel kategória-szekciója a
     `conventions.md` kategória-szótárából van.
  5. Környezet-érték (LD5/5, EV8) — pontosan `local` vagy `remote`: ez a
     `test-runs/<kategória>/<időbélyeg>/<env>/` útvonal-szegmensre joinol, ezért
     NYELVFÜGGETLEN literál.
  6. Kétirányú `R-NN` join (LD5/6, LD6) — ha egy tétel receptre hivatkozik, a
     `test-conventions.md` recept-adatlapja visszahivatkozik a `TL-NNN`-re. Ez a
     D3 átfedés mitigációja: a két artefaktum ugyanazt a tesztet EMLÍTHETI, de
     egyetlen mezőt sem duplikál, és a hivatkozás mindkét irányban látszik.
  7. Elavult cél-host (LD5/7, LD7) — **WARN**, nem bukás: a tétel parancsában
     olyan host áll, amit a projekt a `conventions.md`-ben már nem deklarál. Ez a
     D2 (konkrét parancs a katalógusban) mitigációja — egy port- vagy host-váltás
     különben CSENDBEN hagy elavultat.

FAIL (blokkoló) vs WARN (informatív): a script csak ott ad FAIL-t, ahol a jel
egyértelmű. Bizonytalan esetben WARN — egy hamis blokkolás rosszabb, mint egy
emberi ránézés.

Kilépő kód: 0 = minden kemény check PASS (WARN megengedett),
            1 = legalább egy FAIL (tételes hiánylistával),
            2 = használati hiba.
A nem létező `test-description.md` **FAIL**, nem „kihagyva": a `docs-generated/`
mappa létezése azt jelenti, hogy a 08 már lefutott, a leltár pedig a mappa
kötelező fájlja (LD8). Ha maga a `docs-generated/` sem létezik, a script
`0`-val, „kihagyva" jelzéssel tér vissza — a bootstrap még nem futott le.
"""
import argparse
import re
import sys
from pathlib import Path

from lang_keys import fld, sec, st

# ── Szerkezet-felismerés ──────────────────────────────────────────────────────
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
ITEM_HEADING_RE = re.compile(r"^###\s+(TL-\d{3})\b\s*(?:[—–-]\s*(.*))?$")
FIELD_RE = re.compile(r"^\s*[-*]?\s*\*\*(?P<name>[^:*]+?)\s*:?\s*\*\*\s*:?\s*(?P<value>.*)$")
TABLE_ROW_RE = re.compile(r"^\s*\|(?P<cells>.+)\|\s*$")
SEPARATOR_ROW_RE = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
RECIPE_HEADING_RE = re.compile(r"^###\s*(R\d+)\b")
RECIPE_REF_RE = re.compile(r"\bR\d+\b")
TL_REF_RE = re.compile(r"\bTL-\d{3}\b")

# A `local`/`remote` NYELVFÜGGETLEN (EV8, `<env>` útvonal-szegmens) — a
# projekt-nyelvi „lokális" alakot tudatosan NEM fogadjuk el: a `test-runs/`
# útvonal két néven hasadna szét.
ENV_VALUES = ("local", "remote")

EMPTY = ("", "-", "–", "—", "n/a", "na", "nincs", "none", "tbd", "?")

# A parancsban / lépésekben szereplő ÚTVONAL-jelöltek. A `::`-t előbb levágjuk
# (`pytest test/unit/test_a.py::test_b`), a `#`-et is (`file.ts#L3`).
PATH_TOKEN_RE = re.compile(r"[\w@.\-/]*[\w\-]/[\w@.\-/]*|[\w@.\-]+\.[A-Za-z][\w]{0,5}")
HOST_RE = re.compile(r"https?://([A-Za-z0-9._\-]+(?::\d+)?)")
LOCAL_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "[::1]", "::1"}
CODE_FENCE_RE = re.compile(r"^\s*`{3,}")


def is_empty(value):
    return (value or "").strip().strip("`*_").lower() in EMPTY


def strip_cell(cell):
    return cell.strip().strip("`").strip("*_").strip()


def in_fence(lines):
    """Sorindex → benne van-e kódblokkban (a fence-sorok maguk NEM)."""
    flags, inside = [], False
    for line in lines:
        if CODE_FENCE_RE.match(line):
            flags.append(False)
            inside = not inside
            continue
        flags.append(inside)
    return flags


def section_body(text, title_substr, levels=(2, 3, 4)):
    """Egy címsor törzse a következő, azonos vagy magasabb szintű címsorig."""
    lines = text.splitlines()
    start = level = None
    for i, line in enumerate(lines):
        m = HEADING_RE.match(line)
        if not m:
            continue
        if start is None:
            if len(m.group(1)) in levels and title_substr in m.group(2):
                start, level = i + 1, len(m.group(1))
            continue
        if len(m.group(1)) <= level:
            return "\n".join(lines[start:i])
    return "" if start is None else "\n".join(lines[start:])


def tables(text):
    """A szöveg markdown tábláinak listája: (fejléc-cellák, [adatsorok])."""
    out, header, rows, prev = [], None, [], None
    for line in text.splitlines():
        m = TABLE_ROW_RE.match(line)
        if not m:
            if header is not None:
                out.append((header, rows))
            header, rows, prev = None, [], None
            continue
        if SEPARATOR_ROW_RE.match(line):
            if prev is not None:
                header, rows = [strip_cell(c).lower() for c in prev.split("|")], []
            prev = None
            continue
        if header is None:
            prev = m.group("cells")
            continue
        rows.append([strip_cell(c) for c in m.group("cells").split("|")])
    if header is not None:
        out.append((header, rows))
    return out


# ── A `conventions.md` oldala (KT1) ───────────────────────────────────────────
CATEGORY_SPLIT_RE = re.compile(r"[,;/]+")


def declared_categories(conventions_text):
    """A `Teszt-kategóriák` szótár (KT1). `None` = a mező nincs meg."""
    body = section_body(conventions_text, sec("cv_test_execution"))
    if not body:
        return None
    m = re.search(r"^\s*\**\s*" + re.escape(fld("f_test_categories")) +
                  r"\s*:?\s*\**\s*:?\s*(.*)$", body, re.MULTILINE)
    if not m:
        return None
    return [c for c in (x.strip().strip("`*_") for x in CATEGORY_SPLIT_RE.split(m.group(1)))
            if c and not is_empty(c)]


def declared_globs(conventions_text):
    """A `### Tesztfájl-helyek` tábla: kategória → [glob].

    A táblát a `Glob` fejléc-cella azonosítja — az a szó mindkét prompt-nyelven
    ugyanaz, tehát a felismerés nyelvfüggetlen, és nem téveszthető össze a
    9 oszlopos futtatási táblával."""
    out = {}
    body = section_body(conventions_text, sec("cv_test_execution"))
    for header, rows in tables(body):
        if "glob" not in header:
            continue
        gi = header.index("glob")
        for cells in rows:
            if len(cells) <= gi:
                continue
            cat = cells[0]
            glob = cells[gi]
            if not cat or is_empty(cat) or cat.startswith("<"):
                continue
            if is_empty(glob) or glob.startswith("<"):
                out.setdefault(cat, [])
                continue
            out.setdefault(cat, []).append(glob)
    return out


def declared_hosts(conventions_text):
    """A `conventions.md`-ben bárhol deklarált nem-lokális hostok (LD7)."""
    hosts = set()
    for m in HOST_RE.finditer(conventions_text):
        host = m.group(1)
        if host.split(":")[0] not in LOCAL_HOSTS:
            hosts.add(host.split(":")[0])
    return hosts


def discover(globs, project_root):
    """A deklarált globokkal felderített tesztfájlok (repo-relatív posix)."""
    found = {}
    for cat, patterns in globs.items():
        hits = set()
        for pattern in patterns:
            pattern = pattern.strip().lstrip("./")
            if not pattern:
                continue
            # A `**` a pathlib.glob-ban is működik; a nem-glob alak fájlként vagy
            # mappa-prefixként is értelmes (`test/unit/` → minden alatta).
            try:
                if any(ch in pattern for ch in "*?["):
                    for p in project_root.glob(pattern):
                        if p.is_file():
                            hits.add(p.relative_to(project_root).as_posix())
                else:
                    p = project_root / pattern
                    if p.is_file():
                        hits.add(p.relative_to(project_root).as_posix())
                    elif p.is_dir():
                        for q in p.rglob("*"):
                            if q.is_file():
                                hits.add(q.relative_to(project_root).as_posix())
            except (OSError, ValueError, IndexError):
                continue
        found[cat] = hits
    return found


# ── A leltár oldala (LD1/LD2) ─────────────────────────────────────────────────
def parse_inventory(text):
    """A leltár tételei: [{id, title, category, fields, line, retired, body}]."""
    lines = text.splitlines()
    fenced = in_fence(lines)
    items, category, current = [], None, None
    for i, line in enumerate(lines):
        if fenced[i]:
            if current is not None:
                current["body"].append(line)
            continue
        h = HEADING_RE.match(line)
        if h and len(h.group(1)) == 2:
            category = h.group(2).strip().strip("`*_")
            current = None
            continue
        m = ITEM_HEADING_RE.match(line)
        if m:
            current = {"id": m.group(1), "title": (m.group(2) or "").strip(),
                       "category": category, "fields": {}, "line": i + 1,
                       "body": [], "steps": []}
            items.append(current)
            continue
        if current is None:
            continue
        current["body"].append(line)
        f = FIELD_RE.match(line)
        if f:
            name = f.group("name").strip().strip("`*_")
            current["fields"].setdefault(name, f.group("value").strip())
            current["_last_field"] = name
            continue
        if re.match(r"^\s+\d+\.\s+\S", line) and current.get("_last_field") == fld("f_steps"):
            current["steps"].append(line.strip())
    for it in items:
        it.pop("_last_field", None)
        blob = "\n".join(it["body"])
        it["retired"] = bool(re.search(r"\b" + re.escape(st("retired")) + r"\b", blob)
                             or re.search(r"\bretired\b", blob, re.IGNORECASE))
        it["blob"] = blob
    return items


def item_paths(item, project_root):
    """A tétel `Futtató parancs`-ában (és lépéseiben) szereplő LÉTEZŐ fájlok."""
    haystack = " ".join([item["fields"].get(fld("f_run_command"), "")] + item["steps"])
    existing, candidates = set(), set()
    for raw in PATH_TOKEN_RE.findall(haystack):
        token = raw.split("::")[0].split("#")[0].strip("`\"'").rstrip("/,;)")
        token = token.lstrip("./")
        if not token or token.startswith("-") or "/" not in token and "." not in token:
            continue
        candidates.add(token)
        p = project_root / token
        if p.is_file():
            existing.add(p.relative_to(project_root).as_posix())
    return existing, candidates


def item_hosts(item):
    haystack = " ".join([item["fields"].get(fld("f_run_command"), "")] + item["steps"]
                        + [item["fields"].get(fld("f_expected_result"), "")])
    return {m.group(1).split(":")[0] for m in HOST_RE.finditer(haystack)} - LOCAL_HOSTS


# ── A `test-conventions.md` oldala (LD6) ──────────────────────────────────────
def recipe_backrefs(tc_text):
    """`R-NN` → a recept-adatlapján megnevezett `TL-NNN` azonosítók.

    Egy recept-blokk a `### R-NN` címsornál kezdődik, és a következő `###` vagy
    magasabb szintű címsornál véget ér — a blokkon belüli minden `TL-NNN`
    hivatkozás a recept VISSZA-hivatkozása (LD6)."""
    out, current = {}, None
    for line in tc_text.splitlines():
        m = RECIPE_HEADING_RE.match(line)
        if m:
            current = m.group(1)
            out.setdefault(current, set())
            continue
        h = HEADING_RE.match(line)
        if h and len(h.group(1)) <= 3:
            current = None
            continue
        if current:
            out[current].update(TL_REF_RE.findall(line))
    return out


MANDATORY_FIELDS = ("f_environment", "f_goal", "f_steps", "f_expected_result",
                    "f_run_command", "f_recipe", "f_last_run", "f_source_cycle")
RETIRED_MANDATORY_FIELDS = ("f_source_cycle",)


def field_present(item, key):
    """A mező KI VAN-e töltve. Három szabály, mert a három mező máshogy áll:

    · `f_steps` — a mezőnév után a számozott lépések KÖVETKEZŐ sorokban állnak,
      tehát az inline érték jogosan üres; a lépés-lista a valódi tartalom.
    · `f_recipe` — a `—` LEGITIM érték (nincs recept, LD2), nem hiány; csak a
      mező teljes hiánya baj.
    · minden más — nem lehet üres és nem lehet `—`."""
    name = fld(key)
    raw = item["fields"].get(name)
    if key == "f_steps":
        return bool(item["steps"]) or (raw is not None and not is_empty(raw))
    if key == "f_recipe":
        return raw is not None and raw.strip() != ""
    return raw is not None and not is_empty(raw)


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
    parser.add_argument("test_description", nargs="?",
                        default="docs-generated/test-description.md",
                        help="a teszt-leltár útvonala (default: docs-generated/test-description.md)")
    parser.add_argument("--project-root", default=".", metavar="ÚTVONAL",
                        help="a felderítés gyökere (default: .)")
    parser.add_argument("--conventions", default="conventions.md", metavar="ÚTVONAL",
                        help="a kategória-szótár és a felderítési globok forrása "
                             "(default: conventions.md)")
    parser.add_argument("--test-conventions", default="specs/test-conventions.md",
                        metavar="ÚTVONAL",
                        help="a recept-regiszter a kétirányú R-NN joinhoz (LD6); ha nem "
                             "létezik, a 6. check kimarad (default: specs/test-conventions.md)")
    args = parser.parse_args()

    project_root = Path(args.project_root)
    if not project_root.is_dir():
        print(f"HIBA: nem létező projekt-gyökér: {project_root}", file=sys.stderr)
        return 2
    td_path = Path(args.test_description)
    conv_path = Path(args.conventions)

    print("## LD5 kapu — teszt-leltár ellenőrzés\n")

    if not conv_path.is_file():
        print(f"HIBA: nincs `{conv_path}` — a kategória-szótár és a felderítési globok "
              f"forrása a `00-init-project` kötelező szekciója (KT1). Enélkül a leltár "
              f"teljessége nem eldönthető, és a kapu NEM eshet vissza találgatásra.",
              file=sys.stderr)
        return 2
    conv_text = conv_path.read_text(encoding="utf-8")

    if not td_path.exists():
        if not td_path.parent.is_dir():
            print(f"- A `{td_path.parent}/` mappa nem létezik — **kihagyva** "
                  f"(a `08-doc-sync` bootstrapja még nem futott le).\n")
            print("## Összesített státusz: PASS (kihagyva)")
            return 0
        print(f"- **FAIL** — a `{td_path}` nem létezik, miközben a "
              f"`{td_path.parent}/` mappa igen. A teszt-leltár a mappa **kötelező** "
              f"fájlja (LD8): a bootstrapja független a `system-overview.md` ágától, "
              f"tehát akkor is le kell futnia, ha a mappa most születik.\n")
        print("## Összesített státusz: FAIL")
        return 1

    text = td_path.read_text(encoding="utf-8")
    items = parse_inventory(text)
    categories = declared_categories(conv_text)
    globs = declared_globs(conv_text)

    overall_pass = True
    warn_count = 0

    # ── 1. Felderítés ↔ leltár halmaz-egyezés ────────────────────────────────
    print("### 1. Felderítés ↔ leltár halmaz-egyezés (LD5/1)")
    if not globs:
        overall_pass = False
        print(f"- **FAIL** — a `{conv_path}` `## {sec('cv_test_execution')}` szekciójában "
              f"nincs `Glob` fejlécű tesztfájl-hely tábla (KT1). Ez a felderítés EGYETLEN "
              f"bemenete, és a leltár hatókörének egyetlen szabályozott szűkítője (D5) — "
              f"pótold a `00` fázis szekciójában.")
    else:
        found = discover(globs, project_root)
        all_found = set().union(*found.values()) if found else set()
        inventoried = set()
        broken = []
        for it in items:
            existing, candidates = item_paths(it, project_root)
            inventoried |= existing
            if it["retired"]:
                continue
            if not existing:
                broken.append((it["id"], it["line"], sorted(candidates)[:3]))
        missing = sorted(all_found - inventoried)
        for path in missing:
            overall_pass = False
            print(f"- **FAIL** `{path}` — felderített tesztfájl, amelyhez NINCS `TL-NNN` "
                  f"tétel. A leltár értéke a teljessége: ami nincs benne, arról a következő "
                  f"ciklus nem tudja, hogy létezik, és újra megírja (D5).")
        for tl, line, cands in broken:
            overall_pass = False
            hint = (" · a parancsban talált jelöltek: " + ", ".join(f"`{c}`" for c in cands)) if cands else ""
            print(f"- **FAIL** `{tl}` (sor {line}) — a `{fld('f_run_command')}` egyetlen "
                  f"LÉTEZŐ fájlra sem mutat{hint}. Ha a tesztet a ciklus kivezette, a tétel "
                  f"`{st('retired')}` jelölést kap (és a fájlban MARAD — audit-nyom, D4); "
                  f"ha átnevezték/áthelyezték, a parancsot kell javítani, a `TL` sorszámot NEM.")
        for cat, patterns in sorted(globs.items()):
            print(f"- `{cat}`: {len(found.get(cat, ()))} felderített fájl "
                  f"({', '.join(f'`{p}`' for p in patterns) or 'nincs deklarált glob'})")
        print(f"- Leltározott, létező tesztfájl: {len(inventoried)} · felderített: {len(all_found)}")
    print()

    # ── 2. Hézagmentes, egyedi TL-NNN ────────────────────────────────────────
    print("### 2. Hézagmentes, egyedi `TL-NNN` (LD5/2)")
    numbers = [int(it["id"].split("-")[1]) for it in items]
    dupes = sorted({n for n in numbers if numbers.count(n) > 1})
    for n in dupes:
        overall_pass = False
        print(f"- **FAIL** `TL-{n:03d}` — többször szerepel. A sorszám PROJEKT-szintű és "
              f"egyedi: a `test-runs/<kategória>/<időbélyeg>/<env>/TL-NNN/` eredmény-mappa "
              f"és a `TG-NN` / `R-NN` hivatkozások szó szerinti egyezésre joinolnak (D4).")
    if numbers:
        gaps = sorted(set(range(1, max(numbers) + 1)) - set(numbers))
        for n in gaps:
            overall_pass = False
            print(f"- **FAIL** `TL-{n:03d}` — hiányzik (hézag a sorszámozásban). A `TL-NNN` "
                  f"soha nem újrahasznosított és soha nem törölt: a kivezetett teszt tétele "
                  f"`{st('retired')}` jelölést kap, de a fájlban MARAD (D4). A hézag azt "
                  f"jelenti, hogy egy tétel eltűnt — pótold, vagy jelöld `{st('retired')}`-nek.")
        if not dupes and not gaps:
            print(f"- PASS — TL-001 … TL-{max(numbers):03d}, hézag és duplikátum nélkül "
                  f"({len(items)} tétel, ebből {sum(1 for i in items if i['retired'])} "
                  f"`{st('retired')}`).")
    else:
        overall_pass = False
        print(f"- **FAIL** — a leltárban egyetlen `### TL-NNN — <cím>` tétel sincs. Üres "
              f"vázat ne hagyj: bootstrapkor a felderítés adja a `TL-NNN` vázakat, a "
              f"leírásokat a felhasználóval kell kitölteni (LD8, TC3 — találgatni tilos).")
    print()

    # ── 3. Kötelező mezők ────────────────────────────────────────────────────
    print("### 3. Kötelező mezők (LD5/3, LD2)")
    bad_fields = 0
    for it in items:
        required = RETIRED_MANDATORY_FIELDS if it["retired"] else MANDATORY_FIELDS
        missing_f = [fld(k) for k in required if not field_present(it, k)]
        if missing_f:
            overall_pass = False
            bad_fields += 1
            print(f"- **FAIL** `{it['id']}` (sor {it['line']}) — hiányzó vagy üres mező: "
                  + ", ".join(f"`{n}`" for n in missing_f)
                  + (f" _(`{st('retired')}` tételnél csak a `{fld('f_source_cycle')}` "
                     f"kötelező)_" if it["retired"] else ""))
    if items and not bad_fields:
        print(f"- PASS — mind a {len(items)} tétel adatlapja hiánytalan.")
    print()

    # ── 4. Kategória-érvényesség ─────────────────────────────────────────────
    print("### 4. Kategória-érvényesség (LD5/4, D6)")
    if categories is None:
        warn_count += 1
        print(f"- WARN — a `{conv_path}` nem tartalmaz `{fld('f_test_categories')}` mezőt "
              f"(KT1) — a check kimarad. Pótlása a `00` fázis dolga.")
    else:
        lowered = {c.lower() for c in categories}
        bad_cat = 0
        for it in items:
            cat = (it["category"] or "").strip()
            if not cat or cat.lower() not in lowered:
                overall_pass = False
                bad_cat += 1
                print(f"- **FAIL** `{it['id']}` (sor {it['line']}) — a tétel "
                      f"`{cat or '(nincs kategória-szekció)'}` szekcióban áll, ami nincs a "
                      f"`conventions.md` szótárában ({', '.join(f'`{c}`' for c in categories)}). "
                      f"A kategória-azonosító útvonalra joinol "
                      f"(`test-runs/<kategória>/…`), ezért nem szabad szöveg.")
        if items and not bad_cat:
            print(f"- PASS — mind a {len(items)} tétel deklarált kategóriában áll "
                  f"({', '.join(f'`{c}`' for c in categories)}).")
    print()

    # ── 5. Környezet-érték ───────────────────────────────────────────────────
    print("### 5. Környezet-érték (LD5/5, EV8)")
    bad_env = 0
    for it in items:
        if it["retired"]:
            continue
        value = (it["fields"].get(fld("f_environment"), "") or "").strip().strip("`*_").lower()
        if value not in ENV_VALUES:
            overall_pass = False
            bad_env += 1
            print(f"- **FAIL** `{it['id']}` (sor {it['line']}) — a `{fld('f_environment')}` "
                  f"értéke `{value or '(üres)'}`, a két megengedett érték pedig `local` és "
                  f"`remote`. Ez NYELVFÜGGETLEN literál: a "
                  f"`test-runs/<kategória>/<időbélyeg>/<env>/` útvonal-szegmensre joinol, "
                  f"tehát a projekt-nyelvi alak („lokális\") két néven hasítaná szét a fát.")
    live = [i for i in items if not i["retired"]]
    if live and not bad_env:
        print(f"- PASS — mind a {len(live)} élő tétel `local` vagy `remote`.")
    print()

    # ── 6. Kétirányú R-NN join ───────────────────────────────────────────────
    print("### 6. Kétirányú `R-NN` join (LD5/6, LD6)")
    tc_path = Path(args.test_conventions)
    if not tc_path.is_file():
        warn_count += 1
        print(f"- WARN — nincs `{tc_path}` (TC6: korai ciklusban ez nem hiba) — a check "
              f"kimarad. Ilyenkor minden tétel `{fld('f_recipe')}` mezője `—` legyen.")
    else:
        backrefs = recipe_backrefs(tc_path.read_text(encoding="utf-8"))
        bad_join = 0
        for it in items:
            if it["retired"]:
                continue
            raw = it["fields"].get(fld("f_recipe"), "")
            refs = RECIPE_REF_RE.findall(raw or "")
            if not refs:
                continue
            for r in refs:
                if r not in backrefs:
                    overall_pass = False
                    bad_join += 1
                    print(f"- **FAIL** `{it['id']}` (sor {it['line']}) → `{r}` — a "
                          f"`{tc_path}`-ben nincs `### {r}` recept-adatlap. Lógó hivatkozás.")
                elif it["id"] not in backrefs[r]:
                    overall_pass = False
                    bad_join += 1
                    print(f"- **FAIL** `{it['id']}` ↔ `{r}` — a tétel hivatkozik a receptre, "
                          f"de a `{r}` adatlapja NEM hivatkozik vissza a `{it['id']}`-re. A "
                          f"join mindkét irányban kötelező (LD6): ez az a mitigáció, ami az "
                          f"átfedést LÁTHATÓVÁ teszi a `test-conventions.md` TC10/b "
                          f"blokkjával — mező-szintű tulajdon, de kétirányú hivatkozás (D3).")
        joined = sum(1 for i in items
                     if not i["retired"] and RECIPE_REF_RE.findall(i["fields"].get(fld("f_recipe"), "") or ""))
        if not bad_join:
            print(f"- PASS — {joined} recept-hivatkozás, mindegyik kétirányú.")
    print()

    # ── 7. Elavult cél-host (WARN) ───────────────────────────────────────────
    print("### 7. Elavult cél-host (LD5/7, LD7 — WARN)")
    known = declared_hosts(conv_text)
    stale = []
    for it in items:
        if it["retired"]:
            continue
        for host in sorted(item_hosts(it)):
            if host not in known:
                stale.append((it["id"], it["line"], host))
    for tl, line, host in stale:
        warn_count += 1
        print(f"- WARN `{tl}` (sor {line}) — a parancs a `{host}` hostra hív, amit a "
              f"`{conv_path}` már nem deklarál. A D2 vállalt kockázata ez: konkrét parancs a "
              f"katalógusban azt jelenti, hogy egy port- vagy host-váltás CSENDBEN hagy "
              f"elavultat. Vedd fel kérdésként a `doc-sync-questions.md`-be, és "
              f"vagy a tételt javítsd, vagy a `conventions.md` környezet-deklarációját.")
    if not stale:
        print(f"- PASS — minden cél-host szerepel a `{conv_path}` deklarációiban "
              f"({len(known)} host).")
    print()

    print(f"## Összesített státusz: {'PASS' if overall_pass else 'FAIL'}"
          f" ({warn_count} WARN — a WARN nem blokkol, de nézd át)")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
