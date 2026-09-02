---
phase: 07
name: bs-validate
description: "berkispec - 07. Use it after the implementation (Phase 07), when tasks.md is 'Ready for validation'. Test, lint and build verification AND code review in a single self-healing loop (test-runner, reviewer, implement-fixer, review-fixer subagents). It creates 'validation-report.md' and 'code-review.md'; on PASS it sets the status of spec.md/plan.md/tasks.md to 'Done'."
prerequisites:
  - "specs/cycle-NN-<name>/tasks.md status: <status:ready_for_validate>"
output:
  - "specs/cycle-NN-<name>/test-report/validation-report.md — the complete validation report (a step log per round + # Validation History), append-only"
  - "specs/cycle-NN-<name>/test-report/code-review.md — the findings of the reviewer (Must Fix / Suggestions), updated per round"
  - "specs/cycle-NN-<name>/test-report/validate/round-NN/ — in a separate folder per round, the report artifacts mandated by the `## <sec:cv_test_reporting>` table of conventions.md (the TR3 gate)"
  - "On PASS: spec.md / plan.md / tasks.md status: <status:done>"
prev: bs-implement
next: bs-doc-sync
subagents:
  - "agents/test-runner.md"
  - "agents/reviewer.md"
  - "agents/implement-fixer.md"
  - "agents/review-fixer.md"
scripts:
  - "scripts/round-log.py — opening/closing the `## <sec:round> N` block + the round-NN folder (VD9, TR5)"
  - "scripts/run-tests.py — running the tests from the machine-readable table of the plan, with machine counts (TR1/TR2)"
  - "scripts/sonar-gate.py — the Sonar Quality Gate from the API (with the QG1 distinction)"
  - "scripts/dod-check.py — the DoD ↔ evidence join (DI1)"
  - "scripts/test-substance-check.py — the vacuous test-body (TB1) and selector-existence (TB2) gate"
  - "scripts/validate-gate-check.py — the status/task/DoD/IP1/review/round-block/CK1 collective gate"
  - "scripts/contract-guard.py — the VD3a contract integrity gate"
  - "scripts/report-gate-check.py — the TR3 report gate"
  - "scripts/failure-counter.py — the run log and the stopping limits (VD4)"
shared:
  - "shared/review-checklist.md"
  - "shared/input-from-prev.md"
  - "shared/phase-commit.md"
---
# 07 — Validation and code review
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

We develop software in spec driven development. The development is split into cycles. Every cycle is an independently developable, independently testable subunit of the complete implementation.

This is **phase 7 (0–9)** of the process: 0-init · 1-cycles · 2-spec · 3-plan · 4-tasks · 5-analyze · 6-implement · **7-validate (tests + review) ←** · 8-doc-sync · 9-merge.

---

## Input

The input of the prompt is the folder of the cycle (e.g. `specs/cycle-NN-<cycle-name>`). You find the files needed for the validation (`spec.md`, `plan.md`, `tasks.md`) in this folder.

## <field:f_prerequisite>

0. **Identifying the cycle:** if the user gave a cycle/file, use that; otherwise offer the most recent `specs/cycle-*` folder for confirmation — <!-- INCLUDE:lang/common.md#ciklus-beazonositas --> — and wait for the answer before moving on.

1. **`conventions.md` existence check:** read `conventions.md` in the root of the project. If it does not exist, STOP — they should return to phase `00`.

2. **Working-tree check (only with VCS):** run `git status --short`. (In a No-VCS project it is skipped.)
   - **First look at the status of `tasks.md`.** If it bears a `[validate-loop]` marker, an earlier loop was interrupted: the uncommitted changes in the folder of the cycle (the DoD ticks of `spec.md`, the fixing tasks of `tasks.md`, `test-report/`) are the **own, not yet committed state of the loop** (VD8 — there is no intermediate commit during the loop). In that case **do not offer them for a commit** and do not ask — say in one line that you are continuing an interrupted loop, and go to point 4 of "Handling an interrupted run".
   - Otherwise, if there are uncommitted changes, list them, and ask in one round whether I should commit now or continue — wait for the answer.

3. **The prerequisite gate — with a script, not by reading files.** The three statuses, the `[validate-loop]` marker and the open `validate-input-from-prev.md` items all come out of a single call:

   ```bash
   python3 <platform-scripts-mappa>/validate-gate-check.py \
     specs/cycle-NN-<cycle-name> --stage start
   ```

   - **`exit 0`** → the validation can go.
   - **`exit 1`** → according to the ✗ points printed:
     - **the status of `tasks.md` is not `<status:ready_for_validate>`** → the implementation is not closed yet: report it, and return to phase `06`;
     - **the status of `plan.md` / `spec.md` is not acceptable** (acceptable: `plan.md` → `<status:ready_for_tasks>` or `<status:done>`; `spec.md` → `<status:ready_for_plan>` or `<status:done>`) → if either is reset to `<status:draft>`, tell the user: a decision was made in an earlier phase that requires a sync.
   - `<status:done>` is **normal** for both of them if we came back here after `08-doc-sync` (or the doc-sync re-run before `09-merge`).
   - The `·` lines of the script are INFO (the marker of an interrupted loop, open `input-from-prev` items) — process these, but they do not stop you.

