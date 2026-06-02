---
phase: 04
name: write-tasks
prerequisites:
  - "specs/cycle-NN-<name>/plan.md státusz: Task írásra kész"
output:
  - "specs/cycle-NN-<name>/tasks.md státusz: Implementálásra kész"
prev: 03-write-plan
next: 05-analyze
subagents: []
---

# 04 — Tasks írás

Spec driven development-ben fejlesztünk szoftvert. A fejlesztés ciklusokra van bontva. Minden ciklus egy önállóan lefejleszthető, önállóan tesztelhető részegysége a teljes implementációnak.

Ez a fejlesztési folyamat **4-es fázisa (a 0–8 fázisokból)**:
0. projekt inicializálás (setup)
1. ciklusok kezelése (setup)
2. spec
3. plan
4. **tasks** ← most itt vagyunk
5. analyze
6. implement
7. validate
8. review & merge

---

## Előfeltétel

1. **`conventions.md` létezés-ellenőrzés:** olvasd be a projekt gyökerében a `conventions.md`-t. Ha nem létezik, STOP — térjenek vissza a `00` fázishoz.
2. Olvasd be a `plan.md` státuszát. **Ha a státusz nem `Task írásra kész`, ne kezdj tasks listát írni.** Jelezd a felhasználónak, hogy a plan még nem zárult le, és térjenek vissza a `03` plan fázishoz.
3. **Nyitott kérdések lezártsága:** a `Task írásra kész` státusz implikálja, de explicit ellenőrizd — a `spec-questions.md` és `plan-questions.md` egyikében sincs `[ ]` nyitott kérdés. Ha van, a plan nem zárult le valójában: jelezd, és térjenek vissza a `03` (vagy `02`) fázishoz.

---

## Folytatás megszakított futás után

Ha a tasks.md írása félbeszakadt és új sessionban folytatódik:

1. Olvasd be a `tasks.md` aktuális állapotát.
2. Keresd meg az első hiányos vagy bizonytalan részt: van-e csoport záró `[CHECK]` nélkül, van-e `[RED]` task párja nélkül, van-e a plan-ből lefedetlen módosítás?
3. Ha a tasks lista részben megvan és csak befejezés hiányzik, folytasd onnan ahol abbahagyták — ne kezdd újra.
4. Ha a lista koherensnek tűnik de a státusz még `Piszkozat`, futtasd le a minőségellenőrzést, és zárj le ha átment.

---

## Feladatod

**Ha már létezik `tasks.md` a `specs/cycle-NN-<cycle-name>/` mappában:** olvasd be, és futtasd le rajta a minőségellenőrzést (ld. lent). Ha hiányosságot találsz — hiányzó task, túl nagy task, hiányzó `[CHECK]`, plan-lefedettségi rés — javítsd, és csak ezután zárd le.

**Ha még nem létezik `tasks.md`:** hozd létre a `specs/cycle-NN-<cycle-name>/` mappában az alábbi struktúra szerint.

**Ne implementálj semmit.** A tasks lista az implement fázis bemenete — most csak a lépéseket definiáljuk.

**Ne vegyél fel taskot, amely nincs a plan `Tervezett módosítások` szekciójában.** A tasks lista a plan pontos lebontása — nem bővíti, nem szűkíti a scope-ot.

**Ha egy taskot nem lehet konkrétan leírni** (nincs egyértelmű érintett fájl, nincs egyértelmű elvégzési kritérium), az a plan hiányosságát jelzi. Állj meg, jelezd pontosan mi az alulspecifikált lépés, és kérd a felhasználót, hogy egészítse ki a `plan.md`-t. Egyben állítsd a `plan.md` státuszát vissza `Piszkozat`-ra — a plan nem maradhat `Task írásra kész` státuszban, ha hiányosságot találtál. A plan frissítése és `Task írásra kész` státusz visszaállítása után folytatható a tasks lista.

---

## Kontextus betöltési szabályok

