# „A tesztek legyenek leltározva, és cikluson kívül is futtathatók" — végrehajtási terv

> **Ez a dokumentum önhordó.** Üres kontextusban, `/clear` után is végrehajtható: az 1. szakasz
> megadja a repó-orientációt, a 2. a problémát és a mérést, a 3. a lezárt döntéseket, a 4–6. a
> tételes teendőket, a 7. a dokumentációt, a 8. a kapukat, a 9. a végrehajtási sorrendet.
> **Semmit nem kell kikövetkeztetni** — ha valami mégis hiányzik, az a terv hibája; írd bele.
>
> **Státusz:** **ELKÉSZÜLT** (2026-09-07) — a 3. szakasz döntései a felhasználóval **lezárva**,
> a végrehajtás **befejeződött**, minden kapu zöld. A tervtől való négy eltérés és a
> végrehajtás tapasztalatai a **10. szakaszban**.
> **Előzmény:** a `prompts/inprove-list10.md` (`QF1`–`QF20` · `QT1`–`QT6`) **elkészült**
> (`3132cd9`, review-utómunka `e9244f1`). Ez a kör nem egy meglévő fázist keményít, hanem
> **két új képességet** ad a kerethez: (a) egy **projekt-szintű teszt-leltárt**, amit a
> `08-doc-sync` tart karban és determinisztikus kapu véd, és (b) a tesztek **cikluson kívüli,
> kategóriánkénti futtatását** egy központi, gitignore-olt eredmény-fába.

---

## 0. Hogyan használd ezt a dokumentumot

1. **Olvasd el az 1–2. szakaszt.** Az 1. mondja meg, milyen repóban dolgozol és milyen kézi
   kapuk kötelezők; a 2. adja az indoklást és a mérést.
2. **A 3. szakasz döntéseit ne nyisd újra.** A `D1`–`D10` a felhasználóval **lezárva**
   (2026-09-07); a `D11`–`D13` a terv írója által lezárt apró döntés. Ha valamelyik a
   végrehajtás közben tarthatatlannak bizonyul, **írd a 10. szakaszba, mi lett helyette és
   miért** — ne csendben térj el tőle.
3. **A 9. szakasz sorrendjében haladj**, és minden teendő után **pipálj ebben a fájlban**
   (`- [x]` → `- [x]`).
4. **Kétnyelvű repó:** minden prompt-szerkesztés **hu ÉS en párban** megy (1.2), és ez a kör
   — a `list10`-zel ellentétben — **bővíti a `status-keys.json`-t** (6. szakasz).
5. **Nincs CI és nincs pre-commit hook** — a kapukat (8. szakasz) **kézzel futtasd le**, commit előtt.

---

## 1. Orientáció — mi ez a repó, és mi mozdul

### 1.1 A rendszer

A `berkispec` egy **spec-driven development keretrendszer promptokból**: fázis-skillek (`00`–`09`,
a `03` `03a`/`03b`-re hasadva), segédparancsok (`brainstorm`, `manual-test-plan`, `cycle-status`,
`export-doc`, `quick-flow`), subagent-promptok és determinisztikus **kapu-scriptek**
(`prompts/scripts/`, ma 22 fájl). A repó a **forrás**; egy célprojektbe az `install.sh` /
`install.ps1` → `prompts/scripts/install-helper.py` telepíti (öt platform: claude, codex,
antigravity, cursor, copilot). A telepítő **build-time** oldja fel az
`<!-- INCLUDE:shared/… -->` / `<!-- INCLUDE:lang/… -->` markereket (általános regex,
`install-helper.py:258`–`:288`, rekurzívan `_MAX_INCLUDE_DEPTH = 5`) és a
`<sec:…>` / `<field:…>` / `<status:…>` tokeneket, majd a skillt `bs-<stem>/SKILL.md` alá írja.

**Két fejlesztési út él egymás mellett:** a **teljes flow** (`00`–`09`) és az **egyszerűsített**
(`/bs-quick-flow`). Ez a kör **mindkettőt érinti**, de a súlypontja a `08-doc-sync` (a leltár
gazdája) és egy **új segédparancs**.

Amit ez a terv érint:

| útvonal | mi ez | ÚJ? |
|---|---|---|
| `prompts/skills-{hu,en}/08-doc-sync.md` | a leltár **kizárólagos gazdája** (LD1–LD8) | — |
| `prompts/lang/{hu,en}/08-doc-sync.md` | a leltár sablon-horgonyai | — |
| `prompts/skills-{hu,en}/run-tests.md` | a `/bs-run-tests` segédparancs | **ÚJ** |
| `prompts/lang/{hu,en}/run-tests.md` | a segédparancs user-facing blokkjai | **ÚJ** |
| `prompts/scripts/test-inventory-check.py` | a leltár teljesség-kapuja (LD5) | **ÚJ** |
| `prompts/scripts/run-tests.py` | projekt-szintű tábla-forrás (KT3) | — |
| `prompts/scripts/dod-check.py` · `report-gate-check.py` | bizonyíték-tűzfal (KT6) | — |
| `prompts/skills-{hu,en}/00-init-project.md` | a kategória-szótár és a futtatási tábla bekérdezése (KT1) | — |
| `prompts/lang/{hu,en}/00-init-project.md` | a `## <sec:cv_test_execution>` szekció sablonja | — |
| `prompts/skills-{hu,en}/03b-write-test-plan.md` | a leltár mint current truth (LD9) | — |
| `prompts/skills-{hu,en}/manual-test-plan.md` | a leltár mint harmadik bemenet (LD9) | — |
| `prompts/skills-{hu,en}/quick-flow.md` | leltár-drift jelzés (LD10, a `7/o` elv szerint) | — |
| `prompts/lang/status-keys.json` | **6 új kulcs** mindkét nyelven (6. szakasz) | — |
| `prompts/lang/{hu,en}/descriptions.json` | a `bs-run-tests` telepített leírása | — |
| `.gitignore` | `test-runs/` | — |
| `README-HU.md` · `README.md` · `prompts/meta-improve-prompts.md` · `berki-spec-directory-structure.md` | dokumentáció (7. szakasz) | — |

### 1.2 A két nyelvi tengely (LG2/LG5) — és amit ez a kör bővít

- **prompt-nyelv:** a `prompts/skills-hu/` vs. `prompts/skills-en/` fa (az ágens *instrukcióinak*
  nyelve). **Minden szerkesztés mindkét fán megy, párban.**
- **projekt-nyelv:** amit az ágens a célprojektbe *ír* — ezt a `prompts/lang/{hu,en}/` blokkok és a
  `status-keys.json` tokenjei adják. Artefaktum-szekciónév, mezőnév és státusz-érték a promptban
  **nem literál**, hanem `<sec:…>` / `<field:…>` / `<status:…>` token.
- **⚠ Ez a kör BŐVÍTI a `status-keys.json`-t** (a `list10` nem tette) — a szükséges 6 kulcs a
  **6. szakaszban tételesen fel van sorolva, hu és en értékkel együtt**. A fájl szerkezete:
  `{"hu": {"sections": {…98}, "fields": {…66}, "status": {…37}}, "en": {…}}`.
- **Nyelvfüggetlen literálok, amiket NEM tokenizálunk** (ugyanazon az indokon, amiért az `EV8`
  `[local]`/`[remote]` címkéje sem az): a `TL-NNN` azonosító-prefix, a `test-runs/` mappanév, a
  kategória-azonosítók (`unit` · `rest-e2e` · `ui`), az `<env>` mappaszegmens (`local`/`remote`)
  és a `results.json` kulcsai. Ezek **útvonalra és kapura joinolnak**.
- **A telepítő nem igényel módosítást az új skillhez — ellenőrizve.** Az `install-helper.py`
  a skilleket **globbal** deríti fel (`skills_src.glob("*.md")`, pl. `:851`, `:933`, `:966`,
  `:1001`, `:1048`), tehát az új `run-tests.md` magától bekerül mind az öt platformra.
  **DE:** a `descriptions.json`-ban **kötelező** kulcsot kap, különben a telepítő hibát ír
  (`install-helper.py:440`).

### 1.3 Kötelező kézi kapuk (nincs CI, nincs pre-commit hook)

