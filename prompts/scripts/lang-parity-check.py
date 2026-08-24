#!/usr/bin/env python3
"""A kétnyelvű prompt-fák determinisztikus paritás-kapuja (§11).

Miért kell: a `prompts/<base>-<lang>` fák (skills / agents / shared) és a
`prompts/lang/<lang>` projekt-nyelvi blokkok kézzel tartva CSENDBEN szétcsúsznak
— a magyar oldalon javítunk egy szabályt, az angol oldal pedig a régi viselkedést
telepíti tovább. A telepítés byte-azonossági kerete (16.1) erre vak: az egynyelvű
kimenetet nem érinti, ha a másik fából kimaradt egy szekció.

Ez a kapu SZERKEZETI és LELTÁR-hibákat fog meg — NEM a fordítás jelentés-
helyességét (11.11). A következőket NEM tudja ellenőrizni, azokra emberi review
kell: félrefordított szakszó, megfordított feltétel (`ha van` ↔ `ha nincs`),
elveszett indoklás, olyan mondat, ami nyelvtanilag rendben van, de mást állít.

Használat:
  lang-parity-check.py                  # default („folyamatban") mód
  lang-parity-check.py --check          # ugyanaz, csendesebb kimenettel
  lang-parity-check.py --strict         # a teljes fájlhalmaz-paritás is kötelező

Két üzemmód (LG25):
  DEFAULT  — csak a MINDKÉT oldalon létező fájlpárokra futtatja a 11.3–11.12
             ellenőrzéseket; a féloldalas fájlokat WARN-ként listázza. Így a
             fájlonként haladó fordítási szakasz (§13) alatt is használható.
  --strict — a 11.1 fájlhalmaz-paritás is kötelező (a 16.3 és a PR zárása ezt
             követeli meg).

Kilépő kód: 0 = nincs hiba (WARN megengedett), 1 = legalább egy FAIL,
            2 = használati hiba (nincs prompt-fa, hiányzó status-keys.json).
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

# ── minták ────────────────────────────────────────────────────────────────────
INCLUDE_RE = re.compile(r"<!--\s*INCLUDE:\s*(?P<path>[^\s]+?)\s*-->")
ANCHOR_RE = re.compile(r"^<!--\s*ANCHOR:\s*(?P<name>\S+?)\s*-->\s*$", re.MULTILINE)
RULE_ID_RE = re.compile(r"\b([A-Z]{2,3}\d+[a-z]?(?:/[a-z])?)\b")
TOKEN_RE = re.compile(r"<(sec|field|status):([a-z0-9_]+)>")
TOKEN_GROUPS = {"sec": "sections", "field": "fields", "status": "status"}
HEADING_RE = re.compile(r"^(#{1,6})\s+\S", re.MULTILINE)
FENCE_RE = re.compile(r"^\s*\\?`{3,}(.*)$")
FM_KEYS = ("prerequisites", "output", "prev", "next", "subagents", "shared", "phase")

# 11.10 — a „kemény padló" jelölések. Fájlonként egyeznie kell a két nyelvi
# változatban. A magyar és az angol alak UGYANAZT az osztályt jelöli, ezért egy
# csoportba számoljuk őket: `TILOS` → `FORBIDDEN`/`NEVER` fordítás megengedett,
# az EREJE viszont nem veszhet el (13.2.2).
IMPERATIVES = {
    "⛔": ("⛔",),
    "🔴": ("🔴",),
    "⚠️": ("⚠️",),
    "TILOS/SOHA/FORBIDDEN/NEVER": ("TILOS", "SOHA", "FORBIDDEN", "NEVER"),
    "SZIGORÚ/STRICT": ("SZIGORÚ", "STRICT"),
    "Must Fix": ("Must Fix",),
    "STOP/ÁLLJ MEG": ("STOP", "ÁLLJ MEG"),
}

# 11.8 — a fence-tartalom akkor FORDÍTHATÓ, ha az infostring ezek egyike
# (illusztratív, fájlba nem kerülő példa — 9.1). MINDEN MÁS infostring
# byte-azonosságot követel (biztonságos default): parancsot nem fordítunk.
TRANSLATABLE_FENCES = {"", "md", "markdown", "text", "txt", "mermaid"}

# ...azzal a pontosítással, hogy a KOMMENT és a HELYŐRZŐ a parancs-fence-ben is
# prompt-nyelvi. Egy `# a ciklus-worktree megszűnik` sorral és a
# `git worktree add ../<projekt>-cNN` helyőrzőjével a szó szerinti byte-azonosság
# szembemenne a 16.5 nyelvi tisztaság-ellenőrzéssel (magyar szöveg az `en` fában).
# Amit a check VÉD: a parancsnév, a kapcsolók, az útvonalak és a szkript-argumentumok
# — ezeket a fordító nem írhatja át. Ezért a összevetés előtt maszkoljuk a
# `#`-kommentet és a `<…>` helyőrzőt, és normalizáljuk a whitespace-t.
_COMMENT_RE = re.compile(r"#.*$", re.MULTILINE)
_PLACEHOLDER_RE = re.compile(r"<[^<>\n]*>")
# A DUPLA idézőjeles string a parancsban TARTALOM, nem szintaxis: commit-üzenet
# (`git commit -m "cycle-NN: 06-implement - kész"`) vagy sentinel, amit az ágens
# olvas vissza (`echo "MAR_BENNE"`). Ezek fordulnak. Az EGYSZERES idézőjelet
# szándékosan NEM maszkoljuk: ott jellemzően minta/glob áll (`grep -qxF '.bs-*'`),
# ami parancs-szemantika.
_DQ_STRING_RE = re.compile(r'"[^"\n]*"')


def normalize_code(text):
    text = _COMMENT_RE.sub("", text)
    text = _PLACEHOLDER_RE.sub("<>", text)
    text = _DQ_STRING_RE.sub('""', text)
    return "\n".join(" ".join(line.split()) for line in text.split("\n") if line.strip())

# 11.2 — a suffix nélküli fa tiltott (LG5)
LEGACY_DIRS = ("skills", "agents", "shared")
BASES = ("skills", "agents", "shared")


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
def lang_subdir(base, lang):
    """A `_lang_subdir` (install-helper.py) tükre — NEM hardcode-olt mappanév,
    hogy egy jövőbeli harmadik nyelv se igényeljen script-módosítást (11.1)."""
    return f"{base}-{lang}"


def discover_langs(prompts_dir):
    """A jelen lévő nyelvek: a `<base>-<lang>` mappák és a `lang/<lang>` uniója."""
    langs = set()
    for base in BASES:
        for d in prompts_dir.glob(f"{base}-*"):
            if d.is_dir():
                langs.add(d.name[len(base) + 1:])
    lang_dir = prompts_dir / "lang"
    if lang_dir.is_dir():
        for d in lang_dir.iterdir():
            if d.is_dir():
                langs.add(d.name)
    return sorted(langs)


def tree_dir(prompts_dir, base, lang):
    return prompts_dir / ("lang/" + lang if base == "lang" else lang_subdir(base, lang))


def md_names(directory):
    return {p.name for p in directory.glob("*.md")} if directory.is_dir() else set()


def frontmatter(text):
    """(mezők dict, törzs). Frontmatter nélkül ({}, teljes szöveg)."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, text
    fields, end = {}, None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
        m = re.match(r"^([A-Za-z_][\w-]*):(.*)$", lines[i])
        if m:
            fields[m.group(1)] = m.group(2).strip()
    if end is None:
        return {}, text
    return fields, "\n".join(lines[end + 1:])


