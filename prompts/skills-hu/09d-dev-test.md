---
phase: 09d
name: bs-dev-test
description: "berkispec - 09d. OPCIONÁLIS utolsó fázis (Phase 09d), csak központosított SDD-ben, ha a conventions.md '## Review and merge' szekciójában 'Dev deployment test: yes'. A sikeres merge után telepíti a terméket egy teljesen integrált dev/teszt környezetbe, valódi e2e teszteket futtat rá (VP3), és a bizonyítékot a ciklus 'test-report/dev-test/' mappájába teszi."
prerequisites:
  - "A ciklus be van olvasztva a fő branch-be (bs-merge lefutott)"
  - "conventions.md `## <sec:cv_review_and_merge>` — `Dev deployment test (bs-dev-test): yes` és `SDD mode: centralized`"
  - "conventions.md `Dev deployment command` — kitöltött"
output:
  - "specs/cycle-NN-<name>/test-report/dev-test/ — a VP3 kör bizonyítéka (siker és bukás egyaránt)"
  - "specs/cycle-NN-<name>/cycle-status.md — generált ciklus-státusz"
  - "specs/roadmap.md — a ciklus lezárva (ez az utolsó engedélyezett verifikáció)"
prev: bs-merge
next: bs-write-spec
scripts:
  - "scripts/run-tests.py — a VP3 kör futtatása (--phase dev-test)"
  - "scripts/report-gate-check.py — a VP3 kör riport-artefaktumai (TR3)"
  - "scripts/test-manager.py — test manager feltöltés (gyárilag EZ a fázis, TM4)"
  - "scripts/notify.py — értesítés bukásnál (CS6)"
  - "scripts/cycle-status.py — a generált cycle-status.md (--write)"
---
# 09d — Dev-teszt (VP3)
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

Ez a ciklusvég **opcionális negyedik lépése**, kizárólag a központosított úton: 9a-create-pr · 9b-review · 9c-merge · **9d-dev-test ←**.

> **Mit bizonyít (VP3).** A `07` (`VP1`) azt, hogy funkcionálisan az készült el, ami a spec-ben van; a `VP2` azt, hogy a fő branch-csel egyesítve is működik. A `VP3` azt, hogy **valódi, integrált környezetben** is a spec szerint fut minden — automatikus telepítés után, éles jellegű e2e tesztekkel. Ez az a pont, ahol a legtöbbet érő teszt-információ keletkezik.

> **Miért csak központosított úton (`CS5`).** Az integrált dev-környezetbe telepítés automatizmust és központi infrastruktúrát feltételez. Izolált üzemmódban a `00-init-project` érvényességi szabálya ezt a kombinációt **visszautasítja**.

---

## <field:f_prerequisite>

0. **Ciklus-beazonosítás:** a bemenet a ciklus mappája. Gépi futtatásban az adapter adja át — ne kérdezz vissza.

1. **`conventions.md` `## <sec:cv_review_and_merge>`:**
   - `Dev deployment test (bs-dev-test)` = `yes` — különben ez a fázis nem fut (jelezd és állj meg);
   - `SDD mode` = `centralized`;
   - `Dev deployment command` — **kitöltött**. Ha üres, **STOP**: enélkül a fázis nem tudja, mivel telepítsen (a `00` érvényességi szabálya ezt már a beíráskor elkapja).

2. **Merge-kapu:** a ciklus be van-e olvasztva a fő branch-be?
   ```bash
   git fetch origin
   git log --oneline origin/main --grep="cycle-NN" -1
   ```
   Ha a ciklus commitja nincs a fő branch-en, **STOP** — előbb `bs-merge`.

3. **Teszt-válogatás:** a `plan.md` gépi futtatási táblájában van-e `<status:phase_dev_test>` fázisú sor? Ha nincs, **STOP + kérdés** (gépi futtatásban `dev-test-questions.md` + `exit 2`): a fázis be van kapcsolva, de a terv nem mondja meg, **mit** futtasson — ez terv-hiány, nem „nincs teendő".

---

## Feladatod

1. **Az ág megnyitása** a ciklus útvonalán (`L13-D7`).
2. **Telepítés** a `Dev deployment command`-dal, és a telepítés **igazolása**.
3. **`VP3` — valódi e2e teszt-kör** a telepített rendszeren, `--phase dev-test`.
4. **Bizonyíték + test manager + lezárás.**

---

## 1. Az ág — a riport a ciklus ÚTVONALÁRA megy (L13-D7)

A ciklus mappája (`specs/cycle-NN-<cycle-name>/`) a merge után a **fő branch-en** él, ugyanazon az útvonalon — „vissza a ciklushoz" tehát nem az ágat jelenti, hanem az **útvonalat**. Mivel a ciklus ága ekkor már törölhető (vagy védett a fő branch), a jármű egy **új ág a fő branch-ről**:

```bash
git fetch origin
git switch -c feature/cycle-NN-<cycle-name>-dev-test origin/main
```

_A branch-név a `conventions.md` `## <sec:cv_git_conventions>` **<field:f_branch_naming>** stratégiáját követi, `-dev-test` utótaggal._

---

