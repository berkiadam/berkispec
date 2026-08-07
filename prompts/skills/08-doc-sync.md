---
phase: 08
name: bs-doc-sync
description: "berkispec - 08. Használd a validáció után, merge előtt (Phase 08), ha a tasks.md/plan.md/spec.md mind 'Kész'. A kódváltozásokat a 'docs-generated/' rendszer-dokumentációba és az érintett komponens-README-kbe szinkronizálja (doc-sync-planner subagent, design-drift ellen), karbantartja a 'specs/test-conventions.md' visszatérő teszt-elvárás regisztert, és létrehozza a 'doc-sync-plan.md'-t."
prerequisites:
  - "specs/cycle-NN-<name>/tasks.md státusz: Kész"
  - "specs/cycle-NN-<name>/plan.md státusz: Kész"
  - "specs/cycle-NN-<name>/spec.md státusz: Kész"
output:
  - "docs-generated/ konzisztens állapota (system-overview.md, architecture.md, CHANGELOG.md, design-drift.md, README.md mappa-index + a mappa többi fájlja)"
  - "specs/test-conventions.md — a visszatérő teszt-elvárások és a hozzájuk tartozó receptek élő regisztere (TC1)"
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

2. **Munkafa-ellenőrzés (csak VCS esetén):** futtasd `git status --short`. Ha van commitálatlan változtatás, listázd, és kérdezd meg egy körben, hogy commitáljam-e most vagy folytassam — várj a válaszra. (A doc-sync a ciklus diffjét nézi a fő branch-hez; tiszta munkafa nélkül a diff félrevezető. No-VCS projektben kimarad.)

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

**A `docs-generated/`-en kívül egy további fájl gazdája a doc-sync:** a **`specs/test-conventions.md`** (a `specs/roadmap.md` mellett, **nem** a `docs-generated/`-ben). Ez a mappa-bejárás (DS11) és a DS22 mappa-index halmaz-egyezés **hatókörén kívül** van — saját szabályai vannak, lásd „A `specs/test-conventions.md` karbantartása (TC1–TC11)".

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
2. **Tervkészítés:** a `doc-sync-planner` subagent megírja a `doc-sync-plan.md`-t (per-fájl pipálható terv) — a `specs/test-conventions.md` tételeivel együtt.
3. **Mechanikus végrehajtás:** a fő ágens végrehajtja a terv `[ ]` tételeit, fájlonként mentve és pipálva.
4. **Objektív konzisztencia-kapu (DS22):** a magkapu lefuttatása; bukáskor ember-vezérelt javító hurok (a kérdés a `doc-sync-questions.md`-be). Ezt követi a `test-conventions.md` saját kapuja (TC8, `tc8-gate-check.py`).
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
- **`specs/test-conventions.md`** — promóció / `Utolsó futás` bump / elavult tétel törlése (TC1–TC11). Ez a fájl a `docs-generated/`-en **kívül** van; ha még nem létezik, a TC6 bootstrap-út fut rá — akkor is, ha a `system-overview.md` már létezik.

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

> **Tulajdon-határvonal (DS4) — a komponens létezése dönt, nem a fájltípus.** A **meglévő** komponensek README-je a **doc-sync tulajdona**: a 03 nem tervezi be, a 04 nem generál rá taskot, az implementáció nem írja — **te frissíted**. Egy **új** komponens első `README.md`-je viszont a komponens felépítésének része, ezért azt a **03/04/06 hozza létre** (a plan `Tervezett módosítások`-ban szerepel); neked ott már csak ellenőrizned kell.

Az ebben a ciklusban **érintett** komponensek `README.md`-jét ellenőrizd:
- **Új komponens** (ebben a ciklusban jött létre): a `README.md`-t az implementáció már létrehozta — ellenőrizd, hogy létezik és konzisztens-e. Ha kivételesen hiányzik, pótold.
- **Meglévő komponens:** ha a ciklus a viselkedésén/portján/indításán/kapcsolatain változtatott — **te frissítsd** (ez nem az implementáció elmaradása, hanem a te feladatod).
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

## A `specs/test-conventions.md` karbantartása (TC1–TC11)

### TC1 — Mi ez, és mi NEM

A `specs/test-conventions.md` a projekt **visszatérő teszt-elvárásainak és a hozzájuk tartozó receptek** élő regisztere: az a tudás, ami pár ciklus után „alap" — mit kell minden körben letesztelni, milyen sorrendben, milyen paranccsal, milyen környezetben. A doc-sync a **kizárólagos gazdája**, a `specs/roadmap.md` mellett él (**nem** a `docs-generated/`-ben, mert **normatív** input a jövő ciklusainak, nem leíró as-built doksi).

> **🔴 TC1/a — Ez NEM futtatható forrás.** A regiszterből **semmi nem fut le automatikusan**. A `test-runner` subagent ezt a fájlt **nem olvassa** — kizárólag a `plan.md` Tesztelési stratégia / Regressziós érintettség szekcióit. Egy recept akkor és csak akkor hajtódik végre, ha a `02`/`03` fázis azt tudatosan **beemelte** az adott ciklus `spec.md`/`plan.md`-jébe (emberi jóváhagyással). A regiszter **memória**, a `plan.md` az **egyetlen futtatási igazság**.

**Mi nem tartozik ide:** a `conventions.md` rögzíti, **hogyan** tesztelünk (eszközök, mappastruktúra, futtatási parancsok, elvek) — azt itt **nem ismételjük**. A `plan.md` rögzíti, mi az **új** az adott ciklusban. Ez a fájl azt rögzíti, **mit és mikor kötelező** tesztelni, komponensenként, as-built.

### TC2 — Szerkezet: koordináta-blokk + pontosan három szekció

A fájl **`## 0. Koordináták`** blokkal kezdődik (TC13 — kötelező), utána **három számozott** szekció következik, se több, se kevesebb. A 2. és 3. szekció tételei az 1. szekcióra hivatkoznak (nem duplikálják a koordinátákat), az 1. szekció receptjei pedig a 0. blokk adataira.

