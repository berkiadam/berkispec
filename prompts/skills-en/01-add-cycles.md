---
phase: 01
name: bs-add-cycles
description: "berkispec - 01. Use it after initialization (Phase 01) to plan development cycles (roadmap), reschedule existing ones, or add a new cycle — breaking down tasks into logical, independently testable units. Input: 'conventions.md', optionally a brainstorm session ('brainstorm: NN' — distils 'cycle-design-input.md' from the '/bs-brainstorm' working file, BS18). Creates or updates 'specs/roadmap.md' with 'Done' status."
prerequisites:
  - "conventions.md exists"
output:
  - "specs/roadmap.md status: <status:done>"
  - "specs/cycle-NN-<name>/cycle-design-input.md (empty template, filled in by the user — optional, CD1; filled in when there is brainstorm input, BS18)"
  - "specs/cycle-NN-<name>/spec-input-from-prev.md — ALWAYS created, with an empty template as well (IP1)"
  - "specs/cycle-NN-<name>/plan-input-from-prev.md (only if there is info to hand over, IP1)"
prev: bs-init-project  # or bs-brainstorm (BS18 — brainstorm input)
next: bs-write-spec
subagents:
  - "agents/researcher.md"
shared:
  - "shared/git-preflight.md"
  - "shared/parallel-cycles.md"
  - "shared/input-from-prev.md"
---
# 01 — Managing cycles
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

We develop software using spec driven development. Development is broken into cycles. Every cycle is an independently developable, independently testable sub-unit of the full implementation.

This is **phase 1 (0–9)** of the process: 0-init · **1-cycles ←** · 2-spec · 3-plan · 4-tasks · 5-analyze · 6-implement · 7-validate · 8-doc-sync · 9-review.

---

## <field:f_prerequisite>

1. **`conventions.md` existence check:** read `conventions.md` at the project root. If it doesn't exist, STOP — send them back to the `00` project initialization phase.
2. **Git preflight (shared description):** 01 is the **branch-opening** phase — the *full* preflight applies to it (no-VCS gate + working-tree check + branch-opening preflight: fresh, clean `main`, and resume detection). You do **not** run the actual `git switch -c` here, but AFTER the cycle number + name have been determined, at the closing of the given mode (A/B/C) (BD5).

<!-- INCLUDE:shared/git-preflight.md -->

<!-- INCLUDE:shared/parallel-cycles.md -->

> **Branch = cycle (BD1–BD3).** The cycle branch is created **here, in phase 01**, from `main` (not in 06), and phases 02+ already work on it. On the No-VCS branch (per `conventions.md` there is no version control), you skip every git step: only the `specs/cycle-NN-<name>/` folder and the roadmap get created (BI8).

---

## Resuming after an interrupted run

If phase 01 was interrupted and continues in a new session:

**First, the git state (BQ3 — idempotency, only if there is version control).** The branch-opening preflight (above) already decides this via `git branch --show-current`; here are the consequences:

```
Which branch are we on?
1. main → normal fresh flow: the cycle number/name is followed by `git switch -c` (BD5).
2. a feature branch that is the expected branch name of the CURRENT cycle
   (based on the roadmap's in-progress block / the cycle folder name)
   → this is RESUME: the branch already exists. Do NOT create a new branch
     (`git switch -c` is forbidden), continue on this branch per the document
     state below.
3. a feature branch that is NOT the current cycle's
   → the PW3 decision gate (see the git preflight): offer in ONE question both
     A) the serial close-down (merge/PR per `## <sec:cv_merge_strategy>`, then the
     user switches to main — do not switch automatically) AND B) the parallel
     worktree (`git worktree add --detach ../<project>-cNN origin/main`).
     Do not merely ask for the switch to main, and do not start planning until the answer.
```

**Next, the document state:**

```
1. Does specs/roadmap.md exist?
   → Read its status and content.
   → If it's half-written (there's an open [ ] question, or an incomplete
     cycle block): continue from the first incomplete part, don't start over.

2. Is there a created but incomplete cycle folder (mkdir happened, but the
   roadmap block or the commit is missing)?
   → Finish the missing step (roadmap block, validation, confirmation, commit).
     If the branch is also missing (alongside VCS), first stand on fresh main
     per the branch-opening preflight, then create the branch, and finish on it.

