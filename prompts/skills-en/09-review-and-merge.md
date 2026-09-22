---
phase: 09
name: bs-review-and-merge
description: "berkispec - 09. Use it as the last step of the cycle (Phase 09) if the code, the review and the documentation are all 'Done', AND the '## Review and merge' section of conventions.md says 'PR submission: no'. A single skill: bringing in the main branch into the cycle branch → post-merge test round (VP2: tests + Sonar) → merge with mandatory user confirmation (RD8) → closing the roadmap. With a PR requirement it errors out and redirects to the bs-create-pr → bs-review → bs-merge chain."
prerequisites:
  - "specs/cycle-NN-<name>/tasks.md status: <status:done>"
  - "specs/cycle-NN-<name>/plan.md status: <status:done>"
  - "specs/cycle-NN-<name>/spec.md status: <status:done>"
  - "specs/cycle-NN-<name>/test-report/code-review.md — no unresolved Must Fix (the review gate of 07)"
  - "conventions.md `## <sec:cv_review_and_merge>` — `PR submission: no` (otherwise STOP, L13-D1)"
output:
  - "specs/cycle-NN-<name>/test-report/post-merge/ — the evidence of the VP2 round (on success and on failure alike)"
  - "specs/cycle-NN-<name>/cycle-status.md — generated cycle status (L13-D9)"
  - "Merged cycle branch (local merge according to the Merge strategy of conventions.md)"
  - "specs/roadmap.md — the cycle marked as closed"
prev: bs-doc-sync
next: bs-write-spec
scripts:
  - "scripts/run-tests.py — running the VP2 round from the machine table of the plan (--phase post-merge)"
  - "scripts/sonar-gate.py — the static layer of the VP2 round, with unchanged thresholds"
  - "scripts/report-gate-check.py — the report artifacts of the VP2 round (TR3)"
  - "scripts/test-manager.py — optional test manager upload (TM4/TM6)"
  - "scripts/notify.py — notification on failure (CS6/L13-D11)"
  - "scripts/cycle-status.py — the generated cycle-status.md (--write)"
---
# 09 — Review and merge (isolated path, without a PR)
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

We develop software in spec driven development. The development is split into cycles. Every cycle is an independently developable, independently testable part of the whole implementation.

This is **phase 9 of the process (0–9)**: 0-init · 1-cycles · 2-spec · 3-plan · 4-tasks · 5-analyze · 6-implement · 7-validate (tests + review) · 8-doc-sync · **9-review-and-merge ←**.

> **The code review is NOT in this phase (RV1).** The `reviewer` subagent and the self-healing review loop moved into the **`07-validate`** phase. By the time you get here the review is already clean — in this skill the *review* is the **human approval** (RD8), not another agent run.

> **🔴 There are three verification points (VP1–VP3), and this phase runs the second one.** `07` (`VP1`) proved that **functionally what was built** is what the spec asked for — on the cycle branch, on the old base. **`VP2`** proves that it also works according to the spec **merged with the main branch**. `VP3` (`bs-dev-test`) does not make sense on this path (that is an option of the centralized path).

---

## <field:f_prerequisite>

0. **Identifying the cycle:** if the user named a cycle/file, use that; otherwise offer the most recent `specs/cycle-*` folder for confirmation — <!-- INCLUDE:lang/common.md#ciklus-beazonositas --> — and wait for the answer before moving on.

1. **Checking that `conventions.md` exists:** read `conventions.md` in the project root — the `## <sec:cv_merge_strategy>` and the `## <sec:cv_review_and_merge>` section. If it does not exist, STOP — they should return to phase `00`.

1.b **🔴 Topology gate (L13-D1) — this is the only hard enforcement in this family.** The `PR submission` field of the `## <sec:cv_review_and_merge>` section decides:
   - **`no`** → this is the right skill, continue.
   - **`yes`** → **STOP, error.** This skill may only be used in the PR-less (single-step) mode: <!-- INCLUDE:lang/09-merge.md#L13-D1-pr-kotelezo --> Do not bypass the PR — code pushed onto `main` cannot be taken back afterwards, and bypassing the PR is a **policy violation**, not a matter of convenience.
   - **`n/a` (a no-VCS project, BD11/L13-D20)** → in this project the cycle closes after `08-doc-sync`: none of the merge family runs. Say so, close the cycle on the roadmap, and stop.

