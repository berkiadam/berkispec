<!--
  A `01-add-cycles` PROJEKT-NYELVI blokkjai (9.4 kiemelés).
  Ezt a fájlt a telepítő build-time emeli be az INCLUDE markerek helyére, a
  választott PROJEKT-nyelv (`PROJECT_LANG`) szerint; a marker alakja
  `lang/01-add-cycles.md#<horgony>`.
  A blokkok SZÓ SZERINT kerültek ide — ne fogalmazd át, ne egységesítsd.
  Az ANCHOR sorok NEM részei a beemelt szövegnek, csak határolók (8.9).
  FIGYELEM: ebbe a vezető jegyzetbe ne kerüljön komment-lezáró szekvencia.
-->

<!-- ANCHOR:roadmap-struktura -->
# Fejlesztési Roadmap

**Státusz:** `Piszkozat` | `Nyitott kérdések vannak` | `Kész`

## Nyitott kérdések

- [ ] K01 — <kérdés szövege>
- [x] K02 — <kérdés szövege> → <döntés röviden>

## Cycle 01 — <cím>

**Viselkedés:** Mit tud a rendszer a ciklus végén? (1-2 mondat, felhasználói perspektívából)

**Érintett komponensek:** Mely rendszerrészek változnak?

**Előfeltétel:** — (vagy: Cycle NN)

**Mock stratégia:** Mit kell mock-olni a még nem kész komponensekből?

**Teszt kritérium:** Hogyan ellenőrizhető, hogy the ciklus kész? (konkrét, eldönthető állítás)

---

## Cycle 02 — <cím>

...

<!-- ANCHOR:BD5-ciklus-blokk-sablon -->
## Cycle NN — <cím>

**Viselkedés:** Mit tud a rendszer a ciklus végén? (1-2 mondat, felhasználói perspektívából)

**Érintett komponensek:** Mely rendszerrészek változnak?

**Előfeltétel:** — (vagy: Cycle NN — a meglévők közül)

**Mock stratégia:** Mit kell mock-olni a még nem kész komponensekből?

**Teszt kritérium:** Hogyan ellenőrizhető, hogy a ciklus kész? (konkrét, eldönthető állítás)

<!-- ANCHOR:CD1-design-input-sablon -->
# cycle NN design input from user

> **Ez a fájl a Tiéd.** Ide írhatod le a saját szavaiddal, hogy mit szeretnél ebben a ciklusban:
> elvárások, viselkedés-vázlat, példa kérés/válasz, folyamatleírás, korlátok, hivatkozások, jegyzetek.
>
> **Kitöltése nem kötelező** — üresen hagyva a flow változatlanul működik.
> Ha viszont írsz ide, két fázis is automatikusan beolvassa:
> - `bs-write-spec` (02) — a **viselkedési** tartalmat, a `spec.md` kiindulópontjaként (a `roadmap.md` bejegyzése mellett);
> - `bs-write-code-plan` (03a) — a **technikai/eljárás-jellegű** tartalmat (parancsok, hostok, komponensek, korlátok) a `plan.md`-hez.
>
> Formátum nincs megkötve: folyó szöveg, felsorolás, táblázat, kódrészlet — bármi jó.
> Ezt a fájlt egyik fázis sem írja felül.

<!-- Írj ide. -->

<!-- ANCHOR:specs-ures-kerdes -->
> *"A `specs/` könyvtár üres. Mit szeretnél csinálni?*
> *A) Teljes roadmap tervezés — meghatározzuk az összes fejlesztési ciklust és létrehozzuk a `specs/roadmap.md`-t*
> *B) Egyetlen ciklus hozzáadása — csak egy új ciklust adunk a roadmap-hez"*

<!-- ANCHOR:ciklusok-roadmappal -->
     > *"Találtam [N] meglévő ciklust: [cycle-01-xxx, cycle-02-xxx, ...]. Új ciklust adok a roadmap-hez."*

