---
phase: 00
name: bs-init-project
description: "berkispec - 00. Használd a projekt legelső indításakor (Phase 00), vagy ha a gyökér 'conventions.md' hiányzik/hiányos. A fejlesztővel közösen rögzíti a globális projektkonvenciókat (tech stack, teszt, fejlesztési flow, git merge stratégia) a 'conventions.md'-ben — ez minden további fázis előfeltétele."
prerequisites: []
output:
  - "conventions.md (projekt gyökér)"
prev: null
next: bs-add-cycles
subagents:
  - "agents/researcher.md"
shared:
  - "shared/git-preflight.md"
---
# 00 — Projekt inicializálás
## Kontextus ellenőrzés

Ha azt detektálod, hogy ennek a fázisnak a futtatása most indul (ez az első prompt a fázisban), de a kontextus nem „friss” (azaz a beszélgetési előzmények tartalmaznak korábbi fázisokból vagy futásokból származó üzeneteket), akkor kérdezz rá a felhasználónál:
> *„Úgy tűnik, hogy a fázis indításakor a kontextus nem teljesen friss. Szándékosan nem futtattál `/clear`-t az új fázis megkezdése előtt (a tokenekkel való spórolás érdekében)?”*
Várd meg a felhasználó válaszát, mielőtt folytatnád a fázis futtatását.

---

Ez a prompt egyszer fut le, új projekt indulásakor. Célja a projekt konvencióinak rögzítése, amelyekre az összes fejlesztési ciklus (02–09) hivatkozni fog.

---

## Git-előkészítés — az init saját branch-en fut (BD12)

A `00-init-project` **maga is feature branch-en dolgozik**, alapértelmezett néven `feature/init-project`. **Csirke-tojás sorrend:** a git *elérhetőségét* már itt, az elején detektáld; a „van-e (és lesz-e) verziókezelő" formális rögzítése (BD11) lentebb, a kérdéseknél történik.

1. **Git-elérhetőség detektálása:** `git rev-parse --is-inside-work-tree` (vagy `git rev-parse --git-dir`).
   - **Ha nincs git / nem git-repo** → **ne** hozz branch-et, **ne** PR-ezz/merge-elj. Folytasd közvetlenül a konvenciók rögzítésével; a lenti VCS-kérdés (BD11) rögzíti a `conventions.md`-be a „NINCS VCS" flaget.
   - **Ha van git** → futtasd a branch-nyitó preflightet (lent), majd hozz létre és válts az init-branch-re:

<!-- INCLUDE:shared/git-preflight.md -->

2. **Branch létrehozása (csak git esetén):** a friss, tiszta `main` után `git switch -c feature/init-project`. Az init innentől ezen a branch-en dolgozik (a `conventions.md` írása, commit).
3. **Visszaintegrálás a futás végén:** lásd „Lezárás" — a `conventions.md`-be rögzített `## Merge stratégia` (BD7/BD15) szerint PR vagy közvetlen merge `main`-be; ha nincs döntés/remote, a **default a közvetlen merge** (BQ7).

---

## Feladatod

Hozz létre egy `conventions.md` fájlt a projekt gyökerében az alábbi struktúra szerint. Minden szekciót a felhasználóval közösen töltötök ki — tegyél fel kérdéseket, ahol a döntés nem egyértelmű. A struktúrában szereplő technológiák (pl. Playwright, pytest) és beállítások **ajánlott default-ok**; ezeket a projekt tényleges tech stackje alapján testre kell szabni (pl. Node/Jest, Go/go test stb.).

Az alábbi szekcióknál **aktívan rá kell kérdezned** (nem elég csak pre-fillelni):

