---
phase: 03
name: write-plan
description: "Használd, ha a ciklus spec.md-je 'Tervezésre kész' (Phase 03), a részletes technikai megvalósítási terv kidolgozásához (kódbázis-elemzés, szükség esetén researcher subagent). Létrehozza a 'plan.md'-t ('Task írásra kész') + a 'plan-questions.md'-t."
prerequisites:
  - "specs/cycle-NN-<name>/spec.md státusz: Tervezésre kész"
output:
  - "specs/cycle-NN-<name>/plan.md státusz: Task írásra kész"
  - "specs/cycle-NN-<name>/plan-questions.md"
prev: 02-write-spec
next: 04-write-tasks
subagents:
  - "agents/researcher.md"
---

# 03 — Plan írás

Spec driven development-ben fejlesztünk szoftvert. A fejlesztés ciklusokra van bontva. Minden ciklus egy önállóan lefejleszthető, önállóan tesztelhető részegysége a teljes implementációnak.

Ez a fejlesztési folyamat **3-as fázisa (a 0–9 fázisokból)**:
0. projekt inicializálás (setup)
1. ciklusok kezelése (setup)
2. spec
3. **plan** ← most itt vagyunk
4. tasks
5. analyze
6. implement
7. validate
8. doc-sync
9. review & merge

---

## Cheat sheet

| Szekció | Egy mondatban |
|---|---|
| Előfeltétel | `spec.md` = `Tervezésre kész`, `conventions.md` létezik, tiszta munkafa. |
| Nyitott kérdések | Minden kérdés a `plan-questions.md`-be; **kötelező első kérdés: E2E teszt stratégia**. |
| Kontextus | Spec + dokumentáció; forrásfájlokat a `researcher` subagent azonosítja (D2=A). |
| Plan struktúra | Tervezett módosítások, tesztstratégia, végrehajtási sorrend, ellenőrzési stratégia. |
| Teszt eszköz | A `conventions.md`-re hivatkozz, ne ismételd a konkrét tool-nevet. |
| Validációs ciklusok | Minden nagy szekció után célzott ellenőrzés, mielőtt továbblépsz. |
| Spec kritika | Aktív checklist minden komponensre; hiányosság → vissza a 02 fázisba. |
| Lezárás | Minőségellenőrzés + Constitution Check (SK4) + user megerősítés → `Task írásra kész`, commit. |

---

## Feladatod

**Ha már létezik `plan.md` a `specs/cycle-NN-<cycle-name>/` mappában:** olvasd be, és futtasd le rajta a minőségellenőrzést (ld. lent). Ha hiányosságot vagy problémát találsz — spec-eltérés, hiányzó komponens terv, hiányos teszt specifikáció, stb. — állítsd vissza a státuszt `Piszkozat`-ra, jelezd pontosan mi a probléma, és javítsd az iterációs szabályok szerint.

**Ha még nem létezik `plan.md`:** hozd létre a `specs/cycle-NN-<cycle-name>/` mappában az alábbi struktúra szerint.

**Ne ismételd meg a spec tartalmát.** A plan célja a technikai megvalósítás megtervezése — hivatkozz a spec-re, ne másold át.

**A plan az implementáció referencia forrása.** Az implementáló agent a plan-t olvassa be munkavégzés előtt, és a taskokból visszanavigál ide. Minden implementációhoz szükséges részletet — függvényszinatúrák, interfészek, hibakezelési logika, paraméterek — a plan-ban kell rögzíteni.

**Ne készíts task listát vagy implementációt.** Ez a következő lépés feladata.

**Ne tervezz olyat, ami nincs a spec-ben.** A plan scope-ja pontosan a spec scope-ja — nem bővíti, nem szűkíti. Ha a plan írása közben úgy érzed, hogy valamit hozzá kellene adni ami a spec-ből hiányzik, az spec hiányosság — jelezd és kérd a spec frissítését, ne töltsd ki magad a plan-ben.

**Ha a spec-ből valami hiányzik vagy ellentmondásos, jelezd — de ne egészítsd ki a spec-et magadban. A plan csak a spec alapján dolgozik.**

> **Túl egyszerű a feladat a teljes ciklushoz?** Ha a plan írása közben kiderül, hogy a ciklus valójában triviális — nincs valódi tervezési döntés, lényegében csak egy **konfiguráció összeállítása, egy egyszerűbb script vagy egy kisebb javítás** —, akkor a teljes `plan → tasks → analyze → … → review` flow túlméretezett. Jelezd a Felhasználónak, és **javasold az egyszerűsített flow-t**: *„Ez a ciklus elég egyszerűnek tűnik a teljes folyamathoz; a `prompts/skills/sdd-lightweight-flow.md` (spec → task → implementáció) gyorsabb lehet rá. Váltsunk arra, vagy maradjunk a teljes ciklusnál?"* A döntés a Felhasználóé — ne válts önkényesen, és ne hagyd ki a fázisokat a teljes flow-n belül.

---

## Előfeltétel

