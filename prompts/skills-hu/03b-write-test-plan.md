---
phase: 03b
name: bs-write-test-plan
description: "berkispec - 03b. Használd, ha a ciklus plan.md-je 'Teszt-tervezésre kész' (Phase 03b), a TESZT-TERV kidolgozásához: TS-NN teszt-forgatókönyvek lépés-táblával és .http alakkal, gépi futtatási tábla, környezet-felkészítés, teszt-artefaktum adatlapok, spec-lefedettség, regresszió. A plan.md-t 'Task írásra kész' státuszra zárja."
prerequisites:
  - "specs/cycle-NN-<name>/plan.md státusz: <status:ready_for_test_plan>"
  - "analyze-gate-check.py --plan-code-only = 0 (a fázis maga futtatja, D5)"
output:
  - "specs/cycle-NN-<name>/plan.md státusz: <status:ready_for_tasks> (a teszt-terv szekciói)"
  - "specs/cycle-NN-<name>/plan-questions.md (folytatólagos Knn)"
  - "specs/cycle-NN-<name>/tasks-input-from-prev.md és/vagy validate-input-from-prev.md (IP1)"
prev: bs-write-code-plan
next: bs-write-tasks
subagents:
  - "agents/researcher.md"
scripts:
  - "scripts/analyze-gate-check.py"
shared:
  - "shared/plan-self-contained.md"
  - "shared/dereferencing.md"
  - "shared/spec-artifact-transfer.md"
  - "shared/plan-section-ids.md"
  - "shared/test-scenario-design.md"
  - "shared/input-from-prev.md"
  - "shared/artifact-voice.md"
  - "shared/phase-commit.md"
  - "shared/quality-check-plan-test.md"
---
# 03b — Teszt-terv írás
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

Spec driven development-ben fejlesztünk szoftvert. A fejlesztés ciklusokra van bontva. Minden ciklus egy önállóan lefejleszthető, önállóan tesztelhető részegysége a teljes implementációnak.

Ez a folyamat **3b. fázisa (0–9)**: 0-init · 1-ciklusok · 2-spec · 3a-kód-terv · **3b-teszt-terv ←** · 4-tasks · 5-analyze · 6-implement · 7-validate · 8-doc-sync · 9-merge.

---

## Cheat sheet

| Szekció | Egy mondatban |
|---|---|
| Előfeltétel | `plan.md` = `<status:ready_for_test_plan>`, és az `analyze-gate-check.py --plan-code-only` **általad lefuttatva** `0`-t adott (D5). |
| Hatókör | **Csak a teszt-terv.** A kód-felet nem írod át — pontosan három bővítés megengedett: új `<sec:reverse_coverage>` sor, teszt-artefaktumra szóló új `[P-…]` bejegyzés, és teszt-oldali kockázat a `<sec:risks_and_decisions>`-ben. |
| Bemenet | A `plan.md` **kód-fele** (koordináták, tervezett módosítások, konfiguráció, séma) + a spec **teszt-szekciója és `DoD`-ja** + a `test-conventions.md` 2./3. szekciója. |
| Teszt-forgatókönyvek | `TS-NN` blokk minden spec-tesztesethez (TS1–TS8): lépés-tábla igével, teljes végponttal, fejlécekkel, konkrét bodyval, ellenőrizhető elvárt eredménnyel — REST-nél `.http` alakban is. |
| Generáló recept | `TD0–TD7` (`test-scenario-design.md`) — **ez a fázis motorja**: dimenzió-leltár, megfigyelési négyes, megszámolhatóság, izoláció, kalibráció, önteszt. |
| Gépi futtatási tábla | Kötelező `<sec:machine_run_table>` (TP4): kategória, típus, előfeltétel, parancs, eredményfájl, formátum, takarítás, környezet, **fázis** (PH1). |
| Cél-környezet | A nem-lokális kategória parancsa **literálisan** tartalmazza a cél-hostot, az előfeltétel ugyanoda hív probe-bal, `localhost` tilos (EV2–EV5). |
| Teszt-azonosítók | `TS-NN` + `TC-NN` **közös, ciklus-szinten folytonos** névtér (TI1) — a `tasks.md` és a 07 naplója erre hivatkozik. |
| Tesztfájl-adatlap | Minden `#### <tesztfájl path>` alatt kötelező a `TA1` adatlap: mit ellenőriz · futtatás · fixture-ök · teszt-esetek. |
| Spec-lefedettség | A `<sec:spec_coverage>` tábla **minden sora megnevez legalább egy `TS-NN`-t** (TS7) — a spec teszteseteit konvertálni kell, nem prózaként átmásolni. |
| Környezet-felkészítés | A teszt előfeltételei (token-beszerzés, stack-indítás + health check, egyedi komponens build/deploy/rollback, seed) **szó szerinti parancsként** a plan-ben (TP3); ami korábbi ciklusban épült ki és nincs a regiszterben, azt onnan hozod át (TP3/a). |
| Teszt-receptek | A `specs/test-conventions.md`-ből **maradéktalanul, önhordóan** átemelve (TC1/a) — hivatkozás nem elég, a receptet **fizikailag be kell másolni**. |
| Regresszió | A `<sec:regression_impact>` tábla kitöltve, vagy explicit „nincs". |
| **Önhordóság** | A `plan.md` **mindent** tartalmaz, ami a teszteléshez kell — a `test-runner` **csak ezt** olvassa, sem a spec-et, sem a `test-conventions.md`-t. |
| Validációs ciklusok | Minden nagy szekció után célzott ellenőrzés, mielőtt továbblépsz. |
| Spec kritika | A spec **teszt-szekciójára** és `DoD`-jára szűkítve: hiányzó/ellentmondó teszteset → vissza a 02-be; a spec-ben maradt teszt-koordináta → beemelve. |
| Lezárás | Minőségellenőrzés + **Lezárási kapu (TP2-test, kipipálva kiírva)** + **mechanikus kapu** (`analyze-gate-check.py --plan-only`, M) + user megerősítés → `<status:ready_for_tasks>`, commit. |

