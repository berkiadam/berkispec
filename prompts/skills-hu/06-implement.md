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

1. Vedd a következő elvégzetlen taskot (`- [ ]`).

2. **Visszalépés kódreview-ból (07):** Ha a ciklus a 07 review-kapujának `<status:must_fix>` findingjai miatt került vissza ide, a `tasks.md` végén lévő új feladatokat a `test-report/code-review.md` kritikus észrevételei alapján végezd el. A javítások után a záró `[CHECK]` feladatok újbóli futtatása és commitolása kötelező.

3. **Fejezet-szintű előfeltétel ellenőrzés:** A `tasks.md`-ben a fejezetek `##` szintű blokkokra tagolódnak. (Ha egy task nem esik egyetlen `##` blokkba sem — pl. a lista elején áll fejezetcím nélkül —, kezeld önálló, előfeltétel nélküli taskként, és folytasd a 4. ponttal.) Ha a kiválasztott task az adott fejezet (adott `##` blokk) első elvégzetlen taskja (vagyis a fejezeten belül ez az első `- [ ]`): keresd meg a fejezet fejlécét a `tasks.md`-ben, és nézd meg, hogy közvetlenül alatta van-e `> **Gépi előfeltétel:**` blokk. Ha van: olvasd el a feltételeket, és döntsd el, hogy teljesülnek-e. Ha nem teljesülnek: állj meg, és jelezd a felhasználónak pontosan, mit kell beállítani: *„A(z) [fejezet neve] fejezet megkezdéséhez a következő feltételeknek kell teljesülniük: [feltételek]. Teljesülnek-e ezek?"* — várj a válaszra, mielőtt egyetlen taskot is elkezdenél a fejezetből.

4. **Mielőtt elkezdenéd: döntsd el, hogy a task elvégezhető-e most.** Egy task halasztott lehet, ha: teljes futó stacket igényel (konténerek, valódi Keycloak, E2E infrastruktúra), vagy a csoport összes többi taskja is elvégzetlen és mind hasonló jellegű. Ha a task halasztottnak tűnik, ne próbáld meg végrehajtani — kérdezz rá: *"[Tkkk] infrastruktúra-függő tasknak tűnik (pl. E2E, konténer, valódi Keycloak). Fut a stack, vagy keressem meg a következő elvégezhető implementációs taskot?"*
   > **Szűk kapu (IM1):** ez a kérdés **megállítja a fázist**, ezért csak akkor tedd fel, ha a task szövege **explicit** futó stacket / külső infrastruktúrát követel (konténer, deploy, valódi IdP, böngésző-E2E), **és** a rendelkezésre állását nem tudod magad ellenőrizni (pl. health check paranccsal). Kódolási, teszt-írási, konfigurációs és `[CHECK]`-parancs taskoknál **ne kérdezz — végezd el**. Ha ellenőrizni tudod (health check), **először ellenőrizd**, és csak bukás esetén kérdezz.

5. Olvasd be a task által érintett fájlokat.

6. Implementáld pontosan azt, amit a task leír — ne többet, ne kevesebbet.

7. Ne refaktorálj érintetlen kódot. Ne adj hozzá nem kért feature-t.

