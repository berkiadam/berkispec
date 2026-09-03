---
phase: 06
name: bs-implement
description: "berkispec - 06. Használd, ha az analyze-report.md 'PASS' (Phase 06), a tényleges kódfejlesztéshez. Végrehajtja a tervezett kódmódosításokat a feladatlista alapján, és közben vezeti a 'tasks.md'-t, amíg az el nem éri a 'Validálásra kész' állapotot."
prerequisites:
  - "specs/cycle-NN-<name>/tasks.md státusz: <status:ready_for_implement>"
  - "specs/cycle-NN-<name>/analyze/analyze-report.md státusz: PASS"
output:
  - "Implementált kód"
  - "specs/cycle-NN-<name>/test-report/implement/check-log.md — a [CHECK] futások append-only naplója (TR5)"
  - "specs/cycle-NN-<name>/tasks.md státusz: <status:ready_for_validate>"
prev: bs-analyze
next: bs-validate
subagents:
  - "agents/researcher.md"
scripts:
  - "scripts/test-substance-check.py — vacuous teszt-törzs kapu (TB1)"
  - "scripts/report-gate-check.py — riport-fázis kapu (TR6)"
shared:
  - "shared/parallel-cycles.md"
---
# 06 — Implementálás
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

Spec driven development-ben fejlesztünk szoftvert. A fejlesztés ciklusokra van bontva. Minden ciklus egy önállóan lefejleszthető, önállóan tesztelhető részegysége a teljes implementációnak.

Ez a folyamat **6. fázisa (0–9)**: 0-init · 1-ciklusok · 2-spec · 3-plan · 4-tasks · 5-analyze · **6-implement ←** · 7-validate · 8-doc-sync · 9-review.

---

## <field:f_prerequisite>

0. **Ciklus-beazonosítás:** ha a felhasználó megadott ciklust/fájlt, azt használd; különben a legfrissebb `specs/cycle-*` mappát ajánld fel megerősítésre — <!-- INCLUDE:lang/common.md#ciklus-beazonositas --> — és várj a válaszra, mielőtt továbblépsz.

1. Olvasd be a `tasks.md` státuszát. **Ha a státusz nem `<status:ready_for_implement>`, ne kezdj implementálni.** Jelezd a felhasználónak, hogy a tasks lista még nem zárult le.

2. **Munkafa-ellenőrzés (csak VCS esetén):** futtasd: `git status --short`. Ha van commitálatlan változtatás:
   - Listázd ki az érintett fájlokat.
   - Jelezd: <!-- INCLUDE:lang/06-implement.md#commit-javaslat -->
   - Kérdezd meg: <!-- INCLUDE:lang/06-implement.md#commit-kerdes --> — Ha igen: commitáld a változtatásokat, majd folytasd. Ha nem: folytasd commit nélkül. (No-VCS projektben kimarad.)

3. **🔴 Párhuzamos-ciklus kapu (PW1/PW2 — csak VCS esetén):** a `06` az első fázis, amely a **forrásfát** írja, ezért az implementációs sáv **egyszálú**. A tervezés párhuzamosan mehet több ciklusban (külön worktree), az implementáció nem. Futtasd:

   ```bash
   git worktree list
   git rev-parse --git-common-dir
   git fetch origin && git log --oneline HEAD..origin/main
   ```

   _Remote nélküli (csak lokális) repóban az `origin/main` helyett a lokális `main`-nel dolgozz, `git fetch` nélkül._

   _A parancsban **szándékosan nincs `$( )` behelyettesítés**: a `HEAD..origin/main` ugyanazt a commit-halmazt adja, mint a `merge-base`-es alak, viszont több CLI (pl. Antigravity/Gemini) a parancs-behelyettesítést biztonsági okból nem engedi allowlistelni — az ilyen sor minden futásnál engedélyt kérne._

   - **Ha van másik worktree `cycle-*` branch-en** → **STOP.** Egy másik ciklus még nyitott: vagy azt kell végigvinni a `09`-ig, vagy ezt a ciklust kell megvárni. Ne kezdj implementálni, és ne javasolj `--force`-os megkerülést.
   - **Ha linked worktree-ben vagyunk** (a `git rev-parse --git-common-dir` nem `.git`) → **STOP.** A `06`–`09` a **fő** worktree-ben fut (ott lakik a `main`, amit a `09` igényel). A visszaköltözés lépéssorát lásd a *Párhuzamos ciklusok* blokk PW2/3. pontjában.
   - **Ha a `main` előrement** a ciklus ágának elágazása óta (a `git log` nem üres), **vagy** ha az `analyze-report.md` **`<field:f_validated_base>`** mezőjében szereplő fő branch SHA nem egyezik a jelenlegivel (`git rev-parse origin/main`) → **STOP.** Az `analyze-report.md` `PASS`-a a **régi** alapon készült. Futtasd újra az `05-analyze`-t (`/bs-analyze input: @specs/cycle-NN-<cycle-name>`) — az hozza be a friss fő branch-et (BR1) és validál rajta. `PASS` után térj vissza ide; magad ne rebase-elj.
   - **Egyébként** (egyetlen worktree, friss alap) → folytasd.

<!-- INCLUDE:shared/parallel-cycles.md -->

---

## Feladatod

Implementáld a `tasks.md` taskjait sorban, egyenként.

**Kövesd a projekt meglévő kód konvencióit** — naming, struktúra, tesztszervezés a forráskódból levezethetők. Ha `conventions.md` létezik a projekt gyökerében, olvasd be azt is.