0. **Koordináták** — környezetek, URL-ek/portok, health endpointok, teszt-userek, kliensek, scope-ok, paraméterek, env-fájl pointerek. **Egy helyen, kereshetően.**
1. **Recept-regiszter** — komponensenként/lépésenként: repo-útvonal, image-név, registry-cél, namespace/pod, **indítás**, példa REST/`curl` hívások, build/deploy parancsok. A konkrét URL-eket, usereket és paramétereket **a 0. blokkból veszi** (ott az igazság, itt a hivatkozás).
2. **Minden körben szükséges lokális (mock alapú) tesztek** — az 1. szekció receptjeire hivatkozva.
3. **Minden körben szükséges integrációs / E2E tesztek** — az 1. szekció receptjeire hivatkozva.

A sablont lásd a **Sablonok** szekcióban.

> **⚠ „Prózát ne írj" — mit jelent és mit NEM (TC2/a).** A tiltás a **narratív magyarázatra** vonatkozik: bevezetők, indoklások, „ebben a ciklusban azért döntöttünk így…", tanulságok, összefoglalók. Ezek nem valók ide — a fogyasztó a `02`/`03` fázis, nem az olvasgató ember.
>
> **NEM vonatkozik a tesztesetek részletezésére.** A 2./3. szekció **táblázata index**, nem maga a teszteset: egy egysoros cella soha nem elég ahhoz, hogy a tesztet valaki reprodukálja. Ezért **minden promótált tételhez kötelező egy strukturált részletező blokk** a táblázat alatt (`### L01 — …` / `### I01 — …`), **Cél / Előfeltétel / Lépések / Elvárt eredmény** mezőkkel (TC10/b). Ez nem próza, hanem **struktúra** — a reprodukálhatóság minimuma.
>
> Rossz értelmezés (ez a hiba fordult elő élesben): a szabályt úgy venni, hogy *„csak táblázat lehet a fájlban"*, és a tesztek leírását egysoros cellákra zsugorítani. Az így keletkező regiszterből a következő ciklus nem tudja lefuttatni a tesztet.

### TC3 — Promóció: mi kerül be (bizonyíték-alapú)

**Ne ítéld meg „érzésre", hogy egy teszt „alapvető-e".** Egy tétel akkor promótálódik a 2./3. szekcióba, ha az alábbiak **valamelyike** teljesül:

1. **Empirikus jel (elsődleges):** a teszt/recept egy **korábbi** ciklusban keletkezett, és **ebben** a ciklusban is szerepelt a `plan.md` `Regressziós érintettség` táblájában vagy tényleges futtatásra került — azaz a gyakorlatban bizonyította a ciklus-független relevanciáját.
1.a **Áthozatal-jel (erős empirikus jel, TP3/a):** a ciklus `plan.md`-je egy receptet/előfeltételt **egy korábbi ciklus `plan.md`-jéből** emelt át (a plan-ben `_(forrás: cycle-NN plan.md)_` provenance jelöli, jellemzően token-beszerzés, stack-indítás, egyedi komponens build/deploy, seed). Ez **bizonyíték a ciklus-független relevanciára**: ha a 03 fázisnak vissza kellett nyúlnia egy régi planhez, akkor a tétel hiányzik a regiszterből. **Ezeket sorold fel elsőként a promóciós ajánlatban (TC12)** — a fájl 0. blokkjába a koordinátáival, az 1. szekcióba a receptjével együtt.

2. **Emberi döntés (mindig kötelező):** a felhasználó a `doc-sync-questions.md`-ben megerősítette, hogy a tétel legyen tartós elvárás. **Ezt minden ciklusban tételesen fel kell kínálnod** — lásd **TC12 (promóciós ajánlat)**: az empirikus jel a *javaslatodat* adja, a döntést a felhasználó hozza.

**A promóció HÁROM dolgot jelent, nem egyet (TC3/a).** Egy tétel akkor van promótálva, ha mindhárom megvan — a táblázatsor önmagában **nem** promóció:

1. **Táblázatsor** a 2./3. szekcióban (ID, önhordó egysoros viselkedés, recept-hivatkozás, `Utolsó futás`) — ez az **index**;
2. **Részletező blokk** a táblázat alatt (`### <ID> — <cím>`, Cél / Előfeltétel / Lépések / Elvárt eredmény) — ez a **teszteset** (TC10/b);
3. **Recept** az 1. szekcióban (`Indítás`, `Példa hívás`, parancsok — TC11), amire a tétel hivatkozik, plus a hozzá tartozó koordináták a 0. blokkban (TC13).

**Recept (1. szekció) csak akkor kerül be, ha ebben a ciklusban tényleg lefutott és zöld volt** (a `test-report/` a bizonyíték). **Kitalált, nem verifikált parancsot TILOS beírni** — ha egy koordináta hiányzik vagy bizonytalan, az `doc-sync-questions.md` kérdés, nem néma tipp.

Ami egyik feltételt sem teljesíti, **nem kerül be** — az egyetlen ciklusra szóló teszt marad a ciklus `plan.md`-jében.

### TC4 — A fájl élő snapshot, nem napló (karbantartás + törlés)

- Minden tétel mellett kötelező az **`Utolsó futás: cycle-NN`** marker. Ez azt mutatja, mikor futott a tétel utoljára zölden.
- A fájl **mindig az aktuális állapotot** tükrözi. Ha egy komponens megszűnt, átalakult, vagy a tétel a fejlesztés miatt már nem értelmezhető, a tétel **törlődik** — nem archiválódik, nem kap „elavult" megjegyzést. **A fájl nem hízhat monoton.**
- **Az információ nem vész el:** a törlés ténye és oka a `CHANGELOG.md` ciklus-bejegyzésébe kerül (DS15). Ezért itt **nem** érvényes a „sosem törlünk" elv, ami a `design-drift.md`-re és a kérdés-listákra igen.
- **A törlés látható:** minden törlendő tétel **külön terv-tételként** megjelenik a `doc-sync-plan.md`-ben, így a felhasználó látja és pipálja, mielőtt megtörténik. Csendben nem törölhetsz.
- **Staleness-jelzés:** ha egy tétel `Utolsó futás` markere **3 vagy több ciklussal** régebbi az aktuálisnál, vedd fel `doc-sync-questions.md` kérdésként: *„A(z) `<tétel>` utoljára a cycle-NN-ben futott. Még érvényes elvárás, vagy törlendő?"* Környezeti koordinátát (URL, pod, namespace) **nem tudsz automatikusan verifikálni** — ezért a staleness-marker az egyetlen védőháló ellene.

### TC5 — Titok-osztályozás (KÖTELEZŐ, hatókör-alapú)

