---
phase: 07
name: bs-validate
description: "berkispec - 07. Használd az implementáció után (Phase 07), ha a tasks.md 'Validálásra kész'. Teszt-, lint- és build-ellenőrzés ÉS kódreview egyetlen önjavító hurokban (test-runner, reviewer, implement-fixer, review-fixer subagentek). Létrehozza a 'validation-report.md'-t és a 'code-review.md'-t; PASS esetén a spec.md/plan.md/tasks.md státuszát 'Kész'-re állítja."
prerequisites:
  - "specs/cycle-NN-<name>/tasks.md státusz: <status:ready_for_validate>"
output:
  - "specs/cycle-NN-<name>/test-report/validation-report.md — teljes validálási riport (körönkénti lépés-napló + # Validation History), append-only"
  - "specs/cycle-NN-<name>/test-report/code-review.md — a reviewer findingjei (Must Fix / Suggestions), körönként frissítve"
  - "specs/cycle-NN-<name>/test-report/validate/round-NN/ — körönként külön mappában a conventions.md `## <sec:cv_test_reporting>` táblája szerint kötelező riport-artefaktumok (TR3 kapu)"
  - "PASS esetén: spec.md / plan.md / tasks.md státusz: <status:done>"
prev: bs-implement
next: bs-doc-sync
subagents:
  - "agents/test-runner.md"
  - "agents/reviewer.md"
  - "agents/implement-fixer.md"
  - "agents/review-fixer.md"
scripts:
  - "scripts/round-log.py — a `## <sec:round> N` blokk nyitása/zárása + a round-NN mappa (VD9, TR5)"
  - "scripts/run-tests.py — tesztfuttatás a plan gépi táblájából, gépi darabszámokkal (TR1/TR2)"
  - "scripts/sonar-gate.py — Sonar Quality Gate az API-ból (QG1 megkülönböztetéssel)"
  - "scripts/dod-check.py — DoD ↔ bizonyíték join (DI1)"
  - "scripts/test-substance-check.py — vacuous teszt-törzs (TB1) és szelektor-létezés (TB2)"
  - "scripts/validate-gate-check.py — státusz/task/DoD/IP1/review/kör-blokk/CK1 gyűjtőkapu"
  - "scripts/contract-guard.py — VD3a szerződés-integritás kapu"
  - "scripts/report-gate-check.py — TR3 riport-kapu"
  - "scripts/failure-counter.py — futás-napló és leállási korlátok (VD4)"
shared:
  - "shared/review-checklist.md"
  - "shared/input-from-prev.md"
  - "shared/phase-commit.md"
---
# 07 — Validálás és kódreview
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

Spec driven development-ben fejlesztünk szoftvert. A fejlesztés ciklusokra van bontva. Minden ciklus egy önállóan lefejleszthető, önállóan tesztelhető részegysége a teljes implementációnak.

Ez a folyamat **7. fázisa (0–9)**: 0-init · 1-ciklusok · 2-spec · 3-plan · 4-tasks · 5-analyze · 6-implement · **7-validate (tesztek + review) ←** · 8-doc-sync · 9-merge.

---

## Bemenet

A prompt bemenete a ciklus mappája (pl. `specs/cycle-NN-<cycle-name>`). A validációhoz szükséges fájlokat (`spec.md`, `plan.md`, `tasks.md`) ebben a mappában találod.

## <field:f_prerequisite>

0. **Ciklus-beazonosítás:** ha a felhasználó megadott ciklust/fájlt, azt használd; különben a legfrissebb `specs/cycle-*` mappát ajánld fel megerősítésre — <!-- INCLUDE:lang/common.md#ciklus-beazonositas --> — és várj a válaszra, mielőtt továbblépsz.

1. **`conventions.md` létezés-ellenőrzés:** olvasd be a projekt gyökerében a `conventions.md`-t. Ha nem létezik, STOP — térjenek vissza a `00` fázishoz.

2. **Munkafa-ellenőrzés (csak VCS esetén):** futtasd `git status --short`. (No-VCS projektben kimarad.)
   - **Előbb nézd meg a `tasks.md` státuszát.** Ha `[validate-loop]` markert visel, egy korábbi hurok szakadt meg: a ciklus mappájában lévő commitálatlan változások (`spec.md` DoD-pipák, `tasks.md` javító-taskok, `test-report/`) **a hurok saját, még nem commitolt állapota** (VD8 — a hurok alatt nincs köztes commit). Ilyenkor **ne ajánld fel commitra** és ne kérdezz — jelezd egy sorban, hogy megszakadt hurkot folytatsz, és menj a „Megszakított futás kezelése" 4. pontjára.
   - Egyébként, ha van commitálatlan változtatás, listázd, és kérdezd meg egy körben, hogy commitáljam-e most vagy folytassam — várj a válaszra.

3. **Előfeltétel-kapu — szkripttel, ne fájlbeolvasással.** A három státusz, a `[validate-loop]` marker és a nyitott `validate-input-from-prev.md` tételek egyetlen hívásból kiderülnek:

   ```bash
   python3 <platform-scripts-mappa>/validate-gate-check.py \
     specs/cycle-NN-<cycle-name> --stage start
   ```

   - **`exit 0`** → mehet a validálás.
   - **`exit 1`** → a kiírt ✗ pontok szerint:
     - **`tasks.md` státusza nem `<status:ready_for_validate>`** → az implementáció még nem zárult le: jelezd, és térj vissza a `06` fázishoz;
     - **`plan.md` / `spec.md` státusza nem elfogadható** (elfogadható: `plan.md` → `<status:ready_for_tasks>` vagy `<status:done>`; `spec.md` → `<status:ready_for_plan>` vagy `<status:done>`) → ha valamelyik `<status:draft>`-ra van visszaállítva, jelezd a felhasználónak: valamelyik korábbi fázisban döntés született, amely szinkront igényel.
   - A `<status:done>` mindkettőnél **normális**, ha a `08-doc-sync` (vagy a `09-merge` előtti doc-sync újrafuttatás) után tértünk vissza ide.
   - A szkript `·` sorai INFO-k (megszakadt hurok markere, nyitott `input-from-prev` tételek) — ezeket dolgozd fel, de nem állítanak meg.

4. **Szelektor-kapu (TB2) — a kör ELEJÉN.** Egy elorphanodott `[CHECK]` szelektor (a `06` átnevezett egy teszt-függvényt, a task parancsa a régi nevet őrzi) a kör **elején** derüljön ki, ne a végén:

   ```bash
   python3 <platform-scripts-mappa>/test-substance-check.py \
     specs/cycle-NN-<cycle-name> --selectors-only
   ```

   - **`exit 0`** → mehet tovább;
   - **`exit 1`** → a `tasks.md` és a kód **szétcsúszott**: a felsorolt `[CHECK]` parancsok futtatáskor hibával állnának le, tartalmi ítélet nélkül. Javítsd a `tasks.md` parancsát a tényleges teszt-névre (ez nem tartalmi változtatás, nem sérti a `VD3`-at), **vagy** — ha a teszt egyáltalán nem készült el — vissza a `06`-ra: a `[RED]`/`[GREEN]` task nincs elvégezve.

   A `--selectors-only` szándékosan **csak** a `TB2`-t futtatja: a `TB1` vacuous-vizsgálat a lezárásnál értelmes (A/2 + B blokk), amikor a tesztek már készek.

---

## Ismételt hibák korai ellenőrzése

**Mielőtt bármit futtatnál:** ha létezik `specs/cycle-NN-<cycle-name>/test-report/validation-report.md`, kérdezd le a napló állapotát a szkript **read-only** módjával — **ne olvasd/parse-old kézzel** (a régi, elavult bejegyzésekből téves riasztás születik):

<!-- INCLUDE:shared/python-cmd.md -->

```bash
python3 <platform-scripts-mappa>/failure-counter.py \
  specs/cycle-NN-<cycle-name>/test-report/validation-report.md --status
```

A `--status` az **utolsó** futás bejegyzését és a hozzá tartozó számlálókat írja ki (egymást követő bukás / összes bukás / egymást követő FAIL-futások) — mindig az aktuális állapotot, nem a napló egy régi pontját. Ha az utolsó futás FAIL, és bármelyik számláló **eggyel a küszöbe alatt** van (2/3, 4/5, 4/5), ez **figyelmeztető jelzés, nem megállási pont**: írd a válaszodba egy sorban, hogy *„Figyelem: a(z) [Failed Item] már [N] alkalommal elbukott — ha most is hibázik, a leállási korlát életbe lép és humán beavatkozást kérek."*, majd **folytasd** a validálást (ez NEM kérdés, NE várj választ). A tényleges megállásról mindig a naplózó futtatás **kilépő kódja** dönt (lásd „Naplózás és leállási korlátok"), nem ez az előzetes ránézés.

---

## Feladatod

Ellenőrizd, hogy a ciklus implementációja teljes, helyes **és review-n átment**. A validálás **négy** forrás alapján történik:

1. **`spec.md` — <sec:definition_of_done>**: minden pont teljesül-e?
2. **`plan.md` — <sec:testing_strategy>**: minden előírt teszt lefut-e és átmegy-e?
3. **`tasks.md`**: minden task `[x]` státuszban van-e?
4. **`reviewer` subagent — kódreview (RV1)**: maradt-e lezáratlan `<status:must_fix>` finding a ciklus diffjében?

