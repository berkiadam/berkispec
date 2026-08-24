---
phase: 05
name: bs-analyze
description: "berkispec - 05. Use it before the implementation (Phase 05), when tasks.md is 'Ready for implementation'. A cross-phase consistency gate between spec.md/plan.md/tasks.md: with subagents (analyzer, *-fixer) it identifies and automatically fixes the contradictions. It creates 'analyze-report.md' (PASS/FAIL)."
prerequisites:
  - "specs/cycle-NN-<name>/tasks.md status: <status:ready_for_implement>"
output:
  - "specs/cycle-NN-<name>/analyze-report.md (PASS / FAIL)"
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
| The mechanical gate | Before every run `analyze-gate-check.py` (plan ID ↔ task reference, marker, `⟂`, `DoD-NN`, mandatory tables, **artifacts being run, plan anchors, artifact voice**) — its `<status:must_fix>` hits go into the loop with the target phase given by the script, and its `## <sec:inventory>` block is the input of the `analyzer` (AG3). |
| The analyzer subagents | The read-only cross-check is done by **two parallel** subagents: `agents/analyzer.md` (categories 1–5) and the `analyzer-exec` subagent (category 6, executability) — you merge the two finding lists (E). |
| The fixer subagents | The fixing is done by the `agents/{spec,plan,tasks}-fixer.md` wrappers (= the Fix mode of phase 02/03/04); they write the design documents. |
| Result | `analyze-report.md` PASS or FAIL, with a severity classification + <sec:loop_log>. |
| One analyzer run / iteration | The run of the analyzer is **always full**; from the 2nd run it gets the previous `<status:must_fix>` list (verification) and the `git diff` (navigation) — but it does not narrow itself down to them (D10). The downstream re-derivation is **conditional** (D11). |
| FAIL | **A self-healing loop starts:** the earliest affected target phase → a fixer subagent → downstream re-derivation (`02→03→04`) → a re-analyze, until PASS — with `max X = 3` iterations. |
| Stopping for a question | If the fixer reported an open question: the orchestrator (you) asks the user with a `PHASE/Qnn` header, writes in the answer, and restarts the fixer — the loop **continues** (this is not an error). |
| PASS | On to the 06-implement phase. Commit: a single `cycle-NN: 05-analyze` at the end of the loop. |
| Phase-closing commit | **Mandatory, on every closing branch** (PASS and FAIL alike) — according to the procedure of the *Phase-closing commit* section (PC1). Without a commit the phase is not closed. |

---

## Your role: orchestrator (a read-only invariant)

`05-analyze` is a **conducting** phase. Keep two things in mind throughout:

1. **You do not edit a design document yourself** (`spec.md`, `plan.md`, `tasks.md`). Every content fix is done by the fixer subagents (= the Fix mode of phases 02/03/04). The only file you write is `analyze-report.md`, and your only direct modification on the design documents is **switching the status field** (putting the `[analyze-loop]` marker on and taking it off, see below).
2. **The read-only diagnosis belongs to the `analyzer` subagent.** You read its finding list and decide about PASS / FAIL, then in case of a FAIL you conduct the fixing loop.

