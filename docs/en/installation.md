# Installation

← [Back to the main page](../../README.md) · [Page index](README.md)

Setting up the BerkiSpec framework in the target project is extremely simple and automated with the help of the bundled installer script.

> **⚠ Updating an existing project — the family of the cycle end is NOT backwards compatible.** `09-merge` split into five skills (`bs-review-and-merge` · `bs-create-pr` · `bs-review` · `bs-merge` · `bs-dev-test`), and the framework has **no notion of versions**: there is no alias, no fallback to the old behaviour, no migration machinery. The update is therefore a **re-installation** (the installer replaces the old `bs-merge/` folder as well), plus adding the new `## Review and merge` section to `conventions.md` — by re-running `00-init-project` or by hand (the template lives in the `00` skill). **The artifact data ALREADY PRESENT in the project is a separate question:** in the `Phase` column of the `plan.md` of a running cycle, an empty cell and the `both` value are **still accepted on read** (with the old meaning and a WARN) — but a new plan can no longer write them. The re-installation does not rewrite these.

## Installation steps:
1. Open a terminal in the root of the `berkispec` repository.
2. Run the installer script:
   * **Linux/macOS:**
     ```bash
     ./install.sh
     ```
   * **Windows (PowerShell):**
     ```powershell
     .\install.ps1
     ```
3. The script greets you interactively and asks for the root folder of your target project.
   * *Tip:* while typing the path you can auto-complete folder names with the **Tab** key, and **pressing Tab twice** lists the contents of the current directory.
   * **On reinstall the most recent target folder is offered automatically** — on Linux/macOS it appears pre-filled (Enter = accept, editable with the arrow keys), on Windows the script prints it and accepts it on an empty Enter. For this the installer uses the **`history`** file in the repo root (`LAST_PROJECT_PATH`, `LAST_PLATFORM`, `LAST_INSTALL`). The file is machine-specific, so `.gitignore` excludes it; if the folder stored in it has disappeared in the meantime, the script says so and asks for a new one.
4. Select the AI agent platform you use (1–6).
5. Select the **two languages** — see the *Language settings* section below. Both have a default, acceptable with Enter:
   * **Language of the prompts** (what the agent *reads*): `1) English [default]` / `2) Magyar`
   * **Language of the project** (what the agent *writes*): `1) Magyar [default]` / `2) English`

**Non-interactive (scripted) installation.** If you give **no** flag at all, the interactive route above runs unchanged. With flags, however, it can be automated:

```bash
./install.sh --platform claude --prompt-lang en --project-lang hu --path ~/project
```

| Flag (`install.sh`) | PowerShell | Value | Default |
|---|---|---|---|
| `--platform` | `-Platform` | `claude` \| `codex` \| `antigravity` \| `cursor` \| `copilot` | — (asks) |
| `--prompt-lang` | `-PromptLang` | `hu` \| `en` | `en` |
| `--project-lang` | `-ProjectLang` | `hu` \| `en` | `hu` |
| `--path` | `-Path` | the directory of the target project | — (asks) |
| `--force` | `-Force` | overwrite on conflict | — |
| `--help` | `-Help` | help | — |

If flags are given partially, it uses the ones provided and asks for the rest interactively. **On a conflict without `--force` the non-interactive mode STOPS** — it does not overwrite silently.

## Supported platforms and agents:
The framework can set up the environment for five popular developer platforms:
1. **Google Antigravity CLI:**
   * Creates the `.agents/` configuration folder in the project root.
   * Links the agents into the `.agents/agents/<name>/agent.json` folder structure, and the skills into the `.agents/skills/bs-<name>/SKILL.md` directory.
   * ⚠️ **Interactive use only.** Measured on 2026-09-22 with CLI 1.107.0: there is **no headless mode** (`antigravity chat "<prompt>"` opens a GUI chat session), so Antigravity **cannot run the cycle on a CI runner**. This matters only for **centralized SDD**, where the CI drives `bs-review`/`bs-merge`: there choose `CI agent: command` (see section 9, `## Review and merge`). For local, interactive work Antigravity is fully supported.
2. **Claude Code:**
   * Creates the `.claude/` configuration folder in the project root.
   * Links the agents in `.claude/agents/<name>.md` (Markdown) format, and the skills under `.claude/skills/bs-<name>/SKILL.md`.
