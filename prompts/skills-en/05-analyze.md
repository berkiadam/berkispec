---
phase: 05
name: bs-analyze
description: "berkispec - 05. Use it before the implementation (Phase 05), when tasks.md is 'Ready for implementation'. A cross-phase consistency gate between spec.md/plan.md/tasks.md: with subagents (analyzer, *-fixer) it identifies and automatically fixes the contradictions. It creates 'analyze-report.md' (PASS/FAIL)."
prerequisites:
  - "specs/cycle-NN-<name>/tasks.md status: <status:ready_for_implement>"
output:
  - "specs/cycle-NN-<name>/analyze/analyze-report.md (PASS / FAIL)"
  - "specs/cycle-NN-<name>/analyze/analyze-task.md (the fixing list approved by the user)"
prev: bs-write-tasks
next: bs-implement
subagents:
  - "agents/analyzer.md"
  - "agents/analyzer-exec.md"
  - "agents/spec-fixer.md"
  - "agents/plan-fixer.md"
  - "agents/tasks-fixer.md"
shared:
  - "shared/phase-commit.md"
scripts:
  - "scripts/analyze-gate-check.py"
---
# 05 — Analyze (cross-phase consistency check + self-healing loop)
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

We develop software in spec driven development. The development is split into cycles. Every cycle is an independently developable, independently testable subunit of the complete implementation.

This is **phase 5 (0–9)** of the process: 0-init · 1-cycles · 2-spec · 3-plan · 4-tasks · **5-analyze ←** · 6-implement · 7-validate · 8-doc-sync · 9-review.

---

## Cheat sheet

| Section | In one sentence |
|---|---|
| Prerequisite | `tasks.md` = `<status:ready_for_implement>`, `conventions.md` exists, a clean working tree. |
| A fresh base (BR1) | If the main branch moved ahead since the branch of the cycle, the phase **brings it in** (rebase / merge according to the push state) BEFORE the analyze — otherwise it would validate on an outdated tree. If it did not move ahead, it does not touch the history. |
| Your role | **Orchestrator (read-only):** you do not edit a design document yourself — you conduct, write a report, ask, and switch statuses. |
| The mechanical gate | Before every run `analyze-gate-check.py` (plan ID ↔ task reference, marker, `⟂`, `DoD-NN`, mandatory tables, **artifacts being run, plan anchors, artifact voice**) — its `<status:must_fix>` hits go into the loop with the target phase given by the script, its `## <sec:inventory>` block is the input of `analyzer-exec` (AG3), and `--emit-slices` cuts the slice of each of the three semantic rounds (SH1). |
| The analyzer diagnosis rounds | The read-only cross-check is done by **four parallel rounds**: the `agents/analyzer.md` subagent three times, with three different scopes (`s1-dup-underspec` = categories 1+3, `s2-coverage` = 2+5, `s3-conventions` = 4), plus the `analyzer-exec` subagent (category 6, executability) — you merge the four finding lists (E/SH1). |
| The fixer subagents | The fixing is done by the `agents/{spec,plan,tasks}-fixer.md` wrappers (= the Fix mode of phase 02/03/04); they write the design documents, and **run the mechanical gate themselves** before returning (GS1). If every `<status:must_fix>` is local, the fixers are started **in a single message, in parallel** (LF1). |
| Live report (AR1) | `analyze-report.md` is produced **immediately after the very first diagnosis** with an `IN_PROGRESS` status, with a plain-language tick list (*what is wrong · why it blocks · target phase · state*) — not at the end of the loop. Every step of the loop refreshes it, so the user can see what the phase is working on right now. |
| Triage stop (TR1) | **After every diagnosis round** the loop stops, and in a single question the user decides which **new** `<status:must_fix>` items are to be fixed. The approved ones go onto `analyze-task.md`, the dismissed ones into the report with a `dismissed (triage)` state — and they do not block the `PASS`. Purely mechanical (gate) items get onto the list without asking. |
| Fixing list (`analyze-task.md`, TR1) | The fixers work **exclusively** on the open items of `analyze-task.md`. During a round the loop **does not ask** — it works through the list; the new items found in a new round come up in the next triage. |
| Analysis folder (AD1) | **Every** file of the analysis lives in the `specs/cycle-NN-<cycle-name>/analyze/` subfolder: `analyze-report.md`, `analyze-task.md`, `slices/` and every helper file. |
| Result | `analyze-report.md` PASS or FAIL, with a severity classification + <sec:loop_log>. |
| One analyzer round / iteration | Every round is **full within its own scope**, and a `PASS` requires all four of them to have run; from the 2nd round it gets the previous `<status:must_fix>` list (verification) and the `git diff` (navigation) — but it does not narrow itself down to them (D10). The downstream re-derivation is **conditional** (D11). |
| FAIL | **A self-healing loop starts:** the earliest affected target phase → a fixer subagent → downstream re-derivation (`02→03→04`) → a re-analyze, until PASS — with `max X = 3` iterations. |
| Stopping for a question | If the fixer reported an open question: the orchestrator (you) asks the user with a `PHASE/Qnn` header, writes in the answer, and restarts the fixer — the loop **continues** (this is not an error). |
| PASS | On to the 06-implement phase. Commit: a single `cycle-NN: 05-analyze` at the end of the loop. |
| Phase-closing commit | **Mandatory, on every closing branch** (PASS and FAIL alike) — according to the procedure of the *Phase-closing commit* section (PC1). Without a commit the phase is not closed. |

---

## Your role: orchestrator (a read-only invariant)

`05-analyze` is a **conducting** phase. Keep two things in mind throughout:

1. **You do not edit a design document yourself** (`spec.md`, `plan.md`, `tasks.md`). Every content fix is done by the fixer subagents (= the Fix mode of phases 02/03/04). The only file you write is `analyze-report.md`, and your only direct modification on the design documents is **switching the status field** (putting the `[analyze-loop]` marker on and taking it off, see below).
2. **The read-only diagnosis belongs to the diagnosis rounds** (`analyzer` × 3 scopes + `analyzer-exec`). You read the merged finding list and decide about PASS / FAIL, then in case of a FAIL you conduct the fixing loop.

This way the responsibility of the phase is clean: **diagnosis (analyzer) → conducting (you) → fixing (the fixers)**, each in its own place.

---

## The folder of the analysis (AD1)

**Every** file produced during the analysis goes into the `analyze/` subfolder of the cycle — the root of the cycle belongs to the design documents (`spec.md`, `plan.md`, `tasks.md`, `*-questions.md`), not to the by-products of the analysis:

```
specs/cycle-NN-<cycle-name>/
├── spec.md · plan.md · tasks.md · *-questions.md      ← the design documents (written by the fixers)
└── analyze/
    ├── analyze-report.md    ← the diagnosis and the audit trail (you write it)
    ├── analyze-task.md      ← the approved fixing list, the work list of the fixers (you write it)
    └── slices/              ← the output of the gate's `--emit-slices`; it hides itself with `.gitignore`
```

If you need any analysis helper file (a note, an intermediate list), that goes **here** as well — no analysis file may end up in the root of the cycle. The phase-closing `git add specs/cycle-NN-<cycle-name>/` stages the whole subfolder; `slices/` stays out, because it hides itself.

> **Older cycles:** if `analyze-report.md` stands in the **root** of the cycle from an earlier run, **move it** (`git mv`) into the `analyze/` folder at the beginning of the phase, and note it in one line in the report. A report living in two places would confuse the continuation logic (and the gate of `06`) as well.

---

## <field:f_prerequisite>

0. **Identifying the cycle:** if the user gave a cycle/file, use that; otherwise offer the most recent `specs/cycle-*` folder for confirmation — <!-- INCLUDE:lang/common.md#ciklus-beazonositas --> — and wait for the answer before moving on.

1. **`conventions.md` existence check:** read `conventions.md` in the root of the project. If it does not exist, **STOP** — tell the user that they should return to the `00` project initialization phase, and do not continue.

