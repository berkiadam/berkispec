<!--
  A `quick-flow` PROJEKT-NYELVI blokkjai (9.4 kiemelés).
  Ezt a fájlt a telepítő build-time emeli be az INCLUDE markerek helyére, a
  választott PROJEKT-nyelv (`PROJECT_LANG`) szerint; a marker alakja
  `lang/quick-flow.md#<horgony>`.
  A blokkok SZÓ SZERINT kerültek ide — ne fogalmazd át, ne egységesítsd.
  Az ANCHOR sorok NEM részei a beemelt szövegnek, csak határolók (8.9).
  FIGYELEM: ebbe a vezető jegyzetbe ne kerüljön komment-lezáró szekvencia.
-->

<!-- ANCHOR:BS-flow-valtas-javaslat -->
> *„Ez a feladat a vártnál nagyobb / összetettebb (pl. több komponenst érint, nagyobb kódírást igényel). Javaslom, hogy ne az egyszerűsített flow-t használjuk, hanem a teljes berki spec folyamatot, amely a `01-add-cycles` skill-lel indul (roadmap + dedikált ciklus). Folytathatom úgy?"*

<!-- ANCHOR:BS-roadmap-sor -->
## Cycle NN — <cím>

**Viselkedés:** <mit tud a rendszer a ciklus végén — 1-2 mondat, felhasználói perspektívából>

**Érintett komponensek:** <mely rendszerrészek változnak>

**Teszt kritérium:** <konkrét, eldönthető állítás arról, mikor kész a ciklus>

_(Egyszerűsített [quick-flow] ciklus. A lezáráskor a címsor `✅` jelet kap.)_

<!-- ANCHOR:BS-drift-sor -->
- **<azonosító>** — Terv: <mit ír ma a `docs-generated/`>. As-built: <mit változtatott ez a ciklus>. Indok/státusz: egyszerűsített ciklus `cycle-NN-<cycle-name>`, a `docs-generated/` átvezetése a következő teljes ciklus `08-doc-sync` fázisára vár.
