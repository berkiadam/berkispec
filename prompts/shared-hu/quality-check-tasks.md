<!-- Forrás-jegyzet: ezt a szekciót a 04-write-tasks.md skill ÉS a hozzá tartozó
     fix-mode-* shared fájl is beemeli (build-time INCLUDE). Egy helyen szerkeszd. -->
## Minőségellenőrzés — lezárás előtt

Menj végig a következő csoportokon sorban. Minden csoportot önállóan pipáld ki, mielőtt a következőre lépsz.

### A) Plan lefedettség

- A Prerequisite dokumentumok listája tartalmazza a `plan.md`-t és minden `<status:reviewed>` schema artifaktot?
- **Plan-hivatkozás minden taskon (PID1):** minden task sora `— plan [P-…]`-val végződik, **pontosan egy** elsődleges ID-val (a második zárójelben, „lásd még"-ként)?
- **Az ID-k LÉTEZNEK a planben:** vesd össze a használt ID-kat a plan címsoraival (`grep -o '\[P-[A-Z0-9-]*\]' plan.md`) — nincs kitalált vagy elgépelt ID, és **sorszámos hivatkozás** (`§ 3.1`) sem maradt benne?
- **Nincs leltár-szekcióra mutató hivatkozás:** minden elsődleges hivatkozás `[P-…]`-ID-t viselő **végrehajtható** terv-szekcióra mutat. Ha egy taskhoz nem találtál ilyet, `tasks-questions.md` kérdés lett belőle (nem saját szöveggel pótoltad)?
- **Részhatókör-jelölés:** ahol **több task** hivatkozik ugyanarra az ID-ra, mindegyiken ott van a zárójeles hatókör (`(config fájlok)`, `(betöltő modul)`, `(unit teszt)`)?
- **Csoport-fejlécek:** minden `## <logikai csoport>` cím végén ott vannak a csoport által lefedett plan-ID-k?
- **`<sec:plan_coverage>` tábla teljes:** a plan **minden** `[P-…]` szekciója szerepel a táblában — vagy taskokkal, vagy `—` + egy mondatos indokkal? Nincs ID a planben, ami a táblából kimaradt, és nincs a táblában olyan ID, ami a planben nem létezik?
- **Duplikáció-tilalom (PID1/b):** nincs olyan task, amely a plan érték-listáját, kód→kód leképezését vagy lépéssorát **átmásolva** tartalmazza (a `[CHECK]`/`[OPS]` parancsok kivételével, azok karakterre egyeznek a plan-belivel)?
- **Plan `<sec:planned_changes>` lefedettség:** menj végig fájlonként — minden fájl kapott legalább egy taskot?
- **Plan `<sec:verification_strategy>` lefedettség:** menj végig a plan `<sec:verification_strategy>` szekciójának minden parancsán — mindegyik megjelent `[CHECK]` taskként valamelyik csoportban?
- **<sec:regression_impact> lefedve:** a plan `<sec:regression_impact>` táblázatának **minden sora megjelent-e taskként** — vagy `TREG` taskként a záró csoportban, **vagy** (ha a fájl a plan `<sec:planned_changes>` szekciójában is szerepel) **normál `Tnnn` taskként**? A `TREG` **definíció szerint csak azokra a fájlokra jár, amelyek a `<sec:planned_changes>`-ban NINCSENEK** — ami ott van, azt ne duplikáld `TREG`-ként. Ha a plan azt mondja, nincs érintettség, ez a csoport hiányozhat.
- **`[CHECK]` parancsok által futtatott fájlok létrehozása:** menj végig minden `[CHECK]` task parancsán, és nézd meg, milyen **fájlt vagy scriptet futtat** (pl. integrációs teszt script, futtató wrapper, seed script). Mindegyikre igaz kell legyen, hogy **vagy már létezik a repóban, vagy van rá létrehozó task korábban a listában**. Egy futtatandó, de sehol nem létrehozott állomány garantált bukás — ilyenkor vedd fel a hiányzó létrehozó taskot.
- **Ígért teszt → `[RED]` task:** ha a plan **szövegesen tesztelést ígér** valamire (jellemzően a `<sec:risks>` „kezelés" mondataiban, pl. *„a fallback logikát egységteszttel igazoljuk"*), akkor annak a logikának a `[GREEN]` taskja **előtt** szerepelnie kell egy `[RED]` teszt-írási tasknak. Ígéret teszt-task nélkül lefedettségi rés.
- **`tasks-input-from-prev.md` lezárva? (IP1)** — Ha a fájl létezik, nem maradhat benne `[ ]` tétel: mindegyik vagy beépült a `tasks.md`-be (task vagy sorrend-megkötés), vagy explicit indokkal elvetett. Ami a validálásnál lesz csak releváns, az a `validate-input-from-prev.md`-be került?

### A/2) Marker és destruktív műveletek

- **Artefaktum-hang (AV1)?** — A task-leírások cselekvő, konkrét utasítások az implementálónak; nincs bennük skill-hangú meta-szabály (`🔴`, „Tilos…", „a minőségellenőrzés bukik, ha…") és nincs átmásolt skill-magyarázat.
- **Marker minden taskon:** nincs prefix nélküli task — minden sor `[RED]`, `[GREEN]`, `[CHECK]` vagy `[OPS]` markert visel.
- **`[OPS]` helyesen használva?** — Menj végig az `[OPS]` taskokon: **mindegyik környezetet vagy artefaktumot módosít, nem repo-fájlt.** Ha egy `[OPS]` task fájl-útvonalat szerkeszt (tipikusan a `TREG` regressziós taskok), az **hibás besorolás** → `[RED]`/`[GREEN]`. A téves `[OPS]` besorolás elrontja a destruktív-művelet ellenőrzést.
- **Destruktív / osztott környezeti művelet teljes?** — Ha van olyan `[OPS]` task, amely **közös** környezetet módosít (osztott klaszter, közös registry, megosztott adatbázis), akkor a csoportjában szerepel-e (a) **jóváhagyás-kérő** task az eredeti állapot rögzítésével, (b) a művelet, (c) `[CHECK]` ellenőrzés, (d) feltételes **rollback** task? Ha a plan nem ad rollback-forgatókönyvet, az plan-hiányosság → `tasks-questions.md`.
- **Állapot-perzisztencia ellenőrzése:** ha egy task olyan shell-változóra hivatkozik (`$VAR`), amelyet **egy korábbi task** állít be, az **hibás** — a taskok külön shellben futnak, az érték üres lesz. Az állapot fájlba írandó és onnan olvasandó, vagy a parancsok egy taskba vonandók. Ez különösen a **rollbackre** kritikus: üres azonosítóval nem áll vissza semmi.

### B) TDD helyesség

- Minden `[RED]` taskhoz van párja `[GREEN]` task, és a RED megelőzi a GREEN-t?
- **TDD kötelezettség:** Minden új/módosított üzleti logikát megvalósító `[GREEN]` taskhoz tartozik-e egy azt közvetlenül megelőző `[RED]` (tesztíró) task? (Kivéve ha nem-TDD task, pl. konfiguráció, dokumentáció.)
- Minden task a plan végrehajtási sorrendjét követi?

### C) `[CHECK]` task minőség

- Minden logikai csoport végén van `[CHECK]` task konkrét paranccsal?
- **`[CHECK]` célzottság:** minden `[CHECK]` task célzott parancsot tartalmaz (pl. `npm test -- path/to/test.ts`), nem az egész suite-ot (`npm test`)? A regressziós és teljes E2E futtatás a validate fázis (07) feladata.
- **`[CHECK]` relevanciája:** a csoport záró `[CHECK]` taskja az adott csoport módosításait ellenőrzi — ne futtass más szekció tesztjeit egy csoport záróellenőrzéseként. Ha a csoport módosított kódjához nincs önálló egységteszt (pl. proxy konfiguráció, mock szerver route), typecheck vagy build check elegendő helyette.
- **Parancsok helyessége:** Minden bash parancs (különösen a `[CHECK]` taskokban szereplő `cd` parancsok utáni relatív útvonalak) valós és helyes? A `../../` típusú útvonalak gyakran kiugranak a projekt gyökeréből, kerüld a túlzott visszalépést, ellenőrizd az útvonal logikáját!
- **Regresszió futtatás nincs a tasks-ban:** ellenőrizd, hogy a tasks lista nem tartalmaz regressziós teszteket FUTTATÓ `[CHECK]` taskot — az a validate fázis feladata.
- **`[CHECK]` parancs ↔ `conventions.md` riport-kapcsolók:** nyisd meg a `conventions.md` `## <sec:cv_test_reporting>` tábláját, és vesd össze **soronként** minden `[CHECK]` parancsával. Ha az adott teszt-szintre kötelező riport-kapcsoló van előírva (pl. `--alluredir=allure-results`, `--reporter=…`, `--junitxml=…`), az **szerepeljen a parancsban**. Hiányzó kapcsoló → a 07 fázis riport-kapuja (TR3) bukik el a ciklus végén.
- **`⟂` párhuzamosítás validálva:** minden `⟂ Tkkk` jelölésnél a két task **fájlhalmaza diszjunkt**, és egyik sem futtatja azt, amit a másik ír. `[CHECK]` **soha** nem párhuzamos a saját tesztjét író/módosító taskkal (hamis zöld). Ha nem tudod eldönteni, **vedd le a `⟂`-t** — a szekvenciális futás sosem hibás.
- **Browser E2E marker:** ha egy UI/browser E2E teszt-író task az implementáció UTÁN áll, a markere `[GREEN]` (vagy `[RED]` + zárójeles indoklás) — nincs indoklás nélküli, sorrendben implementáció utáni `[RED]`.

### D) Task granularitás és előkészítés

- **Granularitás:** Van olyan task, ami 3 vagy több fájlt érint, vagy összetett logikát vezet be? Ha igen, bontsd fel.
- **Előkészítő lépések elkülönítése:** menj végig minden `[CHECK]`, `[RED]` és tesztelési taskon — ha bármelyik konfigurációs, előkészítő parancsot is tartalmaz (pl. kulcsgenerálás, docker build, env beállítás, tanúsítvány másolás), az előkészítő lépés kerüljön külön taskba, amely megelőzi a tesztelési taskot.
- **Gépi előfeltételek felszínre hozása:** menj végig a `[CHECK]` taskokon — ha bármelyik a projekt standard futtatási környezetén kívüli gépi feltételt igényel (machine-level env var, pl. `KEYCLOAK_HOME`; telepített külső szoftver; előre futó külső service), ezt a logikai csoport fejlécébe kell emelni blockquote-ban. Bele kell kerülnie: a konkrét env var neve + példaérték; ha a teszt egy külső service-t indít el, a teljes indítóparancs a kritikus flag-ekkel (pl. `kc.sh start-dev --features=token-exchange:v1`). Plan/spec hivatkozás önmagában nem elegendő — az információnak a task szintjén kell láthatónak lennie.
- **Valódi konténerizált tesztfutás:** Ellenőrizted, hogy a felvett `[CHECK]` és integrációs/E2E teszt-taskok valódi, konténerizált szolgáltatások ellen futnak-e le ahelyett, hogy a fejlesztői gépen manuálisan elindított natív folyamatokra hagyatkoznának?

### E) <sec:documentation_group> és TypeScript

- **Meglévő komponens README: NEM lehet task.** Ha a ciklus meglévő komponens konfigurációját (env var-ok, indítási paraméterek, külső kapcsolatok) változtatta meg, a `README.md` frissítése a **`08-doc-sync`** dolga — ha ilyen task bekerült (jellemzően `TLAST`-ként), **töröld**. **Kivétel:** **<status:op_new>** komponens első `README.md`-je, ami normál `Tnnn` `[GREEN]` taskként a komponens fájljai közé tartozik.
- **Nincs státusz-frissítő task?** — Nem szerepel olyan task, amely a `spec.md` / `plan.md` / `tasks.md` **státuszmezőjét** állítja át. Ez a `07-validate` dolga (keretrendszer-gépezet), nem implementációs lépés. Ha a spec DoD-ja ilyet kér, az spec-hiba → `tasks-questions.md`.
- **Architecture / generált dokumentáció (DS4):** **NE** generálj taskot a `docs-generated/architecture.md` (vagy a `docs-generated/` bármely fájlja) frissítésére, még új komponens/interfész/adatfolyam bevezetésekor sem — ezek **kizárólag a `08-doc-sync` fázis** gazdái, amely a teljes ciklus rálátásával komponálja és validálja őket. Az implementáció (06) a kódra koncentrál; az „as-built" dokumentáció a doc-syncben készül.
- **TypeScript rename ellenőrzés:** Ha a ciklus TypeScript interfész-, típus- vagy metódusnevet nevez át, ellenőrizd, hogy a plan `<sec:verification_strategy>` szekciója tartalmaz-e `typecheck` parancsot minden érintett npm package-hez. Ha igen, vedd fel [CHECK] taskként. Ha nem szerepel a planban, **ne találd ki magad** — a parancs csak akkor kerülhet taskba, ha a plan explicit felsorolja (a plan agent ellenőrzi a package.json-ban, hogy a script létezik-e).
- **Rename teljességi `[CHECK]`:** Ha a ciklus egy nevet (végpont, szimbólum, env-változó, fájlnév) **az egész projektben** cserél le, a <sec:documentation_group> csoport záró taskja legyen egy `[CHECK]`, amely a teljes repóban grep-eli a **régi nevet** annak minden alakváltozatában (pl. `init-cache`, `initCache`, `init_cache`, `InitCache`), kizárva a spec **<sec:out_of_scope>**-jában történetinek jelölt utakat (lezárt ciklusok `test-report`-jai, régi `spec.md`-k, `roadmap.md` múltbeli bejegyzései) és a `node_modules`/`.git` mappákat. A task akkor zöld, ha az élő forráson, dokumentáción (gyökér + app `README.md`, `docs/`, `.agent/`) és a verziókövetett build-kimeneten (`dist/`) **nulla** találat marad. Ha a `dist/` verziókövetett, ezt egy tiszta újrabuild (`dist` törlés + `npm run build`) előzze meg, mert a `tsc`/vite nem törli az átnevezett forrás orphan kimenetét.
<!-- INCLUDE:shared/path-format.md -->
- **Kapu-konfiguráció taskja (GC1):** ha a plan a `conventions.md` valamely szekciójának módosítását tervezi (riport-artefaktumok/útvonal-alap, Sonar, teszt-parancsok, portok, merge-stratégia), van rá **külön task** `[GREEN]` markerrel (repo-fájlt szerkeszt, tehát nem `[OPS]`)? Enélkül a 07 kapuja a régi konfigurációval fut.
- **Mechanikus kapu (M):** lefutott az `analyze-gate-check.py` a ciklus mappájára, és `0`-t adott? (A `<status:must_fix>` tételek gépiesen kimutatott hibák — státuszváltás előtt javítandók, nem a 05 hurkára hagyva.)
