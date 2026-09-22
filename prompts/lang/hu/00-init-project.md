<!--
  A `00-init-project` PROJEKT-NYELVI blokkjai (9.4 kiemelés).
  Ezt a fájlt a telepítő build-time emeli be az INCLUDE markerek helyére, a
  választott PROJEKT-nyelv (`PROJECT_LANG`) szerint; a marker alakja
  `lang/00-init-project.md#<horgony>`.
  A blokkok SZÓ SZERINT kerültek ide — ne fogalmazd át, ne egységesítsd.
  Az ANCHOR sorok NEM részei a beemelt szövegnek, csak határolók. Azért
  HTML-komment és nem `##` címsor a határoló, mert a sablonok maguk is tele
  vannak `##` címsorral (8.9).
  FIGYELEM: ebbe a vezető jegyzetbe ne kerüljön komment-lezáró szekvencia.
-->

<!-- ANCHOR:conventions-sablon -->

# Projekt konvenciók

## Projekt áttekintés

_A projekt célja egy-két mondatban. Mi a rendszer feladata?_

## Tech stack

- **Nyelv:**
- **Runtime:**
- **Framework:**
- **Csomagkezelő:**
- **Build eszköz:**
- **Konténerizáció:**

## Projekt referenciák

A fejlesztés és a doc-sync (08) során az alábbi globális tervezési, API és külső referencia-dokumentumok az irányadóak. Az ágens köteles ezeket figyelembe venni a ciklusok tervezésekor és a generált dokumentáció drift-összevetésekor:

- **HLD (High Level Design):** _(pl. docs/design/hld.md vagy hagyd üresen)_
- **LLD (Low Level Design):** _(pl. docs/design/lld.md vagy hagyd üresen)_
- **API Specifikáció / API-leírók:** _(pl. docs/api/openapi.yaml vagy hagyd üresen; ha ki van töltve, a 08-doc-sync DS22 Réteg 2 ellenőrzése összeveti vele a generált interfész/endpoint-leltárt)_
- **API design guideline / API-szabályzat (BD9):** _(pl. docs/api/guidelines.md vagy URL, vagy hagyd üresen — REST konvenciók, verziózás, hibaformátum, elnevezés. A 02–03 fázis ebből dolgozik. **Nagy dokumentum esetén** ne a teljes szöveg kerüljön ide: pointer + a `researcher`-rel készített tömör szabály-checklist — BD10.)_
- **Adatbázis Séma:** _(pl. docs/db/schema.sql vagy hagyd üresen)_
- **Külső / üzleti referencia-doksik:** _(pl. docs/poc.md, vendor dokumentáció, üzleti folyamatleírások vagy hagyd üresen)_
- **Branching-szabályzat (BD8/BD10, ha nagy dokumentum):** _(pointer + kivonat; a kis branching-szabály inkább szó szerint a `## Git és branching konvenciók`-ba)_

## Projekt struktúra

_A gyökér szintű mappák és szerepük. Például:_

- `src/` — fő alkalmazás forráskód
- `apps/` — önálló alkomponensek
- `test/` — tesztek (lásd részletesen lentebb)
- `docs/` — dokumentáció, OpenAPI leírók
- `specs/` — fejlesztési ciklus specifikációk

## Fejlesztési módszertan

Spec-driven development. A fejlesztés ciklusokra van bontva. A workflow két egyszeri setup lépésből és egy 8 lépéses per-ciklus loop-ból áll:

**Setup (egyszer):**
- `00` — projekt inicializálás
- `01` — ciklusok kezelése (`specs/roadmap.md`)

**Per-ciklus loop:**
- `02` — spec (`specs/cycle-NN-<cycle-name>/spec.md`)
- `03` — plan (`specs/cycle-NN-<cycle-name>/plan.md`)
- `04` — tasks (`specs/cycle-NN-<cycle-name>/tasks.md`)
- `05` — analyze (kereszt-fázisos konzisztencia ellenőrzés)
- `06` — implement (kód + `tasks.md` frissítése)
- `07` — validate (tesztek futtatása és DoD ellenőrzés)
- `08` — doc-sync (`docs-generated/` frissítése és konzisztencia-kapu)
- `09` — review & merge (a `## Review and merge` szekció szerint: `09` egyetlen lépésben — vagy `09a` create-pr → `09b` review → `09c` merge, PR feladása esetén; opcionálisan `09d` dev-test)

Minden ciklus mappája: `specs/cycle-NN-<cycle-name>/`

### Flow-választás (alapértelmezett munkamód)

A projektben kétféle flow közül lehet választani **feladatonként**:

- **Teljes flow (02–09):** nagyobb, összetett feladatokhoz — külön `spec.md` / `plan.md` / `tasks.md` + analyze/validate/doc-sync/review minőségi kapuk.
- **Egyszerűsített flow (`/bs-quick-flow`):** kis, jól körülhatárolt feladatokhoz (konfiguráció, egyszerűbb script, kisebb javítás) — háromfázisú `spec-plan.md` → `tasks.md` → implementáció.

**Alapértelmezett flow:** _<teljes | egyszerűsített>_ — _(a projekt jellege alapján kitöltve a 00 fázisban; pl. túlnyomóan konfiguráció/scriptelés/üzemeltetés → egyszerűsített; termékfejlesztés több komponenssel → teljes)_

