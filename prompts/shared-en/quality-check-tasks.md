<!-- Source note: this section is inlined by the 04-write-tasks.md skill AND by the
     corresponding fix-mode-* shared file (build-time INCLUDE). Edit it in one place. -->
## Quality check — before closing

Go through the following groups in order. Tick off every group on its own before moving on to the next one.

### A) Plan coverage

- Does the list of Prerequisite documents contain `plan.md` and every `<status:reviewed>` schema artifact?
- **A plan reference on every task (PID1):** does every task line end with `— plan [P-…]`, with **exactly one** primary ID (a second one in parentheses, as a "see also")?
- **The IDs EXIST in the plan:** compare the IDs used with the headings of the plan (`grep -o '\[P-[A-Z0-9-]*\]' plan.md`) — is there no invented or mistyped ID, and did no **reference by ordinal** (`§ 3.1`) remain in it?
- **No reference pointing at an inventory section:** every primary reference points at an **executable** plan section bearing a `[P-…]` ID. If you did not find such a one for a task, did it become a `tasks-questions.md` question (you did not substitute text of your own)?
- **Sub-scope marking:** where **several tasks** reference the same ID, is the parenthesized scope present on each of them (`(config files)`, `(loader module)`, `(unit test)`)?
- **Group headers:** are the plan IDs covered by the group present at the end of every `## <logical group>` title?
- **The `<sec:plan_coverage>` table is complete:** does **every** `[P-…]` section of the plan appear in the table — either with tasks, or with `—` + a one-sentence justification? Is there no ID in the plan that was left out of the table, and no ID in the table that does not exist in the plan?
- **No duplication (PID1/b):** is there no task that contains the value list, the code→code mapping or the step sequence of the plan **copied over** (except for the `[CHECK]`/`[OPS]` commands, which match the ones in the plan character by character)?
- **Plan `<sec:planned_changes>` coverage:** go through it file by file — did every file get at least one task?
- **Plan `<sec:verification_strategy>` coverage:** go through every command of the `<sec:verification_strategy>` section of the plan — did each one appear as a `[CHECK]` task in one of the groups?
- **<sec:regression_impact> covered:** has **every row** of the `<sec:regression_impact>` table of the plan appeared as a task — either as a `TREG` task in the closing group, **or** (if the file also appears in the `<sec:planned_changes>` section of the plan) **as a normal `Tnnn` task**? `TREG` is **by definition only for the files that are NOT in the `<sec:planned_changes>`** — do not duplicate what is there as a `TREG`. If the plan says there is no impact, this group may be missing.
- **Creating the files run by the `[CHECK]` commands:** go through the command of every `[CHECK]` task, and look at what **file or script it runs** (e.g. an integration test script, a runner wrapper, a seed script). For each of them it must hold that it **either already exists in the repo, or there is a task creating it earlier in the list**. A file to be run but created nowhere is a guaranteed failure — in that case add the missing creating task.
- **A promised test → a `[RED]` task:** if the plan **promises testing in prose** for something (typically in the "handling" sentences of `<sec:risks>`, e.g. *"we verify the fallback logic with a unit test"*), then a `[RED]` test-writing task has to appear **before** the `[GREEN]` task of that logic. A promise without a test task is a coverage gap.
- **Is `tasks-input-from-prev.md` closed? (IP1)** — If the file exists, no `[ ]` item may remain in it: each one is either incorporated into `tasks.md` (as a task or an ordering constraint), or explicitly dropped with a justification. Did whatever will only become relevant at the validation go into `validate-input-from-prev.md`?

### A/2) Markers and destructive operations

- **Artifact voice (AV1)?** — The task descriptions are active, concrete instructions to the implementer; there is no skill-voiced meta rule in them (`🔴`, "It is forbidden…", "the quality check fails if…") and there is no copied-over skill explanation.
- **A marker on every task:** there is no task without a prefix — every line bears a `[RED]`, `[GREEN]`, `[CHECK]` or `[OPS]` marker.
- **Is `[OPS]` used correctly?** — Go through the `[OPS]` tasks: **every one of them modifies an environment or an artifact, not a repo file.** If an `[OPS]` task edits a file path (typically the `TREG` regression tasks), that is a **wrong classification** → `[RED]`/`[GREEN]`. A mistaken `[OPS]` classification breaks the destructive-operation check.
- **Is the destructive / shared-environment operation complete?** — If there is an `[OPS]` task that modifies a **shared** environment (a shared cluster, a common registry, a shared database), does its group contain (a) an **approval-requesting** task that records the original state, (b) the operation, (c) a `[CHECK]` verification, (d) a conditional **rollback** task? If the plan gives no rollback scenario, that is a plan deficiency → `tasks-questions.md`.
- **Checking state persistence:** if a task references a shell variable (`$VAR`) that is set by **an earlier task**, that is **wrong** — the tasks run in separate shells, the value will be empty. The state is to be written into a file and read from there, or the commands are to be merged into one task. This is especially critical for the **rollback**: nothing is restored with an empty identifier.

### B) TDD correctness

- Does every `[RED]` task have a matching `[GREEN]` task, and does the RED precede the GREEN?
- **TDD obligation:** does every `[GREEN]` task implementing new/modified business logic have a `[RED]` (test-writing) task directly preceding it? (Except for non-TDD tasks, e.g. configuration, documentation.)
- Does every task follow the execution order of the plan?

### C) `[CHECK]` task quality

