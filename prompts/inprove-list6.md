# Teszt-terv keményítés — végrehajtási terv (két független rész)

> **Ez a dokumentum önhordó.** Üres kontextusban is végrehajtható. **Két, egymástól független
> munkát** követ nyomon, közös gyökérrel (a keret teszt-oldala gyenge modellen nem tart):
>
> | rész | mit | szakaszok |
> |---|---|---|
> | **A** | **A `03-write-plan` kettéhasítása** — `03a` kód-terv + `03b` teszt-terv, egy `plan.md`-be | 1–18 |
> | **B** | **„Az üres teszt zöld” — bizonyíték-keményítés** (`[CHECK]`-integritás, RED-bizonyíték, vacuous-test és szelektor kapu, forgalmi bizonyíték, artefaktum-frissesség, review-checklist mindkét ágon) | 20–33 |
>
> **A két rész NEM függ egymástól, és nem is szabad összecsatolni őket.** Az A a `03` fázisról
> szól, a B a `06`/`07` gépezetéről; egyik sem előfeltétele a másiknak, és **külön commitolhatók**.
> Ha csak az egyikre van idő, hajtsd végre azt teljesen — a fél-A és a fél-B rosszabb, mint az
> egyik kész. A B rész **nem** igényel új `plan.md`-mezőt, tehát az A vágási táblája (4. szakasz)
> tőle érintetlen.
>
> **Semmit nem kell kikövetkeztetni** — ha valami mégis hiányzik, az a terv hibája; írd bele.

> **Státusz:** mindkét rész jóváhagyott döntés, végrehajtásra vár.
> **A:** a vágás mibenlétéről (kód-fél / teszt-fél, egy `plan.md`) a felhasználó döntött.
> **B:** a felhasználó a **gépi utat** választotta (F1–F4 és F6–F9 determinisztikus checkek + F5 másodlagos
> prózai szabály) az „anti-stub szabály a promptba” úttal szemben.

---

## 0. Hogyan használd ezt a dokumentumot

0. **Válaszd ki, melyik részen dolgozol** (A vagy B — lásd a fejlécet), és **maradj benne**.
   Az A rész az 1–18., a B a 20–33. szakasz. A két rész teendő-számai nem ütköznek
   (`5.1`… vs. `22.1`…), tehát egy fájlban követhető mindkettő.
1. **Olvasd el a választott rész orientációját és döntéseit** — az A-nál az 1–4., a B-nél a
   20–21. szakaszt. Enélkül a teendők félreérthetők.
2. **A sorrend szerint haladj** (A: 17. szakasz · B: **32. szakasz** — a B teendői NEM
   számsorrendben futnak, az F7 az első), és keresd meg az **első kipipálatlan** teendőt.
3. **Egy teendő = egy lépés = egy verifikáció.** Minden pont után futtasd a hozzá tartozó
   ellenőrzést, és pipálj ebben a fájlban (`- [ ]` → `- [x]`).
4. **A repó KÉTNYELVŰ.** Minden prompt-szerkesztést **mindkét fán** (`-hu` és `-en`) át kell
   vezetni. A 17.2 szakasz zárókapui ezt mérik. Ha egy teendő csak a `-hu` fát nevezi meg, az
   `-en` párja **ugyanabban a teendőben** benne van — a szövege az `-en` fa stílusában.
5. **Ne kezdj kódot írni a 3. szakasz döntéseinek megkérdőjelezésével.** Ha a végrehajtás során
   valamelyik döntés tarthatatlannak bizonyul, **állj meg és kérdezz** — ne válassz magadtól
   másik szerkezetet: ez a terv több szomszédos fázis kontraktusát mozgatja.

---

# A. rész — A `03-write-plan` kettéhasítása (kód-terv + teszt-terv)

## 1. Orientáció — mi ez a repó, és mi mozdul

### 1.1 A rendszer

Ez a repó egy **spec-driven development (SDD) promptrendszer**. A `prompts/` mappa egy 10 fázisú
(`00`–`09`) AI-asszisztált fejlesztési ciklus fázis-receptjeit tartalmazza:

- **skillek** (`prompts/skills-hu/`, `prompts/skills-en/`) — egy fázis = egy prompt, amit a
  felhasználó slash-parancsként indít (`/bs-write-plan`);
- **ágensek** (`prompts/agents-hu/`, `prompts/agents-en/`) — specialista subagentek
  (`researcher`, `analyzer`, `reviewer`, `*-fixer`, `doc-sync-planner`);
- **közös blokkok** (`prompts/shared-hu/`, `prompts/shared-en/`) — build-time `INCLUDE`-olt
  szekciók (fix-módok, minőségi kapuk, útvonal-konvenció, commit-recept);
- **projekt-nyelvi tartalom** (`prompts/lang/hu/`, `prompts/lang/en/`, `prompts/lang/status-keys.json`);
- **determinisztikus kapuk** (`prompts/scripts/*.py`) — a gépiesen eldönthető ellenőrzések.

A ciklus fázisai: `00`-init · `01`-ciklusok · `02`-spec · **`03`-plan** · `04`-tasks ·
`05`-analyze · `06`-implement · `07`-validate · `08`-doc-sync · `09`-merge. Minden ciklus mappája
`specs/cycle-NN-<cycle-name>/`, a dokumentumai `spec.md` → `plan.md` → `tasks.md`, státusz-mezőkkel
összekapcsolva (`<status:ready_for_plan>` → `<status:ready_for_tasks>` → `<status:ready_for_implement>`).

### 1.2 A két nyelvi tengely (LG2/LG5)

- A **prompt-nyelv** dönti el, melyik `-<lang>` fából telepít az `install.sh`. A két fa
  **teljesen szimmetrikus**: azonos fájlnevek, azonos szerkezet, nincs suffix nélküli fa.
- A **projekt-nyelv** azt, hogy a `lang/<L>/` blokkok és a `status-keys.json` melyik szelete
  kerül be. Mindkettő **build-time** dől el és bedrótozódik.
- Az artefaktum-**szekciónevek, mezőnevek és státusz-értékek** a promptokban **nem literálok**,
  hanem `<sec:…>` / `<field:…>` / `<status:…>` tokenek, amiket a telepítő old fel a
  `prompts/lang/status-keys.json`-ból. **Új szekciónév/mező/státusz → előbb kulcs a JSON-ba
  (mindkét nyelvi szeletbe), csak utána token a promptban.**
- A **user-facing mondatok és artefaktum-sablonok** a `lang/<L>/<fájl>.md` horgonyaiban élnek,
  `<!-- INCLUDE:lang/<fájl>.md#<horgony> -->` markerrel behivatkozva.

### 1.3 Kötelező kézi kapuk (nincs CI, nincs pre-commit hook)

```bash
python3 prompts/scripts/lang-parity-check.py            # nyelvi paritás (default mód)
python3 prompts/scripts/lang-parity-check.py --strict    # PR zárás előtt (fájlhalmaz-paritás is)
python3 prompts/scripts/sync-gemini-agents.py --check     # a gemini agent.json tükrök
python3 prompts/scripts/sync-gemini-agents.py             # ... és a regenerálásuk (írás)
```

A telepítő ezt a két scriptet **szándékosan nem másolja** a célprojektbe: repó-karbantartó eszközök.

### 1.4 Amit ez a terv NEM érint (kimondott nem-célok)

- **Az `05-analyze` önjavító hurka nem tud a hasításról.** Marad **egy** `plan-fixer`, egy
  `plan.md`, és a Must Fix tételek célfázis-jelölése marad `03-plan`. Indok: a fixer a *dokumentumot*
  javítja, nem a fázist futtatja újra; egy `03a`/`03b` célfázis-hasítás a `05` teljes
  gépezetét (lang-blokkok, riport-sablon, eszkalációs ágak) mozgatná, nulla haszonnal.
- **A `bs-manual-test-plan` (MT) változatlan.** Ugyanabból a `plan.md`-ből szerel össze.
- **A `06`/`07`/`08`/`09` fázis változatlan**, egyetlen kivétellel: a `07` VD5 eszkalációs
  záró-üzenete melyik parancsra irányít vissza (13.4 teendő).
- **A `04` belépő kapuja (EG1) változatlan** — továbbra is a teljes `--plan-only` módot futtatja.
  Ez a terv legfontosabb biztonsági tulajdonsága: a `04` felé menő kontraktus **nem gyengül**.
- **Nem vezetünk be új determinisztikus checket.** A `--plan-code-only` mód a **meglévő** checkek
  szűkebb halmazát futtatja (11. szakasz).
- **A `bs-quick-flow` (egyszerűsített flow) változatlan.** Ellenőrizve: nem hívja a `03`-at, csak
  azt mondja ki, hogy ebben a flow-ban nincs `plan.md`, és hogy a `plan-fixer` `plan.md`-t
  feltételez — mindkét állítás a hasítás után is igaz.
- **A `07` és a `validate-gate-check.py` plan-státusz kapuja változatlan.** Ellenőrizve: mindkettő
  az **elfogadható** státuszokat sorolja (`<status:ready_for_tasks>` / `<status:done>`), tehát az
  új közbenső státuszt nem kell felvenni — egy `<status:ready_for_test_plan>` állapotú planre a
  `07` helyesen bukik meg (a ciklus tervezése nem zárult le).

---

## 2. A probléma és a mérés

### 2.1 A panasz

A `03` fázis által termelt **teszt-terv** minősége tartósan nem elégséges — gyenge modellen
(Gemini Flash-tier) különösen. A keret eddig **szabályokkal** válaszolt erre, három körben:

| Kör | Mit adott | Mi maradt |
|---|---|---|
| `TS1–TS6` (7/f) | per-teszteset `TS-NN` szerkezet, hat determinisztikus check | formailag hibátlan blokkok, bennük **egyetlen** kérés-válasz pár |
| `TD0–TD7` (7/h) | **generáló** recept (`shared-*/test-scenario-design.md`), dimenzió-leltár, megfigyelési négyes | a recept megvan, de a fázis végén, a legkevesebb figyelemnél fut le |
| `TS7`/`TA1`/`WY1` (7/i) | a hiányzó szekció mérése kitöltött struktúrán, tesztfájl-adatlap, cél-mondat | a szekciót a fázis akkor sem nyitja meg mindig |

A negyedik kör **nem lehet több szabály**: a szabályok megvannak, és a kapu is megfogná őket.

### 2.2 A mérés (2026-09-02, `feature/test-target-and-report-hardening` branch)

```bash
wc -l prompts/skills-hu/*.md | sort -n
```

| skill | sor |
|---|---|
| **`03-write-plan.md`** | **1042** |
| `07-validate.md` | 792 |
| `08-doc-sync.md` | 748 |
| `05-analyze.md` | 631 |
| `01-add-cycles.md` | 418 |
| `02-write-spec.md` | 372 |
| `06-implement.md` | 331 |
| `04-write-tasks.md` | 323 |

Ehhez **build-time** hozzáadódik: `shared-hu/test-scenario-design.md` (96 sor),
`shared-hu/quality-check-plan.md` (88 sor), `shared-hu/fix-mode-plan.md` (41),
`shared-hu/input-from-prev.md` (44), `shared-hu/artifact-voice.md` (28),
`shared-hu/path-format.md` (30), `shared-hu/phase-commit.md` (59),
`shared-hu/conventions-change.md` (26), `shared-hu/context-check.md` (27) — a telepített
`SKILL.md` így **~1400 sor**, benne egy ~470 soros sablon-példával.

**A `03` a keret legnagyobb skillje, a `04`-nek több mint háromszorosa.**

### 2.3 Miért a hasítás a helyes válasz (és nem újabb szabály)

Négy érv, ami túlmutat a token-számon:

1. **A `TS7`-vakfolt szerkezetileg megszűnik.** A cycle-30-as bukás az volt, hogy a fázis a
   `<sec:plan_test_scenarios>` szekciót **meg sem nyitotta** — a checkeknek nem volt mit mérniük.
   Ha egy fázisnak *a teszt-szekció az egyetlen leszállítandója*, akkor a „nem nyitottam meg”
   nem állapot: a fázis kimenete maga a szekció.
2. **A teszt-terv lezárt bemenetről indul.** Ma a modell a teszteket **közben** tervezi, miközben
   a `[P-…]` bejegyzések, a fájlútvonalak és a koordináták még alakulnak — ezért lesz a `TS-NN`
   általános, a `TA1` adatlap pedig találgatás. A `03b` bemenete egy **kész** kód-terv konkrét
   azonosítókkal és fájlnevekkel.
3. **Két külön záró checklist, két külön kapu.** Ma egyetlen minőségellenőrzési lista végén ül a
   teszt-oldal — pont ott, ahol a modell figyelme a legkevesebb.
4. **A `7/j` elve újra alkalmazható.** A `03b` **fogadó** fázis: a saját belépő kapujában
   lefuttatja a kód-fél kapuját (`--plan-code-only`), tehát a kód-fél önbevallását is ellenőrzi
   valaki, akinek érdeke, hogy jó bemenetet kapjon.

### 2.4 A vágás már a fájlban van (ezért kis szerkezeti kockázat)

- A sablon a `<sec:testing_strategy>`-nál fordul át kód-tervből teszt-tervbe, és a teszt-oldal a
  `<sec:e2e_tests>` végéig tart — **~335 sor a sablonból tisztán teszt**.
- A `## Validációs ciklusok` **már három körre** van osztva, és az első kettő határa pontosan
  `<sec:planned_changes>` után / `<sec:test_specification>` után.
- A mechanikus kapu checkjei is szétválnak: `check_planned_change_purpose`, `check_env_coordinates`,
  `check_config_lifecycle` (kód-fél) vs. `check_test_scenarios`, `check_test_artifact_datasheet`,
  `check_test_ids`, `check_run_table_phase`, `check_spec_coverage_scenarios`, `check_ts_http_blocks`
  (teszt-fél).

---

## 3. Lezárt döntések

- [x] **D1 — Két skill, egy `plan.md`.** A `03` két fázisra hasad:
  - `prompts/skills-{hu,en}/03a-write-code-plan.md` — frontmatter `name: bs-write-code-plan`
  - `prompts/skills-{hu,en}/03b-write-test-plan.md` — frontmatter `name: bs-write-test-plan`

  Mindkettő **ugyanabba a `specs/cycle-NN-<cycle-name>/plan.md`** fájlba ír, a maga szekcióiba.
  A `03-write-plan.md` fájl **törlődik** (nem marad kompatibilitási wrapper — a keretet
  ciklusonként telepítik újra, és egy „is jó” duplikátum a leggyengébb modellt terelné rossz felé).

  _Fájlnév-konvenció:_ a telepítő a **fájl stemjéből** képzi a skill-mappát (`bs-<stem>` →
  `bs-03a-write-code-plan/SKILL.md`), az **invokálható név** viszont a frontmatter `name` mezője
  (`/bs-write-code-plan`). Ez a mai `03-write-plan.md` + `name: bs-write-plan` mintát követi.

- [x] **D2 — Új közbenső státusz.** `prompts/lang/status-keys.json` `status` szótár:
  `"ready_for_test_plan"` → `hu`: `"Teszt-tervezésre kész"`, `en`: `"Ready for test planning"`.
  A státusz-lánc: `<status:ready_for_plan>` (spec) → **`<status:ready_for_test_plan>`** (03a zárja) →
  `<status:ready_for_tasks>` (03b zárja) → `<status:ready_for_implement>` (04 zárja).

- [x] **D3 — A `03b` a MEGLÉVŐ `--plan-only` kapuval zár.** Nincs `--plan-test-only`. Így a
  teljes plan-kapu tartalma, a `04` EG1 belépő kapuja és a `05` hurok **változatlan** — a
  script-módosítás **tisztán additív**.

- [x] **D4 — A `03a` új, szűkített kapuval zár:** `analyze-gate-check.py … --plan-code-only`.
  A checkhalmazt a 11.2 szakasz **tételesen** felsorolja. A mód a `--plan-only` szemantikáját
  örökli (a `tasks.md`-t üresként kezeli), és **nem** futtat egyetlen teszt-oldali checket sem.

- [x] **D5 — A `03b` belépő kapuja lefuttatja a `--plan-code-only`-t (a `7/j`/EG1 elv).**
  Nem elég elolvasni a `<status:ready_for_test_plan>` mezőt: a `03a` írta be magának.
  Bukásnál a `03b` **STOP**, és visszairányít a `/bs-write-code-plan`-ra — a kód-felet **nem
  javítja** (14.2 alatt kimondott kivétellel).

- [x] **D6 — Két kapu-bélyeg a `plan.md` fejlécében.** Új mező-kulcs:
  `"f_gate_code"` → `hu`: `"Kód-terv kapu"`, `en`: `"Code-plan gate"`.
  - a `03a` a `**<field:f_gate_code>:**` sorba írja az `analyze-gate-check --plan-code-only — PASS, 0 Must Fix (ÉÉÉÉ-HH-NN)` bélyeget;
  - a `03b` a meglévő `**<field:f_gate>:**` sorba a `analyze-gate-check --plan-only — …` bélyeget (változatlan alak).

  A `03b` a `f_gate_code` sort **nem írja át** — a két bélyeg együtt a fázis-lánc nyoma.

- [x] **D7 — A minőségi kapu hasad, a fixer nem.** `prompts/shared-{hu,en}/quality-check-plan.md`
  → `quality-check-plan-code.md` + `quality-check-plan-test.md`. A `03a` a `-code`-ot, a `03b` a
  `-test`-et emeli be; az `agents-{hu,en}/plan-fixer.md` **mindkettőt** (egy fixer, egy dokumentum).
  A `prompts/lang/{hu,en}/quality-check-plan.md` `TP2-lezarasi-kapu` horgonya szintén két horgonyra
  hasad: `TP2-code` + `TP2-test` (a pontok szétosztása a 8.3 teendőben).

- [x] **D8 — Négy közös blokk kiemelése** (mindkét félnek kell, duplikáció nélkül).
  Új fájlok `prompts/shared-hu/` **és** `prompts/shared-en/` alatt:
  | fájl | mit visz | forrás a mai `03`-ban |
  |---|---|---|
  | `dereferencing.md` | Hivatkozás-feloldás (a bemenet szintje nem a plan szintje) | `## Hivatkozás-feloldás (dereferencing) …` szekció |
  | `spec-artifact-transfer.md` | `KX3` — kidolgozott spec-artefaktum szó szerinti átemelése | `## Kidolgozott spec-artefaktum átemelése …` szekció |
  | `plan-section-ids.md` | `PID1` — stabil `[P-…]` szekció-azonosítók | `### 🔴 Stabil szekció-azonosítók (PID1) …` szekció |
  | `plan-self-contained.md` | a `plan.md` önhordósága (a fogyasztó-tábla + az önteszt) | `### 🔴 A `plan.md` ÖNHORDÓ …` szekció |

  Mindegyiket **a `03a` és a `03b` is** beemeli; a `dereferencing.md`-t és a
  `spec-artifact-transfer.md`-t a `plan-fixer` is (a mai `quality-check-plan.md` beemelése
  mellett — a fixernek eddig is szüksége volt rájuk).

- [x] **D9 — `test-scenario-design.md` (TD0–TD7) → a `03b`-be.** A `02-write-spec` beemelése
  **változatlan** (ott a `TD0` spec-hatóköre él); a `03`-ból a `03b`-be kerül. A `plan-fixer`
  beemelése változatlan.

- [x] **D10 — Egy `plan-questions.md`, folytonos `Knn` számozás.** A `03a` hozza létre, a `03b`
  **folytatja** (a meglévő bejegyzéseket nem módosítja, nem számozza újra). A kötelező **`K01` =
  E2E teszt stratégia** kérdés a **`03a`-ban** marad: a `<sec:e2e_infrastructure>` szintje (valódi
  stack / részleges mock / teljes mock) a környezet-felkészítés döntése, és a `03a`
  `<sec:environment_coords>` szekciója ebből él. A `03b` a lezárt `K01`-ből dolgozik, és ha a
  döntés a teszt-tervezés közben tarthatatlannak bizonyul, **új `Knn`-t** vesz fel.

- [x] **D11 — `cycle-status.py`: a plan-fázis két sorra hasad.** „Kód-terv (plan.md)” és
  „Teszt-terv (plan.md)” — mindkettő ugyanabból a státusz-mezőből számol (12.5 teendő).

- [x] **D12 — Az `05` célfázis-jelölése marad `03-plan`.** Lásd 1.4.

---

## 4. A vágás pontos táblája

### 4.1 A `plan.md` szekciói