4. **Selector gate (TB2) — at the START of the round.** An orphaned `[CHECK]` selector (`06` renamed a test function, the task's command still carries the old name) should surface at the **start** of the round, not at the end:

   ```bash
   python3 <platform-scripts-mappa>/test-substance-check.py \
     specs/cycle-NN-<cycle-name> --selectors-only
   ```

   - **`exit 0`** → carry on;
   - **`exit 1`** → `tasks.md` and the code have **drifted apart**: the `[CHECK]` commands listed would fail on execution, with no judgment involved. Fix the `tasks.md` command to the actual test name (this is not a substantive change, it does not violate `VD3`), **or** — if the test was never written at all — back to `06`: the `[RED]`/`[GREEN]` task is not done.

   `--selectors-only` deliberately runs **only** `TB2`: the `TB1` vacuous check makes sense at closing time (the A/2 + B block), when the tests are already written.

---

## An early check of repeated failures

**Before you run anything:** if `specs/cycle-NN-<cycle-name>/test-report/validation-report.md` exists, query the state of the log with the **read-only** mode of the script — **do not read/parse it by hand** (from the old, outdated entries a false alarm is born):

<!-- INCLUDE:shared/python-cmd.md -->

```bash
python3 <platform-scripts-mappa>/failure-counter.py \
  specs/cycle-NN-<cycle-name>/test-report/validation-report.md --status
```

The `--status` prints the entry of the **last** run and the counters belonging to it (consecutive failures / total failures / consecutive FAIL runs) — always the current state, not an old point of the log. If the last run is a FAIL, and any counter is **one below its threshold** (2/3, 4/5, 4/5), this is a **warning signal, not a stopping point**: write into your answer in one line that *"Attention: [Failed Item] has already failed [N] times — if it fails now as well, the stopping limit takes effect and I will ask for human intervention."*, then **continue** the validation (this is NOT a question, do NOT wait for an answer). The actual stopping is always decided by the **exit code** of the logging run (see "Logging and stopping limits"), not by this preliminary look.

---

## What you have to do

Check that the implementation of the cycle is complete, correct **and has passed the review**. The validation is based on **four** sources:

1. **`spec.md` — <sec:definition_of_done>**: is every item fulfilled?
2. **`plan.md` — <sec:testing_strategy>**: does every prescribed test run and pass?
3. **`tasks.md`**: is every task in `[x]` status?
4. **The `reviewer` subagent — the code review (RV1)**: did any unclosed `<status:must_fix>` finding remain in the diff of the cycle?

**Your role is a deterministic checker until a PASS, and an orchestrator in case of a FAIL.** If the validation finds a FAIL — be it a test/Sonar/DoD or a review finding —, you do **not** simply hand control back to the user ("run 06 again"), but **conduct a self-healing loop** (a fixer subagent → the contract integrity gate → a re-validation), until there is a PASS — up to the limit of the **three stopping limits** (per item 3 consecutive / 5 total failures, and 5 consecutive FAIL runs), **escalating upwards** in case of a design error. The fixing is not done by you: for a test/Sonar/DoD failure the `agents/implement-fixer.md`, for a review finding the `agents/review-fixer.md` subagent (both = the Fix mode of 06). See "The self-healing loop (the orchestrator loop)".

> **Why one phase (RV1)?** A review fix **may break a test**, therefore after the fix everything has to be tested again anyway — this used to be the own "re-validate" branch of `09`, repeating the whole machinery of 07. In one loop, the review is simply **step 2 of the full round** (half of the static layer, next to Sonar): it only runs if the fast tests are green, and its findings go into the same log, with the same stopping limits. This way `09` is only the merge.

---

> **The cost principle (VD10/VD11/VD12):** the phase is about the **evidence**, the **acceptance criteria** and the **code quality**. It is not documentation (that is `08`), not the merge (that is `09`), and it does not run everything in every round (see "Round types" — the review also only runs in a full round, after green tests). If something is not needed for the PASS/FAIL decision, it does not belong into this phase.

---

## Handling an interrupted run

The validation may be interrupted at any time. At a restart (a repeated run):
1. **An idempotent run**: start the validation steps from the beginning — **the first round of the continuation is always a FULL round** (VD10), because you cannot know what ran intact before the interruption. If the earlier run already logged something into `test-report/validation-report.md`, that is to be considered the previous (interrupted) run: **read the last `## <sec:round> N` block** — from this you see how far it got (which steps ran, what failed, whether a fixer was started). Do **not overwrite** the interrupted round: close its block with a `**Interrupted** — the run was interrupted here` line, and the new round gets a new `## <sec:round> N+1` block. **You do not delete and do not reuse the report folder of the interrupted round (`validate/round-N/`) either** — the new round gets a new folder (`round-N+1`), so that the partial and the complete evidence do not get mixed (TR5).
2. **Stuck resources**: if you experience a port conflict because of test containers or processes stuck from the earlier interrupted run, kill them, or find a new free port in the way described earlier.
3. **Avoiding duplicated tasks**: if the run ends with a FAIL, and you have to add fixing tasks into the `## <sec:validation_fixes>` / `## <sec:review_fixes>` section of `tasks.md`, always check whether the concrete test failure, Sonar fix or `MF-NN` finding does not already appear as an unfinished task (because of an earlier interrupted validation). If it is already there, do not add it twice.

3/b. **The partial findings of an interrupted diagnostician run (RV-INC):** if the previous round was interrupted **during the run of a diagnostician subagent** (`reviewer`, `test-runner`, `analyzer`), the work the subagent had already carried out is typically **not on disk in its entirety** — it writes its report during the run, not with a single closing operation. Before you restart it in the new round:
   - **Look at the partial artifact.** The `reviewer` writes incrementally (RV-INC): if `<field:f_status>` = `<status:in_progress>` stands in the header of `test-report/code-review.md`, the findings in it are real, only incomplete — **do not discard them and do not overwrite them**.
   - **Ask the user in one line:** *"Is there any partial finding known from the interrupted `<subagent>` run (from the log or the transcript of the platform) that I should hand over to the new run?"*
   - Hand the entries you receive **and** the findings of the partial artifact over in the input of the new subagent as an **"entries to verify"** block — not as finished findings, but as targeted verification points.

   **Guard:** if there is no such partial finding, continue — this is not an error. Without them, however, the new run **starts blind**, and may overlook an error that was already proven.

4. **Recognizing an interrupted self-healing loop (the `[validate-loop]` marker + <sec:validation_history>):** if the status of `tasks.md` bears a `<status:ready_for_implement> [validate-loop]` marker, an earlier validate loop was interrupted — do **not** start with a clean slate. Find out the state of the loop:
   - Query the state of the log: `failure-counter.py <validation-report.md> --status` — this gives the last run, the stuck items and the counters (which attempt it was at). Do not parse it by hand.
   - Read the `## <sec:validation_fixes>` **and** the `## <sec:review_fixes>` section of `tasks.md`: are there still unfinished `[ ]` fixing tasks?
     - **If yes** (the fixer did not run or was interrupted): continue the loop by restarting the appropriate fixer on these tasks (validation → `implement-fixer`, review → `review-fixer`), then re-validate.
     - **If not** (the fixer finished, but the re-validation was left out): run the validation steps again, and evaluate the result according to the loop.
   - The counters are the basis of the stopping limits — at a continuation the script automatically counts on from there (the log is the memory). **Do not zero it, do not rewrite the `# <sec:validation_history>` by hand.**

---

## Context loading rules

> **🔴 The basic principle (VD11/b): if there is a script for it, do not read a file.** For the deterministic questions of the phase (statuses, open tasks/DoD ticks, round blocks, report artifacts, the Sonar gate, the diff of the protected paths, test counts) there **is a script for all of them** — their output is your input, not the content of the files. The raw test log, `sonar-report.md` and the `git diff` should **never** get into the main context, unless a gate explicitly directs you there.

- Read the `spec.md` <sec:definition_of_done> section.
- **Do NOT read `plan.md` into the main context (VD11).** The cycle-specific runtime source of truth is the input of the `test-runner` subagent — it reads the `<sec:testing_strategy>` / `<sec:regression_impact>` / `<sec:e2e_infrastructure>` sections of the plan, not you. The input of the main agent is the **report of the runner**. Two exceptions, both **targeted** (`Grep`, not a full read):
  - checking a plan deficiency (TR4): `grep -n "<the keyword the runner missed>" specs/cycle-NN-<cycle-name>/plan.md` — you only look at the context of the hit;
  - reading out the `<sec:regression_impact>` table for the closing round, if the runner did not return it.
  _Why: `plan.md` is several hundred lines, and in the main context it is resent in every further round — this is one of the largest, completely needless token costs of this phase._
- Read `tasks.md`.
- **Read `code-review.md` only if the review has already run** in this phase — and even then only the `<status:must_fix>` section. The full finding text is the input of the `review-fixer`, not yours.
- **Read `validate-input-from-prev.md`, if it exists** — see the "Handover between phases" section.
- Do not read the whole source code — only what is needed for a concrete check.

---

## Handover between phases (`*-input-from-prev.md`) — IP1

**What you READ:** if `specs/cycle-NN-<cycle-name>/validate-input-from-prev.md` exists, read it **before starting** the validation. It contains the runtime prerequisites and operational notes that came to light in phase 03/04 (e.g. "a VPN is needed before starting the stack", "this test can only be run after the seed step", "the port conflicts with the developer stack"). These typically **prevent** a test failure if you take them into account — therefore process them **before** starting the `test-runner`, and **hand the relevant items over in the input of the subagent**.

Close every `[ ]` item: either you took it into account during the validation (`→ taken into account: <how>`), or it is explicitly dropped with a justification (`→ dropped: <why>`). **Guard:** if the file does not exist, that is not an error — continue.

**What you MAY WRITE INTO:** nothing — 07 is the **end** of the chain. If a lasting piece of knowledge comes to light during the validation that will be needed in the **following cycles** as well, it does not belong here: it belongs into `specs/test-conventions.md`, owned by `08-doc-sync` (TC3 — suggest the promotion there, do not write it yourself).

<!-- INCLUDE:shared/input-from-prev.md -->

---

## Round types — the incremental loop (VD10)

> **Not every round is full.** Most of the cost of the loop comes from the heavy tests (the stack up/down, E2E, regression); re-running these immediately after a fix is a waste, because the fix typically targeted a single item, and often does not succeed on the first attempt.
>
> **The step order of the full round serves this too (VD13): cheap → static → expensive.** Sonar and the code review run without a stack, and fixing their findings **changes the code** — therefore both come **before** the heavy tests. The other way round, the price of every static finding would be a discarded E2E run.

| Round type | When | What runs |
|---|---|---|
| **A full round** | (a) the **first** round of the phase; (b) the **closing confirming** round | 1. the fast tests → 2. **the static layer: Sonar + the code review** (only if 1 is green) → 3. the heavy tests + the regression (only if 1–2 are green) → 4. the DoD/tasks/report gate |
| **A light round** | every round **after a fix**, until it is green | **the complete fast test set** (unit/typecheck) + **exclusively the failed item(s)** that were a heavy test, Sonar or a review finding — nothing else. For a review finding the `reviewer` runs **incrementally**, only on the open `MF-NN`s (RV2) |

**The course of the loop:**

```
round 1     FULL      → FAIL  → fix
round 2     LIGHT     → FAIL  → fix
round 3     LIGHT     → green → NOT a PASS! a mandatory confirming round
round 4     FULL      → PASS (or FAIL → the loop continues)
```

**Mandatory rules:**

1. **A PASS can only be given from a FULL round** in which the **code review also ran and is clean** (RV1). A green light round is **not** a validation — after it a full confirming round starts **immediately**, in the same run, without a fix. ("The unit tests were green, it must be fine" → forbidden.)
2. **A light round is also ONE round** (VD4a): at its end exactly one `failure-counter.py` entry is produced, with the same item names. The stopping limits (3/5/5) count unchanged.
3. **If the failure was a heavy test, Sonar or a review finding**, that **one** item has to be confirmed in the light round as well (for a review finding with the incremental run of the `reviewer`, looking only at the open `MF-NN`s), that is, it has to be run (otherwise the fix cannot be confirmed) — but only that, not the whole heavy set. Running a single E2E test case also requires bringing up the stack; if this cannot be solved partially (according to the plan only the whole set can be run), then **that round will be full** — mark it so in the report.
4. **We do not narrow the fast set.** In a light round the **complete** unit/typecheck suite runs (not only the failed test file) — it costs seconds, but it catches it if the fix broke something elsewhere. Selecting test files is not your business.
5. **The lifecycle of the stack is unchanged:** every heavy-test run is a clean start + cleanup. With the incremental loop this typically happens only 2× in a validation.
6. **Write out the type of the round** in the header of the `## <sec:round> N` block: `— FULL` or `— LIGHT`.

---

## The validation steps

### 0. Preparing the report folder — the split per round (TR5)

The `test-report/` folder is split into **two layers**, and this separation has to be kept throughout:

```
specs/cycle-NN-<cycle-name>/test-report/
├── validation-report.md      ← your report/log: spanning several rounds, APPEND-ONLY (you never overwrite it as a whole)
├── code-review.md            ← the findings of the reviewer (RV1) — written by the subagent, evaluated by you
├── implement/                ← the check log of 06 (not written by you)
│   └── check-log.md
├── validate/
│   ├── round-01/             ← ALL the artifacts of round 1 (allure/unit/coverage/sonar-report.*)
│   └── round-02/             ← those of round 2 — it NEVER overwrites those of round 1
└── review/                   ← LEGACY: it may remain from the 09-review rounds of old cycles (it is not produced in a new cycle)
```

**At the beginning of every round, create its own folder:** `specs/cycle-NN-<cycle-name>/test-report/validate/round-NN/`, where `NN` is **exactly the ordinal of the `## <sec:round> N` of `validation-report.md`**, zero-padded to two digits (`round-01`, `round-02`, …). This pairing gives the whole meaning of the phase: for a failure read from the step table, the report belonging to it can be opened immediately. **If the folder name and the `## <sec:round> N` drift apart, the log is useless** — check it when closing the round.

- **You do not delete, do not overwrite, do not clean up the folders of earlier rounds.** Every round is kept, the failed ones too — those are exactly the most valuable for tracking down an error.
- **`validation-report.md` stays in the root of `test-report/`** (not in a round folder): this is the log spanning several rounds, and `failure-counter.py` also appends here.
- **Hand the path of the round folder over to the `test-runner`** at every call — the subagent does not guess it, and if it does not get it, it asks back.

- **The list above is CLOSED (TR5/c).** Under `test-report/` **only** `validation-report.md`, `code-review.md`, `implement/`, `validate/round-NN/` and the legacy `review/` may exist. If you find anything else — especially a folder named `test-report/test-report/` or `test-report/specs/` — that is **the trace of a broken path base, not evidence: delete it**, and re-run the step with the correct base. The rule above about not deleting the folders of earlier rounds applies **exclusively to the `validate/round-NN/` folders**. The layout guard of `report-gate-check.py` measures this deterministically.

#### 0/a. The three path forms of the round folder (TR5/c)

The same folder has **three forms, with three different bases**. The most frequent mistake is copying one form into a parameter that expects the base of another — this does not produce an error message, but a recursive report tree (`test-report/test-report/…`, `test-report/specs/…`), and the evidence lands where the gate cannot find it.

| Form | Base | Where you use it |
|---|---|---|
| `specs/cycle-NN-<cycle-name>/test-report/validate/round-NN` | repo root | `run-tests.py --round-dir`, the path handed to the `test-runner`, the value of the `{round}` placeholder |
| `test-report/validate/round-NN` | cycle folder | `report-gate-check.py --report-subdir` |
| `validate/round-NN` | `test-report/` | the `<phase-dir>` placeholder or the `REPORT_PHASE_DIR`-style environment variable of the report commands in `conventions.md`, and the `{phase}` placeholder |

> **🔴 If the report-generating command of `conventions.md` asks for the phase folder through a placeholder or an environment variable, the THIRD form goes there** (`validate/round-NN`) — never the other two. `run-tests.py` prints the correct value on every run as a `REPORT_PHASE_DIR=` line: **copy that**, not the path you typed just before it.
>
> The scripts accept and normalize all three forms (they signal it with a `MEGJEGYZÉS (TR5/c)` line) — but in the machine table of `plan.md` the two placeholders (`{round}` / `{phase}`) are **not interchangeable**: `run-tests.py` checks this before the run and stops with `exit 3` on a double prefix.

**The report artifacts are part of the cycle — they do NOT have to be excluded from the diff.** The `git add specs/cycle-NN-<cycle-name>/` deliberately takes in the whole content of `test-report/`: the own report of the test tool (Allure/Playwright HTML, coverage, JUnit XML) is the only evidence about the run that can be opened afterwards. The defense against the size is the single-file HTML (`--single-file`), not the `.gitignore`. If a `test-report/.gitignore` remained from an earlier cycle that excludes the reports, **delete it** — otherwise the TR3 gate looks for a file that never gets into the repo.

**The reports are mandatory according to the `## <sec:cv_test_reporting>` table of `conventions.md` (TR3)** — the last column of the table is a path **relative to the round folder**. The list is produced by the `test-runner`, and before the PASS a deterministic gate checks it (see "The gate of the mandatory test reports").

#### 0/b. OPENING the round in `validation-report.md` (VD9 — mandatory, BEFORE starting the tests)

> **🔴 This is not an end-of-round duty, but the first step of the round.** Writing the report is not an optional side effect: `validation-report.md` is the **mandatory output of the phase**. If you skip this, `failure-counter.py` silently creates the file with the `# <sec:validation_history>` section **only** — the run looks successful, while the report is empty. This is exactly the error that VD9 forbids.

**Do not write it by hand — `round-log.py` does it.** The script creates the file (if there is none), computes the ordinal of the round, opens the `## <sec:round> N` block **before** the `# <sec:validation_history>` header, and creates the `round-NN/` folder belonging to it — this way the folder name and the round number **structurally** cannot drift apart (TR5):

```bash
python3 <platform-scripts-mappa>/round-log.py open \
  specs/cycle-NN-<cycle-name>/test-report/validation-report.md \
  --type FULL --timestamp "2026-08-10 10:32" \
  --trigger "07-validate first run"
```

- The value of `--type` is `FULL` or `LIGHT` (see "Round types"), the `--trigger` is the trigger of the round (the first run / iteration N of the loop / a confirming round / the continuation of an interrupted run).
- The last line of the output is the **`round-subdir:`** — hand this path over to `run-tests.py`, to the `test-runner` and to the report gate.
- **When continuing an interrupted run** add the `--reuse-open` flag: if the last round is still `in progress`, it does not open a new one.

**Fill the step table as you go** — one line after every run and every gate, immediately:

```bash
python3 <platform-scripts-mappa>/round-log.py step \
  specs/cycle-NN-<cycle-name>/test-report/validation-report.md \
  --step "10:34|test-runner — fast tests|npm test -- --run|✓ 43 passed / 0 failed / 0 skipped"
```

This way, even after an interrupted run, it is visible how far it got (see "Handling an interrupted run").

### 1. The fast tests — the cheapest gate (`run-tests.py`, fallback: `test-runner`)

> **The round type (VD10):** the **complete fast set runs in every round** — in a full and in a light round alike (VD10/4) —, because it costs seconds, and it catches it if a fix broke something elsewhere. **Sonar does not run here** (that is step 2).
>
> **If this step fails, the round ends here:** neither the static layer (2.) nor the heavy tests (3.) start. We do not spend a review and an E2E stack on code that is broken at the level of the unit tests.

#### 1/a. The tests — **with a script first, a subagent only if that does not work**

> **🔴 The raw test log should never get into the context.** Running and counting is machine work: this is done by `run-tests.py` from the **machine-readable run table** of `plan.md`, and it answers in 10-20 lines. The `test-runner` subagent is the **fallback**, not the base case.

```bash
python3 <platform-scripts-mappa>/run-tests.py \
  specs/cycle-NN-<cycle-name>/plan.md \
  --round-dir specs/cycle-NN-<cycle-name>/test-report/validate/round-NN \
  --type gyors --phase <status:phase_validate>
```

- **`exit 0/1`** → the output contains, per category, the **command issued** and the `X passed / Y failed / Z skipped` counts, and on a failure the **exact names** of the failed tests — these go verbatim into the `--failed-item` values of `failure-counter.py`. The machine result stays in the `results.json` of the round folder.
- **`exit 2`** → there is **no machine-readable run table** in `plan.md` (an old cycle or an incomplete plan). In that case you **fall back to the `test-runner` subagent** (see 1/b), and in the report of the round state in one line that the machine table of the plan is missing — for `08-doc-sync`/`03` this is an item to fix, but it is **not** the FAIL of the round.
- **`exit 4`** → the table has an **environment error**: a category declared non-local points at a local target (EV5). **Do not run it** — a green result would then not be about the deployed component. This is a gap of `03`: the target of the command has to be aligned with the declared environment, or the `<field:f_environment>` column corrected to `local` if it really runs there. The `implement-fixer` does not fix this (the code is not at fault) — escalate to `03` according to VD5.
- **The output also prints the ENVIRONMENT per category** (`@ dev`, `@ local`), and it goes into `results.json` too. **Carry this into the step table of the round**: it must be visible afterwards from the report where the test was green — a green JUnit XML on its own does not reveal which host it addressed.
- **`exit 3`** → the table has a **placeholder error**: the substitution produces a double path prefix (`test-report/test-report/…` or `test-report/specs/…`, TR5/c). **Do not run anything, and do NOT fall back to the `test-runner`** — the script prints which row and which field is wrong. This is a gap of `03`, not a code bug: fix the machine table of `plan.md` to the correct placeholder (`{round}` = the full path, `{phase}` = the phase folder — see 0/a), and re-run. If the fix is not unambiguous, escalate to `03` according to VD5.
- To confirm a single failed category in a light round: `--only <category>`.

> **🔴 `EV6` — traffic evidence AFTER the run.** `EV1–EV5` protect the **target** **before** the run (host in the command, a reachability probe, the `localhost` ban). `EV6` protects the **traffic** **after** the run: *a green test does not prove that any request was even issued.* In a real cycle the E2E tests meant for the dev environment issued **not a single dev request** (the test bodies were empty shells), yet the round's `rest-logs` folder looked full — with 50 log files that were all `127.0.0.1` entries inherited from an earlier round.
>
> So, for every category with a non-local `<field:f_environment>`, the script checks whether any of the **audit artifacts** declared in the `## <sec:cv_test_reporting>` (TR3) table of `conventions.md` **(a)** came into being during the round and **(b)** contains the target host. On failure the category is a `FAIL` (it goes into `results.json` too) — and the fix is **not** copying a log in, but making the test actually address the target environment (`VD3`).
>
> **Cautious branch:** if the TR3 table declares **no** audit artifact, `EV6` is only a **suggestion** (a `·` line, under the `suggestions` key of `results.json`) — not every project takes on a REST audit log, and we do not fail a project for something it never signed up for. The default for `--conventions` is the `conventions.md` at the repo root; if it does not exist, the check is skipped.

#### 1/b. The fallback: the `test-runner` subagent

If `run-tests.py` returned `exit 2` (there is no machine table), call the `test-runner` subagent (`agents/test-runner.md`) to run the fast (unit/integration) tests. The subagent returns a **structured summary** (see the contract of the agent) — you do not ask for the raw test log back.

> **🔴 If the subagent returns with a `## Run blocked (EX1)` section** — on some platforms (e.g. Antigravity) the subagent **cannot ask for command approval**, therefore it cannot run a test —, then:
> 1. **Do not restart** the subagent, and **do not accept** any estimated result of it (there will not even be one in the report).
> 2. **Run `run-tests.py` yourself**: as the main agent, approval works for you. On that platform this is the **only** working path, which is why the machine-readable run table of `plan.md` is not optional there.
> 3. **If the table is missing as well** (`exit 2`) **and** the subagent is blocked too: the tests cannot be run automatically on this platform → **STOP + human** with the "Where we are" header: *"The tests cannot be run: there is no machine-readable run table in `plan.md`, and the `test-runner` subagent cannot run a command on this platform (EX1). Two solutions: (a) let us complete `plan.md` with the machine table in phase 03, or (b) allow the necessary commands on the auto-run list of the platform."* **Never close the round as a PASS without a run.**

> **🔴 In the call you must hand over the report folder of the round** (TR5): `specs/cycle-NN-<cycle-name>/test-report/validate/round-NN/` — with the ordinal of the current `## <sec:round> N`. The subagent puts every artifact (including `sonar-report.md`/`.html`) here. Hand over as well **which categories** it runs in this round, so that in a light round it does not generate a misleading report for the categories that did not run.

**The subagent works from two sources and nothing else (TR4):** it takes every **cycle-specific** technical detail (commands, URLs, ports, test users, obtaining a token, the start order, the prerequisites) from the `<sec:testing_strategy>` / `<sec:regression_impact>` / `<sec:e2e_infrastructure>` sections of **`plan.md`** — this is why phase 03 wrote the plan **self-containedly** by obligation (TC1/a) —, and the **project-level tool information** (the runner, the folder structure, the report table, the Sonar commands) from `conventions.md`. It does **not read** `test-conventions.md`, it does not work from old cycles, and it does **not guess**. At the start, **reference it explicitly** that the plan is the cycle-specific source of truth.

**Evidence check (TR1/TR2):** `run-tests.py` fulfills this **automatically** (it gives the command and the counts from a machine source, and it marks the `0 passed / 0 failed` case as a FAIL by itself — `TR2`). The rules below apply to the **fallback branch** (the `test-runner` subagent): for every category the **command issued** and the **counts** (`X passed / Y failed / Z skipped`) have to be there. If the evidence is missing for a category, or `0 passed / 0 failed` appears, do **not accept it as a PASS**:
- If, according to the Testing strategy of `plan.md`, that category should exist → this is a **FAIL** (`--failed-item "<category>: 0 tests ran"`), not a green result.
- If, according to the plan, the category deliberately does not exist → `N/A`, and write this out into the step table of the round as well.
- If the subagent reported without evidence, **ask it again** for the missing datum before you decide. Your own assumption does not substitute for the run.

**Handling a plan deficiency (TR4) — it is not a code bug, do not start a fixer on it.** If the `## Plan deficiency (TR4)` section of the report is not empty (the runner left out a test group because a runtime detail is not in `plan.md` — e.g. starting the local Keycloak is not described, the test user or obtaining the token is missing):

1. **Look in `plan.md` yourself** — the runner may have been wrong, or it may be in another section. If it is there, hand it over to it explicitly, and run that group again.
2. **If it really is missing:** this is a deficiency of **phase 03**, not of the implementation. The `implement-fixer` cannot fix this (the code is not the fault), therefore **do not start a loop iteration on it**. Instead, **escalate to the design** according to the VD5 branch escaping upwards: the status of `plan.md` to `<status:draft>`, a single closing commit, and in the message to the user **list item by item what is missing** and for which test:
   > **[VALIDATE · plan deficiency · <test> ]**
   > *"`<test group>` cannot be run: `plan.md` does not contain `<the missing datum>` (e.g. the start command of the local Keycloak and the data of the test user). This is a design deficiency, not a code error — the `test-runner` deliberately does not guess. I have reset the status of `plan.md`; complete the `<sec:testing_strategy>` section self-containedly (TC1/a), then we return here along the `05→06→07` path."*
3. **Log the result of the test groups that did run regardless** into the report of the round — the round is a FAIL, and the skipped group appears in the step table as a "<status:skipped> — plan deficiency" line.

### 2. The static layer — Sonar + the code review in one batch (RV1/RV2/VD13)

> **Why here, BEFORE the heavy tests (VD13)?** Sonar and the review are the only two checks that **do not require a running stack** — and both find errors whose fixing **changes the code**. If the heavy tests (E2E + regression) ran first, the price of every static finding would be a discarded E2E run: after the fix the stack has to be brought up again anyway. Most of the cost of the loop comes exactly from this (VD10), therefore the order is: **cheap → static → expensive**.
>
> **The round type (VD10/RV2):** in a **full** round both run. In a **light** round only the one(s) that were the source of the failure to be confirmed:
> - a Sonar-originated failure (`Sonar QG: …`) → Sonar runs again, the review does not;
> - a review finding (`MF-NN`) → the `reviewer` runs **incrementally**, exclusively on the open `MF-NN` findings (a re-review of the whole diff is forbidden);
> - otherwise the step **is left out**, and a `<status:skipped>` — light round (VD10)` line goes into the step table.
>
> **You evaluate the result of the two checks TOGETHER** — see point 2/c. Do not start a fixer on the findings of Sonar until the review has also run in the same round.

#### 2/a. The Sonar Quality Gate — `sonar-gate.py` (do not read a report)

If `conventions.md` contains a `## <sec:cv_sonar>` section, after running the analysis the gate is evaluated by the script — `sonar-report.md`/`.html` stays as evidence, but you **do not read it**:

```bash
python3 <platform-scripts-mappa>/sonar-gate.py \
  --out specs/cycle-NN-<cycle-name>/test-report/validate/round-NN/sonar-report.md
```

The exit code decides, not your own judgement:
- **`0`** → the Quality Gate is OK (the `MINOR`/`INFO` hits do not block);
- **`1`** → QG FAIL **because of a finding** — the printed `BLOCKER`/`CRITICAL`/`MAJOR` list is the source of the fixing tasks (the filtering has already happened, you do not have to do it);
- **`3`** → QG FAIL **because of a threshold, without a blocking finding** — this is the **QG1 branch** (see below): starting a fixer with an empty failure list is forbidden;
- **`2`** → a usage error (there is no URL/projectKey/token) → the Sonar run goes through the `test-runner` subagent, the old way.

> **Give a separate instruction about Sonar** — the subagent does not guess: if you do not tell it, it **runs it**. In a light round, therefore, write out explicitly that *"Sonar: skipped in this round"* (unless you are confirming a Sonar-originated failure — then *"Sonar: should run"*). In the report `skipped (at the request of the caller)` then stands, which is **not** a PASS and **not** an N/A: when evaluating the round do not qualify it as green, and do not add a fixing task for it either.

Based on the report of the subagent:
- **Quality Gate PASS / N/A:** the informative `MINOR`/`INFO` hits of the `sonar-report.html` and `.md` reports that got into the round folder do not obstruct the validation.
- **Quality Gate FAIL or any fast test FAIL:** **do not start step 3 (the heavy tests)** — the result of the round is a FAIL, move on to the logging, then to the FAIL branch of the loop. When adding the fixing tasks (`tasks.md`), consider only the `BLOCKER`, `CRITICAL` and `MAJOR` level Sonar hits as obstacles that must be fixed (the subagent reports all of them, the filtering happens here, at you).
- **Quality Gate FAIL, but there is no `BLOCKER`/`CRITICAL`/`MAJOR` hit (QG1 — the `exit 3` of `sonar-gate.py`):** the gate was failed not by a finding but by a **threshold** (coverage, duplication, the quality gate on new code) — the script prints which condition and with what value. In that case starting a fixer with an empty failure list is **forbidden** — the loop would spin idle. What to do:
  - If the failed condition is unambiguous from `sonar-report.md` and it **can be fixed on the code side** (typically: missing test coverage on the new code) → add it as a concrete fixing task (e.g. *"Cover the new branches of `<file>` with tests — the coverage threshold of the QG is below X%"*), and let the name of the `--failed-item` be the failed condition (e.g. `Sonar QG: coverage on new code`).
  - If the failed condition **cannot be fixed within the scope of the cycle** (e.g. inherited duplication, a project-level threshold) → this is not a code bug: **STOP + human**, with the *"Where we are"* header, naming the failed condition and with two suggestions (reviewing the threshold in `conventions.md`, or a separate cycle). Do not start a fixer.

#### 2/b. The code review — the `reviewer` subagent (RV1)

> The review runs **after the fast tests but before the heavy tests**: the diff compiles by then and is green at unit level, so we are not looking at half-finished code, while its findings can still be fixed before we ran anything expensive on it.

1. **Start the `reviewer` subagent** (the `agents/reviewer.md` system prompt), handing over to it:
   - the `git diff` between the cycle branch and the main branch (against the target branch named in the Merge strategy of `conventions.md`) — **you run the diff and hand it over**, do not entrust it to the subagent: on several platforms it cannot run a command (EX1). **Narrow the diff down to the source code (RV-SC)** — this is one of the largest token items of the phase:
     ```
     git diff <target>...HEAD -- . ':(exclude)specs/**' ':(exclude)*.lock' ':(exclude)package-lock.json'
     ```
     Extend it with the directories named as **generated** in `conventions.md` (typically `dist/`, `build/`, `docs-generated/`). The reason: reviewing the diff of the design documents is **pure duplication** — the reviewer receives `spec.md` and `plan.md` **as complete files, separately** anyway, and measures the "spec deviation" judgement against their **current** content, not against their change; while generated output and lock files are not subjects of a review. **Do NOT exclude the tests** — reviewing the test code is among the most valuable parts (a missing mock stub, for instance, is only visible there).
   - `conventions.md`, `plan.md` and `spec.md`,
   - **if there has already been a review in this phase:** the previous `test-report/code-review.md`, with the explicit request to focus on the `<status:must_fix>` findings that are **still open**, and to mark the closed ones as closed (an incremental re-review — it should not rewrite the report from scratch).
2. The subagent saves the report into the **`specs/cycle-NN-<cycle-name>/test-report/code-review.md`** file.
   > **If the subagent does not run, or does not produce a `code-review.md`:** this is **not** a code bug, therefore you do **not** start a fixer. The **type of the error** decides what to do — do not deliberate, look at the text of the error message:
   > - **A platform limit** (the text mentions a quota/allowance/limit — e.g. "usage limit", "quota exceeded", "reached its usage limit", or an allowance reset date): **do NOT retry.** The second call runs deterministically into the same thing, and wastes a round. Jump straight to the STOP + human branch, and **copy the error message verbatim** into the question (together with the reset date) — the decision (an admin permission, waiting for the reset, another model pool) belongs to the user, not to you.
   > - **Every other error** (a timeout, a one-off crash, an empty answer): retry **once**.
   >
   > If the subagent cannot be run even so: **STOP + human** with the "Where we are" header — ask whether I should retry it, or carry out the review directly according to the aspects of `reviewer.md` in the main agent.
   >
   > **🔴 If you go down the fallback branch (the review is produced in the main agent), marking the origin of the report is MANDATORY.** The fallback runs on a different model and in a narrower context than the `reviewer` subagent, therefore it is systematically a weaker finding set — whoever reads the report later must see this:
   > - one line into the header of `code-review.md`: **Produced by:** the main agent (fallback) — the reviewer subagent could not be run: <reason>;
   > - in the step table of the round the name of the step should be `code review (2/b, RV1) — fallback: the main agent`, **never** `reviewer subagent`;
   > - write into the `## <sec:closing_summary>` section that making up for the subagent review is recommended;
   > - and a **second mandatory line** in the header: **Criteria list:** `RV-FB1` — all <N> points walked through (or the omitted point named, with a justification). Without this, the rigor of the fallback is once again self-declaration (`7/j`).

   > **🔴 In fallback mode you must walk through THE SAME list, point by point (RV-FB1).** The fallback is not "a quick diff summary": the `reviewer` subagent's criteria list is **verbatim** below, and in a fallback **you** are the reviewer. Go through **every** point, and name in `code-review.md` where it is met and where it is not — especially at the **Test coverage** point: in a real cycle it was precisely the fallback branch that ran, and precisely this point that was skipped, which is why it never came to light that the "written" tests were empty shells (`assert True`). Marking the fallback (above) records the **origin**; it does not license lower rigor.

<!-- INCLUDE:shared/review-checklist.md -->

3. **Evaluate the report:**
   - **`<field:f_status>` = `<status:in_progress>` in the header** → the reviewer **did not finish** the report (an interrupted run — RV-INC). The review gate **cannot be closed with it**: neither to green, nor to FAIL. The findings already written out, however, are **real, only incomplete** — do not discard them and do not overwrite them; handle the step according to the error branch of point 2, and carry the partial findings over into the input of the next review. `validate-gate-check.py` fails this mechanically as well.
   - **There is no unclosed `- [ ]` in the `<sec:critical_fixes>` section** (and the header is `<status:done>`) → the review gate is ✓. If Sonar is green as well, the static layer is green → step 3 (the heavy tests) may go.
   - **There is an unclosed `<status:must_fix>`** → the **round is a FAIL** (not a separate loop!): the findings go among the failed items of the round, and you hand them over as `--failed-item`s at the logging.
     > **🔴 The item name for a review finding:** it should be the **identifier** of the finding appearing in `code-review.md` (`MF-01`, `MF-02`, …), never its paraphrased text — the stopping limit builds on a literal name match (the same rule as with `DoD-NN`). If the reviewer did not give an identifier, **add it in `code-review.md`** consecutively, before you log.
   - **The `Suggestions` section:** it **does not block.** If a suggestion is within the scope of the cycle and can be applied without risk, fix it directly (the next round will test it anyway); if it falls outside the scope or is uncertain, leave it in the list for a future cycle — do not start a scope creep. `Suggestions` **never** go among the `--failed-item`s.

#### 2/c. Merging the findings — one fix batch (VD13)

The `BLOCKER`/`CRITICAL`/`MAJOR` hits of Sonar and the open `<status:must_fix>` findings are **failed items of the same round**: they go into one list, into one `failure-counter.py` call, and they get fixed **in one fixer run** (the Sonar-originated ones → the `implement-fixer`, the review-originated ones → the `review-fixer`; if there are both, in the order of point 6 of the loop: first the `implement-fixer`, then, in the same iteration, the `review-fixer`). This way **one** VD3a contract integrity gate belongs to one round, not two.

**If either half of the static layer fails, do NOT start the heavy tests (3.)** — the result of the round is a FAIL, move on to the gates of step 4 only as far as the evidence already available allows, then to the logging and to the FAIL branch of the loop.

### 3. The heavy tests and the regression checks (the `test-runner` subagent)

> **The round type (VD10):** in a **full** round the heavy tests + the **complete** regression set run. In a **light** round this step **is left out** — the exception: if the failure to be fixed was itself a heavy test, then **exclusively that one item** runs (VD10/3).

Run it only if **steps 1 and 2 were both green** — the heavy tests are only worth it on a diff that is already statically clean. **Primarily with a script** — the same table, a different type filter:

```bash
python3 <platform-scripts-mappa>/run-tests.py \
  specs/cycle-NN-<cycle-name>/plan.md \
  --round-dir specs/cycle-NN-<cycle-name>/test-report/validate/round-NN \
  --type nehez --phase <status:phase_validate>
```

The `<field:f_prerequisite>` and `Cleanup` columns of the table contain bringing the stack up and tearing it down — the cleanup runs even if the run blew up. In case of `exit 2` (there is no machine table), call the `test-runner` subagent, now to run the heavy tests (E2E + regression) — based on the tasks marked `TREG` in `tasks.md` and the `<sec:regression_impact>` table of `plan.md`. **Hand over the same round folder as in step 1** (TR5) — one folder belongs to one round, and the artifacts of the fast and the heavy tests go next to each other. It is the responsibility of the subagent to start the necessary backend services/containers, to resolve port conflicts and to clean up the temporary resources (see the contract of the agent).

> **⚠ A temporary port modification:** if the report of the subagent says a temporary config/port swap was needed, check whether, according to the report, the original state was successfully restored; if not, restore it yourself (`git checkout -- <file>`) before the validate phase ends — this must not get into the diff of the cycle.

**A feature is only done if every test, Sonar and the code review passed as well.** A partial PASS is not acceptable: if any test, Sonar or the review fails, the whole validate is a FAIL.

### 4. The DoD, tasks and report gate checks

#### A. Checking the <sec:definition_of_done> — **with a script first** (`dod-check.py`)

If the DoD items of `spec.md` name their **evidence** (`· _evidence:_ \`<test name>\`` / `\`cmd: <command>\`` / `\`manual: <what>\``), the evaluation is a **join** with the run results of the round — not a judgement:

```bash
python3 <platform-scripts-mappa>/dod-check.py \
  specs/cycle-NN-<cycle-name> \
  --round-dir specs/cycle-NN-<cycle-name>/test-report/validate/round-NN --apply
```

- **`exit 0`** → every DoD item is provably ✓ (with the `--apply` the script also ticked them off in `spec.md`);
- **`exit 1`** → there is a ✗ — the printed `DoD-NN` identifiers go verbatim into the `--failed-item` values of `failure-counter.py`;
- **`exit 3`** → there is a `?` (an item without evidence or a `manual:` one) — **only for these** is your own judgement needed: give them a ✓/✗ with a one-sentence justification. The absence of the evidence is at the same time a **spec quality signal** towards 02/05 — note it in the report of the round, but do not qualify the round as a FAIL because of it;
- **`exit 2`** → the DoD items have no `DoD-NN` identifier → add them in `spec.md` (see below), and run it again.

**Always reference the items by their `DoD-NN` identifier** (DI1) — in the report, in the log and in the fixing tasks alike.

> **⚠ Run without the `--apply`**, you have to mark every fulfilled (`✓`) item with `[x]` in the appropriate line of `spec.md` — do not wait for the end of the whole validation. (This modifies `spec.md` without a commit; during the loop this is correct — the commit happens once, at the end of the loop, VD8.)

> **🔴 The item name for a DoD failure:** the value of `--failed-item` of `failure-counter.py` should be **exactly the `DoD-NN` identifier** (e.g. `--failed-item "DoD-03"`), never the paraphrased text of the item. The counter builds on a literal name match: with text phrased differently in every round, the stopping limit would silently never take effect. **If the DoD items of `spec.md` have no `DoD-NN` identifier** (an older cycle), **add them in `spec.md` first** (consecutively, in the existing order), and only log afterwards — adding them is not a content change, it does not violate VD3.

#### A/2 + B. The other gates in a single call (`validate-gate-check.py`)

Open tasks, open DoD ticks, the unclosed items of `validate-input-from-prev.md` (IP1), an open `<status:must_fix>` (RV1), the match of the round block ↔ the `round-NN/` folder (the VD9 guard, TR5), the verbatim, per-task execution of the `[CHECK]` commands (CK1), and the failure evidence of the `[RED]` tasks in `check-log.md` (RED1) — all of them are regex questions, with a single call:

```bash
python3 <platform-scripts-mappa>/validate-gate-check.py \
  specs/cycle-NN-<cycle-name> --stage close [--require-review]
```

- **`exit 0`** → every gate examined is in order;
- **`exit 1`** → sort out the ✗ points printed (an open task → back to 06 or a fixing task; an open `[ ]` item in the `input-from-prev` → close it with a justification; a missing round block → `round-log.py`);
- **`exit 2`** → a non-existent cycle folder (a mistyped path).

The `--require-review` is needed for the run **before the PASS**: there the absence of `code-review.md` is a failure. In earlier rounds (when the review did not even start) leave it out.

**Test-substance gate (TB1) — a standalone command, in the same stage:**

```bash
python3 <platform-scripts-mappa>/test-substance-check.py specs/cycle-NN-<cycle-name>
```

- **`exit 0`** → there is no empty shell in the test files listed in the plan's `TA1` data sheets;
- **`exit 1`** → the round is a **FAIL**, and the failure type is a **test error** → the `implement-fixer` starts with the `## <sec:validation_fixes>` section. **The `VD3` guard applies here too:** fixing a vacuous test means **writing** the test — not switching the check off, not removing the file from the plan's data sheets, and not "adding" an assertion that is trivially true.

> **🔴 A `CK1` failure is not a fault of the log (VD3).** If the gate reports that a log row's `Task` cell carries a range, or that the logged command does not contain the task's test selector, **rewriting the log after the fact is not a fix** — the `[CHECK]`s must be **re-run one by one**, verbatim, as `tasks.md` writes them, and the new runs logged. A merged run also hides the case where the `tasks.md` selector references a test function that no longer exists. If the framework genuinely cannot filter down to a single case, that is a `CK-DEVIATION: <task> — <reason>` line in the `## <sec:notes>` section of `check-log.md` — **not without a justification**.

> **🔴 A green `[RED]` cannot be fixed by rewriting the log (RED1/VD3).** If the gate reports that a `[RED]` task has no failing (`✗`) run, the missing evidence is **not** supplied by a log row written in after the fact: the test has to be written so that it **actually fails** without the implementation (an `assert True` shell physically cannot be red — which is why this is the strongest, judgment-free signal). In that case the `[RED]` task is **not done** → back to `06` with the `## <sec:validation_fixes>` section. The only exception is a `RED-EXEMPT: <task> — <reason>` line (a regression task updating an existing test that is rightly green) — this falls under the `VD3` anti-test-fraud guard.

> **What is left to you (IP1):** if an `input-from-prev` item **caused an error** during the validation (e.g. a test failed because of a missing prerequisite), that is a FAIL — to be fixed according to the usual loop, not to be settled by dropping it. The script only sees whether it is open; whether you *took it into account* or *dropped it* is written in by you.

#### B/2. The gate of the mandatory test reports (TR3 — deterministic)

The report artifacts declared in the `## <sec:cv_test_reporting>` table of `conventions.md` have to be there **in the folder of the current round**. Do **not check this by eye** — run the gate, handing over the round folder:

```bash
python3 <platform-scripts-mappa>/report-gate-check.py \
  conventions.md specs/cycle-NN-<cycle-name> \
  --report-subdir test-report/validate/round-NN
```

> **🔴 The gate only runs in a FULL round (TR5/VD10).** In a light round not every test category runs deliberately, so the complete report table **cannot even be fulfilled** — the gate then **is left out**, and it appears in the step table of the `## <sec:round> N` as a "skipped — light round (VD10)" line. This is not a loosening: a PASS can only be given from a full round anyway (VD10/1), and there the `exit 0` of the gate is a **mandatory** condition.
>
> _(Earlier the gate ran in every round, but on fixed file names — in that case the light round found the artifact left over from the PREVIOUS round, and gave a false green. The folder per round eliminates this, which is why the rule by round type is needed.)_

- **`exit 0`** → the gate is ✓ (or the project explicitly does not generate a report, or the examined phase is not a report phase — TR6). Write the result into the report of the round.
- **The gate also measures the layout of `test-report/` (TR5/c):** a foreign folder under `test-report/` is `exit 1` — this is not a missing report but a broken path base. The gate names the folder and the reason; delete it and re-run the failing step with the correct base (0/a). You do not start a fixer for this either.
- **`exit 1`** → a missing or empty artifact. **The round cannot be closed as a PASS**, but this is **not a code bug**, therefore you do **not start a fixer**: producing the report is the business of the `test-runner`.
  1. Call the `test-runner` again **explicitly to produce the missing report(s)**, with the command given in the table, and ask it to put the artifact **into the folder of the current round** (hand over the concrete path).
  2. Run the gate again. If it fails the second time as well → **STOP + human** with the "Where we are" header: *"The [artifact] report did not come into existence even after two attempts with the `<command>` command. Human intervention is needed — how do we continue?"*, together with the output of the script.
- **`exit 2`** → the `## <sec:cv_test_reporting>` section of `conventions.md` is missing or unfilled (a placeholder remained). This is a **project configuration deficiency**, not a test error: **STOP + human**, and ask for the section to be added with the content according to the `00-init` (category / tool / command / artifact, or an explicit `**<field:f_report_required>:** no` + a justification). Do not invent the command yourself, and **do not rewrite `conventions.md`** — that is a joint decision of phase 00 and the user.

> The gate runs **in every FULL round**, not only in the last one — and since every round works into its own folder, the report of the failed rounds is kept as well: it can be opened afterwards, what exactly failed in round 2. The artifacts of the light rounds (the report of the fast tests) are kept the same way in their own folder, only the gate does not require them.

> **What is deliberately NOT here (VD12):** the sync of the **component READMEs** and of the generated documentation is the business of `08-doc-sync` (its explicit output, with its own DS22 gate). The examination of the **code comments / JSDoc** for becoming outdated, however, **does belong here**: that is done by the `reviewer` agent of step 2, which reads through the diff anyway. **You yourself (the orchestrator) still do not read through the modified files** — reading the diff is the business of the subagent, you evaluate its report.

### Logging and stopping limits (VD4 — deterministic, with a script)

> **🔴 ONE VALIDATION ROUND = ONE run entry (VD4a).** A round is steps 1–4 (the fast tests → the static layer [Sonar + the code review] → the heavy tests → the DoD/tasks/report gate) — **a light round is a full-value round too** (VD10): at its end exactly one entry is produced the same way, with the same item names. You log the result of the round **at the END of the round, with a single `failure-counter.py` call**, together with all the failed items. **Logging a partial result separately is FORBIDDEN** (e.g. a "the fast tests are green" entry after step 1): an interposed PASS entry **breaks the chain of consecutive failures**, and the 3-attempt stop would never take effect — the loop becomes infinite. The partial result of steps 1–4 goes into the **step table** of the round (see "The `validation-report.md` — the complete validation report"), not into the History.
>
> When does the round close (what goes into one entry)?
> - **Step 1 (the fast tests) failed** → the round ends here (neither the static layer nor the heavy tests): one FAIL entry with the fast test items.
> - **1 is green, 2 (the static layer) failed** → **one** FAIL entry in which the Sonar item(s) **and** the `MF-NN` findings appear together (VD13) — the heavy tests do not run.
> - **1–2 are green, 3 (the heavy tests) failed** → one FAIL entry with the heavy test items (you do not log the green fast tests and the clean review separately).
> - **1–3 are green, 4 (the DoD/tasks/report gate) failed** → one FAIL entry with the failed `DoD-NN` identifiers.
> - **Everything is green** → one PASS entry, without a `--failed-item`.

**Do NOT write/count the run entry and the counters by hand** — the `failure-counter.py` script does it. The path of the scripts is **resolved to a concrete value** in the installed skill (the installer replaces it per platform: `.claude/scripts/` / `.agents/scripts/` / `.cursor/scripts/` / `.github/scripts/` / `.codex/scripts/`); if you do see a `<platform-scripts-mappa>` form, look for which of the five exists in the project. Hand over to it the failed item names returned **verbatim** by the `test-runner` (for a DoD failure the `DoD-NN` identifier — see step 3./A.):

```bash
# FAIL — every failed item as a separate --failed-item (on the verbatim names of the test-runner):
python3 <platform-scripts-mappa>/failure-counter.py \
  specs/cycle-NN-<cycle-name>/test-report/validation-report.md \
  --result FAIL --timestamp "2026-08-06 14:32" \
  --failed-item "<the exact test name/identifier>" [--failed-item "<another>" ...] \
  --details "<a short reason>"
# PASS (everything green — without a --failed-item):
python3 <platform-scripts-mappa>/failure-counter.py \
  specs/cycle-NN-<cycle-name>/test-report/validation-report.md \
  --result PASS --timestamp "2026-08-06 14:32"
```

**The timestamp (portability):** give the value of `--timestamp` as a **concrete string** (`YYYY-MM-DD HH:MM`) — the script deliberately does not read the system time. If you use shell substitution, that is platform dependent: bash/zsh → `$(date '+%Y-%m-%d %H:%M')`, PowerShell → `(Get-Date -Format 'yyyy-MM-dd HH:mm')`. A mistyped or missing timestamp does not break the counting (the item names are what matter), but it does break the readability of the log.

**Three stopping limits — if any of them is fulfilled → `exit 3` → the loop STOPS:**

| Limit | Default | What it catches |
|---|---|---|
| per item **consecutive** failures | 3 | the classic 3 attempts: the same item fails round after round |
| per item **total** failures in the log | 5 | the "sometimes it fails, sometimes it does not" item — including the broken chain |
| **consecutive FAIL runs** | 5 | a diverging loop: a **different** item fails in every round (the VD4b global backstop) |

**The exit code decides, not your own judgement:**
- **`0`** → logged, none of the limits is full → the loop may continue.
- **`3`** → logged, one of the limits is full → **STOP**; the script prints which item and which limit it is because of. The type of the stop is decided by the VD5 heuristic (a design error → escalation; otherwise → STOP + human).
- **`1`** → **an error in the call, the log was NOT modified.** In that case logging by hand is **forbidden** — it would wreck the deterministic counting. Read the error message, fix the call (the most frequent cause: a `FAIL` without a `--failed-item`, a missing `--timestamp`, or a `--failed-item` next to a `PASS`), and run it again. If it does not succeed twice either, **STOP + human**: report the command and the error message to the user.

**A `FIGYELEM:` line in the output** — the script signals if an item failed earlier as well, but an intervening PASS broke the chain. This almost always means that somebody (an earlier run) **logged a partial result** against the VD4a rule. Do not ignore it: the log stops correctly at the "total failures" limit even then, but the `# <sec:validation_history>` is misleading — write into the `--details` that the chain was broken.

### 5. CLOSING the round in `validation-report.md` (VD9 — mandatory, BEFORE the logging script)

> **🔴 This step runs in every round — at a PASS and at a FAIL alike, on every branch.** The order is fixed: **first closing the `## <sec:round> N` block, only then `failure-counter.py`.** The other way round, the script appends the History after the unfinished block, and the log gets mixed up.

**The block is closed by `round-log.py close`** — the mechanical fields (the result, the step lines, the failed items, the DoD table, the header, the `## <sec:closing_summary>`) are written by the script, you only give the free-text parts:

```bash
python3 <platform-scripts-mappa>/round-log.py close \
  specs/cycle-NN-<cycle-name>/test-report/validation-report.md \
  --result FAIL --timestamp "2026-08-10 10:36" \
  --step "10:35|test report gate (TR3)|report-gate-check.py …|✓ exit 0" \
  --failed-item "auth.spec.ts > refresh token rotation" --failed-item "DoD-03" \
  --dod "DoD-01|✓|the token exchange returns 200" --dod "DoD-03|✗|the correlationId is missing" \
  --review "Ran: yes — 2 open <status:must_fix> (MF-01, MF-02)" \
  --decision "FAIL → a fixing round starts, with a light round."
```

- The values of `--failed-item` are **the same** as the ones you give to `failure-counter.py` right after — this way the two lists cannot drift apart.
- At a PASS (or in case of a STOP/escalation) add the `--final "PASS"` / `--final "FAIL (stopped)"` / `--final "escalated"` flag: this updates the header and regenerates the `## <sec:closing_summary>` section.
- The script modifies **only the open block**; it never touches a closed round or the `# <sec:validation_history>`.

The content expectations of the block (which you fill with the `--step` / `--dod` / `--review` / `--decision` fields):

1. **The header line**: the result of the round in place of the `— in progress` (`— PASS` / `— FAIL`); the type of the round (`FULL` / `LIGHT`) should stay.
2. **`### <sec:steps>`** — the execution order with timestamps, with the **verbatim evidence** of the `test-runner` (the command issued + `X passed / Y failed / Z skipped`), and at the **skipped** steps the reason (`skipped — step 1 failed`, `skipped — the static layer failed`, `skipped — light round (VD10)`, `skipped — plan deficiency (TR4)`).
3. **`### <sec:failed_items>`** — with the **exact** item names to be handed over to `failure-counter.py` (for a DoD failure `DoD-NN`).
4. The **`### <sec:definition_of_done>`** table, the **`### Test reports (TR3 / TR5)`**, the **`### Task completion`**, and if there was a fixer: the **`### Fix round`** (the tasks added, the feedback of the fixer, the result of the VD3a gate).
5. **`### <sec:round_verdict>`** — one sentence: why a new round starts, or why the loop stopped / converged.
6. **Update the header of the file** (`<field:f_current_status>`, `<field:f_round_count>`, `<field:f_last_updated>`), and when closing the phase (a PASS, a STOP, an escalation — **on all three branches**) the `## <sec:closing_summary>` section as well (the final result, the rounds split into full/light, the re-run items, the escalation, a temporary environment change).

**A deterministic self-check** — after `round-log.py close`, **before** `failure-counter.py`:

```bash
python3 <platform-scripts-mappa>/validate-gate-check.py specs/cycle-NN-<cycle-name> --stage close
```

This checks the existence of the round block, the `## <sec:round> N` ↔ `round-NN/` match (TR5) and the open items. If it is `exit 1`, **do not run the logging script**, and do not close the phase — sort out the ✗ points printed first.

---

## The `validation-report.md` — the complete validation report (VD9)

> **The file is not a one-line run log, but the complete run log of the validation.** Afterwards it has to be clear from it **what ran, in what order, with what result, what ran again and why** — without anybody having to look up the chat (after a `/clear` that does not even exist). If there is only the `# <sec:validation_history>` in the file, the phase did **not** do its job.

**Who writes what into the file — two sharply separated regions:**

| Region | Where | Owner | Content |
|---|---|---|---|
| The header + the `## <sec:round> N` blocks | from the beginning of the file | **you (the orchestrator)** | the event log of the run, one block per round, **appended — you NEVER overwrite an earlier round** |
| `# <sec:validation_history>` | at the **end** of the file | **exclusively `failure-counter.py`** | a machine run log for the stopping counters |

**🔴 The writing rule — APPEND-ONLY, you NEVER write the file out as a whole again.** The script always appends to the **end of the file**, therefore the `# <sec:validation_history>` header has to stay at the end of the file; you insert the new `## <sec:round> N` block **directly BEFORE the `# <sec:validation_history>` header**. In practice: you insert or extend with a **targeted edit** (matched on a single anchor text) — rewriting the whole file is forbidden, because with a long log the model "summarizes" or drops the earlier rounds along the way, and the history is irrecoverably lost. What you may overwrite: **exclusively** the 3 lines of the header (`<field:f_current_status>` / `<field:f_round_count>` / `<field:f_last_updated>`), the `## <sec:closing_summary>` section, and the **still open** (`in progress`) `## <sec:round> N` block. **You never touch the block of a closed round and the lines of the History** — you do not edit them, do not rearrange them, do not delete them.

**When you write:** three times, in every round — this is step **0/b** and step **4.** of the "Validation steps", not a separate ceremony:
1. **at the beginning of the round (0/b)**: creating the file, if there is none + opening the new `## <sec:round> N` block before the `# <sec:validation_history>`;
2. **along the way**: the line of every step (a test-runner call, a gate, starting/returning a fixer) into the step table immediately — so that the trace is kept even after an interrupted run;
3. **at the end of the round (4.)**: closing the block + updating the header (and, when the phase is closed, the `## <sec:closing_summary>`) — **before running the logging script**, at a PASS and at a FAIL alike.

### The template of the file

```md
<!-- INCLUDE:lang/07-validate.md#validation-report-sablon -->
```

### Mandatory content elements (without these the report is incomplete)

1. **The execution order, with timestamps** — the step table should show what ran, in what order, and **what was left out and why** (e.g. leaving out the heavy tests after failed fast tests). The "<status:skipped>" line is just as important as a step that ran.
2. **The evidence of the `test-runner` verbatim** — the command issued and the `X passed / Y failed / Z skipped` counts (TR1). This is what makes it verifiable afterwards that an actual run stood behind the PASS.
2.a **The own report of the test tool in the folder of the round (TR3/TR5)** — the `**Report folder:**` line in the header of the `## <sec:round> N`, the output of the gate in the step table (which artifacts got in, how big they are). The report lives next to the log, in the own folder of the round; the textual log does not substitute for it, and the report does not substitute for the log. **The number of the folder name and the ordinal of the `## <sec:round> N` must match** — this is what makes the failed step and the evidence belonging to it pairable.
3. **The visibility of the re-runs** — every round is a separate block, and the `## <sec:closing_summary>` lists which items ran several times (this is the answer to the "what ran again" question).
4. **The trace of the fixing round** — which tasks it added, what the fixer returned, what the result of the contract integrity gate (VD3a) was. If the gate found a weakening, **the affected file and the fact of the restoration** should get in as well.
5. **The verdict of the round in one sentence** — why a new round started, or why the loop stopped.
6. **The type of the round (VD10)** — `FULL` or `LIGHT` in the header of the `## <sec:round> N`, and in the step table the reason at the skipped steps: "<status:skipped> — light round (VD10)". The **Rounds** line of the `## <sec:closing_summary>` should split it: how many full, how many light. Without this it cannot be verified afterwards whether the PASS came from a full round.

> **The rounds of the review go here as well** (RV1): `validation-report.md` is the **complete** quality history of the cycle — tests and review alike. `code-review.md` is only the list of the findings, not a log: the course of the loop, the attempt counts and the stopping limits are kept exclusively by the `# <sec:validation_history>` of `validation-report.md`.

---

## The self-healing loop (the orchestrator loop)

In case of a FAIL you do **not** simply hand control back to the user. You conduct an iterative fixing loop — the `implement-fixer` subagent → a re-validation — until there is a PASS, or until the **3-attempt rule (VD4)** / the **branch escaping upwards (VD5)** stops it.

The existing FAIL machinery stays (the `# <sec:validation_history>` of `validation-report.md`, the `## <sec:validation_fixes>` of `tasks.md`, the status reset) — only the earlier "manual handover to the user (run 06 again)" becomes an orchestrated loop. The fixing is not done by you: that is done by the `implement-fixer` subagent (= the Fix mode of 06); you validate, log, decide and switch statuses.

### ⚠ The anti-"test cheating" guard (VD3 — the most important rule of the loop)

**The loop adjusts the CODE to the test / to Sonar / to the DoD / to the review finding — NEVER the other way round.** The test, the <sec:definition_of_done> and the finding of the reviewer are the **contract**; the loop **must not modify** this for the sake of a green result.

**STOP — any of these is forbidden:**
- weakening/loosening a test assertion, or copying the expected value back from the code;
- `skip`/`xfail`/commenting out/deleting a test for the green;
- a hardcoded "expected" value that turns the test green but does not implement the real behavior;
- lowering/rephrasing a DoD item of `spec.md` so that it is easier to fulfill;
- the **cosmetic silencing** of a `<status:must_fix>` finding without fixing the root cause (a lint-suppress comment, disguising the code objected to);
- deleting/rephrasing the `<status:must_fix>` entry of `code-review.md` without a fix.

This rule is given to the `implement-fixer` as well (the guard of the Fix mode of 06) — a cheaper LLM should not drift into test cheating either. **If an error would only be green by changing the test/DoD** → that is not a code fix but a **design error** → VD5 (the branch escaping upwards), not loosening the test.

#### 🔴 The contract integrity gate after the fixer (VD3a — deterministic, mandatory)

The prohibition above is **only an instruction** on its own — the fixer runs on a cheaper model, and the whole value of the loop rests on the green result being real. Therefore after every return of the fixer, **still before the re-validation**, look **actually** at what it rewrote:

```bash
python3 <platform-scripts-mappa>/contract-guard.py specs/cycle-NN-<cycle-name>
```

The script looks at whether a protected path changed (test files according to the "<sec:cv_test_structure>" of `conventions.md`, `spec.md`, `test-report/code-review.md`, the Sonar/lint configuration), and it looks for the classic cheating patterns in the **added lines** (`.skip(`, `xit(`, `@pytest.mark.skip`, `@Disabled`, `NOSONAR`, `eslint-disable`, `@ts-ignore`), and in the **deleted lines** for disappeared assertions, silenced `MF-NN` findings and modified `DoD-NN` lines.

The last line of the output decides whether you have to read a diff at all:

- **`VERDICT: CLEAN`** (`exit 0`) → not a single protected path changed → **do not read the diff**, the re-validation may go.
- **`VERDICT: SUSPECT`** (`exit 1`) → it found a cheating pattern → this is **a weakening of the contract**, see below: restoration + escalation. The suspicious lines are printed by the script, you do not have to look for them.
- **`VERDICT: REVIEW`** (`exit 1`) → a protected path changed, but it found no pattern → **only then** read the diff of the affected files, and decide which case it is:
  - **Legitimate** (adding a new test for the error, adding a missing `DoD-NN`/`MF-NN` identifier, marking a finding as closed in `code-review.md` **after a fix that was actually carried out**, fixing a typo in the *name* of the test) → ✓, but **write into the "Fix round → Contract integrity gate" line of the round** what and why.
  - **A weakening of the contract** (loosening an assertion, `skip`/`xfail`, deleting a test, the expected value copied back from the code, rephrasing/lowering a DoD item, switching off a Sonar rule, deleting/rephrasing a `<status:must_fix>` finding or silencing it with a suppress comment) → **STOP, this is test cheating.** What to do: (1) restore the affected files (`git checkout -- <file>`); (2) log the given item as a FAIL in the usual way; (3) handle it **as an escalation signal** (VD5) — the loop does not try further with this item, because the fixer attacked the contract, not the code.
- After the `git checkout --` restoration, do **not** start a new fixer on the same item immediately — that is the FAIL of the round, and the VD5 branch decides.

This gate is the only place where VD3 is not just an intention but a **verified fact** — do not skip it, not even if the summary of the fixer claims that it did not touch the tests.

### One iteration of the loop

1. **Logging the FAIL of the round (VD4a) — with the `failure-counter.py` script, ONCE per round.** Run it with `--result FAIL` + **all** the failed item names of the round (see "Logging and stopping limits"). This logs the run AND computes the counters — **not by hand**. Before it, close the `## <sec:round> N` block of the round in `validation-report.md` (VD9).
2. **The stopping decision from the exit code of the script (VD4).** `exit 3` → one of the limits is full (per item 3 consecutive / 5 total failures / 5 consecutive FAIL runs) → the loop stops (see "The stopping limits as a loop limit"); the type of the stop is decided by the VD5 heuristic (a design error → escalation; otherwise → STOP + human). `exit 1` → a faulty call, fix it and run it again (logging by hand is FORBIDDEN). `exit 0` → the loop may continue.
3. **An early escalation check (VD5).** If the fixer subagent of the previous iteration (`implement-fixer` or `review-fixer`) returned an **escalation signal**, or the **contract integrity gate (VD3a)** found a weakening, do not keep circling in 06 → **escalate immediately** (see "The branch escaping upwards"), you do not have to wait for the 3rd attempt.
4. **Adding the fixing tasks.** According to the FAIL machinery (see "FAIL — adding the fixing tasks"), into the section **according to the type of the failure** at the end of `tasks.md`, with prerequisite references, as `[GREEN]`/`[CHECK]` tasks:
   - a test / Sonar / DoD failure → `## <sec:validation_fixes>`;
   - a review `<status:must_fix>` (`MF-NN`) → `## <sec:review_fixes>` *(a `[RED]` pair is not needed here — a direct fix)*.
   Avoiding duplicates: do not add the same one twice. **An iteration does not start with an empty failure list** — if there is no concrete item to fix (e.g. a QG1 threshold failure), the loop cannot continue, see the QG1 branch.
5. **Putting on the marker (VD6).** Switch the status of `tasks.md` to `<status:ready_for_implement> [validate-loop]`. The marker signals: the fix mode is active → the fixer steps the status automatically, without a confirmation. *(There is a single marker — for a review fix it is this one too, not a separate `[review-loop]`.)*
6. **Starting the fixer subagent (VD2) — according to the type of the failure.** If **only** a review finding failed in the round → the `review-fixer` with the `## <sec:review_fixes>` tasks; otherwise the `implement-fixer` with the `## <sec:validation_fixes>` tasks. If there are **both** (in the confirming round a test failed as well, and a finding also remained), the `implement-fixer` runs first (a green test is the basis), then, in the same iteration, the `review-fixer`. You start both with the concrete failure list + the prerequisite reports (see "Starting the fixer subagent"). If either fixer returns an **escalation signal** → jump to point 3.
7. **The contract integrity gate (VD3a).** After the fixer returns, run the `git diff` check above **before** you validate again. In case of a weakening: restoration + escalation (point 3).
   - **If the fixer returned with a `RUN BLOCKED (EX1)` signal** (it could not run the verification of its `[CHECK]`, because its subagent cannot get command approval): this is **not** an error and **not** an escalation signal — the fix is done, only the verification was left out. The `run-tests.py` run of the next round will run the complete fast set anyway; **do not tick off** the `[CHECK]` task until that round is green.
8. **The re-validation — with a LIGHT round (VD10).** After the fix, the whole run does **not** start: the complete fast test set runs, plus that one item if the failure was a heavy test, Sonar or a review finding (for the latter with the `reviewer` running incrementally, only on the open `MF-NN`s). This is a **new round** — at its end exactly one log entry is produced again.
   - **FAIL** → a new iteration from point 1 (a light round again).
   - **Green** → **it is still NOT a PASS.** Immediately, without a fix, start a **FULL confirming round** (the fast tests → **Sonar + the code review** → the heavy tests + the regression → the DoD/tasks/report gate). This is a separate round as well, with a separate log entry. The review runs **incrementally** here: handing over the previous `code-review.md`, focusing on the `<status:must_fix>`s that are still open.
     - the confirming round is a **PASS** → the loop converged, jump to "Status handling → PASS" (this is where the marker comes off, and the single closing commit happens);
     - the confirming round is a **FAIL** (the fix broke something elsewhere, or the heavy test fails) → a new iteration from point 1.

### Starting the fixer subagent (VD2)

There are two fixers, with **identical rules** — both are thin wrappers around the "Fix mode" section of `06-implement.md`, so there is no duplicated fixing logic, and the quality rules of 06 take effect automatically:

| Fixer | When | Input |
|---|---|---|
| `agents/implement-fixer.md` | a test / Sonar / DoD failure | the unfinished tasks of the `## <sec:validation_fixes>` of `tasks.md` + `test-report/validation-report.md`, and if Sonar failed, the `test-report/validate/round-NN/sonar-report.md` of **the current round** (give the round number concretely — TR5) |
| `agents/review-fixer.md` | a review `<status:must_fix>` (`MF-NN`) | the unfinished tasks of the `## <sec:review_fixes>` of `tasks.md` + `test-report/code-review.md` (with the text of the findings) |

- **The output (for both):** (a) a summary of the fixes made (which task it closed with what), and (b) an **escalation signal**, if one of the errors could only be brought to "green" by modifying the test/DoD/spec or by silencing the finding (VD3). The subagent **must not** modify the test/the DoD/the finding, and it does **not** write `validation-report.md` or `code-review.md` — that is done by you (the orchestrator).

### The branch escaping upwards (VD5 — the escape hatch)

Not every FAIL is a code bug: sometimes it is a **design error** (the test/DoD contradicts the code, or the plan builds on a faulty base). In that case the loop should not circle in 06 — 06 will never make it green, because it could only be done by loosening the test/DoD, and that is forbidden by VD3.

**The detection heuristic** — a sign of a design error if:
- **(a)** the `implement-fixer` returned an escalation signal (the error could only be made green by changing the test/DoD), **or**
- **(b)** when the stopping limit was reached, the stuck item could, based on the fixing attempts so far, only be made green by changing the test/DoD, **or**
- **(c)** the **contract integrity gate (VD3a)** found that the fixer modified the test/the DoD/the Sonar configuration for the green — in that case, after the restoration, there is no point in asking the same thing from it again.
- **(d)** the `test-runner` reported a **plan deficiency** (TR4): a test group did not run because the runtime detail is not in `plan.md`. This is a deficiency of phase 03 — the fixer cannot fix it, because the code is not the fault.

**What to do (STOP + escalation), in order:**
1. Log into the `# <sec:validation_history>` the stuck item, and that you are escalating because of a **design error** (not a code bug) — in the `--details` field.
2. **A status reset to 03/02:** switch the status of the affected design document back to the appropriate not-done value — `plan.md` → `<status:draft>` (if the plan is at fault), or `spec.md` → `<status:draft>` (if the DoD itself is faulty/contradictory). `tasks.md` stays with the `[validate-loop]` marker (the signal of the stuck state).
3. **A single closing commit** (VD8) — according to the procedure of the *Phase-closing commit* section, **mandatory** (the escalation branch is no exception either).
4. **Tell the user about the handover** — this is a design question, not an automatic fix (it belongs to the analyze-spirited design loop of list2), see the text of the signal below. After the design is settled, the process returns here along the `05→06→07` path.

### The stopping limits as a loop limit (VD4)

The limit of the loop is given by **the exit code of `failure-counter.py`** — **not by your own estimate, and not by a counter read by hand**. Three limits run in parallel (details: "Logging and stopping limits"):

1. **per item 3 consecutive failures** — the classic 3 attempts: it catches exactly the stuck element;
2. **per item 5 total failures** — the "sometimes it fails, sometimes it does not" item, which would avoid (1) by breaking the chain;
3. **5 consecutive FAIL runs (VD4b)** — a global backstop for when **a different item fails in every round**: the loop does not converge, it only produces new errors. This limit stops the diverging loop independently of the per-item counters.

If any of them is fulfilled → `exit 3` → **the loop stops**, the script prints which item and which limit it is because of.

- If the stop is a sign of a **design error** (the VD5 heuristic) → **escalation** (the branch escaping upwards).
- Otherwise → **STOP + human** (a stuck code bug): *"[Failed Item] failed for the [N]th time as well ([which limit]). Human intervention is needed — how do we continue?"* At limit (3): *"The fixing loop has not converged for [N] rounds — a different element fails in every round. Human intervention is needed — how do we continue?"*, listing the failed items of the last rounds. Do not continue the fixing without an answer from the user. A commit at the end (VD8); the `## <sec:validation_fixes>` and the `[validate-loop]` marker stay (the stuck state).

### The commit strategy in the loop (VD8)

- **There is no commit per iteration in the loop** — the earlier commit per FAIL is gone.
- **A single closing commit** at the end of the loop (a PASS / a 3-attempt STOP / an escalation):
  ```bash
  git add specs/cycle-NN-<cycle-name>/
  git commit -m "cycle-NN: 07-validate"
  ```
- **Interruption-safe:** the absence of an intermediate commit is compensated by the `# <sec:validation_history>` + the `[validate-loop]` status marker — the continuation can be reconstructed from these (see "Handling an interrupted run").

**The closing commit is MANDATORY, without exception on every closing branch** (a PASS, a stopping-limit STOP, an escalation upwards, a QG1 threshold failure) — for the procedure see the *Phase-closing commit* section. You must not hand control back to the user without a commit.

<!-- INCLUDE:shared/phase-commit.md -->

In the block above, the value of `<PHASE-TAG>` in this phase is: **`07-validate`**. Step 2 (writing the status) here means arranging the status/marker according to the rule of the given closing branch (at a PASS `spec.md`/`plan.md`/`tasks.md` → `<status:done>` + the marker off; at a STOP/escalation the reset status + the marker staying). You do **not** ask for a confirmation before the commit.

> **The stopping rule (PC1):** if the loop closed (on any branch) but the phase-closing commit is missing (a VCS project, `git log -1 --oneline` does not show the `cycle-NN: 07-validate` commit), **STOP** — commit first, and only close the phase and give the next step / the stopping message afterwards.
>
> **The stopping rule (the VD9 guard) — BEFORE the commit, mandatory:** `validation-report.md` must not consist of the `# <sec:validation_history>` only. Check it deterministically:
> ```bash
> python3 <platform-scripts-mappa>/validate-gate-check.py \
>   specs/cycle-NN-<cycle-name> --stage close --require-review
> ```
> If the script gives `exit 1` (there is no `## <sec:round> N` block, there are fewer round blocks than `# <sec:validation_history>` runs, a `round-NN/` folder is missing, or an open item remained), **STOP** — the mandatory output of the phase is missing or incomplete. Add the missing block(s) from the evidence available (the artifacts of the round folders + the lines of the History), and only commit afterwards. This holds on the PASS, the STOP and the escalation branch alike. *(On a STOP/escalation branch the `--require-review` may be omitted if the review did not even start.)*

### "Where we are" in the stopping messages (LC2)

In the stopping messages towards the user (a stopping-limit STOP, an escalation, a QG1 threshold failure — this is the **only** user contact of the loop, see VD7) show where the loop stands: the stuck element and the limit that is full, referencing the `# <sec:validation_history>`:

```
<!-- INCLUDE:lang/07-validate.md#LC2-megallas-prefix -->
```

At the end of your answer you must place a direct, clickable link to `validation-report.md`.

---

## Status handling

> **The PASS is automatic, because it is based on deterministic checks (tests + Sonar + DoD). A user confirmation is NOT needed — do not ask for a confirmation before switching to `<status:done>` status. The result can be checked afterwards in `validation-report.md` (VD9: a step log per round + the `# <sec:validation_history>`).**

### PASS

Every test passed (with evidence — TR1/TR2), every item of the DoD is fulfilled, every task is `[x]`, the Sonar Quality Gate is a PASS (or N/A), **the test report gate (TR3) is `exit 0`**, **the code review ran and there is no unclosed `<status:must_fix>` (RV1)**, and the contract integrity gate (VD3a) is clean.

> **🔴 The source of the PASS can only be a FULL round (VD10/1).** If the last round was **light** (only the fast tests ran), part of the conditions above cannot even be measured — in that case there is **no PASS**: start a full confirming round, and decide from its result. The check: `— FULL` stands in the header of the `## <sec:round> N` block to be closed, and the heavy test, Sonar (or `N/A` according to the plan) **and the code review that ran** appear in the step table.

What to do:
1. **Close the `## <sec:round> N` block of the round** in `validation-report.md` according to **step 5** (if the block does not exist — because 0/b was left out —, **add it now**, from the evidence of the round), and update the header + the `## <sec:closing_summary>` section (VD9), then log: `failure-counter.py ... --result PASS --timestamp "..."` (without a `--failed-item`). This closes the round in the log.
2. **Take the `[validate-loop]` marker off** (if the loop ran): the status of `tasks.md` switches to `<status:done>` — without a marker. Update the status of `plan.md` and `spec.md` to `<status:done>` as well. The closed tasks of the `## <sec:validation_fixes>` / `## <sec:review_fixes>` sections stay in their place (a trace is kept of what was fixed in the loop).
3. **A single closing commit** (there was no intermediate commit during the loop — VD8), according to the procedure of the *Phase-closing commit* section — **mandatory**:
   ```bash
   git add specs/cycle-NN-<cycle-name>/
   git commit -m "cycle-NN: 07-validate"
   ```
<!-- INCLUDE:lang/07-validate.md#zaro-uzenet -->
   > **At the end of the answer, place the direct, clickable link of `validation-report.md`.**

### FAIL — adding the fixing tasks (steps 4–6 of the loop)

If any test, Sonar, or the DoD check fails, you do **not** hand control back to the user — you prepare and start the next iteration of the loop (see "The self-healing loop"). The steps **in order**:

```
[ ] 0. validation-report.md exists, and the ## <sec:round> N block opened at the BEGINNING
        of the round (step 0/b) — if not, the file contains only the # <sec:validation_history>
        and the report is empty → add it before you move on
[ ] 1. the ## <sec:round> N block is closed in validation-report.md (VD9, step 5): the step table with
        the execution order + the evidence of the test-runner (the command +
        X passed/Y failed/Z skipped), the failed items, the DoD table, the verdict of the round
[ ] 2. failure-counter.py run ONCE, at the END of the round (--result FAIL +
        ALL the failed items of the round; for a DoD failure with the DoD-NN identifier) →
        # <sec:validation_history> updated, the counters stepped deterministically
        ⚠ you do NOT log a partial result separately (e.g. "the fast tests are green") (VD4a)
[ ] 3. The stop from the exit code of the script: exit 3 → STOP (an escalation or a human,
        see below) — do NOT start another fixer; exit 1 → a faulty call, fix it and run
        it again (logging by hand is FORBIDDEN); exit 0 → on
[ ] 4. tasks.md → the ## <sec:validation_fixes> chapter created or continued
[ ] 5. Put at the beginning of the chapter, as prerequisite references:
        - specs/cycle-NN-<cycle-name>/test-report/validation-report.md
        - (if Sonar failed) the Sonar report of the CURRENT round, with the full path:
          specs/cycle-NN-<cycle-name>/test-report/validate/round-NN/sonar-report.md
          ⚠ write out the round number concretely (TR5) — the fixer has to see the result
            of the round that triggered it, not of another one
[ ] 6. The concrete tests / Sonar errors / DoD-NN items to fix added as [GREEN]
        tasks, with a [CHECK] verification task at the end of the group (avoid duplicates!)
        ⚠ if the list would be EMPTY (a QG1 threshold failure) → no iteration starts, see QG1
[ ] 7. tasks.md status → <status:ready_for_implement> [validate-loop]   (the marker, VD6)
[ ] 8. the implement-fixer subagent started with the concrete failure list (VD2)
[ ] 9. After the fixer returns: the contract integrity gate (VD3a) — a git diff on the
        test files / spec.md / the Sonar configuration. A weakening → a git checkout --
        restoration + an escalation (VD5). An escalation signal from the fixer → VD5.
        Otherwise → a re-validation (step 8 of the loop, a new round)
```

**The FAIL branch does NOT commit here and does NOT hand control back to the user** — the commit happens once, at the end of the loop (VD8), and the user contact only in case of a stopping-limit STOP / an escalation / a QG1 (VD7).

#### Signalling the escalation to the user (VD5 — the branch escaping upwards)

With the "Where we are" header (LC2):
<!-- INCLUDE:lang/07-validate.md#VD5-eszkalacio-uzenet -->

#### A validation stop (VD4 — on the `exit 3` of the script)

If `failure-counter.py` returns with an `exit 3` (any of the three limits: per item 3 consecutive, per item 5 total, or 5 consecutive FAIL runs) — **stop**. Do not override the decision of the script, and do not start "one last" fixer. Decide the type of the stop according to the VD5 heuristic:
- **a design error** (it would only be green by modifying the test/DoD, or the VD3a gate found a weakening) → **an escalation** (the message above);
- **a stuck code bug** → with the "Where we are" header: *"[Failed Item] failed for the [N]th time as well ([the limit that is full]). Human intervention is needed — how do we continue?"*
- **a diverging loop** (the global backstop is full) → *"The fixing loop has not converged for [N] rounds — a different element fails in every round: [the items]. Human intervention is needed — how do we continue?"*

In neither case continue the fixing without an answer from the user. In each of them: **a single closing commit** (VD8), and the `[validate-loop]` marker and the `## <sec:validation_fixes>` stay on `tasks.md` to signal the stuck state.