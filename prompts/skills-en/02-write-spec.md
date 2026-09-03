---
phase: 02
name: bs-write-spec
description: "berkispec - 02. Use it when starting a cycle (Phase 02) based on the roadmap, to specify the functional/business requirements. It works on the git branch of the cycle (the branch was created in phase 01 from 'main'), and creates 'spec.md' ('Ready for planning') + 'spec-questions.md'. Prerequisite: 'specs/roadmap.md' status 'Done'."
prerequisites:
  - "specs/roadmap.md status: <status:done>"
output:
  - "specs/cycle-NN-<name>/spec.md status: <status:ready_for_plan>"
  - "specs/cycle-NN-<name>/spec-questions.md"
  - "specs/cycle-NN-<name>/plan-input-from-prev.md and/or tasks-input-from-prev.md (only if there is information to hand over, IP1)"
prev: bs-add-cycles
next: bs-write-code-plan
subagents:
  - "agents/researcher.md"
scripts:
  - "scripts/analyze-gate-check.py"
shared:
  - "shared/input-from-prev.md"
  - "shared/artifact-voice.md"
  - "shared/phase-commit.md"
  - "shared/quality-check-spec.md"
  - "shared/fix-mode-spec.md"
---
# 02 — Writing the spec
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

We develop software in spec driven development. The development is split into cycles. Every cycle is an independently developable, independently testable subunit of the complete implementation.

This is **phase 2 (0–9)** of the process: 0-init · 1-cycles · **2-spec ←** · 3-plan · 4-tasks · 5-analyze · 6-implement · 7-validate · 8-doc-sync · 9-review.

---

## <field:f_prerequisite>

0. **Identifying the cycle:** if the user gave a cycle/file, use that; otherwise offer the most recent `specs/cycle-*` folder for confirmation — <!-- INCLUDE:lang/common.md#ciklus-beazonositas --> — and wait for the answer before moving on.

1. **`conventions.md` existence check:** read `conventions.md` in the root of the project. If it does not exist, STOP — they should return to phase `00`.

1.a **Working-tree check (only with VCS):** run `git status --short`. If there are uncommitted changes, list them, and ask in one round whether I should commit now or continue — wait for the answer. (In a No-VCS project — according to `conventions.md` there is no version control — this and the branch step below are skipped.)

2. **Roadmap check:** read `specs/roadmap.md`. **If the status is not `<status:done>`, do not start writing a spec.** Tell the user that the roadmap is not closed yet, and that they should return to the `01` cycle management phase. If the status is `<status:done>`, find the entry of the given cycle (`cycle-NN-<cycle-name>`) in the roadmap, and use that as the starting point of the spec — the behavior, the affected components, the prerequisites and the test criterion all give a basis for elaborating the spec in detail.

1.b **Reading the recurring test expectations (TC1):** if `specs/test-conventions.md` exists, read it — this is the live register of the recurring test expectations of the project and of the recipes belonging to them, maintained by `08-doc-sync`. **Guard:** if the file does not exist yet (an early cycle — there is nothing to promote yet), **do not stop and do not create it** — say so in one sentence, and continue. How to use the file:
   - from the items of **sections 2 and 3**, lift into the `<sec:test_specification>` section (and — if it really is an acceptance criterion — into the `<sec:definition_of_done>`) what **this cycle takes on as an actual acceptance criterion**, **at the level of behavior**: what has to be checked, for which input what the correct output is. **A command, a test file path, a tool name and a build/deploy step do NOT go here** — that is the business of `plan.md` (according to the spec/plan boundary);
   - do **not** lift the plain "it must not break" kind of regression items into the spec — those belong into the `<sec:regression_impact>` table of `plan.md`, because they are not the goal of the cycle;
   - you read the **0. block** (coordinates: environments, URLs, test users, parameters) and **section 1** (recipes, commands) only as **context**: from these you see the environmental constraints the cycle moves within. They do not get carried over into the spec.
   - **Signalling an invalidation (the input of 08):** if the cycle **invalidates** an existing baseline item (it eliminates or transforms the component it references), write it out explicitly at the end of the `<sec:test_specification>` section: *"Invalidated baseline item: `<ID>` — <why>."* From this `08-doc-sync` knows (TC4) that the item has to be deleted from the register. **Do not write `test-conventions.md` yourself** — the doc-sync is its exclusive owner.

