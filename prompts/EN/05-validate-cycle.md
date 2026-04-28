# 05 - Validate Cycle

Use this prompt when you want a separate validation pass at the end of a cycle to check whether everything is complete.

```text
Validate the closure of this cycle:

specs/<cycle-name>/spec.md
specs/<cycle-name>/plan.md
specs/<cycle-name>/tasks.md

Task:
- check whether all relevant tasks in `tasks.md` are complete
- check whether the definition of done items in `spec.md` are satisfied
- check whether the main technical decisions in `plan.md` were implemented or documented as changed
- run the relevant tests
- check that the test report exists and that its content is valid
- do not introduce a new feature

If you find a gap:
- fix it if it is small and clearly within scope
- if it requires a larger decision, document it as an open question

At the end:
- update the statuses in `tasks.md`
- update the status in `spec.md`
- create a short closing summary
- list the tests that were run
- list remaining risks, or state that there are no known remaining risks
```
