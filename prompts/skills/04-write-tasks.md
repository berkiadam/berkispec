---
phase: 04
name: bs-write-tasks
description: "berkispec - 04. Használd, ha a plan.md 'Task írásra kész' (Phase 04), a technikai terv jól strukturált, egyenként végrehajtható és mérhető feladatokra (DoD) bontásához. Létrehozza a 'tasks.md'-t ('Implementálásra kész') + szükség esetén a 'tasks-questions.md'-t."
prerequisites:
  - "specs/cycle-NN-<name>/plan.md státusz: Task írásra kész"
output:
  - "specs/cycle-NN-<name>/tasks.md státusz: Implementálásra kész"
  - "specs/cycle-NN-<name>/tasks-questions.md (ha merül fel kérdés)"
  - "specs/cycle-NN-<name>/validate-input-from-prev.md (csak ha van átadandó infó, IP1)"
prev: bs-write-plan
next: bs-analyze
subagents: []
scripts:
  - "scripts/analyze-gate-check.py"
shared:
  - "shared/input-from-prev.md"
  - "shared/artifact-voice.md"
  - "shared/phase-commit.md"
  - "shared/quality-check-tasks.md"
  - "shared/questions-tasks.md"
  - "shared/fix-mode-tasks.md"
---
# 04 — Tasks írás
<!-- INCLUDE:shared/context-check.md -->

---

Spec driven development-ben fejlesztünk szoftvert. A fejlesztés ciklusokra van bontva. Minden ciklus egy önállóan lefejleszthető, önállóan tesztelhető részegysége a teljes implementációnak.

Ez a folyamat **4. fázisa (0–9)**: 0-init · 1-ciklusok · 2-spec · 3-plan · **4-tasks ←** · 5-analyze · 6-implement · 7-validate · 8-doc-sync · 9-review.

---

## Előfeltétel

0. **Ciklus-beazonosítás:** ha a felhasználó megadott ciklust/fájlt, azt használd; különben a legfrissebb `specs/cycle-*` mappát ajánld fel megerősítésre — *"A(z) `specs/cycle-NN-<name>` ciklussal szeretnél dolgozni? Igen / Nem (megadom a ciklust)"* — és várj a válaszra, mielőtt továbblépsz.

1. **`conventions.md` létezés-ellenőrzés:** olvasd be a projekt gyökerében a `conventions.md`-t. Ha nem létezik, STOP — térjenek vissza a `00` fázishoz. _(A fázis a ciklus feature branch-én fut; a záró commit oda kerül — No-VCS projektben a commit kimarad.)_
2. Olvasd be a `plan.md` státuszát. **Ha a státusz nem `Task írásra kész`, ne kezdj tasks listát írni.** Jelezd a felhasználónak, hogy a plan még nem zárult le, és térjenek vissza a `03` plan fázishoz.
3. **Nyitott kérdések lezártsága:** a `Task írásra kész` státusz implikálja, de explicit ellenőrizd — a `spec-questions.md` és `plan-questions.md` egyikében sincs `[ ]` nyitott kérdés. Ha van, a plan nem zárult le valójában: jelezd, és térjenek vissza a `03` (vagy `02`) fázishoz.

---

## Folytatás megszakított futás után

Ha a tasks.md írása félbeszakadt és új sessionban folytatódik:

1. Olvasd be a `tasks.md` aktuális állapotát.
2. Keresd meg az első hiányos vagy bizonytalan részt: van-e csoport záró `[CHECK]` nélkül, van-e `[RED]` task párja nélkül, van-e a plan-ből lefedetlen módosítás?
3. Ha a tasks lista részben megvan és csak befejezés hiányzik, folytasd onnan ahol abbahagyták — ne kezdd újra.
4. Ha a lista koherensnek tűnik de a státusz még `Piszkozat`, futtasd le a minőségellenőrzést, és zárj le ha átment.

---

## Feladatod

**Ha már létezik `tasks.md` a `specs/cycle-NN-<cycle-name>/` mappában:** olvasd be, és futtasd le rajta a minőségellenőrzést (ld. lent). Ha hiányosságot találsz — hiányzó task, túl nagy task, hiányzó `[CHECK]`, plan-lefedettségi rés — javítsd, és csak ezután zárd le.

**Ha még nem létezik `tasks.md`:** hozd létre a `specs/cycle-NN-<cycle-name>/` mappában az alábbi struktúra szerint.

**Ne implementálj semmit.** A tasks lista az implement fázis bemenete — most csak a lépéseket definiáljuk.