| Szekció (token) | Ki írja | Megjegyzés |
|---|---|---|
| fejléc: `<field:f_status>` | 03a hozza létre, 03b lépteti | egy státusz-mező |
| fejléc: `<field:f_gate_code>` | **03a** | D6 |
| fejléc: `<field:f_gate>` | **03b** | D6 |
| `<sec:goal_and_approach>` | **03a** | a `<sec:out_of_scope>` kimondás is itt |
| `<sec:affected_components>` | **03a** | |
| `<sec:environment_coords>` (+ `<field:f_target_env>`, `<sec:components_endpoints>`, `<sec:rest_calls_examples>`, `<sec:test_api_users>`, `<sec:other_parameters>`, `<sec:network_access_prereqs>`) | **03a** | KO1 / EV1 — a `03b` ezekből **literál értékeket másol**, nem hivatkozik rájuk |
| `<sec:planned_changes>` (+ `<field:f_purpose>`, WY1) | **03a** | a `03b` által kért ÚJ tesztfájlok/fixture-ök felvétele: 4.3 |
| `<sec:new_dependencies>` | **03a** | |
| `<sec:config_build_changes>` (+ `<sec:config_lifecycle>`, KF1) | **03a** | |
| `<sec:schema_artifacts>` | **03a** | a schema-artifact review-hurok is (03a) |
| `<sec:reverse_coverage>` (SC1) | **03a** hozza létre, **03b bővíti** | 4.3 |
| `<sec:risks_and_decisions>` | **03a** hozza létre, **03b bővíthet** | 4.3 |
| `<sec:testing_strategy>` | **03b** | |
| `<sec:plan_test_scenarios>` (`TS-NN`, TS1–TS8) | **03b** | a `03b` fő leszállítandója |
| `<sec:machine_run_table>` (TP4, PH1, EV2–EV5) | **03b** | |
| `<sec:e2e_infrastructure>` (TP3 bootstrapping) | **03b** | a `K01` döntésére épül |
| `<sec:regression_impact>` | **03b** | |
| `<sec:test_specification>` (TI1, `<sec:spec_coverage>`, Lifecycle, TA1, `<sec:unit_tests>`, `<sec:integration_tests>`, `<sec:e2e_tests>`) | **03b** | |
| `<sec:execution_order>` | **03b** | mindkét fél ismeretében rendezhető (RED a GREEN előtt) |
| `<sec:verification_strategy>` | **03b** | célzott teszt-parancsok |

### 4.2 A prózai (nem sablon) szekciók

| Mai szekció a `03`-ban | 03a | 03b | mód |
|---|---|---|---|
| `Cheat sheet` | ✔ | ✔ | mindkettő **saját**, a maga szekcióira szűkítve |
| `Feladatod` + „ne ismételd a spec-et” hatókör-guard | ✔ | ✔ | mindkettő saját |
| `🔴 A plan.md ÖNHORDÓ` | ✔ | ✔ | **közös blokk** (D8: `plan-self-contained.md`) |
| `<field:f_prerequisite>` | ✔ | ✔ | 03a: spec-státusz + `conventions.md` + munkafa + CD1; 03b: plan-státusz + **`--plan-code-only` futtatás** (D5) |
| `Folytatás megszakított futás után` | ✔ | ✔ | mindkettő saját (a maga szekcióira) |
| `Nyitott kérdések kezelése` + `plan-questions.md` struktúra | ✔ | ✔ | 03a hozza létre a fájlt, 03b folytatja (D10); a `K01`-blokk csak a 03a-ban |
| `Hivatkozás-feloldás (dereferencing)` | ✔ | ✔ | **közös blokk** (D8) |
| `conventions-change.md` INCLUDE (GC1) | ✔ | — | a `conventions.md`-változás terv-oldali |
| `KX3` kidolgozott artefaktum-átemelés | ✔ | ✔ | **közös blokk** (D8) |
| `Fázisok közötti átadás (IP1)` + `input-from-prev.md` | ✔ | ✔ | `plan-input-from-prev.md`-t a **03a** olvassa és zárja le; a kimenő `tasks-`/`validate-input-from-prev.md`-be **mindkettő** írhat |
| `Ciklus design input (CD1)` | ✔ | — | a technikai/koordináta-tartalom a 03a bemenete |
| `Kontextus betöltési szabályok` | ✔ | ✔ | 4.4 |
| `artifact-voice.md` INCLUDE (AV1) | ✔ | ✔ | mindkettő |
| `Stabil szekció-azonosítók (PID1)` | ✔ | ✔ | **közös blokk** (D8) |
| `Plan struktúra` sablon | ✔ | ✔ | **a sablon hasad** a 4.1 tábla szerint; mindkettő csak a **saját** szekcióit sablonozza, és egy soros „ezt a másik fázis írja” jelöléssel utal a többire |
| `Schema Artifaktumok kezelése` | ✔ | — | |
| `Validációs ciklusok 1.` (planned_changes után) | ✔ | — | |
| `Validációs ciklusok 2.` (test_specification után) | — | ✔ | |
| `Validációs ciklusok 3.` (execution_order után) | — | ✔ | |
| `Spec kritika` (hiány + KX-tükör koordináta-visszajelzés) | ✔ | ✔ | 03a: a teljes lista; 03b: **csak** a spec teszt-szekciójára és a `DoD-NN`-ekre szűkítve (hiányzó/ellentmondó teszteset → vissza a 02-be) |
| `Megállási szabályok` | ✔ | ✔ | mindkettő saját listája; a `TP2` pont a maga felére |
| `quality-check-plan*.md` INCLUDE | `-code` | `-test` | D7 |
| `Státusz kezelés` + `Mechanikus kapu (M)` | ✔ | ✔ | 03a: `--plan-code-only` + `f_gate_code`; 03b: `--plan-only` + `f_gate` (a mai szöveg) |
| `phase-commit.md` INCLUDE | ✔ | ✔ | `<FÁZIS-TAG>`: `03a-code-plan` ill. `03b-test-plan` |
| `fix-mode-plan.md` INCLUDE | — | — | **egyik skillbe sem** kerül: a fix-mód a `plan-fixer` wrapperben él (D12), és a mai `03` is csak azért hordozta, hogy a wrapper beemelhesse |

> **Fontos:** a mai `03-write-plan.md` a `fix-mode-plan.md`-t a fájl **végén** emeli be. Mivel a
> `plan-fixer.md` wrapper **ugyanezt a shared fájlt** emeli be közvetlenül, a hasítás után egyik
> skill sem kell hozzá. A `fix-mode-plan.md` tartalma **változatlan** (egy fixer, egy dokumentum).

### 4.3 A három átlapoló pont — explicit szabállyal

Ez a hasítás legkényesebb része. Mindhárom pontot **ki kell írni mindkét skillbe**:

1. **`<sec:reverse_coverage>` (SC1) — 03a hozza létre, 03b append-only bővíti.**
   A `PID1` szerint a teszt-szekciók is kapnak `[P-…]` azonosítót, tehát a tábla mindkét fél
   képességeit tartalmazza. Szabály: a `03b` **csak új sort ad**, meglévő sort nem módosít és nem
   töröl; ha egy meglévő sort hibásnak talál, az `Knn` kérdés vagy visszairányítás a `03a`-ra.

2. **A `03b` által igényelt ÚJ FÁJL felvétele a `<sec:planned_changes>`-ba.**
   A `TA1` adatlap megkövetel minden fixture/mock/tesztadat útvonalát, és kimondja, hogy ami még
   nem létezik, az **új fájl** — tehát a `<sec:planned_changes>`-ban is szerepelnie kell.
   Szabály: a `03b` **hozzáadhat** `<sec:planned_changes>` bejegyzést, de **kizárólag
   teszt-artefaktumra** (tesztfájl, fixture, mock, seed-adat, teszt-helper) — új `[P-…]` ID-val, a
   kötelező `<field:f_purpose>` sorral. Termelő (nem-teszt) kódra **soha**: az visszairányítás a
   `03a`-ra. A `03b` a meglévő `[P-…]` bejegyzéseket **nem szerkeszti**.

3. **`<sec:risks_and_decisions>` — 03b bővíthet.** Teszt-oldali kockázat (flaky forgatókönyv,
   osztott környezet, hosszú futás) ide kerül, új bekezdésként. Meglévő bekezdést nem ír át.

### 4.4 Kontextus betöltési szabályok — ki mit olvas

**`03a` (kód-terv):**
- `spec.md` (teljes), `conventions.md`, `cycle-design-input.md` (CD1), `plan-input-from-prev.md` (IP1),
  `plan-questions.md`;
- `specs/test-conventions.md` — **a 0. blokk (koordináták) és az 1. szekció (receptek)**;
- forrásfájl-azonosítás: `researcher` subagent **Mód A** (`agents/researcher.md`);
- korábbi ciklus `plan.md`-je: csak a `TP3/a` kivételeknél, `researcher` Mód B-vel, literál értékekre.

**`03b` (teszt-terv):**
- **a `plan.md` kód-fele — kötelező, ez a fő bemenet** (`<sec:environment_coords>`,
  `<sec:planned_changes>`, `<sec:config_lifecycle>`, `<sec:schema_artifacts>`, `<sec:reverse_coverage>`);
- `spec.md` — **a `<sec:test_specification>` szekció és a `<sec:definition_of_done>`** (a `TS7`
  konverzió forrása). A spec többi része nem kell;
- `conventions.md` (teszt-eszközök, riport-artefaktumok), `plan-questions.md` (a `K01` döntése);
- `specs/test-conventions.md` — **a 2. és 3. szekció** (minden körben szükséges lokális ill.
  integrációs/E2E tételek) **és** az 1. szekció azon receptjei, amelyek a bootstrappinghez kellenek;
- `researcher` **Mód B** csak akkor, ha egy meglévő tesztfájl tényleges hívásláncát kell literálisan
  kinyerni (a `03a` már felderítette a koordinátákat).

> **A `03b` NEM olvassa újra a kódbázist forrásfájl-azonosítás céljából** — azt a `03a` elvégezte,
> és az eredménye a `<sec:planned_changes>`-ban van. Ez a `03b` kontextus-fegyelme.

---

## 5. Előkészítés

- [ ] **5.1 — Branch.** A munka a `feature/split-plan-phase` branchen fut, `main`-ről ágazva.
  Ha a jelenlegi `feature/test-target-and-report-hardening` branchen van commitálatlan vagy
  be nem olvasztott munka, azt **előbb zárd le** (a felhasználóval egyeztetve) — ez a terv
  ugyanazokat a fájlokat mozgatja.
  ```bash
  git status --short && git branch --show-current
  ```

- [ ] **5.2 — Kiinduló mérés rögzítése.** Írd ki a mai számot, hogy a 16.5 elfogadási kritérium
  mérhető legyen:
  ```bash
  wc -l prompts/skills-hu/03-write-plan.md prompts/skills-en/03-write-plan.md \
        prompts/shared-hu/quality-check-plan.md prompts/lang/hu/quality-check-plan.md
  ```

- [ ] **5.3 — Kapuk zöldek a kezdés előtt** (hogy tudjuk, mit rontottunk el mi):
  ```bash
  python3 prompts/scripts/lang-parity-check.py
  python3 prompts/scripts/sync-gemini-agents.py --check
  ```
  Ha már induláskor WARN/ERROR van, **írd ide, mi volt** — különben a végén nem lesz eldönthető,
  hogy a mi hibánk-e.

---

## 6. Nyelvi szótár és projekt-nyelvi blokkok

- [ ] **6.1 — Új státusz-kulcs** (D2). `prompts/lang/status-keys.json`, a `hu.status` **és** az
  `en.status` szótárba, a `ready_for_plan` és a `ready_for_tasks` közé:
  - `hu`: `"ready_for_test_plan": "Teszt-tervezésre kész"`
  - `en`: `"ready_for_test_plan": "Ready for test planning"`

  ```bash
  python3 -c "import json;d=json.load(open('prompts/lang/status-keys.json'));print(d['hu']['status']['ready_for_test_plan'], '|', d['en']['status']['ready_for_test_plan'])"
  ```

- [ ] **6.2 — Új mező-kulcs** (D6). Ugyanabban a fájlban, a `hu.fields` és `en.fields` szótárba,
  a `f_gate` mellé:
  - `hu`: `"f_gate_code": "Kód-terv kapu"`
  - `en`: `"f_gate_code": "Code-plan gate"`

- [ ] **6.3 — Projekt-nyelvi blokkok hasítása.** A mai `prompts/lang/hu/03-write-plan.md` és
  `prompts/lang/en/03-write-plan.md` **három** horgonyt tartalmaz: `plan-questions-struktura`,
  `statusz-megerosites`, `zaro-uzenet`. Hozz létre helyettük **négy** fájlt:

  | új fájl | horgonyok |
  |---|---|
  | `prompts/lang/{hu,en}/03a-write-code-plan.md` | `plan-questions-struktura` (változatlan tartalom) · `statusz-megerosites` (a **kód-terv** lezárására, `<status:ready_for_test_plan>`-t említve) · `zaro-uzenet` (a `/bs-write-test-plan` indító parancsával) |
  | `prompts/lang/{hu,en}/03b-write-test-plan.md` | `statusz-megerosites` (a teszt-terv lezárására, `<status:ready_for_tasks>`) · `zaro-uzenet` (a `/bs-write-tasks` indító parancsával — a mai `03` záró-üzenete) |

  A vezető HTML-komment fejlécet **másold** a mai fájl mintájára (a horgony-magyarázattal), a
  fájlnevet és a marker-alakot átírva. A mai `lang/{hu,en}/03-write-plan.md` **törlődik**.

  > **Token vagy literál a `lang/` blokkokban?** Mindkettő működik (a telepítő a beemelés
  > **után** oldja fel a tokeneket): a mai `lang/hu/03-write-plan.md` literálisan írja
  > („`Task írásra kész`”), a `lang/hu/quality-check-plan.md` viszont tokent használ
  > (`<status:phase_implement>`). **Az új blokkokban használj tokent**
  > (`<status:ready_for_test_plan>`) — így a magyar és az angol lang-fájl ugyanazt a kulcsot
  > hivatkozza, és egy szótár-átnevezés nem hagy némán elavult literált a szövegben.

  A `03a` `zaro-uzenet` horgonyának magyar tartalma (minta — a szövegezés a mai stílust követi):
  ```
  > *"A kód-terv kész. Folytathatjuk a teszt-tervvel. Az új fázis megkezdése előtt
  > mindenképpen futtass egy `/clear` parancsot a kontextus kiürítéséhez, majd használd
  > ezt a parancsot:*
  > ```
  > /bs-write-test-plan input: @specs/cycle-NN-<cycle-name>/plan.md
  > ```"*
  ```

- [ ] **6.4 — A `02` záró-üzenete átirányítva.** `prompts/lang/{hu,en}/02-write-spec.md`:
  a `/bs-write-plan input: …` sor → `/bs-write-code-plan input: …`.
  ```bash
  grep -rn "bs-write-plan" prompts/lang/    # 6.3 + 6.4 után NULLA találat legyen
  ```

---

## 7. Az új közös blokkok (D8)

Négy blokk, **mindkét** nyelvi fán (`shared-hu/` és `shared-en/`). Mindegyik fájl első sora egy
`<!-- Forrás-jegyzet: … -->` komment a mai `shared-hu/quality-check-plan.md` mintájára, amely
megnevezi, **kik emelik be** (egy helyen szerkeszd).

- [ ] **7.1 — `shared-{hu,en}/plan-self-contained.md`.** A mai `03` `### 🔴 A `plan.md` ÖNHORDÓ —
  ez a fázis legfontosabb szabálya` szekciója **szó szerint**, egyetlen változtatással: a
  „Fogyasztó / Mit olvas / Mit NEM lát” tábla kapjon egy negyedik sort:
  `| `03b-write-test-plan` | a `plan.md` **kód-felét** + a spec teszt-szekcióját és `DoD`-ját | a kódbázist forrásfájl-azonosítás céljából |`
  Beemeli: `03a`, `03b`.

- [ ] **7.2 — `shared-{hu,en}/dereferencing.md`.** A mai `## Hivatkozás-feloldás (dereferencing)
  — a bemenet szintje NEM a plan szintje` szekció **szó szerint** (a táblával, a
  token-hatékonyság-listával és a „hurok bezárása” záró blokkal együtt).
  Beemeli: `03a`, `03b`, `plan-fixer`.

- [ ] **7.3 — `shared-{hu,en}/spec-artifact-transfer.md`.** A mai `## Kidolgozott spec-artefaktum
  átemelése — szó szerint, csonkítás nélkül (KX3)` szekció **szó szerint** (a két táblával, a
  „szabad/tilos” listákkal és a „három félreérthető szabály” záró blokkal).
  Beemeli: `03a`, `03b`, `plan-fixer`.

- [ ] **7.4 — `shared-{hu,en}/plan-section-ids.md`.** A mai `### 🔴 Stabil szekció-azonosítók
  (PID1) — a tasks.md ezekre hivatkozik` szekció **szó szerint** (a kódblokkal és a hét soros
  szabály-táblával), plusz **egy új sor** a táblába:
  `| **Ki adja ki** | A `<sec:planned_changes>` és a nem-teszt szekciók ID-jait a `03a`, a teszt-szekciókét a `03b`. A `03b` **soha nem nevez át és nem töröl** meglévő ID-t. |`
  Beemeli: `03a`, `03b`.

- [ ] **7.5 — Paritás-ellenőrzés a négy új blokkra.**
  ```bash
  python3 prompts/scripts/lang-parity-check.py
  ```

---

## 8. A minőségi kapu hasítása (D7)

- [ ] **8.1 — `shared-{hu,en}/quality-check-plan-code.md`.** A mai `quality-check-plan.md`
  `## Minőségellenőrzés — plan lezárása előtt` listájából **ezek a pontok** kerülnek ide
  (a felsorolás sorrendjében, szó szerint):
  - `🔴 ÖNHORDÓSÁG-LELTÁR` (a 10 soros tábla) — a 10. sor (regressziós érintettség) **kimarad**, az a teszt-fél
  - `🔴 <sec:environment_coords> szekció kész? (KO1)`
  - `Artefaktum-hang (AV1)?`
  - `🔴 Eldöntetlen alternatíva tilalma`
  - `Hivatkozott script/fájl létezik vagy tervezve van?` — a „Belépési pont egyezése” alponttal
  - `Kereszt-dokumentum konzisztencia`
  - `docs-generated/ nincs a tervezett módosítások közt? (DS4)`
  - `Osztott környezetet érintő destruktív művelet teljes?`
  - `🔴 Minden [P-…] bejegyzés megmondja a CÉLT? (WY1)`
  - `Hivatkozás-feloldás megtörtént?`
  - `Nincs tiltott megfogalmazás?`
  - `Hiányzik még valami a plan-ből?` / `Van bármi, ami nem egyértelmű?`
  - `Minden érintett fájl szerepel a tervezett módosításokban?`
  - `Dokumentációk frissítése` · `Kommentek és docstringek`
  - `<!-- INCLUDE:shared/path-format.md -->`
  - `Szekció-ID-k (PID1)`
  - `Scope-kapu (SC1)`
  - `<sec:config_lifecycle> (KF1)`
  - `Horgony-verifikáció` · `Érték-józanság`
  - `A kapu-konfiguráció együtt mozog? (GC1)`
  - `A kidolgozott spec-artefaktumok CSONKÍTÁS NÉLKÜL jöttek át? (KX3)`
  - `A cycle-design-input.md feldolgozva? (CD1)`
  - `A plan-input-from-prev.md minden tétele lezárva? (IP1)`
  - `A plan-ből kihagyott, de értékes infó át lett adva? (IP1)`
  - `Minden szükséges schema artifact azonosítva…` · `Minden schema artifact státusza <status:reviewed>?`
  - `Adatbázis módosítások` (migráció/rollback)
  - `Constitution Check (SK4)`
  - **új pont:** `🔴 A kód-terv kapuja lefutott, és a nyoma bent van? (GS2/a)` — az
    `analyze-gate-check.py --plan-code-only` `0`-t adott, és a bélyeg a `**<field:f_gate_code>:**`
    sorban **és** a fázis-záró válaszban is ott van. Szövegezése a mai `GS2` pont mintájára,
    azzal a záró mondattal, hogy **a `03b` belépő kapuja ugyanezt újra lefuttatja (D5)**.
  - **új pont:** `🔴 A teszt-szekciókat NEM te írod.` — a `03a` nem nyit
    `<sec:testing_strategy>` / `<sec:plan_test_scenarios>` / `<sec:machine_run_table>` /
    `<sec:test_specification>` szekciót, és nem ír `TS-NN` / `TC-NN` azonosítót. Ha a spec
    tesztesetei „kikéredzkednek”, az a `03b` bemenete — a `<sec:reverse_coverage>` sorát felveheted,
    a forgatókönyvet nem. **Indoklás a promptban:** a fél-kész teszt-szekció rosszabb az üresnél,
    mert a `03b` `TS7`-konverziója így egy már meglévő, hibás szerkezetet másol tovább.

  A záró blokk (`Ha bármelyikre nem teljesül…`) marad. A `## Lezárási kapu … (TP2)` szekció
  fejléce is ide kerül, a `TP2-code` horgonnyal (8.3).

