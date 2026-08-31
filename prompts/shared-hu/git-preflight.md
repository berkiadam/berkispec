<!--
  KÖZÖS git-preflight leírás a BRANCH-NYITÓ fázisokhoz (00, 01) — BD13. Ez NEM
  önálló skill/agent, hanem egy megosztott szövegblokk, amelyet a telepítő
  (install-helper.py) build-time INLINE beágyaz a hivatkozó skill telepített
  változatába (a `<!-- INCLUDE:shared/git-preflight.md -->` marker helyére).
  Csak a 00 és a 01 hivatkozik rá (ők hoznak létre branch-et); a 02–09 fázisok
  NEM — nekik a saját, rövid munkafa-ellenőrzésük elég (a 02 ezen felül a 01-ben
  létrehozott branch meglétét ellenőrzi, a 09 a merge-nél vált branch-et).
  Nincs frontmattere: a tartalma szó szerint bemásolódik. Itt szerkeszd.
-->

### Git-preflight (branch-nyitó fázis — `00` / `01`)

> Ez a leírás a **branch-nyitó** fázisokra (`00-init-project`, `01-add-cycles`) vonatkozik — ők ágaznak le `main`-ről. A `02`–`09` fázisok ezt **nem** használják.

#### No-VCS kapu (BD11) — mindig, elsőként

Olvasd ki a `conventions.md` `## <sec:cv_git_conventions>` szekciójából a verziókezelő-flaget:

- Ha ott az áll, hogy **„<status:no_vcs_flag>"**, akkor **minden git-műveletet hagyj ki** ebben a fázisban — nincs `git status`, branch-váltás/-létrehozás, `git pull`, commit. A fázis csak a nem-git teendőit végzi el (fájl/mappa létrehozás). A lenti lépéseket **átugrod**.
- Egyébként (git elérhető, a projekt git-repo) → folytasd a *Munkafa-ellenőrzéssel*.

#### Munkafa-ellenőrzés

Futtasd: `git status --short`. Ha van commitálatlan változtatás:

- Listázd ki az érintett fájlokat.
- Kérdezd meg **egy körben**: <!-- INCLUDE:lang/git-preflight.md#BD13-commit-vagy-folytas --> — várj a válaszra, majd aszerint járj el.

#### Friss, tiszta `main` (leágazás előtt)

A cél, hogy friss `main`-ről (a `conventions.md` `## <sec:cv_git_conventions>` **<field:f_main_branch>** mezője; alapból `main`) ágazz le. A tényleges `git switch -c`-t **nem** itt futtatod — azt a fázis a saját logikája szerint végzi (a `00` azonnal, a `01` a ciklusnév meghatározása UTÁN — BD5).

1. **Worktree-helyzet (PW1/PW3) — a branch-vizsgálat ELŐTT.** A tervezési ablak (`01`–`05`) párhuzamosítható külön `git worktree`-ben, ezért előbb azt kell tudni, hol állunk:

   ```bash
   git worktree list                 # melyik könyvtár melyik branch-en áll
   git rev-parse --git-common-dir    # ha nem `.git`, akkor linked worktree-ben vagyunk
   ```

   - **Egyetlen worktree van** (a common-dir `.git`) → tovább a 2. ponthoz (normál út).
   - **Linked worktree-ben vagyunk**, és a HEAD **már az aktuális ciklus branch-én** áll → ez **resume**: a worktree-t és a branch-et a felhasználó már létrehozta. `git switch -c`, `git switch` és `git pull` **tilos**, a 2. és 3. pontot **ugord át** — a leágazás már friss `origin/main`-ről történt.
   - **Linked worktree-ben vagyunk detached HEAD-del, friss `origin/main`-en** (a worktree épp ehhez a ciklushoz készült — PW3/B) → az alap már friss: a 2. és 3. pontot **ugord át**, a ciklus branch-e a BD5 szerint, a ciklusnév meghatározása után jön létre itt.
   - **Linked worktree-ben vagyunk egy idegen (másik ciklus) branch-én** → a 2. pont PW3 döntési kapuja következik, azzal a különbséggel, hogy az **A)** ág itt nem járható: a `main` a fő worktree-ben áll, ide nem lehet átváltani. Vagy a felhasználó lezárja a másik ciklust és visszaköltözik a fő worktree-be (a *Párhuzamos ciklusok* blokk PW2/2. lépése), vagy **B)** szerint nyit egy új worktree-t ehhez a ciklushoz.

   **Bármelyik linked-worktree ágon (PW4):** ellenőrizd, hogy az eszköz-mappa itt is megvan-e (`ls <platform-scripts-mappa>`). Ha hiányzik — mert a felhasználó kézzel hozta létre a worktree-t —, futtasd a pótlást a fő worktree-ből, és csak utána haladj tovább: `python3 <platform-scripts-mappa>/worktree-setup.py .` (a script a fő worktree-t magától megtalálja a közös git-mappából).

