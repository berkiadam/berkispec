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
#   - 10-cycle-status: csak egy Python scriptet futtat és megjeleníti (0 LLM-ítélet)
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
    "10-cycle-status": "research_agent",
    "analyzer": "deep_reasoning_agent",
}

# Cursor subagent `readonly: true` — CSAK azok az agentek, amelyek biztosan
# SEMMIT nem írnak (a prózájuk is kimondja: „Read-only vagy"): tisztán a hívó
# skillnek adnak vissza megállapítást/összefoglalót, fájlt nem hoznak létre.
# FIGYELEM: a tool-lista nem megbízható jelzés — a `reviewer` (code-review.md)
# és a `test-runner` (report-mappa/config) Bash-en keresztül ÍR, hiába nincs a
# tool-listájukban Edit/Write; ezért ők NINCSENEK itt. Téves readonly=true
# megtörné őket.
READONLY_AGENTS = {"analyzer", "researcher", "doc-sync-planner"}

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
#     AGENT_MODEL_KEYS adja (analyzer → deep, researcher/10-cycle-status →
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

# Minden helper scriptet (prompts/scripts/*.py) átmásol a cél scripts_dest
# mappába, kivéve saját magát (install-helper.py, ami csak a telepítő gépén
# fut, a célprojektben nincs rá szükség). Így új helper script (pl.
# ds22-gate-check.py) hozzáadásakor nem kell mindhárom process_* függvényt
# külön bővíteni.
def copy_helper_scripts(src_dir, scripts_dest):
    scripts_dest.mkdir(parents=True, exist_ok=True)
    scripts_src_dir = Path(src_dir) / "prompts/scripts"
    for script_src in sorted(scripts_src_dir.glob("*.py")):
        if script_src.name == "install-helper.py":
            continue
        script_dest = scripts_dest / script_src.name
        shutil.copy(script_src, script_dest)
        os.chmod(script_dest, 0o755)

# ── Közös leírás-részletek build-time inline-olása a skillekbe (BD13/BD14) ────
# A skillek `<!-- INCLUDE:shared/<fájl> -->` markert tartalmazhatnak. Mivel a
# skillek platformonként eltérő helyre települnek, egy relatív hivatkozás
# futásidőben nem oldódna fel egységesen — ezért a telepítő a marker helyére
# a `prompts/shared/<fájl>` tartalmát ILLESZTI BE (build-time include), így a
# telepített SKILL.md önmagában teljes. A megosztott fájl elején lévő
# magyarázó HTML-kommentet (forrás-jegyzet) nem visszük át.
_INCLUDE_MARKER_RE = re.compile(r'[ \t]*<!--\s*INCLUDE:\s*(?P<path>[^\s]+?)\s*-->[ \t]*')
_shared_include_cache = {}

def _read_shared_include(src_dir, rel_path):
    """Beolvassa és cache-eli a prompts/<rel_path> tartalmát, a vezető
    magyarázó HTML-kommentet levágva."""
    key = (str(src_dir), rel_path)
    if key in _shared_include_cache:
        return _shared_include_cache[key]
    include_path = Path(src_dir) / "prompts" / rel_path
    with open(include_path, 'r', encoding='utf-8') as f:
        text = f.read()
    # Vezető <!-- ... --> blokk (forrás-jegyzet) eltávolítása
    text = re.sub(r'^\s*<!--.*?-->\s*', '', text, count=1, flags=re.DOTALL)
    text = text.strip('\n')
    _shared_include_cache[key] = text
    return text

def inline_shared_includes(content, src_dir):
    """A skill törzsében lévő `<!-- INCLUDE:shared/... -->` markereket a
    hivatkozott fájl tartalmára cseréli. Ha egy marker fájlja nem található,
    a markert érintetlenül hagyja (a telepítés nem törik meg)."""
    def _repl(match):
        rel_path = match.group('path')
        try:
            return _read_shared_include(src_dir, rel_path)
        except OSError:
            return match.group(0)
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
# Az `effort` Cursorban nem dokumentált natív mező (a model lehet inherit/fast/
# model-id); hintként írjuk ki + az alertben, a Cursor az ismeretlen
# frontmatter-kulcsot figyelmen kívül hagyja.
def inject_cursor_agent(content, model, effort, readonly=False):
    injected = inject_markdown_model(content, model, "Cursor", effort)
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
def write_markdown_skill(skill_file, skills_dest, src_dir=None):
    """Skill másolása modell-injektálás NÉLKÜL a <skills_dest>/bs-<stem>/SKILL.md alá.
    A `<!-- INCLUDE:shared/... -->` markerek build-time inline-olódnak (BD14),
    ha a `src_dir` meg van adva."""
    with open(skill_file, 'r', encoding='utf-8') as f:
        content = f.read()
    if src_dir is not None:
        content = inline_shared_includes(content, src_dir)
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
    agents_src = Path(src_dir) / "prompts/agents"
    skills_src = Path(src_dir) / "prompts/skills"

    # 1. Agents → .codex/agents/<stem>.toml (TOML subagent formátum)
    agents_dest = dest_path / ".codex/agents"
    agents_dest.mkdir(parents=True, exist_ok=True)

    for agent_file in agents_src.glob("*.md"):
        stem = _agent_stem(agent_file.name)
        model = get_model(models, "codex", agent_file.name)
        effort = get_effort(models, "codex", agent_file.name)
        readonly = stem in READONLY_AGENTS

        with open(agent_file, 'r', encoding='utf-8') as f:
            content = f.read()

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
        write_markdown_skill(skill_file, skills_dest, src_dir)

    # 3. Helper scripts → .codex/scripts/
    scripts_dest = dest_path / ".codex/scripts"
    copy_helper_scripts(src_dir, scripts_dest)

