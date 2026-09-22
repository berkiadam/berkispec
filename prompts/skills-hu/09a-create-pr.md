---
phase: 09a
name: bs-create-pr
description: "berkispec - 09a. Használd a ciklus lezárásának ELSŐ lépéseként (Phase 09a), ha a conventions.md '## Review and merge' szekciójában 'PR submission: yes'. A ciklus ágának felküldése és a PR megnyitása a conventions.md Merge stratégiája szerint — a review és a beolvasztás két külön skill (bs-review → bs-merge). A PR-t NEM merge-eli."
prerequisites:
  - "specs/cycle-NN-<name>/tasks.md státusz: <status:done>"
  - "specs/cycle-NN-<name>/plan.md státusz: <status:done>"
  - "specs/cycle-NN-<name>/spec.md státusz: <status:done>"
  - "specs/cycle-NN-<name>/test-report/code-review.md — nincs lezáratlan Must Fix (a 07 review-kapuja)"
  - "conventions.md `## <sec:cv_review_and_merge>` — `PR submission: yes`"
output:
  - "Felküldött ciklus-branch + megnyitott PR a conventions.md szolgáltatójánál"
  - "specs/cycle-NN-<name>/cycle-status.md — generált ciklus-státusz a PR linkjével (L13-D9)"
prev: bs-doc-sync
next: bs-review
scripts:
  - "scripts/cycle-status.py — a generált cycle-status.md (--write)"
  - "scripts/notify.py — értesítés, ha a PR nyitása nem-interaktív módban megáll"
---
# 09a — PR létrehozása
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

Spec driven development-ben fejlesztünk szoftvert. A fejlesztés ciklusokra van bontva. Minden ciklus egy önállóan lefejleszthető, önállóan tesztelhető részegysége a teljes implementációnak.

Ez a ciklusvég **első lépése a három lépéses (PR-es) úton**: **9a-create-pr ←** · 9b-review · 9c-merge · (9d-dev-test).

> **Miért három skill és nem egy megszakított fázis (L13-D1).** A PR megjelenése után a folyamatba **külső szereplők** szólnak bele (PR-elfogadó, CI/CD). A skill-határ a legjobb megszakadás-tűrés (13. elv): a lemezen hagyott nyom maga a **fázis-határ**, nem egy marker — a `/clear` utáni ágens abból tudja, hol tart, hogy melyik skillt hívják legközelebb.

> **A topológiát a PR megléte dönti el, nem az üzemmód.** Ez a lánc **izolált** SDD-ben is ez, ha van PR feladás — a különbség csak az, hogy a `bs-review` és a `bs-merge` a fejlesztő gépén vagy a CI/CD-n fut.

---

## <field:f_prerequisite>

0. **Ciklus-beazonosítás:** ha a felhasználó megadott ciklust/fájlt, azt használd; különben a legfrissebb `specs/cycle-*` mappát ajánld fel megerősítésre — <!-- INCLUDE:lang/common.md#ciklus-beazonositas --> — és várj a válaszra, mielőtt továbblépsz.

1. **`conventions.md`:** olvasd be a `## <sec:cv_merge_strategy>` és a `## <sec:cv_review_and_merge>` szekciót. Ha a fájl nem létezik, STOP — térjenek vissza a `00` fázishoz.

1.b **Topológia-ellenőrzés (L13-D1) — itt KÉRDÉS, nem hiba.** Ha a `PR submission` mezője `no`, a projekt PR nélkül dolgozik. Ez **nem policy-sértés**: a felesleges PR ártalmatlan és visszavonható (a két irány nem szimmetrikus). Kérdezd meg, és várj a válaszra:
   <!-- INCLUDE:lang/09-merge.md#L13-D1-pr-felesleges -->
   Ha a felhasználó a `bs-review-and-merge`-öt választja, irányítsd oda, és állj meg.

2. **Munkafa-ellenőrzés:** `git status --short`. Commitálatlan változtatásnál listázd, és kérdezd meg egy körben, hogy commitáljam-e most vagy folytassam — várj a válaszra. Itt **nem** váltunk branch-et: a ciklus saját ágán maradunk, azt küldjük fel.

3. **Státusz-kapu:** `tasks.md` / `plan.md` / `spec.md` státusza `<status:done>`, és a `tasks.md`-n **nincs `[validate-loop]` marker**. Ha bármelyik nem teljesül, térj vissza a `07` fázishoz.

4. **Review-kapu (RV1):** a `test-report/code-review.md` létezik, és nincs benne lezáratlan `- [ ]` a `<sec:critical_fixes>` szekcióban. Ha nem így van, **STOP**, vissza a `07`-re — a PR leírása ebből a fájlból készül, egy nyitott Must Fix-szel nyitott PR a review-t hitelteleníti.

5. **Doc-sync kapu:** a `doc-sync-plan.md` létezik, nincs benne elvégzetlen `[ ]` tétel, nincs nyitott `doc-sync-questions.md` kérdés, a DS22 kapu zöld volt. Ha nem, vissza a `08`-ra.

---

## Feladatod

