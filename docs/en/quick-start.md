# Quick start

← [Back to the main page](../../README.md) · [Page index](README.md)

BerkiSpec is a disciplined, spec-driven development (SDD) framework for pair programming with AI agents.

## The operating principle of the framework:
* **Cycles:** development is divided into well-bounded units (cycles) that can be described with an unambiguous goal and kept easily under control. Every new cycle gets its own Git branch, and all design and logging documents of the cycle go into the `specs/cycle-NN-<cycle-name>/` folder in the project root.
* **Phases:** every cycle is broken down into strict phases that lead the process from the requirements through to implementation and merge.

## Two development routes:
Depending on the complexity of the task, two flows are available:
1. **Full SDD flow:** produces a detailed specification (`spec.md`), a technical plan (`plan.md`) and a task list (`tasks.md`), and runs automatic self-healing quality loops (analyze, validate, review).
2. **Lightweight flow:** for smaller changes, configurations or simple scripts. It runs in one step, without a separate phase breakdown.

## Basic commands (slash commands):
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
