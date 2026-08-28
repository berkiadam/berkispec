#!/usr/bin/env python3
"""MG kapu — a `manual-test-plan.md` determinisztikus minőségi kapuja
(`bs-manual-test-plan` segédparancs, MT5).

Miért kell: a kézi tesztterv értéke azon áll vagy bukik, hogy KONKRÉT
(placeholder-mentes) értékekkel áll benne minden indító parancs, tesztadat,
hívás és elvárt eredmény, és hogy a ciklus minden `DoD-NN` pontja vissza van
vezetve vagy egy tesztcsoportra, vagy egy „kézzel nem tesztelhető" indoklásra.
Ezek gépiesen eldönthetők — egy gyengébb modell hibamódjait (placeholder az
érték helyén, üres cella, lefedetlen DoD, hiányzó `.http` blokk) csak
determinisztikusan lehet elkapni, ezért nem a promptra bízzuk.

Amit ellenőriz:

  MG1  a fájl létezik, és a fejléc <field:f_status> mezője a két megengedett
       mód egyike                                                  → exit 2
  MG2  mind a hat kötelező szekció megvan
  MG3  placeholder- és üres-cella-tilalom az 1-4. szekcióban
  MG4  minden `### TG-NN` csoport teljes (mit tesztelünk / előfeltétel /
       lépés-tábla / minden lépésnek elvárt eredménye)
  MG5  kétirányú DoD-lefedettség (csoport-fejléc ↔ spec Definition of done,
       a „nem kézzel tesztelhető" tábla indoklással elfogadott)
  MG6  az 1. szekció minden komponens-sorában van indító parancs
  MG7  a 3. szekció lefedi a plan gépi futtatási táblájának parancsait;
       as-built módban a felsorolt eredmény-útvonalak léteznek a lemezen
  MG8  útvonal-formátum (RP1): nincs abszolút / gép-specifikus / `file://` alak
  MG9  ahol `curl` van a lépés-táblában, ott ```http blokk is van (és fordítva)
  MG10 a `TG-NN` azonosítók egyediek és hézagmentesek, és a lefedettségi tábla
       `DoD-NN → TG-NN` párjai megegyeznek a csoport-fejlécekkel

Kilépő kód: 0 = tiszta · 1 = legalább egy ✗ · 2 = használati/előfeltétel-hiba
            (nem létező ciklusmappa, hiányzó `manual-test-plan.md`, olvashatatlan
            vagy érvénytelen fejléc-státusz).

A script NYELVFÜGGETLEN: minden szekciónév, mezőnév és státusz-érték a
`lang_keys` (`sec()` / `fld()` / `st()`) hívásain keresztül, a telepített
`lang-keys.json`-ból jön.
"""
import argparse
import re
import sys
from pathlib import Path

from lang_keys import fld, sec, st

# ── átvett minták (MT13: MÁSOLÁS, nem refaktor) ───────────────────────────────
# Az alábbi minták és a `section_span` / `check_path_format` logika az
# `analyze-gate-check.py`-ból származik, SZÓ SZERINT. Nem közös modulba emelve,
# mert (a) az `analyze-gate-check.py` fájlnevében kötőjel van, tehát normál
# `import`-tal nem érhető el, (b) egy `gate_common.py` bevezetése az 1200+ soros
# 05-kapu átírását jelentené — aránytalan regressziós kockázat. Ha egy harmadik
# kapunak is kellene, akkor érdemes kiemelni, külön ciklusban.

# forrás: analyze-gate-check.py HEADING_RE / TABLE_ROW_RE / SEPARATOR_ROW_RE /
#         PLACEHOLDER_CELL_RE (543-546. sor)
HEADING_RE = re.compile(r"^(#{2,4})\s+(.*)$")
TABLE_ROW_RE = re.compile(r"^\s*\|(.+)\|\s*$")
SEPARATOR_ROW_RE = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
PLACEHOLDER_CELL_RE = re.compile(r"^\s*(_.*_|\.\.\.|—|-{1,3}|<.*>)\s*$")

# forrás: analyze-gate-check.py KO1_PLACEHOLDER_RE (814. sor) — az MG3 ugyanazt
# a hibát keresi, mint a C6: placeholder a konkrét érték helyén.
# nyelvfüggő ág — az analyze-gate-check.py C6-jával közös adósság: a magyar
# kulcsszavakra épülő ág angol projekt-nyelvnél gyengébben fog. SZÁNDÉKOSAN nem
# javítjuk itt: az egyoldalú „javítás" pont a két kapu eltéréséhez vezetne.
KO1_PLACEHOLDER_RE = re.compile(
    r"<[^>\n]*(?:ide\s+j|TODO|todo|kitölt|megadni|érték|url|URL|jelszó|password)[^>\n]*>"
    r"|(?<![\w-])(?:TODO|TBD|FIXME|XXX)(?![\w-])"
    r"|(?<![\w-])(?:pl\.\s*)?<\.\.\.>"
)