- Csak a `plan.md`-t olvasd be. A spec és a forrásfájlok a plan fázisban már fel lettek dolgozva — ne olvasd be újra.
- Ha egy task leírásához konkrét fájlnévre vagy path-ra van szükség és az nem szerepel a plan-ben, csak akkor olvasd be az érintett fájlt.

---

## Prerequisite dokumentumok meghatározása

A tasks.md fejlécébe kerülő Prerequisite lista az implementáló agent teljes kontextusa — ezeket olvassa be a végrehajtás előtt.

Mindig benne van:
- `specs/<cycle-name>/plan.md`

Benne van, ha a plan `Schema Artifaktumok` táblájában szerepel `Reviewed` státusszal:
- OpenAPI YAML, Redis key map, DB schema, Avro séma, stb.

Soha nem kerül bele:
- `research.md` vagy más exploratív fázismelléktermék
- `Review Required` státuszú artifact (ha ilyen van, a plan nincs lezárva)

---

## Task formátum

```md
- [ ] T001 [RED]   <tesztfájl létrehozása / teszt megírása> — `path/to/test.ts`
- [ ] T002 [GREEN] <implementáció> — `path/to/file.ts`
- [ ] T003         <nem TDD task> — `path/to/file`  ⟂ T007
- [ ] T004 [CHECK] Futtasd a teszteket / typecheck-et
```

- A sorszám (`T001`, `T002`, ...) szekvenciális, a végrehajtási sorrend alapján.
- A leírás egysoros, konkrét, cselekvő igével kezdődik (pl. *Hozd létre*, *Bővítsd*, *Adj hozzá*, *Futtasd*).
- A fájl path kötelező, ha a task fájlt érint. Ha a task parancs futtatás, a fájl path elhagyható.
- **TDD jelölés:** teszt-írási taskot `[RED]`, a hozzá tartozó implementációs taskot `[GREEN]` prefixszel jelöld. A `[RED]` task mindig megelőzi a párját. Nem TDD task esetén nincs prefix.
- **Ellenőrzési task:** `[CHECK]` prefix, minden logikai csoport végén kötelező — konkrét parancsot tartalmaz a plan `Ellenőrzési stratégia` szekciójából (pl. `npm test`, `npm run typecheck`). Fájl path elhagyható.
- **Párhuzamosítható task jelölése:** ha egy task egy másikkal egyszerre elvégezhető (köztük nincs függőség), jelöld `⟂ Tkkk` suffixszel. Csak akkor jelöld, ha a párhuzamosítás valóban időt takarít meg.
  - **Példa:** `- [ ] T012 [GREEN] Implementáld a foo service-t — `src/foo.ts` ⟂ T013` — azt jelenti, hogy T012 és T013 egyszerre szerkeszthető, mert **nem ugyanazt a fájlt érintik** és nincs köztük függőség. Ha ugyanazt a fájlt érintenék, NEM jelölhető párhuzamosnak.
- **Sorszámozási konvenciók — `T`, `TREG`, `TLAST`:**
  - **`Tnnn`** — normál, szekvenciálisan számozott implementációs task (`T001`, `T002`, …) a logikai csoportokban.
  - **`TREGn`** — regressziós felülvizsgálati task (`TREG1`, `TREG2`, …) a kötelező „Regressziós tesztek felülvizsgálata" záró csoportban. Sorrendben, `[CHECK]` nélkül. Csak olyan fájlra, amely a plan `Regressziós érintettség` táblázatában van, de a `Tervezett módosítások`-ban nincs.
  - **`TLASTn`** — a kötelező „Dokumentáció" záró csoport taskjai (`TLAST1`, `TLAST2`, …), a lista legvégén. Ezek futnak utoljára.
  - A számozás minden prefixen belül 1-től indul és növekvő.

---

## Leírás minőségi elvárások

**A task leírása navigációs pont, nem önálló specifikáció.** Az implementáló agent a plan-t olvassa be munkavégzés előtt — a task feladata az, hogy egyértelműen megmutassa, a plan melyik szekciójára vonatkozik a változtatás. A részletes logikát, interfészeket, hibakezelést a plan tartalmazza.

