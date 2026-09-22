---
phase: 09c
name: bs-merge
description: "berkispec - 09c. Használd a PR-en futott review után (Phase 09c), a három lépéses ciklusvég utolsó kötelező lépéseként. Ellenőrzi a PR állapotát (elfogadott-e — ez veszi át az RD8 szerepét), lefuttatja a post-merge teszt-kört (VP2: tesztek + Sonar) a ciklus ágán, és CSAK zöld eredmény után juttatja a kódot a fő branch-re."
prerequisites:
  - "Megnyitott, ELFOGADOTT PR a ciklus ágára (bs-create-pr + bs-review lefutott)"
  - "specs/cycle-NN-<name>/test-report/code-review.md és ci-code-review.md — nincs lezáratlan Must Fix"
  - "conventions.md `## <sec:cv_review_and_merge>` — `PR submission: yes`"
output:
  - "specs/cycle-NN-<name>/test-report/post-merge/ — a VP2 kör bizonyítéka (siker és bukás egyaránt)"
  - "Beolvasztott ciklus-ág (a PR merge-elve a conventions.md Merge stratégiája szerint)"
  - "specs/cycle-NN-<name>/cycle-status.md — generált ciklus-státusz"
  - "specs/roadmap.md — lezárva, ha nincs bekapcsolt bs-dev-test"
prev: bs-review
next: bs-dev-test
scripts:
  - "scripts/validate-gate-check.py --review-only --require-ci-review — a két review-jelentés kapuja"
  - "scripts/run-tests.py — a VP2 kör futtatása (--phase post-merge)"
  - "scripts/sonar-gate.py — a VP2 kör statikus rétege"
  - "scripts/report-gate-check.py — a VP2 kör riport-artefaktumai (TR3)"
  - "scripts/test-manager.py — opcionális test manager feltöltés (TM4/TM6)"
  - "scripts/notify.py — értesítés bukásnál (CS6)"
  - "scripts/cycle-status.py — a generált cycle-status.md (--write)"
---
# 09c — Merge (post-merge teszt-körrel)
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

Ez a ciklusvég **harmadik lépése a három lépéses (PR-es) úton**: 9a-create-pr · 9b-review · **9c-merge ←** · (9d-dev-test).

> **🔴 A `VP2` a fő branch-re juttatás ELŐTTI kapu (L13-D6/L13-D14).** A kör a **ciklus ágán** fut, a friss fő branch-csel egyesített kódon — és csak zöld eredmény után kerül a kód a fő branch-re. Bukásnál a közös fő branch **érintetlen marad**, a PR nyitva, a ciklus ága él: a `CS6` „commitold a ciklus ágába" követelménye ettől **magától teljesül**, és nem törött fő branch-ből kell visszajönni.

> **A megerősítés helye megváltozott (L13-D5).** Izolált üzemmódban a merge előtt a felhasználó erősít meg (RD8). **Központosított üzemmódban ezt a PR elfogadása veszi át** — az is emberi döntés, csak korábban és máshol, és **nyoma marad a szolgáltatónál**. Hogy a garancia mérhető maradjon, ez a skill **ellenőrzi a PR állapotát**, és megáll, ha nem elfogadott.

---

## <field:f_prerequisite>

0. **Ciklus-beazonosítás:** a bemenet a ciklus mappája. Gépi futtatásban az adapter adja át — ne kérdezz vissza. Interaktív futtatásban: <!-- INCLUDE:lang/common.md#ciklus-beazonositas -->

1. **`conventions.md`:** `## <sec:cv_merge_strategy>` + `## <sec:cv_review_and_merge>`. Ha a `PR submission` nem `yes`, **STOP** — irány a `bs-review-and-merge`.

2. **🔴 PR-állapot kapu (L13-D5):** a PR **elfogadott**-e, és teljesülnek-e a branch-védelmi követelmények?
   ```bash
   gh pr view feature/cycle-NN-<cycle-name> --json state,reviewDecision,mergeStateStatus
   ```
   _(GitLab: `glab mr view`; Bitbucket: a `conventions.md` access-parancsa.)_
   - **`reviewDecision: APPROVED` + nincs blokkoló check** → folytasd.
   - **bármi más** (nyitott change request, függő kötelező check, draft PR) → **STOP**. Enélkül az `RD8` nem áthelyeződne, hanem **eltűnne**: a központosított úton nincs ember a hurokban, aki észrevenné.

