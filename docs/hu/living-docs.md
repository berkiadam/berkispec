# docs-generated/ — élő dokumentáció

← [Vissza a főoldalra](../../README-HU.md) · [Oldalindex](README.md)

A projekt gyökerében lévő **`docs-generated/`** mappa a `08-doc-sync` fázis által ciklusról ciklusra karbantartott, **generált, „as-built" dokumentáció** otthona. Megkülönböztetendő a kézzel írt `docs/` mappától: **minden, amit az AI/skill gyárt vagy ami projekt-követelmény, ide kerül**, és a doc-sync **garantálja a mappa összes fájljának konzisztenciáját** a megvalósult rendszerrel (DS11). A mappát (és tartalmát) **commitálni kell** — ez a leadandó, nem kerülhet `.gitignore`-ba.

Minden generált doksi **fejléc-blokkot** kap (DS17): `> **Lefedve:** cycle-NN-ig · **Utolsó frissítés:** cycle-NN (dátum) · **Generátor/scope:** <mit fed le, mi alapján tartandó konzisztensen>`. A fájlnevek **angolok** (kódbázis-konvenció), a tartalom **magyar** (mint a skillek).

| Fájl | Mi ez | Ki / mikor írja | Hol él |
|---|---|---|---|
| `README.md` | A mappa **indexe/manifesztje** — egysoros leírás fájlonként. Új generált fájl → kötelezően bekerül; elavult bejegyzés → ki (halmaz-egyezés a tényleges tartalommal, DS21). | A 08-doc-sync hozza létre a mappával együtt, és minden futáskor karbantartja. | `docs-generated/README.md` (külön a `prompts/README.md`-től és a gyökér `README.md`-től) |
| `system-overview.md` | **As-built működési áttekintés** (onboarding/stakeholder magasság): képességek/flow-k (képesség szerint, nem ciklusonként), konszolidált szekvenciák (mermaid), állapotmodell, [feltételes] endpoint-leltár. A hiányzó köztes szint a spec és az `architecture.md` között. | A 08-doc-sync komponálja a `src/` + lezárt spec.md-k + roadmap alapján; a `02-write-spec` „pull"-ként **visszaolvassa** current-truth kiindulásként (DS5). | `docs-generated/system-overview.md` |
| `architecture.md` | **„Hogyan épül/fut"** — komponensek, build, deployment, ops. A korábbi `docs/architecture.md` ide költözött; a 06 `TLAST` architecture-író task **nyugdíjazva** (DS4) — a doc-sync a **kizárólagos gazdája**. | A 08-doc-sync reconciliálja minden ciklusban (a korábbi 09-es dokumentációs lépésből áthozva). | `docs-generated/architecture.md` |
| `CHANGELOG.md` | **Részletes, inkrementális, ciklusonkénti** változásnapló — mit változott a rendszer működésében/doksijában. A `system-overview.md` csak coverage-markert + linket tart rá (nem duplikál). | A 08-doc-sync minden futáskor bővíti egy új ciklus-bejegyzéssel (DS15). | `docs-generated/CHANGELOG.md` |
| `design-drift.md` | A megvalósult rendszer **eltérései a HLD/LLD szándéktól** (DS20) — pl. RFC 8693 token exchange vs. legacy Keycloak. A megoldott eltérés nem törlődik, hanem a „Lezárt eltérések" szekcióba kerül. A `system-overview.md` tiszta as-built marad (a drift nem keveredik bele). | A 08-doc-sync tölti fel inkrementálisan; csak **explicit** (spec által megnevezett) vagy checklist-alapú drift kerül be, bizonytalan eset → `doc-sync-questions.md` (DS24d). | `docs-generated/design-drift.md` |
| `test-description.md` | A projekt **teszt-leltára** (LD1–LD8): kategóriánként a `TL-NNN` tételek — `Környezet` (`local`/`remote`), `Cél`, `Lépések` (konkrét parancs), `Elvárt eredmény`, `Futtató parancs`, `Recept`, `Utolsó futás`, `Forrás-ciklus`. Arra válaszol, hogy **milyen tesztek léteznek és mit bizonyítanak** — a `test-conventions.md` viszont arra, hogy **hogyan futtatom** (mező-szintű tulajdon, D3). A `TL-NNN` **projekt-szintű, soha nem újrahasznosított** azonosító; a kivezetett teszt tétele `Kivezetve` jelölést kap, és a fájlban **marad** (audit-nyom, D4). | A 08-doc-sync a **kizárólagos gazdája**; a teljességét **kemény kapu** védi (`test-inventory-check.py`, LD5): a `conventions.md` `### Tesztfájl-helyek` globjaival felderített minden tesztfájlhoz kell tétel, és minden tétel parancsának létező fájlra kell mutatnia. Fogyasztói (csak olvasás): `02-write-spec`, `03b-write-test-plan` (regressziós kör + duplikáció-elkerülés), `bs-manual-test-plan` (a `TG-NN` csoportok harmadik forrása). | `docs-generated/test-description.md` |
| _(projekt-specifikus extra doksik)_ | Bármely további generált doksi (a skill **nem** hardcode-olja, pl. külső rendszer konfiguráció-leírás). | A mappa-bejárás találja meg, a `doc-sync-plan.md` veszi fel; a fejléc-scope dönti el az érintettséget. | `docs-generated/<fájl>` |

