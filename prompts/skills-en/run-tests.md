---
name: bs-run-tests
description: "berkispec - helper command. Running tests OUTSIDE A CYCLE, per category: it runs run-tests.py from the project-level table of the 'Test execution' section of conventions.md, and writes the result into the gitignored 'test-runs/<category>/<UTC-timestamp>/<env>/' tree. Prerequisite: the 'Test execution' section of conventions.md filled in (written by 00-init-project). Not a phase: it is not part of the 00-09 process, it does not change a cycle status, it can be re-run any time — and its result is NEVER cycle evidence."
prerequisites:
  - "conventions.md → the ## <sec:cv_test_execution> section (<field:f_test_categories>, the project-level run table, the test file locations)"
output:
  - "test-runs/<category>/<YYYY-MM-DDTHH-MMZ>/<env>/ — the folder of the run, with results.json and the report artifacts in it"
  - "test-runs/latest.json — the path and the summary of the last run per category"
scripts:
  - "scripts/run-tests.py --table-source conventions — the runner"
shared:
  - "shared/python-cmd.md"
---
# Running tests outside a cycle (`bs-run-tests`) — a helper command
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

This is **not a phase:** it is not part of the `00–09` chain, it does **not touch** the status chain of the cycle (`spec.md` / `plan.md` / `tasks.md`), it does **not write** a cycle artifact, it runs without a subagent, and it can be re-run any time. It does one single thing: it runs **one test category** of the project from the project-level run table, and writes the result into an **out-of-cycle, gitignored** tree.

**Why it is needed:** so far every machine run of the framework was bound to **one cycle and one round** (`run-tests.py` asked for a `plan.md` and a `--round-dir`). The request "run all the e2e tests" was thus pushed **outside** the framework: by hand, without evidence. This command brings it inside the framework — **but not into the evidence logic**.

> 🔴 **The most important rule you have to state (D8):** the result produced here is **NEVER cycle evidence**. A run under `test-runs/` has no `DoD-NN`/`TS-NN` join, no round number, so neither the TR7 freshness nor the RUN1 round coverage is interpretable for it. `dod-check.py` and `report-gate-check.py` **reject** a path under `test-runs/` with `exit 2` — do not try to work around this.

---

## Cheat sheet

| Section | In one sentence |
|---|---|
| The prerequisite (KT1) | The `## <sec:cv_test_execution>` section of `conventions.md` filled in. Without it **STOP** — this is a gap of `00-init-project`, not yours. |
| The entry (KT4) | `/bs-run-tests` (ask), `/bs-run-tests <category>`, `/bs-run-tests <category> <local\|remote>`. |
| Not a phase (D10) | It does not change a status, does not write a cycle artifact, runs without a subagent, does not touch the `00`–`09` chain. |
| The output (KT5) | `test-runs/<category>/<UTC-timestamp>/<env>/` + `test-runs/latest.json`. You write **nowhere** else. |
| The firewall (D8) | The result is not cycle evidence; the gates of `07` reject it. **You state this in the closing message.** |
| The inventory join (KT5) | The `<TL-NNN>` path segment joins the result to the test inventory — traceable per item. |
| Cleanup (D12) | `test-runs/` **never cleans up by itself**; you print its size, and you offer thinning only on an explicit request. |

---

## <field:f_prerequisite>

1. **Reading `conventions.md`.** Read the `## <sec:cv_test_execution>` section of `conventions.md` in the root of the project — **only this section**, not the whole file. What is needed from it: the `**<field:f_test_categories>:**` dictionary, the **project-level run table** and the `### Test file locations` table.

2. **🔴 The entry gate.** If `conventions.md` does not exist, or there is no `## <sec:cv_test_execution>` section with a run table in it, **STOP** — do not guess a command, and do not run a "likely" test command:

   <!-- INCLUDE:lang/run-tests.md#nincs-szekcio-stop -->

   This section is a **mandatory** part of `00-init-project` (KT1). Adding it is the business of the `00` phase; if the user wants to give it here, write it into `conventions.md` **only after their confirmation**, and **only this one section**.

3. **Choosing the category and the environment.** If the call gave it (`/bs-run-tests rest-e2e remote`), use that. If not, **ask once**, and wait for the answer:

   <!-- INCLUDE:lang/run-tests.md#kategoria-kerdes -->

   The given category has to be one of the elements of the `**<field:f_test_categories>:**` dictionary. If it is not, list the declared categories and ask again — **do not run** an undeclared category.

---

## The course of the run

1. **Selecting the rows of the category.** Those rows of the run table whose `<field:f_test_category>` cell is the requested category and whose `<field:f_environment>` cell matches the requested environment. If the category has no row in the requested environment, state it in one line, and **do not run** another environment instead.

2. **A `remote` target: the probe runs FIRST (EV4).** The `Prerequisite` cell of the row contains the reachability probe. `run-tests.py` runs it on its own, but if the probe fails, the category becomes `FAIL` — in that case **do not blindly re-run it**: in the closing message state that the target is not reachable, and that the test result is therefore not interpretable.

3. **The timestamp and the folder (KT5, D11).** Produce a **UTC** timestamp in the `YYYY-MM-DDTHH-MMZ` form (sortable, without a colon — a valid folder name on Windows too), and from that the round folder:

   ```
   test-runs/<category>/<YYYY-MM-DDTHH-MMZ>/<env>/
   ```

   The value of the `<env>` segment is exactly `local` or `remote` — a **language-independent literal** (EV8), the same one that the `<field:f_environment>` field of the test inventory uses.

