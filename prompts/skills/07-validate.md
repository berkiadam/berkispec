---
phase: 07
name: validate
prerequisites:
  - "specs/cycle-NN-<name>/tasks.md státusz: Validálásra kész"
output:
  - "specs/cycle-NN-<name>/test-report/validate-decision.md"
  - "PASS esetén: spec.md / plan.md / tasks.md státusz: Kész"
prev: 06-implement
next: 08-review-and-merge
subagents: []
---

# 07 — Validálás

Spec driven development-ben fejlesztünk szoftvert. A fejlesztés ciklusokra van bontva. Minden ciklus egy önállóan lefejleszthető, önállóan tesztelhető részegysége a teljes implementációnak.

Ez a fejlesztési folyamat **7-es fázisa (a 0–8 fázisokból)**:
0. projekt inicializálás (setup)
1. ciklusok kezelése (setup)
2. spec
3. plan
4. tasks
5. analyze
6. implement
7. **validate** ← most itt vagyunk
8. review & merge

---

## Bemenet

A prompt bemenete a ciklus mappája (pl. `specs/cycle-NN-<cycle-name>`). A validációhoz szükséges fájlokat (`spec.md`, `plan.md`, `tasks.md`) ebben a mappában találod.

## Előfeltétel

1. **`conventions.md` létezés-ellenőrzés:** olvasd be a projekt gyökerében a `conventions.md`-t. Ha nem létezik, STOP — térjenek vissza a `00` fázishoz.

2. **Munkafa ellenőrzés:** futtasd `git status --short`. Ha van commitálatlan változtatás, listázd, és kérdezd meg egy körben, hogy commitáljam-e most vagy folytassam — várj a válaszra.

3. Olvasd be a megadott mappából a `tasks.md`, `plan.md` és `spec.md` fájlok státuszát.

- **Ha a `tasks.md` státusza nem `Validálásra kész`:** az implementáció még nem zárult le. Jelezd, és térj vissza a `06` fázishoz.
- **Ellenőrzőpont:** a `plan.md` és `spec.md` státusza elfogadható értékek:
  - `plan.md`: `Task írásra kész` vagy `Kész`
  - `spec.md`: `Tervezésre kész` vagy `Kész`
  - `Kész` mindkettőnél normális, ha a 08-as review után tértünk vissza ide.
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

---

## Megszakított futás kezelése

A validáció bármikor megszakadhat. Újraindítás (ismételt futtatás) esetén:
1. **Idempotens futás**: Kezdd elölről a validálási lépéseket. Ha a korábbi futás naplózott már valamit a `test-report/validate-decision.md`-be, az az előző (félbeszakadt) futásnak tekintendő.
2. **Beragadt erőforrások**: Ha a korábbi megszakított futásból beragadt teszt konténerek vagy folyamatok miatt portütközést tapasztalsz, lődd ki azokat, vagy keress új szabad portot a korábban leírt módon.
3. **Duplikált taskok elkerülése**: Ha a futás FAIL-lel zárul, és javító feladatokat kell felvenned a `tasks.md` `## Validációs javítások` szekciójába, mindig ellenőrizd, hogy a konkrét teszthiba vagy Sonar javítás nem szerepel-e már elvégzetlen taskként (egy korábbi félbeszakadt validáció okán). Ha már ott van, ne vedd fel duplán.

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

### 1. Gyors tesztek és kódminőség ellenőrzése
 
#### A. Helyi Unit és Integrációs tesztek
Futtasd le a plan Tesztelési stratégiájában meghatározott gyors helyi teszteket, a `conventions.md` Teszt keretrendszer / Teszt struktúra szekciója által megadott eszközzel és mappastruktúrával (a konkrét tool-nevet ne ismételd meg — a `conventions.md` a forrás):
- **Unit tesztek:** minden új és meglévő unit teszt átmegy-e?
- **Integration tesztek:** minden új és meglévő integration teszt átmegy-e?
 
#### B. SonarQube minőségellenőrzés (Podman & Riport Generálás)

**Ha a `conventions.md` NEM tartalmaz `## Sonar minőségellenőrzés` szekciót → skip: ugorj a 2. lépésre.**

