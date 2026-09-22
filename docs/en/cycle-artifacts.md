# The artifact files of a cycle

← [Back to the main page](../../README.md) · [Page index](README.md)

## 10. The artifact files of a cycle

Every cycle gets its own folder: `specs/cycle-NN-<cycle-name>/`

| File | Phase | Content |
|------|-------|----------|
| `spec.md` | 02 | Business behaviour, requirements, affected areas, mock strategy, Definition of Done. The DoD points get a **stable `DoD-NN` identifier** (DI1) and — strongly recommended — an **`· _evidence:_`** field (DI2: a test name / `cmd:` / `manual:`), from which 07 evaluates with a **machine join** using `dod-check.py`, without an LLM judgement. |
| `spec-questions.md` | 02 | The open questions relating to the specification. The spec is only `Ready for planning` if there is no `- [ ]` here. |
| `plan.md` | 03 | The technical execution plan, the affected components, the planned changes, the test/verification strategy. **Self-contained:** every test case and `DoD-NN` point of the spec is mapped onto a plan test case (TP1, the `Spec coverage` table), the recipes of `test-conventions.md` are physically copied in (TC1/a), the **environment preparation** (token acquisition, starting the stack, the build/deploy/rollback of an individual component, seeding) with verbatim commands (TP3), the mandatory **`## Environment coordinates`** section (KO1: component base URLs, ports, health endpoints, verbatim start/stop commands, example REST calls including the token acquisition, test and API users with their passwords, every parameter — without a placeholder or an empty cell, enforced by the `C6` gate), the **configuration lifecycle** for every run mode (KF1) and the **reverse coverage** (a spec source for every plan capability — SC1) — before the closing, the full *Closing gate* (TP2) is mandatory. A mandatory part of it is the **`### Machine-readable run table (run-tests.py)`** (TP4): category / type (`fast`\|`heavy`) / prerequisite / command / result file / format / cleanup / environment / **phase** (PH1: `implement`\|`validate`\|`both`; empty = both) — 07 runs from this with a script, so the raw test log never enters the LLM context. In its absence, 07 falls back to the `test-runner` subagent. Also mandatory is the **`### Test scenarios`** section (TS1): one `TS-NN` block per test case with a `DoD-NN` reference, with `What we test` / `Prerequisite` / a step table / `Cleanup` rows — every row of the step table carries a **verbatim runnable call** and a **concrete, checkable expected result**, and for REST steps the block also carries the call in `.http` form (TS8) (the hard floor of TS3 rules out phrasings of the "runs successfully" kind). This is the primary source of the `TG-NN` groups of `bs-manual-test-plan`. The **design** of the scenarios is driven by the `TD0–TD6` recipe (`shared-hu/test-scenario-design.md`): a dimension inventory for the count (TD1), the observation quartet for the content (TD2 — a counted side effect, directly read state, a negative control), countability (TD3), proof of isolation (TD4), a calibration sample (TD5) and a self-check before the closing (TD6). Every `[P-…]` entry carries a **`Purpose and rationale`** line (WY1: what will be true after the change, what trouble it eliminates, which `DoD-NN` it follows from), every row of the `Spec coverage` table names a `TS-NN` (TS7 — the test cases of the spec have to be converted, not copied over as prose), and under every `#### <test file path>` heading stands the **test artifact data sheet** (TA1: `How to run` · `Fixtures and test data` · `Test cases`). The **`**Target environment:**`** field (EV1) and the **`Environment`** column of the run table (EV2) are mandatory: for a non-local category the target host stands **in the command** (EV3), the `Prerequisite` calls the same place with a reachability probe (EV4), and `localhost` is forbidden (EV5). |
| `plan-questions.md` | 03 | The open questions of the design stage. The plan is only `Ready for tasks` if there is no `- [ ]` here. |
| `tasks.md` | 04 | A checkboxed task list (with `[RED]`/`[GREEN]`/`[CHECK]`/`[OPS]` markers — a marker is mandatory on every task) + the prerequisite documents. For a destructive `[OPS]` operation affecting a shared environment, the approver and the rollback task are mandatory. **The plan link (PID1):** every task references the plan's stable `[P-…]` section identifier (not a serial number), a single primary source, with a sub-scope marker in the case of several tasks; the group headers list the plan IDs covered, and at the end of the file the reverse `Plan coverage` table (plan section → tasks) **and the `Test coverage` table** (TT1: every `TS-NN` scenario and every run-table category → creating task + running task, or a justification) are mandatory. **Entry gate (EG1):** the first step of the phase is actually running `analyze-gate-check.py --plan-only` — the status field of the plan is self-declared, and on a failing gate there is no tasks list. The command of a `[CHECK]` is the one-file command of the plan's test data sheet, and two `[CHECK]`s must not write with `>` into the same log file (T6). **The test link (TI2/TX1):** every test-writing and test-running task refers to the plan's test case at the end of the line in the form `— test [TC-01]` / `— test [TS-03]`, and **every test to be run is a separate checkbox** — one `[CHECK]` runs exactly one identifier, with a test-filtering command. |
| `tasks-questions.md` | 04 | The open questions of the tasks stage (used mostly by the 05 fix mode). `tasks.md` is only `Ready for implementation` if there is no `- [ ]` here. |
| `cycle-design-input.md` | created by: 01 · **filled in by: the user** · consumed by: **02, 03** | The cycle design input (CD1): a free-form cycle specification written by the user in their own words (expectations, an outline, examples). 01 creates it as an empty template in the cycle folder and draws attention to it; **filling it in is optional**. If there is content in it, `bs-write-spec` processes its **behavioural** part (next to the entry in `roadmap.md`, as a primary input), and `bs-write-code-plan` reads it automatically and lifts its **technical/procedural** part — self-containedly — into `plan.md`. Neither phase rewrites the file. |
| `spec-input-from-prev.md` | written by: 01 · consumed by: **02** | The handover between phases (IP1): behavioural details that came up in 01 but do not fit into the roadmap. Only if there is information to hand over. |
| `plan-input-from-prev.md` | written by: 01, 02 · consumed by: **03** | Technical/implementation details taken out of the spec or surfaced during the research. |
| `tasks-input-from-prev.md` | written by: 02, 03 · consumed by: **04** | Preparatory steps and ordering constraints for the task breakdown. |
| `validate-input-from-prev.md` | written by: 03, 04 · consumed by: **07** | Run prerequisites and operational knowledge for the validation (e.g. "a VPN is needed before starting the stack"). |
| `analyze/analyze-report.md` | 05 | The cross-phase consistency report (PASS/FAIL), 6 categories (1+3, 2+5 and 4 are the three scopes of the `analyzer`, 6 is the `analyzer-exec`), the coverage matrix and the `Plan section ↔ task` table **generated by the gate** (the orchestrator splices them in verbatim, then corrects them per the `Affected DoD rows`), an **executability inventory**, and a **Loop log** (the per-iteration audit trail of the self-healing loop). **Every file of the analysis lives in the cycle's `analyze/` subfolder** (AD1). |
| `analyze/analyze-task.md` | 05 | The **fix list approved in the triage (TR1)** — the fixer subagents work exclusively on its open items. Only what the user marked for fixing gets here (plus the items of the mechanical gate, without a question); the rejected items stay in a separate section, which is the memory for filtering in later rounds. Its only writer is the orchestrator. |
| `analyze/slices/` | 05 | The output of the mechanical gate's `--emit-slices`: the input of the three semantic `analyzer` rounds, as a verbatim excision of the design documents. It hides itself with a `.gitignore` and is not committed. |
| `imp-decision.md` | 06 | The implementation decision log: non-obvious solutions and the stops after the 3-attempt rule. |
| `test-report/implement/` | 06 | **An official phase folder (TR6).** It always contains `check-log.md`; if the `**Report phases:**` field of `conventions.md` lists `implement`, then also the full report set of the closing state of 06 (the same table, the same `report-gate-check.py` gate, with `--report-subdir test-report/implement`). If not, the evidence is given by the first FULL round of 07. |
| `test-report/implement/check-log.md` | 06 | The append-only log of the `[CHECK]` runs: time, task, which attempt, mode (normal / validate-loop), the **command actually issued** and the counts (`X passed / Y failed / Z skipped`) — including the failed attempts. Without it, all that would remain from the implementation phase is the `- [x]` tick, which asserts the green but does not prove it (after a `/clear` the chat is gone). |
| `test-report/validation-report.md` | 07 | **The `## Round N` blocks are written by `round-log.py`** (open/step/close) and the `# Validation History` by `failure-counter.py` — the orchestrator only supplies the free-text fields. The validation run history, regression/Sonar defects, consecutive-failure counters — and at the same time the **log of the 07 self-healing loop** (LC2), the anchor of an interrupted run. The **type of the rounds is visible too** (FULL / LIGHT — VD10): the expensive steps (E2E, regression, Sonar, review) only run in the first and the closing confirming round, and in the intermediate fixing rounds the complete fast test set runs. PASS can be given **only from a full round**. |
| `test-report/validate/round-NN/` | 07 | A separate folder per round with **all** the test artifacts of the round (per the `## Test reporting` table of `conventions.md`: Allure/Playwright HTML, coverage, JUnit XML) **and** with `sonar-report.md`/`.html`. The number of the folder = the serial number of the `## Round N`; the folders of earlier rounds are never overwritten (TR5). |
| `manual-test-plan.md` | *(not a phase — `/bs-manual-test-plan`, any time after 05)* | The manual test plan: `Environment and startup` (component, port, health endpoint, verbatim start/stop command), `Test data` (users with passwords, tokens, seed, cleanup — with the TC5 secret rule), `Automated tests` (the plan's machine-readable run table + the location of the results), `TG-NN` **manual test groups** (what we test · prerequisite · a step table with concrete expected results · a `curl` **and** a `.http` block · cleanup), `Not manually testable` (MT10: a justification + what covers it), `Coverage` (`DoD-NN → TG-NN`) and a `Change log`. **Two modes:** `Planned` (from the design, not verified against real code) or `As-built` (verified against the code — in case of a divergence the code wins). A deterministic gate: `manual-test-gate-check.py` (MG1–MG10). **Zero feedback:** neither 07 nor 09 gates on it, and no result file is produced. |
| `doc-sync-plan.md` | 08 | The per-file tickable plan of the `doc-sync-planner` for updating `docs-generated/` (what has to be done / no action + drift findings). The deterministic anchor of the execution **and** of resuming after an interruption (the main agent ticks it). |
| `doc-sync-questions.md` | 08 | The decision points and gate failures of the doc-sync (`Knn`). The main agent asks them one by one; on an open `[ ]` question the phase stops. We never delete, we only tick `[x]`. |
| `test-report/code-review.md` | 07 | The code review report of the `reviewer` agent: `MF-NN` **Must Fix** (blocking) + `S-NN` **Suggestions** (non-blocking). It contains no log — the rounds of the review go into `# Validation History` in `validation-report.md`, on a counter shared with the test failures. In the case of an open finding, the `## Review fixes` section of `tasks.md` is also created. |

### 10.1 The handover between phases (`*-input-from-prev.md`)

**What problem it solves (IP1):** in a phase, information regularly surfaces that is **valuable but does not belong there** — too technical, too detailed, or simply the business of the next phase. Up to now the skills instructed that this be **deleted**: `02-write-spec` literally says that "if a sentence names a technology, a file name or a function → that belongs in the plan, delete it from the spec". So the information went into the bin, not into the next phase — and `03` then rediscovered it (or did not). These files give it **a destination instead of the bin**.

| File | Who may write into it | Who consumes it |
|---|---|---|
| `spec-input-from-prev.md` | 01-add-cycles | **02**-write-spec |
| `plan-input-from-prev.md` | 01, 02 | **03**-write-plan |
| `tasks-input-from-prev.md` | 02, 03 | **04**-write-tasks |
| `validate-input-from-prev.md` | 03, 04 | **07**-validate |

All of them in the cycle's folder (`specs/cycle-NN-<name>/`). **One phase may write into several files** in the same run, if the information has to be spread out (e.g. a technical detail arising in 02 into `plan-input`, and the testing prerequisite following from it into `validate-input`). **06-implement** deliberately does not get its own: it reads `plan.md` and `tasks.md` anyway, so an implementation detail belongs there.

**Its biggest "feeder" is the coordinate filtering of 02 (KX).** What most often bleeds into the spec is **environment coordinates and procedure descriptions** (remote hosts, `localhost` ports, image names, deploy commands, complete deployment runbooks in the `Test specification` section), because they look like useful information. That is why `02-write-spec` runs a **mandatory filtering routine** — both when writing a new spec **and** when re-running on an existing one — that recognises these and **moves** them (it does not delete them) into `plan-input-from-prev.md`, leaving a symbolic reference in the spec (`{PUBLIC_BASE_URL}`). The delimitation in a single rule: **the endpoint path is a contract (spec), while the host / base URL / port / namespace / image / command is a coordinate (plan)**. `03a-write-code-plan` runs the mirror image of this: if the spec stayed too technical, it **lifts the data into the plan** and tells the user (it does not rewrite `spec.md`) — because `plan.md` has to be **self-contained**: the `test-runner` reads only that, so whatever is not there will never run.

**On the consuming side, a reference is not enough (dereferencing).** A handed-over item is often phrased at a high level of abstraction (*"build the image and push it to the registry by running `build.sh`"*). `03a-write-code-plan` **must not reproduce the abstraction level of the input**: if an item **references** a script, a procedure, an existing test or an external API, it has to **resolve the reference from the source** — the actual commands of the script, the registry host, the full JSON payload with every mandatory field — and write the concrete detail into `plan.md`, with the source indicated. For a large or scattered source it calls the `researcher` subagent, **asking for literal values**; the researcher received a narrow exception to its "never raw file content" rule for this (short, verbatim snippets: a command, a URL, a payload, a signature — but not a whole file, and a pointer instead of a secret). This is critical because `04`, `06` and the `test-runner` **no longer see the spec or the source**: whatever did not make it into `plan.md` does not exist for them.

**Item format** — a checkbox list, modelled on the question files, with the source indicated:

```md
- [ ] I01 — [the handed-over information] _(source: 02-write-spec)_
- [x] I02 — [the handed-over information] _(source: 01-add-cycles)_ → incorporated: plan.md "Planned changes"
- [x] I03 — [the handed-over information] _(source: 02-write-spec)_ → rejected: outside the scope of the cycle
```

**Rules:**

- **We never delete** — a closed item gets `[x]` + a one-line note (`→ incorporated: <where>` / `→ rejected: <why>`).
- **It does not block along the way**, but **no open item may remain when the phase is closed**: it is a mandatory point in the quality check of every consuming phase that every item has either been incorporated or **rejected with an explicit reason**. Stepping over it silently is forbidden — this is the safety net against a weaker model that would otherwise ignore the file.
- **It does not ask.** The boundary against `*-questions.md`: a **question** = "I do not know, you decide"; an **input-from-prev** = "I know, but it does not belong here". Whatever is also a question to be decided goes as a question into its own phase's `*-questions.md`.
- **No empty skeleton is created** — the file is only created if there is something to write into it; its absence is not a defect (the same principle as with `test-conventions.md`).
- **Whatever belongs not in the next phase but in a later CYCLE** goes into `specs/roadmap.md`, not here. And whatever is needed in **every future cycle** (a recurring test expectation) goes into `specs/test-conventions.md` — whose owner is `08-doc-sync`.
- **The fix modes of the self-healing loops (05/07/09) ignore these files completely** — they neither read nor write them. Fix mode is a targeted correction for a `Must Fix` list; re-running the handover mechanism there would be nothing but cost and noise.
- **The read-only diagnosis of 05-analyze does watch them, though:** the `s2-coverage` round flags an open `[ ]` item of `spec-`/`plan-`/`tasks-input-from-prev.md` as a **coverage gap** (not `validate-input`, because its consumer runs afterwards). The `Must Fix` names **what was left out** of `spec.md`/`plan.md`/`tasks.md` — it does not ask for the ticking, since the fixer does not write these files.
- It does not touch **`quick-flow`**: that is three-phase, runs in one context, and has nothing to hand over between phases.

The shared description of the mechanism lives in one place — `prompts/shared-hu/input-from-prev.md` — which the installer embeds **inline at build time** into the installed version of the referencing skills (`01`, `02`, `03`, `04`, `07`); the skill only writes its own, phase-specific part around the marker (what it reads, which files it may write into).

---

## 12. Question handling (spec-questions.md / plan-questions.md / tasks-questions.md / doc-sync-questions.md)

In the spec (02), plan (03) and tasks (04) phases the agent keeps its open questions in a separate file. `tasks-questions.md` primarily serves the fix mode of the 05 self-healing loop (but the normal 04 flow may reference it too). **08-doc-sync** follows the same pattern with `doc-sync-questions.md`: the decision points and the DS22 gate failures go here as `Knn`s, the main agent asks them one by one, and on an open `[ ]` question the phase stops (the subagent — `doc-sync-planner` — never asks directly).

**Structure:**
```md
# Cycle NN: <title> — Spec/Plan/Tasks questions

- [ ] K01 — [the text of the question]
- [x] K02 — [the text of the question] → [the decision / the answer in brief]
- [ ] K03 — [the text of the question] _(arose from K02)_
```

**Rules:**
- **One** question at a time is put in front of the user — the agent waits for the answer.
- We **never delete** from the list — a closed question is marked with `[x]`, and the decision is preserved.
- A new question goes to the end of the list with the next `Knn` number.
- The phase can only be closed if every question is `[x]` and the user has explicitly confirmed it.

**The question flow of the analyze loop (05):** the fixer subagents of the self-healing loop (`spec/plan/tasks-fixer`) also write questions **here** when a real decision is needed — but they **do not ask the user directly**. The question is put by the **orchestrator (05-analyze)**, in the dialogue with a **phase prefix**: `SPEC/K07`, `PLAN/K03`, `TASKS/K02` (in the files the question stays a plain `Knn` — the location of the file encodes the phase). Towards the user, every question gets a phase header: `[PHASE · iter n/max X · PHASE/Knn]`.

**Status transitions:**

| State | Condition |
|---------|----------|
| `Draft` | When the phase is started |
| `Open questions` | There is at least one `[ ]` question |
| `Ready for planning` / **`Ready for test planning`** / `Ready for tasks` / `Ready for implementation` | Everything `[x]` + the quality check passed + the user confirmed |

> **The status chain of `plan.md` has two steps (03a → 03b):** `Ready for planning` (the spec) → **`Ready for test planning`** (`03a` closes the code plan) → `Ready for tasks` (`03b` closes the test plan). `Ready for test planning` is **not** the end of the phase from the cycle's point of view: starting `04` with it is an error, and its entry gate (EG1) catches it.

**Loop markers (LC1).** When a self-healing loop reopens a document for correction, the status takes the phase-appropriate not-done value with a **suffix marker** (e.g. `Draft [analyze-loop]`, `Ready for implementation [validate-loop]`). The meaning of the marker is uniform: **fix mode is active** → the fixer steps the status automatically (without user confirmation; the user only steps in at the questions and at the final PASS), and the marker is at the same time the anchor for resuming after an interruption. At the closing (PASS / a clean review) it comes off; on abandonment (`max X` / 3 attempts / `max 5` / escalation) it stays on the document to signal the stuck state.

| Marker | Loop / reopened document | Fixer | Log |
|---|---|---|---|
| `[analyze-loop]` | 05-analyze / the design docs (`spec`/`plan`/`tasks`) | `spec`/`plan`/`tasks-fixer` | `analyze/analyze-report.md` (the Loop log) + `analyze/analyze-task.md` |
| `[validate-loop]` | 07-validate / `tasks.md` | `implement-fixer` (test/Sonar/DoD) and `review-fixer` (Must Fix) — both 06 fix mode | `# Validation History` in `validation-report.md` |

---

## 13. A uniform `Done` status lifecycle

Every document gets its own phase-specific closing status when it is created (`spec.md` → `Ready for planning`, `plan.md` → `Ready for test planning`, then `Ready for tasks`, `tasks.md` → `Ready for implementation`), and then **moves to `Done` as soon as the validate (07) closes the cycle with a PASS**. This way the 08-doc-sync and the merge branch of the cycle end expect `spec.md`/`plan.md`/`tasks.md` uniformly in the `Done` status.

> **The status of a document and the state of the CYCLE are two different things.** The three documents stay `Done` after the merge as well — they really are finished. Whether the **cycle** is done is decided by the last enabled verification point (`VP1` = `07`, `VP2` = the post-merge round, `VP3` = the dev test): while that is still ahead, the cycle row of the roadmap carries the `⏳ waiting for verification` mark, and the generated `cycle-status.md` shows what is left. This way no gate waiting for a `Done` has to be extended item by item.

---
