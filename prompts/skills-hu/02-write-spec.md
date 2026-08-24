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
  - "shared/artifact-voice.md"
  - "shared/phase-commit.md"
  - "shared/quality-check-spec.md"
  - "shared/fix-mode-spec.md"
---
# 02 — Spec írás
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

Spec driven development-ben fejlesztünk szoftvert. A fejlesztés ciklusokra van bontva. Minden ciklus egy önállóan lefejleszthető, önállóan tesztelhető részegysége a teljes implementációnak.

Ez a folyamat **2. fázisa (0–9)**: 0-init · 1-ciklusok · **2-spec ←** · 3-plan · 4-tasks · 5-analyze · 6-implement · 7-validate · 8-doc-sync · 9-review.

---

## Előfeltétel

0. **Ciklus-beazonosítás:** ha a felhasználó megadott ciklust/fájlt, azt használd; különben a legfrissebb `specs/cycle-*` mappát ajánld fel megerősítésre — <!-- INCLUDE:lang/common.md#ciklus-beazonositas --> — és várj a válaszra, mielőtt továbblépsz.

1. **`conventions.md` létezés-ellenőrzés:** olvasd be a projekt gyökerében a `conventions.md`-t. Ha nem létezik, STOP — térjenek vissza a `00` fázishoz.

1.a **Munkafa-ellenőrzés (csak VCS esetén):** futtasd `git status --short`. Ha van commitálatlan változtatás, listázd, és kérdezd meg egy körben, hogy commitáljam-e most vagy folytassam — várj a válaszra. (No-VCS projektben — a `conventions.md` szerint nincs verziókezelő — ez és a lenti branch-lépés kimarad.)

2. **Roadmap ellenőrzés:** Olvasd be a `specs/roadmap.md`-t. **Ha a státusz nem `Kész`, ne kezdj el spec-et írni.** Jelezd a felhasználónak, hogy a roadmap még nem zárult le, és térjenek vissza a `01` ciklusok kezelése fázishoz. Ha a státusz `Kész`, keresd meg a megadott ciklus (`cycle-NN-<cycle-name>`) bejegyzését a roadmap-ben, és használd azt a spec kiindulópontjaként — a viselkedés, az érintett komponensek, az előfeltételek és a teszt kritérium mind alapot adnak a spec részletes kidolgozásához.

1.b **Visszatérő teszt-elvárások beolvasása (TC1):** ha létezik a `specs/test-conventions.md`, olvasd be — ez a projekt visszatérő teszt-elvárásainak és a hozzájuk tartozó recepteknek az élő regisztere, amit a `08-doc-sync` tart karban. **Guard:** ha a fájl még nem létezik (korai ciklus — még nincs promótálható tétel), **ne állj meg és ne hozd létre** — egy mondatban jelezd, és folytasd. A fájl használata:
   - a **2. és 3. szekció** tételeiből azt emeld be a `Teszt specifikáció` szekcióba (és — ha valódi elfogadási feltétel — a `Definition of done`-ba), amit **ez a ciklus tényleges elfogadási feltételként vállal**, **viselkedés-szinten**: mit kell ellenőrizni, milyen bemenetre mi a helyes kimenet. **Parancs, tesztfájl-útvonal, eszköznév és build/deploy lépés ide NEM kerül** — az a `plan.md` dolga (a spec/plan határvonal szerint);
   - a puszta „ne törjön el" jellegű regressziós tételeket **ne** emeld a spec-be — azok a `plan.md` `Regressziós érintettség` táblájába tartoznak, mert nem a ciklus célja;
   - a **0. blokkot** (koordináták: környezetek, URL-ek, teszt-userek, paraméterek) és az **1. szekciót** (receptek, parancsok) csak **kontextusként** olvasod: ebből látod, milyen környezeti korlátok között mozog a ciklus. A spec-be nem kerülnek át.
   - **Érvénytelenítés jelzése (a 08 bemenete):** ha a ciklus egy meglévő baseline-tételt **érvénytelenít** (megszünteti vagy átalakítja a komponenst, amire hivatkozik), írd ki explicit a `Teszt specifikáció` szekció végén: *„Érvénytelenített baseline tétel: `<ID>` — <miért>."* Ebből tudja a `08-doc-sync` (TC4), hogy a tételt törölni kell a regiszterből. **Magad ne írd a `test-conventions.md`-t** — annak a doc-sync a kizárólagos gazdája.