This way the responsibility of the phase is clean: **diagnosis (analyzer) → conducting (you) → fixing (the fixers)**, each in its own place.

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
   git log --oneline $(git merge-base HEAD origin/main)..origin/main
   ```

   _In a repo without a remote (local only) work with the local `main` instead of `origin/main`, without `git fetch`. In place of `main` goes the **<field:f_main_branch>** field of the `## <sec:cv_git_conventions>` of `conventions.md`._

   - **An empty list** → there is nothing to do, continue. (In the parallel planning window this is the normal case: while the other cycle is not merged, the main branch does not move.)
   - **Not empty** → bring the main branch into the branch of the cycle **BEFORE the analyze**:
     - the branch is **not pushed / there is no PR for it** (`git rev-parse --verify origin/feature/cycle-NN-<cycle-name>` gives an error) → `git rebase origin/main`,
     - the branch **is pushed or a PR is open** → `git merge origin/main` (a rebase would require a force push).

     **Before** bringing it in, note the tip of the branch of the cycle (`PRE=$(git rev-parse HEAD)`). Report in one line what you brought in (`git log --oneline` about the commits brought in) — **do not ask for separate permission**, you are working on the own branch of the cycle, this is not destructive. **In case of a conflict, STOP**: list the conflicting files, and ask for a decision; do **not** resolve the generated documents (`docs-generated/`) and `specs/test-conventions.md` by hand — that is the business of `08`.

   - **After bringing it in, produce the REBASE FILE LIST (BR1/a):**
     ```bash
     git diff --name-only "$PRE" HEAD -- . ':(exclude)specs/*'
     ```
     This is the list of the **source, test and config files** that arrived from another cycle/hotfix. If it is not empty, it has to get into the input of **both analyzer subagents** (see *"The two analyzer subagents"* → **The rebase file list**). If it is empty (only the `specs/` folders of other cycles came in), there is nothing to do.
     _Hand over a file list, **not the whole diff** — the subagent reads the necessary details itself (AG3)._

   > **Do not rebase unconditionally.** If the list above is empty, you do **not touch** the history of the branch — the analyze may run several times in the self-healing loop, and a needless rewriting of the history would provoke a force push on a pushed branch.

   **Why here:** this phase is the gate of **base consistency**. This is why the parallel-cycle gate of `06` (PW2) does not prescribe a separate rebase step, but requires that there be a **fresh `05` `PASS`** before `06` — the bringing in is done by `05` itself.

---

## Continuing after an interrupted run

**The first analyze run of the continuation starts WITHOUT a verification list** — you cannot know where the fixing was interrupted, so there is no meaningful "previous round". The run — as always — is full, and the mechanical gate (step 0) runs as well.

The **diagnosis** of the analyze is read-only, but the loop may already have modified the design documents. The continuation is made reconstructable together by the `[analyze-loop]` status marker, the open questions of `*-questions.md` and the Loop log of `analyze-report.md`. The decision tree — **in this order**:

```
1. Does one of the design documents (spec.md / plan.md / tasks.md) bear an
   `[analyze-loop]` status marker?
   → Yes → the loop was interrupted. Do NOT start a new analysis from scratch.
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
   → If the report looks interrupted (not every category is filled in) and
     there is no marker: delete the partial report, and start the analysis again.

3. There is no analyze-report.md and no marker.
   → Start the analysis according to "What you have to do".
```

---

## What you have to do

Check that the design documents of the cycle (`spec.md`, `plan.md`, `tasks.md`) are **consistent with each other and with `conventions.md`** before the implementation starts — and if they are not, **conduct their correction** in a self-healing loop, until they become consistent.

**Do not implement anything.** This is the sanity check (and, if needed, a fixing loop) before the implementation.

The diagnosis looks for problems in **5 categories** (done by the `analyzer` subagent):

1. **Duplications** — the same decision several times within the plan; `tasks.md` describing the test case steps of the plan again; a redundant task. **Taking over the elaborated artifact of the spec into the plan verbatim is NOT a duplication** (KX3) — that is the mandatory self-containedness.
2. **Ambiguity** — vague concepts, missing metrics, an acceptance criterion that cannot be measured.
3. **Under-specification** — a missing acceptance criterion, an undefined component, a plan section that cannot be assigned to a task.
4. **Convention conflicts** — a deviation from `conventions.md` (tech stack, naming, test tool, merge strategy, structure).
5. **Coverage gaps** — the requirement ↔ task assignment: is there a spec requirement with no task belonging to it, or a task that cannot be traced back to the plan.

---

## Context loading rules

- The cross-check requires reading many files together — **starting the two diagnosis subagents is mandatory, in a single message, in parallel** (E): the `analyzer` subagent (categories 1–5, on the `spec.md` + `plan.md` + `tasks.md` + `conventions.md` quartet) and the `analyzer-exec` subagent (category 6, on the `plan.md` + `tasks.md` + the inventory of the gate triple). Both return **exclusively the structured finding list** (the raw file content does not burden the main context).
- Their system prompt is given by the **installed agent definition** of the platform (`analyzer`, `analyzer-exec`) — call them by these names, do not look for them as files in the project.
- **Hand over the corresponding block of the gate output to both subagents, verbatim:**
  - `analyzer-exec` → the **`## <sec:inventory>`** (`<status:mk_artifact>` / `<status:mk_anchor>` / `<status:mk_tone_suspect>` / `<status:mk_test_promise>` / `<status:mk_destructive>`, AG3): this replaces the repo and document exploration, which was the main cost of category 6;
  - `analyzer` → the **`## <sec:coverage_matrix>`** (AG4): the `DoD-NN → [P-…] → task` chain ready-made, so that it does not derive it again.