```bash
python3 prompts/scripts/lang-parity-check.py            # szerkezeti paritás  → 0
python3 prompts/scripts/lang-parity-check.py --strict    # fájlhalmaz-paritás → 0
python3 prompts/scripts/sync-gemini-agents.py --check    # agent.json tükrök  → 0
```
- A `--strict` a **fájlhalmaz**-paritást méri (`check_file_sets`): az új `skills-hu/run-tests.md`
  és `lang/hu/run-tests.md` **csak a `-en` párjával együtt** mehet be.
- A `lang-parity-check` **11.3** checkje az **árva horgonyt** is elbukja: minden új `ANCHOR`-ra
  kell hivatkozó `INCLUDE` marker, mindkét nyelven.
- **Agent-promptot ez a kör módosít** (`LD11/2`: a `doc-sync-planner.md` frontmattere), tehát a
  `sync-gemini-agents.py`-t **előbb írás módban** kell futtatni, utána `--check` → 0. Új
  subagent nem keletkezik.
- **Build-füstteszt kötelező** (három dolog törhet: új skill-fájl, új `descriptions.json` kulcs,
  új tokenek):
  ```bash
  python3 prompts/scripts/install-helper.py claude . <tmp>/hu hu hu   # → Success
  python3 prompts/scripts/install-helper.py claude . <tmp>/en en en   # → Success
  # majd: a telepített bs-run-tests és bs-doc-sync SKILL.md-ben
  # nulla feloldatlan `INCLUDE:` marker és nulla `<sec:|<field:|<status:` token
  ```

### 1.4 A hivatkozott azonosítók — hol nézd meg őket

| hol | mit ad |
|---|---|
| `prompts/meta-improve-prompts.md` „Tervezési elvek" (`7/b`–`7/o`) + a script- és shared-tábla | minden keményítő kör indoklása, és melyik script mit mér |
| `prompts/skills-hu/08-doc-sync.md` | a `docs-generated/` fájlkészlet (`:103`–`:107`), a DS21 mappa-index (`:273`), a TC1–TC11 regiszter (`:283`), példa recept (`:698`) |
| `prompts/lang/hu/00-init-project.md:146`–`:170` | a `conventions.md` `## Teszt-riportolás` szekció sablonja (TR3/TR5/TR6) — az új futtatási tábla ennek a **szomszédja** |
| `README-HU.md` | a felhasználónak szánt leírás, flow-ábrák, a hurkok konvenciói |
| `prompts/inprove-list{9,10}.md` | a legutóbbi két kör tételes terve (`EV8`–`EV10`, `RL1`/`RL2`, `QF`/`QT`) |

Konkrétan hivatkozott, **meglévő** azonosítók: `TC1`–`TC11` (teszt-elvárás regiszter),
`TC10/b` (részletező blokk), `TR3`/`TR5`/`TR6` (riport-tábla, kör-mappa, riport-fázisok),
`TP4/b` (gépi futtatási tábla oszlop-sémája), `TS-NN` (plan teszt-forgatókönyv),
`TG-NN` (kézi teszt-csoport), `R-NN` (recept), `DoD-NN`, `RUN1` (kör-lefedettség),
`SK1` (`skipped` ≠ bizonyíték), `EV1`–`EV5`/`EV8` (cél-környezet, literál host, probe,
localhost-tilalom, hatókör-címke), `DS21`/`DS22` (mappa-index, doc-konzisztencia kapu),
`MT1`/`MT3`/`MT6` (kézi tesztterv kapuja, kétmódúság, lefedettség), `QF7`/`QF17` (quick-flow
drift-jelzés, segédparancs-tábla), `RP1` (útvonal-formátum), `PE1` (fázishatár),
`7/e` (egy fogalom, egy útvonal-alak), `7/m` (a parser ne legyen „okos"), `7/o` (a másik út is
elcsúszhat).

---

## 2. A probléma és a mérés

### 2.1 Három mérhető hiány

**(a) Nincs projekt-szintű válasz arra, hogy „milyen tesztek léteznek".** A `specs/test-conventions.md`
(TC1–TC11) **promóció-alapú és recept-alakú**: csak az kerül bele, amit a felhasználó a doc-syncben
jóváhagy, és arra válaszol, hogy *„hogyan futtatom"*. A `plan.md` `TS-NN` blokkjai és a
`manual-test-plan.md` `TG-NN` csoportjai **per-ciklus** élnek. Következmény: egy új kolléga vagy egy
friss kontextusú ágens **nem tud egy helyről végigolvasni**, milyen tesztek vannak, és mit
bizonyítanak. Mérés: a repó egyetlen artefaktum-sablonja sem ígér teljes teszt-listát — a
`docs-generated/` fájlkészlete (`08-doc-sync.md:103`–`:107`) öt fájlt sorol, teszt-leltár nincs köztük.

**(b) Cikluson kívül nem lehet kategóriát futtatni.** A `run-tests.py` **kötelező pozicionális
argumentuma** a `plan_file` (`:570`), és a `--round-dir` is `required=True` (`:571`). Vagyis a keret
minden gépi futtatása **egy ciklushoz és egy körhöz kötött**. Az „futtasd le az összes e2e tesztet"
kérés ma **nem kivitelezhető** a kereten belül — csak a keret alatt, kézzel, bizonyíték nélkül.

**(c) Az ad-hoc futásnak nincs helye.** A riport ma mindig a ciklusban landol
(`specs/cycle-NN-<name>/test-report/{implement,validate}/round-NN/`, TR5/TR6). Egy cikluson kívüli
regressziós futás vagy **beszennyezi egy ciklus bizonyítékát** (és megbukik a TR7 frissesség-, ill.
a RUN1 kör-lefedettségi kapun), vagy nyomtalanul elveszik.

### 2.2 Amit a keret MA tud (hogy ne tervezzünk mellé)

| Ma | Mit tárol | Gazda | Ki olvassa |
|---|---|---|---|
| `specs/test-conventions.md` (TC1–TC11) | visszatérő teszt-elvárás **+ futtatható recept**: `R-NN`, `<field:f_startup>`, `<field:f_example_call>`, `<field:f_prerequisite>`, `<field:f_cleanup>`, `<status:scope_shared_remote>` | `08-doc-sync` (`tc8-gate-check.py`) | `02`, `03b`, `quick-flow` (csak olvasás) |
| `conventions.md → ## <sec:cv_test_reporting>` | riport-**artefaktumok**, útvonal-alap, riport-generáló parancs kategóriánként | `00-init-project` | `report-gate-check.py` |
| `plan.md` gépi futtatási tábla (TP4/b) | **ciklus**-szintű futtatható sorok: kategória, `<field:f_environment>`, fázis, parancs, időkorlát | `03b` | `run-tests.py` |
| `test-report/{implement,validate}/round-NN/` | a kör bizonyítéka | `06`/`07` | `dod-check.py`, `report-gate-check.py` |

**Tehát a futtató már megvan, és már ismeri a `local`/`remote` tengelyt** (`<field:f_environment>`,
EV2/EV8). Ami hiányzik: (i) egy **projekt-szintű futtatási tábla**, (ii) a cikluson kívüli futás
**helye és szabálya**, (iii) az **emberi teszt-leltár**.

### 2.3 A két vállalt kockázat — és a mitigációja

A `D3` és a `D2` a felhasználó **tudatos** döntése; a terv írója mindkettőnél fenntartást
jelzett, ezért **mérhető mitigáció** kerül melléjük. Ezek nem opcionálisak:

1. **Átfedés a `test-conventions.md` TC10/b részletező blokkjával** (`D3`). A mitigáció a
   **mező-szintű tulajdon** + a **kétirányú join** (`LD6`): a két artefaktum ugyanazt a tesztet
   *említheti*, de **egyetlen mezőt sem duplikál**, és a kapu mindkét irányban méri a
   hivatkozást. Így az átfedés **látható és joinolt**, nem néma — pontosan az a különbség,
   amiért az `RP1` a három helyen élő útvonal-szabályt megszüntette.
