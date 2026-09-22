# docs-generated/ — living documentation

← [Back to the main page](../../README.md) · [Page index](README.md)

The **`docs-generated/`** folder in the project root is the home of the **generated, "as-built" documentation** maintained cycle by cycle by the `08-doc-sync` phase. It is to be distinguished from the hand-written `docs/` folder: **everything that the AI/skill produces or that is a project requirement goes here**, and doc-sync **guarantees the consistency of every file in the folder** with the implemented system (DS11). The folder (and its contents) **must be committed** — it is the deliverable and must not go into `.gitignore`.

Every generated doc gets a **header block** (DS17): `> **Covered:** up to cycle-NN · **Last updated:** cycle-NN (date) · **Generator/scope:** <what it covers, and on what basis it is to be kept consistent>`. The file names are **English** (a codebase convention), while the content is in the **project language** (as with the skills).
| File | What it is | Who writes it / when | Where it lives |
|---|---|---|---|
| `README.md` | The **index/manifest** of the folder — a one-line description per file. A new generated file → it must be added; a stale entry → out (set equality with the actual contents, DS21). | 08-doc-sync creates it together with the folder, and maintains it on every run. | `docs-generated/README.md` (separate from `prompts/README.md` and from the root `README.md`) |
| `system-overview.md` | An **as-built functional overview** (at onboarding/stakeholder altitude): capabilities/flows (by capability, not by cycle), consolidated sequences (mermaid), the state model, [conditionally] an endpoint inventory. The missing intermediate level between the spec and `architecture.md`. | 08-doc-sync composes it from `src/` + the closed spec.md files + the roadmap; `02-write-spec` **reads it back** as a "pull", as a current-truth starting point (DS5). | `docs-generated/system-overview.md` |
| `architecture.md` | **"How it is built/runs"** — components, build, deployment, ops. The earlier `docs/architecture.md` moved here; the `TLAST` architecture-writing task of 06 has been **retired** (DS4) — doc-sync is its **exclusive owner**. | 08-doc-sync reconciles it in every cycle (carried over from the earlier documentation step of 09). | `docs-generated/architecture.md` |
| `CHANGELOG.md` | A **detailed, incremental, per-cycle** change log — what changed in the behaviour/documentation of the system. `system-overview.md` only keeps a coverage marker + a link to it (it does not duplicate). | 08-doc-sync extends it with a new cycle entry on every run (DS15). | `docs-generated/CHANGELOG.md` |
| `design-drift.md` | The **deviations of the implemented system from the HLD/LLD intent** (DS20) — e.g. RFC 8693 token exchange vs. legacy Keycloak. A resolved deviation is not deleted, it moves into the "Closed deviations" section. `system-overview.md` stays purely as-built (the drift does not get mixed into it). | 08-doc-sync fills it up incrementally; only **explicit** drift (named by the spec) or checklist-based drift gets in, and an uncertain case → `doc-sync-questions.md` (DS24d). | `docs-generated/design-drift.md` |
| `test-description.md` | The **test inventory** of the project (LD1–LD8): the `TL-NNN` items per category — `Environment` (`local`/`remote`), `Goal`, `Steps` (a concrete command), `Expected result`, `Run command`, `Recipe`, `Last run`, `Source cycle`. It answers **which tests exist and what they prove** — while `test-conventions.md` answers **how I run them** (field-level ownership, D3). The `TL-NNN` is a **project-level, never reused** identifier; the item of a retired test gets a `Retired` marking and **stays** in the file (an audit trail, D4). | The 08-doc-sync is its **exclusive owner**; its completeness is protected by a **hard gate** (`test-inventory-check.py`, LD5): every test file discovered with the globs of the `### Test file locations` of `conventions.md` needs an item, and the command of every item has to point to an existing file. Its consumers (read-only): `02-write-spec`, `03b-write-test-plan` (the regression round + avoiding duplication), `bs-manual-test-plan` (the third source of the `TG-NN` groups). | `docs-generated/test-description.md` |
| _(project-specific extra docs)_ | Any further generated doc (the skill does **not** hardcode them, e.g. the configuration description of an external system). | The folder walk finds it and `doc-sync-plan.md` picks it up; the header scope decides the affectedness. | `docs-generated/<file>` |

