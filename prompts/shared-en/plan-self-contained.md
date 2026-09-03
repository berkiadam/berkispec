<!-- Source note: this section is inlined by the 03a-write-code-plan.md AND the
     03b-write-test-plan.md skill (build-time INCLUDE). Edit it in one place. -->
### 🔴 `plan.md` is SELF-CONTAINED — this is the most important rule of this phase

**The plan is the last document that still sees the spec.** What happens from here downwards works **exclusively from the plan**:

| Consumer | What it reads | What it does NOT see |
|---|---|---|
| `04-write-tasks` | **only `plan.md`** (the skill explicitly forbids re-reading the spec and the source files) | the spec, the code base |
| `06-implement` | `plan.md` + `tasks.md`; it navigates back here from the tasks | the spec |
| `test-runner` (07/09) | the `<sec:testing_strategy>` and `<sec:regression_impact>` sections of `plan.md` | the spec, `test-conventions.md` |
| `03b-write-test-plan` | the **code half** of `plan.md` + the test section and `DoD` of the spec | the code base for the purpose of source-file identification |

From this follows the rule that **cannot be overridden**: **every piece of information that is needed for the development, the testing or the verification has to be physically in `plan.md`.** Nothing essential may be left out on the grounds that "it is in the spec anyway", "it can be seen in the code", "`build.sh` contains it" or "it was said in the conversation". Whatever is not in the plan **does not exist** for the downstream phases — and it will not run, it only gives the false impression of being documented.

**Concretely, the following have to be in the plan** (whatever is applicable to the given cycle):

- the full path of the affected files; the names of the functions, classes, modules to be created/modified;
- **function signatures, interfaces, types**, the exact form of the interface change;
- data structures and **payloads with concrete fields** (an example request/response, not just a list of field names);
- error branches: condition → HTTP status + errorCode + response body;
- configuration: the **name AND the value** of the env variable, where it is set;
- the coordinates of an external integration: URL, port, realm/client/scope, test user, an example `curl` call;
- runnable **commands verbatim** (build, deploy, startup, running the tests, verification);
- the execution order and the prerequisites; the migration and rollback scenario, if there is a schema change.

> **A self-test (apply it before closing):** *"If somebody gets only `plan.md` and `tasks.md` — without the spec, without knowledge of the code base and without this conversation —, can they develop and test the cycle?"* If they would have to **ask back or guess** at any point, the plan is incomplete. The question is not whether you understand it; it is whether a reader who knows less than you can carry it out.

**Forbidden phrasings in the plan:** "see the spec", "in the usual way", "to the appropriate endpoint", "run `build.sh`", "with the parameters used in the earlier cycle", **"following the pattern of cycle-XX" / "as in the existing test file" / "according to the sequence diagram of the spec"**, `<here comes …>`, `TODO`. Each of them means that the concrete detail **is missing** — add it, or if you do not know it, add it as a question to `plan-questions.md`.

**Do not produce a task list or an implementation.** That is the task of the next step.

**Do not plan anything that is not in the spec.** The scope of the plan is exactly the scope of the spec — it does not widen it, it does not narrow it. If, while writing the plan, you feel that something should be added that is missing from the spec, that is a spec deficiency — report it and ask for the spec to be updated, do not fill it in yourself in the plan.

**If something is missing or contradictory in the spec, report it — but do not complete the spec in your head. The plan works from the spec only.**

> **Is the task too simple for a full cycle?** If, while writing the plan, it turns out that the cycle is actually trivial — there is no real design decision, essentially it is only **putting a configuration together, a simpler script or a smaller fix** —, then the full `plan → tasks → analyze → … → review` flow is oversized. Tell the User, and **recommend the simplified flow**: *"This cycle looks simple enough for the full process; `/bs-quick-flow` (spec → task → implementation) may be faster for it. Shall we switch to that, or stay with the full cycle?"* The decision belongs to the User — do not switch arbitrarily, and do not skip phases within the full flow.
