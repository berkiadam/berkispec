# Meta-prompt — Prompt fejlesztés

Ez a fájl arra való, hogy egy új AI-sessziót indítsál, amelynek célja a `prompts/` mappa promptjainak felülvizsgálata vagy továbbfejlesztése.

**Használat:** Másold be az alábbi szaggatott vonaltól az AI-nak, és add meg a konkrét fejlesztési célt a végén.

---

Egy **spec-driven development workflow** promptrendszerét fejlesztjük. A `prompts/` mappa az AI-asszisztált szoftverfejlesztési ciklus fázisonkénti instrukcióit tartalmazza, **skillekre** (`prompts/skills/` — fázis-receptek) és **ágensekre** (`prompts/agents/` — specialista subagentek) szervezve. Minden skill egy fázist vezérel — ezeket a promptokat adjuk be egy AI-agentnek, hogy az adott fázist elvégezze.

A rendszer célja: egy-két fejlesztő és egy AI-agent együtt, következetes minőségű, tesztelt szoftvert fejlesszen ciklusonként leszállítható egységekben. A promptok adják az agentnek a keretet, korlátokat, minőségellenőrzési listát és megállási szabályokat.

---

## A workflow felépítése

A teljes fejlesztési folyamat 10 lépésből áll (0–9):

**Projekt szintű setup (egyszer fut le):**
- `00` — Projekt inicializálás: `conventions.md` létrehozása (konvenciók, tech stack, portok, merge stratégia)
- `01` — Ciklusok kezelése: `specs/roadmap.md` létrehozása/karbantartása (cikluslista, függőségek, teszt kritériumok)

**Per-ciklus loop (minden fejlesztési ciklusra ismétlődik):**
- `02` — Spec írás: `specs/cycle-NN-<cycle-name>/spec.md` — státusz: `Tervezésre kész`
- `03` — Plan írás: `specs/cycle-NN-<cycle-name>/plan.md` — státusz: `Task írásra kész`
- `04` — Tasks írás: `specs/cycle-NN-<cycle-name>/tasks.md` — státusz: `Implementálásra kész`
- `05` — Analyze: kereszt-fázisos konzisztencia ellenőrzés (read-only orchestrátor) — `analyze-report.md` PASS/FAIL; FAIL esetén önjavító hurok (fixer-subagentek, `max X=3`)
- `06` — Implementálás: kód + `tasks.md` — státusz: `Validálásra kész`
- `07` — Validálás: tesztek + Sonar + DoD ellenőrzés (orchestrátor) — PASS / FAIL; FAIL esetén önjavító hurok (`implement-fixer` = 06 fix-mód, per-item 3-próba korlát, VD5 eszkaláció 03/02-re)
- `08` — Doc-sync: a `docs-generated/` mappa (system-overview, architecture, CHANGELOG, design-drift, mappa-index + komponens README-k) naprakészen tartása az as-built rendszerhez — terv (`doc-sync-planner` subagent → `doc-sync-plan.md`) → mechanikus végrehajtás → objektív konzisztencia-kapu (DS22); kapu-bukásnál ember-vezérelt javítás (`doc-sync-questions.md`). **Nem** önjavító subagent-hurok.
- `09` — Review & Merge: code review + merge (orchestrátor) — FAIL esetén kétfázisú önjavító hurok (`review-fixer` = 06 fix-mód → re-validate → re-review, per-item 3-próba + `max 5`, RD6 eszkaláció); a merge kézi megerősítéssel (RD8)

Minden ciklus mappája: `specs/cycle-NN-<cycle-name>/`

---

## A prompt fájlok

| Fájl | Fázis | Bemenet | Kimenet |
|------|-------|---------|---------|
| `prompts/skills/00-init-project.md` | Projekt init | Projekt leírás | `conventions.md` |
| `prompts/skills/01-add-cycles.md` | Ciklusok kezelése | HLD/LLD vagy leírás | `specs/roadmap.md` |
| `prompts/skills/02-write-spec.md` | Spec | Roadmap + ciklus neve | `spec.md` (`Tervezésre kész`) |
| `prompts/skills/03-write-plan.md` | Plan | `spec.md` | `plan.md` (`Task írásra kész`) |
| `prompts/skills/04-write-tasks.md` | Tasks | `plan.md` | `tasks.md` (`Implementálásra kész`) |
| `prompts/skills/05-analyze.md` | Analyze | ciklus mappa | `analyze-report.md` (PASS/FAIL) — FAIL → önjavító hurok (fixer-subagentek, `max X=3`) |
| `prompts/skills/06-implement.md` | Implementálás | `tasks.md` | Kód + `tasks.md` (`Validálásra kész`) |
| `prompts/skills/07-validate.md` | Validálás | `spec.md`, `plan.md`, `tasks.md` | PASS/FAIL riport a `test-report/` mappában — FAIL → önjavító hurok (`implement-fixer`, 3-próba korlát, VD5 eszkaláció) |
| `prompts/skills/08-doc-sync.md` | Doc-sync | ciklus mappa + `docs-generated/` | konzisztens `docs-generated/` (system-overview, architecture, CHANGELOG, design-drift, README) + `doc-sync-plan.md` — terv (`doc-sync-planner`) → végrehajtás → objektív kapu (DS22); kapu-bukás → ember-vezérelt javítás (`doc-sync-questions.md`) |
| `prompts/skills/09-review-and-merge.md` | Review & Merge | Cycle branch, `plan.md`, `spec.md` | `code-review.md` (+ `# Review History`) + merged branch — FAIL → kétfázisú önjavító hurok (`review-fixer`, re-validate → re-review, 3-próba + `max 5`, RD6) |

