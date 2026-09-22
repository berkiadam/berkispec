# Agent-specific integration

← [Back to the main page](../../README.md) · [Page index](README.md)

`prompts/skills-hu/` and `prompts/agents-hu/` are the **single source of truth**. The various agents look for the skills / subagents in different places:

| Agent | Location of the skills | Location of the subagents |
|---|---|---|
| Claude Code | `~/.claude/skills/bs-{skill_name}/SKILL.md` or `.claude/skills/…` | `~/.claude/agents/` or `.claude/agents/` |
| Cursor (Agent CLI) | `.cursor/skills/bs-{skill_name}/SKILL.md` | `.cursor/agents/{agent_name}.md` |
| Antigravity | `.agents/skills/{skill_name}/SKILL.md` | `.agents/agents/{agent_name}/agent.json` |
| GitHub Copilot | `.github/instructions/bs-{name}.instructions.md` | `.github/agents/{agent_name}.agent.md` |
| Codex CLI | `.agents/skills/bs-{skill_name}/SKILL.md` (shared with Antigravity) | `.codex/agents/{agent_name}.toml` |

To set up the integrations, run the [`install.sh`](../../install.sh) or the [`install.ps1`](../../install.ps1) script:
* **Linux/macOS:**
  ```bash
  chmod +x install.sh
  ./install.sh
  ```
* **Windows (PowerShell):**
  ```powershell
  .\install.ps1
  ```

## 18.0 A platform limitation: running commands in the subagents (EX1)

**The subagents cannot run commands everywhere.** The reason is not the tool declaration (in the Antigravity `agent.json`, `run_command` is there in the `toolNames` list of `test-runner`, `reviewer`, `implement-fixer`, `review-fixer` and `doc-sync-planner`), but the **approval**: a subagent cannot show a permission prompt to the user, so every command that is not auto-approved fails. On Antigravity we saw this as confirmed behaviour.

| Who runs a command | Where it runs | Is it affected by EX1 |
|---|---|---|
| `run-tests.py`, `round-log.py`, the gates | the **main agent** (the skill itself) | no — with the main agent the approval works |
| the `test-runner` subagent | a subagent | **yes** — the fallback branch may be disabled |
| the `[CHECK]` runs of `implement-fixer` / `review-fixer` | a subagent | **yes** — the fix is made, but the verification is left out |
| the `git diff` of the `reviewer` | a subagent | **yes** — which is why the diff is handed over by the orchestrator as an input |

**Two solutions, complementing each other:**

1. **Architectural (this is the default).** Every important run of 07 happens in the **main agent**, with scripts — that is why the `### Machine-readable run table` (TP4) of `plan.md` became mandatory, and why only the `test-runner` is a fallback. Where a subagent is blocked after all, the **EX1 contract** takes effect: the agent returns with a `## Run blocked (EX1)` section, and it **never invents a result** — and the caller then runs the script itself. If the machine-readable table is missing too AND the subagent is blocked, the phase is a **STOP + human**, not a PASS.
2. **Platform-side (optional).** If the agent tool knows an auto-run allowlist, add the framework's scripts and the project's test commands to it (e.g. `python3 .agents/scripts/*`, `npm test`, `npx playwright`, `git diff`) — with that the subagents can run things too, and the fallback branch is restored.

> **Why we do not "generously" let a blocked subagent carry on:** a `test-runner` that cannot run anything but still reports would give a false `43 passed` — out of which 07 makes an automatic `Done` status and a commit. That is why EX1 explicitly forbids inventing a result, and stops the phase instead.

---

## 18.1 Antigravity CLI (Google DeepMind)

If you use the **Antigravity** agent to run the development cycles, the script above prepares the local working environment automatically:
1. It creates the `.agents/skills/` directory and symlinks the `SKILL.md` for each phase.
2. It creates the `.agents/agents/` directory and automatically translates the markdown agent definitions into the `agent.json` format expected by the CLI.

> **🔴 Antigravity cannot be the CI agent of centralized SDD.** Measured on 2026-09-22 (CLI 1.107.0): the only prompt entry point is `antigravity chat "<prompt>"`, which opens a **GUI chat session** — there is no `-p/--print`-style non-interactive mode, so it does not run on a CI runner without a display. `ci-run-skill.sh --selftest` states this and stops with `exit 2`. In such a project set `CI agent: command` in the `## Review and merge` section of `conventions.md` (the platform's own event-driven PR integration, or any other command). **This does not affect local use:** in the interactive Antigravity interface every phase of the framework runs.

### 18.1.1 The planning and logging process (Planning Mode)
The agent logs in its own internal application folder (`~/.gemini/antigravity-cli/brain/`), so these files do not pollute the project's Git repository:
* **Planning stage:** the `implementation_plan.md` plan file, awaiting approval.
* **Execution stage:** the `task.md` to-do list.
* **Validation stage:** the `walkthrough.md` summary.

### 18.1.2 Handling permissions (Permissions)
* **File modifications:** allowed inside the Trusted Workspace.
* **External commands:** they require manual confirmation before running (`Ask` mode).
* **Delegation:** `/permissions` or `/config` (Allow), `--dangerously-skip-permissions` (per session), or `~/.gemini/antigravity-cli/settings.json` (global).

### 18.1.3 Starting the skills and agents (using the TUI)
After the integration script has run, you can start the skills of the individual phases in two ways in the Antigravity interface:
* **Slash commands:** every loaded skill automatically becomes a unique slash command in the prompt. The name of the command comes from the `name` field given in the frontmatter of `SKILL.md` (without the serial number). For example, to start phase 05, simply type:
  ```
  /bs-analyze
  ```
* **An interactive selection menu:** by typing the `/skill` (or `/skills`) command, a visual menu pops up in the terminal, from which you can select the desired phase with the arrows (`↑/↓`) and bring it to life with the `enter` key.
* **Listing the custom agents:** with the `/agens` (or `/agent`) command you can view the registered, individually configured subagents.

## 18.2 Codex CLI (OpenAI)

If you use the **Codex CLI**, the installer works into two different places, because Codex expects the agents and the skills in a different format/location:

1. **Subagents → `.codex/agents/<name>.toml`.** Codex subagents are **TOML** files (not markdown). The installer automatically translates the markdown agent definitions into TOML, and fills in:
   * `name`, `description` (from the agent's `role`), `developer_instructions` (the full agent prompt);
   * `model` and `model_reasoning_effort` — these **take effect natively** (the value given in the file takes precedence over the spawn/`[agents]` default/parent value);
   * `sandbox_mode = "read-only"` for the read-only agents (`analyzer`, `researcher`, `doc-sync-planner`).
   * During a run the subagents can be listed with the `/agent` command, and you can switch between them.
2. **Skills → `.agents/skills/bs-<name>/SKILL.md`.** Codex reads the **project-level** skills from the `.agents/skills/` folder (`.codex/skills` is only a legacy, user-level location — it is not found at project level). The skills are available as slash commands (e.g. `/bs-analyze`).

> ⚠️ **Codex ↔ Antigravity mutual exclusion.** The `.agents/skills/` folder is used by **both Codex AND Antigravity**, so in practice only one of the two can be installed into a given project. The installer watches for this: it warns you in advance when the platform is selected, and if the other platform is already present (`.codex/agents/` ↔ `.agents/agents/`), it asks before the installation whether you want to continue.

---