def yaml_list_len(value, block_lines):
    """Egy frontmatter-kulcs elemszáma: inline `[a, b]`, vagy a következő
    behúzott `- ` sorok száma. Csak a DARABSZÁM számít (11.4) — a tartalom
    nyelvfüggő lehet."""
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return len([x for x in inner.split(",") if x.strip()])
    return len(block_lines)


def frontmatter_list_lengths(text):
    """A FM_KEYS kulcsok elemszáma (a többsoros YAML listákat is beleértve)."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}
    out, current, block = {}, None, []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        m = re.match(r"^([A-Za-z_][\w-]*):(.*)$", line)
        if m:
            if current:
                out[current] = yaml_list_len(out.pop(current + "#raw", ""), block)
            key, value = m.group(1), m.group(2)
            current, block = (key, []) if key in FM_KEYS else (None, [])
            if current:
                out[current + "#raw"] = value
        elif current and re.match(r"^\s+-\s", line):
            block.append(line)
    if current:
        out[current] = yaml_list_len(out.pop(current + "#raw", ""), block)
    return {k: v for k, v in out.items() if not k.endswith("#raw")}


def fences(text):
    """[(infostring, tartalom)] — a `\\`\\`\\`` escape-elt fence-eket is érti,
    mert a skillekben a sablonok escape-elve állnak."""
    out, open_info, buf = [], None, []
    for line in text.split("\n"):
        m = FENCE_RE.match(line.strip().replace("\\", ""))
        if m:
            if open_info is None:
                open_info, buf = m.group(1).strip(), []
            else:
                out.append((open_info, "\n".join(buf)))
                open_info = None
            continue
        if open_info is not None:
            buf.append(line)
    if open_info is not None:
        out.append((open_info, "\n".join(buf)))
    return out


WORD_CHAR = re.compile(r"[0-9A-Za-zÁÉÍÓÖŐÚÜŰáéíóöőúüű_-]")


def contains_literal(text, value):
    """Szóhatáros keresés. A puszta `in` téves találatot ad (`Kör` a
    `körönkénti`-ben, `Kész` a `Készen`-ben) — a 9.6 zárásakor a találatok
    ~90%-a ilyen volt."""
    for m in re.finditer(re.escape(value), text):
        before_ok = m.start() == 0 or not WORD_CHAR.match(text[m.start() - 1])
        after_ok = m.end() == len(text) or not WORD_CHAR.match(text[m.end()])
        if before_ok and after_ok:
            return True
    return False


# ── ellenőrzések ──────────────────────────────────────────────────────────────
def check_asymmetry(prompts_dir, rep):
    """11.2 — aszimmetria-őr (LG5)."""
    for name in LEGACY_DIRS:
        if (prompts_dir / name).is_dir():
            rep.fail("11.2", f"prompts/{name}", "suffix nélküli fa létezik — mindkét "
                     "nyelvnek prefixelt mappában kell élnie (LG5)")


def check_file_sets(prompts_dir, langs, ref, rep, strict):
    """11.1 — fájllista-paritás. Visszaadja a MINDKÉT oldalon létező párokat."""
    pairs = []
    for base in BASES + ("lang",):
        ref_dir = tree_dir(prompts_dir, base, ref)
        if not ref_dir.is_dir():
            continue
        for lang in langs:
            if lang == ref:
                continue
            other = tree_dir(prompts_dir, base, lang)
            a, b = md_names(ref_dir), md_names(other)
            for name in sorted(a & b):
                pairs.append((base, name, ref, lang))
            for name in sorted(a - b):
                where = f"{base}-{lang}/{name}" if base != "lang" else f"lang/{lang}/{name}"
                msg = f"hiányzik (a {ref} oldalon megvan)"
                (rep.fail if strict else rep.warn)("11.1", where, msg)
            for name in sorted(b - a):
                where = f"{base}-{ref}/{name}" if base != "lang" else f"lang/{ref}/{name}"
                (rep.fail if strict else rep.warn)("11.1", where, f"hiányzik (a {lang} oldalon megvan)")
    # a gemini-tükrök: csak fájllista, a tartalmat a sync-gemini-agents.py őrzi
    for lang in langs:
        gem = tree_dir(prompts_dir, "agents", lang) / "gemini-agent"
        ref_gem = tree_dir(prompts_dir, "agents", ref) / "gemini-agent"
        if lang == ref or not ref_gem.is_dir() or not gem.is_dir():
            continue
        a = {d.name for d in ref_gem.iterdir() if d.is_dir()}
        b = {d.name for d in gem.iterdir() if d.is_dir()}
        for name in sorted(a ^ b):
            side = lang if name in a else ref
            (rep.fail if strict else rep.warn)(
                "11.1", f"agents-{side}/gemini-agent/{name}", "féloldalas gemini-tükör")
    return pairs


def check_includes_within_language(prompts_dir, langs, rep):
    """11.3 — horgony ↔ marker kereszt-ellenőrzés. A 9.4 tanulsága: egy vissza nem
    cserélt blokk byte-azonos kimenetet ad, tehát a 16.1 keret vak rá — csak ez a
    leltár mutatja ki.

    A markereket MINDEN nyelv prompt-fájából együtt gyűjtjük: a horgony-nevek
    nyelvfüggetlenek (a marker maga sosem fordul), és a §13 alatt az egyik fa már
    kész lehet, a másik még nem. Ha nyelvenként külön néznénk, a féloldalas
    állapotban minden `lang/en/` horgony árvának látszana — a kapu pedig arra
    tanítana, hogy a FAIL-t ignoráljuk (LG25 indoka).
    A marker-halmazok NYELVEK KÖZÖTTI egyezését a `check_pair` őrzi fájlonként."""
    anchors = {}          # lang -> {"fájl.md#horgony"}
    markers = {}          # "fájl.md#horgony" -> {"skills-hu/02-write-spec.md", …}
    for lang in langs:
        lang_dir = prompts_dir / "lang" / lang
        anchors[lang] = set()
        if lang_dir.is_dir():
            for f in sorted(lang_dir.glob("*.md")):
                text = f.read_text(encoding="utf-8")
                for m in ANCHOR_RE.finditer(text):
                    anchors[lang].add(f"{f.name}#{m.group('name')}")
                if INCLUDE_RE.search(text):
                    rep.fail("11.3", f"lang/{lang}/{f.name}",
                             "a nyelvi blokk INCLUDE markert tartalmaz (8.5 tiltja)")
        for base in BASES:
            d = tree_dir(prompts_dir, base, lang)
            if not d.is_dir():
                continue
            for f in sorted(d.glob("*.md")):
                for m in INCLUDE_RE.finditer(f.read_text(encoding="utf-8")):
                    path = m.group("path")
                    if path.startswith("lang/"):
                        markers.setdefault(path[len("lang/"):], set()).add(f"{d.name}/{f.name}")

    # (a) hivatkozott, de nem létező horgony — nyelvenként, mert a HIÁNYZÓ nyelvi
    #     blokk a telepítéskor csendes `hu` fallbackre esne (LG12)
    for ref, users in sorted(markers.items()):
        for lang in langs:
            if ref not in anchors[lang]:
                rep.fail("11.3", f"lang/{lang}/{ref}",
                         f"hivatkozott, de nem létező horgony — hivatkozza: "
                         f"{', '.join(sorted(users))}")
    # (b) árva horgony — egyetlen nyelv egyetlen prompt-fája sem hivatkozza
    for lang in langs:
        for a in sorted(anchors[lang] - set(markers)):
            rep.fail("11.3", f"lang/{lang}/{a}", "árva horgony — egyetlen marker sem hivatkozza")


def check_descriptions(prompts_dir, langs, ref, rep):
    """11.4 — a `descriptions.json` kulcskészlete PONTOSAN a fa `name` mezőinek
    halmaza legyen, mindkét nyelven; az agent-bejegyzések objektumok
    `description` + `role` kulccsal (LG26)."""
    for lang in langs:
        path = prompts_dir / "lang" / lang / "descriptions.json"
        if not path.exists():
            rep.fail("11.4", f"lang/{lang}/descriptions.json", "hiányzik")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            rep.fail("11.4", f"lang/{lang}/descriptions.json", f"hibás JSON: {exc}")
            continue
        # A `name:` mező byte-azonos a nyelvek között (LG6), ezért a halmazt MINDEN
        # nyelv fájából együtt gyűjtjük. Így a §13 félig lefordított állapotában
        # sem látszik „fölöslegesnek" egy leíró csak azért, mert az adott nyelvre
        # még nem került át a fájl. (A `name:` NYELVEK KÖZÖTTI egyezését a
        # `check_pair` őrzi fájlonként.)
        names, agent_names = set(), set()
        for base in ("skills", "agents"):
            for src_lang in langs:
                d = tree_dir(prompts_dir, base, src_lang)
                if not d.is_dir():
                    continue
                for f in sorted(d.glob("*.md")):
                    fm, _ = frontmatter(f.read_text(encoding="utf-8"))
                    name = fm.get("name", "").strip('"').strip("'")
                    if not name:
                        if src_lang == lang:
                            rep.fail("11.4", f"{d.name}/{f.name}", "hiányzó frontmatter `name:`")
                        continue
                    names.add(name)
                    if base == "agents":
                        agent_names.add(name)
        for extra in sorted(set(data) - names):
            rep.fail("11.4", f"lang/{lang}/descriptions.json",
                     f"'{extra}' bejegyzéshez nincs `name:` a fában")
        for missing in sorted(names - set(data)):
            rep.fail("11.4", f"lang/{lang}/descriptions.json", f"'{missing}' leírója hiányzik")
        for name in sorted(agent_names & set(data)):
            entry = data[name]
            if not isinstance(entry, dict):
                rep.fail("11.4", f"lang/{lang}/descriptions.json",
                         f"'{name}' agent-bejegyzés nem objektum (LG26)")
            elif not entry.get("description") or not entry.get("role"):
                rep.fail("11.4", f"lang/{lang}/descriptions.json",
                         f"'{name}' agent-bejegyzésből hiányzik a description vagy a role (LG26)")


def check_status_keys(prompts_dir, langs, ref, rep):
    """11.5 — a `status-keys.json` kulcs-paritása, és a 10.4 kétigazság-hiba:
    ha a kulcs értéke LITERÁLKÉNT szerepel az egyik nyelv `lang/` blokkjában,
    akkor a párja is szerepeljen a másikéban.

    A meg NEM jelenő kulcs nem hiba: a kulcsok egy része kizárólag
    `<sec:…>` / `<status:…>` token alakban él a prompt-fákban (azt a 11.12
    ellenőrzi), más részüket csak kapu-script olvassa."""
    path = prompts_dir / "lang" / "status-keys.json"
    if not path.exists():
        rep.fail("11.5", "lang/status-keys.json", "hiányzik")
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        rep.fail("11.5", "lang/status-keys.json", f"hibás JSON: {exc}")
        return None
    key_sets = {}
    for lang, groups in data.items():
        key_sets[lang] = {(g, k) for g, ks in groups.items() for k in ks}
    if ref in key_sets:
        for lang, keys in key_sets.items():
            for g, k in sorted(key_sets[ref] - keys):
                rep.fail("11.5", "lang/status-keys.json", f"'{g}:{k}' hiányzik a '{lang}' szeletből")
            for g, k in sorted(keys - key_sets[ref]):
                rep.fail("11.5", "lang/status-keys.json", f"'{g}:{k}' csak a '{lang}' szeletben van")
    for lang in langs:
        if lang == ref or lang not in data or ref not in data:
            continue
        ref_dir, other_dir = prompts_dir / "lang" / ref, prompts_dir / "lang" / lang
        for name in sorted(md_names(ref_dir) & md_names(other_dir)):
            a = (ref_dir / name).read_text(encoding="utf-8")
            b = (other_dir / name).read_text(encoding="utf-8")
            for g in data[ref]:
                for k, ref_val in data[ref][g].items():
                    other_val = data[lang].get(g, {}).get(k)
                    if other_val is None:
                        continue
                    if contains_literal(a, ref_val) and not contains_literal(b, other_val):
                        rep.fail("11.5", f"lang/{lang}/{name}",
                                 f"'{g}:{k}' — a {ref} blokkban ott a {ref_val!r}, "
                                 f"a {lang} blokkból hiányzik a {other_val!r}")
    return data


def check_pair(prompts_dir, base, name, ref, lang, keys, rep):
    """A fájlpárra futó ellenőrzések: 11.3 (marker-halmaz), 11.4 (frontmatter),
    11.6 (szabály-ID), 11.7 (szekció-szerkezet), 11.8 (fence), 11.10
    (imperatívusz), 11.12 (nyelvi token)."""
    a_path = tree_dir(prompts_dir, base, ref) / name
    b_path = tree_dir(prompts_dir, base, lang) / name
    a, b = a_path.read_text(encoding="utf-8"), b_path.read_text(encoding="utf-8")
    where = f"{base}-{lang}/{name}" if base != "lang" else f"lang/{lang}/{name}"

    # 11.3 — a markerek halmaza azonos (a `lang/<f>#<horgony>` a nyelvi mappán
    # belül oldódik fel, ezért a HIVATKOZÁS byte-azonos a két fában)
    ma, mb = Counter(INCLUDE_RE.findall(a)), Counter(INCLUDE_RE.findall(b))
    if ma != mb:
        for marker in sorted(set(ma) | set(mb)):
            if ma[marker] != mb[marker]:
                rep.fail("11.3", where, f"INCLUDE marker eltérés: {marker} "
                         f"({ref}: {ma[marker]}, {lang}: {mb[marker]})")

    # 11.4 — frontmatter
    if base != "lang":
        fa, fb = frontmatter(a)[0], frontmatter(b)[0]
        if fa.get("name") != fb.get("name"):
            rep.fail("11.4", where, f"`name:` eltér ({fa.get('name')!r} vs {fb.get('name')!r}) — "
                     "a slash-parancs azonosítója nem fordul (LG6)")
        la, lb = frontmatter_list_lengths(a), frontmatter_list_lengths(b)
        for key in FM_KEYS:
            if (key in la) != (key in lb):
                rep.fail("11.4", where, f"`{key}:` csak az egyik nyelven van jelen")
            elif key in la and la[key] != lb[key]:
                rep.fail("11.4", where, f"`{key}:` elemszáma eltér ({la[key]} vs {lb[key]})")

    # 11.6 — szabály-ID leltár
    ra, rb = Counter(RULE_ID_RE.findall(a)), Counter(RULE_ID_RE.findall(b))
    for rid in sorted(set(ra) | set(rb)):
        if (ra[rid] > 0) != (rb[rid] > 0):
            side = ref if ra[rid] else lang
            rep.fail("11.6", where, f"a(z) `{rid}` szabály-ID csak a {side} oldalon szerepel")

    # 11.7 — szekció-szerkezet (a címsorok SZINT-sorozata; a szöveg nyelvfüggő)
    ha = [len(m.group(1)) for m in HEADING_RE.finditer(a)]
    hb = [len(m.group(1)) for m in HEADING_RE.finditer(b)]
    if ha != hb:
        rep.fail("11.7", where, f"címsor-szerkezet eltér ({len(ha)} vs {len(hb)} címsor; "
                 f"szint-sorozat {'hossz' if len(ha) != len(hb) else 'sorrend'} eltérés)")

    # 11.8 — fence-paritás (LG27). Az infostring-SOROZAT mindig egyezzen; a
    # tartalom byte-azonossága viszont csak a PROMPT-fákra vonatkozik.
    # A `lang/<L>/` blokkok definíció szerint artefaktum-sablonok: a bennük álló
    # ` ```bash ` fence is projekt-nyelvi (a recept-váz helyőrzői magyarázó
    # szövegek: `<a környezet felhúzása: …>`), és a beemelt slash-parancsok
    # argumentum-címkéi is fordulnak (`ciklus:` → `cycle:`). Ott tehát csak az
    # infostring-sorozatot ellenőrizzük.
    fa_, fb_ = fences(a), fences(b)
    if [i for i, _ in fa_] != [i for i, _ in fb_]:
        rep.fail("11.8", where, f"kódblokk-infostring sorozat eltér "
                 f"({[i for i, _ in fa_]} vs {[i for i, _ in fb_]})")
    elif base != "lang":
        for idx, ((info, ca), (_, cb)) in enumerate(zip(fa_, fb_), 1):
            key = info.split()[0].lower() if info else ""
            if key not in TRANSLATABLE_FENCES and normalize_code(ca) != normalize_code(cb):
                rep.fail("11.8", where, f"a(z) {idx}. `{info}` kódblokk tartalma eltér a "
                         "kommenteken és helyőrzőkön TÚL is — parancsot/kódot nem fordítunk (13.1)")

    # 11.10 — imperatívusz-kapu
    for label, variants in IMPERATIVES.items():
        ca = sum(a.count(v) for v in variants)
        cb = sum(b.count(v) for v in variants)
        if ca != cb:
            rep.fail("11.10", where, f"a(z) `{label}` jelölés darabszáma eltér "
                     f"({ref}: {ca}, {lang}: {cb}) — az utasítás-erősség nem gyengülhet (13.2.2)")

    # 11.12 — nyelvi token-paritás (LG32)
    ta, tb = Counter(TOKEN_RE.findall(a)), Counter(TOKEN_RE.findall(b))
    if ta != tb:
        for tok in sorted(set(ta) | set(tb)):
            if ta[tok] != tb[tok]:
                rep.fail("11.12", where, f"a(z) `<{tok[0]}:{tok[1]}>` token darabszáma eltér "
                         f"({ref}: {ta[tok]}, {lang}: {tb[tok]}) — a fordítás feloldotta literálra?")
    if keys:
        for group, key in sorted(set(ta) | set(tb)):
            for slice_lang in (ref, lang):
                if key not in keys.get(slice_lang, {}).get(TOKEN_GROUPS[group], {}):
                    rep.fail("11.12", where, f"a(z) `<{group}:{key}>` kulcs nincs a "
                             f"status-keys.json '{slice_lang}' szeletében")


