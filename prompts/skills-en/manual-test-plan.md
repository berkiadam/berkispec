---
name: bs-manual-test-plan
description: "berkispec - helper command. Assembling the manual test plan of the cycle: component startup, test data, manual call sequences (curl + .http), expected results, and where the results of the automated tests go. Prerequisite: analyze-report.md is PASS. Not a phase: it is not part of the 00-09 process, it can be called any time after the analyze, and it can be re-run any time."
prerequisites:
  - "specs/cycle-NN-<cycle-name>/analyze/analyze-report.md <field:f_status>: PASS"
output:
  - "specs/cycle-NN-<cycle-name>/manual-test-plan.md — the manual test plan (in <status:mtp_planned> or <status:mtp_as_built> mode)"
scripts:
  - "scripts/manual-test-gate-check.py — the deterministic quality gate"
shared:
  - "shared/phase-commit.md"
---
# Manual test plan (`bs-manual-test-plan`) — a helper command
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

This is **not a phase:** it is not part of the `00–09` chain, it **does not touch** the status chain of the cycle (`spec.md` / `plan.md` / `tasks.md`), and it can be re-run any time. It produces a single thing: `specs/cycle-NN-<cycle-name>/manual-test-plan.md`, with which a **human** can walk through the functionality of the cycle by hand — starts the components, runs the call sequences, compares what came back with what was expected, and knows where to look for the results of the automated tests.

**You do not explore, you assemble.** About 90% of the content is already existing data in the documents of the cycle — your job is to collect it, carry it over without truncation, and arrange it into a human execution order.

---

## Cheat sheet

| Section | In one sentence |
|---|---|
| Prerequisite (MT1) | `analyze-report.md` = `PASS`. Without it **STOP** and back to `05` — that <sec:environment_coords> of `plan.md` is filled in is guaranteed by the mechanical gate of `05`, and that is the single real input of this phase. |
| Two modes (MT3) | It is decided from the status of `tasks.md`: `<status:mtp_planned>` (there is no finished code yet) or `<status:mtp_as_built>` (after the validation). The user may override it. |
| Coverage (MT6) | Every test group leads back to a `DoD-NN` or to a spec test case, and every `DoD-NN` has a group **or** an MT10 justification. **You do not invent a new requirement.** |
| Output (MT4) | **Exclusively** `manual-test-plan.md`. There is no result file, no execution log, and neither `07` nor `09` gates on it. |
| Re-run (MT7) | It merges without a question: the manual content stays, the generated sections are refreshed, the change goes into <sec:mt_changelog>. |
| Gate (MT5) | `manual-test-gate-check.py` — deterministic. `exit 0` → commit; `exit 1` → fixing (max 2 rounds); `exit 2` → STOP. |
| Commit (MT9) | `cycle-NN: manual-test-plan`. **During a loop a path-scoped `git add`** — only `manual-test-plan.md`. |

---

## What it produces — and from what

| What the manual test plan needs | The existing source |
|---|---|
| starting a component, port, health endpoint | `plan.md` → <sec:environment_coords> / <sec:components_endpoints> (KO1) |
| REST call sequences, `curl` | `plan.md` → <sec:rest_calls_examples> |
| test data, users, passwords | `plan.md` → <sec:test_api_users> + <sec:other_parameters> (the TC5 secret rule) |
| network prerequisites | `plan.md` → <sec:network_access_prereqs> |
| what we test with a group | `spec.md` → <sec:test_specification> + <sec:definition_of_done> (`DoD-NN`) |
| automated test commands | `plan.md` → <sec:machine_run_table> |
| where the results go | `conventions.md` → `## <sec:cv_test_reporting>` (TR3 + the TR5 round-folder marker) |

---

## <field:f_prerequisite>

0. **Cycle identification:** if the user gave a cycle/file, use that; otherwise offer the most recent `specs/cycle-*` folder for confirmation — <!-- INCLUDE:lang/common.md#ciklus-beazonositas --> — and wait for the answer before moving on.

