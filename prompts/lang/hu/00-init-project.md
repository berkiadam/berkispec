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
- `09` — review & merge (review + merge a conventions.md Merge stratégiája szerint)

Minden ciklus mappája: `specs/cycle-NN-<cycle-name>/`

### Flow-választás (alapértelmezett munkamód)

A projektben kétféle flow közül lehet választani **feladatonként**:

- **Teljes flow (02–09):** nagyobb, összetett feladatokhoz — külön `spec.md` / `plan.md` / `tasks.md` + analyze/validate/doc-sync/review minőségi kapuk.
- **Egyszerűsített flow (`/bs-quick-flow`):** kis, jól körülhatárolt feladatokhoz (konfiguráció, egyszerűbb script, kisebb javítás) — háromfázisú `spec.md` → `tasks.md` → implementáció.

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
  - Tesztfájlok helye: `test/` (a projekt test struktúrájának megfelelő almappában)
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

_**Riport-fázisok (TR6).** A mező sorolja fel, MELY fázisok kötelesek a fenti artefaktum-készletet előállítani: `validate` (a 07 teljes körei — ez az alapérték), `implement` (a 06 záró állapota), vagy mindkettő (`implement, validate`). Ha az `implement` is szerepel, a 06-implement a státuszváltás előtt legenerálja a készletet a `test-report/implement/` fázis-mappába, és ugyanaz a `report-gate-check.py` zárja. Ha nem, a 06 csak a `check-log.md`-t írja, és a bizonyítékot a 07 első TELJES köre adja. A mező nélküli, régi projekt viselkedése változatlan (`validate`). **Mikor éri meg az `implement`?** Ha az implementációs futásnak önálló bizonyíték-értéke van (böngészős képernyőképek, REST audit-naplók, hosszú E2E), amit a 07 köre már nem reprodukál ugyanabban az állapotban._

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

<!-- ANCHOR:BD9-api-guideline-kerdes -->
*„Van követendő API design guideline / API-szabályzat (REST konvenciók, verziózás, hibaformátum, elnevezés)? Ha igen, hol a dokumentuma?"*

<!-- ANCHOR:zaro-uzenet -->
   *"A projekt konvenciók rögzítve. A következő fázis indítása előtt mindenképpen futtass egy `/clear` parancsot a kontextus kiürítéséhez, majd megkezdhető a ciklusok kezelése: `/bs-add-cycles`."*
