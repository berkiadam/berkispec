# Berkispec Spec Tisztázási Kör és Plan Gate Implementációs Terv

## Cél

Ez a terv a `berkispec` `spec` fázisának tisztázásközpontú működését és a `plan` fázis kötelező továbbengedési (`READY_FOR_PLAN`) gate-jét írja le.

Ebben a körben nincs kódimplementáció, csak a következő fejlesztési kör pontos előkészítése.

## Érintett fájlok

Közvetlenül módosítandó implementációs körben:

* `src/index.mjs`
* `prompts/HU/01-write-spec.md`
* `prompts/EN/01-write-spec.md`
* `prompts/HU/01-modify-spec.md`
* `prompts/EN/01-modify-spec.md`

Már frissített dokumentáció:

* `specification.md`
* `plans/01-plan.md`

## specification.md-ben átvezetett új követelmények

Bevezetett szabálycsoportok:

* interaktív spec tisztázási ciklus `/done` és `/finish` vezérléssel
* `DRAFT` és `READY_FOR_PLAN` státusz-szemantika
* `[NEEDS CLARIFICATION Qxxx: ...]` inline marker kötelező használata
* `Nyitott kérdések` szekció kötelező vezetése
* `Tisztázott döntések` szekció javasolt struktúrája
* `plan` fázis előtti kötelező readiness gate
* `/finish` utáni figyelmeztetés, ha a spec még `DRAFT`

## Promptmódosítási terv

### 1) `01-write-spec.md` (HU + EN)

Mindkét nyelvi változatban explicit utasítások kerülnek be:

* minden szükséges információ meglétének ellenőrzése
* `.berkispec/project-desc.md` kötelező figyelembevétele
* `Reference Files` és user cél közti konzisztencia ellenőrzése
* inkonzisztencia vagy több értelmezés esetén kötelező visszakérdezés
* hiányzó lényeges információ esetén kötelező visszakérdezés
* nyitott kérdés esetén:
  * inline `[NEEDS CLARIFICATION Qxxx: ...]` marker beszúrása
  * kérdés felvétele `Nyitott kérdések` szekcióba
  * státusz marad `DRAFT`
* `READY_FOR_PLAN` csak akkor, ha nincs nyitott kérdés és nincs bizonytalanság

### 2) `01-modify-spec.md` (HU + EN)

Mindkét nyelvi változatban explicit utasítások kerülnek be:

* kapcsolódó `Qxxx` kérdés(ek) azonosítása user válasz alapján
* user válasz beépítése a megfelelő spec részbe
* kapcsolódó inline marker feloldása vagy eltávolítása
* `Nyitott kérdések` állapot frissítése (lezárás / áthelyezés)
* döntés rögzítése `Tisztázott döntések` szekcióban
* új bizonytalanság esetén új `Qxxx` létrehozása
* `READY_FOR_PLAN` csak akkor, ha:
  * nincs OPEN kérdés
  * nincs kipipálatlan kérdés
  * nincs `[NEEDS CLARIFICATION ...]` marker

### 3) Init promptmásolás

Az `init` promptmásolási listában kötelezően szerepel:

* `.berkispec/prompts/01-modify-spec.md`

## `index.mjs` implementációs terv

## Új vagy bővített helper függvények

Tervezett helper-ek:

* `getCodexConfig()` és default értékkezelés
* `ensureCodexAvailable(command)`
* `loadPromptTemplate(promptName)`
* `buildWriteSpecPrompt(context)`
* `buildModifySpecPrompt(context)`
* `runCodex(prompt, options)` (`spawn`, streamelés, bufferelés, exit code check)
* `parseSpecStatus(specContent)`
* `hasNeedsClarificationMarkers(specContent)`
* `parseOpenQuestions(specContent)`
* `validateSpecReadyForPlan(specContent)`
* `warnIfSpecDraftOnFinish(specPath)`

## `runCodex(prompt, options)` működés

Követelmények:

* `child_process.spawn`
* alap parancs: `codex exec <prompt>`
* futtatás: `cwd = process.cwd()`
* `stdout`/`stderr` élő stream a képernyőre
* teljes `stdout`/`stderr` tartalom összegyűjtése
* nem `0` exit code esetén hiba
* prompt mentése `.berkispec/latest-prompt.md`-be futtatás előtt

## Spec fázis új flow implementációja

### Első kör

