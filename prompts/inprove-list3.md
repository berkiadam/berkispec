# Prompt fejlesztési lista — 3. munkafájl: ciklus = branch a 01-add-cycles fázisban

Ez a **munkafájl** egyetlen bővítést követ nyomon: a `prompts/skills/01-add-cycles.md`
skill egészüljön ki azzal, hogy **minden fejlesztési ciklust külön git branch-en**
végzünk.

**A probléma (jelenlegi hiányosság):** A skill *ígéri* a branch-et — a B. mód
névjavaslatánál (229. sor): *„Ez lesz a branch és a mappa neve is (pl.
`cycle-NN-[javasolt-név]`)"* —, **de sehol nem hozza létre és nem vált rá.** Az összes
git művelet (A/B/C mód lezárása) az aktuális branch-en történik, `git switch -c` nélkül.

---

## 0. Rögzített döntések

- [x] **BD1 — Branch időzítése:** A ciklus-branch **itt, a 01 fázisban** jön létre, a
  ciklus legelején (nem a 06-implement fázisban). A tényleges implementáció a 02+
  fázisokban már ezen a branch-en fut.

- [x] **BD2 — Branch bázisa:** A ciklus-branch **main-ről** ágazik le.

- [x] **BD3 — Branch neve = `feature/` + ciklus neve (default):** A branch **alapértelmezett**
  neve `feature/cycle-NN-<name>`. Ez a **default**, ha a `conventions.md` nem rendelkezik
  másképp. Ha a `conventions.md`-ben (BD8 nyomán) más branch-elnevezési stratégia van rögzítve
  (pl. Jira-jegyszám elöl, más prefix), akkor azt kell alkalmazni. A **mappanév minden esetben
  tisztán** `cycle-NN-<name>` marad (prefix nélkül) — csak a git branch neve kap prefixet.

- [x] **BD4 — Main védett, a roadmap is a branch-re megy:** A `main` általában védett
  (nem lehet rá közvetlenül commitolni). Ezért a **roadmap-változtatás (`specs/roadmap.md`)
  és a `cycle-NN: 01-cycles` commit is a feature branch-re kerül**, nem main-re. Indok: a
  ciklus úgyis módosítja a roadmap-et (új blokk, státusz), tehát hozzá kell nyúlni; main-re
  pedig nem lehet commitolni.

- [x] **BD5 — B. mód sorrendje:**
  1. Következő ciklusszám (`NN`) + név meghatározása — main roadmap-je + `ls specs/`
     alapján (még az induló branch-en).
  2. Név jóváhagyása → `cycle-NN-<name>` (mappanév), branch: `feature/cycle-NN-<name>`
     vagy a `conventions.md` szerinti elnevezés.
  3. **Előbb** branch létrehozása main-ről: `git switch -c feature/cycle-NN-<name>` (default).
  4. **Ezután** roadmap-szerkesztés + `mkdir specs/cycle-NN-<name>/` + commit — mind a
     branch-en. A roadmap frissítése (új ciklus blokk + státusz) **már az új branch-en**
     történik, nem a bázison.

- [x] **BD6 — Ha nem main-en állunk induláskor:** A branch mindig **main-ről** ágazik. Ha
  a fázis indulásakor NEM a main-en vagyunk, a skill **ne váltson automatikusan** — mondja
  meg a felhasználónak, hogy váltson main-re, és **előbb figyelmeztesse**, hogy a jelenlegi
  branch-et érdemes lehet merge-elni vagy PR-t feladni rá, mielőtt elhagyja. A tényleges
  váltást a felhasználó végzi (uncommitted munka / nyitott branch miatt). **BQ3 finomítja:**
  ha a feature branch neve épp az aktuális ciklusé, akkor ez resume → nincs figyelmeztetés,
  csendben folytatjuk azon a branch-en.

