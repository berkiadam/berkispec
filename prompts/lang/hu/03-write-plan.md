<!--
  A `03-write-plan` PROJEKT-NYELVI blokkjai (9.4 kiemelés).
  Ezt a fájlt a telepítő build-time emeli be az INCLUDE markerek helyére, a
  választott PROJEKT-nyelv (`PROJECT_LANG`) szerint; a marker alakja
  `lang/03-write-plan.md#<horgony>`.
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
*"A plan minőségellenőrzése átment és minden kérdés lezárt. Készen áll a plan tasks írásra? Ha megerősíted, átállítom `Task írásra kész` státuszra."*

<!-- ANCHOR:zaro-uzenet -->
> *"A plan kész. Folytathatjuk a 4. lépéssel (tasks). Az új fázis megkezdése előtt mindenképpen futtass egy `/clear` parancsot a kontextus kiürítéséhez, majd használd ezt a parancsot:*
> ```
> /bs-write-tasks input: @specs/cycle-NN-<cycle-name>/plan.md
> ```"*