Ha tartalmaz:
1. Indítsd el a SonarQube szervert (ha még nem fut): a `conventions.md`-ben megadott Podman-paranccsal.
2. Futtasd le a SonarQube analízist és a riportgenerálást a `conventions.md` `## Sonar minőségellenőrzés` szekciójában megadott scanner-/riport-paranccsal, a ciklusmappát (`specs/cycle-NN-<cycle-name>`) átadva.
   *A riportgenerálás kiértékeli a Quality Gate-et, és létrehozza a `sonar-report.md` és a látványos `sonar-report.html` fájlokat a megadott ciklusmappa `test-report/` almappájában.*
3. **Quality Gate PASS:** A szkript sikeresen lefut (exit code: 0). Ellenőrizd a létrehozott `test-report/sonar-report.html` és `test-report/sonar-report.md` riportokat. A riportokban szereplő `MINOR` és `INFO` szintű kódszagok csak tájékoztató jellegűek, nem akadályozzák a sikeres validációt, és nem szükséges javítani őket.
4. **Quality Gate FAIL:** A szkript sikertelen állapotkóddal tér vissza (exit code: 2).
   - A hibákat részletesen a generált `test-report/sonar-report.md` és `test-report/sonar-report.html` riportokban láthatod.
   - Rögzítsd a hibát a `specs/cycle-NN-<cycle-name>/test-report/validate-decision.md` fájl végén található `# Validation History` szekcióba.
   - A javító feladatok (`tasks.md`) felvételekor csak a `BLOCKER`, `CRITICAL` és `MAJOR` szintű hibákat tekintsd kötelezően javítandó akadálynak.
   - **Mielőtt továbbmennél a lassú regressziós/E2E tesztekre, a SonarQube Quality Gate-nek zöldnek (PASS) kell lennie!**

### 2. Nehéz tesztek és regressziós ellenőrzések

**E2E és regressziós tesztek futtatása előtt (vagy a teszt keretrendszer global setupjában) mindig ellenőrizd és indítsd el a szükséges backend szolgáltatásokat és konténereket. Erre a célra a `conventions.md` / `plan.md` által megadott, platformfüggetlen env-indító scriptet használd. Sose forduljon elő, hogy a teszt azért bukik vagy nem fut le, mert a környezet nem volt elindítva!**

**Portütközés kezelése:** Ha egy service indítása portütközéssel (address already in use) meghiúsul, ne állj meg. Keresd meg a következő szabad portot (`ss -tlnp | grep :<port>` vagy `lsof -i :<port>`), frissítsd átmenetileg az érintett konfigurációban (`docker-compose`, env fájl), és futtasd újra. Jelezd a felhasználónak melyik portot használtad helyette.

> **⚠ ÁTMENETI MÓDOSÍTÁS — NE COMMITOLD:** A portütközés miatt végzett config-/port-módosítás **ideiglenes**. A validáció végén ÁLLÍTSD VISSZA az eredeti állapotot, vagy győződj meg róla, hogy ezek a változtatások NEM kerülnek be a commitba (`git checkout -- <fájl>` a kérdéses configra). A validate fázis nem rögzíthet véletlen port-módosítást a ciklus diffjébe.

Futtasd le a plan Tesztelési stratégiájában meghatározott nehéz teszteket, majd a teljes regressziós suitot. **Ideiglenes erőforrások takarítása**: ha a tesztek futtatásához ideiglenes fájlokat hoztál létre vagy konténereket indítottál el, a futtatás befejezése után töröld ki a fájlokat és állítsd le / töröld a konténereket.

- **E2E tesztek** (`test/e2e/`): az e2e scriptek `PASS` eredménnyel zárnak-e?
- **Regressziós tesztek**: a `tasks.md` `TREG` jelölésű taskjai és a `plan.md` `Regressziós érintettség` szekciójának táblázata alapján futtasd le a megadott összes meglévő tesztfájlt és E2E scriptet.

