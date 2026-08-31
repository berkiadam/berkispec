---
phase: 03
name: bs-write-plan
description: "berkispec - 03. Use it when the spec.md of the cycle is 'Ready for planning' (Phase 03), to work out the detailed technical implementation plan (code base analysis, the researcher subagent if needed). It creates 'plan.md' ('Ready for tasks') + 'plan-questions.md'."
prerequisites:
  - "specs/cycle-NN-<name>/spec.md status: <status:ready_for_plan>"
output:
  - "specs/cycle-NN-<name>/plan.md status: <status:ready_for_tasks>"
  - "specs/cycle-NN-<name>/plan-questions.md"
  - "specs/cycle-NN-<name>/tasks-input-from-prev.md and/or validate-input-from-prev.md (only if there is information to hand over, IP1)"
prev: bs-write-spec
next: bs-write-tasks
subagents:
  - "agents/researcher.md"
scripts:
  - "scripts/analyze-gate-check.py"
shared:
  - "shared/input-from-prev.md"
  - "shared/artifact-voice.md"
  - "shared/phase-commit.md"
  - "shared/quality-check-plan.md"
  - "shared/fix-mode-plan.md"
---
# 03 — Writing the plan
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

We develop software in spec driven development. The development is split into cycles. Every cycle is an independently developable, independently testable subunit of the complete implementation.

This is **phase 3 (0–9)** of the process: 0-init · 1-cycles · 2-spec · **3-plan ←** · 4-tasks · 5-analyze · 6-implement · 7-validate · 8-doc-sync · 9-review.

---

## Cheat sheet

