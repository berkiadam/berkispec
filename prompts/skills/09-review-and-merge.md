---
phase: 09
name: review-and-merge
description: "Használd a ciklus utolsó lépéseként (Phase 09), ha a kód és a dokumentáció is 'Kész'. Kódreview (reviewer, review-fixer subagentek) a 'code-review.md'-be, majd a branch beolvasztása a 'conventions.md' merge stratégiája szerint (PR nyitás vagy lokális merge)."
prerequisites:
  - "specs/cycle-NN-<name>/tasks.md státusz: Kész"
  - "specs/cycle-NN-<name>/plan.md státusz: Kész"
  - "specs/cycle-NN-<name>/spec.md státusz: Kész"
output:
  - "specs/cycle-NN-<name>/code-review.md"
  - "Merged cycle branch (lokális vagy PR, a conventions.md Merge stratégiája szerint)"
prev: 08-doc-sync
next: 02-write-spec
subagents:
  - "agents/reviewer.md"
  - "agents/review-fixer.md"
---

# 09 — Review és Merge

Spec driven development-ben fejlesztünk szoftvert. A fejlesztés ciklusokra van bontva. Minden ciklus egy önállóan lefejleszthető, önállóan tesztelhető részegysége a teljes implementációnak.

Ez a fejlesztési folyamat **9-es fázisa (a 0–9 fázisokból)**:
0. projekt inicializálás (setup)
1. ciklusok kezelése (setup)
2. spec
3. plan
4. tasks
5. analyze
6. implement
7. validate
8. doc-sync
9. **review & merge** ← most itt vagyunk

---

## Előfeltétel

1. **`conventions.md` létezés-ellenőrzés:** olvasd be a projekt gyökerében a `conventions.md`-t (különösen a `## Merge stratégia` szekciót). Ha nem létezik, STOP — térjenek vissza a `00` fázishoz.

2. **Munkafa ellenőrzés:** futtasd `git status --short`. Ha van commitálatlan változtatás, listázd, és kérdezd meg egy körben, hogy commitáljam-e most vagy folytassam — várj a válaszra. (A review a cycle branch git diffjét nézi a `master`-höz képest; tiszta munkafa nélkül a diff félrevezető.)

3. **Státusz-kapu:** a validate fázis (07) PASS esetén mindhárom fájl státuszát `Kész`-re állítja. Ellenőrizd:
   - `tasks.md` státusza: `Kész`
   - `plan.md` státusza: `Kész`
   - `spec.md` státusza: `Kész`

   Ha bármelyik nem `Kész` (pl. még `Validálásra kész` vagy visszaállított `Piszkozat`), a validálás még nem futott le sikeresen — térj vissza a `07` fázishoz.

4. **Doc-sync kapu:** a `08-doc-sync` fázisnak le kellett futnia a validált kódra. Ellenőrizd, hogy a ciklus `doc-sync-plan.md`-je létezik-e, nincs benne elvégzetlen `[ ]` tétel, nincs nyitott `doc-sync-questions.md` kérdés, és a DS22 kapu zöld volt. Ha ez nem igaz, térj vissza a `08-doc-sync` fázishoz.

---

## Feladatod

1. Automatikus code review futtatása a `reviewer` ágenssel.
2. Review hibák kezelése: FAIL esetén **nem** adod vissza a vezérlést a felhasználónak — **levezényelsz egy önjavító hurkot** (`review-fixer` → újra-validálás → újra-review), amíg a review tiszta és a validálás zöld nem lesz, vagy amíg a 3-próba / `max 5` backstop / eszkaláció meg nem állítja.
3. Merge előtti doc-sync ellenőrzés: ha a review-hurok vagy egy elfogadott review suggestion **kódot módosított**, futtasd újra a `08-doc-sync` fázist a végső kódra, és csak zöld DS22 kapu után folytasd.
4. Merge végrehajtása a `conventions.md` Merge stratégiája szerint (lokális squash vagy PR), **kötelező felhasználói megerősítés után** — a hurok soha nem automatizálja a merge-et (RD8).