**The consistency gate (DS22):** at the end of every run, doc-sync executes an objective, project-independent core gate. Three of its points (no discontinued/renamed identifier in the docs, set equality of the folder index, the coverage-marker bump) are **fully scripted** — they are done by `prompts/scripts/ds22-gate-check.py`, there is no LLM judgement in them, and that is why the installer automatically copies it into the scripts folder of every platform (`.claude/scripts/`, `.agents/scripts/`, `.github/scripts/`). The 4th point (whether every diagram in the source has been carried over) is only assisted by the script with an informative mermaid-block count; the actual pairing decision belongs to the agent. Conditionally (if the `## Project references` section of `conventions.md` declares an API descriptor) an endpoint/interface cross-check also runs. On a failure, the concrete divergence goes into `doc-sync-questions.md` and a **human-driven** correction starts, until the gate goes green.

## 11.1 specs/test-conventions.md — recurring test expectations and recipes (TC1–TC11)

**File:** `specs/test-conventions.md` (next to `specs/roadmap.md` — **not** in `docs-generated/`). **Its owner:** `08-doc-sync`. **Its consumers:** `02-write-spec`, `03a-write-code-plan` and `03b-write-test-plan` (`quick-flow` only reads it).

> **The `docs-generated/test-description.md` test inventory does NOT replace this file, nor the other way round (D3).** The boundary is **field-level ownership**: the inventory is the truth of *goal / steps / expected result* for **every** test; this register is the truth of the *recipe* (`Startup`, `Example call`, `Prerequisite`, `Cleanup`, the credential pointer) for the **promoted, recurring** expectations. **The two never carry the same field**, on a conflict the given file wins per field, and the link is given by a **two-way** reference: the inventory item points to the `R-NN` in its `Recipe` field, and the recipe datasheet points back to the `TL-NNN` in its `Inventory items` field. `test-inventory-check.py` measures **both directions** — a one-sided reference is a failure (LD6).

**What problem it solves:** as a project progresses, it emerges **what has to be tested in every cycle and in what order** — and which recipe belongs to what (e.g. "build the Keycloak dev image, push it to the registry, restart the pod, then check the token exchange with `curl`"). Up to now this knowledge arose in **cycle-local** artifacts (`plan-questions.md`) and was lost at the end of every cycle, so the next cycle **asked the same thing again**. This file is the durable distillate of that dialogue.

**Its structure — a mandatory coordinate block + three sections** (2/3 reference 1, and 1 references 0):

| Section | Content |
|---|---|
| **0. Coordinates** (TC13 — mandatory, at the beginning of the file) | **Every concrete value in one place, searchably:** environments and endpoints (environment, component, URL+port, health endpoint), test users/clients/secrets (environment, identifier, the secret **or a pointer**, scope), parameters and env files. This is the source of truth: the recipes reference it, they do not copy it — if a port or a host changes, it is enough to change it here. The TC5 secret rule applies here too (a shared-platform credential only as a pointer). The TC8 gate checks that it exists, stands at the front, and contains a **filled-in** (not placeholder) row. |
| **1. Recipe register** | Parameters, URLs, ports, component coordinates (repo path, image name, registry target, namespace/pod), test users, example REST/`curl` calls, build/deploy/start commands, prerequisites and order, a scope marker (`local` / `shared-remote`). |
| **2. Local (mock-based) tests needed in every round** | Items referencing the recipes of section 1. |
| **3. Integration / E2E tests needed in every round** | The same. |

