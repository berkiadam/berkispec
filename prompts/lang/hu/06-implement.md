<!--
  A `06-implement` PROJEKT-NYELVI blokkjai (9.4 kiemelés).
  Ezt a fájlt a telepítő build-time emeli be az INCLUDE markerek helyére, a
  választott PROJEKT-nyelv (`PROJECT_LANG`) szerint; a marker alakja
  `lang/06-implement.md#<horgony>`.
  A blokkok SZÓ SZERINT kerültek ide — ne fogalmazd át, ne egységesítsd.
  Az ANCHOR sorok NEM részei a beemelt szövegnek, csak határolók (8.9).
  FIGYELEM: ebbe a vezető jegyzetbe ne kerüljön komment-lezáró szekvencia.
-->

<!-- ANCHOR:check-log-sablon -->
# `[CHECK]` futásnapló — cycle-NN-<cycle-name>

_(Append-only. A 06-implement írja, taskonként. A 07/09 nem ír bele.)_

| Idő | Task | Próba | Mód | Parancs | Eredmény |
|---|---|---|---|---|---|
| 2026-08-07 10:12 | T004 | 1/3 | normál | `npm test -- token-store` | ✗ 12 passed / 1 failed — `initHash returns stable hash` |
| 2026-08-07 10:19 | T004 | 2/3 | normál | `npm test -- token-store` | ✓ 13 passed / 0 failed / 0 skipped |
| 2026-08-07 11:40 | T041 | 1/3 | validate-loop | `npm test -- auth` | ✓ 27 passed / 0 failed / 0 skipped |

## Megjegyzések
- **T004** — átmeneti port-csere a `[CHECK]` futtatásához: 5432 → 5433 (`docker-compose.yml`); a commit előtt visszaállítva.

<!-- ANCHOR:check-log-pelda-sor -->
## <Task azonosító> — <rövid cím>

**Mi volt a gond:** <a hiba tömör leírása>
**Mit próbáltunk:** <sikertelen kísérletek röviden>
**Mi lett a megoldás:** <a végül működő megközelítés>

<!-- ANCHOR:commit-javaslat -->
*"Az implementáció előtt érdemes ezeket commitálni — ha félremegy az implementáció, egy `git reset --hard` visszaállítja a kiindulóállapotot."*

<!-- ANCHOR:commit-kerdes -->
*"Commitáljam ezeket most?"*

<!-- ANCHOR:zaro-uzenet -->
> *"Az implementáció kész. Folytathatjuk a 7. lépéssel (validate). Az új fázis megkezdése előtt mindenképpen futtass egy `/clear` parancsot a kontextus kiürítéséhez, majd használd ezt a parancsot:*
> ```
> /bs-validate input: @specs/cycle-NN-<cycle-name>
> ```"*
