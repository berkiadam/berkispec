---
phase: 03
name: bs-write-plan
description: "berkispec - 03. Használd, ha a ciklus spec.md-je 'Tervezésre kész' (Phase 03), a részletes technikai megvalósítási terv kidolgozásához (kódbázis-elemzés, szükség esetén researcher subagent). Létrehozza a 'plan.md'-t ('Task írásra kész') + a 'plan-questions.md'-t."
prerequisites:
  - "specs/cycle-NN-<name>/spec.md státusz: <status:ready_for_plan>"
output:
  - "specs/cycle-NN-<name>/plan.md státusz: <status:ready_for_tasks>"
  - "specs/cycle-NN-<name>/plan-questions.md"
  - "specs/cycle-NN-<name>/tasks-input-from-prev.md és/vagy validate-input-from-prev.md (csak ha van átadandó infó, IP1)"
prev: bs-write-spec
next: bs-write-tasks
subagents:
  - "agents/researcher.md"
scripts:
  - "scripts/analyze-gate-check.py"
shared:
  - "shared/input-from-prev.md"
  - "shared/artifact-voice.md"
  - "shared/phase-commit.md"
  - "shared/quality-check-plan.md"
  - "shared/fix-mode-plan.md"
---
# 03 — Plan írás
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

Spec driven development-ben fejlesztünk szoftvert. A fejlesztés ciklusokra van bontva. Minden ciklus egy önállóan lefejleszthető, önállóan tesztelhető részegysége a teljes implementációnak.

Ez a folyamat **3. fázisa (0–9)**: 0-init · 1-ciklusok · 2-spec · **3-plan ←** · 4-tasks · 5-analyze · 6-implement · 7-validate · 8-doc-sync · 9-review.

---

## Cheat sheet

| Szekció | Egy mondatban |
|---|---|
| Előfeltétel | `spec.md` = `<status:ready_for_plan>`, `conventions.md` létezik, tiszta munkafa. |
| Nyitott kérdések | Minden kérdés a `plan-questions.md`-be; **kötelező első kérdés: E2E teszt stratégia**. |
| Kontextus | Spec + dokumentáció; forrásfájlokat a `researcher` subagent azonosítja (D2=A). |
| Plan struktúra | <sec:planned_changes>, tesztstratégia, végrehajtási sorrend, ellenőrzési stratégia. |
| Teszt eszköz | A `conventions.md`-re hivatkozz, ne ismételd a konkrét tool-nevet. |
| Teszt-receptek | A `specs/test-conventions.md`-ből **maradéktalanul, önhordóan** átemelve (TC1/a) — hivatkozás nem elég, a receptet **fizikailag be kell másolni**. |
| Szekció-ID | Minden végrehajtható terv-szekció címében stabil `[P-…]` azonosító (PID1) — a `tasks.md` erre hivatkozik, nem sorszámra. Kiadott ID soha nem változik. |
| Scope-kapu | Minden plan-képességhez spec-forrás (követelmény/`DoD-NN`) — `<sec:reverse_coverage>` tábla (SC1), az első oszlopban a szekció `[P-…]` azonosítójával; ami nincs, az vissza a 02-be vagy `<sec:out_of_scope>`. |
| Környezet-felkészítés | A teszt előfeltételei (token-beszerzés, stack-indítás + health check, egyedi komponens build/deploy/rollback, seed) **szó szerinti parancsként** a plan-ben (TP3); ami korábbi ciklusban épült ki és nincs a regiszterben, azt onnan hozod át (TP3/a). |
| Spec-tesztek átemelése | A spec **minden** tesztesete és `DoD-NN` pontja leképződik plan-tesztesetre (TP1), a kötelező `<sec:spec_coverage>` táblával — a részlet nem halasztható a 04-re vagy az implementációra. |
| Fázis-átadás | `plan-input-from-prev.md` beolvasva és lezárva; a nem ide tartozó infó a `tasks-`/`validate-input-from-prev.md`-be (IP1). |
| Design input | `cycle-design-input.md` (a felhasználó saját ciklus-leírása) **automatikusan beolvasva** — a technikai/eljárás-jellegű tartalma a planbe kerül; a fájlt nem írod át (CD1). |
| <sec:environment_coords> | Kötelező `<sec:environment_coords>` (KO1) szekció: komponens-URL-ek/portok, indító parancsok, példa REST hívások, teszt-/API-userek jelszóval, minden paraméter — konkrét értékkel, placeholder és üres cella nélkül. |
| **Önhordóság** | A `plan.md` **mindent** tartalmaz, ami a fejlesztéshez/teszteléshez kell — a 04 és a `test-runner` **csak ezt** olvassa, a spec-et nem. |
| Kapu-konfiguráció | Ha a ciklus olyat változtat, amit egy determinisztikus kapu a `conventions.md`-ből olvas (riport-artefaktumok/útvonal-alap, Sonar, teszt-parancsok, portok, merge-stratégia), a `conventions.md` frissítése **a ciklus része**: tervezd meg, és legyen rá task (GC1). |
| Útvonalak | Kód- és fájl-hivatkozás **a repó gyökeréhez képest relatív** (`src/app.ts:42`), dokumentum-link a fájl saját könyvtárához képest (`./spec.md`); abszolút útvonal és `file://` tilos (RP1). |
| Csonkítás-mentesség | A spec **kidolgozott** artefaktumai (OpenAPI, teljes payload, hibamátrix, többlépéses teszt-forgatókönyv) **szó szerint, hiánytalanul** kerülnek át (KX3) — az irány bővítés és pontosítás, nem összevonás. |
| Hivatkozás-feloldás | Scriptre/tesztre/API-ra hivatkozó bemenetet **fel kell oldani**: a konkrét parancs, URL, payload a plan-be kerül, nem az utalás. |
| Teszt-lépések | Minden integrációs/E2E teszt **lépésről lépésre** kifejtve (ige, végpont, fejléc, body, elvárt válasz) — „a cycle-XX mintájára" tilos. |
| Validációs ciklusok | Minden nagy szekció után célzott ellenőrzés, mielőtt továbblépsz. |
| Spec kritika | Aktív checklist minden komponensre; **hiányosság** → vissza a 02 fázisba, **túlnyúlás** (koordináta a spec-ben) → átemelve a planbe (KX tükre). |
| Lezárás | Minőségellenőrzés + **Lezárási kapu (TP2, kipipálva kiírva)** + Constitution Check (SK4) + **mechanikus kapu** (`analyze-gate-check.py --plan-only`, M) + user megerősítés → `<status:ready_for_tasks>`, commit. |

---

## Feladatod

**Ha már létezik `plan.md` a `specs/cycle-NN-<cycle-name>/` mappában:** olvasd be, és futtasd le rajta a minőségellenőrzést (ld. lent). Ha hiányosságot vagy problémát találsz — spec-eltérés, hiányzó komponens terv, hiányos teszt specifikáció, stb. — állítsd vissza a státuszt `<status:draft>`-ra, jelezd pontosan mi a probléma, és javítsd az iterációs szabályok szerint.

**Ha még nem létezik `plan.md`:** hozd létre a `specs/cycle-NN-<cycle-name>/` mappában az alábbi struktúra szerint.

**Ne ismételd meg a spec tartalmát.** A plan célja a technikai megvalósítás megtervezése — hivatkozz a spec-re, ne másold át.

