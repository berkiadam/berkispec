# 01 - Modify Spec

Használd ezt a promptot, amikor egy meglévő `spec.md` fájlt kell pontosítani az AI kérdései és a user új válasza alapján.

## Agent feladat

```text
Feladat:
- olvasd el a meglévő spec.md fájlt
- olvasd el a Codex előző válaszát vagy nyitott kérdéseit
- olvasd el a user új válaszát
- olvasd el és vedd figyelembe a .berkispec/project-desc.md fájlt
- vesd össze a .berkispec/project-desc.md "Reference Files" szekcióját a user céllal és a módosuló spec tartalmával
- módosítsd a spec.md fájlt úgy, hogy a user válasz beépüljön
- ne készíts plan vagy tasks fájlt
- ne implementálj kódot

Tisztázási szabályok:
- ha a projektleírás, referenciafájlok, user input vagy meglévő spec között inkonzisztencia van, ne találj ki megoldást, kérdezz vissza
- ha lényeges információ hiányzik, kérdezz vissza
- ha több lehetséges értelmezés van, kérdezz vissza

Qxxx kezelés:
- keresd meg a kapcsolódó Qxxx kérdést
- építsd be a user válaszát a releváns spec részbe
- távolítsd el vagy oldd fel a kapcsolódó inline [NEEDS CLARIFICATION Qxxx: ...] markert
- a "Nyitott kérdések" szekcióban jelöld lezártnak, vagy vezesd át lezárt állapotba
- rögzítsd a döntést
- ha új kérdés keletkezik, hozz létre új Qxxx azonosítót

Lezárt döntések:
- vezess "## Tisztázott döntések" szekciót, és rögzítsd benne:
  - Qxxx: eredeti kérdés röviden
  - User válasz: ...
  - Döntés: ...
  - Érintett spec rész: ...

Státusz:
- a specben mindig maradjon explicit státuszmező:
  - `## Állapot` szekcióban vagy `Állapot: ...` sorban
- amíg van OPEN kérdés vagy van [NEEDS CLARIFICATION ...] marker, maradjon DRAFT
- csak akkor állítsd READY_FOR_PLAN-ra, ha nincs OPEN kérdés és nincs marker
```