2. **Hol állunk? (BQ3 — idempotencia/resume):** `git branch --show-current`.
   - **`main`-en vagyunk** → tovább a 3. ponthoz.
   - **feature branch-en vagyunk** → hasonlítsd össze a branch nevét az **aktuális ciklus várt branch-nevével** (a `roadmap.md` folyamatban lévő ciklus-blokkjából / a ciklus mappanevéből):
     - **Egyezik** → ez egy **resume**; a branch már létezik. **Nincs teendő** — folytasd ezen a branch-en, `git switch -c`-t **NE** futtass, és **ne** figyelmeztess.
     - **Nem egyezik** → ez egy **másik, még le nem zárt ciklus** ága. **Ne** csak a `main`-re váltást kérd: ez **döntési kapu (PW3)**. Már az **első válaszodban**, **egyetlen** kérdésben ajánld fel mindkét utat, és várd meg a választ — addig ne kezdj tervezni:

       <!-- INCLUDE:lang/git-preflight.md#PW3-soros-vagy-parhuzamos -->

       - **A) Soros folytatás** — a felhasználó lezárja a jelenlegi ciklust (merge vagy PR a `## <sec:cv_merge_strategy>` szerint), majd **ő vált `main`-re** (a váltást az esetleges nyitott munka miatt ő végzi). Várj, amíg rendezi, aztán tovább a 3. ponthoz.
       - **B) Párhuzamos tervezés worktree-ben** — a másik ciklus nyitva marad, ez a fázis egy **linked worktree**-ben fut. A ciklusszám a branch-scanből (BQ2) adódik, a ciklusnév viszont még nincs meg, ezért a worktree **detached** HEAD-del jön létre friss `origin/main`-en; a branch-et a fázis később, a BD5 szerint nyitja meg benne:
         ```bash
         git fetch origin
         git worktree add --detach ../<projekt>-cNN origin/main
         python3 <platform-scripts-mappa>/worktree-setup.py ../<projekt>-cNN   # PW4
         ```
         **PW4 — az eszköz-mappák pótlása (kötelező lépés).** A worktree csak a **git által követett** fájlokat kapja meg; az agentic eszközök konfigurációja (`.claude/`, `.agents/`, `.codex/`, `.cursor/`, `.github/`, `AGENTS.md`, `CLAUDE.md`, …) projektenként lehet gitignore-olt — ilyenkor az új worktree-ben **nincsenek meg a `bs-*` skillek, a subagentek és a kapu-scriptek**, és az ott induló ágens vakon áll. A `worktree-setup.py` ezt pótolja: a fő worktree gyökeréből a **hiányzó** fájlokat másolja át (meglévőt soha nem ír felül és nem töröl, tehát idempotens). Ha valami mást is át kell hozni, `--extra <útvonal>` kapcsolóval bővíthető.

         **PW5 — átköltözés és STOP (a fázis itt véget ér).** Az ágens a jelenlegi mappához van kötve: a worktree létrehozása után ebben a munkamenetben **NE tervezz tovább**, ne hozz létre ciklusmappát és ne írj a roadmap-be. Add ki a lenti üzenetet — a **worktree ABSZOLÚT útvonalával** és az éppen használt eszköz **indítóparancsával** kitöltve —, majd **állj meg**:

         <!-- INCLUDE:lang/git-preflight.md#PW3-worktree-ujrainditas -->

         Az újraindítás után a fázis a **worktree-ben** fut le elölről: ott a `main`-re váltás elmarad (az a fő worktree-ben marad kicsekkolva), és a 3. pontot átugrod.

       **Melyiket ajánld:** ha a másik ciklus még **nem zárható le** (nyitott munka, folyamatban lévő implementáció, `06`–`09` szakasz), a **B)** az ajánlott — a párhuzamosság határa a *Párhuzamos ciklusok* blokkban van leírva (a `06` nem indul, amíg egy másik ciklus worktree-je nyitva van, PW1/PW2). Ha a másik ciklus gyakorlatilag kész, az **A)** az egyszerűbb.

3. **Friss és tiszta `main` (BQ4):** ha `main`-en vagyunk, a leágazás **előtt**:
   - Ellenőrizd, van-e commitálatlan tartalom **vagy** nem-pusholt lokális commit (pl. `git status --short` + `git status -sb` ahead-jelzés, ill. `git log --branches --not --remotes`).
   - **Ha van** → **ne** húzz `git pull`-t; kérd meg a felhasználót, hogy kezelje le (commit/push/stash), és várj, amíg a `main` tiszta.
   - **Ha tiszta** → `git pull` (a remote-ot is frissíti, így a feature-branch-scan is friss állapotot lát — külön `git fetch` jellemzően nem kell).

A branch-név a `conventions.md` `## <sec:cv_git_conventions>` **<field:f_branch_naming>** mezője szerint áll össze; alapból `feature/cycle-NN-<name>` (a **mappanév** ettől függetlenül mindig tisztán `cycle-NN-<name>`, prefix nélkül — BD3).
