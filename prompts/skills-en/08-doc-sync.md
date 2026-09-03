---
phase: 08
name: bs-doc-sync
description: "berkispec - 08. Use it after validation, before the merge (Phase 08), when tasks.md/plan.md/spec.md are all 'Done'. It synchronizes the code changes into the 'docs-generated/' system documentation and into the affected component READMEs (doc-sync-planner subagent, against design drift), maintains the 'specs/test-conventions.md' register of recurring test expectations, and creates 'doc-sync-plan.md'."
prerequisites:
  - "specs/cycle-NN-<name>/tasks.md status: <status:done>"
  - "specs/cycle-NN-<name>/plan.md status: <status:done>"
  - "specs/cycle-NN-<name>/spec.md status: <status:done>"
output:
  - "a consistent state of docs-generated/ (system-overview.md, architecture.md, CHANGELOG.md, design-drift.md, README.md folder index + the other files of the folder)"
  - "specs/test-conventions.md — the live register of the recurring test expectations and of the recipes belonging to them (TC1)"
  - "The affected component READMEs updated"
  - "specs/cycle-NN-<name>/doc-sync-plan.md (the anchor of the execution and of the continuation)"
  - "specs/cycle-NN-<name>/doc-sync-questions.md (if a decision point / a gate failure comes up)"
prev: bs-validate
next: bs-merge
subagents:
  - "agents/doc-sync-planner.md"
---
# 08 — Documentation sync (doc-sync)
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

We develop software in spec driven development. The development is split into cycles. Every cycle is an independently developable, independently testable subunit of the complete implementation.

This is **phase 8 (0–9)** of the process: 0-init · 1-cycles · 2-spec · 3-plan · 4-tasks · 5-analyze · 6-implement · 7-validate · **8-doc-sync ←** · 9-review.

---

## What this phase is and what it does NOT do

The doc-sync keeps **every generated project document** up to date from cycle to cycle in a dedicated **`docs-generated/`** folder. The phase guarantees that **all** files of the folder are consistent with the realized (as-built) system — among them a coherent behavior description at onboarding/stakeholder altitude (`system-overview.md`), an incrementally growing `CHANGELOG.md`, a `design-drift.md` (the deviations of the realized system from the design) and the `architecture.md` (the "how it is built/runs").

- It is **not** a copy of the spec (the spec is exhaustive, per feature) and **not** the `architecture.md` (build/ops internals). The `system-overview.md` is the missing intermediate level: "what the system does today, with which flows, with which state".
- The content follows the project language (like the skills); the file names are **English** (according to the code base convention).
- The doc-sync runs **before** the review, so the document changes get into the diff and into the commit of the cycle. **But the code review (09) and the doc-sync (08) are INDEPENDENT quality gates:** the reviewer gives findings exclusively on the **code**; the correctness of the generated documents is guaranteed by the **own objective gate** of the doc-sync + its human questions. The reviewer does **not** give a `<status:must_fix>` on the generated documents.

> **GUIDING PRINCIPLE — cheap-LLM compatible.** This phase is written so that a weaker LLM can also carry it out reliably: **"the plan first, then mechanical execution"** (relying on the checkable plan of `doc-sync-plan.md`), **strong guards against "let us start from scratch"/"let us rephrase it"**, and **every decision point as a question** in `doc-sync-questions.md` (never an ad-hoc decision). The thinking condenses into the plan, the execution is mechanical.

---

## Input

The input of the prompt is the folder of the cycle (e.g. `specs/cycle-NN-<cycle-name>`). From here you read the `spec.md` / `plan.md` / `tasks.md` files of the cycle and the diff of the cycle.

Your working files:
- **On an incremental run** (there is an active cycle): `specs/cycle-NN-<cycle-name>/doc-sync-plan.md` and `specs/cycle-NN-<cycle-name>/doc-sync-questions.md`.
- **At the bootstrap** (there is no active cycle): the root `temp/doc-sync-plan.md` and `temp/doc-sync-questions.md` (see the Bootstrap branch section).

---

## <field:f_prerequisite>

0. **Identifying the cycle:** if the user gave a cycle/file, use that; otherwise offer the most recent `specs/cycle-*` folder for confirmation — <!-- INCLUDE:lang/common.md#ciklus-beazonositas --> — and wait for the answer before moving on.

1. **`conventions.md` existence check:** read `conventions.md` in the root of the project (especially the `## <sec:cv_references>` section — this is the register of source grounding, DS19). If it does not exist, STOP — they should return to phase `00`.

2. **Working-tree check (only with VCS):** run `git status --short`. If there are uncommitted changes, list them, and ask in one round whether I should commit now or continue — wait for the answer. (The doc-sync looks at the diff of the cycle against the main branch; without a clean working tree the diff is misleading. In a No-VCS project it is skipped.)

3. **Status gate (checking the PASS of 07-validate):** in case of a PASS, the validate phase (07) sets the status of all three files to `<status:done>`. Check:
   - the status of `tasks.md`: `<status:done>`
   - the status of `plan.md`: `<status:done>`
   - the status of `spec.md`: `<status:done>`

   If any of them is not `<status:done>` (e.g. it is still `<status:ready_for_validate>` or a reset `<status:draft>`), the validation has not run successfully yet — return to phase `07`.

---

## Skill-level file mandate (DS13 — genericity)

The skill names **only two files as mandatory**, which the doc-sync produces and maintains even if the user does not create them explicitly:
- `docs-generated/architecture.md` — the "how it is built/runs" (build/ops internals);
- `docs-generated/system-overview.md` — an operational overview (onboarding/stakeholder).

**Every other file** in `docs-generated/` is tended automatically by the **folder walk** (DS11) — the skill does **not** hardcode a concrete project file (e.g. a keycloak configuration). If there are extra generated documents in a project, the folder walk finds them and `doc-sync-plan.md` picks them up; the skill does not assume their existence.

> The `docs-generated/` folder is **created by the doc-sync if it does not exist yet** (the bootstrap branch) — this way there is no ordering problem about who creates it.

**One further file outside `docs-generated/` is owned by the doc-sync:** **`specs/test-conventions.md`** (next to `specs/roadmap.md`, **not** in `docs-generated/`). This is **outside the scope** of the folder walk (DS11) and of the DS22 folder-index set equality — it has its own rules, see "Maintaining `specs/test-conventions.md` (TC1–TC11)".

> **The boundary towards `conventions.md` (TC1/c) — what the doc-sync does NOT write.** The `conventions.md` in the root of the project is the property of `00-init-project`, and **deterministic gates read it**: the `## <sec:cv_test_reporting>` (report artifacts, `**<field:f_artifact_path_base>:**`, report-generating commands) belongs to the TR3 gate, the `## Sonar` to the Quality Gate. The doc-sync does **not touch** these. What goes into `test-conventions.md` are the **recipes and coordinates** (how the stack starts, which call, which test user) — the **report paths do not**. If a cycle restructures the reporting, that has to be carried over in `conventions.md`, with the cycle's own task (GC1, see `03a-write-code-plan`) — updating `test-conventions.md` is not a substitute for it, and the doc-sync does not make up for it either.

---

## Source grounding — the source hierarchy (DS19)

The doc-sync follows an unambiguous priority order; **in case of a conflict the one standing higher wins**:

1. **Authoritative (what IS — as-built):** `src/` (the actual code: routes / handlers / modules — **this is the primary truth**), the closed cycle `spec.md` files (the later one wins), config; **optionally** an API descriptor (openapi/swagger), **if** the `## <sec:cv_references>` section of `conventions.md` gives it.
2. **Consolidated summary:** `specs/roadmap.md`, `docs-generated/architecture.md`.
3. **Intent / context (what we PLANNED):** the HLD (`README.md`), the LLD, external documents, the POC description — terminology, structure, justification, a drift reference. It does **NOT** override the reality of the code; the deviation goes into `design-drift.md` (DS20).

The **project-specific** paths of level 3 are read by the doc-sync from the **`## <sec:cv_references>` of `conventions.md`** — it does **not hardcode** a file. If the section is empty or missing, you skip level 3 (the drift comparison is then restricted to the deviations named explicitly by the cycle spec).

---

## The files of the doc-sync folder (a reference)

