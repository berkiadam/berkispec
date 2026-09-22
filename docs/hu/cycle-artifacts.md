# Egy ciklus artifact fájljai

← [Vissza a főoldalra](../../README-HU.md) · [Oldalindex](README.md)

## 10. Egy ciklus artifact fájljai

Minden ciklus saját mappát kap: `specs/cycle-NN-<cycle-name>/`

| Fájl | Fázis | Tartalom |
|------|-------|----------|
| `spec.md` | 02 | Üzleti viselkedés, követelmények, érintett területek, mock stratégia, Definition of Done. A DoD-pontok **stabil `DoD-NN` azonosítót** (DI1) és — erősen ajánlottan — **`· _bizonyíték:_`** mezőt kapnak (DI2: tesztnév / `cmd:` / `manual:`), amiből a 07 a `dod-check.py`-jal **gépi joinnal** értékel, LLM-ítélet nélkül. |
| `spec-questions.md` | 02 | A specifikációval kapcsolatos nyitott kérdések. A spec csak akkor `Tervezésre kész`, ha itt nincs `- [ ]`. |
| `plan.md` | 03 | Technikai végrehajtási terv, érintett komponensek, tervezett módosítások, teszt/ellenőrzési stratégia. **Önhordó:** a spec minden tesztesete és `DoD-NN` pontja leképződik plan-tesztesetre (TP1, `Spec-lefedettség` tábla), a `test-conventions.md` receptjei fizikailag bemásolva (TC1/a), a **környezet-felkészítés** (token-beszerzés, stack-indítás, egyedi komponens build/deploy/rollback, seed) szó szerinti parancsokkal (TP3), a kötelező **`## Környezeti koordináták`** szekció (KO1: komponens base URL-ek, portok, health endpointok, szó szerinti indító/leállító parancsok, példa REST hívások a token-beszerzéssel, teszt- és API-userek jelszavakkal, minden paraméter — placeholder és üres cella nélkül, a `C6` kapuval kikényszerítve), a **konfiguráció-életút** minden futtatási módra (KF1) és a **fordított lefedettség** (minden plan-képességhez spec-forrás — SC1) — a lezárás előtt kötelező a teljes *Lezárási kapu* (TP2). Kötelező része a **`### Gépi futtatási tábla (run-tests.py)`** (TP4): kategória / típus (`gyors`\|`nehéz`) / előfeltétel / parancs / eredményfájl / formátum / takarítás / környezet / **fázis** (PH1: `implement`\|`validate`\|`mindkettő`; üres = mindkettő) — ebből futtat a 07 szkripttel, így a nyers teszt-log nem kerül LLM-kontextusba. Hiánya esetén a 07 a `test-runner` subagentre esik vissza. Szintén kötelező a **`### Teszt-forgatókönyvek`** szekció (TS1): tesztesetenként egy `TS-NN` blokk `DoD-NN` hivatkozással, `Mit tesztelünk` / `Előfeltétel` / lépés-tábla / `Takarítás` sorokkal — a lépés-tábla minden sora **szó szerint futtatható hívást** és **konkrét, ellenőrizhető elvárt eredményt** hordoz, REST-lépéseknél pedig a blokk `.http` alakban is tartalmazza a hívást (TS8) (a „sikeresen lefut" jellegű megfogalmazást a TS3 kemény padlója kizárja). Ez a `bs-manual-test-plan` `TG-NN` csoportjainak elsődleges forrása. A forgatókönyvek **tervezését** a `TD0–TD6` recept vezeti (`shared-hu/test-scenario-design.md`): dimenzió-leltár a darabszámhoz (TD1), megfigyelési négyes a tartalomhoz (TD2 — megszámolt mellékhatás, közvetlenül kiolvasott állapot, negatív kontroll), megszámolhatóság (TD3), izoláció-igazolás (TD4), kalibrációs minta (TD5) és lezárás előtti önteszt (TD6). Minden `[P-…]` bejegyzés visel **`Cél és indoklás`** sort (WY1: mi lesz igaz a változás után, milyen bajt szüntet meg, melyik `DoD-NN`-ből következik), a `Spec-lefedettség` tábla minden sora megnevez egy `TS-NN`-t (TS7 — a spec teszteseteit konvertálni kell, nem prózaként átmásolni), és minden `#### <tesztfájl path>` fejléc alatt ott a **teszt-artefaktum adatlap** (TA1: `Futtatás` · `Fixture-ök és tesztadat` · `Teszt-esetek`). Kötelező a **`**Cél-környezet:**`** mező (EV1) és a futtatási tábla **`Környezet`** oszlopa (EV2): nem-lokális kategóriánál a cél-host a **parancsban** áll (EV3), az `Előfeltétel` ugyanoda hív elérhetőségi probe-bal (EV4), és `localhost` tilos (EV5). |
| `plan-questions.md` | 03 | A tervezési szakasz nyitott kérdései. A plan csak akkor `Task írásra kész`, ha itt nincs `- [ ]`. |
| `tasks.md` | 04 | Checkboxos task lista (`[RED]`/`[GREEN]`/`[CHECK]`/`[OPS]` jelölésekkel — marker minden taskon kötelező) + prerequisite dokumentumok. Osztott környezetet érintő destruktív `[OPS]` műveletnél kötelező a jóváhagyó és a rollback task. **Plan-kapcsolat (PID1):** minden task a plan stabil `[P-…]` szekció-azonosítójára hivatkozik (nem sorszámra), egy elsődleges forrásra, több task esetén részhatókör-jelöléssel; a csoport-fejlécek felsorolják a lefedett plan-ID-kat, a fájl végén pedig kötelező a `Plan-lefedettség` fordított tábla (plan-szekció → taskok) **és a `Teszt-lefedettség` tábla** (TT1: minden `TS-NN` forgatókönyv és minden gépi tábla-kategória → létrehozó task + futtató task, vagy indok). **Belépő kapu (EG1):** a fázis első lépése az `analyze-gate-check.py --plan-only` tényleges lefuttatása — a plan státusz-mezője önbevallás, bukó kapunál nincs tasks lista. A `[CHECK]` parancsa a plan teszt-adatlapjának egy fájlra szűkített parancsa, és két `[CHECK]` nem írhat `>`-tal ugyanabba a logfájlba (T6). **Teszt-kapcsolat (TI2/TX1):** minden teszt-író és teszt-futtató task a sor végén `— test [TC-01]` / `— test [TS-03]` alakban hivatkozik a plan tesztesetére, és **minden futtatandó teszt külön checkbox** — egy `[CHECK]` pontosan egy azonosítót futtat, teszt-szűrős paranccsal. |
| `tasks-questions.md` | 04 | A tasks szakasz nyitott kérdései (főleg az 05 fix-mód használja). A `tasks.md` csak akkor `Implementálásra kész`, ha itt nincs `- [ ]`. |
| `cycle-design-input.md` | létrehozza: 01 · **kitölti: a felhasználó** · fogyasztja: **02, 03** | Ciklus design input (CD1): a felhasználó saját szavaival írt, szabad formájú ciklus-specifikáció (elvárások, vázlat, példák). A 01 üres sablonként hozza létre a ciklus mappájában és felhívja rá a figyelmet; **kitöltése opcionális**. Ha van benne tartalom, a `bs-write-spec` a **viselkedési** részét dolgozza fel (a `roadmap.md` bejegyzése mellett, elsődleges bemenetként), a `bs-write-code-plan` pedig automatikusan beolvassa és a **technikai/eljárás-jellegű** részét emeli — önhordóan — a `plan.md`-be. Egyik fázis sem írja át a fájlt. |
| `spec-input-from-prev.md` | írja: 01 · fogyasztja: **02** | Fázisok közötti átadás (IP1): a 01-ben elhangzott, de a roadmap-be nem illő viselkedési részletek. Csak ha van átadandó infó. |
| `plan-input-from-prev.md` | írja: 01, 02 · fogyasztja: **03** | A spec-ből kivett vagy a kutatás során felszínre került technikai/implementációs részletek. |
| `tasks-input-from-prev.md` | írja: 02, 03 · fogyasztja: **04** | Előkészítő lépések és sorrend-megkötések a task-bontáshoz. |
| `validate-input-from-prev.md` | írja: 03, 04 · fogyasztja: **07** | Futtatási előfeltételek és üzemeltetési tudnivalók a validáláshoz (pl. „a stack indítása előtt VPN kell"). |
| `analyze/analyze-report.md` | 05 | Kereszt-fázisos konzisztencia jelentés (PASS/FAIL), 6 kategória (1+3., 2+5. és 4. az `analyzer` három hatóköre, 6. az `analyzer-exec`), **a kapu által generált** lefedettségi mátrix és `Plan-szekció ↔ task` tábla (az orchestrátor szó szerint fűzi be, majd az `Érintett DoD-sorok` szerint javítja), **végrehajthatósági leltár**, **Hurok-napló** (az önjavító hurok iterációnkénti audit-nyoma). **Az analízis minden fájlja a ciklus `analyze/` almappájában él** (AD1). |
| `analyze/analyze-task.md` | 05 | A **triázsban (TR1) jóváhagyott javítási lista** — a fixer-subagentek kizárólag ennek nyitott tételein dolgoznak. Ide csak az kerül, amit a felhasználó javításra jelölt (plusz a mechanikus kapu tételei, kérdés nélkül); az elvetett tételek külön szekcióban maradnak, ez a későbbi körök szűrésének memóriája. Egyetlen írója az orchestrátor. |
| `analyze/slices/` | 05 | A mechanikus kapu `--emit-slices` kimenete: a három szemantikai `analyzer`-kör bemenete, a tervezési dokumentumok szó szerinti kimetszéseként. `.gitignore`-ral rejti magát, nem kerül commitba. |
| `imp-decision.md` | 06 | Implementációs döntési napló: nem egyértelmű megoldások és a 3-próba szabály utáni leállások. |
| `test-report/implement/` | 06 | **Hivatalos fázis-mappa (TR6).** Mindig tartalmazza a `check-log.md`-t; ha a `conventions.md` `**Riport-fázisok:**` mezője felsorolja az `implement`-et, akkor a 06 záró állapotának teljes riport-készletét is (ugyanaz a tábla, ugyanaz a `report-gate-check.py` kapu, `--report-subdir test-report/implement`). Ha nem, a bizonyítékot a 07 első TELJES köre adja. |
| `test-report/implement/check-log.md` | 06 | A `[CHECK]` futások append-only naplója: idő, task, hányadik próba, mód (normál / validate-loop), a **ténylegesen kiadott parancs** és a darabszámok (`X passed / Y failed / Z skipped`) — a bukott próbák is. Enélkül az implementációs fázisból csak a `- [x]` pipa maradna, ami állítja a zöldet, de nem bizonyítja (a chat `/clear` után nincs). |
| `test-report/validation-report.md` | 07 | **A `## Kör N` blokkokat a `round-log.py` írja** (open/step/close), a `# Validation History`-t a `failure-counter.py` — az orchestrátor csak a szabad szöveges mezőket adja. Validációs futástörténet, regressziós/Sonar hibák, consecutive failures számlálók — egyben az **07 önjavító hurok naplója** (LC2), a megszakított futás horgonya. A körök **típusa is látszik** (TELJES / KÖNNYŰ — VD10): a költséges lépések (E2E, regresszió, Sonar, review) csak az első és a záró megerősítő körben futnak, a köztes javító körökben a teljes gyors teszt-készlet. PASS **kizárólag teljes körből** adható. |
| `test-report/validate/round-NN/` | 07 | Körönként külön mappa a kör **összes** teszt-artefaktumával (a `conventions.md` `## Teszt-riportolás` táblája szerint: Allure/Playwright HTML, coverage, JUnit XML) **és** a `sonar-report.md`/`.html`-lel. A mappa száma = a `## Kör N` sorszáma; korábbi körök mappái sosem íródnak felül (TR5). |
| `manual-test-plan.md` | *(nem fázis — `/bs-manual-test-plan`, az 05 után bármikor)* | Kézi tesztterv: `Környezet és indítás` (komponens, port, health endpoint, szó szerinti indító/leállító parancs), `Tesztadatok` (userek jelszóval, tokenek, seed, takarítás — TC5 titok-szabállyal), `Automata tesztek` (a plan gépi futtatási táblája + az eredmények helye), `TG-NN` **kézi tesztcsoportok** (mit tesztelünk · előfeltétel · lépés-tábla konkrét elvárt eredménnyel · `curl` **és** `.http` blokk · takarítás), `Nem kézzel tesztelhető` (MT10: indoklás + mi fedi), `Lefedettség` (`DoD-NN → TG-NN`) és `Változásnapló`. **Kétmódú:** `Tervezett` (a tervből, valós kódon nem verifikált) vagy `As-built` (a kódhoz ellenőrizve — eltérésnél a kód nyer). Determinisztikus kapu: `manual-test-gate-check.py` (MG1–MG10). **Nulla visszacsatolás:** a 07 és a 09 nem kapuz rá, eredményfájl nem készül. |
| `doc-sync-plan.md` | 08 | A `doc-sync-planner` per-fájl pipálható terve a `docs-generated/` frissítéséhez (mit kell tenni / nincs teendő + drift-megállapítások). A végrehajtás **és** a megszakítás-utáni folytatás determinisztikus horgonya (a fő ágens pipálja). |
| `doc-sync-questions.md` | 08 | A doc-sync döntési pontjai és kapu-bukásai (`Knn`). A fő ágens kérdez egyenként; nyitott `[ ]` kérdésnél a fázis megáll. Sosem törlünk, csak `[x]`. |
| `test-report/code-review.md` | 07 | A `reviewer` ágens code review jelentése: `MF-NN` **Must Fix** (blokkol) + `S-NN` **Suggestions** (nem blokkol). Nincs benne napló — a review körei a `validation-report.md` `# Validation History`-jába kerülnek, a teszthibákkal közös számlálón. Nyitott finding esetén a `tasks.md` `## Review javítások` szekciója is keletkezik. |

### 10.1 Fázisok közötti átadás (`*-input-from-prev.md`)

**Milyen problémát old meg (IP1):** egy fázisban rendszeresen felszínre kerül olyan információ, ami **értékes, de nem oda tartozik** — túl technikai, túl részletes, vagy egyszerűen a következő fázis dolga. A skillek eddig ezt **törlésre** utasították: a `02-write-spec` szó szerint azt írja, hogy „ha egy mondat technológiát, fájlnevet, függvényt nevez meg → az plan-be való, töröld a spec-ből". Vagyis az infó a kukába ment, nem a következő fázisba — a `03` pedig újra felderítette (vagy nem). Ezek a fájlok adnak neki **célt a kuka helyett**.

| Fájl | Ki írhat bele | Ki fogyasztja |
|---|---|---|
| `spec-input-from-prev.md` | 01-add-cycles | **02**-write-spec |
| `plan-input-from-prev.md` | 01, 02 | **03**-write-plan |
| `tasks-input-from-prev.md` | 02, 03 | **04**-write-tasks |
| `validate-input-from-prev.md` | 03, 04 | **07**-validate |

Mind a ciklus mappájában (`specs/cycle-NN-<name>/`). **Egy fázis több fájlba is írhat** ugyanabban a futásban, ha az infót szét kell szórni (pl. a 02-ben felmerülő technikai részlet a `plan-input`-ba, a belőle következő tesztelési előfeltétel a `validate-input`-ba). A **06-implement** szándékosan nem kap sajátot: az eleve beolvassa a `plan.md`-t és a `tasks.md`-t, tehát az implementációs részlet oda tartozik.

**A legnagyobb „táplálója" a 02 koordináta-kiszűrése (KX).** A spec-be leggyakrabban **környezeti koordináták és eljárás-leírások** szivárognak be (remote hostok, `localhost` portok, image-nevek, deploy-parancsok, teljes deployment-runbookok a `Teszt specifikáció` szekcióban), mert hasznos infónak tűnnek. A `02-write-spec` ezért egy **kötelező kiszűrő rutint** futtat — új spec írásakor **és** meglévő spec újrafutásakor is —, ami ezeket felismeri és **áthelyezi** (nem törli) a `plan-input-from-prev.md`-be, a spec-ben pedig szimbolikus hivatkozást hagy (`{PUBLIC_BASE_URL}`). Az elhatárolás egyetlen szabályban: **az endpoint-útvonal szerződés (spec), a host / base URL / port / namespace / image / parancs koordináta (plan)**. A `03a-write-code-plan` ennek a tükrét futtatja: ha a spec túl technikai maradt, az adatot **átemeli a planbe** és jelzi a felhasználónak (a `spec.md`-t nem írja át) — mert a `plan.md`-nek **önhordónak** kell lennie: a `test-runner` kizárólag azt olvassa, tehát ami nem ott van, az soha nem fut le.

**A fogyasztó oldalon a hivatkozás nem elég (dereferencing).** Az átadott tétel gyakran magas absztrakciós szinten fogalmaz (*„képfájl build és push a registrybe a `build.sh` futtatásával"*). A `03a-write-code-plan` **nem reprodukálhatja a bemenet absztrakciós szintjét**: ha egy tétel scriptre, eljárásra, meglévő tesztre vagy külső API-ra **hivatkozik**, a hivatkozást **fel kell oldania a forrásból** — a script tényleges parancsai, a registry-host, a teljes JSON payload minden kötelező mezővel —, és a konkrétumot a `plan.md`-be írnia, forrás-megjelöléssel. Nagy vagy szétszórt forrásnál a `researcher` subagentet hívja, **literál értékeket kérve**; a researcher erre kapott egy szűk kivételt a „soha nem nyers fájltartalom" szabálya alól (rövid, szó szerinti részletek: parancs, URL, payload, szignatúra — de nem teljes fájl, és titok helyett pointer). Ez azért kritikus, mert a `04`, a `06` és a `test-runner` **már nem látja a spec-et és a forrást**: ami nem került a `plan.md`-be, az számukra nem létezik.

**Tétel-formátum** — checkbox-lista, a kérdés-fájlok mintájára, forrás-megjelöléssel:

```md
- [ ] I01 — [az átadott információ] _(forrás: 02-write-spec)_
- [x] I02 — [az átadott információ] _(forrás: 01-add-cycles)_ → beépítve: plan.md „Tervezett módosítások"
- [x] I03 — [az átadott információ] _(forrás: 02-write-spec)_ → elvetve: a ciklus scope-ján kívül
```

**Szabályok:**

- **Sosem törlünk** — a lezárt tétel `[x]` + egy soros megjegyzés (`→ beépítve: <hova>` / `→ elvetve: <miért>`).
- **Nem blokkol menet közben**, de a **fázis lezárásakor nem maradhat nyitott tétel**: minden fogyasztó fázis minőségellenőrzésében kötelező pont, hogy minden tétel vagy beépült, vagy **explicit indokkal elvetett**. Csendben átlépni tilos — ez a védőháló egy gyengébb modell ellen, amely különben ignorálná a fájlt.
- **Nem kérdez.** Határvonal a `*-questions.md`-hez: a **kérdés** = „nem tudom, döntsd el"; az **input-from-prev** = „tudom, de nem ide tartozik". Ami eldöntendő kérdés is, az kérdésként megy a saját fázis `*-questions.md`-jébe.
- **Üres váz nem készül** — a fájl csak akkor jön létre, ha van mit beleírni; a hiánya nem hiba (ugyanaz az elv, mint a `test-conventions.md`-nél).
- **Ami nem a következő fázisba, hanem egy későbbi CIKLUSBA tartozik**, az a `specs/roadmap.md`-be megy, nem ide. Ami pedig a **jövő összes ciklusában** kell (visszatérő teszt-elvárás), az a `specs/test-conventions.md`-be — annak a `08-doc-sync` a gazdája.
- **Az önjavító hurkok fix-módjai (05/07/09) teljesen figyelmen kívül hagyják** ezeket a fájlokat — sem nem olvassák, sem nem írják. A fix-mód célzott javítás egy `Must Fix` listára; az átadás-mechanizmus újrafuttatása ott csak költség és zaj lenne.
- **Az 05-analyze read-only diagnózisa viszont figyeli:** az `s2-coverage` kör a `spec-`/`plan-`/`tasks-input-from-prev.md` nyitott `[ ]` tételét **lefedettségi hiányként** jelzi (a `validate-input`-ot nem, mert annak a fogyasztója utána fut). A `Must Fix` azt nevezi meg, **mi maradt ki** a `spec.md`/`plan.md`/`tasks.md`-ből — nem a pipálást kéri, hiszen a fixer ezeket a fájlokat nem írja.
- A **`quick-flow`** nem érinti: háromfázisú, egy kontextusban fut, nincs mit átadni fázisok között.

A mechanizmus közös leírása egyetlen helyen él — `prompts/shared-hu/input-from-prev.md` —, amelyet a telepítő **build-time inline** beágyaz a hivatkozó skillek (`01`, `02`, `03`, `04`, `07`) telepített változatába; a skill csak a saját, fázis-specifikus részét írja a marker körül (mit olvas be, mely fájlokba írhat).

---

## 12. Kérdéskezelés (spec-questions.md / plan-questions.md / tasks-questions.md / doc-sync-questions.md)

A spec (02), plan (03) és tasks (04) fázisban az ágens nyitott kérdéseit külön fájlban tartja nyilván. A `tasks-questions.md` elsősorban az 05 önjavító hurok fix-módját szolgálja (de a normál 04 flow is hivatkozhat rá). A **08-doc-sync** ugyanezt a mintát követi a `doc-sync-questions.md`-vel: a döntési pontok és a DS22 kapu-bukások `Knn`-ként ide kerülnek, a fő ágens egyenként kérdez, és nyitott `[ ]` kérdésnél a fázis megáll (a subagent — `doc-sync-planner` — sosem kérdez közvetlenül).

**Struktúra:**
```md
# Cycle NN: <cím> — Spec/Plan/Tasks kérdések

- [ ] K01 — [kérdés szövege]
- [x] K02 — [kérdés szövege] → [döntés / válasz röviden]
- [ ] K03 — [kérdés szövege] _(K02-ből merült fel)_
```

**Szabályok:**
- Egyszerre **egy** kérdés kerül a felhasználó elé — az ágens megvárja a választ.
- A listából **soha nem törlünk** — lezárt kérdést `[x]`-szel jelölünk, a döntés megmarad.
- Új kérdés a lista végére kerül a következő `Knn` számmal.
- A fázis csak akkor zárható le, ha minden kérdés `[x]` és a felhasználó explicit megerősítette.

**Az analyze-hurok kérdés-folyama (05):** az önjavító hurok fixer-subagentjei (`spec/plan/tasks-fixer`) is **ide** írnak kérdést, amihez valódi döntés kell — de **nem kérdeznek közvetlenül a felhasználótól**. A kérdést az **orchestrátor (05-analyze)** teszi fel, a párbeszédben **fázis-prefixszel**: `SPEC/K07`, `PLAN/K03`, `TASKS/K02` (a fájlokban a kérdés sima `Knn` marad — a fájl helye kódolja a fázist). A user-felé minden kérdés fázis-fejlécet kap: `[FÁZIS · iter n/max X · FÁZIS/Knn]`.

**Státuszátmenetek:**

| Állapot | Feltétel |
|---------|----------|
| `Piszkozat` | Fázis indításakor |
| `Nyitott kérdések vannak` | Van legalább egy `[ ]` kérdés |
| `Tervezésre kész` / **`Teszt-tervezésre kész`** / `Task írásra kész` / `Implementálásra kész` | Minden `[x]` + minőségellenőrzés átment + felhasználó megerősítette |

> **A `plan.md` státusz-lánca két lépcsős (03a → 03b):** `Tervezésre kész` (spec) → **`Teszt-tervezésre kész`** (a `03a` zárja a kód-tervet) → `Task írásra kész` (a `03b` zárja a teszt-tervet). A `Teszt-tervezésre kész` **nem** fázis-vég a ciklus szempontjából: a `04`-et ezzel indítani hiba, a belépő kapuja (EG1) meg is fogja.

**Loop-markerek (LC1).** Amikor egy önjavító hurok visszanyit egy dokumentumot javításra, a státusz a fázis-megfelelő nem-kész értéket egy **suffix-markerrel** kapja (pl. `Piszkozat [analyze-loop]`, `Implementálásra kész [validate-loop]`). A marker jelentése egységes: **fix-mód aktív** → a fixer a státuszt automatikusan lépteti (felhasználói megerősítés nélkül; a user csak a kérdéseknél és a végső PASS-nál lép be), és a marker egyben a megszakítás-utáni folytatás horgonya. Lezáráskor (PASS / tiszta review) lekerül; feladáskor (`max X` / 3-próba / `max 5` / eszkaláció) a megrekedt állapot jelzésére a dokumentumon marad.

| Marker | Hurok / visszanyitott dokumentum | Fixer | Napló |
|---|---|---|---|
| `[analyze-loop]` | 05-analyze / tervezési doksik (`spec`/`plan`/`tasks`) | `spec`/`plan`/`tasks-fixer` | `analyze/analyze-report.md` (Hurok-napló) + `analyze/analyze-task.md` |
| `[validate-loop]` | 07-validate / `tasks.md` | `implement-fixer` (teszt/Sonar/DoD) és `review-fixer` (Must Fix) — mindkettő 06 fix-mód | `validation-report.md` `# Validation History` |

---

## 13. Egységes `Kész` státusz-lifecycle

Minden dokumentum a saját fázis-specifikus záró-státuszát kapja a keletkezésekor (`spec.md` → `Tervezésre kész`, `plan.md` → `Teszt-tervezésre kész`, majd `Task írásra kész`, `tasks.md` → `Implementálásra kész`), majd **`Kész`-re lép, amint a validate (07) PASS lezárja a ciklust**. Így a 08-doc-sync és a ciklusvég merge-ága a `spec.md`/`plan.md`/`tasks.md`-t már egységesen `Kész` státuszban várja.

> **A dokumentum-státusz és a CIKLUS állapota két különböző dolog.** A három dokumentum `Kész` marad a merge után is — azok tényleg elkészültek. Hogy a **ciklus** kész-e, azt az utolsó engedélyezett verifikációs pont dönti el (`VP1` = a `07`, `VP2` = post-merge kör, `VP3` = dev-teszt): amíg az hátravan, a roadmap ciklus-sora `⏳ verifikációra vár` jelölést visel, és a generált `cycle-status.md` mutatja, mi van hátra. Így egyetlen `Kész`-t váró kapu sem bővül tételesen.

---
