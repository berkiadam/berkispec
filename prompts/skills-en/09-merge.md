---
phase: 09
name: bs-merge
description: "berkispec - 09. Use as the last step of the cycle (Phase 09), when the code, the review and the documentation are all 'Done'. Merging the cycle branch according to the merge strategy in 'conventions.md' (opening a PR or a local merge), with mandatory user confirmation."
prerequisites:
  - "specs/cycle-NN-<name>/tasks.md status: <status:done>"
  - "specs/cycle-NN-<name>/plan.md status: <status:done>"
  - "specs/cycle-NN-<name>/spec.md status: <status:done>"
  - "specs/cycle-NN-<name>/test-report/code-review.md — no unresolved Must Fix (the 07 review gate)"
output:
  - "Merged cycle branch (local or PR, according to the Merge strategy in conventions.md)"
  - "specs/roadmap.md — the cycle marked as closed"
prev: bs-doc-sync
next: bs-write-spec
---
# 09 — Merge
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

We develop software in Spec Driven Development. Development is broken down into cycles. Each cycle is an independently developable, independently testable subunit of the full implementation.

This is **phase 9 (0–9)** of the process: 0-init · 1-cycles · 2-spec · 3-plan · 4-tasks · 5-analyze · 6-implement · 7-validate (tests + review) · 8-doc-sync · **9-merge ←**.

