#!/usr/bin/env python3
"""DS22 Réteg 1 magkapu — determinisztikus, LLM-ítélet nélküli ellenőrzések
a 08-doc-sync fázis számára: rename-maradvány grep, mappa-index halmaz-egyezés,
és coverage-marker bump check. A diagram-átkerülés (DS7) csak informatív
összegzést kap (a tényleges pairing-döntés az ágensnél marad).

DS23/DS25 (opcionális, `--spec-file`/`--plan-file` mellett fut): a spec.md
kidolgozott technikai szerződései (config-tábla, log/esemény-séma, hibakód-
tábla — ugyanaz a fogalom, mint a KX3-nál) és a plan.md `Környezeti
koordináták` (KO1) táblája hajlamos NÉMÁN elveszni a doc-sync-nál: a
`doc-sync-planner` „sebészi patch" elve (ne írj újra, csak a változó
szekciót) tömörítésbe fordul, mert semmi nem kényszeríti ki a szó szerinti
átvételt. A DS23/DS25 ugyanazt a horgony-kinyerő technikát használja, mint az
`analyze-gate-check.py` V1 checkje, csak a cél nem egyetlen fájl (plan.md),
hanem a `docs-generated/` TELJES tartalma — a technikai szerződés
elsődlegesen az `architecture.md`-be tartozik, de bárhol landolhat (pl. egy
komponens-specifikus doksiban), a check csak azt méri, landolt-e valahol.

Kilépő kód: 0 = minden kemény check PASS (DS23/DS25 küszöb felett), 1 = legalább egy FAIL.
"""
import argparse
import re
import sys
from pathlib import Path

from lang_keys import fld, sec

RENAME_RE_TEMPLATE = r"\b{}\b"


def check_rename_leftovers(docs_dir, renames):
    """Régi->új névpárok maradványainak keresése a docs-generated/-ben.

    A CHANGELOG.md és a design-drift.md "## Lezárt eltérések" szekciója
    történeti anyag — ott a régi név jogosan előfordulhat, ezekben nem
    keresünk.
    """
    results = []
    if not renames:
        return results

    excluded_files = {"CHANGELOG.md"}
    drift_path = docs_dir / "design-drift.md"
    excluded_line_ranges = {}  # relative filename -> set of excluded line numbers
    if drift_path.exists():
        lines = drift_path.read_text(encoding="utf-8").splitlines()
        closed_start = None
        for i, line in enumerate(lines):
            if line.strip().startswith("## "):
                if "lezárt eltérések" in line.strip().lower():
                    closed_start = i
                elif closed_start is not None:
                    closed_start = None
                    break
        if closed_start is not None:
            excluded_line_ranges["design-drift.md"] = set(range(closed_start, len(lines)))

    for old_name, new_name in renames:
        pattern = re.compile(RENAME_RE_TEMPLATE.format(re.escape(old_name)))
        leftovers = []
        for md_file in sorted(docs_dir.glob("*.md")):
            if md_file.name in excluded_files:
                continue
            excluded_lines = excluded_line_ranges.get(md_file.name, set())
            for lineno, line in enumerate(md_file.read_text(encoding="utf-8").splitlines()):
                if lineno in excluded_lines:
                    continue
                if pattern.search(line):
                    leftovers.append(f"{md_file.name}:{lineno + 1}: {line.strip()}")
        results.append({
            "old": old_name,
            "new": new_name,
            "status": "FAIL" if leftovers else "PASS",
            "leftovers": leftovers,
        })
    return results


def check_folder_index(docs_dir, readme_name="README.md"):
    """A docs-generated/ tényleges .md fájllistája == a README.md bejegyzései."""
    readme_path = docs_dir / readme_name
    actual_files = {p.name for p in docs_dir.glob("*.md") if p.name != readme_name}

    indexed_files = set()
    if readme_path.exists():
        for line in readme_path.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^\s*-\s*`([^`]+)`", line)
            if m:
                indexed_files.add(m.group(1))

    missing_from_readme = sorted(actual_files - indexed_files)
    stale_in_readme = sorted(indexed_files - actual_files)
    status = "PASS" if not missing_from_readme and not stale_in_readme else "FAIL"
    return {
        "status": status,
        "missing_from_readme": missing_from_readme,
        "stale_in_readme": stale_in_readme,
    }


def check_coverage_markers(docs_dir, marker, changed_files):
    """A megadott (ténylegesen módosított) fájlok fejléc-blokkja az aktuális
    cycle markert mutatja-e ('Utolsó frissítés: cycle-NN')."""
    results = []
    for rel_path in changed_files:
        path = docs_dir / rel_path
        if not path.exists():
            results.append({"file": rel_path, "status": "MISSING_FILE"})
            continue
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:10])
        m = re.search(r"\*\*" + re.escape(fld("f_last_updated")) + r":\*\*\s*([\w.-]+)", head)
        if not m:
            results.append({"file": rel_path, "status": "MISSING_HEADER"})
            continue
        found = m.group(1)
        results.append({
            "file": rel_path,
            "status": "PASS" if found == marker else "FAIL",
            "found_marker": found,
            "expected_marker": marker,
        })
    return results


def summarize_diagrams(docs_dir):
    """Informatív összegzés — a tényleges forrás<->cél párosítás ítélet marad az ágensnél."""
    counts = {}
    for md_file in sorted(docs_dir.glob("*.md")):
        n = len(re.findall(r"```mermaid", md_file.read_text(encoding="utf-8")))
        if n:
            counts[md_file.name] = n
    return counts


