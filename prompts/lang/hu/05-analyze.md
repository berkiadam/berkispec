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

**Státusz:** IN_PROGRESS | PASS | FAIL
**Futás:** YYYY-MM-DD HH:MM
**Aktuális lépés:** <mit csinál most a fázis — pl. „iter 2/3 · a plan-fixer az AF-03, AN-01 tételeken dolgozik", vagy „lezárva">
**Hurok:** <iterációk száma> / <max X> (PASS | feladva)
**Validált alap:** `<fő branch neve>@<SHA>` · ciklus ág: `<branch>@<SHA>` (BR1: `behozva` | `nem volt szükséges`)

## Összefoglaló

_Egy-két mondat: konzisztens-e a négyes, vagy hol van a baj, és hogyan zárult a hurok._

## Javítandó tételek (AR1)

_Ez a lista a diagnózis után **azonnal** elkészül, még az első javítás előtt, és a hurok minden
lépésénél frissül — ez a felhasználó ablaka a fázisra. Egy tétel = egy pipálható sor, alatta
emberi nyelvű magyarázat. Tételt utólag **nem törlünk**: a megoldott tétel `[x]`-szel marad, ez az
audit-nyom. Az `analyze-slices/` mappa a diagnoszta-körök **bemenete** (gitignore-olt szeletek,
a tervezési dokumentumok szó szerinti kimetszései), nem eredmény — hogy „mi a baj", kizárólag itt
olvasható._

### Must Fix
- [ ] **AF-01** · <kategória> · `fájl:hely`
      **Mi a baj:** <egy-két mondat emberi nyelven: mit állít most a dokumentum, és miért hibás — a kategória neve önmagában nem magyarázat>
      **Miért blokkol:** <mi romolhat el az implementációban, ha így marad>
      **Célfázis:** <02-spec | 03-plan | 04-tasks>
      **Állapot:** nyitott | javítás alatt (iter <n>) | kérdés (<FÁZIS>/K<nn>) | megoldva (iter <n>) | elvetve — <indoklás>

### Suggestions
- <kategória> — <leírás>

## Végrehajthatósági leltár (6. kategória)

_Az `analyzer-exec` kör kimenetéből átvéve; a `(kapu)` jelölésű mezők a mechanikus kapu eredményéből. **Kötelező szekció** — ha hiányzik, a PASS nem fogadható el._

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
1. _ha az `s2-coverage` kör egy `✓` sorra **tartalmi** hiányt jelentett (`Érintett DoD-sorok`), írd át `✗`-re, és a `Megjegyzés` oszlopba a `Must Fix` rövid hivatkozását;_
2. _ugyanez, ha az `analyzer-exec` kör jelezte, hogy a sor taskja **nem fut le** (végrehajthatósági `Must Fix`)._

_**Mikor (D12):** a végleges tábla a **konvergáló (utolsó, `Must Fix` nélküli) kör** kapu-kimenetéből kerül a riportba, egyszer. Ha a hurok `max X`-nél feladja, az utolsó rendelkezésre álló kapu-kimenetet illeszd be, és jelöld: „(feladáskori állapot)"._

| DoD | Plan szekció (`[P-…]`) | Task(ok) | Lefedve | Megjegyzés |
|---|---|---|---|---|
| `DoD-01` | `[P-CONFIG]` | T001, T002 | ✓ / ✗ | <a tartalmi/végrehajthatósági Must Fix hivatkozása, ha ✗> |

**`DoD-NN`-en túli követelmények** (az `s2-coverage` kör 5. kategóriájából — a generált mátrix ezeket nem látja):
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
- **Nyitott tételek:** <AF-NN / AX-NN azonosítók>
- **Fennmaradt tételek (TS):** <mely azonosítók jöttek vissza „NEM oldódott meg"-ként, és hányadik egymást követő körben — a 2. iterációtól; vagy „nincs">
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