# forrás: analyze-gate-check.py FENCE_RE (907. sor)
FENCE_RE = re.compile(r"^\s*```([A-Za-z0-9_+-]*)\s*$")

# forrás: analyze-gate-check.py FILE_URI_RE … R1_MAX_PER_DOC (1032-1038. sor)
FILE_URI_RE = re.compile(r"file:///?[^\s`\)\]]+")
MACHINE_PATH_RE = re.compile(
    r"(?<![\w.])(?:/home/[\w.-]+|/Users/[\w.-]+|/mnt/[a-z]/[\w.-]+|[A-Za-z]:[\\/]{1,2}Users[\\/])[^\s`\)\]\|]*"
)
PLACEHOLDER_PATH_RE = re.compile(r"(?<![\w.])(?:/path/to/|<projekt>/|<project>/|/абс)[^\s`\)\]\|]*")
MD_ABS_LINK_RE = re.compile(r"\]\((/[^)\s]*|file://[^)\s]*|[A-Za-z]:[\\/][^)\s]*)\)")
ABS_REPO_PATH_RE = re.compile(r"(?<![\w.:/])/((?:[\w.-]+/)+[\w.-]+\.[A-Za-z0-9]{1,5})(?![\w/])")
R1_MAX_PER_DOC = 10

# forrás: analyze-gate-check.py DOD_RE / DOD_BULLET_RE (123-124. sor)
DOD_RE = re.compile(r"DoD-(\d+[a-z]?)")
DOD_BULLET_RE = re.compile(r"^\s*-\s*\[[ xX]\]\s*(.+)$")

# ── saját minták ──────────────────────────────────────────────────────────────
# A tesztcsoport-fejléc kötött formája: `### TG-NN — <név>  (DoD-NN, DoD-NN)`
TG_HEADING_RE = re.compile(r"^###\s+(TG-(\d+))\b(.*)$")
TG_TOKEN_RE = re.compile(r"\bTG-(\d+)\b")
# Az MG3 nyelvsemleges helyőrző-mintája. A generikus `<...>` alak KÉT esetben
# helyőrző (és nem pl. egy XML-tag a payloadban): ha a tartalma szóközt
# tartalmaz (`<a csoport neve>`), vagy ha CSUPA NAGYBETŰS/aláhúzásos
# (`<TOKEN>`, `<CYCLE_NAME>`). Egy `<user>` alakú XML-tag így nem bukik.
ANGLE_PLACEHOLDER_RE = re.compile(r"<[^<>\n]*\s[^<>\n]*>|<[A-Z][A-Z0-9_]*>")
WORD_PLACEHOLDER_RE = re.compile(r"(?<![\w-])(?:TODO|TBD|FIXME|XXX|xxx)(?![\w-])")
ELLIPSIS_CELL_RE = re.compile(r"^\s*(\.\.\.|…|`\.\.\.`|`…`)\s*$")
EMPTY_VALUES = {"", "-", "–", "—", "n/a", "na", "nincs", "none"}
MACHINE_TABLE_CMD_COL = 3  # forrás: run-tests.py parse_matrix — cells[3] = parancs