A specialista subagentek a `prompts/agents/` alatt: `reviewer.md` (09), `analyzer.md` (05 — read-only diagnózis), `researcher.md` (03), `doc-sync-planner.md` (08 — read-only doc-sync tervkészítő), az 05 önjavító hurok fix-mód belépői: `spec-fixer.md`, `plan-fixer.md`, `tasks-fixer.md` (vékony wrapperek a 02/03/04 skill Fix-mód szekciójára), az 07 validate-hurok fix-mód belépője: `implement-fixer.md` és a 09 review-hurok fix-mód belépője: `review-fixer.md` (mindkettő vékony wrapper a 06 skill Fix-mód szekciójára, `## Validációs javítások` ill. `## Review javítások` bemenettel).

A `prompts/README.md` minden fázishoz tartalmazza a felhasználónak szánt copy-paste prompt blokkot.

---

## Tervezési elvek, amelyek minden promptban érvényesülnek

**1. Fáziskapu (előfeltétel-ellenőrzés)**
Minden prompt első lépése: beolvassa az előző fázis dokumentumának státuszát. Ha nem a várt státuszon áll, megáll és visszairányít. Ez megakadályozza, hogy egy befejezetlen fázis alapján haladjon tovább.

**2. Minimális kontextus betöltés**
Az agent csak a szükséges fájlokat olvassa be, csak a releváns részeit. Ha mélyebb kutatásra van szükség, azt delegálja, és az eredményt összefoglalva hozza vissza — ne töltse tele a fő munkamemóriát. A cél: a fő kontextusablak ne telítődjön felesleges információval.

**3. Egyetlen kérdés egyszerre**
Ha a promptnak döntési ponthoz van szüksége a felhasználó inputjára, egyszerre csak egy kérdést tesz fel, megvárja a választ, majd iterál. Ez megelőzi az egyszerre több nyitott kérdés kavalkádját.

**4. Scope fegyelem**
Minden fázis szigorúan a saját scope-ján belül marad:
- Spec: csak az üzleti viselkedést írja le — nem tervez implementációt
- Plan: csak a spec scope-ját fedi le — nem bővíti, nem szűkíti
- Tasks: csak a plan tervezett módosításait bontja le — nem ad hozzá újat

**5. Státuszkezelés**
Minden fázis dokumentuma explicit státuszmezőt kap (`Piszkozat` → fázisspecifikus zárolt státusz). A következő prompt ezt olvassa be kapuként.

**6. Minőségellenőrzési lista (lezárás előtt)**
Minden prompt tartalmaz egy kötelező ellenőrzési listát, amelyet a fázis lezárása előtt le kell futtatni. Ez biztosítja, hogy a következő fázis egy teljes és konzisztens dokumentumot kap.

**7. TDD jelölés (04 + 06)**
A 04-es prompt tasks listát ír, a 06-os (implement) végrehajtja. A TDD ciklus a tasks listában explicit jelöléssel van rögzítve:

- `[RED]` — az agent először megírja a tesztet, amely **bukni fog**, mert az implementáció még nem létezik. Ez rögzíti a várható viselkedést kód formájában, mielőtt bármit implementálnánk.
- `[GREEN]` — ezután jön az implementáció, amelynek célja kizárólag az, hogy a `[RED]` teszt átmenjen. A `[RED]` task mindig megelőzi a párját.
- `[CHECK]` — minden logikai csoport végén kötelező: konkrét parancsot tartalmaz (pl. `npm test`, `npm run typecheck`), amelyet az agent ténylegesen lefuttat. Egy `[RED]`/`[GREEN]` task nem számít késznek, amíg a csoportzáró `[CHECK]` nem zöld.

Nem minden task TDD: konfigurációs fájlok, docker, README, infrastruktúra-változások esetén nincs `[RED]`/`[GREEN]` jelölés.

**8. Megállási szabályok**
A 04-es (tasks) és 06-os (implement) prompt explicit felsorolja azokat az eseteket, amikor az agent megáll és visszakérdez — ne folytassa bizonytalan vagy ellentmondásos helyzetben.

