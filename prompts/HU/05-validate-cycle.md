# 05 - Validate Cycle

Használd ezt a promptot, amikor egy ciklus végén külön ellenőriztetni akarod, hogy minden elkészült-e.

```text
Validáld az alábbi ciklus lezárását:

specs/<cycle-name>/spec.md
specs/<cycle-name>/plan.md
specs/<cycle-name>/tasks.md

Feladat:
- ellenőrizd, hogy a `tasks.md` minden releváns taskja elkészült-e
- ellenőrizd, hogy a `spec.md` definition of done pontjai teljesülnek-e
- ellenőrizd, hogy a `plan.md` szerinti fő technikai döntések megvalósultak-e vagy dokumentáltan változtak-e
- futtasd a releváns teszteket
- ellenőrizd a tesztriport meglétét és tartalmát
- ne vezess be új feature-t

Ha hiányt találsz:
- javítsd, ha kicsi és egyértelműen scope-on belüli
- ha nagyobb döntést igényel, dokumentáld nyitott kérdésként

A végén:
- frissítsd a `tasks.md` státuszait
- frissítsd a `spec.md` állapotát
- készíts rövid lezáró összefoglalót
- sorold fel a futtatott teszteket
- sorold fel a maradó kockázatokat vagy mondd ki, hogy nincs ismert maradó kockázat
```