3. Interrupted mode C (the current cycle's roadmap block is incomplete)?
   → Continue filling in that cycle's block on the cycle's feature branch
     (BQ5/BQ6 — per-cycle fix, not full reconstruction).
```

---

## Mode detection — at startup

> **Step 0 — brainstorm input (BS18).** If the call refers to a brainstorm session (`brainstorm: 04`, *"from the 04 brainstorm"*), **first** read the working file per the *"Brainstorm input (BS18)"* section, and only then continue with mode detection. The brainstorm does not replace mode selection — it adds the input.

**Step 1:** Check the contents of the `specs/` directory (`ls specs/`).

**`specs/` is empty or doesn't exist** → ask **one** question:
<!-- INCLUDE:lang/01-add-cycles.md#specs-ures-kerdes -->

- Answer **A** → continue with **mode A**
- Answer **B** → continue with **mode B**

**`specs/` has cycle folders**:
   **Step 2:** Check whether `specs/roadmap.md` exists.

   - **If it exists** → indicate this, and continue with **mode B**:
<!-- INCLUDE:lang/01-add-cycles.md#ciklusok-roadmappal -->

   - **If it does NOT exist** → ask:
<!-- INCLUDE:lang/01-add-cycles.md#ciklusok-roadmap-nelkul -->
     - **A specific cycle** → Follow the **Mode C — Filling in a single cycle's roadmap block** steps for that one cycle (BQ5/BQ6). If you also want to add a new cycle afterward, continue with **mode B**.
     - **Adding a new cycle** → Continue directly with **mode B**: you add the new cycle, the rest of the roadmap can remain empty/incomplete.

---

## Determining the cycle number (shared — BQ2)

To determine the next cycle number (`NN`), the main `roadmap.md` + `ls specs/` are **not enough**, because there may be a cycle that only exists on a not-yet-merged feature branch. Therefore:

- **With version control:** `NN = max(the cycle numbers in main's `roadmap.md`/`ls specs/`, the `cycle-NN` numbers in feature branches) + 1`.
  - Feature-branch scan: `git branch -a --list '*cycle-*'` (also covering the branch prefix from `conventions.md`, e.g. `feature/cycle-*`), then extracting `cycle-(\d+)` from the branch names.
  - Freshness: the branch-opening preflight's `git pull` has already refreshed the remote too, so the scan sees a fresh `git branch -a` state — a separate `git fetch` is typically not needed.
- **On the No-VCS branch** (no version control): the scan is skipped, `NN = max(the numbers from `ls specs/`/`roadmap.md`) + 1`.

This formula applies in every mode (A/B/C) where a new cycle number is needed — don't collide with cycles opened in parallel that haven't been merged yet.

---

## Mode A — Full roadmap planning

### Git branch in mode A (BQ1) — BEFORE planning

The full roadmap is created and committed on the **first cycle's feature branch**. With version control, **before writing anything into `specs/roadmap.md`**:

1. Ask the user **what the first cycle should be named** (kebab-case). If they don't give a name, the **default** branch is `feature/cycle-01` (no name suffix); if they do, `feature/cycle-01-<name>`.
2. Run the branch-opening preflight (above: fresh, clean `main`, and resume detection — BD6/BQ3/BQ4).
3. Create the branch: `git switch -c feature/cycle-01[-<name>]` (with the prefix per `conventions.md`'s `## <sec:cv_git_conventions>` **<field:f_branch_naming>**; `feature/` by default).
4. **From here on, everything (interview, roadmap writing, commit) happens on this branch** — `main` stays protected (BD4).

**On the No-VCS branch** (no version control) this step is skipped: the roadmap is created directly, without a branch/commit (BI8).

### Your task

Based on the HLD/LLD, determine the development cycles, and describe them in the `specs/roadmap.md` file.

**The most important principle: vertical slicing.** Don't slice by layer (e.g. "Cycle 1: database, Cycle 2: API"), but by feature — every cycle should end with a testable, end-to-end working behavior.

**Don't write a spec, plan, or implementation.** This step only determines the cycle boundaries and the order.

### Output

**File:** `specs/roadmap.md` at the project root. If the `specs/` folder doesn't exist, create it.

### Handoff between phases (`*-input-from-prev.md`) — IP1

During cycle planning, information regularly comes up that **doesn't belong in the roadmap** (a roadmap entry is short: behavior, affected components, prerequisites, test criterion), but is valuable to later phases. **Don't discard it** — write it into the appropriate handoff file in the cycle's folder:

- **`spec-input-from-prev.md`** — for **02-write-spec**: behavioral detail, concrete error case, data field, business rule, acceptance criterion that the user mentioned during the interview but that doesn't fit into the roadmap entry.
  > **🔴 You ALWAYS create this file** — with the template, even if not a single item was collected (with an empty list in that case). This is the **one single exception** to rule 4. **It has no prerequisite whatsoever:** it does not depend on whether there was a `/bs-brainstorm` session, on which mode you are running in (A/B), or on how much was said during the interview. If there is nothing to hand over, the empty list **is itself the information** — this is how 02 knows that the channel was there and that nothing was missed. **Do not fill it with invented items** just so that it is not empty.
- **`plan-input-from-prev.md`** — for **03-write-plan**: technical constraint, information about an existing component or infrastructure, known integration limit that the user mentioned here.

**In mode A** (full roadmap planning) the cycle folder may not exist yet — in that case, write the item into the folder of the cycle it concerns, creating the folder. If the item concerns **multiple cycles**, it doesn't belong here: it should go into the relevant cycle entries in `roadmap.md`.

<!-- INCLUDE:shared/input-from-prev.md -->

### Gathering information — iterative interview

Before determining the cycles, you need enough information. Assess what's available:

**Required minimum:**
- The system's purpose and boundaries are clear
- The main components and actors are identified
- The key user flows (from entry to the main operations) are known
- The integration points with external systems are known

**If any point is missing:** ask **one** targeted question, wait for the answer, then reassess. Keep repeating until the minimum is met. Don't ask multiple questions at once.

> **If there is brainstorm input (BS18):** a good part of the minimum is already in the working file (`## 1. Goal`, `## <sec:bs_facts>`, `## <sec:bs_decisions>`) — **don't ask that again**. Start the interview with the unchecked items of `## <sec:bs_open_questions>`, one at a time.

Once there is enough information, start determining the cycles.

### Principles of vertical slicing

**A good cycle:**
- Implements a single end-to-end behavior (e.g. "the user can log in and see some content")
- Independently testable — at the end of the cycle you can decide whether it's done, without any other cycle being done
- Minimal: contains only as much as is needed to demonstrate the behavior
- Handles not-yet-ready dependencies with a mock strategy

**Signs of bad slicing:**
- Works in only one layer (backend only, UI only, config only)
- Not independently testable — something else is always needed
- Too big: more than 2-3 days of implementation expected → break it down further

### Roadmap structure

```md
<!-- INCLUDE:lang/01-add-cycles.md#roadmap-struktura -->
```

### Validation cycle — after every proposed cycle

Before closing off a cycle description, check:

1. **Is it independently testable?** Can you say "done / not done" without the other cycles?
2. **Is it vertical?** Does it go through the whole stack, or does it only cover one layer?
3. **Is it not too big?** If the expected implementation is more than 2-3 working days, break it down further.
4. **Are the dependencies clear?** If a cycle assumes another cycle's result, is that marked?

If any point is "no", adjust the cycle boundary before moving on.

### Handling open questions

**Basic rule: we never delete from the list. A closed question is only marked with `[x]` — its text and decision remain.**

**Status transitions:**
- At the start of writing the roadmap: `<status:draft>`
- If there is at least one `[ ]` question: `<status:open_questions>`
- If every question is `[x]` and the validation check passed: `<status:done>`

**Iteration rules:**
1. If a question comes up while determining cycle boundaries, add it to the `## Open questions` list in `- [ ] Knn` format, with sequential numbering.
2. Ask the user **one** question, wait for the answer. **Every time you ask a question or request approval/review, you must place a direct, clickable markdown link to the affected files at the end of your response (e.g. in the form `[roadmap.md](file:///absolute/path/specs/roadmap.md)`).**
3. When the answer arrives, mark it `[x]` and add a one-line summary next to it (`→ brief decision`), then carry the decision through into the roadmap.
4. If the answer opens a new question, add it to the end of the list with the next `Knn` number.
5. Keep iterating until every question is in `[x]` status.

Every iteration can be started with new context: `conventions.md` (if it exists), the current state of `specs/roadmap.md`, plus this prompt are enough.

### Stopping rules

- If the HLD/LLD doesn't clearly define a component's behavior and this affects the cycle boundaries: state exactly what's missing, and ask for clarification. Don't make up behavior.
- If a cycle can't be broken down further but is still large: state the risk and leave the decision to the user.
- If the dependencies between cycles are circular: state this, and ask for a decision on the order.
- **PW5:** if a worktree was created on the PW3/B branch of the preflight, the phase **ends there** in this session — you emit the moving-over message (absolute path + the start command of the tool), and you stop. Do not create a cycle folder, do not write into the roadmap: the phase runs from the beginning in the worktree, with a restarted tool.

In every case, flag only **one** problem at a time.

### Status handling

If every question is `[x]` and the validation check passed, ask the user:
<!-- INCLUDE:lang/01-add-cycles.md#roadmap-statusz-megerosites --> — Don't switch the status before confirmation. **Place the direct, clickable link to `specs/roadmap.md` at the end of the response.**

If the user confirms:
- Set the status of `specs/roadmap.md` to `<status:done>`.
- Create the **first cycle's** directory (`mkdir -p specs/cycle-01-<name>/`, if it doesn't exist yet) and the `cycle-design-input.md` template in it, per the *"Cycle design input (CD1)"* section. **Don't** create the other cycles' folders in advance — they get their own during their own 01 run (mode B).
- Make a git commit closing out the phase — **on the already-created `feature/cycle-01[-<name>]` branch** (BD4/BQ1), not on `main`:
  ```bash
  git add specs/roadmap.md specs/cycle-01-<name>/cycle-design-input.md
  git commit -m "cycle-NN: 01-cycles"
  ```
  where `NN` is the number of the first cycle currently being planned (e.g. `cycle-01: 01-cycles`). **On the No-VCS branch, the commit is skipped** (BI8).
- Indicate: <!-- INCLUDE:lang/01-add-cycles.md#A-mod-zaro-uzenet --> — **place the clickable link to `cycle-design-input.md` at the end of the response.**

---

## Mode B — Adding a new cycle

### Preparation

1. Read `specs/roadmap.md` (if it exists) — for context and cycle number determination. If it doesn't exist, create it with the basic structure (`# Development Roadmap\n\n**<field:f_status>:** <status:done>`). _(The actual writing/commit of the roadmap happens on the cycle's feature branch — see "Creating the branch".)_
2. Determine the new cycle number per **"Determining the cycle number (BQ2)"** — the max of main's `roadmap.md`/`ls specs/` **and** the feature branches' `cycle-NN` numbers, plus 1 (with VCS). This step still runs on the starting branch (typically `main`).
3. Indicate to the user:
<!-- INCLUDE:lang/01-add-cycles.md#BQ2-ciklusszam-jelzes -->

### Gathering information

1. Ask **one** question:
<!-- INCLUDE:lang/01-add-cycles.md#BD5-cel-kerdes -->

   > **If there is brainstorm input (BS18):** **skip** this question — the goal is already answered by the working file's `## <sec:bs_goal_question>` and `## <sec:bs_cycle_split>` sections. Instead, summarize in 2-3 lines what you understood from it, and get **that** approved. Only ask about what the file doesn't answer (typically the open items of `## <sec:bs_open_questions>`).

   > **Flow-size check (after describing the goal, before the name suggestion):** Consider whether the task is **too small** for a full, multi-phase cycle. If the goal can be solved in 3-4 steps, in a single pass — typically **assembling/modifying a configuration, writing a simpler script, a smaller fix, or a local tweak** — then the full `02→…→09` flow is oversized. In that case **stop, and suggest the simplified flow**, before creating a cycle:
   >
<!-- INCLUDE:lang/01-add-cycles.md#BS-quick-flow-javaslat -->
   >
   > The decision is the user's: if they want the full cycle, continue here; if the simplified one, redirect them to the `/bs-quick-flow` skill.

2. Once the goal description arrives, come up with a suggestion for the cycle's name in **kebab-case** format, concise, reflecting the behavior (e.g. `performance-load-test`, `token-exchange`, `oidc-login`). Ask about it:
<!-- INCLUDE:lang/01-add-cycles.md#BD5-nevjavaslat -->

If the name doesn't fit, ask the user for their own suggestion, and use that.

If something needs clarifying based on the description or name (e.g. overlap with existing cycles, a dependency), ask **one** more question. Don't ask multiple at once.

### Creating the branch (BD5/BI1) — AFTER the name is approved, BEFORE writing the roadmap

After the name is approved, **before** writing into `specs/roadmap.md` or creating a folder (BD5 order), with version control:

1. Make sure the branch-opening preflight (start of phase) put you on fresh, clean `main` — or that this is a resume on this same cycle branch (BQ3). On resume, there's nothing to do, continue on the existing branch.
2. Standing on `main`, create and switch to the cycle's branch: `git switch -c feature/cycle-NN-<name>` (with the prefix/format per `conventions.md`'s `## <sec:cv_git_conventions>` **<field:f_branch_naming>**; `feature/` by default). The **folder name**, regardless, is plainly `cycle-NN-<name>` (BD3).
3. From here on, everything (roadmap writing, `mkdir`, commit) happens **on this branch**; `main` stays protected (BD4).

