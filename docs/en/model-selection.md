# Automatic selection of models and effort levels

← [Back to the main page](../../README.md) · [Page index](README.md)

> **Principle: maximum token saving.** Every step runs on the **cheapest agent sufficient for it**; we spend the expensive model and deep reasoning only where it is indispensable. Quality does not come from the strength of the model, but from the **strict contracts** (mandatory checklists, "summary only", deterministic scripts).

The tuning happens on **two independent axes**:
- **Model** — *which* model runs (tier: `deep_reasoning_agent` / `default` / `research_agent`).
- **Effort** — *how many* reasoning/thinking tokens it burns (`high` / `medium` / `low`).

The two **do not coincide**: e.g. the fixers run on the `default` **model**, but at **`low` effort**, because they receive a precise, pre-identified defect list — they do not have to discover the problem.

**Model tier — who gets what:**

| Tier (`models.json` key) | Who gets it | Claude / Antigravity / Copilot / Cursor / Codex | Why this tier |
|---|---|---|---|
| `deep_reasoning_agent` (most expensive) | **exclusively** the `analyzer` (05) — **three parallel rounds** per iteration, each with a sliced input (SH1) | `claude-opus-4-8` / `pro` (tier) / `Claude Opus 4.8` / `claude-opus-5` / `gpt-5.6-sol` | Cross-phase consistency **diagnosis** (spec/plan/tasks/conventions) — the deepest reasoning; a mistake made here is the most expensive downstream (bad code is built on a bad diagnosis). |
| `default` | **everything else:** orchestrator skills (05, 07…), the 4 fixers (`spec`/`plan`/`tasks`/`implement`-fixer), `reviewer`, `review-fixer`, `doc-sync-planner`, `test-runner` | `claude-sonnet-5` / `flash` (tier) / `Claude Sonnet 5` / `claude-sonnet-5` / `gpt-5.6-luna` | The fixers receive a **finished, precise defect list** (solution/escalation, not discovery); the orchestrators do bookkeeping (marker, counter, routing) based on the **finished** report of the subagent — not diagnosis. |
| `research_agent` (cheapest) | `researcher` (00/01/02/03/06 + `bs-brainstorm`), the `cycle-status` skill | `claude-haiku-4-5-20251001` / `flash` (tier) / `Claude Haiku 4.5` / `claude-sonnet-5` (low) / `gpt-5.4-mini` | Pure grep/glob/read fan-out, or deterministic script execution — **zero design judgement**; the "summary only, never raw file content" contract protects it. On Antigravity there is no tier cheaper than `flash`, so there it coincides with the `default` tier; in Cursor there is no Haiku, so there the `default` Sonnet 5 runs at `low` effort. |

**Effort allocation — how much reasoning:**

| Effort | Who gets it | Why |
|---|---|---|
| `high` (default effort) | `analyzer`, and every non-overridden agent | Open-ended discovery/diagnosis, where deep reasoning pays. This is the **safe default** (the `default` effort of `models.json`). |
| `medium` | `reviewer`, `doc-sync-planner` | Requires judgement, but along a **fixed list of criteria** (not open-ended discovery). |
| `low` | the 4 fixers + `review-fixer`, `test-runner`, `researcher`, `cycle-status` | Work that fixes a precise defect list in a targeted way, or is purely mechanical — reasoning depth does not pay here, it only burns tokens. |

**One deliberate exception:** the `test-runner` is mechanical (running tests/Sonar/E2E), yet it runs on the `default` **model** (not the cheapest) — the multi-step Bash orchestration (port collision, config restoration) and the reliable summarisation of test/Sonar output that differs per project **with consistent test names** is critical: a mistyped name could silently corrupt the per-item 3-attempt counter of the 07 loop (VD4). (Its effort, however, is `low` — accuracy here is a matter of following a form, not of reasoning depth.)