2. **Tasks status:** read the status of `specs/cycle-NN-<cycle-name>/tasks.md`. **If it is not `<status:ready_for_implement>`, STOP** — the task list is not closed yet. Report it, and they should return to the `04` tasks phase. (Exception: if the status bears a `<status:ready_for_implement> [analyze-loop]` marker, an earlier analyze loop was interrupted — see "Continuing after an interrupted run".)

3. **Working-tree check (only with VCS):** run: `git status --short`. If there are uncommitted changes:
   - List the affected files.
   - Report: *"The analysis loop may modify the design documents; a clean working tree makes it easier to follow what changed."*
   - Ask: *"Should I commit these now, or shall I continue?"* — one question, wait for the answer, then continue. (In a No-VCS project it is skipped.)

4. **🔴 A fresh base (BR1 — only with VCS, conditional):** the value of the analyze comes from measuring the plan against the **actual** code base (anchors `path:line`, the existence of the artifacts being run, plan↔code consistency). If the main branch has moved ahead in the meantime (another cycle got merged, a hotfix arrived), you would be validating on an outdated tree — the green result is false. Check it:

   ```bash
   git fetch origin
   git log --oneline HEAD..origin/main
   ```

   _In a repo without a remote (local only) work with the local `main` instead of `origin/main`, without `git fetch`. In place of `main` goes the **<field:f_main_branch>** field of the `## <sec:cv_git_conventions>` of `conventions.md`._

   _The command **deliberately contains no `$( )` substitution**: `HEAD..origin/main` yields the same commit set as the `merge-base` form, but several CLIs (e.g. Antigravity/Gemini) do not allow command substitution to be allowlisted for security reasons — such a line would ask for permission on every run._

   - **An empty list** → there is nothing to do, continue. (In the parallel planning window this is the normal case: while the other cycle is not merged, the main branch does not move.)
   - **Not empty** → bring the main branch into the branch of the cycle **BEFORE the analyze**:
     - the branch is **not pushed / there is no PR for it** (`git rev-parse --verify origin/feature/cycle-NN-<cycle-name>` gives an error) → `git rebase origin/main`,
     - the branch **is pushed or a PR is open** → `git merge origin/main` (a rebase would require a force push).

     **Before** bringing it in, note the tip of the branch of the cycle (`PRE=$(git rev-parse HEAD)`). Report in one line what you brought in (`git log --oneline` about the commits brought in) — **do not ask for separate permission**, you are working on the own branch of the cycle, this is not destructive. **In case of a conflict, STOP**: list the conflicting files, and ask for a decision; do **not** resolve the generated documents (`docs-generated/`) and `specs/test-conventions.md` by hand — that is the business of `08`.

   - **After bringing it in, produce the REBASE FILE LIST (BR1/a):**
     ```bash
     git diff --name-only "$PRE" HEAD -- . ':(exclude)specs/*'
     ```
     This is the list of the **source, test and config files** that arrived from another cycle/hotfix. If it is not empty, it has to get into the input of **all four diagnosis rounds** (see *"The four diagnosis rounds"* → **The rebase file list**). If it is empty (only the `specs/` folders of other cycles came in), there is nothing to do.
     _Hand over a file list, **not the whole diff** — the subagent reads the necessary details itself (AG3)._

   > **Do not rebase unconditionally.** If the list above is empty, you do **not touch** the history of the branch — the analyze may run several times in the self-healing loop, and a needless rewriting of the history would provoke a force push on a pushed branch.

   **Why here:** this phase is the gate of **base consistency**. This is why the parallel-cycle gate of `06` (PW2) does not prescribe a separate rebase step, but requires that there be a **fresh `05` `PASS`** before `06` — the bringing in is done by `05` itself.

---

## Continuing after an interrupted run

**The first analyze run of the continuation starts WITHOUT a verification list** — you cannot know where the fixing was interrupted, so there is no meaningful "previous round". The run — as always — is full, and the mechanical gate (step 0) runs as well.

The **diagnosis** of the analyze is read-only, but the loop may already have modified the design documents. The continuation is made reconstructable together by the `[analyze-loop]` status marker, the open questions of `*-questions.md`, the open items of `analyze/analyze-task.md` and the Loop log of `analyze-report.md`. **`analyze-task.md` is the strongest anchor:** what is on it has already been approved by the user — continue it without asking; what is in its `Dismissed items` section must not be reopened. The decision tree — **in this order**:

```
1. Does one of the design documents (spec.md / plan.md / tasks.md) bear an
   `[analyze-loop]` status marker?
   → Yes → the loop was interrupted. Do NOT start a new analysis from scratch.
     a/0) Read analyze/analyze-task.md: the open [ ] items are the approved
        work that is not done yet. Continue with those, WITHOUT a new triage.
     a) Read the <sec:loop_log> section of analyze-report.md:
        at which iteration and at which phase it stopped.
     b) Read the affected *-questions.md: is there an open [ ] question?
        → If yes: the loop stopped at a question. Put the question to the
          user (with the phase header), carry it over, then continue the loop
          at the same iteration.
        → If there is no open question: the fixer finished the correction, but
          the re-derivation or the re-analyze was left out. Continue with the
          downstream re-derivation, then run the analyze again.

2. There is no [analyze-loop] marker, but analyze-report.md exists.
   → If its status is PASS: the analysis is closed, on to 06.
   → If its status is FAIL and there is no marker anywhere: the loop closed by
     giving up at max X (see the Loop log of the report). Report the stuck
     state to the user — do not start a new loop automatically without confirmation.
   → If its status is IN_PROGRESS: the report is LIVE (AR1), not broken — the items
     in it are real, only the loop did not run to the end. Do not throw it away and
     do not overwrite it: read from its `Current step:` field and from the `State:`
     fields of the items where it stopped, and continue from there. If the
     `Triage (TR1)` field is filled in, the triage has happened: do not ask
     again, and do not reopen the dismissed items.
   → If the report looks interrupted (not every category is filled in), its status is
     NOT IN_PROGRESS, and there is no marker: delete the partial report, and start the
     analysis again.

3. There is no analyze-report.md and no marker.
   → Start the analysis according to "What you have to do".
```

---

## What you have to do

Check that the design documents of the cycle (`spec.md`, `plan.md`, `tasks.md`) are **consistent with each other and with `conventions.md`** before the implementation starts — and if they are not, **conduct their correction** in a self-healing loop, until they become consistent.

**Do not implement anything.** This is the sanity check (and, if needed, a fixing loop) before the implementation.

The diagnosis looks for problems in **5 categories** (done by the three semantic `analyzer` rounds, split by scope — see "The four diagnosis rounds"):

1. **Duplications** — the same decision several times within the plan; `tasks.md` describing the test case steps of the plan again; a redundant task. **Taking over the elaborated artifact of the spec into the plan verbatim is NOT a duplication** (KX3) — that is the mandatory self-containedness.
2. **Ambiguity** — vague concepts, missing metrics, an acceptance criterion that cannot be measured.
3. **Under-specification** — a missing acceptance criterion, an undefined component, a plan section that cannot be assigned to a task.
4. **Convention conflicts** — a deviation from `conventions.md` (tech stack, naming, test tool, merge strategy, structure).
5. **Coverage gaps** — the requirement ↔ task assignment: is there a spec requirement with no task belonging to it, or a task that cannot be traced back to the plan.

---

## Context loading rules

