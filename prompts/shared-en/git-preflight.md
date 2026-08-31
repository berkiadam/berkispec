<!--
  SHARED git preflight description for the BRANCH-OPENING phases (00, 01) — BD13. This is
  NOT a standalone skill/agent, but a shared text block that the installer
  (install-helper.py) embeds INLINE at build time into the installed version of the
  referencing skill (in place of the `<!-- INCLUDE:shared/git-preflight.md -->` marker).
  Only 00 and 01 reference it (they are the ones creating a branch); phases 02–09 do
  NOT — their own, short working-tree check is enough for them (02 additionally checks
  the existence of the branch created in 01, and 09 switches branches at the merge).
  It has no frontmatter: its content is copied in verbatim. Edit it here.
-->

### Git preflight (branch-opening phase — `00` / `01`)

> This description applies to the **branch-opening** phases (`00-init-project`, `01-add-cycles`) — they are the ones branching off `main`. Phases `02`–`09` do **not** use it.

#### No-VCS gate (BD11) — always, first

Read the version-control flag from the `## <sec:cv_git_conventions>` section of `conventions.md`:

- If it states **"<status:no_vcs_flag>"**, then **skip every git operation** in this phase — no `git status`, no branch switch/creation, no `git pull`, no commit. The phase only carries out its non-git work (creating files/folders). You **skip** the steps below.
- Otherwise (git is available, the project is a git repo) → continue with the *Working-tree check*.

#### Working-tree check

Run: `git status --short`. If there are uncommitted changes:

- List the affected files.
- Ask **in one round**: <!-- INCLUDE:lang/git-preflight.md#BD13-commit-vagy-folytas --> — wait for the answer, then proceed accordingly.

#### A fresh, clean `main` (before branching off)

The goal is to branch off a fresh `main` (the **<field:f_main_branch>** field of the `## <sec:cv_git_conventions>` section of `conventions.md`; `main` by default). You do **not** run the actual `git switch -c` here — the phase does that according to its own logic (`00` immediately, `01` AFTER the name of the cycle is determined — BD5).

1. **Worktree situation (PW1/PW3) — BEFORE examining the branch.** The planning window (`01`–`05`) can be parallelized in a separate `git worktree`, so first we have to know where we are:

   ```bash
   git worktree list                 # which directory is on which branch
   git rev-parse --git-common-dir    # if it is not `.git`, we are in a linked worktree
   ```

   - **There is a single worktree** (the common dir is `.git`) → on to point 2 (the normal path).
   - **We are in a linked worktree**, and the HEAD **is already on the branch of the current cycle** → this is a **resume**: the worktree and the branch were already created by the user. `git switch -c`, `git switch` and `git pull` are **forbidden**, **skip** points 2 and 3 — the branching off already happened from a fresh `origin/main`.
   - **We are in a linked worktree with a detached HEAD, on a fresh `origin/main`** (the worktree has just been created for this cycle — PW3/B) → the base is already fresh: **skip** points 2 and 3, the branch of the cycle is created here according to BD5, after the name of the cycle is determined.
   - **We are in a linked worktree on a foreign (another cycle) branch** → the PW3 decision gate of point 2 follows, with the difference that branch **A)** is not viable here: `main` is checked out in the main worktree, we cannot switch to it here. Either the user closes the other cycle and moves back into the main worktree (step PW2/2 of the *Parallel cycles* block), or they open a new worktree for this cycle according to **B)**.

   **On any linked-worktree branch (PW4):** check that the tool directory exists here as well (`ls <platform-scripts-mappa>`). If it is missing — because the user created the worktree by hand — run the replenishment from the main worktree, and only continue afterwards: `python3 <platform-scripts-mappa>/worktree-setup.py .` (the script finds the main worktree by itself from the shared git directory).

