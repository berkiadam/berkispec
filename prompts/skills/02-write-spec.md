---
phase: 02
name: write-spec
description: "Használd egy ciklus indításakor (Phase 02) a roadmap alapján, a funkcionális/üzleti követelmények specifikálásához. Megnyitja a ciklus git branch-ét ('feature/cycle-NN-...'), és létrehozza a 'spec.md'-t ('Tervezésre kész') + a 'spec-questions.md'-t. Előfeltétel: 'specs/roadmap.md' státusz 'Kész'."
prerequisites:
  - "specs/roadmap.md státusz: Kész"
output:
  - "specs/cycle-NN-<name>/spec.md státusz: Tervezésre kész"
  - "specs/cycle-NN-<name>/spec-questions.md"
prev: 01-add-cycles
next: 03-write-plan
subagents: []
---

# 02 — Spec írás

Spec driven development-ben fejlesztünk szoftvert. A fejlesztés ciklusokra van bontva. Minden ciklus egy önállóan lefejleszthető, önállóan tesztelhető részegysége a teljes implementációnak.

Ez a fejlesztési folyamat **2-es fázisa (a 0–9 fázisokból)**:
0. projekt inicializálás (setup)
1. ciklusok kezelése (setup)
2. **spec** ← most itt vagyunk
3. plan
4. tasks
5. analyze
6. implement
7. validate
8. doc-sync
9. review & merge

---

## Előfeltétel

0. **`conventions.md` létezés-ellenőrzés:** olvasd be a projekt gyökerében a `conventions.md`-t. Ha nem létezik, STOP — térjenek vissza a `00` fázishoz. **Munkafa:** futtasd `git status --short`. Ha van commitálatlan változtatás, listázd, és kérdezd meg egy körben, hogy commitáljam-e most vagy folytassam — várj a válaszra. (A 02 branchet hoz létre; commitálatlan változások átkerülhetnek az új branch-re.)

1. **Roadmap ellenőrzés:** Olvasd be a `specs/roadmap.md`-t. **Ha a státusz nem `Kész`, ne kezdj el spec-et írni.** Jelezd a felhasználónak, hogy a roadmap még nem zárult le, és térjenek vissza a `01` ciklusok kezelése fázishoz. Ha a státusz `Kész`, keresd meg a megadott ciklus (`cycle-NN-<cycle-name>`) bejegyzését a roadmap-ben, és használd azt a spec kiindulópontjaként — a viselkedés, az érintett komponensek, az előfeltételek és a teszt kritérium mind alapot adnak a spec részletes kidolgozásához.

1.b **Current-truth kiindulás (DS5):** ha létezik a `docs-generated/system-overview.md`, olvasd be — ez a megvalósult (as-built) rendszer konszolidált, naprakész működésleírása, amit a `08-doc-sync` fázis tart karban. A spec a **jelenlegi valóságból** induljon: nézd meg, milyen flow-k/állapot/endpointok léteznek már, hogy az új spec ezekre épüljön, ne ütközzön velük. **Guard:** ha a fájl még nem létezik (korai ciklus / a bootstrap előtt), **ne állj meg** — jelezd egy mondatban, hogy a current-truth doksi még nincs, és folytasd a spec írását a roadmap alapján.

2. **Branch létrehozás:** Ellenőrizd, hogy a cycle branch létezik-e. Ha nem, hozd létre a cycle neve alapján (a `specs/roadmap.md`-ből deriválva):
   ```bash
   git checkout -b feature/cycle-<cycle-name>
   ```
   Ha a felhasználó explicit más branch nevet adott meg, azt használd. A spec, plan, tasks fájlok és a schema artifaktumok mind erre a branch-re kerülnek.

---

## Feladatod

**Ha már létezik `spec.md` a `specs/cycle-NN-<cycle-name>/` mappában:** olvasd be a `spec.md`-t és a `spec-questions.md`-t (ha létezik). Futtasd le a minőségellenőrzést. Ha hiányosságot vagy problémát találsz, vedd fel kérdésként a `spec-questions.md`-be, és állítsd vissza a `spec.md` státuszát a valódi állapotnak megfelelően (`Nyitott kérdések vannak` vagy `Piszkozat`). Utána az iterációs szabályok szerint folytatd.

