---
phase: 08
name: review-and-merge
prerequisites:
  - "specs/cycle-NN-<name>/tasks.md státusz: Kész"
  - "specs/cycle-NN-<name>/plan.md státusz: Kész"
  - "specs/cycle-NN-<name>/spec.md státusz: Kész"
output:
  - "specs/cycle-NN-<name>/code-review.md"
  - "Merged cycle branch (lokális vagy PR, a conventions.md Merge stratégiája szerint)"
prev: 07-validate
next: 02-write-spec
subagents:
  - "agents/reviewer.md"
---

# 08 — Review és Merge

Spec driven development-ben fejlesztünk szoftvert. A fejlesztés ciklusokra van bontva. Minden ciklus egy önállóan lefejleszthető, önállóan tesztelhető részegysége a teljes implementációnak.

Ez a fejlesztési folyamat **8-as fázisa (a 0–8 fázisokból)**:
0. projekt inicializálás (setup)
1. ciklusok kezelése (setup)
2. spec
3. plan
4. tasks
5. analyze
6. implement
7. validate
8. **review & merge** ← most itt vagyunk

---

## Előfeltétel

1. **`conventions.md` létezés-ellenőrzés:** olvasd be a projekt gyökerében a `conventions.md`-t (különösen a `## Merge stratégia` szekciót). Ha nem létezik, STOP — térjenek vissza a `00` fázishoz.

2. **Munkafa ellenőrzés:** futtasd `git status --short`. Ha van commitálatlan változtatás, listázd, és kérdezd meg egy körben, hogy commitáljam-e most vagy folytassam — várj a válaszra. (A review a cycle branch git diffjét nézi a `master`-höz képest; tiszta munkafa nélkül a diff félrevezető.)

3. **Státusz-kapu:** a validate fázis (07) PASS esetén mindhárom fájl státuszát `Kész`-re állítja. Ellenőrizd:
   - `tasks.md` státusza: `Kész`
   - `plan.md` státusza: `Kész`
   - `spec.md` státusza: `Kész`

   Ha bármelyik nem `Kész` (pl. még `Validálásra kész` vagy visszaállított `Piszkozat`), a validálás még nem futott le sikeresen — térj vissza a `07` fázishoz.

---

## Feladatod

1. Automatikus code review futtatása a `reviewer` ágenssel.
2. Review hibák kezelése (FAIL esetén vissza a `06-implement` fázisba a `tasks.md` frissítésével).
3. `docs/architecture.md` és komponens README-k frissítése / konzisztencia-ellenőrzése, majd célzott dokumentációs ellenőrzés.
4. Merge végrehajtása a `conventions.md` Merge stratégiája szerint (lokális squash vagy PR), **kötelező felhasználói megerősítés után**.

---

## 1. Automatikus review (Review Agent subagenttel)

A kód ellenőrzését egy dedikált subagent végzi el. Hajtsd végre a következőket:

1. Olvasd be a `prompts/agents/reviewer.md` rendszerpromptot.
2. Definiálj egy `reviewer` subagentet ezzel a rendszerprompttal.
3. Indítsd el a subagentet, átadva neki a cycle branch és a `master` branch közötti `git diff`-et, a `conventions.md`-t, a `plan.md`-t és a `spec.md`-t.
4. A subagent elkészíti a jelentést és elmenti a `specs/cycle-NN-<cycle-name>/code-review.md` fájlba.

> **Ha a subagent nem fut le, vagy nem készít `code-review.md`-t:** STOP. Ne merge-elj review nélkül. Jelezd a felhasználónak, hogy a review nem készült el, és kérdezd meg, hogy próbáljam-e újra a subagentet, vagy végezzem el a review-t közvetlenül a `reviewer.md` szempontjai szerint a fő ágensben.

