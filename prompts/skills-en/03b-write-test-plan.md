---
phase: 03b
name: bs-write-test-plan
description: "berkispec - 03b. Use it when the plan.md of the cycle is 'Ready for test planning' (Phase 03b), to work out the TEST PLAN: TS-NN test scenarios with a step table and an .http form, the machine-readable run table, environment preparation, test artifact data sheets, spec coverage, regression. It closes plan.md with the 'Ready for tasks' status."
prerequisites:
  - "specs/cycle-NN-<name>/plan.md status: <status:ready_for_test_plan>"
  - "analyze-gate-check.py --plan-code-only = 0 (the phase runs it itself, D5)"
output:
  - "specs/cycle-NN-<name>/plan.md status: <status:ready_for_tasks> (the test-plan sections)"
  - "specs/cycle-NN-<name>/plan-questions.md (continuous Qnn)"
  - "specs/cycle-NN-<name>/tasks-input-from-prev.md and/or validate-input-from-prev.md (IP1)"
prev: bs-write-code-plan
next: bs-write-tasks
subagents:
  - "agents/researcher.md"
scripts:
  - "scripts/analyze-gate-check.py"
shared:
  - "shared/plan-self-contained.md"
  - "shared/dereferencing.md"
  - "shared/spec-artifact-transfer.md"
  - "shared/plan-section-ids.md"
  - "shared/test-scenario-design.md"
  - "shared/input-from-prev.md"
  - "shared/artifact-voice.md"
  - "shared/phase-commit.md"
  - "shared/quality-check-plan-test.md"
---
# 03b — Writing the test plan
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

We develop software in spec driven development. The development is split into cycles. Every cycle is an independently developable, independently testable part of the whole implementation.

This is **phase 3b (0–9)** of the process: 0-init · 1-cycles · 2-spec · 3a-code-plan · **3b-test-plan ←** · 4-tasks · 5-analyze · 6-implement · 7-validate · 8-doc-sync · 9-merge.

---

## Cheat sheet

| Section | In one sentence |
|---|---|
| Prerequisite | `plan.md` = `<status:ready_for_test_plan>`, and `analyze-gate-check.py --plan-code-only` **run by you** returned `0` (D5). |
| Scope | **The test plan only.** You do not rewrite the code half — exactly three extensions are allowed: a new `<sec:reverse_coverage>` row, a new `[P-…]` entry for a test artifact, and a test-side risk in `<sec:risks_and_decisions>`. |
| Input | The **code half** of `plan.md` (coordinates, planned changes, configuration, schema) + the **test section and `DoD`** of the spec + sections 2/3 of `test-conventions.md`. |
| Test scenarios | A `TS-NN` block for every test case of the spec (TS1–TS8): a step table with the verb, the full endpoint, headers, a concrete body and a checkable expected result — for REST also in `.http` form. |
| The generating recipe | `TD0–TD7` (`test-scenario-design.md`) — **the engine of this phase**: dimension inventory, the observation quartet, countability, isolation, calibration, self-test. |
| The machine-readable run table | The mandatory `<sec:machine_run_table>` (TP4): category, type, prerequisite, command, result file, format, cleanup, environment, **phase** (PH1). |
| The target environment | The command of a non-local category contains the target host **literally**, the prerequisite calls the same place with a probe, `localhost` is forbidden (EV2–EV5). |
| Test identifiers | `TS-NN` + `TC-NN` in a **shared namespace, continuous across the cycle** (TI1) — `tasks.md` and the log of 07 reference these. |
| The test-file data sheet | Under every `#### <test file path>` the `TA1` data sheet is mandatory: what it checks · how it is run · fixtures · test cases. |
| Spec coverage | **Every row** of the `<sec:spec_coverage>` table names at least one `TS-NN` (TS7) — the test cases of the spec have to be converted, not copied over as prose. |
| Environment preparation | The prerequisites of the test (obtaining a token, starting the stack + a health check, building/deploying/rolling back a custom component, seeding) as **literal commands** in the plan (TP3); what was built in an earlier cycle and is not in the register you lift over from there (TP3/a). |
| Test recipes | Lifted over from `specs/test-conventions.md` **in full, self-containedly** (TC1/a) — a reference is not enough, the recipe has to be **physically copied**. |
| Regression | The `<sec:regression_impact>` table is filled in, or there is an explicit "none". |
| **Self-containedness** | `plan.md` contains **everything** needed for testing — `test-runner` reads **only this**, neither the spec nor `test-conventions.md`. |
| Validation cycles | A targeted check after every large section, before you move on. |
| Spec critique | Narrowed to the **test section** and the `DoD` of the spec: a missing/contradictory test case → back to 02; a test coordinate left in the spec → lifted over. |
| Closing | The quality check + the **Closing gate (TP2-test, printed ticked)** + the **mechanical gate** (`analyze-gate-check.py --plan-only`, M) + user confirmation → `<status:ready_for_tasks>`, commit. |

---

## What you have to do

**You write the TEST HALF of the plan**, into the same `specs/cycle-NN-<cycle-name>/plan.md` file whose code half has already been closed by `03a-write-code-plan`. Your deliverables:

- `<sec:testing_strategy>` — what types of tests are needed, what we mock;
- `<sec:plan_test_scenarios>` — the `TS-NN` scenarios with a step table and an `.http` form (**the main deliverable of the phase**);
- `<sec:machine_run_table>` — the machine-readable run table of `run-tests.py`;
- `<sec:e2e_infrastructure>` — the environment preparation (TP3), built on the closed `Q01` decision;
- `<sec:regression_impact>` — the regression impact;
- `<sec:test_specification>` — test identifiers (TI1), `<sec:spec_coverage>`, Lifecycle, `TA1` data sheets, unit/integration/E2E tables;
- `<sec:execution_order>` and `<sec:verification_strategy>` — ordered with both halves in view.

