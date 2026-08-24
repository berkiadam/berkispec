#!/usr/bin/env python3
import sys
import os
import json
import re
import shutil
from pathlib import Path

# Az agent azonosítója: Claude/Copilot esetén a fájlnév ("researcher.md"),
# Antigravity esetén az agent.json-t tartalmazó mappa neve ("researcher",
# .md kiterjesztés nélkül) kerül ide. A ".md" levágásával mindkét eset
# ugyanarra a stem-re fut, így a lenti egyezés-listák platformfüggetlenek.
def _agent_stem(filename):
    name = Path(filename).name.lower()
    if name.endswith(".md"):
        name = name[:-3]
    return name

# Konkrét agent-ekhez/skillekhez rendelt models.json kulcs — csak azt kapja
# meg egy stem, amit itt EXPLICIT felsorolunk; minden más a "default" tier-re
# esik. Ez egyetlen, egységes tábla — nincs külön "fázis"-alapú besorolás:
# egy skill (pl. 05-analyze.md, 07-validate.md orchestrátor) önmagában NEM
# kap drága modellt csak azért, mert egy drága subagentet hív.
#
# A "legdrágább" (`deep_reasoning_agent`, jellemzően Opus) tier KIZÁRÓLAG az
# `analyzer` agenst illeti: ez a kereszt-fázisos (spec/plan/tasks/conventions)
# konzisztencia-diagnózis — a legmélyebb, leghosszabb-dokumentumos szintézist
# és ellentmondás-/kétértelműség-keresést igénylő pont a teljes folyamatban,
# és egy itt elkövetett hiba a legdrágább downstream-ben (rossz kód épül rossz
# diagnózisra). Minden más — beleértve a fixer-wrappereket (`spec-fixer`,
# `plan-fixer`, `tasks-fixer`, `implement-fixer`), amik már egy PONTOS,
# előre azonosított hibalistát kapnak (nem nekik kell felfedezni a problémát,
# csak megoldani/eszkalálni azt), és magukat az orchestrátor-skilleket
# (05-analyze, 07-validate) — a `default` tier-en fut. Az `implement-fixer`
# saját anti-"teszt-csalás" garde-ja (06-implement) kifejezetten számol azzal,
# hogy egy olcsóbb LLM futtatja.
#
# A "research_agent" kulcs a legolcsóbb, tisztán mechanikus (nincs benne
# tervezési/architekturális ítélet, sem megbízhatatlanság-érzékeny
# szabadformátumú kimenet-értelmezés) munkára szánt tier:
#   - researcher:     kódbázis-/dokumentum-keresés, fan-out + összefoglalás
#   - cycle-status:    csak egy Python scriptet futtat és megjeleníti (0 LLM-ítélet)
#
# A test-runner (tesztek/Sonar/E2E futtatása + eredmény-összegzés) SZÁNDÉKOSAN
# NINCS ezen a legolcsóbb tier-en (`default`-ra esik): több lépéses
# Bash-orchesztrációt végez (portütközés-kezelés, ideiglenes config
# visszaállítása) és projektenként eltérő formátumú teszt-/Sonar-kimenetet
# kell megbízhatóan összegeznie. Egy elgépelt tesztnév vagy félreolvasott
# Sonar-eredmény csendben elronthatja a 07-validate hurok per-item 3-próba
# számlálóját — ez nagyobb kockázat, mint amit a legolcsóbb tier-nél vállalni
# érdemes.
AGENT_MODEL_KEYS = {
    "researcher": "research_agent",
    "cycle-status": "research_agent",
    "analyzer": "deep_reasoning_agent",
}
# Az `analyzer-exec` (6. kategória: végrehajthatóság) SZÁNDÉKOSAN nincs a deep
# tieren: a mechanikus kapu leltára KÉSZEN adja neki a jelölteket (artefaktumok,
# horgonyok, teszt-ígéretek, destruktív műveletek), tehát nem felfedez, hanem egy
# behatárolt listát ítél meg — ez a `default` tier munkája. A felfedező, hosszú
# dokumentumos szintézis maradt az `analyzer`-nél.

# Cursor subagent `readonly: true` — CSAK azok az agentek, amelyek biztosan
# SEMMIT nem írnak (a prózájuk is kimondja: „Read-only vagy"): tisztán a hívó
# skillnek adnak vissza megállapítást/összefoglalót, fájlt nem hoznak létre.
# FIGYELEM: a tool-lista nem megbízható jelzés — a `reviewer` (test-report/code-review.md)
# és a `test-runner` (report-mappa/config) Bash-en keresztül ÍR, hiába nincs a
# tool-listájukban Edit/Write; ezért ők NINCSENEK itt. Téves readonly=true
# megtörné őket.
READONLY_AGENTS = {"analyzer", "analyzer-exec", "researcher", "doc-sync-planner"}

# A models.json szerkezete (platformonként):
#
#   "<platform>": {
#     "deep_reasoning_agent": { "model": <str>, "effort": <str> },
#     "default":              { "model": <str>, "effort": <str> },
#     "research_agent":       { "model": <str>, "effort": <str> },
#     "<agent-stem>":         { "effort": <str> }   # opcionális felülírás(ok)
#   }
#
# Két, egymástól FÜGGETLEN tengely:
#   - MODELL: melyik modell fut. Az agent → tier hozzárendelést az
#     AGENT_MODEL_KEYS adja (analyzer → deep, researcher/cycle-status →
#     research); minden más a `default` tier modelljét kapja.
#   - EFFORT: mennyit "gondolkodik" (thinking-token). Ez NEM esik egybe a
#     modell-tierrel — pl. a fixerek a `default` MODELLEN futnak, de `low`
#     EFFORT jár nekik. Ezért a defaulttól eltérő efforttal bíró agentek a
#     models.json-ban SAJÁT NEVŰ bejegyzésként szerepelnek, csak az `effort`
#     mezővel (a modelljük a default tierből jön).
#
# Feloldási szabály egy agentre (stem):
#   model  = <saját nevű bejegyzés>.model  ha van, különben
#            AGENT_MODEL_KEYS[stem] tier .model, különben default.model
#   effort = <saját nevű bejegyzés>.effort ha van, különben
#            AGENT_MODEL_KEYS[stem] tier .effort, különben default.effort
#
# Így ha egy agentnél a modell nincs külön megadva → default modell; ha az
# effort nincs → az adott tier (vagy a default) effortja. A default effort a
# models.json-ban `high` (biztonságos, mély alapértelmezés).
#
# Az effort NATÍVAN a Claude Code subagent-frontmatter `effort:` mezőjében
# hat. Az Antigravity (agent.json), a Copilot és a Cursor configba is kiírjuk
# (natív mező + látható "Recommended Effort" alert), hogy platformtól
# függetlenül egyetlen helyről (models.json) legyen hangolható.