1.c **Starting from the current truth (DS5):** if `docs-generated/system-overview.md` exists, read it — this is the consolidated, up-to-date behavior description of the realized (as-built) system, maintained by the `08-doc-sync` phase. The spec should start from the **current reality**: look at which flows/state/endpoints already exist, so that the new spec builds on them and does not conflict with them. **Guard:** if the file does not exist yet (an early cycle / before the bootstrap), **do not stop** — say in one sentence that the current-truth document is not there yet, and continue writing the spec based on the roadmap.

1.d **Reading the cycle design input (CD1):** if `specs/cycle-NN-<cycle-name>/cycle-design-input.md` exists, read it — this was written by **the user**, in free form, in their own words about the cycle (phase 01 only created the empty template). For the rules of processing it, see the *"Processing the cycle design input (CD1)"* section below. **Guard:** if the file does not exist, or contains only the template text (there is no substantive user content), **do not stop and do not ask about it** — say so in one sentence (*"`cycle-design-input.md` is empty, I am working from the roadmap entry."*), and continue.

2. **Branch check (the branch was created in 01 — BD1):** the feature branch of the cycle was already created from `main` by the **01-add-cycles** phase; 02 does **not** open a new branch. With version control:
   - `git branch --show-current` → if you are already on the feature branch of the cycle, continue here.
   - If you are on another branch but the one of the cycle exists → switch to it: `git switch feature/cycle-<cycle-name>` (with the name according to the **<field:f_branch_naming>** of the `## <sec:cv_git_conventions>` of `conventions.md`).
   - **Fallback** (if the branch of the cycle does not exist for some reason — e.g. an old flow or an interrupted 01): after the branch-opening preflight (a fresh, clean `main`), create it: `git switch -c feature/cycle-<cycle-name>`. This is an exception, not the main rule — normally 01 has already created it.
   - **On the No-VCS branch** (according to `conventions.md` there is no version control) this step is skipped.

   The spec, plan, tasks files and the schema artifacts all go onto this branch.

---

## What you have to do

**If a `spec.md` already exists in the `specs/cycle-NN-<cycle-name>/` folder:** read `spec.md` and `spec-questions.md` (if it exists). **Look at `cycle-design-input.md` as well** — the user may have written into it or extended it since the previous round; process the items in it that are not yet reflected in the spec according to the rules of CD1. **Run the coordinate filtering (KX)** on the existing text — an earlier run (or another agent) may have left an environment coordinate or a deploy procedure in it; move these into `plan-input-from-prev.md` now. Then run the quality check. If you find a deficiency or a problem, add it as a question to `spec-questions.md`, and set the status of `spec.md` back according to the real state (`<status:open_questions>` or `<status:draft>`). Then continue according to the iteration rules.

**If `spec.md` does not exist yet:** create it in the `specs/cycle-NN-<cycle-name>/` folder according to the structure below.

**Do not produce a plan, a task list or an implementation.** The goal of the spec is to record the requirements, the scope and the behavior — not to design the realization.

### Spec vs plan — what belongs where (examples)

The spec describes the **behavior** (what the client/user sees, for which input what output), the plan the **implementation** (how it is realized). Examples:

| Belongs in the spec (behavior) | Belongs in the plan (implementation) |
|---|---|
| "The `/verify` endpoint returns 403 with the `TMP_031` errorCode if the token is invalid." | "The `callLegacyVerify` service throws `HttpError(403, ...)`, called in `proxy.ts:42`." |
| "After the token expires, the request requires re-authentication." | "A `token:<id>` key in Redis with a TTL, a refresh lock with `SETNX`." |
| "The response contains the `correlationId`." | "The `correlationId` is injected by the `requestContext` middleware." |
| "Two parallel requests must not start two refreshes." | "A distributed lock with Redis `SET NX PX`, a 5s TTL." |
| "Starting the process is available on the `POST /rtm/api/runtime/app/{appId}/build/{buildId}/…/start` endpoint." | "The mock runs on `localhost:5175`, the dev backend on the `https://login.dev.example.local` host." |
| "The PM and the public endpoint are **configurable separately** (two separate base URL parameters)." | "`PUBLIC_BASE_URL=http://localhost:5175`" — the concrete value, port, host. |
| "With the updated SPI the status endpoint returns `200` and `{\"status\":\"spi-ok\"}`." | "`mvn clean package`, an image push to the registry, a deployment swap in the `dsp01` namespace." |
| "The call goes with the access token of the user; with an S2S token `403`." | "The password of the test user is read from `.env.dev`; `oc login` is required." |

