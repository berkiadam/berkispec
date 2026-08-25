---
name: bs-brainstorm
description: "berkispec - helper command. Exploratory ideation and joint planning about the project BEFORE THE SPEC — when the direction of the topic, its implementation approach, or its split into cycles is not yet clear (e.g. 'how should central cert management work?'). Converses, contrasts alternatives, and persists the session's material into the '.bs-brainstorm/brainstorm-NN-<slug>.md' working file. Writes NOTHING else besides the working file, no code; at the end it hands off to the '/bs-add-cycles' or the '/bs-quick-flow' skill."
output:
  - ".bs-brainstorm/brainstorm-NN-<slug>.md (the session's live working file — gitignored)"
  - ".gitignore entry: `.bs-brainstorm/*` (once, after approval)"
next: bs-add-cycles
subagents:
  - "agents/researcher.md"
shared:
  - "shared/path-format.md"
---
# Brainstorm — exploratory ideation and joint planning
<!-- INCLUDE:lang/output-language.md#output-language -->

This is **not a phase**, but a helper command: it can be called any time — in a new project, mid-cycle, between two cycles —, has no prerequisite, and **does not change the status of any cycle**.

**What it is good for:** when the *what* and the *how* are not yet settled. "How should we implement central cert management?", "Is it worth extracting auth?", "What should we do about config duplication?" This is the gap before the 00–09 flow: `01-add-cycles` already assumes you know what you want (it just needs splitting into cycles), and `quick-flow` assumes the task is small and clear.

**What it is NOT good for:** executing a finished, bounded task (→ `/bs-quick-flow`), rescheduling an existing roadmap (→ `/bs-add-cycles`), writing code or debugging (→ the normal flow).

> **Context check: there is NONE here.** This is the one skill that can deliberately be invoked **in the middle of a long conversation** as well — stale context here is normal, and often even useful. **Do not ask about `/clear`**, and do not request a fresh session.

---

## Hard contract (BS1) — what you may write

| Operation | Allowed? |
|---|---|
| Writing/reading `.bs-brainstorm/brainstorm-NN-*.md` | ✅ yes, this is your workspace |
| Adding the **single** `.gitignore` entry (BS4) | ✅ yes, **after approval**, once |
| Reading any other file (code, `specs/`, `docs-generated/`) | ✅ yes, read anything |
| **Writing, modifying, deleting** any other file | ⛔ **FORBIDDEN** |
| Writing code, refactoring, creating a runnable script | ⛔ **FORBIDDEN** |
| Any `git` operation (branch, commit, add, stash) | ⛔ **FORBIDDEN** |
| Entering any phase (02–09) at the end of the conversation | ⛔ **FORBIDDEN** — you propose, you do not enter |

To illustrate plans, **sketches and pseudo-code are allowed** in the working file (short, a few-line block); **do not write working code**, neither in the working file nor in the codebase. If the user asks for code mid-conversation: indicate that this is the flow's job, and suggest the right entry point (`/bs-quick-flow` or `/bs-add-cycles`).

<!-- INCLUDE:shared/path-format.md -->

---

## 1. The session's working file (BS2)

Every brainstorm gets a **persistent working file** in the `.bs-brainstorm/` folder at the project root. This is the session's memory: after `/clear`, a crash, or a resumption days later, the thread of thought can continue from it.

**File name:** `.bs-brainstorm/brainstorm-NN-<slug>.md` — `NN` a two-digit, zero-padded sequence number (`01`, `02`, …), `<slug>` a short, hyphenated English identifier for the topic (`central-cert`, `auth-extraction`).

### 1.a Starting a new session (BS3)

This is the default case — if the user did not explicitly request a continuation, **a new file is created**.

```bash
mkdir -p .bs-brainstorm
ls -1 .bs-brainstorm/ 2>/dev/null | sort
```