def _resolve_agent_config(models, platform, filename):
    """Feloldja egy agent (model, effort) párját a fenti szabály szerint.
    Visszaad: (model_str, effort_str)."""
    platform_models = models.get(platform, {})
    stem = _agent_stem(filename)

    override = platform_models.get(stem, {})
    if not isinstance(override, dict):
        override = {}

    tier_key = AGENT_MODEL_KEYS.get(stem, "default")
    tier = platform_models.get(tier_key)
    if not isinstance(tier, dict):
        tier = {}
    default_tier = platform_models.get("default", {})
    if not isinstance(default_tier, dict):
        default_tier = {}

    model = override.get("model") or tier.get("model") or default_tier.get("model", "")

    if "effort" in override:
        effort = override["effort"]
    elif "effort" in tier:
        effort = tier["effort"]
    else:
        effort = default_tier.get("effort", "high")

    return model, effort

def get_model(models, platform, filename):
    model, _ = _resolve_agent_config(models, platform, filename)
    return model

def get_effort(models, platform, filename):
    _, effort = _resolve_agent_config(models, platform, filename)
    return effort

# ── Nyelvi tengelyek (két független beállítás) ─────────────────────────────
# MINDKETTŐ BUILD-TIME beállítás: a telepítés pillanatában dől el, és utána
# nyomtalan — semmilyen runtime-nak (sem a scripteknek, sem a
# `conventions.md`-nek) nem kell tudnia róla. A kettő között NEM az a
# különbség, hogy melyik mikor hat, hanem a HATÓKÖRÜK:
#
# `PROMPT_LANG`  — a PROMPT nyelve: melyik forrás-fából telepítünk
#                  (`prompts/skills-hu` = hu, `prompts/skills-en` = en).
#                  Hatóköre az AGENSNEK szóló instrukciós szöveg. MINDKÉT
#                  nyelv prefixelt mappában él — nincs kitüntetett, suffix
#                  nélküli fa (LG5).
# `PROJECT_LANG` — a PROJEKT nyelve: a `<!-- INCLUDE:lang/... -->` markerek
#                  feloldását választja (`prompts/lang/<lang>/`). Ez a mappa
#                  szándékosan NEM a `shared-<L>/` alatt van: nem a
#                  prompt-nyelvvel mozog, tehát ott duplikáció lenne.
#                  Hatóköre minden, ami a PROJEKTBE kerül vagy a
#                  FELHASZNÁLÓHOZ szól: szó szerint kimondandó mondatok,
#                  fájlba írt sablonok, státusz-kulcsszavak.
#
# A kettő ORTOGONÁLIS: az `en` prompt + `hu` projekt kombináció a fő use case
# (a prompt tokenben olcsóbb, a leadandó magyar marad).
PROMPT_LANG = "hu"
PROJECT_LANG = "hu"
SUPPORTED_LANGS = ("hu", "en")

# A `hu` a fordítás kanonikus forrás-fája, a mappanevekben viszont TELJES A
# SZIMMETRIA (LG5): mindkét nyelv prefixelt mappában él (`skills-hu` /
# `skills-en`), nincs kitüntetett, suffix nélküli fa. Az aszimmetria csendes
# hibát szülne: egy `skills/`-be írt javítás úgy nézne ki, mintha
# nyelvfüggetlen lenne.
def _lang_subdir(base, lang):
    return f"{base}-{lang}"

def skills_src_dir(src_dir):
    """A prompt-nyelv szerinti skill-forrásmappa."""
    return Path(src_dir) / "prompts" / _lang_subdir("skills", PROMPT_LANG)

def agents_src_dir(src_dir, gemini=False):
    """A prompt-nyelv szerinti agent-forrásmappa (a gemini-agent alfa is)."""
    base = Path(src_dir) / "prompts" / _lang_subdir("agents", PROMPT_LANG)
    return base / "gemini-agent" if gemini else base

# Minden helper scriptet (prompts/scripts/*.py) átmásol a cél scripts_dest
# mappába, kivéve saját magát (install-helper.py, ami csak a telepítő gépén
# fut, a célprojektben nincs rá szükség). Így új helper script (pl.
# ds22-gate-check.py) hozzáadásakor nem kell mindhárom process_* függvényt
# külön bővíteni.
def copy_helper_scripts(src_dir, scripts_dest):
    scripts_dest.mkdir(parents=True, exist_ok=True)
    scripts_src_dir = Path(src_dir) / "prompts/scripts"
    for script_src in sorted(scripts_src_dir.glob("*.py")):
        # A repó-karbantartó szkriptek nem a célprojekt eszközei
        if script_src.name in ("install-helper.py", "sync-gemini-agents.py"):
            continue
        script_dest = scripts_dest / script_src.name
        shutil.copy(script_src, script_dest)
        os.chmod(script_dest, 0o755)

