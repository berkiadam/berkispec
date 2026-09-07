# „A quick-flow legyen újra rövid" — végrehajtási terv (eltávolító kör)

> **Ez a dokumentum önhordó.** Üres kontextusban, `/clear` után is végrehajtható: az 1. szakasz
> megadja a repó-orientációt, a 2. a problémát és a **mérést**, a 3. a lezárt döntéseket, a 4. a
> tételes vágásokat, az 5. az **anti-listát** (amihez NEM nyúlunk), a 6. a dokumentációt, a 7. a
> kapukat, a 8. a végrehajtási sorrendet.
> **Semmit nem kell kikövetkeztetni** — ha valami mégis hiányzik, az a terv hibája; írd bele.
>
> **Státusz:** **TERV** (2026-09-07) — a 3. szakasz döntései a felhasználóval **lezárva**,
> a végrehajtás még nem kezdődött el.
>
> **⚠ Ez egy ELTÁVOLÍTÓ kör.** Minden más `inprove-list` szabályt **adott**; ez **elvesz**. A
> kör legnagyobb kockázata ezért nem a hiányos végrehajtás, hanem a **túlvágás** — ezért van
> 5. szakasz (anti-lista) és 7. szakaszban **regresszió-kapu**, ami azonosító-szinten
> ellenőrzi, hogy csak az eshetett ki, amit a `D3` engedélyez.
>
> **Előzmény és sorrend-függés:**
> - `prompts/inprove-list10.md` (`QF1`–`QF20`, `QT1`–`QT6`) — **elkészült** (`3132cd9`). **Ez a
>   kör okozta a felhízást**: húsz tételt tett a quick-flow-ba, és a hosszt egyetlen döntés sem
>   mérte. Ez a terv nem vonja vissza a `list10` szándékát, csak az **árát** csökkenti.
> - `prompts/inprove-list11.md` (teszt-leltár + központi futtatás) — **megírva, nem
>   végrehajtva**. **Interakció:** a `list11` `LD10` tétele ~4 sort **ad** a quick-flow-hoz
>   (leltár-drift jelzés). Lásd `QS7`.

---

## 0. Hogyan használd ezt a dokumentumot

1. **Olvasd el a 2. szakaszt** — az adja a mérést, ami nélkül a vágások önkényesnek tűnnek, és
   az adja a **kiinduló számot**, amihez a célszámot mérjük.
2. **A 3. szakasz döntéseit ne nyisd újra** (2026-09-07). Ha valamelyik tarthatatlan, **írd a
   9. szakaszba, mi lett helyette és miért**.
3. **A 4. szakasz előtt olvasd el az 5.-et.** Az anti-lista mondja meg, hol áll meg a vágás.
4. **A 8. szakasz sorrendjében haladj**, és minden teendő után **pipálj ebben a fájlban**.
5. **Kétnyelvű repó:** minden szerkesztés **hu ÉS en párban**, a sorszintű igazodást megtartva
   (ma **344/344 sor**, a címsorok ugyanazokon a sorokon).
6. **Nincs CI és nincs pre-commit hook** — a kapukat (7. szakasz) **kézzel futtasd le**.

---

## 1. Orientáció

### 1.1 A rendszer — annyi, amennyi ehhez a körhöz kell

A `berkispec` egy spec-driven development keretrendszer promptokból. A repó a **forrás**; egy
célprojektbe az `install.sh` / `install.ps1` → `prompts/scripts/install-helper.py` telepíti.
A telepítő **build-time** oldja fel az `<!-- INCLUDE:shared/… -->` /
`<!-- INCLUDE:lang/… -->` markereket (`install-helper.py:258`–`:288`, rekurzívan) és a
`<sec:…>` / `<field:…>` / `<status:…>` tokeneket, majd `bs-<stem>/SKILL.md` alá írja.

**🔴 Ebből következik a kör legfontosabb ténye:** a promptot nem a forrásfájl hossza terheli,
hanem a **telepített** méret — az `INCLUDE` blokkok **beépülnek**. A keretben **nincs lusta
betöltés**: egy „függelék" ugyanannyiba kerül, mint a törzs. **A rövidítés egyetlen valódi
eszköze a törlés.**

