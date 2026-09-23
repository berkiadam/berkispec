#!/usr/bin/env python3
"""A kétnyelvű `docs/` dokumentáció-fa determinisztikus kapuja (`DG1`–`DG6`).

Miért kell: a `lang-parity-check.py` docstringje pontosan ezt a hibaosztályt írja
le a prompt-fákra — a kézzel tartott kétnyelvű fák CSENDBEN szétcsúsznak. A
`docs/en` + `docs/hu` fa ugyanígy fog: a magyar oldalon bővül egy szakasz, az
angol oldal pedig a régi állapotot mutatja tovább. A README szétvágása ráadásul
ÚJ hibaosztályt is behozott, a törött relatív linket — ami egy egyfájlos
README-ben definíció szerint nem létezett.

Amit ellenőriz:
  DG1  fájlhalmaz-paritás    — `docs/en/*.md` névhalmaza ≡ `docs/hu/*.md`
  DG2  szakasz-paritás       — fájlpáronként a fejlécek SZÁMA és MÉLYSÉG-SORRENDJE
                               egyezik (a szövegük nem — az fordítás)
  DG3  link-feloldás         — minden relatív link létező fájlra mutat, minden
                               `#horgony` létező fejlécre
  DG4  index halmaz-egyezés  — a `docs/<lang>/README.md` oldalindex bejegyzései
                               ≡ a mappa tényleges `.md` fájljai, és a nyitólap
                               tartalomjegyzéke ≡ ugyanez a halmaz
  DG5  a nyitólap nem hízik  — a gyökér-README-k ≤ 400 sorosak, és nem
                               tartalmaznak `<!-- TOC -->` markert
  DG6  ábra-paritás          — a ```mermaid blokkok száma fájlpáronként egyezik

Amit NEM ellenőriz: a fordítás jelentés-helyességét (ugyanaz a korlát, mint a
`lang-parity-check.py` 11.11-nél), a szövegek minőségét és a külső (http) linkek
elérhetőségét.

A fájlpárokba a két gyökér-nyitólap (`README.md` ↔ `README-HU.md`) is beleszámít
a `DG2`/`DG6` szempontjából: a nyitólapok is tükrözött szerkezetűek.

Használat:
  docs-tree-check.py                    # teljes kimenet
  docs-tree-check.py --check            # csendesebb kimenet (csak a verdikt + FAIL)
  docs-tree-check.py --root <repó>      # a repó gyökere (alap: a szkript helyéből)

Kilépő kód: 0 = nincs hiba (WARN megengedett), 1 = legalább egy FAIL,
            2 = használati hiba (nincs `docs/` fa, nincs nyelvi ág).

Ez REPÓ-KARBANTARTÓ eszköz: a célprojektbe NEM települ (az `install-helper.py`
`copy_helper_scripts()` kizárási listáján szerepel), mert ott nincs `docs/en` fa.
"""
import argparse
import re
import sys
from pathlib import Path

# ── konstansok ────────────────────────────────────────────────────────────────
MAX_ROOT_LINES = 400          # DG5 — kemény korlát, nem WARN
INDEX_NAME = "README.md"      # a nyelvi ág oldalindexe
LANG_DIR_RE = re.compile(r"^[a-z]{2}$")   # `docs/en`, `docs/hu` — a `talks`/`assets` kimarad
TOC_MARKER_RE = re.compile(r"<!--\s*/?\s*TOC\s*-->", re.IGNORECASE)

FENCE_RE = re.compile(r"^\s*`{3,}(.*)$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(\S.*?)\s*$")
LINK_RE = re.compile(r"!?\[[^\]]*\]\(\s*([^)\s]+?)\s*(?:\s+\"[^\"]*\")?\s*\)")
EXTERNAL_RE = re.compile(r"^(?:https?:|mailto:|tel:|#?/)", re.IGNORECASE)


