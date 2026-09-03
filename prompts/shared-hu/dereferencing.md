<!-- Forrás-jegyzet: ezt a szekciót a 03a-write-code-plan.md, a 03b-write-test-plan.md
     ÉS a plan-fixer agent emeli be (build-time INCLUDE). Egy helyen szerkeszd. -->
## Hivatkozás-feloldás (dereferencing) — a bemenet szintje NEM a plan szintje

> **A leggyakoribb hiba ebben a fázisban:** az ágens **reprodukálja a bemenet absztrakciós szintjét**. Ha a spec vagy a `plan-input-from-prev.md` azt írja, hogy *„képfájl build és push a registrybe a `build.sh` futtatásával"*, akkor ez a mondat kerül a plan-be — a **konkrét parancsok, registry-host, image-tag és paraméterek nélkül**. Ugyanígy: ha a bemenet felsorolja egy hívás **paraméterneveit**, az ágens beéri ennyivel, és a plan-ből hiányzik a **tényleges JSON payload** (pl. egy kötelező `"channelType": "MOBILBANK"` mező), amit a meglévő tesztkód tartalmaz.

**A szabály:** a bemenet absztrakciós szintje nem határozza meg a plan absztrakciós szintjét. **Ha egy bemeneti tétel hivatkozik valamire ahelyett, hogy tartalmazná, a hivatkozást FEL KELL OLDANI a forrásból** — mielőtt a plan-be írnád.

**Mit kell feloldani (nem kimerítő lista — a minta a lényeg):**

| A bemenet ezt mondja | Ezt kell kinyerni és a plan-be írni | Forrás |
|---|---|---|
| „futtasd a `build.sh`-t" / „a szokásos deploy folyamat" | a tényleges parancsok szó szerint, registry-host, image-név és tag, env-változók | maga a script, `Dockerfile`, CI-konfiguráció |
| „a login helper endpointtal szerzünk tokent" | teljes URL, metódus, **konkrét JSON payload minden kötelező mezővel**, fejlécek, példa `curl` | meglévő teszt-/segédkód (`test/`), OpenAPI leíró |
| „a meglévő integrációs teszt mintájára" | a tényleges hívási lánc, fixture-ök, seed-adatok, elvárt válaszok | a hivatkozott tesztfájl |
| „a `conventions.md` szerinti eszközzel" | a **döntés** marad hivatkozás, de a **futtatandó parancs** konkrétan | `conventions.md` + `package.json`/`Makefile` |
| „a compose fájl felhúzza a stacket" | service-ek, portok, health check, indítási sorrend | a compose fájl |

**Hogyan, token-hatékonyan:**

- **Kis, célzott forrás** (egy script, egy env-minta, egy compose fájl): olvasd be **közvetlenül**.
- **Nagy vagy szétszórt forrás** (kódbázis-keresés kulcsszóra, sok tesztfájl átnézése): a `researcher` subagentet indítsd (`agents/researcher.md`) — **de a kérésben explicit kérj literál értékeket**: *„add vissza szó szerint a parancsokat / az URL-t / a teljes JSON payloadot, ne összefoglalót"*. A researcher alapból tömörít; itt a **pontosság elsőbbséget élvez a tömörséggel szemben**.
- **Kövesd a láncot:** ha a script egy másik scriptre vagy `.env` fájlra hivatkozik, addig menj, amíg konkrét értéket nem kapsz. **Kivétel:** valódi titok (klaszter-, registry-, VPN-, IAM-credential) — ott **állj meg és pointert írj** (TC5), ne az értéket.
- **Ne másold be a teljes REPÓ-FÁJLT:** egy forrásfájlból/scriptből csak a végrehajtáshoz szükséges részt (parancsok, koordináták, séma, paraméterek) emeld át — a plan terv, nem archívum. **Ez a szabály a repó forrásfájljaira vonatkozik, NEM a spec-ből származó kidolgozott artefaktumokra** (OpenAPI, payload, hibamátrix, teszt-forgatókönyv): azokat teljes egészében át kell vinni, lásd `KX3`.
- **Ne parafrazeálj:** a parancsot és a JSON-t **szó szerint** vidd át. Egy „nagyjából ilyen" payload rosszabb, mint a semmi, mert hibás bizalmat kelt.
- **Jelöld a forrást:** a beemelt érték mellé `_(forrás: keycloak/docker/build.sh)_` — így később kiderül, ha a forrás elmozdult a plan-ben rögzített másolattól.

**Mikor kötelező ezt lefuttatni:** minden olyan bemeneti tételnél (spec, `plan-input-from-prev.md`, `test-conventions.md`, roadmap), amely **eljárásra, scriptre, konfigurációs állományra, külső API-ra vagy meglévő tesztre hivatkozik**. Ez **különösen** igaz korai ciklusban, amikor a `specs/test-conventions.md` még nem létezik: ilyenkor a recept-adatok egyetlen forrása a **meglévő kód és teszt** — keresd meg őket, ne a bemenet szövegére hagyatkozz.

> **A hurok bezárása:** amit így felderítesz (parancsok, koordináták, payload-sémák), az a `<sec:environment_coords>` (KO1) szekcióba kerül — és pontosan az, aminek a ciklus végén a `08-doc-sync` révén be kell kerülnie a `specs/test-conventions.md`-be — a konkrét koordináták a 0. blokkba, a receptek az 1. szekcióba (TC3/TC13) — hogy a következő ciklus már ne derítse fel újra.
