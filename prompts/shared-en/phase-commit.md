<!--
  SHARED description of the PHASE-CLOSING COMMIT (02/03/04 — artifact-writing phases,
  05/07 — self-healing loop phases).
  This is NOT a standalone skill/agent, but a shared text block that the installer
  (install-helper.py) embeds INLINE at build time into the installed version of the
  referencing skill (in place of the `<!-- INCLUDE:shared/phase-commit.md -->` marker).
  Referenced by: 02-write-spec, 03a-write-code-plan, 03b-write-test-plan, 04-write-tasks, 05-analyze, 07-validate.
  The skill declares its own `<PHASE-TAG>` (e.g. `02-spec`) and the closing status
  BEFORE the marker — this block contains only the shared, mandatory procedure.
  It has no frontmatter: its content is copied in verbatim. Edit it here.
-->

### Phase-closing commit (a mandatory step)

> **A phase is not done because the status changes, but because the status change is COMMITTED.** After the user's "done / go ahead / yes" confirmation, writing the status and the commit are **a single, uninterruptible pair of steps** — do not ask, do not wait, do not start other work in between.

> **In loop phases (05-analyze, 07-validate)** the same rule applies, with one addition: there is **no** intermediate commit **during** the loop, the phase-closing commit happens **once**, when the loop is closed — but it is **mandatory on every closing branch**, without exception: PASS, giving up at `max X` / a 3-attempt STOP, escalation upwards (e.g. back to 03), a Quality Gate failure. There is no outcome that returns control to the user without a commit.

**Order (exactly this, without skipping):**

1. **No-VCS gate:** if, according to the `## <sec:cv_git_conventions>` section of `conventions.md`, there is **no version control**, steps 2–5 are skipped — the phase closes with writing the status. Otherwise continue.
2. **Rewriting the <field:f_status>** in the artifact (to the closing status of the phase). **In a loop phase (05, 07)** this also includes writing the status of the report/log and arranging the `[analyze-loop]` / `[validate-loop]` marker, according to the rule of the given closing branch.
3. **Stage + commit** — for the folder of the cycle, with the tag of the phase:
   ```bash
   git add specs/cycle-NN-<cycle-name>/
   git commit -m "cycle-NN: <PHASE-TAG>"
   ```
   The commit is made **on the feature branch of the cycle** (BD4), not on `main`. If you happen to be on `main`, STOP — tell the user, do not commit.
4. **Verification (deterministic, not "by feel"):** run
   ```bash
   git log -1 --oneline && git status --short specs/cycle-NN-<cycle-name>/
   ```
   - The first line of `git log` must show the `cycle-NN: <PHASE-TAG>` commit just made.
   - The output of `git status --short` for the folder of the cycle must be **empty**.
   - If either does not hold (an empty commit, a hook rejected it, a forgotten `git add`), **fix it and run again** — at most 2 attempts, then STOP and report the error to the user together with the output of the command.
5. **Feedback:** in the closing message — BEFORE the command of the next phase — write out the identifier and the message of the commit in one line (e.g. `Commit: a1b2c3d — cycle-NN: <PHASE-TAG>`).

> **The message of the commit is EXACTLY `cycle-NN: <PHASE-TAG>`** — no conventional-commit prefix (`docs(...)`, `feat:`), no wording of your own, no additional description in the first line. 07-validate and 09 look for this format retrospectively, and the verification in step 4 matches it as well. If `git log -1 --oneline` shows something else, **fix it** (`git commit --amend -m "cycle-NN: <PHASE-TAG>"`) before you close the phase.

### Phase boundary — a hard stop after the commit (PE1)

> **The phase ENDS with writing out the identifier of the commit. In the same round you start nothing from the next phase** — you do not create a file, you do not run an analysis, and you do not write into the artifact of the next phase "just as preparation" either. The last element of your closing message is the `/clear` + the starting command of the next phase; **after that you stop and hand control back to the user.**

**This holds even if something encourages you to go on:**

- the earlier to-do list of a **context summary / checkpoint** (e.g. *"3. Call /bs-write-tasks…"*) — the summary records the **past**, it is not a command for the present;
- your own earlier plan or a TODO list of yours that enumerated several phases;
- a "let us go through the whole process" kind of sentence the user gave in an **earlier** round.

**The phase boundary of the skill stands above all of these.** Only one thing overrides it: the user's **explicit request, given after the commit and meant for this round**, to continue — and even then, point out that without a fresh context (`/clear`) the quality of the next phase degrades.

**Why:** the `/clear` per phase is the foundation of the methodology — the next phase starts from its own, clean context, from the committed artifact. If you continue in the same round, the next phase inherits all the rubbish of the current phase (dropped alternatives, half-finished trains of thought), and typically **takes over your decisions instead of deriving them again**.

**Prohibitions:**

- Do **not** report the phase as done, and do **not** give the starting command of the next phase without a commit (except on the No-VCS branch).
- Do **not** postpone the commit to the next phase ("03 will commit it") — every phase commits its own.
- Do **not** start the next phase after the commit in the same round (PE1) — you do **not even create** the artifact of the next phase (`plan.md`, `tasks.md`, code). If you did it anyway, **delete** the file created, restore the clean working tree, and tell the user.
- Do **not** ask for separate permission for the commit: confirming the closing of the phase **includes** the approval of the commit. (About the uncommitted, foreign changes left over from earlier, the working-tree check at the beginning of the phase has already decided.)
