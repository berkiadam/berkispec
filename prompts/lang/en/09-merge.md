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

<!-- ANCHOR:L13-D1-pr-kotelezo -->
> *"According to the `## Review and merge` section of `conventions.md`, this project **submits PRs** (`PR submission: yes`). `/bs-review-and-merge` may only be used in the PR-less mode — with a PR the end of the cycle is three separate steps:*
> ```
> /bs-create-pr input: @specs/cycle-NN-<cycle-name>
> /bs-review     input: @specs/cycle-NN-<cycle-name>
> /bs-merge      input: @specs/cycle-NN-<cycle-name>
> ```
> *Start with `/bs-create-pr`."*

<!-- ANCHOR:L13-D1-pr-felesleges -->
> *"According to the `## Review and merge` section of `conventions.md`, this project does **not submit PRs** (`PR submission: no`) — the cycle closes with the `/bs-review-and-merge` skill, in a single step. Should I open a PR anyway (e.g. because this cycle needs an external review), or shall we switch to `/bs-review-and-merge`?"*

<!-- ANCHOR:zaro-uzenet-create-pr -->
> *"The PR is open: `<PR link>`. The cycle branch is pushed and `cycle-status.md` is updated — on the roadmap the cycle stands at `⏳ waiting for verification`, because the post-merge verification is still ahead.*
>
> *The next step is the review on the PR. Before it, run a `/clear` command to empty the context:*
> ```
> /bs-review input: @specs/cycle-NN-<cycle-name>
> ```
> *In centralized SDD the CI/CD starts this automatically when the PR is opened — in that case you have nothing to do, just wait for the notification."*

<!-- ANCHOR:zaro-uzenet-review -->
> *"The review ran on the PR, its result is in `test-report/ci-code-review.md`. The local review of `07` (`test-report/code-review.md`) is untouched — the gate of `bs-merge` reads both.*
>
> *The next step is the merge with the post-merge test round. Before it, `/clear`:*
> ```
> /bs-merge input: @specs/cycle-NN-<cycle-name>
> ```"*

<!-- ANCHOR:zaro-uzenet-merge -->
> *"The post-merge test round (`VP2`) was green, its evidence is in the `test-report/post-merge/` folder, and the cycle has been merged into the main branch.*
>
> *If the dev test is switched on in `conventions.md` (`Dev deployment test: yes`), the cycle is NOT closed yet — the last verification is still ahead:*
> ```
> /bs-dev-test input: @specs/cycle-NN-<cycle-name>
> ```
> *If it is not switched on, the cycle is closed. Before starting the next cycle, run a `/clear` command:*
> ```
> /bs-add-cycles
> ```"*

<!-- ANCHOR:zaro-uzenet-dev-test -->
> *"The dev test round (`VP3`) ran in the integrated environment, its evidence is in the `test-report/dev-test/` folder<the test manager run URL, if any>. This was the last enabled verification point, so I closed the cycle on the roadmap.*
>
> *The next cycle can begin. Before it, be sure to run a `/clear` command to empty the context:*
> ```
> /bs-add-cycles
> ```"*