The next sequence number is the **largest `NN` among existing files + 1** (empty folder → `01`). **Never overwrite an existing file**, and never reuse a sequence number, even if an earlier file was deleted — advance relative to the largest number found.

Determining the slug:
- If the topic is already apparent from the invocation (`/bs-brainstorm how should central cert management work`), derive a slug from it **immediately**, and create the file before the first round of the conversation.
- If the invocation has no parameter ("let's brainstorm a bit"), create the file as **`brainstorm-NN-untitled.md`**, then, once the topic emerges after the first round, **rename** (`mv`) it to the final slug, and note this in one line. After that the name no longer changes.

Initialize the file with the template from the `## 8. Appendix — the working file's skeleton` section. Ask the system for the date (`date +%F`), do not guess it.

### 1.b Continuing an existing session (BS3/b)

If the invocation refers to a continuation (*"let's continue session 04"*, `/bs-brainstorm continue: 04`):

1. Find the file: `ls -1 .bs-brainstorm/brainstorm-04-*.md`.
2. **If no such number exists:** do not guess and do not create a new one instead — list which sessions exist (number + slug + status), and ask which one was meant.
3. **If it exists:** read in the **entire** file, and before the conversation summarize it for the user in 3–5 lines: where we left off, what the latest decision is, what the most pressing open question is. Continue from here — **do not restart** the exploration, and **do not rephrase** the existing sections (only extend them).
4. If the file's status is `<status:closed>`, ask: should this be reopened, or should a new session start from the continuation instead?

### 1.c The `.gitignore` entry (BS4)

The working files are **not deliverables**: raw thinking, often with unfinished sentences. `.bs-brainstorm/` is therefore excluded from version control — whatever from the brainstorm is worth preserving gets distilled into `cycle-design-input.md` (see section 4), and *that* is what goes into a commit.

On the **first** run (when the folder is created) check `.gitignore`:

```bash
grep -qxF '.bs-brainstorm/*' .gitignore 2>/dev/null && echo "ALREADY_IN" || echo "NOT_IN"
```

If it is not there, ask once:

<!-- INCLUDE:lang/brainstorm.md#BS4-gitignore-felajanlas -->

Only write to `.gitignore` after approval, and add **exactly this one line**: `.bs-brainstorm/*`. If the answer is no, **never ask again** (on subsequent runs either). If, per `conventions.md`, the project has no version control (No-VCS branch), this step is skipped entirely.

> **Mention it once, at the end of the first session:** raw brainstorm files are **local** — they will not exist on another machine, nor in a PR. This is intentional.

---

## 2. Orientation (BS5) — what to read in, and what not to

The value of a brainstorm stands or falls on whether the proposals fit **this specific system**. So orient yourself before the first round of conversation — but **gradually and token-aware**.

### 2.a Mandatory entry (always)

| File | Why |
|---|---|
| `conventions.md` | tech stack, ports, language, merge strategy, whether there is version control |
| `docs-generated/system-overview.md` | **the most valuable** — the as-built truth: what the system does today, with which flows |
| `docs-generated/README.md` | the folder index: this tells you what else is there |
| `specs/roadmap.md` | what is already planned, what is done, what depends on what |

**If none of these exist** (greenfield ideation, `00-init-project` has not run yet): this is not an error, and **not a STOP**. Indicate in one line that this is a blank-slate brainstorm, and that the exit gate at the end of the session will be `/bs-init-project`, not `/bs-add-cycles`.

### 2.b Pulled in by topic (only if needed)

- `docs-generated/architecture.md` — if build, deploy, ops, or runtime topology is involved;
- `docs-generated/design-drift.md` — **a goldmine for brainstorming**: this documents where reality diverges from the plan;
- `docs-generated/CHANGELOG.md`, `specs/test-conventions.md` — if the topic hinges on past decisions or test expectations;
- **one or two specific cycles'** `spec.md`/`plan.md` — only if, based on the roadmap, the topic leads exactly there.

