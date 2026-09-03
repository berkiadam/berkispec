<!-- Forrás-jegyzet: ezt a szekciót a 03a-write-code-plan.md ÉS a 03b-write-test-plan.md
     skill emeli be (build-time INCLUDE). Egy helyen szerkeszd. -->
### 🔴 A `plan.md` ÖNHORDÓ — ez a fázis legfontosabb szabálya

**A plan az utolsó dokumentum, amely még látja a spec-et.** Ami innentől lefelé történik, az **kizárólag a plan-ből** dolgozik:

| Fogyasztó | Mit olvas | Mit NEM lát |
|---|---|---|
| `04-write-tasks` | **csak a `plan.md`-t** (a skill explicit tiltja a spec és a forrásfájlok újraolvasását) | spec, kódbázis |
| `06-implement` | a `plan.md`-t + a `tasks.md`-t; a taskokból ide navigál vissza | spec |
| `test-runner` (07/09) | a `plan.md` `<sec:testing_strategy>` és `<sec:regression_impact>` szekcióit | spec, `test-conventions.md` |
| `03b-write-test-plan` | a `plan.md` **kód-felét** + a spec teszt-szekcióját és `DoD`-ját | a kódbázist forrásfájl-azonosítás céljából |

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
