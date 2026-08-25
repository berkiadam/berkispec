<!--
  The PROJECT-LANGUAGE blocks of `07-validate` (9.4 extraction).
  The installer inlines this file at build time in place of the INCLUDE markers,
  according to the chosen PROJECT language (`PROJECT_LANG`); the marker form is
  `lang/07-validate.md#<anchor>`.
  The blocks were moved here VERBATIM — do not rephrase, do not unify.
  The ANCHOR lines are NOT part of the inlined text, they are delimiters only (8.9).
  CAUTION: no comment-closing sequence may appear in this leading note.
-->

<!-- ANCHOR:validation-report-sablon -->
# Validation report — cycle-NN-<cycle-name>

**Current status:** in progress | PASS | FAIL (stopped) | escalated
**Number of rounds:** N
**Last updated:** YYYY-MM-DD HH:MM

_(You refresh this header at the end of every round — this is the only part you overwrite.)_

---

## Round 1 — YYYY-MM-DD HH:MM — FULL — FAIL

**Trigger:** first run of 07-validate | iteration N of the self-healing loop | confirming round | continuation of an interrupted run
**Report folder:** `test-report/validate/round-01/` _(TR5 — the evidence of the round; the number in the folder name = the number of the round)_

### Steps (in execution order)

| # | Time | Step | What it ran | Result |
|---|---|---|---|---|
| 1 | 10:32 | fast tests | `run-tests.py … --type gyors` | ✓ 43 passed / 0 failed / 0 skipped |
| 2 | 10:34 | Sonar Quality Gate (2/a) | `sonar-gate.py --out …/round-01/sonar-report.md` | ✓ exit 0 — QG PASS (MAJOR: 0, MINOR: 3) |
| 3 | 10:41 | code review (2/b, RV1) | `reviewer` subagent — diff `main…cycle-07` | ✗ 2 open `Must Fix` (MF-01, MF-02) |
| 4 | — | heavy tests | **skipped** — the static layer failed | — |
| 4b | — | E2E (optional row) | **skipped** — plan gap (TR4): the startup of Keycloak is not described | escalation to 03 |
| 5 | 10:42 | test report gate (TR3) | `report-gate-check.py conventions.md specs/cycle-NN-… --report-subdir test-report/validate/round-01` | ✓ exit 0 — `unit-report.html` (88 KB) |
| 6 | 10:42 | DoD check | `dod-check.py … --apply` | ✗ DoD-03 is not fulfilled |
| 7 | 10:43 | logging | `failure-counter.py --result FAIL --failed-item ...` | exit 0 — may continue |

### Failed items

- `MF-01` — `verifyToken()` does not handle the expired key _(1/3 consecutive, 1/5 total)_
- `MF-02` — … _(1/3, 1/5)_
- `DoD-03` — the `/verify` endpoint does not return a `correlationId` in the response _(1/3, 1/5)_

### Definition of done

| ID | Result | Justification |
|---|---|---|
| DoD-01 | ✓ | the token exchange returns 200 with the `<scope>` scope |
| DoD-03 | ✗ | the `correlationId` is missing from the response |

### Code review (RV1)

- **Ran:** yes (full round, the fast tests were green) | incrementally, only on the open `MF-NN`s (light round) | skipped — light round (VD10) | skipped — step 1 failed
- **Report:** `test-report/code-review.md` — 2 open `Must Fix`, 3 `Suggestion`
- **Open findings:** `MF-01` — `verifyToken()` does not handle the expired key; `MF-02` — …
- **Suggestion applied directly:** `S-02` (within scope, risk-free) — the next round tests it
- _(in case of a re-review: which findings were closed, and what stayed open)_

### Test reports (TR3 / TR5)
- **Round folder:** `test-report/validate/round-01/`
- `report-gate-check.py --report-subdir test-report/validate/round-01` → exit 0 / 1 / 2 — the list of the artifacts that got into the round folder, with their size (or: what is missing)
- _(in a light round: "gate skipped — light round (VD10)"; list the fast-test artifacts that were actually generated in this case as well)_

### Task completion
- Every task `[x]`: ✓ / ✗ (if ✗: the list of the unfinished tasks)

### Fix round (if any)

- **Fix tasks added:** T041 `[GREEN]` — …, T042 `[CHECK]` — … _(into the `## Validation fixes` section)_
- **`implement-fixer` started:** 10:45 — input: `DoD-03`; **`review-fixer` started:** 10:52 — input: `MF-01`, `MF-02` _(one batch, one VD3a gate — VD13)_
- **Feedback of the fixer:** 10:44 — "T041 closed: the rotation now happens in `refreshToken()`"; escalation signal: none
- **Contract integrity gate (VD3a):** ✓ clean — the `git diff` did not touch a test file / `spec.md` / the Sonar configuration
  _(or: ✗ — `auth.spec.ts` modified (assertion loosened) → restored with `git checkout --` → escalation)_

### Round verdict

FAIL → a new round starts after the fix. | PASS → the loop converged, statuses to `Done`. | STOP — [limit reached] → human decision. | Escalation to 03/02 — [justification].

---

## Round 2 — YYYY-MM-DD HH:MM — LIGHT — FAIL

_(the same structure; in the step table the rows of the heavy tests and of Sonar read "skipped — light round (VD10)")_

---

## Round 3 — YYYY-MM-DD HH:MM — FULL — PASS

_(confirming round: every step ran)_

---

## Overall summary

- **Final result:** PASS — after 3 rounds
- **Rounds:** 3 in total — of which 2 full, 1 light _(VD10 — a mandatory line for measurability)_
- **Re-run items:** `auth.spec.ts > refresh token rotation` (2 rounds), `DoD-03` (2 rounds)
- **Escalation / human intervention:** there was none
- **Temporary environment change:** [if there was a port swap: which one, and whether it was restored]

# Validation History
_(this section is written by failure-counter.py — you do not edit it by hand)_

<!-- ANCHOR:LC2-megallas-prefix -->
[VALIDATE · <Failed Item> · attempt 3/3]                 ← per-item limit
[VALIDATE · <Failed Item> · total failures 5/5]          ← per-item total limit
[VALIDATE · diverging loop · FAIL runs 5/5]              ← global backstop

<!-- ANCHOR:zaro-uzenet -->
4. Report: *"Validation succeeded. We can continue with step 8: documentation sync (08-doc-sync). Before starting the new phase, be sure to run a `/clear` command to empty the context, then use this command:*
   > ```
   > /bs-doc-sync input: @specs/cycle-NN-<cycle-name>
   > ```"*

<!-- ANCHOR:VD5-eszkalacio-uzenet -->
> **[VALIDATE · <Failed Item> · attempt N/3]**
> *"During validation, [Failed Item] turned out to be a design error: the code could only be green by changing the test or the Definition of done, which the loop must not do (anti-"test cheating"). Therefore I did not step back into 06-implement, but escalate to the design phase. I reset the status of [plan.md / spec.md] so that the design decision can be settled. Continue by reviewing the design:*
> ```
> /bs-write-plan (in case of a DoD error: /bs-write-spec) input: @specs/cycle-NN-<cycle-name>/plan.md (or spec.md)
> ```
> *After the design is settled, the process returns here along the 05→06→07 path."*
> **At the end of the answer: a clickable link to `validation-report.md`.**
