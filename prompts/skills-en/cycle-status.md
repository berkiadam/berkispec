---
name: bs-cycle-status
description: "berkispec - helper command. Checking the status of the cycles. It lists the cycles of the project (Done/In progress), and shows the progress of their phases in detail on an interactive TUI or when given as an argument (DONE, DONE*, IN PROGRESS, NOT RUN YET). It is not a phase: it is not part of the 00-09 process, it can be called at any time."
output: []
---
# Cycle status checker
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

This command allows you to quickly and interactively check the status of all cycles in the project. It can recognize both the Full (00-09) flow and the shortened Lightweight flow, and displays the progress phase by phase.

## Usage Guide

The command can be used in two ways:

1. **Interactive (without a parameter)**:
   If the user does not provide a parameter when calling the command, the agent starts the interactive TUI (Terminal User Interface) application, where you can navigate between the unfinished cycles with the UP/DOWN arrows, and the list of the given cycle's phases updates dynamically on the right side. Pressing ENTER exits the TUI and prints the status of the selected cycle in detail.

2. **Direct (specifying a specific cycle)**:
   A specific cycle folder name can be given (e.g. `cycle-01-oidc-login` or the full path: `specs/cycle-01-oidc-login`). In this case, the TUI does not start, and the agent immediately prints the statuses of the given cycle.

---

## Your task when running as an agent

1. **Reading the parameter**:
   - Check whether the user provided a specific cycle or path as input when starting the command (e.g. `specs/cycle-01-...` or just `cycle-01-...`).

2. **Running the script**:
   - Determine the location of the platform-specific runner script relative to the project root:
     - For **Google Antigravity CLI**: `.agents/scripts/cycle-status.py`
     - For **Claude Code**: `.claude/scripts/cycle-status.py`
     - For **Cursor**: `.cursor/scripts/cycle-status.py`
     - For **GitHub Copilot**: `.github/scripts/cycle-status.py`
     - For **Codex CLI**: `.codex/scripts/cycle-status.py`

   - **If the user specified a cycle (e.g. `specs/cycle-01-oidc-login`)**:
     Run the script with the given argument:
     > **Python command (platform-dependent):** the examples use `python3` (Linux/macOS). On **Windows** `python3` often does not exist — or it is the Microsoft Store stub, which opens the Store —, so there the correct call is `python` or `py -3`. If `python3` gives a "command not found" / "not recognized" error, **try again with `python`, then with `py -3`**, using the same parameters. This is not a bug in the script, and it is not a reason to stop.

     ```bash
     python3 <platform-script-path> <input-parameter>
     ```

   - **If the user did NOT specify a parameter (called it empty)**:
     Run the script in interactive mode (the agent requests approval from the user to run the command):
     ```bash
     python3 <platform-script-path>
     ```

   - **If the user asks for the generated status file (`--write`)**:
     ```bash
     python3 <platform-script-path> specs/cycle-NN-<cycle-name> --write
     ```
     The script writes `cycle-status.md` into the root of the folder of the cycle, and prints the usual output as well.

3. **Displaying the output**:
   - Show the result of the run to the user in the chat.

---

## The generated `cycle-status.md` (`--write`)

The `--write` mode generates the `specs/cycle-NN-<cycle-name>/cycle-status.md` file into the root of the folder of the cycle: what has run, what is left, and an overall status.

- **🔴 A generated file, not hand-written.** A rendering of the evidence, **never a source** — and **no gate ever reads it**. The framework keeps two things strictly apart: a **decision** has to be persisted (it cannot be derived), while a **fact** has to be derived from the evidence, never from self-reporting. "What has run" is the second category: if the agent wrote `VP2: PASS` into it by hand, a self-reporting evidence channel would open next to `report-gate-check.py`. **A lying status file is worse than none** — so do not edit it by hand, and do not "fix" reality into it.
- **When it refreshes by itself:** at every **phase-closing commit** (it is part of the shared `phase-commit` procedure), so it never stands stale. Beyond that, the manual `--write` call works at any time.
- **It is committed:** on the PR and on the centralized path this is the only place where a human sees where the cycle stands **even next to a machine run**. On a conflict it does not have to be resolved: it can simply be regenerated.
- **What else it shows:** based on the `## <sec:cv_review_and_merge>` section of `conventions.md`, the post-merge verification points as well (`VP2` post-merge, `VP3` dev test) — only those the project has switched on — and, if the report of the round carries it, the test manager run URL as a pointer.