# ── Közös leírás-részletek build-time inline-olása a skillekbe (BD13/BD14) ────
# A skillek `<!-- INCLUDE:shared/<fájl> -->` markert tartalmazhatnak. Mivel a
# skillek platformonként eltérő helyre települnek, egy relatív hivatkozás
# futásidőben nem oldódna fel egységesen — ezért a telepítő a marker helyére
# a `prompts/shared-<PROMPT_LANG>/<fájl>` tartalmát ILLESZTI BE (build-time include), így a
# telepített SKILL.md önmagában teljes. A megosztott fájl elején lévő
# magyarázó HTML-kommentet (forrás-jegyzet) nem visszük át.
# ── A `<platform-scripts-mappa>` helyőrző feloldása (BD15) ────────────────────
# A skillek helper-szkripteket hívnak (`failure-counter.py`, `run-tests.py`,
# `round-log.py`, …), de a szkriptek platformonként MÁS mappába települnek.
# Ha a helyőrző a telepített SKILL.md-ben marad, az ágensnek ki kell találnia az
# útvonalat — egy gyengébb modell ilyenkor rossz helyre nyúl, vagy köröket
# pazarol a kereséssel. Ezért a telepítő a KONKRÉT, projektgyökérhez képest
# relatív útvonalra cseréli, platformonként.
SCRIPTS_DIR_BY_PLATFORM = {
    "claude": ".claude/scripts",
    "antigravity": ".agents/scripts",
    "codex": ".codex/scripts",
    "copilot": ".github/scripts",
    "cursor": ".cursor/scripts",
}
_SCRIPTS_DIR_PLACEHOLDER = "<platform-scripts-mappa>"


def substitute_scripts_dir(content, platform):
    """A `<platform-scripts-mappa>` helyőrző cseréje a platform tényleges
    scripts-mappájára. Ismeretlen platformnál változatlanul hagyja (a skill
    szövege ilyenkor is értelmes marad)."""
    target = SCRIPTS_DIR_BY_PLATFORM.get(platform)
    if not target:
        return content
    return content.replace(_SCRIPTS_DIR_PLACEHOLDER, target)


# A marker körüli vízszintes whitespace KÜLÖN csoportban van, mert kétféleképpen
# kell bánni vele (lásd `_marker_is_standalone`):
#   - a saját sorában álló marker esetén a behúzás és a sorvégi szóköz ELTŰNIK a
#     beillesztett blokkal együtt (ez a 8.1 óta a normál, blokk-szintű eset);
#   - a SOR KÖZEPÉN álló markernél viszont meg kell ŐRIZNI, különben a marker
#     elnyeli az előtte lévő szóközt (`A: <!-- … -->` → `A:<blokk>`). Erre a 9.4
#     kiemelésnek van szüksége: a user-facing, szó szerint kimondandó mondatok
#     jellemzően egy felsorolás-pont KÖZEPÉN állnak, körülöttük instrukcióval.
_INCLUDE_MARKER_RE = re.compile(
    r'(?P<lead>[ \t]*)<!--\s*INCLUDE:\s*(?P<path>[^\s]+?)\s*-->(?P<trail>[ \t]*)')
_shared_include_cache = {}

_lang_fallback_warned = set()

def _resolve_include_path(src_dir, rel_path):
    """A marker útvonalát fizikai fájlra oldja fel.

    - `shared/<f>`  → `prompts/shared-<PROMPT_LANG>/<f>` — a PROMPT-nyelvvel mozog (instrukciós blokk,
      a prompt-nyelvvel együtt mozog, mert a hivatkozó fa is nyelvi).
    - `lang/<f>`    → `prompts/lang/<PROJECT_LANG>/<f>` — PROJEKT-nyelvű
      blokk: kimondandó mondatok, fájlba írt sablonok, státusz-kulcsszavak.

    Ha a projekt-nyelvi változat még nem létezik (a kétnyelvűsítés fázisos),
    `hu`-ra esünk vissza **hangos figyelmeztetéssel** — a telepítés nem törik
    meg, de a vegyes nyelv nem marad csendben.
    """
    if rel_path.startswith("lang/"):
        name = rel_path[len("lang/"):]
        primary = Path(src_dir) / "prompts/lang" / PROJECT_LANG / name
        if primary.exists() or PROJECT_LANG == "hu":
            return primary
        fallback = Path(src_dir) / "prompts/lang/hu" / name
        if fallback.exists() and name not in _lang_fallback_warned:
            _lang_fallback_warned.add(name)
            print(f"  FIGYELEM: a(z) '{name}' projekt-nyelvi blokk nincs meg "
                  f"'{PROJECT_LANG}' nyelven — magyar változat kerül be.")
        return fallback
    if rel_path.startswith("shared/"):
        name = rel_path[len("shared/"):]
        return Path(src_dir) / "prompts" / _lang_subdir("shared", PROMPT_LANG) / name
    return Path(src_dir) / "prompts" / rel_path

def _extract_anchor_section(text, anchor, include_path):
    """A `## <anchor>` címsortól a KÖVETKEZŐ `## ` szintű címsorig tartó törzs.

    A horgony nélküli eset (teljes fájl) és ez a két hibakezelés SZÁNDÉKOSAN
    különbözik (lásd `inline_shared_includes`):
      - nem létező FÁJL  → a marker érintetlenül marad, a telepítés nem törik;
      - létező fájl + nem létező HORGONY → `sys.exit(1)`.
    Egy user-facing mondat vagy egy fájlba írandó sablon csendes kihagyása
    súlyosabb, mint megállni: az elsőt a felhasználó azonnal látja a
    telepítés végén, a másodikat csak hetekkel később, egy hibás artefaktumban.
    """
    lines = text.split('\n')
    start = None
    for i, line in enumerate(lines):
        if line.strip() == f"## {anchor}":
            start = i + 1
            break
    if start is None:
        print(f"HIBA: a '{anchor}' horgony nincs meg a(z) {include_path} fájlban.",
              file=sys.stderr)
        print("       A nyelvi blokkok horgonyai: `## <szabály-ID>-<rövid-név>`.",
              file=sys.stderr)
        sys.exit(1)
    end = len(lines)
    for i in range(start, len(lines)):
        if lines[i].startswith('## '):
            end = i
            break
    return '\n'.join(lines[start:end]).strip('\n')