**Szereped a review-ig diagnoszta-vezénylő, FAIL esetén orchestrátor.** A reviewer **read-only diagnoszta** marad (mint az analyzer); a javítást a `review-fixer` subagent (= a 06 Fix-módja) végzi; te review-zol, validálsz, naplózol, döntesz és státuszt fordítasz — a 07 mintájára. Lásd „Az önjavító hurok (orchestrátor-hurok)".

---

## 1. Automatikus review (Review Agent subagenttel)

A kód ellenőrzését egy dedikált subagent végzi el. Hajtsd végre a következőket:

1. Olvasd be a `prompts/agents/reviewer.md` rendszerpromptot.
2. Definiálj egy `reviewer` subagentet ezzel a rendszerprompttal.
3. Indítsd el a subagentet, átadva neki a cycle branch és a `master` branch közötti `git diff`-et, a `conventions.md`-t, a `plan.md`-t és a `spec.md`-t.
4. A subagent elkészíti a jelentést és elmenti a `specs/cycle-NN-<cycle-name>/code-review.md` fájlba.

> **Ha a subagent nem fut le, vagy nem készít `code-review.md`-t:** STOP. Ne merge-elj review nélkül. Jelezd a felhasználónak, hogy a review nem készült el, és kérdezd meg, hogy próbáljam-e újra a subagentet, vagy végezzem el a review-t közvetlenül a `reviewer.md` szempontjai szerint a fő ágensben.

