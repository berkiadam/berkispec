<!--
  A `05-analyze` PROJEKT-NYELVI blokkjai (9.4 kiemelés).
  Ezt a fájlt a telepítő build-time emeli be az INCLUDE markerek helyére, a
  választott PROJEKT-nyelv (`PROJECT_LANG`) szerint; a marker alakja
  `lang/05-analyze.md#<horgony>`.
  A blokkok SZÓ SZERINT kerültek ide — ne fogalmazd át, ne egységesítsd.
  Az ANCHOR sorok NEM részei a beemelt szövegnek, csak határolók (8.9).
  FIGYELEM: ebbe a vezető jegyzetbe ne kerüljön komment-lezáró szekvencia.
-->

<!-- ANCHOR:analyze-report-struktura -->
# Cycle NN: <cím> — Analyze report

**Státusz:** PASS | FAIL
**Futás:** YYYY-MM-DD HH:MM
**Hurok:** <iterációk száma> / <max X> (PASS | feladva)
**Validált alap:** `<fő branch neve>@<SHA>` · ciklus ág: `<branch>@<SHA>` (BR1: `behozva` | `nem volt szükséges`)

## Összefoglaló

_Egy-két mondat: konzisztens-e a négyes, vagy hol van a baj, és hogyan zárult a hurok._

## Megállapítások (utolsó analyze)

### Must Fix
- [ ] <kategória> — <leírás> → célfázis: <fázis> (`fájl:hely` ha van)

### Suggestions
- <kategória> — <leírás>

## Végrehajthatósági leltár (6. kategória)

_Az `analyzer` subagent kimenetéből átvéve; a `(kapu)` jelölésű mezők a mechanikus kapu eredményéből. **Kötelező szekció** — ha hiányzik, a PASS nem fogadható el._

**Futtatott artefaktumok (kapu, A1):** <rendben / HIÁNYZIK: ...>
**Prózában ígért tesztek:** <ígéret → teszteset + task / HIÁNYZIK>
**Artefaktum-tulajdon:** <rendben / a planben szerepel: ...>
**Státusz-frissítő task (kapu, T3):** <nincs / Tnnn>
**Marker-helyesség (kapu, T1/T2):** <rendben / téves [OPS]: ...>
**Destruktív műveletek:** <jóváhagyás + immutable azonosító + rollback megvan / hiányzik: ...>
**Horgony-feloldás (kapu A2 + szimbólum-ítélet):** <feloldható / nem oldható fel: ...>
**Artefaktum-hang (kapu A3 + címzett-ítélet):** <rendben / skill-hangú meta-utasítás maradt: ...>

## Lefedettségi mátrix (követelmény ↔ task)

_**Honnan jön (K/AG4):** ezt a mátrixot a **mechanikus kapu generálja** (`## Lefedettségi mátrix (generált)` blokk), és te **szó szerint** fűzöd ide — nem az LLM vezeti le újra. A `Lefedve (gépi)` oszlop kizárólag a `DoD-NN → [P-…] → task` **lánc meglétét** jelenti._
_**Két javítást te végzel a beillesztett táblán:**_
1. _ha az `analyzer` egy `✓` sorra **tartalmi** hiányt jelentett (`Érintett DoD-sorok`), írd át `✗`-re, és a `Megjegyzés` oszlopba a `Must Fix` rövid hivatkozását;_
2. _ugyanez, ha az `analyzer-exec` jelezte, hogy a sor taskja **nem fut le** (végrehajthatósági `Must Fix`)._

_**Mikor (D12):** a végleges tábla a **konvergáló (utolsó, `Must Fix` nélküli) kör** kapu-kimenetéből kerül a riportba, egyszer. Ha a hurok `max X`-nél feladja, az utolsó rendelkezésre álló kapu-kimenetet illeszd be, és jelöld: „(feladáskori állapot)"._

| DoD | Plan szekció (`[P-…]`) | Task(ok) | Lefedve | Megjegyzés |
|---|---|---|---|---|
| `DoD-01` | `[P-CONFIG]` | T001, T002 | ✓ / ✗ | <a tartalmi/végrehajthatósági Must Fix hivatkozása, ha ✗> |

**`DoD-NN`-en túli követelmények** (az `analyzer` 5. kategóriájából — a generált mátrix ezeket nem látja):
- <spec-követelmény task nélkül> _(vagy: „nincs ilyen")_

## Plan-szekció ↔ task (PID1)

_A plan MINDEN `[P-…]` azonosítója szerepel; a „nincs task" sor indoklással érvényes. **Ezt a táblát is a mechanikus kapu generálja** (`## Plan-szekció ↔ task (generált — PID1)`) — szó szerint fűzd ide._

| Plan szekció (ID) | Hivatkozó taskok | Rendben |
|---|---|---|
| `[P-CONFIG]` | T001, T002, T003 | ✓ |
| `[P-XYZ]` | — (a `Plan-lefedettség` tábla indokolja) | ✓ / ✗ |

_Eltérések, amiket itt kell kimutatni: ID task nélkül · task nem létező ID-ra · sorszámos hivatkozás `[P-…]` helyett · végrehajtható plan-szekció ID nélkül._

## Hurok-napló

_Iterációnkénti audit-nyom — a megszakítás-utáni folytatás horgonya._

### Iteráció 1
- **FAIL kategóriák:** <kategóriák>
- **Célfázis:** <fázis> (legkorábbi érintett)
- **Fix:** <a fixer-subagent összefoglalója egy sorban>
- **Nyitott kérdések:** <FÁZIS/Knn lista vagy „nincs">
- **Re-deriválás:** <mely downstream fázisok hangolódtak újra>
- **Eredmény:** PASS | FAIL → következő iteráció

### Iteráció 2
...

<!-- ANCHOR:zaro-uzenet -->
   > *"Az analízis konzisztensnek találta a tervezési dokumentumokat. Folytathatjuk a 6. lépéssel (implement). Az új fázis megkezdése előtt mindenképpen futtass egy `/clear` parancsot a kontextus kiürítéséhez, majd használd ezt a parancsot:*
   > ```
   > /bs-implement input: @specs/cycle-NN-<cycle-name>/tasks.md
   > ```"*