**Szereped PASS-ig determinisztikus ellenőrző, FAIL esetén orchestrátor.** Ha a validálás FAIL-t talál — akár teszt/Sonar/DoD, akár review-finding —, **nem** adod vissza egyszerűen a vezérlést a felhasználónak („futtasd újra a 06-ot"), hanem **levezényelsz egy önjavító hurkot** (fixer subagent → szerződés-integritás kapu → újra-validálás), amíg PASS nem lesz — a **három leállási korlát** (per-item 3 egymást követő / 5 összes bukás, valamint 5 egymást követő FAIL-futás) határáig, tervezési hiba esetén **felfelé eszkalálva**. A javítást nem te végzed: teszt-/Sonar-/DoD-bukásra az `agents/implement-fixer.md`, review-findingra az `agents/review-fixer.md` subagent (mindkettő = a 06 Fix-módja). Lásd „Az önjavító hurok (orchestrátor-hurok)".

> **Miért egy fázis (RV1)?** A review-javítás **elronthat egy tesztet**, ezért a fix után úgyis újra kell tesztelni — ez korábban a `09` saját „re-validate" ága volt, a 07 teljes gépezetének megismétlésével. Egy hurokban a review egyszerűen a **teljes kör 2. lépése** (a statikus réteg fele, a Sonar mellett): csak akkor fut, ha a gyors tesztek zöldek, és a findingjei ugyanabba a naplóba, ugyanazokkal a leállási korlátokkal kerülnek. A `09` így már csak a merge.

---

> **Költség-elv (VD10/VD11/VD12):** a fázis a **bizonyítékról**, az **elfogadási feltételekről** és a **kódminőségről** szól. Nem dokumentáció (az a `08`), nem merge (az a `09`), és nem futtat mindent minden körben (lásd „Kör-típusok" — a review is csak teljes körben, zöld tesztek után). Ha valami nem a PASS/FAIL döntéshez kell, az nem ebbe a fázisba tartozik.

## Megszakított futás kezelése

A validáció bármikor megszakadhat. Újraindítás (ismételt futtatás) esetén:
1. **Idempotens futás**: Kezdd elölről a validálási lépéseket — **a folytatás első köre mindig TELJES kör** (VD10), mert nem tudhatod, mi futott le épen a megszakadás előtt. Ha a korábbi futás naplózott már valamit a `test-report/validation-report.md`-be, az az előző (félbeszakadt) futásnak tekintendő: **olvasd el az utolsó `## <sec:round> N` blokkot** — ebből látod, meddig jutott (mely lépések futottak le, mi bukott, indult-e fixer). A megszakadt kört **ne írd felül**: zárd le a blokkját egy `**Megszakadt** — a futás itt szakadt meg` sorral, és az új kör új `## <sec:round> N+1` blokkot kap. **A megszakadt kör riport-mappáját (`validate/round-N/`) sem törlöd és nem használod újra** — az új kör új mappát kap (`round-N+1`), hogy a részleges és a teljes bizonyíték ne keveredjen (TR5).
2. **Beragadt erőforrások**: Ha a korábbi megszakított futásból beragadt teszt konténerek vagy folyamatok miatt portütközést tapasztalsz, lődd ki azokat, vagy keress új szabad portot a korábban leírt módon.
3. **Duplikált taskok elkerülése**: Ha a futás FAIL-lel zárul, és javító feladatokat kell felvenned a `tasks.md` `## <sec:validation_fixes>` / `## <sec:review_fixes>` szekciójába, mindig ellenőrizd, hogy a konkrét teszthiba, Sonar-javítás vagy `MF-NN` finding nem szerepel-e már elvégzetlen taskként (egy korábbi félbeszakadt validáció okán). Ha már ott van, ne vedd fel duplán.

3/b. **A megszakadt diagnoszta-futás részleletei (RV-INC):** ha az előző kör egy **diagnoszta subagent futása közben** szakadt meg (`reviewer`, `test-runner`, `analyzer`), a subagent már elvégzett munkája jellemzően **nincs teljes egészében a lemezen** — a jelentését a futás során írja ki, nem egyetlen záró művelettel. Mielőtt az új körben újraindítod:
   - **Nézd meg a részleges artefaktumot.** A `reviewer` inkrementálisan ír (RV-INC): ha a `test-report/code-review.md` fejlécében `<field:f_status>` = `<status:in_progress>` áll, a benne lévő findingok valósak, csak hiányosak — **ne dobd el és ne írd felül őket**.
   - **Kérdezd meg a felhasználót egy sorban:** *„A megszakadt `<subagent>` futásából ismert-e olyan részlelet (a platform naplójából vagy transcriptjéből), amit át kell adnom az új futásnak?"*
   - A kapott tételeket **és** a részleges artefaktum findingjait add át az új subagent bemenetében **„ellenőrizendő tételek"** blokként — nem kész findingként, hanem célzott ellenőrzési pontként.

   **Guard:** ha nincs ilyen részlelet, folytasd — ez nem hiba. Ezek nélkül viszont az új futás **vakon indul**, és egy már bizonyított hibát is elnézhet.

4. **Megszakadt önjavító hurok felismerése (`[validate-loop]` marker + <sec:validation_history>):** ha a `tasks.md` státusza `<status:ready_for_implement> [validate-loop]` markert visel, egy korábbi validate-hurok szakadt meg — **ne** kezdj tiszta lapról. Derítsd ki a hurok állapotát:
   - Kérdezd le a napló állapotát: `failure-counter.py <validation-report.md> --status` — ez adja meg az utolsó futást, a megrekedt itemeket és a számlálókat (hányadik próbánál tartott). Kézzel ne parse-old.
   - Olvasd be a `tasks.md` `## <sec:validation_fixes>` **és** `## <sec:review_fixes>` szekcióját: vannak-e még elvégzetlen `[ ]` javító-taskok?
     - **Ha igen** (a fixer nem futott le vagy félbeszakadt): folytasd a hurkot a megfelelő fixer újraindításával ezekre a taskokra (validációs → `implement-fixer`, review → `review-fixer`), majd újra-validálj.
     - **Ha nincs** (a fixer befejezte, de az újra-validálás maradt el): futtasd újra a validálási lépéseket, és értékeld az eredményt a hurok szerint.
   - A számlálók a leállási korlátok alapja — a folytatáskor a szkript automatikusan onnan számol tovább (a napló a memória). **Ne nullázd, ne írd át kézzel a `# <sec:validation_history>`-t.**

---

## Kontextus betöltési szabályok

> **🔴 Alapelv (VD11/b): ha van rá szkript, ne olvass fájlt.** A fázis determinisztikus kérdéseire (státuszok, nyitott taskok/DoD-pipák, kör-blokkok, riport-artefaktumok, Sonar-kapu, védett útvonalak diffje, teszt-darabszámok) **mind van szkript** — azok kimenete a bemeneted, nem a fájlok tartalma. A nyers teszt-log, a `sonar-report.md` és a `git diff` **soha ne kerüljön a fő kontextusba**, hacsak egy kapu kifejezetten oda nem irányít.

- Olvasd be a `spec.md` <sec:definition_of_done> szekciót.
- **A `plan.md`-t NE olvasd be a fő kontextusba (VD11).** A ciklus-specifikus futtatási igazságforrás a `test-runner` subagent bemenete — ő olvassa a plan `<sec:testing_strategy>` / `<sec:regression_impact>` / `<sec:e2e_infrastructure>` szekcióit, nem te. A fő ágensnek a **runner jelentése** az input. Két kivétel, mindkettő **célzott** (`Grep`, nem teljes beolvasás):
  - plan-hiány (TR4) ellenőrzése: `grep -n "<a runner által hiányolt kulcsszó>" specs/cycle-NN-<cycle-name>/plan.md` — csak a találat környezetét nézed meg;
  - a `<sec:regression_impact>` tábla kiolvasása a záró körhöz, ha a runner nem adta vissza.
  _Miért: a `plan.md` több száz sor, és a fő kontextusban minden további körben újraküldődik — ez a fázis egyik legnagyobb, teljesen fölösleges tokenköltsége._
- Olvasd be a `tasks.md`-t.
- **A `code-review.md`-t csak akkor olvasd be, ha a review már futott** ebben a fázisban — és akkor is csak a `<status:must_fix>` szekciót. A teljes findingszöveg a `review-fixer` bemenete, nem a tiéd.
- **Olvasd be a `validate-input-from-prev.md`-t, ha létezik** — lásd a „Fázisok közötti átadás" szekciót.
- Ne olvasd be az egész forráskódot — csak azt, ami egy konkrét ellenőrzéshez szükséges.

---

## Fázisok közötti átadás (`*-input-from-prev.md`) — IP1

**Amit BEOLVASSZ:** ha létezik a `specs/cycle-NN-<cycle-name>/validate-input-from-prev.md`, olvasd be a validálás **megkezdése előtt**. A 03/04 fázisban derült ki futtatási előfeltételeket és üzemeltetési tudnivalókat tartalmazza (pl. „a stack indítása előtt VPN kell", „ez a teszt csak a seed lépés után futtatható", „a port ütközik a fejlesztői stackkel"). Ezek jellemzően **megelőzik** a teszthibát, ha figyelembe veszed őket — ezért a `test-runner` indítása **előtt** dolgozd fel, és a releváns tételeket **add át a subagent bemenetében**.

Minden `[ ]` tételt zárj le: vagy figyelembe vetted a validálás során (`→ figyelembe vettem: <hogyan>`), vagy explicit indokkal elvetett (`→ elvetve: <miért>`). **Guard:** ha a fájl nem létezik, ez nem hiba — folytasd.

**Amibe ÍRHATSZ:** semmibe — a 07 a lánc **vége**. Ha a validálás során olyan tartós tudnivaló derül ki, ami a **következő ciklusokban** is kell, az nem ide tartozik: a `specs/test-conventions.md`-be való, aminek a `08-doc-sync` a gazdája (TC3 — a promóciót ott javasold, ne írd magad).

<!-- INCLUDE:shared/input-from-prev.md -->

---

## Kör-típusok — inkrementális hurok (VD10)

> **Nem minden kör teljes.** A hurok költségének nagy részét a nehéz tesztek (stack fel/le, E2E, regresszió) adják; ezeket **javítás után azonnal újrafuttatni pazarlás**, mert a javítás jellemzően egyetlen itemre irányult, és gyakran nem is sikerül elsőre.
>
> **A teljes kör lépéssorrendje is ezt szolgálja (VD13): olcsó → statikus → drága.** A Sonar és a kódreview stack nélkül fut, és a findingjaik javítása **megváltoztatja a kódot** — ezért mindkettő a nehéz tesztek **elé** kerül. Fordítva minden statikus finding ára egy eldobott E2E-futás lenne.

| Kör-típus | Mikor | Mi fut |
|---|---|---|
| **Teljes kör** | (a) a fázis **első** köre; (b) a **záró megerősítő** kör | 1. gyors tesztek → 2. **statikus réteg: Sonar + kódreview** (csak ha 1. zöld) → 3. nehéz tesztek + regresszió (csak ha 1–2. zöld) → 4. DoD/tasks/riport-kapu |
| **Könnyű kör** | minden **javítás utáni** kör, amíg zöld nem lesz | **a teljes gyors teszt-készlet** (unit/typecheck) + **kizárólag az(ok) a bukott item(ek)**, ami(k) nehéz teszt, Sonar vagy review-finding volt(ak) — semmi más. Review-findingnál a `reviewer` **inkrementálisan**, csak a nyitott `MF-NN`-ekre fut (RV2) |

**A hurok menete:**

```
1. kör      TELJES    → FAIL  → fix
2. kör      KÖNNYŰ    → FAIL  → fix
3. kör      KÖNNYŰ    → zöld  → NEM PASS! kötelező megerősítő kör
4. kör      TELJES    → PASS (vagy FAIL → a hurok folytatódik)
```

**Kötelező szabályok:**

1. **PASS kizárólag TELJES körből adható**, amelyben a **kódreview is lefutott és tiszta** (RV1). Egy zöld könnyű kör **nem** validálás — utána **azonnal** teljes megerősítő kör indul, ugyanabban a menetben, javítás nélkül. („Zöld volt a unit, biztos jó" → tilos.)
2. **A könnyű kör is EGY kör** (VD4a): a végén pontosan egy `failure-counter.py` bejegyzés készül, ugyanazokkal az item-nevekkel. A leállási korlátok (3/5/5) változatlanul számolnak.
3. **Ha a bukás nehéz teszt, Sonar vagy review-finding volt**, azt az **egy** itemet a könnyű körben is vissza kell igazolni (review-findingnál a `reviewer` inkrementális, csak a nyitott `MF-NN`-eket néző futásával), azaz le kell futtatni (különben nem lehet visszaigazolni a javítást) — de csak azt, nem a teljes nehéz készletet. Egyetlen E2E teszteset futtatásához a stack felhúzása is kell; ha ez nem oldható meg részlegesen (a plan szerint csak a teljes készlet futtatható), akkor **az a kör teljes lesz** — jelöld így a riportban.
4. **A gyors készletet nem szűkítjük.** A könnyű körben a **teljes** unit/typecheck suite fut (nem csak a bukott tesztfájl) — másodpercekbe kerül, viszont elkapja, ha a javítás máshol tört el valamit. Teszt-fájl kiválogatás nem a te dolgod.
5. **A stack életciklusa változatlan:** minden nehéz-teszt futás tiszta indítás + takarítás. Az inkrementális hurokkal ez tipikusan csak 2× történik meg egy validálásban.
6. **A kör típusát írd ki** a `## <sec:round> N` blokk fejlécébe: `— TELJES` vagy `— KÖNNYŰ`.

---

## Validálási lépések

### 0. Riport mappa előkészítése — körönkénti bontás (TR5)

A `test-report/` mappa **két rétegre** oszlik, és ezt a szétválasztást végig tartani kell:

```
specs/cycle-NN-<cycle-name>/test-report/
├── validation-report.md      ← a te riportod/naplód: több körre átívelő, APPEND-ONLY (soha nem írod felül egyben)
├── code-review.md            ← a reviewer findingjei (RV1) — a subagent írja, te értékeled
├── implement/                ← a 06 check-logja (nem te írod)
│   └── check-log.md
├── validate/
│   ├── round-01/             ← az 1. kör ÖSSZES artefaktuma (allure/unit/coverage/sonar-report.*)
│   └── round-02/             ← a 2. köré — az 1. körét SOHA nem írja felül
└── review/                   ← LEGACY: régi ciklusok 09-review köreiből maradhat (új ciklusban nem keletkezik)
```

**Minden kör elején hozd létre a saját mappáját:** `specs/cycle-NN-<cycle-name>/test-report/validate/round-NN/`, ahol `NN` **pontosan a `validation-report.md` `## <sec:round> N` sorszáma**, két számjegyre nullázva (`round-01`, `round-02`, …). Ez a párosítás adja a fázis egész értelmét: a lépés-táblából olvasott bukáshoz azonnal megnyitható a hozzá tartozó riport. **Ha a mappanév és a `## <sec:round> N` elcsúszik, a napló használhatatlan** — ellenőrizd a kör lezárásakor.

- **Korábbi körök mappáit nem törlöd, nem írod felül, nem takarítod.** Minden kör megmarad, a bukottak is — épp azok a legértékesebbek a hibanyomozáshoz.
- **A `validation-report.md` a `test-report/` gyökerében marad** (nem kör-mappában): ez a több körre átívelő napló, a `failure-counter.py` is ide fűz.
- **A kör-mappa útvonalát add át a `test-runner`-nek** minden hívásnál — a subagent nem találja ki, és ha nem kapja meg, visszakérdez.

- **A fenti lista ZÁRT (TR5/c).** A `test-report/` alatt **csak** `validation-report.md`, `code-review.md`, `implement/`, `validate/round-NN/` és a legacy `review/` létezhet. Ha bármi mást találsz — különösen `test-report/test-report/` vagy `test-report/specs/` nevű mappát —, az **elrontott útvonal-bázis nyoma, nem bizonyíték: töröld**, és futtasd újra a lépést a helyes bázissal. A fenti „korábbi körök mappáit nem törlöd" szabály **kizárólag a `validate/round-NN/` mappákra** vonatkozik. A `report-gate-check.py` layout-őre ezt determinisztikusan méri.

#### 0/a. A kör-mappa három útvonal-alakja (TR5/c)

Ugyanannak a mappának **három alakja van, három különböző bázissal**. A leggyakoribb hiba, hogy az egyik alakot a másik bázisát váró paraméterbe másolod — ilyenkor nem hibaüzenet keletkezik, hanem egy rekurzív riport-fa (`test-report/test-report/…`, `test-report/specs/…`), és a bizonyíték olyan helyre kerül, ahol a kapu nem találja meg.

| Alak | Bázis | Hol használod |
|---|---|---|
| `specs/cycle-NN-<cycle-name>/test-report/validate/round-NN` | repó gyökér | `run-tests.py --round-dir`, a `test-runner`-nek átadott útvonal, a `{round}` helyőrző értéke |
| `test-report/validate/round-NN` | ciklus-mappa | `report-gate-check.py --report-subdir` |
| `validate/round-NN` | `test-report/` | a `conventions.md` riport-parancsainak `<phase-dir>` helyőrzője vagy `REPORT_PHASE_DIR`-szerű környezeti változója, és a `{phase}` helyőrző |

> **🔴 Ha a `conventions.md` riport-generáló parancsa helyőrzővel vagy környezeti változóval kéri a fázis-mappát, oda a HARMADIK alak megy** (`validate/round-NN`) — soha nem a másik kettő. A `run-tests.py` minden futásnál kiírja a helyes értéket `REPORT_PHASE_DIR=` sorként: **azt másold**, ne azt az útvonalat, amit épp előtte begépeltél.
>
> A szkriptek mindhárom alakot elfogadják és normalizálják (`MEGJEGYZÉS (TR5/c)` sorral jelzik) — a `plan.md` gépi táblájában viszont a két helyőrző (`{round}` / `{phase}`) **nem cserélhető fel**: a `run-tests.py` a futtatás előtt ellenőrzi, és dupla prefix esetén `exit 3`-mal megáll.

**A riport-artefaktumok a ciklus részei — NEM kell őket kizárni a diffből.** A `git add specs/cycle-NN-<cycle-name>/` szándékosan beveszi a `test-report/` teljes tartalmát: a teszt-eszköz saját riportja (Allure/Playwright HTML, coverage, JUnit XML) az egyetlen utólag megnyitható bizonyíték a futásról. A méret ellen az egyfájlos HTML a védekezés (`--single-file`), nem a `.gitignore`. Ha korábbi ciklusból maradt `test-report/.gitignore`, amely a riportokat kizárja, **töröld** — különben a TR3 kapu olyan fájlt keres, ami sosem kerül be a repóba.

**A riportok a `conventions.md` `## <sec:cv_test_reporting>` táblája szerint kötelezők (TR3)** — a tábla utolsó oszlopa **a kör-mappához képest relatív** útvonal. A listát a `test-runner` állítja elő, és a PASS előtt determinisztikus kapu ellenőrzi (lásd „Kötelező teszt-riportok kapuja").

#### 0/b. A kör MEGNYITÁSA a `validation-report.md`-ben (VD9 — kötelező, a tesztek indítása ELŐTT)

> **🔴 Ez nem a kör végi feladat, hanem a kör első lépése.** A riport írása nem opcionális mellékhatás: a `validation-report.md` **a fázis kötelező outputja**. Ha ezt kihagyod, a `failure-counter.py` némán létrehozza a fájlt **csak** a `# <sec:validation_history>` szekcióval — a futás sikeresnek látszik, közben a riport üres. Pontosan ez a hiba, amit a VD9 tilt.

**Ne kézzel írd — a `round-log.py` csinálja.** A szkript létrehozza a fájlt (ha nincs), kiszámolja a kör sorszámát, megnyitja a `## <sec:round> N` blokkot a `# <sec:validation_history>` fejléc **elé**, és létrehozza a hozzá tartozó `round-NN/` mappát — így a mappanév és a kör-szám **strukturálisan** nem tud elcsúszni (TR5):

```bash
python3 <platform-scripts-mappa>/round-log.py open \
  specs/cycle-NN-<cycle-name>/test-report/validation-report.md \
  --type TELJES --timestamp "2026-08-10 10:32" \
  --trigger "07-validate első futás"
```

- A `--type` értéke `TELJES` vagy `KÖNNYŰ` (lásd „Kör-típusok"), a `--trigger` a kör indítója (első futás / hurok N. iterációja / megerősítő kör / megszakadt futás folytatása).
- A kimenet utolsó sora a **`round-subdir:`** — ezt az útvonalat add át a `run-tests.py`-nak, a `test-runner`-nek és a riport-kapunak.
- **Megszakadt futás folytatásakor** add hozzá a `--reuse-open` kapcsolót: ha az utolsó kör még `folyamatban`, nem nyit újat.

**A lépés-táblát menet közben töltsd** — minden futtatás és kapu után egy sor, azonnal:

```bash
python3 <platform-scripts-mappa>/round-log.py step \
  specs/cycle-NN-<cycle-name>/test-report/validation-report.md \
  --step "10:34|test-runner — gyors tesztek|npm test -- --run|✓ 43 passed / 0 failed / 0 skipped"
```

Így egy megszakadt futás után is látszik, meddig jutott (lásd „Megszakított futás kezelése").

### 1. Gyors tesztek — a legolcsóbb kapu (`run-tests.py`, fallback: `test-runner`)

> **Körtípus (VD10):** a **teljes gyors készlet minden körben fut** — teljes és könnyű körben egyaránt (VD10/4) —, mert másodpercekbe kerül, és elkapja, ha egy javítás máshol tört el valamit. **Sonar itt nem fut** (az a 2. lépés).
>
> **Ha ez a lépés bukik, a kör itt véget ér:** sem a statikus réteg (2.), sem a nehéz tesztek (3.) nem indulnak el. Nem fordítunk review-t és E2E-stacket olyan kódra, ami a unit-tesztek szintjén törött.

#### 1/a. Tesztek — **előbb szkripttel, subagent csak ha az nem megy**

> **🔴 A nyers teszt-log soha ne kerüljön kontextusba.** A futtatás és a darabszámolás gépi munka: ezt a `run-tests.py` végzi a `plan.md` **gépi futtatási táblájából**, és 10-20 sorban válaszol. A `test-runner` subagent a **fallback**, nem az alapeset.

```bash
python3 <platform-scripts-mappa>/run-tests.py \
  specs/cycle-NN-<cycle-name>/plan.md \
  --round-dir specs/cycle-NN-<cycle-name>/test-report/validate/round-NN \
  --type gyors --phase <status:phase_validate>
```

- **`exit 0/1`** → a kimenet kategóriánként tartalmazza a **kiadott parancsot** és a `X passed / Y failed / Z skipped` darabszámokat, bukásnál a bukott tesztek **pontos nevét** — ezek mennek szó szerint a `failure-counter.py --failed-item` értékeibe. A gépi eredmény a kör-mappa `results.json`-jában marad.
- **`exit 2`** → a `plan.md`-ben **nincs gépi futtatási tábla** (régi ciklus vagy hiányos plan). Ilyenkor **esel vissza a `test-runner` subagentre** (lásd 1/b), és a kör riportjában jelezd egy sorban, hogy a plan gépi táblája hiányzik — a `08-doc-sync`/`03` felé ez javítandó tétel, de **nem** a kör FAIL-je.
- **`exit 4`** → a tábla **környezet-hibás**: egy nem-lokálisnak deklarált kategória lokális célra mutat (EV5). **Ne futtass** — a zöld eredmény ilyenkor nem a telepített komponensről szólna. Ez a `03` hiánya: a parancs célpontját kell a deklarált környezethez igazítani, vagy a `<field:f_environment>` oszlopot `lokális`-ra javítani, ha tényleg ott fut. Az `implement-fixer` ezt nem javítja (nem a kód hibás) — VD5 szerint eszkalálj a `03`-ra.
- **A kimenet kategóriánként kiírja a KÖRNYEZETET is** (`@ dev`, `@ lokális`), és a `results.json`-ba is bekerül. **Ezt vidd be a kör lépés-táblájába**: a riportból utólag látszania kell, hol volt zöld a teszt — egy zöld JUnit XML önmagában nem árulja el, melyik hostot szólította meg.
- **`exit 3`** → a tábla **helyőrző-hibás**: a behelyettesítés dupla útvonal-prefixet ad (`test-report/test-report/…` vagy `test-report/specs/…`, TR5/c). **Ne futtass semmit, és NE ess vissza a `test-runner`-re** — a szkript kiírja, melyik sor és melyik mező hibás. Ez a `03` hiánya, nem kód-bug: javítsd a `plan.md` gépi tábláját a helyes helyőrzőre (`{round}` = teljes útvonal, `{phase}` = fázis-mappa — lásd 0/a), és futtasd újra. Ha a javítás nem egyértelmű, a VD5 szerint eszkalálj a `03`-ra.
- Könnyű körben egyetlen bukott kategória visszaigazolásához: `--only <kategória>`.

> **🔴 `EV6` — forgalmi bizonyíték a futtatás UTÁN.** Az `EV1–EV5` a **célpontot** védi a futtatás **előtt** (host a parancsban, elérhetőségi probe, `localhost`-tilalom). Az `EV6` a **forgalmat** védi a futtatás **után**: *egy zöld teszt nem bizonyítja, hogy egyáltalán elindult kérés.* Egy éles ciklusban a dev környezetre szánt E2E tesztek **egyetlen dev kérést sem** indítottak (a teszt-törzsek üres vázak voltak), a kör `rest-logs` mappája mégis telinek látszott — 50 naplófájllal, amelyek mind korábbi körből örökölt, `127.0.0.1`-es bejegyzések voltak.
>
> Ezért minden nem-lokális `<field:f_environment>`-ű kategóriára a szkript megnézi, hogy a `conventions.md` `## <sec:cv_test_reporting>` (TR3) táblájában deklarált **audit-artefaktumok** közt van-e olyan, amely **(a)** a kör alatt keletkezett és **(b)** tartalmazza a cél-hostot. Bukásnál a kategória `FAIL` (a `results.json`-ba is bekerül) — a javítás **nem** a napló bemásolása, hanem hogy a teszt tényleg megszólítsa a cél-környezetet (`VD3`).
>
> **Óvatossági ág:** ha a TR3 tábla **nem deklarál** audit-artefaktumot, az `EV6` csak **javaslat** (`·` sor, a `results.json` `suggestions` kulcsában) — nem minden projekt vállal REST-audit naplót, és egy ilyen projektet nem bukatunk meg olyanért, amit nem is vállalt. A `--conventions` alapértéke a repó gyökerében lévő `conventions.md`; ha nem létezik, a check kimarad.

#### 1/b. Fallback: `test-runner` subagent

Ha a `run-tests.py` `exit 2`-t adott (nincs gépi tábla), hívd a `test-runner` subagentet (`agents/test-runner.md`) a gyors (unit/integration) tesztek lefuttatására. A subagent **strukturált összefoglalót** ad vissza (lásd az agent kontraktusát) — a nyers teszt-logot nem kéred vissza.

> **🔴 Ha a subagent `## Futtatás blokkolva (EX1)` szekcióval tér vissza** — egyes platformokon (pl. Antigravity) a subagent **nem tud parancs-jóváhagyást kérni**, ezért nem tud tesztet futtatni —, akkor:
> 1. **Ne indítsd újra** a subagentet, és **ne fogadd el** semmilyen becsült eredményét (a jelentésben nem is lesz).
> 2. **Futtasd le te magad** a `run-tests.py`-t: fő ágensként nálad a jóváhagyás működik. Ez a platformon az **egyetlen** működő út, ezért ott a `plan.md` gépi futtatási táblája nem opcionális.
> 3. **Ha a tábla is hiányzik** (`exit 2`) **és** a subagent is blokkolt: a tesztek ezen a platformon nem futtathatók automatikusan → **STOP + humán** a „Hol járunk" fejléccel: *„A tesztek nem futtathatók: a `plan.md`-ben nincs gépi futtatási tábla, a `test-runner` subagent pedig ezen a platformon nem tud parancsot futtatni (EX1). Két megoldás: (a) egészítsük ki a `plan.md`-t a gépi táblával a 03 fázisban, vagy (b) engedélyezd a szükséges parancsokat a platform auto-futtatási listáján."* **Soha ne zárd PASS-ra a kört futtatás nélkül.**

> **🔴 A hívásban kötelezően add át a kör riport-mappáját** (TR5): `specs/cycle-NN-<cycle-name>/test-report/validate/round-NN/` — az aktuális `## <sec:round> N` sorszámával. A subagent minden artefaktumot (beleértve a `sonar-report.md`/`.html`-t) ide tesz. Add át azt is, **mely kategóriákat** futtatja ebben a körben, hogy könnyű körben ne generáljon félrevezető riportot a nem futott kategóriákhoz.

**A subagent két forrásból dolgozik, semmi másból (TR4):** minden **ciklus-specifikus** technikai részletet (parancsok, URL-ek, portok, teszt-userek, token-szerzés, indítási sorrend, előfeltételek) a **`plan.md`** `<sec:testing_strategy>` / `<sec:regression_impact>` / `<sec:e2e_infrastructure>` szekcióiból vesz — ezért írta a 03 fázis kötelezően **önhordóra** a plant (TC1/a) —, a **projekt-szintű eszköz-információt** (futtató, mappastruktúra, riport-tábla, Sonar-parancsok) pedig a `conventions.md`-ből. A `test-conventions.md`-t **nem olvassa**, régi ciklusokból nem dolgozik, és **nem találgat**. Az indításkor **hivatkozz rá explicit**, hogy a plan a ciklus-specifikus igazságforrás.

**Bizonyíték-ellenőrzés (TR1/TR2):** a `run-tests.py` ezt **automatikusan teljesíti** (a parancsot és a darabszámokat gépi forrásból adja, és a `0 passed / 0 failed` esetet magától FAIL-nek jelöli — `TR2`). A lenti szabályok a **fallback ágra** (`test-runner` subagent) vonatkoznak: minden kategóriánál ott kell lennie a **kiadott parancsnak** és a **darabszámoknak** (`X passed / Y failed / Z skipped`). Ha egy kategóriánál hiányzik a bizonyíték, vagy `0 passed / 0 failed` szerepel, azt **ne fogadd el PASS-nak**:
- Ha a `plan.md` Tesztelési stratégiája szerint annak a kategóriának léteznie kell → ez **FAIL** (`--failed-item "<kategória>: 0 teszt futott"`), nem zöld eredmény.
- Ha a plan szerint a kategória szándékosan nem létezik → `N/A`, és ezt írd is ki a kör lépés-táblájába.
- Ha a subagent bizonyíték nélkül jelentett, **kérd újra** tőle a hiányzó adatot, mielőtt döntesz. A saját feltételezésed nem pótolja a futtatást.

**Plan-hiány kezelése (TR4) — nem kód-bug, ne indíts rá fixert.** Ha a jelentés `## Plan-hiány (TR4)` szekciója nem üres (a runner azért hagyott ki egy tesztcsoportot, mert egy futtatási részlet nincs a `plan.md`-ben — pl. nincs leírva a lokális Keycloak indítása, hiányzik a teszt-user vagy a token-szerzés):

1. **Nézd meg magad a `plan.md`-ben** — a runner tévedhetett, vagy más szekcióban van. Ha ott van, add át neki explicit, és futtasd újra azt a csoportot.
2. **Ha tényleg hiányzik:** ez a **03 fázis hiánya**, nem az implementációé. A `implement-fixer` ezt nem tudja megjavítani (nem a kód a hibás), ezért **ne indíts hurok-iterációt rá**. Ehelyett **eszkalálj a tervezéshez** a VD5 felfelé menekülő ág szerint: a `plan.md` státusza `<status:draft>`-ra, egyetlen lezáró commit, és a felhasználónak szóló üzenetben **tételesen sorold fel, mi hiányzik** és melyik teszthez kell:
   > **[VALIDATE · plan-hiány · <teszt> ]**
   > *„A(z) `<tesztcsoport>` nem futtatható: a `plan.md` nem tartalmazza a(z) `<hiányzó adat>`-ot (pl. a lokális Keycloak indítási parancsát és a teszt-user adatait). Ez tervezési hiány, nem kód-hiba — a `test-runner` szándékosan nem találgat. A `plan.md` státuszát visszaállítottam; egészítsd ki a `<sec:testing_strategy>` szekciót önhordóan (TC1/a), majd a `05→06→07` úton térünk vissza ide."*
3. **A lefutott tesztcsoportok eredményét ettől függetlenül naplózd** a kör riportjába — a kör FAIL, a kihagyott csoport a lépés-táblában „<status:skipped> — plan-hiány" sorként jelenik meg.

### 2. Statikus réteg — Sonar + kódreview egy batchben (RV1/RV2/VD13)

> **Miért itt, a nehéz tesztek ELŐTT (VD13)?** A Sonar és a review az egyetlen két ellenőrzés, ami **nem igényel futó stacket** — és mindkettő olyan hibákat talál, amiknek a javítása **megváltoztatja a kódot**. Ha a nehéz tesztek (E2E + regresszió) előbb futnának, minden statikus finding ára egy eldobott E2E-futás lenne: a fix után a stack-et úgyis újra fel kell húzni. A hurok költségének nagy részét épp ez adja (VD10), ezért a sorrend: **olcsó → statikus → drága**.
>
> **Körtípus (VD10/RV2):** **teljes** körben mindkettő fut. **Könnyű** körben csak az(ok), ami(k) a visszaigazolandó bukás forrása volt(ak):
> - Sonar-eredetű bukás (`Sonar QG: …`) → a Sonar újra fut, a review nem;
> - review-finding (`MF-NN`) → a `reviewer` **inkrementálisan** fut, kizárólag a nyitott `MF-NN` findingokra (a teljes diff újra-review-ja tilos);
> - egyébként a lépés **kimarad**, a lépés-táblába `<status:skipped> — könnyű kör (VD10)` sor kerül.
>
> **A két ellenőrzés eredményét EGYÜTT értékeled** — lásd a 2/c pontot. Ne indíts fixert a Sonar findingjeire, amíg a review is le nem futott ugyanabban a körben.

#### 2/a. Sonar Quality Gate — `sonar-gate.py` (ne riportot olvass)

Ha a `conventions.md` tartalmaz `## <sec:cv_sonar>` szekciót, az elemzés futtatása után a kaput a szkript értékeli — a `sonar-report.md`/`.html` bizonyítéknak marad, de **nem olvasod el**:

```bash
python3 <platform-scripts-mappa>/sonar-gate.py \
  --out specs/cycle-NN-<cycle-name>/test-report/validate/round-NN/sonar-report.md
```

A kilépő kód dönt, nem a saját ítéleted:
- **`0`** → Quality Gate OK (a `MINOR`/`INFO` találatok nem blokkolnak);
- **`1`** → QG FAIL **finding miatt** — a kiírt `BLOCKER`/`CRITICAL`/`MAJOR` lista a javító-taskok forrása (a szűrés már megtörtént, nem neked kell);
- **`3`** → QG FAIL **küszöb miatt, blokkoló finding nélkül** — ez a **QG1 ág** (lásd lent): tilos üres hibalistával fixert indítani;
- **`2`** → használati hiba (nincs URL/projectKey/token) → a Sonar-futtatás a `test-runner` subagenten keresztül megy, a régi módon.

> **A Sonarról külön rendelkezz** — a subagent nem találgat: ha nem mondod meg, **futtatja**. Könnyű körben tehát írd ki explicit, hogy *„Sonar: kihagyva ebben a körben"* (kivéve, ha épp Sonar-eredetű bukást igazolsz vissza — akkor *„Sonar: fusson"*). A jelentésben ilyenkor `kihagyva (a hívó kérésére)` áll, ami **nem** PASS és **nem** N/A: a kör értékelésénél ne minősítsd zöldnek, és ne is vegyél fel rá javító-taskot.

A subagent jelentése alapján:
- **Quality Gate PASS / N/A:** a kör-mappába került `sonar-report.html` és `.md` riportok tájékoztató jellegű `MINOR`/`INFO` találatai nem akadályozzák a validálást.
- **Quality Gate FAIL vagy bármelyik gyors teszt FAIL:** **ne indítsd el a 3. lépést (nehéz tesztek)** — a kör eredménye FAIL, lépj a naplózásra, majd a hurok FAIL ágára. A javító feladatok (`tasks.md`) felvételekor csak a `BLOCKER`, `CRITICAL` és `MAJOR` szintű Sonar-találatokat tekintsd kötelezően javítandó akadálynak (a subagent az összeset jelenti, a szűrés itt, nálad történik).
- **Quality Gate FAIL, de nincs `BLOCKER`/`CRITICAL`/`MAJOR` találat (QG1 — a `sonar-gate.py` `exit 3`-a):** a kaput nem finding, hanem **küszöb** buktatta (lefedettség, duplikáció, új kód minőségi kapuja) — a szkript kiírja, melyik feltétel és milyen értékkel. Ilyenkor **tilos** üres hibalistával fixert indítani — a hurok üresben forogna. Teendő:
  - Ha a `sonar-report.md`-ből egyértelmű a bukott feltétel és az **kód-oldalon javítható** (tipikusan: hiányzó teszt-lefedettség az új kódon) → vedd fel konkrét javító-taskként (pl. *„Fedd le tesztekkel a `<fájl>` új ágait — a QG coverage küszöbe X% alatt van"*), és a `--failed-item` neve a bukott feltétel legyen (pl. `Sonar QG: coverage on new code`).
  - Ha a bukott feltétel **nem a ciklus hatókörében** javítható (pl. örökölt duplikáció, projekt-szintű küszöb) → ez nem kód-bug: **STOP + humán**, a *„Hol járunk"* fejléccel, a bukott feltétel megnevezésével és két javaslattal (küszöb felülvizsgálata a `conventions.md`-ben, vagy külön ciklus). Ne indíts fixert.

#### 2/b. Kódreview — `reviewer` subagent (RV1)

> A review a **gyors tesztek után, de a nehéz tesztek előtt** fut: a diff ilyenkor már fordul és unit-szinten zöld, tehát nem félkész kódot nézünk, viszont a findingjai még azelőtt javíthatók, hogy bármi drágát futtattunk volna rá.

1. **Indítsd a `reviewer` subagentet** (`agents/reviewer.md` rendszerprompt), átadva neki:
   - a ciklus branch és a fő branch közötti `git diff`-et (a `conventions.md` Merge stratégiájában megnevezett target branch-hez képest) — **a diffet te futtatod le és adod át**, ne bízd a subagentre: több platformon nem tud parancsot futtatni (EX1). **A diffet szűkítsd a forráskódra (RV-SC)** — ez a fázis egyik legnagyobb token-tétele:
     ```
     git diff <target>...HEAD -- . ':(exclude)specs/**' ':(exclude)*.lock' ':(exclude)package-lock.json'
     ```
     Egészítsd ki a `conventions.md`-ben **generáltként** megnevezett könyvtárakkal (tipikusan `dist/`, `build/`, `docs-generated/`). Indok: a tervezési dokumentumok diffjének átnézése **tiszta duplikáció** — a `spec.md`-t és a `plan.md`-t a reviewer amúgy is **teljes fájlként, külön** megkapja, és a „spec eltérés" ítéletet azok **aktuális** tartalmához méri, nem a változásukhoz; a generált kimenet és a lockfile-ok pedig nem review-tárgyak. **A teszteket NE zárd ki** — a teszt-kód review-ja a legértékesebbek közé tartozik (egy hiányzó mock-stub például csak ott látszik).
   - a `conventions.md`-t, a `plan.md`-t és a `spec.md`-t,
   - **ha már volt review ebben a fázisban:** az előző `test-report/code-review.md`-t, azzal az explicit kéréssel, hogy a **még nyitott** `<status:must_fix>` findingokra fókuszáljon, és a lezártakat jelölje lezártként (inkrementális re-review — ne írja újra nulláról a jelentést).
2. A subagent a jelentést a **`specs/cycle-NN-<cycle-name>/test-report/code-review.md`** fájlba menti.
   > **Ha a subagent nem fut le, vagy nem készít `code-review.md`-t:** ez **nem** kód-bug, ezért **nem indítasz fixert**. A teendőt a **hiba típusa** dönti el — ne mérlegelj, nézd meg a hibaüzenet szövegét:
   > - **Platform-korlát** (a szövegben kvóta/keret/limit szerepel — pl. „usage limit", „quota exceeded", „reached its usage limit", vagy egy keret-reset dátum): **NE próbáld újra.** A második hívás determinisztikusan ugyanabba fut, és egy kört pazarol el. Ugorj azonnal a STOP + humán ágra, és a kérdésbe **másold be a hibaüzenetet szó szerint** (a reset-dátummal együtt) — a döntés (admin-engedély, várakozás a resetig, másik modell-pool) a felhasználóé, nem a tiéd.
   > - **Minden más hiba** (időtúllépés, egyszeri összeomlás, üres válasz): próbáld újra **egyszer**.
   >
   > Ha a subagent így sem futtatható: **STOP + humán** a „Hol járunk" fejléccel — kérdezd meg, hogy próbáljam-e újra, vagy végezzem el a review-t közvetlenül a `reviewer.md` szempontjai szerint a fő ágensben.
   >
   > **🔴 Ha a fallback ágra mész (a review a fő ágensben készül), a jelentés eredetét KÖTELEZŐ jelölni.** A fallback más modellen és szűkebb kontextusban fut, mint a `reviewer` subagent, ezért rendszeresen gyengébb lelet — aki később a riportot olvassa, ezt lássa:
   > - a `code-review.md` fejlécébe egy sor: **Készítette:** fő ágens (fallback) — a reviewer subagent nem volt futtatható: <ok>;
   > - a kör lépés-táblájában a lépés neve `kódreview (2/b, RV1) — fallback: fő ágens` legyen, **soha ne** `reviewer subagent`;
   > - az `## <sec:closing_summary>` szekcióba írd be, hogy a subagent-review pótlása ajánlott;
   > - és egy **második kötelező sor** a fejlécbe: **Szempontlista:** `RV-FB1` — mind a <N> pont végigjárva (vagy a kihagyott pont megnevezése, indoklással). Enélkül a fallback szigora ismét önbevallás (`7/j`).

   > **🔴 Fallback módban UGYANEZT a listát kell végigjárnod, tételesen (RV-FB1).** A fallback nem „egy gyors diff-összegzés": a `reviewer` subagent szempontlistája alább **szó szerint** ott van, és fallback esetén **te** vagy a reviewer. Menj végig **minden** ponton, és a `code-review.md`-ben nevezd meg, hol teljesül vagy hol nem — különösen a **Teszt lefedettség** ponton: egy éles ciklusban épp a fallback ág futott, és épp ez a pont maradt ki, ezért nem derült ki, hogy a „megírt" tesztek üres vázak (`assert True`). A fallback jelölése (fentebb) az **eredetet** rögzíti, nem a szigor csökkentését engedi meg.

<!-- INCLUDE:shared/review-checklist.md -->

3. **Értékeld a jelentést:**
   - **A fejlécben `<field:f_status>` = `<status:in_progress>`** → a reviewer **nem fejezte be** a jelentést (megszakadt futás — RV-INC). A review-kapu **nem zárható le vele**: sem zöldre, sem FAIL-re. A már kiírt findingok viszont **valósak, csak hiányosak** — ne dobd el és ne írd felül őket; kezeld a lépést a 2. pont hiba-ága szerint, és a részleges findingokat vidd tovább a következő review bemenetébe. A `validate-gate-check.py` ezt gépileg is elbukja.
   - **Nincs lezáratlan `- [ ]` a `<sec:critical_fixes>` szekcióban** (és a fejléc `<status:done>`) → a review-kapu ✓. Ha a Sonar is zöld, a statikus réteg zöld → mehet a 3. lépés (nehéz tesztek).
   - **Van lezáratlan `<status:must_fix>`** → a **kör FAIL** (nem külön hurok!): a findingok a kör bukott elemei közé kerülnek, és a naplózásnál `--failed-item`-ként adod át őket.
     > **🔴 Item-név review-findingnál:** a `code-review.md`-ben szereplő finding **azonosítója** legyen (`MF-01`, `MF-02`, …), soha ne a parafrazeált szövege — a leállási korlát szó szerinti névegyezésre épül (ugyanaz a szabály, mint a `DoD-NN`-nél). Ha a reviewer nem adott azonosítót, **pótold a `code-review.md`-ben** sorfolytonosan, mielőtt naplózol.
   - **`Suggestions` szekció:** **nem blokkol.** Ha egy javaslat a ciklus scope-ján belül van és kockázat nélkül alkalmazható, javítsd direktben (a következő kör úgyis leteszteli); ha scope-on kívül esik vagy bizonytalan, hagyd a listában jövőbeli ciklusnak — ne kezdj scope creepet. A `Suggestions` **soha nem** kerül a `--failed-item`-ek közé.

#### 2/c. A findingok összevonása — egy fix-batch (VD13)

A Sonar `BLOCKER`/`CRITICAL`/`MAJOR` találatai és a nyitott `<status:must_fix>` findingok **ugyanannak a körnek a bukott elemei**: egy listába kerülnek, egy `failure-counter.py` hívásba, és **egy fixer-menetben** javulnak (Sonar-eredetűek → `implement-fixer`, review-eredetűek → `review-fixer`; ha mindkettő van, a hurok 6. pontja szerinti sorrendben: előbb az `implement-fixer`, utána ugyanabban az iterációban a `review-fixer`). Így egy körhöz **egy** VD3a szerződés-integritás kapu tartozik, nem kettő.

**Ha a statikus réteg bármelyik fele bukik, a nehéz teszteket (3.) NE indítsd el** — a kör eredménye FAIL, lépj a 4. lépés kapuira csak annyiban, amennyi bizonyíték már rendelkezésre áll, majd a naplózásra és a hurok FAIL ágára.

### 3. Nehéz tesztek és regressziós ellenőrzések (`test-runner` subagent)

> **Körtípus (VD10):** **teljes** körben a nehéz tesztek + a **teljes** regressziós készlet fut. **Könnyű** körben ez a lépés **kimarad** — kivétel: ha a javítandó bukás maga nehéz teszt volt, akkor **kizárólag az az egy item** fut (VD10/3).

Csak akkor futtasd, ha az **1. és a 2. lépés is zöld volt** — a nehéz tesztek csak olyan diffre érdemesek, ami már statikusan tiszta. **Elsődlegesen szkripttel** — ugyanaz a tábla, más típus-szűrő:

```bash
python3 <platform-scripts-mappa>/run-tests.py \
  specs/cycle-NN-<cycle-name>/plan.md \
  --round-dir specs/cycle-NN-<cycle-name>/test-report/validate/round-NN \
  --type nehez --phase <status:phase_validate>
```

A tábla `<field:f_prerequisite>` és `Takarítás` oszlopa tartalmazza a stack indítását és lebontását — a takarítás akkor is lefut, ha a futtatás elszállt. `exit 2` (nincs gépi tábla) esetén hívd a `test-runner` subagentet, most a nehéz tesztek (E2E + regresszió) lefuttatására — a `tasks.md` `TREG` jelölésű taskjai és a `plan.md` `<sec:regression_impact>` táblázata alapján. **Ugyanazt a kör-mappát add át, mint az 1. lépésben** (TR5) — egy körhöz egy mappa tartozik, a gyors és a nehéz tesztek artefaktumai egymás mellé kerülnek. A subagent felelőssége a szükséges backend szolgáltatások/konténerek elindítása, a portütközés-elhárítás és az ideiglenes erőforrások takarítása (lásd az agent kontraktusát).

> **⚠ Átmeneti port-módosítás:** ha a subagent jelentése ideiglenes config-/port-csere kell, ellenőrizd, hogy a jelentés szerint sikeresen visszaállt-e az eredeti állapot; ha nem, állítsd vissza te (`git checkout -- <fájl>`), mielőtt a validate fázis véget ér — ez nem kerülhet be a ciklus diffjébe.

**Egy funkció csak akkor kész, ha minden teszt, a Sonar és a kódreview is átment.** Részleges PASS nem elfogadható: ha bármelyik teszt, a Sonar vagy a review hibázik, az egész validate FAIL.

### 4. DoD, tasks és riport-kapu ellenőrzések

#### A. <sec:definition_of_done> ellenőrzése — **előbb szkripttel** (`dod-check.py`)

Ha a `spec.md` DoD-pontjai megnevezik a **bizonyítékukat** (`· _bizonyíték:_ \`<tesztnév>\`` / `\`cmd: <parancs>\`` / `\`manual: <mit>\``), a kiértékelés **join** a kör futási eredményeivel — nem ítélet:

```bash
python3 <platform-scripts-mappa>/dod-check.py \
  specs/cycle-NN-<cycle-name> \
  --round-dir specs/cycle-NN-<cycle-name>/test-report/validate/round-NN --apply
```

- **`exit 0`** → minden DoD-pont bizonyítottan ✓ (a szkript a `--apply`-jal ki is pipálta őket a `spec.md`-ben);
- **`exit 1`** → van ✗ — a kiírt `DoD-NN` azonosítók mennek szó szerint a `failure-counter.py --failed-item` értékeibe;
- **`exit 3`** → van `?` (bizonyíték nélküli vagy `manual:` pont) — **csak ezekhez** kell a saját ítéleted: adj rájuk ✓/✗-ot egy mondatos indoklással. A bizonyíték hiánya egyben **spec-minőségi jelzés** a 02/05 felé — jegyezd fel a kör riportjába, de ne minősítsd emiatt FAIL-nek a kört;
- **`exit 2`** → a DoD-pontoknak nincs `DoD-NN` azonosítójuk → pótold őket a `spec.md`-ben (lásd lent), és futtasd újra.

**A pontokra mindig a `DoD-NN` azonosítójukkal hivatkozz** (DI1) — a riportban, a naplóban és a javító-taskokban egyaránt.

> **⚠ A `--apply` nélkül futtatva** neked kell minden teljesített (`✓`) pontot `[x]`-szel jelölnöd a `spec.md` megfelelő sorában — ne várd meg a teljes validálás végét. (Ez a `spec.md`-t commitálatlanul módosítja; a hurok alatt ez így helyes — a commit a hurok végén, egyszer történik, VD8.)

> **🔴 Item-név DoD-bukásnál:** a `failure-counter.py` `--failed-item` értéke **pontosan a `DoD-NN` azonosító** legyen (pl. `--failed-item "DoD-03"`), soha ne a pont parafrazeált szövege. A számláló szó szerinti név-egyezésre épül: körönként másképp megfogalmazott szöveg mellett a leállási korlát csendben soha nem lép életbe. **Ha a `spec.md` DoD-pontjainak nincs `DoD-NN` azonosítójuk** (régebbi ciklus), **először pótold őket a `spec.md`-ben** (sorfolytonosan, a meglévő sorrendben), és csak utána naplózz — a pótlás nem tartalmi változtatás, nem sérti a VD3-at.

#### A/2 + B. A többi kapu egyetlen hívásban (`validate-gate-check.py`)

Nyitott taskok, nyitott DoD-pipák, `validate-input-from-prev.md` lezáratlan tételei (IP1), nyitott `<status:must_fix>` (RV1), a kör-blokk ↔ `round-NN/` mappa egyezése (VD9-guard, TR5), a `[CHECK]` parancsok szó szerinti, taskonkénti futása (CK1), és a `[RED]` taskok bukás-bizonyítéka a `check-log.md`-ben (RED1) — mind regex-kérdés, egyetlen hívással:

```bash
python3 <platform-scripts-mappa>/validate-gate-check.py \
  specs/cycle-NN-<cycle-name> --stage close [--require-review]
```

- **`exit 0`** → minden vizsgált kapu rendben;
- **`exit 1`** → a kiírt ✗ pontokat rendezd (nyitott task → vissza a 06-ra vagy javító-task; nyitott `[ ]` tétel az `input-from-prev`-ben → zárd le indoklással; hiányzó kör-blokk → `round-log.py`);
- **`exit 2`** → nem létező ciklusmappa (elgépelt útvonal).

A `--require-review` a **PASS előtti** futtatáshoz kell: ott a `code-review.md` hiánya bukás. Korábbi körökben (amikor a review el sem indult) hagyd el.

**Teszt-tartalom kapu (TB1) — önálló parancs, ugyanebben a szakaszban:**

```bash
python3 <platform-scripts-mappa>/test-substance-check.py specs/cycle-NN-<cycle-name>
```

- **`exit 0`** → a plan `TA1` adatlapjaiban felsorolt tesztfájlokban nincs üres váz;
- **`exit 1`** → a kör **FAIL**, és a bukás típusa **teszt-hiba** → az `implement-fixer` indul a `## <sec:validation_fixes>` szekcióval. **A `VD3` garde ide is szól:** a vacuous teszt javítása a teszt **megírása** — nem a check kikapcsolása, nem a fájl kivétele a plan adatlapjaiból, és nem az asszertáció „odaírása" úgy, hogy triviálisan igaz legyen.

> **🔴 A `CK1` bukása nem a napló hibája (VD3).** Ha a kapu azt írja, hogy egy naplósor `Task` cellája intervallumot hordoz, vagy hogy a naplózott parancs nem tartalmazza a task teszt-szűrőjét, **a napló utólagos átírása nem javítás** — a `[CHECK]`-eket **újra kell futtatni egyenként**, szó szerint, ahogy a `tasks.md` írja, és az új futásokat naplózni. Egy összevont futás azt is elrejti, hogy a `tasks.md` szelektora már nem létező teszt-függvényre hivatkozik. Ha a keret tényleg nem tud eset-szintűre szűrni, az a `check-log.md` `## <sec:notes>` szekciójában egy `CK-DEVIATION: <task> — <indok>` sor — **indoklás nélkül nem**.

> **🔴 Egy zöld `[RED]` nem javítható a napló átírásával (RED1/VD3).** Ha a kapu azt írja, hogy egy `[RED]` taskhoz nincs bukott (`✗`) futás, a hiányzó bizonyítékot **nem** utólag beírt naplósor pótolja: a tesztet kell megírni úgy, hogy implementáció nélkül **tényleg bukjon** (egy `assert True` váz fizikailag nem tud vörös lenni — ezért ez a legerősebb, ítélet-mentes jel). A `[RED]` task ilyenkor **nincs elvégezve** → vissza a `06`-ra a `## <sec:validation_fixes>` szekcióval. Kivétel csak a `RED-EXEMPT: <task> — <indok>` sor (meglévő tesztet frissítő, joggal zöld regressziós task) — ez a `VD3` anti-teszt-csalás garde alá tartozik.

> **Ami marad neked (IP1):** ha egy `input-from-prev` tétel a validálás során **hibát okozott** (pl. hiányzó előfeltétel miatt bukott el egy teszt), az FAIL — a szokásos hurok szerint javítandó, nem elvetéssel elintézendő. A szkript csak azt látja, hogy nyitva van-e; azt, hogy *figyelembe vetted* vagy *elvetetted*, te írod bele.

#### B/2. Kötelező teszt-riportok kapuja (TR3 — determinisztikus)

A `conventions.md` `## <sec:cv_test_reporting>` táblájában deklarált riport-artefaktumoknak ott kell lenniük **az aktuális kör mappájában**. Ezt **ne szemre nézd meg** — futtasd a kaput, a kör-mappát átadva:

```bash
python3 <platform-scripts-mappa>/report-gate-check.py \
  conventions.md specs/cycle-NN-<cycle-name> \
  --report-subdir test-report/validate/round-NN
```

> **🔴 A kapu csak TELJES körben fut (TR5/VD10).** Könnyű körben szándékosan nem fut minden tesztkategória, így a teljes riport-tábla **nem is teljesíthető** — a kapu ilyenkor **kimarad**, és a `## <sec:round> N` lépés-táblájában „kihagyva — könnyű kör (VD10)" sorként jelenik meg. Ez nem lazítás: a PASS eleve csak teljes körből adható (VD10/1), és ott a kapu `exit 0`-ja **kötelező** feltétel.
>
> _(Korábban a kapu minden körben futott, de fix fájlnevekre — ilyenkor a könnyű kör az ELŐZŐ kör bennmaradt artefaktumát találta meg, és hamis zöldet adott. A körönkénti mappa ezt megszünteti, ezért kell a körtípus szerinti szabály.)_

- **`exit 0`** → a kapu ✓ (vagy a projekt explicit nem generál riportot, vagy a vizsgált fázis nem riport-fázis — TR6). Az eredményt írd be a kör riportjába.
- **A kapu a `test-report/` layoutját is méri (TR5/c):** idegen mappa a `test-report/` alatt `exit 1` — ez nem hiányzó riport, hanem elrontott útvonal-bázis. A kapu megnevezi a mappát és az okot; töröld, és a hibás lépést futtasd újra a helyes bázissal (0/a). Fixert erre sem indítasz.
- **`exit 1`** → hiányzó vagy üres artefaktum. **A kör nem zárható PASS-ra**, de ez **nem kód-bug**, ezért **nem indítasz fixert**: a riport előállítása a `test-runner` dolga.
  1. Hívd újra a `test-runner`-t **kifejezetten a hiányzó riport(ok) előállítására**, a táblában megadott paranccsal, és kérd, hogy az artefaktumot **az aktuális kör mappájába** tegye (a konkrét útvonalat add át).
  2. Futtasd újra a kaput. Ha másodszorra is bukik → **STOP + humán** a „Hol járunk" fejléccel: *„A(z) [artefaktum] riport két próbálkozásra sem jött létre a `<parancs>` paranccsal. Humán beavatkozás szükséges — hogyan tovább?"*, a szkript kimenetével együtt.
- **`exit 2`** → a `conventions.md` `## <sec:cv_test_reporting>` szekciója hiányzik vagy kitöltetlen (placeholder maradt). Ez **projekt-konfigurációs hiány**, nem teszt-hiba: **STOP + humán**, és kérd a szekció pótlását a `00-init` szerinti tartalommal (kategória / eszköz / parancs / artefaktum, vagy explicit `**<field:f_report_required>:** nem` + indoklás). Magad ne találd ki a parancsot, és **ne írd át a `conventions.md`-t** — az a 00 fázis és a felhasználó közös döntése.

> A kapu **minden TELJES körben** fut, nem csak az utolsóban — és mivel minden kör a saját mappájába dolgozik, a bukott körök riportja is megmarad: utólag megnyitható, mi bukott el konkrétan a 2. körben. A könnyű körök artefaktumai (a gyors tesztek riportja) ugyanígy megmaradnak a saját mappájukban, csak a kapu nem kéri őket számon.

> **Ami szándékosan NINCS itt (VD12):** a **komponens-README-k** és a generált dokumentáció szinkronja a `08-doc-sync` dolga (annak explicit outputja, saját DS22 kapuval). A **kódkommentek / JSDoc** elavulás-vizsgálata viszont **ide tartozik**: azt a 2. lépés `reviewer` ágense végzi, aki amúgy is végigolvassa a diffet. **Te magad (az orchestrátor) továbbra sem olvasod végig a módosított fájlokat** — a diff-olvasás a subagent dolga, te a jelentését értékeled.

### Naplózás és leállási korlátok (VD4 — determinisztikus, szkripttel)

> **🔴 EGY VALIDÁLÁSI KÖR = EGY futás-bejegyzés (VD4a).** Egy kör az 1–4. lépés (gyors tesztek → statikus réteg [Sonar + kódreview] → nehéz tesztek → DoD/tasks/riport-kapu) — **a könnyű kör is teljes értékű kör** (VD10): a végén ugyanúgy pontosan egy bejegyzés készül, ugyanazokkal az item-nevekkel. A kör eredményét **a kör VÉGÉN, egyetlen `failure-counter.py` hívással** naplózod, az összes bukott itemmel együtt. **TILOS részeredményt külön naplózni** (pl. „a gyors tesztek zöldek" bejegyzést az 1. lépés után): egy közbeiktatott PASS-bejegyzés **megszakítja az egymást követő bukások láncát**, és a 3-próba leállás soha nem lépne életbe — a hurok végtelenné válik. Az 1–4. lépés részeredménye a kör **lépés-táblájába** kerül (lásd „A `validation-report.md` — teljes validálási riport"), nem a History-ba.
>
> Mikor zárul a kör (mi kerül egy bejegyzésbe)?
> - **Az 1. lépés (gyors tesztek) bukott** → a kör itt véget ér (sem statikus réteg, sem nehéz tesztek): egy FAIL bejegyzés a gyors teszt-itemekkel.
> - **Az 1. zöld, a 2. (statikus réteg) bukott** → **egy** FAIL bejegyzés, amiben a Sonar-item(ek) **és** az `MF-NN` findingok együtt szerepelnek (VD13) — a nehéz tesztek nem futnak.
> - **Az 1–2. zöld, a 3. (nehéz tesztek) bukott** → egy FAIL bejegyzés a nehéz teszt-itemekkel (a zöld gyors teszteket és a tiszta review-t nem naplózod külön).
> - **Az 1–3. zöld, a 4. (DoD/tasks/riport-kapu) bukott** → egy FAIL bejegyzés a bukott `DoD-NN` azonosítókkal.
> - **Minden zöld** → egy PASS bejegyzés, `--failed-item` nélkül.

**A futás-bejegyzést és a számlálókat NE kézzel írd/számold** — a `failure-counter.py` szkript végzi. A szkriptek útvonala a telepített skillben **konkrét értékre van feloldva** (a telepítő platformonként cseréli: `.claude/scripts/` / `.agents/scripts/` / `.cursor/scripts/` / `.github/scripts/` / `.codex/scripts/`); ha mégis `<platform-scripts-mappa>` alakot látsz, a fenti öt közül keresd meg, melyik létezik a projektben. A `test-runner` által **szó szerint** visszaadott bukott-item neveket add át neki (DoD-bukásnál a `DoD-NN` azonosítót — lásd a 3./A. lépést):

```bash
# FAIL — minden bukott itemet külön --failed-item-ként (a test-runner szó szerinti nevein):
python3 <platform-scripts-mappa>/failure-counter.py \
  specs/cycle-NN-<cycle-name>/test-report/validation-report.md \
  --result FAIL --timestamp "2026-08-06 14:32" \
  --failed-item "<pontos tesztnév/azonosító>" [--failed-item "<másik>" ...] \
  --details "<rövid ok>"
# PASS (minden zöld — --failed-item nélkül):
python3 <platform-scripts-mappa>/failure-counter.py \
  specs/cycle-NN-<cycle-name>/test-report/validation-report.md \
  --result PASS --timestamp "2026-08-06 14:32"
```

**Időbélyeg (hordozhatóság):** a `--timestamp` értékét **konkrét stringként** add meg (`YYYY-MM-DD HH:MM`) — a szkript szándékosan nem olvas rendszeridőt. Ha shell-behelyettesítést használsz, az platformfüggő: bash/zsh → `$(date '+%Y-%m-%d %H:%M')`, PowerShell → `(Get-Date -Format 'yyyy-MM-dd HH:mm')`. Az elgépelt vagy hiányzó időbélyeg nem rontja el a számlálást (az item-nevek számítanak), de a napló olvashatóságát igen.

**Három leállási korlát — bármelyik teljesül → `exit 3` → a hurok MEGÁLL:**

| Korlát | Alapérték | Mit fog meg |
|---|---|---|
| per-item **egymást követő** bukás | 3 | a klasszikus 3-próba: ugyanaz az item körről körre bukik |
| per-item **összes** bukás a naplóban | 5 | a „hol bukik, hol nem" item — a megszakított láncot is |
| **egymást követő FAIL-futások** | 5 | divergáló hurok: körönként **más** item bukik (VD4b globális backstop) |

**A kilépő kód dönt, nem a saját ítéleted:**
- **`0`** → naplózva, egyik korlát sem telt be → a hurok folytatható.
- **`3`** → naplózva, valamelyik korlát betelt → **STOP**; a szkript kiírja, melyik item és melyik korlát miatt. A megállás típusát a VD5 heurisztika dönti el (tervezési hiba → eszkaláció; egyébként → STOP + humán).
- **`1`** → **hiba a hívásban, a napló NEM módosult.** Ilyenkor **tilos kézzel naplózni** — az szétverné a determinisztikus számlálást. Olvasd el a hibaüzenetet, javítsd a hívást (leggyakoribb ok: `FAIL` `--failed-item` nélkül, hiányzó `--timestamp`, vagy `PASS` melletti `--failed-item`), és futtasd újra. Ha kétszer sem sikerül, **STOP + humán**: jelezd a felhasználónak a parancsot és a hibaüzenetet.

**`FIGYELEM:` sor a kimenetben** — a szkript jelzi, ha egy item korábban is bukott, de egy közbeeső PASS megszakította a láncot. Ez majdnem mindig azt jelenti, hogy valaki (egy korábbi futás) **részeredményt naplózott** a VD4a szabály ellenére. Ne hagyd figyelmen kívül: a napló ilyenkor is helyesen áll meg az „összes bukás" korlátnál, de a `# <sec:validation_history>` félrevezető — írd a `--details`-be, hogy a lánc megszakadt.

### 5. A kör LEZÁRÁSA a `validation-report.md`-ben (VD9 — kötelező, a naplózó szkript ELŐTT)

> **🔴 Ez a lépés minden körben lefut — PASS-nál és FAIL-nál egyaránt, minden ágon.** A sorrend kötött: **előbb a `## <sec:round> N` blokk lezárása, csak utána a `failure-counter.py`.** Fordítva a szkript a History-t a befejezetlen blokk után fűzi, és a napló összekeveredik.

**A blokkot a `round-log.py close` zárja le** — a mechanikus mezőket (eredmény, lépés-sorok, bukott elemek, DoD-tábla, fejléc, `## <sec:closing_summary>`) a szkript írja, te csak a szabad szöveges részeket adod meg:

```bash
python3 <platform-scripts-mappa>/round-log.py close \
  specs/cycle-NN-<cycle-name>/test-report/validation-report.md \
  --result FAIL --timestamp "2026-08-10 10:36" \
  --step "10:35|teszt-riport kapu (TR3)|report-gate-check.py …|✓ exit 0" \
  --failed-item "auth.spec.ts > refresh token rotation" --failed-item "DoD-03" \
  --dod "DoD-01|✓|a token-csere 200-at ad" --dod "DoD-03|✗|hiányzik a correlationId" \
  --review "Futott: igen — 2 nyitott <status:must_fix> (MF-01, MF-02)" \
  --decision "FAIL → javító kör indul, könnyű körrel."
```

- A `--failed-item` értékei **ugyanazok**, mint amiket rögtön utána a `failure-counter.py`-nak adsz — így nem tud elcsúszni a két lista.
- PASS-nál (vagy STOP/eszkaláció esetén) add hozzá a `--final "PASS"` / `--final "FAIL (megállt)"` / `--final "eszkalálva"` kapcsolót: ez frissíti a fejlécet és újragenerálja az `## <sec:closing_summary>` szekciót.
- A szkript **csak a nyitott blokkot** módosítja; lezárt kört és a `# <sec:validation_history>`-t soha nem érinti.

A blokk tartalmi elvárásai (amit a `--step` / `--dod` / `--review` / `--decision` mezőkkel töltesz):

1. **Fejléc-sor**: a `— folyamatban` helyére a kör eredménye (`— PASS` / `— FAIL`); a kör típusa (`TELJES` / `KÖNNYŰ`) maradjon.
2. **`### <sec:steps>`** — a végrehajtási sorrend időbélyeggel, a `test-runner` **szó szerinti bizonyítékaival** (kiadott parancs + `X passed / Y failed / Z skipped`), és a **kihagyott** lépéseknél az indok (`kihagyva — az 1. lépés bukott`, `kihagyva — a statikus réteg bukott`, `kihagyva — könnyű kör (VD10)`, `kihagyva — plan-hiány (TR4)`).
3. **`### <sec:failed_items>`** — a `failure-counter.py`-nak átadandó **pontos** item-nevekkel (DoD-bukásnál `DoD-NN`).
4. **`### <sec:definition_of_done>`** tábla, **`### Teszt-riportok (TR3 / TR5)`**, **`### Tasks elvégzettsége`**, és ha volt fixer: **`### Javító kör`** (felvett taskok, a fixer visszajelzése, a VD3a kapu eredménye).
5. **`### <sec:round_verdict>`** — egy mondat: miért indul új kör, vagy miért állt meg / konvergált a hurok.
6. **Frissítsd a fájl fejlécét** (`<field:f_current_status>`, `<field:f_round_count>`, `<field:f_last_updated>`), a fázis lezárásakor (PASS, STOP, eszkaláció — **mindhárom ágon**) pedig az `## <sec:closing_summary>` szekciót is (végeredmény, körök teljes/könnyű bontásban, újrafuttatott elemek, eszkaláció, ideiglenes környezeti módosítás).

**Determinisztikus önellenőrzés** — a `round-log.py close` után, a `failure-counter.py` **előtt**:

```bash
python3 <platform-scripts-mappa>/validate-gate-check.py specs/cycle-NN-<cycle-name> --stage close
```

Ez ellenőrzi a kör-blokk meglétét, a `## <sec:round> N` ↔ `round-NN/` egyezést (TR5) és a nyitott tételeket. Ha `exit 1`, **ne futtasd a naplózó szkriptet**, és ne zárd le a fázist — előbb rendezd a kiírt ✗ pontokat.

---

## A `validation-report.md` — teljes validálási riport (VD9)

> **A fájl nem egy egysoros run-log, hanem a validálás teljes futásnaplója.** Utólag ebből kell kiderülnie, hogy **mi futott, milyen sorrendben, milyen eredménnyel, mi futott újra és miért** — anélkül, hogy bárkinek vissza kellene keresnie a chatet (`/clear` után az nem is létezik). Ha a fájlban csak a `# <sec:validation_history>` van, a fázis **nem** végezte el a dolgát.

**Ki mit ír a fájlba — két, élesen elválasztott régió:**

| Régió | Hol | Gazda | Tartalom |
|---|---|---|---|
| Fejléc + `## <sec:round> N` blokkok | a fájl elejétől | **te (az orchestrátor)** | a futás eseménynaplója, körönként egy blokk, **hozzáfűzve — korábbi kört SOHA nem írsz felül** |
| `# <sec:validation_history>` | a fájl **végén** | **kizárólag a `failure-counter.py`** | gépi run-log a leállási számlálókhoz |

**🔴 Írási szabály — APPEND-ONLY, a fájlt SOHA nem írod ki egyben újra.** A szkript mindig a **fájl végére** fűz, ezért a `# <sec:validation_history>` fejlécnek a fájl végén kell maradnia; az új `## <sec:round> N` blokkot **közvetlenül a `# <sec:validation_history>` fejléc ELÉ** szúrod be. Gyakorlatban: **célzott szerkesztéssel** (egyetlen horgony-szövegre illesztve) szúrsz be vagy egészítesz ki — a teljes fájl újraírása tilos, mert egy hosszú naplónál a modell menet közben „összefoglalja" vagy elhagyja a korábbi köröket, és a történet visszaállíthatatlanul elvész. Amit felülírhatsz: **kizárólag** a fejléc 3 sora (`<field:f_current_status>` / `<field:f_round_count>` / `<field:f_last_updated>`), az `## <sec:closing_summary>` szekció, és a **még nyitott** (`folyamatban`) `## <sec:round> N` blokk. **Lezárt kör blokkjához és a History soraihoz soha nem nyúlsz** — nem szerkeszted, nem rendezed át, nem törlöd.

**Mikor írsz:** háromszor, minden körben — ez a „Validálási lépések" **0/b** és **4.** lépése, nem külön ceremónia:
1. **a kör elején (0/b)**: a fájl létrehozása, ha még nincs + az új `## <sec:round> N` blokk megnyitása a `# <sec:validation_history>` elé;
2. **menet közben**: minden lépés (test-runner hívás, kapu, fixer indítása/visszatérése) sora azonnal a lépés-táblába — hogy egy megszakadt futás után is megmaradjon a nyom;
3. **a kör végén (4.)**: a blokk lezárása + a fejléc (és a fázis lezárásakor az `## <sec:closing_summary>`) frissítése — **a naplózó szkript futtatása előtt**, PASS-nál és FAIL-nál egyaránt.

### A fájl sablonja

```md
<!-- INCLUDE:lang/07-validate.md#validation-report-sablon -->
```

### Kötelező tartalmi elemek (ezek nélkül a riport hiányos)

1. **Végrehajtási sorrend, időbélyeggel** — a lépés-tábla mutassa, mi futott, milyen sorrendben, és **mi maradt ki, miért** (pl. a nehéz tesztek kihagyása bukott gyors tesztek után). A „<status:skipped>" sor ugyanolyan fontos, mint a lefutott lépés.
2. **A `test-runner` bizonyítékai szó szerint** — a kiadott parancs és a `X passed / Y failed / Z skipped` darabszámok (TR1). Ez teszi utólag ellenőrizhetővé, hogy a PASS mögött tényleges futtatás állt.
2.a **A teszt-eszköz saját riportja a kör mappájában (TR3/TR5)** — a `## <sec:round> N` fejlécében a `**Riport-mappa:**` sor, a lépés-táblában a kapu kimenete (mely artefaktumok kerültek be, mekkorák). A riport a napló mellett, a kör saját mappájában él; a szöveges napló nem helyettesíti, a riport nem helyettesíti a naplót. **A mappanév száma és a `## <sec:round> N` sorszáma kötelezően egyezik** — ez teszi a bukott lépést és a hozzá tartozó bizonyítékot összepárosíthatóvá.
3. **Az újrafuttatások láthatósága** — minden kör külön blokk, és az `## <sec:closing_summary>` sorolja fel, mely elemek futottak többször (ez a „mi futott újra" kérdés válasza).
4. **A javító kör nyoma** — mely taskokat vette fel, mit adott vissza a fixer, mi volt a szerződés-integritás kapu (VD3a) eredménye. Ha a kapu gyengítést talált, **az érintett fájl és a visszaállítás ténye is** kerüljön be.
5. **A kör döntése egy mondatban** — miért indult új kör, vagy miért állt meg a hurok.
6. **A kör típusa (VD10)** — a `## <sec:round> N` fejlécben `TELJES` vagy `KÖNNYŰ`, és a lépés-táblában a kihagyott lépéseknél az indok: „<status:skipped> — könnyű kör (VD10)". Az `## <sec:closing_summary>` **Körök** sora bontsa: hány teljes, hány könnyű. Enélkül utólag nem ellenőrizhető, hogy a PASS teljes körből származik-e.

> **A review körei is ide kerülnek** (RV1): a `validation-report.md` a ciklus **teljes** minőségi története — tesztek és review egyaránt. A `code-review.md` csak a findingok listája, nem napló: a hurok menetét, a próbaszámokat és a leállási korlátokat kizárólag a `validation-report.md` `# <sec:validation_history>`-ja tartja nyilván.

---

## Az önjavító hurok (orchestrátor-hurok)

FAIL esetén **nem** adod vissza egyszerűen a vezérlést a felhasználónak. Levezényelsz egy iteratív javító hurkot — `implement-fixer` subagent → újra-validálás — amíg PASS nem lesz, vagy amíg a **3-próba szabály (VD4)** / a **felfelé menekülő ág (VD5)** meg nem állítja.

A meglévő FAIL-gépezet megmarad (a `validation-report.md` `# <sec:validation_history>`, a `tasks.md` `## <sec:validation_fixes>`, a státusz-visszafordítás) — csak a korábbi „kézi visszaadás a felhasználónak (futtasd újra a 06-ot)" lesz orchesztrált hurok. A javítást nem te végzed: azt az `implement-fixer` subagent (= a 06 Fix-módja) csinálja; te validálsz, naplózol, döntesz és státuszt fordítasz.

### ⚠ Anti-„teszt-csalás" garde (VD3 — a hurok legfontosabb szabálya)

**A hurok a KÓDOT igazítja a teszthez / Sonarhoz / DoD-hoz / review-findinghoz — SOHA nem fordítva.** A teszt, a <sec:definition_of_done> és a reviewer findingja a **szerződés**; a hurok ezt a zöld eredmény érdekében **nem módosíthatja**.

**STOP — tilos** bármelyik:
- teszt assertion gyengítése/lazítása, vagy az elvárt érték a kódból visszamásolása;
- teszt `skip`/`xfail`/kikommentezése/törlése a zöldért;
- hardcode-olt „elvárt" érték, amely a tesztet zöldíti, de a valós viselkedést nem valósítja meg;
- a `spec.md` DoD-pont leszállítása/átfogalmazása, hogy könnyebben teljesüljön;
- a `<status:must_fix>` finding **kozmetikai elnémítása** a gyökérok javítása nélkül (lint-suppress komment, a kifogásolt kód álcázása);
- a `code-review.md` `<status:must_fix>` bejegyzésének törlése/átfogalmazása javítás nélkül.

Ezt a szabályt az `implement-fixer` is megkapja (a 06 Fix-mód garde-ja) — egy olcsóbb LLM se sodródjon teszt-csalásba. **Ha egy hiba csak a teszt/DoD megváltoztatásával lenne zöld** → az nem kód-fix, hanem **tervezési hiba** → VD5 (felfelé menekülő ág), nem a teszt lazítása.

#### 🔴 Szerződés-integritás kapu a fixer után (VD3a — determinisztikus, kötelező)

A fenti tiltás önmagában **csak instrukció** — a fixer olcsóbb modellen fut, és a hurok teljes értéke azon áll, hogy a zöld eredmény valódi. Ezért a fixer minden visszatérése után, **még az újra-validálás előtt**, nézd meg **ténylegesen**, mit írt át:

```bash
python3 <platform-scripts-mappa>/contract-guard.py specs/cycle-NN-<cycle-name>
```

A szkript megnézi, hogy változott-e védett útvonal (tesztfájlok a `conventions.md` „<sec:cv_test_structure>" szerint, `spec.md`, `test-report/code-review.md`, Sonar-/lint-konfig), és a **hozzáadott sorokban** keresi a klasszikus csalás-mintákat (`.skip(`, `xit(`, `@pytest.mark.skip`, `@Disabled`, `NOSONAR`, `eslint-disable`, `@ts-ignore`), a **törölt sorokban** pedig az eltűnt assertionöket, elnémított `MF-NN` findingokat és megváltoztatott `DoD-NN` sorokat.

A kimenet utolsó sora dönti el, kell-e egyáltalán diffet olvasnod:

- **`VERDICT: CLEAN`** (`exit 0`) → egyetlen védett útvonal sem változott → **ne olvasd el a diffet**, mehet az újra-validálás.
- **`VERDICT: SUSPECT`** (`exit 1`) → csalás-mintát talált → ez **szerződés-gyengítés**, lásd lent: visszaállítás + eszkaláció. A gyanús sorokat a szkript kiírja, nem kell keresned.
- **`VERDICT: REVIEW`** (`exit 1`) → védett útvonal változott, de mintát nem talált → **csak ekkor** olvasd el az érintett fájlok diffjét, és döntsd el, melyik eset:
  - **Legitim** (új teszt hozzáadása a hibához, `DoD-NN`/`MF-NN` azonosító pótlása, a `code-review.md`-ben egy finding **lezártra jelölése ténylegesen elvégzett javítás után**, elgépelés javítása a teszt *nevében*) → ✓, de **írd be a kör „Javító kör → Szerződés-integritás kapu" sorába**, mit és miért.
  - **Szerződés-gyengítés** (assertion lazítása, `skip`/`xfail`, teszt törlése, elvárt érték kódból visszamásolva, DoD-pont átfogalmazása/leszállítása, Sonar-szabály kikapcsolása, `<status:must_fix>` finding törlése/átfogalmazása vagy suppress-kommenttel elnémítása) → **STOP, ez teszt-csalás.** Teendő: (1) állítsd vissza az érintett fájlokat (`git checkout -- <fájl>`); (2) az adott itemet naplózd FAIL-ként a szokásos módon; (3) kezeld **eszkalációs jelzésként** (VD5) — a hurok nem próbálkozik tovább ezzel az itemmel, mert a fixer a szerződést támadta, nem a kódot.
- A `git checkout --` visszaállítás után **ne** indíts azonnal új fixert ugyanarra az itemre — az a kör FAIL-je, és a VD5 ág dönt.

Ez a kapu az egyetlen hely, ahol a VD3 nem csak szándék, hanem **ellenőrzött tény** — ne hagyd ki, még akkor sem, ha a fixer összefoglalója azt állítja, hogy nem nyúlt a tesztekhez.

### A hurok egy iterációja

1. **A kör FAIL-jének naplózása (VD4a) — a `failure-counter.py` szkripttel, körönként EGYSZER.** Futtasd a `--result FAIL` + a kör **összes** bukott item-nevével (lásd „Naplózás és leállási korlátok"). Ez naplózza a futást ÉS kiszámolja a számlálókat — **ne kézzel**. Előtte zárd le a kör `## <sec:round> N` blokkját a `validation-report.md`-ben (VD9).
2. **Leállás-döntés a szkript kilépő kódjából (VD4).** `exit 3` → valamelyik korlát betelt (per-item 3 egymást követő / 5 összes bukás / 5 egymást követő FAIL-futás) → a hurok megáll (lásd „Leállási korlátok mint hurok-korlát"); a megállás típusát a VD5 heurisztika dönti el (tervezési hiba → eszkaláció; egyébként → STOP + humán). `exit 1` → hibás hívás, javítsd és futtasd újra (kézzel naplózni TILOS). `exit 0` → folytatható a hurok.
3. **Korai eszkaláció-ellenőrzés (VD5).** Ha az előző iteráció fixer subagentje (`implement-fixer` vagy `review-fixer`) **eszkalációs jelzést** adott vissza, vagy a **szerződés-integritás kapu (VD3a)** gyengítést talált, ne körözz tovább a 06-ban → **azonnal eszkalálj** (lásd „Felfelé menekülő ág"), nem kell megvárni a 3. próbát.
4. **Javító-taskok felvétele.** A FAIL-gépezet szerint (lásd „FAIL — javító-taskok felvétele"), a bukás **típusa szerinti szekcióba** a `tasks.md` végén, prerequisite hivatkozásokkal, `[GREEN]`/`[CHECK]` taskként:
   - teszt / Sonar / DoD bukás → `## <sec:validation_fixes>`;
   - review `<status:must_fix>` (`MF-NN`) → `## <sec:review_fixes>` *(itt `[RED]` pár nem kell — direkt javítás)*.
   Duplikátum-kerülés: ne vedd fel kétszer ugyanazt. **Üres hibalistával nem indul iteráció** — ha nincs konkrét javítandó tétel (pl. QG1 küszöb-bukás), a hurok nem folytatható, lásd a QG1 ágat.
5. **Marker felvétele (VD6).** A `tasks.md` státuszát fordítsd `<status:ready_for_implement> [validate-loop]`-ra. A marker jelzi: fix-mód aktív → a fixer automatikusan lépteti a státuszt, megerősítés nélkül. *(Egyetlen marker van — review-javításnál is ez, nem külön `[review-loop]`.)*
6. **A fixer subagent indítása (VD2) — a bukás típusa szerint.** Ha a körben **csak** review-finding bukott → `review-fixer` a `## <sec:review_fixes>` taskokkal; egyébként `implement-fixer` a `## <sec:validation_fixes>` taskokkal. Ha **mindkettő** van (a megerősítő körben teszt is bukott, meg finding is maradt), előbb az `implement-fixer` fut (a zöld teszt az alap), utána ugyanabban az iterációban a `review-fixer`. Mindkettőt a konkrét hibalistával + a prerequisite riportokkal indítod (lásd „A fixer-subagent indítása"). Ha bármelyik fixer **eszkalációs jelzést** ad vissza → ugorj a 3. pontra.
7. **Szerződés-integritás kapu (VD3a).** A fixer visszatérése után futtasd a fenti `git diff` ellenőrzést, **mielőtt** újra validálnál. Gyengítés esetén: visszaállítás + eszkaláció (3. pont).
   - **Ha a fixer `FUTTATÁS BLOKKOLVA (EX1)` jelzéssel tért vissza** (nem tudta lefuttatni a `[CHECK]` ellenőrzését, mert a subagentje nem kaphat parancs-jóváhagyást): ez **nem** hiba és **nem** eszkalációs jelzés — a javítás elkészült, csak az ellenőrzés maradt el. A következő kör `run-tests.py` futása úgyis lefuttatja a teljes gyors készletet; **ne pipáld ki** a `[CHECK]` taskot, amíg az a kör zöld nem lett.
8. **Újra-validálás — KÖNNYŰ körrel (VD10).** A javítás után **nem** a teljes menet indul: a teljes gyors teszt-készlet fut, plusz az az egy item, ha a bukás nehéz teszt, Sonar vagy review-finding volt (utóbbinál a `reviewer` inkrementálisan, csak a nyitott `MF-NN`-ekre). Ez egy **új kör** — a végén megint pontosan egy naplóbejegyzés készül.
   - **FAIL** → új iteráció az 1. ponttól (megint könnyű kör).
   - **Zöld** → **még NEM PASS.** Azonnal, javítás nélkül indíts egy **TELJES megerősítő kört** (gyors tesztek → **Sonar + kódreview** → nehéz tesztek + regresszió → DoD/tasks/riport-kapu). Ez is külön kör, külön naplóbejegyzéssel. A review itt **inkrementálisan** fut: az előző `code-review.md`-t átadva, a még nyitott `<status:must_fix>`-ekre fókuszálva.
     - a megerősítő kör **PASS** → a hurok konvergált, ugrás a „Státusz kezelés → PASS"-ra (itt kerül le a marker, és történik az egyetlen lezáró commit);
     - a megerősítő kör **FAIL** (a javítás máshol tört el valamit, vagy a nehéz teszt bukik) → új iteráció az 1. ponttól.

### A fixer-subagent indítása (VD2)

Két fixer van, **azonos szabályokkal** — mindkettő vékony wrapper a `06-implement.md` „Fix-mód" szekciójára, így nincs duplikált javító logika, és a 06 minőségi szabályai automatikusan érvényesülnek:

| Fixer | Mikor | Bemenet |
|---|---|---|
| `agents/implement-fixer.md` | teszt / Sonar / DoD bukás | a `tasks.md` `## <sec:validation_fixes>` elvégzetlen taskjai + `test-report/validation-report.md`, és ha Sonar bukott, **az aktuális kör** `test-report/validate/round-NN/sonar-report.md`-je (a kör-számot konkrétan add meg — TR5) |
| `agents/review-fixer.md` | review `<status:must_fix>` (`MF-NN`) | a `tasks.md` `## <sec:review_fixes>` elvégzetlen taskjai + `test-report/code-review.md` (a findingok szövegével) |

- **Kimenet (mindkettőnél):** (a) az elvégzett javítások összefoglalója (mely taskot mivel zárt le), és (b) **eszkalációs jelzés**, ha valamelyik hibát csak a teszt/DoD/spec módosításával vagy a finding elnémításával lehetne „zöldre" vinni (VD3). A subagent **nem** módosíthatja a tesztet/DoD-ot/findingot, és **nem** írja a `validation-report.md`-t vagy a `code-review.md`-t — azt te (az orchestrátor).

### Felfelé menekülő ág (VD5 — escape hatch)

Nem minden FAIL kód-bug: néha **tervezési hiba** (a teszt/DoD a kóddal ellentmondó, vagy a terv hibás alapra épül). Ilyenkor a hurok ne 06-ban körözzön — a 06 sosem fogja zöldre vinni, mert csak a tesztet/DoD-ot lazítva lehetne, azt pedig VD3 tiltja.

**Detektálási heurisztika** — tervezési hiba jele, ha:
- **(a)** az `implement-fixer` eszkalációs jelzést adott vissza (a hibát csak a teszt/DoD megváltoztatásával lehetne zöldre vinni), **vagy**
- **(b)** a leállási korlát elérésekor a megrekedt itemet az addigi javítási kísérletek alapján csak a teszt/DoD megváltoztatásával lehetne zöldre vinni, **vagy**
- **(c)** a **szerződés-integritás kapu (VD3a)** azt találta, hogy a fixer a tesztet/DoD-ot/Sonar-konfigot módosította a zöldért — ilyenkor a visszaállítás után nincs értelme újra ugyanazt kérni tőle.
- **(d)** a `test-runner` **plan-hiányt** jelentett (TR4): egy tesztcsoport azért nem futott, mert a futtatási részlet nincs a `plan.md`-ben. Ez a 03 fázis hiánya — a fixer nem tudja megjavítani, mert nem a kód a hibás.

**Teendő (STOP + eszkaláció), sorban:**
1. Naplózd a `# <sec:validation_history>`-ba a megrekedt itemet, és hogy **tervezési hiba** miatt eszkalálsz (nem kód-bug) — a `--details` mezőben.
2. **Státusz-visszafordítás 03/02-re:** fordítsd vissza az érintett tervezési dokumentum státuszát a megfelelő nem-kész értékre — `plan.md` → `<status:draft>` (ha a terv hibás), vagy `spec.md` → `<status:draft>` (ha maga a DoD a hibás/ellentmondásos). A `tasks.md` a `[validate-loop]` markerrel marad (a megrekedt állapot jelzése).
3. **Egyetlen lezáró commit** (VD8) — a *Fázis-záró commit* szekció eljárása szerint, **kötelező** (az eszkalációs ág sem kivétel).
4. **Jelezd a felhasználónak az átadást** — ez tervezési kérdés, nem automatikus javítás (a list2 analyze-szellemű tervezési hurokra tartozik), lásd a jelzés szövegét lent. A folyamat a tervezés rendezése után a `05→06→07` úton tér vissza ide.

### Leállási korlátok mint hurok-korlát (VD4)

A hurok korlátját **a `failure-counter.py` kilépő kódja** adja — **nem a saját becslésed, és nem kézzel olvasott számláló**. Három korlát fut párhuzamosan (részletek: „Naplózás és leállási korlátok"):

1. **per-item 3 egymást követő bukás** — a klasszikus 3-próba: pont a beragadt elemet fogja meg;
2. **per-item 5 összes bukás** — a „hol bukik, hol nem" item, amely a láncot megszakítva kerülné el az (1)-et;
3. **5 egymást követő FAIL-futás (VD4b)** — globális backstop arra, amikor **körönként más item bukik**: a hurok nem konvergál, csak új hibákat termel. Ez a korlát a per-item számlálóktól függetlenül megállítja a divergáló hurkot.

Bármelyik teljesül → `exit 3` → **a hurok megáll**, a szkript kiírja, melyik item és melyik korlát miatt.

- Ha a megállás **tervezési hiba** jele (VD5 heurisztika) → **eszkaláció** (felfelé menekülő ág).
- Egyébként → **STOP + humán** (megrekedt kód-bug): *„A(z) [Failed Item] [N]. alkalommal is elbukott ([melyik korlát]). Humán beavatkozás szükséges — hogyan tovább?"* A (3) korlátnál: *„A javító hurok [N] köre óta nem konvergál — körönként más elem bukik el. Humán beavatkozás szükséges — hogyan tovább?"*, a legutóbbi körök bukott elemeinek felsorolásával. Ne folytasd a javítást a felhasználó válasza nélkül. Commit a végén (VD8); a `## <sec:validation_fixes>` és a `[validate-loop]` marker megmarad (megrekedt állapot).

### Commit-stratégia a hurokban (VD8)

- **A hurokban nincs iterációnkénti commit** — a korábbi FAIL-enkénti commit megszűnik.
- **Egyetlen lezáró commit** a hurok végén (PASS / 3-próba STOP / eszkaláció):
  ```bash
  git add specs/cycle-NN-<cycle-name>/
  git commit -m "cycle-NN: 07-validate"
  ```
- **Megszakítás-biztos:** a köztes commit hiányát a `# <sec:validation_history>` + a `[validate-loop]` státusz-marker pótolja — ezekből a folytatás rekonstruálható (lásd „Megszakított futás kezelése").

**A lezáró commit KÖTELEZŐ, kivétel nélkül minden lezáró ágon** (PASS, leállási korlát STOP, felfelé eszkaláció, QG1 küszöb-bukás) — az eljárást lásd a *Fázis-záró commit* szekcióban. Commit nélkül nem adhatod vissza a vezérlést a felhasználónak.

<!-- INCLUDE:shared/phase-commit.md -->

A fenti blokkban a `<FÁZIS-TAG>` értéke ebben a fázisban: **`07-validate`**. A 2. lépés (státuszírás) itt az adott lezáró ág szabálya szerinti státusz/marker-rendezést jelenti (PASS-nál `spec.md`/`plan.md`/`tasks.md` → `<status:done>` + marker le; STOP/eszkalációnál a visszafordított státusz + a marker fennmaradása). A commit előtt **nem** kérsz megerősítést.

> **Megállási szabály (PC1):** ha a hurok lezárult (bármely ágon), de a fázis-záró commit hiányzik (VCS-es projekt, `git log -1 --oneline` nem a `cycle-NN: 07-validate` commitot mutatja), **STOP** — először commitolj, csak utána zárd le a fázist és add meg a következő lépést / a megállási üzenetet.
>
> **Megállási szabály (VD9-guard) — a commit ELŐTT, kötelező:** a `validation-report.md` nem állhat csak a `# <sec:validation_history>`-ból. Ellenőrizd determinisztikusan:
> ```bash
> python3 <platform-scripts-mappa>/validate-gate-check.py \
>   specs/cycle-NN-<cycle-name> --stage close --require-review
> ```
> Ha a szkript `exit 1`-et ad (nincs `## <sec:round> N` blokk, kevesebb kör-blokk van, mint `# <sec:validation_history>` futás, hiányzik egy `round-NN/` mappa, vagy maradt nyitott tétel), **STOP** — a fázis kötelező outputja hiányzik vagy hiányos. Pótold a hiányzó blokko(ka)t a rendelkezésre álló bizonyítékokból (a kör-mappák artefaktumai + a History sorai), és csak utána commitolj. Ez PASS, STOP és eszkalációs ágon egyaránt érvényes. *(STOP/eszkalációs ágon a `--require-review` elhagyható, ha a review el sem indult.)*

### „Hol járunk" a megállási üzenetekben (LC2)

A user-felé tett megállási üzeneteknél (leállási korlát STOP, eszkaláció, QG1 küszöb-bukás — ez a hurok **egyetlen** user-érintkezése, lásd VD7) jelezd, hol tart a hurok: a megrekedt elemet és a betelt korlátot, a `# <sec:validation_history>`-ra hivatkozva:

```
<!-- INCLUDE:lang/07-validate.md#LC2-megallas-prefix -->
```

A válaszod végén kötelezően helyezz el egy közvetlen, kattintható linket a `validation-report.md`-re.

---

## Státusz kezelés

> **A PASS automatikus, mert determinisztikus ellenőrzéseken alapul (tesztek + Sonar + DoD). Felhasználói megerősítés NEM szükséges — ne kérj megerősítést a `<status:done>` státuszra váltás előtt. Az eredmény utólag is ellenőrizhető a `validation-report.md`-ben (VD9: körönkénti lépés-napló + `# <sec:validation_history>`).**

### PASS

Minden teszt átment (bizonyítékkal — TR1/TR2), a DoD minden pontja teljesül, minden task `[x]`, a Sonar Quality Gate PASS (vagy N/A), **a teszt-riport kapu (TR3) `exit 0`**, **a kódreview lefutott és nincs lezáratlan `<status:must_fix>` (RV1)**, és a szerződés-integritás kapu (VD3a) tiszta.

> **🔴 A PASS forrása kizárólag TELJES kör lehet (VD10/1).** Ha az utolsó kör **könnyű** volt (csak gyors tesztek futottak), a fenti feltételek egy része nem is mérhető — ilyenkor **nincs PASS**: indíts egy teljes megerősítő kört, és annak az eredményéből dönts. Ellenőrzés: a lezárandó `## <sec:round> N` blokk fejlécében `— TELJES` áll, és a lépés-táblában szerepel a nehéz teszt, a Sonar (vagy `N/A` a plan szerint) **és a lefutott kódreview**.

Teendők:
1. **Zárd le a kör `## <sec:round> N` blokkját** a `validation-report.md`-ben az **5. lépés** szerint (ha a blokk nem létezik — mert a 0/b kimaradt —, **most pótold**, a kör bizonyítékaiból), és frissítsd a fejlécet + az `## <sec:closing_summary>` szekciót (VD9), majd naplózz: `failure-counter.py ... --result PASS --timestamp "..."` (`--failed-item` nélkül). Ez zárja le a kört a naplóban.
2. **Vedd le a `[validate-loop]` markert** (ha a hurok futott): a `tasks.md` státusza `<status:done>`-re vált — marker nélkül. Frissítsd a `plan.md` és `spec.md` státuszát is `<status:done>`-re. A `## <sec:validation_fixes>` / `## <sec:review_fixes>` szekciók lezárt taskjai a helyükön maradnak (nyoma marad, mi javult a hurokban).
3. **Egyetlen lezáró commit** (a hurok alatt nem volt köztes commit — VD8), a *Fázis-záró commit* szekció eljárása szerint — **kötelező**:
   ```bash
   git add specs/cycle-NN-<cycle-name>/
   git commit -m "cycle-NN: 07-validate"
   ```
<!-- INCLUDE:lang/07-validate.md#zaro-uzenet -->
   > **A válasz végén helyezd el a `validation-report.md` közvetlen, kattintható linkjét.**

### FAIL — javító-taskok felvétele (a hurok 4–6. lépése)

Ha bármely teszt, a Sonar, vagy a DoD ellenőrzés hibázik, **nem** adod vissza a vezérlést a felhasználónak — a hurok következő iterációját készíted elő és indítod (lásd „Az önjavító hurok"). Lépések **sorban**:

```
[ ] 0. validation-report.md létezik, és a ## <sec:round> N blokk a kör ELEJÉN megnyílt
        (0/b lépés) — ha nincs, a fájl csak a # <sec:validation_history>-t tartalmazza
        és a riport üres → pótold, mielőtt továbbmész
[ ] 1. ## <sec:round> N blokk lezárva a validation-report.md-ben (VD9, 5. lépés): lépés-tábla a
        végrehajtási sorrenddel + a test-runner bizonyítékaival (parancs +
        X passed/Y failed/Z skipped), bukott elemek, DoD-tábla, a kör döntése
[ ] 2. failure-counter.py lefuttatva EGYSZER, a kör VÉGÉN (--result FAIL +
        a kör ÖSSZES bukott iteme; DoD-bukásnál DoD-NN azonosítóval) →
        # <sec:validation_history> frissítve, a számlálók determinisztikusan léptetve
        ⚠ részeredményt (pl. „gyors tesztek zöldek") NEM naplózol külön (VD4a)
[ ] 3. Leállás a szkript kilépő kódjából: exit 3 → STOP (eszkaláció vagy humán,
        lásd lent) — NE indíts újabb fixert; exit 1 → hibás hívás, javítsd és futtasd
        újra (kézzel naplózni TILOS); exit 0 → tovább
[ ] 4. tasks.md → ## <sec:validation_fixes> fejezet létrehozva vagy folytatva
[ ] 5. A fejezet elejére prerequisite hivatkozásként berakva:
        - specs/cycle-NN-<cycle-name>/test-report/validation-report.md
        - (ha Sonar hibázott) az AKTUÁLIS kör Sonar-riportja, teljes útvonallal:
          specs/cycle-NN-<cycle-name>/test-report/validate/round-NN/sonar-report.md
          ⚠ a kör-számot írd ki konkrétan (TR5) — a fixernek az őt kiváltó kör
            eredményét kell látnia, nem egy másikét
[ ] 6. Konkrét javítandó tesztek / Sonar hibák / DoD-NN pontok felvéve [GREEN]
        taskokként, a csoport végén egy [CHECK] ellenőrző taskkal (duplikátum-kerülés!)
        ⚠ ha a lista ÜRES lenne (QG1 küszöb-bukás) → nem indul iteráció, lásd QG1
[ ] 7. tasks.md státusz → <status:ready_for_implement> [validate-loop]   (marker, VD6)
[ ] 8. implement-fixer subagent indítva a konkrét hibalistával (VD2)
[ ] 9. A fixer visszatérése után: szerződés-integritás kapu (VD3a) — git diff a
        tesztfájlokra / spec.md-re / Sonar-konfigra. Gyengítés → git checkout --
        visszaállítás + eszkaláció (VD5). Eszkalációs jelzés a fixertől → VD5.
        Egyébként → újra-validálás (a hurok 8. lépése, új kör)
```

**A FAIL ág itt NEM commitol és NEM ad vissza vezérlést a felhasználónak** — a commit a hurok végén egyetlen alkalommal történik (VD8), a felhasználói érintkezés pedig csak a leállási korlát STOP / eszkaláció / QG1 esetén (VD7).

#### Eszkaláció jelzése a felhasználónak (VD5 — felfelé menekülő ág)

A „Hol járunk" fejléccel (LC2):
<!-- INCLUDE:lang/07-validate.md#VD5-eszkalacio-uzenet -->

#### Validációs leállás (VD4 — a szkript `exit 3`-ára)

Ha a `failure-counter.py` `exit 3`-mal tér vissza (bármelyik a három korlát közül: per-item 3 egymást követő, per-item 5 összes, vagy 5 egymást követő FAIL-futás) — **állj meg**. Ne felülbíráld a szkript döntését, és ne indíts „még egy utolsó" fixert. Döntsd el a megállás típusát a VD5 heurisztika szerint:
- **tervezési hiba** (csak a teszt/DoD módosításával lenne zöld, vagy a VD3a kapu gyengítést talált) → **eszkaláció** (fenti üzenet);
- **megrekedt kód-bug** → a „Hol járunk" fejléccel: *„A(z) [Failed Item] [N]. alkalommal is elbukott ([betelt korlát]). Humán beavatkozás szükséges — hogyan tovább?"*
- **divergáló hurok** (a globális backstop telt be) → *„A javító hurok [N] köre óta nem konvergál — körönként más elem bukik el: [itemek]. Humán beavatkozás szükséges — hogyan tovább?"*

Egyik esetben se folytasd a javítást a felhasználó válasza nélkül. Mindegyiknél: **egyetlen lezáró commit** (VD8), a `[validate-loop]` marker és a `## <sec:validation_fixes>` a megrekedt állapot jelzésére a `tasks.md`-n marad.