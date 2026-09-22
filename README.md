```text
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                                                                      ║
    ║   ██████╗ ███████╗██████╗ ██╗  ██╗██╗███████╗██████╗ ███████╗ ██████╗║
    ║   ██╔══██╗██╔════╝██╔══██╗██║ ██╔╝██║██╔════╝██╔══██╗██╔════╝██╔════╝║
    ║   ██████╔╝█████╗  ██████╔╝█████╔╝ ██║███████╗██████╔╝█████╗  ██║     ║
    ║   ██╔══██╗██╔══╝  ██╔══██╗██╔═██╗ ██║╚════██║██╔═══╝ ██╔══╝  ██║     ║
    ║   ██████╔╝███████╗██║  ██║██║  ██╗██║███████║██║     ███████╗╚██████╗║
    ║   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚══════╝╚═╝     ╚══════╝ ╚═════╝║
    ║                                                                      ║
    ╚══════════════════════════════════════════════════════════════════════╝
```

**HUN version → [README-HU.md](README-HU.md)**

<!-- TOC -->

- [Berki-spec](#berki-spec)
  - [1. Two development routes — choose by the size of the task](#1-two-development-routes--choose-by-the-size-of-the-task)
    - [1.1 Before either route (optional): /bs-brainstorm](#11-before-either-route-optional-bs-brainstorm)
  - [2. Installation](#2-installation)
    - [Installation steps:](#installation-steps)
    - [Supported platforms and agents:](#supported-platforms-and-agents)
    - [Language settings — two independent axes](#language-settings--two-independent-axes)
    - [How can it be used?](#how-can-it-be-used)
  - [3. Quick start](#3-quick-start)
    - [The operating principle of the framework:](#the-operating-principle-of-the-framework)
    - [Two development routes:](#two-development-routes)
    - [Basic commands (slash commands):](#basic-commands-slash-commands)
  - [4. The full berki spec flow (00–09)](#4-the-full-berki-spec-flow-0009)
    - [4.1 High-level summary](#41-high-level-summary)
    - [4.2 Test points — where we test, and what it proves](#42-test-points--where-we-test-and-what-it-proves)
    - [4.3 Automatic selection of models and effort levels](docs/en/model-selection.md)
    - [4.4 The 05-analyze self-healing loop (in detail)](#44-the-05-analyze-self-healing-loop-in-detail)
    - [4.5 The 07-validate self-healing loop (in detail) — tests + code review](#45-the-07-validate-self-healing-loop-in-detail--tests--code-review)
    - [4.6 Self-healing loops (analyze + validate) — shared conventions](#46-self-healing-loops-analyze--validate--shared-conventions)
    - [4.7 Example prompt flow (walking through one cycle)](#47-example-prompt-flow-walking-through-one-cycle)
  - [5. Simplified (lightweight) flow](#5-simplified-lightweight-flow)
    - [5.1 Flowchart](#51-flowchart)
    - [5.2 The three phases in brief](#52-the-three-phases-in-brief)
    - [5.3 Two built-in loop breakers](#53-two-built-in-loop-breakers)
    - [5.4 Optional agents (all read-only, none of them mandatory)](#54-optional-agents-all-read-only-none-of-them-mandatory)
    - [5.5 Starter prompt (copy-paste)](#55-starter-prompt-copy-paste)
    - [5.6 Example prompt](#56-example-prompt)
  - [6. Skill index](#6-skill-index)
  - [7. Agent index](#7-agent-index)
  - [8. Frontmatter schema](#8-frontmatter-schema)
  - [9. conventions.md — Project conventions](#9-conventionsmd--project-conventions)
    - [Branching strategy — cycle = branch (in phase 01)](#branching-strategy--cycle--branch-in-phase-01)
    - [Parallel cycles — a design window with a worktree (PW1/PW2, BD16)](#parallel-cycles--a-design-window-with-a-worktree-pw1pw2-bd16)
    - [A fresh base before the analyze (BR1)](#a-fresh-base-before-the-analyze-br1)
    - [An integration refresh before the merge (W2)](#an-integration-refresh-before-the-merge-w2)
    - [The phase-closing commit (PC1)](#the-phase-closing-commit-pc1)
  - [10. The artifact files of a cycle](#10-the-artifact-files-of-a-cycle)
    - [10.1 The handover between phases (*-input-from-prev.md)](#101-the-handover-between-phases--input-from-prevmd)
  - [11. docs-generated/ — living documentation (owned by 08-doc-sync)](#11-docs-generated--living-documentation-owned-by-08-doc-sync)
    - [11.1 specs/test-conventions.md — recurring test expectations and recipes (TC1–TC11)](#111-specstest-conventionsmd--recurring-test-expectations-and-recipes-tc1tc11)
    - [11.2 export/ — versioned PDF export (/bs-export-doc)](#112-export--versioned-pdf-export-bs-export-doc)
    - [11.3 test-runs/ — running tests outside a cycle (/bs-run-tests)](#113-test-runs--running-tests-outside-a-cycle-bs-run-tests)
  - [12. Question handling (spec-questions.md / plan-questions.md / tasks-questions.md / doc-sync-questions.md)](#12-question-handling-spec-questionsmd--plan-questionsmd--tasks-questionsmd--doc-sync-questionsmd)
  - [13. A uniform Done status lifecycle](#13-a-uniform-done-status-lifecycle)
  - [14. Sonar quality check](#14-sonar-quality-check)
  - [15. The decision log (imp-decision.md)](#15-the-decision-log-imp-decisionmd)
  - [16. The validation report (validation-report.md)](#16-the-validation-report-validation-reportmd)
  - [17. The reviewer agent (agents/reviewer.md)](#17-the-reviewer-agent-agentsreviewermd)
  - [18. Agent-specific integration](#18-agent-specific-integration)
  - [Appendix — The detailed process diagram](#appendix--the-detailed-process-diagram)
    - [18.0 A platform limitation: running commands in the subagents (EX1)](#180-a-platform-limitation-running-commands-in-the-subagents-ex1)
    - [18.1 Antigravity CLI (Google DeepMind)](#181-antigravity-cli-google-deepmind)
      - [18.1.1 The planning and logging process (Planning Mode)](#1811-the-planning-and-logging-process-planning-mode)
      - [18.1.2 Handling permissions (Permissions)](#1812-handling-permissions-permissions)
      - [18.1.3 Starting the skills and agents (using the TUI)](#1813-starting-the-skills-and-agents-using-the-tui)
    - [18.2 Codex CLI (OpenAI)](#182-codex-cli-openai)

<!-- /TOC -->

# Berki-spec

**Berki-spec** is a **spec-driven development (SDD)** framework for developing software with AI agents. It breaks the work into independently testable **cycles**, and drives every cycle down the same disciplined path — from capturing the requirement (`spec`) through the technical design (`plan`) and the task list (`tasks`) to implementation, validation and merge. The process is built from two kinds of building block: **skills** (phase recipes run by the main agent) and **agents** (dedicated specialists invoked as `Task tool` subagents).

> **Status: alpha — there is no stable release yet.** The prompt contracts are hardened round by round, so an update can bring **breaking changes** to an already-installed project (a renamed artifact or cycle folder, a new mandatory gate). If you need a fixed state, install from a tagged version or pin a commit instead of following `main`.

**What makes it different from the SDD tools on the market?**

Most SDD templates give you a single, rigid "spec → plan → code" thread. Berki-spec goes further — and the difference is not in the phases, but in **what happens when reality diverges from the plan**:

- **Adaptive, two-speed flow.** For a large task, the full (00–09) process with its quality gates; for a small, well-bounded task, a simplified three-phase route (`spec → task → implementation`). The two are **interchangeable mid-flight** — no needless ceremony for a configuration change, and no under-design for a complex feature.
- **Self-healing quality loops, with anti-"cheating" discipline.** The `analyze`, `validate` and `review` phases do not merely *report* a defect, they **fix it automatically** in an orchestrated loop. The key rule: the **code adapts to the contract** (test / DoD / review finding), **never the other way round** — the loop does not weaken a test to make it green. If something could only be resolved by changing the contract, it **escalates upwards** into the design phase, in front of a human.
- **Living, "as-built" documentation with drift tracking.** `docs-generated/` stays in sync with the code cycle by cycle, driven through an **objective consistency gate**, and separately records the **deviations of the implemented system from the HLD/LLD intent** (design drift). Documentation does not go stale silently.
- **Interruption-safe, resumable anywhere.** Every phase keeps its state and its open questions in files (we **never delete** from the list, we only tick `[x]`), with status markers — a new session picks up exactly where the previous one stopped.
- **Human gates at the decisions.** Phase transitions are bound to **explicit approval**: the agent proposes and justifies, but does not "run away with it" — the choice of scope and direction stays with the developer.
- **Tool-independent, from a single source.** The same skill/agent definition (single source of truth) runs under Claude Code, Cursor, Antigravity and Codex alike.
- **Optimised for weak/cheap models.** Deterministic safety nets (narrowed fix-mode entry points, mandatory checklists, one question at a time) reduce the chance of error even when it is not the strongest model driving.
- **Maximum token saving — task-proportional model and reasoning-level selection.** Every step runs on the **cheapest agent sufficient for it**, tuned on **two independent axes**: the *model* (which model) and the *effort* (how many reasoning/thinking tokens). The most expensive (Opus-class) model is granted to **exactly one** point: the most critical reasoning, the consistency diagnosis of the `analyzer`. The fixers that correct a precise defect list and the mechanical runners work at **low effort** (on the `default` model too), because they do not have to discover the problem. Code search, test execution and the deterministic steps are done by cheap subagents and scripts, sparing the main context. For the full allocation see [section 4.3](docs/en/model-selection.md).

## 1. Two development routes — choose by the size of the task

The user has **two routes**; the weight of the task decides which one fits:

1. **The full berki spec flow (phases 00–09)** — for larger, more complex developments. Separate `spec.md` → `plan.md` → `tasks.md` documents, with cross-phase `analyze`, `validate`, `doc-sync` and `review` quality gates and self-healing loops. On an empty project it starts with the `00-init-project` skill, for a new cycle with `01-add-cycles`. The rest of this README describes this route.

2. **The simplified (lightweight) flow** — for small, well-bounded tasks that can be solved in 3-4 steps (e.g. **assembling a configuration**, **writing a simpler script**, a minor fix). A single three-phase recipe: `spec-plan.md` → `tasks.md` → implementation, in the `/bs-quick-flow` skill. Both artifacts carry a **status field**, so the phase boundary is a committed fact (`/bs-cycle-status` reads it from there too). There is no separate plan/bs-analyze/bs-validate/bs-doc-sync phase; it calls the optional agents (`researcher`, `analyzer`, `reviewer`) only when they genuinely help.

**How to decide?**

| Characteristic | Simplified flow | Full berki spec flow |
|---|---|---|
| Typical task | configuration, simple script, minor fix | new feature, several components, complex logic |
| Size | solvable in 3-4 steps | self-contained, vertically sliceable cycle(s) |
| Documents | `spec-plan.md` + `tasks.md` (both with a status field) | `spec.md` + `plan.md` + `tasks.md` |
| Quality gates | inline + optional agents | `analyze` / `validate` / `doc-sync` / `review` loops |
| Entry point | `/bs-quick-flow` | `/bs-init-project` / `/bs-add-cycles` |

**Default flow:** the character of the project is clarified in the `00-init-project` phase (product development vs. configuration/scripting), and based on that a **default flow** is written into the **Default flow** field of the `## Development methodology` section of `conventions.md`. That is the starting point — it can be overridden per task.

The two routes are **interchangeable**: if during the simplified flow it turns out that the task outgrows it (more code to write, several components, complex design), the skill stops the work and **redirects to the full process** (`01-add-cycles`). And the other way round: `01-add-cycles` and `03a-write-code-plan` will flag it if the task is too simple for a full cycle, and suggest the simplified flow.

### 1.1 Before either route (optional): `/bs-brainstorm`

The **shared antechamber** of the two routes is the `/bs-brainstorm` helper command — for the case when the question is not yet the *size*, but **what and how** we want at all. ("How should we implement central certificate management?", "Is it worth extracting auth?") This gap sits **before** the `00–09` flow: `01-add-cycles` already assumes that you know what you want (it only has to be split into cycles), and `/bs-quick-flow` assumes the task is small and clear.

**What it does:**
- **Orients itself** in the project: `conventions.md`, `docs-generated/system-overview.md` (the as-built truth), `docs-generated/README.md` (folder index), `specs/roadmap.md` — and, depending on the topic, `architecture.md` and `design-drift.md`. Grinding through the whole `specs/` tree is forbidden (BS6).
- **It explores the codebase with cheap, parallel `researcher` subagents** (Mode B, read-only, cheapest tier, "never raw file content") — so the context of the conversation carries a list of findings rather than dozens of files (BS7).
- **It converses, it does not monologue:** **one** question at a time, for every proposal **2–3 alternatives with trade-offs + an explicit recommendation**, mandatory fitting to the existing system and to `conventions.md`, and sycophancy is forbidden — a risk that was not raised is the agent's fault (BS8–BS13).
- **It persists:** the material of the session goes into the `.bs-brainstorm/brainstorm-NN-<slug>.md` working file with a fixed skeleton (*Goal · Discovered facts with sources · Alternatives · Decisions · Open questions · Proposed cycle split · Log*). After every substantive round it **grows** — it is never rewritten (BS14). So it can be continued after a `/clear`, a crash or a return days later: `/bs-brainstorm let's continue number 04`.

**Hard limits (BS1):** it writes no code, runs no `git`, and modifies **not a single file** outside the `.bs-brainstorm/` folder — with one exception: on the first run it offers to add the `.bs-brainstorm/*` entry to `.gitignore` (after approval, once). At the end it **recommends**, but does not enter the next skill.

**The bridge towards the flow (BS18):** the raw working file is **local and gitignored** (raw thinking, not a deliverable) — whatever is worth keeping is distilled into the cycle's `cycle-design-input.md`, and *that* is what gets committed:

```
/bs-brainstorm how should central cert management work
        ↓                      .bs-brainstorm/brainstorm-04-central-cert.md   (gitignored)
/bs-add-cycles brainstorm: 04
        ↓                      specs/cycle-NN-<name>/cycle-design-input.md    (committed)
/bs-write-spec
```

`01-add-cycles` takes the `## 6. Proposed cycle split` section as the starting point of the roadmap proposal, and asks the unticked items of `## 5. Open questions` **as questions** — whatever the working file already answers, it does not ask again. **One bridge, one direction:** `02-write-spec` does not read the brainstorm, it reads `cycle-design-input.md`.

## 2. Installation

Setting up the BerkiSpec framework in the target project is extremely simple and automated with the help of the bundled installer script.

> **⚠ Updating an existing project — the family of the cycle end is NOT backwards compatible.** `09-merge` split into five skills (`bs-review-and-merge` · `bs-create-pr` · `bs-review` · `bs-merge` · `bs-dev-test`), and the framework has **no notion of versions**: there is no alias, no fallback to the old behaviour, no migration machinery. The update is therefore a **re-installation** (the installer replaces the old `bs-merge/` folder as well), plus adding the new `## Review and merge` section to `conventions.md` — by re-running `00-init-project` or by hand (the template lives in the `00` skill). **The artifact data ALREADY PRESENT in the project is a separate question:** in the `Phase` column of the `plan.md` of a running cycle, an empty cell and the `both` value are **still accepted on read** (with the old meaning and a WARN) — but a new plan can no longer write them. The re-installation does not rewrite these.

### Installation steps:
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

### Supported platforms and agents:
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

### Language settings — two independent axes

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

### How can it be used?
After installation the given platform reads the symlinked definitions automatically:
* **Google Antigravity CLI / Claude Code / Cursor Agent CLI / Codex CLI:** Start the CLI in the folder of the target project (with the `agent` command in the case of Cursor). In the chat interface you can bring up the list of skills by pressing the `/` (slash) character. Every skill appears uniformly under the name `berkispec - <phase>: <description>`, so you can see the order and purpose of the SDD steps immediately. To start, invoke the `bs-init-project` skill! (In Codex you can list/switch between subagents with the `/agent` command.)
* **GitHub Copilot:** In the Copilot Chat window or in the Copilot CLI you can activate the instructions of the desired phase directly with the `@` symbol (e.g. `@bs-init-project`).

---


## 3. Quick start

BerkiSpec is a disciplined, spec-driven development (SDD) framework for pair programming with AI agents.

### The operating principle of the framework:
* **Cycles:** development is divided into well-bounded units (cycles) that can be described with an unambiguous goal and kept easily under control. Every new cycle gets its own Git branch, and all design and logging documents of the cycle go into the `specs/cycle-NN-<cycle-name>/` folder in the project root.
* **Phases:** every cycle is broken down into strict phases that lead the process from the requirements through to implementation and merge.

### Two development routes:
Depending on the complexity of the task, two flows are available:
1. **Full SDD flow:** produces a detailed specification (`spec.md`), a technical plan (`plan.md`) and a task list (`tasks.md`), and runs automatic self-healing quality loops (analyze, validate, review).
2. **Lightweight flow:** for smaller changes, configurations or simple scripts. It runs in one step, without a separate phase breakdown.

### Basic commands (slash commands):
After installation you can reach the skills in the platform's chat interface by pressing the `/` character:

* **`/bs-init-project`**: the very first initialisation of the project (creates the `conventions.md` file).
* **`/bs-add-cycles`**: adding a new development cycle to the roadmap (`roadmap.md`).
* **`/bs-write-spec`**: capturing the requirements, producing the specification of a new cycle (`spec.md` + `spec-questions.md`).
* **`/bs-write-code-plan`**: the **code side** of the technical implementation plan (the code sections of `plan.md` + `plan-questions.md`) — coordinates, planned changes, configuration, schema.
* **`/bs-write-test-plan`**: the **test half** of the same `plan.md` — `TS-NN` scenarios, the machine-readable run table, environment preparation, test-file data sheets.
* **`/bs-write-tasks`**: breaking the technical plan down into measurable tasks (`tasks.md` + `tasks-questions.md`).
* **`/bs-analyze`**: cross-phase consistency check and automatic correction (spec/plan/tasks agreement).
* **`/bs-implement`**: actual code development based on the task list, recording the progress in `tasks.md`.
* **`/bs-validate`**: checking tests, lint, build **and code review** (reviewer agent) in a single automatic fixing loop (after a successful run, the 'Done' status).
* **`/bs-doc-sync`**: synchronising the living documentation (`docs-generated/`) and the READMEs with the code changes, and maintaining `specs/test-conventions.md` (recurring test expectations and recipes).
* **`/bs-review-and-merge`**: closing the cycle **in one step** when there is no PR submission (`PR submission: no`): bringing the main branch into the cycle branch → **post-merge test round** (`VP2`: tests + Sonar) → merge with mandatory user confirmation (RD8). The code review has already run in `/bs-validate`.
* **`/bs-create-pr` → `/bs-review` → `/bs-merge`**: the same **in three steps** when there is a PR submission (`PR submission: yes`) — opening the PR, the review running on the PR (a **machine run** in centralized SDD), and finally the merge after the `VP2` round. On both paths `VP2` is the gate **before** the code reaches the main branch.
* **`/bs-dev-test`** *(optional, only on the centralized path)*: after a successful merge it deploys into an integrated test environment and runs **real e2e tests** against it (`VP3`). When it is switched on, the cycle closes with the green result of this round.
* **`/bs-cycle-status`**: checking the status of the cycles (interactive TUI or command-line status).
* **`/bs-brainstorm`**: exploratory ideation and joint design **before the spec** — with a persistent working file (`.bs-brainstorm/`) and cheap `researcher` exploration; at the end it hands over to `/bs-add-cycles` or `/bs-quick-flow`.
* **`/bs-quick-flow`**: starting the simplified (lightweight) flow for small tasks (spec → task → implementation).
* **`/bs-export-doc`**: versioned PDF export from the markdown docs (together with the mermaid diagrams) into the `export/` folder — with no parameter, from `architecture.md` and `system-overview.md`.
* **`/bs-manual-test-plan`**: assembling the **manual test plan** for the cycle (`manual-test-plan.md`): component startup, test data, manual call sequences (`curl` + `.http`), expected results and the location of the automated test results. Two modes: `Planned` (before implementation, based on `plan.md`) or `As-built` (after validation, verified against the code). Its prerequisite is the `PASS` status of `analyze-report.md`; it is not a phase, it does not change the cycle status, and it can be re-run at any time (it preserves the manual additions).
* **`/bs-run-tests`**: **running tests outside a cycle**, per category (`unit`, `rest-e2e`, `ui` — according to the dictionary of the project). It runs from the project-level table of the `## Test execution` section of `conventions.md`, and writes into the gitignored `test-runs/<category>/<UTC-timestamp>/<env>/` tree, with a per-category `latest.json` pointer. It is not a phase, and its result is **never cycle evidence** — see section 11.3.

---
