<!--
  A `03a-write-code-plan` PROJEKT-NYELVI blokkjai (9.4 kiemelés).
  Ezt a fájlt a telepítő build-time emeli be az INCLUDE markerek helyére, a
  választott PROJEKT-nyelv (`PROJECT_LANG`) szerint; a marker alakja
  `lang/03a-write-code-plan.md#<horgony>`.
  A blokkok SZÓ SZERINT kerültek ide — ne fogalmazd át, ne egységesítsd.
  Az ANCHOR sorok NEM részei a beemelt szövegnek, csak határolók (8.9).
  FIGYELEM: ebbe a vezető jegyzetbe ne kerüljön komment-lezáró szekvencia.
-->

<!-- ANCHOR:plan-questions-struktura -->
# Cycle NN: <cím> — Plan kérdések

- [ ] K01 — [kérdés szövege]
- [x] K02 — [kérdés szövege] → [döntés / válasz röviden]
- [ ] K03 — [kérdés szövege] _(K02 megválaszolásából merült fel)_

<!-- ANCHOR:statusz-megerosites -->
*"A kód-terv minőségellenőrzése átment és minden kérdés lezárt. Készen áll a plan kód-fele a teszt-tervezésre? Ha megerősíted, átállítom `<status:ready_for_test_plan>` státuszra."*

<!-- ANCHOR:zaro-uzenet -->
> *"A kód-terv kész. Folytathatjuk a teszt-tervvel. Az új fázis megkezdése előtt mindenképpen futtass egy `/clear` parancsot a kontextus kiürítéséhez, majd használd ezt a parancsot:*
> ```
> /bs-write-test-plan input: @specs/cycle-NN-<cycle-name>/plan.md
> ```"*