**On the No-VCS branch** (no version control) this is skipped: the roadmap writing and folder creation happen directly, without a branch/commit (BI8).

### Writing the new cycle

Write the cycle description per the standard structure. This description goes into the `specs/roadmap.md` file, inserted after the existing cycles:

```md
<!-- INCLUDE:lang/01-add-cycles.md#BD5-ciklus-blokk-sablon -->
```

### Validation

Before appending to `specs/roadmap.md`, check:

1. **Is there no overlap** with existing cycles? (isn't the same behavior already present?)
2. **Is it independently testable?**
3. **Is it vertical?** (not just one layer)
4. **Is it not too big?** If yes, suggest breaking it down, and ask for a decision.
5. **Are the prerequisites accurate?** (are the referenced cycles really needed?)

If any answer is "no": fix it or ask about it before appending.

### Appending and closing

1. Append the new cycle's description to the end of `specs/roadmap.md`, with a `---` separator after the existing ones. **Edge case:** if the last non-empty line of `roadmap.md` isn't `---`, first insert a `---` before appending the new cycle — this guarantees the separator is present between every cycle block.
2. Show the finished cycle description, and ask for confirmation:
<!-- INCLUDE:lang/01-add-cycles.md#BD5-roadmap-megerosites -->
3. If the user confirms (the `git switch -c` has already happened by now — see "Creating the branch"):
   - Set the roadmap's status to `<status:done>`.
   - Create the cycle's directory: `mkdir -p specs/cycle-NN-<cycle-name>/` (the **folder name** without a prefix, plainly `cycle-NN-<name>` — BD3).
   - Create the **cycle design input template** in the folder: `specs/cycle-NN-<cycle-name>/cycle-design-input.md` — see the *"Cycle design input (CD1)"* section below.
   - Make a git commit closing out the phase — on the **cycle's feature branch** (BD4), not on `main`:
     ```bash
     git add specs/roadmap.md specs/cycle-NN-<cycle-name>/cycle-design-input.md
     git commit -m "cycle-NN: 01-cycles"
     ```
     where `NN` is the number of the cycle just added (e.g. `cycle-16: 01-cycles`). **On the No-VCS branch, the `git switch -c` and the commit are skipped** — only the `mkdir` + roadmap writing + template creation happen (BI8).
   - Indicate the next step — **together with offering the design input**:

<!-- INCLUDE:lang/01-add-cycles.md#B-mod-zaro-uzenet -->
     >
     > **Phase boundary — hard stop (PE1):** phase 01 **ends** with this message. Do **not** start writing a spec in the same round (don't even create `spec.md`), even if a context summary/checkpoint to-do list, your own earlier plan, or the user's "let's go through the whole process" sentence from an earlier round encourages it. Only the user's explicit request, made in this round, overrides this.
     >
     > **Place the direct, clickable link to `cycle-design-input.md` at the end of the response** (e.g. `[cycle-design-input.md](file:///absolute/path/specs/cycle-NN-name/cycle-design-input.md)`), so the user can open it with one click.

---

## Cycle design input (CD1) — the user's own specification

**What this is:** the `cycle-design-input.md` created in the cycle's folder is an **empty template for the user**. Here they can describe, in their own words, in free form, what they want in the cycle — expectations, an outline, an example payload, a process description, links, earlier notes.

**Key rules:**
- **The file belongs to the user.** You (01) only create the template, you do **not** write content into it — **the sole exception is brainstorm input (BS18):** if the call refers to a brainstorm session, the template is created not empty, but with content distilled from the working file. `02-write-spec` (behavioral content) and `03-write-plan` (technical/procedural content) read it automatically, but neither rewrites it.
- **Filling it in is optional.** If it stays empty (only the template text is in it), 02 notes this in one sentence and continues working from the roadmap entry — this is not an error, not a stopping reason.
- **It's not a substitute for `spec-input-from-prev.md`.** **You** write into `spec-input-from-prev.md` (items mentioned during the interview that don't fit into the roadmap, IP1); **the user** writes into `cycle-design-input.md`, after the phase closes, at their own pace.

**Content of the template to create (verbatim, with `NN` substituted for the current cycle number — e.g. `# cycle 25 design input from user`):**

```md
<!-- INCLUDE:lang/01-add-cycles.md#CD1-design-input-sablon -->
```

---

## Brainstorm input (BS18) — taking over a `/bs-brainstorm` session

**What this is:** the `/bs-brainstorm` helper command persists the exploratory ideation before the spec into the `.bs-brainstorm/brainstorm-NN-<slug>.md` working file (facts with sources, alternatives with trade-offs, decisions, open questions, a suggested cycle split). If the user refers to it, this is the **official bridge** between the brainstorm and the flow: the raw working file is local and gitignored, but the `cycle-design-input.md` distilled from it gets committed.

**When it activates:** if the call refers to a session by number — `/bs-add-cycles brainstorm: 04`, *"create the design input from the 04 brainstorm"*. If not, **everything stays unchanged** (the `cycle-design-input.md` is created as an empty template per CD1).

### <sec:steps>

1. **Finding the file:** `ls -1 .bs-brainstorm/brainstorm-04-*.md`.
   - **No such number exists:** don't guess and don't work without it — list the existing sessions (number + slug), and ask which one they meant.
   - **Not even a `.bs-brainstorm/` folder exists:** state in one line that you can't find it (the folder is gitignored, so it doesn't even exist on another machine), and ask whether to continue without brainstorm input.