- [ ] **8.2 — `shared-{hu,en}/quality-check-plan-test.md`.** A maradék pontok:
  - az `ÖNHORDÓSÁG-LELTÁR` **10. sora** (regressziós érintettség) — önálló pontként
  - `🔴 A tesztek a ciklus CÉL-KÖRNYEZETÉN futnak? (EV1–EV5)` — az `<field:f_target_env>` mező
    **létezését** a `03a` kapuja már mérte; itt a futtatási tábla `<field:f_environment>` oszlopa
    és a `TS-NN` hívások a tárgy
  - `🔴 Minden teszteset TS-NN forgatókönyvként ki van fejtve? (TS1–TS6)`
  - `🔴 REST-forgatókönyvnél van .http blokk is? (TS8)`
  - `🔴 A gépi tábla megmondja, melyik FÁZIS futtatja? (PH1)`
  - `🔴 Minden teszteset megmondja, MIT ellenőriz? (TD7)`
  - `🔴 A spec teszt-szekciójának szerkezete nem szivárgott át? (TS7)`
  - `🔴 A teszt-azonosítók a közös névteret követik? (TI1)`
  - `🔴 Minden tesztfájlnak van adatlapja? (TA1)`
  - `A végrehajtási sorrend valóban függőségek alapján rendezett?`
  - `A <sec:test_specification> szekció tartalmaz teszteseteket minden érintett komponenshez?`
  - `A tesztek futtathatók a plan-ből egyedül? (TP3)`
  - `A spec tesztesetei átjöttek? (TP1)`
  - `A plan önhordó a beemelt teszt-receptekre (TC1/a)?`
  - `Minden teszteset Elvárt kimenet oszlopa tartalmaz HTTP státuszt és errorCode-ot?`
  - `A unit tesztek a végrehajtási sorrendben az implementáció ELŐTT szerepelnek?`
  - `Ígért teszt ↔ teszteset ↔ végrehajtási sorrend konzisztencia`
  - `Önteszt:` (a „csak a plan.md-t és a tasks.md-t kapja meg” mondat) — **mindkét** fájlban
    szerepel, mert mindkét fázis lezárásának ez a mércéje
  - `<!-- INCLUDE:shared/path-format.md -->` — szintén mindkettőben (a teszt-szekciók útvonalai)
  - **új pont:** `🔴 A kód-felet NEM te írod át.` — a `03b` nem módosított meglévő
    `[P-…]` bejegyzést, `<sec:environment_coords>` értéket vagy `<sec:reverse_coverage>` sort;
    ami a kód-tervben hibás, az `Knn` kérdés vagy visszairányítás a `/bs-write-code-plan`-ra.
    A megengedett három bővítés (4.3) tételesen felsorolva.
  - **új pont:** `🔴 A mechanikus kapu (teljes plan) lefutott? (GS2)` — a mai `GS2` pont
    változatlanul (`--plan-only`, `f_gate`, a `04` EG1-jére hivatkozva).

  Plusz a `## Lezárási kapu … (TP2)` szekció a `TP2-test` horgonnyal (8.3), és a záró
  „Miért kapu ez, és nem checklist-sor” magyarázat (az a teszt-oldalról szól).

- [ ] **8.3 — `lang/{hu,en}/quality-check-plan.md` horgony-hasítás.** A mai
  `TP2-lezarasi-kapu` horgony helyett **kettő**:
  - `TP2-code`: az `1/b` (WY1), `6` (belépési pont — a kód-oldali fele: a `<sec:planned_changes>`
    új fájljai), `7/b` (KO1), `8/c` (GC1), `8/b` (KX3), `9` (SC1), `10` (horgony-verifikáció),
    `11` (érték-józanság), `12` (PID1) pontok. **Számozd újra `1`-től**, a mai szöveget szó
    szerint megtartva (a pont-azonosítókat — WY1, KO1, GC1, KX3, SC1, PID1 — a szövegben hagyd).
  - `TP2-test`: az `1` (spec-lefedettség), `2` (test-conventions receptek), `3` (lépésenkénti
    kifejtés), `3/b` (TS7), `3/c` (TA1), `3/d` (TD7), `3/d/b` (TI1), `3/e` (TS8), `3/f` (PH1),
    `4` (hibaág), `5` (nincs hivatkozás a lépések helyén), `6` (belépési pont — a teszt-oldali
    fele: az `<sec:verification_strategy>` parancsa a tervezett tesztfájlt hívja), `7` (TP3),
    `8` (korábbi ciklus receptje) pontok. Szintén `1`-től számozva.
  - A mai fájl vezető HTML-komment fejléce marad; a horgony-lista frissül.

- [ ] **8.4 — A mai `shared-{hu,en}/quality-check-plan.md` törlése**, és minden beemelő hely
  átvezetése (8.5).

- [ ] **8.5 — Beemelő helyek.**
  - `skills-{hu,en}/03a-write-code-plan.md` → `<!-- INCLUDE:shared/quality-check-plan-code.md -->`
  - `skills-{hu,en}/03b-write-test-plan.md` → `<!-- INCLUDE:shared/quality-check-plan-test.md -->`
  - `agents-{hu,en}/plan-fixer.md` → **mindkettő**, egymás után, a mai egyetlen INCLUDE helyén;
    a fölötte lévő magyarázó mondat („Ez a 03 fázis minőségi kapuja…”) kapjon egy tagoló
    félmondatot: *„a kód-terv és a teszt-terv kapuja együtt — a fixer mindkét felet javíthatja”*.
  - `plan-fixer.md` `shared:` frontmatter-listája is frissül (a két új fájlra + a 7.2/7.3 blokkokra).
  ```bash
  grep -rn "quality-check-plan\.md" prompts/    # NULLA találat legyen (a -code/-test kivételével)
  ```

---

## 9. `03a-write-code-plan.md` (HU)

- [ ] **9.1 — Fájl létrehozása** `prompts/skills-hu/03a-write-code-plan.md` néven, a mai
  `03-write-plan.md`-ből **másolással és törléssel** (ne írd újra a megmaradó szövegeket —
  a `KX3`/`WY1`/`KO1` szövegek kalibrációs értéke a szó szerinti alakjukban van).
  Frontmatter:
  ```yaml
  ---
  phase: 03a
  name: bs-write-code-plan
  description: "<a 13.1 teendő descriptions.json-jából ide is bekerül a szöveg — a telepítő felülírja, de a repóban is legyen helyes>"
  prerequisites:
    - "specs/cycle-NN-<name>/spec.md státusz: <status:ready_for_plan>"
  output:
    - "specs/cycle-NN-<name>/plan.md státusz: <status:ready_for_test_plan> (a kód-terv szekciói)"
    - "specs/cycle-NN-<name>/plan-questions.md"
    - "specs/cycle-NN-<name>/tasks-input-from-prev.md és/vagy validate-input-from-prev.md (csak ha van átadandó infó, IP1)"
  prev: bs-write-spec
  next: bs-write-test-plan
  subagents:
    - "agents/researcher.md"
  scripts:
    - "scripts/analyze-gate-check.py"
  shared:
    - "shared/plan-self-contained.md"
    - "shared/dereferencing.md"
    - "shared/spec-artifact-transfer.md"
    - "shared/plan-section-ids.md"
    - "shared/conventions-change.md"
    - "shared/input-from-prev.md"
    - "shared/artifact-voice.md"
    - "shared/phase-commit.md"
    - "shared/quality-check-plan-code.md"
  ---
  ```

- [ ] **9.2 — Fázis-önmeghatározás.** A fájl elején a mai „Ez a folyamat **3. fázisa (0–9)**”
  sor helyére: `0-init · 1-ciklusok · 2-spec · **3a-kód-terv ←** · 3b-teszt-terv · 4-tasks · 5-analyze · 6-implement · 7-validate · 8-doc-sync · 9-merge`.
  Ugyanez a lista kerül a `03b`-be, ott a `3b`-nél a nyíllal.

- [ ] **9.3 — Cheat sheet átírása.** A mai 22 soros táblából maradnak a kód-oldali sorok
  (Előfeltétel, Nyitott kérdések, Kontextus, Szekció-ID, Scope-kapu, Környezet-koordináták,
  Önhordóság, Kapu-konfiguráció, Útvonalak, Csonkítás-mentesség, Hivatkozás-feloldás,
  Validációs ciklusok, Spec kritika, Lezárás). **Új sor a tábla elejére:**
  `| Hatókör | **Csak a kód-terv** — a teszt-szekciókat a `03b` írja (`/bs-write-test-plan`). Ide `TS-NN`, `TC-NN`, gépi futtatási tábla és tesztfájl-adatlap NEM kerül. |`
  A `Lezárás` sor a `--plan-code-only` kapura és a `<status:ready_for_test_plan>` státuszra hivatkozik.

- [ ] **9.4 — Törlendő szekciók** (a 4.1/4.2 tábla szerint): a sablonból a
  `<sec:testing_strategy>`-tól a `<sec:e2e_tests>` végéig **és** a `<sec:execution_order>` +
  `<sec:verification_strategy>` blokkok; a prózából a `Validációs ciklusok 2.` és `3.`, a
  `test-scenario-design.md` INCLUDE, a `fix-mode-plan.md` INCLUDE.
  A sablonban a törölt szekciók helyére **egy soros jelölés** kerül:
  ```
  _(A `<sec:testing_strategy>`-tól a `<sec:verification_strategy>`-ig tartó szekciókat a
  `03b-write-test-plan` fázis írja — ide ne kezdd el őket.)_
  ```

- [ ] **9.5 — `<sec:risks_and_decisions>` a sablon végére.** A mai sorrend szerint a
  `risks_and_decisions` az `execution_order`/`verification_strategy` **után** áll; a kód-terv
  sablonjában viszont ez lesz az utolsó szekció. A `03b` sablonjában az `execution_order` és a
  `verification_strategy` a `<sec:risks_and_decisions>` **elé** szúrandó — mondd ki a `03b`-ben,
  hogy a szekciók fizikai sorrendje a mai `plan.md` sorrendje marad, tehát a `03b` a maga
  szekcióit **a `<sec:risks_and_decisions>` elé** írja.

- [ ] **9.6 — `<field:f_prerequisite>` szekció.** A mai 0–4. pont marad (ciklus-beazonosítás,
  `conventions.md`, munkafa, spec-státusz, CD1).

- [ ] **9.7 — Nyitott kérdések.** A mai szekció marad, a `K01` E2E-blokkal együtt (D10).
  Új záró mondat: *a `03b` ugyanezt a fájlt folytatja a következő szabad `Knn` számmal — a
  bejegyzéseket ne számozd újra, és ne töröld.*

- [ ] **9.8 — `Spec kritika`** marad teljes egészében (a négy ellenőrző kérdés + a
  koordináta-visszajelzés/KX-tükör + a „ne találd ki magad” határvonal).

- [ ] **9.9 — `Megállási szabályok`.** A mai lista marad, a `TP2` pont átírva:
  *„A lezárási kapu (TP2-code) bármely pontja `[ ]`”* — a példák a kód-oldalra (hiányzó
  koordináta, `[P-…]` cél nélkül, spec-forrás nélküli képesség, kitöltetlen
  `<sec:config_lifecycle>` cella).

- [ ] **9.10 — `Státusz kezelés` + `Mechanikus kapu (M)`.**
  - státuszok: `<status:draft>` → `<status:open_questions>` → `<status:ready_for_test_plan>`;
  - a kapu-hívás: `python3 <platform-scripts-mappa>/analyze-gate-check.py specs/cycle-NN-<cycle-name> --plan-code-only`;
  - a `0`/`1`/`2` kimenet-kezelés a mai szöveggel;
  - a bélyeg a `**<field:f_gate_code>:**` sorba **és** a fázis-záró válaszba (`ANALYZE-GATE: …`);
  - a „Miért itt (M)” magyarázat marad, egy új mondattal: *a teszt-oldali checkek ebben a módban
    szándékosan nem futnak — azokat a `03b` lezárása méri a teljes `--plan-only` móddal*;
  - **új záró figyelmeztetés:** a `<status:ready_for_test_plan>` **nem** fázis-vég a ciklus
    szempontjából: a `plan.md` addig nem kész, amíg a `03b` le nem zárta. A `04`-et ilyen
    státusszal indítani hiba (a `04` belépő kapuja meg is fogja).

- [ ] **9.11 — `phase-commit.md` + záró üzenet.** `<FÁZIS-TAG>` = `03a-code-plan`, a záró státusz
  `<status:ready_for_test_plan>`. A fájl végén:
  `<!-- INCLUDE:lang/03a-write-code-plan.md#zaro-uzenet -->`.
  A mai `PE1` fázishatár-mondat („Ne kezdj task listát — a `tasks.md`-t létre se hozd”) itt
  **átalakul**: *ne kezdd el a teszt-szekciókat, és a `tasks.md`-t létre se hozd* — mindkét
  átnyúlás tilos, és a kontextus-összefoglaló teendő-listája sem felülbírálja.

- [ ] **9.12 — Kötelező boilerplate INCLUDE-ok (MINDKÉT új skillben).** Ezek nincsenek a
  frontmatter `shared:` listájában (a mai `03` sem sorolja fel őket), de a **törzsben** kötelezők
  — ha kimaradnak, a telepített `SKILL.md`-ből néma módon eltűnik a nyelvi utasítás, a
  kontextus-ellenőrzés és a Windows-os Python-hívás magyarázata:

  | marker | hely a fájlban | mit ad |
  |---|---|---|
  | `<!-- INCLUDE:lang/output-language.md#output-language -->` | közvetlenül a `# <cím>` sor után | a válasz nyelve |
  | `<!-- INCLUDE:shared/context-check.md -->` | az előző után | kontextus-telítettség ellenőrzés |
  | `<!-- INCLUDE:lang/common.md#ciklus-beazonositas -->` | az `<field:f_prerequisite>` 0. pontjában | a ciklus-beazonosítás mondata |
  | `<!-- INCLUDE:shared/python-cmd.md -->` | **közvetlenül a kapu-hívás kódblokkja ELŐTT**, mindkét helyen, ahol `python3` szerepel | a Windows-os `python` / `py -3` fallback |

  A `03b`-ben a `python-cmd.md` **két** helyen kell: a belépő kapunál (10.3/5.) és a lezáró
  kapunál (10.11).
  ```bash
  for f in prompts/skills-hu/03a-write-code-plan.md prompts/skills-hu/03b-write-test-plan.md \
           prompts/skills-en/03a-write-code-plan.md prompts/skills-en/03b-write-test-plan.md; do
    echo "--- $f"; grep -c "INCLUDE:shared/python-cmd.md" "$f"
    grep -q "INCLUDE:lang/output-language.md" "$f" && echo "output-language OK" || echo "output-language HIÁNYZIK"
    grep -q "INCLUDE:shared/context-check.md" "$f" && echo "context-check OK" || echo "context-check HIÁNYZIK"
  done
  ```

---

## 10. `03b-write-test-plan.md` (HU)

- [ ] **10.1 — Fájl létrehozása** `prompts/skills-hu/03b-write-test-plan.md`. Frontmatter:
  ```yaml
  ---
  phase: 03b
  name: bs-write-test-plan
  description: "<lásd 13.1>"
  prerequisites:
    - "specs/cycle-NN-<name>/plan.md státusz: <status:ready_for_test_plan>"
    - "analyze-gate-check.py --plan-code-only = 0 (a fázis maga futtatja, D5)"
  output:
    - "specs/cycle-NN-<name>/plan.md státusz: <status:ready_for_tasks> (a teszt-terv szekciói)"
    - "specs/cycle-NN-<name>/plan-questions.md (folytatólagos Knn)"
    - "specs/cycle-NN-<name>/tasks-input-from-prev.md és/vagy validate-input-from-prev.md (IP1)"
  prev: bs-write-code-plan
  next: bs-write-tasks
  subagents:
    - "agents/researcher.md"
  scripts:
    - "scripts/analyze-gate-check.py"
  shared:
    - "shared/plan-self-contained.md"
    - "shared/dereferencing.md"
    - "shared/spec-artifact-transfer.md"
    - "shared/plan-section-ids.md"
    - "shared/test-scenario-design.md"
    - "shared/input-from-prev.md"
    - "shared/artifact-voice.md"
    - "shared/phase-commit.md"
    - "shared/quality-check-plan-test.md"
  ---
  ```

- [ ] **10.2 — Cheat sheet.** Új tábla (ne a `03a`-ét másold), soronként:
  Előfeltétel (`plan.md` = `<status:ready_for_test_plan>` **és** a kód-kapu `0`-t adott) ·
  Hatókör (**csak a teszt-terv**; a kód-felet nem írod át — a három megengedett bővítés a 4.3-ból) ·
  Bemenet (a `plan.md` kód-fele + a spec teszt-szekciója és `DoD`-ja + `test-conventions` 2./3. szekció) ·
  Teszt-forgatókönyvek (`TS-NN`, TS1–TS8 + a `.http` alak) ·
  Generáló recept (`test-scenario-design.md`, TD0–TD7 — **ez a fázis motorja**) ·
  Gépi futtatási tábla (TP4, PH1) · Cél-környezet (EV2–EV5: a célpont a parancsban) ·
  Teszt-azonosítók (TI1: `TS-NN` + `TC-NN` közös névtér) · Tesztfájl-adatlap (TA1) ·
  Spec-lefedettség (TS7: minden sor megnevez egy `TS-NN`-t) · Környezet-felkészítés (TP3) ·
  Regresszió · Önhordóság · Lezárás (`--plan-only` + `<status:ready_for_tasks>`).

- [ ] **10.3 — `<field:f_prerequisite>` szekció (a D5 kapu).** Sorrend:
  1. ciklus-beazonosítás (`lang/common.md#ciklus-beazonositas` INCLUDE, a mai alakban);
  2. `conventions.md` létezés-ellenőrzés;
  3. munkafa-ellenőrzés (`git status --short`);
  4. a `plan.md` státuszának beolvasása — ha nem `<status:ready_for_test_plan>`:
     - ha `<status:draft>` / `<status:open_questions>` → a kód-terv nem zárult le, vissza a
       `/bs-write-code-plan`-ra;
     - ha már `<status:ready_for_tasks>` → a teszt-terv **készen van**: futtasd le a
       minőségellenőrzést, és ha hiányt találsz, a *Feladatod* szekció szerint javíts (nem
       kezdesz újra);
  5. **🔴 A státusz-mező ÖNBEVALLÁS — futtasd le a kód-terv kapuját (D5).** A mai `04`-es EG1
     szekció szövegének mintájára, `--plan-code-only` móddal, a `0`/`1`/`2` ágakkal:
     `1` esetén **STOP**, a `## <status:must_fix>` tételek felsorolása és visszairányítás a
     `/bs-write-code-plan`-ra. **Te nem javítod a kód-tervet** — különben egy hiányos
     koordináta-készletre épülő teszt-terv betonozódik be. Indoklás egy mondatban: a lezáró
     fázisnak nincs érdeke megbukni a saját kapuján, a fogadónak van.
  6. nyitott kérdések: a `plan-questions.md`-ben nincs `[ ]` — ha van, a kód-terv valójában nem
     zárult le.

- [ ] **10.4 — `Feladatod` szekció.** Négy dolgot mond ki:
  (a) **mi a leszállítandó** — a 4.1 tábla teszt-szekciói, felsorolva;
  (b) **mit nem írsz** — a kód-fél (a három megengedett bővítéssel, 4.3);
  (c) **a `TS7` konverzió a fázis lényege** — a spec tesztesetei nem prózaként másolódnak, hanem
      `TS-NN` blokká **konvertálódnak**; a spec saját címsor-szerkezetét (`Teszteset N`,
      „REST szekvencia”) **nem** nyitod meg a planben;
  (d) **a `TD0–TD7` recept kitöltendő kérdéssor**, nem olvasmány: a dimenzió-leltár szorzata
      dönti el, **hány** forgatókönyv kell.

- [ ] **10.5 — `Folytatás megszakított futás után`.** A mai szekció mintájára, a teszt-szekciókra:
  melyik `TS-NN` van meg, melyik `DoD-NN`-hez nincs még forgatókönyv, kitöltött-e a gépi tábla,
  van-e adatlap minden tesztfájlnál. Elég a `plan.md`, a `plan-questions.md` és ez a prompt.

- [ ] **10.6 — `Kontextus betöltési szabályok`** a 4.4 szakasz `03b`-oldala szerint, benne a
  `TC1/c` regiszter-határvonal blokk és a `TC1/a` önhordósági blokk (a mai szöveggel), valamint
  a kimondott tilalom: *nem indítasz `researcher`-t forrásfájl-azonosításra*.

- [ ] **10.7 — A sablon.** A `03a` sablonjának **záró** részéhez illeszkedően: a
  `<sec:testing_strategy>`-tól a `<sec:verification_strategy>`-ig **minden szekció szó szerint**
  a mai `03`-ból (a `TS-NN` blokk-formával, a `.http` példával, a gépi tábla kitöltési
  szabályaival, a `TP3` bootstrapping-táblával, a négy `[!IMPORTANT]`/`[!CAUTION]` blokkal, a
  `TI1`/`TA1`/`spec_coverage` szekciókkal, a unit/integrációs/E2E példa-sűrűséggel).
  A sablon fejlécében **egy soros jelölés**: *a `<sec:goal_and_approach>`-tól a
  `<sec:reverse_coverage>`-ig a szekciókat a `03a` írta — a fejlécet és a státusz-mezőt te
  lépteted, a tartalmukat nem szerkeszted.*

- [ ] **10.8 — `Validációs ciklusok`.** A mai `2.` (test_specification után) és `3.`
  (execution_order után) kör, `1.` és `2.` sorszámmal, szó szerint.