> **🔴 The most important distinction: path vs. coordinate.** The **endpoint path contract** → spec (e.g. `POST /rtm/.../start`, header names, error codes, payload fields). The **host / base URL / port / namespace / image / command coordinate or procedure** → plan (e.g. `https://…`, `localhost:5175`, `dsp01`, `mvn clean package`). The coordinate changes per environment without the behavior changing — this is why it is not the business of the spec. In the spec reference it **symbolically** (`{PUBLIC_BASE_URL}`), and the plan contains the concrete value.

If a sentence names a technology, a file name, a function or a concrete data-structure realization → that belongs into the plan, **take it out of the spec**.

> **🔴 But do not throw it away (IP1).** If the information taken out is **valuable** — the user said it, or it came to light from the code base, and the next phase will need it —, then instead of deleting it **write it over into `plan-input-from-prev.md`** (a task-level detail into `tasks-input-from-prev.md`). Delete permanently only what really is superfluous or a duplicate. See the "Handover between phases" section.

### Coordinate filtering — recognition and MOVING (KX) — mandatory

Experience shows that what most often creeps into the spec are **environment coordinates and procedure descriptions** (dev hosts, localhost ports, image names, deploy commands), because they look like "useful information". **These have to be filtered out actively** — even if **you** wrote them in the previous round, and even if an earlier run left them in there (see the re-run branch of the "What you have to do" section).

**Go through the whole text of the spec** (every section, including the `<sec:test_specification>` and the `<sec:objective>`), and mark the following:

| To be filtered out (coordinate / procedure → **plan**) | Stays (contract / behavior → **spec**) |
|---|---|
| an absolute URL with a host (`https://something.dev.…`, `http://localhost:5175`) | the endpoint **path** (`/rtm/.../start`, `/init-hash`) |
| `host:port`, a port number, `localhost:NNNN` | the HTTP method, the status code, the errorCode |
| an image name and tag (`…/keycloak:v1`), registry, namespace, pod, deployment name | request/response **payload fields**, an example JSON |
| a CLI command as a step to be executed (`oc`, `kubectl`, `mvn`, `npm`, `docker`/`podman`, `curl`) | header **names** and whether they are mandatory |
| a source/artifact file path (`…/pom.xml`, `…-SNAPSHOT.jar`, `build.sh`) | the **name** and semantics of a configuration parameter (`PUBLIC_BASE_URL` — what it controls) |
| an `.env*` file name and the **values** read from it | a realm/client/scope **identifier**, if the behavior (authorization) depends on it |
| a build/deploy/installation step sequence (a runbook) | an acceptance criterion of the "what has to be true" kind |

> **🔴 KX replaces a coordinate, it does not compress content (KX2).** The scope of the filtering is **exclusively the concrete technical coordinate and the procedure step** — the **logical scenario and the level of detail of the checks** stay. Replacing a `localhost:5175` with `{PUBLIC_BASE_URL}` does **not** entitle you to compress the 8-step process belonging to it into two sentences. If the input (the design input of the user, the roadmap, `spec-input-from-prev.md`, an existing test) is **detailed**, the spec also **stays detailed** — only free of coordinates. **Losing detail is just as much an error as a host left in there.**
>
> **What you may change freely — and have to (KX2/b):** the **style and the wording** (the language of the user becomes an artifact-voiced, decidable requirement — AV1); fixing an **inaccuracy** (sharpening an ambiguous phrasing, unifying a wrong or inconsistent name); **spelling out an incomplete step** (if the input skips a necessary intermediate check or does not state the expected result, complete it — if you do not know what is correct, turn it into a `spec-questions.md` question); reordering a **non-logical order** (if a step assumes a state that a later one produces). **The direction may therefore be extension and refinement, not merging and omission.** If you change the level of detail substantively (reordering, inserting a step), **tell the user in one line** what and why.

**The operation is always MOVING, not deleting:**