1.c **Current-truth kiindulás (DS5):** ha létezik a `docs-generated/system-overview.md`, olvasd be — ez a megvalósult (as-built) rendszer konszolidált, naprakész működésleírása, amit a `08-doc-sync` fázis tart karban. A spec a **jelenlegi valóságból** induljon: nézd meg, milyen flow-k/állapot/endpointok léteznek már, hogy az új spec ezekre épüljön, ne ütközzön velük. **Guard:** ha a fájl még nem létezik (korai ciklus / a bootstrap előtt), **ne állj meg** — jelezd egy mondatban, hogy a current-truth doksi még nincs, és folytasd a spec írását a roadmap alapján.

1.d **Ciklus design input beolvasása (CD1):** ha létezik a `specs/cycle-NN-<cycle-name>/cycle-design-input.md`, olvasd be — ezt **a felhasználó** írta, szabad formában, a saját szavaival a ciklusról (a 01 fázis csak az üres sablont hozta létre). A feldolgozás szabályait lásd a lenti *„Ciklus design input feldolgozása (CD1)"* szekcióban. **Guard:** ha a fájl nem létezik, vagy csak a sablon-szöveget tartalmazza (nincs érdemi felhasználói tartalom), **ne állj meg és ne kérdezz rá** — egy mondatban jelezd (*„A `cycle-design-input.md` üres, a roadmap-bejegyzés alapján dolgozom."*), és folytasd.

2. **Branch-ellenőrzés (a branch a 01-ben jött létre — BD1):** a ciklus feature branch-ét már a **01-add-cycles** fázis létrehozta `main`-ről; a 02 **nem** nyit új branch-et. Verziókezelő mellett:
   - `git branch --show-current` → ha már a ciklus feature branch-én vagy, folytasd itt.
   - Ha egy másik branch-en vagy, de a ciklusé létezik → válts rá: `git switch feature/cycle-<cycle-name>` (a `conventions.md` `## Git és branching konvenciók` **Branch-elnevezési stratégia** szerinti névvel).
   - **Fallback** (ha a ciklus branch-e valamiért nem létezik — pl. régi flow vagy megszakadt 01): a branch-nyitó preflight (friss, tiszta `main`) után hozd létre: `git switch -c feature/cycle-<cycle-name>`. Ez kivétel, nem a főszabály — normál esetben a 01 már létrehozta.
   - **No-VCS ágon** (a `conventions.md` szerint nincs verziókezelő) ez a lépés kimarad.

   A spec, plan, tasks fájlok és a schema artifaktumok mind erre a branch-re kerülnek.

---

## Feladatod

**Ha már létezik `spec.md` a `specs/cycle-NN-<cycle-name>/` mappában:** olvasd be a `spec.md`-t és a `spec-questions.md`-t (ha létezik). **Nézd meg a `cycle-design-input.md`-t is** — a felhasználó az előző kör óta írhatott bele vagy bővíthette; a benne lévő, a spec-ben még nem tükröződő tételeket a CD1 szabályai szerint dolgozd fel. **Futtasd le a koordináta-kiszűrést (KX)** a meglévő szövegen — egy korábbi futás (vagy egy másik ágens) hagyhatott bent környezeti koordinátát vagy deploy-eljárást; ezeket most helyezd át a `plan-input-from-prev.md`-be. Utána futtasd le a minőségellenőrzést. Ha hiányosságot vagy problémát találsz, vedd fel kérdésként a `spec-questions.md`-be, és állítsd vissza a `spec.md` státuszát a valódi állapotnak megfelelően (`Nyitott kérdések vannak` vagy `Piszkozat`). Utána az iterációs szabályok szerint folytatd.

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