| Section | In one sentence |
|---|---|
| Prerequisite | `spec.md` = `<status:ready_for_plan>`, `conventions.md` exists, a clean working tree. |
| Open questions | Every question into `plan-questions.md`; **the mandatory first question: the E2E test strategy**. |
| Context | The spec + the documentation; the source files are identified by the `researcher` subagent (D2=A). |
| Plan structure | <sec:planned_changes>, the test strategy, the execution order, the verification strategy. |
| The test tool | Reference `conventions.md`, do not repeat the concrete tool name. |
| Test recipes | Lifted over from `specs/test-conventions.md` **completely, self-containedly** (TC1/a) — a reference is not enough, the recipe has to be **copied in physically**. |
| Section ID | A stable `[P-…]` identifier in the title of every executable plan section (PID1) — `tasks.md` references this, not an ordinal. An ID once issued never changes. |
| The scope gate | A spec source (a requirement/`DoD-NN`) for every plan capability — the `<sec:reverse_coverage>` table (SC1), with the `[P-…]` identifier of the section in the first column; whatever has none goes back into 02 or into `<sec:out_of_scope>`. |
| Environment preparation | The prerequisites of the test (obtaining a token, starting the stack + a health check, a custom component build/deploy/rollback, a seed) **as verbatim commands** in the plan (TP3); whatever was built up in an earlier cycle and is not in the register, you bring over from there (TP3/a). |
| Lifting the spec tests over | **Every** test case and `DoD-NN` item of the spec maps to a plan test case (TP1), with the mandatory `<sec:spec_coverage>` table — the detail cannot be postponed to 04 or to the implementation. |
| Phase handover | `plan-input-from-prev.md` read and closed; the information that does not belong here into `tasks-`/`validate-input-from-prev.md` (IP1). |
| The design input | `cycle-design-input.md` (the user's own cycle description) is **read automatically** — its technical/procedural content goes into the plan; you do not rewrite the file (CD1). |
| <sec:environment_coords> | A mandatory `<sec:environment_coords>` (KO1) section: component URLs/ports, start commands, example REST calls, test/API users with passwords, every parameter — with concrete values, without a placeholder and without an empty cell. |
| **Self-containedness** | `plan.md` contains **everything** that is needed for the development/testing — 04 and the `test-runner` read **only this**, not the spec. |
| The gate configuration | If the cycle changes something that a deterministic gate reads from `conventions.md` (report artifacts/path base, Sonar, test commands, ports, the merge strategy), updating `conventions.md` is **part of the cycle**: plan it, and there should be a task for it (GC1). |
| Paths | A code and file reference is **relative to the root of the repo** (`src/app.ts:42`), a document link is relative to the own directory of the file (`./spec.md`); an absolute path and `file://` are forbidden (RP1). |
| No truncation | The **elaborated** artifacts of the spec (OpenAPI, a complete payload, an error matrix, a multi-step test scenario) come over **verbatim and complete** (KX3) — the direction is extension and refinement, not merging. |
| Reference resolution | An input referencing a script/a test/an API **has to be resolved**: the concrete command, URL, payload goes into the plan, not the hint. |
| Test steps | Every integration/E2E test is spelled out **step by step** (verb, endpoint, header, body, expected response) — "following the pattern of cycle-XX" is forbidden. |
| Validation cycles | A targeted check after every large section, before you move on. |
| Spec critique | An active checklist for every component; a **deficiency** → back into phase 02, an **overreach** (a coordinate in the spec) → lifted over into the plan (the mirror of KX). |
| Closing | The quality check + the **Closing gate (TP2, written out ticked)** + the Constitution Check (SK4) + the **mechanical gate** (`analyze-gate-check.py --plan-only`, M) + the user confirmation → `<status:ready_for_tasks>`, a commit. |

---

## What you have to do

**If a `plan.md` already exists in the `specs/cycle-NN-<cycle-name>/` folder:** read it, and run the quality check on it (see below). If you find a deficiency or a problem — a spec deviation, a missing component plan, an incomplete test specification, etc. — set the status back to `<status:draft>`, state precisely what the problem is, and fix it according to the iteration rules.

**If `plan.md` does not exist yet:** create it in the `specs/cycle-NN-<cycle-name>/` folder according to the structure below.

**Do not repeat the content of the spec.** The goal of the plan is to design the technical realization — reference the spec, do not copy it over.

> **🔴 The scope — do not over-generalize it!** This rule (and its pair: "reference `conventions.md`, do not repeat the tool name") applies **exclusively to the justification and to the behavior description**: to the *why*, to the business context, to the acceptance criteria. **It never applies to the data needed for the execution.** The guiding principle in one sentence:
>
> **Reference the DECISION — write out the EXECUTION.**
>
> An example: which test framework the project uses is a **decision** → you reference `conventions.md`, you do not repeat it. But **with which command, on which file, in which environment** the test runs **in this cycle** is **execution** → you write it into the plan concretely. If you are uncertain which side something falls on, ask the question: *"can the downstream phase (04/06/07) obtain this information from somewhere else?"* If not — then it has to go into the plan.

### 🔴 `plan.md` is SELF-CONTAINED — this is the most important rule of this phase

**The plan is the last document that still sees the spec.** What happens from here downwards works **exclusively from the plan**:

| Consumer | What it reads | What it does NOT see |
|---|---|---|
| `04-write-tasks` | **only `plan.md`** (the skill explicitly forbids re-reading the spec and the source files) | the spec, the code base |
| `06-implement` | `plan.md` + `tasks.md`; it navigates back here from the tasks | the spec |
| `test-runner` (07/09) | the `<sec:testing_strategy>` and `<sec:regression_impact>` sections of `plan.md` | the spec, `test-conventions.md` |

From this follows the rule that **cannot be overridden**: **every piece of information that is needed for the development, the testing or the verification has to be physically in `plan.md`.** Nothing essential may be left out on the grounds that "it is in the spec anyway", "it can be seen in the code", "`build.sh` contains it" or "it was said in the conversation". Whatever is not in the plan **does not exist** for the downstream phases — and it will not run, it only gives the false impression of being documented.

**Concretely, the following have to be in the plan** (whatever is applicable to the given cycle):

- the full path of the affected files; the names of the functions, classes, modules to be created/modified;
- **function signatures, interfaces, types**, the exact form of the interface change;
- data structures and **payloads with concrete fields** (an example request/response, not just a list of field names);
- error branches: condition → HTTP status + errorCode + response body;
- configuration: the **name AND the value** of the env variable, where it is set;
- the coordinates of an external integration: URL, port, realm/client/scope, test user, an example `curl` call;
- runnable **commands verbatim** (build, deploy, startup, running the tests, verification);
- the execution order and the prerequisites; the migration and rollback scenario, if there is a schema change.

> **A self-test (apply it before closing):** *"If somebody gets only `plan.md` and `tasks.md` — without the spec, without knowledge of the code base and without this conversation —, can they develop and test the cycle?"* If they would have to **ask back or guess** at any point, the plan is incomplete. The question is not whether you understand it; it is whether a reader who knows less than you can carry it out.

**Forbidden phrasings in the plan:** "see the spec", "in the usual way", "to the appropriate endpoint", "run `build.sh`", "with the parameters used in the earlier cycle", **"following the pattern of cycle-XX" / "as in the existing test file" / "according to the sequence diagram of the spec"**, `<here comes …>`, `TODO`. Each of them means that the concrete detail **is missing** — add it, or if you do not know it, add it as a question to `plan-questions.md`.

**Do not produce a task list or an implementation.** That is the task of the next step.

**Do not plan anything that is not in the spec.** The scope of the plan is exactly the scope of the spec — it does not widen it, it does not narrow it. If, while writing the plan, you feel that something should be added that is missing from the spec, that is a spec deficiency — report it and ask for the spec to be updated, do not fill it in yourself in the plan.

**If something is missing or contradictory in the spec, report it — but do not complete the spec in your head. The plan works from the spec only.**

> **Is the task too simple for a full cycle?** If, while writing the plan, it turns out that the cycle is actually trivial — there is no real design decision, essentially it is only **putting a configuration together, a simpler script or a smaller fix** —, then the full `plan → tasks → analyze → … → review` flow is oversized. Tell the User, and **recommend the simplified flow**: *"This cycle looks simple enough for the full process; `/bs-quick-flow` (spec → task → implementation) may be faster for it. Shall we switch to that, or stay with the full cycle?"* The decision belongs to the User — do not switch arbitrarily, and do not skip phases within the full flow.

---

## <field:f_prerequisite>

0. **Identifying the cycle:** if the user gave a cycle/file, use that; otherwise offer the most recent `specs/cycle-*` folder for confirmation — <!-- INCLUDE:lang/common.md#ciklus-beazonositas --> — and wait for the answer before moving on.

1. **`conventions.md` existence check:** read `conventions.md` in the root of the project. If it does not exist, STOP — they should return to phase `00`.
2. **Working-tree check (only with VCS):** run `git status --short`. If there are uncommitted changes, list them, and ask in one round whether I should commit or continue. (In a No-VCS project it is skipped.)
3. Read the status of \`spec.md\`. **If the status is not \`<status:ready_for_plan>\`, do not start writing a plan.** Tell the user that the spec is not closed yet, and that they should return to the `02` spec phase.

4. **Reading the cycle design input (CD1) — automatic:** if `specs/cycle-NN-<cycle-name>/cycle-design-input.md` exists, read it **in every run, without a separate prompt**. This was written by the user in free form about the cycle; 02 has already lifted its behavioral part into the spec, but its **technical, procedural and coordinate content** (commands, hosts/ports, existing components, build/deploy steps, performance and integration constraints) is **directly the input of the plan**. For the rules of processing it, see the *"Processing the cycle design input (CD1)"* section. **Guard:** if the file does not exist or contains only the template text, say so in one sentence and continue — it is not an error and not a reason to stop.

_A note: if the spec is `<status:ready_for_plan>`, `specs/roadmap.md` is implicitly closed — the `02` spec phase has already checked it. A separate roadmap check is not needed._

---

## Continuing after an interrupted run

If the plan phase is interrupted and continues in a new session:

```
1. Read the current state of plan-questions.md (if it exists).
   → Go through the questions in order: you may skip the [x]s, clarify the
     [ ]s one by one. If a new question comes up while reviewing an [x],
     add it to the end of the list with a new Qnn number.

2. Only write/continue plan sections if every question is [x].

3. If plan.md looks coherent but the status is not <status:ready_for_tasks>:
   run the quality check + the Constitution Check, then ask for a confirmation.
```

The current state of `plan.md` and `plan-questions.md` + this prompt is enough for the restart.

---

## Handling open questions

`plan-questions.md` is the question register of the plan phase. Every question that comes up, every spec deficiency, decision point and contradiction goes here — not only into the dialogue. This is what makes the process traceable and continuable after an interruption.

**Basic rule: we never delete from the list. A closed question is only marked with `[x]` — its text and the decision stay.**

### plan-questions.md structure

If it does not exist yet, create it in the `specs/cycle-NN-<cycle-name>/` folder:

```md
<!-- INCLUDE:lang/03-write-plan.md#plan-questions-struktura -->
```

Always append a new question to the end of the list, with the next sequential `Qnn` number.

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

4. **Closing:** if every section is done, every question is closed and the quality check passed, put the question to the user: <!-- INCLUDE:lang/03-write-plan.md#statusz-megerosites --> — Do not switch the status before the confirmation. **At the end of the answer, place the direct, clickable link of `plan.md`.**

5. **A restart in a new context:** if the plan phase is interrupted and continues in a new session, the first step is reading `plan-questions.md` (if it exists). Go through all the questions in order — you may skip the `[x]`s, clarify the `[ ]`s one by one according to the above. If a new question comes up while reviewing an already closed question (`[x]`), add it to the end of the list with a new `Qnn` number, and clarify it before you move on.

---

## Reference resolution (dereferencing) — the level of the input is NOT the level of the plan

> **The most frequent error in this phase:** the agent **reproduces the abstraction level of the input**. If the spec or `plan-input-from-prev.md` says *"an image build and a push to the registry by running `build.sh`"*, then this sentence gets into the plan — **without the concrete commands, the registry host, the image tag and the parameters**. The same way: if the input lists the **parameter names** of a call, the agent settles for that, and the **actual JSON payload** is missing from the plan (e.g. a mandatory `"channelType": "MOBILBANK"` field) that the existing test code contains.

**The rule:** the abstraction level of the input does not determine the abstraction level of the plan. **If an input item references something instead of containing it, the reference HAS TO BE RESOLVED from the source** — before you write it into the plan.

**What has to be resolved (not an exhaustive list — the pattern is the point):**

| The input says this | This has to be extracted and written into the plan | The source |
|---|---|---|
| "run `build.sh`" / "the usual deploy process" | the actual commands verbatim, the registry host, the image name and tag, the env variables | the script itself, the `Dockerfile`, the CI configuration |
| "we obtain a token with the login helper endpoint" | the full URL, the method, the **concrete JSON payload with every mandatory field**, the headers, an example `curl` | the existing test/helper code (`test/`), the OpenAPI descriptor |
| "following the pattern of the existing integration test" | the actual call chain, the fixtures, the seed data, the expected responses | the referenced test file |
| "with the tool according to `conventions.md`" | the **decision** stays a reference, but the **command to be run** concretely | `conventions.md` + `package.json`/`Makefile` |
| "the compose file brings up the stack" | the services, the ports, the health check, the start order | the compose file |

**How, token-efficiently:**

- **A small, targeted source** (one script, one env template, one compose file): read it **directly**.
- **A large or scattered source** (a code base search for a keyword, reviewing many test files): start the `researcher` subagent (`agents/researcher.md`) — **but explicitly ask for literal values in the request**: *"return the commands / the URL / the complete JSON payload verbatim, not a summary"*. The researcher compresses by default; here **precision takes priority over brevity**.
- **Follow the chain:** if the script references another script or an `.env` file, go on until you get a concrete value. **Exception:** a real secret (a cluster, registry, VPN, IAM credential) — there **stop and write a pointer** (TC5), not the value.
- **Do not copy in the whole REPO FILE:** from a source file/script lift over only the part needed for the execution (commands, coordinates, schema, parameters) — the plan is a plan, not an archive. **This rule applies to the source files of the repo, NOT to the elaborated artifacts coming from the spec** (OpenAPI, payload, error matrix, test scenario): those have to be carried over in their entirety, see `KX3`.
- **Do not paraphrase:** carry the command and the JSON over **verbatim**. A "roughly like this" payload is worse than nothing, because it creates false confidence.
- **Mark the source:** next to the value lifted over `_(source: keycloak/docker/build.sh)_` — this way it turns out later if the source moved away from the copy recorded in the plan.

**When this has to be run:** for every input item (the spec, `plan-input-from-prev.md`, `test-conventions.md`, the roadmap) that **references a procedure, a script, a configuration file, an external API or an existing test**. This is **especially** true in an early cycle, when `specs/test-conventions.md` does not exist yet: then the only source of the recipe data is the **existing code and tests** — find them, do not rely on the text of the input.

> **Closing the loop:** what you discover this way (commands, coordinates, payload schemas) goes into the `<sec:environment_coords>` (KO1) section — and it is exactly what has to get into `specs/test-conventions.md` at the end of the cycle through `08-doc-sync` — the concrete coordinates into block 0, the recipes into section 1 (TC3/TC13) — so that the next cycle does not discover it again.

---

<!-- INCLUDE:shared/conventions-change.md -->

---

## Lifting over an elaborated spec artifact — verbatim, without truncation (KX3)

> **This is the OPPOSITE case of `Reference resolution`, and the other most frequent error in this phase.** The previous section is about the input being **too abstract** (it references something instead of containing it) — then it has to be resolved. This section is about the input being **already fully elaborated**: `spec.md` contains a finished OpenAPI descriptor, a complete request/response payload, an error matrix or a ten-step test scenario with expected results. In that case the agent tends to **"abstract it into a plan"**: it merges the steps, replaces the payload with a list of field names, substitutes the descriptor with a "the spec defines it in detail" sentence. **This is data loss, not planning.**

**The rule (the mirror of the `KX2` rule of 02):** if the spec (or `cycle-design-input.md`, `*-input-from-prev.md`, the plan of an earlier cycle) gives an artifact **already elaborated**, it has to be carried over into the plan **verbatim, in its entirety**. **The direction is extension and refinement — merging and omission are not.**

**What it necessarily applies to (the nature of the list is the point, not its length):**

| The artifact in the spec | How it goes into the plan |
|---|---|
| an OpenAPI / JSON Schema / Avro / proto / GraphQL fragment | **as an unchanged block**, with every field, type, `required` and example |
| a request/response payload | **as complete JSON**, with every mandatory and optional field — not as a list of field names |
| an error matrix (status + `errorCode` + body) | **as a complete table**, with every row — not as "the error handling is according to the spec" |
| a multi-step test scenario (①…②…③, with expected results) | **every step, every intermediate check and every expected result** — the steps must not be merged |
| a cache key schema / DB DDL / a migration script | verbatim, with the complete key and field list |
| a configuration template (`.env`, a compose fragment, YAML) | verbatim, with every key |

**What you may — and have to — do:**
- replace the **symbolic coordinates with concrete values** (`{PUBLIC_BASE_URL}` → the actual URL) — this is the rule of `Reference resolution`, therefore an **extension**;
- **add** what is the level of the plan: a test case identifier (`TC-XX-01`), the test level, the run command, the fixture, the environment preparation;
- **spell out** an incomplete step (a missing intermediate check, an expected result that was not given);
- **reorder**, if the order is not executable (report a non-trivial reordering).

**What is forbidden:**
- ❌ **merging** steps or replacing them with a summary of the "the process runs through" kind;
- ❌ replacing a payload with a **list of field names**, a table with **prose**;
- ❌ **referencing** it: *"see the Test specification section of `spec.md`"*, *"the spec describes it in detail"*, *"the other cases are similar"*, *"…etc."*;
- ❌ **leaving out an example** on the grounds that "the schema is enough on its own".

**A self-check (measurable):** the corresponding section of the plan **cannot be shorter** than its source section in the spec. If it did become shorter, that has to be **proven**, it is not self-evident: name what moved elsewhere (e.g. into a separate `<sec:schema_artifacts>` entry), or add it. The mechanical gate of `05-analyze` also measures this mechanically (the `V1`/`V2` check): it looks for the content of the code blocks of the spec in the plan, and compares the extent of the two test sections.

> **The three rules that are easy to misread and therefore tend to conflict — the resolution:**
> - *"The plan is a plan, not an archive"* (see `Reference resolution`) applies to the **source files of the repo**: from a 2000-line script only the part needed for the execution is needed. It **does not apply to the contract artifacts coming from the spec** — those belong to the content of the plan in their entirety.
> - *"The abstraction level of the spec has to be resolved, not reproduced"* is true of the **abstraction level**, not of the **content**: the symbolic coordinate has to be made concrete, but the level of detail has to be preserved (indeed increased).
> - The **duplication category** of `05-analyze` (1.) does **not** apply to the verbatim lifting of the spec → the plan: that is not redundancy but the mandatory self-containedness. Duplication is when the same decision appears twice **within** the plan, or when tasks.md describes the test case steps of the plan again.

---

## Handover between phases (`*-input-from-prev.md`) — IP1

**What you READ:** if `specs/cycle-NN-<cycle-name>/plan-input-from-prev.md` exists, read it at the beginning of the phase. It contains the technical and implementation details that surfaced in phase 01/02 (affected components, existing solutions, technology constraints) that did not fit into the spec. Either build every `[ ]` item into the appropriate section of `plan.md`, or drop it with an explicit justification, and tick it off. **Guard:** if the file does not exist, that is not an error — continue.

**What you MAY WRITE INTO:**
- **`tasks-input-from-prev.md`** — for **04**: a preparatory step, an ordering constraint, a concrete command or an environment prerequisite that is needed at the task breakdown but does not fit into the sections of `plan.md`.
- **`validate-input-from-prev.md`** — for **07**: a runtime prerequisite and an operational note that only becomes relevant at the validation (e.g. "a VPN is needed before starting the stack", "the mock server has to be stopped before running Sonar, because it conflicts on the port").

<!-- INCLUDE:shared/input-from-prev.md -->

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

## The plan structure

### 🔴 Stable section identifiers (PID1) — tasks.md references these

**You write a stable identifier into the title of every executable plan section**, directly after the `###`:

```md
### [P-CONFIG] The configuration system and the config files
### [P-REDIS] Extending the Redis connection
### [P-E2E-UI] The Playwright UI E2E
```

| Rule | Mechanics |
|---|---|
| **Format** | `[P-<NAME>]` — uppercase, hyphenated, 1–2 words, referring to the content of the section. An ordinal is **not** part of it (`[P-3-1]` is forbidden). |
| **Who gets an ID** | **Only an executable plan section:** the subsections of the `<sec:planned_changes>` and of the `<sec:test_specification>` / `<sec:testing_strategy>` — where it is described **what has to be done**. |
| **Who does NOT** | `<sec:goal_and_approach>`, `<sec:affected_components>` (an inventory), `<sec:environment_coords>` (an inventory), `<sec:execution_order>`, `<sec:risks>`, `<sec:new_dependencies>`, the IP1 sections. These **cannot be** the targets of a task reference (E). |
| **Uniqueness** | An ID may appear once in the plan. |
| **Stability** | An ID once issued **never changes** — not even if the ordinal of the section shifts, you rename it, or the chapter moves elsewhere. The ID of a deleted section **cannot be reused**. A new section (e.g. inserted by the analyze loop) gets a **new ID**. |
| **Why** | `tasks.md` references an ID instead of an ordinal. If a fix inserts a `§3.10`, the ordinals shift, and the tasks **silently point at the wrong section** — the ID rules this out. |

_You may use an ordinal for the readability of the title (`### 3.1 [P-CONFIG] …`), but the **referencing key is always the ID**._

\`\`\`md
# Cycle NN: <title> — Plan

**<field:f_status>:** \`<status:draft>\` | \`<status:open_questions>\` | \`<status:ready_for_tasks>\`

## <sec:goal_and_approach>

_One paragraph: what we realize and how. It does not repeat the objective of the spec, but summarizes the technical approach._

## <sec:affected_components>

_A list: which file / component changes, what kind of change it is (a new file, an extension, a modification)._

## <sec:environment_coords> (KO1)

_**A mandatory section — the basis of the self-containedness of `plan.md`.** **Every concrete value** needed for the development and the testing of the cycle goes here, resolved: component URLs and ports, start commands, example REST calls, test and API users with passwords, every parameter. This is the cycle-level counterpart of **block 0** of `specs/test-conventions.md` — but not a reference to it, rather the values actually used in the cycle **verbatim**._

_**Rules:** a placeholder is **forbidden** (`<TODO>`, `<here comes the password>`, `TBD`) — whatever is missing or outdated is a `plan-questions.md` question, not a placeholder. An empty cell is **forbidden**; where something is not applicable to this cycle, a `—` goes. A reference does not substitute for the data ("see the spec", "the usual test user"). The secret rule (TC5): a dev-scoped test user, a mock credential and a local password go here **with a concrete value**; a cluster, registry, VPN, IAM and production credential **never** — instead a pointer (where it is stored, who issues it)._

**<field:f_target_env>:** <the target environment of the cycle: `local`, `dev`, `local + dev`, …>

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
- _the path of the affected file_
- _the name of the affected or to-be-created function/class_
- _the interface change, if there is one (a new parameter, a new return type, a new export)_
- _for a new file, the names of the main exported units_
- _for an existing file, the location of the affected code fragment (e.g. `src/file.ts:14–25`) as a navigation target, if you read the source file_

> **The path format (RP1) — this is where it is most frequently got wrong.** A code and file reference is **relative to the root of the repo**: `src/token-store.ts`, `apps/web/src/index.ts:42`. **Not** relative to the folder of `plan.md` (`../../src/...`), **not** absolute (`/home/...`, `C:\...`), and **not** a `file://` link. The reason: the commands run in the root of the repo, and the gate of `05-analyze` also resolves the anchors there — a reference of the `../../` form cannot be resolved there. The **document links** (e.g. `[spec.md](./spec.md)`), however, are relative to the own directory of the file, so that they are clickable. The detailed rule is in the quality check of the phase.

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

## <sec:testing_strategy>

_What kinds of tests are needed (unit / integration / e2e)? Which existing test file is modified, which new file comes into existence?_

_**The recurring expectations lifted over (TC1) — mandatory if `specs/test-conventions.md` exists:** the items of sections 2 and 3 of the register that are needed in this cycle, **self-containedly** (with the recipe data belonging to them, not with a plain reference). Next to every item lifted over, write the provenance: `_(source: test-conventions.md L01)_`. If you corrected the data of an item in `plan-questions.md`, the **corrected** data goes here._

### <sec:plan_test_scenarios> — **mandatory (TS1)**

> **🔴 Why it is mandatory:** the prose above is about the test **types**, this section is about the test **content**. `plan.md` is self-contained (TC1/a): both the `test-runner` and `bs-manual-test-plan` work **exclusively** from it, and a failed test of `07` must also be reproducible by hand from it. Therefore every test case has to be worked out as an **executable scenario** — not "the login flow will be tested", but step by step: what we call, with which concrete value, and exactly what we expect back.
>
> **The yardstick (self-test):** *"A person who did not take part in the design can carry out the test reading only this section, and can decide whether it succeeded."* If they would have to figure out anything — which URL, which user, what the correct answer is — the scenario is incomplete.
>
> **The test cases of the spec must not be merged (KX3).** If the `<sec:test_specification>` section of the spec describes six cases, six scenarios stand here — expanding and refining is allowed, merging and dropping is not.

One block per scenario, in exactly this form:

#### TS-01 — <the name of the scenario>  (DoD-02, DoD-05)

**<field:f_what_we_test>:** <what this scenario verifies — the behavior it runs for, in one sentence>
**<field:f_prerequisite>:** <the state it starts from: a stack that is up, seed, a logged-in user, the result of an earlier `TS-NN`>

| # | Step | Call | Expected result |
|---|---|---|---|
| 1 | <what we do> | `<a literally runnable call>` | `<a concrete, checkable response>` |

**<field:f_cleanup>:** <what has to be stopped or restored afterwards>

**Rules for filling it in:**
- **`DoD-NN` in the header — mandatory and bidirectional (TS5).** Every scenario names which DoD points it proves, and **every `DoD-NN` must have at least one scenario**. The gate measures both directions.
- **Call column — literally runnable.** For REST, a full `curl`: verb, full URL with the port, headers, the concrete request body. A non-REST test belongs here in the same form: a UI step (what we click, what we type), a CLI command, a DB query. **A reference is not a call** — "see the `<sec:e2e_infrastructure>` section" is not runnable.
- **Expected result column — concrete and checkable.** The status code **and** the identifiable part of the response (field name, value, payload fragment, the text of a UI element). "Runs successfully" / "returns an error" / "gives the expected result" is **forbidden**: it cannot be decided. The hard floor of the gate (TS3): at least one backticked value or a number.
- **Test users, passwords, URLs, ports, identifiers: literally.** The values of `<sec:environment_coords>` (KO1) have to be **written in here**, not referenced — a placeholder is forbidden (TS4), and missing data is a `plan-questions.md` question. Credentials according to the secret rule (TC5): a dev-scope test user yes, a cluster/registry/IAM credential never.
- **The data flow must be traceable.** If the next step uses the output of a step, write out **which field into which variable** (`the `response.initHash` field of the answer → `$INIT_HASH``).
- **Numbering:** from `TS-01`, without gaps and uniquely (TS6). When fixing, do **not** renumber the existing identifiers — new ones go to the end of the list.
- **Bootstrapping does not belong here:** starting the stack, obtaining the token and the deploy live in the `<sec:e2e_infrastructure>` section (TP3); here the `<field:f_prerequisite>` line **references** it.

### <sec:machine_run_table> (run-tests.py) — **mandatory (TP4)**

> **🔴 Why it is mandatory:** the prose above speaks to a human, this table speaks to the **`run-tests.py`** script. If it exists, 07-validate runs the tests **with a script**, and the raw test log never gets into an LLM context — this is the largest token item of this phase. If it is missing, 07 falls back to the more expensive `test-runner` subagent. The table does not substitute for the prose: **the same commands**, in a machine-readable form.

| Category | Type | Prerequisite | Command | Result file | Format | Cleanup | <field:f_environment> |
|---|---|---|---|---|---|---|---|
| unit | gyors | — | `<the verbatim command, with a machine reporter>` | `junit.xml` | junit | — | local |
| integration | gyors | — | `<command>` | `<file>` | junit | — | local |
| e2e | nehez | `<the reachability probe of the target; starting the stack>` | `<the command with the target host>` | `<file>` | junit | `<tear-down>` | `<the name of the target environment>` |

**Rules for filling it in:**
- **The type:** `gyors` (unit/integration/typecheck — it runs in the VD10 light round as well) or `nehez` (E2E/regression — only in a full round). _(These are the values of the `--type` flag of the script, they are not translated.)_
- **Prerequisite / Cleanup:** several commands may be listed with a `;`, matching the bootstrapping steps of the `## <sec:e2e_infrastructure>` section **verbatim**. The cleanup runs even if the run blew up.
- **The command:** preferably with a **machine reporter** (`--reporter=junit`, `--junitxml=…`, `-Dsurefire.reportFormat`) — this way the counts and the failed test names can be extracted precisely, and are not estimated from a regex.
- **The result file:** a path relative to the repo; the script copies it into the round folder as evidence.
- **Placeholders — there are two, with two different bases (TR5/c). Do not mix them up:**
  - `{round}` → the **full** round folder relative to the repo root (`specs/cycle-NN-<cycle-name>/test-report/validate/round-02`). Write this where the command starts from the repo root: `--outputFile={round}/junit.xml`, `--alluredir={round}/e2e/allure-results`.
  - `{phase}` → the **phase folder** relative to `test-report/` (`validate/round-02`). Write this where the report command of `conventions.md` expects the `<phase-dir>` placeholder or a `REPORT_PHASE_DIR`-style environment variable: `REPORT_PHASE_DIR={phase} npm run test:pw`.
  - **Writing `test-report/` before `{round}` is forbidden** (`…/test-report/{round}`) — `{round}` already contains it. The resulting double prefix builds a recursive `test-report/specs/…` report tree; `run-tests.py` checks this before the run and stops with `exit 3`.
- **The format:** `junit` (recommended) or `text` (it counts from the stdout with a regex — weaker evidence).
- **🔴 <field:f_environment> — mandatory in every row (EV2–EV5).** `local` or the name of the target environment goes here. If it is not `local`:
  - the **`Command` cell must literally contain the target host** (through an env variable or a switch, e.g. `PLAYWRIGHT_BASE_URL=https://app.dev.example npx playwright test`) — **the target must not hide in a config file** (EV3). A script named `test:playwright:dev-e2e` may perfectly well have `localhost` in its config: **the name of the command is not evidence, the address is**;
  - a **reachability probe to the same host is mandatory in the `Prerequisite` cell** (`curl -fsS https://app.dev.example/health`) — `run-tests.py` runs the prerequisite, and on its failure the category is FAIL, so **a deployment that never even started cannot be ticked green** (EV4);
  - `localhost` / `127.0.0.1` in the command or in the prerequisite is **forbidden** (EV5) — `run-tests.py` then stops with `exit 4`, without running anything.
- **An empty cell:** `—`.
- If a category **deliberately does not exist** in this project, do not add it to the table, and describe in the prose why.

> **⚠ Platform-dependent commands (Windows).** `run-tests.py` runs the commands with the default shell of the system: Linux/macOS → `/bin/sh`, **Windows → `cmd.exe`**. What may differ because of this: the single quote (`'…'`) is **not** a string delimiter in cmd, the environment variable is `%VAR%` instead of `$VAR`, while the `&&`/`||` work on both. If the project runs on mixed platforms, write a command into the table that is correct on both (typically an `npm run …` / `mvn …` / `pytest …` call) — put the shell-specific steps (starting the stack, the health poll) into a script, and call that. The `;` separator of the `<field:f_prerequisite>`/`Cleanup` column is split and run as separate commands by the **script**, so that is not shell syntax: it is platform independent.

### <sec:e2e_infrastructure>

_(Filling it in is mandatory — based on the level agreed in `plan-questions.md`.)_

_**The place of the recipe data (TC1/a):** **all** the data needed for the execution lifted over from section 1 of `specs/test-conventions.md` goes into this section, verbatim: component coordinates (repo path, image name, registry target, namespace/pod), URLs and ports, the health endpoint, **test users and their passwords**, the scope/client-id and other parameters, **example calls (`curl`)**, build/push/restart commands, prerequisites and the order of the steps. **A reference does not substitute for the data, and a placeholder must not be used** — the `test-runner` sees only this file. Write a credential in here as well only according to the secret rule of the register (TC5): a dev-scoped test user yes, a cluster/registry/VPN/IAM/token credential never — a pointer goes for that._

> **🔴 ENVIRONMENT PREPARATION (bootstrapping) — mandatory content (TP3).** The test **does not begin at the call chain**, but at the environment being ready to run and there being a valid authentication. Every such prerequisite has to be written in here **as a verbatim, runnable command** — the `test-runner` assumes an empty machine, and it can infer nothing. Item by item:
>
> | Prerequisite | What has to be written into the plan |
> |---|---|
> | **Authentication / obtaining a token** | The **complete call** for obtaining the token: the verb, the endpoint, the headers, the request body with the **concrete test user**, the field to be extracted from the response, and which variable it goes into (`$JWE`, `$ACCESS_TOKEN`). Separately for the **user** and for the **S2S/technical** token, if both are needed. With a mock login helper as well: its **call**, not the mere existence of it. The expiry/re-request, if the length of the run justifies it. |
> | **Starting the stack** | The concrete start command (an env-starting script / compose up), the **health check** (which URL has to return `200` by when), the **waiting condition** (not a `sleep`, but a poll), and the stop/cleanup command. |
> | **A custom component build + deploy** (a plugin, an SPI, a custom image, a patched container) | The **complete process command by command**: the location of the source, the build (`mvn`/`npm`/`docker build`), the image name **with a unique tag**, the push to the registry, the replacement of the deployment/pod, the check that it came up (`rollout status` + a health/version endpoint), and the **rollback** (what the original identifier is, how it can be read out, with what it can be restored). In a shared environment, all three conditions of the `[!CAUTION]` block above are needed for this as well. |
> | **Seed / initial state** | The schema, the test data, a realm import, creating a client/scope — with the concrete command or file. |
> | **Network access** | Whether a VPN/proxy/`oc login`/kubeconfig is needed — with a pointer to the credential (TC5), never with the secret. |
> | **The order** | The **execution order** of the above and how they build on each other, so that it can be carried over one to one into the `<sec:execution_order>` section. |
>
> **A self-test for this section:** *"On a fresh machine, after cloning the repo, reading exclusively this plan, can I run the tests — with the token obtained, the stack brought up, the custom component deployed — without inventing anything or looking anything up elsewhere?"* If not, the section is incomplete. Whatever is missing and is not in `test-conventions.md` either has to be **brought over from the plan of the earlier cycle** (TP3/a) or asked from the user.

> [!IMPORTANT]
> **The strict containerization rule:** for the sake of the consistency and machine independence of the test environment, every background service and component participating in the E2E and integration tests must be run in a container (e.g. Docker/Podman). Relying on native services running locally on the host is forbidden (except for the framework/browser running the test itself).

> [!IMPORTANT]
> **Full automation and a clean state (Clean Slate):** the containers have to be designed and started so that running the test configures them into the appropriate state fully automatically, from zero (from 0):
> - *Examples:* with a database, the schema has to be brought up and the test data has to be loaded automatically when the container starts (seeding). With Keycloak (or any external Identity Provider), the realm configuration has to be loaded automatically when the container starts, and the necessary clients and test users have to be created (e.g. through an exported realm import JSON or the admin API).
> - **Cleaning up the resources (Cleanup):** the plan has to contain explicitly how the containers and the temporary resources are stopped and completely deleted after the tests run (e.g. the global teardown hook of the test framework, `trap 'cleanup' EXIT`, compose down), so that no running container or network garbage is left behind.

> [!CAUTION]
> **A destructive operation carried out in a shared (non-disposable) environment — approval, an immutable tag, a rollback.** If the plan modifies a **shared** environment — a deployment/pod replacement in a shared cluster or namespace, an image push to a common registry, a seed/deletion in a shared database, overwriting a configuration —, then **all three** are mandatory in the plan:
> 1. **Approval:** the operation is marked as having a `<status:scope_shared_remote>` scope, and it is recorded in `plan-questions.md` that the user approved it (it may affect the work of colleagues).
> 2. **An immutable identifier:** the artifact issued **must not overwrite an existing identifier** (e.g. we must not push the same image tag again) — the version has to be bumped or a unique (build-identified) tag has to be used. **After an overwritten tag there is nothing to restore to.**
> 3. **A rollback plan:** described concretely, what the original state is (**with the command for reading out** the current image/version/config), and with which command it can be restored if the check fails.
> 4. **State persistence:** if the steps build on **each other's state** (a saved original identifier, a generated unique tag), that state **must not stay in a shell variable**. The execution happens step by step in separate shells, so `VAR=...` / `export VAR=...` **evaporates** by the next step, and the rollback would run with an empty parameter. Prescribe that the state goes into a **file** (e.g. `.rollback-state`), and that the later steps read it from there — or merge the dependent commands into a single step.
>
> If any of these is missing, the operation cannot be planned — add it as a question to `plan-questions.md`.

> [!CAUTION]
> **Handling complex configurations:** if the containerization, the network access (e.g. localhost vs. the container network) or the initial data loading of a component to be tested is complex or ambiguous, the agent **must stop and ask for the help of the user** (with a question added to `plan-questions.md`), so that they shape the test environment together.

**An important rule for starting the E2E environment:** a platform-independent environment-starting script always has to be planned and used (with the tool given by `conventions.md` — e.g. a Python env-starting script) that brings up the necessary container stack or local services, and then the test framework (e.g. the global setup of the browser E2E tool given in `conventions.md`) starts the environment through it. It must never happen that a test fails because of the absence of a manual environment start.

- **The E2E level:** a real containerized stack / partial mocking / full mocking
- **The running services:** which components run as real containers (in the E2E compose file given by `conventions.md`)
- **The mocking justification:** if there is a mocked service, why it is not real — a documented decision
- **Frontend tests:** if there is a web component, the browser E2E tool given by `conventions.md`
- **Backend tests:** the backend test tool given by `conventions.md`
- **The E2E compose file:** the planned services, ports, health checks, start order (with the name given by `conventions.md`)

### <sec:regression_impact>

_If the cycle modifies existing code: an explicit list of the affected existing test files and E2E scripts, and a short justification of why they are affected. This list will be the input of the regression update tasks of the tasks phase and of the regression run of the validate phase._

_If there is no regression impact, write it out explicitly: "There is no regression impact."_

_**Derivation from the register (TC1):** if `specs/test-conventions.md` exists, do **not** invent this table from scratch — compare the components/files modified by the cycle with the section 2/3 items of the register, and every affected item should get into the table (with the ID of the item in the `Why it is affected` column). The "it must not break" kind of items that do not go over into `spec.md` because they are not the goal of the cycle get in here as well. The recipe data needed for the run are contained by the `<sec:e2e_infrastructure>` section above._

| Test file / E2E script | Why it is affected |
|---|---|
| `test/unit/...` | ... |
| `test/integration/cycle-XX-....sh` | ... |
| `test/e2e/auth-login.spec.ts` | test-conventions I01 — the modified middleware runs on this flow |

## <sec:test_specification>

_A summary of the testing approach: what we mock, what we run in a real container, at which levels we test — before you list the concrete cases._

### <sec:spec_coverage> (a mandatory table)

_Every case of the `<sec:test_specification>` section of the spec and every item of the `<sec:definition_of_done>` maps to **at least one** plan test case. Without the table the plan cannot be closed._

| Spec source | Plan test case(s) | Level |
|---|---|---|
| _the name of the spec test case / a `test-conventions` item ID / `DoD-NN`_ | `TC-XX-01`, `TC-XX-E-01` | unit / integration / E2E |

_**The `Level` column is not a free choice:** the nature of the behavior decides it. **If the DoD/spec describes behavior observable on a user interface** (a button, an element appearing, a screen state), then a **browser E2E is mandatory** — an API-level E2E does not substitute for it. If there is no browser E2E tool in the project, that is a `plan-questions.md` question, not a silent downgrade._

### <sec:reverse_coverage> — the scope gate (SC1, a mandatory table)

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

_If a case from the spec **cannot** be tested in this cycle, the row stays, with a justification in the "Plan test case" column (e.g. "cannot be automated — a manual `[CHECK]` in step 7 of the `<sec:execution_order>`"). **It cannot be left empty or omitted.**_

### Lifecycle

| Level | When we write it | When we run it | What it blocks |
|---|---|---|---|
| Unit | BEFORE the implementation | every commit | the RED→GREEN cycle |
| Integration | AFTER the implementation | with the service stack up | closing the cycle |
| E2E | AFTER the implementation | with the full stack up | closing the cycle |

### <sec:unit_tests>

_Isolated tests: business logic, functions, classes isolated from their dependencies. Every external component (database, network, external service) has to be mocked — extremely fast, deterministic. A happy path AND negative tests (a wrong input, a missing parameter, an authorization error, a timeout) are mandatory for every component. One subsection per component. A tabular format: TC-ID, Scenario (what the situation is), Input (what arrives), Expected output (the HTTP status + the errorCode where the error matrix of the spec defines it + the key response fields)._

#### `<test file path>` (new / an extension)

| TC-ID | Scenario | Input | Expected output |
|---|---|---|---|
| TC-XX-01 | ... | ... | ... |

> **🔴 THE TEST CASES OF THE SPEC HAVE TO BE BROUGHT OVER (TP1) — it is not the business of `tasks.md` and not of the implementer.** The cases described in the `<sec:test_specification>` section of the spec and in the `<sec:definition_of_done>` are **not** "too detailed for the plan": they belong exactly here, because the `test-runner` reads **exclusively `plan.md`** — not the spec, not `test-conventions.md`, not `tasks.md`. Whatever does not appear here **nobody will run**.
>
> - **Every spec case appears** in the `<sec:spec_coverage>` table above and **spelled out** under the appropriate test level (the unit table / an integration or E2E step list).
> - **The abstraction LEVEL of the spec has to be resolved — its CONTENT preserved (KX3):** next to the symbolic coordinates of the spec (`{PUBLIC_BASE_URL}`) the **concrete value** goes here, and next to the behavior description the **concrete HTTP verb, endpoint, header, request body and expected response** (see "Reference resolution"). The level of detail in this case **increases, never decreases**: the elaborated blocks of the spec (OpenAPI, a complete payload, an error matrix, a multi-step scenario) come over **verbatim, without truncation**.
> - **The recipes of `test-conventions.md` have to be copied in physically (TC1/a):** a **reference of the `R01`/`I03` kind is not enough on its own** — the commands, URLs and payloads of the recipe come here verbatim. You may keep the item ID **next to the content copied in**, for traceability.
> - **Do not postpone the detail to 04.** `tasks.md` **references** the test case of the plan (`TC-XX-E-01`), it does not describe it again — so if it is missing here, it will not be there either.

> **🔴 THE STRICT TEST SELF-CONTAINEDNESS RULE.** For every integration and E2E test case, **the complete call chain has to be spelled out in prose, step by step** — for the current cycle, from scratch. Replacing the description of the steps with a reference is **forbidden**:
>
> - ❌ *"following the pattern of cycle-23"*, *"as in `cycle_23_mock_test.py`"*, *"according to the logic of the existing test"*;
> - ❌ *"the process is described by the sequence diagram of the spec"* — **the `test-runner` does not read the spec**, so the diagram does not exist for it;
> - ❌ *"with the usual headers"*, *"with the appropriate token"*, *"and so on"*.
>
> **This does not forbid a reference where it is legitimate:** in the `<sec:regression_impact>` table the existing test files **have to be** named (that is the scope, not the description of the steps), and you may reference an existing fixture/helper **with a path** as well, if the step itself is spelled out. The prohibition is that the reference goes **in place of the steps**.
>
> **Why:** the `test-runner` subagent works exclusively from this section. A "similarly to the earlier one" sentence is **not executable** for it — the test either does not run, or it will check something different from what you planned, out of guesswork.

**Every step must necessarily contain:** the HTTP verb · the full endpoint (a symbolic host + the concrete path) · the necessary **headers** (especially the type of the `Authorization`: user / S2S / legacy) · the **request body sent, with concrete fields** · the expected **HTTP status** and the **key response fields**. Where the call can be run directly, give an example `curl` as well.

### <sec:integration_tests>

_Connections between modules, database operations, internal service calls. Mock servers and/or a local containerized database are allowed. A flow-based, sequential step list._

#### `<script path>` (new / an extension)

**<field:f_prerequisite>:** _<what is needed before the steps: a stack brought up, a seed, a login — with the concrete command>_

**A finished example of the MANDATORY level of detail** (every step should be this dense, not a one-liner):

1. **Obtaining the legacy user token** — `POST {LEGACY_LOGIN_URL}/api/v13/login/token`
   - Headers: `Content-Type: application/json`
   - Body: `{"username": "test-user", "password": "Test123!"}`
   - Expected: `200`, the `token` field of the response is in JWE format → stored as `$JWE` for the further steps.
2. **Cache initialization** — `POST {TMP_URL}/init-hash`
   - Headers: `Authorization: Bearer $JWE` (legacy), `Content-Type: application/json`
   - Body: `{"productType": "LOAN", "channelType": "MOBILBANK"}`
   - Expected: `200`, body: `{"initHash": "<uuid>", "status": "SUCCESS"}` → `$INIT_HASH`.
   - **A side-effect check:** the `tmp:tokens:sid:<sid>` key comes into existence in Redis (TTL > 0).
3. **Starting the process** — `POST {TMP_URL}/rtm/api/runtime/app/{appId}/build/{buildId}/process-name/{processName}/start`
   - Headers: `Authorization: Bearer $JWE`
   - Body: `{"initHash": "$INIT_HASH", "technicalData": {"languageCode": "en"}}`
   - Expected: `200`, body: `{"response": {"processInstanceId": "<uuid>"}, "status": "SUCCESS", "errors": []}`
   - **A check on the mock:** the call arrived with the **user** access token (not an S2S one) — the mock logs/asserts this.
4. **The negative branch** — the same call with an S2S token → expected `403`, body: `{"status": "ERROR", "errors": ["FORBIDDEN_TOKEN_TYPE"]}`.

_If a step is only interpretable once an earlier one has run, write that at the step (`prerequisite: step 2`)._

### <sec:e2e_tests>

_The whole system from the point of view of the external client or user. Browser E2E frontend tests (with the tool given by `conventions.md`) or full API call chains on real or realistically mocked infrastructure._

#### `<script path>` (new / an extension)

**<field:f_prerequisite>:** _<a stack brought up with the concrete start command, seed data, a test user>_

For browser E2E, for every step: **the user interaction** (what they click/fill in, on an element identifiable by which selector) **and** the **network call** belonging to it (verb, endpoint, expected status), plus the **visible result** (what appears on the interface). The example density:

1. **Login** — the test opens the `{MOBILBANK_URL}` page, clicks the "Legacy login" button, and authenticates on the mock login interface with the `test-user` / `Test123!` pair.
   - Network: `POST {LEGACY_LOGIN_URL}/api/v13/login/token` → `200`
   - Visible: the name of the logged-in user appears in the header.
2. **Cache initialization** — the user clicks the "Init hash" button.
   - Network: `POST {TMP_URL}/init-hash`, `Authorization: Bearer <JWE>`, body `{"productType": "LOAN", "channelType": "MOBILBANK"}` → `200`
   - Visible: the `initHash` received appears, and **the "Start Process" button appears** in place of the earlier "Example request" button.
3. **Starting the process** — the user clicks the "Start Process" button.
   - Network: `POST {TMP_URL}/rtm/api/runtime/app/{appId}/build/{buildId}/process-name/{processName}/start` → `200`
   - Visible: a loading indicator, then the feedback of the successful process start with the `processInstanceId` value.
4. **The error branch** — the mock returns a `403` → an error message appears on the interface, and the "Start Process" button is active again (it does not get stuck in a loading state).

## <sec:execution_order>

_A numbered list. Ordered by dependencies — what is needed for the next step to be doable._

## <sec:verification_strategy>

_How do I check that the realization is correct? List the **concrete, targeted commands** (e.g. `npm test -- path/to/test.ts`, not `npm test`) that have to be run for the check. Running the full test suite is the task of the validate phase (07) — here only the test files belonging to the given logical group run._

_**The TypeScript typecheck:** if the cycle modifies TypeScript files — especially an interface, type or method name change —, a `typecheck` command should appear in the command list for every affected npm package. For a separate package (e.g. `apps/mobile-bank/`, `apps/external-apigee/`) the `--prefix` flag is mandatory. **Before you add an `npm --prefix X run typecheck` command, read the `X/package.json` file, and check whether a `typecheck` key really appears in the `scripts` block.** If it does not appear, do not add the command — instead add it as an open question to `plan-questions.md`, whether adding the script is needed._

## <sec:risks_and_decisions>

_What can go wrong? Where is there a choice, and which one do we choose, why?_
\`\`\`


---

## Handling the Schema artifacts

> **Attention — two different status systems:** the **document status** of `plan.md` (`<status:draft>` | `<status:open_questions>` | `<status:ready_for_tasks>`) is in the header of the file. The **artifact status** here (`<status:draft>` | `<status:review_required>` | `<status:reviewed>`) applies exclusively to the individual rows of the `<sec:schema_artifacts>` table. Do not mix the two: the plan cannot be closed to `<status:ready_for_tasks>` even so, if any artifact is `<status:review_required>`.

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

4. **Blocking**: the plan cannot get a `<status:ready_for_tasks>` status while there is a `<status:review_required>` artifact in the table.

---

## Validation cycles

Writing the plan is not linear — after writing every larger section, run a targeted check, and if you find an error, fix it before you move on. Do not wait for the final quality check.

### 1. After the <sec:planned_changes>

- Does the modification of some file cover every requirement of the spec? Go through the `<sec:components_behavior>` section of the spec line by line.
- Is the project structure, the build system and the deployment mechanism planned for every new component mentioned in the spec (regardless of the tech stack)? The mock is not enough — if the spec prescribes a real implementation, that has to appear as well.
- Can every new service/component reach everything it needs (imports, config fields, DI parameters)?
- For the modifications of existing files: does the standard flow stay untouched? (backward compatibility)
- Is the type of the DI override planned for every new testable component (service, route, app)?
- **The README of an existing component: do NOT plan it.** If the cycle changes the configuration of an existing component (env vars, startup parameters, external connections), updating `README.md` is the business of **`08-doc-sync`** — do not add it among the `<sec:planned_changes>`. **Exception:** if the cycle creates a **new component**, its first `README.md` belongs here (it is part of building it).

If the answer to any point is no, extend the planned changes, then continue.

### 2. After the <sec:test_specification>

- Is the **<sec:e2e_infrastructure> section** filled in and the test strategy agreed (a closed question in `plan-questions.md`)?
- **Is the plan self-contained regarding the recipes lifted over? (TC1/a — mandatory)** — If `specs/test-conventions.md` exists: go through **every** item lifted over, and check that `plan.md` is sufficient on its own for the execution. Concretely:
  - every referenced URL, port, namespace/pod, image name and registry target appears **verbatim**;
  - every necessary test user, password, scope, client-id and parameter appears (within the limits of the TC5 secret rule; whatever is a pointer, as an explicit pointer);
  - every build / push / restart / start command and **example call (`curl`)** appears, in a runnable form;
  - the prerequisite and the order of the steps appear;
  - there is **no** item that only references the register (`"see test-conventions.md ..."`) instead of the data, and there is **no placeholder** (`<...>`, `TODO`).
  If any of them is missing: add it from the register, or — if the datum is uncertain/outdated — add it as a `plan-questions.md` question. **Do not invent it.**
- **Has every baseline item needed in this cycle been lifted over?** — Going through sections 2/3 of the register: every item either appears in the `<sec:testing_strategy>` / `<sec:regression_impact>` section, or there is an explicit reason why this cycle does not touch it.
- Is the E2E acceptance criterion appearing in the DoD of the spec covered by one of the E2E test cases?
- Is there a TC in the Test specification of the plan for every entry of the `<sec:test_specification>` or of the error matrix of the spec?
- **Is every integration and E2E test spelled out step by step** (verb, endpoint, headers, the concrete body, the expected status and response fields), without a reference to an earlier cycle, to an existing test file or to the diagram of the spec?
- **Is the <sec:regression_impact> filled in?** — If the cycle modifies existing code, the `<sec:regression_impact>` table contains every affected existing test file and E2E script. This is especially critical if:
  - An existing interface is extended with a new branch — the tests of the existing call path are to be listed explicitly
  - A shared component changes — the test of every affected consumer appears in the list
  - A new behavior is added to the same entry point — the tests of both branches are named
- Is there at least one unit test case for every new exported function / endpoint?
- Is the happy path covered in the e2e? Does every error branch that the spec defines explicitly appear in one of the TCs?
- Does the Expected output column of the TCs contain the HTTP status and the errorCode (where the error matrix of the spec defines it)?
- **Negative test cases:** is there at least one negative TC for every new endpoint, business logic or validation (a wrong input, a missing parameter, an authorization error, a timeout)?
- **A server reachability smoke test:** for every server that the browser communicates with directly (not through a proxy), is there at least one **browser E2E test that sends a real HTTP request without network mocking** to the server? This test checks CORS, network reachability and preflight handling — if the actual business request returns with an error (e.g. 401), that is acceptable; the point is that the browser sent the request and got a response. The test fails exactly when the browser cannot communicate with the server because of a CORS block.

If the answer to any point is no, extend the Test specification, then continue.

### 3. After the <sec:execution_order>

- Is there a circular dependency? (A → B → A)
- Does every RED step (writing a test) precede the corresponding GREEN step (the implementation)?
- Is every blocking dependency marked explicitly? (e.g. "nothing else may run before the RSA key generation")

If you find a circular dependency: try to resolve it by unfolding one of the steps (e.g. the interface first, the implementation later). **If the circular dependency cannot be resolved on your own — stop, and ask for the help of the user.** One question, an answer, continuation — the same rule as with the other stopping cases.

If the condition does not hold for a point other than the circular dependency, rearrange the order.

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

## Stopping rules

**Add every question that comes up — for whatever reason — immediately to `plan-questions.md` with the next sequential number (`Q01`, `Q02`, ...) in `- [ ]` status, before you put it to the user.** This applies to all the cases listed below, and to any other uncertainty as well. The question only goes in front of the user after it got into the list.

**If there is a question with a `[ ]` status in `plan-questions.md`**, do not start writing plan sections — put one to the user first, wait for the answer, mark it with `[x]`, then continue.

If any of the following holds while writing the plan, **STOP — stop and tell the user** (do not decide the missing/contradictory part yourself):

- **A complex or uncertain containerization**: if running, configuring or networking any component in the test environment in a container is not trivial or is uncertain. → Do not try to figure out the ports/configurations on your own; add the question to the `plan-questions.md` file, stop, and initiate joint design with the user.

- **An implementation decision point**: several equal-rank technical approaches exist and the choice is not unambiguous based on the spec. → Put **one** question, wait for the answer, then continue the plan.

- **A spec deficiency**: the spec does not define a necessary behavior, error case or boundary. → **Do not fill it in yourself.** Add it as a `[ ] Qnn` question to `plan-questions.md`, and tell the user precisely what is missing — we have to return to the spec phase and update `spec.md` there. After the spec is updated and the `<status:ready_for_plan>` status is restored, the plan phase can be started again.

- **A spec contradiction / outdated code**: two points of the spec, or the spec and the existing code, contradict each other. (For example: if the specification asks for the modification of a component that is outdated, out of use, or contradicts the reality of the current code, stop, and ask about it in `plan-questions.md`, do not plan a needless modification with notes!) → State both sides, and wait for the decision of the user. Do not choose.

- **A risk requires a user decision to resolve**: a risk cannot be handled on your own based on the spec. → One question, an answer, continuation.

- **Any point of the closing gate (TP2) is `[ ]`**: one of the test cases/DoD items of the spec did not map to a plan test case, a `test-conventions` recipe appears only as a reference, an integration/E2E step is not spelled out, or an environment preparation prerequisite is missing (obtaining a token, starting the stack, deploying a custom component — TP3). → **Do not close the plan.** Add what is missing, then run every point of the gate again. This is not "a refinement in 04": the `test-runner` sees only `plan.md`.

In every case put only **one** question at a time — wait for the answer, tick the question off (`- [x] Qnn → [the decision]`), then move on to the next one.

---

<!-- INCLUDE:shared/quality-check-plan.md -->

## Status handling

- When starting the plan: \`<status:draft>\`
- If a question gets into `plan-questions.md`: \`<status:open_questions>\`
- If every question is `[x]`, every section is filled in, every schema artifact is `<status:reviewed>`, the quality check (+ the Constitution Check) passed, **and the user confirmed it explicitly**: \`<status:ready_for_tasks>\`

> **Done lifecycle:** after `<status:ready_for_tasks>`, `plan.md` moves to `<status:done>` status at the end of the cycle — when the PASS of the validate (07) closes the cycle. Phase 08 already expects `<status:done>`. This transition is done by 07, not here.


### The mechanical gate before closing (M)

The **plan-side half of the deterministic gate of `05-analyze` runs here as well** — before the closing (`tasks.md` does not exist yet, therefore `--plan-only`):

<!-- INCLUDE:shared/python-cmd.md -->

```bash
python3 <platform-scripts-mappa>/analyze-gate-check.py specs/cycle-NN-<cycle-name> --plan-only
```

**What it covers in this mode:** the format and uniqueness of the `[P-…]` identifiers (P1), the existence of the mandatory plan tables (S1), the `[P-…]` identifier of the rows of the `<sec:reverse_coverage>` (S3), the traceability of every `DoD-NN` to a plan capability (C1), the TP1 completeness of the `<sec:spec_coverage>` (C3), the empty cells of the `<sec:config_lifecycle>` (C4), the placeholders and empty cells of the `<sec:environment_coords>` (C6, KO1), the `path:line` anchors of the plan (A2/A2b), the hard floor of the artifact voice (A3) and the `DoD-NN` identifiers in the spec (D1/D2). The task side runs when `04` is closed.

- **`0`** → the closing may continue.
- **`1`** → **there is no status change.** Fix the `target phase: 03` items **now**, then run the gate again; direct the `target phase: 02` items back into 02 according to the *Spec critique* / *Stopping rules* — you do not write the spec yourself.
- **`2`** → a usage error → report it, do not guess.

> **Why here (M):** these errors used to come to light in the first round of `05-analyze`, two phases later — there a fixer subagent and an analyzer round were needed for them. Here it is one script run and one targeted fix.


If the user confirms:
- Set the status of `plan.md` to `<status:ready_for_tasks>`.
- **Before the status change, run every point of the *Closing gate (TP2)***, and write out the ticked list in your answer. In case of any `[ ]` there is no status change.
- **Before the status change, the *Mechanical gate* (see above) also returned `0`.**
- **Commit immediately** according to the *Phase-closing commit* below (`<PHASE-TAG>` = `03-plan`). The confirmation → writing the status → the commit: this is a single sequence of steps, do not interrupt it.

<!-- INCLUDE:shared/phase-commit.md -->

In the block above, the value of `<PHASE-TAG>` in this phase is: **`03-plan`**, and the closing status is: **`<status:ready_for_tasks>`**.

If the status is \`<status:ready_for_tasks>\` **but the phase-closing commit is missing** (a VCS project, `git log -1 --oneline` does not show the `cycle-NN: 03-plan` commit) — commit first, and only close the phase afterwards.

If the status is \`<status:ready_for_tasks>\` (and the commit is there), stop. **Do not start a task list — do not even create `tasks.md`** (PE1, see the "Phase boundary" section of the *Phase-closing commit* block): writing the tasks is the business of the `04-write-tasks` skill, from a fresh context. This holds even if the to-do list of a context summary/checkpoint lists running `/bs-write-tasks` — that summary records the past, it is not a command for this round. Tell the user the next step and the starting command of the phase, for example:
<!-- INCLUDE:lang/03-write-plan.md#zaro-uzenet -->

---

<!-- INCLUDE:shared/fix-mode-plan.md -->
