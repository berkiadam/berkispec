<!--
  The PROJECT-LANGUAGE blocks of `00-init-project` (9.4 extraction).
  The installer inlines this file at build time in place of the INCLUDE markers,
  according to the chosen PROJECT language (`PROJECT_LANG`); the marker form is
  `lang/00-init-project.md#<anchor>`.
  The blocks were moved here VERBATIM — do not rephrase, do not unify.
  The ANCHOR lines are NOT part of the inlined text, they are delimiters only.
  The delimiter is an HTML comment and not a `##` heading because the templates
  themselves are full of `##` headings (8.9).
  CAUTION: no comment-closing sequence may appear in this leading note.
-->

<!-- ANCHOR:conventions-sablon -->

# Project conventions

## Project overview

_The goal of the project in one or two sentences. What is the task of the system?_

## Tech stack

- **Language:**
- **Runtime:**
- **Framework:**
- **Package manager:**
- **Build tool:**
- **Containerization:**

## Project references

During development and doc-sync (08), the global design, API and external reference documents below are authoritative. The agent must take them into account when planning cycles and when comparing the generated documentation for drift:

- **HLD (High Level Design):** _(e.g. docs/design/hld.md, or leave it empty)_
- **LLD (Low Level Design):** _(e.g. docs/design/lld.md, or leave it empty)_
- **API specification / API descriptors:** _(e.g. docs/api/openapi.yaml, or leave it empty; if it is filled in, the DS22 Layer 2 check of 08-doc-sync compares the generated interface/endpoint inventory against it)_
- **API design guideline / API policy (BD9):** _(e.g. docs/api/guidelines.md or a URL, or leave it empty — REST conventions, versioning, error format, naming. Phases 02–03 work from this. **For a large document**, do not put the full text here: a pointer + a concise rule checklist prepared with the `researcher` — BD10.)_
- **Database schema:** _(e.g. docs/db/schema.sql, or leave it empty)_
- **External / business reference documents:** _(e.g. docs/poc.md, vendor documentation, business process descriptions, or leave it empty)_
- **Branching policy (BD8/BD10, if it is a large document):** _(pointer + excerpt; a small branching rule rather goes verbatim into `## Git and branching conventions`)_

## Project structure

_The root-level folders and their role. For example:_

- `src/` — main application source code
- `apps/` — standalone subcomponents
- `test/` — tests (see the details below)
- `docs/` — documentation, OpenAPI descriptors
- `specs/` — development cycle specifications

## Development methodology

Spec-driven development. Development is split into cycles. The workflow consists of two one-off setup steps and an 8-step per-cycle loop:

**Setup (once):**
- `00` — project initialization
- `01` — cycle management (`specs/roadmap.md`)

**Per-cycle loop:**
- `02` — spec (`specs/cycle-NN-<cycle-name>/spec.md`)
- `03` — plan (`specs/cycle-NN-<cycle-name>/plan.md`)
- `04` — tasks (`specs/cycle-NN-<cycle-name>/tasks.md`)
- `05` — analyze (cross-phase consistency check)
- `06` — implement (code + updating `tasks.md`)
- `07` — validate (running the tests and checking the DoD)
- `08` — doc-sync (updating `docs-generated/` and the consistency gate)
- `09` — review & merge (according to the `## Review and merge` section: `09` in a single step — or `09a` create-pr → `09b` review → `09c` merge when a PR is submitted; optionally `09d` dev-test)

The folder of every cycle: `specs/cycle-NN-<cycle-name>/`

### Flow selection (default working mode)

Two flows can be chosen from in the project, **per task**:

- **Full flow (02–09):** for larger, complex tasks — separate `spec.md` / `plan.md` / `tasks.md` + the analyze/validate/doc-sync/review quality gates.
- **Simplified flow (`/bs-quick-flow`):** for small, well-bounded tasks (configuration, a simpler script, a smaller fix) — a three-phase `spec-plan.md` → `tasks.md` → implementation.

**Default flow:** _<full | simplified>_ — _(filled in during phase 00 based on the character of the project; e.g. predominantly configuration/scripting/operations → simplified; product development with several components → full)_

The default is only the **starting point**, it can be overridden per task. If a given task does not fit the default flow, the agent says so and suggests the other one (see the flow-size check of `01-add-cycles` and `03a-write-code-plan`, and the overgrowth signal of `/bs-quick-flow`). The decision to switch flows always belongs to the user.

