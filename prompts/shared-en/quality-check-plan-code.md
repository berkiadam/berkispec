<!-- Source note: this section is inlined by the 03a-write-code-plan.md skill AND the
     plan-fixer agent (build-time INCLUDE). Edit it in one place. Its test-side pair is
     quality-check-plan-test.md (D7). -->
## Quality check — before closing the code plan

Before you switch to `<status:ready_for_test_plan>` status, ask yourself:

- **🔴 SELF-CONTAINEDNESS INVENTORY — go through it item by item.** For every row the answer is either "it is there, concretely", or "it is not applicable to this cycle". "The implementer will figure it out" is **not** an acceptable answer:

  | # | Is it needed in the plan? | Check |
  |---|---|---|
  | 1 | the **full path** of the affected files | there is no "in the appropriate module" kind of hint |
  | 2 | function/class names, **signatures, interface change** | the calling side also knows what it calls and what it gets |
  | 3 | data structures **with concrete fields**, an example request/response | not just a list of field names — an **actual payload** |
  | 4 | error branches: condition → status + errorCode + body | there is a counterpart for every error case in the spec |
  | 5 | configuration: the **name AND the value** of the env variable, where it is set | there is no "to be configured" on its own |
  | 6 | external integration: URL, port, realm/client/scope, test user, an example `curl` | the call is **copy-pastable and runnable** |
  | 7 | runnable commands **verbatim** (build, deploy, startup, test) | there is no "run `build.sh`" kind of hint |
  | 8 | execution order + prerequisites | what depends on what, what is needed before it |
  | 9 | migration and rollback, if there is a schema change | — |
- **🔴 Is the <sec:environment_coords> section done? (KO1)** — The `<sec:environment_coords>` section **exists and is filled in**: (a) for every component the base URL, port(s), health endpoint, the **verbatim start and stop command**, repo path/image; (b) for every required REST call the verb + the full URL + the headers + the **concrete request body** + the expected response + the field to be extracted, **including the token acquisition**, with a copy-pastable `curl` example; (c) **every test and API user listed with its password/credential** (a dev-scoped value concretely, a cluster/registry/VPN/IAM/production credential **as a pointer**, TC5); (d) every further parameter needed for the development/testing (identifiers, scope, client-id, namespace, timeout); (e) the network/access prerequisites. **A placeholder and an empty cell are forbidden** — whatever is missing or outdated is a `Qnn` question in `plan-questions.md`; where something is not applicable, `—` stands. If a coordinate appears in the spec, in `test-conventions.md` or in the conversation but not here, the quality check **FAILS**.
- **Artifact voice (AV1)?** — Is there no skill-voiced meta instruction in the plan (`🔴`, `[!CAUTION]`, "It is forbidden…", "it is mandatory…", "go through…")? Whatever originates from a rule appears as a **decision** (e.g. "the tag of the image is unique per run: `v1-<UTC timestamp>`"), and the justification is in the `<sec:risks_and_decisions>` section.
- **🔴 No undecided alternative.** The plan **must not contain a choice**: there is no "`X` **or** `Y`", "possibly", "or the new …", no two ports/URLs/identifiers for the same thing, no two possible expected responses in it. The plan is an **execution instruction**, not a deliberation — if there really are two options, that is a **`plan-questions.md` question**, and the plan can only be closed with the **decided**, concrete variant. (Typical occurrences: the `data-testid` values of test identifiers, mock ports, old/new element names during a rename.)
- **Does the referenced script/file exist or is it planned?** — Go through **every** file and script that the plan wants to run (the commands of `<sec:verification_strategy>`, test steps, the E2E startup, `[CHECK]`-like verifications): each of them **either already exists in the repo**, or appears among the `<sec:planned_changes>` as a **new file**. A script to be run but created nowhere is a sure failure at execution time.
  - **The entry point matches:** the **file** run by the verification command and the **test artifact** planned in the `<sec:test_specification>` should be the same. A typical error: the plan creates a `..._test.py` file, while the verification command runs a `....sh` wrapper that nobody plans — in that case either the wrapper also has to be added to the `<sec:planned_changes>` (with a name according to the convention of the project), or the command has to call the planned file directly. **The two must not hang apart.**
