<!--
  The PROJECT-LANGUAGE blocks of `04-write-tasks` (9.4 extraction).
  The installer inlines this file at build time in place of the INCLUDE markers,
  according to the chosen PROJECT language (`PROJECT_LANG`); the marker form is
  `lang/04-write-tasks.md#<anchor>`.
  The blocks were moved here VERBATIM — do not rephrase, do not unify.
  The ANCHOR lines are NOT part of the inlined text, they are delimiters only (8.9).
  CAUTION: no comment-closing sequence may appear in this leading note.
-->

<!-- ANCHOR:task-formatum -->
- [ ] T001 [RED]   <create the test file / write the test> — `path/to/test.ts` — plan [P-CONFIG] — test [TC-01, TC-02]
- [ ] T002 [GREEN] <implementation> — `path/to/file.ts` — plan [P-CONFIG] (loader module)
- [ ] T003 [OPS]   <non-TDD step: build / push / deploy / manual configuration> — command or `path/to/file` — plan [P-DEPLOY]
- [ ] T004 [CHECK] Run: `npx tsx --test path/to/test.ts -t "<the test function name of TC-01>"` — plan [P-CONFIG] — test [TC-01]
- [ ] T005 [CHECK] Run: `npx tsx --test path/to/test.ts -t "<the test function name of TC-02>"` — plan [P-CONFIG] — test [TC-02]
- [ ] T006 [CHECK] Run: `npm run typecheck` — plan [P-CONFIG]

<!-- ANCHOR:tasks-struktura -->
# Cycle NN: <title> — Tasks

**Status:** `Draft` | `Ready for implementation`

## Prerequisite documents

_The implementing agent reads these before execution._

- `specs/<cycle-name>/plan.md`
- _(further Reviewed artifacts from the Schema artifacts table of the plan)_

> `[RED]` = writing a test (it will fail) · `[GREEN]` = implementation (turning the test green) · `[CHECK]` = running a verification · `[OPS]` = non-TDD step (build, deploy, manual configuration, approval, rollback)

## <Logical group 1 — based on the execution order of the plan> — plan [P-CONFIG], [P-REDIS]

- [ ] T001 [RED]   ... — plan [P-CONFIG] (unit test) — test [TC-01, TC-02]
- [ ] T002 [GREEN] ... — plan [P-CONFIG] (loader module)
- [ ] T003 [CHECK] Run: `npm test -- path/to/test.ts -t "<the name of TC-01>"` — plan [P-CONFIG] — test [TC-01]
- [ ] T004 [CHECK] Run: `npm test -- path/to/test.ts -t "<the name of TC-02>"` — plan [P-CONFIG] — test [TC-02]

## <Logical group 2> — plan [P-ROUTING]

- [ ] T005 [RED] ... — plan [P-ROUTING] — test [TS-01]
- [ ] T006 [CHECK] Run: `pytest test/integration/cycle_NN_test.py -k ts01` — plan [P-ROUTING] — test [TS-01]
- [ ] T007 [CHECK] Run: `npm run typecheck` — plan [P-ROUTING]

## Plan coverage (reverse table)

_Every plan section bearing a `[P-…]` ID appears here, with the tasks belonging to it._

| Plan section (ID + title) | Tasks | Group |
|---|---|---|
| `[P-CONFIG]` Configuration system | T001, T002, T003, T004 | 1 |
| `[P-ROUTING]` Dynamic routing | T005, T006, T007 | 2 |
| `[P-DOCS-ONLY]` … | — (no task: <justification>) | — |

## Test coverage

_Every `TS-NN` scenario of the plan and every category of the machine-readable run table appears here._