- You merge the output of the two subagents (see "The two analyzer subagents"), and decide about PASS / FAIL based on that.
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

---

## Step 0 — the mechanical gate (`analyze-gate-check.py`) — BEFORE EVERY analyze run

The checks that can be decided mechanically are **not done by the `analyzer` subagent**, but by a script — deterministically, cheaply, without false alarms:

<!-- INCLUDE:shared/python-cmd.md -->

```bash
python3 <platform-scripts-mappa>/analyze-gate-check.py specs/cycle-NN-<cycle-name>
```

_(Run from the root of the project, the `--repo-root .` and the `--conventions conventions.md` defaults are fine. If `conventions.md` is elsewhere, give it: `--conventions <path>` — without it the `G1` gate-configuration check is skipped.)_

**What it covers:** plan ID format/uniqueness (P1), the existence of the task→plan reference (P2), a reference to a non-existent ID (P3), an ID without a task (P4), a reference by ordinal (P5), a marker on every task (T1), `[OPS]` on a repo file (T2), a status-updating task (T3), `⟂` symmetry (T4), a missing/duplicated `DoD-NN` (D1), a `DoD-NNb` shaped after-the-fact identifier (D2), the existence of the mandatory tables (S1/S2) — **and the mechanical layer of category 6 (AG3):** the existence of the artifact being run / the creating task (A1 = 6.a), the resolution of a plan `path:line` anchor (A2 = 6.g at file level), the validity of the anchor line number (A2b, a suggestion), the hard floor of artifact voice (A3 = 6.h `🔴`/"Forbidden", a suggestion) — **and further:** the taking over of the elaborated artifacts of the spec (`V1`) and the extent of the test sections (`V2`, KX3), the path format (`R1`, RP1) and the anchor format (`A2c`, a suggestion), and the **gate configuration moving along** (`G1`, GC1: the cycle touches the report structure, but the `## <sec:cv_test_reporting>` table of `conventions.md` does not move → the TR3 gate of 07 would look in the old place).

**The three blocks of the output:**
- **`## <status:must_fix>`** — line by line `[code] (target phase: NN) message`. Each of them is a `<status:must_fix>`, with the target phase given by the script — add them to the list of `analyze-report.md` **verbatim**. Do not question them and do not re-evaluate them: they are the results of a mechanical check.
- **`## Javaslatok`** — they do not block, they do not start a loop; they go into the `Suggestions` section of the report.
- **`## <sec:inventory>`** — **not a finding, but the INPUT of the `analyzer`.** It contains the text of the anchored lines, the state of the artifacts being run and the voice hits requiring a judgement. **Hand it over to the `analyzer` subagent verbatim** — this way it does not have to run `Grep`/`Glob` rounds in the repo (this was the main cost of category 6).

**Exit code:**
- **`0`** → there is no blocking mechanical finding (there may be suggestions and an inventory in the output); start the `analyzer` subagent for the semantic categories, together with the inventory.
- **`1`** → there is a `<status:must_fix>`; start the analyzer the same way, and handle the two finding lists together in the loop.
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
| Scope overreach (SC1): a plan capability has no spec source | **02** (if the capability is needed → a DoD item), **03** (if it is not needed → removing it + `<sec:out_of_scope>`) | without an acceptance criterion it cannot be developed |
| <sec:config_lifecycle> (KF1) is incomplete or missing | **03** | the propagation of the parameter is a design question |
| A spec test case did not map to a plan test case (TP1) / a missing environment preparation (TP3) | **03** | the `test-runner` reads only the plan |
| A missing mandatory table (`<sec:spec_coverage>`, `<sec:reverse_coverage>` → 03; `<sec:plan_coverage>` → 04) | the owner of the table | a table left out = a gate skipped |
| A missing/duplicated `DoD-NN` identifier | **02** | the per-item counter of 07 builds on it |
| An elaborated spec artifact truncated / merged in the plan (KX3 — `V1`/`V2` or semantic) | **03** | the `test-runner` does not read the spec: whatever is left out here will not run |
| Path format (RP1 — `R1`) | the owner of the document: **02 / 03 / 04** | an absolute/machine-specific path is meaningless on another machine and in CI |
| The gate configuration does not move with the structure (GC1 — `G1`) | **03** (+ **04** for the task) | the gate reading `conventions.md` (TR3, Sonar) would run with the old value → 07 fails |

