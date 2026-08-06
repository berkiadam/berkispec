---
phase: 07
name: bs-validate
description: "berkispec - 07. Használd az implementáció után (Phase 07), ha a tasks.md 'Validálásra kész'. Teszt-, lint- és build-ellenőrzés, hiba esetén önjavító kör (implement-fixer subagent). Létrehozza a 'validate-decision.md'-t; PASS esetén a spec.md/plan.md/tasks.md státuszát 'Kész'-re állítja."
prerequisites:
  - "specs/cycle-NN-<name>/tasks.md státusz: Validálásra kész"
output:
  - "specs/cycle-NN-<name>/test-report/validate-decision.md — teljes validálási riport (körönkénti lépés-napló + # Validation History)"
  - "specs/cycle-NN-<name>/test-report/ — a conventions.md `## Teszt-riportolás` táblája szerint kötelező riport-artefaktumok (TR3 kapu)"
  - "PASS esetén: spec.md / plan.md / tasks.md státusz: Kész"
prev: bs-implement
next: bs-doc-sync
subagents:
  - "agents/test-runner.md"
  - "agents/implement-fixer.md"
shared:
  - "shared/input-from-prev.md"
  - "shared/phase-commit.md"
---
# 07 — Validálás
## Kontextus ellenőrzés

Ha azt detektálod, hogy ennek a fázisnak a futtatása most indul (ez az első prompt a fázisban), de a kontextus nem „friss” (azaz a beszélgetési előzmények tartalmaznak korábbi fázisokból vagy futásokból származó üzeneteket), akkor kérdezz rá a felhasználónál:
> *„Úgy tűnik, hogy a fázis indításakor a kontextus nem teljesen friss. Szándékosan nem futtattál `/clear`-t az új fázis megkezdése előtt (a tokenekkel való spórolás érdekében)?”*
Várd meg a felhasználó válaszát, mielőtt folytatnád a fázis futtatását.

---

Spec driven development-ben fejlesztünk szoftvert. A fejlesztés ciklusokra van bontva. Minden ciklus egy önállóan lefejleszthető, önállóan tesztelhető részegysége a teljes implementációnak.

Ez a folyamat **7. fázisa (0–9)**: 0-init · 1-ciklusok · 2-spec · 3-plan · 4-tasks · 5-analyze · 6-implement · **7-validate ←** · 8-doc-sync · 9-review.

---

## Bemenet

A prompt bemenete a ciklus mappája (pl. `specs/cycle-NN-<cycle-name>`). A validációhoz szükséges fájlokat (`spec.md`, `plan.md`, `tasks.md`) ebben a mappában találod.

## Előfeltétel

0. **Ciklus-beazonosítás:** ha a felhasználó megadott ciklust/fájlt, azt használd; különben a legfrissebb `specs/cycle-*` mappát ajánld fel megerősítésre — *"A(z) `specs/cycle-NN-<name>` ciklussal szeretnél dolgozni? Igen / Nem (megadom a ciklust)"* — és várj a válaszra, mielőtt továbblépsz.

1. **`conventions.md` létezés-ellenőrzés:** olvasd be a projekt gyökerében a `conventions.md`-t. Ha nem létezik, STOP — térjenek vissza a `00` fázishoz.

2. **Munkafa-ellenőrzés (csak VCS esetén):** futtasd `git status --short`. (No-VCS projektben kimarad.)
   - **Előbb nézd meg a `tasks.md` státuszát.** Ha `[validate-loop]` markert visel, egy korábbi hurok szakadt meg: a ciklus mappájában lévő commitálatlan változások (`spec.md` DoD-pipák, `tasks.md` javító-taskok, `test-report/`) **a hurok saját, még nem commitolt állapota** (VD8 — a hurok alatt nincs köztes commit). Ilyenkor **ne ajánld fel commitra** és ne kérdezz — jelezd egy sorban, hogy megszakadt hurkot folytatsz, és menj a „Megszakított futás kezelése" 4. pontjára.
   - Egyébként, ha van commitálatlan változtatás, listázd, és kérdezd meg egy körben, hogy commitáljam-e most vagy folytassam — várj a válaszra.

3. Olvasd be a megadott mappából a `tasks.md`, `plan.md` és `spec.md` fájlok státuszát.

- **Ha a `tasks.md` státusza nem `Validálásra kész`:** az implementáció még nem zárult le. Jelezd, és térj vissza a `06` fázishoz.
- **Ellenőrzőpont:** a `plan.md` és `spec.md` státusza elfogadható értékek:
  - `plan.md`: `Task írásra kész` vagy `Kész`
  - `spec.md`: `Tervezésre kész` vagy `Kész`
  - `Kész` mindkettőnél normális, ha a 09-es review (vagy a 09 merge előtti doc-sync újrafuttatása) után tértünk vissza ide.
  - Ha valamelyik `Piszkozat`-ra van visszaállítva, jelezd a felhasználónak — valamelyik korábbi fázisban döntés született, amely szinkront igényel.

---

## Ismételt hibák korai ellenőrzése

**Mielőtt bármit futtatnál:** ha létezik `specs/cycle-NN-<cycle-name>/test-report/validate-decision.md`, kérdezd le a napló állapotát a szkript **read-only** módjával — **ne olvasd/parse-old kézzel** (a régi, elavult bejegyzésekből téves riasztás születik):

```bash
python3 <platform-scripts-mappa>/failure-counter.py \
  specs/cycle-NN-<cycle-name>/test-report/validate-decision.md --status
```

A `--status` az **utolsó** futás bejegyzését és a hozzá tartozó számlálókat írja ki (egymást követő bukás / összes bukás / egymást követő FAIL-futások) — mindig az aktuális állapotot, nem a napló egy régi pontját. Ha az utolsó futás FAIL, és bármelyik számláló **eggyel a küszöbe alatt** van (2/3, 4/5, 4/5), ez **figyelmeztető jelzés, nem megállási pont**: írd a válaszodba egy sorban, hogy *„Figyelem: a(z) [Failed Item] már [N] alkalommal elbukott — ha most is hibázik, a leállási korlát életbe lép és humán beavatkozást kérek."*, majd **folytasd** a validálást (ez NEM kérdés, NE várj választ). A tényleges megállásról mindig a naplózó futtatás **kilépő kódja** dönt (lásd „Naplózás és leállási korlátok"), nem ez az előzetes ránézés.

---

## Feladatod

Ellenőrizd, hogy a ciklus implementációja teljes és helyes. A validálás három forrás alapján történik:

1. **`spec.md` — Definition of done**: minden pont teljesül-e?
2. **`plan.md` — Tesztelési stratégia**: minden előírt teszt lefut-e és átmegy-e?
3. **`tasks.md`**: minden task `[x]` státuszban van-e?

