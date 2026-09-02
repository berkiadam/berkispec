<!--
  The PROJECT-LANGUAGE blocks of `quality-check-plan` (9.4 extraction).
  The installer inlines this file at build time in place of the INCLUDE markers,
  according to the chosen PROJECT language (`PROJECT_LANG`); the marker form is
  `lang/quality-check-plan.md#<anchor>`.
  The blocks were moved here VERBATIM — do not rephrase, do not unify.
  The ANCHOR lines are NOT part of the inlined text, they are delimiters only (8.9).
  CAUTION: no comment-closing sequence may appear in this leading note.
-->

<!-- ANCHOR:TP2-lezarasi-kapu -->
[ ] 1. The `Spec coverage` table is filled in: EVERY case of the spec
       `Test specification` and EVERY `DoD-NN` item maps to at least one plan
       test case (or appears with a justification). No row is left out.
[ ] 1/b. WY1 — A PURPOSE FOR EVERY ENTRY: EVERY `[P-…]` section of the
       `Planned changes` carries a `**<field:f_purpose>:**` line that states
       the behaviour true AFTER the change and the trouble it eliminates, and
       names the spec source (`DoD-NN` or requirement). There is no entry where
       the purpose merely repeats the change or is an empty generality.
[ ] 2. I PHYSICALLY copied in every affected recipe (RXX/IXX) of
       `specs/test-conventions.md` (commands, URLs, payloads, credential pointers)
       — I do not merely reference them. The plan is executable without
       test-conventions.md.
[ ] 3. Every integration and E2E test case contains, step by step: HTTP verb ·
       full endpoint · headers (with the TYPE of the Authorization) · concrete
       request body · expected HTTP status · key response fields. For browser E2E:
       interaction + network call + visible result.
[ ] 3/b. TS7 — SPEC TEST CASE → `TS-NN`: EVERY test case of the spec has been
       converted into a standalone `TS-NN` block in the `Test scenarios` section,
       and every row of the `Spec coverage` table names at least one `TS-NN`
       (or the justification of a case that cannot be tested). The heading
       structure of the test section of the spec has NOT been carried over as a
       parallel, self-named section.
[ ] 3/c. TA1 — TEST ARTIFACT DATA SHEET: under every `#### <test file path>`
       heading there stands the `<field:f_what_it_checks>` (what the file
       verifies — as a claim, with the `DoD-NN`), the `How to run` (framework +
       the command narrowed to this one file, runnable verbatim), the
       `Fixtures and test data` (with path and content — new files also in the
       `Planned changes`) and the `Test cases` (test function name →
       `TC-ID` / `TS-NN`) line.
[ ] 3/d. TD7 — EVERY TEST CASE SAYS WHAT IT VERIFIES: the
       `<field:f_what_we_test>` line of the `TS-NN` blocks, the
       `<field:f_what_it_checks>` column of the unit tables and every numbered
       integration/E2E flow states the behaviour as a CLAIM, with the `DoD-NN` —
       repeating the title ("concurrency test") is not a purpose.
[ ] 3/d/b. TI1 — TEST IDENTIFIERS: the scenarios run from `TS-01`, the cases of
       the test table from `TC-01`, continuously across the cycle, without gaps;
       there is no `TC-<module>-01` style numbering restarted per file. `tasks.md`
       and the log of 07 refer to these.
[ ] 3/e. TS8 — `.http` FORM: every `TS-NN` block containing a REST step also has
       a `.http` code block, with the same values as the `curl`, with full
       headers and body (the manual test plan assembles from this).
[ ] 3/f. PH1 — RUN PHASE: the `<field:f_phase>` column of the machine-readable
       run table has a valid value in every row (`<status:phase_implement>` /
       `<status:phase_validate>` / `<status:phase_both>`; an empty cell means
       both), and at least one category runs in the `<status:phase_validate>`
       phase. No test proving a `DoD-NN` is `<status:phase_implement>`-only.
[ ] 4. Every error branch states the HTTP status, the errorCode (where the error
       matrix of the spec defines it) and a sample of the response body.
[ ] 5. The test section contains no reference IN PLACE OF the steps: "following the
       pattern of cycle-XX", "as in the existing test", "according to the sequence
       diagram of the spec", "with the usual headers".
[ ] 6. The runnable entry point (script/test file) of every test case exists in the
       repo OR appears among the `Planned changes` as a new file, and the command
       of the `Verification strategy` calls exactly that.
[ ] 7. ENVIRONMENT PREPARATION (TP3): the plan contains, as verbatim commands, the
       token acquisition (user and S2S separately, if needed), the startup of the
       stack + health check + shutdown, the build–push–deploy–verify–rollback chain
       of the custom component (plugin/SPI/custom image), the seed and the network
       prerequisites — together with their execution order.
[ ] 7/b. KO1 — ENVIRONMENT COORDINATES: the `Environment coordinates` section
       exists and is complete: the base URL, port(s), health endpoint, verbatim
       start and stop command of EVERY component; an example of EVERY required
       REST call (verb · full URL · headers · concrete body · expected response ·
       extracted value), including the token acquisition; EVERY test and API user
       with its PASSWORD/credential (a dev-scoped value concretely, a cluster/
       registry/VPN/IAM/production credential as a pointer — TC5); every further
       parameter (identifiers, scope, client-id, namespace, timeout); the network
       and access prerequisites. There is no placeholder and no empty cell; where
       something is not applicable, `—` stands. The `C6` check of
       `analyze-gate-check.py` is 0.
[ ] 8. Whatever running the test requires but is present neither in
       `test-conventions.md` nor in this plan, I brought over from the plan of an
       EARLIER CYCLE (TP3/a, with the researcher subagent, with literal values and
       provenance) — or it became a `plan-questions.md` question. There is no
       silent prerequisite of the "we already did this in the previous cycle" kind.
[ ] 8/c. GC1 — GATE CONFIGURATION: if the cycle touches a gate-read convention
       (report artifact/path base, Sonar, test command, port, merge), the affected
       section of `conventions.md` is in the `Planned changes`, with concrete new
       content. `test-conventions.md` is not a substitute for it.
[ ] 8/b. KX3 — NO TRUNCATION: EVERY elaborated artifact of the spec (OpenAPI/JSON/
       YAML/SQL block, complete payload, error matrix, multi-step test scenario) is
       in the plan verbatim and complete. There is no merged step, no payload
       replaced by a list of field names, no "see the spec" reference. The affected
       section of the plan is not shorter than its source section in the spec.
[ ] 9. SCOPE GATE (SC1): the `Reverse coverage` table is filled in, with a `[P-…]`
       identifier in the first column (the coverage chain of 05 runs on this) —
       every plan capability has a spec source (requirement or DoD-NN), or an
       explicit Out of scope, or an open question. There is no capability without a
       spec source.
[ ] 10. ANCHOR VERIFICATION: I CONFIRMED with a Grep/Read command every concrete
       `file:location` / "this symbol is in this file" / "this assertion is in this
       test file" claim. There is no attribution written from memory or by analogy.
[ ] 11. VALUE SANITY: I went through EVERY concrete value of the plan — ports
       (80/443/8080/8443/6379/5432 typos: `433`, `44`, `8O80`), time unit (ms vs s),
       URL scheme ↔ port match (`https://` ↔ 443), version/tag, file path. Whatever
       looked suspicious, I checked against the source.
[ ] 12. SECTION ID (PID1): the title of every executable plan section bears a unique
       `[P-…]` identifier, and the IDs issued earlier are UNCHANGED (especially in
       fix mode: renaming an ID is forbidden, because tasks.md references it).
       Inventory and summary sections did NOT get an ID.
