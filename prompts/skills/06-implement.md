---
phase: 06
name: implement
description: "Használd, ha az analyze-report.md 'PASS' (Phase 06), a tényleges kódfejlesztéshez. Végrehajtja a tervezett kódmódosításokat a feladatlista alapján, és közben vezeti a 'tasks.md'-t, amíg az el nem éri a 'Validálásra kész' állapotot."
prerequisites:
  - "specs/cycle-NN-<name>/tasks.md státusz: Implementálásra kész"
  - "specs/cycle-NN-<name>/analyze-report.md státusz: PASS"
output:
  - "Implementált kód"
  - "specs/cycle-NN-<name>/tasks.md státusz: Validálásra kész"
prev: 05-analyze
next: 07-validate
subagents: []
---

# 06 — Implementálás

Spec driven development-ben fejlesztünk szoftvert. A fejlesztés ciklusokra van bontva. Minden ciklus egy önállóan lefejleszthető, önállóan tesztelhető részegysége a teljes implementációnak.

Ez a fejlesztési folyamat **6-os fázisa (a 0–9 fázisokból)**:
0. projekt inicializálás (setup)
1. ciklusok kezelése (setup)
2. spec
3. plan
4. tasks
5. analyze
6. **implement** ← most itt vagyunk
7. validate
8. doc-sync
9. review & merge

---

## Előfeltétel

Olvasd be a `tasks.md` státuszát. **Ha a státusz nem `Implementálásra kész`, ne kezdj implementálni.** Jelezd a felhasználónak, hogy a tasks lista még nem zárult le.

Futtasd: `git status --short`. Ha van commitálatlan változtatás:
- Listázd ki az érintett fájlokat.
- Jelezd: *"Az implementáció előtt érdemes ezeket commitálni — ha félremegy az implementáció, egy `git reset --hard` visszaállítja a kiindulóállapotot."*
- Kérdezd meg: *"Commitáljam ezeket most?"* — Ha igen: commitáld a változtatásokat, majd folytasd. Ha nem: folytasd commit nélkül.

---

## Feladatod

Implementáld a `tasks.md` taskjait sorban, egyenként.

**Kövesd a projekt meglévő kód konvencióit** — naming, struktúra, tesztszervezés a forráskódból levezethetők. Ha `conventions.md` létezik a projekt gyökerében, olvasd be azt is.

**Folytatás megszakított futás után:** az implementáció bármikor félbeszakadhat — akár az első task közepén is, mielőtt bármit pipáltak volna. Mindig ellenőrizd a tényleges kód állapotát, ne csak a jelöléseket.

**Két forrásból érkezhet visszalépés ide:** (a) a 07-validate FAIL ágáról (`## Validációs javítások` taskok a `tasks.md` végén), vagy (b) a 09-review-and-merge FAIL ágáról (`## Review javítások` taskok + `code-review.md`). Mindkét esetben a `tasks.md` végén lévő új taskok az elvégzendők; a 09 esetén olvasd be a `code-review.md`-t is (lásd a Kontextus betöltési szabályok és a Végrehajtási szabályok 2. pontját). Az alábbi döntési fa ugyanúgy érvényes — a kód tényleges állapotából indulj ki.

Döntési fa a folytatáshoz — **ebben a sorrendben**:

```
1. Van [x]-szel jelölt task?
   → Olvasd be az általa érintett forrásfájlokat, és ellenőrizd, hogy a változtatások valóban megvannak-e.
   → Ha a kód ELLENTMOND a [x] jelölésnek: NE jelölj vissza semmit.
     Jelezd: "A [Tkkk] task [x]-ként van jelölve, de a kód alapján úgy tűnik, hogy [X] nincs kész. Hogyan tovább?"
     Várj a válaszra.

2. Van részben kész [ ] task (az érintett fájlokban van már valami)?
   → Folytasd onnan, ahol abbahagyták. Ne nulláról kezdd.

3. Nincs semmi megkezdve?
   → Kezdd az implementációt az első [ ] tasktól.
```

---

## Kontextus betöltési szabályok