- The cross-check requires reading many files together — **starting all four diagnosis rounds is mandatory, in a single message, in parallel** (E/SH1): the `analyzer` subagent three times (with the scopes `s1-dup-underspec` = categories 1+3, `s2-coverage` = 2+5, `s3-conventions` = 4) and the `analyzer-exec` subagent once (category 6). Each of them returns **exclusively the structured finding list** (the raw file content does not burden the main context).
- Their system prompt is given by the **installed agent definition** of the platform (`analyzer`, `analyzer-exec`) — call them by these names, do not look for them as files in the project. The three semantic rounds use the **same `analyzer` definition**; the difference is the scope, which you give in the launching message.
- **Hand over the corresponding part of the gate output to every round, verbatim:**
  - `analyzer-exec` → the **`## <sec:inventory>`** (`<status:mk_artifact>` / `<status:mk_anchor>` / `<status:mk_tone_suspect>` / `<status:mk_test_promise>` / `<status:mk_destructive>`, AG3): this replaces the repo and document exploration, which was the main cost of category 6;
  - `s2-coverage` → the **`## <sec:coverage_matrix>`** (AG4): the `DoD-NN → [P-…] → task` chain ready-made, so that it does not derive it again;
  - **all three semantic rounds** → the **path of their own slice** (`analyze/slices/<scope>.md`, SH1) **and the name of their scope**. Give the path, **not the content of the slice**: the whole point of the slicing is that the text of the quartet does not reach the subagent through the main context.
- You merge the output of the four rounds (see "The four diagnosis rounds"), and decide about PASS / FAIL based on that.

  > **🔴 If one of the diagnosis rounds does not run, or does not give a findings list:** **do not silently carry out the cross-examination yourself** — the whole value of the phase is that the diagnosis is **independent** of the orchestrator. The **type of the error** decides what to do — do not deliberate, look at the text of the error message:
  > - **A platform limit** (the text mentions a quota/allowance/limit — e.g. "usage limit", "quota exceeded", "reached its usage limit", or an allowance reset date): **do NOT retry.** The second call runs deterministically into the same thing. Jump straight to the STOP + human branch, and **copy the error message verbatim** into the question (together with the reset date) — the decision (an admin permission, waiting for the reset, another model pool) belongs to the user.
  > - **Every other error** (a timeout, a one-off crash, an empty answer): retry **once**. If only **one** of the rounds failed, restart **only that one** — do not discard the findings lists of the other three.
  >
  > If it cannot be run even so: **STOP + human** — ask whether I should retry it, or carry out the missing categories directly in the main agent according to the aspects of `analyzer` / `analyzer-exec`. **Name the scope** of the missing round in the question (which categories were left without a diagnosis).
  >
  > **If you go down the fallback branch, marking the origin of the diagnosis is MANDATORY.** The main agent works on a different model and in a narrower context than the subagent, and on top of that it is the orchestrator itself — so the diagnosis **loses its independence**, and is systematically a weaker finding set. One line should go into the header of `analyze-report.md`: **Diagnosis:** the main agent (fallback) — <subagent> could not be run: <reason>. A PASS produced this way is **not of full value** — note there that making up for the subagent diagnosis is recommended.
- You start the fixing fixer subagents also as Task tool subagents, with their own wrapper prompt (`agents/spec-fixer.md`, `agents/plan-fixer.md`, `agents/tasks-fixer.md`) — see "The self-healing loop".
- **The `*-input-from-prev.md` files (IP1) are inputs too:** the subagent reads the `spec-`/`plan-`/`tasks-input-from-prev.md` files in the folder of the cycle (whichever exists), and reports an open `[ ]` item **as a coverage gap**. The reason: an open item means that an earlier phase handed over a piece of information that the consuming phase neither built in nor dropped — this is just as much a gap as a requirement without a task.

  > **05 does NOT examine `validate-input-from-prev.md`:** its consumer is 07, which runs after the analyze — there it is rightfully still open.
  >
  > **The fix modes of the loop (the fixer subagents) still do not read and do not write these files** (IP1/6). This check is therefore a **diagnosis**: the `<status:must_fix>` names the deficiency of `spec.md`/`plan.md`/`tasks.md` (what was left out), it does not ask for the handover file to be ticked off. Ticking off is the business of the normal (non-fix-mode) phase run.

---

## Severity classification

Every finding is **<status:must_fix>** or **<status:suggestion>**:

- **<status:must_fix>** = it blocks the implementation (an implementation built on a faulty base is risky): a real duplication, a coverage gap, a convention conflict, an undefined component, an acceptance criterion that cannot be decided.
- **<status:suggestion>** = it does not block, it is only a suggested refinement (a rephrasing, a smaller clarification).

**The condition of a PASS:** there is no `<status:must_fix>` finding. If there are only `<status:suggestion>`s, the result is a PASS (the user may decide about the suggestions, but they do not start a loop).

> **With a triage (TR1):** the condition of a `PASS` is, more precisely, that no **non-dismissed** `<status:must_fix>` item is left. An item dismissed by the user **stays** in the report with a `dismissed (triage)` state (the audit trail), but it neither blocks nor starts a loop.

---

## Step 0 — the mechanical gate (`analyze-gate-check.py`) — BEFORE EVERY analyze run

The checks that can be decided mechanically are **not done by the `analyzer` subagent**, but by a script — deterministically, cheaply, without false alarms:

<!-- INCLUDE:shared/python-cmd.md -->

```bash
python3 <platform-scripts-mappa>/analyze-gate-check.py specs/cycle-NN-<cycle-name> --emit-slices
```

_(Run from the root of the project, the `--repo-root .` and the `--conventions conventions.md` defaults are fine. If `conventions.md` is elsewhere, give it: `--conventions <path>` — without it the `G1` gate-configuration check is skipped.)_

**What it covers:** plan ID format/uniqueness (P1), the existence of the task→plan reference (P2), a reference to a non-existent ID (P3), an ID without a task (P4), a reference by ordinal (P5), a marker on every task (T1), `[OPS]` on a repo file (T2), a status-updating task (T3), `⟂` symmetry (T4), an unfilled placeholder in a `[CHECK]`/`[OPS]` command (T5), a missing/duplicated `DoD-NN` (D1), a `DoD-NNb` shaped after-the-fact identifier (D2), the existence of the mandatory tables (S1/S2) — **and the mechanical layer of category 6 (AG3):** the existence of the artifact being run / the creating task (A1 = 6.a), the resolution of a plan `path:line` anchor (A2 = 6.g at file level), the validity of the anchor line number (A2b, a suggestion), the hard floor of artifact voice (A3 = 6.h `🔴`/"Forbidden", a suggestion) — **and further:** the taking over of the elaborated artifacts of the spec (`V1`) and the extent of the test sections (`V2`, KX3), the match of the **test target environment** (`EV1`–`EV5`: is there a declared target environment, does every run category say where it runs, is the target host in the command, is there a reachability probe, and does a non-local category point at localhost), the executability of the plan's **test scenarios** (`TS1`–`TS6`: is there a `TS-NN` block, is it complete, is the call and the expected result concrete step by step, is it free of placeholders, is the `DoD-NN` coverage bidirectional, is the numbering gapless), the path format (`R1`, RP1) and the anchor format (`A2c`, a suggestion), and the **gate configuration moving along** (`G1`, GC1: the cycle touches the report structure, but the `## <sec:cv_test_reporting>` table of `conventions.md` does not move → the TR3 gate of 07 would look in the old place).

**The four blocks of the output:**
- **`## <status:must_fix>`** — line by line `[code] (target phase: NN) message`. Each of them is a `<status:must_fix>`, with the target phase given by the script — add them to the list of `analyze-report.md` **verbatim**. Do not question them and do not re-evaluate them: they are the results of a mechanical check.
- **`## Javaslatok`** — they do not block, they do not start a loop; they go into the `Suggestions` section of the report.
- **`## <sec:inventory>`** — **not a finding, but the INPUT of `analyzer-exec`.** It contains the text of the anchored lines, the state of the artifacts being run and the voice hits requiring a judgement. **Hand it over to the `analyzer-exec` subagent verbatim** — this way it does not have to run `Grep`/`Glob` rounds in the repo (this was the main cost of category 6).
- **`## Szeletek` (SH1)** — **not a finding, but the INPUT of the three semantic rounds.** `--emit-slices` writes the slices into the folder of the cycle (`analyze/slices/s1-dup-underspec.md`, `analyze/slices/s2-coverage.md`, `analyze/slices/s3-conventions.md`); each of them is a verbatim extract of the design documents, cut exactly for the categories of that round. Give the round **the path, not the content.** The folder hides itself with a `.gitignore`, so the phase-closing commit does not stage it, and it does not disturb the working-tree check either.