Amit ez a terv érint:

| útvonal | mit |
|---|---|
| `prompts/skills-{hu,en}/quick-flow.md` | a vágások helye (344 sor forrás → cél ~300) |
| `prompts/meta-improve-prompts.md` | új tervezési elv: a méret korlát (`7/q`, 6. szakasz) |
| `README-HU.md` · `README.md` | az „5. Egyszerűsített flow" ágens-táblája, ha a `QS2` átírja |

**Amit NEM érint:** a `prompts/agents-{hu,en}/` (a `called_by` listák változatlanok — `D2`), a
`prompts/lang/{hu,en}/quick-flow.md` (a három horgony marad), a `status-keys.json` (**új kulcs
nem kell** — ez a kör csak töröl és tömörít), és a `prompts/shared-{hu,en}/` blokkok maguk
(csak a quick-flow-ból vett **hivatkozás** szűnik meg, a blokk marad a többi fogyasztónak).

### 1.2 A két nyelvi tengely (LG2/LG5)

- **prompt-nyelv:** `prompts/skills-hu/` vs. `prompts/skills-en/`. **Minden szerkesztés
  mindkét fán megy, párban**, és a **sorszintű igazodás** megmarad (a vágás mindkét fájlból
  ugyanannyi sort vesz el).
- **projekt-nyelv:** a `prompts/lang/{hu,en}/` blokkok és a `status-keys.json` tokenjei. Ez a
  kör **nem** vezet be új tokent, és **nem** töröl meglévőt (a `<field:…>` hivatkozások a
  megmaradó mondatokban változatlanul állnak).
- **Nyelvfüggetlen literálok, amiket a tömörítés NEM olvaszthat össze magyar/angol szóval:**
  `[local]` / `[remote]` (EV8), a `QF`/`QT` azonosítók, a `TL-NNN` (ha a `list11` már lefutott).

### 1.3 Kötelező kézi kapuk — plusz egy ÚJ

```bash
python3 prompts/scripts/lang-parity-check.py            # szerkezeti paritás  → 0
python3 prompts/scripts/lang-parity-check.py --strict   # fájlhalmaz-paritás → 0
python3 prompts/scripts/sync-gemini-agents.py --check   # agent.json tükrök  → 0
```
- Agent-promptot ez a kör **nem** módosít (`D2`), tehát a `sync-gemini-agents.py`-t **írás
  módban nem kell** futtatni — a `--check`-et igen.
- **ÚJ: méret-kapu** (`D1`). A build után:
  ```bash
  python3 prompts/scripts/install-helper.py claude . <tmp>/hu hu hu   # → Success
  python3 prompts/scripts/install-helper.py claude . <tmp>/en en en   # → Success
  wc -l <tmp>/{hu,en}/.claude/skills/bs-quick-flow/SKILL.md            # → mindkettő ≤ 420
  ```
- **ÚJ: regresszió-kapu** (a túlvágás ellen) — 7. szakasz.

### 1.4 A hivatkozott azonosítók — hol nézd meg őket

| hol | mit ad |
|---|---|
| `prompts/inprove-list10.md` | **ennek a körnek a párja**: a `QF1`–`QF20` / `QT1`–`QT6` tételek eredeti indoklása. Vágás előtt **olvasd el az érintett tételt** |
| `prompts/meta-improve-prompts.md` „Tervezési elvek" + shared-tábla | melyik shared blokk mit rögzít és ki emeli be (`7/b`–`7/o`) |
| `README-HU.md` „5. Egyszerűsített flow" | a felhasználónak szánt leírás (5.1 ábra … 5.6 példa) |

Konkrétan hivatkozott azonosítók: `RP1` (útvonal-formátum, a flow **egyetlen kötelező
kapuja**), `AV1`/`QF14` (artifact-voice), `KX2`/`QF13` (dereferencing), `GC1`/`QF15`
(conventions-change), `IM1`/`QF9` (megállási szabályok ellenpárja), `BQ2` (ciklusszám),
`QT1`–`QT6` (teszt-keményítés), `QF18` (agent-kontraktus), `TD5` (a kalibrációs mintát a
sűrűségéért másold), `7/h` (a padló önmagában nem termel részletet), `7/e` (egy fogalom, egy
útvonal-alak).