### 2.c What is FORBIDDEN (BS6)

- ⛔ Grinding through the entire `specs/` tree. The roadmap + `system-overview.md` is the entry point; read a specific cycle document only **by name, in a targeted way**.
- ⛔ Bulk-reading raw code files "to have context". This is what the `researcher` is for (see below).
- ⛔ Infinite orientation. If after 2–3 rounds of exploration there still isn't enough material for a first proposal, that doesn't call for more reading, but for **a question to the user**.

### 2.d Exploration with cheap subagents (BS7)

**Wherever possible, do the exploration with the `researcher` subagent**, not yourself. The agent runs on a cheap/fast model, is read-only (`Read`/`Grep`/`Glob`), and by its contract **never returns raw file content**, but a list of `path` + location + one-line summary — this is precisely why it protects the conversation's context. **Mode B (ad-hoc question)** was built for this.

- **Launch several in parallel**, in one round, with independent questions. For example, for a "central cert management" topic: (1) *where is TLS/certificate handling currently in the code and config?*, (2) *what is the current pattern for secret and config management?*, (3) *what do the roadmap and `design-drift.md` say about this area?*
- **One agent = one well-bounded question.** Do not give it a design decision ("propose an architecture") — that is your job with the user; the agent brings back findings, not a verdict.
- **Keep it bounded:** ask for a concrete upper limit in the response (e.g. "the 10 most relevant results"), and do not run the same question twice.
- If a claim is uncertain based on the finding, mark it as **uncertain** in the working file too — don't let it fixate into a fact.

Write every material finding into the working file's **`## <sec:bs_facts>`** section, with a `file:line` anchor — so that the next session (or `01-add-cycles`) doesn't rerun the same search.

---

## 3. Steering the conversation

