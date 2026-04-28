# 04 - Implement Tasks

Use this prompt when you want to start the actual implementation of a cycle.

```text
Execute this cycle:

specs/<cycle-name>/spec.md
specs/<cycle-name>/plan.md
specs/<cycle-name>/tasks.md

Task:
- work from `tasks.md`
- follow the technical direction in `plan.md`
- use `spec.md` as the behavior and scope reference
- implement the required code and documentation changes
- check off completed tasks in `tasks.md`
- do not modify unrelated code

Working rules:
- if a task is too large, split it into smaller tasks in `tasks.md`
- if the plan turns out to be wrong, update the plan with a short rationale
- if the spec is incomplete, stop and flag the open question
- diagnostic or test endpoints with production risk may only be active behind an explicit test flag
- after each change, run the relevant test when practical

Verification:
- run the commands listed in the verification section of `tasks.md`
- if a command cannot be run, document why
- when a test fails, investigate and fix it if it is within the cycle scope

At the end:
- update task statuses
- update the spec status if the cycle is complete
- create or update the test report if requested by the tasks
- summarize the modified files
- summarize which tests were run
- flag remaining risks
```