- **Verziókezelő megléte (BD11 — KAPU, elsőként):** *„Van a projektben verziókezelő (git)? Ha nincs, tervezel-e bevezetni?"* A git *elérhetőségét* már a „Git-előkészítés" lépésben detektáltad; itt a szándékot rögzíted. Ha **nincs és nem is lesz**, írd a `## Git és branching konvenciók` szekcióba **explicit**: „NINCS verziókezelő (se GIT, se más), és nem is lesz." Ez a flag **kapuzza** a 01 (és a többi fázis) összes git-lépését: ott ekkor nincs `git switch -c`, nincs branch-figyelmeztetés, nincs commit — csak a `specs/cycle-NN-<name>/` mappa + roadmap készül.
- **Alapértelmezett flow:** kérdezz rá a feladatok jellegére, és ez alapján rögzíts egy default munkamódot: *„Milyen jellegű feladatok lesznek túlnyomórészt ebben a projektben? (a) Termékfejlesztés / új funkciók, több komponenst érintő, összetett logika → **teljes berki spec flow** (02–09); (b) Konfiguráció, scriptelés, üzemeltetés, kisebb javítások → **egyszerűsített flow** (`prompts/skills/sdd-lightweight-flow.md`). Ez lesz az alapértelmezett munkamód; feladatonként felülbírálható."* A választ a `## Fejlesztési módszertan` szekció **Alapértelmezett flow** mezőjébe írd.
- **Teszt keretrendszer:** *„A javasolt teszt stack: <default>. Megfelelő, vagy mást szeretnél?"*
- **Teszt-riportolás (TR3 — KÖTELEZŐ kérdés, a teszt stack után):** *„Milyen riportot generál a teszt-eszközötök, és milyen paranccsal? (pl. Allure HTML, Playwright HTML report, pytest-html, JUnit XML, coverage) — ez minden ciklusban bekerül a `specs/cycle-NN-<name>/test-report/` mappába — körönkénti almappákba —, és a validálás determinisztikus kapuval ellenőrzi a meglétét."* A választ a `## Teszt-riportolás` szekció **táblázatába** vezesd (kategória / eszköz / parancs / artefaktum). **Ezt a szekciót nem hagyhatod pre-fillelt default-tal** — vagy valós parancsok kerülnek bele, vagy a felhasználó explicit kimondja, hogy nincs riport-generálás, és akkor a `**Riport-generálás kötelező:**` mező `nem` + indoklás. Ha az eszköz többféle formátumot tud, **egyfájlos HTML-t javasolj** (a riport a ciklus git-diffjébe kerül).
- **Merge stratégia + visszaintegrálás (BD7/BD15):** kérdezd meg a git szolgáltatót (GitHub / Bitbucket Cloud / Bitbucket Server / GitLab / Lokális), majd **próbáld ki az access-t** a megfelelő paranccsal (lásd a Merge stratégia szekciónál). Ha az access teszt sikertelen, **ne zárd le a `conventions.md`-t** — kérd a token / URL / permissions javítását, vagy alternatív szolgáltató / lokális merge választását. Ez az **egyetlen igazságforrás** arra, hogyan kerül vissza `main`-be egy elkészült branch (PR vagy közvetlen merge) — ezt használja a 09 (ciklus-merge), a 01/00 branch-figyelmeztetés, és a 00 init-branch visszaintegrálása is. Ha nincs döntés/remote, a default a **közvetlen merge** (BQ7). _(Csak a `## Merge stratégia` szekciót töltsd — ne vezess be új mezőt.)_
- **Branch-elnevezési stratégia (BD8 — csak ha van VCS):** kérdezd meg:
  - Kell-e **Jira-jegyszámot** a branch nevének elejére? (ha igen: milyen formátumban)
  - A feature branch-ek **`feature/` prefixszel** kezdődnek-e?
  - **Vagy** mutass rá egy dokumentumra, ahol ezek tisztázva vannak (onnan vesszük át a szabályt).
  A választ a `## Git és branching konvenciók` **Branch-elnevezési stratégia** mezőjébe írd. **Default** (ha a felhasználó nem rendelkezik): `feature/cycle-NN-<name>` (a mappanév mindig prefix nélkül, tisztán `cycle-NN-<name>` — BD3). Kis branching-szabály (prefix, Jira-jegy) mehet **szó szerint** a `conventions.md`-be.
