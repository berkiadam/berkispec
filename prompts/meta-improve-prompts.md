# Meta-prompt — Prompt fejlesztés

Ez a fájl arra való, hogy egy új AI-sessziót indítsál, amelynek célja a `prompts/` mappa promptjainak felülvizsgálata vagy továbbfejlesztése.

**Használat:** Másold be az alábbi szaggatott vonaltól az AI-nak, és add meg a konkrét fejlesztési célt a végén.

---

Egy **spec-driven development workflow** promptrendszerét fejlesztjük. A `prompts/` mappa az AI-asszisztált szoftverfejlesztési ciklus fázisonkénti instrukcióit tartalmazza, **skillekre** (`prompts/skills/` — fázis-receptek) és **ágensekre** (`prompts/agents/` — specialista subagentek) szervezve. Minden skill egy fázist vezérel — ezeket a promptokat adjuk be egy AI-agentnek, hogy az adott fázist elvégezze.

A rendszer célja: egy-két fejlesztő és egy AI-agent együtt, következetes minőségű, tesztelt szoftvert fejlesszen ciklusonként leszállítható egységekben. A promptok adják az agentnek a keretet, korlátokat, minőségellenőrzési listát és megállási szabályokat.

---

## A workflow felépítése

A teljes fejlesztési folyamat 9 lépésből áll (0–8):

**Projekt szintű setup (egyszer fut le):**
- `00` — Projekt inicializálás: `conventions.md` létrehozása (konvenciók, tech stack, portok, merge stratégia)
- `01` — Ciklusok kezelése: `specs/roadmap.md` létrehozása/karbantartása (cikluslista, függőségek, teszt kritériumok)

**Per-ciklus loop (minden fejlesztési ciklusra ismétlődik):**
- `02` — Spec írás: `specs/cycle-NN-<cycle-name>/spec.md` — státusz: `Tervezésre kész`
- `03` — Plan írás: `specs/cycle-NN-<cycle-name>/plan.md` — státusz: `Task írásra kész`
- `04` — Tasks írás: `specs/cycle-NN-<cycle-name>/tasks.md` — státusz: `Implementálásra kész`
- `05` — Analyze: kereszt-fázisos konzisztencia ellenőrzés (read-only) — `analyze-report.md` PASS/FAIL
- `06` — Implementálás: kód + `tasks.md` — státusz: `Validálásra kész`
- `07` — Validálás: tesztek + DoD ellenőrzés — eredmény: PASS / FAIL (riport a `test-report/` mappában)
- `08` — Review & Merge: code review + merge (a `conventions.md` Merge stratégiája szerint)

Minden ciklus mappája: `specs/cycle-NN-<cycle-name>/`

---

## A prompt fájlok

| Fájl | Fázis | Bemenet | Kimenet |
|------|-------|---------|---------|
| `prompts/skills/00-init-project.md` | Projekt init | Projekt leírás | `conventions.md` |
| `prompts/skills/01-add-cycles.md` | Ciklusok kezelése | HLD/LLD vagy leírás | `specs/roadmap.md` |
| `prompts/skills/02-write-spec.md` | Spec | Roadmap + ciklus neve | `spec.md` (`Tervezésre kész`) |
| `prompts/skills/03-write-plan.md` | Plan | `spec.md` | `plan.md` (`Task írásra kész`) |
| `prompts/skills/04-write-tasks.md` | Tasks | `plan.md` | `tasks.md` (`Implementálásra kész`) |
| `prompts/skills/05-analyze.md` | Analyze | ciklus mappa | `analyze-report.md` (PASS/FAIL) |
| `prompts/skills/06-implement.md` | Implementálás | `tasks.md` | Kód + `tasks.md` (`Validálásra kész`) |
| `prompts/skills/07-validate.md` | Validálás | `spec.md`, `plan.md`, `tasks.md` | PASS/FAIL riport a `test-report/` mappában |
| `prompts/skills/08-review-and-merge.md` | Review & Merge | Cycle branch, `plan.md`, `spec.md` | `code-review.md` + merged branch |

A specialista subagentek a `prompts/agents/` alatt: `reviewer.md` (08), `analyzer.md` (05), `researcher.md` (03).

A `prompts/README.md` minden fázishoz tartalmazza a felhasználónak szánt copy-paste prompt blokkot.

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

**8. Megállási szabályok**
A 04-es (tasks) és 06-os (implement) prompt explicit felsorolja azokat az eseteket, amikor az agent megáll és visszakérdez — ne folytassa bizonytalan vagy ellentmondásos helyzetben.

**9. Kereszt-fázisos konzisztencia ellenőrzés (05 — analyze)**
A 04 (tasks) után, az implementáció előtt egy read-only analyze fázis fut: a `spec.md` ↔ `plan.md` ↔ `tasks.md` ↔ `conventions.md` négyest 5 kategóriában ellenőrzi (duplikáció, ambiguitás, alulspecifikáció, konvenció-ütközés, lefedettségi hiány). FAIL esetén státusz-visszafordítással visszalép a legkorábbi érintett tervezési fázisra.

---

## A promptok aktuális állapota

A rendszer aktívan használatban van — több fejlesztési ciklus (cycle-01 – cycle-16) lefutott már ezekkel a promptokkal. A skill fájlok a `prompts/skills/`, a specialista ágensek a `prompts/agents/` mappában olvashatók.

---

## Feladatod

Olvasd be a releváns skill fájlokat a `prompts/skills/` mappából (és szükség szerint az ágenseket a `prompts/agents/`-ból), majd segíts a következő fejlesztési célban:

**[IDE ÍRD LE A KONKRÉT FEJLESZTÉSI CÉLT — pl.:]**
- „A 03-as plan skill minőségellenőrzési listája hiányos — egészítsd ki."
- „A 06-os implement skill nem kezeli megfeloloen a delegalas esetét."
- „Vezess be egy uj 09-es fazist: changelog generalas."
- „Altalanos felulvizsgalat: hol vannak kovetkezetlensegek a skillek kozott?"

Ha nincs konkrét cél megadva, végezz általános felülvizsgálatot: keress következetlenségeket, hiányzó megállási szabályokat, scope-szivárgást a fázisok között, és javasolj konkrét javításokat.