> **🔴 Hatókör — ne általánosítsd túl!** Ez a szabály (és a párja: „a `conventions.md`-re hivatkozz, ne ismételd a tool-nevet") **kizárólag az indoklásra és a viselkedés-leírásra** vonatkozik: a *miért*-re, az üzleti kontextusra, az elfogadási feltételekre. **Soha nem vonatkozik a végrehajtáshoz szükséges adatra.** A vezérelv egy mondatban:
>
> **A DÖNTÉSRE hivatkozz — a VÉGREHAJTÁST írd ki.**
>
> Példa: hogy a projekt melyik teszt-keretrendszert használja, az **döntés** → a `conventions.md`-re hivatkozol, nem ismételed. De hogy **ebben a ciklusban milyen paranccsal, milyen fájlra, milyen környezetben** fut a teszt, az **végrehajtás** → konkrétan a plan-be írod. Ha bizonytalan vagy, melyik oldalra esik valami, tedd fel a kérdést: *„a downstream fázis (04/06/07) ezt az információt máshonnan meg tudja szerezni?"* Ha nem — akkor a plan-be kell.

### 🔴 A `plan.md` ÖNHORDÓ — ez a fázis legfontosabb szabálya

**A plan az utolsó dokumentum, amely még látja a spec-et.** Ami innentől lefelé történik, az **kizárólag a plan-ből** dolgozik:

| Fogyasztó | Mit olvas | Mit NEM lát |
|---|---|---|
| `04-write-tasks` | **csak a `plan.md`-t** (a skill explicit tiltja a spec és a forrásfájlok újraolvasását) | spec, kódbázis |
| `06-implement` | a `plan.md`-t + a `tasks.md`-t; a taskokból ide navigál vissza | spec |
| `test-runner` (07/09) | a `plan.md` `<sec:testing_strategy>` és `<sec:regression_impact>` szekcióit | spec, `test-conventions.md` |

Ebből következik a szabály, amit **nem lehet felülbírálni**: **minden információnak, ami a fejlesztéshez, a teszteléshez vagy az ellenőrzéshez kell, fizikailag a `plan.md`-ben kell lennie.** Nem hagyható ki semmi lényeges arra hivatkozva, hogy „a spec-ben úgyis benne van", „a kódban látszik", „a `build.sh` tartalmazza" vagy „a beszélgetésben elhangzott". Ami nincs a plan-ben, az **nem létezik** a downstream fázisok számára — és nem fog lefutni, csak a dokumentáltság hamis benyomását adja.

**Konkrétan a plan-ben kell lennie** (ami az adott ciklusra értelmezhető):

- érintett fájlok teljes útvonala; létrehozandó/módosítandó függvény-, osztály-, modulnevek;
- **függvényszignatúrák, interfészek, típusok**, az interfész-változás pontos alakja;
- adatszerkezetek és **payloadok konkrét mezőkkel** (példa request/response, nem csak mezőnevek felsorolása);
- hibaágak: feltétel → HTTP státusz + errorCode + response body;
- konfiguráció: env-változó **neve ÉS értéke**, hol állítódik be;
- külső integráció koordinátái: URL, port, realm/kliens/scope, teszt-user, példa `curl` hívás;
- futtatható **parancsok szó szerint** (build, deploy, indítás, teszt-futtatás, ellenőrzés);
- végrehajtási sorrend és előfeltételek; migrációs és rollback forgatókönyv, ha van sémaváltozás.

> **Önteszt (alkalmazd a lezárás előtt):** *„Ha valaki csak a `plan.md`-t és a `tasks.md`-t kapja meg — a spec, a kódbázis ismerete és ez a beszélgetés nélkül —, le tudja fejleszteni és le tudja tesztelni a ciklust?"* Ha bármelyik ponton **vissza kellene kérdeznie vagy találgatnia**, a plan hiányos. Nem az a kérdés, hogy te érted-e; az, hogy egy nálad kevesebbet tudó olvasó végre tudja-e hajtani.

**Tilos megfogalmazások a plan-ben:** „lásd a spec-et", „a szokásos módon", „a megfelelő végpontra", „futtasd a `build.sh`-t", „a korábbi ciklusban használt paraméterekkel", **„a cycle-XX mintájára" / „mint a meglévő tesztfájlban" / „a spec szekvenciadiagramja szerint"**, `<ide jön …>`, `TODO`. Mindegyik azt jelenti, hogy a konkrétum **hiányzik** — pótold, vagy ha nem tudod, vedd fel kérdésként a `plan-questions.md`-be.

**Ne készíts task listát vagy implementációt.** Ez a következő lépés feladata.

**Ne tervezz olyat, ami nincs a spec-ben.** A plan scope-ja pontosan a spec scope-ja — nem bővíti, nem szűkíti. Ha a plan írása közben úgy érzed, hogy valamit hozzá kellene adni ami a spec-ből hiányzik, az spec hiányosság — jelezd és kérd a spec frissítését, ne töltsd ki magad a plan-ben.

**Ha a spec-ből valami hiányzik vagy ellentmondásos, jelezd — de ne egészítsd ki a spec-et magadban. A plan csak a spec alapján dolgozik.**

> **Túl egyszerű a feladat a teljes ciklushoz?** Ha a plan írása közben kiderül, hogy a ciklus valójában triviális — nincs valódi tervezési döntés, lényegében csak egy **konfiguráció összeállítása, egy egyszerűbb script vagy egy kisebb javítás** —, akkor a teljes `plan → tasks → analyze → … → review` flow túlméretezett. Jelezd a Felhasználónak, és **javasold az egyszerűsített flow-t**: *„Ez a ciklus elég egyszerűnek tűnik a teljes folyamathoz; a `/bs-quick-flow` (spec → task → implementáció) gyorsabb lehet rá. Váltsunk arra, vagy maradjunk a teljes ciklusnál?"* A döntés a Felhasználóé — ne válts önkényesen, és ne hagyd ki a fázisokat a teljes flow-n belül.

---

## <field:f_prerequisite>

0. **Ciklus-beazonosítás:** ha a felhasználó megadott ciklust/fájlt, azt használd; különben a legfrissebb `specs/cycle-*` mappát ajánld fel megerősítésre — <!-- INCLUDE:lang/common.md#ciklus-beazonositas --> — és várj a válaszra, mielőtt továbblépsz.

1. **`conventions.md` létezés-ellenőrzés:** olvasd be a projekt gyökerében a `conventions.md`-t. Ha nem létezik, STOP — térjenek vissza a `00` fázishoz.
2. **Munkafa-ellenőrzés (csak VCS esetén):** futtasd `git status --short`. Ha van commitálatlan változtatás, listázd, és kérdezd meg egy körben, hogy commitáljam-e vagy folytassam. (No-VCS projektben kimarad.)
3. Olvasd be a \`spec.md\` státuszát. **Ha a státusz nem \`<status:ready_for_plan>\`, ne kezdj el plan-t írni.** Jelezd a felhasználónak, hogy a spec még nem zárult le, és térjenek vissza a `02` spec fázishoz.

4. **Ciklus design input beolvasása (CD1) — automatikus:** ha létezik a `specs/cycle-NN-<cycle-name>/cycle-design-input.md`, olvasd be **minden futásban, külön felszólítás nélkül**. Ezt a felhasználó írta szabad formában a ciklusról; a 02 a viselkedési részét már a spec-be emelte, de a **technikai, eljárás- és koordináta-jellegű tartalma** (parancsok, hostok/portok, meglévő komponensek, build/deploy lépések, teljesítmény- és integrációs korlátok) **közvetlenül a plan bemenete**. A feldolgozás szabályait lásd a *„Ciklus design input feldolgozása (CD1)"* szekcióban. **Guard:** ha a fájl nem létezik vagy csak a sablon-szöveget tartalmazza, egy mondatban jelezd és folytasd — nem hiba, nem megállási ok.

_Megjegyzés: ha a spec `<status:ready_for_plan>`, a `specs/roadmap.md` implicit lezárt — a `02` spec fázis már ellenőrizte. Külön roadmap ellenőrzés nem szükséges._

---

## Folytatás megszakított futás után

Ha a plan fázis megszakad és új sessionban folytatódik:

```
1. Olvasd be a plan-questions.md aktuális állapotát (ha létezik).
   → Menj végig a kérdéseken sorban: [x]-eket átugorhatod, [ ]-eket
     egyenként tisztázd. Ha egy [x] áttekintésekor új kérdés merül fel,
     vedd fel a lista végére új Knn számmal.

2. Csak akkor írj/folytass plan szekciókat, ha minden kérdés [x].

3. Ha a plan.md koherensnek tűnik, de a státusz nem <status:ready_for_tasks>:
   futtasd a minőségellenőrzést + Constitution Check, majd kérj megerősítést.
```

Elég a `plan.md` és a `plan-questions.md` aktuális állapota + ez a prompt az újraindításhoz.

---

## Nyitott kérdések kezelése

A `plan-questions.md` a plan fázis kérdés-nyilvántartója. Minden felmerülő kérdés, spec hiányosság, döntési pont és ellentmondás ide kerül — nem csak a párbeszédbe. Ez teszi a folyamatot visszakövethetővé és megszakítás után folytathatóvá.

**Alapszabály: a listából soha nem törlünk. Lezárt kérdést csak `[x]`-szel jelölünk — a szövege és a döntés megmarad.**

### plan-questions.md struktúra

Ha még nem létezik, hozd létre a `specs/cycle-NN-<cycle-name>/` mappában:

```md
<!-- INCLUDE:lang/03-write-plan.md#plan-questions-struktura -->
```

Az új kérdést mindig a lista végére fűzd, a következő szekvenciális `Knn` számmal.

### Munkafolyamat

1. **Induláskor:** mielőtt bármilyen plan szekciót megírsz, olvasd be a spec-et és az érintett forrásfájlokat, és azonosítsd az összes felmerülő kérdést — beleértve a spec-ben jelzett _„Technológiai alapdöntések tisztázandók a plan fázisban"_ pontokat is. Vedd fel mindegyiket a `plan-questions.md`-be `- [ ] Knn` formátumban, szekvenciális számozással (K01, K02, ...). Ha már vannak korábbi kérdések a fájlban, folytasd a számozást onnan — a régi bejegyzéseket ne módosítsd, ne töröld. Ha kérdések kerülnek a `plan-questions.md`-be, állítsd a `plan.md` státuszát `<status:open_questions>`-ra.

    > **🔴 KÖTELEZŐ ELSŐ KÉRDÉS — E2E teszt stratégia.** A `plan-questions.md` **első** bejegyzése (`K01`) mindig az E2E lefedettség megközelítése. Ezt ne hagyd ki és ne told hátrébb. Az agent köteles előzetesen átvizsgálni a meglévő tesztelési infrastruktúrát (a `conventions.md` / meglévő integrációs tesztek alapján).
    - **Ha létezik `specs/test-conventions.md`:** a K01 kérdést **abból** kiindulva tedd fel — ne a nulláról kérdezz. Sorold fel konkrétan, mely 2./3. szekciós tételeket és 1. szekciós recepteket tervezed beemelni ebbe a ciklusba, és kérdezz rá: érvényesek-e még a 0. blokk adatai (URL, pod, teszt-user, paraméter), kell-e valamit elhagyni vagy hozzáadni. `<status:scope_shared_remote>` hatókörű recept beemeléséhez **explicit jóváhagyás kell**.
    - Ha a meglévő tesztelési infrastruktúra hibrid vagy natív gazdagépes folyamatokra épül (nem teljesen konténerizált), a kérdésben kötelezően fel kell tárnia ezt az eltérést a "Szigorú konténerizációs szabállyal" szemben, és javaslatot kell tennie:
      1. a meglévő hibrid/natív infrastruktúrát használjuk tovább ebben a ciklusban (hogy minimalizáljuk a meglévő tesztek átírásának kockázatát), vagy
      2. most alakítsuk át a teljes tesztelési infrastruktúrát teljesen konténerizáltra (megfelelve a szigorú szabálynak).
    - Az agent ajánlást tesz a spec és a meglévő infrastruktúra alapján — három lehetséges szint: (1) valódi konténerizált stack, (2) részleges mock (csak az, ami tényleg nem elérhető), (3) teljes mock (csak ha valódi infra semmilyen formában nem megvalósítható). Az ajánlást indokolja. A döntés csak a felhasználó jóváhagyása után kerül a plan-be. Mock csak dokumentált indoklással fogadható el.

2. **Tisztázás:** kérdésenként haladj — egyszerre csak egyet tegyél fel a felhasználónak. Ha megérkezett a válasz: jelöld `[x]`-szel a `plan-questions.md`-ben, és írj mellé egy soros összefoglalót a döntésről (`→ ...`). Ha a válaszból új kérdés merül fel: azonnal vedd fel a `plan-questions.md` lista végére a következő `Knn` számmal, mielőtt folytatnád. **Minden alkalommal, amikor kérdést teszel fel vagy jóváhagyást/véleményezést kérsz, a válaszod végén kötelezően helyezz el egy közvetlen, kattintható markdown linket az érintett fájlokra (pl. `[plan-questions.md](file:///abszolút/útvonal/specs/cycle-NN-name/plan-questions.md)` formában).**

3. **Folytatás:** csak akkor kezdj plan szekciókat írni, ha a `plan-questions.md` minden kérdése `[x]` státuszban van.

4. **Lezárás:** Ha minden szekció kész, minden kérdés lezárt és a minőségellenőrzés átment, tedd fel a kérdést a felhasználónak: <!-- INCLUDE:lang/03-write-plan.md#statusz-megerosites --> — Ne állítsd át a státuszt a megerősítés előtt. **A válasz végén helyezd el a `plan.md` közvetlen, kattintható linkjét.**

5. **Újraindítás új kontextusban:** ha a plan fázis megszakad és új sessionban folytatódik, az első lépés a `plan-questions.md` beolvasása (ha létezik). Menj végig az összes kérdésen sorban — a `[x]`-eket átugorhatod, a `[ ]`-eket egyenként tisztázd a fentiek szerint. Ha egy már lezárt kérdés (`[x]`) áttekintésekor új kérdés merül fel, vedd fel a lista végére új `Knn` számmal, és tisztázd, mielőtt továbblépnél.

---

## Hivatkozás-feloldás (dereferencing) — a bemenet szintje NEM a plan szintje

> **A leggyakoribb hiba ebben a fázisban:** az ágens **reprodukálja a bemenet absztrakciós szintjét**. Ha a spec vagy a `plan-input-from-prev.md` azt írja, hogy *„képfájl build és push a registrybe a `build.sh` futtatásával"*, akkor ez a mondat kerül a plan-be — a **konkrét parancsok, registry-host, image-tag és paraméterek nélkül**. Ugyanígy: ha a bemenet felsorolja egy hívás **paraméterneveit**, az ágens beéri ennyivel, és a plan-ből hiányzik a **tényleges JSON payload** (pl. egy kötelező `"channelType": "MOBILBANK"` mező), amit a meglévő tesztkód tartalmaz.

**A szabály:** a bemenet absztrakciós szintje nem határozza meg a plan absztrakciós szintjét. **Ha egy bemeneti tétel hivatkozik valamire ahelyett, hogy tartalmazná, a hivatkozást FEL KELL OLDANI a forrásból** — mielőtt a plan-be írnád.

**Mit kell feloldani (nem kimerítő lista — a minta a lényeg):**

| A bemenet ezt mondja | Ezt kell kinyerni és a plan-be írni | Forrás |
|---|---|---|
| „futtasd a `build.sh`-t" / „a szokásos deploy folyamat" | a tényleges parancsok szó szerint, registry-host, image-név és tag, env-változók | maga a script, `Dockerfile`, CI-konfiguráció |
| „a login helper endpointtal szerzünk tokent" | teljes URL, metódus, **konkrét JSON payload minden kötelező mezővel**, fejlécek, példa `curl` | meglévő teszt-/segédkód (`test/`), OpenAPI leíró |
| „a meglévő integrációs teszt mintájára" | a tényleges hívási lánc, fixture-ök, seed-adatok, elvárt válaszok | a hivatkozott tesztfájl |
| „a `conventions.md` szerinti eszközzel" | a **döntés** marad hivatkozás, de a **futtatandó parancs** konkrétan | `conventions.md` + `package.json`/`Makefile` |
| „a compose fájl felhúzza a stacket" | service-ek, portok, health check, indítási sorrend | a compose fájl |

**Hogyan, token-hatékonyan:**

- **Kis, célzott forrás** (egy script, egy env-minta, egy compose fájl): olvasd be **közvetlenül**.
- **Nagy vagy szétszórt forrás** (kódbázis-keresés kulcsszóra, sok tesztfájl átnézése): a `researcher` subagentet indítsd (`agents/researcher.md`) — **de a kérésben explicit kérj literál értékeket**: *„add vissza szó szerint a parancsokat / az URL-t / a teljes JSON payloadot, ne összefoglalót"*. A researcher alapból tömörít; itt a **pontosság elsőbbséget élvez a tömörséggel szemben**.
- **Kövesd a láncot:** ha a script egy másik scriptre vagy `.env` fájlra hivatkozik, addig menj, amíg konkrét értéket nem kapsz. **Kivétel:** valódi titok (klaszter-, registry-, VPN-, IAM-credential) — ott **állj meg és pointert írj** (TC5), ne az értéket.
- **Ne másold be a teljes REPÓ-FÁJLT:** egy forrásfájlból/scriptből csak a végrehajtáshoz szükséges részt (parancsok, koordináták, séma, paraméterek) emeld át — a plan terv, nem archívum. **Ez a szabály a repó forrásfájljaira vonatkozik, NEM a spec-ből származó kidolgozott artefaktumokra** (OpenAPI, payload, hibamátrix, teszt-forgatókönyv): azokat teljes egészében át kell vinni, lásd `KX3`.
- **Ne parafrazeálj:** a parancsot és a JSON-t **szó szerint** vidd át. Egy „nagyjából ilyen" payload rosszabb, mint a semmi, mert hibás bizalmat kelt.
- **Jelöld a forrást:** a beemelt érték mellé `_(forrás: keycloak/docker/build.sh)_` — így később kiderül, ha a forrás elmozdult a plan-ben rögzített másolattól.

**Mikor kötelező ezt lefuttatni:** minden olyan bemeneti tételnél (spec, `plan-input-from-prev.md`, `test-conventions.md`, roadmap), amely **eljárásra, scriptre, konfigurációs állományra, külső API-ra vagy meglévő tesztre hivatkozik**. Ez **különösen** igaz korai ciklusban, amikor a `specs/test-conventions.md` még nem létezik: ilyenkor a recept-adatok egyetlen forrása a **meglévő kód és teszt** — keresd meg őket, ne a bemenet szövegére hagyatkozz.

> **A hurok bezárása:** amit így felderítesz (parancsok, koordináták, payload-sémák), az a `<sec:environment_coords>` (KO1) szekcióba kerül — és pontosan az, aminek a ciklus végén a `08-doc-sync` révén be kell kerülnie a `specs/test-conventions.md`-be — a konkrét koordináták a 0. blokkba, a receptek az 1. szekcióba (TC3/TC13) — hogy a következő ciklus már ne derítse fel újra.

---

<!-- INCLUDE:shared/conventions-change.md -->

---

## Kidolgozott spec-artefaktum átemelése — szó szerint, csonkítás nélkül (KX3)

> **Ez a `Hivatkozás-feloldás` ELLENTÉTES esete, és a másik leggyakoribb hiba ebben a fázisban.** Az előző szekció arról szól, amikor a bemenet **túl absztrakt** (hivatkozik valamire ahelyett, hogy tartalmazná) — akkor fel kell oldani. Ez a szekció arról szól, amikor a bemenet **már teljesen kidolgozott**: a `spec.md` tartalmaz egy kész OpenAPI-leírót, egy komplett request/response payloadot, egy hibamátrixot vagy egy tízlépéses, elvárt eredményekkel ellátott teszt-forgatókönyvet. Ilyenkor az ágens hajlamos **„tervvé absztrahálni"**: összevonja a lépéseket, a payloadot mezőnév-felsorolásra cseréli, a leírót „a spec részletesen definiálja" mondattal helyettesíti. **Ez adatvesztés, nem tervezés.**

**A szabály (a 02 `KX2` szabályának tükre):** ha a spec (vagy a `cycle-design-input.md`, a `*-input-from-prev.md`, egy korábbi ciklus planje) egy artefaktumot **már kidolgozva ad meg**, azt a plan-be **szó szerint, teljes egészében** kell átvinni. **Az irány bővítés és pontosítás — összevonás és elhagyás nem.**

**Mire vonatkozik kötelezően (a lista jellege a lényeg, nem a hossza):**

| Artefaktum a spec-ben | Hogyan kerül a plan-be |
|---|---|
| OpenAPI / JSON Schema / Avro / proto / GraphQL részlet | **változatlan blokként**, minden mezővel, típussal, `required`-del, példával |
| request/response payload | **teljes JSON-ként**, minden kötelező és opcionális mezővel — nem mezőnév-felsorolásként |
| hibamátrix (státusz + `errorCode` + body) | **teljes táblaként**, minden sorral — nem „a hibakezelés a spec szerint" |
| többlépéses teszt-forgatókönyv (①…②…③, elvárt eredményekkel) | **minden lépés, minden köztes ellenőrzés és minden elvárt eredmény** — a lépések nem vonhatók össze |
| cache-kulcs séma / DB DDL / migrációs script | szó szerint, teljes kulcs- és mező-listával |
| konfigurációs minta (`.env`, compose-részlet, YAML) | szó szerint, minden kulccsal |

**Amit szabad — és kell:**
- a **szimbolikus koordinátákat konkrét értékre** cserélni (`{PUBLIC_BASE_URL}` → tényleges URL) — ez a `Hivatkozás-feloldás` szabálya, tehát **bővítés**;
- **hozzátenni**, ami a plan szintje: teszteset-azonosító (`TC-XX-01`), teszt-szint, futtatási parancs, fixture, környezet-felkészítés;
- **kifejteni** a hiányos lépést (hiányzó köztes ellenőrzés, meg nem adott elvárt eredmény);
- **átrendezni**, ha a sorrend nem végrehajtható (a nem triviális átrendezést jelezd).

**Amit tilos:**
- ❌ lépéseket **összevonni** vagy „a folyamat végigfut" típusú összefoglalóra cserélni;
- ❌ payloadot **mezőnév-felsorolásra**, táblát **prózára** cserélni;
- ❌ **hivatkozni** rá: *„lásd a `spec.md` Teszt specifikáció szekcióját"*, *„a spec részletesen leírja"*, *„a többi eset hasonlóan"*, *„…stb."*;
- ❌ **példát elhagyni** azzal, hogy „a séma önmagában elég".

**Önellenőrzés (mérhető):** a plan megfelelő szekciója **nem lehet rövidebb**, mint a spec forrás-szekciója. Ha rövidebb lett, az **bizonyítandó**, nem magától értetődő: nevezd meg, mi került át máshova (pl. külön `<sec:schema_artifacts>` bejegyzésbe), vagy pótold. A `05-analyze` mechanikus kapuja ezt gépiesen is méri (`V1`/`V2` check): a spec kód-blokkjainak tartalmát keresi a plan-ben, és összeveti a két teszt-szekció terjedelmét.

> **A három félreérthető szabály, ami emiatt szokott ütközni — a feloldás:**
> - *„A plan terv, nem archívum"* (lásd `Hivatkozás-feloldás`) a **repó forrásfájljaira** vonatkozik: egy 2000 soros scriptből csak a végrehajtáshoz szükséges rész kell. A **spec-ből származó szerződés-artefaktumokra nem vonatkozik** — azok teljes egészében a plan tartalmához tartoznak.
> - *„A spec absztrakciós szintjét fel kell oldani, nem reprodukálni"* az **absztrakciós szintre** igaz, nem a **tartalomra**: a szimbolikus koordinátát konkréttá kell tenni, de a részletességet megőrizni (sőt növelni).
> - A `05-analyze` **duplikáció-kategóriája** (1.) **nem** vonatkozik a spec → plan szó szerinti átemelésre: az nem redundancia, hanem a kötelező önhordóság. Duplikáció az, ha ugyanaz a döntés a plan-en **belül** kétszer szerepel, vagy ha a tasks.md újra leírja a plan teszteset-lépéseit.

---

## Fázisok közötti átadás (`*-input-from-prev.md`) — IP1

**Amit BEOLVASSZ:** ha létezik a `specs/cycle-NN-<cycle-name>/plan-input-from-prev.md`, olvasd be a fázis elején. Ez a 01/02 fázisban felszínre került technikai és implementációs részleteket tartalmazza (érintett komponensek, meglévő megoldások, technológiai megkötések), amelyek a spec-be nem illettek. Minden `[ ]` tételt vagy építs be a `plan.md` megfelelő szekciójába, vagy vess el explicit indokkal, és pipáld ki. **Guard:** ha a fájl nem létezik, ez nem hiba — folytasd.

**Amibe ÍRHATSZ:**
- **`tasks-input-from-prev.md`** — a **04**-nek: előkészítő lépés, sorrend-megkötés, konkrét parancs vagy környezeti előfeltétel, ami a task-bontásnál kell, de a `plan.md` szekcióiba nem illik.
- **`validate-input-from-prev.md`** — a **07**-nek: futtatási előfeltétel és üzemeltetési tudnivaló, ami csak a validálásnál válik relevánssá (pl. „a stack indítása előtt VPN kell", „a Sonar futtatás előtt a mock szervert le kell állítani, mert ütközik a porton").

<!-- INCLUDE:shared/input-from-prev.md -->

---

## Ciklus design input feldolgozása (CD1)

A `specs/cycle-NN-<cycle-name>/cycle-design-input.md` a **felhasználó saját, szabad formájú ciklus-leírása** (a 01 hozta létre üres sablonként, a felhasználó töltötte ki — opcionálisan). A 02 ennek a **viselkedési** részét már a `spec.md`-be emelte; ami **neked** marad, az a **technikai és eljárás-jellegű tartalom**, ami a spec-be nem való, de a plan-nek elsőrangú bemenete:

- konkrét parancsok, scriptek, build/deploy lépések;
- hostok, portok, base URL-ek, namespace-ek, image-nevek (koordináták);
- meglévő komponensek, könyvtárak, minta-implementációk megnevezése;
- technológiai megkötés, teljesítmény-korlát, integrációs feltétel;
- a felhasználó által vázolt megvalósítási irány vagy sorrend-preferencia.

**Szabályok:**

1. **Ne írd át a fájlt, és ne pipálj ki benne semmit.** Ez a felhasználó dokumentuma, nem átadó-fájl (`*-input-from-prev.md`).
2. **Az önhordóság szabálya (a fázis legfontosabb szabálya) itt is érvényes.** A design inputból származó adatot **be kell másolni a `plan.md`-be** — hivatkozni rá („lásd a design inputban") **tilos**: a 04 és a `test-runner` nem olvassa ezt a fájlt.
3. **Hivatkozás-feloldás kötelező.** Ha a design input scriptre, meglévő tesztre, konfigra vagy külső API-ra **hivatkozik**, oldd fel a forrásból (konkrét parancs, URL, teljes payload) a *„Hivatkozás-feloldás (dereferencing)"* szekció szerint — a felhasználó vázlatos megfogalmazását ne reprodukáld.
4. **Ütközés esetén kérdezz.** Ha a design input ellentmond a `spec.md`-nek (amit a felhasználó már jóváhagyott), **ne dönts magadtól**: vedd fel `Knn` kérdésként a `plan-questions.md`-be. Ha a design input olyan **viselkedési** elvárást tartalmaz, ami a spec-ből hiányzik, az a *spec kritika* ága — jelezd, hogy a 02-be tartozik.
5. **Ami nem a plan dolga, azt add tovább**, ne dobd el: task-szintű előkészítő lépés → `tasks-input-from-prev.md`, futtatási/üzemeltetési tudnivaló → `validate-input-from-prev.md` (IP1).
6. **Jelezd a felhasználónak** egy tömör listában, hogy a design input mely tételei hova kerültek (plan szekció / tasks-input / validate-input / új `Knn` / a 02-be visszairányítva).

**Guard:** ha a fájl nem létezik vagy csak a sablon van benne, ez nem hiba — egy mondatban jelezd, és folytasd.

---

## Kontextus betöltési szabályok

- Olvasd be a ciklus `spec.md`-jét.
- Ha létezik `cycle-design-input.md`: olvasd be (CD1) — a felhasználó saját ciklus-leírása, a technikai része a plan bemenete.
- Ha létezik `plan-questions.md`: olvasd be.
> **Melyik regiszter mit tud (TC1/c):** a **riport-artefaktumok, az útvonal-alapjuk és a riport-generáló parancsok** a projekt `conventions.md` `## <sec:cv_test_reporting>` szekciójában élnek — **azt olvassa a 07 TR3 kapuja**. A `specs/test-conventions.md` a **receptek és koordináták** regisztere. Ha a ciklus a riport-struktúrát vagy a riport-parancsot változtatja, a `conventions.md`-t kell átvezetni (GC1) — a `test-conventions.md` frissítése nem helyettesíti.

- **Visszatérő teszt-elvárások és receptek (TC1) — `specs/test-conventions.md`:** ha létezik, olvasd be **teljes egészében** (a 0. blokkot és mindhárom szekciót). Ez a `08-doc-sync` által karbantartott regiszter: **0. blokk = Koordináták** (környezetek, URL-ek/portok, health endpointok, teszt-userek, kliensek, scope-ok, paraméterek, env-pointerek — **minden konkrét érték egy helyen**), 1. szekció = recept-regiszter (komponens-koordináták, indítás, példa hívások, build/deploy parancsok), 2. szekció = minden körben szükséges lokális (mock alapú) tesztek, 3. szekció = minden körben szükséges integrációs/E2E tesztek. **Guard:** ha a fájl nem létezik (korai ciklus), ne állj meg és ne hozd létre — egy mondatban jelezd, és a `plan-questions.md` K01 kérdését a meglévő tesztelési infrastruktúra alapján tedd fel.

  > **🔴 A `plan.md` ÖNHORDÓ (TC1/a — kötelező).** A `run-tests.py` szkript a `plan.md` **gépi futtatási tábláját** olvassa, a `test-runner` subagent (fallback) pedig a `test-conventions.md`-t **nem olvassa** — kizárólag a `plan.md` `<sec:testing_strategy>` és `<sec:regression_impact>` szekcióit. Ezért **minden tesztelési feladatot maradéktalanul át kell emelni a `plan.md`-be**, kiegészítve a 0. blokk és az 1. szekció **összes** hozzá tartozó adatával: teszt-userek és jelszavaik, URL-ek, portok, namespace/pod, image-név, registry-cél, paraméterek, **példa hívások (`curl`)**, build/push/restart parancsok, előfeltételek és futási sorrend.
  > - **Puszta hivatkozás NEM elég** (`„lásd test-conventions.md R03"` önmagában tilos) — a `test-conventions.md`-re csak **provenance**-ként hivatkozz a beemelt tartalom mellett (pl. „_(forrás: test-conventions.md R03)_").
  > - **Placeholder TILOS** (`<ide jön a jelszó>`, `<TODO URL>`) — ha egy adat hiányzik vagy elavult, az `plan-questions.md` kérdés, nem placeholder.
  > - **Nem automatikus futtatás:** a regiszterből **csak az** kerül át, ami ebben a ciklusban tényleg szükséges. Ez a beemelés maga az emberi kontroll-pont — a `plan.md` a futtatás egyetlen igazsága.
  > - **Elavult tétel:** ha egy recept adata nem stimmel a valósággal, vagy az `<field:f_last_run>` markere régi, **kérdezz rá** a `plan-questions.md`-ben. A `test-conventions.md`-t **ne írd** — a javítás a `08-doc-sync` dolga (TC4); a ciklus a plan-be a felhasználóval egyeztetett, helyes adatot veszi.
  > - **`<status:scope_shared_remote>` hatókörű recept** (a regiszter így jelöli): a beemelés előtt **kötelezően kérdezz rá** a `plan-questions.md`-ben — osztott dev/test környezetben egy image-push vagy pod-restart más munkáját is érinti.
- **Forrásfájl-azonosítás (a plan dolga, nem a spec-é):** a spec `<sec:referenced_files>` szekciója **csak dokumentációs/specifikációs anyagot** tartalmaz (README, OpenAPI, séma, példa payload) — forrásfájlokat (`.ts`, `.tsx`, `.js`, `package.json`, stb.) **nem**. A módosítandó/érintett forrásfájlokat a **03 fázis azonosítja önállóan**, a spec `<sec:components_behavior>` szekciója alapján. Ehhez indítsd el a `researcher` subagentet (`agents/researcher.md`), amely visszaadja az érintett forrásfájlok listáját (path + hely + jelleg) — a nyers fájltartalom nem terheli a fő kontextust. Csak az így azonosított, valóban releváns forrásfájl-részeket olvasd be közvetlenül.
- **Spec-ben hivatkozott dokumentációs/specifikációs fájlok:** ha a `spec.md` a `<sec:referenced_files>`-ban külső leírókra hivatkozik (JSON séma, OpenAPI leíró, példa payload), ezeket is olvasd be a terv elkészítése előtt.
- **Külső függőségek dokumentációja:** Ha a ciklus külső függőséget vezet be vagy igénybe vesz (pl. Keycloak, külső API, messaging broker), kérd be a vonatkozó dokumentációt vagy MCP szervereket a felhasználótól még a plan megkezdése előtt. Nézd át, és döntsd el, hogy elegendő és releváns információ áll-e rendelkezésre. Ha nem, vedd fel nyitott kérdésként a `plan-questions.md`-be.
- Ha egy nagy vagy bonyolult fájlt kell megértened, hívd ugyanazt a `researcher` subagentet (`agents/researcher.md`, Mód B) a kutatáshoz. A subagent csak az összefoglalót adja vissza — a nyers fájltartalom nem kerül be a fő kontextusba.
- **Dokumentáció felkutatása (Documentation Reconnaissance):** Az ágens köteles a tervezés megkezdése előtt felkutatni a teljes projektben lévő összes olyan leírást (pl. `docs/` mappa, README.md fájlok, diagramok), amely érintett lehet a változások által (pl. hivatkozik a módosítandó végpontra, változóra vagy folyamatra). Mivel ez a keresés sok fájl beolvasásával járhat, **a `researcher` subagent (`agents/researcher.md`) végzi** — ugyanaz az ágens, amelyik a forrásfájlokat azonosítja. A subagent elvégzi a kereséseket, elemzi a találatokat, és kizárólag a módosítandó dokumentumok listáját és a cserélendő részek rövid összefoglalóját adja vissza, megóvva ezzel a fő kontextus tisztaságát. Elsődleges cél, hogy a projektben lévő összes leírás és diagram naprakész legyen.
- **Korábbi ciklusok `plan.md`-jei — fő szabály:** ne olvasd be őket. **Kivételek, amikor viszont KÖTELEZŐ megnézni (TP3/a):**
  1. a spec explicit függőséget jelöl egy korábbi ciklusra; **vagy**
  2. **a ciklus tesztjeinek futtatásához olyan környezeti előfeltétel kell, amit egy korábbi ciklus épített ki** (egyedi plugin/SPI, mock szerver, seed-adat, konténer-stack, teszt-user, token-beszerző helper), **és a hozzá tartozó parancsok nincsenek benne a `specs/test-conventions.md`-ben**. A regiszterbe a `08-doc-sync` promótál — ami még nem került be, az **csak az adott ciklus `plan.md`-jében létezik**.
  - **Hogyan:** ne olvasd be a teljes fájlt a fő kontextusba — indítsd a `researcher` subagentet (`agents/researcher.md`, Mód B) a konkrét kérdéssel (pl. „a `cycle-24-...` planjéből add vissza **szó szerint** a Keycloak SPI build/push/rollout parancsait, az image-nevet, a namespace-t és a rollback-lépést"), **literál értékeket kérve**. A kapott parancsokat a *Hivatkozás-feloldás* szabálya szerint **bemásolod** ebbe a planbe, `_(forrás: cycle-NN plan.md)_` provenance-szal.
  - **Mennyit:** csak a végrehajtáshoz ténylegesen szükséges receptet — nem a korábbi ciklus tervét, döntéseit vagy scope-ját.
  - **Ha ellentmond a valóságnak** (a parancs elavultnak tűnik, más az image-tag): `plan-questions.md` kérdés, ne találgass.
  - **Jelezd a felhasználónak** egy sorban, hogy melyik korábbi ciklus planjéből mit emeltél át — ez a `08-doc-sync` számára is jelzés, hogy a tétel promótálandó a `test-conventions.md`-be.

---

<!-- INCLUDE:shared/artifact-voice.md -->

---

## Plan struktúra

### 🔴 Stabil szekció-azonosítók (PID1) — a tasks.md ezekre hivatkozik

**Minden végrehajtható terv-szekció címébe stabil azonosítót írsz**, közvetlenül a `###` után:

```md
### [P-CONFIG] Konfigurációs rendszer és config-fájlok
### [P-REDIS] Redis kapcsolódás kiterjesztése
### [P-E2E-UI] Playwright felületi E2E
```

| Szabály | Mechanika |
|---|---|
| **Formátum** | `[P-<NÉV>]` — nagybetűs, kötőjeles, 1–2 szó, a szekció tartalmára utal. Sorszám **nem** része (`[P-3-1]` tilos). |
| **Ki kap ID-t** | **Csak végrehajtható terv-szekció:** a `<sec:planned_changes>` és a `<sec:test_specification>` / `<sec:testing_strategy>` alszekciói — ahol az van leírva, **mit kell csinálni**. |
| **Ki NEM kap** | `<sec:goal_and_approach>`, `<sec:affected_components>` (leltár), `<sec:environment_coords>` (leltár), `<sec:execution_order>`, `<sec:risks>`, `<sec:new_dependencies>`, IP1-szekciók. Ezek **nem lehetnek** task-hivatkozás célpontjai (E). |
| **Egyediség** | Egy ID egyszer szerepelhet a plan-ben. |
| **Stabilitás** | Egy kiadott ID **soha nem változik** — akkor sem, ha a szekció sorszáma eltolódik, átnevezed, vagy a fejezet átkerül máshova. Törölt szekció ID-ja **nem használható újra**. Új szekció (pl. az analyze-hurok szúrta be) **új ID-t** kap. |
| **Miért** | A `tasks.md` sorszám helyett ID-re hivatkozik. Ha egy javítás beszúr egy `§3.10`-et, a sorszámok elcsúsznak, és a taskok **némán rossz szekcióra mutatnak** — az ID ezt kizárja. |

_Sorszámot használhatsz a cím olvashatóságáért (`### 3.1 [P-CONFIG] …`), de a **hivatkozási kulcs mindig az ID**._

\`\`\`md
# Cycle NN: <cím> — Plan

**<field:f_status>:** \`<status:draft>\` | \`<status:open_questions>\` | \`<status:ready_for_tasks>\`
**<field:f_gate>:** _<a mechanikus kapu eredménye a lezáráskor — pl. `analyze-gate-check --plan-only — PASS, 0 Must Fix (2026-09-01)`>_

## <sec:goal_and_approach>

_Egy bekezdés: mit valósítunk meg és hogyan. Nem ismétli a spec célkitűzését, hanem a technikai megközelítést összegzi._

## <sec:affected_components>

_Felsorolás: melyik fájl / komponens változik, milyen jellegű változás (új fájl, bővítés, módosítás)._

## <sec:environment_coords> (KO1)

_**Kötelező szekció — a `plan.md` önhordóságának alapja.** Ide kerül **minden konkrét érték**, ami a ciklus fejlesztéséhez és teszteléséhez kell, feloldva: komponens-URL-ek és portok, indító parancsok, példa REST hívások, teszt- és API-userek jelszóval, minden paraméter. Ez a `specs/test-conventions.md` **0. blokkjának ciklus-szintű megfelelője** — de nem hivatkozás rá, hanem a ciklusban tényleg használt értékek **szó szerint**._

_**Szabályok:** placeholder **tilos** (`<TODO>`, `<ide jön a jelszó>`, `TBD`) — ami hiányzik vagy elavult, az `plan-questions.md` kérdés, nem placeholder. Üres cella **tilos**; ami erre a ciklusra nem értelmezhető, oda `—` kerül. Hivatkozás nem helyettesíti az adatot („lásd a spec-et", „a szokásos teszt-user"). Titok-szabály (TC5): dev-hatókörű teszt-user, mock-credential és lokális jelszó **konkrét értékkel** ide kerül; klaszter-, registry-, VPN-, IAM- és éles credential **soha** — helyette pointer (hol tárolják, ki adja ki)._

**<field:f_target_env>:** <a ciklus cél-környezete: `lokális`, `dev`, `lokális + dev`, …>

_**Kötelező mező (EV1).** Ki kell mondani, MELY környezetre szól ez a ciklus — mert egy zöld teszt önmagában nem bizonyítja, HOL volt zöld. Egy éles ciklus a dev-re telepített, a tesztjei viszont lokális célpontra futottak (egy `…:dev-e2e` nevű script configjában `baseURL: "http://127.0.0.1:5178"` állt): minden zöld lett, és így nem derült ki, hogy a dev-re telepített komponens el sem indult. Ez a mező köti a teszt-célpontot a ciklus szándékához, és erre méri az `05` kapuja a futtatási tábla `<field:f_environment>` oszlopát és a `TS-NN` hívásait (EV1–EV5)._

### <sec:components_endpoints>

| Komponens | Repo-útvonal / image | Base URL | Port(ok) | Health endpoint | Indítás (szó szerinti parancs) | Leállítás / takarítás |
|---|---|---|---|---|---|---|
| `tmp-service` | `services/tmp/`, `registry.example/tmp:v1-<UTC>` | `http://localhost:8081` | 8081 (HTTP), 5005 (debug) | `GET /actuator/health` → `200` | `docker compose -f docker-compose.e2e.yml up -d tmp-service` | `docker compose -f docker-compose.e2e.yml down -v` |

### <sec:rest_calls_examples>

_Minden olyan hívásból, amit a fejlesztés vagy a teszt használ: **ige, teljes URL, fejlécek, konkrét request body minden kötelező mezővel, elvárt válasz, a válaszból kinyerendő mező**. A token-beszerzés (user és S2S külön, ha mindkettő kell) itt is kötelező — nem elég, hogy „van login helper"._

| Hívás | Ige + végpont | Fejlécek | Request body | Elvárt válasz | Kinyert érték |
|---|---|---|---|---|---|
| user token | `POST http://localhost:9090/api/v13/login/token` | `Content-Type: application/json` | `{"userId":"test-user","password":"Test123!"}` | `200`, `{"token":"…"}` | `$JWE` ← `.token` |

\`\`\`bash
# user token
JWE=$(curl -sS -X POST 'http://localhost:9090/api/v13/login/token' \
  -H 'Content-Type: application/json' \
  -d '{"userId":"test-user","password":"Test123!"}' | jq -r '.token')

# cache init
curl -sS -X POST 'http://localhost:8081/init-hash' \
  -H "Authorization: Bearer $JWE" -H 'Content-Type: application/json' \
  -d '{"productType":"LOAN","channelType":"MOBILBANK"}'
\`\`\`

### <sec:test_api_users>

| User / kliens | Jelszó / credential | Hol érvényes | Szerep / scope / client-id | Mire használjuk |
|---|---|---|---|---|
| `test-user` | `Test123!` | lokális mock login (`http://localhost:9090`) | `retail` | E2E bejelentkezés |
| `tmp-s2s` | pointer: `Vault kv/dev/tmp` (TC5 — a titok nem kerül a plan-be) | dev klaszter | `client_credentials`, scope `tmp.write` | S2S token |

### <sec:other_parameters>

| Paraméter | Érték | Hol / mikor kell |
|---|---|---|
| `appId` / `buildId` / `processName` | `42` / `7` / `loan-onboarding` | a folyamatindító hívás útvonal-paraméterei |

### <sec:network_access_prereqs>

_VPN, proxy, `oc login` / kubeconfig, namespace, registry-belépés: mi kell, milyen sorrendben, és **pointer** a credentialre (TC5) — soha nem a titok._

## <sec:planned_changes>

_Fájlonként, függvény/osztály szinten: mi változik és miért. Nem kód, hanem szándék. Minden bejegyzés tartalmazza:_
- _a **<field:f_purpose>** sort: mit akarunk elérni és miért (WY1 — lásd alább, kötelező)_
- _az érintett fájl path-ját_
- _az érintett vagy létrehozandó függvény/osztály nevét_
- _az interfész változást, ha van (új paraméter, új return type, új export)_
- _új fájl esetén a fő exportált egységek nevét_
- _meglévő fájl esetén az érintett kódrészlet helye (pl. `src/file.ts:14–25`) navigációs célként, ha a forrásfájlt beolvastad_

> **Útvonal-formátum (RP1) — itt a leggyakoribb elrontása.** A kód- és fájl-hivatkozás **a repó gyökeréhez képest relatív**: `src/token-store.ts`, `apps/web/src/index.ts:42`. **Nem** a `plan.md` mappájához képest (`../../src/...`), **nem** abszolút (`/home/...`, `C:\...`), és **nem** `file://` link. Indok: a parancsok a repó gyökerében futnak, és a `05-analyze` kapuja is oda oldja fel a horgonyokat — egy `../../` alakú hivatkozás ott feloldhatatlan. A **dokumentum-linkek** (pl. `[spec.md](./spec.md)`) viszont a fájl saját könyvtárához képest relatívak, hogy kattinthatók legyenek. A részletes szabály a fázis minőségellenőrzésében van.

> **🔴 Minden `[P-…]` bejegyzés kötelezően megmondja a CÉLT (WY1).** A „mit írunk át" önmagában nem mondja meg, **mit akarunk elérni** — az implementáló, a `reviewer` és a 07 hurok fixere viszont pontosan ebből dönti el, hogy egy eltérő megoldás is jó-e, és mikor van kész a változtatás. Ezért minden `### [P-…]` szekció az érintett fájlok mellett **kötelezően** ezt a sort viseli:
>
> ```md
> **<field:f_purpose>:** <a viselkedés, ami a változás UTÁN igaz lesz> — mert <a jelenlegi hiányosság vagy hiba, amit megszüntet>. (<sec:definition_of_done>: DoD-03)
> ```
>
> - **A cél a spec-ből következik, nem a te ötleted (a SC1 tükre):** a mondat végén megnevezett `DoD-NN` (vagy spec-követelmény) ugyanaz, ami ehhez a `[P-…]`-hoz a `<sec:reverse_coverage>` táblában áll. Ha nem tudod megnevezni a forrást, a bejegyzésnek nincs helye a plan-ben: vagy `plan-questions.md` kérdés, vagy vissza a 02-be.
> - **Ami NEM cél:** a módosítás megismétlése más szavakkal („bevezetjük a `getS2SToken()` metódust"), a fájlnév („frissítjük a configot"), üres általánosság („javítjuk a minőséget", „refaktorálunk"). A cél a **viselkedést** mondja ki, amit a rendszer utána produkál, és a **bajt**, amit megszüntet.
> - **Egy bekezdés, nem egy szó.** Ha a bejegyzés több fájlt és több lépést fog össze, a cél is összefoglalja, mi lesz belőlük együtt.

**Kalibrációs minta egy bejegyzésre** (a sűrűséget másold, ne a témát):

```md
### [P-30-02] S2S gépi token tárolása a Redis session store-ban
- **Érintett fájlok:** `src/services/session-store-service.ts`, `src/types/session.ts:41-58`
- **<field:f_purpose>:** a `tmp-s2s` gépi token a több pod által közösen olvasott Redis kulcsra kerül (`{namespace}_tmp:tokens:s2s`), így három párhuzamosan futó példány közül **egy** kér új tokent a Keycloaktól, nem mind a három — mert ma minden példány a saját memóriájában tartja, és minden hidegindulás annyi `client_credentials` hívást termel, ahány pod fut. (<sec:definition_of_done>: DoD-01, DoD-04)
- **Módosítási részletek:**
  1. …
```

_Ha ez a szintű részletesség nem érhető el a spec alapján, olvasd be az érintett forrásfájl releváns részét._

**Interfész tervezési elv — deep module:** Új modul vagy függvény tervezésekor törekedj arra, hogy sok funkcionalitást rejtsen el egyszerű interfész mögé. A hívó oldalnak nem kell tudnia a belső logikáról — csak a bemenetet és a kimenetet látja. Kerüld a shallow module-t: ha egy függvény kevés logikát csinál de komplex hívást igényel, az a komplexitást a hívó félre hárítja ahelyett, hogy elrejtené.

> **🔴 A `docs-generated/` NEM kerülhet ide (DS4).** A `docs-generated/` mappa fájljai (`system-overview.md`, `architecture.md`, `CHANGELOG.md`, `design-drift.md`, mappa-index) a **08-doc-sync kizárólagos tulajdonai** — azokat sem a plan nem tervezi, sem az implementáció nem írja. Ide **kizárólag** a forráskód, a konfiguráció és a tesztek kerülnek. (A generált doksik frissítése a ciklus végén, a 08 fázisban történik, automatikusan.)
>
> **Komponens-README — a határvonal a komponens létezése (nem a fájltípus):**
> - **Új komponens első `README.md`-je** → **ide tartozik** (a komponens felépítésének része; a doc-sync csak azt tudja rekonciliálni, ami már létezik).
> - **Meglévő komponens README-jének frissítése** (env-változó, port, indítás, kapcsolatok változtak) → **NEM ide tartozik**: azt a `08-doc-sync` végzi. Ne tervezz rá módosítást és ne generálj rá taskot.

**Új komponens tervezési elv:** Minden spec-ben említett új komponens — tech stacktől függetlenül — saját bejegyzést kap a tervezett módosításokban. Ez tartalmazza: a projekt struktúrát, a build rendszert (pl. Maven, Gradle, npm, go.mod), a kommunikációs módot (REST, messaging, gRPC, stb.) és a deployment mechanizmust (JAR, Docker image, bináris, stb.). Egy komponens nem tekinthető tervezettnek, ha csak a mock/szimuláció szerepel a plan-ben, de a spec valós implementációt ír elő.

Új komponensnél a `README.md` kötelező deliverable — vedd fel explicit a tervezett módosítások közé (`<komponens-gyökér>/README.md`, új fájl). Tartalma: mit csinál, indítás, port, debug, logok, kapcsolatok.

## <sec:new_dependencies>

_Új csomagok és külső függőségek, ha a ciklus igényli — tech stacktől függetlenül (npm, Maven, pip, stb.). Ha nincs új függőség, ezt explicit írd ki: "Nincs új függőség."_

## <sec:config_build_changes>

_Új env var-ok, docker módosítások, konfigurációs fájl változások. Ha nincs ilyen, explicit írd ki: "Nincs konfiguráció változás."_

_**Konfiguráció-életút (KF1) — minden új/módosított paraméterhez kötelező sor.** Egy paraméter bevezetése nem ér véget a kód olvasásánál: **minden futtatási módban** el kell jutnia a futó processzhez, különben a teszt más konfigurációval fut, mint a fejlesztés._

| Paraméter | Honnan jön (default / fájl / env) | Lokális futás | Unit/integrációs teszt | Konténer / compose | Dev deploy | Ha hiányzik |
|---|---|---|---|---|---|---|
| `TMP_CONFIG_PATH` | env, default `config/tmp-config.yaml` | `.env` | teszt-fixture env | `docker-compose.yml` `environment:` + kötet-mount | deployment env | fail-fast indulásnál |

_Az utolsó oszlop kötelező: **fail-fast** vagy **konkrét default** — „nincs meghatározva" nem elfogadható. Ha egy cella üres maradna, az **hiányzó terv**: vagy kitöltöd, vagy `plan-questions.md` kérdés lesz belőle._

## <sec:schema_artifacts>

_A ciklus által bevezetett vagy módosított formális sémák és API leírók. <field:f_status>: `<status:draft>` | `<status:review_required>` | `<status:reviewed>`_

| Artifact | Típus | Fájl | Státusz |
|---|---|---|---|
| ... | OpenAPI / Redis key map / Avro / DB schema | `docs/...` | `<status:review_required>` |

## <sec:testing_strategy>

_Milyen típusú tesztek kellenek (unit / integrációs / e2e)? Melyik meglévő tesztfájl módosul, melyik új fájl keletkezik?_

_**Beemelt visszatérő elvárások (TC1) — kötelező, ha létezik `specs/test-conventions.md`:** a regiszter 2. és 3. szekciójának ebben a ciklusban szükséges tételei, **önhordóan** (a hozzájuk tartozó recept-adatokkal, nem puszta hivatkozással). Minden beemelt tétel mellé írd a provenance-t: `_(forrás: test-conventions.md L01)_`. Ha egy tétel adatát a `plan-questions.md`-ben javítottad, a **javított** adat kerül ide._

<!-- INCLUDE:shared/test-scenario-design.md -->

### <sec:plan_test_scenarios> — **kötelező (TS1)**

> **🔴 Miért kötelező:** a fenti próza a teszt-**típusokról** szól, ez a szekció a teszt **tartalmáról**. A `plan.md` önhordó (TC1/a): a `test-runner` és a `bs-manual-test-plan` is **kizárólag** ebből dolgozik, és a `07` egy bukott tesztjét is ebből kell tudni kézzel reprodukálni. Ezért minden tesztesetet **végrehajtható forgatókönyvként** kell kifejteni — nem „a login flow tesztelve lesz", hanem lépésenként: mit hívunk, milyen konkrét értékkel, és pontosan mit várunk vissza.
>
> **A mérce (önteszt):** *„Egy ember, aki nem vett részt a tervezésben, kizárólag ezt a szekciót olvasva végig tudja csinálni a tesztet, és el tudja dönteni, hogy sikerült-e."* Ha bármit ki kellene találnia — melyik URL, melyik user, mi a helyes válasz —, a forgatókönyv hiányos.
>
> **A spec tesztesetei nem összevonhatók (KX3).** Ha a spec `<sec:test_specification>` szekciója hat esetet ír le, itt hat forgatókönyv áll — bővíteni és pontosítani szabad, összevonni és elhagyni nem.
>
> **🔴 A spec teszt-szekciójának SZERKEZETÉT ne másold — konvertáld (TS7).** A leggyakoribb bukás nem az, hogy a teszt kimarad, hanem hogy a fázis a spec **saját címsor-szerkezetét** hozza át (`Teszteset 0`, `Teszteset 1`, „REST szekvencia", „Verifikáció" felsorolással), és emellett a `### <sec:plan_test_scenarios>` szekció **létre sem jön**. Az eredmény olvasható prózának tűnik, de: a mechanikus kapu nem látja (nincs `TS-NN`), a `test-runner` nem futtatja, a `bs-manual-test-plan` nem szerel össze belőle semmit, és a lépésenkénti elvárt eredmény ellenőrizhetetlen marad. Ezért:
>
> - a spec **minden** tesztesete **egy önálló `TS-NN` blokká** konvertálódik, a fenti négy sorral és a négyoszlopos lépés-táblával;
> - a spec teszteseteinek **nem nyithatsz párhuzamos, saját nevű szekciót** (`Részletes tesztesetek`, `Szekvencia-leírások`, `Teszteset N`) — ami nincs `TS-NN` blokkban, az a keret számára nem létezik;
> - a megfeleltetést a `<sec:spec_coverage>` tábla rögzíti: **minden sor `Plan teszteset(ek)` cellája megnevez legalább egy `TS-NN`-t** (a `TC-…` azonosító mellett). A kapu ezt méri, mindkét irányban.

Forgatókönyvenként egy blokk, pontosan ebben a formában:

#### TS-01 — <a forgatókönyv neve>  (DoD-02, DoD-05)

**<field:f_what_we_test>:** <mit ellenőriz ez a forgatókönyv — a viselkedés, amiért fut, egy mondatban>
**<field:f_prerequisite>:** <milyen állapotból indul: felhúzott stack, seed, bejelentkezett user, korábbi `TS-NN` eredménye>

| # | Lépés | Hívás | Elvárt eredmény |
|---|---|---|---|
| 1 | <mit csinálunk> | `<szó szerint futtatható hívás>` | `<konkrét, ellenőrizhető válasz>` |

**<field:f_cleanup>:** <mit kell utána leállítani vagy visszaállítani>

**Kitöltési szabályok:**
- **`<field:f_what_we_test>` — állítás, nem téma (TD7).** Ez a sor mondja meg, **mit ellenőriz** a forgatókönyv és **miért**: a viselkedés egy eldönthető állításként (*„öt egyidejű kérésből pontosan egy újítja meg a tokent, a többi a meglévővel szolgál ki"*), plusz az elfogadási feltétel vagy kockázat, amit igazol. **A fejléc megismétlése nem elég** („konkurencia-teszt", „az `/init-hash` tesztelése") — abból a 06/07 fázisban nem derül ki, hogy egy bukás valódi hiba-e vagy rossz teszt. A kapu ezt méri (TS2).
- **`DoD-NN` a fejlécben — kötelező és kétirányú (TS5).** Minden forgatókönyv megnevezi, mely DoD-pontokat igazolja, és **minden `DoD-NN`-hez tartoznia kell legalább egy forgatókönyvnek**. A kapu mindkét irányt méri.
- **Hívás oszlop — szó szerint futtatható.** REST-nél teljes `curl`: ige, teljes URL porttal, fejlécek, konkrét request body. Nem REST teszt is ide tartozik ugyanebben a formában: UI-lépés (mire kattintunk, mit írunk be), CLI-parancs, DB-lekérdezés. **Hivatkozás nem hívás** — „lásd a `<sec:e2e_infrastructure>` szekciót" nem futtatható.
- **Elvárt eredmény oszlop — konkrét és ellenőrizhető.** Státuszkód **és** a válasz azonosítható része (mezőnév, érték, payload-részlet, UI-elem szövege). A „sikeresen lefut" / „hibát ad" / „a várt eredményt adja" **tilos**: nem eldönthető. A kapu kemény padlója (TS3): legalább egy backtickes érték vagy szám.
- **Teszt-userek, jelszavak, URL-ek, portok, azonosítók: literálisan.** A `<sec:environment_coords>` (KO1) értékeit **ide be kell írni**, nem hivatkozni rájuk — placeholder tilos (TS4), a hiányzó adat `plan-questions.md` kérdés. Credential-t a titok-szabály (TC5) szerint: dev-hatókörű teszt-user igen, klaszter/registry/IAM credential soha.
- **Az adatfolyam legyen követhető.** Ha egy lépés kimenetét a következő használja, írd ki, **melyik mezőt melyik változóba** (`a válasz `response.initHash` mezője → `$INIT_HASH``).
- **Számozás:** `TS-01`-től, hézagmentesen és egyediül (TS6). Javításnál a meglévő azonosítókat **ne számozd újra** — az újak a lista végére kerülnek.
- **🔴 REST-hívásnál a `.http` blokk is kötelező (TS8).** A lépés-tábla `Hívás` cellája a **gépnek** szól (egysoros, futtatható `curl`/parancs) — egy embernek viszont a fejlécekkel és a body-val együtt kell látnia a kérést, kattintható alakban. Ezért minden olyan `TS-NN` blokk végén, amelynek van REST-lépése, áll egy ```http infostringes kódblokk (VSCode REST Client / IntelliJ `.http` alak) **ugyanazokkal az értékekkel**, a lépés számára hivatkozva:

```http
@tmp = https://tmp.dev.example.com
@legacy = https://legacy.dev.example.com

### 3. lépés — munkamenet nyitása (a válasz `sid` mezője → a 4. lépés `{{sid}}` változója)
POST {{legacy}}/api/v13/login/login
Content-Type: application/json

{"email": "teszt.user@example.com", "password": "Pass1234", "clientId": "INTERNETBANK", "sessionId": "session-1"}

### 4. lépés — cache inicializálás
POST {{tmp}}/init-hash
Authorization: Bearer {{jwe}}
Content-Type: application/json
X-Correlation-Id: 11111111-1111-1111-1111-111111111111

{"productType": "LOAN"}
```

  A blokk **nem helyettesíti** a lépés-táblát (a kapu TS3-a a tábla celláit méri), és fordítva sem: a kettő ugyanaz a hívás két közönségnek. Ha eltérnek, az egyik hibás — javítsd. Ez a forma megy tovább változtatás nélkül a `bs-manual-test-plan` `TG-NN` csoportjaiba (MT11), és a kapu mindkét irányban méri (TS8): `curl` `.http` nélkül és `.http` `curl` nélkül is megállapítás.
- **A bootstrapping nem ide tartozik:** a stack indítása, a token-szerzés és a deploy a `<sec:e2e_infrastructure>` szekcióban él (TP3); itt az `<field:f_prerequisite>` sor **hivatkozik** rá.

### <sec:machine_run_table> (run-tests.py) — **kötelező (TP4)**

> **🔴 Miért kötelező:** a fenti próza az embernek szól, ez a tábla a **`run-tests.py`** szkriptnek. Ha megvan, a 07-validate a teszteket **szkripttel** futtatja, és a nyers teszt-log soha nem kerül LLM-kontextusba — ez a fázis legnagyobb token-tétele. Ha hiányzik, a 07 a drágább `test-runner` subagentre esik vissza. A tábla nem helyettesíti a prózát: **ugyanazok a parancsok**, gépi alakban.

| Kategória | Típus | Előfeltétel | Parancs | Eredményfájl | Formátum | Takarítás | <field:f_environment> | <field:f_phase> |
|---|---|---|---|---|---|---|---|---|
| unit | gyors | — | `<szó szerinti parancs, gépi riporterrel>` | `junit.xml` | junit | — | lokális | <status:phase_both> |
| integrációs | gyors | — | `<parancs>` | `<fájl>` | junit | — | lokális | <status:phase_both> |
| e2e | nehéz | `<a cél elérhetőségi probe-ja; stack indítása>` | `<parancs a cél-hosttal>` | `<fájl>` | junit | `<lebontás>` | `<a cél-környezet neve>` | <status:phase_validate> |

**Kitöltési szabályok:**
- **Típus:** `gyors` (unit/integrációs/typecheck — a VD10 könnyű körben is fut) vagy `nehéz` (E2E/regresszió — csak teljes körben).
- **Előfeltétel / Takarítás:** `;`-vel több parancs is felsorolható, a `## <sec:e2e_infrastructure>` szekció bootstrapping-lépéseivel **szó szerint** egyezően. A takarítás akkor is lefut, ha a futtatás elszállt.
- **Parancs:** lehetőleg **gépi riporterrel** (`--reporter=junit`, `--junitxml=…`, `-Dsurefire.reportFormat`) — így a darabszámok és a bukott tesztnevek pontosan kinyerhetők, és nem regexből becsültek.
- **Eredményfájl:** a repóhoz képest relatív útvonal; a szkript a kör-mappába másolja bizonyítéknak.
- **Helyőrzők — kettő van, két különböző bázissal (TR5/c). Ne keverd őket:**
  - `{round}` → a repó gyökeréhez képest relatív **teljes** kör-mappa (`specs/cycle-NN-<cycle-name>/test-report/validate/round-02`). Ezt írd oda, ahol a parancs a repó gyökeréből indul: `--outputFile={round}/junit.xml`, `--alluredir={round}/e2e/allure-results`.
  - `{phase}` → a `test-report/`-hoz képest relatív **fázis-mappa** (`validate/round-02`). Ezt írd oda, ahol a `conventions.md` riport-parancsa a `<phase-dir>` helyőrzőt vagy egy `REPORT_PHASE_DIR`-szerű környezeti változót vár: `REPORT_PHASE_DIR={phase} npm run test:pw`.
  - **Tilos a `{round}` elé `test-report/`-ot írni** (`…/test-report/{round}`) — a `{round}` már tartalmazza. Az így keletkező dupla prefix rekurzív `test-report/specs/…` riport-fát épít; a `run-tests.py` a futtatás előtt ellenőrzi, és `exit 3`-mal megáll.
- **Formátum:** `junit` (ajánlott) vagy `text` (a stdout-ból regexszel számol — gyengébb bizonyíték).
- **🔴 <field:f_environment> — kötelező minden sorban (EV2–EV5).** Ide `lokális` vagy a cél-környezet neve kerül. Ha nem `lokális`:
  - a **`Parancs` cellának literálisan tartalmaznia kell a cél-hostot** (env-változóval vagy kapcsolóval, pl. `PLAYWRIGHT_BASE_URL=https://app.dev.example npx playwright test`) — **a célpont nem rejtőzhet konfigfájlban** (EV3). Egy `test:playwright:dev-e2e` nevű script configjában simán állhat `localhost`: **a parancs neve nem bizonyíték, a cím az**;
  - az **`Előfeltétel` cellába kötelező egy elérhetőségi probe** ugyanarra a hostra (`curl -fsS https://app.dev.example/health`) — a `run-tests.py` az előfeltételt futtatja, és bukásakor a kategória FAIL, tehát **egy le sem futó deploy nem tud zöldre pipálódni** (EV4);
  - `localhost` / `127.0.0.1` a parancsban vagy az előfeltételben **tilos** (EV5) — a `run-tests.py` ilyenkor `exit 4`-gyel megáll, futtatás nélkül.
- **<field:f_phase> — melyik FÁZIS futtatja (PH1).** Három érték: `<status:phase_implement>` (csak a 06 fázis dev-hurka futtatja), `<status:phase_validate>` (csak a 07-validate), `<status:phase_both>` (mindkettő). **Az üres cella `<status:phase_both>`-t jelent** — a hallgatás soha nem jelent kihagyást, tehát a jelöletlen kategória mindenhol lefut. A `run-tests.py` a `--phase` kapcsolóval szűr: a `06` `--phase <status:phase_implement>`-tel, a `07` `--phase <status:phase_validate>`-tel hívja.
  - **Mikor `<status:phase_implement>`:** olcsó, gyors dev-hurok ellenőrzés, amit a validálásban egy bővebb kategória úgyis lefed (pl. külön `lint` vagy `typecheck` sor a teljes unit-készlet mellett).
  - **Mikor `<status:phase_validate>`:** drága vagy telepített környezetet igénylő kategória (E2E, regresszió, dev-deployra futó teszt), amit a 06 dev-hurkában nem érdemes vagy nem lehet futtatni.
  - **🔴 `DoD-NN`-t bizonyító teszt sosem lehet `<status:phase_implement>`-only.** A `07` a `dod-check.py`-jal a **validálási kör** bizonyítékaiból joinol: ami csak a 06-ban futott, arról a DoD-nak nincs bizonyítéka, és a pont `?`-lel marad. Ha egy kategória a DoD-hoz kell, `<status:phase_validate>` vagy `<status:phase_both>` a helyes érték.
- **Üres cella:** `—`.
- Ha egy kategória **szándékosan nem létezik** ebben a projektben, ne vedd fel a táblába, és a prózában írd le, miért.

> **⚠ Platformfüggő parancsok (Windows).** A `run-tests.py` a parancsokat a rendszer alapértelmezett shelljével futtatja: Linux/macOS → `/bin/sh`, **Windows → `cmd.exe`**. Ami emiatt eltérhet: az egyszeres idézőjel (`'…'`) a cmd-ben **nem** string-határoló, a környezeti változó `$VAR` helyett `%VAR%`, a `&&`/`||` viszont mindkettőn működik. Ha a projekt vegyes platformon fut, olyan parancsot írj a táblába, ami mindkettőn helyes (jellemzően egy `npm run …` / `mvn …` / `pytest …` hívás az) — a shell-specifikus lépéseket (stack indítása, health-poll) tedd egy scriptbe, és azt hívd. Az `<field:f_prerequisite>`/`Takarítás` oszlop `;` elválasztóját a **szkript** bontja fel és futtatja külön parancsként, tehát az nem shell-szintaxis: platformfüggetlen.

### <sec:e2e_infrastructure>

_(Kitöltése kötelező — a `plan-questions.md`-ben megállapodott szint alapján.)_

_**A recept-adatok helye (TC1/a):** a `specs/test-conventions.md` 1. szekciójából beemelt **összes** végrehajtáshoz szükséges adat ebbe a szekcióba kerül, szó szerint: komponens-koordináták (repo-útvonal, image-név, registry-cél, namespace/pod), URL-ek és portok, health endpoint, **teszt-userek és jelszavaik**, scope/client-id és egyéb paraméterek, **példa hívások (`curl`)**, build/push/restart parancsok, előfeltételek és a lépések sorrendje. **Hivatkozás nem helyettesíti az adatot, és placeholder nem használható** — a `test-runner` csak ezt a fájlt látja. Credential-t ide is csak a regiszter titok-szabálya (TC5) szerint írj: dev-hatókörű teszt-user igen, klaszter/registry/VPN/IAM/token credential soha — arra pointer megy._

> **🔴 KÖRNYEZET-FELKÉSZÍTÉS (bootstrapping) — kötelező tartalom (TP3).** A teszt **nem a hívásláncnál kezdődik**, hanem ott, hogy a környezet futásra kész és van érvényes hitelesítés. Minden ilyen előfeltételt **szó szerinti, futtatható parancsként** ide kell írni — a `test-runner` üres gépet feltételez, és semmit nem tud kikövetkeztetni. Tételesen:
>
> | Előfeltétel | Mit kell a plan-be írni |
> |---|---|
> | **Hitelesítés / token-beszerzés** | A token megszerzésének **teljes hívása**: ige, végpont, fejlécek, request body a **konkrét teszt-userrel**, a válaszból kinyerendő mező, és hogy melyik változóba kerül (`$JWE`, `$ACCESS_TOKEN`). Külön a **user** és az **S2S/technikai** tokenre, ha mindkettő kell. Mock login helper esetén is: a **hívása**, ne a puszta létezése. Lejárat/újrakérés, ha a futás hossza indokolja. |
> | **Stack indítása** | A konkrét indító parancs (env-indító script / compose up), a **health check** (mely URL-t mikorra kell `200`-nak adnia), a **várakozási feltétel** (ne `sleep`, hanem poll), és a leállítás/takarítás parancsa. |
> | **Egyedi komponens build + deploy** (plugin, SPI, custom image, patchelt konténer) | A **teljes folyamat parancsonként**: forrás helye, build (`mvn`/`npm`/`docker build`), image-név **egyedi taggel**, push a registrybe, a deployment/pod cseréje, a kiállás ellenőrzése (`rollout status` + health/verzió-endpoint), és a **rollback** (mi az eredeti azonosító, hogyan olvasható ki, mivel állítható vissza). Osztott környezetben ehhez a fenti `[!CAUTION]` blokk mindhárom feltétele is kell. |
> | **Seed / kezdőállapot** | Séma, tesztadat, realm-import, kliens/scope létrehozása — a konkrét paranccsal vagy fájllal. |
> | **Hálózati elérés** | VPN/proxy/`oc login`/kubeconfig szükségessége — pointerrel a credentialre (TC5), soha nem a titokkal. |
> | **Sorrend** | A fentiek **végrehajtási sorrendje** és egymásra épülése, hogy a `<sec:execution_order>` szekcióba egy az egyben átvihető legyen. |
>
> **Önteszt erre a szekcióra:** *„Egy friss gépen, a repo klónozása után, kizárólag ezt a plant olvasva le tudom futtatni a teszteket — token-szerzéssel, felhúzott stackkel, deployolt egyedi komponenssel — anélkül, hogy bármit kitalálnék vagy máshonnan kikeresnék?"* Ha nem, a szekció hiányos. Ami hiányzik és nincs a `test-conventions.md`-ben sem, azt a **korábbi ciklus planjéből kell áthozni** (TP3/a) vagy a felhasználótól megkérdezni.

> [!IMPORTANT]
> **Szigorú konténerizációs szabály:** A tesztkörnyezet konzisztenciája és gépfüggetlensége érdekében az E2E és integrációs tesztekben részt vevő összes háttér-szolgáltatást és komponenst kötelező konténerben (pl. Docker/Podman) futtatni. Tilos a gazdagépen helyileg futó natív szolgáltatásokra hagyatkozni (kivéve magát a tesztet futtató keretrendszert/böngészőt).

> [!IMPORTANT]
> **Teljes automatizáció és tiszta állapot (Clean Slate):** A konténereket úgy kell megtervezni és elindítani, hogy a teszt futtatása teljesen a nulláról (0-ról) automatikusan konfigurálja be őket a megfelelő állapotra:
> - *Példák:* Adatbázis esetén a konténer indításakor automatikusan fel kell húzni a sémát és be kell tölteni a tesztadatokat (seeding). Keycloak (vagy bármely külső Identity Provider) esetén a konténer indulásakor automatikusan be kell tölteni a realm konfigurációt, és létre kell hozni a szükséges klienseket és tesztfelhasználókat (pl. exportált realm import JSON-ön vagy admin API-n keresztül).
> - **Erőforrások takarítása (Cleanup):** A tervnek explicit tartalmaznia kell, hogy a tesztek futása után hogyan történik meg a konténerek és ideiglenes erőforrások leállítása és teljes törlése (pl. a teszt keretrendszer global teardown hookja, `trap 'cleanup' EXIT`, compose down), hogy ne maradjon hátra futó konténer vagy hálózati szemét.

> [!CAUTION]
> **Osztott (nem eldobható) környezetben végzett destruktív művelet — jóváhagyás, immutable tag, rollback.** Ha a terv **közös** környezetet módosít — deployment/pod csere osztott klaszterben vagy namespace-ben, image push közös registrybe, seed/törlés osztott adatbázisban, konfiguráció felülírása —, akkor a plan-ben **mindhárom** kötelező:
> 1. **Jóváhagyás:** a művelet `<status:scope_shared_remote>` hatókörűként megjelölve, és a `plan-questions.md`-ben rögzítve, hogy a felhasználó jóváhagyta (kollégák munkáját érintheti).
> 2. **Immutable azonosító:** a kiadott artefaktum **ne írjon felül meglévő azonosítót** (pl. ne pusholjuk újra ugyanazt az image-taget) — verziót kell léptetni vagy egyedi (build-azonosítós) taget használni. **Egy felülírt tag után nincs mihez visszaállni.**
> 3. **Rollback-terv:** konkrétan leírva, mi az eredeti állapot (a jelenlegi image/verzió/konfig **kiolvasásának parancsával**), és milyen paranccsal állítható vissza, ha az ellenőrzés elbukik.
> 4. **Állapot-perzisztencia:** ha a lépések **egymás állapotára** épülnek (mentett eredeti azonosító, generált egyedi tag), az az állapot **nem maradhat shell-változóban**. A végrehajtás lépésenként külön shellben történik, tehát a `VAR=...` / `export VAR=...` a következő lépésre **elpárolog**, és a rollback üres paraméterrel futna. Írd elő, hogy az állapot **fájlba** kerüljön (pl. `.rollback-state`), és a későbbi lépések onnan olvassák — vagy vond egyetlen lépésbe a függő parancsokat.
>
> Ha bármelyik hiányzik, a művelet nem tervezhető be — vedd fel kérdésként a `plan-questions.md`-be.

> [!CAUTION]
> **Komplex konfigurációk kezelése:** Ha egy tesztelendő komponens konténerizálása, hálózati elérése (pl. localhost vs. konténeres hálózat) vagy kezdeti adatfeltöltése komplex vagy nem egyértelmű, az ágens **köteles megállni és a felhasználó segítségét kérni** (a `plan-questions.md`-be felvett kérdéssel), hogy közös tervezéssel alakítsák ki a tesztkörnyezetet.

**Fontos szabály E2E környezet indítására:** mindig platformfüggetlen környezet-indító szkriptet kell tervezni és használni (a `conventions.md` által megadott eszközzel — pl. Python env-indító script), amely felhúzza a szükséges container stack-et vagy lokális service-eket, majd a teszt keretrendszer (pl. a `conventions.md`-ben megadott browser E2E eszköz global setupja) ezen keresztül indítja a környezetet. Soha nem fordulhat elő, hogy egy teszt manuális környezetindítás hiánya miatt bukik el.

- **E2E szint:** valódi konténerizált stack / részleges mock / teljes mock
- **Futó service-ek:** melyik komponensek futnak valódi konténerként (a `conventions.md` által megadott E2E compose fájlban)
- **Mock indoklás:** ha van mockolt service, miért nem valódi — dokumentált döntés
- **Frontend tesztek:** ha van web komponens, a `conventions.md` által megadott browser E2E eszköz
- **Backend tesztek:** a `conventions.md` által megadott backend teszt eszköz
- **E2E compose fájl:** tervezett service-ek, portok, health check-ek, indítási sorrend (a `conventions.md` által megadott néven)

### <sec:regression_impact>

_Ha a ciklus meglévő kódot módosít: explicit lista az érintett meglévő tesztfájlokról és E2E scriptekről, és rövid indoklás, hogy miért érintett. Ez a lista lesz a tasks fázis regresszió-frissítési tasljainak és a validate fázis regressziós futtatásának a bemenete._

_Ha nincs regressziós érintettség, ezt explicit írd ki: „Nincs regressziós érintettség."_

_**Származtatás a regiszterből (TC1):** ha létezik `specs/test-conventions.md`, ezt a táblát **ne a nulláról találd ki** — vesd össze a ciklus által módosított komponenseket/fájlokat a regiszter 2./3. szekciós tételeivel, és minden érintett tétel kerüljön a táblába (a `Miért érintett` oszlopban a tétel ID-jával). Ide azok a „ne törjön el" jellegű tételek is bekerülnek, amelyek a `spec.md`-be nem mennek át, mert nem a ciklus célja. A futtatáshoz szükséges recept-adatokat a fenti `<sec:e2e_infrastructure>` szekció tartalmazza._

| Tesztfájl / E2E script | Miért érintett |
|---|---|
| `test/unit/...` | ... |
| `test/integration/cycle-XX-....sh` | ... |
| `test/e2e/auth-login.spec.ts` | test-conventions I01 — a módosított middleware ezen a flow-n fut |

## <sec:test_specification>

_A tesztelési megközelítés összefoglalása: mit mockolunk, mit futtatunk valódi konténerben, milyen szinteken tesztelünk — mielőtt felsorolod a konkrét eseteket._

### 🔴 Teszt-azonosítók — a plan és a tasks közös névtere (TI1)

A `tasks.md` **erre a két azonosítóra hivatkozik**, és a `07` bizonyíték-joinja is ezekkel dolgozik. Ezért a ciklusban **pontosan két teszt-azonosító család** él, mindkettő ciklus-szinten egyedi és hézagmentes:

| Azonosító | Mit jelöl | Hol keletkezik |
|---|---|---|
| `TS-NN` | végrehajtható **forgatókönyv** (integrációs / E2E / kézi), lépés-táblával | `<sec:plan_test_scenarios>` |
| `TC-NN` | egyetlen **teszteset** a teszt-táblákban (jellemzően unit) | `<sec:unit_tests>` / `<sec:integration_tests>` / `<sec:e2e_tests>` |

- **`TC-01`-től folytonosan, a CIKLUS egészére** — nem fájlonként újrakezdve, és **nem** `TC-<modul>-01` alakban. Egy azonosító egy tesztesetet jelöl, akárhány tesztfájl van.
- **Az azonosító soha nem változik** a ciklus során (a `tasks.md` és a `07` naplója hivatkozik rá). Utólagos beszúrás a következő szabad számot kapja; törölt szám nem használható újra.
- **Minden `TC-NN` és `TS-NN` gazdát kap a `tasks.md`-ben** (`TT1`): egy taskot, amely megírja, és egy `[CHECK]`-et, amely lefuttatja. Ezért a **granularitás számít**: egy `TC-NN` akkora legyen, amit egy teszt-futtató parancs **külön is le tud futtatni** (`-t "<név>"`, `-k <minta>`), különben a futtató checkbox nem tud rá szűrni.

### <sec:spec_coverage> (kötelező tábla)

_A spec `<sec:test_specification>` szekciójának minden esete és a `<sec:definition_of_done>` minden pontja **legalább egy** plan-tesztesetre képződik le. A tábla nélkül a plan nem zárható le._

| Spec forrás | Plan teszteset(ek) | Szint |
|---|---|---|
| _spec teszt-eset megnevezése / `test-conventions` tétel ID / `DoD-NN`_ | `TS-03`, `TC-01`, `TC-02` | unit / integrációs / E2E |

_**A `Plan teszteset(ek)` cella kötelezően megnevez legalább egy `TS-NN` forgatókönyvet (TS7)** — a `TC-…` azonosító önmagában nem elég: az csak egy tábla-sor, a `TS-NN` a végrehajtható forgatókönyv. Kivétel csak az az eset, amely ebben a ciklusban nem tesztelhető: ott a cella az indoklást hordozza (pl. „nem automatizálható — kézi `[CHECK]` a `<sec:execution_order>` 7. lépésében"), és a kapu ezt megjegyzésként engedi át._

_**A `Szint` oszlop nem szabad választás:** a viselkedés természete dönti el. **Ha a DoD/spec felhasználói felületen megfigyelhető viselkedést ír le** (gomb, megjelenő elem, képernyő-állapot), akkor **browser E2E kötelező** — az API-szintű E2E nem helyettesíti. Ha a projektben nincs browser E2E eszköz, az `plan-questions.md` kérdés, nem néma leminősítés._

### <sec:reverse_coverage> — scope-kapu (SC1, kötelező tábla)

_Minden plan-képességnek **vissza kell vezethetőnek lennie** a specre. Sorold fel a plan érdemi képességeit/szekcióit, és mindegyikhez a spec-forrást:_

| Plan-képesség / szekció | Spec-forrás (követelmény vagy `DoD-NN`) |
|---|---|
| _`[P-REDIS]` Redis sentinel/cluster + TLS_ | _DoD-02_ |

_**Az első oszlop viselje a szekció `[P-…]` azonosítóját** (nem sorszámot, nem puszta címet), a második pedig a `DoD-NN` azonosítót, ahol az a spec-forrás. Ezen a két oszlopon fut a `05-analyze` mechanikus kapujának lefedettségi lánca (`DoD-NN → [P-…] → task`): ha a sor csak szabad szöveget tartalmaz (`§3.2 …`), a lánc gépiesen nem zárható, és a kapu `S3` megállapítást ad. Ha egy képességhez tartozó szekciónak nincs `[P-…]` azonosítója, az a PID1 hiánya — előbb adj neki ID-t._

_**Ha egy sorhoz nincs spec-forrás, három lehetőség van — negyedik nincs:**_
1. _**vissza a 02-be:** a képesség kell → kérj rá DoD-pontot (jelezd a felhasználónak, mi hiányzik; a spec-et magad nem írod);_
2. _**<sec:out_of_scope>:** a plan `<sec:goal_and_approach>` szekciójában explicit kimondod, hogy nem készül el ebben a ciklusban, és **kiveszed a plan-ből**;_
3. _**`plan-questions.md` kérdés,** ha nem tudod eldönteni._

_Spec-forrás nélküli, „hasznosnak tűnő" képesség a plan-ben **tiltott**: teszt és elfogadási feltétel nélkül fejlesztésre kerülne._

_Ha egy spec-beli eset ebben a ciklusban **nem** tesztelhető, az sor marad, a „Plan teszteset" oszlopban indoklással (pl. „nem automatizálható — manuális `[CHECK]` a `<sec:execution_order>` 7. lépésében"). **Üresen hagyni vagy kihagyni nem lehet.**_

### Lifecycle

| Szint | Mikor írjuk | Mikor futtatjuk | Mit blokkol |
|---|---|---|---|
| Unit | implementáció ELŐTT | minden commit | RED→GREEN ciklus |
| Integrációs | implementáció UTÁN | service stack up | ciklus lezárás |
| E2E | implementáció UTÁN | teljes stack up | ciklus lezárás |

### Teszt-artefaktum adatlap (TA1) — minden tesztfájl fejlécében kötelező

> **🔴 Miért kötelező:** egy tesztfájl megtervezése **nem ér véget a tesztesetek felsorolásával**. Ha nincs kimondva, melyik **kerettel** készül, milyen **paranccsal futtatható önmagában**, milyen **fixture / mock / tesztadat** kell hozzá, és melyik **teszt-függvény** melyik esetet fedi, azt az implementáló kitalálja — a `[CHECK]` task pedig más állományt fog futtatni, mint amit terveztél, vagy a teszt egyedül nem is futtatható. A `<sec:unit_tests>`, `<sec:integration_tests>` és `<sec:e2e_tests>` minden `#### <tesztfájl path>` fejléce alatt, a tesztesetek ELŐTT ez az adatlap áll:

```md
#### `test/unit/token-store.test.ts` (új)

**<field:f_what_it_checks>:** a megosztott tárolóból olvasó token-elérés viselkedése: üres tárolónál nincs találgatott érték, párhuzamos olvasóknál pedig pontosan egy megújítás fut (DoD-01, DoD-04).
**<field:f_test_run>:** `node:test` + `tsx` — `npx tsx --test test/unit/token-store.test.ts`
**<field:f_test_fixtures>:** `test/fixtures/s2s-token.json` (új fájl — a `<sec:planned_changes>` `[P-30-09]` bejegyzésében): egy lejárt és egy érvényes `S2STokenEntry`; a Redist az `ioredis-mock` helyettesíti (meglévő függőség)
**<field:f_test_cases>:** `returns null on empty store` → `TC-01` · `refreshes once for 5 parallel readers` → `TC-02`, a `TS-01` 5. lépése
**<field:f_prerequisite>:** nincs külső előfeltétel; env: `REDIS_KEY_NAMESPACE=dsp`
```

**Kitöltési szabályok:**
- **<field:f_what_it_checks> — a tesztfájl célja, állításként (TD7).** Mit ellenőriz ez az állomány **együtt**, és melyik `DoD-NN`-t szolgálja. Nem a fájlnév kifejtése („a token-store tesztjei"), hanem a viselkedés, amiért létezik.
- **<field:f_test_run> — a keret ÉS az erre az egy fájlra szűkített, szó szerint futtatható parancs.** Ugyanez a parancs kerül a `[CHECK]` taskba és a `<sec:verification_strategy>`-be. A `<sec:machine_run_table>` kategória-szintű parancsa ennél bővebb lehet (a teljes suite), de nem mondhat ellent neki: a **futtatott állomány** ugyanaz.
- **Minden fixture, mock, seed és tesztadat, ami még nem létezik, egyben ÚJ FÁJL** — tehát útvonallal szerepelnie kell a `<sec:planned_changes>`-ban is, különben senki nem hozza létre. A tartalmát itt kell megadni (vagy a generáló parancsot). Ha nincs ilyen, a cella `—`.
- **A teszt-függvények nevei nem opcionálisak.** Ez a leképezés köti a tervet a `TC-…` esetekhez és a `TS-NN` forgatókönyvekhez: ebből derül ki, hogy egy forgatókönyv melyik lépését melyik automata teszt fedi le, és mi marad kézi ellenőrzésnek. Új tesztnél a **függvénynév maga a specifikáció** — abból kell látszania, mit állít.
- **Bővítésnél (`(bővítés)`) ugyanez:** melyik meglévő teszt-függvény módosul és miért, milyen új függvények jönnek be, és változik-e a futtató parancs.
- **A setup/teardown, a szükséges env-változók és a külső előfeltételek** (konténer, mock szerver, hálózat, seed) az `<field:f_prerequisite>` sorba kerülnek, szó szerinti paranccsal. A `<sec:e2e_infrastructure>` bootstrapping-lépéseire hivatkozni csak akkor lehet, ha ott a parancs szó szerint le van írva.

### <sec:unit_tests>

_Izolált tesztek: függőségektől elszigetelt üzleti logika, függvények, osztályok. Minden külső komponenst (adatbázis, hálózat, külső service) mockolni kell — rendkívül gyors, determinisztikus. Kötelező happy path ÉS negatív tesztek (hibás bemenet, hiányzó paraméter, jogosultsági hiba, timeout) minden komponenshez. Komponensenként egy alfejezet. Táblázatos formátum: TC-ID, Scenario (mi a helyzet), Input (mi érkezik), Elvárt kimenet (HTTP státusz + errorCode ahol a spec hibamátrixa definiálja + kulcs response mezők)._

#### `<tesztfájl path>` (új / bővítés)

**<field:f_what_it_checks>:** _<mit ellenőriz ez a tesztfájl, állításként + a `DoD-NN`>_
**<field:f_test_run>:** _<keret + az erre a fájlra szűkített, szó szerint futtatható parancs>_
**<field:f_test_fixtures>:** _<fixture / mock / tesztadat útvonallal és tartalommal, vagy `—`>_
**<field:f_test_cases>:** _<teszt-függvény neve → `TC-NN` / `TS-NN` leképezés>_

| TC-ID | <field:f_what_it_checks> | Scenario | Input | Elvárt kimenet |
|---|---|---|---|---|
| TC-01 | _<a viselkedés állításként + a `DoD-NN`>_ | ... | ... | ... |

_**A `<field:f_what_it_checks>` oszlop kötelező (TD7):** minden unit-eset kimondja, **mit ellenőriz** — a viselkedés eldönthető állításként, nem a bemenet megismétlése. „Hibás input" nem cél; a cél: *„hiányzó `expiresAt` mezőnél a betöltés `ConfigError`-t dob, nem `0`-ra esik vissza (DoD-02)"*._

> **🔴 A SPEC TESZTESETEIT ÁT KELL HOZNI (TP1) — nem a `tasks.md` és nem az implementáló dolga.** A spec `<sec:test_specification>` szekciójában és a `<sec:definition_of_done>`-ban leírt esetek **nem** „túl részletesek a plan-hez": pontosan ide tartoznak, mert a `test-runner` **kizárólag a `plan.md`-t olvassa** — a spec-et nem, a `test-conventions.md`-t nem, a `tasks.md`-t nem. Ami itt nem szerepel, azt **senki nem fogja lefuttatni**.
>
> - **Mindegyik spec-eset megjelenik** a fenti `<sec:spec_coverage>` táblában és **kifejtve** a megfelelő teszt-szint alatt (unit tábla / integrációs vagy E2E lépéslista).
> - **A spec absztrakciós SZINTJÉT kell feloldani — a TARTALMÁT megőrizni (KX3):** a spec szimbolikus koordinátái (`{PUBLIC_BASE_URL}`) mellé itt kerül a **konkrét érték**, a viselkedés-leíráshoz a **konkrét HTTP ige, végpont, fejléc, request body és elvárt válasz** (lásd „Hivatkozás-feloldás"). A részletesség ilyenkor **növekszik, soha nem csökken**: a spec kidolgozott blokkjai (OpenAPI, teljes payload, hibamátrix, többlépéses forgatókönyv) **szó szerint, csonkítás nélkül** kerülnek át.
> - **A `test-conventions.md` receptjeit fizikailag be kell másolni (TC1/a):** az `R01`/`I03` típusú **hivatkozás önmagában nem elég** — a recept parancsai, URL-jei, payloadjai szó szerint ide kerülnek. A tétel ID-t megtarthatod **a bemásolt tartalom mellett**, nyomkövetésként.
> - **Ne halaszd a részletet a 04-re.** A `tasks.md` a plan tesztesetére **hivatkozik** (`TC-XX-E-01`), nem újra leírja — tehát ha itt hiányzik, ott sem lesz meg.

> **🔴 SZIGORÚ TESZT-ÖNHORDÓSÁGI SZABÁLY.** Minden integrációs és E2E tesztesetnél **szövegesen, lépésről lépésre ki kell fejteni a teljes hívásláncot** — az aktuális ciklusra, a nulláról. **Tilos** hivatkozással helyettesíteni a lépések leírását:
>
> - ❌ *„a cycle-23 mintájára"*, *„mint a `cycle_23_mock_test.py`-ban"*, *„a meglévő teszt logikája szerint"*;
> - ❌ *„a folyamatot a spec szekvenciadiagramja írja le"* — **a `test-runner` a spec-et nem olvassa**, tehát az ábra számára nem létezik;
> - ❌ *„a szokásos fejlécekkel"*, *„a megfelelő tokennel"*, *„és így tovább"*.
>
> **Ez nem tiltja a hivatkozást ott, ahol jogos:** a `<sec:regression_impact>` táblában **kell** megnevezni a meglévő tesztfájlokat (az a scope, nem a lépések leírása), és egy meglévő fixture-re/helperre is hivatkozhatsz **útvonallal**, ha a lépés maga ki van fejtve. A tilalom az, hogy a hivatkozás **a lépések helyére** kerüljön.
>
> **Miért:** a `test-runner` subagent kizárólag ebből a szekcióból dolgozik. Egy „a korábbihoz hasonlóan" mondat számára **végrehajthatatlan** — a teszt vagy nem fut le, vagy találgatásból mást fog ellenőrizni, mint amit terveztél.

**Minden lépésnek kötelezően tartalmaznia kell:** HTTP ige · teljes végpont (szimbolikus host + konkrét útvonal) · a szükséges **fejléceket** (különösen az `Authorization` típusát: user / S2S / legacy) · a küldött **request body-t konkrét mezőkkel** · az elvárt **HTTP státuszt** és a **kulcs válasz-mezőket**. Ahol a hívás közvetlenül futtatható, adj **példa `curl`-t** is.

### <sec:integration_tests>

_Modulok közötti kapcsolatok, adatbázis-műveletek, belső service-hívások. Mock szerverek és/vagy lokális konténerizált adatbázis megengedett. Flow-alapú, szekvenciális lépéslista._

#### `<script path>` (új / bővítés)

**<field:f_what_it_checks>:** _<mit ellenőriz ez a tesztfájl, állításként + a `DoD-NN`>_
**<field:f_test_run>:** _<keret + az erre a fájlra szűkített, szó szerint futtatható parancs>_
**<field:f_test_fixtures>:** _<fixture / mock / tesztadat útvonallal és tartalommal, vagy `—`>_
**<field:f_test_cases>:** _<teszt-függvény neve → `TC-NN` / `TS-NN` leképezés>_
**<field:f_prerequisite>:** _<mi kell a lépések előtt: felhúzott stack, seed, bejelentkezés — a konkrét paranccsal>_

**Kész példa a KÖTELEZŐ részletességre** (ilyen sűrűségű legyen minden lépés, ne egysoros):

1. **Legacy user token beszerzése** — `POST {LEGACY_LOGIN_URL}/api/v13/login/token`
   - Fejlécek: `Content-Type: application/json`
   - Body: `{"username": "test-user", "password": "Test123!"}`
   - Elvárt: `200`, a válasz `token` mezője JWE formátumú → eltárolva `$JWE` néven a további lépésekhez.
2. **Cache inicializálás** — `POST {TMP_URL}/init-hash`
   - Fejlécek: `Authorization: Bearer $JWE` (legacy), `Content-Type: application/json`
   - Body: `{"productType": "LOAN", "channelType": "MOBILBANK"}`
   - Elvárt: `200`, body: `{"initHash": "<uuid>", "status": "SUCCESS"}` → `$INIT_HASH`.
   - **Oldalhatás-ellenőrzés:** a Redisben létrejön a `tmp:tokens:sid:<sid>` kulcs (TTL > 0).
3. **Folyamatindítás** — `POST {TMP_URL}/rtm/api/runtime/app/{appId}/build/{buildId}/process-name/{processName}/start`
   - Fejlécek: `Authorization: Bearer $JWE`
   - Body: `{"initHash": "$INIT_HASH", "technicalData": {"languageCode": "en"}}`
   - Elvárt: `200`, body: `{"response": {"processInstanceId": "<uuid>"}, "status": "SUCCESS", "errors": []}`
   - **Ellenőrzés a mockon:** a hívás a **user** access tokennel érkezett (nem S2S) — a mock ezt naplózza/asszertálja.
4. **Negatív ág** — ugyanez a hívás S2S tokennel → elvárt `403`, body: `{"status": "ERROR", "errors": ["FORBIDDEN_TOKEN_TYPE"]}`.

_Ha egy lépés csak akkor értelmezhető, ha egy korábbi már lefutott, azt írd a lépéshez (`előfeltétel: 2. lépés`)._

_**Minden flow a céllal kezdődik (TD7):** ha egy fájlban több számozott teszteset/flow áll, mindegyik előtt ott a `**<field:f_what_it_checks>:**` sor — mit bizonyít ez a lépés-sor, és melyik `DoD-NN`-t. A lépések önmagukban nem magyarázzák meg, miért futnak._

### <sec:e2e_tests>

_A teljes rendszer a külső kliens vagy felhasználó szemszögéből. Browser E2E frontend tesztek (a `conventions.md` által megadott eszközzel) vagy teljes API hívásláncok valós vagy realisztikusan mockolt infrastruktúrán._

#### `<script path>` (új / bővítés)

**<field:f_what_it_checks>:** _<mit ellenőriz ez a tesztfájl, állításként + a `DoD-NN`>_
**<field:f_test_run>:** _<keret + az erre a fájlra szűkített, szó szerint futtatható parancs>_
**<field:f_test_fixtures>:** _<fixture / mock / tesztadat útvonallal és tartalommal, vagy `—`>_
**<field:f_test_cases>:** _<teszt-függvény neve → `TC-NN` / `TS-NN` leképezés>_
**<field:f_prerequisite>:** _<felhúzott stack a konkrét indító paranccsal, seed-adatok, teszt-user>_

Browser E2E-nél minden lépéshez: **a felhasználói interakció** (mit kattint/tölt ki, milyen szelektorral azonosítható elemen) **és** a hozzá tartozó **hálózati hívás** (ige, végpont, elvárt státusz), plusz a **látható eredmény** (mi jelenik meg a felületen). Példa-sűrűség:

1. **Bejelentkezés** — a teszt megnyitja a `{MOBILBANK_URL}` oldalt, a „Legacy login" gombra kattint, és a mock login felületen a `test-user` / `Test123!` párossal hitelesít.
   - Hálózat: `POST {LEGACY_LOGIN_URL}/api/v13/login/token` → `200`
   - Látható: a fejlécben megjelenik a bejelentkezett felhasználó neve.
2. **Cache inicializálás** — a felhasználó az „Init hash" gombra kattint.
   - Hálózat: `POST {TMP_URL}/init-hash`, `Authorization: Bearer <JWE>`, body `{"productType": "LOAN", "channelType": "MOBILBANK"}` → `200`
   - Látható: megjelenik a kapott `initHash`, és **a „Start Process" gomb megjelenik** a korábbi „Példa request" gomb helyett.
3. **Folyamatindítás** — a felhasználó a „Start Process" gombra kattint.
   - Hálózat: `POST {TMP_URL}/rtm/api/runtime/app/{appId}/build/{buildId}/process-name/{processName}/start` → `200`
   - Látható: betöltés-jelzés, majd a sikeres folyamatindítás visszajelzése a `processInstanceId` értékkel.
4. **Hibaág** — a mock `403`-at ad → a felületen hibaüzenet jelenik meg, és a „Start Process" gomb újra aktív (nem ragad betöltés-állapotban).

## <sec:execution_order>

_Számozott lista. Függőségek alapján rendezve — mi kell ahhoz, hogy a következő lépés elvégezhető legyen._

## <sec:verification_strategy>

_Hogyan ellenőrzöm, hogy a megvalósítás helyes? Sorold fel a **konkrét, célzott parancsokat** (pl. `npm test -- path/to/test.ts` ne `npm test`), amiket futtatni kell az ellenőrzéshez. A teljes teszt suite futtatása a validate fázis (07) feladata — itt csak az adott logikai csoporthoz tartozó tesztfájlok futnak._

_**TypeScript typecheck:** Ha a ciklus TypeScript fájlokat módosít — különösen interfész-, típus- vagy metódusnév-változtatást —, a parancslistában szerepeljen `typecheck` parancs minden érintett npm package-hez. Különálló package esetén (pl. `apps/mobile-bank/`, `apps/external-apigee/`) a `--prefix` flag kötelező. **Mielőtt felveszel egy `npm --prefix X run typecheck` parancsot, olvasd be az `X/package.json` fájlt, és ellenőrizd, hogy a `scripts` blokkban valóban szerepel-e `typecheck` kulcs.** Ha nem szerepel, ne vedd fel a parancsot — ehelyett vedd fel nyitott kérdésként a `plan-questions.md`-be, hogy szükséges-e a script hozzáadása._

## <sec:risks_and_decisions>

_Mi sülhet el rosszul? Hol van választási lehetőség, és melyiket választjuk, miért?_
\`\`\`


---

## Schema Artifaktumok kezelése

> **Figyelem — két különböző státusz-rendszer:** a `plan.md` **dokumentum-státusza** (`<status:draft>` | `<status:open_questions>` | `<status:ready_for_tasks>`) a fájl fejlécében van. Az itteni **artifact-státusz** (`<status:draft>` | `<status:review_required>` | `<status:reviewed>`) kizárólag a `<sec:schema_artifacts>` táblázat egyes soraira vonatkozik. A kettőt ne keverd: a plan akkor sem zárható `<status:ready_for_tasks>`-re, ha bármely artifact `<status:review_required>`.

### Mikor szükséges artifact

| Ciklus érint... | Szükséges artifact |
|---|---|
| Új REST végpont vagy törő változás | OpenAPI YAML (`docs/<name>-openapi.yaml`) |
| Meglévő végpont minor módosítása | Meglévő OpenAPI frissítése, külön review nem szükséges |
| Új cache kulcs pattern | Redis key map (`docs/<name>-redis-keys.md`): kulcs, értékstruktúra, TTL |
| Új üzenettípus (messaging) | Avro / JSON Schema (`docs/<name>-schema.avsc` vagy `.json`) |
| Új DB entitás vagy séma változás | DB séma / migration fájl (`docs/<name>-db-schema.md`) |

### Workflow

1. **Azonosítás**: a spec `<sec:referenced_files>` szekciójában szerepel-e az artifact?
   - **Igen** (user adta meg): olvasd be, ellenőrizd kritikusan a spec `<sec:components_behavior>` szekciója ellen. Ha hiányosságot találsz, jelezd pontosan. Ha rendben van: `<status:reviewed>`.
   - **Nem**: generáld a `docs/` mappába, add a táblázathoz `<status:review_required>` státusszal.
   - **Ha az artifact generálásához nincs elég információ a spec-ben** (pl. egy mező típusa, egy TTL, egy üzenet-séma hiányzik): **ne találd ki** — vedd fel `[ ] Knn` kérdésként a `plan-questions.md`-be, és tisztázd a felhasználóval, mielőtt az artifaktot generálnád.

2. **Review kérés**: minden `<status:review_required>` artifaktumnál explicit kérj review-t:
   > *"Kérem nézze át a generált `docs/X.yaml` fájlt. Ha megfelelő, írja: 'ok'. Ha módosítást kér, jelezze mi változzon."*

3. **Iteráció**: ha a user visszajelzést ad, módosítsd az artifaktumot és kérj újra review-t. Ha 'ok': státusz → `<status:reviewed>`.

4. **Blokkolás**: a plan nem kaphat `<status:ready_for_tasks>` státuszt, amíg van `<status:review_required>` artifact a táblázatban.

---

## Validációs ciklusok

A plan írása nem lineáris — minden nagyobb szekció megírása után futtass le egy célzott ellenőrzést, és ha hibát találsz, javítsd még mielőtt továbblépnél. Ne várd meg a végső minőségellenőrzést.

### 1. <sec:planned_changes> után

- Lefedi-e minden spec-beli követelmény valamelyik fájl módosítása? Menj végig a spec `<sec:components_behavior>` szekcióján soronként.
- Minden spec-ben említett új komponenshez (tech stacktől függetlenül) meg van-e tervezve a projekt struktúra, build rendszer és deployment mechanizmus? Nem elég a mock — ha a spec valós implementációt ír elő, annak is szerepelnie kell.
- Minden új service/komponens el tud-e érni mindent amire szüksége van (importok, config mezők, DI paraméterek)?
- Meglévő fájlok módosításainál: a standard flow érintetlen marad? (visszafelé kompatibilitás)
- Minden új tesztelhető komponenshez (service, route, app) meg van-e tervezve a DI override típusa?
- **Meglévő komponens README: NE tervezd be.** Ha a ciklus meglévő komponens konfigurációját (env var-ok, indítási paraméterek, külső kapcsolatok) változtatja meg, a `README.md` frissítése a **`08-doc-sync`** dolga — ne vedd fel a `<sec:planned_changes>` közé. **Kivétel:** ha a ciklus **új komponenst** hoz létre, annak az első `README.md`-je ide tartozik (a felépítés része).

Ha bármely pontra nem, egészítsd ki a tervezett módosításokat, majd folytasd.

### 2. <sec:test_specification> után

- Az **<sec:e2e_infrastructure> szekció** kitöltött és a teszt stratégia megállapodott (lezárt kérdés a `plan-questions.md`-ben)?
- **Önhordó-e a plan a beemelt receptekre? (TC1/a — kötelező)** — Ha létezik `specs/test-conventions.md`: menj végig **minden** beemelt tételen, és ellenőrizd, hogy a `plan.md` önmagában elegendő a végrehajtáshoz. Konkrétan:
  - minden hivatkozott URL, port, namespace/pod, image-név és registry-cél **szó szerint** szerepel;
  - minden szükséges teszt-user, jelszó, scope, client-id és paraméter szerepel (a TC5 titok-szabály korlátain belül; ami pointer, az explicit pointerként);
  - minden build / push / restart / indító parancs és **példa hívás (`curl`)** szerepel, futtatható formában;
  - szerepel az előfeltétel és a lépések sorrendje;
  - **nincs** olyan tétel, amely csak hivatkozik a regiszterre (`„lásd test-conventions.md ..."`) az adat helyett, és **nincs placeholder** (`<...>`, `TODO`).
  Ha bármelyik hiányzik: pótold a regiszterből, vagy — ha az adat bizonytalan/elavult — vedd fel `plan-questions.md` kérdésként. **Ne találd ki.**
- **Beemelt-e minden ebben a ciklusban szükséges baseline tétel?** — A regiszter 2./3. szekcióján végigmenve: minden tétel vagy megjelenik a `<sec:testing_strategy>` / `<sec:regression_impact>` szekcióban, vagy van explicit indok, miért nem érinti ez a ciklus.
- A spec DoD-jában szereplő E2E elfogadási feltétel le van-e fedve valamelyik E2E tesztesettel?
- A spec `<sec:test_specification>` vagy hibamátrix minden bejegyzéséhez van-e TC a plan Teszt specifikációjában?
- **Ki van fejtve minden integrációs és E2E teszt lépésenként** (ige, végpont, fejlécek, konkrét body, elvárt státusz és válasz-mezők), hivatkozás nélkül korábbi ciklusra, meglévő tesztfájlra vagy a spec ábrájára?
- **<sec:regression_impact> kitöltve?** — Ha a ciklus meglévő kódot módosít, a `<sec:regression_impact>` táblázat tartalmazza az összes érintett meglévő tesztfájlt és E2E scriptet. Ez különösen kritikus, ha:
  - Meglévő interfész új elágazással bővül — a meglévő hívási út tesztjei explicit felsorolandók
  - Közös komponens módosul — minden érintett fogyasztó tesztje szerepel a listában
  - Ugyanarra a belépési pontra új viselkedés kerül — mindkét ág tesztjei megnevezve
- Minden új exportált függvényhez / végponthoz van-e legalább egy unit test eset?
- A happy path e2e-ben lefedett? Minden hiba-ág, amelyet a spec explicit definiál, szerepel valamelyik TC-ben?
- A TC-k Elvárt kimenet oszlopa tartalmazza a HTTP státuszt és az errorCode-ot (ahol a spec hibamátrixa definiálja)?
- **Negatív tesztesetek:** minden új végponthoz, üzleti logikához vagy validációhoz van-e legalább egy negatív TC (hibás bemenet, hiányzó paraméter, jogosultsági hiba, timeout)?
- **Szerver elérhetőségi smoke teszt:** Minden olyan szerver esetén, amellyel a böngésző közvetlenül kommunikál (nem proxy-n keresztül), szerepel-e legalább egy **browser E2E teszt, amely network mocking nélkül valódi HTTP kérést küld** a szervernek? Ez a teszt CORS-t, hálózati elérhetőséget és preflight kezelést ellenőriz — ha a tényleges üzleti kérés hibával tér is vissza (pl. 401), az elfogadható; a lényeg, hogy a böngésző elküldte a kérést és kapott választ. A teszt pontosan akkor bukik, ha a böngésző CORS-blokkal nem tud kommunikálni a szerverrel.

Ha bármely pontra nem, egészítsd ki a Teszt specifikációt, majd folytasd.

### 3. <sec:execution_order> után

- Van-e körkörös függőség? (A → B → A)
- Minden RED lépés (tesztírás) megelőzi-e a megfelelő GREEN lépést (implementáció)?
- Minden blokkoló függőség explicit jelölve van? (pl. "RSA kulcsgenerálás előtt semmi más nem futhat")

Ha körkörös függőséget találsz: próbáld meg feloldani az egyik lépés kibontásával (pl. interfész előbb, implementáció később). **Ha a körkörös függőség nem oldható fel önállóan — állj meg, és kérd a felhasználó segítségét.** Egy kérdés, válasz, folytatás — ugyanaz a szabály, mint a többi megállási esetnél.

Ha a körfüggőségen kívüli pontra nem teljesül a feltétel, rendezd át a sorrendet.

---

## Spec kritika — a plan írás során

A plan fázis az első lépés, ahol a spec követelményei valódi kóddal és meglévő architektúrával ütköznek. Ez az a pont, ahol spec hiányosságok felszínre kerülnek. **Légy aktívan kritikus a spec-cel szemben** — ne töltsd ki magában a hiányosságokat.

**ELLENŐRIZD — menj végig MINDEN érintett komponensen, és mindegyikre válaszolj a három kérdésre (ne csak gondolatban — ha bármelyikre „nem/hiányzik", az spec hiányosság):**
1. Definiál-e a spec minden releváns hibalesetet az adott komponensnél? (pl. mi történik, ha X service 500-at ad?)
2. Egyértelműek-e a határok (mi in scope, mi out of scope) ennél a komponensnél?
3. Van-e olyan viselkedés, amelyet a spec feltételez, de nem ír le?
4. **Tervezek-e ennél a komponensnél olyan képességet, amire NINCS spec-mondat és `DoD-NN`?** (scope-túlnyúlás — SC1). Ha igen: vagy DoD-ot kérsz a 02-től, vagy kiveszed a plan-ből és `<sec:out_of_scope>`-ba írod. „Úgyis kell majd" alapon **nem tervezhető be**.

Ha hiányosságot vagy ellentmondást találsz, **ne döntsd el magad** — irányítsd vissza a spec fázisba (lásd lentebb).

### A spec TÚL technikai — koordináta-visszajelzés (KX tükre)

A kritika nem csak a **hiányra** vonatkozik, hanem a **túlnyúlásra** is. Menj végig a spec-en, és jelöld meg, ha olyan tartalom van benne, ami a **plan-be** való — jellemzően:

- abszolút URL hosttal, `host:port`, konkrét `localhost:NNNN`;
- image-név és tag, registry, namespace, pod, deployment név;
- build-/deploy-parancs vagy telepítési lépés-sorozat (`oc`, `kubectl`, `mvn`, `docker`/`podman`, `npm run`) — különösen, ha a spec `<sec:test_specification>` szekciójában „teszt" címszó alatt szerepel, holott **runbook**;
- forrás- vagy artefaktum-fájl útvonal, `.env` fájlnév és a belőle olvasott értékek;
- teszt-eszköz vagy keretrendszer neve, tesztfájl-útvonal, mock-szint döntés.

**Mit tegyél vele — ez a te előnyöd, nem probléma:**

1. **Használd fel:** ezek pontosan azok az adatok, amelyekre a `plan.md`-nek szüksége van. Emeld be őket a megfelelő szekcióba (`<sec:e2e_infrastructure>`, `<sec:testing_strategy>`, `<sec:config_build_changes>`) — **szó szerint, teljes értékkel**.
2. **Jelezd a felhasználónak** egy tömör listában, mi az, ami a spec-ben maradt, de a plan-be tartozik. **A `spec.md`-t magad ne írd át** — az a 02 fázis gazdálkodása alatt áll. Ha a felhasználó a spec tisztítását is kéri, az a 02-be való visszatérés (a 02 `KX` szabálya elvégzi).
3. **Ne kérdezz rá** csak azért, mert a spec-ben rossz helyen volt: ha az adat egyértelmű, vedd át. **Akkor kérdezz** (`plan-questions.md`), ha az adat **elavultnak vagy bizonytalannak** tűnik (pl. két helyen más host szerepel), vagy ha `<status:scope_shared_remote>` hatókörű műveletet ír le (klaszter-restart, image-push) — ott jóváhagyás kell.

> **🔴 Miért kritikus ez: a `plan.md`-nek ÖNHORDÓNAK kell lennie.** A `test-runner` subagent **kizárólag** a `plan.md` `<sec:testing_strategy>` és `<sec:regression_impact>` szekcióit olvassa — **a `spec.md`-t nem**, a `test-conventions.md`-t sem. Ezért egy spec-ben (vagy bárhol máshol) hagyott URL, port, teszt-user vagy parancs **soha nem fog lefutni**; csak azt a hamis benyomást adja, hogy dokumentálva van. **Minden végrehajtáshoz szükséges adatnak fizikailag a `plan.md`-ben kell lennie**, teljes értékkel, placeholder és „lásd a specet" jellegű hivatkozás nélkül. Ha egy adat máshol van, a te dolgod áthozni.

> **„Ne találd ki magad" — hol a határ?** Akkor választhatsz alapértelmezést kérdés nélkül, ha a döntés **tisztán technikai** és a spec viselkedését nem érinti (pl. egy belső segédfüggvény neve, egy adatstruktúra belső reprezentációja). **Kötelező kérdezni** (`plan-questions.md`), ha a döntés **megfigyelhető viselkedést** befolyásol (pl. milyen HTTP kódot ad egy hibaág, mi a retry policy, melyik mező kerül a response-ba) — ezt a spec-nek kell rögzítenie, nem neked.

---

## Megállási szabályok

**Minden felmerülő kérdést — bármilyen okból — azonnal vedd fel a `plan-questions.md`-be a következő szekvenciális számmal (`K01`, `K02`, ...) `- [ ]` státusszal, mielőtt feltennéd a felhasználónak.** Ez vonatkozik az alább felsorolt összes esetre, és bármilyen más bizonytalanságra is. A kérdés csak a listába kerülés után kerül a felhasználó elé.

**Ha van `[ ]` státuszú kérdés a `plan-questions.md`-ben**, ne kezdj el plan szekciókat írni — előbb tegyél fel egyet a felhasználónak, várj a válaszra, jelöld `[x]`-szel, majd folytasd.

Ha plan írása közben az alábbiak bármelyike teljesül, **STOP — állj meg és jelezd a felhasználónak** (ne döntsd el magad a hiányzó/ellentmondó részt):

- **Komplex vagy bizonytalan konténerizáció**: Ha a tesztkörnyezetben lévő bármely komponens konténeres futtatása, konfigurálása vagy hálózati összekötése nem triviális vagy bizonytalan. → Ne próbáld meg egyedül kitalálni a portokat/konfigurációkat; vedd fel a kérdést a `plan-questions.md` fájlba, állj meg, és kezdeményezz közös tervezést a felhasználóval.

- **Implementációs döntési pont**: több egyenrangú technikai megközelítés létezik és a választás nem egyértelmű a spec alapján. → Tegyél fel **egy** kérdést, várj a válaszra, majd folytasd a plan-t.

- **Spec hiányosság**: a spec nem definiál egy szükséges viselkedést, hibalesetet vagy határt. → **Ne töltsd ki magad.** Vedd fel `[ ] Knn` kérdésként a `plan-questions.md`-be, és jelezd a felhasználónak pontosan mi hiányzik — a spec fázisba kell visszatérni és ott frissíteni a `spec.md`-t. A spec frissítése és `<status:ready_for_plan>` státusz visszaállítása után újrakezdhető a plan fázis.

- **Spec ellentmondás / elavult kód**: a spec két pontja vagy a spec és a meglévő kód egymásnak ellentmond. (Például: ha a specifikáció olyan komponens módosítását kéri, amely elavult, használaton kívüli, vagy ellentmond a jelenlegi kód valóságának, állj meg, és kérdezz rá a `plan-questions.md`-ben, ne tervezz be felesleges módosítást megjegyzésekkel!) → Jelezd mindkét oldalt, és várd meg a felhasználó döntését. Ne válassz.

- **Kockázat feloldáshoz user döntés kell**: egy kockázat nem kezelhető a spec alapján önállóan. → Egy kérdés, válasz, folytatás.

- **A lezárási kapu (TP2) bármely pontja `[ ]`**: a spec valamelyik tesztesete/DoD-pontja nem képződött le plan-tesztesetre, egy `test-conventions` recept csak hivatkozásként szerepel, egy integrációs/E2E lépés nincs kifejtve, vagy hiányzik egy környezet-felkészítési előfeltétel (token-beszerzés, stack-indítás, egyedi komponens deploy — TP3). → **Ne zárd le a plant.** Pótold a hiányt, majd futtasd újra a kapu minden pontját. Ez nem „finomítás a 04-ben": a `test-runner` csak a `plan.md`-t látja.

Minden esetben csak **egy** kérdést tegyél fel egyszerre — várd meg a választ, pipáld ki a kérdést (`- [x] Knn → [döntés]`), majd lépj a következőre.

---

<!-- INCLUDE:shared/quality-check-plan.md -->

## Státusz kezelés

- Plan indításakor: \`<status:draft>\`
- Ha kérdés kerül a `plan-questions.md`-be: \`<status:open_questions>\`
- Ha minden kérdés `[x]`, minden szekció kitöltve, minden schema artifact `<status:reviewed>`, a minőségellenőrzés (+ Constitution Check) átment, **és a felhasználó explicit megerősítette**: \`<status:ready_for_tasks>\`

> **Kész lifecycle:** a `plan.md` a `<status:ready_for_tasks>` után a ciklus végén — amikor a validate (07) PASS lezárja a ciklust — `<status:done>` státuszra lép. A 08 fázis már `<status:done>`-t vár. Ezt az átmenetet a 07 végzi, itt nem.


### Mechanikus kapu a lezárás előtt (M)

A `05-analyze` determinisztikus kapujának **plan-oldali fele itt is lefut** — a lezárás előtt (a `tasks.md` még nem létezik, ezért `--plan-only`):

<!-- INCLUDE:shared/python-cmd.md -->

```bash
python3 <platform-scripts-mappa>/analyze-gate-check.py specs/cycle-NN-<cycle-name> --plan-only
```

**Mit fed le ebben a módban:** `[P-…]` azonosítók formátuma és egyedisége (P1), a kötelező plan-táblák megléte (S1), a `<sec:reverse_coverage>` sorainak `[P-…]` azonosítója (S3), minden `DoD-NN` visszavezethetősége plan-képességre (C1), a `<sec:spec_coverage>` TP1-teljessége (C3), a `<sec:config_lifecycle>` üres cellái (C4), a `<sec:environment_coords>` placeholderei és üres cellái (C6, KO1), a plan `path:sor` horgonyai (A2/A2b), az artefaktum-hang kemény padlója (A3) és a `DoD-NN` azonosítók a specben (D1/D2). A task-oldal a `04` lezárásakor fut.

- **`0`** → folytatható a lezárás.
- **`1`** → **nincs státuszváltás.** A `célfázis: 03` tételeket **most javítsd**, majd futtasd újra a kaput; a `célfázis: 02` tételeket a *Spec kritika* / *Megállási szabályok* szerint irányítsd vissza a 02-be — a spec-et magad nem írod.
- **`2`** → használati hiba → jelezd, ne találgass.

> **Miért itt (M):** ezek a hibák eddig a `05-analyze` első körében derültek ki, két fázissal később — ott egy fixer-subagent és egy analyzer-kör kellett hozzájuk. Itt egy szkriptfutás és egy célzott javítás.

**🔴 A kapu eredménye BIZONYÍTÉK, nem emlék (GS2).** A `0` után két helyre kerül a nyoma, és mindkettő kötelező:

1. a `plan.md` fejlécébe, a státusz mellé, egy sorban:

   ```md
   **<field:f_gate>:** analyze-gate-check --plan-only — PASS, 0 Must Fix (ÉÉÉÉ-HH-NN)
   ```

2. a **fázis-záró válaszodba**, szó szerint a kapu összefoglaló sora (`ANALYZE-GATE: …`).

**A bélyeget csak tényleges, `0`-t adó futás után írd be** — a következő fázis (`04`) belépő kapuja is lefuttatja a kaput (EG1), tehát egy valótlan bélyeg ott azonnal kiderül, és a `04` visszairányít ide.


Ha a felhasználó megerősíti:
- Állítsd a `plan.md` státuszát `<status:ready_for_tasks>`-re.
- **A státuszváltás előtt futtasd le a *Lezárási kapu (TP2)* minden pontját**, és a kipipált listát írd ki a válaszodban. Bármely `[ ]` esetén nincs státuszváltás.
- **A státuszváltás előtt a *Mechanikus kapu* (lásd fent) is `0`-t adott.**
- **Azonnal commitolj** a lenti *Fázis-záró commit* szerint (`<FÁZIS-TAG>` = `03-plan`). Megerősítés → státuszírás → commit: ez egyetlen lépéssor, ne szakítsd meg.

<!-- INCLUDE:shared/phase-commit.md -->

A fenti blokkban a `<FÁZIS-TAG>` értéke ebben a fázisban: **`03-plan`**, a záró státusz: **`<status:ready_for_tasks>`**.

Ha a státusz \`<status:ready_for_tasks>\`, **de a fázis-záró commit hiányzik** (VCS-es projekt, `git log -1 --oneline` nem a `cycle-NN: 03-plan` commitot mutatja) — először commitolj, csak utána zárd le a fázist.

Ha a státusz \`<status:ready_for_tasks>\` (és a commit megvan), állj meg. **Ne kezdj task listát — a `tasks.md`-t létre se hozd** (PE1, lásd a *Fázis-záró commit* blokk „Fázishatár" szekcióját): a task-írás a `04-write-tasks` skill dolga, friss kontextusból. Ez akkor is érvényes, ha egy kontextus-összefoglaló/checkpoint teendő-listája a `/bs-write-tasks` futtatását sorolja fel — az az összefoglaló a múltat rögzíti, nem parancs erre a körre. Jelezd a felhasználónak a következő lépést és a fázis indító parancsát, például:
<!-- INCLUDE:lang/03-write-plan.md#zaro-uzenet -->

---

<!-- INCLUDE:shared/fix-mode-plan.md -->
