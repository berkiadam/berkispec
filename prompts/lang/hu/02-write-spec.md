<!--
  A `02-write-spec` PROJEKT-NYELVI blokkjai (9.4 kiemelés).
  Ezt a fájlt a telepítő build-time emeli be az INCLUDE markerek helyére, a
  választott PROJEKT-nyelv (`PROJECT_LANG`) szerint; a marker alakja
  `lang/02-write-spec.md#<horgony>`.
  A blokkok SZÓ SZERINT kerültek ide — ne fogalmazd át, ne egységesítsd.
  Az ANCHOR sorok NEM részei a beemelt szövegnek, csak határolók (8.9).
  FIGYELEM: ebbe a vezető jegyzetbe ne kerüljön komment-lezáró szekvencia.
-->

<!-- ANCHOR:spec-questions-struktura -->
# Cycle NN: <cím> — Spec kérdések

- [ ] K01 — [kérdés szövege]
- [x] K02 — [kérdés szövege] → [döntés / válasz röviden]
- [ ] K03 — [kérdés szövege] _(K02 megválaszolásából merült fel)_

<!-- ANCHOR:statusz-megerosites -->
*"A spec minőségellenőrzése átment és minden kérdés lezárt. Készen áll a spec tervezésre? Ha megerősíted, átállítom `Tervezésre kész` státuszra."*

<!-- ANCHOR:zaro-uzenet -->
> *"A spec kész. Folytathatjuk a 3. lépéssel (plan). Az új fázis megkezdése előtt mindenképpen futtass egy `/clear` parancsot a kontextus kiürítéséhez, majd használd ezt a parancsot:
> ```
> /bs-write-plan input: @specs/cycle-NN-<cycle-name>/spec.md, ciklus: cycle-NN-<cycle-name>
> ```"*
