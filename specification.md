# berkispec specification

## Cél

A `berkispec` egy repo-lokális, kézi hajtású spec-driven workflow segédprogram.

Célja:

* a fejlesztési munkát jól elkülönített fázisokra bontani
* a projekt tartós kontextusát külön kezelni a feature/ciklus szintű specifikációktól
* a Codex számára konzisztens, újrahasználható promptokat előállítani
* a fejlesztőnek egyszerű, interaktív CLI-t adni
* a `spec` fázist interaktív, tisztázásközpontú Codex authoring ciklussá tenni

Az új működésben a `berkispec` a `spec` fázisban ténylegesen meghívja a Codex CLI-t, és az AI-val iteratív tisztázási körökben készül a `spec.md`.

## Felelősségmegosztás

### berkispec

A `berkispec` workflow-vezérlő.

Feladata:

* fázisok vezérlése
* lokális workspace és állományok előkészítése
* promptok összeállítása
* `spec` fázisban Codex CLI meghívása
* prompt mentése `.berkispec/latest-prompt.md` fájlba
* fázisok közti továbbengedési feltételek érvényesítése

### Codex CLI

A Codex CLI a tényleges agent.

Feladata:

* `spec.md` létrehozása
* meglévő `spec.md` módosítása
* tisztázandó kérdések azonosítása
* nyitott kérdések kezelése és döntések beépítése
* `DRAFT` és `READY_FOR_PLAN` státusz szabályos kezelése

### Auth és konfigurációs felelősség

Kötelező szabályok:

* a `berkispec` nem kezel OpenAI tokent, API kulcsot vagy authentikációt
* a Codex CLI login, auth, token, model és globális config kezelése a Codex CLI saját felelőssége
* az `init` fázisban nincs tokenmentés, API kulcs bekérés vagy Codex login kezelés
* a `berkispec` legfeljebb a `codex` parancs elérhetőségét ellenőrzi
* ha a `codex` parancs nem elérhető, a hibaüzenet:

```text
Codex CLI nem elérhető. Telepítsd és futtasd külön: codex login
```

### Régi működés leváltása

Kötelező döntések:

* a régi prompt-only működést nem kell megőrizni
* a `spec` fázis új célműködése tényleges Codex CLI hívás
* nem kell `--prompt-only`
* nem kell `--no-codex`

## Fő modell

A `berkispec` két külön réteget kezel:

### 1. Projekt szintű tartós kontextus

Tárolási hely:

```text
.berkispec/project-desc.md
```

Tartalma:

* projekt rövid szöveges leírása
* opcionális referenciafájl-lista

### 2. Ciklus / feature szintű specifikáció

Tárolási hely:

```text
specs/
  cycle-XX-cycle-name/
    spec.md
    plan.md
    tasks.md
```

Jelentés:

```text
spec.md  -> mit akarunk
plan.md  -> hogyan tervezzük megvalósítani
tasks.md -> milyen végrehajtási lépésekben csináljuk meg
```

## Fázisok

A `berkispec` főmenüjében választható fázisok:

1. `init`
2. `project`
3. `spec`
4. `plan`
5. `tasks`
6. `implement`
7. `validate`
8. `exit`

Az `exit` nem munkafázis, hanem az interaktív futás lezárása.

Interaktív módban a `berkispec` maradjon aktív addig, amíg a felhasználó az `exit` opciót nem választja.
Egy fázis lefutása után a CLI térjen vissza a főmenübe.

Kivétel:

* a `spec` fázis interaktív módban saját belső iteratív ciklust futtat
* a `spec` fázis csak `/finish` után tér vissza a főmenübe

Nem interaktív módban egy parancs továbbra is egyetlen fázist futtat, majd kilép.

## Config

A `.berkispec/config.json` opcionálisan tartalmazhat Codex beállítást:

```json
{
  "projectLanguage": "HU",
  "codex": {
    "enabled": true,
    "command": "codex",
    "mode": "exec",
    "sandbox": "workspace-write",
    "approval": "on-request"
  }
}
```

Ha nincs `codex` config, a default értékek:

* `enabled: true`
* `command: "codex"`
* `mode: "exec"`

## Fázisleírás

### init

Az `init` bootstrap fázis.

Feladata:

* létrehozni a `.berkispec/` könyvtárat
* kiválasztani és menteni a projekt nyelvét
* a kiválasztott nyelv promptjait bemásolni a projektlokális `.berkispec/prompts/` könyvtárba
* opcionálisan ellenőrizni a `codex` parancs elérhetőségét

Kötelező szabályok:

* projekt nyelv csak egyszer választható
* `init` nem kérhet API kulcsot
* `init` nem menthet tokent
* `init` nem kezelhet Codex login folyamatot

Elvárt promptmásolási eredmény:

```text
.berkispec/prompts/
  00-init.md
  01-project.md
  01-write-spec.md
  01-modify-spec.md
  02-write-plan.md
  03-write-tasks.md
  04-implement-tasks.md
  05-validate-cycle.md
```

### project

A `project` fázis kezeli a projekt tartós alapadatait (`.berkispec/project-desc.md`).

Kötelező szabály:

* az első `spec` fázis előtt a `project` fázist legalább egyszer le kell futtatni
* a `spec` fázis validálja, hogy van projektkontextus

### spec

A `spec` fázis új ciklust indít, majd interaktív tisztázási loopban készíti a specifikációt.

#### Kötelező validáció

* `.berkispec/project-desc.md` létezik
* `.berkispec/project-desc.md` tartalmaz projektkontextust
* `codex` parancs elérhető

Hibaüzenetek:

```text
Validációs hiba: a spec fázis előtt kötelező lefuttatni a `berkispec project` parancsot.
```

```text
Codex CLI nem elérhető. Telepítsd és futtasd külön: codex login
```

#### Első kör

Kötelező input:

```text
Ciklus neve:
<rövid név>

Cél:
<többsoros célleírás>
```

A `Cél` mező többsoros, lezárása `/done`.

Lépések:

1. Projektkontextus ellenőrzése.
2. Ciklusnév bekérése.
3. Célleírás bekérése többsoros inputként.
4. `/done` hatására első prompt összeállítása a `.berkispec/prompts/01-write-spec.md` alapján.
5. Prompt mentése `.berkispec/latest-prompt.md` fájlba.
6. Codex futtatása.
7. Codex létrehozza a `specs/cycle-XX-<slug>/spec.md` fájlt.

#### Interaktív módosító ciklus

Az első Codex kör után a `spec` fázis nem zárul le, hanem tisztázási ciklusban marad.

A user:

* válaszolhat a kérdésekre
* adhat további pontosítást
* `/done`-nal indíthat új Codex kört
* `/finish`-sel lezárhatja a spec interaktív ciklust

Parancsjelentések:

* `/done`: aktuális inputblokk lezárása és Codex hívás indítása
* `/finish`: spec interaktív ciklus lezárása

Fontos:

* a `/finish` nem jelenti automatikusan, hogy a spec kész
* `/finish` után is maradhat a spec státusza `DRAFT`
* ha a user `DRAFT` állapotban zárja le a ciklust, a `berkispec` jelezze, hogy a `plan` fázis blokkolva lesz

#### Spec tisztázási szabályok

A `01-write-spec.md` és `01-modify-spec.md` promptok kötelezően utasítsák az agentet az alábbiakra:

1. Vizsgálja meg, hogy rendelkezésre áll-e minden szükséges információ a spec megírásához vagy módosításához.
2. Olvassa el és vegye figyelembe a `.berkispec/project-desc.md` fájlt.
3. A `.berkispec/project-desc.md` `Reference Files` szekciójában felsorolt fájlokat vesse össze a user céllal és a spec tartalmával.
4. Inkonzisztencia esetén ne találjon ki megoldást, hanem kérdezzen vissza.
5. Lényeges hiányzó információ esetén kérdezzen vissza.
6. Több értelmezés esetén kérdezzen vissza.
7. Amíg nyitott kérdés van, a spec státusza maradjon `DRAFT`.
8. Csak akkor állítsa a státuszt `READY_FOR_PLAN` értékre, ha nincs több nyitott kérdés, és a spec alapján biztonságosan készíthető plan.

#### Nyitott kérdések kezelése a spec.md-ben

A tisztázandó kérdéseket két szinten kötelező kezelni.

Inline jelölés:

```text
[NEEDS CLARIFICATION Q001: rövid kérdés vagy bizonytalanság]
```

Összesített szekció:

```markdown
## Nyitott kérdések

- [ ] Q001: rövid kérdés
  - Kontextus: hol vagy milyen követelményhez kapcsolódik
  - Miért fontos: miért blokkolja vagy befolyásolja a specifikációt
  - Státusz: OPEN
  - User válasz: _még nincs_
  - Döntés: _még nincs_
```

Kötelező szabály:

* az inline marker és az összesített nyitott kérdés lista együtt kötelező
* azonosítók stabilak és monoton növekvők: `Q001`, `Q002`, `Q003`, ...

`01-write-spec.md` viselkedés:

* ha kérdés van, tegye be az inline `[NEEDS CLARIFICATION Qxxx: ...]` markert a releváns helyre
* vegye fel a kérdést a `Nyitott kérdések` szekcióba
* hagyja a spec státuszát `DRAFT` állapotban

`01-modify-spec.md` viselkedés user válasz után:

* keresse meg a kapcsolódó `Qxxx` kérdést
* építse be a választ a megfelelő spec részbe
* oldja fel vagy távolítsa el a kapcsolódó inline markert
* a `Nyitott kérdések` szekcióban jelölje lezártként, vagy mozgassa át
* rögzítse a döntést
* ha új kérdés keletkezik, hozzon létre új `Qxxx` azonosítót
* csak akkor állítsa `READY_FOR_PLAN` státuszra a specet, ha nincs több OPEN kérdés és nincs több inline marker

Javasolt lezárt döntés forma:

```markdown
## Tisztázott döntések

- Q001: eredeti kérdés röviden
  - User válasz: ...
  - Döntés: ...
  - Érintett spec rész: ...
```

### plan

A `plan` fázis a meglévő `spec.md` alapján technikai tervet készíttet.

Input:

```bash
./berkispec plan <cycle>
```

#### Plan státusz-gate

A `plan` fázis csak akkor indulhat, ha a cél cycle `spec.md` megfelel minden feltételnek:

* egyértelmű státuszmezőben szerepel a `READY_FOR_PLAN` érték
* elfogadható formák:
  * `Status: READY_FOR_PLAN`
  * `Állapot: READY_FOR_PLAN`
* nincs `DRAFT` állapot
* nincs `[NEEDS CLARIFICATION ...]` marker
* a `Nyitott kérdések` szekcióban nincs OPEN vagy kipipálatlan kérdés

Ha bármelyik feltétel sérül, a `plan` fázis validációs hibával álljon le.

Hibaüzenet minta:

```text
A spec még DRAFT állapotban van, ezért nem indítható a plan fázis.
Előbb fejezd be a spec tisztázását a `berkispec spec` fázisban, majd csak akkor lépj tovább, ha a spec státusza READY_FOR_PLAN.
```

Következmény:

* a `spec` fázis iteratív tisztázási ciklus marad, amíg nyitott kérdés van
* a `/finish` csak a spec interaktív ciklust zárja le
* a `plan` továbbengedés egyetlen jele a `READY_FOR_PLAN`

### tasks

Input:

```bash
./berkispec tasks <cycle>
```

### implement

Input:

```bash
./berkispec implement <cycle>
```

### validate

Input:

```bash
./berkispec validate <cycle>
```

## Prompt fájlok

Forrás könyvtár:

```text
tools/berkispec/prompts/
  HU/
  EN/
```

Spec tisztázási logikához kötelezően módosítandó:

* `tools/berkispec/prompts/HU/01-write-spec.md`
* `tools/berkispec/prompts/EN/01-write-spec.md`
* `tools/berkispec/prompts/HU/01-modify-spec.md`
* `tools/berkispec/prompts/EN/01-modify-spec.md`

Project-lokális másolat:

```text
.berkispec/prompts/
  00-init.md
  01-project.md
  01-write-spec.md
  01-modify-spec.md
  02-write-plan.md
  03-write-tasks.md
  04-implement-tasks.md
  05-validate-cycle.md
```

## Többsoros bevitel

`/done`:

* `project` leírás lezárása
* `spec` első célleírás lezárása
* `spec` módosító inputblokk lezárása és új Codex kör indítása

`/finish`:

* `spec` interaktív ciklus lezárása
* nem ad automatikus `READY_FOR_PLAN` státuszt

## `.berkispec` mappa szerepe

Várható tartalom:

```text
.berkispec/
  config.json
  latest-prompt.md
  project-desc.md
  prompts/
    00-init.md
    01-project.md
    01-write-spec.md
    01-modify-spec.md
    02-write-plan.md
    03-write-tasks.md
    04-implement-tasks.md
    05-validate-cycle.md
  history/
```

## Jelenlegi implementáció állapota

Meglévő CLI fájl:

```text
tools/berkispec/index.mjs
```

Az új tisztázási szabályok, a `Qxxx` markerkezelés, és a `plan` előtti `READY_FOR_PLAN` gate még nincs implementálva.

## Fontos döntések

* A `spec` fázis interaktív tisztázási loop.
* A `spec` csak akkor továbbengedhető `plan` fázisba, ha `READY_FOR_PLAN`.
* A `DRAFT` explicit blokkoló állapot.
* A `/finish` nem jelent automatikus készültséget.
* A `berkispec` nem old fel bizonytalanságot feltételezéssel; erre a promptok is kötelezik az agentet.
