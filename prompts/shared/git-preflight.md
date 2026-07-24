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

Olvasd ki a `conventions.md` `## Git és branching konvenciók` szekciójából a verziókezelő-flaget:

- Ha ott az áll, hogy **„NINCS verziókezelő (se GIT, se más), és nem is lesz."**, akkor **minden git-műveletet hagyj ki** ebben a fázisban — nincs `git status`, branch-váltás/-létrehozás, `git pull`, commit. A fázis csak a nem-git teendőit végzi el (fájl/mappa létrehozás). A lenti lépéseket **átugrod**.
- Egyébként (git elérhető, a projekt git-repo) → folytasd a *Munkafa-ellenőrzéssel*.

#### Munkafa-ellenőrzés

Futtasd: `git status --short`. Ha van commitálatlan változtatás:

- Listázd ki az érintett fájlokat.
- Kérdezd meg **egy körben**: *„Commitáljam ezeket most, vagy folytassam?"* — várj a válaszra, majd aszerint járj el.

#### Friss, tiszta `main` (leágazás előtt)

A cél, hogy friss `main`-ről (a `conventions.md` `## Git és branching konvenciók` **Fő branch** mezője; alapból `main`) ágazz le. A tényleges `git switch -c`-t **nem** itt futtatod — azt a fázis a saját logikája szerint végzi (a `00` azonnal, a `01` a ciklusnév meghatározása UTÁN — BD5).

1. **Hol állunk? (BQ3 — idempotencia/resume):** `git branch --show-current`.
   - **`main`-en vagyunk** → tovább a 2. ponthoz.
   - **feature branch-en vagyunk** → hasonlítsd össze a branch nevét az **aktuális ciklus várt branch-nevével** (a `roadmap.md` folyamatban lévő ciklus-blokkjából / a ciklus mappanevéből):
     - **Egyezik** → ez egy **resume**; a branch már létezik. **Nincs teendő** — folytasd ezen a branch-en, `git switch -c`-t **NE** futtass, és **ne** figyelmeztess.
     - **Nem egyezik** → **csak ekkor** szólj a felhasználónak: a jelenlegi branch-et érdemes lehet **merge-elni vagy PR-t feladni rá** a `## Merge stratégia` szerint, **mielőtt elhagyja**; majd kérd meg, hogy **váltson `main`-re** (a váltást ő végzi az esetleges nyitott munka miatt). Várj, amíg rendezi.
2. **Friss és tiszta `main` (BQ4):** ha `main`-en vagyunk, a leágazás **előtt**:
   - Ellenőrizd, van-e commitálatlan tartalom **vagy** nem-pusholt lokális commit (pl. `git status --short` + `git status -sb` ahead-jelzés, ill. `git log --branches --not --remotes`).
   - **Ha van** → **ne** húzz `git pull`-t; kérd meg a felhasználót, hogy kezelje le (commit/push/stash), és várj, amíg a `main` tiszta.
   - **Ha tiszta** → `git pull` (a remote-ot is frissíti, így a feature-branch-scan is friss állapotot lát — külön `git fetch` jellemzően nem kell).

A branch-név a `conventions.md` `## Git és branching konvenciók` **Branch-elnevezési stratégia** mezője szerint áll össze; alapból `feature/cycle-NN-<name>` (a **mappanév** ettől függetlenül mindig tisztán `cycle-NN-<name>`, prefix nélkül — BD3).
