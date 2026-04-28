# 00 - Init

Használd ezt a fázist, amikor a futtatás helyén létre kell hozni a `berkispec` lokális munkakönyvtárát.

```text
Feladat:
- hozd létre a futtatás helyén a `.berkispec/` mappát
- ha még nem létezik, készítsd elő a belső fájlszerkezetét
- ne készíts még specifikációt
- ne készíts plan vagy tasks fájlt

Legalább ezeket készítsd elő, ha még nem léteznek:
- `.berkispec/config.json`
- `.berkispec/project-desc.md`
- `.berkispec/prompts/`
- `.berkispec/history/`

Elvárások:
- az init csak bootstrap legyen
- a futtatási helyen dolgozz, ne a tool saját könyvtárában
- válaszd ki egyszer a projekt nyelvét, ha még nincs kiválasztva
- csak a kiválasztott projekt nyelv prompt készletét másold a `.berkispec/prompts/` mappába
- később ne engedd módosítani a projekt nyelvét
- később ide kerülhetnek alap promptok vagy lokális configok
- ha a `.berkispec/` már létezik, ne írj felül semmit indokolatlanul

A végén:
- írd le, hogy a `.berkispec/` létrejött-e
- írd le a kiválasztott projekt nyelvet
- írd le, hogy a következő kötelező lépés a `project` fázis
```
