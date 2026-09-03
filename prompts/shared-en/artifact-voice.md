<!--
  SHARED "artifact voice" rule (AV1) — for phases 02/03/04.
  This is NOT a standalone skill/agent, but a shared text block that the installer
  (install-helper.py) embeds INLINE at build time into the installed version of the
  referencing skill (in place of the `<!-- INCLUDE:shared/artifact-voice.md -->` marker).
  Referenced by: 02-write-spec, 03a-write-code-plan, 03b-write-test-plan, 04-write-tasks.
  It has no frontmatter: its content is copied in verbatim. Edit it here.
-->

> **🔴 Artifact voice (AV1) — the document speaks to a HUMAN, not to you.** The reader of `spec.md` / `plan.md` / `tasks.md` is the implementer (human or agent), **not the addressee of your instructions**. Therefore **never copy** the skill text into the artifact:
>
> **The ADDRESSEE is the test, not the formatting.** Ask the question: *"if I delete this sentence, does the implementer lose a piece of information they need?"*
> - **Yes → it stays** (rephrased at most). Such is, for example, a machine-checkable prerequisite list ("`oc` must be logged in, namespace: `X`"), a warning about a shared environment, or an ordering constraint. **You may highlight these** with an `[!IMPORTANT]` / `[!CAUTION]` block — the highlighting in itself is not an error if the content addresses the implementer.
> - **No, it only repeats a rule that applies to you → it goes out.**
>
> - **Do not carry over the meta instructions:** *"It is forbidden to …"*, *"you must check …"*, *"go through …"*, *"do not forget …"*, *"the quality check fails if …"*, *"STRICT RULE"*. These apply to **your work**, not to the behavior of the system.
> **🔴 A hard floor — the FORM is not negotiable.** The addressee test decides whether the **content** stays; the **wording**, however, has to be rewritten even when the content is legitimate:
> - the **`🔴`** marking is the internal emphasis of the skills — it **never** gets into an artifact (the neutral `[!IMPORTANT]`/`[!CAUTION]` does);
> - the **"It is forbidden…" / "FORBIDDEN…"** imperative **must not be used** in an artifact, not even when the constraint behind it is real.
>
> In such a case you **do not delete the information, you rephrase it**: ❌ *"🔴 Using the static `:v1` tag is forbidden"* → ✅ *"The tag of the image is unique per run (`v1-<UTC timestamp>`); overwriting the static tag would make the rollback impossible."* The same knowledge, in a neutral, descriptive tone.
> - **You translate the rule into a DECISION.** You do not write down what the skill forbade you to do, but **what the decision was**. Example:
>   - ❌ *"🔴 Using the static `:v1` tag is forbidden, because the rollback would be illusory."*
>   - ✅ *"The tag of the image is unique per run: `v1-<UTC timestamp>`."* — and the justification goes into the `<sec:risks_and_decisions>` section (in the plan), respectively into the `<sec:risks>` section (in the spec).
>
> **Why it matters:** these documents are read **mechanically** by the downstream phases. An imperative left in there is ambiguous as a requirement or as a task (the way a "the state of spec.md has to be updated" DoD item became a task), and when the skill changes later it stays there as an outdated copy.
>
> **This is not a ban on explanation:** the **justification** (why we decided this way, what the risk is) is still needed — only in the section designated for it, in a **descriptive** tone.