3. **Review-kapu — MINDKÉT jelentés (L13-D1 / Q21):**
   <!-- INCLUDE:shared/python-cmd.md -->
   ```bash
   python3 <platform-scripts-mappa>/validate-gate-check.py \
     specs/cycle-NN-<cycle-name> --review-only --require-ci-review
   ```
   A kapu a `07` lokális `code-review.md`-jét **és** a `bs-review` `ci-code-review.md`-jét is olvassa: egyikben sem lehet nyitott `<status:must_fix>`, és egyik sem lehet befejezetlen (RV-INC). **Ez nem új kikényszerítés**, hanem a mai `09` előfeltételének szétosztása — enélkül a három skillre vágás elveszítené azt a védelmet, ami ma megvan.

4. **Státusz-kapu:** `tasks.md` / `plan.md` / `spec.md` = `<status:done>`, `[validate-loop]` marker nélkül.

5. **Doc-sync kapu:** a `doc-sync-plan.md` létezik, minden tétele pipált, nincs nyitott `doc-sync-questions.md` kérdés.

---

## Feladatod

1. **Integrációs frissítés:** a fő branch behozása a ciklus ágába (W2).
2. **`VP2` — post-merge teszt-kör** a ciklus ágán: tesztek + Sonar + riport-kapu.
3. **Csak zöld eredmény után:** a PR beolvasztása (a kód fő branch-re juttatása).
4. **Lezárás:** roadmap, generált `cycle-status.md`, és átadás a `bs-dev-test`-nek, ha be van kapcsolva.

---

## 1. Integrációs frissítés (W2 / RM5)

```bash
git fetch origin
git log --oneline HEAD..origin/main
```

- **Üres lista → a fő branch nem ment előre.** A `Skip post-merge tests if master unchanged` mező dönt (RM11): `yes` → a `VP2` kihagyható (a kihagyás okát írd a `test-report/post-merge/skipped.md`-be, a fő branch SHA-jával); `no` → a kör akkor is lefut.
- **Nem üres →** hozd be a fő branch-et a ciklus ágába. Mivel az ág fel van küldve és PR van rá, a helyes mechanika a **merge** (a rebase force-push-t igényelne egy review alatt lévő ágon):
  ```bash
  PRE=$(git rev-parse HEAD)
  git merge origin/main
  git diff --name-only "$PRE" HEAD
  ```
  Ha a behozott változás a ciklus hatókörét érinti (ugyanazok a fájlok, ugyanaz a szerződés), a `VP2` kör **kötelező** — és ha a `VP2` bukik, a szabály a *A `VP2` bukása* szekció. Ütközésnél: ne találd ki a feloldást, nem egyértelmű esetben **STOP** (gépi futtatásban `merge-questions.md` + `exit 2`).

---

## 2. `VP2` — post-merge teszt-kör a ciklus ágán

> **🔴 Központosított úton a `VP2` tesztjeinek tipikusan teljesen konténerizálhatónak kell lenniük (`CS4`):** a CI teszt-node-ján `compose`-zal fel kell húzni egy **teljes, mockokkal ellátott teszt környezetet**, és abban futtatni a teszteket, **már a fő branch-csel egyesített kóddal**. A környezet **receptje** (hogyan indul a stack, milyen mock, milyen teszt-user) a `specs/test-conventions.md`-be tartozik (TC1/c), a riport-artefaktumok és a parancsok a `conventions.md`-be.

### 2/a. Tesztek

```bash
python3 <platform-scripts-mappa>/run-tests.py \
  specs/cycle-NN-<cycle-name>/plan.md \
  --round-dir specs/cycle-NN-<cycle-name>/test-report/post-merge \
  --phase <status:phase_post_merge>
```

