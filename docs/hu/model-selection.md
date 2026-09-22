# Modellek és effort-szintek automatikus választása

← [Vissza a főoldalra](../../README-HU.md) · [Oldalindex](README.md)

> **Elv: maximális token-megtakarítás.** Minden lépés a hozzá **elégséges legolcsóbb ágensen** fut; a drága modellt és a mély reasoningot csak ott költjük, ahol nélkülözhetetlen. A minőséget nem a modell ereje adja, hanem a **szigorú kontraktusok** (kötelező ellenőrzőlisták, „csak összefoglaló", determinisztikus scriptek).

A hangolás **két független tengelyen** történik:
- **Modell** — *melyik* modell fut (tier: `deep_reasoning_agent` / `default` / `research_agent`).
- **Effort** — *mennyi* reasoning/thinking-tokent éget (`high` / `medium` / `low`).

A kettő **nem esik egybe**: pl. a fixerek a `default` **modellen** futnak, de **`low` efforton**, mert pontos, előre azonosított hibalistát kapnak — nem nekik kell felfedezni a problémát.

**Modell-tier — ki mit kap:**

| Tier (`models.json` kulcs) | Ki kapja | Claude / Antigravity / Copilot / Cursor / Codex | Miért ez a tier |
|---|---|---|---|
| `deep_reasoning_agent` (legdrágább) | **kizárólag** `analyzer` (05) — iterációnként **három párhuzamos kör**, körönként szeletelt bemenettel (SH1) | `claude-opus-4-8` / `pro` (tier) / `Claude Opus 4.8` / `claude-opus-5` / `gpt-5.6-sol` | Kereszt-fázisos konzisztencia-**diagnózis** (spec/plan/tasks/conventions) — a legmélyebb reasoning; egy itt vétett hiba a legdrágább downstream (rossz diagnózisra rossz kód épül). |
| `default` | **minden más:** orchestrátor-skillek (05, 07…), a 4 fixer (`spec`/`plan`/`tasks`/`implement`-fixer), `reviewer`, `review-fixer`, `doc-sync-planner`, `test-runner` | `claude-sonnet-5` / `flash` (tier) / `Claude Sonnet 5` / `claude-sonnet-5` / `gpt-5.6-luna` | A fixerek **kész, pontos hibalistát** kapnak (megoldás/eszkaláció, nem felfedezés); az orchestrátorok bookkeeping-et végeznek (marker, számláló, routing) a subagent **kész** jelentése alapján — nem diagnózis. |
| `research_agent` (legolcsóbb) | `researcher` (00/01/02/03/06 + `bs-brainstorm`), `cycle-status` skill | `claude-haiku-4-5-20251001` / `flash` (tier) / `Claude Haiku 4.5` / `claude-sonnet-5` (low) / `gpt-5.4-mini` | Tiszta grep/glob/read fan-out, ill. determinisztikus script-futtatás — **nulla tervezési ítélet**; a „csak összefoglaló, soha nyers fájltartalom" kontraktus véd. Antigravityn nincs olcsóbb tier a `flash`-nél, ezért ott a `default` tierrel esik egybe; Cursorban nincs Haiku, ott a `default` Sonnet 5 fut `low` efforton. |

**Effort-leosztás — mennyi reasoning:**

| Effort | Ki kapja | Miért |
|---|---|---|
| `high` (default effort) | `analyzer`, és minden nem-felülírt agent | Nyílt végű felfedezés/diagnózis, ahol a mély reasoning fizet. Ez a **biztonságos alapértelmezés** (a `models.json` `default` effortja). |
| `medium` | `reviewer`, `doc-sync-planner` | Ítéletet igényel, de **kötött szempontlista** mentén (nem nyílt felfedezés). |
| `low` | a 4 fixer + `review-fixer`, `test-runner`, `researcher`, `cycle-status` | Pontos hibalistát célzottan javító, ill. tisztán mechanikus munka — a reasoning-mélység itt nem fizet, csak tokent éget. |

**Egy szándékos kivétel:** a `test-runner` mechanikus (tesztek/Sonar/E2E futtatása), mégis `default` **modellen** (nem a legolcsóbbon) fut — a több lépéses Bash-orchesztráció (portütközés, config-visszaállítás) és a projektenként eltérő teszt-/Sonar-kimenet megbízható, **konzisztens tesztnevű** összegzése kritikus: egy elgépelt név csendben elronthatná a 07-hurok per-item 3-próba számlálóját (VD4). (Az effortja viszont `low` — a pontosság formakövetés, nem reasoning-mélység kérdése.)

**Konfiguráció és telepítés:**
- **Forrás:** [`prompts/models.json`](../../prompts/models.json) — platformonként (`claude` / `antigravity` / `copilot` / `cursor` / `codex`) a 3 tier `{model, effort}` objektumként, plusz a defaulttól eltérő agentek **saját nevű sorként** (csak az `effort` mezővel; a modelljük a `default` tierből jön). Az `install-helper.py` `AGENT_MODEL_KEYS` szótára rendeli az `analyzer`/`researcher`/`cycle-status` stemeket a tierekhez (az `analyzer-exec` szándékosan nincs benne: a kapu leltára készen adja neki a jelölteket, tehát `default` tieren fut); ami nincs sem itt, sem saját sorként a `models.json`-ban, `default` modellt és `default` (=`high`) effortot kap.
- **Beírás telepítéskor** (`./install.sh`): Antigravity → `agent.json` `"model"` kulcs, **tier-értékkel** (`pro` / `flash` / `inherit`); Claude Code / Copilot → az agent-fájl YAML frontmatter `model` + `effort` mezője; Cursor → az agent-fájl YAML frontmatter `model` mezője, **modell-azonosítóval és zárójeles paraméterrel**: `model: claude-opus-5[effort=high]` (a Cursor nem ismer külön `effort:` mezőt); Codex → a `.codex/agents/<név>.toml` `model` + `model_reasoning_effort` kulcsa (+ read-only agenteknél `sandbox_mode = "read-only"`).
- **A skillek** (orchestrátor fő ágensek, nem subagentek) **sem `model`-t, sem `effort`-ot nem kapnak** — egyetlen platformon sem. A skill-szintű `model` ugyanis **nem része az Agent Skills alap-szabványnak** (az csak `name`/`description`/`license`/`compatibility`/`metadata`/`allowed-tools`), hanem Claude Code-kiterjesztés, amit a célplatformokon a modellváltás **nem, vagy nem megbízhatóan** követ:
  - **Codex:** a SKILL.md csak `name` + `description`-t ismer → egy `model` inert.
  - **Copilot:** az `.instructions.md` nem ismer `model` mezőt (az csak *prompt*-fájlnál van) → inert.
  - **Antigravity:** a `model` az *agent* frontmatter mezője, a skillé nem → inert.
  - **Cursor:** a `model`-kiterjesztést legfeljebb részlegesen ismeri → nem garantált.
  - **Claude Code:** a dokumentáció ígéri a skill-`model` váltást, de a valóságban **runtime-ban nem hat** ([anthropics/claude-code #45191](https://github.com/anthropics/claude-code/issues/45191), „not planned"-ként lezárva).
  Mivel egy beírt skill-`model` a legjobb esetben inert, a legrosszabban félrevezető (nem létező képességet sugall), **sehová nem injektáljuk**. A modell-hangolás **kizárólag az agentek/subagentek** szintjén hat megbízhatóan (Claude subagent `model`/`effort`, Codex `.codex/agents/*.toml` `model`/`model_reasoning_effort`) — ott marad meg.
- **Effort natív támogatása:** Claude Code-ban a subagent `effort:` frontmatter-mező, Codexben a `.codex/agents/*.toml` `model_reasoning_effort` mezője **natívan hat** (a fájl értéke elsőbbséget élvez). A többi platformon (Antigravity/Copilot) az érték **látható ajánlás** (frontmatter + „Recommended Effort" alert) — az Antigravity sémájában nincs is `effort` mező, ezért oda csak az alertbe kerül. A Cursor `model` mezője viszont natív — ott az effort is natívan hat a `[effort=...]` paraméterben. Fontos: a Cursor a **modell-azonosítót** várja (`claude-opus-5`), nem megjelenített nevet („Opus 4.8"); érvénytelen azonosítónál csendben a szülő ágens modelljére esik vissza. Cursornál a read-only agentek (`analyzer`, `analyzer-exec`, `researcher`, `doc-sync-planner`) `readonly: true`-t, Codexnél `sandbox_mode = "read-only"`-t kapnak.
- **Manuális váltás:** ha nem a telepített ágensekre támaszkodsz, kövesd a fenti leosztást a CLI/IDE modell- és effort-választójában.

**Antigravity-specifikum — a `model` mező TIER, nem modellnév** ([Antigravity: Subagents](https://antigravity.google/docs/subagents))

Az Antigravity custom agent sémájában a `model` mező **modell-tiert** vesz fel, nem konkrét modell nevét:

```
model: pro       # a legerősebb tier
model: flash     # gyors/olcsó tier
model: inherit   # a szülő ágens modellje (alapértelmezés)
```

- **A modellnév érvénytelen.** A korábban beírt `"model": "Claude Opus 4.6"` nem tier → a subagent az `inherit` alapértelmezésre esik vissza, azaz **a szülő ágens modelljén fut** (jellemzően Flash-en). Ez néma: a fájlban ott a „helyes" modellnév, a futás mégis a szülőé — pontosan ezért futott az `analyzer` Flash-en akkor is, amikor az `agent.json`-ban Opus szerepelt.
- **`effort` mező nincs a sémában.** A tier maga hordozza a képesség-szintet; az `effort` értéket ezért csak **látható ajánlásként** (alert) írjuk ki, az `agent.json`-ba nem. Ennek egy következménye van a leosztásban: mivel a `flash`-nél nincs olcsóbb tier, a `research_agent` és a `default` **ugyanazt kapja** — az effort-alapú megkülönböztetés itt nem érvényesíthető gépiesen.
- **Tier-leképezés:** `deep_reasoning_agent` → `pro`, `default` és `research_agent` → `flash`.

> A `.agents/agents/<név>/agent.json` formátumot a jelenlegi Antigravity-doksi már nem említi — a leírt hely `.agents/agents/<név>.md` YAML frontmatterrel. Az `agent.json` a gyakorlatban továbbra is betöltődik (a telepített ágensek megjelennek és futnak), ezért egyelőre maradunk nála; ha az Antigravity ejti a támogatását, a telepítő `process_antigravity` függvénye az a pont, ahol a `.md` formátumra kell váltani.

**Cursor-specifikum — a subagent `model` mező** ([Cursor: Subagents](https://cursor.com/docs/subagents))

A Cursor subagent-frontmatter mezői: `name`, `description`, `model`, `readonly`, `is_background`. **Külön `effort:` mező nincs** — a paraméterek a modell azonosítójához tapadnak szögletes zárójellel, vesszővel elválasztva:

```yaml
model: claude-opus-5[effort=high]        # effort= / context= / fast=
model: claude-sonnet-5[effort=low]
model: inherit                            # a szülő ágens modellje (alapértelmezés)
```

Három dolog, ami könnyen félrevisz:

1. **Azonosítót vár, nem megjelenített nevet.** A `model: Opus 4.8` alak nem érvényes; `claude-opus-5` / `claude-sonnet-5` kell.
2. **A modellválasztó UI címkéi nem a frontmatter-forma.** A Cursor felületén látható `claude-opus-5-thinking-high` / `gpt-5.6-sol-medium` stílusú slugok a *picker* nevei; a dokumentált frontmatter-alak az azonosító + `[effort=…]`. Claude-ból a slug-listán csak `-thinking-high` létezik, tehát a `-thinking-low` / `-thinking-medium` alakok érvénytelenek — pont az alacsony effortú agenteknél (fixerek, `test-runner`, `researcher`) hibáznának.
3. **Az érvénytelen érték NÉMA.** Ha az azonosítót a Cursor nem ismeri fel — vagy felismeri, de nincs hozzá jogosultság (admin letiltotta, a csomag nem tartalmazza, illetve legacy request-alapú csomagnál Max Mode kellene) —, akkor **hibaüzenet nélkül a szülő ágens modelljére esik vissza**. A tünet csak a viselkedésen látszik: pl. az `analyzer` látszólag fut, de nem Opus 5-ön.

Emiatt a `models.json` **`cursor` szekciójába mindig modell-azonosítót írj**; az effortot a telepítő fűzi hozzá (`install-helper.py` → `inject_cursor_agent`). Ugyanitt egy tier-eltérés: **Cursorban nincs Haiku**, ezért a `research_agent` a `default` Sonnet 5-öt kapja `low` efforton — ugyanaz a megoldás, mint Antigravityn a Flash-sel.
