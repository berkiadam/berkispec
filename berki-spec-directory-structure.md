# Berki-spec — directory structure reference

This document describes **what every folder and file is for** — both in this repository and in a target project after installation. It is the detailed companion of [`README.md`](README.md) (Hungarian: [`README-HU.md`](README-HU.md)).

There are **two distinct trees** to keep apart:

| Tree | What it is | Who maintains it |
|---|---|---|
| **This repository** (`berkispec/`) | The **source of truth** of the framework: the prompts, the shared blocks, the language content and the gate scripts. No project ever runs from here directly. | The framework maintainer, by hand |
| **The target project** | What `install.sh` copies in (platform folders + scripts) **plus** everything the flow produces during work (`specs/`, `docs-generated/`, reports). | The installer + the phases 00–09 |

---

## 1. This repository — the framework source

The framework consists of a single folder, `prompts/`, plus the installer in the root. Everything under `prompts/` exists in **two prompt-language trees** (`-hu` / `-en`) with identical file names and identical structure; the tables below name the `-hu` variant, but every row has an `-en` pair.

### 1.1 The repository root

| Path | What it is for |
|---|---|
| `README.md` | The full framework documentation in **English**. The starter prompt block for the user lives in it, and it is the canonical description of the flow. |
| `README-HU.md` | The same documentation in **Hungarian**. The two files are kept in sync by hand; a structural change belongs in both. |
| `berki-spec-directory-structure.md` | This file — the detailed folder/file reference. |
| `install.sh` / `install.ps1` | The installer entry points (Linux/macOS and Windows PowerShell). They collect the target folder, the platform and the two languages interactively, or accept them as flags (`--platform`, `--prompt-lang`, `--project-lang`, `--path`, `--force`), then hand the work to `prompts/scripts/install-helper.py`. |
| `history` | Machine-specific installer memory (`LAST_PROJECT_PATH`, `LAST_PLATFORM`, `LAST_INSTALL`) so that a reinstall can offer the previous target. Excluded by `.gitignore`. |
| `docs/` | Hand-written illustrations for the documentation (e.g. `worktree-vscode-source-control.png`). Not generated. |
| `prompts/` | Everything the framework consists of — see below. |

### 1.2 `prompts/skills-<lang>/` — the phase skills

A **skill is a recipe**: a static methodology that the **main agent** runs. The folder name carries the **prompt language** (`skills-hu/` ↔ `skills-en/`); the two trees are fully symmetrical, with identical file names and identical structure.

