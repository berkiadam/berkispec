---
phase: 04
name: bs-write-tasks
description: "berkispec - 04. Use it when plan.md is 'Ready for tasks' (Phase 04), to split the technical plan into well-structured, individually executable and measurable items (DoD). It creates 'tasks.md' ('Ready for implementation') + 'tasks-questions.md' if needed."
prerequisites:
  - "specs/cycle-NN-<name>/plan.md status: <status:ready_for_tasks>"
output:
  - "specs/cycle-NN-<name>/tasks.md status: <status:ready_for_implement>"
  - "specs/cycle-NN-<name>/tasks-questions.md (if a question comes up)"
  - "specs/cycle-NN-<name>/validate-input-from-prev.md (only if there is information to hand over, IP1)"
prev: bs-write-plan
next: bs-analyze
subagents: []
scripts:
  - "scripts/analyze-gate-check.py"
shared:
  - "shared/input-from-prev.md"
  - "shared/artifact-voice.md"
  - "shared/phase-commit.md"
  - "shared/quality-check-tasks.md"
  - "shared/questions-tasks.md"
  - "shared/fix-mode-tasks.md"
---
# 04 — Writing the tasks
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

We develop software in spec driven development. The development is split into cycles. Every cycle is an independently developable, independently testable subunit of the complete implementation.

This is **phase 4 (0–9)** of the process: 0-init · 1-cycles · 2-spec · 3-plan · **4-tasks ←** · 5-analyze · 6-implement · 7-validate · 8-doc-sync · 9-review.

---

## <field:f_prerequisite>

0. **Identifying the cycle:** if the user gave a cycle/file, use that; otherwise offer the most recent `specs/cycle-*` folder for confirmation — <!-- INCLUDE:lang/common.md#ciklus-beazonositas --> — and wait for the answer before moving on.

1. **`conventions.md` existence check:** read `conventions.md` in the root of the project. If it does not exist, STOP — they should return to phase `00`. _(The phase runs on the feature branch of the cycle; the closing commit goes there — in a No-VCS project the commit is skipped.)_
2. Read the status of `plan.md`. **If the status is not `<status:ready_for_tasks>`, do not start writing a tasks list.** Tell the user that the plan is not closed yet, and that they should return to the `03` plan phase.
3. **The open questions are closed:** the `<status:ready_for_tasks>` status implies it, but check it explicitly — there is no open `[ ]` question in either `spec-questions.md` or `plan-questions.md`. If there is, the plan is not really closed: report it, and they should return to phase `03` (or `02`).

---

## Continuing after an interrupted run

If writing tasks.md was interrupted and continues in a new session:

1. Read the current state of `tasks.md`.
2. Find the first incomplete or uncertain part: is there a group without a closing `[CHECK]`, is there a `[RED]` without its pair, is there a change from the plan that is not covered?
3. If the tasks list is partly there and only the finish is missing, continue from where it was left off — do not start again.
4. If the list looks coherent but the status is still `<status:draft>`, run the quality check, and close it if it passed.

---

## What you have to do

**If a `tasks.md` already exists in the `specs/cycle-NN-<cycle-name>/` folder:** read it, and run the quality check on it (see below). If you find a deficiency — a missing task, a task that is too large, a missing `[CHECK]`, a plan coverage gap — fix it, and only close it afterwards.

**If `tasks.md` does not exist yet:** create it in the `specs/cycle-NN-<cycle-name>/` folder according to the structure below.

**Do not implement anything.** The tasks list is the input of the implement phase — now we only define the steps.

**Do not add a task that is not in the `<sec:planned_changes>` section of the plan.** The tasks list is the exact breakdown of the plan — it does not widen and does not narrow the scope.

