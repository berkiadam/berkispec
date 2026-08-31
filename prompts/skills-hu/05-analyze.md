---
phase: 05
name: bs-analyze
description: "berkispec - 05. Használd az implementáció előtt (Phase 05), ha a tasks.md 'Implementálásra kész'. Kereszt-fázisos konzisztencia-kapu a spec.md/plan.md/tasks.md között: subagentekkel (analyzer, *-fixer) azonosítja és automatikusan javítja az ellentmondásokat. Létrehozza az 'analyze-report.md'-t (PASS/FAIL)."
prerequisites:
  - "specs/cycle-NN-<name>/tasks.md státusz: <status:ready_for_implement>"
output:
  - "specs/cycle-NN-<name>/analyze/analyze-report.md (PASS / FAIL)"
  - "specs/cycle-NN-<name>/analyze/analyze-task.md (a felhasználó által jóváhagyott javítási lista)"
prev: bs-write-tasks
next: bs-implement
subagents:
  - "agents/analyzer.md"
  - "agents/analyzer-exec.md"
  - "agents/spec-fixer.md"
  - "agents/plan-fixer.md"
  - "agents/tasks-fixer.md"
shared:
  - "shared/phase-commit.md"
scripts:
  - "scripts/analyze-gate-check.py"
---
# 05 — Analyze (kereszt-fázisos konzisztencia ellenőrzés + önjavító hurok)
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

Spec driven development-ben fejlesztünk szoftvert. A fejlesztés ciklusokra van bontva. Minden ciklus egy önállóan lefejleszthető, önállóan tesztelhető részegysége a teljes implementációnak.

Ez a folyamat **5. fázisa (0–9)**: 0-init · 1-ciklusok · 2-spec · 3-plan · 4-tasks · **5-analyze ←** · 6-implement · 7-validate · 8-doc-sync · 9-review.

---

## Cheat sheet

| Szekció | Egy mondatban |
|---|---|
| Előfeltétel | `tasks.md` = `<status:ready_for_implement>`, `conventions.md` létezik, tiszta munkafa. |
| Friss alap (BR1) | Ha a fő branch előrement a ciklus ága óta, a fázis **behozza** (rebase / merge a push-állapot szerint) az analyze ELŐTT — különben elavult fán validálna. Ha nem ment előre, az előzményhez nem nyúl. |
| Szereped | **Orchestrátor (read-only):** te magad tervezési dokumentumot nem szerkesztesz — vezényelsz, riportot írsz, kérdezel, státuszt fordítasz. |
| Mechanikus kapu | Minden futás előtt `analyze-gate-check.py` (plan-ID ↔ task-hivatkozás, marker, `⟂`, `DoD-NN`, kötelező táblák, **futtatott artefaktumok, plan-horgonyok, artefaktum-hang**) — a `<status:must_fix>` találatai a szkript célfázisával mennek a hurokba, a `## <sec:inventory>` blokkja az `analyzer-exec` bemenete (AG3), a `--emit-slices` pedig kimetszi a három szemantikai kör szeletét (SH1). |
| Analyzer diagnoszta-körök | A read-only kereszt-vizsgálatot **négy párhuzamos kör** végzi: háromszor az `agents/analyzer.md` subagent, három különböző hatókörrel (`s1-dup-underspec` = 1+3., `s2-coverage` = 2+5., `s3-conventions` = 4. kategória), plusz az `analyzer-exec` subagent (6. kategória, végrehajthatóság) — te a négy megállapítás-listát fésülöd össze (E/SH1). |
| Fixer-subagentek | A javítást a `agents/{spec,plan,tasks}-fixer.md` wrapperek végzik (= 02/03/04 fázis Fix-módja); ők írják a tervezési dokumentumokat, és visszatérés előtt **maguk futtatják a mechanikus kaput** (GS1). Ha minden `<status:must_fix>` lokális, a fixerek **egyetlen üzenetben, párhuzamosan** indulnak (LF1). |
| Élő riport (AR1) | Az `analyze-report.md` **a legelső diagnózis után azonnal** elkészül `IN_PROGRESS` státusszal, emberi nyelvű pipálólistával (*mi a baj · miért blokkol · célfázis · állapot*) — nem a hurok végén. A hurok minden lépése frissíti, így a felhasználó látja, min dolgozik éppen a fázis. |
| Triázs-megállás (TR1) | **Minden diagnoszta-kör után** a hurok megáll, és a felhasználó egyetlen kérdésben eldönti, mely **új** `<status:must_fix>` tételeket javítsuk. A jóváhagyottak az `analyze-task.md`-re kerülnek, az elvetettek `elvetve (triázs)` állapottal a riportba — és nem blokkolják a `PASS`-t. A tisztán mechanikus (kapu-)tételek kérdés nélkül kerülnek fel a listára. |
| Javítási lista (`analyze-task.md`, TR1) | A fixerek **kizárólag** az `analyze-task.md` nyitott tételein dolgoznak. Egy kör közben a hurok **nem kérdez** — végigmegy a listán; az új körben talált új tételek a következő triázsban kerülnek rá. |
| Analízis-mappa (AD1) | Az analízis **minden** fájlja a `specs/cycle-NN-<cycle-name>/analyze/` almappában él: `analyze-report.md`, `analyze-task.md`, `slices/` és minden segédfájl. |
| Eredmény | `analyze-report.md` PASS vagy FAIL, súlyossági besorolással + <sec:loop_log>. |
| Egy analyzer-kör / iteráció | Minden kör **teljes a saját hatókörében**, és a `PASS`-hoz mind a négynek le kell futnia; a 2. körtől megkapja az előző `<status:must_fix>` listát (verifikáció) és a `git diff`-et (navigáció) — de nem szűkíti rá magát (D10). A downstream re-deriválás **feltételes** (D11). |
| FAIL | **Önjavító hurok indul:** legkorábbi érintett célfázis → fixer-subagent → downstream re-deriválás (`02→03→04`) → újra-analyze, amíg PASS — `max X = 3` iterációval. |
| Kérdés-megállás | Ha a fixer nyitott kérdést jelentett: az orchestrátor (te) kérdezed a felhasználót `FÁZIS/Knn` fejléccel, beírod a választ, újraindítod a fixert — a hurok **folytatódik** (nem hiba). |
| PASS | Tovább a 06-implement fázisra. Commit: a hurok végén egyetlen `cycle-NN: 05-analyze`. |
| Fázis-záró commit | **Kötelező, minden lezáró ágon** (PASS és FAIL egyaránt) — a *Fázis-záró commit* szekció eljárása szerint (PC1). Commit nélkül a fázis nincs lezárva. |

---

## Szereped: orchestrátor (read-only invariáns)

A `05-analyze` egy **vezénylő** fázis. Két dolgot tarts észben végig:

1. **Te magad nem szerkesztesz tervezési dokumentumot** (`spec.md`, `plan.md`, `tasks.md`). Minden tartalmi javítást a fixer-subagentek (= a 02/03/04 fázisok Fix-módja) végeznek. Az egyetlen fájl, amit te írsz, az `analyze-report.md`, és az egyetlen közvetlen módosításod a tervezési dokumentumokon a **státusz-mező fordítása** (a `[analyze-loop]` marker fel- és levétele, lásd lent).
2. **A read-only diagnózis a diagnoszta-köröké** (`analyzer` × 3 hatókör + `analyzer-exec`). Te az összefésült megállapítás-listát olvasod és döntesz PASS / FAIL-ról, majd FAIL esetén levezényled a javító hurkot.

Így a fázis felelőssége tiszta: **diagnózis (analyzer) → vezénylés (te) → javítás (fixerek)**, mindegyik a maga helyén.

---

## Az analízis mappája (AD1)

Az analízis során keletkező **minden** fájl a ciklus `analyze/` almappájába kerül — a ciklus gyökere a tervezési dokumentumoké (`spec.md`, `plan.md`, `tasks.md`, `*-questions.md`), nem az analízis melléktermékeié:

```
specs/cycle-NN-<cycle-name>/
├── spec.md · plan.md · tasks.md · *-questions.md      ← a tervezési dokumentumok (a fixerek írják)
└── analyze/
    ├── analyze-report.md    ← a diagnózis és az audit-nyom (te írod)
    ├── analyze-task.md      ← a jóváhagyott javítási lista, a fixerek munkalistája (te írod)
    └── slices/              ← a kapu `--emit-slices` kimenete; `.gitignore`-ral rejti magát
```

Ha egy analízis-segédfájlra szükséged van (jegyzet, köztes lista), az is **ide** kerül — a ciklus gyökerébe analízis-fájl nem kerülhet. A fázis-záró `git add specs/cycle-NN-<cycle-name>/` az egész almappát stage-eli; a `slices/` kimarad, mert elrejti magát.

> **Régi ciklusok:** ha a `analyze-report.md` a ciklus **gyökerében** áll egy korábbi futásból, **mozgasd át** (`git mv`) az `analyze/` mappába a fázis elején, és a riportban jegyezd meg egy sorban. Két helyen élő riport a folytatás-logikát (és a `06` kapuját) is megzavarná.

---

## <field:f_prerequisite>

0. **Ciklus-beazonosítás:** ha a felhasználó megadott ciklust/fájlt, azt használd; különben a legfrissebb `specs/cycle-*` mappát ajánld fel megerősítésre — <!-- INCLUDE:lang/common.md#ciklus-beazonositas --> — és várj a válaszra, mielőtt továbblépsz.

1. **`conventions.md` létezés-ellenőrzés:** olvasd be a projekt gyökerében a `conventions.md`-t. Ha nem létezik, **STOP** — jelezd a felhasználónak, hogy térjenek vissza a `00` projekt inicializálás fázishoz, és ne folytasd.

