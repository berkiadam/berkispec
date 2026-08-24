<!--
  The PROJECT-LANGUAGE blocks of `09-merge` (9.4 extraction).
  The installer inlines this file at build time in place of the INCLUDE markers,
  according to the chosen PROJECT language (`PROJECT_LANG`); the marker form is
  `lang/09-merge.md#<anchor>`.
  The blocks were moved here VERBATIM — do not rephrase, do not unify.
  The ANCHOR lines are NOT part of the inlined text, they are delimiters only (8.9).
  CAUTION: no comment-closing sequence may appear in this leading note.
-->

<!-- ANCHOR:RD8-merge-megerosites -->
> *"Validation and review are clean (07), the doc-sync gate is green. I am ready to merge according to the `<provider>` strategy (`feature/cycle-NN-<cycle-name>` → `<target branch>`). May I proceed?"*

<!-- ANCHOR:zaro-uzenet -->
> *"Validation and code review succeeded in 07, the doc-sync gate is green, and I closed the cycle according to the Merge strategy in `conventions.md` (`<local squash merge` / `PR created>`). The cycle closed successfully.*
>
> *The next cycle can begin. Before starting the new cycle, be sure to run a `/clear` command to empty the context.*
>
> *To add a new cycle:*
> ```
> /bs-add-cycles
> ```
> *Or, if the next cycle is already on the roadmap, straight to the spec phase:*
> ```
> /bs-write-spec input: @specs/roadmap.md, cycle: cycle-NN-<cycle-name>
> ```"*
