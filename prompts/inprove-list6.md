

# A megerősítő kör lefokozása — végrehajtási terv

> **Ez a dokumentum önhordó.** Üres kontextusban is végrehajtható: az 1. szakasz megadja az
> orientációt, a 2. a mérést, a 3. az opciókat, a 4. a javasolt döntést, az 5. a pontos
> szerkesztési helyeket, a 6. az elfogadási kritériumokat.
> **Semmit nem kell kikövetkeztetni** — ha valami mégis hiányzik, az a terv hibája; írd bele.

> **Státusz:** javaslat — a döntés (3. szakasz) még nem született meg.
> **Előzmény:** a 07-validate futásának gyorsítására tett négy javaslat **4. tétele**. Az 1–3.
> tétel (EN prompt-nyelv, a gépi futtatási tábla kikényszerítése, `RV-SC` diff-szűkítés)
> **elkészült** — lásd az 1.4 szakaszt.

---

## 0. Hogyan használd ezt a dokumentumot

1. **Olvasd el az 1–2. szakaszt** (orientáció + mérés). Enélkül a 3. szakasz opciói
   félreérthetők: nem mindegy, hogy a megerősítő kör melyik eleme mennyibe kerül.
2. **A 3. szakasz döntést kér.** Ez nem gépies teendő — a felhasználóé. Amíg nincs döntés,
   az 5. szakaszhoz **ne nyúlj**.
3. **A döntés után az 5. szakasz szerint haladj**, és minden pont után futtasd a hozzá
   tartozó ellenőrzést (6. szakasz), majd **pipálj ebben a fájlban** (`- [ ]` → `- [x]`).
4. **Kétnyelvű repó:** minden prompt-szerkesztés **hu ÉS en** párban megy. A `lang-parity-check.py`
   ezt kapuzza, de csak szerkezetileg — a jelentés-helyességért te felelsz.

---

## 1. Orientáció

### 1.1 Mi a megerősítő kör

