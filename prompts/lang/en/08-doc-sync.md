<!--
  The PROJECT-LANGUAGE blocks of `08-doc-sync` (9.4 extraction).
  The installer inlines this file at build time in place of the INCLUDE markers,
  according to the chosen PROJECT language (`PROJECT_LANG`); the marker form is
  `lang/08-doc-sync.md#<anchor>`.
  The blocks were moved here VERBATIM — do not rephrase, do not unify.
  The ANCHOR lines are NOT part of the inlined text, they are delimiters only (8.9).
  CAUTION: no comment-closing sequence may appear in this leading note.
-->

<!-- ANCHOR:TC12-promocio-kerdes -->
- [ ] Q03 — Which cycle test should I promote to project level into `test-conventions.md`?

| # | Behavior (this is how it would go in) | Section | Recipe | Suggestion | Justification |
|---|---|---|---|---|---|
| 1 | The mock `/start-process` returns 201 for a valid `processName`, and 400 for a missing body | 2 | R02 | to promote | the contract of the mock lives in every cycle |
| 2 | `/verify` returns 403 with the `TMP_031` errorCode for an expired token | 3 | **a new recipe is needed** (startup + example call are missing) | to promote | every auth change affects it |
| 3 | The one-off run of the migration script of cycle-24 | 2 | R01 | stays cycle-local | one-off data migration, not repeatable |

_Did not run in this cycle (therefore not a candidate): `<test>` — `<why>`._

**Listing the numbers is enough as an answer** (e.g. "1, 2" or "all of them" / "none of them"). I will write the skipped ones into the decision log so that I do not ask about them again in the next cycle.

<!-- ANCHOR:TC12-dontes-naplo-sablon -->
## Non-promoted candidates (decision log)

- The one-off run of the migration script of cycle-24 — decision: `not to promote` (one-off data migration) · cycle-24

<!-- ANCHOR:TC10-tetel-blokk-sablon -->
### L01 — The mock `/start-process` returns 201 for a valid request

- **Goal:** the contract of the FlowX mock stays stable — the client can rely on the documented response.
- **Prerequisite:** `R02` runs (the startup is described there) · the port according to the `local` row of the `0.` block.
- **Steps:**
  1. `POST /start-process` with the `{"processName": "onboarding"}` payload.
  2. The same with an empty body.
- **Expected result:** for step 1 `201` + `{"processInstanceId": "<uuid>"}`; for step 2 `400` + the `MISSING_BODY` errorCode.

<!-- ANCHOR:doc-sync-questions-struktura -->
# Cycle NN: <title> — Doc-sync questions

- [ ] Q01 — [question text]
- [x] Q02 — [question text] → [decision / short answer]
- [ ] Q03 — [question text] _(raised by Q02)_

<!-- ANCHOR:DS10-doc-sync-plan-vaz -->
- [ ] <file> — <operation: reconciliation | new | no action> — <what exactly> (scope: <flow/component>)
  <for reconciliation/new, the Replacement text block of the subagent: the current snippet to be replaced → the new text written>

<!-- ANCHOR:DS17-fejlec-blokk -->
> **Covered:** up to cycle-16 · **Last updated:** cycle-16 (2026-06-04) · **Generator/scope:** as-built description of the behavior — every user/business flow and state of the system; source: src/ + closed spec.md files (DS19).

<!-- ANCHOR:DS15-changelog-vaz -->
## cycle-NN — <title> (YYYY-MM-DD)

**What changed in the behavior:** <behavior-level change, per flow>
**What changed in the documents:** <which docs-generated/ files + what>
**Renames (if any):** <old → new identifier>

<!-- ANCHOR:DS-system-overview-vaz -->
> **Covered:** up to cycle-NN · **Last updated:** ... · **Generator/scope:** ...

# <Name of the system> — Operational overview

> Detailed change log: [CHANGELOG.md](./CHANGELOG.md). Deviations from the design: [design-drift.md](./design-drift.md).

## What the system does (summary)
_<1-2 paragraphs: the task of the system, its main capabilities.>_

## Capabilities and flows
_<Structured by capability (NOT by cycle). For every flow: a short description + a consolidated mermaid diagram (sequenceDiagram / graph), with the outdated one replaced.>_

## State model
_<Session, cache/store mapping, token lifecycle.>_

## Endpoint inventory _(conditional — only if the system has a network interface; DS2/DS22 Layer 2)_
_<Endpoint → short description. If there is no network interface, this section is omitted.>_

<!-- ANCHOR:DS20-design-drift-vaz -->
- **<identifier>** — Design: <what the HLD/LLD states>. As-built: <what was implemented>. Justification/status: <why; open or closed>.

