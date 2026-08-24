<!--
  The PROJECT-LANGUAGE blocks of `01-add-cycles` (9.4 extraction).
  The installer inlines this file at build time in place of the INCLUDE markers,
  according to the chosen PROJECT language (`PROJECT_LANG`); the marker form is
  `lang/01-add-cycles.md#<anchor>`.
  The blocks were moved here VERBATIM — do not rephrase, do not unify.
  The ANCHOR lines are NOT part of the inlined text, they are delimiters only (8.9).
  CAUTION: no comment-closing sequence may appear in this leading note.
-->

<!-- ANCHOR:roadmap-struktura -->
# Development Roadmap

**Status:** `Draft` | `Open questions` | `Done`

## Open questions

- [ ] Q01 — <question text>
- [x] Q02 — <question text> → <decision, briefly>

## Cycle 01 — <title>

**Behavior:** What can the system do at the end of the cycle? (1-2 sentences, from the user's perspective)

**Affected components:** Which parts of the system change?

**Prerequisite:** — (or: Cycle NN)

**Mock strategy:** What has to be mocked from the components that are not ready yet?

**Test criterion:** How can it be verified that the cycle is done? (a concrete, decidable statement)

---

## Cycle 02 — <title>

...

<!-- ANCHOR:BD5-ciklus-blokk-sablon -->
## Cycle NN — <title>

**Behavior:** What can the system do at the end of the cycle? (1-2 sentences, from the user's perspective)

**Affected components:** Which parts of the system change?

**Prerequisite:** — (or: Cycle NN — from the existing ones)

**Mock strategy:** What has to be mocked from the components that are not ready yet?

**Test criterion:** How can it be verified that the cycle is done? (a concrete, decidable statement)

<!-- ANCHOR:CD1-design-input-sablon -->
# cycle NN design input from user

> **This file is Yours.** Write down here, in your own words, what you would like in this cycle:
> expectations, a sketch of the behavior, an example request/response, a process description, constraints, references, notes.
>
> **Filling it in is not mandatory** — left empty, the flow works unchanged.
> If you do write here, however, two phases read it automatically:
> - `bs-write-spec` (02) — the **behavioral** content, as the starting point of `spec.md` (alongside the entry in `roadmap.md`);
> - `bs-write-plan` (03) — the **technical/procedural** content (commands, hosts, components, constraints) for `plan.md`.
>
> The format is not constrained: running text, a list, a table, a code snippet — anything works.
> No phase overwrites this file.

<!-- Write here. -->

<!-- ANCHOR:specs-ures-kerdes -->
> *"The `specs/` directory is empty. What would you like to do?*
> *A) Full roadmap planning — we define all the development cycles and create `specs/roadmap.md`*
> *B) Adding a single cycle — we only add one new cycle to the roadmap"*

<!-- ANCHOR:ciklusok-roadmappal -->
     > *"I found [N] existing cycles: [cycle-01-xxx, cycle-02-xxx, ...]. I am adding a new cycle to the roadmap."*

<!-- ANCHOR:ciklusok-roadmap-nelkul -->
     > *"I found [N] existing cycles in the `specs/` folder, but I cannot find the `specs/roadmap.md` file. Which cycle are we working with now? I will restore the roadmap block of that cycle (per cycle, on the feature branch of the cycle) — the other cycles live on their own branch / in the merged main roadmap."*

<!-- ANCHOR:roadmap-statusz-megerosites -->
*"The roadmap quality check passed and every question is closed. Is the roadmap ready? If you confirm, I will switch it to `Done` status."*

<!-- ANCHOR:A-mod-zaro-uzenet -->
*"The roadmap is done. We can continue with the spec phase of cycle 1 (02). I created the `specs/cycle-01-<name>/cycle-design-input.md` file — you can write the specification of cycle 1 there in your own words. Filling it in is not mandatory, but if you write in it, `bs-write-spec` will take it into account."*

<!-- ANCHOR:BQ2-ciklusszam-jelzes -->
   > *"Existing cycles: [N pcs — cycle-01-xxx, ...]. Next cycle number: [NN]."*

<!-- ANCHOR:BD5-cel-kerdes -->
   > *"What is the goal of the new cycle? Describe briefly what behavior you would like to implement."*

<!-- ANCHOR:BS-quick-flow-javaslat -->
   > > *"This task looks small enough that the full development cycle (separate spec/plan/tasks + analyze/validate/review) may be too much for it. I recommend the simplified flow instead (`/bs-quick-flow`): `spec.md` → `task.md` → implementation, in a few steps. Shall we go with that, or would you still like a full cycle?"*

<!-- ANCHOR:BD5-nevjavaslat -->
   > *"Based on the goal, the suggested name is: `[suggested-name]`. This will be the name of the branch and of the folder as well (e.g. `cycle-NN-[suggested-name]`). Is it suitable, or would you prefer something else?"*

<!-- ANCHOR:BD5-roadmap-megerosites -->
   > *"I added the Cycle NN — [title] description. If you confirm, I will update the roadmap status to `Done` and create the directory of the cycle."*

<!-- ANCHOR:B-mod-zaro-uzenet -->
     > *"Cycle NN — [title] added. Directory created: `specs/cycle-NN-<cycle-name>/`*
     >
     > *I created the `specs/cycle-NN-<cycle-name>/cycle-design-input.md` file. **You can write the specification of the cycle there in your own words** — expectations, a sketch, examples, anything that is on your mind. **Filling it in is not mandatory**, the flow can continue with it empty; but if you write in it, `bs-write-spec` (02) reads it and takes it into account as the starting point of the spec. It is worth filling in BEFORE starting the spec phase.*
     >
     > *Next step — writing the spec. Before starting the new phase, be sure to run a `/clear` command to empty the context, then use this command:*
     > ```
     > /bs-write-spec input: @specs/roadmap.md, cycle: cycle-NN-<cycle-name>
     > ```"*

<!-- ANCHOR:BS18-design-input-brainstormbol -->
> *"I created the `specs/cycle-NN-<name>/cycle-design-input.md` file and filled it with the decisions of brainstorm session NN. **Read it through** — this will be the starting point of `bs-write-spec` (02). Feel free to correct, extend or delete from it; the file is Yours, no phase overwrites it."*

<!-- ANCHOR:BQ5-C-mod-jelzes -->
   > *"I restored/corrected the roadmap block of `cycle-NN-<name>` in `specs/roadmap.md`. Please review it. If it is in order and you confirm, I will commit it on the branch of the cycle."*