**What you do NOT write:** the sections of the code half (`<sec:goal_and_approach>`, `<sec:affected_components>`, `<sec:environment_coords>`, `<sec:planned_changes>`, `<sec:new_dependencies>`, `<sec:config_build_changes>`, `<sec:schema_artifacts>`). From these you copy **literal values** into your test sections — you do not reference them, and you do not edit them.

> **The three allowed extensions into the code half — there is no fourth:**
> 1. **`<sec:reverse_coverage>`:** you may add a **new row** for your own test sections (per `PID1` the test sections carry a `[P-…]` ID too). You do not modify and do not delete an existing row; if you find an existing row wrong, that is a `Qnn` question or a redirect to `03a`.
> 2. **`<sec:planned_changes>`:** you may add a **new `[P-…]` entry`**, **exclusively for a test artifact** (test file, fixture, mock, seed data, test helper) — with the mandatory `**<field:f_purpose>:**` line. The `TA1` data sheet requires the path of every fixture, and whatever does not exist yet is a **new file**. **Never** for production (non-test) code: that is a redirect to `03a`. You do not edit an existing `[P-…]` entry.
> 3. **`<sec:risks_and_decisions>`:** you may write a **new paragraph** about a test-side risk (a flaky scenario, a shared environment, a long run). You do not rewrite an existing paragraph.

**🔴 The `TS7` conversion is the essence of this phase.** The test cases of the spec are **not copied over as prose** into the plan, they are **converted** into `TS-NN` blocks. You do **not open** the spec's own heading structure (`Test case N`, "REST sequence", "Verification") in the plan: what is not in a `TS-NN` block is not seen by the gate, is not run by `test-runner`, and is not assembled by the manual test plan.

**🔴 The `TD0–TD7` recipe is a question sequence to be filled in, not a reading.** The **product** of the dimension inventory decides **how many** scenarios are needed — not how many test cases happened to fit into the spec. The recipe is in the `test-scenario-design.md` block, below.

**If a test plan already exists in `plan.md`** (the status is `<status:ready_for_tasks>`): read it, and run the quality check on it. If you find a gap, fix it according to the iteration rules — do not start over.

---

<!-- INCLUDE:shared/plan-self-contained.md -->

---

## <field:f_prerequisite>

0. **Identifying the cycle:** if the user gave a cycle/file, use that; otherwise offer the most recent `specs/cycle-*` folder for confirmation — <!-- INCLUDE:lang/common.md#ciklus-beazonositas --> — and wait for the answer before you move on.

1. **`conventions.md` existence check:** read `conventions.md` in the root of the project. If it does not exist, STOP — go back to phase `00`.
2. **Working-tree check (only with VCS):** run `git status --short`. If there are uncommitted changes, list them, and ask in one round whether to commit them or to continue. (Skipped in a no-VCS project.)
3. **Read the status of `plan.md`.** If it is not `<status:ready_for_test_plan>`:
   - `<status:draft>` or `<status:open_questions>` → **the code plan has not been closed.** STOP, and send the user back to `/bs-write-code-plan`.
   - already `<status:ready_for_tasks>` → **the test plan is done.** Do not start over: run the quality check, and if you find a gap, fix it according to the *What you have to do* section.

4. **🔴 The status field is SELF-DECLARED — run the gate of the code plan (D5).** The `<status:ready_for_test_plan>` status was written by `03a` **for itself**; the quality of your input must not depend on its own claim. Run:

<!-- INCLUDE:shared/python-cmd.md -->

   ```bash
   python3 <platform-scripts-mappa>/analyze-gate-check.py specs/cycle-NN-<cycle-name> --plan-code-only
   ```

   - **`0`** → the code plan is fine, you may continue.
   - **`1`** → **STOP.** List the `## <status:must_fix>` items, and send the user back to `/bs-write-code-plan`: *"The gate of the code plan gave N blocking findings (…) — these have to be settled in `03a` before the test plan."* **You do NOT fix the code plan** — otherwise a test plan built on an incomplete coordinate set gets set in concrete, and the defect only surfaces in `07`, as a plan gap.
   - **`2`** → a usage error → report it, do not guess.

   **Why you are the one who runs it (the principle of `7/j`):** the closing phase has no interest in failing its own gate — **the receiving one does**, because it is the one writing a bad plan from an incomplete input. The stamp (the `**<field:f_gate_code>:**` line) is a **claim**, this run is the **evidence**.

5. **Open questions:** there is no `[ ]` question in `plan-questions.md`. If there is, the code plan was not really closed — clarify it before writing a test section (the `Q01` E2E decision in particular: the `<sec:e2e_infrastructure>` section is built on it).

---

## Continuing after an interrupted run

If the test-plan phase is interrupted and continues in a new session:

```
1. Read the test sections of plan.md and the state of plan-questions.md.
   → Which TS-NN block is already there, which DoD-NN has no scenario yet,
     is the machine-readable run table filled in, is there a TA1 data
     sheet for every test file?

2. Only write/continue test sections if every question is [x].

3. If the test plan looks coherent but the status is not
   <status:ready_for_tasks>: run the quality check + the mechanical gate,
   then ask for a confirmation.
```

The current state of `plan.md`, `plan-questions.md` + this prompt is enough for the restart.

---

## Handling open questions