2. **Full read.** The working file is short; read it in full, don't skim.
3. **Interview input.** The `## <sec:bs_cycle_split>` section is the **starting point for the roadmap proposal** (one unit = one cycle candidate), `## 1. Goal` is the cycle's goal, `## <sec:bs_facts>` is the affected components. **Don't ask again about what the file already answers** — the user has already talked it through once.
4. **The open questions are your questions.** The **unchecked** items of `## <sec:bs_open_questions>` are open: these become the targeted questions of the interview (one at a time), or — if they fall outside the cycle's scope — entries in the roadmap's `## Open questions` section. **Never treat them as settled fact.**
5. **The cycle-split suggestion is not a command.** The brainstorm's suggestion is a good starting point, but the principles of vertical slicing (see the section above) and the `## Validation cycle` check must **still be run** against it. If the suggested split violates the principles (not independently testable, too big, circular dependency), say so, and suggest a change — the decision is the user's.

### Filling in `cycle-design-input.md`

The CD1 template's header and explanatory block go into the file **unchanged** (the user still writes into it afterward); but the distillate goes in place of `<!-- Write here. -->`:

- **What to carry over:** `## <sec:bs_decisions>` (this is the main content), the description of the **kept** option among the `## 3. Alternatives` that affect this cycle, and the lines of `## <sec:bs_facts>` that concern this cycle (together with the `file:line` anchors — their navigational value also persists in phases 02/03).
- **What NOT to carry over:** `## <sec:bs_log>`, closed/discarded threads, the session's meta-information, and the full list of `## <sec:bs_cycle_split>` (only **this** cycle's slice of it belongs here — the rest is the roadmap's job).
- **A brainstorm split across multiple cycles:** every cycle gets **only its own slice**. Decisions common across cycles go into the roadmap's cycle block, or into `spec-input-from-prev.md` (IP1), not repeated in every design input.
- **Tone:** descriptive, addressed to the implementer. Rephrase conversation traces from the brainstorm (*"we discussed that…"*, *"you asked…"*) into a decision: *"Certificates are managed by a central store; components only receive a reference."*
- **Don't reference the `.bs-brainstorm/` path** in the committed document: the folder is gitignored, the link is dead on another machine and in a PR. A line without a path is enough to indicate the origin: `> Distilled from the decisions of brainstorm session NN.`
- **If the file already exists and has content** (the user has already written into it): **don't overwrite it.** Append the distillate to the end under a `## Brainstorm distillate` subheading, and mention it in one line.

