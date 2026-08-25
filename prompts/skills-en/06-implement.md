---
phase: 06
name: bs-implement
description: "berkispec - 06. Use when analyze-report.md is 'PASS' (Phase 06), for the actual code development. Executes the planned code changes based on the task list, and meanwhile maintains 'tasks.md' until it reaches the 'Ready for validation' state."
prerequisites:
  - "specs/cycle-NN-<name>/tasks.md status: <status:ready_for_implement>"
  - "specs/cycle-NN-<name>/analyze-report.md status: PASS"
output:
  - "Implemented code"
  - "specs/cycle-NN-<name>/test-report/implement/check-log.md — the append-only log of [CHECK] runs (TR5)"
  - "specs/cycle-NN-<name>/tasks.md status: <status:ready_for_validate>"
prev: bs-analyze
next: bs-validate
subagents:
  - "agents/researcher.md"
shared:
  - "shared/parallel-cycles.md"
---
# 06 — Implementation
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

We develop software in spec driven development. Development is broken into cycles. Each cycle is an independently developable, independently testable subunit of the full implementation.

This is **phase 6 (0–9)** of the process: 0-init · 1-cycles · 2-spec · 3-plan · 4-tasks · 5-analyze · **6-implement ←** · 7-validate · 8-doc-sync · 9-review.

---

## <field:f_prerequisite>

0. **Cycle identification:** if the user specified a cycle/file, use it; otherwise offer the most recent `specs/cycle-*` folder for confirmation — <!-- INCLUDE:lang/common.md#ciklus-beazonositas --> — and wait for the response before proceeding.

1. Read the `tasks.md` status. **If the status is not `<status:ready_for_implement>`, do not start implementing.** Inform the user that the task list has not yet been finalized.

2. **Working tree check (VCS only):** run: `git status --short`. If there are uncommitted changes:
   - List the affected files.
   - State: <!-- INCLUDE:lang/06-implement.md#commit-javaslat -->
   - Ask: <!-- INCLUDE:lang/06-implement.md#commit-kerdes --> — If yes: commit the changes, then continue. If no: continue without committing. (Omitted in a no-VCS project.)

3. **🔴 Parallel-cycle gate (PW1/PW2 — VCS only):** `06` is the first phase that writes to the **source tree**, so the implementation lane is **single-threaded**. Planning can happen in parallel across several cycles (separate worktrees), implementation cannot. Run:

   ```bash
   git worktree list
   git rev-parse --git-common-dir
   git fetch origin && git log --oneline $(git merge-base HEAD origin/main)..origin/main
   ```

   _In a repo without a remote (local only), work with the local `main` instead of `origin/main`, without `git fetch`._

   - **If there is another worktree on a `cycle-*` branch** → **STOP.** Another cycle is still open: either it must be carried through to `09`, or this cycle must wait its turn. Do not start implementing, and do not suggest a `--force` workaround.
   - **If we are in a linked worktree** (`git rev-parse --git-common-dir` is not `.git`) → **STOP.** `06`–`09` run in the **main** worktree (that is where `main` lives, which `09` needs). See the PW2/3 steps in the *Parallel cycles* block for how to move back.
   - **If `main` has moved forward** since the cycle branch diverged (the `git log` output is not empty), **or** if the main branch SHA in the `analyze-report.md` **`<field:f_validated_base>`** field does not match the current one (`git rev-parse origin/main`) → **STOP.** The `analyze-report.md` `PASS` was produced on the **old** base. Re-run `05-analyze` (`/bs-analyze input: @specs/cycle-NN-<cycle-name>`) — it will pull in the fresh main branch (BR1) and validate against it. Return here after `PASS`; do not rebase yourself.
   - **Otherwise** (single worktree, fresh base) → continue.

<!-- INCLUDE:shared/parallel-cycles.md -->

---

## Your task

Implement the tasks in `tasks.md` in order, one by one.

**Follow the project's existing code conventions** — naming, structure, test organization can be derived from the source code. If `conventions.md` exists at the project root, read that too.

**Resuming after an interrupted run:** implementation can be interrupted at any time — even in the middle of the first task, before anything was checked off. Always verify the actual state of the code, not just the markings.

**Two sources can send us back here — both from the 07-validate FAIL branch:** (a) test/Sonar/DoD failure (`## <sec:validation_fixes>` tasks at the end of `tasks.md`), or (b) a code review finding (`## <sec:review_fixes>` tasks + `test-report/code-review.md`). In both cases, the new tasks at the end of `tasks.md` are the ones to perform; on the review branch, also read `test-report/code-review.md` (see the Context loading rules and item 2 of the Execution rules). The decision tree below applies the same way — start from the actual state of the code.

Decision tree for resuming — **in this order**:

```
1. Is there a task marked [x]?
   → Read the source files it touches, and verify that the changes are actually in place.
   → If the code CONTRADICTS the [x] marking: do NOT unmark anything.
     State: "Task [Tkkk] is marked [x], but based on the code it looks like [X] is not done. How should we proceed?"
     Wait for the response.

2. Is there a partially done [ ] task (something already exists in the affected files)?
   → Continue from where it was left off. Do not start from scratch.

3. Is nothing started at all?
   → Start implementation with the first [ ] task.
```

---

## Context loading rules

- Before starting implementation, read `tasks.md`, then the **Prerequisite documents** listed within it. These contain the function signatures, interfaces, and error-handling logic.
- **Review feedback:** If `tasks.md` contains fix tasks originating from a review (the 07 review gate found `<status:must_fix>`), also read `specs/cycle-NN-<cycle-name>/test-report/code-review.md` to understand the context and expectations of the fixes.
- For each task, read **only the source files named in that task** — and only the relevant parts of them. The task's logical context lives in the Prerequisite documents.
- Do not read the spec.
- **Source localization**: if the task names a component or function but the exact file/line is unknown — call the `researcher` subagent (`agents/researcher.md`, Mode B) for the search. The subagent returns the path and the relevant lines, not the entire file.
- **Large file**: if the affected file is large and only one section is relevant — call the `researcher` subagent (`agents/researcher.md`, Mode B) for extraction. Do not load the entire file into the main context.
- For small, known files: read directly.

---

## Design principles

**Deep module — not shallow module:** When writing a new function or module, aim to hide a lot of logic behind a simple interface. The caller should not need to know the internal details. If a new function does a single line of work but expects a complex parameter, rethink it — you are probably pushing the complexity onto the caller side.

**Code comments:** Every function should have a one-line header comment describing what it does. Add a short, one-line explanation for non-trivial logic, external API calls, and decision points — at a level that a developer coming from a different programming language would understand the intent. Trivial lines (e.g. `return result`, a simple getter) do not need a comment.
- **Keeping comments and docstrings up to date:** If you modify or rename an existing piece of code, a function, a variable, or an endpoint, the associated explanatory code comments, JSDoc/TSDoc docstrings, and type annotations **must also be updated** to match the new names and behavior. Stale comments must not remain in the code.

---

## Execution rules

> **Continuity — NO stopping between tasks (IM1).** This phase processes the task list **in one run**: closing a task (checkbox + `check-log` entry + commit) is **not** the end of the phase, and is **not** the end of your response. Immediately after the commit, **take up the next unfinished task in the same turn** — do not hand the floor back to the user, do not ask whether you may continue.
>
> **The exhaustive list of stopping conditions** — only these halt the phase:
> 1. a *Stopping rule* has been met (see the section);
> 2. the section's `> **Machine prerequisite:**` block is not satisfied (item 3);
> 3. the task appears to be infrastructure-dependent and must be asked about (item 4);
> 4. the `[CHECK]` has failed three times (3-attempt rule, item 8);
> 5. **every** task is `[x]`, and the closing message of *Status handling* follows.
>
> Anything else — including "the task is done and committed" — is **continuation**, not a stop. The one-line progress notice (item 13) belongs in the **middle** of your response, not at the end.
>
> _Note on the framework's convention:_ the sentence "**Place the clickable link to … at the end of the response**" is a **stop signal** in the other phases (a question or end of phase). That is why in this phase it **deliberately does not appear per task** — the link to `tasks.md` belongs in the phase's closing message.

1. Take the next unfinished task (`- [ ]`).

2. **Returning from code review (07):** If the cycle came back here because of `<status:must_fix>` findings from the 07 review gate, carry out the new tasks at the end of `tasks.md` based on the critical findings in `test-report/code-review.md`. After the fixes, re-running and committing the closing `[CHECK]` tasks is mandatory.

3. **Section-level prerequisite check:** In `tasks.md`, sections are organized into `##`-level blocks. (If a task does not fall under any `##` block — e.g. it sits at the top of the list without a section heading — treat it as a standalone task with no prerequisite, and continue with item 4.) If the selected task is the first unfinished task in its section (that `##` block) (i.e. within the section it is the first `- [ ]`): find the section heading in `tasks.md`, and check whether a `> **Machine prerequisite:**` block sits directly below it. If there is one: read the conditions and decide whether they are met. If they are not met: stop, and tell the user exactly what needs to be set up: *"To begin the [section name] section, the following conditions must be met: [conditions]. Are these met?"* — wait for the response before starting a single task from that section.

