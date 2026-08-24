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

3. **Displaying the output**:
   - Show the result of the run to the user in the chat.