1. inicializáltság és projektkontextus validálása
2. ciklusnév + többsoros célleírás bekérése (`/done`)
3. új cycle mappa létrehozása
4. `01-write-spec.md` alapú prompt összeállítása
5. Codex futtatása
6. `spec.md` létrejöttének ellenőrzése

### Interaktív tisztázási kör

1. user inputblokk fogadása
2. `/done` esetén `01-modify-spec.md` alapú új prompt + Codex kör
3. `/finish` esetén spec loop lezárása
4. `/finish` után azonnali státuszellenőrzés:
   * ha `DRAFT`, figyelmeztetés: a plan fázis blokkolt lesz

## Plan gate validáció

### Ellenőrizendő feltételek

A `plan` csak akkor indulhat, ha mind igaz:

* van egyértelmű `READY_FOR_PLAN` státusz (`Status:` vagy `Állapot:` kulccsal)
* nincs `DRAFT` státusz
* nincs `[NEEDS CLARIFICATION ...]` marker
* a `Nyitott kérdések` szekcióban nincs OPEN vagy kipipálatlan kérdés

### Minimális parser/validátor logika

1. `spec.md` tartalom beolvasása
2. státusz sorok keresése:
   * `Status: READY_FOR_PLAN`
   * `Állapot: READY_FOR_PLAN`
3. tiltó állapotok keresése (`DRAFT`)
4. regex keresés inline markerre: `\[NEEDS CLARIFICATION Q\d{3}:`
5. `Nyitott kérdések` blokkban OPEN és `[ ]` minták keresése
6. sikertelen ellenőrzés esetén validációs hiba és leállás

### Hibaüzenet irányelv

Specifikált hibaüzenet:

```text
A spec még DRAFT állapotban van, ezért nem indítható a plan fázis.
Előbb fejezd be a spec tisztázását a `berkispec spec` fázisban, majd csak akkor lépj tovább, ha a spec státusza READY_FOR_PLAN.
```

## `/done` és `/finish` kezelési terv

* `/done`: aktuális inputblokk lezárása + Codex hívás
* `/finish`: interaktív spec ciklus lezárása
* `/finish` nem jelent kész specifikációt
* `DRAFT` esetén lezáráskor figyelmeztetni kell a usert a plan-blokkolásra

## Hibakezelés

Kezelendő esetek:

* hiányzó vagy üres `.berkispec/project-desc.md`
* hiányzó `01-write-spec.md` vagy `01-modify-spec.md` prompt
* nem elérhető `codex` parancs
* sikertelen Codex futás (nem `0` exit code)
* hiányzó `spec.md` a futás után
* érvénytelen vagy hiányzó státusz a `plan` előtt
* nyitott kérdések vagy inline markerek maradása `plan` indítás előtt

## Kézi tesztelési lépések

1. Spec generálás nyitott kérdéssel
   Elvárt: `DRAFT` státusz + inline `NEEDS CLARIFICATION` marker + `Nyitott kérdések` bejegyzés.
2. Plan indítás blokkolása `DRAFT` spec esetén
   Elvárt: validációs hiba és leállás.
3. User válasz beépítése `01-modify-spec.md` alapján
   Elvárt: kapcsolódó `Qxxx` frissül, marker feloldódik vagy törlődik, döntés rögzül.
4. `READY_FOR_PLAN` státusz elérése
   Elvárt: nincs OPEN kérdés, nincs inline marker, státusz `READY_FOR_PLAN`.
5. Plan fázis engedélyezése `READY_FOR_PLAN` spec esetén
   Elvárt: `berkispec plan <cycle>` validáció átmegy és a plan prompt elkészül/fut.

## Kockázatok és nyitott döntések

* A `Nyitott kérdések` szekció formátuma félig strukturált Markdown; parser oldalon egy robustus, de egyszerű heurisztikára van szükség.
* Többnyelvű státuszkulcs (`Status` / `Állapot`) támogatása kötelező, további lokalizáció nem cél.
* Dönteni kell, hogy lezárt kérdések a `Nyitott kérdések` szekcióban maradjanak kipipálva, vagy minden lezárt elem átkerüljön a `Tisztázott döntések` szekcióba.
* A promptoknak elég erősnek kell lenniük ahhoz, hogy az agent ne “találjon ki” hiányzó döntéseket, hanem következetesen visszakérdezzen.
