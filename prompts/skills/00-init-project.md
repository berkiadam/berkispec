---
phase: 00
name: init-project
prerequisites: []
output:
  - "conventions.md (projekt gyökér)"
prev: null
next: 01-add-cycles
subagents: []
---

# 00 — Projekt inicializálás

Ez a prompt egyszer fut le, új projekt indulásakor. Célja a projekt konvencióinak rögzítése, amelyekre az összes fejlesztési ciklus (02–08) hivatkozni fog.

---

## Feladatod

Hozz létre egy `conventions.md` fájlt a projekt gyökerében az alábbi struktúra szerint. Minden szekciót a felhasználóval közösen töltötök ki — tegyél fel kérdéseket, ahol a döntés nem egyértelmű. A struktúrában szereplő technológiák (pl. Playwright, pytest) és beállítások **ajánlott default-ok**; ezeket a projekt tényleges tech stackje alapján testre kell szabni (pl. Node/Jest, Go/go test stb.).

Két szekciónál **aktívan rá kell kérdezned** (nem elég csak pre-fillelni):
- **Teszt keretrendszer:** *„A javasolt teszt stack: <default>. Megfelelő, vagy mást szeretnél?"*
- **Merge stratégia:** kérdezd meg a git szolgáltatót (GitHub / Bitbucket Cloud / Bitbucket Server / GitLab / Lokális), majd **próbáld ki az access-t** a megfelelő paranccsal (lásd a Merge stratégia szekciónál). Ha az access teszt sikertelen, **ne zárd le a `conventions.md`-t** — kérd a token / URL / permissions javítását, vagy alternatív szolgáltató / lokális merge választását.

Ne kezdj spec-et, plan-t vagy implementációt. Ez a lépés kizárólag a projekt konvencióit rögzíti.

---

## Kontextus betöltési szabályok

- Csak annyi információt gyűjts be a projektről, amennyi a `conventions.md` kitöltéséhez szükséges.
- Ha a projekt már létező kódot tartalmaz és egy komponens mélyebb megértése kell, indíts subagent-et a kutatáshoz.

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

A fejlesztés során az alábbi globális tervezési és API specifikációs dokumentumok az irányadóak. Az ágens köteles ezeket figyelembe venni a ciklusok tervezésekor:

- **HLD (High Level Design):** _(pl. docs/design/hld.md vagy hagyd üresen)_
- **LLD (Low Level Design):** _(pl. docs/design/lld.md vagy hagyd üresen)_
- **API Specifikáció:** _(pl. docs/api/openapi.yaml vagy hagyd üresen)_
- **Adatbázis Séma:** _(pl. docs/db/schema.sql vagy hagyd üresen)_

## Projekt struktúra

_A gyökér szintű mappák és szerepük. Például:_

- `src/` — fő alkalmazás forráskód
- `apps/` — önálló alkomponensek
- `test/` — tesztek (lásd részletesen lentebb)
- `docs/` — dokumentáció, OpenAPI leírók
- `specs/` — fejlesztési ciklus specifikációk

## Fejlesztési módszertan

Spec-driven development. A fejlesztés ciklusokra van bontva. A workflow két egyszeri setup lépésből és egy 5 lépéses per-ciklus loop-ból áll:

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
- `08` — review & merge (review + merge a conventions.md Merge stratégiája szerint)

Minden ciklus mappája: `specs/cycle-NN-<cycle-name>/`

## Git és branching konvenciók

- **Fő branch:** `master`
- **Cycle branch:** `feature/cycle-<cycle-name>` — minden fejlesztési ciklus saját branch-en él
- **Branch nyitás:** a spec fázis (02) legelején, a branch tartalmazza a `specs/`, `docs/` és `src/` változásokat egyaránt
- **Merge:** a `## Merge stratégia` szekció szerint, a review & merge fázis (08) sikeres lefutása után
- **Commit granularitás:** taskonként egy commit

## Merge stratégia

_A ciklus lezárásakor (08 fázis) ezt használja az ágens. A 00 fázisban tisztázandó, és az access-t **ki kell próbálni** — a `conventions.md` nem zárható le, amíg a választott szolgáltatóhoz sikeresen hozzá nem férünk (vagy a felhasználó alternatívát/lokális merge-et választ)._

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
- **Sonar riport helye:** `specs/cycle-NN-<cycle-name>/test-report/sonar-report.md` (automatikusan generálódik a validálás során)

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
3. A Merge stratégia kitöltött, és az access validáció **sikeresen lefutott** (vagy a fejlesztő explicit lokális merge-et választott)?
4. A portok, env változók és Sonar (ha van) szekciók a projekt valóságát tükrözik?

Ha bármelyikre nem, egészítsd ki, mielőtt lezárod.

### Commit és jelzés

Ha a minőségellenőrzés átment:
1. Készíts git commitot a fázis lezárásáról:
   ```bash
   git add conventions.md && git commit -m "cycle-NN: 00-init"
   ```
   _(A 00 fázis nem ciklusspecifikus; a `cycle-NN:` prefix az első ciklusra utal — pl. `cycle-01: 00-init`.)_
2. Jelezd a felhasználónak:

   *"A projekt konvenciók rögzítve. Megkezdhető a ciklusok kezelése: `prompts/skills/01-add-cycles.md`."*
