<!--
  KÖZÖS leírás a FÁZIS-ZÁRÓ COMMITRÓL (02/03/04 — artefaktum-író fázisok,
  05/07 — önjavító hurok-fázisok).
  Ez NEM önálló skill/agent, hanem megosztott szövegblokk, amelyet a telepítő
  (install-helper.py) build-time INLINE beágyaz a hivatkozó skill telepített
  változatába (a `<!-- INCLUDE:shared/phase-commit.md -->` marker helyére).
  Hivatkozik rá: 02-write-spec, 03-write-plan, 04-write-tasks, 05-analyze, 07-validate.
  A skill a marker ELŐTT deklarálja a saját `<FÁZIS-TAG>`-jét (pl. `02-spec`)
  és a záró státuszt — ez a blokk csak a közös, kötelező eljárást tartalmazza.
  Nincs frontmattere: a tartalma szó szerint bemásolódik. Itt szerkeszd.
-->

### Fázis-záró commit (kötelező lépés)

> **A fázis nem attól kész, hogy a státusz átáll, hanem attól, hogy a státuszváltás COMMITOLVA van.** A felhasználó „kész / mehet / igen" megerősítése után a státuszírás és a commit **egyetlen, megszakíthatatlan lépéspár** — a kettő között ne kérdezz, ne várj, ne kezdj más munkába.

> **Hurok-fázisokban (05-analyze, 07-validate)** ugyanez a szabály, egy kiegészítéssel: a hurok **alatt nincs** köztes commit, a fázis-záró commit a hurok lezárásakor **egyszer** történik — de **minden lezáró ágon kötelező**, kivétel nélkül: PASS, `max X` feladás / 3-próba STOP, felfelé eszkaláció (pl. vissza a 03-hoz), Quality Gate-bukás. Nincs olyan kimenet, amely commit nélkül adja vissza a vezérlést a felhasználónak.

**Sorrend (pontosan ez, kihagyás nélkül):**

1. **No-VCS kapu:** ha a `conventions.md` `## Git és branching konvenciók` szekciója szerint **nincs verziókezelő**, a 2–5. lépés kimarad — a fázis a státuszírással zárul. Egyébként folytasd.
2. **Státusz átírása** az artefaktumban (a fázis záró státuszára). **Hurok-fázisban (05, 07)** ide tartozik a jelentés/napló státuszának beírása és a `[analyze-loop]` / `[validate-loop]` marker rendezése is, az adott lezáró ág szabálya szerint.
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

**Tiltások:**

- **Ne** jelentsd késznek a fázist, és **ne** add meg a következő fázis indító parancsát commit nélkül (No-VCS ágat kivéve).
- **Ne** halaszd a commitot a következő fázisra („majd a 03 commitolja") — minden fázis a sajátját commitolja.
- **Ne** kérj külön engedélyt a commitra: a fázis lezárásának megerősítése **magában foglalja** a commit jóváhagyását. (A commitálatlan, korábbról ottmaradt idegen változtatásokról a fáziseleji munkafa-ellenőrzés már döntött.)