`plan-questions.md` is the **shared** question register of the plan phase (03a **and** 03b). It was created by `03a`; you **continue** it.

**Ground rule: we never delete from the list, and we never renumber.** You leave the closed entries (`[x]`) of `03a` untouched — the `Q01` E2E decision is the foundation of your `<sec:e2e_infrastructure>` section. You append a new question to the end of the list, with the **next free** `Qnn` number.

**If the decision of `Q01` turns out to be untenable during test planning** (e.g. the chosen mock level cannot prove `DoD-03`), **do not rewrite the closed entry**: add a new `Qnn` that references it, and put it to the user.

**The workflow:** proceed question by question — put only one at a time. When the answer arrives: mark it `[x]`, and write a one-line summary of the decision next to it (`→ ...`). If a new question comes up from the answer, add it to the end of the list immediately. **Every time you ask a question or ask for an approval, place a direct, clickable markdown link to the file concerned at the end of your answer.**

**Closing:** if every test section is done, every question is closed and the quality check passed, put the question to the user: <!-- INCLUDE:lang/03b-write-test-plan.md#statusz-megerosites --> — Do not switch the status before the confirmation. **Place the direct, clickable link of `plan.md` at the end of the answer.**

---

<!-- INCLUDE:shared/dereferencing.md -->

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

## Context loading rules

> **Your main input is the code half of `plan.md`** — not the spec, and not the code base. `03a` has already discovered the coordinates and the affected source files; your job is to build a test scenario from these, with **literal values**.

- **`plan.md` — mandatory, the whole code half:** `<sec:goal_and_approach>`, `<sec:affected_components>`, `<sec:environment_coords>` (URLs, ports, test users with passwords, example calls), `<sec:planned_changes>` (`[P-…]` IDs, purposes), `<sec:config_lifecycle>`, `<sec:schema_artifacts>`, `<sec:reverse_coverage>`.
- **`spec.md` — the `<sec:test_specification>` section and the `<sec:definition_of_done>`.** This is the source of the `TS7` conversion. You do **not** have to re-read the rest of the spec (the goal, component behavior, requirements) — whatever is needed for the design is already in the code half of the plan.
- **`conventions.md`:** the test tools (`<sec:cv_test_framework>`, `<sec:cv_test_structure>`) and the **report artifacts** (`<sec:cv_test_reporting>`) — the result-file column of the machine-readable run table lives on this.
- **`plan-questions.md`:** the closed decisions, the `Q01` E2E strategy in particular.

> **Which register knows what (TC1/c):** the **report artifacts, their path base and the report-generating commands** live in the `## <sec:cv_test_reporting>` section of the project `conventions.md` — **that is what the TR3 gate of 07 reads**. `specs/test-conventions.md` is the register of the **recipes and coordinates**. If the cycle changes the report structure or the report command, `conventions.md` has to be updated (GC1) — updating `test-conventions.md` is not a substitute for it. **Modifying `conventions.md` is the business of the code plan** (`03a`): if such a change is needed, that is a `Qnn` question or a redirect.

- **`specs/test-conventions.md` — sections 2 and 3** (the locally, resp. integration/E2E required items of every round), **and** those recipes of section 1 that are needed for the bootstrapping. **Guard:** if the file does not exist (an early cycle), do not stop and do not create it — state it in one sentence, and work from the existing test infrastructure.

  > **🔴 `plan.md` is SELF-CONTAINED (TC1/a — mandatory).** The `run-tests.py` script reads the **machine-readable run table** of `plan.md`, and the `test-runner` subagent (the fallback) does **not read** `test-conventions.md` — only the `<sec:testing_strategy>` and `<sec:regression_impact>` sections of `plan.md`. Therefore **every testing task has to be lifted into `plan.md` completely**, supplemented with **all** the belonging data of block 0 and section 1: test users and their passwords, URLs, ports, namespace/pod, image name, registry target, parameters, **example calls (`curl`)**, build/push/restart commands, prerequisites and the run order.
  > - **A plain reference is NOT enough** (`"see test-conventions.md R03"` on its own is forbidden) — reference `test-conventions.md` only as **provenance** next to the content lifted over (e.g. "_(source: test-conventions.md R03)_").
  > - **A placeholder is FORBIDDEN** (`<here comes the password>`, `<TODO URL>`) — if a datum is missing or outdated, that is a `plan-questions.md` question, not a placeholder.
  > - **It is not an automatic run:** **only what** is really needed in this cycle is carried over from the register. This lifting is itself the human control point — `plan.md` is the single truth of the run.
  > - **An outdated item:** if the data of a recipe does not match reality, or its `<field:f_last_run>` marker is old, **ask about it** in `plan-questions.md`. Do **not write** `test-conventions.md` — fixing it is the business of `08-doc-sync` (TC4); the cycle takes the correct data agreed with the user into the plan.
  > - **A recipe with a `<status:scope_shared_remote>` scope** (the register marks it so): before lifting it, **you must ask** about it in `plan-questions.md` — in a shared dev/test environment an image push or a pod restart affects the work of others as well.

- **🔴 You do NOT start a `researcher` for source-file identification.** `03a` did that, and its result is in `<sec:planned_changes>`. This is the context discipline of this phase: re-exploring the code base here is duplicated work, and the test plan is built from the plan, not from the code.
- **`researcher` Mode B — for one purpose only:** if the **actual call chain of an existing test file** has to be extracted literally (a fixture, a seed, a helper, an expected response), you may start it — **asking for literal values**, according to the rule of *Reference resolution*.
- **The `plan.md` files of earlier cycles — only with the TP3/a exception:** if running the test requires an environment prerequisite built by an earlier cycle (a custom plugin/SPI, a mock server, seed data, a container stack, a test user, a token-obtaining helper), **and its commands are not in `specs/test-conventions.md`**, you lift those over with `researcher` Mode B, **verbatim**, with a `_(source: cycle-NN plan.md)_` provenance. Only the recipe needed for the execution — not the design of the earlier cycle.