---

## 2. A probléma és a mérés

### 2.1 A mért állapot (2026-09-07)

```
telepített bs-quick-flow:   502 sor · 66 221 bájt · ~22 000 token
forrás:                     344 sor (hu) / 344 (en)
beemelt shared+lang:       ~141 sor  (a 344-hez ADÓDIK)
a list10 ELŐTT:            ~265 telepített sor (210 forrás + context-check + output-language)
                            → +90% egyetlen kör alatt
```

A többi telepített skill mellett:

| skill | telepített sor |
|---|---|
| `bs-cycle-status` | 105 |
| `bs-brainstorm` | 311 |
| `bs-manual-test-plan` | 445 |
| **`bs-quick-flow`** | **502** |
| `bs-06-implement` | 538 |
| `bs-02-write-spec` | 655 |
| `bs-07-validate` | 1116 |

**A törés:** a „kis feladatok olcsó útja" ma a nagy flow **spec-fázisának 77%-a**, és nagyobb,
mint a `06-implement`. Egy 3-4 lépéses feladatnál az **instrukció** többe kerül, mint a munka.

### 2.2 Hol van a sor — a forrás szakasz-súlyai

| blokk | sor | a kör álláspontja |
|---|---|---|
| `## 3. A Háromfázisú Munkafolyamat` | **125** (36%) | ez a flow **maga** — nem vágjuk (5. szakasz) |
| beemelt shared blokkok | **141** | ebből **28** vágható (`QS1`) |
| `## 4. Felhasznált specialista ágensek` | 35 | **a legrosszabb ár/érték** → `QS2` |
| `## 1. Alapelvek és könyvtárszerkezet` | 32 | `QS3` + `QS4` |
| frontmatter + fejléc | 29 | kötelező |
| `## 5. Megállási szabályok` (IM1) | 25 | **nem vágjuk** (5. szakasz) |
| `## 2. Új fejlesztési ciklus indítása` | 23 | nem vágjuk |
| `## Mikor ezt a flow-t…` | 21 | nem vágjuk |
| `Gyors lépéssor` + `## 6.` + `## 7.` | 33 | `QS5` óvatosan |

### 2.3 A mérés, ami eddig hiányzott

A `list10` húsz tételét mind indoklás vezette — **de a hosszt egyetlen döntés sem mérte**, és a
`meta-improve-prompts.md`-ben sincs olyan elv, ami a méretet korlátnak tekintené. Ezért a kör
nem csak vág, hanem **rögzíti a korlátot** (`D6` → `7/q`): különben a következő keményítő kör
észrevétlenül visszahizlalja.

---

## 3. Lezárt döntések (a felhasználóval egyeztetve, 2026-09-07 — ne nyisd újra)

- **D1 — Célszám: a telepített `bs-quick-flow` ≤ 420 sor, mindkét nyelven.** A mérés a
  `wc -l` a build kimenetén (1.3). A várható eredmény ~420-425 sor a mai 502-ből (−16%).
  **Teszt-szabály (`QT1`–`QT6`), megállási szabály (`QF9`/IM1), fázis-kapu (`QF2`/`QF4`) és
  kapu-hívás (`QF11`/RP1) NEM esik el.**
- **D2 — A három opcionális ágens MARAD, tömörítve.** A `## 4.` szekció ~10 sorra megy össze:
  egy 3 soros tábla (ágens / mikor érdemes / mit mondj a hiányzó bemenet helyett), és a
  részletes `QF18` helyettesítés-tábla (7 sor + magyarázat) **egy-egy fél sorba** sűrűsödik.
  **Az `analyzer` is marad.** Az agent-promptok `called_by` listája **változatlan** — tehát
  nincs agent-frontmatter változás, nincs `sync-gemini-agents.py` írás mód.