5. Olvasd be a `code-review.md` fájlt és értékeld az eredményt:
   - **Ha a jelentés "Kritikus javítandók (Must Fix)" szekciójában vannak lezáratlan `- [ ]` checkboxok:**
     1. Hozz létre a `tasks.md` végén egy új `## Review javítások` fejezetet.
     2. Hivatkozd be a fejezet elején a prerequisite dokumentumok közé a `specs/cycle-NN-<cycle-name>/code-review.md` fájlt.
     3. Vedd fel a konkrét javítandó kód-review hibákat új `[GREEN]` taskokként, a csoport végén egy `[CHECK]` ellenőrző taskot megadva. *(Review-javításoknál `[RED]` párt nem kell felvenni — a javítás nem TDD-körrel, hanem direkten történik.)*
     4. Állítsd a `tasks.md` státuszát vissza `Implementálásra kész` állapotra.
     5. Jelezd a felhasználónak a sikertelen review-t és a visszalépést, majd kérd meg az implementációs lépés futtatására a javításhoz:
        > *"A kódellenőrzés során kritikus hibák merültek fel. A hibákat rögzítettem a `tasks.md` végén új feladatokként, a státuszt pedig visszaállítottam `Implementálásra kész` állapotra. Folytasd az implementáció javításával:
        > ```
        > Kövesd a `prompts/skills/06-implement.md` utasításait.
        > Input: `specs/cycle-NN-<cycle-name>/tasks.md`
        > ```"*
   - **Ha nincsenek kritikus hibák (csak javaslatok/ajánlások vannak vagy teljesen tiszta a jelentés):**
     A `Suggestions` szekció **nem blokkol**. Ha egy javaslat a ciklus scope-ján belül van és kockázat nélkül, gyorsan alkalmazható, javítsd direktben és commitold (`cycle-NN: 08-merge - review suggestion`). Ha scope-on kívül esik vagy bizonytalan, hagyd a `Suggestions` listában jövőbeli ciklusnak — ne kezdj scope creep-et. Ezután folytasd a dokumentáció ellenőrzésével és a merge folyamattal.

---

## 2. `docs/architecture.md` frissítése

A `docs/architecture.md` a rendszer élő, kumulatív dokumentációja. Az implement fázis `TLAST` taskja már felvette az új elemeket — ez a lépés a **konzisztencia-ellenőrzés és finomítás**: átjárja a teljes dokumentumot, javítja az elavult részeket, és a ciklus végső állapotát egységessé teszi.

### Mi kerüljön bele

- **Bevezető** — minden frissítésnél felülírjuk: egy-két bekezdés, ami összefoglalja a rendszer aktuális célját, komponenseit és az utolsó ciklus változásait.
- **Komponensek leírása** — minden komponenshez: feladat, konfiguráció, függőségek, deployment mechanizmus.
- **Architektúra diagramok** — aktuális állapotot tükröző Mermaid diagramok. Elavult ábra nem maradhat a dokumentumban.
- **Adatfolyamok és hívási szekvenciák** — az összes jelentős flow diagramja.
- **Hivatkozások** — minden formális leíróra mutasson hivatkozás: OpenAPI YAML-ok, Redis key map-ek, Keycloak konfig, egyéb doksi-k.
- **Kulcsdöntések és indoklásuk** — miért így és nem másképp.

### Frissítési szabályok

- Csak azt írd felül, ami ebben a ciklusban változott — a többi érintetlen marad.
- Új komponens → új fejezet. Módosult komponens → az érintett fejezet frissül. Törölt funkció → a hivatkozások eltávolítandók.
- Ha a struktúra már nem tükrözi jól a rendszert, rendezd újra a fejezeteket.

### Konzisztencia ellenőrzés

**Minden egyes módosított szekció után** — ne csak a végén — ellenőrizd:
- Van-e más fejezet vagy ábra a dokumentumban, amely ellentmond az éppen frissítettnek?
- Minden diagram az aktuális állapotot mutatja? (komponensek neve, portok, kapcsolatok)
- Minden hivatkozás érvényes? (fájl létezik, tartalom egyezik)
- A bevezető konzisztens az összes többi fejezettel?

Ha ellentmondást találsz, azonnal javítsd.

### Komponens README-k ellenőrzése

Az `architecture.md` frissítése után ellenőrizd az ebben a ciklusban **érintett** komponensek `README.md` fájljait:
- Új komponens: létezik-e a `README.md`? Ha nem, hozd létre.
- Meglévő komponens: ha a ciklus változtatott a komponens viselkedésén, portján, indításán vagy kapcsolatain — frissítsd a README-t.
- A README tartalma konzisztens az `architecture.md` megfelelő fejezetével?

### Dokumentációs konzisztencia-ellenőrzés és commit

A review **a kód** diffjén futott; a dokumentáció (`architecture.md`, README-k) ezután változott, ezért az nem volt review-zott. Mielőtt merge-elnél, végezz **célzott dokumentációs konzisztencia-ellenőrzést** (ez NEM új subagent review, csak átolvasás):
- A frissített `architecture.md` és README-k konzisztensek-e a kód tényleges állapotával?
- Minden diagram, port, hivatkozás az aktuális állapotot tükrözi?

Ha rendben, commitold a dokumentációs változásokat a merge előtt:
```bash
git add docs/ <érintett README-k>
git commit -m "cycle-NN: 08-merge - dokumentáció frissítés"
```

