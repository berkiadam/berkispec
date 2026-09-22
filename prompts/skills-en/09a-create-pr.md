---
phase: 09a
name: bs-create-pr
description: "berkispec - 09a. Use it as the FIRST step of closing the cycle (Phase 09a) if the '## Review and merge' section of conventions.md says 'PR submission: yes'. Pushing the cycle branch and opening the PR according to the Merge strategy of conventions.md — the review and the merge are two separate skills (bs-review → bs-merge). It does NOT merge the PR."
prerequisites:
  - "specs/cycle-NN-<name>/tasks.md status: <status:done>"
  - "specs/cycle-NN-<name>/plan.md status: <status:done>"
  - "specs/cycle-NN-<name>/spec.md status: <status:done>"
  - "specs/cycle-NN-<name>/test-report/code-review.md — no unresolved Must Fix (the review gate of 07)"
  - "conventions.md `## <sec:cv_review_and_merge>` — `PR submission: yes`"
output:
  - "A pushed cycle branch + an opened PR at the provider of conventions.md"
  - "specs/cycle-NN-<name>/cycle-status.md — generated cycle status with the PR link (L13-D9)"
prev: bs-doc-sync
next: bs-review
scripts:
  - "scripts/cycle-status.py — the generated cycle-status.md (--write)"
  - "scripts/notify.py — notification if opening the PR stops in non-interactive mode"
---
# 09a — Creating the PR
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

We develop software in spec driven development. The development is split into cycles. Every cycle is an independently developable, independently testable part of the whole implementation.

This is the **first step of the end of the cycle on the three-step (PR) path**: **9a-create-pr ←** · 9b-review · 9c-merge · (9d-dev-test).

> **Why three skills and not one interrupted phase (L13-D1).** Once the PR appears, **external actors** have a say in the process (the PR approver, the CI/CD). The skill boundary is the best interruption tolerance (principle 13): the trace left on disk is the **phase boundary** itself, not a marker — the agent after a `/clear` knows where things stand from which skill is called next.

> **The topology is decided by the presence of a PR, not by the mode.** This chain is the same in **isolated** SDD too if there is a PR submission — the only difference is whether `bs-review` and `bs-merge` run on the developer's machine or on the CI/CD.

---

## <field:f_prerequisite>

0. **Identifying the cycle:** if the user named a cycle/file, use that; otherwise offer the most recent `specs/cycle-*` folder for confirmation — <!-- INCLUDE:lang/common.md#ciklus-beazonositas --> — and wait for the answer before moving on.

1. **`conventions.md`:** read the `## <sec:cv_merge_strategy>` and the `## <sec:cv_review_and_merge>` section. If the file does not exist, STOP — they should return to phase `00`.

1.b **Topology check (L13-D1) — here it is a QUESTION, not an error.** If the `PR submission` field is `no`, the project works without PRs. This is **not a policy violation**: a superfluous PR is harmless and revocable (the two directions are not symmetric). Ask, and wait for the answer:
   <!-- INCLUDE:lang/09-merge.md#L13-D1-pr-felesleges -->
   If the user chooses `bs-review-and-merge`, redirect there and stop.

2. **Working tree check:** `git status --short`. With uncommitted changes, list them and ask in one round whether I should commit now or continue — wait for the answer. We do **not** switch branches here: we stay on the own branch of the cycle, that is what we push.

3. **Status gate:** the status of `tasks.md` / `plan.md` / `spec.md` is `<status:done>`, and there is **no `[validate-loop]` marker** on `tasks.md`. If any of these does not hold, return to phase `07`.

4. **Review gate (RV1):** `test-report/code-review.md` exists and contains no unresolved `- [ ]` in the `<sec:critical_fixes>` section. If this is not so, **STOP**, back to `07` — the description of the PR is built from this file, and a PR opened with an open Must Fix discredits the review.

5. **Doc-sync gate:** `doc-sync-plan.md` exists, has no unfinished `[ ]` item, there is no open `doc-sync-questions.md` question, and the DS22 gate was green. If not, back to `08`.

---

## Your task

