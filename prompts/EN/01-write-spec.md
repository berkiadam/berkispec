# 01 - Write Spec

Use this prompt when you want to create the specification for a new cycle or feature.

## Required User Input

The user prompt must contain at least these two fields:

```text
Cycle name:
<short cycle name goes here>

Goal:
<textual goal description goes here>
```

## Agent Validation

Before writing a specification:

1. Check that the user prompt contains a `Cycle name` field.
2. Check that the user prompt contains a `Goal` field.
3. If either one is missing, do not create a file. Reply with:

```text
Validation error: creating a spec requires the `Cycle name` and `Goal` fields.
```

4. If both fields are present, assign an automatic cycle number.
5. Choose the number based on the existing `specs/cycle-*` folders: largest existing cycle number + 1.
6. The cycle folder name must be:

```text
specs/cycle-XX-<slug>/
```

The `<slug>` must be a short, lowercase, hyphenated version of `Cycle name`.

Example:

```text
Cycle name:
TMP token refresh error handling E2E

Goal:
Prove with an E2E test that the TMP returns a controlled error when the FlowX refresh grant fails.
```

If the largest existing cycle is `cycle-07-*`, the new file location is:

```text
specs/cycle-08-tmp-token-refresh-error-handling-e2e/spec.md
```

## Usable User Prompt Example

```text
Cycle name:
<write the short cycle or feature name here>

Goal:
<describe what you want to achieve or prove here>
```

## Agent Task

If validation succeeds:

```text
Task:
- read the relevant project documentation and code
- understand the current behavior
- create a new `specs/cycle-XX-<slug>/spec.md` file
- do not implement code
- do not create a plan or tasks file in this phase
- read and consider `.berkispec/project-desc.md`
- compare the `.berkispec/project-desc.md` "Reference Files" section with the user goal and the evolving spec
- if there is any inconsistency between project description, reference files, user input, or the evolving spec, do not invent a solution, ask a clarifying question
- if any essential information is missing, ask a clarifying question
- if multiple valid interpretations exist, ask a clarifying question

The `spec.md` file contains:
- goal
- background and motivation
- scope
- out of scope
- affected user or system flow
- functional requirements
- error handling and edge case expectations
- affected components at a high level
- required tests / proof methods
- definition of done
- open questions

Expectations:
- include an explicit status field in the spec in one of these forms:
  - `## Status` section with `DRAFT` or `READY_FOR_PLAN`
  - or `Status: DRAFT` / `Status: READY_FOR_PLAN` line
- for a newly created spec, the initial status must be `DRAFT`
- the spec must be decision-ready, but it must not be an implementation plan
- where you are uncertain, add a local inline marker:
  [NEEDS CLARIFICATION Q001: short question]
- track all open questions in:
  ## Nyitott kérdések
  - [ ] Q001: short question
    - Kontextus: ...
    - Miért fontos: ...
    - Státusz: OPEN
    - User válasz: _még nincs_
    - Döntés: _még nincs_
- keep question IDs stable and increasing: Q001, Q002, Q003...
- do not invent a new architecture if the repo's existing patterns are sufficient
- while at least one open question exists, keep the spec status as DRAFT
- set status to READY_FOR_PLAN only when there are no open questions, no inline [NEEDS CLARIFICATION ...] markers, and the plan can be safely created from the spec
- at the end, summarize which questions need human approval
```