**Ha még nem létezik `spec.md`:** hozd létre a `specs/cycle-NN-<cycle-name>/` mappában az alábbi struktúra szerint.

**Ne készíts plan-t, task listát vagy implementációt.** A spec célja a követelmények, a scope és a viselkedés rögzítése — nem a megvalósítás megtervezése.

### Spec vs plan — mi hova tartozik (példák)

A spec a **viselkedést** írja le (mit lát a kliens/felhasználó, milyen bemenetre milyen kimenet), a plan az **implementációt** (hogyan valósul meg). Példák:

| Spec-be való (viselkedés) | Plan-be való (implementáció) |
|---|---|
| „A `/verify` végpont 403-at ad `TMP_031` errorCode-dal, ha a token érvénytelen." | „A `callLegacyVerify` service `HttpError(403, ...)`-t dob, a `proxy.ts:42`-ben hívva." |
| „A token lejárta után a kérés újraautentikálást igényel." | „Redis-ben `token:<id>` kulcs TTL-lel, refresh lock `SETNX`-szel." |
| „A válasz tartalmazza a `correlationId`-t." | „A `correlationId`-t a `requestContext` middleware injektálja." |
| „Két párhuzamos kérés nem indíthat két refresh-t." | „Elosztott lock Redis `SET NX PX`-szel, 5s TTL." |

Ha egy mondat technológiát, fájlnevet, függvényt vagy konkrét adatszerkezet-megvalósítást nevez meg → az plan-be való, töröld a spec-ből.

---

## Spec struktúra

\`\`\`md
# Cycle NN: <cím>

**Státusz:** \`Piszkozat\` | \`Nyitott kérdések vannak\` | \`Tervezésre kész\`

## Célkitűzés

_Mit akarunk elérni ezzel a ciklussal? Egy-két mondat: üzleti vagy technikai cél, és miért szükséges._

## Architektúra / folyamat leírás

_Komponensek kapcsolata és az adatfolyam. Ha a ciklus komponenseket érint, készíts Mermaid \`graph\` diagramot. Ha új folyamatot vagy hívási sorrendet vezet be, készíts Mermaid \`sequenceDiagram\`-ot is. Ha egyik sem értelmezhető, hagyd el._

_**Diagram szabályok:**_
- _Mermaid node labelekben használj \`<br/>\` sortöréshez (a \`\n\` nem renderelődik le)._
- _Ha az ábra hívási sorrendet ábrázol (pl. \`graph\` folyamatábra, \`sequenceDiagram\`), számozd be a nyilakat ①②③… sorrendben. Ahol a szekvencia nem értelmezhető (pl. statikus architektúra-áttekintő), a számozás elhagyható._

## Komponensek és viselkedés

_Részletes viselkedési spec komponensenként: API végpontok, request/response formátum, belső logika, hibakezelés._

_Ha egy komponens viselkedésének megértéséhez **olvasandó segédfájl** szükséges (pl. egy meglévő mock szerver vagy shared service), hivatkozd be közvetlenül a leírásánál is. A módosítandó vagy létrehozandó fájlok **nem** kerülnek ide — azok kizárólag a `Hivatkozott fájlok` szekció feladata._

_Ha a spec olyan új komponenst vezet be, amelynek technológiai alapdöntései még nyitottak (build rendszer, kommunikációs mód, deployment mechanizmus, runtime/nyelv, stb.), add hozzá a komponens leírásához ezt a jelzést: **„Technológiai alapdöntések tisztázandók a plan fázisban."** — A spec ne specifikálja ezeket a részleteket, csak jelezze, hogy a plan fázisnak erre figyelmet kell fordítania._

_**Döntési kritérium:** Akkor kell a jelzés, ha a komponens projekt struktúrájára, build rendszerére vagy deployment mechanizmusára **nem tudsz egyértelműen egy meglévő komponenst mutatni mintaként a repóban**. Ha van már hasonló komponens (pl. egy újabb Fastify app, ahol már létezik minta), a jelzés elhagyható. Ha nincs (pl. az első Java projekt, az első gRPC service), a jelzés kötelező._

## Out of scope

_Mi NEM tartozik ebbe a ciklusba. Explicit felsorolás — megakadályozza a scope creep-et._

## Hivatkozott fájlok

_Dokumentációs és specifikációs anyagok: README-k, HOW-TO-k, OpenAPI leírók, Avro sémák, DB migrációk, meglévő spec fájlok, viselkedés-referencia szkriptek (pl. mock szerver, amelyet olvasni kell a viselkedés megértéséhez). **Forrásfájlok (.ts, .tsx, .js, package.json, stb.) nem kerülnek ide — azok a plan fázisban kerülnek azonosításra. A fájlok elérési útjai/linkjei mindig a fájl aktuális könyvtárához képest relatív útvonalak legyenek (a mappa mélységének megfelelő számú visszalépéssel a projekt gyökeréig, pl. `../../apps/legacy-login/README.md`), abszolút útvonalak vagy `file://` sémájú linkek nem használhatók.**_