**Promotion is always the user's decision (TC12).** In every doc-sync run the phase **offers the cycle's tests item by item**: from the Testing strategy of `plan.md`, the `[RED]`/`[CHECK]`/`TREG` tasks of `tasks.md` and the actual runs in `test-report/` it assembles a candidate list, and for each one it writes down the **self-contained behaviour description** (this is how it would be added), the target section, the recipe needed (an existing `R-ID` or a new one) and a **recommendation + a reason** — then, **in a single round**, it asks in `doc-sync-questions.md` which ones it should lift to project level. This is a **blocking question**: no promotion happens without an answer, and the phase cannot be closed with an open promotion question either. Whatever is not added goes into the **`## Non-promoted candidates (decision log)`** appendix at the end of the file, so that the next cycle **does not ask about it again**. Only a test that **actually ran and was green** in this cycle may be offered (TC3).

**Two quality rules that the TC8 gate enforces:**

- **TC10 — self-contained items.** The "What it verifies" description of sections 2/3 **must not reference another document**: neither a spec section number (`1.2. FlowX Mock negative tests`) nor a cycle (`Cycle 19 init-hash tests`). The reader (a 02/03 phase with a fresh context, or a new colleague) will not open the closed `spec.md` files. Instead, a **behaviour-level** description is required: *"the mock `/start-process` returns 201 for a valid `processName`, and 400 for a missing body"*. The cycle number belongs in the `Last run` / `Evidence` column.
- **TC10/b — the detailed description of the test comes over too.** The table is an **index**, not a test case: for every promoted item a `### <ID>` **detail block** is mandatory below the table — `Goal` / `Prerequisite` / `Steps` / `Expected result`. The content of the test description written in the cycle's `spec.md`/`plan.md` **comes over in full** (if there were three steps and two error codes there, there will be as many here), but **normalised to be self-contained**: the spec numbering, the cycle reference and any "see above" are resolved or deleted, and the secrets are replaced with pointers. The "do not write prose" rule applies **only to narrative explanation** (justifications, lessons), not to the structured description of the test cases — the skill now explicitly rules out this misunderstanding.
- **TC11 — runnable coordinates.** The mandatory elements of every recipe: **`Startup`** (how I bring up the environment needed + a health check; for a unit test an explicit `N/A`), **`Example call`** (the full URL, headers, payload, expected response — a `curl` or `.http` block; if a token is needed, the call to obtain the token too), and **`Shutdown / cleanup`**. The environment prerequisites of section 3 (*"a local Keycloak is running"*) **have to reference an `R-ID`** — otherwise it does not become clear how they can be satisfied, and the test is not reproducible.

**The most important rule (TC1/a) — this is NOT a runnable source.** Nothing runs automatically from the register: the `test-runner` subagent **does not read** this file, only the `Testing strategy` / `Regression impact` sections of `plan.md`. A recipe is executed if and only if the `02`/`03` phase has consciously **lifted** it into the cycle's `spec.md`/`plan.md` — if in doubt, by interviewing the user. That lifting is itself the human control point: **`plan.md` is the single truth of the execution**, and the register is the memory.

**The two projections of the lifting** (per the existing spec/plan boundary):
- **`spec.md` → `Test specification` / `Definition of done`:** those items of sections 2/3 that the cycle takes on as an **acceptance criterion** — at **behaviour level**, referencing the item's ID. No command, test file path or tool name goes here. Purely "must not break" style regression items do not go into the spec.
- **`plan.md` → `Testing strategy` / `E2E infrastructure` / `Regression impact`:** the **complete, self-contained** lifting — every URL, port, namespace/pod, image name, test user and password, parameter, **example `curl` call**, build/push/restart command, prerequisite and order, **verbatim**. A bare reference or a placeholder is forbidden (the `test-runner` sees only this); the register is referenced only as **provenance**. The quality check of 03 explicitly verifies this.

