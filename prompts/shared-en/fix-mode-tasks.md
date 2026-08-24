<!-- Source note: the Fix mode section of the 04-write-tasks skill, extracted so that the
     tasks-fixer subagent prompt can inline it at build time (BD14/b). Edit it in one place. -->
## Fix mode (analyze-loop entry point)

> **When it is active:** this section is started by the self-healing loop of `05-analyze` through the `agents/tasks-fixer.md` wrapper — **not** by normal tasks writing. The input is a concrete `<status:must_fix>` list, not a full re-run.

> **Reading the skill is not needed (D13):** every rule needed for the fix mode is in this prompt — including the "Quality check" section of the phase. **In fix mode do not read the whole phase skill** (`04-write-tasks.md`): it is unnecessary, and it tempts you to re-run the whole phase, whereas the task is a narrow, targeted correction.

The fix mode is a **narrowed entry point:** you correct the given `<status:must_fix>` findings in a targeted way (typically a coverage gap or a task-level duplication), you **do not rewrite the whole list**. In fix mode you **ignore** the `*-input-from-prev.md` files **completely** (you neither read nor write them) — IP1/6. (Otherwise a cheaper LLM tends to start the phase from scratch — that is forbidden.) The quality check of the normal flow (the "Quality check" section of the phase) still applies to the corrected parts — **only to the corrected parts**, not to the whole list.

### Two entry forms
1. **Direct correction:** the `<status:must_fix>` concerns the tasks list (a coverage gap, a redundant task — the target phase is 04).
2. **Downstream re-derivation (reconciliation):** the loop corrected further up (02/03), and the tasks list has to be **aligned** with the changed plan. A targeted reconciliation, not a full rewrite: you adjust only the tasks belonging to the changed plan sections.

### Input
- The `<status:must_fix>` list filtered for the tasks (category + description + `file:location`), or, in case of a reconciliation, the summary of the changed upstream (plan).
- The current state of `tasks.md` and `tasks-questions.md`.

### Auto-fixable vs. has to be asked (the boundary)

| Fix it yourself (auto) | Turn it into a question (a new `Qnn` in `tasks-questions.md`) |
|---|---|
| Filling a coverage gap (adding a missing task from the plan), merging a task duplication, unifying naming, carrying a plan change over into the tasks list | A task that cannot be derived unambiguously from the plan (the plan is incomplete), a circular task dependency, a conditional task or one depending on an external dependency |

A `<status:must_fix>` that needs a **real decision** (typically when it signals a deficiency of the plan) — **do not invent it**; add it as a new `Qnn` to the end of `tasks-questions.md`, and **do not ask the user directly** (in fix mode you have no interactive channel). The asking is done by the orchestrator (`05-analyze`), with a `TASKS/Qnn` prefix towards the user. (This is the fix-mode equivalent of the "Stopping rules" point of the normal flow: in normal mode STOP + report, in fix mode collecting questions into `tasks-questions.md`.)

### What is MANDATORY to preserve in fix mode as well (PID1)

When adding or modifying a task, the referencing order must not break — this is exactly the most frequent silent damage done by the loop:

- **every new task gets a `— plan [P-…]` reference** (one primary ID; if several tasks share an ID, with a sub-scope marking);
- **update the `<sec:plan_coverage>` table** with the new tasks — it must not stay in its old state;
- **extend the plan-ID list of the group header**, if a task covering a new section got into the group;
- if the plan-fixer created a **new `[P-…]` section**, it needs a referencing task (or a justified row in the table);
- **you never invent a plan ID**: if you cannot assign an existing ID to the task, that is a `tasks-questions.md` question.

_(The mechanical gate — `analyze-gate-check.py` — will point these out in the next round anyway; it is cheaper to do it right here.)_

### <field:f_status> (auto, the `[analyze-loop]` marker)
The loop reopened the status of `tasks.md` with an `[analyze-loop]` marker (e.g. `<status:draft> [analyze-loop]`). While the marker is present, you step the status **automatically**, without asking for confirmation:
- there is an open `[ ]` question in `tasks-questions.md` → it stays `<status:draft> [analyze-loop]`;
- every question is `[x]` and the targeted correction is done (the quality check passed) → `<status:ready_for_implement> [analyze-loop]`.

Putting the marker on and taking it off is handled by the orchestrator; you only step the status value.

### Return summary (to the orchestrator)
Return a concise summary: (a) which `<status:must_fix>` items / plan changes you carried over and how, (b) which new `Qnn` questions you added to `tasks-questions.md` (with their identifier). You write `tasks.md` and `tasks-questions.md`; you do **not** write `analyze-report.md` — that belongs to the orchestrator.

- **`downstream-effect:`** (D11) — a mandatory field: `none`, or `yes — <what changed that affects the next phase>`. The orchestrator decides from this whether the downstream fixers have to be started at all. **In case of uncertainty, `yes`**, naming the concrete reason — but a plain "just to be safe" is not a reason.