def _force_utf8_output():
    """Windows-kompatibilitás: a konzol örökölt kódlapja (cp852 / cp1250) nem
    tudja megjeleníteni a kimenet tipográfiai és ékezetes karaktereit (✓, →, ő),
    és a `print()` ilyenkor `UnicodeEncodeError`-t dobna. Forrás: ds22-gate-check.py."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


class Findings:
    """✗ gyűjtő. Az `add()` szignatúrája szándékosan azonos az
    `analyze-gate-check.py` gyűjtőjével, hogy az átvett `check_path_format`
    változtatás nélkül működjön (a `phase` argumentumot itt nem használjuk)."""

    def __init__(self):
        self.items = []

    def add(self, code, phase, msg):
        self.items.append((code, msg))

    def codes(self):
        return {code for code, _ in self.items}


# ── szekció- és táblakezelés ──────────────────────────────────────────────────
def section_span(lines, title_substr):
    """Egy címsor (`##`-`####`) törzsének (kezdő, végző) SORINDEXE; a törzs a
    következő, azonos vagy magasabb szintű címsorig tart. (None, None), ha a
    címsor nincs meg.

    forrás: analyze-gate-check.py section_body (564. sor) — ugyanaz a logika,
    csak sorindexet ad vissza, hogy a ✗ sorok fájl:sor bizonyítékot kaphassanak."""
    start = level = None
    for i, line in enumerate(lines):
        m = HEADING_RE.match(line)
        if not m:
            continue
        if start is None:
            if title_substr in m.group(2):
                start, level = i + 1, len(m.group(1))
            continue
        if len(m.group(1)) <= level:
            return start, i
    if start is None:
        return None, None
    return start, len(lines)


def section_lines(lines, title_substr):
    """A szekció törzsének [(sorszám, sor)] listája (1-alapú sorszám)."""
    start, end = section_span(lines, title_substr)
    if start is None:
        return []
    return [(i + 1, lines[i]) for i in range(start, end)]


def parse_tables(numbered_lines):
    """A megadott sorokban álló MINDEN markdown tábla:
    [(fejléc-cellák, [(sorszám, cellák)])].

    A fejlécsor átugrása állapotgéppel megy (`seen_separator`) — amíg a
    `|---|---|` elválasztó nem jött, a sorokat nem adatnak tekintjük. A
    sablon-/példasorokat (minden cellája placeholder vagy üres) kihagyja.
    forrás: analyze-gate-check.py table_rows / check_env_coordinates (C6)."""
    tables = []
    header, rows, prev, seen_sep = None, [], None, False

    def flush():
        nonlocal header, rows, prev, seen_sep
        if header is not None:
            tables.append((header, rows))
        header, rows, prev, seen_sep = None, [], None, False

    for lineno, line in numbered_lines:
        m = TABLE_ROW_RE.match(line)
        if not m:
            flush()
            continue
        cells = [c.strip() for c in m.group(1).split("|")]
        if SEPARATOR_ROW_RE.match(line):
            seen_sep = True
            header = prev if prev is not None else []
            continue
        if not seen_sep:
            prev = cells
            continue
        if cells and all(PLACEHOLDER_CELL_RE.match(c) or not c for c in cells):
            continue  # sablon-/példasor
        rows.append((lineno, cells))
    flush()
    return tables


def col_index(header, field_name):
    """Az oszlop indexe, amelynek fejléce tartalmazza a mezőnevet (kisbetűs
    részillesztés). None, ha nincs ilyen oszlop."""
    needle = field_name.lower()
    for i, cell in enumerate(header):
        if needle in cell.lower():
            return i
    return None


def header_field(lines, field_key):
    """A dokumentum fejléc-blokkjának `**<mezőnév>:** érték` sora — az érték."""
    pattern = re.compile(r"^\s*\**\s*" + re.escape(fld(field_key)) + r"\s*:\s*\**\s*(.*)$",
                         re.IGNORECASE)
    for line in lines:
        clean = line.replace("**", "").strip()
        m = pattern.match(clean)
        if m:
            return m.group(1).strip()
    return None


# ── MG3 ───────────────────────────────────────────────────────────────────────
def check_placeholders(lines, f):
    """MG3 — placeholder- és üres-cella-tilalom az 1-4. szekcióban.

    Két szemantikai csapda, amit az `analyze-gate-check.py` C6-jából PONTOSAN így
    kell átvenni, különben a két kapu mást mond ugyanarra a szövegre:
      1. A CSUPA-placeholder sor NEM hiba: az sablonsor (`continue`). Csak abban
         a sorban hiba az üres cella, amelyikben legalább egy valódi érték is áll.
         A `—` tehát LEGÁLIS „nem értelmezhető" jelölés, nem hiányzó adat.
      2. A fejlécsor átugrása állapotgéppel megy (`seen_separator`)."""
    for key in ("mt_environment", "mt_test_data", "mt_automated_tests", "mt_manual_groups"):
        body = section_lines(lines, sec(key))
        if not body:
            continue
        in_fence = False
        for lineno, line in body:
            if FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue  # a `.http` / `curl` blokk tartalma konkrét adat
            for rx in (KO1_PLACEHOLDER_RE, ANGLE_PLACEHOLDER_RE, WORD_PLACEHOLDER_RE):
                m = rx.search(line)
                if m:
                    f.add("MG3", "—", f"manual-test-plan.md:{lineno} placeholder áll konkrét "
                                      f"érték helyett: `{m.group(0)[:70]}` (szekció: {sec(key)}) — "
                                      f"a hiányzó adatot a plan.md-ből vagy a kódból kell feloldani, "
                                      f"ami erre a ciklusra nem értelmezhető, oda `—` kerül")
                    break
        for header, rows in parse_tables(body):
            for lineno, cells in rows:
                bad = [i for i, c in enumerate(cells)
                       if not c or ELLIPSIS_CELL_RE.match(c)]
                if bad:
                    name = cells[0] if cells and cells[0] else "(üres sor)"
                    label = header[bad[0]] if bad[0] < len(header) and header[bad[0]] else f"#{bad[0] + 1}"
                    f.add("MG3", "—", f"manual-test-plan.md:{lineno} a `{name}` sorában "
                                      f"{len(bad)} kitöltetlen cella van (első: `{label}`) — "
                                      f"üresen nem hagyható, `—`-t írj oda, ha nem értelmezhető")


# ── tesztcsoportok ────────────────────────────────────────────────────────────
def test_groups(lines):
    """A `### TG-NN` csoportok: [{id, num, dods, start, end}] (sorindexek)."""
    start, end = section_span(lines, sec("mt_manual_groups"))
    if start is None:
        return []
    groups = []
    for i in range(start, end):
        m = TG_HEADING_RE.match(lines[i])
        if m:
            groups.append({
                "id": m.group(1),
                "num": int(m.group(2)),
                "lineno": i + 1,
                "dods": [f"DoD-{d}" for d in DOD_RE.findall(m.group(3))],
                "start": i + 1,
                "end": end,
            })
    for a, b in zip(groups, groups[1:]):
        a["end"] = b["lineno"] - 1
    # A `Nem kézzel tesztelhető` alszekció a 4. szekció végén áll — az utolsó
    # csoport törzse ott véget ér, különben a tábláját a csoportjának hinnénk.
    nm_start, _ = section_span(lines, sec("mt_not_manual"))
    if groups and nm_start is not None and groups[-1]["lineno"] < nm_start <= groups[-1]["end"]:
        groups[-1]["end"] = nm_start - 1
    return groups


def group_lines(lines, group):
    return [(i + 1, lines[i]) for i in range(group["start"], group["end"])]


def check_groups(lines, f):
    """MG4 — minden csoport teljes; MG9 — `curl` ↔ ```http blokk szimmetria."""
    groups = test_groups(lines)
    if not groups:
        f.add("MG4", "—", f"a `{sec('mt_manual_groups')}` szekcióban nincs egyetlen "
                          f"`### TG-NN — <név>  (DoD-NN)` alakú tesztcsoport sem — "
                          f"a kézi tesztterv lényege ez a szekció")
        return groups

    for g in groups:
        body = group_lines(lines, g)
        text = "\n".join(line for _, line in body)
        missing = []
        for key in ("f_what_we_test", "f_prerequisite", "f_cleanup"):
            if not re.search(r"\*\*\s*" + re.escape(fld(key)) + r"\s*:", text, re.IGNORECASE):
                missing.append(f"`{fld(key)}`")
        if missing:
            f.add("MG4", "—", f"{g['id']} (manual-test-plan.md:{g['lineno']}): hiányzó sor: "
                              f"{', '.join(missing)}")

        step_table = None
        for header, rows in parse_tables(body):
            if col_index(header, fld("f_steps")) is not None or \
               col_index(header, fld("f_expected_result")) is not None:
                step_table = (header, rows)
                break
        if step_table is None:
            f.add("MG4", "—", f"{g['id']} (manual-test-plan.md:{g['lineno']}): nincs lépés-tábla "
                              f"(`{fld('f_steps')}` / `{fld('f_expected_result')}` oszlopokkal)")
            continue
        header, rows = step_table
        if not rows:
            f.add("MG4", "—", f"{g['id']} (manual-test-plan.md:{g['lineno']}): a lépés-tábla "
                              f"egyetlen adatsort sem tartalmaz")
        idx = col_index(header, fld("f_expected_result"))
        if idx is None:
            f.add("MG4", "—", f"{g['id']} (manual-test-plan.md:{g['lineno']}): a lépés-táblából "
                              f"hiányzik a `{fld('f_expected_result')}` oszlop")
        else:
            for lineno, cells in rows:
                value = cells[idx].strip() if idx < len(cells) else ""
                if not value or value.lower() in EMPTY_VALUES or ELLIPSIS_CELL_RE.match(value):
                    f.add("MG4", "—", f"{g['id']} (manual-test-plan.md:{lineno}): a lépés "
                                      f"`{fld('f_expected_result')}` cellája üres vagy jelöletlen — "
                                      f"konkrét státuszkód / mezőnév / képernyő-elem kell ide, "
                                      f"a „működik\" nem elfogadható")

        # MG9 — a két hívási alak együtt jár: a `curl` a terminálnak, a `.http`
        # blokk a VSCode REST Client / IntelliJ felületének. Az egyik nélkül a
        # terv fél közönségnek szól.
        has_curl = re.search(r"(?<![\w-])curl(?![\w-])", text) is not None
        has_http = any(FENCE_RE.match(line) and FENCE_RE.match(line).group(1).lower() == "http"
                       for _, line in body)
        if has_curl and not has_http:
            f.add("MG9", "—", f"{g['id']} (manual-test-plan.md:{g['lineno']}): van `curl` hívás, "
                              f"de nincs ```http blokk — a `.http` alak is kötelező (MT11)")
        if has_http and not has_curl:
            f.add("MG9", "—", f"{g['id']} (manual-test-plan.md:{g['lineno']}): van ```http blokk, "
                              f"de nincs `curl` hívás — a `curl` alak is kötelező (MT11)")
    return groups


