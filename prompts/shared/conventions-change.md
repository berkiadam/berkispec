<!-- Forrás-jegyzet: mikor és hogyan módosíthat egy CIKLUS a projekt-szintű
     conventions.md-t, és mi mozog vele együtt (GC1). A 03 skill és a 03 minőségi
     kapuja (tehát a plan-fixer is) beemeli. Egy helyen szerkeszd. -->
**Kapu-konfiguráció együtt mozog a struktúrával (GC1).**

A `conventions.md` a **projekt** szintű igazságforrás, és a `00-init-project` a tulajdonosa — de több **determinisztikus kapu is ebből olvas**, ezért ha egy ciklus olyat változtat, amit egy kapu itt keres, a `conventions.md`-t **ugyanabban a ciklusban** hozzá kell igazítani. Ellenkező esetben a kapu a régi helyen/értékkel keres, és a `07-validate` bukik — a hiba két fázissal később, a validálásban derül ki.

**Amit kapu olvas a `conventions.md`-ből** (ha a ciklus ezekhez hozzáér, a szekció frissítése a ciklus része):

| `conventions.md` szekció | Ki olvassa | Mi romlik el, ha nem mozog vele |
|---|---|---|
| `## Teszt-riportolás` (artefaktumok, útvonal-alap, riport-parancsok) | `report-gate-check.py` (TR3, 07) | a kapu a régi útvonalon keresi a riportot → FAIL |
| `## Sonar` (projekt-kulcs, küszöbök, riport helye) | `sonar-gate.py` (07) | Quality Gate-ellenőrzés hibás projektre/küszöbre fut |
| `## Teszt eszközök` / teszt-parancsok | `run-tests.py`, `test-runner` (07) | nem létező parancsot futtat |
| `## Merge stratégia` | `09-merge` | a merge-ág rossz úton próbálkozik |
| `## Portok`, `## Env változók` | 06/07 futtatás | a teszt más konfigurációval fut, mint a fejlesztés |

**Hogyan módosít egy ciklus konvenciót — a négy feltétel:**
1. **Explicit döntés,** nem melléktermék: a `spec.md`-ben legyen rá `DoD-NN` pont (vagy legalább a plan `Cél és megközelítés` szekciójában kimondott döntés), hogy a ciklus a konvenciót is megváltoztatja.
2. **A plan tervezi:** a `conventions.md` érintett szekciója szerepel a `Tervezett módosítások`-ban, a **konkrét új tartalommal** (nem „frissítjük a konvenciókat" jelleggel).
3. **Van rá task:** a `tasks.md`-ben külön task szerkeszti a `conventions.md`-t. A marker `[GREEN]` (repo-fájlt módosít), **nem** `[OPS]`.
4. **A kapu ugyanebben a ciklusban újra fut:** a 07 TELJES köre a frissített `conventions.md`-vel validál — így a változás bizonyítottan működik, nem a következő ciklusra hagyott adósság.

> **Mikor NEM a ciklus dolga:** ha a kérdés az, hogy a **projekt-konvenció maga** helyes-e (más teszt-eszköz, más merge-stratégia, más naming), az **emberi döntés** → a `05-analyze` súlyos konvenció-ütközés ága a `00`-ra irányít. A GC1 arról szól, amikor a döntés **már megvan**, és a ciklus végrehajtja: azt nem kell a `00`-ba visszatolni.

> **A `specs/test-conventions.md` NEM helyettesíti (TC1/c):** riport-artefaktum, útvonal-alap és riport-parancs → `conventions.md` (ezt olvassa a TR3 kapu); teszt-recept és koordináta → `test-conventions.md` (a 08-doc-sync tartja karban). Ha a ciklus a riport-struktúrát alakítja át, **a `test-conventions.md` frissítése önmagában nem elég.**