> **Code review is NOT part of this phase (RV1).** The `reviewer` subagent and the review self-fixing loop moved to the **`07-validate`** phase: there the review is the 2nd step of the full round (the static layer's half, alongside Sonar), and findings run into the same loop, the same stop limits, as test failures. By the time you get here, the review is already clean — this phase is **exclusively about merging**.

---

## <field:f_prerequisite>

0. **Cycle identification:** if the user specified a cycle/file, use it; otherwise propose the most recent `specs/cycle-*` folder for confirmation — <!-- INCLUDE:lang/common.md#ciklus-beazonositas --> — and wait for the reply before proceeding.

1. **`conventions.md` existence check:** read the `conventions.md` in the project root (especially the `## <sec:cv_merge_strategy>` section). If it does not exist, STOP — go back to phase `00`.

2. **Working tree check (VCS only):** run `git status --short`. If there are uncommitted changes, list them, and ask in one round whether to commit now or continue — wait for the reply. You are working on the cycle's **own feature branch**; switching to the main branch happens later in the Merge step, after user confirmation (RD8) — do not switch here. (Skipped in a no-VCS project.)

2.b **Worktree situation (W1 — VCS only):** `09` switches to the main branch, so **it must run in the worktree that contains `main`**. Check:

   ```bash
   git worktree list
   git rev-parse --git-common-dir     # if not `.git`, we are in a linked worktree
   ```

   - **Single worktree** → nothing to do, the Merge step below is fine as is.
   - **We are in a linked worktree** (a leftover cycle worktree from a parallel planning window) → **STOP.** `git switch main` will be refused here ("already used by worktree"). The `06`–`09` segment runs in the **main** worktree: the cycle must be moved back there (`git worktree remove ../<cycle-worktree>`, then in the main worktree `git switch feature/cycle-NN-<cycle-name>`), and continue from there. Commit any uncommitted content first — do **not** use `--force`.
   - **There is ANOTHER worktree on a `cycle-*` branch** → that is a cycle being planned in parallel. This does **not** block the merge (the other cycle is up to `05`), but after the merge, notify: the other cycle must pull in the fresh `main` before `06` and re-run `05` (PW2).

3. **Status gate:** if the validate phase (07) PASSes, it sets all three files' status to `<status:done>`. Check:
   - `tasks.md` status: `<status:done>` — and **no `[validate-loop]` marker on it** (the marker indicates a stuck loop)
   - `plan.md` status: `<status:done>`
   - `spec.md` status: `<status:done>`

   If any of them is not `<status:done>` (e.g. still `<status:ready_for_validate>` or reset to `<status:draft>`), validation has not yet completed successfully — go back to phase `07`.

4. **Review gate (RV1):** `specs/cycle-NN-<name>/test-report/code-review.md` must exist, and it **must not have an unresolved `- [ ]` in the `<sec:critical_fixes>` section**. If it is missing or there is an open `<status:must_fix>`, the 07 review gate has not closed — **STOP**, go back to phase `07`. **Do not merge without review**, and do not run the review "quickly" here: that is the job of `07`, with its own fixing loop and stop limits.

5. **Doc-sync gate:** the `08-doc-sync` phase must have run on the validated code. Check that the cycle's `doc-sync-plan.md` exists, has no incomplete `[ ]` item, has no open `doc-sync-questions.md` question, and the DS22 gate was green. If this is not the case, go back to phase `08-doc-sync`.

---

## Your task

1. **Pre-merge doc-sync check:** if code has changed since the `08-doc-sync` closure, re-run doc-sync on the final code, and only continue after a green DS22 gate.
1.b **Integration update (W2):** if the main branch has moved forward since the cycle branch was created, bring it in (rebase or merge), and depending on the nature of the change route back to `07` or `08` — never merge an untested combination.
2. **Perform the merge** according to the Merge strategy in `conventions.md` (local squash or PR), **only after mandatory user confirmation** (RD8) — the merge is never automatic.
3. **Close the roadmap** and provide the starting prompt for the next cycle.

In this phase there is **no self-fixing loop and no subagent**: if any of the pre-merge checks fail, the correct step is to route back to `07` or `08`, not to fix it in place.

---

## 1. Pre-merge doc-sync check (DS23.2)

The `08-doc-sync` gate and the `07` review gate are **independent gates**. The reviewer only produces code findings (`test-report/code-review.md`); the correctness of the generated documentation is ensured by `08-doc-sync`'s own DS22 gate.

Normally the `07 → 08 → 09` order already yields consistent docs: the review closed in 07, so 08 already documented the **final** code. Before the merge, still check:

1. **Has any code changed since the `08-doc-sync` closing commit?**
   ```bash
   BASE=$(git log --format=%H -1 --grep="^cycle-NN: 08-doc-sync")
   git diff --name-only "$BASE" HEAD
   ```
   - If **not** (empty list, or only paths under `specs/`), nothing to do.
   - If **yes**, re-run `08-doc-sync` on the final code:
     ```text
     /bs-doc-sync input: @specs/cycle-NN-<cycle-name>
     ```
2. Wait until `08-doc-sync`'s DS22 gate is green, there is no open `doc-sync-questions.md` question, and every item of `doc-sync-plan.md` is checked off.
3. After doc-sync has run, come back here, and only then ask for merge confirmation.

**It is forbidden** here to produce any code finding, or to turn doc-sync into a review: code → the `07` review gate; docs → `doc-sync-plan.md` / `doc-sync-questions.md` + DS22 gate.

---

## 1.b Integration update — has the main branch moved forward? (W2)

The green tests of `07` and the docs of `08` were built **on the base** from which the cycle branch diverged. If the main branch has moved forward in the meantime (another cycle merged, a hotfix arrived), then the merge would create a **combination that was never tested**. So before the merge confirmation:

```bash
git fetch origin
git log --oneline $(git merge-base HEAD origin/main)..origin/main
```

_In a repo without a remote (local only), work with the local `main` instead of `origin/main`, without `git fetch`. `main` is replaced by the `conventions.md` `## <sec:cv_git_conventions>` **<field:f_main_branch>** field._

- **Empty list** → the cycle branch is at the top of the main branch, continue with the Merge step. _(Cross-check: does the `analyze-report.md` **`<field:f_validated_base>`** field's main branch SHA also show this — if not, `05` closed on an older base, and the re-validation rule below applies.)_
- **Not empty** → the main branch must be brought into the cycle branch, **and then re-validated**:

1. **Bringing it in** (same mechanics as `05`'s BR1 step). The choice is not a matter of taste:
   - if the branch is **not pushed / has no PR** (`git rev-parse --verify origin/feature/cycle-NN-<cycle-name>` errors) → `git rebase origin/main` (linear history; the `cycle-NN: <phase>` commit messages are preserved, so `git log --grep`-based searches keep working),
   - if the branch **is pushed or has a PR open** → `git merge origin/main` into the cycle branch (rebase would require a force-push on a branch under review).
   - In case of conflict, the rules of *Handling merge conflicts* below apply — **do not** resolve the generated docs (`docs-generated/`) and `specs/test-conventions.md` by hand: those are restored by re-running `08`.
2. **Re-validation according to the merged-in base.** BEFORE bringing it in, note the tip of the cycle branch (`PRE=$(git rev-parse HEAD)`), then afterward check what came in: `git diff --name-only "$PRE" HEAD`. Depending on the nature of the hits:
   - **source code or tests changed** → **STOP**, go back to `07` (tests + review on the fresh base). Return here after `07` PASSes.
   - **only `docs-generated/`, `conventions.md` or `specs/test-conventions.md` changed** → **STOP**, go back to `08` (regenerate the generated docs). Return here after a green DS22 gate.
   - **only other cycles' `specs/cycle-MM-*/` folders changed** → nothing to do, continue with the Merge step.
3. Only after this, ask for merge confirmation.

**Do not ask for separate permission to bring it in** (you are working on the cycle's own branch, this is not destructive) — but **always announce** the `07`/`08` routing back, because that is a phase change.

---

## 2. Merge — according to the Merge strategy in conventions.md

Read the `## <sec:cv_merge_strategy>` section of `conventions.md`, and proceed according to the **<field:f_provider>** field. **On either branch, user confirmation is MANDATORY before the merge** — merging into `master` and deleting the branch is destructive, and cannot be carried out without confirmation. `07` PASSing (green tests + clean review) is automatic; the merge, however, is **still closed off by manual confirmation** (RD8).

### Confirmation (mandatory on both branches)

Ask, and **wait for explicit confirmation**:
<!-- INCLUDE:lang/09-merge.md#RD8-merge-megerosites -->
> **At the end of the reply, place a direct, clickable link to `test-report/validation-report.md` and `test-report/code-review.md`.**

Do not proceed before confirmation.

### A) Local (no PR)

After confirmation:
```bash
# 1. Switch to the main branch (the conventions.md `## <sec:cv_git_conventions>`
#    <field:f_main_branch> field, or the `## <sec:cv_merge_strategy>` PR target — `main` by default)
git switch main

# 2. Squash merge from the cycle branch
git merge --squash feature/cycle-NN-<cycle-name>

# 3. Commit with the cycle's title and the plan's objective
git commit -m "cycle-NN: 09-merge - <title>" -m "<goal and approach from plan.md>"

# 4. Delete the local cycle branch
git branch -D feature/cycle-NN-<cycle-name>
```

> **W3 — if the cycle branch is still checked out in a worktree**, `git branch -D` will refuse ("used by worktree"). In that case first `git worktree remove <path>` (if there is uncommitted content, commit it first, without `--force`), and only then delete the branch. An abandoned entry is cleaned up by `git worktree prune`.

### B) GitHub / Bitbucket / GitLab (PR)

After confirmation, create the PR with the provider given in `conventions.md`, against the target branch from `conventions.md`. The PR description should be the content of `code-review.md`:
- **GitHub:** `gh pr create --base <target> --head feature/cycle-NN-<cycle-name> --title "cycle-NN: <title>" --body-file specs/cycle-NN-<cycle-name>/test-report/code-review.md`
- **GitLab:** `glab mr create --target-branch <target> --title "cycle-NN: <title>" --description "$(cat specs/cycle-NN-<cycle-name>/test-report/code-review.md)"`
- **Bitbucket:** according to the access command in `conventions.md`, via REST API or CLI.

On a PR-based branch, **do not** delete the branch locally and **do not** merge into `master` directly — the merge happens on the provider after review/CI.

### Handling merge conflicts

If a merge conflict occurs during the merge:
1. **Do NOT guess the resolution.** List the conflicting files (`git status`).
2. For each conflicting file, look at both sides (the `master` and the cycle branch version), and decide based on `plan.md` / `spec.md` which one is correct — or whether the two need to be merged together.
3. If the resolution is unambiguous given the cycle's intent, resolve it, re-run the relevant check, then commit.
4. **If the resolution is not unambiguous** (both sides contain substantive, conflicting logic), STOP — notify the user of the conflicting files and the two sides, and ask for a decision.

---

## Roadmap status update

After the merge, update `specs/roadmap.md`: mark the given cycle as closed (e.g. with a `✅` or `(done)` marker next to the cycle's title), so the roadmap reflects the cycle's completion. Commit the roadmap update (on a PR branch it can be part of the PR, on a local branch a separate commit).

---

## Status handling

If the merge (or PR creation) succeeded, notify the user of the cycle's closure and the starting prompt for the next cycle:

<!-- INCLUDE:lang/09-merge.md#zaro-uzenet -->