- **D3 — Az `artifact-voice.md` INCLUDE kivezet a quick-flow-ból (AV1 / `QF14`).**
  **Ez a kör EGYETLEN tényleges szabály-kivezetése — nem „veszteség nélküli" tömörítés.**
  Indok: a nagy flow-ban az `artifact-voice` **kemény padló, mert az `05` méri**; a
  quick-flow-ban kapu nélküli próza, a `05` pedig itt nem fut. A blokk **megmarad a keretben**
  (`02`, `03a`, `03b`, `04` továbbra is hordozza) — csak ebből a flow-ból kerül ki a
  hivatkozás. **A frontmatter `shared:` listájából is kivezet.**
- **D4 — A másik négy INCLUDE MARAD**, és a végrehajtó **nem** „optimalizálhatja" tovább:
  - `path-format.md` (RP1) — ez hordozza a flow **egyetlen kötelező kapuját**
    (`analyze-gate-check.py --paths-only`);
  - `dereferencing.md` (KX2) — itt a `spec.md` az **egyetlen** végrehajtási igazság, tehát a
    `list10` `QF13` szerint **szigorúbban** kell, mint a nagy flow-ban;
  - `conventions-change.md` (GC1) — a flow **tipikus feladata** épp konfiguráció / port /
    teszt-parancs, vagyis pont az, amit a kapuk a `conventions.md`-ből olvasnak;
  - `context-check.md` — fázis-eleji kontextus-ellenőrzés, a keretben 16/16 fázis-skill és a
    `cycle-status`/`manual-test-plan`/`quick-flow` hordozza.
- **D5 — Az IM1 szekció és a happy-path lista nem vágható agresszíven.** A
  `## 5. Megállási szabályok` (25 sor) és a `Gyors lépéssor` (14 sor) **gyenge/olcsó modellen a
  leggyakoribb hibamód** ellen dolgozik (taskonkénti visszakérdezés, illetve a fázis-sorrend
  elvesztése). A `QS5` legfeljebb a **háromszor elmondott** mondatokat vonja össze.
- **D6 — A méret ettől a körtől korlát.** Új tervezési elv a `meta-improve-prompts.md`-ben
  (`7/q`), a mérés módjával és a `≤ 420` számmal. **Kapu-scriptet nem írunk** hozzá (egy `wc -l`
  nem ér egy új scriptet) — a kapu **kézi**, a 7. szakasz sorolja.

---

## 4. A vágások tételesen

> **A tételek a vágás SZÁNDÉKÁT és a nyereséget adják meg; a végleges prózát a végrehajtó írja.**
> Minden tétel előtt **olvasd el a `list10` megfelelő tételét** (`QF`/`QT` azonosító szerint) —
> ha a vágás után a szabály **szándéka** nem olvasható ki a maradékból, akkor túl sokat vettél el.

