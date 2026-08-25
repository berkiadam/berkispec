<!--
  SHARED description of the HANDOVER BETWEEN PHASES (`*-input-from-prev.md`) — IP1.
  This is NOT a standalone skill/agent, but a shared text block that the installer
  (install-helper.py) embeds INLINE at build time into the installed version of the
  referencing skill (in place of the `<!-- INCLUDE:shared/input-from-prev.md -->` marker).
  Referenced by: 01-add-cycles, 02-write-spec, 03-write-plan, 04-write-tasks,
  07-validate. The quick-flow does NOT (it is three-phase and runs in one context).
  The skill writes its own, phase-specific part AROUND the marker (what it reads,
  which files it may write) — this block contains only the shared rules.
  It has no frontmatter: its content is copied in verbatim. Edit it here.
-->

**What it is for (IP1):** in a phase, information often surfaces that is **valuable but does not belong there** — too technical, too detailed, or simply the business of the next phase. So far the skills instructed to **delete** it (e.g. 02: "if a sentence names a technology, a file name, a function → that belongs in the plan, delete it from the spec"), that is, the information was lost. These files give it a destination instead of the bin.

**The files** — all in the folder of the cycle (`specs/cycle-NN-<cycle-name>/`):

| File | Who may write it | Who consumes it |
|---|---|---|
| `spec-input-from-prev.md` | 01-add-cycles | **02**-write-spec |
| `plan-input-from-prev.md` | 01, 02 | **03**-write-plan |
| `tasks-input-from-prev.md` | 02, 03 | **04**-write-tasks |
| `validate-input-from-prev.md` | 03, 04 | **07**-validate |

**One phase may write into several files** in the same run, if the information has to be spread out (e.g. a technical detail coming up in 02 goes into the `plan-input`, and the testing prerequisite following from it goes into the `validate-input`).

> **06-implement** deliberately does **not** get such a file: it reads `plan.md` and `tasks.md` anyway, so an implementation detail belongs there, not into a separate channel.

**Item format** (a checkbox list, following the pattern of the question files):

```md
<!-- INCLUDE:lang/input-from-prev.md#IP1-tetel-formatum -->
```

**Rules:**

1. **We never delete.** A closed item is marked with `[x]`, and a one-line note is written next to it (`→ incorporated: <where>` or `→ dropped: <why>`). The text and the decision stay.
2. **It does not block** — in contrast to the open questions of `*-questions.md`, an open `[ ]` item **does not stop** the phase along the way. **But no open item may remain when the phase is closed:** it is a mandatory point of the quality check that every item is either **incorporated** or **explicitly dropped with a justification**. Silently stepping over it is forbidden.
3. **It does not ask.** The boundary towards `*-questions.md`: a **question** = "I do not know, you decide"; the **input-from-prev** = "I do know, but it does not belong here". If an item **also** is a question to be decided, then raise it as a question in the `*-questions.md` of your own phase — the input file only hands over, it does not ask.
4. **Do not create an empty skeleton.** The file **comes into existence only** if there is something to write into it. If there is no information to hand over, the file should not exist — the consuming phase does not treat its absence as an error.
   > **One single exception: `01-add-cycles` ALWAYS creates `spec-input-from-prev.md`**, with an empty template as well. The reason: this is the **first** handoff file of the chain, and 01 is the only phase that builds the cycle folder from scratch — if it is missing here, 02 does not see the "there is no information to hand over" case, but that the channel does not even exist, and from 03 onward nobody knows there would have been anywhere to write. **For the other three files (`plan-`, `tasks-`, `validate-input-from-prev.md`) the rule above applies unchanged.**
   > **An empty skeleton is not a call to fill it in:** if there is no item to hand over, the list should stay empty — do not invent items so that "the file is not empty".
5. **What belongs not into the next phase but into a later CYCLE** does **not** go here, but into `specs/roadmap.md` (into the entry of a new or an existing cycle). Only information meant for the further phases of the **current cycle** goes into these files.
6. **The self-healing loops (the fix modes of 05/07/09) ignore these files completely** — they neither read nor write them. The fix mode is a targeted correction for a `<status:must_fix>` list; re-running the handover mechanism there would only be cost and noise. (The **read-only diagnosis** of 05 is a separate matter: it does report if an item was left open — see the 05 skill.)
7. **Do not rewrite the artifact of another phase.** If a plan-level detail comes up in 02, you write it into `plan-input-from-prev.md` — **not** into `plan.md` (which does not even exist yet, or is not managed by your phase).
