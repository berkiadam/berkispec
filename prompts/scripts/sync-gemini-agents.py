#!/usr/bin/env python3
"""A `prompts/agents-<lang>/gemini-agent/<név>/agent.json` fájlok `Instructions`
szekciójának szinkronizálása a `prompts/agents-<lang>/<név>.md` prompt törzsével.

Miért kell: az Antigravity/Gemini platform agent.json sémát vár, ezért a
subagent-promptok ott JSON-ba ágyazva élnek. Ez a beágyazott szöveg a `.md`
prompt SZÓ SZERINTI másolata (a frontmatter nélkül) — kézzel tartva viszont
csendben elcsúszik: a `.md`-t javítjuk, a JSON pedig a régi viselkedést
telepíti tovább az Antigravity-felhasználóknak.

Használat:
  sync-gemini-agents.py            # szinkronizál, és kiírja mi változott
  sync-gemini-agents.py --check    # csak ellenőriz (exit 1, ha van eltérés)

Kilépő kód: 0 = minden szinkronban (vagy sikeres frissítés)
            1 = --check módban eltérés van
"""
import argparse
import json
import re
import sys
from pathlib import Path

FRONTMATTER_RE = re.compile(r"^---\n.*?\n---\n", re.DOTALL)


def md_body(path):
    return FRONTMATTER_RE.sub("", path.read_text(encoding="utf-8"), count=1).strip() + "\n"


def sync_tree(agents_dir, check):
    """Egy prompt-nyelvi agent-fa szinkronja. Visszaadja az eltérések listáját."""
    gemini_dir = agents_dir / "gemini-agent"
    drift = []

    # Új subagent: ha van `agents/<név>.md`, de még nincs gemini `agent.json`,
    # itt jön létre a séma-vázzal — különben az Antigravity-telepítés csendben
    # kihagyná az új ágenst (a process_antigravity a mappákon iterál).
    for md_path in sorted(agents_dir.glob("*.md")):
        target = gemini_dir / md_path.stem / "agent.json"
        if target.exists():
            continue
        role = ""
        for line in md_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("role:"):
                role = line.split(":", 1)[1].strip().strip('"')
                break
        skeleton = {
            "name": md_path.stem,
            "displayName": md_path.stem,
            "description": role or md_path.stem,
            "hidden": False,
            "customAgentSpec": {
                "customAgent": {
                    "systemPromptSections": [{"title": "Instructions", "content": ""}],
                    "toolNames": ["view_file", "list_dir", "grep_search"],
                }
            },
        }
        if not check:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(skeleton, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        drift.append(f"{md_path.stem} (új agent.json)")

    # `--check` módban a tükör-mappa hiánya DRIFT, nem összeomlás: a fenti ciklus
    # már felvette a hiányzó agent.json-okat a drift-listába, itt csak nincs mit
    # végigjárni. (Enélkül a 14.3 „futtasd a --check-et a munka elején" szabálya
    # használhatatlan: egy új nyelvi fán a kapu traceback-kel állt le.)
    if not gemini_dir.is_dir():
        return drift

    for agent_dir in sorted(gemini_dir.iterdir()):
        if not agent_dir.is_dir():
            continue
        json_path = agent_dir / "agent.json"
        md_path = agents_dir / f"{agent_dir.name}.md"
        if not json_path.is_file() or not md_path.is_file():
            print(f"KIHAGYVA: {agent_dir.name} (hiányzó agent.json vagy .md)", file=sys.stderr)
            continue

        data = json.loads(json_path.read_text(encoding="utf-8"))
        try:
            sections = data["customAgentSpec"]["customAgent"]["systemPromptSections"]
        except KeyError:
            print(f"KIHAGYVA: {agent_dir.name} (nem várt agent.json séma)", file=sys.stderr)
            continue

        want = md_body(md_path)
        for section in sections:
            if section.get("title") != "Instructions":
                continue
            if section.get("content", "").strip() == want.strip():
                continue
            drift.append(agent_dir.name)
            if not check:
                section["content"] = want
                json_path.write_text(
                    json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
                )

    return drift


def main():
    parser = argparse.ArgumentParser(description="gemini agent.json ↔ agents-<lang>/*.md szinkron")
    parser.add_argument("--check", action="store_true", help="csak ellenőrzés, írás nélkül")
    parser.add_argument("--root", default=Path(__file__).resolve().parents[2],
                        help="a repó gyökere (alap: a szkript helyéből számolva)")
    args = parser.parse_args()

    # MINDEN prompt-nyelvi fát egymás után futtatunk (`prompts/agents-hu`,
    # `prompts/agents-en`, …), így egy futás mindkét nyelvet szinkronban tartja,
    # és a `--check` egyszerre ellenőriz mindent. Nincs `--prompt-lang` flag:
    # a féloldalas futtatás pont azt a csendes elcsúszást engedné meg, amit ez a
    # kapu meg akar fogni.
    trees = sorted(d for d in (Path(args.root) / "prompts").glob("agents-*") if d.is_dir())
    if not trees:
        print("HIBA: nincs egyetlen prompts/agents-<lang> fa sem", file=sys.stderr)
        return 1

    drift = []
    for agents_dir in trees:
        drift += [f"{agents_dir.name}/{name}" for name in sync_tree(agents_dir, args.check)]

    if not drift:
        names = ", ".join(d.name for d in trees)
        print(f"GEMINI-SYNC: minden agent.json szinkronban a .md prompttal ({names})")
        return 0
    verb = "eltér" if args.check else "frissítve"
    print(f"GEMINI-SYNC: {len(drift)} agent {verb}: {', '.join(drift)}")
    return 1 if args.check else 0


if __name__ == "__main__":
    sys.exit(main())
