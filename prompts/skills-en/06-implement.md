---
phase: 06
name: bs-implement
description: "berkispec - 06. Use when analyze-report.md is 'PASS' (Phase 06), for the actual code development. Executes the planned code changes based on the task list, and meanwhile maintains 'tasks.md' until it reaches the 'Ready for validation' state."
prerequisites:
  - "specs/cycle-NN-<name>/tasks.md status: <status:ready_for_implement>"
  - "specs/cycle-NN-<name>/analyze/analyze-report.md status: PASS"
output:
  - "Implemented code"
  - "specs/cycle-NN-<name>/test-report/implement/check-log.md — the append-only log of [CHECK] runs (TR5)"
  - "specs/cycle-NN-<name>/tasks.md status: <status:ready_for_validate>"
prev: bs-analyze
next: bs-validate
subagents:
  - "agents/researcher.md"
scripts:
  - "scripts/test-substance-check.py — the vacuous test-body gate (TB1)"
  - "scripts/report-gate-check.py — the report-phase gate (TR6)"
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
   git fetch origin && git log --oneline HEAD..origin/main
   ```

   _In a repo without a remote (local only), work with the local `main` instead of `origin/main`, without `git fetch`._

   _The command **deliberately contains no `$( )` substitution**: `HEAD..origin/main` yields the same commit set as the `merge-base` form, but several CLIs (e.g. Antigravity/Gemini) do not allow command substitution to be allowlisted for security reasons — such a line would ask for permission on every run._

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

> **🔴 A consistent state when you hand the floor back (IM2).** Before you hand the floor back for ANY reason — a question, a stopping rule, a quota, or simply the end of your response — the task currently in progress must be in a **closed** or an **explicitly suspended** state:
>
> - **closed** = `- [x]` in `tasks.md` **+** a `check-log` entry (if there was a `[CHECK]`) **+** a commit (item 12);
> - **suspended** = the checkbox stays `- [ ]`, but a line goes into `imp-decision.md` — *which task, how far it got, what the open question is, which files are modified without a commit* — and you state this in your response as well.
>
> **Leaving uncommitted, unbooked work behind is forbidden.** The interruption tolerance of this phase (and the evidence of `07`) is built on the per-task commit: without a tick and a commit the next session finds nothing but a dirty working tree, from which it cannot tell how far which task got, and what the user interrupted. **If you have to stop, book first, talk after.**
>
> This rule is **independent** of whether the stop was justified: even a justified question can only be asked from a consistent state.

> **🔴 A test task cannot be closed with an empty skeleton (RED1/TB1).** In this phase writing a test is **not** preparation for `07`: the test is finished here, with a full body. `assert True`, `pass`, a `TODO` comment or a body without an assertion are forbidden — and so is an assertion that merely compares the mock's own return value with itself. The body must contain a claim bound to the **response or the state of the system**.
>
> **"`07` will write it later" is not a branch.** `07` validates, it does not implement: an empty skeleton comes back from there as `X passed`, and every later piece of evidence in the chain (the DoD join, the report, the `PASS` verdict) is built on that false green.
>
> **`pytest.skip` / `it.skip` / `@Disabled` do not close out a task either (SK1).** A conditional skip (`if os.environ.get("RUN_REMOTE_E2E") != "true": pytest.skip(...)`) is just as empty a shell as `assert True` — it is only harder to notice, because it shows up as `skipped` rather than `failed` in the runner's output. It does not count in the evidence join of `07` either: `dod-check.py` does **not** accept a `skipped` case as `DoD-NN` evidence, and `validate-gate-check.py` **fails the round** if the data sheet of the plan refers to it as `TC-NN`. If the test can only run in a separate environment, the **condition has to be made satisfiable** (the switch belongs in the command of the machine run table of the plan), not the test silently skipped.
>
> **🔴 The marking of the test is not decoration (RL1/RL2).** If the `TS-NN` block of the plan is `[remote]`, the test has to carry the corresponding marking (`@pytest.mark.remote`, a Playwright `@remote` tag), and the REST logging fixture picks the folder **from that**: `<round folder>/<category>/rest-logs/<local|remote>/<test-name>/`. The test name is the name of the test function, normalized to be path-safe (`[^A-Za-z0-9._-]` → `-`, leading and trailing `-` trimmed; `test_foo[dsp01]` → `test_foo-dsp01`). **The classification is a property of the test AS A WHOLE:** if the test calls even a single component that does not run on the local machine, the whole test is `remote` — this is why the fixture moves things in the teardown, not per request. **We do not classify by the address called:** a `127.0.0.1` behind an `oc port-forward` is remote, while a compose service name is local. The gate of `07` looks at two things: whether the `remote/` folder really contains a non-local address (`RL1` — a remote folder left empty or containing only `127.0.0.1` is a **failure**, unless the address is declared as a port-forward in the `Environments and endpoints` table), and whether the test of every `[remote]` scenario produced a log at all (`RL2`).
>
> This is **not** advice but the precondition of the phase's two gates: a `[RED]` task requires failure evidence (item 8/b, `RED1`), and before the phase is closed the test-substance gate (`TB1`) reads through the test files listed in the `TA1` data sheets of the plan. An empty skeleton is not "we will fix it later" — it is an obstacle **now**.

1. Take the next unfinished task (`- [ ]`).

2. **Returning from code review (07):** If the cycle came back here because of `<status:must_fix>` findings from the 07 review gate, carry out the new tasks at the end of `tasks.md` based on the critical findings in `test-report/code-review.md`. After the fixes, re-running and committing the closing `[CHECK]` tasks is mandatory.

3. **Section-level prerequisite check:** In `tasks.md`, sections are organized into `##`-level blocks. (If a task does not fall under any `##` block — e.g. it sits at the top of the list without a section heading — treat it as a standalone task with no prerequisite, and continue with item 4.) If the selected task is the first unfinished task in its section (that `##` block) (i.e. within the section it is the first `- [ ]`): find the section heading in `tasks.md`, and check whether a `> **Machine prerequisite:**` block sits directly below it. If there is one: read the conditions and decide whether they are met. If they are not met: stop, and tell the user exactly what needs to be set up: *"To begin the [section name] section, the following conditions must be met: [conditions]. Are these met?"* — wait for the response before starting a single task from that section.