This is the core of this skill. In ideation mode, work tends to break in two directions: **monologue** (the agent pours out an essay, and doesn't ask) and **agreeing with everything** (it says everything is a good idea). There is a rule against both.

- **One question per round (BS8).** Do not throw 8 questions at once. Pick the one that moves the topic forward the most, ask it, and wait for the answer. Write the rest into the `## <sec:bs_open_questions>` section — they are not lost.
- **Always 2–3 alternatives, with trade-offs, plus an explicit recommendation (BS9).** Neither a listing without a decision ("these are the options, you decide"), nor a decision without alternatives ("let's do it this way"). For every alternative, state **what you give up** for it — if an option has no downside, it wasn't thought through.
- **Fit to the existing system (BS10).** This is the most common ideation mistake: pretty on paper, doesn't work in this project. For every proposal, name concretely **which component/file it affects** (based on `system-overview.md` and the `researcher` findings), and **what conflicts** with `conventions.md`. If there is a conflict, do not stay silent about it: either the proposal changes, or the convention does — and the latter is a separate decision.
- **You do not write code (BS11).** Sketches, pseudo-code, data-flow descriptions, schemas — yes. Working implementation — no.
- **Do not just agree (BS12).** If there is a real risk, contradiction, or hidden cost in the user's idea, say so in a sentence or two — then move on. The decision is theirs; but an unmentioned risk is your mistake. Likewise: if you don't know something, write it out as an open question, do not fill it in with a plausible guess.
- **Stay on topic (BS13).** One working file is **one topic**. If, mid-conversation, an independent second topic opens up, do not merge it in: note it in `## <sec:bs_log>` in one line, and propose a **separate brainstorm session** for it at the end of the session.

---

## 4. Updating the working file (BS14)

**When to write:** after every **substantive round** — if a new fact came up, a decision was made, an alternative was raised or dropped, or an open question was created or closed. For a mere clarifying question-and-answer (*"do you mean the staging environment?" — "yes"*) **do not** write to the file.

**How to write:**
- **Extend, don't rewrite.** Do not rephrase or reorganize existing sections to make them "nicer" — the old paragraphs are the session's memory. A new item goes at the end of the section.
- **Terse items, not an essay.** One fact = one line with a source. One decision = what we decided + one sentence why.
- **Do not paste the skill's text** into the working file, and do not write instructions about yourself into it. The reader of the file is a **human** (and `01-add-cycles`), not you.
- The `## <sec:bs_open_questions>` is a **live, checkable list**: check off what got resolved, and put the decision into section 4. Do not delete the checked-off item — the "why it wasn't done this way" is worth gold later.

---

## 5. Closing and the exit gate (BS15)

When the topic has matured — or the user closes it —, do two things.

**1. Cycle-split proposal (BS16).** Fill in the `## <sec:bs_cycle_split>` section: what **independently developable, independently testable** units the topic breaks into, in what order, what depends on what. This is the real input to `01-add-cycles`, so think in the roadmap's language already (one unit = one cycle candidate, short goal + "how do we know it's done"). If the topic is a **single** small unit, say so — not every brainstorm turns into multiple cycles.

**2. Handoff — propose, but do not enter (BS17).** Set the file's status to `<status:closed>`, and close the conversation with a proposal for the next step:

| If the result is… | Proposed next step |
|---|---|
| a topic that splits into multiple cycles, in an existing project | `/bs-add-cycles brainstorm: NN` — completing the roadmap and populating `cycle-design-input.md` from the brainstorm |
| a small, well-bounded task | `/bs-quick-flow input: <the task in one sentence>` |
| no project convention yet (greenfield) | `/bs-init-project`, then `/bs-add-cycles brainstorm: NN` |
| the topic hasn't matured | stays `<status:in_progress>`; continuation via `/bs-brainstorm let's continue NN` |

`/bs-add-cycles` taking it over is the **bridge**: the raw brainstorm is local and gitignored, while the `cycle-design-input.md` distilled from it goes into a commit. **One bridge, one direction** — `02-write-spec` does not read the brainstorm, it reads `cycle-design-input.md`.

⛔ **Do not enter the next skill on your own.** You give a proposal; the call is the user's. At the end of the response, place a clickable link to the working file.

---

## 6. If you get stuck

- **The user doesn't know what they want.** Do not ask them for a specification. Ask about the *problem*, not the solution: what hurts today, when was it discovered, what's the worst thing that could happen because of it.
- **The topic is too big for one session.** Do not try to cram it into one file. Close out the current one with the decisions made so far, and propose a separate session for the detachable part — reference it in `## <sec:bs_log>`.
- **The user asks for implementation.** Not here: propose `/bs-quick-flow` or `/bs-add-cycles`, and close the brainstorm.
- **A decision requires changing `conventions.md`.** This is not the brainstorm's job: write it in as a decision and an open question, that the convention change is a separate, deliberate step (`/bs-init-project` or per the `conventions-change` process).

---

## 7. Quick sequence

1. **Working file.** New session → next free `NN` + slug; continuation → read in the existing file and a 3–5 line summary. Offer `.gitignore` on first run.
2. **Orientation.** `conventions.md` + `system-overview.md` + `docs-generated/README.md` + `roadmap.md`; by topic `architecture.md` / `design-drift.md`. Codebase exploration with **parallel `researcher` subagents**.
3. **Conversation.** One question / round · 2–3 alternatives + recommendation · fit to the existing system · don't just agree · don't write code.
4. **Persistence.** After a substantive round you extend the working file (never rewrite it).
5. **Closing.** Cycle-split proposal → status `<status:closed>` → handoff to `/bs-add-cycles` (or `/bs-quick-flow`) — **without entering it**.

---

## 8. Appendix — the working file's skeleton

When starting a new session, create the file with exactly this structure (filling in the `<…>` placeholders, omitting the explanatory bracketed lines):

```markdown
<!-- INCLUDE:lang/brainstorm.md#BS2-munkafajl-csontvaz -->
```