# ── DS23/DS25 — technikai szerződés- és környezet-mentesség ──────────────────
# Ugyanaz a horgony-kinyerő technika, mint az `analyze-gate-check.py` V1
# checkjében (spec.md kidolgozott artefaktuma → plan.md), csak a cél a
# `docs-generated/` teljes szövege, mert a helyes cél-fájl (architecture.md
# vagy egy komponens-specifikus doksi) döntése nem a szkripté.

FENCE_RE = re.compile(r"^\s*```([A-Za-z0-9_+-]*)\s*$")
CONTRACT_LANGS = {
    "yaml", "yml", "json", "jsonc", "json5", "http", "sql", "ddl", "xml",
    "toml", "ini", "env", "dotenv",
}
ALNUM_RUN_RE = re.compile(r"[A-Za-z0-9_]{4,}")
HEADING_RE = re.compile(r"^(#{2,4})\s+(.*)$")
TABLE_ROW_RE = re.compile(r"^\s*\|(.+)\|\s*$")
SEPARATOR_ROW_RE = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
PLACEHOLDER_CELL_RE = re.compile(r"^\s*(_.*_|\.\.\.|—|-{1,3}|<.*>)\s*$")
BACKTICK_RE = re.compile(r"`([^`]{3,})`")
CONTRACT_MIN_ANCHORS = 3
CONTRACT_MAX_ANCHORS = 12
CONTRACT_MIN_COVERAGE = 0.6


def _docs_haystack(docs_dir):
    """A `docs-generated/` teljes szövege, szóköz-normalizálva — ide keresünk
    horgonyt, mert a helyes cél-fájlt nem a szkript dönti el."""
    parts = []
    for md_file in sorted(docs_dir.glob("*.md")):
        parts.append(" ".join(md_file.read_text(encoding="utf-8").split()))
    return " ".join(parts)


def _fenced_blocks(text):
    out, lines = [], text.splitlines()
    heading, i = "", 0
    while i < len(lines):
        m = HEADING_RE.match(lines[i])
        if m:
            heading = m.group(2).strip()
            i += 1
            continue
        f = FENCE_RE.match(lines[i])
        if not f:
            i += 1
            continue
        lang, start, body = f.group(1).lower(), i + 1, []
        i += 1
        while i < len(lines) and not FENCE_RE.match(lines[i]):
            body.append(lines[i])
            i += 1
        i += 1
        out.append((lang, heading, start, body))
    return out


def _is_contract_block(lang, body):
    if lang in CONTRACT_LANGS:
        return True
    joined = "\n".join(body)
    if not lang and (re.search(r'^\s*[{\[]', joined) or re.search(r'^\s*[\w"-]+\s*:\s+\S', joined, re.MULTILINE)):
        return True
    return False


def _contract_anchors(body):
    seen, out = set(), []
    for line in body:
        s = " ".join(line.split())
        if len(s) < 12 or not ALNUM_RUN_RE.search(s):
            continue
        if s in seen:
            continue
        seen.add(s)
        out.append(s)
    return out


