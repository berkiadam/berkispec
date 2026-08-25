---
phase: 00
name: bs-init-project
description: "berkispec - 00. Use at the very first start of the project (Phase 00), or if the root 'conventions.md' is missing/incomplete. Together with the developer it records the global project conventions (tech stack, test, development flow, git merge strategy) in 'conventions.md' — this is the prerequisite for every further phase."
prerequisites: []
output:
  - "conventions.md (project root)"
prev: null
next: bs-add-cycles
subagents:
  - "agents/researcher.md"
shared:
  - "shared/git-preflight.md"
---
# 00 — Project initialization
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

This prompt runs once, at the start of a new project. Its purpose is to record the project's conventions, which all further development cycles (02–09) will reference.

---

## Git preparation — init runs on its own branch (BD12)

The `00-init-project` **itself works on a feature branch** too, with the default name `feature/init-project`. **Chicken-and-egg order:** detect the *availability* of git right here, at the start; the formal recording of "is there (and will there be) version control" (BD11) happens further below, in the questions.

1. **Detecting git availability:** `git rev-parse --is-inside-work-tree` (or `git rev-parse --git-dir`).
   - **If there is no git / not a git repo** → **do not** create a branch, **do not** PR/merge. Continue directly with recording the conventions; the VCS question below (BD11) records the "NO VCS" flag into `conventions.md`.
   - **If git exists** → run the branch-opening preflight (below), then create and switch to the init branch:

<!-- INCLUDE:shared/git-preflight.md -->

2. **Creating the branch (git only):** after a fresh, clean `main`, `git switch -c feature/init-project`. From here on, init works on this branch (writing `conventions.md`, commit).
3. **Back-integration at the end of the run:** see "Closing" — according to the `## <sec:cv_merge_strategy>` recorded in `conventions.md` (BD7/BD15), PR or direct merge into `main`; if there is no decision/remote, the **default is direct merge** (BQ7).

---

## Your task

Create a `conventions.md` file in the project root according to the structure below. Fill in each section together with the developer — ask questions wherever the decision is not obvious. The technologies (e.g. Playwright, pytest) and settings appearing in the structure are **recommended defaults**; these must be customized based on the project's actual tech stack (e.g. Node/Jest, Go/go test, etc.).

For the sections below you **must actively ask** (it is not enough to just pre-fill):

- **Presence of version control (BD11 — GATE, first):** <!-- INCLUDE:lang/00-init-project.md#BD11-vcs-kerdes --> You already detected the *availability* of git in the "Git preparation" step; here you record the intent. If there **is none and will be none**, write into the `## <sec:cv_git_conventions>` section **explicitly**: <!-- INCLUDE:lang/00-init-project.md#BD11-nincs-vcs-flag --> This flag **gates** all git steps of 01 (and the other phases): in that case there is no `git switch -c`, no branch warning, no commit there — only the `specs/cycle-NN-<name>/` folder + roadmap is created.
- **<field:f_default_flow>:** ask about the nature of the tasks, and based on that record a default working mode: <!-- INCLUDE:lang/00-init-project.md#flow-kerdes --> Write the answer into the **<field:f_default_flow>** field of the `## <sec:cv_methodology>` section.
- **<sec:cv_test_framework>:** <!-- INCLUDE:lang/00-init-project.md#teszt-stack-kerdes -->
- **Test reporting (TR3 — MANDATORY question, after the test stack):** <!-- INCLUDE:lang/00-init-project.md#TR3-riport-kerdes --> Enter the answer into the **table** of the `## <sec:cv_test_reporting>` section (category / tool / command / artifact). **This section may not be left with a pre-filled default** — either real commands go into it, or the user explicitly states that there is no report generation, in which case the `**<field:f_report_required>:**` field is `no` + justification. If the tool can produce multiple formats, **recommend a single-file HTML** (the report goes into the cycle's git diff).
- **Merge strategy + back-integration (BD7/BD15):** ask about the git provider (GitHub / Bitbucket Cloud / Bitbucket Server / GitLab / Local), then **try out access** with the appropriate command (see the Merge strategy section). If the access test fails, **do not close `conventions.md`** — ask for the token / URL / permissions to be fixed, or for an alternative provider / local merge to be chosen. This is the **single source of truth** for how a finished branch gets back into `main` (PR or direct merge) — this is used by 09 (cycle merge), the 01/00 branch warning, and the back-integration of the 00 init branch too. If there is no decision/remote, the default is **direct merge** (BQ7). _(Only fill in the `## <sec:cv_merge_strategy>` section — do not introduce a new field.)_
- **Branch naming strategy (BD8 — only if there is VCS):** ask:
  - Does the branch name need to start with a **Jira ticket number**? (if yes: in what format)
  - Do feature branches start with a **`feature/` prefix**?
  - **Or** point to a document where these are clarified (we take the rule from there).
  Write the answer into the **<field:f_branch_naming>** field of `## <sec:cv_git_conventions>`. **Default** (if the user has no preference): `feature/cycle-NN-<name>` (the folder name is always without prefix, plainly `cycle-NN-<name>` — BD3). A small branching rule (prefix, Jira ticket) can go **verbatim** into `conventions.md`.
