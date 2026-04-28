# 03 - Write Tasks

Használd ezt a promptot, amikor a jóváhagyott `spec.md` és `plan.md` alapján végrehajtható task listát akarsz készíttetni.

```text
Készíts végrehajtási task listát az alábbi fájlok alapján:

specs/<cycle-name>/spec.md
specs/<cycle-name>/plan.md

A task lista helye:

specs/<cycle-name>/tasks.md

Feladat:
- olvasd el a specet és a plant
- készíts checkboxos `tasks.md` fájlt
- ne implementálj kódot

A `tasks.md` legyen:
- konkrét
- pipálható
- kis lépésekre bontott
- fájlhoz, komponenshez vagy ellenőrizhető kimenethez kötött
- végrehajtási sorrendbe rendezett

A task lista tartalmazza:
- kódmódosítási taskok
- dokumentációs taskok
- teszt / verifikációs taskok
- riport / lezárási taskok

Formátum:

- [ ] T001 ...
- [ ] T002 ...
- [ ] T003 ...

Elvárások:
- ne legyen túl nagy egy task
- ne legyen homályos task, például "javítsd a működést"
- minden fontos DoD pontnak legyen task vagy verifikációs task megfelelője
- a végén legyen `Állapot` szekció `READY_FOR_IMPLEMENTATION` értékkel
```