- Implementálás megkezdése előtt olvasd be a `tasks.md`-t, majd a benne felsorolt **Prerequisite dokumentumokat**. Ezek tartalmazzák a függvényszignatúrákat, interfészeket, hibakezelési logikát.
- **Review visszacsatolás:** Ha a `tasks.md` tartalmaz review-ból származó javítási feladatokat (vagy a folyamat a 09-es review & merge fázisból lépett vissza ide), olvasd be a `specs/cycle-NN-<cycle-name>/code-review.md` fájlt is, hogy megértsd a javítások kontextusát és elvárásait.
- Minden tasknál **csak az adott taskban megnevezett forrásfájlokat** olvasd be — és csak a releváns részeiket. A task logikai kontextusa a Prerequisite dokumentumokban van.
- Ne olvasd be a spec-et.
- **Forrás lokalizálás**: ha a task komponenst vagy függvényt nevez meg, de a pontos fájl/sor nem ismert — indíts subagent-et a kereséshez. A subagent visszaadja a path-t és a releváns sorokat, nem a teljes fájlt.
- **Nagy fájl**: ha az érintett fájl nagy és csak egy szekció releváns — indíts subagent-et a kinyeréshez. Ne töltsd be a teljes fájlt a fő kontextusba.
- Kis, ismert fájloknál: direkt read.

---

## Tervezési elvek

**Deep module — ne shallow module:** Új függvényt vagy modult írva törekedj arra, hogy sok logikát rejtsen el egyszerű interfész mögé. A hívónak ne kelljen tudnia a belső részletekről. Ha egy új függvény egyetlen sort csinál de komplex paramétert vár, gondold újra — valószínűleg a hívó oldalra tolod a komplexitást.

**Kódkommentek:** Minden függvénynek legyen egy egysoros fejléc-kommentje, amely leírja, mit csinál. Nem triviális logikához, external API hívásokhoz és döntési pontokhoz fűzz rövid, egy-soros magyarázatot — olyan szinten, hogy más programnyelvből érkező fejlesztő is értse a szándékot. Triviális sorokhoz (pl. `return result`, egyszerű getter) nem kell komment.
- **Kommentek és docstringek naprakészen tartása:** Ha egy meglévő kódrészletet, függvényt, változót vagy végpontot módosítasz vagy átnevezel, a hozzájuk tartozó magyarázó kódkommenteket, JSDoc/TSDoc docstringeket és típus-annotációkat is **kötelezően frissíteni kell** az új elnevezéseknek és működésnek megfelelően. Elavult (stale) kommentek nem maradhatnak a kódban.

---

## Végrehajtási szabályok

1. Vedd a következő elvégzetlen taskot (`- [ ]`).

2. **Visszalépés kódellenőrzésből (08):** Ha a ciklus sikertelen kódellenőrzés (08) miatt került vissza ide, a `tasks.md` végén lévő új feladatokat a `code-review.md` kritikus észrevételei alapján végezd el. A javítások után a záró `[CHECK]` feladatok újbóli futtatása és commitolása kötelező.

3. **Fejezet-szintű előfeltétel ellenőrzés:** A `tasks.md`-ben a fejezetek `##` szintű blokkokra tagolódnak. (Ha egy task nem esik egyetlen `##` blokkba sem — pl. a lista elején áll fejezetcím nélkül —, kezeld önálló, előfeltétel nélküli taskként, és folytasd a 4. ponttal.) Ha a kiválasztott task az adott fejezet (adott `##` blokk) első elvégzetlen taskja (vagyis a fejezeten belül ez az első `- [ ]`): keresd meg a fejezet fejlécét a `tasks.md`-ben, és nézd meg, hogy közvetlenül alatta van-e `> **Gépi előfeltétel:**` blokk. Ha van: olvasd el a feltételeket, és döntsd el, hogy teljesülnek-e. Ha nem teljesülnek: állj meg, és jelezd a felhasználónak pontosan, mit kell beállítani: *„A(z) [fejezet neve] fejezet megkezdéséhez a következő feltételeknek kell teljesülniük: [feltételek]. Teljesülnek-e ezek?"* — várj a válaszra, mielőtt egyetlen taskot is elkezdenél a fejezetből.

4. **Mielőtt elkezdenéd: döntsd el, hogy a task elvégezhető-e most.** Egy task halasztott lehet, ha: teljes futó stacket igényel (konténerek, valódi Keycloak, E2E infrastruktúra), vagy a csoport összes többi taskja is elvégzetlen és mind hasonló jellegű. Ha a task halasztottnak tűnik, ne próbáld meg végrehajtani — kérdezz rá: *"[Tkkk] infrastruktúra-függő tasknak tűnik (pl. E2E, konténer, valódi Keycloak). Fut a stack, vagy keressem meg a következő elvégezhető implementációs taskot?"*

5. Olvasd be a task által érintett fájlokat.

6. Implementáld pontosan azt, amit a task leír — ne többet, ne kevesebbet.

