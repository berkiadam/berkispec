<!--
  The PROJECT-LANGUAGE blocks of `06-implement` (9.4 extraction).
  The installer inlines this file at build time in place of the INCLUDE markers,
  according to the chosen PROJECT language (`PROJECT_LANG`); the marker form is
  `lang/06-implement.md#<anchor>`.
  The blocks were moved here VERBATIM — do not rephrase, do not unify.
  The ANCHOR lines are NOT part of the inlined text, they are delimiters only (8.9).
  CAUTION: no comment-closing sequence may appear in this leading note.
-->

<!-- ANCHOR:check-log-sablon -->
# `[CHECK]` run log — cycle-NN-<cycle-name>

_(Append-only. Written by 06-implement, per task. 07/09 do not write into it.)_

| Time | Task | Attempt | Mode | Command | Result |
|---|---|---|---|---|---|
| 2026-08-07 09:58 | T003 | 1/3 | normal | `npx tsx --test test/unit/token-store.test.ts` | ✗ 0 passed / 1 failed — `refreshes once for 5 parallel readers` (RED1: the test exists, the implementation does not yet) |
| 2026-08-07 10:12 | T004 | 1/3 | normal | `npm test -- token-store` | ✗ 12 passed / 1 failed — `initHash returns stable hash` |
| 2026-08-07 10:19 | T004 | 2/3 | normal | `npm test -- token-store` | ✓ 13 passed / 0 failed / 0 skipped |
| 2026-08-07 11:40 | T041 | 1/3 | validate-loop | `npm test -- auth` | ✓ 27 passed / 0 failed / 0 skipped |

## Notes
- **T004** — temporary port swap for running the `[CHECK]`: 5432 → 5433 (`docker-compose.yml`); restored before the commit.
- **RED-EXEMPT: TREG1** — the existing test in `test/e2e/auth-login.spec.ts` is rightly green after the middleware change too; the task only updates the selector.

<!-- ANCHOR:check-log-pelda-sor -->
## <Task ID> — <short title>

**What the problem was:** <concise description of the failure>
**What we tried:** <unsuccessful attempts, briefly>
**What the solution was:** <the approach that finally worked>

<!-- ANCHOR:commit-javaslat -->
*"It is worth committing these before the implementation — if the implementation goes wrong, a `git reset --hard` restores the starting state."*

<!-- ANCHOR:commit-kerdes -->
*"Should I commit these now?"*

<!-- ANCHOR:zaro-uzenet -->
> *"The implementation is done. We can continue with step 7 (validate). Before starting the new phase, be sure to run a `/clear` command to empty the context, then use this command:*
> ```
> /bs-validate input: @specs/cycle-NN-<cycle-name>
> ```"*
