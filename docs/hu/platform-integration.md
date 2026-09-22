# Ágens-specifikus integráció

← [Vissza a főoldalra](../../README-HU.md) · [Oldalindex](README.md)

A `prompts/skills-hu/` és `prompts/agents-hu/` a **single source of truth**. A különböző ágensek más-más helyen keresik a skilleket / subagenteket:

| Ágens | Skill-hely | Subagent-hely |
|---|---|---|
| Claude Code | `~/.claude/skills/bs-{skill_name}/SKILL.md` vagy `.claude/skills/…` | `~/.claude/agents/` vagy `.claude/agents/` |
| Cursor (Agent CLI) | `.cursor/skills/bs-{skill_name}/SKILL.md` | `.cursor/agents/{agent_name}.md` |
| Antigravity | `.agents/skills/{skill_name}/SKILL.md` | `.agents/agents/{agent_name}/agent.json` |
| GitHub Copilot | `.github/instructions/bs-{name}.instructions.md` | `.github/agents/{agent_name}.agent.md` |
| Codex CLI | `.agents/skills/bs-{skill_name}/SKILL.md` (közös az Antigravity-vel) | `.codex/agents/{agent_name}.toml` |

Az integrációk beállításához futtasd a [`install.sh`](../../install.sh) vagy a [`install.ps1`](../../install.ps1) scriptet:
* **Linux/macOS:**
  ```bash
  chmod +x install.sh
  ./install.sh
  ```
* **Windows (PowerShell):**
  ```powershell
  .\install.ps1
  ```

## 18.0 Platform-korlát: parancs-futtatás a subagentekben (EX1)

**A subagentek nem mindenhol tudnak parancsot futtatni.** Az ok nem a tool-deklaráció (az Antigravity `agent.json`-ban a `run_command` ott van a `test-runner`, `reviewer`, `implement-fixer`, `review-fixer` és `doc-sync-planner` `toolNames` listájában), hanem a **jóváhagyás**: a subagent nem tud engedélykérő promptot mutatni a felhasználónak, ezért minden parancs elhasal, ami nincs auto-engedélyezve. Antigravityn ezt visszaigazolt viselkedésként láttuk.

| Ki futtat parancsot | Hol fut | Érinti-e az EX1 |
|---|---|---|
| `run-tests.py`, `round-log.py`, a kapuk | a **fő ágens** (a skill maga) | nem — a fő ágensnél a jóváhagyás működik |
| `test-runner` subagent | subagent | **igen** — a fallback-ág letiltódhat |
| `implement-fixer` / `review-fixer` `[CHECK]` futásai | subagent | **igen** — a javítás megvan, az ellenőrzés marad el |
| `reviewer` `git diff`-je | subagent | **igen** — ezért a diffet az orchestrátor adja át bemenetként |

**Két megoldás, egymást kiegészítve:**

1. **Architekturális (ez az alapértelmezés).** A 07 minden fontos futtatása a **fő ágensben**, szkriptekkel történik — ezért lett a `plan.md` `### Gépi futtatási tábla` (TP4) kötelező, és ezért fallback csak a `test-runner`. Ahol a subagent mégis blokkolt, ott az **EX1 kontraktus** lép életbe: az agent `## Futtatás blokkolva (EX1)` szekcióval tér vissza, és **soha nem talál ki eredményt** — a hívó pedig maga futtatja a szkriptet. Ha a gépi tábla is hiányzik ÉS a subagent is blokkolt, a fázis **STOP + humán**, nem PASS.
2. **Platform-oldali (opcionális).** Ha az ágens-eszköz ismer auto-futtatási allowlistát, vedd fel rá a keretrendszer szkriptjeit és a projekt teszt-parancsait (pl. `python3 .agents/scripts/*`, `npm test`, `npx playwright`, `git diff`) — ezzel a subagentek is futtathatnak, és a fallback-ág is visszaáll.

> **Miért nem engedjük „nagyvonalúan" tovább a blokkolt subagentet:** egy `test-runner`, amelyik nem tud futtatni, de mégis jelent, hamis `43 passed`-et adna — abból a 07 automatikus `Kész` státuszt és commitot csinál. Ezért az EX1 explicit tiltja az eredmény-kitalálást, és inkább megállítja a fázist.

---

## 18.1 Antigravity CLI (Google DeepMind)

Ha az **Antigravity** ágenst használod a fejlesztési ciklusok futtatására, a fenti script automatikusan előkészíti a lokális munkakörnyezetet:
1. Létrehozza a `.agents/skills/` könyvtárat, és mindegyik fázishoz symlinkeli a `SKILL.md`-t.
2. Létrehozza a `.agents/agents/` könyvtárat, és a markdown ágens-definíciókat automatikusan a CLI által elvárt `agent.json` formátumra fordítja.

