## Context check

**A deterministic rule — do not deliberate, count.**

Count **your own, earlier phase-closing messages** in the conversation. A message counts as phase-closing **only** if it contains **all three** elements:

1. a commit identifier, **and**
2. a call to run `/clear`, **and**
3. the `/bs-*` command of the next phase.

The counter applies **only to your own, earlier phase-closing messages**. No other content increases it — whatever else you see in the context does not affect the number.

| Counter | What to do |
| --- | --- |
| **0** | **The context is fresh — you continue without asking.** This is the normal case. |
| **≥1** | You ask once (see below), and wait for the answer. |

**Two hard exceptions that override the counting — in both of them asking is forbidden:**

- if this skill call is the **first user message** in the conversation, the counter is **0 by definition**;
- if you are **uncertain** about the number, the counter is **0**.

If (and only if) the counter is **≥1**, ask:

<!-- INCLUDE:lang/context-check.md#kontextus-nem-friss -->

Wait for the answer before continuing.
