---
phase: 05
name: analyze
prerequisites:
  - "specs/cycle-NN-<name>/tasks.md státusz: Implementálásra kész"
output:
  - "specs/cycle-NN-<name>/analyze-report.md (PASS / FAIL)"
prev: 04-write-tasks
next: 06-implement
subagents:
  - "agents/analyzer.md"
---

# 05 — Analyze (kereszt-fázisos konzisztencia ellenőrzés)

Spec driven development-ben fejlesztünk szoftvert. A fejlesztés ciklusokra van bontva. Minden ciklus egy önállóan lefejleszthető, önállóan tesztelhető részegysége a teljes implementációnak.

Ez a fejlesztési folyamat **5-ös fázisa (a 0–8 fázisokból)**:
0. projekt inicializálás (setup)
1. ciklusok kezelése (setup)
2. spec
3. plan
4. tasks
5. **analyze** ← most itt vagyunk
6. implement
7. validate
8. review & merge

---

## Cheat sheet

| Szekció | Egy mondatban |
|---|---|
| Előfeltétel | `tasks.md` = `Implementálásra kész`, `conventions.md` létezik, tiszta munkafa. |
| Feladatod | Read-only kereszt-ellenőrzés a `spec.md` ↔ `plan.md` ↔ `tasks.md` ↔ `conventions.md` négyesen, 5 kategóriában. |
| Analyzer subagent | A nehéz kereszt-vizsgálatot a `agents/analyzer.md` subagent végzi; te a jelentését értékeled. |
| Eredmény | `analyze-report.md` PASS vagy FAIL, súlyossági besorolással. |
| FAIL | Státusz-visszafordítás + visszalépés a kategória → fázis leképezés szerint (legkorábbi érintett fázis nyer). |
| PASS | Tovább a 06-implement fázisra. Commit: `cycle-NN: 05-analyze`. |

---

## Előfeltétel

1. **`conventions.md` létezés-ellenőrzés:** olvasd be a projekt gyökerében a `conventions.md`-t. Ha nem létezik, **STOP** — jelezd a felhasználónak, hogy térjenek vissza a `00` projekt inicializálás fázishoz, és ne folytasd.

2. **Tasks státusz:** olvasd be a `specs/cycle-NN-<cycle-name>/tasks.md` státuszát. **Ha nem `Implementálásra kész`, STOP** — a task lista még nem zárult le. Jelezd, és térjenek vissza a `04` tasks fázishoz.

3. **Munkafa ellenőrzés:** futtasd: `git status --short`. Ha van commitálatlan változtatás:
   - Listázd ki az érintett fájlokat.
   - Jelezd: *"Az analízis read-only, de a tiszta munkafa segít a pontos kereszt-ellenőrzésben."*
   - Kérdezd meg: *"Commitáljam ezeket most, vagy folytassam?"* — egy kérdés, várj a válaszra, majd folytasd.

---

## Folytatás megszakított futás után

Az analízis read-only, ezért újraindítható kockázat nélkül. Döntési fa — **ebben a sorrendben**:

```
1. Létezik már analyze-report.md a ciklus mappájában?
   → Olvasd be. Ha a státusza FAIL és a visszalépés már megtörtént
     (a célfázis dokumentuma nem-kész státuszon áll): NE futtasd újra,
     jelezd a felhasználónak, hogy a visszalépés érvényben van.
   → Ha a státusza PASS: jelezd, hogy az analízis már lezárult, tovább a 06-ra.

2. Létezik analyze-report.md, de félbeszakadtnak tűnik
   (nincs minden kategória kitöltve)?
   → Töröld a részleges jelentést, és kezdd elölről az analízist.

3. Nincs analyze-report.md?
   → Kezdd az analízist az "Feladatod" szerint.
```

---

## Feladatod

Ellenőrizd, hogy a ciklus tervezési dokumentumai (`spec.md`, `plan.md`, `tasks.md`) **konzisztensek egymással és a `conventions.md`-vel**, mielőtt az implementáció megkezdődne. Ez egy **read-only** fázis: nem módosítasz forrásfájlt vagy tervezési dokumentumot — kizárólag jelentést készítesz (kivéve FAIL esetén a státusz-visszafordítást, lásd lent).