- [x] **BD7 — Merge vs PR projektfüggő, az init fázisban tisztázandó:** Hogy egy elkészült
  ciklus-branch **merge-eléssel vagy PR-rel** kerül vissza main-be, az **mindig az adott
  projekttől függ**. Ezt a `00-init-project.md` skillben kell tisztázni és rögzíteni (pl. a
  `conventions.md`-be), hogy a 01 (és a későbbi fázisok) a projekt konvenciója szerint tudják
  megfogalmazni a merge/PR figyelmeztetést (BD6).

- [x] **BD8 — Branch-elnevezési stratégia az init fázisban tisztázandó (default: `feature/`):**
  A `00-init-project.md` külön kérdezzen rá a szervezet branch-elnevezési stratégiájára, és
  rögzítse a `conventions.md`-be. Konkrét kérdések:
  - Kell-e **Jira-jegyszámot** a branch nevének elejére írni? (ha igen: milyen formátumban)
  - A feature branch-ek **`feature/` prefixszel** kezdődnek-e?
  - **Vagy** mutasson rá a felhasználó egy dokumentumra, ahol ezek tisztázva vannak (akkor
    onnan vesszük át a szabályt).
  **Default:** ha a felhasználó nem rendelkezik és a `conventions.md` nem tartalmaz mást, a
  branch-név `feature/cycle-NN-<name>` (BD3). Az init eredménye adja a branch teljes nevének
  prefixét.

- [x] **BD9 — API-írási szabályzat az init fázisban tisztázandó:** A `00-init-project.md`
  kérdezzen rá, hogy van-e **API-szabályzat / API design guideline**, amit követni kell (pl.
  REST konvenciók, verziózás, hibaformátum, elnevezés). Ha van, **hol** található az ezt leíró
  dokumentum — a pointer kerüljön a `conventions.md`-be, hogy a spec/plan fázisok (02–03) ebből
  dolgozhassanak. A nagy dokumentumok kezelését lásd BD10.