4. **Before starting: decide whether the task can be done now.** A task may be deferred if it requires a fully running stack (containers, a real Keycloak, E2E infrastructure), or if all the other tasks in the group are also unfinished and are all of a similar nature. If the task looks deferred, do not attempt to execute it — ask: *"[Tkkk] looks like an infrastructure-dependent task (e.g. E2E, container, real Keycloak). Is the stack running, or should I look for the next task that can be implemented?"*
   > **Narrow gate (IM1):** this question **stops the phase**, so only ask it if the task text **explicitly** requires a running stack / external infrastructure (container, deploy, real IdP, browser E2E), **and** you cannot verify its availability yourself (e.g. via a health-check command). For coding, test-writing, configuration, and `[CHECK]`-command tasks, **do not ask — do it**. If you can verify it (health check), **verify first**, and ask only if it fails.

5. Read the files affected by the task.

6. Implement exactly what the task describes — no more, no less.

7. Do not refactor untouched code. Do not add unrequested features.

8. **Executing a `[CHECK]` task:**
   - Run the specified command.
   - If it reports an error, fix the preceding tasks within the group, then re-run it.
   - The group may only be marked done (`- [x]`) after a green `[CHECK]` — close out `[RED]`/`[GREEN]` tasks only at that point too.
   - **🔴 Log it in `check-log.md` (TR5) — every attempt, including the failed ones.** The command's output lives in the chat, and the chat is gone after `/clear`; without this, all that remains from the phase is a checkbox that claims green, without proving it. See the *`[CHECK]` run log* section.
   - **3-attempt rule:** If `[CHECK]` has failed three times in a row, and fix attempts within the group have not resolved it — **stop**. Describe what you tried, and tell the user: *"[Tkkk] failed three times. [Short summary of the error and the solutions attempted.] How should we proceed?"*
   - **Port conflict:** If starting a service or running a test fails due to a port conflict (address already in use), do not stop. Find the next free port (`ss -tlnp | grep :<port>` or `lsof -i :<port>`), temporarily update the affected configuration (`docker-compose`, env file), and re-run. Tell the user which port you used instead.
     > **⚠ TEMPORARY CHANGE — DO NOT COMMIT:** the config/port change made for the port conflict is temporary. Before committing the task, RESTORE it, or exclude it from `git add` (it must not end up in the cycle's diff). Only the task's actual code change may be committed.

9. **`⟂ Tkkk` marking:** the given task and the referenced task are independent of each other — if they can be done at the same time, invoke both edits in parallel.
   - **Example:** if T012 contains `⟂ T013`, then T012 and T013 can be edited at the same time.
   - **Exception:** if both tasks touch the same file, run them sequentially.

10. **Cleaning up temporary resources**: If you created temporary files or started containers while executing the task, delete the files and stop/remove the containers after the task (or `[CHECK]`) finishes. Do not leave leftovers behind for the next task.

11. **Mark it done in `tasks.md`:** set the task's checkbox to `- [x]`. **This `tasks.md` change is also part of the commit** — the code and the workflow state must not drift apart.

12. **Git commit:** After the task is successfully completed and the group-closing `[CHECK]` (or the task's own check, if there is no group) is green, commit the change **together with the affected source files, `tasks.md`, AND `check-log.md`**:
    ```bash
    git add <affected files> \
            specs/cycle-NN-<cycle-name>/tasks.md \
            specs/cycle-NN-<cycle-name>/test-report/implement/check-log.md \
      && git commit -m "cycle-NN: Tkkk - <task description>"
    ```
    where `NN` is the cycle number (e.g. `16`), `Tkkk` is the task ID (e.g. `T001`), and the description is a condensed version of the task text.
    **Example:** `cycle-16: T001 - add initHash function to token-store`
    Commit the `[RED]` and `[GREEN]` states separately as well.

13. **Progress notice, then IMMEDIATELY continue.** Write **one short line** about which task was completed (e.g. `T004 done — token-store initHash + unit test green (commit a1b2c3d)`), and **in the same turn** continue from item 1 with the next unfinished task. This line is a **progress log, not a closing response**: do not append a link, a summary, or "may I continue?" (see the *Continuity* rule, IM1).

---

## Stopping rules

If any of the following is met while implementing, **STOP — stop and inform the user** (do not drift onward, do not try to "creatively" push forward):

- The task description contradicts the existing code and the correct solution is not clear.
- Completing the task would require modifying a file that is not named in the task description.
- A task assumes the result of an earlier task, but that one is not yet done.
- **A `[CHECK]` task has failed three times in a row** (see rule 8).

In every case, ask only **one** question, wait for the response, then continue.

---

## `[CHECK]` run log (TR5) — `test-report/implement/check-log.md`

> **Why it's needed:** the output of `[CHECK]` commands lives in the chat, and the chat is gone after `/clear`. Without this, all that remains from the implementation phase is a `- [x]` checkbox and a commit message — both *claim* it was green, but neither proves it. 07-validate demands proof (TR1/TR2) and report artifacts (TR3) for the same reason; in 06, this log is the cheap, text-based counterpart of that.

**Where:** `specs/cycle-NN-<cycle-name>/test-report/implement/check-log.md`. If the folder does not exist, create it. Do **not** touch the `test-report/validate/` and `test-report/review/` subfolders — those are the evidence of 07 and 09.

**When to write to it:** **after every `[CHECK]` run, including the failed ones** — not just after the eventual green attempt. The log is **append-only**: you never rewrite or delete an earlier line.

**What you do NOT do:** you do not generate an HTML/Allure/coverage report. That is 07's job — 07's first FULL round measures 06's closing state anyway, and two report sets about the same thing is a needless duplication in the git diff.

### File template

```md
<!-- INCLUDE:lang/06-implement.md#check-log-sablon -->
```

**Columns:**
- **Time** — a concrete string (`YYYY-MM-DD HH:MM`). Shell substitution is platform-dependent: bash/zsh → `$(date '+%Y-%m-%d %H:%M')`, PowerShell → `(Get-Date -Format 'yyyy-MM-dd HH:mm')`. If you cannot determine it, `—` is acceptable too; the other columns are what matters.
- **Attempt** — which attempt out of the 3-attempt rule (item 8): `1/3`, `2/3`, `3/3`. This is what makes it visible in hindsight that a group was hard to get through.
- **<field:f_mode>** — `normal` \| `validate-loop` (07's self-healing loop — both test fixes and review fixes). `[CHECK]` runs executed in fix mode are **logged the same way**, with the appropriate marker — so the fix rounds leave a trace too.
- **Command** — the command that was actually issued, **verbatim**, not the idealized version from the task text.
- **Result** — `✓`/`✗` + the runner's counts (`X passed / Y failed / Z skipped`), and on failure, the name(s) of the failed test(s) with a short error message. **If the command is not a test** (build, lint, typecheck), put one line of the essential output in place of the count (e.g. `0 errors`).

**<sec:notes> section** — this is where any circumstance that affected the run but does not fit the table goes: a temporary port swap (and whether it was reverted — the port-conflict rule in item 8), a manually started/stopped container, a skipped check and its reason.

---

## Documenting problem-solving

If, while completing a task, you succeed in solving the problem only after at least 3 failed attempts, create or extend the `specs/cycle-NN-<cycle-name>/imp-decision.md` file:

```md
<!-- INCLUDE:lang/06-implement.md#check-log-pelda-sor -->
```

If the file already exists, append to it — do not overwrite earlier entries.

---

## New component README

_(Reminder of the 03-plan `README.md` requirement — here is where the execution happens, not a new requirement.)_ If a task creates a new component (new application, new service, new standalone module), a `README.md` file must be created in the component's root folder. Its content:

- **What it does** — one or two sentences about the component's responsibility
- **<field:f_startup>** — the concrete command(s) for running it locally
- **Port** — which port it listens on
- **Debug** — if meaningful: how to debug it, what debug port it uses
- **Logs** — what events it logs, what log levels exist
- **Connections** — which other components it depends on, what it calls, what calls it

The README.md is part of the implementation — not after-the-fact documentation. It must be finished when the component is done.

---


## Status handling

- While implementing: `<status:implement_in_progress>`
- If every task is `[x]`: update the `tasks.md` status to `<status:ready_for_validate>`, and **commit this state change** (the final status must be recorded separately) — together with the last entries of `check-log.md`:
  ```bash
  git add specs/cycle-NN-<cycle-name>/tasks.md \
          specs/cycle-NN-<cycle-name>/test-report/implement/check-log.md \
    && git commit -m "cycle-NN: 06-implement - done, ready for validation"
  ```
  **Check before the status change:** `check-log.md` exists, and every group-closing `[CHECK]` has at least one line for it in the log. If a group is `[x]` but the log has no entry for it, the evidence is missing — add the missing log line based on the actual run (not from memory: if you do not know, re-run the `[CHECK]`).

If the status is `<status:ready_for_validate>`, stop. Inform the user of the next step and the phase's launch command, for example:
<!-- INCLUDE:lang/06-implement.md#zaro-uzenet -->
> **Place the direct, clickable link to `tasks.md` and `check-log.md` at the end of the response** — this is the phase's single stop signal (IM1).


> **Phase boundary — hard stop (PE1).** The phase **ends** with the closing message (commit ID + `/clear` + the next phase's command). In the same turn, you do **not** start anything from the next phase — you do not even create the next phase's artifact. This holds even if a **context summary / checkpoint** to-do list, your own earlier plan, or a "let's go through the whole process" remark from the user in an earlier turn encourages moving on: the skill's phase boundary outranks all of that. Only an **explicit request from the user for this turn** overrides it. If you nonetheless started it, **delete the resulting file**, restore a clean working tree, and report it.

---

<!-- INCLUDE:shared/fix-mode-implement.md -->