2. **Working tree check:** run `git status --short`. If there are uncommitted changes, list them and ask in one round whether I should commit now or continue — wait for the answer. You work on the **own feature branch** of the cycle; switching to the main branch happens later, in the Merge step, after user confirmation (RD8) — do not switch here.

2.b **Worktree situation (W1):** this phase switches to the main branch, so **it has to run in the worktree that contains `main`**. Check:

   ```bash
   git worktree list
   git rev-parse --git-common-dir     # if it is not `.git`, we are in a linked worktree
   ```

   - **A single worktree** → nothing to do, the steps below are fine as they are.
   - **We are in a linked worktree** → **STOP.** `git switch main` would be refused here ("already used by worktree"). The `06`–`09` stretch runs in the **main** worktree: the cycle has to be moved back there (`git worktree remove ../<cycle-worktree>`, then `git switch feature/cycle-NN-<cycle-name>` in the main worktree) and continued from there. Commit the uncommitted content first — do **not** use `--force`.
   - **There is ANOTHER worktree on a `cycle-*` branch** → that is a cycle being planned in parallel. It does **not** block the merge (the other cycle is at most at `05`), but say so after the merge: before `06`, the other cycle has to bring in the fresh `main` and re-run `05` (PW2).

3. **Status gate:** on PASS the validate phase (07) sets the status of all three files to `<status:done>`. Check:
   - the status of `tasks.md`: `<status:done>` — and **there is no `[validate-loop]` marker on it** (the marker means a stuck loop)
   - the status of `plan.md`: `<status:done>`
   - the status of `spec.md`: `<status:done>`

   If any of them is not `<status:done>`, the validation has not completed successfully — return to phase `07`.

4. **Review gate (RV1):** `specs/cycle-NN-<name>/test-report/code-review.md` has to exist, and **it may not contain an unresolved `- [ ]` in the `<sec:critical_fixes>` section**. If it is missing or there is an open `<status:must_fix>`, the review gate of 07 has not closed — **STOP**, return to phase `07`. **Do not merge without a review**, and do not run the review "quickly" here: that is the job of 07, with its own fix loop and stopping limits.

5. **Doc-sync gate:** the `08-doc-sync` phase had to run on the validated code. Check that the `doc-sync-plan.md` of the cycle exists, that it has no unfinished `[ ]` item, that there is no open `doc-sync-questions.md` question, and that the DS22 gate was green. If this is not true, return to the `08-doc-sync` phase.

---

## Your task

Closing the cycle in **four steps, in a fixed order** (L13-D14):

1. **Pre-merge doc-sync check** (DS23.2) — has code changed since `08`.
2. **Integration update:** bringing the main branch **into the cycle branch** (rebase or merge, W2/RM5).
3. **`VP2` — post-merge test round on the cycle branch**, on the code merged with the fresh main branch: tests + Sonar + report gate.
4. **The merge** after mandatory user confirmation (RD8), then **deleting the cycle branch**, closing the roadmap and the generated `cycle-status.md`.

> **🔴 The order is not interchangeable.** `VP2` runs **before** the merge, on the cycle branch. The other way round, at the moment of a failure the whole diff of the cycle would already be on `main`, and bringing the fix back would be a **second** squash merge. This way, on a failure `main` is **untouched**, the fix goes on the cycle branch, and the merge happens once.

In this phase there is **no self-healing loop and no subagent**: if any of the pre-merge checks fails, the correct step is redirecting to `07` or `08`, not fixing it here.

---

## 1. Pre-merge doc-sync check (DS23.2)

`08-doc-sync` and the review gate of `07` are **independent gates**. The reviewer only gives code findings (`test-report/code-review.md`); the correctness of the generated documentation is guaranteed by the own DS22 gate of `08-doc-sync`.

1. **Has code changed since the closing commit of `08-doc-sync`?**
   ```bash
   BASE=$(git log --format=%H -1 --grep="^cycle-NN: 08-doc-sync")
   git diff --name-only "$BASE" HEAD
   ```
   - If **no** (an empty list, or only paths under `specs/`), there is nothing to do.
   - If **yes**, restart `08-doc-sync` on the final code:
     ```text
     /bs-doc-sync input: @specs/cycle-NN-<cycle-name>
     ```