def check_group_ids(lines, groups, f):
    """MG10 — a `TG-NN` azonosítók egyediek és hézagmentesek, és a lefedettségi
    tábla párjai megegyeznek a csoport-fejlécekkel."""
    nums = [g["num"] for g in groups]
    dupes = sorted({n for n in nums if nums.count(n) > 1})
    if dupes:
        f.add("MG10", "—", "duplikált tesztcsoport-azonosító: "
                           + ", ".join(f"TG-{n:02d}" for n in dupes))
    if nums:
        expected = list(range(1, len(nums) + 1))
        if sorted(nums) != expected:
            missing = [n for n in expected if n not in nums]
            f.add("MG10", "—", f"a `TG-NN` sorszámozás hézagos: {len(nums)} csoport van, "
                               f"de hiányzik: {', '.join(f'TG-{n:02d}' for n in missing)}")

    header_pairs = {(d, g["id"]) for g in groups for d in g["dods"]}
    table_pairs = set()
    for header, rows in parse_tables(section_lines(lines, sec("mt_coverage"))):
        for _, cells in rows:
            dods = [f"DoD-{d}" for d in DOD_RE.findall(cells[0] if cells else "")]
            tgs = [f"TG-{int(n):02d}" for n in TG_TOKEN_RE.findall(" ".join(cells[1:]))]
            for d in dods:
                for t in tgs:
                    table_pairs.add((d, t))
    if not table_pairs and header_pairs:
        f.add("MG10", "—", f"a `{sec('mt_coverage')}` tábla üres vagy hiányzik, miközben a "
                           f"csoport-fejlécek {len(header_pairs)} `DoD-NN → TG-NN` párt "
                           f"deklarálnak")
    else:
        for pair in sorted(header_pairs - table_pairs):
            f.add("MG10", "—", f"a `{pair[0]} → {pair[1]}` pár a csoport-fejlécben szerepel, "
                               f"de a `{sec('mt_coverage')}` táblában nem")
        for pair in sorted(table_pairs - header_pairs):
            f.add("MG10", "—", f"a `{pair[0]} → {pair[1]}` pár a `{sec('mt_coverage')}` táblában "
                               f"szerepel, de a `{pair[1]}` csoport fejlécében nem")


