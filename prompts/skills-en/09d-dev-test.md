---
phase: 09d
name: bs-dev-test
description: "berkispec - 09d. An OPTIONAL last phase (Phase 09d), only in centralized SDD, if the '## Review and merge' section of conventions.md says 'Dev deployment test: yes'. After a successful merge it deploys the product into a fully integrated dev/test environment, runs real e2e tests against it (VP3), and puts the evidence into the 'test-report/dev-test/' folder of the cycle."
prerequisites:
  - "The cycle is merged into the main branch (bs-merge has run)"
  - "conventions.md `## <sec:cv_review_and_merge>` — `Dev deployment test (bs-dev-test): yes` and `SDD mode: centralized`"
  - "conventions.md `Dev deployment command` — filled in"
output:
  - "specs/cycle-NN-<name>/test-report/dev-test/ — the evidence of the VP3 round (on success and on failure alike)"
  - "specs/cycle-NN-<name>/cycle-status.md — generated cycle status"
  - "specs/roadmap.md — the cycle closed (this is the last enabled verification)"
prev: bs-merge
next: bs-write-spec
scripts:
  - "scripts/run-tests.py — running the VP3 round (--phase dev-test)"
  - "scripts/report-gate-check.py — the report artifacts of the VP3 round (TR3)"
  - "scripts/test-manager.py — test manager upload (by default THIS is the phase, TM4)"
  - "scripts/notify.py — notification on failure (CS6)"
  - "scripts/cycle-status.py — the generated cycle-status.md (--write)"
---
# 09d — Dev test (VP3)
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

This is the **optional fourth step of the end of the cycle**, exclusively on the centralized path: 9a-create-pr · 9b-review · 9c-merge · **9d-dev-test ←**.

> **What it proves (VP3).** `07` (`VP1`) proved that functionally what was built is what the spec asked for; `VP2` proved that it also works merged with the main branch. `VP3` proves that everything also runs according to the spec **in a real, integrated environment** — after an automatic deployment, with production-like e2e tests. This is the point where the most valuable test information is produced.

> **Why only on the centralized path (`CS5`).** Deploying into an integrated dev environment presumes automation and central infrastructure. In isolated mode the validity rule of `00-init-project` **rejects** this combination.

---

## <field:f_prerequisite>

0. **Identifying the cycle:** the input is the folder of the cycle. In a machine run the adapter hands it over — do not ask back.

1. **`conventions.md` `## <sec:cv_review_and_merge>`:**
   - `Dev deployment test (bs-dev-test)` = `yes` — otherwise this phase does not run (say so and stop);
   - `SDD mode` = `centralized`;
   - `Dev deployment command` — **filled in**. If it is empty, **STOP**: without it the phase does not know what to deploy with (the validity rule of `00` catches this already at write time).

2. **Merge gate:** is the cycle merged into the main branch?
   ```bash
   git fetch origin
   git log --oneline origin/main --grep="cycle-NN" -1
   ```
   If the commit of the cycle is not on the main branch, **STOP** — run `bs-merge` first.

3. **Test selection:** is there a row with the `<status:phase_dev_test>` phase in the machine run table of `plan.md`? If there is none, **STOP + a question** (in a machine run `dev-test-questions.md` + `exit 2`): the phase is switched on, but the plan does not say **what** to run — this is a gap in the plan, not "nothing to do".

---

## Your task

1. **Opening the branch** on the path of the cycle (`L13-D7`).
2. **Deployment** with the `Dev deployment command`, and **proving** the deployment.
3. **`VP3` — a real e2e test round** against the deployed system, `--phase dev-test`.
4. **Evidence + test manager + closing.**

---

## 1. The branch — the report goes onto the PATH of the cycle (L13-D7)

The folder of the cycle (`specs/cycle-NN-<cycle-name>/`) lives on the **main branch** after the merge, on the same path — "back to the cycle" therefore does not mean the branch but the **path**. Since the cycle branch may already be deleted by then (or the main branch is protected), the vehicle is a **new branch from the main branch**:

```bash
git fetch origin
git switch -c feature/cycle-NN-<cycle-name>-dev-test origin/main
```

_The branch name follows the **<field:f_branch_naming>** strategy of the `## <sec:cv_git_conventions>` section of `conventions.md`, with a `-dev-test` suffix._

---