8. **`[CHECK]` task végrehajtása:**
   - Futtasd le a megadott parancsot.
   - Ha hibát jelez, javítsd a csoporton belüli előző taskokat, majd futtasd újra.
   - Csak zöld `[CHECK]` után jelölhető kész (`- [x]`) a csoport — a `[RED]`/`[GREEN]` taskokat is csak ekkor zárd le.
   - **🔴 Naplózd a `check-log.md`-be (TR5) — minden próbát, a bukottakat is.** A parancs kimenete a chatben él, a chat pedig `/clear` után nincs; enélkül a fázisból csak egy pipa marad, ami állítja a zöldet, de nem bizonyítja. Lásd a *`[CHECK]` futásnapló* szekciót.
   - **3 próba szabály:** Ha a `[CHECK]` háromszor egymás után hibával tért vissza, és a csoporton belüli javítási kísérletek sem vezettek eredményre — **állj meg**. Írd le, mit próbáltál, és jelezd a felhasználónak: *"[Tkkk] háromszor sikertelen volt. [Rövid összefoglalás a hibáról és a próbált megoldásokról.] Hogyan tovább?"*
   - **Portütközés:** Ha service indítása vagy teszt futtatása portütközéssel (address already in use) meghiúsul, ne állj meg. Keresd meg a következő szabad portot (`ss -tlnp | grep :<port>` vagy `lsof -i :<port>`), frissítsd átmenetileg az érintett konfigurációban (`docker-compose`, env fájl), és futtasd újra. Jelezd a felhasználónak melyik portot használtad helyette.
     > **⚠ ÁTMENETI MÓDOSÍTÁS — NE COMMITOLD:** a portütközés miatti config-/port-változtatás ideiglenes. A task commitja előtt ÁLLÍTSD VISSZA, vagy zárd ki a `git add`-ból (ne kerüljön a ciklus diffjébe). Csak a task tényleges kódváltozása commitolható.

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
- **Próba** — hányadik kísérlet a 3-próba szabályból (8. pont): `1/3`, `2/3`, `3/3`. Ez teszi utólag láthatóvá, hogy egy csoport nehezen ment át.
- **<field:f_mode>** — `normál` \| `validate-loop` (a 07 önjavító hurka — teszt- és review-javítás egyaránt). A fix-módban futtatott `[CHECK]`-eket **ugyanígy naplózod**, a megfelelő markerrel — így a javító körök is nyomot hagynak.
- **Parancs** — a ténylegesen kiadott parancs **szó szerint**, nem a task szövegében szereplő idealizált változat.
- **Eredmény** — `✓`/`✗` + a futtató darabszámai (`X passed / Y failed / Z skipped`), bukásnál a bukott teszt(ek) neve rövid hibaüzenettel. **Ha a parancs nem teszt** (build, lint, typecheck), a darabszám helyett a lényegi kimenet egy sora (pl. `0 errors`).

**<sec:notes> szekció** — ide kerül minden olyan körülmény, ami a futást befolyásolta, de nem fér a táblába: átmeneti port-csere (és hogy visszaállt-e — 8. pont portütközés-szabálya), kézzel indított/leállított konténer, kihagyott ellenőrzés és annak indoka.

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
  **Ellenőrzés a státuszváltás előtt:** lefutott a *Riport-fázis (TR6)* szekció (a `--phases` lekérdezés, és ha az `implement` riport-fázis, a kapu `exit 0`-val); a `check-log.md` létezik, és minden csoportzáró `[CHECK]`-hez tartozik benne legalább egy sor. Ha egy csoport `[x]`, de a naplóban nincs hozzá bejegyzés, a bizonyíték hiányzik — pótold a naplósort a tényleges futtatás alapján (ne emlékezetből: ha nem tudod, futtasd újra a `[CHECK]`-et).

Ha a státusz `<status:ready_for_validate>`, állj meg. Jelezd a felhasználónak a következő lépést és a fázis indító parancsát, például:
<!-- INCLUDE:lang/06-implement.md#zaro-uzenet -->
> **A válasz végén helyezd el a `tasks.md` és a `check-log.md` közvetlen, kattintható linkjét** — a fázis egyetlen megállás-jelzője ez (IM1).


> **Fázishatár — kemény megállás (PE1).** A fázis a záró üzenettel (commit-azonosító + `/clear` + a következő fázis parancsa) **véget ér**. Ugyanabban a körben a következő fázisból **semmit nem kezdesz el** — a következő fázis artefaktumát létre sem hozod. Ez akkor is érvényes, ha egy **kontextus-összefoglaló / checkpoint** teendő-listája, a saját korábbi terved vagy a felhasználó egy korábbi körben adott „menjünk végig a folyamaton" mondata továbbmenetelre biztat: a skill fázishatára minden ilyen felett áll. Csak a felhasználó **erre a körre szóló, explicit** kérése írja felül. Ha mégis belekezdtél, **töröld a keletkezett fájlt**, állítsd vissza a tiszta munkafát, és jelezd.

---

<!-- INCLUDE:shared/fix-mode-implement.md -->
