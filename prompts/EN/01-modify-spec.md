# 01 - Modify Spec

Use this prompt when an existing `spec.md` file must be refined based on the AI's previous questions and the user's new clarifications.

## Agent Task

```text
Task:
- read the existing spec.md file
- read the previous Codex response or open questions
- read the user's new clarification
- read and consider `.berkispec/project-desc.md`
- compare the `.berkispec/project-desc.md` "Reference Files" section with the user goal and the evolving spec content
- update spec.md so the user's clarification is incorporated
- do not create plan or tasks files
- do not implement code

Clarification rules:
- if there is any inconsistency between project description, reference files, user input, or existing spec, do not invent a solution, ask a clarifying question
- if essential information is missing, ask a clarifying question
- if multiple interpretations are possible, ask a clarifying question

Qxxx handling:
- find the related Qxxx question
- incorporate the user's answer in the relevant spec section
- remove or resolve the related inline [NEEDS CLARIFICATION Qxxx: ...] marker
- in "Nyitott kérdések", mark the question resolved or move it to resolved decisions
- record the final decision
- if a new question appears, create a new Qxxx ID

Resolved decisions:
- maintain a "## Tisztázott döntések" section with:
  - Qxxx: original short question
  - User válasz: ...
  - Döntés: ...
  - Érintett spec rész: ...

Status:
- always keep an explicit status field in the spec:
  - in a `## Status` section or as a `Status: ...` line
- keep status as DRAFT while any OPEN question or [NEEDS CLARIFICATION ...] marker exists
- set status to READY_FOR_PLAN only when there are no OPEN questions and no markers
```