# ── MG5 ───────────────────────────────────────────────────────────────────────
def dod_ids(spec_text):
    """A spec `Definition of done` szekciójának `DoD-NN` azonosítói, sorrendben.
    forrás: analyze-gate-check.py dod_ids (668. sor) — szó szerint, hogy a két
    kapu ugyanazt a halmazt lássa."""
    out = []
    spec_lines = spec_text.splitlines()
    for _, line in section_lines(spec_lines, sec("definition_of_done")):
        m = DOD_BULLET_RE.match(line)
        if not m:
            continue
        found = DOD_RE.search(m.group(1))
        if found and found.group(1) not in out:
            out.append(found.group(1))
    return out


def not_manual_dods(lines, f):
    """A `Nem kézzel tesztelhető` tábla `DoD-NN`-jei — CSAK azok, amelyek mellett
    indoklás is áll (MT10: azonosító + egy mondat indoklás + mi fedi)."""
    accepted = set()
    for header, rows in parse_tables(section_lines(lines, sec("mt_not_manual"))):
        for lineno, cells in rows:
            dods = [f"DoD-{d}" for d in DOD_RE.findall(cells[0] if cells else "")]
            if not dods:
                continue
            reason = cells[1].strip() if len(cells) > 1 else ""
            if not reason or reason.lower() in EMPTY_VALUES or ELLIPSIS_CELL_RE.match(reason):
                f.add("MG5", "—", f"manual-test-plan.md:{lineno} a `{', '.join(dods)}` a "
                                  f"`{sec('mt_not_manual')}` táblában indoklás nélkül áll — "
                                  f"MT10: egy mondat indoklás kötelező, különben a DoD-pont "
                                  f"lefedetlen")
                continue
            accepted.update(dods)
    return accepted