- [x] **BD10 — Nagy külső szabály-dokumentumok kezelése (hibrid: pointer + kivonat):** Ha a
  felhasználó branching- vagy API-szabályokat tartalmazó dokumentumra mutat, azt **NEM szabad
  teljes szöveggel** a `conventions.md`-be tenni (minden fázis behúzná → token-duzzadás).
  Megoldás:
  - **Pointer** a `conventions.md`-be: a forrás elérési útja/URL-je + egy soros leírás, mit
    szabályoz.
  - **Kivonat**: az init a `researcher` subagenttel (`agents/researcher.md`) **egyszer**
    beolvastatja a nagy doksit, és kihozat belőle egy tömör, normatív **szabály-checklistet**
    (konkrét do/don't pontok), ami a `conventions.md`-be kerül. Ez pár soros, mindig elérhető.
  - **Mély/ritka részletek**: a fogyasztó fázis (branching → 01, API → 02–03) a `researcher`-t
    hívja, ami a **teljes** doksit on-demand olvassa a subagent kontextusában — a fő flow nem
    szennyeződik.
  - **Kivétel — kis szabályok szó szerint:** a branching-szabály tipikusan pici (prefix,
    Jira-jegy) → mehet szó szerint a `conventions.md`-be, ott nincs szükség pointer+kivonat
    játékra. A hibrid elsősorban a nagy API-guideline-okra vonatkozik.
  - **Drift:** a pointer megőrzi a forrást, így a kivonat újragenerálható, ha a doksi változik.

- [x] **BD11 — Van-e egyáltalán verziókezelő? (init fázisban tisztázandó, a branch-logika
  kapuja):** A teljes branch-logika (BD1–BD10, BQ2, BQ3) **feltételezi a git-et**. Ezért a
  `00-init-project.md`-nek **tisztáznia kell, van-e verziókezelő a projektben**:
  - Ha a `git` elérhető és a projekt git-repo → normál branch-flow.
  - Ha a `git` **nem érhető el** (nincs repo / nincs telepítve) → **kérdezzen rá** a
    felhasználónál, és ha nincs és nem is lesz VCS, **rögzítse a `conventions.md`-be
    explicit módon: „NINCS verziókezelő (se GIT, se más), és nem is lesz."**
  - Ez a flag a **kapu**: ha a `conventions.md` azt mondja, nincs VCS, a 01 (és a többi fázis)
    **kihagy minden git-műveletet** — nincs `git switch -c`, nincs branch-figyelmeztetés,
    nincs commit; a ciklus csak a `specs/cycle-NN-<name>/` mappát hozza létre és a roadmap-et
    írja, verziókezelés nélkül.

- [x] **BD12 — Az init-project (00) is saját feature branch-en fut:** A `00-init-project.md`
  önmaga is egy feature branch-en dolgozzon, alapértelmezett néven **`feature/init-project`**.
  - **Futás előtti ellenőrzés (ugyanaz, mint BD6 + BQ4):** main-en vagyunk-e; a main friss-e
    (`git pull`); nincs-e commitálatlan vagy nem-pusholt lokális változás. Ha nem tiszta →
    kérd meg a felhasználót, hogy rendezze, mielőtt indulna. Ha rendben → `git switch -c
    feature/init-project`, és az init a branch-en dolgozik.
  - **Futás utáni visszaintegrálás:** az init végén **PR feladás vagy közvetlen merge** main-be
    — **aszerint, amit az init futása közben a `conventions.md`-be rögzítettünk** (BD7 merge
    vs PR). Azaz a döntés ugyanabban a futásban születik meg, amit itt alkalmazunk.
  - **Csirke-tojás sorrend (fontos):**
    - A **branch-létrehozás** (`feature/init-project`) csak akkor fut, ha git elérhető. A VCS
      meglétét (BD11) az init tisztázza — de a `git` **elérhetőségét** már az elején detektálni
      lehet (pl. `git rev-parse`), a formális „NINCS és nem is lesz" rögzítés a hiánynál készül.
      Ha nincs git → az init nem hoz branch-et, nem PR-ezik/merge-el (a BD11 no-VCS ága).
    - A **merge-vs-PR** (BD7) döntés a futás közben kerül a `conventions.md`-be, és a **futás
      végén** alkalmazzuk. Ha a felhasználó nem dönt / nincs remote → default a közvetlen merge
      main-be (eldöntendő, lásd BQ7).

- [x] **BD13 — Közös git-preflight leírás: `prompts/shared/git-preflight.md`:** A
  futás-előtti ellenőrzés (main-en vagyunk-e; friss-e a main `git pull`-lal; nincs-e
  commitálatlan vagy nem-pusholt változás) **egyetlen közös fájlba** kerül:
  `prompts/shared/git-preflight.md` (új `prompts/shared/` mappa, az `agents/` és `skills/`
  testvére). **Scope:** nem csak a 00/01 — a **02–09 fázisok is** ugyanezt a „Munkafa
  ellenőrzés" blokkot duplikálják jelenleg, tehát mindannyian erre a közös leírásra
  hivatkozzanak, a duplikáció megszűnik. A no-VCS ág (BD11) itt is kapu: git nélkül a preflight
  kihagyva.

- [x] **BD14 — A telepítő scriptek juttassák el a közös leírást minden ágenshez:** Mivel a
  skillek platformonként eltérő helyre települnek (`.claude/skills/bs-*/SKILL.md`,
  `.agents/skills/`, Codex `.codex/agents/*.toml`, Copilot `.github/instructions/`,
  `.cursor/skills/`), egy relatív `shared/git-preflight.md` hivatkozás **futásidőben nem
  oldódna fel egységesen**. Ezért a `install.sh` / `install.ps1` és a
  `prompts/scripts/install-helper.py` **telepítéskor ágyazza be (inline)** a
  `prompts/shared/git-preflight.md` tartalmát minden hivatkozó skillbe (build-time include),
  hogy a telepített SKILL.md önmagában teljes legyen. Ez minden támogatott ágensnél működjön
  (Claude, Codex, Copilot, Antigravity, Cursor). (Alternatíva: a fájl külön másolása egy ismert
  útra + runtime olvasás — törékenyebb a platform-eltérések miatt, ezért az inline az ajánlott.)

- [x] **BD15 — BD7 a MEGLÉVŐ `## Merge stratégia`-ra épül (ne új mező):** A `conventions.md`-ben
  **már van** `## Merge stratégia` szekció (`Szolgáltató` mező), amit a **09-review-and-merge**
  olvas és aszerint csinál lokális squash merge-et vagy PR-t. A BD7 (merge vs PR) **ezt
  használja/terjeszti ki**, nem vezet be új mezőt. A BD6/BD12 figyelmeztetés és a 00
  visszaintegrálás (BQ7) is ebből a szekcióból dolgozzon — egyetlen igazságforrás a merge
  stratégiára.

---

## 1. Nyitott kérdések (döntés előtt)

- [x] **BQ7 (ELDÖNTVE) — Visszaintegrálás default: MERGE:** Ha nincs explicit `## Merge
  stratégia` döntés (vagy nincs remote), a default a **közvetlen merge main-be** — nem PR.
  Ez vonatkozik a `feature/init-project` (BD12) visszaintegrálására és általánosan a ciklus-
  branch-ek visszaintegrálására is, ha a `conventions.md` nem rendelkezik másképp.

- [x] **BQ1 (ELDÖNTVE) — A. mód: az 1. ciklus branch-ére, default `feature/cycle-01`:** Az
  A. mód a teljes roadmap-et **az első ciklus feature branch-én** hozza létre és commitolja.
  A branch létrehozása előtt **kérdezzük meg a felhasználót, mi legyen az első ciklus neve**;
  a **default: `feature/cycle-01`** (ha a felhasználó nem ad nevet). A branch-flow egyébként a
  B. mód mintáját követi (BD5, BD6, BQ3, BQ4): main-check + preflight, majd `git switch -c
  feature/cycle-01[-<name>]`, és a roadmap + commit a branch-en. A no-VCS ág (BD11) itt is
  kihagyja a git-műveleteket.

- [x] **BQ2 (ELDÖNTVE) — Számozás a feature branch-ek átnézésével:** A `NN` meghatározásakor
  **nem elég** a main `roadmap.md` + `ls specs/`, mert lehet olyan ciklus, ami csak egy
  (még nem merge-elt) feature branch-en létezik. **Döntés:** a következő ciklusszám
  meghatározása előtt **nézzük végig a feature branch-eket** (lokális + remote), és keressük
  meg a bennük szereplő `cycle-NN` neveket. Az új ciklusszám:
  `max(main roadmap/specs ciklusszámai, feature branch-ekben lévő ciklusszámok) + 1`.
  Így nem lesz ütközés a párhuzamosan nyitott / nem merge-elt ciklusokkal.
  - Mechanizmus: `git branch -a --list '*cycle-*'` (a BD8 szerinti prefixet is lefedve, pl.
    `feature/cycle-*`), a branch-nevekből `cycle-(\d+)` kinyerése, egyesítve a
    main-oldali `ls specs/` + `roadmap.md` számokkal. A max + 1 az új szám.
  - Megjegyzés: érdemes a remote állapot frissessége miatt előbb `git fetch` (lásd BQ4).

- [x] **BQ3 (ELDÖNTVE) — Újrafuttatás / idempotencia branch-ellenőrzéssel:** Induláskor,
  mielőtt bármit tennénk (`git branch --show-current`):
  1. **A jelenlegi branch main vagy feature?**
  2. **Ha feature branch** → hasonlítsd össze a nevét az aktuális ciklus várt branch-nevével
     (resume-nál a `roadmap.md` in-progress ciklus blokkjából / a mappanévből derül ki):
     - **Egyezik** → ezt a branch-et **már egyszer létrehoztuk** (ez egy resume). **Nincs
       teendő** — folytatjuk ezen a branch-en, `git switch -c`-t NEM futtatunk.
     - **Nem egyezik** → **csak ekkor** szólj a felhasználónak, hogy intézkedjen (BD6
       szerinti merge/PR figyelmeztetés + váltás main-re).
  3. **Ha main** → normál friss flow (BD5): a számozás/név után `git switch -c`.
  Ez **finomítja a BD6-ot:** nem vakon figyelmeztetünk minden nem-main esetben, csak ha a
  feature branch nem az aktuális ciklusé.

- [x] **BQ4 (ELDÖNTVE) — Main frissítése a leágazás előtt, tiszta munkafa mellett:** Ha
  main-en vagyunk (BQ3 szerint), a branch létrehozása **előtt** friss bázis kell. Sorrend:
  1. **Előbb ellenőrizd**, van-e commitálatlan tartalom **vagy** nem-pusholt lokális commit
     (pl. `git status --short` + `git log --branches --not --remotes` / `git status -sb`
     ahead-jelzés).
  2. **Ha van** → **ne** húzz pull-t; **kérd meg a felhasználót**, hogy kezelje le ezeket
     (commit/push/stash), hogy a main tiszta legyen. Várj, amíg rendezi.
  3. **Ha tiszta** → `git pull`, hogy a legfrissebb main legyen meg, majd `git switch -c ...`.
  - Mellékhaszon: a `pull` a remote-ot is frissíti, így a BQ2 feature-branch-scan
     (`git branch -a`) is friss remote-állapotot lát — külön `git fetch` jellemzően nem kell.

- [x] **BQ5 (ELDÖNTVE) — C. mód: csak az adott ciklus roadmap-részét javítjuk, a ciklus
  feature branch-én:** A C. mód **ne** írja/commitolja az egész roadmap-et egy közös branchre.
  Ehelyett **mindig csak az adott ciklus roadmap-blokkját** javítjuk/pótoljuk, és azt **az
  adott ciklus feature branch-én** (ugyanaz a per-ciklus branch-elv, mint a B. módban). Így a
  védett main + „branch = ciklus" invariáns megmarad, nincs több-ciklust-egyszerre-commitoló
  rekonstrukciós branch.
  > **BQ6 rendezte:** a C. mód eredeti teljes-rekonstrukciós célja **megszűnik**, per-ciklus
  > javítássá alakul (lásd lent).

- [x] **BQ6 (ELDÖNTVE) — A C. mód átalakul per-ciklus javítássá:** A klasszikus „teljes roadmap
  rekonstrukció az összes ciklusmappából, egy `Piszkozat` dokumentumba" forgatókönyv **megszűnik**.
  Helyette: ha az aktuális ciklus roadmap-blokkja hiányzik/hibás, a C. mód **csak azt az egy
  blokkot** pótolja/javítja, **a ciklus feature branch-én** (BQ5). A többi ciklus a saját
  branch-én / a merge-elt main-roadmap-ben él. A teljes roadmap main-en a ciklusok merge-elésével
  áll össze, nem egy nagy rekonstrukciós lépésben.

---

## 2. Implementációs teendők (döntések után)

- [x] **BI1 — B. mód lezárás átírása** (270–287. sor): a `mkdir` + commit elé kerüljön a
  `git switch -c cycle-NN-<name>` main-ről; a commit-üzenet és a következő-lépés szöveg
  változatlan maradhat.

- [x] **BI2 — Előfeltétel / munkafa-check igazítása** (32. sor): a tiszta-munkafa ellenőrzés
  és a branch-váltás sorrendjének összehangolása. Ide kerül:
  - **BD6 „nem main-en vagyunk"** ellenőrzés: `git branch --show-current` → ha nem main (és
    BQ3 szerint nem az aktuális ciklus branch-e), figyelmeztetés (jelenlegi branch merge/PR a
    projekt konvenciója szerint) + felszólítás, hogy váltson main-re.
  - **BQ4 main-frissítés:** ha main-en vagyunk, a `git switch -c` **előtt**: (1) tiszta-e a
    munkafa + nincs-e nem-pusholt commit? (2) ha nem tiszta → kérd a felhasználót, hogy
    rendezze; (3) ha tiszta → `git pull`, majd branch létrehozása.