## Git and branching conventions

- **Version control:** _(git | "NO version control (neither GIT nor anything else), and none is planned." — BD11)_ — if the "NO" flag is written in, phases 00/01 and 02–09 **skip every git step** (no branch, no warning, no commit).
- **Main branch:** `main` — the base the cycle branches are cut from (BD2). _(A project may differ, e.g. `master`; the branch logic reads this field.)_
- **Cycle branch:** every development cycle lives **on its own branch**, cut from `main` (BD1–BD2). The branch contains the `specs/`, `docs/` and `src/` changes alike.
- **Opening the branch:** it is created **in the cycle management phase (01)**, at the very beginning of the cycle (not in 02/06); the 00 init itself runs on the `feature/init-project` branch (BD12).
- **Branch naming strategy (BD8):** _(default: `feature/cycle-NN-<name>`; if there is a Jira prefix / another organizational rule / a pointer to a document, it goes here)_ — the **folder name** is always without a prefix regardless of this, plainly `cycle-NN-<name>` (BD3).
- **Merge / back-integration:** according to the `## Merge strategy` section (PR or direct merge; if there is no decision/remote, the default is the direct merge — BQ7), after the successful run of 09; the same section also governs the back-integration of the 00 init branch (BD7/BD15).
- **Commit granularity:** one commit per task.

## Merge strategy

_The agent uses this when closing the cycle (phase 09). It has to be clarified in phase 00, and the access has to be **tried out** — `conventions.md` cannot be closed until we successfully reach the chosen provider (or the user chooses an alternative / a local merge)._

_**A single source of truth for back-integration (BD15):** this section states how **any** finished branch gets back into `main` — the cycle branch (09), the 01/00 branch warning (BD6), and the back-integration of the own `feature/init-project` branch of 00 (BD12) all work from this. If there is no explicit decision or remote, the **default is the direct merge into `main`** (not a PR — BQ7)._

- **Provider:** GitHub | Bitbucket Cloud | Bitbucket Server | GitLab | Local (no PR)
- **Repository URL:** _(for Bitbucket on-prem, the API endpoint as well)_
- **Authentication:** CLI (`gh` / `glab` / `bb`) | token (env var name) | SSH
- **PR target branch:** _(`master` by default)_
- **Merge type:** squash | merge commit | rebase
- **Branch protection:** _(if any — e.g. CI check, review requirement)_
- **Access test command:** _(example — see below)_

_Access validation per provider (phase 00 runs it, a successful exit/HTTP 200 is required):_
- _GitHub: `gh auth status` + `gh repo view <repo>`_
- _Bitbucket Cloud: `curl -u <user>:<token> https://api.bitbucket.org/2.0/repositories/<ws>/<repo>` → HTTP 200_
- _Bitbucket on-prem: `curl -u <user>:<token> <api-url>/rest/api/1.0/projects/<key>/repos/<repo>` → HTTP 200_
- _GitLab: `glab auth status` + `glab repo view <repo>`_
- _Local: there is no validation_

## Review and merge

_**This section drives the last phase of the cycle (RM8):** is there a PR, where the review and the merge run, is there a post-merge test round (`VP2`), is there a dev-deployment e2e round (`VP3`), what happens on a failure, and what the CI calls. **The section name, the field names and the values are English literals** — a machine reads them, so they are language-independent (the same rule as for the `[local]`/`[remote]` labels and the test category identifiers); the explanatory prose stays in the project language._

- **PR submission:** yes | no
- **SDD mode:** isolated | centralized
- **Post-merge tests:** yes | no
- **Skip post-merge tests if master unchanged:** yes | no
- **Dev deployment test (bs-dev-test):** yes | no | n/a
- **Dev deployment command:** _(only if `Dev deployment test` is `yes` — the verbatim command that performs the deployment)_
- **Failure handling:** notify | auto-fix-loop
- **Notification channel:** slack | teams | command | none
- **Notification secret (env var):** BS_NOTIFY_WEBHOOK
- **Notification command:** _(only if the channel is `command`)_
- **CI agent:** claude-code | cursor | copilot | antigravity | command
- **CI agent command:** _(only if `CI agent` is `command`)_

