<!--
  A `08-doc-sync` PROJEKT-NYELVI blokkjai (9.4 kiemelés).
  Ezt a fájlt a telepítő build-time emeli be az INCLUDE markerek helyére, a
  választott PROJEKT-nyelv (`PROJECT_LANG`) szerint; a marker alakja
  `lang/08-doc-sync.md#<horgony>`.
  A blokkok SZÓ SZERINT kerültek ide — ne fogalmazd át, ne egységesítsd.
  Az ANCHOR sorok NEM részei a beemelt szövegnek, csak határolók (8.9).
  FIGYELEM: ebbe a vezető jegyzetbe ne kerüljön komment-lezáró szekvencia.
-->

<!-- ANCHOR:TC12-promocio-kerdes -->
- [ ] K03 — Melyik ciklus-tesztet emeljem be projekt szintre a `test-conventions.md`-be?

| # | Viselkedés (így kerülne be) | Szekció | Recept | Javaslat | Indok |
|---|---|---|---|---|---|
| 1 | A mock `/start-process` 201-et ad érvényes `processName`-re, és 400-at hiányzó body-ra | 2 | R02 | promótálandó | a mock szerződése minden ciklusban él |
| 2 | A `/verify` 403-at ad `TMP_031` errorCode-dal lejárt tokenre | 3 | **új recept kell** (indítás + példa hívás hiányzik) | promótálandó | minden auth-változás érinti |
| 3 | A cycle-24-es migrációs script egyszeri lefutása | 2 | R01 | marad ciklus-lokális | egyszeri adatmigráció, nem ismételhető |

_Nem futott le ebben a ciklusban (ezért nem jelölt): `<teszt>` — `<miért>`._