4. **Calling the runner.** The `--table-source conventions` tells the script to read the table from `conventions.md` (the `plan.md` positional argument can then be omitted):

   <!-- INCLUDE:shared/python-cmd.md -->

   ```bash
   python3 <platform-scripts-folder>/run-tests.py \
     --table-source conventions \
     --conventions conventions.md \
     --round-dir test-runs/<category>/<YYYY-MM-DDTHH-MMZ>/<env> \
     --only <category>
   ```

   The default of `--json` is the `results.json` of the round folder — do **not** override it. The script writes `"cycle": null` into `results.json`, because the path is under `test-runs/` (KT6/a).

> **Test manager (optional, TM4) — an out-of-cycle run may upload too.** If the `**<field:f_test_manager_phases>:**` field of the `## <sec:cv_test_reporting>` section of `conventions.md` lists the `ad-hoc` value, `--mode preflight` runs **before** and `--mode publish` **after** the run (`test-manager.py --phase ad-hoc --round-dir <the run folder>`). **This does NOT bypass the evidence firewall (D8/KT6):** the metadata of the upload carries `cycle=none`, so a convenience run stays distinguishable from cycle evidence at the provider as well. For trend and flaky data this is exactly the most valuable source.

5. **The exit codes — what they mean here:** `0` = every run category is green · `1` = at least one category failed (or ran 0 tests — TR2) · `2` = there is no table or the category is unknown → **STOP**, with adding `conventions.md` · `3` = a placeholder error in the table → **STOP**, `conventions.md` has to be fixed · `4` = the table is environment-broken: a non-local category points to a local target (EV5) → **NOT runnable**, because a green result would then not be about the deployed component.

6. **The inventory join (KT5).** If the `docs-generated/test-description.md` test inventory exists in the project, place the result of the run **per item** as well: inside the round folder, into a `<TL-NNN>/` subfolder the report artifact belonging to that item. **This is the second benefit of the inventory**: the result of a central run is traceable per item. If a run test **cannot be mapped** to a `TL-NNN`, it goes under `unmapped/<test-name>/`, and you flag it in the closing message — this signals a gap of the `LD5` gate, so it is a task for the next `08-doc-sync`. **Do NOT touch the inventory itself** (its owner is `08`, LD1).

7. **Updating `test-runs/latest.json`.** The path and the summary of the **last** run per category. The file stands in the root of `test-runs/`, and it is a **file, not a symlink** (D11 — a symlink requires a separate right on Windows):

   ```json
   <!-- INCLUDE:lang/run-tests.md#latest-json-vaz -->
   ```

   Rewrite only the key of the category just run; **leave** the entries of the other categories **untouched**.

---

## Retention and cleanup (D12)

- `test-runs/` **never cleans up by itself.** The cleanup safety rule of the framework applies here too: **only an element created by the current run** may be deleted.
- In the closing message **print the total size of the `test-runs/` folder** (e.g. `du -sh test-runs/`).
- **Offer thinning only on an explicit request**, and even then item by item: which runs of which category with which timestamp you would delete, and how much space it frees. Without asking you may **not delete a single earlier run**.
- The folder is **gitignored** (KT7): the results are machine-dependent and can be regenerated, therefore we do not version them. If the `test-runs/` entry is missing from `.gitignore`, **state it in one line** — adding it is the business of `00-init-project`, do not write into it on your own.

---

## The evidence firewall (D8) — stated

<!-- INCLUDE:lang/run-tests.md#tuzfal-figyelmeztetes -->

**Why:** the evidence logic of the framework builds on a `DoD-NN`/`TS-NN` join, on TR7 freshness and on RUN1 round coverage — an out-of-cycle run has **nothing to join to**. Without this the most obvious shortcut would be to run the central suite and point `dod-check.py` at it: the cycle would be green without the tests of the cycle having run.

---

## The closing feedback

The PE1 part of the common block (the phase boundary + the command of the next phase) is **not interpreted** here: this is not a phase, there is no "next phase". The command ends with the closing message:

<!-- INCLUDE:lang/run-tests.md#zaro-uzenet -->

> **`<status:skipped>` is NOT green (SK1).** List the skipped tests **item by item** — an "everything is green" summary with twenty skipped tests behind it is worse than an open failure.

---

## Stopping rules

1. **There is no `## <sec:cv_test_execution>` section** (the prerequisite 2.) → STOP, directing towards `/bs-init-project`.
2. **An undeclared category was requested** → list the declared ones, and ask again. Do not run something "similar" instead.
3. **The script gives an exit code of `2`, `3` or `4`** → STOP, with the output of the script. In the case of `4` (the EV5 environment error) **especially**: a green result would then not be about the deployed component.
4. **The user wants to use the result as cycle evidence** → state once that the gates of `07` reject this, and direct them towards `/bs-validate`. Do not work around the gate, and do not copy the files into the `test-report/` folder of a cycle.

---

## What NOT to do

- **Do not write into the `test-report/` folder of the cycle** and do not copy anything there from `test-runs/` (D8).
- **Do not touch the status chain of the cycle** (`spec.md` / `plan.md` / `tasks.md`) or the artifacts of `06`/`07`/`08`/`09`.
- **Do not write the `docs-generated/test-description.md` test inventory** — its owner is `08-doc-sync` (LD1). A test that cannot be matched to a `TL-NNN` you only **flag**.
- **Do not edit `conventions.md`** without the explicit confirmation of the user, and even then **only** the `## <sec:cv_test_execution>` section.
- **Do not guess a command.** If the table gives no command for a category, that is a gap of `conventions.md` — a question, not improvisation.
- **Do not delete an earlier run** without asking (D12).
