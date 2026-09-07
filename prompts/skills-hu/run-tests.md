---
name: bs-run-tests
description: "berkispec - segédparancs. Teszt-futtatás CIKLUSON KÍVÜL, kategóriánként: a conventions.md 'Teszt-futtatás' szekciójának projekt-szintű táblájából futtatja a run-tests.py-t, és az eredményt a gitignore-olt 'test-runs/<kategória>/<UTC-időbélyeg>/<env>/' fába írja. Előfeltétel: a conventions.md 'Teszt-futtatás' szekciója kitöltve (a 00-init-project írja). Nem fázis: a 00-09 folyamatnak nem része, nem változtat ciklus-státuszt, bármikor újrafuttatható — és az eredménye SOHA nem ciklus-bizonyíték."
prerequisites:
  - "conventions.md → ## <sec:cv_test_execution> szekció (<field:f_test_categories>, projekt-szintű futtatási tábla, tesztfájl-helyek)"
output:
  - "test-runs/<kategória>/<YYYY-MM-DDTHH-MMZ>/<env>/ — a futás mappája, benne a results.json és a riport-artefaktumok"
  - "test-runs/latest.json — kategóriánként az utolsó futás útvonala és összegzése"
scripts:
  - "scripts/run-tests.py --table-source conventions — a futtató"
shared:
  - "shared/python-cmd.md"
---
# Teszt-futtatás cikluson kívül (`bs-run-tests`) — segédparancs
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

Ez **nem fázis:** a `00–09` láncnak nem része, a ciklus státusz-láncához (`spec.md` / `plan.md` / `tasks.md`) **nem nyúl**, ciklus-artefaktumot **nem ír**, subagent nélkül fut, és bármikor újrafuttatható. Egyetlen dolgot csinál: lefuttatja a projekt **egy teszt-kategóriáját** a projekt-szintű futtatási táblából, és az eredményt egy **cikluson kívüli, gitignore-olt** fába írja.

**Miért kell:** a keret minden gépi futtatása eddig **egy ciklushoz és egy körhöz** volt kötve (a `run-tests.py` `plan.md`-et és `--round-dir`-t kért). Az „futtasd le az összes e2e tesztet" kérés így a kereten **kívülre** szorult: kézzel, bizonyíték nélkül. Ez a parancs behozza a keretbe — **de nem a bizonyíték-logikába**.

> 🔴 **A legfontosabb szabály, amit ki kell mondanod (D8):** az itt keletkező eredmény **SOHA nem ciklus-bizonyíték**. A `test-runs/` alatti futásnak nincs `DoD-NN`/`TS-NN` joinja, nincs kör-száma, tehát a TR7 frissesség és a RUN1 kör-lefedettség sem értelmezhető rá. A `dod-check.py` és a `report-gate-check.py` a `test-runs/` alatti útvonalat `exit 2`-vel **visszautasítja** — ezt ne próbáld megkerülni.

---

## Cheat sheet

| Szekció | Egy mondatban |
|---|---|
| Előfeltétel (KT1) | A `conventions.md` `## <sec:cv_test_execution>` szekciója kitöltve. Enélkül **STOP** — a `00-init-project` hiánya, nem a tiéd. |
| Belépő (KT4) | `/bs-run-tests` (kérdezz), `/bs-run-tests <kategória>`, `/bs-run-tests <kategória> <local\|remote>`. |
| Nem fázis (D10) | Státuszt nem változtat, ciklus-artefaktumot nem ír, subagent nélkül fut, a `00`–`09` láncot nem érinti. |
| Kimenet (KT5) | `test-runs/<kategória>/<UTC-időbélyeg>/<env>/` + `test-runs/latest.json`. Más helyre **nem** írsz. |
| Tűzfal (D8) | Az eredmény nem ciklus-bizonyíték; a `07` kapui visszautasítják. **Ezt kimondod a záró üzenetben.** |
| Leltár-join (KT5) | A `<TL-NNN>` mappaszegmens joinolja az eredményt a teszt-leltárhoz — tételenként visszakereshető. |
| Takarítás (D12) | A `test-runs/` **soha nem takarít magától**; a méretét kiírod, ritkítást csak explicit kérésre ajánlasz. |

---

## <field:f_prerequisite>

1. **`conventions.md` beolvasás.** Olvasd be a projekt gyökerében a `conventions.md` `## <sec:cv_test_execution>` szekcióját — **csak ezt a szekciót**, ne a teljes fájlt. Kell belőle: a `**<field:f_test_categories>:**` szótár, a **projekt-szintű futtatási tábla** és a `### Tesztfájl-helyek` tábla.