Ez a fájl **verziókezelt és merge-elt** — ami bekerül, az a git history-ban marad. A döntés **nem** szubjektív veszélybecslés, hanem egyetlen mechanikus kérdés: **„személyt hitelesít, vagy osztott platformhoz ad hozzáférést?"**

| **Bekerülhet** (hatóköre az eldobható dev-példány, nem személyhez tartozik) | **NEM kerülhet be — csak pointer** (személyt hitelesít vagy osztott platformhoz ad hozzáférést) |
|---|---|
| seedelt dev teszt-userek + jelszavaik, dev IdP (pl. Keycloak) realm-admin, lokális DB-user, mock-service API-kulcs, dev client-secret | klaszter/OpenShift login, registry (pl. Nexus) push-credential, VPN, cloud IAM, git/CI token, **bármi, ami más környezetben (test/prod) is működik** |

- A bal oszlop tételei jellemzően **már ma is a repóban vannak** (seed/realm-import fájlok, Clean Slate szabály) — összegyűjtésük nem új expozíció.
- **Pointer formája:** *„a credential a `<hely>`-ből szerezhető meg"* — soha nem az érték.
- **Bizonytalan eset → kérdés** a `doc-sync-questions.md`-be, és amíg nincs válasz, **pointert írsz, nem értéket**. A default a kihagyás.

### TC6 — Bootstrap: ha a fájl nem létezik (akár a 30. ciklusban)

A berkispec bekerülhet egy **már futó projektbe**, ahol ez a fájl soha nem létezett. **Ne üres lappal kezdj, és ne az embert kérdezd ki a nulláról** — először állíts össze egy **javaslatot** abból, ami már megvan (ezt a `doc-sync-planner` végzi):

- a lezárt ciklusok `spec.md` / `plan.md` fájljainak `Teszt specifikáció`, `Tesztelési stratégia`, `E2E infrastruktúra` és `Regressziós érintettség` szekciói — itt vannak a visszatérő tételek;
- a lezárt ciklusok `plan-questions.md` fájljai — **itt vannak a környezeti koordináták**, amik eddig ciklusonként elszivárogtak;
- a meglévő `test/` mappa és E2E compose fájl, valamint a `conventions.md` `## Projekt referenciák` szekciója.

Ezután a **javaslatról** folytatsz párbeszédet a `doc-sync-questions.md`-n keresztül: *„Ezeket találtam visszatérő elvárásként; melyik érvényes még, mi maradt ki, és mi a helyes URL / pod / paraméter ma?"* — javítani sokkal könnyebb, mint diktálni.

> A `test-conventions.md` bootstrapja **független** a `docs-generated/` bootstrap-ágától: akkor is le kell futnia, ha a `system-overview.md` már létezik (inkrementális ág). A fájl **hiánya nem hiba** korai ciklusokban — ha nincs mit promótálni (nincs TC3 szerinti tétel), a fájl **ne jöjjön létre**; ekkor a `doc-sync-plan.md` „nincs teendő" tétele rögzíti az indokot. Üres vázat **ne** hozz létre — egy üres fájlt a következő fázis hajlamos találgatással kitölteni.

### TC7 — Kérdés-hatókör: bootstrap vs steady state

**Minden ciklusban kérdezni kell**, hogy mi kerüljön be — de a kérdés terjedelme eltér:

- **Első futás (bootstrap):** széles interjú a TC6 szerinti javaslat alapján. Egyszeri, megéri.
- **Minden további ciklus (steady state):** **ne** nyisd újra a teljes beszélgetést. Egy **rövid, célzott megerősítés** a doc-sync javaslatáról: *„Ezt promótálnám, ezt törölném, ezeket bumpolom — jó?"* A felhasználó pipál vagy javít. A javaslat maga a `doc-sync-plan.md` tételeiben áll, a kérdés a `doc-sync-questions.md`-ben.

**Mindkét esetben kötelező a TC12 promóciós ajánlat** — a ciklus tesztjeinek tételes felkínálása döntésre. A bootstrapnál ez a széles interjú része; steady state-ben ez a „rövid, célzott megerősítés" konkrét formája.

### TC13 — Koordináta-blokk a fájl elején (KÖTELEZŐ)

**A fájl első blokkja a `## 0. Koordináták`** — itt gyűlik össze minden környezet-, hozzáférés- és paraméter-adat, **egy helyen, kereshetően**. Aki tesztelni akar, ne recepteken lapozgasson végig azért, hogy megtalálja, melyik porton fut a mock, vagy mi a teszt-user jelszava.

**Kötelező tartalom — három tábla:**

| Tábla | Mit gyűjt |
|---|---|
| **Környezetek és végpontok** | környezet (lokális / dev / …), komponens, URL + port, health endpoint |
| **Teszt-userek, kliensek, titkok** | környezet, név/azonosító (user, `client-id`, service account), titok **vagy pointer**, scope/szerep |
| **Paraméterek és env-fájlok** | paraméter- és környezeti változó nevek, érték vagy pointer, hol használjuk |

**Szabályok:**

1. **Ez az igazságforrás.** Ha egy URL, user vagy paraméter itt szerepel, a receptek (1. szekció) **hivatkoznak rá**, nem másolják. Ha két helyen más érték áll, az hiba — a 0. blokk nyer, a receptet javítsd.
2. **TC5 titok-szabály itt is él.** Dev-hatókörű teszt-jelszó beírható; **osztott platform credential (klaszter, registry, VPN, IAM, éles token) SOHA** — helyette pointer: `pointer: .env.dev → TMP_S2S_SECRET` vagy `pointer: jelszókezelő / Vault`. A TC8 titok-checkje ezt a blokkot is nézi.
3. **Csak verifikált érték (TC3).** Ami ebben a ciklusban nem futott le és nem is erősítette meg a felhasználó, az nem kerül be. Bizonytalan koordináta → `doc-sync-questions.md` kérdés.
4. **Környezetenként külön sor.** A „localhost:8080 vagy a dev host" típusú összemosás használhatatlan — a `Környezet` oszlop kötelező.
5. **Elavulás.** Ha egy koordináta a ciklusban bizonyítottan megváltozott (más port, más host, más user), **itt kell frissíteni** — és a rá hivatkozó receptek automatikusan helyesek maradnak. Ez a blokk fő haszna.

A TC8 kapu ellenőrzi, hogy a blokk **létezik, a fájl elején áll, és van benne kitöltött adatsor** — üres vagy placeholderes tábla bukik.