**Exit code:**
- **`0`** → there is no blocking mechanical finding (there may be suggestions, an inventory and slices in the output); start the four diagnosis rounds, each with the block belonging to it.
- **`1`** → there is a `<status:must_fix>`; start the four rounds the same way, and handle all the finding lists together in the loop.
- **`2`** → a usage error (a missing cycle folder or document) → STOP, report it to the user.

**The gate runs in every iteration** (after the fixing as well) — this way a mechanical regression cannot slip through.

> **The `analyzer` no longer gets a separate task for these.** If it does return such a finding, it is a duplicate: the output of the script is authoritative.

---

## FAIL — category → target phase mapping

A cheaper LLM has to be given a concrete target, not "back to the appropriate phase". The category of the `<status:must_fix>` finding determines the fixing target phase (= which fixer subagent you start):

| Category | Target phase (fixer) | Reason |
|---|---|---|
| Duplication | 03 (at design level), 04 (at task level) | to the source of the redundancy |
| Ambiguity | 03 (a technical decision), 02 (a behavioral one — rare) | where the concept has to be clarified |
| Under-specification | 03 (an undefined component), 02 (a missing acceptance criterion) | to the level of the missing decision |
| Convention conflict | 03 (mild), 00 (severe — a `conventions.md` review) | in line with the logic of SK4 |
| A convention conflict where the cycle **deliberately** changes a convention (GC1) | **03** — the plan should plan the update of `conventions.md` (+ **04** for the task) | the decision is already made; this is execution, not a convention review, therefore it does not go back to `00` |
| Coverage gap | 04 (re-assigning requirement ↔ task) | the task list is the incomplete one |
| Coverage gap — an open `*-input-from-prev.md` item (IP1) | the **consuming** phase (02 / 03 / 04 according to the file) | that is where building in the handed-over information was left out |
| An error of the plan reference (PID1): a missing / non-existent `[P-…]` / a reference by ordinal / a `[P-…]` without a task | **04** | the references of `tasks.md` broke |
| An executable plan section has no `[P-…]` identifier (PID1) | **03** | issuing the ID is the business of the plan |
| An unfilled placeholder in a `[CHECK]`/`[OPS]` command (`T5`) | **04** | `06` issues the command verbatim: it would have to guess |
| Scope overreach (SC1): a plan capability has no spec source | **02** (if the capability is needed → a DoD item), **03** (if it is not needed → removing it + `<sec:out_of_scope>`) | without an acceptance criterion it cannot be developed |
| <sec:config_lifecycle> (KF1) is incomplete or missing | **03** | the propagation of the parameter is a design question |
| A spec test case did not map to a plan test case (TP1) / a missing environment preparation (TP3) | **03** | the `test-runner` reads only the plan |
| A missing mandatory table (`<sec:spec_coverage>`, `<sec:reverse_coverage>` → 03; `<sec:plan_coverage>` → 04) | the owner of the table | a table left out = a gate skipped |
| A missing/duplicated `DoD-NN` identifier | **02** | the per-item counter of 07 builds on it |
| An elaborated spec artifact truncated / merged in the plan (KX3 — `V1`/`V2` or semantic) | **03** | the `test-runner` does not read the spec: whatever is left out here will not run |
| A test scenario is missing or not executable (`TS1`–`TS6`) | **03** | `plan.md` is self-contained: both the `test-runner` and the manual test plan work only from it |
| The test does not run on the target environment of the cycle (`EV1`–`EV5`) | **03** | a test running against a local target goes green even if the deployed component never started |
| Path format (RP1 — `R1`) | the owner of the document: **02 / 03 / 04** | an absolute/machine-specific path is meaningless on another machine and in CI |
| The gate configuration does not move with the structure (GC1 — `G1`) | **03** (+ **04** for the task) | the gate reading `conventions.md` (TR3, Sonar) would run with the old value → 07 fails |

**The earliest affected phase wins:** if several categories are FAIL and they point at different target phases, the loop jumps to the **earliest affected phase** (02 < 03 < 04), and re-derives the downstream phases from there — otherwise the later phases would build on a faulty base. (A severe convention conflict points at `00`: this requires a human decision at the level of `conventions.md` — in that case the loop stops and asks, it does not fix automatically.)

---

## Live report (AR1) — the report is produced right after the diagnosis

The most expensive side effect of this phase used to be that the user **could not see what was wrong** during the whole run of the loop: the only thing that showed up on disk was the `analyze/slices/` input slices (gitignored, verbatim cut-outs of the design documents), while `analyze-report.md` was born only at the **end** of the loop. An interrupted or long-running loop therefore left nothing behind that could be read.

**The rule:** `analyze-report.md` is produced **immediately after the first merged diagnosis** — still **before the first fixer is started** — with an `IN_PROGRESS` status, and it is refreshed at every step of the loop. This is your job (orchestrator), and it does not violate the read-only invariant: the report is not a design document.

**When you write / refresh it:**

| Point | What you write into the report |
|---|---|
| After merging the first diagnosis (before the loop) | The full file with an `IN_PROGRESS` status: `Summary`, the **`Items to fix`** tick list with every merged `<status:must_fix>` item, `Suggestions`, `Executability inventory`, the two generated tables. This is produced even if the diagnosis gave a PASS (with an empty Must Fix list). |
| Before starting a fixer (loop points 2-3) | `Current step:` = which fixer runs on which identifiers; the `State:` field of the affected items becomes `being fixed (iter <n>)`. |
| At a question stop (loop point 4) | The `State:` field of the item becomes `question (<PHASE>/Q<nn>)`, and `Current step:` signals that the loop is waiting for the user. |
| After the re-analyze (loop point 6) | The row of every resolved item flips to `[x]`, `State:` = `resolved (iter <n>)`; new findings go to the end of the list as **new** items; the Loop log gets the entry of the iteration. |
| When the loop closes | `IN_PROGRESS` → `PASS` or `FAIL`, `Current step:` = `closed`, the `Loop:` field filled in. |

**What has to be said about an item of the list.** The report is read by a **human** who does not hold the four documents in their head — the name of the category (`coverage gap`, `convention conflict`) is therefore not an explanation on its own. Three fields are mandatory:

- **`The contradiction`** — *what contradicts what.* Name **both sides**, each with its own `file:location` reference: what one document states, and what the other one does. For a one-sided gap (no task for a `DoD-NN`, no acceptance criterion for a component) one of the sides is the **absence**: say what is missing, and which point of which document would expect it.
- **`Why it blocks`** — *what can break in the implementation* if it stays like this. This is what separates a `<status:must_fix>` from a `<status:suggestion>`.
- **`How it would be correct`** — *the target state.* One or two sentences about what the document has to say after the fix for the set of four to be consistent. This is the field that makes the report usable: without it the user knows that something is wrong, but not what would be right.

> **`How it would be correct` is not your design decision.** If the target state **follows unambiguously** from the other three documents (one of the sides is obviously the one left behind), write it down as a statement — this is what the fixer will carry out. If, however, it takes a **real decision** (which side is the correct one, which technological route, how wide the test scope is), then the field carries the **question to be decided**, the `State` of the item is `question (<PHASE>/Q<nn>)`, and you put the question to the user — neither you nor the fixer decides it.

The identifier of the item (`AF-NN` / `AC-NN` / `AN-NN` / `AX-NN`) comes from the diagnostic round and gets into the report **verbatim** — the same one you hand over to the fixer, and the one the survival rule (TS) counts on.

> **An item is never removed from the list afterwards.** A resolved item **stays** with `[x]` and a `resolved (iter <n>)` state — this way the list is a tick list and an audit trail at the same time. For a dismissed item the `dismissed — <justification>` state is mandatory; if an item was made to disappear without a justification, the report cannot be closed.

---

## Triage stop (TR1) — the user decides what gets fixed

