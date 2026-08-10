---
phase: 09
name: bs-merge
description: "berkispec - 09. Használd a ciklus utolsó lépéseként (Phase 09), ha a kód, a review és a dokumentáció is 'Kész'. A ciklus branch beolvasztása a 'conventions.md' merge stratégiája szerint (PR nyitás vagy lokális merge), kötelező felhasználói megerősítéssel."
prerequisites:
  - "specs/cycle-NN-<name>/tasks.md státusz: Kész"
  - "specs/cycle-NN-<name>/plan.md státusz: Kész"
  - "specs/cycle-NN-<name>/spec.md státusz: Kész"
  - "specs/cycle-NN-<name>/test-report/code-review.md — nincs lezáratlan Must Fix (a 07 review-kapuja)"
output:
  - "Merged cycle branch (lokális vagy PR, a conventions.md Merge stratégiája szerint)"
  - "specs/roadmap.md — a ciklus lezártként jelölve"
prev: bs-doc-sync
next: bs-write-spec
---
# 09 — Merge
<!-- INCLUDE:shared/context-check.md -->

---

Spec driven development-ben fejlesztünk szoftvert. A fejlesztés ciklusokra van bontva. Minden ciklus egy önállóan lefejleszthető, önállóan tesztelhető részegysége a teljes implementációnak.

Ez a folyamat **9. fázisa (0–9)**: 0-init · 1-ciklusok · 2-spec · 3-plan · 4-tasks · 5-analyze · 6-implement · 7-validate (tesztek + review) · 8-doc-sync · **9-merge ←**.

> **A kódreview NEM ebben a fázisban van (RV1).** A `reviewer` subagent és a review önjavító hurka a **`07-validate`** fázisba került: ott a review a teljes kör 4. lépése, és a findingok ugyanabba a hurokba, ugyanazokba a leállási korlátokba futnak be, mint a teszthibák. Mire idejutsz, a review már tiszta — ez a fázis **kizárólag a beolvasztásról** szól.

---

## Előfeltétel

0. **Ciklus-beazonosítás:** ha a felhasználó megadott ciklust/fájlt, azt használd; különben a legfrissebb `specs/cycle-*` mappát ajánld fel megerősítésre — *"A(z) `specs/cycle-NN-<name>` ciklussal szeretnél dolgozni? Igen / Nem (megadom a ciklust)"* — és várj a válaszra, mielőtt továbblépsz.

1. **`conventions.md` létezés-ellenőrzés:** olvasd be a projekt gyökerében a `conventions.md`-t (különösen a `## Merge stratégia` szekciót). Ha nem létezik, STOP — térjenek vissza a `00` fázishoz.

2. **Munkafa-ellenőrzés (csak VCS esetén):** futtasd `git status --short`. Ha van commitálatlan változtatás, listázd, és kérdezd meg egy körben, hogy commitáljam-e most vagy folytassam — várj a válaszra. A ciklus **saját feature branch-én** dolgozol; a fő branch-re váltás majd a Merge lépésben, felhasználói megerősítés után történik (RD8) — itt ne válts. (No-VCS projektben kimarad.)

3. **Státusz-kapu:** a validate fázis (07) PASS esetén mindhárom fájl státuszát `Kész`-re állítja. Ellenőrizd:
   - `tasks.md` státusza: `Kész` — és **nincs rajta `[validate-loop]` marker** (a marker megrekedt hurkot jelent)
   - `plan.md` státusza: `Kész`
   - `spec.md` státusza: `Kész`

   Ha bármelyik nem `Kész` (pl. még `Validálásra kész` vagy visszaállított `Piszkozat`), a validálás még nem futott le sikeresen — térj vissza a `07` fázishoz.

4. **Review-kapu (RV1):** a `specs/cycle-NN-<name>/test-report/code-review.md`-nek léteznie kell, és **nem lehet benne lezáratlan `- [ ]` a `Kritikus javítandók (Must Fix)` szekcióban**. Ha hiányzik vagy van nyitott `Must Fix`, a 07 review-kapuja nem zárult le — **STOP**, térj vissza a `07` fázishoz. **Ne merge-elj review nélkül**, és ne futtasd le itt a review-t „gyorsan": az a 07 dolga, a saját javító hurkával és leállási korlátaival.

5. **Doc-sync kapu:** a `08-doc-sync` fázisnak le kellett futnia a validált kódra. Ellenőrizd, hogy a ciklus `doc-sync-plan.md`-je létezik-e, nincs benne elvégzetlen `[ ]` tétel, nincs nyitott `doc-sync-questions.md` kérdés, és a DS22 kapu zöld volt. Ha ez nem igaz, térj vissza a `08-doc-sync` fázishoz.

---

## Feladatod

1. **Merge előtti doc-sync ellenőrzés:** ha a `08-doc-sync` lezárása óta változott kód, futtasd újra a doc-syncet a végső kódra, és csak zöld DS22 kapu után folytasd.
2. **Merge végrehajtása** a `conventions.md` Merge stratégiája szerint (lokális squash vagy PR), **kötelező felhasználói megerősítés után** (RD8) — a merge soha nem automatikus.
3. **Roadmap lezárása** és a következő ciklus indító promptjának megadása.