| File | What it is for |
|---|---|
| `00-init-project.md` | Project initialisation: it interviews the user about the conventions (tech stack, ports, test tooling, report table, merge strategy, Sonar) and writes `conventions.md`. Runs once per project, on its own `feature/init-project` branch. |
| `01-add-cycles.md` | Cycle management: it creates/maintains `specs/roadmap.md`, allocates the next cycle number (by scanning branches, BQ2), creates the cycle folder and the cycle branch. This is where the parallel-worktree offer (PW3) lives. |
| `02-write-spec.md` | Writes `spec.md`: business behaviour, requirements, test specification, Definition of Done with `DoD-NN` identifiers. It filters environment coordinates out of the spec (KX) and hands them on instead of deleting them. |
| `03a-write-code-plan.md` | Writes the **code half** of `plan.md`: the self-contained technical execution plan — environment coordinates (KO1), the target environment (EV1), the planned changes with a purpose (WY1), the configuration lifecycle (KF1), the schema artifacts and the reverse coverage (SC1). It closes with `analyze-gate-check.py --plan-code-only` and the `Ready for test planning` status. |
| `03b-write-test-plan.md` | Writes the **test half** of the same `plan.md`: the `TS-NN` test scenarios (TS1–TS8, with the `.http` form), the machine-readable run table (TP4/PH1), the E2E infrastructure (TP3), the regression impact and the test specification (TI1, the `TA1` data sheets, spec coverage TS7). Its entry gate runs `--plan-code-only` itself (D5); it closes with the full `--plan-only` gate. The longest skill in the framework. |
| `04-write-tasks.md` | Writes `tasks.md`: the checkboxed task list with `[RED]`/`[GREEN]`/`[CHECK]`/`[OPS]` markers, and the plan links (`[P-…]`, PID1). |
| `05-analyze.md` | Cross-phase consistency check and the self-healing loop that follows it. A read-only orchestrator: it runs the mechanical gate, starts four parallel diagnostician rounds, conducts the triage, and drives the fixer subagents. |
| `06-implement.md` | Implementation: it works through the task list **in a single run** (IM1), ticks the tasks, writes `check-log.md`, and commits per task. Its **Fix mode** section is the delegation target of `implement-fixer`/`review-fixer`. |
| `07-validate.md` | Validation + code review in one loop: fast tests → the static layer (Sonar + reviewer) → heavy tests → the DoD/gates. The most script-driven phase (VD11/b). |
| `08-doc-sync.md` | Keeps `docs-generated/` and `specs/test-conventions.md` up to date: plan → mechanical execution → an objective gate. Not a self-healing subagent loop. |
| `09-merge.md` | Merges the cycle branch (local squash or PR), with the status/review/doc-sync gates and mandatory manual confirmation (RD8). |
| `brainstorm.md` | *(Not a phase.)* Exploratory ideation **before** the flow, with a persistent working file in `.bs-brainstorm/`. It writes nothing outside that folder (BS1). |
| `quick-flow.md` | *(A separate route.)* The simplified three-phase flow (`spec.md` → `task.md` → implementation) for small tasks. |
| `cycle-status.md` | *(Helper command.)* Reports the status of the cycles; it runs `cycle-status.py`. |
| `export-doc.md` | *(Helper command.)* Versioned PDF export from the markdown docs; it runs `export-doc.py`. |
| `manual-test-plan.md` | *(Helper command.)* Assembles the manual test plan (`manual-test-plan.md`) for a human to walk the cycle through. Zero feedback into the flow (MT4). |

### 1.3 `prompts/agents-<lang>/` — the specialist agents

An **agent is a specialist executor**: a dedicated system prompt that a skill starts **as a Task tool subagent**, so that the reading it does never lands in the main context.

| File | What it is for | Read-only |
|---|---|---|
| `analyzer.md` | Cross-phase **semantic** consistency diagnosis (categories 1–5) in phase 05, in three parallel rounds with a scope parameter. The only agent on the most expensive model tier. | yes |
| `analyzer-exec.md` | **Executability** diagnosis (category 6) from the plan + tasks + the gate's inventory, in parallel with the `analyzer`. | yes |
| `reviewer.md` | Code review on the cycle diff as step 2 of the 07 round → `code-review.md` with `MF-NN` / `S-NN` identifiers. | yes |
| `researcher.md` | Codebase and document research (Mode A for 03, Mode B for 00/01/02/06 and the brainstorm). The cheapest tier; its contract is "a summary, never raw file content". | yes |
| `test-runner.md` | The mechanical execution of tests/Sonar/E2E in 07 — a factual summary, no PASS/FAIL decision. The fallback when `plan.md` has no machine-readable run table. | no |
| `doc-sync-planner.md` | The read-only planner of phase 08: a per-file tickable plan **plus** the finished replacement texts (a surgical patch). | yes |
| `spec-fixer.md` · `plan-fixer.md` · `tasks-fixer.md` | The fix-mode entry points of the 05 loop for phases 02/03/04. Thin wrappers: the fix-mode section and the phase's quality gate are inlined into them at build time (D13), so they never read a phase skill. | no |
| `implement-fixer.md` | The fix-mode entry point of the 07 loop for test/Sonar/DoD failures (`## Validation fixes`). | no |
| `review-fixer.md` | The fix-mode entry point of the 07 loop for review findings (`## Review fixes`). | no |
| `gemini-agent/<name>/agent.json` | Antigravity-specific mirrors of the agent prompts, one subfolder per agent. Kept in sync by `sync-gemini-agents.py`; **never edit them by hand**. | — |

### 1.4 `prompts/shared-<lang>/` — shared text blocks

These are **not** skills or agents: they are blocks that a skill (or an agent prompt) references with a `<!-- INCLUDE:shared/<file> -->` marker, and that the installer **inlines at build time**. This is what makes an installed SKILL complete on its own while the rule lives in exactly one place.

