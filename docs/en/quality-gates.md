# Quality gates, decision log and review

← [Back to the main page](../../README.md) · [Page index](README.md)

## 14. Sonar quality check

The validate phase (07) — if `conventions.md` contains a `## Sonar quality check` section — runs a Podman-based SonarQube analysis.

**The process:**
1. Starting the SonarQube server (if it is not running yet).
2. Running the scanner as specified in `conventions.md` (with the project's test-tooling script).
3. The reports go into the folder of the **current validation round** (`test-report/validate/round-NN/sonar-report.md` + `.html`); a Quality Gate FAIL stops with a non-zero status.
4. **The evaluation of the Quality Gate is deterministic — it is done by `sonar-gate.py` from the Sonar Web API** (`/api/qualitygates/project_status` + `/api/issues/search`), not by reading the report with an LLM. The exit code decides:
   - **`0`** — QG OK (the `MINOR`/`INFO` hits do not block);
   - **`1`** — QG FAIL **because of a finding**: the printed `BLOCKER`/`CRITICAL`/`MAJOR` list in `file:line + message` form is the source of the fix tasks (the severity filtering has already happened);
   - **`3`** — QG FAIL **because of a threshold, without a blocking finding** (QG1): the script names the failed condition (e.g. `new_coverage: 71.2 (threshold: < 80)`). In that case **starting a fixer with an empty defect list is forbidden** — either a concrete coverage task is created, or STOP + human;
   - **`2`** — a usage error (a missing URL/projectKey/token) → Sonar then runs through the `test-runner` subagent, the old way.

   With the `--out` switch the script also generates the `sonar-report.md` evidence into the round folder (TR3).

   > **⚠ The Quality Gate typically measures ONLY the new code.** The gate can be `OK` even next to a legacy `BLOCKER` (or one coming from a first analysis without a baseline) — verified on a live SonarQube. If the project wants to close this gap, with the `--fail-on BLOCKER` (or `BLOCKER,CRITICAL`) switch the script gives a FAIL even with a green gate. **Deliberately opt-in:** switched on in an old codebase, the loop would start producing fix tasks for legacy findings outside the scope of the cycle.
5. **PASS:** the validation continues. **FAIL:** the defects go into `validation-report.md`, the status of `tasks.md` changes to `Ready for implementation [validate-loop]`, and the **07 self-healing loop** starts the `implement-fixer` subagent (06 fix mode) to fix the Sonar defects, and then re-validates — up to the 3-attempt limit (see "The validation log").

**Detecting modifications (SCM & Git Blame):** SonarQube uses the `.git` SCM and Git Blame data, and separates the **New Issues** from the legacy ones relative to the main branch (a git diff). The Quality Gate applies only to the newly modified lines.

---

## 15. The decision log (imp-decision.md)

`imp-decision.md` is the log of the hard decisions and dead ends of the implement phase (06) (`specs/cycle-NN-<cycle-name>/imp-decision.md`). If solving a task required at least 3 unsuccessful attempts:
```md
## T0XX — <short title>

**What the trouble was:** <a concise description of the defect>
**What we tried:** <the unsuccessful attempts in brief>
**What the solution turned out to be:** <the approach that finally worked>
```

---

## 16. The validation report (validation-report.md)

`test-report/validation-report.md` tracks the runs, SonarQube results and test failures of the validate phase (07). **The file is not written by hand by the orchestrator:** the `## Round N` blocks are opened (`open`), filled (`step`) and closed (`close`) by `round-log.py` — including the creation of the `round-NN/` folder with the same serial number — and the `# Validation History` by `failure-counter.py`. The orchestrator only adds the free-text fields (the verdict of the round, the DoD justification). Consecutive failures are counted per item by the `failure-counter.py` script (deterministically, not by the agent by hand) — it appends the entries in the following format:

```md
# Validation History

- **Run 1 (2025-01-15 10:30) - FAIL**
  - **Failed Item:** TokenExchangeService › should return 403 for invalid token
  - **Consecutive Failures for this item:** 1
  - **Details:** NullPointerException during the JWE decoding

- **Run 3 (2025-01-15 14:20) - PASS**
```

**Stopping limits:** `failure-counter.py` stops with `exit 3` if an item reaches **3 consecutive** or **5 total** failures, or if the loop still has not converged after **5 consecutive FAIL runs** (a stuck code bug → STOP + human; a design defect → escalation to 03/02). **One validation round = one `Run` entry** — logging a partial result is forbidden, because an interposed PASS would break the failure chain.

**The file is not just a log, but a full report (VD9):** above the `# Validation History` there is one `## Round N` block per round — the execution order with timestamps (what ran, what was left out and why), the evidence of the `test-runner` (the command + `X passed / Y failed / Z skipped`), the result of the **test report gate (TR3)**, the `DoD-NN` table, the trace of the fixing round (tasks → fixer → the VD3a contract gate) and the verdict of the round; and at the end, an `## Overall summary` with the re-run items. The full mechanics of the loop are described in section 4.5.

**The `test-report/` folder belongs to the reports too — broken down per round (TR5):** the artifacts declared in the `## Test reporting` table of `conventions.md` (Allure/Playwright HTML, coverage, JUnit XML) go here in every cycle, and are part of the cycle's git diff. Not into the root, but into **a separate subfolder per round**, so that the evidence of every round of a self-healing loop is preserved — this way the report belonging to a failure indicated in the step table of `validation-report.md` can be opened:

```
specs/cycle-NN-<name>/test-report/
├── validation-report.md        # the log of 07 — spanning several rounds, append-only
├── implement/
│   └── check-log.md            # the log of the [CHECK] runs of 06 (command, attempt, counts)
└── validate/
    ├── round-01/               # every artifact of the 1st validation round (+ sonar-report.md/.html)
    └── round-02/               # those of the 2nd — it never overwrites those of the 1st
```

The number in the folder name **must match** the serial number of the `## Round N` in `validation-report.md`. The gate of `report-gate-check.py` checks the folder of the given round with the `--report-subdir test-report/validate/round-NN` switch — **mandatorily in a full round, not in a light one** (in a light round not every test category runs deliberately, so the full report table cannot be satisfied either). The folders of the rounds are never deleted: those of the failed rounds are the most valuable for tracking down a defect.

---

## 17. The reviewer agent (agents/reviewer.md)

**When it is called:** by the **07 — Validation and code review** phase, as **step 2** of the validation round (RV1) — one half of the "static layer", next to the Sonar Quality Gate. It runs exclusively in a **full** round (in a light round only incrementally, on the open `MF-NN`s), and only if the **fast tests** (unit/typecheck) are green; at that point the heavy tests (E2E/regression) have **not yet run**. It does not start alongside a failing fast test: the code cannot even be compiled. The rationale for the order (VD13): fixing review findings changes the code, so it is cheaper to review first and to spend the E2E stack only on a review-clean diff.

**What it does:** as a Task tool subagent it reviews the changes of the cycle branch (a git diff against the main branch), and produces a structured, **machine-parseable** report:
- **Critical fixes (Must Fix)** — blocking; in the form `- [ ] **MF-NN** — <file>:<line> — <description>`. `MF-NN` is a **stable identifier**: this is what the orchestrator uses to step the per-item stopping counter, so it must not be renumbered at a re-review.
- **Suggested improvements (Suggestions)** — non-blocking, with an `S-NN` identifier.

**Output:** `specs/cycle-NN-<cycle-name>/test-report/code-review.md`. **It writes no log:** the history of the loop, the attempt counters and the stopping limits live in `# Validation History` in `validation-report.md`, on a counter **shared** with the test failures.

**The criteria list lives in a shared block, and the fallback branch gets it too (RV-FB1).** The `## Review criteria` section and the `Must Fix` vs `Suggestion` dividing line live in a single copy in `prompts/shared-en/review-checklist.md`, and the installer inlines it into **two** places: the prompt of the `reviewer` **and** the reviewer-fallback block of `07`. By definition the fallback does not read the subagent's prompt — without this the review there falls back to a "look through the diff" level, which is exactly what happened in a live cycle. The **decidable question about an empty test body** (`TB1`) went into this list as well: a new or modified test function in the diff with no assertion → `Must Fix`.

The `reviewer` is a **read-only diagnostician** (like the `analyzer`): it only writes the report, it performs no correction and it does not ask. The correction is done by the `review-fixer` (= 06 fix mode), and the orchestration by the 07 orchestrator.

**The feedback loop:**
- **Must Fix** → the **FAIL of the round** (not a separate loop): the findings go among the `## Review fixes` tasks under the name `MF-NN`, the `review-fixer` fixes them, and then a light round + a mandatory full confirming round follow, **with a re-review**. For the detailed mechanics see [section 4.5](self-healing-loops.md).
- **Suggestion** → does not block; the orchestrator only fixes it directly if it stays within scope and is risk-free (the next round will test it anyway).
- **No Must Fix + green tests** → the validation is a PASS, onwards to `08-doc-sync`.

---