2. **Where are we? (BQ3 — idempotence/resume):** `git branch --show-current`.
   - **We are on `main`** → on to point 3.
   - **We are on a feature branch** → compare the name of the branch with the **expected branch name of the current cycle** (from the in-progress cycle block of `roadmap.md` / from the folder name of the cycle):
     - **It matches** → this is a **resume**; the branch already exists. **There is nothing to do** — continue on this branch, do **NOT** run `git switch -c`, and do **not** warn.
     - **It does not match** → this is the branch of **another cycle that is not closed yet**. Do **not** merely ask for a switch to `main`: this is a **decision gate (PW3)**. Already in your **first answer**, offer both paths in a **single** question, and wait for the answer — do not start planning until then:

       <!-- INCLUDE:lang/git-preflight.md#PW3-soros-vagy-parhuzamos -->

       - **A) Serial continuation** — the user closes the current cycle (merge or PR according to `## <sec:cv_merge_strategy>`), then **they switch to `main`** themselves (they do the switch, because of possible open work). Wait until they sort it out, then on to point 3.
       - **B) Parallel planning in a worktree** — the other cycle stays open, and this phase runs in a **linked worktree**. The cycle number comes from the branch scan (BQ2), but the name of the cycle is not known yet, so the worktree is created with a **detached** HEAD on a fresh `origin/main`; the branch is opened in it later by the phase, according to BD5:
         ```bash
         git fetch origin
         git worktree add --detach ../<project>-cNN origin/main
         python3 <platform-scripts-mappa>/worktree-setup.py ../<project>-cNN   # PW4
         ```
         **PW4 — replenishing the tool directories (a mandatory step).** The worktree only receives the files **tracked by git**; the configuration of the agentic tools (`.claude/`, `.agents/`, `.codex/`, `.cursor/`, `.github/`, `AGENTS.md`, `CLAUDE.md`, …) may be gitignored depending on the project — in that case the `bs-*` skills, the subagents and the gate scripts **are missing** in the new worktree, and the agent starting there is blind. `worktree-setup.py` replenishes them: it copies the **missing** files from the root of the main worktree (it never overwrites and never deletes an existing one, so it is idempotent). If something else has to be brought over as well, it can be extended with the `--extra <path>` switch.

         **PW5 — moving over and STOP (the phase ends here).** The agent is bound to the current directory: after creating the worktree, do **NOT** plan any further in this session, do not create a cycle folder and do not write into the roadmap. Emit the message below — filled in with the **ABSOLUTE path** of the worktree and the **start command** of the tool in use — and then **stop**:

         <!-- INCLUDE:lang/git-preflight.md#PW3-worktree-ujrainditas -->

         After the restart, the phase runs from the beginning **in the worktree**: there the switch to `main` is skipped (it stays checked out in the main worktree), and point 3 is skipped.

       **Which one to recommend:** if the other cycle **cannot be closed yet** (open work, implementation in progress, the `06`–`09` stretch), **B)** is the recommended one — the boundary of the parallelism is described in the *Parallel cycles* block (`06` does not start while the worktree of another cycle is open, PW1/PW2). If the other cycle is practically done, **A)** is the simpler one.

3. **A fresh and clean `main` (BQ4):** if we are on `main`, **before** branching off:
   - Check whether there is uncommitted content **or** an unpushed local commit (e.g. `git status --short` + the ahead indicator of `git status -sb`, respectively `git log --branches --not --remotes`).
   - **If there is** → do **not** run `git pull`; ask the user to handle it (commit/push/stash), and wait until `main` is clean.
   - **If it is clean** → `git pull` (this refreshes the remote as well, so the feature-branch scan also sees a fresh state — a separate `git fetch` is typically not needed).

The branch name is assembled according to the **<field:f_branch_naming>** field of the `## <sec:cv_git_conventions>` section of `conventions.md`; by default `feature/cycle-NN-<name>` (the **folder name** is always plainly `cycle-NN-<name>` regardless of this, without a prefix — BD3).
