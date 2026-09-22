# Quick start

← [Vissza a főoldalra](../../README-HU.md) · [Oldalindex](README.md)

A BerkiSpec egy fegyelmezett, spec-driven development (SDD) keretrendszer AI-ágensekkel való páros programozáshoz.

## A keretrendszer működési elve:
* **Ciklusok (Cycles):** A fejlesztést jól körülhatárolt, egyértelmű céllal leírható, könnyen kézben tartható egységekre (ciklusokra) osztjuk. Minden új ciklus saját Git branch-et kap, és a ciklus összes tervezési és naplózási dokumentuma a projekt gyökerében lévő `specs/cycle-NN-<cycle-name>/` mappába kerül.
* **Fázisok (Phases):** Minden ciklus szigorú fázisokra van bontva, amelyek végigvezetik a folyamatot a követelményektől a megvalósításig és a merge-ig.

## Két fejlesztési út:
A feladat összetettségétől függően kétféle flow áll rendelkezésre:
1. **Teljes SDD Flow:** Részletes specifikációt (`spec.md`), technikai tervet (`plan.md`) és feladatlistát (`tasks.md`) készít, valamint automatikus önjavító minőségi hurkokat (analyze, validate, review) futtat.
2. **Könnyű (Lightweight) Flow:** Kisebb módosításokhoz, konfigurációkhoz vagy egyszerű scriptekhez. Egy lépésben fut le, nincs külön fázisbontása.

## Alapvető parancsok (Slash Commands):
A telepítés után a platform chat felületén a `/` karakter leütésével érheted el a skilleket:

* **`/bs-init-project`**: A projekt legelső inicializálása (létrehozza a `conventions.md` fájlt).
* **`/bs-add-cycles`**: Új fejlesztési ciklus hozzáadása az ütemtervhez (`roadmap.md`).
* **`/bs-write-spec`**: Követelmények rögzítése, új ciklus specifikációjának elkészítése (`spec.md` + `spec-questions.md`).
* **`/bs-write-code-plan`**: A technikai megvalósítási terv **kód-oldala** (`plan.md` kód-szekciói + `plan-questions.md`) — koordináták, tervezett módosítások, konfiguráció, séma.
* **`/bs-write-test-plan`**: Ugyanannak a `plan.md`-nek a **teszt-fele** — `TS-NN` forgatókönyvek, gépi futtatási tábla, környezet-felkészítés, tesztfájl-adatlapok.
* **`/bs-write-tasks`**: A technikai terv lebontása mérhető feladatokra (`tasks.md` + `tasks-questions.md`).
* **`/bs-analyze`**: Kereszt-fázisos konzisztencia-ellenőrzés és automatikus javítás (spec/plan/tasks egyezés).
* **`/bs-implement`**: Tényleges kódfejlesztés a feladatlista alapján, a haladás rögzítésével a `tasks.md`-ben.
* **`/bs-validate`**: Tesztek, lint, build **és kódreview** (reviewer agent) ellenőrzése egyetlen automatikus javító hurokban (sikeres futtatás után 'Kész' státusz).
* **`/bs-doc-sync`**: Az élő dokumentáció (`docs-generated/`) és README-k szinkronizálása a kódváltozásokkal, valamint a `specs/test-conventions.md` (visszatérő teszt-elvárások és receptek) karbantartása.
* **`/bs-review-and-merge`**: A ciklus lezárása **egy lépésben**, ha nincs PR feladás (`PR submission: no`): a fő branch behozása a ciklus ágába → **post-merge teszt-kör** (`VP2`: tesztek + Sonar) → beolvasztás kötelező felhasználói megerősítéssel (RD8). A kódreview már a `/bs-validate`-ben lefutott.
* **`/bs-create-pr` → `/bs-review` → `/bs-merge`**: ugyanez **három lépésben**, ha van PR feladás (`PR submission: yes`) — a PR megnyitása, a PR-en futó (központosított SDD-ben **gépi**) review, végül a beolvasztás a `VP2` kör után. A `VP2` mindkét úton a fő branch-re juttatás **előtti** kapu.
* **`/bs-dev-test`** *(opcionális, csak központosított úton)*: a sikeres merge után telepít egy integrált teszt-környezetbe, és **valódi e2e teszteket** futtat rá (`VP3`). Ha be van kapcsolva, a ciklus ennek a körnek a zöldjével zárul.
* **`/bs-cycle-status`**: Ciklusok státuszának ellenőrzése (interaktív TUI vagy parancssori státusz).
* **`/bs-brainstorm`**: Feltáró ötletelés és közös tervezés **a spec előtt** — perzisztens munkafájllal (`.bs-brainstorm/`), olcsó `researcher` feltárással; a végén átad a `/bs-add-cycles`-nak vagy a `/bs-quick-flow`-nak.
* **`/bs-quick-flow`**: Az egyszerűsített (lightweight) flow elindítása kis feladatokhoz (spec → task → implementáció).
* **`/bs-export-doc`**: Verziózott PDF export a markdown doksikból (mermaid ábrákkal együtt) az `export/` mappába — paraméter nélkül az `architecture.md`-ből és a `system-overview.md`-ből.
* **`/bs-manual-test-plan`**: **Kézi tesztterv** összeállítása a ciklushoz (`manual-test-plan.md`): komponens-indítás, tesztadatok, kézi hívási szekvenciák (`curl` + `.http`), elvárt eredmények és az automata tesztek eredményének helye. Két mód: `Tervezett` (implementáció előtt, a `plan.md` alapján) vagy `As-built` (validálás után, a kódhoz ellenőrizve). Előfeltétele az `analyze-report.md` `PASS` státusza; nem fázis, nem változtat ciklus-státuszt, és bármikor újrafuttatható (a kézi kiegészítéseket megőrzi).
* **`/bs-run-tests`**: **Teszt-futtatás cikluson kívül**, kategóriánként (`unit`, `rest-e2e`, `ui` — a projekt szótára szerint). A `conventions.md` `## Teszt-futtatás` szekciójának projekt-szintű táblájából futtat, és a gitignore-olt `test-runs/<kategória>/<UTC-időbélyeg>/<env>/` fába ír, kategóriánkénti `latest.json` mutatóval. Nem fázis, és az eredménye **soha nem ciklus-bizonyíték** — lásd a 11.3 szakaszt.

---
