---
phase: 08
name: bs-doc-sync
description: "berkispec - 08. Használd a validáció után, merge előtt (Phase 08), ha a tasks.md/plan.md/spec.md mind 'Kész'. A kódváltozásokat a 'docs-generated/' rendszer-dokumentációba és az érintett komponens-README-kbe szinkronizálja (doc-sync-planner subagent, design-drift ellen), és létrehozza a 'doc-sync-plan.md'-t."
prerequisites:
  - "specs/cycle-NN-<name>/tasks.md státusz: Kész"
  - "specs/cycle-NN-<name>/plan.md státusz: Kész"
  - "specs/cycle-NN-<name>/spec.md státusz: Kész"
output:
  - "docs-generated/ konzisztens állapota (system-overview.md, architecture.md, CHANGELOG.md, design-drift.md, README.md mappa-index + a mappa többi fájlja)"
  - "Érintett komponens README-k frissítve"
  - "specs/cycle-NN-<name>/doc-sync-plan.md (a végrehajtás és a folytatás horgonya)"
  - "specs/cycle-NN-<name>/doc-sync-questions.md (ha merül fel döntési pont / kapu-bukás)"
prev: bs-validate
next: bs-review-and-merge
subagents:
  - "agents/doc-sync-planner.md"
---
# 08 — Dokumentáció szinkron (doc-sync)
## Kontextus ellenőrzés

Ha azt detektálod, hogy ennek a fázisnak a futtatása most indul (ez az első prompt a fázisban), de a kontextus nem „friss” (azaz a beszélgetési előzmények tartalmaznak korábbi fázisokból vagy futásokból származó üzeneteket), akkor kérdezz rá a felhasználónál:
> *„Úgy tűnik, hogy a fázis indításakor a kontextus nem teljesen friss. Szándékosan nem futtattál `/clear`-t az új fázis megkezdése előtt (a tokenekkel való spórolás érdekében)?”*
Várd meg a felhasználó válaszát, mielőtt folytatnád a fázis futtatását.

---

Spec driven development-ben fejlesztünk szoftvert. A fejlesztés ciklusokra van bontva. Minden ciklus egy önállóan lefejleszthető, önállóan tesztelhető részegysége a teljes implementációnak.

Ez a folyamat **8. fázisa (0–9)**: 0-init · 1-ciklusok · 2-spec · 3-plan · 4-tasks · 5-analyze · 6-implement · 7-validate · **8-doc-sync ←** · 9-review.

---

## Mi ez a fázis és mit NEM csinál