**A living snapshot, not a journal (TC4):** next to every item there is a `Last run: cycle-NN` marker; the file always reflects the current state. If a component has been discontinued or the item is no longer meaningful, the item is **deleted** (not archived) — the fact and the reason for the deletion go into `CHANGELOG.md`, and every deletion is a **separate, tickable plan item** in `doc-sync-plan.md`, so that the user can see it. An environment coordinate (URL, pod) cannot be verified automatically, so with a marker 3+ cycles old doc-sync **asks about it**.

**Evidence-based promotion (TC3):** what counts as "fundamental" is not decided "by feel". An item is promoted if (a) it comes from an earlier cycle and appeared in the regression list of `plan.md` in **this** cycle too, or actually ran — i.e. it has proved its cycle-independent relevance — **or** (b) the user has confirmed it. A recipe only if it **ran green in this cycle**; **writing in an invented command is forbidden**.

**Secret classification (TC5)** — a scope-based, mechanical decision ("does it authenticate a person, or does it grant access to a shared platform?"):

| May be included (dev-scoped, not belonging to a person) | Pointer only (authenticates a person / a shared platform) |
|---|---|
| seeded dev test users + their passwords, a dev IdP realm admin, a local DB user, a mock API key, a dev client secret | cluster/OpenShift login, a registry push credential, VPN, cloud IAM, a git/CI token, anything that also works on test/prod |

An uncertain case → a question, and until there is an answer, **a pointer goes in, not a value**. (Because of the Clean Slate rule, the items in the left column are typically already in the repo today, in the seed/realm-import files.)

**Bootstrap in an existing project (TC6):** berkispec may be introduced into a project already in its 30th cycle, where the file has never existed. In that case the `doc-sync-planner` **assembles a proposal** from the existing material (the test sections of closed `spec.md`/`plan.md` files, closed `plan-questions.md` files — this is where the environment coordinates are —, the `test/` folder, the E2E compose file, the `conventions.md` references), and doc-sync holds a dialogue **about that** — it does not ask from a blank page. If there is not a single promotable item, the file **is not created** (no empty skeleton is produced, because the next phase would fill that in by guessing). The bootstrap is **independent** of the bootstrap branch of `docs-generated/`.

**Question scope (TC7):** it has to ask in every cycle, but the extent differs — a **broad interview at bootstrap**, and in **steady state** a short, targeted confirmation of doc-sync's proposal ("I would promote this, delete that, and bump these — ok?"). The channel is `doc-sync-questions.md`, so that it can be continued even after an interrupted run.

**Its own gate (TC8) — scripted:** the DS22 core gate runs on `docs-generated/`, and this file is outside that, so it has its own gate. The gate is **fully deterministic, without an LLM judgement** — it is done by `prompts/scripts/tc8-gate-check.py`, which the installer copies into the same platform scripts folder as `ds22-gate-check.py` (`.claude/scripts/`, `.agents/scripts/`, `.github/scripts/`, `.codex/scripts/`, `.cursor/scripts/`):

```bash
python3 <platform-scripts-folder>/tc8-gate-check.py specs/test-conventions.md \
  --project-root . --marker cycle-NN [--stale-after 3]
```

| # | Check | Blocking? |
|---|---|---|
| 1 | **Path existence** — do the named repo-internal paths (test file, script, compose, component folder) exist | **FAIL** if the parent folder exists but the target does not (a sure sign of staleness); if it cannot be resolved as repo-internal (an external reference, an image ref, an HTTP endpoint), only **WARN** |
| 2 | **Dangling reference** — does every item of sections 2/3 reference an existing section-1 recipe (`R-ID`) | **FAIL**; an unreferenced recipe is a **WARN** |
| 3 | **Secret check (TC5)** — has a forbidden credential been included | **FAIL** on a certain pattern (a PAT/key prefix, a private key block, `oc login --password`, `docker login -p`); a platform word + a credential word in the same line is a **WARN** |
| 4 | **The `Last run` marker (TC4)** — is there a marker, and which one has gone stale | a missing marker is a **FAIL**; a stale one (3+ cycles by default) is a **WARN** → a question trigger |