2. **A kézi reprodukciós szint elavulása** (`D2`): literál host és konkrét parancs a
   katalógusban azt jelenti, hogy egy port- vagy host-váltás **csendben elavultat** hagy. A
   mitigáció (`LD7`): kötelező `<field:f_last_run>` a tételen, és a kapu **összevetése** a
   `conventions.md`-ben deklarált környezetekkel — ha a tételben olyan host áll, amit a projekt
   már nem deklarál, a kapu jelzi.

---

## 3. Lezárt döntések

### A felhasználóval egyeztetve (2026-09-07 — ne nyisd újra)

- **D1 — A leltár helye és gazdája.** `docs-generated/test-description.md`, és a **kizárólagos
  gazdája a `08-doc-sync`** (mint a `docs-generated/` többi fájljának). Következmény, amit ki kell
  mondani: egy **cikluson kívül** vagy **quick-flow-ban** írt teszt csak a következő doc-sync
  futásban jelenik meg a leltárban — erre szolgál a `LD10` drift-jelzés.
- **D2 — A tétel alakja: kézi reprodukció szintje.** Sorszám + cél + lépések, ahol a lépések
  **konkrét parancsot/hívást és konkrét elvárt eredményt** tartalmaznak (mint a
  `bs-manual-test-plan` `TG-NN` csoportjai). Nem viselkedés-szintű összefoglaló.
- **D3 — A `test-conventions.md` TC10/b MARAD, eltérő hatókörrel.** TC10/b csak a **promótált,
  visszatérő** elvárásokra; a leltár **minden** tesztre. **Mező-szintű tulajdon:** a leltár a
  *cél / lépések / elvárt eredmény* igazsága, a `test-conventions.md` a *recept*
  (`<field:f_startup>`, `<field:f_example_call>`, `<field:f_prerequisite>`, `<field:f_cleanup>`,
  credential-pointer) igazsága. Ütközés esetén **mezőnként az adott fájl nyer**; azonos mezőt a
  kettő nem hordoz.
- **D4 — `TL-NNN` új azonosító-prefix.** A repóban **szabad** (ellenőrizve: 0 előfordulás).
  Projekt-szintű, **soha nem újrahasznosított** sorszám, három számjegy (`TL-001`). Tesztfájl
  átnevezése, mozgatása vagy átírása **nem** változtatja meg. Kivezetett teszt tétele
  `<status:retired>` jelölést kap, és **nem törlődik** (audit-nyom).
- **D5 — Teljesség: kemény kapu.** Új `test-inventory-check.py`: a `conventions.md`-ben deklarált
  tesztfájl-helyekről felderíti a létező teszteket, és **halmaz-egyezést** kér a leltár
  azonosítóival (a DS21 mappa-index kapu mintájára). Eltérés → a doc-sync nem zárható.
  **`TL-EXEMPT` felmentő lista NINCS** — a hatókör szűkítése a `conventions.md` tesztfájl-hely
  deklarációjában történik (ez az egyetlen szabályozott kiskapu).
- **D6 — Kategória-szótár: projekt-deklarált.** A projekt a `conventions.md`-ben sorolja fel a
  kategóriáit (alap-javaslat: `unit` · `rest-e2e` · `ui`, opcionálisan `coverage`). A keret annyit
  köt ki, hogy a `plan.md` gépi táblájának `Kategória` értékei a deklarált halmaz **részhalmazai**
  legyenek — ez gépiesen ellenőrizhető (`KT2`). **A `unit` is része a központi futtatásnak.**
- **D7 — A központi futtatás mappája `test-runs/`, gitignore-olt.** Séma:
  `test-runs/<kategória>/<UTC-időbélyeg>/<env>/<TL-NNN>/`, a futás gyökerében `results.json`.
  A név szándékosan **nem** `test-results/`: az a mai `test-report/`-tól egy betűben térne el, és a
  `7/e` elv pont az ilyen útvonal-összekeverésekből született.
- **D8 — Bizonyíték-tűzfal.** A `test-runs/` alatti eredmény **soha nem bizonyíték** a `06`/`07`
  kapuiban. A `results.json` `"cycle": null` jelölőt kap, és a `dod-check.py` +
  `report-gate-check.py` **visszautasítja** a `test-runs/` alatti `--round-dir`-t. Indok: a keret
  bizonyíték-logikája `DoD-NN`/`TS-NN` joinra, TR7 frissességre és RUN1 kör-lefedettségre épül —
  egy cikluson kívüli futásnak nincs mihez joinolnia. Enélkül az első dolog, amit egy gyengébb
  modell tenni fog: lefuttatja a központi szvitet, és ráállítja a `dod-check.py`-t.
- **D9 — Nincs negyedik útvonal-bázis (`7/e`).** A központi futás **nem** új bázis: a
  `run-tests.py --round-dir` már ma **repó-gyökér-relatív**, tehát a `test-runs/…` csak egy másik
  ÉRTÉK ugyanabban a paraméterben. A `conventions.md` `**<field:f_artifact_path_base>**` jelölője
  **változatlan** (a ciklus-riportokra vonatkozik).
- **D10 — A futtató segédparancs.** `/bs-run-tests`, a `bs-manual-test-plan` mintájára: **nem
  fázis**, státuszt nem változtat, a `00`–`09` láncot nem érinti, subagent nélkül fut, bármikor
  újrafuttatható. A projekt-szintű futtatási tábla a `conventions.md`
  `## <sec:cv_test_execution>` szekciója, **azonos oszlop-sémával**, mint a plan gépi táblája
  (TP4/b) — egy parser, egy szabály (`7/m`: a parsert **nem** tesszük „okossá", hogy kétféle
  táblát is megegyen).

### A terv írója által lezárva (kis, visszafordítható döntések)

- **D11 — Időbélyeg és mutató.** UTC, `YYYY-MM-DDTHH-MMZ` alak (rendezhető, kettőspont nélküli,
  tehát Windows-on is érvényes mappanév). A `test-runs/latest.json` **fájl** (nem szimlink —
  a szimlink Windows-on külön jogot igényel, és az `init-project.sh` szimlink-alapú ága LG19
  szerint elavult).
- **D12 — Megtartás/takarítás.** A `test-runs/` **soha nem takarít magától**: a keret takarítási
  biztonsági szabálya (csak az aktuális futás által létrehozott elem törölhető) itt is él. A
  `/bs-run-tests` a záró üzenetben kiírja a mappa méretét, és **csak explicit kérésre** ajánl
  ritkítást.
- **D13 — A skill neve és shared-blokkjai.** Fájlnév `prompts/skills-{hu,en}/run-tests.md` →
  telepítve `bs-run-tests` (a `prompts/scripts/run-tests.py` névazonossága szándékos: a skill
  ezt a scriptet vezényli). Beemelt blokkok: `shared/context-check.md` (a `conventions.md`-t
  olvassa) és `shared/python-cmd.md` (a script-hívás alakja). `path-format.md` **nem** kell:
  ez a skill nem szerkeszt tervezési artefaktumot.

---

## 4. A teszt-leltár (`docs-generated/test-description.md`)

- [x] **LD1 — Az artefaktum szerkezete.** Fejléc (`<field:f_last_run>`-mentes, de a generálás
      dátumával), majd **kategóriánként egy szekció** a `conventions.md`-ben deklarált kategória
      nevével (D6), és a szekción belül a `TL-NNN` tételek **sorszám szerint**. A fájl
      címsora/fő szekciója `<sec:test_inventory>`. A tételek **nem** rendeződnek át a
      kategória-váltáskor: a `TL-NNN` sorszám globális és állandó (D4).