def process_antigravity(src_dir, dest_path, models):
    dest_path = Path(dest_path)
    agents_src = Path(src_dir) / "prompts/agents/gemini-agent"
    skills_src = Path(src_dir) / "prompts/skills"
    
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

        data["model"] = model
        data["effort"] = effort

        try:
            sections = data["customAgentSpec"]["customAgent"]["systemPromptSections"]
            for section in sections:
                if section.get("title") == "Instructions":
                    content = section.get("content", "")
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
        write_markdown_skill(skill_file, skills_dest, src_dir)

    # 3. Process helper scripts
    scripts_dest = dest_path / ".agents/scripts"
    copy_helper_scripts(src_dir, scripts_dest)

def process_claude(src_dir, dest_path, models):
    dest_path = Path(dest_path)
    agents_src = Path(src_dir) / "prompts/agents"
    skills_src = Path(src_dir) / "prompts/skills"
    
    # 1. Process agents
    agents_dest = dest_path / ".claude/agents"
    agents_dest.mkdir(parents=True, exist_ok=True)
    
    for agent_file in agents_src.glob("*.md"):
        model = get_model(models, "claude", agent_file.name)
        effort = get_effort(models, "claude", agent_file.name)
        with open(agent_file, 'r', encoding='utf-8') as f:
            content = f.read()

        new_content = inject_markdown_model(content, model, "Claude Code", effort)

        with open(agents_dest / agent_file.name, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
    # 2. Process skills
    skills_dest = dest_path / ".claude/skills"
    skills_dest.mkdir(parents=True, exist_ok=True)
    
    for skill_file in skills_src.glob("*.md"):
        write_markdown_skill(skill_file, skills_dest, src_dir)

    # 3. Process helper scripts
    scripts_dest = dest_path / ".claude/scripts"
    copy_helper_scripts(src_dir, scripts_dest)

def process_copilot(src_dir, dest_path, models):
    dest_path = Path(dest_path)
    agents_src = Path(src_dir) / "prompts/agents"
    skills_src = Path(src_dir) / "prompts/skills"
    
    # 1. Process agents
    agents_dest = dest_path / ".github/agents"
    agents_dest.mkdir(parents=True, exist_ok=True)
    
    for agent_file in agents_src.glob("*.md"):
        agent_name = agent_file.stem
        model = get_model(models, "copilot", agent_file.name)
        effort = get_effort(models, "copilot", agent_file.name)

        with open(agent_file, 'r', encoding='utf-8') as f:
            content = f.read()

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
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Build-time include-inline-olás (BD14) — a Copilot is teljes SKILL-t kap.
        content = inline_shared_includes(content, src_dir)

        with open(instructions_dest / f"bs-{clean_name}.instructions.md", 'w', encoding='utf-8') as f:
            f.write(content)

    # 3. Process helper scripts
    scripts_dest = dest_path / ".github/scripts"
    copy_helper_scripts(src_dir, scripts_dest)

def process_cursor(src_dir, dest_path, models):
    dest_path = Path(dest_path)
    agents_src = Path(src_dir) / "prompts/agents"
    skills_src = Path(src_dir) / "prompts/skills"

    # 1. Process agents → .cursor/agents/*.md (Cursor Agent subagent formátum,
    #    ugyanaz a szerkezet, mint Claude Code-nál: YAML frontmatter + prompt).
    agents_dest = dest_path / ".cursor/agents"
    agents_dest.mkdir(parents=True, exist_ok=True)

    for agent_file in agents_src.glob("*.md"):
        model = get_model(models, "cursor", agent_file.name)
        effort = get_effort(models, "cursor", agent_file.name)
        readonly = _agent_stem(agent_file.name) in READONLY_AGENTS

        with open(agent_file, 'r', encoding='utf-8') as f:
            content = f.read()

        new_content = inject_cursor_agent(content, model, effort, readonly)

        with open(agents_dest / agent_file.name, 'w', encoding='utf-8') as f:
            f.write(new_content)

    # 2. Process skills → .cursor/skills/bs-<name>/SKILL.md (Agent Skills)
    skills_dest = dest_path / ".cursor/skills"
    skills_dest.mkdir(parents=True, exist_ok=True)

    for skill_file in skills_src.glob("*.md"):
        write_markdown_skill(skill_file, skills_dest, src_dir)

    # 3. Process helper scripts
    scripts_dest = dest_path / ".cursor/scripts"
    copy_helper_scripts(src_dir, scripts_dest)

def main():
    if len(sys.argv) < 4:
        print("Usage: install-helper.py <platform> <src_dir> <dest_path>")
        sys.exit(1)
        
    platform = sys.argv[1]
    src_dir = sys.argv[2]
    dest_path = sys.argv[3]
    
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