2. **Tasks státusz:** olvasd be a `specs/cycle-NN-<cycle-name>/tasks.md` státuszát. **Ha nem `<status:ready_for_implement>`, STOP** — a task lista még nem zárult le. Jelezd, és térjenek vissza a `04` tasks fázishoz. (Kivétel: ha a státusz `<status:ready_for_implement> [analyze-loop]` markert visel, egy korábbi analyze-hurok szakadt meg — lásd „Folytatás megszakított futás után".)

3. **Munkafa-ellenőrzés (csak VCS esetén):** futtasd: `git status --short`. Ha van commitálatlan változtatás:
   - Listázd ki az érintett fájlokat.
   - Jelezd: *"Az analízis hurok módosíthatja a tervezési dokumentumokat; a tiszta munkafa megkönnyíti a visszakövetést."*
   - Kérdezd meg: *"Commitáljam ezeket most, vagy folytassam?"* — egy kérdés, várj a válaszra, majd folytasd. (No-VCS projektben kimarad.)

4. **🔴 Friss alap (BR1 — csak VCS esetén, feltételes):** az analyze értéke abból jön, hogy a tervet a **tényleges** kódbázishoz méri (horgonyok `path:sor`, futtatott artefaktumok létezése, plan↔kód konzisztencia). Ha a fő branch időközben előrement (másik ciklus merge-elődött, hotfix érkezett), akkor egy elavult fán validálnál — a zöld eredmény hamis. Ellenőrizd:

   ```bash
   git fetch origin
   git log --oneline HEAD..origin/main
   ```

   _Remote nélküli (csak lokális) repóban az `origin/main` helyett a lokális `main`-nel dolgozz, `git fetch` nélkül. A `main` helyére a `conventions.md` `## <sec:cv_git_conventions>` **<field:f_main_branch>** mezője kerül._

   _A parancsban **szándékosan nincs `$( )` behelyettesítés**: a `HEAD..origin/main` ugyanazt a commit-halmazt adja, mint a `merge-base`-es alak, viszont több CLI (pl. Antigravity/Gemini) a parancs-behelyettesítést biztonsági okból nem engedi allowlistelni — az ilyen sor minden futásnál engedélyt kérne._

   - **Üres lista** → nincs teendő, folytasd. (A párhuzamos tervezési ablakban ez a normál eset: amíg a másik ciklus nincs merge-elve, a fő branch nem mozdul.)
   - **Nem üres** → hozd be a fő branch-et a ciklus ágába **az analyze ELŐTT**:
     - a branch **nincs pusholva / nincs rá PR** (`git rev-parse --verify origin/feature/cycle-NN-<cycle-name>` hibát ad) → `git rebase origin/main`,
     - a branch **pusholva van vagy PR nyitva** → `git merge origin/main` (a rebase force-push-t igényelne).

     A behozás **előtt** jegyezd fel a ciklus ágának csúcsát (`PRE=$(git rev-parse HEAD)`). Egy sorban jelezd, mit hoztál be (`git log --oneline` a behozott commitokról) — **külön engedélyt ne kérj**, a ciklus saját ágán dolgozol, ez nem destruktív. **Konfliktus esetén STOP**: listázd az ütköző fájlokat, és kérj döntést; a generált doksit (`docs-generated/`) és a `specs/test-conventions.md`-t **ne** kézzel oldd fel — az a `08` dolga.

   - **A behozás után állítsd elő a REBASE-FÁJLLISTÁT (BR1/a):**
     ```bash
     git diff --name-only "$PRE" HEAD -- . ':(exclude)specs/*'
     ```
     Ez a másik ciklusból/hotfixből érkezett **forrás-, teszt- és konfigfájlok** listája. Ha nem üres, **mind a négy diagnoszta-kör bemenetébe** be kell kerülnie (lásd *„A négy diagnoszta-kör"* → **Rebase-fájllista**). Ha üres (csak más ciklusok `specs/` mappái jöttek be), nincs teendő.
     _Fájllistát adj át, **ne a teljes diffet** — a subagent a szükséges részleteket maga olvassa be (AG3)._

   > **Ne rebase-elj feltétel nélkül.** Ha a fenti lista üres, a branch előzményéhez **nem nyúlsz** — az analyze önjavító hurokban többször is lefuthat, és a fölösleges előzmény-átírás pusholt ágon force-push-t provokálna.

   **Miért itt:** ez a fázis az **alap-konzisztencia kapuja**. A `06` párhuzamos-ciklus kapuja (PW2) ezért nem külön rebase-lépést ír elő, hanem azt, hogy a `06` előtt legyen **friss `05` `PASS`** — a behozást maga az `05` végzi el.

---

## Folytatás megszakított futás után

**A folytatás első analyze-futása verifikációs lista NÉLKÜL indul** — nem tudhatod, hol szakadt meg a javítás, így nincs értelmes „előző kör". A futás — mint mindig — teljes, és a mechanikus kapu (0. lépés) is fut.

Az analyze **diagnózisa** read-only, de a hurok már módosíthatta a tervezési dokumentumokat. A folytatást a `[analyze-loop]` státusz-marker, a `*-questions.md` nyitott kérdései, az `analyze/analyze-task.md` nyitott tételei és az `analyze-report.md` Hurok-naplója együtt teszi rekonstruálhatóvá. **Az `analyze-task.md` a legerősebb horgony:** ami rajta van, azt a felhasználó már jóváhagyta — folytasd kérdés nélkül; ami az `Elvetett tételek` szekciójában van, azt ne nyisd vissza. Döntési fa — **ebben a sorrendben**:

```
1. Visel valamelyik tervezési dokumentum (spec.md / plan.md / tasks.md)
   `[analyze-loop]` státusz-markert?
   → Igen → a hurok megszakadt. NE kezdj új analízist elölről.
     a/0) Olvasd be az analyze/analyze-task.md-t: a nyitott [ ] tételek a
        jóváhagyott, még el nem végzett munka. Ezekkel folytasd, ÚJ triázs nélkül.
     a) Olvasd be az analyze-report.md <sec:loop_log> szekcióját:
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
   → Ha státusza IN_PROGRESS: a riport ÉLŐ (AR1), nem hibás — a benne lévő
     tételek valósak, csak a hurok nem futott végig. NE dobd el és ne írd felül:
     az `Aktuális lépés:` mezőjéből és a tételek `Állapot:` mezőjéből olvasd ki,
     hol állt meg, és onnan folytasd. Ha a `Triázs (TR1)` mező ki van töltve,
     a triázs megtörtént: ne kérdezd meg újra, és az elvetett tételeket ne nyisd vissza.
   → Ha a report félbeszakadtnak tűnik (nincs minden kategória kitöltve), a státusza
     NEM IN_PROGRESS, és nincs marker: töröld a részleges riportot, és kezdd elölről
     az analízist.

3. Nincs analyze-report.md és nincs marker.
   → Kezdd az analízist az "Feladatod" szerint.
```

---

## Feladatod

Ellenőrizd, hogy a ciklus tervezési dokumentumai (`spec.md`, `plan.md`, `tasks.md`) **konzisztensek egymással és a `conventions.md`-vel**, mielőtt az implementáció megkezdődne — és ha nem, **vezényeld le a javításukat** egy önjavító hurokban, amíg konzisztenssé válnak.

**Ne implementálj semmit.** Ez a sanity check (és szükség esetén javító hurok) az implementáció előtt.

A diagnózis **5 kategóriában** keres problémát (a három szemantikai `analyzer`-kör végzi, hatókör szerint elosztva — lásd „A négy diagnoszta-kör"):

1. **Duplikációk** — ugyanaz a döntés a plan-en belül többször; a `tasks.md` újra leírja a plan teszteset-lépéseit; redundáns task. **A spec kidolgozott artefaktumának szó szerinti átvétele a plan-be NEM duplikáció** (KX3) — az a kötelező önhordóság.
2. **Ambiguitás** — vágy fogalmak, hiányzó mérőszámok, nem mérhető elfogadási feltétel.
3. **Alulspecifikáció** — hiányzó elfogadási feltétel, meghatározatlan komponens, taskhoz nem rendelhető plan-szekció.
4. **Konvenció-ütközések** — a `conventions.md`-vel szembeni eltérés (tech stack, naming, teszt eszköz, merge stratégia, struktúra).
5. **Lefedettségi hiányok** — követelmény ↔ task egymáshoz rendelés: van-e spec-követelmény, amelyhez nem tartozik task, vagy task, amely nem vezethető vissza a planre.

---

## Kontextus betöltési szabályok

- A kereszt-vizsgálat sok fájl együttes olvasását igényli — **kötelező mind a négy diagnoszta-kör indítása, egyetlen üzenetben, párhuzamosan** (E/SH1): háromszor az `analyzer` subagent (hatókörönként `s1-dup-underspec` = 1+3., `s2-coverage` = 2+5., `s3-conventions` = 4. kategória) és egyszer az `analyzer-exec` subagent (6. kategória). Mindegyik **kizárólag a strukturált megállapítás-listát adja vissza** (a nyers fájltartalom nem terheli a fő kontextust).
- A rendszerpromptjukat a platform **telepített agent-definíciója** adja (`analyzer`, `analyzer-exec`) — ezeket a neveken hívd, ne keresd őket fájlként a projektben. A három szemantikai kör **ugyanazt az `analyzer` definíciót** használja; a különbség a hatókör, amit az indító üzenetben adsz meg.
- **Add át a kapu kimenetének megfelelő részét minden körnek, szó szerint:**
  - `analyzer-exec` → a **`## <sec:inventory>`** (`<status:mk_artifact>` / `<status:mk_anchor>` / `<status:mk_tone_suspect>` / `<status:mk_test_promise>` / `<status:mk_destructive>`, AG3): ez váltja ki a repó- és dokumentum-felderítést, ami a 6. kategória fő költsége volt;
  - `s2-coverage` → a **`## <sec:coverage_matrix>`** (AG4): a `DoD-NN → [P-…] → task` lánc készen, hogy ne vezesse le újra;
  - **mindhárom szemantikai kör** → a **saját szeletének útvonala** (`analyze/slices/<hatókör>.md`, SH1) **és a hatóköre neve**. Az útvonalat add meg, **ne a szelet tartalmát**: a szeletelés egész célja az, hogy a négyes szövege ne a fő kontextuson keresztül érkezzen a subagenthez.
- A négy kör kimenetét te fésülöd össze (lásd „A négy diagnoszta-kör"), és ez alapján döntesz PASS / FAIL-ról.

  > **🔴 Ha valamelyik diagnoszta-kör nem fut le, vagy nem ad megállapítás-listát:** **ne végezd el csendben magad a kereszt-vizsgálatot** — a fázis egész értéke az, hogy a diagnózis **független** a vezénylőtől. A teendőt a **hiba típusa** dönti el — ne mérlegelj, nézd meg a hibaüzenet szövegét:
  > - **Platform-korlát** (a szövegben kvóta/keret/limit szerepel — pl. „usage limit", „quota exceeded", „reached its usage limit", vagy egy keret-reset dátum): **NE próbáld újra.** A második hívás determinisztikusan ugyanabba fut. Ugorj azonnal a STOP + humán ágra, és a kérdésbe **másold be a hibaüzenetet szó szerint** (a reset-dátummal együtt) — a döntés (admin-engedély, várakozás a resetig, másik modell-pool) a felhasználóé.
  > - **Minden más hiba** (időtúllépés, egyszeri összeomlás, üres válasz): próbáld újra **egyszer**. Ha csak az **egyik** kör bukott, kizárólag **azt** indítsd újra — a másik három megállapítás-listáját ne dobd el.
  >
  > Ha így sem futtatható: **STOP + humán** — kérdezd meg, hogy próbáljam-e újra, vagy végezzem el a hiányzó kategóriákat közvetlenül az `analyzer` / `analyzer-exec` szempontjai szerint a fő ágensben. A hiányzó kör **hatókörét nevezd meg** a kérdésben (melyik kategóriák maradtak diagnózis nélkül).
  >
  > **Ha a fallback ágra mész, a diagnózis eredetét KÖTELEZŐ jelölni.** A fő ágens más modellen és szűkebb kontextusban dolgozik, mint a subagent, ráadásul ő maga a vezénylő — tehát a diagnózis **elveszti a függetlenségét**, és rendszeresen gyengébb lelet. Az `analyze-report.md` fejlécébe kerüljön egy sor: **Diagnózis:** fő ágens (fallback) — a(z) <subagent> nem volt futtatható: <ok>. Egy így született PASS **nem teljes értékű** — írd oda, hogy a subagent-diagnózis pótlása ajánlott.
- A javító fixer-subagenteket szintén Task tool subagent-ként indítod, a saját wrapper-promptjukkal (`agents/spec-fixer.md`, `agents/plan-fixer.md`, `agents/tasks-fixer.md`) — lásd „Az önjavító hurok".
- **A `*-input-from-prev.md` fájlok (IP1) is bemenetek:** a subagent beolvassa a ciklus mappájában lévő `spec-`/`plan-`/`tasks-input-from-prev.md` fájlokat (amelyik létezik), és **nyitott `[ ]` tételt lefedettségi hiányként** jelez. Indoklás: egy nyitott tétel azt jelenti, hogy egy korábbi fázis átadott egy információt, amit a fogyasztó fázis se be nem épített, se el nem vetett — ez ugyanolyan rés, mint egy task nélküli követelmény.

  > **A `validate-input-from-prev.md`-t az 05 NEM vizsgálja:** annak a fogyasztója a 07, ami az analyze után fut — ott jogosan nyitott még.
  >
  > **A hurok fix-módjai (a fixer-subagentek) ezeket a fájlokat továbbra sem olvassák és nem írják** (IP1/6). Ez a check tehát **diagnózis**: a `<status:must_fix>` a `spec.md`/`plan.md`/`tasks.md` hiányosságát nevezi meg (mi maradt ki), nem az átadó fájl kipipálását kéri. A pipálás a normál (nem fix-módú) fázis-futás dolga.

---

## Súlyossági besorolás

Minden megállapítás **<status:must_fix>** vagy **<status:suggestion>**:

- **<status:must_fix>** = blokkolja az implementációt (a hibás alapra épülő implementáció kockázatos): valódi duplikáció, lefedettségi rés, konvenció-ütközés, meghatározatlan komponens, nem eldönthető elfogadási feltétel.
- **<status:suggestion>** = nem blokkol, csak javasolt finomítás (átfogalmazás, kisebb tisztázás).

**PASS feltétele:** nincs `<status:must_fix>` megállapítás. Ha csak `<status:suggestion>`-ök vannak, az eredmény PASS (a suggestion-öket a felhasználó eldöntheti, de nem indítanak hurkot).

> **Triázs mellett (TR1):** a `PASS` feltétele pontosabban az, hogy ne maradjon **el nem vetett** `<status:must_fix>` tétel. A felhasználó által elvetett tétel a riportban `elvetve (triázs)` állapottal **megmarad** (audit-nyom), de nem blokkol és nem indít hurkot.

---

## 0. lépés — mechanikus kapu (`analyze-gate-check.py`) — MINDEN analyze-futás előtt

A gépiesen eldönthető ellenőrzéseket **nem az `analyzer` subagent végzi**, hanem egy szkript — determinisztikusan, olcsón, hamis riasztás nélkül:

<!-- INCLUDE:shared/python-cmd.md -->

```bash
python3 <platform-scripts-mappa>/analyze-gate-check.py specs/cycle-NN-<cycle-name> --emit-slices
```

_(A projekt gyökeréből futtatva a `--repo-root .` és a `--conventions conventions.md` alapérték jó. Ha a `conventions.md` máshol van, add meg: `--conventions <útvonal>` — enélkül a `G1` kapu-konfiguráció check kimarad.)_

**Mit fed le:** plan-ID formátum/egyediség (P1), task→plan hivatkozás megléte (P2), nem létező ID-ra hivatkozás (P3), ID task nélkül (P4), sorszámos hivatkozás (P5), marker minden taskon (T1), `[OPS]` repo-fájlon (T2), státusz-frissítő task (T3), `⟂` szimmetria (T4), kitöltetlen placeholder a `[CHECK]`/`[OPS]` parancsban (T5), `DoD-NN` hiány/duplikáció (D1), `DoD-NNb` alakú utólagos azonosító (D2), kötelező táblák megléte (S1/S2) — **és a 6. kategória gépies rétege (AG3):** futtatott artefaktum létezése / létrehozó task (A1 = 6.a), plan-`path:sor` horgony feloldása (A2 = 6.g fájl-szintje), horgony-sorszám érvényessége (A2b, javaslat), artefaktum-hang kemény padlója (A3 = 6.h `🔴`/„Tilos", javaslat) — **továbbá:** a spec kidolgozott artefaktumainak átvétele (`V1`) és a teszt-szekciók terjedelme (`V2`, KX3), a **teszt-cél környezet** egyezése (`EV1`–`EV5`: van-e deklarált cél-környezet, megmondja-e minden futtatási kategória, hol fut, a parancsban van-e a cél-host, van-e elérhetőségi probe, és nem mutat-e nem-lokális kategória localhostra), a plan **teszt-forgatókönyveinek** végrehajthatósága (`TS1`–`TS6`: van-e `TS-NN` blokk, teljes-e, konkrét-e lépésenként a hívás és az elvárt eredmény, placeholder-mentes-e, kétirányú-e a `DoD-NN` lefedettség, hézagmentes-e a sorszámozás), az útvonal-formátum (`R1`, RP1) és a horgony-formátum (`A2c`, javaslat), valamint a **kapu-konfiguráció együtt mozgása** (`G1`, GC1: a ciklus a riport-struktúrát érinti, de a `conventions.md` `## <sec:cv_test_reporting>` táblája nem mozdul → a 07 TR3 kapuja a régi helyen keresne).

**A kimenet négy blokkja:**
- **`## <status:must_fix>`** — soronként `[kód] (célfázis: NN) üzenet`. Mindegyik `<status:must_fix>`, a szkript célfázisával — vedd fel őket az `analyze-report.md` listájába **szó szerint**. Ezeket ne kérdőjelezd meg és ne értékeld újra: gépi ellenőrzés eredményei.
- **`## Javaslatok`** — nem blokkolnak, nem indítanak hurkot; a riport `Suggestions` szekciójába kerülnek.
- **`## <sec:inventory>`** — **nem megállapítás, hanem az `analyzer-exec` BEMENETE.** A horgonyzott sorok szövegét, a futtatott artefaktumok állapotát és az ítéletet igénylő hang-találatokat tartalmazza. **Add át szó szerint az `analyzer-exec` subagentnek** — ettől nem kell a repóban `Grep`/`Glob` köröket futtatnia (ez a 6. kategória fő költsége volt).
- **`## Szeletek` (SH1)** — **nem megállapítás, hanem a három szemantikai kör BEMENETE.** A `--emit-slices` a ciklus mappájába írja a szeleteket (`analyze/slices/s1-dup-underspec.md`, `analyze/slices/s2-coverage.md`, `analyze/slices/s3-conventions.md`); mindegyik a tervezési dokumentumok szó szerinti kimetszése, épp az adott kör kategóriáihoz. A körnek **az útvonalat add meg, ne a tartalmat.** A mappa `.gitignore`-ral rejti magát, tehát a fázis-záró commit nem stage-eli, és a munkafa-ellenőrzést sem zavarja.

**Kilépő kód:**
- **`0`** → nincs blokkoló mechanikus megállapítás (javaslat, leltár és szelet lehet a kimenetben); indítsd a négy diagnoszta-kört, mindegyiket a rá tartozó blokkal.
- **`1`** → van `<status:must_fix>`; ugyanígy indítsd a négy kört, és az összes megállapítás-listát együtt kezeld a hurokban.
- **`2`** → használati hiba (hiányzó ciklusmappa vagy dokumentum) → STOP, jelezd a felhasználónak.

**A kapu minden iterációban fut** (a javítás után is) — így a mechanikus regresszió nem tud átcsúszni.

> **Az `analyzer` ezekre már nem kap külön feladatot.** Ha mégis ilyen megállapítást ad vissza, az duplikátum: a szkript kimenete az irányadó.

---

## FAIL — kategória → célfázis leképezés

Egy olcsóbb LLM-nek konkrét célt kell adni, nem „vissza a megfelelő fázisba". A `<status:must_fix>` megállapítás kategóriája határozza meg a javító célfázist (= melyik fixer-subagentet indítod):

| Kategória | Célfázis (fixer) | Indok |
|---|---|---|
| Duplikáció | 03 (tervezési szintű), 04 (task-szintű) | a redundancia forrásához |
| Ambiguitás | 03 (technikai döntés), 02 (viselkedési — ritka) | ahol a fogalmat tisztázni kell |
| Alulspecifikáció | 03 (meghatározatlan komponens), 02 (hiányzó elfogadási feltétel) | a hiányzó döntés szintjére |
| Konvenció-ütközés | 03 (enyhe), 00 (súlyos — `conventions.md` felülvizsgálat) | összhangban az SK4 logikájával |
| Konvenció-ütközés, ahol a ciklus **szándékosan** változtat konvenciót (GC1) | **03** — a plan tervezze meg a `conventions.md` frissítését (+ **04** a taskra) | a döntés már megvan; ez végrehajtás, nem konvenció-felülvizsgálat, tehát nem megy vissza a `00`-ra |
| Lefedettségi hiány | 04 (követelmény ↔ task újrarendelés) | a task lista a hiányos |
| Lefedettségi hiány — nyitott `*-input-from-prev.md` tétel (IP1) | a **fogyasztó** fázis (02 / 03 / 04 a fájl szerint) | ott maradt ki az átadott infó beépítése |
| Plan-hivatkozás hibája (PID1): hiányzó / nem létező `[P-…]` / sorszámos hivatkozás / `[P-…]`-hoz nincs task | **04** | a `tasks.md` hivatkozásai romlottak el |
| Végrehajtható plan-szekciónak nincs `[P-…]` azonosítója (PID1) | **03** | az ID kiadása a plan dolga |
| Kitöltetlen placeholder egy `[CHECK]`/`[OPS]` parancsban (`T5`) | **04** | a `06` szó szerint adja ki a parancsot: találgatnia kellene |
| Scope-túlnyúlás (SC1): plan-képességnek nincs spec-forrása | **02** (ha kell a képesség → DoD-pont), **03** (ha nem kell → kivétel + `<sec:out_of_scope>`) | elfogadási feltétel nélkül nem fejleszthető |
| <sec:config_lifecycle> (KF1) hiányos vagy hiányzik | **03** | a paraméter propagációja terv-kérdés |
| Spec-teszteset nem képződött le plan-tesztesetre (TP1) / hiányzó környezet-felkészítés (TP3) | **03** | a `test-runner` csak a plant olvassa |
| Kötelező tábla hiánya (`<sec:spec_coverage>`, `<sec:reverse_coverage>` → 03; `<sec:plan_coverage>` → 04) | a tábla gazdája | a kimaradt tábla = kihagyott kapu |
| Hiányzó/duplikált `DoD-NN` azonosító | **02** | a 07 per-item számlálója erre épül |
| Kidolgozott spec-artefaktum csonkítva / összevonva a plan-ben (KX3 — `V1`/`V2` vagy szemantikai) | **03** | a `test-runner` a spec-et nem olvassa: ami itt kimarad, nem fut le |
| Teszt-forgatókönyv hiányzik vagy nem végrehajtható (`TS1`–`TS6`) | **03** | a `plan.md` önhordó: a `test-runner` és a kézi tesztterv is csak ebből dolgozik |
| A teszt nem a ciklus cél-környezetén fut (`EV1`–`EV5`) | **03** | egy lokális célra futó teszt zöld lesz akkor is, ha a telepített komponens el sem indult |
| Útvonal-formátum (RP1 — `R1`) | a dokumentum gazdája: **02 / 03 / 04** | abszolút/gép-specifikus útvonal más gépen és CI-ben értelmetlen |
| Kapu-konfiguráció nem mozog a struktúrával (GC1 — `G1`) | **03** (+ **04** a taskra) | a `conventions.md`-t olvasó kapu (TR3, Sonar) a régi értékkel futna → a 07 bukik |

**Legkorábbi érintett fázis nyer:** ha több kategória is FAIL és különböző célfázisokra mutat, a hurok a **legkorábbi érintett fázisra** ugrik (02 < 03 < 04), majd onnan deriválja le újra a downstream fázisokat — különben a későbbi fázisok hibás alapra épülnének. (Súlyos konvenció-ütközés `00`-ra mutat: ez emberi döntést igényel a `conventions.md` szintjén — ilyenkor a hurok megáll és kérdez, nem javít automatikusan.)

---

## Élő riport (AR1) — a riport a diagnózis után azonnal elkészül

A fázis legdrágább mellékhatása az volt, hogy a felhasználó a hurok teljes futása alatt **nem látta, mi a baj**: a lemezen csak az `analyze/slices/` bemeneti szeletek jelentek meg (gitignore-olt, szó szerinti kimetszések a tervezési dokumentumokból), a `analyze-report.md` pedig csak a hurok **végén** született meg. Egy megszakadt vagy elhúzódó hurok így semmit nem hagyott maga után, amit el lehet olvasni.

**A szabály:** az `analyze-report.md` az **első összefésült diagnózis után azonnal** elkészül — még az **első fixer indítása előtt** —, `IN_PROGRESS` státusszal, és a hurok minden lépésénél frissül. Ez a te dolgod (orchestrátor), és nem sérti a read-only invariánst: a riport nem tervezési dokumentum.

**Mikor írod / frissíted:**

| Pont | Mit írsz a riportba |
|---|---|
| Az első diagnózis összefésülése után (a hurok előtt) | Teljes fájl `IN_PROGRESS` státusszal: `Összefoglaló`, a **`Javítandó tételek`** pipálólista minden egyesített `<status:must_fix>` tétellel, `Suggestions`, `Végrehajthatósági leltár`, a két generált tábla. Ez akkor is elkészül, ha a diagnózis PASS-t adott (üres Must Fix listával). |
| Fixer indítása előtt (hurok 2–3. pont) | `Aktuális lépés:` = melyik fixer melyik azonosítókon fut; az érintett tételek `Állapot:` mezője `javítás alatt (iter <n>)`. |
| Kérdés-megállásnál (hurok 4. pont) | A tétel `Állapot:` mezője `kérdés (<FÁZIS>/K<nn>)`, és a `Aktuális lépés:` jelzi, hogy a hurok a felhasználóra vár. |
| Újra-analyze után (hurok 6. pont) | A megoldott tételek sora `[x]`-re vált, `Állapot:` = `megoldva (iter <n>)`; az új megállapítások **új** tételként kerülnek a lista végére; a Hurok-napló megkapja az iteráció bejegyzését. |
| A hurok lezárásakor | `IN_PROGRESS` → `PASS` vagy `FAIL`, `Aktuális lépés:` = `lezárva`, a `Hurok:` mező kitöltve. |

**Amit a lista tételéről ki kell mondani.** A riportot **ember olvassa**, aki nem tartja fejben a négy dokumentumot — a kategória neve (`lefedettségi hiány`, `konvenció-ütközés`) ezért önmagában nem magyarázat. Három mező kötelező:

- **`Az ellentmondás`** — *mi mond ellent minek.* Nevezd meg **mindkét oldalt**, mindkettőt a saját `fájl:hely` hivatkozásával: mit állít az egyik dokumentum, és mit a másik. Egyoldalú hiánynál (nincs task egy `DoD-NN`-hez, nincs elfogadási feltétel egy komponenshez) az egyik oldal a **hiány**: mondd meg, mi hiányzik, és melyik dokumentum melyik pontja várná el.
- **`Miért blokkol`** — *mi romolhat el az implementációban*, ha így marad. Ez különbözteti meg a `<status:must_fix>`-et a `<status:suggestion>`-től.
- **`Hogyan lenne helyes`** — *a célállapot.* Egy-két mondat arról, mit kell mondania a dokumentumnak a javítás után, hogy a négyes konzisztens legyen. Ez az a mező, amitől a riport használható: enélkül a felhasználó tudja, hogy baj van, de nem tudja, mi lenne a jó.

> **A `Hogyan lenne helyes` nem a te tervezési döntésed.** Ha a célállapot **egyértelműen levezethető** a másik három dokumentumból (az egyik oldal nyilvánvalóan a lemaradt), írd le állításként — ezt fogja a fixer végrehajtani. Ha viszont **valódi döntés** kell hozzá (melyik oldal a helyes, melyik technológiai út, mekkora a teszt-hatóköre), akkor a mezőbe a **döntendő kérdés** kerül, a tétel `Állapot`-ja `kérdés (<FÁZIS>/K<nn>)`, és a kérdést a felhasználónak teszed fel — nem te döntöd el, és nem a fixer.

A tétel azonosítója (`AF-NN` / `AC-NN` / `AN-NN` / `AX-NN`) a diagnoszta-körből származik, és **szó szerint** kerül a riportba — ugyanaz, amit a fixernek átadsz, és amire a túlélés-szabály (TS) számol.

> **Tételt utólag nem távolítunk el a listáról.** A megoldott tétel `[x]`-szel, `megoldva (iter <n>)` állapottal **marad** — a lista így egyszerre pipálólista és audit-nyom. Egy elvetett tételnél az `elvetve — <indoklás>` állapot kötelező; indoklás nélkül eltüntetett tétel esetén a riport nem zárható le.

---

## Triázs-megállás (TR1) — a felhasználó dönti el, mit javítunk

A diagnózis olcsó, a javítás drága. Egy `<status:must_fix>` tétel azt mondja, hogy a diagnoszta-kör szerint az implementáció hibás alapra épülne — de hogy **megéri-e** érte fixer-kört, downstream re-deriválást és újra-analyze-t futtatni, az **a felhasználó döntése**, nem a fázisé. Enélkül a hurok rendszeresen elkölti mind a három iterációt olyan tételekre (átfogalmazás, kozmetikai eltérés, elméleti rés), amelyek mellett az implementáció simán elindulhatna.

**A szabály:** **minden diagnoszta-kör után** — az elsőt is beleértve — a hurok **megáll**, és egyetlen kérdésben a felhasználó választja ki, mely **eddig el nem döntött** tételek javítását kéri. A jóváhagyott tételek az `analyze-task.md` javítási listára kerülnek; fixert **kizárólag** az ezen szereplő nyitott tételekre indítasz.

**Egy körön belül a hurok nem kérdez** (a kérdés-megállás és a túlélés-szabály kivételével, lásd ott): végigmegy az `analyze-task.md` nyitott tételein. Amit egy későbbi kör **újként** talál, az a **következő** triázsban kerül a felhasználó elé — nem szakítja meg a futó kört.

### Mikor marad el a kérdés

- **Nincs `<status:must_fix>`** → nincs mit triázsolni, a fázis `PASS`-szal zárul.
- **Minden tétel a mechanikus kapuból jön** (P/T/S/A/C/D kódok) → **kérdés nélkül javítsd.** Ezek determinisztikusak, olcsók, és jellemzően a hivatkozási rendet állítják helyre (`[P-…]` hivatkozás, task-marker, `DoD-NN` azonosító) — épp azt, amire az implementáció és a `07` kapui támaszkodnak.
- **Már eldöntött tétel** → **soha nem kérdezed meg újra.** Ami az `analyze-task.md`-en van, azt javítjuk; amit a felhasználó elvetett, azt nem — a triázs mindig **kizárólag** azokra a tételekre kérdez, amelyek egyik listán sincsenek még rajta.
- **Nincs új tétel a körben** → nincs kérdés, a hurok megy tovább a listán.
- **Folytatáskor** (megszakadt futás): az `analyze-task.md` a horgony — a rajta lévő tételek már jóvá vannak hagyva, folytasd őket kérdés nélkül.

### Hogyan kérdezd

Egyetlen üzenet, számozott lista — tételenként egy sor és egy javaslat, semmi több:

```
[TRIÁZS · iter <n>/<max X>]
Az analízis <n> ÚJ javítandó tételt talált. Melyiket vegyük fel a javítási listára?

1. AF-02 · 03-plan · <egy mondat: mi mond ellent minek>
   Javaslat: JAVÍTSUK — <fél mondat: mi romlana el az implementációban>
2. AC-05 · 02-spec · <egy mondat>
   Javaslat: HALASZTHATÓ — <fél mondat: miért nem téríti el az implementációt>
...

Válasz: `mind` · a javítandók sorszáma/azonosítója (pl. `1,3`) · `egyik sem`
(A kiválasztottak az analyze-task.md-re kerülnek; az elvetettek nem tűnnek el:
`elvetve (triázs)` állapottal a riportban maradnak.)
```

Az **első** triázsnál a kérdés bevezetője „Melyiket javítsuk, mielőtt az implementáció elindul?"; a **későbbi** köröknél már csak az adott körben **újonnan** felfedezett tételekről kérdezel.

A válaszod végén add meg az `analyze-report.md` közvetlen, kattintható linkjét — a részletes indoklás (`Az ellentmondás` / `Miért blokkol` / `Hogyan lenne helyes`) ott olvasható, a kérdésben nem kell megismételni. Ez az **egyetlen** pont, ahol egyszerre több döntést kérsz egy üzenetben: a triázs természete a lista, nem az egyesével kérdezés.

**A javaslat a te ítéleted, és egyetlen kérdésre válaszol: eltérítené-e ez a tétel az implementációt?**
- **JAVÍTSUK** — a fejlesztő (vagy a `06` ágens) e nélkül rossz dolgot vagy semmit nem implementálna: lefedettségi rés (követelmény task nélkül), végrehajthatatlan vagy nem futtatható task (`AX-NN`), hiányzó vagy nem eldönthető elfogadási feltétel, konvenció-ütközés, a spec kidolgozott artefaktumának csonkítása (KX3), hiányzó vagy törött `[P-…]` hivatkozás.
- **HALASZTHATÓ** — a tétel a dokumentumot javítaná, nem az implementációt: átfogalmazás, duplikátum-összevonás, artefaktum-hang (6.h), útvonal-formátum (`R1`), olyan ambiguitás, aminek a gyakorlati olvasata egyértelmű.

Javaslatot adsz, nem döntést: ha a felhasználó egy `JAVÍTSUK`-ot is elvet, azt **vita nélkül** vedd tudomásul és rögzítsd.

### A válasz feldolgozása

- **A kiválasztott tételek** felkerülnek az `analyze-task.md` **Javítandó tételek** listájára (`felvéve: iter <n>`), és onnantól a hurok ezeken dolgozik. A **legkorábbi célfázist** mindig az `analyze-task.md` **nyitott** tételeiből határozod meg.
- **Az elvetett tételek** az `analyze-report.md`-ben maradnak: `[x]`, `Állapot: elvetve (triázs, iter <n>) — a felhasználó nem kérte a javítását`, és felkerülnek az `analyze-task.md` **Elvetett tételek** szekciójába is (ez a szűrés memóriája). Töltsd ki a riport fejlécének `Triázs (TR1)` mezőjét és az adott iteráció napló-bejegyzését.
- **`egyik sem` az első triázsnál** → nem indul hurok: a riport `PASS`-szal zárul (`Hurok:` = `0 / <max X> (triázs: nem indult)`), a `[analyze-loop]` marker fel sem kerül, a fázis-záró commit viszont **ugyanúgy kötelező**. Egy mondatban jelezd, hogy az implementáció ismert, tudatosan elfogadott ellentmondások mellett indul, és hogy a tételek a riportból bármikor visszavehetők. (`analyze-task.md` ilyenkor is készül — üres javítandó listával, teli elvetett listával.)
- **Az elvetett tétel többé nem nyílik vissza.** A további diagnoszta-körök **újra meg fogják találni** — az összefésülésnél (lásd „A négy diagnoszta-kör" 2.a pontja) az `analyze-task.md` **Elvetett tételek** szekciója alapján szűrd ki őket: se a triázs-kérdésbe, se a `<status:must_fix>` listára ne kerüljenek vissza. Enélkül a hurok nem tudna konvergálni, és a felhasználót körönként ugyanazzal a kérdéssel zaklatnád.

### A javítási lista: `analyze-task.md`

- **Helye:** `specs/cycle-NN-<cycle-name>/analyze/analyze-task.md` (AD1). **Szerkezetét lásd az „analyze-task.md struktúra" szekcióban.**
- **Az egyetlen írója te vagy** (orchestrátor). A fixerek **olvashatják**, de nem írják — párhuzamos fix-batch (LF1) mellett két fixer ugyanazt a fájlt írná. A bemenetüket továbbra is te adod át (a rájuk szűrt tétel-lista), a pipálás a te dolgod.
- **Mikor frissíted:** triázs után (új tételek felvétele) · fixer indításakor (`javítás alatt (iter <n>)`) · kérdés-megállásnál (`kérdés (<FÁZIS>/K<nn>)`) · újra-analyze után (a megoldott tételek `[x]` + `kész (iter <n>)`).
- **A hurok kilépési feltétele erre a listára hivatkozik:** `PASS` akkor adható, ha az `analyze-task.md`-en **nincs nyitott tétel**, és a legutóbbi diagnoszta-kör sem hozott el nem döntött `<status:must_fix>`-et.
- **A riport és a lista viszonya:** az `analyze-report.md` a **diagnózis és az audit-nyom** (mi a baj, miért blokkol, hogyan lenne helyes, mi lett vele); az `analyze-task.md` a **munkalista** (mit csinálunk, hol tart). Ugyanaz az `AF-NN` / `AC-NN` / `AN-NN` / `AX-NN` azonosító köti össze őket — az azonosítót sehol ne írd át.

---

## Az önjavító hurok (orchestrátor-hurok)

FAIL esetén **nem** adod vissza egyszerűen a vezérlést a felhasználónak. Helyette levezényelsz egy iteratív javító hurkot, amíg PASS nem lesz, vagy amíg el nem éred a `max X` korlátot.

### A hurok egy iterációja

0. **Élő riport (AR1).** Ha még nem létezik, **most hozd létre** az `analyze-report.md`-t `IN_PROGRESS` státusszal és a teljes `Javítandó tételek` pipálólistával — az első fixer indítása ELŐTT. Ha már létezik, ennél a pontnál csak az `Aktuális lépés:` mezőt és az érintett tételek `Állapot:` mezőjét vezeted át. Riport nélkül ne indíts fixert: a felhasználónak nem lenne mit elolvasnia arról, min dolgozik a hurok.
0.a **Triázs-megállás (TR1) — minden diagnoszta-kör után, az ÚJ tételekre.** A riport frissítése után, a **fixer indítása előtt** állj meg, és kérdezd meg a felhasználót, mely **eddig el nem döntött** `<status:must_fix>` tételeket vegyük fel a javítási listára (lásd „Triázs-megállás (TR1)"). A jóváhagyottak felkerülnek az `analyze-task.md`-re, az elvetettek annak `Elvetett tételek` szekciójába. Ha a körben nincs új tétel, ez a pont kimarad.
1. **Célfázis meghatározása.** Az `analyze-task.md` **nyitott** tételeinek kategóriáiból (a fenti leképezés szerint) határozd meg a **legkorábbi érintett célfázist** (02/03/04). Ez a fixer belépési pontja. A hurok minden további pontja **kizárólag az `analyze-task.md` nyitott tételeivel** dolgozik.
1.a **Lokális fix-batch — PÁRHUZAMOS indítás (LF1).** Mielőtt a szekvenciális útra lépnél, osztályozd az `analyze-task.md` nyitott tételeit:
   - **lokális** tétel = a javítása a saját dokumentumán belül elvégezhető, és **definíció szerint nincs downstream hatása**: megfogalmazás-pontosítás, ambiguitás feloldása mérőszámmal, duplikátum-összevonás, artefaktum-hang (6.h), útvonal-formátum (`R1`), elgépelés, hiányzó vagy elromlott `[P-…]` hivatkozás pótlása (`P2`/`P3`/`P5`);
   - **strukturális** tétel = minden más: lefedettségi rés, hiányzó task vagy plan-szekció, hiányzó elfogadási feltétel, konvenció-ütközés, KX3-csonkítás, végrehajthatósági `<status:must_fix>`.

   **Ha a listán KIZÁRÓLAG lokális tétel van:** indítsd az érintett fixereket **egyetlen üzenetben, párhuzamosan** — dokumentumonként egyet, mindegyiknek a rá szűrt listával. Az 5. pont downstream re-deriválása ilyenkor **kimarad** (minden fixer `downstream-hatás: nincs`-et ad). Ha valamelyik fixer mégis `van`-t jelent, kezeld normál iterációként, és a Hurok-naplóba írd be, melyik tételt minősítetted félre.
   **Ha van a listán akár egy strukturális tétel is:** a 2. ponttól a szokásos szekvenciális út következik (legkorábbi célfázis → downstream). Az érintett dokumentum **lokális tételei ilyenkor ráülnek** ugyanarra a fixer-hívásra — külön kört nem érdemelnek.

   > **Egy dokumentumra SOHA ne indíts két fixert párhuzamosan** — ugyanazt a fájlt írnák. A párhuzamosság dokumentumok között van, nem tételek között.
   >
   > **Miért nyer.** A gyakori eset sok apró megállapítás. Szekvenciálisan ez `02 → 03 → 04`: három fixer-kör, plusz a köztük lévő downstream re-deriválás. Így egyetlen párhuzamos batch, aminek az eltelt ideje a leglassabb fixeré.
2. **Státusz-marker felvétele.** A célfázistól lefelé minden érintett dokumentum státuszát fordítsd a fázis-megfelelő nem-kész állapotra `[analyze-loop]` markerrel (pl. `<status:draft> [analyze-loop]`). A marker jelzi: fix-mód aktív → a fixerek automatikusan léptetik a státuszt (lásd D7), és megszakítás után jelzi, hogy a doksit a hurok nyitotta vissza.
3. **Fixer-subagent indítása** a célfázishoz tartozó wrapperrel (lásd „Fixer-subagent indítása").
4. **Kérdés-megállás kezelése.** Ha a fixer az összefoglalójában nyitott kérdéseket jelentett (új `Knn` bejegyzések a `*-questions.md`-ben): tedd fel őket a felhasználónak **egyesével**, fázis-fejléccel (lásd „Fázis-fejléces kérdésformátum"), vezesd át a választ a `*-questions.md`-be (`[x]` + döntés), majd **indítsd újra ugyanazt a fixert** a most már megválaszolt kérdéssel. Ez nem számít új analyze-iterációnak.
4.a **„Változott-e egyáltalán?" őrszem — N.** A fixer visszatérése után futtasd: `git diff --stat -- specs/cycle-NN-<cycle-name>/`.
   - **Ha a diff üres**, és a fixer **nem** vett fel új `Knn` kérdést sem, akkor a dokumentumok változatlanok — a következő analyzer-kör **bizonyosan ugyanazt a `<status:must_fix>` listát** adná. Ilyenkor **ne indíts analyzer-futást**: állj meg, és kérdezd meg a felhasználót, hogyan folytassa (kézi javítás / a `<status:must_fix>` tétel elvetése / a `conventions.md` felülvizsgálata) — a fázis-fejléces kérdésformátummal. Jegyezd fel a Hurok-naplóba: `a fixer nem hajtott végre változtatást`.
   - **Ha a diff nem üres** (vagy van új kérdés) → tovább a 4.b pontra.


4.b **Mechanikus visszacsatolás a fixer után — G (a fixer önellenőrzése után, GS1).** A fixer a visszatérése ELŐTT maga lefuttatja a kaput, és a `kapu:` mezőben jelenti az eredményt. Ez a pont ezért **védőháló, nem alaplépés:** ha a `kapu:` mező `tiszta`, futtasd le a kaput egyszer (0. lépés, `--emit-slices`-szal, mert a szeleteknek amúgy is frissülni kell), és ha valóban nincs mechanikus `<status:must_fix>`, **menj tovább az 5. pontra egyetlen fixer-kör nélkül**. A lenti visszaküldő ág csak akkor él, ha a fixer önellenőrzése nem konvergált (`kapu: maradt — …`), vagy a kapu mégis talál valamit.
   - **Csak mechanikus `<status:must_fix>` van** (P/T/S/A/C/D kódok, tehát kizárólag a kapu kimenete) → **küldd vissza ugyanannak a fixernek** a kapu tételeit, szó szerint. Ez **nem új iteráció**, és **nem indít analyzer-futást**: a hurokszámláló nem nő.
   - **Nincs mechanikus `<status:must_fix>`** → tovább az 5. pontra.
   - **Korlát:** ugyanezt a visszacsatolást **legfeljebb kétszer** futtasd egy iterációban. Ha a fixer harmadszorra is mechanikusan hibás dokumentumot ad vissza, kezeld normál iterációként (az 5. ponttól tovább), és a Hurok-naplóban jegyezd fel: `fixer mechanikus regressziója nem konvergált`.


5. **Downstream re-deriválás — FELTÉTELESEN (D11).** A felfelé javítás után a célfázis alatti fázisokat kell összehangolni (`02 → 03 → 04`) — **de csak akkor, ha a javításnak van downstream hatása.**
   - A fixer visszatérési összefoglalója kötelezően tartalmaz egy **`downstream-hatás:`** mezőt (lásd „Fixer-subagent indítása"): `nincs`, vagy `van — <mi változott, ami a következő fázist érinti>`.
   - **`nincs`** (tipikusan: megfogalmazás-pontosítás, duplikátum-összevonás, artefaktum-hang javítása, elgépelés) → **a downstream fixereket NE indítsd el.** Egy felesleges plan- vagy tasks-fixer futás teljes dokumentum-beolvasással jár, és új hibát is bevihet.
   - **`van`** → indítsd a downstream fixert, és **add át neki a `downstream-hatás` szövegét** — ez a reconciliation hatóköre. Ez **célzott reconciliation, nem teljes újraírás**: a lezárt `*-questions.md` döntéseket megőrzi.
   - Ha a fixer nem adta meg a mezőt, **kérdezd vissza tőle** egy mondatban — ne tippelj, és ne futtasd el „biztos, ami biztos" alapon a teljes láncot.
   - **Minden downstream fixer után is fut a 4.b mechanikus visszacsatolás** — a `tasks.md` hivatkozási rendjét jellemzően épp a reconciliation rontja el.
6. **Újra-analyze — EGY teljes kör, NÉGY PÁRHUZAMOS diagnoszta-körrel (D10/E/SH1).** Előbb futtasd a **mechanikus kaput** `--emit-slices`-szal (0. lépés) — a szeleteknek a javítás utáni állapotot kell tükrözniük —, majd indítsd a **négy kört egyetlen üzenetben, párhuzamosan** (lásd „A négy diagnoszta-kör"). Mindegyik **egyszer** fut, a saját hatókörében teljes módban, és két extra bemenetet kap:
   - **az előző kör `<status:must_fix>` listája** — az analyzer jelentésének **első blokkja** tételenként igazolja, hogy megoldódott-e;
   - **a tervezési dokumentumok változása**: `git diff -- specs/cycle-NN-<cycle-name>/` (a hurok alatt nincs commit, tehát a diff a hurok teljes változását mutatja) — ez **navigáció**: a megváltozott szakaszokat nézze meg először, mert ott a legvalószínűbb az új rés. A vizsgálat hatóköre viszont a **teljes dokumentum** marad.

   Az eredmény alapján:
   - **Nincs `<status:must_fix>`, és az `analyze-task.md`-en sincs nyitott tétel** → a hurok konvergált, ugrás a „Státusz kezelés → PASS"-ra (itt kerül le a marker és történik az egyetlen commit).
   - **Van `<status:must_fix>`** → előbb a **triázs (0.a)** az **új** tételekre (a már eldöntöttekre nem kérdezel rá), majd új iteráció az 1. ponttól, a hurokszámláló +1. Ha a triázs után az `analyze-task.md`-en nem maradt nyitott tétel (a felhasználó minden újat elvetett), a hurok **konvergáltnak számít** → PASS.

   > **A `PASS` kizárólag teljes körből adható** — vagyis mind a négy diagnoszta-kör lefutott és értelmezhető megállapítás-listát adott; a `git diff` a fókuszt adja, nem a hatókört.

6.a **Túlélés-szabály (per-item eszkaláció) — TS.** Mielőtt új iterációt indítanál, nézd meg a diagnoszta-körök jelentésének **első blokkját** (`Előző kör Must Fix tételei`), és gyűjtsd ki azokat az `AF-NN` / `AC-NN` / `AN-NN` / `AX-NN` tételeket, amelyek `NEM oldódott meg` jelöléssel jöttek vissza.
   - **Vezesd a túlélés-számlálót a Hurok-naplóban:** iterációnként írd ki a fennmaradt tételek azonosítóit. Egy tétel túlélés-száma az, hogy hányadik **egymást követő** iterációban jött vissza `NEM oldódott meg`-ként.
   - **Ha egy tétel a MÁSODIK egymást követő iterációt is túléli, ne add oda harmadszor is a fixernek.** Két sikertelen javítási kísérlet után a legvalószínűbb magyarázat nem az, hogy a fixer ügyetlen, hanem hogy a tétel **valódi döntést igényel** (technológiai alap, konfigurációs út, teszt-hatókör), amit a fixer definíció szerint nem hozhat meg — lásd a fix-mód „valódi döntés" szabályát. Ilyenkor:
     1. **alakítsd kérdéssé:** vedd fel `Knn`-ként a célfázis `*-questions.md` fájljába, ha a fixer még nem tette meg;
     2. **kérdezd meg a felhasználót** a fázis-fejléces formátummal, **egyesével**;
     3. a választ vezesd át (`[x]` + döntés), majd **indítsd újra a fixert** a most már megválaszolt kérdéssel.

     Ez a 4. pont kérdés-megállásának felel meg: **nem új iteráció, és nem fogyaszt `X`-et.**
   - **Jegyezd fel a Hurok-naplóba:** `TS — <azonosító> a 2. kört is túlélte → kérdéssé alakítva`.

   > **Miért kell.** A `max X` **hurok-szintű** korlát: nem veszi észre, ha a fixer nagy csomagot visz be, közben viszont ugyanazt a néhány tételt körről körre érintetlenül hagyja. A hurok ilyenkor elégeti mind a három iterációt, és a felhasználó a végén egy `3/3 (feladva)` riportot kap — ahelyett, hogy a második körben megkapta volna a néhány konkrét kérdést, ami után a hurok konvergálhatott volna. A 07-ben ugyanezt a szerepet a per-item leállási számláló (VD4) és az eszkalációs heurisztika (VD5) tölti be.

### A négy diagnoszta-kör (E/SH1) — párhuzamos indítás és összefésülés

A diagnózist **négy párhuzamos kör** végzi, egymástól független hatókörrel. **Egyetlen üzenetben indítsd őket, hogy párhuzamosan futhassanak** — a fázis eltelt ideje így a leglassabb köré, nem a négy összege. Az első három **ugyanazt az `analyzer` definíciót** hívja, más hatókörrel; a hatókör nevét és a szelet útvonalát az indító üzenetben adod meg.

| Kör (hatókör) | Definíció | Kategóriák | Bemenete | Prefix |
|---|---|---|---|---|
| `s1-dup-underspec` | `agents/analyzer.md` | **1. duplikáció + 3. alulspecifikáció** (a KX3-csonkítás is) | `analyze/slices/s1-dup-underspec.md` | `AF-NN` |
| `s2-coverage` | `agents/analyzer.md` | **2. ambiguitás + 5. lefedettség tartalmi ítélete** | `analyze/slices/s2-coverage.md` + a kapu **generált mátrixa** + az átadó fájlok + `cycle-design-input.md` | `AC-NN` |
| `s3-conventions` | `agents/analyzer.md` | **4. konvenció-ütközés** | `analyze/slices/s3-conventions.md` | `AN-NN` |
| `analyzer-exec` | `agents/analyzer-exec.md` | **6. kategória** (prózában ígért teszt, artefaktum-tulajdon, destruktív művelet, horgony-szimbólum, artefaktum-hang) | `plan.md` + `tasks.md` + a kapu **`## <sec:inventory>`** blokkja | `AX-NN` |

_Mind a négy kör bemenete kiegészül a **rebase-fájllistával**, ha a BR1 behozta a fő branch-et (lásd lent)._

> **Ha a szeletek nem készültek el** (a kapu `--emit-slices` nélkül futott, vagy a szelet-fájl üres), az nem megállás: a szemantikai körök a tervezési dokumentumokból dolgoznak, ahogy a szeletelés előtt tették. A körök számát és hatókörét ez **nem** változtatja meg.

**Rebase-fájllista (BR1/a) — csak ha a BR1 behozott valamit.** Ilyenkor a **forrásfa** változott, nem a tervezési dokumentumok: az analyzer a saját `git diff`-navigációjából (D10) erről semmit nem lát. Ezért add át **mind a négy** körnek a fájllistát, ezzel a felszólítással:

> *„Az alábbi fájlok a fő branch behozásával (rebase/merge) érkeztek a ciklus ágába, egy másik ciklus vagy hotfix eredményeként: `<fájllista>`. Nézd meg célzottan, hogy a `plan.md` és a `tasks.md` rájuk mutató hivatkozásai, horgonyai, szignatúra- és interfész-feltevései **állnak-e még** (átnevezett vagy áthelyezett szimbólum, megváltozott paraméterlista, eltűnt export, módosult konfigkulcs). A vizsgálat hatóköre ettől NEM szűkül — ez fókusz, nem hatókör."*

A fájllista **fókusz, nem szűkítés** (ugyanaz az elv, mint a dokumentum-diffnél, D10): a `PASS` továbbra is kizárólag teljes analyzer-futásból adható. A behozott változásokból eredő elcsúszás a szokásos úton megy tovább — `<status:must_fix>` → legkorábbi célfázis → fixer —, **külön „rebase-javító kör" nincs**: az önjavító hurok maga a javító kör.

**Az összefésülés a te dolgod:**
1. A négy `<status:must_fix>` listát és a kapu `<status:must_fix>` listáját **egy listába** fűzöd, majd a **legkorábbi érintett célfázist** ebből az egyesített listából határozod meg.
2. **Duplikátum-szűrés:** ha ugyanarra a `fájl:hely`-re több kör is adott megállapítást, a **specifikusabbat** tartsd meg (jellemzően az `analyzer-exec` végrehajthatósági tételét), és a többit ne vidd tovább a fixernek. Az azonosítót **ne írd át** — a megtartott tétel a saját prefixével megy tovább.
2.a **Triázs-szűrés (TR1):** az `analyze-task.md` **Elvetett tételek** szekciójában szereplő tétellel azonos `fájl:hely` + kategória párosú megállapítás **nem kerül** sem az egyesített `<status:must_fix>` listára, sem a triázs-kérdésbe — az az elvetett tétel újbóli felfedezése, nem új hiba. A riportban se nyisd vissza; a Hurok-naplóba írd: `TR1 — <azonosító> újra megjelent, elvetve marad`.
3. A riport `Végrehajthatósági leltár` szekciója az `analyzer-exec` kimenetéből jön, a `Lefedettségi mátrix` a **kapuból** (lásd lent), az `Érintett DoD-sorok` az `s2-coverage` és az `analyzer-exec` köréből.
4. **Ha az egyik kör hibára fut vagy nem ad értelmezhető listát**, ne minősítsd PASS-nak a kört: indítsd újra azt az egyet (ez nem új iteráció). A hiányzó kör kategóriái **nem esnek ki** — diagnózis nélküli kategóriával PASS nem adható.

### Fixer-subagent indítása

- A fixer-subagent **rendszerpromptja** a célfázis fixer-wrappere: `agents/spec-fixer.md` (02), `agents/plan-fixer.md` (03), `agents/tasks-fixer.md` (04). A wrapper **tartalmazza** a fázis Fix-mód szekcióját és a fázis minőségi kapuját (közös forrásból, build-time beemelve) — nincs duplikált javító logika, és a fázis saját kapui automatikusan érvényesülnek.
- **A fixer nem olvas fázis-skillt (D13).** A wrapperben minden szabály benne van; ha egy fixer mégis a skill beolvasását jelenti be, az hiba (a teljes fázis újrafuttatására csábít egy célzott javítás helyett).
- **Bemenet** a subagentnek: az `analyze-task.md` célfázisra szűrt **nyitott** tétel-listája **az `AF-NN` / `AC-NN` / `AN-NN` / `AX-NN` azonosítókkal együtt** (azonosító + kategória + leírás + `fájl:hely` + a `miért blokkol` és a `hogyan lenne helyes` mező) + a célfázis dokumentumai. A `hogyan lenne helyes` a javítás **célállapota** — ha kérdést tartalmaz, előbb a felhasználó válaszol, és a válasz megy a fixernek. Az azonosítókat **ne hagyd el és ne írd át** — a túlélés-szabály (TS) szó szerinti azonosító-egyezésre épül.
- **Kimenet** a subagenttől: (a) az elvégzett (mechanikus) javítások összefoglalója, (b) a **`downstream-hatás:`** mező (`nincs` / `van — <mi érinti a következő fázist>`, D11), (c) a `*-questions.md`-be felvett **<status:op_new>** kérdések azonosítói — azoké a pontoké, amelyekhez valódi döntés kell —, és (d) a **`kapu:`** mező (GS1): a saját záró kapu-futásának eredménye. A subagent **nem kérdez közvetlenül a felhasználótól** (nincs interaktív csatornája); csak gyűjt és visszaad. A kérdezés a te dolgod (D2).
- **Teljességi ellenőrzés a visszatéréskor.** Vesd össze az átadott listát a fixer összefoglalójával: **minden** átadott azonosítónak meg kell jelennie vagy javítottként, vagy `Knn` kérdésként, vagy explicit „nem tudtam kezelni" indoklással. **Ha egy azonosító némán hiányzik**, ne indíts analyzer-futást rá: kérdezd vissza a fixertől egy mondatban, mi lett vele. Egy némán kihagyott tétel különben úgy néz ki, mintha a fixer megpróbálta és nem sikerült volna — és a TS-számláló hamis képet adna.

### `max X` hurokszámláló + leállás

- **Alapérték: `max X = 3`.**
- **`X` egysége: a teljes analyze-újrafutások száma.** Egy `FAIL → fix → re-deriv → re-analyze` ciklus = **1** iteráció, és **egy** analyzer-futás. A követő-kérdések miatti fixer-újraindítások és az egyes downstream fixer-hívások **nem** növelik `X`-et.
- **Két, egymástól független kilépési feltétel:**
  1. **Nyitott kérdés** → a hurok megáll, kérdez; a user válaszol; a hurok **folytatódik** (ez nem hiba, és nem fogyaszt iterációt).
  2. **`max X` elérve konvergencia nélkül** → a hurok feladja (lásd „Státusz kezelés → FAIL").

### `[analyze-loop]` státusz-marker (D7)

- **Formátum:** `[analyze-loop]` suffix a státusz-érték végén, pl. `<status:draft> [analyze-loop]`, `<status:open_questions> [analyze-loop]`.
- **Jelentése:** a dokumentumot az analyze-hurok nyitotta vissza, fix-mód aktív. Amíg a marker jelen van, a fixerek a státuszt **automatikusan** léptetik (megerősítés nélkül) — eltérően a 02/03/04 normál „megerősítés a státuszváltás előtt" szabályától. A felhasználó csak a **kérdéseknél** és a **végső PASS-nál** lép be.
- **Levétele:** PASS-kor (→ normál flow, a fixer a fázis valódi záró-státuszát adja) vagy `max X` feladáskor a vég-állapot szerint (lásd FAIL). A marker megléte egyúttal a megszakítás-utáni folytatás horgonya is.

### Commit-stratégia a hurokban (D9)

- **`analyze-loop`-ban nincs iterációnkénti commit** — zaj-mentes marad a történet.
- **Egyetlen commit a hurok lezárásakor** (PASS vagy `max X` feladás): `cycle-NN: 05-analyze`. Ez a commit **kötelező, mindkét ágon** — az eljárást (stage → commit → determinisztikus ellenőrzés → visszajelzés) lásd a *Fázis-záró commit* szekcióban (PC1).
- **Megszakítás-biztos:** a köztes commit hiányát a `[analyze-loop]` státusz-marker + a `*-questions.md` + a <sec:loop_log> pótolja — ezekből a folytatás rekonstruálható (lásd „Folytatás megszakított futás után").

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

Hozd létre / frissítsd a `specs/cycle-NN-<cycle-name>/analyze/analyze-report.md` fájlt (relatív útvonal-formátum a dokumentum tartalmában, `file://` tilos). **A létrehozás időpontja az első diagnózis utáni pont, nem a fázis vége** — lásd az *Élő riport (AR1)* szekciót:

```md
<!-- INCLUDE:lang/05-analyze.md#analyze-report-struktura -->
```

---

## analyze-task.md struktúra

Hozd létre / frissítsd a `specs/cycle-NN-<cycle-name>/analyze/analyze-task.md` fájlt (AD1). **Az első triázs után jön létre**, és a hurok minden lépésénél frissül. Ez a fixerek munkalistája; a „miért" a riportban van, ide a **teendő** kerül:

```md
<!-- INCLUDE:lang/05-analyze.md#analyze-task-struktura -->
```

---

## Minőségellenőrzés — a jelentés lezárása előtt

Menj végig, mind a **6** kategória ténylegesen lefutott-e — vagyis **mind a négy diagnoszta-kör megjött-e** (`s1-dup-underspec` → 1+3., `s2-coverage` → 2+5., `s3-conventions` → 4., `analyzer-exec` → 6. kategória). **A 6. kategóriánál külön ellenőrizd, hogy a subagent visszaadta-e a „Végrehajthatósági leltárt"** — enélkül a PASS nem fogadható el, mert épp azok a hibák maradnának rejtve, amelyeket a lefedettségi mátrix szerkezetileg nem lát:

1. **Duplikáció** — átnézve spec/plan/tasks redundanciára?
2. **Ambiguitás** — minden elfogadási feltétel mérhető/eldönthető?
3. **Alulspecifikáció** — minden komponens és feltétel meghatározott?
4. **Konvenció-ütközés** — minden tervezési döntés egyezik a `conventions.md`-vel?
5. **Lefedettség** — a kapu generált mátrixa bekerült a riportba, és az `s2-coverage` kör tartalmi ítélete (`Érintett DoD-sorok` + `DoD-NN`-en túli követelmények) át van vezetve rajta?
6. **Végrehajthatóság és artefaktum-tulajdon** — az `analyzer-exec` visszaadta a *Végrehajthatósági leltárt* (lásd fent), a **mechanikus kapu** (`analyze-gate-check.py`) lefutott ebben a körben `--emit-slices`-szal, és a kapu blokkjait át is adtad a köröknek (AG3/AG4/SH1)?

Ha bármelyik kategória nem futott le, ne zárd le a jelentést. Ha a hurok futott, ellenőrizd azt is, hogy a **<sec:loop_log>** minden iterációt tartalmaz.

**A `Javítandó tételek` lista lezárt-e? (AR1)** — a riport nem zárható le úgy, hogy egy tétel `[ ]` állapotban, `nyitott` vagy `javítás alatt` mezővel marad. Minden tétel három végállapot valamelyikébe fut: `[x]` + `megoldva (iter <n>)`, vagy `[x]` + `elvetve — <indoklás>`, vagy — `FAIL` ág esetén — `[ ]` + `kérdés (<FÁZIS>/K<nn>)` illetve `nyitott`, **kifejezetten a feladás dokumentumaként**, a Hurok-naplóból hivatkozva. Egy `PASS` mellett nyitva hagyott tétel önmagában is a jelentés visszautasításának oka. A triázsban (TR1) elvetett tétel ugyanide fut be: `[x]` + `elvetve (triázs, iter <n>) — a felhasználó nem kérte a javítását`.

**Az `analyze-task.md` lezárt-e?** — `PASS` mellett nem maradhat rajta nyitott (`[ ]`) tétel, és minden tételének meg kell lennie a riportban is, ugyanazzal az azonosítóval és egyeztethető végállapottal. Ha a riport és a lista ellentmond egymásnak, a jelentés nem zárható le.

**A `Triázs (TR1)` fejléc-mező kitöltve?** — ha az első diagnózis adott `<status:must_fix>` tételt, a mezőben szerepel, mit választott a felhasználó (`mind` / azonosítók / `egyik sem`) és hány tétel maradt elvetve. **Triázs-döntés nélkül elvetett tétel nem lehet a riportban** — az az orchestrátor önkényes szűkítése lenne.

**A `<field:f_validated_base>` mező kitöltve? (BR1)** — a riport fejlécében szerepel a fő branch neve és SHA-ja (`git rev-parse origin/main`), a ciklus ágának csúcsa (`git rev-parse HEAD`), és hogy a BR1 hozott-e be valamit. Ezt a `06` és a `09` **összeveti a saját futásakori állapottal**: ha időközben előrement a fő branch, az `analyze-report.md` `PASS`-a elavult alapon készült. Placeholder vagy hiányzó mező esetén a jelentés nem zárható le. (No-VCS projektben a mező értéke `—`.)

---

## Státusz kezelés

### PASS (a hurok konvergált, vagy első nekifutásra tiszta)

Nincs `<status:must_fix>` megállapítás — vagy ami maradt, azt a felhasználó a triázsban vetette el (TR1).

Teendők **sorban**:
1. A riport már létezik (AR1) — **ne írd újra nulláról**: állítsd a státuszát `IN_PROGRESS`-ről `PASS`-ra, az `Aktuális lépés:` mezőt `lezárva`-ra, töltsd ki a `Hurok:` mezőt és a Hurok-naplót (ha volt iteráció), és pipáld ki a `Javítandó tételek` lista maradék tételeit a végállapotukkal. A `Triázs (TR1)` mezőt is töltsd ki (ha volt triázs). **Zárd le az `analyze-task.md`-t is:** ne maradjon rajta nyitott tétel.
2. **Vedd le a `[analyze-loop]` markert** minden érintett dokumentumról — a fixerek a fázis valódi záró-státuszát adták (`<status:ready_for_plan>` / `<status:ready_for_tasks>` / `<status:ready_for_implement>`); ellenőrizd, hogy ez áll-e mindegyiken.
3. **Egyetlen lezáró commit** (a hurok alatt nem volt köztes commit) — a *Fázis-záró commit* szekció eljárása szerint, **kötelező**:
   ```bash
   git add specs/cycle-NN-<cycle-name>/
   git commit -m "cycle-NN: 05-analyze"
   ```
4. **Ha a triázs elvetett tételeket:** egy mondatban mondd meg, hányat, és hogy `elvetve (triázs)` állapottal a riportban visszakereshetők — a `PASS` tudatosan elfogadott ellentmondások mellett született.
5. Jelezd a felhasználónak a következő lépést és a fázis indító parancsát:
<!-- INCLUDE:lang/05-analyze.md#zaro-uzenet -->
   > **A válasz végén helyezd el az `analyze-report.md` közvetlen, kattintható linkjét.**

### FAIL (`max X` elérve PASS nélkül)

A hurok `max X = 3` iteráció után sem konvergált.

Teendők **sorban**:
1. A riport már létezik (AR1) — **ne írd újra nulláról**: állítsd a státuszát `IN_PROGRESS`-ről `FAIL`-re, az `Aktuális lépés:` mezőt `lezárva`-ra, a `Hurok:` mezőbe `<max X>/<max X> (feladva)`, és a Hurok-naplóba a megrekedt állapotot (mely `<status:must_fix>` maradt, melyik fázisnál). A `Javítandó tételek` listán a megrekedt tételek `[ ]`-ben maradnak — ez a feladás dokumentuma. Az `analyze-task.md`-en **ugyanezek maradnak nyitva**: ez a folytatás munkalistája.
2. **Hagyd rajta a `[analyze-loop]` markert** az érintett dokumentumokon — így a felhasználó (vagy egy következő session) látja, hogy a hurok nyitotta vissza őket, és hol akadt el.
3. **Egyetlen lezáró commit** — a *Fázis-záró commit* szekció eljárása szerint, **kötelező** (a FAIL ág sem kivétel):
   ```bash
   git add specs/cycle-NN-<cycle-name>/
   git commit -m "cycle-NN: 05-analyze"
   ```
4. Összefoglalás + kérdés a felhasználónak: foglald össze, melyik `<status:must_fix>` nem oldódott meg és miért (pl. ismétlődő ambiguitás, amit a fixer nem tud eldönteni), és kérdezd meg, hogyan folytassák (kézi javítás az adott fázisban / döntés egy nyitott kérdésre / a `conventions.md` felülvizsgálata súlyos konvenció-ütközésnél).
   > **A válasz végén helyezd el az `analyze-report.md` közvetlen, kattintható linkjét.**

<!-- INCLUDE:shared/phase-commit.md -->

A fenti blokkban a `<FÁZIS-TAG>` értéke ebben a fázisban: **`05-analyze`**. A commit a **hurok lezárásakor, egyszer** történik — de **minden lezáró ágon** (PASS és `max X` FAIL egyaránt). A hurok alatt nincs köztes commit; a köztes állapotot a `[analyze-loop]` marker, a `*-questions.md` fájlok és a Hurok-napló őrzi.

> **Megállási szabály (PC1):** ha az `analyze-report.md` státusza `PASS` vagy `FAIL`, de a fázis-záró commit hiányzik (VCS-es projekt, `git log -1 --oneline` nem a `cycle-NN: 05-analyze` commitot mutatja), **STOP** — először commitolj, csak utána zárd le a fázist és add meg a következő lépést.

---

## Kérdezési szabályok

- Csak **egy** kérdést tegyél fel egyszerre, várd meg a választ. **Egyetlen kivétel a triázs-megállás (TR1):** ott egy üzenetben, számozott listaként kéred be a döntést az összes tételre — a lista maga a kérdés.
- A hurok közbeni kérdéseknél használd a **fázis-fejléces kérdésformátumot** (`[FÁZIS · iter n/max X · FÁZIS/Knn]`).
- Minden alkalommal, amikor kérdést teszel fel vagy jóváhagyást kérsz, a válaszod végén kötelezően helyezz el egy közvetlen, kattintható markdown linket az érintett fájlra.