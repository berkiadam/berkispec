<!-- Source note: the "Handling open questions" section of 04-write-tasks,
     extracted so that the tasks-fixer subagent prompt can inline it too (BD14/b). -->
## Handling open questions (tasks-questions.md)

`tasks-questions.md` is the question register of the tasks phase, following the pattern of `spec-questions.md` / `plan-questions.md`. **Scope:** it is primarily used by the Fix mode (see below), when a task-level decision comes up; the normal 04 flow may also reference it if a question arises, instead of the usual "STOP and report" (e.g. an interruption-safe record when continuing in a new session).

**Structure** (if it does not exist yet, create it in the `specs/cycle-NN-<cycle-name>/` folder):

```md
<!-- INCLUDE:lang/questions-tasks.md#tasks-questions-struktura -->
```

**Rules** (identical to the spec/plan question register):
- **One** question goes in front of the user at a time — wait for the answer.
- We **never delete** from the list — a closed question is marked with `[x]`, the decision stays.
- A new question goes to the end of the list with the next sequential `Qnn` number.
- **`tasks.md` status interaction:** if there is at least one open `[ ]` question in `tasks-questions.md`, `tasks.md` **cannot be** `<status:ready_for_implement>`. The status stays `<status:draft>` until every question is `[x]`. (In Fix mode, according to the `[analyze-loop]` marked equivalents — see below.)