---

## 3. Merge — a conventions.md Merge stratégiája szerint

Olvasd be a `conventions.md` `## Merge stratégia` szekcióját, és a **Szolgáltató** mező alapján járj el. **Bármelyik ágon a merge előtt KÖTELEZŐ a felhasználói megerősítés** — a `master`-be merge és a branch törlése destruktív, megerősítés nélkül nem hajtható végre.

### Megerősítés (mindkét ágon kötelező)

Kérdezd meg, és **várj explicit megerősítésre**:
> *"A review tiszta, a dokumentáció frissítve. Készen állok a merge-re a `<szolgáltató>` stratégia szerint (`feature/cycle-<cycle-name>` → `<target branch>`). Végrehajthatom?"*
> **A válasz végén helyezd el a `code-review.md` közvetlen, kattintható linkjét.**

Ne lépj tovább a megerősítés előtt.

### A) Lokális (nincs PR)

Megerősítés után:
```bash
# 1. Válts át a master (vagy a konvencióban megadott target) ágra
git checkout master

# 2. Squash merge a ciklus ágáról
git merge --squash feature/cycle-<cycle-name>

# 3. Commit a ciklus címével és a plan célkitűzésével
git commit -m "cycle-NN: 08-merge - <cím>" -m "<cél és megközelítés a plan.md-ből>"

# 4. A lokális ciklus ág törlése
git branch -D feature/cycle-<cycle-name>
```

### B) GitHub / Bitbucket / GitLab (PR)

Megerősítés után hozd létre a PR-t a `conventions.md`-ben megadott szolgáltató szerint, a `conventions.md` target branchére. A PR description a `code-review.md` tartalma legyen:
- **GitHub:** `gh pr create --base <target> --head feature/cycle-<cycle-name> --title "cycle-NN: <cím>" --body-file specs/cycle-NN-<cycle-name>/code-review.md`
- **GitLab:** `glab mr create --target-branch <target> --title "cycle-NN: <cím>" --description "$(cat specs/cycle-NN-<cycle-name>/code-review.md)"`
- **Bitbucket:** a `conventions.md` access-parancsa szerint, REST API-n vagy CLI-n keresztül.

A PR-alapú ágon **ne** töröld lokálisan a branchet és **ne** merge-elj a `master`-be közvetlenül — a merge a szolgáltatón történik a review/CI után.

### Merge conflict kezelése

Ha a merge során ütközés (merge conflict) lép fel:
1. **NE találd ki a feloldást.** Listázd ki az ütköző fájlokat (`git status`).
2. Minden ütköző fájlnál nézd meg mindkét oldalt (a `master` és a cycle branch verzióját), és a `plan.md` / `spec.md` alapján döntsd el, melyik a helyes — vagy hogy a kettő összefésülése kell-e.
3. Ha a feloldás egyértelmű a ciklus szándéka alapján, oldd fel, futtasd újra a releváns ellenőrzést, majd commitold.
4. **Ha a feloldás nem egyértelmű** (mindkét oldal érdemi, ütköző logikát tartalmaz), STOP — jelezd a felhasználónak az ütköző fájlokat és a két oldalt, és kérj döntést.

---

## Roadmap státusz frissítés

A merge után frissítsd a `specs/roadmap.md`-t: jelöld az adott ciklust lezártként (pl. a ciklus címe mellé `✅` vagy `(kész)` jelölés), hogy a roadmap tükrözze a ciklus befejezését. Commitold a roadmap frissítését (PR-ágon a PR része lehet, lokális ágon külön commit).

---

## Státusz kezelés

Ha a merge (vagy PR létrehozás) sikeresen megtörtént, jelezd a felhasználónak a ciklus lezárását és a következő ciklus indító promptját:

> *"A kódellenőrzés sikeres volt, a dokumentációkat frissítettem, és a ciklust lezártam a `conventions.md` Merge stratégiája szerint (`<lokális squash merge` / `PR létrehozva>`). A ciklus sikeresen lezárult.*
>
> *Megkezdhető a következő ciklus. Új ciklus hozzáadásához:*
> ```
> Kövesd a `prompts/skills/01-add-cycles.md` utasításait.
> ```
> *Vagy ha a következő ciklus már a roadmap-en van, közvetlenül a spec fázissal:*
> ```
> Kövesd a `prompts/skills/02-write-spec.md` utasításait.
> Input: `specs/roadmap.md` (ciklus kontextus), ciklus: cycle-NN-<cycle-name>
> ```"*
