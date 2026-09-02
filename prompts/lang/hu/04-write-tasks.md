<!--
  A `04-write-tasks` PROJEKT-NYELVI blokkjai (9.4 kiemelés).
  Ezt a fájlt a telepítő build-time emeli be az INCLUDE markerek helyére, a
  választott PROJEKT-nyelv (`PROJECT_LANG`) szerint; a marker alakja
  `lang/04-write-tasks.md#<horgony>`.
  A blokkok SZÓ SZERINT kerültek ide — ne fogalmazd át, ne egységesítsd.
  Az ANCHOR sorok NEM részei a beemelt szövegnek, csak határolók (8.9).
  FIGYELEM: ebbe a vezető jegyzetbe ne kerüljön komment-lezáró szekvencia.
-->

<!-- ANCHOR:task-formatum -->
- [ ] T001 [RED]   <tesztfájl létrehozása / teszt megírása> — `path/to/test.ts` — plan [P-CONFIG] — test [TC-01, TC-02]
- [ ] T002 [GREEN] <implementáció> — `path/to/file.ts` — plan [P-CONFIG] (betöltő modul)
- [ ] T003 [OPS]   <nem TDD lépés: build / push / deploy / kézi konfiguráció> — parancs vagy `path/to/file` — plan [P-DEPLOY]
- [ ] T004 [CHECK] Futtasd: `npx tsx --test path/to/test.ts -t "<TC-01 teszt-függvény neve>"` — plan [P-CONFIG] — test [TC-01]
- [ ] T005 [CHECK] Futtasd: `npx tsx --test path/to/test.ts -t "<TC-02 teszt-függvény neve>"` — plan [P-CONFIG] — test [TC-02]
- [ ] T006 [CHECK] Futtasd: `npm run typecheck` — plan [P-CONFIG]

<!-- ANCHOR:tasks-struktura -->
# Cycle NN: <cím> — Tasks

**Státusz:** `Piszkozat` | `Implementálásra kész`

## Prerequisite dokumentumok

_Az implementáló agent ezeket olvassa be a végrehajtás előtt._

- `specs/<cycle-name>/plan.md`
- _(további Reviewed artifaktok a plan Schema Artifaktumok táblájából)_

> `[RED]` = teszt írása (bukni fog) · `[GREEN]` = implementáció (teszt zöldítése) · `[CHECK]` = ellenőrzés futtatása · `[OPS]` = nem-TDD lépés (build, deploy, kézi konfiguráció, jóváhagyás, rollback)

## <Logikai csoport 1 — a plan végrehajtási sorrendje alapján> — plan [P-CONFIG], [P-REDIS]

- [ ] T001 [RED]   ... — plan [P-CONFIG] (unit teszt) — test [TC-01, TC-02]
- [ ] T002 [GREEN] ... — plan [P-CONFIG] (betöltő modul)
- [ ] T003 [CHECK] Futtasd: `npm test -- path/to/test.ts -t "<TC-01 neve>"` — plan [P-CONFIG] — test [TC-01]
- [ ] T004 [CHECK] Futtasd: `npm test -- path/to/test.ts -t "<TC-02 neve>"` — plan [P-CONFIG] — test [TC-02]

## <Logikai csoport 2> — plan [P-ROUTING]

- [ ] T005 [RED] ... — plan [P-ROUTING] — test [TS-01]
- [ ] T006 [CHECK] Futtasd: `pytest test/integration/cycle_NN_test.py -k ts01` — plan [P-ROUTING] — test [TS-01]
- [ ] T007 [CHECK] Futtasd: `npm run typecheck` — plan [P-ROUTING]

## Plan-lefedettség (fordított tábla)

_Minden `[P-…]` ID-t viselő plan-szekció szerepel itt, a hozzá tartozó taskokkal._

| Plan szekció (ID + cím) | Taskok | Csoport |
|---|---|---|
| `[P-CONFIG]` Konfigurációs rendszer | T001, T002, T003, T004 | 1 |
| `[P-ROUTING]` Dinamikus routing | T005, T006, T007 | 2 |
| `[P-DOCS-ONLY]` … | — (nincs task: <indok>) | — |

## Teszt-lefedettség

_A plan minden `TS-NN` forgatókönyve és a gépi futtatási tábla minden kategóriája szerepel itt._

| Plan-teszt (`TS-NN` / `TC-NN` / kategória) | Létrehozó task | Futtató task | Megjegyzés |
|---|---|---|---|
| `TC-01` keyNamespace default | T001 | T003 | unit |
| `TC-02` hiányzó `expiresAt` → hiba | T001 | T004 | unit |
| `TS-01` Hideg indítású konkurencia | T005 | T006 | pytest, `implement` + `validate` |
| unit (gépi tábla) | — | T003, T004 | a 07 a táblából is futtatja |
| e2e (gépi tábla) | T005 | — | `validate`-fázisú: a 07 futtatja a táblából |
| `TS-07` Kézi SPI-ellenőrzés | — | — | nem automatizálható: kézi `[OPS]` lépés a T018-ban |

