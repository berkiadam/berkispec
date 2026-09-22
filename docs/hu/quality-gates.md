# Minőségi kapuk, döntési napló és review

← [Vissza a főoldalra](../../README-HU.md) · [Oldalindex](README.md)

## 14. Sonar minőségellenőrzés

A validate fázis (07) — ha a `conventions.md` tartalmaz `## Sonar minőségellenőrzés` szekciót — Podman-alapú SonarQube analízist futtat.

**Folyamat:**
1. SonarQube szerver indítása (ha még nem fut).
2. Scanner futtatása a `conventions.md`-ben megadott módon (a projekt teszt-tooling scriptjével).
3. A riportok az **aktuális validálási kör mappájába** kerülnek (`test-report/validate/round-NN/sonar-report.md` + `.html`); a Quality Gate FAIL non-zero státusszal áll meg.
4. **A Quality Gate kiértékelése determinisztikus — a `sonar-gate.py` végzi a Sonar Web API-ból** (`/api/qualitygates/project_status` + `/api/issues/search`), nem a riport LLM-es elolvasásával. A kilépő kód dönt:
   - **`0`** — QG OK (a `MINOR`/`INFO` találatok nem blokkolnak);
   - **`1`** — QG FAIL **finding miatt**: a kiírt `BLOCKER`/`CRITICAL`/`MAJOR` lista `fájl:sor + üzenet` alakban a javító-taskok forrása (a severity-szűrés már megtörtént);
   - **`3`** — QG FAIL **küszöb miatt, blokkoló finding nélkül** (QG1): a szkript megnevezi a bukott feltételt (pl. `new_coverage: 71.2 (küszöb: < 80)`). Ilyenkor **tilos üres hibalistával fixert indítani** — vagy konkrét lefedettségi task készül, vagy STOP + humán;
   - **`2`** — használati hiba (hiányzó URL/projectKey/token) → a Sonar a `test-runner` subagenten keresztül fut, a régi módon.

   A `--out` kapcsolóval a szkript a `sonar-report.md` bizonyítékot is legenerálja a kör-mappába (TR3).

   > **⚠ A Quality Gate tipikusan CSAK az új kódot méri.** Egy örökölt (vagy baseline nélküli első elemzésből származó) `BLOCKER` mellett is lehet `OK` a gate — élő SonarQube-on ellenőrizve. Ha a projekt ezt a rést be akarja zárni, a `--fail-on BLOCKER` (vagy `BLOCKER,CRITICAL`) kapcsolóval a szkript zöld gate mellett is FAIL-t ad. **Szándékosan opt-in:** régi kódbázison bekapcsolva a hurok a ciklus scope-ján kívüli, örökölt findingokra kezdene javító-taskokat gyártani.
