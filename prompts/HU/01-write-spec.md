# 01 - Write Spec

Használd ezt a promptot, amikor egy új ciklus vagy feature specifikációját akarod elkészíttetni.

## Kötelező user input

A user promptnak legalább ezt a két mezőt kell tartalmaznia:

```text
Ciklus neve:
<ide jön a ciklus rövid neve>

Cél:
<ide jön a cél szöveges leírása>
```

## Agent validáció

Mielőtt specifikációt írsz:

1. Ellenőrizd, hogy a user prompt tartalmaz-e `Ciklus neve` mezőt.
2. Ellenőrizd, hogy a user prompt tartalmaz-e `Cél` mezőt.
3. Ha bármelyik hiányzik, ne hozz létre fájlt, hanem válaszolj ezzel:

```text
Validációs hiba: a spec létrehozásához kötelező megadni a `Ciklus neve` és `Cél` mezőket.
```

4. Ha mindkét mező megvan, adj automatikus ciklussorszámot.
5. A sorszámot a meglévő `specs/cycle-*` almappák alapján válaszd ki: a legnagyobb meglévő ciklussorszám + 1.
6. A ciklus mappaneve legyen:

```text
specs/cycle-XX-<slug>/
```

A `<slug>` a `Ciklus neve` rövid, kisbetűs, kötőjeles változata legyen.

Példa:

```text
Ciklus neve:
TMP token refresh error handling E2E

Cél:
Bizonyítsuk E2E teszttel, hogy sikertelen FlowX refresh grant esetén a TMP kontrollált hibát ad vissza.
```

Ha a legnagyobb meglévő ciklus a `cycle-07-*`, akkor az új fájl helye:

```text
specs/cycle-08-tmp-token-refresh-error-handling-e2e/spec.md
```

## Használható user prompt példa

```text
Ciklus neve:
<ide írd a ciklus vagy feature rövid nevét>

Cél:
<ide írd le, mit szeretnél elérni vagy bizonyítani>
```

## Agent feladat

Ha a validáció sikeres:

```text
Feladat:
- olvasd el a releváns projekt dokumentációt és kódot
- értsd meg a jelenlegi működést
- hozz létre új `specs/cycle-XX-<slug>/spec.md` fájlt
- ne implementálj kódot
- ne készíts plan vagy tasks fájlt ebben a fázisban
- olvasd el és vedd figyelembe a .berkispec/project-desc.md fájlt
- vesd össze a .berkispec/project-desc.md "Reference Files" szekcióját a user céllal és a készülő spec tartalmával
- ha a projektleírás, referenciafájlok, user input vagy a készülő spec között inkonzisztencia van, ne találj ki megoldást, kérdezz vissza
- ha lényeges információ hiányzik, kérdezz vissza
- ha több lehetséges értelmezés van, kérdezz vissza

A `spec.md` tartalmazza:
- cél
- háttér és motiváció
- scope
- out of scope
- érintett felhasználói vagy rendszerfolyamat
- funkcionális követelmények
- hibakezelési és edge case elvárások
- érintett komponensek magas szinten
- kötelező tesztek / bizonyítási módok
- definition of done
- nyitott kérdések

Elvárások:
- a spec tartalmazzon egyértelmű státuszmezőt, az alábbi formák egyikében:
  - `## Állapot` szekció `DRAFT` vagy `READY_FOR_PLAN` értékkel
  - vagy `Állapot: DRAFT` / `Állapot: READY_FOR_PLAN` sor
- új spec létrehozásakor a kezdeti státusz kötelezően `DRAFT`
- a spec legyen döntésképes, de ne legyen implementációs terv
- ahol bizonytalan vagy, jelöld pontosan inline markerrel:
  [NEEDS CLARIFICATION Q001: rövid kérdés]
- minden nyitott kérdést vezesd az összesített szekcióban:
  ## Nyitott kérdések
  - [ ] Q001: rövid kérdés
    - Kontextus: ...
    - Miért fontos: ...
    - Státusz: OPEN
    - User válasz: _még nincs_
    - Döntés: _még nincs_
- a kérdésazonosítók stabilak és növekvők legyenek: Q001, Q002, Q003...
- ne találj ki új architektúrát, ha a repo meglévő mintái elegendőek
- amíg legalább egy nyitott kérdés van, a spec státusza maradjon DRAFT
- csak akkor állítsd READY_FOR_PLAN-ra a státuszt, ha nincs több nyitott kérdés, nincs több inline [NEEDS CLARIFICATION ...] marker, és a spec alapján biztonságosan készíthető plan
- a végén foglald össze, milyen kérdésekben kell emberi jóváhagyás
```
