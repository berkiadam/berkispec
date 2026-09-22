# The full berki spec flow (00–09)

← [Back to the main page](../../README.md) · [Page index](README.md)

This chapter describes the **full, many-phase** development route with its flowcharts — from the project setup (00–01) through the per-cycle loop (02–09) to the merge, including the self-healing loops. The **other route**, the simplified three-phase flow, is detailed further down, in the "Simplified (lightweight) flow" chapter.
> **Code markers:** in the text, codes of the form `DS`/`VD`/`RD`/`LC`/`SK` + a number (e.g. `DS22`, `RD6`, `LC1`) are the internal rule identifiers of the skill files. Their detailed definition lives in the given skill; here they only serve as searchable anchors, you do not need to resolve them to understand the README.

## 4.1 High-level summary

This diagram summarises the sequential process of phases 00–09, the entry points, the interview loops and the defect-fixing feedback paths.

```mermaid
flowchart TD
    %% Styling definitions
    classDef setup fill:#e0f2fe,stroke:#2563eb,stroke-width:2px,color:#1e293b;
    classDef design fill:#e0f2fe,stroke:#0d9488,stroke-width:2px,color:#1e293b;
    classDef dev fill:#e0f2fe,stroke:#16a34a,stroke-width:2px,color:#1e293b;
    classDef review fill:#f3e8ff,stroke:#8b5cf6,stroke-width:2px,color:#1e293b;
    classDef doc fill:#f3e8ff,stroke:#8b5cf6,stroke-width:2px,color:#1e293b;
    classDef start fill:#f1f5f9,stroke:#64748b,stroke-width:2px,color:#1e293b;
    classDef userInput fill:#ffedd5,stroke:#ea580c,stroke-width:2px,color:#7c2d12;

    %% Entry points
    Start1(["Start in an empty project"]):::start
    Start2(["Add a new cycle"]):::start
    BS(["<b>/bs-brainstorm</b> (optional)<br/>exploratory ideation before the spec<br/>.bs-brainstorm/brainstorm-NN.md"]):::userInput

    %% Phase boxes
    0["<b>0. Project Setup</b><br/>(create conventions.md)"]:::setup
    1["<b>1. Init Cycles</b><br/>(create roadmap.md, cycle dir)"]:::setup
    2["<b>2. Create Spec</b><br/>(create spec.md)"]:::design
    3["<b>3. Create Plan</b><br/>(two steps: 03a code plan + 03b test plan → plan.md)"]:::design
    4["<b>4. Create Tasks</b><br/>(create tasks.md from plan.md)"]:::design
    5["<b>5. Analyze</b><br/>(cross-phase consistency check)"]:::design
    6["<b>6. Implement</b><br/>(create code from plan.md and tasks.md)"]:::dev
    7["<b>7. Validate</b><br/>(regression, sonar and E2E check)"]:::dev
    8["<b>8. Doc-sync</b><br/>(docs-generated/ consistency + objective gate)"]:::doc
    9["<b>9. Review and Merge</b><br/>(isolated SDD — local review + merge)"]:::review
    9a["<b>9a. Create PR</b><br/>(centralized SDD)"]:::review
    9b["<b>9b. Review</b><br/>(machine-run on the CI)"]:::review
    9c["<b>9c. Merge</b><br/>(+ post-merge tests, VP2)"]:::review
    9d["<b>9d. Dev-test</b> — optional<br/>(deploy + real E2E, VP3)"]:::review
    End([Cycle finished]):::start

    %% Clarifying interview nodes
    Int0(["User interview"]):::userInput
    Int1(["User interviews"]):::userInput
    Int2(["User interviews"]):::userInput
    Int3(["User interview"]):::userInput

    %% Starting connections
    Start1 --> 0
    Start2 --> 1

    %% Optional antechamber: the brainstorm is not a phase — it feeds phase 00/01
    %% through the cycle-design-input.md distilled from the working file (BS18).
    BS -. "no conventions.md yet" .-> 0
    BS -. "brainstorm: NN → cycle-design-input.md" .-> 1

    %% Transitions and feedback paths between the phases
    0 --> 1
    0 <--> Int0

    1 --> 2
    1 <--> Int1

    2 --> 3
    2 <--> Int2

    3 --> 4
    3 <--> Int3

    4 --> 5

    %% The analyze self-healing loop (05):
    %% on FAIL the orchestrator starts the fix mode of the earliest affected phase
    %% (02/03/04) (fixer subagents), then re-derivation along the existing 2→3→4→5
    %% forward path (02→03→04) → re-analyze, up to max X=3.
    5 -. "FAIL → spec-fixer (02 fix mode)" .-> 2
    5 -. "FAIL → plan-fixer (03 fix mode)" .-> 3
    5 -. "FAIL → tasks-fixer (04 fix mode)" .-> 4
    5 <--> Int5(["User interview<br/>(open question of a fixer → answer → continue)"]):::userInput
    5 -- "max X reached without PASS → stops + asks" --> StopAnalyze(["Loop abandoned — human decision"]):::userInput
    5 -- "PASS" --> 6

    6 --> 7

    %% The validate self-healing loop (07) — tests AND code review in one loop (RV1):
    %% on FAIL the orchestrator (07) starts the implement-fixer or the review-fixer
    %% subagent (06 fix mode) → re-validation until PASS — with three stopping
    %% limits; on a design defect it escalates upwards to 03/02 (VD5).
    7 -. "FAIL (test/Sonar/DoD or Must Fix)<br/>→ implement-fixer / review-fixer → re-validate" .-> 6
    7 <--> Int7(["User interview<br/>(3-attempt STOP / escalation)"]):::userInput
    7 -- "design defect → escalation to 03/02" --> StopValidateEsc(["Design phase (03/02) review"]):::userInput
    7 -- "stopping limit exhausted without PASS → stops + asks" --> StopValidate(["Loop stops — human decision"]):::userInput
    7 -- "PASS" --> 8

    %% Doc-sync (08): plan (doc-sync-planner) → mechanical execution → objective gate (DS22).
    %% NOT a self-healing subagent loop; on a gate failure, human-driven correction (doc-sync-questions.md).
    8 <--> Int8d(["User interview<br/>(gate failure / decision point → doc-sync-questions.md)"]):::userInput
    %% The TWO BRANCHES of the cycle end — the `## Review and merge` section of
    %% `conventions.md` decides which one runs (the PRESENCE OF A PR, not the mode).
    8 -- "isolated SDD (no PR)" --> 9
    8 -- "centralized SDD (PR required)" --> 9a

    %% Merge (09): no loop and no subagent — the review has already run in 07.
    %% If code changed since 08, doc-sync runs again first (DS23.2), then a MANUALLY confirmed merge (RD8).
    9 -. "code changed since 08 → doc-sync again (DS23.2)" .-> 8
    9 -. "code change in the loop → 08-doc-sync again" .-> 8
    9 -- "green VP2 → merge (manual confirmation, RD8)" --> End

    %% The centralized branch: the PR triggers the CI/CD, the review and the merge
    %% run as machine runs. VP2 is the gate BEFORE the code reaches main (L13-D14).
    9a --> 9b
    9b --> 9c
    9c -. "code changed → 08-doc-sync again" .-> 8
    9c -- "optional" --> 9d
    9c --> End
    9d --> End