**Ne implementálj semmit.** Ez a sanity check az implementáció előtt.

A vizsgálat **5 kategóriában** keres problémát:

1. **Duplikációk** — ismétlődő követelmények a spec/plan/tasks között (ugyanaz a viselkedés többször, redundáns task).
2. **Ambiguitás** — vágy fogalmak, hiányzó mérőszámok, nem mérhető elfogadási feltétel.
3. **Alulspecifikáció** — hiányzó elfogadási feltétel, meghatározatlan komponens, taskhoz nem rendelhető plan-szekció.
4. **Konvenció-ütközések** — a `conventions.md`-vel szembeni eltérés (tech stack, naming, teszt eszköz, merge stratégia, struktúra).
5. **Lefedettségi hiányok** — követelmény ↔ task egymáshoz rendelés: van-e spec-követelmény, amelyhez nem tartozik task, vagy task, amely nem vezethető vissza a planre.

---

## Kontextus betöltési szabályok

- A kereszt-vizsgálat sok fájl együttes olvasását igényli — **kötelező az `agents/analyzer.md` subagent indítása**. A subagent beolvassa a `spec.md` + `plan.md` + `tasks.md` + `conventions.md` négyest, elvégzi az 5 kategóriás vizsgálatot, és **kizárólag a strukturált jelentést adja vissza** (a nyers fájltartalom nem terheli a fő kontextust).
- A subagent rendszerpromptja: olvasd be a `prompts/agents/analyzer.md`-t, és ezzel definiáld az `analyzer` subagentet.
- A subagent kimenetét te értékeled, és ez alapján döntesz PASS / FAIL-ról.

---

## Súlyossági besorolás

Minden megállapítás **Must Fix** vagy **Suggestion**:

- **Must Fix** = blokkolja az implementációt (a hibás alapra épülő implementáció kockázatos): valódi duplikáció, lefedettségi rés, konvenció-ütközés, meghatározatlan komponens, nem eldönthető elfogadási feltétel.
- **Suggestion** = nem blokkol, csak javasolt finomítás (átfogalmazás, kisebb tisztázás).

**PASS feltétele:** nincs `Must Fix` megállapítás. Ha csak `Suggestion`-ök vannak, az eredmény PASS (a suggestion-öket a felhasználó eldöntheti, de nem állítják meg a folyamatot).

---

## FAIL — kategória → visszalépési cél

Egy olcsóbb LLM-nek konkrét célt kell adni, nem „vissza a megfelelő fázisba". A `Must Fix` megállapítás kategóriája határozza meg a visszalépés célfázisát:

| Kategória | Visszalépés | Indok |
|---|---|---|
| Duplikáció | 03 (tervezési szintű), 04 (task-szintű) | a redundancia forrásához |
| Ambiguitás | 03 (technikai döntés), 02 (viselkedési — ritka) | ahol a fogalmat tisztázni kell |
| Alulspecifikáció | 03 (meghatározatlan komponens), 02 (hiányzó elfogadási feltétel) | a hiányzó döntés szintjére |
| Konvenció-ütközés | 03 (enyhe), 00 (súlyos — `conventions.md` felülvizsgálat) | összhangban az SK4 logikájával |
| Lefedettségi hiány | 04 (követelmény ↔ task újrarendelés) | a task lista a hiányos |

**Szabályok:**
- A visszalépés **státusz-visszafordítással** jár: a célfázis dokumentuma visszaáll a nem-kész státuszára (`spec.md` → `Piszkozat`, `plan.md` → `Piszkozat`, `tasks.md` → `Piszkozat`).
- Ha **több kategória is FAIL**, a **legkorábbi érintett fázisra** kell visszalépni (02 < 03 < 04), hogy a későbbi fázisok ne épüljenek hibás alapra.
- A státusz-visszafordítás az egyetlen írási művelet, amit ez a fázis a tervezési dokumentumokon végez.