- [ ] **QS1 — `artifact-voice.md` INCLUDE kivezetése** (`D3`, AV1 / `QF14`). Törlendő: a
      `<!-- INCLUDE:shared/artifact-voice.md -->` marker, a körülötte lévő `---` szeparátor, és
      a frontmatter `shared:` listájából az `"shared/artifact-voice.md"` sor. **Nyereség: −28
      telepített sor + 3 forrás-sor.** _(A `list10` `QF14` indoklása: „a nagy flow-ban ez kemény
      padló (az `05` méri), itt kapu nélkül is hordozható szabály" — most épp ezt a
      „kapu nélkül is" részt mérlegeljük át a méret javára.)_
      **Pótlás:** a `## 1. Alapelvek` egy **fél mondatot** kap arról, hogy az artefaktum az
      implementálónak szól, nem az ágensnek — a 28 soros blokk helyett.
- [ ] **QS2 — A `## 4. Felhasznált specialista ágensek` szekció ~35 → ~10 sor** (`D2`).
      Marad: a bevezető mondat („opcionálisan, kis feladatnál hagyd ki"), **egy** tábla három
      sorral (ágens · mikor érdemes · **mit mondj a hiányzó bemenet helyett**), és **egy** sor a
      „mit nem használ" listáról (fixerek, `doc-sync-planner`) → túlnövés-jelzés.
      Kivezet: a részletes `QF18` helyettesítés-tábla (7 sor), a „Gyengébb/olcsóbb modellel"
      idézet-blokk (beolvasztva a bevezető mondatba), és a `plan-fixer`/`doc-sync-planner`
      külön bekezdései. **A `QF18` azonosító a fájlban MARAD** (a tömörített tábla fejlécében),
      hogy a regresszió-kapu (7. szakasz) átengedje, és a `list10` indoklása visszakereshető
      legyen. **Nyereség: −25 sor.**
- [ ] **QS3 — A három INCLUDE utáni „leképezés" jegyzet 1-1 sorra.** Ma a `path-format`,
      `dereferencing` és `conventions-change` blokk után 4-6 soros `>` idézet-blokk magyarázza,
      hogyan képződik le a szabály erre a flow-ra. A **szándék** egy sorban is elmondható
      (`RP1`: „ez a flow egyetlen kötelező kapuja, a `spec.md`+`tasks.md` párra fut"; `KX2`:
      „itt a `spec.md` az egyetlen igazság, tehát a feloldás szigorúbb"; `GC1`: „a `plan`/`07`
      helyét a `spec.md` technikai vázlata és a 3. fázis tesztje veszi át").
      **Nyereség: −10 sor.**
- [ ] **QS4 — A `## 1. Alapelvek és könyvtárszerkezet` prózája.** Az öt pont közül a
      „Dokumentumvezérelt fejlesztés", a „README.md karbantartása" és a „Dokumentáció nyelve"
      pont **hosszabb, mint a szabály**. Egy-egy mondatra rövidítendő; a `QS1` fél mondata ide
      kerül. **A „Két artefaktum, két státusz" pont (QF2) változatlan.**
      **Nyereség: −10 sor.**
- [ ] **QS5 — A `Gyors lépéssor` ↔ `## 3.` átfedés csökkentése — ÓVATOSAN** (`D5`). A
      happy-path lista 6 pontja **marad** (ezt követi egy gyenge modell); csak azok a mondatok
      vonhatók össze, amelyek **szó szerint** megismétlődnek a `## 3.` fázis-leírásában
      (jellemzően a `⛔ ÁLLJ MEG` és az RP1-kapu megfogalmazása). **Nyereség: max −8 sor.**
      Ha a lista bármelyik pontja **elveszti** a fázis nevét, a státusz-értéket vagy a `⛔`-t,
      **állj le és ne vágd** — a lista értéke épp az önmagában olvashatóság.
- [ ] **QS6 — Sorszintű igazodás és a mérés.** A vágás után a hu és az en példány
      **ugyanannyi sor** legyen, a címsorok ugyanazokon a sorokon (ma 344/344). A `QS1`–`QS5`
      összesített várható nyeresége **−53 forrás-sor és −28 beemelt sor**, azaz
      **502 → ~421 telepített sor**. Ha a build után **420 fölött** vagy: a `QS3`/`QS4`
      tömörítést húzd meg jobban — **ne** a `## 3.`, `## 5.` vagy a `QT`-csomag rovására
      (5. szakasz).
- [ ] **QS7 — Sorrend-függés a `list11`-hez.** Ha a `prompts/inprove-list11.md` **már
      lefutott**, a quick-flow-ban ott van az `LD10` leltár-drift jelzés (~4 sor), tehát a
      kiinduló méret nem 502, hanem ~506 — a **célszám (`≤ 420`) akkor is érvényes**, csak
      ~4 sorral több a vágandó. Ha a `list11` **még nem futott**, a `list11` `LD10` tételéhez
      **írd be**, hogy a `7/q` méret-korlát él, tehát a 4 sort a lehető legtömörebben adja.
      **A két kör bármelyik sorrendben végrehajtható**, más interakció nincs.

---

## 5. Anti-lista — amihez NEM nyúlunk (és miért)

**Ez a szakasz a kör legfontosabb védőhálója.** Egy eltávolító körben a modell hajlamos a
„még ez is kivehető" spirálra; az alábbiak **nem** vághatók, és ha a célszám csak ezek árán
teljesülne, akkor a **célszám** engedjen, ne a szabály:

| NEM vágható | sor | miért |
|---|---|---|
| `## 3. A Háromfázisú Munkafolyamat` | 125 | ez a flow maga: a három fázis, a státusz-kapuk (`QF2`/`QF4`), a technikai vázlat (a `plan.md` pótléka) és a `QT`-csomag |
| A `QT1`–`QT6` hat pontja + a **kalibrációs minta** | ~25 | a `7/h` elv: a padló önmagában nem termel részletet, a **kitöltött minta** hordozza a sűrűséget (`TD5`). A minta törlése kigyomlálná a `QT3`-at |
| `## 5. Megállási szabályok` + az IM1 ellenpár | 25 | `D5`: a taskonkénti visszakérdezés a leggyakoribb hibamód gyenge modellen |
| `path-format` · `dereferencing` · `conventions-change` · `context-check` INCLUDE | 113 | `D4`: az RP1 a flow egyetlen kapuja; a KX2 itt szigorúbb; a GC1 a flow tipikus feladata |
| `## 2.` git-konvenció (`QF1`) és `BQ2` ciklusszám (`QF5`) | 23 | e kettő nélkül a flow **más ágnévvel és ütköző ciklusszámmal** dolgozik, mint a nagy flow — ez volt a `list10` `2.2/(b)` törése |
| `## Mikor ezt a flow-t…` + a túlnövés-tripwire | 21 | e nélkül a flow **átvenné** a nagy feladatokat is, ami a legdrágább hibamód |
| A `QF6` roadmap és `QF7` drift-jelzés | ~10 | a `list10` `D5` döntése: a flow-határ mind a négy rése bekerül. Ezek a **projekt** konzisztenciáját védik, nem a ciklust |

---

## 6. Dokumentáció

- [ ] **6.1 — `prompts/meta-improve-prompts.md`: új tervezési elv `7/q`** (`D6`) —
      **„a második út mérete korlát, nem következmény"**. Tartalma: a 2.1 mérés (502 sor,
      +90% egy kör alatt, a `02` fázis 77%-a), a `≤ 420` telepített sor korlát, a mérés módja
      (`wc -l` a buildben, mindkét nyelven), és a **„Prompt-módosításnál…"** kérdés, amit a
      keret minden elve visel: *„ha ebbe a flow-ba szabályt teszel, mi esik ki helyette — és a
      build után is 420 alatt van?"*. Hivatkozás a `7/o`-ra (a másik út is elcsúszhat) és erre
      a tervre.
      _(A `7/q` a `bs-quick-flow` bekezdését is kiegészíti egy fél sorral: „mérete korlátos".)_
- [ ] **6.2 — `README-HU.md` + `README.md` — csak ha a `QS2` átírja az ágens-táblát.** A
      README-k „5. Egyszerűsített flow" szekciójában van egy **ágens-tábla** (5.4), amely a
      három subagentet és a helyettesítéseiket sorolja. Ha a `QS2` a skillben tömörít, a
      README 5.4 táblája **ne mondjon többet, mint a skill** — a tartalmat keresd, ne a
      sorszámot. **A két README-t párban** szerkeszd: ezt **egyetlen gépi kapu sem méri**
      (a `lang-parity-check.py` hatóköre `BASES = ("skills","agents","shared")` + `lang`,
      `:116`–`:117` — a gyökér-README-ket nem látja).
- [ ] **6.3 — `prompts/inprove-list10.md`: NEM írjuk át.** A `list*` fájlok a **múltat
      rögzítik**. Ha a `QS1` kivezeti a `QF14`-et, azt **itt**, a `list12` 9. szakaszában kell
      rögzíteni — a `list10` `QF14` pipája marad, mert az akkor valóban elkészült.

---

## 7. Kapuk (kézzel, commit előtt)

- [ ] `python3 prompts/scripts/lang-parity-check.py` → 0
- [ ] `python3 prompts/scripts/lang-parity-check.py --strict` → 0
- [ ] `python3 prompts/scripts/sync-gemini-agents.py --check` → 0 _(agent-prompt nem változik — `D2`)_
- [ ] **Build hu + en** → `Success`, és a telepített `SKILL.md`-ben **nulla** feloldatlan
      `INCLUDE:` marker, **nulla** `<sec:|<field:|<status:` token.
- [ ] **MÉRET-KAPU (`D1`):** `wc -l <tmp>/{hu,en}/.claude/skills/bs-quick-flow/SKILL.md`
      → **mindkettő ≤ 420**. Ha nem: `QS3`/`QS4` tovább, **nem** az 5. szakasz rovására.
- [ ] **REGRESSZIÓ-KAPU / azonosítók (a túlvágás ellen).** A quick-flow-ban ma **15**
      azonosító él (mindkét nyelven): `QF1 QF2 QF4 QF6 QF7 QF8 QF11 QF16 QF18 QT1 QT2 QT3 QT4
      QT5 QT6`. Vágás után **mind a 15-nek meg kell lennie**:
      ```bash
      for L in hu en; do
        grep -oE '\bQF-A[0-9]+|\bQF[0-9]+|\bQT[0-9]+' prompts/skills-$L/quick-flow.md \
          | sort -u > /tmp/after-$L.txt
        git show HEAD:prompts/skills-$L/quick-flow.md \
          | grep -oE '\bQF-A[0-9]+|\bQF[0-9]+|\bQT[0-9]+' | sort -u > /tmp/before-$L.txt
        diff /tmp/before-$L.txt /tmp/after-$L.txt && echo "$L: azonosító-halmaz VÁLTOZATLAN"
      done
      ```
      **Bármelyik azonosító eltűnése = túlvágás**, kivéve ha a 9. szakaszban indokolva van.
- [ ] **REGRESSZIÓ-KAPU / shared INCLUDE-ok.** Ma **5** shared blokk: `context-check`,
      `path-format`, `artifact-voice`, `dereferencing`, `conventions-change`. Vágás után
      **pontosan 4**, és a kiesett **pontosan az `artifact-voice`** (`D3`). Ellenőrzés a
      frontmatter `shared:` listáján **és** a törzs markerein, **mindkét nyelven**.
- [ ] **Emberi review (nem gépi kapu):** a hu/en pár átolvasása — a tömörítés **jelentést** is
      elvehet, amit a paritás-kapu nem lát. Külön nézd meg, hogy a `QS3` egysoros leképezései
      és a `QS2` tömörített ágens-táblája **önmagában érthető-e** annak, aki a `list10`-et nem
      olvasta.

---

## 8. Végrehajtási sorrend

1. **Olvasd el az 5. szakaszt** (anti-lista) — ez a kör kockázata a túlvágás.
2. **`QS1`** — az `artifact-voice` kivezetése (marker + `---` + frontmatter `shared:` sor),
   és a pótló fél mondat a `## 1.`-be. Ez a legnagyobb egyszeri nyereség (−28).
3. **`QS2`** — a `## 4.` ágens-szekció tömörítése (−25). A `QF18` azonosító maradjon a fájlban.
4. **`QS3` + `QS4`** — a három leképezés-jegyzet és a `## 1.` prózája (−20).
5. **`QS5`** — a happy-path átfedés, óvatosan (max −8).
6. **`QS6`** — sorszintű igazodás helyreállítása, majd **build + méret-kapu**. Ha 420 fölött
   van, vissza a 4. lépéshez.
7. **`QS7`** — a `list11` sorrend-függés lezárása (vagy a `list11` `LD10` tételébe a
   méret-megjegyzés beírása).
8. **6. szakasz** — a `7/q` elv és (ha kell) a két README.
9. **7. szakasz** — kapuk, majd egy commit. A commit-üzenetben **mondd ki, hogy ez eltávolító
   kör**, és sorold fel, mi vezetett ki (`QF14`/AV1) — a paritás-kapu ezt nem látja.

---

## 9. A végrehajtás tapasztalatai és a tervtől való eltérések

_(Kitöltendő a végrehajtás közben. Ide kerül a `QF14`/AV1 kivezetésének rögzítése, a tényleges
telepített sorszám, és minden pont, ahol a terv tévedett vagy hiányos volt.)_