- **Cross-document consistency.** The same resource appears **everywhere with the same** URL, port, identifier and path — within the plan **and** with respect to the spec as well. If a path/host differs between the spec and the plan (or between two places in the plan), **one of them is wrong**: stop yourself, and clarify it (`plan-questions.md`), do not let a `[CHECK]` fail on it later.
- **Is `docs-generated/` not among the planned changes? (DS4)** — The generated documents are the property of 08-doc-sync; if they got in, delete them from the `<sec:planned_changes>`. The README of an **existing** component cannot be planned either (that is also the business of 08) — **only the first README of a new component** may go here.
- **Is a destructive operation touching a shared environment complete? (approval + immutable identifier + rollback)** — If the plan modifies a shared cluster/registry/database, are all three present? In the case of an overwritten image tag or configuration **there is nothing to restore to** — this is a blocking deficiency.
- **🔴 Does every `[P-…]` entry state its PURPOSE? (WY1)** — **Every** `[P-…]` section of the `<sec:planned_changes>` carries a `**<field:f_purpose>:**` line: what we want to achieve (the behaviour AFTER the change), why (the gap or defect it eliminates), and from which spec source (`DoD-NN` or requirement — the same one that stands for this ID in the `<sec:reverse_coverage>` table). **Repeating the change is not a purpose** ("we introduce the `getX()` method"), and neither is the file name ("we update the config"). If you cannot write a purpose for an entry, it is either scope leakage (it has no spec source) or a `plan-questions.md` question.
- **Was the reference resolution done?** — Is there no sentence in the plan that **references a script, a procedure, an existing test or an external API** without writing out the concrete detail needed from it (command, URL, payload schema, parameter)? If the input was phrased at a high level of abstraction, **did you go down to the source**?
- **Is there no forbidden phrasing?** — "see the spec", "in the usual way", "to the appropriate endpoint", "run `build.sh`", "with the parameters of the earlier cycle", `<here comes …>`, `TODO`.
- Is anything still missing from the plan?
- Is there anything that is unclear or ambiguous?
- Does every affected file appear in the planned changes?
- **Updating the documentation:** is every description, README and diagram (e.g. a `.drawio` file) affected by the changes listed among the planned changes?
- **Comments and docstrings:** do the planned changes take into account the updating of the comments and descriptions in the source code according to the new naming/behavior?
<!-- INCLUDE:shared/path-format.md -->
- **Section IDs (PID1):** does every executable plan section bear a unique `[P-…]` ID, are the earlier ones unchanged, and did an inventory section get no ID?
- **Scope gate (SC1):** is the `<sec:reverse_coverage>` table filled in, does every plan capability have a spec source (or <sec:out_of_scope> / a question)? The first column bears the `[P-…]` identifier of the section, the second the `DoD-NN` — the coverage chain of 05 runs on this (`S3`).
- **<sec:config_lifecycle> (KF1):** is there a row in the table for every new/modified parameter, filled in **for every run mode** (local, test, container/compose, dev deploy) + the "if it is missing" behavior?
- **Anchor verification:** is every `file:location` and "this symbol/assertion is there" claim confirmed with Grep/Read?
- **Value sanity:** are the ports, time units, URL scheme↔port, versions, paths reviewed (a typical typo: `433` instead of `443`)?
- **Does the gate configuration move along? (GC1)** — If the cycle touches the report structure, the report commands, the Sonar configuration, the test commands, the ports or the merge strategy: does the **affected section of `conventions.md` appear in the `<sec:planned_changes>`, with concrete new content**, and can 04 write a task for it? (Updating `specs/test-conventions.md` is **not** a substitute for this — the TR3 gate reads `conventions.md`.)
- **Did the elaborated spec artifacts come over WITHOUT TRUNCATION? (KX3)** — Go through the code blocks (OpenAPI/JSON/YAML/SQL/payload), error matrices and multi-step test scenarios of the spec: does each of them appear in the plan **verbatim and in full**? Is there no merged step, no payload replaced by a list of field names, no table replaced by prose, and no "see the spec" / "the other cases are similar" reference? **The affected section of the plan is not shorter than its source section in the spec** — and if it is, can you name where the rest went?
- **Is `cycle-design-input.md` processed? (CD1)** — If the file exists and contains substantive content, did you read it, and does every technical/procedural item of it have a traceable fate: it was incorporated into `plan.md` **verbatim, self-containedly** (not as a reference!), or it moved into `tasks-`/`validate-input-from-prev.md`, or it became a `Qnn` question, or it is a spec deficiency directed back into 02. Did you leave the file **unchanged**?
- **Is every item of `plan-input-from-prev.md` closed? (IP1)** — If the file exists, no `[ ]` item may remain in it: each one is either incorporated into `plan.md` (the note shows where), or explicitly dropped with a justification.
- **Was the valuable information left out of the plan handed over? (IP1)** — Did a task-level preparatory step go into `tasks-input-from-prev.md`, and a validation-specific runtime prerequisite into `validate-input-from-prev.md`?
- Is every required schema artifact identified and present in the table?
- **Database changes:** if the cycle introduces a schema change/a new entity, is the migration and rollback (restore) scenario planned and documented?
- Is the status of every schema artifact `<status:reviewed>`? (If there is a `<status:review_required>`, the plan cannot be closed.)
- **Constitution Check (SK4):** is every plan decision (tech stack, naming, structure, test tool, merge strategy, security) in line with `conventions.md`?
  - **A small deviation** (e.g. refining a name): add it to `plan-questions.md`, and ask the user about it.
  - **A severe deviation** (it fundamentally conflicts with the conventions): **STOP**, back to phase `02` or `00` to review the convention.