### Closing

Instead of the usual CD1 feedback, indicate that the file is **not empty**:

<!-- INCLUDE:lang/01-add-cycles.md#BS18-design-input-brainstormbol -->

Place the clickable link to `cycle-design-input.md` here too, at the end of the response.

---

## Mode C — Filling in/fixing a single cycle's roadmap block (per-cycle — BQ5/BQ6)

### What changed (BQ6)

The classic "**full** roadmap reconstruction from all cycle folders into a single `<status:draft>` document" scenario is **gone**. In the **branch = cycle** model, the full main roadmap is assembled by **merging** the cycles, not by one big reconstruction step. Therefore, mode C now **only** fills in/fixes the given cycle's roadmap block, **on that cycle's feature branch** (BQ5) — this preserves the protected `main` + the "branch = cycle" invariant, and there's no more reconstruction branch that commits multiple cycles at once. The automatic C→B transition is also gone.

### When it runs

When the **current cycle's** roadmap block is missing or incorrect (`specs/roadmap.md` doesn't contain it, or contains that `cycle-NN-<name>` block incompletely), while the cycle's folder already exists. **You only work with that one cycle** — not with all of `specs/`.

### <sec:steps>

1. **Identifying the cycle:** which cycle is it (the user gave it / the folder name of the cycle in progress). This is the ONE cycle you're filling in.

