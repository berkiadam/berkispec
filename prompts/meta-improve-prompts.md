# Meta-prompt — Prompt fejlesztés

Ez a fájl arra való, hogy egy új AI-sessziót indítsál, amelynek célja a `prompts/` mappa promptjainak felülvizsgálata vagy továbbfejlesztése.

**Használat:** Másold be az alábbi szaggatott vonaltól az AI-nak, és add meg a konkrét fejlesztési célt a végén.

---

Egy **spec-driven development workflow** promptrendszerét fejlesztjük. A `prompts/` mappa az AI-asszisztált szoftverfejlesztési ciklus fázisonkénti instrukcióit tartalmazza, **skillekre** (`prompts/skills-hu/` — fázis-receptek) és **ágensekre** (`prompts/agents-hu/` — specialista subagentek) szervezve. Minden skill egy fázist vezérel — ezeket a promptokat adjuk be egy AI-agentnek, hogy az adott fázist elvégezze.

A rendszer célja: egy-két fejlesztő és egy AI-agent együtt, következetes minőségű, tesztelt szoftvert fejlesszen ciklusonként leszállítható egységekben. A promptok adják az agentnek a keretet, korlátokat, minőségellenőrzési listát és megállási szabályokat.

---

## A workflow felépítése

A teljes fejlesztési folyamat 10 lépésből áll (0–9):

**A flow ELŐTT (opcionális segédparancs):**
- `bs-brainstorm` — feltáró ötletelés és közös tervezés, amikor még a *mit és hogyan* a kérdés. Perzisztens munkafájl (`.bs-brainstorm/brainstorm-NN-<slug>.md`, gitignore-olt), olcsó **párhuzamos `researcher`** feltárás (BS7), beszélgetési gardek (egy kérdés/kör, 2–3 alternatíva + ajánlás, tilos az igenelés, BS8–BS13). **Nem fázis:** nem változtat státuszt, kódot és a mappán kívül semmit nem ír (BS1). Átadás a flow-nak: `/bs-add-cycles brainstorm: NN` → a `cycle-design-input.md` feltöltése a desztillátummal (BS18).

**A flow UTÁN / mellett (opcionális segédparancs):**
- `bs-manual-test-plan` — **kézi tesztterv** a ciklushoz (`specs/cycle-NN-<cycle-name>/manual-test-plan.md`), hogy egy ember végig tudja próbálni a ciklus funkcionalitását: komponens-indítás, tesztadatok, `TG-NN` tesztcsoportok konkrét hívásokkal (`curl` **és** `.http`) és konkrét elvárt eredménnyel, kétirányú `DoD-NN` lefedettség (MT6), és az automata teszteredmények helye. **Kapu:** az `analyze-report.md` `PASS` státusza (MT1) — a fázis nem felderít, hanem **összeszerel** a `plan.md` `## Környezeti koordináták` (KO1), a `spec.md` DoD/teszt-szekció és a `conventions.md` riport-táblája alapján; ezért egyben őszinteség-teszt a KO1-re. **Kétmódú (MT3):** `Tervezett` (a tervből, valós kódon nem verifikált) vagy `As-built` (a kódhoz ellenőrizve — eltérésnél a kód nyer, és bekerül a `Változásnapló`-ba). **Nem fázis és nulla visszacsatolás (MT4):** a `00–09` láncot, a státusz-láncot és a `07`/`08`/`09` gépezetét nem érinti, eredményfájl nem készül. Determinisztikus kapu zárja (`manual-test-gate-check.py`, MG1–MG10), fő ágenssel, subagent nélkül (MT5).

**Projekt szintű setup (egyszer fut le):**
- `00` — Projekt inicializálás: `conventions.md` létrehozása (konvenciók, tech stack, portok, merge stratégia)
- `01` — Ciklusok kezelése: `specs/roadmap.md` létrehozása/karbantartása (cikluslista, függőségek, teszt kritériumok)