---

<!-- INCLUDE:shared/artifact-voice.md -->

---

## Plan structure — the test half

<!-- INCLUDE:shared/plan-section-ids.md -->

> **The sections from `<sec:goal_and_approach>` to `<sec:reverse_coverage>` have already been written by `03a-write-code-plan`** — you step the header and the status field, you do not edit their content (for the three allowed extensions see the *What you have to do* section). You write your own sections **BEFORE `<sec:risks_and_decisions>`**: the physical order of the sections of `plan.md` stays unchanged.

\`\`\`md
## <sec:testing_strategy>

_What kinds of tests are needed (unit / integration / e2e)? Which existing test file is modified, which new file comes into existence?_

_**The recurring expectations lifted over (TC1) — mandatory if `specs/test-conventions.md` exists:** the items of sections 2 and 3 of the register that are needed in this cycle, **self-containedly** (with the recipe data belonging to them, not with a plain reference). Next to every item lifted over, write the provenance: `_(source: test-conventions.md L01)_`. If you corrected the data of an item in `plan-questions.md`, the **corrected** data goes here._

<!-- INCLUDE:shared/test-scenario-design.md -->

### <sec:plan_test_scenarios> — **mandatory (TS1)**

> **🔴 Why it is mandatory:** the prose above is about the test **types**, this section is about the test **content**. `plan.md` is self-contained (TC1/a): both the `test-runner` and `bs-manual-test-plan` work **exclusively** from it, and a failed test of `07` must also be reproducible by hand from it. Therefore every test case has to be worked out as an **executable scenario** — not "the login flow will be tested", but step by step: what we call, with which concrete value, and exactly what we expect back.
>
> **The yardstick (self-test):** *"A person who did not take part in the design can carry out the test reading only this section, and can decide whether it succeeded."* If they would have to figure out anything — which URL, which user, what the correct answer is — the scenario is incomplete.
>
> **The test cases of the spec must not be merged (KX3).** If the `<sec:test_specification>` section of the spec describes six cases, six scenarios stand here — expanding and refining is allowed, merging and dropping is not.
>
> **🔴 Do not copy the STRUCTURE of the test section of the spec — convert it (TS7).** The most frequent failure is not that a test is left out, but that the phase brings over the **own heading structure of the spec** (`Test case 0`, `Test case 1`, with a "REST sequence", "Verification" bullet list), and next to it the `### <sec:plan_test_scenarios>` section **is never even created**. The result looks like readable prose, but: the mechanical gate does not see it (there is no `TS-NN`), the `test-runner` does not run it, the `bs-manual-test-plan` assembles nothing from it, and the per-step expected result stays uncheckable. Therefore:
>
> - **every** test case of the spec is converted into **one standalone `TS-NN` block**, with the four lines above and the four-column step table;
> - you **must not open a parallel, self-named section** for the test cases of the spec (`Detailed test cases`, `Sequence descriptions`, `Test case N`) — whatever is not in a `TS-NN` block does not exist for the framework;
> - the mapping is recorded by the `<sec:spec_coverage>` table: **the `Plan test case(s)` cell of every row names at least one `TS-NN`** (next to the `TC-…` identifier). This is what the gate measures, in both directions.

One block per scenario, in exactly this form:

#### TS-01 — <the name of the scenario>  (DoD-02, DoD-05)

**<field:f_what_we_test>:** <what this scenario verifies — the behavior it runs for, in one sentence>
**<field:f_prerequisite>:** <the state it starts from: a stack that is up, seed, a logged-in user, the result of an earlier `TS-NN`>

| # | Step | Call | Expected result |
|---|---|---|---|
| 1 | <what we do> | `<a literally runnable call>` | `<a concrete, checkable response>` |

**<field:f_cleanup>:** <what has to be stopped or restored afterwards>

**Rules for filling it in:**
- **`<field:f_what_we_test>` — a claim, not a topic (TD7).** This line says **what** the scenario verifies and **why**: the behaviour as a decidable claim (*"out of five simultaneous requests exactly one renews the token, the rest are served from the existing one"*), plus the acceptance criterion or risk it proves. **Repeating the heading is not enough** ("concurrency test", "testing `/init-hash`") — from that, phases 06/07 cannot tell whether a failure is a real defect or a bad test. The gate measures this (TS2).
- **`DoD-NN` in the header — mandatory and bidirectional (TS5).** Every scenario names which DoD points it proves, and **every `DoD-NN` must have at least one scenario**. The gate measures both directions.
- **Call column — literally runnable.** For REST, a full `curl`: verb, full URL with the port, headers, the concrete request body. A non-REST test belongs here in the same form: a UI step (what we click, what we type), a CLI command, a DB query. **A reference is not a call** — "see the `<sec:e2e_infrastructure>` section" is not runnable.
- **Expected result column — concrete and checkable.** The status code **and** the identifiable part of the response (field name, value, payload fragment, the text of a UI element). "Runs successfully" / "returns an error" / "gives the expected result" is **forbidden**: it cannot be decided. The hard floor of the gate (TS3): at least one backticked value or a number.
- **Test users, passwords, URLs, ports, identifiers: literally.** The values of `<sec:environment_coords>` (KO1) have to be **written in here**, not referenced — a placeholder is forbidden (TS4), and missing data is a `plan-questions.md` question. Credentials according to the secret rule (TC5): a dev-scope test user yes, a cluster/registry/IAM credential never.
- **The data flow must be traceable.** If the next step uses the output of a step, write out **which field into which variable** (`the `response.initHash` field of the answer → `$INIT_HASH``).
- **Numbering:** from `TS-01`, without gaps and uniquely (TS6). When fixing, do **not** renumber the existing identifiers — new ones go to the end of the list.
- **🔴 For a REST call the `.http` block is mandatory too (TS8).** The `Call` cell of the step table speaks to the **machine** (a one-line, runnable `curl`/command) — a human, however, needs to see the request with its headers and body, in a clickable form. So at the end of every `TS-NN` block that has a REST step there stands a ```http fenced code block (the VSCode REST Client / IntelliJ `.http` form) with **the same values**, referring to the number of the step:

```http
@tmp = https://tmp.dev.example.com
@legacy = https://legacy.dev.example.com

