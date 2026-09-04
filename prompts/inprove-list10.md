# „A quick-flow ne csússzon el a nagy flow-tól" — végrehajtási terv

> **Ez a dokumentum önhordó.** Üres kontextusban, `/clear` után is végrehajtható: az 1. szakasz
> megadja a repó-orientációt, a 2. a problémát és a mérést, a 3. a lezárt döntéseket, a 4–9. a
> tételes teendőket, a 10. a dokumentációt, a 11. a kapukat, a 12. a végrehajtási sorrendet.
> **Semmit nem kell kikövetkeztetni** — ha valami mégis hiányzik, az a terv hibája; írd bele.
>
> **Státusz:** **KÉSZ** (2026-09-04) — a 4–11. szakasz végrehajtva, a kapuk zöldek.
> A `10.7` szándékosan nyitva maradt (hatókörön kívül; a felhasználó nem kérte).
> **Előzmény:** a `prompts/inprove-list9.md` (`EV8`–`EV10` · `RL1` · `RL2`) **elkészült**
> (`be7e868`). Ez a terv nem a nagy flow-t keményíti tovább, hanem a **másik utat** hozza vissza
> a nagy flow mellé: a `quick-flow` utolsó tartalmi köre a `7/f`–`7/n` keményítések, a `03a`/`03b`
> hasítás és a közös shared-blokkok (RP1, GC1, AV1, phase-commit) **előtt** volt — az azóta
> bevezetett minden tanulság kimaradt belőle.

---

## 0. Hogyan használd ezt a dokumentumot

1. **Olvasd el az 1–2. szakaszt.** Az 1. mondja meg, milyen repóban dolgozol és milyen kézi
   kapuk kötelezők; a 2. adja az indoklást, ami nélkül a tételek önkényesnek tűnnek.
2. **A 3. szakasz döntéseit ne nyisd újra.** Mind a négy fő döntés a felhasználóval **lezárva**
   (2026-09-04). Ha valamelyik a végrehajtás közben tarthatatlannak bizonyul, **írd a 13.
   szakaszba, mi lett helyette és miért** — ne csendben térj el tőle.
3. **A 12. szakasz sorrendjében haladj**, és minden teendő után **pipálj ebben a fájlban**
   (`- [ ]` → `- [x]`).
4. **Kétnyelvű repó:** minden prompt-szerkesztés **hu ÉS en párban** megy (1.2). A
   `prompts/skills-hu/quick-flow.md` és a `prompts/skills-en/quick-flow.md` ma **sorszinten
   igazodik** (mindkettő 210 sor, a címsorok ugyanazokon a sorokon) — ezt a szerkesztés után is
   tartsd meg, hogy a paritás-kapu olvasható maradjon.
5. **Nincs CI és nincs pre-commit hook** — a kapukat (11. szakasz) **kézzel futtasd le**, commit előtt.

---

## 1. Orientáció — mi ez a repó, és mi mozdul

### 1.1 A rendszer

A `berkispec` egy **spec-driven development keretrendszer promptokból**: fázis-skillek (`00`–`09`),
segédparancsok (`brainstorm`, `manual-test-plan`, `cycle-status`, `export-doc`, `quick-flow`),
subagent-promptok és determinisztikus **kapu-scriptek**. A repó a **forrás**; egy célprojektbe az
`install.sh` / `install.ps1` → `prompts/scripts/install-helper.py` telepíti (öt platform: claude,
codex, antigravity, cursor, copilot). A telepítő **build-time** oldja fel az
`<!-- INCLUDE:shared/… -->` / `<!-- INCLUDE:lang/… -->` markereket és a
`<sec:…>` / `<field:…>` / `<status:…>` tokeneket, és a skillt `bs-<stem>/SKILL.md` alá írja
(`install-helper.py:742`).

**Két fejlesztési út él egymás mellett:** a **teljes flow** (`00`–`09`, `spec.md` + `plan.md` +
`tasks.md`, determinisztikus kapuk, önjavító hurkok) és az **egyszerűsített flow**
(`/bs-quick-flow`: háromfázisú `spec.md` → task lista → implementáció, kapu- és hurok-mentes,
kis feladatokhoz). Ez a terv **csak az egyszerűsítettet** módosítja — a nagy flow gépezetéhez
nem nyúl.

Amit ez a terv érint:

| útvonal | mi ez |
|---|---|
| `prompts/skills-{hu,en}/quick-flow.md` | az egyszerűsített flow skillje — a terv fő célpontja (210 sor) |
| `prompts/lang/{hu,en}/quick-flow.md` | a quick-flow projekt-nyelvi blokkjai (ma **egy** horgony) |
| `prompts/lang/{hu,en}/descriptions.json` | a `bs-quick-flow` telepített leírása (ma `task.md`-t ír) |
| `prompts/agents-{hu,en}/{researcher,analyzer,reviewer}.md` | a három opcionális ágens `called_by` listája |
| `prompts/skills-{hu,en}/manual-test-plan.md` | az MT1 kapu — quick-flow ágat kap |
| `prompts/scripts/cycle-status.py` | a ciklus-státusz script lightweight ága (visszafelé-kompatibilitás) |
| `README-HU.md` · `README.md` | az „5. Egyszerűsített flow" szekció (5.1–5.6) és a hivatkozó mondatok |
| `prompts/meta-improve-prompts.md` | a meta-prompt fájl-táblája (ma nem is sorolja a quick-flow-t) |

### 1.2 A két nyelvi tengely (LG2/LG5)

- **prompt-nyelv:** a `prompts/skills-hu/` vs. `prompts/skills-en/` fa (az ágens *instrukcióinak*
  nyelve). **Minden szerkesztés mindkét fán megy, párban.**
- **projekt-nyelv:** amit az ágens a célprojektbe *ír* — ezt a `prompts/lang/{hu,en}/` blokkok és a
  `status-keys.json` tokenjei adják. Artefaktum-szekciónév, mezőnév és státusz-érték a promptban
  **nem literál**, hanem `<sec:…>` / `<field:…>` / `<status:…>` token.
- **Ez a terv NEM bővíti a `status-keys.json`-t:** a QF2 státuszaihoz a **meglévő** kulcsok
  elegendők (`draft`, `ready_for_tasks`, `ready_for_implement`, `done` — lásd D2).