**If a task cannot be described concretely** (there is no unambiguous affected file, there is no unambiguous completion criterion), that signals a deficiency of the plan. Stop, state precisely which step is under-specified, and ask the user to complete `plan.md`. At the same time set the status of `plan.md` back to `<status:draft>` — the plan must not stay in `<status:ready_for_tasks>` status if you found a deficiency. After the plan is updated and the `<status:ready_for_tasks>` status is restored, the tasks list can continue.

---

## Context loading rules

- Read only `plan.md`. The spec and the source files were already processed in the plan phase — do not read them again.
- If a concrete file name or path is needed for the description of a task and it does not appear in the plan, only then read the affected file.
- **`tasks-input-from-prev.md`** (if it exists) — the items handed over to you by the earlier phases. See the "Handover between phases" section.

---

## Handover between phases (`*-input-from-prev.md`) — IP1

**What you READ:** if `specs/cycle-NN-<cycle-name>/tasks-input-from-prev.md` exists, read it. It contains the preparatory steps and ordering constraints that surfaced in phase 02/03 (e.g. "the key generation has to precede the container build"). Either build every `[ ]` item into `tasks.md` **as a task or as an ordering constraint**, or drop it with an explicit justification, and tick it off. **Guard:** if the file does not exist, that is not an error — continue.

**What you MAY WRITE INTO:**
- **`validate-input-from-prev.md`** — for **07**: a runtime prerequisite or an operational note that came to light during the task breakdown but will only be relevant at the validation (e.g. "the TREG-04 test can only be run after the seed task", "the port conflicts with the developer stack, therefore it has to be stopped before the validate").

<!-- INCLUDE:shared/input-from-prev.md -->

---

## Determining the Prerequisite documents

The Prerequisite list going into the header of tasks.md is the complete context of the implementing agent — it reads these before the execution.

Always in it:
- `specs/<cycle-name>/plan.md`

In it, if it appears in the `<sec:schema_artifacts>` table of the plan with `<status:reviewed>` status:
- OpenAPI YAML, Redis key map, DB schema, Avro schema, etc.

Never gets into it:
- `research.md` or another exploratory phase by-product
- an artifact with `<status:review_required>` status (if there is one, the plan is not closed)

---

<!-- INCLUDE:shared/artifact-voice.md -->

---

## Task format

```md
<!-- INCLUDE:lang/04-write-tasks.md#task-formatum -->
```

### 🔴 A plan reference on every task (PID1) — mandatory

| Rule | Mechanics |
|---|---|
| **Mandatory** | At the end of every task line: `— plan [P-…]`. There is no task without a reference. |
| **The ID is the key, not the ordinal** | `plan [P-CONFIG]` — **not** `plan.md § 3.1`. The ordinal shifts when the plan grows; the ID does not. If a section in the plan has **no** `[P-…]` ID, that is a plan deficiency → a `tasks-questions.md` question (do not invent an ID). |
| **One primary source (D)** | Exactly **one** ID is the primary one. If another section is relevant too, it goes in parentheses: `— plan [P-CFGPROP] (see also: [P-CONFIG])`. Two equal-rank IDs on one task are **forbidden** — if two are really needed, the task **is to be split into two tasks**. |
| **Only at an executable section (E)** | The target of the primary reference is always a plan section bearing a `[P-…]` ID. **You must not reference an inventory, a goal or an ordering** (these do not even get an ID). If you find no plan section for the task, that is a **plan deficiency** → `tasks-questions.md`, do not substitute text of your own. |
| **A sub-scope, if you share (F)** | If **several tasks** reference the same ID, each of them gets a parenthesized scope marking: `— plan [P-CONFIG] (config files)` / `— plan [P-CONFIG] (loader module)` / `— plan [P-CONFIG] (unit test)`. Without it, at the first such task the implementer implements the **whole** section. |

