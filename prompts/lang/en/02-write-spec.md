<!--
  The PROJECT-LANGUAGE blocks of `02-write-spec` (9.4 extraction).
  The installer inlines this file at build time in place of the INCLUDE markers,
  according to the chosen PROJECT language (`PROJECT_LANG`); the marker form is
  `lang/02-write-spec.md#<anchor>`.
  The blocks were moved here VERBATIM — do not rephrase, do not unify.
  The ANCHOR lines are NOT part of the inlined text, they are delimiters only (8.9).
  CAUTION: no comment-closing sequence may appear in this leading note.
-->

<!-- ANCHOR:spec-questions-struktura -->
# Cycle NN: <title> — Spec questions

- [ ] Q01 — [question text]
- [x] Q02 — [question text] → [decision / short answer]
- [ ] Q03 — [question text] _(raised by answering Q02)_

<!-- ANCHOR:statusz-megerosites -->
*"The spec quality check passed and every question is closed. Is the spec ready for planning? If you confirm, I will switch it to `Ready for planning` status."*

<!-- ANCHOR:zaro-uzenet -->
> *"The spec is done. We can continue with step 3 (plan). Before starting the new phase, be sure to run a `/clear` command to empty the context, then use this command:
> ```
> /bs-write-code-plan input: @specs/cycle-NN-<cycle-name>/spec.md, cycle: cycle-NN-<cycle-name>
> ```"*