def check_unknown_tokens(prompts_dir, langs, keys, rep):
    """11.12 — a féloldalas fákon is: minden token kulcsa létezzen. A
    `check_pair` csak a párokat látja; egy egynyelvű fa tokenjei így is
    átcsúsznának a telepítésig (ahol `exit 1` lenne belőle)."""
    if not keys:
        return
    for lang in langs:
        for base in BASES:
            d = tree_dir(prompts_dir, base, lang)
            if not d.is_dir():
                continue
            for f in sorted(d.glob("*.md")):
                for group, key in sorted(set(TOKEN_RE.findall(f.read_text(encoding="utf-8")))):
                    missing = [s for s in sorted(keys)
                               if key not in keys[s].get(TOKEN_GROUPS[group], {})]
                    if missing:
                        rep.fail("11.12", f"{d.name}/{f.name}",
                                 f"ismeretlen kulcs: `<{group}:{key}>` (nincs a "
                                 f"status-keys.json {', '.join(repr(s) for s in missing)} "
                                 f"szeletében)")


def main():
    parser = argparse.ArgumentParser(
        description="kétnyelvű prompt-fa paritás-kapu (§11)")
    parser.add_argument("--check", action="store_true",
                        help="csendesebb kimenet (csak az eltérések)")
    parser.add_argument("--strict", action="store_true",
                        help="a teljes fájlhalmaz-paritás (11.1) is kötelező (LG25)")
    parser.add_argument("--ref", default="hu",
                        help="a referencia prompt-nyelv (alap: hu)")
    parser.add_argument("--root", default=Path(__file__).resolve().parents[2],
                        help="a repó gyökere (alap: a szkript helyéből számolva)")
    args = parser.parse_args()

    prompts_dir = Path(args.root) / "prompts"
    if not prompts_dir.is_dir():
        print(f"HIBA: nincs {prompts_dir} mappa.", file=sys.stderr)
        return 2

    langs = discover_langs(prompts_dir)
    if not langs:
        print("HIBA: nincs egyetlen nyelvi prompt-fa sem "
              "(prompts/<base>-<lang> vagy prompts/lang/<lang>).", file=sys.stderr)
        return 2
    ref = args.ref if args.ref in langs else langs[0]

    rep = Report()
    check_asymmetry(prompts_dir, rep)
    pairs = check_file_sets(prompts_dir, langs, ref, rep, args.strict)
    check_includes_within_language(prompts_dir, langs, rep)
    check_descriptions(prompts_dir, langs, ref, rep)
    keys = check_status_keys(prompts_dir, langs, ref, rep)
    for base, name, a_lang, b_lang in pairs:
        check_pair(prompts_dir, base, name, a_lang, b_lang, keys, rep)
    check_unknown_tokens(prompts_dir, langs, keys, rep)

    mode = "strict" if args.strict else "default"
    print(f"LANG-PARITY [{mode}] — nyelvek: {', '.join(langs)} (referencia: {ref}) · "
          f"{len(pairs)} fájlpár ellenőrizve")
    if rep.warns and not args.check:
        print(f"\n  WARN ({len(rep.warns)}) — a `--strict` ezekből FAIL-t csinál:")
        for check, where, msg in rep.warns[:40]:
            print(f"    [{check}] {where}: {msg}")
        if len(rep.warns) > 40:
            print(f"    … és további {len(rep.warns) - 40} tétel")
    elif rep.warns:
        print(f"  WARN: {len(rep.warns)} tétel (féloldalas fájl / tükör)")
    if rep.fails:
        print(f"\n  ✗ FAIL ({len(rep.fails)}):")
        for check, where, msg in rep.fails:
            print(f"    [{check}] {where}: {msg}")
        return 1
    print("  ✓ nincs szerkezeti eltérés. (A fordítás JELENTÉS-helyességét ez a kapu "
          "nem ellenőrzi — 11.11.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
