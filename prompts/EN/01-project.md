# 01 - Project

Use this phase when the project's basic data and durable context must be recorded or extended.

```text
Task:
- work with the `.berkispec/project-desc.md` file at the execution location
- create it if it does not exist yet
- manage the short project description and the list of reference files
- do not create a specification
- do not create a plan or tasks file

Possible operations:
- create a new project description
- `add description`: extend the textual description
- `add files`: add new reference files
- preserve existing content and only extend it

The `project-desc.md` file contains:
- textual project summary
- relative paths of reference files

Expectations:
- file paths must stay inside the execution directory
- references outside the project root must not be allowed
- file selection is optional
- the textual description is minimally recommended, but it must be possible to extend it later

At the end:
- state whether `.berkispec/project-desc.md` was created or updated
- state that the `spec` phase will reference this file automatically
```