Ebben a fázisban **nincs önjavító hurok és nincs subagent**: ha a merge előtti ellenőrzések bármelyike bukik, a helyes lépés a visszairányítás a `07`-re vagy a `08`-ra, nem a helyben javítás.

---

## 1. Merge előtti doc-sync ellenőrzés (DS23.2)

A `08-doc-sync` és a `07` review-kapuja **független kapuk**. A reviewer kizárólag kód-findingot ad (`test-report/code-review.md`); a generált dokumentáció helyességét a `08-doc-sync` saját DS22 kapuja biztosítja.

Normál esetben a `07 → 08 → 09` sorrend már konzisztens doksit ad: a review a 07-ben lezárult, tehát a 08 már a **végleges** kódot dokumentálta. A merge előtt mégis ellenőrizd:

1. **Változott-e kód a `08-doc-sync` lezáró commitja óta?**
   ```bash
   BASE=$(git log --format=%H -1 --grep="^cycle-NN: 08-doc-sync")
   git diff --name-only "$BASE" HEAD
   ```
   - Ha **nem** (üres lista, vagy csak `specs/` alatti útvonalak), nincs teendő.
   - Ha **igen**, indítsd újra a `08-doc-sync`-et a végső kódra:
     ```text
     /bs-doc-sync input: @specs/cycle-NN-<cycle-name>
     ```
2. Várd meg, amíg a `08-doc-sync` DS22 kapuja zöld, nincs nyitott `doc-sync-questions.md` kérdés, és a `doc-sync-plan.md` minden tétele pipált.
3. A doc-sync lefutása után térj vissza ide, és csak ezután kérj merge-megerősítést.

**Tilos** itt bármilyen kód-findingot gyártani vagy a doc-syncet review-vá alakítani: kód → a `07` review-kapuja; doksi → `doc-sync-plan.md` / `doc-sync-questions.md` + DS22 kapu.

---

## 2. Merge — a conventions.md Merge stratégiája szerint

Olvasd be a `conventions.md` `## Merge stratégia` szekcióját, és a **Szolgáltató** mező alapján járj el. **Bármelyik ágon a merge előtt KÖTELEZŐ a felhasználói megerősítés** — a `master`-be merge és a branch törlése destruktív, megerősítés nélkül nem hajtható végre. A `07` PASS-a (zöld tesztek + tiszta review) automatikus; a merge-et viszont **változatlanul kézi megerősítés** zárja (RD8).

### Megerősítés (mindkét ágon kötelező)

Kérdezd meg, és **várj explicit megerősítésre**:
> *"A validálás és a review tiszta (07), a doc-sync kapu zöld. Készen állok a merge-re a `<szolgáltató>` stratégia szerint (`feature/cycle-NN-<cycle-name>` → `<target branch>`). Végrehajthatom?"*
> **A válasz végén helyezd el a `test-report/validation-report.md` és a `test-report/code-review.md` közvetlen, kattintható linkjét.**

Ne lépj tovább a megerősítés előtt.

### A) Lokális (nincs PR)

Megerősítés után:
```bash
# 1. Válts át a fő branch-re (a conventions.md `## Git és branching konvenciók`
#    Fő branch mezője, ill. a `## Merge stratégia` PR target — alapból `main`)
git switch main

# 2. Squash merge a ciklus ágáról
git merge --squash feature/cycle-NN-<cycle-name>

# 3. Commit a ciklus címével és a plan célkitűzésével
git commit -m "cycle-NN: 09-merge - <cím>" -m "<cél és megközelítés a plan.md-ből>"

# 4. A lokális ciklus ág törlése
git branch -D feature/cycle-NN-<cycle-name>
```

### B) GitHub / Bitbucket / GitLab (PR)

Megerősítés után hozd létre a PR-t a `conventions.md`-ben megadott szolgáltató szerint, a `conventions.md` target branchére. A PR description a `code-review.md` tartalma legyen:
- **GitHub:** `gh pr create --base <target> --head feature/cycle-NN-<cycle-name> --title "cycle-NN: <cím>" --body-file specs/cycle-NN-<cycle-name>/test-report/code-review.md`
- **GitLab:** `glab mr create --target-branch <target> --title "cycle-NN: <cím>" --description "$(cat specs/cycle-NN-<cycle-name>/test-report/code-review.md)"`
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

> *"A validálás és a kódreview a 07-ben sikeres volt, a doc-sync kapu zöld, és a ciklust lezártam a `conventions.md` Merge stratégiája szerint (`<lokális squash merge` / `PR létrehozva>`). A ciklus sikeresen lezárult.*
>
> *Megkezdhető a következő ciklus. Az új ciklus megkezdése előtt mindenképpen futtass egy `/clear` parancsot a kontextus kiürítéséhez.*
>
> *Új ciklus hozzáadásához:*
> ```
> /bs-add-cycles
> ```
> *Vagy ha a következő ciklus már a roadmap-en van, közvetlenül a spec fázissal:*
> ```
> /bs-write-spec input: @specs/roadmap.md, ciklus: cycle-NN-<cycle-name>
> ```"*