## 2. Deployment into the integrated environment

Run the command recorded in the `Dev deployment command` field of `conventions.md`, **verbatim**. The command belongs to the project, not to the framework — the detailed recipe (what it deploys, with what data, how it is rolled back) belongs into `specs/test-conventions.md` (TC1/c).

> **🔴 A green test does not prove WHERE it was green (`7/g`).** After the deployment and before the tests, **prove** that the deployed system is running and reachable: the `<field:f_prerequisite>` cell of the `<status:phase_dev_test>` rows of `plan.md` contains the reachability probe with the **target host** (EV4), and the command contains the target host **literally** (EV3). `localhost` / `127.0.0.1` without a declared port forward is **forbidden** (EV5) — `run-tests.py` catches this with `exit 4`, without running anything.

If the deployment fails: **this is not a test failure but an environment error** — a notification + `exit 1`, and the cycle stays in the `<status:waiting_for_verification>` state. Do not run tests against a system that never came up: a green result would mean nothing then.

---

## 3. `VP3` — the test round

<!-- INCLUDE:shared/python-cmd.md -->

### 3/a. Test manager preflight (TM4 — by default THIS phase uploads)

```bash
python3 <platform-scripts-mappa>/test-manager.py --mode preflight --phase dev-test \
  --round-dir specs/cycle-NN-<cycle-name>/test-report/dev-test
```

**The preflight runs BEFORE the test round, and it does not just look at the presence of the env var but at the LOADABILITY of the client** — a `reporter`-shaped client on a wrong runtime version can kill the whole test run, with zero tests executed. Without a token a complete e2e round would be wasted. `exit 3` = the phase is not on the list (skipped, not an error).

### 3/b. The tests

```bash
python3 <platform-scripts-mappa>/run-tests.py \
  specs/cycle-NN-<cycle-name>/plan.md \
  --round-dir specs/cycle-NN-<cycle-name>/test-report/dev-test \
  --phase <status:phase_dev_test>
```

### 3/c. Report gate and upload

```bash
python3 <platform-scripts-mappa>/report-gate-check.py \
  conventions.md specs/cycle-NN-<cycle-name> \
  --report-subdir test-report/dev-test

python3 <platform-scripts-mappa>/test-manager.py --mode publish --phase dev-test \
  --round-dir specs/cycle-NN-<cycle-name>/test-report/dev-test
```

- The last line of the output of `publish` is `TEST_MANAGER_RUN_URL=<url>` — this goes into the report, into the notification (`notify.py --run-url`) and into the generated `cycle-status.md`. On a failed round the developer is thus **one click away from the trace**.
- **The upload counts as done if and only if the run URL has appeared** (L13-D26): with a wrong token the client can finish green, with `exit 0`, while nothing has been uploaded. Without a URL a `test manager: FAILED (no run URL in the output)` line goes into the report.
- **The upload is not evidence** (TM7): the evidence of the cycle is the **committed** `test-report/dev-test/` set. The `**<field:f_test_manager_required>:**` value `yes` is what turns an upload error into a hard gate.

---

## 4. Closing

1. **Commit the evidence** onto the `-dev-test` branch and integrate it back according to the `## <sec:cv_merge_strategy>` section of `conventions.md` (a PR or a direct merge) — **the report written into the folder of the cycle has to get onto the main branch**, otherwise the evidence chain breaks.
2. **On a failure:**
   ```bash
   python3 <platform-scripts-mappa>/notify.py --phase dev-test \
     --cycle specs/cycle-NN-<cycle-name> --status fail --run-url "<the URL of the test manager>"
   ```
   The fix goes through the `## <sec:post_merge_fixes>` section of `tasks.md` (the machinery of `06`/`07` runs on it unchanged) — **not** a new cycle, but the continuation of the still open cycle. The explicit exception: if the failure does not belong to this cycle, a new cycle is started for it, and this cycle can be closed (L13-D8).
3. **After a green round this was the last enabled verification** — mark the cycle as closed in `specs/roadmap.md` (`✅`), and regenerate the status:
   ```bash
   python3 <platform-scripts-mappa>/cycle-status.py specs/cycle-NN-<cycle-name> --write
   ```
4. Tell the user that the cycle is closed:

<!-- INCLUDE:lang/09-merge.md#zaro-uzenet-dev-test -->
