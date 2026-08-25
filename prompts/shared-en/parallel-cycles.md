<!--
  SHARED description of PARALLEL CYCLE WORK (the worktree window, PW1/PW2 — BD16).
  This is NOT a standalone skill/agent, but a shared text block that the installer
  (install-helper.py) embeds INLINE at build time into the installed version of the
  referencing skill (in place of the `<!-- INCLUDE:shared/parallel-cycles.md -->` marker).
  Referenced by: 01-add-cycles (the description of the window), 06-implement (the gate).
  It has no frontmatter: its content is copied in verbatim. Edit it here.
-->

### Parallel cycles — the planning window (PW1/PW2)

Two cycles **may proceed in parallel**, in separate `git worktree`s, in separate agent sessions (e.g. while `cycle-26` is being implemented, the spec of `cycle-27` is being written). This has a **hard boundary**:

| Phase | May run in parallel? | Why |
|---|---|---|
| `01` … `05` (cycle, spec, plan, tasks, analyze) | **Yes** | They only write the `specs/cycle-NN-<name>/` folder — there is no overlap with the files of the other branch, and there is no runtime resource involved (port, dev deploy, registry tag, shared DB/IdP). |
| `06` … `09` (implementation, validation, doc-sync, merge) | **No** | `06` writes the source tree (a real merge conflict), `07` consumes shared runtime resources, `08` writes guaranteed conflicting files (`docs-generated/`, `specs/test-conventions.md`), `09` requires `main`. |

**PW1 — the implementation lane is single-threaded.** **One** cycle at a time may be in the `06`–`09` stretch. The other cycles may get that far, but they wait their turn there.

**PW2 — crossing the boundary before `06` (a mandatory order).** The green result of `05` was produced on the **old** `main`: the plan and the tasks were designed for a code base that did not yet contain the changes of the other cycle. Therefore, before starting `06`:

1. **The other cycle must be merged** (its `09` ran, its worktree is gone). Until then, `06` must not start.
2. **Move back into the main worktree** (`06`–`09` run there, so that the switch to `main` in `09` works):
   ```bash
   git worktree remove ../<cycle-worktree>        # the cycle worktree ceases to exist
   git switch feature/cycle-NN-<cycle-name>       # in the MAIN worktree, where main/the other branch was so far
   ```
   If `git worktree remove` refuses because of uncommitted content: **do not** use `--force` — commit on the branch of the cycle, and try again.
3. **Re-running `05-analyze` on the fresh base:**
   ```text
   /bs-analyze input: @specs/cycle-NN-<cycle-name>
   ```
   `05` **brings in the fresh main branch itself** into the branch of the cycle (BR1: rebase if the branch is not pushed; merge if a PR is open for it), and validates afterwards — so the anchors (`path:line`), the existence of the files and the plan↔code consistency are proven after the changes of the other cycle as well. If the analyze is `FAIL`, fixing it is the business of `03`/`04` — `06` opens only after `PASS`.

**Creating a worktree (for the planning window).** You do **not** have to switch to `main` — it stays checked out in the main worktree:
```bash
git fetch origin
git worktree add ../<project>-cNN -b feature/cycle-NN-<name> origin/main
```
The linked worktree works with its own HEAD and index, so the working-tree checks of the two agents do not see each other. The folder of the other cycle (`specs/cycle-MM-*/`) **does not even appear** in the worktree until it is merged — this is why the cycle numbering scans the branch names (BQ2), not `ls specs/`.