- [ ] **10.9 — `Spec kritika — a teszt-oldalon`.** Szűkített változat: hiányzó/ellentmondó
  teszteset, lefedetlen `DoD-NN`, a spec-ben hagyott teszt-koordináta (KX-tükör → beemelés a
  teszt-szekcióba), és a „megfigyelhető viselkedést érintő döntés → kérdés” határvonal.
  Kimondva: a `spec.md`-t **nem írod**, a `<sec:planned_changes>`-t **nem írod át**.

- [ ] **10.10 — `Megállási szabályok`.** A mai listából: implementációs döntési pont (itt:
  teszt-stratégiai), spec-hiányosság, spec-ellentmondás, komplex konténerizáció, a `TP2-test`
  kapu bármely `[ ]` pontja. **Új eset:** *ha a teszt megtervezéséhez olyan koordináta,
  parancs vagy termelő-kód-változás kell, ami a kód-tervben nincs* → `Knn` kérdés **vagy**
  visszairányítás a `/bs-write-code-plan`-ra; a kód-tervet magad nem írod át.

- [ ] **10.11 — `Státusz kezelés` + `Mechanikus kapu (M)`.** A mai `03`-as szekció **szó szerint**
  (`--plan-only`, `f_gate` bélyeg, a `04` EG1-jére hivatkozó záró mondat), a státusz-lánccal:
  a `<status:ready_for_test_plan>`-ról `<status:ready_for_tasks>`-ra a felhasználó megerősítése után.
  A „Kész lifecycle” megjegyzés (a `07` állítja `<status:done>`-ra) ide kerül.

- [ ] **10.12 — `phase-commit.md` + záró üzenet.** `<FÁZIS-TAG>` = `03b-test-plan`, záró státusz
  `<status:ready_for_tasks>`, a fájl végén
  `<!-- INCLUDE:lang/03b-write-test-plan.md#zaro-uzenet -->`, és a mai `PE1` fázishatár-mondat
  változatlanul (a `tasks.md`-t létre se hozd).

- [ ] **10.13 — A mai `prompts/skills-hu/03-write-plan.md` törlése.**

---

## 11. A determinisztikus kapu (`analyze-gate-check.py`)

- [ ] **11.1 — Új CLI-flag.** `prompts/scripts/analyze-gate-check.py`, az `argparse` blokkba a
  `--plan-only` mellé:
  ```python
  parser.add_argument(
      "--plan-code-only",
      action="store_true",
      help="a 03a-code-plan fázis lezárásához: csak a kód-terv checkjei futnak "
           "(a teszt-szekciók még nem léteznek; azokat a 03b lezárásakor a --plan-only méri)",
  )
  ```
  A mód **implikálja** a `--plan-only` szemantikáját (a `tasks.md`-t üresként kezeli, és
  előfeltételként csak a `spec.md` + `plan.md` létezését kéri). A `main()`-ben rögtön az
  argumentum-feldolgozás után: `if args.plan_code_only: args.plan_only = True`, majd egy
  `code_only = args.plan_code_only` lokális változóval szűrjük a checkeket.
  Ha mindkét flag meg van adva, az **nem hiba** (a `--plan-code-only` a szűkebb).

- [ ] **11.2 — A checkhalmaz.** `code_only` módban **kizárólag** ezek futnak:

  | check | ID | megjegyzés |
  |---|---|---|
  | `check_plan_ids` | P1 | változatlan |
  | `check_dod` | D1/D2 | a spec `DoD-NN` azonosítói |
  | `check_required_tables(plan, REQUIRED_PLAN_CODE_TABLES, …)` | S1 | **új konstans**, lásd 11.3 |
  | `check_config_lifecycle` | C4 | változatlan |
  | `check_env_coordinates` | C6/KO1 | változatlan |
  | `check_planned_change_purpose` | WY1 | változatlan |
  | `check_target_environment(…, code_only=True)` | EV1 | **új paraméter**, lásd 11.4 |
  | `check_gate_config_moves` | GC1 | változatlan (a `tasks_text` üres) |
  | `check_path_format` (spec+plan) | R1 | változatlan |
  | `check_plan_anchors` | A2/A2b | változatlan |
  | `check_artifact_voice` (spec+plan) | A3 | változatlan |
  | `check_gate_stamp(…, field="f_gate_code")` | GA1 | **új paraméter**, lásd 11.5 |
  | `check_judgment_candidates` | — | csak leltárt ad, nem megállapítást; maradhat |

  **Nem futnak** `code_only` módban: `check_coverage_chain`, `check_spec_artifact_transfer` (V1),
  `check_test_section_volume` (V2), `check_test_scenarios` (TS1–TS6),
  `check_spec_coverage_scenarios` (TS7), `check_test_artifact_datasheet` (TA1),
  `check_ts_http_blocks` (TS8), `check_run_table_phase` (PH1), `check_test_ids` (TI1),
  `check_executed_artifacts`, és a `--plan-only` alatt már ma sem futó tasks-oldali checkek.

  > **Miért marad ki a `check_coverage_chain` (C1/S3-lánc)?** A `DoD-NN → [P-…] → task` lánc
  > azt méri, hogy minden `DoD-NN` visszavezethető plan-képességre. Egy **kizárólag teszttel**
  > igazolt `DoD-NN` a kód-fél lezárásakor még nem lehet lefedve — a check ott **hamis FAIL**-t
  > adna. A `03b` lezárásakor a `--plan-only` ezt teljes egészében méri, tehát nem veszik el.
  > A `<sec:reverse_coverage>` tábla **létezését és `[P-…]` formátumát** viszont a `code_only`
  > mód is kéri (11.3).

  > **Miért marad ki a `check_executed_artifacts`?** A futtatott artefaktumok (teszt-parancsok
  > belépési pontjai) a teszt-félben keletkeznek.

- [ ] **11.3 — `REQUIRED_PLAN_CODE_TABLES` konstans.** A `REQUIRED_PLAN_TABLES` mellé, a
  205. sor környékére:
  ```python
  # A 03a-code-plan lezárásakor kötelező plan-táblák. A `spec_coverage` és a
  # `machine_run_table` szándékosan NEM szerepel: azok a 03b-test-plan
  # leszállítandói, és a teljes `--plan-only` mód méri őket.
  REQUIRED_PLAN_CODE_TABLES = [REQUIRED_PLAN_TABLES[1], REQUIRED_PLAN_TABLES[2]]  # reverse_coverage, environment_coords
  ```
  **Indexelés helyett** írd ki a két tételt explicit (`sec("reverse_coverage")`, `sec("environment_coords")`)
  ugyanazzal a fázis- és magyarázat-szöveggel, hogy a `REQUIRED_PLAN_TABLES` átrendezése ne
  rontsa el némán.

- [ ] **11.4 — `check_target_environment(plan_text, f, code_only=False)`.** A függvény ma az
  `EV1` mezőt **és** a futtatási tábla `<field:f_environment>` oszlopát méri (EV2–EV5).
  `code_only=True` esetén **csak** az `EV1` ág fut (a `**<field:f_target_env>:**` mező létezése és
  kitöltöttsége); a tábla-oldali ágakból azonnal visszatér. A docstringbe kerüljön be, hogy
  EV2–EV5 a `03b` lezárásának tárgya.

- [ ] **11.5 — `check_gate_stamp(plan_text, f, field="f_gate", status_key="ready_for_tasks")`.**
  A függvény ma a `**<field:f_gate>:**` bélyeg meglétét méri (`GA1`, **javaslat**, nem Must Fix).
  **Két** paramétert kell felvennie, nem egyet:
  ```python
  def check_gate_stamp(plan_text, f, field="f_gate", status_key="ready_for_tasks"):
      """GA1 — lezárt plan → van-e nyoma a mechanikus kapu futásának."""
      head = "\n".join(plan_text.splitlines()[:20])
      status_m = re.search(r"\*\*" + re.escape(fld("f_status")) + r":\*\*\s*(.+)", head)
      if not status_m or st(status_key).lower() not in status_m.group(1).lower():
          return
      if re.search(r"\*\*" + re.escape(fld(field)) + r"[^*:]*:?\*\*", head):
          return
      f.suggest("GA1", "03", …)   # a szövegben `st(status_key)` és `fld(field)`
  ```
  > **🔴 Ezt könnyű elrontani.** A check **korán visszatér**, ha a plan státusza nem
  > `<status:ready_for_tasks>`. A `03a` lezárásakor a státusz `<status:ready_for_test_plan>`,
  > tehát a puszta `field` paraméter **nem elég**: a `status_key` nélkül a check `code_only`
  > módban csendben soha nem mérne semmit. `code_only` hívás:
  > `check_gate_stamp(plan_text, f, field="f_gate_code", status_key="ready_for_test_plan")`.
  > A hibaüzenetben a futtatandó parancs is `--plan-code-only`-ra változik.

- [ ] **11.5/b — A `--plan-only` help-szövege.** A mai súgó: *„a 03-plan fázis lezárásához: csak a
  spec+plan checkek futnak (a tasks.md még nem létezik)”* → a `03b-test-plan` fázisra átírva
  (és az új flag súgója a `03a`-ra hivatkozik, 11.1). Ugyanígy a `--plan-only` mód alatti
  kód-kommentek (`# `--plan-only` módban a tasks-oldalt üresként kezeljük…`) kapják meg, hogy
  ez a mód a **teljes plan** kapuja.
  ```bash
  grep -n "03-plan" prompts/scripts/*.py
  ```

- [ ] **11.6 — Kimeneti sor.** A `code_only` mód összefoglalója maradjon **ugyanaz a prefix**
  (`ANALYZE-GATE: N Must Fix, M javaslat`), hogy a `GS2` bélyeg-konvenció (a záró válaszba szó
  szerint bemásolt sor) ne változzon. Az első kiírt sor előtt legyen egy mód-jelző sor:
  `# mód: --plan-code-only (a teszt-oldali checkek nem futnak — azokat a 03b lezárása méri)`.

- [ ] **11.7 — `--emit-slices` viselkedés.** A mai `elif args.emit_slices and args.plan_only`
  ág üzenete `code_only` módban is helyes (a `tasks.md` nem létezik) — ellenőrizd, hogy nem
  hasal el; ha kell, a mód nevét is írja ki.

- [ ] **11.8 — Használati hiba.** `--plan-code-only` + `--report-closure` (vagy `--paths-only`)
  együtt: a mai ág-sorrend szerint az önálló módok előbb futnak le. Nézd meg, és ha egy
  kombináció csendben félreértelmeződik, adj `exit 2`-t explicit üzenettel.

- [ ] **11.9 — Füstteszt egy meglévő ciklus mappán.** Ha van a gépen berkispec-es projekt,
  futtasd le rajta mindkét módot, és hasonlítsd össze a Must Fix listákat:
  ```bash
  python3 prompts/scripts/analyze-gate-check.py <ciklus-mappa> --plan-only       > /tmp/full.txt
  python3 prompts/scripts/analyze-gate-check.py <ciklus-mappa> --plan-code-only  > /tmp/code.txt
  diff /tmp/full.txt /tmp/code.txt
  ```
  **Elvárás:** a `## <status:must_fix>` blokk `code_only` módban a teljes lista **részhalmaza**
  (a teszt-oldali kódok eltűnnek, új Must Fix kód nem jelenik meg).
  **A `## Javaslatok` blokkra ez NEM áll:** a `GA1` a két módban **más mezőt és más státuszt**
  mér (`f_gate_code` + `<status:ready_for_test_plan>` vs. `f_gate` + `<status:ready_for_tasks>`),
  tehát egy lezárt planen `code_only` módban akkor is felbukkanhat, ha a teljes módban nem —
  ez **helyes viselkedés**, ne „javítsd” el. Ha bármelyik módban `exit 2` (használati hiba) jön,
  az a 11.1–11.8 hibája.
  **Célzott próba a 11.5 csapdájára:** vedd ki kézzel a `**<field:f_gate_code>:**` sort egy
  `<status:ready_for_test_plan>` státuszú plan fejlécéből, és futtasd a `--plan-code-only`-t —
  a `GA1` javaslatnak **meg kell jelennie**. Ha csendben átmegy, a `status_key` paraméter
  hiányzik vagy rosszul van bekötve.
  Ha nincs kézre eső valódi ciklus, gyárts a scratchpadba egy minimál ciklus-mappát
  (`spec.md` + `plan.md` a `03a` sablonja szerint), és azon fusson a füstteszt.

---

## 12. Szomszéd fázisok és scriptek átvezetése

- [ ] **12.1 — `04-write-tasks.md` (HU+EN).** Két dolog:
  - a `prev:` frontmatter → `bs-write-test-plan`;
  - a `2.` pont (státusz-beolvasás) mellé egy zárójeles mondat: *ha a `plan.md`
    `<status:ready_for_test_plan>` állapotban van, a **teszt-terv** hiányzik — vissza a
    `/bs-write-test-plan`-ra.* Az `EG1` kapu-blokk (`2/b`) **változatlan** (D3).

- [ ] **12.2 — `02-write-spec.md` (HU+EN).** `next:` → `bs-write-code-plan`; a törzsben a
  „A 03 is beolvassa” mondat → „A `03a-write-code-plan` is beolvassa”.

- [ ] **12.3 — `agents-{hu,en}/researcher.md`.** A `Mód A — Strukturált plan-feltárás
  (`03-write-plan.md`)` fejléc és a `called_by`/`skills:` lista → `03a-write-code-plan.md`.
  A „ha a hívó literál értékeket kér (jellemzően `03-write-plan`)” mondat → `03a-write-code-plan`
  **és** `03b-write-test-plan` (mindkettő kérhet literál értéket).

- [ ] **12.4 — `agents-{hu,en}/plan-fixer.md`.** A 8.5-ben leírt INCLUDE-átvezetés, plusz:
  - a `1.` teendő „Ne olvasd be a fázis-skillt (`/bs-03-write-plan`)” hivatkozás →
    *(`/bs-write-code-plan`, `/bs-write-test-plan`)*;
  - a `description`/`role` szövegében a `03-write-plan` → `03a/03b` (a tényleges leírót a
    `descriptions.json` adja, lásd 13.1 — **ott is** át kell vezetni);
  - **egy új mondat a wrapper teendői közé:** a fixer **mindkét felet** javíthatja ugyanabban a
    `plan.md`-ben; a `[P-…]` ID-kra és a `TS-NN`/`TC-NN` azonosítókra vonatkozó
    átnevezés-tilalom változatlanul él.

- [ ] **12.5 — `prompts/scripts/cycle-status.py` (D11).**
  - új konstans a fájl elején: `_S_READY_TEST_PLAN = st("ready_for_test_plan").lower()`;
  - a mai egyetlen „Tervezés (plan.md)” sor helyett **kettő**:
    - `"Kód-terv (plan.md)"` → `KÉSZ`, ha a státusz ∈ {`ready_for_test_plan`, `ready_for_tasks`,
      `ready_for_implement`, `ready_for_validate`, `done`}; `FOLYAMATBAN`, ha van státusz, de nem
      ezek; `MÉG NEM FUTOTT`, ha nincs `plan.md`;
    - `"Teszt-terv (plan.md)"` → `KÉSZ`, ha a státusz ∈ {`ready_for_tasks`, `ready_for_implement`,
      `ready_for_validate`, `done`}; `FOLYAMATBAN`, ha `ready_for_test_plan`; `MÉG NEM FUTOTT` egyébként.
  - **Ellenőrizd**, hogy az összesített ciklus-státusz (minden fázis KÉSZ) logikája nem sérül:
    a két sor ugyanabból a mezőből számol, tehát egy `done` plan mindkettőt KÉSZ-re teszi.
  ```bash
  python3 prompts/scripts/cycle-status.py <ciklus-mappa>   # ha van kézre eső projekt
  ```

- [ ] **12.6 — `prompts/lang/{hu,en}/07-validate.md`.** A VD5 eszkalációs blokk
  `/bs-write-plan (DoD-hiba esetén: /bs-write-spec)` sora → `/bs-write-code-plan` vagy
  `/bs-write-test-plan` **a hiba jellege szerint**, egy fél soros útmutatással:
  *teszt-forgatókönyv, futtatási tábla, tesztfájl → `/bs-write-test-plan`; koordináta, tervezett
  módosítás, konfiguráció → `/bs-write-code-plan`; `DoD` → `/bs-write-spec`.*

- [ ] **12.7 — `prompts/scripts/report-gate-check.py`.** A `03-write-plan „Kapu-konfiguráció
  együtt mozog" szabályát` hibaszöveg → `03a-write-code-plan`.

- [ ] **12.8 — Maradék hivatkozások.** Futtasd le **mindhárom** mintát, és vezess át mindent,
  ami megmaradt:
  ```bash
  grep -rn "03-write-plan\|bs-write-plan\b" --include=*.md --include=*.py --include=*.json \
       --include=*.sh --include=*.ps1 . | grep -v inprove-list
  grep -rn "03-plan" --include=*.md --include=*.py --include=*.json . | grep -v inprove-list
  ```
  **Elvárás az első mintára:** nulla találat (az `inprove-list*.md` munkafájlok kivételével —
  azok a múltat rögzítik, ne írd át őket).

  **A második minta (`03-plan`) elvárása NEM nulla.** Amit **át kell** vezetni:
  `analyze-gate-check.py` `--plan-only` súgója (11.5/b), `report-gate-check.py` hibaszövege
  (12.7), a `plan-fixer` leírói (12.4/13.1).
  Amit **szándékosan meg kell hagyni** (D12 — az `05` hurok célfázis-jelölése egy dokumentumra,
  a `plan.md`-re mutat, nem fázisra):
  - `prompts/lang/{hu,en}/05-analyze.md` — `**Célfázis:** <02-spec | 03-plan | 04-tasks>` és az
    `AF-NN` sablonsor;
  - `prompts/skills-{hu,en}/05-analyze.md` — a példa-sor (`1. AF-02 · 03-plan · …`);
  - a `analyze-gate-check.py` `f.add(...)/f.suggest(...)` hívásainak `"03"` célfázis-argumentumai.

  > **Ha ezt a megkülönböztetést elrontod**, vagy egy soha nem létező `03a-plan`/`03b-plan`
  > célfázis kerül a hurokba (és az `05` orchestrátor nem tudja, melyik fixert indítsa), vagy
  > megállsz egy olyan találatnál, amit nem kell javítani.

---

## 13. Leírók és telepítés

- [ ] **13.1 — `descriptions.json` (HU+EN).** `prompts/lang/hu/descriptions.json` és
  `prompts/lang/en/descriptions.json`:
  - a `"bs-write-plan"` kulcs **törlése**;
  - **két új kulcs** a helyére (a `bs-write-spec` és a `bs-write-tasks` közé):
    - `"bs-write-code-plan"` — magyar minta: *„berkispec - 03a. Használd, ha a ciklus spec.md-je
      'Tervezésre kész' (Phase 03a), a technikai megvalósítási terv **kód-oldalának**
      kidolgozásához: környezeti koordináták, tervezett módosítások (céllal), konfiguráció,
      séma-artefaktumok, scope-kapu (kódbázis-elemzés, szükség esetén researcher subagent).
      A plan.md-t 'Teszt-tervezésre kész' státuszra zárja; a teszt-tervet a
      /bs-write-test-plan írja."*
    - `"bs-write-test-plan"` — magyar minta: *„berkispec - 03b. Használd, ha a ciklus plan.md-je
      'Teszt-tervezésre kész' (Phase 03b), a **teszt-terv** kidolgozásához: TS-NN
      teszt-forgatókönyvek lépés-táblával és .http alakkal, gépi futtatási tábla,
      környezet-felkészítés, teszt-artefaktum adatlapok, spec-lefedettség, regresszió.
      A plan.md-t 'Task írásra kész' státuszra zárja."*
  - a `plan-fixer` bejegyzés `description` szövegében a `03-write-plan` → `03a/03b` (12.4).

  > **Kemény kapu:** a telepítő `exit 1`-gyel megáll, ha egy skill `name`-jéhez nincs leíró
  > (`install-helper.py`, 11.4 kapu). Ha a `13.1` kimarad, **semmi nem telepíthető**.

- [ ] **13.2 — Telepítési füstteszt mind az öt platformra.** A skillek `glob("*.md")`-del
  kerülnek be, tehát az új fájlok automatikusan telepítődnek — de a leíró-kapu és az
  INCLUDE-feloldás nem. Telepíts egy eldobható célmappába, és ellenőrizd:
  ```bash
  TMP=$(mktemp -d)
  ./install.sh   # a promptok kérdéseinél: célmappa=$TMP, prompt-nyelv=hu, projekt-nyelv=hu
  ls $TMP/.claude/skills/ | grep -i plan
  grep -c "INCLUDE:" $TMP/.claude/skills/bs-03a-write-code-plan/SKILL.md   # 0 legyen
  grep -c "INCLUDE:" $TMP/.claude/skills/bs-03b-write-test-plan/SKILL.md   # 0 legyen
  grep -rn "<sec:\|<field:\|<status:" $TMP/.claude/skills/bs-03*/SKILL.md  # 0 találat legyen
  grep -n "Teszt-tervezésre kész" $TMP/.claude/skills/bs-03a-write-code-plan/SKILL.md
  ```
  Ha marad feloldatlan `INCLUDE` marker vagy `<sec:…>` token, az elírt fájlnév/horgony vagy
  hiányzó `status-keys.json` kulcs — javítsd, ne hagyd a telepítettben.
  Ismételd meg **`en` prompt-nyelvvel** is (legalább egy platformra).

