#!/usr/bin/env python3
"""DS22 Réteg 1 magkapu — determinisztikus, LLM-ítélet nélküli ellenőrzések
a 08-doc-sync fázis számára: rename-maradvány grep, mappa-index halmaz-egyezés,
és coverage-marker bump check. A diagram-átkerülés (DS7) csak informatív
összegzést kap (a tényleges pairing-döntés az ágensnél marad).

Kilépő kód: 0 = mindhárom kemény check PASS, 1 = legalább egy FAIL.
"""
import argparse
import re
import sys
from pathlib import Path

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
        m = re.search(r"\*\*Utolsó frissítés:\*\*\s*([\w.-]+)", head)
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


def parse_rename_arg(value):
    if "=" not in value:
        raise argparse.ArgumentTypeError(f"várt formátum RÉGI=ÚJ, kaptam: {value}")
    old, new = value.split("=", 1)
    return (old, new)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docs_dir", help="a docs-generated/ mappa útvonala")
    parser.add_argument("--rename", action="append", type=parse_rename_arg, default=[],
                         metavar="RÉGI=ÚJ", help="deklarált átnevezés-pár (ismételhető)")
    parser.add_argument("--marker", default=None, metavar="cycle-NN",
                         help="az aktuális ciklus coverage-marker értéke")
    parser.add_argument("--changed-file", action="append", default=[], metavar="FÁJLNÉV",
                         help="ténylegesen módosított docs-generated fájl (a --marker ellenőrzéséhez, ismételhető)")
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

    print(f"## Összesített státusz: {'PASS' if overall_pass else 'FAIL'}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