- The ordinal (`T001`, `T002`, ...) is sequential, based on the execution order.
- The description is one line, concrete, and starts with an active verb (e.g. *Create*, *Extend*, *Add*, *Run*).
- The file path is mandatory if the task touches a file. If the task is running a command, the file path may be omitted.
- **TDD marking:** mark a test-writing task with a `[RED]` prefix, and the implementation task belonging to it with a `[GREEN]` one. The `[RED]` task always precedes its pair.
  - **Exception — a browser E2E (UI) test:** fail-first is not expected there (the test is written for the finished interface). If the test-writing task stands AFTER the implementation, its marker is **`[GREEN]`**, not `[RED]` — otherwise the marker suggests a false TDD order. If you do leave it as `[RED]` (because it really is fail-first), **justify it with a parenthesized half-sentence** in the text of the task.
- **A marker is mandatory on every task — there is no task without a prefix.** The reason: the absence of the prefix cannot be distinguished from somebody having **forgotten** the marker.
- **`[OPS]` — a sharp boundary:** only a step that does **NOT modify a repo file** but changes the **environment or an artifact** may get it: build, image push, deploy, manual configuration, creating/deleting an external resource, asking for approval, rollback.
  - **Whatever edits a repo file is NEVER `[OPS]`** — that is `[RED]` (writing/updating a test) or `[GREEN]` (modifying a source and config file), even when it is about a **regression fix**. A `TREG` task that updates an existing test file gets a `[RED]` marker.
  - This boundary is what makes it possible to filter out the `[OPS]` tasks mechanically for the destructive-operation check (see below) — if code-editing tasks are also `[OPS]`, that filtering is useless.
- **Verification task:** the `[CHECK]` prefix, mandatory at the end of every logical group — it contains a concrete command from the `<sec:verification_strategy>` section of the plan (e.g. `npm test`, `npm run typecheck`). The file path may be omitted.
- **Marking a parallelizable task:** if a task can be done at the same time as another one (there is no dependency between them), mark it with a `⟂ Tkkk` suffix. Mark it only if the parallelization really saves time.
  - **Example:** `- [ ] T012 [GREEN] Implement the foo service — `src/foo.ts` ⟂ T013` — it means that T012 and T013 can be edited at the same time, because they **do not touch the same file** and there is no dependency between them. If they touched the same file, it CANNOT be marked as parallel.
  - **🔴 A `[CHECK]` is NEVER parallelizable with the task that creates or modifies the artifact it runs** (a test-writing `[RED]`/`[GREEN]` ⟂ its own `[CHECK]` = a false green: the `[CHECK]` runs on the old or missing test file). The check before writing out the `⟂`, mechanically: **are the file sets of the two tasks disjoint?** If any file is common — or one task runs the file/command that the other one writes —, the `⟂` is **forbidden**.
- **Numbering conventions — `T`, `TREG`, `TLAST`:**
  - **`Tnnn`** — a normal, sequentially numbered implementation task (`T001`, `T002`, …) in the logical groups.
  - **`TREGn`** — a regression review task (`TREG1`, `TREG2`, …) in the mandatory "<sec:regression_review_group>" closing group. In order, without a `[CHECK]`. Only for a file that is in the `<sec:regression_impact>` table of the plan but not in the `<sec:planned_changes>`. **Its marker is `[RED]`** (it updates an existing test file) — **not `[OPS]`**, because it edits a repo file.
  - **`TLASTn`** — the tasks of the "<sec:documentation_group>" closing group (`TLAST1`, `TLAST2`, …), at the very end of the list, if there are any. These run last. **IMPORTANT (DS4):** every file of `docs-generated/` (`system-overview.md`, `architecture.md`, `CHANGELOG.md`, `design-drift.md`, the folder index) is owned **exclusively** by the `08-doc-sync` phase; 04 generates **no** `TLAST` task for them.
    - **Component README — the boundary is the existence of the component:** updating the README of an **existing** component (env variable, port, startup, connections) is the business of **08-doc-sync** → **there is no `TLAST` for it**. The first `README.md` of a **new component**, however, is part of building it → it appears as a normal `Tnnn` task (`[GREEN]`), together with the other files of the component, **not** as a `TLAST`.
    - **🔴 A status-updating task is FORBIDDEN.** Never add a task for switching the **status field** of `spec.md` / `plan.md` / `tasks.md` ("set it to `<status:done>`", "update the state of the phase"). The status lifecycle is the **machinery of the framework**: `07-validate` sets all three to `<status:done>` in case of a PASS. Such a task conflicts with it and gives false coverage. If such a "meta" item appears in the `<sec:definition_of_done>` of the spec (e.g. *"the documentation and the state of spec.md have been updated"*), that is a **spec error** — do not cover it with a task, but add it to `tasks-questions.md`.
    - A `TLAST` therefore only gets into the list if the plan **explicitly** asks for a documentation update that lives **neither** in `docs-generated/` **nor** is a component README (e.g. a project-specific manual document).
  - The numbering starts from 1 within every prefix and increases.