The diagnosis is cheap, the fixing is expensive. A `<status:must_fix>` item says that, according to the diagnostic round, the implementation would be built on a faulty base — but whether it is **worth** a fixer round, a downstream re-derivation and a re-analyze for it is **the user's decision**, not the phase's. Without this, the loop regularly burns all three iterations on items (a rephrasing, a cosmetic deviation, a theoretical gap) that the implementation could perfectly well start alongside.

**The rule:** **after every diagnosis round** — including the first one — the loop **stops**, and in a single question the user selects which of the **so far undecided** items they want fixed. The approved items go onto the `analyze-task.md` fixing list; you start a fixer **exclusively** for the open items standing on it.

**Within a round the loop does not ask** (apart from the question stop and the survival rule, see there): it works through the open items of `analyze-task.md`. What a later round finds as **new** comes up in the **next** triage — it does not interrupt the running round.

### When the question is left out

- **There is no `<status:must_fix>`** → there is nothing to triage, the phase closes with a `PASS`.
- **Every item comes from the mechanical gate** (P/T/S/A/C/D codes) → **fix them without asking.** These are deterministic, cheap, and they typically restore the referencing order (`[P-…]` reference, task marker, `DoD-NN` identifier) — exactly what the implementation and the gates of `07` rely on.
- **An already decided item** → you **never ask about it again.** What is on `analyze-task.md` gets fixed; what the user dismissed does not — the triage always asks **exclusively** about the items that are on neither list yet.
- **No new item in the round** → no question, the loop goes on with the list.
- **On a continuation** (an interrupted run): `analyze-task.md` is the anchor — the items on it are already approved, continue them without asking.

### How to ask

A single message, a numbered list — one line and one recommendation per item, nothing more:

```
[TRIAGE · iter <n>/<max X>]
The analysis found <n> NEW items to fix. Which ones should go onto the fixing list?

1. AF-02 · 03-plan · <one sentence: what contradicts what>
   Recommendation: FIX — <half a sentence: what would break in the implementation>
2. AC-05 · 02-spec · <one sentence>
   Recommendation: DEFERRABLE — <half a sentence: why it does not derail the implementation>
...

Answer: `all` · the numbers/identifiers to fix (e.g. `1,3`) · `none`
(The selected ones go onto analyze-task.md; the dismissed ones do not disappear:
they stay in the report with a `dismissed (triage)` state.)
```

At the **first** triage the lead-in of the question is "Which ones should we fix before the implementation starts?"; in the **later** rounds you only ask about the items discovered **newly** in that round.

Put the direct, clickable link of `analyze-report.md` at the end of your answer — the detailed justification (`The contradiction` / `Why it blocks` / `How it would be correct`) can be read there, it does not have to be repeated in the question. This is the **only** point where you ask for several decisions in one message: the nature of a triage is the list, not asking one by one.

**The recommendation is your judgement, and it answers a single question: would this item derail the implementation?**
- **FIX** — without it the developer (or the `06` agent) would implement the wrong thing or nothing: a coverage gap (a requirement without a task), a task that cannot be executed or run (`AX-NN`), a missing or undecidable acceptance criterion, a convention conflict, the truncation of an elaborated artifact of the spec (KX3), a missing or broken `[P-…]` reference.
- **DEFERRABLE** — the item would improve the document, not the implementation: a rephrasing, merging a duplicate, artifact voice (6.h), path format (`R1`), an ambiguity whose practical reading is unambiguous.

You give a recommendation, not a decision: if the user dismisses even a `FIX` item, accept and record it **without arguing**.

### Processing the answer

- **The selected items** get onto the **Items to fix** list of `analyze-task.md` (`added: iter <n>`), and from then on the loop works on those. You always determine the **earliest target phase** from the **open** items of `analyze-task.md`.
- **The dismissed items** stay in `analyze-report.md`: `[x]`, `State: dismissed (triage, iter <n>) — the user did not ask for it to be fixed`, and they also go into the **Dismissed items** section of `analyze-task.md` (that is the memory of the filtering). Fill in the `Triage (TR1)` field of the report header and the log entry of the given iteration.
- **`none` at the first triage** → no loop starts: the report closes with a `PASS` (`Loop:` = `0 / <max X> (triage: not started)`), the `[analyze-loop]` marker is not even put on, but the phase-closing commit is **still mandatory**. In one sentence, state that the implementation starts alongside known, deliberately accepted contradictions, and that the items can be picked up from the report at any time. (`analyze-task.md` is produced in this case as well — with an empty items-to-fix list and a full dismissed list.)
- **A dismissed item never reopens.** The later diagnostic rounds **will find them again** — at the merging (see point 2.a of "The four diagnosis rounds") filter them out based on the **Dismissed items** section of `analyze-task.md`: they must get neither into the triage question nor onto the `<status:must_fix>` list. Without this the loop could not converge, and you would pester the user with the same question round after round.

### The fixing list: `analyze-task.md`

- **Its place:** `specs/cycle-NN-<cycle-name>/analyze/analyze-task.md` (AD1). **For its structure see the "analyze-task.md structure" section.**
- **Its only writer is you** (the orchestrator). The fixers **may read** it, but they do not write it — with a parallel fix batch (LF1) two fixers would write the same file. You still hand over their input (the item list filtered for them), and the ticking off is your business.
- **When you refresh it:** after a triage (adding the new items) · when starting a fixer (`being fixed (iter <n>)`) · at a question stop (`question (<PHASE>/Q<nn>)`) · after a re-analyze (the resolved items get `[x]` + `done (iter <n>)`).
- **The exit condition of the loop refers to this list:** a `PASS` can be given if there is **no open item** on `analyze-task.md`, and the latest diagnosis round did not produce an undecided `<status:must_fix>` either.
- **The relation of the report and the list:** `analyze-report.md` is the **diagnosis and the audit trail** (what is wrong, why it blocks, how it would be correct, what became of it); `analyze-task.md` is the **work list** (what we are doing, where it stands). The same `AF-NN` / `AC-NN` / `AN-NN` / `AX-NN` identifier ties them together — never rewrite the identifier anywhere.

---

## The self-healing loop (the orchestrator loop)

In case of a FAIL you do **not** simply hand control back to the user. Instead, you conduct an iterative fixing loop until there is a PASS, or until you reach the `max X` limit.

### One iteration of the loop

0. **Live report (AR1).** If it does not exist yet, **create** `analyze-report.md` now, with an `IN_PROGRESS` status and the full `Items to fix` tick list — BEFORE the first fixer is started. If it already exists, at this point you only carry over the `Current step:` field and the `State:` field of the affected items. Do not start a fixer without a report: the user would have nothing to read about what the loop is working on.
0.a **Triage stop (TR1) — after every diagnosis round, for the NEW items.** After refreshing the report, and **before the fixer is started**, stop and ask the user which **so far undecided** `<status:must_fix>` items should go onto the fixing list (see "Triage stop (TR1)"). The approved ones go onto `analyze-task.md`, the dismissed ones into its `Dismissed items` section. If there is no new item in the round, this point is left out.
1. **Determining the target phase.** From the categories of the **open** items of `analyze-task.md` (according to the mapping above), determine the **earliest affected target phase** (02/03/04). This is the entry point of the fixer. Every further point of the loop works **exclusively with the open items of `analyze-task.md`**.
1.a **Local fix batch — PARALLEL start (LF1).** Before you step onto the sequential path, classify the open items of `analyze-task.md`:
   - a **local** item = its fix can be carried out within its own document, and it has **no downstream effect by construction**: a refinement of the wording, resolving an ambiguity with a metric, merging a duplicate, artifact voice (6.h), path format (`R1`), a typo, restoring a missing or broken `[P-…]` reference (`P2`/`P3`/`P5`);
   - a **structural** item = everything else: a coverage gap, a missing task or plan section, a missing acceptance criterion, a convention conflict, a KX3 truncation, an executability `<status:must_fix>`.

   **If the list contains EXCLUSIVELY local items:** start the affected fixers **in a single message, in parallel** — one per document, each with the list filtered for it. The downstream re-derivation of point 5 is **left out** in this case (every fixer gives `downstream-effect: none`). If a fixer does report `yes` after all, handle it as a normal iteration, and write into the Loop log which item you classified wrongly.
   **If the list contains even one structural item:** the usual sequential path follows from point 2 (the earliest target phase → downstream). The **local items of the affected document ride along** on the same fixer call in that case — they do not deserve a round of their own.

   > **NEVER start two fixers in parallel on the same document** — they would write the same file. The parallelism is between documents, not between items.
   >
   > **Why it wins.** The common case is many small findings. Sequentially that is `02 → 03 → 04`: three fixer rounds, plus the downstream re-derivation between them. This way it is a single parallel batch, whose elapsed time is that of the slowest fixer.