- [ ] **13.3 — Gemini agent.json tükrök.** A `plan-fixer` és a `researcher` promptja változott,
  tehát a tükröket regenerálni kell:
  ```bash
  python3 prompts/scripts/sync-gemini-agents.py
  python3 prompts/scripts/sync-gemini-agents.py --check   # 0 exit
  ```

---

## 14. Dokumentáció

- [ ] **14.1 — `README-HU.md` és `README.md`.** Átvezetendő helyek (mindkét fájlban):
  - a fázis-lista / „Indító prompt (copy-paste)” szekció: a `03` két parancsra bomlik;
  - a `* **/bs-write-plan**: …` felsorolás-pont → két pont;
  - a nagy fázis-tábla `| /bs-write-plan | Plan | spec.md | plan.md (Task írásra kész) …` sora
    → **két sor** (`/bs-write-code-plan`, `/bs-write-test-plan`) a 4.1 tábla szerinti
    bemenet/kimenet oszlopokkal;
  - a „Shift-left: a kapu a 03 és 04 lezárásakor is fut (M)” szekció: **három** lezárási kapu
    van (`03a` → `--plan-code-only`, `03b` → `--plan-only`, `04` → teljes), a `04` EG1-je
    változatlanul a `--plan-only`;
  - a példa-séta (`Futtasd a parancsot: /bs-write-plan input: @specs/cycle-02-oidc-login/spec.md`)
    → két lépés, közte `/clear`;
  - a `prev:`/`next:` frontmatter-példa (`next: 03-write-plan`) → `03a-write-code-plan`;
  - a „02/03/04 (analyze-hurok, D13)” bekezdés: a `03` minőségi kapuja **két** shared fájlban él;
  - az `agents/plan-fixer.md` sora: a wrapper mindkét felet javítja;
  - a státusz-lánc felsorolása, ahol szerepel: **új** `Teszt-tervezésre kész` állomás.

- [ ] **14.2 — `berki-spec-directory-structure.md`.** A `03-write-plan.md` sora → két sor.
  A „The longest skill in the framework” megjegyzés a `03b`-hez kerül (vagy törlődik, ha a
  16.5 mérés szerint már nem igaz).

- [ ] **14.3 — `prompts/meta-improve-prompts.md`.** Három helyen:
  - a *„A workflow felépítése”* per-ciklus felsorolásában a `03` → `03a` + `03b`, egy-egy
    mondatos leírással és a köztes státusszal;
  - a *„A prompt fájlok”* táblában a `03-write-plan.md` sor → két sor (a mai sor tartalmának
    szétosztásával: a `TS-NN`/`TS1–TS8`/`PH1`/`TP4`/`test-scenario-design` a `03b`-hez);
  - **új tervezési elv `7/k` néven**, a `7/j` után. Vázlat (a meglévő elvek hangján, egy
    bekezdésben): *A negyedik teszt-keményítő kör nem szabály volt, hanem **fázishatár**. A
    `TS1–TS6`, a `TD0–TD7` és a `TS7`/`TA1`/`WY1` mind ugyanarra a hibára válaszolt — a
    teszt-terv a fázis végén, a legkevesebb figyelemnél készül —, és mindegyik ugyanott ért
    véget: a szabály megvolt, a kapu megfogta volna, a fázis mégis egy mondatos forgatókönyveket
    termelt. A `03` (1042 sor, a keret legnagyobb skillje, a `04` háromszorosa) ezért két fázisra
    hasadt: `03a` a kód-terv, `03b` a teszt-terv, **egyetlen `plan.md`-be**. A nyereség nem a
    token, hanem három szerkezeti tulajdonság: (a) egy fázis, amelynek a teszt-szekció az
    **egyetlen** leszállítandója, nem tudja „nem megnyitni” azt (a `TS7`-vakfolt megszűnik);
    (b) a `03b` **lezárt** kód-tervről indul, tehát a `TA1` adatlap és a `TS-NN` hívások literál
    értékei nem találgatások; (c) a `7/j` elve újra alkalmazható: a `03b` **fogadó** fázisként
    lefuttatja a kód-fél kapuját (`--plan-code-only`), mert neki érdeke a jó bemenet. A `04` felé
    menő kontraktus **nem gyengült**: a `03b` a teljes `--plan-only` kapuval zár, és a `04` EG1-je
    változatlan. **Prompt-módosításnál:** ha egy fázis kimenete két, egymástól minőségileg
    független artefaktum-halmaz, és a második rendre gyengébb, akkor először a **fázishatárt**
    kérdőjelezd meg, ne a szabálysűrűséget — és ha hasítasz, mindig kérdezd meg, melyik fél
    **ír** és melyik csak **olvas** egy megosztott dokumentumban (itt: a `03b` három, tételesen
    felsorolt bővítést tehet a kód-félbe, semmi mást).*

- [ ] **14.4 — `prompts/lang/{hu,en}/01-add-cycles.md`.** A `bs-write-plan` (03) hivatkozás
  → `bs-write-code-plan` (03a).

---

## 15. Kapuk és commit

- [ ] **15.1 — Nyelvi paritás (default).**
  ```bash
  python3 prompts/scripts/lang-parity-check.py
  ```
  A féloldalas fájlok WARN-jai megengedettek, **hiba nem**.

- [ ] **15.2 — Nyelvi paritás (strict).**
  ```bash
  python3 prompts/scripts/lang-parity-check.py --strict
  ```
  Itt a **teljes fájlhalmaz-paritás** is kötelező: minden új `-hu` fájlnak van `-en` párja
  (4 új shared blokk + 2 quality-check + 2 skill + 2 lang fájl).

- [ ] **15.3 — Gemini tükrök.** `python3 prompts/scripts/sync-gemini-agents.py --check` → 0.

- [ ] **15.4 — Jelentés-review (emberi).** A paritás-kapu a **szerkezeti** eltérést fogja meg, a
  **jelentés**-eltérést nem. Menj végig a nyolc új/módosított fájlpáron, és ellenőrizd, hogy az
  angol szöveg ugyanazt mondja — különös figyelemmel a 8.1/8.2 **új** pontjaira és a `03b`
  belépő kapujának (10.3/5.) indoklására.

- [ ] **15.5 — Commit.** Egy commit, magyar üzenettel, a keret konvenciója szerint:
  `refactor(prompts): a 03-plan fázis hasítása kód-tervre (03a) és teszt-tervre (03b)`
  A törzsben: a `--plan-code-only` mód, az új státusz és mező, a `04` EG1 változatlansága.

---

## 16. Elfogadási kritériumok

- [ ] **16.1** A `prompts/skills-hu/` és `prompts/skills-en/` mappában **nincs** `03-write-plan.md`,
  van `03a-write-code-plan.md` és `03b-write-test-plan.md`.
- [ ] **16.2** A 12.8 két grep-mintája lefutott: a `03-write-plan|bs-write-plan` mintára **nulla**
  találat (az `inprove-list*.md` kivételével), a `03-plan` mintára pedig **csak** a 12.8-ban
  tételesen felsorolt, szándékosan megtartott helyek maradtak (`05` célfázis-jelölés + a kapu
  `f.add/f.suggest` `"03"` argumentumai).
- [ ] **16.3** `analyze-gate-check.py --plan-code-only` egy valódi (vagy gyártott) ciklus-mappán
  a `--plan-only` Must Fix listájának **részhalmazát** adja, `exit 0`/`1` értelmesen.
- [ ] **16.4** A telepítés mind az öt platformra lefut, és a telepített
  `bs-03a-write-code-plan/SKILL.md` + `bs-03b-write-test-plan/SKILL.md` fájlokban **nincs**
  feloldatlan `INCLUDE:` marker és `<sec:` / `<field:` / `<status:` token.
- [ ] **16.5** Méret: mindkét új skill **600 sor alatt** van (a mai 1042 helyett).
  ```bash
  wc -l prompts/skills-hu/03a-write-code-plan.md prompts/skills-hu/03b-write-test-plan.md
  ```
  Ha valamelyik 600 fölött marad, **állj meg és jelezd** — akkor a vágás nem oldotta meg a
  méret-problémát, és a 3. szakasz döntéseit újra kell nézni (nem a szöveget kell tömöríteni:
  a teszt-szabályok tömörítése a `7/f`/`7/h` szerint adatvesztés).
- [ ] **16.6** `lang-parity-check.py --strict` és `sync-gemini-agents.py --check` egyaránt 0.
- [ ] **16.7 — ÉLES PRÓBA (a legfontosabb).** Egy valódi, kicsi ciklus végigvitele egy éles
  projekten `/bs-write-code-plan` → `/clear` → `/bs-write-test-plan` → `/bs-write-tasks` →
  `/bs-analyze` úton, **gyenge modellen** (a keményítés célközönsége). Amit mérni kell:
  - a `03a` nem kezdett teszt-szekciót, és a `--plan-code-only` `0`-t adott;
  - a `03b` belépő kapuja lefutott (a válaszban ott az `ANALYZE-GATE: …` sor);
  - a `<sec:plan_test_scenarios>` szekció **létrejött**, és a `TS-NN` blokkok **nem** egy
    kérés-válasz párból állnak (ez volt a `7/h` panasza — ez a próba tárgya);
  - a `04` EG1 kapuja `0`-t adott a lezárt planre.
  A tapasztalatot **írd vissza ebbe a fájlba** a 18. szakaszba.

---

## 17. Végrehajtási sorrend

### 17.1 A lépések sorrendje

1. **5.** Előkészítés (branch, mérés, kiinduló kapuk).
2. **6.** Nyelvi szótár és `lang/` blokkok — *ez van legelöl, mert nélküle minden új token feloldatlan marad.*
3. **7.** A négy új közös blokk.
4. **8.** A minőségi kapu hasítása (shared + lang horgonyok).
5. **9.** `03a` (HU).
6. **10.** `03b` (HU).
7. **11.** A determinisztikus kapu (`--plan-code-only`) + füstteszt.
8. **9/10 angol párja** — a két új skill `-en` változata (a HU véglegesítése **után**, hogy ne
   kelljen kétszer átvezetni).
9. **12.** Szomszéd fázisok és scriptek.
10. **13.** Leírók és telepítési füstteszt.
11. **14.** Dokumentáció.
12. **15.** Kapuk és commit.
13. **16.7** Éles próba.

### 17.2 Miért ez a sorrend

- A **szótár elöl**: egy hiányzó `status-keys.json` kulcs miatt a telepítő feloldatlan
  `<status:…>` tokent hagy a `SKILL.md`-ben — és a hibát csak a 13.2 füstteszt fogja meg,
  addig minden munka „jónak látszik”.
- A **shared blokkok a skillek előtt**: a skillek csak `INCLUDE` markert tartalmaznak; ha a
  cél-fájl nincs meg, a telepítő hasal el.
- A **kapu-script a skillek után**: a `code_only` checkhalmazt a `03a` végleges sablonjához
  kell illeszteni (melyik tábla kötelező), nem fordítva.
- Az **angol fa a magyar véglegesítése után**: a hasítás közben még mozognak a szekció-határok;
  a paritás-kapu a végén egyszer, tisztán fut le.
- A **dokumentáció a végén**: a README-k a végleges parancsneveket és a végleges kapu-neveket
  írják le.

---

## 18. Tapasztalatok (a végrehajtás közben töltsd)

> Ide kerül minden olyan felismerés, ami a terv írásakor nem látszott — különösen a 16.7 éles
> próba eredménye. Ha egy döntés (3. szakasz) tarthatatlannak bizonyult, **írd ide, mi lett
> helyette és miért** — ez lesz a `meta-improve-prompts.md` `7/k` elv végleges szövegének forrása.

- _(még nincs bejegyzés)_

---
---

# B. rész — „Az üres teszt zöld”: bizonyíték-keményítés

## 20. Orientáció — a konkrét eset és a mért mechanizmus

> Ha ezt a részt üres kontextusban kezded, az 1.1–1.3 szakasz (a repó felépítése, a két nyelvi
> tengely, a kötelező kézi kapuk) **ide is érvényes** — olvasd el azt is.

### 20.1 Mi történt (`cycle-30`, éles projekt)

Az éles példaprojekt (`flowx-token-exchange`) `cycle-30-tmp-token-concurrency-and-health-improvements`
ciklusában a dev környezetre szánt E2E tesztek **soha nem futtattak egyetlen dev kérést sem**, a
`07-validate` mégis `PASS`-ra zárt. A tényleges lánc:

1. A `tasks.md` `T020`–`T027` `[RED]` taskjai előírták az E2E tesztek megírását.
2. A `06-implement` a tesztfájlba (`test/integration/cycle_30_concurrency_test.py`) **üres vázakat**
   írt: a teszt-függvények törzse `assert True`.
3. A `pytest` **26 passed / 0 failed** eredménnyel zárt, a taskok `- [x]`-re kerültek.
4. A `07` determinisztikus rétege (`run-tests.py`) a JUnit XML `passed`/`failed` számlálóit
   olvasta → zöld. A `dod-check.py` a bizonyíték-stringet a **teszt nevére** illesztette → ✓.
   A `reviewer` nem adott `<status:must_fix>`-et.
5. A `test-report/validate/round-01/e2e/rest-logs/` mappában **50 naplófájl** állt — mind
   `127.0.0.1:3028`-as és mind **korábbi körből örökölt** (hónapokkal régebbi időbélyeg). A
   riport tehát *telinek látszott*.

**Ez a hibaosztály visszatérő** — a felhasználó szerint nem első alkalommal fordult elő.

### 20.2 Amit a keretben ellenőriztem — az első négy determinisztikus rés

Ezek **nem** feltételezések: mindegyik mellé odaírtam, hol nézhető meg.

**(1) A `[RED]`-nek soha nem kellett vörösnek lennie.**
`prompts/skills-hu/06-implement.md`, a *Végrehajtási szabályok* 8. pontja:

> „Csak zöld `[CHECK]` után jelölhető kész (`- [x]`) a csoport — a `[RED]`/`[GREEN]` taskokat is
> csak ekkor zárd le.”

A TDD ciklus **első fele nincs bizonyítva**: a keret sehol nem kéri, hogy a `[RED]` task
elvégzése után a teszt **bukjon**. A `06` per-task folyamata (1–13. pont) csak zöldséget ismer,
a 12. pont pedig külön commitot kér a `[RED]` és a `[GREEN]` állapotra — tehát a RED *commit*
létezik, de senki nem nézi meg, hogy vörös volt-e. **Egy `assert True` stub ettől
megkülönböztethetetlen egy valódi teszttől — sőt könnyebb út, mert azonnal zöld.**

**(2) A DoD-join a teszt NEVÉRE illeszt, nem a tartalmára.**
`prompts/scripts/dod-check.py`: az `index_tests(round_dir)` a JUnit XML-ből **nevek szerint**
indexel, a `match_test()` a `· _bizonyíték:_` stringet erre illeszti. Egy `test_t30_01` nevű
`assert True` ✓-t ad a `DoD-NN`-re.

**(3) Nem-lokális kategóriánál nincs FORGALMI bizonyíték.**
Az `EV1–EV5` (7/g) a **parancsot** és az **előfeltételt** védi: host a parancsban (EV3),
elérhetőségi probe (EV4), `localhost`-tilalom (EV5). A `run-tests.py`
`check_environment_mismatch(rows)` a futtatás **ELŐTT**, a **táblán** fut. A lánc egy lépéssel
korábban szakadt el: itt nem az volt a kérdés, *hol* futott, hanem hogy **futott-e egyáltalán
forgalom**. A keletkezett bizonyítékot (`rest-logs`) senki nem veti össze a cél-hosttal.

**(4) Az örökölt artefaktum hamis teltséget ad.**
`prompts/scripts/report-gate-check.py` `check_artifact(report_dir, rel)` — a docstringje szerint
*„(ok, üzenet) — létezik-e és nem üres-e az artefaktum”*. Egy előző körből ottmaradt fájl
**mindkettőnek megfelel**; mappa esetén a `rglob("*")` a régi fájlokat is megszámolja.

### 20.2/b Három további rés — a ciklus fájljainak második elemzéséből

A `cycle-30` artefaktumainak részletes átvizsgálása (`check-log.md`, `tasks.md`,
`validation-report.md`, JUnit XML) **három további**, egymástól független rést hozott felszínre.
Az első közülük **a fentebbi (1) pont kapuját is hatástalanítaná**, ezért kötelező vele együtt
kezelni.

**(5) A `[CHECK]` parancsokat nem futtatta egyenként — és a napló ezt elrejtette.**
A `tasks.md` **nyolc külön** `[CHECK]` taskot ír elő (`T030a`, `T031`–`T037`), mindegyik egy
konkrét `pytest …::test_t30_0N_<név>` **szelektorral**. A `check-log.md`-ben viszont **egyetlen
összevont** futás áll (`pytest test/integration/cycle_30_concurrency_test.py` — teljes fájl,
szelektor nélkül), és ez az egy sor a **`Task` cellájában egy intervallumot** hordoz
(`T030a-T037`), tehát mind a nyolc taskra rávezetve.

Két következménye van, és mindkettő súlyos:
- **Ha a `06` szó szerint, egyenként futtatta volna a parancsokat, a `T035`–`T037` azonnal
  hibával állt volna le**: a szelektorokban szereplő függvénynevek
  (`::test_t30_05_health_endpoint_quietness` stb.) **már nem is léteztek** a fájlban, mert a
  `T025`–`T027` időközben átnevezte őket. A `tasks.md` és a kód szétcsúszása **egy hibaüzenetként
  jelentkezett volna**, minden tartalmi ítélet nélkül. Ez a legkorábbi és legolcsóbb fogópont az
  egész láncban.
- **Az intervallumos `Task` cella a `RED1` joinját (F1) is megeteti:** ha egy naplósor nyolc
  taskra hivatkozhat, a „minden `[RED]` taskhoz van `✗` sor” join formálisan teljesíthető
  egyetlen összevont futással. **Ezért az F1 nem állhat önmagában** — a `check-log.md`
  fegyelmét (egy sor = egy task) előbb ki kell kényszeríteni (F7, 27. szakasz).

A keret ezt **félig már deklarálja:** a `TX1` szabály (`prompts/skills-hu/04-write-tasks.md:213`,
`shared-hu/quality-check-tasks.md:17`, mérve az `analyze-gate-check.py:1516`
`check_task_test_refs`-ben) kimondja, hogy *„egy teszt-futtató `[CHECK]` pontosan egy
teszt-azonosítót futtat”* — de ez **a `tasks.md` szövegére** vonatkozik, és a `TC-NN`/`TS-NN`
azonosítók számát méri. Azt, hogy a `06` **valóban** úgy is futtatta-e, semmi nem ellenőrzi.

**(6) Nincs kereszt-ellenőrzés a `[CHECK]` parancsok szelektorai és a tesztfájl tartalma között.**
Az `analyze-gate-check.py` a `TC-NN`/`TS-NN` szintű azonosítókat egyezteti, de a shell-parancsba
írt **konkrét függvényneveket** (`::test_xyz`, `-t "<név>"`, `-k <minta>`) sem egymással, sem a
tényleges forrásfájllal nem veti össze. Ez a hibaosztály **az implementáció közben keletkezik**
(a `06` átnevez egy tesztet, a később futó `[CHECK]` a régi nevet őrzi), tehát az `05-analyze`-ban
**elvileg sem** fogható meg — a helye a `07` indulása.

**(7) A review `fallback` ágon futott, és a fallback nem hordozza a checklistet.**
A `reviewer` subagent listája explicit tartalmazza a *„Teszt lefedettség: a tesztek tényleg az
új logikát fedik-e le”* szempontot — pontosan azt, ami az `assert True` stubokat elkapta volna.
A `cycle-30`-nál viszont a review a **fő ágensben, fallback módban** futott, és ott a diff
felületes összegzése történt a checklist tételes végigjárása helyett. A `07`
(`prompts/skills-hu/07-validate.md:363–365`) **helyesen megköveteli a fallback jelölését** a
riportban (ez meg is történt), de **nem viszi át a szempontlistát a fallback ágra** — az a
`reviewer.md`-ben él, amit a fallback definíció szerint nem olvas.

> **Ez az én F5-ömet is korrigálja:** a `reviewer` promptjának élesítése (26.2)
> **ebben a ciklusban nulla hatással lett volna**, mert az a prompt nem is futott. A hiányzó
> mechanizmus nem a szempont szövege, hanem hogy a **két végrehajtási ág ugyanazt a listát
> kapja** (F9, 28. szakasz).

**(8) *(megfigyelés, nem rés)* A JUnit XML minden `test_*` esetre `time="0.000"`-t rögzített.**
Egy „konkurencia”-nak nevezett teszt, amely 0 ms alatt lefut, gyanús. Ez **heurisztika**, nem
bizonyíték (egy valódi unit teszt is lehet 0 ms) — ezért **javaslat-szintű** jelzésként érdemes
beépíteni (F6, 29. szakasz), soha nem FAIL-ként.

