---
phase: 02
name: bs-write-spec
description: "berkispec - 02. Használd egy ciklus indításakor (Phase 02) a roadmap alapján, a funkcionális/üzleti követelmények specifikálásához. A ciklus git branch-én dolgozik (a branch a 01 fázisban jött létre 'main'-ről), és létrehozza a 'spec.md'-t ('Tervezésre kész') + a 'spec-questions.md'-t. Előfeltétel: 'specs/roadmap.md' státusz 'Kész'."
prerequisites:
  - "specs/roadmap.md státusz: Kész"
output:
  - "specs/cycle-NN-<name>/spec.md státusz: Tervezésre kész"
  - "specs/cycle-NN-<name>/spec-questions.md"
  - "specs/cycle-NN-<name>/plan-input-from-prev.md és/vagy tasks-input-from-prev.md (csak ha van átadandó infó, IP1)"
prev: bs-add-cycles
next: bs-write-plan
subagents:
  - "agents/researcher.md"
shared:
  - "shared/input-from-prev.md"
---
# 02 — Spec írás
## Kontextus ellenőrzés

Ha azt detektálod, hogy ennek a fázisnak a futtatása most indul (ez az első prompt a fázisban), de a kontextus nem „friss” (azaz a beszélgetési előzmények tartalmaznak korábbi fázisokból vagy futásokból származó üzeneteket), akkor kérdezz rá a felhasználónál:
> *„Úgy tűnik, hogy a fázis indításakor a kontextus nem teljesen friss. Szándékosan nem futtattál `/clear`-t az új fázis megkezdése előtt (a tokenekkel való spórolás érdekében)?”*
Várd meg a felhasználó válaszát, mielőtt folytatnád a fázis futtatását.

---

Spec driven development-ben fejlesztünk szoftvert. A fejlesztés ciklusokra van bontva. Minden ciklus egy önállóan lefejleszthető, önállóan tesztelhető részegysége a teljes implementációnak.

Ez a folyamat **2. fázisa (0–9)**: 0-init · 1-ciklusok · **2-spec ←** · 3-plan · 4-tasks · 5-analyze · 6-implement · 7-validate · 8-doc-sync · 9-review.

---

## Előfeltétel

0. **Ciklus-beazonosítás:** ha a felhasználó megadott ciklust/fájlt, azt használd; különben a legfrissebb `specs/cycle-*` mappát ajánld fel megerősítésre — *"A(z) `specs/cycle-NN-<name>` ciklussal szeretnél dolgozni? Igen / Nem (megadom a ciklust)"* — és várj a válaszra, mielőtt továbblépsz.

1. **`conventions.md` létezés-ellenőrzés:** olvasd be a projekt gyökerében a `conventions.md`-t. Ha nem létezik, STOP — térjenek vissza a `00` fázishoz.

1.a **Munkafa-ellenőrzés (csak VCS esetén):** futtasd `git status --short`. Ha van commitálatlan változtatás, listázd, és kérdezd meg egy körben, hogy commitáljam-e most vagy folytassam — várj a válaszra. (No-VCS projektben — a `conventions.md` szerint nincs verziókezelő — ez és a lenti branch-lépés kimarad.)

2. **Roadmap ellenőrzés:** Olvasd be a `specs/roadmap.md`-t. **Ha a státusz nem `Kész`, ne kezdj el spec-et írni.** Jelezd a felhasználónak, hogy a roadmap még nem zárult le, és térjenek vissza a `01` ciklusok kezelése fázishoz. Ha a státusz `Kész`, keresd meg a megadott ciklus (`cycle-NN-<cycle-name>`) bejegyzését a roadmap-ben, és használd azt a spec kiindulópontjaként — a viselkedés, az érintett komponensek, az előfeltételek és a teszt kritérium mind alapot adnak a spec részletes kidolgozásához.