- Is there a `[CHECK]` task with a concrete command at the end of every logical group?
- **`[CHECK]` targeting:** does every `[CHECK]` task contain a targeted command (e.g. `npm test -- path/to/test.ts`), not the whole suite (`npm test`)? Running the regression and the full E2E is the task of the validate phase (07).
- **The relevance of the `[CHECK]`:** the closing `[CHECK]` task of the group verifies the modifications of that group — do not run the tests of another section as the closing check of a group. If there is no separate unit test for the code modified by the group (e.g. a proxy configuration, a mock server route), a typecheck or a build check is enough instead.
- **The correctness of the commands:** is every bash command (especially the relative paths after the `cd` commands appearing in the `[CHECK]` tasks) real and correct? Paths of the `../../` kind often jump out of the project root, avoid excessive stepping up, check the logic of the path!
- **No regression run in the tasks:** check that the tasks list contains no `[CHECK]` task RUNNING regression tests — that is the task of the validate phase.
- **`[CHECK]` command ↔ the report flags of `conventions.md`:** open the `## <sec:cv_test_reporting>` table of `conventions.md`, and compare it **row by row** with every `[CHECK]` command. If a mandatory report flag is prescribed for the given test level (e.g. `--alluredir=allure-results`, `--reporter=…`, `--junitxml=…`), it **must appear in the command**. A missing flag → the report gate of phase 07 (TR3) fails at the end of the cycle.
- **`⟂` parallelization validated:** at every `⟂ Tkkk` marking, the **file sets of the two tasks are disjoint**, and neither of them runs what the other writes. A `[CHECK]` is **never** parallel with the task writing/modifying its own test (a false green). If you cannot decide, **remove the `⟂`** — sequential execution is never wrong.
- **Browser E2E marker:** if a UI/browser E2E test-writing task stands AFTER the implementation, its marker is `[GREEN]` (or `[RED]` + a parenthesized justification) — there is no `[RED]` after the implementation in the order without a justification.

### D) Task granularity and preparation

- **Granularity:** is there a task that touches 3 or more files, or introduces complex logic? If yes, split it up.
- **Separating the preparatory steps:** go through every `[CHECK]`, `[RED]` and testing task — if any of them also contains a configuration or preparatory command (e.g. key generation, docker build, setting an env, copying a certificate), the preparatory step should go into a separate task that precedes the testing task.
- **Surfacing the machine-level prerequisites:** go through the `[CHECK]` tasks — if any of them requires a machine-level condition outside the standard runtime environment of the project (a machine-level env var, e.g. `KEYCLOAK_HOME`; installed external software; an external service running beforehand), this has to be lifted into the header of the logical group, in a blockquote. It has to contain: the concrete name of the env var + an example value; if the test starts an external service, the full start command with the critical flags (e.g. `kc.sh start-dev --features=token-exchange:v1`). A plan/spec reference on its own is not enough — the information has to be visible at the level of the task.
- **A genuinely containerized test run:** did you check whether the `[CHECK]` and integration/E2E test tasks added run against real, containerized services, instead of relying on native processes started manually on the developer machine?

### E) <sec:documentation_group> and TypeScript

- **The README of an existing component: it CANNOT be a task.** If the cycle changed the configuration of an existing component (env vars, startup parameters, external connections), updating `README.md` is the business of **`08-doc-sync`** — if such a task got in (typically as a `TLAST`), **delete it**. **Exception:** the first `README.md` of a **<status:op_new>** component, which belongs among the files of the component as a normal `Tnnn` `[GREEN]` task.
- **Is there no status-updating task?** — There is no task that switches the **status field** of `spec.md` / `plan.md` / `tasks.md`. That is the business of `07-validate` (framework machinery), not an implementation step. If the DoD of the spec asks for such a thing, that is a spec error → `tasks-questions.md`.
- **Architecture / generated documentation (DS4):** do **NOT** generate a task for updating `docs-generated/architecture.md` (or any file of `docs-generated/`), not even when introducing a new component/interface/data flow — these are owned **exclusively by the `08-doc-sync` phase**, which composes and validates them with an overview of the whole cycle. The implementation (06) concentrates on the code; the "as-built" documentation is produced in the doc-sync.
- **TypeScript rename check:** if the cycle renames a TypeScript interface, type or method name, check whether the `<sec:verification_strategy>` section of the plan contains a `typecheck` command for every affected npm package. If yes, add it as a [CHECK] task. If it does not appear in the plan, **do not invent it yourself** — the command may only get into a task if the plan lists it explicitly (the plan agent checks in package.json whether the script exists).
- **Rename completeness `[CHECK]`:** if the cycle replaces a name (an endpoint, a symbol, an env variable, a file name) **across the whole project**, the closing task of the <sec:documentation_group> group should be a `[CHECK]` that greps the **old name** in the whole repo in all of its variants (e.g. `init-cache`, `initCache`, `init_cache`, `InitCache`), excluding the paths marked as historical in the **<sec:out_of_scope>** of the spec (the `test-report`s of closed cycles, old `spec.md`s, the past entries of `roadmap.md`) and the `node_modules`/`.git` folders. The task is green if **zero** hits remain in the live source, in the documentation (root + app `README.md`, `docs/`, `.agent/`) and in the version-controlled build output (`dist/`). If `dist/` is version controlled, a clean rebuild (deleting `dist` + `npm run build`) should precede this, because `tsc`/vite does not delete the orphan output of the renamed source.
<!-- INCLUDE:shared/path-format.md -->
- **A task for the gate configuration (GC1):** if the plan schedules the modification of one of the sections of `conventions.md` (report artifacts/path base, Sonar, test commands, ports, merge strategy), is there a **separate task** for it with a `[GREEN]` marker (it edits a repo file, so not `[OPS]`)? Without it the gate of 07 runs with the old configuration.
- **The mechanical gate (M):** did `analyze-gate-check.py` run on the folder of the cycle, and did it return `0`? (The `<status:must_fix>` items are mechanically detected errors — they are to be fixed before the status change, not left to the loop of 05.)
