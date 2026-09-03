<!-- Source note: this section is included (build-time INCLUDE) by both the
     02-write-spec.md and the 03b-write-test-plan.md skill (and by their matching
     fix-mode-* shared files). Edit it in one place. -->
## Designing test scenarios — dimensions and observation points (TD1–TD7)

The surrounding rules (KX2, KX3, TS1–TS6) **preserve** whatever detail the input carries — but none of them **creates** a scenario. If the input is a single sentence ("token renewal must not be duplicated when several instances run"), the hard floor of TS3 is satisfied by one step and one backticked value: a formally complete test that proves nothing about the behaviour. This block is the missing step: it turns test design into **questions to be answered**, so that it does not have to be inferred.

**Scope — how far in which phase (TD0):** in the `<sec:test_specification>` (spec) section, steps 1 and 2 run at **behaviour level**: naming the dimensions and the observation points is mandatory, but coordinates stay symbolic and commands are **FORBIDDEN** — those belong to `plan.md`. In the `<sec:plan_test_scenarios>` (plan) section the same six rules run, but with literal values and calls that are runnable verbatim.

### 1. Dimension inventory — this decides HOW MANY scenarios are needed (TD1)

Walk through the six dimensions below and write down, for each, which of its values are **relevant in this cycle**. Wherever two or more values are relevant, the dimension **multiplies**: every meaningful combination is **a scenario of its own**.

| # | Dimension | Typical values | Example |
|---|---|---|---|
| 1 | instance count and concurrency | 1 instance / N instances; 1 request / N simultaneous requests | 3 pods, 5 requests arriving at once |
| 2 | initial state | empty / populated / partially populated store | empty cache vs. existing entry |
| 3 | lifecycle band or state-machine state | valid / boundary / expired / missing | valid, within-margin, hard expired |
| 4 | resource scope | global / bound to an entity — **and the two crossed** | system-wide vs. bound to a session |
| 5 | input class | valid / missing / malformed / unauthorised | — |
| 6 | order and timing | before-after / simultaneous / interrupted | the holding instance dies halfway |

- **The product must be written out.** One line before the scenario list should state where the count comes from: e.g. *"2 scopes (global, session) × 2 expiry bands (within-margin, hard expired) = 4 scenarios"*. This is the only checkable trace that the list is not ad hoc.
- **Merging is allowed only with a reason.** If two combinations exercise the same code path they may share one scenario — but **write down in one line why**. An unjustified merge is a coverage gap.
- **🔴 A single scenario is suspicious.** If the cycle's behaviour has two or more dimensions but the list has one item, the inventory **did not run** — go back to step 1.

### 1/b. Every test case states WHAT it verifies and WHY (TD7)

Steps do not explain themselves just by being concrete. A "5 parallel requests, all `200`" step list does not reveal on its own **which behaviour** it runs to prove, and because of that the later phases cannot decide whether a failure is a real defect or a bad test — and the fixer then takes the easiest path that turns the step green, not the one that restores the behaviour. Therefore **every test case — scenario, unit case, integration flow, test file — states BEFORE the steps:**

| What has to be stated | Its measure |
|---|---|
| **what it verifies** | the behaviour as a claim about which, after the run, it can be decided whether it is true (not a summary of the steps, not the name of the test repeated) |
| **why it matters** | which acceptance criterion (`DoD-NN`) or risk it proves — what would silently break without it |
| **what the evidence is** | which observation (from the TD2 quartet) decides the question |