1.b **Visszatérő teszt-elvárások beolvasása (TC1):** ha létezik a `specs/test-conventions.md`, olvasd be — ez a projekt visszatérő teszt-elvárásainak és a hozzájuk tartozó recepteknek az élő regisztere, amit a `08-doc-sync` tart karban. **Guard:** ha a fájl még nem létezik (korai ciklus — még nincs promótálható tétel), **ne állj meg és ne hozd létre** — egy mondatban jelezd, és folytasd. A fájl használata:
   - a **2. és 3. szekció** tételeiből azt emeld be a `Teszt specifikáció` szekcióba (és — ha valódi elfogadási feltétel — a `Definition of done`-ba), amit **ez a ciklus tényleges elfogadási feltételként vállal**, **viselkedés-szinten**: mit kell ellenőrizni, milyen bemenetre mi a helyes kimenet. **Parancs, tesztfájl-útvonal, eszköznév és build/deploy lépés ide NEM kerül** — az a `plan.md` dolga (a spec/plan határvonal szerint);
   - a puszta „ne törjön el" jellegű regressziós tételeket **ne** emeld a spec-be — azok a `plan.md` `Regressziós érintettség` táblájába tartoznak, mert nem a ciklus célja;
   - az **1. szekciót** (koordináták, URL-ek, parancsok) csak **kontextusként** olvasod: ebből látod, milyen környezeti korlátok között mozog a ciklus. A spec-be nem kerül át.
   - **Érvénytelenítés jelzése (a 08 bemenete):** ha a ciklus egy meglévő baseline-tételt **érvénytelenít** (megszünteti vagy átalakítja a komponenst, amire hivatkozik), írd ki explicit a `Teszt specifikáció` szekció végén: *„Érvénytelenített baseline tétel: `<ID>` — <miért>."* Ebből tudja a `08-doc-sync` (TC4), hogy a tételt törölni kell a regiszterből. **Magad ne írd a `test-conventions.md`-t** — annak a doc-sync a kizárólagos gazdája.

1.c **Current-truth kiindulás (DS5):** ha létezik a `docs-generated/system-overview.md`, olvasd be — ez a megvalósult (as-built) rendszer konszolidált, naprakész működésleírása, amit a `08-doc-sync` fázis tart karban. A spec a **jelenlegi valóságból** induljon: nézd meg, milyen flow-k/állapot/endpointok léteznek már, hogy az új spec ezekre épüljön, ne ütközzön velük. **Guard:** ha a fájl még nem létezik (korai ciklus / a bootstrap előtt), **ne állj meg** — jelezd egy mondatban, hogy a current-truth doksi még nincs, és folytasd a spec írását a roadmap alapján.

2. **Branch-ellenőrzés (a branch a 01-ben jött létre — BD1):** a ciklus feature branch-ét már a **01-add-cycles** fázis létrehozta `main`-ről; a 02 **nem** nyit új branch-et. Verziókezelő mellett:
   - `git branch --show-current` → ha már a ciklus feature branch-én vagy, folytasd itt.
   - Ha egy másik branch-en vagy, de a ciklusé létezik → válts rá: `git switch feature/cycle-<cycle-name>` (a `conventions.md` `## Git és branching konvenciók` **Branch-elnevezési stratégia** szerinti névvel).
   - **Fallback** (ha a ciklus branch-e valamiért nem létezik — pl. régi flow vagy megszakadt 01): a branch-nyitó preflight (friss, tiszta `main`) után hozd létre: `git switch -c feature/cycle-<cycle-name>`. Ez kivétel, nem a főszabály — normál esetben a 01 már létrehozta.
   - **No-VCS ágon** (a `conventions.md` szerint nincs verziókezelő) ez a lépés kimarad.

   A spec, plan, tasks fájlok és a schema artifaktumok mind erre a branch-re kerülnek.

---

## Feladatod