- [x] **LD2 — A tétel adatlapja** — új `ANCHOR` a `prompts/lang/{hu,en}/08-doc-sync.md`-ben,
      a skillben INCLUDE marker hivatkozik rá. Kötelező mezők (mind **meglévő** token, kivéve
      ahol jelezve):
      `### TL-NNN — <cím>` · `**<field:f_environment>:**` `local` / `remote` ·
      `**<field:f_goal>:**` (egy állítás-mondat: mit bizonyít, melyik képességre) ·
      `**<field:f_steps>:**` (számozott lépések, **konkrét parancs/hívás**) ·
      `**<field:f_expected_result>:**` (eldönthető érték, backtickben) ·
      `**<field:f_run_command>:**` (**ÚJ token** — a szelektoros futtatás egy sorban) ·
      `**<field:f_recipe>:**` (`R-NN` hivatkozás vagy „—") ·
      `**<field:f_last_run>:**` (dátum + `local`/`remote`) ·
      `**<field:f_source_cycle>:**` (**ÚJ token** — melyik ciklus hozta létre).
      **Kalibrációs minta kell mellé** (kitöltött példa), mert a `7/h` szerint a padló önmagában
      nem termel részletet — a mintát a `08-doc-sync.md:698` `R03` recept és a
      `03b-write-test-plan.md` `TS-NN` blokkja sűrűségéért másold, ne a témájáért (`TD5`).
- [x] **LD3 — Azonosító-életút (D4).** A `08` **soha nem használ újra** `TL-NNN`-t, és **nem
      írja át** a meglévőt (a `TS`/`AF` azonosítók szabálya: a join szó szerinti egyezésre épül).
      Megszűnt teszt tétele `<status:retired>` (**ÚJ token**) jelölést kap az indoklással és a
      kivezető ciklussal; a tétel a fájlban **marad**.
- [x] **LD4 — A `08` karbantartási lépései.** Minden doc-sync futásban: (a) sorold fel a ciklus
      tesztjeit (a `test-report/` tényleges tartalmából és a `plan.md` `TS-NN` blokkjaiból),
      (b) vezesd át a leltárba (új tétel / meglévő frissítése / `retired`), (c) a **nem
      verifikált** adatot **ne** írd be, hanem kérdés a `doc-sync-questions.md`-be (a `TC3`
      verifikációs szabály mintájára), (d) a `<field:f_last_run>` bumpolása.
      **A leltár a `doc-sync-plan.md` pipálható tervének külön sorát kapja** (per-fájl terv, DS-minta).
- [x] **LD5 — `test-inventory-check.py` (a kemény kapu, D5).** Amit mér:
      1. **Felderítés ↔ leltár halmaz-egyezés:** a `conventions.md` tesztfájl-hely deklarációjából
         globbal összeszedett tesztfájlok mindegyikéhez tartozik legalább egy `TL-NNN` tétel, és
         minden `TL-NNN` tétel `<field:f_run_command>`-ja **létező** fájlra mutat (nem `retired`
         tételnél). Hiány mindkét irányban → `exit 1`, a hiányzó elem tételes felsorolásával.
      2. **Hézagmentes, egyedi `TL-NNN`** (a `TS6` mintája).
      3. **Kötelező mezők jelenléte** minden tételen (LD2).
      4. **Kategória-érvényesség:** a tétel kategóriája a `conventions.md`-ben deklarált halmazból van.
      5. **`<field:f_environment>` értéke** pontosan `local` vagy `remote` (EV8 literál).
      6. **Kétirányú `R-NN` join** (LD6).
      7. **Elavult cél-host** (LD7) — ez **figyelmeztetés** (`exit 0` + WARN), nem bukás.
      **A CLI-szerződés (a `tc8-gate-check.py:627`–`:633` tényleges alakja szerint)** —
      _a 6. checkhez egy negyedik, opcionális flag is kellett (`--test-conventions`), lásd a
      10.3 szakaszt:_
      ```
      test-inventory-check.py [docs-generated/test-description.md]  # pozicionális, opcionális, ez az alapérték
                              --project-root .                       # a felderítés gyökere
                              --conventions conventions.md           # a kategória-szótár és a globok forrása
      exit 0 = PASS (WARN-ok a kimeneten) · 1 = FAIL (tételes hiánylista) · 2 = használati hiba
      ```
      A kimenet nyelve a `lang_keys.py`-n megy (mint a többi kapunál).
- [x] **LD6 — Kétirányú join a `test-conventions.md`-vel (a D3 mitigációja).** Ha egy `TL-NNN`
      tételhez tartozik recept, a tétel `<field:f_recipe>`-je az `R-NN`-re mutat, **és** a
      `test-conventions.md` `R-NN` adatlapja visszamutat a `TL-NNN`-re. A kapu **mindkét irányt**
      méri (a `TS5` kétirányú `DoD-NN` ↔ `TS-NN` lefedettség mintájára). Egyoldalú hivatkozás → bukás.
      **Mező-szintű tulajdon kimondása:** a `08` a TC10/b részletező blokkba **nem** írja be újra a
      lépéseket, hanem a `TL-NNN`-re hivatkozik; a leltár pedig **nem** ismétli meg az indítást,
      a példa hívást, az előfeltételt és a takarítást.
- [x] **LD7 — Frissesség (a D2 mitigációja).** A `<field:f_last_run>` kötelező, és a kapu
      összevetést végez: a tételek parancsaiban szereplő **cél-hostok** részhalmazát adják-e a
      `conventions.md`-ben deklarált környezeteknek. Ha egy tétel olyan hostot használ, amit a
      projekt már nem deklarál, a kapu **WARN**-t ad a tétel azonosítójával, és a `08` kérdést
      tesz a `doc-sync-questions.md`-be.
- [x] **LD8 — Bootstrap és mappa-index.** (a) A `docs-generated/README.md` (DS21) index-sort kap a
      `test-description.md`-re — a DS21 **halmaz-egyezés** kapu különben elbukik.
      _(Ellenőrizve: a `ds22-gate-check.py` `check_folder_index()` (`:79`) a mappa **tényleges**
      `.md` listáját veti össze a README bejegyzéseivel — **nincs bedrótozott fájllista**, tehát
      script-módosítás nem kell, csak az index-sor.)_
      (b) A leltár bootstrapja **független** a `system-overview.md` bootstrap-ágától (a
      `test-conventions.md` mintájára, `08-doc-sync.md:361`): akkor is le kell futnia, ha a
      `docs-generated/` most születik. Bootstrapkor a felderítés adja a `TL-NNN` vázakat, a
      leírásokat a felhasználóval kell kitölteni — **találgatni tilos** (TC3).
- [x] **LD9 — Fogyasztók (csak olvasás).** Egy-egy bekezdés:
      - **`03b-write-test-plan.md`** — a leltár **current truth** a meglévő tesztekről: a
        regressziós kör kiválasztásához és a duplikáció elkerüléséhez innen olvass (ma erre
        semmi nem mutat). A fájlt a `03b` **nem írja**.
      - **`manual-test-plan.md`** — **harmadik bemenet** a `plan.md` és a `spec.md` mellé: a
        `TG-NN` csoportok a `TL-NNN` tételekből **összeszerelhetők** (az MT „nem felderít, hanem
        összeszerel" elve), és a `TG-NN` fejléce hivatkozik a `TL-NNN`-re. Ez csökkenti az MT
        munkáját, és a `TL` ↔ `TG` join az MT6 lefedettséget is erősíti.
      - **`02-write-spec.md`** — egy sor: a leltárból látszik, mi van már letesztelve, tehát a
        spec ne írjon elő már létező tesztet újra.
- [x] **LD10 — quick-flow drift-jelzés (`7/o`).** A `quick-flow` lezárási pontja (ma QF7 a
      `design-drift.md`-re) mondja ki: ha a ciklus **tesztet adott vagy módosított**, a
      `docs-generated/test-description.md` a következő teljes ciklus `08-doc-sync` fázisáig
      **elavult marad** — ez bekerül a drift-sorba **és** a felhasználóhoz szóló figyelmeztetésbe.
      A leltárhoz a quick-flow **nem nyúl** (D1: a gazda a `08`).

- [x] **LD11 — A két frontmatter, amit könnyű elfelejteni** (mindkettő **hu + en** párban):
      1. **`08-doc-sync.md` `output:` lista** (`:9`–`:14`) — új sor a
         `docs-generated/test-description.md`-re, a `specs/test-conventions.md` sorának (`:11`)
         stílusában. A frontmatter-listák hosszát a `lang-parity-check.py` **méri**
         (`frontmatter_list_lengths`), tehát a hu és az en lista **ugyanannyi elemű** legyen.
      2. **`agents-{hu,en}/doc-sync-planner.md`** — a `08` tervkészítő subagentje.
         **Ellenőrizve:** a prompt szándékosan projektfüggetlen (*„Skill-szinten csak az
         `architecture.md` és a `system-overview.md` kötelező. Minden más fájlt a
         `docs-generated/` mappa bejárásából … vegyél fel"*, `:30`), tehát a leltárt
         **bejárással megtalálja** — de az `LD4` **aktív karbantartási** teendői (a ciklus
         tesztjeinek felsorolása, `retired` jelölés, kérdés a nem verifikált adatra) ebből
         **nem következnek**. Ezért a `test-conventions.md` mintájára (`:11`, `:17`) a leltár is
         kap egy bemeneti és egy terv-tétel sort.
      **🔴 Következmény a kapukra:** ezzel **agent-frontmatter változik**, tehát a
      `sync-gemini-agents.py`-t **írás módban is** le kell futtatni (8. szakasz).

---

## 5. A központi futtatás (`/bs-run-tests` + `test-runs/`)

- [x] **KT1 — `conventions.md` `## <sec:cv_test_execution>` szekció** (**ÚJ token**) — sablon a
      `prompts/lang/{hu,en}/00-init-project.md`-be, a `## <sec:cv_test_reporting>` (`:146`)
      **szomszédjaként**, és kötelező bekérdezés a `00-init-project.md`-ben (a TR3 kérdés
      mintájára). Tartalma:
      - `**<field:f_test_categories>:**` (**ÚJ token**) — a projekt kategória-szótára,
        vesszővel (`unit, rest-e2e, ui`).
      - A **futtatási tábla**, a plan gépi táblájával **azonos oszlop-sémával** (TP4/b).
        **🔴 AZ ITT EREDETILEG FELSOROLT ÖT OSZLOP TÉVES VOLT — lásd a 10.1 szakaszt:**
        a `D10` „azonos oszlop-séma" elve nyert, tehát a tábla a **teljes kilenc oszlopos**
        TP4/b sémát követi (`Kategória | Típus | Előfeltétel | Parancs | Eredményfájl |
        Formátum | Takarítás | <field:f_environment> | <field:f_phase>`).
        A tábla fejléce a `run-tests.py:86` `HEADER_FIRST_CELL_WORDS` szerint felismerhető
        (`kategória` / `category`) — **ne írj más első oszlopot**.
      - **Tesztfájl-helyek deklarációja** (a `LD5` felderítés bemenete): kategóriánként egy
        vagy több glob (pl. `rest-e2e: tests/e2e/**/*.spec.ts`). Ez az `LD5` kapu **egyetlen
        szabályozott kiskapuja** (D5).
        **⚠ ÜTKÖZÉS-FIGYELMEZTETÉS (RP1):** a `conventions.md` teszt-stack szekciója **ma is
        deklarál** tesztfájl-helyet, prózában — `prompts/lang/hu/00-init-project.md:140`:
        *„Tesztfájlok helye: `test/` …"*. **Ne hozz létre második igazságot.** A határvonal: a
        **gépiesen olvasott, kategóriánkénti globok** kizárólag a `## <sec:cv_test_execution>`
        szekcióba kerülnek, és a meglévő prózai sor **pointert kap** rá (*„a gépi felderítés
        globjait a `## <sec:cv_test_execution>` adja"*). A prózai sort **ne töröld** (emberi
        olvasónak szól), de értéket se duplikálj benne.
      - **EV-szabályok érvényesek:** `remote` kategória sora **literál cél-hostot** hordoz
        (EV3), és van hozzá `Előfeltétel`-probe (EV4); `localhost`/`127.0.0.1` tilos deklarált
        port-forward nélkül (EV5).
- [x] **KT2 — Kategória-részhalmaz kapu (D6).** Az `analyze-gate-check.py`-ba (a plan-oldali
      checkek közé) egy check: a `plan.md` gépi futtatási táblájának `Kategória` értékei
      részhalmazai a `conventions.md` `<field:f_test_categories>` halmazának. Eltérés → a
      `03b` lezáró kapuja bukik, a nem deklarált érték felsorolásával.
      _(Ez ma szabad szöveg, tehát csendben elcsúszhat — ugyanaz a hibamód, mint a `TP4/b`-nél.)_
- [x] **KT3 — `run-tests.py`: projekt-szintű tábla-forrás.** A `parse_matrix()` (`:94`)
      **szövegre** dolgozik, tehát a parser **változatlan** marad (`7/m`). Amit módosítani kell:
      a `plan_file` pozicionális argumentum (`:570`) általánosítása — javasolt alak:
      `--table-source plan|conventions` + a fájl útvonala, a régi pozicionális hívás
      **visszafelé kompatibilisen** megtartva. A `--round-dir` (`:571`) marad kötelező; a
      központi futásnál az értéke `test-runs/…`. A `--json` alapértéke (`:590`)
      `<round-dir>/results.json` — ez a központi futásnál is jó.
      **A meglévő hívási helyek — MINDET nézd át, egyik sem törhet** (a `-hu` fa; az `-en`
      párja ugyanott, plusz a `gemini-agent/*/agent.json` tükrök, amiket a
      `sync-gemini-agents.py` generál):

      | fájl | hívás |
      |---|---|
      | `skills-{hu,en}/07-validate.md` | **14** |
      | `skills-{hu,en}/03b-write-test-plan.md` | **9** (a gépi tábla dokumentálása) |
      | `agents-{hu,en}/test-runner.md` | 2 |
      | `skills-{hu,en}/06-implement.md` · `03a-write-code-plan.md` · `quick-flow.md` | 1-1 |
      | `agents-{hu,en}/implement-fixer.md` · `review-fixer.md` | 1-1 |
      | `shared-{hu,en}/quality-check-plan-test.md` · `conventions-change.md` | 1-1 |

      **Scriptek, amelyek a `run-tests.py`-ra hivatkoznak vagy vele joinolnak** (ezeket is
      ellenőrizd, ha a CLI változik): `analyze-gate-check.py`, `report-gate-check.py`,
      `round-log.py`, `validate-gate-check.py`, `manual-test-gate-check.py`, `install-helper.py`.
      _Ha a régi pozicionális alak megmarad, ezek egyike sem igényel szerkesztést — ezért
      választjuk a **bővítést** és nem az átírást (`7/m`: a hívó ne találgasson)._
- [x] **KT4 — `/bs-run-tests` skill (hu + en).** Tartalma:
      - **Belépő alakok:** `/bs-run-tests` (kérdezze meg, melyik kategória és melyik környezet),
        `/bs-run-tests <kategória>`, `/bs-run-tests <kategória> <local|remote>`.
      - **Nem fázis (D10):** státuszt nem változtat, ciklus-artefaktumot nem ír, a `00`–`09`
        láncot nem érinti, subagent nélkül fut. Ezt **ki kell mondani** (az MT4 mintájára).
      - **A futás menete:** `conventions.md` beolvasása → a kategória sorainak kiválasztása →
        `remote` célnál a probe lefuttatása (EV4) → `run-tests.py` hívása a `test-runs/…`
        kör-mappára → a `results.json` és a riport-artefaktumok helyének kiírása.
      - **Záró összefoglaló:** kategória, környezet, futott/bukott/`skipped` bontás
        (a `skipped` **nem** zöld — SK1), a mappa útvonala, a `test-runs/` teljes mérete (D12).
      - **Bizonyíték-tűzfal kimondva (D8):** *„ez a futás NEM ciklus-bizonyíték; a `07` kapuja
        nem fogadja el"* — plusz a `latest.json` frissítése.
- [x] **KT5 — A mappa-séma és a mutató.** `test-runs/<kategória>/<YYYY-MM-DDTHH-MMZ>/<env>/<TL-NNN>/`,
      a futás gyökerében `results.json`, a `test-runs/latest.json`-ben kategóriánként az utolsó
      futás útvonala és összegzése (D11). A `<TL-NNN>` szegmens joinolja az eredményt a leltárhoz —
      **ez a leltár második haszna**: egy központi futás eredménye tételenként visszakereshető.
      _(Ha egy futtatott teszt nem azonosítható `TL-NNN`-hez, az `LD5` kapu hiányát jelzi — a
      skill ilyenkor `unmapped/<teszt-név>/` alá írja, és a záró üzenetben jelzi.)_
- [x] **KT6 — Bizonyíték-tűzfal implementáció (D8).** (a) A `run-tests.py` a `results.json`-be
      `"cycle": null`-t ír, ha a `--round-dir` a `test-runs/` alatt van; (b) a `dod-check.py`
      (`--round-dir`, `:157`) és a `report-gate-check.py` (`--report-subdir`, `:321`)
      **`exit 2`-vel megáll**, ha a kapott útvonal a `test-runs/` alatt van, a kimondott
      indoklással; (c) a `07-validate.md` és a `06-implement.md` egy sora kimondja ugyanezt
      prózában is.
- [x] **KT7 — `.gitignore`** — `test-runs/` felvétele (a mai tartalom: `history`,
      `__pycache__/`, `*.pyc`). ~~**A célprojekt `.gitignore`-ját a `00-init-project` írja**~~ —
      **ez a premissza téves volt: a `00` ma egyáltalán nem nyúl a `.gitignore`-hoz.**
      A sor a `BS4` (brainstorm) mintája szerint, **jóváhagyás-kötött felajánlásként** került
      a `00`-ba — lásd a 10.4 szakaszt.
- [x] **KT9 — Az új skill kötelező boilerplate-je** (ezt nulla kontextusból könnyű elhibázni):
      1. **Frontmatter** a `manual-test-plan.md:1`–`:13` mintája szerint: `name: bs-run-tests`,
         `description:` (a `descriptions.json` **nem** helyettesíti — a skill fájlban is kell),
         `prerequisites:` (a `conventions.md` `## <sec:cv_test_execution>` szekciója),
         `output:` (a `test-runs/…` futás-mappa és a `latest.json`), `scripts:`
         (`scripts/run-tests.py`), `shared:` (`shared/context-check.md`, `shared/python-cmd.md`
         — D13).
      2. **A törzs első két sora KÖTELEZŐ** (ellenőrizve: **16/16** mai skill így kezdődik):
         `<!-- INCLUDE:lang/output-language.md#output-language -->`, majd
         `<!-- INCLUDE:shared/context-check.md -->`.
      3. **A `lang/{hu,en}/run-tests.md` vezető jegyzete**: a többi lang-fájl fejkommentjét
         másold (mit tesz a telepítő, hogy az `ANCHOR` sorok nem részei a szövegnek, és a
         *„ebbe a vezető jegyzetbe ne kerüljön komment-lezáró szekvencia"* figyelmeztetés).
      4. **Sorszintű igazodás:** a hu és en példány címsorai ugyanazokon a sorokon álljanak
         (a `quick-flow` párnál ez ma 344/344) — így a paritás-kapu kimenete olvasható marad.
- [x] **KT8 — Segédparancs-kereszthivatkozások.** A `/bs-run-tests` bekerül: a `quick-flow.md`
      6. szekciójának segédparancs-táblájába (QF17), a `README-HU.md`/`README.md`
      segédparancs-táblájába, és a `meta-improve-prompts.md` segédparancs-listájába (7. szakasz).

---

## 6. Új nyelvi kulcsok (`prompts/lang/status-keys.json`)

- [x] **TK1 — Hat új kulcs, mindkét nyelven.** _(Végül **hét** kellett: a `LD6` kétirányú
      joinjához a `f_inventory_items` mező is — lásd a 10.2 szakaszt.)_ A meglévő kulcsokat **ne** duplikáld: ellenőrizve
      (2026-09-07), hogy a `<field:f_goal>` (`Cél`), `<field:f_steps>` (`Lépések`),
      `<field:f_expected_result>` (`Elvárt eredmény`), `<field:f_environment>` (`Környezet`),
      `<field:f_recipe>` (`Recept`), `<field:f_last_run>` (`Utolsó futás`),
      `<field:f_prerequisite>` (`Előfeltétel`), `<field:f_cleanup>` (`Takarítás`),
      `<field:f_target_env>` (`Cél-környezet`), `<status:scope_local>`,
      `<status:scope_shared_remote>` **mind létezik** — ezeket használd.

| csoport | kulcs | hu | en |
|---|---|---|---|
| `sections` | `test_inventory` | Teszt-leltár | Test inventory |
| `sections` | `cv_test_execution` | Teszt-futtatás | Test execution |
| `fields` | `f_run_command` | Futtató parancs | Run command |
| `fields` | `f_source_cycle` | Forrás-ciklus | Source cycle |
| `fields` | `f_test_categories` | Teszt-kategóriák | Test categories |
| `fields` | `f_inventory_items` | Leltár-tételek | Inventory items | _(**+1, a tervben nem volt** — 10.2)_
| `status` | `retired` | Kivezetve | Retired |

> **Ha a végrehajtás közben kiderül, hogy további kulcs kell, az a terv hibája → 10. szakasz.**
> A `lang-parity-check.py` a `status-keys.json` **kulcs-paritását** is méri
> (**11.5**, `check_status_keys()`, `:395`): egy csak az egyik nyelvi szeletben létező kulcs
> azonnali bukás — tehát mind a hat kulcs a `hu` ÉS az `en` szeletbe egyszerre kerül be.

---

## 7. Dokumentáció

> **🔴 A gyökér-dokumentumokat EGYETLEN gépi kapu sem méri — ellenőrizve.** A
> `lang-parity-check.py` hatóköre `BASES = ("skills", "agents", "shared")` + `lang`
> (`:116`–`:117`), tehát a `README-HU.md` ↔ `README.md` párt **nem látja**: az eltérésük
> csendben megmarad. Ezért a `7.1` és a `7.2` **ugyanazt az öt szerkesztést** kéri, és a
> 8. szakasz emberi review-tétele **külön** kitér rá. A gyökérben ma három dokumentum van
> (`README-HU.md`, `README.md`, `berki-spec-directory-structure.md`) — a `jegyzet.md`
> **privát munkaterület: ne olvasd, ne szerkeszd, ne commitold.**

- [x] **7.1 — `README-HU.md`** (a **tartalmat** keresd, ne a sorszámot — a szerkesztés közben
      csúszik):
      - a **„Dokumentumok" tábla**: új sor a `docs-generated/test-description.md`-re;
      - a **`docs-generated/` fájlkészletét** bemutató szakasz (a `08` leírásánál): a leltár
        mint hatodik fájl, a `TL-NNN` azonosítóval és a kemény kapuval;
      - a **segédparancs-tábla**: új sor a `bs-run-tests`-re (`/bs-cycle-status`,
        `/bs-manual-test-plan`, `/bs-export-doc`, `/bs-brainstorm`, `/bs-quick-flow` mellé);
      - egy **rövid szakasz a központi futtatásról**: mikor használd, hova ír, és hogy
        **nem ciklus-bizonyíték** (D8);
      - a `test-conventions.md` fogyasztóit felsoroló mondat: a leltár **nem** helyettesíti,
        a határvonal a D3 szerinti mező-szintű tulajdon.
- [x] **7.2 — `README.md` (az ANGOL pár) — ugyanaz az öt szerkesztés.** Nem rövidítve, nem
      összefoglalva: a két README **tartalmilag egyenértékű**. A helyek ugyanott vannak,
      néhány sorral eltolva (a `list10` mérése szerint az angol pár ~10-12 sorral előrébb
      tart). A `TL-NNN`, `test-runs/`, `local`/`remote` és a kategória-azonosítók **mindkét
      nyelven ugyanazok** (nyelvfüggetlen literálok, 1.2).
- [x] **7.3 — `prompts/meta-improve-prompts.md`.** (a) A **script-tábla** két új sora:
      `test-inventory-check.py` (ki futtatja: `08`, `doc-sync-planner`) és a `run-tests.py`
      sorának bővítése a `bs-run-tests` hívóval. (b) A **segédparancs-lista** új tétele:
      `bs-run-tests`. (c) A **fájl-tábla** új sora: `prompts/skills-hu/run-tests.md`.
      (d) **Új tervezési elv: `7/p` — „a bizonyíték ciklushoz kötött; a kényelmi futtatás nem
      bizonyíték"** — a D8 indoklásával és azzal a méréssel, amit a 2.1/(c) ad.
- [x] **7.4 — `prompts/lang/{hu,en}/descriptions.json`**: a `bs-run-tests` kulcs (kötelező —
      `install-helper.py:440`), a `bs-manual-test-plan` leírásának stílusában: mit tesz, mi a
      bemenete, és hogy **nem fázis**.
- [x] **7.5 — `berki-spec-directory-structure.md`**: a `docs-generated/test-description.md`, a
      `test-runs/` (gitignore-olt) és a `run-tests.md` skill felvétele — kinek a tulajdona
      melyik (a fájl épp ezt a kérdést válaszolja meg).
      _**Ennek nincs angol párja** (ellenőrizve: a gyökérben csak `berki-spec-directory-structure.md`
      van) — tehát itt nincs mit párosítani, ne keresd a `-EN` változatot, és ne is hozz létre
      újat: az nem ennek a körnek a hatóköre._
- [x] **7.6 — `prompts/lang/{hu,en}/08-doc-sync.md` és `…/run-tests.md`**: minden **user-facing
      mondat** és **artefaktum-sablon** (a `TL-NNN` adatlap, a `retired` jelölés szövege, a
      `latest.json` összegző mondata, a tűzfal-figyelmeztetés) **nem** a skillbe kerül, hanem új
      `ANCHOR` a lang-fájlba, **mindkét nyelven**, és a skillben INCLUDE marker hivatkozik rá
      (különben a `lang-parity-check` 11.3 árva-horgony vagy hiányzó-marker checkje bukik).

---

## 8. Kapuk (kézzel, commit előtt)

- [x] `python3 prompts/scripts/lang-parity-check.py` → 0
- [x] `python3 prompts/scripts/lang-parity-check.py --strict` → 0
- [x] `python3 prompts/scripts/sync-gemini-agents.py` **(írás mód — KÖTELEZŐ)**, mert az
      `LD11/2` módosítja a `doc-sync-planner` frontmatterét
- [x] `python3 prompts/scripts/sync-gemini-agents.py --check` → 0
- [x] **Build-füstteszt** (1.3): `install-helper.py claude . <tmp>/hu hu hu` és `… en en` →
      `Success`, és a telepített `bs-run-tests` + `bs-doc-sync` `SKILL.md`-jében **nulla**
      feloldatlan `INCLUDE:` marker és **nulla** `<sec:|<field:|<status:` token.
- [x] **`test-inventory-check.py` füst-teszt** próba-fixtúrán: (a) teljes leltár → `exit 0`;
      (b) felderített, de nem leltározott tesztfájl → `exit 1` a fájl nevével; (c) leltározott,
      de nem létező tesztfájl → `exit 1`; (d) egyoldalú `R-NN` hivatkozás → `exit 1`;
      (e) nem deklarált host → `exit 0` + WARN.
- [x] **`run-tests.py --dry-run` füst-teszt** a `conventions.md` futtatási táblájára
      (`--table-source conventions`), és a **régi** pozicionális `plan.md` hívásra is
      (visszafelé kompatibilitás, KT3).
- [x] **Tűzfal füst-teszt** (D8): `dod-check.py --round-dir test-runs/…` → `exit 2`;
      `report-gate-check.py … --report-subdir` `test-runs/` alatti értékkel → `exit 2`.
- [x] **Emberi review (nem gépi kapu) — két külön dolog:**
      1. **Prompt-fa:** a `lang-parity-check.py` a **szerkezeti** eltérést fogja meg, a
         **jelentés**-eltérést nem — az új `run-tests.md` hu/en párt és a `08` módosított
         szakaszait át kell olvasni.
      2. **Gyökér-README pár:** a `README-HU.md` ↔ `README.md` **egyáltalán nincs kapu alatt**
         (a `BASES` nem tartalmazza) — a `7.1`/`7.2` öt szerkesztését **tételesen** vesd össze
         a két fájlban.

---

## 9. Végrehajtási sorrend

1. **6. szakasz (TK1)** — a hat nyelvi kulcs. Ez **minden** további szerkesztés előfeltétele:
   token nélkül a promptba írt mezőnév literál lenne, amit a paritás-kapu megfog.
2. **5. szakasz / KT1–KT2** — a `conventions.md` szekció-sablonja és a `00` bekérdezése, plusz a
   kategória-részhalmaz kapu. Ez adja a **felderítés bemenetét** a leltárnak (LD5), ezért előbb kell.
3. **4. szakasz (LD1–LD8, LD11)** — a leltár szerkezete, adatlapja, a `08` lépései, a kemény
   kapu, és a két frontmatter (`08` `output:` + `doc-sync-planner`).
4. **4. szakasz (LD9–LD10)** — a fogyasztók (`03b`, `manual-test-plan`, `02`) és a quick-flow
   drift-jelzés. Külön lépés, mert **négy másik skillt** módosít.
5. **5. szakasz / KT3–KT9** — a script-általánosítás, az új segédparancs (a `KT9`
   boilerplate-jével), a mappa-séma, a tűzfal, a `.gitignore` és a kereszthivatkozások.
6. **7. szakasz** — dokumentáció (README ×2, meta-prompt, descriptions, directory-structure,
   lang-blokkok).
7. **8. szakasz** — kapuk, majd egy commit. A commit-üzenetben **külön jelöld**, hogy ez a kör
   **új artefaktumot és új kapu-scriptet** vezet be (nem csak prompt-szöveget módosít), mert a
   paritás-kapu ezt nem látja.

---

## 10. A végrehajtás tapasztalatai és a tervtől való eltérések

_Kitöltve a végrehajtás során (2026-09-07). A `D1`–`D13` döntéseket nem írtuk felül;
az alábbi pontok azok, ahol a **teendő-szintű leírás** tévedett vagy hiányos volt._

### 10.1 A `KT1` oszlop-listája ellentmondott a `D10`-nek — a `D10` nyert

**Amit a terv írt.** A `KT1` a `conventions.md` futtatási táblájának oszlopait így sorolta:
`| Kategória | <field:f_environment> | Parancs | Időkorlát | Riport-artefaktum |` (öt oszlop).

**Miért tarthatatlan.** A `D10` — a felhasználóval **lezárt** döntés — azt mondja ki, hogy a
tábla oszlop-sémája **azonos** a plan gépi tábláját (TP4/b), *„egy parser, egy szabály
(`7/m`)"*. A TP4/b séma viszont **kilenc** oszlop, és a `run-tests.py` `parse_matrix()`
**fix oszlop-pozíciókkal** olvas (`cells[0]`…`cells[8]`). A `KT1` öt oszlopa így minden
cellát rossz mezőbe tett volna: a `Parancs` a `elofeltetel` mezőbe, az `Időkorlát` a
`parancs` mezőbe — azaz a szkript az „Időkorlát" szót próbálta volna shell-parancsként
lefuttatni. Ez **pontosan a `TP4/b` hibamódja**, ami miatt a `7/m` szerint a parsert
szándékosan nem tettük „okossá".

**Amit helyette tettünk.** A `D10` nyer: a `## <sec:cv_test_execution>` szekció táblája a
**teljes kilenc oszlopos TP4/b séma**
(`Kategória | Típus | Előfeltétel | Parancs | Eredményfájl | Formátum | Takarítás |
<field:f_environment> | <field:f_phase>`). A `Fázis` oszlop cikluson kívül `—` (ami a
`run-tests.py`-ban „mindkettő", tehát a fázis-szűrés nem tünteti el a sort), a `Típus`
értékei pedig a szkript nyelvfüggetlen CLI-értékei (`gyors` / `nehez`) — **mindkét
prompt-nyelven ugyanazok**, ahogy a `03b` táblája is előírja. A `KT1` „Időkorlát" és
„Riport-artefaktum" oszlopa így **nem létezik**: az időkorlátot a `--timeout` adja, a
riport-artefaktumot pedig az `Eredményfájl` oszlop.

**Tanulság a következő körre.** Ha egy terv egyszerre mond ki egy **elvet** („azonos
oszlop-séma") és sorol fel egy **konkrét listát**, a kettőt a terv írásakor össze kell
vetni — itt a lista egy korábbi vázlatból maradt benne, és csendben ellentmondott a
lezárt döntésnek.

### 10.2 Egy hetedik nyelvi kulcs kellett (`f_inventory_items`) — a `TK1` hiánya

**Amit a terv írt.** A `TK1` **hat** új kulcsot sorolt fel, és kimondta: *„Ha a végrehajtás
közben kiderül, hogy további kulcs kell, az a terv hibája → 10. szakasz."*

**Mi hiányzott.** Az `LD6` **kétirányú** joinhoz a `test-conventions.md` recept-adatlapján
egy **visszamutató mező** kell (`R-NN` → `TL-NNN`). A terv az irányt kimondta („a `R-NN`
adatlapja visszamutat a `TL-NNN`-re"), a hozzá tartozó **mezőnevet** viszont nem — és
mezőnév nélkül a prompt csak literált tudott volna írni, amit a paritás-kapu megfog.

**Amit tettünk.** Új `fields` kulcs: `f_inventory_items` — hu `Leltár-tételek`, en
`Inventory items`. Bekerült a `TC2-test-conventions-vaz` recept-sablonjába és a `08`
skill `R03` kész példájába is. A `status-keys.json` így **hét** kulccsal bővült, nem
hattal (`sections`: 100, `fields`: 70, `status`: 38).

### 10.3 A `test-inventory-check.py` egy negyedik CLI-flaget kapott

**Amit a terv írt.** A `LD5` CLI-szerződése három argumentumot adott meg: a pozicionális
leltár-útvonalat, a `--project-root`-ot és a `--conventions`-t.

**Mi hiányzott.** A **6. check** (kétirányú `R-NN` join) a `specs/test-conventions.md`-t is
olvassa — annak útvonalát viszont a szerződés nem adta meg. Ezért a script kapott egy
`--test-conventions` flaget `specs/test-conventions.md` alapértékkel. A dokumentált három
argumentum **változatlanul működik** (a flag opcionális, sane default-tal), tehát ez
bővítés, nem átírás — ugyanaz a megközelítés, amit a `KT3` a `run-tests.py`-nál választott.
Ha a fájl nem létezik (TC6: korai ciklusban ez nem hiba), a 6. check **WARN**-nal kimarad.

**Két további, a terv által nem részletezett viselkedés-döntés a kapuban:**

1. **A `<field:f_recipe>` mezőnél a `—` LEGITIM érték, nem hiány.** A `LD2` ezt kimondja
   (*„`R-NN` hivatkozás vagy »—«"*), a 3. check „kötelező mezők" listája viszont naivan
   üresként kezelte volna. A kapu ezért mezőnként háromféle jelenlét-szabályt használ:
   a `<field:f_steps>`-nél a **számozott lépés-lista** a tartalom (az inline érték jogosan
   üres), a `<field:f_recipe>`-nél a mező **léte** elég, minden más mezőnél nem lehet üres
   és nem lehet `—`.
2. **A nem létező leltár csak akkor FAIL, ha a `docs-generated/` mappa létezik.** A terv
   `LD8/b`-je kimondta, hogy a bootstrap független a `system-overview.md` ágától, de nem
   mondta meg, mit tegyen a kapu egy olyan projektben, ahol a `docs-generated/` **még
   egyáltalán nincs**. Ott a script `0`-val, „kihagyva" jelzéssel tér vissza (a `tc8`
   mintájára); ha viszont a mappa létezik és csak a leltár nincs meg, az **FAIL**.

### 10.4 A `KT7` premisszája téves volt: a `00-init-project` nem ír `.gitignore`-t

**Amit a terv írt.** *„A célprojekt `.gitignore`-ját a `00-init-project` írja — ezért a `00`
skillbe is bekerül a sor."*

**Mi a valóság.** A `00-init-project` **egyáltalán nem nyúl** a `.gitignore`-hoz; a
keretben ezt a mintát a `bs-brainstorm` (`BS4`) és a `bs-export-doc` használja:
**jóváhagyás-kötött, egyszeri felajánlás**, és ha a felhasználó nemet mond, a skill
**soha többé nem kérdezi újra**.

**Amit tettünk.** A `test-runs/` bejegyzés a `00`-ba került, de a `BS4` mintája szerint:
`grep -qxF` létezés-ellenőrzés → felajánlás (`KT7-gitignore-felajanlas` horgony, hu+en) →
írás **csak jóváhagyás után**, pontosan egy sor. A `/bs-run-tests` ezért **nem kérdez**
újra (az kettős kérdés lenne, és megsértené a „ha nemet mond, ne kérdezd újra" szabályt):
csak **egy sorban jelzi**, ha a bejegyzés hiányzik. A repó saját `.gitignore`-ja is
megkapta a `test-runs/` sort.

### 10.5 Amit a terv helyesen mért fel (nem kellett eltérni)

Ezeket a végrehajtás **megerősítette** — érdemes rögzíteni, mert egy következő kör
ugyanezeket a kérdéseket fogja feltenni:

- **A `KT3` visszafelé kompatibilitása elég volt.** A `plan_file` `nargs="?"`-ra váltása +
  a `--table-source plan|conventions` mellett a **31 meglévő hivatkozási hely és mind a
  három tényleges bash-hívás** (`06-implement` ×1, `07-validate` ×2) **változatlan** —
  egyetlen call site-ot sem kellett szerkeszteni, és a `results.json`-t olvasó öt script
  (`dod-check`, `report-gate-check`, `round-log`, `validate-gate-check`,
  `failure-counter`) sem, mert a két új kulcs (`cycle`, `table_source`) **additív**.
- **A `parse_matrix()` törzse valóban változatlan maradt** — csak egy opcionális
  `section` paramétert kapott (`7/m` betartva).
- **A `normalize_round_dir()` viszont NEM volt „szövegre dolgozó".** A terv a parsert
  említette, de a normalizálót nem: az `cycle / "test-report" / phase_dir`-t épített,
  tehát a `test-runs/…` értéket **`<ciklus>/test-report/test-runs/…`-ra mangolta volna**.
  Ezért kapott egy `CENTRAL_RUN_ROOT` ágat, amely a `test-runs/` alatti útvonalat szó
  szerint veszi át, és a `cycle=None` esetet is kezeli. _(Ez a `7/e` „egy fogalom, egy
  útvonal-alak" elv gyakorlati csapdája: a `D9` helyesen mondta, hogy nincs negyedik
  bázis, de a meglévő normalizáló implicit feltételezte, hogy MINDIG van ciklus.)_
- **A telepítő tényleg nem igényelt módosítást** (glob-alapú skill-felderítés,
  glob-alapú script-másolás) — mind az **öt platform** (claude, codex, antigravity,
  cursor, copilot) `Success`-szel épült, és a `bs-run-tests` + a
  `test-inventory-check.py` mindegyikben megjelent.
- **A `ds22-gate-check.py` valóban nem igényelt módosítást** a `DS21` mappa-indexhez
  (`check_folder_index()` a mappa tényleges `.md` listáját olvassa).
- **A `manual-test-gate-check.py` `TG-NN` fejléc-parsere elbírja a `TL-NNN` kiterjesztést**
  (`DOD_RE.findall` a fejléc maradékán fut, a `TG_TOKEN_RE` pedig csak a lefedettségi
  táblán) — az `LD9` szerinti
  `### TG-03 — <név>  (DoD-02, DoD-05 · TL-014, TL-018)` alak nem törte el a kaput.

### 10.6 Amit ez a kör NEM oldott meg (tudatosan)

- **A `KT5` `<TL-NNN>/` alkönyvtár-elhelyezése prompt-szintű, nem script-szintű.** A
  `run-tests.py` a riport-artefaktumot a kör-mappa gyökerébe másolja; a tételenkénti
  szétosztást a `/bs-run-tests` skill végzi a futás után. Egy következő kör
  determinisztikussá teheti (a `TL-NNN` ↔ tesztfájl join a leltárból gépiesen olvasható),
  de ehhez a `run-tests.py`-nak ismernie kellene a leltárat — az pedig új bemenet-kötés
  egy eddig leltár-független szkriptben.
- **A `test-runs/latest.json` írása is prompt-szintű.** A szkript a `results.json`-t írja;
  a `latest.json` aggregálása a skill dolga. Indok ugyanaz: a `run-tests.py` nem tudja,
  hogy központi futásról van-e szó **azon túl**, amit a `--round-dir`-ből kiolvas, és a
  `latest.json` séma projekt-szintű aggregátum, nem futás-eredmény.
- **A `16.6` éles próba** (a `prompts/inprove-list10.md` és a kétnyelvűsítési terv nyitott
  tétele) továbbra is nyitott — ez a kör nem érintette.