- **A terv MINDEN tokenje létezik — ellenőrizve (2026-09-04).** `f_target_env` (Cél-környezet),
  `f_main_branch` (Fő branch), `f_branch_naming` (Branch-elnevezési stratégia), `f_status`
  (Státusz), `sec:cv_git_conventions` (Git és branching konvenciók), `status:draft` / `ready_for_tasks`
  / `ready_for_implement` / `done` / `must_fix` / `suggestion` — mind benne van a
  `status-keys.json` `hu` és `en` szeletében. **Új kulcsot ne vezess be**; ha mégis kellene,
  az a terv hibája → 13. szakasz.
- **A telepítő nem igényel módosítást a 6. szakasz INCLUDE-jaihoz — ellenőrizve.** Az
  `install-helper.py` a `shared/` markereket **általános regexszel** oldja fel bármelyik
  skillben (`:258`–`:288`, rekurzívan `_MAX_INCLUDE_DEPTH = 5` mélységig); nincs per-skill
  allowlist, tehát a `quick-flow.md`-be tett új marker **magától** feloldódik. A token-feloldás
  az INCLUDE **után** fut, tehát a beemelt blokkok tokenjei is feloldódnak.
- **Nyelvfüggetlen literál kivétel:** a `[local]` / `[remote]` címke (QT2) — ugyanazon az indokon,
  amiért az `EV8` is nyelvfüggetlen (útvonalra és kapura joinol; lásd `7/n`).

### 1.3 Kötelező kézi kapuk (nincs CI, nincs pre-commit hook)

```bash
python3 prompts/scripts/lang-parity-check.py            # szerkezeti paritás  → 0
python3 prompts/scripts/lang-parity-check.py --strict   # fájlhalmaz-paritás  → 0
python3 prompts/scripts/sync-gemini-agents.py --check   # agent.json tükrök   → 0
```
Mivel ez a terv **agent-promptot is** módosít (9. szakasz), a `sync-gemini-agents.py`-t előbb
**írás módban** kell lefuttatni: `python3 prompts/scripts/sync-gemini-agents.py`.

### 1.4 A hivatkozott azonosítók — hol nézd meg őket

Ez a terv sok meglévő azonosítót említ (`RP1`, `GC1`, `AV1`, `KX2`, `IM1`, `BQ2`, `PE1`, `MT1`,
`TC1`, `EV1`–`EV5`, `EV8`, `TD7`, `TB1`, `SK1`, `CK1`, `TX1`, `7/f`–`7/n`). **Nem kell fejből
tudnod őket:**

| hol | mit ad |
|---|---|
| `prompts/meta-improve-prompts.md` „Tervezési elvek" (7/b–7/n) | minden keményítő kör indoklása és azonosítói |
| `README-HU.md` | a felhasználónak szánt leírás, flow-ábrák, a hurkok konvenciói |
| `prompts/inprove-list{7,8,9}.md` | a legutóbbi három kör tételes terve (`EV`, `RUN1`, `SK1`, `RL`) |

---

## 2. A probléma és a mérés

### 2.1 A mérés: mikor csúszott el