**Folytatás megszakított futás után:** az implementáció bármikor félbeszakadhat — akár az első task közepén is, mielőtt bármit pipáltak volna. Mindig ellenőrizd a tényleges kód állapotát, ne csak a jelöléseket.

**Két forrásból érkezhet visszalépés ide — mindkettő a 07-validate FAIL ágáról:** (a) teszt-/Sonar-/DoD-hiba (`## <sec:validation_fixes>` taskok a `tasks.md` végén), vagy (b) kódreview-finding (`## <sec:review_fixes>` taskok + `test-report/code-review.md`). Mindkét esetben a `tasks.md` végén lévő új taskok az elvégzendők; a review-ágon olvasd be a `test-report/code-review.md`-t is (lásd a Kontextus betöltési szabályok és a Végrehajtási szabályok 2. pontját). Az alábbi döntési fa ugyanúgy érvényes — a kód tényleges állapotából indulj ki.

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
- **Review visszacsatolás:** Ha a `tasks.md` tartalmaz review-ból származó javítási feladatokat (a 07 review-kapuja `<status:must_fix>`-et talált), olvasd be a `specs/cycle-NN-<cycle-name>/test-report/code-review.md` fájlt is, hogy megértsd a javítások kontextusát és elvárásait.
- Minden tasknál **csak az adott taskban megnevezett forrásfájlokat** olvasd be — és csak a releváns részeiket. A task logikai kontextusa a Prerequisite dokumentumokban van.
- Ne olvasd be a spec-et.
- **Forrás lokalizálás**: ha a task komponenst vagy függvényt nevez meg, de a pontos fájl/sor nem ismert — hívd a `researcher` subagentet (`agents/researcher.md`, Mód B) a kereséshez. A subagent visszaadja a path-t és a releváns sorokat, nem a teljes fájlt.
- **Nagy fájl**: ha az érintett fájl nagy és csak egy szekció releváns — hívd a `researcher` subagentet (`agents/researcher.md`, Mód B) a kinyeréshez. Ne töltsd be a teljes fájlt a fő kontextusba.
- Kis, ismert fájloknál: direkt read.

---

## Tervezési elvek

**Deep module — ne shallow module:** Új függvényt vagy modult írva törekedj arra, hogy sok logikát rejtsen el egyszerű interfész mögé. A hívónak ne kelljen tudnia a belső részletekről. Ha egy új függvény egyetlen sort csinál de komplex paramétert vár, gondold újra — valószínűleg a hívó oldalra tolod a komplexitást.

**Kódkommentek:** Minden függvénynek legyen egy egysoros fejléc-kommentje, amely leírja, mit csinál. Nem triviális logikához, external API hívásokhoz és döntési pontokhoz fűzz rövid, egy-soros magyarázatot — olyan szinten, hogy más programnyelvből érkező fejlesztő is értse a szándékot. Triviális sorokhoz (pl. `return result`, egyszerű getter) nem kell komment.
- **Kommentek és docstringek naprakészen tartása:** Ha egy meglévő kódrészletet, függvényt, változót vagy végpontot módosítasz vagy átnevezel, a hozzájuk tartozó magyarázó kódkommenteket, JSDoc/TSDoc docstringeket és típus-annotációkat is **kötelezően frissíteni kell** az új elnevezéseknek és működésnek megfelelően. Elavult (stale) kommentek nem maradhatnak a kódban.

---

## Végrehajtási szabályok

> **Folytonosság — a taskok között NINCS megállás (IM1).** Ez a fázis **egy futásban** dolgozza fel a task listát: egy task lezárása (pipa + `check-log` bejegyzés + commit) **nem** a fázis vége, és **nem** a válaszod vége. A commit után **azonnal vedd a következő elvégzetlen taskot ugyanabban a körben** — ne add vissza a szót a felhasználónak, ne kérdezz rá, hogy folytathatod-e.
>
> **A megállás kimerítő listája** — csak ezek állítják meg a fázist:
> 1. teljesült egy *Megállási szabály* (lásd a szekciót);
> 2. a fejezet `> **Gépi előfeltétel:**` blokkja nem teljesül (3. pont);
> 3. a task infrastruktúra-függőnek tűnik, és rá kell kérdezni (4. pont);
> 4. a `[CHECK]` háromszor bukott (3-próba szabály, 8. pont);
> 5. **minden** task `[x]`, és jön a *Státusz kezelés* záró üzenete.
>
> Bármi más — köztük „a task elkészült és commitolva van" — **folytatás**, nem megállás. A haladásról szóló egysoros jelzés (13. pont) a válaszod **közepén** van, nem a végén.
>
> _Megjegyzés a keretrendszer konvenciójáról:_ a „**A válasz végén helyezd el a … kattintható linkjét**" mondat a többi fázisban **megállás-jelző** (kérdés vagy fázis-vég). Ezért ebben a fázisban **taskonként szándékosan nem szerepel** — a `tasks.md` linkje a fázis záró üzenetébe tartozik.

