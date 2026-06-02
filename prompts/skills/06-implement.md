---
phase: 06
name: implement
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

Ez a fejlesztési folyamat **6-os fázisa (a 0–8 fázisokból)**:
0. projekt inicializálás (setup)
1. ciklusok kezelése (setup)
2. spec
3. plan
4. tasks
5. analyze
6. **implement** ← most itt vagyunk
7. validate
8. review & merge

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

**Két forrásból érkezhet visszalépés ide:** (a) a 07-validate FAIL ágáról (`## Validációs javítások` taskok a `tasks.md` végén), vagy (b) a 08-review-and-merge FAIL ágáról (`## Review javítások` taskok + `code-review.md`). Mindkét esetben a `tasks.md` végén lévő új taskok az elvégzendők; a 08 esetén olvasd be a `code-review.md`-t is (lásd a Kontextus betöltési szabályok és a Végrehajtási szabályok 2. pontját). Az alábbi döntési fa ugyanúgy érvényes — a kód tényleges állapotából indulj ki.

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
- **Review visszacsatolás:** Ha a `tasks.md` tartalmaz review-ból származó javítási feladatokat (vagy a folyamat a 08-as review & merge fázisból lépett vissza ide), olvasd be a `specs/cycle-NN-<cycle-name>/code-review.md` fájlt is, hogy megértsd a javítások kontextusát és elvárásait.
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