**The earliest affected phase wins:** if several categories are FAIL and they point at different target phases, the loop jumps to the **earliest affected phase** (02 < 03 < 04), and re-derives the downstream phases from there — otherwise the later phases would build on a faulty base. (A severe convention conflict points at `00`: this requires a human decision at the level of `conventions.md` — in that case the loop stops and asks, it does not fix automatically.)

---

## The self-healing loop (the orchestrator loop)

In case of a FAIL you do **not** simply hand control back to the user. Instead, you conduct an iterative fixing loop until there is a PASS, or until you reach the `max X` limit.

### One iteration of the loop

1. **Determining the target phase.** From the categories of the `<status:must_fix>` list (according to the mapping above), determine the **earliest affected target phase** (02/03/04). This is the entry point of the fixer.
2. **Putting on the status marker.** From the target phase downwards, switch the status of every affected document to the phase-appropriate not-done state with an `[analyze-loop]` marker (e.g. `<status:draft> [analyze-loop]`). The marker signals: the fix mode is active → the fixers step the status automatically (see D7), and after an interruption it shows that the document was reopened by the loop.
3. **Starting the fixer subagent** with the wrapper belonging to the target phase (see "Starting the fixer subagent").
4. **Handling a stop for a question.** If the fixer reported open questions in its summary (new `Qnn` entries in `*-questions.md`): put them to the user **one by one**, with a phase header (see "The question format with a phase header"), carry the answer over into `*-questions.md` (`[x]` + the decision), then **restart the same fixer** with the question now answered. This does not count as a new analyze iteration.
4.a **The "did anything change at all?" sentinel — N.** After the fixer returns, run: `git diff --stat -- specs/cycle-NN-<cycle-name>/`.
   - **If the diff is empty**, and the fixer did **not** add a new `Qnn` question either, then the documents are unchanged — the next analyzer round would **certainly** give the same `<status:must_fix>` list. In that case **do not start an analyzer run**: stop, and ask the user how to continue (a manual fix / dropping the `<status:must_fix>` item / a review of `conventions.md`) — with the question format with a phase header. Note it in the Loop log: `the fixer made no change`.
   - **If the diff is not empty** (or there is a new question) → on to point 4.b.


4.b **Mechanical feedback after the fixer — G.** As soon as the fixer has returned (and its questions are answered), **run the mechanical gate** (step 0) — still before the analyzer.
   - **There is only a mechanical `<status:must_fix>`** (P/T/S/A/C/D codes, that is, exclusively the output of the gate) → **send the items of the gate back to the same fixer**, verbatim. This is **not a new iteration**, and it **does not start an analyzer run**: the loop counter does not grow.
   - **There is no mechanical `<status:must_fix>`** → on to point 5.
   - **Limit:** run this same feedback **at most twice** within one iteration. If the fixer gives back a mechanically faulty document for the third time as well, handle it as a normal iteration (on from point 5), and note in the Loop log: `the mechanical regression of the fixer did not converge`.


5. **Downstream re-derivation — CONDITIONALLY (D11).** After fixing upwards, the phases below the target phase have to be aligned (`02 → 03 → 04`) — **but only if the fix has a downstream effect.**
   - The return summary of the fixer necessarily contains a **`downstream-effect:`** field (see "Starting the fixer subagent"): `none`, or `yes — <what changed that affects the next phase>`.
   - **`none`** (typically: a refinement of the wording, merging a duplicate, fixing the artifact voice, a typo) → **do NOT start the downstream fixers.** A needless plan- or tasks-fixer run means reading the whole document, and it may introduce a new error as well.
   - **`yes`** → start the downstream fixer, and **hand over the text of the `downstream-effect`** to it — this is the scope of the reconciliation. This is a **targeted reconciliation, not a full rewrite**: it preserves the closed decisions of `*-questions.md`.
   - If the fixer did not give the field, **ask it back** in one sentence — do not guess, and do not run the whole chain "just to be safe".
   - **The mechanical feedback of 4.b runs after every downstream fixer as well** — the referencing order of `tasks.md` is typically broken exactly by the reconciliation.
