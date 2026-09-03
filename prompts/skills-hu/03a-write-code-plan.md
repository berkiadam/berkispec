---
phase: 03a
name: bs-write-code-plan
description: "berkispec - 03a. Használd, ha a ciklus spec.md-je 'Tervezésre kész' (Phase 03a), a technikai megvalósítási terv KÓD-OLDALÁNAK kidolgozásához: környezeti koordináták, tervezett módosítások (céllal), konfiguráció, séma-artefaktumok, scope-kapu (kódbázis-elemzés, szükség esetén researcher subagent). A plan.md-t 'Teszt-tervezésre kész' státuszra zárja; a teszt-tervet a /bs-write-test-plan írja."
prerequisites:
  - "specs/cycle-NN-<name>/spec.md státusz: <status:ready_for_plan>"
output:
  - "specs/cycle-NN-<name>/plan.md státusz: <status:ready_for_test_plan> (a kód-terv szekciói)"
  - "specs/cycle-NN-<name>/plan-questions.md"
  - "specs/cycle-NN-<name>/tasks-input-from-prev.md és/vagy validate-input-from-prev.md (csak ha van átadandó infó, IP1)"
prev: bs-write-spec
next: bs-write-test-plan
subagents:
  - "agents/researcher.md"
scripts:
  - "scripts/analyze-gate-check.py"
shared:
  - "shared/plan-self-contained.md"
  - "shared/dereferencing.md"
  - "shared/spec-artifact-transfer.md"
  - "shared/plan-section-ids.md"
  - "shared/conventions-change.md"
  - "shared/input-from-prev.md"
  - "shared/artifact-voice.md"
  - "shared/phase-commit.md"
  - "shared/quality-check-plan-code.md"
---
# 03a — Kód-terv írás
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

Spec driven development-ben fejlesztünk szoftvert. A fejlesztés ciklusokra van bontva. Minden ciklus egy önállóan lefejleszthető, önállóan tesztelhető részegysége a teljes implementációnak.

Ez a folyamat **3a. fázisa (0–9)**: 0-init · 1-ciklusok · 2-spec · **3a-kód-terv ←** · 3b-teszt-terv · 4-tasks · 5-analyze · 6-implement · 7-validate · 8-doc-sync · 9-merge.

---

## Cheat sheet