- **A title is not a purpose.** "Test case 3: concurrency" — that is a topic, not a claim. The claim is: *"out of five simultaneous requests exactly one renews the token, the other four are served from the existing one, and none of them blocks for longer than 2 s."*
- **Scope (per TD0):** in the spec phase a behaviour-level sentence referring to a `DoD-NN`; in the plan phase the same, but with the concrete values referenced.
- **If you cannot say in one sentence what it verifies, the test case is not designed** — either it merges several cases (split it along the TD1 product), or there is no acceptance criterion behind it (then the question goes into the phase's question file).

### 2. The observation quartet — this decides WHAT goes into a scenario (TD2)

A scenario's step table is not a request-response pair: besides the trigger, **four** kinds of observation must appear wherever they are meaningful. The lower three are the ones that merely following the template never produces — which is why they are phrased as questions:

| Kind | The question to answer | What it puts in the step table |
|---|---|---|
| direct response | what does the called interface return? | status code **and** an identifiable field of the response |
| counted side effect | what is it that happens **exactly this many times**? (outbound call, retry, log entry, created record) | a row whose expected result is a **number** |
| directly read state | which stored state can be read without asking the system? (key, DB row, file, metric) | a query against the store — with the **name/key literally** and the value too |
| negative control | what must **NOT** happen? | a row whose expected result is the **absence** of an effect |

- **The key's name must be checked, not just its existence.** A naming defect (duplicated postfix, wrong prefix) is **invisible** in the response — the request still returns 200. So the row for read state carries the key/field name verbatim as an expected value.
- **Timing expectations need a measured value.** If the expectation is "does not block" or "no added latency", then the step carries a **measured value and a threshold** (e.g. the response time for the concurrent requests is `< 200 ms`). Without a threshold the expectation is not decidable.

### 3. Countability — if it cannot be measured, it is not a test (TD3)

An expectation of the form "exactly once" / "is not duplicated" / "produces no logs" can be proved **only by counting**. So every such expectation must name the **source of the count**: a mock request journal, a request counter, an application metric, a log subset, or a query against the store. If the cycle has no such source, then either it must be **planned in** (among the plan's planned changes), or the question goes into the phase's question file — "it presumably runs only once" is **not** an expected result.

### 4. Negative control — the only way to prove isolation (TD4)

If the cycle commits to a **scope or an isolation** property (X affects only Y, never Z), then proving it takes **two** observations: that X happened, and that **meanwhile** nothing happened to Z. At least one scenario must contain a step that exercises the path meant to be protected while the effect is under way, with **unchangedness** as its expected result (the other entity's request still succeeds, the other key is untouched). An acceptance criterion that commits to isolation is **not covered** without a negative control.

### 5. Calibration sample — the floor for density (TD5)

The block below is **not** your cycle's content: copy its **density** and its **observation points**, not its subject. A scenario standing on fewer observation points than this is suspicious.

```md
#### TS-01 — Cold-start concurrency: global token, 3 instances, 5 sessions  (DoD-01, DoD-07)

**<field:f_what_we_test>:** starting from an empty store, under a burst of simultaneous requests exactly one instance renews the global token, the others wait for it, and the session-level path is not blocked meanwhile.
**<field:f_prerequisite>:** 3 running instances on the same store (startup: `<sec:e2e_infrastructure>` steps 1–3), reachability probe green.

| # | Step | Call | Expected result |
|---|---|---|---|
| 1 | flush the store | `redis-cli -h redis.remote.example.com -n 0 FLUSHDB` | `OK`, and `KEYS ns01_tmp:*` returns an empty list |
| 2 | reset the request journal | `curl -s -X POST https://mock.remote.example.com/__admin/requests/reset` | `200` |
| 3 | create 5 sessions | `for i in 1 2 3 4 5; do curl -s -X POST https://tmp.remote.example.com/login -H 'Content-Type: application/json' -d '{"username":"testuser@example.com","password":"Pass1234"}' -o sess-$i.json; done` | all 5 responses are `200`, and the 5 extracted `sid` values are pairwise **different** |
| 4 | fire 5 requests simultaneously | `printf '%s\n' 1 2 3 4 5 \| xargs -P 5 -I{} curl -s -o out-{}.json -w '%{http_code} %{time_total}\n' -X POST https://tmp.remote.example.com/init-hash -H "Authorization: Bearer $(jq -r .access_token sess-{}.json)"` | all 5 lines are `200`, and every `out-N.json` contains an `initHash` field |
| 5 | counted side effect | `curl -s https://mock.remote.example.com/__admin/requests/count -d '{"method":"POST","url":"/token","bodyPatterns":[{"contains":"grant_type=client_credentials"}]}' \| jq .count` | `1` — exactly one renewal call for the 5 requests |
| 6 | read state: key name and shape | `redis-cli -h redis.remote.example.com --no-raw GET ns01_tmp:tokens:s2s \| jq 'keys'` | the key's name is exactly `ns01_tmp:tokens:s2s` (not `…:tokens:tokens:s2s`), and the JSON fields are `["accessToken","expiresAt","issuedAt"]` |
| 7 | read state: the lock is released | `redis-cli -h redis.remote.example.com EXISTS ns01_tmp:tokens:s2s:lock` | `0` — the holding instance deleted it when it finished |
| 8 | negative control | **simultaneously** with step 4: `curl -s -o /dev/null -w '%{http_code} %{time_total}\n' https://tmp.remote.example.com/media/42 -H "Authorization: Bearer $(jq -r .access_token sess-1.json)"` | `200`, and the response time is `< 0.5` s — renewing the global token did not block the session-level path |
| 9 | measured timing expectation | the `%{time_total}` values from step 4 | each one `< 2.0` s — nothing hangs beyond the wait timeout |

**<field:f_cleanup>:** `rm -f sess-*.json out-*.json`; scale the instance count back to 1; flush the store.
```

### 6. Self-check before closing the section (TD6)

- The dimension product is **written out**, and the number of scenarios matches it (or every merge is justified in one line).
- Every scenario has a **counted side effect** row (a number in the expected result) — or one line explaining why that is not meaningful here.
- Every scenario has a **directly read state** row, including the name of the key/field.
- Acceptance criteria that commit to isolation have a **negative control** step.
- Every "exactly once" / "is not duplicated" / "produces no" expectation names the **source of the count**.
- Every "does not block" / "no added latency" expectation carries a **measured value and a threshold**.
- **Every test case states what it verifies and why** (TD7) — as a claim, with a `DoD-NN` reference; repeating the title is not enough.
