<!-- Forrás-jegyzet: ezt a szekciót a 03a-write-code-plan.md, a 03b-write-test-plan.md
     ÉS a plan-fixer agent emeli be (build-time INCLUDE). Egy helyen szerkeszd. -->
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