**Per-ciklus loop (minden fejlesztési ciklusra ismétlődik):**
- `02` — Spec írás: `specs/cycle-NN-<cycle-name>/spec.md` — státusz: `Tervezésre kész`
- `03` — Plan írás: `specs/cycle-NN-<cycle-name>/plan.md` — státusz: `Task írásra kész`
- `04` — Tasks írás: `specs/cycle-NN-<cycle-name>/tasks.md` — státusz: `Implementálásra kész`
- `05` — Analyze: kereszt-fázisos konzisztencia ellenőrzés (read-only orchestrátor) — `analyze-report.md` PASS/FAIL; FAIL esetén önjavító hurok (fixer-subagentek, `max X=3`)
- `06` — Implementálás: kód + `tasks.md` — státusz: `Validálásra kész`; a `test-report/implement/` **hivatalos fázis-mappa** (TR6): mindig a `check-log.md` helye, és ha a `conventions.md` `**Riport-fázisok:**` mezője felsorolja az `implement`-et, a záró állapot teljes riport-készletéé is (ugyanaz a `report-gate-check.py` kapu)
- `07` — Validálás és kódreview: gyors tesztek → statikus réteg (Sonar + `reviewer` subagent) → nehéz tesztek/regresszió → DoD/kapuk (VD13: olcsó → statikus → drága; orchestrátor). **Determinisztikus réteg (VD11/b):** a futtatás/kiértékelés szkriptekkel megy (`run-tests.py` a plan gépi táblájából, `sonar-gate.py` az API-ból, `dod-check.py` bizonyíték-joinnal, `contract-guard.py` a VD3a kapura, `validate-gate-check.py` a kis kapukra, `round-log.py` a naplóra) — a nyers teszt-log, a Sonar-riport és a `git diff` nem kerül LLM-kontextusba — PASS / FAIL; FAIL esetén önjavító hurok (`implement-fixer` / `review-fixer` = 06 fix-mód, per-item 3 egymást követő / 5 összes bukás + 5 egymást követő FAIL-futás korlát, VD5 eszkaláció 03/02-re)
- `08` — Doc-sync: a `docs-generated/` mappa (system-overview, architecture, CHANGELOG, design-drift, mappa-index + komponens README-k) naprakészen tartása az as-built rendszerhez — terv (`doc-sync-planner` subagent → `doc-sync-plan.md`) → mechanikus végrehajtás → objektív konzisztencia-kapu (DS22); kapu-bukásnál ember-vezérelt javítás (`doc-sync-questions.md`). **Nem** önjavító subagent-hurok.
- `09` — Merge: a ciklus branch beolvasztása (lokális squash vagy PR) — nincs hurok és nincs subagent; a kapuk (státusz, tiszta review, doc-sync) bukása visszairányít a `07`-re vagy a `08`-ra; a merge kézi megerősítéssel (RD8)

Minden ciklus mappája: `specs/cycle-NN-<cycle-name>/`

---

## A prompt fájlok

> **⚠ A repó KÉTNYELVŰ — a lenti tábla a `-hu` fát nevezi meg, de MINDEN sorának van `-en` párja.**
> A szerkezet **teljesen szimmetrikus** (LG5): nincs suffix nélküli, kitüntetett fa.
>
> ```
> prompts/
> ├── skills-hu/  · agents-hu/  · shared-hu/    # a magyar prompt-nyelvi fa
> ├── skills-en/  · agents-en/  · shared-en/    # az angol — AZONOS fájlnevek, AZONOS szerkezet
> ├── lang/                                     # a PROJEKT-nyelvi tartalom (a két tengely itt találkozik)
> │   ├── status-keys.json                      # szekciónév / mezőnév / státusz szótár (`hu` + `en` szelet)
> │   ├── hu/  ·  en/                           # projekt-nyelvi blokkok + `descriptions.json`
> └── scripts/                                  # nyelvfüggetlen
> ```
>
> **Két nyelvi tengely, egymástól függetlenül:** a **prompt-nyelv** dönti el, melyik `-<lang>`
> fából telepítünk; a **projekt-nyelv** azt, hogy a `lang/<L>/` blokkok és a `status-keys.json`
> melyik szelete kerül be. Mindkettő **build-time** dől el és bedrótozódik (LG2) — a projektben
> semmilyen nyelvi mező nem marad (LG17).
>
> **Amit egy prompt-módosításnál tudni kell:**
> - a **szerkezeti** változást (címsor, kódblokk, INCLUDE-marker, szabály-ID, nyelvi token,
>   imperatívusz-darabszám) **mindkét fán** át kell vezetni — ezt a `lang-parity-check.py` őrzi;
> - az **artefaktum-szekciónevek, mezőnevek és státusz-értékek** a promptban **NEM literálok**,
>   hanem `<sec:…>` / `<field:…>` / `<status:…>` tokenek, amiket a telepítő old fel a
>   `lang/status-keys.json`-ból. **Új szekciónév → előbb kulcs a JSON-ba, csak utána token.**
> - a **user-facing mondatok és az artefaktum-sablonok** nem a promptban élnek, hanem a
>   `lang/<L>/<fájl>.md` horgonyaiban, `<!-- INCLUDE:lang/<fájl>.md#<horgony> -->` markerrel
>   behivatkozva — ezeket **mindkét nyelven** szerkeszteni kell.