**Ha már létezik `spec.md` a `specs/cycle-NN-<cycle-name>/` mappában:** olvasd be a `spec.md`-t és a `spec-questions.md`-t (ha létezik). **Futtasd le a koordináta-kiszűrést (KX)** a meglévő szövegen — egy korábbi futás (vagy egy másik ágens) hagyhatott bent környezeti koordinátát vagy deploy-eljárást; ezeket most helyezd át a `plan-input-from-prev.md`-be. Utána futtasd le a minőségellenőrzést. Ha hiányosságot vagy problémát találsz, vedd fel kérdésként a `spec-questions.md`-be, és állítsd vissza a `spec.md` státuszát a valódi állapotnak megfelelően (`Nyitott kérdések vannak` vagy `Piszkozat`). Utána az iterációs szabályok szerint folytatd.

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
| „A folyamatindítás a `POST /rtm/api/runtime/app/{appId}/build/{buildId}/…/start` végponton érhető el." | „A mock a `localhost:5175`-en, a dev backend a `https://login.dev.example.local` hoston fut." |
| „A PM és a public végpont **külön konfigurálható** (két külön base URL paraméter)." | „`PUBLIC_BASE_URL=http://localhost:5175`" — a konkrét érték, port, host. |
| „A frissített SPI-val a status endpoint `200`-at és `{\"status\":\"spi-ok\"}`-ot ad." | „`mvn clean package`, image push a registrybe, deployment-csere a `dsp01` namespace-ben." |
| „A hívás a felhasználó access tokenjével megy; S2S tokennel `403`." | „A teszt-user jelszava a `.env.dev`-ből olvasva; `oc login` szükséges." |

> **🔴 A legfontosabb elhatárolás: útvonal vs. koordináta.** Az **endpoint-útvonal szerződés** → spec (pl. `POST /rtm/.../start`, fejlécnevek, hibakódok, payload-mezők). A **host / base URL / port / namespace / image / parancs koordináta vagy eljárás** → plan (pl. `https://…`, `localhost:5175`, `dsp01`, `mvn clean package`). A koordináta a viselkedés változása nélkül is változik környezetenként — ezért nem a spec dolga. A spec-ben **szimbolikusan** hivatkozz rá (`{PUBLIC_BASE_URL}`), a konkrét értéket a plan tartalmazza.

Ha egy mondat technológiát, fájlnevet, függvényt vagy konkrét adatszerkezet-megvalósítást nevez meg → az plan-be való, **vedd ki a spec-ből**.

> **🔴 De ne dobd el (IP1).** Ha a kivett információ **értékes** — a felhasználó mondta, vagy a kódbázisból derült ki, és a következő fázisnak szükség lesz rá —, akkor a törlés helyett **írd át a `plan-input-from-prev.md`-be** (task-szintű részletet a `tasks-input-from-prev.md`-be). Csak azt töröld véglegesen, ami tényleg fölösleges vagy duplikátum. Lásd a „Fázisok közötti átadás" szekciót.

### Koordináta-kiszűrés — felismerés és ÁTHELYEZÉS (KX) — kötelező

A tapasztalat szerint a spec-be leggyakrabban **környezeti koordináták és eljárás-leírások** szivárognak be (dev hostok, localhost-portok, image-nevek, deploy-parancsok), mert „hasznos infónak" tűnnek. **Ezeket aktívan ki kell szűrni** — akkor is, ha **te** írtad az előző körben, és akkor is, ha egy korábbi futás hagyta bent (lásd a „Feladatod" szekció újrafutás-ágát).

**Menj végig a spec teljes szövegén** (minden szekción, a `Teszt specifikáció`-t és a `Célkitűzés`-t is beleértve), és jelöld meg az alábbiakat:

| Kiszűrendő (koordináta / eljárás → **plan**) | Marad (szerződés / viselkedés → **spec**) |
|---|---|
| abszolút URL hosttal (`https://valami.dev.…`, `http://localhost:5175`) | endpoint-**útvonal** (`/rtm/.../start`, `/init-hash`) |
| `host:port`, portszám, `localhost:NNNN` | HTTP metódus, státuszkód, errorCode |
| image-név és tag (`…/keycloak:v1`), registry, namespace, pod, deployment név | request/response **payload-mezők**, példa JSON |
| CLI-parancs végrehajtandó lépésként (`oc`, `kubectl`, `mvn`, `npm`, `docker`/`podman`, `curl`) | fejléc-**nevek** és kötelezőségük |
| forrás-/artefaktum-fájl útvonal (`…/pom.xml`, `…-SNAPSHOT.jar`, `build.sh`) | konfigurációs paraméter **neve** és szemantikája (`PUBLIC_BASE_URL` — mit szabályoz) |
| `.env*` fájlnév és a belőle olvasott **értékek** | realm/kliens/scope **azonosító**, ha a viselkedés (jogosultság) függ tőle |
| build/deploy/telepítési lépés-sorozat (runbook) | „mit kell igaznak lennie" jellegű elfogadási feltétel |