---

## Quality expectations for the description

**The description of the task is a navigation point, not a standalone specification.** The implementing agent reads the plan before doing the work — the job of the task is to show unambiguously which section of the plan the change relates to. The detailed logic, the interfaces and the error handling are contained by the plan.

The description has to contain:
- **What to do** — an active verb + the name of the affected unit (function, class, file)
- **Which file** — the path is mandatory if the task touches a file
- **A plan section reference** — **always mandatory**, with the stable ID: `— plan [P-…]` (the format and the rules are above, in the *A plan reference on every task* table)

Give a detail in the description of the task **only if** the plan does not contain it:
- For running a command: the actual shell command (e.g. `openssl genrsa -out key.pem 2048`)
- For referencing an external resource: if an external resource is needed for testing or running the task (a certificate, an API key, mock data, a special configuration), reference the section of the plan where this can be found (`— plan [P-CONFIG]`). The implementing agent should not have to go searching.

> **🔴 No duplication (PID1/b) — the detail lives in the plan.** If a value list, a code→code mapping, a locator strategy or a step sequence is **already in the plan**, you do **not copy it over** into the task: the task says in one line what has to be done, and points there with a `[P-…]`. Identical content kept in two places **drifts apart**, and afterwards nobody knows which one is true.
> - **If you feel that the detail is needed in the task, because it cannot be carried out without it** → the detail **is missing from the plan**: in fix mode (05-analyze) write it **into the plan** (that is the business of the `plan-fixer`), in the normal flow add it as a `tasks-questions.md` question. tasks.md is **never a substitute for the plan**.
> - **Exception — the `[CHECK]` and `[OPS]` commands:** these stand in the task verbatim (this is what the implementer runs), matching the identical command in the plan **character by character**.

**The principle of compression:** what a developer can tell a colleague in one sentence is enough. The detail is in the plan — do not copy it over.

| Too verbose | Good |
|---|---|
| `Implement: async callLegacyVerify(legacyLoginBaseUrl, jweToken, logger): Promise<{userId, sessionId, regId}> — GET <url>/verify (Authorization: Bearer), if not 200 throw new HttpError(403, 'Legacy token verification failed', 'TMP_031')` | `Implement the callLegacyVerify service (GET /verify, with TMP_031 error handling)` |
| `Rewrite the { error: "..." } expected responses of the error tests to the { correlationId: <string>, messages: [{ code: "TMP_XXX", params: { description: "..." } }] } format` | `Update the expected responses of the error tests to the ErrorMessageResponse format` |

**Length limit:** if the description approaches 100 characters, you have probably copied a plan detail into it — the reference is enough.

---

## Tasks structure

```md
<!-- INCLUDE:lang/04-write-tasks.md#tasks-struktura -->
```

**The plan reference of the group header (B) is mandatory:** at the end of every `## <group>` title, the plan IDs covered by the group are present. This is what makes it followable at a glance for a human which chapter of the plan is realized where — the tasks are grouped by **execution order**, not by the structure of the plan, so one plan section **may scatter into several groups** (e.g. the test writing of `[P-CONFIG]` into group 1, its implementation into group 3).

