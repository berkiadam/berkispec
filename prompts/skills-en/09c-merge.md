---
phase: 09c
name: bs-merge
description: "berkispec - 09c. Use it after the review that ran on the PR (Phase 09c), as the last mandatory step of the three-step end of the cycle. It checks the state of the PR (is it approved — this takes over the role of RD8), runs the post-merge test round (VP2: tests + Sonar) on the cycle branch, and gets the code onto the main branch ONLY after a green result."
prerequisites:
  - "An opened, APPROVED PR for the cycle branch (bs-create-pr + bs-review have run)"
  - "specs/cycle-NN-<name>/test-report/code-review.md and ci-code-review.md — no unresolved Must Fix"
  - "conventions.md `## <sec:cv_review_and_merge>` — `PR submission: yes`"
output:
  - "specs/cycle-NN-<name>/test-report/post-merge/ — the evidence of the VP2 round (on success and on failure alike)"
  - "A merged cycle branch (the PR merged according to the Merge strategy of conventions.md)"
  - "specs/cycle-NN-<name>/cycle-status.md — generated cycle status"
  - "specs/roadmap.md — closed if there is no bs-dev-test switched on"
prev: bs-review
next: bs-dev-test
scripts:
  - "scripts/validate-gate-check.py --review-only --require-ci-review — the gate of the two review reports"
  - "scripts/run-tests.py — running the VP2 round (--phase post-merge)"
  - "scripts/sonar-gate.py — the static layer of the VP2 round"
  - "scripts/report-gate-check.py — the report artifacts of the VP2 round (TR3)"
  - "scripts/test-manager.py — optional test manager upload (TM4/TM6)"
  - "scripts/notify.py — notification on failure (CS6)"
  - "scripts/cycle-status.py — the generated cycle-status.md (--write)"
---
# 09c — Merge (with the post-merge test round)
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

This is the **third step of the end of the cycle on the three-step (PR) path**: 9a-create-pr · 9b-review · **9c-merge ←** · (9d-dev-test).

> **🔴 `VP2` is the gate BEFORE the code reaches the main branch (L13-D6/L13-D14).** The round runs **on the cycle branch**, on the code merged with the fresh main branch — and the code goes onto the main branch only after a green result. On a failure the shared main branch **stays untouched**, the PR stays open and the cycle branch lives: the `CS6` requirement of "commit it into the cycle branch" is thereby satisfied **by itself**, and nobody has to come back from a broken main branch.

> **The place of the confirmation has changed (L13-D5).** In isolated mode the user confirms before the merge (RD8). **In centralized mode this is taken over by the approval of the PR** — that is a human decision too, only earlier and elsewhere, and **it leaves a trace at the provider**. So that the guarantee stays measurable, this skill **checks the state of the PR** and stops if it is not approved.

---

## <field:f_prerequisite>

0. **Identifying the cycle:** the input is the folder of the cycle. In a machine run the adapter hands it over — do not ask back. In an interactive run: <!-- INCLUDE:lang/common.md#ciklus-beazonositas -->

1. **`conventions.md`:** `## <sec:cv_merge_strategy>` + `## <sec:cv_review_and_merge>`. If `PR submission` is not `yes`, **STOP** — go to `bs-review-and-merge`.

2. **🔴 PR state gate (L13-D5):** is the PR **approved**, and are the branch protection requirements satisfied?
   ```bash
   gh pr view feature/cycle-NN-<cycle-name> --json state,reviewDecision,mergeStateStatus
   ```
   _(GitLab: `glab mr view`; Bitbucket: the access command of `conventions.md`.)_
   - **`reviewDecision: APPROVED` + no blocking check** → continue.
   - **anything else** (an open change request, a pending required check, a draft PR) → **STOP**. Without this `RD8` would not be relocated but would **disappear**: on the centralized path there is nobody in the loop to notice it.

3. **Review gate — BOTH reports (L13-D1 / Q21):**
   <!-- INCLUDE:shared/python-cmd.md -->
   ```bash
   python3 <platform-scripts-mappa>/validate-gate-check.py \
     specs/cycle-NN-<cycle-name> --review-only --require-ci-review
   ```
   The gate reads the local `code-review.md` of `07` **and** the `ci-code-review.md` of `bs-review`: neither may contain an open `<status:must_fix>`, and neither may be unfinished (RV-INC). **This is not a new enforcement**, but the distribution of the precondition of today's `09` — without it, splitting into three skills would lose the protection that exists today.

4. **Status gate:** `tasks.md` / `plan.md` / `spec.md` = `<status:done>`, without a `[validate-loop]` marker.

5. **Doc-sync gate:** `doc-sync-plan.md` exists, all of its items are ticked, there is no open `doc-sync-questions.md` question.

---

## Your task

1. **Integration update:** bringing the main branch into the cycle branch (W2).
2. **`VP2` — the post-merge test round** on the cycle branch: tests + Sonar + report gate.
3. **Only after a green result:** merging the PR (getting the code onto the main branch).
4. **Closing:** the roadmap, the generated `cycle-status.md`, and handing over to `bs-dev-test` if it is switched on.

---

## 1. Integration update (W2 / RM5)

```bash
git fetch origin
git log --oneline HEAD..origin/main
```