### step 3 — opening a session (the `sid` field of the response → the `{{sid}}` variable of step 4)
POST {{legacy}}/api/v13/login/login
Content-Type: application/json

{"email": "test.user@example.com", "password": "Pass1234", "clientId": "INTERNETBANK", "sessionId": "session-1"}

### step 4 — cache initialization
POST {{tmp}}/init-hash
Authorization: Bearer {{jwe}}
Content-Type: application/json
X-Correlation-Id: 11111111-1111-1111-1111-111111111111

{"productType": "LOAN"}
```

  The block **does not replace** the step table (the TS3 of the gate measures the cells of the table), nor the other way round: the two are the same call for two audiences. If they differ, one of them is wrong — fix it. This form carries over unchanged into the `TG-NN` groups of `bs-manual-test-plan` (MT11), and the gate measures it in both directions (TS8): a `curl` without a `.http` and a `.http` without a `curl` are both findings.
- **Bootstrapping does not belong here:** starting the stack, obtaining the token and the deploy live in the `<sec:e2e_infrastructure>` section (TP3); here the `<field:f_prerequisite>` line **references** it.

### <sec:machine_run_table> (run-tests.py) — **mandatory (TP4)**

> **🔴 Why it is mandatory:** the prose above speaks to a human, this table speaks to the **`run-tests.py`** script. If it exists, 07-validate runs the tests **with a script**, and the raw test log never gets into an LLM context — this is the largest token item of this phase. If it is missing, 07 falls back to the more expensive `test-runner` subagent. The table does not substitute for the prose: **the same commands**, in a machine-readable form.

| Category | Type | Prerequisite | Command | Result file | Format | Cleanup | <field:f_environment> | <field:f_phase> |
|---|---|---|---|---|---|---|---|---|
| unit | gyors | — | `<the verbatim command, with a machine reporter>` | `junit.xml` | junit | — | local | <status:phase_both> |
| integration | gyors | — | `<command>` | `<file>` | junit | — | local | <status:phase_both> |
| e2e | nehez | `<the reachability probe of the target; starting the stack>` | `<the command with the target host>` | `<file>` | junit | `<tear-down>` | `<the name of the target environment>` | <status:phase_validate> |

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
- **<field:f_phase> — which PHASE runs it (PH1).** Three values: `<status:phase_implement>` (only the dev loop of phase 06 runs it), `<status:phase_validate>` (only 07-validate), `<status:phase_both>`. **An empty cell means `<status:phase_both>`** — silence never means skipping, so an unmarked category runs everywhere. `run-tests.py` filters with the `--phase` switch: `06` calls it with `--phase <status:phase_implement>`, `07` with `--phase <status:phase_validate>`.
  - **When `<status:phase_implement>`:** a cheap, fast dev-loop check that a broader category covers anyway during validation (e.g. a separate `lint` or `typecheck` row next to the full unit set).
  - **When `<status:phase_validate>`:** an expensive category or one requiring a deployed environment (E2E, regression, a test running against the dev deploy) that is not worth running — or cannot be run — in the dev loop of 06.
  - **🔴 A test proving a `DoD-NN` can never be `<status:phase_implement>`-only.** With `dod-check.py`, `07` joins evidence from the **validation round**: whatever ran only in 06 leaves the DoD without evidence, and the item stays at `?`. If a category is needed for the DoD, the correct value is `<status:phase_validate>` or `<status:phase_both>`.
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

### 🔴 Test identifiers — the shared namespace of the plan and the tasks (TI1)

`tasks.md` **references these two identifiers**, and the evidence join of `07` works with them as well. So exactly **two families of test identifiers** live in a cycle, both unique and gapless across the cycle:

| Identifier | What it marks | Where it is created |
|---|---|---|
| `TS-NN` | an executable **scenario** (integration / E2E / manual), with a step table | `<sec:plan_test_scenarios>` |
| `TC-NN` | a single **test case** in the test tables (typically unit) | `<sec:unit_tests>` / `<sec:integration_tests>` / `<sec:e2e_tests>` |

- **From `TC-01` continuously, for the WHOLE CYCLE** — not restarted per file, and **not** in a `TC-<module>-01` form. One identifier marks one test case, however many test files there are.
- **The identifier never changes** during the cycle (`tasks.md` and the log of `07` refer to it). A later insertion gets the next free number; a deleted number is not reused.
- **Every `TC-NN` and `TS-NN` gets an owner in `tasks.md`** (`TT1`): a task that writes it and a `[CHECK]` that runs it. So **granularity matters**: a `TC-NN` should be as big as a test run command can execute **on its own** (`-t "<name>"`, `-k <pattern>`), otherwise the running checkbox cannot filter for it.

### <sec:spec_coverage> (a mandatory table)

_Every case of the `<sec:test_specification>` section of the spec and every item of the `<sec:definition_of_done>` maps to **at least one** plan test case. Without the table the plan cannot be closed._

| Spec source | Plan test case(s) | Level |
|---|---|---|
| _the name of the spec test case / a `test-conventions` item ID / `DoD-NN`_ | `TS-03`, `TC-01`, `TC-02` | unit / integration / E2E |

_**The `Plan test case(s)` cell mandatorily names at least one `TS-NN` scenario (TS7)** — the `TC-…` identifier on its own is not enough: that is only a table row, while the `TS-NN` is the executable scenario. The only exception is a case that cannot be tested in this cycle: there the cell carries the justification (e.g. "cannot be automated — a manual `[CHECK]` in step 7 of the `<sec:execution_order>`"), and the gate lets that through as a note._

_**The `Level` column is not a free choice:** the nature of the behavior decides it. **If the DoD/spec describes behavior observable on a user interface** (a button, an element appearing, a screen state), then a **browser E2E is mandatory** — an API-level E2E does not substitute for it. If there is no browser E2E tool in the project, that is a `plan-questions.md` question, not a silent downgrade._

_If a case from the spec **cannot** be tested in this cycle, the row stays, with a justification in the "Plan test case" column (e.g. "cannot be automated — a manual `[CHECK]` in step 7 of the `<sec:execution_order>`"). **It cannot be left empty or omitted.**_

### Lifecycle

| Level | When we write it | When we run it | What it blocks |
|---|---|---|---|
| Unit | BEFORE the implementation | every commit | the RED→GREEN cycle |
| Integration | AFTER the implementation | with the service stack up | closing the cycle |
| E2E | AFTER the implementation | with the full stack up | closing the cycle |

### The test artifact data sheet (TA1) — mandatory in the header of every test file

> **🔴 Why it is mandatory:** designing a test file **does not end with listing the test cases**. If it is not stated with which **framework** it is written, with what **command it can be run on its own**, what **fixture / mock / test data** it needs, and which **test function** covers which case, the implementer will make it up — and the `[CHECK]` task will run a different artifact than the one you planned, or the test will not be runnable on its own at all. Under every `#### <test file path>` heading of the `<sec:unit_tests>`, `<sec:integration_tests>` and `<sec:e2e_tests>`, BEFORE the test cases, this data sheet stands:

```md
#### `test/unit/token-store.test.ts` (new)

**<field:f_what_it_checks>:** the behaviour of token access reading from the shared store: with an empty store there is no guessed value, and with parallel readers exactly one renewal runs (DoD-01, DoD-04).
**<field:f_test_run>:** `node:test` + `tsx` — `npx tsx --test test/unit/token-store.test.ts`
**<field:f_test_fixtures>:** `test/fixtures/s2s-token.json` (a new file — in the `[P-30-09]` entry of the `<sec:planned_changes>`): one expired and one valid `S2STokenEntry`; the Redis is replaced by `ioredis-mock` (an existing dependency)
**<field:f_test_cases>:** `returns null on empty store` → `TC-01` · `refreshes once for 5 parallel readers` → `TC-02`, step 5 of `TS-01`
**<field:f_prerequisite>:** no external prerequisite; env: `REDIS_KEY_NAMESPACE=dsp`
```

**Filling rules:**
- **<field:f_what_it_checks> — the purpose of the test file, as a claim (TD7).** What this artifact verifies **together**, and which `DoD-NN` it serves. Not an unfolding of the file name ("the tests of the token store"), but the behaviour it exists for.
- **<field:f_test_run> — the framework AND the command narrowed to this one file, runnable verbatim.** The same command goes into the `[CHECK]` task and into the `<sec:verification_strategy>`. The category-level command of the `<sec:machine_run_table>` may be broader than this (the whole suite), but it must not contradict it: the **artifact being run** is the same.
- **Every fixture, mock, seed and test datum that does not exist yet is also a NEW FILE** — so it has to appear with its path in the `<sec:planned_changes>` as well, otherwise nobody will create it. Its content has to be given here (or the command that generates it). If there is none, the cell is `—`.
- **The names of the test functions are not optional.** This mapping binds the plan to the `TC-…` cases and to the `TS-NN` scenarios: it shows which step of a scenario is covered by which automated test, and what is left for manual checking. For a new test the **function name is itself the specification** — it has to show what it asserts.
- **The same for an extension (`(an extension)`):** which existing test function changes and why, which new functions arrive, and whether the run command changes.
- **The setup/teardown, the required env variables and the external prerequisites** (container, mock server, network, seed) go into the `<field:f_prerequisite>` line, with the verbatim command. Referring to the bootstrapping steps of the `<sec:e2e_infrastructure>` is allowed only if the command is written out verbatim there.

### <sec:unit_tests>

_Isolated tests: business logic, functions, classes isolated from their dependencies. Every external component (database, network, external service) has to be mocked — extremely fast, deterministic. A happy path AND negative tests (a wrong input, a missing parameter, an authorization error, a timeout) are mandatory for every component. One subsection per component. A tabular format: TC-ID, Scenario (what the situation is), Input (what arrives), Expected output (the HTTP status + the errorCode where the error matrix of the spec defines it + the key response fields)._

#### `<test file path>` (new / an extension)