3. **Cursor (Agent CLI):**
   * Creates the `.cursor/` configuration folder in the project root.
   * Links the subagents in `.cursor/agents/<name>.md` (Markdown) format (the read-only agents get `readonly: true`), and the skills under `.cursor/skills/bs-<name>/SKILL.md`.
4. **GitHub Copilot (CLI & IDE):**
   * Creates the `.github/` configuration folder in the project root.
   * Links the agents as `.github/agents/<name>.agent.md` files, and arranges the skills as global instructions in `.github/instructions/bs-<name>.instructions.md`.
5. **Codex CLI:**
   * Creates the subagents as `.codex/agents/<name>.toml` **TOML** files (with native `model` + `model_reasoning_effort` fields; the read-only agents get `sandbox_mode = "read-only"`).
   * Places the skills under `.agents/skills/bs-<name>/SKILL.md` — Codex reads project-level skills from there.
   * ⚠️ **Caution:** Codex and Antigravity use a **shared** `.agents/skills/` folder, so only one of the two can be installed into a given project. The installer warns and asks if the other one is already present.

## Language settings — two independent axes

The framework knows **two mutually independent** language settings. They are not the same thing, and they **do not have to match**:

| Setting | What it determines | Default |
|---|---|---|
| **Language of the prompts** | The language of the **instructions the agent reads** (the language of the `skills-*` / `agents-*` / `shared-*` tree). It does not affect your documents. | **English** |
| **Language of the project** | The language the **agent writes in**: `spec.md`, `plan.md`, `tasks.md`, `conventions.md`, reports, `docs-generated/` — and the language it **answers you** in, in the chat. | **Magyar** |

**The four combinations:**

| Prompt | Project | When this is the right one |
|---|---|---|
| **EN** | **HU** | *The default.* Hungarian team, Hungarian deliverable documentation — but the agent gets English instructions, which are cheaper in tokens and which weaker/cheaper models follow more accurately. |
| HU | HU | If you want to read/maintain the prompt text in Hungarian too. |
| EN | EN | International project. |
| HU | EN | Rare, but valid: Hungarian maintainer, English deliverable. |

**Both are decided at install time and are WIRED IN to the installed prompts.** **No language field of any kind is written into the project** — neither into `conventions.md` nor anywhere else — therefore:

- afterwards it can be changed **only by reinstalling**;
- for an existing project there is **no migration to do**: until you reinstall, everything stays as it was;
- the installer's **closing summary prints both languages** — this is the only place where you are confronted with your choice.

> **The main risk: language bleed.** With English instructions + a Hungarian project, the model (especially a weaker one) tends to bleed English words into the Hungarian document, or to write the whole artifact in English. The main weapon against this is the **`output-language` block**: at the very beginning of every skill and every agent — right after the H1 — a block is inserted which states, **in the language of the project**, what has to be written in that language (artifacts, sentences addressed to the user), what stays English (identifiers, file names, commands, rule IDs), and that **mixing is a defect to be fixed**. A rule phrased in the target language is at once an instruction and a linguistic anchor — it measurably holds better than a "write in Hungarian" phrased in English.

> **The gate scripts follow the language of the project too.** The deterministic gates (report gate, DoD check, round log, analyze gate, TC8) do not match on hardcoded Hungarian text: the installer writes the dictionary of the chosen project language next to the scripts (`lang-keys.json`), and the scripts take the section titles, field names and status values from it. So what they *search for* and what they *write* into the artifact is in the language of the project. Their input, on the other hand, is **language-independent**: they accept the forms of both languages, so a project that started in Hungarian does not fall out after an English reinstall.
>
> **⚠️ One remainder with `project = English`:** the **console messages** of the gate scripts are Hungarian (these address the runner and the agent, they never end up in an artifact). The installer flags this separately at the point of choice.

## How can it be used?
After installation the given platform reads the symlinked definitions automatically:
* **Google Antigravity CLI / Claude Code / Cursor Agent CLI / Codex CLI:** Start the CLI in the folder of the target project (with the `agent` command in the case of Cursor). In the chat interface you can bring up the list of skills by pressing the `/` (slash) character. Every skill appears uniformly under the name `berkispec - <phase>: <description>`, so you can see the order and purpose of the SDD steps immediately. To start, invoke the `bs-init-project` skill! (In Codex you can list/switch between subagents with the `/agent` command.)
* **GitHub Copilot:** In the Copilot Chat window or in the Copilot CLI you can activate the instructions of the desired phase directly with the `@` symbol (e.g. `@bs-init-project`).

---
