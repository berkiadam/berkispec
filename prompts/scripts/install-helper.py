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

def get_model(models, platform, filename):
    platform_models = models.get(platform, {})
    stem = _agent_stem(filename)

    agent_key = AGENT_MODEL_KEYS.get(stem)
    if agent_key and agent_key in platform_models:
        return platform_models[agent_key]

    return platform_models.get("default", "")

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

def inject_markdown_model(content, model, platform_name):
    parts = content.split('---')
    if len(parts) >= 3:
        frontmatter = parts[1]
        body = '---'.join(parts[2:])
        
        # Inject model: <model> into frontmatter
        lines = frontmatter.splitlines()
        model_found = False
        new_lines = []
        for line in lines:
            if line.strip().startswith('model:'):
                new_lines.append(f"model: {model}")
                model_found = True
            else:
                new_lines.append(line)
        if not model_found:
            new_lines.append(f"model: {model}")
        new_frontmatter = '\n'.join(new_lines)
        
        # Also inject visual warning alert block into body
        alert = f"\n> [!IMPORTANT]\n> **Recommended Model ({platform_name}):** {model}\n\n"
        return f"---{new_frontmatter}\n---{alert}{body.lstrip()}"
    else:
        # No frontmatter, construct frontmatter with model
        alert = f"> [!IMPORTANT]\n> **Recommended Model ({platform_name}):** {model}\n\n"
        return f"---\nmodel: {model}\n---\n{alert}{content.lstrip()}"

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
        
        with open(agent_json_src, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        data["model"] = model
        
        try:
            sections = data["customAgentSpec"]["customAgent"]["systemPromptSections"]
            for section in sections:
                if section.get("title") == "Instructions":
                    content = section.get("content", "")
                    section["content"] = f"> [!IMPORTANT]\n> **Recommended Model (Antigravity):** {model}\n\n" + content
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
        skill_name = skill_file.stem
        model = get_model(models, "antigravity", skill_file.name)
        
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        new_content = inject_markdown_model(content, model, "Antigravity")
        
        skill_dest_dir = skills_dest / f"bs-{skill_name}"
        skill_dest_dir.mkdir(parents=True, exist_ok=True)
        
        with open(skill_dest_dir / "SKILL.md", 'w', encoding='utf-8') as f:
            f.write(new_content)

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
        with open(agent_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        new_content = inject_markdown_model(content, model, "Claude Code")
        
        with open(agents_dest / agent_file.name, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
    # 2. Process skills
    skills_dest = dest_path / ".claude/skills"
    skills_dest.mkdir(parents=True, exist_ok=True)
    
    for skill_file in skills_src.glob("*.md"):
        skill_name = skill_file.stem
        model = get_model(models, "claude", skill_file.name)
        
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        new_content = inject_markdown_model(content, model, "Claude Code")
        
        skill_dest_dir = skills_dest / f"bs-{skill_name}"
        skill_dest_dir.mkdir(parents=True, exist_ok=True)
        
        with open(skill_dest_dir / "SKILL.md", 'w', encoding='utf-8') as f:
            f.write(new_content)

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
        
        with open(agent_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        new_content = inject_markdown_model(content, model, "Copilot")
        
        with open(agents_dest / f"{agent_name}.agent.md", 'w', encoding='utf-8') as f:
            f.write(new_content)
            
    # 2. Process skills (instructions)
    instructions_dest = dest_path / ".github/instructions"
    instructions_dest.mkdir(parents=True, exist_ok=True)
    
    for skill_file in skills_src.glob("*.md"):
        skill_name = skill_file.stem
        clean_name = re.sub(r'^\d\d-', '', skill_name)
        model = get_model(models, "copilot", skill_file.name)
        
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        new_content = inject_markdown_model(content, model, "Copilot")
        
        with open(instructions_dest / f"bs-{clean_name}.instructions.md", 'w', encoding='utf-8') as f:
            f.write(new_content)

    # 3. Process helper scripts
    scripts_dest = dest_path / ".github/scripts"
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
    else:
        print(f"Error: Unknown platform {platform}")
        sys.exit(1)
        
    print("Success")

if __name__ == "__main__":
    main()
