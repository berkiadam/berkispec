<!-- Source note: the Fix mode section of the 06-implement skill, extracted so that the
     implement-fixer and the review-fixer subagent prompts can inline it at build time
     (BD14/b, D13). This way the fixers do NOT have to read the whole of
     06-implement.md — which would be a path that does not even exist in the target project.
     Edit it in one place. -->
## Fix mode (the entry point of the self-healing loop of 07)

> **When it is active:** this section is started by the self-healing loop of `07-validate` through a fixer subagent — **not** by the normal implementation. There are two wrappers, with identical mechanics and **the same marker** (`[validate-loop]`), only the input section differs:
> - **test/Sonar/DoD failure:** the `implement-fixer` subagent → the input is the tasks of the `## <sec:validation_fixes>` section of `tasks.md`;
> - **code review finding:** the `review-fixer` subagent → the input is the tasks of the `## <sec:review_fixes>` section of `tasks.md` (the `MF-NN` findings of `test-report/code-review.md`).
>
> In both cases the task is the targeted correction of a **concrete failure list**, not the re-implementation of the whole cycle.
> **Reading the skill is not needed (D13):** every rule needed for the fix mode is in this prompt. **In fix mode do not read the whole phase skill** (`06-implement`): it is unnecessary, such a path does not even exist in the target project, and it tempts you to re-run the whole phase, whereas the task is a narrow, targeted correction.

The fix mode is a **narrowed entry point:** you correct the given test/Sonar/DoD failures in a targeted way, you **do not re-implement the cycle** (2.2). (Otherwise a cheaper LLM tends to start the phase from scratch — that is forbidden.) The normal execution and quality rules of 06 (running the `[CHECK]` green, updating the code comments, deep module) still apply to the corrected parts — **including the `[CHECK]` run log**: you record the checks run in fix mode into `test-report/implement/check-log.md` just the same, with a `validate-loop` marking in the **<field:f_mode>** column. This way the `[CHECK]`s of the fixing rounds also leave a trace, and the loop can be reconstructed afterwards.

> **What you do NOT write in fix mode:** the `test-report/validate/` round folders — those belong to the orchestrator (07) and to the `test-runner`. You only extend `test-report/implement/check-log.md` (on top of the code and the fixing section of `tasks.md`).

### Input
Depending on the caller, the unfinished `[GREEN]`/`[CHECK]` tasks of the fixing section at the end of `tasks.md`, together with the prerequisite references at the beginning of the section:
- **test/Sonar/DoD branch:** `## <sec:validation_fixes>` (added by 07 from the concrete test/Sonar failures); prerequisite:
  - `specs/cycle-NN-<cycle-name>/test-report/validation-report.md` (the `# <sec:validation_history>` with the details of the failures),
  - if Sonar failed: the Sonar report of **that round** — `specs/cycle-NN-<cycle-name>/test-report/validate/round-NN/sonar-report.md`. The concrete round number is given by the prerequisite reference of the section (TR5); **do not go rummaging in the folders of other rounds**, and not in the root of `test-report/` either — there is no Sonar report there.
- **review branch:** `## <sec:review_fixes>` (added by 07 from the `<status:must_fix>` findings); prerequisite:
  - `specs/cycle-NN-<cycle-name>/test-report/code-review.md` (the findings with their `MF-NN` identifier).
- The current state of `tasks.md` (the `<status:ready_for_implement> [validate-loop]` status).

### The boundary between fix mode and normal implement (2.2)
- **Focus:** exclusively the tasks of the active fixing section (`## <sec:validation_fixes>` OR `## <sec:review_fixes>`) — correcting the concrete failed tests / Sonar failures / unfulfilled DoD items / `<status:must_fix>` findings.
- **Not a full re-implementation:** do not re-run and do not rewrite the tasks that are already green and closed (`[x]`). You work on the failure list only.
- 06 already knows both entries (see "A step back can arrive here from two sources" — the `## <sec:validation_fixes>` and the `## <sec:review_fixes>` branch); the fix mode builds on that, it does not duplicate it.

### <field:f_status> (auto, the `[validate-loop]` marker)
The loop reopened the status of `tasks.md` with its marker (`<status:ready_for_implement> [validate-loop]`) — the same marker is used for the test fixes and for the review fixes. While the marker is present, you step the status **automatically**, without asking for confirmation (in contrast to the normal "confirmation before the status change" rule) — keeping the marker throughout:
- during the correction: `<status:implement_in_progress> [validate-loop]`;
- if every task of the active fixing section is `[x]` and the group-closing `[CHECK]` is green: `<status:ready_for_validate> [validate-loop]`.

Putting the marker on and taking it off is handled by the orchestrator (`07-validate`); you only step the status value.

### ⚠ Anti-"cheating" guard (VD3 / RD4 — mandatory)

**The fix mode adjusts the CODE to the test / to Sonar / to the DoD / to the review finding — NEVER the other way round.** The test, the DoD and the `<status:must_fix>` finding of the reviewer are the **contract**, which the fix mode must not weaken and must not silence.

**It is FORBIDDEN** to force a green/clean result in any way that circumvents the contract:
- weakening or loosening a test assertion, or copying the expected value back from the code;
- `skip`/`xfail`/commenting out/deleting a test;
- a hardcoded "expected" value that only turns the test green but does not implement the real behavior;
- lowering or rephrasing a <sec:definition_of_done> item of `spec.md` so that it is easier to fulfill;
- **(review branch, VD3)** the **cosmetic silencing** of a `<status:must_fix>` finding without fixing the root cause (a lint-suppress comment, disguising the code objected to), or deleting/rephrasing the finding in `test-report/code-review.md` without fixing it.

**If you judge that a failure could ONLY be turned green/clean by changing the contract (test/DoD/spec) or by silencing the finding** — that is **not a code fix**. **STOP**: do not touch the contract, but hand it back to the orchestrator in the return summary with an **escalation signal** (see below). This is the input of the branch escaping upwards — the VD5 branch of 07 (the design/contract question has to be settled in phase 03/02, not here).

### Return summary (to the orchestrator)
At the end of your run, give a concise summary to the calling orchestrator (`07-validate`):
- **Corrections made:** which fixing tasks you closed, and how (one line per failure/finding) — with what code change it became green/done.
- **Escalation signal (if any):** if one of the failures could only be turned green/clean by modifying the contract (test/DoD/spec) or by silencing the finding (forbidden by VD3/RD4) → state it unambiguously: *"ESCALATION: [item] appears to be a design/contract error — it would only be green by modifying the contract or by silencing the finding; I did not fix it."* State why.
- **The current status of `tasks.md`** (with the `[validate-loop]` marker).

You write the code and the active fixing section of `tasks.md` (`## <sec:validation_fixes>` / `## <sec:review_fixes>`); you do **not** write `validation-report.md` and `test-report/code-review.md` — those belong to the orchestrator.