**Ne vegyél fel taskot, amely nincs a plan `Tervezett módosítások` szekciójában.** A tasks lista a plan pontos lebontása — nem bővíti, nem szűkíti a scope-ot.

**Ha egy taskot nem lehet konkrétan leírni** (nincs egyértelmű érintett fájl, nincs egyértelmű elvégzési kritérium), az a plan hiányosságát jelzi. Állj meg, jelezd pontosan mi az alulspecifikált lépés, és kérd a felhasználót, hogy egészítse ki a `plan.md`-t. Egyben állítsd a `plan.md` státuszát vissza `Piszkozat`-ra — a plan nem maradhat `Task írásra kész` státuszban, ha hiányosságot találtál. A plan frissítése és `Task írásra kész` státusz visszaállítása után folytatható a tasks lista.

---

## Kontextus betöltési szabályok

- Csak a `plan.md`-t olvasd be. A spec és a forrásfájlok a plan fázisban már fel lettek dolgozva — ne olvasd be újra.
- Ha egy task leírásához konkrét fájlnévre vagy path-ra van szükség és az nem szerepel a plan-ben, csak akkor olvasd be az érintett fájlt.
- **`tasks-input-from-prev.md`** (ha létezik) — a korábbi fázisok által neked átadott tételek. Lásd a „Fázisok közötti átadás" szekciót.

---

## Fázisok közötti átadás (`*-input-from-prev.md`) — IP1