def _read_shared_include(src_dir, rel_path):
    """Beolvassa és cache-eli a marker által hivatkozott blokk tartalmát, a
    vezető magyarázó HTML-kommentet levágva. A cache kulcsa tartalmazza a
    projekt-nyelvet ÉS a prompt-nyelvet, mert a `lang/` markerek feloldása az
    egyiktől, a `shared/` markereké a másiktól függ.

    A marker útvonala `<fájl>#<horgony>` alakú is lehet (8.1/8.2) — ilyenkor a
    fájlnak csak a `## <horgony>` szekciója kerül be. Erre a projekt-nyelvi
    blokkoknál van szükség: fájlonként EGY nyelvi fájl, sok horgonnyal."""
    file_part, _, anchor = rel_path.partition('#')
    key = (str(src_dir), file_part, anchor, PROMPT_LANG, PROJECT_LANG)
    if key in _shared_include_cache:
        return _shared_include_cache[key]
    include_path = _resolve_include_path(src_dir, file_part)
    with open(include_path, 'r', encoding='utf-8') as f:
        text = f.read()
    # Vezető <!-- ... --> blokk (forrás-jegyzet) eltávolítása
    text = re.sub(r'^\s*<!--.*?-->\s*', '', text, count=1, flags=re.DOTALL)
    if anchor:
        text = _extract_anchor_section(text, anchor, include_path)
    else:
        text = text.strip('\n')
    _shared_include_cache[key] = text
    return text

# ── PROJEKT-nyelvi frontmatter: `description` + `role` (LG15/LG26) ──────────
# A frontmatterbe nem lehet INCLUDE-olni, ezért ez a két mező build-time
# BEHELYETTESÍTÉSSEL kerül be a `prompts/lang/<PROJECT_LANG>/descriptions.json`-ból.
# Miért a PROJEKT nyelve és nem a promptok nyelve: ezzel a mezővel illeszti az
# agent a FELHASZNÁLÓ kérését a skillhez/subagenthez, a felhasználó pedig a
# projekt nyelvén ír. `EN` prompt + `HU` projekt esetén tehát magyar leíró kell,
# különben kereszt-nyelvi illesztés történik — ami pont a gyenge modelleken
# romlik el. A kulcs a frontmatter `name` mezője, ami NEM fordul (LG6), tehát
# stabil. Agentnél az érték objektum: {"description": …, "role": …} — a `role`
# is illesztő-felület, sőt a markdown-agent kódút a `description`-t ebből írja.
_descriptions_cache = {}


def load_descriptions(src_dir):
    """A projekt-nyelvi leírások betöltése, cache-elve. Hiányzó nyelvi fájl
    esetén `hu` fallback hangos figyelmeztetéssel (LG12); ha a `hu` sincs meg,
    megállunk — leíró nélkül a skillek gyakorlatilag meghívhatatlanok."""
    key = (str(src_dir), PROJECT_LANG)
    if key in _descriptions_cache:
        return _descriptions_cache[key]
    path = Path(src_dir) / "prompts/lang" / PROJECT_LANG / "descriptions.json"
    if not path.exists():
        fallback = Path(src_dir) / "prompts/lang/hu/descriptions.json"
        if not fallback.exists():
            print(f"HIBA: nincs meg a {path} és a magyar tartalék sem.", file=sys.stderr)
            sys.exit(1)
        print(f"  FIGYELEM: a descriptions.json nincs meg '{PROJECT_LANG}' nyelven "
              f"— magyar leírók kerülnek be.")
        path = fallback
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    _descriptions_cache[key] = data
    return data


_FM_FIELD_RE_CACHE = {}


def _yaml_quoted(value):
    """Egysoros, idézőjelezett YAML skalár — a mai frontmatterek formája."""
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ') + '"'


def _replace_fm_field(content, field, value):
    """A frontmatter `<field>:` sorát cseréli. Csak az ELSŐ `---` blokkban
    keres, hogy a törzsben lévő azonos kezdetű sorokat ne bántsa."""
    lines = content.split('\n')
    if not lines or lines[0].strip() != '---':
        return content, False
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            break
        if lines[i].startswith(field + ':'):
            lines[i] = f"{field}: {_yaml_quoted(value)}"
            return '\n'.join(lines), True
    return content, False


def substitute_lang_frontmatter(content, src_dir, kind, source_name):
    """A `description` (skill) ill. `description` + `role` (agent) mező cseréje a
    projekt-nyelvi értékre. Hiányzó kulcs → `sys.exit(1)`: leíró nélkül a skill
    nem triggerel, tehát a csendes átengedés súlyosabb, mint a megállás."""
    data = load_descriptions(src_dir)
    lines = content.split('\n')
    name = ""
    if lines and lines[0].strip() == '---':
        for line in lines[1:]:
            if line.strip() == '---':
                break
            if line.startswith('name:'):
                name = line[len('name:'):].strip().strip('"').strip("'")
                break
    if not name:
        return content  # nincs frontmatter `name` — nincs mit illeszteni
    if name not in data:
        print(f"HIBA: a '{name}' ({source_name}) nincs a projekt-nyelvi "
              f"descriptions.json-ban.", file=sys.stderr)
        print("       Minden skill és agent `name`-jéhez kell leíró (11.4 kapu).",
              file=sys.stderr)
        sys.exit(1)
    entry = data[name]
    if kind == 'agent':
        if not isinstance(entry, dict):
            print(f"HIBA: a '{name}' agent-bejegyzésnek objektumnak kell lennie "
                  f'({{"description": …, "role": …}}).', file=sys.stderr)
            sys.exit(1)
        content, _ = _replace_fm_field('\n'.join(lines), 'description', entry['description'])
        if entry.get('role'):
            content, _ = _replace_fm_field(content, 'role', entry['role'])
        return content
    if isinstance(entry, dict):
        entry = entry.get('description', '')
    content, _ = _replace_fm_field('\n'.join(lines), 'description', entry)
    return content


def prepare_skill_content(skill_file, src_dir, platform):
    """MINDEN skill-transzformáció egy helyen (8.7). Két skill-író kódút van
    (`write_markdown_skill` és a `process_copilot` saját ciklusa), és korábban
    mindegyik maga hívta a lépéseket — ez előbb-utóbb elcsúszott volna. Sorrend:
    projekt-nyelvi frontmatter → INCLUDE-feloldás → scripts-mappa helyőrző."""
    with open(skill_file, 'r', encoding='utf-8') as f:
        content = f.read()
    if src_dir is not None:
        content = substitute_lang_frontmatter(content, src_dir, 'skill', skill_file.name)
        content = inline_shared_includes(content, src_dir)
    return substitute_scripts_dir(content, platform)


