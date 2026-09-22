# Two development routes

← [Back to the main page](../../README.md) · [Page index](README.md)

The user has **two routes**; the weight of the task decides which one fits:

1. **The full berki spec flow (phases 00–09)** — for larger, more complex developments. Separate `spec.md` → `plan.md` → `tasks.md` documents, with cross-phase `analyze`, `validate`, `doc-sync` and `review` quality gates and self-healing loops. On an empty project it starts with the `00-init-project` skill, for a new cycle with `01-add-cycles`. The rest of this README describes this route.

2. **The simplified (lightweight) flow** — for small, well-bounded tasks that can be solved in 3-4 steps (e.g. **assembling a configuration**, **writing a simpler script**, a minor fix). A single three-phase recipe: `spec-plan.md` → `tasks.md` → implementation, in the `/bs-quick-flow` skill. Both artifacts carry a **status field**, so the phase boundary is a committed fact (`/bs-cycle-status` reads it from there too). There is no separate plan/bs-analyze/bs-validate/bs-doc-sync phase; it calls the optional agents (`researcher`, `analyzer`, `reviewer`) only when they genuinely help.

**How to decide?**

| Characteristic | Simplified flow | Full berki spec flow |
|---|---|---|
| Typical task | configuration, simple script, minor fix | new feature, several components, complex logic |
| Size | solvable in 3-4 steps | self-contained, vertically sliceable cycle(s) |
| Documents | `spec-plan.md` + `tasks.md` (both with a status field) | `spec.md` + `plan.md` + `tasks.md` |
| Quality gates | inline + optional agents | `analyze` / `validate` / `doc-sync` / `review` loops |
| Entry point | `/bs-quick-flow` | `/bs-init-project` / `/bs-add-cycles` |

**Default flow:** the character of the project is clarified in the `00-init-project` phase (product development vs. configuration/scripting), and based on that a **default flow** is written into the **Default flow** field of the `## Development methodology` section of `conventions.md`. That is the starting point — it can be overridden per task.

The two routes are **interchangeable**: if during the simplified flow it turns out that the task outgrows it (more code to write, several components, complex design), the skill stops the work and **redirects to the full process** (`01-add-cycles`). And the other way round: `01-add-cycles` and `03a-write-code-plan` will flag it if the task is too simple for a full cycle, and suggest the simplified flow.

## 1.1 Before either route (optional): `/bs-brainstorm`

The **shared antechamber** of the two routes is the `/bs-brainstorm` helper command — for the case when the question is not yet the *size*, but **what and how** we want at all. ("How should we implement central certificate management?", "Is it worth extracting auth?") This gap sits **before** the `00–09` flow: `01-add-cycles` already assumes that you know what you want (it only has to be split into cycles), and `/bs-quick-flow` assumes the task is small and clear.

**What it does:**
- **Orients itself** in the project: `conventions.md`, `docs-generated/system-overview.md` (the as-built truth), `docs-generated/README.md` (folder index), `specs/roadmap.md` — and, depending on the topic, `architecture.md` and `design-drift.md`. Grinding through the whole `specs/` tree is forbidden (BS6).
- **It explores the codebase with cheap, parallel `researcher` subagents** (Mode B, read-only, cheapest tier, "never raw file content") — so the context of the conversation carries a list of findings rather than dozens of files (BS7).
- **It converses, it does not monologue:** **one** question at a time, for every proposal **2–3 alternatives with trade-offs + an explicit recommendation**, mandatory fitting to the existing system and to `conventions.md`, and sycophancy is forbidden — a risk that was not raised is the agent's fault (BS8–BS13).
- **It persists:** the material of the session goes into the `.bs-brainstorm/brainstorm-NN-<slug>.md` working file with a fixed skeleton (*Goal · Discovered facts with sources · Alternatives · Decisions · Open questions · Proposed cycle split · Log*). After every substantive round it **grows** — it is never rewritten (BS14). So it can be continued after a `/clear`, a crash or a return days later: `/bs-brainstorm let's continue number 04`.

**Hard limits (BS1):** it writes no code, runs no `git`, and modifies **not a single file** outside the `.bs-brainstorm/` folder — with one exception: on the first run it offers to add the `.bs-brainstorm/*` entry to `.gitignore` (after approval, once). At the end it **recommends**, but does not enter the next skill.

**The bridge towards the flow (BS18):** the raw working file is **local and gitignored** (raw thinking, not a deliverable) — whatever is worth keeping is distilled into the cycle's `cycle-design-input.md`, and *that* is what gets committed:

```
/bs-brainstorm how should central cert management work
        ↓                      .bs-brainstorm/brainstorm-04-central-cert.md   (gitignored)
/bs-add-cycles brainstorm: 04
        ↓                      specs/cycle-NN-<name>/cycle-design-input.md    (committed)
/bs-write-spec
```

`01-add-cycles` takes the `## 6. Proposed cycle split` section as the starting point of the roadmap proposal, and asks the unticked items of `## 5. Open questions` **as questions** — whatever the working file already answers, it does not ask again. **One bridge, one direction:** `02-write-spec` does not read the brainstorm, it reads `cycle-design-input.md`.