1. Add the item to `plan-input-from-prev.md` as a new `- [ ] Inn` entry, with the **complete, verbatim** information (URL, port, command, order — do not shorten it, because 03 will work from it) and with the source marked: `_(source: 02-write-spec, filtered coordinate)_`.
2. In its place in the spec either a **symbolic reference** goes (`{PUBLIC_BASE_URL}/rtm/.../start`), or — if the sentence was purely a procedure — it **is left out**.
3. If a **whole subsection** is a procedure description (e.g. "Dev Keycloak deployment and SPI update": image build → registry push → deployment swap), then move the **whole block** over as one item. Do not try to rephrase it into "behavior" in the spec — at most the **result** goes into the spec as an acceptance criterion (e.g. "with the updated SPI the status endpoint returns `spi-ok`").
4. **Tell the user** what you moved — line by line or item by item, in a concise list. This is a visible reduction of the content of the spec, therefore it must not happen silently.
5. If you are uncertain whether an item is a contract or a coordinate, **do not decide on your own** — add it as a question to `spec-questions.md`.

> **Why can we not leave it in the spec "just to be safe"?** Because `plan.md` has to be **self-contained**: the `test-runner` subagent reads `plan.md` only, not the spec. A URL or a command left in the spec **will never run** — it only gives the false impression that it is documented. Moving it is therefore not a formality, but what makes the information executable at all.

---

## Processing the cycle design input (CD1)

`specs/cycle-NN-<cycle-name>/cycle-design-input.md` is the **user's own, free-form cycle specification**: expectations, a sketch of the behavior, an example request/response, a process description, constraints, notes. Phase 01 creates it as an empty template; filling it in is **optional**.

**If there is substantive content in it, you must process it** — alongside the entry of `roadmap.md` this is the primary input of the spec, and it is usually more detailed than that. In case of a conflict (the design input says something different from the roadmap entry) **do not decide on your own**: add it as a question to `spec-questions.md`.

**Rules:**

1. **Do not rewrite and do not tick off the file.** This is the user's document, not a handover file (`*-input-from-prev.md`) — there are no `[ ]` items in it that you would close. Read it, process it, leave it untouched.
2. **The fate of every substantive item must be traceable.** Whatever the design input contains must either (a) appear in the appropriate section of `spec.md`, or (b) move into `plan-input-from-prev.md` / `tasks-input-from-prev.md` (if it is an implementation or task-level detail), or (c) go explicitly into the `<sec:out_of_scope>` section, or (d) become a `spec-questions.md` question. **Dropping it silently is forbidden.**
3. **The KX rule applies to this too.** The design input is typically full of environment coordinates and procedures (hosts, ports, commands) — **do not copy these into the spec**: move them into `plan-input-from-prev.md` according to the *"Coordinate filtering (KX)"* section, with their complete, verbatim content, marked `_(source: cycle-design-input.md)_`.
3.a **But preserve the level of detail (KX2).** The design input is the **most detailed** input of the user — typically they describe the test scenario and the steps of the process in the greatest detail. Replacing coordinates does **not** authorize compressing the content: if the design input describes a 10-step verification sequence, **at least 10 steps** remain in the `<sec:test_specification>` section of `spec.md`, with symbolic coordinates. **Never summarize a case described in detail by the user** — losing detail is the most frequent and the most expensive error in this phase, because 03/04/06/07 only see what remained here. You **may fix and extend** the style, the inaccuracies, the missing steps and the non-logical order (KX2/b) — the design input is a raw draft, not scripture; only losing content is forbidden.
4. **The tone is not inherited (AV1).** The design input was written in the language of the user ("I would like it if…", "let us do it so that…"); from this an **artifact-voiced, decidable requirement** becomes in `spec.md`.
5. **Incompleteness is not an error.** The design input is not a complete spec — go around the areas it does not touch according to the usual ambiguity analysis and question flow.
6. **Tell the user** that you processed it: in a concise list, where each item went (spec section / plan-input / out of scope / a new `Qnn` question).

> **03a reads it too.** `cycle-design-input.md` is also processed automatically by `03a-write-code-plan` (its technical/procedural content). This **does not exempt** you from point 3: still move the coordinates filtered out by KX into `plan-input-from-prev.md`, marked `_(source: cycle-design-input.md)_` — this way 03 sees them in one place, as items to be closed, not only in the raw text of the user.