**<field:f_what_it_checks>:** _<what this test file verifies, as a claim + the `DoD-NN`>_
**<field:f_test_run>:** _<the framework + the command narrowed to this file, runnable verbatim>_
**<field:f_test_fixtures>:** _<fixture / mock / test data with path and content, or `—`>_
**<field:f_test_cases>:** _<the name of the test function → `TC-NN` / `TS-NN` mapping>_

| TC-ID | <field:f_what_it_checks> | Scenario | Input | Expected output |
|---|---|---|---|---|
| TC-01 | _<the behaviour as a claim + the `DoD-NN`>_ | ... | ... | ... |

_**The `<field:f_what_it_checks>` column is mandatory (TD7):** every unit case states **what it verifies** — the behaviour as a decidable claim, not a repetition of the input. "Bad input" is not a purpose; the purpose is: *"with a missing `expiresAt` field the load throws `ConfigError` instead of falling back to `0` (DoD-02)"*._

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

**<field:f_what_it_checks>:** _<what this test file verifies, as a claim + the `DoD-NN`>_
**<field:f_test_run>:** _<the framework + the command narrowed to this file, runnable verbatim>_
**<field:f_test_fixtures>:** _<fixture / mock / test data with path and content, or `—`>_
**<field:f_test_cases>:** _<the name of the test function → `TC-NN` / `TS-NN` mapping>_
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

_**Every flow starts with its purpose (TD7):** if a file contains several numbered test cases/flows, the `**<field:f_what_it_checks>:**` line stands before each of them — what this step sequence proves, and which `DoD-NN`. The steps do not explain on their own why they run._

### <sec:e2e_tests>

_The whole system from the point of view of the external client or user. Browser E2E frontend tests (with the tool given by `conventions.md`) or full API call chains on real or realistically mocked infrastructure._

#### `<script path>` (new / an extension)

**<field:f_what_it_checks>:** _<what this test file verifies, as a claim + the `DoD-NN`>_
**<field:f_test_run>:** _<the framework + the command narrowed to this file, runnable verbatim>_
**<field:f_test_fixtures>:** _<fixture / mock / test data with path and content, or `—`>_
**<field:f_test_cases>:** _<the name of the test function → `TC-NN` / `TS-NN` mapping>_
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