- [x] **BI3 — „Folytatás megszakított futás után" + induló branch-ellenőrzés (BQ3)** (36–53.
  sor): induláskor `git branch --show-current` → main/feature ág; feature esetén
  név-egyezés az aktuális ciklus branch-nevével → egyezik: resume, nincs teendő (nincs
  `git switch -c`); nem egyezik: BD6 figyelmeztetés + váltás main-re.

- [x] **BI4 — A. mód lezárás branch-esítése (BQ1)** (196–204. sor): a roadmap `Kész`-re
  állítása + commit **előtt** kérdés a felhasználóhoz az 1. ciklus nevéről (default:
  `feature/cycle-01`), majd preflight (BD6/BQ4) + `git switch -c feature/cycle-01[-<name>]`;
  a roadmap-írás és a commit a branch-en. No-VCS ág (BD11) kihagyja a git-lépéseket.

- [x] **BI5 — C. mód átírása per-ciklus javításra (BQ5 + BQ6)** (290–316. sor): a teljes
  rekonstrukciós logika (`ls -d specs/cycle-*/`, researcher-es összesítés, teljes
  `Piszkozat` roadmap felépítése, C→B átmenet) **eltávolítása/átalakítása**. Helyette: az
  aktuális ciklus hiányzó/hibás roadmap-blokkjának pótlása a ciklus feature branch-én, a B.
  mód mintája szerint. Commit a ciklus branch-re.