def prepare_agent_content(agent_file, src_dir, platform):
    """Ugyanaz az agent-promptokra: a `description` ÉS a `role` is projekt-nyelvi
    (LG26). Mind a négy agent-kódút ezt használja."""
    with open(agent_file, 'r', encoding='utf-8') as f:
        content = f.read()
    if src_dir is not None:
        content = substitute_lang_frontmatter(content, src_dir, 'agent', agent_file.name)
        content = inline_shared_includes(content, src_dir)
    return substitute_scripts_dir(content, platform)


_MAX_INCLUDE_DEPTH = 5

def _marker_is_standalone(match):
    """Igaz, ha a marker (a körülötte lévő vízszintes whitespace-szel együtt) a
    saját sorát tölti ki — tehát sem előtte, sem utána nincs más tartalom a
    sorban. Csak ilyenkor szabad a whitespace-t elnyelni."""
    text = match.string
    before = text.rfind("\n", 0, match.start()) + 1
    after = text.find("\n", match.end())
    if after == -1:
        after = len(text)
    return not text[before:match.start()].strip() and not text[match.end():after].strip()

def inline_shared_includes(content, src_dir, _depth=0):
    """A skill törzsében lévő `<!-- INCLUDE:shared/... -->` markereket a
    hivatkozott fájl tartalmára cseréli. Ha egy marker fájlja nem található,
    a markert érintetlenül hagyja (a telepítés nem törik meg).

    A behelyezett fájl maga is tartalmazhat INCLUDE markert (BD14/b) — ezt
    rekurzívan oldjuk fel, `_MAX_INCLUDE_DEPTH` mélységig. Erre a fix-mód
    fájloknak van szüksége: a `shared/fix-mode-*.md` beemeli a hozzá tartozó
    `shared/quality-check-*.md`-t, hogy a fixer-subagent prompt önmagában
    teljes legyen, és ne kelljen a teljes fázis-skillt beolvasnia."""
    if _depth >= _MAX_INCLUDE_DEPTH:
        return content
    def _repl(match):
        rel_path = match.group('path')
        try:
            included = _read_shared_include(src_dir, rel_path)
        except OSError:
            return match.group(0)
        resolved = inline_shared_includes(included, src_dir, _depth + 1)
        if _marker_is_standalone(match):
            return resolved
        return match.group('lead') + resolved + match.group('trail')
    return _INCLUDE_MARKER_RE.sub(_repl, content)

def _build_alert(model, platform_name, effort=None):
    lines = [f"> **Recommended Model ({platform_name}):** {model}"]
    if effort is not None:
        lines.append(f"> **Recommended Effort ({platform_name}):** {effort}")
    return "> [!IMPORTANT]\n" + "\n".join(lines) + "\n\n"

# A `model` mindig injektálódik (frontmatter mező + látható alert). Az `effort`
# opcionális: ha None (pl. skilleknél, amik az orchestrátor-fő ágensek, nem
# subagentek), nem kerül be — csak az agenteknél adjuk át.
def inject_markdown_model(content, model, platform_name, effort=None):
    parts = content.split('---')
    if len(parts) >= 3:
        frontmatter = parts[1]
        body = '---'.join(parts[2:])

        # Inject model: <model> (és opcionálisan effort:) a frontmatterbe
        lines = frontmatter.splitlines()
        model_found = False
        effort_found = False
        new_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('model:'):
                new_lines.append(f"model: {model}")
                model_found = True
            elif effort is not None and stripped.startswith('effort:'):
                new_lines.append(f"effort: {effort}")
                effort_found = True
            else:
                new_lines.append(line)
        if not model_found:
            new_lines.append(f"model: {model}")
        if effort is not None and not effort_found:
            new_lines.append(f"effort: {effort}")
        new_frontmatter = '\n'.join(new_lines)

        # Also inject visual warning alert block into body
        alert = "\n" + _build_alert(model, platform_name, effort)
        return f"---{new_frontmatter}\n---{alert}{body.lstrip()}"
    else:
        # No frontmatter, construct frontmatter with model (+ effort)
        fm = f"model: {model}"
        if effort is not None:
            fm += f"\neffort: {effort}"
        alert = _build_alert(model, platform_name, effort)
        return f"---\n{fm}\n---\n{alert}{content.lstrip()}"

# Cursor Agent subagent (.cursor/agents/*.md): a szokásos model/effort + alert
# injektálás, majd a Cursor-subagent által elvárt mezők pótlása:
#   - description: az automatikus delegáláshoz KRITIKUS (a `role:` mezőből
#     származtatjuk, ha nincs külön megadva);
#   - readonly: true, ha az agent a READONLY_AGENTS allowlisten van (biztosan
#     semmit nem ír) — így Cursorban sem tud véletlenül írni.
# A Cursor NEM ismer külön `effort:` frontmatter-mezőt: a modell azonosítója
# maga hordozza a paramétereket szögletes zárójeles jelöléssel —
# `model: <model-id>[effort=high]` (több paraméter vesszővel: `[effort=high,context=300k]`).
# Ezért a models.json cursor-szekciójában MODELL-AZONOSÍTÓT kell megadni
# (`claude-opus-5`), nem megjelenített nevet („Opus 4.8"), az effortot pedig
# ide fűzzük hozzá. Érvénytelen azonosító esetén a Cursor csendben a szülő
# ágens modelljére esik vissza — a hiba nem látszik, csak a viselkedésen.
def inject_cursor_agent(content, model, effort, readonly=False):
    model_spec = f"{model}[effort={effort}]" if effort else model
    injected = inject_markdown_model(content, model_spec, "Cursor")
    parts = injected.split('---')
    if len(parts) < 3:
        return injected

    frontmatter = parts[1]
    body = '---'.join(parts[2:])
    lines = frontmatter.splitlines()

    role = ""
    have_desc = False
    have_readonly = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('role:'):
            role = stripped[len('role:'):].strip().strip('"')
        elif stripped.startswith('description:'):
            have_desc = True
        elif stripped.startswith('readonly:'):
            have_readonly = True

    if not have_desc:
        lines.append(f'description: {role or "BerkiSpec agent"}')
    if readonly and not have_readonly:
        lines.append('readonly: true')

    return f"---{chr(10).join(lines)}\n---{body}"

