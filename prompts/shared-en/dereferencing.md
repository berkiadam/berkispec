<!-- Source note: this section is inlined by 03a-write-code-plan.md, 03b-write-test-plan.md
     AND the plan-fixer agent (build-time INCLUDE). Edit it in one place. -->
## Reference resolution (dereferencing) — the level of the input is NOT the level of the plan

> **The most frequent error in this phase:** the agent **reproduces the abstraction level of the input**. If the spec or `plan-input-from-prev.md` says *"an image build and a push to the registry by running `build.sh`"*, then this sentence gets into the plan — **without the concrete commands, the registry host, the image tag and the parameters**. The same way: if the input lists the **parameter names** of a call, the agent settles for that, and the **actual JSON payload** is missing from the plan (e.g. a mandatory `"channelType": "MOBILBANK"` field) that the existing test code contains.

**The rule:** the abstraction level of the input does not determine the abstraction level of the plan. **If an input item references something instead of containing it, the reference HAS TO BE RESOLVED from the source** — before you write it into the plan.

**What has to be resolved (not an exhaustive list — the pattern is the point):**

| The input says this | This has to be extracted and written into the plan | The source |
|---|---|---|
| "run `build.sh`" / "the usual deploy process" | the actual commands verbatim, the registry host, the image name and tag, the env variables | the script itself, the `Dockerfile`, the CI configuration |
| "we obtain a token with the login helper endpoint" | the full URL, the method, the **concrete JSON payload with every mandatory field**, the headers, an example `curl` | the existing test/helper code (`test/`), the OpenAPI descriptor |
| "following the pattern of the existing integration test" | the actual call chain, the fixtures, the seed data, the expected responses | the referenced test file |
| "with the tool according to `conventions.md`" | the **decision** stays a reference, but the **command to be run** concretely | `conventions.md` + `package.json`/`Makefile` |
| "the compose file brings up the stack" | the services, the ports, the health check, the start order | the compose file |

**How, token-efficiently:**

- **A small, targeted source** (one script, one env template, one compose file): read it **directly**.
- **A large or scattered source** (a code base search for a keyword, reviewing many test files): start the `researcher` subagent (`agents/researcher.md`) — **but explicitly ask for literal values in the request**: *"return the commands / the URL / the complete JSON payload verbatim, not a summary"*. The researcher compresses by default; here **precision takes priority over brevity**.
- **Follow the chain:** if the script references another script or an `.env` file, go on until you get a concrete value. **Exception:** a real secret (a cluster, registry, VPN, IAM credential) — there **stop and write a pointer** (TC5), not the value.
- **Do not copy in the whole REPO FILE:** from a source file/script lift over only the part needed for the execution (commands, coordinates, schema, parameters) — the plan is a plan, not an archive. **This rule applies to the source files of the repo, NOT to the elaborated artifacts coming from the spec** (OpenAPI, payload, error matrix, test scenario): those have to be carried over in their entirety, see `KX3`.
- **Do not paraphrase:** carry the command and the JSON over **verbatim**. A "roughly like this" payload is worse than nothing, because it creates false confidence.
- **Mark the source:** next to the value lifted over `_(source: keycloak/docker/build.sh)_` — this way it turns out later if the source moved away from the copy recorded in the plan.

**When this has to be run:** for every input item (the spec, `plan-input-from-prev.md`, `test-conventions.md`, the roadmap) that **references a procedure, a script, a configuration file, an external API or an existing test**. This is **especially** true in an early cycle, when `specs/test-conventions.md` does not exist yet: then the only source of the recipe data is the **existing code and tests** — find them, do not rely on the text of the input.

> **Closing the loop:** what you discover this way (commands, coordinates, payload schemas) goes into the `<sec:environment_coords>` (KO1) section — and it is exactly what has to get into `specs/test-conventions.md` at the end of the cycle through `08-doc-sync` — the concrete coordinates into block 0, the recipes into section 1 (TC3/TC13) — so that the next cycle does not discover it again.
