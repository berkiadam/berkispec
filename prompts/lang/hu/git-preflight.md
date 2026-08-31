<!--
  A `git-preflight` PROJEKT-NYELVI blokkjai (9.4 kiemelés).
  Ezt a fájlt a telepítő build-time emeli be az INCLUDE markerek helyére, a
  választott PROJEKT-nyelv (`PROJECT_LANG`) szerint; a marker alakja
  `lang/git-preflight.md#<horgony>`.
  A blokkok SZÓ SZERINT kerültek ide — ne fogalmazd át, ne egységesítsd.
  Az ANCHOR sorok NEM részei a beemelt szövegnek, csak határolók (8.9).
  FIGYELEM: ebbe a vezető jegyzetbe ne kerüljön komment-lezáró szekvencia.
-->

<!-- ANCHOR:BD13-commit-vagy-folytas -->
*„Commitáljam ezeket most, vagy folytassam?"*

<!-- ANCHOR:PW3-soros-vagy-parhuzamos -->
*„A `<másik-ciklus>` ciklus ága még nyitva van. Két lehetőség van: **A)** lezárjuk (merge/PR), visszaállsz `main`-re, és itt tervezzük az új ciklust — vagy **B)** párhuzamosan dolgozunk: nyitok neki egy külön `git worktree`-t, és ott indul a tervezés. Melyiket válasszuk?"*

<!-- ANCHOR:PW3-worktree-ujrainditas -->
*„Létrehoztam a worktree-t ide: `<a worktree ABSZOLÚT útvonala>` — az eszköz-mappák (skillek, subagentek, kapu-scriptek) át vannak másolva. Ebben a munkamenetben nem tudom folytatni, mert az ágens a jelenlegi mappához van kötve. Kérlek: **(1)** zárd be ezt az agentic CLI-t, **(2)** lépj át a másik mappába: `cd <a worktree ABSZOLÚT útvonala>`, **(3)** indítsd el ott újra ugyanazt az eszközt (`<az eszköz indítóparancsa>`), **(4)** és futtasd újra ezt a fázist. Ez a mappa és a jelenlegi ciklus ága érintetlen marad."*
