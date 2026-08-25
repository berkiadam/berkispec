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

1. **Where are we? (BQ3 — idempotence/resume):** `git branch --show-current`.
   - **We are on `main`** → on to point 2.
   - **We are on a feature branch** → compare the name of the branch with the **expected branch name of the current cycle** (from the in-progress cycle block of `roadmap.md` / from the folder name of the cycle):
     - **It matches** → this is a **resume**; the branch already exists. **There is nothing to do** — continue on this branch, do **NOT** run `git switch -c`, and do **not** warn.
     - **It does not match** → **only then** tell the user: the current branch may be worth **merging or opening a PR for** according to `## <sec:cv_merge_strategy>`, **before leaving it**; then ask them to **switch to `main`** (they do the switch themselves, because of possible open work). Wait until they sort it out.
1.b **Parallel cycle / worktree (PW1):** if the user starts planning **in parallel, next to another cycle** (the `06`–`09` stretch is running in another cycle), then this phase works **in a linked `git worktree`**, and there is no need (and no way) to switch to `main` — that is checked out in the main worktree, and git refuses the second checkout. Recognize it:

   ```bash
   git worktree list                 # which directory is on which branch
   git rev-parse --git-common-dir    # if it is not `.git`, we are in a linked worktree
   ```

   - **We are in a linked worktree, and the branch is already the branch of the cycle** → this is a **resume**: the worktree and the branch were already created by the user (`git worktree add -b feature/cycle-NN-<name> ../<dir> origin/main`). Do **NOT** run `git switch` and `git pull`, and skip point 2 below — the branching off already happened from a fresh `origin/main`.
   - **`main` is checked out in another worktree, but we are not on the branch of the cycle here yet** → do not try to switch to `main`. Ask the user to create the worktree of the cycle for the parallel work (`git fetch origin && git worktree add ../<project>-cNN -b feature/cycle-NN-<name> origin/main`), and to restart the phase from there.
   - **There is a single worktree** → the normal path follows (point 2).

   The boundary of the parallelism (the planning window and the gate before `06`) is described in the *Parallel cycles* block — `06` does not start while the worktree of another cycle is open.

2. **A fresh and clean `main` (BQ4):** if we are on `main`, **before** branching off:
   - Check whether there is uncommitted content **or** an unpushed local commit (e.g. `git status --short` + the ahead indicator of `git status -sb`, respectively `git log --branches --not --remotes`).
   - **If there is** → do **not** run `git pull`; ask the user to handle it (commit/push/stash), and wait until `main` is clean.
   - **If it is clean** → `git pull` (this refreshes the remote as well, so the feature-branch scan also sees a fresh state — a separate `git fetch` is typically not needed).

The branch name is assembled according to the **<field:f_branch_naming>** field of the `## <sec:cv_git_conventions>` section of `conventions.md`; by default `feature/cycle-NN-<name>` (the **folder name** is always plainly `cycle-NN-<name>` regardless of this, without a prefix — BD3).
