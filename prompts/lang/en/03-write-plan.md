<!--
  The PROJECT-LANGUAGE blocks of `03-write-plan` (9.4 extraction).
  The installer inlines this file at build time in place of the INCLUDE markers,
  according to the chosen PROJECT language (`PROJECT_LANG`); the marker form is
  `lang/03-write-plan.md#<anchor>`.
  The blocks were moved here VERBATIM — do not rephrase, do not unify.
  The ANCHOR lines are NOT part of the inlined text, they are delimiters only (8.9).
  CAUTION: no comment-closing sequence may appear in this leading note.
-->

<!-- ANCHOR:plan-questions-struktura -->
# Cycle NN: <title> — Plan questions

- [ ] Q01 — [question text]
- [x] Q02 — [question text] → [decision / short answer]
- [ ] Q03 — [question text] _(raised by answering Q02)_

<!-- ANCHOR:statusz-megerosites -->
*"The plan quality check passed and every question is closed. Is the plan ready for writing tasks? If you confirm, I will switch it to `Ready for tasks` status."*

<!-- ANCHOR:zaro-uzenet -->
> *"The plan is done. We can continue with step 4 (tasks). Before starting the new phase, be sure to run a `/clear` command to empty the context, then use this command:*
> ```
> /bs-write-tasks input: @specs/cycle-NN-<cycle-name>/plan.md
> ```"*
