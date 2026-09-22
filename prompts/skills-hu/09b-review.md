---
phase: 09b
name: bs-review
description: "berkispec - 09b. Használd a PR megnyitása után (Phase 09b), a három lépéses (PR-es) ciklusvég második lépéseként. A PR diffjére futtatja a reviewer subagentet — központosított SDD-ben gépi futtatásban, a CI/CD-n, emberi beavatkozás nélkül —, és a 'test-report/ci-code-review.md'-be ír. A 07 lokális 'code-review.md'-jét SOHA nem írja felül."
prerequisites:
  - "Megnyitott PR a ciklus ágára (bs-create-pr lefutott)"
  - "specs/cycle-NN-<name>/test-report/code-review.md — nincs lezáratlan Must Fix (a 07 review-kapuja)"
  - "conventions.md `## <sec:cv_review_and_merge>` — `PR submission: yes`"
output:
  - "specs/cycle-NN-<name>/test-report/ci-code-review.md — a PR-en futtatott review findingjei (RV-INC, inkrementálisan írva)"
  - "specs/cycle-NN-<name>/review-questions.md — ha nem-interaktív módban döntés kell (exit 2)"
prev: bs-create-pr
next: bs-merge
subagents:
  - "agents/reviewer.md"
scripts:
  - "scripts/validate-gate-check.py — a befejezetlen review (RV-INC) kapuja"
  - "scripts/notify.py — értesítés nyitott Must Fix esetén (CS6)"
  - "scripts/cycle-status.py — a generált cycle-status.md (--write)"
shared:
  - "shared/review-checklist.md"
---
# 09b — Review a PR-en
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

Ez a ciklusvég **második lépése a három lépéses (PR-es) úton**: 9a-create-pr · **9b-review ←** · 9c-merge · (9d-dev-test).

> **Miért van második review, ha a `07`-ben már volt (RV1).** A `07` review-ja a **ciklus ágán, a régi alapon**, a fejlesztő gépén futott. Ez a kör a **PR-en** fut — a fő branch-csel szemben —, és központosított SDD-ben **gépi futtatásban, emberi beavatkozás nélkül** (`CS2`). A két kör **nem ugyanazt** a diffet nézi, ezért **két külön fájlba** ír.

> **🔴 A `07` bizonyítéka sérthetetlen.** Ez a skill a `test-report/ci-code-review.md`-be ír; a `test-report/code-review.md`-t **soha nem írja felül és nem szerkeszti**. A `bs-merge` belépő kapuja **mindkét fájlt** olvassa.

---

## <field:f_prerequisite>

0. **Ciklus-beazonosítás:** a bemenet a ciklus mappája (`input: @specs/cycle-NN-<cycle-name>`). Gépi futtatásban az adapter adja át — ne kérdezz vissza (lásd *Nem-interaktív szerződés*). Interaktív futtatásban a szokásos megerősítés: <!-- INCLUDE:lang/common.md#ciklus-beazonositas -->

1. **`conventions.md`:** `## <sec:cv_review_and_merge>` — ha a `PR submission` nem `yes`, ez a skill nem ide való: **STOP**, irány a `bs-review-and-merge`.

2. **PR-kapu:** létezik-e nyitott PR a ciklus ágára? (`gh pr view <branch> --json state,url` / `glab mr view` / a szolgáltató access-parancsa.) Ha nincs, **STOP** — előbb `bs-create-pr`.

3. **Review-kapu (RV1):** a `test-report/code-review.md` létezik, és nincs benne lezáratlan `- [ ]` a `<sec:critical_fixes>` szekcióban. Ha van, a `07` nem zárult le — **STOP**, vissza a `07`-re.

4. **Folytatás megszakadt futás után (RV-INC):** ha a `test-report/ci-code-review.md` fejlécében `<field:f_status>` = `<status:in_progress>` áll, a benne lévő findingok **valósak, csak hiányosak** — ne dobd el és ne írd felül őket, hanem folytasd a review-t onnan, ahol abbamaradt.

---

## Feladatod