def root_page(lang):
    """A nyelvi ághoz tartozó gyökér-nyitólap neve. Az `en` a kitüntetett
    alapértelmezés (`README.md`), minden más nyelv utótagot kap — így egy
    harmadik nyelv sem igényel script-módosítást."""
    return "README.md" if lang == "en" else f"README-{lang.upper()}.md"


class Report:
    """FAIL/WARN gyűjtő. A FAIL-ok a kilépő kódot is állítják."""

    def __init__(self):
        self.fails = []
        self.warns = []

    def fail(self, check, where, msg):
        self.fails.append((check, where, msg))

    def warn(self, check, where, msg):
        self.warns.append((check, where, msg))


# ── segédfüggvények ───────────────────────────────────────────────────────────
def strip_fences(text):
    """A kódblokkok sorait üresre cseréli, de a SORSZÁMOZÁST megtartja — így a
    fence-en belüli `#` sor nem fejléc és a `](...)` nem link, a hibaüzenet
    sorszáma viszont a valódi fájlra mutat."""
    out = []
    fence = None
    for line in text.splitlines():
        m = FENCE_RE.match(line)
        if m:
            marker = line.strip()[:3]
            if fence is None:
                fence = marker
            elif line.strip().startswith(fence):
                fence = None
            out.append("")
            continue
        out.append("" if fence else line)
    return out


def headings(lines):
    """(szint, szöveg) párok a fence-mentesített sorokból."""
    found = []
    for line in lines:
        m = HEADING_RE.match(line)
        if m:
            found.append((len(m.group(1)), m.group(2)))
    return found


def slugify(text):
    """A GitHub fejléc-horgony képzése: a linkekből a szöveg marad, az inline
    markdown jelölők eltűnnek, a maradékból kisbetűs, kötőjeles slug lesz."""
    s = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    s = re.sub(r"[`*_~]", "", s)
    s = s.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    return re.sub(r"\s+", "-", s)


def anchors(lines):
    """A fájl fejléceiből képzett horgony-halmaz, a GitHub duplikátum-kezelésével
    (`-1`, `-2` utótag az ismétlődő slugokra)."""
    seen = {}
    result = set()
    for _level, text in headings(lines):
        base = slugify(text)
        n = seen.get(base, 0)
        seen[base] = n + 1
        result.add(base if n == 0 else f"{base}-{n}")
    return result


def mermaid_count(text):
    """A ```mermaid blokkok száma (csak a NYITÓ fence-t számoljuk)."""
    return sum(1 for line in text.splitlines()
               if line.strip().startswith("```") and line.strip()[3:].strip().lower() == "mermaid")


def links(lines):
    """(sorszám, cél) párok a fence-mentesített sorokból, a külső linkek nélkül."""
    found = []
    for i, line in enumerate(lines, start=1):
        for target in LINK_RE.findall(line):
            if EXTERNAL_RE.match(target):
                continue
            found.append((i, target))
    return found


def page_set(directory):
    """A mappa témaoldalai — az oldalindex (`README.md`) nélkül."""
    return {p.name for p in directory.glob("*.md") if p.name != INDEX_NAME}


# ── DG1 ───────────────────────────────────────────────────────────────────────
def check_file_sets(docs_dir, langs, ref, rep):
    """Fájlhalmaz-paritás. Visszaadja a MINDEN nyelvi ágban meglévő fájlneveket."""
    sets = {lang: {p.name for p in (docs_dir / lang).glob("*.md")} for lang in langs}
    common = set.intersection(*sets.values())
    for lang in langs:
        if lang == ref:
            continue
        missing = sorted(sets[ref] - sets[lang])
        extra = sorted(sets[lang] - sets[ref])
        for name in missing:
            rep.fail("DG1", f"docs/{lang}/{name}", f"hiányzik (a `{ref}` ágban megvan)")
        for name in extra:
            rep.fail("DG1", f"docs/{lang}/{name}", f"nincs párja a `{ref}` ágban")
    return sorted(common)


