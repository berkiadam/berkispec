# berkispec 🚧

**Spec-driven development CLI with Codex integration**

`berkispec` is a local, interactive CLI tool that helps structure development into clear phases and drive implementation through specifications.

> ⚠️ **Status: under active development**
>
> This project is not production-ready yet. Expect breaking changes.

---

## What is berkispec?

`berkispec` is inspired by spec-driven workflows, but designed to:

- work locally in your repository
- integrate with Codex CLI as an agent
- guide development through a structured lifecycle
- enforce clarity before implementation

---

## Core Idea

Instead of jumping straight into coding:

~~~
idea → code ❌
~~~

Follow a structured flow:

~~~
idea → spec → plan → tasks → implement → validate ✅
~~~

Each phase has a clear responsibility.

---

## Workflow Phases

| Phase | Purpose |
|---|---|
| `init` | Setup project-local workspace |
| `project` | Define persistent project context |
| `spec` | Create and refine feature specification |
| `plan` | Define technical implementation plan |
| `tasks` | Break down into executable steps |
| `implement` | Execute tasks |
| `validate` | Verify completion |

---

## Codex Integration

`berkispec` uses **Codex CLI** as the execution agent.

- `berkispec` = workflow orchestration
- Codex = spec writer / modifier / implementation agent

The tool itself does not manage OpenAI tokens or authentication. Codex CLI handles login, auth, model selection, and global configuration.

---

## Interactive Spec Loop

The `spec` phase is not one-shot.

~~~
1. You define the goal
2. Codex generates spec.md
3. Codex asks questions if something is unclear
4. You answer
5. Codex updates spec.md
6. Repeat until the spec is ready
~~~

Commands:

~~~
/done   → submit current input block and trigger Codex
/finish → exit the spec phase
~~~

---

## Specification States

Each specification has a status:

~~~
## Status

DRAFT
~~~

or:

~~~
## Status

READY_FOR_PLAN
~~~

Rules:

- `DRAFT` means open questions or unclear requirements remain
- `READY_FOR_PLAN` means the spec is ready for technical planning
- `/finish` does not automatically mean the spec is ready

---

## Plan Gate

The `plan` phase can only start when the spec contains:

~~~
Status: READY_FOR_PLAN
~~~

or, in Hungarian projects:

~~~
Állapot: READY_FOR_PLAN
~~~

The `plan` phase is blocked if:

- the spec is still `DRAFT`
- there are `[NEEDS CLARIFICATION ...]` markers
- there are open questions
- the status is missing or ambiguous

---

## Handling Open Questions

`berkispec` uses structured clarification inside `spec.md`.

### Inline marker

~~~
[NEEDS CLARIFICATION Q001: timeout value?]
~~~

### Open questions section

~~~
## Open Questions

- [ ] Q001: timeout value
  - Context: API call timeout
  - Why important: affects retry behavior
  - Status: OPEN
  - User answer: _not answered yet_
  - Decision: _not decided yet_
~~~

### Resolved decisions

~~~
## Resolved Decisions

- Q001: timeout value
  - User answer: 30 seconds
  - Decision: API timeout is 30 seconds
  - Affected spec section: Functional Requirements
~~~

---

## Project Structure

~~~
.berkispec/
  config.json
  latest-prompt.md
  project-desc.md
  prompts/
  history/

specs/
  cycle-XX-name/
    spec.md
    plan.md
    tasks.md
~~~

---

## Getting Started

~~~
./berkispec init
./berkispec project
./berkispec spec
~~~

---

## Current Status

`berkispec` is currently in early development.

Planned and evolving areas:

- Codex CLI integration
- interactive spec refinement loop
- status-based phase gates
- local prompt management
- history tracking
- better validation and reporting

---

## Philosophy

- clarity before code
- questions over assumptions
- specification as source of truth
- human approval before implementation planning

---

## License

TBD