> **🔴 Konzisztens állapot a szó visszaadásakor (IM2).** Mielőtt BÁRMILYEN okból visszaadod a szót — kérdés, megállási szabály, kvóta, vagy egyszerűen a válaszod vége —, az éppen futó task legyen **lezárt** vagy **explicit módon félbehagyott** állapotban:
>
> - **lezárt** = `- [x]` a `tasks.md`-ben **+** `check-log` bejegyzés (ha volt `[CHECK]`) **+** commit (12. pont);
> - **félbehagyott** = a checkbox `- [ ]` marad, de az `imp-decision.md`-be bekerül egy sor — *melyik task, meddig jutott, mi a nyitott kérdés, mely fájlok vannak módosítva commit nélkül* —, és ezt a válaszodban is kimondod.
>
> **Commitálatlan, könyveletlen munkát hagyni tilos.** A fázis megszakadás-tűrése (és a `07` bizonyítéka) a taskonkénti commitra épül: pipa és commit nélkül a következő session csak egy piszkos munkafát talál, amiről nem tudja eldönteni, melyik task meddig jutott, és mi az, amit a felhasználó félbeszakított. **Ha meg kell állnod, előbb könyvelj, aztán beszélj.**
>
> Ez a szabály **független** attól, hogy a megállás jogos volt-e: egy jogos kérdés is csak konzisztens állapotból tehető fel.

> **🔴 Teszt-task nem zárható üres vázzal (RED1/TB1).** Ebben a fázisban a teszt-írás **nem** előkészítés a `07`-nek: a teszt itt készül el, teljes törzzsel. Tilos `assert True`, `pass`, `TODO`-komment vagy asszertáció nélküli törzs — és tilos az olyan asszertáció is, ami csak a mock saját visszatérési értékét hasonlítja önmagához. A törzsnek a **rendszer válaszához vagy állapotához** kötött állítást kell tartalmaznia.
>
> **A „majd a 07 megírja" nem ág.** A `07` validál, nem implementál: egy üres váz onnan `X passed`-ként jön vissza, és a lánc minden későbbi bizonyítéka (DoD-join, riport, `PASS` verdikt) erre a hamis zöldre épül.
>
> **A `pytest.skip` / `it.skip` / `@Disabled` sem zárja le a taskot (SK1).** A feltételes kihagyás (`if os.environ.get("RUN_REMOTE_E2E") != "true": pytest.skip(...)`) ugyanolyan üres váz, mint az `assert True` — csak nehezebb észrevenni, mert a futtató kimenetében `skipped`-ként, nem `failed`-ként jelenik meg. A `07` bizonyíték-joinjában sem számít: a `dod-check.py` a `skipped` esetet **nem** fogadja el `DoD-NN` bizonyítéknak, a `validate-gate-check.py` pedig **bukatja a kört**, ha a plan adatlapja `TC-NN`-ként hivatkozik rá. Ha a teszt csak külön környezetben futtatható, a **feltételt kell teljesíthetővé tenni** (a kapcsoló a plan gépi táblájának parancsában legyen), nem a tesztet némán kihagyni.
>
> **🔴 A teszt jelölése nem dekoráció (RL1/RL2).** Ha a plan `TS-NN` blokkja `[remote]`, a tesztnek hordoznia kell a megfelelő jelölést (`@pytest.mark.remote`, Playwright `@remote` tag), és a REST-naplózó fixture **ebből** választ mappát: `<kör-mappa>/<kategória>/rest-logs/<local|remote>/<teszt-név>/`. A teszt-név a teszt-függvény neve, útvonal-biztosra normalizálva (`[^A-Za-z0-9._-]` → `-`, a széleken lévő `-` levágva; `test_foo[dsp01]` → `test_foo-dsp01`). **A besorolás a teszt EGÉSZÉNEK tulajdonsága:** ha a teszt akár egyetlen nem a lokális gépen futó komponenst is hív, az egész teszt `remote` — a fixture ezért a teardownban mozgat, nem kérésenként. **Nem a hívott címből sorolunk be:** egy `oc port-forward` mögötti `127.0.0.1` remote, egy compose service-név pedig local. A `07` kapuja két dolgot néz: a `remote/` mappában tényleg van-e nem-lokális cím (`RL1` — egy üresen maradt vagy csak `127.0.0.1`-et tartalmazó remote mappa **bukás**, hacsak a cím nincs port-forwardként deklarálva a `Környezetek és végpontok` táblában), és hogy minden `[remote]` forgatókönyv tesztje termelt-e egyáltalán naplót (`RL2`).
>
> Ez **nem** jótanács, hanem a fázis két kapujának előfeltétele: a `[RED]` taskhoz bukás-bizonyíték kell (8/b pont, `RED1`), a fázis lezárása előtt pedig a teszt-tartalom kapu (`TB1`) végigolvassa a plan `TA1` adatlapjaiban felsorolt tesztfájlokat. Az üres váz nem „majd javítjuk" — **most** akadály.

1. Vedd a következő elvégzetlen taskot (`- [ ]`).

2. **Visszalépés kódreview-ból (07):** Ha a ciklus a 07 review-kapujának `<status:must_fix>` findingjai miatt került vissza ide, a `tasks.md` végén lévő új feladatokat a `test-report/code-review.md` kritikus észrevételei alapján végezd el. A javítások után a záró `[CHECK]` feladatok újbóli futtatása és commitolása kötelező.

3. **Fejezet-szintű előfeltétel ellenőrzés:** A `tasks.md`-ben a fejezetek `##` szintű blokkokra tagolódnak. (Ha egy task nem esik egyetlen `##` blokkba sem — pl. a lista elején áll fejezetcím nélkül —, kezeld önálló, előfeltétel nélküli taskként, és folytasd a 4. ponttal.) Ha a kiválasztott task az adott fejezet (adott `##` blokk) első elvégzetlen taskja (vagyis a fejezeten belül ez az első `- [ ]`): keresd meg a fejezet fejlécét a `tasks.md`-ben, és nézd meg, hogy közvetlenül alatta van-e `> **Gépi előfeltétel:**` blokk. Ha van: olvasd el a feltételeket, és döntsd el, hogy teljesülnek-e. Ha nem teljesülnek: állj meg, és jelezd a felhasználónak pontosan, mit kell beállítani: *„A(z) [fejezet neve] fejezet megkezdéséhez a következő feltételeknek kell teljesülniük: [feltételek]. Teljesülnek-e ezek?"* — várj a válaszra, mielőtt egyetlen taskot is elkezdenél a fejezetből.

