# 02 - Write Plan

Use this prompt when you want to create a technical implementation plan based on an approved `spec.md`.

```text
Create an implementation plan based on this specification:

specs/<cycle-name>/spec.md

The plan location:

specs/<cycle-name>/plan.md

Task:
- read the `spec.md` file
- read the relevant code and documentation
- create a `plan.md` file
- do not implement code
- do not create a tasks file in this phase

The `plan.md` file contains:
- goal and approach
- affected components
- affected files or modules
- planned changes
- configuration / runtime changes
- data flow or request flow
- testing and verification strategy
- execution order
- risks
- decision points

Expectations:
- the plan must start from the spec and must not introduce new scope
- indicate if the spec is incomplete or contradictory
- prefer the repo's existing patterns
- clearly mark changes that carry production risk
- at the end, state whether the tasks file can be created based on the plan
```