| File | What it defines | Who includes it |
|---|---|---|
| `context-check.md` | The phase-opening context check (is the context fresh, has `/clear` been run). | every phase skill |
| `python-cmd.md` | The platform-dependent Python invocation (`python3` / `python` / `py -3`). | every skill that calls a script |
| `git-preflight.md` | The no-VCS gate, the working-tree check, the fresh/clean `main` requirement and resume detection. | `00`, `01` |
| `parallel-cycles.md` | Parallel cycles: the 01–05 design window in a worktree (PW1–PW5) and the gate before 06. | `01`, `06` |
| `input-from-prev.md` | The handover mechanism between phases (IP1) and the item format. | `01`, `02`, `03`, `04`, `07` |
| `plan-self-contained.md` | The most important rule of phase 03: `plan.md` is self-contained — the consumer table and the self-test. | `03a`, `03b` |
| `dereferencing.md` | The abstraction level of the input is not the abstraction level of the plan — a reference has to be resolved from the source. | `03a`, `03b`, `plan-fixer` |
| `spec-artifact-transfer.md` | KX3: an elaborated spec artifact is lifted over verbatim, without truncation. | `03a`, `03b`, `plan-fixer` |
| `plan-section-ids.md` | PID1: the stable `[P-…]` section identifiers `tasks.md` refers to, and who issues them (03a/03b). | `03a`, `03b` |
| `conventions-change.md` | GC1: when and how a cycle may modify `conventions.md`, and which gate reads which section. | `03` + its quality gate |
| `path-format.md` | RP1: a code reference is relative to the repo root, a document link to the file's own directory. | the quality gate of `02`/`03`/`04` |
| `artifact-voice.md` | AV1: skill text must not bleed into `spec.md`/`plan.md`/`tasks.md`. | `02`, `03`, `04` |
| `phase-commit.md` | PC1: the phase-closing commit procedure and the phase boundary (PE1). | `02`, `03`, `04`, `05`, `07` |
| `test-scenario-design.md` | TD0–TD7: the **generating** recipe for test scenarios — the dimension inventory, the observation quartet, countability, the negative control, a calibration sample and a self-check. | `03` + `plan-fixer` |
| `review-checklist.md` | The review criteria of the code review (including the decidable `TB1` question about an empty test body) and the `<status:must_fix>` vs `<status:suggestion>` dividing line. | the `reviewer` agent **and** the reviewer-fallback block of `07` (RV-FB1) |
| `quality-check-{spec,tasks}.md` · `quality-check-plan-{code,test}.md` | The quality gate of phase 02/03/04, run before the closing. The gate of 03 is **split** (D7): `03a` includes `-code`, `03b` includes `-test`, and the `plan-fixer` includes **both**. | the skill **and** its fixer agent (D13) |
| `fix-mode-{spec,plan,tasks}.md` | The Fix-mode (analyze-loop entry point) section of phase 02/03/04. | the skill **and** its fixer agent (D13) |
| `questions-tasks.md` | The question-register order of phase 04 (`tasks-questions.md`). | `04` + `tasks-fixer` |

### 1.5 `prompts/lang/` — the project-language content

This is the **only** place where the two language axes meet. The **prompt language** decides which `-<lang>` tree is installed; the **project language** decides which slice of this folder is baked in. Both are decided at install time and wired in (no language field remains in the project).

| Path | What it is for |
|---|---|
| `status-keys.json` | The dictionary of the project-language **section names, field names and status values**, with an `hu` and an `en` slice. The `<sec:…>` / `<field:…>` / `<status:…>` tokens of the prompts are resolved from it at build time. **A new section name goes into this JSON first, and only then becomes a token.** |
| `hu/` · `en/` | The project-language blocks: user-facing sentences and artifact templates, in `<!-- ANCHOR:<anchor> -->` sections, referenced from a prompt by `<!-- INCLUDE:lang/<file>.md#<anchor> -->`. Identical file names and identical anchors in both. |
| `<lang>/descriptions.json` | The skill/agent descriptors (the text shown by the slash-command list). |

### 1.6 `prompts/scripts/` — automation and the deterministic gates