**Amit BEOLVASSZ:** ha létezik a `specs/cycle-NN-<cycle-name>/tasks-input-from-prev.md`, olvasd be. Ez a 02/03 fázisban felszínre került előkészítő lépéseket és sorrend-megkötéseket tartalmazza (pl. „a kulcsgenerálásnak meg kell előznie a konténer-buildet"). Minden `[ ]` tételt vagy építs be a `tasks.md`-be **taskként vagy sorrend-megkötésként**, vagy vess el explicit indokkal, és pipáld ki. **Guard:** ha a fájl nem létezik, ez nem hiba — folytasd.

**Amibe ÍRHATSZ:**
- **`validate-input-from-prev.md`** — a **07**-nek: futtatási előfeltétel vagy üzemeltetési tudnivaló, ami a task-bontás során derült ki, de csak a validálásnál lesz releváns (pl. „a TREG-04 teszt csak a seed task után futtatható", „a port ütközik a fejlesztői stackkel, ezért a validate előtt le kell állítani").

<!-- INCLUDE:shared/input-from-prev.md -->

---

## Prerequisite dokumentumok meghatározása

A tasks.md fejlécébe kerülő Prerequisite lista az implementáló agent teljes kontextusa — ezeket olvassa be a végrehajtás előtt.

Mindig benne van:
- `specs/<cycle-name>/plan.md`

Benne van, ha a plan `Schema Artifaktumok` táblájában szerepel `Reviewed` státusszal:
- OpenAPI YAML, Redis key map, DB schema, Avro séma, stb.

Soha nem kerül bele:
- `research.md` vagy más exploratív fázismelléktermék
- `Review Required` státuszú artifact (ha ilyen van, a plan nincs lezárva)

---

<!-- INCLUDE:shared/artifact-voice.md -->

---

## Task formátum

```md
- [ ] T001 [RED]   <tesztfájl létrehozása / teszt megírása> — `path/to/test.ts` — plan [P-CONFIG]
- [ ] T002 [GREEN] <implementáció> — `path/to/file.ts` — plan [P-CONFIG] (betöltő modul)
- [ ] T003 [OPS]   <nem TDD lépés: build / push / deploy / kézi konfiguráció> — parancs vagy `path/to/file` — plan [P-DEPLOY]
- [ ] T004 [CHECK] Futtasd a teszteket / typecheck-et — plan [P-CONFIG]
```

### 🔴 Plan-hivatkozás minden taskon (PID1) — kötelező

| Szabály | Mechanika |
|---|---|
| **Kötelező** | Minden task sora végén: `— plan [P-…]`. Hivatkozás nélküli task nincs. |
| **Az ID a kulcs, nem a sorszám** | `plan [P-CONFIG]` — **ne** `plan.md § 3.1`. A sorszám elcsúszik, ha a plan bővül; az ID nem. Ha a plan-ben egy szekciónak **nincs** `[P-…]` ID-ja, az plan-hiány → `tasks-questions.md` kérdés (ne találj ki ID-t). |
| **Egy elsődleges forrás (D)** | Pontosan **egy** ID az elsődleges. Ha egy másik szekció is releváns, az zárójelben: `— plan [P-CFGPROP] (lásd még: [P-CONFIG])`. Két egyenrangú ID egy taskon **tilos** — ha tényleg kettő kell, a task **két taskra bontandó**. |
| **Csak végrehajtható szekcióra (E)** | Az elsődleges hivatkozás célja mindig `[P-…]`-ID-t viselő terv-szekció. **Leltárra, célra, sorrendre nem hivatkozhatsz** (ezek nem is kapnak ID-t). Ha a taskhoz nem találsz terv-szekciót, az **plan-hiány** → `tasks-questions.md`, ne pótold saját szöveggel. |
| **Részhatókör, ha osztozol (F)** | Ha ugyanarra az ID-ra **több task** hivatkozik, mindegyik kap egy zárójeles hatókör-jelölést: `— plan [P-CONFIG] (config fájlok)` / `— plan [P-CONFIG] (betöltő modul)` / `— plan [P-CONFIG] (unit teszt)`. Enélkül az implementáló az első ilyen tasknál az **egész** szekciót megvalósítja. |

- A sorszám (`T001`, `T002`, ...) szekvenciális, a végrehajtási sorrend alapján.
- A leírás egysoros, konkrét, cselekvő igével kezdődik (pl. *Hozd létre*, *Bővítsd*, *Adj hozzá*, *Futtasd*).
- A fájl path kötelező, ha a task fájlt érint. Ha a task parancs futtatás, a fájl path elhagyható.
- **TDD jelölés:** teszt-írási taskot `[RED]`, a hozzá tartozó implementációs taskot `[GREEN]` prefixszel jelöld. A `[RED]` task mindig megelőzi a párját.
  - **Kivétel — browser E2E (UI) teszt:** ott a fail-first nem elvárt (a teszt a kész felületre íródik). Ha a teszt-író task az implementáció UTÁN áll, a markere **`[GREEN]`**, nem `[RED]` — különben a marker hamis TDD-sorrendet sugall. Ha mégis `[RED]`-nek hagyod (mert tényleg fail-first), a task szövegében **egy zárójeles félmondattal indokold**.
- **Marker minden taskon kötelező — prefix nélküli task nincs.** Indok: a prefix hiánya nem megkülönböztethető attól, hogy valaki **elfelejtette** a markert.
- **`[OPS]` — éles határvonal:** kizárólag olyan lépés kaphatja, amely **NEM módosít repo-fájlt**, hanem a **környezetet vagy egy artefaktumot** változtatja: build, image push, deploy, kézi konfiguráció, külső erőforrás létrehozása/törlése, jóváhagyás-kérés, rollback.
  - **Ami repo-fájlt szerkeszt, az SOHA nem `[OPS]`** — az `[RED]` (teszt írása/frissítése) vagy `[GREEN]` (forrás- és konfigfájl módosítása), akkor is, ha **regressziós javításról** van szó. Egy `TREG` task, amely egy meglévő tesztfájlt frissít, `[RED]` markert kap.
  - Ez a határvonal teszi lehetővé, hogy az `[OPS]` taskokat gépiesen ki lehessen szűrni a destruktív-művelet ellenőrzéshez (lásd lent) — ha kód-szerkesztő taskok is `[OPS]`-ok, az a szűrés használhatatlan.
- **Ellenőrzési task:** `[CHECK]` prefix, minden logikai csoport végén kötelező — konkrét parancsot tartalmaz a plan `Ellenőrzési stratégia` szekciójából (pl. `npm test`, `npm run typecheck`). Fájl path elhagyható.
- **Párhuzamosítható task jelölése:** ha egy task egy másikkal egyszerre elvégezhető (köztük nincs függőség), jelöld `⟂ Tkkk` suffixszel. Csak akkor jelöld, ha a párhuzamosítás valóban időt takarít meg.
  - **Példa:** `- [ ] T012 [GREEN] Implementáld a foo service-t — `src/foo.ts` ⟂ T013` — azt jelenti, hogy T012 és T013 egyszerre szerkeszthető, mert **nem ugyanazt a fájlt érintik** és nincs köztük függőség. Ha ugyanazt a fájlt érintenék, NEM jelölhető párhuzamosnak.
  - **🔴 `[CHECK]` SOHA nem párhuzamosítható azzal a taskkal, amely az általa futtatott artefaktumot létrehozza vagy módosítja** (teszt-író `[RED]`/`[GREEN]` ⟂ a saját `[CHECK]`-je = hamis zöld: a `[CHECK]` a régi vagy hiányzó tesztfájlon fut le). Ellenőrzés a `⟂` kiírása előtt, mechanikusan: **a két task fájlhalmaza diszjunkt-e?** Ha bármelyik fájl közös — vagy az egyik task azt a fájlt/parancsot futtatja, amit a másik ír —, a `⟂` **tilos**.
- **Sorszámozási konvenciók — `T`, `TREG`, `TLAST`:**
  - **`Tnnn`** — normál, szekvenciálisan számozott implementációs task (`T001`, `T002`, …) a logikai csoportokban.
  - **`TREGn`** — regressziós felülvizsgálati task (`TREG1`, `TREG2`, …) a kötelező „Regressziós tesztek felülvizsgálata" záró csoportban. Sorrendben, `[CHECK]` nélkül. Csak olyan fájlra, amely a plan `Regressziós érintettség` táblázatában van, de a `Tervezett módosítások`-ban nincs. **Markere `[RED]`** (meglévő tesztfájlt frissít) — **nem `[OPS]`**, mert repo-fájlt szerkeszt.
  - **`TLASTn`** — a „Dokumentáció" záró csoport taskjai (`TLAST1`, `TLAST2`, …), a lista legvégén, ha vannak. Ezek futnak utoljára. **FONTOS (DS4):** a `docs-generated/` minden fájlja (`system-overview.md`, `architecture.md`, `CHANGELOG.md`, `design-drift.md`, mappa-index) a `08-doc-sync` fázis **kizárólagos** gazdája; a 04 ezekhez **nem** generál `TLAST` taskot.
    - **Komponens-README — a határvonal a komponens létezése:** **meglévő** komponens README-jének frissítése (env-változó, port, indítás, kapcsolatok) a **08-doc-sync** dolga → **nincs rá `TLAST`**. **Új komponens első `README.md`-je** viszont a felépítés része → normál `Tnnn` taskként szerepel (`[GREEN]`), a komponens többi fájljával együtt, **nem** `TLAST`-ként.
    - **🔴 Státusz-frissítő task TILOS.** Soha ne vegyél fel taskot a `spec.md` / `plan.md` / `tasks.md` **státuszmezőjének** átállítására („állítsd `Kész`-re", „frissítsd a fázis állapotát"). A státusz-életciklus a **keretrendszer gépezete**: a `07-validate` állítja mindhármat `Kész`-re PASS esetén. Egy ilyen task ütközik vele, és hamis lefedettséget ad. Ha a spec `Definition of done`-jában szerepel ilyen „meta" pont (pl. *„a dokumentáció és a spec.md állapota frissítésre került"*), az **spec-hiba** — ne fedd le taskkal, hanem vedd fel a `tasks-questions.md`-be.
    - `TLAST` tehát csak akkor kerül a listába, ha a plan **explicit** kér egy olyan dokumentáció-frissítést, ami **sem** a `docs-generated/`-ben él, **sem** komponens-README (pl. egy projekt-specifikus kézi doksi).
  - A számozás minden prefixen belül 1-től indul és növekvő.