- **An empty list → the main branch has not moved ahead.** The `Skip post-merge tests if master unchanged` field decides (RM11): `yes` → `VP2` may be skipped (write the reason of the skip into `test-report/post-merge/skipped.md`, with the SHA of the main branch); `no` → the round runs anyway.
- **A non-empty list →** bring the main branch into the cycle branch. Since the branch is pushed and has a PR, the correct mechanics is a **merge** (a rebase would require a force push on a branch under review):
  ```bash
  PRE=$(git rev-parse HEAD)
  git merge origin/main
  git diff --name-only "$PRE" HEAD
  ```
  If the change brought in touches the scope of the cycle (the same files, the same contract), the `VP2` round is **mandatory** — and if `VP2` fails, the rule is the *Failure of `VP2`* section. On a conflict: do not invent the resolution, and in an ambiguous case **STOP** (in a machine run `merge-questions.md` + `exit 2`).

---

## 2. `VP2` — the post-merge test round on the cycle branch

> **🔴 On the centralized path the tests of `VP2` typically have to be fully containerizable (`CS4`):** on the test node of the CI a **complete test environment with mocks** has to be brought up with `compose`, and the tests have to run in it, **already with the code merged with the main branch**. The **recipe** of the environment (how the stack starts, which mock, which test user) belongs into `specs/test-conventions.md` (TC1/c), the report artifacts and the commands into `conventions.md`.

### 2/a. Tests

```bash
python3 <platform-scripts-mappa>/run-tests.py \
  specs/cycle-NN-<cycle-name>/plan.md \
  --round-dir specs/cycle-NN-<cycle-name>/test-report/post-merge \
  --phase <status:phase_post_merge>
```

The `<field:f_prerequisite>` and the `Cleanup` column bring the setup and the teardown of the compose environment — the cleanup runs even if the execution blew up. A `MEGJEGYZÉS (PH1)` line ("there is nothing to run") next to a switched-on `Post-merge tests` is **a gap in the plan**, not "nothing to do": in a machine run this is `merge-questions.md` + `exit 2`.

### 2/b. Sonar — the static layer of the round

```bash
python3 <platform-scripts-mappa>/sonar-gate.py \
  --out specs/cycle-NN-<cycle-name>/test-report/post-merge/sonar-report.md
```

The same script with the same `conventions.md` thresholds as in `07`: the merge brings in new code that the Sonar round of `07` never saw.

### 2/c. Report gate

```bash
python3 <platform-scripts-mappa>/report-gate-check.py \
  conventions.md specs/cycle-NN-<cycle-name> \
  --report-subdir test-report/post-merge
```

**Success and failure both leave a trace** — the `test-report/post-merge/` set goes into the folder and the branch of the cycle, committed and pushed, so it is visible on the PR as well.

### 2/d. Test manager (optional, TM4)

If the `**<field:f_test_manager_phases>:**` field lists the `post-merge` phase, `--mode preflight` runs **before** the round and `--mode publish` **after** it (`test-manager.py`), and the run URL goes into the report from the last line of the output (`TEST_MANAGER_RUN_URL=`). **The upload is not evidence** (TM7), and its failure does not fail the round by default.

### Failure of `VP2`

1. The evidence is already in place — **do not delete it, do not overwrite it**. Commit it and push it onto the cycle branch: this way it is visible on the PR.
2. **The main branch is untouched**, the PR stays open.
3. `Failure handling: notify` (the default) → a notification (`notify.py --phase post-merge --status fail`), and a **human** starts the fix: the items go into the `## <sec:post_merge_fixes>` section of `tasks.md`, then `/bs-implement` (fix mode) → `/bs-validate` → back here.
4. `Failure handling: auto-fix-loop` → the fix loop starts on the CI, with the **unchanged** stopping limits of the loop of `07`, then escalation to a human.
5. **The explicit exception** (L13-D8): if the failure **does not belong to this cycle** (a regression of another cycle, an environment error), a new cycle is started for it, and this cycle can be closed. The decision is human, based on the report — in a machine run this is `exit 2` + a question.

---

## 3. The merge

Only after a green `VP2` (or if the round did not run). According to the **<field:f_provider>** and **Merge type** fields of the `## <sec:cv_merge_strategy>` section of `conventions.md`:

```bash
gh pr merge feature/cycle-NN-<cycle-name> --squash --delete-branch=false
```

_(GitLab: `glab mr merge`; Bitbucket: the access command of `conventions.md`. The merge type comes from `conventions.md` — squash / merge commit / rebase.)_

> **🔴 Do NOT delete the cycle branch here** (L13-D7). If `Dev deployment test` is switched on, the `VP3` round is still ahead, and its failure has to write onto the path of the cycle — the vehicle for that is a `<cycle-branch>-dev-test` branch opened from the main branch, but until that has run, keep the cycle branch.
>
> **In isolated mode (there is a PR, but the merge happens on your machine)** the user confirmation before the merge is **mandatory** (RD8):
> <!-- INCLUDE:lang/09-merge.md#RD8-merge-megerosites -->

---

## 4. Closing

1. **Roadmap:** if `Dev deployment test` is **not** switched on, `VP2` was the last enabled verification — mark the cycle as closed (`✅`). If it **is** switched on, the cycle row stays at `<status:waiting_for_verification>` (L13-D8).
2. **Generated cycle status:**
   ```bash
   python3 <platform-scripts-mappa>/cycle-status.py specs/cycle-NN-<cycle-name> --write
   ```
3. Give the next step:

<!-- INCLUDE:lang/09-merge.md#zaro-uzenet-merge -->