_**Which skill runs — `PR submission` decides, not `SDD mode`:**_
- _`no` → a **single** skill: `/bs-review-and-merge` (09)._
- _`yes` → **three** skills: `/bs-create-pr` (09a) → `/bs-review` (09b) → `/bs-merge` (09c)._
- _`Dev deployment test: yes` → one more phase after the merge: `/bs-dev-test` (09d)._

_**Post-merge tests (`VP2`).** The round runs on the **cycle branch**: first we bring the main branch into the cycle branch, then the test round builds and runs on the code merged with the fresh `main`, and **only after a green result** comes the merge (isolated path) or the push (centralized path). **Which** tests run in it is stated by the `Phase` column of the machine run table of `plan.md` (the `post-merge` value) — in a quick-flow cycle by the `## Merge tests` section of `spec-plan.md`. The round also runs the **static layer** (Sonar, with the same thresholds as `07`), because the merge brings in code the Sonar round of `07` never saw. The evidence goes into the `test-report/post-merge/` folder of the cycle — on success and on failure alike._

_**Skip post-merge tests if master unchanged.** If the main branch has not moved ahead since the cycle branched off, the `VP2` round would measure exactly what `07` has just measured. With `yes` the round may be skipped in that case (the fact and the reason of the skip go into the report); with `no` it always runs._

_**Dev deployment test (`VP3`).** It only makes sense with `SDD mode: centralized`: after a successful merge an automation deploys the product into a fully integrated test environment (`Dev deployment command`), and real e2e tests run against it. Test selection is the `dev-test` value of the `Phase` column; the detailed environment recipe (compose, mocks, test data) belongs into `specs/test-conventions.md` (TC1/c). The evidence goes into the `test-report/dev-test/` folder of the cycle._

_**Failure handling.** `notify` (the default): the report goes onto the path of the cycle, `notify.py` notifies the developer, and a **human** starts the fix. `auto-fix-loop`: a self-healing loop starts on the CI, with the unchanged stopping limits of the loop of `07` (per item 3 consecutive / 5 total failures, 5 consecutive FAIL runs, then escalation to a human)._

_**Notification.** The secret lives **exclusively in an environment variable**, only the NAME of the variable goes into the section (the same rule as in the `Authentication: token (env var name)` field of `## Merge strategy`) — a webhook URL passed as a command-line argument would leak into the transcript, into `check-log.md` and into the CI log as well. `none` is a **legitimate, explicit answer** (a one-person PoC), but not one that follows from silence. Email gets no separate backend: the `command` value covers it (`msmtp`, `sendmail`, a company script), just as it covers Jira or PagerDuty._