```

## 4.2 Test points — where we test, and what it proves

In the `bs` SDD we **test in three places, for three different reasons**. The three points are not redundancy: each one proves something **different**, and the other two cannot replace the third.

1. **`validate` (07)** — we validate the implementation produced by the agent **against the spec**, on the developer's **local machine**. Typically unit and locally running component tests.
2. **post-merge test (`VP2`)** — **after merging with the main branch**. Where it runs depends on which SDD we use: it can be **part of the CI/CD process** and it can run on the **local machine**. With CI/CD: unit tests, **Sonar**, and **containerized, mocked** component tests. **Sonar is needed here too — exactly as it is in `validate`:** the merge brings in code that the Sonar round of `07` never saw, and static defects can arise from it just as runtime ones can. This is zero new machinery: the same `sonar-gate.py`, with the same `conventions.md` thresholds.
3. **dev test (`VP3`)** — after an **automatic deploy**, in a **real test system**, with e2e tests. It only makes sense on the centralized path (`/bs-dev-test`).

**And all three have to be channeled back** — this is the fourth element of the diagram, not a footnote: the report goes onto the **path of the cycle** (`test-report/<phase>/`, committed), the **notification** goes out, and the failure either goes back to the developer or — if it is switched on — into the **fix loop** of the CI.

```mermaid
flowchart LR
    classDef dev fill:#e0f2fe,stroke:#16a34a,stroke-width:2px,color:#1e293b;
    classDef review fill:#f3e8ff,stroke:#8b5cf6,stroke-width:2px,color:#1e293b;
    classDef fb fill:#ffedd5,stroke:#ea580c,stroke-width:2px,color:#7c2d12;

    VP1["<b>1. validate (07)</b><br/>local dev machine<br/>unit + local component tests<br/><i>proves: the implementation matches the spec</i>"]:::dev
    VP2["<b>2. post-merge test</b><br/>local machine OR CI/CD — depends on the SDD mode<br/>unit + <b>Sonar</b> (as in validate) + containerized, mocked component tests<br/><i>proves: it still works merged with master</i>"]:::dev
    VP3["<b>3. dev-test</b> — optional<br/>real test system, after an automatic deploy<br/>real E2E tests<br/><i>proves: it works in a real integrated environment</i>"]:::review
    FB(["<b>back-channel</b><br/>report into the cycle folder + branch · notification · fix loop"]):::fb

    VP1 --> VP2 --> VP3
    VP1 -. "FAIL" .-> FB
    VP2 -. "FAIL" .-> FB
    VP3 -. "FAIL" .-> FB