### 20.3 Miért nem elég a prózai anti-stub szabály

Az eset elemzésekor kézenfekvő javaslat: *anti-stub szabály a `06` promptjába, teszt-tartalom-
ellenőrzés a `reviewer` promptjába*. Ez a keret **saját tanulságai szerint** nem tart:

- a `7/h` elv: *„a padló önmagában nem termel részletet”* — a szabály, amit ugyanannak az
  ágensnek kell a **saját kimenetére** alkalmaznia, gyenge modellen elsőként esik ki;
- a `7/j` elv: *„a státusz-mező önbevallás — a FOGADÓ fázis ellenőrizzen”* — az implementálónak
  **érdeke a pipa**, tehát nem ő a jó ellenőr;
- a `reviewer` **nem determinisztikus kapu**: LLM-ítélet, ami épp ebben az esetben elmaradt.

Ezért a B rész **hét determinisztikus checket** vezet be, és a prózai szabály (F5) csak
**másodlagos** megerősítés. A legerősebb jelek ingyen vannak: **egy vacuous teszt fizikailag nem
tud vörös lenni**, és **egy nem létező függvénynévre hivatkozó parancs fizikailag hibával áll le**.

> **A „prózai” és a „szerkezeti prózai” szabály nem ugyanaz.** Az F5 *kérés* (az ágens ne
> akarjon stubot írni) — ezért másodlagos. Az F9 viszont **szerkezeti**: a review-szempontlista
> **fizikailag ott van** mindkét végrehajtási ágon (subagent és fallback), build-time
> beemeléssel — nem az ágens jószándékán múlik, hogy megtalálja. Ez a keret `D13` mintája
> (a fix-módok és a minőségi kapuk már így élnek), és ezért **nem** másodlagos.

---

## 21. Lezárt döntések (B rész)

- [x] **BD1 — F1: RED-bizonyíték, ÚJ FORMÁTUM NÉLKÜL.** A `check-log.md` tábla `Eredmény`
  oszlopa ma is `✗ X passed / Y failed` vagy `✓ …` alakú, és van `Task` oszlopa. A szabály tehát
  a meglévő naplón mérhető: **minden `[RED]` markerű task azonosítójához tartozik legalább egy
  `✗` sor a `check-log.md`-ben.** Ehhez a `06`-ba egy új lépés kell (a `[RED]` task után
  **azonnal** futtatni a célzott tesztet és naplózni a bukást), a `07` kapujába pedig a join.

- [x] **BD2 — F1 kivétel-ág: `RED-EXEMPT`.** Nem minden `[RED]` task tud bukni: a `TREGn`
  regressziós taskok meglévő tesztfájlt frissítenek, és a teszt maradhat zöld. Ilyenkor a
  `check-log.md` `## Megjegyzések` szekciójába egy sor kerül:
  `RED-EXEMPT: <task-azonosító> — <egy mondat indoklás>`. A kapu ezt elfogadja.
  **A prefix nyelvfüggetlen literál** (mint a `TS-NN` vagy a `DoD-NN`), **nem** kerül a
  `status-keys.json`-ba: a scriptnek stabil horgony kell, és a napló amúgy is gépi olvasásra van.

- [x] **BD3 — F2: új script, `prompts/scripts/test-substance-check.py`.** Nem `git diff`-ből
  dolgozik (az branch-név-függő és a fix-körökben elcsúszik), hanem a **plan `TA1` adatlapjaiból**:
  a `<sec:unit_tests>` / `<sec:integration_tests>` / `<sec:e2e_tests>` szekciók
  `#### <tesztfájl path>` fejlécei adják a vizsgálandó fájlok listáját (ugyanaz a forrás, amit az
  `analyze-gate-check.py` `check_test_artifact_datasheet` már parse-ol). A scriptek `glob("*.py")`-vel
  telepítődnek (`install-helper.py` `copy_helper_scripts`), tehát az új fájl **automatikusan**
  bekerül a célprojektbe — nincs lista, amit frissíteni kell.

- [x] **BD4 — F2 hatókör: KONZERVATÍV mintakészlet.** A check **csak a bizonyosan vacuous**
  alakokat fogja meg (a hamis pozitív itt drágább, mint egy kihagyott eset, mert a fejlesztő
  bizalmát viszi el):
  | tiltott alak | miért |
  |---|---|
  | a teszt-függvény törzse **kizárólag** `assert True` / `assert 1 == 1` / `assert not False` | nem ellenőriz semmit |
  | a törzs **kizárólag** `pass` / `...` / `return` / `return None` | üres váz |
  | a törzs **kizárólag** komment(ek) + a fentiek | ua. |
  | a törzsben **egyetlen assert/expect sincs** és nincs `raise`/`pytest.fail`/`throw` sem | nincs állítás |
  **Nem** vizsgálunk coverage-küszöböt, asszertáció-darabszámot, mutation scoret, és nem
  minősítjük az asszertáció *tartalmát* — az LLM-ítélet, nem kapu.

- [x] **BD5 — F3: `EV6` a `run-tests.py`-ba, a futtatás UTÁN.** Ha egy futtatási kategória
  `<field:f_environment>` értéke nem lokális (a meglévő `env_is_local()` dönti el), akkor a kör
  bizonyítékai közt kell lennie olyan audit-artefaktumnak, amely **(a)** a kör alatt keletkezett
  és **(b)** tartalmazza a cél-hostot.
  **Óvatossági ág (kötelező):** ha a projekt `conventions.md`-je a `## <sec:cv_test_reporting>`
  (TR3) táblájában **nem deklarál** ilyen audit-artefaktumot, a check **javaslat** (nem FAIL) —
  nem minden projektnek van REST-audit naplója, és egy ilyen projektet nem bukatunk meg olyanért,
  amit nem is vállalt. FAIL **csak akkor**, ha a tábla deklarál audit-artefaktumot, de az a
  cél-hostot nem tartalmazza vagy nem a körben keletkezett.

- [x] **BD6 — F4: mtime-padló a `report-gate-check.py` `check_artifact()`-jába.** Referencia-idő:
  a kör-mappa `results.json`-jának mtime-ja, vagy — ha nincs — a kör-mappa létrejötte.
  **Ha egyik sem megállapítható, a check kimarad** (nem találgat, nem bukat).

- [x] **BD7 — Nincs új `plan.md`-mező és nincs új státusz-kulcs.** Ellenőrizve mind a négy
  checkre: az F1 a `tasks.md` markereiből és a `check-log.md`-ből dolgozik, az F2 a plan meglévő
  `TA1` adatlapjaiból, az F3 a meglévő `<field:f_environment>` oszlopból és a `conventions.md`
  TR3 táblájából, az F4 fájlrendszer-metaadatból. **Ezért a B rész az A résztől független**, és
  a `03b` skill (A rész) szövegéhez sem kell hozzányúlni.

- [x] **BD8 — Új szabály-ID-k:** `RED1` (RED-bizonyíték), `TB1` (vacuous teszt-törzs tilalma),
  `TB2` (szelektor-létezés), `TB3` (futásidő-heurisztika, javaslat), `CK1` (`[CHECK]`
  végrehajtási integritás), `EV6` (forgalmi bizonyíték), `TR7` (artefaktum-frissesség),
  `RV-FB1` (a review-checklist mindkét ágon). Ezek a `meta-improve-prompts.md` új `7/l`
  elvében kapnak indoklást (30.3).

- [x] **BD9 — F7 (`CK1`) a legelső teendő, mert az F1 rá épül.** A `check-log.md` fegyelme
  (**egy sor = egy task-azonosító**, intervallum és felsorolás tilos) és a
  task↔parancs join nélkül a `RED1` join megetethető egyetlen összevont futással (20.2/b (5)).
  A végrehajtási sorrend (32. szakasz) ezért F7-tel kezd, nem F1-gyel.

- [x] **BD10 — F8 (`TB2`) ugyanabba a scriptbe kerül, mint az F2.** A
  `test-substance-check.py` már beolvassa a tesztfájlokat; a szelektor-létezés ugyanazon
  fájlokon egy második check. **Nem** külön script: két script, ami ugyanazokat a fájlokat
  olvassa, kétszer fizet és kétszer romlik el.
  A `tasks.md` `[CHECK]` parancsainak parse-olása viszont **új bemenet** a scriptnek — ezért kap
  egy `--tasks` ágat (alap: a ciklus-mappa `tasks.md`-je).

- [x] **BD11 — F9 (`RV-FB1`): a `reviewer` szempontlistája közös blokkba kerül.** Új fájl:
  `prompts/shared-{hu,en}/review-checklist.md`, a mai `agents-{hu,en}/reviewer.md`
  `## <sec:review_criteria>` (magyar szövegben: `## Ellenőrzési szempontok`) szekciójának
  **szó szerinti** tartalmával. Beemeli: a `reviewer.md` (a mai helyén) **és** a
  `07-validate.md` reviewer-**fallback** szekciója. Ez a `D13` minta: a fallback nem olvassa a
  subagent promptját, tehát a listát **fizikailag** meg kell kapnia.

- [x] **BD12 — F6 (`TB3`) SOHA nem FAIL.** A JUnit `time` attribútum heurisztika: egy valódi
  unit teszt is lefuthat 0 ms alatt. Kimeneti szint: **javaslat** (a `run-tests.py`
  `results.json`-jába és a kimenetbe), és csak akkor, ha a kategória `<field:f_environment>`-je
  **nem lokális** vagy a teszt neve olyan viselkedésre utal, ami nem lehet 0 ms
  (a konzervatív szabály: **minden** eset `time="0.000"` az adott fájlban → egy javaslat-sor).
  Küszöböt, arányt és „lassú teszt” figyelmeztetést **nem** vezetünk be.

- [x] **BD13 — A `TX1` szabály szövege nem változik.** A `04`/`quality-check-tasks` `TX1`
  helyesen mondja ki, hogy egy `[CHECK]` egy tesztet futtat; a rés nem a szabályban, hanem a
  **végrehajtás ellenőrzésében** van. Az `analyze-gate-check.py` `check_task_test_refs`
  (TI2/TX1) checkjéhez **nem nyúlunk** — a `CK1` a `06` naplóján és a `07` kapujában mér.

---

## 22. F1 — RED-bizonyíték (`RED1`)

- [x] **22.1 — Új lépés a `06` per-task folyamatába (HU+EN).**
  `prompts/skills-{hu,en}/06-implement.md`, a *Végrehajtási szabályok* **8. pontja UTÁN**, új
  **8/b** pontként (a 8. pont a `[CHECK]` task végrehajtása — ez a `[RED]` taskra vonatkozik):

  ```md
  8/b. **🔴 `[RED]` task lezárása: a tesztnek BUKNIA kell (RED1).** Egy `[RED]` task nem a
      tesztfájl létrejöttével készül el, hanem azzal, hogy a megírt teszt **vörös** — ez a
      TDD-ciklus első fele, és **ez az egyetlen bizonyíték arra, hogy a teszt tényleg ellenőriz
      valamit**. Ezért a `[RED]` task pipálása előtt:
      1. futtasd le a **célzott** tesztet (a plan `TA1` adatlapjának `<field:f_test_run>`
         parancsát, az egy fájlra/esetre szűkítve — ne a teljes suite-ot);
      2. a futásnak **nem-nulla** kilépő kóddal, `failed > 0` eredménnyel kell zárnia;
      3. naplózd a `check-log.md`-be **a `[RED]` task azonosítójával** és `✗` eredménnyel
         (a napló amúgy is minden próbát rögzít).
      **Ha a teszt ELSŐ futásra zöld, a task NEM kész** — a teszt vagy nem azt ellenőrzi, amit a
      plan előír, vagy üres váz (`assert True`, `pass`, asszertáció nélküli törzs). Ilyenkor a
      tesztet kell megírni, nem a taskot lezárni. Egy zöld `[RED]` a leggyakoribb néma
      teszt-csalás: a suite `X passed`-et jelent, a `DoD` bizonyítékot kap, és a validálás
      `PASS`-ra zár anélkül, hogy bármit ellenőriztünk volna.
      **Kivétel — `RED-EXEMPT`:** ha a `[RED]` task **meglévő** tesztet frissít (jellemzően a
      `TREGn` regressziós taskok), és a teszt a változás után is joggal zöld, akkor a
      `check-log.md` `## <sec:notes>` szekciójába írj egy sort:
      `RED-EXEMPT: <task> — <miért nem tud bukni>`. Indoklás nélkül a task nem zárható.
  ```

  A 8. pont *„Csak zöld `[CHECK]` után jelölhető kész a csoport”* mondata **marad** — az a
  `[GREEN]` feltétele; a 8/b a `[RED]`-é. Írd oda egy félmondatban, hogy a kettő **nem
  helyettesíti egymást**.

- [x] **22.2 — A `check-log.md` szekció bővítése (HU+EN).** Ugyanabban a fájlban a
  *`[CHECK]` futásnapló (TR5)* szekció **Oszlopok** listája alá:
  - az **Eredmény** oszlop leírásához egy mondat: a `✗` a `[RED]` taskoknál **nem hiba, hanem a
    kötelező bizonyíték** (RED1);
  - a **`<sec:notes>` szekció** leírásához: itt élnek a `RED-EXEMPT:` sorok is.

- [x] **22.3 — A `check-log` projekt-nyelvi sablonja (HU+EN).**
  `prompts/lang/{hu,en}/06-implement.md`, a `check-log-sablon` horgony: a példa-tábla kapjon
  **egy új sort**, amely egy `[RED]` task vörös futását mutatja, és a `## Megjegyzések` blokk
  egy `RED-EXEMPT:` példasort:
  ```md
  | 2026-08-07 09:58 | T003 | 1/3 | normál | `npx tsx --test test/unit/token-store.test.ts` | ✗ 0 passed / 1 failed — `refreshes once for 5 parallel readers` (RED1: a teszt megvan, az implementáció még nincs) |
  ```
  ```md
  - **RED-EXEMPT: TREG1** — a `test/e2e/auth-login.spec.ts` meglévő tesztje a middleware-változás után is joggal zöld; a task csak a szelektort frissíti.
  ```
  A magyar és az angol sablon **ugyanezt** a két sort kapja (az angolban `RED-EXEMPT` prefix
  **változatlanul**, csak az indoklás angol).

- [x] **22.4 — A join a `07` kapujába: `check_red_proof()` a `validate-gate-check.py`-ba.**
  A script ma `check_tasks(cycle, rep, stage)` néven olvassa a `tasks.md`-t, és van `close`
  szakasza — ide illik:
  ```python
  def check_red_proof(cycle, rep, stage):
      """RED1 — minden [RED] taskhoz van bukott futás a check-log.md-ben.

      Egy `assert True` stub fizikailag nem tud vörös lenni: ez az egyetlen
      NEM ítélet-igényes jel arra, hogy a teszt ellenőriz valamit."""
      if stage != "close":
          return
      # 1. a tasks.md [RED] taskjainak azonosítói (T001 / TREG1 / TLAST1 alakok)
      # 2. a check-log.md sorai: | idő | Task | próba | mód | parancs | eredmény |
      #    → task-azonosító -> {"✓", "✗"} halmaz
      # 3. RED-EXEMPT: <task> sorok a jegyzet-szekcióból → felmentve
      # 4. minden [RED] task, aminek nincs `✗` sora és nincs felmentése → rep.bad(...)
  ```
  Bekötés a `main()`-be a `check_tasks(...)` után. **Guard (kötelező):** ha a `check-log.md`
  **nem létezik**, a check `rep.info(...)`-ot ad, nem `bad`-et — régi ciklusokban a napló nem
  feltétlenül van meg, és egy visszamenőleges bukás csak zajt termel.

  > **🔴 Ez a join az F7 (`CK1`) NÉLKÜL megetethető.** A `cycle-30` naplójában egyetlen sor
  > `Task` cellája `T030a-T037` intervallumot hordozott — egy ilyen sorral a „minden `[RED]`
  > taskhoz van `✗`” formálisan teljesíthető egyetlen összevont futással. Ezért a
  > **task-azonosító parse-olása szigorú:** a `Task` cella pontosan **egy** azonosítót
  > tartalmazhat (`T001`, `TREG1`, `TLAST1`, `T030a`); ha intervallumot (`-`), felsorolást (`,`)
  > vagy több azonosítót tartalmaz, az **`CK1` megállapítás**, nem elfogadott sor.
  > **Ezért az F7-et az F1 ELŐTT kell megcsinálni** (BD9, 32. szakasz).

- [x] **22.5 — A `07` skill szövege (HU+EN).** `prompts/skills-{hu,en}/07-validate.md`, az
  **A/2 + B** kapu-blokk (`validate-gate-check.py … --stage close`) felsorolásába egy tétel:
  *„…, és a `[RED]` taskok bukás-bizonyítéka a `check-log.md`-ben (RED1)”*. Plusz a bukás-ág
  mellé egy mondat: **egy zöld `[RED]` nem javítható a napló átírásával** — a tesztet kell
  megírni; ez a `VD3` anti-teszt-csalás garde alá tartozik.

- [x] **22.6 — Verifikáció.** Egy éles (vagy gyártott) ciklus mappán:
  ```bash
  python3 prompts/scripts/validate-gate-check.py <ciklus-mappa> --stage close
  ```
  **Célzott próba:** vegyél egy ciklust, ahol a `check-log.md`-ben egy `[RED]` taskhoz csak `✓`
  sor van → a kapunak **buknia kell**; írj be egy `RED-EXEMPT:` sort ugyanahhoz a taskhoz →
  **át kell mennie**. A `cycle-30` naplója (ha elérhető) élő regressziós teszt: azon a kapunak
  bukni kell.

---

## 23. F2 + F8 — Vacuous-test kapu (`TB1`) és szelektor-létezés (`TB2`)

- [x] **23.1 — Új script: `prompts/scripts/test-substance-check.py`.**
  **Bemenet:** `cycle_dir` (pozicionális), `--repo-root` (alap: `.`), opcionálisan
  `--files <path> …` (célzott futtatás egy fájllistára).
  **Működés:**
  1. beolvassa a `plan.md`-t, és a `<sec:unit_tests>` / `<sec:integration_tests>` /
     `<sec:e2e_tests>` szekciók `#### <path>` fejléceiből kigyűjti a tesztfájl-útvonalakat
     (a `(új)` / `(bővítés)` utótagot levágva; a szekciónevek a `lang_keys.py` `sec()`-jén
     keresztül — ne írd be literálisan);
  2. minden létező fájlt beolvas, és **teszt-függvényenként** vizsgál. Függvény-felismerés
     nyelvenként, konzervatívan:
     - Python: `def test_*` / `async def test_*`;
     - JS/TS: `it(`, `test(` callback;
     - egyéb kiterjesztés → **kimarad** (nem találgat, `info` sorral jelzi);
  3. a BD4 mintakészlet szerint ítél; minden találat egy sor:
     `✗ <fájl>:<sor> <függvénynév> — <melyik minta>`;
  4. **kimenet és kilépő kód:** `0` = nincs találat (vagy nincs mit vizsgálni),
     `1` = van vacuous teszt, `2` = használati hiba (nincs `plan.md`, nincs ciklus-mappa).
  **Nyelvi függés:** a script a `lang-keys.json`-t használja (mint a többi kapu), tehát
  nyelvfüggetlen; a kimenete a projekt nyelvén beszél.
  **Kötelező docstring** a fájl elején, a `RED1`-re és a `cycle-30`-ra hivatkozva — a többi
  script mintája szerint (miért létezik ez a kapu, mit fogott volna meg).

- [x] **23.2 — A `06` fázis-vég hívja (HU+EN).** `prompts/skills-{hu,en}/06-implement.md`, a
  fázis-záró szekcióban (ahol a `check-log.md` és a riport-készlet zárul), a
  `<!-- INCLUDE:shared/python-cmd.md -->` mellé:
  ```bash
  python3 <platform-scripts-mappa>/test-substance-check.py specs/cycle-NN-<cycle-name>
  ```
  `1` esetén **a fázis nem zárható**: a felsorolt teszt-függvényeket meg kell írni. Kimondva:
  *ez nem „a teszt majd a 07-ben megíródik” — a `[RED]` task terméke a teszt, és üres váz esetén
  a task nincs elvégezve (RED1).*

- [x] **23.3 — A `07` A/2 kapu-blokk hívja (HU+EN).** `prompts/skills-{hu,en}/07-validate.md`,
  a `validate-gate-check.py` hívása mellé, önálló parancsként (a `--stage close` szakaszban).
  `1` esetén a kör **FAIL**, és a bukás típusa **teszt-hiba** → az `implement-fixer` indul a
  `## <sec:validation_fixes>` szekcióval. **A `VD3` garde ide is szól:** a vacuous teszt javítása
  a teszt **megírása**, nem a check kikapcsolása vagy a fájl kivétele a plan adatlapjaiból.

- [x] **23.4 — Verifikáció.** Gyárts egy próbafájlt a scratchpadba (`def test_x(): assert True`),
  vedd fel a plan `<sec:unit_tests>` szekciójába `#### <path>` fejléccel, és futtasd:
  ```bash
  python3 prompts/scripts/test-substance-check.py <ciklus-mappa> --repo-root .
  ```
  Elvárás: `exit 1` és a függvény megnevezése. Utána írj bele egy valódi asszertációt →
  `exit 0`. **Hamis-pozitív próba (kötelező):** egy `pytest.raises` blokkot tartalmazó teszt és
  egy `expect(...)` alapú TS-teszt **ne** bukjon.

