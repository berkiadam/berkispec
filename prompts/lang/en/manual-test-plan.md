<!--
  The PROJECT-LANGUAGE blocks of `manual-test-plan` (the bs-manual-test-plan helper
  command) (9.4 extraction, MT12).
  The installer inlines this file build-time at the place of the INCLUDE markers,
  according to the chosen PROJECT language (`PROJECT_LANG`); the form of the marker is
  `lang/manual-test-plan.md#<anchor>`.
  The blocks got here VERBATIM — do not rephrase them, do not unify them.
  The ANCHOR lines are NOT part of the inlined text, they are only delimiters. The
  delimiter is an HTML comment and not a `##` heading because the document template
  itself is full of `##` headings (8.9).
  ATTENTION: no comment-closing sequence may get into this leading note, and no
  INCLUDE marker may get into the file either (8.5).
-->

<!-- ANCHOR:dokumentum-sablon -->

# Manual test plan — cycle-NN-<cycle-name>

**<field:f_status>:** <status:mtp_planned> | <status:mtp_as_built>
**<field:f_mode>:** <the reason of the mode choice in one line — e.g. "tasks.md = <status:ready_for_validate>">
**Source:** plan.md <sec:environment_coords> · spec.md <sec:definition_of_done> · conventions.md
**<field:f_last_updated>:** YYYY-MM-DD

> (only in <status:mtp_planned> mode) ⚠ The implementation has not been closed yet. The
> steps come from the plan, they are NOT verified on real code — on a difference the code wins.

## 1. <sec:mt_environment>

| Component | Port | Health endpoint | <field:f_startup> | <field:f_shutdown> |
|---|---|---|---|---|
| ... | ... | ... | `...` | `...` |

**<field:f_prerequisite>:** network and access prerequisites, startup order.

## 2. <sec:mt_test_data>

| Name | Value | Where it is created | <field:f_cleanup> |
|---|---|---|---|
| ... | ... | ... | ... |

This covers the test users with their passwords, the tokens and the way to obtain them, the
seed records, the identifiers and the scopes. The TC5 secret rule: a dev-scope value
concretely, but a cluster, registry, VPN, IAM or production credential **only as a pointer**.

## 3. <sec:mt_automated_tests>

| What it runs | Command | Where the result goes |
|---|---|---|
| ... | `...` | `...` |

**<field:f_test_results_so_far>:** <concrete paths, or "does not exist yet">

## 4. <sec:mt_manual_groups>

### TG-01 — <the name of the group>  (DoD-03, DoD-07)

**<field:f_what_we_test>:** <one or two sentences: what behavior this group proves>
**<field:f_prerequisite>:** <what has to be ready before the group>

| # | <field:f_steps> | Call / operation | <field:f_expected_result> |
|---|---|---|---|
| 1 | obtaining a token | `curl -s -X POST http://localhost:8080/auth/token -d '{"user":"tester"}'` | 200, the `access_token` field of the response is not empty |
| 2 | ... | ... | ... |

```http
POST http://localhost:8080/auth/token
Content-Type: application/json

{ "user": "tester", "password": "tester-dev" }
```

**<field:f_cleanup>:** <what has to be restored after the group>

### TG-02 — ...

### <sec:mt_not_manual>

| DoD-NN | Why it cannot be tested manually | What covers it |
|---|---|---|
| DoD-05 | ... | the `...` automated test / the Sonar gate |

## 5. <sec:mt_coverage>

| DoD-NN | Test group |
|---|---|
| DoD-03 | TG-01 |

## <sec:mt_changelog>

- **YYYY-MM-DD — <mode>:** <what it added / what it modified / what became stale and why>

<!-- ANCHOR:mod-tervezett-figyelmeztetes -->
> ⚠ **<status:mtp_planned> mode — the steps are NOT verified on real code.** The plan was
> made from the <sec:environment_coords> section of `plan.md` and from the
> <sec:test_specification> section of `spec.md`, the implementation has not been closed
> yet. On a difference **the code wins**; after the validation run this command again, and
> the plan is refreshed to <status:mtp_as_built> mode.

<!-- ANCHOR:analyze-kapu-stop -->
*"There is no analyze report in `PASS` state for this cycle, therefore the manual test plan
cannot be produced. This command builds on the filled-in <sec:environment_coords> section
of `plan.md` — that it stands there without placeholders, with concrete values, is
guaranteed by the mechanical gate of `05-analyze`. Run the analyze phase first: `/bs-analyze
input: @specs/cycle-NN-<cycle-name>` — then call this again."*

<!-- ANCHOR:quick-flow-kapu-stop -->
*"This cycle follows the simplified (quick-flow) flow — there is no `plan.md` and no
analyze phase — so the manual test plan starts from the status of `tasks.md`. The status
of `tasks.md` is currently neither `<status:ready_for_implement>` nor `<status:done>`, so
the task list is not approved yet: the plan would build on steps that may still change.
Close Phase 2 of `/bs-quick-flow` first (approval + status + commit), then call this
again."*

<!-- ANCHOR:mod-bejelentes -->
*"The manual test plan is produced in <mode> mode, because the status of `tasks.md` is:
<status>. If this is not right, give the mode as an input (`mode: planned` or
`mode: as-built`)."*

<!-- ANCHOR:ujrafutas-bejelentes -->
*"Refreshing an existing manual test plan — I keep the manual additions, I do not renumber
the existing `TG-NN` identifiers, and I write the change into the <sec:mt_changelog>
section."*

<!-- ANCHOR:zaro-uzenet -->
> *"The manual test plan is done — <mode> mode.*
> - *Test groups: <N> pieces (TG-01 … TG-NN)*
> - *Covered DoD items: <listing> · not manually testable: <listing or "none">*
> - *Gate: `manual-test-gate-check.py` → OK*
> - *Commit: <hash> — cycle-NN: manual-test-plan*
>
> *The plan: [manual-test-plan.md](./manual-test-plan.md)"*
