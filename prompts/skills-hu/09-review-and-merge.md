---
phase: 09
name: bs-review-and-merge
description: "berkispec - 09. Használd a ciklus utolsó lépéseként (Phase 09), ha a kód, a review és a dokumentáció is 'Kész', ÉS a conventions.md '## Review and merge' szekciójában 'PR submission: no'. Egyetlen skill: a fő branch behozása a ciklus ágába → post-merge teszt-kör (VP2: tesztek + Sonar) → beolvasztás kötelező felhasználói megerősítéssel (RD8) → roadmap-lezárás. PR-kötelezettség esetén hibát ad, és a bs-create-pr → bs-review → bs-merge láncra irányít."
prerequisites:
  - "specs/cycle-NN-<name>/tasks.md státusz: <status:done>"
  - "specs/cycle-NN-<name>/plan.md státusz: <status:done>"
  - "specs/cycle-NN-<name>/spec.md státusz: <status:done>"
  - "specs/cycle-NN-<name>/test-report/code-review.md — nincs lezáratlan Must Fix (a 07 review-kapuja)"
  - "conventions.md `## <sec:cv_review_and_merge>` — `PR submission: no` (különben STOP, L13-D1)"
output:
  - "specs/cycle-NN-<name>/test-report/post-merge/ — a VP2 kör bizonyítéka (siker és bukás egyaránt)"
  - "specs/cycle-NN-<name>/cycle-status.md — generált ciklus-státusz (L13-D9)"
  - "Merged cycle branch (lokális merge a conventions.md Merge stratégiája szerint)"
  - "specs/roadmap.md — a ciklus lezártként jelölve"
prev: bs-doc-sync
next: bs-write-spec
scripts:
  - "scripts/run-tests.py — a VP2 kör futtatása a plan gépi táblájából (--phase post-merge)"
  - "scripts/sonar-gate.py — a VP2 kör statikus rétege, változatlan küszöbökkel"
  - "scripts/report-gate-check.py — a VP2 kör riport-artefaktumai (TR3)"
  - "scripts/test-manager.py — opcionális test manager feltöltés (TM4/TM6)"
  - "scripts/notify.py — értesítés bukásnál (CS6/L13-D11)"
  - "scripts/cycle-status.py — a generált cycle-status.md (--write)"
---
# 09 — Review and merge (izolált út, PR nélkül)
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

Spec driven development-ben fejlesztünk szoftvert. A fejlesztés ciklusokra van bontva. Minden ciklus egy önállóan lefejleszthető, önállóan tesztelhető részegysége a teljes implementációnak.

Ez a folyamat **9. fázisa (0–9)**: 0-init · 1-ciklusok · 2-spec · 3-plan · 4-tasks · 5-analyze · 6-implement · 7-validate (tesztek + review) · 8-doc-sync · **9-review-and-merge ←**.

> **A kódreview NEM ebben a fázisban van (RV1).** A `reviewer` subagent és a review önjavító hurka a **`07-validate`** fázisba került. Mire idejutsz, a review már tiszta — ebben a skillben a *review* az **emberi jóváhagyás** (RD8), nem egy újabb agent-futás.

> **🔴 Három bizonyítási pont van (VP1–VP3), és ez a fázis a másodikat futtatja.** A `07` (`VP1`) azt bizonyította, hogy **funkcionálisan az készült el**, ami a spec-ben van — a ciklus ágán, a régi alapon. A **`VP2`** azt bizonyítja, hogy **a fő branch-csel egyesítve** is a spec szerint működik. A `VP3` (`bs-dev-test`) ezen az úton nem értelmes (az a központosított út opciója).

---

## <field:f_prerequisite>

0. **Ciklus-beazonosítás:** ha a felhasználó megadott ciklust/fájlt, azt használd; különben a legfrissebb `specs/cycle-*` mappát ajánld fel megerősítésre — <!-- INCLUDE:lang/common.md#ciklus-beazonositas --> — és várj a válaszra, mielőtt továbblépsz.

1. **`conventions.md` létezés-ellenőrzés:** olvasd be a projekt gyökerében a `conventions.md`-t — a `## <sec:cv_merge_strategy>` és a `## <sec:cv_review_and_merge>` szekciót. Ha nem létezik, STOP — térjenek vissza a `00` fázishoz.

