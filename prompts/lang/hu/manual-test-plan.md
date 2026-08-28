<!--
  A `manual-test-plan` (bs-manual-test-plan segédparancs) PROJEKT-NYELVI blokkjai
  (9.4 kiemelés, MT12).
  Ezt a fájlt a telepítő build-time emeli be az INCLUDE markerek helyére, a
  választott PROJEKT-nyelv (`PROJECT_LANG`) szerint; a marker alakja
  `lang/manual-test-plan.md#<horgony>`.
  A blokkok SZÓ SZERINT kerültek ide — ne fogalmazd át, ne egységesítsd.
  Az ANCHOR sorok NEM részei a beemelt szövegnek, csak határolók. Azért
  HTML-komment és nem `##` címsor a határoló, mert a dokumentum-sablon maga is
  tele van `##` címsorral (8.9).
  FIGYELEM: ebbe a vezető jegyzetbe ne kerüljön komment-lezáró szekvencia, és a
  fájlba INCLUDE marker sem (8.5).
-->

<!-- ANCHOR:dokumentum-sablon -->

# Kézi tesztterv — cycle-NN-<cycle-name>

**<field:f_status>:** <status:mtp_planned> | <status:mtp_as_built>
**<field:f_mode>:** <a módválasztás indoka egy sorban — pl. „tasks.md = <status:ready_for_validate>">
**Forrás:** plan.md <sec:environment_coords> · spec.md <sec:definition_of_done> · conventions.md
**<field:f_last_updated>:** ÉÉÉÉ-HH-NN

> (csak <status:mtp_planned> módban) ⚠ Az implementáció még nem zárult le. A lépések a
> tervből származnak, valós kódon NEM verifikáltak — eltérés esetén a kód a mérvadó.

## 1. <sec:mt_environment>

| Komponens | Port | Health endpoint | <field:f_startup> | <field:f_shutdown> |
|---|---|---|---|---|
| ... | ... | ... | `...` | `...` |

**<field:f_prerequisite>:** hálózati és hozzáférési előfeltételek, indítási sorrend.

## 2. <sec:mt_test_data>

| Név | Érték | Hol keletkezik | <field:f_cleanup> |
|---|---|---|---|
| ... | ... | ... | ... |

Ide tartoznak a teszt-userek jelszóval, a tokenek és a beszerzésük módja, a seed rekordok,
az azonosítók és a scope-ok. TC5 titok-szabály: a dev-hatókörű érték konkrétan, a
klaszter-, registry-, VPN-, IAM- és éles credential viszont **csak pointerként** szerepel.

## 3. <sec:mt_automated_tests>

| Mit futtat | Parancs | Az eredmény helye |
|---|---|---|
| ... | `...` | `...` |

**<field:f_test_results_so_far>:** <konkrét útvonalak, vagy „még nem létezik">

## 4. <sec:mt_manual_groups>

### TG-01 — <a csoport neve>  (DoD-03, DoD-07)

**<field:f_what_we_test>:** <egy-két mondat: milyen viselkedést igazol ez a csoport>
**<field:f_prerequisite>:** <mi álljon készen a csoport előtt>

| # | <field:f_steps> | Hívás / művelet | <field:f_expected_result> |
|---|---|---|---|
| 1 | token beszerzése | `curl -s -X POST http://localhost:8080/auth/token -d '{"user":"tester"}'` | 200, a válasz `access_token` mezője nem üres |
| 2 | ... | ... | ... |

```http
POST http://localhost:8080/auth/token
Content-Type: application/json

{ "user": "tester", "password": "tester-dev" }
```

**<field:f_cleanup>:** <mit kell visszaállítani a csoport után>

### TG-02 — ...

### <sec:mt_not_manual>

| DoD-NN | Miért nem tesztelhető kézzel | Mi fedi |
|---|---|---|
| DoD-05 | ... | `...` automata teszt / Sonar kapu |

## 5. <sec:mt_coverage>

| DoD-NN | Tesztcsoport |
|---|---|
| DoD-03 | TG-01 |

## <sec:mt_changelog>

- **ÉÉÉÉ-HH-NN — <mód>:** <mit adott hozzá / mit módosított / mi avult el és miért>

<!-- ANCHOR:mod-tervezett-figyelmeztetes -->
> ⚠ **<status:mtp_planned> mód — a lépések valós kódon NEM verifikáltak.** A terv a
> `plan.md` <sec:environment_coords> szekciójából és a `spec.md` <sec:test_specification>
> szekciójából készült, az implementáció még nem zárult le. Eltérés esetén **a kód a
> mérvadó**; a validálás után futtasd újra ezt a parancsot, és a terv `<status:mtp_as_built>`
> módra frissül.

<!-- ANCHOR:analyze-kapu-stop -->
*"Nincs `PASS` állapotú analyze-riport ehhez a ciklushoz, ezért a kézi tesztterv nem
készíthető el. Ez a parancs a `plan.md` kitöltött <sec:environment_coords> szekciójára
épül — hogy az placeholder nélkül, konkrét értékekkel áll, azt az `05-analyze` mechanikus
kapuja garantálja. Futtasd le előbb az analyze fázist: `/bs-analyze input:
@specs/cycle-NN-<cycle-name>` — utána hívj újra. (Ha a ciklus az egyszerűsített
[lightweight] flow-t követi, ez a parancs nem használható: ott nincs `plan.md` és nincs
analyze fázis — a kézi tesztterv a teljes flow-hoz készült.)"*

<!-- ANCHOR:mod-bejelentes -->
*"A kézi tesztterv <mód> módban készül, mert a `tasks.md` státusza: <státusz>. Ha ez nem
jó, add meg a módot inputként (`mód: tervezett` vagy `mód: as-built`)."*

<!-- ANCHOR:ujrafutas-bejelentes -->
*"Létező kézi tesztterv frissítése — a kézi kiegészítéseket megőrzöm, a meglévő `TG-NN`
azonosítókat nem számozom újra, a változást pedig a <sec:mt_changelog> szekcióba írom."*

<!-- ANCHOR:zaro-uzenet -->
> *"A kézi tesztterv elkészült — <mód> mód.*
> - *Tesztcsoportok: <N> darab (TG-01 … TG-NN)*
> - *Lefedett DoD-pontok: <felsorolás> · nem kézzel tesztelhető: <felsorolás vagy „nincs">*
> - *Kapu: `manual-test-gate-check.py` → OK*
> - *Commit: <hash> — cycle-NN: manual-test-plan*
>
> *A terv: [manual-test-plan.md](./manual-test-plan.md)"*
