<!--
  The PROJECT-LANGUAGE blocks of `03a-write-code-plan` (9.4 extraction).
  The installer inlines this file at build time in place of the INCLUDE markers,
  according to the chosen PROJECT language (`PROJECT_LANG`); the marker form is
  `lang/03a-write-code-plan.md#<anchor>`.
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
*"The code-plan quality check passed and every question is closed. Is the code half of the plan ready for test planning? If you confirm, I will switch it to `<status:ready_for_test_plan>` status."*

<!-- ANCHOR:zaro-uzenet -->
> *"The code plan is done. We can continue with the test plan. Before starting the new phase, be sure to run a `/clear` command to empty the context, then use this command:*
> ```
> /bs-write-test-plan input: @specs/cycle-NN-<cycle-name>/plan.md
> ```"*