| Fájl | Fázis | Bemenet | Kimenet |
|------|-------|---------|---------|
| `prompts/skills-hu/brainstorm.md` | *(nem fázis — a flow előtt)* | téma szabad szöveggel / `folytassuk a NN-est` | `.bs-brainstorm/brainstorm-NN-<slug>.md` (Cél · Tények forrással · Alternatívák · Döntések · Nyitott kérdések · Javasolt ciklus-vágás · Napló) — átadás a `01`-nek (BS18) |
| `prompts/skills-hu/manual-test-plan.md` | *(nem fázis — az 05 után bármikor)* | ciklus mappa (opcionálisan `mód: tervezett` / `mód: as-built`) | `manual-test-plan.md` (Környezet és indítás · Tesztadatok · Automata tesztek · `TG-NN` kézi tesztcsoportok · Nem kézzel tesztelhető · Lefedettség · Változásnapló) — előfeltétel: `analyze-report.md` = `PASS`; kapu: `manual-test-gate-check.py` |
| `prompts/skills-hu/00-init-project.md` | Projekt init | Projekt leírás | `conventions.md` |
| `prompts/skills-hu/01-add-cycles.md` | Ciklusok kezelése | HLD/LLD vagy leírás | `specs/roadmap.md` |
| `prompts/skills-hu/02-write-spec.md` | Spec | Roadmap + ciklus neve | `spec.md` (`Tervezésre kész`) |
| `prompts/skills-hu/03-write-plan.md` | Plan | `spec.md` | `plan.md` (`Task írásra kész`) — kötelező része a `### Teszt-forgatókönyvek` szekció (`TS-NN`, TS1–TS6) és a `### Gépi futtatási tábla` (TP4); a forgatókönyvek tervezését a `shared-hu/test-scenario-design.md` recept vezeti (TD0–TD6) |
| `prompts/skills-hu/04-write-tasks.md` | Tasks | `plan.md` | `tasks.md` (`Implementálásra kész`) |
| `prompts/skills-hu/05-analyze.md` | Analyze | ciklus mappa | `analyze-report.md` (PASS/FAIL) — mechanikus kapu + négy párhuzamos diagnoszta-kör (`analyzer` × 3 hatókör, `analyzer-exec`); FAIL → önjavító hurok (fixer-subagentek, `max X=3`, iterációnként egy analyzer-kör) |
| `prompts/skills-hu/06-implement.md` | Implementálás | `tasks.md` | Kód + `tasks.md` (`Validálásra kész`) + `test-report/implement/` (`check-log.md`, és riport-fázis esetén a teljes riport-készlet — TR6); a task listát **egy futásban** dolgozza fel (IM1) |
| `prompts/skills-hu/07-validate.md` | Validálás + kódreview | `spec.md`, `plan.md`, `tasks.md`, cycle diff | `test-report/validation-report.md` + `test-report/code-review.md` — FAIL → önjavító hurok (`implement-fixer` / `review-fixer`, 3-próba korlát, VD5 eszkaláció) |
| `prompts/skills-hu/08-doc-sync.md` | Doc-sync | ciklus mappa + `docs-generated/` | konzisztens `docs-generated/` (system-overview, architecture, CHANGELOG, design-drift, README) + `doc-sync-plan.md` — terv (`doc-sync-planner`) → végrehajtás → objektív kapu (DS22); kapu-bukás → ember-vezérelt javítás (`doc-sync-questions.md`) |
| `prompts/skills-hu/09-merge.md` | Merge | ciklus mappa, `conventions.md` | merged branch / PR + lezárt roadmap — nincs hurok és nincs subagent; bukó kapu → vissza a 07-re vagy a 08-ra |

A specialista subagentek a `prompts/agents-hu/` alatt: `reviewer.md` (07 — read-only kód-diagnózis), `analyzer.md` (05 — read-only **szemantikai** diagnózis, 1–5. kategória, hatókör-paraméterrel három párhuzamos körben), `analyzer-exec.md` (05 — read-only **végrehajthatósági** diagnózis, 6. kategória; az `analyzer`-körökkel párhuzamosan fut), `researcher.md` (03 Mód A; 00/01/02/06 + `bs-brainstorm` Mód B), `doc-sync-planner.md` (08 — read-only doc-sync tervkészítő), az 05 önjavító hurok fix-mód belépői: `spec-fixer.md`, `plan-fixer.md`, `tasks-fixer.md`, a 07 hurkának két fix-mód belépője: `implement-fixer.md` (teszt/Sonar/DoD) és `review-fixer.md` (review-findingok), `## Validációs javítások` ill. `## Review javítások` bemenettel.

**A fix-mód belépők két megvalósítása** (mindkettő logika-duplikáció nélkül): a 02/03/04 fixerek promptja **önhordó** — a fix-mód szekció és a fázis minőségi kapuja a `prompts/shared-hu/{fix-mode,quality-check}-*.md` fájlokból **build-time beemelődik** a skillbe és a wrapperbe is, így a fixer **nem olvas fázis-skillt** (D13). A 06 fix-módját használó `implement-fixer`/`review-fixer` viszont még a klasszikus úton, a `06-implement.md` Fix-mód szekciójának beolvasásával delegál.

A repó gyökerében lévő `README-HU.md` „Indító prompt (copy-paste)" szekciója tartalmazza a felhasználónak szánt indító prompt blokkot.