2. **Branch (BQ5):** with version control, work on that **cycle's feature branch** — following mode B's "Creating the branch" pattern: if there's no branch yet, `git switch -c feature/cycle-NN-<name>` after the branch-opening preflight (fresh, clean `main`); if this is a resume and you're already on the cycle's branch (BQ3), continue there, without `git switch -c`. **On the No-VCS branch, git is skipped.**

3. **Filling in/fixing the missing/incorrect block:** if `specs/roadmap.md` doesn't exist, create it with the basic structure (`# Development Roadmap\n\n**<field:f_status>:** <status:done>`). Fill in/fix the given cycle's `## Cycle NN — title` block per the standard structure, from the cycle's `spec.md` (if it exists). If the input is large, query it concisely with the `researcher` subagent (`agents/researcher.md`, Mode B) (title, the first sentence of `<sec:objective>`, affected components, key points of `<sec:test_specification>`/`<sec:definition_of_done>`) — sparing the main context. **Only touch this one block**, don't overwrite the rest of the roadmap.

4. **Validation + confirmation:** show the filled-in/fixed block, and ask for confirmation:
<!-- INCLUDE:lang/01-add-cycles.md#BQ5-C-mod-jelzes -->
   > **Place the direct, clickable link to `specs/roadmap.md` at the end of the response.** Don't proceed before confirmation.

5. **Closing (after confirmation):** commit on the **cycle's feature branch** (BD4):
   ```bash
   git add specs/roadmap.md
   git commit -m "cycle-NN: 01-cycles"
   ```
   **On the No-VCS branch, the commit is skipped.** The cycle can then continue with the 02 spec phase (or, if you also want to add a new cycle, with mode B).