**The `<sec:plan_coverage>` table (C) is mandatory, and it is produced when the list is CLOSED** — when every task is already there. It is not separate work: you go through the `[P-…]` sections of the plan, and collect the task identifiers referencing each of them. **Every ID has to appear**: if there is no task belonging to a plan section, the row still gets in, with `—` and a **one-sentence justification** (e.g. "only a verification strategy, 07 runs it"). An empty row without a justification = a coverage gap.

The groups mirror the stages of the execution order of the plan. Every group can be done and verified on its own. Every group has at least one `[CHECK]` task at its end.

**Mandatory closing groups:** the last two groups of the tasks list are always the following, in this order:

**1. <sec:regression_review_group>** — exclusively for the files that **appear** in the `<sec:regression_impact>` table of the plan but **do not appear** in the `<sec:planned_changes>` section of the plan. If a file appears in both places, it is always a T task — not a TREG. Add it only as a plain task (`[ ] TREG...`) without a `[CHECK]`. If it requires no modification, the task is indicative ("Check that it stayed untouched"). **RUNNING the regression tests does not belong here — that is the task of the validate phase (07).**

**Ordering rule:** the implementing agent does the TREG tasks before the <sec:documentation_group> section, but after the section containing the integration [CHECK] tasks. If updating a TREG file is needed for the [CHECK] task of an earlier section to be green, that file is not a TREG — it goes in as a T task before the [CHECK] task of the appropriate section.

**A file may appear only once in the tasks list.**

If the plan says that there is no regression impact, this group may be omitted.

```md
<!-- INCLUDE:lang/04-write-tasks.md#desztruktiv-csoport-sablon -->
```

**2. <sec:documentation_group>** — a standalone, last group, **only if it is needed**. **You generate a `TLAST` task neither for any file of `docs-generated/` (architecture.md, system-overview.md, CHANGELOG.md, design-drift.md), nor for the `README.md` of an existing component** — these are written and kept consistent by the `08-doc-sync` phase, with an overview of the whole cycle (DS4). This group gets into the list **only if** the plan **explicitly** asks for a documentation update that does **not** belong under the ownership of `docs-generated/`. In a purely renaming/refactoring cycle, or if the plan names no such document, this group **may be omitted**.

```md
<!-- INCLUDE:lang/04-write-tasks.md#dokumentacio-csoport-sablon -->
```

_A note on document ownership (DS4): `architecture.md` and the whole `docs-generated/` folder are owned **exclusively by the `08-doc-sync` phase** — the earlier `TLAST1 → docs/architecture.md` closing task is **retired**. The implementation (06) concentrates on the code; the "as-built" documentation of the realized system (behavior description, architecture, changelog, drift) is composed and validated by the doc-sync with its own consistency gate. This way there is no double writer and no ordering problem._

---

## The marks of a good task

- **Small**: a task is suitable for a standalone commit if **(a) it touches at most 2 files, AND (b) it covers a single logical change**. If there are 3+ files OR several independent logical changes in it, split it into independently committable parts. (The borderline case — e.g. 2 files + complex logic — is also to be split if condition (b) is violated.)
- **Concrete**: it is unambiguous what has to be done and in which file.
- **It counts as done** if: the affected file is modified, and the closing `[CHECK]` task of the group ran without an error. A `[RED]` or `[GREEN]` task on its own cannot be considered done until the group-closing `[CHECK]` is green.
- **Non-overlapping**: one change appears in one task only.

If a task is too large, split it in two.

---

<!-- INCLUDE:shared/quality-check-tasks.md -->

## Stopping rules

If any of the following holds while writing the tasks, **STOP — stop and tell the user** (do not invent the missing part):