# A skillek (orchestrátor fő ágensek, NEM subagentek) SZÁNDÉKOSAN nem kapnak
# modell-injektálást egyetlen platformon sem. Indok: a skill-szintű `model` mező
# NEM része az Agent Skills alap-szabványnak (az csak name/description/license/
# compatibility/metadata/allowed-tools) — Claude Code-kiterjesztés. A célplatformok
# vagy egyáltalán nem ismerik (Codex SKILL.md = csak name+description; Copilot
# instructions = csak applyTo; Antigravity = a `model` az AGENT mezője, nem a skillé;
# Cursor = a `model`-kiterjesztést legfeljebb részlegesen), vagy — Claude Code
# esetén — a dokumentáció ígéri, de runtime-ban NEM hat (anthropics/claude-code
# #45191, "not planned"-ként lezárva). Egy beírt skill-`model` így a legjobb
# esetben inert, a legrosszabb esetben félrevezető (nem létező képességet sugall).
# A modellváltás KIZÁRÓLAG az agentek/subagentek szintjén hat megbízhatóan (Claude
# subagent model/effort, Codex TOML model/model_reasoning_effort) — ott marad meg.
def write_markdown_skill(skill_file, skills_dest, src_dir=None, platform=None):
    """Skill másolása modell-injektálás NÉLKÜL a <skills_dest>/bs-<stem>/SKILL.md alá.
    Minden tartalmi transzformáció a közös `prepare_skill_content()`-ben él
    (8.7), hogy a Copilot saját skill-ciklusa se csússzon el tőle."""
    content = prepare_skill_content(skill_file, src_dir, platform)
    skill_dest_dir = skills_dest / f"bs-{skill_file.stem}"
    skill_dest_dir.mkdir(parents=True, exist_ok=True)
    with open(skill_dest_dir / "SKILL.md", 'w', encoding='utf-8') as f:
        f.write(content)

# ── Codex CLI (.codex/agents/*.toml + .agents/skills/) ──────────────────────
# A Codex subagentek NEM markdownok, hanem TOML-fájlok (.codex/agents/<n>.toml).
# A hivatalos spec szerint minden mező, ami a config.toml-ben él, itt is megadható;
# a `model` és a `model_reasoning_effort` NATÍVAN hat (a fájlban megadott érték
# elsőbbséget élvez a spawn-/[agents]-default/parent érték felett). A read-only
# agentek (READONLY_AGENTS) `sandbox_mode = "read-only"`-t kapnak. A markdown
# agent-prompt teljes törzse a `developer_instructions` mezőbe kerül, elé a
# szokásos "Recommended" alerttel (a modell/effort natív, de a láthatóság kedvéért
# ott is jelezzük, egységesen a többi platformmal).
#
# A skillek viszont a `.agents/skills/`-be kerülnek (bs-<n>/SKILL.md): a Codex a
# PROJEKT-szintű skilleket innen olvassa — a `.codex/skills` csak legacy,
# user-szintű hely, projekt-szinten NEM található meg. Ez a mappa UGYANAZ, mint
# az Antigravity-é; a telepítő ezért kölcsönösen kizárja a két platform egyidejű
# telepítését ugyanabba a projektbe (lásd install.sh / install.ps1).

def _split_agent_markdown(content):
    """Visszaadja az agent markdown (name, role, description, body) négyesét. A
    body a frontmatter utáni teljes törzs (a --- lezárás után). A `description`
    az agent-regisztráció kanonikus mezője; ha nincs, a `role`-ra esünk vissza."""
    parts = content.split('---')
    if len(parts) >= 3:
        frontmatter = parts[1]
        body = '---'.join(parts[2:]).lstrip('\n')
        name = ""
        role = ""
        description = ""
        for line in frontmatter.splitlines():
            stripped = line.strip()
            if stripped.startswith('name:'):
                name = stripped[len('name:'):].strip().strip('"').strip("'")
            elif stripped.startswith('role:'):
                role = stripped[len('role:'):].strip().strip('"').strip("'")
            elif stripped.startswith('description:'):
                description = stripped[len('description:'):].strip().strip('"').strip("'")
        return name, role, description, body
    return "", "", "", content

def _toml_basic_string(s):
    """TOML basic (egysoros) string, escape-elve."""
    s = s.replace('\\', '\\\\').replace('"', '\\"')
    s = s.replace('\r', '').replace('\n', '\\n').replace('\t', '\\t')
    return f'"{s}"'

def _toml_multiline_string(s):
    """TOML többsoros string a hosszú törzshöz. Alapból literal ('''…'''), ami
    NEM dolgoz fel escape-eket (a markdown \\ és " karakterei érintetlenek
    maradnak); ha a törzs tartalmaz ''' szekvenciát, basic (\"\"\"…\"\"\")
    változatra esünk vissza, escape-eléssel. A nyitó delimiter utáni azonnali
    újsort a TOML lenyeli, ezért szándékosan újsorral kezdünk/zárunk."""
    if "'''" not in s:
        return "'''\n" + s + "\n'''"
    esc = s.replace('\\', '\\\\').replace('"""', '\\"\\"\\"')
    return '"""\n' + esc + '\n"""'

def _build_codex_agent_toml(name, description, model, effort, developer_instructions, readonly):
    lines = [
        f"name = {_toml_basic_string(name)}",
        f"description = {_toml_basic_string(description)}",
    ]
    if model:
        lines.append(f"model = {_toml_basic_string(model)}")
    if effort:
        lines.append(f"model_reasoning_effort = {_toml_basic_string(effort)}")
    if readonly:
        lines.append('sandbox_mode = "read-only"')
    lines.append(f"developer_instructions = {_toml_multiline_string(developer_instructions)}")
    return "\n".join(lines) + "\n"

