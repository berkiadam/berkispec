---
phase: 07
name: bs-validate
description: "berkispec - 07. Használd az implementáció után (Phase 07), ha a tasks.md 'Validálásra kész'. Teszt-, lint- és build-ellenőrzés, hiba esetén önjavító kör (implement-fixer subagent). Létrehozza a 'validate-decision.md'-t; PASS esetén a spec.md/plan.md/tasks.md státuszát 'Kész'-re állítja."
prerequisites:
  - "specs/cycle-NN-<name>/tasks.md státusz: Validálásra kész"
output:
  - "specs/cycle-NN-<name>/test-report/validate-decision.md"
  - "PASS esetén: spec.md / plan.md / tasks.md státusz: Kész"
prev: bs-implement
next: bs-doc-sync
subagents:
  - "agents/test-runner.md"
  - "agents/implement-fixer.md"
---
# 07 — Validálás
## Kontextus ellenőrzés

Ha azt detektálod, hogy ennek a fázisnak a futtatása most indul (ez az első prompt a fázisban), de a kontextus nem „friss” (azaz a beszélgetési előzmények tartalmaznak korábbi fázisokból vagy futásokból származó üzeneteket), akkor kérdezz rá a felhasználónál:
> *„Úgy tűnik, hogy a fázis indításakor a kontextus nem teljesen friss. Szándékosan nem futtattál `/clear`-t az új fázis megkezdése előtt (a tokenekkel való spórolás érdekében)?”*
Várd meg a felhasználó válaszát, mielőtt folytatnád a fázis futtatását.

---

Spec driven development-ben fejlesztünk szoftvert. A fejlesztés ciklusokra van bontva. Minden ciklus egy önállóan lefejleszthető, önállóan tesztelhető részegysége a teljes implementációnak.

Ez a folyamat **7. fázisa (0–9)**: 0-init · 1-ciklusok · 2-spec · 3-plan · 4-tasks · 5-analyze · 6-implement · **7-validate ←** · 8-doc-sync · 9-review.

---

## Bemenet

A prompt bemenete a ciklus mappája (pl. `specs/cycle-NN-<cycle-name>`). A validációhoz szükséges fájlokat (`spec.md`, `plan.md`, `tasks.md`) ebben a mappában találod.

## Előfeltétel

0. **Ciklus-beazonosítás:** ha a felhasználó megadott ciklust/fájlt, azt használd; különben a legfrissebb `specs/cycle-*` mappát ajánld fel megerősítésre — *"A(z) `specs/cycle-NN-<name>` ciklussal szeretnél dolgozni? Igen / Nem (megadom a ciklust)"* — és várj a válaszra, mielőtt továbblépsz.

1. **`conventions.md` létezés-ellenőrzés:** olvasd be a projekt gyökerében a `conventions.md`-t. Ha nem létezik, STOP — térjenek vissza a `00` fázishoz.

2. **Munkafa-ellenőrzés (csak VCS esetén):** futtasd `git status --short`. Ha van commitálatlan változtatás, listázd, és kérdezd meg egy körben, hogy commitáljam-e most vagy folytassam — várj a válaszra. (No-VCS projektben kimarad.)

3. Olvasd be a megadott mappából a `tasks.md`, `plan.md` és `spec.md` fájlok státuszát.

- **Ha a `tasks.md` státusza nem `Validálásra kész`:** az implementáció még nem zárult le. Jelezd, és térj vissza a `06` fázishoz.
- **Ellenőrzőpont:** a `plan.md` és `spec.md` státusza elfogadható értékek:
  - `plan.md`: `Task írásra kész` vagy `Kész`
  - `spec.md`: `Tervezésre kész` vagy `Kész`
  - `Kész` mindkettőnél normális, ha a 09-es review (vagy a 09 merge előtti doc-sync újrafuttatása) után tértünk vissza ide.
  - Ha valamelyik `Piszkozat`-ra van visszaállítva, jelezd a felhasználónak — valamelyik korábbi fázisban döntés született, amely szinkront igényel.

---

## Ismételt hibák korai ellenőrzése