1. **Pre-merge doc-sync check** (DS23.2) — has code changed since `08`.
2. **Integration update:** bringing the main branch into the cycle branch (W2) — so that we do not open the PR on an obsolete base.
3. **Pushing the cycle branch and opening the PR.**
4. **Updating the generated `cycle-status.md`** with the PR link, and handing over to `bs-review`.

> **🔴 The `VP2` test round does NOT run here.** On this path the post-merge verification happens in the **`bs-merge`** phase, **before** the code reaches the main branch (L13-D6/L13-D14). Here only the PR is opened.

In this phase there is **no self-healing loop and no subagent**.

---

## 1. Pre-merge doc-sync check (DS23.2)

1. **Has code changed since the closing commit of `08-doc-sync`?**
   ```bash
   BASE=$(git log --format=%H -1 --grep="^cycle-NN: 08-doc-sync")
   git diff --name-only "$BASE" HEAD
   ```
   - If **no** (an empty list, or only paths under `specs/`), there is nothing to do.
   - If **yes**, restart `08-doc-sync` on the final code: `/bs-doc-sync input: @specs/cycle-NN-<cycle-name>`
2. Continue only after a green DS22 gate.

---

## 2. Integration update (W2)

```bash
git fetch origin
git log --oneline HEAD..origin/main
```

_In place of `main` comes the **<field:f_main_branch>** field of the `## <sec:cv_git_conventions>` section of `conventions.md`. There is **deliberately no `$( )` substitution** in the command (allowlistability)._

- **An empty list** → continue with opening the PR.
- **A non-empty list** → bring the main branch into the cycle branch (`git rebase origin/main` if the branch is not pushed yet; `git merge origin/main` if it already is), then look at what came in (`git diff --name-only "$PRE" HEAD`):
  - **source code or a test changed** → the `VP2` round of `bs-merge` will run on it anyway; if the change brought in touches the scope of the cycle, **STOP**, back to `07`.
  - **only `docs-generated/` / `conventions.md` / `specs/test-conventions.md`** → **STOP**, back to `08`.
  - **only the `specs/cycle-MM-*/` folders of other cycles** → nothing to do.

On a conflict the *Handling a merge conflict* rules of `bs-review-and-merge` apply: do not invent the resolution, and in an ambiguous case STOP + ask.

---

## 3. Opening the PR

1. **Pushing the branch:**
   ```bash
   git push -u origin feature/cycle-NN-<cycle-name>
   ```
2. **Creating the PR** according to the provider and the target branch of the `## <sec:cv_merge_strategy>` section of `conventions.md`. Let the PR description be the content of `code-review.md`:
   - **GitHub:** `gh pr create --base <target> --head feature/cycle-NN-<cycle-name> --title "cycle-NN: <title>" --body-file specs/cycle-NN-<cycle-name>/test-report/code-review.md`
   - **GitLab:** `glab mr create --target-branch <target> --title "cycle-NN: <title>" --description "$(cat specs/cycle-NN-<cycle-name>/test-report/code-review.md)"`
   - **Bitbucket:** according to the access command of `conventions.md`, over the REST API or the CLI.
3. **Do NOT merge the PR**, and do **not** switch to the main branch — the merge is the job of `bs-merge`, and accepting the PR is a human decision (`L13-D5`).

> **A non-interactive (CI) run:** if the skill would want to ask something in this mode (a missing target branch, an ambiguous provider configuration), **the question = STOP**: write the question into `specs/cycle-NN-<cycle-name>/create-pr-questions.md`, send a notification (`notify.py`), and the adapter returns with `exit 2`. Do not invent an answer.

---

## 4. Closing and handover

1. **Generated cycle status** (L13-D9) — together with the PR link:
   <!-- INCLUDE:shared/python-cmd.md -->
   ```bash
   python3 <platform-scripts-mappa>/cycle-status.py specs/cycle-NN-<cycle-name> --write
   ```
   `cycle-status.md` is a **generated file**: a rendering of the evidence, never a source. Commit it onto the cycle branch and push it (`git push`).
2. Do **NOT** close the roadmap yet: the cycle is done when the last enabled verification is green (L13-D8) — that is still ahead. The cycle row of the roadmap gets the `<status:waiting_for_verification>` mark.
3. Give the user the PR link and the next step:

<!-- INCLUDE:lang/09-merge.md#zaro-uzenet-create-pr -->