---

## Leírás minőségi elvárások

**A task leírása navigációs pont, nem önálló specifikáció.** Az implementáló agent a plan-t olvassa be munkavégzés előtt — a task feladata az, hogy egyértelműen megmutassa, a plan melyik szekciójára vonatkozik a változtatás. A részletes logikát, interfészeket, hibakezelést a plan tartalmazza.

A leírásnak tartalmaznia kell:
- **Mit csinálni** — cselekvő ige + érintett egység neve (függvény, osztály, fájl)
- **Melyik fájl** — a path kötelező, ha a task fájlt érint
- **Plan szekció hivatkozás** — **mindig kötelező**, a stabil ID-val: `— plan [P-…]` (a formátum és a szabályok fent, a *Plan-hivatkozás minden taskon* táblában)

Részletet **csak akkor** adj a task leírásába, ha a plan nem tartalmazza:
- Parancs futtatásoknál: a tényleges shell parancs (pl. `openssl genrsa -out key.pem 2048`)
- Külső erőforrás hivatkozásnál: ha a task teszteléséhez vagy futtatásához külső erőforrás kell (tanúsítvány, API kulcs, mock adat, speciális konfiguráció), hivatkozz a plan azon szekciójára, ahol ez megtalálható (`— plan [P-CONFIG]`). Az implementáló agentnek ne kelljen keresgélnie.