Exit code: `0` = every hard check PASSed (a WARN is allowed), `1` = at least one FAIL, `2` = a usage error. **If the file does not exist, the script returns `0` with a "skipped" indication** (TC6: its absence in an early cycle is not a defect). A WARN does not block, but it must not be ignored either: the answer to each one is a fix or a `doc-sync-questions.md` question. On a failure, the same **human-driven** fixing loop runs as with DS22.

**What does not belong here:** `conventions.md` records **how** we test (tools, folder structure, commands, principles — owned by a human, stable); `plan.md` records what is **new** in this cycle. This file records **what has to be tested and when**, per component, as-built.

## 11.2 export/ — versioned PDF export (`/bs-export-doc`)

**Command:** `/bs-export-doc` · **Script:** `prompts/scripts/export-doc.py` · **Output:** `export/<name>-v<N>.pdf`

The `docs-generated/` docs live in **markdown** — but life asks for a shareable, archivable version in PDF (stakeholder review, audit, an onboarding pack). This helper command provides that, **together with the mermaid diagrams**. **It is not a phase:** it has no prerequisite, it changes no status, and it can be run at any time.

**What it exports:**
- **without a parameter**, the two mandatory generated docs (`docs-generated/architecture.md`, `docs-generated/system-overview.md`);
- **with a parameter**, the named file(s) — the skill resolves the free text ("from the cycle-16 plan too") into concrete paths, and reads back what it is going to do before exporting.

**Versioning:** an **independent** counter per file — the maximum of the `<name>-v<N>.pdf` files in the `export/` folder **+ 1**, and `v1` for an empty folder. **The cycle goes not into the file name** but onto the **title page** of the PDF (`Covered: up to cycle-16 · v3`), which the script reads out of the doc's header block (DS17) — this way the file name stays short while the PDF remains traceable. The script **never modifies** the source files: it makes a copy into the build folder and puts the YAML header on that.

**The chain:** `pandoc` + **`mermaid-filter`** + `xelatex`. `mermaid-filter` **pre-renders** the diagram with Chromium (`MERMAID_FILTER_FORMAT=pdf`), so the PDF engine receives finished vector graphics.

> **Why this chain — on the basis of measurement.** By default mermaid puts the labels into a `foreignObject`. Measured on an identical fixture (a sequenceDiagram + a flowchart): **WeasyPrint** with default settings **loses every label of the flowchart** (empty boxes — its own, partial SVG engine skips the `foreignObject`); with `htmlLabels: false` it is fixed. The **Chromium-based** routes are flawless: `xelatex` because `mermaid-filter` hands it already-rendered graphics, and **`pagedjs-cli`** because it is Chromium itself. So the decisive factor is **not** "LaTeX vs CSS" but the `foreignObject` — and since on the xelatex route the diagram is flawless by default, there is **no need** to rewrite `htmlLabels` (the mermaid blocks of the source stay untouched, and the PDF shows the same thing as the editor preview).

**Why `xelatex` is the default instead of `pagedjs`** (on the same 8–10 page test document):

| | xelatex | pagedjs-cli |
|---|---|---|
| Page count for the same content | **8** | 10 (+25%) |
| Blank page | none | **there is one** (page 2 has 0.0% ink) |
| Page number in the footer / in the TOC | yes / yes, with a dotted leader | no / no |
| Runtime | 16.8 s | 15.9 s |
| Dependency | pandoc + texlive (a system package) | + the npm-global `pagedjs-cli` (its own Chromium) |
| Its advantage | print-quality typesetting, dense page filling | **CSS-based formatting** — much easier to customise |

That is why the engine is a **parameter**, not a built-in decision: `--engine pagedjs` is a flag, in case you want to shape the look in CSS (in that case the script supplies the page number with an `@page` margin box).

**The key options of the script:** `--paper a3` (for wide sequence diagrams), `--engine xelatex|pagedjs`, `--check` (a dependency check only), `--dry-run` (what it would produce, with what version number), `--export-dir`, `--keep-build`.