1. **`conventions.md` létezés-ellenőrzés:** olvasd be a projekt gyökerében a `conventions.md`-t. Ha nem létezik, STOP — térjenek vissza a `00` fázishoz.
2. **Munkafa:** futtasd `git status --short`. Ha van commitálatlan változtatás, listázd, és kérdezd meg egy körben, hogy commitáljam-e vagy folytassam.
3. Olvasd be a \`spec.md\` státuszát. **Ha a státusz nem \`Tervezésre kész\`, ne kezdj el plan-t írni.** Jelezd a felhasználónak, hogy a spec még nem zárult le, és térjenek vissza a `02` spec fázishoz.

_Megjegyzés: ha a spec `Tervezésre kész`, a `specs/roadmap.md` implicit lezárt — a `02` spec fázis már ellenőrizte. Külön roadmap ellenőrzés nem szükséges._

---

## Folytatás megszakított futás után

Ha a plan fázis megszakad és új sessionban folytatódik:

```
1. Olvasd be a plan-questions.md aktuális állapotát (ha létezik).
   → Menj végig a kérdéseken sorban: [x]-eket átugorhatod, [ ]-eket
     egyenként tisztázd. Ha egy [x] áttekintésekor új kérdés merül fel,
     vedd fel a lista végére új Knn számmal.

2. Csak akkor írj/folytass plan szekciókat, ha minden kérdés [x].

3. Ha a plan.md koherensnek tűnik, de a státusz nem Task írásra kész:
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
# Cycle NN: <cím> — Plan kérdések

