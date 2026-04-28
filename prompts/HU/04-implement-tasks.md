# 04 - Implement Tasks

Használd ezt a promptot, amikor a ciklus tényleges implementációját akarod elindítani.

```text
Hajtsd végre az alábbi ciklust:

specs/<cycle-name>/spec.md
specs/<cycle-name>/plan.md
specs/<cycle-name>/tasks.md

Feladat:
- dolgozz a `tasks.md` alapján
- kövesd a `plan.md` technikai irányát
- használd a `spec.md` fájlt viselkedési és scope referenciaként
- implementáld a szükséges kód- és dokumentációs módosításokat
- pipáld ki a kész taskokat a `tasks.md` fájlban
- ne módosíts unrelated kódot

Munkaszabályok:
- ha egy task túl nagy, bontsd kisebb taskokra a `tasks.md` fájlban
- ha a plan hibásnak bizonyul, frissítsd a plant rövid indoklással
- ha a spec hiányos, állj meg és jelezd a nyitott kérdést
- production kockázatú diagnosztikai vagy teszt endpoint csak explicit teszt flag mellett lehet aktív
- minden módosítás után futtasd a releváns tesztet, ha életszerű

Verifikáció:
- futtasd a `tasks.md` verifikációs szekciójában szereplő parancsokat
- ha valamelyik parancs nem futtatható, dokumentáld az okát
- sikertelen teszt esetén vizsgáld ki és javítsd, ha a ciklus scope-jába tartozik

A végén:
- frissítsd a tasks státuszait
- frissítsd a spec állapotát, ha elkészült
- készíts vagy frissíts tesztriportot, ha a tasks ezt kéri
- foglald össze a módosított fájlokat
- foglald össze, milyen tesztek futottak le
- jelezd a maradék kockázatokat
```
