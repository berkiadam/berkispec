<!-- Source note: TWO places include this section (build-time INCLUDE):
     agents-en/reviewer.md (the subagent branch) AND the reviewer-fallback block
     of skills-en/07-validate.md (RV-FB1). By definition the fallback does not read
     the subagent's prompt, so it must receive the criteria list PHYSICALLY.
     Edit it in one place. -->
## Review criteria

- **Convention compliance:** File and variable names, import rules, cleanliness of architecture layers per `conventions.md`.
- **Code quality:** Unnecessary code duplication (DRY), overly complex functions, type safety (e.g. TypeScript/Python types).
- **Scope discipline:** Does the code contain unplanned functionality not listed in `plan.md` (scope creep)?
- **Spec deviation:** Does the implemented behavior meet the requirements of `spec.md`? A deviation from the specification is `<status:must_fix>`.
- **Error handling:** Proper error catching, use of specific error codes per the specification.
- **Test coverage:** Do the tests actually cover the new logic, and are regression tests unbroken?
- **Outdated comments and docstrings (VD12):** in files modified or newly created in the diff, are the comments, JSDoc/TSDoc/docstring descriptions **up to date** relative to the changes made (rename, changed parameter, changed error code, removed branch)? A comment that describes the **previous** behavior of the code is more misleading than its absence. Classification: **`<status:must_fix>`** if the comment/docstring **actively lies** about the current behavior (wrong parameter, wrong return value, removed error code); **`<status:suggestion>`** if it is merely incomplete or imprecisely worded. _(The 07 orchestrator deliberately does **not** read through the modified files in full — that is your job, since you go through the diff anyway.)_

## <status:must_fix> vs <status:suggestion> — the dividing line

The reviewer's decision is binary toward the 07-validate orchestrator: does it block the PASS or not.

- **<status:must_fix> = blocks the validation PASS** (and thereby the merge as well). This includes: security hole, specification deviation (the code does not do what `spec.md` says), convention violation (contrary to `conventions.md`), incorrect or missing error handling, broken regression test, scope creep.
- **<status:suggestion> = does not block.** This includes: refactoring idea, naming tip, cleanliness suggestion, optional simplification. A positive-toned remark can also go here (e.g. "this turned out well, worth applying elsewhere too").

In case of doubt: does the issue block correct/safe operation? If yes → <status:must_fix>. If it would only be nicer/cleaner → <status:suggestion>.
