---
name: bs-export-doc
description: "berkispec - helper command. Creates a versioned PDF from markdown documents (together with mermaid diagrams) into the 'export/' folder at the project root. Without a parameter, from the 'docs-generated/architecture.md' and 'system-overview.md' files, otherwise from the named file(s). The version number is independent per file: the last + 1, starting from v1."
output:
  - "export/<name>-v<N>.pdf (independent version number per file)"
---
# Export doc — versioned PDF from markdown documents
<!-- INCLUDE:lang/output-language.md#output-language -->

This is **not a phase**, but a helper command: it can be run at any time, has no prerequisite and does not change the cycle's state. The actual work is done by the `export-doc.py` script — your job is to decide **what** the PDF should be created from, then call the script and report back the result.

---

## What it does

- **Without a parameter:** creates one PDF each from the two mandatory generated documents:
  - `docs-generated/architecture.md` → `export/architecture-v<N>.pdf`
  - `docs-generated/system-overview.md` → `export/system-overview-v<N>.pdf`
- **With a parameter:** from the named file(s) — if the user asks "this one too", then from the two defaults **and** the named ones.
- **Version number:** **independent** per file — the maximum of the `<name>-v<N>.pdf` files in the `export/` folder + 1, `v1` for an empty folder. The script calculates this, **don't calculate it yourself**.
- The **cycle** does not go into the filename, but onto the PDF's **title page** (`<field:f_covered>: up to cycle-NN · v3`) — the script reads it from the document's header block.
- It **never modifies** the source files (the owner of `docs-generated/` is `08-doc-sync`).

---

## Your task

### 1. Resolving the input

Look at what the user specified when calling the command:

| The user writes… | What you pass to the script |
|---|---|
| nothing | **no file argument** (the script uses the two defaults) |
| specific file(s) (e.g. `@docs-generated/architecture.md`) | exactly those |
| "the specs too", "the cycle-16 plan" — **free text** | resolve it to concrete file paths, and **before including it, list for the user what you are going to export** |
| "everything", "all the docs" | don't guess: ask which folder/files they mean (all of `docs-generated/`, or `specs/` too?) |

**If a named file does not exist**, don't substitute another one on your own — flag it and ask.

### 2. Running the script

Determine the platform-specific script location relative to the project root:

- **Claude Code:** `.claude/scripts/export-doc.py`
- **Google Antigravity CLI:** `.agents/scripts/export-doc.py`
- **Codex CLI:** `.codex/scripts/export-doc.py`
- **Cursor:** `.cursor/scripts/export-doc.py`
- **GitHub Copilot:** `.github/scripts/export-doc.py`

<!-- INCLUDE:shared/python-cmd.md -->

```bash
# without a parameter (the two default docs)
python3 <platform-script-path>

# from specific file(s)
python3 <platform-script-path> docs-generated/architecture.md specs/cycle-16-oidc/plan.md
```

**Options** (only specify if the user asks or the situation warrants it):

| Option | When |
|---|---|
| `--paper a3` | if a diagram would become unreadably small on A4 (wide sequence diagrams) |
| `--engine pagedjs` | if the user requests CSS-based formatting. **Default `xelatex`** — this gives a page-numbered table of contents and tighter layout; pagedjs lays out more loosely and tends to insert blank pages |
| `--check` | only checks the dependencies (pandoc, mermaid-filter, xelatex + LaTeX packages), does not export |
| `--dry-run` | prints which files would produce which version-numbered PDF — does not run pandoc |
| `--export-dir <folder>` | if the user wants it somewhere other than `export/` |
| `--keep-build` | for debugging: the build folder is kept even on success |

### 3. Reporting the result

Print the script's output, and at the end of your response place a **direct, clickable link** to the completed PDF(s).

### 4. Excluding `export/` from version control (one-time, only with VCS)

If the project has version control, and the `export/` folder is **not yet** excluded (`git check-ignore -q export/` returns a non-zero exit code), ask **once**:

<!-- INCLUDE:lang/export-doc.md#gitignore-felajanlas -->

Only write to `.gitignore` after the user's approval. If they say no, don't ask again on subsequent runs.

---

## Error handling

- **Missing dependency (exit code `2`):** the script prints what's missing and the install command (typically `npm install -g mermaid-filter`). **Do not try to work around it** and do not generate a PDF without mermaid rendering: without diagrams, or with broken ones, the document is unusable. Pass the install command to the user, and stop.
- **Pandoc error (exit code `1`):** the script prints pandoc's stderr, the `mermaid-filter.err`, and the xelatex log, and **keeps the build folder**. If a specific mermaid block has a syntax error, that is a **source error** in `docs-generated/` — tell the user it needs to be fixed in the `08-doc-sync` phase, don't rewrite the generated document yourself.
- **Partial success:** if multiple files were requested and only some were completed, list which succeeded and which didn't — the script reports this per file.

---

## What NOT to do

- **Do not modify the source markdown files** — neither the mermaid blocks nor the header block. The script makes a copy in the build folder and applies the YAML header there.
- **Do not calculate the version number yourself** and do not rename the output — the script does this deterministically.
- **Do not run pandoc directly** with manually assembled parameters. The engine settings (`MERMAID_FILTER_FORMAT`, `header.tex`, `--resource-path`, scaling of wide diagrams) are in the script — a manual call would omit these, and the diagram quality would degrade or labels would be lost.
- **Do not commit the `export/` folder**, unless the user asks: the PDF is binary, grows with each cycle, and can be regenerated at any time from `docs-generated/` (which, on the other hand, is version-controlled).
