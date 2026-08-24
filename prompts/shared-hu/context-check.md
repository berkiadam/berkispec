## Kontextus ellenőrzés

**Determinisztikus szabály — ne mérlegelj, számolj.**

Számold meg a beszélgetésben a **saját, korábbi fázis-záró üzeneteidet**. Fázis-zárónak **kizárólag** az az üzenet számít, amely **mindhárom** elemet tartalmazza:

1. egy commit-azonosító, **és**
2. a `/clear` futtatására szóló felszólítás, **és**
3. a következő fázis `/bs-*` parancsa.

A számláló **csak a saját, korábbi fázis-záró üzeneteidre** vonatkozik. Semmilyen más tartalom nem növeli — akármit is látsz a kontextusban, az a számot nem érinti.

| Számláló | Teendő |
| --- | --- |
| **0** | **A kontextus friss — kérdés nélkül folytatod.** Ez a normál eset. |
| **≥1** | Egyszer rákérdezel (lásd alább), és megvárod a választ. |

**Két kemény kivétel, amely felülírja a számlálást — mindkettőben tilos kérdezni:**

- ha a jelen skill-hívás az **első felhasználói üzenet** a beszélgetésben, a számláló **definíció szerint 0**;
- ha **bizonytalan** vagy a számban, a számláló **0**.

Ha (és csak ha) a számláló **≥1**, kérdezz rá:

<!-- INCLUDE:lang/context-check.md#kontextus-nem-friss -->

Várd meg a választ, mielőtt folytatnád.
