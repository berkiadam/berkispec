<!--
  The PROJECT-LANGUAGE blocks of `git-preflight` (9.4 extraction).
  The installer inlines this file at build time in place of the INCLUDE markers,
  according to the chosen PROJECT language (`PROJECT_LANG`); the marker form is
  `lang/git-preflight.md#<anchor>`.
  The blocks were moved here VERBATIM — do not rephrase, do not unify.
  The ANCHOR lines are NOT part of the inlined text, they are delimiters only (8.9).
  CAUTION: no comment-closing sequence may appear in this leading note.
-->

<!-- ANCHOR:BD13-commit-vagy-folytas -->
*"Should I commit these now, or shall I continue?"*

<!-- ANCHOR:PW3-soros-vagy-parhuzamos -->
*"The branch of cycle `<other-cycle>` is still open. There are two options: **A)** we close it (merge/PR), you switch back to `main`, and we plan the new cycle here — or **B)** we work in parallel: I open a separate `git worktree` for it, and the planning starts there. Which one shall we go with?"*

<!-- ANCHOR:PW3-worktree-ujrainditas -->
*"I created the worktree here: `<the ABSOLUTE path of the worktree>` — the tool directories (skills, subagents, gate scripts) have been copied over. I cannot continue in this session, because the agent is bound to the current directory. Please: **(1)** close this agentic CLI, **(2)** change into the other directory: `cd <the ABSOLUTE path of the worktree>`, **(3)** start the same tool again there (`<the start command of the tool>`), **(4)** and re-run this phase. This directory and the branch of the current cycle stay untouched."*