- [x] **23.5 — F8: szelektor-létezés (`TB2`) — UGYANEBBE a scriptbe (BD10).** Második check a
  `test-substance-check.py`-ban, új `--tasks <path>` bemenettel (alap: a ciklus-mappa
  `tasks.md`-je):
  1. a `tasks.md` **`[CHECK]`** taskjainak parancs-celláiból (backtickes parancs) kigyűjti a
     **teszt-szelektorokat**, három alakban:
     - `pytest <fájl>::<függvénynév>` (és `::<Class>::<függvény>`),
     - `-t "<név>"` / `--test-name-pattern "<név>"` (node:test, vitest, jest),
     - `-k <minta>` (pytest kulcsszó-szűrő) — itt csak **literál** minta esetén ítél, logikai
       kifejezésnél (`and` / `or` / `not`) `info` sorral kimarad;
  2. minden szelektorra megnézi, hogy a hivatkozott fájl **tartalmazza-e** a nevet — egyszerű
     szöveges keresés, **nem AST**: egy átnevezés így is kiderül, és nincs nyelv-specifikus
     törékenység;
  3. **ítélet:** hiányzó név → `✗ <task> — a <fájl> nem tartalmazza a <név> tesztet (TB2)`.
     Ez **Must Fix** szintű, `exit 1`.
  **Guard:** ha a hivatkozott fájl nem létezik, azt is jelezze — de ha a fájl a plan
  `<sec:planned_changes>`-ában **új fájlként** szerepel és a `06` még nem futott, `info`.

  > **Miért ez a legkorábbi fogópont:** a `cycle-30`-ban a `T035`–`T037` `[CHECK]` parancsai
  > olyan függvénynevekre hivatkoztak, amelyeket a `T025`–`T027` időközben **átnevezett**. Ha a
  > `06` egyenként futtatja őket (F7), a pytest **azonnal** hibát ad — semmilyen tartalmi
  > ítéletre nincs szükség. Ez a check ugyanezt **futtatás nélkül** is megmondja.

- [x] **23.6 — A `TB2` a `07` INDULÁSÁNÁL is fut.** Egy elorphanodott szelektor a kör
  **elején** derüljön ki, ne a végén. `prompts/skills-{hu,en}/07-validate.md`, az Előfeltétel
  szekcióba, a `validate-gate-check.py --stage start` hívása mellé:
  ```bash
  python3 <platform-scripts-mappa>/test-substance-check.py specs/cycle-NN-<cycle-name> --selectors-only
  ```
  A `--selectors-only` csak a `TB2`-t futtatja; a `TB1` vacuous-vizsgálat a lezárásnál értelmes,
  amikor a tesztek már készek. **Verifikáció:** nevezz át kézzel egy teszt-függvényt a fájlban →
  a checknek buknia kell; állítsd vissza → át kell mennie.

---

## 24. F3 — Forgalmi bizonyíték nem-lokális kategóriánál (`EV6`)

- [x] **24.1 — `run-tests.py`: új `--conventions` kapcsoló.** A script ma nem kapja meg a
  `conventions.md` útvonalát (az `analyze-gate-check.py` és a `report-gate-check.py` igen).
  Alap: `conventions.md` a repó gyökerében; ha nem létezik, a 24.2 check **kimarad** egy `info`
  sorral (nem bukat).

- [x] **24.2 — `check_traffic_evidence(...)` a futtatás UTÁN.** Az `EV6` logika:
  1. a `conventions.md` `## <sec:cv_test_reporting>` (TR3) táblájából kigyűjti az
     **audit-jellegű artefaktumokat** — azokat a sorokat, amelyek a kör-mappán belüli
     mappát/fájlt deklarálnak (a `report-gate-check.py` már ugyanezt a táblát parse-olja: **a
     parse-olót emeld ki közös helyre vagy ismételd meg pontosan, ne találj ki harmadik alakot**);
  2. minden olyan kategóriára, ahol `not env_is_local(row["kornyezet"])`:
     - kigyűjti a cél-hostot a `Parancs` és az `Előfeltétel` cellából (a meglévő host-felismerő
       mintát használva — az `EV3` már ezt teszi);
     - megnézi, hogy a kör-mappában van-e olyan audit-artefaktum-fájl, amely **(a)** a kör
       kezdete után keletkezett (`results.json` mtime vagy a kör-mappa létrejötte) és **(b)**
       tartalmazza a cél-hostot;
  3. **ítélet:** ha a TR3 tábla deklarál audit-artefaktumot és nincs ilyen fájl → a kategória
     **FAIL** (`failed_items` bejegyzéssel, a `results.json`-ba is beírva). Ha a tábla **nem**
     deklarál audit-artefaktumot → **javaslat** a kimenetben, nem FAIL (BD5).
  A hibaüzenet mondja ki a lényeget: *„a kategória nem-lokális környezetre szól, de a körben
  keletkezett bizonyítékok egyike sem tartalmazza a `<host>` címet — a teszt vagy nem futott, vagy
  nem oda futott”*.

- [x] **24.3 — A plan-oldal ellenőrzése: NINCS teendő.** Ellenőrizve (BD7): az `EV6` a meglévő
  `<field:f_environment>` oszlopból és a `conventions.md` TR3 táblájából dolgozik — **nem kell új
  plan-mező**, tehát a `03`/`03b` skill szövege és a `analyze-gate-check.py` plan-checkjei
  változatlanok. Ezt a pontot csak **pipáld ki** az ellenőrzés után; ha mégis új mezőt találsz
  szükségesnek, **állj meg és jelezd** (az A rész vágási táblája függ ettől).

- [x] **24.4 — A `07` szövege (HU+EN).** A `run-tests.py` hívása körüli magyarázatba egy blokk:
  az `EV1–EV5` a **célpontot** védi a futtatás előtt, az `EV6` a **forgalmat** a futtatás után —
  *egy zöld teszt nem bizonyítja, hogy egyáltalán elindult kérés*. Egy mondat a `cycle-30`-ról,
  a `7/g` blokk stílusában (az konkrét esettel indokol, ezért marad meg).

- [x] **24.5 — Verifikáció.** A `cycle-30` kör-mappáján (vagy gyártott másolatán): a
  `rest-logs` régi, `127.0.0.1`-es fájljaival a nem-lokális kategória **FAIL** legyen; egy
  frissen keletkezett, a dev hostot tartalmazó fájllal **PASS**. Külön próba: olyan projekt,
  amelynek TR3 táblája nem deklarál audit-artefaktumot → **nem bukhat** (csak javaslat).

---

## 25. F4 — Artefaktum-frissesség (`TR7`)

- [x] **25.1 — mtime-padló a `check_artifact()`-ba.** `prompts/scripts/report-gate-check.py`:
  a függvény kapjon egy `since=None` paramétert.
  - fájlnál: ha `since` adott és `target.stat().st_mtime < since` → `(False, "ELAVULT: … (a kör előtt keletkezett)")`;
  - mappánál: a `files` szűrése `st_mtime >= since`-re, és ha így **egy** fájl sem marad →
    `(False, "CSAK ÖRÖKÖLT FÁJLOK: …")`. A visszaadott darabszám és méret is a **friss** fájlokra
    értendő.
- [x] **25.2 — A referencia-idő megállapítása.** A hívó helyen (a kör-/fázis-mappa
  feloldása után): `results.json` mtime → ha nincs, a kör-mappa `st_mtime` → ha egyik sem,
  `since=None` és a check **kimarad** (BD6). A kimenetben egy sor mondja meg, melyik
  referenciát használta — különben egy „ELAVULT” üzenet nem debuggolható.
- [x] **25.3 — A `06` riport-fázisa (TR6) is érintett.** Ha a projekt az `implement`-et
  riport-fázisnak deklarálja, a `report-gate-check.py` ott is fut — nézd meg, hogy a
  `test-report/implement/` esetén a referencia-idő értelmes-e (ott nincs `results.json`).
  Ha nem, ott `since=None` maradjon.
- [x] **25.4 — Verifikáció.** Egy kör-mappán állítsd vissza egy artefaktum mtime-ját
  (`touch -d '2020-01-01' <fájl>`), és futtasd a kaput → **buknia kell**; `touch <fájl>` után
  **át kell mennie**.

---

## 26. F5 — A két prózai megerősítés (másodlagos)

> **Ezek nélkül is működik az összes determinisztikus kapu** (F1–F4, F6–F9), és önmagukban nem
> is elégségesek (20.3). Azért kellenek, hogy az ágens **ne akarjon** stubot írni — a kapu pedig
> azért, hogy ne **tudjon**.
>
> **A 26.2 önmagában kevés — az F9 (28. szakasz) teszi hatásossá.** A `cycle-30`-nál a review a
> **fallback** ágon futott, tehát a `reviewer.md` promptja **nem is futott le**: egy ott élesített
> kérdésnek nulla hatása lett volna. A 26.2 a subagent-ágat javítja, a 28. szakasz pedig azt,
> hogy a lista a fallback ágon is **fizikailag jelen** legyen.

- [x] **26.1 — Anti-stub mondat a `06` fázis-szintű garde-jába (HU+EN).** A `06` ma a
  **fix-módra** tartalmaz anti-teszt-csalás védőhálót (a `VD3` párja). A **normál**
  implementációs fázisra kerüljön be egy tömör tilalom, a `RED1`-re hivatkozva: teszt-író task
  nem zárható üres vázzal (`assert True`, `pass`, asszertáció nélküli törzs), és a
  „majd a 07 megírja” **nem** ág.

- [x] **26.2 — Egy KEMÉNY kérdés a `reviewer`-be (HU+EN).** `prompts/agents-{hu,en}/reviewer.md`
  ma ennyit mond: *„Teszt lefedettség: A tesztek tényleg az új logikát fedik-e le…”* — ez
  általános. Helyette/mellette egy **eldönthető** kérdés a `<status:must_fix>` kategóriába:
  *„Van-e a diffben olyan új vagy módosított teszt-függvény, amelynek törzsében nincs a rendszer
  válaszához vagy állapotához kötött asszertáció (csak `assert True`, `pass`, konstans
  összehasonlítás, vagy kizárólag a mock saját visszatérési értékének ellenőrzése)? Ha igen, az
  `<status:must_fix>` — a teszt zöld, de nem bizonyít semmit.”*
  Egy mondat indoklás is kerüljön oda (a `cycle-30`), hogy egy gyengébb modell se általánosítsa el.

---

## 27. F7 — A `[CHECK]` végrehajtási integritása (`CK1`)

> **Ez a B rész első teendője (BD9):** az F1 joinja e nélkül megetethető, és ez a legkorábbi,
> legolcsóbb fogópont az egész láncban (20.2/b (5)).

- [x] **27.1 — A `06` szó szerinti, egyenkénti futtatása (HU+EN).**
  `prompts/skills-{hu,en}/06-implement.md`, a *Végrehajtási szabályok* **8. pontjába**
  (`[CHECK]` task végrehajtása), az első alpont fölé:

  ```md
  - **🔴 A parancsot SZÓ SZERINT, ÖNMAGÁBAN futtasd (CK1).** A `[CHECK]` task parancsát
    **pontosan úgy** add ki, ahogy a task írja — a teszt-szűrővel (`::<függvény>`, `-t "<név>"`,
    `-k <minta>`) együtt. **Tilos** több `[CHECK]` parancsát egy futásba vonni, a szűrőt
    elhagyni („futtatom az egész fájlt, az is lefedi”), vagy egy bővebb futás eredményét
    több taskra rávezetni. Egy `[CHECK]` = egy futás = **egy** naplósor **egy** task-azonosítóval.
    **Miért:** a szűrő az egyetlen dolog, ami a taskot a `plan.md` tesztesetéhez (`TC-NN`/`TS-NN`)
    köti — enélkül a pipa nem azonosítóhoz kötött állítás (`TX1`). És ami ennél sokkal
    fontosabb: ha a teszt neve az implementáció közben **megváltozott**, a szűrt parancs
    **azonnal hibát ad**, az összevont futás viszont zölden átmegy. Egy éles ciklusban nyolc
    `[CHECK]` task helyett egyetlen, szűrő nélküli futás került a naplóba, három szelektor pedig
    már nem létező függvénynévre hivatkozott — a `tasks.md` és a kód szétcsúszása így teljesen
    láthatatlan maradt.
    **Ha a parancs hibát ad, mert a szelektor nem talál semmit** (`no tests ran`,
    `ERROR: not found`), az **nem** futtatási hiba, amit összevonással kell megkerülni: vagy a
    tesztet nevezték át (akkor a `tasks.md` parancsát kell javítani, és a javítást jelezni), vagy
    a teszt nem készült el (akkor a `[RED]`/`[GREEN]` task nincs elvégezve).
  ```

- [x] **27.2 — A `check-log.md` fegyelme: egy sor = egy task (HU+EN).** Ugyanabban a fájlban a
  *`[CHECK]` futásnapló (TR5)* szekció **Oszlopok** listájában a **Task** oszlop leírásához
  (ha nincs ilyen alpont, hozd létre a `Próba` fölé):
  ```md
  - **Task** — **pontosan egy** task-azonosító (`T001`, `T030a`, `TREG1`, `TLAST1`).
    Intervallum (`T030a-T037`), felsorolás (`T031, T032`) és „több task egy sorban" **tilos**
    (CK1): a napló így nem bizonyíték, hanem összefoglaló, és a `07` kapuja nem tudja
    taskonként eldönteni, mi futott le.
  ```