def check_dod_coverage(lines, spec_text, groups, f):
    """MG5 — kétirányú DoD-lefedettség."""
    for g in groups:
        if not g["dods"]:
            f.add("MG5", "—", f"{g['id']} (manual-test-plan.md:{g['lineno']}): a fejléc egyetlen "
                              f"`DoD-NN`-t sem nevez meg — MT6: minden csoport visszavezet egy "
                              f"`DoD-NN`-re vagy egy spec-tesztesetre")
    covered = {d for g in groups for d in g["dods"]} | not_manual_dods(lines, f)
    if spec_text is None:
        return "nincs spec.md — a visszirány kimarad"
    ids = [f"DoD-{n}" for n in dod_ids(spec_text)]
    if not ids:
        return f"a spec.md `{sec('definition_of_done')}` szekciójában nincs `DoD-NN` — a visszirány kimarad"
    missing = [d for d in ids if d not in covered]
    for d in missing:
        f.add("MG5", "—", f"a spec.md `{d}` pontja lefedetlen: nem szerepel egyetlen "
                          f"tesztcsoport fejlécében sem, és a `{sec('mt_not_manual')}` táblában "
                          f"sincs indoklással")
    return f"{len(ids) - len(missing)}/{len(ids)} `DoD-NN` lefedve"


# ── MG6 / MG7 ─────────────────────────────────────────────────────────────────
def check_startup_commands(lines, f):
    """MG6 — az 1. szekció minden komponens-sorában van nem üres, nem placeholder
    indító parancs."""
    body = section_lines(lines, sec("mt_environment"))
    if not body:
        return "a szekció hiányzik (MG2)"
    checked = 0
    for header, rows in parse_tables(body):
        idx = col_index(header, fld("f_startup"))
        if idx is None:
            continue
        for lineno, cells in rows:
            checked += 1
            value = cells[idx].strip().strip("`").strip() if idx < len(cells) else ""
            name = cells[0] if cells and cells[0] else "(névtelen komponens)"
            if (not value or value.lower() in EMPTY_VALUES
                    or ELLIPSIS_CELL_RE.match(value)
                    or ANGLE_PLACEHOLDER_RE.search(value)
                    or KO1_PLACEHOLDER_RE.search(value)):
                f.add("MG6", "—", f"manual-test-plan.md:{lineno} a `{name}` komponens "
                                  f"`{fld('f_startup')}` cellájában nincs konkrét parancs "
                                  f"(`{value or 'üres'}`) — ez a terv első lépése, találgatni nem lehet")
    if not checked:
        f.add("MG6", "—", f"az 1. szekció táblájában nincs `{fld('f_startup')}` oszlop "
                          f"kitöltött komponens-sorral")
        return "nincs ellenőrizhető komponens-sor"
    return f"{checked} komponens-sor ellenőrizve"


def machine_commands(plan_text):
    """A plan gépi futtatási táblájának parancsai.
    forrás: run-tests.py parse_matrix — a 4. oszlop (index 3) a parancs."""
    if plan_text is None:
        return []
    out = []
    for header, rows in parse_tables(section_lines(plan_text.splitlines(), sec("machine_run_table"))):
        for _, cells in rows:
            if len(cells) <= MACHINE_TABLE_CMD_COL:
                continue
            cmd = cells[MACHINE_TABLE_CMD_COL].strip().strip("`").strip()
            if cmd and cmd.lower() not in EMPTY_VALUES and cmd not in out:
                out.append(cmd)
    return out


def normalize_cmd(value):
    return " ".join(value.replace("`", " ").split()).lower()


