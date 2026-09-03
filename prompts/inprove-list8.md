# „A zöld kör nem bizonyítja, hogy a KATEGÓRIA lefutott" — végrehajtási terv

> **Ez a dokumentum önhordó.** Üres kontextusban, `/clear` után is végrehajtható: az 1. szakasz
> megadja a repó-orientációt, a 2. a mért bizonyítékot, a 3. a lezárt döntéseket, a 4–7. a négy
> keményítés tételes teendőit, a 8. a dokumentációt, a 9. a kapukat, a 10. a végrehajtási sorrendet.
> **Semmit nem kell kikövetkeztetni** — ha valami mégis hiányzik, az a terv hibája; írd bele.
>
> **Státusz:** végrehajtásra vár. A 3. szakasz döntései **lezártak** — nem kell rákérdezned.
> **Előzmény:** a `prompts/inprove-list6.md` **B része** (CK1 · RED1 · TB1–TB3 · EV6 · TR7 · RV-FB1)
> **elkészült**; ez a terv az ott maradt rést zárja. A `list6` **A része** (a `03` hasítása
> `03a`/`03b`-re) szintén elkészült — ez a terv **a hasítás utáni fájlneveket használja**.

---

## 0. Hogyan használd ezt a dokumentumot

1. **Olvasd el az 1–2. szakaszt.** Az 1. mondja meg, milyen repóban dolgozol és milyen kézi
   kapuk kötelezők; a 2. adja a bizonyítékot, ami nélkül a checkek önkényesnek tűnnek.
2. **A 3. szakasz döntéseit ne nyisd újra.** Ha valamelyik a végrehajtás közben tarthatatlannak
   bizonyul, **írd a 11. szakaszba, mi lett helyette és miért** — ne csendben térj el tőle.
3. **A 10. szakasz sorrendjében haladj**, és minden teendő után **pipálj ebben a fájlban**
   (`- [ ]` → `- [x]`). A négy keményítés **független egymástól**, külön is commitolható.
4. **Kétnyelvű repó:** minden prompt-szerkesztés **hu ÉS en párban** megy (1.2). A
   `lang-parity-check.py` a szerkezeti eltérést megfogja, a jelentés-eltérést **nem** — azt neked
   kell átolvasnod.
5. **Nincs CI és nincs pre-commit hook** — a kapukat (9. szakasz) **kézzel futtasd le**, commit előtt.

---

## 1. Orientáció — mi ez a repó, és mi mozdul

### 1.1 A rendszer

A `berkispec` egy **spec-driven development keretrendszer promptokból**: fázis-skillek (`00`–`09`),
subagent-promptok és determinisztikus **kapu-scriptek**. A repó a **forrás**; egy célprojektbe az
`install.sh` / `install.ps1` telepíti (öt platform: claude, codex, antigravity, cursor, copilot).
A telepítő **build-time** oldja fel az `<!-- INCLUDE:shared/… -->` / `<!-- INCLUDE:lang/… -->`
markereket és a `<sec:…>` / `<field:…>` / `<status:…>` tokeneket.

Amit ez a terv érint:

| útvonal | mi ez |
|---|---|
| `prompts/skills-{hu,en}/03b-write-test-plan.md` | a teszt-terv fázis (a `03` hasítás után; a gépi futtatási tábla itt születik) |
| `prompts/skills-{hu,en}/07-validate.md` | a validálási fázis orchestrátora |
| `prompts/shared-{hu,en}/quality-check-plan-test.md` | a `03b` minőségi kapuja (a `plan-fixer` is beemeli) |
| `prompts/scripts/analyze-gate-check.py` | a tervezési dokumentumok mechanikus kapuja (`--plan-only`, `--plan-code-only`) |
| `prompts/scripts/run-tests.py` | a `07` futtatója a plan **gépi futtatási táblájából** |
| `prompts/scripts/validate-gate-check.py` | a `07` gyűjtőkapuja (`--stage start` / `close`) |
| `prompts/scripts/dod-check.py` | a `DoD-NN` ↔ teszt-bizonyíték join |
| `prompts/lang/status-keys.json` | a szótár: `sections` / `fields` / `status`, `hu` és `en` ággal |

### 1.2 A két nyelvi tengely (LG2/LG5)

- **prompt-nyelv:** a `prompts/skills-hu/` vs. `prompts/skills-en/` fa (az ágens *instrukcióinak*
  nyelve). **Minden szerkesztés mindkét fán megy, párban.**
- **projekt-nyelv:** amit az ágens a célprojektbe *ír* — ezt a `prompts/lang/{hu,en}/` blokkok és a
  `status-keys.json` tokenjei adják. A **scriptekben soha ne írj magyar/angol literált**: a
  `lang_keys` modul `sec()` / `fld()` / `st()` függvényeit használd (a scriptek már importálják).

### 1.3 Kötelező kézi kapuk (nincs CI, nincs pre-commit hook)

```bash
python3 prompts/scripts/lang-parity-check.py            # szerkezeti paritás  → 0
python3 prompts/scripts/lang-parity-check.py --strict   # fájlhalmaz-paritás  → 0
python3 prompts/scripts/sync-gemini-agents.py --check   # agent.json tükrök   → 0
```
Ha egy **agent-prompt** (`prompts/agents-{hu,en}/*.md`) változik, előbb írás módban regenerálj:
`python3 prompts/scripts/sync-gemini-agents.py`.

### 1.4 Amit ez a terv NEM érint (kimondott nem-célok)

- **Nem** nyúlunk a `03` hasításához (`03a`/`03b`) — az kész, a `list6` A része.
- **Nem** vezetünk be új `plan.md`-mezőt és új státuszt. Mind a négy check **meglévő**
  artefaktumokból dolgozik.