| Plan test (`TS-NN` / `TC-NN` / category) | Creating task | Running task | Note |
|---|---|---|---|
| `TC-01` keyNamespace default | T001 | T003 | unit |
| `TC-02` missing `expiresAt` → error | T001 | T004 | unit |
| `TS-01` Cold-start concurrency | T005 | T006 | pytest, `implement` + `validate` |
| unit (run table) | — | T003, T004 | 07 also runs it from the table |
| e2e (run table) | T005 | — | `validate`-phase: 07 runs it from the table |
| `TS-07` Manual SPI check | — | — | cannot be automated: a manual `[OPS]` step in T018 |

<!-- ANCHOR:desztruktiv-csoport-sablon -->
## Destructive tasks / tasks touching a shared environment — approval and rollback

If the plan schedules a step that modifies a **shared (non-disposable) environment** — deployment/pod replacement in a shared cluster, image push to a common registry, seeding or deletion in a shared database, overwriting a configuration —, it must be **flanked by three tasks** in its own logical group:

```md
- [ ] T0nn [OPS]   Ask the user for APPROVAL to run <operation> — affected: <environment/namespace/registry>; the operation may also affect the work of other developers. Record the original state INTO A FILE: `<state-reading command> > .rollback-state`
- [ ] T0nn [OPS]   <the actual destructive operation> — `<concrete command; reading the state of the earlier step from the file>`
- [ ] T0nn [CHECK] Verify that the operation succeeded — `<verification command + expected output>`
- [ ] T0nn [OPS]   ROLLBACK (only if the previous `[CHECK]` failed): restore the original state — `<restoring command, read from .rollback-state>`
```

> **🔴 State persistence — the most frequent silent error.** Every task runs in a **separate shell**, therefore `VAR=...` or `export VAR=...` **evaporates by the next task**. If the rollback or the deploy references a value produced in an earlier task (a saved original identifier, a generated unique tag), it would **run with an empty parameter** — that is, the rollback exists on paper but does not work in practice. Therefore such state **goes into a file**, and later tasks read it from there; or you merge the dependent commands **into one task**.

Two further rules for the state file:
- **Where it should go:** into the folder of the cycle (`specs/cycle-NN-<cycle-name>/.rollback-state`), **not into the root of the repo**. If it does end up in the root, add a task that also writes it into `.gitignore` — otherwise, after an interrupted run, it stays in the working tree and may get into a commit.
- **Cleanup is mandatory:** the last task of the group (or the successful `[CHECK]`) must delete it (`rm -f`). After an interrupted run an old state file is **worse than nothing**: it would restore to an outdated identifier.

- The **approval task comes first** — the destructive operation must not run without the user having agreed to it.
- The approval task **records the original state** (together with the reading command) — without it the rollback cannot be carried out.
- The **rollback task stands at the end of the group**, conditionally. If the plan gives no rollback scenario, that is a **plan deficiency**: raise it as a question in `tasks-questions.md`, do not invent it yourself.
- **If the operation overwrites an existing identifier** (e.g. it pushes to the same image tag), point it out: in that case **there is nothing to restore to**, so either the version must be bumped, or the rollback is not real — this requires a review of the plan.

## Regression test review

- [ ] TREG1 Verify / update: `test/unit/foo.test.ts` — affected, because [justification from the plan]
- [ ] TREG2 Verify / update: `test/integration/cycle-XX-foo.sh` — affected, because [justification from the plan]

<!-- ANCHOR:dokumentacio-csoport-sablon -->
## Documentation

- [ ] TLAST1 ...the documentation update explicitly requested by the plan that does NOT belong under docs-generated/...

<!-- ANCHOR:statusz-megerosites -->
*"The quality check of the task list passed. Is the task list ready for implementation? If you confirm, I will switch it to `Ready for implementation` status."*

<!-- ANCHOR:zaro-uzenet -->
> *"The task list is done. We can continue with step 5 (analyze — cross-phase consistency check). Before starting the new phase, be sure to run a `/clear` command to empty the context, then use this command:
> ```
> /bs-analyze input: @specs/cycle-NN-<cycle-name>
> ```"*