---

## Feladatod

**A plan TESZT-FELÉT írod meg**, ugyanabba a `specs/cycle-NN-<cycle-name>/plan.md` fájlba, amelynek a kód-felét a `03a-write-code-plan` már lezárta. A leszállítandód:

- `<sec:testing_strategy>` — milyen típusú tesztek kellenek, mit mockolunk;
- `<sec:plan_test_scenarios>` — a `TS-NN` forgatókönyvek lépés-táblával és `.http` alakkal (**a fázis fő leszállítandója**);
- `<sec:machine_run_table>` — a `run-tests.py` gépi futtatási táblája;
- `<sec:e2e_infrastructure>` — a környezet-felkészítés (TP3), a lezárt `K01` döntésére építve;
- `<sec:regression_impact>` — a regressziós érintettség;
- `<sec:test_specification>` — teszt-azonosítók (TI1), `<sec:spec_coverage>`, Lifecycle, `TA1` adatlapok, unit/integrációs/E2E táblák;
- `<sec:execution_order>` és `<sec:verification_strategy>` — mindkét fél ismeretében rendezve.

**Amit NEM írsz:** a kód-fél szekcióit (`<sec:goal_and_approach>`, `<sec:affected_components>`, `<sec:environment_coords>`, `<sec:planned_changes>`, `<sec:new_dependencies>`, `<sec:config_build_changes>`, `<sec:schema_artifacts>`). Ezekből **literál értékeket másolsz** a teszt-szekcióidba — nem hivatkozol rájuk, és nem szerkeszted őket.

> **A három megengedett bővítés a kód-félbe — más nincs:**
> 1. **`<sec:reverse_coverage>`:** **új sort** adhatsz a saját teszt-szekcióidhoz (a `PID1` szerint a teszt-szekciók is `[P-…]` ID-t viselnek). Meglévő sort nem módosítasz és nem törölsz; ha egy meglévő sort hibásnak találsz, az `Knn` kérdés vagy visszairányítás a `03a`-ra.
> 2. **`<sec:planned_changes>`:** **új `[P-…]` bejegyzést** vehetsz fel, **kizárólag teszt-artefaktumra** (tesztfájl, fixture, mock, seed-adat, teszt-helper) — a kötelező `**<field:f_purpose>:**` sorral. A `TA1` adatlap megköveteli minden fixture útvonalát, és ami még nem létezik, az **új fájl**. Termelő (nem-teszt) kódra **soha**: az visszairányítás a `03a`-ra. Meglévő `[P-…]` bejegyzést nem szerkesztesz.
> 3. **`<sec:risks_and_decisions>`:** **új bekezdést** írhatsz teszt-oldali kockázatról (flaky forgatókönyv, osztott környezet, hosszú futás). Meglévő bekezdést nem írsz át.

**🔴 A `TS7` konverzió a fázis lényege.** A spec tesztesetei **nem prózaként másolódnak** a planbe, hanem `TS-NN` blokká **konvertálódnak**. A spec saját címsor-szerkezetét (`Teszteset N`, „REST szekvencia", „Verifikáció") **nem nyitod meg** a planben: ami nincs `TS-NN` blokkban, azt a kapu nem látja, a `test-runner` nem futtatja és a kézi tesztterv nem szereli össze.

**🔴 A `TD0–TD7` recept kitöltendő kérdéssor, nem olvasmány.** A dimenzió-leltár **szorzata** dönti el, **hány** forgatókönyv kell — nem az, hogy hány teszteset fért bele a specbe. A recept a `test-scenario-design.md` blokkban van, lent.

**Ha már létezik teszt-terv a `plan.md`-ben** (a státusz `<status:ready_for_tasks>`): olvasd be, és futtasd le rajta a minőségellenőrzést. Ha hiányosságot találsz, javítsd az iterációs szabályok szerint — ne kezdd újra.

---

<!-- INCLUDE:shared/plan-self-contained.md -->

---

## <field:f_prerequisite>

0. **Ciklus-beazonosítás:** ha a felhasználó megadott ciklust/fájlt, azt használd; különben a legfrissebb `specs/cycle-*` mappát ajánld fel megerősítésre — <!-- INCLUDE:lang/common.md#ciklus-beazonositas --> — és várj a válaszra, mielőtt továbblépsz.

