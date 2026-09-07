<!--
  The PROJECT-LANGUAGE blocks of `run-tests` (the bs-run-tests helper command)
  (9.4 extraction, KT9/3).
  The installer inlines this file build-time at the place of the INCLUDE markers,
  according to the chosen PROJECT language (`PROJECT_LANG`); the form of the marker is
  `lang/run-tests.md#<anchor>`.
  The blocks got here VERBATIM — do not rephrase them, do not unify them.
  The ANCHOR lines are NOT part of the inlined text, they are only delimiters. The
  delimiter is an HTML comment and not a `##` heading because the templates themselves are
  full of `##` headings (8.9).
  ATTENTION: no comment-closing sequence may get into this leading note, and no
  INCLUDE marker may get into the file either (8.5).
-->

<!-- ANCHOR:nincs-szekcio-stop -->
*"There is no `## Test execution` section with a project-level run table in
`conventions.md`, so I cannot run a test outside a cycle: I do not know which categories
exist, and with which command I start each one. This is a mandatory section of the
`00-init-project` phase (KT1) — let us add it with `/bs-init-project`, or give me the
categories and the commands, and I will add the section into `conventions.md` after your confirmation."*

<!-- ANCHOR:kategoria-kerdes -->
*"Which test category should I run, and in which environment? The declared categories:
<the categories from the dictionary of conventions.md>. For a `remote` target I run the
reachability probe first. (You can also give it like this: `/bs-run-tests <category> <local|remote>`.)"*

<!-- ANCHOR:tuzfal-figyelmeztetes -->
> 🔴 **This run is NOT cycle evidence.** The result goes into the `test-runs/` tree, the
> `cycle` field of `results.json` is `null`, and the gates of `07-validate` (`dod-check.py`,
> `report-gate-check.py`) **reject** a path under `test-runs/` (`exit 2`).
> If cycle evidence is needed, the round of `06`/`07` has to be run, and that writes into
> the `test-report/<phase>/round-NN/` folder of the cycle.

<!-- ANCHOR:latest-json-vaz -->
{
  "<category>": {
    "path": "test-runs/<category>/<YYYY-MM-DDTHH-MMZ>/<env>",
    "env": "local | remote",
    "finished_at": "<YYYY-MM-DDTHH-MMZ>",
    "verdict": "PASS | FAIL",
    "passed": 0,
    "failed": 0,
    "skipped": 0
  }
}

<!-- ANCHOR:zaro-uzenet -->
> *"The test run is done — category: <category>, environment: <local|remote>.*
> - *Result: <N> ran / <N> failed / <N> skipped — VERDICT: <PASS|FAIL>*
> - *The skipped tests are NOT green: <the names of the skipped tests, or "none">*
> - *Run folder: `test-runs/<category>/<timestamp>/<env>/` · machine summary: `results.json`*
> - *Traceable per item: <the listing of the TL-NNN folders, or "no inventory mapping">*
> - *The size of the `test-runs/` folder now: <size>*
>
> *This run is not cycle evidence — the gate of `07` does not accept it."*
