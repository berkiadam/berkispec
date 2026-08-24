<!-- Source note: the Fix mode section of the 03-write-plan skill, extracted so that the
     plan-fixer subagent prompt can inline it at build time (BD14/b). Edit it in one place. -->
## Fix mode (analyze-loop entry point)

> **When it is active:** this section is started by the self-healing loop of `05-analyze` through the `agents/plan-fixer.md` wrapper — **not** by normal plan writing. The input is a concrete `<status:must_fix>` list, not a full re-run.

> **Reading the skill is not needed (D13):** every rule needed for the fix mode is in this prompt — including the "Quality check" section of the phase. **In fix mode do not read the whole phase skill** (`03-write-plan.md`): it is unnecessary, and it tempts you to re-run the whole phase, whereas the task is a narrow, targeted correction.

The fix mode is a **narrowed entry point:** you correct the given `<status:must_fix>` findings in a targeted way, you **do not rewrite the whole plan**. In fix mode you **ignore** the `*-input-from-prev.md` files **completely** (you neither read nor write them) — IP1/6. (Otherwise a cheaper LLM tends to start the phase from scratch — that is forbidden.) The quality gates of the normal flow (the "Quality check" section of the phase + the Constitution Check) still apply to the corrected parts — **only to the corrected parts**, not to the whole document.

> **Section IDs in fix mode (PID1):** you **do not rename and do not delete** the existing `[P-…]` identifiers — `tasks.md` references them, and a rename severs every affected task from its plan. When inserting a new section, a **new ID**; when deleting a section, tell the orchestrator that the tasks referencing it also have to be sorted out by the 04 fixer.

### Two entry forms
1. **Direct correction:** the `<status:must_fix>` finding concerns the plan (the target phase is 03) — you correct it in a targeted way.
2. **Downstream re-derivation (reconciliation):** the loop corrected further up (02, spec), and the plan has to be **aligned** with the changed spec. This is a **targeted reconciliation, not a full rewrite:** you adjust only the plan parts belonging to the changed spec sections, and you **preserve** the closed decisions of `plan-questions.md`.

### Input
- The `<status:must_fix>` list filtered for the plan (category + description + `file:location`), or, in case of a reconciliation, the summary of the changed upstream (spec).
- The current state of `plan.md` and `plan-questions.md`.

### Auto-fixable vs. has to be asked (the boundary)

| Fix it yourself (auto) | Turn it into a question (a new `Qnn` in `plan-questions.md`) |
|---|---|
| Refining the coverage/component mapping, unifying naming, merging a design duplication, carrying a spec change over into the plan | A technical decision affecting observable behavior (HTTP code, retry policy, response field), the fundamental technology decision of an undefined component, a spec contradiction |

A `<status:must_fix>` that needs a **real decision** — **do not invent it**; add it as a new `Qnn` to the end of `plan-questions.md`, and **do not ask the user directly** (in fix mode you have no interactive channel). The asking is done by the orchestrator (`05-analyze`). (The boundary is the same as in normal plan writing: you do not decide a question affecting observable behavior or a fundamental technology choice on your own.)

### <field:f_status> (auto, the `[analyze-loop]` marker)
The loop reopened the status of `plan.md` with an `[analyze-loop]` marker (e.g. `<status:draft> [analyze-loop]`). While the marker is present, you step the status **automatically**, without asking for confirmation:
- there is an open `[ ]` question in `plan-questions.md` → `<status:open_questions> [analyze-loop]`;
- every question is `[x]`, every section is in order, every schema artifact is `<status:reviewed>`, and the targeted correction is done → `<status:ready_for_tasks> [analyze-loop]`.

Putting the marker on and taking it off is handled by the orchestrator; you only step the status value.

### Return summary (to the orchestrator)
Return a concise summary: (a) which `<status:must_fix>` items / spec changes you carried over and how, (b) which new `Qnn` questions you added to `plan-questions.md` (with their identifier). You write `plan.md` and `plan-questions.md`; you do **not** write `analyze-report.md` — that belongs to the orchestrator.

- **`downstream-effect:`** (D11) — a mandatory field: `none`, or `yes — <what changed that affects the next phase>`. The orchestrator decides from this whether the downstream fixers have to be started at all. **In case of uncertainty, `yes`**, naming the concrete reason — but a plain "just to be safe" is not a reason.