1. **A review hatókörének meghatározása:** a PR diffje a target branch-hez képest.
2. **A `reviewer` subagent futtatása** erre a diffre, a közös szempontlistával.
3. **A findingok kiértékelése** és a verdikt — a kapuktól, nem az ágens önbevallásából.

<!-- INCLUDE:shared/review-checklist.md -->

---

## 1. A review hatóköre

```bash
git fetch origin
git diff --name-only origin/main...HEAD
```

_A `main` helyére a `conventions.md` `## <sec:cv_git_conventions>` **<field:f_main_branch>** mezője (ill. a PR target branche) kerül. A három pont (`...`) az elágazási pont óta a ciklus ágán keletkezett változást adja — pontosan azt, amit a PR mutat._

A `reviewer` subagent kontraktusa változatlan (`agents/reviewer.md`), két behelyettesítéssel:
- a **hatókör** a PR diffje (nem a ciklus-ág teljes története);
- a **kimeneti fájl** a `specs/cycle-NN-<cycle-name>/test-report/ci-code-review.md`.

---

## 2. A verdikt — a kapuktól, nem az ágenstől

> **🔴 Az ágens kilépő kódja nem verdikt.** A legtöbb CLI `0`-val lép ki akkor is, ha a munka rosszul sikerült. A fázis verdiktje ezért **determinisztikus kapuból** jön:

<!-- INCLUDE:shared/python-cmd.md -->

```bash
python3 <platform-scripts-mappa>/validate-gate-check.py \
  specs/cycle-NN-<cycle-name> --review-only
```

- **A `ci-code-review.md` fejléce `<status:in_progress>`** → a review **befejezetlen**: a kör sem zöldre, sem FAIL-re nem zárható (RV-INC). Folytatni kell.
- **Nincs nyitott `<status:must_fix>`** → a fázis zöld, mehet a `bs-merge`.
- **Van nyitott `<status:must_fix>`** → a fázis **FAIL**:
  1. értesítés (`Failure handling: notify` — az alapértelmezés):
     ```bash
     python3 <platform-scripts-mappa>/notify.py --phase review \
       --cycle specs/cycle-NN-<cycle-name> --status fail
     ```
  2. a PR **nyitva marad**, a ciklus ága él, a fejlesztő a saját gépén javít: a findingok a `tasks.md` `## <sec:review_fixes>` szekciójába kerülnek, és a `/bs-implement` fix-módja + `/bs-validate` fut rájuk;
  3. `Failure handling: auto-fix-loop` esetén a CI-n indul a javító hurok — a `07` hurkának **változatlan** leállási korlátaival (per-item 3 egymást követő / 5 összes bukás, 5 egymást követő FAIL-futás), majd eszkaláció emberhez. A korlát elérése után **ugyanaz az értesítés** megy, mint a `notify` ágon.

---

## Nem-interaktív szerződés (gépi futtatás a CI-n)

Központosított SDD-ben ezt a skillt a `ci-run-skill.sh` adapter indítja, nem ember. Egy interaktív kérdés ilyenkor vagy örökre vár, vagy — ami rosszabb — **kitalál egy választ**. Ezért:

> **Nem-interaktív módban a kérdés = STOP.** Írd a kérdést a `specs/cycle-NN-<cycle-name>/review-questions.md` fájlba (a `doc-sync-questions.md` mintájára), küldj értesítést, és az adapter `exit 2`-vel tér vissza. A PR nyitva marad, a fejlesztő a saját gépén folytatja.

**Ne találgass, és ne „döntsd el helyette":** egy kitalált válasz a gépi futtatásban észrevétlen marad, mert nincs ember a hurokban, aki észrevegye.

---

## Lezárás

1. Regeneráld a generált ciklus-státuszt:
   ```bash
   python3 <platform-scripts-mappa>/cycle-status.py specs/cycle-NN-<cycle-name> --write
   ```
2. Commitold a `ci-code-review.md`-t és a `cycle-status.md`-t a **ciklus ágára** (a PR-be), és küldd fel.
3. Jelezd a következő lépést:

<!-- INCLUDE:lang/09-merge.md#zaro-uzenet-review -->