- **🔴 Has the code-plan gate run, and is its trace inside? (GS2/a)** — Before closing, did you actually run `analyze-gate-check.py --plan-code-only`, did it return `0`, and is the result visible in **two places**: in the `**<field:f_gate_code>:**` line of the `plan.md` header and in the `ANALYZE-GATE: …` line of your phase-closing answer? The status field is self-declared — the entry gate of `03b` **runs this very gate again** (D5), so an untrue stamp comes out one phase later anyway.
- **🔴 You are NOT the one who writes the test sections.** You do **not even open** the `<sec:testing_strategy>`, `<sec:plan_test_scenarios>`, `<sec:machine_run_table>`, `<sec:e2e_infrastructure>`, `<sec:regression_impact>` and `<sec:test_specification>` sections, and you write no `TS-NN` / `TC-NN` identifier. If the test cases of the spec are "pushing to get out", they are inputs of `03b` — you may add the corresponding row to the `<sec:reverse_coverage>` table, but not the scenario. **Why this is a gate:** a half-finished test section is **worse than an empty one**, because the `TS7` conversion of `03b` would carry an already existing, faulty structure forward — exactly the defect this phase was split for.

If any of these is not satisfied (or something is missing), complete the plan before you close it.

---

## Closing gate — the self-containedness, coordinates and scope of the code plan (TP2-code)

> **You must run this list item by item BEFORE the `<status:ready_for_test_plan>` status, and print the ticked list in your answer.** Not "by feel" — for every item name **where** it is satisfied (section, `[P-…]` ID), or why it is not applicable in this cycle. **With a single `[ ]` left the code plan cannot be closed** — fix it and run the list again.

```
<!-- INCLUDE:lang/quality-check-plan.md#TP2-code -->
```

**Why this is a gate and not a checklist row:** `03b` works from your output, and the **literal values** of the `TA1` data sheets, the `TS-NN` calls and the machine-readable run table come from here. A missing coordinate is still one line here; in the test plan a whole scenario would already be built on guesswork — and the entry gate of `03b` (D5) sends it back here anyway.