4. **Before starting: decide whether the task can be done now.** A task may be deferred if it requires a fully running stack (containers, a real Keycloak, E2E infrastructure), or if all the other tasks in the group are also unfinished and are all of a similar nature. If the task looks deferred, do not attempt to execute it — ask: *"[Tkkk] looks like an infrastructure-dependent task (e.g. E2E, container, real Keycloak). Is the stack running, or should I look for the next task that can be implemented?"*
   > **Narrow gate (IM1):** this question **stops the phase**, so only ask it if the task text **explicitly** requires a running stack / external infrastructure (container, deploy, real IdP, browser E2E), **and** you cannot verify its availability yourself (e.g. via a health-check command). For coding, test-writing, configuration, and `[CHECK]`-command tasks, **do not ask — do it**. If you can verify it (health check), **verify first**, and ask only if it fails.

5. Read the files affected by the task.

6. Implement exactly what the task describes — no more, no less.

7. Do not refactor untouched code. Do not add unrequested features.

8. **Executing a `[CHECK]` task:**
   - **🔴 Run the command VERBATIM, ON ITS OWN (CK1).** Issue the `[CHECK]` task's command **exactly** as the task writes it — together with the test selector (`::<function>`, `-t "<name>"`, `-k <pattern>`). It is **forbidden** to merge several `[CHECK]` commands into one run, to drop the selector ("I'll run the whole file, that covers it too"), or to carry the result of a broader run over to several tasks. One `[CHECK]` = one run = **one** log row with **one** task identifier.
     **Why:** the selector is the only thing that ties the task to the `plan.md` test case (`TC-NN`/`TS-NN`) — without it the checkbox is not a claim bound to an identifier (`TX1`). And, far more importantly: if the test's name **changed** during implementation, the filtered command **fails immediately**, whereas the merged run passes green. In a real cycle, instead of eight `[CHECK]` tasks a single run without a selector was logged, and three selectors referenced function names that no longer existed — so the drift between `tasks.md` and the code stayed completely invisible.
     **If the command errors out because the selector matches nothing** (`no tests ran`, `ERROR: not found`), that is **not** an execution failure to be worked around by merging runs: either the test was renamed (then the `tasks.md` command must be fixed, and the fix reported), or the test was never written (then the `[RED]`/`[GREEN]` task is not done).
   - Run the specified command.
   - If it reports an error, fix the preceding tasks within the group, then re-run it.
   - The group may only be marked done (`- [x]`) after a green `[CHECK]` — close out `[RED]`/`[GREEN]` tasks only at that point too. **This is the condition for `[GREEN]`; the condition for `[RED]` is the failure evidence in item 8/b — the two do not substitute for each other** (a `[RED]` task does not become done just because the group-closing `[CHECK]` eventually went green).
   - **🔴 Log it in `check-log.md` (TR5) — every attempt, including the failed ones.** The command's output lives in the chat, and the chat is gone after `/clear`; without this, all that remains from the phase is a checkbox that claims green, without proving it. See the *`[CHECK]` run log* section.
   - **3-attempt rule:** If `[CHECK]` has failed three times in a row, and fix attempts within the group have not resolved it — **stop**. Describe what you tried, and tell the user: *"[Tkkk] failed three times. [Short summary of the error and the solutions attempted.] How should we proceed?"*
   - **Port conflict:** If starting a service or running a test fails due to a port conflict (address already in use), do not stop. Find the next free port (`ss -tlnp | grep :<port>` or `lsof -i :<port>`), temporarily update the affected configuration (`docker-compose`, env file), and re-run. Tell the user which port you used instead.
     > **⚠ TEMPORARY CHANGE — DO NOT COMMIT:** the config/port change made for the port conflict is temporary. Before committing the task, RESTORE it, or exclude it from `git add` (it must not end up in the cycle's diff). Only the task's actual code change may be committed.

8/b. **🔴 Closing out a `[RED]` task: the test MUST fail (RED1).** A `[RED]` task is not done when the test file comes into existence, but when the test that was written is **red** — this is the first half of the TDD cycle, and **it is the only evidence that the test actually checks something**. So, before ticking the `[RED]` task:
   1. run the **targeted** test (the `<field:f_test_run>` command from the plan's `TA1` data sheet, narrowed to the one file/case — not the whole suite);
   2. the run must end with a **non-zero** exit code and a `failed > 0` result;
   3. log it in `check-log.md` **with the `[RED]` task's identifier** and a `✗` result (the log records every attempt anyway).

   **If the test is green on its FIRST run, the task is NOT done** — either the test does not check what the plan prescribes, or it is an empty shell (`assert True`, `pass`, a body without assertions). In that case the test is what has to be written, not the task closed out. A green `[RED]` is the most common silent test fraud: the suite reports `X passed`, the `DoD` gets its evidence, and the validation closes on `PASS` without anything having been checked.

   **Exception — `RED-EXEMPT`:** if the `[RED]` task updates an **existing** test (typically the `TREGn` regression tasks) and the test is rightly green after the change too, then write a line into the `## <sec:notes>` section of `check-log.md`: `RED-EXEMPT: <task> — <why it cannot fail>`. Without a justification the task cannot be closed.

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
- Completing the task would require modifying a file that is not named in the task description — **except for a forced consequential change (IM3), see below**.
- A task assumes the result of an earlier task, but that one is not yet done.
- **A `[CHECK]` task has failed three times in a row** (see rule 8).

In every case, ask only **one** question, wait for the response, then continue. **IM2 applies before a stop as well:** first the tick + commit, or the `imp-decision.md` entry about the suspension, and only then the question.

> **This list is exhaustive (IM1).** The phase is stopped exclusively by the four cases listed here, plus item 3 of the *Execution rules* (an unmet `> **Machine prerequisite:**` block) and item 4 (an infrastructure-dependent task). Anything else — including "the task is done and committed" — is a **continuation**, not a stop.

### A forced consequential change (IM3) — the exception to the "file not named" rule

A deletion, a rename or a signature change inevitably ripples out to files the task does not name (the default value pointing at the deleted config, the import of the renamed symbol). If you stopped at every such case, the phase would get stuck in almost every cycle — but if you freely rewrite anything, that is exactly the "creative drift" this section forbids. The boundary:

**You may carry it out without stopping if ALL THREE hold:**
1. the change is a **mechanical consequence** of the listed change — carrying over a reference —, not new behaviour;
2. it has **exactly one correct form** (there is no choice between two solutions, no real design freedom);
3. the failing `[CHECK]`, compilation or test **points at the file and the line itself** — you are not the one hunting for "what else might be affected".

**In that case:** make the **narrowest possible** fix, record it in `imp-decision.md` (*which task forced it · which file:line · why there is only one correct form*), and mention it in the progress line as well. **Do not stop.**

**If any of the conditions does not hold** — you would have to choose between two routes, the consequence would introduce new behaviour, or the scope grows beyond carrying over a reference — **stop and ask**. "I'll creatively push on" is a rule violation here.

> **The feedback is mandatory.** List the files affected this way — the ones no task names — in the **closing message of the phase** as well: it means that `04` (and the coverage round of `05`) left out a mandatory consequential change — otherwise `07` and `09` see a diff in the cycle that was planned nowhere.

---

## `[CHECK]` run log (TR5) — `test-report/implement/check-log.md`

> **Why it's needed:** the output of `[CHECK]` commands lives in the chat, and the chat is gone after `/clear`. Without this, all that remains from the implementation phase is a `- [x]` checkbox and a commit message — both *claim* it was green, but neither proves it. 07-validate demands proof (TR1/TR2) and report artifacts (TR3) for the same reason; in 06, this log is the cheap, text-based counterpart of that.

**Where:** `specs/cycle-NN-<cycle-name>/test-report/implement/check-log.md`. If the folder does not exist, create it. Do **not** touch the `test-report/validate/` and `test-report/review/` subfolders — those are the evidence of 07 and 09.

**When to write to it:** **after every `[CHECK]` run, including the failed ones** — not just after the eventual green attempt. The log is **append-only**: you never rewrite or delete an earlier line.

**What you do NOT do per task:** you do not generate an HTML/Allure/coverage report after every task — the `[CHECK]` log is the cheap, text-based evidence. The full report set is produced **once**, at the end of the phase, and only if the project has declared `implement` a report phase (TR6) — see the *Report phase* section.

### File template

```md
<!-- INCLUDE:lang/06-implement.md#check-log-sablon -->
```

**Columns:**
- **Time** — a concrete string (`YYYY-MM-DD HH:MM`). Shell substitution is platform-dependent: bash/zsh → `$(date '+%Y-%m-%d %H:%M')`, PowerShell → `(Get-Date -Format 'yyyy-MM-dd HH:mm')`. If you cannot determine it, `—` is acceptable too; the other columns are what matters.
- **Task** — **exactly one** task identifier (`T001`, `T030a`, `TREG1`, `TLAST1`). A range (`T030a-T037`), a list (`T031, T032`) and "several tasks in one row" are **forbidden** (CK1): that way the log is a summary rather than evidence, and `07`'s gate cannot decide per task what was actually run.
- **Attempt** — which attempt out of the 3-attempt rule (item 8): `1/3`, `2/3`, `3/3`. This is what makes it visible in hindsight that a group was hard to get through.
- **<field:f_mode>** — `normal` \| `validate-loop` (07's self-healing loop — both test fixes and review fixes). `[CHECK]` runs executed in fix mode are **logged the same way**, with the appropriate marker — so the fix rounds leave a trace too.
- **Command** — the command that was actually issued, **verbatim**, not the idealized version from the task text.
- **Result** — `✓`/`✗` + the runner's counts (`X passed / Y failed / Z skipped`), and on failure, the name(s) of the failed test(s) with a short error message. **For `[RED]` tasks the `✗` is not a failure but the mandatory evidence (RED1)** — per item 8/b, it is precisely this row that makes the `[RED]` task closable. **If the command is not a test** (build, lint, typecheck), put one line of the essential output in place of the count (e.g. `0 errors`).

**<sec:notes> section** — this is where any circumstance that affected the run but does not fit the table goes: a temporary port swap (and whether it was reverted — the port-conflict rule in item 8), a manually started/stopped container, a skipped check and its reason. **The exemption lines live here too:** `RED-EXEMPT: <task> — <reason>` (the `[RED]` cannot fail, item 8/b) and `CK-DEVIATION: <task> — <reason>` (the framework cannot filter down to a single case, item 8). Both prefixes are **language-independent literals** — `07`'s gate matches on them verbatim.

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


## Implement-phase tests (PH1) — once, at the end of the phase

The `<field:f_phase>` column of the machine-readable run table of `plan.md` says which categories have to run in **this** phase (`<status:phase_implement>` or `<status:phase_both>`; **an unmarked row belongs here too** — silence does not mean skipping). This does not replace the per-task `[CHECK]`: the `[CHECK]` proves the green of a group, this proves the **closing state of the phase**, with machine counts and evidence. After every task is `[x]`, but BEFORE the status change, **once**:

```bash
python3 <platform-scripts-mappa>/run-tests.py \
  specs/cycle-NN-<cycle-name>/plan.md \
  --round-dir specs/cycle-NN-<cycle-name>/test-report/implement \
  --phase <status:phase_implement>
```

- **`exit 0`** → the output brings, per category, the command issued and the `X passed / Y failed / Z skipped` counts; the evidence goes into the phase folder and enters with the closing commit.
- **`exit 1`** → there is a failing category: this is **the same 3-attempt rule** as with a `[CHECK]` — fix the failure, run it again, and log it into `check-log.md`. After three failures stop and ask.
- **`exit 2`** → there is no machine-readable table in the plan (an old cycle): this is not your fault and not a stop — note in one line in the closing message of the phase that the table of `03` is missing.
- **A `MEGJEGYZÉS (PH1)` line saying there is nothing to run** → every row of the table is `<status:phase_validate>`-only. Move on.

> **This is not a new stopping point (IM1).** The run is part of closing the phase, in the same turn — unlike the `[CHECK]`s it does **not** run per task.

## Test-substance gate (TB1) — before closing the phase

Once every task is `[x]`, but **before** the status change, run the test-substance gate. It examines the test files listed in the plan's `TA1` data sheets: is any of them an **empty shell** (`assert True`, `pass`, a body without assertions)?

```bash
python3 <platform-scripts-mappa>/test-substance-check.py specs/cycle-NN-<cycle-name>
```

- **`exit 0`** → the *Report phase* and the status change can proceed;
- **`exit 1`** → **the phase cannot be closed.** The test functions listed must **be written**: this is not "the test will be written in 07" — the test is the **product** of the `[RED]` task, and with an empty shell the task is not done (RED1). After fixing it, re-run the task's `[CHECK]` (verbatim, with the selector — CK1), log it, and only then close.

> **Why this is a machine gate and not a checklist line:** an empty shell is green immediately, so the `[CHECK]` counter, the `DoD` evidence and the validation `PASS` are **all satisfiable** without anything having been checked. The implementer has an interest in the checkbox (`7/j`) — which is why this is not left to their judgment.

## Report phase (TR6) — `test-report/implement/`

`implement/` is an **official phase folder**: not only the place of `check-log.md`, but also that of the full report set of 06's closing state — if the project decides so. The decision lives in the `**<field:f_report_phases>:**` field of the `## <sec:cv_test_reporting>` section of `conventions.md` (`implement`, `validate`, or both; in the absence of the field the default is `validate`). **Do not guess it** — query it deterministically, after every task is `[x]` but BEFORE the status change:

```bash
python3 <platform-scripts-mappa>/report-gate-check.py \
  conventions.md specs/cycle-NN-<cycle-name> --phases
```

- **`implement` is not in the output** → you have nothing to do: the report set is produced by 07 in its own rounds. Move on to the status change.
- **`implement` is in the output** → run the report-generating commands of the `## <sec:cv_test_reporting>` table of `conventions.md` for the phase folder, then close with the gate:

```bash
python3 <platform-scripts-mappa>/report-gate-check.py \
  conventions.md specs/cycle-NN-<cycle-name> \
  --report-subdir test-report/implement
```

**The form of the phase folder is `implement`** — this is what the `<phase-dir>` placeholder or the `REPORT_PHASE_DIR`-style environment variable of the report commands gets. Never write the full `specs/cycle-NN-<cycle-name>/test-report/implement` path there: mixing up the bases builds a recursive `test-report/test-report/…` tree, which the layout guard of the gate fails with `exit 1` (TR5/c).

- **`exit 0`** → done, the status change can follow; the report artifacts go in with the closing commit.
- **`exit 1`** → a missing or empty artifact, or a foreign folder under `test-report/`. **This is not a code bug: you do not start a fixer and you do not step back to a task** — re-run the missing report-generating command, or delete the foreign folder, and re-run the gate. If the command itself is wrong (it does not produce the artifact), that is a gap of `conventions.md`: stop and ask the user.

> **This is not a new stopping point (IM1).** Generating the report is part of closing the phase, in the same turn — do not hand the floor back to the user between the `--phases` query and the gate.

## Status handling

- While implementing: `<status:implement_in_progress>`
- If every task is `[x]`: update the `tasks.md` status to `<status:ready_for_validate>`, and **commit this state change** (the final status must be recorded separately) — together with the last entries of `check-log.md`:
  ```bash
  git add specs/cycle-NN-<cycle-name>/tasks.md \
          specs/cycle-NN-<cycle-name>/test-report/implement/ \
    && git commit -m "cycle-NN: 06-implement - done, ready for validation"
  ```
  **Check before the status change:** the *Test-substance gate (TB1)* section has run (`exit 0`) and the *Report phase (TR6)* section has run (the `--phases` query, and if `implement` is a report phase, the gate with `exit 0`); `check-log.md` exists, and every group-closing `[CHECK]` has at least one line for it in the log. If a group is `[x]` but the log has no entry for it, the evidence is missing — add the missing log line based on the actual run (not from memory: if you do not know, re-run the `[CHECK]`).

If the status is `<status:ready_for_validate>`, stop. Inform the user of the next step and the phase's launch command, for example:
<!-- INCLUDE:lang/06-implement.md#zaro-uzenet -->
> **Place the direct, clickable link to `tasks.md` and `check-log.md` at the end of the response** — this is the phase's single stop signal (IM1).


> **Phase boundary — hard stop (PE1).** The phase **ends** with the closing message (commit ID + `/clear` + the next phase's command). In the same turn, you do **not** start anything from the next phase — you do not even create the next phase's artifact. This holds even if a **context summary / checkpoint** to-do list, your own earlier plan, or a "let's go through the whole process" remark from the user in an earlier turn encourages moving on: the skill's phase boundary outranks all of that. Only an **explicit request from the user for this turn** overrides it. If you nonetheless started it, **delete the resulting file**, restore a clean working tree, and report it.

---

<!-- INCLUDE:shared/fix-mode-implement.md -->