def check_automated_tests(lines, plan_text, mode, cycle_path, f):
    """MG7 — a 3. szekció HALMAZKÉNT lefedi a plan gépi futtatási táblájának
    parancsait; as-built módban a felsorolt eredmény-útvonalak léteznek."""
    body = section_lines(lines, sec("mt_automated_tests"))
    if not body:
        return "a szekció hiányzik (MG2)"
    haystack = normalize_cmd("\n".join(line for _, line in body))
    commands = machine_commands(plan_text)
    for cmd in commands:
        if normalize_cmd(cmd) not in haystack:
            f.add("MG7", "—", f"a plan.md `{sec('machine_run_table')}` táblájának `{cmd}` "
                              f"parancsa nem szerepel a `{sec('mt_automated_tests')}` "
                              f"szekcióban — a kézi tesztelő így nem tudja, mit futtat a gép")

    note = f"{len(commands)} gépi parancs egyeztetve"
    if mode != st("mtp_as_built").lower():
        return note + " (a `planned` mód nem ellenőrzi az eredmény-útvonalakat)"

    results_line = None
    marker = re.compile(r"^\s*[-*]?\s*\**\s*`?" + re.escape(fld("f_test_results_so_far"))
                        + r"`?\s*\**\s*:\s*(.*)$", re.IGNORECASE)
    for lineno, line in body:
        m = marker.match(line.replace("**", ""))
        if m:
            results_line = (lineno, m.group(1))
            break
    if results_line is None:
        f.add("MG7", "—", f"a `{sec('mt_automated_tests')}` szekcióból hiányzik a "
                          f"`{fld('f_test_results_so_far')}:` sor — as-built módban itt kell "
                          f"állnia a ténylegesen létező eredmény-fájlok listájának")
        return note
    lineno, value = results_line
    paths = re.findall(r"`([^`\n]+)`", value)
    checked = 0
    for raw in paths:
        candidate = raw.strip().rstrip("/")
        if "/" not in candidate and "." not in candidate:
            continue  # nem útvonal (pl. egy megjegyzés backtickben)
        checked += 1
        if not (cycle_path / candidate).exists() and not (Path(".") / candidate).exists():
            f.add("MG7", "—", f"manual-test-plan.md:{lineno} a felsorolt eredmény-útvonal nem "
                              f"létezik: `{candidate}` — as-built módban CSAK azt sorold fel, "
                              f"ami tényleg ott van")
    return note + f" · {checked} eredmény-útvonal ellenőrizve"


# ── MG8 ───────────────────────────────────────────────────────────────────────
def check_path_format(docs, repo_root, f):
    """MG8 = R1 (RP1) — abszolút / gép-specifikus / `file://` útvonal.

    forrás: analyze-gate-check.py check_path_format (1042. sor) — SZÓ SZERINT.
    A `file://`, a gép-specifikus és a placeholder alak mindenhol hiba
    (kódblokkban is); a „gyökér-abszolút repó-útvonal" alakot viszont csak
    kódblokkon KÍVÜL jelezzük, mert egy parancsban a konténer-belső
    `/opt/app/...` útvonal jogos lehet."""
    for doc, text, phase in docs:
        hits, in_fence = 0, False
        for lineno, line in enumerate(text.splitlines(), start=1):
            if FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            found = []
            for m in FILE_URI_RE.finditer(line):
                found.append((m.group(0)[:70], "`file://` sémájú link"))
            for m in MACHINE_PATH_RE.finditer(line):
                found.append((m.group(0)[:70], "gép-specifikus abszolút útvonal"))
            for m in PLACEHOLDER_PATH_RE.finditer(line):
                found.append((m.group(0)[:70], "placeholder útvonal"))
            if not in_fence:
                for m in MD_ABS_LINK_RE.finditer(line):
                    found.append((m.group(1)[:70], "abszolút markdown-link"))
                for m in ABS_REPO_PATH_RE.finditer(line):
                    if (repo_root / m.group(1)).is_file():
                        found.append((m.group(0)[:70], f"abszolút repó-útvonal (helyesen: `{m.group(1)}`)"))
            if found:
                value, why = found[0]
                extra = f" (+{len(found) - 1} további illeszkedő minta ugyanezen a soron)" if len(found) > 1 else ""
                hits += 1
                if hits <= R1_MAX_PER_DOC:
                    f.add("MG8", phase, f"{doc}:{lineno} {why}: `{value}`{extra} — a kód-/fájl-"
                                        f"hivatkozás a repó gyökeréhez képest relatív, a "
                                        f"dokumentum-link a fájl saját könyvtárához képest (RP1)")
        if hits > R1_MAX_PER_DOC:
            f.add("MG8", phase, f"{doc}: további {hits - R1_MAX_PER_DOC} útvonal-formátum hiba "
                                f"(nem listázva)")


# ── main ──────────────────────────────────────────────────────────────────────
MANDATORY_SECTIONS = ("mt_environment", "mt_test_data", "mt_automated_tests",
                      "mt_manual_groups", "mt_coverage", "mt_changelog")