2. Wait until the DS22 gate of `08-doc-sync` is green, there is no open `doc-sync-questions.md` question, and every item of `doc-sync-plan.md` is ticked.
3. After doc-sync has run, come back here.

It is **forbidden** to produce any code finding here or to turn doc-sync into a review: code → the review gate of `07`; docs → `doc-sync-plan.md` / `doc-sync-questions.md` + the DS22 gate.

---

## 2. Integration update — bringing the main branch into the cycle branch (W2 / RM5)

The green tests of `07` and the docs of `08` were produced **on the base** the cycle branched off from. If the main branch has moved ahead in the meantime, the merge would create a **combination that was never tested**:

```bash
git fetch origin
git log --oneline HEAD..origin/main
```

_In a repo without a remote (local only), work with the local `main` instead of `origin/main`, without `git fetch`. In place of `main` comes the **<field:f_main_branch>** field of the `## <sec:cv_git_conventions>` section of `conventions.md`._

_There is **deliberately no `$( )` substitution** in the command: `HEAD..origin/main` gives the same commit set as the `merge-base` form, but several CLIs (e.g. Antigravity/Gemini) do not allow command substitution to be allowlisted for security reasons — such a line would ask for permission on every run._

- **An empty list → the main branch has NOT moved ahead.** In that case the `Skip post-merge tests if master unchanged` field of `## <sec:cv_review_and_merge>` decides (RM11):
  - **`yes`** → the `VP2` round **may be skipped**: it would measure exactly what `07` has just measured, on the same code. **The skip may not stay unmarked** — write one line into `test-report/post-merge/skipped.md` saying *"VP2 skipped: the main branch has not moved ahead since the cycle branched off (`git log HEAD..origin/main` is empty), `Skip post-merge tests if master unchanged: yes`"*, together with the SHA of the main branch. Jump to step 4.
  - **`no`** → the `VP2` round runs anyway (step 3).
  - _(Cross-check: does the main branch SHA of the **<field:f_validated_base>** field of `analyze-report.md` show the same — if not, `05` closed on an older base, and the re-validation rule below applies.)_
- **A non-empty list → the main branch has to be brought into the cycle branch:**

1. **Bringing it in** (the same mechanics as step BR1 of `05`). The choice is not a matter of taste:
   - the branch is **not pushed / has no PR** (`git rev-parse --verify origin/feature/cycle-NN-<cycle-name>` errors out) → `git rebase origin/main` (a linear history; the `cycle-NN: <phase>` commit messages survive, so the `git log --grep` based searches keep working),
   - the branch **is pushed** → `git merge origin/main` into the cycle branch (a rebase would require a force push).
   - On a conflict the rules of *Handling a merge conflict* below apply — do **not** resolve the generated docs (`docs-generated/`) and `specs/test-conventions.md` by hand: those are restored by re-running `08`.
2. **Re-validation according to the base brought in.** BEFORE bringing it in, note the tip of the cycle branch (`PRE=$(git rev-parse HEAD)`), afterwards look at what came in: `git diff --name-only "$PRE" HEAD`. According to the nature of the hits:
   - **source code or a test changed** → the `VP2` round (step 3) is **mandatory**. If the change brought in touches the scope of the cycle (the same files, the same contract), **STOP**, return to `07` on the fresh base; after the PASS of `07` come back here.
   - **only `docs-generated/`, `conventions.md` or `specs/test-conventions.md` changed** → **STOP**, return to `08`. Come back here after a green DS22 gate.
   - **only the `specs/cycle-MM-*/` folders of other cycles changed** → nothing to do, continue with the `VP2` round.

**Do not ask for permission for bringing it in separately** (you work on the own branch of the cycle, this is not destructive) — but **always signal** the redirection to `07`/`08`, because that is a phase change.

---

## 3. `VP2` — post-merge test round on the cycle branch

It runs if the `Post-merge tests` field of `## <sec:cv_review_and_merge>` is `yes` and step 2 did not skip it (RM11). **The round runs on the cycle branch, on the code merged with the fresh main branch, BEFORE the merge.**