| Szekció | Egy mondatban |
|---|---|
| Hatókör | **Csak a kód-terv** — a teszt-szekciókat a `03b` írja (`/bs-write-test-plan`). Ide `TS-NN`, `TC-NN`, gépi futtatási tábla és tesztfájl-adatlap NEM kerül. |
| Előfeltétel | `spec.md` = `<status:ready_for_plan>`, `conventions.md` létezik, tiszta munkafa. |
| Nyitott kérdések | Minden kérdés a `plan-questions.md`-be; **kötelező első kérdés: E2E teszt stratégia**. |
| Kontextus | Spec + dokumentáció; forrásfájlokat a `researcher` subagent azonosítja (D2=A). |
| Plan struktúra | <sec:goal_and_approach>, <sec:affected_components>, <sec:environment_coords>, <sec:planned_changes>, <sec:new_dependencies>, <sec:config_build_changes>, <sec:schema_artifacts>, <sec:reverse_coverage>, <sec:risks_and_decisions>. |
| Szekció-ID | Minden végrehajtható terv-szekció címében stabil `[P-…]` azonosító (PID1) — a `tasks.md` erre hivatkozik, nem sorszámra. Kiadott ID soha nem változik. |
| Scope-kapu | Minden plan-képességhez spec-forrás (követelmény/`DoD-NN`) — `<sec:reverse_coverage>` tábla (SC1), az első oszlopban a szekció `[P-…]` azonosítójával; ami nincs, az vissza a 02-be vagy `<sec:out_of_scope>`. |
| Fázis-átadás | `plan-input-from-prev.md` beolvasva és lezárva; a nem ide tartozó infó a `tasks-`/`validate-input-from-prev.md`-be (IP1). |
| Design input | `cycle-design-input.md` (a felhasználó saját ciklus-leírása) **automatikusan beolvasva** — a technikai/eljárás-jellegű tartalma a planbe kerül; a fájlt nem írod át (CD1). |
| <sec:environment_coords> | Kötelező `<sec:environment_coords>` (KO1) szekció: komponens-URL-ek/portok, indító parancsok, példa REST hívások, teszt-/API-userek jelszóval, minden paraméter — konkrét értékkel, placeholder és üres cella nélkül. |
| **Önhordóság** | A `plan.md` **mindent** tartalmaz, ami a fejlesztéshez/teszteléshez kell — a 04 és a `test-runner` **csak ezt** olvassa, a spec-et nem. |
| Kapu-konfiguráció | Ha a ciklus olyat változtat, amit egy determinisztikus kapu a `conventions.md`-ből olvas (riport-artefaktumok/útvonal-alap, Sonar, teszt-parancsok, portok, merge-stratégia), a `conventions.md` frissítése **a ciklus része**: tervezd meg, és legyen rá task (GC1). |
| Útvonalak | Kód- és fájl-hivatkozás **a repó gyökeréhez képest relatív** (`src/app.ts:42`), dokumentum-link a fájl saját könyvtárához képest (`./spec.md`); abszolút útvonal és `file://` tilos (RP1). |
| Csonkítás-mentesség | A spec **kidolgozott** artefaktumai (OpenAPI, teljes payload, hibamátrix, többlépéses teszt-forgatókönyv) **szó szerint, hiánytalanul** kerülnek át (KX3) — az irány bővítés és pontosítás, nem összevonás. |
| Hivatkozás-feloldás | Scriptre/tesztre/API-ra hivatkozó bemenetet **fel kell oldani**: a konkrét parancs, URL, payload a plan-be kerül, nem az utalás. |
| Validációs ciklusok | Minden nagy szekció után célzott ellenőrzés, mielőtt továbblépsz. |
| Spec kritika | Aktív checklist minden komponensre; **hiányosság** → vissza a 02 fázisba, **túlnyúlás** (koordináta a spec-ben) → átemelve a planbe (KX tükre). |
| Lezárás | Minőségellenőrzés + **Lezárási kapu (TP2-code, kipipálva kiírva)** + Constitution Check (SK4) + **mechanikus kapu** (`analyze-gate-check.py --plan-code-only`, M) + user megerősítés → `<status:ready_for_test_plan>`, commit. |

---

## Feladatod

**A plan KÓD-FELÉT írod meg** — a `<sec:goal_and_approach>`-tól a `<sec:reverse_coverage>`-ig, plusz a `<sec:risks_and_decisions>`. A teszt-szekciókat (`<sec:testing_strategy>`, `<sec:plan_test_scenarios>`, `<sec:machine_run_table>`, `<sec:e2e_infrastructure>`, `<sec:regression_impact>`, `<sec:test_specification>`, `<sec:execution_order>`, `<sec:verification_strategy>`) a **következő fázis**, a `03b-write-test-plan` írja **ugyanebbe a `plan.md`-be**.

> **🔴 Ne kezdd el a teszt-szekciókat — még vázlatként sem.** Ha a spec tesztesetei „kikéredzkednek" a plan-be, az a `03b` bemenete, nem a te leszállítandód: a `<sec:reverse_coverage>` táblába felveheted a hozzájuk tartozó sort, a forgatókönyvet nem. **Miért:** a fél-kész teszt-szekció **rosszabb az üresnél** — a `03b` `TS7`-konverziója egy már meglévő, hibás szerkezetet másolna tovább, és pontosan ez a hiba szülte ezt a fázishatárt.