> **🔴 Duplikáció-tilalom (PID1/b) — a részlet a plan-ben él.** Ha egy érték-lista, kód→kód leképezés, lokátor-stratégia vagy lépéssor **már benne van a plan-ben**, azt a taskba **nem másolod át**: a task egy sorban megmondja, mit kell tenni, és `[P-…]`-val odamutat. Két helyen tartott azonos tartalom **szétcsúszik**, és utána senki nem tudja, melyik az igaz.
> - **Ha úgy érzed, a taskba kell a részlet, mert enélkül nem végrehajtható** → a részlet **a plan-ből hiányzik**: fix-módban (05-analyze) írd a **plan-be** (a `plan-fixer` dolga), normál flow-ban vedd fel `tasks-questions.md` kérdésként. A tasks.md **soha nem a plan pótléka**.
> - **Kivétel — a `[CHECK]` és `[OPS]` parancsok:** ezek szó szerint a taskban állnak (az implementáló ezt futtatja), a plan-ben lévő azonos paranccsal **karakterre egyezően**.

**Tömörítési elv:** amit egy fejlesztő egy mondatban el tud mondani kollégájának, az elég. A részlet a plan-ban van — ne másold át.

| Túl bőbeszédű | Jó |
|---|---|
| `Implementáld: async callLegacyVerify(legacyLoginBaseUrl, jweToken, logger): Promise<{userId, sessionId, regId}> — GET <url>/verify (Authorization: Bearer), nem 200 esetén throw new HttpError(403, 'Legacy token verification failed', 'TMP_031')` | `Implementáld a callLegacyVerify service-t (GET /verify, TMP_031 hibakezeléssel)` |
| `Írd át a hibatesztek { error: "..." } expected response-ait { correlationId: <string>, messages: [{ code: "TMP_XXX", params: { description: "..." } }] } formátumra` | `Frissítsd a hibateszt expected response-okat ErrorMessageResponse formátumra` |

**Hosszúsági korlát:** ha a leírás megközelíti a 100 karaktert, valószínűleg plan-részletet másoltál bele — elég a hivatkozás.

---

## Tasks struktúra

```md
# Cycle NN: <cím> — Tasks

**Státusz:** `Piszkozat` | `Implementálásra kész`

## Prerequisite dokumentumok

_Az implementáló agent ezeket olvassa be a végrehajtás előtt._

- `specs/<cycle-name>/plan.md`
- _(további Reviewed artifaktok a plan Schema Artifaktumok táblájából)_

> `[RED]` = teszt írása (bukni fog) · `[GREEN]` = implementáció (teszt zöldítése) · `[CHECK]` = ellenőrzés futtatása · `[OPS]` = nem-TDD lépés (build, deploy, kézi konfiguráció, jóváhagyás, rollback)

## <Logikai csoport 1 — a plan végrehajtási sorrendje alapján> — plan [P-CONFIG], [P-REDIS]

- [ ] T001 [RED]   ... — plan [P-CONFIG] (unit teszt)
- [ ] T002 [GREEN] ... — plan [P-CONFIG] (betöltő modul)
- [ ] T003 [CHECK] Futtasd: `npm test -- path/to/test.ts` — plan [P-CONFIG]

## <Logikai csoport 2> — plan [P-ROUTING]

- [ ] T004 ... — plan [P-ROUTING]
- [ ] T005 [CHECK] Futtasd: `npm run typecheck` — plan [P-ROUTING]

## Plan-lefedettség (fordított tábla)

_Minden `[P-…]` ID-t viselő plan-szekció szerepel itt, a hozzá tartozó taskokkal._

| Plan szekció (ID + cím) | Taskok | Csoport |
|---|---|---|
| `[P-CONFIG]` Konfigurációs rendszer | T001, T002, T003 | 1 |
| `[P-ROUTING]` Dinamikus routing | T004, T005 | 2 |
| `[P-DOCS-ONLY]` … | — (nincs task: <indok>) | — |
```

**A csoport-fejléc plan-hivatkozása (B) kötelező:** minden `## <csoport>` cím végén ott vannak a csoport által lefedett plan-ID-k. Ez teszi emberi szemmel egy pillantás alatt követhetővé, hogy melyik terv-fejezet hol valósul meg — a taskok ugyanis **végrehajtási sorrend** szerint csoportosulnak, nem a plan tagolása szerint, így egy plan-szekció **több csoportba is szóródhat** (pl. `[P-CONFIG]` teszt-írása az 1., implementációja a 3. csoportban).