```

> **The cycle is done when the LAST enabled verification is green.** Which one is the last is stated by the `## Review and merge` section of `conventions.md` (`Post-merge tests`, `Dev deployment test`). Until then the cycle row of the roadmap carries the `⏳ waiting for verification` mark, and the generated `cycle-status.md` shows the same.

> *The earlier, full detailed process diagram lives on on its own page: [The detailed process diagram](process-diagram.md).*

## 4.7 Example prompt flow (walking through one cycle)

Walking through a concrete cycle, `cycle-02-oidc-login`, in the order of the prompts. `00`/`01` are a **one-off** setup, `02`–`09` repeat **per cycle**. Start every phase with its own starting prompt, in a **new chat session**; replace `<cycle-name>` and the other placeholders. In the block below, the `→` lines mark the interaction taking place in the phase (interview, approval, loop).

```
# ①  00 — Project initialisation  (only for an empty project, once)
Run the command: `/bs-init-project input: OIDC-based login for the mobile bank frontend`
   → the agent asks through the conventions (tech stack, tests, merge strategy) → conventions.md

# ②  01 — Managing cycles
Run the command: `/bs-add-cycles input: New cycle — OIDC login for the mobile bank frontend`
   → name proposal: cycle-02-oidc-login → "ok" → specs/roadmap.md (Done) + the cycle folder

# ③  02 — Writing the spec
Run the command: `/bs-write-spec input: @specs/roadmap.md`
   → spec-questions.md questions one by one → answers → "the spec is ready, go" → spec.md (Ready for planning)

# ④  03a — Writing the code plan
Run the command: `/bs-write-code-plan input: @specs/cycle-02-oidc-login/spec.md`
   → mandatory first question: E2E test strategy → answers → "approved" → plan.md (Ready for test planning)

# ⑤  /clear, then 03b — Writing the test plan (into the same plan.md)
Run the command: `/bs-write-test-plan input: @specs/cycle-02-oidc-login/plan.md`
   → the phase ITSELF runs the gate of the code plan (D5) → TS-NN scenarios → "approved" → plan.md (Ready for tasks)

# ⑥  04 — Writing the tasks
Run the command: `/bs-write-tasks input: @specs/cycle-02-oidc-login/plan.md`
   → "go" → tasks.md (Ready for implementation)

# ⑦  05 — Analyze
Run the command: `/bs-analyze input: @specs/cycle-02-oidc-login`
   → cross-phase check; from the items found, YOU choose (triage) what it should fix → self-healing loop on analyze-task.md → analyze-report.md (PASS)

# ⑧  06 — Implementation
Run the command: `/bs-implement input: @specs/cycle-02-oidc-login/tasks.md`
   → code + progress in tasks.md → tasks.md (Ready for validation)

# (at any time after 05, an unnumbered step) — the manual test plan
# Run the command: `/bs-manual-test-plan input: @specs/cycle-02-oidc-login`
#    → manual-test-plan.md (in Planned or As-built mode) — not a phase, it changes no status

# ⑨  07 — Validation
Run the command: `/bs-validate input: @specs/cycle-02-oidc-login`
   → fast tests → Sonar + code review (reviewer subagent) → heavy tests + DoD;
     on FAIL a self-healing loop → PASS → status of spec/plan/tasks: Done

# ⑩  08 — Doc-sync
Run the command: `/bs-doc-sync input: @specs/cycle-02-oidc-login`
   → updating docs-generated/ + the objective gate → consistent documentation

# ⑪  09 — Review and merge  (the PR-less path; with a PR: /bs-create-pr → /bs-review → /bs-merge)
Run the command: `/bs-review-and-merge input: @specs/cycle-02-oidc-login`
   → gates (status + clean review + doc-sync) → bring in main → VP2 round (tests + Sonar)
   → merge (with manual confirmation) → closing the roadmap + cycle-status.md
```

The next cycle (`cycle-03-...`) starts with `02` again — `00`/`01` do not repeat.