# ── DG2 · DG6 ─────────────────────────────────────────────────────────────────
def check_pair(rep, ref_path, other_path, ref_label, other_label):
    """Szakasz- és ábra-paritás egy fájlpárra."""
    ref_text = ref_path.read_text(encoding="utf-8")
    other_text = other_path.read_text(encoding="utf-8")
    ref_heads = headings(strip_fences(ref_text))
    other_heads = headings(strip_fences(other_text))

    ref_levels = [lvl for lvl, _ in ref_heads]
    other_levels = [lvl for lvl, _ in other_heads]
    if len(ref_levels) != len(other_levels):
        rep.fail("DG2", other_label,
                 f"{len(other_levels)} fejléc, a `{ref_label}` oldalon {len(ref_levels)}")
    elif ref_levels != other_levels:
        for idx, (a, b) in enumerate(zip(ref_levels, other_levels), start=1):
            if a != b:
                rep.fail("DG2", other_label,
                         f"a(z) {idx}. fejléc mélysége {b} (`{other_heads[idx - 1][1]}`), "
                         f"a `{ref_label}` oldalon {a} (`{ref_heads[idx - 1][1]}`)")
                break

    ref_mermaid = mermaid_count(ref_text)
    other_mermaid = mermaid_count(other_text)
    if ref_mermaid != other_mermaid:
        rep.fail("DG6", other_label,
                 f"{other_mermaid} mermaid blokk, a `{ref_label}` oldalon {ref_mermaid}")


# ── DG3 ───────────────────────────────────────────────────────────────────────
def check_links(rep, root, paths):
    """Relatív link- és horgony-feloldás. A horgonyt a CÉLFÁJL fejléceihez méri,
    tehát az oldalközi `fájl.md#szakasz` alakot is ellenőrzi."""
    anchor_cache = {}

    def anchors_of(path):
        key = str(path)
        if key not in anchor_cache:
            anchor_cache[key] = anchors(strip_fences(path.read_text(encoding="utf-8")))
        return anchor_cache[key]

    for path in paths:
        label = path.relative_to(root).as_posix()
        lines = strip_fences(path.read_text(encoding="utf-8"))
        for lineno, target in links(lines):
            file_part, _, anchor = target.partition("#")
            if not file_part:
                if anchor and anchor not in anchors_of(path):
                    rep.fail("DG3", f"{label}:{lineno}",
                             f"a `#{anchor}` horgonynak nincs fejléce a saját fájljában")
                continue
            resolved = (path.parent / file_part).resolve()
            if not resolved.exists():
                rep.fail("DG3", f"{label}:{lineno}", f"a `{target}` nem létező fájlra mutat")
                continue
            if anchor and resolved.suffix == ".md" and anchor not in anchors_of(resolved):
                rep.fail("DG3", f"{label}:{lineno}",
                         f"a `#{anchor}` horgonynak nincs fejléce a `{file_part}` fájlban")


# ── DG4 ───────────────────────────────────────────────────────────────────────
def check_indexes(rep, root, docs_dir, langs):
    """Az oldalindex és a nyitólap tartalomjegyzéke ≡ a mappa tényleges oldalai."""
    for lang in langs:
        lang_dir = docs_dir / lang
        actual = page_set(lang_dir)

        index_path = lang_dir / INDEX_NAME
        if not index_path.exists():
            rep.fail("DG4", f"docs/{lang}/{INDEX_NAME}", "nincs oldalindex")
        else:
            lines = strip_fences(index_path.read_text(encoding="utf-8"))
            indexed = {t.partition("#")[0] for _n, t in links(lines)
                       if "/" not in t and t.partition("#")[0].endswith(".md")}
            indexed.discard(INDEX_NAME)
            _diff(rep, f"docs/{lang}/{INDEX_NAME}", actual, indexed, "az oldalindexből")

        page = root / root_page(lang)
        if not page.exists():
            rep.fail("DG4", root_page(lang), "nincs nyitólap ehhez a nyelvi ághoz")
            continue
        lines = strip_fences(page.read_text(encoding="utf-8"))
        prefix = f"docs/{lang}/"
        listed = {t.partition("#")[0][len(prefix):] for _n, t in links(lines)
                  if t.startswith(prefix) and t.partition("#")[0].endswith(".md")}
        listed.discard(INDEX_NAME)
        _diff(rep, root_page(lang), actual, listed, "a nyitólap tartalomjegyzékéből")


