# 03 - Write Tasks

Use this prompt when you want to create an executable task list based on the approved `spec.md` and `plan.md`.

```text
Create an execution task list based on these files:

specs/<cycle-name>/spec.md
specs/<cycle-name>/plan.md

The task list location:

specs/<cycle-name>/tasks.md

Task:
- read the spec and the plan
- create a checkbox-based `tasks.md` file
- do not implement code

The `tasks.md` file must be:
- concrete
- checkable
- broken down into small steps
- tied to files, components, or verifiable outputs
- ordered by execution sequence

The task list contains:
- code change tasks
- documentation tasks
- test / verification tasks
- report / closing tasks

Format:

- [ ] T001 ...
- [ ] T002 ...
- [ ] T003 ...

Expectations:
- no task should be too large
- no task should be vague, such as "fix the behavior"
- every important DoD item must have a corresponding task or verification task
- at the end, include a `Status` section with the value `READY_FOR_IMPLEMENTATION`
```