**Telepítés és scriptek.** A támogatott telepítési út: `./install.sh` (vagy `install.ps1`) →
`prompts/scripts/install-helper.py`. A `prompts/scripts/init-project.sh` **elavult** (LG19):
szimlink-alapú alternatíva, amit soha nem használtunk — ne hivatkozz rá, és ne fejleszd tovább.

**⛔ KÉTNYELVŰ REPÓ — KÖTELEZŐ KÉZI KAPUK MINDEN COMMIT ELŐTT.** A promptok **két
prompt-nyelvi fában** élnek (`prompts/skills-hu/` ↔ `prompts/skills-en/`, ugyanígy
`agents-*` és `shared-*`), a projekt-nyelvi blokkok pedig a `prompts/lang/<nyelv>/`
alatt. **Nincs CI és nincs pre-commit hook**, tehát a két fa szinkronját semmi nem
őrzi automatikusan — ezt a két scriptet **kézzel kell lefuttatni**:

```bash
python3 prompts/scripts/lang-parity-check.py      # nyelvi paritás (§11) — default mód
python3 prompts/scripts/sync-gemini-agents.py --check   # a gemini agent.json tükrök
```

- **Ha az egyik nyelvi fát szerkeszted, a másikat is szerkeszd** — a paritás-kapu a
  szerkezeti eltérést (címsor, kódblokk, INCLUDE-marker, szabály-ID, nyelvi token,
  imperatívusz-darabszám) megfogja, a **jelentés**-eltérést nem: az emberi review dolga.
- A kapu **két üzemmódú**: a napi, commit előtti futás a **defaultot** használja (a
  féloldalas fájlok WARN-ok), a PR zárása és a végső elfogadás a **`--strict`**-et
  (ott a teljes fájlhalmaz-paritás is kötelező).
- Mindkét script **repó-karbantartó eszköz**: a telepítő szándékosan **nem másolja**
  őket a célprojektbe.

---

## Tervezési elvek, amelyek minden promptban érvényesülnek

**1. Fáziskapu (előfeltétel-ellenőrzés)**
Minden prompt első lépése: beolvassa az előző fázis dokumentumának státuszát. Ha nem a várt státuszon áll, megáll és visszairányít. Ez megakadályozza, hogy egy befejezetlen fázis alapján haladjon tovább.

**2. Minimális kontextus betöltés**
Az agent csak a szükséges fájlokat olvassa be, csak a releváns részeit. Ha mélyebb kutatásra van szükség, azt delegálja, és az eredményt összefoglalva hozza vissza — ne töltse tele a fő munkamemóriát. A cél: a fő kontextusablak ne telítődjön felesleges információval.

**3. Egyetlen kérdés egyszerre**
Ha a promptnak döntési ponthoz van szüksége a felhasználó inputjára, egyszerre csak egy kérdést tesz fel, megvárja a választ, majd iterál. Ez megelőzi az egyszerre több nyitott kérdés kavalkádját.

**4. Scope fegyelem**
Minden fázis szigorúan a saját scope-ján belül marad:
- Spec: csak az üzleti viselkedést írja le — nem tervez implementációt
- Plan: csak a spec scope-ját fedi le — nem bővíti, nem szűkíti
- Tasks: csak a plan tervezett módosításait bontja le — nem ad hozzá újat

**5. Státuszkezelés**
Minden fázis dokumentuma explicit státuszmezőt kap (`Piszkozat` → fázisspecifikus zárolt státusz). A következő prompt ezt olvassa be kapuként.

**6. Minőségellenőrzési lista (lezárás előtt)**
Minden prompt tartalmaz egy kötelező ellenőrzési listát, amelyet a fázis lezárása előtt le kell futtatni. Ez biztosítja, hogy a következő fázis egy teljes és konzisztens dokumentumot kap.

**7. TDD jelölés (04 + 06)**
A 04-es prompt tasks listát ír, a 06-os (implement) végrehajtja. A TDD ciklus a tasks listában explicit jelöléssel van rögzítve:

- `[RED]` — az agent először megírja a tesztet, amely **bukni fog**, mert az implementáció még nem létezik. Ez rögzíti a várható viselkedést kód formájában, mielőtt bármit implementálnánk.
- `[GREEN]` — ezután jön az implementáció, amelynek célja kizárólag az, hogy a `[RED]` teszt átmenjen. A `[RED]` task mindig megelőzi a párját.
- `[CHECK]` — minden logikai csoport végén kötelező: konkrét parancsot tartalmaz (pl. `npm test`, `npm run typecheck`), amelyet az agent ténylegesen lefuttat. Egy `[RED]`/`[GREEN]` task nem számít késznek, amíg a csoportzáró `[CHECK]` nem zöld.

Nem minden task TDD: konfigurációs fájlok, docker, README, infrastruktúra-változások esetén nincs `[RED]`/`[GREEN]` jelölés.

