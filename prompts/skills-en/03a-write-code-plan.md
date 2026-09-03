---
phase: 03a
name: bs-write-code-plan
description: "berkispec - 03a. Use it when the spec.md of the cycle is 'Ready for planning' (Phase 03a), to work out the CODE SIDE of the technical implementation plan: environment coordinates, planned changes (with a purpose), configuration, schema artifacts, the scope gate (code base analysis, the researcher subagent if needed). It closes plan.md with the 'Ready for test planning' status; the test plan is written by /bs-write-test-plan."
prerequisites:
  - "specs/cycle-NN-<name>/spec.md status: <status:ready_for_plan>"
output:
  - "specs/cycle-NN-<name>/plan.md status: <status:ready_for_test_plan> (the code-plan sections)"
  - "specs/cycle-NN-<name>/plan-questions.md"
  - "specs/cycle-NN-<name>/tasks-input-from-prev.md and/or validate-input-from-prev.md (only if there is information to hand over, IP1)"
prev: bs-write-spec
next: bs-write-test-plan
subagents:
  - "agents/researcher.md"
scripts:
  - "scripts/analyze-gate-check.py"
shared:
  - "shared/plan-self-contained.md"
  - "shared/dereferencing.md"
  - "shared/spec-artifact-transfer.md"
  - "shared/plan-section-ids.md"
  - "shared/conventions-change.md"
  - "shared/input-from-prev.md"
  - "shared/artifact-voice.md"
  - "shared/phase-commit.md"
  - "shared/quality-check-plan-code.md"
---
# 03a — Writing the code plan
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

We develop software in spec driven development. The development is split into cycles. Every cycle is an independently developable, independently testable part of the whole implementation.

This is **phase 3a (0–9)** of the process: 0-init · 1-cycles · 2-spec · **3a-code-plan ←** · 3b-test-plan · 4-tasks · 5-analyze · 6-implement · 7-validate · 8-doc-sync · 9-merge.

---

## Cheat sheet