<!-- ANCHOR:ciklusok-roadmap-nelkul -->
     > *"Találtam [N] meglévő ciklust a `specs/` mappában, de nem találom a `specs/roadmap.md` fájlt. Melyik ciklussal dolgozunk most? Az adott ciklus roadmap-blokkját pótolom (per-ciklus, a ciklus feature branch-én) — a többi ciklus a saját branch-én / a merge-elt main-roadmap-ben él."*

<!-- ANCHOR:roadmap-statusz-megerosites -->
*"A roadmap minőségellenőrzése átment és minden kérdés lezárt. Készen áll a roadmap? Ha megerősíted, átállítom `Kész` státuszra."*

<!-- ANCHOR:A-mod-zaro-uzenet -->
*"A roadmap kész. Folytathatjuk az 1. ciklus spec fázisával (02). Létrehoztam a `specs/cycle-01-<name>/cycle-design-input.md` fájlt — ide leírhatod a saját szavaiddal az 1. ciklus specifikációját. Kitöltése nem kötelező, de ha írsz bele, a `bs-write-spec` figyelembe fogja venni."*

<!-- ANCHOR:BQ2-ciklusszam-jelzes -->
   > *"Meglévő ciklusok: [N db — cycle-01-xxx, ...]. Következő ciklusszám: [NN]."*

<!-- ANCHOR:BD5-cel-kerdes -->
   > *"Mi az új ciklus célja? Röviden írd le, milyen viselkedést szeretnél megvalósítani."*

<!-- ANCHOR:BS-quick-flow-javaslat -->
   > > *„Ez a feladat elég kicsinek tűnik a teljes fejlesztési ciklushoz (külön spec/plan/tasks + analyze/validate/review). Javaslom helyette az egyszerűsített flow-t (`/bs-quick-flow`): `spec.md` → `task.md` → implementáció, néhány lépésben. Mehetünk azzal, vagy mégis teljes ciklust szeretnél?"*

<!-- ANCHOR:BD5-nevjavaslat -->
   > *"A cél alapján a javasolt név: `[javasolt-név]`. Ez lesz a branch és a mappa neve is (pl. `cycle-NN-[javasolt-név]`). Megfelelő, vagy inkább mást szeretnél?"*

<!-- ANCHOR:BD5-roadmap-megerosites -->
   > *"Hozzáadtam a Cycle NN — [cím] leírást. Ha megerősíted, frissítem a roadmap státuszát `Kész`-re és létrehozom a ciklus könyvtárát."*

<!-- ANCHOR:B-mod-zaro-uzenet -->
     > *"Cycle NN — [cím] hozzáadva. Könyvtár létrehozva: `specs/cycle-NN-<cycle-name>/`*
     >
     > *Létrehoztam a `specs/cycle-NN-<cycle-name>/cycle-design-input.md` fájlt. **Ide leírhatod a saját szavaiddal a ciklus specifikációját** — elvárásokat, vázlatot, példákat, bármit, ami a fejedben van. **Kitöltése nem kötelező**, üresen is folytatható a flow; de ha írsz bele, a `bs-write-spec` (02) beolvassa és a spec kiindulópontjaként figyelembe veszi. Érdemes a spec fázis indítása ELŐTT kitölteni.*
     >
     > *Következő lépés — spec írás. Az új fázis megkezdése előtt mindenképpen futtass egy `/clear` parancsot a kontextus kiürítéséhez, majd használd ezt a parancsot:*
     > ```
     > /bs-write-spec input: @specs/roadmap.md, ciklus: cycle-NN-<cycle-name>
     > ```"*

<!-- ANCHOR:BS18-design-input-brainstormbol -->
> *„Létrehoztam a `specs/cycle-NN-<name>/cycle-design-input.md` fájlt, és feltöltöttem a NN. brainstorm session döntéseivel. **Olvasd át** — ez lesz a `bs-write-spec` (02) kiindulópontja. Bátran javítsd, bővítsd vagy húzz ki belőle; a fájl a Tiéd, egyik fázis sem írja felül."*

<!-- ANCHOR:BQ5-C-mod-jelzes -->
   > *"A(z) `cycle-NN-<name>` roadmap-blokkját pótoltam/javítottam a `specs/roadmap.md`-ben. Kérlek nézd át. Ha rendben van és megerősíted, commitolom a ciklus branch-én."*