**7/b. Csonkítás-mentes átemelés (KX2 a 02-ben, KX3 a 03-ban)**
A fázisok közötti átadás **kétirányú hibát** tud véteni, és mindkettőre van szabály. (a) A bemenet **túl absztrakt** (hivatkozik valamire ahelyett, hogy tartalmazná) → `Hivatkozás-feloldás`: a hivatkozást fel kell oldani a forrásból, literál értékekkel. (b) A bemenet **már kidolgozott** (OpenAPI-leíró, teljes payload, hibamátrix, többlépéses teszt-forgatókönyv) → **szó szerint, csonkítás nélkül** kell átvinni: a 02-ben ez a `KX2` („ne zanzásítsd a teszteseteket"), a 03-ban a `KX3`. Az irány mindkettőben: **bővítés és pontosítás igen, összevonás és elhagyás nem.** A `KX3` explicit feloldja azt a három szabályt, ami korábban az egyszerűsítés felé nyomta a plan-írót („a plan terv, nem archívum" — az a repó forrásfájljaira szól; „az absztrakciós szintet fel kell oldani, nem reprodukálni" — a *szintre* igaz, a *tartalomra* nem; a 05 duplikáció-kategóriája — az nem vonatkozik a kötelező önhordóságra). A 05 mechanikus kapuja méri (`V1`: a spec szerződés-blokkjai megvannak-e a plan-ben; `V2`: a teszt-szekciók terjedelme), a prózai csonkítás pedig az `analyzer` 3. kategóriájában marad. **Prompt-módosításnál ezt ne rontsd el:** a „tömörítsd", „ne duplikálj", „a plan legyen rövid" jellegű utasítás ebben a fázisban adatvesztést okoz.

**7/c. Útvonal-konvenció (RP1)**
Egyetlen közös blokk (`prompts/shared-hu/path-format.md`) definiálja: **kód- és fájl-hivatkozás a repó gyökeréhez** képest relatív (a parancsok ott futnak, és a `05` mechanikus kapuja oda oldja fel a horgonyokat), **dokumentum-link a fájl saját könyvtárához** képest (hogy kattintható legyen); abszolút, gép-specifikus és `file://` alak tilos a dokumentum tartalmában (a chat-válaszban adott kattintható link kivétel). A kapu `R1` checkje méri. **Prompt-módosításnál ne írd újra fázisonként** — a szabály korábban három helyen, egymással ütköző tartalommal élt.

**7/d. A kapu-konfiguráció együtt mozog a struktúrával (GC1)**
Több determinisztikus kapu a projekt `conventions.md`-jéből olvas (TR3 riport-artefaktumok és útvonal-alap, Sonar küszöbök, teszt-parancsok, portok, merge-stratégia). Ha egy ciklus olyat változtat, amit egy kapu ott keres, a `conventions.md` frissítése **a ciklus része**: explicit döntés → a plan tervezi konkrét tartalommal → `[GREEN]` task → a kapu ugyanebben a ciklusban újra fut. A `00`-ra csak akkor megy vissza, ha magát a **projekt-konvenciót** kérdőjelezzük meg. Határvonal (TC1/c): riport-artefaktum/útvonal-alap/riport-parancs → `conventions.md`; teszt-recept és koordináta → `specs/test-conventions.md`. **Séma-váltásnál kötelező migrációs őr:** ha egy struktúra jelentése változik, de a formátuma nem (mint a TR5-nél: a tábla utolsó oszlopa `test-report/` gyökér → kör-mappa), a régi adat **csendben félreértelmeződik** — ezért a szekcióba verzió/szemantika-jelölő kell (`**Artefaktum-útvonal alapja:**`), és a kapu a jelölő hiányában nem találgat, hanem `exit 2`-vel megáll a pótlandó sorral. **Prompt-módosításnál:** ha egy kapu által olvasott struktúra jelentését módosítod, mindig tedd mellé a jelölőt és a migrációs ágat.

**7/g. Egy zöld teszt nem bizonyítja, HOL volt zöld (EV1–EV5)**
Egy ciklus a dev környezetre telepített, a tesztjei viszont lokális célpontra futottak — egy `…:dev-e2e` **nevű** script configjában `baseURL: "http://127.0.0.1:5178"` állt. Minden zöld lett, a validálás PASS-ra zárt, és nem derült ki, hogy a telepített komponens el sem indult. A plan **nem** volt felületes: a `<sec:environment_coords>` végig dev URL-eket sorolt. A baj az volt, hogy **a teszt tényleges célpontja sehol nem volt látható** — parancs helyett egy npm-script neve, a cím egy konfigfájlban —, a bizonyíték (JUnit XML, Allure) pedig nem rögzíti a megszólított hostot. Ezért: kötelező `**<field:f_target_env>:**` mező a planben (EV1), kötelező `<field:f_environment>` oszlop a futtatási táblában (EV2), és nem-lokális kategóriánál a cél-host **literálisan a parancsban** (EV3) + **elérhetőségi probe** ugyanoda az `Előfeltétel` cellában (EV4) + `localhost`-tilalom (EV5, a `TS-NN` hívásokra is). A `run-tests.py` a futtatás **előtt** megáll (`exit 4`), és a környezetet a bizonyítékba írja. **Prompt-módosításnál:** minden új teszt-futtatási útnál kérdezd meg, honnan olvasható ki a CÉLPONT — ha csak egy név utal rá, az nem elég.

**7/f. A teszt-forgatókönyv nem próza (TS1–TS6)**
A `03` hajlamos a spec teszteseteit „nagy vonalakban" átvenni (típus + érintett fájl, lépés és elvárt eredmény nélkül) — akkor is, ha a felhasználó a spec-ben lépésről lépésre leírta. A prompt-oldali szabályok (TC1/a, KX3, a `quality-check-plan` „lépésenkénti híváslánc" pontja) mind megvoltak, de **egyik sem volt ellenőrizhető**: a `<sec:testing_strategy>` szabad próza, a `V2` kapu pedig **aggregált** sorszámot mér, amit a gépi tábla és a bootstrapping hossza elfed. Ezért a plan kötelező, **per-teszteset szerkezetet** kapott: a `### <sec:plan_test_scenarios>` szekció `TS-NN` blokkjai (`Mit tesztelünk` · `Előfeltétel` · négyoszlopos lépés-tábla · `Takarítás`), az `analyze-gate-check.py` hat checkjével (TS1 létezés · TS2 teljesség · TS3 **lépésenkénti** konkrétum · TS4 placeholder-tilalom · TS5 kétirányú `DoD-NN` ↔ `TS-NN` · TS6 hézagmentes azonosítók). A TS3 kemény padlója: az elvárt eredmény cellában legalább egy backtickes érték vagy szám — a „sikeresen lefut" nem eldönthető. A forma azonos a `bs-manual-test-plan` `TG-NN` csoportjaival: a `TS-NN` ugyanaz, a keletkezés helyére felhozva, ezért az MT innentől tényleg **összeszerel**. **Prompt-módosításnál:** a „tömörítsd a teszt-szekciót" jellegű utasítás itt adatvesztés, és minden új prózai teszt-elvárás mellé kérdezd meg, mivel lesz gépiesen mérhető.

