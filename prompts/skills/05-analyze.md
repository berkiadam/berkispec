---
phase: 05
name: bs-analyze
description: "berkispec - 05. Használd az implementáció előtt (Phase 05), ha a tasks.md 'Implementálásra kész'. Kereszt-fázisos konzisztencia-kapu a spec.md/plan.md/tasks.md között: subagentekkel (analyzer, *-fixer) azonosítja és automatikusan javítja az ellentmondásokat. Létrehozza az 'analyze-report.md'-t (PASS/FAIL)."
prerequisites:
  - "specs/cycle-NN-<name>/tasks.md státusz: Implementálásra kész"
output:
  - "specs/cycle-NN-<name>/analyze-report.md (PASS / FAIL)"
prev: bs-write-tasks
next: bs-implement
subagents:
  - "agents/analyzer.md"
  - "agents/spec-fixer.md"
  - "agents/plan-fixer.md"
  - "agents/tasks-fixer.md"
shared:
  - "shared/phase-commit.md"
scripts:
  - "scripts/analyze-gate-check.py"
---
# 05 — Analyze (kereszt-fázisos konzisztencia ellenőrzés + önjavító hurok)
## Kontextus ellenőrzés

Ha azt detektálod, hogy ennek a fázisnak a futtatása most indul (ez az első prompt a fázisban), de a kontextus nem „friss” (azaz a beszélgetési előzmények tartalmaznak korábbi fázisokból vagy futásokból származó üzeneteket), akkor kérdezz rá a felhasználónál:
> *„Úgy tűnik, hogy a fázis indításakor a kontextus nem teljesen friss. Szándékosan nem futtattál `/clear`-t az új fázis megkezdése előtt (a tokenekkel való spórolás érdekében)?”*
Várd meg a felhasználó válaszát, mielőtt folytatnád a fázis futtatását.

---

Spec driven development-ben fejlesztünk szoftvert. A fejlesztés ciklusokra van bontva. Minden ciklus egy önállóan lefejleszthető, önállóan tesztelhető részegysége a teljes implementációnak.

Ez a folyamat **5. fázisa (0–9)**: 0-init · 1-ciklusok · 2-spec · 3-plan · 4-tasks · **5-analyze ←** · 6-implement · 7-validate · 8-doc-sync · 9-review.

---

## Cheat sheet

| Szekció | Egy mondatban |
|---|---|
| Előfeltétel | `tasks.md` = `Implementálásra kész`, `conventions.md` létezik, tiszta munkafa. |
| Szereped | **Orchestrátor (read-only):** te magad tervezési dokumentumot nem szerkesztesz — vezényelsz, riportot írsz, kérdezel, státuszt fordítasz. |
| Mechanikus kapu | Minden futás előtt `analyze-gate-check.py` (plan-ID ↔ task-hivatkozás, marker, `⟂`, `DoD-NN`, kötelező táblák) — a találatai `Must Fix`-ek a szkript által adott célfázissal. |
| Analyzer subagent | A read-only kereszt-vizsgálatot a `agents/analyzer.md` subagent végzi; te a megállapítás-listáját értékeled. |
| Fixer-subagentek | A javítást a `agents/{spec,plan,tasks}-fixer.md` wrapperek végzik (= 02/03/04 fázis Fix-módja); ők írják a tervezési dokumentumokat. |
| Eredmény | `analyze-report.md` PASS vagy FAIL, súlyossági besorolással + Hurok-napló. |
| Delta + sweep | A 2. futástól az analyzer **delta módban** dolgozik (előző Must Fix lista + `git diff`); a PASS **kizárólag a záró teljes sweepből** adható (D10). A downstream re-deriválás **feltételes** (D11). |
| FAIL | **Önjavító hurok indul:** legkorábbi érintett célfázis → fixer-subagent → downstream re-deriválás (`02→03→04`) → újra-analyze, amíg PASS — `max X = 3` iterációval. |
| Kérdés-megállás | Ha a fixer nyitott kérdést jelentett: az orchestrátor (te) kérdezed a felhasználót `FÁZIS/Knn` fejléccel, beírod a választ, újraindítod a fixert — a hurok **folytatódik** (nem hiba). |
| PASS | Tovább a 06-implement fázisra. Commit: a hurok végén egyetlen `cycle-NN: 05-analyze`. |
| Fázis-záró commit | **Kötelező, minden lezáró ágon** (PASS és FAIL egyaránt) — a *Fázis-záró commit* szekció eljárása szerint (PC1). Commit nélkül a fázis nincs lezárva. |

---

## Szereped: orchestrátor (read-only invariáns)

A `05-analyze` egy **vezénylő** fázis. Két dolgot tarts észben végig:

1. **Te magad nem szerkesztesz tervezési dokumentumot** (`spec.md`, `plan.md`, `tasks.md`). Minden tartalmi javítást a fixer-subagentek (= a 02/03/04 fázisok Fix-módja) végeznek. Az egyetlen fájl, amit te írsz, az `analyze-report.md`, és az egyetlen közvetlen módosításod a tervezési dokumentumokon a **státusz-mező fordítása** (a `[analyze-loop]` marker fel- és levétele, lásd lent).
2. **A read-only diagnózis a `analyzer` subagenté.** Te a megállapítás-listáját olvasod és döntesz PASS / FAIL-ról, majd FAIL esetén levezényled a javító hurkot.

Így a fázis felelőssége tiszta: **diagnózis (analyzer) → vezénylés (te) → javítás (fixerek)**, mindegyik a maga helyén.

---

## Előfeltétel

0. **Ciklus-beazonosítás:** ha a felhasználó megadott ciklust/fájlt, azt használd; különben a legfrissebb `specs/cycle-*` mappát ajánld fel megerősítésre — *"A(z) `specs/cycle-NN-<name>` ciklussal szeretnél dolgozni? Igen / Nem (megadom a ciklust)"* — és várj a válaszra, mielőtt továbblépsz.

1. **`conventions.md` létezés-ellenőrzés:** olvasd be a projekt gyökerében a `conventions.md`-t. Ha nem létezik, **STOP** — jelezd a felhasználónak, hogy térjenek vissza a `00` projekt inicializálás fázishoz, és ne folytasd.