> **🔴 Az Antigravity nem lehet a központosított SDD CI-ágense.** Mérve 2026-09-22-én (CLI 1.107.0): az egyetlen prompt-fogadó belépő az `antigravity chat "<prompt>"`, ami **GUI chat-session-t nyit** — nincs `-p/--print`-szerű nem-interaktív mód, tehát display nélküli CI-futtatón nem fut le. A `ci-run-skill.sh --selftest` ezt kimondja, és `exit 2`-vel megáll. Ilyen projektben a `conventions.md` `## Review and merge` szekciójában `CI agent: command` a helyes érték (a platform saját, esemény-vezérelt PR-integrációja vagy bármely más parancs). **A lokális használatot ez nem érinti:** az interaktív Antigravity felületen a keret minden fázisa fut.

### 18.1.1 Tervezési és naplózási folyamat (Planning Mode)
Az ágens a saját belső alkalmazásmappájában (`~/.gemini/antigravity-cli/brain/`) naplóz, így ezek a fájlok nem szennyezik a projekt Git repository-ját:
* **Tervezési szakasz:** `implementation_plan.md` tervfájl, jóváhagyásra várva.
* **Végrehajtási szakasz:** `task.md` teendőlista.
* **Validációs szakasz:** `walkthrough.md` összegzés.

### 18.1.2 Jogosultságok kezelése (Permissions)
* **Fájlmódosítások:** a Trusted Workspace-en belül engedélyezett.
* **Külső parancsok:** futtatás előtt manuális megerősítést igényelnek (`Ask` mód).
* **Delegálás:** `/permissions` vagy `/config` (Allow), `--dangerously-skip-permissions` (session), vagy `~/.gemini/antigravity-cli/settings.json` (globális).

### 18.1.3 Skillek és Ágensek indítása (TUI használat)
Az integrációs script lefutása után az Antigravity felületén kétféleképpen is elindíthatod az egyes fázisok skill-jeit:
* **Slash parancsok:** Minden betöltött skill automatikusan egyedi slash paranccsá válik a promptban. A parancs neve a `SKILL.md` frontmatterében megadott `name` mezőből származik (sorszám nélkül). Például a 05-ös fázis indításához egyszerűen írd be:
  ```
  /bs-analyze
  ```
* **Interaktív választómenü:** A `/skill` (vagy `/skills`) parancs beírásával egy vizuális menü ugrik fel a terminálban, ahonnan a nyilakkal (`↑/↓`) kiválaszthatod és az `enter` billentyűvel életre hívhatod a kívánt fázist.
* **Egyedi ágensek listázása:** A `/agens` (vagy `/agent`) paranccsal tekintheted meg a regisztrált, egyedileg konfigurált subagenteket.

## 18.2 Codex CLI (OpenAI)

Ha a **Codex CLI**-t használod, a telepítő két különböző helyre dolgozik, mert a Codex az agenteket és a skilleket eltérő formátumban/helyen várja:

1. **Subagentek → `.codex/agents/<név>.toml`.** A Codex subagentek **TOML**-fájlok (nem markdown). A telepítő a markdown agent-definíciókat automatikusan TOML-ra fordítja, és kitölti:
   * `name`, `description` (az agent `role`-jából), `developer_instructions` (a teljes agent-prompt);
   * `model` és `model_reasoning_effort` — ezek **natívan hatnak** (a fájlban megadott érték elsőbbséget élvez a spawn-/`[agents]`-default/parent érték felett);
   * `sandbox_mode = "read-only"` a read-only agenteknél (`analyzer`, `researcher`, `doc-sync-planner`).
   * Futás közben a subagentek a `/agent` paranccsal listázhatók, illetve válthatsz közöttük.
2. **Skillek → `.agents/skills/bs-<név>/SKILL.md`.** A Codex a **projekt-szintű** skilleket a `.agents/skills/` mappából olvassa (a `.codex/skills` csak legacy, user-szintű hely — projekt-szinten nem található meg). A skillek slash-parancsként érhetők el (pl. `/bs-analyze`).

> ⚠️ **Codex ↔ Antigravity kölcsönös kizárás.** A `.agents/skills/` mappát **a Codex ÉS az Antigravity is használja**, ezért egy projektbe a kettő közül gyakorlatilag csak az egyik telepíthető. A telepítő ezt figyeli: a platform kiválasztásakor előre figyelmeztet, és ha a másik platform már jelen van (`.codex/agents/` ↔ `.agents/agents/`), a telepítés előtt rákérdez, folytatod-e.

---