A `<field:f_prerequisite>` és a `Takarítás` oszlop hozza a compose-os környezet felhúzását és lebontását — a takarítás akkor is lefut, ha a futtatás elszállt. `MEGJEGYZÉS (PH1)` („nincs mit futtatni") a bekapcsolt `Post-merge tests` mellett **terv-hiány**, nem „nincs teendő": gépi futtatásban ez `merge-questions.md` + `exit 2`.

### 2/b. Sonar — a kör statikus rétege

```bash
python3 <platform-scripts-mappa>/sonar-gate.py \
  --out specs/cycle-NN-<cycle-name>/test-report/post-merge/sonar-report.md
```

Ugyanaz a script, ugyanazok a `conventions.md` küszöbök, mint a `07`-ben: az egyesítés új kódot hoz be, amit a `07` Sonar-köre sosem látott.

### 2/c. Riport-kapu

```bash
python3 <platform-scripts-mappa>/report-gate-check.py \
  conventions.md specs/cycle-NN-<cycle-name> \
  --report-subdir test-report/post-merge
```

**Siker és bukás egyaránt nyomot hagy** — a `test-report/post-merge/` készlet a ciklus mappájába és ágába kerül, commitolva és felküldve, tehát a PR-en is látszik.

### 2/d. Test manager (opcionális, TM4)

Ha a `**<field:f_test_manager_phases>:**` mező felsorolja a `post-merge` fázist, a kör **előtt** `--mode preflight`, a kör **után** `--mode publish` fut (`test-manager.py`), és a kimenet utolsó sorából (`TEST_MANAGER_RUN_URL=`) kerül a futás-URL a riportba. **A feltöltés nem bizonyíték** (TM7), és a bukása alapból nem buktat.

### A `VP2` bukása

1. A bizonyíték már a helyén van — **ne töröld, ne írd felül**. Commitold és küldd fel a ciklus ágára: a PR-en így látszik.
2. **A fő branch érintetlen**, a PR nyitva marad.
3. `Failure handling: notify` (alap) → értesítés (`notify.py --phase post-merge --status fail`), és a javítást **ember** indítja: a tételek a `tasks.md` `## <sec:post_merge_fixes>` szekciójába kerülnek, majd `/bs-implement` (fix-mód) → `/bs-validate` → vissza ide.
4. `Failure handling: auto-fix-loop` → a CI-n indul a javító hurok, a `07` hurkának **változatlan** leállási korlátaival, majd eszkaláció emberhez.
5. **A kimondott kivétel** (L13-D8): ha a bukás **nem ehhez a ciklushoz tartozik** (másik ciklus regressziója, környezeti hiba), új ciklus indul rá, és ez a ciklus lezárható. A döntés emberi, a riport alapján — gépi futtatásban ez `exit 2` + kérdés.

---

## 3. A beolvasztás

Csak zöld `VP2` után (vagy ha a kör nem futott). A `conventions.md` `## <sec:cv_merge_strategy>` **<field:f_provider>** és **Merge típusa** mezője szerint:

```bash
gh pr merge feature/cycle-NN-<cycle-name> --squash --delete-branch=false
```

_(GitLab: `glab mr merge`; Bitbucket: a `conventions.md` access-parancsa. A merge típusa a `conventions.md`-ből jön — squash / merge commit / rebase.)_

> **🔴 A ciklus ágát itt NE töröld** (L13-D7). Ha a `Dev deployment test` be van kapcsolva, a `VP3` kör még hátravan, és a bukásának a ciklus útvonalára kell írnia — a jármű ilyenkor egy a fő branch-ről nyitott `<ciklus-ág>-dev-test` ág, de amíg ez le nem futott, a ciklus ágát hagyd meg.
>
> **Izolált üzemmódban (PR van, de a merge a te gépeden történik)** a merge előtt **kötelező a felhasználói megerősítés** (RD8):
> <!-- INCLUDE:lang/09-merge.md#RD8-merge-megerosites -->

---

## 4. Lezárás

1. **Roadmap:** ha a `Dev deployment test` **nincs** bekapcsolva, a `VP2` volt az utolsó engedélyezett verifikáció — jelöld a ciklust lezártként (`✅`). Ha **be van** kapcsolva, a ciklus-sor `<status:waiting_for_verification>` marad (L13-D8).
2. **Generált ciklus-státusz:**
   ```bash
   python3 <platform-scripts-mappa>/cycle-status.py specs/cycle-NN-<cycle-name> --write
   ```
3. Jelezd a következő lépést:

<!-- INCLUDE:lang/09-merge.md#zaro-uzenet-merge -->