2. **🔴 Belépő kapu.** Ha a `conventions.md` nem létezik, vagy nincs benne `## <sec:cv_test_execution>` szekció futtatási táblával, **STOP** — ne találgass parancsot, és ne futtass „valószínű" teszt-parancsot:

   <!-- INCLUDE:lang/run-tests.md#nincs-szekcio-stop -->

   Ez a szekció a `00-init-project` **kötelező** része (KT1). A pótlása a `00` fázis dolga; ha a felhasználó itt akarja megadni, a `conventions.md`-be **csak a megerősítése után** írd bele, és **kizárólag ezt az egy szekciót**.

3. **Kategória- és környezet-választás.** Ha a hívás megadta (`/bs-run-tests rest-e2e remote`), azt használd. Ha nem, **kérdezz egyszer**, és várd meg a választ:

   <!-- INCLUDE:lang/run-tests.md#kategoria-kerdes -->

   A megadott kategória a `**<field:f_test_categories>:**` szótár egyik eleme kell legyen. Ha nem az, sorold fel a deklarált kategóriákat, és kérdezz újra — **ne futtass** nem deklarált kategóriát.

---

## A futás menete

1. **A kategória sorainak kiválasztása.** A futtatási tábla azon sorai, amelyek `<field:f_test_category>` cellája a kért kategória, és amelyek `<field:f_environment>` cellája a kért környezetnek felel meg. Ha a kategóriához a kért környezetben nincs sor, azt egy sorban jelezd, és **ne futtass** másik környezetet helyette.

2. **`remote` cél: a probe ELŐBB fut (EV4).** A sor `Előfeltétel` cellája tartalmazza az elérhetőségi probe-ot. Ezt a `run-tests.py` magától lefuttatja, de ha a probe bukik, a kategória `FAIL` lesz — ilyenkor **ne futtasd újra vakon**: a záró üzenetben mondd ki, hogy a cél nem érhető el, és a teszt-eredmény ezért nem értelmezhető.

3. **Az időbélyeg és a mappa (KT5, D11).** Képezz **UTC** időbélyeget `YYYY-MM-DDTHH-MMZ` alakban (rendezhető, kettőspont nélkül — Windowson is érvényes mappanév), és ebből a kör-mappát:

   ```
   test-runs/<kategória>/<YYYY-MM-DDTHH-MMZ>/<env>/
   ```

   Az `<env>` szegmens értéke pontosan `local` vagy `remote` — **nyelvfüggetlen literál** (EV8), ugyanaz, amit a teszt-leltár `<field:f_environment>` mezője használ.

4. **A futtató hívása.** A `--table-source conventions` mondja meg a szkriptnek, hogy a táblát a `conventions.md`-ből olvassa (a `plan.md` pozicionális argumentum ilyenkor elhagyható):

   <!-- INCLUDE:shared/python-cmd.md -->

   ```bash
   python3 <platform-scripts-mappa>/run-tests.py \
     --table-source conventions \
     --conventions conventions.md \
     --round-dir test-runs/<kategória>/<YYYY-MM-DDTHH-MMZ>/<env> \
     --only <kategória>
   ```

   A `--json` alapértéke a kör-mappa `results.json`-ja — ezt **ne írd át**. A szkript a `results.json`-be `"cycle": null`-t ír, mert az útvonal a `test-runs/` alatt van (KT6/a).

5. **Kilépő kódok — mit jelentenek itt:** `0` = minden futtatott kategória zöld · `1` = legalább egy kategória bukott (vagy 0 tesztet futtatott — TR2) · `2` = nincs tábla vagy ismeretlen kategória → **STOP**, a `conventions.md` pótlásával · `3` = helyőrző-hiba a táblában → **STOP**, a `conventions.md` javítandó · `4` = a tábla környezet-hibás: nem-lokális kategória lokális célra mutat (EV5) → **NEM futtatható**, mert a zöld eredmény ilyenkor nem a telepített komponensről szólna.

6. **Leltár-join (KT5).** Ha a projektben létezik a `docs-generated/test-description.md` teszt-leltár, a futás eredményét **tételenként** is helyezd el: a kör-mappán belül `<TL-NNN>/` alkönyvtárba az adott tételhez tartozó riport-artefaktumot. **Ez a leltár második haszna**: egy központi futás eredménye tételenként visszakereshető. Ha egy futtatott teszt **nem azonosítható** `TL-NNN`-hez, az `unmapped/<teszt-név>/` alá kerül, és a záró üzenetben jelzed — ez az `LD5` kapu hiányát jelzi, tehát a következő `08-doc-sync` teendője. **A leltárhoz magához NE nyúlj** (a gazdája a `08`, LD1).