**A `Plan-lefedettség` tábla (C) kötelező, és a lista LEZÁRÁSAKOR készül** — akkor, amikor már minden task megvan. Nem külön munka: végigmész a plan `[P-…]` szekcióin, és mindegyikhez kigyűjtöd a rá hivatkozó task-azonosítókat. **Minden ID-nak szerepelnie kell**: ha egy plan-szekcióhoz nem tartozik task, a sor akkor is bekerül, `—` és **egy mondatos indok** (pl. „csak ellenőrzési stratégia, a 07 futtatja"). Indok nélküli üres sor = lefedettségi rés.

A csoportok a plan végrehajtási sorrendjének szakaszait tükrözik. Minden csoport önállóan elvégezhető és ellenőrizhető. Minden csoportnak van legalább egy `[CHECK]` taskja a végén.

**Kötelező záró csoportok:** a tasks lista utolsó két csoportja mindig a következő, ebben a sorrendben:

**1. Regressziós tesztek felülvizsgálata** — kizárólag azokhoz a fájlokhoz, amelyek **szerepelnek** a plan `Regressziós érintettség` táblázatában, de **nem szerepelnek** a plan `Tervezett módosítások` szekciójában. Ha egy fájl mindkét helyen szerepel, az mindig T task — nem TREG. Csak sima taskként (`[ ] TREG...`) vedd fel `[CHECK]` nélkül. Ha nem igényel módosítást, a task jelzésértékű („Ellenőrizd, hogy érintetlen maradt"). **A regressziós tesztek FUTTATÁSA nem ide való — az a validate fázis (07) feladata.**

**Sorrendszabály:** A TREG taskokat az implementáló agent a Dokumentáció szekció előtt, de az integrációs [CHECK] taskokat tartalmazó szekció után végzi el. Ha egy TREG fájl frissítése szükséges ahhoz, hogy egy korábbi szekció [CHECK] taskja zöld legyen, az a fájl nem TREG — T taskként kerül a megfelelő szekció [CHECK] taskja elé.

**Egy fájl a tasks listában csak egyszer szerepelhet.**

Ha a plan azt mondja, hogy nincs regressziós érintettség, ez a csoport kihagyható.

```md
## Destruktív / osztott környezetet érintő taskok — jóváhagyás és rollback

Ha a plan **közös (nem eldobható) környezetet** módosító lépést tervez — deployment/pod csere osztott klaszterben, image push közös registrybe, seed vagy törlés osztott adatbázisban, konfiguráció felülírása —, azt **három tasknak kell közrefognia** a saját logikai csoportjában:

```md
- [ ] T0nn [OPS]   Kérj JÓVÁHAGYÁST a felhasználótól a <művelet> futtatására — érintett: <környezet/namespace/registry>; a művelet más fejlesztők munkáját is érintheti. Rögzítsd az eredeti állapotot FÁJLBA: `<állapot-kiolvasó parancs> > .rollback-state`
- [ ] T0nn [OPS]   <a tényleges destruktív művelet> — `<konkrét parancs; a korábbi lépés állapotát a fájlból olvasva>`
- [ ] T0nn [CHECK] Ellenőrizd a művelet sikerét — `<ellenőrző parancs + elvárt kimenet>`
- [ ] T0nn [OPS]   ROLLBACK (csak ha az előző `[CHECK]` elbukott): állítsd vissza az eredeti állapotot — `<visszaállító parancs, a .rollback-state-ből olvasva>`
```

> **🔴 Állapot-perzisztencia — a leggyakoribb csendes hiba.** Minden task **külön shellben** fut, ezért a `VAR=...` vagy `export VAR=...` a **következő taskra elpárolog**. Ha a rollback vagy a deploy egy korábbi taskban előállított értékre (mentett eredeti azonosító, generált egyedi tag) hivatkozik, az **üres paraméterrel futna** — vagyis a rollback papíron megvan, a gyakorlatban nem működik. Ezért az ilyen állapot **fájlba kerül**, és a későbbi taskok onnan olvassák; vagy a függő parancsokat **egy taskba** vonod.

Az állapot-fájlra két további szabály:
- **Hova kerüljön:** a ciklus mappájába (`specs/cycle-NN-<cycle-name>/.rollback-state`), **ne a repo gyökerébe**. Ha mégis a gyökérbe kerül, vedd fel egy taskot, ami a `.gitignore`-ba is beírja — különben egy megszakadt futás után a munkafában marad, és bekerülhet egy commitba.
- **Takarítás kötelező:** a csoport utolsó taskja (vagy a sikeres `[CHECK]`) törölje (`rm -f`). Megszakadt futás után egy régi állapot-fájl **rosszabb, mint a semmi**: egy elavult azonosítóra állítana vissza.

- A **jóváhagyó task az első** — a destruktív művelet nem futhat le anélkül, hogy a felhasználó rábólintott volna.
- A jóváhagyó task **rögzíti az eredeti állapotot** (a kiolvasó paranccsal együtt) — enélkül a rollback nem végrehajtható.
- A **rollback task a csoport végén** áll, feltételesen. Ha a plan nem ad rollback-forgatókönyvet, az **plan-hiányosság**: vedd fel kérdésként a `tasks-questions.md`-be, ne találd ki magad.
- **Ha a művelet felülír egy meglévő azonosítót** (pl. ugyanarra az image-tagre pushol), jelezd: ilyenkor **nincs mihez visszaállni**, tehát vagy verziót kell léptetni, vagy a rollback nem valós — ez a plan felülvizsgálatát igényli.

## Regressziós tesztek felülvizsgálata

- [ ] TREG1 Ellenőrizd / frissítsd: `test/unit/foo.test.ts` — érintett, mert [indok a plan-ből]
- [ ] TREG2 Ellenőrizd / frissítsd: `test/integration/cycle-XX-foo.sh` — érintett, mert [indok a plan-ből]
```

**2. Dokumentáció** — önálló, utolsó csoport, **csak ha szükséges**. **A `docs-generated/` egyetlen fájljához sem (architecture.md, system-overview.md, CHANGELOG.md, design-drift.md), és meglévő komponens `README.md`-jéhez sem generálsz `TLAST` taskot** — ezeket a `08-doc-sync` fázis írja és tartja konzisztensen, a teljes ciklus rálátásával (DS4). Ez a csoport **csak akkor** kerül a listába, ha a plan **explicit** kér egy olyan dokumentáció-frissítést, amely **nem** a `docs-generated/` gazdája alá tartozik. Tisztán átnevezési/refaktorálási ciklusnál, vagy ha a plan nem nevez meg ilyen doksit, ez a csoport **elhagyható**.

```md
## Dokumentáció

- [ ] TLAST1 ...a plan által explicit kért, NEM docs-generated/ alá tartozó dokumentáció-frissítés...
```

_Megjegyzés a doksi-felelősségről (DS4): az `architecture.md` és a teljes `docs-generated/` mappa **kizárólag a `08-doc-sync` fázis** gazdája — a korábbi `TLAST1 → docs/architecture.md` záró task **nyugdíjazva**. Az implementáció (06) a kódra koncentrál; a megvalósult rendszer „as-built" dokumentációját (működésleírás, architektúra, changelog, drift) a doc-sync komponálja és validálja a saját konzisztencia-kapujával. Így nincs kettős író és nincs sorrend-probléma._

---

## Egy jó task ismérvei

- **Kis méretű**: egy task akkor önálló commitra alkalmas, ha **(a) legfeljebb 2 fájlt érint, ÉS (b) egyetlen logikai változást fed le**. Ha 3+ fájl VAGY több független logikai változás van benne, bontsd önállóan commitolható részekre. (A határeset — pl. 2 fájl + összetett logika — is bontandó, ha a (b) feltétel sérül.)
- **Konkrét**: egyértelmű, mit kell csinálni és melyik fájlban.
- **Elvégzettnek számít**, ha: az érintett fájl módosítva van, és a csoport záró `[CHECK]` taskja hibamentesen lefutott. Egy `[RED]` vagy `[GREEN]` task önmagában nem tekinthető kész-nek, amíg a csoportzáró `[CHECK]` nem zöld.
- **Nem átfedő**: egy változtatás csak egy taskban szerepel.

Ha egy task túl nagy, bontsd ketté.

---

<!-- INCLUDE:shared/quality-check-tasks.md -->

## Megállási szabályok

Ha tasks írása közben az alábbiak bármelyike teljesül, **STOP — állj meg és jelezd a felhasználónak** (ne találd ki a hiányzó részt):

- **Task nem specifikálható:** nincs egyértelmű érintett fájl, nincs elvégzési kritérium, vagy a lépés nem bontható le egyértelműen. Ez a plan hiányosságát jelzi. Állítsd a `plan.md` státuszát vissza `Piszkozat`-ra, jelezd pontosan mi az alulspecifikált lépés, és kérd a plan frissítését. A tasks lista csak ezután folytatható.
- **A plan egy `Tervezett módosítások` bejegyzéséhez nem tudsz taskot megfogalmazni:** a bejegyzés alulspecifikált vagy értelmezhetetlen. Állítsd a `plan.md`-t `Piszkozat`-ra, jelezd melyik bejegyzés, és kérd a pontosítást.
- **Egy task csak feltételesen végezhető el** (pl. egy még nem létező fájltól vagy egy másik ciklus eredményétől függ): jelezd a függőséget, és kérj döntést — előfeltétel-taskként vegyük-e fel, vagy a plan hiányos.
- **A plan és a meglévő kód ellentmond egymásnak:** egy lépés megvalósíthatatlannak tűnik a jelenlegi kódbázis alapján. Ne módosítsd a plan-t magad — jelezd, és kérj döntést.
- **Körkörös függőség a taskokban:** A → B → A jellegű függőség, amit nem lehet feloldani átrendezéssel. Jelezd pontosan, és kérj döntést.

Minden esetben csak **egy** problémát jelezz egyszerre.

---

## Státusz kezelés

### Mechanikus kapu a lezárás előtt (M)

Ugyanaz a determinisztikus kapu, ami a `05-analyze` első lépése — de **itt fut le, a lezárás előtt**:

<!-- INCLUDE:shared/python-cmd.md -->

```bash
python3 <platform-scripts-mappa>/analyze-gate-check.py specs/cycle-NN-<cycle-name>
```

- **`0`** → nincs blokkoló megállapítás; folytatható a lezárás. A `## Javaslatok` és a `## Leltár` blokk tájékoztató — a javaslatokat eldöntheted, de nem blokkolnak.
- **`1`** → **nincs státuszváltás.** A `## Must Fix` tételek gépiesen kimutatott hibák (hiányzó `— plan [P-…]` hivatkozás, nem létező ID, marker, `⟂` szimmetria, elavult `Plan-lefedettség` tábla, task nélküli DoD-pont, task-határon átnyúló shell-változó, nem létező futtatott artefaktum).
  - a **`célfázis: 04`** tételeket **most javítsd**, majd futtasd újra a kaput;
  - a **`célfázis: 03` / `02`** tételeket a *Megállási szabályok* szerint jelezd a felhasználónak — a plan vagy a spec hiányát nem te javítod.
- **`2`** → használati hiba (hiányzó fájl) → jelezd, ne találgass.

> **Miért itt (M):** ha a hiba már itt kiderül, a javítás **ugyanabban a fázisban, friss kontextusban** történik. Ha átcsúszik, a `05-analyze` önjavító hurkában derül ki, ahol egy fixer-subagentet és egy analyzer-kört kell rá elhasználni — ugyanarra a hibára.


Ha a lista teljes, a minőségellenőrzés átment **és a mechanikus kapu `0`-t adott**, tedd fel a kérdést a felhasználónak:
*"A task lista minőségellenőrzése átment. Készen áll a tasks lista implementálásra? Ha megerősíted, átállítom `Implementálásra kész` státuszra."* — Ne állítsd át a státuszt a megerősítés előtt. **A válasz végén helyezd el a `tasks.md` közvetlen, kattintható linkjét.**

Ha a felhasználó megerősíti:
- Állítsd a `tasks.md` státuszát `Implementálásra kész`-re.
- **Azonnal commitolj** a lenti *Fázis-záró commit* szerint (`<FÁZIS-TAG>` = `04-tasks`). Megerősítés → státuszírás → commit: ez egyetlen lépéssor, ne szakítsd meg.

<!-- INCLUDE:shared/phase-commit.md -->

A fenti blokkban a `<FÁZIS-TAG>` értéke ebben a fázisban: **`04-tasks`**, a záró státusz: **`Implementálásra kész`**.

> **Kész lifecycle:** a `tasks.md` az `Implementálásra kész` → (implementáció során `Validálásra kész`) → a validate (07) PASS után `Kész` státuszra lép. A 08 fázis már `Kész`-t vár.

Ha a státusz `Implementálásra kész`, **de a fázis-záró commit hiányzik** (VCS-es projekt, `git log -1 --oneline` nem a `cycle-NN: 04-tasks` commitot mutatja) — először commitolj, csak utána zárd le a fázist.

Ha a státusz `Implementálásra kész` (és a commit megvan), állj meg. Ne kezdj implementálni vagy analízist. Jelezd a felhasználónak a következő lépést és a fázis indító parancsát, például:
> *"A task lista kész. Folytathatjuk az 5. lépéssel (analyze — kereszt-fázisos konzisztencia ellenőrzés). Az új fázis megkezdése előtt mindenképpen futtass egy `/clear` parancsot a kontextus kiürítéséhez, majd használd ezt a parancsot:
> ```
> /bs-analyze input: @specs/cycle-NN-<cycle-name>
> ```"*
> **A válasz végén helyezd el a `tasks.md` közvetlen, kattintható linkjét.**

---

<!-- INCLUDE:shared/questions-tasks.md -->
---

<!-- INCLUDE:shared/fix-mode-tasks.md -->