**What the script solves beyond the chain** — without these, quality degrades with a manual `pandoc` call: an embedded `header.tex` (boxing code blocks with `tcolorbox`, breaking long paths with `fvextra`, `xurl`, accented characters), the **automatic scaling down of wide diagrams** to the text block (`max width=\linewidth`), `--resource-path` to the source folder (so that relative image references resolve from the build folder too), and `PUPPETEER_EXECUTABLE_PATH` pointing at the system browser, so that it does not download yet another Chromium.

**In case of an error:** on a missing dependency the script **stops** (exit code `2`) and prints the install command (`npm install -g mermaid-filter`) — it does not produce a PDF without mermaid rendering, because without the diagrams the doc is useless. On a pandoc error (`1`) it prints pandoc's stderr, `mermaid-filter.err` and the xelatex log, and **keeps the build folder** for debugging. Broken mermaid syntax is a **source defect of `docs-generated/`** — to be fixed in the `08-doc-sync` phase, not in the export.

**Hygiene:** `mermaid-filter` writes `mermaid-filter.err` into the cwd, so pandoc runs in the `export/.build/<name>/` folder — the project root does not get littered. On success the build folder is deleted. The **`export/` folder belongs in `.gitignore`**: the PDF is binary, it grows per cycle, and it can be regenerated at any time from the (version-controlled) `docs-generated/` — the skill offers this once, but only writes it in with approval.

---

## 11.3 test-runs/ — running tests outside a cycle (`/bs-run-tests`)

**When to use it.** When the question is not "is this cycle green" but **"does everything still work"**: an ad-hoc regression run after an environment change, running through a `unit` suite during a refactor, or checking whether the `rest-e2e` category reaches a freshly deployed component. The framework could **not** do this so far: `run-tests.py` mandatorily asked for a `plan.md` and a round folder, so every machine run was bound to **one cycle and one round**, and the request "run all the e2e tests" was pushed outside the framework, to manual commands — where not a single `EV` gate runs.

**What it runs from.** From the **project-level run table** of the `## Test execution` section of `conventions.md` (KT1), whose column schema is **identical** to the machine-readable run table of `plan.md` (TP4/b) — one parser, one rule. `00-init-project` fills it in with the user, together with the category dictionary (`unit` · `rest-e2e` · `ui`) and the per-category test file globs. The table of `plan.md` is **independent** of this and stays: that one is about one round of one cycle, this one about the project.

**Where it writes.** `test-runs/<category>/<YYYY-MM-DDTHH-MMZ>/<env>/` — a UTC timestamp without a colon (a valid folder name on Windows too), and the `<env>` segment is exactly `local` or `remote`. In the root of the run stands `results.json`, and in the root of `test-runs/` the `latest.json` (the path and the summary of the last run per category — **a file, not a symlink**). If the project has a test inventory, the result can be placed per item as well, in `<TL-NNN>/` subfolders — **this is the second benefit of the inventory**: the result of a central run is traceable per item. The folder is **gitignored**: it is machine-dependent and regenerable. It **never cleans up by itself** — `/bs-run-tests` prints its size in the closing message, and offers thinning only on an explicit request.

**🔴 And what matters most: this is NOT cycle evidence.** The evidence logic of the framework builds on a `DoD-NN`/`TS-NN` join, on TR7 freshness and on RUN1 round coverage — an out-of-cycle run has **nothing to join to**. That is why it is locked out at three levels: `run-tests.py` writes `"cycle": null` into `results.json` if the path is under `test-runs/`; `dod-check.py` and `report-gate-check.py` **reject** a path under `test-runs/` with `exit 2`; and the `06`/`07` skills state the same in prose as well. Without this the most obvious shortcut would be to run the central suite and point `dod-check.py` at it — the cycle would be green without the tests of the cycle having run. This is the `7/p` design principle: **evidence is bound to a cycle; a convenience run is not evidence.**

---
