<!--
  THE LANGUAGE OF THE OUTPUT (9.5) — this block is inlined at the top of every skill
  and every agent, directly after the H1. This is the ONLY place from which the agent
  learns which language it must write in: the project language is decided at build
  time and leaves no trace after installation (LG2/LG17) — neither conventions.md nor
  any other runtime source carries it.
  The block is DELIBERATELY written in the TARGET language (9.5.2): a rule phrased in
  the target language is at once an instruction AND a language anchor, and it holds
  measurably better than a rule phrased in another language.
  CAUTION: no comment-closing sequence may appear in this leading note.
-->

<!-- ANCHOR:output-language -->
> **🔴 THE LANGUAGE OF THE OUTPUT — ENGLISH. This is not a matter of style, it is a mandatory rule.**
>
> **You write in English:**
> - **every artifact** you create or edit — `spec.md`, `plan.md`, `tasks.md`,
>   `conventions.md`, `roadmap.md`, reports, question files, the documents of
>   `docs-generated/`: the headings, the body text, the table cells and the lists alike;
> - **every sentence you address to the user** in your answers — question, notice,
>   summary, error message, request for confirmation;
> - **the comments and docstrings written into the code**, if the existing code of the
>   project also comments in English; if the existing code uses another language, follow
>   the habit of the code base.
>
> **STAYS AS IT IS — never translate these:**
> - identifiers, function and variable names, type names, API field names, enum values;
> - file and folder names, paths, commands, flags, env variable names;
> - the framework's own identifiers: `/bs-*` command names, rule IDs (`DS22`, `TR3`,
>   `[P-…]`, `DoD-NN`, `MF-NN`, `Qnn`), task markers (`[RED]`, `[GREEN]`, `[CHECK]`, `[OPS]`),
>   status markers (`[analyze-loop]`, `[validate-loop]`);
> - code blocks, JSON/YAML keys, regexes, HTTP methods and status codes.
>
> **Mixing is an error.** A sentence of another language dropped into an English paragraph,
> a foreign-language heading in the English document or a half-translated table is **an
> error to be fixed**, not a matter of taste: the downstream phases and the deterministic
> gates **match mechanically** on the section titles and the status values, and a heading
> in the wrong language causes a gate failure.
>
> **If you find text in a language contrary to this prompt** in the artifact of an earlier
> phase, **do not rewrite it on your own** — report it to the user, and write your own
> added text in English.
