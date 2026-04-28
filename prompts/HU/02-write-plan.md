# 02 - Write Plan

Használd ezt a promptot, amikor a jóváhagyott `spec.md` alapján technikai implementációs tervet akarsz készíttetni.

```text
Készíts implementációs tervet az alábbi specifikáció alapján:

specs/<cycle-name>/spec.md

A terv helye:

specs/<cycle-name>/plan.md

Feladat:
- olvasd el a `spec.md` fájlt
- olvasd el a releváns kódot és dokumentációt
- készíts `plan.md` fájlt
- ne implementálj kódot
- ne készíts tasks fájlt ebben a fázisban

A `plan.md` tartalmazza:
- cél és megközelítés
- érintett komponensek
- érintett fájlok vagy modulok
- tervezett módosítások
- konfigurációs / runtime változások
- adatfolyam vagy request flow
- tesztelési és verifikációs stratégia
- végrehajtási sorrend
- kockázatok
- döntési pontok

Elvárások:
- a plan a specből induljon ki, ne vezessen be új scope-ot
- jelezd, ha a spec hiányos vagy ellentmondásos
- preferáld a repo meglévő mintáit
- külön jelöld, ha valamelyik módosítás production kockázatot hordoz
- a végén írd le, hogy a plan alapján elkészíthető-e a tasks fájl
```