2. **Putting on the status marker.** From the target phase downwards, switch the status of every affected document to the phase-appropriate not-done state with an `[analyze-loop]` marker (e.g. `<status:draft> [analyze-loop]`). The marker signals: the fix mode is active → the fixers step the status automatically (see D7), and after an interruption it shows that the document was reopened by the loop.
3. **Starting the fixer subagent** with the wrapper belonging to the target phase (see "Starting the fixer subagent").
4. **Handling a stop for a question.** If the fixer reported open questions in its summary (new `Qnn` entries in `*-questions.md`): put them to the user **one by one**, with a phase header (see "The question format with a phase header"), carry the answer over into `*-questions.md` (`[x]` + the decision), then **restart the same fixer** with the question now answered. This does not count as a new analyze iteration.
4.a **The "did anything change at all?" sentinel — N.** After the fixer returns, run: `git diff --stat -- specs/cycle-NN-<cycle-name>/`.
   - **If the diff is empty**, and the fixer did **not** add a new `Qnn` question either, then the documents are unchanged — the next analyzer round would **certainly** give the same `<status:must_fix>` list. In that case **do not start an analyzer run**: stop, and ask the user how to continue (a manual fix / dropping the `<status:must_fix>` item / a review of `conventions.md`) — with the question format with a phase header. Note it in the Loop log: `the fixer made no change`.
   - **If the diff is not empty** (or there is a new question) → on to point 4.b.


4.b **Mechanical feedback after the fixer — G (after the fixer self-check, GS1).** The fixer runs the gate itself BEFORE returning, and reports the result in its `gate:` field. This point is therefore a **safety net, not the base step:** if the `gate:` field says `clean`, run the gate once (step 0, with `--emit-slices`, since the slices have to be refreshed anyway), and if there really is no mechanical `<status:must_fix>`, **go on to point 5 without a single fixer round**. The send-back branch below only applies if the fixer self-check did not converge (`gate: remained — …`), or the gate does find something after all.
   - **There is only a mechanical `<status:must_fix>`** (P/T/S/A/C/D codes, that is, exclusively the output of the gate) → **send the items of the gate back to the same fixer**, verbatim. This is **not a new iteration**, and it **does not start an analyzer run**: the loop counter does not grow.
   - **There is no mechanical `<status:must_fix>`** → on to point 5.
   - **Limit:** run this same feedback **at most twice** within one iteration. If the fixer gives back a mechanically faulty document for the third time as well, handle it as a normal iteration (on from point 5), and note in the Loop log: `the mechanical regression of the fixer did not converge`.


5. **Downstream re-derivation — CONDITIONALLY (D11).** After fixing upwards, the phases below the target phase have to be aligned (`02 → 03 → 04`) — **but only if the fix has a downstream effect.**
   - The return summary of the fixer necessarily contains a **`downstream-effect:`** field (see "Starting the fixer subagent"): `none`, or `yes — <what changed that affects the next phase>`.
   - **`none`** (typically: a refinement of the wording, merging a duplicate, fixing the artifact voice, a typo) → **do NOT start the downstream fixers.** A needless plan- or tasks-fixer run means reading the whole document, and it may introduce a new error as well.
   - **`yes`** → start the downstream fixer, and **hand over the text of the `downstream-effect`** to it — this is the scope of the reconciliation. This is a **targeted reconciliation, not a full rewrite**: it preserves the closed decisions of `*-questions.md`.
   - If the fixer did not give the field, **ask it back** in one sentence — do not guess, and do not run the whole chain "just to be safe".
   - **The mechanical feedback of 4.b runs after every downstream fixer as well** — the referencing order of `tasks.md` is typically broken exactly by the reconciliation.
6. **Re-analyze — ONE full round, with FOUR PARALLEL diagnosis rounds (D10/E/SH1).** First run the **mechanical gate** with `--emit-slices` (step 0) — the slices have to reflect the state after the fixing —, then start the **four rounds in a single message, in parallel** (see "The four diagnosis rounds"). Each of them runs **once**, in full mode within its own scope, and gets two extra inputs:
   - **the `<status:must_fix>` list of the previous round** — the **first block** of the analyzer's report verifies item by item whether it got resolved;
   - **the change of the design documents**: `git diff -- specs/cycle-NN-<cycle-name>/` (there is no commit during the loop, so the diff shows the complete change of the loop) — this is **navigation**: it should look at the changed sections first, because a new gap is most likely there. The scope of the examination, however, stays the **whole document**.

   Based on the result:
   - **There is no `<status:must_fix>`, and there is no open item on `analyze-task.md` either** → the loop converged, jump to "Status handling → PASS" (this is where the marker comes off and the single commit happens).
   - **There is a `<status:must_fix>`** → first the **triage (0.a)** for the **new** items (you do not ask again about the already decided ones), then a new iteration from point 1, the loop counter +1. If after the triage no open item is left on `analyze-task.md` (the user dismissed everything new), the loop **counts as converged** → PASS.

   > **A `PASS` can only be given from a full round** — that is, all four diagnosis rounds ran and gave an interpretable finding list; the `git diff` gives the focus, not the scope.

6.a **The survival rule (per-item escalation) — TS.** Before you start a new iteration, look at the **first block** of the reports of the diagnosis rounds (`Previous round's Must Fix items`), and collect those `AF-NN` / `AC-NN` / `AN-NN` / `AX-NN` items that came back marked `NOT resolved`.
   - **Keep the survival counter in the Loop log:** write out the identifiers of the surviving items for each iteration. The survival count of an item is which **consecutive** iteration it came back in as `NOT resolved`.
   - **If an item survives the SECOND consecutive iteration as well, do not hand it to the fixer a third time.** After two unsuccessful fixing attempts the most likely explanation is not that the fixer is clumsy, but that the item **requires a genuine decision** (a technology base, a configuration path, a test scope) that the fixer by definition must not make — see the "genuine decision" rule of the fix mode. In that case:
     1. **turn it into a question:** add it as a `Qnn` into the `*-questions.md` file of the target phase, if the fixer has not done so already;
     2. **ask the user** with the phase-header format, **one by one**;
     3. carry the answer over (`[x]` + the decision), then **restart the fixer** with the question now answered.

     This corresponds to the question stop of point 4: it is **not a new iteration, and does not consume `X`.**
   - **Note in the Loop log:** `TS — <identifier> survived the 2nd round as well → turned into a question`.

   > **Why it is needed.** `max X` is a **loop-level** limit: it does not notice when the fixer brings in a big package while leaving the same few items untouched round after round. In that case the loop burns all three iterations, and the user gets a `3/3 (given up)` report at the end — instead of having received the few concrete questions in the second round, after which the loop could have converged. In 07 the same role is filled by the per-item stop counter (VD4) and the escalation heuristic (VD5).

### The four diagnosis rounds (E/SH1) — parallel start and merging

The diagnosis is done by **four parallel rounds**, with scopes independent of each other. **Start them in a single message so that they can run in parallel** — this way the elapsed time of the phase is that of the slowest round, not the sum of the four. The first three call the **same `analyzer` definition** with a different scope; you give the name of the scope and the path of the slice in the launching message.

