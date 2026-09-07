<!--
  A `run-tests` (bs-run-tests segédparancs) PROJEKT-NYELVI blokkjai
  (9.4 kiemelés, KT9/3).
  Ezt a fájlt a telepítő build-time emeli be az INCLUDE markerek helyére, a
  választott PROJEKT-nyelv (`PROJECT_LANG`) szerint; a marker alakja
  `lang/run-tests.md#<horgony>`.
  A blokkok SZÓ SZERINT kerültek ide — ne fogalmazd át, ne egységesítsd.
  Az ANCHOR sorok NEM részei a beemelt szövegnek, csak határolók. Azért
  HTML-komment és nem `##` címsor a határoló, mert a sablonok maguk is tele
  vannak `##` címsorral (8.9).
  FIGYELEM: ebbe a vezető jegyzetbe ne kerüljön komment-lezáró szekvencia, és a
  fájlba INCLUDE marker sem (8.5).
-->

<!-- ANCHOR:nincs-szekcio-stop -->
*„A `conventions.md`-ben nincs `## Teszt-futtatás` szekció projekt-szintű futtatási
táblával, ezért cikluson kívül nem tudok tesztet futtatni: nem tudom, milyen kategóriák
vannak, és melyiket milyen paranccsal indítom. Ez a `00-init-project` fázis kötelező
szekciója (KT1) — pótoljuk a `/bs-init-project` paranccsal, vagy add meg a kategóriákat és
a parancsokat, és felveszem a szekciót a `conventions.md`-be a megerősítésed után."*

<!-- ANCHOR:kategoria-kerdes -->
*„Melyik teszt-kategóriát futtassam, és melyik környezetben? Deklarált kategóriák:
<kategóriák a conventions.md szótárából>. A `remote` célnál előbb lefuttatom az
elérhetőségi probe-ot. (Megadhatod így is: `/bs-run-tests <kategória> <local|remote>`.)"*

<!-- ANCHOR:tuzfal-figyelmeztetes -->
> 🔴 **Ez a futás NEM ciklus-bizonyíték.** Az eredmény a `test-runs/` fába kerül, a
> `results.json` `cycle` mezője `null`, és a `07-validate` kapui (`dod-check.py`,
> `report-gate-check.py`) a `test-runs/` alatti útvonalat **visszautasítják** (`exit 2`).
> Ha ciklus-bizonyítékra van szükség, a `06`/`07` körét kell lefuttatni, és az a ciklus
> `test-report/<fázis>/round-NN/` mappájába ír.

<!-- ANCHOR:latest-json-vaz -->
{
  "<kategória>": {
    "path": "test-runs/<kategória>/<YYYY-MM-DDTHH-MMZ>/<env>",
    "env": "local | remote",
    "finished_at": "<YYYY-MM-DDTHH-MMZ>",
    "verdict": "PASS | FAIL",
    "passed": 0,
    "failed": 0,
    "skipped": 0
  }
}

<!-- ANCHOR:zaro-uzenet -->
> *"Teszt-futtatás kész — kategória: <kategória>, környezet: <local|remote>.*
> - *Eredmény: <N> futott / <N> bukott / <N> kihagyva — VERDICT: <PASS|FAIL>*
> - *A kihagyott tesztek NEM zöldek: <a kihagyott tesztek nevei, vagy „nincs">*
> - *Futás-mappa: `test-runs/<kategória>/<időbélyeg>/<env>/` · gépi összegzés: `results.json`*
> - *Tételenként visszakereshető: <a TL-NNN mappák felsorolása, vagy „nincs leltár-hozzárendelés">*
> - *A `test-runs/` mappa mérete most: <méret>*
>
> *Ez a futás nem ciklus-bizonyíték — a `07` kapuja nem fogadja el."*