1.b **🔴 Topológia-kapu (L13-D1) — ez az egyetlen kemény kikényszerítés ebben a családban.** A `## <sec:cv_review_and_merge>` szekció `PR submission` mezője dönt:
   - **`no`** → ez a helyes skill, folytasd.
   - **`yes`** → **STOP, hiba.** Ez a skill csak PR nélküli (osztatlan) üzemmódban használható: <!-- INCLUDE:lang/09-merge.md#L13-D1-pr-kotelezo --> Ne kerüld meg a PR-t — a `main`-re nyomott kód utólag nem vonható vissza, és a PR megkerülése **policy-sértés**, nem kényelmi kérdés.
   - **`n/a` (No-VCS projekt, BD11/L13-D20)** → ebben a projektben a ciklus a `08-doc-sync` után lezárul: a merge-család egyetlen skillje sem fut. Jelezd, zárd le a roadmap-en a ciklust, és állj meg.

2. **Munkafa-ellenőrzés:** futtasd `git status --short`. Ha van commitálatlan változtatás, listázd, és kérdezd meg egy körben, hogy commitáljam-e most vagy folytassam — várj a válaszra. A ciklus **saját feature branch-én** dolgozol; a fő branch-re váltás majd a Merge lépésben, felhasználói megerősítés után történik (RD8) — itt ne válts.