- [x] **BI6 — `00-init-project.md` bővítése (BD11 + BD7 + BD8 + BD9):** az init fázis külön
  kérdezze meg és rögzítse a `conventions.md`-be:
  - **BD11 — Verziókezelő megléte (KAPU, elsőként):** van-e git a projektben? Ha nincs és nem
    is lesz → rögzítse explicit: „NINCS VCS (se GIT, se más)". Ez kapuzza az összes lenti
    branch-logikát.
  - **BD7 — Merge vs PR:** hogyan kerül vissza egy ciklus-branch main-be (közvetlen merge
    vagy PR)?
  - **BD8 — Branch-elnevezési stratégia:** kell-e Jira-jegyszám a branch elejére? Van-e
    `feature/` prefix? Vagy pointer egy dokumentumra, ami ezt leírja.
  - **BD9 — API-szabályzat:** van-e követendő API design guideline, és ha igen, hol a
    dokumentuma (pointer a `conventions.md`-be a 02–03 fázisok számára).
  - **BD10 — Nagy doksik hibrid kezelése:** ha a felhasználó nagy dokumentumra mutat (API-
    guideline, esetleg terjedelmes branching-szabályzat), az init **ne** tegye be teljes
    szöveggel — hanem (a) pointer a `conventions.md`-be, és (b) a `researcher` subagenttel
    készíttessen belőle tömör szabály-checklist kivonatot a `conventions.md`-be. Kis branching-
    szabály maradhat szó szerint.
  Ezek a `conventions.md`-be kerülnek, hogy a 01 (BD3 branch-név prefix, BD6 merge/PR
  figyelmeztetés) és a spec/plan fázisok ebből tudjanak dolgozni.