The installer copies **every `*.py`** into the target project's platform scripts folder, except the three maintainer tools marked below. The point of these scripts is that a machine-decidable question is answered by a script and not by an LLM: it is cheaper, it produces no false alarm, and its result is an exit code rather than an opinion.

| Script | Phase | What it decides / does | Copied into the project |
|---|---|---|---|
| `install-helper.py` | — | The engine of the installer: model + effort assignment, file copying, `INCLUDE` inlining (BD14), token resolution, resolving `<platform-scripts-folder>` (BD15). | **no** |
| `sync-gemini-agents.py` | — | Keeps the `Instructions` section of `gemini-agent/*/agent.json` in sync with the `agents/*.md` prompt (`--check` for a gate run). | **no** |
| `lang-parity-check.py` | — | The parity gate of the two prompt trees: file list, INCLUDE markers, frontmatter, rule IDs, heading structure, code blocks, imperative count, language tokens. `--strict` for closing a PR. | **no** |
| `lang_keys.py` | — | The shared language-key loader **imported by every gate script**: it resolves the section names, field names and status values from the `lang-keys.json` written next to the scripts by the installer (or, when run inside this repo, from the `hu` slice of `prompts/lang/status-keys.json`). This is why the gates match on the language of the project rather than on hardcoded text. Not a standalone command. | yes |
| `analyze-gate-check.py` | 05 (+ 03/04) | The mechanical gate: plan↔task references, markers, `DoD-NN`, mandatory tables, executed artifacts, plan anchors, artifact voice, the coverage chain, `TS1–TS8`, `TA1` (test artifact data sheet), `WY1` (the purpose of a planned change), `PH1` (run phase), `TT1` (test coverage in tasks.md), `TI1`/`TI2`/`TX1` (the shared `TS-NN`/`TC-NN` test namespace, one test per `[CHECK]`), `T6` (colliding `[CHECK]` outputs), `GA1` (gate stamp), `EV1–EV5`. It also **generates** the two report tables, the `## Inventory` for the analyzer-exec, and the `--emit-slices` slices for the semantic rounds. | yes |
| `run-tests.py` | 07 | Runs the tests from the machine-readable table of `plan.md`, so the raw test log never enters the LLM context. It stops **before** the run on a wrong path base (`exit 3`) or a wrong test target (`exit 4`). | yes |
| `round-log.py` | 07 | Opens/fills/closes the `## Round N` blocks of `validation-report.md` and creates the `round-NN/` folder with a matching number. | yes |
| `failure-counter.py` | 07 | The run log of the loop and the three stopping limits (3 consecutive / 5 total per item, 5 consecutive FAIL runs) — it stops with `exit 3`. | yes |
| `dod-check.py` | 07 | Joins the DoD points with the round's JUnit results through the `· _evidence:_` fields (DI1/DI2). | yes |
| `contract-guard.py` | 07 | The VD3a contract-integrity gate: protected paths + cheating patterns in the diff. | yes |
| `sonar-gate.py` | 07 | Reads the Sonar Quality Gate from the Web API; a separate exit code for "failed on a threshold without a blocking finding" (QG1). | yes |
| `validate-gate-check.py` | 07 | The collective gate: statuses, open tasks/DoD ticks, IP1 items, open Must Fix findings, round block ↔ folder match. | yes |
| `test-substance-check.py` | 06/07 | `TB1`: no vacuous body (`assert True`, `pass`, a body without an assertion) in the test files listed in the `TA1` data sheets of the plan; `TB2`: the test selector of a `[CHECK]` command actually exists in the test file. | yes |
| `report-gate-check.py` | 06/07 | The TR3 gate: are the reports required by `conventions.md` present in the phase folder; plus the report-phase query (`--phases`, TR6) and the `test-report/` layout guard (TR5/c). | yes |
| `ds22-gate-check.py` | 08 | The DS22 Layer 1 core gate: no discontinued/renamed identifier in the docs, folder-index set equality, coverage-marker bump. | yes |
| `tc8-gate-check.py` | 08 | The TC8 gate on `specs/test-conventions.md`: path existence, dangling reference, secret check, `Last run` marker. Returns `0` with "skipped" if the file does not exist. | yes |
| `manual-test-gate-check.py` | — | The gate of `bs-manual-test-plan` (MG1–MG10): header status, mandatory sections, test group completeness, bidirectional DoD coverage, `curl` ↔ ```http symmetry, `TG-NN` identifiers. | yes |
| `worktree-setup.py` | — | PW4: copies the missing agentic tool folders into a worktree opened for a parallel cycle. It never overwrites an existing file and never copies a git-tracked one. | yes |
| `cycle-status.py` | — | The runner of the `bs-cycle-status` skill (interactive TUI or direct output). | yes |
| `export-doc.py` | — | The runner of the `bs-export-doc` skill: pandoc + `mermaid-filter` + xelatex → a versioned PDF. | yes |

### 1.7 The remaining files under `prompts/`

| Path | What it is for |
|---|---|
| `models.json` | The model + effort configuration per platform: the three tiers (`deep_reasoning_agent` / `default` / `research_agent`) as `{model, effort}`, plus the agents that differ from the default as rows named after themselves. The installer bakes the values into the agent files. |
| `meta-improve-prompts.md` | The meta template for prompt development: it describes the workflow, the design principles and the mandatory manual gates for a session whose job is to improve the prompts. |
| `inprove-list*.md` | The historical prompt-development lists (what was changed and why). Reference material, not run by anything. |

---

## 2. A target project after installation

Nothing from this repository runs in place. `install.sh` writes the prompts, the agents and the scripts into the target project in the native format of the chosen platform, and the framework then creates the rest **while you work**.

### 2.1 What the installer writes in

The installer writes **nothing into the project root** except the root files that are the tools' own conventions (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.mcp.json`).

