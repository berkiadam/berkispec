# Prompt fejlesztési lista

A `prompts/meta-improve-prompts.md` alapján végzett átfogó felülvizsgálat eredménye. Nyolc szakaszban:

0. **Döntést igénylő pontok** — irányválasztások, mielőtt a tényleges javítás elkezdődik
1. Hiányosságok az egyes promptokban
2. Inkonzisztenciák a promptok között
3. Olcsóbb LLM megfelelőség
4. Prioritás szerinti összegzés
5. Spec-kit ihlette új pontok (SK1–SK7)
6. Skill + Agent refaktor
7. Megjegyzések a javítási folyamathoz

A lista alapján **második körben** végezzük a javításokat. Mielőtt a szövegezés elkezdődne, a 0. szakasz minden pontján döntést kell hozni — több későbbi javítás iránya ezektől függ.

---

## 0. Döntést igénylő pontok

Ezek nem javítások, hanem **irányválasztások**. Minden ponton el kell döntenünk, melyik alternatívát választjuk, mielőtt a tényleges prompt-átírás kezdődne. Egy-egy döntés több későbbi javítás iránya is meghatározza.

- [x] **D1 — `conventions.md` státusza:** legyen explicit státuszmező (mint a többi dokumentumon), vagy elég a „puszta lét" mint kapuszabály a 01-es fázis számára?
  - **A:** Státuszmező (pl. `Piszkozat` | `Kész`) — egységes a többi dokumentummal, explicit kapu.
  - **B (választott):** Puszta lét — egyszerűbb, kevésbé bürokratikus. A `conventions.md` per definitionem kész, ha létezik.
  - **Érintett pontok a listán:** 1.1, 1.2
  - **Döntés indoklása:** A `conventions.md` természete eltér a többi dokumentumtól: nem fázisokon megy át, csak egyszer keletkezik és időnként frissül. Két állapot (`Piszkozat`/`Kész`) felesleges bürokrácia.
  - **A puszta lét csak akkor jó kapuszabály, ha garantáljuk, hogy ha létezik, akkor kész.** Ezért feltételek:
    1. A 00-ban legyen **lezárás előtti minőségellenőrzési lista** (1.1 negyedik pont) — minden szekció kitöltött-e?
    2. A 00-ban legyen **explicit lezáró commit** (1.1 első pont) — a commitba kerülés az implicit „Kész" jelölés.
    3. A 01–08 promptokban legyen **explicit `conventions.md` létezés-ellenőrzés** beolvasás előtt.

- [x] **D2 — Forrásfájl-azonosítás helye (02 vs 03):** a spec `Hivatkozott fájlok` szekciója tartalmazhat-e forrásfájlt, vagy csak a plan azonosítson forrásfájlokat?
  - **A (választott):** A spec csak dokumentációs hivatkozást tartalmaz (README, OpenAPI, séma); a 03 önállóan azonosítja a forrásfájlokat a `Tervezett módosítások` szekció előtt. → A 02 jelenlegi szabálya marad, a 03-at kell átírni.
  - **B:** A spec tartalmazhat forrásfájlt is mint kontextus; a 03 ezeket olvassa be. → A 03 jelenlegi szabálya marad, a 02 tiltást fel kell oldani.
  - **Érintett pontok a listán:** 1.4, 2.3, 3.2.2
  - **Döntés indoklása:** A spec viselkedést ír le, nem implementációt. Forrásfájl-azonosítás már implementációs döntés — a plan dolga. A spec stabil, hosszabb életű; forrásfájl-név refaktor során változhat, elavulna a spec-ben. A 03 amúgy is rendelkezik subagent-alapú „Documentation Reconnaissance" logikával forrásfájl-azonosításra.
  - **Következmény a 03-ra:** a *„Csak a spec `Hivatkozott fájlok` szekciójában szereplő forrásfájlokat olvasd be"* mondatot át kell írni úgy, hogy a 03 önállóan azonosítja a forrásfájlokat (subagent vagy közvetlen kódvizsgálat alapján), és a spec hivatkozáslistája csak dokumentációs/specifikációs anyagokat ad.

- [x] **D3 — 07 PASS előtti felhasználói megerősítés:** kérje, vagy automatikus PASS legyen?
  - **A:** Kérjen megerősítést — konzisztens a 02–04 mintájával.
  - **B (választott):** Automatikus PASS — a validate determinisztikus (tesztek + DoD + Sonar), nem szubjektív, felesleges a megerősítés. Csak dokumentálni kell, miért nem kér.
  - **Érintett pontok a listán:** 1.7, 2.1
  - **Döntés indoklása:** A 07 PASS feltétele determinisztikus: minden teszt zöld + DoD pontjai `✓` + Sonar Quality Gate PASS. Ez objektív ellenőrzés, nem szubjektív minőségi vélemény (mint a 02–04). A megerősítés szertartásos lenne, és a folyamat lendülete fontosabb. A fejlesztő bármikor ellenőrizheti az eredményt a `validate-decision.md`-ben.
  - **Következmény a 07-re:** Legyen explicit mondat a 07 promptban a Státusz kezelés / PASS szekció elején: *„A PASS automatikus, mert determinisztikus ellenőrzéseken alapul (tesztek + Sonar + DoD). Felhasználói megerősítés nem szükséges — az eredmény a `validate-decision.md`-ben ellenőrizhető."* Ez nélkül egy olcsóbb LLM hibásan próbálhat megerősítést kérni.

- [x] **D4 — PR vs lokális squash merge:** PR-alapú flow, vagy lokális merge?
  - **A:** PR-alapú — GitHub PR létrehozás, review/CI, majd merge. A README/meta jelenleg ezt sugallja.
  - **B:** Lokális squash merge — egyszemélyes lokális fejlesztéshez gyorsabb, nincs GitHub függőség.
  - **C (választott):** Konvenció-vezérelt — a 00 prompt tisztázza a merge stratégiát (GitHub / Bitbucket Cloud / Bitbucket Server / GitLab / Lokális), majd az ágens **kipróbálja az access-t**, és nem zárja le a `conventions.md`-t, amíg a választott szolgáltatóhoz sikeresen hozzá nem fér (vagy a felhasználó alternatívát választ).
  - **Érintett pontok a listán:** 1.1 (új), 1.8, 2.3, 4.2
  - **Döntés indoklása:** Egy single source of truth (a `conventions.md`) tartja a merge stratégiát. A fail-fast validáció a projekt elején történik, nem a 08 fázisban — így az implementáció után nem derül ki, hogy nincs token. Általános prompt család marad, támogat többféle szolgáltatót.
  - **Új szekció a `conventions.md`-ben (`## Merge stratégia`):**
    - **Szolgáltató:** GitHub | Bitbucket Cloud | Bitbucket Server | GitLab | Lokális (nincs PR)
    - **Repository URL** (Bitbucket on-prem esetén az API endpoint is)
    - **Authentication:** CLI (`gh` / `glab` / `bb`) | token (env var név) | SSH
    - **PR target branch** (alapból `master`)
    - **Merge típusa:** squash | merge commit | rebase
    - **Branch védelem** (ha van — pl. CI check, review követelmény)
    - **Access teszt parancs** (példa)
  - **Access validation a 00-ban — szolgáltatónként:**
    - GitHub: `gh auth status` + `gh repo view <repo>` → mindkettő `exit 0`
    - Bitbucket Cloud: `curl -u <user>:<token> https://api.bitbucket.org/2.0/repositories/<ws>/<repo>` → HTTP 200
    - Bitbucket on-prem: `curl -u <user>:<token> <api-url>/rest/api/1.0/projects/<key>/repos/<repo>` → HTTP 200
    - GitLab: `glab auth status` + `glab repo view <repo>` → mindkettő `exit 0`
    - Lokális: nincs validation
  - **Megállási szabály:** ha a validation sikertelen, az ágens nem zárja le a `conventions.md`-t — kéri a hibajavítást (token, URL, permissions), vagy másik szolgáltató választását, vagy lokális merge-re váltást.
  - **Következmény a 08-ra:** a 08 jelentősen egyszerűsödik. Beolvassa a `conventions.md` Merge stratégia szekcióját, és aszerint hajtja végre: PR létrehozás (a `code-review.md` legyen a PR description), vagy lokális `git merge --squash`. **A felhasználói megerősítés a merge előtt mindkét esetben kötelező marad** — ez független a D4-től, a 4.1 Kritikus pont alatt marad.
  - **Hatás a README/meta-promptra:** a PR-nyelvet ki kell venni / általánosítani „a `conventions.md` merge stratégiája szerint" formulára.

