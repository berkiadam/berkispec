<!-- Source note: this section is inlined by the 03a-write-code-plan.md AND the
     03b-write-test-plan.md skill (build-time INCLUDE). Edit it in one place. -->
### 🔴 Stable section identifiers (PID1) — tasks.md references these

**You write a stable identifier into the title of every executable plan section**, directly after the `###`:

```md
### [P-CONFIG] The configuration system and the config files
### [P-REDIS] Extending the Redis connection
### [P-E2E-UI] The Playwright UI E2E
```

| Rule | Mechanics |
|---|---|
| **Format** | `[P-<NAME>]` — uppercase, hyphenated, 1–2 words, referring to the content of the section. An ordinal is **not** part of it (`[P-3-1]` is forbidden). |
| **Who gets an ID** | **Only an executable plan section:** the subsections of the `<sec:planned_changes>` and of the `<sec:test_specification>` / `<sec:testing_strategy>` — where it is described **what has to be done**. |
| **Who does NOT** | `<sec:goal_and_approach>`, `<sec:affected_components>` (an inventory), `<sec:environment_coords>` (an inventory), `<sec:execution_order>`, `<sec:risks>`, `<sec:new_dependencies>`, the IP1 sections. These **cannot be** the targets of a task reference (E). |
| **Uniqueness** | An ID may appear once in the plan. |
| **Stability** | An ID once issued **never changes** — not even if the ordinal of the section shifts, you rename it, or the chapter moves elsewhere. The ID of a deleted section **cannot be reused**. A new section (e.g. inserted by the analyze loop) gets a **new ID**. |
| **Why** | `tasks.md` references an ID instead of an ordinal. If a fix inserts a `§3.10`, the ordinals shift, and the tasks **silently point at the wrong section** — the ID rules this out. |
| **Who issues it** | The IDs of `<sec:planned_changes>` and the non-test sections are issued by `03a`, those of the test sections by `03b`. `03b` **never renames and never deletes** an existing ID. |

_You may use an ordinal for the readability of the title (`### 3.1 [P-CONFIG] …`), but the **referencing key is always the ID**._
