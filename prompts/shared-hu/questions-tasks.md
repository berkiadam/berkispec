<!-- Forrás-jegyzet: a 04-write-tasks „Nyitott kérdések kezelése" szekciója,
     kiemelve, hogy a tasks-fixer subagent prompt is beemelhesse (BD14/b). -->
## Nyitott kérdések kezelése (tasks-questions.md)

A `tasks-questions.md` a tasks fázis kérdés-nyilvántartója, a `spec-questions.md` / `plan-questions.md` mintájára. **Scope:** elsősorban a Fix-mód (lásd lent) használja, amikor task-szintű döntés merül fel; a normál 04 flow is hivatkozhat rá, ha kérdés keletkezik a megszokott „STOP és jelezd" helyett (pl. új sessionban folytatott, megszakítás-biztos rögzítés).

**Struktúra** (ha még nem létezik, hozd létre a `specs/cycle-NN-<cycle-name>/` mappában):

```md
<!-- INCLUDE:lang/questions-tasks.md#tasks-questions-struktura -->
```

**Szabályok** (azonosak a spec/plan kérdés-nyilvántartóval):
- Egyszerre **egy** kérdés kerül a felhasználó elé — várd meg a választ.
- A listából **soha nem törlünk** — lezárt kérdést `[x]`-szel jelölünk, a döntés megmarad.
- Új kérdés a lista végére kerül a következő szekvenciális `Knn` számmal.
- **`tasks.md` státusz-kölcsönhatás:** ha van legalább egy nyitott `[ ]` kérdés a `tasks-questions.md`-ben, a `tasks.md` **nem lehet** `<status:ready_for_implement>`. A státusz `<status:draft>` marad, amíg minden kérdés `[x]`. (Fix-módban a `[analyze-loop]` markeres megfelelők szerint — lásd lent.)