**Konzisztencia-kapu (DS22):** a doc-sync minden futás végén lefuttat egy objektív, projektfüggetlen magkaput. Három pontja (nincs megszűnt/átnevezett azonosító a doksikban, mappa-index halmaz-egyezés, coverage-marker bump) **teljesen szkriptelt** — a `prompts/scripts/ds22-gate-check.py` végzi, nincs bennük LLM-ítélet, ezért a telepítő minden platform scripts-mappájába (`.claude/scripts/`, `.agents/scripts/`, `.github/scripts/`) automatikusan bemásolja. A 4. pontot (minden forrásbeli ábra átkerült-e) a script csak informatív mermaid-blokk-számlálással segíti, a tényleges pairing-döntés az ágensé. Feltételesen (ha a `conventions.md` `## Projekt referenciák` API-leírót deklarál) egy endpoint/interfész kereszt-ellenőrzés is fut. Bukáskor a konkrét eltérés a `doc-sync-questions.md`-be kerül, és **ember-vezérelt** javítás indul, míg a kapu zöld nem lesz.

## 11.1 specs/test-conventions.md — visszatérő teszt-elvárások és receptek (TC1–TC11)

**Fájl:** `specs/test-conventions.md` (a `specs/roadmap.md` mellett — **nem** a `docs-generated/`-ben). **Gazdája:** a `08-doc-sync`. **Fogyasztói:** a `02-write-spec`, a `03a-write-code-plan` és a `03b-write-test-plan` (a `quick-flow` csak olvassa).

> **A `docs-generated/test-description.md` teszt-leltár NEM helyettesíti ezt a fájlt, és fordítva sem (D3).** A határvonal **mező-szintű tulajdon**: a leltár a *cél / lépések / elvárt eredmény* igazsága **minden** tesztre; ez a regiszter a *recept* igazsága (`Indítás`, `Példa hívás`, `Előfeltétel`, `Takarítás`, credential-pointer) a **promótált, visszatérő** elvárásokra. **Azonos mezőt a kettő nem hordoz**, ütközésnél mezőnként az adott fájl nyer, és a kapcsolatot egy **kétirányú** hivatkozás adja: a leltár tétele a `Recept` mezőben az `R-NN`-re mutat, a recept adatlapja pedig a `Leltár-tételek` mezőben vissza a `TL-NNN`-re. A `test-inventory-check.py` **mindkét irányt** méri — egyoldalú hivatkozás bukás (LD6).