def process_codex(src_dir, dest_path, models):
    dest_path = Path(dest_path)
    agents_src = agents_src_dir(src_dir)
    skills_src = skills_src_dir(src_dir)

    # 1. Agents → .codex/agents/<stem>.toml (TOML subagent formátum)
    agents_dest = dest_path / ".codex/agents"
    agents_dest.mkdir(parents=True, exist_ok=True)

    for agent_file in agents_src.glob("*.md"):
        stem = _agent_stem(agent_file.name)
        model = get_model(models, "codex", agent_file.name)
        effort = get_effort(models, "codex", agent_file.name)
        readonly = stem in READONLY_AGENTS

        # A subagent-promptok is kaphatnak `<!-- INCLUDE:shared/... -->` markert
        # (BD14), és a `description`/`role` a PROJEKT nyelvét követi (LG26) —
        # mindkettőt a közös prepare_agent_content() végzi.
        content = prepare_agent_content(agent_file, src_dir, "codex")

        name, role, description, body = _split_agent_markdown(content)
        agent_name = name or stem
        description = description or role or "BerkiSpec agent"
        developer_instructions = _build_alert(model, "Codex", effort) + body

        toml_text = _build_codex_agent_toml(
            agent_name, description, model, effort, developer_instructions, readonly
        )
        with open(agents_dest / f"{stem}.toml", 'w', encoding='utf-8') as f:
            f.write(toml_text)

    # 2. Skills → .agents/skills/bs-<name>/SKILL.md (a Codex innen olvassa)
    skills_dest = dest_path / ".agents/skills"
    skills_dest.mkdir(parents=True, exist_ok=True)

    for skill_file in skills_src.glob("*.md"):
        write_markdown_skill(skill_file, skills_dest, src_dir, "codex")

    # 3. Helper scripts → .codex/scripts/
    scripts_dest = dest_path / ".codex/scripts"
    copy_helper_scripts(src_dir, scripts_dest)