1. **`conventions.md` existence check:** read `conventions.md` in the root of the project. If it does not exist, **STOP** — tell the user to return to the `00` project initialization phase, and do not continue.

2. **🔴 The analyze gate (MT1):** read the `<field:f_status>` field of the header of `specs/cycle-NN-<cycle-name>/analyze/analyze-report.md`. _(If the file is not there, look at the old place in the root of the cycle as well — `specs/cycle-NN-<cycle-name>/analyze-report.md`.)_ **If the file does not exist, or its status is not `PASS`, STOP:**

   <!-- INCLUDE:lang/manual-test-plan.md#analyze-kapu-stop -->

   **Do not start writing a plan**, and do not try to invent the missing coordinates: without a `PASS` it is not guaranteed that <sec:environment_coords> is filled in, and the plan is usable precisely because it stands there with concrete values.

3. **Working-tree check (only with VCS):** run: `git status --short`. If the status of `tasks.md` bears an `[analyze-loop]` or `[validate-loop]` marker, **do not offer the folder of the cycle for a commit** — signal in one line that a loop is running, and that the phase-closing commit is path-scoped for that reason (MT9). Otherwise it is enough to signal the uncommitted items in one line: this command only writes a new file, it does not touch the existing work. (In a No-VCS project the step is left out.)

---

## Choosing the mode (MT3)

The mode is decided by the status of `tasks.md`:

| `tasks.md` status | Mode |
|---|---|
| `<status:ready_for_implement>` (or the file is missing, or it bears an `[analyze-loop]` marker) | `<status:mtp_planned>` |
| `<status:ready_for_validate>` or `<status:done>` (with a `[validate-loop]` marker as well) | `<status:mtp_as_built>` |

**Write out the chosen mode to the user in one line**, with the justification, before you start working:

<!-- INCLUDE:lang/manual-test-plan.md#mod-bejelentes -->

The user may override it (with a `mode: planned` / `mode: as-built` input) — in that case their choice is the valid one, and write this out in one line as well.

---

## Reading the input (minimal context)

Read **only** these sections, not the whole files:

- **`plan.md`:** <sec:environment_coords> (and its subsections: <sec:components_endpoints>, <sec:rest_calls_examples>, <sec:test_api_users>, <sec:other_parameters>, <sec:network_access_prereqs>), <sec:testing_strategy>, <sec:machine_run_table>;
- **`spec.md`:** <sec:definition_of_done> (with the `DoD-NN` identifiers), <sec:test_specification>;
- **`conventions.md`:** `## <sec:cv_test_reporting>` (together with the TR5 `<field:f_artifact_path_base>` marker), `## <sec:cv_git_conventions>` (to decide the No-VCS branch).

> **🔴 Carrying over without truncation (the KX2/KX3 analogy).** The `curl` examples, payloads, users, passwords and commands taken from <sec:environment_coords> are carried over **verbatim, with their full value**. It is **FORBIDDEN** to condense them, to replace them with a placeholder (`<TOKEN>`, `...`), or to replace them with a "see the plan" reference: `manual-test-plan.md` is read by a **human** who does not open `plan.md`. For the paths the RP1 convention applies — an absolute, machine-specific or `file://` form is **FORBIDDEN** in the document.

---

## The as-built check — only in `<status:mtp_as_built>` mode

For every coordinate carried over (route, port, env variable, config key) **find the real source in the code** (route definitions, config files, compose/manifest). On a difference:

- **the code wins** — the real value goes into the plan;
- the difference goes into <sec:mt_changelog> in the form `plan.md <sec:environment_coords>: <old> → code: <new>`;
- **signal in one line** in your answer to the user that the coordinates of `plan.md` are stale — this is a signal for the promotion of `08-doc-sync` too.

In `<status:mtp_planned>` mode this step is **left out**: do not read code and do not guess, the header warning states that the steps are not verified on real code:

<!-- INCLUDE:lang/manual-test-plan.md#mod-tervezett-figyelmeztetes -->

---

## The skeleton of the document (MT11)

The shared context comes first (startup, test data, automated tests), and after it one **self-contained** block per test group. Follow this skeleton:

<!-- INCLUDE:lang/manual-test-plan.md#dokumentum-sablon -->

**Fixed formal rules** (the gate builds on these):

- the form of the test-group header is `### TG-NN — <name>  (DoD-NN[, DoD-NN...])`;
- the `TG-NN` identifiers are **unique** within the file and numbered without gaps;
- for a UI test the "Call / operation" cell contains the **exact URL** and the click step; for REST a `curl`, and the group also has at least one code block with an `http` infostring (the VSCode REST Client / IntelliJ `.http` form);
- the `<field:f_expected_result>` cell of every step row is **concrete** (a status code, a field name, a screen element) — "it works" and "it runs flawlessly" are not acceptable;
- whatever is not applicable for this cycle gets a `—`; **you may not leave a cell empty**.

---

## Forming the test groups (MT6 + MT10)

1. Every group proves **one coherent behavior**, and its header lists the `DoD-NN` items it covers.
2. The content of the group is assembled from the cases of <sec:test_specification> in `spec.md` and from the sequences of <sec:rest_calls_examples> in `plan.md` — **you do not invent a new requirement**, and you do not add an exploratory group.
3. Every group has **test data** (referring to section 2 or in place) and a **cleanup** (`<field:f_cleanup>`).
4. **A `DoD-NN` that cannot be tested manually (MT10):** whatever cannot be checked by hand (an internal refactor, a lint rule, a coverage threshold, a CI configuration) goes into the <sec:mt_not_manual> table: `DoD-NN` + **a one-sentence justification** + which automated test or gate covers it. Do not invent a meaningless manual step instead.
5. The <sec:mt_coverage> table lists the `DoD-NN → TG-NN` pairs, and it **has to match** the group headers.

---

## The automated tests and the place of the test results

- The rows of the <sec:mt_automated_tests> table are the rows of <sec:machine_run_table> in `plan.md` — the **command is carried over verbatim**.
- Resolve the place of the result from the `## <sec:cv_test_reporting>` table of `conventions.md` and from the TR5 `<field:f_artifact_path_base>` marker.
- **`<field:f_test_results_so_far>`:**
  - in `<status:mtp_planned>` mode the **future** paths, with a `_(does not exist yet)_` mark;
  - in `<status:mtp_as_built>` mode the **actually existing** files (`test-report/implement/check-log.md`, and if there has already been a validation, `test-report/validate/round-NN/...`). **List only what is really there** — the gate checks this.

---

## Re-run — a silent merge with a change log (MT7)

If `manual-test-plan.md` already exists, work **without a question**, and signal in one line:

<!-- INCLUDE:lang/manual-test-plan.md#ujrafutas-bejelentes -->

- refresh the generated sections (1–5.);
- **keep** the **manual additions** in them (a line or paragraph that cannot be traced back to the inputs);
- **do not renumber** the `TG-NN` identifiers — the existing ones stay, the new ones go to the end of the row;
- write a <sec:mt_changelog> entry: date, mode, what you added / modified / what became stale and why.

---

## The quality checklist (before the gate)

- [ ] The `<field:f_status>` field of the header is one of the two allowed values, and the `<field:f_mode>` field justifies it.
- [ ] All six mandatory sections are present, and in sections 1–4 there is **no placeholder and no empty table cell**.
- [ ] Every component row has a concrete startup command.
- [ ] Every `TG-NN` group has a `<field:f_what_we_test>`, a `<field:f_prerequisite>`, a step table and a `<field:f_cleanup>`, and every step has a concrete expected result.
- [ ] Every `DoD-NN` is covered: in a group header **or** in the <sec:mt_not_manual> table, with a justification.
- [ ] Where there is a `curl`, there is an `http` code block as well.
- [ ] There is no absolute, machine-specific or `file://` path (RP1).