| Platform | Skills | Subagents | Scripts |
|---|---|---|---|
| Claude Code | `.claude/skills/bs-<name>/SKILL.md` | `.claude/agents/<name>.md` (frontmatter `model` + `effort`) | `.claude/scripts/` |
| Cursor (Agent CLI) | `.cursor/skills/bs-<name>/SKILL.md` | `.cursor/agents/<name>.md` (`model: <id>[effort=…]`, `readonly`) | `.cursor/scripts/` |
| Antigravity | `.agents/skills/<name>/SKILL.md` | `.agents/agents/<name>/agent.json` (`model` = **tier**) | `.agents/scripts/` |
| Codex CLI | `.agents/skills/bs-<name>/SKILL.md` | `.codex/agents/<name>.toml` (`model`, `model_reasoning_effort`, `sandbox_mode`) | `.codex/scripts/` |
| GitHub Copilot | `.github/instructions/bs-<name>.instructions.md` | `.github/agents/<name>.agent.md` | `.github/scripts/` |

> ⚠️ **Codex and Antigravity share `.agents/skills/`**, so in practice only one of the two can be installed into a given project. The installer warns about this and asks before continuing.

Next to the scripts the installer also places **`lang-keys.json`** — the slice of `status-keys.json` for the chosen project language. This is what makes the gate scripts search for and write the section titles, field names and status values in the language of the project.

### 2.2 What the framework creates while you work

```
<target project>/
├── conventions.md
├── specs/
│   ├── roadmap.md
│   ├── test-conventions.md
│   └── cycle-NN-<cycle-name>/
├── docs-generated/
│   ├── README.md
│   ├── system-overview.md
│   ├── architecture.md
│   ├── CHANGELOG.md
│   ├── design-drift.md
│   └── <component>/README.md
├── export/
└── .bs-brainstorm/
    └── brainstorm-NN-<slug>.md
```

| Path | What it is for | Who owns it |
|---|---|---|
| `conventions.md` | The project-specific technical agreements in one place: tech stack, ports, project references, test conventions, the **test reporting table** (TR3 — this is what the report gate reads), the report phases (TR6), the merge strategy, the Sonar settings, the git/branching conventions. Several deterministic gates read from here, so if a cycle changes something the gate looks for here, **updating it is part of that cycle** (GC1). | `00`, and a cycle under GC1 |
| `specs/roadmap.md` | The cycle list with dependencies and test criteria; a cycle is closed here at the merge. | `01`, `09` |
| `specs/test-conventions.md` | What has to be tested in **every** cycle, per component, as-built — with a mandatory coordinate block (TC13) and the recipe register. **Nothing runs from it automatically** (TC1/a): a recipe only executes if 02/03 has consciously lifted it into the cycle's spec/plan. | `08` |
| `docs-generated/` | The generated, as-built documentation. It is the deliverable — it must be committed and must not go into `.gitignore`. Every file carries a header block (DS17) with `Covered` / `Last updated` / `Generator/scope`. | `08` |
| `export/` | Versioned PDF exports (`<name>-v<N>.pdf`). Binary, it grows per cycle and can be regenerated at any time → it belongs in `.gitignore`. | `bs-export-doc` |
| `.bs-brainstorm/` | The persistent working files of the ideation sessions. Raw thinking, not a deliverable → gitignored; what is worth keeping is distilled into the cycle's `cycle-design-input.md`. | `bs-brainstorm` |