7. Ne refaktorálj érintetlen kódot. Ne adj hozzá nem kért feature-t.

8. **`[CHECK]` task végrehajtása:**
   - Futtasd le a megadott parancsot.
   - Ha hibát jelez, javítsd a csoporton belüli előző taskokat, majd futtasd újra.
   - Csak zöld `[CHECK]` után jelölhető kész (`- [x]`) a csoport — a `[RED]`/`[GREEN]` taskokat is csak ekkor zárd le.
   - **3 próba szabály:** Ha a `[CHECK]` háromszor egymás után hibával tért vissza, és a csoporton belüli javítási kísérletek sem vezettek eredményre — **állj meg**. Írd le, mit próbáltál, és jelezd a felhasználónak: *"[Tkkk] háromszor sikertelen volt. [Rövid összefoglalás a hibáról és a próbált megoldásokról.] Hogyan tovább?"*
   - **Portütközés:** Ha service indítása vagy teszt futtatása portütközéssel (address already in use) meghiúsul, ne állj meg. Keresd meg a következő szabad portot (`ss -tlnp | grep :<port>` vagy `lsof -i :<port>`), frissítsd átmenetileg az érintett konfigurációban (`docker-compose`, env fájl), és futtasd újra. Jelezd a felhasználónak melyik portot használtad helyette.
     > **⚠ ÁTMENETI MÓDOSÍTÁS — NE COMMITOLD:** a portütközés miatti config-/port-változtatás ideiglenes. A task commitja előtt ÁLLÍTSD VISSZA, vagy zárd ki a `git add`-ból (ne kerüljön a ciklus diffjébe). Csak a task tényleges kódváltozása commitolható.

9. **`⟂ Tkkk` jelölés:** az adott task és a hivatkozott task egymástól független — ha egyszerre elvégezhetők, hívd meg mindkét szerkesztést párhuzamosan.
   - **Példa:** ha T012 tartalmazza `⟂ T013`, akkor T012 és T013 egyszerre szerkeszthetők.
   - **Kivétel:** ha mindkét task ugyanazt a fájlt érinti, futtasd őket sorban.

10. **Ideiglenes erőforrások takarítása**: Ha a task végrehajtása során ideiglenes fájlokat hoztál létre vagy konténereket indítottál el, a task (vagy `[CHECK]`) befejezése után töröld ki a fájlokat és állítsd le / töröld a konténereket. Ne hagyj magad után maradványokat a következő task számára.

11. **Jelöld késznek a `tasks.md`-ben:** állítsd a task checkboxát `- [x]`-re. **Ez a `tasks.md` módosítás is a commit része** — a kód és a workflow-állapot nem csúszhat szét.

12. **Git commit:** A task sikeres befejezése és a csoportzáró `[CHECK]` (vagy a task saját ellenőrzése, ha nincs csoport) zöldre futása után commitáld a változtatást **az érintett forrásfájlokkal ÉS a `tasks.md`-vel együtt**:
    ```bash
    git add <érintett fájlok> specs/cycle-NN-<cycle-name>/tasks.md && git commit -m "cycle-NN: Tkkk - <task leírása>"
    ```
    ahol `NN` a ciklus száma (pl. `16`), `Tkkk` a task azonosítója (pl. `T001`), a leírás pedig a task szövegének tömörített változata.
    **Példa:** `cycle-16: T001 - add initHash function to token-store`
    A `[RED]` és `[GREEN]` állapotokat is külön commitold.

13. Jelezd a felhasználónak melyik task készült el, és lépj a következő taskra. **A válasz végén helyezz el egy közvetlen, kattintható markdown linket a `tasks.md`-re.**

---

## Megállási szabályok