<!-- ANCHOR:desztruktiv-csoport-sablon -->
## Destruktív / osztott környezetet érintő taskok — jóváhagyás és rollback

Ha a plan **közös (nem eldobható) környezetet** módosító lépést tervez — deployment/pod csere osztott klaszterben, image push közös registrybe, seed vagy törlés osztott adatbázisban, konfiguráció felülírása —, azt **három tasknak kell közrefognia** a saját logikai csoportjában:

```md
- [ ] T0nn [OPS]   Kérj JÓVÁHAGYÁST a felhasználótól a <művelet> futtatására — érintett: <környezet/namespace/registry>; a művelet más fejlesztők munkáját is érintheti. Rögzítsd az eredeti állapotot FÁJLBA: `<állapot-kiolvasó parancs> > .rollback-state`
- [ ] T0nn [OPS]   <a tényleges destruktív művelet> — `<konkrét parancs; a korábbi lépés állapotát a fájlból olvasva>`
- [ ] T0nn [CHECK] Ellenőrizd a művelet sikerét — `<ellenőrző parancs + elvárt kimenet>`
- [ ] T0nn [OPS]   ROLLBACK (csak ha az előző `[CHECK]` elbukott): állítsd vissza az eredeti állapotot — `<visszaállító parancs, a .rollback-state-ből olvasva>`
```

> **🔴 Állapot-perzisztencia — a leggyakoribb csendes hiba.** Minden task **külön shellben** fut, ezért a `VAR=...` vagy `export VAR=...` a **következő taskra elpárolog**. Ha a rollback vagy a deploy egy korábbi taskban előállított értékre (mentett eredeti azonosító, generált egyedi tag) hivatkozik, az **üres paraméterrel futna** — vagyis a rollback papíron megvan, a gyakorlatban nem működik. Ezért az ilyen állapot **fájlba kerül**, és a későbbi taskok onnan olvassák; vagy a függő parancsokat **egy taskba** vonod.

Az állapot-fájlra két további szabály:
- **Hova kerüljön:** a ciklus mappájába (`specs/cycle-NN-<cycle-name>/.rollback-state`), **ne a repo gyökerébe**. Ha mégis a gyökérbe kerül, vedd fel egy taskot, ami a `.gitignore`-ba is beírja — különben egy megszakadt futás után a munkafában marad, és bekerülhet egy commitba.
- **Takarítás kötelező:** a csoport utolsó taskja (vagy a sikeres `[CHECK]`) törölje (`rm -f`). Megszakadt futás után egy régi állapot-fájl **rosszabb, mint a semmi**: egy elavult azonosítóra állítana vissza.

- A **jóváhagyó task az első** — a destruktív művelet nem futhat le anélkül, hogy a felhasználó rábólintott volna.
- A jóváhagyó task **rögzíti az eredeti állapotot** (a kiolvasó paranccsal együtt) — enélkül a rollback nem végrehajtható.
- A **rollback task a csoport végén** áll, feltételesen. Ha a plan nem ad rollback-forgatókönyvet, az **plan-hiányosság**: vedd fel kérdésként a `tasks-questions.md`-be, ne találd ki magad.
- **Ha a művelet felülír egy meglévő azonosítót** (pl. ugyanarra az image-tagre pushol), jelezd: ilyenkor **nincs mihez visszaállni**, tehát vagy verziót kell léptetni, vagy a rollback nem valós — ez a plan felülvizsgálatát igényli.

## Regressziós tesztek felülvizsgálata

- [ ] TREG1 Ellenőrizd / frissítsd: `test/unit/foo.test.ts` — érintett, mert [indok a plan-ből]
- [ ] TREG2 Ellenőrizd / frissítsd: `test/integration/cycle-XX-foo.sh` — érintett, mert [indok a plan-ből]

<!-- ANCHOR:dokumentacio-csoport-sablon -->
## Dokumentáció

- [ ] TLAST1 ...a plan által explicit kért, NEM docs-generated/ alá tartozó dokumentáció-frissítés...

<!-- ANCHOR:statusz-megerosites -->
*"A task lista minőségellenőrzése átment. Készen áll a tasks lista implementálásra? Ha megerősíted, átállítom `Implementálásra kész` státuszra."*

<!-- ANCHOR:zaro-uzenet -->
> *"A task lista kész. Folytathatjuk az 5. lépéssel (analyze — kereszt-fázisos konzisztencia ellenőrzés). Az új fázis megkezdése előtt mindenképpen futtass egy `/clear` parancsot a kontextus kiürítéséhez, majd használd ezt a parancsot:
> ```
> /bs-analyze input: @specs/cycle-NN-<cycle-name>
> ```"*