1. **`conventions.md` létezés-ellenőrzés:** olvasd be a projekt gyökerében a `conventions.md`-t. Ha nem létezik, STOP — térjenek vissza a `00` fázishoz.
2. **Munkafa-ellenőrzés (csak VCS esetén):** futtasd `git status --short`. Ha van commitálatlan változtatás, listázd, és kérdezd meg egy körben, hogy commitáljam-e vagy folytassam. (No-VCS projektben kimarad.)
3. **Olvasd be a `plan.md` státuszát.** Ha nem `<status:ready_for_test_plan>`:
   - `<status:draft>` vagy `<status:open_questions>` → **a kód-terv nem zárult le.** STOP, és irányítsd vissza a felhasználót a `/bs-write-code-plan`-ra.
   - már `<status:ready_for_tasks>` → **a teszt-terv készen van.** Ne kezdd újra: futtasd le a minőségellenőrzést, és ha hiányt találsz, a *Feladatod* szekció szerint javíts.

4. **🔴 A státusz-mező ÖNBEVALLÁS — futtasd le a kód-terv kapuját (D5).** A `<status:ready_for_test_plan>` státuszt a `03a` írta be **magának**; a te bemeneted minősége nem az ő állításán múlik. Futtasd le:

<!-- INCLUDE:shared/python-cmd.md -->

   ```bash
   python3 <platform-scripts-mappa>/analyze-gate-check.py specs/cycle-NN-<cycle-name> --plan-code-only
   ```

   - **`0`** → a kód-terv rendben, folytathatod.
   - **`1`** → **STOP.** Sorold fel a `## <status:must_fix>` tételeket, és irányítsd vissza a felhasználót a `/bs-write-code-plan`-ra: *„A kód-terv kapuja N blokkoló megállapítást adott (…) — a teszt-terv előtt ezeket a `03a`-ban kell rendezni."* **A kód-tervet NEM javítod** — különben egy hiányos koordináta-készletre épülő teszt-terv betonozódik be, és a hiba csak a `07`-ben derül ki, plan-hiányként.
   - **`2`** → használati hiba → jelezd, ne találgass.

   **Miért te futtatod (a `7/j` elve):** a lezáró fázisnak nincs érdeke megbukni a saját kapuján — **a fogadónak viszont van**, mert a hiányos bemenetből ő ír rossz tervet. A bélyeg (`**<field:f_gate_code>:**` sor) **állítás**, ez a futás a **bizonyíték**.

5. **Nyitott kérdések:** a `plan-questions.md`-ben nincs `[ ]` státuszú kérdés. Ha van, a kód-terv valójában nem zárult le — tisztázd, mielőtt teszt-szekciót írnál (a `K01` E2E-döntés különösen: a `<sec:e2e_infrastructure>` szekció erre épül).

---

## Folytatás megszakított futás után

Ha a teszt-terv fázis megszakad és új sessionban folytatódik:

```
1. Olvasd be a plan.md teszt-szekcióit és a plan-questions.md állapotát.
   → Melyik TS-NN blokk van már meg, melyik DoD-NN-hez nincs még
     forgatókönyv, kitöltött-e a gépi futtatási tábla, van-e TA1
     adatlap minden tesztfájlnál?

2. Csak akkor írj/folytass teszt-szekciókat, ha minden kérdés [x].

3. Ha a teszt-terv koherensnek tűnik, de a státusz nem
   <status:ready_for_tasks>: futtasd a minőségellenőrzést + a
   mechanikus kaput, majd kérj megerősítést.
```

Elég a `plan.md`, a `plan-questions.md` aktuális állapota + ez a prompt az újraindításhoz.

---

## Nyitott kérdések kezelése

A `plan-questions.md` a plan fázis (03a **és** 03b) **közös** kérdés-nyilvántartója. A `03a` hozta létre; te **folytatod**.

**Alapszabály: a listából soha nem törlünk, és nem számozunk újra.** A `03a` lezárt bejegyzéseit (`[x]`) érintetlenül hagyod — a `K01` E2E-döntés a te `<sec:e2e_infrastructure>` szekciód alapja. Az új kérdést a lista végére fűzöd, a **következő szabad** `Knn` számmal.

**Ha a `K01` döntése a teszt-tervezés közben tarthatatlannak bizonyul** (pl. a választott mock-szint nem tudja igazolni a `DoD-03`-at), **ne írd át a lezárt bejegyzést**: vegyél fel új `Knn`-t, amely hivatkozik rá, és tedd fel a felhasználónak.

**Munkafolyamat:** kérdésenként haladj — egyszerre csak egyet tegyél fel. Ha megérkezett a válasz: jelöld `[x]`-szel, és írj mellé egy soros összefoglalót (`→ ...`). Ha a válaszból új kérdés merül fel, azonnal vedd fel a lista végére. **Minden alkalommal, amikor kérdést teszel fel vagy jóváhagyást kérsz, a válaszod végén helyezz el egy közvetlen, kattintható markdown linket az érintett fájlra.**