def _diff(rep, where, actual, listed, what):
    for name in sorted(actual - listed):
        rep.fail("DG4", where, f"a `{name}` oldal hiányzik {what}")
    for name in sorted(listed - actual):
        rep.fail("DG4", where, f"a `{name}` bejegyzés mögött nincs oldal ({what} elavult)")


# ── DG5 ───────────────────────────────────────────────────────────────────────
def check_root_pages(rep, root, langs):
    """A nyitólap nem hízik vissza: sorkorlát + tiltott generált TOC marker."""
    for lang in langs:
        name = root_page(lang)
        path = root / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        count = len(text.splitlines())
        if count > MAX_ROOT_LINES:
            rep.fail("DG5", name,
                     f"{count} sor — a felső korlát {MAX_ROOT_LINES} "
                     f"(a részleteknek a `docs/{lang}/` fában a helyük)")
        for i, line in enumerate(text.splitlines(), start=1):
            if TOC_MARKER_RE.search(line):
                rep.fail("DG5", f"{name}:{i}",
                         "generált `<!-- TOC -->` marker — a tartalomjegyzék "
                         "fizikai aloldalakra visz, nem fájlon belüli horgonyokra")


# ── belépő ────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="csendesebb kimenet (csak a verdikt és a FAIL-ok)")
    parser.add_argument("--ref", default="en", help="a referencia nyelvi ág (alap: en)")
    parser.add_argument("--root", default=Path(__file__).resolve().parents[2],
                        help="a repó gyökere (alap: a szkript helyéből számolva)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    docs_dir = root / "docs"
    if not docs_dir.is_dir():
        print(f"HIBA: nincs {docs_dir} mappa.", file=sys.stderr)
        return 2

    langs = sorted(d.name for d in docs_dir.iterdir()
                   if d.is_dir() and LANG_DIR_RE.match(d.name))
    if len(langs) < 2:
        print("HIBA: legalább két nyelvi ág kell a docs/ alatt "
              "(pl. docs/en és docs/hu).", file=sys.stderr)
        return 2
    ref = args.ref if args.ref in langs else langs[0]

    rep = Report()
    common = check_file_sets(docs_dir, langs, ref, rep)

    pairs = 0
    for lang in langs:
        if lang == ref:
            continue
        for name in common:
            check_pair(rep, docs_dir / ref / name, docs_dir / lang / name,
                       f"docs/{ref}/{name}", f"docs/{lang}/{name}")
            pairs += 1
        ref_page, other_page = root / root_page(ref), root / root_page(lang)
        if ref_page.exists() and other_page.exists():
            check_pair(rep, ref_page, other_page, root_page(ref), root_page(lang))
            pairs += 1

    scanned = [p for lang in langs for p in sorted((docs_dir / lang).glob("*.md"))]
    scanned += [root / root_page(lang) for lang in langs if (root / root_page(lang)).exists()]
    check_links(rep, root, scanned)
    check_indexes(rep, root, docs_dir, langs)
    check_root_pages(rep, root, langs)

    print(f"DOCS-TREE — nyelvi ágak: {', '.join(langs)} (referencia: {ref}) · "
          f"{len(scanned)} oldal · {pairs} fájlpár ellenőrizve")
    if rep.warns and not args.check:
        print(f"\n  WARN ({len(rep.warns)}):")
        for check, where, msg in rep.warns:
            print(f"    [{check}] {where}: {msg}")
    elif rep.warns:
        print(f"  WARN: {len(rep.warns)} tétel")
    if rep.fails:
        print(f"\n  ✗ FAIL ({len(rep.fails)}):")
        for check, where, msg in rep.fails:
            print(f"    [{check}] {where}: {msg}")
        return 1
    print("  ✓ a fa paritásos, minden link felold, a nyitólapok a korláton belül vannak.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