_Ha a ciklus REST API-t, üzenetsor-üzenetet, cache struktúrát vagy DB sémát érint, és már léteznek formális leírók (OpenAPI YAML, Avro schema, Redis key map, DB migration), hivatkozd be őket itt. A plan fázis ezeket fogja validálni vagy — ha nem léteznek — generálni._

## Teszt specifikáció

_Tesztadatok, tesztelendő esetek (happy path + hibaesetek), kötelező viselkedési ellenőrzések._

## Kockázatok

_Mi sülhet el rosszul? Milyen feltételezéseken alapul a spec? Elfogadott POC korlátok, nyitott technikai kockázatok._

## Definition of done

_Ellenőrizhető, pipálható feltételek. Minden pont legyen konkrét és egyértelműen eldönthető (igen/nem)._
\`\`\`

---

## Kontextus betöltési szabályok

- Csak azt olvasd be, ami a spec megírásához feltétlenül szükséges.
- Ha egy bonyolult meglévő modult vagy logikát kell megértened, indíts egy **subagent**et a kutatáshoz. A subagent csak az összefoglalót adja vissza — a nyers fájltartalom nem kerül be a fő kontextusba.
- Ha az előző ciklusok architektúrájára van szükség, kérdezz rá egy mondatban — ne olvasd be az összes korábbi spec-et.
- Ha konkrét meglévő kódot kell érteni, csak az érintett fájlt vagy részt olvasd be.

---

## Folytatás megszakított futás után

Ha a spec fázis megszakad és új sessionban folytatódik:

```
1. Olvasd be a spec-questions.md aktuális állapotát (ha létezik).
   → Folytasd az első [ ] státuszú kérdéstől.

2. Olvasd be a spec.md aktuális állapotát.
   → Ha van [ ] nyitott kérdés: a státusz "Nyitott kérdések vannak".
   → Ha minden kérdés [x], de nincs user megerősítés: futtasd a
     minőségellenőrzést, majd kérj megerősítést (ne állítsd Tervezésre késznek).