**9. Kereszt-fázisos konzisztencia ellenőrzés + önjavító hurok (05 — analyze)**
A 04 (tasks) után, az implementáció előtt egy analyze fázis fut: a `analyzer` subagent (read-only diagnózis) a `spec.md` ↔ `plan.md` ↔ `tasks.md` ↔ `conventions.md` négyest 5 kategóriában ellenőrzi (duplikáció, ambiguitás, alulspecifikáció, konvenció-ütközés, lefedettségi hiány). FAIL esetén az 05 **orchestrátorként önjavító hurkot vezényel**: a legkorábbi érintett célfázishoz indít egy fixer-subagentet (a 02/03/04 fix-módja), downstream re-deriválás (`02→03→04`, célzott reconciliation) után újra-analyze fut — amíg PASS, vagy `max X=3` iterációig. A döntést igénylő kérdéseket a fixerek a `*-questions.md`-be gyűjtik (nem kérdeznek közvetlenül), és az orchestrátor teszi fel a felhasználónak (`FÁZIS/Knn` fejléccel); nyitott kérdésnél a hurok megáll, válasz után folytatódik. A hurok alatt a dokumentumok `[analyze-loop]` státusz-markert viselnek (auto-státusz + megszakítás-biztos folytatás), és csak a hurok végén készül egyetlen commit.

**10. Önjavító hurok a kód-fázisokban (07 — validate, 09 — review)**
A 05-analyze mintáját két további fázis is átveszi. **07-validate:** tesztek/Sonar/DoD FAIL esetén az 07 orchestrátorként az `implement-fixer` subagentet (= 06 fix-mód) indítja a `## Validációs javítások` hibalistára, majd újra-validál — a per-item 3-próba korlátig (`[validate-loop]` marker, VD3 anti-„teszt-csalás", VD5 eszkaláció 03/02-re). **09-review:** `Must Fix` esetén a 09 orchestrátorként a `review-fixer` subagentet (= 06 fix-mód) indítja a `## Review javítások` findingokra, és **kétfázisú** hurkot vezényel — `fix → re-validate (07 teljes ellenőrzései) → re-review` —, amíg a review tiszta és a validálás zöld; korlát a per-item 3-próba + `max 5` backstop (`[review-loop]` marker, RD4 anti-„csalás", RD6 jel-vezérelt eszkaláció 03/02-re). A merge **kézi megerősítéssel** zárul (RD8), szemben a 07 auto-PASS-ával. A három hurok közös konvencióit (marker, napló, fixer-wrapper, commit-at-end) a `README.md` „Önjavító hurkok (analyze + validate + review)" szekciója rögzíti.

**11. Élő működési dokumentáció (08 — doc-sync)**
A 07-validate és a 09-review közé egy dedikált **doc-sync** fázis ékelődik, amely ciklusról ciklusra naprakészen tartja a generált projekt-dokumentációt egy `docs-generated/` mappában (`system-overview.md` as-built működésleírás, `architecture.md`, részletes `CHANGELOG.md`, `design-drift.md`, mappa-index README + komponens README-k). Ez **nem** a négy önjavító hurok mintáját követi: a működése **„terv előbb, aztán mechanikus végrehajtás"** (a `doc-sync-planner` read-only subagent → `doc-sync-plan.md` pipálható terv → a fő ágens mechanikusan végrehajtja), majd egy **objektív, projektfüggetlen konzisztencia-kapu** (DS22: megszűnt/átnevezett azonosító `grep`, ábra-átkerülés, mappa-index halmaz-egyezés, coverage-marker) zár. Kapu-bukásnál **ember-vezérelt** javítás indul a `doc-sync-questions.md`-n keresztül (nem subagent-önjavító hurok). A `02-write-spec` „pull"-ként beolvassa a `system-overview.md`-t current-truth kiindulásként; a doc-sync „push"-ként írja — a kettő tartja őszintén a doksit. A 08-doc-sync és a 09-review **független minőségi kapuk**: a reviewer csak kódra ad findingot, a generált doksik helyességét a doc-sync saját kapuja garantálja.

---

## A promptok aktuális állapota

A rendszer aktívan használatban van — több fejlesztési ciklus (cycle-01 – cycle-16) lefutott már ezekkel a promptokkal. A skill fájlok a `prompts/skills/`, a specialista ágensek a `prompts/agents/` mappában olvashatók.

---

## Feladatod

Olvasd be a releváns skill fájlokat a `prompts/skills/` mappából (és szükség szerint az ágenseket a `prompts/agents/`-ból), majd segíts a következő fejlesztési célban:

**[IDE ÍRD LE A KONKRÉT FEJLESZTÉSI CÉLT — pl.:]**
- „A 03-as plan skill minőségellenőrzési listája hiányos — egészítsd ki."
- „A 06-os implement skill nem kezeli megfeloloen a delegalas esetét."
- „Vezess be egy uj 09-es fazist: changelog generalas."
- „Altalanos felulvizsgalat: hol vannak kovetkezetlensegek a skillek kozott?"

Ha nincs konkrét cél megadva, végezz általános felülvizsgálatot: keress következetlenségeket, hiányzó megállási szabályokat, scope-szivárgást a fázisok között, és javasolj konkrét javításokat.