| File | What it is | Header scope (DS17 — "what it covers") |
|---|---|---|
| `docs-generated/README.md` | The **index/manifest** of the folder (a one-line description per file, DS21) | the actual file list of the `docs-generated/` folder |
| `docs-generated/system-overview.md` | An as-built operational overview (capabilities/flows, sequences, state model, [conditional] endpoint inventory) | every user/business flow and state of the system |
| `docs-generated/architecture.md` | "How it is built/runs" — components, build, deployment, ops, **technical contracts** (config fields, log/event schema, error-code table — verbatim, DS23) **and environment coordinates** (URL/port/test user, DS25) | the structure and the operation of the system |
| `docs-generated/CHANGELOG.md` | A detailed, incremental change log per cycle (DS15) | the behavior/document change of every closed cycle |
| `docs-generated/design-drift.md` | The deviations of the realized system from the HLD/LLD intent (DS20) | the design ↔ as-built deviations + "<sec:closed_deviations>" |
| _(project-specific extra documents)_ | found by the folder walk; the header scope decides whether it is affected | declared by the own header of the file |

---

## Handling an interrupted run + idempotence (DS10 — MANDATORY)

The doc-sync may be interrupted at any time. At a restart, do **NOT** start with a clean slate — the phase **recognizes what is done**, and continues from there. The anchors of the continuation:

1. **The ticked/open items of `doc-sync-plan.md`** — this is the deterministic state of the execution.
2. **The open `[ ]` questions of `doc-sync-questions.md`** — if there are any, the phase is waiting for them.
3. **The "<field:f_covered> up to cycle-NN" markers of the generated documents** (the header block) — these show how fresh each file is.

**The order of continuation (mandatory):**
1. **First** the open `[ ]` questions of `doc-sync-questions.md` (if there is an open question → the phase is waiting for it, do not move on).
2. **After that** the `[ ]` (unfinished) items of `doc-sync-plan.md`, in order.

**The ticking rule (cheap-LLM-safe):** always put the tick of a plan item in **AFTER the file is actually saved** (never before). Every plan item should be **re-run safe** (of a reconciliation nature, converging to the same place) — this way an interruption at worst re-runs an already finished item harmlessly, it does not leave out a change that was not written.

**If there is no `doc-sync-plan.md` yet:** the phase starts with producing the plan (see below). **If there is one:** the phase continues according to the order of continuation above — it does not produce a new plan from scratch, only if the existing plan is incomplete.

---

## What you have to do — the course of the phase

The doc-sync follows the **"the plan first, then mechanical execution"** pattern. The steps:

1. **Branching:** bootstrap or incremental? (see below)
2. **Producing the plan:** the `doc-sync-planner` subagent writes `doc-sync-plan.md` (a checkable plan per file) — together with the items of `specs/test-conventions.md`.
3. **Mechanical execution:** the main agent carries out the `[ ]` items of the plan, saving and ticking per file.
4. **The objective consistency gate (DS22):** running the core gate; in case of a failure a human-driven fixing loop (the question into `doc-sync-questions.md`). This is followed by the own gate of `test-conventions.md` (TC8, `tc8-gate-check.py`).
5. **Commit + moving on to 09.**

---

## 1. Branching: bootstrap vs incremental

**Look at whether `docs-generated/system-overview.md` exists:**

- **It does NOT exist → the BOOTSTRAP branch.** Nobody has put the `docs-generated/` folder together yet. This is a one-off large piece of work, with **a separate work plan and a user confirmation** belonging to it — see the "Bootstrap branch" section. **Do not start it without a confirmation.**
- **It exists → the INCREMENTAL branch.** The normal cycle run: you only rewrite the **affected** flows/sections, and a light check runs on the rest. See the "Incremental branch" section.

---

## 2. Producing the plan with the `doc-sync-planner` subagent → `doc-sync-plan.md` (DS14)

The heavy work (collecting the sources, the per-file diagnosis, the drift findings) is done by a **read-only diagnostician subagent**, following the pattern of the `analyzer`. The **main agent asks** (from `doc-sync-questions.md`) and **carries out** the plan — the subagent does **not** ask directly and does **not** write the documents.

**The steps of producing the plan:**
1. The `doc-sync-planner` subagent is given by the **installed agent definition** of the platform — call it by this name, do not look for it as a file in the project.
2. Start it, handing over: the folder of the cycle (`spec.md`/`plan.md`/`tasks.md`), the `git diff` of the cycle against `master`, `conventions.md` (with the `## <sec:cv_references>`), and the current content of the `docs-generated/` folder.
3. The subagent returns the **checkable plan per file** (for every file of the folder + for the new files needed: "what has to be done" or "no action" + the drift findings) **and, for every `<status:op_reconciliation>`/`<status:op_new>` item, the finished `<field:f_replacement_text>`** (the current snippet to be replaced + the new text written). **The main agent writes the plan AND the replacement texts into `doc-sync-plan.md`** (incrementally: `specs/cycle-NN-<cycle-name>/doc-sync-plan.md`; at the bootstrap: `temp/doc-sync-plan.md`) — this way the replacement text is persistent, and the resume of an interrupted run continues from the file (DS10). Since the subagent **has already read** the whole content of `docs-generated/` and written the replacement text, the main agent does **not have to read and recompose** the files — it only applies.

> **If the subagent does not run, or does not give a plan:** do not start writing documents "from your head". The **type of the error** decides what to do: at **a platform limit** (the text mentions a quota/allowance/limit — e.g. "usage limit", "quota exceeded", or an allowance reset date) **do not retry**, because the second call runs deterministically into the same thing; at **every other error** (a timeout, a one-off crash) one retry is justified. After that **STOP**, tell the user — at a platform limit copying the error message **verbatim**, together with the reset date —, and ask whether I should retry the subagent, or put the plan together directly in the main agent according to the aspects of the `doc-sync-planner`.
>
> **If you go down the fallback branch, marking the origin of the plan is MANDATORY.** The main agent works on a different model and in a narrower context than the subagent, therefore it is systematically a weaker plan — one line should go into the header of `doc-sync-plan.md`: **Produced by:** the main agent (fallback) — `doc-sync-planner` could not be run: <reason>. This way a later reader knows what the plan is worth.

For the format of `doc-sync-plan.md` see the **Templates** section. **Ticking the plan is the state of the execution** — an interrupted run continues from here (DS10).

---

## 3. The incremental branch (DS9, DS11, DS14)

It runs if `system-overview.md` **exists**. **Bounded scope:** you only rewrite the **affected** flows/sections; the holistic comb-through is a **bounded** check, **not** a full re-audit.

### 3.1 The mechanical rule of being affected (DS24e)

A `docs-generated/` file is **affected** if the diff of the cycle moves a component/flow/endpoint that the **header scope** of the file (DS17) declares as covered; otherwise it is **unaffected**. The `doc-sync-planner` **applies this rule, it does not decide by feel**:
- **an affected file →** <status:op_reconciliation> (rewriting only the affected sections, with the outdated part replaced);
- **an unaffected file →** a light check: based on the header scope, confirm that the cycle really does not affect it → the "<status:op_no_action>" item of `doc-sync-plan.md` records it (the coverage marker may stay at the old cycle-NN).

### 3.2 The execution (mechanical: applying the replacement texts of the subagent)

You carry out the `[ ]` items of `doc-sync-plan.md`, file by file — but you **do not compose and do not read again**: for every `<status:op_reconciliation>`/`<status:op_new>` item the `doc-sync-planner` **gave a finished `<field:f_replacement_text>`** (the current snippet to be replaced + the new text). Your job is to **apply it mechanically**:
1. Open the target file, and replace the "to be replaced" snippet of the `<field:f_replacement_text>` with the "new text" (for a `<status:op_new>` file: create the file with the given content).
2. **After** saving, tick the plan item (the DS10 ticking rule).
3. **Fallback:** if the given "to be replaced" snippet does not match unambiguously (e.g. because of a change in the meantime), then — and only then — read the affected section of the file, and carry out the replacement by hand based on the "new text" of the subagent. This is the exception, not the main rule.