- **API policy / API design guideline (BD9):** <!-- INCLUDE:lang/00-init-project.md#BD9-api-guideline-kerdes --> The pointer goes into the `## <sec:cv_references>` section, so phases 02–03 can work from it.
- **Large external rule documents (BD10 — hybrid: pointer + excerpt):** if the user points to a **large** document (API guideline, extensive branching policy), do **NOT** put it into `conventions.md` with full text (every phase would pull it in → token bloat). Instead: **(a)** a pointer into `## <sec:cv_references>` (source path/URL + one-line description of what it governs); **(b)** have the `researcher` subagent (`agents/researcher.md`) read it in **once**, and have it produce a compact, normative **rule checklist** (concrete do/don't points), which goes into `conventions.md`. The deep/rare details are read on-demand by the consuming phase (branching → 01, API → 02–03) via the `researcher`. The pointer preserves the source, so the excerpt can be regenerated if the document changes.

Do not start a spec, plan, or implementation. This step only records the project's conventions.

---

## Context loading rules

- Only gather as much information about the project as is needed to fill in `conventions.md`.
- If the project already contains existing code and a deeper understanding of a component is needed, call the `researcher` subagent (`agents/researcher.md`, Mode B) — it returns only a summary, the raw file content does not enter the main context.

## Questioning rules

- Ask only **one** question at a time.
- If the user's answer opens up a further question, add it to the list.
- Keep iterating until every section is filled in.

## Stopping rules

- If the user's answer contradicts previously recorded conventions, point out the contradiction and ask for clarification.
- If the user chooses a technology you have no information about, point this out and ask them to provide a reference or documentation.

---

## conventions.md structure

```md
<!-- INCLUDE:lang/00-init-project.md#conventions-sablon -->
```

---

## Continuing after an interrupted run

If phase 00 was interrupted and continues in a new session:

```
1. Does conventions.md already exist?
   → Read it, and check which sections are filled in.
   → Continue from the first incomplete/empty section — do not start over.

2. Does conventions.md exist, but is incomplete (empty sections, unfilled Merge
   strategy, access validation not run)?
   → conventions.md is NOT considered done until every section is filled in
     AND the merge access validation has succeeded. Continue with the missing parts.

3. No conventions.md?
   → Start according to "Your task".
```

---

## Closing

> **The "done" marking of `conventions.md` is its mere existence** — there is no separate status field. Therefore the file may only be finally created (committed) once every section is filled in and the quality check has passed. Phases 01–08 afterward only perform an existence check.

### Quality check — before closing

Before closing, check:
1. Is every section filled in (no pre-fill placeholder left empty)?
2. Has the Test framework been agreed with the developer (not just left as the default without confirmation)?
2.a/b **Is the `**<field:f_artifact_path_base>:**` field filled in (TR5/b)?** — for a new project, `cycle-folder`. Without this, the `07-validate` TR3 gate stops with `exit 2`.
2.a **Is the `## <sec:cv_test_reporting>` section filled in with real data (TR3)?** — the table contains actual report-generating commands and artifact names, **or** the `**<field:f_report_required>:**` field is `no` + justification. A template placeholder (`<command>`, `<the chosen runner>`) may not remain: the `07-validate` gate reads this table, and with a placeholder every cycle would fail.
3. Is the Merge strategy filled in, and has the access validation **run successfully** (or has the developer explicitly chosen local merge)?
4. Do the ports, env variables and Sonar (if any) sections reflect the reality of the project?
5. Is the **<field:f_default_flow>** field of `## <sec:cv_methodology>` set to the value agreed with the developer (`full` or `simplified`), with no placeholder left?
6. **Is the VCS flag of `## <sec:cv_git_conventions>` set (BD11):** either git, or explicit "NO version control …"?
7. **Alongside VCS: is the Branch naming strategy field filled in (BD8)** (default `feature/cycle-NN-<name>`, or the organizational rule/pointer)?
8. **If the user pointed to an API design guideline / large policy (BD9/BD10):** is the pointer there in `## <sec:cv_references>`, and for a large document, the compact rule checklist produced with the `researcher`?

If any of these is not, complete it before closing.

### Commit, back-integration and notification

If the quality check has passed:

1. **Commit (VCS only) — on the `feature/init-project` branch** (BD12):
   ```bash
   git add conventions.md && git commit -m "cycle-NN: 00-init"
   ```
   _(Phase 00 is not cycle-specific; the `cycle-NN:` prefix refers to the first cycle — e.g. `cycle-01: 00-init`.)_
2. **Back-integration into `main` (VCS only) — according to `## <sec:cv_merge_strategy>` (BD7/BD12):** based on the provider recorded in the section, **submit a PR** or **direct merge** into `main`; if there is no explicit decision/remote, the default is **direct merge** (BQ7). Before a destructive step (merge/branch deletion), ask for user confirmation.
3. **No-VCS branch (BD11):** if according to `conventions.md` there is no version control, steps 1–2 are skipped — the mere existence of the `conventions.md` file is the "done" marking, without branch/commit/merge.
4. Notify the user:

<!-- INCLUDE:lang/00-init-project.md#zaro-uzenet -->