3. Ha nincs spec.md: kezdd a "Feladatod" szerint.
```

Elég a `spec.md` és a `spec-questions.md` aktuális állapota + ez a prompt az újraindításhoz.

---

## Ambiguitás-vizsgálat — kérdés-keresési sablon

A kérdések felfedezéséhez menj végig az alábbi **10 kategórián**, és ahol **valódi ambiguitást** találsz, vedd fel kérdésként a `spec-questions.md`-be. **Iránymutatás, nem kötelezettség:** nem kell minden kategóriára kérdést feltenned — csak ahol tényleg hiányzik vagy kétértelmű az infó.

1. **Funkcionalitás** — mit csinál pontosan a rendszer? (pl. „A token lejárta után mi történik a folyamatban lévő kérésekkel?")
2. **Adatmodell** — mezők, típusok, kötelezőség, validáció. (pl. „A `userId` opcionális vagy kötelező a payloadban?")
3. **UX / interfész** — felhasználói vagy API felület viselkedése. (pl. „Hibakor mit lát a kliens — üzenet, kód, redirect?")
4. **Teljesítmény** — mérőszámok, limitek. (pl. „Van elvárt válaszidő vagy throughput?")
5. **Biztonság** — auth, jogosultság, titkosítás. (pl. „Milyen scope kell a végponthoz?")
6. **Integrációk** — külső rendszerek, szerződések. (pl. „A külső API melyik verziójára épülünk?")
7. **Hibakezelés** — hibaesetek, fallback. (pl. „Timeout esetén retry vagy azonnali hiba?")
8. **Jogosultság / szerepkörök** — ki mit tehet. (pl. „Admin és sima user között van különbség?")
9. **Observability** — naplózás, metrika, trace. (pl. „Mit kell naplózni a flow-ban korrelációhoz?")
10. **Egyéb** — minden, ami a fentiekbe nem fér be, de tisztázandó.

Ez csak a **kérdés-felfedezés segédlete** — a meglévő `spec-questions.md` flow változatlan.

---

## Nyitott kérdések kezelése

A `spec-questions.md` a spec fázis kérdés-nyilvántartója. **Minden felmerülő kérdést — bármilyen okból — azonnal ide kell felvenni, mielőtt a felhasználónak feltennéd.** Ez vonatkozik az üzleti döntésekre, ismeretlen korlátokra, kétértelmű követelményekre, hibaágakra és bármilyen más bizonytalanságra egyaránt.

**Alapszabály: a listából soha nem törlünk. Lezárt kérdést csak `[x]`-szel jelölünk — a szövege és a döntés megmarad.**

### spec-questions.md struktúra

Ha még nem létezik, hozd létre a `specs/cycle-NN-<cycle-name>/` mappában:

```md
# Cycle NN: <cím> — Spec kérdések