The typical items (all of them arrive with the replacement text of the subagent):
- **`system-overview.md`** — updating the affected flows/sequences/state; the mermaid blocks of the cycle into the appropriate capability section, with the **outdated one replaced** (DS7); bumping the `<field:f_covered>`/`<field:f_last_updated>` of the header.
- **`architecture.md` reconciliation** (brought over from today's 09, DS3): the subagent gave a surgical replacement text for the parts **changed** in the cycle (see "The reconciliation of `architecture.md`" for the scope rules).
- **The component READMEs** — checking/updating the `README.md` of the components **affected** in this cycle (see "The component READMEs").
- **`CHANGELOG.md`** — a new, detailed, incremental cycle entry (DS15, see the template). `system-overview.md` only keeps a coverage marker + a link to it, it does not duplicate.
- **`design-drift.md`** — adding the **<status:op_new>** deviations introduced by the given cycle; moving a deviation that ceased into the "<sec:closed_deviations>" section (**not deleting it**) — see "The drift comparison".
- **`docs-generated/README.md`** — maintaining the folder index: a new generated file → it gets in; an outdated entry → out.
- **`specs/test-conventions.md`** — promotion / a `<field:f_last_run>` bump / deleting an outdated item (TC1–TC11). This file is **outside** `docs-generated/`; if it does not exist yet, the TC6 bootstrap path runs for it — even if `system-overview.md` already exists.

### 3.3 Diagram replacement + a check that everything came over (DS7)

You fit the mermaid blocks of the cycle into the appropriate capability section, with the **outdated one replaced**. A binary/`.drawio` diagram → **a link + an exported PNG**. **A mandatory check:** did every diagram from the source come over — not one may be left out (this is one of the checks of the DS22 core gate).

### 3.4 The anti-"let us start from scratch" guard (the cheap-LLM guiding principle)

It is **FORBIDDEN** to rephrase the untouched parts of `docs-generated/`, to rewrite the whole file, or to "make the unchanged content nicer". The principle of the fix modes (05/07/09) holds here too: the doc-sync is a **<status:op_reconciliation>**, not a re-composition. You only rewrite the **affected** sections, according to the items of `doc-sync-plan.md`.

---

## 4. The bootstrap branch (DS6, DS8, DS13, DS18) — the mechanics

It runs if `system-overview.md` does **not** exist. This is a **one-off large piece of work** → an **explicit user confirmation is needed** before the start. The working files (`doc-sync-plan.md`, `doc-sync-questions.md`) go into the root `temp/` folder (there is no active cycle).

The mechanics of the bootstrap:

- **2.1 — Source priority (DS6):** the backbone is `specs/roadmap.md` (the "Behavior" + "Test criterion" per cycle, already consolidated) **+** `architecture.md` §0; you read the cycle `spec.md` files **mainly for the mermaid diagrams and the details**. **Source vs. moving:** the source files (the roadmap, the HLD README, the POC description, the openapi, the SKILL) are the **sources** of the bootstrap (to be read), they do **not** move into `docs-generated/`.
- **2.2 — "The later cycle wins":** only the **current state** gets in; in case of a conflict, according to the cycle order of the roadmap, the **later cycle overrides** (e.g. `init-hash`, not `init-cache`). **A behavior that ceased must not get in.**
- **2.3 — Bounded delegation:** you delegate the source collection **per capability** to the `doc-sync-planner` subagent; the main phase **composes**; the main agent **asks** (DS12).
- **2.4 — The `architecture.md` §0 migration (DS8):** the §0 (the system picture, the component responsibilities, the data flow, the demo path) moves over into `system-overview.md`; `architecture.md` stays purely the "how it is built/runs", with a cross-link. **Moving** `architecture.md` (and the project-specific extra documents) into `docs-generated/` is a project-level step of work plan 8.
- **2.5 — Header declaration (DS17):** every bootstrapped file gets the header block.
- **2.6 — Objective verification (DS22):** the Layer 1 core gate + the Layer 2 conditional API-descriptor cross-check (see "The objective consistency gate").
- **2.7 — User confirmation + slicing (DS18):** reviewed per file/per capability, through `doc-sync-questions.md`.

> **A bootstrap warning:** the `docs-generated/` folder and its content **have to be committed** (this is the deliverable), it must **not** go into `.gitignore`.

---

## The reconciliation of `architecture.md` (brought over from 09, DS3)

`docs-generated/architecture.md` is the living, cumulative "how it is built/runs" documentation of the system. **The doc-sync is its exclusive owner** (the earlier 06 `TLAST` architecture-writing task is RETIRED — DS4). The replacement text is composed by the `doc-sync-planner` with an overview of the whole cycle (spec/plan/diff + code); the rules below are the **criteria the planner prepares the surgical patch for**, and the main agent applies it.

### What should get into it
- **The introduction** — we overwrite it at every update: the current goal of the system, its components, the changes of the last cycle.
- **The description of the components** — task, configuration, dependencies, deployment mechanism.
- **Architecture diagrams** — Mermaid diagrams reflecting the current state. **An outdated diagram must not remain.**
- **Data flows and call sequences** — a diagram of every significant flow.
- **References** — to every formal descriptor (OpenAPI YAML, Redis key map, external config).
- **Key decisions and their justification.**

### Update rules
- Overwrite only what **changed in this cycle** — the rest stays untouched (bounded scope, DS9).
- A new component → a new chapter. A modified component → the affected chapter is updated. A deleted feature → the references are to be removed.

### Consistency check (after every modified section)
- Is there another chapter/diagram that contradicts the one just updated?
- Does every diagram show the current state (component names, ports, connections)?
- Is every reference valid (the file exists, the content matches)?
- Is the introduction consistent with the other chapters?

If you find a contradiction, fix it immediately.

### The component READMEs

> **The ownership boundary (DS4) — the existence of the component decides, not the file type.** The README of an **existing** component is the **property of the doc-sync**: 03 does not plan it, 04 does not generate a task for it, the implementation does not write it — **you update it**. The first `README.md` of a **<status:op_new>** component, however, is part of building the component, therefore that is **created by 03/04/06** (it appears in the `<sec:planned_changes>` of the plan); there you only have to check it.

Check the `README.md` of the components **affected** in this cycle:
- **A new component** (it came into existence in this cycle): the `README.md` was already created by the implementation — check that it exists and is consistent. If it is exceptionally missing, add it.
- **An existing component:** if the cycle changed its behavior/port/startup/connections — **you update it** (this is not an omission of the implementation, but your task).
- Is the README consistent with the corresponding chapter of `architecture.md`?

---

## The drift comparison + `design-drift.md` (DS20)

Beyond the pure as-built description, the doc-sync **compares the realized system with the HLD/LLD intent** (level 3 of the source hierarchy, from the references of `conventions.md`), and collects the **documented deviations** into `docs-generated/design-drift.md`. **`system-overview.md` stays pure as-built** — the drift does not get mixed into it.

**A cheap-LLM-safe limit (DS24d):** per cycle, **only** the drift gets in that:
- the cycle **spec names explicitly** as a deviation, **or**
- a concrete **comparison checklist** surfaces (the level 3 references of `conventions.md` vs. as-built).

**An uncertain case → `doc-sync-questions.md`** (Qnn), never a silent guess. A cheap LLM should **not** "look for" a deviation open-endedly.

- A resolved (ceased) deviation is **not deleted**, but goes into the "<sec:closed_deviations>" section (traceability — the "we never delete" principle).
- The drift items also get into the ticked list of `doc-sync-plan.md`.
- Examples: "the HLD states RFC 8693 token exchange, the implementation uses a legacy Keycloak `subject_issuer`"; "the HLD says `/init-cache`, the system uses `/init-hash` (cycle-16)".

---

## Maintaining the `docs-generated/README.md` folder index (DS21)

The **index/manifest** of the folder — it briefly describes what each file is (a one-line description per file). At every run the doc-sync ensures:
- **A new generated file in the folder → it necessarily gets in** to the index.
- **An outdated entry → out** (the actual content of the folder == the entries of the README, set equality).

At the **creation** of the folder (the bootstrap) the index is created as well. This `docs-generated/README.md` is **separate** from `prompts/README.md` and from the root `README.md`.

---

## Maintaining `specs/test-conventions.md` (TC1–TC11)

### TC1 — What it is, and what it is NOT

`specs/test-conventions.md` is the living register of the **recurring test expectations of the project and of the recipes belonging to them**: the knowledge that after a few cycles becomes "the basics" — what has to be tested in every round, in what order, with which command, in which environment. The doc-sync is its **exclusive owner**, and it lives next to `specs/roadmap.md` (**not** in `docs-generated/`, because it is a **normative** input for the future cycles, not a descriptive as-built document).

> **🔴 TC1/a — This is NOT a runnable source.** **Nothing runs automatically** from the register. The `test-runner` subagent does **not read** this file — only the <sec:testing_strategy> / <sec:regression_impact> sections of `plan.md`. A recipe is executed if and only if phase `02`/`03` deliberately **inlined** it into the `spec.md`/`plan.md` of the given cycle (with human approval). The register is **memory**, `plan.md` is the **only runtime truth**.

**What does not belong here:** `conventions.md` records **how** we test (tools, folder structure, run commands, principles) — we do **not repeat** that here. `plan.md` records what is **<status:op_new>** in the given cycle. This file records **what and when it is mandatory** to test, per component, as-built.

### TC2 — Structure: a coordinate block + exactly three sections

The file starts with a **`## <sec:coordinates>`** block (TC13 — mandatory), followed by **three numbered** sections, no more, no less. The items of sections 2 and 3 reference section 1 (they do not duplicate the coordinates), and the recipes of section 1 reference the data of block 0.

0. **Coordinates** — environments, URLs/ports, health endpoints, test users, clients, scopes, parameters, env file pointers. **In one place, searchably.**
1. **The recipe register** — per component/per step: the repo path, the image name, the registry target, the namespace/pod, the **startup**, example REST/`curl` calls, build/deploy commands. It takes the concrete URLs, users and parameters **from block 0** (the truth is there, the reference is here).
2. **The local (mock-based) tests required in every round** — referencing the recipes of section 1.
3. **The integration / E2E tests required in every round** — referencing the recipes of section 1.

For the template see the **Templates** section.

> **⚠ "Do not write prose" — what it means and what it does NOT (TC2/a).** The prohibition applies to **narrative explanation**: introductions, justifications, "in this cycle we decided this way because…", lessons, summaries. These do not belong here — the consumer is phase `02`/`03`, not a human reading it through.
>
> **It does NOT apply to detailing the test cases.** The **table of section 2/3 is an index**, not the test case itself: a one-line cell is never enough for somebody to reproduce the test. Therefore **a structured detail block is mandatory for every promoted item** below the table (`### L01 — …` / `### I01 — …`), with **<field:f_goal> / <field:f_prerequisite> / <field:f_steps> / <field:f_expected_result>** fields (TC10/b). This is not prose but **structure** — the minimum of reproducibility.
>
> The wrong interpretation (this is the error that occurred in the field): taking the rule to mean that *"only a table may be in the file"*, and shrinking the descriptions of the tests into one-line cells. From a register produced this way, the next cycle cannot run the test.

### TC3 — Promotion: what gets in (evidence-based)

**Do not judge "by feel" whether a test is "fundamental".** An item is promoted into section 2/3 if **one** of the following holds:

1. **An empirical signal (primary):** the test/recipe came into existence in an **earlier** cycle, and in **this** cycle it also appeared in the `<sec:regression_impact>` table of `plan.md` or was actually run — that is, it proved its cycle-independent relevance in practice.
1.b **The `<sec:environment_coords>` section of the cycle `plan.md` (KO1) — the primary promotion source of block 0.** Phase 03 collects here the concrete values actually used in the cycle: component base URLs, ports, health endpoints, start/stop commands, example REST calls (with the token acquisition), test and API users with passwords, parameters, network prerequisites. **Go through it item by item**, and promote whatever is cycle-independent: the concrete values into **block 0**, the step sequences/commands into **section 1**. For a credential the TC5 secret rule holds (a dev-scoped value yes, a cluster/registry/VPN/IAM/production credential only as a pointer). If a value from block 0 changed to **something else** in the KO1 section of the plan, the **plan wins** — update the register.

1.a **A carry-over signal (a strong empirical signal, TP3/a):** the `plan.md` of the cycle lifted a recipe/prerequisite **from the `plan.md` of an earlier cycle** (in the plan a `_(source: cycle-NN plan.md)_` provenance marks it, typically a token acquisition, a stack startup, a custom component build/deploy, a seed). This is **evidence of cycle-independent relevance**: if phase 03 had to reach back to an old plan, then the item is missing from the register. **List these first in the promotion offer (TC12)** — into block 0 of the file with their coordinates, into section 1 together with their recipe.

2. **A human decision (always mandatory):** the user confirmed in `doc-sync-questions.md` that the item should be a lasting expectation. **You have to offer this item by item in every cycle** — see **TC12 (the promotion offer)**: the empirical signal gives your *suggestion*, the decision is made by the user.

**Promotion means THREE things, not one (TC3/a).** An item is promoted if all three are present — the table row on its own is **not** a promotion:

1. **A table row** in section 2/3 (ID, a self-contained one-line behavior, a recipe reference, `<field:f_last_run>`) — this is the **index**;
2. **A detail block** below the table (`### <ID> — <title>`, <field:f_goal> / <field:f_prerequisite> / <field:f_steps> / <field:f_expected_result>) — this is the **test case** (TC10/b);
3. **A recipe** in section 1 (`<field:f_startup>`, `<field:f_example_call>`, commands — TC11) that the item references, plus the coordinates belonging to it in block 0 (TC13).

**A recipe (section 1) only gets in if it actually ran and was green in this cycle** (the `test-report/` is the evidence). **Writing in an invented, unverified command is FORBIDDEN** — if a coordinate is missing or uncertain, that is a `doc-sync-questions.md` question, not a silent guess.

Whatever fulfills neither condition **does not get in** — a test for a single cycle stays in the `plan.md` of the cycle.

### TC4 — The file is a live snapshot, not a log (maintenance + deletion)

- Next to every item the **`<field:f_last_run>: cycle-NN`** marker is mandatory. It shows when the item last ran green.
- The file **always reflects the current state**. If a component ceased, was transformed, or the item is no longer interpretable because of the development, the item is **deleted** — it is not archived, it does not get an "outdated" note. **The file must not grow monotonically.**
- **The information is not lost:** the fact and the reason of the deletion go into the cycle entry of `CHANGELOG.md` (DS15). This is why the "we never delete" principle does **not** apply here, which does apply to `design-drift.md` and to the question lists.
- **The deletion is visible:** every item to be deleted appears as a **separate plan item** in `doc-sync-plan.md`, so the user sees and ticks it before it happens. You must not delete silently.
- **A staleness signal:** if the `<field:f_last_run>` marker of an item is **3 or more cycles** older than the current one, add it as a `doc-sync-questions.md` question: *"`<item>` last ran in cycle-NN. Is it still a valid expectation, or is it to be deleted?"* An environment coordinate (URL, pod, namespace) **cannot be verified automatically** — this is why the staleness marker is the only safety net against it.

### TC5 — Secret classification (MANDATORY, scope-based)

This file is **version controlled and merged** — whatever gets in stays in the git history. The decision is **not** a subjective risk estimate, but a single mechanical question: **"does it authenticate a person, or does it give access to a shared platform?"**

| **May get in** (its scope is the disposable dev instance, it does not belong to a person) | **May NOT get in — only a pointer** (it authenticates a person or gives access to a shared platform) |
|---|---|
| seeded dev test users + their passwords, a dev IdP (e.g. Keycloak) realm admin, a local DB user, a mock-service API key, a dev client secret | a cluster/OpenShift login, a registry (e.g. Nexus) push credential, a VPN, a cloud IAM, a git/CI token, **anything that works in another environment (test/prod) as well** |

- The items of the left column are typically **already in the repo today** (seed/realm import files, the Clean Slate rule) — collecting them is not a new exposure.
- **The form of a pointer:** *"the credential can be obtained from `<place>`"* — never the value.
- **An uncertain case → a question** into `doc-sync-questions.md`, and until there is an answer, **you write a pointer, not a value**. The default is leaving it out.

### TC6 — Bootstrap: if the file does not exist (even in the 30th cycle)

The berkispec may get into an **already running project**, where this file never existed. **Do not start with an empty page, and do not interrogate the human from scratch** — first put together a **suggestion** from what already exists (this is done by the `doc-sync-planner`):

- the `<sec:test_specification>`, `<sec:testing_strategy>`, `<sec:e2e_infrastructure>` and `<sec:regression_impact>` sections of the `spec.md` / `plan.md` files of the closed cycles — the recurring items are here;
- the `plan-questions.md` files of the closed cycles — **the environment coordinates are here**, the ones that leaked away per cycle so far;
- the existing `test/` folder and the E2E compose file, and the `## <sec:cv_references>` section of `conventions.md`.

After that you continue the dialogue about the **suggestion** through `doc-sync-questions.md`: *"I found these as recurring expectations; which of them is still valid, what was left out, and what is the correct URL / pod / parameter today?"* — correcting is much easier than dictating.

> The bootstrap of `test-conventions.md` is **independent** of the bootstrap branch of `docs-generated/`: it has to run even if `system-overview.md` already exists (the incremental branch). The **absence of the file is not an error** in early cycles — if there is nothing to promote (there is no item according to TC3), the file **should not be created**; in that case the "<status:op_no_action>" item of `doc-sync-plan.md` records the reason. Do **not** create an empty skeleton — the next phase tends to fill an empty file with guesses.

### TC7 — The scope of the questions: bootstrap vs steady state

**You have to ask in every cycle** what should get in — but the extent of the question differs:

- **The first run (bootstrap):** a wide interview based on the suggestion according to TC6. It is one-off, it is worth it.
- **Every further cycle (steady state):** do **not** reopen the whole conversation. A **short, targeted confirmation** about the suggestion of the doc-sync: *"I would promote this, delete this, bump these — is that all right?"* The user ticks or corrects. The suggestion itself stands in the items of `doc-sync-plan.md`, the question in `doc-sync-questions.md`.

**In both cases the TC12 promotion offer is mandatory** — offering the tests of the cycle item by item for a decision. At the bootstrap this is part of the wide interview; in the steady state this is the concrete form of the "short, targeted confirmation".

### TC13 — The coordinate block at the beginning of the file (MANDATORY)

**The first block of the file is the `## <sec:coordinates>`** — this is where every environment, access and parameter datum gathers, **in one place, searchably**. Whoever wants to test should not have to page through recipes to find out which port the mock runs on, or what the password of the test user is.

**Mandatory content — three tables:**

| Table | What it collects |
|---|---|
| **Environments and endpoints** | the environment (local / remote / …), the component, the URL + port, the health endpoint — **a local-looking address behind a `port-forward`/SSH tunnel is a separate row with the `remote` environment** (the `RL1` gate reads the exempted addresses out of this) |
| **Test users, clients, secrets** | the environment, the name/identifier (user, `client-id`, service account), the secret **or a pointer**, the scope/role |
| **Parameters and env files** | parameter and environment variable names, the value or a pointer, where we use it |

**Rules:**

1. **This is the source of truth.** If a URL, a user or a parameter appears here, the recipes (section 1) **reference it**, they do not copy it. If two places hold different values, that is an error — block 0 wins, correct the recipe.
2. **The TC5 secret rule holds here too.** A dev-scoped test password may be written in; **a shared platform credential (cluster, registry, VPN, IAM, a production token) NEVER** — instead a pointer: `pointer: .env.dev → TMP_S2S_SECRET` or `pointer: password manager / Vault`. The secret check of TC8 looks at this block as well.
3. **Only a verified value (TC3).** Whatever did not run in this cycle and was not confirmed by the user either does not get in. An uncertain coordinate → a `doc-sync-questions.md` question.
4. **A separate row per environment.** Blurring of the "localhost:8080 or the remote host" kind is useless — the `Environment` column is mandatory.
5. **Becoming outdated.** If a coordinate provably changed in the cycle (another port, another host, another user), **it has to be updated here** — and the recipes referencing it stay correct automatically. This is the main benefit of this block.

The TC8 gate checks that the block **exists, stands at the beginning of the file, and contains a filled-in data row** — an empty or placeholder table fails.

### TC12 — The promotion offer: you offer the tests of the cycle item by item (MANDATORY)

**Promotion is never a silent decision.** In every doc-sync run you **have to list the tests of the cycle**, and **ask the user which of them you should lift to project level** into `test-conventions.md`. Neither lifting nor leaving out may happen without a question — the TC3 evidence rule says **what you suggest**, but the decision belongs to the user.

**1. Putting the candidate list together.** Collect the tests of the cycle from three sources:
- `plan.md` → `<sec:testing_strategy>` and `<sec:regression_impact>`;
- `tasks.md` → the `[RED]` / `[CHECK]` / `TREG` tasks;
- `test-report/` → **what actually ran**: the step table per round of `validation-report.md`, the test-tool reports of the `validate/round-NN/` folders, and for the checks during the implementation `implement/check-log.md` — these are the evidence.

**Only what actually ran and was green in this cycle may get on the list** (TC3). Do not offer what did not run — state on a separate line why it was left out.

**2. For every candidate, prepare the information needed for the decision** — the user should not have to look anything up:
- a **self-contained, behavior-level description** (phrased according to TC10 — this will be the text of the item if it gets in);
- **which section it would go into**: 2 (local/mock) or 3 (integration/E2E);
- **which recipe it needs**: an existing `R-ID`, or a **new recipe** (and then what is missing from it — the startup, an example call);
- **a suggestion + a one-line justification**: `to promote` (why it is cycle-independent) or `stays cycle-local` (why it is one-off).

**3. The question — in ONE round, into `doc-sync-questions.md`.** Do not put a separate question per test: one `Qnn` item, with the complete table in it, and a simple answer format:

```md
<!-- INCLUDE:lang/08-doc-sync.md#TC12-promocio-kerdes -->
```

**4. Wait for the answer.** This is a **blocking question**: promotion does not happen without an answer, and the phase cannot be closed with an open `[ ]` question either. If the user says no to an item, **do not argue** — record it.

**5. Carrying the answer over:**
- **Yes** → the item gets into section 2/3 (with a self-contained text according to TC10), and if a new recipe is needed, you add that too (TC11: the startup + an example call + the cleanup, with verified commands only).
- **No** → the item goes into the **decision log** at the end of the file, so that the next cycle does not ask about it again:

```md
<!-- INCLUDE:lang/08-doc-sync.md#TC12-dontes-naplo-sablon -->
```

This appendix is **not** a numbered section (the TC2 structure stays untouched): a plain list after the `## 3.` section. **If an item appears here, do not offer it again in the next cycle** — unless its behavior changed substantially; then it may come as a new candidate, with the new description.

**A steady state shortcut (TC7):** steps 2–5 run in every cycle, but if the cycle has 1–2 tests, the table is 1–2 rows as well — the question is still mandatory, only short.

### TC10 — Self-contained items: the register does not reference the cycle documents

**`test-conventions.md` has to make sense on its own.** Its reader (phase `02`/`03` in a fresh context, or a new colleague) **will not open** the old `spec.md` files — those closed together with the cycle, and their numbering restarts per cycle.

**🔴 It is FORBIDDEN in the "What it verifies" field** (and in the recipe names):
- **lifting over a spec section ordinal:** *"1.2. FlowX Backend Mock negative and positive tests"*, *"2.3. Full Dev integration test"* — the `1.2.` is the internal numbering of another document, it means nothing here;
- **referencing a cycle as an identifier:** *"Cycle 19 init-hash E2E integration tests"*, *"Level 2 E2E local Keycloak tests"* — which behavior is it about? The cycle number belongs into the `<field:f_last_run>` / `Evidence` column, not into the description;
- **a file name as a description:** *"external-apigee-client unit test"* — what does that test verify?
- **a reference to an earlier spec/plan document** ("according to point 3 of spec.md").

**Instead: a behavior-level, self-contained phrasing** — for which input what the correct output is. For example:

| Bad (referencing) | Good (self-contained) |
|---|---|
| `1.2. FlowX Backend Mock negative and positive tests` | `The mock /start-process returns 201 for a valid processName, and 400 for a missing body` |
| `Cycle 19 init-hash E2E integration tests` | `The TMP init-hash endpoint returns the same hash for the same payload, and 409 for a repeated init` |
| `Mobile Bank external apigee client unit test` | `The Apigee client retries 3× on a 503, and throws the error upwards at the 4th failure` |
| `2.1. Dev Keycloak SPI operation check` | `The dev Keycloak SPI returns 200 and an `spi-ok` status on /health/ready` |

#### TC10/b — The detailed description of the test has to be brought over (not only its title)

**The textual specification of a promoted test must not be lost.** The `spec.md` / `plan.md` of the cycle contains the goal, the steps and the expected result of the test case — **bring this content over** into the register, into the detail block below the table. The one-line cell of the table is only a pointer; the next cycle will know from the block how to **run** the test.

**A mandatory format — one block per item below the table of the section:**

```md
<!-- INCLUDE:lang/08-doc-sync.md#TC10-tetel-blokk-sablon -->
```

**Faithfully, but normalized to be self-contained — do NOT copy blindly.** The text of `spec.md`/`plan.md` often contains elements that are meaningless or forbidden here. When bringing it over, it is **mandatory** to weed these out:

| What the source text may contain | What you do with it |
|---|---|
| a spec section ordinal (`1.2.`), a cycle reference (`the test of cycle-19`) | **you delete it** — TC10 forbids it |
| "see above", "according to the point above", a spec-internal cross-reference | **you resolve it**: you write in what it references |
| a concrete secret (a shared platform credential) | **you replace it with a pointer** — TC5 |
| a cycle-specific one-off step (a migration, a one-off data load) | **you leave it out** — it is not a recurring expectation |
| an unverified / assumed step | **you do not bring it over**, a question into `doc-sync-questions.md` — TC3 |

The **content** (the goal, the order of the steps, the expected values), however, comes over **in full**: if there were three steps and two expected error codes in the spec, there will be three steps and two error codes here as well. Shortening "to the essence" is **not allowed** — the essence is exactly what is needed for the reproduction.

**Rewriting retrospectively:** if there is already a referencing item or a row without a detail block in the file, **rewrite it to be self-contained in the next doc-sync run**. If the behavior is not unambiguous from either the text of the item or the test file, that is **a question into `doc-sync-questions.md`** (do not guess) — the item stays until then, but marked.

### TC11 — Runnable coordinates: the startup + an example call are mandatory

**A recipe is a recipe because a stranger can run it** — not because it names the test file. An `npm test` line on its own is not a recipe: it does not say what it needs, how I call the endpoint, and how I know that it is good.

**The mandatory elements of every `R-ID` recipe:**

1. **`<field:f_startup>`** — how I bring up the environment that this recipe requires: a concrete command (`docker compose -f … up -d`, `podman run …`, `npm run dev`, `oc port-forward …`), plus **how I check that it comes up** (the health endpoint + the expected response). If the recipe requires no environment (a pure unit test), write it out explicitly: `N/A — it requires no running environment`. Leaving it empty is not an option.
2. **`<field:f_example_call>`** — if the recipe touches an HTTP/gRPC/CLI endpoint: **at least one actual call**, with the full URL, the headers, the payload and the **expected response**. A `curl`, or a `.http` block (VS Code REST Client / IntelliJ) — the latter is better if there are already `.http` files in the project (then **reference the file as well**: `test/http/token-exchange.http`). If the call requires a token, **the call for obtaining the token should go here as well** ("Authorization: Bearer …" on its own is not runnable).
3. **`Shutdown / cleanup`** — what has to be stopped/deleted after the run (especially for a `<status:scope_shared_remote>` scope, TC5/TC3).

**The prerequisites must not hang in the air.** In the `<field:f_prerequisite>` column of section 2/3, text of the *"a local keycloak is running"*, *"the mock stack is running"*, *"the VPN connection is active"* kind is **worthless on its own** — it has to say **how** I fulfill it. Therefore the prerequisite either **references an `R-ID`** (which has a `<field:f_startup>` block), or the `<field:f_startup>` block of the referenced recipe contains it. If there is no recipe for a prerequisite (e.g. starting the local Keycloak is described nowhere), **add a new recipe for it** — this is typically the most useful item in the whole register.

> **The TC3 verification holds here too:** write in only a start command and an example call that **actually ran in this cycle** (the `test-report/` is the evidence), or that the user confirmed in `doc-sync-questions.md`. An invented `curl` is worse than a missing one — the next cycle will build on it.

### TC9 — The mandatory test report item (TR3) — agreed with the user

**A mandatory report artifact goes into the `specs/cycle-NN-<name>/test-report/` folder in every cycle** — the own, openable report of the test tool (Allure/Playwright HTML, pytest-html, JUnit XML, coverage). The reports live in **per-round subfolders** (TR5): `test-report/validate/round-NN/`, respectively `test-report/review/round-NN/` for the re-validate rounds of 09; in the root of `test-report/` are the logs (`validation-report.md`, `implement/check-log.md`). **The single source of truth for the command and the artifact name is the `## <sec:cv_test_reporting>` table of `conventions.md`** (filled in by phase 00 together with the user); `07-validate` enforces this with a deterministic gate (`report-gate-check.py`). We do **not duplicate** this in the register (TC1) — here only the expectation and the source reference stand, in the **<field:f_required_report>** row of sections 2 and 3.

**The mandatory duties of the doc-sync in every run:**

1. **Read** the `## <sec:cv_test_reporting>` section of `conventions.md` and the actual content of the `test-report/` folder of the cycle — together with the round subfolders (the **last** `validate/round-NN/` respectively `review/round-NN/` shows what ran in the closing round).
2. **Compare the two.** If a test category or tool ran in the cycle that is **not in the table** (e.g. Allure was just introduced, or a new E2E layer), that is an **incomplete project convention**.
3. **In that case a question to the user is MANDATORY** — add it to `doc-sync-questions.md`, and **wait for the answer** (this is not a silent fix):
   > *"In the cycle `<tool>` ran, but there is no report row for it in the `## <sec:cv_test_reporting>` table of `conventions.md`. What report should it generate, with which command, and under what name should it go into the `test-report/` folder of the cycle? (If no report is needed for this category, I will record that too.)"*
4. **Carrying the answer over — a narrow, permission-bound exception:** `conventions.md` is otherwise the property of phase 00, but **after an explicit answer from the user** the doc-sync may update **exclusively the `## <sec:cv_test_reporting>` table** (a new row / a modified artifact name). Do not touch another section, and do not write into it without an answer.
5. **On the register side**, the `**<field:f_required_report>:**` row of section 2/3 should reflect the current state of the table (the artifact name + `source: conventions.md → ## <sec:cv_test_reporting>`). Check 5 of the TC8 gate verifies this.
6. **If the declared artifact is not there in the folder of the closing round** (e.g. from an older cycle, or because the reports are still in the root of `test-report/` from before the per-round split was introduced), that is **not an error for the doc-sync to fix** — state in the summary that the TR3 gate of `07-validate` did not catch that cycle (an old cycle from before the gate was introduced), and move on.

> **The TC6 bootstrap rule holds:** if there is nothing to promote, `test-conventions.md` **should not be created** just for the sake of the report row. The report expectation then lives in `conventions.md`, which always exists.

### TC8 — The own gate of the file (`tc8-gate-check.py` — scripted)

The DS22 core gate runs on `docs-generated/`, this file is **outside** it, therefore it has its **own gate**. The gate is **fully scripted** — there is no LLM judgement in it, so **do not grep by hand**, run the script (the installer copies it into the same platform scripts folder as `ds22-gate-check.py`):

<!-- INCLUDE:shared/python-cmd.md -->

```bash
python3 <platform-scripts-mappa>/tc8-gate-check.py specs/test-conventions.md \
  --project-root . \
  --marker cycle-NN
```

- **`--marker`**: the current cycle — staleness on the `<field:f_last_run>` markers is computed relative to this. It may be omitted; then it only checks the **existence** of the marker, not the staleness.
- **`--stale-after N`**: at a difference of this many cycles or more the item is outdated (default: **3**, according to the TC4 rule).

**The nine checks:**

| # | What it verifies | Does it block? |
|---|---|---|
| 1 | **Path existence (TC8/1)** — do the repo-internal paths named in the file (a test file, a script, a compose file, a component folder) exist | **FAIL** if the parent folder exists but the target does not (a sure sign: an outdated item). If the path cannot be resolved as repo-internal (an external reference, an image ref, an endpoint), only a **WARN** |
| 2 | **A dangling reference (TC8/2)** — does every item of section 2/3 reference an existing section 1 recipe (`R-ID`), and does it have a reference at all | **FAIL**. A recipe that is not referenced is a **WARN** |
| 3 | **The secret check (TC8/3)** — did a credential forbidden by TC5 get in | **FAIL** for a sure pattern (a PAT/key prefix, a private key block, `oc login --password`, `docker login -p`); a platform word + a credential word in one line is only a **WARN** |
| 4 | **The `<field:f_last_run>` marker (TC4)** — does every recipe and every section 2/3 item get a marker, and which one is outdated | A missing marker: **FAIL**. An outdated one (`--stale-after`): **WARN** → a question into `doc-sync-questions.md` |
| 5 | **The mandatory report row (TC9/TR3)** — is the `**<field:f_required_report>:**` row there at the beginning of sections 2 and 3 | **FAIL** if it is missing from either section. A **WARN** if the row contains a generating command (that is the business of `conventions.md` — duplication) |
| 6 | **Runnable coordinates (TC11)** — does every recipe have a `<field:f_startup>` field; do the ones touching an endpoint have an `<field:f_example_call>` block; do the environment prerequisites of section 3 reference a recipe | **FAIL** for all three — a recipe without a startup/an example call is not runnable, and with a dangling prerequisite the test cannot be reproduced |
| 7a | **Item detailing (TC10/b)** — does every table item of section 2/3 have a `### <ID>` detail block belonging to it, with `<field:f_goal>` / `<sec:steps>` / `<field:f_expected_result>` in it | **FAIL** — the table row is an index, not a test case; without a block the item cannot be reproduced. An orphan block without a table row: **WARN** |
| 7 | **Self-contained items (TC10)** — the "What it verifies" cell of section 2/3 must not start with a spec section ordinal (`1.2.`) and must not reference a cycle (`Cycle 19 …`) | **FAIL** — a description pointing at another document is uninterpretable on its own |

**Exit code:** `0` = every hard check PASSes (a WARN is allowed), `1` = at least one FAIL, `2` = a usage error. **If the file does not exist, the script returns `0`, with a "skipped" note** — according to TC6 its absence in an early cycle is not an error.

**You must not ignore the WARNs**, they only do not block: for each of them the answer is either a fix or a `doc-sync-questions.md` question. On a failure (`1`) the same **human-driven** fixing loop runs as with DS22: the concrete deviation as a `Qnn` into `doc-sync-questions.md`, a fix, then the gate runs again, until it is green.

---

## The objective consistency gate (DS22) + handling a gate failure (DS10)

After the execution it is **mandatory** to run the two-layer, project-independent gate. The core gate is **objective/deterministic** (grep, set comparison, inventory pairing, reading markers) — there is no "judge whether the text is good" in it, therefore Layer 1 is **done by a script, you do not grep by hand**.

### Layer 1 — the always-running, generic core gate (`ds22-gate-check.py`)

Run `ds22-gate-check.py` on the `docs-generated/` folder. The installer copies it into the platform-specific scripts folder (following the pattern of the cycle-status): with Antigravity `.agents/scripts/`, with Claude Code `.claude/scripts/`, with Cursor `.cursor/scripts/`, with Copilot `.github/scripts/`, with Codex `.codex/scripts/`.

```bash
python3 <platform-scripts-mappa>/ds22-gate-check.py docs-generated/ \
  --rename <old-name>=<new-name> \
  --marker cycle-NN \
  --changed-file <the name of the file actually modified, repeatable> \
  --spec-file specs/cycle-NN-<cycle-name>/spec.md \
  --plan-file specs/cycle-NN-<cycle-name>/plan.md
```

- **`--rename`**: the old→new name pairs come from the **DECLARED** renames of the cycle (the roadmap/`spec.md`; e.g. the name of cycle-16 is literally `rename-init-cache-to-init-hash` → `init-cache=init-hash`) — **NOT from guessing at the diff** (DS24b). If a rename is not declared, there is **no automatic inference** — you do not give a `--rename` for it. The script automatically skips the historical sections (`CHANGELOG.md` in its entirety, the "Closed deviations" section of `design-drift.md`).
- **`--marker` / `--changed-file`**: give the files actually modified based on `doc-sync-plan.md` — the script checks whether their header block shows the current `cycle-NN` (DS17). Do **not** give the unaffected files (those may stay with an earlier marker, if the "no action" item of the plan confirms it).
- The script also gives an **informative** (non-blocking) summary about the number of mermaid blocks found in `docs-generated/` — this helps you decide point 2 (see below), but the actual pairing decision is made by you.

The script fully covers 3 of the 4 original checks (a hard PASS/FAIL):
1. A rename leftover (based on the `--rename` above).
3. Folder-index set equality (DS21) — the actual file list of `docs-generated/` **==** the entries of `README.md`.
4. The coverage-marker bump (DS17) — based on the `--changed-file` above.

**5/6. Technical-contract and environment preservation (DS23/DS25).** The same failure pattern as KX3 in the spec→plan handoff, just in the spec/plan → `docs-generated` direction: the `doc-sync-planner`'s "surgical patch" principle (do not rewrite, only the changing section) drifts into summarizing when nothing forces verbatim transfer — a worked-out config table, log/event JSON schema, or error-code table in the spec quietly becomes a **silent loss**, because the bootstrap/reconciliation writes a one-sentence summary in its place instead. The plan's `Environment coordinates` (KO1) table — URLs, ports, test users — gets lost the same way, even though it needs a designated home somewhere in `docs-generated/`, or the docs alone are not enough to run/reach the system locally. With `--spec-file`/`--plan-file`, the script:
- **DS23** — breaks the spec.md's worked-out technical-contract blocks (YAML/JSON config, log/event schema, error-code table) into anchors (the same technique as `V1` in `analyze-gate-check.py`), and checks whether they landed **anywhere** in `docs-generated/` — not necessarily one single file, because the right target (`architecture.md` or a component-specific doc, e.g. `redis-usage.md`) is a decision you make in the plan.
- **DS25** — looks up every non-secret value of the plan's `Environment coordinates` table (URL, port, path, dev test user — allowed per TC5) in `docs-generated/`; the script **skips** password/secret/token-like rows (those must point to a pointer, not the raw value).

**On failure the remedy is the same as for every Layer 1 check:** the missing contract/coordinate becomes a plan item in `doc-sync-plan.md` (typically into `architecture.md`, for a technical contract), the main agent inserts it, then the gate reruns.

**Point 2** (did every diagram from the source come over — DS7) is only helped by the script with an informative block count; the actual inventory → target pairing (does every source diagram have a pair in the output, a binary/`.drawio` → a link + a PNG) **has to be decided by you** — this is the only point of Layer 1 that requires a real (though simple) reconciliation judgement, not a pure set operation. (The numbering deliberately follows the original 1–4 list above, point 2 is left out of the script.)

The exit code of the script (`0` = all three hard checks PASS, `1` = at least one FAIL) + your own check of point 2 decide together whether the gate is a PASS overall.

### Layer 2 — a conditional, declaration-driven cross-check

**IF** the `## <sec:cv_references>` section of `conventions.md` gives an API descriptor (openapi/swagger/etc.), **THEN** the doc-sync compares the generated interface/endpoint inventory against it. **If it is not declared → you SKIP this check, it does not block.** (This is why the "endpoint inventory" section of `system-overview.md` is conditional as well.)

### A gate failure → a human-driven fixing loop (DS10)

The gate is **not** a self-healing subagent loop (like 05/07/09), and **not** loop-less either. If the core gate **fails**:
1. The concrete deviation goes into **`doc-sync-questions.md`** as a new `Qnn` (a deterministic deviation, not a "maybe it is better this way").
2. The **main agent asks** / the user decides or fixes.
3. The **affected `doc-sync-plan.md` plan items + the gate run again** → repetition, until the gate is **green** (or the user stops it explicitly).
4. **A loop limit:** the gate fixing waits for a human decision (there is no runaway risk); per deviation, `doc-sync-questions.md` logs how many times the same one comes back.

> **The doc-sync is NOT a fourth self-healing loop.** It is a separate category: an **objective gate (DS22) + a human-driven fix (DS10)**, not an LC1–LC4-style subagent self-healing loop. The three self-healing loops (analyze/validate/review) stay **three**.

---

## Question handling (DS10/DS12) — `doc-sync-questions.md`

**Every decision point and gate failure** has to be added here immediately as a new `Qnn`, **before** you put it to the user. The **main agent asks** one by one (the subagent does not ask directly).

**Basic rule: we never delete from the list. A closed question is only marked with `[x]`** — the text and the decision stay.

**Iteration rules:**
1. If there is a `[ ]` question, put **one**, wait for the answer. Do not pour all of them on the user at once. **At the end of your answer you must place a direct, clickable link to `doc-sync-questions.md`.**
2. An answered question → `[x]` + a one-line summary (`→ ...`), the decision carried over into the affected document and into `doc-sync-plan.md`.
3. A new question to the end of the list, with the next `Qnn` number.
4. **With an open `[ ]` question the phase STOPS** — do not move on without the answer.

**Structure** (if it does not exist yet, create it):
```md
<!-- INCLUDE:lang/08-doc-sync.md#doc-sync-questions-struktura -->
```

---

## The header block on every generated document (DS17)

The generated documents do **not** get a `<status:draft>→<status:done>` lifecycle. Instead, every generated document gets a short **header block** at the beginning of the file:

```md
> **<field:f_covered>:** up to cycle-NN · **<field:f_last_updated>:** cycle-NN (YYYY-MM-DD) · **<field:f_generator_scope>:** <based on what it is to be kept consistent — what this file covers>
```

- The `<field:f_generator_scope>` field is at the same time the input of the affectedness rule (DS24e): from this the planner knows whether a cycle affects the file.
- The "is it consistent" guarantee is given by the **phase gate** (DS22) in every cycle, not by a status field.
- You bump the coverage marker **only on the files actually modified** (DS22 Layer 1 / check 4).

---

## Templates (DS24a) — a skeleton to fill in + a finished mini example

You **fill in** the literal templates below, you do not compose them from scratch. The **bootstrap and the incremental branch use the same ones**.

### A `doc-sync-plan.md` item

Every item is one line + (for the `<status:op_reconciliation>`/`<status:op_new>` items) the finished **replacement text block** of the subagent written into the same place. **You write the replacement text into the file as well** (you do not only keep it in your memory) — this way the resume of an interrupted run (DS10) can apply it again from the file, and the planner does not have to be re-run.

**Skeleton:**
```md
<!-- INCLUDE:lang/08-doc-sync.md#DS10-doc-sync-plan-vaz -->
```
**A finished example:**
```md
- [ ] docs-generated/system-overview.md — reconciliation — updating the "Init-hash flow" sequence to the /init-hash endpoint; the old /init-cache diagram replaced (scope: token-init flow)
- [ ] docs-generated/CHANGELOG.md — new — the cycle-16 entry: the /init-cache → /init-hash rename (scope: token-init flow)
- [ ] docs-generated/architecture.md — no action — the build/deploy did not change in cycle-16 (scope: build/ops)
```

### The header block (DS17)

**Skeleton:** see above. **A finished example:**
```md
<!-- INCLUDE:lang/08-doc-sync.md#DS17-fejlec-blokk -->
```

### A `CHANGELOG.md` entry (DS15)

**Skeleton:**
```md
<!-- INCLUDE:lang/08-doc-sync.md#DS15-changelog-vaz -->
```
**A finished example:**
```md
## cycle-16 — renaming init-cache to init-hash (2026-06-04)

**What changed in the behavior:** the token-init endpoint `/init-cache` → `/init-hash`; the request/response format is unchanged.
**What changed in the documents:** system-overview.md (the token-init flow sequence + the state model), design-drift.md (the HLD `/init-cache` ↔ as-built `/init-hash` deviation into "Closed deviations").
**Renames:** `init-cache` → `init-hash` (the endpoint + all of its variants).
```

### The `system-overview.md` skeleton

```md
<!-- INCLUDE:lang/08-doc-sync.md#DS-system-overview-vaz -->
```

### A `design-drift.md` item (DS20)

**Skeleton:**
```md
<!-- INCLUDE:lang/08-doc-sync.md#DS20-design-drift-vaz -->
```
**A finished example:**
```md
## Active deviations
- **token-exchange-mode** — Design: the HLD states RFC 8693 token exchange. As-built: a legacy Keycloak `subject_issuer`. Justification: the legacy IdP does not support RFC 8693 (a POC limitation).

## Closed deviations
- **init-endpoint-name** — Design: the HLD says `/init-cache`. As-built: `/init-hash` (cycle-16). Closed: the HLD is to be updated; the system uses `/init-hash`.
```

### `specs/test-conventions.md` (TC2)

**Skeleton** — a mandatory **`## <sec:coordinates>`** block at the beginning of the file (TC13), followed by exactly three **numbered** sections (2/3 reference 1), and finally an optional, **unnumbered** `## <sec:not_promoted>` appendix (TC12):
````md
<!-- INCLUDE:lang/08-doc-sync.md#TC2-test-conventions-vaz -->
````

> **Every table row has a `### <ID>` detail block belonging to it** (TC10/b) — the table is the index, the block is the test case. The TC8 gate checks that no item has a missing block, and that the <field:f_goal> / <field:f_steps> / <field:f_expected_result> are in the block.

> The **<field:f_required_report>** row is mandatory in both sections (the TC8 gate checks it). **It contains only the name of the artifact and the source reference — NOT the generating command** (that is the business of `conventions.md`, TC1: we do not duplicate). If the project deliberately does not generate a report, the value of the row is `none — according to conventions.md the report generation is not mandatory`.

**A finished mini example (one item of section 1):**
````md
### R03 — Keycloak dev image build + deploy
- **Where it is:** `infra/keycloak/` · image: `nexus.example.local/dev/keycloak:latest` · namespace: `dev-auth`, pod: `keycloak-0`
- **Access:** `https://keycloak-dev.example.local` · health: `/health/ready`
- **Test users / parameters:** `test-user` / `Test123!` (scope: `profile openid`), realm admin: `admin` / `admin` (the dev realm), client-id: `demo-app`
- **Commands:**
  ```bash
  podman build -t nexus.example.local/dev/keycloak:latest infra/keycloak/
  podman push nexus.example.local/dev/keycloak:latest
  oc -n dev-auth rollout restart statefulset/keycloak && oc -n dev-auth rollout status statefulset/keycloak
  ```
- **Example call:**
  ```bash
  curl -s -X POST "https://keycloak-dev.example.local/realms/demo/protocol/openid-connect/token" \
    -d "grant_type=password&client_id=demo-app&username=test-user&password=Test123!"
  ```
- **Prerequisite / order:** `oc login` has happened (the credential is not here — a TC5 pointer: in the vault of the team); after the restart the health returns `ready`, only then may any I item run
- **Scope:** `shared-remote` — the dev cluster is used by others as well
- **Last run:** cycle-29
````

### A `docs-generated/README.md` index row (DS21)

**Skeleton:**
```md
<!-- INCLUDE:lang/08-doc-sync.md#DS21-readme-index-vaz -->
```
**A finished example:**
```md
- `system-overview.md` — An as-built operational overview (capabilities, flows, state). Maintained by the doc-sync (08) in every cycle.
- `architecture.md` — "How it is built/runs": components, build, deployment. Owned by the doc-sync (08).
- `CHANGELOG.md` — A detailed, incremental cycle change log. Extended by the doc-sync (08).
- `design-drift.md` — The deviations of the realized system from the HLD/LLD design. Maintained by the doc-sync (08).
```

---

## Commit + moving on to 09 (1.13)

After the gate runs green — **and only if the answer to the TC12 promotion offer has arrived** (the phase cannot be closed with an open `[ ]` promotion question):

1. **Commit** — the `docs-generated/` + the component READMEs + the working files of the cycle:
   ```bash
   git add docs-generated/ <the affected READMEs> specs/test-conventions.md specs/cycle-NN-<cycle-name>/doc-sync-plan.md specs/cycle-NN-<cycle-name>/doc-sync-questions.md
   git commit -m "cycle-NN: 08-doc-sync"
   ```
   _(Add `specs/test-conventions.md` only if it exists — in an early cycle, without an item to promote, it does not come into existence, TC6.)_
   _(At the bootstrap the `docs-generated/` + the moved files + the reference rewrites; the fate of the root `temp/` working files is decided by work plan 8.)_

2. **Tell the user the next step:**
<!-- INCLUDE:lang/08-doc-sync.md#zaro-uzenet -->
   > **At the end of the answer, place the direct, clickable link of `docs-generated/system-overview.md` (and of `doc-sync-plan.md`).**
> **Phase boundary — a hard stop (PE1).** The phase **ends** with the closing message (the commit identifier + `/clear` + the command of the next phase). In the same round you start **nothing** from the next phase — you do not even create the artifact of the next phase. This holds even if the to-do list of a **context summary / checkpoint**, your own earlier plan or a "let us go through the whole process" sentence given by the user in an earlier round encourages you to go on: the phase boundary of the skill stands above all of these. Only the user's **explicit request meant for this round** overrides it. If you did start anyway, **delete the file created**, restore the clean working tree, and report it.