7. **`test-runs/latest.json` frissítése.** Kategóriánként az **utolsó** futás útvonala és összegzése. A fájl a `test-runs/` gyökerében áll, és **fájl, nem szimlink** (D11 — a szimlink Windowson külön jogot igényel):

   ```json
   <!-- INCLUDE:lang/run-tests.md#latest-json-vaz -->
   ```

   Csak a most futtatott kategória kulcsát írd át; a többi kategória bejegyzését **hagyd érintetlenül**.

---

## Megtartás és takarítás (D12)

- A `test-runs/` **soha nem takarít magától.** A keret takarítási biztonsági szabálya itt is él: **csak az aktuális futás által létrehozott elem** törölhető.
- A záró üzenetben **írd ki a `test-runs/` mappa teljes méretét** (pl. `du -sh test-runs/`).
- **Ritkítást csak explicit kérésre ajánlj**, és akkor is tételesen: melyik kategória melyik időbélyegű futásait törölnéd, és mennyi helyet szabadít fel. Kérdés nélkül **egyetlen korábbi futást sem törölhetsz**.
- A mappa **gitignore-olt** (KT7): az eredmények gépfüggőek és újragenerálhatók, ezért nem verziókezeljük. Ha a `.gitignore`-ból hiányzik a `test-runs/` bejegyzés, azt **egy sorban jelezd** — a felvétele a `00-init-project` dolga, ne írj bele magadtól.

---

## A bizonyíték-tűzfal (D8) — kimondva

<!-- INCLUDE:lang/run-tests.md#tuzfal-figyelmeztetes -->

**Miért:** a keret bizonyíték-logikája `DoD-NN`/`TS-NN` joinra, TR7 frissességre és RUN1 kör-lefedettségre épül — egy cikluson kívüli futásnak **nincs mihez joinolnia**. Enélkül a legkézenfekvőbb rövidítés az lenne, hogy lefuttatjuk a központi szvitet, és ráállítjuk a `dod-check.py`-t: a ciklus zöld lenne anélkül, hogy a ciklus tesztjei lefutottak volna.

---

## Záró visszajelzés

A közös blokk PE1 szakasza (fázishatár + a következő fázis parancsa) itt **nem értelmezett**: ez nem fázis, nincs „következő fázis". A parancs a záró üzenettel véget ér:

<!-- INCLUDE:lang/run-tests.md#zaro-uzenet -->

> **A `<status:skipped>` NEM zöld (SK1).** A kihagyott teszteket **tételesen** sorold fel — egy „minden zöld" összefoglaló, ami mögött húsz kihagyott teszt áll, rosszabb, mint a nyílt bukás.

---

## Megállási szabályok

1. **Nincs `## <sec:cv_test_execution>` szekció** (Előfeltétel 2.) → STOP, a `/bs-init-project` felé irányítva.
2. **Nem deklarált kategóriát kértek** → sorold fel a deklaráltakat, és kérdezz újra. Ne futtass helyette „hasonlót".
3. **A szkript `2`, `3` vagy `4` kilépő kódot ad** → STOP, a szkript kimenetével. A `4` (EV5 környezet-hiba) esetén **különösen**: a zöld eredmény ilyenkor nem a telepített komponensről szólna.
4. **A felhasználó ciklus-bizonyítékként akarja használni az eredményt** → mondd ki egyszer, hogy a `07` kapui ezt visszautasítják, és irányítsd a `/bs-validate` felé. Ne kerüld meg a kaput, és ne másold át a fájlokat egy ciklus `test-report/` mappájába.

---

## Amit NE tegyél

- **Ne írj a ciklus `test-report/` mappájába** és ne másolj oda semmit a `test-runs/`-ból (D8).
- **Ne nyúlj a ciklus státusz-láncához** (`spec.md` / `plan.md` / `tasks.md`) és a `06`/`07`/`08`/`09` artefaktumaihoz.
- **Ne írd a `docs-generated/test-description.md` teszt-leltárat** — a gazdája a `08-doc-sync` (LD1). A `TL-NNN`-hez nem illeszthető tesztet csak **jelzed**.
- **Ne szerkeszd a `conventions.md`-t** a felhasználó explicit megerősítése nélkül, és akkor is **kizárólag** a `## <sec:cv_test_execution>` szekciót.
- **Ne találgass parancsot.** Ha a tábla egy kategóriához nem ad parancsot, az a `conventions.md` hiánya — kérdés, nem improvizáció.
- **Ne törölj korábbi futást** kérdés nélkül (D12).