---

## analyze-report.md struktúra

Hozd létre a `specs/cycle-NN-<cycle-name>/analyze-report.md` fájlt (relatív útvonal-formátum, `file://` tilos):

```md
# Cycle NN: <cím> — Analyze report

**Státusz:** PASS | FAIL
**Futás:** YYYY-MM-DD HH:MM

## Összefoglaló

_Egy-két mondat: konzisztens-e a négyes, vagy hol van a baj._

## Megállapítások

### Must Fix
- [ ] <kategória> — <leírás> → visszalépés: <célfázis> (`fájl:hely` ha van)

### Suggestions
- <kategória> — <leírás>

## Lefedettségi mátrix (követelmény ↔ task)

| Spec követelmény | Plan szekció | Task(ok) | Lefedve |
|---|---|---|---|
| ... | ... | T0xx | ✓ / ✗ |
```

---

## Minőségellenőrzés — a jelentés lezárása előtt

Menj végig, mind az 5 kategória ténylegesen lefutott-e:

1. **Duplikáció** — átnézve spec/plan/tasks redundanciára?
2. **Ambiguitás** — minden elfogadási feltétel mérhető/eldönthető?
3. **Alulspecifikáció** — minden komponens és feltétel meghatározott?
4. **Konvenció-ütközés** — minden tervezési döntés egyezik a `conventions.md`-vel?
5. **Lefedettség** — a lefedettségi mátrix minden spec-követelményt és minden taskot tartalmaz?

Ha bármelyik kategória nem futott le, ne zárd le a jelentést.

---

## Státusz kezelés

### PASS

Nincs `Must Fix` megállapítás.

Teendők:
1. Írd a `analyze-report.md` státuszát `PASS`-re.
2. Commitáld a fázis lezárását:
   ```bash
   git add specs/cycle-NN-<cycle-name>/
   git commit -m "cycle-NN: 05-analyze"
   ```
3. Jelezd a felhasználónak a következő lépést és a fázis indító promptját:
   > *"Az analízis konzisztensnek találta a tervezési dokumentumokat. Folytathatjuk a 6. lépéssel (implement). Használd ezt a promptot:*
   > ```
   > Kövesd a `prompts/skills/06-implement.md` utasításait.
   > Input: `specs/cycle-NN-<cycle-name>/tasks.md`
   > ```"*
   > **A válasz végén helyezd el az `analyze-report.md` közvetlen, kattintható linkjét.**

### FAIL

Van legalább egy `Must Fix` megállapítás.

Teendők **sorban**:
1. Írd a `analyze-report.md` státuszát `FAIL`-re, a `Must Fix` listával és a visszalépési célokkal.
2. Határozd meg a visszalépési célfázist a kategória → fázis leképezés szerint (több FAIL esetén a legkorábbi fázis).
3. Fordítsd vissza a célfázis dokumentumának státuszát a nem-kész állapotra (`Piszkozat`).
4. Commitáld a fázis eredményét:
   ```bash
   git add specs/cycle-NN-<cycle-name>/
   git commit -m "cycle-NN: 05-analyze"
   ```
5. Jelezd a felhasználónak a visszalépést és a célfázis indító promptját, például:
   > *"Az analízis konzisztencia-hibákat talált. Részletek az `analyze-report.md`-ben. A `<célfázis dokumentum>` státuszát visszaállítottam `Piszkozat`-ra. Folytasd a `<célfázis>` fázissal:*
   > ```
   > Kövesd a `prompts/skills/0X-<fázis>.md` utasításait.
   > Input: `specs/cycle-NN-<cycle-name>/...`
   > ```"*
   > **A válasz végén helyezd el az `analyze-report.md` közvetlen, kattintható linkjét.**

---

## Kérdezési szabályok

- Csak **egy** kérdést tegyél fel egyszerre, várd meg a választ.
- Minden alkalommal, amikor kérdést teszel fel vagy jóváhagyást kérsz, a válaszod végén kötelezően helyezz el egy közvetlen, kattintható markdown linket az érintett fájlra.