**Mielőtt bármit futtatnál:** ha létezik `specs/cycle-NN-<cycle-name>/test-report/validate-decision.md`, olvasd be a `# Validation History` szekcióját. Ha bármelyik tesztnél vagy elemnél a `Consecutive Failures for this item` értéke már eléri a **2**-t, ez **figyelmeztető jelzés, nem megállási pont**: írd a válaszodba egy sorban, hogy *„Figyelem: a(z) [Failed Item] már kétszer egymás után elbukott — ha most is hibázik, a 3-próba szabály életbe lép és humán beavatkozást kérek."*, majd **folytasd** a validálást (ez NEM kérdés, NE várj választ). A tényleges megállás csak akkor következik be, ha a `Consecutive Failures` eléri a **3**-at (lásd a 3-próba szabályt a FAIL ágon).

---

## Feladatod

Ellenőrizd, hogy a ciklus implementációja teljes és helyes. A validálás három forrás alapján történik:

1. **`spec.md` — Definition of done**: minden pont teljesül-e?
2. **`plan.md` — Tesztelési stratégia**: minden előírt teszt lefut-e és átmegy-e?
3. **`tasks.md`**: minden task `[x]` státuszban van-e?

**Szereped PASS-ig determinisztikus ellenőrző, FAIL esetén orchestrátor.** Ha a validálás FAIL-t talál, **nem** adod vissza egyszerűen a vezérlést a felhasználónak („futtasd újra a 06-ot"), hanem **levezényelsz egy önjavító hurkot** (`implement-fixer` subagent → újra-validálás), amíg PASS nem lesz — a meglévő **3-próba szabály** korlátjával és tervezési hiba esetén **felfelé eszkalálva**. A javítást nem te végzed: azt az `agents/implement-fixer.md` subagent (= a 06 Fix-módja) csinálja. Lásd „Az önjavító hurok (orchestrátor-hurok)".

---

## Megszakított futás kezelése

A validáció bármikor megszakadhat. Újraindítás (ismételt futtatás) esetén:
1. **Idempotens futás**: Kezdd elölről a validálási lépéseket. Ha a korábbi futás naplózott már valamit a `test-report/validate-decision.md`-be, az az előző (félbeszakadt) futásnak tekintendő.
2. **Beragadt erőforrások**: Ha a korábbi megszakított futásból beragadt teszt konténerek vagy folyamatok miatt portütközést tapasztalsz, lődd ki azokat, vagy keress új szabad portot a korábban leírt módon.
3. **Duplikált taskok elkerülése**: Ha a futás FAIL-lel zárul, és javító feladatokat kell felvenned a `tasks.md` `## Validációs javítások` szekciójába, mindig ellenőrizd, hogy a konkrét teszthiba vagy Sonar javítás nem szerepel-e már elvégzetlen taskként (egy korábbi félbeszakadt validáció okán). Ha már ott van, ne vedd fel duplán.

4. **Megszakadt önjavító hurok felismerése (`[validate-loop]` marker + Validation History):** ha a `tasks.md` státusza `Implementálásra kész [validate-loop]` markert visel, egy korábbi validate-hurok szakadt meg — **ne** kezdj tiszta lapról. Derítsd ki a hurok állapotát:
   - Olvasd be a `# Validation History`-t: melyik volt az utolsó FAIL, melyik a megrekedt item, és hány a `Consecutive Failures for this item` (hányadik próbánál tartott).
   - Olvasd be a `tasks.md` `## Validációs javítások` szekcióját: vannak-e még elvégzetlen `[ ]` javító-taskok?
     - **Ha igen** (a fixer nem futott le vagy félbeszakadt): folytasd a hurkot a fixer újraindításával ezekre a taskokra, majd újra-validálj.
     - **Ha nincs** (a fixer befejezte, de az újra-validálás maradt el): futtasd újra a validálási lépéseket, és értékeld az eredményt a hurok szerint.
   - A `Consecutive Failures` számláló a 3-próba korlát alapja — a folytatáskor onnan számolj tovább, ne nullázd.

---

## Kontextus betöltési szabályok

- Olvasd be a `spec.md` Definition of done szekciót.
- Olvasd be a `plan.md` Tesztelési stratégia és Ellenőrzési stratégia szekciókat.
- Olvasd be a `tasks.md`-t.
- Ne olvasd be az egész forráskódot — csak azt, ami egy konkrét ellenőrzéshez szükséges.

---

## Validálási lépések

### 0. Riport mappa előkészítése

Mielőtt bármit futtatnál, győződj meg róla, hogy létezik a `specs/cycle-NN-<cycle-name>/test-report/` mappa. Ha nem létezik, hozd létre — ide kerül a `validate-decision.md`, a `sonar-report.md` és minden teszt-artefakt.

### 1. Gyors tesztek és kódminőség ellenőrzése (`test-runner` subagent)

Hívd a `test-runner` subagentet (`agents/test-runner.md`) a gyors (unit/integration) tesztek és — ha a `conventions.md` tartalmaz `## Sonar minőségellenőrzés` szekciót — a SonarQube-elemzés lefuttatására. A subagent maga dönti el a konkrét parancsokat a `conventions.md`/`plan.md` alapján, elindítja a szükséges Podman-konténert, és **strukturált összefoglalót** ad vissza (lásd az agent kontraktusát) — a nyers teszt-/Sonar-logot nem kéred vissza.

A subagent jelentése alapján:
- **Quality Gate PASS / N/A:** a `test-report/sonar-report.html` és `.md` riportok tájékoztató jellegű `MINOR`/`INFO` találatai nem akadályozzák a validálást.
- **Quality Gate FAIL vagy bármelyik gyors teszt FAIL:** rögzítsd a hibát a `# Validation History` szekcióba (lásd lent), és **ne indítsd el a 2. lépést (nehéz tesztek)** — lépj egyenesen a hurok FAIL ágára. A javító feladatok (`tasks.md`) felvételekor csak a `BLOCKER`, `CRITICAL` és `MAJOR` szintű Sonar-találatokat tekintsd kötelezően javítandó akadálynak (a subagent az összeset jelenti, a szűrés itt, nálad történik).

### 2. Nehéz tesztek és regressziós ellenőrzések (`test-runner` subagent)

Csak akkor hívd, ha az 1. lépés PASS volt. Hívd újra a `test-runner` subagentet, most a nehéz tesztek (E2E + regresszió) lefuttatására — a `tasks.md` `TREG` jelölésű taskjai és a `plan.md` `Regressziós érintettség` táblázata alapján. A subagent felelőssége a szükséges backend szolgáltatások/konténerek elindítása, a portütközés-elhárítás és az ideiglenes erőforrások takarítása (lásd az agent kontraktusát).

> **⚠ Átmeneti port-módosítás:** ha a subagent jelentése ideiglenes config-/port-csere kell, ellenőrizd, hogy a jelentés szerint sikeresen visszaállt-e az eredeti állapot; ha nem, állítsd vissza te (`git checkout -- <fájl>`), mielőtt a validate fázis véget ér — ez nem kerülhet be a ciklus diffjébe.

**Ismételt hibák naplózása (szkripttel, determinisztikusan):** mindkét lépés (1. és 2.) eredményét naplóznod kell a `specs/cycle-NN-<cycle-name>/test-report/validate-decision.md` `# Validation History` szekciójába. **A futás-bejegyzést és a per-item egymást-követő-bukás számlálót NE kézzel írd/számold** — a `failure-counter.py` szkript végzi (a telepítő a platform scripts-mappájába másolja: `.claude/scripts/` / `.agents/scripts/` / `.cursor/scripts/` / `.github/scripts/` / `.codex/scripts/`). A `test-runner` által **szó szerint** visszaadott bukott-item neveket add át neki:

```bash
# FAIL — minden bukott itemet külön --failed-item-ként (a test-runner nevein):
python3 <platform-scripts-mappa>/failure-counter.py \
  specs/cycle-NN-<cycle-name>/test-report/validate-decision.md \
  --result FAIL --timestamp "$(date '+%Y-%m-%d %H:%M')" \
  --failed-item "<pontos tesztnév/azonosító>" [--failed-item "<másik>" ...] \
  --details "<rövid ok>"
# PASS (minden zöld):
python3 <platform-scripts-mappa>/failure-counter.py \
  specs/cycle-NN-<cycle-name>/test-report/validate-decision.md \
  --result PASS --timestamp "$(date '+%Y-%m-%d %H:%M')"
```

A szkript hozzáfűzi a `Run X` bejegyzést a dokumentált formátumban, kiszámolja itemenként az egymást követő bukások számát, és a **kilépő kódjával jelzi a 3-próba szabályt (VD4): `0` = folytatható, `3` = legalább egy item elérte a 3-at → a hurok MEGÁLL** (a szkript kiírja, melyik item). Ha a `test-report/` mappa nem létezik, előbb hozd létre.

**Egy funkció csak akkor kész, ha minden teszt és a Sonar is átment.** Részleges PASS nem elfogadható: ha bármelyik teszt vagy a Sonar hibázik, az egész validate FAIL.

### 3. DoD és README ellenőrzések

#### A. Definition of done ellenőrzése
Minden DoD ponthoz adjál egyértelmű választ: ✓ vagy ✗, egy mondatban indokolva.

> **⚠ Fontos akció:** Minden teljesített (`✓`) pontot azonnal jelölj `[x]`-szel a `spec.md` megfelelő sorában is — ne várd meg a teljes validálás végét.

#### B. Meglévő komponens README ellenőrzése
Ha a ciklus meglévő komponens konfigurációját (env var-ok, indítási paraméterek, külső kapcsolatok) változtatta meg: a komponens `README.md` szinkronban van-e a változásokkal? Ha nem, jelezd — a README frissítése az implement fázis lezáratlan feladata.

#### C. Tasks ellenőrzése
Minden task `[x]` státuszban van-e? Ha van elvégzetlen task, jelezd.

#### D. Kódkommentek és docstringek ellenőrzése
Ellenőrizd a módosított vagy újonnan létrehozott fájlokban lévő kommenteket és JSDoc/TSDoc leírásokat. Győződj meg róla, hogy a végrehajtott kódváltozások (pl. átnevezések, logikai módosítások) után a hozzájuk kapcsolódó kommentek is frissültek, és nem maradtak elavult (stale) vagy félrevezető megjegyzések a forráskódban.

---

## Eredmény

A validálás végén adj egy tömör összefoglalót:

```
## Validálási eredmény

**Státusz:** PASS | FAIL

### Tesztek
- Unit: ✓ / ✗
- Integration: ✓ / ✗
- E2E: ✓ / ✗
- Regresszió: ✓ / ✗ / N/A
- Sonar Quality Gate: ✓ / ✗ / N/A

### Definition of done
- [ DoD pont ]: ✓ / ✗
...

### Tasks elvégzettsége
- Minden task [x]: ✓ / ✗ (ha ✗: felsorolás az elvégzetlen taskokról)

### Kódkommentek és dokumentáció
- Kommentek és docstringek naprakészek: ✓ / ✗

### Nyitott problémák
- [ha van]
```

---

## Az önjavító hurok (orchestrátor-hurok)

FAIL esetén **nem** adod vissza egyszerűen a vezérlést a felhasználónak. Levezényelsz egy iteratív javító hurkot — `implement-fixer` subagent → újra-validálás — amíg PASS nem lesz, vagy amíg a **3-próba szabály (VD4)** / a **felfelé menekülő ág (VD5)** meg nem állítja.

A meglévő FAIL-gépezet megmarad (a `validate-decision.md` `# Validation History`, a `tasks.md` `## Validációs javítások`, a státusz-visszafordítás) — csak a korábbi „kézi visszaadás a felhasználónak (futtasd újra a 06-ot)" lesz orchesztrált hurok. A javítást nem te végzed: azt az `implement-fixer` subagent (= a 06 Fix-módja) csinálja; te validálsz, naplózol, döntesz és státuszt fordítasz.

### ⚠ Anti-„teszt-csalás" garde (VD3 — a hurok legfontosabb szabálya)

**A hurok a KÓDOT igazítja a teszthez / Sonarhoz / DoD-hoz — SOHA nem fordítva.** A teszt és a Definition of done a **szerződés**; a hurok ezt a zöld eredmény érdekében **nem módosíthatja**.

**STOP — tilos** bármelyik:
- teszt assertion gyengítése/lazítása, vagy az elvárt érték a kódból visszamásolása;
- teszt `skip`/`xfail`/kikommentezése/törlése a zöldért;
- hardcode-olt „elvárt" érték, amely a tesztet zöldíti, de a valós viselkedést nem valósítja meg;
- a `spec.md` DoD-pont leszállítása/átfogalmazása, hogy könnyebben teljesüljön.

Ezt a szabályt az `implement-fixer` is megkapja (a 06 Fix-mód garde-ja) — egy olcsóbb LLM se sodródjon teszt-csalásba. **Ha egy hiba csak a teszt/DoD megváltoztatásával lenne zöld** → az nem kód-fix, hanem **tervezési hiba** → VD5 (felfelé menekülő ág), nem a teszt lazítása.

### A hurok egy iterációja

1. **FAIL naplózása + 3-próba (VD4) egy lépésben — a `failure-counter.py` szkripttel.** Futtasd a szkriptet a `--result FAIL` + a bukott item-nevekkel (lásd „Ismételt hibák naplózása"). Ez naplózza a futást ÉS kiszámolja a per-item számlálót — **ne kézzel**.
2. **3-próba döntés a szkript kilépő kódjából (VD4).** `exit 3` → legalább egy item elérte a 3-at → a hurok megáll (lásd „3-próba szabály mint hurok-korlát"); a megállás típusát a VD5 heurisztika dönti el (tervezési hiba → eszkaláció; egyébként → STOP + humán). `exit 0` → folytatható a hurok.
3. **Korai eszkaláció-ellenőrzés (VD5).** Ha az előző iteráció `implement-fixer` subagentje **eszkalációs jelzést** adott vissza (a hibát csak a teszt/DoD módosításával lehetne zöldre vinni), ne körözz tovább a 06-ban → **azonnal eszkalálj** (lásd „Felfelé menekülő ág"), nem kell megvárni a 3. próbát.
4. **Javító-taskok felvétele.** A FAIL-gépezet szerint (lásd „FAIL — javító-taskok felvétele"): `## Validációs javítások` szekció a `tasks.md` végén, prerequisite hivatkozásokkal, `[GREEN]`/`[CHECK]` taskként a konkrét teszt-/Sonar-hibák. Duplikátum-kerülés: ne vedd fel kétszer ugyanazt.
5. **Marker felvétele (VD6).** A `tasks.md` státuszát fordítsd `Implementálásra kész [validate-loop]`-ra. A marker jelzi: fix-mód aktív → a fixer automatikusan lépteti a státuszt, megerősítés nélkül.
6. **`implement-fixer` subagent indítása (VD2).** A konkrét teszt-/Sonar-hibalistával + a prerequisite riportokkal (lásd „A fixer-subagent indítása"). Ha a fixer **eszkalációs jelzést** ad vissza → ugorj a 3. pontra.
7. **Újra-validálás.** Kezdd elölről a „Validálási lépéseket" (gyors tesztek → Sonar → nehéz tesztek → DoD/README).
   - **PASS** (minden teszt + Sonar + DoD zöld) → a hurok konvergált, ugrás a „Státusz kezelés → PASS"-ra (itt kerül le a marker, és történik az egyetlen lezáró commit).
   - **FAIL** → új iteráció az 1. ponttól.

### A fixer-subagent indítása (VD2)

- A subagent **rendszerpromptja** az `agents/implement-fixer.md` wrapper, amely a `06-implement.md` „Fix-mód (validate-hurok belépő)" szekciójára delegál — nincs duplikált javító logika, a 06 minőségi szabályai automatikusan érvényesülnek.
- **Bemenet:** a `tasks.md` `## Validációs javítások` elvégzetlen taskjai (a konkrét teszt-/Sonar-/DoD-hibák) + a prerequisite riportok (`validate-decision.md`, és ha Sonar bukott, `sonar-report.md`).
- **Kimenet:** (a) az elvégzett javítások összefoglalója (mely taskot mivel zárt le), és (b) **eszkalációs jelzés**, ha valamelyik hibát csak a teszt/DoD módosításával lehetne zöldre vinni (VD3). A subagent **nem** módosíthatja a tesztet/DoD-ot, és **nem** írja a `validate-decision.md`-t — azt te (az orchestrátor).

### Felfelé menekülő ág (VD5 — escape hatch)

Nem minden FAIL kód-bug: néha **tervezési hiba** (a teszt/DoD a kóddal ellentmondó, vagy a terv hibás alapra épül). Ilyenkor a hurok ne 06-ban körözzön — a 06 sosem fogja zöldre vinni, mert csak a tesztet/DoD-ot lazítva lehetne, azt pedig VD3 tiltja.

**Detektálási heurisztika** — tervezési hiba jele, ha:
- **(a)** az `implement-fixer` eszkalációs jelzést adott vissza (a hibát csak a teszt/DoD megváltoztatásával lehetne zöldre vinni), **vagy**
- **(b)** a 3-próba elérésekor a megrekedt itemet az addigi javítási kísérletek alapján csak a teszt/DoD megváltoztatásával lehetne zöldre vinni.

**Teendő (STOP + eszkaláció), sorban:**
1. Naplózd a `# Validation History`-ba a megrekedt itemet, és hogy **tervezési hiba** miatt eszkalálsz (nem kód-bug).
2. **Státusz-visszafordítás 03/02-re:** fordítsd vissza az érintett tervezési dokumentum státuszát a megfelelő nem-kész értékre — `plan.md` → `Piszkozat` (ha a terv hibás), vagy `spec.md` → `Piszkozat` (ha maga a DoD a hibás/ellentmondásos). A `tasks.md` a `[validate-loop]` markerrel marad (a megrekedt állapot jelzése).
3. **Egyetlen lezáró commit** (VD8).
4. **Jelezd a felhasználónak az átadást** — ez tervezési kérdés, nem automatikus javítás (a list2 analyze-szellemű tervezési hurokra tartozik), lásd a jelzés szövegét lent. A folyamat a tervezés rendezése után a `05→06→07` úton tér vissza ide.

### 3-próba szabály mint hurok-korlát (VD4)

A hurok korlátja a **meglévő 3-próba szabály** — **nincs külön globális számláló**. Ha a `# Validation History` alapján bármely tesztnél vagy a SonarQube minőségellenőrzésnél a `Consecutive Failures for this item` eléri a **3**-at (a mostani futást is beleszámítva): a hurok megáll a **beragadt elemnél**. Ez okosabb, mint egy globális `max X`, mert pont a megrekedt itemet fogja meg.

- Ha a megállás **tervezési hiba** jele (VD5 heurisztika) → **eszkaláció** (felfelé menekülő ág).
- Egyébként → **STOP + humán** (megrekedt kód-bug): *„A(z) [Failed Item] egymás után harmadszor is elbukott. Humán beavatkozás szükséges — hogyan tovább?"* Ne folytasd a javítást a felhasználó válasza nélkül. Commit a végén (VD8); a `## Validációs javítások` és a `[validate-loop]` marker megmarad (megrekedt állapot).

### Commit-stratégia a hurokban (VD8)

- **A hurokban nincs iterációnkénti commit** — a korábbi FAIL-enkénti commit megszűnik.
- **Egyetlen lezáró commit** a hurok végén (PASS / 3-próba STOP / eszkaláció):
  ```bash
  git add specs/cycle-NN-<cycle-name>/
  git commit -m "cycle-NN: 07-validate"
  ```
- **Megszakítás-biztos:** a köztes commit hiányát a `# Validation History` + a `[validate-loop]` státusz-marker pótolja — ezekből a folytatás rekonstruálható (lásd „Megszakított futás kezelése").

### „Hol járunk" a megállási üzenetekben (LC2)

A user-felé tett megállási üzeneteknél (3-próba STOP, eszkaláció — ez a hurok **egyetlen** user-érintkezése, lásd VD7) jelezd, hol tart a hurok: a megrekedt elemet és a próbaszámot, a `# Validation History`-ra hivatkozva:

```
[VALIDATE · <Failed Item> · próba 3/3]
<üzenet szövege>
```

A válaszod végén kötelezően helyezz el egy közvetlen, kattintható linket a `validate-decision.md`-re.

---

## Státusz kezelés

> **A PASS automatikus, mert determinisztikus ellenőrzéseken alapul (tesztek + Sonar + DoD). Felhasználói megerősítés NEM szükséges — ne kérj megerősítést a `Kész` státuszra váltás előtt. Az eredmény bármikor ellenőrizhető a `validate-decision.md`-ben.**

### PASS

Minden teszt átment, a DoD teljesül, minden task `[x]`, és a Sonar Quality Gate PASS (vagy N/A).

Teendők:
1. **Vedd le a `[validate-loop]` markert** (ha a hurok futott): a `tasks.md` státusza `Kész`-re vált — marker nélkül. Frissítsd a `plan.md` és `spec.md` státuszát is `Kész`-re.
2. **Egyetlen lezáró commit** (a hurok alatt nem volt köztes commit — VD8):
   ```bash
   git add specs/cycle-NN-<cycle-name>/
   git commit -m "cycle-NN: 07-validate"
   ```
3. Jelezd: *"Validálás sikeres. Folytathatjuk a 8. lépéssel: dokumentáció szinkron (08-doc-sync). Az új fázis megkezdése előtt mindenképpen futtass egy `/clear` parancsot a kontextus kiürítéséhez, majd használd ezt a parancsot:*
   > ```
   > /bs-doc-sync input: @specs/cycle-NN-<cycle-name>
   > ```"*
   > **A válasz végén helyezd el a `validate-decision.md` közvetlen, kattintható linkjét.**

### FAIL — javító-taskok felvétele (a hurok 4–6. lépése)

Ha bármely teszt, a Sonar, vagy a DoD ellenőrzés hibázik, **nem** adod vissza a vezérlést a felhasználónak — a hurok következő iterációját készíted elő és indítod (lásd „Az önjavító hurok"). Lépések **sorban**:

```
[ ] 1. failure-counter.py lefuttatva (--result FAIL + bukott itemek) →
        # Validation History frissítve, a számláló determinisztikusan léptetve
[ ] 2. 3-próba a szkript kilépő kódjából: exit 3 → STOP
        (eszkaláció vagy humán, lásd lent) — NE indíts újabb fixert; exit 0 → tovább
[ ] 3. tasks.md → ## Validációs javítások fejezet létrehozva vagy folytatva
[ ] 4. A fejezet elejére prerequisite hivatkozásként berakva:
        - specs/cycle-NN-<cycle-name>/test-report/validate-decision.md
        - (ha Sonar hibázott) specs/cycle-NN-<cycle-name>/test-report/sonar-report.md
[ ] 5. Konkrét javítandó tesztek / Sonar hibák felvéve [GREEN] taskokként,
        a csoport végén egy [CHECK] ellenőrző taskkal (duplikátum-kerülés!)
[ ] 6. tasks.md státusz → Implementálásra kész [validate-loop]   (marker, VD6)
[ ] 7. implement-fixer subagent indítva a konkrét hibalistával (VD2)
[ ] 8. A fixer visszatérése után: ha eszkalációs jelzés jött → felfelé menekülő ág (VD5);
        egyébként újra-validálás (a hurok 7. lépése)
```

**A FAIL ág itt NEM commitol és NEM ad vissza vezérlést a felhasználónak** — a commit a hurok végén egyetlen alkalommal történik (VD8), a felhasználói érintkezés pedig csak a 3-próba STOP / eszkaláció esetén (VD7).

#### Eszkaláció jelzése a felhasználónak (VD5 — felfelé menekülő ág)

A „Hol járunk" fejléccel (LC2):
> **[VALIDATE · <Failed Item> · próba N/3]**
> *"A validáció során a(z) [Failed Item] tervezési hibának bizonyult: a kód csak a teszt vagy a Definition of done megváltoztatásával lenne zöld, amit a hurok nem tehet meg (anti-„teszt-csalás"). Ezért nem a 06-implementbe léptem vissza, hanem a tervezési fázishoz eszkalálok. A(z) [plan.md / spec.md] státuszát visszaállítottam, hogy a tervezési döntést rendezni lehessen. Folytasd a tervezés felülvizsgálatával:*
> ```
> /bs-write-plan (DoD-hiba esetén: /bs-write-spec) input: @specs/cycle-NN-<cycle-name>/plan.md (vagy spec.md)
> ```
> *A folyamat a tervezés rendezése után a 05→06→07 úton tér vissza ide."*
> **A válasz végén: kattintható link a `validate-decision.md`-re.**

#### 3-próba szabály (Validációs leállás — VD4)

Ha a `# Validation History` alapján bármelyik tesztnél vagy a SonarQube minőségellenőrzésnél a `Consecutive Failures for this item` értéke eléri a **3**-at (a mostani futást is beleszámítva) — **állj meg** (ez a hurok korlátja, nincs külön számláló). Döntsd el a megállás típusát a VD5 heurisztika szerint:
- **tervezési hiba** (csak a teszt/DoD módosításával lenne zöld) → **eszkaláció** (fenti üzenet);
- **megrekedt kód-bug** → a „Hol járunk" fejléccel: *„A(z) [Failed Item] egymás után harmadszor is elbukott. Humán beavatkozás szükséges — hogyan tovább?"* Ne folytasd a javítást a felhasználó válasza nélkül.

Mindkét esetben: **egyetlen lezáró commit** (VD8), a `[validate-loop]` marker és a `## Validációs javítások` a megrekedt állapot jelzésére a `tasks.md`-n marad.