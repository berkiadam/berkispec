<!--
  KÖZÖS leírás a PÁRHUZAMOS CIKLUS-MUNKÁRÓL (worktree-ablak, PW1/PW2 — BD16).
  Ez NEM önálló skill/agent, hanem megosztott szövegblokk, amelyet a telepítő
  (install-helper.py) build-time INLINE beágyaz a hivatkozó skill telepített
  változatába (a `<!-- INCLUDE:shared/parallel-cycles.md -->` marker helyére).
  Hivatkozik rá: 01-add-cycles (az ablak ismertetése), 06-implement (a kapu).
  Nincs frontmattere: a tartalma szó szerint bemásolódik. Itt szerkeszd.
-->

### Párhuzamos ciklusok — a tervezési ablak (PW1/PW2)

Két ciklus **párhuzamosan is haladhat**, külön `git worktree`-ben, külön agens-munkamenetben (pl. amíg a `cycle-26` implementálódik, a `cycle-27` spec-je készül). Ennek **kemény határa van**:

| Fázis | Párhuzamosan futhat? | Miért |
|---|---|---|
| `01` … `05` (ciklus, spec, plan, tasks, analyze) | **Igen** | Csak a `specs/cycle-NN-<name>/` mappát írják — nincs átfedés a másik ág fájljaival, és nincs futtatási erőforrás (port, dev deploy, registry-tag, közös DB/IdP). |
| `06` … `09` (implementálás, validálás, doc-sync, merge) | **Nem** | A `06` a forrásfát írja (valódi merge-konfliktus), a `07` közös futtatási erőforrást fogyaszt, a `08` garantáltan ütköző fájlokat ír (`docs-generated/`, `specs/test-conventions.md`), a `09` a `main`-t igényli. |

**PW1 — az implementációs sáv egyszálú.** Egyszerre **egy** ciklus lehet a `06`–`09` szakaszban. A többi ciklus eddig eljuthat, de ott megvárja a sorát.

**PW2 — határátlépés a `06` előtt (kötelező sorrend).** Az `05` zöld eredménye a **régi** `main`-en készült: a plan és a tasks arra a kódbázisra tervezett, amiben a másik ciklus változásai még nem voltak benne. Ezért a `06` megkezdése előtt:

1. **A másik ciklus legyen merge-elve** (a `09` lefutott, a worktree-je eltűnt). Amíg nincs, a `06` nem kezdődhet el.
2. **Visszaköltözés a fő worktree-be** (a `06`–`09` ott fut, hogy a `09` `main`-re váltása működjön):
   ```bash
   git worktree remove ../<ciklus-worktree>       # a ciklus-worktree megszűnik
   git switch feature/cycle-NN-<cycle-name>       # a FŐ worktree-ben, ahol eddig a main/másik ág volt
   ```
   Ha a `git worktree remove` commitálatlan tartalom miatt megtagadja: **ne** használj `--force`-ot — commitolj a ciklus ágán, és próbáld újra.
3. **Az `05-analyze` újrafuttatása a friss alapon:**
   ```text
   /bs-analyze input: @specs/cycle-NN-<cycle-name>
   ```
   Az `05` **maga hozza be a friss fő branch-et** a ciklus ágába (BR1: rebase, ha a branch nincs pusholva; merge, ha PR nyitva van rá), és utána validál — így a horgonyok (`path:sor`), a fájllétezés és a plan↔kód konzisztencia a másik ciklus változásai után is igazolt. Ha az analyze `FAIL`, a javítás a `03`/`04` dolga — a `06` csak `PASS` után nyílik.

**Worktree létrehozása (a tervezési ablakhoz).** A `main`-re **nem** kell átállni — az a fő worktree-ben marad kicsekkolva:
```bash
git fetch origin
git worktree add ../<projekt>-cNN -b feature/cycle-NN-<name> origin/main
```
A linked worktree a saját HEAD-jével és indexével dolgozik, tehát a két agens munkafa-ellenőrzése nem látja egymást. A másik ciklus mappája (`specs/cycle-MM-*/`) **nem is jelenik meg** a worktree-ben, amíg az nincs merge-elve — a ciklusszámozás ezért a branch-neveket scanneli (BQ2), nem az `ls specs/`-et.
