<!-- Source note: when and how a CYCLE may modify the project-level
     conventions.md, and what moves together with it (GC1). It is inlined by the 03
     skill and by the quality check of 03 (so by the plan-fixer too). Edit it in one place. -->
**The gate configuration moves together with the structure (GC1).**

`conventions.md` is the **project**-level source of truth, and `00-init-project` is its owner — but several **deterministic gates also read from it**, therefore if a cycle changes something that a gate looks for here, `conventions.md` has to be adjusted **in the same cycle**. Otherwise the gate looks in the old place/for the old value, and `07-validate` fails — the error surfaces two phases later, in the validation.

**What a gate reads from `conventions.md`** (if the cycle touches these, updating the section is part of the cycle):

| `conventions.md` section | Who reads it | What breaks if it does not move along |
|---|---|---|
| `## <sec:cv_test_reporting>` (artifacts, path base, report phases, report commands) | `report-gate-check.py` (TR3/TR6, 06 + 07) | the gate looks for the report on the old path, or demands it in the wrong phase → FAIL |
| `## Sonar` (project key, thresholds, location of the report) | `sonar-gate.py` (07) | the Quality Gate check runs for the wrong project/threshold |
| `## <sec:cv_test_tools>` / test commands | `run-tests.py`, `test-runner` (07) | it runs a command that does not exist |
| `## <sec:cv_merge_strategy>` | `09-merge` | the merge branch tries the wrong path |
| `## <sec:cv_ports>`, `## <sec:cv_env_vars_short>` | 06/07 execution | the test runs with a different configuration than the development |

**How a cycle modifies a convention — the four conditions:**
1. **An explicit decision,** not a by-product: there should be a `DoD-NN` item for it in `spec.md` (or at least a decision stated in the `<sec:goal_and_approach>` section of the plan) that the cycle also changes the convention.
2. **The plan plans it:** the affected section of `conventions.md` appears in the `<sec:planned_changes>`, with the **concrete new content** (not in a "we will update the conventions" manner).
3. **There is a task for it:** a separate task in `tasks.md` edits `conventions.md`. The marker is `[GREEN]` (it modifies a repo file), **not** `[OPS]`.
4. **The gate runs again in the same cycle:** the FULL round of 07 validates with the updated `conventions.md` — this way the change is proven to work, it is not a debt left to the next cycle.

> **When it is NOT the cycle's business:** if the question is whether the **project convention itself** is correct (a different test tool, a different merge strategy, a different naming), that is a **human decision** → the severe convention-conflict branch of `05-analyze` directs it to `00`. GC1 is about the case when the decision **is already made** and the cycle carries it out: that need not be pushed back into `00`.

> **`specs/test-conventions.md` is not a substitute (TC1/c):** report artifact, path base and report command → `conventions.md` (this is what the TR3 gate reads); test recipe and coordinates → `test-conventions.md` (maintained by 08-doc-sync). If the cycle restructures the reporting, **updating `test-conventions.md` on its own is not enough.**