- [ ] K01 — [kérdés szövege]
- [x] K02 — [kérdés szövege] → [döntés / válasz röviden]
- [ ] K03 — [kérdés szövege] _(K02 megválaszolásából merült fel)_
```

Az új kérdést mindig a lista végére fűzd, a következő szekvenciális `Knn` számmal.

### Státusz átmenetek (spec.md státusz mező)

- Új spec indításakor: `Piszkozat`
- Ha van legalább egy `[ ]` státuszú kérdés a `spec-questions.md`-ben: `Nyitott kérdések vannak`
- Ha minden kérdés `[x]` státuszú és a minőségellenőrzés átment, és a user explicit megerősítette: `Tervezésre kész`

### Iterációs szabályok

1. Ha van `[ ]` státuszú kérdés a `spec-questions.md`-ben, tegyél fel **egyet**, és várd meg a választ. Ne zúdítsd rá egyszerre az összes kérdést a felhasználóra. **Minden alkalommal, amikor kérdést teszel fel vagy jóváhagyást/véleményezést kérsz, a válaszod végén kötelezően helyezz el egy közvetlen, kattintható markdown linket az érintett fájlokra (pl. `[spec-questions.md](file:///abszolút/útvonal/specs/cycle-NN-name/spec-questions.md)` formában).**
2. Ha a kérdés megválaszolódott: jelöld `[x]`-szel a `spec-questions.md`-ben, írj mellé egy soros összefoglalót (`→ ...`), és vezessük át a döntést a `spec.md` megfelelő szekciójába.
3. Ha a válasz új kérdést nyit meg: azonnal vedd fel a `spec-questions.md` lista végére a következő `Knn` számmal, mielőtt folytatnád.
4. Addig iterálj, amíg minden kérdés `[x]` státuszban van.
5. Ha minden kérdés lezárt, futtasd le a minőségellenőrzést. Ha átment, **tedd fel a kérdést a felhasználónak**: *"A spec minőségellenőrzése átment és minden kérdés lezárt. Készen áll a spec tervezésre? Ha megerősíted, átállítom `Tervezésre kész` státuszra."* — Ne állítsd át a státuszt a megerősítés előtt. **A válasz végén helyezd el a `spec.md` közvetlen, kattintható linkjét.**
6. Ha a felhasználó explicit megerősíti (pl. "igen", "kész", "mehet"), állítsd a `spec.md` státuszát `Tervezésre kész`-re, és készíts git commitot a fázis befejezéséről:
   ```bash
   git add specs/cycle-NN-<cycle-name>/
   git commit -m "cycle-NN: 02-spec"
   ```

Minden iteráció indítható új kontextussal: elég a `spec.md` és a `spec-questions.md` aktuális állapota + ez a prompt. Újraindításkor olvasd be a `spec-questions.md`-t, és folytasd az első `[ ]` státuszú kérdéstől.

---

## Megállási szabályok

Ha az alábbiak bármelyike teljesül, **STOP — állj meg és ne lépj tovább**:

- **Van `[ ]` státuszú kérdés a `spec-questions.md`-ben** — tegyél fel egyet a felhasználónak, várj a válaszra, majd folytasd. Ne tegyél fel több kérdést egyszerre.
- **A minőségellenőrzés hibát talált** — javítsd a hibát, majd futtasd újra. Ne állítsd `Tervezésre kész`-re a státuszt, amíg nem ment át.
- **A felhasználó megerősítése hiányzik** — a státusz `Tervezésre kész`-re csak explicit megerősítés után állítható. Ne állítsd át kérdezés nélkül.
- **A spec plan-tartalmú elemet tartalmaz** (pl. technológiaválasztás, implementációs részlet, konkrét fájlterv) — töröld, nem spec-be való.
- **A státusz már `Tervezésre kész`** — állj meg. Ne kezdj plan-t vagy task listát. Jelezd a felhasználónak a következő lépést és a fázis indító promptját, például:
> *"A spec kész. Folytathatjuk a 3. lépéssel (plan). Használd ezt a promptot:
> ```
> Kövesd a `prompts/skills/03-write-plan.md` utasításait.
> Input: `specs/cycle-NN-<cycle-name>/spec.md` (spec kontextus), ciklus: cycle-NN-<cycle-name>
> ```"*
> **A válasz végén helyezd el a `spec.md` közvetlen, kattintható linkjét.**


---

## Státusz kezelés

| Állapot | Feltétel |
|---|---|
| `Piszkozat` | Spec indításakor |
| `Nyitott kérdések vannak` | Van legalább egy `[ ]` kérdés a `spec-questions.md`-ben |
| `Tervezésre kész` | Minden kérdés `[x]` + minőségellenőrzés átment + **felhasználó explicit megerősítette** |

A `Tervezésre kész`-re váltás után készíts git commitot (`cycle-NN: 02-spec`) — lásd az Iterációs szabályok 6. pontját. Ne állítsd át a státuszt megerősítés nélkül.

> **Kész lifecycle:** a `spec.md` a `Tervezésre kész` után a ciklus végén — amikor a validate (07) PASS lezárja a ciklust — `Kész` státuszra lép. A 08 fázis már `Kész`-t vár. Ezt az átmenetet a 07 végzi, itt nem.

---

## Minőségellenőrzés — minden iteráció végén kérdezd meg magadtól:

- Van bármi ami a spec fájlban nem egyértelmű, hiányzik, vagy pontosításra szorul?
- Van-e olyan tartalom, ami plan-be vagy tasks-ba való, nem spec-be? Ha igen, töröld.
- Minden "Definition of done" pont ellenőrizhető és egyértelmű?
- Az "Out of scope" szekció megakadályozza-e a scope creep-et?
- A "Hivatkozott fájlok" lista teljes, **és kizárólag dokumentációs anyagokat tartalmaz?** (OpenAPI leírók, README-k, sémák, meglévő spec fájlok, viselkedés-referencia szkriptek) — `.ts`, `.tsx`, `.js`, `.mjs`, `package.json` és egyéb forrásfájlok **nem szerepelhetnek**; ha szerepelnek, töröld őket. Forrásfájlok azonosítása a plan fázis feladata. **Szigorú szabály: a specifikáció szöveges részeiben sem szerepelhetnek (még a Kockázatok vagy az Out of scope szekciókban sem) konkrét forrásfájlnevek! A fájlok elérési útjai/linkjei mindig a fájl aktuális könyvtárához képest relatív útvonalak legyenek (a mappa mélységének megfelelő számú visszalépéssel a projekt gyökeréig, pl. `../../apps/legacy-login/README.md`), abszolút útvonalak vagy `file://` sémájú linkek nem szerepelhetnek bennük.**
- **Minden hivatkozott érték, struktúra és adat specifikálva van?** — Ha a spec portot, URL-t, konfigurációs értéket, hibakódot vagy bármilyen adatstruktúrát (JSON, YAML, vagy egyéb formátum) említ vagy hivatkozik rá, teljesülnie kell:
  - A konkrét értéke vagy egyértelmű generálási szabálya szerepel a spec-ben
  - Van legalább egy példa (example request/response, example payload, stb.)
  - Ahol értelmezhető: szerepel vagy hivatkozva van egy séma (OpenAPI, JSON Schema, Avro, stb.)
  - Az implementálónak ne kelljen semmit kitalálnia — ha a spec leír egy mezőt, tudnia kell mi kerül bele
- **Minden hibaág specifikálva van?** — Menj végig az összes komponensen és hívási láncon, és ellenőrizd, hogy minden hibaeset explicit le van-e írva. Ez az ellenőrzés minden módosítási iteráció végén kötelező. Különösen:
  - REST hívásoknál: minden nem-200 válasz esetén meg kell adni a HTTP státuszkódot és az errorCode-ot (ha van), valamint a response body struktúráját
  - Validációs hibáknál: mi a feltétel, mi a visszatérési kód, mi kerül a response body-ba
  - Külső service hibáknál (timeout, 5xx): hogyan kezeli a hívó komponens, mit ad vissza a kliensnek
  - Ha egy hibaág nincs specifikálva, ne töltsd ki magad — jelezd nyitott kérdésként
- **E2E elfogadási feltétel a DoD-ban?** — Ha a ciklus bármilyen funkcionális viselkedést vezet be (API, service, UI flow), a DoD-ban szerepelnie kell egy E2E szintű elfogadási feltételnek. A konkrét módszertant (Playwright, pytest, mock szint) a plan fázis határozza meg — a spec az elvárást rögzíti, nem az implementációt. Ha nincs ilyen pont a DoD-ban, add hozzá.

- **Szükséges-e regressziós ellenőrzés?** — Ha a ciklus meglévő funkciót bővít vagy módosít, a spec Teszt specifikáció szekciójában jelezni kell, hogy a korábbi működés regressziós tesztekkel ellenőrizendő. Ez különösen kritikus, ha:
  - Meglévő interfész új funkcióval vagy elágazással bővül (pl. új paraméter, új kód ág, flow detection bevezetése) — a meglévő hívási út nem törhetett el
  - Közös komponens módosul (route handler, middleware, shared service) — minden fogyasztóját ellenőrizni kell
  - Meglévő viselkedés mellé új viselkedés kerül ugyanarra a végpontra vagy belépési pontra — a két ág egymástól függetlenül kell működjön

- **Rename / projekt-szintű csere — teljes lefedettség a DoD-ban?** — Ha a ciklus célja egy név (végpont, szimbólum, env-változó, fájlnév) **lecserélése az egész projektben** (a célkitűzés ilyenkor jellemzően „a teljes projektben" / „mindenhol" fordulatot tartalmaz), akkor a DoD nem elég, ha csak a *forráskódot* sorolja fel. A spec íráskor menj végig az alábbi artefaktum-osztályokon, és minden olyanra, ahol a régi név **ténylegesen előfordulhat**, vagy legyen explicit DoD-pont, vagy kerüljön az **Out of scope**-ba (indokkal). Ne maradjon szürke zóna:
  - **Forráskód** (`src/`, `apps/*/src/`) és a hozzá tartozó tesztek
  - **Élő, nem-forrás dokumentáció:** gyökér `README.md`, app-szintű README-k, `docs/` (architektúra, diagramok pl. `.drawio`), **az `.agent/` alatti skill/agent leírások** — ezek a rendszer *aktuális* viselkedését írják le, ezért átírandók
  - **Build-kimenet / generált artefaktum:** ha a `dist/` (vagy más generált mappa) verziókövetett, a DoD-ban szerepeljen egy **tiszta újrabuild** (a régi, átnevezett forrás orphan kimenete nem törlődik magától — pl. a `tsc` nem takarítja); vagy mondd ki Out of scope-ként, hogy a `dist/` nem követett
  - **Konfiguráció és env:** `.env*` minták, compose/CI fájlok, env-változó nevek
  - **Történeti artefaktumok** (lezárt ciklusok `spec.md`/`test-report`-jai, dátumozott logok, `roadmap.md` múltbeli bejegyzései): ezek **szándékosan érintetlenek** — tedd explicit Out of scope-ba, hogy az analyze/review ne jelezze hibaként, és hogy ne is írja át őket senki visszamenőleg.
  Megkülönböztető szabály: az **endpoint/szimbólum neve** (átírandó) ≠ az azonos szót használó **fogalom** (pl. „token cache", „Redis Cache" — marad). A DoD fogalmazzon elég pontosan ahhoz, hogy ez ne mosódjon össze.

---

## Fix-mód (analyze-hurok belépő)

> **Mikor aktív:** ezt a szekciót az `05-analyze` önjavító hurka indítja az `agents/spec-fixer.md` wrapperen keresztül — **nem** a normál spec-írás. A bemenet egy konkrét `Must Fix` lista, nem teljes újrafutás.

A fix-mód egy **szűkített belépő:** a megadott `Must Fix` megállapításokat javítod célzottan, **nem írod újra az egész specet**. (Ellenkező esetben egy olcsóbb LLM hajlamos elölről kezdeni a fázist — ez tilos.) A normál flow minőségi kapui (a fenti minőségellenőrzés) a javított részekre továbbra is érvényesek.

### Bemenet
- A spec-re szűrt `Must Fix` lista (kategória + leírás + `fájl:hely`).
- A `spec.md` és a `spec-questions.md` aktuális állapota.

### Auto-javítható vs kérdezni kell (a határvonal)

| Magától javítsd (auto) | Kérdésbe tedd (`spec-questions.md` új `Knn`) |
|---|---|
| Lefedettségi rés szöveges pótlása, naming-egységesítés, megfogalmazás-pontosítás, duplikált követelmény összevonása | Spec-szintű ambiguitás, hiányzó vagy nem eldönthető elfogadási feltétel, meghatározatlan viselkedés, üzleti döntés |

A `Must Fix`-et, amihez **valódi döntés** kell, **ne találd ki** — vedd fel új `Knn`-ként a `spec-questions.md` végére (a normál flow szerint), és **ne kérdezd közvetlenül a felhasználót** (fix-módban nincs interaktív csatornád). A kérdezést az orchestrátor (`05-analyze`) végzi, fázis-fejléccel.

### Státusz (auto, `[analyze-loop]` marker)
A hurok a `spec.md` státuszát `[analyze-loop]` markerrel nyitotta vissza (pl. `Piszkozat [analyze-loop]`). Amíg a marker jelen van, **automatikusan** lépteted a státuszt, megerősítés-kérés nélkül (eltérően a normál flow „megerősítés a státuszváltás előtt" szabályától):
- van nyitott `[ ]` kérdés a `spec-questions.md`-ben → `Nyitott kérdések vannak [analyze-loop]`;
- minden kérdés `[x]` és a célzott javítás kész → `Tervezésre kész [analyze-loop]`.

A marker fel- és levételét az orchestrátor kezeli; te csak a státusz-értéket lépteted, a markert változatlanul hagyod.

### Visszatérési összefoglaló (az orchestrátornak)
Adj vissza tömör összefoglalót: (a) mely `Must Fix`-eket javítottad és hogyan, (b) milyen új `Knn` kérdéseket vettél fel a `spec-questions.md`-be (azonosítóval). A `spec.md`-t és a `spec-questions.md`-t te írod; az `analyze-report.md`-t **nem** — az az orchestrátoré.