4. **Mielőtt elkezdenéd: döntsd el, hogy a task elvégezhető-e most.** Egy task halasztott lehet, ha: teljes futó stacket igényel (konténerek, valódi Keycloak, E2E infrastruktúra), vagy a csoport összes többi taskja is elvégzetlen és mind hasonló jellegű. Ha a task halasztottnak tűnik, ne próbáld meg végrehajtani — kérdezz rá: *"[Tkkk] infrastruktúra-függő tasknak tűnik (pl. E2E, konténer, valódi Keycloak). Fut a stack, vagy keressem meg a következő elvégezhető implementációs taskot?"*
   > **Szűk kapu (IM1):** ez a kérdés **megállítja a fázist**, ezért csak akkor tedd fel, ha a task szövege **explicit** futó stacket / külső infrastruktúrát követel (konténer, deploy, valódi IdP, böngésző-E2E), **és** a rendelkezésre állását nem tudod magad ellenőrizni (pl. health check paranccsal). Kódolási, teszt-írási, konfigurációs és `[CHECK]`-parancs taskoknál **ne kérdezz — végezd el**. Ha ellenőrizni tudod (health check), **először ellenőrizd**, és csak bukás esetén kérdezz.

5. Olvasd be a task által érintett fájlokat.

6. Implementáld pontosan azt, amit a task leír — ne többet, ne kevesebbet.

7. Ne refaktorálj érintetlen kódot. Ne adj hozzá nem kért feature-t.

