<!-- Source note: the Fix mode section of the 02-write-spec skill, extracted so that the
     spec-fixer subagent prompt can inline it at build time (BD14/b). This way the fixer
     does NOT have to read the whole of 02-write-spec.md. Edit it in one place. -->
## Fix mode (analyze-loop entry point)

> **When it is active:** this section is started by the self-healing loop of `05-analyze` through the `agents/spec-fixer.md` wrapper — **not** by normal spec writing. The input is a concrete `<status:must_fix>` list, not a full re-run.

> **Reading the skill is not needed (D13):** every rule needed for the fix mode is in this prompt — including the "Quality check" section of the phase. **In fix mode do not read the whole phase skill** (`02-write-spec.md`): it is unnecessary, and it tempts you to re-run the whole phase, whereas the task is a narrow, targeted correction.

The fix mode is a **narrowed entry point:** you correct the given `<status:must_fix>` findings in a targeted way, you **do not rewrite the whole spec**. In fix mode you **ignore** the `*-input-from-prev.md` files **completely** (you neither read nor write them) — IP1/6. (Otherwise a cheaper LLM tends to start the phase from scratch — that is forbidden.) The quality gates of the normal flow (the "Quality check" section of the phase) still apply to the corrected parts — **only to the corrected parts**, not to the whole document.

### Input
- The `<status:must_fix>` list filtered for the spec (category + description + `file:location`).
- The current state of `spec.md` and `spec-questions.md`.

### Auto-fixable vs. has to be asked (the boundary)

| Fix it yourself (auto) | Turn it into a question (a new `Qnn` in `spec-questions.md`) |
|---|---|
| Filling a coverage gap in prose, unifying naming, refining wording, merging a duplicated requirement | Spec-level ambiguity, a missing or undecidable acceptance criterion, undefined behavior, a business decision |

A `<status:must_fix>` that needs a **real decision** — **do not invent it**; add it as a new `Qnn` to the end of `spec-questions.md` (according to the normal flow), and **do not ask the user directly** (in fix mode you have no interactive channel). The asking is done by the orchestrator (`05-analyze`), with a phase header.

### <field:f_status> (auto, the `[analyze-loop]` marker)
The loop reopened the status of `spec.md` with an `[analyze-loop]` marker (e.g. `<status:draft> [analyze-loop]`). While the marker is present, you step the status **automatically**, without asking for confirmation (in contrast to the "confirmation before the status change" rule of the normal flow):
- there is an open `[ ]` question in `spec-questions.md` → `<status:open_questions> [analyze-loop]`;
- every question is `[x]` and the targeted correction is done → `<status:ready_for_plan> [analyze-loop]`.

Putting the marker on and taking it off is handled by the orchestrator; you only step the status value, you leave the marker unchanged.

### Return summary (to the orchestrator)
Return a concise summary: (a) which `<status:must_fix>` items you fixed and how, (b) which new `Qnn` questions you added to `spec-questions.md` (with their identifier). You write `spec.md` and `spec-questions.md`; you do **not** write `analyze-report.md` — that belongs to the orchestrator.

- **`downstream-effect:`** (D11) — a mandatory field: `none`, or `yes — <what changed that affects the next phase>`. The orchestrator decides from this whether the downstream fixers have to be started at all. **In case of uncertainty, `yes`**, naming the concrete reason — but a plain "just to be safe" is not a reason.