## 2. Telepítés az integrált környezetbe

Futtasd a `conventions.md` `Dev deployment command` mezőjében rögzített parancsot, **szó szerint**. A parancs a projekté, nem a kereté — a részletes recept (mit telepít, milyen adattal, hogyan áll vissza) a `specs/test-conventions.md`-be tartozik (TC1/c).

> **🔴 Egy zöld teszt nem bizonyítja, HOL volt zöld (`7/g`).** A telepítés után, a tesztek előtt **igazold**, hogy a telepített rendszer fut és elérhető: a `plan.md` `<status:phase_dev_test>` sorainak `<field:f_prerequisite>` cellájában ott az elérhetőségi probe a **cél-hosttal** (EV4), és a parancs **literálisan** tartalmazza a cél-hostot (EV3). `localhost` / `127.0.0.1` deklarált port-forward nélkül **tilos** (EV5) — a `run-tests.py` ezt `exit 4`-gyel megfogja, futtatás nélkül.

Ha a telepítés bukik: **ez nem teszt-bukás, hanem környezeti hiba** — értesítés + `exit 1`, és a ciklus `<status:waiting_for_verification>` állapotban marad. Ne futtass tesztet egy fel sem állt rendszerre: a zöld eredmény ilyenkor semmit nem jelentene.

---

## 3. `VP3` — a teszt-kör

<!-- INCLUDE:shared/python-cmd.md -->

### 3/a. Test manager preflight (TM4 — gyárilag EZ a fázis tölt fel)

```bash
python3 <platform-scripts-mappa>/test-manager.py --mode preflight --phase dev-test \
  --round-dir specs/cycle-NN-<cycle-name>/test-report/dev-test
```

**A preflight a teszt-kör ELŐTT fut, és nem csak az env var meglétét nézi, hanem a kliens BETÖLTHETŐSÉGÉT** — egy `reporter` alakú kliens rossz runtime-verzión az egész teszt-futást meg tudja ölni, nulla lefutott teszttel. Token nélkül egy teljes e2e kör veszne kárba. `exit 3` = a fázis nincs a listán (kihagyva, nem hiba).

### 3/b. A tesztek

```bash
python3 <platform-scripts-mappa>/run-tests.py \
  specs/cycle-NN-<cycle-name>/plan.md \
  --round-dir specs/cycle-NN-<cycle-name>/test-report/dev-test \
  --phase <status:phase_dev_test>
```

### 3/c. Riport-kapu és feltöltés

```bash
python3 <platform-scripts-mappa>/report-gate-check.py \
  conventions.md specs/cycle-NN-<cycle-name> \
  --report-subdir test-report/dev-test

python3 <platform-scripts-mappa>/test-manager.py --mode publish --phase dev-test \
  --round-dir specs/cycle-NN-<cycle-name>/test-report/dev-test
```

- A `publish` kimenetének utolsó sora `TEST_MANAGER_RUN_URL=<url>` — ez megy a riportba, az értesítésbe (`notify.py --run-url`) és a generált `cycle-status.md`-be. Egy bukott körnél a fejlesztő így **egy kattintással a trace-nél van**.
- **A feltöltés akkor és csak akkor számít megtörténtnek, ha a futás-URL megjelent** (L13-D26): a kliens rossz tokennel zölden, `exit 0`-val végezhet, miközben semmi nem töltődött fel. URL híján a riportba `test manager: FAILED (nincs futás-URL a kimeneten)` sor kerül.
- **A feltöltés nem bizonyíték** (TM7): a ciklus bizonyítéka a **commitolt** `test-report/dev-test/` készlet. A `**<field:f_test_manager_required>:**` `igen` érték teszi a feltöltési hibát kemény kapuvá.

---

## 4. Lezárás

1. **Commitold a bizonyítékot** a `-dev-test` ágra, és integráld vissza a `conventions.md` `## <sec:cv_merge_strategy>` szerint (PR vagy közvetlen merge) — **a ciklus mappájába írt riport a fő branch-re kell, hogy kerüljön**, különben a bizonyíték-lánc megszakad.
2. **Bukásnál:**
   ```bash
   python3 <platform-scripts-mappa>/notify.py --phase dev-test \
     --cycle specs/cycle-NN-<cycle-name> --status fail --run-url "<a test manager URL-je>"
   ```
   A javítás a `tasks.md` `## <sec:post_merge_fixes>` szekcióján át megy (a `06`/`07` gépezete változatlanul fut rá) — **nem** új ciklus, hanem a még nyitott ciklus folytatása. A kimondott kivétel: ha a bukás nem ehhez a ciklushoz tartozik, új ciklus indul rá, és ez a ciklus lezárható (L13-D8).
3. **Zöld kör esetén ez volt az utolsó engedélyezett verifikáció** — jelöld a ciklust lezártként a `specs/roadmap.md`-ben (`✅`), és regeneráld a státuszt:
   ```bash
   python3 <platform-scripts-mappa>/cycle-status.py specs/cycle-NN-<cycle-name> --write
   ```
4. Jelezd a ciklus lezárását:

<!-- INCLUDE:lang/09-merge.md#zaro-uzenet-dev-test -->
