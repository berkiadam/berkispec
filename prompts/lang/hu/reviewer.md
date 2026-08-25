<!--
  A `reviewer` PROJEKT-NYELVI blokkjai (9.4 kiemelés).
  Ezt a fájlt a telepítő build-time emeli be az INCLUDE markerek helyére, a
  választott PROJEKT-nyelv (`PROJECT_LANG`) szerint; a marker alakja
  `lang/reviewer.md#<horgony>`.
  A blokkok SZÓ SZERINT kerültek ide — ne fogalmazd át, ne egységesítsd.
  Az ANCHOR sorok NEM részei a beemelt szövegnek, csak határolók (8.9).
  FIGYELEM: ebbe a vezető jegyzetbe ne kerüljön komment-lezáró szekvencia.
-->

<!-- ANCHOR:RV1-code-review-formatum -->
# Cycle NN: <cím> — Code review

**Státusz:** Folyamatban | Kész

## Összefoglaló

_Egy-két mondat: merge-elhető-e, vagy mi blokkol. Részleges review esetén ide kerül, mit nem néztél át._

## Kritikus javítandók (Must Fix)

- [ ] **MF-01** — <file>:<line> — <probléma rövid leírása>
- [ ] **MF-02** — <file>:<line> — <probléma rövid leírása>

## Javasolt fejlesztések (Suggestions)

- **S-01** — <file>:<line> — <javaslat rövid leírása>

<!-- ANCHOR:RV1-lezaras-jeloles -->
`- [x] **MF-01** — …  ✅ javítva`