**A művelet mindig ÁTHELYEZÉS, nem törlés:**

1. Vedd fel a tételt a `plan-input-from-prev.md`-be új `- [ ] Inn` bejegyzésként, a **teljes, szó szerinti** infóval (URL, port, parancs, sorrend — ne rövidítsd le, mert a 03 ebből fog dolgozni) és a forrás megjelölésével: `_(forrás: 02-write-spec, kiszűrt koordináta)_`.
2. A spec-ben a helyére vagy **szimbolikus hivatkozás** kerül (`{PUBLIC_BASE_URL}/rtm/.../start`), vagy — ha a mondat tisztán eljárás volt — **kimarad**.
3. Ha egy **teljes alszekció** eljárás-leírás (pl. „Dev Keycloak deployment és SPI frissítés": image build → registry push → deployment csere), akkor az **egész blokkot** vidd át egy tételként. Ne próbáld a spec-ben „viselkedéssé" átfogalmazni — a spec-be legfeljebb az **eredmény** kerül elfogadási feltételként (pl. „a frissített SPI-val a status endpoint `spi-ok`-ot ad").
4. **Jelezd a felhasználónak**, mit helyeztél át — soronként vagy tételenként, egy tömör listában. Ez a spec tartalmának látható csökkentése, ezért nem történhet csendben.
5. Ha bizonytalan vagy, hogy egy tétel szerződés-e vagy koordináta, **ne dönts magadtól** — vedd fel kérdésként a `spec-questions.md`-be.

> **Miért nem hagyhatjuk a spec-ben „biztos, ami biztos" alapon?** Mert a `plan.md`-nek **önhordónak** kell lennie: a `test-runner` subagent kizárólag a `plan.md`-t olvassa, a spec-et nem. Egy spec-ben hagyott URL vagy parancs **soha nem fog lefutni** — csak azt a hamis benyomást adja, hogy dokumentálva van. Az áthelyezés tehát nem formalitás, hanem az, ami az infót egyáltalán végrehajthatóvá teszi.

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

_**Eset-orientált, nem eljárás-orientált.** Azt írod le, **minek kell igaznak lennie** („S2S tokennel hívva a start-process 403-at ad"), nem azt, **hogyan jutunk oda** („indítsuk a stacket, majd…"). A lépésenkénti folyamat-leírás a `plan.md` dolga._

_**Ide NEM kerül** (mind a `plan.md`-be való, a KX szabály szerint kiszűrendő):_
- _port, host, base URL, konkrét `localhost:NNNN` — csak szimbolikus hivatkozás (`{PUBLIC_BASE_URL}`);_
- _build-, deploy- vagy telepítési parancs és lépés-sorozat (image build, registry push, deployment csere, `oc`/`mvn`/`npm`) — **ez nem teszt, hanem runbook**;_
- _teszt-eszköz és keretrendszer neve, tesztfájl-útvonal (a `conventions.md` rögzíti, a `plan.md` hivatkozza);_
- _mock-szint és konténerizációs döntés („valódi stack vs. részleges mock", melyik service fut konténerben) — ez a `03` fázis kötelező első kérdése (`K01`), nem a spec dolga;_
- _teszt-környezeti credential és `.env` érték._

_A **teszt-szintek** (unit / integrációs / E2E) megnevezése rendben van, ha a viselkedés szintjét jelöli — de a szintek **infrastruktúrája** a plan-é._

_Ha létezik `specs/test-conventions.md`: a 2./3. szekció azon tételei, amelyeket ez a ciklus elfogadási feltételként vállal — **viselkedés-szinten**, a tétel ID-jára hivatkozva (pl. „I01 — a token-csere a `<scope>` scope-pal 200-at ad"). Parancs, tesztfájl-útvonal és eszköznév ide nem kerül (TC1). A ciklus által **érvénytelenített** baseline tételeket a szekció végén explicit írd ki._

## Kockázatok

_Mi sülhet el rosszul? Milyen feltételezéseken alapul a spec? Elfogadott POC korlátok, nyitott technikai kockázatok._

## Definition of done

_Ellenőrizhető, pipálható feltételek. Minden pont legyen konkrét és egyértelműen eldönthető (igen/nem)._
\`\`\`

---

## Kontextus betöltési szabályok

- Csak azt olvasd be, ami a spec megírásához feltétlenül szükséges.
- Ha egy bonyolult meglévő modult vagy logikát kell megértened, hívd a `researcher` subagentet (`agents/researcher.md`, Mód B) a kutatáshoz. A subagent csak az összefoglalót adja vissza — a nyers fájltartalom nem kerül be a fő kontextusba.
- Ha az előző ciklusok architektúrájára van szükség, kérdezz rá egy mondatban — ne olvasd be az összes korábbi spec-et.
- Ha konkrét meglévő kódot kell érteni, csak az érintett fájlt vagy részt olvasd be.

---

## Fázisok közötti átadás (`*-input-from-prev.md`) — IP1

**Amit BEOLVASSZ:** ha létezik a `specs/cycle-NN-<cycle-name>/spec-input-from-prev.md`, olvasd be a fázis elején (a spec írása előtt). Ez a 01-add-cycles fázisban elhangzott, de a roadmap-be nem illő viselkedési részleteket tartalmazza. Minden `[ ]` tételt vagy építs be a `spec.md` megfelelő szekciójába, vagy vess el explicit indokkal, és pipáld ki. **Guard:** ha a fájl nem létezik, ez nem hiba — folytasd.

**Amibe ÍRHATSZ:**
- **`plan-input-from-prev.md`** — a **03**-nak: minden technikai/implementációs részlet, amit a spec-ből kivettél vagy a kutatás során megtudtál (érintett komponens, meglévő megoldás, technológiai megkötés, teljesítmény-korlát).
- **`tasks-input-from-prev.md`** — a **04**-nek: konkrét előkészítő lépés vagy sorrend-megkötés, ami már most kiderült (pl. „a kulcsgenerálásnak meg kell előznie a konténer-buildet").

<!-- INCLUDE:shared/input-from-prev.md -->

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
- **A státusz már `Tervezésre kész`** — állj meg. Ne kezdj plan-t vagy task listát. Jelezd a felhasználónak a következő lépést és a fázis indító parancsát, például:
> *"A spec kész. Folytathatjuk a 3. lépéssel (plan). Az új fázis megkezdése előtt mindenképpen futtass egy `/clear` parancsot a kontextus kiürítéséhez, majd használd ezt a parancsot:
> ```
> /bs-write-plan input: @specs/cycle-NN-<cycle-name>/spec.md, ciklus: cycle-NN-<cycle-name>
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
- **DoD anti-minta: nincs „meta" pont?** — A *„X leírása elkészült"*, *„a teszt definiált"*, *„a menete dokumentált"* típusú pont **nem DoD**: egy doksi létét ellenőrzi, nem a rendszer működését. Minden DoD-pont **megfigyelhető viselkedésre** legyen igen/nem eldönthető. Rossz: *„a dev Keycloak SPI-frissítés menetének tesztje definiált."* Jó: *„a frissített SPI-val a status endpoint 200-at és `spi-ok` státuszt ad."*
- Az "Out of scope" szekció megakadályozza-e a scope creep-et?
- A "Hivatkozott fájlok" lista teljes, **és kizárólag dokumentációs anyagokat tartalmaz?** (OpenAPI leírók, README-k, sémák, meglévő spec fájlok, viselkedés-referencia szkriptek) — `.ts`, `.tsx`, `.js`, `.mjs`, `package.json` és egyéb forrásfájlok **nem szerepelhetnek**; ha szerepelnek, töröld őket. Forrásfájlok azonosítása a plan fázis feladata. **Szigorú szabály: a specifikáció szöveges részeiben sem szerepelhetnek (még a Kockázatok, az Out of scope vagy a Teszt specifikáció szekciókban sem) konkrét forrásfájlnevek — és ugyanez érvényes a build-/deploy-parancsokra (`mvn`, `oc`, `kubectl`, `docker`/`podman`, `npm run`), az image-nevekre és tagekre, a registry/namespace/pod/deployment nevekre, valamint a konkrét `host:port` és abszolút URL értékekre (KX). Ezeket nem törölni kell, hanem a `plan-input-from-prev.md`-be áthelyezni. A fájlok elérési útjai/linkjei mindig a fájl aktuális könyvtárához képest relatív útvonalak legyenek (a mappa mélységének megfelelő számú visszalépéssel a projekt gyökeréig, pl. `../../apps/legacy-login/README.md`), abszolút útvonalak vagy `file://` sémájú linkek nem szerepelhetnek bennük.**
- **Koordináta-kiszűrés (KX) lefutott?** — Végigmentél a spec teljes szövegén, és nincs benne környezeti koordináta (abszolút URL hosttal, `host:port`, image-név, namespace/pod/deployment, registry) vagy eljárás-leírás (build/deploy parancs, runbook, forrás-/artefaktum-fájl útvonal)? Ami volt, azt **áthelyezted** a `plan-input-from-prev.md`-be (nem törölted), teljes szöveggel, és **jelezted a felhasználónak**? A `Teszt specifikáció` szekciót külön is nézd át — ott szivárog be a leggyakrabban egy deployment-runbook „teszt" címszó alatt.

- **Minden hivatkozott érték, struktúra és adat specifikálva van?** — **Hatókör:** ez a szabály a **szerződés-adatokra** vonatkozik (payload-mezők, fejlécnevek, hibakódok, endpoint-útvonalak, konfigurációs paraméterek neve és szemantikája) — **nem** a környezeti koordinátákra. Egy hostra/portra/namespace-re **nem** az a helyes válasz, hogy „írjuk be a konkrét értéket", hanem hogy **szimbolikusan hivatkozunk rá, az értéket pedig a plan tartalmazza** (KX). Ha a spec szerződés-adatot említ vagy hivatkozik rá, teljesülnie kell:
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

- **A `spec-input-from-prev.md` minden tétele lezárva? (IP1)** — Ha a fájl létezik, nem maradhat benne `[ ]` tétel: mindegyik vagy beépült a `spec.md`-be (a megjegyzés mutatja, hova), vagy explicit indokkal elvetett. Csendben átlépni tilos.
- **A spec-ből kivett, de értékes infó át lett adva? (IP1)** — Ha technikai/implementációs részletet vettél ki a spec-ből, az a `plan-input-from-prev.md`-be került (nem a kukába)?

- **Visszatérő teszt-elvárások átvezetve? (TC1)** — Ha létezik `specs/test-conventions.md`, végigmentél a 2. és 3. szekción, és minden olyan tétel, amelyet ez a ciklus elfogadási feltételként vállal, megjelenik a `Teszt specifikáció`-ban (viselkedés-szinten, a tétel ID-jára hivatkozva)? Bekerült-e parancs, tesztfájl-útvonal vagy eszköznév a spec-be? Ha igen, **töröld** — az a `plan.md`-be tartozik. A ciklus által érvénytelenített baseline tételek explicit jelölve vannak a 08 számára?

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

A fix-mód egy **szűkített belépő:** a megadott `Must Fix` megállapításokat javítod célzottan, **nem írod újra az egész specet**. A `*-input-from-prev.md` fájlokat fix-módban **teljesen figyelmen kívül hagyod** (sem nem olvasod, sem nem írod) — IP1/6. (Ellenkező esetben egy olcsóbb LLM hajlamos elölről kezdeni a fázist — ez tilos.) A normál flow minőségi kapui (a fenti minőségellenőrzés) a javított részekre továbbra is érvényesek.

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