- [x] **27.3 — A join a `07` kapujába: `check_command_integrity()`.**
  `prompts/scripts/validate-gate-check.py`, a `check_red_proof()` (22.4) mellé:
  ```python
  def check_command_integrity(cycle, rep, stage):
      """CK1 — a [CHECK] taskok parancsai szó szerint, egyenként futottak-e.

      1. a check-log.md minden sorának `Task` cellája PONTOSAN egy azonosító
         (intervallum/felsorolás → rep.bad);
      2. minden `[CHECK]` taskhoz van legalább egy naplósor a saját azonosítójával;
      3. a naplósor `Parancs` cellája tartalmazza a task parancsának
         TESZT-SZŰRŐ részét (`::<fn>`, `-t "<név>"`, `-k <minta>`), ha a task
         parancsában van ilyen — különben `rep.bad`: összevont/szűrő nélküli futás.
      Eltérés-ág: a `## <sec:notes>` szekcióban egy
      `CK-DEVIATION: <task> — <indok>` sor felmenti (pl. a keret nem támogatja a
      szűrést) — indoklás nélkül nem.
      """
  ```
  **Guard:** ha nincs `check-log.md`, `rep.info(...)` (mint a 22.4-ben).
  **Normalizálás:** a parancs-összevetés ne karakterre menjen (idézőjel-típus, `python` vs
  `python3`, útvonal-prefix eltérhet) — **csak a szűrő-részt** hasonlítsd, whitespace-re
  normalizálva. Ez kevesebb hamis pozitívot ad, és pont azt méri, ami elveszett.

- [x] **27.4 — A `07` skill szövege (HU+EN).** Az **A/2 + B** kapu-blokk felsorolásába:
  *„…, a `[CHECK]` parancsok szó szerinti, taskonkénti futása (CK1)”*. A bukás-ág mellé egy
  mondat: **a napló utólagos átírása nem javítás** (`VD3`) — a `[CHECK]`-eket újra kell futtatni
  egyenként.

- [x] **27.5 — Verifikáció.** A `cycle-30` naplóján (vagy másolatán) a kapunak **buknia kell**
  (intervallumos `Task` cella + szűrő nélküli parancs). Egy rendben lévő ciklus naplóján
  **át kell mennie** — ez a 31.6 hamis-pozitív próba része.

---

## 28. F9 — A review-checklist mindkét végrehajtási ágon (`RV-FB1`)

- [x] **28.1 — Új közös blokk: `prompts/shared-{hu,en}/review-checklist.md`.** A mai
  `prompts/agents-{hu,en}/reviewer.md` `## Ellenőrzési szempontok` szekciójának **szó szerinti**
  tartalma (a hét pont: konvenciók · kódminőség · scope fegyelem · spec eltérés · hibakezelés ·
  teszt lefedettség · elavult kommentek/VD12). A fájl első sora a szokásos
  `<!-- Forrás-jegyzet: … -->` komment, amely megnevezi a **két** beemelőt.
  **A `## <status:must_fix>` vs `<status:suggestion>` határvonal szekció is ide kerül** — a
  fallback ágon anélkül nem tud besorolni.

- [x] **28.2 — A `reviewer.md` a blokkot emeli be (HU+EN).** A mai szekció helyére
  `<!-- INCLUDE:shared/review-checklist.md -->`, és a frontmatter `shared:` listájába a fájl.
  **A tartalom nem változik** — csak a helye.

- [x] **28.3 — A `07` fallback szekciója is beemeli (HU+EN).**
  `prompts/skills-{hu,en}/07-validate.md`, a reviewer-fallback blokk (a mai „🔴 Ha a fallback
  ágra mész…” figyelmeztetés, ~363–365. sor) **után**:
  ```md
  > **🔴 Fallback módban UGYANEZT a listát kell végigjárnod, tételesen (RV-FB1).** A fallback nem
  > „egy gyors diff-összegzés": a `reviewer` subagent szempontlistája alább **szó szerint** ott
  > van, és fallback esetén **te** vagy a reviewer. Menj végig **minden** ponton, és a
  > `code-review.md`-ben nevezd meg, hol teljesül vagy hol nem — különösen a **Teszt lefedettség**
  > ponton: egy éles ciklusban épp a fallback ág futott, és épp ez a pont maradt ki, ezért nem
  > derült ki, hogy a „megírt" tesztek üres vázak (`assert True`). A fallback jelölése (fentebb)
  > az **eredetet** rögzíti, nem a szigor csökkentését engedi meg.

  <!-- INCLUDE:shared/review-checklist.md -->
  ```
  A `07` frontmatter `shared:` listájába is vedd fel a fájlt.

- [x] **28.4 — A `code-review.md` fallback-fejléce mondja meg, mit járt végig.** A `07`
  fallback-blokk `Készítette: fő ágens (fallback)` sora mellé egy második kötelező sor:
  `**Szempontlista:** RV-FB1 — mind a <N> pont végigjárva` (vagy a kihagyott pont megnevezése
  indokkal). Enélkül a fallback szigora ismét önbevallás (`7/j`).

- [x] **28.5 — Paritás + tükrök.** A `reviewer` promptja változott → a gemini `agent.json`
  tükröt regenerálni kell:
  ```bash
  python3 prompts/scripts/lang-parity-check.py
  python3 prompts/scripts/sync-gemini-agents.py && python3 prompts/scripts/sync-gemini-agents.py --check
  ```

---

## 29. F6 — Futásidő-heurisztika (`TB3`, javaslat-szint)

- [x] **29.1 — A JUnit `time` attribútum kiolvasása.** `prompts/scripts/run-tests.py`,
  a `parse_junit()` függvény ma `(passed, failed, skipped, names)` négyest ad vissza. Vedd fel az
  esetek `time` attribútumát is (a visszatérési érték bővítése helyett **külön** segédfüggvény is
  lehet, ha az a kevésbé invazív — a `results.json` szerkezetét ne törd el).

- [x] **29.2 — A javaslat-szabály (BD12 szerint, KONZERVATÍVAN).** Egy eredményfájlra
  **egyetlen** javaslat-sor akkor keletkezik, ha az adott fájl **minden** teszt-esetének `time`
  értéke `0.000` (vagy hiányzik) **és** a kategória legalább egy tesztet futtatott:
  ```
  [TB3] javaslat: a `<kategória>` kategória minden tesztje 0.000 s alatt futott le
        (<N> eset) — ha a kategória hálózati hívást, konkurenciát vagy I/O-t
        tesztel, ez üres vázra utalhat. Nem blokkol; a TB1/TB2 kapu a mérvadó.
  ```
  **Soha nem FAIL**, soha nem `failed_items`. A `results.json`-ba `suggestions` (vagy hasonló,
  már létező) kulcs alá kerül — ha nincs ilyen kulcs, vezess be egyet, de a meglévő fogyasztókat
  (`dod-check.py`, `round-log.py`) ne törd el.

- [x] **29.3 — Verifikáció.** A `cycle-30` JUnit XML-jén (vagy másolatán) a javaslatnak meg kell
  jelennie; egy normál unit-suite XML-jén, ahol van nem-nulla idő, **nem** jelenhet meg.
  **Külön próba:** egy tisztán szinkron, valóban 0 ms-os unit kategórián a javaslat megjelenik —
  ez **elfogadható zaj**, ezért nem blokkol; ellenőrizd, hogy tényleg nem befolyásolja a
  kilépő kódot.

---

## 30. Dokumentáció (B rész)

- [x] **30.1 — `README-HU.md` + `README.md`.** Három helyen:
  - a `07-validate` determinisztikus rétegének felsorolásába az új kapuk
    (`test-substance-check.py` = `TB1`/`TB2`, a `validate-gate-check.py` `RED1`- és
    `CK1`-joinja, az `EV6` a `run-tests.py`-ban, a `TR7` a `report-gate-check.py`-ban);
  - a `06-implement` leírásába a `[RED]` bukás-bizonyíték (`RED1`) és a szó szerinti,
    taskonkénti `[CHECK]` futtatás (`CK1`) egy-egy mondattal;
  - a `reviewer` sorához: a szempontlista közös blokkban él, és a **fallback ág is megkapja**
    (`RV-FB1`).
- [x] **30.2 — `berki-spec-directory-structure.md`.** Az új script (`test-substance-check.py`)
  és az új közös blokk (`shared-*/review-checklist.md`) felvétele, egy soros leírással.
- [x] **30.3 — `prompts/meta-improve-prompts.md`: új elv `7/l`.** A `7/k` (A rész) után.
  Vázlat a meglévő elvek hangján:

  *A `7/g` kimondta, hogy **egy zöld teszt nem bizonyítja, HOL volt zöld**. Egy éles ciklus
  (cycle-30) megmutatta, hogy a lánc egy lépéssel korábban is elszakad: **egy zöld teszt azt sem
  bizonyítja, hogy bármit ellenőriztünk, sőt azt sem, hogy a tervezett parancs futott le.** A
  tesztfájlba `assert True` vázak kerültek, a nyolc `[CHECK]` task helyett egyetlen, szűrő nélküli
  futás került a naplóba (annak `Task` cellájában intervallummal), három `[CHECK]` szelektor pedig
  már átnevezett függvényre hivatkozott — és mindez **zöld** volt: a `passed` számláló nőtt, a
  `dod-check.py` a teszt **nevére** joinolt, a `rest-logs` mappa korábbi körök fájljaitól telinek
  látszott, a review pedig **fallback ágon** futott, ahol a szempontlista fizikailag nem volt jelen.
  Hét determinisztikus kapu zárja: `CK1` (a `[CHECK]` szó szerint, egyenként, egy sor = egy task),
  `RED1` (minden `[RED]`-hez bukott futás — `RED-EXEMPT` indoklással felmenthető), `TB1` (vacuous
  teszt-törzs tilalma konzervatív mintakészlettel), `TB2` (a parancs szelektora létezik a
  tesztfájlban), `EV6` (nem-lokális kategóriánál a körben keletkezett bizonyíték tartalmazza a
  cél-hostot), `TR7` (a kör-mappa artefaktuma a kör alatt keletkezett), `RV-FB1` (a
  review-szempontlista build-time **mindkét** végrehajtási ágon jelen van). **Prompt-módosításnál
  három kérdés:** (a) ha egy fázis „kész” jelzése egy **számláló** vagy egy **név** egyezésén áll
  (`X passed`, teszt-név → `DoD-NN`), mi bizonyítja, hogy a számláló mögött **történt** is valami?
  (b) ha egy szabály a **tervre** vonatkozik (`TX1`: egy `[CHECK]` egy teszt), mi ellenőrzi, hogy a
  **végrehajtás** is így ment? (c) ha egy szabály egy **subagent** promptjában él, mi történik a
  **fallback** ágon, ahol az a prompt nem is fut? A prózai szabály itt szándékosan másodlagos: az
  implementálónak érdeke a pipa (`7/j`), az LLM-reviewer pedig nem kapu — a szerkezeti próza
  (a lista fizikai jelenléte mindkét ágon) viszont igen.*

- [x] **30.4 — A nyolc új ID felvétele a `README` szabály-jegyzékébe**, ha van ilyen
  (`grep -n "TR6\|EV5\|TX1" README-HU.md` mutatja a helyét): `CK1`, `RED1`, `TB1`, `TB2`, `TB3`,
  `EV6`, `TR7`, `RV-FB1` — plusz a `RED-EXEMPT` és a `CK-DEVIATION` naplójelölés.

---

## 31. Kapuk és elfogadási kritériumok (B rész)

- [x] **31.1** `python3 prompts/scripts/lang-parity-check.py` → hiba nélkül (a `06`, `07`,
  `reviewer`, az új `shared-*/review-checklist.md` és a `lang/*/06-implement.md` mindkét fán
  módosult/létrejött).
- [x] **31.2** `python3 prompts/scripts/lang-parity-check.py --strict` → 0 (az új közös blokknak
  **mindkét** nyelvi fán léteznie kell).
- [x] **31.3** `python3 prompts/scripts/sync-gemini-agents.py --check` → 0 (a `reviewer` prompt
  változott; előtte írás módban regenerálva).
- [x] **31.4** Telepítési füstteszt: a `test-substance-check.py` megjelenik mind az öt platform
  scripts-mappájában, és a telepített `06`/`07`/`reviewer` fájlokban **nincs** feloldatlan
  `INCLUDE:` marker vagy `<sec:`/`<field:`/`<status:` token. Külön ellenőrzés: a
  `review-checklist.md` tartalma **kétszer** jelenik meg a telepített fában (a `reviewer`-ben és
  a `07`-ben) — ez **szándékos** (RV-FB1), nem duplikáció-hiba.
- [x] **31.5** Mind a hét check **célzott bukás-próbája** lefutott: 27.5 (`CK1`), 22.6 (`RED1`),
  23.4 (`TB1`), 23.6 (`TB2`), 24.5 (`EV6`), 25.4 (`TR7`), 29.3 (`TB3`).
- [x] **31.6** **Hamis-pozitív próba (kötelező).** Futtasd le az összes új checket **egy korábbi,
  sikeresen lezárt ciklusra** (nem a `cycle-30`-ra). Ami itt bukik, azt **meg kell érteni**:
  vagy valódi rés volt abban a ciklusban is (akkor írd a 33. szakaszba), vagy a check túl
  agresszív (akkor szűkítsd). **Egy kapu, ami a jó ciklust is bukatja, használhatatlan** — a
  fejlesztő ki fogja kapcsolni. **A `CK1` itt a legkockázatosabb** (a régi naplók formátuma
  lazább volt): ha egy lezárt ciklus naplója intervallumos cellát tartalmaz, az **valódi**
  találat, de mérlegeld, hogy a check `bad` vagy `info` legyen a **régi** ciklusokra
  (pl. a napló első sorának dátuma alapján nem kell visszamenőlegesen bukatni).
- [x] **31.7 — ÉLES PRÓBA a `cycle-30`-on, regressziós tesztként.** A hét kapu közül **legalább
  négynek** buknia kell rajta: `CK1` (intervallumos naplósor + szűrő nélküli parancs), `TB2`
  (átnevezett szelektorok a `T035`–`T037`-ben), `TB1` (az `assert True` törzsek), `RED1` (nincs
  `✗` sor a `[RED]` taskokhoz). Ha valamelyik **nem** bukik, az a check hibája — nem azt méri,
  amit gondolunk. Az `EV6`-nak és a `TR7`-nek szintén bukni kell, ha a `rest-logs` mappa és a
  `conventions.md` TR3 táblája elérhető.
- [x] **31.8** Commit: `feat(prompts): bizonyíték-keményítés — CK1, RED1, TB1-TB3, EV6, TR7, RV-FB1`

---

## 32. Végrehajtási sorrend (B rész)

1. **27.** F7 — `CK1`: a `[CHECK]` szó szerinti, taskonkénti futása + a napló fegyelme.
   *Elöl van két okból: (a) ez a legkorábbi és legolcsóbb fogópont — szűrt parancsnál a hiba
   magától hibaüzenetként jelentkezik; (b) az F1 joinja e nélkül megetethető (BD9).*
2. **22.** F1 — `RED1`: RED-bizonyíték. *Az F7 naplófegyelmére épül.*
3. **23.** F2/F8 — `TB1` + `TB2` egy scriptben. *A `TB2` (szelektor-létezés) a `cycle-30`
   legélesebb, futtatás nélküli jelzése; a `TB1` a maradék vacuous esetekre.*
4. **25.** F4 — `TR7`: artefaktum-frissesség. *Az `EV6` ELŐTT: ugyanazt a „mikor keletkezett”
   logikát használja, csak szűkebben és önállóan tesztelhetően.*
5. **24.** F3 — `EV6`: forgalmi bizonyíték. *A legösszetettebb (TR3-parse + host-felismerés +
   frissesség), ezért a stabil `TR7` után.*
6. **28.** F9 — `RV-FB1`: a review-checklist mindkét ágon. *Szerkezeti, nem másodlagos.*
7. **29.** F6 — `TB3`: futásidő-heurisztika (javaslat).
8. **31.5–31.6** A célzott bukás-próbák és a **hamis-pozitív próba**.
9. **26.** F5 — a két prózai megerősítés.
10. **30.** Dokumentáció.
11. **31.1–31.4, 31.7–31.8** Kapuk, éles próba a `cycle-30`-on, commit.

> **Miért a prózai szabály (F5) a végén:** ha elöl lenne, a végrehajtó abban a hitben zárná le a
> munkát, hogy „a szabály megvan” — pontosan az a csapda, amit a 20.3 szakasz leír. Az F9 ettől
> **különbözik** (szerkezeti: a lista fizikailag jelen van mindkét ágon), ezért az a
> determinisztikus checkek közt, nem a végén szerepel.

---

## 33. Tapasztalatok (B rész — a végrehajtás közben töltsd)

> Ide kerül a 31.6 hamis-pozitív próba eredménye (mely régi ciklus min bukott, és miért), a
> 31.7 éles próba eredménye, és minden olyan felismerés, ami a terv írásakor nem látszott. Ez
> lesz a `7/l` elv végleges szövegének forrása.

- **`CK1` — éles próba a `cycle-30`-on (27.5 / 31.7 előlegezve).** A kapu a valós
  `flowx-token-exchange/specs/cycle-30-…` mappán **bukik**, pontosan a két várt megállapítással:
  a 13. naplósor `Task` cellája `T030a-T037` intervallum, és mind a nyolc `[CHECK]` taskhoz
  (`T030a`, `T031`–`T037`) hiányzik a saját naplósor.
- **`CK1` — hamis-pozitív próba korábbi, lezárt ciklusokon (31.6 előlegezve).** A `cycle-26`,
  `-27`, `-28`, `-29` naplóiban **egyetlen** intervallumos/felsorolásos `Task` cella sincs (a
  „egy sor = egy task" fegyelem visszamenőleg is állt), viszont mindegyikben **hiányoznak
  naplósorok** `[CHECK]` taskokhoz (`cycle-28`: `T016`; `cycle-29`: `T024b`, `T025`, `T025a–c`;
  `cycle-27`: 5 db; `cycle-26`: 9 db). Kézzel ellenőrizve (`cycle-28/T016`, `cycle-29/T025*`):
  ezek **valódi rések** — a `[CHECK]` lefutott, de nyoma nem maradt —, nem parse-hiba. Ezért a
  check `bad` szinten marad; a régi ciklusokra szánt enyhítés (31.6 mérlegelése) **elmarad**,
  mert a találatok nem formai eltérések, hanem hiányzó bizonyíték.
- **`RED1` — éles próba és visszamenőleges zaj.** A `cycle-30`-on a kapu **bukik** (13 `[RED]`
  taskhoz nincs `✗` sor). A `cycle-26`–`-29` naplóin **ugyanígy bukik** (8 / 6 / 3 / 2 task) —
  ez **nem** hamis pozitív, hanem az új követelmény visszamenőleges hatása: a `[RED]` bukás
  naplózását a 22.1 lépés vezeti be, korábban senki nem kérte. Mivel a kapu csak az **éppen
  validált** ciklusra fut, a régi ciklusok soha nem futnak bele; ezért `bad` szinten marad,
  enyhítés nélkül. A felmentő ág (`RED-EXEMPT`) és a valódi `✗` sor is ellenőrizve — mindkettő
  átengedi.
- **`TB1`/`TB2` — éles próba a `cycle-30`-on (31.7 előlegezve).** A `TB2` a plan-adatlapok nélkül is
  bukik: a `T035`–`T037` `[CHECK]` szelektorai (`test_t30_05_health_endpoint_quietness`,
  `…_06_multi_token_session_isolation`, `…_07_upstream_routing_debug_logging`) **nincsenek benne**
  a tesztfájlban — pontosan az átnevezés, amit a terv leírt. A `TB1` a `--files`-os célzott
  futtatásban **7 vacuous törzset** talál (mind `assert True`). **Fontos részlet:** a `cycle-30`
  plan-je még **nem tartalmaz `TA1` adatlapokat** (`#### <tesztfájl>` fejléc), ezért a `TB1` a
  plan-vezérelt, alapértelmezett módban „kimarad" `info`-val — a kapu a plan-fegyelemre épül
  (`TA1`), és visszamenőleg csak `--files`-szal mérhető. Új ciklusokban ez nem probléma (a `TA1`
  a `03` kapujában kötelező), de **a `TB1` erőssége a `TA1` erősségén áll**.
- **`TB1`/`TB2` — hamis-pozitív próba (31.6 előlegezve).** A `cycle-26`–`-29` mind `OK`
  (`exit 0`): nincs `TA1` adatlap → `TB1` kimarad, és a `[CHECK]` parancsaikban nincs
  teszt-szelektor → `TB2` kimarad. Egyetlen hamis találat sincs. Célzott próbák: `pytest.raises`
  blokkot tartalmazó Python teszt és `expect(...)` alapú vitest teszt **nem** bukik;
  `@pytest.mark.skip` dekorátoros és `it.skip(...)` teszt **nem** ítélhető; `-k "health and not
  slow"` logikai kifejezésnél a `TB2` `info`-val kimarad.
- **🔴 `TR7` — a `results.json` a futás VÉGÉN íródik (a BD6 referencia-idejének javítása).**
  A BD6 a `results.json` mtime-ját nevezte meg padlónak, de a `run-tests.py` a fájlt a futás
  **után** írja ki — így minden, a körben keletkezett artefaktum „a padló előttinek" minősült
  volna, azaz a kapu **minden** teljes kört elbukatott volna. Javítás: a `run-tests.py` a
  `results.json`-ba beírja a kör **kezdetét** (`started_at`, additív mező — a `dod-check.py` és a
  `round-log.py` a `results` kulcsot olvassa, nem törik el). A `report-gate-check.py`
  `round_reference_time()`-ja ezt használja; `started_at` nélküli (régi) körnél
  `min(results.json mtime, kör-mappa mtime) − 1 nap` a **becsült** padló (a kimenet megnevezi,
  melyiket használta). Az egy napos tolerancia szándékos: egy kör órák alatt lefut, az örökölt
  artefaktum hetekkel-hónapokkal régebbi.
- **`TR7` — visszamenőleg NEM mérhető (a 31.7 vonatkozó része nem teljesíthető).** A `cycle-30`
  kör-mappája a mai kapun **átmegy**, mert a git nem őrzi meg az mtime-okat: a „hónapokkal
  régebbi" `rest-logs` fájlok a munkafában friss mtime-mal állnak. A `TR7` tehát **élő körben**
  fog (ott a padló és a fájlok egy futásból származnak), utólagos ciklus-vizsgálatra nem
  alkalmas. Hamis pozitív viszont nincs: a `cycle-28`/`-29` bukásai mind a **régi** „HIÁNYZIK"
  ágból jönnek (könnyű körök, hiányzó e2e/playwright artefaktumok), nem a frissesség-padlóból.
- **`EV6` — a TR3-parse-oló ÚJRAHASZNOSÍTVA, nem újraírva.** A `run-tests.py` `importlib`-bel
  betölti a `report-gate-check.py`-t (a kötőjeles fájlnév miatt nem sima `import`), és annak
  `extract_section` / `parse_rows` / `EMPTY_VALUES` elemeit használja. Így nincs harmadik
  tábla-értelmezés, ami csendben szétcsúszhatna a kapuval (24.2 kikötése).
- **`EV6` — a frissesség-padló ugyanaz, mint a `TR7`-nél.** A forgalmi bizonyíték a kör
  **kezdete** (`started_at`) után keletkezett audit-fájlok közt keresi a cél-hostot. Mindhárom ág
  ellenőrizve gyártott kör-mappán: (a) örökölt, `127.0.0.1`-es napló → a kategória `FAIL` +
  `failed_items` bejegyzés; (b) a **futás közben** írt, dev hostot tartalmazó napló → nem szól;
  (c) TR3 tábla audit-artefaktum nélkül → csak `·` javaslat, `VERDICT: PASS`.
- **`EV6` — a `24.3` megerősítve:** nem kell új `plan.md`-mező. A check a meglévő
  `<field:f_environment>` oszlopból és a `conventions.md` TR3 táblájából dolgozik, a cél-hostot a
  `Parancs`/`Előfeltétel` cellából nyeri (az `EV3` mintája szerint) — az A rész vágási táblája
  érintetlen.
- **`RV-FB1` — a blokk a `<status:must_fix>` határvonal-szekciót is viszi.** A
  `shared-{hu,en}/review-checklist.md` a `## Ellenőrzési szempontok` **és** a
  `## <status:must_fix> vs <status:suggestion>` szekciót tartalmazza szó szerint (28.1) — a
  fallback ág anélkül nem tud besorolni. A `reviewer.md` frontmatterébe új `shared:` kulcs
  került (eddig nem volt neki), a gemini `agent.json` tükrök regenerálva; a tükör a feloldatlan
  `INCLUDE:shared/review-checklist.md` markert hordozza, ahogy a többi agent is (a telepítő oldja
  fel). `lang-parity-check --strict` → 0, `sync-gemini-agents --check` → 0.
- **🔴 `TB3` — a `cycle-30`-on NEM szól (a BD12 konzervatív szabályának ára).** A kör
  `e2e/pytest-junit.xml`-jében 8 esetből **7** `time="0.000"` — a nyolcadik
  (`test_t30_00_dsp01_preflight_readiness`) 0.305 s. A BD12 szabálya („**minden** eset 0.000 az
  adott fájlban") így nem teljesül, tehát a 29.3 elvárása (a javaslat megjelenik a `cycle-30`
  XML-jén) **nem teljesül** — és ezt szándékosan **nem** javítjuk küszöbbel vagy aránnyal, mert a
  BD12 azt explicit kizárja. A `TB3` amúgy is csak javaslat: a `cycle-30`-at a `TB1` (7 vacuous
  törzs) és a `TB2` (3 elorphanodott szelektor) fogja meg, ezért a heurisztika hallgatása nem
  hagy rést. Ellenőrizve gyártott XML-eken: minden-nulla fájl → egy `·` javaslat-sor;
  vegyes (0.812 s + 0.000 s) fájl → nincs javaslat; a kilépő kód mindkét esetben `0`.
- **F5 — a prózai pár a KÖZÖS blokkba került, nem a `reviewer.md`-be.** A 26.2 a `reviewer.md`-t nevezte
  meg, de a 28.1 (F9) időközben a szempontlistát a `shared-{hu,en}/review-checklist.md`-be emelte.
  Az eldönthető `TB1`-kérdés ezért oda került: így **mindkét** végrehajtási ágon (subagent és
  `07`-fallback) jelen van — pontosan az a hatás, amit a 26. szakasz bevezetője kért („a 26.2
  önmagában kevés"). A 26.1 anti-stub blokk a `06` *Végrehajtási szabályok* fejezetébe, az `IM2`
  garde után került, a `RED1`/`TB1` kapukra hivatkozva.
- **A `7/l` elv a `7/e` UTÁN áll, nem a `7/k` után.** A terv a `7/k` (A rész) mögé tette volna, de
  az A rész nincs végrehajtva, tehát `7/k` nem létezik — a `7/l` a `7/x` csoport végére került. Az
  A rész elvégzésekor a `7/k` egyszerűen elé szúrható, sorszám-ütközés nélkül.
- **31.7 újramérve (regresszió).** A `cycle-30`-on a mai fán: `CK1` bukik (13. naplósor
  `T030a-T037` intervallum + 8 hiányzó naplósor), `RED1` bukik (13 `[RED]` taskhoz nincs `✗`),
  `TB2` bukik (3 elorphanodott szelektor), `TB1` a `--files`-os futtatásban 7 vacuous törzset talál
  — tehát **négy** kapu fog, ahogy a 31.7 megköveteli. A `cycle-26`–`-29` a `TB1`/`TB2`-n
  `exit 0` (hamis pozitív nincs).
- **31.4 füstteszt mind az öt platformon.** `test-substance-check.py` mind az öt scripts-mappában
  megvan; a telepített `06`/`07`/`reviewer` fájlokban **0** feloldatlan `INCLUDE:`/`<sec:`/`<field:`/
  `<status:` token (hu és en prompt-nyelven is), és a `review-checklist.md` tartalma platformonként
  **pontosan két** fájlban jelenik meg (`reviewer` + `07`) — az RV-FB1 szándéka szerint.

- **Nyelvfüggetlen napló-parse.** A `check-log.md` tábláját a `Task` fejléc-cella (mindkét nyelvi
  fán ugyanaz a szó) alapján indexeljük, a parancs- és eredmény-cellát pedig **tartalom** szerint
  (backtick, ill. `✓`/`✗`) — így a nyelvfüggő fejlécnevekre (`Parancs`/`Command`) nem kell
  támaszkodni, és a `--stage close` join mindkét projekt-nyelven ugyanazt méri.