**In fix mode** (the 05-analyze loop) you read `cycle-design-input.md` **only if** a concrete `<status:must_fix>` references a conflict with the design input — otherwise do not, so that the loop does not start the phase from scratch.

---

<!-- INCLUDE:shared/artifact-voice.md -->

---

## Spec structure

\`\`\`md
# Cycle NN: <title>

**<field:f_status>:** \`<status:draft>\` | \`<status:open_questions>\` | \`<status:ready_for_plan>\`

## <sec:objective>

_What do we want to achieve with this cycle? One or two sentences: the business or technical goal, and why it is needed._

## <sec:architecture_flow>

_The connection of the components and the data flow. If the cycle touches components, produce a Mermaid \`graph\` diagram. If it introduces a new process or call order, produce a Mermaid \`sequenceDiagram\` as well. If neither is applicable, omit it._

_**Diagram rules:**_
- _In Mermaid node labels use \`<br/>\` for a line break (the \`\n\` does not render)._
- _If the diagram depicts a call order (e.g. a \`graph\` flow chart, a \`sequenceDiagram\`), number the arrows ①②③… in order. Where the sequence is not applicable (e.g. a static architecture overview), the numbering may be omitted._

## <sec:components_behavior>

_A detailed behavioral spec per component: API endpoints, request/response format, internal logic, error handling._

_If a **helper file to be read** is needed for understanding the behavior of a component (e.g. an existing mock server or a shared service), reference it directly at its description as well. The files to be modified or created do **not** go here — those are exclusively the task of the `<sec:referenced_files>` section._

_If the spec introduces a new component whose fundamental technology decisions are still open (build system, communication mode, deployment mechanism, runtime/language, etc.), add this note to the description of the component: **"The fundamental technology decisions are to be clarified in the plan phase."** — The spec should not specify these details, only signal that the plan phase has to pay attention to them._

_**Decision criterion:** the note is needed if you **cannot point unambiguously at an existing component in the repo as a model** for the project structure, build system or deployment mechanism of the component. If there already is a similar component (e.g. another Fastify app, where a model already exists), the note may be omitted. If there is not (e.g. the first Java project, the first gRPC service), the note is mandatory._

## <sec:out_of_scope>

_What does NOT belong into this cycle. An explicit list — it prevents scope creep._

## <sec:referenced_files>

_Documentation and specification materials: READMEs, HOW-TOs, OpenAPI descriptors, Avro schemas, DB migrations, existing spec files, behavior-reference scripts (e.g. a mock server that has to be read to understand the behavior). **Source files (.ts, .tsx, .js, package.json, etc.) do not go here — those are identified in the plan phase. The paths/links of the files must always be relative to the current directory of the file (with as many steps up to the project root as the depth of the folder requires, e.g. `../../apps/legacy-login/README.md`), absolute paths or `file://` scheme links must not be used.**_

_If the cycle touches a REST API, a message-queue message, a cache structure or a DB schema, and formal descriptors already exist (OpenAPI YAML, Avro schema, Redis key map, DB migration), reference them here. The plan phase will validate these or — if they do not exist — generate them._

## <sec:test_specification>

_Test data, cases to be tested (happy path + error cases), mandatory behavioral checks._

_**🔴 Every test case states WHAT it verifies and WHY (TD7).** BEFORE the steps, the case says in one sentence which **behaviour** it proves — as a decidable claim — and which `<sec:definition_of_done>` item (`DoD-NN`) or risk it proves. **A title is not a purpose:** "Test case 3: concurrency" is a topic, not a claim; the claim is: *"out of five simultaneous requests exactly one renews the token, the rest are served from the existing one"*. This sentence carries the intent over into `03` (where it becomes the `<field:f_what_we_test>` line) and into `07`: without it, for a failing test it cannot be decided whether the code broke or the test is bad._

_**Case-oriented, not procedure-oriented.** You describe **what has to be true** ("called with an S2S token, start-process returns 403"), not **how we get there** ("let us start the stack, then…"). The **environment-preparing** step sequence (starting the stack, build, deploy, installation) is the business of `plan.md`._

