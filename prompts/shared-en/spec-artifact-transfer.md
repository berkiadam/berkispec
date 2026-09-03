<!-- Source note: this section is inlined by 03a-write-code-plan.md, 03b-write-test-plan.md
     AND the plan-fixer agent (build-time INCLUDE). Edit it in one place. -->
## Lifting over an elaborated spec artifact — verbatim, without truncation (KX3)

> **This is the OPPOSITE case of `Reference resolution`, and the other most frequent error in this phase.** The previous section is about the input being **too abstract** (it references something instead of containing it) — then it has to be resolved. This section is about the input being **already fully elaborated**: `spec.md` contains a finished OpenAPI descriptor, a complete request/response payload, an error matrix or a ten-step test scenario with expected results. In that case the agent tends to **"abstract it into a plan"**: it merges the steps, replaces the payload with a list of field names, substitutes the descriptor with a "the spec defines it in detail" sentence. **This is data loss, not planning.**

**The rule (the mirror of the `KX2` rule of 02):** if the spec (or `cycle-design-input.md`, `*-input-from-prev.md`, the plan of an earlier cycle) gives an artifact **already elaborated**, it has to be carried over into the plan **verbatim, in its entirety**. **The direction is extension and refinement — merging and omission are not.**

**What it necessarily applies to (the nature of the list is the point, not its length):**

| The artifact in the spec | How it goes into the plan |
|---|---|
| an OpenAPI / JSON Schema / Avro / proto / GraphQL fragment | **as an unchanged block**, with every field, type, `required` and example |
| a request/response payload | **as complete JSON**, with every mandatory and optional field — not as a list of field names |
| an error matrix (status + `errorCode` + body) | **as a complete table**, with every row — not as "the error handling is according to the spec" |
| a multi-step test scenario (①…②…③, with expected results) | **every step, every intermediate check and every expected result** — the steps must not be merged |
| a cache key schema / DB DDL / a migration script | verbatim, with the complete key and field list |
| a configuration template (`.env`, a compose fragment, YAML) | verbatim, with every key |

**What you may — and have to — do:**
- replace the **symbolic coordinates with concrete values** (`{PUBLIC_BASE_URL}` → the actual URL) — this is the rule of `Reference resolution`, therefore an **extension**;
- **add** what is the level of the plan: a test case identifier (`TC-XX-01`), the test level, the run command, the fixture, the environment preparation;
- **spell out** an incomplete step (a missing intermediate check, an expected result that was not given);
- **reorder**, if the order is not executable (report a non-trivial reordering).

**What is forbidden:**
- ❌ **merging** steps or replacing them with a summary of the "the process runs through" kind;
- ❌ replacing a payload with a **list of field names**, a table with **prose**;
- ❌ **referencing** it: *"see the Test specification section of `spec.md`"*, *"the spec describes it in detail"*, *"the other cases are similar"*, *"…etc."*;
- ❌ **leaving out an example** on the grounds that "the schema is enough on its own".

**A self-check (measurable):** the corresponding section of the plan **cannot be shorter** than its source section in the spec. If it did become shorter, that has to be **proven**, it is not self-evident: name what moved elsewhere (e.g. into a separate `<sec:schema_artifacts>` entry), or add it. The mechanical gate of `05-analyze` also measures this mechanically (the `V1`/`V2` check): it looks for the content of the code blocks of the spec in the plan, and compares the extent of the two test sections.

> **The three rules that are easy to misread and therefore tend to conflict — the resolution:**
> - *"The plan is a plan, not an archive"* (see `Reference resolution`) applies to the **source files of the repo**: from a 2000-line script only the part needed for the execution is needed. It **does not apply to the contract artifacts coming from the spec** — those belong to the content of the plan in their entirety.
> - *"The abstraction level of the spec has to be resolved, not reproduced"* is true of the **abstraction level**, not of the **content**: the symbolic coordinate has to be made concrete, but the level of detail has to be preserved (indeed increased).
> - The **duplication category** of `05-analyze` (1.) does **not** apply to the verbatim lifting of the spec → the plan: that is not redundancy but the mandatory self-containedness. Duplication is when the same decision appears twice **within** the plan, or when tasks.md describes the test case steps of the plan again.