- [x] **BI8 — VCS-kapu a 01 fázisban (BD11):** a 01 minden git-művelet előtt olvassa ki a
  `conventions.md` VCS-flag-jét. Ha „NINCS VCS" → hagyja ki a branch-létrehozást, a
  branch-figyelmeztetéseket és a commitokat; csak `mkdir specs/cycle-NN-<name>/` + roadmap-írás
  történjen. A feature-branch-scan (BI7) is csak VCS esetén fut.

- [x] **BI9 — `00-init-project.md` saját branch-flow (BD12):** az init elején git-elérhetőség
  detektálása; ha van git → main-check + friss-check (pull) + tiszta-munkafa-check (BD6/BQ4
  mintája), majd `git switch -c feature/init-project`. Az init végén a `conventions.md`-be
  rögzített merge/PR konvenció (BD7) szerinti visszaintegrálás main-be (BQ7 default). No-VCS
  ág (BD11): branch/PR/merge kihagyva.

- [x] **BI7 — Ciklusszámozás a feature branch-ek átnézésével (BQ2):** A B. mód
  ciklusszám-meghatározását (212–213. sor) és a mód-detektálást (57–79. sor) egészítsük ki:
  a `NN` = `max(main `roadmap.md`/`ls specs/` ciklusszámai, a feature branch-ekben lévő
  `cycle-NN` számok) + 1`. Branch-scan: `git branch -a --list '*cycle-*'` (a BD8 prefixet is
  lefedve), `cycle-(\d+)` kinyerés. A frissességet a BQ4 `git pull`-ja adja (remote is
  frissül), külön `git fetch` jellemzően nem kell.