**Milyen problémát old meg:** ahogy egy projekt előrehalad, kialakul, hogy **minden ciklusban mit és milyen sorrendben kell letesztelni** — és mihez milyen recept tartozik (pl. „a Keycloak dev image-t buildelni, a registry-be pusholni, a podot újraindítani, majd a token-cserét `curl`-lel ellenőrizni"). Ez a tudás eddig **ciklus-lokális** artefaktumokban (`plan-questions.md`) keletkezett és minden ciklus végén elveszett, így a következő ciklus **újra megkérdezte ugyanazt**. Ez a fájl ennek a párbeszédnek a tartós desztillátuma.

**Szerkezete — kötelező koordináta-blokk + három szekció** (a 2./3. az 1.-re hivatkozik, az 1. a 0.-ra):

| Szekció | Tartalom |
|---|---|
| **0. Koordináták** (TC13 — kötelező, a fájl elején) | **Minden konkrét érték egy helyen, kereshetően:** környezetek és végpontok (környezet, komponens, URL+port, health endpoint), teszt-userek/kliensek/titkok (környezet, azonosító, titok **vagy pointer**, scope), paraméterek és env-fájlok. Ez az igazságforrás: a receptek hivatkoznak rá, nem másolják — ha egy port vagy host változik, elég itt átírni. A TC5 titok-szabály itt is él (osztott platform credential csak pointerként). A TC8 kapu ellenőrzi, hogy létezik, elöl áll és van benne **kitöltött** (nem placeholder) sor. |
| **1. Recept-regiszter** | Paraméterek, URL-ek, portok, komponens-koordináták (repo-útvonal, image-név, registry-cél, namespace/pod), teszt-userek, példa REST/`curl` hívások, build/deploy/indító parancsok, előfeltételek és sorrend, hatókör-jelölés (`lokális` / `osztott-remote`). |
| **2. Minden körben szükséges lokális (mock alapú) tesztek** | Az 1. szekció receptjeire hivatkozó tételek. |
| **3. Minden körben szükséges integrációs / E2E tesztek** | Ugyanígy. |

**A promóció mindig a felhasználó döntése (TC12).** Minden doc-sync futásban a fázis **tételesen felkínálja a ciklus tesztjeit**: a `plan.md` Tesztelési stratégiájából, a `tasks.md` `[RED]`/`[CHECK]`/`TREG` taskjaiból és a `test-report/` tényleges futásaiból összeállít egy jelöltlistát, mindegyikhez odaírja az **önhordó viselkedés-leírást** (így kerülne be), a cél-szekciót, a szükséges receptet (meglévő `R-ID` vagy új) és egy **javaslatot + indokot** — majd **egy körben** megkérdezi a `doc-sync-questions.md`-ben, melyiket emelje be projekt szintre. Ez **blokkoló kérdés**: promóció nem történik válasz nélkül, és a fázis sem zárható le nyitott promóciós kérdéssel. Ami nem kerül be, az a fájl végén lévő **`## Nem promótált jelöltek (döntés-napló)`** appendixbe kerül, hogy a következő ciklus **ne kérdezzen rá újra**. Csak olyan teszt kínálható fel, amely ebben a ciklusban **ténylegesen lefutott és zöld volt** (TC3).

**Két minőségi szabály, amit a TC8 kapu kikényszerít:**

- **TC10 — önhordó tételek.** A 2./3. szekció „Mit ellenőriz" leírása **nem hivatkozhat más dokumentumra**: sem spec-szekció sorszámra (`1.2. FlowX Mock negatív tesztek`), sem ciklusra (`Cycle 19 init-hash tesztek`). Az olvasó (egy friss kontextusú 02/03 fázis vagy egy új kolléga) nem fogja megnyitni a lezárt `spec.md`-ket. Helyette **viselkedés-szintű** leírás kell: *„a mock `/start-process` 201-et ad érvényes `processName`-re, és 400-at hiányzó body-ra"*. A ciklus-szám az `Utolsó futás` / `Bizonyíték` oszlopba tartozik.
- **TC10/b — a teszt részletes leírása is átjön.** A táblázat **index**, nem teszteset: minden promótált tételhez kötelező egy `### <ID>` **részletező blokk** a táblázat alatt — `Cél` / `Előfeltétel` / `Lépések` / `Elvárt eredmény`. A ciklus `spec.md`/`plan.md`-jében megírt tesztleírás **tartalma maradéktalanul átjön** (ha ott három lépés és két hibakód volt, itt is annyi lesz), de **önhordóra normalizálva**: a spec-számozás, ciklus-hivatkozás és „lásd fent" feloldva vagy törölve, a titkok pointerre cserélve. A „prózát ne írj" szabály **csak a narratív magyarázatra** vonatkozik (indoklások, tanulságok), nem a tesztesetek strukturált leírására — ezt a félreértést a skill most explicit kizárja.
- **TC11 — futtatható koordináták.** Minden recept kötelező elemei: **`Indítás`** (hogyan húzom fel a szükséges környezetet + health-ellenőrzés; unit tesztnél explicit `N/A`), **`Példa hívás`** (teljes URL, headerek, payload, várt válasz — `curl` vagy `.http` blokk; ha token kell, a token megszerzésének hívása is), és **`Leállítás / takarítás`**. A 3. szekció környezeti előfeltételei (*„lokális Keycloak fut"*) **`R-ID`-re kell hivatkozzanak** — különben nem derül ki, hogyan teljesíthetők, és a teszt nem reprodukálható.

**A legfontosabb szabály (TC1/a) — ez NEM futtatható forrás.** A regiszterből semmi nem fut le automatikusan: a `test-runner` subagent ezt a fájlt **nem olvassa**, kizárólag a `plan.md` `Tesztelési stratégia` / `Regressziós érintettség` szekcióit. Egy recept akkor és csak akkor hajtódik végre, ha a `02`/`03` fázis azt tudatosan **beemelte** a ciklus `spec.md`/`plan.md`-jébe — ha kérdéses, a felhasználó interjúztatásával. Ez a beemelés maga az emberi kontroll-pont: **a `plan.md` a futtatás egyetlen igazsága**, a regiszter a memória.

**A beemelés két projekciója** (a meglévő spec/plan határvonal szerint):
- **`spec.md` → `Teszt specifikáció` / `Definition of done`:** a 2./3. szekció azon tételei, amelyeket a ciklus **elfogadási feltételként** vállal — **viselkedés-szinten**, a tétel ID-jára hivatkozva. Parancs, tesztfájl-útvonal, eszköznév ide nem kerül. A puszta „ne törjön el" jellegű regressziós tételek nem mennek a spec-be.
- **`plan.md` → `Tesztelési stratégia` / `E2E infrastruktúra` / `Regressziós érintettség`:** a **maradéktalan, önhordó** beemelés — minden URL, port, namespace/pod, image-név, teszt-user és jelszó, paraméter, **példa `curl` hívás**, build/push/restart parancs, előfeltétel és sorrend **szó szerint**. Puszta hivatkozás és placeholder tilos (a `test-runner` csak ezt látja); a regiszterre csak **provenance**-ként hivatkozunk. Ezt a 03 minőségellenőrzése explicit ellenőrzi.

**Élő snapshot, nem napló (TC4):** minden tétel mellett `Utolsó futás: cycle-NN` marker; a fájl mindig az aktuális állapotot tükrözi. Ha egy komponens megszűnt vagy a tétel már nem értelmezhető, a tétel **törlődik** (nem archiválódik) — a törlés ténye és oka a `CHANGELOG.md`-be kerül, és minden törlés **külön, pipálható terv-tétel** a `doc-sync-plan.md`-ben, hogy a felhasználó lássa. Környezeti koordinátát (URL, pod) nem lehet automatikusan verifikálni, ezért 3+ ciklus régi marker esetén a doc-sync **rákérdez**.

**Bizonyíték-alapú promóció (TC3):** nem „érzésre" dől el, mi az „alapvető". Egy tétel akkor promótálódik, ha (a) egy korábbi ciklusból származik és **ebben** a ciklusban is szerepelt a `plan.md` regressziós listájában vagy tényleg lefutott — azaz bizonyította a ciklus-független relevanciáját —, **vagy** (b) a felhasználó megerősítette. Recept csak akkor, ha **ebben a ciklusban zölden lefutott**; **kitalált parancsot tilos beírni**.

**Titok-osztályozás (TC5)** — hatókör-alapú, mechanikus döntés („személyt hitelesít, vagy osztott platformhoz ad hozzáférést?"):

| Bekerülhet (dev-hatókörű, nem személyhez tartozik) | Csak pointer (személyt hitelesít / osztott platform) |
|---|---|
| seedelt dev teszt-userek + jelszavaik, dev IdP realm-admin, lokális DB-user, mock API-kulcs, dev client-secret | klaszter/OpenShift login, registry push-credential, VPN, cloud IAM, git/CI token, bármi ami test/prod-on is működik |

Bizonytalan eset → kérdés, és amíg nincs válasz, **pointer megy, nem érték**. (A bal oszlop tételei a Clean Slate szabály miatt jellemzően már ma is a repóban vannak a seed/realm-import fájlokban.)

**Bootstrap meglévő projektben (TC6):** a berkispec bekerülhet egy már a 30. ciklusában lévő projektbe, ahol a fájl soha nem létezett. Ekkor a `doc-sync-planner` **javaslatot állít össze** a meglévő anyagból (lezárt `spec.md`/`plan.md` teszt-szekciói, lezárt `plan-questions.md`-k — itt vannak a környezeti koordináták —, `test/` mappa, E2E compose, `conventions.md` referenciák), és a doc-sync **arról** folytat párbeszédet — nem üres lapról kérdez. Ha nincs egyetlen promótálható tétel sem, a fájl **nem jön létre** (üres váz nem készül, mert azt a következő fázis találgatással töltené ki). A bootstrap **független** a `docs-generated/` bootstrap-ágától.

**Kérdés-hatókör (TC7):** minden ciklusban kérdezni kell, de a terjedelem eltér — **bootstrapnél** széles interjú, **steady state-ben** rövid, célzott megerősítés a doc-sync javaslatáról („ezt promótálnám, ezt törölném, ezeket bumpolom — jó?"). A csatorna a `doc-sync-questions.md`, hogy egy megszakadt futás után is folytatható legyen.

**Saját kapu (TC8) — szkriptelt:** a DS22 magkapu a `docs-generated/`-re fut, ez a fájl azon kívül van, ezért saját kapuja van. A kapu **teljesen determinisztikus, LLM-ítélet nélküli** — a `prompts/scripts/tc8-gate-check.py` végzi, amit a telepítő ugyanabba a platform-scripts mappába másol, mint a `ds22-gate-check.py`-t (`.claude/scripts/`, `.agents/scripts/`, `.github/scripts/`, `.codex/scripts/`, `.cursor/scripts/`):

```bash
python3 <platform-scripts-mappa>/tc8-gate-check.py specs/test-conventions.md \
  --project-root . --marker cycle-NN [--stale-after 3]
```

| # | Check | Blokkol? |
|---|---|---|
| 1 | **Útvonal-létezés** — a megnevezett repo-belső útvonalak (tesztfájl, script, compose, komponens-mappa) léteznek-e | **FAIL**, ha a szülő-mappa létezik, de a cél nem (biztos jel az elavulásra); ha repo-belsőként nem oldható fel (külső hivatkozás, image-ref, HTTP endpoint), csak **WARN** |
| 2 | **Lógó hivatkozás** — a 2./3. szekció minden tétele létező 1. szekciós receptre (`R-ID`) hivatkozik-e | **FAIL**; a nem hivatkozott recept **WARN** |
| 3 | **Titok-check (TC5)** — bekerült-e tiltott credential | **FAIL** biztos mintánál (PAT/kulcs-prefix, privát kulcs blokk, `oc login --password`, `docker login -p`); platform-szó + credential-szó egy sorban **WARN** |
| 4 | **`Utolsó futás` marker (TC4)** — van-e marker, és melyik avult el | hiányzó marker **FAIL**; elavult (default 3+ ciklus) **WARN** → kérdés-trigger |

Kilépő kód: `0` = minden kemény check PASS (WARN megengedett), `1` = legalább egy FAIL, `2` = használati hiba. **Ha a fájl nem létezik, a script `0`-val, „kihagyva" jelzéssel tér vissza** (TC6: a hiánya korai ciklusban nem hiba). A WARN nem blokkol, de nem is hagyható figyelmen kívül: mindegyikre javítás vagy `doc-sync-questions.md` kérdés a válasz. Bukáskor ugyanaz az **ember-vezérelt** javító hurok fut, mint a DS22-nél.

**Mi nem tartozik ide:** a `conventions.md` rögzíti, **hogyan** tesztelünk (eszközök, mappastruktúra, parancsok, elvek — ember birtokolja, stabil); a `plan.md` azt, mi az **új** ebben a ciklusban. Ez a fájl azt, **mit és mikor kötelező** tesztelni, komponensenként, as-built.

## 11.2 export/ — verziózott PDF export (`/bs-export-doc`)

**Parancs:** `/bs-export-doc` · **Script:** `prompts/scripts/export-doc.py` · **Kimenet:** `export/<név>-v<N>.pdf`

A `docs-generated/` doksik **markdown**ban élnek — átadható, archiválható változatot viszont PDF-ben kér az élet (stakeholder review, audit, onboarding-csomag). Ez a segédparancs ezt adja, a **mermaid ábrákkal együtt**. **Nem fázis:** nincs előfeltétele, nem változtat státuszt, bármikor futtatható.

**Mit exportál:**
- **paraméter nélkül** a két kötelező generált doksit (`docs-generated/architecture.md`, `docs-generated/system-overview.md`);
- **paraméterrel** a megnevezett fájl(oka)t — a skill oldja fel a szabad szöveget („a cycle-16 plan-jéből is") konkrét útvonalakra, és exportálás előtt visszaolvassa, mit fog csinálni.

**Verziózás:** fájlonként **független** számláló — az `export/` mappában lévő `<név>-v<N>.pdf` fájlok maximuma **+ 1**, üres mappánál `v1`. A **ciklus nem a fájlnévbe**, hanem a PDF **címlapjára** kerül (`Lefedve: cycle-16-ig · v3`), amit a script a doksi fejléc-blokkjából (DS17) olvas ki — így a fájlnév rövid marad, a PDF mégis visszakövethető. A forrásfájlokat a script **soha nem módosítja**: a build-mappába készít másolatot, és arra teszi rá a YAML fejlécet.

**A lánc:** `pandoc` + **`mermaid-filter`** + `xelatex`. A `mermaid-filter` Chromiummal **előre lerendereli** a diagramot (`MERMAID_FILTER_FORMAT=pdf`), így a PDF-motor kész vektorgrafikát kap.

> **Miért ez a lánc — mérési alapon.** A mermaid alapból `foreignObject`-be teszi a címkéket. Egy azonos fixtúrán (sequenceDiagram + flowchart) mérve: **WeasyPrint** alapbeállítással a flowchart **összes címkéjét elveszti** (üres dobozok — a saját, részleges SVG-motorja kihagyja a `foreignObject`-et); `htmlLabels: false`-szal megjavul. A **Chromium-alapú** utak hibátlanok: az `xelatex` azért, mert a `mermaid-filter` már renderelt grafikát ad neki, a **`pagedjs-cli`** pedig azért, mert maga Chromium. Vagyis **nem** a „LaTeX vs CSS" a döntő, hanem a `foreignObject` — és mivel az xelatex úton a diagram alapból hibátlan, a `htmlLabels` átírására **nincs szükség** (a forrás mermaid blokkjai érintetlenek maradnak, a PDF ugyanazt mutatja, mint a szerkesztői preview).

**Miért az `xelatex` a default a `pagedjs` helyett** (ugyanazon a 8–10 oldalas tesztdokumentumon):

| | xelatex | pagedjs-cli |
|---|---|---|
| Oldalszám ugyanarra a tartalomra | **8** | 10 (+25%) |
| Üres oldal | nincs | **van** (a 2. oldal 0,0% tinta) |
| Oldalszám a láblécben / a TOC-ban | van / van, pontozott vezetővel | nincs / nincs |
| Futásidő | 16,8 s | 15,9 s |
| Függőség | pandoc + texlive (rendszercsomag) | + npm-globális `pagedjs-cli` (saját Chromium) |
| Előnye | nyomdai tördelés, tömör oldalkitöltés | **CSS-alapú formázás** — sokkal könnyebb testreszabás |

A motor ezért **paraméter**, nem beépített döntés: `--engine pagedjs` egy flag, ha a kinézetet CSS-ben akarod szabni (a script ilyenkor `@page` margin-boxszal pótolja az oldalszámot).

**A script kulcs-opciói:** `--paper a3` (széles szekvencia-diagramokhoz), `--engine xelatex|pagedjs`, `--check` (csak függőség-ellenőrzés), `--dry-run` (mit készítene, milyen verziószámmal), `--export-dir`, `--keep-build`.

**Amit a script a láncon túl megold** — ezek nélkül kézi `pandoc`-hívással romlik a minőség: beágyazott `header.tex` (kódblokk-dobozolás `tcolorbox`-szal, hosszú útvonalak tördelése `fvextra`-val, `xurl`, magyar karakterek), **széles ábrák automatikus leskálázása** a szövegtükörre (`max width=\linewidth`), `--resource-path` a forrásmappára (a relatív képhivatkozások a build-mappából is feloldódnak), és `PUPPETEER_EXECUTABLE_PATH` a rendszer böngészőjére, hogy ne töltsön le még egy Chromiumot.

**Hiba esetén:** hiányzó függőségnél a script **megáll** (kilépő kód `2`) és kiírja a telepítő parancsot (`npm install -g mermaid-filter`) — mermaid-renderelés nélkül nem készít PDF-et, mert a diagramok nélkül a doksi használhatatlan. Pandoc-hibánál (`1`) kiírja a pandoc stderr-jét, a `mermaid-filter.err`-t és az xelatex logot, és **megtartja a build-mappát** hibakereséshez. Hibás mermaid szintaxis a `docs-generated/` **forráshibája** — a `08-doc-sync` fázisban javítandó, nem az exportban.

**Higiénia:** a `mermaid-filter` a cwd-be írja a `mermaid-filter.err`-t, ezért a pandoc az `export/.build/<név>/` mappában fut — a projekt gyökere nem szemetes. Siker esetén a build-mappa törlődik. Az **`export/` mappa `.gitignore`-ba** való: a PDF bináris, ciklusonként hízik, és bármikor újragenerálható a (verziókezelt) `docs-generated/`-ből — a skill ezt egyszer felajánlja, de csak jóváhagyással írja be.

---

## 11.3 test-runs/ — cikluson kívüli teszt-futtatás (`/bs-run-tests`)

**Mikor használd.** Amikor a kérdés nem az, hogy „zöld-e ez a ciklus", hanem az, hogy **„működik-e még minden"**: egy ad-hoc regressziós futás egy környezet-váltás után, egy `unit` szvit átfutása refaktor közben, vagy annak ellenőrzése, hogy a `rest-e2e` kategória elér-e egy frissen telepített komponenst. Ezt a keret eddig **nem** tudta: a `run-tests.py` kötelezően `plan.md`-et és kör-mappát kért, tehát minden gépi futtatás **egy ciklushoz és egy körhöz** volt kötve, és az „futtasd le az összes e2e tesztet" kérés a kereten kívülre, kézi parancsokra szorult — ahol egyetlen `EV` kapu sem fut le.

**Miből futtat.** A `conventions.md` `## Teszt-futtatás` szekciójának **projekt-szintű futtatási táblájából** (KT1), amelynek oszlop-sémája **azonos** a `plan.md` gépi futtatási tábláját (TP4/b) — egy parser, egy szabály. A `00-init-project` tölti ki a felhasználóval, a kategória-szótárral (`unit` · `rest-e2e` · `ui`) és a kategóriánkénti tesztfájl-glob-okkal együtt. A `plan.md` táblája ettől **független** és megmarad: az a ciklus egy körére szól, ez a projektre.

**Hova ír.** `test-runs/<kategória>/<YYYY-MM-DDTHH-MMZ>/<env>/` — UTC időbélyeg kettőspont nélkül (Windowson is érvényes mappanév), az `<env>` szegmens pontosan `local` vagy `remote`. A futás gyökerében a `results.json`, a `test-runs/` gyökerében pedig a `latest.json` (kategóriánként az utolsó futás útvonala és összegzése — **fájl, nem szimlink**). Ha a projektben van teszt-leltár, az eredmény tételenként is elhelyezhető `<TL-NNN>/` alkönyvtárakban — **ez a leltár második haszna**: egy központi futás eredménye tételenként visszakereshető. A mappa **gitignore-olt**: gépfüggő és újragenerálható. **Soha nem takarít magától** — a `/bs-run-tests` a záró üzenetben kiírja a méretét, és ritkítást csak explicit kérésre ajánl.

**🔴 És ami a legfontosabb: ez NEM ciklus-bizonyíték.** A keret bizonyíték-logikája `DoD-NN`/`TS-NN` joinra, TR7 frissességre és RUN1 kör-lefedettségre épül — egy cikluson kívüli futásnak **nincs mihez joinolnia**. Ezért három szinten van elzárva: a `run-tests.py` a `results.json`-be `"cycle": null`-t ír, ha az útvonal a `test-runs/` alatt van; a `dod-check.py` és a `report-gate-check.py` a `test-runs/` alatti útvonalat **`exit 2`-vel visszautasítja**; és a `06`/`07` skill prózában is kimondja ugyanezt. Enélkül a legkézenfekvőbb rövidítés az lenne, hogy lefuttatjuk a központi szvitet, és ráállítjuk a `dod-check.py`-t — a ciklus zöld lenne anélkül, hogy a ciklus tesztjei lefutottak volna. Ez a `7/p` tervezési elv: **a bizonyíték ciklushoz kötött; a kényelmi futtatás nem bizonyíték.**

---