- **A task cannot be specified:** there is no unambiguous affected file, there is no completion criterion, or the step cannot be broken down unambiguously. This signals a deficiency of the plan. Set the status of `plan.md` back to `<status:draft>`, state precisely which step is under-specified, and ask for the plan to be updated. The tasks list can only continue afterwards.
- **You cannot formulate a task for an entry of the `<sec:planned_changes>` of the plan:** the entry is under-specified or uninterpretable. Set `plan.md` to `<status:draft>`, state which entry it is, and ask for a refinement.
- **A task can only be done conditionally** (e.g. it depends on a file that does not exist yet or on the result of another cycle): state the dependency, and ask for a decision — should it be added as a prerequisite task, or is the plan incomplete.
- **The plan and the existing code contradict each other:** a step seems unrealizable based on the current code base. Do not modify the plan yourself — report it, and ask for a decision.
- **A circular dependency in the tasks:** a dependency of the A → B → A kind that cannot be resolved by reordering. State it precisely, and ask for a decision.

In every case report only **one** problem at a time.

---

## Status handling

### The mechanical gate before closing (M)

The same deterministic gate that is the first step of `05-analyze` — but **it runs here, before the closing**:

<!-- INCLUDE:shared/python-cmd.md -->

```bash
python3 <platform-scripts-mappa>/analyze-gate-check.py specs/cycle-NN-<cycle-name>
```

- **`0`** → there is no blocking finding; the closing can continue. The `## Javaslatok` and the `## <sec:inventory>` block are informative — you may decide about the suggestions, but they do not block.
- **`1`** → **there is no status change.** The `## <status:must_fix>` items are mechanically detected errors (a missing `— plan [P-…]` reference, a non-existent ID, a marker, `⟂` symmetry, an outdated `<sec:plan_coverage>` table, a DoD item without a task, a shell variable crossing a task boundary, a non-existent artifact being run).
  - fix the **`target phase: 04`** items **now**, then run the gate again;
  - report the **`target phase: 03` / `02`** items to the user according to the *Stopping rules* — you do not fix a deficiency of the plan or of the spec.
- **`2`** → a usage error (a missing file) → report it, do not guess.

> **Why here (M):** if the error comes to light already here, the fix happens **in the same phase, in a fresh context**. If it slips through, it comes to light in the self-healing loop of `05-analyze`, where a fixer subagent and an analyzer round have to be spent on it — on the same error.


If the list is complete, the quality check passed **and the mechanical gate returned `0`**, put the question to the user:
<!-- INCLUDE:lang/04-write-tasks.md#statusz-megerosites --> — Do not switch the status before the confirmation. **At the end of the answer, place the direct, clickable link of `tasks.md`.**

If the user confirms:
- Set the status of `tasks.md` to `<status:ready_for_implement>`.
- **Commit immediately** according to the *Phase-closing commit* below (`<PHASE-TAG>` = `04-tasks`). Confirmation → writing the status → commit: this is a single sequence of steps, do not interrupt it.

<!-- INCLUDE:shared/phase-commit.md -->

In the block above, the value of `<PHASE-TAG>` in this phase is: **`04-tasks`**, and the closing status is: **`<status:ready_for_implement>`**.

> **Done lifecycle:** `tasks.md` goes `<status:ready_for_implement>` → (during the implementation `<status:ready_for_validate>`) → after the PASS of the validate (07) to `<status:done>` status. Phase 08 already expects `<status:done>`.

If the status is `<status:ready_for_implement>` **but the phase-closing commit is missing** (a VCS project, `git log -1 --oneline` does not show the `cycle-NN: 04-tasks` commit) — commit first, and only close the phase afterwards.

If the status is `<status:ready_for_implement>` (and the commit is there), stop. Do not start implementing or analyzing. Tell the user the next step and the starting command of the phase, for example:
<!-- INCLUDE:lang/04-write-tasks.md#zaro-uzenet -->
> **At the end of the answer, place the direct, clickable link of `tasks.md`.**

---

<!-- INCLUDE:shared/questions-tasks.md -->
---

<!-- INCLUDE:shared/fix-mode-tasks.md -->