**Lezárás:** ha minden teszt-szekció kész, minden kérdés lezárt és a minőségellenőrzés átment, tedd fel a kérdést a felhasználónak: <!-- INCLUDE:lang/03b-write-test-plan.md#statusz-megerosites --> — Ne állítsd át a státuszt a megerősítés előtt. **A válasz végén helyezd el a `plan.md` közvetlen, kattintható linkjét.**

---

<!-- INCLUDE:shared/dereferencing.md -->

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

## Kontextus betöltési szabályok

> **A fő bemeneted a `plan.md` kód-fele** — nem a spec, és nem a kódbázis. A `03a` már felderítette a koordinátákat és az érintett forrásfájlokat; a te dolgod ezekből **literál értékekkel** teszt-forgatókönyvet építeni.

- **`plan.md` — kötelező, teljes egészében a kód-fél:** `<sec:goal_and_approach>`, `<sec:affected_components>`, `<sec:environment_coords>` (URL-ek, portok, teszt-userek jelszóval, példa hívások), `<sec:planned_changes>` (`[P-…]` ID-k, célok), `<sec:config_lifecycle>`, `<sec:schema_artifacts>`, `<sec:reverse_coverage>`.
- **`spec.md` — a `<sec:test_specification>` szekció és a `<sec:definition_of_done>`.** Ez a `TS7` konverzió forrása. A spec többi részét (célkitűzés, komponens-viselkedés, követelmények) **nem kell** újraolvasnod — amit a tervezéshez tudni kell belőle, az a plan kód-felében már benne van.
- **`conventions.md`:** a teszt-eszközök (`<sec:cv_test_framework>`, `<sec:cv_test_structure>`) és a **riport-artefaktumok** (`<sec:cv_test_reporting>`) — a gépi futtatási tábla eredményfájl-oszlopa ebből él.
- **`plan-questions.md`:** a lezárt döntések, különösen a `K01` E2E-stratégia.

> **Melyik regiszter mit tud (TC1/c):** a **riport-artefaktumok, az útvonal-alapjuk és a riport-generáló parancsok** a projekt `conventions.md` `## <sec:cv_test_reporting>` szekciójában élnek — **azt olvassa a 07 TR3 kapuja**. A `specs/test-conventions.md` a **receptek és koordináták** regisztere. Ha a ciklus a riport-struktúrát vagy a riport-parancsot változtatja, a `conventions.md`-t kell átvezetni (GC1) — a `test-conventions.md` frissítése nem helyettesíti. **A `conventions.md` módosítása a kód-terv dolga** (`03a`): ha ilyenre van szükség, az `Knn` kérdés vagy visszairányítás.