| Round (scope) | Definition | Categories | Its input | Prefix |
|---|---|---|---|---|
| `s1-dup-underspec` | `agents/analyzer.md` | **1. duplication + 3. under-specification** (the KX3 truncation too) | `analyze/slices/s1-dup-underspec.md` | `AF-NN` |
| `s2-coverage` | `agents/analyzer.md` | **2. ambiguity + 5. the content judgement of coverage** | `analyze/slices/s2-coverage.md` + the **generated matrix** of the gate + the handover files + `cycle-design-input.md` | `AC-NN` |
| `s3-conventions` | `agents/analyzer.md` | **4. convention conflict** | `analyze/slices/s3-conventions.md` | `AN-NN` |
| `analyzer-exec` | `agents/analyzer-exec.md` | **Category 6** (a test promised in prose, artifact ownership, a destructive operation, an anchor symbol, artifact voice) | `plan.md` + `tasks.md` + the **`## <sec:inventory>`** block of the gate | `AX-NN` |

_The input of all four rounds is extended with the **rebase file list**, if BR1 brought in the main branch (see below)._

> **If the slices were not produced** (the gate ran without `--emit-slices`, or the slice file is empty), that is not a stop: the semantic rounds work from the design documents, as they did before the slicing. This does **not** change the number of the rounds or their scopes.

**The rebase file list (BR1/a) — only if BR1 brought in something.** In that case the **source tree** changed, not the design documents: the analyzer sees nothing of this from its own `git diff` navigation (D10). Therefore hand the file list over to **all four** rounds, with this call:

> *"The following files arrived into the branch of the cycle with the bringing in of the main branch (rebase/merge), as the result of another cycle or a hotfix: `<file list>`. Look specifically at whether the references, anchors, signature and interface assumptions of `plan.md` and `tasks.md` pointing at them **still hold** (a renamed or moved symbol, a changed parameter list, a disappeared export, a modified config key). The scope of the examination does NOT narrow because of this — this is focus, not scope."*

The file list is **focus, not a narrowing** (the same principle as with the document diff, D10): a `PASS` can still only be given from a full analyzer run. A drift resulting from the changes brought in continues along the usual path — `<status:must_fix>` → the earliest target phase → a fixer —, there is **no separate "rebase fixing round"**: the self-healing loop is itself the fixing round.

**The merging is your business:**
1. You join the four `<status:must_fix>` lists and the `<status:must_fix>` list of the gate **into one list**, and then determine the **earliest affected target phase** from this merged list.
2. **Duplicate filtering:** if several rounds gave a finding for the same `file:location`, keep the **more specific** one (typically the executability item of the `analyzer-exec`), and do not carry the others over to the fixer. **Do not rewrite the identifier** — the item you keep goes on with its own prefix.
2.a **Triage filtering (TR1):** a finding with the same `file:location` + category pair as an item in the **Dismissed items** section of `analyze-task.md` gets **neither** onto the merged `<status:must_fix>` list **nor** into the triage question — that is the rediscovery of the dismissed item, not a new error. Do not reopen it in the report either; write into the Loop log: `TR1 — <identifier> showed up again, stays dismissed`.
3. The `Executability inventory` section of the report comes from the output of the `analyzer-exec`, the `Coverage matrix` from the **gate** (see below), the `Affected DoD rows` from the `s2-coverage` and the `analyzer-exec` round.
4. **If one of the rounds runs into an error or does not give an interpretable list**, do not qualify the round as a PASS: restart that one (this is not a new iteration). The categories of the missing round **do not drop out** — a PASS cannot be given with a category left without a diagnosis.

### Starting the fixer subagent

- The **system prompt** of the fixer subagent is the fixer wrapper of the target phase: `agents/spec-fixer.md` (02), `agents/plan-fixer.md` (03), `agents/tasks-fixer.md` (04). The wrapper **contains** the Fix mode section of the phase and the quality gate of the phase (from a shared source, inlined at build time) — there is no duplicated fixing logic, and the own gates of the phase take effect automatically.
- **The fixer does not read a phase skill (D13).** Every rule is in the wrapper; if a fixer does announce reading the skill, that is an error (it tempts to re-run the whole phase instead of a targeted fix).
- **The input** to the subagent: the **open** item list of `analyze-task.md` filtered for the target phase **together with the `AF-NN` / `AC-NN` / `AN-NN` / `AX-NN` identifiers** (identifier + category + description + `file:location` + the `why it blocks` and the `how it would be correct` fields) + the documents of the target phase. The `how it would be correct` is the **target state** of the fix — if it carries a question, the user answers first, and the answer is what goes to the fixer. **Do not drop and do not rewrite** the identifiers — the survival rule (TS) builds on a literal identifier match.
- **The output** from the subagent: (a) a summary of the (mechanical) fixes made, (b) the **`downstream-effect:`** field (`none` / `yes — <what affects the next phase>`, D11), (c) the identifiers of the **<status:op_new>** questions added to `*-questions.md` — of those points that need a real decision —, and (d) the **`gate:`** field (GS1): the result of its own closing gate run. The subagent **does not ask the user directly** (it has no interactive channel); it only collects and returns. Asking is your business (D2).
- **A completeness check on return.** Compare the list you handed over with the fixer's summary: **every** identifier handed over must appear either as fixed, or as a `Qnn` question, or with an explicit "I could not handle it" justification. **If an identifier is silently missing**, do not start an analyzer run for it: ask the fixer back in one sentence what happened to it. Otherwise a silently omitted item looks as if the fixer had tried and failed — and the TS counter would give a false picture.

### The `max X` loop counter + stopping

- **Default: `max X = 3`.**
- **The unit of `X`: the number of full analyze re-runs.** One `FAIL → fix → re-deriv → re-analyze` cycle = **1** iteration, and **one** analyzer run. The fixer restarts caused by follow-up questions and the individual downstream fixer calls do **not** increase `X`.
- **Two exit conditions independent of each other:**
  1. **An open question** → the loop stops and asks; the user answers; the loop **continues** (this is not an error, and it does not consume an iteration).
  2. **`max X` reached without convergence** → the loop gives up (see "Status handling → FAIL").

### The `[analyze-loop]` status marker (D7)

- **Format:** an `[analyze-loop]` suffix at the end of the status value, e.g. `<status:draft> [analyze-loop]`, `<status:open_questions> [analyze-loop]`.
- **Its meaning:** the document was reopened by the analyze loop, the fix mode is active. While the marker is present, the fixers step the status **automatically** (without a confirmation) — in contrast to the normal "confirmation before the status change" rule of 02/03/04. The user only steps in at the **questions** and at the **final PASS**.
- **Taking it off:** at a PASS (→ the normal flow, the fixer gives the real closing status of the phase) or when giving up at `max X`, according to the end state (see FAIL). The presence of the marker is at the same time the anchor for continuing after an interruption.

### Commit strategy in the loop (D9)

- **In an `analyze-loop` there is no commit per iteration** — the history stays free of noise.
- **A single commit when the loop is closed** (a PASS or giving up at `max X`): `cycle-NN: 05-analyze`. This commit is **mandatory on both branches** — for the procedure (stage → commit → deterministic verification → feedback) see the *Phase-closing commit* section (PC1).
- **Interruption-safe:** the absence of an intermediate commit is compensated by the `[analyze-loop]` status marker + the `*-questions.md` + the <sec:loop_log> — the continuation can be reconstructed from these (see "Continuing after an interrupted run").

---

## The question format with a phase header

When you put a question to the user during the loop, always show **where the loop stands**. The template of the question:

```
[<PHASE> · iter <n>/<max X> · <PHASE>/<Qnn>]
<the text of the question>
```

- **Phase:** `SPEC` / `PLAN` / `TASKS` (the target phase the question comes from).
- **`iter n/max X`:** which analyze iteration the loop is at.
- **`PHASE/Qnn`:** the identifier of the question with a phase prefix in the dialogue (`SPEC/Q07`, `PLAN/Q03`, `TASKS/Q02`). **In the files** the question stays a plain `Qnn` — the location of the file (`spec-questions.md` / `plan-questions.md` / `tasks-questions.md`) encodes the phase.