def check_contract_transfer(docs_dir, spec_text):
    """DS23 — a spec.md kidolgozott technikai szerződései (config/YAML-tábla,
    log/esemény JSON-séma, hibakód-tábla) landoltak-e VALAHOL a
    `docs-generated/`-ben. A `<sec:out_of_scope>` szekció szándékosan kihagyott
    példáit nem kérjük számon (ugyanaz a kivétel, mint a V1-nél)."""
    haystack = _docs_haystack(docs_dir)
    results = []
    for lang, heading, lineno, body in _fenced_blocks(spec_text):
        if "out of scope" in heading.lower():
            continue
        if not _is_contract_block(lang, body):
            continue
        anchors = _contract_anchors(body)
        if len(anchors) < CONTRACT_MIN_ANCHORS:
            continue
        sample = anchors[:CONTRACT_MAX_ANCHORS]
        missing = [a for a in sample if a not in haystack]
        found = len(sample) - len(missing)
        coverage = found / len(sample)
        results.append({
            "heading": heading or "(cím nélküli blokk)",
            "lineno": lineno,
            "lang": lang or "jelöletlen",
            "found": found,
            "total": len(sample),
            "coverage": coverage,
            "status": "PASS" if coverage >= CONTRACT_MIN_COVERAGE else "FAIL",
            "missing_sample": missing[:3],
        })
    return results


def _table_rows(text, title_substr):
    """Egy `## <cím>` szekció ELSŐ markdown táblájának adatsorai."""
    lines, start = text.splitlines(), None
    for i, line in enumerate(lines):
        m = HEADING_RE.match(line)
        if m and title_substr in m.group(2):
            start = i + 1
            break
    if start is None:
        return []
    rows, seen_separator = [], False
    for line in lines[start:]:
        if HEADING_RE.match(line):
            break
        m = TABLE_ROW_RE.match(line)
        if not m:
            if rows:
                break
            continue
        if SEPARATOR_ROW_RE.match(line):
            seen_separator = True
            continue
        if not seen_separator:
            continue
        cells = [c.strip() for c in m.group(1).split("|")]
        if cells and all(PLACEHOLDER_CELL_RE.match(c) or not c for c in cells):
            continue
        rows.append(cells)
    return rows


SECRET_LABEL_RE = re.compile(
    r"jelsz|password|secret|titok|token|api[- ]?key|credential", re.IGNORECASE
)


def check_environment_coords_transfer(docs_dir, plan_text):
    """DS25 — a plan.md `Környezeti koordináták` (KO1) táblájának értékei
    (URL-ek, portok, teszt-userek, elérési utak) megjelennek-e VALAHOL a
    `docs-generated/`-ben. Enélkül a docs-generated önmagában nem elég ahhoz,
    hogy valaki lokálisan futtassa/elérje a rendszert.

    Titok-szűrés (ua. elv, mint a TC5-nél): jelszó/secret/token jellegű SOR
    címkéjét kihagyjuk — ezeknek a docs-generated-ben pointerre kell
    hivatkozniuk, nem a nyers értékre, tehát a hiányuk itt NEM hiba."""
    haystack = _docs_haystack(docs_dir)
    rows = _table_rows(plan_text, sec("environment_coords"))
    missing = []
    for cells in rows:
        if len(cells) < 2:
            continue
        label, value = cells[0], cells[1]
        if SECRET_LABEL_RE.search(label):
            continue
        candidates = BACKTICK_RE.findall(value)
        if not candidates and value and len(value) <= 80:
            candidates = [value]
        for c in candidates:
            c_norm = " ".join(c.split())
            if len(c_norm) < 3 or c_norm in ("—", "-", "N/A"):
                continue
            if c_norm not in haystack:
                missing.append((label.strip() or "(névtelen sor)", c_norm))
    return {
        "row_count": len(rows),
        "missing": missing,
        "status": "PASS" if not missing else "FAIL",
    }