A `quick-flow.md` utolsó **tartalmi** módosítása a 2026-08-25-i tokenizálás (`83397e9`) előtti kör.
Azóta a nagy flow négy teszt-keményítő kört (`7/f`–`7/n`), egy fázishasítást (`03a`/`03b`) és öt
közös shared-blokkot kapott — a quick-flow **egyikből sem**. Az elcsúszás nem véletlen: a
`quick-flow` egyetlen `inprove-list` hatókörében sem szerepelt (a `list6` kifejezetten
*„A `bs-quick-flow` változatlan"*-t rögzített), és a `meta-improve-prompts.md` fájl-táblája
**ma sem sorolja** — vagyis a következő felülvizsgálat is átlépne rajta (10.3).

### 2.2 A bizonyíték: három mérhető törés

**(a) A `bs-cycle-status` minden quick-flow ciklusra hibás állapotot mutat.** A
`cycle-status.py` lightweight ága (`:357`) `tasks.md`-t keres (`:201`), és **státusz-mezőt** olvas
a `spec.md`/`tasks.md`-ből (`get_status_from_file`, `:89` — `Státusz:` sor nélkül `None`). A
quick-flow viszont `task.md`-t (egyes szám) ír, és **egyik artefaktumába sem tesz státuszt**.
Eredmény minden quick-flow ciklusra: `Specifikáció: MÉG NEM FUTOTT` + `Feladatlista: MÉG NEM
FUTOTT`, holott a ciklus akár kész is lehet. Ez nem kozmetika: a jóváhagyás ténye **sehol nem
perzisztens**, tehát `/clear` vagy megszakadás után az ágens nem tudja, jóvá volt-e hagyva a spec.

**(b) A skill három szekciója tényszerűen elavult.** A „Telepítés és aktiválás" szekció
`sdd-skill` nevet, `.claude/skills/sdd-skill/SKILL.md` útvonalat és `/sdd-skill` parancsot ír, plusz
szimlinkes szinkront javasol (a szimlink-alapú `init-project.sh` LG19 szerint elavult); a
`/goal` parancs nem létezik a keretben; a git-szekció `master` ágat, `feature/<jira>-<summary>`
nevet és Jira-prefixes commitot **drótoz be**, miközben a nagy flow mindezt a `conventions.md`
`<sec:cv_git_conventions>`-jéből olvassa (`f_main_branch` alapból `main`, `f_branch_naming`
alapból `feature/cycle-NN-<name>`, No-VCS flag). Egy telepített projektben ma a két flow **más
ágnévvel és más commit-formátummal** dolgozik.

**(c) A három opcionális ágens kontraktusa elcsúszott.** A `reviewer` ma
`called_by: ["skills/07-validate.md"]`, kötelező bemenete a `plan.md`, és a kimenete **fájl**:
`specs/cycle-NN-<name>/test-report/code-review.md` (RV-INC inkrementális váz, `MF-NN`
azonosítók). A quick-flow azt írja, hogy „listát ad vissza" — a subagent viszont fájlt ír egy nem
létező mappába, `plan.md` nélkül. Az `analyzer` elsődleges bemenete a kapu `--emit-slices`
szelete, a dokumentum-bemenetei `plan.md` + `tasks.md`; a `researcher` `called_by` listája pedig
**nem is tartalmazza** a quick-flow-t, holott hívja.

### 2.3 A tartalmi rés: a tesztstratégia szabad próza

A quick-flow tesztstratégiája ma **szabad próza** — pontosan az az állapot, amiről a nagy flow
négy kör alatt megtanulta, hogy egy mondatos, önigazoló teszteket termel. Két konkrétum:

- A flow-nak **van egy egész szekciója** valós, megosztott környezetről (OpenShift namespace, pod,
  secret) — közben nincs kötelező cél-környezet mező, nincs „a cél-host literálisan a parancsban",
  és nincs `localhost`-tilalom. A `7/g` (`EV1`–`EV5`) szó szerint ezt a hibát írja le, és ez a
  flow (konfiguráció, üzemeltetés, script) van neki a legjobban kitéve.
- A 3. fázis ma azt kéri, hogy bukás után *„futtasd újra az ÖSSZES tesztet"* — a nagy flow-ban épp
  ez a **gyűjtő futás tilos** (`CK1`/`TX1`), mert mögüle sem a lefutás, sem a bukás nem
  azonosítható. A két flow itt **egymással ellentétes** utasítást ad.

### 2.4 A flow-határ rései

- **Ciklusszám-ütközés:** a quick-flow csak `ls specs/`-et néz, a `01` viszont a **BQ2** formulát
  (`main` roadmap + `ls specs/` + a feature branch-ek `cycle-NN` számainak maximuma + 1). Egy nem
  merge-elt ágon élő ciklus számával a quick-flow **ütközhet**.
- **Roadmap:** a quick-flow ciklusa soha nem jelenik meg a `specs/roadmap.md`-ben → a projekt
  ciklustörténete hiányos, és a BQ2 sem lát rá.
- **`docs-generated/` drift:** a `02-write-spec` a `system-overview.md`-t **current truth**-ként
  olvassa be. Egy quick-flow ciklus viselkedést változtat, de a `docs-generated/`-hez nem nyúl
  (nincs `08`) → a következő nagy ciklus `02`-je **elavult igazságból** indul.
- **`bs-manual-test-plan` elérhetetlen:** az MT1 kapu `analyze-report.md` = `PASS`-t követel
  (`manual-test-plan.md:60`), ami a quick-flow-ban soha nem létezik — pedig a kézi tesztterv épp
  itt (konfiguráció, üzemeltetés) a leghasznosabb.
- **Brainstorm-átvétel:** a `brainstorm` átad a `/bs-quick-flow input: …`-nak
  (`brainstorm.md:173`), de a quick-flow nem írja le, hogyan vesz át egy desztillátumot.

---

## 3. Lezárt döntések (a felhasználóval egyeztetve, 2026-09-04 — ne nyisd újra)

- **D1 — Átnevezés + státusz-mező.** A quick-flow második artefaktuma `task.md` → **`tasks.md`**,
  és **mindkét** artefaktum (`spec.md`, `tasks.md`) kap `<field:f_status>` mezőt. Indok: így a
  `cycle-status.py` lightweight ága **változtatás nélkül** működik, az RP1 `--paths-only` kapu is
  ránéz a `tasks.md`-re (a `task.md` ma láthatatlan neki), és teljesül az 5. tervezési elv
  (státuszkezelés), amiből a quick-flow ma kimarad. **Ár:** a meglévő quick-flow ciklusok régi
  neve — ezért a `cycle-status.py` **visszafelé-kompatibilis ágat** kap (QF3).
- **D2 — Nem bővítjük a `status-keys.json`-t.** A meglévő kulcsok pontosan illeszkednek:
  `spec.md`: `<status:draft>` → jóváhagyáskor `<status:ready_for_tasks>`;
  `tasks.md`: `<status:draft>` → jóváhagyáskor `<status:ready_for_implement>` → a ciklus
  lezárásakor `<status:done>`. A `cycle-status.py` a `tasks.md` `done` státuszából mondja a
  „Megvalósítás: KÉSZ"-t (`:380`), tehát a lánc gépiesen zárul.
- **D3 — Teszt-keményítés: közepes csomag.** Átkerül: `EV1`/`EV3`/`EV5` (cél-környezet, literál
  host, localhost-tilalom), `EV8` (`[local]`/`[remote]` címke), `TD7` („mit ellenőriz és miért"),
  `TB1` (vacuous teszt), `SK1` (`skipped` ≠ bizonyíték), `CK1`/`TX1` (egy futtatás = egy
  azonosítható teszt). **NEM kerül át** a `shared/test-scenario-design.md` (TD0–TD7, 96 sor)
  teljes beemelése: a quick-flow „olcsó" jellege a lényege. Kapu-script **egyik tételhez sem**
  készül — ha egy valódi quick-flow ciklus megmutatja, hogy a próza nem elég, akkor fizetünk
  kapu-fogat (ugyanaz a mérték, mint a `TD6`-nál).
- **D4 — Agent-kontraktus: a quick-flow ad helyettesítéseket.** A három agent-prompt **törzse
  változatlan**; a quick-flow adja meg tételesen, mi kerül a hiányzó bemenetek helyére és hova
  íródik a kimenet. Az agent-fájlokból csak a **`called_by` lista** bővül a quick-flow-val.
  Indok: a nagy flow promptjait nem hígítjuk, és nem kell hozzájuk tartalmi paritás-kör.
- **D5 — A flow-határ mind a négy rése bekerül** (8. szakasz): BQ2 ciklusszám, roadmap-bejegyzés,
  `docs-generated/` drift-jelzés, `manual-test-plan` quick-flow ág.
- **D6 — A determinisztikus gépezet marad a nagy flow-ban.** A `analyze-gate-check.py`,
  `run-tests.py`, `dod-check.py`, `report-gate-check.py`, a gépi futtatási tábla, a
  `DoD-NN → [P-…] → task → TS-NN` azonosító-lánc, az önjavító hurkok, a Sonar és a doc-sync
  **nem** kerül át. Ez adja a két út közti különbséget; ha ezek kellenek, az a túlnövés jelzése,
  és a skill ma is helyesen mondja ezt. **Egy kivétel:** az RP1 kapu (`--paths-only`) hívása,
  amit a D1 átnevezés ingyen elérhetővé tesz (QF11).
- **D7 — A Jira-prefixes commit-konvenció megmarad**, de nem bedrótozva: a `conventions.md`
  git-szekciójából olvasott konvenció **egyik eseteként**. Ha a projekt nem Jira-t használ, a
  quick-flow a `conventions.md`-t követi (QF1).
- **D8 — Új azonosító-prefixek.** A quick-flow-specifikus szabályok `QF-` (folyamat) és `QT-`
  (teszt) prefixet kapnak, hogy a nagy flow azonosítóival ne ütközzenek és hivatkozhatók legyenek.

---

## 4. Elavult tartalom kivezetése (nincs döntés — azonnal végrehajtható)

Mindegyik tétel **hu + en párban** megy, és a két fájl sorszintű igazodását megtartva.

- [x] **QF-A1 — A „Telepítés és aktiválás (skillként)" szekció törlése** (`quick-flow.md` 51–62.
      sor — a szekció-címtől a `## 1. Alapelvek` előtti `---`-ig). Elavult a név (`sdd-skill` → `bs-quick-flow`), az útvonal (`bs-<stem>/SKILL.md`), a
      parancs (`/sdd-skill` → `/bs-quick-flow`) és a szimlink-javaslat (LG19). **Egyetlen más
      skill sem tartalmaz telepítési szekciót** — a telepítés a `README`-k és az `install.sh`
      dolga, nem a skillé. A szekciót pótlás nélkül töröld.
- [x] **QF-A2 — A `/goal` mondat törlése** (78. sor: *„Hosszabb vagy összetettebb ciklusoknál a
      Felhasználó a `/goal` paranccsal…"*). Ilyen parancs a keretben nem létezik (a repóban csak
      a quick-flow két nyelvi példánya említi).
- [x] **QF-A3 — Halott linkek javítása.** `[01-add-cycles](01-add-cycles.md)` (24. sor) → a
      telepített layoutban nem létezik → **parancs-hivatkozás**: `/bs-add-cycles`.
      `[README.md](../README.md)` (két markdown-link: **69.** és **130.** sor) → a
      telepített skillből `.claude/skills/README.md`-re mutat → **gyökér-relatív** `README.md`
      (RP1 kód-hivatkozás alak).
- [x] **QF-A4 — Helyőrző egységesítése.** `cycle-XX-<név>` → **`cycle-NN-<cycle-name>`** minden
      előfordulásban (a README quick-flow ábrája már `cycle-NN`-t ír).
- [x] **QF-A5 — „Task tool subagent-ként" → eszközfüggetlen megfogalmazás** (110. sor). Öt
      platformra telepítünk; a megfogalmazás legyen az, amit a `05-analyze` is használ, vagy
      egyszerűen *„indítsd el a `researcher` subagentet (read-only)"*.

---

## 5. Státusz-mező és átnevezés (D1 · D2)

- [x] **QF1 — A `conventions.md` git-szekciójának olvasása.** A 2. szakasz („Új fejlesztési ciklus
      indítása") 1. pontja ma `master`-t, `feature/<jira>-<summary>`-t és Jira-prefixes commitot
      drótoz be. Helyette: olvasd a `conventions.md` `## <sec:cv_git_conventions>` szekcióját, és
      onnan vedd a **No-VCS flaget** (ha ott az áll, minden git-művelet kimarad), a
      **<field:f_main_branch>** mezőt (alapból `main`) és a **<field:f_branch_naming>** mezőt.
      A Jira-prefix a commit-üzenetben **a konvenció egyik eseteként** marad (D7): ha a
      `conventions.md` mást ír elő, az nyer. **A `git-preflight.md` blokkot NE emeld be** — az a
      branch-nyitó `00`/`01` teljes preflightja (worktree-ág, PW1–PW5), ide túlméretezett; a
      quick-flow saját, rövid munkafa-ellenőrzése elég, csak a **forrása** legyen a
      `conventions.md`.

> **A 4–9. szakasz tételei a szabály SZÁNDÉKÁT és a mérést adják meg, a végleges prózát a
> végrehajtó írja.** Hogy ne kelljen formátumot kitalálni, minden új szerkezethez van
> **másolható minta a repóban**: a státusz-fejléc és a fázis-záró lépéssor →
> `prompts/skills-{hu,en}/02-write-spec.md`; a `<field:f_target_env>` mező és a
> `<field:f_environment>` használata → `03b-write-test-plan.md`; a „mit ellenőriz és miért"
> mondat és a **kalibrációs minta** műfaja → `03b-write-test-plan.md` `TS-NN` blokkja és `TA1`
> adatlapja; a `[local]`/`[remote]` címke alakja → ugyanott az `EV8`. **A mintát a sűrűségéért
> másold, ne a témájáért** (`TD5`).

- [x] **QF2 — Státusz-mező mindkét artefaktumban.** A `spec.md` és a `tasks.md` fejléce kap egy
      `**<field:f_status>:**` sort, a D2 szerinti értékekkel:
      `spec.md`: `<status:draft>` → a felhasználói jóváhagyás pillanatában `<status:ready_for_tasks>`;
      `tasks.md`: `<status:draft>` → jóváhagyáskor `<status:ready_for_implement>` → a ciklus
      lezárásakor `<status:done>`.
      A státuszírás és a commit **egyetlen, megszakíthatatlan lépéspár** (a `phase-commit.md`
      mintája szerint, lásd QF12).
- [x] **QF3 — `task.md` → `tasks.md` átnevezés.** Minden előfordulás a skillben, a
      `lang/{hu,en}/descriptions.json` `bs-quick-flow` leírásában (ma szó szerint
      *„spec.md → task.md"*), a README-kben (10.1/10.2) és a
      `berki-spec-directory-structure.md`-ben (10.6).
      **🔴 NE globális cserével dolgozz — három csapda van a repóban:**
      1. **`analyze/analyze-task.md`** — a **nagy flow** artefaktuma (a `05` TR1-triázsában
         jóváhagyott javítási lista). Előfordul a `lang/en/05-analyze.md`-ben,
         a `agents-{hu,en}/plan-fixer.md`-ben és a README-k több szakaszában. Egy
         `s/task\.md/tasks\.md/g` **elrontja az `05` hurkát** — ehhez a fájlnévhez ne érj.
      2. **`README-HU.md:1576` / `README.md:1564`** — az **Antigravity CLI belső** naplófájlja
         (*„Végrehajtási szakasz: `task.md` teendőlista"*, az `implementation_plan.md` /
         `walkthrough.md` mellett). Ez az eszköz sajátja, **nem** a quick-flow artefaktuma —
         változatlan marad.
      3. A `prompts/inprove-list*.md` és a `history/` **múltat rögzít** — visszamenőleg nem írjuk át. **A `cycle-status.py` visszafelé
      kompatibilis ágat kap:** a lightweight ág `tasks.md`-t keres, és ha az nincs, a régi
      `task.md`-t is megnézi (`:201` környéke, a `analyze_file` / `validate_file_*` mintája
      szerint, ahol a régi hely már ma is visszafelé kompatibilitásból marad).
- [x] **QF4 — Fázis-kapu a 2. és 3. fázis elején.** Ma a fázisváltás egyetlen jelzése a
      beszélgetésben elhangzott „igen". A 2. fázis belépője olvassa a `spec.md`
      `<field:f_status>`-át (`<status:ready_for_tasks>` kell), a 3. fázis a `tasks.md`-ét
      (`<status:ready_for_implement>`). Ez az 1. tervezési elv (fáziskapu), és ez teszi a
      megszakadást túlélhetővé.

---

## 6. Közös shared-blokkok beemelése (a duplikált szabályok megszüntetése)

A quick-flow ma **két** INCLUDE-ot hordoz (`lang/output-language.md`, `shared/context-check.md`).

- [x] **QF10 — `<!-- INCLUDE:shared/path-format.md -->`** (RP1). A skill „Alapelvek" szekciója ma
      saját prózában írja újra az útvonal-szabályt — pontosan azt a hibát ismételve, amit az RP1
      megszüntetett (a szabály korábban három helyen, ütköző tartalommal élt). A saját bekezdést
      **töröld**, helyére a marker.
- [x] **QF11 — Az RP1 kapu hívása a fázisok végén.** A `path-format.md` blokk maga írja elő a
      `analyze-gate-check.py … --paths-only` futtatását; a D1 átnevezés után ez a quick-flow
      `spec.md` + `tasks.md` párjára **is lefut**. A konzisztencia-ellenőrzési pontokban mondd ki,
      hogy ez a kapu **kötelező** (a többi determinisztikus kapu továbbra sem — D6).
- [x] **QF12 — `<!-- INCLUDE:shared/phase-commit.md -->` vagy a determinisztikus ellenőrzés
      átvétele.** A quick-flow ma commitol, de „érzésre": nincs `git log -1 --oneline` + üres
      `git status --short <ciklus-mappa>` ellenőrzés, és nincs kimondott fázishatár (PE1).
      **Döntés a végrehajtónál:** ha a `phase-commit.md` teljes beemelése túl nagy (a hurok-fázisok
      bekezdései itt értelmetlenek), akkor a **4. lépés determinisztikus ellenőrzését** és a
      PE1 fázishatárt vegyük át rövidítve, a blokkra hivatkozva. A commit-üzenet formátuma
      **nem** a nagy flow `cycle-NN: <fázis-tag>` alakja (arra a `07`/`09` keres vissza, ami itt
      nem fut), hanem a `conventions.md`-ből olvasott konvenció (QF1/D7).
- [x] **QF13 — `<!-- INCLUDE:shared/dereferencing.md -->`** (KX2). Itt a `spec.md` az **egyetlen**
      végrehajtási igazság (nincs `plan.md`), tehát a hivatkozás-feloldás és a csonkítás-mentes
      átemelés még kritikusabb, mint a nagy flow-ban — ma csak a TC1-pontnál van kimondva.
- [x] **QF14 — `<!-- INCLUDE:shared/artifact-voice.md -->`** (AV1). A `spec.md`/`tasks.md` az
      implementálónak szól; a nagy flow-ban ez kemény padló (az `05` méri), itt kapu nélkül is
      hordozható szabály.
- [x] **QF15 — `<!-- INCLUDE:shared/conventions-change.md -->`** (GC1). A quick-flow **tipikus
      feladata** épp konfiguráció, port, teszt-parancs — vagyis pont az, amit a kapuk a
      `conventions.md`-ből olvasnak. Ma semmi nem mondja, hogy a `conventions.md` frissítése a
      ciklus része. _(A blokk négy feltétele közül a 2. és 4. a nagy flow plan/07-jére hivatkozik
      — a beemelés mellé egy sor kell, hogy ebben a flow-ban a `spec.md` technikai vázlata és a
      3. fázis tesztje veszi át a szerepüket.)_
- [x] **QF9 — Konszolidált „Megállási szabályok" szekció + az IM1 ellenpár.** A megállási esetek
      ma szét vannak szórva (⛔ kapuk, beragadás, spec-hiba, túlnövés). Egy záró szekció sorolja
      fel mind, **és mondja ki a kimondott ellenpárt** (`IM1` mintájára): a 3. fázis a task listát
      **egy futásban** dolgozza fel, egy task lezárása (pipa) **nem** fázis-vég, és a megállás
      eseteinél **nincs több** — taskonkénti felhasználói riport, per-task link vagy
      „folytathatom?" kérdés nem kerülhet a hurokba. Ez ma teljesen hiányzik, és pont a gyenge
      modellek hibamódja.

---

## 7. Teszt-keményítés — közepes csomag (D3)

Mind a hat tétel a `spec.md` **Kötelező Tesztelési Stratégia** pontjába és a `tasks.md`
teszt-lépéseibe megy. **Kapu-script egyikhez sem készül** (D3).

- [x] **QT1 — Cél-környezet (EV1/EV3/EV5 leképezése).** A tesztstratégia kap egy kötelező
      **`<field:f_target_env>`** sort (a nagy flow ugyanezt a mezőt használja a planben). Nem
      lokális cél esetén: a **cél-host literálisan a parancsban** szerepeljen (npm-script neve
      vagy configfájlban rejtett cím **nem elég** — `7/g`), a lépés előtt legyen egy
      **elérhetőségi probe** ugyanarra a hostra, és a `localhost` / `127.0.0.1` alak
      **tilos**, kivéve ha a lokálisnak látszó cím egy **deklarált** port-forward mögött van
      (ezt a spec mondja ki, `7/n`).
- [x] **QT2 — `[local]` / `[remote]` címke** (EV8). Minden teszt-lépés / teszt-csoport fejléce
      viseli a címkét. **Nyelvfüggetlen literál** (1.2) — az indok ugyanaz, mint az `EV8`-nál: a
      címke joinolható marad. Kapu nincs; az érték az, hogy a *szándék* kimondva legyen, és a
      remote-teszt hiánya **hiányként** kiolvasható legyen.
- [x] **QT3 — „Mit ellenőriz és miért" minden teszt-lépés előtt** (TD7). Egy állítás-mondat, a
      `spec.md` cél- vagy DoD-pontjára hivatkozva. A `tasks.md` teszt-lépései ma parancsok cél
      nélkül → bukásnál nem eldönthető, a kód rossz-e vagy a teszt, és az ágens a legkönnyebb
      zöldítő utat választja. **Kalibrációs minta kell mellé** (kitöltött példa), mert a `7/h`
      szerint a padló önmagában nem termel részletet.
- [x] **QT4 — Vacuous teszt tilalma** (TB1). `assert True`, üres törzs, csak-létezést-ellenőrző
      váz **nem teszt**. Konzervatív mintakészlet elég (a nagy flow `test-substance-check.py`-ja
      itt nem fut).
- [x] **QT5 — `skipped` ≠ bizonyíték** (SK1). Egy `pytest.skip` / `test.skip` úton kilépő teszt
      nem igazol semmit: ha egy tervezett teszt skippel, azt a lezárás előtt **ki kell mondani** a
      felhasználónak, indoklással — nem számolható zöldnek.
- [x] **QT6 — Egy futtatás = egy azonosítható teszt** (CK1/TX1) — **és a mai ütköző mondat
      feloldása.** A 3. fázis ma azt kéri, hogy bukás után *„futtasd újra az ÖSSZES tesztet"*.
      Helyette: (a) minden teszt-lépés **azonosíthatóan, szelektorral** fut, egy lépés = egy
      futás; (b) a **regressziós összefutás külön, utolsó lépés** — nem helyettesíti a
      lépésenkénti futást. Így a bukás visszakereshető marad, és nem tűnik el egy gyűjtő
      futásban.

---

## 8. Flow-határ — a két út együttélése (D5)

- [x] **QF5 — Ciklusszám a BQ2 formula szerint.** A 2. szakasz 3. pontja („Ciklusszám
      megkeresése") ma csak `ls specs/`-et néz. Helyette a `01-add-cycles` **BQ2** formulája:
      `NN = max(roadmap.md + ls specs/ ciklusszámai, a feature branch-ekben lévő cycle-NN
      számok) + 1` (VCS mellett). A szabályt **ne írd újra** — hivatkozz a `01` „Ciklusszám
      meghatározása (BQ2)" szekciójára, és vedd át a formulát egy sorban.
- [x] **QF6 — Roadmap-bejegyzés.** Ha a `specs/roadmap.md` **létezik**, a quick-flow ciklusa egy
      sorral bekerül (ciklusszám, név, egy mondat, státusz), és a lezáráskor lezárt állapotot kap.
      **Ha nem létezik, ne hozd létre** (a roadmap gazdája a `01`) — ilyenkor egy sor a záró
      üzenetben, hogy a ciklus nincs regisztrálva.
- [x] **QF7 — `docs-generated/` drift-jelzés.** A ciklus lezárásakor: ha a `docs-generated/`
      **létezik** és a ciklus a rendszer viselkedését változtatta, egy sor a
      `docs-generated/design-drift.md`-be (mit változtattunk, melyik quick-flow ciklus, mi nincs
      átvezetve), **és** explicit figyelmeztetés a felhasználónak, hogy a `docs-generated/` a
      következő nagy ciklus `08-doc-sync` fázisáig elavult marad. Indok: a `02-write-spec` a
      `system-overview.md`-t **current truth**-ként olvassa. A `docs-generated/` többi fájljához
      **nem** nyúlunk (annak gazdája a `08`).
- [x] **QF8 — `manual-test-plan` quick-flow ág.** A `manual-test-plan.md` MT1 kapuja
      (`:29`, `:60`) `analyze-report.md` = `PASS`-t követel. Kapjon **második, egyenértékű
      belépőt**: ha a ciklusban **nincs** `plan.md` (tehát quick-flow ciklus), a kapu a `tasks.md`
      `<field:f_status>` mezőjét olvassa, és **pontosan két értéket** fogad el:
      `<status:ready_for_implement>` vagy `<status:done>` (a státuszok **nem rendezettek**, ezért
      nincs „legalább ilyen" összehasonlítás — a két elfogadott értéket tételesen sorold fel;
      `<status:draft>` esetén STOP), és a fázis a `spec.md` technikai vázlatából + tesztstratégiájából szerel össze
      (a `plan.md` `<sec:environment_coords>` helyett). A `manual-test-gate-check.py` **nem
      ellenőrzi** az MT1-et (az a skill prompt dolga), tehát script-módosítás nem kell — de a
      gate-check `TG-NN`/MG-checkjei így is lefutnak a kimeneten. **A quick-flow oldalán:** egy
      sor, hogy a `/bs-manual-test-plan` innen is használható.
- [x] **QF16 — Brainstorm-átvétel.** A skill belépője ismerje fel a
      `/bs-quick-flow brainstorm: NN` alakot (a `brainstorm.md:173` átadó sorával összhangban):
      olvassa be a `.bs-brainstorm/brainstorm-NN-<slug>.md` desztillátumát (Cél · Tények ·
      Döntések · Nyitott kérdések), és abból induljon az interjú — a nyitott kérdéseket
      **kérdezze meg**, ne találgassa.
- [x] **QF17 — Segédparancs-kereszthivatkozások.** Egy rövid szekció/tábla: `/bs-cycle-status`
      (ismeri a lightweight flow-t), `/bs-manual-test-plan` (QF8 után elérhető),
      `/bs-export-doc`, `/bs-brainstorm` (QF16). Ma a quick-flow **egyet sem** említ.

---

## 9. Agent-kontraktus (D4)

- [x] **QF18 — A quick-flow tételesen megadja a helyettesítéseket.** A „Felhasznált specialista
      ágensek" tábla mellé, ágensenként egy sor:
      - **`researcher`** — változatlan használat (Mód B: ad-hoc kérdés). Nincs helyettesítés.
      - **`analyzer`** — hatókör-paramétert **nem** adunk (a prompt ilyenkor mind az öt
        kategóriát viszi — ez a dokumentált degradációs ág); szelet-fájl nincs; a bemenet a
        `spec.md` + `tasks.md` **pár** (a `plan.md` helyét a `spec.md` technikai vázlata veszi
        át). Mondd ki, hogy a `plan.md`-re hivatkozó bemeneti pontja ebben a flow-ban üres.
      - **`reviewer`** — kötelező `plan.md` helyett a `spec.md` **technikai vázlata**; a kimenet
        **`specs/cycle-NN-<cycle-name>/code-review.md`** (a ciklus gyökerében, `test-report/`
        nélkül — azt a mappát a quick-flow nem használja); az `MF-NN` azonosítók és az RV-INC
        inkrementális írás **megmarad** (megszakadás-tűrés), de **nincs** per-item számláló és
        nincs önjavító hurok: a `<status:must_fix>` tételeket a fő ágens a lezárás előtt inline
        javítja, a `<status:suggestion>`-öket jelzi.
- [x] **QF19 — `called_by` bővítés** a három agent-promptban (`agents-hu/` **és** `agents-en/`):
      `researcher.md`, `analyzer.md`, `reviewer.md` frontmatterébe bekerül a
      `"skills/quick-flow.md"` sor. A promptok **törzse változatlan** (D4).
- [x] **QF20 — `sync-gemini-agents.py` regenerálás** (írás módban), majd `--check` → 0. Agent-
      frontmatter változott, tehát ez **kötelező** (1.3).

---

## 10. Dokumentáció

- [x] **10.1 — `README-HU.md`** — a **teljes** érintett sorlista (2026-09-04-i állapot;
      a szerkesztés közben csúszik, ezért a *tartalmat* keresd, ne a számot):
      **100.** (a két út bemutatása) · **108.** („Dokumentumok" tábla-sor: `spec.md` + `task.md`) ·
      **909–1010.** az „5. Egyszerűsített flow" szekció egésze — ebből: **911.** (bevezető),
      **938./939./942.** (5.1 mermaid ábra csomópontjai), **971./972.** (5.2 fázis-tábla),
      **977.** (5.3 fázis-visszalépés), **986.** (5.4 ágens-tábla `analyzer` sora),
      **1011./1013./1014./1018.** (5.6 példa-prompt párbeszéde) ·
      **1040.** (segédparancs-tábla `bs-quick-flow` sora) · **1192.** (*„a háromfázisú `quick-flow`
      … Jira-prefixes commit-konvenciójával a `spec.md` és a `task.md` jóváhagyásakor"* → QF1/QF2/QF3) ·
      **1285.** (a `test-conventions.md` fogyasztói).
      **Tartalmilag** az 5.1 ábra kap státusz-mezőt és fázis-kaput, az 5.2 tábla a kötelező
      cél-környezetet és a QT-tételeket, az 5.4 tábla a QF18 helyettesítéseit.
      **NEM módosul:** **1576.** (Antigravity belső `task.md` — QF3/2. csapda), és minden
      `analyze-task.md` előfordulás (**613./615./632./635./656./881./1035./1214./1420.**).
- [x] **10.2 — `README.md`** (angol pár, ugyanazok a helyek eltolva): **98.** · **106.** ·
      **900–1000.** (ebből **902.**, **929./930./933.**, **962./963.**, **967.**, **976.**,
      **1001./1003./1004./1008.**) · **1030.** · **1182.** · **1274.**
      **NEM módosul:** **1564.** (Antigravity belső `task.md`).
- [x] **10.3 — `prompts/meta-improve-prompts.md`.** (a) A fájl-tábla kap sort a
      `prompts/skills-hu/quick-flow.md`-re (ahogy a `brainstorm` és a `manual-test-plan` már
      kapott), **és** a `cycle-status` / `export-doc` segédparancsokra — ezek hiánya az oka, hogy
      a quick-flow kimaradt minden felülvizsgálatból (2.1). (b) Új tervezési elv: **`7/o` — „a
      második út is elcsúszhat: ha egy keményítő kör a nagy flow-ban tanulságot hoz, kérdezd meg,
      igaz-e a quick-flow-ra is"**, a `QF`/`QT` azonosítókkal és azzal a méréssel, amit a 2.2
      szakasz ad (a `cycle-status` törése).
- [x] **10.4 — `prompts/lang/{hu,en}/descriptions.json`**: a `bs-quick-flow` leírásában
      `task.md` → `tasks.md`.
- [x] **10.6 — `berki-spec-directory-structure.md`** (**48. sor**): a `quick-flow.md` sora ma
      *„(`spec.md` → `task.md` …)"*-t ír → QF3 szerint. Ez a negyedik dokumentum, amit a
      quick-flow érint — a korábbi tervek egyike sem sorolta.
- [ ] **10.7 _(hatókörön kívül — csak ha a felhasználó kéri)_.** A keresés közben kiderült, hogy a
      `meta-improve-prompts.md` **9. tervezési elve** (az `05`-analyze leírása) is elavult: nem
      ismeri a **TR1 triázs-megállást**, az `analyze/analyze-task.md` javítási listát és az
      **AD1** `analyze/` almappát, amiket a `README-HU.md` (613./615./1214./1420. sor) már
      dokumentál. Ez **nem** a quick-flow dolga, és nem része ennek a tervnek — de ha a
      meta-promptot amúgy is szerkesztjük (10.3), egy körben javítható.
- [x] **10.5 — `prompts/lang/{hu,en}/quick-flow.md`**: ha bármelyik új tétel **user-facing
      mondatot** vagy **artefaktum-sablont** vezet be (pl. a QF6 roadmap-bejegyzés sablonja, a
      QF7 drift-sor formája, a QF8 átirányító üzenet), az **nem** a skillbe kerül, hanem új
      `ANCHOR` a lang-fájlba, **mindkét nyelven**, és a skillben INCLUDE marker hivatkozik rá.

---

## 11. Kapuk (kézzel, commit előtt)

- [x] `python3 prompts/scripts/sync-gemini-agents.py` (írás, mert agent-frontmatter változott)
- [x] `python3 prompts/scripts/sync-gemini-agents.py --check` → 0
- [x] `python3 prompts/scripts/lang-parity-check.py` → 0
- [x] `python3 prompts/scripts/lang-parity-check.py --strict` → 0
- [x] **Füst-teszt a `cycle-status.py`-ra:** egy `tasks.md`-vel és státusszal rendelkező, plusz egy
      régi `task.md`-s (státusz nélküli) próba-ciklusmappán fusson le, és mindkettőre értelmes
      állapotot adjon (QF3 visszafelé-kompatibilitás).
- [x] **Emberi review (ez nem gépi kapu):** a `lang-parity-check.py` a **szerkezeti** eltérést fogja meg, a
      **jelentés**-eltérést nem — a hu/en quick-flow párt át kell olvasni. **Megtörtént (2026-09-05):**
      a 344-344 sor tételes összevetése **egyetlen jelentés-eltérést sem** talált (lásd 13/8.).

---

## 12. Végrehajtási sorrend

1. **4. szakasz** (QF-A1…A5) — elavult tartalom kivezetése. Döntést nem igényel, és megtisztítja
   a fájlt a további szerkesztéshez.
2. **5. szakasz** (QF1–QF4) — `conventions.md`-olvasás, státusz-mező, átnevezés, fázis-kapuk.
   A `cycle-status.py` visszafelé-kompatibilis ága **ugyanebben a körben** (QF3).
3. **6. szakasz** (QF10–QF15, QF9) — shared-blokkok és a megállási szabályok. A `path-format`
   beemelése után a saját, duplikált bekezdést **tényleg töröld**, különben két szabály él.
4. **7. szakasz** (QT1–QT6) — a teszt-keményítés közepes csomagja, kalibrációs mintákkal.
5. **8. szakasz** (QF5–QF8, QF16, QF17) — flow-határ. A QF8 a `manual-test-plan.md`-t is módosítja.
6. **9. szakasz** (QF18–QF20) — agent-kontraktus + gemini-tükrök regenerálása.
7. **10. szakasz** — dokumentáció (README ×2, meta-prompt, descriptions, lang-blokkok).
8. **11. szakasz** — kapuk, majd egy commit. A commit-üzenetben **külön jelöld**, hogy tartalmi
   javítás is van benne (nem csak szerkezeti), mert a paritás-kapu ezt nem látja.

---

## 13. A végrehajtás tapasztalatai és a tervtől való eltérések

A 3. szakasz **négy fő döntése (D1–D8) változatlanul állt**; a terv lefutott. Az alábbi hét pont
kiegészítés vagy pontosítás, nem döntés-felülírás.

1. **QF16 — a brainstorm átadó sora `input:`, nem `brainstorm: NN`.** A `brainstorm.md:173` átadó
   táblája ma szó szerint `/bs-quick-flow input: <a feladat egy mondatban>`-t javasol, tehát a
   tervben feltételezett `brainstorm: NN` alak ott **nem szerepel**. A `brainstorm.md`-hez nem
   nyúltunk (nincs a terv hatókörében); helyette a quick-flow **belépő szekciója mindhárom alakot
   felismeri** (`/bs-quick-flow`, `input: …`, `brainstorm: NN`), és a desztillátum-olvasás a
   harmadikhoz tartozik. Így a meglévő átadás nem törik, az új út viszont dokumentált.
2. **QF12 — a `phase-commit.md` NEM lett beemelve, a rövidített átvétel nyert.** A blokk két
   ponton mondana ellent a QF1/D7-nek: (a) kimondja, hogy a commit üzenete **pontosan**
   `cycle-NN: <fázis-tag>` (itt viszont a `conventions.md` dönt), (b) a hurok-fázisok
   (05/07) bekezdései ebben a flow-ban értelmezhetetlenek. Ezért a 4. lépés determinisztikus
   ellenőrzése (`git log -1 --oneline` + üres `git status --short`) és a PE1 fázishatár
   **rövidítve, a blokkra hivatkozva** került a két fázis-záró pontba.
3. **QF3 / `cycle-status.py` — a visszafelé-kompatibilitás a fájlnévnél tovább ment.** A puszta
   `task.md`-fallback a 11. szakasz füst-tesztjén még mindig `MÉG NEM FUTOTT`-ot adott volna a
   régi ciklusokra (azokban **nincs** státusz-mező, az volt a 2.2/a törés lényege). Ezért a
   lightweight ág a státusz-mező hiányában **közvetett bizonyítékra** vált (`KÉSZ*` / `INDIRECT`,
   a keretben már létező jelölés): a spec akkor lezárt, ha van feladatlista, a megvalósítás pedig
   a checkbox-arányból derül (új `count_checkboxes()` segédfüggvény). Új stílusú ciklust ez nem
   érint — ott mindig van státusz.
4. **QF6 — a roadmap nem tábla.** A `specs/roadmap.md` a `01-add-cycles` szerint `## Cycle NN —
   <cím>` blokkokból áll, a lezárást a címsorban lévő `✅` jelzi (ezt olvassa a
   `cycle-status.py` `is_roadmap_cycle_closed()`-je). A `BS-roadmap-sor` horgony ezért **blokk-
   sablon**, nem táblasor.
5. **QF8 — a `lang/{hu,en}/manual-test-plan.md` `analyze-kapu-stop` blokkját is át kellett írni.**
   Az utolsó mondata szó szerint azt állította, hogy quick-flow ciklusban *„ez a parancs nem
   használható"* — ez a QF8 után hazugság lett volna. A mondat kikerült, és új horgony
   (`quick-flow-kapu-stop`) fogalmazza meg a `<status:draft>` esetén adandó STOP-üzenetet.
6. **QF3 — két, a 10. szakaszban nem sorolt lang-blokk is `task.md`-t írt.** A
   `lang/{hu,en}/01-add-cycles.md` (a `01` quick-flow-javaslata) és a
   `lang/{hu,en}/00-init-project.md` (a módszertan-összefoglaló) — mindkettő javítva.
7. **A skill szerkezete bővült.** A `quick-flow.md` frontmattere megkapta a keretben szokásos
   `output` / `subagents` / `scripts` / `shared` kulcsokat (a shared-lista a QF10/QF13–QF15
   markereket tükrözi), és két új szekció keletkezett: `## 5. Megállási szabályok` (QF9) és
   `## 6. Segédparancsok` (QF17) — emiatt a Best Practice szekció `## 5.`-ből `## 7.`-re
   csúszott, plusz a fájl elejére bekerült egy `## Belépő` szekció (QF16). A két nyelvi példány
   sorszinten továbbra is igazodik (mindkettő **344 sor**).

8. **Az emberi review eredménye (2026-09-05).** A hu/en `quick-flow.md` pár mind a 344 sora
   tételesen összevetve: a szekció-sorrend, a QF/QT azonosítók, az INCLUDE markerek, a mermaid
   ábra élei, a kalibrációs minta és a Megállási szabályok / Segédparancsok táblák **soronként
   fedik egymást**, jelentés-eltérés nincs. Egyetlen javítás született, és az is a köröktől
   független, régi (`8bd758c` óta élő) elgépelés a magyar példányban: *„egy ülé/menetben"* →
   *„egy ülésben/menetben"* (35. sor; az angol pár már helyesen `in a single session/pass`).
   A `lang/{hu,en}/quick-flow.md` három horgonya és a `manual-test-plan` QF8-ágai szintén
   egyeznek. A build-füstteszt megismételve: `install-helper.py` hu+en `Success`, a telepített
   `bs-quick-flow` (502/504 sor) és `bs-manual-test-plan` (445/449 sor) `SKILL.md`-jében **nulla**
   feloldatlan INCLUDE marker és nulla feloldatlan token.

**A kapuk eredménye (11. szakasz):** `sync-gemini-agents.py` (írás + `--check`) → 0 ·
`lang-parity-check.py` → 0 · `--strict` → 0 · a `cycle-status.py` füst-teszt négy próba-ciklusra
(új stílus kész / új stílus folyamatban / régi `task.md` teljesen kipipálva / régi `task.md`
félkész) értelmes állapotot ad · `install-helper.py` build mindkét nyelven `Success`, a
`bs-quick-flow` és a `bs-manual-test-plan` telepített `SKILL.md`-jében **nulla** feloldatlan
`INCLUDE` marker és `<sec:…>`/`<field:…>`/`<status:…>` token.