1. **Merge előtti doc-sync ellenőrzés** (DS23.2) — változott-e kód a `08` óta.
2. **Integrációs frissítés:** a fő branch behozása a ciklus ágába (W2) — hogy a PR-t ne egy elavult alapra nyissuk.
3. **A ciklus ágának felküldése és a PR megnyitása.**
4. **A generált `cycle-status.md` frissítése** a PR linkjével, és átadás a `bs-review`-nak.

> **🔴 A `VP2` teszt-kör NEM itt fut.** Ezen az úton a merge utáni verifikáció a **`bs-merge`** fázisban, a fő branch-re juttatás **előtt** történik (L13-D6/L13-D14). Itt csak a PR nyílik meg.

Ebben a fázisban **nincs önjavító hurok és nincs subagent**.

---

## 1. Merge előtti doc-sync ellenőrzés (DS23.2)

1. **Változott-e kód a `08-doc-sync` lezáró commitja óta?**
   ```bash
   BASE=$(git log --format=%H -1 --grep="^cycle-NN: 08-doc-sync")
   git diff --name-only "$BASE" HEAD
   ```
   - Ha **nem** (üres lista, vagy csak `specs/` alatti útvonalak), nincs teendő.
   - Ha **igen**, indítsd újra a `08-doc-sync`-et a végső kódra: `/bs-doc-sync input: @specs/cycle-NN-<cycle-name>`
2. Csak zöld DS22 kapu után folytasd.

---

## 2. Integrációs frissítés (W2)

```bash
git fetch origin
git log --oneline HEAD..origin/main
```

_A `main` helyére a `conventions.md` `## <sec:cv_git_conventions>` **<field:f_main_branch>** mezője kerül. A parancsban **szándékosan nincs `$( )` behelyettesítés** (allowlistelhetőség)._

- **Üres lista** → folytasd a PR nyitásával.
- **Nem üres** → hozd be a fő branch-et a ciklus ágába (`git rebase origin/main`, ha az ág még nincs felküldve; `git merge origin/main`, ha már igen), majd nézd meg, mi jött be (`git diff --name-only "$PRE" HEAD`):
  - **forráskód vagy teszt változott** → a `bs-merge` `VP2` köre úgyis lefut rá; ha a behozott változás a ciklus hatókörét érinti, **STOP**, vissza a `07`-re.
  - **csak `docs-generated/` / `conventions.md` / `specs/test-conventions.md`** → **STOP**, vissza a `08`-ra.
  - **csak más ciklusok `specs/cycle-MM-*/` mappái** → nincs teendő.

Ütközésnél a `bs-review-and-merge` *Merge conflict kezelése* szabályai érvényesek: ne találd ki a feloldást, nem egyértelmű esetben STOP + kérdés.

---

## 3. A PR megnyitása

1. **Az ág felküldése:**
   ```bash
   git push -u origin feature/cycle-NN-<cycle-name>
   ```
2. **PR létrehozása** a `conventions.md` `## <sec:cv_merge_strategy>` szolgáltatója és target branche szerint. A PR description a `code-review.md` tartalma legyen:
   - **GitHub:** `gh pr create --base <target> --head feature/cycle-NN-<cycle-name> --title "cycle-NN: <cím>" --body-file specs/cycle-NN-<cycle-name>/test-report/code-review.md`
   - **GitLab:** `glab mr create --target-branch <target> --title "cycle-NN: <cím>" --description "$(cat specs/cycle-NN-<cycle-name>/test-report/code-review.md)"`
   - **Bitbucket:** a `conventions.md` access-parancsa szerint, REST API-n vagy CLI-n keresztül.
3. **A PR-t NE merge-eld**, és a fő branch-re **ne válts** — a beolvasztás a `bs-merge` dolga, a PR elfogadása pedig emberi döntés (`L13-D5`).

> **Nem-interaktív (CI) futtatás:** ha a skill ebben a módban kérdezni akarna (hiányzó target branch, kétértelmű szolgáltató-konfiguráció), **a kérdés = STOP**: írd a kérdést a `specs/cycle-NN-<cycle-name>/create-pr-questions.md` fájlba, küldj értesítést (`notify.py`), és az adapter `exit 2`-vel tér vissza. Ne találj ki választ.

---

## 4. Lezárás és átadás

1. **Generált ciklus-státusz** (L13-D9) — a PR linkjével együtt:
   <!-- INCLUDE:shared/python-cmd.md -->
   ```bash
   python3 <platform-scripts-mappa>/cycle-status.py specs/cycle-NN-<cycle-name> --write
   ```
   A `cycle-status.md` **generált fájl**: rendering a bizonyítékból, sosem forrás. Commitold a ciklus ágára, és küldd fel (`git push`).
2. A roadmap-et **még NE zárd le**: a ciklus akkor kész, ha az utolsó engedélyezett verifikáció zöld (L13-D8) — az még hátravan. A roadmap ciklus-sorára a `<status:waiting_for_verification>` jelölés kerül.
3. Jelezd a felhasználónak a PR linkjét és a következő lépést:

<!-- INCLUDE:lang/09-merge.md#zaro-uzenet-create-pr -->