<!-- ANCHOR:TC2-test-conventions-vaz -->
> **Last review:** cycle-NN · **Owner:** 08-doc-sync · **Not a runnable source** — the recipe is inlined into the spec.md/plan.md of the cycle by phase 02/03 (TC1/a).

# Test conventions — recurring expectations and recipes

## 0. Coordinates

_Every environment, access and parameter datum **in one place** (TC13). The recipes of section 1 reference these, they do not repeat them._

### Environments and endpoints

| Environment | Component | URL / port | Health endpoint |
|---|---|---|---|
| local | <component> | `http://localhost:PORT` | `/health` |
| dev | <component> | `https://<host>` | `/health/ready` |

### Test users, clients, secrets

| Environment | Name / identifier | Secret | Scope / role |
|---|---|---|---|
| local | `<user>` | `<dev-only password>` | `<realm / role>` |
| dev | `<client-id>` | pointer: `.env.dev` → `<VARIABLE>` | `<scope>` |

### Parameters and env files

| Name | Value / pointer | Where we use it |
|---|---|---|
| `<PARAMETER>` | `<value or pointer>` | `<recipe or component>` |

## 1. Recipe register

### R01 — <name of the component / step>
- **Where it is:** <repo path, image name, registry target, namespace/pod>
- **Access:** <URLs, ports, health endpoint>
- **Test users / parameters:** <user + password (dev-scoped only, TC5!), scope, client-id>
- **Startup:** _(mandatory — TC11)_
  ```bash
  <bringing up the environment: docker compose up / podman run / npm run dev / oc port-forward …>
  <health check: curl -s http://localhost:PORT/health → what you expect back>
  ```
- **Commands:**
  ```bash
  <running the test / build / push / restart — only a verified command that actually ran (TC3)>
  ```
- **Example call:** _(mandatory if the recipe touches an HTTP/gRPC/CLI endpoint — TC11)_
  ```bash
  curl -s -X POST "<full URL>" \
    -H 'Content-Type: application/json' -H 'Authorization: Bearer <how I obtain it>' \
    -d '{"<field>": "<value>"}'
  # Expected response: 200, body: {"<field>": "<value>"}
  ```
- **Shutdown / cleanup:** <how I stop the environment I brought up, what has to be deleted>
- **Prerequisite / order:** <what it needs — referencing another recipe by `R-ID`, what comes before/after it>
- **Scope:** `local` | `shared-remote` — <if shared, phase 03 must ask about it when inlining>
- **Last run:** cycle-NN

## 2. Local (mock-based) tests required in every round

**Mandatory report (TR3):** `<artifact in the folder of the validation round>` — source: `conventions.md → ## Test reporting`

| ID | What it verifies | Recipe | Last run |
|---|---|---|---|
| L01 | <self-contained behavior description: for which input what the correct output is — TC10> | R01 | cycle-NN |

### L01 — <the self-contained title of the item>

- **Goal:** <what this test proves — 1 sentence>
- **Prerequisite:** <`R-ID` runs · which data of the `0.` block are needed>
- **Steps:**
  1. <concrete step — call/command/interaction>
  2. <...>
- **Expected result:** <status code, field, value — something that can be decided yes/no>

## 3. Integration / E2E tests required in every round

**Mandatory report (TR3):** `<artifact in the folder of the validation round>` — source: `conventions.md → ## Test reporting`

| ID | What it verifies | Recipe | Prerequisite | Last run |
|---|---|---|---|---|
| I01 | <self-contained behavior description — TC10> | R01, R02 | <`R05` runs (the startup is described there) — TC11> | cycle-NN |

### I01 — <the self-contained title of the item>

- **Goal:** <what this test proves — 1 sentence>
- **Prerequisite:** <`R05` runs · which data of the `0.` block are needed>
- **Steps:**
  1. <concrete step — call/command/interaction>
  2. <...>
- **Expected result:** <status code, field, value — something that can be decided yes/no>

## Non-promoted candidates (decision log)

_(Optional appendix, TC12 — an unnumbered section. Whatever the user did not want at project level goes here; the next cycle will not offer these again.)_

- <self-contained behavior description> — decision: `not to promote` (<justification>) · cycle-NN

<!-- ANCHOR:DS21-readme-index-vaz -->
- `<file name>` — <one-line description: what it is, who writes it and when>

<!-- ANCHOR:zaro-uzenet -->
   > *"The documentation is in sync with the implemented system, the consistency gate is green. We can continue with step 9: review & merge (09). Before starting the new phase, be sure to run a `/clear` command to empty the context, then use this command:*
   > ```
   > /bs-merge input: @specs/cycle-NN-<cycle-name>
   > ```"*
