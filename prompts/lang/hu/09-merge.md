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

<!-- ANCHOR:L13-D1-pr-kotelezo -->
> *"A `conventions.md` `## Review and merge` szekciója szerint ebben a projektben **PR feladás van** (`PR submission: yes`). A `/bs-review-and-merge` csak PR nélküli üzemmódban használható — PR mellett a ciklusvég három külön lépés:*
> ```
> /bs-create-pr input: @specs/cycle-NN-<cycle-name>
> /bs-review     input: @specs/cycle-NN-<cycle-name>
> /bs-merge      input: @specs/cycle-NN-<cycle-name>
> ```
> *Kezdd a `/bs-create-pr`-rel."*

<!-- ANCHOR:L13-D1-pr-felesleges -->
> *"A `conventions.md` `## Review and merge` szekciója szerint ebben a projektben **nincs PR feladás** (`PR submission: no`) — a ciklus a `/bs-review-and-merge` skillel zárul, egy lépésben. Mégis nyissak PR-t (pl. mert ennél a ciklusnál külső review kell), vagy váltsunk a `/bs-review-and-merge`-re?"*

<!-- ANCHOR:zaro-uzenet-create-pr -->
> *"A PR megnyitva: `<PR link>`. A ciklus ága felküldve, a `cycle-status.md` frissítve — a roadmap-en a ciklus `⏳ verifikációra vár` állapotban áll, mert a merge utáni verifikáció még hátravan.*
>
> *A következő lépés a review a PR-en. Előtte futtass egy `/clear` parancsot a kontextus kiürítéséhez:*
> ```
> /bs-review input: @specs/cycle-NN-<cycle-name>
> ```
> *Központosított SDD-ben ezt a CI/CD indítja automatikusan a PR megnyitására — ilyenkor nincs teendőd, csak az értesítést várd."*

<!-- ANCHOR:zaro-uzenet-review -->
> *"A review lefutott a PR-en, az eredménye a `test-report/ci-code-review.md`-ben. A `07` lokális review-ja (`test-report/code-review.md`) érintetlen — a `bs-merge` kapuja mindkettőt olvassa.*
>
> *A következő lépés a beolvasztás a post-merge teszt-körrel. Előtte `/clear`:*
> ```
> /bs-merge input: @specs/cycle-NN-<cycle-name>
> ```"*

<!-- ANCHOR:zaro-uzenet-merge -->
> *"A post-merge teszt-kör (`VP2`) zöld volt, a bizonyítéka a `test-report/post-merge/` mappában, és a ciklus beolvadt a fő branch-be.*
>
> *Ha a `conventions.md`-ben be van kapcsolva a dev-teszt (`Dev deployment test: yes`), a ciklus MÉG NEM zárult le — hátravan az utolsó verifikáció:*
> ```
> /bs-dev-test input: @specs/cycle-NN-<cycle-name>
> ```
> *Ha nincs bekapcsolva, a ciklus lezárult. A következő ciklus megkezdése előtt futtass egy `/clear` parancsot:*
> ```
> /bs-add-cycles
> ```"*

<!-- ANCHOR:zaro-uzenet-dev-test -->
> *"A dev-teszt kör (`VP3`) lefutott az integrált környezetben, a bizonyítéka a `test-report/dev-test/` mappában<a test manager futás-URL-je, ha van>. Ez volt az utolsó engedélyezett verifikációs pont, ezért a ciklust lezártam a roadmap-en.*
>
> *Megkezdhető a következő ciklus. Előtte mindenképpen futtass egy `/clear` parancsot a kontextus kiürítéséhez:*
> ```
> /bs-add-cycles
> ```"*