### TC12 — Promóciós ajánlat: a ciklus tesztjeit tételesen felkínálod (KÖTELEZŐ)

**A promóció soha nem néma döntés.** Minden doc-sync futásban **fel kell sorolnod a ciklus tesztjeit**, és **meg kell kérdezned a felhasználót, melyiket emeled be projekt szintre** a `test-conventions.md`-be. Sem a beemelés, sem a kihagyás nem történhet kérdés nélkül — a TC3 bizonyíték-szabály azt mondja meg, **mit javasolsz**, de a döntés a felhasználóé.

**1. A jelöltlista összeállítása.** Gyűjtsd össze a ciklus tesztjeit három forrásból:
- `plan.md` → `Tesztelési stratégia` és `Regressziós érintettség`;
- `tasks.md` → a `[RED]` / `[CHECK]` / `TREG` taskok;
- `test-report/` → **mi futott le ténylegesen**: a `validate-decision.md` körönkénti lépés-táblája, a `validate/round-NN/` mappák teszt-eszköz riportjai, és az implementáció alatti ellenőrzésekhez az `implement/check-log.md` — ezek a bizonyítékok.

**Csak az kerülhet a listára, ami ebben a ciklusban tényleg lefutott és zöld volt** (TC3). Ami nem futott, azt ne kínáld fel — jelezd külön sorban, hogy miért maradt ki.

**2. Minden jelölthez készítsd elő a döntéshez szükséges információt** — a felhasználónak ne kelljen visszakeresnie semmit:
- **önhordó, viselkedés-szintű leírás** (TC10 szerint megfogalmazva — ez lesz a tétel szövege, ha bekerül);
- **melyik szekcióba menne**: 2. (lokális/mock) vagy 3. (integrációs/E2E);
- **milyen recept kell hozzá**: meglévő `R-ID`, vagy **új recept** (és akkor mi hiányzik belőle — indítás, példa hívás);
- **javaslat + egysoros indok**: `promótálandó` (miért ciklus-független) vagy `marad ciklus-lokális` (miért egyszeri).

**3. A kérdés — EGY körben, a `doc-sync-questions.md`-be.** Ne tegyél fel tesztenként külön kérdést: egy `Knn` tétel, benne a teljes táblázat, és egy egyszerű válaszformátum:

```md
- [ ] K03 — Melyik ciklus-tesztet emeljem be projekt szintre a `test-conventions.md`-be?

| # | Viselkedés (így kerülne be) | Szekció | Recept | Javaslat | Indok |
|---|---|---|---|---|---|
| 1 | A mock `/start-process` 201-et ad érvényes `processName`-re, és 400-at hiányzó body-ra | 2 | R02 | promótálandó | a mock szerződése minden ciklusban él |
| 2 | A `/verify` 403-at ad `TMP_031` errorCode-dal lejárt tokenre | 3 | **új recept kell** (indítás + példa hívás hiányzik) | promótálandó | minden auth-változás érinti |
| 3 | A cycle-24-es migrációs script egyszeri lefutása | 2 | R01 | marad ciklus-lokális | egyszeri adatmigráció, nem ismételhető |

_Nem futott le ebben a ciklusban (ezért nem jelölt): `<teszt>` — `<miért>`._

**Válaszként elég a sorszámok felsorolása** (pl. „1, 2" vagy „mindet" / „egyiket sem"). A kihagyottakat a döntés-naplóba írom, hogy a következő ciklusban ne kérdezzek rá újra.
```

**4. Várd meg a választ.** Ez **blokkoló kérdés**: promóció nem történik válasz nélkül, és a fázis sem zárható le nyitott `[ ]` kérdéssel. Ha a felhasználó egy tételre nemet mond, **ne vitatkozz** — rögzítsd.

**5. A válasz átvezetése:**
- **Igen** → a tétel bekerül a 2./3. szekcióba (TC10 szerinti önhordó szöveggel), és ha új recept kell, azt is felveszed (TC11: indítás + példa hívás + takarítás, csak verifikált parancsokkal).
- **Nem** → a tétel a **döntés-naplóba** kerül a fájl végén, hogy a következő ciklus ne kérdezzen rá újra:

```md
## Nem promótált jelöltek (döntés-napló)

- A cycle-24-es migrációs script egyszeri lefutása — döntés: `nem promótálandó` (egyszeri adatmigráció) · cycle-24
```

Ez az appendix **nem** számozott szekció (a TC2 szerkezet érintetlen marad): sima felsorolás a `## 3.` szekció után. **Ha egy tétel itt szerepel, a következő ciklusban ne kínáld fel újra** — kivéve, ha a viselkedése lényegesen megváltozott; akkor új jelöltként, az új leírással jöhet.

**Steady state rövidítés (TC7):** a 2–5. lépés minden ciklusban lefut, de ha a ciklusnak 1–2 tesztje van, a táblázat is 1–2 soros — a kérdés így is kötelező, csak rövid.

### TC10 — Önhordó tételek: a regiszter nem hivatkozik a ciklus-dokumentumokra

**A `test-conventions.md` egyedül is értelmes kell legyen.** Az olvasója (a `02`/`03` fázis egy friss kontextusban, vagy egy új kolléga) **nem fogja megnyitni** a régi `spec.md`-ket — azok a ciklussal együtt lezárultak, a számozásuk pedig ciklusonként újraindul.