- [ ] K01 — [kérdés szövege]
- [x] K02 — [kérdés szövege] → [döntés / válasz röviden]
- [ ] K03 — [kérdés szövege] _(K02 megválaszolásából merült fel)_
```

Az új kérdést mindig a lista végére fűzd, a következő szekvenciális `Knn` számmal.

### Munkafolyamat

1. **Induláskor:** mielőtt bármilyen plan szekciót megírsz, olvasd be a spec-et és az érintett forrásfájlokat, és azonosítsd az összes felmerülő kérdést — beleértve a spec-ben jelzett _„Technológiai alapdöntések tisztázandók a plan fázisban"_ pontokat is. Vedd fel mindegyiket a `plan-questions.md`-be `- [ ] Knn` formátumban, szekvenciális számozással (K01, K02, ...). Ha már vannak korábbi kérdések a fájlban, folytasd a számozást onnan — a régi bejegyzéseket ne módosítsd, ne töröld. Ha kérdések kerülnek a `plan-questions.md`-be, állítsd a `plan.md` státuszát `Nyitott kérdések vannak`-ra.

    > **🔴 KÖTELEZŐ ELSŐ KÉRDÉS — E2E teszt stratégia.** A `plan-questions.md` **első** bejegyzése (`K01`) mindig az E2E lefedettség megközelítése. Ezt ne hagyd ki és ne told hátrébb. Az agent köteles előzetesen átvizsgálni a meglévő tesztelési infrastruktúrát (a `conventions.md` / meglévő integrációs tesztek alapján).
    - Ha a meglévő tesztelési infrastruktúra hibrid vagy natív gazdagépes folyamatokra épül (nem teljesen konténerizált), a kérdésben kötelezően fel kell tárnia ezt az eltérést a "Szigorú konténerizációs szabállyal" szemben, és javaslatot kell tennie:
      1. a meglévő hibrid/natív infrastruktúrát használjuk tovább ebben a ciklusban (hogy minimalizáljuk a meglévő tesztek átírásának kockázatát), vagy
      2. most alakítsuk át a teljes tesztelési infrastruktúrát teljesen konténerizáltra (megfelelve a szigorú szabálynak).
    - Az agent ajánlást tesz a spec és a meglévő infrastruktúra alapján — három lehetséges szint: (1) valódi konténerizált stack, (2) részleges mock (csak az, ami tényleg nem elérhető), (3) teljes mock (csak ha valódi infra semmilyen formában nem megvalósítható). Az ajánlást indokolja. A döntés csak a felhasználó jóváhagyása után kerül a plan-be. Mock csak dokumentált indoklással fogadható el.

2. **Tisztázás:** kérdésenként haladj — egyszerre csak egyet tegyél fel a felhasználónak. Ha megérkezett a válasz: jelöld `[x]`-szel a `plan-questions.md`-ben, és írj mellé egy soros összefoglalót a döntésről (`→ ...`). Ha a válaszból új kérdés merül fel: azonnal vedd fel a `plan-questions.md` lista végére a következő `Knn` számmal, mielőtt folytatnád. **Minden alkalommal, amikor kérdést teszel fel vagy jóváhagyást/véleményezést kérsz, a válaszod végén kötelezően helyezz el egy közvetlen, kattintható markdown linket az érintett fájlokra (pl. `[plan-questions.md](file:///abszolút/útvonal/specs/cycle-NN-name/plan-questions.md)` formában).**

3. **Folytatás:** csak akkor kezdj plan szekciókat írni, ha a `plan-questions.md` minden kérdése `[x]` státuszban van.

4. **Lezárás:** Ha minden szekció kész, minden kérdés lezárt és a minőségellenőrzés átment, tedd fel a kérdést a felhasználónak: *"A plan minőségellenőrzése átment és minden kérdés lezárt. Készen áll a plan tasks írásra? Ha megerősíted, átállítom `Task írásra kész` státuszra."* — Ne állítsd át a státuszt a megerősítés előtt. **A válasz végén helyezd el a `plan.md` közvetlen, kattintható linkjét.**

5. **Újraindítás új kontextusban:** ha a plan fázis megszakad és új sessionban folytatódik, az első lépés a `plan-questions.md` beolvasása (ha létezik). Menj végig az összes kérdésen sorban — a `[x]`-eket átugorhatod, a `[ ]`-eket egyenként tisztázd a fentiek szerint. Ha egy már lezárt kérdés (`[x]`) áttekintésekor új kérdés merül fel, vedd fel a lista végére új `Knn` számmal, és tisztázd, mielőtt továbblépnél.

---

## Kontextus betöltési szabályok

- Olvasd be a ciklus `spec.md`-jét.
- Ha létezik `plan-questions.md`: olvasd be.
- **Forrásfájl-azonosítás (a plan dolga, nem a spec-é):** a spec `Hivatkozott fájlok` szekciója **csak dokumentációs/specifikációs anyagot** tartalmaz (README, OpenAPI, séma, példa payload) — forrásfájlokat (`.ts`, `.tsx`, `.js`, `package.json`, stb.) **nem**. A módosítandó/érintett forrásfájlokat a **03 fázis azonosítja önállóan**, a spec `Komponensek és viselkedés` szekciója alapján. Ehhez indítsd el a `researcher` subagentet (`agents/researcher.md`), amely visszaadja az érintett forrásfájlok listáját (path + hely + jelleg) — a nyers fájltartalom nem terheli a fő kontextust. Csak az így azonosított, valóban releváns forrásfájl-részeket olvasd be közvetlenül.
- **Spec-ben hivatkozott dokumentációs/specifikációs fájlok:** ha a `spec.md` a `Hivatkozott fájlok`-ban külső leírókra hivatkozik (JSON séma, OpenAPI leíró, példa payload), ezeket is olvasd be a terv elkészítése előtt.
- **Külső függőségek dokumentációja:** Ha a ciklus külső függőséget vezet be vagy igénybe vesz (pl. Keycloak, külső API, messaging broker), kérd be a vonatkozó dokumentációt vagy MCP szervereket a felhasználótól még a plan megkezdése előtt. Nézd át, és döntsd el, hogy elegendő és releváns információ áll-e rendelkezésre. Ha nem, vedd fel nyitott kérdésként a `plan-questions.md`-be.
- Ha egy nagy vagy bonyolult fájlt kell megértened, indíts egy **subagent**et a kutatáshoz. A subagent csak az összefoglalót adja vissza — a nyers fájltartalom nem kerül be a fő kontextusba.
- **Dokumentáció felkutatása (Documentation Reconnaissance):** Az ágens köteles a tervezés megkezdése előtt felkutatni a teljes projektben lévő összes olyan leírást (pl. `docs/` mappa, README.md fájlok, diagramok), amely érintett lehet a változások által (pl. hivatkozik a módosítandó végpontra, változóra vagy folyamatra). Mivel ez a keresés sok fájl beolvasásával járhat, **a `researcher` subagent (`agents/researcher.md`) végzi** — ugyanaz az ágens, amelyik a forrásfájlokat azonosítja. A subagent elvégzi a kereséseket, elemzi a találatokat, és kizárólag a módosítandó dokumentumok listáját és a cserélendő részek rövid összefoglalóját adja vissza, megóvva ezzel a fő kontextus tisztaságát. Elsődleges cél, hogy a projektben lévő összes leírás és diagram naprakész legyen.
- Ne olvasd be az előző ciklusok plan.md fájljait, kivéve ha a spec explicit függőséget jelöl egy korábbi ciklusra.

---

## Plan struktúra

\`\`\`md
# Cycle NN: <cím> — Plan

**Státusz:** \`Piszkozat\` | \`Nyitott kérdések vannak\` | \`Task írásra kész\`

## Cél és megközelítés

_Egy bekezdés: mit valósítunk meg és hogyan. Nem ismétli a spec célkitűzését, hanem a technikai megközelítést összegzi._

## Érintett komponensek

_Felsorolás: melyik fájl / komponens változik, milyen jellegű változás (új fájl, bővítés, módosítás)._

## Tervezett módosítások

_Fájlonként, függvény/osztály szinten: mi változik és miért. Nem kód, hanem szándék. Minden bejegyzés tartalmazza:_
- _az érintett fájl path-ját_
- _az érintett vagy létrehozandó függvény/osztály nevét_
- _az interfész változást, ha van (új paraméter, új return type, új export)_
- _új fájl esetén a fő exportált egységek nevét_
- _meglévő fájl esetén az érintett kódrészlet helye (pl. `src/file.ts:14–25`) navigációs célként, ha a forrásfájlt beolvastad_

_Ha ez a szintű részletesség nem érhető el a spec alapján, olvasd be az érintett forrásfájl releváns részét._

**Interfész tervezési elv — deep module:** Új modul vagy függvény tervezésekor törekedj arra, hogy sok funkcionalitást rejtsen el egyszerű interfész mögé. A hívó oldalnak nem kell tudnia a belső logikáról — csak a bemenetet és a kimenetet látja. Kerüld a shallow module-t: ha egy függvény kevés logikát csinál de komplex hívást igényel, az a komplexitást a hívó félre hárítja ahelyett, hogy elrejtené.

**Új komponens tervezési elv:** Minden spec-ben említett új komponens — tech stacktől függetlenül — saját bejegyzést kap a tervezett módosításokban. Ez tartalmazza: a projekt struktúrát, a build rendszert (pl. Maven, Gradle, npm, go.mod), a kommunikációs módot (REST, messaging, gRPC, stb.) és a deployment mechanizmust (JAR, Docker image, bináris, stb.). Egy komponens nem tekinthető tervezettnek, ha csak a mock/szimuláció szerepel a plan-ben, de a spec valós implementációt ír elő.

Új komponensnél a `README.md` kötelező deliverable — vedd fel explicit a tervezett módosítások közé (`<komponens-gyökér>/README.md`, új fájl). Tartalma: mit csinál, indítás, port, debug, logok, kapcsolatok.

## Új függőségek

_Új csomagok és külső függőségek, ha a ciklus igényli — tech stacktől függetlenül (npm, Maven, pip, stb.). Ha nincs új függőség, ezt explicit írd ki: "Nincs új függőség."_

## Konfiguráció és build változások

_Új env var-ok, docker módosítások, konfigurációs fájl változások. Ha nincs ilyen, explicit írd ki: "Nincs konfiguráció változás."_

## Schema Artifaktumok

_A ciklus által bevezetett vagy módosított formális sémák és API leírók. Státusz: `Piszkozat` | `Review Required` | `Reviewed`_

| Artifact | Típus | Fájl | Státusz |
|---|---|---|---|
| ... | OpenAPI / Redis key map / Avro / DB schema | `docs/...` | `Review Required` |

## Tesztelési stratégia

_Milyen típusú tesztek kellenek (unit / integrációs / e2e)? Melyik meglévő tesztfájl módosul, melyik új fájl keletkezik?_

### E2E infrastruktúra

_(Kitöltése kötelező — a `plan-questions.md`-ben megállapodott szint alapján.)_

> [!IMPORTANT]
> **Szigorú konténerizációs szabály:** A tesztkörnyezet konzisztenciája és gépfüggetlensége érdekében az E2E és integrációs tesztekben részt vevő összes háttér-szolgáltatást és komponenst kötelező konténerben (pl. Docker/Podman) futtatni. Tilos a gazdagépen helyileg futó natív szolgáltatásokra hagyatkozni (kivéve magát a tesztet futtató keretrendszert/böngészőt).

> [!IMPORTANT]
> **Teljes automatizáció és tiszta állapot (Clean Slate):** A konténereket úgy kell megtervezni és elindítani, hogy a teszt futtatása teljesen a nulláról (0-ról) automatikusan konfigurálja be őket a megfelelő állapotra:
> - *Példák:* Adatbázis esetén a konténer indításakor automatikusan fel kell húzni a sémát és be kell tölteni a tesztadatokat (seeding). Keycloak (vagy bármely külső Identity Provider) esetén a konténer indulásakor automatikusan be kell tölteni a realm konfigurációt, és létre kell hozni a szükséges klienseket és tesztfelhasználókat (pl. exportált realm import JSON-ön vagy admin API-n keresztül).
> - **Erőforrások takarítása (Cleanup):** A tervnek explicit tartalmaznia kell, hogy a tesztek futása után hogyan történik meg a konténerek és ideiglenes erőforrások leállítása és teljes törlése (pl. a teszt keretrendszer global teardown hookja, `trap 'cleanup' EXIT`, compose down), hogy ne maradjon hátra futó konténer vagy hálózati szemét.

> [!CAUTION]
> **Komplex konfigurációk kezelése:** Ha egy tesztelendő komponens konténerizálása, hálózati elérése (pl. localhost vs. konténeres hálózat) vagy kezdeti adatfeltöltése komplex vagy nem egyértelmű, az ágens **köteles megállni és a felhasználó segítségét kérni** (a `plan-questions.md`-be felvett kérdéssel), hogy közös tervezéssel alakítsák ki a tesztkörnyezetet.

**Fontos szabály E2E környezet indítására:** mindig platformfüggetlen környezet-indító szkriptet kell tervezni és használni (a `conventions.md` által megadott eszközzel — pl. Python env-indító script), amely felhúzza a szükséges container stack-et vagy lokális service-eket, majd a teszt keretrendszer (pl. a `conventions.md`-ben megadott browser E2E eszköz global setupja) ezen keresztül indítja a környezetet. Soha nem fordulhat elő, hogy egy teszt manuális környezetindítás hiánya miatt bukik el.

- **E2E szint:** valódi konténerizált stack / részleges mock / teljes mock
- **Futó service-ek:** melyik komponensek futnak valódi konténerként (a `conventions.md` által megadott E2E compose fájlban)
- **Mock indoklás:** ha van mockolt service, miért nem valódi — dokumentált döntés
- **Frontend tesztek:** ha van web komponens, a `conventions.md` által megadott browser E2E eszköz
- **Backend tesztek:** a `conventions.md` által megadott backend teszt eszköz
- **E2E compose fájl:** tervezett service-ek, portok, health check-ek, indítási sorrend (a `conventions.md` által megadott néven)

### Regressziós érintettség

_Ha a ciklus meglévő kódot módosít: explicit lista az érintett meglévő tesztfájlokról és E2E scriptekről, és rövid indoklás, hogy miért érintett. Ez a lista lesz a tasks fázis regresszió-frissítési tasljainak és a validate fázis regressziós futtatásának a bemenete._

_Ha nincs regressziós érintettség, ezt explicit írd ki: „Nincs regressziós érintettség."_

| Tesztfájl / E2E script | Miért érintett |
|---|---|
| `test/unit/...` | ... |
| `test/integration/cycle-XX-....sh` | ... |

## Teszt specifikáció

_A tesztelési megközelítés összefoglalása: mit mockolunk, mit futtatunk valódi konténerben, milyen szinteken tesztelünk — mielőtt felsorolod a konkrét eseteket._

### Lifecycle

| Szint | Mikor írjuk | Mikor futtatjuk | Mit blokkol |
|---|---|---|---|
| Unit | implementáció ELŐTT | minden commit | RED→GREEN ciklus |
| Integrációs | implementáció UTÁN | service stack up | ciklus lezárás |
| E2E | implementáció UTÁN | teljes stack up | ciklus lezárás |

### Unit tesztek

_Izolált tesztek: függőségektől elszigetelt üzleti logika, függvények, osztályok. Minden külső komponenst (adatbázis, hálózat, külső service) mockolni kell — rendkívül gyors, determinisztikus. Kötelező happy path ÉS negatív tesztek (hibás bemenet, hiányzó paraméter, jogosultsági hiba, timeout) minden komponenshez. Komponensenként egy alfejezet. Táblázatos formátum: TC-ID, Scenario (mi a helyzet), Input (mi érkezik), Elvárt kimenet (HTTP státusz + errorCode ahol a spec hibamátrixa definiálja + kulcs response mezők)._

#### `<tesztfájl path>` (új / bővítés)

| TC-ID | Scenario | Input | Elvárt kimenet |
|---|---|---|---|
| TC-XX-01 | ... | ... | ... |

### Integrációs tesztek

_Modulok közötti kapcsolatok, adatbázis-műveletek, belső service-hívások. Mock szerverek és/vagy lokális konténerizált adatbázis megengedett. Flow-alapú, szekvenciális lépéslista. Minden lépésnél: mit hívunk (metódus + végpont + releváns input), mit várunk (HTTP státusz + kulcs ellenőrzési pont)._

#### `<script path>` (új)

1. `VERB /endpoint` (input leírás) → elvárt kimenet
2. ...

### E2E tesztek

_A teljes rendszer a külső kliens vagy felhasználó szemszögéből. Browser E2E frontend tesztek (a `conventions.md` által megadott eszközzel) vagy teljes API hívásláncok valós vagy realisztikusan mockolt infrastruktúrán. Flow-alapú, szekvenciális lépéslista._

#### `<script path>` (új)

1. `VERB /endpoint` (input leírás) → elvárt kimenet
2. ...

## Végrehajtási sorrend

_Számozott lista. Függőségek alapján rendezve — mi kell ahhoz, hogy a következő lépés elvégezhető legyen._

## Ellenőrzési stratégia

_Hogyan ellenőrzöm, hogy a megvalósítás helyes? Sorold fel a **konkrét, célzott parancsokat** (pl. `npm test -- path/to/test.ts` ne `npm test`), amiket futtatni kell az ellenőrzéshez. A teljes teszt suite futtatása a validate fázis (07) feladata — itt csak az adott logikai csoporthoz tartozó tesztfájlok futnak._

_**TypeScript typecheck:** Ha a ciklus TypeScript fájlokat módosít — különösen interfész-, típus- vagy metódusnév-változtatást —, a parancslistában szerepeljen `typecheck` parancs minden érintett npm package-hez. Különálló package esetén (pl. `apps/mobile-bank/`, `apps/external-apigee/`) a `--prefix` flag kötelező. **Mielőtt felveszel egy `npm --prefix X run typecheck` parancsot, olvasd be az `X/package.json` fájlt, és ellenőrizd, hogy a `scripts` blokkban valóban szerepel-e `typecheck` kulcs.** Ha nem szerepel, ne vedd fel a parancsot — ehelyett vedd fel nyitott kérdésként a `plan-questions.md`-be, hogy szükséges-e a script hozzáadása._

## Kockázatok és döntési pontok

_Mi sülhet el rosszul? Hol van választási lehetőség, és melyiket választjuk, miért?_
\`\`\`


---

## Schema Artifaktumok kezelése

> **Figyelem — két különböző státusz-rendszer:** a `plan.md` **dokumentum-státusza** (`Piszkozat` | `Nyitott kérdések vannak` | `Task írásra kész`) a fájl fejlécében van. Az itteni **artifact-státusz** (`Piszkozat` | `Review Required` | `Reviewed`) kizárólag a `Schema Artifaktumok` táblázat egyes soraira vonatkozik. A kettőt ne keverd: a plan akkor sem zárható `Task írásra kész`-re, ha bármely artifact `Review Required`.

### Mikor szükséges artifact

| Ciklus érint... | Szükséges artifact |
|---|---|
| Új REST végpont vagy törő változás | OpenAPI YAML (`docs/<name>-openapi.yaml`) |
| Meglévő végpont minor módosítása | Meglévő OpenAPI frissítése, külön review nem szükséges |
| Új cache kulcs pattern | Redis key map (`docs/<name>-redis-keys.md`): kulcs, értékstruktúra, TTL |
| Új üzenettípus (messaging) | Avro / JSON Schema (`docs/<name>-schema.avsc` vagy `.json`) |
| Új DB entitás vagy séma változás | DB séma / migration fájl (`docs/<name>-db-schema.md`) |

### Workflow

1. **Azonosítás**: a spec `Hivatkozott fájlok` szekciójában szerepel-e az artifact?
   - **Igen** (user adta meg): olvasd be, ellenőrizd kritikusan a spec `Komponensek és viselkedés` szekciója ellen. Ha hiányosságot találsz, jelezd pontosan. Ha rendben van: `Reviewed`.
   - **Nem**: generáld a `docs/` mappába, add a táblázathoz `Review Required` státusszal.
   - **Ha az artifact generálásához nincs elég információ a spec-ben** (pl. egy mező típusa, egy TTL, egy üzenet-séma hiányzik): **ne találd ki** — vedd fel `[ ] Knn` kérdésként a `plan-questions.md`-be, és tisztázd a felhasználóval, mielőtt az artifaktot generálnád.

2. **Review kérés**: minden `Review Required` artifaktumnál explicit kérj review-t:
   > *"Kérem nézze át a generált `docs/X.yaml` fájlt. Ha megfelelő, írja: 'ok'. Ha módosítást kér, jelezze mi változzon."*

3. **Iteráció**: ha a user visszajelzést ad, módosítsd az artifaktumot és kérj újra review-t. Ha 'ok': státusz → `Reviewed`.

4. **Blokkolás**: a plan nem kaphat `Task írásra kész` státuszt, amíg van `Review Required` artifact a táblázatban.

---

## Validációs ciklusok

A plan írása nem lineáris — minden nagyobb szekció megírása után futtass le egy célzott ellenőrzést, és ha hibát találsz, javítsd még mielőtt továbblépnél. Ne várd meg a végső minőségellenőrzést.

### 1. Tervezett módosítások után

- Lefedi-e minden spec-beli követelmény valamelyik fájl módosítása? Menj végig a spec `Komponensek és viselkedés` szekcióján soronként.
- Minden spec-ben említett új komponenshez (tech stacktől függetlenül) meg van-e tervezve a projekt struktúra, build rendszer és deployment mechanizmus? Nem elég a mock — ha a spec valós implementációt ír elő, annak is szerepelnie kell.
- Minden új service/komponens el tud-e érni mindent amire szüksége van (importok, config mezők, DI paraméterek)?
- Meglévő fájlok módosításainál: a standard flow érintetlen marad? (visszafelé kompatibilitás)
- Minden új tesztelhető komponenshez (service, route, app) meg van-e tervezve a DI override típusa?
- **Meglévő komponens README:** Ha a ciklus meglévő komponens konfigurációját (env var-ok, indítási paraméterek, külső kapcsolatok) változtatja meg, a komponens `README.md`-je is érintett fájlként szerepel a Tervezett módosításokban?

Ha bármely pontra nem, egészítsd ki a tervezett módosításokat, majd folytasd.

### 2. Teszt specifikáció után

- Az **E2E infrastruktúra szekció** kitöltött és a teszt stratégia megállapodott (lezárt kérdés a `plan-questions.md`-ben)?
- A spec DoD-jában szereplő E2E elfogadási feltétel le van-e fedve valamelyik E2E tesztesettel?
- A spec `Teszt specifikáció` vagy hibamátrix minden bejegyzéséhez van-e TC a plan Teszt specifikációjában?
- **Regressziós érintettség kitöltve?** — Ha a ciklus meglévő kódot módosít, a `Regressziós érintettség` táblázat tartalmazza az összes érintett meglévő tesztfájlt és E2E scriptet. Ez különösen kritikus, ha:
  - Meglévő interfész új elágazással bővül — a meglévő hívási út tesztjei explicit felsorolandók
  - Közös komponens módosul — minden érintett fogyasztó tesztje szerepel a listában
  - Ugyanarra a belépési pontra új viselkedés kerül — mindkét ág tesztjei megnevezve
- Minden új exportált függvényhez / végponthoz van-e legalább egy unit test eset?
- A happy path e2e-ben lefedett? Minden hiba-ág, amelyet a spec explicit definiál, szerepel valamelyik TC-ben?
- A TC-k Elvárt kimenet oszlopa tartalmazza a HTTP státuszt és az errorCode-ot (ahol a spec hibamátrixa definiálja)?
- **Negatív tesztesetek:** minden új végponthoz, üzleti logikához vagy validációhoz van-e legalább egy negatív TC (hibás bemenet, hiányzó paraméter, jogosultsági hiba, timeout)?
- **Szerver elérhetőségi smoke teszt:** Minden olyan szerver esetén, amellyel a böngésző közvetlenül kommunikál (nem proxy-n keresztül), szerepel-e legalább egy **browser E2E teszt, amely network mocking nélkül valódi HTTP kérést küld** a szervernek? Ez a teszt CORS-t, hálózati elérhetőséget és preflight kezelést ellenőriz — ha a tényleges üzleti kérés hibával tér is vissza (pl. 401), az elfogadható; a lényeg, hogy a böngésző elküldte a kérést és kapott választ. A teszt pontosan akkor bukik, ha a böngésző CORS-blokkal nem tud kommunikálni a szerverrel.

Ha bármely pontra nem, egészítsd ki a Teszt specifikációt, majd folytasd.

### 3. Végrehajtási sorrend után

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

Ha hiányosságot vagy ellentmondást találsz, **ne döntsd el magad** — irányítsd vissza a spec fázisba (lásd lentebb).

> **„Ne találd ki magad" — hol a határ?** Akkor választhatsz alapértelmezést kérdés nélkül, ha a döntés **tisztán technikai** és a spec viselkedését nem érinti (pl. egy belső segédfüggvény neve, egy adatstruktúra belső reprezentációja). **Kötelező kérdezni** (`plan-questions.md`), ha a döntés **megfigyelhető viselkedést** befolyásol (pl. milyen HTTP kódot ad egy hibaág, mi a retry policy, melyik mező kerül a response-ba) — ezt a spec-nek kell rögzítenie, nem neked.

---

## Megállási szabályok

**Minden felmerülő kérdést — bármilyen okból — azonnal vedd fel a `plan-questions.md`-be a következő szekvenciális számmal (`K01`, `K02`, ...) `- [ ]` státusszal, mielőtt feltennéd a felhasználónak.** Ez vonatkozik az alább felsorolt összes esetre, és bármilyen más bizonytalanságra is. A kérdés csak a listába kerülés után kerül a felhasználó elé.

**Ha van `[ ]` státuszú kérdés a `plan-questions.md`-ben**, ne kezdj el plan szekciókat írni — előbb tegyél fel egyet a felhasználónak, várj a válaszra, jelöld `[x]`-szel, majd folytasd.

Ha plan írása közben az alábbiak bármelyike teljesül, **STOP — állj meg és jelezd a felhasználónak** (ne döntsd el magad a hiányzó/ellentmondó részt):

- **Komplex vagy bizonytalan konténerizáció**: Ha a tesztkörnyezetben lévő bármely komponens konténeres futtatása, konfigurálása vagy hálózati összekötése nem triviális vagy bizonytalan. → Ne próbáld meg egyedül kitalálni a portokat/konfigurációkat; vedd fel a kérdést a `plan-questions.md` fájlba, állj meg, és kezdeményezz közös tervezést a felhasználóval.

- **Implementációs döntési pont**: több egyenrangú technikai megközelítés létezik és a választás nem egyértelmű a spec alapján. → Tegyél fel **egy** kérdést, várj a válaszra, majd folytasd a plan-t.

- **Spec hiányosság**: a spec nem definiál egy szükséges viselkedést, hibalesetet vagy határt. → **Ne töltsd ki magad.** Vedd fel `[ ] Knn` kérdésként a `plan-questions.md`-be, és jelezd a felhasználónak pontosan mi hiányzik — a spec fázisba kell visszatérni és ott frissíteni a `spec.md`-t. A spec frissítése és `Tervezésre kész` státusz visszaállítása után újrakezdhető a plan fázis.

- **Spec ellentmondás / elavult kód**: a spec két pontja vagy a spec és a meglévő kód egymásnak ellentmond. (Például: ha a specifikáció olyan komponens módosítását kéri, amely elavult, használaton kívüli, vagy ellentmond a jelenlegi kód valóságának, állj meg, és kérdezz rá a `plan-questions.md`-ben, ne tervezz be felesleges módosítást megjegyzésekkel!) → Jelezd mindkét oldalt, és várd meg a felhasználó döntését. Ne válassz.

- **Kockázat feloldáshoz user döntés kell**: egy kockázat nem kezelhető a spec alapján önállóan. → Egy kérdés, válasz, folytatás.

Minden esetben csak **egy** kérdést tegyél fel egyszerre — várd meg a választ, pipáld ki a kérdést (`- [x] Knn → [döntés]`), majd lépj a következőre.

---

## Minőségellenőrzés — plan lezárása előtt

Mielőtt \`Task írásra kész\` státuszra váltasz, tedd fel magadnak:

- Hiányzik még valami a plan-ből?
- Van bármi, ami nem egyértelmű vagy kétértelmű?
- A végrehajtási sorrend valóban függőségek alapján rendezett?
- Minden érintett fájl szerepel a tervezett módosításokban?
- **Dokumentációk frissítése:** Minden, a változtatások által érintett leírás, README és diagram (pl. `.drawio` fájl) fel van-e tüntetve a tervezett módosítások között?
- **Kommentek és docstringek:** A tervezett módosítások figyelembe veszik-e a forráskódban lévő kommentek és leírások frissítését az új elnevezéseknek/működésnek megfelelően?
- **Fájl elérési utak formátuma:** Minden fájl elérési útja és linkje a fájl aktuális könyvtárához képest relatív útvonal legyen (a mappa mélységének megfelelő számú visszalépéssel a projekt gyökeréig, pl. `../../apps/legacy-login/config/users.json`)? Abszolút útvonalak vagy `file://` sémájú linkek sehol nem szerepelhetnek a dokumentációban.
- A `Teszt specifikáció` szekció tartalmaz teszteseteket minden érintett komponenshez?
- Minden teszteset Elvárt kimenet oszlopa tartalmaz HTTP státuszt és errorCode-ot (ahol a spec hibamátrixa definiálja)?
- A unit tesztek a végrehajtási sorrendben az implementáció ELŐTT szerepelnek?
- Minden szükséges schema artifact azonosítva és a táblázatban szerepel?
- **Adatbázis módosítások:** Ha a ciklus sémaváltozást/új entitást hoz be, meg van-e tervezve és dokumentálva a migrációs és rollback (visszaállítási) forgatókönyv?
- Minden schema artifact státusza `Reviewed`? (Ha van `Review Required`, a plan nem zárható le.)
- **Constitution Check (SK4):** minden plan-döntés (tech stack, naming, struktúra, teszt eszköz, merge stratégia, biztonság) összhangban van a `conventions.md`-vel?
  - **Kis eltérés** (pl. egy elnevezés finomítása): vedd fel a `plan-questions.md`-be, és kérdezz rá a felhasználótól.
  - **Súlyos eltérés** (alapvetően ütközik a konvenciókkal): **STOP**, vissza a `02` vagy `00` fázishoz a konvenció felülvizsgálatára.

Ha bármelyikre nem teljesül a feltétel (vagy hiányzik valami), egészítsd ki a plan-t, mielőtt lezárod.

---

## Státusz kezelés

- Plan indításakor: \`Piszkozat\`
- Ha kérdés kerül a `plan-questions.md`-be: \`Nyitott kérdések vannak\`
- Ha minden kérdés `[x]`, minden szekció kitöltve, minden schema artifact `Reviewed`, a minőségellenőrzés (+ Constitution Check) átment, **és a felhasználó explicit megerősítette**: \`Task írásra kész\`

> **Kész lifecycle:** a `plan.md` a `Task írásra kész` után a ciklus végén — amikor a validate (07) PASS lezárja a ciklust — `Kész` státuszra lép. A 08 fázis már `Kész`-t vár. Ezt az átmenetet a 07 végzi, itt nem.

Ha a felhasználó megerősíti:
- Állítsd a `plan.md` státuszát `Task írásra kész`-re.
- Készíts git commitot a fázis befejezéséről:
  ```bash
  git add specs/cycle-NN-<cycle-name>/
  git commit -m "cycle-NN: 03-plan"
  ```

Ha a státusz \`Task írásra kész\`, állj meg. Ne kezdj task listát. Jelezd a felhasználónak a következő lépést és a fázis indító promptját, például:
> *"A plan kész. Folytathatjuk a 4. lépéssel (tasks). Használd ezt a promptot:*
> ```
> Kövesd a `prompts/skills/04-write-tasks.md` utasításait.
> Input: `specs/cycle-NN-<cycle-name>/plan.md`
> ```"*

---

## Fix-mód (analyze-hurok belépő)

> **Mikor aktív:** ezt a szekciót az `05-analyze` önjavító hurka indítja az `agents/plan-fixer.md` wrapperen keresztül — **nem** a normál plan-írás. A bemenet egy konkrét `Must Fix` lista, nem teljes újrafutás.

A fix-mód egy **szűkített belépő:** a megadott `Must Fix` megállapításokat javítod célzottan, **nem írod újra az egész plant**. (Ellenkező esetben egy olcsóbb LLM hajlamos elölről kezdeni a fázist — ez tilos.) A normál flow minőségi kapui (minőségellenőrzés + Constitution Check) a javított részekre továbbra is érvényesek.

### Két belépési alak
1. **Közvetlen javítás:** a `Must Fix` megállapítás a plant érinti (a célfázis 03) — célzottan javítod.
2. **Downstream re-deriválás (reconciliation):** a hurok feljebb (02, spec) javított, és a plant a megváltozott spec-hez kell **összehangolni**. Ez **célzott reconciliation, nem teljes újraírás:** csak a megváltozott spec-szakaszokhoz tartozó plan-részeket igazítod, a lezárt `plan-questions.md` döntéseket **megőrzöd**.

### Bemenet
- A planre szűrt `Must Fix` lista (kategória + leírás + `fájl:hely`), vagy reconciliation esetén a megváltozott upstream (spec) összefoglalója.
- A `plan.md` és a `plan-questions.md` aktuális állapota.

### Auto-javítható vs kérdezni kell (a határvonal)

| Magától javítsd (auto) | Kérdésbe tedd (`plan-questions.md` új `Knn`) |
|---|---|
| Lefedettségi/komponens-leképezés pontosítása, naming-egységesítés, tervezési duplikáció összevonása, spec-változás átvezetése a planbe | Megfigyelhető viselkedést érintő technikai döntés (HTTP kód, retry policy, response mező), meghatározatlan komponens technológiai alapdöntése, spec-ellentmondás |

A `Must Fix`-et, amihez **valódi döntés** kell, **ne találd ki** — vedd fel új `Knn`-ként a `plan-questions.md` végére, és **ne kérdezd közvetlenül a felhasználót** (fix-módban nincs interaktív csatornád). A kérdezést az orchestrátor (`05-analyze`) végzi. (Lásd a fenti „Ne találd ki magad — hol a határ?" szabályt — fix-módban is ugyanaz a határvonal.)

### Státusz (auto, `[analyze-loop]` marker)
A hurok a `plan.md` státuszát `[analyze-loop]` markerrel nyitotta vissza (pl. `Piszkozat [analyze-loop]`). Amíg a marker jelen van, **automatikusan** lépteted a státuszt, megerősítés-kérés nélkül:
- van nyitott `[ ]` kérdés a `plan-questions.md`-ben → `Nyitott kérdések vannak [analyze-loop]`;
- minden kérdés `[x]`, minden szekció rendben, minden schema artifact `Reviewed`, a célzott javítás kész → `Task írásra kész [analyze-loop]`.

A marker fel- és levételét az orchestrátor kezeli; te csak a státusz-értéket lépteted.

### Visszatérési összefoglaló (az orchestrátornak)
Adj vissza tömör összefoglalót: (a) mely `Must Fix`-eket / spec-változásokat vezettél át és hogyan, (b) milyen új `Knn` kérdéseket vettél fel a `plan-questions.md`-be (azonosítóval). A `plan.md`-t és a `plan-questions.md`-t te írod; az `analyze-report.md`-t **nem** — az az orchestrátoré.