5. **PASS:** a validálás folytatódik. **FAIL:** a hibák a `validation-report.md`-be kerülnek, a `tasks.md` státusza `Implementálásra kész [validate-loop]`-ra vált, és az **07 önjavító hurok** elindítja az `implement-fixer` subagentet (06 fix-mód) a Sonar-hibák javítására, majd újra-validál — a 3-próba korlátig (lásd „Validációs napló").

**Módosítások detektálása (SCM & Git Blame):** a SonarQube a `.git` SCM és Git Blame adatokat használja, és a fő ághoz képest (git diff) választja külön az **új hibákat (New Issues)** az örökölt hibáktól. A Quality Gate csak az újonnan módosított sorokra vonatkozik.

---

## 15. Döntési napló (imp-decision.md)

Az `imp-decision.md` az implement fázis (06) nehéz döntéseinek és zsákutcáinak naplója (`specs/cycle-NN-<cycle-name>/imp-decision.md`). Ha egy task megoldásához legalább 3 sikertelen kísérlet kellett:

```md
## T0XX — <rövid cím>

**Mi volt a gond:** <hiba tömör leírása>
**Mit próbáltunk:** <sikertelen kísérletek röviden>
**Mi lett a megoldás:** <a végül működő megközelítés>
```

---

## 16. Validációs riport (validation-report.md)

A `test-report/validation-report.md` a validate fázis (07) futásait, SonarQube eredményeit és teszthibáit követi. **A fájlt nem kézzel írja az orchestrátor:** a `## Kör N` blokkokat a `round-log.py` nyitja (`open`), tölti (`step`) és zárja (`close`) — beleértve a `round-NN/` mappa létrehozását azonos sorszámmal —, a `# Validation History`-t pedig a `failure-counter.py`. Az orchestrátor csak a szabad szöveges mezőket adja hozzá (kör döntése, DoD-indoklás). Az egymást követő bukásokat elemenként a `failure-counter.py` szkript számolja (determinisztikusan, nem az ágens kézzel) — az alábbi formátumban fűzi hozzá a bejegyzéseket:

```md
# Validation History

- **Run 1 (2025-01-15 10:30) - FAIL**
  - **Failed Item:** TokenExchangeService › should return 403 for invalid token
  - **Consecutive Failures for this item:** 1
  - **Details:** NullPointerException a JWE dekódoláskor

- **Run 3 (2025-01-15 14:20) - PASS**
```

**Leállási korlátok:** a `failure-counter.py` `exit 3`-mal áll meg, ha egy elem **3 egymást követő** vagy **5 összes** bukást ér el, vagy ha **5 egymást követő FAIL-futás** után sem konvergál a hurok (megrekedt kód-bug → STOP + humán; tervezési hiba → eszkaláció 03/02-re). **Egy validálási kör = egy `Run` bejegyzés** — részeredményt naplózni tilos, mert a közbeiktatott PASS megszakítaná a bukás-láncot.

**A fájl nem csak napló, hanem teljes riport (VD9):** a `# Validation History` fölött körönként egy `## Kör N` blokk áll — végrehajtási sorrend időbélyeggel (mi futott, mi maradt ki és miért), a `test-runner` bizonyítékai (parancs + `X passed / Y failed / Z skipped`), a **teszt-riport kapu (TR3)** eredménye, `DoD-NN` tábla, a javító kör nyoma (taskok → fixer → VD3a szerződés-kapu) és a kör döntése; a végén `## Összegzés` az újrafuttatott elemekkel. A hurok teljes mechanikáját a 4.5 szekció írja le.

**A `test-report/` mappa a riportoké is — körönkénti bontásban (TR5):** a `conventions.md` `## Teszt-riportolás` táblájában deklarált artefaktumok (Allure/Playwright HTML, coverage, JUnit XML) minden ciklusban ide kerülnek, és a ciklus git-diffjének részei. Nem a gyökérbe, hanem **körönként külön almappába**, hogy egy önjavító hurok minden köréről megmaradjon a bizonyíték — a `validation-report.md` lépés-táblájában jelzett bukáshoz így megnyitható a hozzá tartozó riport:

```
specs/cycle-NN-<name>/test-report/
├── validation-report.md        # a 07 naplója — több körre átívelő, append-only
├── implement/
│   └── check-log.md            # a 06 [CHECK]-futásainak naplója (parancs, próba, darabszámok)
└── validate/
    ├── round-01/               # az 1. validálási kör összes artefaktuma (+ sonar-report.md/.html)
    └── round-02/               # a 2. köré — az 1. körét sosem írja felül
```

A mappanév száma **kötelezően egyezik** a `validation-report.md` `## Kör N` sorszámával. A `report-gate-check.py` kapuja a `--report-subdir test-report/validate/round-NN` kapcsolóval az adott kör mappáját ellenőrzi — **teljes körben kötelezően, könnyű körben nem** (könnyű körben szándékosan nem fut minden tesztkategória, így a teljes riport-tábla nem is teljesíthető). Körök mappái sosem törlődnek: a bukott köröké a legértékesebb a hibanyomozáshoz.

---

## 17. Reviewer agent (agents/reviewer.md)

**Mikor hívja meg:** A **07 — Validálás és kódreview** fázis, a validálási kör **2. lépéseként** (RV1) — a „statikus réteg" fele, a Sonar Quality Gate mellett. Kizárólag **teljes** körben fut (könnyű körben csak inkrementálisan, a nyitott `MF-NN`-ekre), és csak akkor, ha a **gyors tesztek** (unit/typecheck) zöldek; a nehéz tesztek (E2E/regresszió) ilyenkor **még nem futottak**. Bukott gyors teszt mellett nem indul: fordítani sem lehet a kódot. A sorrend indoka (VD13): a review-findingok javítása megváltoztatja a kódot, ezért olcsóbb előbb review-zni, és csak review-tiszta diffre elkölteni az E2E-stacket.

**Mit csinál:** Task tool subagent-ként átnézi a cycle branch változásait (git diff a fő ág ellen), és strukturált, **gépiesen parszolható** jelentést készít:
- **Kritikus javítandók (Must Fix)** — blokkolók; `- [ ] **MF-NN** — <file>:<line> — <leírás>` formátumban. Az `MF-NN` **stabil azonosító**: ezzel lépteti az orchestrátor a per-item leállási számlálót, ezért re-review-nál nem szabad újraszámozni.
- **Javasolt fejlesztések (Suggestions)** — nem blokkolók, `S-NN` azonosítóval.

**Output:** `specs/cycle-NN-<cycle-name>/test-report/code-review.md`. **Naplót nem ír:** a hurok története, a próbaszámlálók és a leállási korlátok a `validation-report.md` `# Validation History`-jában élnek, a teszthibákkal **közös** számlálón.

**A szempontlista közös blokkban él, és a fallback ág is megkapja (RV-FB1).** Az `## Ellenőrzési szempontok` és a `Must Fix` vs `Suggestion` határvonal a `prompts/shared-hu/review-checklist.md`-ben van egy példányban, és a telepítő **két** helyre emeli be: a `reviewer` promptjába **és** a `07` reviewer-fallback blokkjába. A fallback definíció szerint nem olvassa a subagent promptját — enélkül ott a review „nézd át a diffet" szintre esik vissza, ami egy éles ciklusban pontosan meg is történt. Ebbe a listába került az **üres teszt-törzs eldönthető kérdése** is (`TB1`): asszertáció nélküli új vagy módosított teszt-függvény a diffben → `Must Fix`.

A `reviewer` **read-only diagnoszta** (mint az `analyzer`): csak a jelentést írja, javítást nem végez, és nem kérdez. A javítást a `review-fixer` (= 06 fix-mód), a vezénylést a 07 orchestrátor végzi.

**Visszacsatolási kör:**
- **Must Fix** → a **kör FAIL-je** (nem külön hurok): a findingok `MF-NN` néven a `## Review javítások` taskok közé kerülnek, a `review-fixer` javítja, majd könnyű kör + kötelező teljes megerősítő kör következik **re-review-val**. A részletes mechanikát lásd az [4.5 szekcióban](self-healing-loops.md).
- **Suggestion** → nem blokkol; az orchestrátor csak akkor javítja direktben, ha a scope-on belül marad és kockázatmentes (a következő kör úgyis leteszteli).
- **Nincs Must Fix + zöld tesztek** → a validálás PASS, tovább a `08-doc-sync`-re.

---