**Szereped PASS-ig determinisztikus ellenőrző, FAIL esetén orchestrátor.** Ha a validálás FAIL-t talál, **nem** adod vissza egyszerűen a vezérlést a felhasználónak („futtasd újra a 06-ot"), hanem **levezényelsz egy önjavító hurkot** (`implement-fixer` subagent → szerződés-integritás kapu → újra-validálás), amíg PASS nem lesz — a **három leállási korlát** (per-item 3 egymást követő / 5 összes bukás, valamint 5 egymást követő FAIL-futás) határáig, tervezési hiba esetén **felfelé eszkalálva**. A javítást nem te végzed: azt az `agents/implement-fixer.md` subagent (= a 06 Fix-módja) csinálja. Lásd „Az önjavító hurok (orchestrátor-hurok)".

---

## Megszakított futás kezelése

A validáció bármikor megszakadhat. Újraindítás (ismételt futtatás) esetén:
1. **Idempotens futás**: Kezdd elölről a validálási lépéseket. Ha a korábbi futás naplózott már valamit a `test-report/validate-decision.md`-be, az az előző (félbeszakadt) futásnak tekintendő: **olvasd el az utolsó `## Kör N` blokkot** — ebből látod, meddig jutott (mely lépések futottak le, mi bukott, indult-e fixer). A megszakadt kört **ne írd felül**: zárd le a blokkját egy `**Megszakadt** — a futás itt szakadt meg` sorral, és az új kör új `## Kör N+1` blokkot kap.
2. **Beragadt erőforrások**: Ha a korábbi megszakított futásból beragadt teszt konténerek vagy folyamatok miatt portütközést tapasztalsz, lődd ki azokat, vagy keress új szabad portot a korábban leírt módon.
3. **Duplikált taskok elkerülése**: Ha a futás FAIL-lel zárul, és javító feladatokat kell felvenned a `tasks.md` `## Validációs javítások` szekciójába, mindig ellenőrizd, hogy a konkrét teszthiba vagy Sonar javítás nem szerepel-e már elvégzetlen taskként (egy korábbi félbeszakadt validáció okán). Ha már ott van, ne vedd fel duplán.

4. **Megszakadt önjavító hurok felismerése (`[validate-loop]` marker + Validation History):** ha a `tasks.md` státusza `Implementálásra kész [validate-loop]` markert visel, egy korábbi validate-hurok szakadt meg — **ne** kezdj tiszta lapról. Derítsd ki a hurok állapotát:
   - Kérdezd le a napló állapotát: `failure-counter.py <validate-decision.md> --status` — ez adja meg az utolsó futást, a megrekedt itemeket és a számlálókat (hányadik próbánál tartott). Kézzel ne parse-old.
   - Olvasd be a `tasks.md` `## Validációs javítások` szekcióját: vannak-e még elvégzetlen `[ ]` javító-taskok?
     - **Ha igen** (a fixer nem futott le vagy félbeszakadt): folytasd a hurkot a fixer újraindításával ezekre a taskokra, majd újra-validálj.
     - **Ha nincs** (a fixer befejezte, de az újra-validálás maradt el): futtasd újra a validálási lépéseket, és értékeld az eredményt a hurok szerint.
   - A számlálók a leállási korlátok alapja — a folytatáskor a szkript automatikusan onnan számol tovább (a napló a memória). **Ne nullázd, ne írd át kézzel a `# Validation History`-t.**

---

## Kontextus betöltési szabályok

- Olvasd be a `spec.md` Definition of done szekciót.
- Olvasd be a `plan.md` Tesztelési stratégia és Ellenőrzési stratégia szekciókat.
- Olvasd be a `tasks.md`-t.
- **Olvasd be a `validate-input-from-prev.md`-t, ha létezik** — lásd a „Fázisok közötti átadás" szekciót.
- Ne olvasd be az egész forráskódot — csak azt, ami egy konkrét ellenőrzéshez szükséges.

---

## Fázisok közötti átadás (`*-input-from-prev.md`) — IP1

**Amit BEOLVASSZ:** ha létezik a `specs/cycle-NN-<cycle-name>/validate-input-from-prev.md`, olvasd be a validálás **megkezdése előtt**. A 03/04 fázisban derült ki futtatási előfeltételeket és üzemeltetési tudnivalókat tartalmazza (pl. „a stack indítása előtt VPN kell", „ez a teszt csak a seed lépés után futtatható", „a port ütközik a fejlesztői stackkel"). Ezek jellemzően **megelőzik** a teszthibát, ha figyelembe veszed őket — ezért a `test-runner` indítása **előtt** dolgozd fel, és a releváns tételeket **add át a subagent bemenetében**.

Minden `[ ]` tételt zárj le: vagy figyelembe vetted a validálás során (`→ figyelembe vettem: <hogyan>`), vagy explicit indokkal elvetett (`→ elvetve: <miért>`). **Guard:** ha a fájl nem létezik, ez nem hiba — folytasd.

**Amibe ÍRHATSZ:** semmibe — a 07 a lánc **vége**. Ha a validálás során olyan tartós tudnivaló derül ki, ami a **következő ciklusokban** is kell, az nem ide tartozik: a `specs/test-conventions.md`-be való, aminek a `08-doc-sync` a gazdája (TC3 — a promóciót ott javasold, ne írd magad).

<!-- INCLUDE:shared/input-from-prev.md -->

---

## Validálási lépések

### 0. Riport mappa előkészítése

Mielőtt bármit futtatnál, győződj meg róla, hogy létezik a `specs/cycle-NN-<cycle-name>/test-report/` mappa. Ha nem létezik, hozd létre — ide kerül a `validate-decision.md`, a `sonar-report.md` és minden teszt-artefakt.

**A riport-artefaktumok a ciklus részei — NEM kell őket kizárni a diffből.** A `git add specs/cycle-NN-<cycle-name>/` szándékosan beveszi a `test-report/` teljes tartalmát: a teszt-eszköz saját riportja (Allure/Playwright HTML, coverage, JUnit XML) az egyetlen utólag megnyitható bizonyíték a futásról. A méret ellen az egyfájlos HTML a védekezés (`--single-file`), nem a `.gitignore`. Ha korábbi ciklusból maradt `test-report/.gitignore`, amely a riportokat kizárja, **töröld** — különben a TR3 kapu olyan fájlt keres, ami sosem kerül be a repóba.

**A riportok a `conventions.md` `## Teszt-riportolás` táblája szerint kötelezők (TR3)** — a listát a `test-runner` állítja elő, és a PASS előtt determinisztikus kapu ellenőrzi (lásd „Kötelező teszt-riportok kapuja").

### 1. Gyors tesztek és kódminőség ellenőrzése (`test-runner` subagent)

Hívd a `test-runner` subagentet (`agents/test-runner.md`) a gyors (unit/integration) tesztek és — ha a `conventions.md` tartalmaz `## Sonar minőségellenőrzés` szekciót — a SonarQube-elemzés lefuttatására. A subagent **strukturált összefoglalót** ad vissza (lásd az agent kontraktusát) — a nyers teszt-/Sonar-logot nem kéred vissza.

**A subagent két forrásból dolgozik, semmi másból (TR4):** minden **ciklus-specifikus** technikai részletet (parancsok, URL-ek, portok, teszt-userek, token-szerzés, indítási sorrend, előfeltételek) a **`plan.md`** `Tesztelési stratégia` / `Regressziós érintettség` / `E2E infrastruktúra` szekcióiból vesz — ezért írta a 03 fázis kötelezően **önhordóra** a plant (TC1/a) —, a **projekt-szintű eszköz-információt** (futtató, mappastruktúra, riport-tábla, Sonar-parancsok) pedig a `conventions.md`-ből. A `test-conventions.md`-t **nem olvassa**, régi ciklusokból nem dolgozik, és **nem találgat**. Az indításkor **hivatkozz rá explicit**, hogy a plan a ciklus-specifikus igazságforrás.

**Bizonyíték-ellenőrzés (TR1/TR2) — a jelentés átvételekor, kötelező:** minden kategóriánál ott kell lennie a **kiadott parancsnak** és a **darabszámoknak** (`X passed / Y failed / Z skipped`). Ha egy kategóriánál hiányzik a bizonyíték, vagy `0 passed / 0 failed` szerepel, azt **ne fogadd el PASS-nak**:
- Ha a `plan.md` Tesztelési stratégiája szerint annak a kategóriának léteznie kell → ez **FAIL** (`--failed-item "<kategória>: 0 teszt futott"`), nem zöld eredmény.
- Ha a plan szerint a kategória szándékosan nem létezik → `N/A`, és ezt írd is ki a kör lépés-táblájába.
- Ha a subagent bizonyíték nélkül jelentett, **kérd újra** tőle a hiányzó adatot, mielőtt döntesz. A saját feltételezésed nem pótolja a futtatást.

**Plan-hiány kezelése (TR4) — nem kód-bug, ne indíts rá fixert.** Ha a jelentés `## Plan-hiány (TR4)` szekciója nem üres (a runner azért hagyott ki egy tesztcsoportot, mert egy futtatási részlet nincs a `plan.md`-ben — pl. nincs leírva a lokális Keycloak indítása, hiányzik a teszt-user vagy a token-szerzés):

1. **Nézd meg magad a `plan.md`-ben** — a runner tévedhetett, vagy más szekcióban van. Ha ott van, add át neki explicit, és futtasd újra azt a csoportot.
2. **Ha tényleg hiányzik:** ez a **03 fázis hiánya**, nem az implementációé. A `implement-fixer` ezt nem tudja megjavítani (nem a kód a hibás), ezért **ne indíts hurok-iterációt rá**. Ehelyett **eszkalálj a tervezéshez** a VD5 felfelé menekülő ág szerint: a `plan.md` státusza `Piszkozat`-ra, egyetlen lezáró commit, és a felhasználónak szóló üzenetben **tételesen sorold fel, mi hiányzik** és melyik teszthez kell:
   > **[VALIDATE · plan-hiány · <teszt> ]**
   > *„A(z) `<tesztcsoport>` nem futtatható: a `plan.md` nem tartalmazza a(z) `<hiányzó adat>`-ot (pl. a lokális Keycloak indítási parancsát és a teszt-user adatait). Ez tervezési hiány, nem kód-hiba — a `test-runner` szándékosan nem találgat. A `plan.md` státuszát visszaállítottam; egészítsd ki a `Tesztelési stratégia` szekciót önhordóan (TC1/a), majd a `05→06→07` úton térünk vissza ide."*
3. **A lefutott tesztcsoportok eredményét ettől függetlenül naplózd** a kör riportjába — a kör FAIL, a kihagyott csoport a lépés-táblában „kihagyva — plan-hiány" sorként jelenik meg.

A subagent jelentése alapján:
- **Quality Gate PASS / N/A:** a `test-report/sonar-report.html` és `.md` riportok tájékoztató jellegű `MINOR`/`INFO` találatai nem akadályozzák a validálást.
- **Quality Gate FAIL vagy bármelyik gyors teszt FAIL:** **ne indítsd el a 2. lépést (nehéz tesztek)** — a kör eredménye FAIL, lépj a naplózásra, majd a hurok FAIL ágára. A javító feladatok (`tasks.md`) felvételekor csak a `BLOCKER`, `CRITICAL` és `MAJOR` szintű Sonar-találatokat tekintsd kötelezően javítandó akadálynak (a subagent az összeset jelenti, a szűrés itt, nálad történik).
- **Quality Gate FAIL, de nincs `BLOCKER`/`CRITICAL`/`MAJOR` találat (QG1):** a kaput nem finding, hanem **küszöb** buktatta (lefedettség, duplikáció, új kód minőségi kapuja). Ilyenkor **tilos** üres hibalistával fixert indítani — a hurok üresben forogna. Teendő:
  - Ha a `sonar-report.md`-ből egyértelmű a bukott feltétel és az **kód-oldalon javítható** (tipikusan: hiányzó teszt-lefedettség az új kódon) → vedd fel konkrét javító-taskként (pl. *„Fedd le tesztekkel a `<fájl>` új ágait — a QG coverage küszöbe X% alatt van"*), és a `--failed-item` neve a bukott feltétel legyen (pl. `Sonar QG: coverage on new code`).
  - Ha a bukott feltétel **nem a ciklus hatókörében** javítható (pl. örökölt duplikáció, projekt-szintű küszöb) → ez nem kód-bug: **STOP + humán**, a *„Hol járunk"* fejléccel, a bukott feltétel megnevezésével és két javaslattal (küszöb felülvizsgálata a `conventions.md`-ben, vagy külön ciklus). Ne indíts fixert.

### 2. Nehéz tesztek és regressziós ellenőrzések (`test-runner` subagent)

Csak akkor hívd, ha az 1. lépés PASS volt. Hívd újra a `test-runner` subagentet, most a nehéz tesztek (E2E + regresszió) lefuttatására — a `tasks.md` `TREG` jelölésű taskjai és a `plan.md` `Regressziós érintettség` táblázata alapján. A subagent felelőssége a szükséges backend szolgáltatások/konténerek elindítása, a portütközés-elhárítás és az ideiglenes erőforrások takarítása (lásd az agent kontraktusát).

> **⚠ Átmeneti port-módosítás:** ha a subagent jelentése ideiglenes config-/port-csere kell, ellenőrizd, hogy a jelentés szerint sikeresen visszaállt-e az eredeti állapot; ha nem, állítsd vissza te (`git checkout -- <fájl>`), mielőtt a validate fázis véget ér — ez nem kerülhet be a ciklus diffjébe.

**Egy funkció csak akkor kész, ha minden teszt és a Sonar is átment.** Részleges PASS nem elfogadható: ha bármelyik teszt vagy a Sonar hibázik, az egész validate FAIL.

### Naplózás és leállási korlátok (VD4 — determinisztikus, szkripttel)

> **🔴 EGY VALIDÁLÁSI KÖR = EGY futás-bejegyzés (VD4a).** Egy kör az 1–3. lépés (gyors tesztek + Sonar → nehéz tesztek → DoD/README). A kör eredményét **a kör VÉGÉN, egyetlen `failure-counter.py` hívással** naplózod, az összes bukott itemmel együtt. **TILOS részeredményt külön naplózni** (pl. „a gyors tesztek zöldek" bejegyzést az 1. lépés után): egy közbeiktatott PASS-bejegyzés **megszakítja az egymást követő bukások láncát**, és a 3-próba leállás soha nem lépne életbe — a hurok végtelenné válik. A `1.`/`2.` lépés részeredménye a kör **lépés-táblájába** kerül (lásd „A `validate-decision.md` — teljes validálási riport"), nem a History-ba.
>
> Mikor zárul a kör (mi kerül egy bejegyzésbe)?
> - **Az 1. lépés bukott** → a kör itt véget ér (nehéz tesztek nem futnak): egy FAIL bejegyzés a gyors teszt-/Sonar-itemekkel.
> - **Az 1. zöld, a 2. bukott** → egy FAIL bejegyzés a nehéz teszt-itemekkel (a zöld gyors teszteket nem naplózod külön).
> - **Az 1. és 2. zöld, a 3. (DoD/tasks) bukott** → egy FAIL bejegyzés a bukott `DoD-NN` azonosítókkal.
> - **Minden zöld** → egy PASS bejegyzés, `--failed-item` nélkül.

**A futás-bejegyzést és a számlálókat NE kézzel írd/számold** — a `failure-counter.py` szkript végzi (a telepítő a platform scripts-mappájába másolja: `.claude/scripts/` / `.agents/scripts/` / `.cursor/scripts/` / `.github/scripts/` / `.codex/scripts/`). A `test-runner` által **szó szerint** visszaadott bukott-item neveket add át neki (DoD-bukásnál a `DoD-NN` azonosítót — lásd a 3.A lépést):

```bash
# FAIL — minden bukott itemet külön --failed-item-ként (a test-runner szó szerinti nevein):
python3 <platform-scripts-mappa>/failure-counter.py \
  specs/cycle-NN-<cycle-name>/test-report/validate-decision.md \
  --result FAIL --timestamp "2026-08-06 14:32" \
  --failed-item "<pontos tesztnév/azonosító>" [--failed-item "<másik>" ...] \
  --details "<rövid ok>"
# PASS (minden zöld — --failed-item nélkül):
python3 <platform-scripts-mappa>/failure-counter.py \
  specs/cycle-NN-<cycle-name>/test-report/validate-decision.md \
  --result PASS --timestamp "2026-08-06 14:32"
```

**Időbélyeg (hordozhatóság):** a `--timestamp` értékét **konkrét stringként** add meg (`YYYY-MM-DD HH:MM`) — a szkript szándékosan nem olvas rendszeridőt. Ha shell-behelyettesítést használsz, az platformfüggő: bash/zsh → `$(date '+%Y-%m-%d %H:%M')`, PowerShell → `(Get-Date -Format 'yyyy-MM-dd HH:mm')`. Az elgépelt vagy hiányzó időbélyeg nem rontja el a számlálást (az item-nevek számítanak), de a napló olvashatóságát igen.

**Három leállási korlát — bármelyik teljesül → `exit 3` → a hurok MEGÁLL:**

| Korlát | Alapérték | Mit fog meg |
|---|---|---|
| per-item **egymást követő** bukás | 3 | a klasszikus 3-próba: ugyanaz az item körről körre bukik |
| per-item **összes** bukás a naplóban | 5 | a „hol bukik, hol nem" item — a megszakított láncot is |
| **egymást követő FAIL-futások** | 5 | divergáló hurok: körönként **más** item bukik (VD4b globális backstop) |

**A kilépő kód dönt, nem a saját ítéleted:**
- **`0`** → naplózva, egyik korlát sem telt be → a hurok folytatható.
- **`3`** → naplózva, valamelyik korlát betelt → **STOP**; a szkript kiírja, melyik item és melyik korlát miatt. A megállás típusát a VD5 heurisztika dönti el (tervezési hiba → eszkaláció; egyébként → STOP + humán).
- **`1`** → **hiba a hívásban, a napló NEM módosult.** Ilyenkor **tilos kézzel naplózni** — az szétverné a determinisztikus számlálást. Olvasd el a hibaüzenetet, javítsd a hívást (leggyakoribb ok: `FAIL` `--failed-item` nélkül, hiányzó `--timestamp`, vagy `PASS` melletti `--failed-item`), és futtasd újra. Ha kétszer sem sikerül, **STOP + humán**: jelezd a felhasználónak a parancsot és a hibaüzenetet.

**`FIGYELEM:` sor a kimenetben** — a szkript jelzi, ha egy item korábban is bukott, de egy közbeeső PASS megszakította a láncot. Ez majdnem mindig azt jelenti, hogy valaki (egy korábbi futás) **részeredményt naplózott** a VD4a szabály ellenére. Ne hagyd figyelmen kívül: a napló ilyenkor is helyesen áll meg az „összes bukás" korlátnál, de a `# Validation History` félrevezető — írd a `--details`-be, hogy a lánc megszakadt.

### 3. DoD és README ellenőrzések

#### A. Definition of done ellenőrzése
Minden DoD ponthoz adjál egyértelmű választ: ✓ vagy ✗, egy mondatban indokolva. **A pontokra mindig a `DoD-NN` azonosítójukkal hivatkozz** (DI1) — a riportban, a naplóban és a javító-taskokban egyaránt.

> **⚠ Fontos akció:** Minden teljesített (`✓`) pontot azonnal jelölj `[x]`-szel a `spec.md` megfelelő sorában is — ne várd meg a teljes validálás végét. (Ez a `spec.md`-t commitálatlanul módosítja; a hurok alatt ez így helyes — a commit a hurok végén, egyszer történik, VD8.)

> **🔴 Item-név DoD-bukásnál:** a `failure-counter.py` `--failed-item` értéke **pontosan a `DoD-NN` azonosító** legyen (pl. `--failed-item "DoD-03"`), soha ne a pont parafrazeált szövege. A számláló szó szerinti név-egyezésre épül: körönként másképp megfogalmazott szöveg mellett a leállási korlát csendben soha nem lép életbe. **Ha a `spec.md` DoD-pontjainak nincs `DoD-NN` azonosítójuk** (régebbi ciklus), **először pótold őket a `spec.md`-ben** (sorfolytonosan, a meglévő sorrendben), és csak utána naplózz — a pótlás nem tartalmi változtatás, nem sérti a VD3-at.

#### A/2. `validate-input-from-prev.md` lezárása (IP1)
Ha a fájl létezik, menj végig a tételein: mindegyik vagy **figyelembe vett** (`→ figyelembe vettem: <hogyan>`), vagy **explicit indokkal elvetett**. Nyitott `[ ]` tétellel a validálás nem zárható PASS-ra. Ha egy tétel a validálás során **hibát okozott** (pl. hiányzó előfeltétel miatt bukott el egy teszt), az FAIL — a szokásos hurok szerint javítandó, nem elvetéssel elintézendő.

#### B. Meglévő komponens README ellenőrzése
Ha a ciklus meglévő komponens konfigurációját (env var-ok, indítási paraméterek, külső kapcsolatok) változtatta meg: a komponens `README.md` szinkronban van-e a változásokkal? Ha nem, jelezd — a README frissítése az implement fázis lezáratlan feladata.

#### C. Tasks ellenőrzése
Minden task `[x]` státuszban van-e? Ha van elvégzetlen task, jelezd.

#### C/2. Kötelező teszt-riportok kapuja (TR3 — determinisztikus)

A `conventions.md` `## Teszt-riportolás` táblájában deklarált riport-artefaktumoknak ott kell lenniük a ciklus `test-report/` mappájában. Ezt **ne szemre nézd meg** — futtasd a kaput:

```bash
python3 <platform-scripts-mappa>/report-gate-check.py \
  conventions.md specs/cycle-NN-<cycle-name>
```

- **`exit 0`** → a kapu ✓ (vagy a projekt explicit nem generál riportot). Az eredményt írd be a kör riportjába.
- **`exit 1`** → hiányzó vagy üres artefaktum. **A kör nem zárható PASS-ra**, de ez **nem kód-bug**, ezért **nem indítasz fixert**: a riport előállítása a `test-runner` dolga.
  1. Hívd újra a `test-runner`-t **kifejezetten a hiányzó riport(ok) előállítására**, a táblában megadott paranccsal, és kérd, hogy az artefaktumot a ciklus `test-report/` mappájába tegye.
  2. Futtasd újra a kaput. Ha másodszorra is bukik → **STOP + humán** a „Hol járunk" fejléccel: *„A(z) [artefaktum] riport két próbálkozásra sem jött létre a `<parancs>` paranccsal. Humán beavatkozás szükséges — hogyan tovább?"*, a szkript kimenetével együtt.
- **`exit 2`** → a `conventions.md` `## Teszt-riportolás` szekciója hiányzik vagy kitöltetlen (placeholder maradt). Ez **projekt-konfigurációs hiány**, nem teszt-hiba: **STOP + humán**, és kérd a szekció pótlását a `00-init` szerinti tartalommal (kategória / eszköz / parancs / artefaktum, vagy explicit `**Riport-generálás kötelező:** nem` + indoklás). Magad ne találd ki a parancsot, és **ne írd át a `conventions.md`-t** — az a 00 fázis és a felhasználó közös döntése.

> A kapu **minden körben** fut, nem csak az utolsóban: így a riport a bukott körökről is megmarad, és utólag látszik, mi bukott el a 2. körben.

#### D. Kódkommentek és docstringek ellenőrzése
Ellenőrizd a módosított vagy újonnan létrehozott fájlokban lévő kommenteket és JSDoc/TSDoc leírásokat. Győződj meg róla, hogy a végrehajtott kódváltozások (pl. átnevezések, logikai módosítások) után a hozzájuk kapcsolódó kommentek is frissültek, és nem maradtak elavult (stale) vagy félrevezető megjegyzések a forráskódban.

---

## A `validate-decision.md` — teljes validálási riport (VD9)

> **A fájl nem egy egysoros run-log, hanem a validálás teljes futásnaplója.** Utólag ebből kell kiderülnie, hogy **mi futott, milyen sorrendben, milyen eredménnyel, mi futott újra és miért** — anélkül, hogy bárkinek vissza kellene keresnie a chatet (`/clear` után az nem is létezik). Ha a fájlban csak a `# Validation History` van, a fázis **nem** végezte el a dolgát.

**Ki mit ír a fájlba — két, élesen elválasztott régió:**

| Régió | Hol | Gazda | Tartalom |
|---|---|---|---|
| Fejléc + `## Kör N` blokkok | a fájl elejétől | **te (az orchestrátor)** | a futás eseménynaplója, körönként egy blokk, **hozzáfűzve — korábbi kört SOHA nem írsz felül** |
| `# Validation History` | a fájl **végén** | **kizárólag a `failure-counter.py`** | gépi run-log a leállási számlálókhoz |

**Írási szabály (fontos):** a szkript mindig a **fájl végére** fűz, ezért a `# Validation History` fejlécnek a fájl végén kell maradnia. Az új `## Kör N` blokkot **közvetlenül a `# Validation History` fejléc ELÉ** szúrod be. Gyakorlatban: olvasd be a fájlt, állítsd össze az új tartalmat (fejléc + eddigi körök + új kör + változatlan History), és írd ki. **A History szekció sorait soha ne szerkeszd, ne rendezd át, ne töröld.**

**Mikor írsz:** minden kör **végén**, a naplózó szkript futtatása **előtt** — PASS-nál és FAIL-nál egyaránt. Ezen felül a kör közben keletkező eseményeket (fixer indítása, visszatérése, kapu eredménye) **menet közben** jegyzed fel, hogy egy megszakadt futás után is megmaradjon a nyom.

### A fájl sablonja

```md
# Validálási riport — cycle-NN-<cycle-name>

**Jelenlegi státusz:** folyamatban | PASS | FAIL (megállt) | eszkalálva
**Körök száma:** N
**Utolsó frissítés:** YYYY-MM-DD HH:MM

_(Ezt a fejlécet minden kör végén frissíted — ez az egyetlen rész, amit felülírsz.)_

---

## Kör 1 — YYYY-MM-DD HH:MM — FAIL

**Indító:** 07-validate első futás | önjavító hurok N. iterációja | 09-review re-validate | megszakadt futás folytatása

### Lépések (végrehajtási sorrendben)

| # | Idő | Lépés | Mit futtatott | Eredmény |
|---|---|---|---|---|
| 1 | 10:32 | test-runner — gyors tesztek | `npm test -- --run` | ✗ FAIL — 41 passed / 2 failed / 0 skipped |
| 2 | 10:34 | test-runner — Sonar | `./scripts/sonar-report.sh` | ✓ QG PASS (MAJOR: 0, MINOR: 3) |
| 3 | — | nehéz tesztek | **kihagyva** — az 1. lépés bukott | — |
| 3b | — | E2E (opcionális sor) | **kihagyva** — plan-hiány (TR4): nincs leírva a Keycloak indítása | eszkaláció a 03-ra |
| 4 | 10:35 | teszt-riport kapu (TR3) | `report-gate-check.py conventions.md specs/cycle-NN-…` | ✓ exit 0 — `allure-report.html` (412 KB), `unit-report.html` (88 KB) |
| 5 | 10:35 | DoD-ellenőrzés | — | ✗ DoD-03 nem teljesül |
| 6 | 10:36 | naplózás | `failure-counter.py --result FAIL --failed-item ...` | exit 0 — folytatható |

### Bukott elemek

- `auth.spec.ts > refresh token rotation` — `expected 200, received 401` _(1/3 egymást követő, 1/5 összes)_
- `DoD-03` — a `/verify` végpont nem ad `correlationId`-t a válaszban _(1/3, 1/5)_

### Definition of done

| ID | Eredmény | Indoklás |
|---|---|---|
| DoD-01 | ✓ | a token-csere 200-at ad a `<scope>` scope-pal |
| DoD-03 | ✗ | a válaszból hiányzik a `correlationId` |

### Teszt-riportok (TR3)
- `report-gate-check.py` → exit 0 / 1 / 2 — a `test-report/`-ba került artefaktumok felsorolása mérettel (vagy: mi hiányzik)

### Tasks elvégzettsége
- Minden task `[x]`: ✓ / ✗ (ha ✗: az elvégzetlen taskok felsorolása)

### Kódkommentek és dokumentáció
- Kommentek és docstringek naprakészek: ✓ / ✗

### Javító kör (ha volt)

- **Felvett javító-taskok:** T041 `[GREEN]` — …, T042 `[CHECK]` — … _(a `## Validációs javítások` szekcióba)_
- **`implement-fixer` indítva:** 10:38 — bemenet: a fenti 2 bukott elem
- **A fixer visszajelzése:** 10:44 — „T041 lezárva: a rotáció most a `refreshToken()`-ben történik"; eszkalációs jelzés: nincs
- **Szerződés-integritás kapu (VD3a):** ✓ tiszta — a `git diff` nem érintett tesztfájlt / `spec.md`-t / Sonar-konfigot
  _(vagy: ✗ — `auth.spec.ts` módosítva (assertion lazítva) → `git checkout --` visszaállítva → eszkaláció)_

### A kör döntése

FAIL → új kör indul a javítás után. | PASS → a hurok konvergált, státuszok `Kész`-re. | STOP — [betelt korlát] → humán döntés. | Eszkaláció 03/02-re — [indok].

---

## Kör 2 — YYYY-MM-DD HH:MM — PASS

_(ugyanaz a szerkezet; a 3. lépésnél már látszik, hogy a nehéz tesztek is lefutottak)_

---

## Összegzés

- **Végeredmény:** PASS — 2 kör után
- **Újrafuttatott elemek:** `auth.spec.ts > refresh token rotation` (2 kör), `DoD-03` (2 kör)
- **Eszkaláció / humán beavatkozás:** nem volt
- **Ideiglenes környezeti módosítás:** [ha volt port-csere: melyik, és visszaállt-e]

# Validation History
_(ezt a szekciót a failure-counter.py írja — kézzel nem szerkeszted)_
```

### Kötelező tartalmi elemek (ezek nélkül a riport hiányos)

1. **Végrehajtási sorrend, időbélyeggel** — a lépés-tábla mutassa, mi futott, milyen sorrendben, és **mi maradt ki, miért** (pl. a nehéz tesztek kihagyása bukott gyors tesztek után). A „kihagyva" sor ugyanolyan fontos, mint a lefutott lépés.
2. **A `test-runner` bizonyítékai szó szerint** — a kiadott parancs és a `X passed / Y failed / Z skipped` darabszámok (TR1). Ez teszi utólag ellenőrizhetővé, hogy a PASS mögött tényleges futtatás állt.
2.a **A teszt-eszköz saját riportja a `test-report/`-ban (TR3)** — a riport-kapu kimenete (mely artefaktumok kerültek be, mekkorák). A riport a fájl mellett, a ciklus mappájában él; a szöveges napló nem helyettesíti, a riport nem helyettesíti a naplót.
3. **Az újrafuttatások láthatósága** — minden kör külön blokk, és az `## Összegzés` sorolja fel, mely elemek futottak többször (ez a „mi futott újra" kérdés válasza).
4. **A javító kör nyoma** — mely taskokat vette fel, mit adott vissza a fixer, mi volt a szerződés-integritás kapu (VD3a) eredménye. Ha a kapu gyengítést talált, **az érintett fájl és a visszaállítás ténye is** kerüljön be.
5. **A kör döntése egy mondatban** — miért indult új kör, vagy miért állt meg a hurok.

> **A 09-review re-validate körei is ide kerülnek** (`**Indító:** 09-review re-validate`), hogy a ciklus teljes validálási története egy fájlban legyen — a `code-review.md` a review-hurok naplója, nem a validálásé.

---

## Az önjavító hurok (orchestrátor-hurok)

FAIL esetén **nem** adod vissza egyszerűen a vezérlést a felhasználónak. Levezényelsz egy iteratív javító hurkot — `implement-fixer` subagent → újra-validálás — amíg PASS nem lesz, vagy amíg a **3-próba szabály (VD4)** / a **felfelé menekülő ág (VD5)** meg nem állítja.

A meglévő FAIL-gépezet megmarad (a `validate-decision.md` `# Validation History`, a `tasks.md` `## Validációs javítások`, a státusz-visszafordítás) — csak a korábbi „kézi visszaadás a felhasználónak (futtasd újra a 06-ot)" lesz orchesztrált hurok. A javítást nem te végzed: azt az `implement-fixer` subagent (= a 06 Fix-módja) csinálja; te validálsz, naplózol, döntesz és státuszt fordítasz.

### ⚠ Anti-„teszt-csalás" garde (VD3 — a hurok legfontosabb szabálya)

**A hurok a KÓDOT igazítja a teszthez / Sonarhoz / DoD-hoz — SOHA nem fordítva.** A teszt és a Definition of done a **szerződés**; a hurok ezt a zöld eredmény érdekében **nem módosíthatja**.

**STOP — tilos** bármelyik:
- teszt assertion gyengítése/lazítása, vagy az elvárt érték a kódból visszamásolása;
- teszt `skip`/`xfail`/kikommentezése/törlése a zöldért;
- hardcode-olt „elvárt" érték, amely a tesztet zöldíti, de a valós viselkedést nem valósítja meg;
- a `spec.md` DoD-pont leszállítása/átfogalmazása, hogy könnyebben teljesüljön.

Ezt a szabályt az `implement-fixer` is megkapja (a 06 Fix-mód garde-ja) — egy olcsóbb LLM se sodródjon teszt-csalásba. **Ha egy hiba csak a teszt/DoD megváltoztatásával lenne zöld** → az nem kód-fix, hanem **tervezési hiba** → VD5 (felfelé menekülő ág), nem a teszt lazítása.

#### 🔴 Szerződés-integritás kapu a fixer után (VD3a — determinisztikus, kötelező)

A fenti tiltás önmagában **csak instrukció** — a fixer olcsóbb modellen fut, és a hurok teljes értéke azon áll, hogy a zöld eredmény valódi. Ezért a fixer minden visszatérése után, **még az újra-validálás előtt**, nézd meg **ténylegesen**, mit írt át:

```bash
git status --short          # mi módosult a hurok kezdete óta (a hurok alatt nincs commit — VD8)
git diff -- <tesztfájlok/mappák a conventions.md „Teszt struktúra" szerint> \
            specs/cycle-NN-<cycle-name>/spec.md \
            <Sonar/lint konfig a conventions.md szerint>
```

- **Ha a diff üres** ezekre az útvonalakra → a kapu ✓, mehet az újra-validálás.
- **Ha bármelyik érintett**, olvasd el a diffet, és döntsd el, melyik eset:
  - **Legitim** (új teszt hozzáadása a hibához, `DoD-NN` azonosító pótlása, elgépelés javítása a teszt *nevében*) → ✓, de **írd be a kör „Javító kör → Szerződés-integritás kapu" sorába**, mit és miért.
  - **Szerződés-gyengítés** (assertion lazítása, `skip`/`xfail`, teszt törlése, elvárt érték kódból visszamásolva, DoD-pont átfogalmazása/leszállítása, Sonar-szabály kikapcsolása) → **STOP, ez teszt-csalás.** Teendő: (1) állítsd vissza az érintett fájlokat (`git checkout -- <fájl>`); (2) az adott itemet naplózd FAIL-ként a szokásos módon; (3) kezeld **eszkalációs jelzésként** (VD5) — a hurok nem próbálkozik tovább ezzel az itemmel, mert a fixer a szerződést támadta, nem a kódot.
- A `git checkout --` visszaállítás után **ne** indíts azonnal új fixert ugyanarra az itemre — az a kör FAIL-je, és a VD5 ág dönt.

Ez a kapu az egyetlen hely, ahol a VD3 nem csak szándék, hanem **ellenőrzött tény** — ne hagyd ki, még akkor sem, ha a fixer összefoglalója azt állítja, hogy nem nyúlt a tesztekhez.

### A hurok egy iterációja

1. **A kör FAIL-jének naplózása (VD4a) — a `failure-counter.py` szkripttel, körönként EGYSZER.** Futtasd a `--result FAIL` + a kör **összes** bukott item-nevével (lásd „Naplózás és leállási korlátok"). Ez naplózza a futást ÉS kiszámolja a számlálókat — **ne kézzel**. Előtte zárd le a kör `## Kör N` blokkját a `validate-decision.md`-ben (VD9).
2. **Leállás-döntés a szkript kilépő kódjából (VD4).** `exit 3` → valamelyik korlát betelt (per-item 3 egymást követő / 5 összes bukás / 5 egymást követő FAIL-futás) → a hurok megáll (lásd „Leállási korlátok mint hurok-korlát"); a megállás típusát a VD5 heurisztika dönti el (tervezési hiba → eszkaláció; egyébként → STOP + humán). `exit 1` → hibás hívás, javítsd és futtasd újra (kézzel naplózni TILOS). `exit 0` → folytatható a hurok.
3. **Korai eszkaláció-ellenőrzés (VD5).** Ha az előző iteráció `implement-fixer` subagentje **eszkalációs jelzést** adott vissza, vagy a **szerződés-integritás kapu (VD3a)** gyengítést talált, ne körözz tovább a 06-ban → **azonnal eszkalálj** (lásd „Felfelé menekülő ág"), nem kell megvárni a 3. próbát.
4. **Javító-taskok felvétele.** A FAIL-gépezet szerint (lásd „FAIL — javító-taskok felvétele"): `## Validációs javítások` szekció a `tasks.md` végén, prerequisite hivatkozásokkal, `[GREEN]`/`[CHECK]` taskként a konkrét teszt-/Sonar-hibák. Duplikátum-kerülés: ne vedd fel kétszer ugyanazt. **Üres hibalistával nem indul iteráció** — ha nincs konkrét javítandó tétel (pl. QG1 küszöb-bukás), a hurok nem folytatható, lásd a QG1 ágat.
5. **Marker felvétele (VD6).** A `tasks.md` státuszát fordítsd `Implementálásra kész [validate-loop]`-ra. A marker jelzi: fix-mód aktív → a fixer automatikusan lépteti a státuszt, megerősítés nélkül.
6. **`implement-fixer` subagent indítása (VD2).** A konkrét teszt-/Sonar-hibalistával + a prerequisite riportokkal (lásd „A fixer-subagent indítása"). Ha a fixer **eszkalációs jelzést** ad vissza → ugorj a 3. pontra.
7. **Szerződés-integritás kapu (VD3a).** A fixer visszatérése után futtasd a fenti `git diff` ellenőrzést, **mielőtt** újra validálnál. Gyengítés esetén: visszaállítás + eszkaláció (3. pont).
8. **Újra-validálás.** Kezdd elölről a „Validálási lépéseket" (gyors tesztek → Sonar → nehéz tesztek → DoD/README). Ez egy **új kör** — a végén megint pontosan egy naplóbejegyzés készül.
   - **PASS** (minden teszt + Sonar + DoD zöld) → a hurok konvergált, ugrás a „Státusz kezelés → PASS"-ra (itt kerül le a marker, és történik az egyetlen lezáró commit).
   - **FAIL** → új iteráció az 1. ponttól.

### A fixer-subagent indítása (VD2)

- A subagent **rendszerpromptja** az `agents/implement-fixer.md` wrapper, amely a `06-implement.md` „Fix-mód (validate-hurok belépő)" szekciójára delegál — nincs duplikált javító logika, a 06 minőségi szabályai automatikusan érvényesülnek.
- **Bemenet:** a `tasks.md` `## Validációs javítások` elvégzetlen taskjai (a konkrét teszt-/Sonar-/DoD-hibák) + a prerequisite riportok (`validate-decision.md`, és ha Sonar bukott, `sonar-report.md`).
- **Kimenet:** (a) az elvégzett javítások összefoglalója (mely taskot mivel zárt le), és (b) **eszkalációs jelzés**, ha valamelyik hibát csak a teszt/DoD módosításával lehetne zöldre vinni (VD3). A subagent **nem** módosíthatja a tesztet/DoD-ot, és **nem** írja a `validate-decision.md`-t — azt te (az orchestrátor).

### Felfelé menekülő ág (VD5 — escape hatch)

Nem minden FAIL kód-bug: néha **tervezési hiba** (a teszt/DoD a kóddal ellentmondó, vagy a terv hibás alapra épül). Ilyenkor a hurok ne 06-ban körözzön — a 06 sosem fogja zöldre vinni, mert csak a tesztet/DoD-ot lazítva lehetne, azt pedig VD3 tiltja.

**Detektálási heurisztika** — tervezési hiba jele, ha:
- **(a)** az `implement-fixer` eszkalációs jelzést adott vissza (a hibát csak a teszt/DoD megváltoztatásával lehetne zöldre vinni), **vagy**
- **(b)** a leállási korlát elérésekor a megrekedt itemet az addigi javítási kísérletek alapján csak a teszt/DoD megváltoztatásával lehetne zöldre vinni, **vagy**
- **(c)** a **szerződés-integritás kapu (VD3a)** azt találta, hogy a fixer a tesztet/DoD-ot/Sonar-konfigot módosította a zöldért — ilyenkor a visszaállítás után nincs értelme újra ugyanazt kérni tőle.
- **(d)** a `test-runner` **plan-hiányt** jelentett (TR4): egy tesztcsoport azért nem futott, mert a futtatási részlet nincs a `plan.md`-ben. Ez a 03 fázis hiánya — a fixer nem tudja megjavítani, mert nem a kód a hibás.

**Teendő (STOP + eszkaláció), sorban:**
1. Naplózd a `# Validation History`-ba a megrekedt itemet, és hogy **tervezési hiba** miatt eszkalálsz (nem kód-bug) — a `--details` mezőben.
2. **Státusz-visszafordítás 03/02-re:** fordítsd vissza az érintett tervezési dokumentum státuszát a megfelelő nem-kész értékre — `plan.md` → `Piszkozat` (ha a terv hibás), vagy `spec.md` → `Piszkozat` (ha maga a DoD a hibás/ellentmondásos). A `tasks.md` a `[validate-loop]` markerrel marad (a megrekedt állapot jelzése).
3. **Egyetlen lezáró commit** (VD8) — a *Fázis-záró commit* szekció eljárása szerint, **kötelező** (az eszkalációs ág sem kivétel).
4. **Jelezd a felhasználónak az átadást** — ez tervezési kérdés, nem automatikus javítás (a list2 analyze-szellemű tervezési hurokra tartozik), lásd a jelzés szövegét lent. A folyamat a tervezés rendezése után a `05→06→07` úton tér vissza ide.

### Leállási korlátok mint hurok-korlát (VD4)

A hurok korlátját **a `failure-counter.py` kilépő kódja** adja — **nem a saját becslésed, és nem kézzel olvasott számláló**. Három korlát fut párhuzamosan (részletek: „Naplózás és leállási korlátok"):

1. **per-item 3 egymást követő bukás** — a klasszikus 3-próba: pont a beragadt elemet fogja meg;
2. **per-item 5 összes bukás** — a „hol bukik, hol nem" item, amely a láncot megszakítva kerülné el az (1)-et;
3. **5 egymást követő FAIL-futás (VD4b)** — globális backstop arra, amikor **körönként más item bukik**: a hurok nem konvergál, csak új hibákat termel. Ez a korlát a per-item számlálóktól függetlenül megállítja a divergáló hurkot.

Bármelyik teljesül → `exit 3` → **a hurok megáll**, a szkript kiírja, melyik item és melyik korlát miatt.

- Ha a megállás **tervezési hiba** jele (VD5 heurisztika) → **eszkaláció** (felfelé menekülő ág).
- Egyébként → **STOP + humán** (megrekedt kód-bug): *„A(z) [Failed Item] [N]. alkalommal is elbukott ([melyik korlát]). Humán beavatkozás szükséges — hogyan tovább?"* A (3) korlátnál: *„A javító hurok [N] köre óta nem konvergál — körönként más elem bukik el. Humán beavatkozás szükséges — hogyan tovább?"*, a legutóbbi körök bukott elemeinek felsorolásával. Ne folytasd a javítást a felhasználó válasza nélkül. Commit a végén (VD8); a `## Validációs javítások` és a `[validate-loop]` marker megmarad (megrekedt állapot).

### Commit-stratégia a hurokban (VD8)

- **A hurokban nincs iterációnkénti commit** — a korábbi FAIL-enkénti commit megszűnik.
- **Egyetlen lezáró commit** a hurok végén (PASS / 3-próba STOP / eszkaláció):
  ```bash
  git add specs/cycle-NN-<cycle-name>/
  git commit -m "cycle-NN: 07-validate"
  ```
- **Megszakítás-biztos:** a köztes commit hiányát a `# Validation History` + a `[validate-loop]` státusz-marker pótolja — ezekből a folytatás rekonstruálható (lásd „Megszakított futás kezelése").

**A lezáró commit KÖTELEZŐ, kivétel nélkül minden lezáró ágon** (PASS, leállási korlát STOP, felfelé eszkaláció, QG1 küszöb-bukás) — az eljárást lásd a *Fázis-záró commit* szekcióban. Commit nélkül nem adhatod vissza a vezérlést a felhasználónak.

<!-- INCLUDE:shared/phase-commit.md -->

A fenti blokkban a `<FÁZIS-TAG>` értéke ebben a fázisban: **`07-validate`**. A 2. lépés (státuszírás) itt az adott lezáró ág szabálya szerinti státusz/marker-rendezést jelenti (PASS-nál `spec.md`/`plan.md`/`tasks.md` → `Kész` + marker le; STOP/eszkalációnál a visszafordított státusz + a marker fennmaradása). A commit előtt **nem** kérsz megerősítést.

> **Megállási szabály (PC1):** ha a hurok lezárult (bármely ágon), de a fázis-záró commit hiányzik (VCS-es projekt, `git log -1 --oneline` nem a `cycle-NN: 07-validate` commitot mutatja), **STOP** — először commitolj, csak utána zárd le a fázist és add meg a következő lépést / a megállási üzenetet.

### „Hol járunk" a megállási üzenetekben (LC2)

A user-felé tett megállási üzeneteknél (leállási korlát STOP, eszkaláció, QG1 küszöb-bukás — ez a hurok **egyetlen** user-érintkezése, lásd VD7) jelezd, hol tart a hurok: a megrekedt elemet és a betelt korlátot, a `# Validation History`-ra hivatkozva:

```
[VALIDATE · <Failed Item> · próba 3/3]                  ← per-item korlát
[VALIDATE · <Failed Item> · összes bukás 5/5]           ← per-item összes-korlát
[VALIDATE · divergáló hurok · FAIL-futások 5/5]         ← globális backstop
```

A válaszod végén kötelezően helyezz el egy közvetlen, kattintható linket a `validate-decision.md`-re.

---

## Státusz kezelés

> **A PASS automatikus, mert determinisztikus ellenőrzéseken alapul (tesztek + Sonar + DoD). Felhasználói megerősítés NEM szükséges — ne kérj megerősítést a `Kész` státuszra váltás előtt. Az eredmény utólag is ellenőrizhető a `validate-decision.md`-ben (VD9: körönkénti lépés-napló + `# Validation History`).**

### PASS

Minden teszt átment (bizonyítékkal — TR1/TR2), a DoD minden pontja teljesül, minden task `[x]`, a Sonar Quality Gate PASS (vagy N/A), **a teszt-riport kapu (TR3) `exit 0`**, és a szerződés-integritás kapu (VD3a) tiszta.

Teendők:
1. **Zárd le a kör `## Kör N` blokkját** a `validate-decision.md`-ben, és frissítsd a fejlécet + az `## Összegzés` szekciót (VD9), majd naplózz: `failure-counter.py ... --result PASS --timestamp "..."` (`--failed-item` nélkül). Ez zárja le a kört a naplóban.
2. **Vedd le a `[validate-loop]` markert** (ha a hurok futott): a `tasks.md` státusza `Kész`-re vált — marker nélkül. Frissítsd a `plan.md` és `spec.md` státuszát is `Kész`-re.
3. **Egyetlen lezáró commit** (a hurok alatt nem volt köztes commit — VD8), a *Fázis-záró commit* szekció eljárása szerint — **kötelező**:
   ```bash
   git add specs/cycle-NN-<cycle-name>/
   git commit -m "cycle-NN: 07-validate"
   ```
4. Jelezd: *"Validálás sikeres. Folytathatjuk a 8. lépéssel: dokumentáció szinkron (08-doc-sync). Az új fázis megkezdése előtt mindenképpen futtass egy `/clear` parancsot a kontextus kiürítéséhez, majd használd ezt a parancsot:*
   > ```
   > /bs-doc-sync input: @specs/cycle-NN-<cycle-name>
   > ```"*
   > **A válasz végén helyezd el a `validate-decision.md` közvetlen, kattintható linkjét.**

### FAIL — javító-taskok felvétele (a hurok 4–6. lépése)

Ha bármely teszt, a Sonar, vagy a DoD ellenőrzés hibázik, **nem** adod vissza a vezérlést a felhasználónak — a hurok következő iterációját készíted elő és indítod (lásd „Az önjavító hurok"). Lépések **sorban**:

```
[ ] 1. ## Kör N blokk lezárva a validate-decision.md-ben (VD9): lépés-tábla a
        végrehajtási sorrenddel + a test-runner bizonyítékaival (parancs +
        X passed/Y failed/Z skipped), bukott elemek, DoD-tábla, a kör döntése
[ ] 2. failure-counter.py lefuttatva EGYSZER, a kör VÉGÉN (--result FAIL +
        a kör ÖSSZES bukott iteme; DoD-bukásnál DoD-NN azonosítóval) →
        # Validation History frissítve, a számlálók determinisztikusan léptetve
        ⚠ részeredményt (pl. „gyors tesztek zöldek") NEM naplózol külön (VD4a)
[ ] 3. Leállás a szkript kilépő kódjából: exit 3 → STOP (eszkaláció vagy humán,
        lásd lent) — NE indíts újabb fixert; exit 1 → hibás hívás, javítsd és futtasd
        újra (kézzel naplózni TILOS); exit 0 → tovább
[ ] 4. tasks.md → ## Validációs javítások fejezet létrehozva vagy folytatva
[ ] 5. A fejezet elejére prerequisite hivatkozásként berakva:
        - specs/cycle-NN-<cycle-name>/test-report/validate-decision.md
        - (ha Sonar hibázott) specs/cycle-NN-<cycle-name>/test-report/sonar-report.md
[ ] 6. Konkrét javítandó tesztek / Sonar hibák / DoD-NN pontok felvéve [GREEN]
        taskokként, a csoport végén egy [CHECK] ellenőrző taskkal (duplikátum-kerülés!)
        ⚠ ha a lista ÜRES lenne (QG1 küszöb-bukás) → nem indul iteráció, lásd QG1
[ ] 7. tasks.md státusz → Implementálásra kész [validate-loop]   (marker, VD6)
[ ] 8. implement-fixer subagent indítva a konkrét hibalistával (VD2)
[ ] 9. A fixer visszatérése után: szerződés-integritás kapu (VD3a) — git diff a
        tesztfájlokra / spec.md-re / Sonar-konfigra. Gyengítés → git checkout --
        visszaállítás + eszkaláció (VD5). Eszkalációs jelzés a fixertől → VD5.
        Egyébként → újra-validálás (a hurok 8. lépése, új kör)
```

**A FAIL ág itt NEM commitol és NEM ad vissza vezérlést a felhasználónak** — a commit a hurok végén egyetlen alkalommal történik (VD8), a felhasználói érintkezés pedig csak a leállási korlát STOP / eszkaláció / QG1 esetén (VD7).

#### Eszkaláció jelzése a felhasználónak (VD5 — felfelé menekülő ág)

A „Hol járunk" fejléccel (LC2):
> **[VALIDATE · <Failed Item> · próba N/3]**
> *"A validáció során a(z) [Failed Item] tervezési hibának bizonyult: a kód csak a teszt vagy a Definition of done megváltoztatásával lenne zöld, amit a hurok nem tehet meg (anti-„teszt-csalás"). Ezért nem a 06-implementbe léptem vissza, hanem a tervezési fázishoz eszkalálok. A(z) [plan.md / spec.md] státuszát visszaállítottam, hogy a tervezési döntést rendezni lehessen. Folytasd a tervezés felülvizsgálatával:*
> ```
> /bs-write-plan (DoD-hiba esetén: /bs-write-spec) input: @specs/cycle-NN-<cycle-name>/plan.md (vagy spec.md)
> ```
> *A folyamat a tervezés rendezése után a 05→06→07 úton tér vissza ide."*
> **A válasz végén: kattintható link a `validate-decision.md`-re.**

#### Validációs leállás (VD4 — a szkript `exit 3`-ára)

Ha a `failure-counter.py` `exit 3`-mal tér vissza (bármelyik a három korlát közül: per-item 3 egymást követő, per-item 5 összes, vagy 5 egymást követő FAIL-futás) — **állj meg**. Ne felülbíráld a szkript döntését, és ne indíts „még egy utolsó" fixert. Döntsd el a megállás típusát a VD5 heurisztika szerint:
- **tervezési hiba** (csak a teszt/DoD módosításával lenne zöld, vagy a VD3a kapu gyengítést talált) → **eszkaláció** (fenti üzenet);
- **megrekedt kód-bug** → a „Hol járunk" fejléccel: *„A(z) [Failed Item] [N]. alkalommal is elbukott ([betelt korlát]). Humán beavatkozás szükséges — hogyan tovább?"*
- **divergáló hurok** (a globális backstop telt be) → *„A javító hurok [N] köre óta nem konvergál — körönként más elem bukik el: [itemek]. Humán beavatkozás szükséges — hogyan tovább?"*

Egyik esetben se folytasd a javítást a felhasználó válasza nélkül. Mindegyiknél: **egyetlen lezáró commit** (VD8), a `[validate-loop]` marker és a `## Validációs javítások` a megrekedt állapot jelzésére a `tasks.md`-n marad.