6. **Re-analyze — ONE full round, with TWO PARALLEL subagents (D10/E).** First run the **mechanical gate** (step 0), then start the `analyzer` and the `analyzer-exec` subagent **in a single message, in parallel** (see "The two analyzer subagents"). Both run **once**, in full mode, and get two extra inputs:
   - **the `<status:must_fix>` list of the previous round** — the **first block** of the analyzer's report verifies item by item whether it got resolved;
   - **the change of the design documents**: `git diff -- specs/cycle-NN-<cycle-name>/` (there is no commit during the loop, so the diff shows the complete change of the loop) — this is **navigation**: it should look at the changed sections first, because a new gap is most likely there. The scope of the examination, however, stays the **whole document**.

   Based on the result:
   - **There is no `<status:must_fix>`** → the loop converged, jump to "Status handling → PASS" (this is where the marker comes off and the single commit happens).
   - **There is a `<status:must_fix>`** → a new iteration from point 1, the loop counter +1.

   > **A `PASS` can only be given from a full analyzer run** — the `git diff` gives the focus, not the scope.

### The two analyzer subagents (E) — parallel start and merging

The diagnosis is done by **two subagents**, with scopes independent of each other. **Start them in a single message so that they can run in parallel** — this way the elapsed time of the phase is that of the slower one, not their sum.

| Subagent | Scope | Its input |
|---|---|---|
| `agents/analyzer.md` | **Categories 1–5** (duplication, ambiguity, under-specification, convention conflict, the **content** judgement of coverage) | `spec.md` + `plan.md` + `tasks.md` + `conventions.md` + the handover files + `cycle-design-input.md` + the **generated matrix** of the gate |
| `agents/analyzer-exec.md` | **Category 6** (a test promised in prose, artifact ownership, a destructive operation, an anchor symbol, artifact voice) | `plan.md` + `tasks.md` + the **`## <sec:inventory>`** block of the gate |

_The input of both subagents is extended with the **rebase file list**, if BR1 brought in the main branch (see below)._

**The rebase file list (BR1/a) — only if BR1 brought in something.** In that case the **source tree** changed, not the design documents: the analyzer sees nothing of this from its own `git diff` navigation (D10). Therefore hand the file list over to **both** subagents, with this call:

> *"The following files arrived into the branch of the cycle with the bringing in of the main branch (rebase/merge), as the result of another cycle or a hotfix: `<file list>`. Look specifically at whether the references, anchors, signature and interface assumptions of `plan.md` and `tasks.md` pointing at them **still hold** (a renamed or moved symbol, a changed parameter list, a disappeared export, a modified config key). The scope of the examination does NOT narrow because of this — this is focus, not scope."*

The file list is **focus, not a narrowing** (the same principle as with the document diff, D10): a `PASS` can still only be given from a full analyzer run. A drift resulting from the changes brought in continues along the usual path — `<status:must_fix>` → the earliest target phase → a fixer —, there is **no separate "rebase fixing round"**: the self-healing loop is itself the fixing round.

**The merging is your business:**
1. You join the two `<status:must_fix>` lists and the `<status:must_fix>` list of the gate **into one list**, and then determine the **earliest affected target phase** from this merged list.
2. **Duplicate filtering:** if both subagents gave a finding for the same `file:location`, keep the **more specific** one (typically the executability item of the `analyzer-exec`), and do not carry the other one over to the fixer.
3. The `Executability inventory` section of the report comes from the output of the `analyzer-exec`, the `Coverage matrix` from the **gate** (see below), the `Affected DoD rows` from both.
4. **If one of the subagents runs into an error or does not give an interpretable list**, do not qualify the round as a PASS: restart that one (this is not a new iteration).

### Starting the fixer subagent