_**🔴 Do not condense the test cases (KX2).** If the input — the `cycle-design-input.md` of the user, `spec-input-from-prev.md`, the roadmap or an existing test — gives a **detailed test scenario** (a multi-step verification sequence, branches, intermediate states, concrete input→expected output pairs), **preserve it in full detail**: every step, the intermediate checks and the expected results have to stay. Replace **only the coordinates** with a symbolic reference (`{PUBLIC_BASE_URL}`, `{MEDIA_BASE_URL}`, `{TEST_USER}`) — do **not** simplify the **logical content**, do not merge the steps, and do not replace them with a summary of the "the process runs through" kind._

_**A formatting tip that protects 03:** put the elaborated artifact (an OpenAPI fragment, a complete JSON payload, DDL, a `curl`) into a **code block** with the appropriate language marking (```yaml`, ```json`, ```sql`). This way the mechanical gate of `05-analyze` **checks mechanically** (`V1` check) whether 03 really took it over verbatim — in case of truncation it becomes a `<status:must_fix>`, you do not have to notice it._

_**What you may — and have to — do (KX2/b):** rephrase the text of the user into artifact voice; fix an inaccuracy, an ambiguity, an inconsistent name; **spell out an incomplete step** (a missing intermediate check, completing an expected result that was not given — if you do not know what is correct, it becomes a `spec-questions.md` question); **reorder a non-logical order** (if a step builds on a state produced later). The direction is **extension and refinement** — merging and omission are not. Tell the user about a non-trivial reordering/insertion._

_**Being case-oriented does not mean being short.** A behavioral sequence (①…②…③, each with its own expected result) **stays case-oriented** even if it is ten steps long — because it describes what has to be true, not how we produce the environment. The "procedure-oriented" prohibition applies to the **runbook** (image build, `oc`/`mvn`, deployment swap), not to the **behavior sequence**. In case of doubt: **let the detail rather stay** — losing detail comes to light in phase `06`/`07`, when nobody knows any more what should have been checked._

_**What does NOT go here** (all of it belongs into `plan.md`, to be filtered out according to the KX rule):_
- _a port, host, base URL, a concrete `localhost:NNNN` — only a symbolic reference (`{PUBLIC_BASE_URL}`);_
- _a build, deploy or installation command and step sequence (image build, registry push, deployment swap, `oc`/`mvn`/`npm`) — **this is not a test but a runbook**;_
- _the name of the test tool and framework, a test file path (recorded by `conventions.md`, referenced by `plan.md`);_
- _the level of mocking and the containerization decision ("a real stack vs. partial mocking", which service runs in a container) — this is the mandatory first question (`Q01`) of phase `03`, not the business of the spec;_
- _a test-environment credential and an `.env` value._

_Naming the **test levels** (unit / integration / E2E) is fine if it marks the level of the behavior — but the **infrastructure** of the levels belongs to the plan._

_If `specs/test-conventions.md` exists: those items of section 2/3 that this cycle takes on as an acceptance criterion — **at the level of behavior**, referencing the ID of the item (e.g. "I01 — the token exchange returns 200 with the `<scope>` scope"). A command, a test file path and a tool name do not go here (TC1). Write out explicitly at the end of the section the baseline items **invalidated** by the cycle._

## <sec:risks>

_What can go wrong? What assumptions is the spec based on? Accepted POC limitations, open technical risks._

## <sec:definition_of_done>

_Verifiable, checkable conditions. Every item should be concrete and unambiguously decidable (yes/no)._

- [ ] **DoD-01** — [the verifiable condition]
      · _evidence:_ \`[test name | cmd: <command> | manual: <what we check by hand>]\`
- [ ] **DoD-02** — [the verifiable condition]
      · _evidence:_ \`[…]\`
\`\`\`

> **The evidence field (DI2) — strongly recommended.** For every DoD item, name **what proves** that it is fulfilled: a **test name** (from the test specification of `plan.md`), a **`cmd:` command**, or — if it really can only be checked by hand — `manual: <what>`. `07-validate` evaluates these with `dod-check.py` by a **machine join** with the run results of the round: for an item that has evidence, no LLM judgement is needed, and a ✓ given from memory cannot happen. An item without evidence is not an error, but 07 marks it with a `?` and asks for a manual judgement — if there are many of these, that signals a weakness in the verifiability of the spec. *(The evidence here is a **behavior-level name**, not a test file path or a run command fragment — the spec/plan boundary stays valid; the `cmd:` form is only justified if there is no test case for it.)*

> **The `DoD-NN` identifier is mandatory and stable (DI1).** Every DoD item gets its own, consecutive identifier (`DoD-01`, `DoD-02`, …), and this identifier **never changes** during the cycle — `07-validate` logs the failed DoD items into the `# <sec:validation_history>` under this name, and counts the 3-attempt stop under this name. If an item is inserted later, it gets the next free number (do not renumber the list); if an item is deleted, its number cannot be reused. With a paraphrased DoD item or one without an identifier, the stopping mechanism of the loop breaks silently.