> **A local run — containerization is not mandatory (RM10).** On this path everything runs on the developer's machine, so the tests of the `VP2` round do **not** have to be fully containerizable (that is a requirement of the centralized path, `CS4`).

<!-- INCLUDE:shared/python-cmd.md -->

### 3/a. Tests — from the machine table of the plan, with the `post-merge` phase filter

```bash
python3 <platform-scripts-mappa>/run-tests.py \
  specs/cycle-NN-<cycle-name>/plan.md \
  --round-dir specs/cycle-NN-<cycle-name>/test-report/post-merge \
  --phase <status:phase_post_merge>
```

- **`exit 0`** → the round is green, `results.json` and the report artifacts are in the `test-report/post-merge/` folder.
- **`exit 1`** → failure → the *Failure of `VP2`* section.
- **a `MEGJEGYZÉS (PH1)` line saying "there is nothing to run"** → not a single row of the plan table carries the `<status:phase_post_merge>` value while `conventions.md` switched the round on. **This is not "nothing to do" but a gap in the plan:** STOP, and ask the user which categories belong to the post-merge round — the answer goes into the `<field:f_phase>` column of the machine table of `plan.md` (fixing `conventions.md`/`plan.md` is part of the cycle in such a case, GC1).
- **`exit 2/3/4`** → the same meaning as in `07` (missing machine table / placeholder error / environment error): a gap of `03`, not a code bug.

### 3/b. Sonar — the static layer of the round

**Sonar is part of the post-merge round too, exactly as in `07`** — in both modes, not only in CI/CD. The merge **brings in new code** into the cycle branch that the Sonar round of `07` **never saw**: static defects can arise from the merge just as runtime ones can. Zero new machinery — the same script, the same `conventions.md` thresholds:

```bash
python3 <platform-scripts-mappa>/sonar-gate.py \
  --out specs/cycle-NN-<cycle-name>/test-report/post-merge/sonar-report.md
```

The exit code decides (`0` OK · `1` FAIL because of a finding · `3` FAIL because of a threshold, QG1 · `2` usage error) — exactly as in step 2/a of `07`. If `conventions.md` has no `## <sec:cv_sonar>` section, this step is skipped.

### 3/c. Report gate

```bash
python3 <platform-scripts-mappa>/report-gate-check.py \
  conventions.md specs/cycle-NN-<cycle-name> \
  --report-subdir test-report/post-merge
```

The gate enforces the artifacts of the TR3 table of `conventions.md` if the `**<field:f_report_phases>:**` field lists the `post-merge` phase. **Success and failure both leave a trace:** the `test-report/post-merge/` set goes into the folder and the branch of the cycle, committed — this way the *it ran and was green* case stays distinguishable afterwards from the *nobody ever tried* case.

### 3/d. Test manager (optional, TM4)

If the `**<field:f_test_manager_phases>:**` field of the `## <sec:cv_test_reporting>` section of `conventions.md` lists the `post-merge` phase:

```bash
python3 <platform-scripts-mappa>/test-manager.py --mode preflight --phase post-merge \
  --round-dir specs/cycle-NN-<cycle-name>/test-report/post-merge          # BEFORE the test round
python3 <platform-scripts-mappa>/test-manager.py --mode publish --phase post-merge \
  --round-dir specs/cycle-NN-<cycle-name>/test-report/post-merge          # AFTER the test round
```

The last line of the output is `TEST_MANAGER_RUN_URL=<url>`. **The upload is not evidence** (TM7): the evidence of the cycle remains the committed report set, the URL is only a pointer. `exit 3` = the phase is not on the list (skipped, not an error); `exit 4` = the upload failed — by default this does **not** fail the round (`**<field:f_test_manager_required>:**` is `no`), but a line about it goes into the report.

### Failure of `VP2`

The failure is **not a reopening**, but the continuation of the still open cycle (L13-D8):

1. The evidence is already in place (`test-report/post-merge/`) — **do not delete it, do not overwrite it**.
2. **Notification** (`Failure handling: notify`, the default):
   ```bash
   python3 <platform-scripts-mappa>/notify.py --phase post-merge \
     --cycle specs/cycle-NN-<cycle-name> --status fail
   ```
   If `Notification channel` is `none`, this step is skipped.
