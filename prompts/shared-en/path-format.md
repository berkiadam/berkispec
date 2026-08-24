<!-- Source note: the single definition of the path convention. It is inlined by the
     quality check of 02/03/04 AND by the fixer agent belonging to them (build-time INCLUDE).
     Edit it in one place — the rule used to live in three places, with different content. -->
**Path format (RP1) — two kinds of reference, two rules:**

| What you reference | Format | Example |
|---|---|---|
| **Code and file reference** — affected component, planned change, `path:line` anchor, argument of a command | **relative to the root of the repo** | `src/token-store.ts`, `apps/web/src/index.ts:42`, `bash scripts/seed.sh` |
| **Document link** — a markdown link to another document | **relative to the own directory of the file** (so that it is clickable) | `[spec.md](./spec.md)`, `[architecture](../../docs/architecture.md)` |

**Why this way:** the commands run **in the root of the repo** (06-implement, 07-validate, `test-runner`), `git` and the helper scripts interpret the path the same way, and the mechanical gate of `05-analyze` (`A2`/`V1` check) **resolves the references to it**. A code reference of the form `../../src/app.ts` cannot be resolved in the gate and is wrong in the command — while for a *document link* the file-relative form is exactly the correct one, because that is what is clickable.

**Forbidden in both cases:**
- an **absolute path** (`/home/adam/repos/project/src/app.ts`, `C:\Users\...\src\app.ts`, `/mnt/c/...`) — machine specific, meaningless on another machine and in CI;
- a **`file://` scheme link** in the content of the document (a clickable link given in the *chat answer* is a different matter — that is expected there);
- a **placeholder** path (`<project>/src/...`, `/path/to/...`).

**What is NOT a file path, so the rule does not apply to it:** the path of an HTTP endpoint (`/api/v1/token-exchange`), a container-internal path in a command (`docker exec app cat /opt/app/config.yaml`), a JSON pointer, a regex.

_The mechanical gate of `05-analyze` checks this mechanically (`R1` check): `file://`, machine-specific and absolute repo paths in the design documents are `<status:must_fix>`._