**7/h. A konzerváló szabály nem hoz létre tesztet (TD0–TD6)**
A `TS1–TS6` után a panasz nem szűnt meg, csak áthelyeződött: formailag hibátlan `TS-NN` blokkok, bennük egyetlen kérés-válasz pár. Az ok, hogy a keret minden teszt-szabálya **konzerváló** volt (`KX2`/`KX3` megőrzi, amit a bemenet hordoz; a `TS3` **kemény padlót** ad) — egy gyenge modell pedig pontosan a padlóra optimalizál, egy mondatos bemenetből meg nincs mit megőrizni. A hiányzó lépés a **létrehozás**: a `prompts/shared-hu/test-scenario-design.md` blokk (a `03` skill és a `plan-fixer` beemeli) kitöltendő kérdésekké alakítja a teszt-tervezést — `TD1` dimenzió-leltár (a szorzat kiírásával dönti el, **hány** forgatókönyv kell), `TD2` megfigyelési négyes (válasz · **megszámolt** mellékhatás · **közvetlenül kiolvasott** állapot · **negatív kontroll**), `TD3` megszámolhatóság (a számlálás forrását meg kell nevezni), `TD4` negatív kontroll az izolációhoz, `TD5` kitöltött kalibrációs minta (a **sűrűséget** kell másolni, nem a témát), `TD6` önteszt. A `TD0` hatókör-jelölés tartja a spec/plan határvonalat: a spec-fázisban viselkedés-szint és parancs-tilalom, a plan-fázisban literál értékek. **Prompt-módosításnál:** minden új teszt-elvárásnál kérdezd meg, hogy a szabály **megőriz** vagy **létrehoz** — és ha a bemenet lehet egyetlen mondat is, akkor kell mellé generáló recept. A padló önmagában nem termel részletet. A `TD6` pontjai szándékosan **jelöltek** egy későbbi determinisztikus checkhez, nem kapu: kapu-fogat csak akkor fizess, ha egy valódi ciklus megmutatja, hogy a recept nem elég.