A leírásnak tartalmaznia kell:
- **Mit csinálni** — cselekvő ige + érintett egység neve (függvény, osztály, fájl)
- **Melyik fájl** — a path kötelező, ha a task fájlt érint
- **Plan szekció hivatkozás** — ha a task neve önmagában nem egyértelmű, add meg a plan érintett szekcióját: `— plan.md § <szekció>`

Részletet **csak akkor** adj a task leírásába, ha a plan nem tartalmazza:
- Parancs futtatásoknál: a tényleges shell parancs (pl. `openssl genrsa -out key.pem 2048`)
- Külső erőforrás hivatkozásnál: ha a task teszteléséhez vagy futtatásához külső erőforrás kell (tanúsítvány, API kulcs, mock adat, speciális konfiguráció), hivatkozz a `plan.md` vagy `spec.md` azon szekciójára, ahol ez megtalálható (pl. `— plan.md § Konfiguráció és build változások`). Az implementáló agentnek ne kelljen keresgélnie.

**Tömörítési elv:** amit egy fejlesztő egy mondatban el tud mondani kollégájának, az elég. A részlet a plan-ban van — ne másold át.

| Túl bőbeszédű | Jó |
|---|---|
| `Implementáld: async callLegacyVerify(legacyLoginBaseUrl, jweToken, logger): Promise<{userId, sessionId, regId}> — GET <url>/verify (Authorization: Bearer), nem 200 esetén throw new HttpError(403, 'Legacy token verification failed', 'TMP_031')` | `Implementáld a callLegacyVerify service-t (GET /verify, TMP_031 hibakezeléssel)` |
| `Írd át a hibatesztek { error: "..." } expected response-ait { correlationId: <string>, messages: [{ code: "TMP_XXX", params: { description: "..." } }] } formátumra` | `Frissítsd a hibateszt expected response-okat ErrorMessageResponse formátumra` |

**Hosszúsági korlát:** ha a leírás megközelíti a 100 karaktert, valószínűleg plan-részletet másoltál bele — elég a hivatkozás.

---

## Tasks struktúra

```md
# Cycle NN: <cím> — Tasks

**Státusz:** `Piszkozat` | `Implementálásra kész`

## Prerequisite dokumentumok

_Az implementáló agent ezeket olvassa be a végrehajtás előtt._

- `specs/<cycle-name>/plan.md`
- _(további Reviewed artifaktok a plan Schema Artifaktumok táblájából)_

> `[RED]` = teszt írása (bukni fog) · `[GREEN]` = implementáció (teszt zöldítése) · `[CHECK]` = ellenőrzés futtatása

## <Logikai csoport 1 — a plan végrehajtási sorrendje alapján>

- [ ] T001 [RED]   ...
- [ ] T002 [GREEN] ...
- [ ] T003 [CHECK] Futtasd: `npm test -- path/to/test.ts`

## <Logikai csoport 2>

- [ ] T004 ...
- [ ] T005 [CHECK] Futtasd: `npm run typecheck`
```

A csoportok a plan végrehajtási sorrendjének szakaszait tükrözik. Minden csoport önállóan elvégezhető és ellenőrizhető. Minden csoportnak van legalább egy `[CHECK]` taskja a végén.

**Kötelező záró csoportok:** a tasks lista utolsó két csoportja mindig a következő, ebben a sorrendben:

**1. Regressziós tesztek felülvizsgálata** — kizárólag azokhoz a fájlokhoz, amelyek **szerepelnek** a plan `Regressziós érintettség` táblázatában, de **nem szerepelnek** a plan `Tervezett módosítások` szekciójában. Ha egy fájl mindkét helyen szerepel, az mindig T task — nem TREG. Csak sima taskként (`[ ] TREG...`) vedd fel `[CHECK]` nélkül. Ha nem igényel módosítást, a task jelzésértékű („Ellenőrizd, hogy érintetlen maradt"). **A regressziós tesztek FUTTATÁSA nem ide való — az a validate fázis (07) feladata.**

**Sorrendszabály:** A TREG taskokat az implementáló agent a Dokumentáció szekció előtt, de az integrációs [CHECK] taskokat tartalmazó szekció után végzi el. Ha egy TREG fájl frissítése szükséges ahhoz, hogy egy korábbi szekció [CHECK] taskja zöld legyen, az a fájl nem TREG — T taskként kerül a megfelelő szekció [CHECK] taskja elé.

**Egy fájl a tasks listában csak egyszer szerepelhet.**

Ha a plan azt mondja, hogy nincs regressziós érintettség, ez a csoport kihagyható.

```md
## Regressziós tesztek felülvizsgálata

- [ ] TREG1 Ellenőrizd / frissítsd: `test/unit/foo.test.ts` — érintett, mert [indok a plan-ből]
- [ ] TREG2 Ellenőrizd / frissítsd: `test/integration/cycle-XX-foo.sh` — érintett, mert [indok a plan-ből]
```

**2. Dokumentáció** — önálló, utolsó csoport. Ha a ciklus új architektúrális elemet (komponens, interfész, adatfolyam) vezet be, az utolsó task a `docs/architecture.md` frissítése. Tisztán átnevezési vagy refaktorálási ciklusnál ez elhagyható, ha a plan nem tartalmazza.

```md
## Dokumentáció

- [ ] TLAST1 Frissítsd a `docs/architecture.md`-t az új modulok, komponensek, adatfolyamok leírásával — `docs/architecture.md`
- [ ] TLAST2 ...egyéb dokumentáció a plan alapján...
```

_Megjegyzés a `TLAST` és a 08-as frissítés különbségéről: A `TLAST` task az implementáció részeként frissíti az `architecture.md`-t — az éppen elkészült új elemeket (komponensek, interfészek, adatfolyamok) rögzíti. A 08-as review & merge fázis ezután elvégzi a **konzisztencia-ellenőrzést**: átjárja a teljes dokumentumot, javítja az elavult részeket, és a ciklus végső állapotát egységessé teszi. A két lépés nem duplikálja egymást: a `TLAST` ír, a 08 ellenőriz és finomít._

---

## Egy jó task ismérvei

- **Kis méretű**: egy task akkor önálló commitra alkalmas, ha **(a) legfeljebb 2 fájlt érint, ÉS (b) egyetlen logikai változást fed le**. Ha 3+ fájl VAGY több független logikai változás van benne, bontsd önállóan commitolható részekre. (A határeset — pl. 2 fájl + összetett logika — is bontandó, ha a (b) feltétel sérül.)
- **Konkrét**: egyértelmű, mit kell csinálni és melyik fájlban.
- **Elvégzettnek számít**, ha: az érintett fájl módosítva van, és a csoport záró `[CHECK]` taskja hibamentesen lefutott. Egy `[RED]` vagy `[GREEN]` task önmagában nem tekinthető kész-nek, amíg a csoportzáró `[CHECK]` nem zöld.
- **Nem átfedő**: egy változtatás csak egy taskban szerepel.

Ha egy task túl nagy, bontsd ketté.

---

## Minőségellenőrzés — lezárás előtt

Menj végig a következő csoportokon sorban. Minden csoportot önállóan pipáld ki, mielőtt a következőre lépsz.

### A) Plan lefedettség

- A Prerequisite dokumentumok listája tartalmazza a `plan.md`-t és minden `Reviewed` schema artifaktot?
- **Plan `Tervezett módosítások` lefedettség:** menj végig fájlonként — minden fájl kapott legalább egy taskot?
- **Plan `Ellenőrzési stratégia` lefedettség:** menj végig a plan `Ellenőrzési stratégia` szekciójának minden parancsán — mindegyik megjelent `[CHECK]` taskként valamelyik csoportban?
- **Regressziós érintettség lefedve:** a plan `Regressziós érintettség` táblázatának minden sora megjelent-e `TREG` taskként? Ha a plan azt mondja nincs érintettség, ez a csoport hiányozhat.

### B) TDD helyesség

- Minden `[RED]` taskhoz van párja `[GREEN]` task, és a RED megelőzi a GREEN-t?
- **TDD kötelezettség:** Minden új/módosított üzleti logikát megvalósító `[GREEN]` taskhoz tartozik-e egy azt közvetlenül megelőző `[RED]` (tesztíró) task? (Kivéve ha nem-TDD task, pl. konfiguráció, dokumentáció.)
- Minden task a plan végrehajtási sorrendjét követi?

### C) `[CHECK]` task minőség

- Minden logikai csoport végén van `[CHECK]` task konkrét paranccsal?
- **`[CHECK]` célzottság:** minden `[CHECK]` task célzott parancsot tartalmaz (pl. `npm test -- path/to/test.ts`), nem az egész suite-ot (`npm test`)? A regressziós és teljes E2E futtatás a validate fázis (07) feladata.
- **`[CHECK]` relevanciája:** a csoport záró `[CHECK]` taskja az adott csoport módosításait ellenőrzi — ne futtass más szekció tesztjeit egy csoport záróellenőrzéseként. Ha a csoport módosított kódjához nincs önálló egységteszt (pl. proxy konfiguráció, mock szerver route), typecheck vagy build check elegendő helyette.
- **Parancsok helyessége:** Minden bash parancs (különösen a `[CHECK]` taskokban szereplő `cd` parancsok utáni relatív útvonalak) valós és helyes? A `../../` típusú útvonalak gyakran kiugranak a projekt gyökeréből, kerüld a túlzott visszalépést, ellenőrizd az útvonal logikáját!
- **Regresszió futtatás nincs a tasks-ban:** ellenőrizd, hogy a tasks lista nem tartalmaz regressziós teszteket FUTTATÓ `[CHECK]` taskot — az a validate fázis feladata.

### D) Task granularitás és előkészítés

- **Granularitás:** Van olyan task, ami 3 vagy több fájlt érint, vagy összetett logikát vezet be? Ha igen, bontsd fel.
- **Előkészítő lépések elkülönítése:** menj végig minden `[CHECK]`, `[RED]` és tesztelési taskon — ha bármelyik konfigurációs, előkészítő parancsot is tartalmaz (pl. kulcsgenerálás, docker build, env beállítás, tanúsítvány másolás), az előkészítő lépés kerüljön külön taskba, amely megelőzi a tesztelési taskot.
- **Gépi előfeltételek felszínre hozása:** menj végig a `[CHECK]` taskokon — ha bármelyik a projekt standard futtatási környezetén kívüli gépi feltételt igényel (machine-level env var, pl. `KEYCLOAK_HOME`; telepített külső szoftver; előre futó külső service), ezt a logikai csoport fejlécébe kell emelni blockquote-ban. Bele kell kerülnie: a konkrét env var neve + példaérték; ha a teszt egy külső service-t indít el, a teljes indítóparancs a kritikus flag-ekkel (pl. `kc.sh start-dev --features=token-exchange:v1`). Plan/spec hivatkozás önmagában nem elegendő — az információnak a task szintjén kell láthatónak lennie.
- **Valódi konténerizált tesztfutás:** Ellenőrizted, hogy a felvett `[CHECK]` és integrációs/E2E teszt-taskok valódi, konténerizált szolgáltatások ellen futnak-e le ahelyett, hogy a fejlesztői gépen manuálisan elindított natív folyamatokra hagyatkoznának?

### E) Dokumentáció és TypeScript

- **Meglévő komponens README:** Ha a ciklus meglévő komponens konfigurációját (env var-ok, indítási paraméterek, külső kapcsolatok) változtatta meg, a komponens `README.md` frissítése szerepel-e taskként a Dokumentáció csoportban?
- **Architecture dokumentáció:** Ha a ciklus új komponenst, interfészt, adatfolyamot vagy architektúrális elemet vezet be, az utolsó task a `docs/architecture.md` frissítése. Tisztán átnevezési, refaktorálási vagy törlési ciklusnál ez elhagyható, ha a plan nem tartalmazza.
- **TypeScript rename ellenőrzés:** Ha a ciklus TypeScript interfész-, típus- vagy metódusnevet nevez át, ellenőrizd, hogy a plan `Ellenőrzési stratégia` szekciója tartalmaz-e `typecheck` parancsot minden érintett npm package-hez. Ha igen, vedd fel [CHECK] taskként. Ha nem szerepel a planban, **ne találd ki magad** — a parancs csak akkor kerülhet taskba, ha a plan explicit felsorolja (a plan agent ellenőrzi a package.json-ban, hogy a script létezik-e).
- **Fájl elérési utak formátuma:** Minden fájl elérési útja és linkje a fájl aktuális könyvtárához képest relatív útvonal legyen (a mappa mélységének megfelelő számú visszalépéssel a projekt gyökeréig, pl. `../../apps/legacy-login/config/users.json`)? Abszolút útvonalak vagy `file://` sémájú linkek sehol nem szerepelhetnek a dokumentációban.

---

## Megállási szabályok

Ha tasks írása közben az alábbiak bármelyike teljesül, **STOP — állj meg és jelezd a felhasználónak** (ne találd ki a hiányzó részt):

- **Task nem specifikálható:** nincs egyértelmű érintett fájl, nincs elvégzési kritérium, vagy a lépés nem bontható le egyértelműen. Ez a plan hiányosságát jelzi. Állítsd a `plan.md` státuszát vissza `Piszkozat`-ra, jelezd pontosan mi az alulspecifikált lépés, és kérd a plan frissítését. A tasks lista csak ezután folytatható.
- **A plan egy `Tervezett módosítások` bejegyzéséhez nem tudsz taskot megfogalmazni:** a bejegyzés alulspecifikált vagy értelmezhetetlen. Állítsd a `plan.md`-t `Piszkozat`-ra, jelezd melyik bejegyzés, és kérd a pontosítást.
- **Egy task csak feltételesen végezhető el** (pl. egy még nem létező fájltól vagy egy másik ciklus eredményétől függ): jelezd a függőséget, és kérj döntést — előfeltétel-taskként vegyük-e fel, vagy a plan hiányos.
- **A plan és a meglévő kód ellentmond egymásnak:** egy lépés megvalósíthatatlannak tűnik a jelenlegi kódbázis alapján. Ne módosítsd a plan-t magad — jelezd, és kérj döntést.
- **Körkörös függőség a taskokban:** A → B → A jellegű függőség, amit nem lehet feloldani átrendezéssel. Jelezd pontosan, és kérj döntést.

Minden esetben csak **egy** problémát jelezz egyszerre.

---

## Státusz kezelés

Ha a lista teljes és a minőségellenőrzés átment, tedd fel a kérdést a felhasználónak:
*"A task lista minőségellenőrzése átment. Készen áll a tasks lista implementálásra? Ha megerősíted, átállítom `Implementálásra kész` státuszra."* — Ne állítsd át a státuszt a megerősítés előtt. **A válasz végén helyezd el a `tasks.md` közvetlen, kattintható linkjét.**

Ha a felhasználó megerősíti:
- Állítsd a `tasks.md` státuszát `Implementálásra kész`-re.
- Készíts git commitot a fázis befejezéséről:
  ```bash
  git add specs/cycle-NN-<cycle-name>/
  git commit -m "cycle-NN: 04-tasks"
  ```

> **Kész lifecycle:** a `tasks.md` az `Implementálásra kész` → (implementáció során `Validálásra kész`) → a validate (07) PASS után `Kész` státuszra lép. A 08 fázis már `Kész`-t vár.

Ha a státusz `Implementálásra kész`, állj meg. Ne kezdj implementálni vagy analízist. Jelezd a felhasználónak a következő lépést és a fázis indító promptját, például:
> *"A task lista kész. Folytathatjuk az 5. lépéssel (analyze — kereszt-fázisos konzisztencia ellenőrzés). Használd ezt a promptot:
> ```
> Kövesd a `prompts/skills/05-analyze.md` utasításait.
> Input: `specs/cycle-NN-<cycle-name>`
> ```"*
> **A válasz végén helyezd el a `tasks.md` közvetlen, kattintható linkjét.**