- **API-szabályzat / API design guideline (BD9):** *„Van követendő API design guideline / API-szabályzat (REST konvenciók, verziózás, hibaformátum, elnevezés)? Ha igen, hol a dokumentuma?"* A pointer a `## Projekt referenciák` szekcióba kerül, hogy a 02–03 fázis ebből dolgozhasson.
- **Nagy külső szabály-dokumentumok (BD10 — hibrid: pointer + kivonat):** ha a felhasználó **nagy** dokumentumra mutat (API-guideline, terjedelmes branching-szabályzat), azt **NE** tedd be teljes szöveggel a `conventions.md`-be (minden fázis behúzná → token-duzzadás). Helyette: **(a)** pointer a `## Projekt referenciák`-ba (forrás elérési útja/URL + egysoros leírás, mit szabályoz); **(b)** a `researcher` subagenttel (`agents/researcher.md`) **egyszer** olvastasd be, és hozass ki belőle egy tömör, normatív **szabály-checklistet** (konkrét do/don't pontok), ami a `conventions.md`-be kerül. A mély/ritka részleteket a fogyasztó fázis (branching → 01, API → 02–03) on-demand a `researcher`-rel olvassa. A pointer megőrzi a forrást, így a kivonat újragenerálható, ha a doksi változik.

Ne kezdj spec-et, plan-t vagy implementációt. Ez a lépés kizárólag a projekt konvencióit rögzíti.

---

## Kontextus betöltési szabályok

- Csak annyi információt gyűjts be a projektről, amennyi a `conventions.md` kitöltéséhez szükséges.
- Ha a projekt már létező kódot tartalmaz és egy komponens mélyebb megértése kell, hívd a `researcher` subagentet (`agents/researcher.md`, Mód B) — csak összefoglalót ad vissza, a nyers fájltartalom nem kerül be a fő kontextusba.

## Kérdezési szabályok

- Csak **egy** kérdést tegyél fel egyszerre.
- Ha a felhasználó válasza újabb kérdést nyit meg, add hozzá a listához.
- Addig iterálj, amíg minden szekció ki nem töltött.

## Megállási szabályok

- Ha a felhasználó válasza ellentmond a korábban rögzített konvencióknak, jelezd az ellentmondást és kérd pontosítását.
- Ha a felhasználó olyan technológiát választ, amelyről nincs információd, jelezd és kérd, hogy adjon referenciát vagy dokumentációt.

---

## conventions.md struktúra

```md
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
- **Egyszerűsített flow (`prompts/skills/sdd-lightweight-flow.md`):** kis, jól körülhatárolt feladatokhoz (konfiguráció, egyszerűbb script, kisebb javítás) — háromfázisú `spec.md` → `task.md` → implementáció.

**Alapértelmezett flow:** _<teljes | egyszerűsített>_ — _(a projekt jellege alapján kitöltve a 00 fázisban; pl. túlnyomóan konfiguráció/scriptelés/üzemeltetés → egyszerűsített; termékfejlesztés több komponenssel → teljes)_

A default csak a **kiindulópont**, feladatonként felülbírálható. Ha egy adott feladat nem illik a default flow-ba, az ágens jelzi és a másikat javasolja (lásd a `01-add-cycles` és `03-write-plan` flow-méret ellenőrzését, illetve a `sdd-lightweight-flow` túlnövés-jelzését). A flow-váltás döntése mindig a felhasználóé.

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

_**Hova kerülnek (TR5):** a riportok nem közvetlenül a `test-report/` gyökerébe, hanem **körönkénti almappákba** mennek — `test-report/validate/round-01/`, `round-02/`, … a validálási körökhöz, `test-report/review/round-NN/` a 09-review re-validate köreihez. Így egy önjavító hurok minden körének megmarad a saját bizonyítéka, és a `validate-decision.md` lépés-táblájában jelzett bukáshoz megnyitható a hozzá tartozó riport. **A táblázat utolsó oszlopa a KÖR-MAPPÁHOZ képest relatív útvonal** (fájl vagy mappa) — a kör-mappát a hívó fázis adja át a `test-runner`-nek és a kapunak (`--report-subdir`)._

**Riport-generálás kötelező:** igen

| Teszt-kategória | Eszköz | Riport-generáló parancs | Artefaktum a kör-mappában |
|---|---|---|---|
| E2E | Playwright (+ Allure) | `npx playwright test --reporter=html && npx allure generate ./allure-results --single-file -o ./allure-report` | `allure-report.html` |
| Unit / integrációs | _a választott futtató_ | `<riport-generáló parancs>` | `unit-report.html` |
| Lefedettség | _pl. c8 / coverage.py_ | `<parancs>` | `coverage/` |

_Kitöltési szabályok:_
- **Egyfájlos HTML-t preferálj** (`allure generate --single-file`, `--reporter=html` egy fájlba), mert a riport a ciklus git-diffjébe kerül. Ha az eszköz csak mappát tud (pl. teljes Allure static site), az is elfogadható — akkor a mappa neve `/`-re végződjön (`allure-report/`).
- Ha egy kategóriához nincs riport-artefaktum, az utolsó oszlopba `-` kerül (a kapu kihagyja azt a sort).
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
- **Quality Gate elvárás:** PASSED — a `07-validate` fázisban blokkol, amíg nem teljesül
- **Sonar riport helye:** a validálási kör mappája — `specs/cycle-NN-<cycle-name>/test-report/validate/round-NN/sonar-report.md` (+ `.html`); automatikusan generálódik a validálás során, körönként külön (TR5)

## Kockázatok és ismert korlátok

_Projekt szintű technikai korlátok, elfogadott POC határok._
```

---

## Folytatás megszakított futás után

Ha a 00 fázis félbeszakadt és új sessionban folytatódik:

```
1. Létezik már conventions.md?
   → Olvasd be, és nézd meg, mely szekciók kitöltöttek.
   → Folytasd az első hiányos/üres szekciótól — ne kezdd elölről.

2. A conventions.md létezik, de hiányos (üres szekciók, kitöltetlen Merge
   stratégia, lefuttatlan access validáció)?
   → A conventions.md NEM tekinthető késznek, amíg minden szekció kitöltött
     ÉS a merge access validáció sikeres. Folytasd a hiányzó részekkel.

3. Nincs conventions.md?
   → Kezdd a "Feladatod" szerint.
```

---

## Lezárás

> **A `conventions.md` „kész" jelölése a puszta léte** — nincs külön státuszmező. Ezért a fájl csak akkor jöhet létre véglegesen (commitba kerülve), ha minden szekció kitöltött és a minőségellenőrzés átment. A 01–08 fázisok ezután csak létezés-ellenőrzést végeznek.

### Minőségellenőrzés — lezárás előtt

Mielőtt lezárod, ellenőrizd:
1. Minden szekció kitöltött (nincs üresen hagyott pre-fill placeholder)?
2. A Teszt keretrendszer a fejlesztővel egyeztetett (nem csak a default maradt megerősítés nélkül)?
2.a **A `## Teszt-riportolás` szekció valós adatokkal kitöltött (TR3)?** — a táblázatban tényleges riport-generáló parancsok és artefaktum-nevek állnak, **vagy** a `**Riport-generálás kötelező:**` mező `nem` + indoklás. Sablon-placeholder (`<parancs>`, `<a választott futtató>`) nem maradhat benne: a `07-validate` kapuja ezt a táblát olvassa, és placeholder mellett minden ciklus bukna.
3. A Merge stratégia kitöltött, és az access validáció **sikeresen lefutott** (vagy a fejlesztő explicit lokális merge-et választott)?
4. A portok, env változók és Sonar (ha van) szekciók a projekt valóságát tükrözik?
5. A `## Fejlesztési módszertan` **Alapértelmezett flow** mezője a fejlesztővel egyeztetett értékre van állítva (`teljes` vagy `egyszerűsített`), nem maradt placeholder?
6. **A `## Git és branching konvenciók` VCS-flagje beállítva (BD11):** vagy git, vagy explicit „NINCS verziókezelő …"?
7. **VCS mellett: a Branch-elnevezési stratégia mező kitöltött (BD8)** (default `feature/cycle-NN-<name>`, vagy a szervezeti szabály/pointer)?
8. **Ha a felhasználó API design guideline-t / nagy szabályzatot jelölt (BD9/BD10):** a `## Projekt referenciák`-ban ott a pointer, és nagy doksinál a `researcher`-rel készített tömör szabály-checklist?

Ha bármelyikre nem, egészítsd ki, mielőtt lezárod.

### Commit, visszaintegrálás és jelzés

Ha a minőségellenőrzés átment:

1. **Commit (csak VCS esetén) — a `feature/init-project` branch-en** (BD12):
   ```bash
   git add conventions.md && git commit -m "cycle-NN: 00-init"
   ```
   _(A 00 fázis nem ciklusspecifikus; a `cycle-NN:` prefix az első ciklusra utal — pl. `cycle-01: 00-init`.)_
2. **Visszaintegrálás `main`-be (csak VCS esetén) — a `## Merge stratégia` szerint (BD7/BD12):** a szekcióban rögzített szolgáltató alapján **PR feladás** vagy **közvetlen merge** `main`-be; ha nincs explicit döntés/remote, a default a **közvetlen merge** (BQ7). Destruktív lépés (merge/branch-törlés) előtt kérj felhasználói megerősítést.
3. **No-VCS ág (BD11):** ha a `conventions.md` szerint nincs verziókezelő, az 1–2. lépés kimarad — a `conventions.md` fájl puszta léte a „kész" jelölés, branch/commit/merge nélkül.
4. Jelezd a felhasználónak:

   *"A projekt konvenciók rögzítve. A következő fázis indítása előtt mindenképpen futtass egy `/clear` parancsot a kontextus kiürítéséhez, majd megkezdhető a ciklusok kezelése: `prompts/skills/01-add-cycles.md`."*