def read(path):
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def main():
    _force_utf8_output()
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("cycle_path", help="a ciklus mappája (pl. specs/cycle-07-oidc)")
    parser.add_argument("--mode", choices=("planned", "as-built"), default=None,
                        help="a mód felülbírálása (alap: a fájl fejléc-státuszából)")
    parser.add_argument("--repo-root", default=".",
                        help="a repó gyökere az MG8 útvonal-feloldásához (alap: .)")
    args = parser.parse_args()

    cycle = Path(args.cycle_path)
    if not cycle.is_dir():
        print(f"HIBA: nem létező ciklusmappa: {cycle}", file=sys.stderr)
        return 2

    doc_path = cycle / "manual-test-plan.md"
    text = read(doc_path)
    if text is None:
        print(f"HIBA: nincs meg a {doc_path}. Ez a kapu bemenete — futtasd le előbb a "
              f"`/bs-manual-test-plan` parancsot erre a ciklusra.", file=sys.stderr)
        return 2

    lines = text.splitlines()
    planned, as_built = st("mtp_planned").lower(), st("mtp_as_built").lower()
    raw_status = header_field(lines[:20], "f_status")
    status = (raw_status or "").split("|")[0].strip().lower() if raw_status else None
    if status not in (planned, as_built):
        print(f"HIBA (MG1): a {doc_path} fejlécéből hiányzik vagy érvénytelen a "
              f"`**{fld('f_status')}:**` sor (talált érték: {raw_status!r}).\n"
              f"Pótold a fájl fejlécében az alábbiak közül a helyessel:\n\n"
              f"  **{fld('f_status')}:** {st('mtp_planned')}\n"
              f"  **{fld('f_status')}:** {st('mtp_as_built')}\n", file=sys.stderr)
        return 2
    mode = {"planned": planned, "as-built": as_built}.get(args.mode, status)

    spec_text = read(cycle / "spec.md")
    plan_text = read(cycle / "plan.md")

    f = Findings()
    print(f"Kézi tesztterv kapu (MT5) — {doc_path}")
    print(f"  mód: {mode}{' (--mode felülbírálás)' if args.mode else ''}")
    print(f"  ✓ MG1 — fejléc-státusz: {status}")

    missing_sections = [sec(k) for k in MANDATORY_SECTIONS
                        if section_span(lines, sec(k))[0] is None]
    if missing_sections:
        f.add("MG2", "—", "hiányzó kötelező szekció: " + ", ".join(f"`{s}`" for s in missing_sections))
        print(f"  ✗ MG2 — {len(missing_sections)} kötelező szekció hiányzik")
    else:
        print(f"  ✓ MG2 — mind a {len(MANDATORY_SECTIONS)} kötelező szekció megvan")

    before = len(f.items)
    check_placeholders(lines, f)
    print(f"  {'✓' if len(f.items) == before else '✗'} MG3 — placeholder / üres cella az 1-4. "
          f"szekcióban: {len(f.items) - before} találat")

    before = len(f.items)
    groups = check_groups(lines, f)
    print(f"  {'✓' if len(f.items) == before else '✗'} MG4/MG9 — {len(groups)} tesztcsoport "
          f"ellenőrizve: {len(f.items) - before} találat")

    before = len(f.items)
    note = check_dod_coverage(lines, spec_text, groups, f)
    print(f"  {'✓' if len(f.items) == before else '✗'} MG5 — DoD-lefedettség: {note}")
    if spec_text is None:
        print("    · nincs spec.md a ciklus mappájában — a visszirány nem ellenőrizhető")

    before = len(f.items)
    note = check_startup_commands(lines, f)
    print(f"  {'✓' if len(f.items) == before else '✗'} MG6 — indító parancsok: {note}")

    before = len(f.items)
    note = check_automated_tests(lines, plan_text, mode, cycle, f)
    print(f"  {'✓' if len(f.items) == before else '✗'} MG7 — automata tesztek: {note}")
    if plan_text is None:
        print("    · nincs plan.md a ciklus mappájában — a gépi parancsok nem egyeztethetők")

    before = len(f.items)
    check_path_format([("manual-test-plan.md", text, "—")], Path(args.repo_root), f)
    print(f"  {'✓' if len(f.items) == before else '✗'} MG8 — útvonal-formátum (RP1): "
          f"{len(f.items) - before} találat")

    before = len(f.items)
    check_group_ids(lines, groups, f)
    print(f"  {'✓' if len(f.items) == before else '✗'} MG10 — azonosítók és lefedettségi tábla: "
          f"{len(f.items) - before} találat")

    if not f.items:
        print("\nKAPU OK — a kézi tesztterv gépiesen ellenőrizhető része hiánytalan.")
        return 0

    print(f"\nKAPU BUKOTT — {len(f.items)} javítandó tétel:")
    for code, msg in f.items:
        print(f"  ✗ [{code}] {msg}")
    print("\nJavítsd a fenti pontokat, és futtasd újra a kaput. Legfeljebb 2 javító "
          "próbálkozás, utána állj meg és kérdezz.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