A default csak a **kiindulópont**, feladatonként felülbírálható. Ha egy adott feladat nem illik a default flow-ba, az ágens jelzi és a másikat javasolja (lásd a `01-add-cycles` és `03a-write-code-plan` flow-méret ellenőrzését, illetve a `/bs-quick-flow` túlnövés-jelzését). A flow-váltás döntése mindig a felhasználóé.

## Git és branching konvenciók

- **Verziókezelő:** _(git | „NINCS verziókezelő (se GIT, se más), és nem is lesz." — BD11)_ — ha a „NINCS" flag van beírva, a 00/01 és a 02–09 fázisok **minden git-lépést kihagynak** (nincs branch, figyelmeztetés, commit).
- **Fő branch:** `main` — a ciklus-branch-ek leágazási bázisa (BD2). _(Projekt eltérhet, pl. `master`; a branch-logika ezt a mezőt olvassa.)_
- **Cycle branch:** minden fejlesztési ciklus **saját branch-en** él, `main`-ről ágazva (BD1–BD2). A branch a `specs/`, `docs/` és `src/` változásokat egyaránt tartalmazza.
- **Branch nyitás:** a **ciklusok kezelése fázisban (01)** jön létre, a ciklus legelején (nem a 02/06-ban); a 00 init maga a `feature/init-project` branch-en fut (BD12).
- **Branch-elnevezési stratégia (BD8):** _(default: `feature/cycle-NN-<name>`; ha van Jira-prefix / más szervezeti szabály / pointer egy dokumentumra, ide)_ — a **mappanév** ettől függetlenül mindig prefix nélkül, tisztán `cycle-NN-<name>` (BD3).
- **Merge / visszaintegrálás:** a `## Merge stratégia` szekció szerint (PR vagy közvetlen merge; ha nincs döntés/remote, default a közvetlen merge — BQ7), a 09 sikeres lefutása után; ugyanez a szekció adja a 00 init-branch visszaintegrálását is (BD7/BD15).
- **Commit granularitás:** taskonként egy commit.

## Merge stratégia

_A ciklus lezárásakor (09 fázis) ezt használja az ágens. A 00 fázisban tisztázandó, és az access-t **ki kell próbálni** — a `conventions.md` nem zárható le, amíg a választott szolgáltatóhoz sikeresen hozzá nem férünk (vagy a felhasználó alternatívát/lokális merge-et választ)._

_**Egyetlen igazságforrás a visszaintegrálásra (BD15):** ez a szekció adja meg, hogyan kerül vissza `main`-be **bármely** elkészült branch — a ciklus-branch (09), a 01/00 branch-figyelmeztetés (BD6), és a 00 saját `feature/init-project` branch-ének visszaintegrálása (BD12) is ebből dolgozik. Ha nincs explicit döntés vagy remote, a **default a közvetlen merge `main`-be** (nem PR — BQ7)._

- **Szolgáltató:** GitHub | Bitbucket Cloud | Bitbucket Server | GitLab | Lokális (nincs PR)
- **Repository URL:** _(Bitbucket on-prem esetén az API endpoint is)_
- **Authentication:** CLI (`gh` / `glab` / `bb`) | token (env var név) | SSH
- **PR target branch:** _(alapból `master`)_
- **Merge típusa:** squash | merge commit | rebase
- **Branch védelem:** _(ha van — pl. CI check, review követelmény)_
- **Access teszt parancs:** _(példa — lásd lent)_

_Access validáció szolgáltatónként (a 00 fázis futtatja, sikeres exit/HTTP 200 kell):_
- _GitHub: `gh auth status` + `gh repo view <repo>`_
- _Bitbucket Cloud: `curl -u <user>:<token> https://api.bitbucket.org/2.0/repositories/<ws>/<repo>` → HTTP 200_
- _Bitbucket on-prem: `curl -u <user>:<token> <api-url>/rest/api/1.0/projects/<key>/repos/<repo>` → HTTP 200_
- _GitLab: `glab auth status` + `glab repo view <repo>`_
- _Lokális: nincs validáció_

## Review and merge

_**A ciklus utolsó fázisát ez a szekció vezérli (RM8):** van-e PR, hol fut a review és a merge, van-e merge utáni teszt-kör (`VP2`), van-e dev-telepítéses e2e kör (`VP3`), mi történik bukásnál, és mit hív a CI. **A szekciónév, a mezőnevek és az értékek angol literálok** — ezeket gép olvassa, ezért nyelvfüggetlenek (ugyanaz a szabály, mint a `[local]`/`[remote]` jelöléseknél és a teszt-kategória-azonosítóknál); a magyarázó próza a projekt nyelvén marad._

- **PR submission:** yes | no
- **SDD mode:** isolated | centralized
- **Post-merge tests:** yes | no
- **Skip post-merge tests if master unchanged:** yes | no
- **Dev deployment test (bs-dev-test):** yes | no | n/a
- **Dev deployment command:** _(csak ha a `Dev deployment test` értéke `yes` — a telepítést végző, szó szerinti parancs)_
- **Failure handling:** notify | auto-fix-loop
- **Notification channel:** slack | teams | command | none
- **Notification secret (env var):** BS_NOTIFY_WEBHOOK
- **Notification command:** _(csak ha a csatorna `command`)_
- **CI agent:** claude-code | cursor | copilot | antigravity | command
- **CI agent command:** _(csak ha a `CI agent` értéke `command`)_

_**Melyik skill fut — a `PR submission` dönti el, nem az `SDD mode`:**_
- _`no` → **egyetlen** skill: `/bs-review-and-merge` (09)._
- _`yes` → **három** skill: `/bs-create-pr` (09a) → `/bs-review` (09b) → `/bs-merge` (09c)._
- _`Dev deployment test: yes` → a merge után még egy fázis: `/bs-dev-test` (09d)._

_**Post-merge tests (`VP2`).** A kör a **ciklus ágán** fut: előbb behozzuk a fő branch-et a ciklus ágába, utána épül és fut a teszt-kör a friss `main`-nel egyesített kódon, és **csak zöld eredmény után** történik a beolvasztás (izolált úton), illetve a push (központosított úton). Hogy **mely** tesztek futnak benne, azt a `plan.md` gépi futtatási táblájának `Fázis` oszlopa mondja meg (`post-merge` érték) — quick-flow ciklusban a `spec-plan.md` `## Merge tesztek` szekciója. A kör a **statikus réteget is** futtatja (Sonar, ugyanazokkal a küszöbökkel, mint a `07`), mert az egyesítés olyan kódot hoz be, amit a `07` Sonar-köre sosem látott. A bizonyíték a ciklus `test-report/post-merge/` mappájába kerül — sikernél és bukásnál egyaránt._

_**Skip post-merge tests if master unchanged.** Ha a fő branch nem ment előre a ciklus ága óta, a `VP2` kör ugyanazt mérné, amit a `07` az imént lemért. `yes` esetén ilyenkor a kör kihagyható (a kihagyás ténye és oka a riportba kerül); `no` esetén mindig lefut._

_**Dev deployment test (`VP3`).** Csak `SDD mode: centralized` mellett értelmes: a sikeres merge után egy automatizmus telepíti a terméket egy teljesen integrált teszt-környezetbe (`Dev deployment command`), és valódi e2e tesztek futnak rá. A teszt-válogatás a `Fázis` oszlop `dev-test` értéke; a részletes környezet-recept (compose, mockok, tesztadat) a `specs/test-conventions.md`-be tartozik (TC1/c). A bizonyíték a ciklus `test-report/dev-test/` mappájába kerül._

_**Failure handling.** `notify` (alapértelmezés): a riport a ciklus útvonalára kerül, a fejlesztőt a `notify.py` értesíti, a javítást **ember** indítja. `auto-fix-loop`: a CI-n önjavító hurok indul, a `07` hurkának változatlan leállási korlátaival (per-item 3 egymást követő / 5 összes bukás, 5 egymást követő FAIL-futás, majd eszkaláció emberhez)._

_**Notification.** A titok **kizárólag környezeti változóban** él, a szekcióba csak a változó NEVE kerül (ugyanaz a szabály, mint a `## Merge stratégia` `Authentication: token (env var név)` mezőjénél) — egy webhook-URL parancssori argumentumként a transzkriptbe, a `check-log.md`-be és a CI-naplóba is beszivárogna. A `none` **legitim, kimondott válasz** (egyszemélyes PoC), de nem az, ami hallgatásból következik. Az e-mail külön backendet nem kap: a `command` érték lefedi (`msmtp`, `sendmail`, céges script), ahogy a Jirát vagy a PagerDutyt is._

_**CI agent.** A központosított úton a CI a `ci-run-skill.sh <skill> <ciklus-útvonal>` adaptert hívja, az pedig az itt megnevezett ágenst indítja nem-interaktív módban. **Az ágenst előre tisztázzuk és ki is próbáljuk** (`ci-run-skill.sh --selftest`), ugyanúgy, ahogy a merge-szolgáltató access-ét: egy nem-interaktív futtatás, ami először éles PR-en derül ki, hogy nem megy, a legrosszabb helyen bukik el. **🔴 Mérve (2026-09-22): az `antigravity` ág CI-ben nem használható** — a CLI 1.107.0 szerkesztő-alkalmazás, headless módja nincs; a selftest ezt ki is mondja. Ilyen esetben `CI agent: command` (a platform saját, esemény-vezérelt PR-integrációja vagy bármely más parancs)._

_**Érvényességi szabályok** (a `00` a beíráskor ellenőrzi, mert konfigurációs hibát ott olcsóbb elkapni, mint minden ciklus végén):_
- _`SDD mode: centralized` + `PR submission: no` → **elutasítva** (a központosított út definíció szerint PR-triggerelt);_
- _`Dev deployment test: yes` + `SDD mode: isolated` → **elutasítva** (a `VP3` csak központosított úton értelmes);_
- _`Dev deployment test: yes` esetén a `Dev deployment command` **kötelező**;_
- _`Notification channel` ≠ `none` esetén a `Notification secret (env var)` **kötelező**;_
- _`Notification channel: command` esetén a `Notification command`, `CI agent: command` esetén a `CI agent command` **kötelező**;_
- _**No-VCS projektben az egész szekció `n/a`**, és a ciklus a `08-doc-sync` után lezárul — a `bs-review-and-merge` / `bs-create-pr` / `bs-review` / `bs-merge` / `bs-dev-test` egyike sem fut._

## Teszt struktúra

```
test/
  unit/          — izolált függvénytesztek, minden dependency mockolva, gyors
  integration/   — komponens szintű tesztek, külső HTTP/service határok mockolva
  e2e/           — teljes rendszer fut, valós vagy realisztikus mock service-ek
  performance/   — terhelési és stressztesztek, külön tooling
  mocks/         — újrahasználható mock szerverek, test double-ok, fixture-ök
  helpers/       — tesztek között megosztott segédfüggvények, report generátorok
```

### Tesztelési elvek

- Új üzleti logikához unit test kötelező.
- Új API végponthoz vagy service integrációhoz integration test kötelező.
- Új teljes folyamathoz (user story szintű) e2e test kötelező.
- Mock szerverek a `test/mocks/` mappába kerülnek, újrafelhasználhatóan.
- Minden tesztkör önállóan futtatható és cleanup után állapotmentes.

## Teszt keretrendszer

_Az alábbiak **ajánlott default-ok** modern, korszerű eszközökkel (lokális fejlesztői használatra). Nem kötelezőek: az agent a 00 fázisban explicit egy körben rákérdez — „A javasolt teszt stack: <default>. Megfelelő, vagy mást szeretnél (pl. Cypress, Jest, Vitest, go test)?" — és a fejlesztő döntését rögzíti. Innentől ez a szekció a single source of truth: a 03/07 fázis erre hivatkozik, nem ismétli meg a tool-nevet._

- **Frontend E2E:** Playwright _(ajánlott — alternatíva: Cypress)_
- **Backend tesztek:** Python — `pytest` + `httpx` _(ajánlott — alternatíva: a projekt nyelvének natív keretrendszere, pl. Jest/Vitest Node, go test Go)_
  - Tesztfájlok helye: `test/` (a projekt test struktúrájának megfelelő almappában) — _embernek szóló tájékoztatás; a **gépi felderítés** kategóriánkénti globjait a `## Teszt-futtatás` szekció `### Tesztfájl-helyek` táblája adja (RP1: itt ne duplikálj értéket)_
  - Python test függőségek: `requirements-test.txt` vagy `pyproject.toml [test]` szekció
- **E2E infrastruktúra:** `docker compose` — konténerizált teljes stack
  - E2E compose fájl: `docker-compose.e2e.yml` a projekt gyökerében
- **Mock eszközök:** _projekt-specifikusan töltendő ki — milyen mock framework-öket, szervereket, stub eszközöket használunk_

## Teszt-riportolás

_**Kötelező szekció (TR3).** Minden ciklus `specs/cycle-NN-<name>/test-report/` mappájába be kell kerülnie a projekt teszt-eszközének **saját, megnyitható riportjának** (Allure HTML, Playwright HTML, pytest-html, JUnit XML, coverage-riport stb.) — a chat `/clear` után nincs, a riport az egyetlen utólag ellenőrizhető bizonyíték. Ezt a táblázatot a `07-validate` **determinisztikus kapuval** (`report-gate-check.py`) kéri számon: hiányzó artefaktum → a validálás nem zárható PASS-ra. Az oszlopsorrend kötött._

_**Hova kerülnek (TR5):** a riportok nem közvetlenül a `test-report/` gyökerébe, hanem **körönkénti almappákba** mennek — `test-report/validate/round-01/`, `round-02/`, … a validálási körökhöz (a review a 07 körének 2. lépése, nem kap külön mappát). Így egy önjavító hurok minden körének megmarad a saját bizonyítéka, és a `validation-report.md` lépés-táblájában jelzett bukáshoz megnyitható a hozzá tartozó riport. **A táblázat utolsó oszlopa a KÖR-MAPPÁHOZ képest relatív útvonal** (fájl vagy mappa) — a kör-mappát a hívó fázis adja át a `test-runner`-nek és a kapunak (`--report-subdir`)._

**Riport-generálás kötelező:** igen
**Artefaktum-útvonal alapja:** kör-mappa
**Riport-fázisok:** validate
**Test manager:** none
**Test manager alak:** —
**Test manager token env var:** —
**Test manager fázisok:** dev-test
**Test manager kötelező:** nem
**Test manager parancs:** —

_**Riport-fázisok (TR6).** A mező sorolja fel, MELY fázisok kötelesek a fenti artefaktum-készletet előállítani: `validate` (a 07 teljes körei — ez az alapérték), `implement` (a 06 záró állapota), `post-merge` (a merge utáni `VP2` kör) és `dev-test` (a `/bs-dev-test` `VP3` köre) — vesszős felsorolásban (`implement, validate, post-merge`). Ha az `implement` is szerepel, a 06-implement a státuszváltás előtt legenerálja a készletet a `test-report/implement/` fázis-mappába, és ugyanaz a `report-gate-check.py` zárja. Ha nem, a 06 csak a `check-log.md`-t írja, és a bizonyítékot a 07 első TELJES köre adja. **A `post-merge` és a `dev-test` fázist a `## Review and merge` szekció kapcsolja be** (`Post-merge tests`, `Dev deployment test`); ha ott be van kapcsolva, ide is fel kell venni, különben a `report-gate-check.py` nem keresi a kör artefaktumait. A mező nélküli, régi projekt viselkedése változatlan (`validate`). **Mikor éri meg az `implement`?** Ha az implementációs futásnak önálló bizonyíték-értéke van (böngészős képernyőképek, REST audit-naplók, hosszú E2E), amit a 07 köre már nem reprodukál ugyanabban az állapotban._

_**A jelölő kötelező (TR5/b).** Az utolsó oszlop jelentése 2026-08-07-én megváltozott (`test-report/` gyökér → **kör-mappa**), a formátuma viszont nem — egy régi tábla ezért csendben félreértelmeződne. A `report-gate-check.py` a jelölő hiányában **nem találgat**: `exit 2` + a pótlandó sor. Elfogadott érték: `kör-mappa` (mai séma) vagy `test-report` (régi, flat séma — ilyenkor a kapu a `test-report/` gyökérhez oldja fel az útvonalakat). Meglévő projekt migrációja: írd be a jelölőt a valós sémával, és ha a ciklus most tér át a mai sémára, a `conventions.md` átírása **a ciklus része** (lásd a 03 „Kapu-konfiguráció együtt mozog" szabályát)._

_**Határvonal a `specs/test-conventions.md`-hez (TC1/c):** ide, a `conventions.md`-be tartoznak a **riport-artefaktumok, az útvonal-alapjuk és a riport-generáló parancsok** — ezt olvassa a TR3 kapu. A `specs/test-conventions.md`-be tartoznak a **teszt-receptek és koordináták** (hogyan indul a stack, milyen hívás, milyen teszt-user), amit a 08-doc-sync tart karban. Riport-layout vagy riport-parancs változik → **`conventions.md`**; „hogyan fut / mi kell hozzá" változik → **`test-conventions.md`**; ha mindkettő → **mindkettő**. A kettő összekeverése a leggyakoribb forrása annak, hogy a 07 kapuja a régi helyen keres._

| Teszt-kategória | Eszköz | Riport-generáló parancs | Artefaktum a kör-mappában |
|---|---|---|---|
| E2E | Playwright (+ Allure) | `npx playwright test --reporter=html && npx allure generate ./allure-results --single-file -o ./allure-report` | `allure-report.html` |
| Unit / integrációs | _a választott futtató_ | `<riport-generáló parancs>` | `unit-report.html` |
| Lefedettség | _pl. c8 / coverage.py_ | `<parancs>` | `coverage/` |
| Alkalmazás-oldali audit / REST kérés-válasz | _a szolgáltatás saját napló-írása_ | _a teszt-futás mellékterméke — a naplózás bekapcsolása a parancs_ | `e2e/rest-logs/` |

_Kitöltési szabályok:_
- **Egyfájlos HTML-t preferálj** (`allure generate --single-file`, `--reporter=html` egy fájlba), mert a riport a ciklus git-diffjébe kerül. Ha az eszköz csak mappát tud (pl. teljes Allure static site), az is elfogadható — akkor a mappa neve `/`-re végződjön (`allure-report/`).
- Ha egy kategóriához nincs riport-artefaktum, az utolsó oszlopba `-` kerül (a kapu kihagyja azt a sort).
- **🔴 A REST-naplók TESZT-SZERINTI almappákba mennek:** `<artefaktum>/<local|remote>/<teszt-név>/`. A `local`/`remote` szint **nyelvfüggetlen**, és a **teszt saját jelöléséből** következik (nem a hívott címből — egy `oc port-forward` mögötti `127.0.0.1` **remote**, egy compose service-név pedig **local**). A teszt-név a teszt-függvény neve, útvonal-biztosra normalizálva: **minden `[^A-Za-z0-9._-]` karakter `-`-re, a széleken lévő `-` levágva, kisbetűsítés NINCS** (`test_foo[dsp01]` → `test_foo-dsp01`; a paraméter **nem** lesz külön alkönyvtár). A `07` kapuja (`RL1`/`RL2`) erre a szerkezetre joinol: megnézi, hogy a `remote/` alatti naplók tartalmaznak-e valóban nem-lokális címet, és hogy minden `[remote]`-nak jelölt forgatókönyv termelt-e naplót. Enélkül a napló **egy lapos halom**, amelyből utólag nem állapítható meg, melyik teszt mit hívott — és egy korábbi körből örökölt fájlokkal teli mappa **telinek látszik**. _(A TR3 tábla artefaktum-cellája NEM változik — marad `e2e/rest-logs/`; az új szintek az ALÁ kerülnek, és a `report-gate-check.py` `rglob`-bal járja be a mappát, tehát a beágyazott szerkezetet változtatás nélkül látja.)_
- **Az alkalmazás-oldali bizonyíték is TÁBLASOR, nem próza.** Ami a teszt-futás alatt keletkezik és utólag megnyitható — REST kérés/válasz audit-napló, korrelációs-azonosító nyom, alkalmazás-log-kivonat —, azt ugyanúgy vedd fel a táblába, mint a teszt-eszköz riportját. Amit a tábla nem kér, azt a `report-gate-check.py` **nem is keresi**: csendben elmarad, és a hiánya csak hónapokkal később derül ki. A fájlnév- és fejléc-konvenciót a `specs/test-conventions.md` rögzíti (TC1/c), a **kötelezőség** viszont ide tartozik.
- **Ha a projekt egyáltalán nem generál teszt-riportot**, a fenti flaget írd `nem`-re, **indoklással** (pl. „csak manuális smoke-teszt van"). Ez tudatos, rögzített döntés — a kapu ilyenkor kihagyódik. Üresen hagyni vagy kitöltetlen táblázatot hagyni **nem** opció: a kapu ilyenkor használati hibát jelez.

_**Test manager integráció (TM1–TM10) — opcionális, alapból KIKAPCSOLVA.** A keret nem ír elő külső test managert: `Test manager: none` mellett nulla új lépés és nulla új hálózati függés van. A commitolt `test-report/` készlet marad **az egyetlen** ciklus-bizonyíték; a test manager a **másik tengely** — cikluson átnyúló trend, flaky-detektálás, hibák ok szerinti csoportosítása —, amit a git nem tud megőrizni. **A feltöltés soha nem bizonyíték** (TM7): a `report-gate-check.py` egy URL-t tartalmazó, artefaktum nélküli riport-készletet ugyanúgy elutasít, mint ma._

_**A mezők jelentése:**_
- _`Test manager`: `none` (alap) · `testdino` · `reportportal` · `qase` · `command` — melyik adapter fut. `none` esetén a többi mező elhagyható._
- _`Test manager alak`: `reporter` (a kliens a teszt-futtató reporter-láncában fut és futás közben streamel — pl. TestDino) vagy `import` (a kész `junit.xml`-t egy parancs utólag tolja fel — pl. ReportPortal, Qase). A két alak nem helyettesíthető egymással._
- _`Test manager token env var`: a változó **NEVE**, sosem az értéke — egy test manager API-token osztott platform credential (TC5), a `conventions.md`-be soha nem kerülhet. A `test-manager.py` maga olvassa ki a környezetből, és **soha nem kap tokent parancssorban**._
- _`Test manager fázisok`: vesszős felsorolás — `implement` · `validate` · `post-merge` · `dev-test` · `ad-hoc`. **Alapérték: `dev-test`**, mert a `VP3` kör termeli a legtöbbet érő adatot, a `07` (`VP1`) pedig nem válhat token- és hálózatfüggővé: az sértené az izolált SDD üzemmódot. Az `ad-hoc` a cikluson kívüli `/bs-run-tests` futásokra vonatkozik — ezek metaadata `cycle=none`, tehát a `D8`/`KT6` bizonyíték-tűzfal a szolgáltatónál is látszik._
- _`Test manager kötelező`: `igen` · `nem` (alap) — buktassa-e a fázist a feltöltés bukása. Alapból **nem**: ha a bizonyíték már commitolva van, egy 502-es SaaS nem érvényteleníthet egy zöld tesztkört. Az eredmény viszont sosem marad jelöletlen: a kör riportjába és a `results.json`-ba `uploaded <url>` / `FAILED <ok>` / `skipped (<fázis> nincs a listán)` sor kerül._
- _`Test manager parancs`: szó szerinti parancssor, **csak** `command` providernél — ezzel TestRail, Xray, Allure TestOps vagy bármi más beköthető a keret módosítása nélkül._

_**Kitöltött példa (TestDino, `reporter` alak):** `Test manager: testdino` · `Test manager alak: reporter` · `Test manager token env var: TESTDINO_TOKEN` · `Test manager fázisok: dev-test` · `Test manager kötelező: nem`. A riporter-blokk beírása a projekt `playwright.config.ts`-ébe **a projekt dolga** (a keret ehhez nem nyúl), a recept helye a `specs/test-conventions.md` (TC1/c). ⚠ A TestDino `reporter` csomagja **Node ≥ 22.12**-t követel: régebbi Node-on be sem töltődik, és ezzel az egész teszt-futást megöli — ezért próbálja a `test-manager.py --mode preflight` a riporter **betölthetőségét**, nem csak az env var meglétét._

## Teszt-futtatás

_**Kötelező szekció (KT1).** Ez a szekció a **cikluson kívüli** teszt-futtatás egyetlen gépi igazságforrása: a `/bs-run-tests` segédparancs ebből olvassa ki, mely kategóriát milyen paranccsal futtasson, és a `08-doc-sync` teszt-leltára (`docs-generated/test-description.md`) ebből deríti fel, milyen tesztfájlok léteznek. A **ciklus**-szintű futtatást továbbra is a `plan.md` gépi futtatási táblája adja (TP4) — a kettő nem helyettesíti egymást: ez a szekció projekt-szintű és ciklus-független, az pedig egy ciklus egy körére szól._

**Teszt-kategóriák:** unit, rest-e2e, ui

_A projekt kategória-szótára, vesszővel felsorolva (ajánlott alap: `unit` · `rest-e2e` · `ui`, opcionálisan `coverage`). A `plan.md` gépi futtatási táblájának `Kategória` értékei ennek a halmaznak a **részhalmazai** kell legyenek — ezt az `05-analyze` mechanikus kapuja ellenőrzi (KT2). A kategória-azonosítók **nyelvfüggetlenek** (útvonalra és kapura joinolnak: `test-runs/<kategória>/…`), ezért ne fordítsd le őket._

### Projekt-szintű futtatási tábla

_Az oszlop-séma **azonos** a `plan.md` gépi futtatási táblájával (TP4/b) — egy parser, egy szabály. A `run-tests.py` FIX oszlop-pozíciókkal olvas, tehát az első oszlop mindig a `Kategória`, és a sorrend nem cserélhető fel. A `Típus` oszlop értékei (`gyors` / `nehez`) a szkript `--type` kapcsolójának nyelvfüggetlen értékei — ezeket nem fordítjuk._

| Kategória | Típus | Előfeltétel | Parancs | Eredményfájl | Formátum | Takarítás | Környezet | Fázis |
|---|---|---|---|---|---|---|---|---|
| unit | gyors | — | `<szó szerinti parancs, gépi riporterrel>` | `junit.xml` | junit | — | lokális | — |
| rest-e2e | nehéz | `<a cél elérhetőségi probe-ja>` | `<parancs a cél-hosttal>` | `<fájl>` | junit | `<lebontás>` | `<remote — a cél-környezet neve>` | — |

_Kitöltési szabályok:_
- **A `Fázis` oszlop itt `—`:** ez **kimondott jelölés** („nem fázis-kötött"), nem üres cella és nem hallgatólagos alapértelmezés — a cikluson kívüli futásnak nincs fázisa. A `/bs-run-tests` fázis-szűrő nélkül hívja a szkriptet, tehát a szűrő ága le sem fut. **A `plan.md` gépi táblájában viszont az üres cella HIBA** (PH1): ott minden sor explicit, vesszős felsorolást visel (`implement`, `validate`, `post-merge`, `dev-test`).
- **A `{round}` és a `{phase}` helyőrző itt is működik:** a `/bs-run-tests` a `test-runs/…` futás-mappát adja át `--round-dir`-ként, tehát a `{round}` arra oldódik fel — nem ciklus-mappára.
- **EV-szabályok érvényesek:** a `remote` környezetű sor parancsa **literálisan** tartalmazza a cél-hostot (EV3), és van hozzá `Előfeltétel`-probe ugyanarra a célra (EV4); `localhost` / `127.0.0.1` deklarált port-forward nélkül **TILOS** (EV5). A `run-tests.py` ezt futásidőben is méri (`exit 4`).

### Tesztfájl-helyek

_A **gépi felderítés** globjai, kategóriánként. Ez a `test-inventory-check.py` (LD5) egyetlen bemenete, és ez az **egyetlen szabályozott hely**, ahol a teszt-leltár hatóköre szűkíthető: ami itt nincs deklarálva, azt a leltár-kapu nem is keresi._

| Kategória | Glob |
|---|---|
| unit | `test/unit/**/test_*.py` |
| rest-e2e | `test/e2e/**/*.spec.ts` |
| ui | `test/ui/**/*.spec.ts` |

_A `## Teszt keretrendszer` szekció prózai „Tesztfájlok helye" sora **embernek** szól és megmarad — de értéket nem duplikál: a gépiesen olvasott globok **kizárólag itt** élnek (RP1: egy fogalom, egy hely). Ha egy kategóriának nincs tesztfájlja, a `Glob` cellába `—` kerül; a kategória akkor is a szótár része marad._

## Naming konvenciók

- **Fájlok:** `kebab-case`
- **TypeScript osztályok:** `PascalCase`
- **Függvények, változók:** `camelCase`
- **Környezeti változók:** `UPPER_SNAKE_CASE`
- **Unit tesztfájlok (TypeScript):** `<modul>.test.ts`
- **Unit tesztfájlok (Python):** `test_<modul>.py`
- **E2E scriptek:** `cycle-NN-<leírás>.sh`

## Portok és service-ek

_Az alkalmazás komponenseinek portjai. Például:_

| Komponens | Port |
|-----------|------|
|           |      |

## Környezeti változók

_A projekt szintű `.env` fájl helye és a kötelező változók listája._

## Sonar minőségellenőrzés

_(Hagyd ki ezt a szekciót, ha a projekt nem használ SonarQube-ot.)_

- **Sonar szerver indítása (Podman):** `podman run -d --name sonarqube -p 9000:9000 docker.io/library/sonarqube:community`
- **Scanner futtatás:**
  - TypeScript/JavaScript: `podman run --rm --network=host -v ".:/usr/src" docker.io/sonarsource/sonar-scanner-cli -Dsonar.projectKey=<project-key> -Dsonar.host.url=http://localhost:9000 -Dsonar.token=<token>`
  - Java (Maven): `mvn sonar:sonar -Dsonar.host.url=http://localhost:9000 -Dsonar.token=<token>`
  - _(további nyelvek: scanner parancsot a projekt struktúrájához igazítva tölts ki)_
- **Projekt kulcs (`sonar.projectKey`):** _töltsd ki a projekt azonosítójával_
- **Sonar host URL:** `http://localhost:9000` _(a `sonar-gate.py` innen kérdezi le a Quality Gate-et az API-n)_
- **Token env-változó:** `SONAR_TOKEN` _(a tokent SOHA ne írd ide — csak a változó nevét; a `sonar-gate.py` a `SONAR_HOST_URL` / `SONAR_PROJECT_KEY` / `SONAR_TOKEN` env-változókat is elfogadja)_
- **Quality Gate elvárás:** PASSED — a `07-validate` fázisban blokkol, amíg nem teljesül. A kaput a `sonar-gate.py` értékeli az API-ból (QG státusz + bukott feltételek + BLOCKER/CRITICAL/MAJOR findingek), nem a riport LLM-es elolvasásával
- **Sonar riport helye:** a validálási kör mappája — `specs/cycle-NN-<cycle-name>/test-report/validate/round-NN/sonar-report.md` (+ `.html`); automatikusan generálódik a validálás során, körönként külön (TR5)

## Kockázatok és ismert korlátok

_Projekt szintű technikai korlátok, elfogadott POC határok._

<!-- ANCHOR:BD11-vcs-kerdes -->
*„Van a projektben verziókezelő (git)? Ha nincs, tervezel-e bevezetni?"*

<!-- ANCHOR:BD11-nincs-vcs-flag -->
„NINCS verziókezelő (se GIT, se más), és nem is lesz."

<!-- ANCHOR:flow-kerdes -->
*„Milyen jellegű feladatok lesznek túlnyomórészt ebben a projektben? (a) Termékfejlesztés / új funkciók, több komponenst érintő, összetett logika → **teljes berki spec flow** (02–09); (b) Konfiguráció, scriptelés, üzemeltetés, kisebb javítások → **egyszerűsített flow** (`/bs-quick-flow`). Ez lesz az alapértelmezett munkamód; feladatonként felülbírálható."*

<!-- ANCHOR:teszt-stack-kerdes -->
*„A javasolt teszt stack: <default>. Megfelelő, vagy mást szeretnél?"*

<!-- ANCHOR:TR3-riport-kerdes -->
*„Milyen riportot generál a teszt-eszközötök, és milyen paranccsal? (pl. Allure HTML, Playwright HTML report, pytest-html, JUnit XML, coverage) — ez minden ciklusban bekerül a `specs/cycle-NN-<name>/test-report/` mappába — körönkénti almappákba —, és a validálás determinisztikus kapuval ellenőrzi a meglétét."*

<!-- ANCHOR:KT1-futtatas-kerdes -->
*„Milyen teszt-kategóriákra bomlik a projekt tesztkészlete (pl. `unit`, `rest-e2e`, `ui`, `coverage`), melyik kategóriát milyen **szó szerinti paranccsal** futtatom le a teljes projektre, és hol vannak a kategória tesztfájljai (glob)? Ezt a cikluson kívüli futtatás (`/bs-run-tests`) és a teszt-leltár felderítése használja — a ciklus-szintű futtatást továbbra is a `plan.md` táblája adja."*

<!-- ANCHOR:KT7-gitignore-felajanlas -->
> *„A `test-runs/` mappa most nincs kizárva a verziókezelésből. Ide a `/bs-run-tests` cikluson kívüli teszt-futtatásai írnak: gépfüggő, bármikor újragenerálható eredmények, amelyek a keret bizonyíték-logikájában amúgy sem számítanak (D8). Javaslom felvenni a `.gitignore`-ba a `test-runs/` bejegyzést. Felvegyem?"*

<!-- ANCHOR:BD9-api-guideline-kerdes -->
*„Van követendő API design guideline / API-szabályzat (REST konvenciók, verziózás, hibaformátum, elnevezés)? Ha igen, hol a dokumentuma?"*

<!-- ANCHOR:RM8-review-merge-kerdes -->
*„Hogyan zárul a ciklus ebben a projektben? (a) **Van-e PR feladás**, vagy a ciklus ága közvetlenül, a te gépeden kerül vissza a fő branch-re? (b) A review és a merge a **te gépeden** fut (izolált SDD), vagy a PR triggereli a CI/CD-t, és ott, **emberi beavatkozás nélkül** megy (központosított SDD)? Ez dönti el, hogy a ciklus végén egyetlen skill fut (`/bs-review-and-merge`), vagy három (`/bs-create-pr` → `/bs-review` → `/bs-merge`)."*

<!-- ANCHOR:VP2-post-merge-kerdes -->
*„Legyen-e **merge utáni teszt-kör** (`VP2`)? Ez a ciklus ágán fut, miután behoztuk a friss fő branch-et, és **a beolvasztás előtt** bizonyítja, hogy a kód a masterrel egyesítve is a spec szerint működik (tesztek + Sonar). Ha igen: **kihagyható-e**, amikor a fő branch nem ment előre a ciklus ága óta? És központosított úton legyen-e utána **dev-telepítéses e2e kör** (`/bs-dev-test`, `VP3`) — ha igen, milyen paranccsal telepítünk dev-környezetbe?"*

<!-- ANCHOR:CS6-ertesites-kerdes -->
*„Ha a merge utáni vagy a dev-teszt kör bukik, **hogyan értesüljön róla a fejlesztő**? (`slack` / `teams` / szabad `command` / `none`.) A titok soha nem kerül a `conventions.md`-be — csak a környezeti változó NEVE. A `none` legitim válasz egyszemélyes projektben, de **kimondott** válasz legyen, ne hallgatás. És bukásnál mi történjen: `notify` (ember javít) vagy `auto-fix-loop` (a CI önjavító hurka indul)?"*

<!-- ANCHOR:CI-agent-kerdes -->
*„Központosított úton **melyik ágens fut a CI-ben** (`claude-code` / `cursor` / `copilot` / `antigravity` / szabad `command`)? A `claude-code`, a `cursor` és a `copilot` hívható nem-interaktív (print) módban; az **`antigravity` viszont NEM** — a CLI-je (1.107.0) szerkesztő-alkalmazás, a prompt GUI chat-session-t nyit, tehát display nélküli CI-futtatón nem fut le: ott a `command` ág a becsületes válasz. A hitelesítés (API-kulcs, költség) és az engedély-modell ezen felül is platformonként más — ezért most ki is próbáljuk."*

<!-- ANCHOR:TM3-test-manager-kerdes -->
*„Használtok **külső test managert** (TestDino, ReportPortal, Qase, TestRail, Xray …), ahova a teszteredmények cikluson átnyúlóan felkerülnek? Ez **opcionális, alapból kikapcsolva** (`none`) — a ciklus bizonyítéka a commitolt riport marad, a test manager a trend- és flaky-adatot adja hozzá. Ha igen: melyik szolgáltató, és a kliense a teszt-futtató **reporter-láncába** kerül (`reporter`), vagy a kész `junit.xml`-t **utólag tolja fel** egy parancs (`import`)?"*

<!-- ANCHOR:zaro-uzenet -->
   *"A projekt konvenciók rögzítve. A következő fázis indítása előtt mindenképpen futtass egy `/clear` parancsot a kontextus kiürítéséhez, majd megkezdhető a ciklusok kezelése: `/bs-add-cycles`."*