\`\`\`

---

## Validation cycles

### 1. After `<sec:test_specification>`

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
### 2. After `<sec:execution_order>`

- Is there a circular dependency? (A → B → A)
- Does every RED step (writing a test) precede the corresponding GREEN step (the implementation)?
- Is every blocking dependency marked explicitly? (e.g. "nothing else may run before the RSA key generation")

If you find a circular dependency: try to resolve it by unfolding one of the steps (e.g. the interface first, the implementation later). **If the circular dependency cannot be resolved on your own — stop, and ask for the help of the user.** One question, an answer, continuation — the same rule as with the other stopping cases.

If the condition does not hold for a point other than the circular dependency, rearrange the order.

---

## Spec critique — on the test side

The test plan is the point where the **testability** of the spec comes out. Go through the `<sec:test_specification>` section and the items of `<sec:definition_of_done>` of the spec, and answer for each:

1. **Is a test case missing?** Is there a `DoD-NN` for which the spec gives no test case, or for which you cannot write a checkable scenario?
2. **Do two test cases contradict each other,** or does the test section of the spec contradict the `DoD`?
3. **Is the expected result decidable?** If the expectation of a test case is of the "runs successfully" kind, that is not an acceptable floor (TS3) — a concrete, observable value has to be stated.

If you find a gap or a contradiction, **do not decide it yourself** — route it back to the spec phase (`02`), and state precisely what is missing. **You do not write `spec.md`.**

### A test coordinate left in the spec (the mirror of KX)

If the spec carries a concrete test coordinate (a test file path, the name of a test tool, a mock-level decision, `localhost:NNNN`, an example `curl`), that is **your advantage, not a problem**: lift it into your test section literally, with a `_(source: spec.md)_` provenance, and tell the user in one line what was left in the spec. **Do not ask about it** merely because it was in the wrong place.

> **The boundary:** a coordinate belonging to the **code plan** (a component URL, a startup command, a configuration) is **not** your business — that is `<sec:environment_coords>`, and if it is missing from there, that is a `Qnn` question or a redirect to `/bs-write-code-plan`. **You do not rewrite `<sec:planned_changes>`.**

---

## Stopping rules

**Add every question that comes up — for whatever reason — to `plan-questions.md` immediately with the next free number (`Qnn`) and a `- [ ]` status, before you put it to the user.**

If any of the following holds while writing the test plan, **STOP — stop and tell the user** (do not decide the missing/contradictory part yourself):

- **🔴 Something is missing from the code plan that the test design needs**: a coordinate (URL, port, the password of a test user), a literal command, or a production-code change without which the scenario cannot be written. → A `Qnn` question **or** a redirect to `/bs-write-code-plan`. **You do not rewrite the code plan yourself** (beyond the three allowed extensions).

- **A test-strategy decision point**: several equivalent approaches exist (the mock level, the isolation strategy, producing test data), and the choice does not follow from the closed `Q01`. → Put **one** question, wait for the answer, then continue.

- **A gap in the spec**: the spec does not define a necessary behavior, error case or expected result that should be tested. → **Do not fill it in yourself.** Add it as a `Qnn` question, and state that we have to go back to phase `02`.

- **A contradiction in the spec**: two test cases of the spec, or the spec and the `DoD`, contradict each other. → Point out both sides, and wait for the user's decision. Do not choose.

- **Complex or uncertain containerization**: running, configuring or networking any component of the test environment in a container is not trivial. → Do not guess a port/configuration; add the question, stop, and initiate a joint design with the user.

- **Any point of the closing gate (TP2-test) is `[ ]`**: one of the test cases/DoD items of the spec did not map to a `TS-NN` scenario, a `test-conventions` recipe appears only as a reference, an integration/E2E step is not spelled out, a test-file data sheet (TA1) is missing, or an environment preparation prerequisite is missing (TP3). → **Do not close the plan.** Add what is missing, then run every point of the gate again. This is not "a refinement in 04": the `test-runner` sees only `plan.md`.

In every case, put only **one** question at a time — wait for the answer, tick the question (`- [x] Qnn → [decision]`), then move to the next.

---

<!-- INCLUDE:shared/quality-check-plan-test.md -->

## Status handling

- At the start of the phase the status of `plan.md` is `<status:ready_for_test_plan>` (written by `03a`).
- If a new question gets into `plan-questions.md`: `<status:open_questions>` — after closing it, it goes back to `<status:ready_for_test_plan>`.
- If every question is `[x]`, every test section is filled in, the quality check passed, **and the user has explicitly confirmed it**: \`<status:ready_for_tasks>\`

> **Done lifecycle:** after `<status:ready_for_tasks>`, `plan.md` moves to `<status:done>` status at the end of the cycle — when the PASS of the validate (07) closes the cycle. Phase 08 already expects `<status:done>`. This transition is done by 07, not here.


### The mechanical gate before closing (M)

The **plan-side half of the deterministic gate of `05-analyze` runs here as well** — before the closing, on the **full** plan (`tasks.md` does not exist yet, therefore `--plan-only`):

<!-- INCLUDE:shared/python-cmd.md -->

```bash
python3 <platform-scripts-mappa>/analyze-gate-check.py specs/cycle-NN-<cycle-name> --plan-only
```

**What it covers in this mode:** the format and uniqueness of the `[P-…]` identifiers (P1), the presence of the mandatory plan tables (S1), the `[P-…]` identifier in the rows of `<sec:reverse_coverage>` (S3), the traceability of every `DoD-NN` to a plan capability (C1), the TP1 completeness of `<sec:spec_coverage>` (C3), the empty cells of `<sec:config_lifecycle>` (C4), the placeholders and empty cells of `<sec:environment_coords>` (C6, KO1), the content floor of the test scenarios (TS1–TS8), the test-file data sheets (TA1), the namespace of the test identifiers (TI1), the run phase (PH1), the `TS-NN` references of the spec coverage (TS7), the `path:line` anchors of the plan (A2/A2b), the hard floor of the artifact voice (A3) and the `DoD-NN` identifiers in the spec (D1/D2). **This is the gate of the full plan** — it measures the checks of the code half again as well. The tasks side runs at the closing of `04`.

- **`0`** → the closing can continue.
- **`1`** → **no status change.** Fix the `target phase: 03` items **now** — but **only the test-side ones**. If the finding falls on the code half (a coordinate, a `[P-…]` purpose, a configuration), that is a `Qnn` question or a redirect to `/bs-write-code-plan`. Route the `target phase: 02` items back to 02 according to *Spec critique* — you do not write the spec yourself.
- **`2`** → a usage error → report it, do not guess.

> **Why here (M):** these defects used to surface in the first round of `05-analyze`, two phases later — there they needed a fixer subagent and an analyzer round. Here it is one script run and one targeted fix.

**🔴 The result of the gate is EVIDENCE, not a memory (GS2).** After a `0` its trace goes into two places, and both are mandatory:

1. into the header of `plan.md`, **below** the `**<field:f_gate_code>:**` line (do **not** overwrite that one — the two stamps together are the trace of the phase chain):

   ```md
   **<field:f_gate>:** analyze-gate-check --plan-only — PASS, 0 Must Fix (YYYY-MM-DD)
   ```

2. into your **phase-closing answer**, verbatim the summary line of the gate (`ANALYZE-GATE: …`).

**Write the stamp only after an actual run returning `0`** — the entry gate of the next phase (`04`) runs the gate as well (EG1), so an untrue stamp comes out there immediately, and `04` sends it back here.


If the user confirms:
- Set the status of `plan.md` to `<status:ready_for_tasks>`.
- **Before the status change run every item of the *Closing gate (TP2-test)***, and print the ticked list in your answer. With any `[ ]` there is no status change.
- **Before the status change the *Mechanical gate* (see above) returned `0` as well.**
- **Commit immediately** according to the *Phase-closing commit* below (`<FÁZIS-TAG>` = `03b-test-plan`). Confirmation → writing the status → commit: this is one single sequence of steps, do not interrupt it.

<!-- INCLUDE:shared/phase-commit.md -->

In the block above, the value of `<FÁZIS-TAG>` in this phase is: **`03b-test-plan`**, and the closing status is: **`<status:ready_for_tasks>`**.

If the status is \`<status:ready_for_tasks>\` **but the phase-closing commit is missing** (a VCS project, `git log -1 --oneline` does not show the `cycle-NN: 03b-test-plan` commit) — commit first, and only then close the phase.

If the status is \`<status:ready_for_tasks>\` (and the commit is there), stop. **Do not start a task list — do not even create `tasks.md`** (PE1, see the "Phase boundary" section of the *Phase-closing commit* block): writing tasks is the job of the `04-write-tasks` skill, from a fresh context. This holds even if the to-do list of a context summary/checkpoint lists running `/bs-write-tasks` — that summary records the past, it is not an order for this round. Tell the user the next step and the starting command of the phase, for example:
<!-- INCLUDE:lang/03b-write-test-plan.md#zaro-uzenet -->