Ha implementálás közben az alábbiak bármelyike teljesül, **STOP — állj meg és jelezd a felhasználónak** (ne sodródj tovább, ne próbálj „kreatívan" továbblépni):

- A task leírása ellentmond a meglévő kódnak és nem egyértelmű a helyes megoldás.
- A task elvégzéséhez olyan fájlt kellene módosítani, ami nincs benne a task leírásában.
- Egy task feltételezi egy korábbi task eredményét, de az még nincs kész.
- **Egy `[CHECK]` task háromszor egymás után hibával tért vissza** (lásd 8. szabály).

Minden esetben csak **egy** kérdést tegyél fel, várj a válaszra, majd folytasd.

---

## Problémamegoldás dokumentálása

Ha egy task elvégzése során legalább 3 sikertelen kísérlet után sikerül megoldani a problémát, hozd létre vagy bővítsd a `specs/cycle-NN-<cycle-name>/imp-decision.md` fájlt:

```md
## <Task azonosító> — <rövid cím>

**Mi volt a gond:** <a hiba tömör leírása>
**Mit próbáltunk:** <sikertelen kísérletek röviden>
**Mi lett a megoldás:** <a végül működő megközelítés>
```

Ha a fájl már létezik, append-elj — ne írd felül a korábbi bejegyzéseket.

---

## Új komponens README

_(Emlékeztető a 03-plan `README.md` követelményéről — itt a végrehajtás történik, nem új követelmény.)_ Ha egy task új komponenst hoz létre (új alkalmazás, új service, új önálló modul), a komponens gyökér mappájában kötelező létrehozni egy `README.md` fájlt. Tartalma:

- **Mit csinál** — egy-két mondat a komponens felelősségéről
- **Indítás** — konkrét parancs(ok) a helyi futtatáshoz
- **Port** — milyen porton hallgatózik
- **Debug** — ha értelmes: hogyan kell debuggolni, milyen debug portot használ
- **Logok** — milyen eseményeket naplóz, milyen log szintek vannak
- **Kapcsolatok** — milyen más komponensektől függ, miket hív, mi hívja őt

A README.md az implementáció része — nem utólagos dokumentáció. Akkor kell elkészülnie, amikor a komponens kész.

---


## Státusz kezelés

- Implementálás közben: `Implementálás folyamatban`
- Ha minden task `[x]`: frissítsd a `tasks.md` státuszát `Validálásra kész`-re, és **commitold ezt az állapotváltozást** (a végső státusz külön legyen rögzítve):
  ```bash
  git add specs/cycle-NN-<cycle-name>/tasks.md && git commit -m "cycle-NN: 06-implement - kész, validálásra kész"
  ```

Ha a státusz `Validálásra kész`, állj meg. Jelezd a felhasználónak a következő lépést és a fázis indító promptját, például:
> *"Az implementáció kész. Folytathatjuk a 7. lépéssel (validate). Használd ezt a promptot:*
> ```
> Kövesd a `prompts/skills/07-validate.md` utasításait.
> Input: `specs/cycle-NN-<cycle-name>`
> ```"*

---

## Fix-mód (validate- és review-hurok belépő)

> **Mikor aktív:** ezt a szekciót egy önjavító hurok indítja egy fixer-wrapperen keresztül — **nem** a normál implementáció. Két hívó van, azonos mechanikával, csak a bemeneti szekció és a marker más:
> - **validate-hurok (07):** `agents/implement-fixer.md` → bemenet a `tasks.md` `## Validációs javítások` taskjai (teszt-/Sonar-/DoD-hibák), marker `[validate-loop]`;
> - **review-hurok (08):** `agents/review-fixer.md` → bemenet a `tasks.md` `## Review javítások` taskjai (a `code-review.md` `Must Fix` findingjai), marker `[review-loop]`.
>
> Mindkét esetben egy **konkrét hibalista** célzott javítása a feladat, nem a teljes ciklus újra-implementálása.

A fix-mód egy **szűkített belépő:** a megadott teszt-/Sonar-/DoD-hibákat javítod célzottan, **nem implementálod újra a ciklust** (2.2). (Ellenkező esetben egy olcsóbb LLM hajlamos elölről kezdeni a fázist — ez tilos.) A 06 normál végrehajtási és minőségi szabályai (a `[CHECK]` zöldre futtatása, kódkomment-frissítés, deep module) a javított részekre továbbra is érvényesek.

### Bemenet
A hívótól függően a `tasks.md` végén lévő javító-szekció elvégzetlen `[GREEN]`/`[CHECK]` taskjai, a szekció elején lévő prerequisite hivatkozásokkal együtt:
- **validate-hurok:** `## Validációs javítások` (a 07 vette fel a konkrét teszt-/Sonar-hibákból); prerequisite:
  - `specs/cycle-NN-<cycle-name>/test-report/validate-decision.md` (a `# Validation History` a hibák részleteivel),
  - ha Sonar hibázott: `specs/cycle-NN-<cycle-name>/test-report/sonar-report.md`.
- **review-hurok:** `## Review javítások` (a 08 vette fel a `Must Fix` findingokból); prerequisite:
  - `specs/cycle-NN-<cycle-name>/code-review.md` (a findingok + a `# Review History`).
- A `tasks.md` aktuális állapota (`Implementálásra kész [validate-loop]` **vagy** `[review-loop]` státusz).

### Fix-mód ↔ normál implement elhatárolása (2.2)
- **Fókusz:** kizárólag az aktív javító-szekció taskjai (`## Validációs javítások` VAGY `## Review javítások`) — a konkrét megbukott tesztek / Sonar-hibák / nem teljesült DoD-pontok / `Must Fix` findingok javítása.
- **Nem teljes újra-implementáció:** a már zöld, lezárt taskokat (`[x]`) ne futtasd újra és ne írd át. Csak a hibalistára dolgozol.
- A 06 már ismeri mindkét belépést (lásd „Két forrásból érkezhet visszalépés ide" — a `## Validációs javítások` és a `## Review javítások` ág); a fix-mód erre épül, nem duplikálja.

### Státusz (auto, `[validate-loop]` / `[review-loop]` marker)
A hurok a `tasks.md` státuszát a saját markerével nyitotta vissza (`Implementálásra kész [validate-loop]` a 07-ből, illetve `Implementálásra kész [review-loop]` a 09-ből). Amíg a marker jelen van, **automatikusan** lépteted a státuszt, megerősítés-kérés nélkül (eltérően a normál „megerősítés a státuszváltás előtt" szabálytól) — a markert végig megtartva:
- javítás közben: `Implementálás folyamatban [<aktív-loop>]`;
- ha az aktív javító-szekció minden taskja `[x]` és a csoportzáró `[CHECK]` zöld: `Validálásra kész [<aktív-loop>]`.

A marker fel- és levételét az orchestrátor (`07-validate` ill. `09-review-and-merge`) kezeli; te csak a státusz-értéket lépteted.

### ⚠ Anti-„csalás" garde (VD3 / RD4 — kötelező)

**A fix-mód a KÓDOT igazítja a teszthez / Sonarhoz / DoD-hoz / a review-findinghoz — SOHA nem fordítva.** A teszt, a DoD és a reviewer `Must Fix` findingja a **szerződés**, azt a fix-mód nem gyengítheti és nem némíthatja el.

**TILOS** a zöld/tiszta eredmény bármilyen kikényszerítése a szerződés megkerülésével:
- teszt assertion gyengítése, lazítása, vagy elvárt érték a kódból visszamásolása;
- teszt `skip`/`xfail`/kikommentezése/törlése;
- hardcode-olt „elvárt" érték, amely csak a tesztet zöldíti, de a valós viselkedést nem valósítja meg;
- a `spec.md` Definition of done pont leszállítása vagy átfogalmazása, hogy könnyebben teljesüljön;
- **(review-hurok, RD4)** a `Must Fix` finding **kozmetikai elnémítása** a gyökérok javítása nélkül (lint-suppress komment, a kifogásolt kód álcázása), vagy a `code-review.md` finding törlése/átfogalmazása javítás nélkül.

**Ha úgy ítéled meg, hogy egy hibát CSAK a szerződés (teszt/DoD/spec) megváltoztatásával vagy a finding elnémításával lehetne zöldre/tisztára vinni** — az **nem kód-fix**. **STOP**: ne nyúlj a szerződéshez, hanem add vissza az orchestrátornak a visszatérési összefoglalóban **eszkalációs jelzéssel** (lásd lent). Ez a felfelé menekülő ág bemenete — validate-hurokból a 07 VD5, review-hurokból a 09 RD6 (a tervezési/szerződés-kérdést a 03/02 fázisban kell rendezni, nem itt).

### Visszatérési összefoglaló (az orchestrátornak)
A futásod végén adj tömör összefoglalót a hívó orchestrátornak (`07-validate` vagy `09-review-and-merge`):
- **Elvégzett javítások:** mely javító-taskokat zártad le, és hogyan (hibánként/findingonként egy sor) — milyen kódváltozással lett zöld/kész.
- **Eszkalációs jelzés (ha van):** ha valamelyik hibát csak a szerződés (teszt/DoD/spec) módosításával vagy a finding elnémításával lehetne zöldre/tisztára vinni (VD3/RD4 tiltja) → jelezd egyértelműen: *„ESZKALÁCIÓ: [item] tervezési/szerződés-hibának tűnik — csak a szerződés módosításával vagy a finding elnémításával lenne zöld; nem javítottam."* Add meg, miért.
- **A `tasks.md` aktuális státusza** (a `[validate-loop]` / `[review-loop]` markerrel).

A kódot és a `tasks.md` aktív javító-szekcióját (`## Validációs javítások` / `## Review javítások`) te írod; a `validate-decision.md`-t és a `code-review.md`-t **nem** — azok az orchestrátoré.
