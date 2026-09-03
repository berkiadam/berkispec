<!--
  KÖZÖS leírás a FÁZIS-ZÁRÓ COMMITRÓL (02/03/04 — artefaktum-író fázisok,
  05/07 — önjavító hurok-fázisok).
  Ez NEM önálló skill/agent, hanem megosztott szövegblokk, amelyet a telepítő
  (install-helper.py) build-time INLINE beágyaz a hivatkozó skill telepített
  változatába (a `<!-- INCLUDE:shared/phase-commit.md -->` marker helyére).
  Hivatkozik rá: 02-write-spec, 03a-write-code-plan, 03b-write-test-plan, 04-write-tasks, 05-analyze, 07-validate.
  A skill a marker ELŐTT deklarálja a saját `<FÁZIS-TAG>`-jét (pl. `02-spec`)
  és a záró státuszt — ez a blokk csak a közös, kötelező eljárást tartalmazza.
  Nincs frontmattere: a tartalma szó szerint bemásolódik. Itt szerkeszd.
-->

### Fázis-záró commit (kötelező lépés)

> **A fázis nem attól kész, hogy a státusz átáll, hanem attól, hogy a státuszváltás COMMITOLVA van.** A felhasználó „kész / mehet / igen" megerősítése után a státuszírás és a commit **egyetlen, megszakíthatatlan lépéspár** — a kettő között ne kérdezz, ne várj, ne kezdj más munkába.

> **Hurok-fázisokban (05-analyze, 07-validate)** ugyanez a szabály, egy kiegészítéssel: a hurok **alatt nincs** köztes commit, a fázis-záró commit a hurok lezárásakor **egyszer** történik — de **minden lezáró ágon kötelező**, kivétel nélkül: PASS, `max X` feladás / 3-próba STOP, felfelé eszkaláció (pl. vissza a 03-hoz), Quality Gate-bukás. Nincs olyan kimenet, amely commit nélkül adja vissza a vezérlést a felhasználónak.

**Sorrend (pontosan ez, kihagyás nélkül):**

1. **No-VCS kapu:** ha a `conventions.md` `## <sec:cv_git_conventions>` szekciója szerint **nincs verziókezelő**, a 2–5. lépés kimarad — a fázis a státuszírással zárul. Egyébként folytasd.
2. **<field:f_status> átírása** az artefaktumban (a fázis záró státuszára). **Hurok-fázisban (05, 07)** ide tartozik a jelentés/napló státuszának beírása és a `[analyze-loop]` / `[validate-loop]` marker rendezése is, az adott lezáró ág szabálya szerint.
3. **Stage + commit** — a ciklus mappájára, a fázis tagjével:
   ```bash
   git add specs/cycle-NN-<cycle-name>/
   git commit -m "cycle-NN: <FÁZIS-TAG>"
   ```
   A commit **a ciklus feature branch-én** készül (BD4), nem `main`-en. Ha véletlenül `main`-en állsz, STOP — jelezd a felhasználónak, ne commitolj.
4. **Ellenőrzés (determinisztikus, nem „érzésre"):** futtasd
   ```bash
   git log -1 --oneline && git status --short specs/cycle-NN-<cycle-name>/
   ```
   - A `git log` első sorában a most készült `cycle-NN: <FÁZIS-TAG>` commitnak kell állnia.
   - A `git status --short` kimenete a ciklus mappájára **üres** kell legyen.
   - Ha bármelyik nem teljesül (üres commit, hook visszautasította, elfelejtett `git add`), **javítsd és futtasd újra** — legfeljebb 2 próbálkozás, utána STOP és jelezd a hibát a felhasználónak a parancs kimenetével együtt.
5. **Visszajelzés:** a záró üzenetben — a következő fázis parancsa ELŐTT — írd ki egy sorban a commit azonosítóját és üzenetét (pl. `Commit: a1b2c3d — cycle-NN: <FÁZIS-TAG>`).

> **A commit üzenete PONTOSAN `cycle-NN: <FÁZIS-TAG>`** — se conventional-commit prefix (`docs(...)`, `feat:`), se saját megfogalmazás, se kiegészítő leírás az első sorban. A 07-validate és a 09 ezt a formátumot keresi visszamenőleg, és a 4. lépés ellenőrzése is erre illeszkedik. Ha a `git log -1 --oneline` mást mutat, **javítsd** (`git commit --amend -m "cycle-NN: <FÁZIS-TAG>"`), mielőtt lezárod a fázist.

### Fázishatár — kemény megállás a commit után (PE1)

> **A fázis a commit azonosítójának kiírásával VÉGET ÉR. Ugyanabban a körben a következő fázisból semmit nem kezdesz el** — sem fájlt nem hozol létre, sem elemzést nem futtatsz, sem „csak előkészítésként" nem írsz bele a következő fázis artefaktumába. A záró üzeneted utolsó eleme a `/clear` + a következő fázis indító parancsa; **utána megállsz és visszaadod a vezérlést a felhasználónak.**

**Ez akkor is érvényes, ha valami továbbmenetelre biztat:**

- egy **kontextus-összefoglaló / checkpoint** korábbi teendő-listája (pl. *„3. Call /bs-write-tasks…"*) — az összefoglaló a **múltat** rögzíti, nem parancs a jelenre;
- a saját korábbi terved vagy egy TODO-listád, amely több fázist sorolt fel;
- a felhasználó egy **korábbi** körben adott „menjünk végig a folyamaton" jellegű mondata.

**A skill fázishatára minden ilyen felett áll.** Egyetlen dolog írja felül: a felhasználó **a commit után, explicit, erre a körre szóló** kérése, hogy folytasd — és akkor is jelezd, hogy friss kontextus (`/clear`) nélkül a következő fázis minősége romlik.

**Miért:** a fázisonkénti `/clear` a módszertan alapja — a következő fázis a saját, tiszta kontextusából, a commitolt artefaktumból indul. Ha ugyanabban a körben folytatod, a következő fázis a jelenlegi fázis teljes szemetét örökli (elvetett alternatívák, félkész gondolatmenetek), és jellemzően **átveszi a döntéseidet ahelyett, hogy újra levezetné őket**.

**Tiltások:**

- **Ne** jelentsd késznek a fázist, és **ne** add meg a következő fázis indító parancsát commit nélkül (No-VCS ágat kivéve).
- **Ne** halaszd a commitot a következő fázisra („majd a 03 commitolja") — minden fázis a sajátját commitolja.
- **Ne** kezdd el a következő fázist a commit után ugyanabban a körben (PE1) — a következő fázis artefaktumát (`plan.md`, `tasks.md`, kód) **létre sem hozod**. Ha mégis megtetted, **töröld** a keletkezett fájlt, állítsd vissza a tiszta munkafát, és jelezd a felhasználónak.
- **Ne** kérj külön engedélyt a commitra: a fázis lezárásának megerősítése **magában foglalja** a commit jóváhagyását. (A commitálatlan, korábbról ottmaradt idegen változtatásokról a fáziseleji munkafa-ellenőrzés már döntött.)