**Ha már létezik `plan.md` a `specs/cycle-NN-<cycle-name>/` mappában:** olvasd be, és futtasd le rajta a minőségellenőrzést (ld. lent) — **a kód-oldali szekciókra**. Ha hiányosságot vagy problémát találsz — spec-eltérés, hiányzó komponens terv, hiányos koordináta-készlet, stb. — állítsd vissza a státuszt `<status:draft>`-ra, jelezd pontosan mi a probléma, és javítsd az iterációs szabályok szerint. (Ha a plan már `<status:ready_for_test_plan>` vagy annál előrébb tart, a teszt-szekciókat **akkor sem** szerkeszted.)

**Ha még nem létezik `plan.md`:** hozd létre a `specs/cycle-NN-<cycle-name>/` mappában az alábbi struktúra szerint.

**Ne ismételd meg a spec tartalmát.** A plan célja a technikai megvalósítás megtervezése — hivatkozz a spec-re, ne másold át.
> **🔴 Hatókör — ne általánosítsd túl!** Ez a szabály (és a párja: „a `conventions.md`-re hivatkozz, ne ismételd a tool-nevet") **kizárólag az indoklásra és a viselkedés-leírásra** vonatkozik: a *miért*-re, az üzleti kontextusra, az elfogadási feltételekre. **Soha nem vonatkozik a végrehajtáshoz szükséges adatra.** A vezérelv egy mondatban:
>
> **A DÖNTÉSRE hivatkozz — a VÉGREHAJTÁST írd ki.**
>
> Példa: hogy a projekt melyik teszt-keretrendszert használja, az **döntés** → a `conventions.md`-re hivatkozol, nem ismételed. De hogy **ebben a ciklusban milyen paranccsal, milyen fájlra, milyen környezetben** fut a teszt, az **végrehajtás** → konkrétan a plan-be írod. Ha bizonytalan vagy, melyik oldalra esik valami, tedd fel a kérdést: *„a downstream fázis (04/06/07) ezt az információt máshonnan meg tudja szerezni?"* Ha nem — akkor a plan-be kell.

---

<!-- INCLUDE:shared/plan-self-contained.md -->

---

## <field:f_prerequisite>

0. **Ciklus-beazonosítás:** ha a felhasználó megadott ciklust/fájlt, azt használd; különben a legfrissebb `specs/cycle-*` mappát ajánld fel megerősítésre — <!-- INCLUDE:lang/common.md#ciklus-beazonositas --> — és várj a válaszra, mielőtt továbblépsz.

1. **`conventions.md` létezés-ellenőrzés:** olvasd be a projekt gyökerében a `conventions.md`-t. Ha nem létezik, STOP — térjenek vissza a `00` fázishoz.
2. **Munkafa-ellenőrzés (csak VCS esetén):** futtasd `git status --short`. Ha van commitálatlan változtatás, listázd, és kérdezd meg egy körben, hogy commitáljam-e vagy folytassam. (No-VCS projektben kimarad.)
3. Olvasd be a \`spec.md\` státuszát. **Ha a státusz nem \`<status:ready_for_plan>\`, ne kezdj el plan-t írni.** Jelezd a felhasználónak, hogy a spec még nem zárult le, és térjenek vissza a `02` spec fázishoz.

4. **Ciklus design input beolvasása (CD1) — automatikus:** ha létezik a `specs/cycle-NN-<cycle-name>/cycle-design-input.md`, olvasd be **minden futásban, külön felszólítás nélkül**. Ezt a felhasználó írta szabad formában a ciklusról; a 02 a viselkedési részét már a spec-be emelte, de a **technikai, eljárás- és koordináta-jellegű tartalma** (parancsok, hostok/portok, meglévő komponensek, build/deploy lépések, teljesítmény- és integrációs korlátok) **közvetlenül a plan bemenete**. A feldolgozás szabályait lásd a *„Ciklus design input feldolgozása (CD1)"* szekcióban. **Guard:** ha a fájl nem létezik vagy csak a sablon-szöveget tartalmazza, egy mondatban jelezd és folytasd — nem hiba, nem megállási ok.

_Megjegyzés: ha a spec `<status:ready_for_plan>`, a `specs/roadmap.md` implicit lezárt — a `02` spec fázis már ellenőrizte. Külön roadmap ellenőrzés nem szükséges._

---
---

## Folytatás megszakított futás után

Ha a plan fázis megszakad és új sessionban folytatódik:

```
1. Olvasd be a plan-questions.md aktuális állapotát (ha létezik).
   → Menj végig a kérdéseken sorban: [x]-eket átugorhatod, [ ]-eket
     egyenként tisztázd. Ha egy [x] áttekintésekor új kérdés merül fel,
     vedd fel a lista végére új Knn számmal.

2. Csak akkor írj/folytass kód-terv szekciókat, ha minden kérdés [x].

3. Ha a plan.md kód-fele koherensnek tűnik, de a státusz nem
   <status:ready_for_test_plan>:
   futtasd a minőségellenőrzést + Constitution Check, majd kérj megerősítést.
```

Elég a `plan.md` és a `plan-questions.md` aktuális állapota + ez a prompt az újraindításhoz.

---
---

## Nyitott kérdések kezelése

A `plan-questions.md` a plan fázis kérdés-nyilvántartója. Minden felmerülő kérdés, spec hiányosság, döntési pont és ellentmondás ide kerül — nem csak a párbeszédbe. Ez teszi a folyamatot visszakövethetővé és megszakítás után folytathatóvá.

**Alapszabály: a listából soha nem törlünk. Lezárt kérdést csak `[x]`-szel jelölünk — a szövege és a döntés megmarad.**

### plan-questions.md struktúra

Ha még nem létezik, hozd létre a `specs/cycle-NN-<cycle-name>/` mappában:

```md
<!-- INCLUDE:lang/03a-write-code-plan.md#plan-questions-struktura -->
```

Az új kérdést mindig a lista végére fűzd, a következő szekvenciális `Knn` számmal.

> **Ugyanezt a fájlt a `03b-write-test-plan` folytatja** a következő szabad `Knn` számmal. A bejegyzéseket **ne számozd újra, és ne töröld** — a `03b` a te lezárt döntéseidből dolgozik (különösen a `K01` E2E-stratégiából).

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

4. **Lezárás:** Ha minden szekció kész, minden kérdés lezárt és a minőségellenőrzés átment, tedd fel a kérdést a felhasználónak: <!-- INCLUDE:lang/03a-write-code-plan.md#statusz-megerosites --> — Ne állítsd át a státuszt a megerősítés előtt. **A válasz végén helyezd el a `plan.md` közvetlen, kattintható linkjét.**

5. **Újraindítás új kontextusban:** ha a plan fázis megszakad és új sessionban folytatódik, az első lépés a `plan-questions.md` beolvasása (ha létezik). Menj végig az összes kérdésen sorban — a `[x]`-eket átugorhatod, a `[ ]`-eket egyenként tisztázd a fentiek szerint. Ha egy már lezárt kérdés (`[x]`) áttekintésekor új kérdés merül fel, vedd fel a lista végére új `Knn` számmal, és tisztázd, mielőtt továbblépnél.

---
---

<!-- INCLUDE:shared/dereferencing.md -->

---

<!-- INCLUDE:shared/conventions-change.md -->

---

<!-- INCLUDE:shared/spec-artifact-transfer.md -->

---

## Fázisok közötti átadás (`*-input-from-prev.md`) — IP1

**Amit BEOLVASSZ:** ha létezik a `specs/cycle-NN-<cycle-name>/plan-input-from-prev.md`, olvasd be a fázis elején. Ez a 01/02 fázisban felszínre került technikai és implementációs részleteket tartalmazza (érintett komponensek, meglévő megoldások, technológiai megkötések), amelyek a spec-be nem illettek. Minden `[ ]` tételt vagy építs be a `plan.md` megfelelő szekciójába, vagy vess el explicit indokkal, és pipáld ki. **Guard:** ha a fájl nem létezik, ez nem hiba — folytasd.

**Amibe ÍRHATSZ:**
- **`tasks-input-from-prev.md`** — a **04**-nek: előkészítő lépés, sorrend-megkötés, konkrét parancs vagy környezeti előfeltétel, ami a task-bontásnál kell, de a `plan.md` szekcióiba nem illik.
- **`validate-input-from-prev.md`** — a **07**-nek: futtatási előfeltétel és üzemeltetési tudnivaló, ami csak a validálásnál válik relevánssá (pl. „a stack indítása előtt VPN kell", „a Sonar futtatás előtt a mock szervert le kell állítani, mert ütközik a porton").

<!-- INCLUDE:shared/input-from-prev.md -->

---
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
---

## Plan struktúra

<!-- INCLUDE:shared/plan-section-ids.md -->

\`\`\`md
# Cycle NN: <cím> — Plan

**<field:f_status>:** \`<status:draft>\` | \`<status:open_questions>\` | \`<status:ready_for_test_plan>\` | \`<status:ready_for_tasks>\`
**<field:f_gate_code>:** _<a kód-terv mechanikus kapujának eredménye a lezáráskor — pl. `analyze-gate-check --plan-code-only — PASS, 0 Must Fix (2026-09-01)`>_
**<field:f_gate>:** _<a teljes plan kapujának eredménye — ezt a `03b-write-test-plan` írja, te ne töltsd ki>_

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


## <sec:reverse_coverage> — scope-kapu (SC1, kötelező tábla)

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

_(A `<sec:testing_strategy>`-tól a `<sec:verification_strategy>`-ig tartó szekciókat a
`03b-write-test-plan` fázis írja — ide ne kezdd el őket.)_

## <sec:risks_and_decisions>

_Mi sülhet el rosszul? Hol van választási lehetőség, és melyiket választjuk, miért?_
\`\`\`

---

## Schema Artifaktumok kezelése

> **Figyelem — két különböző státusz-rendszer:** a `plan.md` **dokumentum-státusza** (`<status:draft>` | `<status:open_questions>` | `<status:ready_for_test_plan>`) a fájl fejlécében van. Az itteni **artifact-státusz** (`<status:draft>` | `<status:review_required>` | `<status:reviewed>`) kizárólag a `<sec:schema_artifacts>` táblázat egyes soraira vonatkozik. A kettőt ne keverd: a kód-terv akkor sem zárható `<status:ready_for_test_plan>`-re, ha bármely artifact `<status:review_required>`.

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

4. **Blokkolás**: a kód-terv nem kaphat `<status:ready_for_test_plan>` státuszt, amíg van `<status:review_required>` artifact a táblázatban.

---
---

## Validációs ciklusok

### A `<sec:planned_changes>` után

- Lefedi-e minden spec-beli követelmény valamelyik fájl módosítása? Menj végig a spec `<sec:components_behavior>` szekcióján soronként.
- Minden spec-ben említett új komponenshez (tech stacktől függetlenül) meg van-e tervezve a projekt struktúra, build rendszer és deployment mechanizmus? Nem elég a mock — ha a spec valós implementációt ír elő, annak is szerepelnie kell.
- Minden új service/komponens el tud-e érni mindent amire szüksége van (importok, config mezők, DI paraméterek)?
- Meglévő fájlok módosításainál: a standard flow érintetlen marad? (visszafelé kompatibilitás)
- Minden új tesztelhető komponenshez (service, route, app) meg van-e tervezve a DI override típusa?
- **Meglévő komponens README: NE tervezd be.** Ha a ciklus meglévő komponens konfigurációját (env var-ok, indítási paraméterek, külső kapcsolatok) változtatja meg, a `README.md` frissítése a **`08-doc-sync`** dolga — ne vedd fel a `<sec:planned_changes>` közé. **Kivétel:** ha a ciklus **új komponenst** hoz létre, annak az első `README.md`-je ide tartozik (a felépítés része).

Ha bármely pontra nem, egészítsd ki a tervezett módosításokat, majd folytasd.
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

- **A lezárási kapu (TP2-code) bármely pontja `[ ]`**: hiányzik egy környezeti koordináta (URL, port, teszt-user jelszava, indító parancs), egy `[P-…]` bejegyzésnek nincs `<field:f_purpose>` sora, egy plan-képességhez nincs spec-forrás a `<sec:reverse_coverage>` táblában, vagy a `<sec:config_lifecycle>` valamelyik cellája kitöltetlen. → **Ne zárd le a kód-tervet.** Pótold a hiányt, majd futtasd újra a kapu minden pontját. Ez nem „finomítás a 03b-ben": a `03b` a te literál értékeidből írja a `TA1` adatlapokat és a `TS-NN` hívásokat, és a belépő kapuja (D5) úgyis visszaküld ide.

Minden esetben csak **egy** kérdést tegyél fel egyszerre — várd meg a választ, pipáld ki a kérdést (`- [x] Knn → [döntés]`), majd lépj a következőre.

---

---

<!-- INCLUDE:shared/quality-check-plan-code.md -->

## Státusz kezelés

- Plan indításakor: \`<status:draft>\`
- Ha kérdés kerül a `plan-questions.md`-be: \`<status:open_questions>\`
- Ha minden kérdés `[x]`, minden **kód-oldali** szekció kitöltve, minden schema artifact `<status:reviewed>`, a minőségellenőrzés (+ Constitution Check) átment, **és a felhasználó explicit megerősítette**: \`<status:ready_for_test_plan>\`

> **🔴 A `<status:ready_for_test_plan>` NEM a ciklus plan-fázisának a vége.** A `plan.md` addig nincs kész, amíg a `03b-write-test-plan` le nem zárta `<status:ready_for_tasks>`-ra. A `04`-et ilyen státusszal indítani hiba — a `04` belépő kapuja (EG1) meg is fogja, mert a teljes `--plan-only` kapu a hiányzó teszt-szekciókra bukik.

> **Kész lifecycle:** a `plan.md` a `<status:ready_for_tasks>` után a ciklus végén — amikor a validate (07) PASS lezárja a ciklust — `<status:done>` státuszra lép. Ezt az átmenetet a 07 végzi, itt nem.


### Mechanikus kapu a lezárás előtt (M)

A `05-analyze` determinisztikus kapujának **kód-oldali fele itt is lefut** — a lezárás előtt (a `tasks.md` és a teszt-szekciók még nem léteznek, ezért `--plan-code-only`):

<!-- INCLUDE:shared/python-cmd.md -->

```bash
python3 <platform-scripts-mappa>/analyze-gate-check.py specs/cycle-NN-<cycle-name> --plan-code-only
```

**Mit fed le ebben a módban:** `[P-…]` azonosítók formátuma és egyedisége (P1), a kód-oldali kötelező plan-táblák megléte — `<sec:reverse_coverage>` és `<sec:environment_coords>` (S1) —, a `<sec:config_lifecycle>` üres cellái (C4), a `<sec:environment_coords>` placeholderei és üres cellái (C6, KO1), a `**<field:f_target_env>:**` mező megléte (EV1), minden `[P-…]` bejegyzés célja (WY1), a kapu-konfiguráció együttmozgása (GC1), a plan `path:sor` horgonyai (A2/A2b), az útvonal-formátum (R1), az artefaktum-hang kemény padlója (A3) és a `DoD-NN` azonosítók a specben (D1/D2).

> **A teszt-oldali checkek ebben a módban szándékosan NEM futnak** (`TS1–TS8`, `TA1`, `TI1`, `PH1`, `TS7`, a lefedettségi lánc és a `<sec:machine_run_table>` megléte) — azokat a `03b` lezárása méri a teljes `--plan-only` móddal. Egy kizárólag teszttel igazolt `DoD-NN` itt még **nem lehet** lefedve; ha ezeket most mérnénk, a kapu hamis FAIL-t adna.

- **`0`** → folytatható a lezárás.
- **`1`** → **nincs státuszváltás.** A `célfázis: 03` tételeket **most javítsd**, majd futtasd újra a kaput; a `célfázis: 02` tételeket a *Spec kritika* / *Megállási szabályok* szerint irányítsd vissza a 02-be — a spec-et magad nem írod.
- **`2`** → használati hiba → jelezd, ne találgass.

> **Miért itt (M):** ezek a hibák eddig a `05-analyze` első körében derültek ki, két fázissal később — ott egy fixer-subagent és egy analyzer-kör kellett hozzájuk. Itt egy szkriptfutás és egy célzott javítás.

**🔴 A kapu eredménye BIZONYÍTÉK, nem emlék (GS2/a).** A `0` után két helyre kerül a nyoma, és mindkettő kötelező:

1. a `plan.md` fejlécébe, a státusz mellé, egy sorban:

   ```md
   **<field:f_gate_code>:** analyze-gate-check --plan-code-only — PASS, 0 Must Fix (ÉÉÉÉ-HH-NN)
   ```

2. a **fázis-záró válaszodba**, szó szerint a kapu összefoglaló sora (`ANALYZE-GATE: …`).

**A bélyeget csak tényleges, `0`-t adó futás után írd be** — a következő fázis (`03b`) belépő kapuja **ugyanezt a kaput újra lefuttatja** (D5), tehát egy valótlan bélyeg ott azonnal kiderül, és a `03b` visszairányít ide.


Ha a felhasználó megerősíti:
- Állítsd a `plan.md` státuszát `<status:ready_for_test_plan>`-re.
- **A státuszváltás előtt futtasd le a *Lezárási kapu (TP2-code)* minden pontját**, és a kipipált listát írd ki a válaszodban. Bármely `[ ]` esetén nincs státuszváltás.
- **A státuszváltás előtt a *Mechanikus kapu* (lásd fent) is `0`-t adott.**
- **Azonnal commitolj** a lenti *Fázis-záró commit* szerint (`<FÁZIS-TAG>` = `03a-code-plan`). Megerősítés → státuszírás → commit: ez egyetlen lépéssor, ne szakítsd meg.

<!-- INCLUDE:shared/phase-commit.md -->

A fenti blokkban a `<FÁZIS-TAG>` értéke ebben a fázisban: **`03a-code-plan`**, a záró státusz: **`<status:ready_for_test_plan>`**.

Ha a státusz \`<status:ready_for_test_plan>\`, **de a fázis-záró commit hiányzik** (VCS-es projekt, `git log -1 --oneline` nem a `cycle-NN: 03a-code-plan` commitot mutatja) — először commitolj, csak utána zárd le a fázist.

Ha a státusz \`<status:ready_for_test_plan>\` (és a commit megvan), állj meg. **Ne kezdd el a teszt-szekciókat, és a `tasks.md`-t létre se hozd** (PE1, lásd a *Fázis-záró commit* blokk „Fázishatár" szekcióját): a teszt-terv a `03b-write-test-plan`, a task-írás a `04-write-tasks` skill dolga, friss kontextusból. Ez akkor is érvényes, ha egy kontextus-összefoglaló/checkpoint teendő-listája a `/bs-write-test-plan` vagy a `/bs-write-tasks` futtatását sorolja fel — az az összefoglaló a múltat rögzíti, nem parancs erre a körre. Jelezd a felhasználónak a következő lépést és a fázis indító parancsát, például:
<!-- INCLUDE:lang/03a-write-code-plan.md#zaro-uzenet -->