def parse_rename_arg(value):
    if "=" not in value:
        raise argparse.ArgumentTypeError(f"várt formátum RÉGI=ÚJ, kaptam: {value}")
    old, new = value.split("=", 1)
    return (old, new)



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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docs_dir", help="a docs-generated/ mappa útvonala")
    parser.add_argument("--rename", action="append", type=parse_rename_arg, default=[],
                         metavar="RÉGI=ÚJ", help="deklarált átnevezés-pár (ismételhető)")
    parser.add_argument("--marker", default=None, metavar="cycle-NN",
                         help="az aktuális ciklus coverage-marker értéke")
    parser.add_argument("--changed-file", action="append", default=[], metavar="FÁJLNÉV",
                         help="ténylegesen módosított docs-generated fájl (a --marker ellenőrzéséhez, ismételhető)")
    parser.add_argument("--spec-file", default=None, metavar="ÚTVONAL",
                         help="a ciklus spec.md-je (DS23: technikai szerződések átvétele) — elhagyható, ekkor a check kimarad")
    parser.add_argument("--plan-file", default=None, metavar="ÚTVONAL",
                         help="a ciklus plan.md-je (DS25: Környezeti koordináták átvétele) — elhagyható, ekkor a check kimarad")
    args = parser.parse_args()

    docs_dir = Path(args.docs_dir)
    if not docs_dir.is_dir():
        print(f"HIBA: nem létező mappa: {docs_dir}", file=sys.stderr)
        return 2

    overall_pass = True

    print("## DS22 Réteg 1 — magkapu eredmény\n")

    print("### 1. Rename-maradvány ellenőrzés")
    rename_results = check_rename_leftovers(docs_dir, args.rename)
    if not rename_results:
        print("- Nincs megadott átnevezés-pár — kihagyva.\n")
    else:
        for r in rename_results:
            print(f"- `{r['old']}` → `{r['new']}`: **{r['status']}**")
            for leftover in r["leftovers"]:
                print(f"  - {leftover}")
            if r["status"] == "FAIL":
                overall_pass = False
        print()

    print("### 2. Mappa-index halmaz-egyezés (DS21)")
    index_result = check_folder_index(docs_dir)
    print(f"- Státusz: **{index_result['status']}**")
    if index_result["missing_from_readme"]:
        print(f"  - README-ből hiányzik: {', '.join(index_result['missing_from_readme'])}")
    if index_result["stale_in_readme"]:
        print(f"  - README-ben van, de a fájl nem létezik: {', '.join(index_result['stale_in_readme'])}")
    if index_result["status"] == "FAIL":
        overall_pass = False
    print()

    print("### 3. Coverage-marker bump (DS17)")
    if args.marker is None or not args.changed_file:
        print("- Nincs megadott marker/changed-file — kihagyva.\n")
    else:
        marker_results = check_coverage_markers(docs_dir, args.marker, args.changed_file)
        for r in marker_results:
            if r["status"] == "PASS":
                print(f"- `{r['file']}`: **PASS**")
            elif r["status"] == "MISSING_FILE":
                print(f"- `{r['file']}`: **MISSING_FILE** (a fájl nem létezik)")
                overall_pass = False
            elif r["status"] == "MISSING_HEADER":
                print(f"- `{r['file']}`: **MISSING_HEADER** (nincs fejléc-blokk)")
                overall_pass = False
            else:
                print(f"- `{r['file']}`: **FAIL** (talált marker: `{r['found_marker']}`, elvárt: `{r['expected_marker']}`)")
                overall_pass = False
        print()

    print("### 4. Diagram-előfordulások (informatív — a pairing-döntés az ágensé)")
    diagram_counts = summarize_diagrams(docs_dir)
    if diagram_counts:
        for name, count in diagram_counts.items():
            print(f"- `{name}`: {count} mermaid blokk")
    else:
        print("- Nincs mermaid blokk a docs-generated/-ben.")
    print()

    print("### 5. Technikai szerződés-átvétel (DS23)")
    if args.spec_file is None:
        print("- Nincs megadott --spec-file — kihagyva.\n")
    else:
        spec_path = Path(args.spec_file)
        if not spec_path.is_file():
            print(f"- HIBA: {spec_path} nem található — kihagyva.\n")
        else:
            contract_results = check_contract_transfer(docs_dir, spec_path.read_text(encoding="utf-8"))
            if not contract_results:
                print("- Nincs kidolgozott technikai szerződés-blokk a spec.md-ben.\n")
            else:
                for r in contract_results:
                    print(f"- spec.md:{r['lineno']} (`{r['heading']}`, {r['lang']}): **{r['status']}** "
                          f"({r['found']}/{r['total']} horgony megvan)")
                    if r["status"] == "FAIL":
                        overall_pass = False
                        for m in r["missing_sample"]:
                            print(f"  - hiányzik: {m[:80]}")
                print()

    print("### 6. Környezeti koordináták átvétele (DS25)")
    if args.plan_file is None:
        print("- Nincs megadott --plan-file — kihagyva.\n")
    else:
        plan_path = Path(args.plan_file)
        if not plan_path.is_file():
            print(f"- HIBA: {plan_path} nem található — kihagyva.\n")
        else:
            env_result = check_environment_coords_transfer(docs_dir, plan_path.read_text(encoding="utf-8"))
            if env_result["row_count"] == 0:
                print("- A plan.md-ben nincs `Környezeti koordináták` tábla — kihagyva.\n")
            else:
                print(f"- Státusz: **{env_result['status']}** ({env_result['row_count']} sor ellenőrizve)")
                for label, value in env_result["missing"]:
                    print(f"  - hiányzik a docs-generated/-ből: `{label}` → `{value}`")
                if env_result["status"] == "FAIL":
                    overall_pass = False
                print()

    print(f"## Összesített státusz: {'PASS' if overall_pass else 'FAIL'}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