_**CI agent.** On the centralized path the CI calls the `ci-run-skill.sh <skill> <cycle-path>` adapter, which starts the agent named here in non-interactive mode. **The agent is clarified in advance and also tried out** (`ci-run-skill.sh --selftest`), exactly like the access of the merge provider: a non-interactive run that turns out not to work first on a live PR fails in the worst possible place. **🔴 Measured (2026-09-22): the `antigravity` branch is not usable on a CI** — its CLI 1.107.0 is an editor application with no headless mode; the selftest states this too. In that case use `CI agent: command` (the platform's own event-driven PR integration, or any other command)._

_**Validity rules** (00 checks them at write time, because a configuration error is cheaper to catch there than at the end of every cycle):_
- _`SDD mode: centralized` + `PR submission: no` → **rejected** (the centralized path is PR-triggered by definition);_
- _`Dev deployment test: yes` + `SDD mode: isolated` → **rejected** (`VP3` only makes sense on the centralized path);_
- _with `Dev deployment test: yes` the `Dev deployment command` is **mandatory**;_
- _with `Notification channel` ≠ `none` the `Notification secret (env var)` is **mandatory**;_
- _with `Notification channel: command` the `Notification command`, with `CI agent: command` the `CI agent command` is **mandatory**;_
- _**In a no-VCS project the whole section is `n/a`**, and the cycle closes after `08-doc-sync` — none of `bs-review-and-merge` / `bs-create-pr` / `bs-review` / `bs-merge` / `bs-dev-test` runs._

## Test structure

```
test/
  unit/          — isolated function tests, every dependency mocked, fast
  integration/   — component-level tests, external HTTP/service boundaries mocked
  e2e/           — the whole system runs, with real or realistic mock services
  performance/   — load and stress tests, separate tooling
  mocks/         — reusable mock servers, test doubles, fixtures
  helpers/       — helper functions shared between tests, report generators
```

### Testing principles

- A unit test is mandatory for new business logic.
- An integration test is mandatory for a new API endpoint or service integration.
- An e2e test is mandatory for a new complete process (at user story level).
- Mock servers go into the `test/mocks/` folder, in a reusable form.
- Every test suite can be run on its own and is stateless after cleanup.

## Test framework

_The following are **recommended defaults** with modern, up-to-date tools (for local developer use). They are not mandatory: in phase 00 the agent asks about them explicitly in one round — "The suggested test stack: <default>. Is it suitable, or would you like something else (e.g. Cypress, Jest, Vitest, go test)?" — and records the developer's decision. From then on this section is the single source of truth: phases 03/07 reference it, they do not repeat the tool name._

- **Frontend E2E:** Playwright _(recommended — alternative: Cypress)_
- **Backend tests:** Python — `pytest` + `httpx` _(recommended — alternative: the native framework of the project's language, e.g. Jest/Vitest for Node, go test for Go)_
  - Location of the test files: `test/` (in the subfolder matching the test structure of the project) — _information for a human; the per-category globs of the **machine discovery** are given by the `### Test file locations` table of the `## Test execution` section (RP1: do not duplicate a value here)_
  - Python test dependencies: `requirements-test.txt` or the `pyproject.toml [test]` section
- **E2E infrastructure:** `docker compose` — a containerized full stack
  - E2E compose file: `docker-compose.e2e.yml` in the root of the project
- **Mock tools:** _to be filled in per project — which mock frameworks, servers and stub tools we use_

## Test reporting

_**Mandatory section (TR3).** The **own, openable report** of the project's test tool (Allure HTML, Playwright HTML, pytest-html, JUnit XML, coverage report, etc.) must get into the `specs/cycle-NN-<name>/test-report/` folder of every cycle — after a `/clear` the chat is gone, and the report is the only evidence that can be checked afterwards. `07-validate` enforces this table with a **deterministic gate** (`report-gate-check.py`): a missing artifact → the validation cannot be closed as PASS. The column order is fixed._

_**Where they go (TR5):** the reports do not go directly into the root of `test-report/`, but into **per-round subfolders** — `test-report/validate/round-01/`, `round-02/`, … for the validation rounds (the review is step 2 of the round of 07, it does not get a separate folder). This way every round of a self-healing loop keeps its own evidence, and the report belonging to a failure marked in the step table of `validation-report.md` can be opened. **The last column of the table is a path relative to the ROUND FOLDER** (a file or a folder) — the round folder is handed to the `test-runner` and to the gate by the calling phase (`--report-subdir`)._

**Report generation required:** yes
**Artifact path base:** round-folder
**Report phases:** validate
**Test manager:** none
**Test manager shape:** —
**Test manager token env var:** —
**Test manager phases:** dev-test
**Test manager required:** no
**Test manager command:** —

_**Report phases (TR6).** The field lists WHICH phases are required to produce the artifact set above: `validate` (the full rounds of 07 — this is the default), `implement` (the closing state of 06), `post-merge` (the `VP2` round after the merge) and `dev-test` (the `VP3` round of `/bs-dev-test`) — as a comma-separated list (`implement, validate, post-merge`). If `implement` is also listed, 06-implement generates the set into the `test-report/implement/` phase folder before the status change, and the same `report-gate-check.py` closes it. If not, 06 only writes `check-log.md`, and the evidence comes from the first FULL round of 07. **The `post-merge` and `dev-test` phases are switched on by the `## Review and merge` section** (`Post-merge tests`, `Dev deployment test`); if they are on there, they have to be listed here too, otherwise `report-gate-check.py` does not look for the artifacts of the round. The behavior of an old project without the field is unchanged (`validate`). **When is `implement` worth it?** If the implementation run has evidence value of its own (browser screenshots, REST audit logs, long E2E runs) that the round of 07 no longer reproduces in the same state._

_**The marker is mandatory (TR5/b).** The meaning of the last column changed on 2026-08-07 (`test-report/` root → **round folder**), but its format did not — an old table would therefore be silently misinterpreted. In the absence of the marker, `report-gate-check.py` **does not guess**: `exit 2` + the line to be added. Accepted values: `round-folder` (today's scheme) or `test-report` (the old, flat scheme — in which case the gate resolves the paths to the root of `test-report/`). Migration of an existing project: write in the marker with the real scheme, and if the cycle is switching to today's scheme now, rewriting `conventions.md` is **part of the cycle** (see the "The gate configuration moves together" rule of 03)._

_**The boundary towards `specs/test-conventions.md` (TC1/c):** the **report artifacts, their path base and the report-generating commands** belong here, into `conventions.md` — this is what the TR3 gate reads. The **test recipes and coordinates** (how the stack starts, which call, which test user) belong into `specs/test-conventions.md`, which 08-doc-sync maintains. The report layout or a report command changes → **`conventions.md`**; "how it runs / what it needs" changes → **`test-conventions.md`**; if both → **both**. Mixing the two up is the most frequent source of the gate of 07 looking in the old place._

| Test category | Tool | Report-generating command | Artifact in the round folder |
|---|---|---|---|
| E2E | Playwright (+ Allure) | `npx playwright test --reporter=html && npx allure generate ./allure-results --single-file -o ./allure-report` | `allure-report.html` |
| Unit / integration | _the chosen runner_ | `<report-generating command>` | `unit-report.html` |
| Coverage | _e.g. c8 / coverage.py_ | `<command>` | `coverage/` |
| Application-side audit / REST request-response | _the service's own log writing_ | _a by-product of the test run — the command is turning the logging on_ | `e2e/rest-logs/` |

_Rules for filling it in:_
- **Prefer a single-file HTML** (`allure generate --single-file`, `--reporter=html` into one file), because the report goes into the git diff of the cycle. If the tool can only produce a folder (e.g. a full Allure static site), that is acceptable too — then the folder name should end with `/` (`allure-report/`).
- If there is no report artifact for a category, `-` goes into the last column (the gate skips that row).
- **🔴 The REST logs go into PER-TEST subfolders:** `<artifact>/<local|remote>/<test-name>/`. The `local`/`remote` level is **language-independent**, and follows from the **test's own marking** (not from the address called — a `127.0.0.1` behind an `oc port-forward` is **remote**, while a compose service name is **local**). The test name is the name of the test function, normalized to be path-safe: **every `[^A-Za-z0-9._-]` character to `-`, leading and trailing `-` trimmed, NO lowercasing** (`test_foo[dsp01]` → `test_foo-dsp01`; the parameter does **not** become a separate subfolder). The gate of `07` (`RL1`/`RL2`) joins on this structure: it checks whether the logs under `remote/` really contain a non-local address, and whether every scenario marked `[remote]` produced a log at all. Without it the log is **one flat heap** from which it cannot be established afterwards which test called what — and a folder full of files inherited from an earlier round **looks full**. _(The artifact cell of the TR3 table does NOT change — it stays `e2e/rest-logs/`; the new levels go BELOW it, and `report-gate-check.py` walks the folder with `rglob`, so it sees the nested structure without any change.)_
- **Application-side evidence is a TABLE ROW too, not prose.** Whatever is produced during the test run and can be opened afterwards — a REST request/response audit log, a correlation-id trace, an application log excerpt — put it into the table just like the report of the test tool. What the table does not ask for, `report-gate-check.py` **does not look for**: it is silently omitted, and its absence only surfaces months later. The file name and header convention is recorded in `specs/test-conventions.md` (TC1/c), but **whether it is mandatory** belongs here.
- **If the project does not generate a test report at all**, set the flag above to `no`, **with a justification** (e.g. "there is only a manual smoke test"). This is a conscious, recorded decision — the gate is then skipped. Leaving it empty or leaving an unfilled table is **not** an option: the gate then reports a usage error.

_**Test manager integration (TM1–TM10) — optional, OFF by default.** The framework does not prescribe an external test manager: with `Test manager: none` there are zero new steps and zero new network dependencies. The committed `test-report/` set remains **the only** cycle evidence; the test manager is the **other axis** — cross-cycle trends, flaky detection, grouping failures by cause — which git cannot preserve. **The upload is never evidence** (TM7): `report-gate-check.py` rejects a report set that contains a URL but not the requested artifact, exactly as it does today._

_**What the fields mean:**_
- _`Test manager`: `none` (default) · `testdino` · `reportportal` · `qase` · `command` — which adapter runs. With `none` the other fields may be left out._
- _`Test manager shape`: `reporter` (the client runs in the reporter chain of the test runner and streams during the run — e.g. TestDino) or `import` (a command pushes the finished `junit.xml` afterwards — e.g. ReportPortal, Qase). The two shapes are not interchangeable._
- _`Test manager token env var`: the **NAME** of the variable, never its value — a test manager API token is a shared platform credential (TC5) and must never go into `conventions.md`. `test-manager.py` reads it from the environment itself and **never receives a token on the command line**._
- _`Test manager phases`: a comma-separated list — `implement` · `validate` · `post-merge` · `dev-test` · `ad-hoc`. **Default: `dev-test`**, because the `VP3` round produces the most valuable data, while `07` (`VP1`) must not become token- and network-dependent: that would break the isolated SDD mode. `ad-hoc` covers the out-of-cycle `/bs-run-tests` runs — their metadata carries `cycle=none`, so the `D8`/`KT6` evidence firewall is visible at the provider as well._
- _`Test manager required`: `yes` · `no` (default) — should a failed upload fail the phase. By default **no**: if the evidence is already committed, a 502 from a SaaS must not invalidate a green test round. The result never stays unmarked though: an `uploaded <url>` / `FAILED <reason>` / `skipped (<phase> not listed)` line goes into the report of the round and into `results.json`._
- _`Test manager command`: a verbatim command line, **only** for the `command` provider — this connects TestRail, Xray, Allure TestOps or anything else without modifying the framework._

_**A filled example (TestDino, `reporter` shape):** `Test manager: testdino` · `Test manager shape: reporter` · `Test manager token env var: TESTDINO_TOKEN` · `Test manager phases: dev-test` · `Test manager required: no`. Writing the reporter block into the `playwright.config.ts` of the project is **the project's job** (the framework does not touch it), and the recipe belongs into `specs/test-conventions.md` (TC1/c). ⚠ The TestDino `reporter` package requires **Node ≥ 22.12**: on an older Node it does not even load, and it kills the whole test run with it — this is why `test-manager.py --mode preflight` probes the **loadability** of the reporter, not just the presence of the env var._

## Test execution

_**Mandatory section (KT1).** This section is the single machine-readable source of truth for **out-of-cycle** test execution: the `/bs-run-tests` helper command reads from it which category to run with which command, and the test inventory of `08-doc-sync` (`docs-generated/test-description.md`) discovers from it which test files exist. **Cycle**-level execution is still given by the machine-readable run table of `plan.md` (TP4) — the two do not replace each other: this section is project-level and cycle-independent, while that one is about one round of one cycle._

**Test categories:** unit, rest-e2e, ui

_The category dictionary of the project, listed with commas (recommended baseline: `unit` · `rest-e2e` · `ui`, optionally `coverage`). The `Category` values of the machine-readable run table of `plan.md` must be **subsets** of this set — this is checked by the mechanical gate of `05-analyze` (KT2). The category identifiers are **language-independent** (they join onto paths and gates: `test-runs/<category>/…`), so do not translate them._

### Project-level run table

_The column schema is **identical** to the machine-readable run table of `plan.md` (TP4/b) — one parser, one rule. `run-tests.py` reads with FIXED column positions, so the first column is always `Category`, and the order cannot be swapped. The values of the `Type` column (`gyors` / `nehez`) are the language-independent values of the script's `--type` flag — they are not translated._

| Category | Type | Prerequisite | Command | Result file | Format | Cleanup | Environment | Phase |
|---|---|---|---|---|---|---|---|---|
| unit | gyors | — | `<verbatim command, with a machine-readable reporter>` | `junit.xml` | junit | — | local | — |
| rest-e2e | nehez | `<the reachability probe of the target>` | `<command with the target host>` | `<file>` | junit | `<teardown>` | `<remote — the name of the target environment>` | — |

_Filling rules:_
- **The `Phase` column is `—` here:** this is an **explicit marker** ("not phase-bound"), not an empty cell and not a silent default — an out-of-cycle run has no phase. `/bs-run-tests` calls the script without a phase filter, so that branch of the filter does not even run. **In the machine table of `plan.md` an empty cell is an ERROR though** (PH1): there every row carries an explicit, comma-separated list (`implement`, `validate`, `post-merge`, `dev-test`).
- **The `{round}` and `{phase}` placeholders work here too:** `/bs-run-tests` passes the `test-runs/…` run folder as `--round-dir`, so `{round}` resolves to that — not to a cycle folder.
- **The EV rules apply:** the command of a `remote` environment row contains the target host **literally** (EV3), and there is a `Prerequisite` probe to the same target for it (EV4); `localhost` / `127.0.0.1` without a declared port-forward is **FORBIDDEN** (EV5). `run-tests.py` measures this at runtime as well (`exit 4`).

### Test file locations

_The globs of the **machine discovery**, per category. This is the single input of `test-inventory-check.py` (LD5), and this is the **only regulated place** where the scope of the test inventory can be narrowed: what is not declared here is not looked for by the inventory gate either._

| Category | Glob |
|---|---|
| unit | `test/unit/**/test_*.py` |
| rest-e2e | `test/e2e/**/*.spec.ts` |
| ui | `test/ui/**/*.spec.ts` |

_The prose "Location of the test files" line of the `## Test framework` section speaks to a **human** and stays — but it does not duplicate a value: the machine-read globs live **only here** (RP1: one concept, one place). If a category has no test file, `—` goes into the `Glob` cell; the category still stays part of the dictionary._

## Naming conventions

- **Files:** `kebab-case`
- **TypeScript classes:** `PascalCase`
- **Functions, variables:** `camelCase`
- **Environment variables:** `UPPER_SNAKE_CASE`
- **Unit test files (TypeScript):** `<module>.test.ts`
- **Unit test files (Python):** `test_<module>.py`
- **E2E scripts:** `cycle-NN-<description>.sh`

## Ports and services

_The ports of the application's components. For example:_

| Component | Port |
|-----------|------|
|           |      |

## Environment variables

_The location of the project-level `.env` file and the list of the mandatory variables._

## Sonar quality check

_(Skip this section if the project does not use SonarQube.)_

- **Starting the Sonar server (Podman):** `podman run -d --name sonarqube -p 9000:9000 docker.io/library/sonarqube:community`
- **Running the scanner:**
  - TypeScript/JavaScript: `podman run --rm --network=host -v ".:/usr/src" docker.io/sonarsource/sonar-scanner-cli -Dsonar.projectKey=<project-key> -Dsonar.host.url=http://localhost:9000 -Dsonar.token=<token>`
  - Java (Maven): `mvn sonar:sonar -Dsonar.host.url=http://localhost:9000 -Dsonar.token=<token>`
  - _(further languages: fill in the scanner command adjusted to the structure of the project)_
- **Project key (`sonar.projectKey`):** _fill in with the identifier of the project_
- **Sonar host URL:** `http://localhost:9000` _(`sonar-gate.py` queries the Quality Gate from here through the API)_
- **Token env variable:** `SONAR_TOKEN` _(NEVER write the token here — only the name of the variable; `sonar-gate.py` also accepts the `SONAR_HOST_URL` / `SONAR_PROJECT_KEY` / `SONAR_TOKEN` env variables)_
- **Quality Gate expectation:** PASSED — it blocks in the `07-validate` phase until it is fulfilled. The gate is evaluated by `sonar-gate.py` from the API (QG status + failed conditions + BLOCKER/CRITICAL/MAJOR findings), not by an LLM reading the report
- **Location of the Sonar report:** the folder of the validation round — `specs/cycle-NN-<cycle-name>/test-report/validate/round-NN/sonar-report.md` (+ `.html`); it is generated automatically during validation, separately per round (TR5)

## Risks and known limitations

_Project-level technical limitations, accepted POC boundaries._

<!-- ANCHOR:BD11-vcs-kerdes -->
*"Is there version control (git) in the project? If not, are you planning to introduce it?"*

<!-- ANCHOR:BD11-nincs-vcs-flag -->
"NO version control (neither GIT nor anything else), and none is planned."

<!-- ANCHOR:flow-kerdes -->
*"What kind of tasks will there predominantly be in this project? (a) Product development / new features, complex logic touching several components → **the full berki spec flow** (02–09); (b) Configuration, scripting, operations, smaller fixes → **the simplified flow** (`/bs-quick-flow`). This will be the default working mode; it can be overridden per task."*

<!-- ANCHOR:teszt-stack-kerdes -->
*"The suggested test stack: <default>. Is it suitable, or would you like something else?"*

<!-- ANCHOR:TR3-riport-kerdes -->
*"What report does your test tool generate, and with which command? (e.g. Allure HTML, Playwright HTML report, pytest-html, JUnit XML, coverage) — this gets into the `specs/cycle-NN-<name>/test-report/` folder in every cycle — into per-round subfolders —, and the validation checks its presence with a deterministic gate."*

<!-- ANCHOR:KT1-futtatas-kerdes -->
*"Which test categories does the project's test suite break down into (e.g. `unit`, `rest-e2e`, `ui`, `coverage`), with which **verbatim command** do I run each category over the whole project, and where are the test files of the category (glob)? This is used by out-of-cycle execution (`/bs-run-tests`) and by the discovery of the test inventory — cycle-level execution is still given by the table of `plan.md`."*

<!-- ANCHOR:KT7-gitignore-felajanlas -->
> *"The `test-runs/` folder is currently not excluded from version control. The out-of-cycle test runs of `/bs-run-tests` write here: machine-dependent results, regenerable at any time, which do not count in the evidence logic of the framework anyway (D8). I recommend adding the `test-runs/` entry into `.gitignore`. Should I add it?"*

<!-- ANCHOR:BD9-api-guideline-kerdes -->
*"Is there an API design guideline / API policy to follow (REST conventions, versioning, error format, naming)? If yes, where is its document?"*

<!-- ANCHOR:RM8-review-merge-kerdes -->
*"How does a cycle close in this project? (a) **Is there a PR submission**, or does the cycle branch go back into the main branch directly, on your machine? (b) Do the review and the merge run **on your machine** (isolated SDD), or does the PR trigger the CI/CD and run there **without human intervention** (centralized SDD)? This decides whether a single skill runs at the end of the cycle (`/bs-review-and-merge`) or three (`/bs-create-pr` → `/bs-review` → `/bs-merge`)."*

<!-- ANCHOR:VP2-post-merge-kerdes -->
*"Should there be a **post-merge test round** (`VP2`)? It runs on the cycle branch after we bring in the fresh main branch, and **before the merge** it proves that the code also works according to the spec when merged with master (tests + Sonar). If yes: **may it be skipped** when the main branch has not moved ahead since the cycle branched off? And on the centralized path, should a **dev-deployment e2e round** follow (`/bs-dev-test`, `VP3`) — if yes, with which command do we deploy into the dev environment?"*

<!-- ANCHOR:CS6-ertesites-kerdes -->
*"If the post-merge or the dev-test round fails, **how should the developer be notified**? (`slack` / `teams` / a free `command` / `none`.) The secret never goes into `conventions.md` — only the NAME of the environment variable. `none` is a legitimate answer in a one-person project, but it has to be an **explicit** answer, not silence. And what should happen on a failure: `notify` (a human fixes it) or `auto-fix-loop` (a self-healing loop starts on the CI)?"*

<!-- ANCHOR:CI-agent-kerdes -->
*"On the centralized path, **which agent runs on the CI** (`claude-code` / `cursor` / `copilot` / `antigravity` / a free `command`)? `claude-code`, `cursor` and `copilot` can be called in non-interactive (print) mode; **`antigravity` cannot** — its CLI (1.107.0) is an editor application, a prompt opens a GUI chat session, so it does not run on a CI runner without a display: there the `command` branch is the honest answer. Beyond that, authentication (API key, cost) and the permission model differ per platform as well — this is why we try it out right now."*

<!-- ANCHOR:TM3-test-manager-kerdes -->
*"Do you use an **external test manager** (TestDino, ReportPortal, Qase, TestRail, Xray …) where test results are collected across cycles? This is **optional and off by default** (`none`) — the evidence of the cycle remains the committed report, the test manager adds the trend and flaky data. If yes: which provider, and does its client go into the **reporter chain** of the test runner (`reporter`), or does a command **push the finished `junit.xml` afterwards** (`import`)?"*

<!-- ANCHOR:zaro-uzenet -->
   *"The project conventions are recorded. Before starting the next phase, be sure to run a `/clear` command to empty the context, then cycle management can begin: `/bs-add-cycles`."*