**Configuration and installation:**
- **Source:** [`prompts/models.json`](../../prompts/models.json) — per platform (`claude` / `antigravity` / `copilot` / `cursor` / `codex`) the 3 tiers as `{model, effort}` objects, plus the agents that differ from the default **as rows named after themselves** (with only the `effort` field; their model comes from the `default` tier). The `AGENT_MODEL_KEYS` dictionary of `install-helper.py` maps the `analyzer`/`researcher`/`cycle-status` stems to the tiers (`analyzer-exec` is deliberately not in it: the inventory of the gate hands it the candidates ready-made, so it runs on the `default` tier); whatever is in neither place, nor as its own row in `models.json`, gets the `default` model and the `default` (=`high`) effort.
- **Writing it in at install time** (`./install.sh`): Antigravity → the `"model"` key of `agent.json`, with a **tier value** (`pro` / `flash` / `inherit`); Claude Code / Copilot → the `model` + `effort` fields of the agent file's YAML frontmatter; Cursor → the `model` field of the agent file's YAML frontmatter, **with a model identifier and a parameter in brackets**: `model: claude-opus-5[effort=high]` (Cursor knows no separate `effort:` field); Codex → the `model` + `model_reasoning_effort` keys of `.codex/agents/<name>.toml` (+ `sandbox_mode = "read-only"` for the read-only agents).
- **The skills** (orchestrator main agents, not subagents) **get neither a `model` nor an `effort`** — on any platform. A skill-level `model` is namely **not part of the base Agent Skills standard** (that only has `name`/`description`/`license`/`compatibility`/`metadata`/`allowed-tools`), but a Claude Code extension, which the target platforms **do not, or do not reliably, honour** for switching models:
  - **Codex:** SKILL.md only knows `name` + `description` → a `model` is inert.
  - **Copilot:** `.instructions.md` knows no `model` field (that only exists for a *prompt* file) → inert.
  - **Antigravity:** `model` is a field of the *agent* frontmatter, not of the skill → inert.
  - **Cursor:** it knows the `model` extension at best partially → not guaranteed.
  - **Claude Code:** the documentation promises the skill-`model` switch, but in reality it **has no effect at runtime** ([anthropics/claude-code #45191](https://github.com/anthropics/claude-code/issues/45191), closed as "not planned").
  Since a skill-`model` written in is inert in the best case and misleading in the worst (it suggests a capability that does not exist), **we inject it nowhere**. Model tuning takes reliable effect **exclusively at the level of the agents/subagents** (Claude subagent `model`/`effort`, Codex `.codex/agents/*.toml` `model`/`model_reasoning_effort`) — that is where it stays.
- **Native support for effort:** in Claude Code the subagent `effort:` frontmatter field, and in Codex the `model_reasoning_effort` field of `.codex/agents/*.toml`, **take effect natively** (the value in the file takes precedence). On the other platforms (Antigravity/Copilot) the value is a **visible recommendation** (frontmatter + a "Recommended Effort" alert) — Antigravity's schema has no `effort` field at all, so there it only goes into the alert. Cursor's `model` field, on the other hand, is native — there the effort also takes effect natively in the `[effort=...]` parameter. Important: Cursor expects the **model identifier** (`claude-opus-5`), not a display name ("Opus 4.8"); on an invalid identifier it silently falls back to the parent agent's model. In Cursor the read-only agents (`analyzer`, `analyzer-exec`, `researcher`, `doc-sync-planner`) get `readonly: true`, and in Codex `sandbox_mode = "read-only"`.
- **Manual switching:** if you do not rely on the installed agents, follow the allocation above in the model and effort selector of your CLI/IDE.

**Antigravity specifics — the `model` field is a TIER, not a model name** ([Antigravity: Subagents](https://antigravity.google/docs/subagents))

In Antigravity's custom agent schema the `model` field takes a **model tier**, not the name of a concrete model:

```
model: pro       # the strongest tier
model: flash     # the fast/cheap tier
model: inherit   # the parent agent's model (default)
```

- **The model name is invalid.** The `"model": "Claude Opus 4.6"` written in earlier is not a tier → the subagent falls back to the `inherit` default, i.e. it **runs on the parent agent's model** (typically Flash). This is silent: the "correct" model name sits there in the file, yet the run is the parent's — this is exactly why the `analyzer` ran on Flash even when `agent.json` said Opus.
- **There is no `effort` field in the schema.** The tier itself carries the capability level; that is why we write the `effort` value out only as a **visible recommendation** (alert), not into `agent.json`. This has one consequence for the allocation: since there is no tier cheaper than `flash`, `research_agent` and `default` **get the same thing** — the effort-based distinction cannot be enforced mechanically here.
- **Tier mapping:** `deep_reasoning_agent` → `pro`, `default` and `research_agent` → `flash`.

> The `.agents/agents/<name>/agent.json` format is no longer mentioned by the current Antigravity docs — the documented location is `.agents/agents/<name>.md` with YAML frontmatter. In practice `agent.json` still loads (the installed agents appear and run), so for now we stay with it; if Antigravity drops support for it, the `process_antigravity` function of the installer is the point where the switch to the `.md` format has to be made.

**Cursor specifics — the subagent `model` field** ([Cursor: Subagents](https://cursor.com/docs/subagents))

The fields of a Cursor subagent frontmatter: `name`, `description`, `model`, `readonly`, `is_background`. **There is no separate `effort:` field** — the parameters attach to the model's identifier in square brackets, separated by commas:

```yaml
model: claude-opus-5[effort=high]        # effort= / context= / fast=
model: claude-sonnet-5[effort=low]
model: inherit                            # the parent agent's model (default)
```

Three things that easily mislead:

1. **It expects an identifier, not a display name.** The form `model: Opus 4.8` is not valid; it has to be `claude-opus-5` / `claude-sonnet-5`.
2. **The labels of the model picker UI are not the frontmatter form.** The slugs visible in Cursor's interface in the style of `claude-opus-5-thinking-high` / `gpt-5.6-sol-medium` are the names of the *picker*; the documented frontmatter form is the identifier + `[effort=…]`. From Claude, only `-thinking-high` exists in the slug list, so the forms `-thinking-low` / `-thinking-medium` are invalid — and they would fail precisely for the low-effort agents (fixers, `test-runner`, `researcher`).
3. **An invalid value is SILENT.** If Cursor does not recognise the identifier — or recognises it but there is no entitlement for it (an admin disabled it, the plan does not include it, or with a legacy request-based plan Max Mode would be needed) — then it **falls back to the parent agent's model without an error message**. The symptom only shows in the behaviour: e.g. the `analyzer` seemingly runs, but not on Opus 5.

For this reason, always write a **model identifier into the `cursor` section** of `models.json`; the effort is appended by the installer (`install-helper.py` → `inject_cursor_agent`). One tier divergence belongs here too: **there is no Haiku in Cursor**, so `research_agent` gets the `default` Sonnet 5 at `low` effort — the same solution as with Flash on Antigravity.