8. **`[CHECK]` task végrehajtása:**
   - **🔴 A parancsot SZÓ SZERINT, ÖNMAGÁBAN futtasd (CK1).** A `[CHECK]` task parancsát **pontosan úgy** add ki, ahogy a task írja — a teszt-szűrővel (`::<függvény>`, `-t "<név>"`, `-k <minta>`) együtt. **Tilos** több `[CHECK]` parancsát egy futásba vonni, a szűrőt elhagyni („futtatom az egész fájlt, az is lefedi"), vagy egy bővebb futás eredményét több taskra rávezetni. Egy `[CHECK]` = egy futás = **egy** naplósor **egy** task-azonosítóval.
     **Miért:** a szűrő az egyetlen dolog, ami a taskot a `plan.md` tesztesetéhez (`TC-NN`/`TS-NN`) köti — enélkül a pipa nem azonosítóhoz kötött állítás (`TX1`). És ami ennél sokkal fontosabb: ha a teszt neve az implementáció közben **megváltozott**, a szűrt parancs **azonnal hibát ad**, az összevont futás viszont zölden átmegy. Egy éles ciklusban nyolc `[CHECK]` task helyett egyetlen, szűrő nélküli futás került a naplóba, három szelektor pedig már nem létező függvénynévre hivatkozott — a `tasks.md` és a kód szétcsúszása így teljesen láthatatlan maradt.
     **Ha a parancs hibát ad, mert a szelektor nem talál semmit** (`no tests ran`, `ERROR: not found`), az **nem** futtatási hiba, amit összevonással kell megkerülni: vagy a tesztet nevezték át (akkor a `tasks.md` parancsát kell javítani, és a javítást jelezni), vagy a teszt nem készült el (akkor a `[RED]`/`[GREEN]` task nincs elvégezve).
   - Futtasd le a megadott parancsot.
   - Ha hibát jelez, javítsd a csoporton belüli előző taskokat, majd futtasd újra.
   - Csak zöld `[CHECK]` után jelölhető kész (`- [x]`) a csoport — a `[RED]`/`[GREEN]` taskokat is csak ekkor zárd le. **Ez a `[GREEN]` feltétele; a `[RED]`-é a 8/b pont bukás-bizonyítéka — a kettő nem helyettesíti egymást** (egy `[RED]` task nem lesz kész attól, hogy a csoportzáró `[CHECK]` végül zöld).
   - **🔴 Naplózd a `check-log.md`-be (TR5) — minden próbát, a bukottakat is.** A parancs kimenete a chatben él, a chat pedig `/clear` után nincs; enélkül a fázisból csak egy pipa marad, ami állítja a zöldet, de nem bizonyítja. Lásd a *`[CHECK]` futásnapló* szekciót.
   - **3 próba szabály:** Ha a `[CHECK]` háromszor egymás után hibával tért vissza, és a csoporton belüli javítási kísérletek sem vezettek eredményre — **állj meg**. Írd le, mit próbáltál, és jelezd a felhasználónak: *"[Tkkk] háromszor sikertelen volt. [Rövid összefoglalás a hibáról és a próbált megoldásokról.] Hogyan tovább?"*
   - **Portütközés:** Ha service indítása vagy teszt futtatása portütközéssel (address already in use) meghiúsul, ne állj meg. Keresd meg a következő szabad portot (`ss -tlnp | grep :<port>` vagy `lsof -i :<port>`), frissítsd átmenetileg az érintett konfigurációban (`docker-compose`, env fájl), és futtasd újra. Jelezd a felhasználónak melyik portot használtad helyette.
     > **⚠ ÁTMENETI MÓDOSÍTÁS — NE COMMITOLD:** a portütközés miatti config-/port-változtatás ideiglenes. A task commitja előtt ÁLLÍTSD VISSZA, vagy zárd ki a `git add`-ból (ne kerüljön a ciklus diffjébe). Csak a task tényleges kódváltozása commitolható.

8/b. **🔴 `[RED]` task lezárása: a tesztnek BUKNIA kell (RED1).** Egy `[RED]` task nem a tesztfájl létrejöttével készül el, hanem azzal, hogy a megírt teszt **vörös** — ez a TDD-ciklus első fele, és **ez az egyetlen bizonyíték arra, hogy a teszt tényleg ellenőriz valamit**. Ezért a `[RED]` task pipálása előtt:
   1. futtasd le a **célzott** tesztet (a plan `TA1` adatlapjának `<field:f_test_run>` parancsát, az egy fájlra/esetre szűkítve — ne a teljes suite-ot);
   2. a futásnak **nem-nulla** kilépő kóddal, `failed > 0` eredménnyel kell zárnia;
   3. naplózd a `check-log.md`-be **a `[RED]` task azonosítójával** és `✗` eredménnyel (a napló amúgy is minden próbát rögzít).

   **Ha a teszt ELSŐ futásra zöld, a task NEM kész** — a teszt vagy nem azt ellenőrzi, amit a plan előír, vagy üres váz (`assert True`, `pass`, asszertáció nélküli törzs). Ilyenkor a tesztet kell megírni, nem a taskot lezárni. Egy zöld `[RED]` a leggyakoribb néma teszt-csalás: a suite `X passed`-et jelent, a `DoD` bizonyítékot kap, és a validálás `PASS`-ra zár anélkül, hogy bármit ellenőriztünk volna.

   **Kivétel — `RED-EXEMPT`:** ha a `[RED]` task **meglévő** tesztet frissít (jellemzően a `TREGn` regressziós taskok), és a teszt a változás után is joggal zöld, akkor a `check-log.md` `## <sec:notes>` szekciójába írj egy sort: `RED-EXEMPT: <task> — <miért nem tud bukni>`. Indoklás nélkül a task nem zárható.

9. **`⟂ Tkkk` jelölés:** az adott task és a hivatkozott task egymástól független — ha egyszerre elvégezhetők, hívd meg mindkét szerkesztést párhuzamosan.
   - **Példa:** ha T012 tartalmazza `⟂ T013`, akkor T012 és T013 egyszerre szerkeszthetők.
   - **Kivétel:** ha mindkét task ugyanazt a fájlt érinti, futtasd őket sorban.

10. **Ideiglenes erőforrások takarítása**: Ha a task végrehajtása során ideiglenes fájlokat hoztál létre vagy konténereket indítottál el, a task (vagy `[CHECK]`) befejezése után töröld ki a fájlokat és állítsd le / töröld a konténereket. Ne hagyj magad után maradványokat a következő task számára.

11. **Jelöld késznek a `tasks.md`-ben:** állítsd a task checkboxát `- [x]`-re. **Ez a `tasks.md` módosítás is a commit része** — a kód és a workflow-állapot nem csúszhat szét.

12. **Git commit:** A task sikeres befejezése és a csoportzáró `[CHECK]` (vagy a task saját ellenőrzése, ha nincs csoport) zöldre futása után commitáld a változtatást **az érintett forrásfájlokkal, a `tasks.md`-vel ÉS a `check-log.md`-vel együtt**:
    ```bash
    git add <érintett fájlok> \
            specs/cycle-NN-<cycle-name>/tasks.md \
            specs/cycle-NN-<cycle-name>/test-report/implement/check-log.md \
      && git commit -m "cycle-NN: Tkkk - <task leírása>"
    ```
    ahol `NN` a ciklus száma (pl. `16`), `Tkkk` a task azonosítója (pl. `T001`), a leírás pedig a task szövegének tömörített változata.
    **Példa:** `cycle-16: T001 - add initHash function to token-store`
    A `[RED]` és `[GREEN]` állapotokat is külön commitold.

13. **Haladásjelzés, majd AZONNAL tovább.** Írj **egy rövid sort** arról, melyik task készült el (pl. `T004 kész — token-store initHash + unit teszt zöld (commit a1b2c3d)`), és **ugyanabban a körben** folytasd az 1. ponttól a következő elvégzetlen taskkal. Ez a sor **haladás-napló, nem záró válasz**: ne fűzz hozzá linket, összefoglalót vagy „folytathatom?" kérdést (lásd a *Folytonosság* szabályt, IM1).

---

## Megállási szabályok

Ha implementálás közben az alábbiak bármelyike teljesül, **STOP — állj meg és jelezd a felhasználónak** (ne sodródj tovább, ne próbálj „kreatívan" továbblépni):

- A task leírása ellentmond a meglévő kódnak és nem egyértelmű a helyes megoldás.
- A task elvégzéséhez olyan fájlt kellene módosítani, ami nincs benne a task leírásában — **kivéve a kényszerű következmény-módosítást (IM3), lásd lent**.
- Egy task feltételezi egy korábbi task eredményét, de az még nincs kész.
- **Egy `[CHECK]` task háromszor egymás után hibával tért vissza** (lásd 8. szabály).

Minden esetben csak **egy** kérdést tegyél fel, várj a válaszra, majd folytasd. **Megállás előtt is érvényes az IM2:** előbb a pipa + commit, vagy az `imp-decision.md` bejegyzés a félbehagyásról, és csak utána a kérdés.

> **Ez a lista kimerítő (IM1).** A fázist kizárólag az itt felsorolt négy eset állítja meg, plusz a *Végrehajtási szabályok* 3. pontja (nem teljesülő `> **Gépi előfeltétel:**` blokk) és 4. pontja (infrastruktúra-függő task). Bármi más — köztük „a task elkészült és commitolva van" — **folytatás**, nem megállás.

### Kényszerű következmény-módosítás (IM3) — kivétel a „nem listázott fájl" szabály alól

Egy törlés, átnevezés vagy szignatúra-változás óhatatlanul átgyűrűzik olyan fájlokra, amelyeket a task nem sorol fel (a törölt configra mutató alapérték, az átnevezett szimbólum importja). Ha minden ilyen esetben megállnál, a fázis szinte minden ciklusban elakadna — ha viszont szabadon átírsz bármit, az a „kreatív sodródás", amit ez a szekció tilt. A határ:

**Elvégezheted megállás nélkül, ha MINDHÁROM teljesül:**
1. a módosítás a listázott változtatás **mechanikus következménye** — egy hivatkozás átvezetése —, nem új viselkedés;
2. **pontosan egy helyes alakja van** (nem kell két megoldás között választani, nincs érdemi tervezési szabadság);
3. a bukó `[CHECK]`, fordítás vagy teszt **maga mutat rá** a fájlra és a sorra — nem te keresed meg, hogy „mi minden érintett még".

**Ilyenkor:** végezd el a **lehető legszűkebb** javítást, vedd fel az `imp-decision.md`-be (*melyik task kényszerítette ki · melyik fájl:sor · miért csak egy helyes alak van*), és említsd a haladás-sorban is. **Ne állj meg.**

**Ha bármelyik feltétel nem teljesül** — választani kell két út között, a következmény új viselkedést vezetne be, vagy a hatókör túlnő egy hivatkozás-átvezetésen — **állj meg és kérdezz**. A „kreatívan továbblépek" ilyenkor szabályszegés.

> **A visszacsatolás kötelező.** Az így érintett, egyetlen taskban sem szereplő fájlokat sorold fel a **fázis záró üzenetében** is: ez azt jelenti, hogy a `04` (és a `05` lefedettségi köre) kihagyott egy kötelező következmény-módosítást — a `07` és a `09` különben egy sehol nem tervezett diffet lát a ciklusban.

---

## `[CHECK]` futásnapló (TR5) — `test-report/implement/check-log.md`

> **Miért kell:** a `[CHECK]` parancsok kimenete a chatben él, a chat pedig `/clear` után nincs. Enélkül az implementációs fázisból csak egy `- [x]` pipa és egy commit-üzenet marad — mindkettő *állítja*, hogy zöld volt, de nem bizonyítja. A 07-validate ugyanezért követeli meg a bizonyítékot (TR1/TR2) és a riport-artefaktumokat (TR3); a 06-ban ennek olcsó, szöveges párja ez a napló.

**Hol:** `specs/cycle-NN-<cycle-name>/test-report/implement/check-log.md`. Ha a mappa nem létezik, hozd létre. A `test-report/validate/` és `test-report/review/` almappákhoz **nem nyúlsz** — azok a 07 és a 09 bizonyítékai.

**Mikor írsz bele:** **minden `[CHECK]` futás után, a bukottak után is** — nem csak a végül zöld próba után. A napló **append-only**: korábbi sort nem írsz át és nem törölsz.

**Mit NEM csinálsz taskonként:** nem generálsz HTML/Allure/coverage riportot minden task után — a `[CHECK]`-napló az olcsó, szöveges bizonyíték. A teljes riport-készlet a fázis végén, **egyszer** készül el, és csak akkor, ha a projekt az `implement`-et riport-fázisnak deklarálta (TR6) — lásd a *Riport-fázis* szekciót.

### A fájl sablonja

```md
<!-- INCLUDE:lang/06-implement.md#check-log-sablon -->
```

**Oszlopok:**
- **Idő** — konkrét string (`YYYY-MM-DD HH:MM`). Shell-behelyettesítés platformfüggő: bash/zsh → `$(date '+%Y-%m-%d %H:%M')`, PowerShell → `(Get-Date -Format 'yyyy-MM-dd HH:mm')`. Ha nem tudod megállapítani, `—` is elfogadható; a többi oszlop a lényeg.
- **Task** — **pontosan egy** task-azonosító (`T001`, `T030a`, `TREG1`, `TLAST1`). Intervallum (`T030a-T037`), felsorolás (`T031, T032`) és „több task egy sorban" **tilos** (CK1): a napló így nem bizonyíték, hanem összefoglaló, és a `07` kapuja nem tudja taskonként eldönteni, mi futott le.
- **Próba** — hányadik kísérlet a 3-próba szabályból (8. pont): `1/3`, `2/3`, `3/3`. Ez teszi utólag láthatóvá, hogy egy csoport nehezen ment át.
- **<field:f_mode>** — `normál` \| `validate-loop` (a 07 önjavító hurka — teszt- és review-javítás egyaránt). A fix-módban futtatott `[CHECK]`-eket **ugyanígy naplózod**, a megfelelő markerrel — így a javító körök is nyomot hagynak.
- **Parancs** — a ténylegesen kiadott parancs **szó szerint**, nem a task szövegében szereplő idealizált változat.
- **Eredmény** — `✓`/`✗` + a futtató darabszámai (`X passed / Y failed / Z skipped`), bukásnál a bukott teszt(ek) neve rövid hibaüzenettel. **A `[RED]` taskoknál a `✗` nem hiba, hanem a kötelező bizonyíték (RED1)** — a 8/b pont szerint a `[RED]` task pont ettől a sortól lesz lezárható. **Ha a parancs nem teszt** (build, lint, typecheck), a darabszám helyett a lényegi kimenet egy sora (pl. `0 errors`).

**<sec:notes> szekció** — ide kerül minden olyan körülmény, ami a futást befolyásolta, de nem fér a táblába: átmeneti port-csere (és hogy visszaállt-e — 8. pont portütközés-szabálya), kézzel indított/leállított konténer, kihagyott ellenőrzés és annak indoka. **Itt élnek a felmentő sorok is:** `RED-EXEMPT: <task> — <indok>` (a `[RED]` nem tud bukni, 8/b pont) és `CK-DEVIATION: <task> — <indok>` (a keret nem tud eset-szintűre szűrni, 8. pont). Mindkét prefix **nyelvfüggetlen literál** — a `07` kapuja szó szerint ezekre illeszt.

---

## Problémamegoldás dokumentálása

Ha egy task elvégzése során legalább 3 sikertelen kísérlet után sikerül megoldani a problémát, hozd létre vagy bővítsd a `specs/cycle-NN-<cycle-name>/imp-decision.md` fájlt:

```md
<!-- INCLUDE:lang/06-implement.md#check-log-pelda-sor -->
```

Ha a fájl már létezik, append-elj — ne írd felül a korábbi bejegyzéseket.

---

## Új komponens README

_(Emlékeztető a 03-plan `README.md` követelményéről — itt a végrehajtás történik, nem új követelmény.)_ Ha egy task új komponenst hoz létre (új alkalmazás, új service, új önálló modul), a komponens gyökér mappájában kötelező létrehozni egy `README.md` fájlt. Tartalma:

- **Mit csinál** — egy-két mondat a komponens felelősségéről
- **<field:f_startup>** — konkrét parancs(ok) a helyi futtatáshoz
- **Port** — milyen porton hallgatózik
- **Debug** — ha értelmes: hogyan kell debuggolni, milyen debug portot használ
- **Logok** — milyen eseményeket naplóz, milyen log szintek vannak
- **Kapcsolatok** — milyen más komponensektől függ, miket hív, mi hívja őt

A README.md az implementáció része — nem utólagos dokumentáció. Akkor kell elkészülnie, amikor a komponens kész.

---


## Implement-fázisú tesztek (PH1) — a fázis végén, egyszer

A `plan.md` gépi futtatási táblájának `<field:f_phase>` oszlopa megmondja, mely kategóriákat kell **ebben** a fázisban futtatni (`<status:phase_implement>` vagy `<status:phase_both>`; **a jelöletlen sor is ide tartozik** — a hallgatás nem jelent kihagyást). Ez nem a taskonkénti `[CHECK]` helyett van: a `[CHECK]` a csoport zöldjét igazolja, ez pedig a **fázis záró állapotát**, gépi darabszámokkal és bizonyítékkal. Miután minden task `[x]`, de a státuszváltás ELŐTT, **egyszer**:

```bash
python3 <platform-scripts-mappa>/run-tests.py \
  specs/cycle-NN-<cycle-name>/plan.md \
  --round-dir specs/cycle-NN-<cycle-name>/test-report/implement \
  --phase <status:phase_implement>
```

- **`exit 0`** → a kimenet kategóriánként hozza a kiadott parancsot és a `X passed / Y failed / Z skipped` darabszámokat; a bizonyíték a fázis-mappába kerül, és a záró committal megy be.
- **`exit 1`** → van bukott kategória: ez **ugyanaz a 3-próba szabály**, mint a `[CHECK]`-nél — javítsd a bukást, futtasd újra, és a naplózás a `check-log.md`-be megy. Háromszori bukás után állj meg és kérdezz.
- **`exit 2`** → a plan-ben nincs gépi tábla (régi ciklus): ez nem a te hibád és nem megállás — jelezd egy sorban a fázis záró üzenetében, hogy a `03` táblája hiányzik.
- **`MEGJEGYZÉS (PH1)` sor „nincs mit futtatni"** → a tábla minden sora `<status:phase_validate>`-only. Menj tovább.

> **Ez nem új megállási pont (IM1).** A futtatás a fázis lezárásának része, ugyanabban a körben — a `[CHECK]`-ekkel ellentétben taskonként **nem** fut.

## Teszt-tartalom kapu (TB1) — a fázis lezárása előtt

Minden task `[x]`, de a státuszváltás **előtt** futtasd le a teszt-tartalom kaput. A plan `TA1` adatlapjaiban felsorolt tesztfájlokat vizsgálja: van-e köztük **üres váz** (`assert True`, `pass`, asszertáció nélküli törzs).

```bash
python3 <platform-scripts-mappa>/test-substance-check.py specs/cycle-NN-<cycle-name>
```

- **`exit 0`** → mehet a *Riport-fázis* és a státuszváltás;
- **`exit 1`** → **a fázis nem zárható.** A felsorolt teszt-függvényeket **meg kell írni**: ez nem „a teszt majd a 07-ben megíródik" — a `[RED]` task **terméke** a teszt, és üres váz esetén a task nincs elvégezve (RED1). A javítás után futtasd újra a task `[CHECK]`-jét (szó szerint, szűrővel — CK1), naplózz, és csak utána zárj.

> **Miért gépi kapu ez, és nem checklist-sor:** egy üres váz azonnal zöld, tehát a `[CHECK]` számlálója, a `DoD` bizonyítéka és a validálás `PASS`-a **mind teljesíthető** anélkül, hogy bármit ellenőriztünk volna. Az implementálónak érdeke a pipa (`7/j`) — ezért nem az ő ítéletére van bízva.

## Riport-fázis (TR6) — `test-report/implement/`

Az `implement/` **hivatalos fázis-mappa**: nemcsak a `check-log.md` helye, hanem a 06 záró állapotának teljes riport-készletéé is — ha a projekt így rendelkezik. A döntés a `conventions.md` `## <sec:cv_test_reporting>` szekciójának `**<field:f_report_phases>:**` mezőjében él (`implement`, `validate`, vagy mindkettő; a mező hiányában az alapérték `validate`). **Ne találgasd** — kérdezd le determinisztikusan, miután minden task `[x]`, de a státuszváltás ELŐTT:

```bash
python3 <platform-scripts-mappa>/report-gate-check.py \
  conventions.md specs/cycle-NN-<cycle-name> --phases
```

- **A kimenetben nincs `implement`** → nincs dolgod: a riport-készletet a 07 állítja elő a saját köreiben. Menj tovább a státuszváltásra.
- **A kimenetben ott van az `implement`** → futtasd le a `conventions.md` `## <sec:cv_test_reporting>` táblájának riport-generáló parancsait a fázis-mappára, majd zárd a kapuval:

```bash
python3 <platform-scripts-mappa>/report-gate-check.py \
  conventions.md specs/cycle-NN-<cycle-name> \
  --report-subdir test-report/implement
```

**A fázis-mappa alakja `implement`** — ezt kapja a riport-parancsok `<phase-dir>` helyőrzője vagy `REPORT_PHASE_DIR`-szerű környezeti változója. Soha ne a teljes `specs/cycle-NN-<cycle-name>/test-report/implement` útvonalat írd oda: a bázisok összekeverése rekurzív `test-report/test-report/…` fát épít, amit a kapu layout-őre `exit 1`-gyel bukat (TR5/c).

- **`exit 0`** → kész, mehet a státuszváltás; a riport-artefaktumok a záró committal mennek be.
- **`exit 1`** → hiányzó vagy üres artefaktum, vagy idegen mappa a `test-report/` alatt. **Ez nem kód-bug: nem indítasz fixert és nem lépsz vissza taskra** — futtasd újra a hiányzó riport-generáló parancsot, illetve töröld az idegen mappát, és futtasd újra a kaput. Ha a parancs maga hibás (nem áll elő tőle az artefaktum), az a `conventions.md` hiánya: állj meg, és kérdezz a felhasználótól.

> **Ez nem új megállási pont (IM1).** A riport-generálás a fázis lezárásának része, ugyanabban a körben — a `--phases` lekérdezés és a kapu között ne add vissza a szót a felhasználónak.

## Státusz kezelés

- Implementálás közben: `<status:implement_in_progress>`
- Ha minden task `[x]`: frissítsd a `tasks.md` státuszát `<status:ready_for_validate>`-re, és **commitold ezt az állapotváltozást** (a végső státusz külön legyen rögzítve) — a `check-log.md` utolsó bejegyzéseivel együtt:
  ```bash
  git add specs/cycle-NN-<cycle-name>/tasks.md \
          specs/cycle-NN-<cycle-name>/test-report/implement/ \
    && git commit -m "cycle-NN: 06-implement - kész, validálásra kész"
  ```
  **Ellenőrzés a státuszváltás előtt:** lefutott a *Teszt-tartalom kapu (TB1)* szekció (`exit 0`) és a *Riport-fázis (TR6)* szekció (a `--phases` lekérdezés, és ha az `implement` riport-fázis, a kapu `exit 0`-val); a `check-log.md` létezik, és minden csoportzáró `[CHECK]`-hez tartozik benne legalább egy sor. Ha egy csoport `[x]`, de a naplóban nincs hozzá bejegyzés, a bizonyíték hiányzik — pótold a naplósort a tényleges futtatás alapján (ne emlékezetből: ha nem tudod, futtasd újra a `[CHECK]`-et).

Ha a státusz `<status:ready_for_validate>`, állj meg. Jelezd a felhasználónak a következő lépést és a fázis indító parancsát, például:
<!-- INCLUDE:lang/06-implement.md#zaro-uzenet -->
> **A válasz végén helyezd el a `tasks.md` és a `check-log.md` közvetlen, kattintható linkjét** — a fázis egyetlen megállás-jelzője ez (IM1).


> **Fázishatár — kemény megállás (PE1).** A fázis a záró üzenettel (commit-azonosító + `/clear` + a következő fázis parancsa) **véget ér**. Ugyanabban a körben a következő fázisból **semmit nem kezdesz el** — a következő fázis artefaktumát létre sem hozod. Ez akkor is érvényes, ha egy **kontextus-összefoglaló / checkpoint** teendő-listája, a saját korábbi terved vagy a felhasználó egy korábbi körben adott „menjünk végig a folyamaton" mondata továbbmenetelre biztat: a skill fázishatára minden ilyen felett áll. Csak a felhasználó **erre a körre szóló, explicit** kérése írja felül. Ha mégis belekezdtél, **töröld a keletkezett fájlt**, állítsd vissza a tiszta munkafát, és jelezd.

---

<!-- INCLUDE:shared/fix-mode-implement.md -->