> **🔴 A KX koordinátát cserél, nem tartalmat tömörít (KX2).** A kiszűrés hatóköre **kizárólag a konkrét technikai koordináta és az eljárás-lépés** — a **logikai forgatókönyv és az ellenőrzések részletessége** megmarad. Egy `localhost:5175` → `{PUBLIC_BASE_URL}` csere **nem** jogosít fel arra, hogy a hozzá tartozó 8 lépéses folyamatot két mondatba sűrítsd. Ha a bemenet (a felhasználó design inputja, a roadmap, a `spec-input-from-prev.md`, egy meglévő teszt) **részletes**, a spec is **részletes marad** — csak koordináta-mentes. **A részletvesztés éppolyan hiba, mint a benne felejtett host.**
>
> **Amin viszont szabadon változtathatsz — sőt, kell (KX2/b):** a **stílus és a megfogalmazás** (a felhasználó nyelvéből artefaktum-hangú, eldönthető követelmény lesz — AV1); a **pontatlanság** javítása (kétértelmű megfogalmazás élesítése, hibás vagy inkonzisztens elnevezés egységesítése); a **hiányos lépés kifejtése** (ha a bemenet átugrik egy szükséges köztes ellenőrzést vagy nem mondja meg az elvárt eredményt, egészítsd ki — ha nem tudod, mi a helyes, tedd `spec-questions.md` kérdéssé); a **nem logikus sorrend** átrendezése (ha egy lépés olyan állapotot feltételez, amit egy későbbi hoz létre). **Az irány tehát bővítés és pontosítás lehet, összevonás és elhagyás nem.** Ha a részletességen érdemben változtatsz (átrendezés, lépés-beszúrás), **jelezd egy sorban a felhasználónak**, mit és miért.

**A művelet mindig ÁTHELYEZÉS, nem törlés:**