---

## The deterministic gate (`manual-test-gate-check.py`)

After the prompt-level list, running the gate is **mandatory** — it measures the mechanically decidable part of the points above, without false alarms:

<!-- INCLUDE:shared/python-cmd.md -->

```bash
python3 <platform-scripts-mappa>/manual-test-gate-check.py specs/cycle-NN-<cycle-name>
```

**Exit code:**

- **`0`** → clean, the commit may go.
- **`1`** → there is a `✗` line: fix the points written out, and run it again. **At most 2 fixing attempts**, after that **STOP**: write out the output of the gate and ask.
- **`2`** → a usage or prerequisite error (a non-existent cycle folder, a missing `manual-test-plan.md`, an invalid header status) → **STOP**, with the line to be supplied. Do not work around this on your own.

---

## Stopping rules

1. **There is no `PASS` analyze report** (Prerequisite 2.) → STOP, with the `/bs-analyze` command.
2. There is a **placeholder or an empty cell** in the <sec:environment_coords> section of `plan.md` that cannot be resolved from the code either → **STOP**, and signal that one has to go back to `03`. (The gate of `05` should rule this out — if it happens anyway, that is telling.)
3. Neither **a manual step nor an MT10 justification** can be formed for a `DoD-NN` → **ask** (one question at a time, and wait for the answer).
4. The gate **fails even after two fixing rounds** → STOP, with the output of the gate.
5. The commit check **fails twice** (see step 4 of the *Phase-closing commit* block) → STOP.

---

## The phase-closing commit (MT9)

The value of `<PHASE-TAG>` is: **`manual-test-plan`** — so the message of the commit is `cycle-NN: manual-test-plan`.

> **⛔ Loop guard — a mandatory deviation from the shared block.** If `tasks.md` bears an `[analyze-loop]` or `[validate-loop]` marker, the `git add` of step 3 may be **exclusively** this:
>
> ```bash
> git add specs/cycle-NN-<cycle-name>/manual-test-plan.md
> ```
>
> **NEVER** stage the folder of the cycle and **never** use `-A`: according to the VD8 rule of `07-validate` there is **no** intermediate commit during the loop — `test-report/`, the `DoD-NN` check marks and the fixing tasks stand uncommitted on purpose, and the interruption handling of `07` recognizes from this that it is continuing an interrupted loop. A naive `git add specs/cycle-NN-<cycle-name>/` would **pull the rug out from under `07`**. In that case the `git status --short` check of step 4 also applies to this one file only.

> **Step 2 of the shared block (writing the status) means the OWN `<field:f_status>` field of `manual-test-plan.md` here** (`<status:mtp_planned>` / `<status:mtp_as_built>`) — **not** the status of `spec.md` / `plan.md` / `tasks.md`. This command does not touch the status chain of the cycle.

<!-- INCLUDE:shared/phase-commit.md -->

---

## The closing feedback

The PE1 section of the shared block (the phase boundary + the command of the next phase) is **not applicable** here: this is not a phase, there is no "next phase". The command ends with the closing message:

<!-- INCLUDE:lang/manual-test-plan.md#zaro-uzenet -->

---

## What NOT to do

- **Do not write a result file** (`manual-test-results.md`) and do not keep a checkable execution log (MT4) — the fate of the bugs found belongs to the user.
- **Do not touch the status chain of the cycle** and the artifacts of `07` / `08` / `09`.
- **Do not invent a new requirement** and do not add an exploratory test group (MT6).
- **Do not condense** the `curl` calls, payloads and commands taken from the plan.
- **Do not write the secrets into it**: a cluster, registry, VPN, IAM or production credential appears only as a pointer (TC5).
- **Do not ask** on a re-run whether to refresh the file (MT7) — merge without a question.
