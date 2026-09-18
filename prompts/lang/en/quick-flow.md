<!--
  The PROJECT-LANGUAGE blocks of `quick-flow` (9.4 extraction).
  The installer inlines this file at build time in place of the INCLUDE markers,
  according to the chosen PROJECT language (`PROJECT_LANG`); the marker form is
  `lang/quick-flow.md#<anchor>`.
  The blocks were moved here VERBATIM — do not rephrase, do not unify.
  The ANCHOR lines are NOT part of the inlined text, they are delimiters only (8.9).
  CAUTION: no comment-closing sequence may appear in this leading note.
-->

<!-- ANCHOR:BS-flow-valtas-javaslat -->
> *"This task is larger / more complex than expected (e.g. it touches several components, it requires substantial coding). I recommend that we do not use the simplified flow, but the full berki spec process, which starts with the `01-add-cycles` skill (roadmap + a dedicated cycle). May I continue that way?"*

<!-- ANCHOR:BS-roadmap-sor -->
## Cycle NN — <title>

**Behavior:** <what the system can do at the end of the cycle — 1-2 sentences, from the user's perspective>

**Affected components:** <which parts of the system change>

**Test criterion:** <a concrete, decidable statement about when the cycle is done>

_(Simplified [quick-flow] cycle. On closing, the heading gets a `✅` mark.)_

<!-- ANCHOR:BS-drift-sor -->
- **<identifier>** — Design: <what `docs-generated/` says today>. As-built: <what this cycle changed>. Reason/status: simplified cycle `cycle-NN_quick-flow_<cycle-name>`, carrying it over into `docs-generated/` awaits the `08-doc-sync` phase of the next full cycle.

<!-- ANCHOR:LD10-teszt-leltar-drift-sor -->
- **test inventory** — Design: `docs-generated/test-description.md` describes the test suite from before `cycle-NN`. As-built: this cycle added/changed a test (`<which test file(s)>`). Reason/status: simplified cycle `cycle-NN_quick-flow_<cycle-name>`, carrying the inventory over awaits the `08-doc-sync` phase of the next full cycle (the owner is `08`, LD1).