---

## Context loading rules

- Read only what is absolutely necessary for writing the spec.
- If you have to understand a complex existing module or logic, call the `researcher` subagent (`agents/researcher.md`, Mode B) for the research. The subagent returns only the summary — the raw file content does not get into the main context.
- If the architecture of earlier cycles is needed, ask about it in one sentence — do not read all the earlier specs.
- If you have to understand concrete existing code, read only the affected file or part.

---

## Handover between phases (`*-input-from-prev.md`) — IP1

**What you READ:** if `specs/cycle-NN-<cycle-name>/spec-input-from-prev.md` exists, read it at the beginning of the phase (before writing the spec). It contains the behavioral details that came up in the 01-add-cycles phase but did not fit into the roadmap. Either build every `[ ]` item into the appropriate section of `spec.md`, or drop it with an explicit justification, and tick it off. **Guard:** if the file does not exist, that is not an error — continue.

**What you MAY WRITE INTO:**
- **`plan-input-from-prev.md`** — for **03**: every technical/implementation detail that you took out of the spec or learned during the research (an affected component, an existing solution, a technology constraint, a performance limit).
- **`tasks-input-from-prev.md`** — for **04**: a concrete preparatory step or ordering constraint that already came to light (e.g. "the key generation has to precede the container build").

<!-- INCLUDE:shared/input-from-prev.md -->

---

## Continuing after an interrupted run

If the spec phase is interrupted and continues in a new session:

```
1. Read the current state of spec-questions.md (if it exists).
   → Continue from the first question with a [ ] status.

2. Read the current state of spec.md.
   → If there is an open [ ] question: the status is "<status:open_questions>".
   → If every question is [x] but there is no user confirmation: run the
     quality check, then ask for confirmation (do not set it to Ready for planning).

3. If there is no spec.md: start according to "What you have to do".
```

The current state of `spec.md` and `spec-questions.md` + this prompt is enough for the restart.

---

## Ambiguity analysis — a template for finding questions

To discover the questions, go through the **10 categories** below, and where you find **real ambiguity**, add it as a question to `spec-questions.md`. **Guidance, not an obligation:** you do not have to ask a question for every category — only where the information really is missing or ambiguous.

1. **Functionality** — what exactly does the system do? (e.g. "What happens to the requests in progress after the token expires?")
2. **Data model** — fields, types, whether they are mandatory, validation. (e.g. "Is `userId` optional or mandatory in the payload?")
3. **UX / interface** — the behavior of the user or API interface. (e.g. "What does the client see on an error — a message, a code, a redirect?")
4. **Performance** — metrics, limits. (e.g. "Is there an expected response time or throughput?")
5. **Security** — auth, authorization, encryption. (e.g. "Which scope is needed for the endpoint?")
6. **Integrations** — external systems, contracts. (e.g. "Which version of the external API do we build on?")
7. **Error handling** — error cases, fallback. (e.g. "In case of a timeout, a retry or an immediate error?")
8. **Authorization / roles** — who can do what. (e.g. "Is there a difference between an admin and a plain user?")
9. **Observability** — logging, metrics, trace. (e.g. "What has to be logged in the flow for correlation?")
10. **Other** — everything that does not fit into the above but has to be clarified.

This is only an **aid for discovering questions** — the existing `spec-questions.md` flow is unchanged.

---

## Handling open questions

`spec-questions.md` is the question register of the spec phase. **Every question that comes up — for whatever reason — has to be added here immediately, before you put it to the user.** This applies to business decisions, unknown constraints, ambiguous requirements, error branches and any other uncertainty alike.

**Basic rule: we never delete from the list. A closed question is only marked with `[x]` — its text and the decision stay.**

### spec-questions.md structure

If it does not exist yet, create it in the `specs/cycle-NN-<cycle-name>/` folder:

```md
<!-- INCLUDE:lang/02-write-spec.md#spec-questions-struktura -->
```

Always append a new question to the end of the list, with the next sequential `Qnn` number.

### Status transitions (the status field of spec.md)

- When starting a new spec: `<status:draft>`
- If there is at least one question with a `[ ]` status in `spec-questions.md`: `<status:open_questions>`
- If every question has an `[x]` status and the quality check passed, and the user explicitly confirmed it: `<status:ready_for_plan>`

### Iteration rules

1. If there is a question with a `[ ]` status in `spec-questions.md`, put **one** of them, and wait for the answer. Do not pour all the questions on the user at once. **Every time you put a question or ask for approval/review, you must place at the end of your answer a direct, clickable markdown link to the affected files (e.g. in the form `[spec-questions.md](file:///absolute/path/specs/cycle-NN-name/spec-questions.md)`).**
2. If the question got answered: mark it with `[x]` in `spec-questions.md`, write a one-line summary next to it (`→ ...`), and carry the decision over into the appropriate section of `spec.md`.
3. If the answer opens a new question: add it immediately to the end of the `spec-questions.md` list with the next `Qnn` number, before you continue.
4. Iterate until every question has an `[x]` status.
5. If every question is closed, run the quality check. If it passed, **put the question to the user**: <!-- INCLUDE:lang/02-write-spec.md#statusz-megerosites --> — Do not switch the status before the confirmation. **At the end of the answer, place the direct, clickable link of `spec.md`.**
6. If the user confirms explicitly (e.g. "yes", "done", "go ahead"), set the status of `spec.md` to `<status:ready_for_plan>`, **and commit immediately** — see the *Phase-closing commit* section below (`<PHASE-TAG>` = `02-spec`). Confirmation → writing the status → commit: this is a single sequence of steps.

Every iteration can be started with a new context: the current state of `spec.md` and `spec-questions.md` + this prompt is enough. At a restart, read `spec-questions.md`, and continue from the first question with a `[ ]` status.

---

## Stopping rules

If any of the following holds, **STOP — stop and do not move on**:

- **There is a question with a `[ ]` status in `spec-questions.md`** — put one to the user, wait for the answer, then continue. Do not put several questions at once.
- **The quality check found an error** — fix the error, then run it again. Do not set the status to `<status:ready_for_plan>` until it passes.
- **The confirmation of the user is missing** — the status can only be set to `<status:ready_for_plan>` after an explicit confirmation. Do not switch it without asking.
- **The spec contains an element with plan content** (e.g. a technology choice, an implementation detail, a concrete file plan) — delete it, it does not belong into the spec.
- **The status is `<status:ready_for_plan>` but the phase-closing commit is missing** (a VCS project, `git log -1 --oneline` does not show the `cycle-NN: 02-spec` commit) — commit first according to the *Phase-closing commit*, and only close the phase afterwards.
- **The status is already `<status:ready_for_plan>`** (and the commit is there) — stop. Do not start a plan or a task list. Tell the user the next step and the starting command of the phase, for example:
<!-- INCLUDE:lang/02-write-spec.md#zaro-uzenet -->
> **At the end of the answer, place the direct, clickable link of `spec.md`.**


---

## Status handling

| State | Condition |
|---|---|
| `<status:draft>` | When starting the spec |
| `<status:open_questions>` | There is at least one `[ ]` question in `spec-questions.md` |
| `<status:ready_for_plan>` | Every question is `[x]` + the quality check passed + **the user confirmed it explicitly** |

After switching to `<status:ready_for_plan>`, a git commit (`cycle-NN: 02-spec`) is **mandatory** — for the procedure see the *Phase-closing commit* section. Do not switch the status without a confirmation.

<!-- INCLUDE:shared/phase-commit.md -->

In the block above, the value of `<PHASE-TAG>` in this phase is: **`02-spec`**, and the closing status is: **`<status:ready_for_plan>`**.

> **Done lifecycle:** after `<status:ready_for_plan>`, `spec.md` moves to `<status:done>` status at the end of the cycle — when the PASS of the validate (07) closes the cycle. Phase 08 already expects `<status:done>`. This transition is done by 07, not here.

---

<!-- INCLUDE:shared/quality-check-spec.md -->

---

<!-- INCLUDE:shared/fix-mode-spec.md -->