A `07-validate` önjavító hurka körökben dolgozik. Két körtípus van (a skill „Kör-típusok —
inkrementális hurok (VD10)" szekciója):

- **Teljes kör:** gyors tesztek → statikus réteg (Sonar + kódreview) → nehéz tesztek +
  regresszió → DoD/tasks/riport-kapu.
- **Könnyű kör:** a teljes gyors teszt-készlet + **kizárólag** az(ok) a bukott item(ek), ami(k)
  nehéz teszt, Sonar vagy review-finding volt(ak).

A hurok menete a skill saját ábrája szerint:

```
1. kör      TELJES    → FAIL  → fix
2. kör      KÖNNYŰ    → FAIL  → fix
3. kör      KÖNNYŰ    → zöld  → NEM PASS! kötelező megerősítő kör
4. kör      TELJES    → PASS (vagy FAIL → a hurok folytatódik)
```

A **4. kör a megerősítő kör**: egy **teljes** kör, **javítás nélkül**, közvetlenül azután, hogy
egy könnyű kör zöld lett.

### 1.2 Miért létezik

Két, egymástól független indoka van, és ezeket a lefokozáskor külön kell kezelni:

1. **Mérhetőség (VD10/1).** Egy könnyű körben a PASS feltételeinek egy része **meg sem mérhető**
   — nem futott nehéz teszt, nem futott Sonar, nem futott teljes review. A PASS ezért csak
   teljes körből adható.
2. **A javítás mellékhatása.** A fixer a kódot módosította; a megerősítő kör azt kérdezi, hogy
   a javítás **nem tört-e el mást**.

### 1.3 Hol van definiálva (a szerkesztendő helyek)

| Hely | Mit mond |
|---|---|
| `skills-{hu,en}/07-validate.md` → „Kör-típusok" tábla | a teljes kör kiváltója: „(a) a fázis **első** köre; (b) a **záró megerősítő** kör" |
| ugyanott, **1. kötelező szabály** | „PASS kizárólag TELJES körből adható… utána **azonnal** teljes megerősítő kör indul, ugyanabban a menetben, javítás nélkül" |
| ugyanott, **4. kötelező szabály** | „**A gyors készletet nem szűkítjük.** …másodpercekbe kerül, viszont elkapja, ha a javítás máshol tört el valamit." |
| „Az önjavító hurok" → 8. pont **Zöld** ága | „**még NEM PASS.** Azonnal, javítás nélkül indíts egy **TELJES megerősítő kört** (gyors tesztek → **Sonar + kódreview** → nehéz tesztek + regresszió → DoD/tasks/riport-kapu)… A review itt **inkrementálisan** fut" |
| „Státusz kezelés → PASS" előtti 🔴 blokk (VD10/1) | a PASS-ellenőrzés: „a lépés-táblában szerepel a nehéz teszt, a Sonar (vagy `N/A` a plan szerint) **és a lefutott kódreview**" |

A körnaplózás oldaláról: `round-log.py --type TELJES|KÖNNYŰ --trigger "megerősítő kör"`.
A záró kapu oldaláról: `validate-gate-check.py --stage close --require-review`.

### 1.4 Mi készült el már (kontextus)

Ugyanennek a gyorsítási körnek az 1–3. tétele **kész**:

- **EN prompt-nyelv** — kiderült, hogy már telepítve volt; nincs további nyereség rajta.
- **Gépi futtatási tábla (TP4) kikényszerítése** — bekerült az `analyze-gate-check.py`
  `REQUIRED_PLAN_TABLES` listájába (`S1` kód). Ettől a 07 nem esik vissza a drága
  `test-runner` subagentre.
- **`RV-SC` diff-szűkítés** — a `reviewer` mostantól forráskódra szűkített diffet kap
  (`':(exclude)specs/**'` + generált könyvtárak + lockfile-ok).

**Ezért a mostani mérést a fenti állapotra kell érteni**, nem a korábbira.

---

## 2. Mérés — mibe kerül a megerősítő kör

A kör négy eleme **nagyon eltérő** költségű. Ez a terv legfontosabb megállapítása: aki
„a megerősítő kört" akarja olcsóbbá tenni, annak elemenként kell néznie.

| Elem | Token-költség | Óraidő | Mit véd |
|---|---|---|---|
| Gyors tesztek (`run-tests.py`) | **elhanyagolható** — a szkript 10–20 sorban válaszol, a nyers log soha nem kerül kontextusba | másodpercek–percek | a javítás máshol tört el valamit (unit szinten) |
| Sonar (`sonar-gate.py`) | **elhanyagolható** — szkript, gépi kimenet | 1–2 perc | a javítás új kódszagot vitt be |
| **Kódreview (RV1/RV2)** | **nagy** — a `reviewer` a legdrágább subagent-hívás a fázisban | percek | lásd a 2.1 pontot |
| **Nehéz tesztek (E2E + regresszió)** | közepes — a riport gépi, de a stack-kezelés hosszú | **a legtöbb óraidő** — tiszta indítás + takarítás | a javítás integrációs szinten tört el valamit |

### 2.1 A kulcs-megfigyelés: a megerősítő kör review-ja jellemzően üresjárat

A skill a megerősítő körben **inkrementális** review-t ír elő:

> „A review itt **inkrementálisan** fut: az előző `code-review.md`-t átadva, a még nyitott
> `<status:must_fix>`-ekre fókuszálva."

Az inkrementális review (RV2) definíció szerint **kizárólag a még nyitott `MF-NN` findingokat
nézi** — a `reviewer` kontraktusa is így szól („a teljes diff újra-review-ja tilos").

Ebből következik: **ha a megerősítő kör indulásakor nincs nyitott `MF-NN`** (márpedig
tipikusan nincs, hiszen az előző kör épp ezért lett zöld), akkor az RV2-nek **nincs mit
megvizsgálnia**. Nem tudja elkapni a fixer által **újonnan** bevitt problémát sem, mert nem a
friss diffet nézi, hanem a régi findinglistát.

**Vagyis a megerősítő kör review-ja ilyenkor nem gyengébb védelem — hanem semmilyen**, miközben
a fázis legdrágább subagent-hívása. Ez a legjobb vágási pont.

> ⚠ **Ez a megállapítás felülírja a korábbi javaslatot.** Az eredeti javaslat a **gyors teszteket**
> akarta kihagyni a megerősítő körből — az viszont a kör **legolcsóbb** eleme, ráadásul a skill
> 4. kötelező szabálya külön indokolja a megtartását („másodpercekbe kerül, viszont elkapja, ha
> a javítás máshol tört el valamit"). A gyors teszteket **meg kell tartani.**

---

## 3. Opciók — döntést igényel

Mind a négy opció **azonos invariánst tart**: a PASS forrása továbbra is teljes kör, és a
nehéz tesztek a megerősítő körben **lefutnak**.

### O1 — A review kimarad, ha nincs nyitott `MF-NN` *(javasolt)*

A megerősítő körben a kódreview akkor és csak akkor fut, ha maradt nyitott `MF-NN`. Ha nincs,
a lépés `kihagyva (nincs nyitott MF-NN)` bejegyzést kap.

- **Nyereség:** a fázis legdrágább subagent-hívása marad ki, körönként egyszer.
- **Minőség-ár:** **gyakorlatilag nulla** — lásd a 2.1 pontot: az RV2 ilyenkor sem vizsgálna semmit.
- **Kockázat:** a PASS-ellenőrzés ma megköveteli a „lefutott kódreview" sort a lépés-táblában
  (VD10/1) — ezt együtt kell módosítani, különben a kapu ellentmond a szabálynak.

### O2 — A Sonar kimarad, ha a fixer diffje nem érint forrásfájlt

Ha a fixer csak dokumentumot/tesztet módosított, a Sonar nem hozhat új találatot.

- **Nyereség:** 1–2 perc óraidő, minimális token.
- **Minőség-ár:** kicsi, de nem nulla (a Sonar teszt-fájlokra is futhat, ha a projekt így méri).
- **Megjegyzés:** a mechanizmus **már létezik** — a skill ismeri a `kihagyva (a hívó kérésére)`
  állapotot. Csak az alapértelmezést kell megfordítani ebben az egy körben.

### O3 — A gyors tesztek kimaradnak *(NEM javasolt)*

Az eredeti javaslat. A 2. szakasz mérése alapján a **legolcsóbb** elemet vágná ki, miközben ez
az egyetlen olcsó háló a „a fix máshol tört el valamit" ellen. **Elvetésre javasolt** — de itt
marad dokumentálva, hogy ne merüljön fel újra megfontolatlanul.

### O4 — A megerősítő kör teljesen elmarad, ha a fixer nem módosított forrásfájlt

Ha a `git diff` szerint a fixer egyetlen forrásfájlt sem érintett (csak `tasks.md`-t pipált,
dokumentumot javított), akkor nincs mit megerősíteni.

- **Nyereség:** a teljes kör (a nehéz tesztekkel együtt) — messze a legnagyobb.
- **Minőség-ár:** **valódi.** Az utolsó zöld kör könnyű volt, tehát nem futott nehéz teszt;
  ha a hurok csak könnyű köröket látott, PASS-t adnánk E2E-bizonyíték nélkül.
- **Feltétel, ami nélkül nem szabad:** csak akkor alkalmazható, ha **ebben a fázisban** már
  futott legalább egy teljes kör zöld nehéz tesztekkel, és azóta forrásfájl nem változott.
  Ez a feltétel gépiesen ellenőrizhető a `validation-report.md` lépés-tábláiból.

### Döntési tábla

| Opció | Nyereség | Minőség-ár | Javaslat |
|---|---|---|---|
| **O1** — review kihagyása, ha nincs nyitott `MF-NN` | nagy (token) | ~nulla | ✅ **javasolt** |
| **O2** — Sonar kihagyása forrás-érintetlen fixnél | kicsi (óraidő) | kicsi | ✅ javasolt |
| **O3** — gyors tesztek kihagyása | elhanyagolható | közepes | ❌ elvetve |
| **O4** — a kör elhagyása szigorú feltétellel | **legnagyobb** | valódi, de korlátozott | ⚠ döntést kér |

- [ ] **D1 — Döntés:** melyik opciók valósuljanak meg? (javasolt: **O1 + O2**; az **O4** külön
      döntés, mert ez az egyetlen, ami tényleges lefedettséget áldoz)

---

## 4. A javasolt csomag (O1 + O2)

Ha D1 az ajánlást fogadja el, a megerősítő kör így néz ki:

```
Megerősítő kör (TELJES, javítás nélkül)
  1. gyors tesztek           → FUT (változatlan)
  2/a Sonar                  → FUT, KIVÉVE ha a fixer diffje nem érint forrásfájlt
  2/b kódreview (RV2)        → FUT, KIVÉVE ha nincs nyitott MF-NN
  3. nehéz tesztek + regr.   → FUT (változatlan)
  4. DoD/tasks/riport-kapu   → FUT (változatlan)
```

**Amit ez NEM változtat meg:** a PASS továbbra is teljes körből jön, a nehéz tesztek továbbra is
lefutnak, a leállási korlátok (VD4) és a körnaplózás (VD9) érintetlen.

---

## 5. Végrehajtás — pontos szerkesztési helyek

> A sorszámok tájékoztatók (a fájl változik) — a **idézett szöveg** az igazi horgony.

### 5.1 A hurok „Zöld" ága — a megerősítő kör leírása

- [ ] **T1.** `skills-hu/07-validate.md` + `skills-en/07-validate.md`, „Az önjavító hurok"
      8. pont **Zöld** ága. A mai szöveg:
      *„Azonnal, javítás nélkül indíts egy **TELJES megerősítő kört** (gyors tesztek → **Sonar +
      kódreview** → nehéz tesztek + regresszió → DoD/tasks/riport-kapu)."*
      Egészítsd ki a két feltételes kihagyással (O1, O2), és **mondd ki az indokot** — az RV2
      nyitott `MF-NN` nélkül nem vizsgál semmit (2.1). Az indok nélkül egy gyenge modell
      „biztos, ami biztos" alapon úgyis lefuttatja.

### 5.2 A PASS-ellenőrzés összehangolása

- [ ] **T2.** Ugyanott, a „Státusz kezelés → PASS" előtti 🔴 blokk (VD10/1). A mai ellenőrzés:
      *„a lépés-táblában szerepel a nehéz teszt, a Sonar (vagy `N/A` a plan szerint) **és a
      lefutott kódreview**"*.
      A „lefutott kódreview" feltételt bővítsd: **lefutott VAGY `kihagyva (nincs nyitott MF-NN)`**.
      Ugyanez a Sonarra az O2 miatt.
      > 🔴 **Ezt a T1-gyel EGYÜTT kell megcsinálni.** Ha csak a T1 megy be, a kapu ellentmond a
      > szabálynak: a kör jogosan hagyja ki a review-t, a PASS-ellenőrzés viszont elbukik rajta.

### 5.3 A „Kör-típusok" tábla és az 1. kötelező szabály

- [ ] **T3.** A „Kör-típusok" tábla **teljes kör** sora és az **1. kötelező szabály** ma azt
      sugallja, hogy a teljes kör mind a négy lépést mindig lefuttatja. Írd hozzá egy fél
      mondatban, hogy a megerősítő körben a statikus réteg két eleme **feltételesen** kimarad,
      és hivatkozz a hurok 8. pontjára. A **4. kötelező szabályt** („A gyors készletet nem
      szűkítjük") **ne bántsd** — az O3 elvetve.

### 5.4 A kapu-script

- [ ] **T4.** `prompts/scripts/validate-gate-check.py` — `check_review()`. Ma a hiányzó
      `code-review.md` `--require-review` mellett bukás. Az O1 után a megerősítő körben
      **létező, de nem frissített** `code-review.md` a normális eset — ez ma is átmegy
      (nincs nyitott `- [ ]`), tehát **valószínűleg nincs teendő**.
      **Ellenőrizd, ne feltételezd:** futtasd le a 6.2 próbát, és csak akkor módosíts, ha bukik.

### 5.5 Nyelvi paritás és tükrök

- [ ] **T5.** `lang-parity-check.py --check --strict` → exit 0.
- [ ] **T6.** Agent-prompt nem változik ebben a tervben, de ha mégis: `sync-gemini-agents.py`.

---

## 6. Elfogadási kritériumok

- [ ] **A1.** `bash prompts/scripts/acceptance-check.sh` → **10 teljesült · 0 bukott**.
      A 16.1 keret bukni **fog** (szándékos tartalmi változás) — ellenőrizd, hogy a változott
      hash-ek száma **pontosan** a várt halmaz (a `07-validate` 5 platformon = 5 skill-hash,
      agent 0), majd `--baseline`-nal alapozz újra.
- [ ] **A2.** `python3 prompts/scripts/lang-parity-check.py --check --strict` → exit 0.
- [ ] **A3.** Token-mérés: a telepített `bs-07-validate/SKILL.md` mérete **nem nőhet érdemben**
      (a kihagyási szabályok szövege pár száz karakter). A cél a **futásidejű** megtakarítás,
      nem a skill rövidítése — ha a skill érdemben hízik, a megfogalmazás túl bőbeszédű.

### 6.2 Kapu-próba (a T4-hez)

Építs egy próba-ciklusmappát, amelyben a `code-review.md` létezik, **nincs** benne nyitott
`- [ ] **MF-NN**`, és a `validation-report.md` utolsó köre `— TELJES`, a lépés-táblában
`kódreview … kihagyva (nincs nyitott MF-NN)` sorral. Ezen:

```
python3 prompts/scripts/validate-gate-check.py <ciklusmappa> --stage close --require-review
```

**Elvárás:** exit 0. Ha bukik, a T4 mégis kell.

---

## 7. Kockázatok

1. **A gyenge modell „biztos, ami biztos" alapon lefuttatja a kihagyható lépést.** Ez ellen
   egyetlen dolog véd: a kihagyás **indokának** kimondása a promptban (2.1), nem csak az
   engedélyé. Ezt a T1 kötelező része.
2. **T1 és T2 szétcsúszása.** Külön commitban bemenve a kapu ellentmond a szabálynak. Egy
   commitba menjenek.
3. **Az O4 csendes bekúszása.** Az O4 külön döntés (D1). Ha valaki a T1 kapcsán „logikusnak"
   érzi az egész kör elhagyását, az **lefedettség-vesztés** — a hurok könnyű körei nem futtatnak
   nehéz tesztet.
4. **A mérés elavulása.** A 2. szakasz táblája az `RV-SC` **utáni** állapotra érvényes. Ha a
   diff-szűkítés változik, a review költsége is változik — a táblát frissíteni kell.

---

## 8. Végrehajtási sorrend

1. **D1 döntés** (3. szakasz) — enélkül semmi.
2. **T1 + T2 egyetlen commitban** (hu + en), utána **A2**.
3. **T3** (hu + en).
4. **6.2 kapu-próba** → ha bukik, **T4**.
5. **A1** — elfogadási sor + a 16.1 újraalapozás.
6. Ha a felhasználó az **O4**-et is kérte: külön terv-szakasz kell hozzá (a „futott-e már teljes
   kör zöld nehéz tesztekkel" feltétel gépi ellenőrzésével), **nem** a T1 kiterjesztéseként.

### Commit-stratégia

Egy commit a T1+T2 párosnak, egy a T3-nak, és ha kell, egy a T4-nek. Üzenet-minta a repó
szokása szerint: `07.4: a megerősítő kör statikus rétege feltételessé válik (O1+O2)`.

---
---

# II. Az 05-analyze gyorsítása — a maradék tételek

> **Ez a rész önhordó, de NEM önálló dokumentum:** az I. rész (a 07 megerősítő köre) független
> tőle, csak a fájl közös. A II. rész az `05-analyze` fázis gyorsítására tett hat javaslat
> **maradéka**: az 1–3. tétel (a fixer önellenőrzése, a négy párhuzamos diagnoszta-kör
> szeletelt bemenettel, a párhuzamos lokális fix-batch) **elkészült** — lásd a II.1 szakaszt.
> **Státusz:** javaslat. A II.3–II.6 tétel egyike sincs eldöntve.

---

## II.1 Ami már elkészült (a kiindulási állapot)

| Tétel | Szabály-ID | Hol él |
|---|---|---|
| A fixer a visszatérése ELŐTT maga futtatja a mechanikus kaput, és a `kapu:` mezőben jelenti az eredményt; a 4.b orchestrátor-kör védőhálóvá szelídült | `GS1` | `agents-{hu,en}/{spec,plan,tasks}-fixer.md`, `skills-*/05-analyze.md` 4.b |
| A szemantikai diagnózis **három párhuzamos körre** oszlik (`s1-dup-underspec` = 1+3., `s2-coverage` = 2+5., `s3-conventions` = 4. kategória), a 6. kategória marad az `analyzer-exec`-nél → négy párhuzamos kör | `SH1` | `agents-*/analyzer.md` (hatókör-paraméter), `skills-*/05-analyze.md` („A négy diagnoszta-kör") |
| A körök bemenetét a kapu **kimetszi** (`--emit-slices` → `<ciklus>/analyze-slices/*.md`, önmagát rejtő `.gitignore`-ral), így egyik kör sem olvassa a teljes négyest | `SH1` | `scripts/analyze-gate-check.py` (`SLICES`, `emit_slices`) |
| Ha minden `Must Fix` **lokális** (megfogalmazás, hang, útvonal-formátum, duplikátum-összevonás, elromlott `[P-…]`), a fixerek egyetlen üzenetben, **párhuzamosan** indulnak, downstream re-deriválás nélkül | `LF1` | `skills-*/05-analyze.md` 1.a |

**Amit ez a csomag NEM oldott meg** — ezek a II.3–II.6 tételek.

---

## II.2 Mérés — ezt kell megismételni döntés előtt

A II.3–II.6 sorrendje attól függ, hogy **melyik a hosszú pólus**. Ez ma nincs megmérve, és
találgatásból rossz tételt választanánk. A recept:

1. Futtass egy éles `05-analyze` ciklust FAIL-lel (legalább 2 iteráció).
2. A Hurok-naplóba iterációnként írasd bele: **a hívások számát** (kapu, kör, fixer), **a körök
   eltelt idejét** külön-külön, és **az emberi kérdés-körök számát + a válaszra várás idejét**.
3. A három szám aránya adja a döntést:
   - ha az **emberi kérdés-körök** dominálnak → **II.3** (kérdés-batch) az első tétel;
   - ha a **kör-tokenek** dominálnak → **II.4** (jelölt-inventory);
   - ha az **iterációszám** dominál (3/3 feladva) → **II.5** (shard-szűkített közbenső kör).

> **A II.1 utáni állapotot mérd, ne a régit.** A négy párhuzamos kör és a `GS1` már megváltoztatta
> az arányokat: a fixer-körfordulások száma iterációnként 2–4-gyel csökkent.

---

## II.3 Döntés-jellegű tételek előre, BATCHELVE — döntést igényel

**A probléma.** Egy döntést igénylő megállapítás ma a leglassabb úton jut a felhasználóhoz:
kör → merge → fixer lefut → `Knn` → kérdés → válasz → fixer újra. A `TS` túlélés-szabály
ráadásul csak a **második** túlélés után eszkalál, tehát a rossz esetben két iteráció ég el
azelőtt, hogy a felhasználó egyáltalán meglátná a kérdést.

**A javaslat.** Az összefésülésnél (a fixer indítása ELŐTT) osztályozd a tételeket
`fixer-javítható` / `döntés-igényes` szerint. A döntés-igényeseket (ambiguitás, súlyos
konvenció-ütközés, definiálatlan komponens) az orchestrátor **azonnal** felteszi — és **egy
blokkban az összeset**, nem egyesével.

**Miért döntést igényel.** Ütközik az „egyszerre egy kérdés" szabállyal, ami szándékos
gyenge-modell-védelem (a `05` „Kérdezési szabályok" szekciója és a `shared/questions-tasks.md`).
Az érv a batch mellett: itt az **orchestrátor** kérdez, nem a fixer, és a fázis eltelt idejének
nagy részét épp az emberi körök adják. Az érv ellene: több kérdés egy blokkban a gyengébb
modellnél összecsúszó válaszokat és félrevezetett `[x]` pipálást szül.

**Három lehetséges alak (a döntés ezek között van):**

- **A) Nincs batch, csak korábbi eszkaláció.** A `TS` az **első** túlélés után eszkalál a
  döntés-jellegű kategóriákban. Egy iterációt nyer, szabályt nem sért. *(A legkisebb kockázat.)*
- **B) Előre-osztályozás, egyesével kérdezve.** A döntés-igényes tételek a fixer előtt jönnek ki,
  de továbbra is egy kérdés / egy válasz. A fixer-körfordulásokat nyerjük meg, az emberi
  köröket nem.
- **C) Előre-osztályozás + batch.** A teljes nyereség, a teljes szabály-ütközéssel.

**Ha C mellett dönt a felhasználó, ez kell hozzá:**
- [ ] `skills-{hu,en}/05-analyze.md` — az összefésülés (`A négy diagnoszta-kör` → `Az összefésülés
      a te dolgod`) új 5. pontja: a `döntés-igényes` osztály definíciója + a batch-kérdés formátuma.
- [ ] Ugyanott a „Kérdezési szabályok" szekcióban **kimondott kivétel**: az `05` orchestrátor
      döntés-batchje az egyetlen hely, ahol több kérdés mehet egy blokkban — a fixerek és a többi
      fázis szabálya nem változik.
- [ ] A batch-formátum: számozott lista, tételenként `[FÁZIS · iter n/max X · FÁZIS/Knn]` fejléc,
      és **kötelező visszaolvasás**: a válaszok átvezetése után az orchestrátor tételenként
      visszaidézi, mit írt be, mielőtt a fixert indítja.
- [ ] Elfogadás: egy éles ciklus, ahol 3 döntés-igényes tétel van — a hurok **egy** emberi körben
      kapja meg mindhárom választ, és a `*-questions.md` mindhárom `[x]`-e a helyes döntést hordozza.

---

## II.4 Jelölt-inventory az 1–4. kategóriára (a `SH1` folytatása)

**Az elv, ami már bizonyított.** A 6. kategóriát az `AG3` leltár tette olcsóvá: a subagent nem
**keres**, hanem **ítél** egy kész jelölt-listán. Ugyanez a négy szemantikai kategóriára még nincs
meg — a szeletelés (`SH1`) csak a **bemenet méretét** vágta le, a keresés munkáját nem.

**Mit lehet gépiesen jelöltté tenni** (mind a `analyze-gate-check.py`-ba, a leltár mellé):

| Kategória | Jelölt-generátor | Blokk |
|---|---|---|
| 1. duplikáció | normalizált bekezdés-/szakaszpárok `difflib.SequenceMatcher` hasonlósága a plan-en belül és plan↔tasks között, küszöb felett | `## Duplikátum-jelöltek` |
| 2. ambiguitás | vágy-szótár (`megfelelő`, `gyors`, `robusztus`, `optimális`, `hatékony`) + **szám és összehasonlítás nélküli** `DoD-NN` és elfogadási sorok | `## Ambiguitás-jelöltek` |
| 3. alulspecifikáció (KX3-próza) | a spec tábla- és listasorai, amelyek jellegzetes tokenje nem szerepel a plan-ben (a mai `V1`/`V2` csak kódblokkot és terjedelmet mér) | `## Csonkítás-jelöltek` |
| 4. konvenció-ütközés | `conventions.md`-ből kulcs-érték tények kinyerése (stack, teszt-eszköz, elnevezés, útvonalak), majd ütköző tokenek keresése a plan-ben | `## Konvenció-jelöltek` |

**Ez a legnagyobb token-nyereség, és a legnagyobb munka.** Becsült méret: 300–400 sor a kapuba,
plusz a négy blokk átvezetése a három kör promptjába. A **fő kockázat a false-positive ráta**:
minden jelölt-fajtát külön kell hangolni, mert egy zajos jelölt-lista rosszabb, mint a semmi
(a kör az ítélet helyett a szűrésre megy el). Ezért:

- [ ] **Egy jelölt-fajta = egy külön lépés, saját méréssel.** Kezdd a **2. kategóriával**
      (a vágy-szótár a legkevésbé zajos), és csak akkor menj a következőre, ha a jelöltek
      **legalább fele** valódi megállapítássá válik egy éles cikluson.
- [ ] A jelölt-blokk **soha nem megállapítás**: a kapu `Must Fix` és `Javaslatok` blokkja nem nő
      tőle, az exit code nem változik. Ugyanaz a szerződés, mint a leltárnál.
- [ ] A kör promptja mondja ki: **a jelölt-lista nem szűkíti a hatókört** — a szeleten kívüli
      megállapítás továbbra is jelenthető (különben a zajszűrés lefedettség-vesztéssé válik).

---

## II.5 Shard-szűkített közbenső kör + szakasz-hash cache

**A probléma.** A `D10` szerint minden kör teljes, és `max X = 3` iterációban akár **három** teljes
négy-körös diagnózis fut le — miközben a 2. és 3. iteráció jellemzően egyetlen dokumentum egyetlen
szakaszát érinti.

**A javaslat.** A `PASS` garanciáját megtartva:
- az **1..n−1** iterációkban csak a kapu + azok a körök futnak, amelyek szeletét a
  `git diff` érintette;
- a `PASS` előtt **egy teljes kör** kötelező (ez marad a `D10` betűje).

**Determinisztikus biztosíték.** A kapu a szelet-fájl fejlécébe írja minden bemeneti szakasz
**tartalom-hash-ét**, és az `analyze-report.md` Hurok-naplója rögzíti őket. Egy kör csak akkor
hagyható ki, ha **minden** input-szakaszának hash-e változatlan az előző körhöz képest. Ez nem
LLM-ítélet, hanem összehasonlítás — ezért nem tud csendben lefedettséget veszíteni.

- [ ] `scripts/analyze-gate-check.py` — `# SECTION-HASHES:` sor a szelet fejlécébe (szakaszonként
      rövid `sha256`), és egy `--slice-hashes` kimeneti blokk az orchestrátornak.
- [ ] `skills-{hu,en}/05-analyze.md` — a 6. lépés kap egy „mit kell újrafuttatni" alpontot,
      a `D10` mellé kimondva, hogy a **PASS-kör** továbbra is teljes.
- [ ] `lang/{hu,en}/05-analyze.md` — a Hurok-napló sor-formátuma kap egy `kihagyott körök:` mezőt
      (audit-nyom: ha valaki később hibát talál, látszik, melyik kör mit nem nézett meg).
- [ ] **Kockázat, amit ki kell mondani:** a kereszt-dokumentumos csatolás. Egy `tasks.md`-változás
      nyithat rést olyan körben, aminek a szelete nem változott (pl. `s3-conventions`). Ezért a
      kihagyás feltétele **minden** input-szakasz változatlansága, és nem elég a „saját"
      dokumentum változatlansága.

---

## II.6 A drága tier háromszorozódása — a `SH1` nyitva hagyott ára

**A tény.** Az `install-helper.py` `AGENT_MODEL_KEYS` **agent-stem szerint** rendel tiert
(`analyzer` → `deep_reasoning_agent`). Mivel a három szemantikai kör **ugyanazt az `analyzer`
definíciót** hívja, mind a három a **legdrágább** tieren fut. A szeletelés miatt a bemenet
körönként jóval kisebb, tehát a token-összeg nagyságrendileg 1,3–1,5× (nem 3×), de ez az
**Opus-osztályú** kereten jelenik meg — épp azon, amit a rendszer szándékosan egyetlen pontra
szorít (README 5.3).

**A javaslat.** Ha a drága keret a szűk keresztmetszet, a `s2-coverage` és/vagy az
`s3-conventions` kör kapjon **saját agent-definíciót** `default` tieren:

- [ ] `agents-{hu,en}/analyzer-conv.md` — a 4. kategória önálló, vékony diagnosztája
      (`s3-conventions` a legjobb jelölt: a `conventions.md` kulcs-érték jellegű összevetése a
      legkevesebb reasoningot igényli).
- [ ] `lang/{hu,en}/descriptions.json` — `description` + `role` mindkét nyelven (LG26).
- [ ] `scripts/install-helper.py` — `READONLY_AGENTS` (kötelező: read-only sandbox) és — ha
      `default`-nál más kell — `AGENT_MODEL_KEYS`.
- [ ] `models.json` — platformonként `effort` sor, ha a `default` nem jó.
- [ ] `scripts/sync-gemini-agents.py` futtatása (az új agent `agent.json` váza automatikusan
      létrejön), majd a `toolNames` kézi beállítása.
- [ ] README: az agent-tábla, az 5.3 tier-tábla és az 5.4 ábra.

> **Miért nem ez lett az első megoldás.** Egy új agent-definíció **hét** felületet érint (fenti
> lista), a hatókör-paraméter viszont egyet. A II.1 ezért a kis felületű utat választotta —
> a tier-szétválasztás akkor válik indokolttá, ha a mérés (II.2) kimutatja a drága keret
> telítődését.

---

## II.7 Amit szándékosan NEM javasolunk

1. **Az analyzer szűkítése a `git diff`-re.** A `D10` pont ezt zárja ki: a kereszt-fázisos hiba
   jellemzően a **nem változott** oldalon nyílik. A II.5 hash-alapú kihagyása más dolog —
   ott a kihagyás feltétele bizonyított változatlanság, nem heurisztika.
2. **A `BR1` friss-alap ellenőrzés elhagyása.** Az adja a `PASS` érvényességét; nélküle a
   `06` és a `09` összevetése értelmetlenné válik.
3. **A `Végrehajthatósági leltár` opcionálissá tétele.** A `05` minőségellenőrzése kimondja: e
   nélkül a PASS nem fogadható el, mert épp azok a hibák maradnának rejtve, amiket a lefedettségi
   mátrix szerkezetileg nem lát.