**Inside `docs-generated/`** — every file carries a header block (DS17) with `Covered` / `Last updated` / `Generator/scope`, and all of them are owned by `08-doc-sync`:

| File | What it is for |
|---|---|
| `README.md` | The folder's index/manifest — one line per file. A new generated file must be added, and a stale entry removed (set equality with the actual content, DS21). |
| `system-overview.md` | The as-built description of behaviour at onboarding/stakeholder altitude: capabilities/flows, consolidated sequences, the state model. `02-write-spec` reads it back as the current-truth starting point (DS5). |
| `architecture.md` | How the system is built and how it runs — components, build, deployment, ops. Its exclusive owner is 08 (the architecture-writing task of 06 has been retired, DS4). |
| `CHANGELOG.md` | A detailed, incremental, per-cycle change log of what changed in the behaviour/documentation of the system. |
| `design-drift.md` | The deviations of the implemented system from the HLD/LLD intent (DS20). A resolved deviation is not deleted, it moves to the "Closed deviations" section. |
| `<component>/README.md` | The component READMEs. An **existing** component's README is owned by 08; only a **new** component's first README may be written by 06. |
| _(project-specific extra docs)_ | Any further generated doc. The skill does not hardcode them: the folder walk finds them and the header scope decides whether a cycle affects them. |

### 2.3 One cycle folder — `specs/cycle-NN-<cycle-name>/`

```
specs/cycle-NN-<cycle-name>/
├── cycle-design-input.md
├── spec.md
├── spec-questions.md
├── plan.md
├── plan-questions.md
├── tasks.md
├── tasks-questions.md
├── spec-input-from-prev.md
├── plan-input-from-prev.md
├── tasks-input-from-prev.md
├── validate-input-from-prev.md
├── analyze/
│   ├── analyze-report.md
│   ├── analyze-task.md
│   └── slices/
├── imp-decision.md
├── doc-sync-plan.md
├── doc-sync-questions.md
├── manual-test-plan.md
└── test-report/
    ├── validation-report.md
    ├── code-review.md
    ├── implement/
    │   └── check-log.md
    └── validate/
        ├── round-01/
        └── round-02/
```

