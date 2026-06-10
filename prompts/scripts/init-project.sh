#!/usr/bin/env bash
#
# init-project.sh — Skill és Agent integráció a támogatott ágensekhez
#

set -euo pipefail

# Segédfunkciók
show_help() {
  echo "Használat:"
  echo "  $0 [agy|claude|codex]"
  echo ""
  echo "Paraméterek:"
  echo "  agy    - Antigravity CLI workspace-level skills és agents integráció"
  echo "  claude - Claude Code integráció (még nem implementált)"
  echo "  codex  - Codex CLI integráció (még nem implementált)"
}

# Ágens típusának bekérése
AGENT_TYPE=""

# 1. Ha van CLI paraméter
if [ $# -gt 0 ]; then
  case "$1" in
    agy|antigravity)
      AGENT_TYPE="agy"
      ;;
    claude|claude-code)
      AGENT_TYPE="claude"
      ;;
    codex)
      AGENT_TYPE="codex"
      ;;
    -h|--help)
      show_help
      exit 0
      ;;
    *)
      echo "Hiba: Ismeretlen ágens típus: $1"
      show_help
      exit 1
      ;;
  esac
fi

# 2. Ha nincs megadva, rákérdezünk interaktívan
if [ -z "$AGENT_TYPE" ]; then
  echo "Milyen ágens alapon fut a projekt?"
  echo "  1) agy (Antigravity)"
  echo "  2) claude (Claude Code)"
  echo "  3) codex (Codex CLI)"
  read -p "Válassz egy opciót (1-3): " opt
  case "$opt" in
    1) AGENT_TYPE="agy" ;;
    2) AGENT_TYPE="claude" ;;
    3) AGENT_TYPE="codex" ;;
    *) echo "Érvénytelen opció."; exit 1 ;;
  esac
fi

# 3. Akciók az ágens típusától függően
case "$AGENT_TYPE" in
  claude|codex)
    echo "A(z) '$AGENT_TYPE' integráció még nincs implementálva."
    exit 0
    ;;
  agy)
    echo "Antigravity (agy) integráció indítása..."
    
    # Előfeltétel-ellenőrzés
    if [ ! -d "prompts/skills" ] || [ ! -d "prompts/agents" ]; then
      echo "Hiba: A 'prompts/skills' vagy 'prompts/agents' mappa nem található!"
      echo "Kérlek a projekt gyökérkönyvtárából futtasd a scriptet!"
      exit 1
    fi
    
    # 1. Lépés: Skillek linkelése
    echo "Skillek linkelése..."
    mkdir -p ".agents/skills"
    
    for skill_file in prompts/skills/*.md; do
      [ -e "$skill_file" ] || continue
      
      filename=$(basename "$skill_file")
      skill_name="${filename%.md}"
      
      skill_target_dir=".agents/skills/$skill_name"
      skill_link="$skill_target_dir/SKILL.md"
      
      echo "  - Skill feldolgozás: $skill_name"
      mkdir -p "$skill_target_dir"
      
      # Idempotens symlink ellenőrzés
      if [ -L "$skill_link" ]; then
        current_target=$(readlink "$skill_link")
        if [ "$current_target" == "../../../prompts/skills/$filename" ]; then
          continue
        else
          rm "$skill_link"
        fi
      elif [ -e "$skill_link" ]; then
        echo "    Figyelem: Egy valódi fájl áll a symlink útjában: $skill_link. Kihagyva."
        continue
      fi
      
      ln -s "../../../prompts/skills/$filename" "$skill_link"
    done
    
    # 2. Lépés: Ágensek fordítása JSON formátumra
    echo "Ágensek fordítása JSON formátumra..."
    mkdir -p ".agents/agents"
    
    for agent_file in prompts/agents/*.md; do
      [ -e "$agent_file" ] || continue
      
      filename=$(basename "$agent_file")
      agent_name="${filename%.md}"
      
      agent_target_dir=".agents/agents/$agent_name"
      agent_json="$agent_target_dir/agent.json"
      
      echo "  - Ágens fordítása: $agent_name"
      mkdir -p "$agent_target_dir"
      
      # Python script futtatása az átalakításhoz
      python3 - "$agent_file" "$agent_json" << 'EOF'
import sys
import re
import json

src_file = sys.argv[1]
dst_file = sys.argv[2]

with open(src_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Frontmatter és törzs szétválasztása
parts = content.split('---')
if len(parts) < 3:
    print(f"Hiba: {src_file} nem megfelelő frontmatter formátumú.")
    sys.exit(1)

frontmatter_raw = parts[1]
body = '---'.join(parts[2:]).strip()

# Kulcs-érték párok kinyerése frontmatterből
metadata = {}
for line in frontmatter_raw.splitlines():
    line = line.strip()
    if not line or ':' not in line:
        continue
    key, val = line.split(':', 1)
    key = key.strip()
    val = val.strip().strip('"').strip("'")
    metadata[key] = val

# Eszköz-leképezés
tool_mapping = {
    "Read": ["view_file", "list_dir"],
    "Grep": ["grep_search"],
    "Bash": ["run_command"],
    "Write": ["write_to_file", "replace_file_content", "multi_replace_file_content"]
}

mapped_tools = []
tools_match = re.search(r'tools:\s*\[(.*?)\]', frontmatter_raw)
if tools_match:
    tools_list = [t.strip().strip('"').strip("'") for t in tools_match.group(1).split(',')]
    for t in tools_list:
        if t in tool_mapping:
            mapped_tools.extend(tool_mapping[t])
        else:
            mapped_tools.append(t)

agent_json_data = {
    "name": metadata.get("name", ""),
    "displayName": metadata.get("name", ""),
    "description": metadata.get("role", ""),
    "hidden": False,
    "customAgentSpec": {
        "customAgent": {
            "systemPromptSections": [
                {
                    "title": "Instructions",
                    "content": body
                }
            ],
            "toolNames": mapped_tools
        }
    }
}

with open(dst_file, 'w', encoding='utf-8') as f:
    json.dump(agent_json_data, f, indent=2, ensure_ascii=False)

EOF
    done
    
    echo "Antigravity (agy) integráció sikeresen befejeződött!"
    ;;
esac