**7/e. Egy fogalom, egy útvonal-alak (TR5/c) + a riport-fázis (TR6)**
A kör-/fázis-mappának **három bázisa** van: `run-tests.py --round-dir` (repó gyökér), `report-gate-check.py --report-subdir` (ciklus-mappa) és a projekt riport-parancsainak `<phase-dir>` / `REPORT_PHASE_DIR` alakja (`test-report/`). Az egyik alak beragasztása egy másik bázist váró paraméterbe **nem hibaüzenetet ad, hanem rekurzív riport-fát** (`test-report/test-report/…`, `test-report/specs/…`). Ezért: a `07` **0/a** szekciója egy táblában definiálja mind a hármat, a `test-report/` felső szintje **zárt lista** (idegen mappa = útvonal-hiba, törlendő — a takarítási tilalom csak a `round-NN/`-re szól), a szkriptek mind a három alakot normalizálják, a `plan.md` gépi táblája két nem felcserélhető helyőrzőt kap (`{round}` teljes útvonal / `{phase}` fázis-mappa), a `run-tests.py` a futtatás **előtt** `exit 3`-mal megfogja a dupla prefixet, a `report-gate-check.py` pedig layout-őrrel `exit 1`-gyel bukatja. **A TR3 kapu kizárólag a `## Teszt-riportolás` tábla SORAIT kéri számon** — a szekció prózáját nem: ezért az alkalmazás-oldali bizonyíték (REST kérés/válasz audit-napló) is táblasor. A `**Riport-fázisok:**` mező (TR6) dönti el, hogy a `06` csak a `check-log.md`-t írja-e, vagy a záró állapotról a teljes riport-készletet is. **Prompt-módosításnál:** ne írj ki fázisonként útvonalat magyarázat nélkül, és ne vezess be negyedik bázist.

**8. Megállási szabályok — és a 06 folytonossága (IM1)**
A 04-es (tasks) és 06-os (implement) prompt explicit felsorolja azokat az eseteket, amikor az agent megáll és visszakérdez — ne folytassa bizonytalan vagy ellentmondásos helyzetben.

A 06-ban ehhez **kimondott ellenpár** is tartozik: a fázis **egy futásban** dolgozza fel a task listát, egy task lezárása (pipa + `check-log` + task-commit) **nem** fázis-vég, és a megállás öt eseténél (Megállási szabály · fejezet gépi előfeltétele · explicit infrastruktúra-igény · 3-próba · minden task kész) **nincs több**. Ez azért kell kimondva, mert a keretrendszer többi fázisában a „*A válasz végén helyezd el a … kattintható linkjét*" mondat **megállás-jelző**; amíg ez a mondat a 06 per-task lépésében szerepelt, az ágens minden task után visszaadta a szót. **Prompt-módosításnál ezt ne rontsd el:** taskonkénti felhasználói riport, per-task link vagy „folytathatom?" kérdés nem kerülhet vissza a hurokba.

**9. Kereszt-fázisos konzisztencia ellenőrzés + önjavító hurok (05 — analyze)**
A 04 (tasks) után, az implementáció előtt egy analyze fázis fut, **három rétegben**:
1. **mechanikus kapu** (`analyze-gate-check.py`) — minden kör előtt: a gépiesen eldönthető ellenőrzések (hivatkozás-egyeztetés mindkét irányban, markerek, `⟂`, `DoD-NN`, kötelező táblák, futtatott artefaktumok, plan-horgonyok, `Konfiguráció-életút` üres cellái, task-határon átnyúló shell-változó, artefaktum-hang kemény padlója). A kapu **generálja** a riport két lefedettségi tábláját (`DoD-NN → [P-…] → task` lánc), és **leltárt** ad az ítélet-igényes checkek jelöltjeiről;
2. **`analyzer` × 3 hatókör** (read-only, egymással párhuzamosan) — a szemantikai kategóriák a `spec.md` ↔ `plan.md` ↔ `tasks.md` ↔ `conventions.md` négyesen, három körre osztva (`s1-dup-underspec` = duplikáció + alulspecifikáció, `s2-coverage` = ambiguitás + a lefedettség **tartalmi** ítélete a generált mátrixon, `s3-conventions` = konvenció-ütközés); minden kör a kapu `--emit-slices` módjával kimetszett **saját szeletéből** dolgozik, nem a teljes négyesből (SH1);
3. **`analyzer-exec`** (read-only, az előzőekkel **párhuzamosan**) — végrehajthatóság és artefaktum-tulajdon a `plan.md` + `tasks.md` + leltár hármasból.

Iterációnként **egy** teljes analyzer-kör fut (a `PASS` csak teljes körből adható), és négy rövidítő ág védi az iteráció-számot: a fixer **visszatérés előtt maga futtatja a kaput** (GS1), az orchestrátor kapu-futása utána védőháló — mechanikus regresszió esetén az visszamegy ugyanahhoz a fixerhez, analyzer-kör nélkül (G) —, ha a fixer semmit nem változtatott, a hurok megáll és kérdez (N), és ha minden `Must Fix` lokális, a fixerek egyetlen üzenetben, párhuzamosan indulnak (LF1). Ugyanez a kapu a `03` és `04` fázis **lezárása előtt** is lefut (M), hogy a gépies hibák a keletkezésük helyén derüljenek ki. FAIL esetén az 05 **orchestrátorként önjavító hurkot vezényel**: a legkorábbi érintett célfázishoz indít egy fixer-subagentet (a 02/03/04 fix-módja), downstream re-deriválás (`02→03→04`, célzott reconciliation) után újra-analyze fut — amíg PASS, vagy `max X=3` iterációig. A döntést igénylő kérdéseket a fixerek a `*-questions.md`-be gyűjtik (nem kérdeznek közvetlenül), és az orchestrátor teszi fel a felhasználónak (`FÁZIS/Knn` fejléccel); nyitott kérdésnél a hurok megáll, válasz után folytatódik. A hurok alatt a dokumentumok `[analyze-loop]` státusz-markert viselnek (auto-státusz + megszakítás-biztos folytatás), és csak a hurok végén készül egyetlen commit.