| File / folder | Phase | What it is for |
|---|---|---|
| `cycle-design-input.md` | created by `01`, **filled in by the user**, consumed by `02`+`03` | The user's own free-form cycle specification (expectations, an outline, examples). Filling it in is optional; no phase ever rewrites it. `02` processes its behavioural part, `03` lifts its technical part into the plan. |
| `spec.md` | `02` | Business behaviour, requirements, mock strategy, test specification, and the Definition of Done with stable `DoD-NN` identifiers and `· _evidence:_` fields (DI1/DI2). |
| `plan.md` | `03` | The **self-contained** technical execution plan: affected components, planned changes, the mandatory `## Environment coordinates` (KO1), the machine-readable run table (TP4), the `TS-NN` test scenarios (TS1–TS8, with the `.http` form), the test artifact data sheets (TA1), the purpose of every planned change (WY1) and the target environment (EV1). The only source the `test-runner` reads. |
| `tasks.md` | `04` | The checkboxed task list with `[RED]`/`[GREEN]`/`[CHECK]`/`[OPS]` markers and the plan links (`[P-…]`, PID1). During the 07 loop it also carries the `## Validation fixes` / `## Review fixes` sections. |
| `spec-questions.md` · `plan-questions.md` · `tasks-questions.md` | `02` · `03` · `04` | The open questions of the given phase. A phase can only be closed with no `- [ ]` left; a closed question stays as `[x]` with the decision. |
| `*-input-from-prev.md` (4 files) | written upstream, consumed downstream | The handover between phases (IP1): information that is valuable but does not belong in the current phase. `spec-` (01→02), `plan-` (01,02→03), `tasks-` (02,03→04), `validate-` (03,04→07). Created only if there is something to hand over. |
| `analyze/analyze-report.md` | `05` | The PASS/FAIL consistency report: the six categories, the two coverage tables generated by the gate, the executability inventory and the Loop log. |
| `analyze/analyze-task.md` | `05` | The fix list approved in the triage (TR1) — the fixer subagents work exclusively from its open items. The rejected items stay in a separate section as the memory for later rounds. |
| `analyze/slices/` | `05` | The input slices cut out by the gate for the three semantic analyzer rounds. Gitignored. |
| `imp-decision.md` | `06` | The implementation decision log: non-obvious solutions and the stops after the 3-attempt rule. |
| `doc-sync-plan.md` | `08` | The `doc-sync-planner`'s per-file tickable plan plus the finished replacement texts. The anchor of the execution and of resuming after an interruption. |
| `doc-sync-questions.md` | `08` | The decision points and gate failures of the doc-sync (`Knn`). |
| `manual-test-plan.md` | *(not a phase)* | The manual test plan produced by `bs-manual-test-plan`: startup, test data, `TG-NN` manual test groups, bidirectional DoD coverage. Zero feedback into the flow. |
| `test-report/validation-report.md` | `07` | The run journal: one `## Round N` block per round (written by `round-log.py`) plus the `# Validation History` (written by `failure-counter.py`). After a `/clear` this is the only place the validation can be reconstructed from. |
| `test-report/code-review.md` | `07` | The `reviewer`'s findings: `MF-NN` Must Fix (blocking) + `S-NN` Suggestions (non-blocking). |
| `test-report/implement/check-log.md` | `06` | The append-only log of the `[CHECK]` runs: time, task, attempt, the command actually issued and the counts — including the failed attempts. |
| `test-report/implement/` | `06` | An official phase folder (TR6). Beyond `check-log.md` it holds the full report set of the closing state as well, if `conventions.md` lists `implement` among the report phases. |
| `test-report/validate/round-NN/` | `07` | One folder per validation round with every test artifact of that round (per the report table) plus `sonar-report.md`/`.html`. Its number matches the `## Round N`; earlier rounds are never overwritten. |

**Three things worth knowing about this folder:**

1. **The folder name never carries a branch prefix.** The branch may be `feature/cycle-07-oidc-login` (or something the naming strategy of `conventions.md` prescribes), but the folder is always plain `cycle-NN-<name>`.
2. **The `test-report/` top level is a closed list** (TR5/c): `validation-report.md`, `code-review.md`, `implement/`, `validate/`. Anything else there is a **path defect** (a wrong base pasted into a parameter expecting a different one), to be deleted — the cleanup prohibition covers only the `round-NN/` folders, whose evidence is never overwritten or deleted.
3. **The question files are never pruned.** A closed question stays as `[x]` with the decision next to it; the same applies to the `*-input-from-prev.md` items (`→ incorporated: …` / `→ rejected: …`).

---

## 3. What to commit and what to ignore

| Path | Commit? | Why |
|---|---|---|
| `specs/**` (spec, plan, tasks, questions, reports) | **yes** | The design documents and the evidence are the deliverable; after a `/clear` this is the only place the work can be reconstructed from. |
| `specs/cycle-*/analyze/slices/` | no | Generated input slices; the folder hides itself with a `.gitignore`. |
| `docs-generated/**` | **yes** | The living documentation is a deliverable. |
| `export/**` | no | Binary, regenerable from the version-controlled markdown. |
| `.bs-brainstorm/**` | no | Raw thinking; the distillate goes into `cycle-design-input.md`, and that is what gets committed. |
| The platform folders (`.claude/`, `.agents/`, `.codex/`, `.cursor/`, `.github/`) | project decision | Whichever way you decide, note that a worktree only receives git-**tracked** files — for the gitignored case `worktree-setup.py` (PW4) supplies them. |