3. **A decision — whose fault is it?** This is a human decision, based on the report:
   - **it belongs to this cycle** → the fix goes into the **`## <sec:post_merge_fixes>`** section of `tasks.md`, and the existing machinery runs on it: `/bs-implement` (fix mode) → `/bs-validate`, then back here from step 2. The cycle branch **lives**, `main` is untouched.
   - **it does not belong to this cycle** (a regression of another cycle, an environment error) → a **new cycle** is started for it (`/bs-add-cycles`), and this cycle can be closed. State in the report why.
4. Regenerate `cycle-status.md` (see step 5) and stop.

---

## 4. The merge — according to the Merge strategy of conventions.md

Only if `VP2` **was green** (or did not run because of `Post-merge tests: no` / the RM11 skip).

Read the `## <sec:cv_merge_strategy>` section of `conventions.md` and proceed according to the **<field:f_provider>** field. **Before the merge the user confirmation is MANDATORY** (RD8) — merging into the main branch and deleting the branch are destructive, they may not be performed without confirmation.

### Confirmation (mandatory)

Ask, and **wait for an explicit confirmation**:
<!-- INCLUDE:lang/09-merge.md#RD8-merge-megerosites -->
> **At the end of the answer put the direct, clickable link of `test-report/validation-report.md`, `test-report/code-review.md` and — if there was a `VP2` round — `test-report/post-merge/`.**

Do not move on before the confirmation.

### The merge itself

After the confirmation:
```bash
# 1. Switch to the main branch (the <field:f_main_branch> field of
#    `## <sec:cv_git_conventions>`, or the `## <sec:cv_merge_strategy>` PR target — `main`)
git switch main

# 2. Squash merge from the cycle branch
git merge --squash feature/cycle-NN-<cycle-name>

# 3. Commit with the title of the cycle and the objective from the plan
git commit -m "cycle-NN: 09-merge - <title>" -m "<goal and approach from plan.md>"

# 4. Deleting the local cycle branch — ONLY AFTER a green VP2 (L13-D7)
git branch -D feature/cycle-NN-<cycle-name>
```

> **🔴 Delete the cycle branch behind the verification.** On the isolated path `VP2` and all of its fix rounds run **on the same branch** — if we deleted it right after the merge, the evidence of the failure and the fix would have no vehicle left. This is why the deletion is the last step.

> **W3 — if the cycle branch is still checked out in a worktree**, `git branch -D` refuses ("used by worktree"). In that case first `git worktree remove <path>` (with uncommitted content, commit first, without `--force`), and only then delete the branch. An abandoned entry is cleaned up by `git worktree prune`.

### Handling a merge conflict

If a merge conflict arises during the merge:
1. **Do NOT invent the resolution.** List the conflicting files (`git status`).
2. For every conflicting file look at both sides (the main branch and the cycle branch version), and decide from `plan.md` / `spec.md` which one is correct — or whether the two have to be merged.
3. If the resolution is unambiguous based on the intent of the cycle, resolve it, re-run the relevant check, then commit.
4. **If the resolution is not unambiguous** (both sides contain substantial, conflicting logic), STOP — show the user the conflicting files and the two sides, and ask for a decision.

---

## 5. Roadmap, cycle status and closing

**The cycle is done when the LAST enabled verification is green** (L13-D8). On this path that is `VP2` (or `07`, if `Post-merge tests: no`) — so after the merge the cycle can **really** be closed.

1. **Roadmap:** mark the cycle as closed in `specs/roadmap.md` (`✅` / `(done)`), and commit it.
2. **Generated cycle status** (L13-D9/L13-D15):
   ```bash
   python3 <platform-scripts-mappa>/cycle-status.py specs/cycle-NN-<cycle-name> --write
   ```
   `cycle-status.md` is a **generated file, not hand-written**: a rendering of the evidence, never a source — a gate never reads it. Commit it together with the roadmap update.
3. Tell the user that the cycle is closed, and give the starting prompt of the next cycle:

<!-- INCLUDE:lang/09-merge.md#zaro-uzenet -->
