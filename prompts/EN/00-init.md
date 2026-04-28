# 00 - Init

Use this phase when the local `berkispec` working directory must be created at the execution location.

```text
Task:
- create the `.berkispec/` folder at the execution location
- prepare its internal file structure if it does not exist yet
- do not create a specification yet
- do not create a plan or tasks file

Prepare at least these items if they do not exist yet:
- `.berkispec/config.json`
- `.berkispec/project-desc.md`
- `.berkispec/prompts/`
- `.berkispec/history/`

Expectations:
- init is only bootstrap
- work at the execution location, not in the tool's own directory
- select the project language once, if it has not been selected yet
- copy only the prompt set matching the selected project language into `.berkispec/prompts/`
- do not allow changing the project language later
- if `.berkispec/` already exists, do not overwrite anything unnecessarily

At the end:
- state whether `.berkispec/` was created or already existed
- state the selected project language
- state that the next required step is the `project` phase
```