def process_antigravity(src_dir, dest_path, models):
    dest_path = Path(dest_path)
    agents_src = agents_src_dir(src_dir, gemini=True)
    skills_src = skills_src_dir(src_dir)
    
    # 1. Process agents
    agents_dest = dest_path / ".agents/agents"
    agents_dest.mkdir(parents=True, exist_ok=True)
    
    for agent_dir in agents_src.iterdir():
        if not agent_dir.is_dir():
            continue
        agent_name = agent_dir.name
        agent_json_src = agent_dir / "agent.json"
        if not agent_json_src.exists():
            continue
            
        model = get_model(models, "antigravity", agent_name)
        effort = get_effort(models, "antigravity", agent_name)

        with open(agent_json_src, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Az Antigravity `model` mezője MODELL-TIER enum (`inherit` / `flash` /
        # `pro`), nem modellnév: egy "Claude Opus 4.6" érték érvénytelen, és a
        # subagent az `inherit` alapértelmezésre esik vissza (a szülő ágens
        # modelljén fut). Ezért a models.json antigravity-szekciójába tiert kell
        # írni. Külön `effort` mező nincs a sémában — csak látható ajánlásként
        # (alert) tesszük ki, a JSON-ba nem írjuk, hogy ne sugalljon nem létező
        # képességet.
        data["model"] = model

        # A `description` a PROJEKT nyelvét követi (LG26); a mai tükörben ez a
        # markdown `role:` mezőjével egyezik, ezért abból jön. (A `displayName`
        # az agent NEVE, nem leíró — azt nem fordítjuk, LG6.) Az agent.json a prompt-nyelvű
        # gemini-tükörből jön, ezért itt build-time cseréljük — különben
        # `EN` prompt + `HU` projekt esetén angol leíró illesztené a magyar
        # felhasználói kérést.
        _lang_entry = load_descriptions(src_dir).get(agent_name)
        if isinstance(_lang_entry, dict):
            data["description"] = _lang_entry.get("role") or _lang_entry["description"]
        elif _lang_entry is None:
            print(f"HIBA: a '{agent_name}' nincs a projekt-nyelvi descriptions.json-ban.",
                  file=sys.stderr)
            sys.exit(1)

        try:
            sections = data["customAgentSpec"]["customAgent"]["systemPromptSections"]
            for section in sections:
                if section.get("title") == "Instructions":
                    content = inline_shared_includes(section.get("content", ""), src_dir)
                    content = substitute_scripts_dir(content, "antigravity")
                    section["content"] = _build_alert(model, "Antigravity", effort) + content
        except KeyError:
            pass
            
        agent_dest_dir = agents_dest / agent_name
        agent_dest_dir.mkdir(parents=True, exist_ok=True)
        
        with open(agent_dest_dir / "agent.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    # 2. Process skills
    skills_dest = dest_path / ".agents/skills"
    skills_dest.mkdir(parents=True, exist_ok=True)
    
    for skill_file in skills_src.glob("*.md"):
        write_markdown_skill(skill_file, skills_dest, src_dir, "antigravity")

    # 3. Process helper scripts
    scripts_dest = dest_path / ".agents/scripts"
    copy_helper_scripts(src_dir, scripts_dest)

def process_claude(src_dir, dest_path, models):
    dest_path = Path(dest_path)
    agents_src = agents_src_dir(src_dir)
    skills_src = skills_src_dir(src_dir)
    
    # 1. Process agents
    agents_dest = dest_path / ".claude/agents"
    agents_dest.mkdir(parents=True, exist_ok=True)
    
    for agent_file in agents_src.glob("*.md"):
        model = get_model(models, "claude", agent_file.name)
        effort = get_effort(models, "claude", agent_file.name)
        # A subagent-promptok is kaphatnak `<!-- INCLUDE:shared/... -->` markert
        # (BD14), és a `description`/`role` a PROJEKT nyelvét követi (LG26) —
        # mindkettőt a közös prepare_agent_content() végzi.
        content = prepare_agent_content(agent_file, src_dir, "claude")

        new_content = inject_markdown_model(content, model, "Claude Code", effort)

        with open(agents_dest / agent_file.name, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
    # 2. Process skills
    skills_dest = dest_path / ".claude/skills"
    skills_dest.mkdir(parents=True, exist_ok=True)
    
    for skill_file in skills_src.glob("*.md"):
        write_markdown_skill(skill_file, skills_dest, src_dir, "claude")

    # 3. Process helper scripts
    scripts_dest = dest_path / ".claude/scripts"
    copy_helper_scripts(src_dir, scripts_dest)

def process_copilot(src_dir, dest_path, models):
    dest_path = Path(dest_path)
    agents_src = agents_src_dir(src_dir)
    skills_src = skills_src_dir(src_dir)
    
    # 1. Process agents
    agents_dest = dest_path / ".github/agents"
    agents_dest.mkdir(parents=True, exist_ok=True)
    
    for agent_file in agents_src.glob("*.md"):
        agent_name = agent_file.stem
        model = get_model(models, "copilot", agent_file.name)
        effort = get_effort(models, "copilot", agent_file.name)

        # A subagent-promptok is kaphatnak `<!-- INCLUDE:shared/... -->` markert
        # (BD14), és a `description`/`role` a PROJEKT nyelvét követi (LG26) —
        # mindkettőt a közös prepare_agent_content() végzi.
        content = prepare_agent_content(agent_file, src_dir, "copilot")

        new_content = inject_markdown_model(content, model, "Copilot", effort)

        with open(agents_dest / f"{agent_name}.agent.md", 'w', encoding='utf-8') as f:
            f.write(new_content)
            
    # 2. Process skills (instructions)
    instructions_dest = dest_path / ".github/instructions"
    instructions_dest.mkdir(parents=True, exist_ok=True)
    
    for skill_file in skills_src.glob("*.md"):
        skill_name = skill_file.stem
        clean_name = re.sub(r'^\d\d-', '', skill_name)

        # Nincs modell-injektálás: a Copilot `.instructions.md` frontmatter nem
        # ismer `model` mezőt (az csak prompt-fájlnál van) → inert lenne. Lásd a
        # write_markdown_skill fölötti indoklást.
        # Ugyanaz a transzformáció-lánc, mint a write_markdown_skill-ben (8.7):
        # projekt-nyelvi frontmatter → INCLUDE-feloldás → scripts-mappa.
        content = prepare_skill_content(skill_file, src_dir, "copilot")

        with open(instructions_dest / f"bs-{clean_name}.instructions.md", 'w', encoding='utf-8') as f:
            f.write(content)

    # 3. Process helper scripts
    scripts_dest = dest_path / ".github/scripts"
    copy_helper_scripts(src_dir, scripts_dest)

def process_cursor(src_dir, dest_path, models):
    dest_path = Path(dest_path)
    agents_src = agents_src_dir(src_dir)
    skills_src = skills_src_dir(src_dir)

    # 1. Process agents → .cursor/agents/*.md (Cursor Agent subagent formátum,
    #    ugyanaz a szerkezet, mint Claude Code-nál: YAML frontmatter + prompt).
    agents_dest = dest_path / ".cursor/agents"
    agents_dest.mkdir(parents=True, exist_ok=True)

    for agent_file in agents_src.glob("*.md"):
        model = get_model(models, "cursor", agent_file.name)
        effort = get_effort(models, "cursor", agent_file.name)
        readonly = _agent_stem(agent_file.name) in READONLY_AGENTS

        # A subagent-promptok is kaphatnak `<!-- INCLUDE:shared/... -->` markert
        # (BD14), és a `description`/`role` a PROJEKT nyelvét követi (LG26) —
        # mindkettőt a közös prepare_agent_content() végzi.
        content = prepare_agent_content(agent_file, src_dir, "cursor")

        new_content = inject_cursor_agent(content, model, effort, readonly)

        with open(agents_dest / agent_file.name, 'w', encoding='utf-8') as f:
            f.write(new_content)

    # 2. Process skills → .cursor/skills/bs-<name>/SKILL.md (Agent Skills)
    skills_dest = dest_path / ".cursor/skills"
    skills_dest.mkdir(parents=True, exist_ok=True)

    for skill_file in skills_src.glob("*.md"):
        write_markdown_skill(skill_file, skills_dest, src_dir, "cursor")

    # 3. Process helper scripts
    scripts_dest = dest_path / ".cursor/scripts"
    copy_helper_scripts(src_dir, scripts_dest)

def main():
    global PROMPT_LANG, PROJECT_LANG

    if len(sys.argv) < 4:
        print("Usage: install-helper.py <platform> <src_dir> <dest_path> "
              "[prompt_lang] [project_lang]")
        sys.exit(1)

    platform = sys.argv[1]
    src_dir = sys.argv[2]
    dest_path = sys.argv[3]

    # A két nyelvi argumentum OPCIONÁLIS: hiányában `hu`/`hu`, tehát a régi,
    # 3-argumentumos hívás (és a telepített kimenet) változatlan marad.
    if len(sys.argv) > 4:
        PROMPT_LANG = sys.argv[4].strip().lower()
    if len(sys.argv) > 5:
        PROJECT_LANG = sys.argv[5].strip().lower()

    for label, lang in (("prompt", PROMPT_LANG), ("projekt", PROJECT_LANG)):
        if lang not in SUPPORTED_LANGS:
            print(f"Error: ismeretlen {label}-nyelv: '{lang}' "
                  f"(támogatott: {', '.join(SUPPORTED_LANGS)})")
            sys.exit(1)

    # A prompt-nyelvhez tartozó forrás-fa létezés-ellenőrzése: jobb itt
    # megállni, mint egy üres skills/ mappával "sikeresen" telepíteni.
    for d in (skills_src_dir(src_dir), agents_src_dir(src_dir)):
        if not d.is_dir():
            print(f"Error: a '{PROMPT_LANG}' prompt-nyelvhez tartozó forrásmappa "
                  f"nem létezik: {d}")
            sys.exit(1)

    if (PROMPT_LANG, PROJECT_LANG) != ("hu", "hu"):
        print(f"  Nyelvek — prompt: {PROMPT_LANG.upper()}, "
              f"projekt: {PROJECT_LANG.upper()}")
    
    models_path = Path(src_dir) / "prompts/models.json"
    if not models_path.exists():
        print(f"Error: models.json not found at {models_path}")
        sys.exit(1)
        
    with open(models_path, 'r', encoding='utf-8') as f:
        models = json.load(f)
        
    if platform == "antigravity":
        process_antigravity(src_dir, dest_path, models)
    elif platform == "claude":
        process_claude(src_dir, dest_path, models)
    elif platform == "copilot":
        process_copilot(src_dir, dest_path, models)
    elif platform == "cursor":
        process_cursor(src_dir, dest_path, models)
    elif platform == "codex":
        process_codex(src_dir, dest_path, models)
    else:
        print(f"Error: Unknown platform {platform}")
        sys.exit(1)
        
    print("Success")

if __name__ == "__main__":
    main()