2. **Tasks státusz:** olvasd be a `specs/cycle-NN-<cycle-name>/tasks.md` státuszát. **Ha nem `Implementálásra kész`, STOP** — a task lista még nem zárult le. Jelezd, és térjenek vissza a `04` tasks fázishoz. (Kivétel: ha a státusz `Implementálásra kész [analyze-loop]` markert visel, egy korábbi analyze-hurok szakadt meg — lásd „Folytatás megszakított futás után".)

3. **Munkafa-ellenőrzés (csak VCS esetén):** futtasd: `git status --short`. Ha van commitálatlan változtatás:
   - Listázd ki az érintett fájlokat.
   - Jelezd: *"Az analízis hurok módosíthatja a tervezési dokumentumokat; a tiszta munkafa megkönnyíti a visszakövetést."*
   - Kérdezd meg: *"Commitáljam ezeket most, vagy folytassam?"* — egy kérdés, várj a válaszra, majd folytasd. (No-VCS projektben kimarad.)

---

## Folytatás megszakított futás után

**A folytatás első analyze-futása mindig TELJES** (nem delta) — nem tudhatod, hol szakadt meg a javítás, és mihez képest lenne értelmes a diff. A mechanikus kapu (0. lépés) is fut.

Az analyze **diagnózisa** read-only, de a hurok már módosíthatta a tervezési dokumentumokat. A folytatást a `[analyze-loop]` státusz-marker, a `*-questions.md` nyitott kérdései és az `analyze-report.md` Hurok-naplója együtt teszi rekonstruálhatóvá. Döntési fa — **ebben a sorrendben**:

```
1. Visel valamelyik tervezési dokumentum (spec.md / plan.md / tasks.md)
   `[analyze-loop]` státusz-markert?
   → Igen → a hurok megszakadt. NE kezdj új analízist elölről.
     a) Olvasd be az analyze-report.md Hurok-napló szekcióját:
        melyik iterációnál és melyik fázisnál állt meg.
     b) Olvasd be az érintett *-questions.md-t: van-e nyitott [ ] kérdés?
        → Ha igen: a hurok kérdés-megállásnál állt. Tedd fel a kérdést a
          felhasználónak (fázis-fejléccel), vezesd át, majd folytasd a hurkot
          ugyanannál az iterációnál.
        → Ha nincs nyitott kérdés: a fixer befejezte a javítást, de a
          re-deriválás vagy az újra-analyze maradt el. Folytasd a downstream
          re-deriválással, majd futtasd újra az analyze-t.

2. Nincs [analyze-loop] marker, de létezik analyze-report.md.
   → Ha státusza PASS: az analízis lezárult, tovább a 06-ra.
   → Ha státusza FAIL és nincs marker sehol: a hurok lezárult max X feladással
     (lásd a report Hurok-naplóját). Jelezd a felhasználónak a megrekedt
     állapotot — ne indíts automatikusan új hurkot megerősítés nélkül.
   → Ha a report félbeszakadtnak tűnik (nincs minden kategória kitöltve) és
     nincs marker: töröld a részleges riportot, és kezdd elölről az analízist.

3. Nincs analyze-report.md és nincs marker.
   → Kezdd az analízist az "Feladatod" szerint.
```

---

## Feladatod

Ellenőrizd, hogy a ciklus tervezési dokumentumai (`spec.md`, `plan.md`, `tasks.md`) **konzisztensek egymással és a `conventions.md`-vel**, mielőtt az implementáció megkezdődne — és ha nem, **vezényeld le a javításukat** egy önjavító hurokban, amíg konzisztenssé válnak.

**Ne implementálj semmit.** Ez a sanity check (és szükség esetén javító hurok) az implementáció előtt.

A diagnózis **5 kategóriában** keres problémát (a `analyzer` subagent végzi):

1. **Duplikációk** — ismétlődő követelmények a spec/plan/tasks között (ugyanaz a viselkedés többször, redundáns task).
2. **Ambiguitás** — vágy fogalmak, hiányzó mérőszámok, nem mérhető elfogadási feltétel.
3. **Alulspecifikáció** — hiányzó elfogadási feltétel, meghatározatlan komponens, taskhoz nem rendelhető plan-szekció.
4. **Konvenció-ütközések** — a `conventions.md`-vel szembeni eltérés (tech stack, naming, teszt eszköz, merge stratégia, struktúra).
5. **Lefedettségi hiányok** — követelmény ↔ task egymáshoz rendelés: van-e spec-követelmény, amelyhez nem tartozik task, vagy task, amely nem vezethető vissza a planre.

---

## Kontextus betöltési szabályok

- A kereszt-vizsgálat sok fájl együttes olvasását igényli — **kötelező az `agents/analyzer.md` subagent indítása**. A subagent beolvassa a `spec.md` + `plan.md` + `tasks.md` + `conventions.md` négyest, elvégzi a **6 kategóriás** vizsgálatot (az utolsó, „végrehajthatóság és artefaktum-tulajdon" kategóriához **célzottan a repóban is ellenőriz létezést** — `Glob`/`Read`, nem audit), és **kizárólag a strukturált megállapítás-listát adja vissza** (a nyers fájltartalom nem terheli a fő kontextust).
- A subagent rendszerpromptja: olvasd be a `prompts/agents/analyzer.md`-t, és ezzel definiáld az `analyzer` subagentet.
- A subagent kimenetét te értékeled, és ez alapján döntesz PASS / FAIL-ról.
- A javító fixer-subagenteket szintén Task tool subagent-ként indítod, a saját wrapper-promptjukkal (`agents/spec-fixer.md`, `agents/plan-fixer.md`, `agents/tasks-fixer.md`) — lásd „Az önjavító hurok".
- **A `*-input-from-prev.md` fájlok (IP1) is bemenetek:** a subagent beolvassa a ciklus mappájában lévő `spec-`/`plan-`/`tasks-input-from-prev.md` fájlokat (amelyik létezik), és **nyitott `[ ]` tételt lefedettségi hiányként** jelez. Indoklás: egy nyitott tétel azt jelenti, hogy egy korábbi fázis átadott egy információt, amit a fogyasztó fázis se be nem épített, se el nem vetett — ez ugyanolyan rés, mint egy task nélküli követelmény.

  > **A `validate-input-from-prev.md`-t az 05 NEM vizsgálja:** annak a fogyasztója a 07, ami az analyze után fut — ott jogosan nyitott még.
  >
  > **A hurok fix-módjai (a fixer-subagentek) ezeket a fájlokat továbbra sem olvassák és nem írják** (IP1/6). Ez a check tehát **diagnózis**: a `Must Fix` a `spec.md`/`plan.md`/`tasks.md` hiányosságát nevezi meg (mi maradt ki), nem az átadó fájl kipipálását kéri. A pipálás a normál (nem fix-módú) fázis-futás dolga.

---

## Súlyossági besorolás

Minden megállapítás **Must Fix** vagy **Suggestion**:

- **Must Fix** = blokkolja az implementációt (a hibás alapra épülő implementáció kockázatos): valódi duplikáció, lefedettségi rés, konvenció-ütközés, meghatározatlan komponens, nem eldönthető elfogadási feltétel.
- **Suggestion** = nem blokkol, csak javasolt finomítás (átfogalmazás, kisebb tisztázás).

**PASS feltétele:** nincs `Must Fix` megállapítás. Ha csak `Suggestion`-ök vannak, az eredmény PASS (a suggestion-öket a felhasználó eldöntheti, de nem indítanak hurkot).

---

## 0. lépés — mechanikus kapu (`analyze-gate-check.py`) — MINDEN analyze-futás előtt

A gépiesen eldönthető ellenőrzéseket **nem az `analyzer` subagent végzi**, hanem egy szkript — determinisztikusan, olcsón, hamis riasztás nélkül:

> **Python-parancs (platformfüggő):** a példákban `python3` szerepel (Linux/macOS). **Windowson** a `python3` gyakran nem létezik — vagy a Microsoft Store stubja, ami megnyitja a Store-t —, ezért ott `python` vagy `py -3` a helyes hívás. Ha a `python3` „command not found" / „not recognized" hibát ad, **próbáld újra `python`-nal, majd `py -3`-mal**, ugyanazokkal a paraméterekkel. Ez nem a szkript hibája, és nem kell miatta megállni.

```bash
python3 <platform-scripts-mappa>/analyze-gate-check.py specs/cycle-NN-<cycle-name>
```

**Mit fed le:** plan-ID formátum/egyediség (P1), task→plan hivatkozás megléte (P2), nem létező ID-ra hivatkozás (P3), ID task nélkül (P4), sorszámos hivatkozás (P5), marker minden taskon (T1), `[OPS]` repo-fájlon (T2), státusz-frissítő task (T3), `⟂` szimmetria (T4), `DoD-NN` hiány/duplikáció (D1), `DoD-NNb` alakú utólagos azonosító (D2), kötelező táblák megléte (S1/S2).

**Kilépő kód:**
- **`0`** → nincs mechanikus megállapítás; indítsd az `analyzer` subagentet a szemantikai kategóriákra.
- **`1`** → a kimenet soronként `[kód] (célfázis: NN) üzenet` formátumú. **Mindegyik `Must Fix`**, a szkript által megadott célfázissal — vedd fel őket az `analyze-report.md` `Must Fix` listájába **szó szerint**, és az `analyzer` szemantikai megállapításaival együtt kezeld a hurokban. Ezeket ne kérdőjelezd meg és ne értékeld újra: gépi ellenőrzés eredményei.
- **`2`** → használati hiba (hiányzó ciklusmappa vagy dokumentum) → STOP, jelezd a felhasználónak.

**A kapu minden iterációban fut** (a javítás után is), és a delta-analyze mellett is teljes — így a mechanikus regresszió nem tud átcsúszni.

> **Az `analyzer` ezekre már nem kap külön feladatot.** Ha mégis ilyen megállapítást ad vissza, az duplikátum: a szkript kimenete az irányadó.

---

## FAIL — kategória → célfázis leképezés

Egy olcsóbb LLM-nek konkrét célt kell adni, nem „vissza a megfelelő fázisba". A `Must Fix` megállapítás kategóriája határozza meg a javító célfázist (= melyik fixer-subagentet indítod):

| Kategória | Célfázis (fixer) | Indok |
|---|---|---|
| Duplikáció | 03 (tervezési szintű), 04 (task-szintű) | a redundancia forrásához |
| Ambiguitás | 03 (technikai döntés), 02 (viselkedési — ritka) | ahol a fogalmat tisztázni kell |
| Alulspecifikáció | 03 (meghatározatlan komponens), 02 (hiányzó elfogadási feltétel) | a hiányzó döntés szintjére |
| Konvenció-ütközés | 03 (enyhe), 00 (súlyos — `conventions.md` felülvizsgálat) | összhangban az SK4 logikájával |
| Lefedettségi hiány | 04 (követelmény ↔ task újrarendelés) | a task lista a hiányos |
| Lefedettségi hiány — nyitott `*-input-from-prev.md` tétel (IP1) | a **fogyasztó** fázis (02 / 03 / 04 a fájl szerint) | ott maradt ki az átadott infó beépítése |
| Plan-hivatkozás hibája (PID1): hiányzó / nem létező `[P-…]` / sorszámos hivatkozás / `[P-…]`-hoz nincs task | **04** | a `tasks.md` hivatkozásai romlottak el |
| Végrehajtható plan-szekciónak nincs `[P-…]` azonosítója (PID1) | **03** | az ID kiadása a plan dolga |
| Scope-túlnyúlás (SC1): plan-képességnek nincs spec-forrása | **02** (ha kell a képesség → DoD-pont), **03** (ha nem kell → kivétel + `Out of scope`) | elfogadási feltétel nélkül nem fejleszthető |
| Konfiguráció-életút (KF1) hiányos vagy hiányzik | **03** | a paraméter propagációja terv-kérdés |
| Spec-teszteset nem képződött le plan-tesztesetre (TP1) / hiányzó környezet-felkészítés (TP3) | **03** | a `test-runner` csak a plant olvassa |
| Kötelező tábla hiánya (`Spec-lefedettség`, `Fordított lefedettség` → 03; `Plan-lefedettség` → 04) | a tábla gazdája | a kimaradt tábla = kihagyott kapu |
| Hiányzó/duplikált `DoD-NN` azonosító | **02** | a 07 per-item számlálója erre épül |

**Legkorábbi érintett fázis nyer:** ha több kategória is FAIL és különböző célfázisokra mutat, a hurok a **legkorábbi érintett fázisra** ugrik (02 < 03 < 04), majd onnan deriválja le újra a downstream fázisokat — különben a későbbi fázisok hibás alapra épülnének. (Súlyos konvenció-ütközés `00`-ra mutat: ez emberi döntést igényel a `conventions.md` szintjén — ilyenkor a hurok megáll és kérdez, nem javít automatikusan.)

---

## Az önjavító hurok (orchestrátor-hurok)

FAIL esetén **nem** adod vissza egyszerűen a vezérlést a felhasználónak. Helyette levezényelsz egy iteratív javító hurkot, amíg PASS nem lesz, vagy amíg el nem éred a `max X` korlátot.

### A hurok egy iterációja

1. **Célfázis meghatározása.** A `Must Fix` lista kategóriáiból (a fenti leképezés szerint) határozd meg a **legkorábbi érintett célfázist** (02/03/04). Ez a fixer belépési pontja.
2. **Státusz-marker felvétele.** A célfázistól lefelé minden érintett dokumentum státuszát fordítsd a fázis-megfelelő nem-kész állapotra `[analyze-loop]` markerrel (pl. `Piszkozat [analyze-loop]`). A marker jelzi: fix-mód aktív → a fixerek automatikusan léptetik a státuszt (lásd D7), és megszakítás után jelzi, hogy a doksit a hurok nyitotta vissza.
3. **Fixer-subagent indítása** a célfázishoz tartozó wrapperrel (lásd „Fixer-subagent indítása").
4. **Kérdés-megállás kezelése.** Ha a fixer az összefoglalójában nyitott kérdéseket jelentett (új `Knn` bejegyzések a `*-questions.md`-ben): tedd fel őket a felhasználónak **egyesével**, fázis-fejléccel (lásd „Fázis-fejléces kérdésformátum"), vezesd át a választ a `*-questions.md`-be (`[x]` + döntés), majd **indítsd újra ugyanazt a fixert** a most már megválaszolt kérdéssel. Ez nem számít új analyze-iterációnak.
5. **Downstream re-deriválás — FELTÉTELESEN (D11).** A felfelé javítás után a célfázis alatti fázisokat kell összehangolni (`02 → 03 → 04`) — **de csak akkor, ha a javításnak van downstream hatása.**
   - A fixer visszatérési összefoglalója kötelezően tartalmaz egy **`downstream-hatás:`** mezőt (lásd „Fixer-subagent indítása"): `nincs`, vagy `van — <mi változott, ami a következő fázist érinti>`.
   - **`nincs`** (tipikusan: megfogalmazás-pontosítás, duplikátum-összevonás, artefaktum-hang javítása, elgépelés) → **a downstream fixereket NE indítsd el.** Egy felesleges plan- vagy tasks-fixer futás teljes dokumentum-beolvasással jár, és új hibát is bevihet.
   - **`van`** → indítsd a downstream fixert, és **add át neki a `downstream-hatás` szövegét** — ez a reconciliation hatóköre. Ez **célzott reconciliation, nem teljes újraírás**: a lezárt `*-questions.md` döntéseket megőrzi.
   - Ha a fixer nem adta meg a mezőt, **kérdezd vissza tőle** egy mondatban — ne tippelj, és ne futtasd el „biztos, ami biztos" alapon a teljes láncot.
6. **Újra-analyze — DELTA módban (D10).** Előbb futtasd a **mechanikus kaput** (0. lépés — mindig teljes), majd indítsd az `analyzer` subagentet **delta bemenettel**:
   - **az előző kör `Must Fix` listája** (amit javítani kellett), és
   - **a tervezési dokumentumok változása**: `git diff -- specs/cycle-NN-<cycle-name>/` (a hurok alatt nincs commit, tehát a diff a hurok teljes változását mutatja).

   A delta-analyzer feladata kettő: **(a) igazolja**, hogy a `Must Fix` tételek tényleg megoldódtak, és **(b) a megváltozott szekciókra fókuszáltan** keressen új ellentmondást (a változás új rést nyithatott a nem változott részekhez képest). A hat kategória szemantikai része érvényes, de **csak a diff által érintett tartalomra**.
   - **Még van `Must Fix`** → új iteráció az 1. ponttól, a hurokszámláló +1.
   - **Nincs több `Must Fix`** → **még NEM PASS**: jön a **záró teljes sweep** (7. pont).

7. **Záró teljes sweep — a PASS egyetlen forrása (D10).** Javítás nélkül indíts egy **teljes** `analyzer` futást (mind a hat kategória, a teljes dokumentumokon, delta nélkül) + a mechanikus kaput.
   - **Nincs `Must Fix`** → a hurok konvergált, ugrás a „Státusz kezelés → PASS"-ra (itt kerül le a marker és történik az egyetlen commit).
   - **Van `Must Fix`** → új iteráció az 1. ponttól, a hurokszámláló +1. *(Ez normális: épp ezért van a sweep — a cycle-25-nél is a második teljes futás hozta elő a két lefedettségi rést.)*

   **Az első analyze-futás is teljes** (nincs mihez képest delta). A `max X` szempontjából a delta-analyze és a záró sweep **együtt egy iteráció**.

### Fixer-subagent indítása

- A fixer-subagent **rendszerpromptja** a célfázis fixer-wrappere: `agents/spec-fixer.md` (02), `agents/plan-fixer.md` (03), `agents/tasks-fixer.md` (04). A wrapper a megfelelő skill **Fix-mód** szekciójára delegál — nincs duplikált javító logika, és a fázis saját minőségi kapui automatikusan érvényesülnek.
- **Bemenet** a subagentnek: a célfázisra szűrt `Must Fix` lista (kategória + leírás + `fájl:hely`) + a célfázis dokumentumai.
- **Kimenet** a subagenttől: (a) az elvégzett (mechanikus) javítások összefoglalója, (b) a **`downstream-hatás:`** mező (`nincs` / `van — <mi érinti a következő fázist>`, D11), és (c) a `*-questions.md`-be felvett **új** kérdések azonosítói — azoké a pontoké, amelyekhez valódi döntés kell. A subagent **nem kérdez közvetlenül a felhasználótól** (nincs interaktív csatornája); csak gyűjt és visszaad. A kérdezés a te dolgod (D2).

### `max X` hurokszámláló + leállás

- **Alapérték: `max X = 3`.**
- **`X` egysége: a teljes analyze-újrafutások száma.** Egy `FAIL → fix → re-deriv → re-analyze` ciklus = **1** iteráció. A követő-kérdések miatti fixer-újraindítások és az egyes downstream fixer-hívások **nem** növelik `X`-et.
- **Két, egymástól független kilépési feltétel:**
  1. **Nyitott kérdés** → a hurok megáll, kérdez; a user válaszol; a hurok **folytatódik** (ez nem hiba, és nem fogyaszt iterációt).
  2. **`max X` elérve konvergencia nélkül** → a hurok feladja (lásd „Státusz kezelés → FAIL").

### `[analyze-loop]` státusz-marker (D7)

- **Formátum:** `[analyze-loop]` suffix a státusz-érték végén, pl. `Piszkozat [analyze-loop]`, `Nyitott kérdések vannak [analyze-loop]`.
- **Jelentése:** a dokumentumot az analyze-hurok nyitotta vissza, fix-mód aktív. Amíg a marker jelen van, a fixerek a státuszt **automatikusan** léptetik (megerősítés nélkül) — eltérően a 02/03/04 normál „megerősítés a státuszváltás előtt" szabályától. A felhasználó csak a **kérdéseknél** és a **végső PASS-nál** lép be.
- **Levétele:** PASS-kor (→ normál flow, a fixer a fázis valódi záró-státuszát adja) vagy `max X` feladáskor a vég-állapot szerint (lásd FAIL). A marker megléte egyúttal a megszakítás-utáni folytatás horgonya is.

### Commit-stratégia a hurokban (D9)

- **`analyze-loop`-ban nincs iterációnkénti commit** — zaj-mentes marad a történet.
- **Egyetlen commit a hurok lezárásakor** (PASS vagy `max X` feladás): `cycle-NN: 05-analyze`. Ez a commit **kötelező, mindkét ágon** — az eljárást (stage → commit → determinisztikus ellenőrzés → visszajelzés) lásd a *Fázis-záró commit* szekcióban (PC1).
- **Megszakítás-biztos:** a köztes commit hiányát a `[analyze-loop]` státusz-marker + a `*-questions.md` + a Hurok-napló pótolja — ezekből a folytatás rekonstruálható (lásd „Folytatás megszakított futás után").

---

## Fázis-fejléces kérdésformátum

Amikor a hurok közben kérdést teszel fel a felhasználónak, mindig jelezd, **hol jár** a hurok. A kérdés sablonja:

```
[<FÁZIS> · iter <n>/<max X> · <FÁZIS>/<Knn>]
<kérdés szövege>
```

- **Fázis:** `SPEC` / `PLAN` / `TASKS` (a célfázis, ahonnan a kérdés származik).
- **`iter n/max X`:** hányadik analyze-iterációnál tart a hurok.
- **`FÁZIS/Knn`:** a kérdés azonosítója fázis-prefixszel a párbeszédben (`SPEC/K07`, `PLAN/K03`, `TASKS/K02`). A **fájlokban** a kérdés sima `Knn` marad — a fájl helye (`spec-questions.md` / `plan-questions.md` / `tasks-questions.md`) kódolja a fázist.

Szabályok: **egyszerre egy kérdés**, várd meg a választ, és a válaszod végén helyezz el egy közvetlen, kattintható linket az érintett `*-questions.md`-re.

Példa:

> **[PLAN · iter 2/3 · PLAN/K05]**
> A `callLegacyVerify` timeout esetén retry-zzon, vagy azonnal 504-et adjon vissza? A spec nem rendelkezik róla.
> [plan-questions.md](file:///.../specs/cycle-NN-name/plan-questions.md)

---

## analyze-report.md struktúra

Hozd létre / frissítsd a `specs/cycle-NN-<cycle-name>/analyze-report.md` fájlt (relatív útvonal-formátum a dokumentum tartalmában, `file://` tilos):

```md
# Cycle NN: <cím> — Analyze report

**Státusz:** PASS | FAIL
**Futás:** YYYY-MM-DD HH:MM
**Hurok:** <iterációk száma> / <max X> (PASS | feladva)

## Összefoglaló

_Egy-két mondat: konzisztens-e a négyes, vagy hol van a baj, és hogyan zárult a hurok._

## Megállapítások (utolsó analyze)

### Must Fix
- [ ] <kategória> — <leírás> → célfázis: <fázis> (`fájl:hely` ha van)

### Suggestions
- <kategória> — <leírás>

## Végrehajthatósági leltár (6. kategória)

_Az `analyzer` subagent kimenetéből átvéve. **Kötelező szekció** — ha hiányzik, a PASS nem fogadható el._

**Futtatott artefaktumok:** <fájl → létezik / létrehozó task Tnnn / HIÁNYZIK>
**Prózában ígért tesztek:** <ígéret → teszteset + task / HIÁNYZIK>
**Artefaktum-tulajdon:** <rendben / a planben szerepel: ...>
**Státusz-frissítő task:** <nincs / Tnnn>
**Marker-helyesség:** <rendben / téves [OPS]: ...>
**Destruktív műveletek:** <jóváhagyás + immutable azonosító + rollback megvan / hiányzik: ...>
**Horgony-feloldás:** <feloldható / nem oldható fel: ...>
**Artefaktum-hang:** <rendben / skill-hangú meta-utasítás maradt: ...>

## Lefedettségi mátrix (követelmény ↔ task)

_**Mikor töltöd ki (D12):** a két mátrix a **záró teljes sweep** eredményéből készül, egyszer — a köztes iterációk nem generálják újra (gépiesen újraszámolható tartalom, a köztes állapotot a Hurok-napló őrzi). Ha a hurok `max X`-nél feladja, a mátrixokat az utolsó rendelkezésre álló állapotból töltsd ki, és jelöld: „(feladáskori állapot)"._

| Spec követelmény | Plan szekció (`[P-…]`) | Task(ok) | Lefedve |
|---|---|---|---|
| ... | `[P-CONFIG]` | T0xx | ✓ / ✗ |

## Plan-szekció ↔ task (PID1)

_A plan MINDEN `[P-…]` azonosítója szerepel; a „nincs task" sor indoklással érvényes._

| Plan szekció (ID) | Hivatkozó taskok | Rendben |
|---|---|---|
| `[P-CONFIG]` | T001, T002, T003 | ✓ |
| `[P-XYZ]` | — (indok: ...) | ✓ / ✗ |

_Eltérések, amiket itt kell kimutatni: ID task nélkül · task nem létező ID-ra · sorszámos hivatkozás `[P-…]` helyett · végrehajtható plan-szekció ID nélkül._

## Hurok-napló

_Iterációnkénti audit-nyom — a megszakítás-utáni folytatás horgonya._

### Iteráció 1
- **FAIL kategóriák:** <kategóriák>
- **Célfázis:** <fázis> (legkorábbi érintett)
- **Fix:** <a fixer-subagent összefoglalója egy sorban>
- **Nyitott kérdések:** <FÁZIS/Knn lista vagy „nincs">
- **Re-deriválás:** <mely downstream fázisok hangolódtak újra>
- **Eredmény:** PASS | FAIL → következő iteráció

### Iteráció 2
...
```

---

## Minőségellenőrzés — a jelentés lezárása előtt

Menj végig, mind a **6** kategória ténylegesen lefutott-e (az `analyzer` subagent kimenetében). **A 6. kategóriánál külön ellenőrizd, hogy a subagent visszaadta-e a „Végrehajthatósági leltárt"** — enélkül a PASS nem fogadható el, mert épp azok a hibák maradnának rejtve, amelyeket a lefedettségi mátrix szerkezetileg nem lát:

1. **Duplikáció** — átnézve spec/plan/tasks redundanciára?
2. **Ambiguitás** — minden elfogadási feltétel mérhető/eldönthető?
3. **Alulspecifikáció** — minden komponens és feltétel meghatározott?
4. **Konvenció-ütközés** — minden tervezési döntés egyezik a `conventions.md`-vel?
5. **Lefedettség** — a lefedettségi mátrix minden spec-követelményt és minden taskot tartalmaz?
6. **Végrehajthatóság és artefaktum-tulajdon** — a subagent visszaadta a *Végrehajthatósági leltárt* (lásd fent), és a **mechanikus kapu** (`analyze-gate-check.py`) is lefutott ebben a körben?

Ha bármelyik kategória nem futott le, ne zárd le a jelentést. Ha a hurok futott, ellenőrizd azt is, hogy a **Hurok-napló** minden iterációt tartalmaz.

---

## Státusz kezelés

### PASS (a hurok konvergált, vagy első nekifutásra tiszta)

Nincs `Must Fix` megállapítás.

Teendők **sorban**:
1. Írd a `analyze-report.md` státuszát `PASS`-re, töltsd ki a `Hurok:` mezőt és a Hurok-naplót (ha volt iteráció).
2. **Vedd le a `[analyze-loop]` markert** minden érintett dokumentumról — a fixerek a fázis valódi záró-státuszát adták (`Tervezésre kész` / `Task írásra kész` / `Implementálásra kész`); ellenőrizd, hogy ez áll-e mindegyiken.
3. **Egyetlen lezáró commit** (a hurok alatt nem volt köztes commit) — a *Fázis-záró commit* szekció eljárása szerint, **kötelező**:
   ```bash
   git add specs/cycle-NN-<cycle-name>/
   git commit -m "cycle-NN: 05-analyze"
   ```
4. Jelezd a felhasználónak a következő lépést és a fázis indító parancsát:
   > *"Az analízis konzisztensnek találta a tervezési dokumentumokat. Folytathatjuk a 6. lépéssel (implement). Az új fázis megkezdése előtt mindenképpen futtass egy `/clear` parancsot a kontextus kiürítéséhez, majd használd ezt a parancsot:*
   > ```
   > /bs-implement input: @specs/cycle-NN-<cycle-name>/tasks.md
   > ```"*
   > **A válasz végén helyezd el az `analyze-report.md` közvetlen, kattintható linkjét.**

### FAIL (`max X` elérve PASS nélkül)

A hurok `max X = 3` iteráció után sem konvergált.

Teendők **sorban**:
1. Írd a `analyze-report.md` státuszát `FAIL`-re, a `Hurok:` mezőbe `<max X>/<max X> (feladva)`, és a Hurok-naplóba a megrekedt állapotot (mely `Must Fix` maradt, melyik fázisnál).
2. **Hagyd rajta a `[analyze-loop]` markert** az érintett dokumentumokon — így a felhasználó (vagy egy következő session) látja, hogy a hurok nyitotta vissza őket, és hol akadt el.
3. **Egyetlen lezáró commit** — a *Fázis-záró commit* szekció eljárása szerint, **kötelező** (a FAIL ág sem kivétel):
   ```bash
   git add specs/cycle-NN-<cycle-name>/
   git commit -m "cycle-NN: 05-analyze"
   ```
4. Összefoglalás + kérdés a felhasználónak: foglald össze, melyik `Must Fix` nem oldódott meg és miért (pl. ismétlődő ambiguitás, amit a fixer nem tud eldönteni), és kérdezd meg, hogyan folytassák (kézi javítás az adott fázisban / döntés egy nyitott kérdésre / a `conventions.md` felülvizsgálata súlyos konvenció-ütközésnél).
   > **A válasz végén helyezd el az `analyze-report.md` közvetlen, kattintható linkjét.**

<!-- INCLUDE:shared/phase-commit.md -->

A fenti blokkban a `<FÁZIS-TAG>` értéke ebben a fázisban: **`05-analyze`**. A commit a **hurok lezárásakor, egyszer** történik — de **minden lezáró ágon** (PASS és `max X` FAIL egyaránt). A hurok alatt nincs köztes commit; a köztes állapotot a `[analyze-loop]` marker, a `*-questions.md` fájlok és a Hurok-napló őrzi.

> **Megállási szabály (PC1):** ha az `analyze-report.md` státusza `PASS` vagy `FAIL`, de a fázis-záró commit hiányzik (VCS-es projekt, `git log -1 --oneline` nem a `cycle-NN: 05-analyze` commitot mutatja), **STOP** — először commitolj, csak utána zárd le a fázist és add meg a következő lépést.

---

## Kérdezési szabályok

- Csak **egy** kérdést tegyél fel egyszerre, várd meg a választ.
- A hurok közbeni kérdéseknél használd a **fázis-fejléces kérdésformátumot** (`[FÁZIS · iter n/max X · FÁZIS/Knn]`).
- Minden alkalommal, amikor kérdést teszel fel vagy jóváhagyást kérsz, a válaszod végén kötelezően helyezz el egy közvetlen, kattintható markdown linket az érintett fájlra.