- [x] **D5 — `subagent-review.md` output szerkezete (Pozitív megfigyelések):** legyen vagy ne?
  - **A:** Legyen — a README ezt írja le. A `subagent-review.md`-t bővíteni kell.
  - **B (választott):** Ne legyen — a README-t kell javítani, a review jelentésben csak Must Fix + Suggestions szerepel.
  - **Érintett pontok a listán:** 1.8, 1.9, 2.3, 4.3
  - **Döntés indoklása:** A `code-review.md` akcióvezérelt artifact — a 06 visszalépéskor ezt parszolja a javításokhoz. A pozitív megfigyelések nem indítanak akciót, csak növelik a kontextust. A Suggestions szekció már most is tartalmazhat pozitív hangnemű elemeket („ez jól sikerült, de érdemes X-ben is alkalmazni").
  - **Következmény a README-re:** a „Pozitív megfigyelések" mondatot törölni kell a review subagent leírásából.

- [x] **D6 — `subagent-review.md` súlyossági besorolás:** milyen szintek?
  - **A (választott):** Két szint — Must Fix + Suggestions (jelenlegi).
  - **B:** Három szint — Blocker + Critical/Major + Suggestions, finomabb priorizálás a 06 visszalépéséhez.
  - **C:** Négy szint — Blocker + Critical + Major + Suggestions (közelebb a Sonar-besoroláshoz).
  - **Érintett pontok a listán:** 1.9
  - **Döntés indoklása:** A reviewer döntése bináris a 06 felé — blokkolja-e a merge-et vagy nem? Ezt két szint pontosan kifejezi. Finomabb besorolás bizonytalanságot okoz egy olcsóbb LLM-nek, és a 06 visszalépés sorrendje amúgy is a TDD `[RED]/[GREEN]` logikából jön, nem a review-ból.
  - **Következmény a `subagent-review.md`-re:** a határvonalat explicit kell definiálni. Legyen kimondva: *„Must Fix = a merge-et blokkolja (biztonsági rés, specifikáció-eltérés, konvenció-megszegés, hibás hibakezelés). Suggestion = nem blokkolja, csak javasolt javítás (refaktor, elnevezés, tisztaság)."*

- [x] **D7 — Commit message formátum egységesítése:** mi legyen a minta?
  - **A (választott — könnyített):** `cycle-NN: <fázis-szám>-<rövid név>` egységesen, a `T` prefix maga jelzi a 06-implement fázist, ezért ott nem kell explicit `06-` prefix.
  - **B:** `cycle-NN: <fázis név>` (szám nélkül) — egyszerűbb, de a fázis-szám-alapú rendezés elveszik.
  - **C:** Egyéb minta — javaslattal.
  - **Érintett pontok a listán:** 1.1, 2.3, 4.2
  - **Döntés indoklása:** A fázis-szám hasznos `git log --grep`-pel és sortrendezésben. A 02–04, 07 már stimmel — csak 00, 01, 08 igényel módosítást. A 06 task-commitja már most konzisztens (`T` betű = 06 fázis, `cycle-NN:` után).
  - **Végleges minta fázisonként (SK1 átsorszámozás után, 0–8):**
    - 00: `cycle-NN: 00-init` _(új — eddig nem volt commit a 00 végén)_
    - 01: `cycle-NN: 01-cycles` _(jelenleg: `01-init-cycle`)_
    - 02: `cycle-NN: 02-spec` _(változatlan)_
    - 03: `cycle-NN: 03-plan` _(változatlan)_
    - 04: `cycle-NN: 04-tasks` _(változatlan)_
    - **05: `cycle-NN: 05-analyze` (ÚJ FÁZIS, SK1 alapján)**
    - 06: `cycle-NN: T001 - <leírás>` _(eddig 05, taskonként)_
    - 07: `cycle-NN: 07-validate` _(eddig 06)_
    - 08: `cycle-NN: 08-merge - <ciklus cím>` _(eddig 07, jelenleg: `cycle-NN: <cím>`)_

---

## 1. Hiányosságok az egyes promptokban

### 1.1 `00-init-project.md`

- [x] **Hiányzik a `git commit` lépés** a `conventions.md` lezárásakor. Minden többi fázis (01–08) commit-tal zárul — ez kilóg a mintából.
  - Javaslat (D7 = A alapján): a "Lezárás" szekcióba illesszünk be egy `git add conventions.md && git commit -m "cycle-NN: 00-init"` lépést. _(Megj.: a 00 fázis nem ciklusspecifikus, de a `cycle-NN:` prefix az első ciklusra utal — alternatíva: `00-init` prefix nélkül, ha egyértelművé tesszük.)_
- [x] **A `conventions.md` „kész" jelölését explicit dokumentálni kell.** (D1 = B: puszta lét, státuszmező nélkül.) A `conventions.md` puszta léte a „kész" jelölés — ezt mindenhol explicitté kell tenni: a 00-ban kimondva, a 01–08-ban pedig csak létezés-ellenőrzésként.
- [x] **Nincs „Folytatás megszakított futás után" döntési fa.** Mit tegyen az agent, ha félig kitöltött `conventions.md`-t talál? A 04, 06, 07 fázisokban van ilyen szekció.
- [x] **Nincs lezárás előtti minőségellenőrzési lista.** A meta-prompt szerint minden fázisnak kötelező ellenőrzési listával kell zárnia. A 00 jelenleg csak azt mondja, hogy ha minden szekció kitöltött, jelezze a következő fázist.
- [x] **A Teszt keretrendszer sablon passzív, nem „ajánlott default + tisztázó kérdés" formátumú.** A 00 jelenleg fix értékeket pre-fillel (Playwright, pytest+httpx, docker compose), de nem mondja ki, hogy ezek **ajánlott default-ok**, és nem kérdezi meg aktívan a fejlesztőt, hogy elfogadja-e őket vagy mást szeretne. Ennek a sablonnak kell a single source of truth-ot megalapoznia a 03/07 számára.
  - Javaslat: a Teszt keretrendszer szekció (és a hasonló pre-fillelt szekciók, pl. Konténerek, E2E env script) legyen *„ajánlott — alternatívák: ..."* formátumú, és az agent kérdezzen rá explicit egy körben: *„A javasolt teszt stack: <default>. Megfelelő, vagy mást szeretnél?"*
- [x] **Új `## Merge stratégia` szekció és access validation lépés.** (D4 = C alapján.) A 00 prompt kérdezze meg a git szolgáltatót (GitHub / Bitbucket Cloud / Bitbucket Server / GitLab / Lokális), majd a választott módon **kipróbálja az access-t** a megfelelő parancstal (`gh auth status` + `gh repo view`, `curl` Bitbucket-re, stb.). Ha sikertelen, ne zárja le a `conventions.md`-t — kérje a token / URL / permissions javítását, vagy alternatív választást. A részletek (szekció szerkezet, validation parancsok szolgáltatónként, megállási szabály) a D4 döntésénél le vannak írva.

### 1.2 `01-add-cycles.md`

- [x] **Nincs előfeltételként a `conventions.md` ellenőrzése.** A 01 közvetlenül a 00 után jön, de nem ellenőrzi, hogy létezik-e a `conventions.md`. (D1 = B alapján: csak létezés-ellenőrzés szükséges, státuszmező nincs.) Ha a fájl nem létezik, jelezze, hogy térjenek vissza a 00-ra.
- [x] **Hiányzik dedikált „Folytatás megszakított futás után" szekció.** A 01 több módot és részben elkészült `roadmap.md`-t kezelhet, mégsem mondja meg, hogyan folytasson az agent félig megírt roadmap, részben létrehozott ciklusmappa vagy félbeszakadt rekonstrukció esetén.
- [x] **A C. mód — Roadmap rekonstrukció túl erősen automatikus.** A prompt szerint a 01 létrehozhatja vagy felülírhatja a `specs/roadmap.md`-t, majd megerősítés, validáció és commit nélkül `Kész` státuszra állítja. Ez kilóg az A/B mód és a többi fázis user confirmation + commit mintájából.
- [x] **Nincs `git status --short` előellenőrzés.** A 01 roadmapet ír és ciklusmappát hoz létre; ha commitálatlan változások vannak, nem derül ki induláskor, hogy a fázis milyen munkafára épít.
- [x] **B. módban a `---` elválasztó beszúrási logikája nem fed le edge case-eket.** Mi van, ha a `roadmap.md` utolsó nem-üres sora nem `---`? Javaslat: *„Ha a roadmap.md utolsó nem-üres sora nem `---`, először szúrj be egyet, mielőtt az új ciklust hozzáfűznéd."* Vagy egységesen: minden ciklus után kötelezően `---` kerüljön (A, B, C módok is generálják).

### 1.3 `02-write-spec.md`

- [x] **Hiányzik dedikált „Folytatás megszakított futás után" szekció.** Az iterációs szabályok 5. pontjának végén egy mondat utal rá: *„Minden iteráció indítható új kontextussal: elég a `spec.md` és a `spec-questions.md` aktuális állapota + ez a prompt."* — de ez nem dedikált szekció, és nem döntési fa formátumú. A 04, 06 fázisokban szigorúbb a kezelés.
- [x] **Nincs `git status --short` előellenőrzés** a fázis indításakor. A 06-ban van ez, és különösen indokolt itt is, mert a 02 branchet hoz létre (`git checkout -b feature/cycle-<cycle-name>`) — ha vannak commitálatlan változtatások, azok átkerülhetnek az új branch-re.
- [x] **A státuszkezelés az iterációs szabályok 6. pontjában van elrejtve**, nem külön szekcióban. Olvashatóság szempontjából rossz — a 03, 04, 06, 07 fázisoknak van dedikált „Státusz kezelés" szekciójuk.

### 1.4 `03-write-plan.md`

- [x] **Hiányzik dedikált „Folytatás megszakított futás után" szekció.** A „Munkafolyamat 5. pont"-ban van rá utalás (*„Újraindítás új kontextusban..."*), de nincs döntési fa formátumban (mint a 06-ban), és nincs külön szekcióként.
- [x] **A „Spec kritika — a plan írás során" szekció passzív megfogalmazású.** Felsorol 3 kérdést („Tedd fel magadnak..."), de nincs explicit checklist amit minden komponensre végig kell járni. Egy olcsóbb LLM könnyen kihagyja, mert nincs „ellenőrizd minden komponensnél" típusú akció-utasítás.
- [x] **A `plan-questions.md` „Kötelező első kérdés" (E2E teszt stratégia) mélyen el van rejtve** a Munkafolyamat 1. pontjában, egy hosszú bekezdés közepén. Ez fontos kötelező lépés — érdemes lenne saját szekciót adni neki vagy legalábbis kiemelt blockquote-ot.
- [x] A Schema Artifaktumok kezelése (artifact típusok + Workflow) nem mondja meg, **mit tegyen az agent, ha az artifact generálásához nem áll rendelkezésre elég információ a spec-ből**. Nyitott kérdésnek kell felvenni? Nincs leírva.
- [x] **A 03 forrásfájl-olvasási szabályát át kell írni a D2 = A alapján.** A 03 jelenlegi szövege (*„csak a spec `Hivatkozott fájlok` szekciójában szereplő forrásfájlokat olvasd be"*) ellentmond a 02 tiltásnak. Helyette: a 03 **önállóan azonosítja** a forrásfájlokat (subagent / közvetlen kódvizsgálat), és a spec `Hivatkozott fájlok` szekciójából **csak dokumentációs anyagokat** (README, OpenAPI, séma) olvas be. A 02 jelenlegi tiltó szabálya marad.
- [x] **A tesztelési technológiák hardcode-olva vannak konkrét tool-nevekkel és tool-specifikus API-kkal.** A plan struktúrában fixen szerepel *„Frontend tesztek: Playwright"*, *„Backend tesztek: pytest + httpx"*, *„Python alapú env script (`start_env.py`)"*, és a 296. sor egy **Playwright-specifikus API-ra** (`page.route()`) épülő minőségellenőrzési pontot ír elő. Ez akkor is gond, ha a `conventions.md` ezeket default-ként ajánlja: ha a fejlesztő a 00-ban Cypress-t választott, a 03 ellentmond neki.
  - Javítási irány **(„ajánlás + hivatkozás" séma)**:
    1. **Konkrét tool-nevek** (Playwright, pytest, httpx) helyett a `conventions.md` „Teszt keretrendszer" szekciójára hivatkozzon. Pl. *„Frontend tesztek: ha van web komponens, a conventions.md által megadott browser E2E eszköz"*.
    2. **Tool-specifikus API-k** (`page.route()`) helyett viselkedési követelmény. Pl. *„browser E2E teszt, amely network mocking nélkül valódi HTTP kérést küld"*.
    3. **Fájlnév-szintű hivatkozások** (`start_env.py`, `docker-compose.e2e.yml`) maradhatnak, ha a 00 ezeket konkrét névvel ajánlja default-ként — de a 03 hivatkozza, hogy „a conventions.md által megadott env indító script".

### 1.5 `04-write-tasks.md`

- [x] **Nincs explicit előfeltételként a `spec-questions.md` és `plan-questions.md` lezártsága.** A `plan.md` `Task írásra kész` státuszban benne van implicit, hogy minden kérdés zárt — de az ellenőrzés nem külön mondva.
- [x] **A „Megállási szabályok" rövid (3 pont)**, míg a 03-ban gazdag. Hiányzó esetek:
  - Mi van, ha a plan `Tervezett módosítások` egy bejegyzéséhez semmilyen taskot nem tudsz megfogalmazni?
  - Mi van, ha egy task csak feltételesen végezhető el (pl. függ egy nem létező fájltól)?
- [x] **A `TLAST` és `TREG` sorszámozási konvenció nincs explicit definiálva** — a példa mutatja (`TLAST1`, `TREG1`), de hogy hány lehet, milyen sorrendben, mit jelent — implicit.
- [x] **A „kis méretű task" határértéke homályos.** A 04 azt mondja *„legfeljebb 1-2 fájl"* és *„3 vagy több → bontsd"* — de mi a teendő pont 2-3 fájlnál, vagy 2 fájl + összetett logika esetén? Finomítás: *„Egy task akkor önálló commitra alkalmas, ha (a) legfeljebb 2 fájlt érint, ÉS (b) egyetlen logikai változást fed le. Ha 3+ fájl VAGY több független logikai változás, bontsd."*

### 1.6 `06-implement.md`

- [x] **Hiányzik a klikkelhető markdown link szabály** a válaszok végén (02, 03, 04-ben van). A 06 is kér néha megerősítést / jelez taskok kész állapotáról — ott is hasznos lenne.
- [x] **A `code-review.md` beolvasási utasítás eldugva** a Kontextus betöltési szabályok 2. pontjába. A 08-ból visszalépő flow szempontjából ez kritikus — érdemes lenne főhelyre tenni, esetleg külön „08-ból visszatérés" szekcióba.
- [x] **Nincs explicit utasítás arra, mi a teendő, ha a `tasks.md`-ben egy task nincs csoportba sorolva** (`##` blokk nélkül). A fejezet-szintű előfeltétel ellenőrzés (3. szabály) feltételezi, hogy minden task valamelyik `##` blokkba esik.
- [x] **A „Visszalépés kódellenőrzésből (08)" külön a 2. pontban van**, de nincs összekötve a „Folytatás megszakított futás után" döntési fával. Két forrásból érkezhet visszalépés (07 vagy 08) — a dokumentum nem strukturálja egyértelműen.
- [x] **Az „Új komponens README" szekció (146–156. sor) duplikálja a 03-ban szereplő README követelményt.** Nincs harm benne, de nem világos, hogy ez új követelmény-e vagy emlékeztető.
- [x] **A taskonkénti commit nem mondja ki, hogy a `tasks.md` checkbox frissítése is commitolandó.** Így előállhat olyan állapot, hogy a kód commitolva van, de a task `[x]` jelölése vagy a státuszváltás nincs rögzítve.
- [x] **A végső `Validálásra kész` státusz commitja nincs explicit kimondva.** Az implement végén a `tasks.md` státusza módosul, de nincs külön lezáró commit szabály erre az állapotváltozásra.
- [x] **Portütközésnél az ideiglenes konfigurációmódosítás sorsa nincs szabályozva.** A prompt engedi átmenetileg átírni portokat/configot, de nem mondja ki, hogy ezt vissza kell állítani vagy legalább nem szabad véletlenül commitolni.

### 1.7 `07-validate.md`

- [x] **Nincs `git status --short` ellenőrzés az indítás előtt** (06-ban van).
- [x] **FAIL ágon nincs explicit git commit** a `tasks.md` és `validate-decision.md` frissítéséről. PASS ágon van. Egy olcsóbb LLM nem fogja commitolni, és így a visszalépés utáni állapot nem rögzített.
- [x] **A PASS-előtti megerősítés-mentesség legyen explicit dokumentálva.** (D3 = B alapján: szándékos automatikus PASS.) A 07 Státusz kezelés / PASS szekciója elején kerüljön be egy mondat: *„A PASS automatikus, mert determinisztikus ellenőrzéseken alapul (tesztek + Sonar + DoD). Felhasználói megerősítés nem szükséges — az eredmény a `validate-decision.md`-ben ellenőrizhető."* Ez nélkül egy olcsóbb LLM hibásan próbálhat megerősítést kérni.
- [x] **A `test-report/` mappa létrehozásának utasítása csak zárójeles megjegyzésben szerepel** (106. sor: *„ha a fájl nem létezik, a `test-report/` mappával együtt hozd létre"*). Önálló lépésként kellene kiemelni.
- [x] **Az „Ismételt hibák korai ellenőrzése" szekcióban (34–36. sor) ellentmondás van**: *„jelezd, de folytasd a validálást a válasz bevárása nélkül"* — más helyeken a megállási szabályok mindig várnak választ. Egy olcsóbb LLM-nek ez összezavaró.
- [x] **A validáció hardcode-olt tesztelési technológiákat tartalmaz.** Unit/integration/e2e futtatásnál konkrét mappákat (`test/unit/`, `test/integration/`, `test/e2e/`) és eszközöket említ (pytest/httpx, Playwright jellegű E2E, `start_env.py`), és a Sonar futtatás is konkrét Python script-path-ra (`test/test-tools/generate_sonar_report.py`) hivatkozik. Ezek a `conventions.md`-ben rögzített default-ok kell, hogy legyenek, és a 07 hivatkozza vissza őket — nem ismételje meg.
  - Javítási irány **(„ajánlás + hivatkozás" séma)**: a 07 *„a conventions.md által megadott unit/integration/E2E teszt eszközzel futtasd"* megfogalmazást használjon. A konkrét tool-választást a 00 ajánlja default-ként, a fejlesztő a `conventions.md`-ben rögzíti, és a 07 onnan dolgozik.
- [x] **Portütközésnél az ideiglenes konfigurációmódosítás sorsa itt sincs szabályozva.** A 07 is engedi átmeneti port/config módosítást, de nem mondja ki, hogy a validáció végén vissza kell állítani vagy nem szabad commitolni.

### 1.8 `08-review-and-merge.md`

- [x] **Nincs `git status --short` ellenőrzés.**
- [x] **Nincs explicit felhasználói megerősítés a `master`-be merge előtt.** Ez nagy kockázat — a merge `master`-re destruktív, megerősítés nélküli akció. A `git branch -D feature/cycle-<cycle-name>` ugyanígy (force delete).
- [x] **Nem kezel merge conflict-ot rendesen** — csak egy zárójeles utalás van rá (*„Megjegyzés: Ha a merge során ütközések lépnének fel, azokat oldd fel, végezd el a commitot, és jelezd a felhasználónak"*). Ez nem elég részletes — egy olcsóbb LLM nem tudja eldönteni, mit jelent „feloldani".
- [x] **Nincs jelzés arra, mi történjen, ha a subagent nem fut le** vagy nem készít riportot (`code-review.md` hiányzik).
- [x] **A `subagent-review.md` output és a README.md leírása ellentmondanak.** (D5 = B alapján rendezve: a `subagent-review.md` marad Must Fix + Suggestions, a README-ből törölni kell a „Pozitív megfigyelések" mondatot.)
- [x] **Nem világos, mi a teendő, ha a review jelentés tartalmaz `[ ]` checkboxokat a Suggestions szekcióban.** A logika csak a Must Fix szekciót ellenőrzi.
- [x] **A dokumentációfrissítés a review után történik, de nincs utána új ellenőrzési pont.** A 08 előbb lefuttatja a review-t, majd módosítja a `docs/architecture.md`-t és README-ket. Ezek a változások így review/validáció nélkül kerülhetnek a squash merge-be, hacsak nincs külön újraellenőrzés vagy commit-szabály.
- [x] **A 08 merge logikáját át kell írni konvenció-vezéreltre.** (D4 = C alapján.) A 08 olvassa be a `conventions.md` Merge stratégia szekcióját, és aszerint hajtsa végre:
  - **Lokális** → jelenlegi `git merge --squash` master-re + `git branch -D` (felhasználói megerősítés után — lásd 4.1).
  - **GitHub / Bitbucket / GitLab** → PR létrehozás (`gh pr create` / `glab mr create` / Bitbucket API), a `code-review.md` legyen a PR description, target branch a konvencióból. A felhasználói megerősítés a merge előtt itt is kötelező.
- [x] **A roadmap frissítése nincs kezelve.** A README részletes diagramja „Roadmap státusz frissítés"-t ír a merge lépéshez, de a 08 promptban nincs ilyen teendő. Dönteni kell, hogy kell-e cikluslezárást rögzíteni a roadmapben.

### 1.9 `subagent-review.md`

- [x] **Túl rövid (21 sor) a fontosságához képest.** Egy reviewer-nek konkrét keretrendszer kellene.
- [x] **Nincs explicit utasítás arra, hogy a Must Fix bejegyzések tartalmazzanak file:line referenciát**, hogy a 06-ba visszalépő agent meg tudja találni a problémát.
- [x] **Nincs leírva, mit tegyen, ha a diff túl nagy / nem érti.** Megáll? Részleges review-t készít?
- [x] ~~**Nincs „Pozitív megfigyelések" szekció**, pedig a README.md említi.~~ (D5 = B alapján törölve: a szekció szándékosan nincs; a README-t kell javítani, nem a promptot.)
- [x] **A Must Fix vs Suggestion határvonal nincs explicit definiálva.** (D6 = A alapján: maradunk a két szintnél, de a határvonalat ki kell mondani.) Legyen a `subagent-review.md`-ben: *„Must Fix = a merge-et blokkolja (biztonsági rés, specifikáció-eltérés, konvenció-megszegés, hibás hibakezelés). Suggestion = nem blokkolja, csak javasolt javítás (refaktor, elnevezés, tisztaság)."*
- [x] **A `code-review.md` struktúrája nincs szabványosítva — gépileg parszolhatónak kell lennie.** A `subagent-review.md` írja elő a Must Fix bejegyzések fix formátumát: `- [ ] <file>:<line> — <probléma rövid leírása>`. Ez biztosítja, hogy a 06-ba visszalépő agent gépiesen tudja parszolni a javítandó tételeket. Az 1.9 első pontjával (file:line referencia) összefüggő, de explicit formátum-szabályt is be kell vezetni.
- [x] **Nincs leírva, mit jelent „spec eltérés"** — a spec.md beolvasása nincs előírva a bemenetek között (csak `plan.md`-é). Inkonzisztens.

---

## 2. Inkonzisztenciák a promptok között

### 2.1 Strukturális inkonzisztenciák

| Téma | Hol van | Hol hiányzik | Megjegyzés |
|------|---------|--------------|------------|
| `git status --short` előellenőrzés | 06 | 00, 01, 02, 03, 04, 05, 07, 08 | A 02 branchet hoz létre, ott különösen indokolt; ha tiszta munkafa a cél, minden író/commitoló fázisnál egységesen kell |
| `git commit` lezáráskor | 01, 02, 03, 04, 06 (taskonként), 07 (PASS), 08 (squash) | 00, 01 C. mód, 06 végső státuszváltás, 07 (FAIL ág) | A 07 FAIL ágon a tasks.md módosul, de nincs commit; a 06-ban a task checkbox/státusz frissítések commitolása sem explicit |
| Felhasználói megerősítés státuszváltás előtt | 02, 03, 04 | 08 (merge) | A 07 PASS-nál D3 = B alapján szándékosan nincs (determinisztikus). A 08 master merge megerősítés nélkül viszont valódi kockázat. |
| Klikkelhető markdown link a válasz végén | 01, 02, 03, 04 | 05, 06, 07, 08 | Konzisztencia hiánya |
| „Egy kérdés egyszerre" explicit szabály | 00, 01, 02, 03 | 04, 05, 06, 07, 08 | A 04+ fázisok is feltehetnek kérdést |
| Dedikált „Folytatás megszakított futás után" szekció | 04, 07 | 00, 01, 02, 03, 05, 06 (csak részben), 08 | A 06 döntési fája jó minta lenne mindenhol |
| Fájl elérési út formátum (relatív, `file://` tilos) | 02, 03, 04 | 00, 01, 05, 06, 07, 08 | A 00-ben még abszolút utak példák szerepelnek |
| `questions.md` kérdés-nyilvántartó | 02, 03 | 04, 05, 06, 07, 08 | Nincs indokolva, miért csak a 02–03-ban |
| Minőségellenőrzési lista | 02, 03, 04 | 00, 05, 06, 07, 08 (csak részben) | A 00 és 06 nem zár dedikált checklisttel |

### 2.2 Stílusbeli inkonzisztenciák

- [x] **A 02–03 fázis prózai**: „Iterációs szabályok" alatt rejti a státuszkezelést, megszakítást, lezárást. A 04, 06, 07 dedikált szekciókat használ. Olcsóbb LLM-nek az utóbbi struktúra sokkal könnyebben követhető.
- [ ] **A blockquote és kiemelés használata eltér**: a 03 sok IMPORTANT/CAUTION blokkot használ (`> [!IMPORTANT]`), a többi prompt csak sima blockquote-ot vagy bold-ot.
- [ ] **A „Megállási szabályok" pozíciója eltér**: néhol a fázis közepén, néhol a végén.

### 2.3 Tartalmi inkonzisztenciák

- [x] **README.md vs `subagent-review.md`** (D5 = B alapján rendezve: a `subagent-review.md` marad Must Fix + Suggestions, a README-ből törölni kell a „Pozitív megfigyelések" mondatot.)
- [x] **README.md bemenet-megnevezés eltér**: a 02-höz a „Új spec" promptban backticket használ (`` `specs/...` ``), a 03-hoz `@`-jelölést (`@prompts/...`). Vegyes — érdemes egységesíteni.
- [x] **README.md-ben elütés/rossz fájlnév van:** a magas szintű diagram `task.md`-t ír, miközben a workflow fájlja `tasks.md`.
- [x] **README.md magas szintű diagramja rossz visszalépési fázist mutat:** 07 FAIL és 08 review FAIL esetén a diagram 04-re mutat, miközben a részletes flow és a promptok szerint a `tasks.md` frissítése után 06-ban folytatódik az implementáció.
- [x] **README.md review Suggestions kezelése eltér a 08 prompttól:** a README szerint kisebb észrevételt a 08-as agent direktben javít, a 08 prompt viszont csak a Must Fix checkboxokat kezeli, a Suggestions sorsát nem definiálja.
- [x] **A kattintható chat-linkek és a dokumentumba írt fájlutak szabálya keveredik.** A 01–03 promptok `file://` példákat adnak a válasz végére tett linkekhez, miközben a generált dokumentumokban relatív utak és `file://` tiltás szerepel. Ezt két külön szabályként kellene megfogalmazni.
- [x] **Commit message formátum egységesítése (D7 = A + SK1 átsorszámozás):**
  - **Változatlan:** 02, 03, 04, taskonkénti T-prefix (most már a 06 fázisban).
  - **Új commit (eddig nem volt):** 00: `cycle-NN: 00-init`
  - **Frissítendő prefix:**
    - 01: `01-init-cycle` → `01-cycles`
    - 08: `cycle-NN: <cím>` → `cycle-NN: 08-merge - <ciklus cím>` (eddig 07)
  - **Új fázis commit:** 05: `cycle-NN: 05-analyze` (SK1)
  - **Átsorszámozott fázis commit:** 07: `cycle-NN: 07-validate` (eddig `06-validate`)
- [x] **A 03 plan struktúra `Schema Artifaktumok` táblázatának státuszai** (`Piszkozat` | `Review Required` | `Reviewed`) nem konzisztensek a `plan.md` saját státuszaival (`Piszkozat` | `Nyitott kérdések vannak` | `Task írásra kész`). Két státusz-rendszer egyetlen dokumentumban — könnyen összekeverhető. _(Az egységes `Kész` lifecycle-modell — lásd 6.4 és 4.2 — ennek a dokumentumközi részét rendezi; a 03-on belüli kettős táblázat-státusz külön vizuális szétválasztást igényel, lásd 4.3.)_
- [x] **A 02 és 03 ellentmond a `Hivatkozott fájlok` tartalmáról.** (D2 = A alapján rendezve: 02 jelenlegi tiltása marad, 03 önállóan azonosítja a forrásfájlokat.)
- [x] **A `conventions.md` használata nincs egységesen érvényesítve:** a README szerint 02–08 hivatkozik rá, de a promptokban csak részlegesen jelenik meg explicit beolvasási vagy kapuszabályként.
- [x] **Teszttechnológia és indítóscript konvenció ütközik:** a 00 sablonja Playwright/pytest/httpx default-okat tartalmaz, de a *„projektfüggő"* nyelvezetet használ, miközben a 03/07 konkrét nevekkel hivatkozza ezeket. A prompt-család **általános, default-okkal proaktívan ajánló** szándékot követ (lokális fejlesztői használat) — ezt a szándékot explicit kell tenni a 00-ban, és a 03/07-nek a `conventions.md`-re kell hivatkoznia a konkrét tool-név ismétlése helyett.
- [x] **PR vs lokális merge fogalom keveredik a metában és a README-ben.** (D4 = C alapján rendezve: konvenció-vezérelt merge. A meta/README PR-nyelvét általánosítani kell „a `conventions.md` Merge stratégiája szerint" formulára — nem fix flow, hanem projektfüggő.)

### 2.4 Fázis-átmenetek inkonzisztens leírása

- [x] **A 02 lezárás-üzenete** ad konkrét futtatható promptot a következő fázishoz:
  ```
  Kövesd a `prompts/03-write-plan.md` utasításait.
  Input: ...
  ```
  **A 07 PASS üzenete** viszont csak annyit mond: *„Folytathatjuk a 8. lépéssel: review & merge (08)."* — nincs konkrét futtatható prompt.
- [x] **A 08-nak nincs „Következő ciklus" indító üzenete** — csak annyi: *„Megkezdhető a következő ciklus spec fázisa (02)."* Lehetne explicit prompt mintát adni.
- [x] **A 01 C. mód átmenete túl rövidre zár:** rekonstrukció után automatikusan B. módba lép, de nincs user review, minőségellenőrzés, commit és explicit lezárási üzenet a rekonstruált roadmapre.
- [x] **A 08 dokumentációs módosításai után nincs visszacsatolási lépés:** ha a review már lefutott, majd a 08 módosítja az architecture/README fájlokat, nem egyértelmű, hogy kell-e új review, validáció, vagy legalább célzott dokumentációs ellenőrzés.

---

## 3. Olcsóbb LLM megfelelőség

### 3.1 Erősségek (jól működnek olcsóbb LLM-mel is)

- ✅ **A 06 „Döntési fa a folytatáshoz"** (numbered, expliciten kódba ágyazva) — kiváló minta.
- ✅ **A 04 „Túl bőbeszédű | Jó" példa táblázat** — kiváló, ezt mindenhol érdemes lenne alkalmazni.
- ✅ **TDD jelölés `[RED]/[GREEN]/[CHECK]`** — konkrét és világos.
- ✅ **PASS / FAIL séma** a 07-ban — egyértelmű végeredmény.
- ✅ **A 01 „mód detektálás" döntési fája** (A/B/C mód) — explicit és követhető.

### 3.2 Gyenge pontok olcsóbb LLM-nek

#### 3.2.1 Túl hosszú / sűrű promptok

- [x] **A 03-write-plan.md ~390 soros**, 7+ szekcióval, 3 validációs ciklussal, 5 megállási szabállyal. Egy Haiku 4.5 könnyen elveszik benne. **Ez a legnagyobb kockázat.**
  - Javaslat: cheat sheet a prompt elején (1-soros összefoglaló minden szekcióhoz).
- [ ] **A 04 minőségellenőrzési lista 5 csoportban (A–E), 15+ ponton keresztül futtatandó.** Sok információ, könnyen átsiklik felette.

#### 3.2.2 Implicit megkülönböztetések, határvonalak

- [x] **„A spec csak viselkedést ír le, nem implementációt"** — egy olcsóbb LLM nehezen ítéli meg a határvonalat példák nélkül.
  - Javaslat: konkrét „spec-ben elfogadható" vs „plan-be való" példák.
- [x] **„Ne találd ki magad" szabály sokszor előfordul**, de a határvonal homályos. Mikor szabad alapértelmezett értéket választani vs mikor kötelező kérdezni? Példák segítenének.
- [x] **„Légy aktívan kritikus a spec-cel szemben" (03)** — viselkedési instrukció, amit az olcsó modellek hajlamosak figyelmen kívül hagyni. Checklist hiányzik.
- [x] **Forrásfájl vs dokumentációs hivatkozás határvonala keveredik.** (D2 = A alapján rendezve: spec csak dokumentációs anyag, plan azonosítja a forrásfájlokat.) Az olcsóbb LLM számára explicit példák kellenek a 02-ben (mi mehet a `Hivatkozott fájlok`-ba) és a 03-ban (hogyan azonosítson forrásfájlt subagent-tel).
- [x] **A „ajánlott default" és a „kötelező eszköz" határvonala nincs explicit kimondva.** (Átfedésben a 2.3 „Teszttechnológia és indítóscript konvenció ütközik" ponttal — együtt rendezendő. A javítás iránya: a 00 mondja ki, hogy „ezek ajánlott default-ok, a fejlesztő tisztázza, és innentől a `conventions.md` a single source of truth"; a 03/07 hivatkozzon vissza, ne ismételje a tool-nevet.)

#### 3.2.3 Vizuális/strukturális zsúfoltság

- [ ] **A „Szigorú konténerizációs szabály" (03)** blockquote-ban van, sok IMPORTANT/CAUTION jelzéssel — vizuálisan zsúfolt, könnyen átsiklik felette.
- [ ] **Hosszú minőségellenőrzési listák bullet-pontokkal**: a 03-ban 15+ pont, ahol a sorrend és az egymásra épülés nem mindig egyértelmű.
  - Javaslat: számozott, kötelezően kipipálandó struktúra.

#### 3.2.4 Komplex elágazások / állapotgép

- [ ] **A `Reviewed` / `Review Required` artifact státuszok** kezelése a 03-ban háromféle workflow-ban (Schema Artifaktumok) — túl sok elágazás egy szekcióban.
- [ ] **A 07 PASS/FAIL elágazás + 3-próba szabály + ismételt hibák korai ellenőrzése** — három különböző állapotgép egymásra rakódva. Olcsóbb LLM-nek nehéz követni.
- [ ] **Több fájl egyidejű menedzselése** (`spec.md` + `spec-questions.md`, `plan.md` + `plan-questions.md`) — a kettő szinkronizálása komplex. Egy olcsóbb LLM elfelejtheti az egyiket frissíteni.
- [x] **A 01 A/B/C módja jó döntési fa, de nincs lezárási állapotgéppel összekötve.** Különösen a C módnál könnyen kimarad a review/commit/confirmation.
- [x] **A 08 review → dokumentációfrissítés → merge sorrendje több állapotot kever.** Egy olcsóbb LLM könnyen úgy tekinti, hogy a review után már minden merge-elhető, pedig a dokumentáció még változhat.

#### 3.2.5 Rejtett szabályok

- [x] **A `⟂ Tkkk` jelölés** szinte rejtetten van bevezetve (04: egy sor, 06: egy szabály). Az olcsóbb LLM hajlamos figyelmen kívül hagyni.
  - Javaslat: kiemelt példa mindkét promptban.
- [x] **A `TLAST` és `TREG` sorszámozási konvenció** csak példában szerepel — definíciója nincs.

#### 3.2.6 Tárgyilagos „STOP" kulcsszó hiánya

- [x] Sok helyen „javítsd a hibát" megfogalmazás van **„STOP — vissza X fázisba"** helyett. Olcsóbb LLM-nek explicit STOP szignálok kellenek.
- [x] **A „Megállási szabályok" szekciók** néhol nem mondják meg expliciten, hogy „STOP", csak hogy „állj meg és jelezd". A különbség egy olcsóbb LLM-nek nem feltétlenül világos.
- [x] **Az ideiglenes módosításoknál nincs „STOP / NE COMMITOLD" jelzés.** Portütközésnél átmeneti config-változás engedélyezett, de nincs erős tiltás a véletlen commit ellen.

### 3.3 Konkrét javítási irányok olcsóbb LLM-re

1. **Cheat sheet** a prompt elején minden fázishoz (1-soros összefoglaló minden szekcióhoz).
2. **Számozott checklist** mindenhol a bullet-pontok helyett a minőségellenőrzési listákban.
3. **Példák minden szabálynál** — különösen „rossz vs jó" formátumban (a 04 mintát követve).
4. **Rövidebb szekciók**, vagy bontás több prompt-ra (pl. a 03 felbontása).
5. **STOP kulcsszó** a megállási szabályoknál, hogy ne sodródjon tovább.
6. **Decision flow chart** szövegesen (mint a 06-ban) minden komplex döntéshez.
7. **Explicit „ELLENŐRIZD" akció-utasítások** a passzív „kérdezd magadtól" helyett.
8. **NE COMMITOLD / ÁLLÍTSD VISSZA jelzés** minden átmeneti config- vagy portmódosításnál.
9. **Projektkonvencióból vezetett tool-választás** minden tesztelési és indítási szabálynál.

---

## 4. Prioritás szerinti összegzés

### 4.1 Kritikus (azonnali javítás javasolt)

- [x] **08-as fázis: master-be merge előtti felhasználói megerősítés hiánya.** Destruktív, megerősítés nélküli akció.
- [x] **07 FAIL ágon nincs git commit** — visszalépés után a változtatások nem rögzítettek.
- [x] **subagent-review.md hiányos** (file:line, „Pozitív megfigyelések" diszkrepancia a README-vel, blocker súlyossági besorolás).
- [x] **00-init-project.md hiányzó git commit.** (D1 = B alapján státuszmező nem kell, csak a commit hiánya marad valódi probléma.)
- [x] **07 ellentmondás a „korai hibaellenőrzés" szabályban** (jelez, de nem vár választ — vs többi megállási szabály).
- [x] **01 C. mód roadmap rekonstrukciója megerősítés/validáció/commit nélkül állít `Kész` státuszt.** Ez felülírhat fontos tervezési állapotot.
- [x] **02/03 ellentmondás a spec `Hivatkozott fájlok` tartalmáról.** (D2 = A alapján rendezve, lásd a megfelelő pont.) Ez közvetlenül rossz plan-kontextust eredményezhet — kritikus, mert a 03 jelentős átírást igényel.

### 4.2 Fontos (második körben)

- [x] **06-ban a `tasks.md` checkbox/státusz frissítések commitolása nem explicit.** A kód és a workflow állapot szétcsúszhat. (Áthelyezve 4.1-ből: nem destruktív, csak inkonzisztencia.)
- [x] **08-ban a review után történik dokumentációmódosítás új ellenőrzés nélkül.** Review-olatlan változás kerülhet a master merge-be. (Áthelyezve 4.1-ből: kockázat, de nem adatvesztés. A megoldás: célzott dokumentációs konzisztencia-ellenőrzés merge előtt, nem új subagent review.)
- [x] **„Megszakított futás" szekció** egységesítése — minden promptra dedikált szekció + döntési fa (06 mintájára).
- [x] **Felhasználói megerősítés és klikkelhető link szabály** egységesítése (02–04 mintájára) a 05, 06, 07, 08-ra.
- [x] **Commit message formátum egységesítése (D7 = A):** csak a 00, 01 és 08 igényel módosítást. Végleges minta a D7 döntésénél le van írva.
- [x] **03-write-plan.md tagolás javítása**: cheat sheet, kiemelt E2E teszt stratégia kérdés, számozott checklist.
- [x] **Példák hozzáadása** a határvonal-szabályokhoz (spec vs plan, „ne találd ki" szabály).
- [x] **`conventions.md` kapuszabály és beolvasási szabály egységesítése** 01–08 között.
- [x] **Egységes `Kész` státusz-lifecycle bevezetése** (lásd 6.4): minden dokumentum a fázis-specifikus záró-státuszáról `Kész`-re lép, amint a downstream fázis átveszi (spec→03, plan→04, tasks→05/06). A `<fázis-specifikus> → Kész` átmenetet explicit rögzíteni kell az érintett promptokban, hogy a 08 prerequisites egységesen `Kész`-t várhasson. Egyúttal rendezi a 2.3 kettős státusz-rendszer pontját is.
- [x] **Teszttechnológiai szabályok „ajánlás + hivatkozás" sémára alakítása**:
  - **00 promptban**: a Teszt keretrendszer (és hasonló) szekció legyen explicit *„ajánlott default — alternatívák: ..."* formátumú, és az agent kérdezzen rá aktívan a fejlesztőnél. A prompt-család célja, hogy modern, korszerű eszközöket (Playwright, pytest+httpx, Podman, Python env script) sugalljon — ez maradjon, csak legyen kimondva, hogy ajánlás.
  - **03/07 promptokban**: a konkrét tool-nevek (Playwright, pytest, httpx) helyett `conventions.md` hivatkozás. Tool-specifikus API-k (pl. `page.route()`) viselkedési követelménnyé általánosítása (*„network mocking nélkül"*).
  - **Cél**: a `conventions.md` egyetlen forrásként rögzítse a tool-választást; a 00 ajánlja proaktívan a default-okat; a 03/07 sose mondjon ellent a fejlesztő döntésének.
- [x] **Ideiglenes port/config módosítások rollback/commit tiltásának rögzítése** 06 és 07 promptban.
- [x] **Merge stratégia konvenció-vezéreltté tétele (D4 = C):**
  - **00 prompt:** új `## Merge stratégia` szekció a `conventions.md` sablonjában, access validation lépéssel.
  - **08 prompt:** olvassa be a Merge stratégiát, és aszerint hajtsa végre (lokális vagy PR — GitHub / Bitbucket / GitLab).
  - **README és meta:** a PR-nyelvet általánosítani „a `conventions.md` Merge stratégiája szerint" formulára.
- [x] **SK2 implementálása (02-write-spec):** a 10-kategóriás ambiguitás-vizsgálat segédlet (`## Ambiguitás-vizsgálat — kérdés-keresési sablon`) beépítése. Iránymutatás, nem kötelezettség — csak ott kérdés, ahol valódi ambiguitás. Részletek az SK2 döntésénél.
- [x] **SK4 implementálása (03-write-plan):** Constitution Check egy-soros ellenőrzési pont a „Minőségellenőrzés — plan lezárása előtt" szekcióban (plan-döntések ↔ `conventions.md`). Kis eltérés → `plan-questions.md`; súlyos eltérés → STOP, vissza 02/00. Részletek az SK4 döntésénél.

### 4.3 Hasznos (harmadik körben)

- [x] **README.md vs `subagent-review.md` szinkronizálása.** (D5 = B alapján: a README-ből törölni a „Pozitív megfigyelések" mondatot.)
- [x] **README.md bemenet-jelölés egységesítése** (backtick vs @-jelölés).
- [x] **README.md diagramok és fájlnevek javítása** (`task.md` → `tasks.md`, 07/08 FAIL visszalépés 06-ra, roadmap frissítés eldöntése).
- [x] **`TLAST` és `TREG` konvenciók explicit definiálása.**
- [x] **`⟂ Tkkk` párhuzamosítás jelölés kiemelése** példával.
- [x] **A 03 `Schema Artifaktumok` szekció kettős státusz-rendszer** vizuális szétválasztása.
- [x] **A 08 következő ciklus indító prompt minta** hozzáadása (mint a 02–04 és 06-ban).
- [x] **`tanulságok.md` áthelyezése `prompts/` → `docs/`.** A fájl nem prompt, hanem előadás-vázlat / lessons learned dokumentum. A `prompts/` mappa szemantikája tisztább marad így. (Elvégezve: `git mv prompts/tanulságok.md docs/tanulságok.md`.)

---

## 5. Spec-kit ihlette új pontok

Az alábbi pontok a [github/spec-kit](https://github.com/github/spec-kit) projekt promptjainak áttekintése után kerültek a listára. Egyenként megyünk át rajtuk — minden pontnál eldöntjük, hogy felvesszük-e a fejlesztési listára, és ha igen, milyen formában.

- [x] **SK1 — `analyze` jellegű kereszt-fázisos konzisztencia ellenőrzés (új 05 fázis).** Új read-only fázis a `tasks.md` után, az implementáció előtt: végigfut a `spec.md` + `plan.md` + `tasks.md` hármason és **5 kategóriában** keres problémát:
  1. **Duplikációk** (ismétlődő követelmények)
  2. **Ambiguitás** (vágy fogalmak, hiányzó mérőszámok)
  3. **Alulspecifikáció** (hiányzó elfogadási feltételek, meghatározatlan komponensek)
  4. **Konvenció-ütközések** (a `conventions.md`-vel szembeni eltérések)
  5. **Lefedettségi hiányok** (követelmény ↔ task egymáshoz rendelése)

  **Döntés: új önálló fázis (A2), teljes sorszám-eltolással.** A 0–7 számozás 0–8-ra bővül.
  - Kimenet: strukturált jelentés súlyossági besorolással a `specs/cycle-NN-<name>/analyze-report.md`-be.
  - Read-only: nem módosít fájlokat, csak jelent (kivéve a státusz-visszafordítást FAIL esetén).
  - PASS esetén: tovább az új 06-implement fázisra.
  - Commit: `cycle-NN: 05-analyze`.

  **FAIL esetén — kategória → visszalépési cél (explicit leképezés):** egy olcsóbb LLM-nek konkrét célt kell adni, nem „vissza a megfelelő fázisba".

  | Kategória | Visszalépés | Indok |
  |---|---|---|
  | Duplikáció | 03 (tervezési), 04 (task-szintű) | a redundancia forrásához |
  | Ambiguitás | 03 (technikai döntés), 02 (viselkedési — ritka) | ahol a fogalmat tisztázni kell |
  | Alulspecifikáció | 03 (meghatározatlan komponens), 02 (hiányzó elfogadási feltétel) | a hiányzó döntés szintjére |
  | Konvenció-ütközés | 03 (enyhe), 00 (súlyos — `conventions.md` felülvizsgálat) | összhangban az SK4 logikájával |
  | Lefedettségi hiány | 04 (követelmény ↔ task újrarendelés) | a task lista a hiányos |

  - A visszalépés **státusz-visszafordítással** jár (a célfázis dokumentuma visszaáll nem-kész státuszra).
  - Ha **több kategória is FAIL**, a legkorábbi érintett fázisra kell visszalépni (02 < 03 < 04), hogy a későbbi fázisok ne épüljenek hibás alapra.

  **Beleszületési követelmények (az új prompt a 6.6.2-ben ezekkel jöjjön létre):** mivel a 05-analyze új fázis, a 2.1 kereszt-követelményei eleve vonatkoznak rá, nem utólag pótolva:
  - `conventions.md` létezés-ellenőrzés beolvasás előtt (D1 = B).
  - `git status --short` előellenőrzés az indításkor (egységes minden fázissal, bár a fázis maga read-only).
  - Dedikált „Folytatás megszakított futás után" szekció döntési fával (06 mintájára).
  - Minőségellenőrzési lista a jelentés lezárása előtt: mind az 5 kategória végigfutott-e.
  - „Egy kérdés egyszerre" szabály + klikkelhető markdown link a válasz végén.
  - Relatív útvonal-formátum az `analyze-report.md`-ben (`file://` tilos).

  **Új fázis-számozás (minden fázis +1 a 04 után):**
  | Új szám | Új fájlnév | Eddigi szám | Eddigi fájlnév |
  |---|---|---|---|
  | 00 | `00-init-project.md` | 00 | (változatlan) |
  | 01 | `01-add-cycles.md` | 01 | (változatlan) |
  | 02 | `02-write-spec.md` | 02 | (változatlan) |
  | 03 | `03-write-plan.md` | 03 | (változatlan) |
  | 04 | `04-write-tasks.md` | 04 | (változatlan) |
  | **05** | **`05-analyze.md`** | — | **ÚJ** |
  | 06 | `06-implement.md` | 05 | `05-implement.md` |
  | 07 | `07-validate.md` | 06 | `06-validate.md` |
  | 08 | `08-review-and-merge.md` | 07 | `07-review-and-merge.md` |

  **Átsorszámozási teendők (felvéve külön pontokként alább):**
  - Fájlnevek `git mv` (5 → 6, 6 → 7, 7 → 8)
  - D7 commit message minták frissítése (06-implement, 07-validate, 08-merge)
  - Minden prompt belső hivatkozás (pl. „a 05-implement fázisra lépünk")
  - `prompts/README.md` szöveges leírások + 2 Mermaid diagram (magas szintű + részletes)
  - `prompts/meta-improve-prompts.md` fázis-számok
  - `docs/tanulságok.md` 4. dia (csővezeték leírás) + Mermaid diagram
  - Bármely cycle-mappában lévő `tasks.md` referencia, ha visszafelé kompatibilitás kell (de új ciklusoktól már új számozás)

- [x] **SK2 — Strukturált 10-kategóriás ambiguitás-vizsgálat (`clarify`) — csak a 02-write-spec.md-be.** A spec-kit a kérdés-gyűjtéshez **10 kategóriás sablont** ad az ágensnek (funkcionalitás, adatmodell, UX, teljesítmény, biztonság, integrációk, hibakezelés, jogosultság, observability, egyéb). Az ágens végigfut ezeken, és csak ott tesz fel kérdést, ahol valódi ambiguitás van.

  **Döntés: A — csak a 02-be (nem a 03-ba).** Indok: a spec a viselkedést írja le, ott van értelme a klasszikus ambiguitás-vizsgálatnak. A 03 plan-kérdései természetükben más jellegűek (technikai döntések, alternatívák választása) — a jelenlegi szabadabb forma jobb ott.

  **Implementálás:**
  - Új szekció a 02 promptban (`## Ambiguitás-vizsgálat — kérdés-keresési sablon`).
  - 10 kategória felsorolása + 1-2 példa kérdés mindegyikre.
  - **Iránymutatás, nem kötelezettség:** *„Menj végig a 10 kategórián, és ahol valódi ambiguitást találsz, vedd fel kérdésként a `spec-questions.md`-be. Nem kell minden kategóriára kérdést feltenned — csak ahol tényleg hiányzik az infó."*
  - A meglévő `spec-questions.md` flow változatlan — ez csak az ágens **kérdés-felfedezési segédlete**.

- [x] ~~**SK3 — `[NEEDS CLARIFICATION]` inline jelölés a spec/plan szövegében.**~~ **NEM felvéve.** A `spec-questions.md` és `plan-questions.md` rendszerünk már most lefedi a célt: minden ami pontosításra szorul, beletehető. A `Tervezésre kész` státusz garantálja, hogy minden kérdés lezárt — nincs olyan időpillanat, amikor egy „félig kész" spec-et másnak (pl. plan-író ágensnek) kellene értelmeznie. Az inline tag plusz szinkron felelősséget hozna (tag + questions.md párban tartva) anélkül, hogy új értéket adna a rendszerünkben.

- [x] **SK4 — Constitution Check a 03 plan fázisban — enyhített forma.** A spec-kit minden plan-nál explicit ellenőrzi a `constitution.md`-vel való összhangot. Nálunk a 03 beolvassa a `conventions.md`-t, de nincs explicit ellenőrzési pont a plan döntéseire vonatkozóan.

  **Döntés: enyhített forma — új minőségellenőrzési pont a 03 zárása előtt, nem új teljes szekció.**

  **Implementálás:**
  - Új egy-soros ellenőrzési pont a 03 *„Minőségellenőrzés — plan lezárása előtt"* szekciójában: *„Constitution Check: minden plan-döntés (tech stack, naming, struktúra, teszt eszköz, merge stratégia, biztonság) összhangban van a `conventions.md`-vel?"*
  - **Ha kis eltérés:** vedd fel a `plan-questions.md`-be, kérdezz rá a felhasználótól.
  - **Ha súlyos eltérés** (alapvetően ütközik a konvenciókkal): STOP, vissza a 02 vagy 00 fázishoz a konvenció felülvizsgálatára.
  - **Nem duplikálja az SK1-et:** az SK4 korai check a 03 lezárás előtt (csak plan vs conventions), az SK1 final sanity check a 05-analyze fázisban (teljes spec ↔ plan ↔ tasks ↔ conventions kereszt-vizsgálat). Az SK4 korábban fedez fel problémát, mielőtt a 04 task lista is hibás alapokra épülne.

- [x] ~~**SK5 — `[P]` párhuzamosítás jelölés vs `⟂ Tkkk`.**~~ **NEM felvéve — marad a jelenlegi `⟂ Tkkk`.** Az explicit reláció érték: ha a 04 fázisban már átgondoltuk a függőségeket, az ágensnek nem kell újra eldöntenie 06 (implement) fázisban. Az olcsóbb LLM-nek explicit instrukció jobb, mint szabad döntés — a `[P]` esetén az ágens dolga észrevenni, hogy két `[P]`-jelölt task mégse párhuzamosítható, ha ugyanazt a fájlt érintik. A jelenlegi „rejtett szabály" probléma megoldása **a 4.3-ban már szereplő pont:** kiemelt példa a 04 és 06 promptokban, nem a jelölés cseréje.

- [x] ~~**SK6 — Külön `checklist.md` artifact**~~ (NEM javasolt felvenni: a jelenlegi inline minőségellenőrzési lista egyszerűbb, single-developer flow-ban nincs előnye a külön fájlnak.)

- [x] ~~**SK7 — User Story-alapú szervezés a tasks-ban**~~ (NEM javasolt felvenni: a jelenlegi lépés-alapú szervezés működik, a user story-alapú átdolgozás nagy munka kis haszonért egy single-developer flow-ban.)

---

## 6. Skill + Agent refaktor

Az [github/spec-kit](https://github.com/github/spec-kit) projekt által inspirált **teljes szerkezeti refaktor**. A jelenlegi laposan szervezett `prompts/` mappát strukturáljuk át skillekre (fázis-receptek) és ágensekre (specialista végrehajtók), formalizálva a [`tanulságok.md`](../docs/tanulságok.md) fogalmi keretét (skill = recept, ágens = aktor).

### 6.1 Eldöntött irányok

- [x] **Mappanév: `agents/` (angol, konzisztens a `skills/` és `templates/`-vel).**
- [x] **Skill-formátum: eszközfüggetlen YAML frontmatter** (saját séma, nem Claude Code-specifikus). Indok: a prompt-család továbbra is általános marad, bármilyen ágens értheti. Ha később natív skill-integrációra megyünk (Claude Code, Antigravity), a konvertálás mechanikus.
- [x] **Ágens-hívás: Task tool subagent-ként** (a meglévő `subagent-review.md` mechanikájának folytatása). Eszközfüggetlen, nem köt önálló fázis-szintű ágens-rendszerhez.

### 6.2 Új mappastruktúra

```
prompts/
├── skills/                       # Fázis-skillek (00–08)
│   ├── 00-init-project.md
│   ├── 01-add-cycles.md
│   ├── 02-write-spec.md
│   ├── 03-write-plan.md
│   ├── 04-write-tasks.md
│   ├── 05-analyze.md             (ÚJ, SK1)
│   ├── 06-implement.md           (eddig 05)
│   ├── 07-validate.md            (eddig 06)
│   └── 08-review-and-merge.md    (eddig 07)
├── agents/                       # Specialista ágensek dedikált prompttal
│   ├── reviewer.md               (régi prompts/subagent-review.md)
│   ├── analyzer.md               (ÚJ, SK1 subagent)
│   └── researcher.md             (opcionális — a 03 kódkutató subagentje)
├── templates/                    # Üres mappa, jövőbeli sablonok
├── scripts/                      # Automatizációs bash scriptek
│   └── init-project.sh           # Ágens-integráció (placeholder, lásd 6.9)
├── README.md                     # Folyamat leírás + skill/agent index
├── meta-improve-prompts.md       # Marad
└── inprove-list.md               # Marad (fejlesztési lista)
```

### 6.3 Futtatási modell

**Minden skill-t a fő ágens futtatja** — a felhasználó által indított Claude (Claude Code, Antigravity, Cursor, stb.). Nincs választás, ezért **nincs külön frontmatter-mező** a futtató ágensre.

**A `subagents:` mező** (a skill-frontmatterben) kizárólag a **Task tool-on keresztül meghívott specialista ágenseket** sorolja fel. Ezek az `agents/` alatti fájlok, amelyeket a skill futás közben dedikált subagent-ként indít.

Tehát:
- **Skill → fő ágens (implicit, mindig így van)**
- **Skill → subagent (explicit, `subagents:` mezőben felsorolva + a skill törzsében részletezve)**

### 6.4 Skill-frontmatter séma

Minden `skills/*.md` kapja:

```yaml
---
phase: 02
name: write-spec
prerequisites:
  - "specs/roadmap.md státusz: Kész"
output:
  - "specs/cycle-NN-<name>/spec.md státusz: Tervezésre kész"
  - "specs/cycle-NN-<name>/spec-questions.md"
prev: 01-add-cycles
next: 03-write-plan
subagents: []       # Task tool-on hívott specialisták (agents/ alatti fájlok)
---

# 02 — Spec írás
...
```

**Példa subagent-tel:**

```yaml
---
phase: 08
name: review-and-merge
prerequisites:
  - "specs/cycle-NN-<name>/tasks.md státusz: Kész"
  - "specs/cycle-NN-<name>/plan.md státusz: Kész"
  - "specs/cycle-NN-<name>/spec.md státusz: Kész"
output:
  - "specs/cycle-NN-<name>/code-review.md"
  - "Merged cycle branch (lokális vagy PR, a conventions.md Merge stratégiája szerint)"
prev: 07-validate
next: 02-write-spec       # új ciklus indítása
subagents:
  - "agents/reviewer.md"  # Task tool subagent code review-hoz
---

# 08 — Review és Merge
...
```

> **Státusz-szókincs a `prerequisites`/`output` mezőkben (egységes `Kész` modell):** minden dokumentum a saját fázis-specifikus záró-státuszát kapja a keletkezésekor (pl. `spec.md` → `Tervezésre kész`, `plan.md` → `Task írásra kész`), majd **`Kész`-re lép, amint a downstream fázis átveszi és továbbépít rá** (a spec-et a 03, a plan-t a 04, a tasks-ot a 05/06 „veszi át"). Így a 08 fázis a `spec.md`/`plan.md`/`tasks.md`-t már egységesen `Kész` státuszban várja. A státusz-átmenet (`<fázis-specifikus> → Kész`) explicit rögzítendő minden érintett promptban — lásd a 4.2 megfelelő pontját.

### 6.5 Agent-frontmatter séma

Minden `agents/*.md` kapja:

```yaml
---
name: reviewer
role: "Kód-review specialista ágens"
called_by: ["skills/08-review-and-merge.md"]
inputs:
  - "Cycle branch git diff (vs master)"
  - "conventions.md"
  - "specs/cycle-NN-<name>/plan.md"
outputs:
  - "specs/cycle-NN-<name>/code-review.md"
tools: ["Read", "Bash", "Grep"]
---

# Reviewer agent — System prompt
...
```

### 6.6 Migrációs lépések

- [x] **6.6.1 — Mappa-struktúra létrehozása.** `mkdir -p prompts/skills prompts/agents prompts/templates`
- [x] **6.6.2 — `git mv` az összes fázis-promptra a `skills/` alá, egyúttal SK1 átsorszámozás:**
  - `prompts/00-init-project.md` → `prompts/skills/00-init-project.md`
  - `prompts/01-add-cycles.md` → `prompts/skills/01-add-cycles.md`
  - `prompts/02-write-spec.md` → `prompts/skills/02-write-spec.md`
  - `prompts/03-write-plan.md` → `prompts/skills/03-write-plan.md`
  - `prompts/04-write-tasks.md` → `prompts/skills/04-write-tasks.md`
  - **`prompts/skills/05-analyze.md` (ÚJ fájl, SK1)**
  - `prompts/05-implement.md` → `prompts/skills/06-implement.md`
  - `prompts/06-validate.md` → `prompts/skills/07-validate.md`
  - `prompts/07-review-and-merge.md` → `prompts/skills/08-review-and-merge.md`
- [x] **6.6.3 — `git mv` a subagent-review.md-re és új ágens-fájlok létrehozása:**
  - `prompts/subagent-review.md` → `prompts/agents/reviewer.md` (az 1.9 összes javításával együtt: file:line, Must Fix/Suggestion határvonal, gépileg parszolható `code-review.md` formátum).
  - `prompts/agents/analyzer.md` (ÚJ, SK1) — saját keretrendszerrel, a `reviewer.md` mintájára: bemenetek (`spec.md` + `plan.md` + `tasks.md` + `conventions.md`), az SK1 5 kategóriája, súlyossági besorolás, az `analyze-report.md` gépileg parszolható formátuma, és a FAIL-leképezés (lásd SK1).
  - `prompts/agents/researcher.md` (OPCIONÁLIS — a 03 jelenlegi „Documentation Reconnaissance" subagentjének formalizálása) — ha felvesszük: bemenet (kódbázis + spec `Hivatkozott fájlok`), kimenet (forrásfájl-azonosítás a 03 számára, D2 = A szerint).
- [x] **6.6.4 — Frontmatter hozzáadása minden skill és agent fájlhoz** (6.4 és 6.5 séma szerint).
- [x] **6.6.5 — Belső hivatkozások javítása az összes skill-ben:**
  - `prompts/05-implement.md` típusú referenciák → `prompts/skills/06-implement.md`
  - `prompts/subagent-review.md` → `prompts/agents/reviewer.md`
  - Minden „lépés X" típusú szöveg az új sorszámozással (05 = analyze, 06 = implement, stb.)
- [x] **6.6.6 — `prompts/README.md` teljes átírása:**
  - Új mappa-struktúra leírása
  - Skill-index (mind a 9 skill listája)
  - Agent-index (a 2 kötelező ágens: `reviewer`, `analyzer` — plusz a `researcher`, ha a 6.6.3 opcionális pontját felvesszük)
  - Frontmatter séma dokumentálása
  - Diagramok (magas szintű + részletes) az új fázis-számozással (0–8)
  - Bemenet-jelölés egységesítése (lásd 2.3)
  - Diagram-elütések javítása (`task.md` → `tasks.md`, FAIL visszalépés 04 → 06-implement, lásd 4.3)
- [x] **6.6.7 — `docs/tanulságok.md` frissítése:**
  - Új fázis-számozás (0–8) a 4. diában és a Mermaid diagramban
  - Új SK1 fázis bemutatása
  - Új agents/ struktúra említése a Skill/Ágens fogalmak diáján (2. dia)
- [x] **6.6.8 — `prompts/meta-improve-prompts.md` frissítése:**
  - Fázis-számozás 0–7 → 0–8
  - Új SK1 fázis említése
  - Új mappa-hivatkozások (`prompts/skills/`, `prompts/agents/`)
- [x] **6.6.9 — Commit message a refaktorhoz:** önálló commit (nem ciklus-specifikus), pl. `refactor: skill+agent struktúra bevezetése (SK1 + 6. szakasz)`.

### 6.7 Hatás a többi pontra

- Az **SK1 átsorszámozási teendői** (lásd SK1 részletes blokkja) **beleolvadnak ebbe a refaktorba** — egyszerre végezzük el.
- A **D7 commit message minta** SK1 átsorszámozás utáni formája lesz használatos (lásd D7-nél).
- A **4.3 README diagram-javítások** beleolvadnak a 6.6.6 lépésbe.
- **A `subagent-review.md` minden javítása** (1.9 pontok: file:line, Must Fix/Suggestion határvonal, code-review.md struktúra) az új `prompts/agents/reviewer.md`-ben kerül implementálásra.

### 6.8 Mit nem csinálunk most

- **Nincs Claude Code-specifikus skill-konverzió** — a frontmatter eszközfüggetlen marad.
- **Nincs automatikus slash-command integráció a refaktor első körében** — a felhasználó továbbra is „másolja be a prompt-ot" módon indítja a fázisokat. Az ágens-integráció scriptes automatizálása a 6.9 alatt opcionálisan implementálható.
- **Nincs MCP szerver építés** — a spec-kit ezt használja, mi nem szükségesnek tartjuk lokális single-developer flow-ban.

### 6.9 Ágens-specifikus integráció (későbbi implementáció)

A `prompts/skills/` és `prompts/agents/` a **single source of truth**. A különböző ágensek azonban más-más helyen keresik a skilleket / ágenseket:

| Ágens | Skill-hely | Subagent-hely |
|---|---|---|
| Claude Code | `~/.claude/commands/` vagy `.claude/commands/` (project) | `~/.claude/agents/` vagy `.claude/agents/` |
| Cursor (Agent CLI) | `.cursor/skills/bs-{skill_name}/SKILL.md` | `.cursor/agents/{agent_name}.md` |
| Antigravity | nincs natív skill-konvenció (manuális másolás) | — |
| Codex CLI | nincs standard skill-rendszer (manuális másolás) | — |
| OpenCode | saját konvenció (nem dokumentált a listában) | — |

**Implementálási tervek:**

- [ ] **6.9.1 — `prompts/scripts/init-project.sh` implementálása.** A script symlinkeket hoz létre a projekt-szintű ágens-mappákba (`.claude/commands/` → `prompts/skills/`, `.claude/agents/` → `prompts/agents/`, stb.). Idempotens, biztonságos, válaszható (CLI-paraméter vagy interaktív választás). A jelenlegi `init-project.sh` placeholder — a teljes refaktor után kell tartalommal kitölteni. A részletes terv a script header-comment-jében szerepel.

- [ ] **6.9.2 — `prompts/README.md` „Ágens-specifikus integráció" szekció.** Minden támogatott ágenshez egy-egy parancs vagy útmutató (manuális symlink példa vagy az `init-project.sh` használati módja).

**Most nem csináljuk** — a felhasználó jelzése szerint a strukturális refaktor (6.5–6.8) és az SK1 implementáció elsőbbséget élvez. A scriptet csak a refaktor után érdemes kitölteni, mert akkor lesz mire mutatni a symlinkeknek.

---

## 7. Megjegyzések a javítási folyamathoz

- A javításokat **prioritás szerint, csoportonként** érdemes elvégezni.
- **Sorrend a strukturális refaktor (6.) és a tartalmi javítások (1–4.) között:** előbb a strukturális refaktor + SK1 átsorszámozás (fájlnevek `git mv`, belső hivatkozások, README/diagramok), és **utána** a tartalmi javítások az új fájlneveken. Fordított sorrendben kétszer kellene dolgozni a hivatkozásokon, mert a refaktor minden belső referenciát átír.
- Minden javítás után **futtassuk le a meta-improve-prompts.md-t** újra, hogy ellenőrizzük, nem keletkezett-e új inkonzisztencia.
- A nagy prompt (03-write-plan.md) esetén **a tagolás javítása előtt** érdemes megegyezni a struktúrában, hogy ne kelljen kétszer dolgozni.
- Az olcsóbb LLM-re vonatkozó javításokat **konkrét tesztcaseekkel** lehet validálni (pl. Haiku 4.5 futtatás egy egyszerű ciklusra).