- The **system prompt** of the fixer subagent is the fixer wrapper of the target phase: `agents/spec-fixer.md` (02), `agents/plan-fixer.md` (03), `agents/tasks-fixer.md` (04). The wrapper **contains** the Fix mode section of the phase and the quality gate of the phase (from a shared source, inlined at build time) — there is no duplicated fixing logic, and the own gates of the phase take effect automatically.
- **The fixer does not read a phase skill (D13).** Every rule is in the wrapper; if a fixer does announce reading the skill, that is an error (it tempts to re-run the whole phase instead of a targeted fix).
- **The input** to the subagent: the `<status:must_fix>` list filtered for the target phase (category + description + `file:location`) + the documents of the target phase.
- **The output** from the subagent: (a) a summary of the (mechanical) fixes made, (b) the **`downstream-effect:`** field (`none` / `yes — <what affects the next phase>`, D11), and (c) the identifiers of the **<status:op_new>** questions added to `*-questions.md` — of those points that need a real decision. The subagent **does not ask the user directly** (it has no interactive channel); it only collects and returns. Asking is your business (D2).

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

Create / update the `specs/cycle-NN-<cycle-name>/analyze-report.md` file (a relative path format in the content of the document, `file://` is forbidden):

```md
<!-- INCLUDE:lang/05-analyze.md#analyze-report-struktura -->
```

---

## Quality check — before closing the report

Go through whether all **6** categories really ran (1–5 in the output of the `analyzer`, 6 in that of the `analyzer-exec` — **whether both arrived at all**). **For category 6, check separately whether the subagent returned the "Executability inventory"** — without it the PASS cannot be accepted, because exactly those errors would stay hidden that the coverage matrix does not see structurally:

1. **Duplication** — is spec/plan/tasks reviewed for redundancy?
2. **Ambiguity** — is every acceptance criterion measurable/decidable?
3. **Under-specification** — is every component and condition defined?
4. **Convention conflict** — does every design decision match `conventions.md`?
5. **Coverage** — did the generated matrix of the gate get into the report, and is the content judgement of the `analyzer` (`Affected DoD rows` + requirements beyond `DoD-NN`) carried over onto it?
6. **Executability and artifact ownership** — did the `analyzer-exec` return the *Executability inventory* (see above), did the **mechanical gate** (`analyze-gate-check.py`) run in this round, and did you hand the blocks of the gate over to the two subagents (AG3/AG4)?

If any of the categories did not run, do not close the report. If the loop ran, check as well that the **<sec:loop_log>** contains every iteration.

**Is the `<field:f_validated_base>` field filled in? (BR1)** — the name and SHA of the main branch (`git rev-parse origin/main`), the tip of the branch of the cycle (`git rev-parse HEAD`), and whether BR1 brought in anything appear in the header of the report. `06` and `09` **compare this with the state at their own run**: if the main branch has moved ahead in the meantime, the `PASS` of `analyze-report.md` was produced on an outdated base. With a placeholder or a missing field, the report cannot be closed. (In a No-VCS project the value of the field is `—`.)

---

## Status handling

### PASS (the loop converged, or it was clean on the first attempt)

There is no `<status:must_fix>` finding.

What to do, **in order**:
1. Write the status of `analyze-report.md` to `PASS`, fill in the `Loop:` field and the Loop log (if there was an iteration).
2. **Take the `[analyze-loop]` marker off** every affected document — the fixers gave the real closing status of the phase (`<status:ready_for_plan>` / `<status:ready_for_tasks>` / `<status:ready_for_implement>`); check that this is what stands on each of them.
3. **A single closing commit** (there was no intermediate commit during the loop) — according to the procedure of the *Phase-closing commit* section, **mandatory**:
   ```bash
   git add specs/cycle-NN-<cycle-name>/
   git commit -m "cycle-NN: 05-analyze"
   ```
4. Tell the user the next step and the starting command of the phase:
<!-- INCLUDE:lang/05-analyze.md#zaro-uzenet -->
   > **At the end of the answer, place the direct, clickable link of `analyze-report.md`.**

### FAIL (`max X` reached without a PASS)

The loop did not converge even after `max X = 3` iterations.

What to do, **in order**:
1. Write the status of `analyze-report.md` to `FAIL`, `<max X>/<max X> (given up)` into the `Loop:` field, and the stuck state into the Loop log (which `<status:must_fix>` remained, at which phase).
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

- Put only **one** question at a time, wait for the answer.
- For the questions during the loop, use the **question format with a phase header** (`[PHASE · iter n/max X · PHASE/Qnn]`).
