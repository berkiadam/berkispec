---
phase: 09b
name: bs-review
description: "berkispec - 09b. Use it after the PR has been opened (Phase 09b), as the second step of the three-step (PR) end of the cycle. It runs the reviewer subagent on the diff of the PR — in centralized SDD as a machine run on the CI/CD, without human intervention — and writes into 'test-report/ci-code-review.md'. It NEVER overwrites the local 'code-review.md' of 07."
prerequisites:
  - "An opened PR for the cycle branch (bs-create-pr has run)"
  - "specs/cycle-NN-<name>/test-report/code-review.md — no unresolved Must Fix (the review gate of 07)"
  - "conventions.md `## <sec:cv_review_and_merge>` — `PR submission: yes`"
output:
  - "specs/cycle-NN-<name>/test-report/ci-code-review.md — the findings of the review run on the PR (RV-INC, written incrementally)"
  - "specs/cycle-NN-<name>/review-questions.md — if a decision is needed in non-interactive mode (exit 2)"
prev: bs-create-pr
next: bs-merge
subagents:
  - "agents/reviewer.md"
scripts:
  - "scripts/validate-gate-check.py — the gate of an unfinished review (RV-INC)"
  - "scripts/notify.py — notification on an open Must Fix (CS6)"
  - "scripts/cycle-status.py — the generated cycle-status.md (--write)"
shared:
  - "shared/review-checklist.md"
---
# 09b — Review on the PR
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

This is the **second step of the end of the cycle on the three-step (PR) path**: 9a-create-pr · **9b-review ←** · 9c-merge · (9d-dev-test).

> **Why a second review if there already was one in `07` (RV1).** The review of `07` ran **on the cycle branch, on the old base**, on the developer's machine. This round runs **on the PR** — against the main branch — and in centralized SDD as a **machine run, without human intervention** (`CS2`). The two rounds do **not** look at the same diff, which is why they write into **two separate files**.

> **🔴 The evidence of `07` is inviolable.** This skill writes into `test-report/ci-code-review.md`; it **never overwrites or edits** `test-report/code-review.md`. The entry gate of `bs-merge` reads **both files**.

---

## <field:f_prerequisite>

0. **Identifying the cycle:** the input is the folder of the cycle (`input: @specs/cycle-NN-<cycle-name>`). In a machine run the adapter hands it over — do not ask back (see *The non-interactive contract*). In an interactive run, the usual confirmation: <!-- INCLUDE:lang/common.md#ciklus-beazonositas -->

1. **`conventions.md`:** `## <sec:cv_review_and_merge>` — if `PR submission` is not `yes`, this is not the right skill: **STOP**, go to `bs-review-and-merge`.

2. **PR gate:** is there an open PR for the cycle branch? (`gh pr view <branch> --json state,url` / `glab mr view` / the access command of the provider.) If there is none, **STOP** — run `bs-create-pr` first.

3. **Review gate (RV1):** `test-report/code-review.md` exists and contains no unresolved `- [ ]` in the `<sec:critical_fixes>` section. If there is one, `07` has not closed — **STOP**, back to `07`.

4. **Continuing after an interrupted run (RV-INC):** if the header of `test-report/ci-code-review.md` says `<field:f_status>` = `<status:in_progress>`, the findings in it are **real, only incomplete** — do not throw them away and do not overwrite them, continue the review from where it stopped.

---

## Your task

1. **Determining the scope of the review:** the diff of the PR against the target branch.
2. **Running the `reviewer` subagent** on that diff, with the shared checklist.
3. **Evaluating the findings** and the verdict — from the gates, not from the self-report of the agent.

<!-- INCLUDE:shared/review-checklist.md -->

---

## 1. The scope of the review

```bash
git fetch origin
git diff --name-only origin/main...HEAD
```

_In place of `main` comes the **<field:f_main_branch>** field of the `## <sec:cv_git_conventions>` section of `conventions.md` (or the target branch of the PR). The three dots (`...`) give the changes produced on the cycle branch since the branching point — exactly what the PR shows._

The contract of the `reviewer` subagent is unchanged (`agents/reviewer.md`), with two substitutions:
- the **scope** is the diff of the PR (not the whole history of the cycle branch);
- the **output file** is `specs/cycle-NN-<cycle-name>/test-report/ci-code-review.md`.

---

## 2. The verdict — from the gates, not from the agent

> **🔴 The exit code of the agent is not a verdict.** Most CLIs exit with `0` even when the work turned out badly. The verdict of the phase therefore comes from a **deterministic gate**:

<!-- INCLUDE:shared/python-cmd.md -->

```bash
python3 <platform-scripts-mappa>/validate-gate-check.py \
  specs/cycle-NN-<cycle-name> --review-only
```

- **The header of `ci-code-review.md` says `<status:in_progress>`** → the review is **unfinished**: the round can be closed neither as green nor as FAIL (RV-INC). It has to be continued.
- **No open `<status:must_fix>`** → the phase is green, `bs-merge` can follow.
- **There is an open `<status:must_fix>`** → the phase is **FAIL**:
  1. notification (`Failure handling: notify` — the default):
     ```bash
     python3 <platform-scripts-mappa>/notify.py --phase review \
       --cycle specs/cycle-NN-<cycle-name> --status fail
     ```
  2. the PR **stays open**, the cycle branch lives, and the developer fixes it on their own machine: the findings go into the `## <sec:review_fixes>` section of `tasks.md`, and the fix mode of `/bs-implement` + `/bs-validate` runs on them;
  3. with `Failure handling: auto-fix-loop` the fix loop starts on the CI — with the **unchanged** stopping limits of the loop of `07` (per item 3 consecutive / 5 total failures, 5 consecutive FAIL runs), then escalation to a human. After the limit is reached, **the same notification** goes out as on the `notify` branch.

---

## The non-interactive contract (a machine run on the CI)

In centralized SDD this skill is started by the `ci-run-skill.sh` adapter, not by a human. An interactive question in that case either waits forever or — worse — **invents an answer**. Therefore:

> **In non-interactive mode the question = STOP.** Write the question into `specs/cycle-NN-<cycle-name>/review-questions.md` (following the pattern of `doc-sync-questions.md`), send a notification, and the adapter returns with `exit 2`. The PR stays open, and the developer continues on their own machine.

**Do not guess, and do not "decide instead of them":** an invented answer stays unnoticed in a machine run, because there is nobody in the loop to notice it.

---

## Closing

1. Regenerate the generated cycle status:
   ```bash
   python3 <platform-scripts-mappa>/cycle-status.py specs/cycle-NN-<cycle-name> --write
   ```
2. Commit `ci-code-review.md` and `cycle-status.md` onto the **cycle branch** (into the PR), and push them.
3. Give the next step:

<!-- INCLUDE:lang/09-merge.md#zaro-uzenet-review -->