Rules: **one question at a time**, wait for the answer, and place a direct, clickable link to the affected `*-questions.md` at the end of your answer.

Example:

> **[PLAN · iter 2/3 · PLAN/Q05]**
> Should `callLegacyVerify` retry in case of a timeout, or return a 504 immediately? The spec does not state it.
> [plan-questions.md](file:///.../specs/cycle-NN-name/plan-questions.md)

---

## analyze-report.md structure

Create / update the `specs/cycle-NN-<cycle-name>/analyze/analyze-report.md` file (a relative path format in the content of the document, `file://` is forbidden). **The moment of creation is the point after the first diagnosis, not the end of the phase** — see the *Live report (AR1)* section:

```md
<!-- INCLUDE:lang/05-analyze.md#analyze-report-struktura -->
```

---

## analyze-task.md structure

Create / refresh the `specs/cycle-NN-<cycle-name>/analyze/analyze-task.md` file (AD1). **It is created after the first triage**, and it is refreshed at every step of the loop. This is the work list of the fixers; the "why" is in the report, what goes here is the **to-do**:

```md
<!-- INCLUDE:lang/05-analyze.md#analyze-task-struktura -->
```

---

## Quality check — before closing the report

Go through whether all **6** categories really ran — that is, **whether all four diagnosis rounds arrived** (`s1-dup-underspec` → categories 1+3, `s2-coverage` → 2+5, `s3-conventions` → 4, `analyzer-exec` → 6). **For category 6, check separately whether the subagent returned the "Executability inventory"** — without it the PASS cannot be accepted, because exactly those errors would stay hidden that the coverage matrix does not see structurally:

1. **Duplication** — is spec/plan/tasks reviewed for redundancy?
2. **Ambiguity** — is every acceptance criterion measurable/decidable?
3. **Under-specification** — is every component and condition defined?
4. **Convention conflict** — does every design decision match `conventions.md`?
5. **Coverage** — did the generated matrix of the gate get into the report, and is the content judgement of the `s2-coverage` round (`Affected DoD rows` + requirements beyond `DoD-NN`) carried over onto it?
6. **Executability and artifact ownership** — did the `analyzer-exec` return the *Executability inventory* (see above), did the **mechanical gate** (`analyze-gate-check.py`) run in this round with `--emit-slices`, and did you hand the blocks of the gate over to the rounds (AG3/AG4/SH1)?

If any of the categories did not run, do not close the report. If the loop ran, check as well that the **<sec:loop_log>** contains every iteration.

**Is the `Items to fix` list closed? (AR1)** — the report cannot be closed with an item left in a `[ ]` state with an `open` or `being fixed` field. Every item runs into one of three end states: `[x]` + `resolved (iter <n>)`, or `[x]` + `dismissed — <justification>`, or — on the `FAIL` branch — `[ ]` + `question (<PHASE>/Q<nn>)` or `open`, **explicitly as the documentation of the giving up**, referenced from the Loop log. An item left open next to a `PASS` is in itself a reason to reject the report. An item dismissed in the triage (TR1) runs into the same place: `[x]` + `dismissed (triage, iter <n>) — the user did not ask for it to be fixed`.

**Is `analyze-task.md` closed?** — next to a `PASS` no open (`[ ]`) item may be left on it, and every item of it must be present in the report as well, with the same identifier and a reconcilable end state. If the report and the list contradict each other, the report cannot be closed.

**Is the `Triage (TR1)` header field filled in?** — if the first diagnosis produced a `<status:must_fix>` item, the field states what the user chose (`all` / identifiers / `none`) and how many items were left dismissed. **An item dismissed without a triage decision cannot be in the report** — that would be an arbitrary narrowing by the orchestrator.

**Is the `<field:f_validated_base>` field filled in? (BR1)** — the name and SHA of the main branch (`git rev-parse origin/main`), the tip of the branch of the cycle (`git rev-parse HEAD`), and whether BR1 brought in anything appear in the header of the report. `06` and `09` **compare this with the state at their own run**: if the main branch has moved ahead in the meantime, the `PASS` of `analyze-report.md` was produced on an outdated base. With a placeholder or a missing field, the report cannot be closed. (In a No-VCS project the value of the field is `—`.)

---

## Status handling

### PASS (the loop converged, or it was clean on the first attempt)

There is no `<status:must_fix>` finding — or what was left, the user dismissed in the triage (TR1).

What to do, **in order**:
1. The report already exists (AR1) — **do not rewrite it from scratch**: set its status from `IN_PROGRESS` to `PASS`, the `Current step:` field to `closed`, fill in the `Loop:` field and the Loop log (if there was an iteration), and tick off the remaining items of the `Items to fix` list with their end state. Fill in the `Triage (TR1)` field as well (if there was a triage). **Close `analyze-task.md` too:** no open item may be left on it.
2. **Take the `[analyze-loop]` marker off** every affected document — the fixers gave the real closing status of the phase (`<status:ready_for_plan>` / `<status:ready_for_tasks>` / `<status:ready_for_implement>`); check that this is what stands on each of them.
3. **A single closing commit** (there was no intermediate commit during the loop) — according to the procedure of the *Phase-closing commit* section, **mandatory**:
   ```bash
   git add specs/cycle-NN-<cycle-name>/
   git commit -m "cycle-NN: 05-analyze"
   ```
4. **If the triage dismissed items:** state in one sentence how many, and that they can be looked up in the report with a `dismissed (triage)` state — the `PASS` was produced alongside deliberately accepted contradictions.
5. Tell the user the next step and the starting command of the phase:
<!-- INCLUDE:lang/05-analyze.md#zaro-uzenet -->
   > **At the end of the answer, place the direct, clickable link of `analyze-report.md`.**

### FAIL (`max X` reached without a PASS)

The loop did not converge even after `max X = 3` iterations.

What to do, **in order**:
1. The report already exists (AR1) — **do not rewrite it from scratch**: set its status from `IN_PROGRESS` to `FAIL`, the `Current step:` field to `closed`, `<max X>/<max X> (given up)` into the `Loop:` field, and the stuck state into the Loop log (which `<status:must_fix>` remained, at which phase). On the `Items to fix` list the stuck items stay in `[ ]` — that is the documentation of the giving up. **The same items stay open on `analyze-task.md`**: that is the work list of the continuation.
2. **Leave the `[analyze-loop]` marker on** the affected documents — this way the user (or a next session) sees that the loop reopened them, and where it got stuck.
3. **A single closing commit** — according to the procedure of the *Phase-closing commit* section, **mandatory** (the FAIL branch is no exception either):
   ```bash
   git add specs/cycle-NN-<cycle-name>/
   git commit -m "cycle-NN: 05-analyze"
   ```
4. A summary + a question to the user: summarize which `<status:must_fix>` did not get resolved and why (e.g. a recurring ambiguity that the fixer cannot decide), and ask how they should continue (a manual fix in the given phase / a decision on an open question / a review of `conventions.md` in case of a severe convention conflict).
   > **At the end of the answer, place the direct, clickable link of `analyze-report.md`.**

<!-- INCLUDE:shared/phase-commit.md -->

In the block above, the value of `<PHASE-TAG>` in this phase is: **`05-analyze`**. The commit happens **once, when the loop is closed** — but **on every closing branch** (PASS and `max X` FAIL alike). There is no intermediate commit during the loop; the intermediate state is kept by the `[analyze-loop]` marker, the `*-questions.md` files and the Loop log.

> **Stopping rule (PC1):** if the status of `analyze-report.md` is `PASS` or `FAIL`, but the phase-closing commit is missing (a VCS project, `git log -1 --oneline` does not show the `cycle-NN: 05-analyze` commit), **STOP** — commit first, and only close the phase and give the next step afterwards.

---

## Rules for asking

- Put only **one** question at a time, wait for the answer. **The single exception is the triage stop (TR1):** there you ask for the decision on all items in one message, as a numbered list — the list itself is the question.
- For the questions during the loop, use the **question format with a phase header** (`[PHASE · iter n/max X · PHASE/Qnn]`).