A doc-sync **minden generált projekt-dokumentumot** ciklusról ciklusra naprakészen tart egy dedikált **`docs-generated/`** mappában. A fázis garantálja, hogy a mappa **összes** fájlja konzisztens a megvalósult (as-built) rendszerrel — köztük egy koherens, onboarding/stakeholder magasságú működésleírás (`system-overview.md`), egy inkrementálisan növekvő `CHANGELOG.md`, egy `design-drift.md` (a megvalósult rendszer eltérései a tervtől) és az `architecture.md` (a „hogyan épül/fut").

- **Nem** a spec mása (a spec kimerítő, per-feature) és **nem** az `architecture.md` (build/ops belső). A `system-overview.md` a hiányzó köztes szint: „mit csinál ma a rendszer, milyen flow-kkal, milyen állapottal".
- A tartalom **magyar** (mint a skillek); a fájlnevek **angolok** (a kódbázis-konvenció szerint).
- A doc-sync a review **előtt** fut, így a doksi-változások a ciklus diffjébe és a commitba kerülnek. **De a kód-review (09) és a doc-sync (08) FÜGGETLEN minőségi kapuk:** a reviewer kizárólag a **kódra** ad findingot; a generált doksik helyességét a doc-sync **saját objektív kapuja** + emberi kérdései garantálják. A reviewer a generált doksikra **nem** ad `Must Fix`-et.

> **VEZÉRELV — olcsó-LLM-kompatibilis.** Ez a fázis úgy van megírva, hogy egy gyengébb LLM is megbízhatóan végrehajtsa: **„terv előbb, aztán mechanikus végrehajtás"** (a `doc-sync-plan.md` pipálható tervére támaszkodva), **erős gardek a „kezdjük elölről"/„fogalmazzuk át" ellen**, és **minden döntési pont kérdésként** a `doc-sync-questions.md`-be (sosem ad-hoc döntés). A gondolkodás a tervbe sűrűsödik, a végrehajtás mechanikus.

---

## Bemenet

A prompt bemenete a ciklus mappája (pl. `specs/cycle-NN-<cycle-name>`). Innen olvasod a ciklus `spec.md` / `plan.md` / `tasks.md` fájljait és a ciklus diffjét.

A munkafájljaid:
- **Inkrementális futáskor** (van aktív ciklus): `specs/cycle-NN-<cycle-name>/doc-sync-plan.md` és `specs/cycle-NN-<cycle-name>/doc-sync-questions.md`.
- **Bootstrapnél** (nincs aktív ciklus): a gyökér `temp/doc-sync-plan.md` és `temp/doc-sync-questions.md` (lásd a Bootstrap-ág szekciót).

---

## Előfeltétel

0. **Ciklus-beazonosítás:** ha a felhasználó megadott ciklust/fájlt, azt használd; különben a legfrissebb `specs/cycle-*` mappát ajánld fel megerősítésre — *"A(z) `specs/cycle-NN-<name>` ciklussal szeretnél dolgozni? Igen / Nem (megadom a ciklust)"* — és várj a válaszra, mielőtt továbblépsz.

1. **`conventions.md` létezés-ellenőrzés:** olvasd be a projekt gyökerében a `conventions.md`-t (különösen a `## Projekt referenciák` szekciót — ez a forrás-grounding regisztere, DS19). Ha nem létezik, STOP — térjenek vissza a `00` fázishoz.

2. **Munkafa ellenőrzés:** futtasd `git status --short`. Ha van commitálatlan változtatás, listázd, és kérdezd meg egy körben, hogy commitáljam-e most vagy folytassam — várj a válaszra. (A doc-sync a ciklus diffjét nézi a `master`-höz; tiszta munkafa nélkül a diff félrevezető.)

3. **Státusz-kapu (a 07-validate PASS ellenőrzése):** a validate fázis (07) PASS esetén mindhárom fájl státuszát `Kész`-re állítja. Ellenőrizd:
   - `tasks.md` státusza: `Kész`
   - `plan.md` státusza: `Kész`
   - `spec.md` státusza: `Kész`

   Ha bármelyik nem `Kész` (pl. még `Validálásra kész` vagy visszaállított `Piszkozat`), a validálás még nem futott le sikeresen — térj vissza a `07` fázishoz.

---

## Skill-szintű fájl-mandátum (DS13 — generikusság)

A skill **csak két fájlt nevez meg kötelezőként**, amelyet a doc-sync akkor is legyárt és karbantart, ha a felhasználó nem hozza létre explicit:
- `docs-generated/architecture.md` — „hogyan épül/fut" (build/ops belső);
- `docs-generated/system-overview.md` — működési áttekintés (onboarding/stakeholder).

**Minden más fájl** a `docs-generated/`-ben a **mappa-bejárással** (DS11) automatikusan gondozott — a skill **nem** hardcode-ol konkrét projekt-fájlt (pl. keycloak-konfiguráció). Ha egy projektben extra generált doksik vannak, azokat a mappa-bejárás találja meg és a `doc-sync-plan.md` veszi fel; a skill nem feltételezi a létüket.

> A `docs-generated/` mappát a doc-sync **hozza létre, ha még nincs** (bootstrap-ág) — így nincs sorrend-probléma azzal, hogy ki hozza létre.

---

## Forrás-grounding — forrás-hierarchia (DS19)

A doc-sync egyértelmű prioritási sorrendet követ; **ütközéskor a feljebb álló nyer**:

1. **Mérvadó (mi VAN — as-built):** `src/` (tényleges kód: route-ok / handlerek / modulok — **ez az elsődleges igazság**), a lezárt ciklus-`spec.md`-k (későbbi nyer), config; **opcionálisan** egy API-leíró (openapi/swagger), **ha** a `conventions.md` `## Projekt referenciák` szekciója megadja.
2. **Konszolidált összefoglaló:** `specs/roadmap.md`, `docs-generated/architecture.md`.
3. **Szándék / kontextus (mit TERVEZTÜNK):** HLD (`README.md`), LLD, külső doksik, POC-leírás — terminológia, struktúra, indoklás, drift-referencia. **NEM** írja felül a kód valóságát; az eltérés a `design-drift.md`-be kerül (DS20).

A 3. szint **projekt-specifikus** elérési útjait a doc-sync a **`conventions.md` `## Projekt referenciák`** szekciójából olvassa — **nem hardcode-ol** fájlt. Ha a szekció üres vagy hiányzik, a 3. szintet kihagyod (a drift-összevetés ekkor csak a ciklus-spec által explicit megnevezett eltérésekre szorítkozik).

---

## A doc-sync mappa fájljai (referencia)

| Fájl | Mi ez | Fejléc-scope (DS17 — „mit fed le") |
|---|---|---|
| `docs-generated/README.md` | A mappa **indexe/manifesztje** (egysoros leírás fájlonként, DS21) | a `docs-generated/` mappa tényleges fájllistája |
| `docs-generated/system-overview.md` | As-built működési áttekintés (képességek/flow-k, szekvenciák, állapotmodell, [feltételes] endpoint-leltár) | a rendszer összes felhasználói/üzleti flow-ja és állapota |
| `docs-generated/architecture.md` | „Hogyan épül/fut" — komponensek, build, deployment, ops | a rendszer felépítése és üzemeltetése |
| `docs-generated/CHANGELOG.md` | Részletes, inkrementális, ciklusonkénti változásnapló (DS15) | minden lezárt ciklus működés-/doksi-változása |
| `docs-generated/design-drift.md` | A megvalósult rendszer eltérései a HLD/LLD szándéktól (DS20) | a terv ↔ as-built eltérések + „Lezárt eltérések" |
| _(projekt-specifikus extra doksik)_ | a mappa-bejárás találja meg; a fejléc-scope dönti el az érintettséget | a fájl saját fejléce deklarálja |

---

## Megszakított futás kezelése + idempotencia (DS10 — KÖTELEZŐ)

A doc-sync bármikor megszakadhat. Újraindításkor **NE kezdj tiszta lapról** — a fázis **felismeri, mi van kész**, és onnan folytat. A folytatás horgonyai:

1. **`doc-sync-plan.md` pipált/nyitott tételei** — ez a végrehajtás determinisztikus állapota.
2. **A `doc-sync-questions.md` nyitott `[ ]` kérdései** — ha van, arra vár a fázis.
3. **A generált doksik „Lefedve cycle-NN-ig" markerei** (fejléc-blokk) — ezek mutatják, melyik fájl meddig friss.

**Folytatási sorrend (kötelező):**
1. **Először** a `doc-sync-questions.md` nyitott `[ ]` kérdései (ha van nyitott kérdés → a fázis arra vár, ne lépj tovább).
2. **Utána** a `doc-sync-plan.md` `[ ]` (elvégzetlen) tételei, sorban.

**Pipa-szabály (olcsó-LLM-biztos):** egy terv-tétel pipáját **mindig a fájl tényleges mentése UTÁN** tedd be (sosem előtte). Minden terv-tétel legyen **újrafuttatás-biztos** (reconciliation jellegű, ugyanoda konvergál) — így egy megszakadás legrosszabb esetben egy már kész tételt futtat újra ártalmatlanul, nem hagy ki meg nem írt változást.

**Ha még nincs `doc-sync-plan.md`:** a fázis a tervkészítéssel indul (lásd lent). **Ha van:** a fázis a fenti folytatási sorrend szerint folytat — nem készít új tervet a nulláról, csak ha a meglévő terv hiányos.

---

## Feladatod — a fázis menete

A doc-sync **„terv előbb, aztán mechanikus végrehajtás"** mintát követ. A lépések:

1. **Ág-elágazás:** bootstrap vagy inkrementális? (lásd lent)
2. **Tervkészítés:** a `doc-sync-planner` subagent megírja a `doc-sync-plan.md`-t (per-fájl pipálható terv).
3. **Mechanikus végrehajtás:** a fő ágens végrehajtja a terv `[ ]` tételeit, fájlonként mentve és pipálva.
4. **Objektív konzisztencia-kapu (DS22):** a magkapu lefuttatása; bukáskor ember-vezérelt javító hurok (a kérdés a `doc-sync-questions.md`-be).
5. **Commit + továbblépés a 09-re.**

---

## 1. Ág-elágazás: bootstrap vs inkrementális

**Nézd meg, létezik-e a `docs-generated/system-overview.md`:**

- **NEM létezik → BOOTSTRAP-ág.** A `docs-generated/` mappát még senki nem rakta össze. Ez egyszeri nagy munka, **külön munkaterv és felhasználói megerősítés** tartozik hozzá — lásd a „Bootstrap-ág" szekciót. **Ne kezdj bele megerősítés nélkül.**
- **Létezik → INKREMENTÁLIS ág.** A normál ciklus-futás: csak az **érintett** flow-kat/szekciókat írod át, a többire könnyű check fut. Lásd az „Inkrementális ág" szekciót.

---

## 2. Tervkészítés a `doc-sync-planner` subagenttel → `doc-sync-plan.md` (DS14)

A nehéz munkát (forrásgyűjtés, per-fájl diagnózis, drift-megállapítások) egy **read-only diagnoszta subagent** végzi, az `analyzer` mintájára. A **fő ágens kérdez** (a `doc-sync-questions.md`-ből) és **hajtja végre** a tervet — a subagent **nem** kérdez közvetlenül és **nem** írja a doksikat.

**A tervkészítés lépései:**
1. Olvasd be a `prompts/agents/doc-sync-planner.md` rendszerpromptot.
2. Definiálj egy `doc-sync-planner` subagentet ezzel a rendszerprompttal.
3. Indítsd el, átadva neki: a ciklus mappáját (`spec.md`/`plan.md`/`tasks.md`), a ciklus `git diff`-jét a `master`-höz, a `conventions.md`-t (a `## Projekt referenciák`-kal), és a `docs-generated/` mappa aktuális tartalmát.
4. A subagent visszaadja a **per-fájl pipálható tervet** (a mappa minden fájljára + a szükséges új fájlokra: „mit kell tenni" vagy „nincs teendő" + a drift-megállapítások) **és minden `reconciliation`/`új` tételhez a kész `Csereszöveg`et** (lecserélendő jelenlegi részlet + megírt új szöveg). **A fő ágens a tervet ÉS a csereszövegeket a `doc-sync-plan.md`-be írja** (inkrementálisan: `specs/cycle-NN-<cycle-name>/doc-sync-plan.md`; bootstrapnél: `temp/doc-sync-plan.md`) — így a csereszöveg perzisztens, egy megszakadt futás resume-ja a fájlból folytat (DS10). Mivel a subagent **már beolvasta** a teljes `docs-generated/` tartalmat és megírta a csereszöveget, a fő ágensnek a fájlokat **nem kell újraolvasnia és újrakomponálnia** — csak alkalmaz.

> **Ha a subagent nem fut le, vagy nem ad tervet:** ne kezdj el „fejből" doksit írni — STOP, jelezd a felhasználónak, és kérdezd, hogy próbáljam-e újra a subagentet, vagy állítsam-e össze a tervet közvetlenül a `doc-sync-planner.md` szempontjai szerint a fő ágensben.

A `doc-sync-plan.md` formátumát lásd a **Sablonok** szekcióban. **A terv pipálása a végrehajtás állapota** — innen folytat egy megszakadt futás (DS10).

---

## 3. Inkrementális ág (DS9, DS11, DS14)

Akkor fut, ha a `system-overview.md` **létezik**. **Bounded scope:** csak az **érintett** flow-kat/szekciókat írod át; a holisztikus átfésülés **bounded** ellenőrzés, **nem** teljes újra-audit.

### 3.1 Az érintettség mechanikus szabálya (DS24e)

Egy `docs-generated/` fájl **érintett**, ha a ciklus diffje olyan komponenst/flow-t/endpointot mozdít, amit a fájl **fejléc-scope-ja** (DS17) lefedettként deklarál; egyébként **érintetlen**. A `doc-sync-planner` **ezt a szabályt alkalmazza, nem érzésre dönt**:
- **érintett fájl →** reconciliation (csak az érintett szekciók átírása, az elavult lecserélve);
- **érintetlen fájl →** könnyű check: a fejléc-scope alapján igazold, hogy tényleg nem érinti a ciklus → a `doc-sync-plan.md` „nincs teendő" tétele rögzíti (a coverage-marker maradhat a régi cycle-NN-en).

### 3.2 A végrehajtás (mechanikus: a subagent csereszövegeinek alkalmazása)

A `doc-sync-plan.md` `[ ]` tételeit hajtod végre, fájlonként — de **nem komponálsz és nem olvasol újra**: a `doc-sync-planner` minden `reconciliation`/`új` tételhez **kész `Csereszöveg`et adott** (lecserélendő jelenlegi részlet + új szöveg). A dolgod ezt **mechanikusan alkalmazni**:
1. Nyisd meg a cél fájlt, és cseréld a `Csereszöveg` „lecserélendő" részletét az „új szöveg"-re (`új` fájlnál: hozd létre a fájlt a megadott tartalommal).
2. Mentés **után** pipáld a terv-tételt (DS10 pipa-szabály).
3. **Fallback:** ha a megadott „lecserélendő" részlet nem illeszkedik egyértelműen (pl. időközbeni eltérés), akkor — és csak akkor — olvasd be a fájl érintett szekcióját, és a subagent „új szöveg"-e alapján végezd el a cserét kézzel. Ez a kivétel, nem a főszabály.

A tipikus tételek (mind a subagent csereszövegével érkezik):
- **`system-overview.md`** — az érintett flow-k/szekvenciák/állapot frissítése; a ciklus mermaid blokkjai a megfelelő képesség-szekcióba, az **elavultat lecserélve** (DS7); a fejléc `Lefedve`/`Utolsó frissítés` bumpolása.
- **`architecture.md` reconciliation** (a mai 09-ből áthozva, DS3): a subagent a ciklusban **változott** részekre adott sebészi csereszöveget (lásd „Az `architecture.md` reconciliation" a hatókör-szabályokért).
- **Komponens README-k** — az ebben a ciklusban **érintett** komponensek `README.md`-jének ellenőrzése/frissítése (lásd „Komponens README-k").
- **`CHANGELOG.md`** — új, részletes, inkrementális ciklus-bejegyzés (DS15, lásd a sablont). A `system-overview.md` csak coverage-markert + linket tart rá, nem duplikál.
- **`design-drift.md`** — az adott ciklus által bevezetett **új** eltérések felvétele; a megszűnt eltérés áthelyezése a „Lezárt eltérések" szekcióba (**nem törlés**) — lásd „Drift-összevetés".
- **`docs-generated/README.md`** — a mappa-index karbantartása: új generált fájl → bekerül; elavult bejegyzés → ki.

### 3.3 Diagram-csere + átkerülés-ellenőrzés (DS7)

A ciklus mermaid blokkjait a megfelelő képesség-szekcióba illeszted, az **elavultat lecserélve**. Bináris/`.drawio` ábra → **link + exportált PNG**. **Kötelező ellenőrzés:** minden forrásbeli ábra átkerült-e — egy sem maradhat le (ez a DS22 magkapu egyik checkje).

### 3.4 Anti-„kezdjük elölről" garde (olcsó-LLM-vezérelv)

**TILOS** a `docs-generated/` érintetlen részeit átfogalmazni, az egész fájlt újraírni, vagy „szebbé tenni" a változatlan tartalmat. A fix-módok (05/07/09) elve itt is él: a doc-sync **reconciliation**, nem újra-komponálás. Csak az **érintett** szekciókat írod át, a `doc-sync-plan.md` tételei szerint.

---

## 4. Bootstrap-ág (DS6, DS8, DS13, DS18) — a mechanika

Akkor fut, ha a `system-overview.md` **nem létezik**. Ez **egyszeri nagy munka** → a start előtt **explicit felhasználói megerősítés kell**. A munkafájlok (`doc-sync-plan.md`, `doc-sync-questions.md`) a gyökér `temp/` mappába kerülnek (nincs aktív ciklus).

A bootstrap mechanikája:

- **2.1 — Forrás-prioritás (DS6):** a gerinc a `specs/roadmap.md` (ciklusonkénti „Viselkedés" + „Teszt kritérium", már konszolidálva) **+** az `architecture.md` §0; a ciklus `spec.md`-ket **főleg a mermaid ábrákért és a részletekért** olvasod. **Forrás vs. áthelyezés:** a forrás-fájlok (roadmap, HLD README, POC-leírás, openapi, SKILL) a bootstrap **forrásai** (olvasandók), **nem** költöznek a `docs-generated/`-be.
- **2.2 — „Későbbi ciklus nyer":** csak az **aktuális állapot** kerül be; ütközésnél a roadmap ciklus-sorrendje szerint a **későbbi ciklus felülír** (pl. `init-hash`, nem `init-cache`). **Megszűnt viselkedés nem kerülhet be.**
- **2.3 — Bounded delegálás:** a forrásgyűjtést **képességenként** a `doc-sync-planner` subagentre delegálod; a fő fázis **komponál**; a fő ágens **kérdez** (DS12).
- **2.4 — `architecture.md` §0 migráció (DS8):** a §0 (rendszerkép, komponens-felelősségek, adatfolyam, demó-út) átkerül a `system-overview.md`-be; az `architecture.md` tisztán a „hogyan épül/fut" marad, kereszt-linkkel. Az `architecture.md` (és a projekt-specifikus extra doksik) **áthelyezése** a `docs-generated/`-be a 8. munkaterv projekt-szintű lépése.
- **2.5 — Fejléc-deklaráció (DS17):** minden bootstrap-elt fájl megkapja a fejléc-blokkot.
- **2.6 — Objektív verifikáció (DS22):** a Réteg 1 magkapu + a Réteg 2 feltételes API-leíró kereszt-ellenőrzés (lásd „Objektív konzisztencia-kapu").
- **2.7 — Felhasználói megerősítés + darabolás (DS18):** fájlonként/képességenként review-zva, a `doc-sync-questions.md`-n keresztül.

> **Bootstrap-figyelmeztetés:** a `docs-generated/` mappát és tartalmát **commitálni kell** (ez a leadandó), **nem** kerülhet `.gitignore`-ba.

---

## Az `architecture.md` reconciliation (a 09-ből áthozva, DS3)

A `docs-generated/architecture.md` a rendszer élő, kumulatív „hogyan épül/fut" dokumentációja. **A doc-sync a kizárólagos gazdája** (a korábbi 06 `TLAST` architecture-író task NYUGDÍJAZVA — DS4). A csereszöveget a `doc-sync-planner` komponálja a teljes ciklus rálátásával (spec/plan/diff + kód); az alábbi szabályok azok a **kritériumok, amelyekre a planner a sebészi patchet készíti**, a fő ágens pedig alkalmazza.

### Mi kerüljön bele
- **Bevezető** — minden frissítésnél felülírjuk: a rendszer aktuális célja, komponensei, az utolsó ciklus változásai.
- **Komponensek leírása** — feladat, konfiguráció, függőségek, deployment mechanizmus.
- **Architektúra diagramok** — aktuális állapotot tükröző Mermaid diagramok. **Elavult ábra nem maradhat.**
- **Adatfolyamok és hívási szekvenciák** — az összes jelentős flow diagramja.
- **Hivatkozások** — minden formális leíróra (OpenAPI YAML, Redis key map, külső konfig). 
- **Kulcsdöntések és indoklásuk.**

### Frissítési szabályok
- Csak azt írd felül, ami **ebben a ciklusban változott** — a többi érintetlen marad (bounded scope, DS9).
- Új komponens → új fejezet. Módosult komponens → az érintett fejezet frissül. Törölt funkció → a hivatkozások eltávolítandók.

### Konzisztencia-ellenőrzés (minden módosított szekció után)
- Van-e más fejezet/ábra, amely ellentmond az éppen frissítettnek?
- Minden diagram az aktuális állapotot mutatja (komponensnevek, portok, kapcsolatok)?
- Minden hivatkozás érvényes (a fájl létezik, a tartalom egyezik)?
- A bevezető konzisztens a többi fejezettel?

Ha ellentmondást találsz, azonnal javítsd.

### Komponens README-k
Az ebben a ciklusban **érintett** komponensek `README.md`-jét ellenőrizd:
- Új komponens: létezik-e a `README.md`? Ha nem, hozd létre.
- Meglévő komponens: ha a ciklus a viselkedésén/portján/indításán/kapcsolatain változtatott — frissítsd.
- A README konzisztens-e az `architecture.md` megfelelő fejezetével?

---

## Drift-összevetés + `design-drift.md` (DS20)

A doc-sync a tiszta as-built leíráson túl **összeveti a megvalósultat a HLD/LLD szándékkal** (a forrás-hierarchia 3. szintje, a `conventions.md` referenciáiból), és a **dokumentált eltéréseket** a `docs-generated/design-drift.md`-be gyűjti. **A `system-overview.md` tiszta as-built marad** — a drift nem keveredik bele.

**Olcsó-LLM-biztos korlát (DS24d):** ciklusonként **csak** az a drift kerül be, amit:
- a ciklus **spec explicit** eltérésként megnevez, **vagy**
- egy konkrét **összevetési checklist** felszínre hoz (a `conventions.md` 3. szintű referenciái vs. as-built).

**Bizonytalan eset → `doc-sync-questions.md`** (Knn), sosem néma tipp. Olcsó LLM **ne** „keressen" nyílt végűen eltérést.

- A megoldott (megszűnt) eltérés **nem törlődik**, hanem a „Lezárt eltérések" szekcióba kerül (visszakövethetőség — a „sosem törlünk" elv).
- A drift-tételek a `doc-sync-plan.md` pipált listájába is bekerülnek.
- Példák: „a HLD RFC 8693 token exchange-et ír, a megvalósítás legacy Keycloak `subject_issuer`-rel"; „a HLD `/init-cache`, a rendszer `/init-hash` (cycle-16)".

---

## `docs-generated/README.md` mappa-index karbantartása (DS21)

A mappa **indexe/manifesztje** — röviden leírja, melyik fájl micsoda (egy-egy soros leírás fájlonként). A doc-sync minden futáskor biztosítja:
- **Új generált fájl a mappában → kötelezően bekerül** az indexbe.
- **Elavult bejegyzés → ki** (a mappa tényleges tartalma == a README bejegyzései, halmaz-egyezés).

A mappa **létrehozásakor** (bootstrap) az index is létrejön. Ez a `docs-generated/README.md` **külön** a `prompts/README.md`-től és a gyökér `README.md`-től.

---

## Objektív konzisztencia-kapu (DS22) + kapu-bukás kezelése (DS10)

A végrehajtás után **kötelező** lefuttatni a kétrétegű, projektfüggetlen kaput. A magkapu **objektív/determinisztikus** (grep, halmaz-összevetés, leltár-párosítás, marker-olvasás) — nincs benne „ítéld meg, jó-e a szöveg", ezért a Réteg 1-et **szkript végzi, nem te grepelsz kézzel**.

### Réteg 1 — mindig futó, generikus magkapu (`ds22-gate-check.py`)

Futtasd a `ds22-gate-check.py`-t a `docs-generated/` mappára. A telepítő a platform-specifikus scripts-mappába másolja (a 10-cycle-status mintájára): Antigravity-nél `.agents/scripts/`, Claude Code-nál `.claude/scripts/`, Cursornál `.cursor/scripts/`, Copilotnál `.github/scripts/`, Codexnél `.codex/scripts/`.

```bash
python3 <platform-scripts-mappa>/ds22-gate-check.py docs-generated/ \
  --rename <régi-név>=<új-név> \
  --marker cycle-NN \
  --changed-file <a ténylegesen módosított fájl neve, ismételhető>
```

- **`--rename`**: a régi→új névpárok a ciklus **DEKLARÁLT** átnevezéseiből jönnek (roadmap/`spec.md`; pl. a cycle-16 neve literálisan `rename-init-cache-to-init-hash` → `init-cache=init-hash`) — **NEM diff-találgatásból** (DS24b). Ha egy átnevezés nincs deklarálva, **nincs auto-következtetés** — nem adsz meg `--rename`-t rá. A szkript automatikusan kihagyja a történeti szekciókat (`CHANGELOG.md` teljes egészében, `design-drift.md` „Lezárt eltérések" szekciója).
- **`--marker` / `--changed-file`**: a `doc-sync-plan.md` alapján ténylegesen módosított fájlokat add meg — a szkript ellenőrzi, hogy a fejléc-blokkjuk az aktuális `cycle-NN`-t mutatja-e (DS17). Az érintetlen fájlokat **ne** add meg (azok maradhatnak korábbi markerrel, ha a plan „nincs teendő" tétele ezt igazolja).
- A szkript emellett **informatív** (nem blokkoló) összegzést ad a `docs-generated/`-ben talált mermaid-blokkok számáról — ez segít neked eldönteni a 2. pontot (lásd lent), de a tényleges pairing-döntést te hozod.

A szkript a 4 originális checkből 3-at teljesen lefed (kemény PASS/FAIL):
1. Rename-maradvány (a fenti `--rename` alapján).
3. Mappa-index halmaz-egyezés (DS21) — a `docs-generated/` tényleges fájllistája **==** a `README.md` bejegyzései.
4. Coverage-marker bump (DS17) — a fenti `--changed-file` alapján.

A **2. pontot** (minden forrásbeli ábra átkerült-e — DS7) a szkript csak informatív blokk-számlálással segíti; a tényleges leltár → cél-párosítást (van-e minden forrás-ábrának párja a kimenetben, bináris/`.drawio` → link + PNG) **neked kell eldöntened** — ez a Réteg 1 egyetlen olyan pontja, ami valódi (bár egyszerű) egyeztetési ítéletet igényel, nem tiszta halmaz-művelet. (A számozás szándékosan követi a fenti eredeti 1–4-es listát, a 2. pont kimarad a szkriptből.)

A szkript kilépő kódja (`0` = mindhárom kemény check PASS, `1` = legalább egy FAIL) + a 2. pont saját ellenőrzésed alapján dől el, hogy a kapu összességében PASS-e.

### Réteg 2 — feltételes, deklaráció-vezérelt kereszt-ellenőrzés

**HA** a `conventions.md` `## Projekt referenciák` szekciója megad egy API-leírót (openapi/swagger/stb.), **AKKOR** a doc-sync összeveti vele a generált interfész/endpoint-leltárt. **Ha nincs deklarálva → ezt a check-et KIHAGYOD, nem blokkol.** (Ezért a `system-overview.md` „endpoint-leltár" szekciója is feltételes.)

### Kapu-bukás → ember-vezérelt javító hurok (DS10)

A kapu **nem** önjavító subagent-hurok (mint a 05/07/09), és **nem is** hurok nélküli. Ha a magkapu **bukik**:
1. A konkrét eltérés a **`doc-sync-questions.md`-be** kerül új `Knn`-ként (determinisztikus eltérés, nem „talán jobb így").
2. A **fő ágens kérdez** / a user dönt vagy javít.
3. Az **érintett `doc-sync-plan.md` terv-tételek + a kapu újrafutnak** → ismétlés, amíg a kapu **zöld** nem lesz (vagy a user explicit leállítja).
4. **Hurok-korlát:** a kapu-javítás emberi döntésre vár (nincs runaway-kockázat); per-eltérés a `doc-sync-questions.md` naplózza, hányadszor kerül vissza ugyanaz.

> **A doc-sync NEM negyedik önjavító hurok.** Külön kategória: **objektív kapu (DS22) + ember-vezérelt javítás (DS10)**, nem LC1–LC4-stílusú subagent-önjavító hurok. A három önjavító hurok (analyze/validate/review) marad **három**.

---

## Kérdés-kezelés (DS10/DS12) — `doc-sync-questions.md`

**Minden döntési pontot és kapu-bukást** azonnal ide kell felvenni új `Knn`-ként, **mielőtt** a felhasználónak feltennéd. A **fő ágens kérdez** egyenként (a subagent nem kérdez közvetlenül).

**Alapszabály: a listából soha nem törlünk. Lezárt kérdést csak `[x]`-szel jelölünk** — a szöveg és a döntés megmarad.

**Iterációs szabályok:**
1. Ha van `[ ]` kérdés, tegyél fel **egyet**, várj a válaszra. Ne zúdítsd rá egyszerre az összeset. **A válaszod végén kötelezően helyezz el egy közvetlen, kattintható linket a `doc-sync-questions.md`-re.**
2. Megválaszolt kérdés → `[x]` + egysoros összefoglaló (`→ ...`), a döntés átvezetve az érintett doksiba és a `doc-sync-plan.md`-be.
3. Új kérdés a lista végére, a következő `Knn` számmal.
4. **Nyitott `[ ]` kérdésnél a fázis MEGÁLL** — ne lépj tovább a válasz nélkül.

**Struktúra** (ha még nem létezik, hozd létre):
```md
# Cycle NN: <cím> — Doc-sync kérdések

- [ ] K01 — [kérdés szövege]
- [x] K02 — [kérdés szövege] → [döntés / válasz röviden]
- [ ] K03 — [kérdés szövege] _(K02-ből merült fel)_
```

---

## Fejléc-blokk minden generált doksin (DS17)

A generált doksik **nem** kapnak `Piszkozat→Kész` életciklust. Helyette minden generált doksi egy rövid **fejléc-blokkot** kap a fájl elején:

```md
> **Lefedve:** cycle-NN-ig · **Utolsó frissítés:** cycle-NN (YYYY-MM-DD) · **Generátor/scope:** <mi alapján tartandó konzisztensen — mit fed le ez a fájl>
```

- A `Generátor/scope` mező egyúttal az érintettség-szabály (DS24e) bemenete: ebből tudja a planner, hogy egy ciklus érinti-e a fájlt.
- A „konzisztens-e" garanciát a **fázis-kapu** (DS22) adja minden ciklusban, nem egy státuszmező.
- A coverage-markert **csak a ténylegesen módosított** fájlokon bumpolod (DS22 Réteg 1 / 4. check).

---

## Sablonok (DS24a) — kitöltendő váz + kész mini-példa

Az alábbi literál sablonokat **kitöltöd**, nem nulláról komponálod. A **bootstrap és az inkrementális ág ugyanezeket** használja.

### `doc-sync-plan.md` tétel

Minden tétel egy sor + (a `reconciliation`/`új` tételeknél) a subagent kész **csereszöveg-blokkja** ugyanoda beírva. **A csereszöveget is a fájlba írod** (nem csak a memóriádban tartod) — így egy megszakadt futás resume-ja (DS10) a fájlból újra tudja alkalmazni, a plannert nem kell újrafuttatni.

**Váz:**
```md
- [ ] <fájl> — <művelet: reconciliation | új | nincs teendő> — <mit pontosan> (scope: <flow/komponens>)
  <reconciliation/új esetén a subagent Csereszöveg-blokkja: lecserélendő jelenlegi részlet → megírt új szöveg>
```
**Kész példa:**
```md
- [ ] docs-generated/system-overview.md — reconciliation — az „Init-hash flow" szekvencia frissítése az /init-hash endpointra; régi /init-cache ábra lecserélve (scope: token-init flow)
- [ ] docs-generated/CHANGELOG.md — új — cycle-16 bejegyzés: /init-cache → /init-hash átnevezés (scope: token-init flow)
- [ ] docs-generated/architecture.md — nincs teendő — a build/deploy nem változott a cycle-16-ban (scope: build/ops)
```

### Fejléc-blokk (DS17)

**Váz:** lásd fent. **Kész példa:**
```md
> **Lefedve:** cycle-16-ig · **Utolsó frissítés:** cycle-16 (2026-06-04) · **Generátor/scope:** as-built működésleírás — a rendszer összes felhasználói/üzleti flow-ja és állapota; forrás: src/ + lezárt spec.md-k (DS19).
```

### `CHANGELOG.md` bejegyzés (DS15)

**Váz:**
```md
## cycle-NN — <cím> (YYYY-MM-DD)

**Mi változott a működésben:** <viselkedés-szintű változás, flow-nként>
**Mi változott a doksikban:** <mely docs-generated/ fájlok + mi>
**Átnevezések (ha van):** <régi → új azonosító>
```
**Kész példa:**
```md
## cycle-16 — init-cache átnevezése init-hash-re (2026-06-04)

**Mi változott a működésben:** a token-init endpoint `/init-cache` → `/init-hash`; a kérés/válasz formátum változatlan.
**Mi változott a doksikban:** system-overview.md (token-init flow szekvencia + állapotmodell), design-drift.md (a HLD `/init-cache` ↔ as-built `/init-hash` eltérés „Lezárt eltérések"-be).
**Átnevezések:** `init-cache` → `init-hash` (endpoint + minden alakváltozat).
```

### `system-overview.md` váz

```md
> **Lefedve:** cycle-NN-ig · **Utolsó frissítés:** ... · **Generátor/scope:** ...

# <Rendszer neve> — Működési áttekintés

> Részletes változásnapló: [CHANGELOG.md](./CHANGELOG.md). Eltérések a tervtől: [design-drift.md](./design-drift.md).

## Mit csinál a rendszer (összefoglaló)
_<1-2 bekezdés: a rendszer feladata, fő képességei.>_

## Képességek és flow-k
_<Képesség szerint strukturálva (NEM ciklusonként). Minden flow-hoz: rövid leírás + konszolidált mermaid (sequenceDiagram / graph), az elavult lecserélve.>_

## Állapotmodell
_<Session, cache/store mapping, token-életciklus.>_

## Endpoint-leltár _(feltételes — csak ha a rendszernek van hálózati interfésze; DS2/DS22 Réteg 2)_
_<Endpoint → rövid leírás. Ha nincs hálózati interfész, ez a szekció elmarad.>_
```

### `design-drift.md` tétel (DS20)

**Váz:**
```md
- **<azonosító>** — Terv: <mit ír a HLD/LLD>. As-built: <mi a megvalósult>. Indok/státusz: <miért; nyitott vagy lezárt>.
```
**Kész példa:**
```md
## Aktív eltérések
- **token-exchange-mód** — Terv: a HLD RFC 8693 token exchange-et ír. As-built: legacy Keycloak `subject_issuer`. Indok: a legacy IdP nem támogatja az RFC 8693-at (POC-korlát).

## Lezárt eltérések
- **init-endpoint-név** — Terv: HLD `/init-cache`. As-built: `/init-hash` (cycle-16). Lezárva: a HLD frissítendő; a rendszer az `/init-hash`-t használja.
```

### `docs-generated/README.md` index-sor (DS21)

**Váz:**
```md
- `<fájlnév>` — <egysoros leírás: mi ez, ki/mikor írja>
```
**Kész példa:**
```md
- `system-overview.md` — As-built működési áttekintés (képességek, flow-k, állapot). A doc-sync (08) tartja karban minden ciklusban.
- `architecture.md` — „Hogyan épül/fut": komponensek, build, deployment. A doc-sync (08) gazdája.
- `CHANGELOG.md` — Részletes, inkrementális ciklus-változásnapló. A doc-sync (08) bővíti.
- `design-drift.md` — A megvalósult rendszer eltérései a HLD/LLD tervtől. A doc-sync (08) karbantartja.
```

---

## Commit + továbblépés a 09-re (1.13)

A kapu zöldre futása után:

1. **Commit** — a `docs-generated/` + a komponens README-k + a ciklus munkafájljai:
   ```bash
   git add docs-generated/ <érintett README-k> specs/cycle-NN-<cycle-name>/doc-sync-plan.md specs/cycle-NN-<cycle-name>/doc-sync-questions.md
   git commit -m "cycle-NN: 08-doc-sync"
   ```
   _(Bootstrapnél a `docs-generated/` + az áthelyezett fájlok + a hivatkozás-átírások; a gyökér `temp/` munkafájlok sorsát a 8. munkaterv dönti el.)_

2. **Jelezd a felhasználónak a következő lépést:**
   > *"A dokumentáció szinkronban van a megvalósult rendszerrel, a konzisztencia-kapu zöld. Folytathatjuk a 9. lépéssel: review & merge (09). Az új fázis megkezdése előtt mindenképpen futtass egy `/clear` parancsot a kontextus kiürítéséhez, majd használd ezt a parancsot:*
   > ```
   > /bs-review-and-merge input: @specs/cycle-NN-<cycle-name>
   > ```"*
   > **A válasz végén helyezd el a `docs-generated/system-overview.md` (és a `doc-sync-plan.md`) közvetlen, kattintható linkjét.**