**🔴 TILOS a „Mit ellenőriz" mezőben** (és a recept-nevekben):
- **spec-szekció sorszám átemelése:** *„1.2. FlowX Backend Mock negatív és pozitív tesztek"*, *„2.3. Teljes Dev integrációs teszt"* — a `1.2.` egy másik dokumentum belső számozása, itt semmit nem jelent;
- **ciklusra hivatkozás azonosítóként:** *„Cycle 19 init-hash E2E integrációs tesztek"*, *„Level 2 E2E lokális Keycloak tesztek"* — melyik viselkedésről van szó? A ciklus-szám a `Utolsó futás` / `Bizonyíték` oszlopba való, nem a leírásba;
- **fájlnév mint leírás:** *„external-apigee-client unit teszt"* — mit ellenőriz az a teszt?
- **hivatkozás korábbi spec/plan dokumentumra** („a spec.md 3. pontja szerint").

**Helyette: viselkedés-szintű, önhordó megfogalmazás** — milyen bemenetre mi a helyes kimenet. Például:

| Rossz (hivatkozó) | Jó (önhordó) |
|---|---|
| `1.2. FlowX Backend Mock negatív és pozitív tesztek` | `A mock /start-process 201-et ad érvényes processName-re, és 400-at hiányzó body-ra` |
| `Cycle 19 init-hash E2E integrációs tesztek` | `A TMP init-hash végpont ugyanazt a hash-t adja vissza ugyanarra a payloadra, és 409-et ismételt initre` |
| `Mobile Bank external apigee client unit teszt` | `Az Apigee kliens 3× újrapróbál 503-ra, és a 4. hibánál felfelé dobja a hibát` |
| `2.1. Dev Keycloak SPI működés-ellenőrzés` | `A dev Keycloak SPI a /health/ready-n 200-at és `spi-ok` státuszt ad` |

#### TC10/b — A teszt részletes leírását át kell hozni (nem csak a címét)

**A promótált teszt szöveges specifikációja nem veszhet el.** A ciklus `spec.md`-je / `plan.md`-je tartalmazza a teszteset célját, lépéseit és elvárt eredményét — **ezt a tartalmat hozd át** a regiszterbe, a táblázat alatti részletező blokkba. A táblázat egysoros cellája csak mutató; a következő ciklus a blokkból fogja tudni **lefuttatni** a tesztet.

**Kötelező formátum — tételenként egy blokk a szekció táblázata alatt:**

```md
### L01 — A mock `/start-process` 201-et ad érvényes kérésre

- **Cél:** a FlowX mock szerződése stabil marad — a kliens a dokumentált válaszra épülhet.
- **Előfeltétel:** `R02` fut (a felhúzás ott van leírva) · a `0.` blokk `lokális` sora szerinti port.
- **Lépések:**
  1. `POST /start-process` a `{"processName": "onboarding"}` payloaddal.
  2. Ugyanez üres body-val.
- **Elvárt eredmény:** az 1. lépésre `201` + `{"processInstanceId": "<uuid>"}`; a 2. lépésre `400` + `MISSING_BODY` errorCode.
```

**Hűen, de önhordóra normalizálva — NE vakon másolj.** A `spec.md`/`plan.md` szövege gyakran olyan elemeket is tartalmaz, amelyek itt értelmetlenek vagy tiltottak. Az áthozatalkor **kötelező** ezeket kigyomlálni:

| Amit a forrásszöveg tartalmazhat | Mit csinálsz vele |
|---|---|
| spec-szekció sorszám (`1.2.`), ciklus-hivatkozás (`a cycle-19-es teszt`) | **törlöd** — TC10 tiltja |
| „lásd fent", „a fenti pont szerint", spec-belső kereszthivatkozás | **feloldod**: beírod, mire hivatkozik |
| konkrét titok (osztott platform credential) | **pointerre cseréled** — TC5 |
| ciklus-specifikus egyszeri lépés (migráció, egyszeri adatfeltöltés) | **elhagyod** — nem visszatérő elvárás |
| nem verifikált / feltételezett lépés | **nem hozod át**, kérdés a `doc-sync-questions.md`-be — TC3 |

A **tartalom** (cél, lépések sorrendje, elvárt értékek) viszont **maradéktalanul** átjön: ha a specben három lépés és két elvárt hibakód szerepelt, itt is három lépés és két hibakód lesz. Rövidíteni „a lényegre" **nem szabad** — pont az a lényeg, ami a reprodukáláshoz kell.

**Átírás visszamenőleg:** ha a fájlban már van hivatkozó tétel vagy részletező blokk nélküli sor, **a következő doc-sync futásban írd át** önhordóra. Ha a viselkedés a tétel szövegéből és a tesztfájlból sem derül ki egyértelműen, az **kérdés a `doc-sync-questions.md`-be** (ne találgass) — a tétel addig marad, de megjelölve.

### TC11 — Futtatható koordináták: indítás + példa hívás kötelező

**A recept attól recept, hogy egy idegen le tudja futtatni** — nem attól, hogy megnevezi a tesztfájlt. Egy `npm test` sor önmagában nem recept: nem mondja meg, mi kell hozzá, hogyan hívom a végpontot, és honnan tudom, hogy jó.

**Minden `R-ID` recept kötelező elemei:**

1. **`Indítás`** — hogyan húzom fel azt a környezetet, amit ez a recept igényel: konkrét parancs (`docker compose -f … up -d`, `podman run …`, `npm run dev`, `oc port-forward …`), plusz **hogyan ellenőrzöm, hogy feláll** (health endpoint + várt válasz). Ha a recept nem igényel környezetet (tiszta unit teszt), írd ki explicit: `N/A — nem igényel futó környezetet`. Üresen hagyni nem opció.
2. **`Példa hívás`** — ha a recept HTTP/gRPC/CLI végpontot érint: **legalább egy tényleges hívás**, teljes URL-lel, headerekkel, payloaddal és a **várt válasszal**. `curl`, vagy `.http` (VS Code REST Client / IntelliJ) blokk — az utóbbi akkor jobb, ha a projektben már vannak `.http` fájlok (akkor **hivatkozz a fájlra is**: `test/http/token-exchange.http`). Ha a hívás tokent igényel, **a token megszerzésének hívása is kerüljön ide** (az „Authorization: Bearer …" önmagában nem futtatható).
3. **`Leállítás / takarítás`** — mit kell leállítani/törölni a futtatás után (különösen `osztott-remote` hatókörnél, TC5/TC3).

**Az előfeltételek nem lóghatnak a levegőben.** A 2./3. szekció `Előfeltétel` oszlopában a *„lokális keycloak fut"*, *„mock stack fut"*, *„VPN kapcsolat aktív"* típusú szöveg **önmagában értéktelen** — meg kell mondani, **hogyan** teljesítem. Ezért az előfeltétel vagy **`R-ID`-re hivatkozik** (amelynek van `Indítás` blokkja), vagy a hivatkozott recept `Indítás` blokkja tartalmazza. Ha egy előfeltételhez nincs recept (pl. a lokális Keycloak indítása sehol nincs leírva), **vegyél fel rá új receptet** — ez tipikusan a leghasznosabb tétel az egész regiszterben.

> **A TC3 verifikáció itt is él:** csak olyan indító parancsot és példa hívást írj be, ami **ebben a ciklusban tényleg lefutott** (a `test-report/` a bizonyíték), vagy amit a felhasználó a `doc-sync-questions.md`-ben megerősített. Kitalált `curl` rosszabb, mint a hiányzó — a következő ciklus rá fog építeni.

### TC9 — Kötelező teszt-riport tétel (TR3) — a felhasználóval egyeztetve

**Minden ciklusban kötelező riport-artefaktum kerül a `specs/cycle-NN-<name>/test-report/` mappába** — a teszt-eszköz saját, megnyitható riportja (Allure/Playwright HTML, pytest-html, JUnit XML, coverage). A riportok **körönkénti almappákban** élnek (TR5): `test-report/validate/round-NN/`, illetve a 09 re-validate köreinél `test-report/review/round-NN/`; a `test-report/` gyökerében a naplók vannak (`validate-decision.md`, `implement/check-log.md`). A **parancs és az artefaktum-név egyetlen igazságforrása a `conventions.md` `## Teszt-riportolás` táblája** (a 00 fázis tölti ki a felhasználóval); a `07-validate` ezt determinisztikus kapuval (`report-gate-check.py`) kéri számon. A regiszterben ezt **nem duplikáljuk** (TC1) — itt csak az elvárás és a forrás-hivatkozás áll, a 2. és 3. szekció **Kötelező riport (TR3)** sorában.

**A doc-sync kötelező teendői minden futásban:**

1. **Olvasd be** a `conventions.md` `## Teszt-riportolás` szekcióját és a ciklus `test-report/` mappájának tényleges tartalmát — a kör-almappákkal együtt (a **legutolsó** `validate/round-NN/` ill. `review/round-NN/` mutatja, mi futott a záró körben).
2. **Vesd össze a kettőt.** Ha a ciklusban olyan teszt-kategória vagy eszköz futott, amely **nincs benne a táblában** (pl. most került be az Allure, vagy egy új E2E réteg), az **hiányos projekt-konvenció**.
3. **Ilyenkor KÖTELEZŐ kérdés a felhasználónak** — vedd fel a `doc-sync-questions.md`-be, és **várd meg a választ** (ez nem néma javítás):
   > *„A ciklusban a(z) `<eszköz>` futott, de a `conventions.md` `## Teszt-riportolás` táblájában nincs hozzá riport-sor. Milyen riportot generáljon, milyen paranccsal, és milyen néven kerüljön a ciklus `test-report/` mappájába? (Ha nem kell riport ehhez a kategóriához, azt is rögzítem.)"*
4. **A válasz átvezetése — szűk, engedélyhez kötött kivétel:** a `conventions.md` egyébként a 00 fázis tulajdona, de a felhasználó **explicit válasza után** a doc-sync frissítheti **kizárólag a `## Teszt-riportolás` táblát** (új sor / módosított artefaktum-név). Más szekcióhoz ne nyúlj, és válasz nélkül ne írj bele.
5. **A regiszter oldalán** a 2./3. szekció `**Kötelező riport (TR3):**` sora tükrözze a tábla aktuális állapotát (artefaktum-név + `forrás: conventions.md → ## Teszt-riportolás`). A TC8 kapu 5. checkje ezt ellenőrzi.
6. **Ha a záró kör mappájában nincs meg a deklarált artefaktum** (pl. egy régebbi ciklusból, vagy mert a riportok még a `test-report/` gyökerében vannak a körönkénti bontás bevezetése előttről), az **nem a doc-sync javítandó hibája** — jelezd az összefoglalóban, hogy a `07-validate` TR3 kapuja azt a ciklust nem fogta meg (régi ciklus a kapu bevezetése előttről), és lépj tovább.

> **A TC6 bootstrap-szabály él:** ha nincs mit promótálni, a `test-conventions.md` **ne jöjjön létre** pusztán a riport-sor kedvéért. A riport-elvárás ilyenkor a `conventions.md`-ben él, ami mindig létezik.

### TC8 — A fájl saját kapuja (`tc8-gate-check.py` — szkriptelt)

A DS22 magkapu a `docs-generated/`-re fut, ez a fájl azon **kívül** van, ezért **saját kapuja** van. A kapu **teljesen szkriptelt** — nincs benne LLM-ítélet, ezért **ne grepelj kézzel**, futtasd a scriptet (a telepítő ugyanabba a platform-scripts mappába másolja, mint a `ds22-gate-check.py`-t):

> **Python-parancs (platformfüggő):** a példákban `python3` szerepel (Linux/macOS). **Windowson** a `python3` gyakran nem létezik — vagy a Microsoft Store stubja, ami megnyitja a Store-t —, ezért ott `python` vagy `py -3` a helyes hívás. Ha a `python3` „command not found" / „not recognized" hibát ad, **próbáld újra `python`-nal, majd `py -3`-mal**, ugyanazokkal a paraméterekkel. Ez nem a szkript hibája, és nem kell miatta megállni.

```bash
python3 <platform-scripts-mappa>/tc8-gate-check.py specs/test-conventions.md \
  --project-root . \
  --marker cycle-NN
```

- **`--marker`**: az aktuális ciklus — ehhez képest számol staleness-t az `Utolsó futás` markereken. Elhagyható; akkor csak a marker **létét** ellenőrzi, az elavulást nem.
- **`--stale-after N`**: ennyi vagy több ciklus eltérésnél elavult a tétel (default: **3**, a TC4 szabály szerint).

**A kilenc check:**

| # | Mit ellenőriz | Blokkol? |
|---|---|---|
| 1 | **Útvonal-létezés (TC8/1)** — a fájlban megnevezett repo-belső útvonalak (tesztfájl, script, compose fájl, komponens-mappa) léteznek-e | **FAIL**, ha a szülő-mappa létezik, de a cél nem (biztos jel: elavult tétel). Ha az útvonal repo-belsőként nem oldható fel (külső hivatkozás, image-ref, endpoint), csak **WARN** |
| 2 | **Lógó hivatkozás (TC8/2)** — a 2./3. szekció minden tétele létező 1. szekciós receptre (`R-ID`) hivatkozik-e, és van-e egyáltalán hivatkozása | **FAIL**. A nem hivatkozott recept **WARN** |
| 3 | **Titok-check (TC8/3)** — bekerült-e TC5 szerint tiltott credential | **FAIL** biztos mintánál (PAT/kulcs-prefix, privát kulcs blokk, `oc login --password`, `docker login -p`); platform-szó + credential-szó egy sorban csak **WARN** |
| 4 | **`Utolsó futás` marker (TC4)** — minden recept és 2./3. szekciós tétel kap-e markert, és melyik avult el | Hiányzó marker: **FAIL**. Elavult (`--stale-after`): **WARN** → kérdés a `doc-sync-questions.md`-be |
| 5 | **Kötelező riport-sor (TC9/TR3)** — a 2. és 3. szekció elején ott van-e a `**Kötelező riport (TR3):**` sor | **FAIL**, ha hiányzik valamelyik szekcióból. **WARN**, ha a sor tartalmaz generáló parancsot (az a `conventions.md` dolga — duplikáció) |
| 6 | **Futtatható koordináták (TC11)** — minden receptnek van-e `Indítás` mezője; a végpontot érintőknek `Példa hívás` blokkja; a 3. szekció környezeti előfeltételei hivatkoznak-e receptre | **FAIL** mindháromra — recept indítás/példa hívás nélkül nem futtatható, lógó előfeltétel mellett nem reprodukálható a teszt |
| 7a | **Tétel-részletezés (TC10/b)** — minden 2./3. szekciós táblázat-tételhez tartozik-e `### <ID>` részletező blokk, benne `Cél` / `Lépések` / `Elvárt eredmény` | **FAIL** — a táblázatsor index, nem teszteset; blokk nélkül a tétel nem reprodukálható. Táblázatsor nélküli árva blokk: **WARN** |
| 7 | **Önhordó tételek (TC10)** — a 2./3. szekció „Mit ellenőriz" cellája nem kezdődhet spec-szekció sorszámmal (`1.2.`) és nem hivatkozhat ciklusra (`Cycle 19 …`) | **FAIL** — a más dokumentumra mutató leírás önmagában értelmezhetetlen |

**Kilépő kód:** `0` = minden kemény check PASS (WARN megengedett), `1` = legalább egy FAIL, `2` = használati hiba. **Ha a fájl nem létezik, a script `0`-val, „kihagyva" jelzéssel tér vissza** — TC6 szerint a hiánya korai ciklusban nem hiba.

**A WARN-okat nem hagyhatod figyelmen kívül**, csak nem blokkolnak: mindegyikre vagy javítás, vagy `doc-sync-questions.md` kérdés a válasz. Bukáskor (`1`) ugyanaz az **ember-vezérelt** javító hurok fut, mint a DS22-nél: a konkrét eltérés `Knn`-ként a `doc-sync-questions.md`-be, javítás, majd a kapu újrafut, amíg zöld nem lesz.

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

### `specs/test-conventions.md` (TC2)

**Váz** — egy kötelező **`## 0. Koordináták`** blokk a fájl elején (TC13), utána pontosan három **számozott** szekció (a 2./3. az 1.-re hivatkozik), végül egy opcionális, **nem számozott** `## Nem promótált jelöltek (döntés-napló)` appendix (TC12):
````md
> **Utolsó felülvizsgálat:** cycle-NN · **Gazda:** 08-doc-sync · **Nem futtatható forrás** — a receptet a 02/03 fázis emeli be a ciklus spec.md/plan.md-jébe (TC1/a).

# Teszt konvenciók — visszatérő elvárások és receptek

## 0. Koordináták

_Minden környezet-, hozzáférés- és paraméter-adat **egy helyen** (TC13). Az 1. szekció receptjei ezekre hivatkoznak, nem ismétlik meg őket._

### Környezetek és végpontok

| Környezet | Komponens | URL / port | Health endpoint |
|---|---|---|---|
| lokális | <komponens> | `http://localhost:PORT` | `/health` |
| dev | <komponens> | `https://<host>` | `/health/ready` |

### Teszt-userek, kliensek, titkok

| Környezet | Név / azonosító | Titok | Scope / szerep |
|---|---|---|---|
| lokális | `<user>` | `<dev-only jelszó>` | `<realm / szerep>` |
| dev | `<client-id>` | pointer: `.env.dev` → `<VÁLTOZÓ>` | `<scope>` |

### Paraméterek és env-fájlok

| Név | Érték / pointer | Hol használjuk |
|---|---|---|
| `<PARAMÉTER>` | `<érték vagy pointer>` | `<recept vagy komponens>` |

## 1. Recept-regiszter

### R01 — <komponens / lépés neve>
- **Hol van:** <repo-útvonal, image-név, registry-cél, namespace/pod>
- **Elérés:** <URL-ek, portok, health endpoint>
- **Teszt-userek / paraméterek:** <user + jelszó (csak dev-hatókörű, TC5!), scope, client-id>
- **Indítás:** _(kötelező — TC11)_
  ```bash
  <a környezet felhúzása: docker compose up / podman run / npm run dev / oc port-forward …>
  <health-ellenőrzés: curl -s http://localhost:PORT/health → mit vársz vissza>
  ```
- **Parancsok:**
  ```bash
  <a teszt futtatása / build / push / restart — csak verifikált, tényleg lefutott parancs (TC3)>
  ```
- **Példa hívás:** _(kötelező, ha a recept HTTP/gRPC/CLI végpontot érint — TC11)_
  ```bash
  curl -s -X POST "<teljes URL>" \
    -H 'Content-Type: application/json' -H 'Authorization: Bearer <hogyan szerzem meg>' \
    -d '{"<mező>": "<érték>"}'
  # Várt válasz: 200, body: {"<mező>": "<érték>"}
  ```
- **Leállítás / takarítás:** <hogyan állítom le a felhúzott környezetet, mit kell törölni>
- **Előfeltétel / sorrend:** <mi kell hozzá — másik receptre `R-ID`-vel hivatkozva, mi jön előtte/utána>
- **Hatókör:** `lokális` | `osztott-remote` — <ha osztott, a beemelésnél a 03 kötelezően rákérdez>
- **Utolsó futás:** cycle-NN

## 2. Minden körben szükséges lokális (mock alapú) tesztek

**Kötelező riport (TR3):** `<artefaktum a validálási kör mappájában>` — forrás: `conventions.md → ## Teszt-riportolás`

| ID | Mit ellenőriz | Recept | Utolsó futás |
|---|---|---|---|
| L01 | <önhordó viselkedés-leírás: milyen bemenetre mi a helyes kimenet — TC10> | R01 | cycle-NN |

### L01 — <a tétel önhordó címe>

- **Cél:** <mit bizonyít ez a teszt — 1 mondat>
- **Előfeltétel:** <`R-ID` fut · a 0. blokk melyik adatai kellenek>
- **Lépések:**
  1. <konkrét lépés — hívás/parancs/interakció>
  2. <...>
- **Elvárt eredmény:** <státuszkód, mező, érték — amit igen/nem el lehet dönteni>

## 3. Minden körben szükséges integrációs / E2E tesztek

**Kötelező riport (TR3):** `<artefaktum a validálási kör mappájában>` — forrás: `conventions.md → ## Teszt-riportolás`

| ID | Mit ellenőriz | Recept | Előfeltétel | Utolsó futás |
|---|---|---|---|---|
| I01 | <önhordó viselkedés-leírás — TC10> | R01, R02 | <`R05` fut (a felhúzás ott van leírva) — TC11> | cycle-NN |

### I01 — <a tétel önhordó címe>

- **Cél:** <mit bizonyít ez a teszt — 1 mondat>
- **Előfeltétel:** <`R05` fut · a 0. blokk melyik adatai kellenek>
- **Lépések:**
  1. <konkrét lépés — hívás/parancs/interakció>
  2. <...>
- **Elvárt eredmény:** <státuszkód, mező, érték — amit igen/nem el lehet dönteni>

## Nem promótált jelöltek (döntés-napló)

_(Opcionális appendix, TC12 — nem számozott szekció. Ide kerül, amit a felhasználó nem kért projekt szintre; a következő ciklus ezeket már nem kínálja fel újra.)_

- <önhordó viselkedés-leírás> — döntés: `nem promótálandó` (<indok>) · cycle-NN
````

> **Minden táblázatsorhoz tartozik egy `### <ID>` részletező blokk** (TC10/b) — a táblázat az index, a blokk a teszteset. A TC8 kapu ellenőrzi, hogy egyik tételnek sincs hiányzó blokkja, és hogy a blokkban ott a Cél / Lépések / Elvárt eredmény.

> A **Kötelező riport (TR3)** sor mindkét szekcióban kötelező (a TC8 kapu ellenőrzi). **Csak az artefaktum nevét és a forrás-hivatkozást tartalmazza — a generáló parancsot NEM** (az a `conventions.md` dolga, TC1: nem duplikálunk). Ha a projekt tudatosan nem generál riportot, a sor értéke `nincs — a conventions.md szerint a riport-generálás nem kötelező`.

**Kész mini-példa (1. szekció egy tétele):**
````md
### R03 — Keycloak dev image build + deploy
- **Hol van:** `infra/keycloak/` · image: `nexus.example.local/dev/keycloak:latest` · namespace: `dev-auth`, pod: `keycloak-0`
- **Elérés:** `https://keycloak-dev.example.local` · health: `/health/ready`
- **Teszt-userek / paraméterek:** `test-user` / `Test123!` (scope: `profile openid`), realm-admin: `admin` / `admin` (dev realm), client-id: `demo-app`
- **Parancsok:**
  ```bash
  podman build -t nexus.example.local/dev/keycloak:latest infra/keycloak/
  podman push nexus.example.local/dev/keycloak:latest
  oc -n dev-auth rollout restart statefulset/keycloak && oc -n dev-auth rollout status statefulset/keycloak
  ```
- **Példa hívás:**
  ```bash
  curl -s -X POST "https://keycloak-dev.example.local/realms/demo/protocol/openid-connect/token" \
    -d "grant_type=password&client_id=demo-app&username=test-user&password=Test123!"
  ```
- **Előfeltétel / sorrend:** `oc login` megtörtént (a credential nem itt van — TC5 pointer: a csapat vault-jában); a restart után a health `ready`-t ad, csak utána futhat bármely I-tétel
- **Hatókör:** `osztott-remote` — a dev klasztert más is használja
- **Utolsó futás:** cycle-29
````

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

A kapu zöldre futása után — **és csak akkor, ha a TC12 promóciós ajánlatra megjött a válasz** (nyitott `[ ]` promóciós kérdéssel a fázis nem zárható le):

1. **Commit** — a `docs-generated/` + a komponens README-k + a ciklus munkafájljai:
   ```bash
   git add docs-generated/ <érintett README-k> specs/test-conventions.md specs/cycle-NN-<cycle-name>/doc-sync-plan.md specs/cycle-NN-<cycle-name>/doc-sync-questions.md
   git commit -m "cycle-NN: 08-doc-sync"
   ```
   _(A `specs/test-conventions.md`-t csak akkor add hozzá, ha létezik — korai ciklusban, promótálható tétel nélkül nem jön létre, TC6.)_
   _(Bootstrapnél a `docs-generated/` + az áthelyezett fájlok + a hivatkozás-átírások; a gyökér `temp/` munkafájlok sorsát a 8. munkaterv dönti el.)_

2. **Jelezd a felhasználónak a következő lépést:**
   > *"A dokumentáció szinkronban van a megvalósult rendszerrel, a konzisztencia-kapu zöld. Folytathatjuk a 9. lépéssel: review & merge (09). Az új fázis megkezdése előtt mindenképpen futtass egy `/clear` parancsot a kontextus kiürítéséhez, majd használd ezt a parancsot:*
   > ```
   > /bs-review-and-merge input: @specs/cycle-NN-<cycle-name>
   > ```"*
   > **A válasz végén helyezd el a `docs-generated/system-overview.md` (és a `doc-sync-plan.md`) közvetlen, kattintható linkjét.**
> **Fázishatár — kemény megállás (PE1).** A fázis a záró üzenettel (commit-azonosító + `/clear` + a következő fázis parancsa) **véget ér**. Ugyanabban a körben a következő fázisból **semmit nem kezdesz el** — a következő fázis artefaktumát létre sem hozod. Ez akkor is érvényes, ha egy **kontextus-összefoglaló / checkpoint** teendő-listája, a saját korábbi terved vagy a felhasználó egy korábbi körben adott „menjünk végig a folyamaton" mondata továbbmenetelre biztat: a skill fázishatára minden ilyen felett áll. Csak a felhasználó **erre a körre szóló, explicit** kérése írja felül. Ha mégis belekezdtél, **töröld a keletkezett fájlt**, állítsd vissza a tiszta munkafát, és jelezd.