1. Vedd fel a tételt a `plan-input-from-prev.md`-be új `- [ ] Inn` bejegyzésként, a **teljes, szó szerinti** infóval (URL, port, parancs, sorrend — ne rövidítsd le, mert a 03 ebből fog dolgozni) és a forrás megjelölésével: `_(forrás: 02-write-spec, kiszűrt koordináta)_`.
2. A spec-ben a helyére vagy **szimbolikus hivatkozás** kerül (`{PUBLIC_BASE_URL}/rtm/.../start`), vagy — ha a mondat tisztán eljárás volt — **kimarad**.
3. Ha egy **teljes alszekció** eljárás-leírás (pl. „Dev Keycloak deployment és SPI frissítés": image build → registry push → deployment csere), akkor az **egész blokkot** vidd át egy tételként. Ne próbáld a spec-ben „viselkedéssé" átfogalmazni — a spec-be legfeljebb az **eredmény** kerül elfogadási feltételként (pl. „a frissített SPI-val a status endpoint `spi-ok`-ot ad").
4. **Jelezd a felhasználónak**, mit helyeztél át — soronként vagy tételenként, egy tömör listában. Ez a spec tartalmának látható csökkentése, ezért nem történhet csendben.
5. Ha bizonytalan vagy, hogy egy tétel szerződés-e vagy koordináta, **ne dönts magadtól** — vedd fel kérdésként a `spec-questions.md`-be.

> **Miért nem hagyhatjuk a spec-ben „biztos, ami biztos" alapon?** Mert a `plan.md`-nek **önhordónak** kell lennie: a `test-runner` subagent kizárólag a `plan.md`-t olvassa, a spec-et nem. Egy spec-ben hagyott URL vagy parancs **soha nem fog lefutni** — csak azt a hamis benyomást adja, hogy dokumentálva van. Az áthelyezés tehát nem formalitás, hanem az, ami az infót egyáltalán végrehajthatóvá teszi.

---

## Ciklus design input feldolgozása (CD1)

A `specs/cycle-NN-<cycle-name>/cycle-design-input.md` a **felhasználó saját, szabad formájú ciklus-specifikációja**: elvárások, viselkedés-vázlat, példa kérés/válasz, folyamatleírás, korlátok, jegyzetek. A 01 fázis üres sablonként hozza létre; a kitöltése **opcionális**.

**Ha van benne érdemi tartalom, kötelezően fel kell dolgoznod** — ez a `roadmap.md` bejegyzése *mellett* a spec elsődleges bemenete, és rendszerint részletesebb annál. Ütközés esetén (a design input mást mond, mint a roadmap-bejegyzés) **ne dönts magadtól**: vedd fel kérdésként a `spec-questions.md`-be.

**Szabályok:**

1. **Ne írd át és ne pipáld ki a fájlt.** Ez a felhasználó dokumentuma, nem átadó-fájl (`*-input-from-prev.md`) — nincsenek benne `[ ]` tételek, amiket lezárnál. Olvasd, dolgozd fel, hagyd érintetlenül.
2. **Minden érdemi tétel sorsa legyen követhető.** Amit a design input tartalmaz, annak vagy (a) meg kell jelennie a `spec.md` megfelelő szekciójában, vagy (b) át kell kerülnie a `plan-input-from-prev.md` / `tasks-input-from-prev.md`-be (ha implementációs vagy task-szintű részlet), vagy (c) explicit az `Out of scope` szekcióba kell kerülnie, vagy (d) `spec-questions.md` kérdéssé kell válnia. **Csendben elejteni tilos.**
3. **A KX szabály erre is érvényes.** A design input jellemzően tele van környezeti koordinátával és eljárással (hostok, portok, parancsok) — ezeket **ne másold a spec-be**: a *„Koordináta-kiszűrés (KX)"* szekció szerint a `plan-input-from-prev.md`-be helyezd át, teljes, szó szerinti tartalommal, `_(forrás: cycle-design-input.md)_` megjelöléssel.
3.a **De a részletességet őrizd meg (KX2).** A design input a felhasználó **legrészletesebb** bemenete — jellemzően ő írja le a legaprólékosabban a teszt-forgatókönyvet és a folyamat lépéseit. A koordináta-csere **nem** ad felhatalmazást a tartalom tömörítésére: ha a design input egy 10 lépéses ellenőrzési szekvenciát ír le, a `spec.md` `Teszt specifikáció` szekciójában **legalább 10 lépés** marad, szimbolikus koordinátákkal. **A felhasználó által részletesen leírt esetet soha ne foglald össze** — a részletvesztés a leggyakoribb és a legdrágább hiba ebben a fázisban, mert a 03/04/06/07 már csak azt látja, ami itt megmaradt. A stílust, a pontatlanságot, a hiányzó lépéseket és a nem logikus sorrendet **javíthatod és bővítheted** (KX2/b) — a design input nyers vázlat, nem szentírás; csak a tartalom-vesztés tilos.
4. **A hangnem nem öröklődik (AV1).** A design input a felhasználó nyelvén íródott („szeretném, ha…", „csináljuk úgy, hogy…"); a `spec.md`-be ebből **artefaktum-hangú, eldönthető követelmény** lesz.
5. **A hiányosság nem hiba.** A design input nem teljes spec — a benne nem érintett területeket a szokásos ambiguitás-vizsgálat és kérdés-flow szerint járd körbe.
6. **Jelezd a felhasználónak**, hogy feldolgoztad: egy tömör listában, hogy mely tételek hova kerültek (spec szekció / plan-input / out of scope / új `Knn` kérdés).

> **A 03 is beolvassa.** A `cycle-design-input.md`-t a `03-write-plan` szintén automatikusan feldolgozza (a technikai/eljárás-jellegű tartalmát). Ez **nem mentesít** a 3. pont alól: a KX-szel kiszűrt koordinátákat továbbra is helyezd át a `plan-input-from-prev.md`-be, `_(forrás: cycle-design-input.md)_` megjelöléssel — így a 03 egy helyen, lezárandó tételként is látja őket, nem csak a felhasználó nyers szövegében.

**Fix-módban** (05-analyze hurok) a `cycle-design-input.md`-t **csak akkor** olvasod be, ha egy konkrét `Must Fix` a design inputtal való ütközésre hivatkozik — egyébként ne, hogy a hurok ne kezdje elölről a fázist.

---

<!-- INCLUDE:shared/artifact-voice.md -->

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

_**Eset-orientált, nem eljárás-orientált.** Azt írod le, **minek kell igaznak lennie** („S2S tokennel hívva a start-process 403-at ad"), nem azt, **hogyan jutunk oda** („indítsuk a stacket, majd…"). A **környezet-előkészítő** lépés-sorozat (stack indítása, build, deploy, telepítés) a `plan.md` dolga._

_**🔴 Ne zanzásítsd a teszteseteket (KX2).** Ha a bemenet — a felhasználó `cycle-design-input.md`-je, a `spec-input-from-prev.md`, a roadmap vagy egy meglévő teszt — **részletes teszt-forgatókönyvet** ad (többlépéses ellenőrzési szekvencia, elágazások, közbenső állapotok, konkrét bemenet→elvárt kimenet párok), azt **teljes részletességgel őrizd meg**: minden lépés, a köztes ellenőrzések és az elvárt eredmények maradjanak meg. Kizárólag a **koordinátákat** cseréld szimbolikus hivatkozásra (`{PUBLIC_BASE_URL}`, `{MEDIA_BASE_URL}`, `{TEST_USER}`) — a **logikai tartalmat ne egyszerűsítsd le**, ne vond össze a lépéseket, és ne cseréld „a folyamat végigfut" típusú összefoglalóra._

_**Formázási tipp, ami a 03-at védi:** a kidolgozott artefaktumot (OpenAPI-részlet, teljes JSON payload, DDL, `curl`) tedd **kódblokkba** a megfelelő nyelv-jelöléssel (```yaml`, ```json`, ```sql`). A `05-analyze` mechanikus kapuja így **gépiesen ellenőrzi** (`V1` check), hogy a 03 szó szerint át is vette-e — csonkítás esetén `Must Fix` lesz belőle, nem kell észrevenni._

_**Amit viszont szabad — és kell (KX2/b):** átfogalmazni a felhasználó szövegét artefaktum-hangúra; pontatlanságot, kétértelműséget, inkonzisztens elnevezést javítani; **hiányos lépést kifejteni** (hiányzó köztes ellenőrzés, meg nem adott elvárt eredmény pótlása — ha nem tudod, mi a helyes, `spec-questions.md` kérdés lesz belőle); **nem logikus sorrendet átrendezni** (ha egy lépés később előálló állapotra épül). Az irány **bővítés és pontosítás** — összevonás és elhagyás nem. A nem triviális átrendezést/beszúrást jelezd a felhasználónak._

_**Az eset-orientáltság nem rövidséget jelent.** Egy viselkedési szekvencia (①…②…③, mindegyik saját elvárt eredménnyel) **eset-orientált marad** akkor is, ha tíz lépés hosszú — mert azt írja le, minek kell igaznak lennie, nem azt, hogyan állítjuk elő a környezetet. Az „eljárás-orientált" tiltás a **runbookra** vonatkozik (image build, `oc`/`mvn`, deployment-csere), nem a **viselkedés-szekvenciára**. Kétség esetén: **inkább maradjon a részlet** — a részletvesztés a `06`/`07` fázisban derül ki, amikor már senki nem tudja, mit kellett volna ellenőrizni._

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

- [ ] **DoD-01** — [az ellenőrizhető feltétel]
      · _bizonyíték:_ `[tesztnév | cmd: <parancs> | manual: <mit ellenőrzünk kézzel>]`
- [ ] **DoD-02** — [az ellenőrizhető feltétel]
      · _bizonyíték:_ `[…]`
\`\`\`

> **A bizonyíték-mező (DI2) — erősen ajánlott.** Minden DoD-ponthoz nevezd meg, **mi bizonyítja** a teljesülését: egy **tesztnév** (a `plan.md` teszt-specifikációjából), egy **`cmd:` parancs**, vagy — ha tényleg csak kézzel ellenőrizhető — `manual: <mit>`. A `07-validate` a `dod-check.py`-jal **gépi join**-nal értékeli ki ezeket a kör futási eredményeivel: bizonyítékkal bíró pontnál nincs szükség LLM-ítéletre, és nem fordulhat elő emlékezetből adott ✓. Bizonyíték nélküli pont nem hiba, de a 07 `?`-lel jelöli, és kézi ítéletet kér rá — ha sok ilyen van, az a spec ellenőrizhetőségének gyengeségét jelzi. *(A bizonyíték itt **viselkedés-szintű megnevezés**, nem tesztfájl-útvonal vagy futtatási parancs-részlet — a spec/plan határvonal érvényes marad; a `cmd:` alak is csak akkor indokolt, ha nincs hozzá teszteset.)*

> **A `DoD-NN` azonosító kötelező és stabil (DI1).** Minden DoD-pont saját, sorfolytonos azonosítót kap (`DoD-01`, `DoD-02`, …), és ez az azonosító **soha nem változik meg** a ciklus során — a `07-validate` ezzel a névvel naplózza a bukott DoD-pontokat a `# Validation History`-ba, és ezen a néven számolja a 3-próba leállást. Ha egy pont utólag beszúrásra kerül, a következő szabad számot kapja (ne számozd újra a listát); ha egy pont törlődik, a száma nem használható újra. Parafrazeált vagy azonosító nélküli DoD-pontnál a hurok leállító-mechanizmusa csendben elromlik.

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
<!-- INCLUDE:lang/02-write-spec.md#spec-questions-struktura -->
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
5. Ha minden kérdés lezárt, futtasd le a minőségellenőrzést. Ha átment, **tedd fel a kérdést a felhasználónak**: <!-- INCLUDE:lang/02-write-spec.md#statusz-megerosites --> — Ne állítsd át a státuszt a megerősítés előtt. **A válasz végén helyezd el a `spec.md` közvetlen, kattintható linkjét.**
6. Ha a felhasználó explicit megerősíti (pl. "igen", "kész", "mehet"), állítsd a `spec.md` státuszát `Tervezésre kész`-re, **és azonnal commitolj** — lásd a lenti *Fázis-záró commit* szekciót (`<FÁZIS-TAG>` = `02-spec`). Megerősítés → státuszírás → commit: ez egyetlen lépéssor.

Minden iteráció indítható új kontextussal: elég a `spec.md` és a `spec-questions.md` aktuális állapota + ez a prompt. Újraindításkor olvasd be a `spec-questions.md`-t, és folytasd az első `[ ]` státuszú kérdéstől.

---

## Megállási szabályok

Ha az alábbiak bármelyike teljesül, **STOP — állj meg és ne lépj tovább**:

- **Van `[ ]` státuszú kérdés a `spec-questions.md`-ben** — tegyél fel egyet a felhasználónak, várj a válaszra, majd folytasd. Ne tegyél fel több kérdést egyszerre.
- **A minőségellenőrzés hibát talált** — javítsd a hibát, majd futtasd újra. Ne állítsd `Tervezésre kész`-re a státuszt, amíg nem ment át.
- **A felhasználó megerősítése hiányzik** — a státusz `Tervezésre kész`-re csak explicit megerősítés után állítható. Ne állítsd át kérdezés nélkül.
- **A spec plan-tartalmú elemet tartalmaz** (pl. technológiaválasztás, implementációs részlet, konkrét fájlterv) — töröld, nem spec-be való.
- **A státusz `Tervezésre kész`, de a fázis-záró commit hiányzik** (VCS-es projekt, `git log -1 --oneline` nem a `cycle-NN: 02-spec` commitot mutatja) — először commitolj a *Fázis-záró commit* szerint, csak utána zárd le a fázist.
- **A státusz már `Tervezésre kész`** (és a commit megvan) — állj meg. Ne kezdj plan-t vagy task listát. Jelezd a felhasználónak a következő lépést és a fázis indító parancsát, például:
<!-- INCLUDE:lang/02-write-spec.md#zaro-uzenet -->
> **A válasz végén helyezd el a `spec.md` közvetlen, kattintható linkjét.**


---

## Státusz kezelés

| Állapot | Feltétel |
|---|---|
| `Piszkozat` | Spec indításakor |
| `Nyitott kérdések vannak` | Van legalább egy `[ ]` kérdés a `spec-questions.md`-ben |
| `Tervezésre kész` | Minden kérdés `[x]` + minőségellenőrzés átment + **felhasználó explicit megerősítette** |

A `Tervezésre kész`-re váltás után **kötelező** git commit (`cycle-NN: 02-spec`) — az eljárást lásd a *Fázis-záró commit* szekcióban. Ne állítsd át a státuszt megerősítés nélkül.

<!-- INCLUDE:shared/phase-commit.md -->

A fenti blokkban a `<FÁZIS-TAG>` értéke ebben a fázisban: **`02-spec`**, a záró státusz: **`Tervezésre kész`**.

> **Kész lifecycle:** a `spec.md` a `Tervezésre kész` után a ciklus végén — amikor a validate (07) PASS lezárja a ciklust — `Kész` státuszra lép. A 08 fázis már `Kész`-t vár. Ezt az átmenetet a 07 végzi, itt nem.

---

<!-- INCLUDE:shared/quality-check-spec.md -->

---

<!-- INCLUDE:shared/fix-mode-spec.md -->
