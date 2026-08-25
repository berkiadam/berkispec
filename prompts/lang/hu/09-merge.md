<!--
  A `09-merge` PROJEKT-NYELVI blokkjai (9.4 kiemelés).
  Ezt a fájlt a telepítő build-time emeli be az INCLUDE markerek helyére, a
  választott PROJEKT-nyelv (`PROJECT_LANG`) szerint; a marker alakja
  `lang/09-merge.md#<horgony>`.
  A blokkok SZÓ SZERINT kerültek ide — ne fogalmazd át, ne egységesítsd.
  Az ANCHOR sorok NEM részei a beemelt szövegnek, csak határolók (8.9).
  FIGYELEM: ebbe a vezető jegyzetbe ne kerüljön komment-lezáró szekvencia.
-->

<!-- ANCHOR:RD8-merge-megerosites -->
> *"A validálás és a review tiszta (07), a doc-sync kapu zöld. Készen állok a merge-re a `<szolgáltató>` stratégia szerint (`feature/cycle-NN-<cycle-name>` → `<target branch>`). Végrehajthatom?"*

<!-- ANCHOR:zaro-uzenet -->
> *"A validálás és a kódreview a 07-ben sikeres volt, a doc-sync kapu zöld, és a ciklust lezártam a `conventions.md` Merge stratégiája szerint (`<lokális squash merge` / `PR létrehozva>`). A ciklus sikeresen lezárult.*
>
> *Megkezdhető a következő ciklus. Az új ciklus megkezdése előtt mindenképpen futtass egy `/clear` parancsot a kontextus kiürítéséhez.*
>
> *Új ciklus hozzáadásához:*
> ```
> /bs-add-cycles
> ```
> *Vagy ha a következő ciklus már a roadmap-en van, közvetlenül a spec fázissal:*
> ```
> /bs-write-spec input: @specs/roadmap.md, ciklus: cycle-NN-<cycle-name>
> ```"*