- **`specs/test-conventions.md` — a 2. és a 3. szekció** (minden körben szükséges lokális, ill. integrációs/E2E tételek), **és** az 1. szekció azon receptjei, amelyek a bootstrappinghez kellenek. **Guard:** ha a fájl nem létezik (korai ciklus), ne állj meg és ne hozd létre — egy mondatban jelezd, és a meglévő tesztelési infrastruktúrából dolgozz.

  > **🔴 A `plan.md` ÖNHORDÓ (TC1/a — kötelező).** A `run-tests.py` szkript a `plan.md` **gépi futtatási tábláját** olvassa, a `test-runner` subagent (fallback) pedig a `test-conventions.md`-t **nem olvassa** — kizárólag a `plan.md` `<sec:testing_strategy>` és `<sec:regression_impact>` szekcióit. Ezért **minden tesztelési feladatot maradéktalanul át kell emelni a `plan.md`-be**, kiegészítve a 0. blokk és az 1. szekció **összes** hozzá tartozó adatával: teszt-userek és jelszavaik, URL-ek, portok, namespace/pod, image-név, registry-cél, paraméterek, **példa hívások (`curl`)**, build/push/restart parancsok, előfeltételek és futási sorrend.
  > - **Puszta hivatkozás NEM elég** (`„lásd test-conventions.md R03"` önmagában tilos) — a `test-conventions.md`-re csak **provenance**-ként hivatkozz a beemelt tartalom mellett (pl. „_(forrás: test-conventions.md R03)_").
  > - **Placeholder TILOS** (`<ide jön a jelszó>`, `<TODO URL>`) — ha egy adat hiányzik vagy elavult, az `plan-questions.md` kérdés, nem placeholder.
  > - **Nem automatikus futtatás:** a regiszterből **csak az** kerül át, ami ebben a ciklusban tényleg szükséges.
  > - **Elavult tétel:** ha egy recept adata nem stimmel a valósággal, vagy az `<field:f_last_run>` markere régi, **kérdezz rá** a `plan-questions.md`-ben. A `test-conventions.md`-t **ne írd** — a javítás a `08-doc-sync` dolga (TC4).
  > - **`<status:scope_shared_remote>` hatókörű recept** (a regiszter így jelöli): a beemelés előtt **kötelezően kérdezz rá** a `plan-questions.md`-ben — osztott dev/test környezetben egy image-push vagy pod-restart más munkáját is érinti.

- **🔴 NEM indítasz `researcher`-t forrásfájl-azonosításra.** Azt a `03a` elvégezte, és az eredménye a `<sec:planned_changes>`-ban van. Ez a fázis kontextus-fegyelme: a kódbázis újra-feltárása itt duplikált munka, és a teszt-terv a plan-ből épül, nem a kódból.
- **`researcher` Mód B — csak egy célra:** ha egy **meglévő tesztfájl tényleges hívásláncát** kell literálisan kinyerni (fixture, seed, helper, elvárt válasz), indíthatod — **literál értékeket kérve**, a *Hivatkozás-feloldás* szabálya szerint.
- **Korábbi ciklusok `plan.md`-jei — csak a TP3/a kivétellel:** ha a teszt futtatásához olyan környezeti előfeltétel kell, amit egy korábbi ciklus épített ki (egyedi plugin/SPI, mock szerver, seed-adat, konténer-stack, teszt-user, token-beszerző helper), **és a parancsai nincsenek a `specs/test-conventions.md`-ben**, azokat a `researcher` Mód B-vel, **szó szerint** hozod át, `_(forrás: cycle-NN plan.md)_` provenance-szal. Csak a végrehajtáshoz szükséges receptet — nem a korábbi ciklus tervét.

---

<!-- INCLUDE:shared/artifact-voice.md -->

---

## Plan struktúra — a teszt-fél

<!-- INCLUDE:shared/plan-section-ids.md -->

> **A `<sec:goal_and_approach>`-tól a `<sec:reverse_coverage>`-ig a szekciókat a `03a-write-code-plan` már megírta** — a fejlécet és a státusz-mezőt te lépteted, a tartalmukat nem szerkeszted (a három megengedett bővítést lásd a *Feladatod* szekcióban). A saját szekcióidat **a `<sec:risks_and_decisions>` ELÉ** írod: a `plan.md` szekcióinak fizikai sorrendje változatlan marad.

\`\`\`md
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

#### TS-01 [remote] — <a forgatókönyv neve>  (DoD-02, DoD-05)

**<field:f_what_we_test>:** <mit ellenőriz ez a forgatókönyv — a viselkedés, amiért fut, egy mondatban>
**<field:f_prerequisite>:** <milyen állapotból indul: felhúzott stack, seed, bejelentkezett user, korábbi `TS-NN` eredménye>

| # | Lépés | Hívás | Elvárt eredmény |
|---|---|---|---|
| 1 | <mit csinálunk> | `<szó szerint futtatható hívás>` | `<konkrét, ellenőrizhető válasz>` |

**<field:f_cleanup>:** <mit kell utána leállítani vagy visszaállítani>

**Kitöltési szabályok:**
- **🔴 Hatókör-címke a fejlécben — kötelező, és NYELVFÜGGETLEN: `[local]` vagy `[remote]` (EV8).** `remote` minden olyan forgatókönyv, amely akár EGYETLEN olyan komponenst is megszólít, ami nem a lokális gépen fut — a saját gépen futó konténer még `local`. **A cím önmagában nem dönt:** egy `oc port-forward` mögötti `127.0.0.1:8080` **remote** (a komponens a klaszterben fut), egy compose service-név (`http://keycloak:8080`) pedig **local**. A címke szabja meg, **hova kerülnek a forgatókönyv REST-naplói a kör-mappában** (`…/rest-logs/<local|remote>/<teszt-név>/`), és a `07` kapuja (`RL1`/`RL2`) ebből joinol — ezért nem projekt-nyelvi `status`-token, hanem angol literál: a mappanevek a keretben mindig angolul állnak. A teszt-**függvény** a `<field:f_test_cases>` adatlap-soron át örökli a forgatókönyv címkéjét, tehát nem kell kétszer leírni; vegyes hatókörű tesztfájlnál a függvény szintjén felülírható (`` `test_foo` → `TC-01` [remote] ``). A **`TC-NN` unit-esetek NEM kapnak címkét** (definíció szerint izoláltak, tehát `local`) — **címke nélküli teszt alapértéke `local`**.
- **`<field:f_what_we_test>` — állítás, nem téma (TD7).** Ez a sor mondja meg, **mit ellenőriz** a forgatókönyv és **miért**: a viselkedés egy eldönthető állításként (*„öt egyidejű kérésből pontosan egy újítja meg a tokent, a többi a meglévővel szolgál ki"*), plusz az elfogadási feltétel vagy kockázat, amit igazol. **A fejléc megismétlése nem elég** („konkurencia-teszt", „az `/init-hash` tesztelése") — abból a 06/07 fázisban nem derül ki, hogy egy bukás valódi hiba-e vagy rossz teszt. A kapu ezt méri (TS2).
- **`DoD-NN` a fejlécben — kötelező és kétirányú (TS5).** Minden forgatókönyv megnevezi, mely DoD-pontokat igazolja, és **minden `DoD-NN`-hez tartoznia kell legalább egy forgatókönyvnek**. A kapu mindkét irányt méri.
- **Hívás oszlop — szó szerint futtatható.** REST-nél teljes `curl`: ige, teljes URL porttal, fejlécek, konkrét request body. Nem REST teszt is ide tartozik ugyanebben a formában: UI-lépés (mire kattintunk, mit írunk be), CLI-parancs, DB-lekérdezés. **Hivatkozás nem hívás** — „lásd a `<sec:e2e_infrastructure>` szekciót" nem futtatható.
- **Elvárt eredmény oszlop — konkrét és ellenőrizhető.** Státuszkód **és** a válasz azonosítható része (mezőnév, érték, payload-részlet, UI-elem szövege). A „sikeresen lefut" / „hibát ad" / „a várt eredményt adja" **tilos**: nem eldönthető. A kapu kemény padlója (TS3): legalább egy backtickes érték vagy szám.
- **Teszt-userek, jelszavak, URL-ek, portok, azonosítók: literálisan.** A `<sec:environment_coords>` (KO1) értékeit **ide be kell írni**, nem hivatkozni rájuk — placeholder tilos (TS4), a hiányzó adat `plan-questions.md` kérdés. Credential-t a titok-szabály (TC5) szerint: dev-hatókörű teszt-user igen, klaszter/registry/IAM credential soha.
- **Az adatfolyam legyen követhető.** Ha egy lépés kimenetét a következő használja, írd ki, **melyik mezőt melyik változóba** (`a válasz `response.initHash` mezője → `$INIT_HASH``).
- **Számozás:** `TS-01`-től, hézagmentesen és egyediül (TS6). Javításnál a meglévő azonosítókat **ne számozd újra** — az újak a lista végére kerülnek.
- **🔴 REST-hívásnál a `.http` blokk is kötelező (TS8).** A lépés-tábla `Hívás` cellája a **gépnek** szól (egysoros, futtatható `curl`/parancs) — egy embernek viszont a fejlécekkel és a body-val együtt kell látnia a kérést, kattintható alakban. Ezért minden olyan `TS-NN` blokk végén, amelynek van REST-lépése, áll egy ```http infostringes kódblokk (VSCode REST Client / IntelliJ `.http` alak) **ugyanazokkal az értékekkel**, a lépés számára hivatkozva:

```http
@tmp = https://tmp.remote.example.com
@legacy = https://legacy.remote.example.com

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
| e2e | nehéz | `<a cél elérhetőségi probe-ja; stack indítása>` | `<parancs a cél-hosttal>` | `<fájl>` | junit | `<lebontás>` | `<remote — a cél-környezet neve>` | <status:phase_validate> |

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
- **🔴 <field:f_environment> — kötelező minden sorban (EV2–EV5).** Ide `lokális` vagy `remote` kerül — **`remote` minden olyan futás, amely akár EGYETLEN olyan komponenst is hív, ami nem a lokális gépen fut** (a saját gépen futó konténer még `lokális`). Ha nem `lokális`:
  - a **`Parancs` cellának literálisan tartalmaznia kell a cél-hostot** (env-változóval vagy kapcsolóval, pl. `PLAYWRIGHT_BASE_URL=https://app.remote.example npx playwright test`) — **a célpont nem rejtőzhet konfigfájlban** (EV3). Egy `test:playwright:remote-e2e` nevű script configjában simán állhat `localhost`: **a parancs neve nem bizonyíték, a cím az**;
  - az **`Előfeltétel` cellába kötelező egy elérhetőségi probe** ugyanarra a hostra (`curl -fsS https://app.remote.example/health`) — a `run-tests.py` az előfeltételt futtatja, és bukásakor a kategória FAIL, tehát **egy le sem futó deploy nem tud zöldre pipálódni** (EV4);
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

\`\`\`

---

## Validációs ciklusok

### 1. A `<sec:test_specification>` után

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
### 2. A `<sec:execution_order>` után

- Van-e körkörös függőség? (A → B → A)
- Minden RED lépés (tesztírás) megelőzi-e a megfelelő GREEN lépést (implementáció)?
- Minden blokkoló függőség explicit jelölve van? (pl. "RSA kulcsgenerálás előtt semmi más nem futhat")

Ha körkörös függőséget találsz: próbáld meg feloldani az egyik lépés kibontásával (pl. interfész előbb, implementáció később). **Ha a körkörös függőség nem oldható fel önállóan — állj meg, és kérd a felhasználó segítségét.** Egy kérdés, válasz, folytatás — ugyanaz a szabály, mint a többi megállási esetnél.

Ha a körfüggőségen kívüli pontra nem teljesül a feltétel, rendezd át a sorrendet.

---

## Spec kritika — a teszt-oldalon

A teszt-terv az a pont, ahol a spec **tesztelhetősége** kiderül. Menj végig a spec `<sec:test_specification>` szekcióján és a `<sec:definition_of_done>` pontjain, és mindegyikre válaszolj:

1. **Hiányzik-e teszteset?** Van olyan `DoD-NN`, amelyhez a spec nem ad tesztesetet, vagy amelyhez nem tudsz ellenőrizhető forgatókönyvet írni?
2. **Ellentmond-e két teszteset egymásnak,** vagy a spec teszt-szekciója a `DoD`-nak?
3. **Eldönthető-e az elvárt eredmény?** Ha egy teszteset elvárása „sikeresen lefut" jellegű, az nem elfogadható padló (TS3) — konkrét, megfigyelhető értéket kell kimondani.

Ha hiányosságot vagy ellentmondást találsz, **ne döntsd el magad** — irányítsd vissza a spec fázisba (`02`), és jelezd pontosan, mi hiányzik. **A `spec.md`-t nem írod.**

### A spec-ben maradt teszt-koordináta (a KX tükre)

Ha a spec konkrét teszt-koordinátát hordoz (tesztfájl-útvonal, teszt-eszköz neve, mock-szint döntés, `localhost:NNNN`, példa `curl`), az **a te előnyöd, nem probléma**: emeld be a teszt-szekciódba literálisan, `_(forrás: spec.md)_` provenance-szal, és jelezd a felhasználónak egy sorban, mi maradt a spec-ben. **Ne kérdezz rá** csak azért, mert rossz helyen volt.

> **A határ:** ami a **kód-tervbe** tartozó koordináta (komponens-URL, indító parancs, konfiguráció), az **nem** a te dolgod — az a `<sec:environment_coords>`, és ha hiányzik onnan, az `Knn` kérdés vagy visszairányítás a `/bs-write-code-plan`-ra. **A `<sec:planned_changes>`-t nem írod át.**

---

## Megállási szabályok

**Minden felmerülő kérdést — bármilyen okból — azonnal vedd fel a `plan-questions.md`-be a következő szabad számmal (`Knn`) `- [ ]` státusszal, mielőtt feltennéd a felhasználónak.**

Ha teszt-terv írása közben az alábbiak bármelyike teljesül, **STOP — állj meg és jelezd a felhasználónak** (ne döntsd el magad a hiányzó/ellentmondó részt):

- **🔴 Hiányzik a kód-tervből valami, ami a teszt megtervezéséhez kell**: koordináta (URL, port, teszt-user jelszava), szó szerinti parancs, vagy egy termelő-kód-változás, ami nélkül a forgatókönyv nem írható meg. → `Knn` kérdés **vagy** visszairányítás a `/bs-write-code-plan`-ra. **A kód-tervet magad nem írod át** (a három megengedett bővítésen kívül).

- **Teszt-stratégiai döntési pont**: több egyenrangú megközelítés létezik (mock-szint, izolációs stratégia, teszt-adat előállítása), és a választás nem egyértelmű a lezárt `K01`-ből. → Tegyél fel **egy** kérdést, várj a válaszra, majd folytasd.

- **Spec hiányosság**: a spec nem definiál egy szükséges viselkedést, hibalesetet vagy elvárt eredményt, amit tesztelni kellene. → **Ne töltsd ki magad.** Vedd fel `Knn` kérdésként, és jelezd, hogy a `02` fázisba kell visszatérni.

- **Spec ellentmondás**: a spec két tesztesete vagy a spec és a `DoD` egymásnak ellentmond. → Jelezd mindkét oldalt, és várd meg a felhasználó döntését. Ne válassz.

- **Komplex vagy bizonytalan konténerizáció**: a tesztkörnyezet bármely komponensének konténeres futtatása, konfigurálása vagy hálózati összekötése nem triviális. → Ne találgass portot/konfigurációt; vedd fel a kérdést, állj meg, és kezdeményezz közös tervezést.

- **A lezárási kapu (TP2-test) bármely pontja `[ ]`**: a spec valamelyik tesztesete/DoD-pontja nem képződött le `TS-NN` forgatókönyvre, egy `test-conventions` recept csak hivatkozásként szerepel, egy integrációs/E2E lépés nincs kifejtve, hiányzik egy tesztfájl-adatlap (TA1), vagy hiányzik egy környezet-felkészítési előfeltétel (TP3). → **Ne zárd le a plant.** Pótold a hiányt, majd futtasd újra a kapu minden pontját. Ez nem „finomítás a 04-ben": a `test-runner` csak a `plan.md`-t látja.

Minden esetben csak **egy** kérdést tegyél fel egyszerre — várd meg a választ, pipáld ki a kérdést (`- [x] Knn → [döntés]`), majd lépj a következőre.

---

<!-- INCLUDE:shared/quality-check-plan-test.md -->

## Státusz kezelés

- A fázis indulásakor a `plan.md` státusza `<status:ready_for_test_plan>` (ezt a `03a` írta).
- Ha új kérdés kerül a `plan-questions.md`-be: `<status:open_questions>` — a lezárása után visszaáll `<status:ready_for_test_plan>`-re.
- Ha minden kérdés `[x]`, minden teszt-szekció kitöltve, a minőségellenőrzés átment, **és a felhasználó explicit megerősítette**: \`<status:ready_for_tasks>\`

> **Kész lifecycle:** a `plan.md` a `<status:ready_for_tasks>` után a ciklus végén — amikor a validate (07) PASS lezárja a ciklust — `<status:done>` státuszra lép. A 08 fázis már `<status:done>`-t vár. Ezt az átmenetet a 07 végzi, itt nem.


### Mechanikus kapu a lezárás előtt (M)

A `05-analyze` determinisztikus kapujának **plan-oldali fele itt is lefut** — a lezárás előtt, a **teljes** plan-re (a `tasks.md` még nem létezik, ezért `--plan-only`):

<!-- INCLUDE:shared/python-cmd.md -->

```bash
python3 <platform-scripts-mappa>/analyze-gate-check.py specs/cycle-NN-<cycle-name> --plan-only
```

**Mit fed le ebben a módban:** `[P-…]` azonosítók formátuma és egyedisége (P1), a kötelező plan-táblák megléte (S1), a `<sec:reverse_coverage>` sorainak `[P-…]` azonosítója (S3), minden `DoD-NN` visszavezethetősége plan-képességre (C1), a `<sec:spec_coverage>` TP1-teljessége (C3), a `<sec:config_lifecycle>` üres cellái (C4), a `<sec:environment_coords>` placeholderei és üres cellái (C6, KO1), a teszt-forgatókönyvek tartalmi padlója (TS1–TS8), a tesztfájl-adatlapok (TA1), a teszt-azonosítók névtere (TI1), a futtatási fázis (PH1), a spec-lefedettség `TS-NN` hivatkozásai (TS7), a plan `path:sor` horgonyai (A2/A2b), az artefaktum-hang kemény padlója (A3) és a `DoD-NN` azonosítók a specben (D1/D2). **Ez a teljes plan kapuja** — a kód-fél checkjeit is újra méri. A task-oldal a `04` lezárásakor fut.

- **`0`** → folytatható a lezárás.
- **`1`** → **nincs státuszváltás.** A `célfázis: 03` tételeket **most javítsd** — de **csak a teszt-oldaliakat**. Ha a megállapítás a kód-félre esik (koordináta, `[P-…]` cél, konfiguráció), az `Knn` kérdés vagy visszairányítás a `/bs-write-code-plan`-ra. A `célfázis: 02` tételeket a *Spec kritika* szerint irányítsd vissza a 02-be — a spec-et magad nem írod.
- **`2`** → használati hiba → jelezd, ne találgass.

> **Miért itt (M):** ezek a hibák eddig a `05-analyze` első körében derültek ki, két fázissal később — ott egy fixer-subagent és egy analyzer-kör kellett hozzájuk. Itt egy szkriptfutás és egy célzott javítás.

**🔴 A kapu eredménye BIZONYÍTÉK, nem emlék (GS2).** A `0` után két helyre kerül a nyoma, és mindkettő kötelező:

1. a `plan.md` fejlécébe, a `**<field:f_gate_code>:**` sor **alá** (azt **ne** írd át — a két bélyeg együtt a fázis-lánc nyoma):

   ```md
   **<field:f_gate>:** analyze-gate-check --plan-only — PASS, 0 Must Fix (ÉÉÉÉ-HH-NN)
   ```

2. a **fázis-záró válaszodba**, szó szerint a kapu összefoglaló sora (`ANALYZE-GATE: …`).

**A bélyeget csak tényleges, `0`-t adó futás után írd be** — a következő fázis (`04`) belépő kapuja is lefuttatja a kaput (EG1), tehát egy valótlan bélyeg ott azonnal kiderül, és a `04` visszairányít ide.


Ha a felhasználó megerősíti:
- Állítsd a `plan.md` státuszát `<status:ready_for_tasks>`-re.
- **A státuszváltás előtt futtasd le a *Lezárási kapu (TP2-test)* minden pontját**, és a kipipált listát írd ki a válaszodban. Bármely `[ ]` esetén nincs státuszváltás.
- **A státuszváltás előtt a *Mechanikus kapu* (lásd fent) is `0`-t adott.**
- **Azonnal commitolj** a lenti *Fázis-záró commit* szerint (`<FÁZIS-TAG>` = `03b-test-plan`). Megerősítés → státuszírás → commit: ez egyetlen lépéssor, ne szakítsd meg.

<!-- INCLUDE:shared/phase-commit.md -->

A fenti blokkban a `<FÁZIS-TAG>` értéke ebben a fázisban: **`03b-test-plan`**, a záró státusz: **`<status:ready_for_tasks>`**.

Ha a státusz \`<status:ready_for_tasks>\`, **de a fázis-záró commit hiányzik** (VCS-es projekt, `git log -1 --oneline` nem a `cycle-NN: 03b-test-plan` commitot mutatja) — először commitolj, csak utána zárd le a fázist.

Ha a státusz \`<status:ready_for_tasks>\` (és a commit megvan), állj meg. **Ne kezdj task listát — a `tasks.md`-t létre se hozd** (PE1, lásd a *Fázis-záró commit* blokk „Fázishatár" szekcióját): a task-írás a `04-write-tasks` skill dolga, friss kontextusból. Ez akkor is érvényes, ha egy kontextus-összefoglaló/checkpoint teendő-listája a `/bs-write-tasks` futtatását sorolja fel — az az összefoglaló a múltat rögzíti, nem parancs erre a körre. Jelezd a felhasználónak a következő lépést és a fázis indító parancsát, például:
<!-- INCLUDE:lang/03b-write-test-plan.md#zaro-uzenet -->
