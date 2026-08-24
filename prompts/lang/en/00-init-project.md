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
- `09` — review & merge (review + merge according to the Merge strategy of conventions.md)

The folder of every cycle: `specs/cycle-NN-<cycle-name>/`

### Flow selection (default working mode)

Two flows can be chosen from in the project, **per task**:

- **Full flow (02–09):** for larger, complex tasks — separate `spec.md` / `plan.md` / `tasks.md` + the analyze/validate/doc-sync/review quality gates.
- **Simplified flow (`/bs-quick-flow`):** for small, well-bounded tasks (configuration, a simpler script, a smaller fix) — a three-phase `spec.md` → `task.md` → implementation.

**Default flow:** _<full | simplified>_ — _(filled in during phase 00 based on the character of the project; e.g. predominantly configuration/scripting/operations → simplified; product development with several components → full)_

The default is only the **starting point**, it can be overridden per task. If a given task does not fit the default flow, the agent says so and suggests the other one (see the flow-size check of `01-add-cycles` and `03-write-plan`, and the overgrowth signal of `/bs-quick-flow`). The decision to switch flows always belongs to the user.

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
  - Location of the test files: `test/` (in the subfolder matching the test structure of the project)
  - Python test dependencies: `requirements-test.txt` or the `pyproject.toml [test]` section
- **E2E infrastructure:** `docker compose` — a containerized full stack
  - E2E compose file: `docker-compose.e2e.yml` in the root of the project
- **Mock tools:** _to be filled in per project — which mock frameworks, servers and stub tools we use_

## Test reporting

_**Mandatory section (TR3).** The **own, openable report** of the project's test tool (Allure HTML, Playwright HTML, pytest-html, JUnit XML, coverage report, etc.) must get into the `specs/cycle-NN-<name>/test-report/` folder of every cycle — after a `/clear` the chat is gone, and the report is the only evidence that can be checked afterwards. `07-validate` enforces this table with a **deterministic gate** (`report-gate-check.py`): a missing artifact → the validation cannot be closed as PASS. The column order is fixed._

_**Where they go (TR5):** the reports do not go directly into the root of `test-report/`, but into **per-round subfolders** — `test-report/validate/round-01/`, `round-02/`, … for the validation rounds (the review is step 2 of the round of 07, it does not get a separate folder). This way every round of a self-healing loop keeps its own evidence, and the report belonging to a failure marked in the step table of `validation-report.md` can be opened. **The last column of the table is a path relative to the ROUND FOLDER** (a file or a folder) — the round folder is handed to the `test-runner` and to the gate by the calling phase (`--report-subdir`)._

**Report generation required:** yes
**Artifact path base:** round-folder

_**The marker is mandatory (TR5/b).** The meaning of the last column changed on 2026-08-07 (`test-report/` root → **round folder**), but its format did not — an old table would therefore be silently misinterpreted. In the absence of the marker, `report-gate-check.py` **does not guess**: `exit 2` + the line to be added. Accepted values: `round-folder` (today's scheme) or `test-report` (the old, flat scheme — in which case the gate resolves the paths to the root of `test-report/`). Migration of an existing project: write in the marker with the real scheme, and if the cycle is switching to today's scheme now, rewriting `conventions.md` is **part of the cycle** (see the "The gate configuration moves together" rule of 03)._

_**The boundary towards `specs/test-conventions.md` (TC1/c):** the **report artifacts, their path base and the report-generating commands** belong here, into `conventions.md` — this is what the TR3 gate reads. The **test recipes and coordinates** (how the stack starts, which call, which test user) belong into `specs/test-conventions.md`, which 08-doc-sync maintains. The report layout or a report command changes → **`conventions.md`**; "how it runs / what it needs" changes → **`test-conventions.md`**; if both → **both**. Mixing the two up is the most frequent source of the gate of 07 looking in the old place._

| Test category | Tool | Report-generating command | Artifact in the round folder |
|---|---|---|---|
| E2E | Playwright (+ Allure) | `npx playwright test --reporter=html && npx allure generate ./allure-results --single-file -o ./allure-report` | `allure-report.html` |
| Unit / integration | _the chosen runner_ | `<report-generating command>` | `unit-report.html` |
| Coverage | _e.g. c8 / coverage.py_ | `<command>` | `coverage/` |

_Rules for filling it in:_
- **Prefer a single-file HTML** (`allure generate --single-file`, `--reporter=html` into one file), because the report goes into the git diff of the cycle. If the tool can only produce a folder (e.g. a full Allure static site), that is acceptable too — then the folder name should end with `/` (`allure-report/`).
- If there is no report artifact for a category, `-` goes into the last column (the gate skips that row).
- **If the project does not generate a test report at all**, set the flag above to `no`, **with a justification** (e.g. "there is only a manual smoke test"). This is a conscious, recorded decision — the gate is then skipped. Leaving it empty or leaving an unfilled table is **not** an option: the gate then reports a usage error.

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

<!-- ANCHOR:BD9-api-guideline-kerdes -->
*"Is there an API design guideline / API policy to follow (REST conventions, versioning, error format, naming)? If yes, where is its document?"*

<!-- ANCHOR:zaro-uzenet -->
   *"The project conventions are recorded. Before starting the next phase, be sure to run a `/clear` command to empty the context, then cycle management can begin: `/bs-add-cycles`."*