- [x] **BI10 — Közös `prompts/shared/git-preflight.md` létrehozása + skillek átkötése (BD13):**
  új `prompts/shared/` mappa + `git-preflight.md` a preflight blokkal (main-check, `git pull`
  frissesség, tiszta munkafa, no-VCS kapu). A **00, 01, és a 02–09** skillekben a duplikált
  „Munkafa ellenőrzés" blokk cseréje a közös leírásra való hivatkozással (a frontmatterben is
  jelezve, az `agents/…` minta szerint).

- [x] **BI11 — Telepítő: közös leírás inline-olása minden ágenshez (BD14):** `install.sh`,
  `install.ps1` és `prompts/scripts/install-helper.py` bővítése úgy, hogy a
  `prompts/shared/git-preflight.md` tartalma **telepítéskor beágyazódjon** minden hivatkozó
  skill telepített változatába (Claude / Codex / Copilot / Antigravity / Cursor mindegyikénél),
  így a telepített SKILL.md önmagában teljes.

- [x] **BI12 — `## Merge stratégia` újrahasználat (BD15):** a BI6 (00 init) és a BI1/BI2
  (01 branch-figyelmeztetés) a `conventions.md` **meglévő** `## Merge stratégia` szekciójából
  dolgozzon (amit a 09 is használ), ne vezessen be új mezőt. Szükség esetén a szekció
  kiegészítése a 00-init visszaintegrálás igényeivel (BQ7 default).

- [x] **BI13 — `README.md` frissítése + új „Branching stratégia" alfejezet:** a `README.md`-be
  új alfejezet a branch-modellről. Tartalma: a per-ciklus branch elv (BD1–BD3, default
  `feature/cycle-NN-<name>`), main-ről ágazás + preflight (BD6/BQ4), a 00 saját branch-e
  (BD12), a számozás branch-scannel (BQ2), a visszaintegrálás merge-default (BQ7) és a
  `## Merge stratégia` kapcsolat (BD15), valamint a no-VCS ág (BD11). **Elhelyezés:** logikusan
  a `## 10. conventions.md` közelébe vagy önálló szekcióként az 5. (flow) után — a
  `## Merge stratégia`-ra és a ciklus-artifact szekciókra hivatkozva. A szomszédos szekciók
  (skill-index, mappastruktúra) is frissüljenek, ahol branch-információ releváns.

- [x] **BI14 — Branch-viselkedés dokumentálása az érintett skillekben:** minden érintett
  skillbe (00, 01, és ahol a preflight/branch releváns: 02–09) kerüljön rövid, explicit leírás
  arról, **hol mi történik branch ügyben** (pl. a 01-ben: „itt jön létre a `feature/cycle-NN`
  branch main-ről"; a 09-ben: „itt integrálódik vissza a `## Merge stratégia` szerint"). Cél:
  a skillt olvasó (ember és gyenge modell is) egyértelműen lássa a branch-lépést a saját
  fázisában, ne csak a README-ből.