**Ismételt hibák naplózása:** Minden egyes validációs vagy tesztfutás hibát naplóznod kell a `specs/cycle-NN-<cycle-name>/test-report/validate-decision.md` fájl végén található `# Validation History` szekcióba (ha a fájl nem létezik, a `test-report/` mappával együtt hozd létre).
Minden futásnál rögzítsd a hibás teszt nevét és számold ki, hogy ez hanyadik egymást követő bukása annak a konkrét tesztnek/elemnek:
```md
- **Run X (YYYY-MM-DD HH:MM) - FAIL**
  - **Failed Item:** [A hibás teszt pontos neve / azonosítója]
  - **Consecutive Failures for this item:** [Előző egymás utáni hibák száma + 1]
  - **Details:** [Hiba leírása és oka]
```
Ha a teljes validálás sikeres volt (minden gyors és nehéz teszt, regresszió, és Sonar átment), a történet végére jegyezd fel: `Run X (YYYY-MM-DD HH:MM) - PASS`.

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

## Státusz kezelés

> **A PASS automatikus, mert determinisztikus ellenőrzéseken alapul (tesztek + Sonar + DoD). Felhasználói megerősítés NEM szükséges — ne kérj megerősítést a `Kész` státuszra váltás előtt. Az eredmény bármikor ellenőrizhető a `validate-decision.md`-ben.**

### PASS

Minden teszt átment, a DoD teljesül, minden task `[x]`, és a Sonar Quality Gate PASS (vagy N/A).

Teendők:
1. Frissítsd a `tasks.md`, `plan.md` és `spec.md` státuszát `Kész`-re.
2. Commitáld a fázis lezárását:
   ```bash
   git add specs/cycle-NN-<cycle-name>/
   git commit -m "cycle-NN: 07-validate"
   ```
3. Jelezd: *"Validálás sikeres. Folytathatjuk a 8. lépéssel: review & merge (08). Használd ezt a promptot:*
   > ```
   > Kövesd a `prompts/skills/08-review-and-merge.md` utasításait.
   > Input: `specs/cycle-NN-<cycle-name>`
   > ```"*
   > **A válasz végén helyezd el a `validate-decision.md` közvetlen, kattintható linkjét.**

### FAIL

Ha bármely teszt, a Sonar, vagy a DoD ellenőrzés hibázik, végezd el az alábbi lépéseket **sorban**:

```
[ ] 1. validate-decision.md frissítve a hibával (# Validation History szekció)
[ ] 2. tasks.md → ## Validációs javítások fejezet létrehozva vagy folytatva
[ ] 3. A fejezet elejére prerequisite hivatkozásként berakva:
        - specs/cycle-NN-<cycle-name>/test-report/validate-decision.md
        - (ha Sonar hibázott) specs/cycle-NN-<cycle-name>/test-report/sonar-report.md
[ ] 4. Konkrét javítandó tesztek / Sonar hibák felvéve [GREEN] taskokként,
        a csoport végén egy [CHECK] ellenőrző taskkal
[ ] 5. tasks.md státusz → Implementálásra kész
[ ] 6. A FAIL ág változásai commitolva (a visszalépés állapota így rögzített):
        git add specs/cycle-NN-<cycle-name>/
        git commit -m "cycle-NN: 07-validate"
[ ] 7. Felhasználónak jelezve a visszalépést
```

Jelzés szövege:
> *"A validáció során hibák léptek fel. A hibákat és a riportokat rögzítettem a `tasks.md` végén új feladatokként, a státuszt pedig visszaállítottam `Implementálásra kész` állapotra. Folytasd az implementáció javításával:*
> ```
> Kövesd a `prompts/skills/06-implement.md` utasításait.
> Input: `specs/cycle-NN-<cycle-name>/tasks.md`
> ```"*

**3-próba szabály (Validációs leállás):** Ha a `# Validation History` alapján bármelyik tesztnél vagy a SonarQube minőségellenőrzésnél a `Consecutive Failures for this item` értéke eléri a **3**-at (a mostani futást is beleszámítva) — állj meg, és jelezd a felhasználónak: *„A(z) [Failed Item] egymás után harmadszor is elbukott. Humán beavatkozás szükséges — hogyan tovább?"* Ne folytasd a javítást a felhasználó válasza nélkül.