**10. Önjavító hurok a kód-fázisban (07 — validate + review)**
A 05-analyze mintáját a **07-validate** veszi át, egyetlen hurokban a tesztekre ÉS a kódreview-ra (RV1). A teljes kör négy lépése (VD13 — olcsó → statikus → drága): gyors tesztek → **statikus réteg: Sonar + kódreview** (`reviewer` subagent, csak ha a gyors tesztek zöldek) → nehéz tesztek + regresszió → DoD/tasks/riport-kapu. A statikus réteg azért előzi meg a nehéz teszteket, mert a Sonar és a review stack nélkül fut, a findingjaik javítása viszont megváltoztatja a kódot — fordított sorrendben minden statikus finding ára egy eldobott E2E-futás lenne. Bármelyik bukása a kör FAIL-je, egyetlen naplóbejegyzéssel a `validation-report.md` `# Validation History`-jába: teszt-/Sonar-/DoD-hibára az `implement-fixer` (`## Validációs javítások`), review-findingra a `review-fixer` (`## Review javítások`) indul — mindkettő 06 fix-mód, közös `[validate-loop]` markerrel és **közös** leállási korlátokkal (per-item 3 egymást követő / 5 összes, plusz 5 egymást követő FAIL-futás). VD3 anti-„teszt-csalás" + VD3a szerződés-integritás kapu, VD5 eszkaláció 03/02-re. A javítás után könnyű kör, majd kötelező **teljes megerősítő kör** — PASS csak teljes körből, tiszta review-val. A review a 07-be költözésével a korábbi 09-es „re-validate" ág megszűnt (az a 07 gépezetét duplikálta); a `09-merge` így már csak a **kézi megerősítéssel** záruló beolvasztás (RD8). A hurkok közös konvencióit a `README-HU.md` „Önjavító hurkok" szekciója rögzíti.

**11. Élő működési dokumentáció (08 — doc-sync)**
A 07-validate és a 09-merge közé egy dedikált **doc-sync** fázis ékelődik, amely ciklusról ciklusra naprakészen tartja a generált projekt-dokumentációt egy `docs-generated/` mappában (`system-overview.md` as-built működésleírás, `architecture.md`, részletes `CHANGELOG.md`, `design-drift.md`, mappa-index README + komponens README-k). Ez **nem** a négy önjavító hurok mintáját követi: a működése **„terv előbb, aztán mechanikus végrehajtás"** (a `doc-sync-planner` read-only subagent → `doc-sync-plan.md` pipálható terv → a fő ágens mechanikusan végrehajtja), majd egy **objektív, projektfüggetlen konzisztencia-kapu** (DS22: megszűnt/átnevezett azonosító `grep`, ábra-átkerülés, mappa-index halmaz-egyezés, coverage-marker) zár. Kapu-bukásnál **ember-vezérelt** javítás indul a `doc-sync-questions.md`-n keresztül (nem subagent-önjavító hurok). A `02-write-spec` „pull"-ként beolvassa a `system-overview.md`-t current-truth kiindulásként; a doc-sync „push"-ként írja — a kettő tartja őszintén a doksit. A 08-doc-sync és a 07 review-kapuja **független minőségi kapuk**: a reviewer csak kódra ad findingot, a generált doksik helyességét a doc-sync saját kapuja garantálja.

---

## A promptok aktuális állapota

A rendszer aktívan használatban van — több fejlesztési ciklus (cycle-01 – cycle-16) lefutott már ezekkel a promptokkal. A skill fájlok a `prompts/skills-hu/`, a specialista ágensek a `prompts/agents-hu/` mappában olvashatók.

---

## Feladatod

Olvasd be a releváns skill fájlokat a `prompts/skills-hu/` mappából (és szükség szerint az ágenseket a `prompts/agents-hu/`-ból), majd segíts a következő fejlesztési célban:

**[IDE ÍRD LE A KONKRÉT FEJLESZTÉSI CÉLT — pl.:]**
- „A 03-as plan skill minőségellenőrzési listája hiányos — egészítsd ki."
- „A 06-os implement skill nem kezeli megfeloloen a delegalas esetét."
- „Vezess be egy uj 09-es fazist: changelog generalas."
- „Altalanos felulvizsgalat: hol vannak kovetkezetlensegek a skillek kozott?"

Ha nincs konkrét cél megadva, végezz általános felülvizsgálatot: keress következetlenségeket, hiányzó megállási szabályokat, scope-szivárgást a fázisok között, és javasolj konkrét javításokat.