5. Olvasd be a `code-review.md` fájlt és értékeld az eredményt:
   - **Ha a jelentés "Kritikus javítandók (Must Fix)" szekciójában vannak lezáratlan `- [ ]` checkboxok:** **nem** adod vissza a vezérlést a felhasználónak — **levezényelsz egy önjavító hurkot** (lásd „Az önjavító hurok (orchestrátor-hurok)"). A hurok a `Must Fix`-eket `## Review javítások` taskokká alakítja, és `review-fixer` → újra-validálás → újra-review iterációkkal javít, amíg a review tiszta és a validálás zöld nem lesz (vagy a 3-próba / `max 5` backstop / eszkaláció megállítja).
   - **Ha nincsenek kritikus hibák (csak javaslatok/ajánlások vannak vagy teljesen tiszta a jelentés):**
     A `Suggestions` szekció **nem blokkol**. Ha egy javaslat a ciklus scope-ján belül van és kockázat nélkül, gyorsan alkalmazható, javítsd direktben és commitold (`cycle-NN: 09-review - review suggestion`). Ha scope-on kívül esik vagy bizonytalan, hagyd a `Suggestions` listában jövőbeli ciklusnak — ne kezdj scope creep-et. Ha bármilyen kódmódosítás történt, a merge előtt futtasd újra a `08-doc-sync`-et (lásd §2). Ezután folytasd a merge folyamattal.

---

## Az önjavító hurok (orchestrátor-hurok)

`Must Fix` esetén **nem** adod vissza a vezérlést a felhasználónak. Levezényelsz egy iteratív, **kétfázisú** javító hurkot — `review-fixer` subagent → **újra-validálás (07 ellenőrzései)** → **újra-review (reviewer)** — amíg a review tiszta **és** a validálás zöld nem lesz, vagy amíg a **per-item 3-próba** / a **`max 5` globális backstop** / a **felfelé/humán menekülő ág** meg nem állítja.

A reviewer **read-only diagnoszta** marad (mint az analyzer); te (09) vagy az orchestrátor (mint a 07). A javítást a `review-fixer` subagent (= a 06 Fix-módja) végzi; te review-zol, validálsz, naplózol, döntesz és státuszt fordítasz. A meglévő FAIL-gépezet (`code-review.md`, `## Review javítások`, státusz-visszafordítás) megmarad — csak a korábbi „kézi visszaadás" lesz orchesztrált hurok.

### Miért kétfázisú (RD2)

Egy review-javítás **elronthat egy tesztet**, ezért a fix után **előbb újra-validálni** kell (07), és csak utána újra-review-zni — `review-fixer → re-validate → re-review`, nem `review-fixer → re-review`. Mindkét kapunak zöldnek kell lennie a továbblépéshez:
- a **re-validate** megfogja a review-fix okozta regressziót (különben tiszta review mellett tört teszttel mennénk merge-re);
- a **re-review** ellenőrzi, hogy a `Must Fix` valóban megszűnt-e.

A re-validate a `07-validate` **teljes** „Validálási lépések" szekcióját futtatja (összes teszt + Sonar + DoD — a regresszió-fogás miatt, nem célzott futtatás; RD2), de **nem** indítja a 07 saját önjavító hurkát: a fix-vezénylést itt a 09 hurka végzi (egyetlen aktív orchestrátor, egyetlen aktív próba-számláló — nincs egymásba akadó hurok).

### ⚠ Anti-„csalás" garde (RD4 — a hurok legfontosabb szabálya)

**A hurok a KÓDOT igazítja a reviewer findingjához ÉS a tesztekhez — SOHA nem fordítva.** TILOS:
- a `Must Fix` finding **kozmetikai elnémítása** a gyökérok javítása nélkül (lint-suppress komment, a kifogásolt kód álcázása);
- a re-validate „zöldítése" teszt-csalással (teszt gyengítése/skip/törlése, hardcode, DoD/spec leszállítása);
- a `code-review.md` `Must Fix` bejegyzésének törlése/átfogalmazása javítás nélkül.

Ezt a szabályt a `review-fixer` is megkapja (a 06 Fix-mód garde-ja). **Ha egy `Must Fix` csak a szerződés (teszt/DoD/spec) módosításával vagy a finding elnémításával lenne „zöld"** → az nem kód-fix → felfelé/humán menekülő ág (RD6).

### A hurok egy iterációja

1. **FAIL naplózása.** Írd a `code-review.md` `# Review History`-jába a futás eredményét: a megrekedt item(ek) pontos neve + a `Consecutive Failures for this item` számláló (előző egymás utáni hibák + 1).
2. **3-próba ellenőrzés (kilépés).** Ha bármely itemnél a `Consecutive Failures` eléri a **3**-at (a mostani iterációt is beleszámítva) → a hurok megáll (lásd „3-próba + globális backstop"). A megállás típusát az RD6 dönti el.
3. **Globális backstop ellenőrzés.** Ha az összes iteráció száma elérte a **`max 5`**-öt → STOP + humán (a `# Review History`-ra hivatkozva), akkor is, ha egyetlen item sem ért el 3 próbát.
4. **Korai eszkaláció-ellenőrzés (RD6).** Ha az előző iteráció `review-fixer`-e **eszkalációs jelzést** adott (a findinget csak a szerződés módosításával vagy elnémítással lehetne kezelni) → ne körözz tovább, azonnal a felfelé/humán menekülő ág.
5. **Javító-taskok felvétele.** A `tasks.md` végén `## Review javítások` szekció, a `code-review.md` prerequisite-tel; a konkrét `Must Fix`-ek `[GREEN]` taskként, a csoport végén `[CHECK]` ellenőrző taskkal. *(Review-javításnál `[RED]` pár nem kell — direkt javítás.)* Duplikátum-kerülés: ne vedd fel kétszer ugyanazt.
6. **Marker felvétele (RD7).** A `tasks.md` státuszát fordítsd `Implementálásra kész [review-loop]`-ra. A marker jelzi: fix-mód aktív → a fixer automatikusan lépteti a státuszt, megerősítés nélkül.
7. **`review-fixer` subagent indítása.** A konkrét `Must Fix`-listával + a `code-review.md` prerequisite-tel (lásd „A fixer-subagent indítása"). Ha a fixer eszkalációs jelzést ad → ugorj a 4. pontra.
8. **Re-validate (a 07 teljes ellenőrzései).** Futtasd a `07-validate` „Validálási lépéseit" (gyors tesztek → Sonar → nehéz tesztek → DoD). **Nem** indítod a 07 saját hurkát.
   - **FAIL** (regresszió) → ez is a hurok FAIL-je: új iteráció az 1. ponttól (a regresszált teszt lesz a megrekedt item).
9. **Re-review (reviewer subagent).** Ha a re-validate zöld, futtasd újra a `reviewer` subagentet a friss diffre, és olvasd be az új `code-review.md`-t.
   - **Tiszta** (nincs lezáratlan `Must Fix`) → a hurok konvergált: vedd le a `[review-loop]` markert (a `tasks.md` `Kész`), írd a `# Review History`-ba a `PASS`-t, egyetlen lezáró commit (RD9), majd lépj a merge előtti doc-sync ellenőrzésre (§2) és a merge-megerősítésre (§3).
   - **Még van `Must Fix`** → új iteráció az 1. ponttól.

### A fixer-subagent indítása

- A subagent **rendszerpromptja** az `agents/review-fixer.md` wrapper, amely a `06-implement.md` „Fix-mód" szekciójára delegál (a `## Review javítások` bemenettel) — nincs duplikált javító logika, a 06 minőségi szabályai automatikusan érvényesülnek.
- **Bemenet:** a `tasks.md` `## Review javítások` elvégzetlen taskjai + a `code-review.md` (findingok + `# Review History`).
- **Kimenet:** (a) az elvégzett javítások összefoglalója, és (b) **eszkalációs jelzés**, ha valamelyik findinget csak a szerződés módosításával vagy elnémítással lehetne kezelni (RD4). A subagent **nem** írja a `code-review.md`-t — azt te (az orchestrátor).

### Felfelé / humán menekülő ág (RD6 — JEL-VEZÉRELT)

Nem minden `Must Fix` kód-bug. A hurok **alapból minden findinget kód-fixként kezel**, és **csak konkrét jelre** eszkalál — nincs előzetes „ez vajon tervezési vita?" osztályozás (olcsó-LLM-biztos):

- **(b ág) Tervezési / szerződés-ügy → eszkaláció 03/02-re:** ha a `review-fixer` **explicit „szerződés-módosítás kéne" jelet** ad (a findinget csak a teszt/DoD/spec módosításával vagy elnémítással lehetne kezelni). Teendő, sorban: (1) naplózd a `# Review History`-ba, hogy szerződés-ügy miatt eszkalálsz; (2) fordítsd vissza az érintett tervezési dokumentum státuszát — `plan.md` → `Piszkozat` (ha a terv hibás), vagy `spec.md` → `Piszkozat` (ha a DoD/spec a hibás/ellentmondásos); a `tasks.md` a `[review-loop]` markerrel marad; (3) egyetlen lezáró commit (RD9); (4) jelezd a felhasználónak az átadást (a list2 tervezési hurokra; a folyamat a 05→06→07 úton tér vissza ide).
- **(c ág) Reviewer-ítélet vitája → STOP + humán:** ha a **per-item 3-próba kimerül** szerződés-jel NÉLKÜL (a fix nem konvergál, vagy a fixer vitatja a finding érvényességét), vagy a **`max 5` backstop** elér. Teendő: egyetlen lezáró commit (RD9); a `[review-loop]` marker + a `## Review javítások` a megrekedt állapot jelzésére marad; a 09 összefoglal + kérdez.
- **Bizonytalan / nem eldönthető → STOP + humán** (sosem néma tipp).

### 3-próba + globális backstop (RD5)

- **Elsődleges kilépés — per-item 3-próba:** ha a `# Review History` alapján bármely `Must Fix` itemnél vagy regresszált tesztnél a `Consecutive Failures for this item` eléri a **3**-at (a mostani iterációt is beleszámítva) → STOP a megrekedt elemnél (okosabb, mint egy globális számláló, mert pont a beragadt itemet fogja meg).
- **Másodlagos — globális backstop `max 5`:** a kétfázisú hurok runaway-kockázata ellen az összes iteráció felső határa `max 5`; elérve ugyanúgy STOP + humán, a `# Review History`-ra hivatkozva.

### Commit-stratégia a hurokban (RD9)

- **A hurokban nincs iterációnkénti commit** — egyetlen lezáró commit a hurok végén (tiszta review + zöld validálás / 3-próba STOP / backstop / eszkaláció):
  ```bash
  git add specs/cycle-NN-<cycle-name>/
  git commit -m "cycle-NN: 09-review"
  ```
- **Megszakítás-biztos:** a köztes commit hiányát a `# Review History` + a `[review-loop]` státusz-marker pótolja.

### „Hol járunk" a megállási üzenetekben

A user-felé tett megállási üzeneteknél (3-próba / backstop STOP, eszkaláció) jelezd, hol tart a hurok — a megrekedt itemet és a próbaszámot, a `# Review History`-ra hivatkozva:

```
[REVIEW · <Must Fix item> · próba 3/3]
<üzenet szövege>
```

A válaszod végén kötelezően helyezz el egy közvetlen, kattintható linket a `code-review.md`-re.

### Megszakított futás kezelése

A hurok bármikor megszakadhat. Újraindításkor **ne** kezdj tiszta lapról — derítsd ki a hurok állapotát (a 07 mintájára):
- Ha a `tasks.md` státusza `Implementálásra kész [review-loop]` markert visel, egy korábbi review-hurok szakadt meg.
- Olvasd be a `code-review.md` `# Review History`-t: melyik volt az utolsó FAIL, melyik a megrekedt item, és hány a `Consecutive Failures` (hányadik próbánál tartott) — a folytatáskor onnan számolj tovább, ne nullázd.
- Olvasd be a `tasks.md` `## Review javítások` szekcióját: vannak-e még elvégzetlen `[ ]` javító-taskok?
  - **Ha igen** (a fixer nem futott le vagy félbeszakadt): folytasd a fixer újraindításával ezekre a taskokra, majd re-validate → re-review.
  - **Ha nincs** (a fixer befejezte, de a re-validate/re-review maradt el): folytasd a re-validate-tel, és értékeld a hurok szerint.

---

## 2. Merge előtti doc-sync újrafuttatás (DS23.2)

A `08-doc-sync` és a `09-review` **független kapuk**. A reviewer kizárólag kód-findingot ad (`code-review.md`); a generált dokumentáció helyességét a `08-doc-sync` saját DS22 kapuja biztosítja.

Mivel a review-hurok a doc-sync után is módosíthat kódot, a merge előtt ellenőrizd:

1. **Változott-e kód a 09 review-hurok vagy direkt review suggestion miatt?**
   - Ha **nem**, nincs teendő: a normál `07 → 08 → 09` sorrend már konzisztens doksit adott.
   - Ha **igen**, indítsd újra a `08-doc-sync`-et a végső kódra:
     ```text
     Kövesd a `prompts/skills/08-doc-sync.md` utasításait.
     Input: `specs/cycle-NN-<cycle-name>`
     ```
2. Várd meg, amíg a `08-doc-sync` DS22 kapuja zöld, nincs nyitott `doc-sync-questions.md` kérdés, és a `doc-sync-plan.md` minden tétele pipált.
3. A doc-sync lefutása után térj vissza ide, és csak ezután kérj merge-megerősítést.

**Tilos** a generált doksik miatt `Must Fix` findingot gyártani vagy review-findingot doc-sync kérdésként átroutolni. Kód → `code-review.md` + `review-fixer`; doksi → `doc-sync-plan.md` / `doc-sync-questions.md` + DS22 kapu.

---

## 3. Merge — a conventions.md Merge stratégiája szerint

Olvasd be a `conventions.md` `## Merge stratégia` szekcióját, és a **Szolgáltató** mező alapján járj el. **Bármelyik ágon a merge előtt KÖTELEZŐ a felhasználói megerősítés** — a `master`-be merge és a branch törlése destruktív, megerősítés nélkül nem hajtható végre. Az önjavító hurok csak a „tiszta review + zöld validálás" állapotig automatikus; a merge-et **változatlanul kézi megerősítés** zárja (RD8), szemben a 07 auto-PASS-ával.

### Megerősítés (mindkét ágon kötelező)

Kérdezd meg, és **várj explicit megerősítésre**:
> *"A review tiszta, a doc-sync kapu zöld. Készen állok a merge-re a `<szolgáltató>` stratégia szerint (`feature/cycle-<cycle-name>` → `<target branch>`). Végrehajthatom?"*
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
git commit -m "cycle-NN: 09-merge - <cím>" -m "<cél és megközelítés a plan.md-ből>"

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

> *"A kódellenőrzés sikeres volt, a doc-sync kapu zöld, és a ciklust lezártam a `conventions.md` Merge stratégiája szerint (`<lokális squash merge` / `PR létrehozva>`). A ciklus sikeresen lezárult.*
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