| Section | In one sentence |
|---|---|
| Scope | **The code plan only** — the test sections are written by `03b` (`/bs-write-test-plan`). NO `TS-NN`, `TC-NN`, machine-readable run table or test-file data sheet goes in here. |
| Prerequisite | `spec.md` = `<status:ready_for_plan>`, `conventions.md` exists, a clean working tree. |
| Open questions | Every question into `plan-questions.md`; **the mandatory first question: the E2E test strategy**. |
| Context | The spec + the documentation; the source files are identified by the `researcher` subagent (D2=A). |
| Plan structure | <sec:goal_and_approach>, <sec:affected_components>, <sec:environment_coords>, <sec:planned_changes>, <sec:new_dependencies>, <sec:config_build_changes>, <sec:schema_artifacts>, <sec:reverse_coverage>, <sec:risks_and_decisions>. |
| Section ID | A stable `[P-…]` identifier in the title of every executable plan section (PID1) — `tasks.md` references this, not an ordinal. An ID once issued never changes. |
| The scope gate | A spec source (a requirement/`DoD-NN`) for every plan capability — the `<sec:reverse_coverage>` table (SC1), with the `[P-…]` identifier of the section in the first column; whatever has none goes back into 02 or into `<sec:out_of_scope>`. |
| Phase handover | `plan-input-from-prev.md` read and closed; the information that does not belong here into `tasks-`/`validate-input-from-prev.md` (IP1). |
| The design input | `cycle-design-input.md` (the user's own cycle description) is **read automatically** — its technical/procedural content goes into the plan; you do not rewrite the file (CD1). |
| <sec:environment_coords> | A mandatory `<sec:environment_coords>` (KO1) section: component URLs/ports, start commands, example REST calls, test/API users with passwords, every parameter — with concrete values, without a placeholder and without an empty cell. |
| **Self-containedness** | `plan.md` contains **everything** that is needed for the development/testing — 04 and the `test-runner` read **only this**, not the spec. |
| The gate configuration | If the cycle changes something that a deterministic gate reads from `conventions.md` (report artifacts/path base, Sonar, test commands, ports, the merge strategy), updating `conventions.md` is **part of the cycle**: plan it, and there should be a task for it (GC1). |
| Paths | A code and file reference is **relative to the root of the repo** (`src/app.ts:42`), a document link is relative to the own directory of the file (`./spec.md`); an absolute path and `file://` are forbidden (RP1). |
| No truncation | The **elaborated** artifacts of the spec (OpenAPI, a complete payload, an error matrix, a multi-step test scenario) come over **verbatim and complete** (KX3) — the direction is extension and refinement, not merging. |
| Reference resolution | An input referencing a script/a test/an API **has to be resolved**: the concrete command, URL, payload goes into the plan, not the hint. |
| Validation cycles | A targeted check after every large section, before you move on. |
| Spec critique | An active checklist for every component; a **deficiency** → back into phase 02, an **overreach** (a coordinate in the spec) → lifted over into the plan (the mirror of KX). |
| Closing | The quality check + the **Closing gate (TP2-code, printed ticked)** + the Constitution Check (SK4) + the **mechanical gate** (`analyze-gate-check.py --plan-code-only`, M) + user confirmation → `<status:ready_for_test_plan>`, commit. |

---

## What you have to do

**You write the CODE HALF of the plan** — from `<sec:goal_and_approach>` to `<sec:reverse_coverage>`, plus `<sec:risks_and_decisions>`. The test sections (`<sec:testing_strategy>`, `<sec:plan_test_scenarios>`, `<sec:machine_run_table>`, `<sec:e2e_infrastructure>`, `<sec:regression_impact>`, `<sec:test_specification>`, `<sec:execution_order>`, `<sec:verification_strategy>`) are written by the **next phase**, `03b-write-test-plan`, into the **same** `plan.md`.

> **🔴 Do not start the test sections — not even as a draft.** If the test cases of the spec are "pushing to get into" the plan, they are the input of `03b`, not your deliverable: you may add the corresponding row to the `<sec:reverse_coverage>` table, but not the scenario. **Why:** a half-finished test section is **worse than an empty one** — the `TS7` conversion of `03b` would carry an already existing, faulty structure forward, and that is exactly the defect this phase boundary was born from.

**If a `plan.md` already exists in the `specs/cycle-NN-<cycle-name>/` folder:** read it, and run the quality check on it (see below) — **on the code-side sections**. If you find a gap or a problem — a spec deviation, a missing component design, an incomplete coordinate set, etc. — set the status back to `<status:draft>`, state precisely what the problem is, and fix it according to the iteration rules. (If the plan is already at `<status:ready_for_test_plan>` or further, you still do **not** edit the test sections.)

**If `plan.md` does not exist yet:** create it in the `specs/cycle-NN-<cycle-name>/` folder according to the structure below.

**Do not repeat the content of the spec.** The goal of the plan is to design the technical realization — reference the spec, do not copy it over.
> **🔴 The scope — do not over-generalize it!** This rule (and its pair: "reference `conventions.md`, do not repeat the tool name") applies **exclusively to the justification and to the behavior description**: to the *why*, to the business context, to the acceptance criteria. **It never applies to the data needed for the execution.** The guiding principle in one sentence:
>
> **Reference the DECISION — write out the EXECUTION.**
>
> An example: which test framework the project uses is a **decision** → you reference `conventions.md`, you do not repeat it. But **with which command, on which file, in which environment** the test runs **in this cycle** is **execution** → you write it into the plan concretely. If you are uncertain which side something falls on, ask the question: *"can the downstream phase (04/06/07) obtain this information from somewhere else?"* If not — then it has to go into the plan.

---

<!-- INCLUDE:shared/plan-self-contained.md -->

---

## <field:f_prerequisite>

0. **Identifying the cycle:** if the user gave a cycle/file, use that; otherwise offer the most recent `specs/cycle-*` folder for confirmation — <!-- INCLUDE:lang/common.md#ciklus-beazonositas --> — and wait for the answer before moving on.

1. **`conventions.md` existence check:** read `conventions.md` in the root of the project. If it does not exist, STOP — they should return to phase `00`.
2. **Working-tree check (only with VCS):** run `git status --short`. If there are uncommitted changes, list them, and ask in one round whether I should commit or continue. (In a No-VCS project it is skipped.)
3. Read the status of \`spec.md\`. **If the status is not \`<status:ready_for_plan>\`, do not start writing a plan.** Tell the user that the spec is not closed yet, and that they should return to the `02` spec phase.

4. **Reading the cycle design input (CD1) — automatic:** if `specs/cycle-NN-<cycle-name>/cycle-design-input.md` exists, read it **in every run, without a separate prompt**. This was written by the user in free form about the cycle; 02 has already lifted its behavioral part into the spec, but its **technical, procedural and coordinate content** (commands, hosts/ports, existing components, build/deploy steps, performance and integration constraints) is **directly the input of the plan**. For the rules of processing it, see the *"Processing the cycle design input (CD1)"* section. **Guard:** if the file does not exist or contains only the template text, say so in one sentence and continue — it is not an error and not a reason to stop.

_A note: if the spec is `<status:ready_for_plan>`, `specs/roadmap.md` is implicitly closed — the `02` spec phase has already checked it. A separate roadmap check is not needed._

---
---

## Continuing after an interrupted run

If the plan phase is interrupted and continues in a new session:

```
1. Read the current state of plan-questions.md (if it exists).
   → Go through the questions in order: you may skip the [x]s, clarify the
     [ ]s one by one. If a new question comes up while reviewing an [x],
     add it to the end of the list with a new Qnn number.

2. Only write/continue code-plan sections if every question is [x].

3. If the code half of plan.md looks coherent but the status is not
   <status:ready_for_test_plan>:
   run the quality check + the Constitution Check, then ask for a confirmation.
```

The current state of `plan.md` and `plan-questions.md` + this prompt is enough for the restart.

---
---

## Handling open questions

`plan-questions.md` is the question register of the plan phase. Every question that comes up, every spec deficiency, decision point and contradiction goes here — not only into the dialogue. This is what makes the process traceable and continuable after an interruption.

**Basic rule: we never delete from the list. A closed question is only marked with `[x]` — its text and the decision stay.**

### plan-questions.md structure

If it does not exist yet, create it in the `specs/cycle-NN-<cycle-name>/` folder:

```md
<!-- INCLUDE:lang/03a-write-code-plan.md#plan-questions-struktura -->
```

Always append a new question to the end of the list, with the next sequential `Qnn` number.

> **The very same file is continued by `03b-write-test-plan`** with the next free `Qnn` number. Do **not** renumber and do **not** delete the entries — `03b` works from your closed decisions (the `Q01` E2E strategy in particular).

### The workflow

1. **At the start:** before you write any plan section, read the spec and the affected source files, and identify all the questions that come up — including the _"The fundamental technology decisions are to be clarified in the plan phase"_ points marked in the spec. Add all of them to `plan-questions.md` in the `- [ ] Qnn` format, with sequential numbering (Q01, Q02, ...). If there are already earlier questions in the file, continue the numbering from there — do not modify and do not delete the old entries. If questions get into `plan-questions.md`, set the status of `plan.md` to `<status:open_questions>`.

    > **🔴 THE MANDATORY FIRST QUESTION — the E2E test strategy.** The **first** entry (`Q01`) of `plan-questions.md` is always the approach to E2E coverage. Do not skip it and do not push it back. The agent must review the existing testing infrastructure beforehand (based on `conventions.md` / the existing integration tests).
    - **If `specs/test-conventions.md` exists:** put the Q01 question starting **from it** — do not ask from scratch. List concretely which section 2/3 items and section 1 recipes you plan to lift into this cycle, and ask: are the data of block 0 (URL, pod, test user, parameter) still valid, does anything have to be left out or added. Lifting a recipe with a `<status:scope_shared_remote>` scope requires an **explicit approval**.
    - If the existing testing infrastructure is hybrid or builds on native host processes (not fully containerized), the question must necessarily surface this deviation from the "Strict containerization rule", and it has to make a proposal:
      1. we keep using the existing hybrid/native infrastructure in this cycle (to minimize the risk of rewriting the existing tests), or
      2. we now transform the whole testing infrastructure to be fully containerized (complying with the strict rule).
    - The agent makes a recommendation based on the spec and the existing infrastructure — three possible levels: (1) a real containerized stack, (2) partial mocking (only what is really not available), (3) full mocking (only if real infrastructure cannot be realized in any form). It justifies the recommendation. The decision gets into the plan only after the approval of the user. Mocking is acceptable only with a documented justification.

2. **Clarification:** proceed question by question — put only one to the user at a time. When the answer has arrived: mark it with `[x]` in `plan-questions.md`, and write a one-line summary of the decision next to it (`→ ...`). If a new question comes up from the answer: add it immediately to the end of the `plan-questions.md` list with the next `Qnn` number, before you continue. **Every time you put a question or ask for approval/review, you must place at the end of your answer a direct, clickable markdown link to the affected files (e.g. in the form `[plan-questions.md](file:///absolute/path/specs/cycle-NN-name/plan-questions.md)`).**

3. **Continuation:** only start writing plan sections if every question of `plan-questions.md` is in `[x]` status.

4. **Closing:** if every section is done, every question is closed and the quality check passed, put the question to the user: <!-- INCLUDE:lang/03a-write-code-plan.md#statusz-megerosites --> — Do not switch the status before the confirmation. **At the end of the answer, place the direct, clickable link of `plan.md`.**

5. **A restart in a new context:** if the plan phase is interrupted and continues in a new session, the first step is reading `plan-questions.md` (if it exists). Go through all the questions in order — you may skip the `[x]`s, clarify the `[ ]`s one by one according to the above. If a new question comes up while reviewing an already closed question (`[x]`), add it to the end of the list with a new `Qnn` number, and clarify it before you move on.

---
---

<!-- INCLUDE:shared/dereferencing.md -->

---

<!-- INCLUDE:shared/conventions-change.md -->

---

<!-- INCLUDE:shared/spec-artifact-transfer.md -->

---

## Handover between phases (`*-input-from-prev.md`) — IP1

**What you READ:** if `specs/cycle-NN-<cycle-name>/plan-input-from-prev.md` exists, read it at the beginning of the phase. It contains the technical and implementation details that surfaced in phase 01/02 (affected components, existing solutions, technology constraints) that did not fit into the spec. Either build every `[ ]` item into the appropriate section of `plan.md`, or drop it with an explicit justification, and tick it off. **Guard:** if the file does not exist, that is not an error — continue.

**What you MAY WRITE INTO:**
- **`tasks-input-from-prev.md`** — for **04**: a preparatory step, an ordering constraint, a concrete command or an environment prerequisite that is needed at the task breakdown but does not fit into the sections of `plan.md`.
- **`validate-input-from-prev.md`** — for **07**: a runtime prerequisite and an operational note that only becomes relevant at the validation (e.g. "a VPN is needed before starting the stack", "the mock server has to be stopped before running Sonar, because it conflicts on the port").

<!-- INCLUDE:shared/input-from-prev.md -->

---
---

## Processing the cycle design input (CD1)

`specs/cycle-NN-<cycle-name>/cycle-design-input.md` is the **user's own, free-form cycle description** (created by 01 as an empty template, filled in by the user — optionally). 02 has already lifted its **behavioral** part into `spec.md`; what remains for **you** is the **technical and procedural content** that does not belong into the spec but is a first-rate input for the plan:

- concrete commands, scripts, build/deploy steps;
- hosts, ports, base URLs, namespaces, image names (coordinates);
- naming existing components, libraries, model implementations;
- a technology constraint, a performance limit, an integration condition;
- the implementation direction or ordering preference sketched by the user.

**Rules:**

1. **Do not rewrite the file, and do not tick anything off in it.** This is the user's document, not a handover file (`*-input-from-prev.md`).
2. **The rule of self-containedness (the most important rule of the phase) applies here too.** The data coming from the design input **has to be copied into `plan.md`** — referencing it ("see the design input") is **forbidden**: 04 and the `test-runner` do not read this file.
3. **Reference resolution is mandatory.** If the design input **references** a script, an existing test, a config or an external API, resolve it from the source (the concrete command, URL, complete payload) according to the *"Reference resolution (dereferencing)"* section — do not reproduce the sketchy phrasing of the user.
4. **In case of a conflict, ask.** If the design input contradicts `spec.md` (which the user has already approved), **do not decide on your own**: add it as a `Qnn` question to `plan-questions.md`. If the design input contains a **behavioral** expectation that is missing from the spec, that is the branch of the *spec critique* — report that it belongs into 02.
5. **Pass on what is not the business of the plan**, do not drop it: a task-level preparatory step → `tasks-input-from-prev.md`, a runtime/operational note → `validate-input-from-prev.md` (IP1).
6. **Tell the user** in a concise list where each item of the design input went (a plan section / tasks-input / validate-input / a new `Qnn` / directed back into 02).

**Guard:** if the file does not exist or contains only the template, that is not an error — say so in one sentence, and continue.

---
---

## Context loading rules

- Read the `spec.md` of the cycle.
- If `cycle-design-input.md` exists: read it (CD1) — the user's own cycle description, its technical part is an input of the plan.
- If `plan-questions.md` exists: read it.
> **Which register knows what (TC1/c):** the **report artifacts, their path base and the report-generating commands** live in the `## <sec:cv_test_reporting>` section of the project `conventions.md` — **that is what the TR3 gate of 07 reads**. `specs/test-conventions.md` is the register of the **recipes and coordinates**. If the cycle changes the report structure or the report command, `conventions.md` has to be updated (GC1) — updating `test-conventions.md` is not a substitute for it.

- **Recurring test expectations and recipes (TC1) — `specs/test-conventions.md`:** if it exists, read it **in its entirety** (block 0 and all three sections). This is the register maintained by `08-doc-sync`: **block 0 = the Coordinates** (environments, URLs/ports, health endpoints, test users, clients, scopes, parameters, env pointers — **every concrete value in one place**), section 1 = the recipe register (component coordinates, startup, example calls, build/deploy commands), section 2 = the local (mock-based) tests required in every round, section 3 = the integration/E2E tests required in every round. **Guard:** if the file does not exist (an early cycle), do not stop and do not create it — say so in one sentence, and put the Q01 question of `plan-questions.md` based on the existing testing infrastructure.

  > **🔴 `plan.md` is SELF-CONTAINED (TC1/a — mandatory).** The `run-tests.py` script reads the **machine-readable run table** of `plan.md`, and the `test-runner` subagent (the fallback) does **not read** `test-conventions.md` — only the `<sec:testing_strategy>` and `<sec:regression_impact>` sections of `plan.md`. Therefore **every testing task has to be lifted into `plan.md` completely**, supplemented with **all** the belonging data of block 0 and section 1: test users and their passwords, URLs, ports, namespace/pod, image name, registry target, parameters, **example calls (`curl`)**, build/push/restart commands, prerequisites and the run order.
  > - **A plain reference is NOT enough** (`"see test-conventions.md R03"` on its own is forbidden) — reference `test-conventions.md` only as **provenance** next to the content lifted over (e.g. "_(source: test-conventions.md R03)_").
  > - **A placeholder is FORBIDDEN** (`<here comes the password>`, `<TODO URL>`) — if a datum is missing or outdated, that is a `plan-questions.md` question, not a placeholder.
  > - **It is not an automatic run:** **only what** is really needed in this cycle is carried over from the register. This lifting is itself the human control point — `plan.md` is the single truth of the run.
  > - **An outdated item:** if the data of a recipe does not match reality, or its `<field:f_last_run>` marker is old, **ask about it** in `plan-questions.md`. Do **not write** `test-conventions.md` — fixing it is the business of `08-doc-sync` (TC4); the cycle takes the correct data agreed with the user into the plan.
  > - **A recipe with a `<status:scope_shared_remote>` scope** (the register marks it so): before lifting it, **you must ask** about it in `plan-questions.md` — in a shared dev/test environment an image push or a pod restart affects the work of others as well.
- **Identifying the source files (the business of the plan, not of the spec):** the `<sec:referenced_files>` section of the spec contains **documentation/specification material only** (README, OpenAPI, schema, example payload) — **not** source files (`.ts`, `.tsx`, `.js`, `package.json`, etc.). The source files to be modified/affected are **identified by phase 03 on its own**, based on the `<sec:components_behavior>` section of the spec. For this, start the `researcher` subagent (`agents/researcher.md`), which returns the list of the affected source files (path + location + character) — the raw file content does not burden the main context. Read directly only the parts of the source files identified this way that really are relevant.
- **Documentation/specification files referenced in the spec:** if `spec.md` references external descriptors in the `<sec:referenced_files>` (a JSON schema, an OpenAPI descriptor, an example payload), read these as well before producing the plan.
- **The documentation of external dependencies:** if the cycle introduces or makes use of an external dependency (e.g. Keycloak, an external API, a messaging broker), request the relevant documentation or MCP servers from the user before starting the plan. Review it, and decide whether sufficient and relevant information is available. If not, add it as an open question to `plan-questions.md`.
- If you have to understand a large or complex file, call the same `researcher` subagent (`agents/researcher.md`, Mode B) for the research. The subagent returns only the summary — the raw file content does not get into the main context.
- **Documentation Reconnaissance:** before starting the design, the agent must find every description in the whole project (e.g. the `docs/` folder, README.md files, diagrams) that may be affected by the changes (e.g. it references the endpoint, variable or process to be modified). Since this search may involve reading many files, **it is done by the `researcher` subagent (`agents/researcher.md`)** — the same agent that identifies the source files. The subagent carries out the searches, analyzes the hits, and returns exclusively the list of the documents to be modified and a short summary of the parts to be replaced, thereby protecting the cleanliness of the main context. The primary goal is that every description and diagram in the project be up to date.
- **The `plan.md` files of earlier cycles — the main rule:** do not read them. **The exceptions, when it IS MANDATORY to look (TP3/a):**
  1. the spec marks an explicit dependency on an earlier cycle; **or**
  2. **running the tests of the cycle requires an environment prerequisite that was built up by an earlier cycle** (a custom plugin/SPI, a mock server, seed data, a container stack, a test user, a token-obtaining helper), **and the commands belonging to it are not in `specs/test-conventions.md`**. Into the register it is `08-doc-sync` that promotes — whatever has not got in yet **exists only in the `plan.md` of the given cycle**.
  - **How:** do not read the whole file into the main context — start the `researcher` subagent (`agents/researcher.md`, Mode B) with the concrete question (e.g. "from the plan of `cycle-24-...` return **verbatim** the Keycloak SPI build/push/rollout commands, the image name, the namespace and the rollback step"), **asking for literal values**. You **copy** the commands obtained into this plan according to the rule of *Reference resolution*, with a `_(source: cycle-NN plan.md)_` provenance.
  - **How much:** only the recipe really needed for the execution — not the plan, the decisions or the scope of the earlier cycle.
  - **If it contradicts reality** (the command looks outdated, the image tag is different): a `plan-questions.md` question, do not guess.
  - **Tell the user** in one line which earlier cycle plan you lifted what from — this is a signal for `08-doc-sync` as well that the item is to be promoted into `test-conventions.md`.

---

<!-- INCLUDE:shared/artifact-voice.md -->

---
---

## Plan structure

<!-- INCLUDE:shared/plan-section-ids.md -->

\`\`\`md
# Cycle NN: <title> — Plan

**<field:f_status>:** \`<status:draft>\` | \`<status:open_questions>\` | \`<status:ready_for_test_plan>\` | \`<status:ready_for_tasks>\`
**<field:f_gate_code>:** _<the result of the mechanical gate of the code plan at closing — e.g. `analyze-gate-check --plan-code-only — PASS, 0 Must Fix (2026-09-01)`>_
**<field:f_gate>:** _<the result of the gate of the full plan — this is written by `03b-write-test-plan`, do not fill it in>_

## <sec:goal_and_approach>

_One paragraph: what we realize and how. It does not repeat the objective of the spec, but summarizes the technical approach._

## <sec:affected_components>

_A list: which file / component changes, what kind of change it is (a new file, an extension, a modification)._

## <sec:environment_coords> (KO1)

_**A mandatory section — the basis of the self-containedness of `plan.md`.** **Every concrete value** needed for the development and the testing of the cycle goes here, resolved: component URLs and ports, start commands, example REST calls, test and API users with passwords, every parameter. This is the cycle-level counterpart of **block 0** of `specs/test-conventions.md` — but not a reference to it, rather the values actually used in the cycle **verbatim**._

_**Rules:** a placeholder is **forbidden** (`<TODO>`, `<here comes the password>`, `TBD`) — whatever is missing or outdated is a `plan-questions.md` question, not a placeholder. An empty cell is **forbidden**; where something is not applicable to this cycle, a `—` goes. A reference does not substitute for the data ("see the spec", "the usual test user"). The secret rule (TC5): a dev-scoped test user, a mock credential and a local password go here **with a concrete value**; a cluster, registry, VPN, IAM and production credential **never** — instead a pointer (where it is stored, who issues it)._

**<field:f_target_env>:** <the target environment of the cycle: `local`, `remote`, `local + remote`, …>

_**Mandatory field (EV1).** It has to be stated WHICH environment this cycle is about — because a green test on its own does not prove WHERE it was green. A live cycle deployed to dev, but its tests ran against a local target (a script named `…:dev-e2e` had `baseURL: "http://127.0.0.1:5178"` in its config): everything went green, and so it never came to light that the component deployed to dev did not even start. This field binds the test target to the intent of the cycle, and the gate of `05` measures the `<field:f_environment>` column of the run table and the `TS-NN` calls against it (EV1–EV5)._

### <sec:components_endpoints>

| Component | Repo path / image | Base URL | Port(s) | Health endpoint | Startup (verbatim command) | Shutdown / cleanup |
|---|---|---|---|---|---|---|
| `tmp-service` | `services/tmp/`, `registry.example/tmp:v1-<UTC>` | `http://localhost:8081` | 8081 (HTTP), 5005 (debug) | `GET /actuator/health` → `200` | `docker compose -f docker-compose.e2e.yml up -d tmp-service` | `docker compose -f docker-compose.e2e.yml down -v` |

### <sec:rest_calls_examples>

_From every call that the development or the test uses: **the verb, the full URL, the headers, the concrete request body with every mandatory field, the expected response, the field to be extracted from the response**. Obtaining the token (the user and the S2S separately, if both are needed) is mandatory here too — it is not enough that "there is a login helper"._

| Call | Verb + endpoint | Headers | Request body | Expected response | Extracted value |
|---|---|---|---|---|---|
| user token | `POST http://localhost:9090/api/v13/login/token` | `Content-Type: application/json` | `{"userId":"test-user","password":"Test123!"}` | `200`, `{"token":"…"}` | `$JWE` ← `.token` |

\`\`\`bash
# user token
JWE=$(curl -sS -X POST 'http://localhost:9090/api/v13/login/token' \
  -H 'Content-Type: application/json' \
  -d '{"userId":"test-user","password":"Test123!"}' | jq -r '.token')

# cache init
curl -sS -X POST 'http://localhost:8081/init-hash' \
  -H "Authorization: Bearer $JWE" -H 'Content-Type: application/json' \
  -d '{"productType":"LOAN","channelType":"MOBILBANK"}'
\`\`\`

### <sec:test_api_users>

| User / client | Password / credential | Where it is valid | Role / scope / client-id | What we use it for |
|---|---|---|---|---|
| `test-user` | `Test123!` | the local mock login (`http://localhost:9090`) | `retail` | the E2E login |
| `tmp-s2s` | pointer: `Vault kv/dev/tmp` (TC5 — the secret does not go into the plan) | the dev cluster | `client_credentials`, scope `tmp.write` | the S2S token |

### <sec:other_parameters>

| Parameter | Value | Where / when it is needed |
|---|---|---|
| `appId` / `buildId` / `processName` | `42` / `7` / `loan-onboarding` | the path parameters of the process-starting call |

### <sec:network_access_prereqs>

_A VPN, a proxy, `oc login` / a kubeconfig, a namespace, a registry login: what is needed, in what order, and a **pointer** to the credential (TC5) — never the secret._

## <sec:planned_changes>

_Per file, at the function/class level: what changes and why. Not code, but intent. Every entry contains:_
- _the **<field:f_purpose>** line: what we want to achieve and why (WY1 — see below, mandatory)_
- _the path of the affected file_
- _the name of the affected or to-be-created function/class_
- _the interface change, if there is one (a new parameter, a new return type, a new export)_
- _for a new file, the names of the main exported units_
- _for an existing file, the location of the affected code fragment (e.g. `src/file.ts:14–25`) as a navigation target, if you read the source file_

> **The path format (RP1) — this is where it is most frequently got wrong.** A code and file reference is **relative to the root of the repo**: `src/token-store.ts`, `apps/web/src/index.ts:42`. **Not** relative to the folder of `plan.md` (`../../src/...`), **not** absolute (`/home/...`, `C:\...`), and **not** a `file://` link. The reason: the commands run in the root of the repo, and the gate of `05-analyze` also resolves the anchors there — a reference of the `../../` form cannot be resolved there. The **document links** (e.g. `[spec.md](./spec.md)`), however, are relative to the own directory of the file, so that they are clickable. The detailed rule is in the quality check of the phase.

> **🔴 Every `[P-…]` entry states its PURPOSE — mandatory (WY1).** "What we rewrite" on its own does not say **what we want to achieve** — while the implementer, the `reviewer` and the fixer of the 07 loop decide exactly from this whether a different solution is also acceptable, and when the change is done. Therefore every `### [P-…]` section carries this line next to the affected files:
>
> ```md
> **<field:f_purpose>:** <the behaviour that will be true AFTER the change> — because <the current gap or defect it eliminates>. (<sec:definition_of_done>: DoD-03)
> ```
>
> - **The purpose follows from the spec, it is not your idea (the mirror of SC1):** the `DoD-NN` (or spec requirement) named at the end of the sentence is the same one that stands for this `[P-…]` in the `<sec:reverse_coverage>` table. If you cannot name the source, the entry has no place in the plan: either it is a `plan-questions.md` question, or it goes back to the 02.
> - **What is NOT a purpose:** repeating the change in other words ("we introduce the `getS2SToken()` method"), the file name ("we update the config"), empty generality ("we improve the quality", "we refactor"). The purpose states the **behaviour** the system produces afterwards, and the **trouble** it eliminates.
> - **One paragraph, not one word.** If the entry bundles several files and several steps, the purpose summarizes what they add up to together.

**A calibration sample for one entry** (copy the density, not the topic):

```md
### [P-30-02] Storing the S2S machine token in the Redis session store
- **Affected files:** `src/services/session-store-service.ts`, `src/types/session.ts:41-58`
- **<field:f_purpose>:** the `tmp-s2s` machine token moves onto a Redis key read by all pods (`{namespace}_tmp:tokens:s2s`), so that out of three instances running in parallel **one** asks the Keycloak for a new token, not all three — because today every instance keeps it in its own memory, and every cold start produces as many `client_credentials` calls as there are pods running. (<sec:definition_of_done>: DoD-01, DoD-04)
- **Change details:**
  1. …
```

_If this level of detail is not available from the spec, read the relevant part of the affected source file._

**An interface design principle — a deep module:** when designing a new module or function, aim for it to hide a lot of functionality behind a simple interface. The calling side does not have to know about the internal logic — it only sees the input and the output. Avoid a shallow module: if a function does little logic but requires a complex call, that pushes the complexity onto the caller instead of hiding it.

> **🔴 `docs-generated/` MUST NOT get here (DS4).** The files of the `docs-generated/` folder (`system-overview.md`, `architecture.md`, `CHANGELOG.md`, `design-drift.md`, the folder index) are the **exclusive property of 08-doc-sync** — neither the plan plans them, nor the implementation writes them. **Only** the source code, the configuration and the tests go here. (Updating the generated documents happens at the end of the cycle, in phase 08, automatically.)
>
> **The component README — the boundary is the existence of the component (not the file type):**
> - **The first `README.md` of a new component** → **it belongs here** (part of building the component; the doc-sync can only reconcile what already exists).
> - **Updating the README of an existing component** (env variable, port, startup, connections changed) → it does **NOT** belong here: that is done by `08-doc-sync`. Do not plan a modification for it and do not generate a task for it.

**A new component design principle:** every new component mentioned in the spec — regardless of the tech stack — gets its own entry in the planned changes. This contains: the project structure, the build system (e.g. Maven, Gradle, npm, go.mod), the communication mode (REST, messaging, gRPC, etc.) and the deployment mechanism (JAR, Docker image, binary, etc.). A component cannot be considered planned if only the mock/simulation appears in the plan while the spec prescribes a real implementation.

For a new component the `README.md` is a mandatory deliverable — add it explicitly among the planned changes (`<component-root>/README.md`, a new file). Its content: what it does, the startup, the port, debugging, the logs, the connections.

## <sec:new_dependencies>

_New packages and external dependencies, if the cycle requires them — regardless of the tech stack (npm, Maven, pip, etc.). If there is no new dependency, write it out explicitly: "There is no new dependency."_

## <sec:config_build_changes>

_New env vars, docker modifications, configuration file changes. If there are none, write it out explicitly: "There is no configuration change."_

_**The configuration lifecycle (KF1) — a mandatory row for every new/modified parameter.** Introducing a parameter does not end at reading the code: **in every run mode** it has to reach the running process, otherwise the test runs with a different configuration than the development._

| Parameter | Where it comes from (default / file / env) | Local run | Unit/integration test | Container / compose | Dev deploy | If it is missing |
|---|---|---|---|---|---|---|
| `TMP_CONFIG_PATH` | env, default `config/tmp-config.yaml` | `.env` | a test fixture env | `docker-compose.yml` `environment:` + a volume mount | the deployment env | fail-fast at startup |

_The last column is mandatory: **fail-fast** or a **concrete default** — "it is not defined" is not acceptable. If a cell would stay empty, that is a **missing plan**: either you fill it in, or it becomes a `plan-questions.md` question._

## <sec:schema_artifacts>

_The formal schemas and API descriptors introduced or modified by the cycle. <field:f_status>: `<status:draft>` | `<status:review_required>` | `<status:reviewed>`_

| Artifact | Type | File | Status |
|---|---|---|---|
| ... | OpenAPI / Redis key map / Avro / DB schema | `docs/...` | `<status:review_required>` |


## <sec:reverse_coverage> — the scope gate (SC1, a mandatory table)

_Every plan capability **has to be traceable back** to the spec. List the substantive capabilities/sections of the plan, and for each of them the spec source:_

| Plan capability / section | Spec source (a requirement or `DoD-NN`) |
|---|---|
| _`[P-REDIS]` Redis sentinel/cluster + TLS_ | _DoD-02_ |

_**The first column should bear the `[P-…]` identifier of the section** (not an ordinal, not a bare title), and the second the `DoD-NN` identifier where that is the spec source. The coverage chain of the mechanical gate of `05-analyze` (`DoD-NN → [P-…] → task`) runs on these two columns: if the row contains only free text (`§3.2 …`), the chain cannot be closed mechanically, and the gate gives an `S3` finding. If the section belonging to a capability has no `[P-…]` identifier, that is the absence of PID1 — give it an ID first._

_**If there is no spec source for a row, there are three possibilities — there is no fourth:**_
1. _**back into 02:** the capability is needed → ask for a DoD item for it (tell the user what is missing; you do not write the spec yourself);_
2. _**<sec:out_of_scope>:** in the `<sec:goal_and_approach>` section of the plan you state explicitly that it will not be produced in this cycle, and you **take it out of the plan**;_
3. _**a `plan-questions.md` question,** if you cannot decide._

_A capability in the plan without a spec source that "seems useful" is **forbidden**: it would be developed without a test and an acceptance criterion._

_(The sections from `<sec:testing_strategy>` to `<sec:verification_strategy>` are written by the
`03b-write-test-plan` phase — do not start them here.)_

## <sec:risks_and_decisions>

_What can go wrong? Where is there a choice, and which one do we choose, why?_
\`\`\`

---

## Handling the Schema artifacts

> **Attention — two different status systems:** the **document status** of `plan.md` (`<status:draft>` | `<status:open_questions>` | `<status:ready_for_test_plan>`) is in the header of the file. The **artifact status** here (`<status:draft>` | `<status:review_required>` | `<status:reviewed>`) applies exclusively to the individual rows of the `<sec:schema_artifacts>` table. Do not mix the two: the code plan cannot be closed to `<status:ready_for_test_plan>` even so, if any artifact is `<status:review_required>`.

### When an artifact is needed

| The cycle touches... | The artifact needed |
|---|---|
| A new REST endpoint or a breaking change | An OpenAPI YAML (`docs/<name>-openapi.yaml`) |
| A minor modification of an existing endpoint | Updating the existing OpenAPI, a separate review is not needed |
| A new cache key pattern | A Redis key map (`docs/<name>-redis-keys.md`): the key, the value structure, the TTL |
| A new message type (messaging) | An Avro / JSON Schema (`docs/<name>-schema.avsc` or `.json`) |
| A new DB entity or a schema change | A DB schema / migration file (`docs/<name>-db-schema.md`) |

### The workflow

1. **Identification**: does the artifact appear in the `<sec:referenced_files>` section of the spec?
   - **Yes** (the user gave it): read it, check it critically against the `<sec:components_behavior>` section of the spec. If you find a deficiency, state it precisely. If it is in order: `<status:reviewed>`.
   - **No**: generate it into the `docs/` folder, add it to the table with a `<status:review_required>` status.
   - **If there is not enough information in the spec for generating the artifact** (e.g. the type of a field, a TTL, a message schema is missing): **do not invent it** — add it as a `[ ] Qnn` question to `plan-questions.md`, and clarify it with the user before you generate the artifact.

2. **Asking for a review**: for every `<status:review_required>` artifact, ask for a review explicitly:
   > *"Please review the generated `docs/X.yaml` file. If it is suitable, write: 'ok'. If you request a modification, state what should change."*

3. **Iteration**: if the user gives feedback, modify the artifact and ask for a review again. If it is 'ok': the status → `<status:reviewed>`.

4. **Blocking**: the code plan cannot get a `<status:ready_for_test_plan>` status while there is a `<status:review_required>` artifact in the table.

---
---

## Validation cycles

### After `<sec:planned_changes>`

- Does the modification of some file cover every requirement of the spec? Go through the `<sec:components_behavior>` section of the spec line by line.
- Is the project structure, the build system and the deployment mechanism planned for every new component mentioned in the spec (regardless of the tech stack)? The mock is not enough — if the spec prescribes a real implementation, that has to appear as well.
- Can every new service/component reach everything it needs (imports, config fields, DI parameters)?
- For the modifications of existing files: does the standard flow stay untouched? (backward compatibility)
- Is the type of the DI override planned for every new testable component (service, route, app)?
- **The README of an existing component: do NOT plan it.** If the cycle changes the configuration of an existing component (env vars, startup parameters, external connections), updating `README.md` is the business of **`08-doc-sync`** — do not add it among the `<sec:planned_changes>`. **Exception:** if the cycle creates a **new component**, its first `README.md` belongs here (it is part of building it).

If the answer to any point is no, extend the planned changes, then continue.
---

## Spec critique — during the writing of the plan

The plan phase is the first step where the requirements of the spec collide with real code and the existing architecture. This is the point where spec deficiencies surface. **Be actively critical of the spec** — do not fill the deficiencies in yourself.

**CHECK — go through EVERY affected component, and answer the three questions for each of them (not only in your head — if the answer to any of them is "no/missing", that is a spec deficiency):**
1. Does the spec define every relevant error case at the given component? (e.g. what happens if service X returns a 500?)
2. Are the boundaries unambiguous (what is in scope, what is out of scope) at this component?
3. Is there a behavior that the spec assumes but does not describe?
4. **Am I planning a capability at this component for which there is NO spec sentence and `DoD-NN`?** (a scope overreach — SC1). If yes: you either ask for a DoD from 02, or you take it out of the plan and write it into the `<sec:out_of_scope>`. On the basis of "we will need it anyway" it **cannot be planned in**.

If you find a deficiency or a contradiction, **do not decide it yourself** — direct it back into the spec phase (see below).

### The spec is TOO technical — coordinate feedback (the mirror of KX)

The critique applies not only to the **absence** but to the **overreach** as well. Go through the spec, and mark it if there is content in it that belongs into the **plan** — typically:

- an absolute URL with a host, `host:port`, a concrete `localhost:NNNN`;
- an image name and tag, a registry, a namespace, a pod, a deployment name;
- a build/deploy command or an installation step sequence (`oc`, `kubectl`, `mvn`, `docker`/`podman`, `npm run`) — especially if it appears in the `<sec:test_specification>` section of the spec under the heading of a "test", while it is a **runbook**;
- a source or artifact file path, an `.env` file name and the values read from it;
- the name of a test tool or framework, a test file path, a mocking-level decision.

**What to do with it — this is your advantage, not a problem:**

1. **Use it:** these are exactly the data that `plan.md` needs. Lift them into the appropriate section (`<sec:e2e_infrastructure>`, `<sec:testing_strategy>`, `<sec:config_build_changes>`) — **verbatim, with the full value**.
2. **Tell the user** in a concise list what it is that stayed in the spec but belongs into the plan. **Do not rewrite `spec.md` yourself** — that is under the management of phase 02. If the user asks for the spec to be cleaned up as well, that means returning into 02 (the `KX` rule of 02 does it).
3. **Do not ask about it** just because it was in the wrong place in the spec: if the datum is unambiguous, take it over. **Ask** (`plan-questions.md`) if the datum looks **outdated or uncertain** (e.g. a different host appears in two places), or if it describes an operation with a `<status:scope_shared_remote>` scope (a cluster restart, an image push) — an approval is needed there.

> **🔴 Why this is critical: `plan.md` has to be SELF-CONTAINED.** The `test-runner` subagent reads **exclusively** the `<sec:testing_strategy>` and `<sec:regression_impact>` sections of `plan.md` — **not `spec.md`**, and not `test-conventions.md` either. Therefore a URL, a port, a test user or a command left in the spec (or anywhere else) **will never run**; it only gives the false impression of being documented. **Every piece of data needed for the execution has to be physically in `plan.md`**, with its full value, without a placeholder and without a "see the spec" kind of reference. If a datum is elsewhere, it is your job to bring it over.

> **"Do not invent it yourself" — where is the boundary?** You may choose a default without asking if the decision is **purely technical** and does not affect the behavior of the spec (e.g. the name of an internal helper function, the internal representation of a data structure). It is **mandatory to ask** (`plan-questions.md`) if the decision influences **observable behavior** (e.g. what HTTP code an error branch returns, what the retry policy is, which field goes into the response) — that has to be recorded by the spec, not by you.

---
---

## Stopping rules

**Add every question that comes up — for whatever reason — immediately to `plan-questions.md` with the next sequential number (`Q01`, `Q02`, ...) in `- [ ]` status, before you put it to the user.** This applies to all the cases listed below, and to any other uncertainty as well. The question only goes in front of the user after it got into the list.

**If there is a question with a `[ ]` status in `plan-questions.md`**, do not start writing plan sections — put one to the user first, wait for the answer, mark it with `[x]`, then continue.

If any of the following holds while writing the plan, **STOP — stop and tell the user** (do not decide the missing/contradictory part yourself):

- **A complex or uncertain containerization**: if running, configuring or networking any component in the test environment in a container is not trivial or is uncertain. → Do not try to figure out the ports/configurations on your own; add the question to the `plan-questions.md` file, stop, and initiate joint design with the user.

- **An implementation decision point**: several equal-rank technical approaches exist and the choice is not unambiguous based on the spec. → Put **one** question, wait for the answer, then continue the plan.

- **A spec deficiency**: the spec does not define a necessary behavior, error case or boundary. → **Do not fill it in yourself.** Add it as a `[ ] Qnn` question to `plan-questions.md`, and tell the user precisely what is missing — we have to return to the spec phase and update `spec.md` there. After the spec is updated and the `<status:ready_for_plan>` status is restored, the plan phase can be started again.

- **A spec contradiction / outdated code**: two points of the spec, or the spec and the existing code, contradict each other. (For example: if the specification asks for the modification of a component that is outdated, out of use, or contradicts the reality of the current code, stop, and ask about it in `plan-questions.md`, do not plan a needless modification with notes!) → State both sides, and wait for the decision of the user. Do not choose.

- **A risk requires a user decision to resolve**: a risk cannot be handled on your own based on the spec. → One question, an answer, continuation.

- **Any point of the closing gate (TP2-code) is `[ ]`**: an environment coordinate is missing (URL, port, the password of a test user, a startup command), a `[P-…]` entry has no `<field:f_purpose>` line, a plan capability has no spec source in the `<sec:reverse_coverage>` table, or a cell of `<sec:config_lifecycle>` is unfilled. → **Do not close the code plan.** Add what is missing, then run every point of the gate again. This is not "a refinement in 03b": `03b` writes the `TA1` data sheets and the `TS-NN` calls from your literal values, and its entry gate (D5) sends it back here anyway.

In every case put only **one** question at a time — wait for the answer, tick the question off (`- [x] Qnn → [the decision]`), then move on to the next one.

---

---

<!-- INCLUDE:shared/quality-check-plan-code.md -->

## Status handling

- When starting the plan: \`<status:draft>\`
- If a question gets into `plan-questions.md`: \`<status:open_questions>\`
- If every question is `[x]`, every **code-side** section is filled in, every schema artifact is `<status:reviewed>`, the quality check (+ the Constitution Check) passed, **and the user has explicitly confirmed it**: \`<status:ready_for_test_plan>\`

> **🔴 `<status:ready_for_test_plan>` is NOT the end of the plan phase of the cycle.** `plan.md` is not done until `03b-write-test-plan` has closed it at `<status:ready_for_tasks>`. Starting `04` with this status is an error — the entry gate of `04` (EG1) catches it too, because the full `--plan-only` gate fails on the missing test sections.

> **Done lifecycle:** after `<status:ready_for_tasks>`, `plan.md` moves to `<status:done>` status at the end of the cycle — when the PASS of the validate (07) closes the cycle. This transition is done by 07, not here.


### The mechanical gate before closing (M)

The **code-side half of the deterministic gate of `05-analyze` runs here as well** — before the closing (`tasks.md` and the test sections do not exist yet, therefore `--plan-code-only`):

<!-- INCLUDE:shared/python-cmd.md -->

```bash
python3 <platform-scripts-mappa>/analyze-gate-check.py specs/cycle-NN-<cycle-name> --plan-code-only
```

**What it covers in this mode:** the format and uniqueness of the `[P-…]` identifiers (P1), the presence of the code-side mandatory plan tables — `<sec:reverse_coverage>` and `<sec:environment_coords>` (S1) —, the empty cells of `<sec:config_lifecycle>` (C4), the placeholders and empty cells of `<sec:environment_coords>` (C6, KO1), the presence of the `**<field:f_target_env>:**` field (EV1), the purpose of every `[P-…]` entry (WY1), the gate configuration moving along (GC1), the `path:line` anchors of the plan (A2/A2b), the path format (R1), the hard floor of the artifact voice (A3) and the `DoD-NN` identifiers in the spec (D1/D2).

> **The test-side checks deliberately do NOT run in this mode** (`TS1–TS8`, `TA1`, `TI1`, `PH1`, `TS7`, the coverage chain and the presence of `<sec:machine_run_table>`) — those are measured by the closing of `03b` with the full `--plan-only` mode. A `DoD-NN` proven exclusively by a test **cannot yet** be covered here; measuring these now would make the gate give a false FAIL.

- **`0`** → the closing can continue.
- **`1`** → **no status change.** Fix the `target phase: 03` items **now**, then run the gate again; route the `target phase: 02` items back to 02 according to *Spec critique* / *Stopping rules* — you do not write the spec yourself.
- **`2`** → a usage error → report it, do not guess.

> **Why here (M):** these defects used to surface in the first round of `05-analyze`, two phases later — there they needed a fixer subagent and an analyzer round. Here it is one script run and one targeted fix.

**🔴 The result of the gate is EVIDENCE, not a memory (GS2/a).** After a `0` its trace goes into two places, and both are mandatory:

1. into the header of `plan.md`, next to the status, on one line:

   ```md
   **<field:f_gate_code>:** analyze-gate-check --plan-code-only — PASS, 0 Must Fix (YYYY-MM-DD)
   ```

2. into your **phase-closing answer**, verbatim the summary line of the gate (`ANALYZE-GATE: …`).

**Write the stamp only after an actual run returning `0`** — the entry gate of the next phase (`03b`) **runs this very gate again** (D5), so an untrue stamp comes out there immediately, and `03b` sends it back here.


If the user confirms:
- Set the status of `plan.md` to `<status:ready_for_test_plan>`.
- **Before the status change run every item of the *Closing gate (TP2-code)***, and print the ticked list in your answer. With any `[ ]` there is no status change.
- **Before the status change the *Mechanical gate* (see above) returned `0` as well.**
- **Commit immediately** according to the *Phase-closing commit* below (`<FÁZIS-TAG>` = `03a-code-plan`). Confirmation → writing the status → commit: this is one single sequence of steps, do not interrupt it.

<!-- INCLUDE:shared/phase-commit.md -->

In the block above, the value of `<FÁZIS-TAG>` in this phase is: **`03a-code-plan`**, and the closing status is: **`<status:ready_for_test_plan>`**.

If the status is \`<status:ready_for_test_plan>\` **but the phase-closing commit is missing** (a VCS project, `git log -1 --oneline` does not show the `cycle-NN: 03a-code-plan` commit) — commit first, and only then close the phase.

If the status is \`<status:ready_for_test_plan>\` (and the commit is there), stop. **Do not start the test sections, and do not even create `tasks.md`** (PE1, see the "Phase boundary" section of the *Phase-closing commit* block): the test plan is the job of the `03b-write-test-plan` skill, and writing tasks is the job of `04-write-tasks`, from a fresh context. This holds even if the to-do list of a context summary/checkpoint lists running `/bs-write-test-plan` or `/bs-write-tasks` — that summary records the past, it is not an order for this round. Tell the user the next step and the starting command of the phase, for example:
<!-- INCLUDE:lang/03a-write-code-plan.md#zaro-uzenet -->