2.b **Worktree-helyzet (W1):** ez a fázis a fő branch-re vált, ezért **a `main`-t tartalmazó worktree-ben kell futnia**. Ellenőrizd:

   ```bash
   git worktree list
   git rev-parse --git-common-dir     # ha nem `.git`, linked worktree-ben vagyunk
   ```

   - **Egyetlen worktree** → nincs teendő, a lenti lépések változatlanul jók.
   - **Linked worktree-ben vagyunk** → **STOP.** A `git switch main` itt megtagadva lesz („already used by worktree"). A `06`–`09` szakasz a **fő** worktree-ben fut: a ciklust oda kell visszaköltöztetni (`git worktree remove ../<ciklus-worktree>`, majd a fő worktree-ben `git switch feature/cycle-NN-<cycle-name>`), és onnan folytatni. A commitálatlan tartalmat előbb commitold — `--force`-ot **ne** használj.
   - **Van egy MÁSIK worktree `cycle-*` branch-en** → az egy párhuzamosan tervezett ciklus. Ez a merge-et **nem** blokkolja (a másik ciklus a `05`-ig van), de a merge után szólj: a másik ciklusnak a `06` előtt be kell hoznia a friss `main`-t és újra kell futtatnia az `05`-öt (PW2).

3. **Státusz-kapu:** a validate fázis (07) PASS esetén mindhárom fájl státuszát `<status:done>`-re állítja. Ellenőrizd:
   - `tasks.md` státusza: `<status:done>` — és **nincs rajta `[validate-loop]` marker** (a marker megrekedt hurkot jelent)
   - `plan.md` státusza: `<status:done>`
   - `spec.md` státusza: `<status:done>`

   Ha bármelyik nem `<status:done>`, a validálás még nem futott le sikeresen — térj vissza a `07` fázishoz.

4. **Review-kapu (RV1):** a `specs/cycle-NN-<name>/test-report/code-review.md`-nek léteznie kell, és **nem lehet benne lezáratlan `- [ ]` a `<sec:critical_fixes>` szekcióban**. Ha hiányzik vagy van nyitott `<status:must_fix>`, a 07 review-kapuja nem zárult le — **STOP**, térj vissza a `07` fázishoz. **Ne merge-elj review nélkül**, és ne futtasd le itt a review-t „gyorsan": az a 07 dolga, a saját javító hurkával és leállási korlátaival.

5. **Doc-sync kapu:** a `08-doc-sync` fázisnak le kellett futnia a validált kódra. Ellenőrizd, hogy a ciklus `doc-sync-plan.md`-je létezik-e, nincs benne elvégzetlen `[ ]` tétel, nincs nyitott `doc-sync-questions.md` kérdés, és a DS22 kapu zöld volt. Ha ez nem igaz, térj vissza a `08-doc-sync` fázishoz.

---

## Feladatod

A ciklus lezárása **négy lépésben, kötött sorrendben** (L13-D14):

1. **Merge előtti doc-sync ellenőrzés** (DS23.2) — változott-e kód a `08` óta.
2. **Integrációs frissítés:** a fő branch **behozása a ciklus ágába** (rebase vagy merge, W2/RM5).
3. **`VP2` — post-merge teszt-kör a ciklus ágán**, a friss fő branch-csel egyesített kódon: tesztek + Sonar + riport-kapu.
4. **Beolvasztás** kötelező felhasználói megerősítés után (RD8), majd **a ciklus ágának törlése**, roadmap-lezárás és a generált `cycle-status.md`.

> **🔴 A sorrend nem felcserélhető.** A `VP2` a beolvasztás **előtt** fut, a ciklus ágán. Ha fordítva tennénk, a bukás pillanatában a `main`-en már ott állna a ciklus teljes diffje, és a javítás visszavezetése egy **második** squash merge lenne. Így viszont bukásnál a `main` **érintetlen**, a javítás a ciklus ágán megy, és a beolvasztás egyszer történik.

Ebben a fázisban **nincs önjavító hurok és nincs subagent**: ha a merge előtti ellenőrzések bármelyike bukik, a helyes lépés a visszairányítás a `07`-re vagy a `08`-ra, nem a helyben javítás.

---

## 1. Merge előtti doc-sync ellenőrzés (DS23.2)

A `08-doc-sync` és a `07` review-kapuja **független kapuk**. A reviewer kizárólag kód-findingot ad (`test-report/code-review.md`); a generált dokumentáció helyességét a `08-doc-sync` saját DS22 kapuja biztosítja.

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
3. A doc-sync lefutása után térj vissza ide.

**Tilos** itt bármilyen kód-findingot gyártani vagy a doc-syncet review-vá alakítani: kód → a `07` review-kapuja; doksi → `doc-sync-plan.md` / `doc-sync-questions.md` + DS22 kapu.

---

## 2. Integrációs frissítés — a fő branch behozása a ciklus ágába (W2 / RM5)

A `07` zöld tesztjei és a `08` doksija **azon az alapon** készültek, ahonnan a ciklus ága elágazott. Ha a fő branch időközben előrement, a beolvasztás egy **soha nem tesztelt kombinációt** hozna létre:

```bash
git fetch origin
git log --oneline HEAD..origin/main
```

_Remote nélküli (csak lokális) repóban az `origin/main` helyett a lokális `main`-nel dolgozz, `git fetch` nélkül. A `main` helyére a `conventions.md` `## <sec:cv_git_conventions>` **<field:f_main_branch>** mezője kerül._

_A parancsban **szándékosan nincs `$( )` behelyettesítés**: a `HEAD..origin/main` ugyanazt a commit-halmazt adja, mint a `merge-base`-es alak, viszont több CLI (pl. Antigravity/Gemini) a parancs-behelyettesítést biztonsági okból nem engedi allowlistelni — az ilyen sor minden futásnál engedélyt kérne._

- **Üres lista → a fő branch NEM ment előre.** Ilyenkor a `## <sec:cv_review_and_merge>` `Skip post-merge tests if master unchanged` mezője dönt (RM11):
  - **`yes`** → a `VP2` kör **kihagyható**: ugyanazt mérné, amit a `07` az imént lemért, ugyanazon a kódon. **A kihagyás nem maradhat jelöletlen** — írd be a `test-report/post-merge/skipped.md` fájlba egy sorban, hogy *„VP2 kihagyva: a fő branch nem ment előre a ciklus ága óta (`git log HEAD..origin/main` üres), `Skip post-merge tests if master unchanged: yes`"*, a fő branch SHA-jával együtt. Ugorj a 4. lépésre.
  - **`no`** → a `VP2` kör akkor is lefut (3. lépés).
  - _(Kereszt-ellenőrzés: az `analyze-report.md` **<field:f_validated_base>** mezőjének fő branch SHA-ja is ezt mutatja-e — ha nem, az `05` egy régebbi alapon zárult, és a lenti újravalidálási szabály érvényes.)_
- **Nem üres → be kell hozni a fő branch-et a ciklus ágába:**

1. **Behozás** (ugyanaz a mechanika, mint az `05` BR1 lépése). A választás nem ízlés kérdése:
   - a branch **nincs pusholva / nincs rá PR** (`git rev-parse --verify origin/feature/cycle-NN-<cycle-name>` hibát ad) → `git rebase origin/main` (lineáris előzmény; a `cycle-NN: <fázis>` commit-üzenetek megmaradnak, tehát a `git log --grep` alapú keresések működnek),
   - a branch **pusholva van** → `git merge origin/main` a ciklus ágba (a rebase force-push-t igényelne).
   - Ütközés esetén a lenti *Merge conflict kezelése* szabályai érvényesek — a generált doksit (`docs-generated/`) és a `specs/test-conventions.md`-t **ne** kézzel oldd fel: azokat a `08` újrafuttatása állítja helyre.
2. **Újravalidálás a behozott alap szerint.** A behozás ELŐTT jegyezd fel a ciklus ágának csúcsát (`PRE=$(git rev-parse HEAD)`), utána nézd meg, mi jött be: `git diff --name-only "$PRE" HEAD`. A találatok jellege szerint:
   - **forráskód vagy teszt változott** → a `VP2` kör (3. lépés) **kötelező**. Ha a behozott változás a ciklus hatókörét érinti (ugyanazok a fájlok, ugyanaz a szerződés), **STOP**, vissza a `07`-re a friss alapon; a `07` PASS-a után térj vissza ide.
   - **csak `docs-generated/`, `conventions.md` vagy `specs/test-conventions.md` változott** → **STOP**, vissza a `08`-ra. Zöld DS22 kapu után térj vissza ide.
   - **csak más ciklusok `specs/cycle-MM-*/` mappái változtak** → nincs teendő, folytasd a `VP2` körrel.

**Ne kérj engedélyt a behozásra külön** (a ciklus saját ágán dolgozol, ez nem destruktív) — de a `07`/`08` visszairányítást **mindig jelezd**, mert az fázisváltás.

---

## 3. `VP2` — post-merge teszt-kör a ciklus ágán

Akkor fut, ha a `## <sec:cv_review_and_merge>` `Post-merge tests` mezője `yes`, és a 2. lépés nem hagyta ki (RM11). **A kör a ciklus ágán fut, a friss fő branch-csel egyesített kódon, a beolvasztás ELŐTT.**

> **Lokális futtatás — nem kötelező a konténerizáltság (RM10).** Ezen az úton minden a fejlesztő gépén fut, tehát a `VP2` kör tesztjeinek **nem** kell teljesen konténerizálhatónak lenniük (az a központosított út követelménye, `CS4`).

<!-- INCLUDE:shared/python-cmd.md -->

### 3/a. Tesztek — a plan gépi táblájából, `post-merge` fázis-szűrővel

```bash
python3 <platform-scripts-mappa>/run-tests.py \
  specs/cycle-NN-<cycle-name>/plan.md \
  --round-dir specs/cycle-NN-<cycle-name>/test-report/post-merge \
  --phase <status:phase_post_merge>
```

- **`exit 0`** → a kör zöld, a `results.json` és a riport-artefaktumok a `test-report/post-merge/` mappában.
- **`exit 1`** → bukás → *A `VP2` bukása* szekció.
- **`MEGJEGYZÉS (PH1)` sor „nincs mit futtatni"** → a plan táblájának egyetlen sora sem visel `<status:phase_post_merge>` értéket, miközben a `conventions.md` bekapcsolta a kört. **Ez nem „nincs teendő", hanem terv-hiány:** STOP, és kérdezd meg a felhasználót, mely kategóriák tartoznak a merge utáni körbe — a válasz a `plan.md` gépi táblájának `<field:f_phase>` oszlopába kerül (a `conventions.md`/`plan.md` javítása ilyenkor a ciklus része, GC1).
- **`exit 2/3/4`** → ugyanaz a jelentés, mint a `07`-ben (hiányzó gépi tábla / helyőrző-hiba / környezet-hiba): a `03` hiánya, nem kód-bug.

### 3/b. Sonar — a kör statikus rétege

**A Sonar a post-merge körnek is része, ugyanúgy, ahogy a `07`-ben** — mindkét üzemmódban, nem csak CI/CD-ben. Az egyesítés **új kódot hoz be** a ciklus ágába, amit a `07` Sonar-köre **sosem látott**: a statikus hibák ugyanúgy keletkezhetnek az egyesítésből, mint a futásidejűek. Nulla új gépezet — ugyanaz a script, ugyanazok a `conventions.md` küszöbök:

```bash
python3 <platform-scripts-mappa>/sonar-gate.py \
  --out specs/cycle-NN-<cycle-name>/test-report/post-merge/sonar-report.md
```

A kilépő kód dönt (`0` OK · `1` finding miatti FAIL · `3` küszöb miatti FAIL, QG1 · `2` használati hiba) — pontosan úgy, ahogy a `07` 2/a lépésében. Ha a `conventions.md`-ben nincs `## <sec:cv_sonar>` szekció, ez a lépés kimarad.

### 3/c. Riport-kapu

```bash
python3 <platform-scripts-mappa>/report-gate-check.py \
  conventions.md specs/cycle-NN-<cycle-name> \
  --report-subdir test-report/post-merge
```

A kapu akkor kéri számon a `conventions.md` TR3 táblájának artefaktumait, ha a `**<field:f_report_phases>:**` mező felsorolja a `post-merge` fázist. **Siker és bukás egyaránt nyomot hagy:** a `test-report/post-merge/` készlet a ciklus mappájába és ágába kerül, commitolva — így utólag megkülönböztethető a *lefutott és zöld volt* a *ki sem próbálták* esettől.

### 3/d. Test manager (opcionális, TM4)

Ha a `conventions.md` `## <sec:cv_test_reporting>` szekciójában a `**<field:f_test_manager_phases>:**` mező felsorolja a `post-merge` fázist:

```bash
python3 <platform-scripts-mappa>/test-manager.py --mode preflight --phase post-merge \
  --round-dir specs/cycle-NN-<cycle-name>/test-report/post-merge          # a teszt-kör ELŐTT
python3 <platform-scripts-mappa>/test-manager.py --mode publish --phase post-merge \
  --round-dir specs/cycle-NN-<cycle-name>/test-report/post-merge          # a teszt-kör UTÁN
```

A kimenet utolsó sora `TEST_MANAGER_RUN_URL=<url>`. **A feltöltés nem bizonyíték** (TM7): a ciklus bizonyítéka a commitolt riport-készlet marad, a URL csak pointer. `exit 3` = a fázis nincs a listán (kihagyva, nem hiba); `exit 4` = a feltöltés bukott — ez alapból **nem** buktatja a kört (`**<field:f_test_manager_required>:**` `nem`), de a riportba egy sor kerül róla.

### A `VP2` bukása

A bukás **nem visszanyitás**, hanem a még nyitott ciklus folytatása (L13-D8):

1. A bizonyíték már a helyén van (`test-report/post-merge/`) — **ne töröld, ne írd felül**.
2. **Értesítés** (`Failure handling: notify`, az alapértelmezés):
   ```bash
   python3 <platform-scripts-mappa>/notify.py --phase post-merge \
     --cycle specs/cycle-NN-<cycle-name> --status fail
   ```
   Ha a `Notification channel` `none`, ez a lépés kimarad.
3. **Döntés — kié a hiba?** Ez emberi döntés, a riport alapján:
   - **ehhez a ciklushoz tartozik** → a javítás a `tasks.md` **`## <sec:post_merge_fixes>`** szekciójába kerül, és a meglévő gépezet fut rá: `/bs-implement` (fix-mód) → `/bs-validate`, majd vissza ide a 2. lépéstől. A ciklus ága **él**, a `main` érintetlen.
   - **nem ehhez a ciklushoz tartozik** (másik ciklus regressziója, környezeti hiba) → **új ciklus** indul rá (`/bs-add-cycles`), és ez a ciklus lezárható. Mondd ki a riportban, miért.
4. Regeneráld a `cycle-status.md`-t (lásd az 5. lépést), és állj meg.

---

## 4. Beolvasztás — a conventions.md Merge stratégiája szerint

Csak akkor, ha a `VP2` **zöld volt** (vagy a `Post-merge tests: no` / RM11-kihagyás miatt nem futott).

Olvasd be a `conventions.md` `## <sec:cv_merge_strategy>` szekcióját, és a **<field:f_provider>** mező alapján járj el. **A merge előtt KÖTELEZŐ a felhasználói megerősítés** (RD8) — a fő branch-be merge és a branch törlése destruktív, megerősítés nélkül nem hajtható végre.

### Megerősítés (kötelező)

Kérdezd meg, és **várj explicit megerősítésre**:
<!-- INCLUDE:lang/09-merge.md#RD8-merge-megerosites -->
> **A válasz végén helyezd el a `test-report/validation-report.md`, a `test-report/code-review.md` és — ha volt `VP2` kör — a `test-report/post-merge/` közvetlen, kattintható linkjét.**

Ne lépj tovább a megerősítés előtt.

### A beolvasztás

Megerősítés után:
```bash
# 1. Válts át a fő branch-re (a conventions.md `## <sec:cv_git_conventions>`
#    <field:f_main_branch> mezője, ill. a `## <sec:cv_merge_strategy>` PR target — alapból `main`)
git switch main

# 2. Squash merge a ciklus ágáról
git merge --squash feature/cycle-NN-<cycle-name>

# 3. Commit a ciklus címével és a plan célkitűzésével
git commit -m "cycle-NN: 09-merge - <cím>" -m "<cél és megközelítés a plan.md-ből>"

# 4. A lokális ciklus ág törlése — CSAK a zöld VP2 UTÁN (L13-D7)
git branch -D feature/cycle-NN-<cycle-name>
```

> **🔴 A ciklus ágát a verifikáció mögött töröld.** Az izolált úton a `VP2` és minden javító köre **ugyanazon az ágon** fut — ha a merge után azonnal törölnénk, a bukás bizonyítékának és a javításnak nem maradna járműve. A törlés ezért az utolsó lépés.

> **W3 — ha a ciklus ága még ki van csekkolva egy worktree-ben**, a `git branch -D` megtagadja („used by worktree"). Ilyenkor előbb `git worktree remove <útvonal>` (commitálatlan tartalom esetén előbb commit, `--force` nélkül), és csak utána töröld a branch-et. Elhagyott bejegyzést a `git worktree prune` rendez.

### Merge conflict kezelése

Ha a merge során ütközés (merge conflict) lép fel:
1. **NE találd ki a feloldást.** Listázd ki az ütköző fájlokat (`git status`).
2. Minden ütköző fájlnál nézd meg mindkét oldalt (a fő branch és a cycle branch verzióját), és a `plan.md` / `spec.md` alapján döntsd el, melyik a helyes — vagy hogy a kettő összefésülése kell-e.
3. Ha a feloldás egyértelmű a ciklus szándéka alapján, oldd fel, futtasd újra a releváns ellenőrzést, majd commitold.
4. **Ha a feloldás nem egyértelmű** (mindkét oldal érdemi, ütköző logikát tartalmaz), STOP — jelezd a felhasználónak az ütköző fájlokat és a két oldalt, és kérj döntést.

---

## 5. Roadmap, cycle-status és lezárás

**A ciklus akkor kész, ha az UTOLSÓ engedélyezett verifikáció zöld** (L13-D8). Ezen az úton ez a `VP2` (vagy a `07`, ha a `Post-merge tests: no`) — tehát a beolvasztás után a ciklus **valóban lezárható**.

1. **Roadmap:** jelöld a ciklust lezártként a `specs/roadmap.md`-ben (`✅` / `(kész)`), és commitold.
2. **Generált ciklus-státusz** (L13-D9/L13-D15):
   ```bash
   python3 <platform-scripts-mappa>/cycle-status.py specs/cycle-NN-<cycle-name> --write
   ```
   A `cycle-status.md` **generált fájl, nem kézzel írt**: rendering a bizonyítékból, sosem forrás — kapu soha nem olvassa. Commitold a roadmap-frissítéssel együtt.
3. Jelezd a felhasználónak a ciklus lezárását és a következő ciklus indító promptját:

<!-- INCLUDE:lang/09-merge.md#zaro-uzenet -->