- **Nem** írjuk át a `run-tests.py` tábla-parserét úgy, hogy „okosan" felismerje az idegen
  oszlop-sorrendet. A séma **kötelező**, nem kitalálandó (lásd D2).
- **Nem** bántjuk a `05-analyze` `03-plan` célfázis-jelölését (az egy dokumentumra mutat, nem fázisra).

---

## 2. A probléma és a mérés

### 2.1 A panasz

Egy éles ciklus (`cycle-30`, `flowx-token-exchange`) **PASS**-ra zárt úgy, hogy a **dev környezetre
tervezett tesztek se nem íródtak meg, se nem futottak le**. A validálási problémákat **két ágens is
elemezte**, és egyik sem vette észre — mert ez **hiány**-állítás („egy deklarált kategória nem futott
le"), amit egy LLM-review szerkezetileg rosszul lát. Determinisztikusan viszont triviális: két
meglévő artefaktum **joinja**.

### 2.2 A mérés (2026-09-03, `flowx-token-exchange` `cycle-26`…`cycle-30`)

**(a) A kör nem a plan táblájából megy — és ezt semmi nem méri.**

| ciklus | gépi futtatási tábla | `results.json` a kör-mappákban | a dev kategória futott? |
|---|---|---|---|
| 26 / 27 / 28 | **nincs** | 0 | nincs mit mérni |
| 29 | 5 sor (2 db `dev (dsp01)`) | 5 körből 4 | `round-04`-ben **igen**, PASS |
| 30 | 4 sor (`R06` = `dev`) | **0** | **soha** |

A `cycle-29` **záró, `TELJES`, PASS** köre (`Kör 5`) sem hordoz `results.json`-t, és a
lépés-táblája **üres** — a PASS-t adó körről nincs gépi nyoma, mi futott.

**(b) A `cycle-30` gépi táblája nem a keret sémája, ezért nem is lehetett belőle futtatni.**
A `run-tests.py` `parse_matrix()` **fix oszlop-pozíciókkal** olvas. A `cycle-30` táblája
`Recept | Kategória | Előfeltétel | Parancs | Időkorlát | Siker-kristályosítás | Elvárt kimenet | Környezet`.
A parser kimenete ezen a táblán (ténylegesen lefuttatva):

```
kategoria='Recept' tipus='kategória'   eredmeny='Időkorlát'   ← a FEJLÉC adatsorként
kategoria='R01'    tipus='unit'        eredmeny='60s'         ← az eredményfájl helyén időkorlát
kategoria='R06'    tipus='dev e2e'     eredmeny='300s'        ← a típus se `gyors`/`nehéz`
```

A `S1` kapu csak azt nézi, hogy a **szekció létezik-e**. A tábla „megvolt", de gépileg
használhatatlan — innen az ad-hoc kézi parancsok, és innen tűnt el az `R06`. A tünet a `cycle-29`
`results.json`-jában feketén-fehéren ott áll:
`"nem sikerült darabszámot kinyerni — csak a kilépő kód áll rendelkezésre (TR1 gyenge bizonyíték)"`.

**(b/2) Ugyanez a parser angol projekt-nyelven a FEJLÉCET is futtatná.** A `parse_matrix()` a
fejlécsort a `cells[0].lower() in ("kategória", "kategoria")` feltétellel hagyja ki — az angol
prompt-fa viszont `| Category | Type | … |` fejlécet ír elő. Lefuttatva egy angol fejlécű táblán:
`kategoria='Category'`, `parancs='Command'` — vagyis a szkript a `Command` szót adná ki shell
parancsként. Ez **latens hiba**, független a `cycle-30`-tól: minden angol projekt-nyelvű ciklust
érint.

**(c) A dev-parancs env-változói dekorációk.**
A plan `R06` parancsa `TEST_ENV=dev DEV_BASE_URL=…`-t állít. Mindkét változó **0 találat** a
célprojekt `test/` fájában. A kód valójában `TMP_BASE_URL` / `PUBLIC_TMP_BASE_URL` /
`MEDIA_TMP_BASE_URL`-t olvas, a dev-kapcsoló pedig `RUN_DEV_E2E` — ami viszont **0 találat a
`plan.md`-ben és a `tasks.md`-ben**.

**(d) A néma skip bizonyítéknak számít — és ez egy scripthiba.**
A ciklus tesztfájljában 8 esetből 7 törzse `assert True`; az egyetlen valódi:

```python
def test_t30_00_dsp01_preflight_readiness():
    if os.environ.get("RUN_DEV_E2E") != "true":
        pytest.skip("RUN_DEV_E2E!=true, skipping dsp01 cluster check")
```

Az implement fázis JUnit XML-jében ez `skipped`. A `dod-check.py` viszont így indexel:

```python
failed = case.find("failure") is not None or case.find("error") is not None
index[key] = "FAIL" if failed or prev == "FAIL" else "PASS"
```

Vagyis a **`<skipped>` eset `PASS`-ként kerül az indexbe** → egy némán kihagyott dev-teszt
`DoD-NN` **bizonyítékként** szolgál. Ez a lánc utolsó szeme.

### 2.3 Miért nem fogta meg a `list6` B része

| meglévő kapu | miért engedte át |
|---|---|
| `TB1`/`TB2` | **megfogta** a 7 vacuous törzset és a 3 elorphanodott szelektort — de a *hiányzó kategóriáról* nem mond semmit |
| `EV3` (host a parancsban) | a cél-host **literálisan ott volt** a parancsban — csak épp a kód nem olvasta a változót |
| `EV4`/`EV5`/`EV6` | mind a `run-tests.py`-ban futnak; **ha az orchestrátor kézzel ad ki parancsokat, egyik sem fut le** |
| `TR3` (riport-artefaktumok) | az artefaktumok megvoltak — csak nem arról, amiről kellett volna |
| `PH1` | a `Fázis` oszlop hiányzott a táblából → „üres = mindkettő", nincs megállapítás |

**A tanulság általánosítva:** a `7/l` elv (a) kérdése — *ha egy fázis „kész" jelzése egy számláló
vagy egy név egyezésén áll, mi bizonyítja, hogy történt is valami?* — a **kategória** szintjén még
nem volt feltéve. A `run-tests.py` a **tábla** alapján futtat; ha a táblát senki nem használja,
az egész EV-lánc néma.

---

## 3. Lezárt döntések

- [x] **D1 — Négy keményítés + egy futásidejű hibajavítás.** `RUN1` (kör-lefedettség),
  `TP4/b` (tábla-séma), `EV7` (env-változó kötés), `SK1` (néma skip) — plusz az **5.0**
  (`parse_matrix()` nyelvfüggő fejléc-felismerése), ami nem kapu, hanem hibajavítás. Egyik sem előfeltétele a
  másiknak, **külön commitolhatók**; a 10. szakasz sorrendje csak hozam-optimalizálás.

- [x] **D2 — A gépi futtatási tábla sémája KÖTELEZŐ, nem kitalálandó.** A `run-tests.py` fix
  oszlop-pozíciókkal olvas; ezt **nem** tesszük „okossá" (fejléc-alapú oszlop-felismerés), mert az
  a hibát elrejtené: egy idegen sémájú tábla akkor is rossz bizonyítékot termelne (`eredmeny='60s'`).
  Helyette a **`03b` lezárásakor** bukjon a kapu, ahol a tábla keletkezik.

- [x] **D3 — A `RUN1` kizárólag TELJES körre szól.** A könnyű kör (VD10) **szándékosan** futtat
  részhalmazt; ha a `RUN1` ott is mérne, minden javító körben hamis pozitívot adna. A kör típusát a
  `validation-report.md` `## <sec:round> N — <dátum> — TELJES|KÖNNYŰ — …` fejléce mondja meg
  (`st("round_type_full")` = `TELJES`).

- [x] **D4 — Nincs gépi futtatási tábla → a `RUN1` kimarad (`info`), nem bukik.** A `cycle-26`–`-28`
  planjeiben nincs tábla (a `TP4` fiatalabb náluk). Egy kapu, ami a régi, lezárt ciklusokat is
  bukatja, használhatatlan — a fejlesztő kikapcsolja. **A tábla hiányát a `S1` kapu amúgy is méri**
  a `03b` lezárásakor.

- [x] **D5 — Hiányzó `results.json` TELJES körben: `bad`.** Ez a legfontosabb egyetlen sor az egész
  tervben: azt jelenti, hogy a kört **nem a plan táblájából hajtották**. Visszamenőleg is találat
  (`cycle-29` `Kör 5`, `cycle-30` `Kör 1`) — de ez **valódi rés**, nem formai eltérés (2.2/a).

- [x] **D6 — Az `EV7` a `run-tests.py`-ba kerül, a futtatás ELŐTT.** Ott van a tábla, ott van a
  `check_environment_mismatch` (EV5) mintája, és ott van a `exit 4` ág. A `03b` kapujában nem
  mérhető megbízhatóan: a tesztfájl a tervezéskor még nem létezik.

- [x] **D7 — Az `SK1` két helyen javít.** (a) `dod-check.py`: a `<skipped>` eset **nem** `PASS`
  (egysoros osztály-javítás); (b) `validate-gate-check.py`: a kör JUnit-jaiban `skipped` eset,
  amelynek neve a plan `<sec:spec_coverage>` / `TS-NN` / `TC-NN` hivatkozásai közt szerepel,
  **`bad`** — indoklással felmenthető (`SKIP-EXEMPT`, a `RED-EXEMPT` mintájára).

- [x] **D8 — Nincs új `plan.md` mező és nincs új státusz.** Mind a négy check meglévő
  artefaktumokból dolgozik: `plan.md` gépi tábla, `results.json`, `validation-report.md`,
  JUnit XML, tesztfájlok.

---

## 4. `RUN1` — kör-lefedettség (a legnagyobb hozam)

> **Mit mér:** egy **TELJES** kör lezárásakor a plan gépi futtatási táblájának minden olyan sora,
> amely a `validate` fázisban fut (`<field:f_phase>` = `<status:phase_validate>` vagy
> `<status:phase_both>`, **üres cella = mindkettő**), megjelenik-e a kör `results.json`-jában.

- [ ] **4.1 — Új check a `validate-gate-check.py`-ba: `check_run_coverage(cycle, rep, stage)`.**
  A fájl felépítése: modul-szintű `check_*` függvények, mind `(cycle, rep, stage)` szignatúrával,
  a `Report` osztály `ok()` / `info()` / `bad()` metódusaival (a `bad()` állítja a `failed` flaget,
  abból lesz `exit 1`). A `main()` a hívási sorrendet adja (`check_tasks` … `check_report`).
  Az új check a **`check_report` UTÁN** hívódjon (az állapítja meg, hogy a kör-mappák léteznek).

  A logika:
  1. `stage == "start"` → `return` (a kör elején még nincs mit mérni).
  2. Olvasd be a `cycle/"plan.md"`-t. A gépi tábla sorait **ne parse-old újra kézzel**: töltsd be a
     `run-tests.py`-t modulként (a kötőjeles fájlnév miatt `importlib`-bel — a mintát lásd a
     `run-tests.py` `_load_report_gate_module()` függvényében), és használd a `parse_matrix()` és a
     `row_phases()` függvényét. **Indoklás:** így nincs harmadik tábla-értelmezés, ami csendben
     szétcsúszhat a futtatóval.
  3. Ha a tábla üres → `rep.info(...)` + `return` (D4).
  4. Az elvárt kategóriák: azok a sorok, amelyekre `"validate" in row_phases(row)`.
  5. A `validation-report.md`-ből szedd ki a kör-blokkokat:
     `^## <sec:round> (\d+) — .* — (TELJES|KÖNNYŰ) —` alakban (a típus-literált **ne** írd be:
     `st("round_type_full")`). Csak a **TELJES** körökre mérj (D3).
  6. Minden ilyen körre nézd meg a `cycle/"test-report"/"validate"/f"round-{n:02d}"/"results.json"`-t:
     - **nincs meg** → `rep.bad(...)`: *„a `round-NN` TELJES kör, de nincs `results.json` — a kört
       nem a plan gépi futtatási táblájából hajtották (RUN1). A `07` a `run-tests.py`-jal futtat;
       kézi parancsokból nincs gépi nyoma, mely kategória futott le."*
     - **megvan** → olvasd be, `json.load(...)["results"]`, és a bejegyzések **`kategoria`** kulcsát
       (magyar kulcs! a `run-tests.py` írja így) vesd össze az elvárt kategóriákkal.
       Az összevetés **kis-nagybetű- és backtick-érzéketlen** legyen (a plan celláiban `` `R06` ``
       alak is előfordul) — a normalizálás: `.strip().strip("`*").lower()`.
     - hiányzó kategóriánként → `rep.bad(...)`: *„a `round-NN` TELJES körből hiányzik a `<kategória>`
       kategória (RUN1) — a plan a `validate` fázisra írja elő. Vagy futtasd le, vagy a
       `results.json`-ba kerüljön be `skipped` státusszal és indoklással."*
  7. Ha minden rendben: `rep.ok(...)` a lefedett kategóriák számával.

- [ ] **4.2 — Felmentő ág (`RUN-EXEMPT`).** Egy tudatosan kihagyott kategória (pl. VPN nélküli
  futás) ne bukassa a kört, de hagyjon nyomot. A felmentés helye a `validation-report.md` **adott
  kör-blokkja**, a `RED-EXEMPT` / `CK-DEVIATION` mintájára:
  `RUN-EXEMPT: <kategória> — <miért nem futtatható ebben a körben>`
  Ha van ilyen sor a kör blokkjában, a hiányzó kategória `rep.info(...)`, nem `rep.bad(...)`.
  > **🔴 A `results.json`-ba NE várj `skipped` státuszt.** A `run-tests.py` **kizárólag `PASS` és
  > `FAIL` státuszt ír** (`entry["status"]`, ~585–651. sor) — nincs `skipped` állapota. Egy ilyen
  > ágra épített felmentés soha nem sülne el.
  > **A `_exemptions(text, prefix)` segédfüggvényt (`validate-gate-check.py`, ~192. sor) így,
  > ahogy van, NEM tudod újrahasználni:** a kulcs-mintája task-azonosítóra van drótozva
  > (`T[A-Z]*\d+[a-z]?`), a kategória-név viszont szabad szöveg. **Általánosítsd** egy harmadik,
  > alapértelmezett paraméterrel — `_exemptions(text, prefix, key_re=r"T[A-Z]*\d+[a-z]?")` —, így a
  > `RED1` és a `CK1` viselkedése bájtra változatlan marad, az új hívások pedig saját mintát adnak
  > (kategóriára pl. `[^\s—–-]+`). Egy parser maradjon, ne három.

- [ ] **4.3 — A `07` skill szövege (HU+EN).** `prompts/skills-{hu,en}/07-validate.md`, a
  **kör-lezáró kapu-blokk** felsorolásába egy sor:
  *„**`RUN1`:** TELJES körben a plan minden `validate`-fázisú kategóriája szerepel a kör
  `results.json`-jában. Ha nincs `results.json`, a kört nem a gépi táblából hajtottad — futtasd a
  `run-tests.py`-jal, ne kézzel."*
  A `03b`-re mutató visszairányítás **nem** kell: ez végrehajtási, nem tervezési hiba.

- [ ] **4.4 — Verifikáció.** Gyárts a scratchpadba egy kör-mappát (vagy használj éleset):
  - **bukás-próba:** TELJES kör-blokk a `validation-report.md`-ben + hiányzó `results.json` → `exit 1`,
    a `RUN1` sorral;
  - **bukás-próba 2:** `results.json` megvan, de a `validate`-fázisú `e2e` kategória nincs benne → `exit 1`;
  - **hamis-pozitív próba:** ugyanez **KÖNNYŰ** kör-blokkal → **nem** szól;
  - **hamis-pozitív próba 2:** olyan ciklus, amelynek planjében nincs gépi tábla → `info`, `exit 0`.

---

## 5. `TP4/b` — a gépi futtatási tábla SÉMÁJA (a gyökérok)

> **Mit mér:** a tábla oszlopai a keret sémáját követik-e. A `S1` csak a szekció **létezését** nézi;
> egy idegen oszlop-sorrendű tábla átmegy rajta, a `run-tests.py` viszont **fix pozíciókkal** olvas,
> tehát csendben rossz cellákat használ.

A kötelező séma (a `03b` sablonjából, `prompts/skills-hu/03b-write-test-plan.md`):

```
| Kategória | Típus | Előfeltétel | Parancs | Eredményfájl | Formátum | Takarítás | Környezet | Fázis |
```
(az utolsó kettő opcionális: 7, 8 vagy 9 oszlop — a régi táblák így futnak tovább).

- [ ] **5.0 — 🔴 ELŐBB: a `parse_matrix()` fejléc-felismerése nyelvfüggő (futásidejű hiba).**
  A `run-tests.py` `parse_matrix()`-a így hagyja ki a fejlécsort:
  ```python
  if not cells or cells[0].lower() in ("kategória", "kategoria"):
      continue
  ```
  Az **angol** projekt-nyelvű plan fejléce viszont `| Category | Type | … |` (lásd
  `prompts/skills-en/03b-write-test-plan.md` 288. sor) — az nem illeszkedik, tehát a **fejlécsor
  adatsorként** kerül a listába. Lefuttatva egy angol fejlécű táblán:
  ```
  kategoria='Category'  parancs='Command'   tipus='type'    ← a FEJLÉC futtatandó kategóriaként
  kategoria='unit'      parancs='npm test'  tipus='gyors'
  ```
  Vagyis egy angol projektben a `run-tests.py` megpróbálná **lefuttatni a `Command` szót** shell
  parancsként, és `Category` néven FAIL kategóriát írna a `results.json`-ba — ami utána a `RUN1`
  join-ját is megzavarná.
  **Javítás — nyelvfüggetlenül, szerkezetből:** a fejléc az a sor, amelyet **közvetlenül elválasztó
  sor követ** (`|---|---|…`). Ezt ismerd fel, és azt a sort hagyd ki; a mai literál-listát
  (`kategória`/`kategoria`) tartsd meg **másodlagos** ágnak, hogy az elválasztó nélküli, kézzel írt
  táblák se törjenek el.
  **Verifikáció:** `parse_matrix()` egy angol és egy magyar fejlécű, egyébként azonos táblán
  **ugyanazt az egy adatsort** adja vissza.

- [ ] **5.1 — Új check az `analyze-gate-check.py`-ba: `check_run_table_schema(plan_text, f)`.**
  A fájl konvenciói: `table_rows(text, sec("machine_run_table"))` adja a sorokat cellalistaként;
  a megállapítás `f.add(kód, célfázis, üzenet)` (blokkol) vagy `f.suggest(...)` (nem blokkol);
  a nyelvfüggő nevek `sec()` / `fld()` / `st()`. **Mintának a `check_run_table_phase` (PH1)
  függvényt vedd** — ugyanezt a táblát járja be.

  Három, egymástól független megállapítás (mind `f.add`, célfázis `"03"`):
  1. **Fejléc-cella ellenőrzés.** A tábla első sorának első cellája a `Kategória` (`fld` szerinti)
     szó legyen. Ha nem: *„a gépi futtatási tábla első oszlopa nem a `Kategória` (TP4/b) — a
     `run-tests.py` fix oszlop-pozíciókkal olvas, tehát az eltolt tábla minden celláját rossz
     mezőbe teszi. A kötelező sorrend: …"* + a séma kiírása.
  2. **Típus-oszlop.** Minden adatsor 2. cellája a **`gyors`** vagy a **`nehéz`** szó legyen
     (üres cella megengedett a régi tábláknál — akkor `f.suggest`). Ha más érték áll ott
     (pl. `unit`, `e2e`, `dev e2e`): `f.add` — *„a `Típus` oszlop csak `gyors` vagy `nehéz` lehet;
     ez dönti el, mi fut a könnyű körben (VD10). A kategória NEVE az első oszlopba való."*
     > **🔴 Itt szándékosan LITERÁLT illesztünk, nem szótár-kulcsot — és ez nem hiba.** A
     > `run-tests.py` a típust **nyelvfüggetlen literálként** kezeli: a `main()` a `--type`
     > kapcsolót `gyors`/`nehez` értékekkel veszi, és **prefix-illesztéssel** szűr
     > (`r["tipus"].startswith("gyor"/"nehe")`, ~526–528. sor). Az **angol** prompt-fa is ezt írja
     > elő (`prompts/skills-en/03b-write-test-plan.md`: `| unit | gyors | …`). Ha itt új
     > `status`-kulcsot vezetnél be (`type_fast`/`type_heavy`), a **kapu és a futtató szétcsúszna**:
     > a kapu `fast`-ot követelne, a `run-tests.py` pedig `gyor` prefixet keresne, és **egyetlen
     > kategóriát sem választana ki**. Ezért: **prefix-illesztés, ékezet-érzéketlenül**
     > (`gyor` / `neh`), pontosan úgy, ahogy a futtató.
     >
     > _(A `gyors`/`nehez` literál az angol fában valódi szennyeződés, és a `nehéz`/`nehez`
     > írásmód sem egységes — de a javítása **külön munka**: együtt kell mozgatni a
     > `run-tests.py` `--type` kapcsolóját, a `07` skill hívásait és mindkét prompt-fát. Ebbe a
     > tervbe **ne** vedd bele; ha zavar, vedd fel külön tételként.)_
  3. **Eredményfájl-oszlop.** Az 5. cella vagy `—` (üres jelölés), vagy **útvonalnak látszik**:
     tartalmaz `/`-t vagy `.`-ot ÉS nem illeszkedik a `^\d+\s*[smh]$` (időtartam) mintára.
     Ha időtartam áll ott: `f.add` — *„az `Eredményfájl` oszlopban időtartam áll (`60s`) — a
     tábla oszlopai eltolódtak (TP4/b). A `run-tests.py` ezt a cellát fájlként nyitná meg, és a
     darabszámok kinyerése némán elbukna (TR1 gyenge bizonyíték)."*

- [ ] **5.2 — A check hívása.** Az `analyze-gate-check.py` `main()`-jében, a `check_run_table_phase`
  (PH1) hívása **mellé**, a teszt-oldali blokkba — vagyis abba az ágba, amely `code_only` módban
  **nem** fut (a `--plan-code-only` a `03a` lezárása, ott a tábla még nem létezik). Keresd a
  `if not code_only:` blokkot, ahol a `check_test_scenarios` / `check_run_table_phase` hívások állnak.

- [ ] **5.3 — A `03b` minőségi kapujának új pontja (HU+EN).**
  `prompts/shared-{hu,en}/quality-check-plan-test.md`, a `PH1`-es pont mellé:
  *„**🔴 A gépi tábla a keret SÉMÁJÁT követi? (TP4/b)** — az oszlopok sorrendje `Kategória · Típus ·
  Előfeltétel · Parancs · Eredményfájl · Formátum · Takarítás · Környezet · Fázis`, a `Típus` értéke
  `gyors`/`nehéz`, az `Eredményfájl` útvonal (nem időkorlát). A `run-tests.py` **fix
  oszlop-pozíciókkal** olvas: egy saját sémájú tábla nem hibaüzenetet ad, hanem **rossz cellákat
  használ** — és a fázis kézi parancsokra esik vissza, ahol egyetlen `EV` kapu sem fut le."*

- [ ] **5.4 — Verifikáció.** `analyze-gate-check.py … --plan-only`:
  - **bukás-próba:** másold a scratchpadba a `cycle-30` planjét (vagy gyárts egy táblát
    `Recept | Kategória | …` fejléccel) → a `TP4/b` mindhárom megállapítása jelenjen meg;
  - **hamis-pozitív próba:** egy szabályos, 7 és egy 9 oszlopos tábla → **nincs** `TP4/b` találat.

---

## 6. `EV7` — a parancs env-változói nem dekorációk

> **Mit mér:** ha egy **nem-lokális** kategória parancsa env-változót állít (`NÉV=érték` alakban a
> parancs elején), a változó **neve** megjelenik-e a parancs által futtatott teszt-kódban. Ha nem,
> a „dev" futás bájtra ugyanaz, mint a lokális — miközben minden bizonyíték devnek látszik.

- [ ] **6.1 — Új check a `run-tests.py`-ba: `check_env_binding(rows, repo_root)`.**
  A `check_environment_mismatch` (EV5) **mellé**, ugyanabba a szakaszba. Logika:
  1. Csak azokra a sorokra, ahol `not env_is_local(row["kornyezet"])`.
  2. A `parancs` cellából szedd ki a vezető env-hozzárendeléseket:
     `re.findall(r"(?:^|\s)([A-Z][A-Z0-9_]{2,})=", parancs)`. Ha nincs, a sor kimarad (a cél-host
     lehet kapcsolóban is — azt az `EV3` méri).
  3. Keresd meg a parancs által futtatott **útvonal-jelölteket**: a parancsból a
     `[\w./-]+\.(py|ts|js|mjs|spec\.ts|test\.py)` és a könyvtár-alakok (`test/integration/`).
     Ha egyik sem létezik a `repo_root` alatt, a check `info`-val kimarad (nem tudjuk, mit futtat).
  4. Minden változónévre nézd meg, szerepel-e **szövegszerűen** a jelölt fájlokban (könyvtárnál
     rekurzívan, csak `.py/.ts/.js/.mjs/.json/.yaml/.yml/.env*` kiterjesztésekre).
  5. Ha egy változó **sehol** nem szerepel → megállapítás:
     *„az `<kategória>` (`<környezet>`) parancsa `<VÁLTOZÓ>=…`-t állít, de ez a változónév a
     futtatott teszt-kódban nem szerepel (EV7) — a beállítás dekoráció: a futás ugyanaz, mint
     lokálisan. Vagy a kód olvassa be, vagy a parancs a tényleges kapcsolót használja."*

- [ ] **6.2 — Hova kösd.** A `main()`-ben, közvetlenül a `check_environment_mismatch` (`exit 4`)
  ág **után**, a futtatás **előtt**. **Kilépő kód: NEM új.** Az `EV7` **javaslat-szintű** (a
  kimenetben `·` sor), nem állítja meg a futást — indoklás: egy szokatlan, de működő
  kapcsoló-átadás (pl. `pytest.ini`-ből olvasott név) hamis pozitív lenne, és egy futást megállító
  hamis pozitív a legdrágább hiba. **Kivétel:** ha a sorhoz **egyetlen** env-változó tartozik, és az
  nem szerepel a kódban, **plusz** a kategória `nehéz` típusú → az üzenet `🔴` prefixet kap
  (a kimenetben feltűnő), de a kilépő kód akkor is változatlan.

- [ ] **6.3 — A `07` skill szövege (HU+EN).** A `run-tests.py` hívása körüli magyarázatba egy mondat:
  *„Az `EV7` javaslat-sorai a **nem-lokális** kategóriák env-változóit mérik: ha egy `DEV_BASE_URL=`
  a parancsban van, de a tesztkódban nincs, a „dev" futás lokális futás volt."*

- [ ] **6.4 — Verifikáció.** Gyárts a scratchpadba két sort:
  - `DEV_BASE_URL=https://app.dev.example pytest test/e2e/` + egy `test/e2e/x.py`, amely **nem**
    említi a `DEV_BASE_URL`-t → jelenjen meg az `EV7` javaslat;
  - ugyanez, de a fájlban `os.environ.get("DEV_BASE_URL")` → **ne** szóljon.
  - lokális kategória env-változóval → **ne** szóljon (nem-lokálisra szűkítünk).

---

## 7. `SK1` — a néma skip nem bizonyíték

> **Mit mér:** (a) a `dod-check.py` ne kezelje a `<skipped>` esetet `PASS`-ként; (b) a `07`
> kapujában bukjon, ha a kör JUnit-jaiban olyan eset `skipped`, amelyre a plan `TS-NN`/`TC-NN`
> lefedettsége hivatkozik.

- [ ] **7.1 — `dod-check.py`: a skip önálló állapot.** Az `index_tests(round_dir)` (a `*.xml`-eket bejáró
  függvény, ~73–91. sor; a fogyasztója a `match_test(evidence, index)`) ma így dönt:
  ```python
  failed = case.find("failure") is not None or case.find("error") is not None
  index[key] = "FAIL" if failed or prev == "FAIL" else "PASS"
  ```
  Vezess be **három** állapotot (`FAIL` > `SKIP` > `PASS` precedenciával — a rosszabb nyer):
  ```python
  failed = case.find("failure") is not None or case.find("error") is not None
  skipped = case.find("skipped") is not None
  state = "FAIL" if failed else ("SKIP" if skipped else "PASS")
  prev = index.get(key)
  index[key] = state if prev is None else _worse(prev, state)
  ```
  A `_worse(a, b)` egy háromelemű rangsor szerint választ. Ahol a script ma a `"PASS"` értéket
  vizsgálja (a `DoD-NN` bizonyíték-eldöntésnél), ott a `SKIP` **ne** számítson bizonyítéknak: a
  DoD-pont maradjon bizonyíték nélkül, a kimenetben pedig jelenjen meg, hogy **miért**
  (*„a hivatkozott teszt lefutott, de `skipped` volt"*) — ez sokkal informatívabb, mint a puszta hiány.
  > **🔴 Ez a terv legfontosabb egyetlen javítása.** Enélkül minden alábbi check megkerülhető:
  > elég egy `pytest.skip(...)` a teszt elejére, és a `DoD` bizonyítékot kap.

- [ ] **7.2 — `validate-gate-check.py`: `check_skipped_evidence(cycle, rep, stage)`.**
  1. `stage == "start"` → `return`.
  2. Gyűjtsd össze a plan `<sec:spec_coverage>` táblájából és a `<sec:test_specification>`
     szekcióból hivatkozott teszt-neveket **és** a `TS-NN`/`TC-NN` azonosítókat. A `TA1` adatlap
     `<field:f_test_cases>` sora adja a `teszt-függvény → TC-ID` leképezést — ez a join kulcsa.
  3. A legutolsó kör-mappa `*.xml` JUnit fájljaiban keresd a `skipped` eseteket.
  4. Ha egy `skipped` eset neve szerepel a plan leképezésében → `rep.bad(...)`:
     *„a `<teszt neve>` eset a `round-NN` körben `skipped` volt, de a plan `<TC-ID>`-ként
     bizonyítéknak jelöli (SK1) — a kihagyott teszt nem bizonyíték. Futtasd le, vagy írj
     `SKIP-EXEMPT: <teszt> — <miért nem futtatható ebben a körben>` sort a `check-log.md`
     `## <sec:notes>` szekciójába."*
  5. Felmentés: `SKIP-EXEMPT: <teszt-név> — <indok>` a `check-log.md` `## <sec:notes>` szekciójában.
     A parser a 4.2-ben **általánosított** `_exemptions(text, prefix, key_re=...)` — a teszt-függvény
     neve nem task-azonosító, ezért saját kulcs-mintát adj (`[\w./:\[\]-]+`).

- [ ] **7.3 — A `06` és a `07` szövege (HU+EN).** A `06-implement.md` anti-stub garde-jába
  (a `RED1/TB1` blokk mellé) egy mondat: *„A `pytest.skip` / `it.skip` / `@Disabled` **nem** zárja
  le a taskot: a némán kihagyott teszt a `07` bizonyíték-joinjában sem számít (SK1)."*
  A `07-validate.md` kapu-blokkjába egy sor az `SK1`-ről.

- [ ] **7.4 — Verifikáció.**
  - **bukás-próba:** gyárts egy JUnit XML-t egy `<skipped>` esettel, amelynek neve a plan `TA1`
    adatlapjában `TC-01`-ként szerepel → `exit 1`, az `SK1` sorral;
  - **felmentés-próba:** `SKIP-EXEMPT: <teszt> — nincs VPN ebben a körben` a `check-log.md`
    jegyzet-szekciójában → átengedi;
  - **`dod-check.py` próba:** ugyanaz az XML → a hozzá tartozó `DoD-NN` **ne** kapjon bizonyítékot;
  - **hamis-pozitív próba:** egy `skipped` eset, amelyre a plan **nem** hivatkozik (pl. platform-
    függő teszt) → **ne** bukjon.

---

## 8. Dokumentáció

- [ ] **8.1 — `README-HU.md` + `README.md`.** Három helyen:
  - a `07-validate` determinisztikus rétegének táblájába két sor: *„Lefutott-e a plan MINDEN
    validate-fázisú kategóriája?" → `validate-gate-check.py` (`RUN1`)*, és *„A kihagyott teszt
    bizonyíték-e?" → `dod-check.py` + `validate-gate-check.py` (`SK1`)*;
  - a `03b-write-test-plan` sorához egy fél mondat a `TP4/b` séma-kényszerről;
  - **új tanulság-bekezdés** a meglévők közé (a „Az üres teszt is zöld…" bekezdés **után**),
    a 2. szakasz mérésével és a négy kapu táblájával.
- [ ] **8.2 — `berki-spec-directory-structure.md`.** A `dod-check.py` és a `validate-gate-check.py`
  sorának bővítése az új checkekkel; a `run-tests.py` soráé az `EV7`-tel.
- [ ] **8.3 — `prompts/meta-improve-prompts.md`: új elv `7/m`**, a `7/l` után. Vázlat a meglévő
  elvek hangján:

  *A `7/l` a **teszt** szintjén kérdezte meg, mi bizonyítja, hogy történt is valami. Egy éles ciklus
  megmutatta, hogy ugyanez a kérdés a **kategória** szintjén még nem volt feltéve: a plan gépi
  futtatási táblájában ott állt egy `dev` kategória, a tesztek dev-módja **meg sem íródott**, a
  kategória **soha nem futott le** — és a kör `PASS`-ra zárt. A lánc négy ponton szakadt: (a) a
  tábla nem a keret sémáját követte, ezért a `run-tests.py` nem tudott belőle futtatni, és a fázis
  **kézi parancsokra** esett vissza — ahol egyetlen `EV` kapu sem fut le; (b) semmi nem mérte, hogy
  a kör lefedte-e a tábla `validate`-fázisú sorait; (c) a parancs `DEV_BASE_URL=…`-t állított,
  amit a tesztkód nem olvasott; (d) az egyetlen valódi teszt `pytest.skip`-pel kilépett, a
  `dod-check.py` pedig a `<skipped>` esetet **`PASS`-ként** indexelte, tehát a `DoD` bizonyítékot
  kapott. Négy determinisztikus kapu zárja: `RUN1`, `TP4/b`, `EV7`, `SK1`. **Prompt-módosításnál
  két kérdés:** (a) ha egy fázis egy **gépi leírót** (tábla, manifest, konfiguráció) használ
  bemenetként, mi garantálja, hogy a leíró **parse-olható**, és mi történik, ha nem — hibaüzenet
  vagy néma visszaesés kézi útra? (b) ha egy bizonyíték **három állapotú** lehet (pass / fail /
  skipped), a kapu mindhárommal számol-e, vagy a harmadikat csendben a jóhoz sorolja?*

---

## 9. Kapuk és elfogadási kritériumok

- [ ] **9.1** `python3 prompts/scripts/lang-parity-check.py` → hiba nélkül.
- [ ] **9.2** `python3 prompts/scripts/lang-parity-check.py --strict` → 0.
- [ ] **9.3** `python3 prompts/scripts/sync-gemini-agents.py --check` → 0 (ha agent-prompt változott,
  előtte írás módban regenerálva).
- [ ] **9.4** Mind a négy script **szintaktikailag ép** és a súgója fut:
  ```bash
  for s in analyze-gate-check run-tests validate-gate-check dod-check; do
    python3 -c "import ast;ast.parse(open('prompts/scripts/$s.py').read())" && echo "$s OK"
  done
  ```
- [ ] **9.5** Telepítési füstteszt legalább egy platformra, **hu és en** prompt-nyelven: a
  telepített `07-validate` és `03b-write-test-plan` fájlokban **nincs** feloldatlan `INCLUDE:`
  marker és `<sec:` / `<field:` / `<status:` token.
- [ ] **9.6** Mind a négy check **célzott bukás-próbája** lefutott: 4.4, 5.4, 6.4, 7.4 — és az
  **5.0** verifikációja is (magyar és angol fejlécű tábla ugyanazt az egy adatsort adja).
- [ ] **9.7 — Hamis-pozitív próba (kötelező).** Futtasd le a `RUN1`-et és az `SK1`-et **korábbi,
  sikeresen lezárt ciklusokra**. Ami itt bukik, azt **meg kell érteni**: vagy valódi rés volt ott is
  (akkor írd a 11. szakaszba), vagy a check túl agresszív (akkor szűkítsd). **Egy kapu, ami a jó
  ciklust is bukatja, használhatatlan.** A `TP4/b`-nél külön figyelj a régi, 7 oszlopos táblákra.
- [ ] **9.8 — Éles próba (regressziós teszt).** Ha elérhető a `cycle-30` (vagy hasonló) ciklus-mappa:
  a `RUN1`-nek és a `TP4/b`-nek **buknia kell** rajta, az `SK1`-nek az implement-fázis JUnit-ján.
  Ha valamelyik **nem** bukik, az a check hibája — nem azt méri, amit gondolunk.
- [ ] **9.9** Commit: `feat(prompts): kör-lefedettség és skip-bizonyíték keményítés — RUN1, TP4/b, EV7, SK1`
  (az **5.0** külön, előrehozott commitot is kaphat: `fix(scripts): a gépi futtatási tábla fejléce nyelvfüggetlenül`)

---

## 10. Végrehajtási sorrend

1. **7.1** — `dod-check.py` skip-javítás. *Elöl, mert egysoros osztály-javítás, és enélkül minden
   további check megkerülhető egy `pytest.skip`-pel.*
2. **5.0** — a `parse_matrix()` nyelvfüggetlen fejléc-felismerése. *Futásidejű hiba, egy
   feltétel; minden alatta lévő check ezen a parseren áll.*
3. **5.1–5.4** `TP4/b` — a tábla-séma kapuja. *A gyökérok: ez fogja meg a hibát ott, ahol keletkezik
   (a `03b` lezárásakor), nem két fázissal később.*
4. **4.** `RUN1` — kör-lefedettség. *A `TP4/b` után, mert szabályos táblát feltételez; a
   `run-tests.py` `parse_matrix()`-át hívja.*
5. **7.2–7.3** `SK1` — a kapu-oldal és a prompt-szövegek.
6. **6.** `EV7` — env-változó kötés. *A legkisebb hozam és a legnagyobb hamis-pozitív kockázat,
   ezért javaslat-szinten és utoljára.*
7. **9.6–9.7** A célzott bukás-próbák és a **hamis-pozitív próba**.
8. **8.** Dokumentáció.
9. **9.1–9.5, 9.8–9.9** Kapuk, éles próba, commit.

> **Miért a `dod-check.py` javítása az első:** a `RUN1` azt méri, hogy a kategória **lefutott-e**,
> az `SK1` azt, hogy a teszt **ellenőrzött-e**. Ha a `<skipped>` továbbra is `PASS`, akkor egy
> lefutott kategória is adhat üres bizonyítékot — a `RUN1` zöldje ilyenkor **hamis megnyugvás**.

---

## 11. Tapasztalatok (a végrehajtás közben töltsd)

> Ide kerül a 9.7 hamis-pozitív próba eredménye (mely régi ciklus min bukott, és miért), a 9.8 éles
> próba eredménye, és minden olyan felismerés, ami a terv írásakor nem látszott. Ha egy döntés
> (3. szakasz) tarthatatlannak bizonyult, **írd ide, mi lett helyette és miért** — ez lesz a
> `meta-improve-prompts.md` `7/m` elv végleges szövegének forrása.

- _(még nincs bejegyzés)_