**Válaszként elég a sorszámok felsorolása** (pl. „1, 2" vagy „mindet" / „egyiket sem"). A kihagyottakat a döntés-naplóba írom, hogy a következő ciklusban ne kérdezzek rá újra.

<!-- ANCHOR:TC12-dontes-naplo-sablon -->
## Nem promótált jelöltek (döntés-napló)

- A cycle-24-es migrációs script egyszeri lefutása — döntés: `nem promótálandó` (egyszeri adatmigráció) · cycle-24

<!-- ANCHOR:TC10-tetel-blokk-sablon -->
### L01 — A mock `/start-process` 201-et ad érvényes kérésre

- **Cél:** a FlowX mock szerződése stabil marad — a kliens a dokumentált válaszra épülhet.
- **Előfeltétel:** `R02` fut (a felhúzás ott van leírva) · a `0.` blokk `lokális` sora szerinti port.
- **Lépések:**
  1. `POST /start-process` a `{"processName": "onboarding"}` payloaddal.
  2. Ugyanez üres body-val.
- **Elvárt eredmény:** az 1. lépésre `201` + `{"processInstanceId": "<uuid>"}`; a 2. lépésre `400` + `MISSING_BODY` errorCode.

<!-- ANCHOR:doc-sync-questions-struktura -->
# Cycle NN: <cím> — Doc-sync kérdések

- [ ] K01 — [kérdés szövege]
- [x] K02 — [kérdés szövege] → [döntés / válasz röviden]
- [ ] K03 — [kérdés szövege] _(K02-ből merült fel)_

<!-- ANCHOR:DS10-doc-sync-plan-vaz -->
- [ ] <fájl> — <művelet: reconciliation | új | nincs teendő> — <mit pontosan> (scope: <flow/komponens>)
  <reconciliation/új esetén a subagent Csereszöveg-blokkja: lecserélendő jelenlegi részlet → megírt új szöveg>

<!-- ANCHOR:DS17-fejlec-blokk -->
> **Lefedve:** cycle-16-ig · **Utolsó frissítés:** cycle-16 (2026-06-04) · **Generátor/scope:** as-built működésleírás — a rendszer összes felhasználói/üzleti flow-ja és állapota; forrás: src/ + lezárt spec.md-k (DS19).

<!-- ANCHOR:DS15-changelog-vaz -->
## cycle-NN — <cím> (YYYY-MM-DD)

**Mi változott a működésben:** <viselkedés-szintű változás, flow-nként>
**Mi változott a doksikban:** <mely docs-generated/ fájlok + mi>
**Átnevezések (ha van):** <régi → új azonosító>

<!-- ANCHOR:DS-system-overview-vaz -->
> **Lefedve:** cycle-NN-ig · **Utolsó frissítés:** ... · **Generátor/scope:** ...

# <Rendszer neve> — Működési áttekintés

> Részletes változásnapló: [CHANGELOG.md](./CHANGELOG.md). Eltérések a tervtől: [design-drift.md](./design-drift.md).

## Mit csinál a rendszer (összefoglaló)
_<1-2 bekezdés: a rendszer feladata, fő képességei.>_

## Képességek és flow-k
_<Képesség szerint strukturálva (NEM ciklusonként). Minden flow-hoz: rövid leírás + konszolidált mermaid (sequenceDiagram / graph), az elavult lecserélve.>_

## Állapotmodell
_<Session, cache/store mapping, token-életciklus.>_

## Endpoint-leltár _(feltételes — csak ha a rendszernek van hálózati interfésze; DS2/DS22 Réteg 2)_
_<Endpoint → rövid leírás. Ha nincs hálózati interfész, ez a szekció elmarad.>_

<!-- ANCHOR:DS20-design-drift-vaz -->
- **<azonosító>** — Terv: <mit ír a HLD/LLD>. As-built: <mi a megvalósult>. Indok/státusz: <miért; nyitott vagy lezárt>.

<!-- ANCHOR:TC2-test-conventions-vaz -->
> **Utolsó felülvizsgálat:** cycle-NN · **Gazda:** 08-doc-sync · **Nem futtatható forrás** — a receptet a 02/03 fázis emeli be a ciklus spec.md/plan.md-jébe (TC1/a).

# Teszt konvenciók — visszatérő elvárások és receptek

## 0. Koordináták

_Minden környezet-, hozzáférés- és paraméter-adat **egy helyen** (TC13). Az 1. szekció receptjei ezekre hivatkoznak, nem ismétlik meg őket._

### Környezetek és végpontok

| Környezet | Komponens | URL / port | Health endpoint |
|---|---|---|---|
| lokális | <komponens> | `http://localhost:PORT` | `/health` |
| remote | <komponens> | `https://<host>` | `/health/ready` |
| remote | keycloak (port-forward → keycloak.apps.ocp.example) | `http://127.0.0.1:8080` | `/health/ready` |

_**🔴 Ha egy cím lokálisnak LÁTSZIK, de távolra visz** (`kubectl`/`oc port-forward`, SSH-alagút), azt **külön sorban, `remote` környezettel** kell felvenni, a valódi célt is megnevezve — ez az EGYETLEN hely, ahol ez látszik: a `127.0.0.1:8080` a naplóban semmit nem árul el arról, hogy a másik végén egy osztott klaszter van. **A sor alakja kötött, mert a `07` `RL1` kapuja gépileg olvassa:** a `Környezet` cella `remote`, az `URL / port` cella a **lokálisnak látszó cím**, a `Komponens` cella pedig tartalmazza a `port-forward` szót és a valódi célt (a fenti harmadik sor a minta). Az `RL1` ebből annyit használ, hogy a `remote` környezetű sorok `URL / port` cellájából kigyűjti a lokálisnak látszó címeket — ezek a **felmentett** címek: ha egy `rest-logs/remote/<teszt>/` mappa naplói CSAK ilyen címekre mennek, az nem bukás._

### Teszt-userek, kliensek, titkok

| Környezet | Név / azonosító | Titok | Scope / szerep |
|---|---|---|---|
| lokális | `<user>` | `<dev-only jelszó>` | `<realm / szerep>` |
| remote | `<client-id>` | pointer: `.env.remote` → `<VÁLTOZÓ>` | `<scope>` |

### Paraméterek és env-fájlok

| Név | Érték / pointer | Hol használjuk |
|---|---|---|
| `<PARAMÉTER>` | `<érték vagy pointer>` | `<recept vagy komponens>` |

## 1. Recept-regiszter

### R01 — <komponens / lépés neve>
- **Hol van:** <repo-útvonal, image-név, registry-cél, namespace/pod>
- **Elérés:** <URL-ek, portok, health endpoint>
- **Teszt-userek / paraméterek:** <user + jelszó (csak dev-hatókörű, TC5!), scope, client-id>
- **Indítás:** _(kötelező — TC11)_
  ```bash
  <a környezet felhúzása: docker compose up / podman run / npm run dev / oc port-forward …>
  <health-ellenőrzés: curl -s http://localhost:PORT/health → mit vársz vissza>
  ```
- **Parancsok:**
  ```bash
  <a teszt futtatása / build / push / restart — csak verifikált, tényleg lefutott parancs (TC3)>
  ```
- **Példa hívás:** _(kötelező, ha a recept HTTP/gRPC/CLI végpontot érint — TC11)_
  ```bash
  curl -s -X POST "<teljes URL>" \
    -H 'Content-Type: application/json' -H 'Authorization: Bearer <hogyan szerzem meg>' \
    -d '{"<mező>": "<érték>"}'
  # Várt válasz: 200, body: {"<mező>": "<érték>"}
  ```
- **Leállítás / takarítás:** <hogyan állítom le a felhúzott környezetet, mit kell törölni>
- **Előfeltétel / sorrend:** <mi kell hozzá — másik receptre `R-ID`-vel hivatkozva, mi jön előtte/utána>
- **Hatókör:** `lokális` | `osztott-remote` — <ha osztott, a beemelésnél a 03 kötelezően rákérdez>
- **Leltár-tételek:** <a receptre hivatkozó `TL-NNN` tételek a teszt-leltárból, vagy `—` — a hivatkozás KÉTIRÁNYÚ (LD6), a kapu mindkét irányt méri>
- **Utolsó futás:** cycle-NN

## 2. Minden körben szükséges lokális (mock alapú) tesztek

**Kötelező riport (TR3):** `<artefaktum a validálási kör mappájában>` — forrás: `conventions.md → ## Teszt-riportolás`

| ID | Mit ellenőriz | Recept | Utolsó futás |
|---|---|---|---|
| L01 | <önhordó viselkedés-leírás: milyen bemenetre mi a helyes kimenet — TC10> | R01 | cycle-NN |

### L01 — <a tétel önhordó címe>

- **Cél:** <mit bizonyít ez a teszt — 1 mondat>
- **Előfeltétel:** <`R-ID` fut · a 0. blokk melyik adatai kellenek>
- **Lépések:**
  1. <konkrét lépés — hívás/parancs/interakció>
  2. <...>
- **Elvárt eredmény:** <státuszkód, mező, érték — amit igen/nem el lehet dönteni>

## 3. Minden körben szükséges integrációs / E2E tesztek

**Kötelező riport (TR3):** `<artefaktum a validálási kör mappájában>` — forrás: `conventions.md → ## Teszt-riportolás`

| ID | Mit ellenőriz | Recept | Előfeltétel | Utolsó futás |
|---|---|---|---|---|
| I01 | <önhordó viselkedés-leírás — TC10> | R01, R02 | <`R05` fut (a felhúzás ott van leírva) — TC11> | cycle-NN |

### I01 — <a tétel önhordó címe>

- **Cél:** <mit bizonyít ez a teszt — 1 mondat>
- **Előfeltétel:** <`R05` fut · a 0. blokk melyik adatai kellenek>
- **Lépések:**
  1. <konkrét lépés — hívás/parancs/interakció>
  2. <...>
- **Elvárt eredmény:** <státuszkód, mező, érték — amit igen/nem el lehet dönteni>

## Nem promótált jelöltek (döntés-napló)

_(Opcionális appendix, TC12 — nem számozott szekció. Ide kerül, amit a felhasználó nem kért projekt szintre; a következő ciklus ezeket már nem kínálja fel újra.)_

- <önhordó viselkedés-leírás> — döntés: `nem promótálandó` (<indok>) · cycle-NN

<!-- ANCHOR:LD1-test-description-vaz -->
> **Lefedve:** cycle-NN-ig · **Utolsó frissítés:** cycle-NN (YYYY-MM-DD) · **Generátor/scope:** a projekt teljes tesztkészlete — minden tesztfájl, amit a `conventions.md` `## Teszt-futtatás` szekciója glob-bal deklarál; forrás: a ciklusok `test-report/` bizonyítékai + a `plan.md` teszt-forgatókönyvei.

# Teszt-leltár

_Ez a fájl arra a kérdésre válaszol, hogy **milyen tesztek léteznek a projektben, és mit bizonyítanak** — egy helyen, végigolvashatóan, egy friss kontextusú ágensnek és egy új kollégának egyaránt. A gazdája a `08-doc-sync`: más fázis és más parancs nem írja._

_**Amit ez a fájl NEM:** nem futtatható forrás és nem recept-regiszter. Az indítást, a példa hívást, az előfeltételt és a takarítást a `specs/test-conventions.md` hordozza (mező-szintű tulajdon: azonos mezőt a kettő nem duplikál), a ciklus-szintű futtatást pedig a `plan.md` gépi futtatási táblája. Innen a **cél / lépések / elvárt eredmény** az igazság._

_A tételek **kategóriánként** csoportosulnak (a `conventions.md` kategória-szótára szerint), a `TL-NNN` sorszám viszont **projekt-szintű és globális**: soha nem újrahasznosított, és a kategória-váltás sem írja át._

## <kategória — a `conventions.md` `Teszt-kategóriák` szótárából>

<!-- ANCHOR:LD2-tl-adatlap-vaz -->
### TL-NNN — <a tétel önhordó címe: milyen bemenetre mi a helyes kimenet>

- **Környezet:** local | remote
- **Cél:** <egy állítás-mondat: mit bizonyít ez a teszt, és melyik képességről>
- **Lépések:**
  1. <konkrét parancs / hívás — szó szerint kiadhatóan, nem viselkedés-szintű összefoglaló>
  2. <...>
- **Elvárt eredmény:** <eldönthető érték backtickben: státuszkód, mezőnév, darabszám>
- **Futtató parancs:** `<a szelektoros futtatás EGY sorban — csak ezt az egy tesztet futtatja>`
- **Recept:** <`R-NN` hivatkozás a `specs/test-conventions.md`-be, vagy `—`, ha nincs>
- **Utolsó futás:** <YYYY-MM-DD> (local | remote)
- **Forrás-ciklus:** cycle-NN

<!-- ANCHOR:LD2-tl-adatlap-pelda -->
### TL-014 — A token-init végpont ugyanarra a payloadra ugyanazt a hash-t adja, ismételt initre 409-et

- **Környezet:** remote
- **Cél:** bizonyítja, hogy az init-hash idempotens, és a duplikált init nem hoz létre második session-t.
- **Lépések:**
  1. `curl -s -X POST "https://tmp-dev.example.local/init-hash" -H 'Content-Type: application/json' -d '{"clientRef":"dsp01"}'`
  2. Ugyanaz a hívás, változatlan payloaddal, 1 másodpercen belül.
  3. `curl -s "https://tmp-dev.example.local/sessions?clientRef=dsp01"`
- **Elvárt eredmény:** az 1. lépésre `200` + `{"initHash":"<64 hex>"}`; a 2. lépésre `409` + `TMP_031` errorCode; a 3. lépésre pontosan `1` session.
- **Futtató parancs:** `npx playwright test test/e2e/init-hash.spec.ts --grep "idempotent init"`
- **Recept:** R03
- **Utolsó futás:** 2026-09-04 (remote)
- **Forrás-ciklus:** cycle-16

<!-- ANCHOR:LD3-retired-jeloles -->
### TL-007 — A régi /init-cache végpont 200-at ad érvényes payloadra — **Kivezetve**

- **Kivezetve:** a végpont a cycle-16-ban `/init-hash`-re neveződött át, a régi útvonal megszűnt. A tétel utódja: `TL-014`.
- **Forrás-ciklus:** cycle-11

<!-- ANCHOR:LD4-leltar-kerdes -->
- [ ] K04 — A teszt-leltár melyik hiányzó adatát töltsem ki?

| # | Tétel | Mi hiányzik / mi bizonytalan | Miért nem írom be magamtól |
|---|---|---|---|
| 1 | TL-018 (`test/e2e/payment.spec.ts`) | mit bizonyít a teszt (cél) és mi az elvárt eredmény | a tesztfájl neve nem mondja meg, és ebben a ciklusban nem futott — találgatni tilos |
| 2 | TL-009 | a parancs a `old-app.stale.example` hostra hív, amit a `conventions.md` már nem deklarál | vagy a tétel elavult, vagy a `conventions.md` környezet-deklarációja — ezt nem dönthetem el |

**Válaszként elég a hiányzó adat megadása tételenként** (vagy „töröld"/„jelöld kivezetettnek", ha a teszt már nem él).

<!-- ANCHOR:DS21-readme-index-vaz -->
- `<fájlnév>` — <egysoros leírás: mi ez, ki/mikor írja>

<!-- ANCHOR:zaro-uzenet -->
   > *"A dokumentáció szinkronban van a megvalósult rendszerrel, a konzisztencia-kapu zöld. Folytathatjuk a 9. lépéssel: review & merge (09). Hogy melyik paranccsal, azt a `conventions.md` `## Review and merge` szekciójának `PR submission` mezője dönti el. Az új fázis megkezdése előtt mindenképpen futtass egy `/clear` parancsot a kontextus kiürítéséhez, majd:*
   > ```
   > /bs-review-and-merge input: @specs/cycle-NN-<cycle-name>   # PR submission: no
   > /bs-create-pr        input: @specs/cycle-NN-<cycle-name>   # PR submission: yes
   > ```"*
