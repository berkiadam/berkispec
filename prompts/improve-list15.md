# „A központosított SDD nem fut le" — a CI-lánc kiépítése

> **Állapot: ELŐKÉSZÍTŐ ANYAG.** Ez a dokumentum még **nem** végrehajtott kör: a mérést, a
> már lezárt döntéseket és a kanonikus mintákat rögzíti, hogy a végrehajtás ne a nulláról
> induljon. Amíg a 7. szakasz csomagjai nincsenek lepipálva, a repó egyetlen promptja és
> scriptje sem változott ettől a körtől.

---

## 0. Hogyan használd ezt a dokumentumot

- A **2. szakasz** a mért mai állapot: mit mond ma a keret a központosított útról, és hol
  szakad el a lánc. Minden tétel `fájl:sor` hivatkozással áll — ezek 2026-09-23-i mérések.
- A **3. szakasz** a kanonikus pipeline-minták (GitHub Actions + Azure DevOps). Implementáláskor
  **ezeket másold**, ne a prózát.
- A **4. szakasz** a lezárt döntések (`L15-D1`…). **Ezeket ne döntsd el újra másképp** — ha
  mégis kell, a döntés mellé írd oda, mi változott.
- A **6. szakasz** a nyitott kérdések: ezek még a Felhasználóra várnak.
- A **7. szakasz** a végrehajtási csomagok — a kör akkor kezdődik, amikor a 6. kiürül.

## 0.1 A hivatkozott keret-azonosítók — hol nézd meg őket

| azonosító | mit jelöl | hol áll |
|---|---|---|
| `CS1`–`CS7` | a központosított SDD követelményei | `prompts/improve-list13.md` 5. szakasz |
| `VP1`/`VP2`/`VP3` | a három bizonyítási pont | `prompts/improve-list13.md` 2.1 |
| `L13-D1`–`L13-D26` | a `list13` lezárt döntései | `prompts/improve-list13.md` 8. szakasz |
| `RM8`, `RM11` | a `## Review and merge` szekció követelményei | `prompts/improve-list13.md` 3. + 3.1 |
| `TM1`–`TM10` | test manager integráció | `prompts/improve-list13.md` 5.b |
| `RV1`, `RV-INC` | a review-kapu és a megszakadás-tűrés | `prompts/skills-hu/07-validate.md`, `agents-hu/reviewer.md` |
| `BD8`, `BQ2`–`BQ4`, `PW1`–`PW5` | git-preflight, branch-elnevezés | `prompts/shared-hu/git-preflight.md` |
| `TR3`, `TR6`, `TR7` | riport-artefaktumok és frissesség | `prompts/skills-hu/07-validate.md` |
| `D8`/`KT6` | bizonyíték-tűzfal (`test-runs/` ≠ ciklus-bizonyíték) | `prompts/improve-list13.md` 6.4 |

---

## 1. A kiváltó megfigyelés

A `list13` kör **megépítette a központosított SDD szerződését**: a `09a`–`09d` skill-családot, a
`ci-run-skill.sh` adaptert, a `notify.py`-t, a `## Review and merge` kapcsolótáblát és a három
bizonyítási pontot. A `docs/hu/full-flow.md` ábráján a `PR` nyíl átvisz a CI/CD sávba, és ott
„ember nélkül" fut a `9b` → `9c` → `9d`.

**A lánc első szeme viszont hiányzik.** A repóban nincs egyetlen pipeline-definíció sem, és a
`ci-run-skill.sh`-t a `00-init-project` `--selftest`-jén kívül **semmi nem hívja**. A
„PR feladása triggereli a CI/CD-t" (`CS1`) ma **prózai állítás**, nem futtatható artefaktum:

- a `--selftest` kipróbálja, hogy az ágens CLI **elérhető-e** — de nem azt, hogy a **lánc** lefut-e;
- a `ci-run-skill.sh <skill> <ciklus-útvonal>` **kötelezően** kér ciklus-útvonalat, miközben a
  CI-nek csak egy PR-je és egy branch-neve van — a leképezést semmi nem mondja ki;
- a `09b` és a `09c` **commitol és push-ol a PR ágára**, ami ugyanazt a pipeline-t újraindítja —
  a hurkot semmi nem töri meg;
- a `Failure handling: auto-fix-loop` érték a `00`-ban **felajánlható**, de a mechanizmusa
  sehol nem létezik.

Ez a kör ezt a négy hézagot zárja be, plusz a hozzájuk tapadó hatokat (2. szakasz).

### 1.1 A lánc, ahogy megbeszéltük (2026-09-23)

```
A FEJLESZTŐ GÉPÉN
  … 02–08 fázisok …
  /bs-create-pr  → ág felküldése + PR megnyitása, ott MEGÁLL
                   (a roadmapon: ⏳ verifikációra vár)
         │
         ▼  a PR feladása az INDÍTÓ ESEMÉNY
A CI/CD-BEN (ember nélkül)
  1. klón egy üres mappába, átállás a PR ágára
  2. berkispec telepítése + a `CI agent` mező szerinti ágens CLI (antigravity NEM)
  3. ci-run-skill.sh → a ciklus feloldása a PR diffjéből (L15-D1)
  4. KÓDREVIEW — az ÁGENS futtatja a bs-review skillt          ← itt van az ítélet
  5. KAPU — validate-gate-check.py                             ← itt van a döntés
       bukott → ugrás a 7-re (fail-fast, L15-D5)
  6. MERGE UTÁNI TESZTEK a merge-commiton (L15-D4)
  7. a bizonyíték commitolása + push a PR-ágra (CS6)          → head = B
  8. a PIPA kiírása API-n a B commitra (L15-D6)
       `berkispec/review-and-test-runner`  ✓ / ✗
       + értesítés (notify.py), ha bukott vagy emberi döntés kell
         │
         ▼
A SZOLGÁLTATÓNÁL
  a branch policy dönt: megvan-e MINDEN szükséges pipa? (L15-D3)
       ─ gépi pipa + (ha a szervezet kéri) emberi jóváhagyás
       ─ ha nincs meg mind → a folyamat VÁR, magától nem megy tovább
       ─ ha megvan mind   → a beolvasztás már csak egy parancs
```

**A lényeg három mondatban.** A review **ágens** dolga, mert ítélet kell hozzá; a **folytatásról**
determinisztikus kapu dönt, nem az ágens; a **beolvaszthatóságról** pedig a szolgáltató
policy-je, nem a keret.

---

## 2. Mérés — a mai állapot (2026-09-23)

### 2.1 `G1` — Semmi nem indítja a CI-t

```
$ grep -rln "\.github/workflows\|gitlab-ci\|azure-pipelines" prompts/ docs/ *.md
prompts/improve-list2.md
docs/talks/ai-transformation-slides.md
docs/talks/ai-transformation-in-enterprise-env.md
```

Egyik sem pipeline-definíció: az első egy régi kör terve, a másik kettő prezentációs anyag. A
`ci-run-skill.sh` hívói a repóban:

| hol | mi |
|---|---|
| `prompts/skills-{hu,en}/00-init-project.md:155` | `--selftest` a `conventions.md` lezárása előtt |
| `prompts/lang/{hu,en}/00-init-project.md:146` | a `CI agent` mező magyarázó prózája |
| `berki-spec-directory-structure.md:137` | a telepített fájl leírása |
| `prompts/meta-improve-prompts.md:146` | a script-tábla sora |

**Éles futtató sehol.** A `docs/hu/platform-integration.md` sem mondja meg, milyen eseményre és
milyen jogosultsággal fut — csak azt, hogy az Antigravity nem alkalmas rá.

### 2.2 `G2` — A ciklus-útvonal felderítése

Az adapter szerződése ma:

```
ci-run-skill.sh <skill-név> <ciklus-útvonal>      # mindkettő KÖTELEZŐ
```

A branch-névből következtetni **nem szabad**, és ezt maga a keret mondja ki:

> `prompts/lang/hu/00-init-project.md:89` — „**Branch-elnevezési stratégia (BD8):** _(default:
> `feature/cycle-NN-<name>`; ha van Jira-prefix / más szervezeti szabály / pointer egy
> dokumentumra, ide)_ — a **mappanév** ettől függetlenül mindig prefix nélkül, tisztán
> `cycle-NN-<name>`"

Ugyanez a `prompts/shared-hu/git-preflight.md:78`-ban. A keret **végig mappa → branch** irányban
képez le: a `git-preflight` BQ3 resume-felismerése a roadmap ciklus-blokkjából / a mappanévből
állítja elő a **várt** branch-nevet, és ahhoz hasonlít (`git-preflight.md:50`). Visszafelé sosem.

**Következmény:** egy Jira-prefixes vagy szervezeti elnevezésű projektben a branch-alapú
feloldás az **első éles PR-en** dőlne el — a legrosszabb helyen.

### 2.3 `G3` — A CI push-ja újraindítja a CI-t

| hol | mit ír és hova |
|---|---|
| `prompts/skills-hu/09b-review.md` *Lezárás* 2. | `ci-code-review.md` + `cycle-status.md` → commit a **ciklus ágára**, majd push |
| `prompts/skills-hu/09c-merge.md` *A `VP2` bukása* 1. | a `test-report/post-merge/` készlet → commit + push a ciklus ágára |

Mindkettő a PR ágára push-ol, ami a `pull_request` / PR-validation eseményt **újra kiváltja**.
Ma semmi nem töri meg a hurkot: nincs skip-token, nincs bot-szűrés, nincs állapot-összevetés.

> **Szolgáltató-aszimmetria (fontos!).** GitHubon a `GITHUB_TOKEN`-nel végzett push
> **dokumentáltan nem indít új workflow-futást** — ott a hurok magától megtörik. Azure DevOps-on
> a build service push-ja **igenis újraindítja** a PR-validációt (csak a commit-üzenetbe tett
> `***NO_CI***` fogja vissza). Egy szolgáltató-specifikus viselkedésre **nem építhetünk közös
> szabályt**: ezért lett a teherhordó guard provider-független (`L15-D2`).

### 2.4 `G4` — A review nem kötődik a PR head SHA-jához

A `bs-merge` belépő kapuja:

```bash
python3 <platform-scripts-mappa>/validate-gate-check.py \
  specs/cycle-NN-<cycle-name> --review-only --require-ci-review
```

A `prompts/scripts/validate-gate-check.py` `check_review()` / `_check_one_review()` (`:397`,
`:423`) **két dolgot** mér: van-e lezáratlan `Must Fix`, és `<status:in_progress>`-on áll-e a
fejléc. **Azt nem, hogy a review melyik commitra készült.**

**Következmény:** a fejlesztő a zöld review után új commitot nyom a PR-re, és a `bs-merge` kapuja
**zöldnek látja a régi diffre készült review-t**. A `TR7` frissesség-elv a riportokra már él, a
review-ra nem.

Ugyanez a rés a `VP2` és a tényleges beolvasztás között: a `09c` megnézi a `mergeStateStatus`-t,
de nincs join arra, hogy a `post-merge/` kör **melyik fő-branch-SHA-val** futott.

### 2.5 `G5` — Az `auto-fix-loop` konfigurálható, de nem létezik

```
$ grep -rn "auto-fix-loop" prompts/ docs/ *.md | grep -v improve-list13 | wc -l
   (csak próza: 09b, 09c, implement-fixer, a 00 lang-blokkja és a docs)
```

- **Felajánlva:** `prompts/lang/{hu,en}/00-init-project.md` — `Failure handling: notify | auto-fix-loop`
- **Hivatkozva:** `09b-review.md` (2. szakasz 3. pont), `09c-merge.md` (*A `VP2` bukása* 4. pont),
  `agents-{hu,en}/implement-fixer.md`
- **Megvalósítva:** sehol. Nincs skill, nincs script, nincs belépő pont.

Amit egyik hivatkozás sem mond meg: **ki indítja** a hurkot a CI-n, **hol él az állapota** (a
`failure-counter.py` számlálói ma a `07` kör-mappájához kötöttek), **ki commitol** és **mit**, és
**hogyan lép ki** — a „`07` hurkának változatlan leállási korlátai" mondat egy olyan gépezetre
hivatkozik, ami a `07` orchestrátorában él, nem önállóan hívhatóan.

**Ez ma kitölthetetlen csekk:** a `00` felajánl egy értéket, amit bekapcsolva a rendszer nem tud
mást tenni, mint amit a `notify` ág tenne.

### 2.6 `G6` — Nincs időkorlát és írás-hatókör a gépi ágensre

`prompts/scripts/ci-run-skill.sh` `main()`:

```bash
  set +e
  eval "$cmd"
  local agent_rc=$?
  set -e
```

Se `timeout`, se a keletkezett diff hatókörének ellenőrzése. A `07` ágán a `contract-guard.py`
(VD3a) épp ezt az osztályt védi — *a javítás nem írhatja át a tesztelt szerződést* —, de a CI-ág
ágensére ma semmi hasonló nem fut. Egy `bs-review` futásnak elvileg **két fájlt** szabadna
írnia (`test-report/ci-code-review.md`, `cycle-status.md`); ezt semmi nem méri.

### 2.7 `G7` — Nincs egyetlen CI-preflight

Központosított futáshoz **legalább öt** dolog kell a futtatón:

| mi | honnan | ma ki ellenőrzi |
|---|---|---|
| az ágens CLI a PATH-on | telepítés | `--selftest` ✓ |
| az ágens hitelesítése (API-kulcs / szolgáltatás-fiók) | titok | részben (`CURSOR_API_KEY` figyelmeztetés) |
| `Notification secret (env var)` | titok | `notify.py` futáskor, `exit 2` |
| test manager token | titok | `test-manager.py --mode preflight`, de csak a teszt-körben |
| git push jog + PR-írási jog | a futtató identitása | **senki** |

A `--selftest` maga mondja ki a korlátját: *„A hitelesítést ez a selftest NEM tudja ellenőrizni…
Éles használat előtt futtasd le ezt a scriptet MAGÁN A CI-N is."* Ez becsületes, de a hiányzó
push-jog **az ágens-futás után**, a legdrágább ponton bukik.

### 2.8 `G8` — A `09d` visszaintegrálása rekurzív

`prompts/skills-hu/09d-dev-test.md` *4. Lezárás* 1. pont: a `-dev-test` ág bizonyítékát
*„integráld vissza a `conventions.md` `## Merge stratégia` szerint (PR vagy közvetlen merge)"*.

Központosított úton viszont a `PR submission: yes` **kötelező** (`L13-D1` érvényességi szabály),
tehát ez egy **újabb PR** — ami újraindítja a pipeline-t, és `bs-review`-t futtat egy
riport-only diffre. A kivétel sehol nincs kimondva.

### 2.9 `G9` — Párhuzamosság

A `CS4` szerint a `VP2` tesztjei a CI teszt-node-ján `compose`-zal felhúzott környezetben futnak.
Két ciklus PR-je egyszerre **ugyanazokat a portokat** kérné. A keretben nincs konkurencia-szabály,
és a `conventions.md` `## Portok` szekciója projekt-szintű, nem futás-szintű.

### 2.10 `G10` — Az `SDD mode` gépiesen nem hat semmire

A `ci-run-skill.sh` `rm_field()`-je három mezőt olvas: `CI agent`, `CI agent command` — az
`SDD mode`-ot **nem**. A `09c` `L13-D5` szerinti üzemmód-függése (izolált úton kötelező az `RD8`
megerősítés, központosítotton a PR elfogadása veszi át) **prózában** él, `<!-- INCLUDE -->`-dal;
semmi nem méri, melyik módban vagyunk.

### 2.11 `G11` — Az Azure DevOps nincs a szolgáltatók között

> `prompts/lang/hu/00-init-project.md:99` — „**Szolgáltató:** GitHub | Bitbucket Cloud |
> Bitbucket Server | GitLab | Lokális (nincs PR)"

A `09a` PR-nyitása `gh` / `glab` / „Bitbucket access-parancs" ágakat ismer
(`09a-create-pr.md:107-110`), a `09c` PR-állapot-kapuja ugyanígy (`09c-merge.md:49`). **Az
`az repos pr` sehol nincs.** Egy Azure DevOps pipeline tehát ma olyan projektnek szólna,
amelyben a `09a` meg sem tudta volna nyitni a PR-t.

### 2.12 A telepített scripts-mappa platformonként más

| platform | scripts-mappa |
|---|---|
| Claude Code | `.claude/scripts/` |
| Cursor | `.cursor/scripts/` |
| Antigravity | `.agents/scripts/` |
| Codex CLI | `.codex/scripts/` |
| GitHub Copilot | `.github/scripts/` |

(`berki-spec-directory-structure.md:162-166`.) A pipeline ezért **nem drótozhatja be** az
útvonalat: változóból kell jönnie.

---

## 3. A kanonikus pipeline-minták — EZEKET másold

> **⚠ FIGYELEM — EZEK A MINTÁK AZ `L15-D3`–`L15-D8` DÖNTÉSEK ELŐTT KÉSZÜLTEK (2026-09-23).**
> Még érvényes belőlük: a checkout-csapdák (`fetch-depth: 0`, a forrás-ág explicit checkoutja),
> a titok-tábla, a `BS_*` env-szerződés, az Azure `pr:` trigger korlátja és az időkorlátok.
> **Át kell írni belőlük** (a `C` csomag feladata):
> - a **két külön pipeline** (review és merge) helyett **egy kombinált futás** (`L15-D5`);
> - a verdikt nem a job eredménye, hanem egy **API-n kitett státusz a saját commitra** (`L15-D6`);
> - a `pull_request_review` trigger kiesik, mert a jóváhagyásra a **szolgáltató policy-je** vár (`L15-D3`);
> - a gépi identitás és a hozzá tartozó jogok (`L15-D8`).
>
> A minták a **4. szakasz lezárt döntéseire** épülnek, és feltételezik az ott leírt
> adapter-bővítést (opcionális ciklus-útvonal, `--resolve-cycle`, `BS_*` env-szerződés).
> **Amíg a 7. szakasz A és C csomagja nincs kész, ezek nem futtathatók.**

### 3.0 A közös szerződés — ez a rész platformfüggetlen

**A pipeline buta, az adapter okos.** A CI-nek egyetlen dolga van: előállítani a munkakönyvtárat
és a környezeti változókat, meghívni az adaptert, és a kilépő kódot verdiktté fordítani. Minden
szabály (melyik ciklus, melyik kapu, mikor kell ember) az adapterben és a skillekben él — így egy
ötödik szolgáltató bekötése **nem érinti a keretet**.

| env var | mit ad át | GitHub | Azure DevOps |
|---|---|---|---|
| `BS_BASE_REF` | a PR cél-branch-e | `github.base_ref` | `System.PullRequest.TargetBranch` |
| `BS_HEAD_SHA` | a PR **forrás**-commitja | `github.event.pull_request.head.sha` | `System.PullRequest.SourceCommitId` |
| `BS_HEAD_REF` | a PR forrás-ága | `github.event.pull_request.head.ref` | `System.PullRequest.SourceBranch` |
| `BS_SCRIPTS_DIR` | a telepített scripts-mappa | pipeline-változó (2.12) | pipeline-változó (2.12) |
| `BS_CONVENTIONS` | a `conventions.md` útvonala | opcionális | opcionális |

**Kilépő kód → verdikt (mindkét platformon azonos):**

| exit | jelentés | mit tegyen a pipeline |
|---|---|---|
| `0` | a determinisztikus kapuk zöldek | a job zöld |
| `1` | kapu-bukás (van bizonyíték a lemezen) | a job piros, a bizonyíték commitolva |
| `2` | **emberi döntés kell** (`*-questions.md`) | a job piros, **külön annotációval** — ez nem kódhiba |

A `2` azért piros, mert a PR-t **blokkolnia kell**: egy nyitott kérdés mellett a merge ugyanolyan
veszélyes, mint egy bukott kapu mellett. A megkülönböztetés az üzenetben van, nem a színben.

**Titkok** (a `conventions.md`-be csak a **nevük** kerül, sosem az értékük):

| titok | mire kell | hol állítod be |
|---|---|---|
| az ágens API-kulcsa (pl. `ANTHROPIC_API_KEY`, `CURSOR_API_KEY`) | a nem-interaktív ágens-futás | GitHub: repository secret · Azure: variable group (secret) |
| `BS_NOTIFY_WEBHOOK` (vagy a projekt saját neve) | `notify.py` | ugyanott |
| a test manager tokenje | `test-manager.py` | ugyanott, csak ha be van kapcsolva |
| push-jog a PR ágára | a bizonyíték visszacommitolása | GitHub: `permissions: contents: write` · Azure: a **build service** `Contribute` joga a repón |

### 3.1 GitHub Actions — `.github/workflows/berkispec-review.yml` (9b)

```yaml
name: berkispec — 9b review a PR-en

on:
  pull_request:
    types: [opened, synchronize, reopened]

# Egy PR-en egyszerre egy futás. A `cancel-in-progress: false` SZÁNDÉKOS: egy
# félbeszakított review részleges, de VALÓS bizonyítékot hagy a lemezen (RV-INC),
# és a fejléce `in_progress`-on marad — a megszakítás tehát nem olcsó, hanem drága.
concurrency:
  group: berkispec-review-${{ github.event.pull_request.number }}
  cancel-in-progress: false

permissions:
  contents: write        # a ci-code-review.md + cycle-status.md visszacommitolása
  pull-requests: write   # PR-komment / státusz

jobs:
  review:
    # Fork-ból érkező PR-re NEM fut: ott a titkok elvileg sem elérhetők, tehát az
    # ágens nem tudna hitelesíteni. Központosított SDD-ben a ciklus ága úgyis
    # ugyanabban a repóban él (a 09a a saját repójába push-ol).
    if: github.event.pull_request.head.repo.full_name == github.repository
    runs-on: ubuntu-latest
    timeout-minutes: 45          # G6 — a beragadt ágens ne egye meg a teljes keretet
    env:
      BS_SCRIPTS_DIR: .claude/scripts
      BS_BASE_REF: ${{ github.base_ref }}
      BS_HEAD_SHA: ${{ github.event.pull_request.head.sha }}
      BS_HEAD_REF: ${{ github.event.pull_request.head.ref }}
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      BS_NOTIFY_WEBHOOK: ${{ secrets.BS_NOTIFY_WEBHOOK }}

    steps:
      - uses: actions/checkout@v4
        with:
          # 🔴 KÉT CSAPDA EGYSZERRE:
          #  1. `pull_request` eseményen a checkout alapból a MERGE-COMMITOT hozza
          #     (`refs/pull/N/merge`), detached HEAD-en: arra nem lehet push-olni, és
          #     a SHA-ja minden futáskor más — egy SHA-alapú frissesség-kapu sosem
          #     egyezne vele. Ezért kérjük expliciten a PR FORRÁS-ÁGÁT.
          #  2. A `fetch-depth` alapból 1, így az `origin/<base>...HEAD` nem oldható
          #     fel — a ciklus-feloldás (L15-D1) néma hibába futna.
          ref: ${{ github.event.pull_request.head.ref }}
          fetch-depth: 0
          persist-credentials: true

      - name: git identitás
        run: |
          git config user.name  "berkispec-ci"
          git config user.email "berkispec-ci@users.noreply.github.com"

      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - uses: actions/setup-node@v4
        with: { node-version: '22' }

      - name: Az ágens CLI telepítése
        # A `conventions.md` `CI agent:` mezőjének megfelelő CLI. A `--selftest`
        # a következő lépésben megnézi, hogy tényleg a PATH-on van-e.
        run: npm install -g @anthropic-ai/claude-code

      - name: Előfeltételek — a DRÁGA futás ELŐTT (G7)
        run: |
          set -e
          bash "$BS_SCRIPTS_DIR/ci-run-skill.sh" --selftest
          bash "$BS_SCRIPTS_DIR/ci-run-skill.sh" --resolve-cycle
          # A push-jog kipróbálása ÍRÁS NÉLKÜL: ha ez bukik, a hiba itt derül ki,
          # nem egy negyvenperces ágens-futás után.
          git push --dry-run origin "HEAD:${BS_HEAD_REF}"

      - name: 9b — review a PR diffjén
        id: skill
        run: |
          set +e
          bash "$BS_SCRIPTS_DIR/ci-run-skill.sh" bs-review
          echo "rc=$?" >> "$GITHUB_OUTPUT"
          exit 0      # a verdiktet a következő lépés mondja ki

      - name: A bizonyíték visszacommitolása
        # `always()`: a BUKOTT kör bizonyítéka ugyanúgy a PR-re kell, mint a zöldé (CS6).
        # GitHubon a GITHUB_TOKEN-nel végzett push DOKUMENTÁLTAN nem indít új
        # workflow-futást, tehát itt nincs ön-trigger hurok (Azure-on van — lásd 2.3).
        if: always()
        run: |
          git add -A specs/
          git diff --cached --quiet && echo "nincs mit commitolni" && exit 0
          git commit -m "cycle: 9b-review bizonyíték (CI)"
          git push origin "HEAD:${BS_HEAD_REF}"

      - name: Verdikt
        run: |
          case "${{ steps.skill.outputs.rc }}" in
            0) echo "::notice::a determinisztikus kapuk zöldek — mehet a 9c" ;;
            1) echo "::error::kapu-bukás — a findingok a test-report/ci-code-review.md-ben"; exit 1 ;;
            2) echo "::error::EMBERI DÖNTÉS KELL — lásd a ciklusmappa *-questions.md fájlját"; exit 1 ;;
            *) echo "::error::ismeretlen kilépő kód"; exit 1 ;;
          esac
```

### 3.2 GitHub Actions — `berkispec-merge.yml` (9c)

```yaml
name: berkispec — 9c merge (VP2 + beolvasztás)

on:
  pull_request_review:
    types: [submitted]
  workflow_dispatch:

permissions:
  contents: write
  pull-requests: write

jobs:
  merge:
    # 🔴 A PR ELFOGADÁSA veszi át az RD8 kézi megerősítés szerepét (L13-D5).
    # Ezért ez a job KIZÁRÓLAG jóváhagyásra indul — és a 09c a saját kapujában
    # újra ellenőrzi a PR állapotát, mert egy esemény nem bizonyíték.
    if: github.event_name == 'workflow_dispatch' || github.event.review.state == 'approved'
    runs-on: ubuntu-latest
    timeout-minutes: 90          # a VP2 kör konténeres környezetet húz fel (CS4)
    env:
      BS_SCRIPTS_DIR: .claude/scripts
      BS_BASE_REF: ${{ github.event.pull_request.base.ref }}
      BS_HEAD_SHA: ${{ github.event.pull_request.head.sha }}
      BS_HEAD_REF: ${{ github.event.pull_request.head.ref }}
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}     # a `gh pr view` / `gh pr merge` hívásokhoz
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      BS_NOTIFY_WEBHOOK: ${{ secrets.BS_NOTIFY_WEBHOOK }}

    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.ref }}
          fetch-depth: 0
          persist-credentials: true

      - name: git identitás
        run: |
          git config user.name  "berkispec-ci"
          git config user.email "berkispec-ci@users.noreply.github.com"

      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - uses: actions/setup-node@v4
        with: { node-version: '22' }
      - run: npm install -g @anthropic-ai/claude-code

      - name: Előfeltételek
        run: |
          set -e
          bash "$BS_SCRIPTS_DIR/ci-run-skill.sh" --resolve-cycle
          docker compose version     # a VP2 konténeres környezete (CS4)

      - name: 9c — VP2 kör + beolvasztás
        id: skill
        run: |
          set +e
          bash "$BS_SCRIPTS_DIR/ci-run-skill.sh" bs-merge
          echo "rc=$?" >> "$GITHUB_OUTPUT"
          exit 0

      - name: A VP2 bizonyítéka a PR-re
        # 🔴 A BUKÁS a fontosabb eset: ilyenkor a fő branch ÉRINTETLEN marad, a PR
        # nyitva, és a `test-report/post-merge/` készlet a ciklus ágán látszik (L13-D14).
        if: always()
        run: |
          git add -A specs/
          git diff --cached --quiet && exit 0
          git commit -m "cycle: 9c-merge VP2 bizonyíték (CI)"
          git push origin "HEAD:${BS_HEAD_REF}"

      - name: Verdikt
        run: |
          case "${{ steps.skill.outputs.rc }}" in
            0) echo "::notice::beolvasztva — a VP2 zöld volt" ;;
            1) echo "::error::VP2 bukás — a fő branch érintetlen, a riport a PR-en"; exit 1 ;;
            2) echo "::error::EMBERI DÖNTÉS KELL — lásd a *-questions.md fájlt"; exit 1 ;;
          esac
```

### 3.3 GitHub Actions — `berkispec-dev-test.yml` (9d, opcionális)

```yaml
name: berkispec — 9d dev-teszt (VP3)

on:
  workflow_dispatch:
    inputs:
      cycle:
        description: "a ciklus mappája (üresen: feloldás a legutóbbi push diffjéből)"
        required: false
  # Automatikus indítás a beolvasztás után. A ciklus feloldásához a `github.event.before`
  # (a push ELŐTTI fő-branch-SHA) megy a BS_BASE_REF-be: az adapter a nem létező
  # `origin/<sha>` után CSUPASZ refként is megpróbálja feloldani, és az működik.
  # push:
  #   branches: [main]
  #   paths: ['specs/cycle-*/**']

permissions:
  contents: write

jobs:
  dev-test:
    runs-on: ubuntu-latest
    timeout-minutes: 120         # telepítés + valódi e2e kör
    env:
      BS_SCRIPTS_DIR: .claude/scripts
      BS_BASE_REF: ${{ github.event.before || github.ref_name }}
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      BS_NOTIFY_WEBHOOK: ${{ secrets.BS_NOTIFY_WEBHOOK }}
      TEST_MANAGER_TOKEN: ${{ secrets.TEST_MANAGER_TOKEN }}
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0, persist-credentials: true }

      - name: git identitás
        run: |
          git config user.name  "berkispec-ci"
          git config user.email "berkispec-ci@users.noreply.github.com"

      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - uses: actions/setup-node@v4
        with: { node-version: '22' }
      - run: npm install -g @anthropic-ai/claude-code

      - name: 9d — telepítés + VP3
        id: skill
        run: |
          set +e
          bash "$BS_SCRIPTS_DIR/ci-run-skill.sh" bs-dev-test ${{ inputs.cycle }}
          echo "rc=$?" >> "$GITHUB_OUTPUT"
          exit 0

      - name: Verdikt
        run: |
          case "${{ steps.skill.outputs.rc }}" in
            0) echo "::notice::a VP3 zöld — a ciklus lezárható" ;;
            1) echo "::error::VP3 bukás — a riport a test-report/dev-test/ alatt"; exit 1 ;;
            2) echo "::error::EMBERI DÖNTÉS KELL"; exit 1 ;;
          esac
```

### 3.4 Azure DevOps — `azure-pipelines/berkispec-review.yml` (9b)

```yaml
# 🔴 AZURE REPOS: A YAML `pr:` TRIGGERE NEM MŰKÖDIK Azure Repos Git repóra.
# A PR-validációt BRANCH POLICY-ként kell bekötni:
#   Repos → Branches → <fő branch> → ⋯ → Branch policies →
#   Build Validation → + → ez a pipeline · Trigger: Automatic · Requirement: Required
# (A `pr:` blokkot csak GitHub- és Bitbucket-forrású repóknál veszi figyelembe az
# Azure Pipelines. Ez a leggyakoribb „miért nem indul el" ok.)
trigger: none
pr: none

pool:
  vmImage: ubuntu-latest

variables:
  - group: berkispec-secrets        # ANTHROPIC_API_KEY, BS_NOTIFY_WEBHOOK, …
  - name: BS_SCRIPTS_DIR
    value: .claude/scripts

jobs:
  - job: review
    displayName: "9b — review a PR-en"
    timeoutInMinutes: 45            # G6
    steps:
      - checkout: self
        # 🔴 UGYANAZ A KÉT CSAPDA, MINT GITHUBON:
        #  1. a PR-build a `refs/pull/N/merge` MERGE-COMMITOT checkoutolja, detached
        #     HEAD-en — a visszapush-hoz a forrás-ágra kell állni (lásd a következő lépés);
        #  2. a `fetchDepth: 0` nélkül az `origin/<base>...HEAD` nem oldható fel.
        fetchDepth: 0
        persistCredentials: true     # enélkül nincs visszapush

      - script: |
          set -e
          git config user.name  "berkispec-ci"
          git config user.email "berkispec-ci@example.invalid"
          BRANCH="${SYSTEM_PULLREQUEST_SOURCEBRANCH#refs/heads/}"
          git switch "$BRANCH"
          echo "a forrás-ágon: $BRANCH ($(git rev-parse HEAD))"
        displayName: "git identitás + a PR forrás-ága"

      - task: UsePythonVersion@0
        inputs: { versionSpec: '3.12' }
      - task: NodeTool@0
        inputs: { versionSpec: '22.x' }

      - script: npm install -g @anthropic-ai/claude-code
        displayName: "Az ágens CLI telepítése"

      - script: |
          set -e
          bash "$BS_SCRIPTS_DIR/ci-run-skill.sh" --selftest
          bash "$BS_SCRIPTS_DIR/ci-run-skill.sh" --resolve-cycle
          git push --dry-run origin HEAD
        displayName: "Előfeltételek — a drága futás ELŐTT (G7)"
        env:
          BS_BASE_REF: $(System.PullRequest.TargetBranch)
          BS_HEAD_SHA: $(System.PullRequest.SourceCommitId)
          BS_HEAD_REF: $(System.PullRequest.SourceBranch)

      - script: |
          set +e
          bash "$BS_SCRIPTS_DIR/ci-run-skill.sh" bs-review
          echo "##vso[task.setvariable variable=skillRc]$?"
          exit 0
        displayName: "9b — review a PR diffjén"
        env:
          BS_BASE_REF: $(System.PullRequest.TargetBranch)
          BS_HEAD_SHA: $(System.PullRequest.SourceCommitId)
          BS_HEAD_REF: $(System.PullRequest.SourceBranch)
          ANTHROPIC_API_KEY: $(ANTHROPIC_API_KEY)
          BS_NOTIFY_WEBHOOK: $(BS_NOTIFY_WEBHOOK)

      - script: |
          set -e
          git add -A specs/
          git diff --cached --quiet && echo "nincs mit commitolni" && exit 0
          # 🔴 A `***NO_CI***` OPTIMALIZÁCIÓ, NEM VÉDELEM. Azure DevOps-on a build
          # service push-ja ÚJRAINDÍTANÁ a PR-validációt (GitHubon a GITHUB_TOKEN-es
          # push nem indít semmit — lásd 2.3). A teherhordó szabály attól függetlenül
          # a SHA-kötött frissesség (L15-D2): ez csak megspórol egy felesleges buildet.
          git commit -m "cycle: 9b-review bizonyíték (CI) ***NO_CI***"
          git push origin "HEAD:${SYSTEM_PULLREQUEST_SOURCEBRANCH#refs/heads/}"
        displayName: "A bizonyíték visszacommitolása"
        condition: always()

      - script: |
          case "$(skillRc)" in
            0) echo "a determinisztikus kapuk zöldek — mehet a 9c" ;;
            1) echo "##vso[task.logissue type=error]kapu-bukás — lásd a ci-code-review.md-t"; exit 1 ;;
            2) echo "##vso[task.logissue type=error]EMBERI DÖNTÉS KELL — lásd a *-questions.md fájlt"; exit 1 ;;
            *) echo "##vso[task.logissue type=error]ismeretlen kilépő kód"; exit 1 ;;
          esac
        displayName: "Verdikt"
        condition: always()
```

### 3.5 Azure DevOps — `azure-pipelines/berkispec-merge.yml` (9c)

> **🔴 Azure DevOps-on nincs natív „PR jóváhagyva" pipeline-trigger.** Három becsületes út van,
> és mindhárom ugyanoda fut be (a `09c` a saját kapujában úgyis ellenőrzi a PR állapotát):
> 1. **kézi indítás** paraméterrel (az alábbi minta — a legegyszerűbb, és a jóváhagyás
>    emberi döntése amúgy is a PR-en történt);
> 2. **service hook** a *Pull request updated* eseményre, ami a pipeline REST API-ját hívja;
> 3. **auto-complete** a PR-en: a policy-k teljesülésekor az Azure maga olvaszt be — ez viszont
>    **kiveszi a `VP2`-t a merge elé** (`L13-D14`), tehát központosított SDD-ben **nem** járható.

```yaml
trigger: none
pr: none

parameters:
  - name: cyclePath
    displayName: "A ciklus mappája (üresen: feloldás a PR diffjéből)"
    type: string
    default: ""
  - name: sourceBranch
    displayName: "A ciklus ága"
    type: string

pool:
  vmImage: ubuntu-latest

variables:
  - group: berkispec-secrets
  - name: BS_SCRIPTS_DIR
    value: .claude/scripts

jobs:
  - job: merge
    displayName: "9c — VP2 kör + beolvasztás"
    timeoutInMinutes: 90
    steps:
      - checkout: self
        fetchDepth: 0
        persistCredentials: true

      - script: |
          set -e
          git config user.name  "berkispec-ci"
          git config user.email "berkispec-ci@example.invalid"
          git switch "${{ parameters.sourceBranch }}"
        displayName: "git identitás + a ciklus ága"

      - task: UsePythonVersion@0
        inputs: { versionSpec: '3.12' }
      - task: NodeTool@0
        inputs: { versionSpec: '22.x' }
      - script: npm install -g @anthropic-ai/claude-code
        displayName: "Az ágens CLI telepítése"

      - script: |
          set -e
          docker compose version          # a VP2 konténeres környezete (CS4)
          bash "$BS_SCRIPTS_DIR/ci-run-skill.sh" --resolve-cycle
        displayName: "Előfeltételek"
        env:
          BS_HEAD_REF: ${{ parameters.sourceBranch }}

      - script: |
          set +e
          bash "$BS_SCRIPTS_DIR/ci-run-skill.sh" bs-merge ${{ parameters.cyclePath }}
          echo "##vso[task.setvariable variable=skillRc]$?"
          exit 0
        displayName: "9c — VP2 + merge"
        env:
          BS_HEAD_REF: ${{ parameters.sourceBranch }}
          ANTHROPIC_API_KEY: $(ANTHROPIC_API_KEY)
          BS_NOTIFY_WEBHOOK: $(BS_NOTIFY_WEBHOOK)
          # az `az repos pr` hívásokhoz (PR-állapot kapu, beolvasztás):
          AZURE_DEVOPS_EXT_PAT: $(System.AccessToken)

      - script: |
          set -e
          git add -A specs/
          git diff --cached --quiet && exit 0
          git commit -m "cycle: 9c-merge VP2 bizonyíték (CI) ***NO_CI***"
          git push origin "HEAD:${{ parameters.sourceBranch }}"
        displayName: "A VP2 bizonyítéka a PR-re"
        condition: always()

      - script: |
          case "$(skillRc)" in
            0) echo "beolvasztva — a VP2 zöld volt" ;;
            1) echo "##vso[task.logissue type=error]VP2 bukás — a fő branch érintetlen"; exit 1 ;;
            2) echo "##vso[task.logissue type=error]EMBERI DÖNTÉS KELL"; exit 1 ;;
          esac
        displayName: "Verdikt"
        condition: always()
```

### 3.6 Azure DevOps — `azure-pipelines/berkispec-dev-test.yml` (9d, opcionális)

```yaml
# A beolvasztás után indul a fő branch-en. A ciklus feloldásához a push ELŐTTI
# állapot kell base-ként: az Azure ezt a `Build.SourceVersion` előzményeként adja,
# ezért itt a ciklus-útvonalat EXPLICITEN adjuk át (a legkevesebb varázslat).
trigger: none
pr: none

parameters:
  - name: cyclePath
    displayName: "A ciklus mappája"
    type: string

pool:
  vmImage: ubuntu-latest

variables:
  - group: berkispec-secrets
  - name: BS_SCRIPTS_DIR
    value: .claude/scripts

jobs:
  - job: devtest
    displayName: "9d — telepítés + VP3"
    timeoutInMinutes: 120
    steps:
      - checkout: self
        fetchDepth: 0
        persistCredentials: true
      - script: |
          git config user.name  "berkispec-ci"
          git config user.email "berkispec-ci@example.invalid"
        displayName: "git identitás"
      - task: UsePythonVersion@0
        inputs: { versionSpec: '3.12' }
      - task: NodeTool@0
        inputs: { versionSpec: '22.x' }
      - script: npm install -g @anthropic-ai/claude-code
        displayName: "Az ágens CLI telepítése"
      - script: |
          set +e
          bash "$BS_SCRIPTS_DIR/ci-run-skill.sh" bs-dev-test "${{ parameters.cyclePath }}"
          echo "##vso[task.setvariable variable=skillRc]$?"
          exit 0
        displayName: "9d — VP3"
        env:
          ANTHROPIC_API_KEY: $(ANTHROPIC_API_KEY)
          BS_NOTIFY_WEBHOOK: $(BS_NOTIFY_WEBHOOK)
          TEST_MANAGER_TOKEN: $(TEST_MANAGER_TOKEN)
      - script: |
          case "$(skillRc)" in
            0) echo "a VP3 zöld — a ciklus lezárható" ;;
            1) echo "##vso[task.logissue type=error]VP3 bukás"; exit 1 ;;
            2) echo "##vso[task.logissue type=error]EMBERI DÖNTÉS KELL"; exit 1 ;;
          esac
        displayName: "Verdikt"
        condition: always()
```

---

## 4. Lezárt döntések

### `L15-D1` — A ciklust az adapter oldja fel, a PR DIFFJÉBŐL (2026-09-23)

**A döntés.** A `ci-run-skill.sh` második argumentuma **opcionálissá** válik. Ha hiányzik, az
adapter a PR diffjéből oldja fel a ciklust. Új, önálló mód: `--resolve-cycle`, ami csak kiírja
a feloldott útvonalat.

```
ci-run-skill.sh <skill-név> [<ciklus-útvonal>]
ci-run-skill.sh --resolve-cycle
```

**Miért nem a branch-névből.** Mert a keret maga mondja ki, hogy a branch-név **konfigurálható**
(`BD8`: Jira-prefix, szervezeti szabály, pointer), a mappanév viszont mindig tiszta — és a keret
végig **mappa → branch** irányban képez le (2.2). A branch-alapú feloldás egy Jira-prefixes
projektben az első éles PR-en dőlne el.

**Miért nem a PR címéből/törzséből.** Ember írja (elgépelhető), és a kiolvasásához
szolgáltató-CLI kell — `gh` / `glab` / `az` / Bitbucket REST: négy ág, négy auth. A diff **csak
gitet** igényel.

**Miért ez illik a kerethez.** A diff **bizonyíték**, nem önbevallás — ugyanaz az elv, mint
„a verdikt a determinisztikus kapuktól jön, nem az ágenstől" (`L13-D13`) és a generált
`cycle-status.md`-nél: *rendering a bizonyítékból, sosem forrás* (`L13-D9`).

**Miért az adapterben, és nem a pipeline YAML-ben.** Mert a szabály különben három-négy helyen
élne (GitHub · Azure · GitLab · Bitbucket), eltérő alakban — pontosan az `RP1` tanulsága. Így a
pipeline buta marad: `ci-run-skill.sh bs-review`.

**A szabály:**

1. `git diff --name-only origin/<base>...HEAD` → a `specs/cycle-*/` prefixek halmaza;
2. **pontosan egy** → ez a ciklus útvonala;
3. **nulla** → `exit 2` (ez nem berkispec-ciklus PR-je — a pipeline szűrőjének ki kellett volna
   zárnia; csendben zöldre engedni a legdrágább hiba);
4. **több** → `exit 2` + a lista. Ez egyben kimondott policy: **EGY PR = EGY CIKLUS**;
5. **cross-check, nem forrás:** ha a branch-név hordoz `cycle-NN`-t, az egyezzen a feloldott
   mappáéval; eltérésnél `exit 2` (rossz cél-branchre nyitott PR).

**🔴 A három pont (`...`) kötelező.** A `09a` és a `09c` behozza a fő branch-et a ciklus ágába;
két ponttal (`..`) a fő branch **saját** változásai is bejönnének — köztük **más ciklusok
`specs/` mappái** —, és a feloldás azonnal kétértelmű lenne.

**A base-ref forrása** (ebben a sorrendben): `BS_BASE_REF` env → `origin/HEAD` symbolic ref →
`main`. A `conventions.md` `## Merge stratégia` szekcióját **szándékosan nem** olvassa: annak a
neve **projekt-nyelvű**, míg a `## Review and merge` mezői angol literálok (`L13-D2`) — az
adapter ma is csak az utóbbit tudja olvasni.

#### Mérés — a prototípus, eldobható repóban (2026-09-23)

A feloldó logikát egy eldobható git-repóban végigpróbáltam. **A prototípus kódja nincs
commitolva** (a `ci-run-skill.sh` érintetlen); a mérés eredménye:

| # | eset | várt | mért |
|---|---|---|---|
| 1 | `JIRA-4711-valami-mas-nev` ág, egy ciklusmappa a diffben | feloldja | `specs/cycle-31-foo`, `exit 0` ✓ |
| 2 | két ciklusmappa a diffben | `exit 2` + lista | `HIBA: a diff 2 ciklusmappát érint — EGY PR = EGY CIKLUS`, `exit 2` ✓ |
| 3 | a fő branch előrement **másik ciklus** mappájával, majd merge a ciklus ágába | csak a sajátját adja | `specs/cycle-31-foo`, `exit 0` ✓ — **a három pont működik** |
| 4 | `feature/cycle-99-tevedes` ág, de a diff `cycle-31` | `exit 2` | `HIBA: a branch-név cycle-99-et mond, a diff viszont specs/cycle-31-foo`, `exit 2` ✓ |
| 5 | `hotfix/urgent` ág, nincs ciklusmappa a diffben | `exit 2` | `HIBA: … egyetlen specs/cycle-*/ mappát sem érint`, `exit 2` ✓ |

A 3. eset a legfontosabb: **ez az, amit két ponttal elrontottunk volna**, és ami csak akkor
derült volna ki, amikor két ciklus fut párhuzamosan.

### `L15-D2` — A CI ön-trigger hurkát SHA-kötött frissesség töri meg (2026-09-23)

> **🔴 FELÜLÍRVA ugyanaznap az `L15-D6` által.** A kombinált pipa és az API-n kitett státusz
> mindkét problémát megoldja, amire ez a döntés született: az ön-trigger hurkot (nem kell
> CI-t triggerelő token, mert a pipa nem a futás mellékterméke) és a `G4` elavulást (az új
> push úgyis érvényteleníti a pipát, mert az a committhoz kötődik). **A forrás-SHA szabály
> így nem kötelező** — opcióként megmarad, ha később mégis kelleni fog (pl. hogy egy
> `specs/`-only push ne indítson teljes kört). Az indoklás azért marad itt, mert a csapdák
> (merge-commit checkout, `BS_HEAD_SHA`) változatlanul érvényesek.

**A probléma.** A `09b` és a `09c` a PR ágára commitol és push-ol (2.3), ami újraindítja a
pipeline-t. Ugyanez a rés fordítva is nyitva van: egy zöld review után érkező fejlesztői commit
után a `bs-merge` kapuja **a régi diffre készült review-t** látja zöldnek (2.4, `G4`).

**A döntés.** A `ci-code-review.md` **fejléce hordozza a review-zott commit SHA-ját**, és ezt
két helyen használjuk:

1. az **adapter** az ágens indítása **előtt** összeveti a jelenlegi head SHA-val — egyezés esetén
   `exit 0` („már lefutott erre a SHA-ra"), az ágens el sem indul;
2. a **`validate-gate-check.py --require-ci-review`** ugyanezt méri a `bs-merge` belépő kapujában
   — ezzel zárul a `G4`.

**Miért nem skip-token (`[skip ci]` / `***NO_CI***`).** Mert az csak a **runner indulását** fogja
vissza, a **frissességről semmit nem mond**: egy emberi push után a régi review továbbra is
zöldnek látszana. A skip-token így is használható **optimalizációként** (a 3.4 Azure-mintában
ott is van), de a teherhordó szabály a SHA.

**Miért nem pipeline-szintű szűrő.** Mert szolgáltatónként más alakban élne (2.3: GitHubon a
`GITHUB_TOKEN`-es push eleve nem triggerel, Azure-on igen) — a szabály négy helyen, négyféleképp.

**🔴 A csapda, ami enélkül elnyelné az egészet.** `pull_request` eseményen a GitHub (és PR-buildben
az Azure) **egy merge-commitot checkoutol** (`refs/pull/N/merge`), aminek a SHA-ja **minden
futáskor más**. Ott a `git rev-parse HEAD` nem a PR head-je, tehát az összevetés sosem egyezne, és
a guard **sosem fogna**. Ezért:
- a pipeline **expliciten a forrás-ágat checkoutolja** (3.1), és
- átadja a `BS_HEAD_SHA`-t (`github.event.pull_request.head.sha` / `System.PullRequest.SourceCommitId`).

**Ki írja a mezőt.** A **skill** (`09b` *Lezárás*), **nem** a `reviewer` agent. Így az agent
kontraktusa érintetlen marad (`RV-INC` inkrementális írás változatlan), és a SHA-t úgyis a
skill/adapter tudja. Ez a meta-prompt **6. ellenőrzési pontja**: egy elcsúszott agent-kontraktus
nyelvtanilag hibátlan promptot hagy maga után, amit egyetlen kapu sem fog meg.

**Ripple** (a 7. szakasz B csomagja): `lang/status-keys.json` (**mindkét** nyelvi szelet) →
`skills-{hu,en}/09b-review.md` → `validate-gate-check.py` → `ci-run-skill.sh`. Az új mezőnév
**előbb kulcs a JSON-ba, csak utána token a promptban**.

### `L15-D3` — A „mehet tovább?" választ a SZOLGÁLTATÓ adja, nem a `conventions.md` (2026-09-23)

**A döntés.** A ciklusvég nem azt kérdezi, hogy *„elfogadták-e a PR-t"*, hanem hogy
*„beolvasztható-e **most**"* — és ezt a szolgáltatótól kérdezi:

- **GitHub:** `gh pr view --json mergeStateStatus,statusCheckRollup` — a `CLEAN` azt jelenti,
  hogy minden kötelező check zöld **és** a szükséges jóváhagyások megvannak;
- **Azure DevOps:** a PR policy-kiértékelések állapota (`az repos pr show`, `mergeStatus` +
  policy evaluations).

**Miért nem a `conventions.md`.** Két ok:
1. a branch policy a **kikényszeríthető** szabály — ha a `conventions.md` azt mondaná
   „nem kell jóváhagyás", a szerver viszont megköveteli, a lánc **minden ciklusban az utolsó
   lépésnél bukna**, a legdrágább ponton;
2. ugyanaz a szabály két helyen **szétcsúszik** — a keret saját `7/m` tanulsága.

**Viszonya az `L13-D5`-höz: nem felülírja, hanem általánosítja.** A mai `09c` kapu
(`reviewDecision: APPROVED` → különben STOP) bedrótozza, hogy **emberi** pipa kell. Az új
kérdésfeltevésben az emberi jóváhagyás **egy pipa a többi között**: ha a szervezet megköveteli,
a folyamat vár rá; ha nem, a gépi pipa után rögtön mehet. A ciklusvég **egyik esetben sem dönt
a policy helyett** — csak megkérdezi.

### `L15-D4` — A merge utáni tesztek PR-checkként futnak, MINDEN push-ra (2026-09-23)

**A döntés.** A merge utáni tesztkör (`VP2`) nem a jóváhagyás **után**, külön fázisban fut,
hanem **PR-ellenőrzésként** — és újrafut minden új push-ra. **Ez szándékos:** új kódhoz új
bizonyíték kell.

**Miért működik ez együtt az `L13-D14`-gyel** (*a `VP2` a fő branch-re juttatás ELŐTTI kapu, a
friss fő branch-csel egyesített kódon*): **mindkét szolgáltató alapból a MERGE-COMMITOT építi**
PR-ellenőrzéskor (GitHub: `refs/pull/N/merge`, Azure ugyanígy), tehát a PR-check **eleve az
egyesített állapotot** teszteli. Amit korábban „checkout-csapdának" neveztünk, az itt pont a
kívánt viselkedés.

**Két szerep, két különböző checkout — ezt nem szabad összekeverni:**

| szerep | mit checkoutol | miért |
|---|---|---|
| **kódreview** (`09b`) | a PR **forrás-ágát**, expliciten | mert bizonyítékot push-ol vissza, és az ág saját változásait nézi |
| **merge utáni tesztek** (`VP2`) | az **alapértelmezett merge-commitot** | mert az egyesített állapotot kell bizonyítania |

**Policy-feltétel.** Hogy az „egyesített állapot" tényleg a **friss** maint jelentse: GitHubon
*Require branches to be up to date before merging*; Azure-on a Build validation policy alapból
újraértékel, ha a target branch elmozdul.

**Az ára, kimondva.** A tesztkör minden push-ra lefut, nem csak a végén — konténeres környezet,
`compose`, lassú. Az `RM11` mező (*Skip post-merge tests if master unchanged*) ezen csak részben
segít, mert itt a **branch** változik, nem a main. A Felhasználó ezt tudva vállalta:
*„direkt jó, ha az új PR push-ra megint lefut, fusson is"*.

### `L15-D5` — EGY közös gépi pipa: `berkispec/review-and-test-runner` (2026-09-23)

**A döntés.** A kódreview és a merge utáni tesztek **ugyanabban a futásban**, sorban mennek, és
a végén **egyetlen** gépi pipa kerül a PR-re:

```
berkispec/review-and-test-runner    ✓ / ✗
```

A futáson belül a sorrend **fail-fast**: ha a review bukik, a tesztkör **el sem indul** — nincs
értelme konténer-időt égetni egy olyan változatra, amit úgyis át kell dolgozni.

**Miért egy és nem kettő.** Mert a két pipa **körkörösségbe futna**: a tesztek pipája kellene a
beolvaszthatósághoz, de a tesztek csak akkor indulhatnának, ha a PR már beolvasztható. Egy közös
pipa ezt megszünteti — és ez teszi lehetővé az `L15-D6`-ot is: **a pipa azért kerülhet a végére,
mert addigra már minden bizonyíték commitolva van.**

**Az ára:** a PR felületén nem látszik külön, melyik fele bukott. A riport és a job-log megmondja,
és az értesítés is ezt hordozza.

### `L15-D6` — A pipát a job teszi ki, API-n, a SAJÁT commitjára (2026-09-23)

**A probléma, amit megold.** A kötelező check a **committhoz** kötődik, nem a PR-hez. A ciklusvég
viszont a saját futása végén **megváltoztatja azt a commitot**, amire a pipát kapná — mert a
riportot visszacommitolja (`CS6`). Ebből két rossz vég lenne:

- **GitHubon** a beépített tokennel végzett push **nem indít workflow-t** (ez a végtelen hurok
  elleni védelem) → az új head-commitra **soha nem érkezik pipa** → a PR **beragad**
  (*„Expected — Waiting for status to be reported"*);
- **Azure DevOps-on** a push **újraindítja** a validációt → a kör **pörög**.

**A döntés.** A verdikt **ne a futás mellékterméke legyen**, hanem egy önálló rekord, amit a job
**expliciten ír ki API-n, arra a SHA-ra, amit ő hozott létre**:

```
1. push                        → head = A, indul a futás
2. kódreview                   (bukik → ugrás a 4-re)
3. merge utáni tesztek
4. a bizonyíték commitolása    → head = B
5. a pipa KIÍRÁSA a B commitra → a PR beolvasztható
```

```bash
# GitHub — Commit Status API
NEW_SHA=$(git rev-parse HEAD)
gh api -X POST "repos/$OWNER/$REPO/statuses/$NEW_SHA" \
  -f state=success -f context=berkispec/review-and-test-runner \
  -f description="review zöld, merge utáni tesztek zöldek"
```

```bash
# Azure DevOps — PR Status API (genre/name páros)
# POST .../pullRequests/{id}/statuses
#   {state, context: {genre: "berkispec", name: "review-and-test-runner"}, targetUrl}
```

**🔴 Két kötelező kiegészítés:**

1. **A pipát akkor is ki kell tenni, ha a job elszáll.** Ha a futás timeoutol vagy összeomlik és
   nincs státusz, a PR **némán blokkolva marad** — se zöld, se piros. Kell egy `always()` /
   `condition: always()` lépés, ami bukás-státuszt tesz ki.
2. **Verseny:** ha a fejlesztő a 4. és 5. lépés között push-ol (head = `C`), a pipa a `B`-re
   kerül, a head viszont `C`. **Ez helyes** — új kódhoz új review kell —, és magától gyógyul,
   mert a `C` push új futást indít. Tudni kell viszont, hogy a PR egy körig „hiányzó pipával" áll.

**Amit ez megspórol:** nem kell CI-t triggerelő token (PAT / App token a push-hoz), és nem kell a
forrás-SHA szabály sem — mindkettő az `L15-D2` kerülő útja volt ugyanerre a problémára.

### `L15-D7` — A kötelező check NEVET követel, nem futást (2026-09-23)

Az `L15-D6` csak akkor működik, ha a branch policy **a státusz nevét** követeli meg, nem azt,
hogy „a workflow lefusson":

| | ma tipikusan | ehhez kell |
|---|---|---|
| **GitHub** | a workflow-job maga a check, a kiváltó commiton | branch protection a **`berkispec/review-and-test-runner` context-névre** (Commit Status API) |
| **Azure DevOps** | *Build validation* policy | **Status policy** (külső szolgáltatás státusza), `berkispec` genre-rel |

Ez pont az a mechanizmus, amit ezekre kitaláltak: **a külső rendszer mondja ki a verdiktet, nem a
build lefutásának ténye.** Ugyanaz, mint a keret `L13-D13` elve, csak a szolgáltató felületén.

> **A státusznév mindkét platformon AZONOS lehet** (`berkispec/review-and-test-runner`) — ez a
> közös nevező, és ez kerül a branch policy-be. A dokumentáció ezt a nevet rögzítse.

### `L15-D8` — Gépi identitás, licenc nélkül, mindkét platformon (2026-09-23)

A CI-ben futó ciklusvég **ne egy fejlesztő nevében** commitoljon és pipáljon — a központosított út
auditálhatóságának éppen ez a lényege. **Követelmény: a gépi entitás NEM foglalhat licencet.**

| | GitHub | Azure DevOps |
|---|---|---|
| **választott megoldás** | **GitHub App** (pl. `berkispec`) | **beépített Build Service identitás** (`$(System.AccessToken)`) |
| megjelenés | `berkispec[bot]` | `<Projekt> Build Service (<org>)` |
| **ikon** | ✅ az App feltöltött logója | ❌ nincs |
| licenc | nem fogyaszt seatet | nem tag, tehát nem fogyaszt licencet |
| token | telepítési token, óránként lejár | a pipeline tokenje |

**🔴 A service principal / managed identity utat SZÁNDÉKOSAN elvetettük:** az Azure DevOps ezeket
hozzáférési szinttel (Stakeholder / Basic) veszi fel a szervezetbe, ugyanúgy, mint a
felhasználókat — vagyis **Basic szinten licenc-tétel lehet**. A pontos billing-viselkedést a
bevezetéskor ellenőrizni kell; a build service viszont **biztosan ingyenes**, mert nem tag, hanem
a projekt saját szolgáltatás-identitása.

**Amit be kell állítani Azure-on** (Project Settings → Repositories → Security, a
`<Projekt> Build Service` principalra):

| jog | mire kell |
|---|---|
| **Contribute** | a bizonyíték push-olása a PR-ágra |
| **Contribute to pull requests** | a PR-státusz (pipa) és a kommentek |

Plusz: a pipeline adja ki a tokent a scriptnek (`SYSTEM_ACCESSTOKEN: $(System.AccessToken)`), és
az org szintű **Limit job authorization scope** ne zárja ki a repót.

**A felismerhetőség három forrása** (GitHubon mind a három, Azure-on az alsó kettő):
1. az **App logója** a check mellett;
2. a **commit szerzője** — ez **szabad szöveg** a commit-objektumban, függetlenül attól, ki
   push-olt: `git config user.name "berkispec CI"`;
3. a **státusz neve** (`berkispec/review-and-test-runner`).

---

## 5. Amit ez a kör NEM érint (előzetes anti-lista)

- **A `07` (`VP1`) tartalma és kapui** — a `CS2` a futtatási környezetet változtatja, nem a
  `reviewer` agent szerződését (ugyanaz az anti-tétel, mint a `list13` 7. szakaszában).
- **A `05` analyze hurka**, a `08` DS22/TC8/LD5 kapui.
- **A `D8`/`KT6` bizonyíték-tűzfal elve** — a CI-ben keletkező riport ugyanúgy a ciklus
  mappájába megy, a `test-runs/` fa érintetlen.
- **A `## Merge stratégia` meglévő mezői** — az Azure DevOps mint **szolgáltató** (`G11`) új
  érték, nem új mezőkészlet.
- **A quick-flow** (`7/o`) — a `bs-quick-flow` a `L13-D16` szerint a merge-ágba fut be; ha a
  központosított ág változik, **az ő belépője változatlan marad**. (Ellenőrizendő a
  végrehajtáskor, de előzetesen nem várunk ripple-t.)
- **A `docs/` fa háromrétegű szerkezete** (`list14`) — új témaoldal nem nyílik, a meglévő
  `platform-integration.md` bővül.

---

## 6. Nyitott kérdések — ezek még a Felhasználóra várnak

### `Q1` — Hol legyen a pipeline-minták helye, és telepítse-e a telepítő?

A 3. szakasz mintái ma **ebben a dokumentumban** élnek. Három út:
- **(a)** önálló mappa a repóban (pl. `prompts/ci/github-actions/` + `prompts/ci/azure-devops/`),
  amit a telepítő **nem** másol — a felhasználó bemásolja;
- **(b)** ugyanez, de a telepítő **bemásolja** a célprojektbe (új fájloszály a
  `berki-spec-directory-structure.md`-ben, és tisztázandó, kié a fájl, ha a CI-csapat is
  hozzányúl);
- **(c)** a `00-init-project` **generálja** a `conventions.md` mezőiből.

### `Q2` — Az Azure DevOps mint szolgáltató (`G11`)

Ez a kör vegye-e fel az `Azure DevOps`-ot a `00` szolgáltató-listájába, és írja-e meg az
`az repos pr create` / `az repos pr show` / `az repos pr update --status completed` ágakat a
`09a`/`09c`-ben? Enélkül az Azure-pipeline olyan projektnek szól, amelyben a `09a` meg sem
tudta volna nyitni a PR-t.

### ~~`Q3` — Ki commitolja a CI-ben keletkezett bizonyítékot?~~ — **LEZÁRVA (2026-09-23)**

> **A válasz az `L15-D6`-ból következik: a futás commitol, még a pipa kiírása ELŐTT.** Nincs
> kettős tulajdonlás: a sorrend köti meg — előbb bizonyíték, utána verdikt. A skill prózájából
> a „commitold és küldd fel” lépés ettől még nem esik ki: lokális, interaktív futásban az
> egyetlen commitoló. Az alábbi eredeti szöveg a döntés nyoma.

#### Az eredeti kérdés

Ma a **skill** (`09b`/`09c` *Lezárás*). A 3. szakasz mintái **biztonsági hálóként** is
commitolnak (`if: always()` / `condition: always()`), mert egy elszállt ágens nem jut el a
`git push`-ig — a bukott kör bizonyítéka viszont pont akkor a legfontosabb (`CS6`). **Kettős
tulajdonlás:** vagy a skillből vesszük ki, vagy kimondjuk, hogy a pipeline-é a *fallback*, és
a „nincs mit commitolni" ág a normális eset.

### `Q4` — Az `auto-fix-loop` (`G5`) belefér-e ebbe a körbe?

Ez a legnagyobb önálló darab: belépő pont, állapot-tárolás a CI-n, a `07` leállási korlátainak
újrahasznosítása, eszkaláció. Alternatíva: **ebben a körben töröljük** a `Failure handling`
mező `auto-fix-loop` értékét (a `00` ne ajánlja fel), és külön kör építse ki — egy nem létező
opció felajánlása rosszabb, mint a hiánya.

### `Q5` — A `G6` írás-hatókör kapuja

Legyen-e a CI-ágensre „csak ezeket a fájlokat írhattad" ellenőrzés (a `contract-guard.py`
mintájára), vagy elég az időkorlát? A `bs-review` elvileg **két fájlt** írhat
(`test-report/ci-code-review.md`, `cycle-status.md`).

### `Q6` — A `G8` (rekurzív `09d`) és a `G9` (párhuzamosság)

Belefér-e ebbe a körbe, vagy külön tételek? A `G8` megoldása valószínűleg egy kimondott kivétel
a `09d` lezárásában; a `G9`-é egy konkurencia-mező a `conventions.md`-ben.

---

### `Q7` — Melyik berkispec-verziót telepíti a CI?

A lánc 2. lépése telepíti a keretet a CI-futtatóra. Ha ez a **master**, akkor a CI **más
keretverzióval** futtathatja a ciklusvéget, mint amivel a fejlesztő dolgozott — a keret pedig
hétről hétre változik. **Javaslat:** a pipeline **taget** húzzon, és a tag a `conventions.md`-ben
legyen rögzítve (új mező). Eldöntendő: legyen-e ilyen mező, és a `00` ellenőrizze-e.

> **Mért háttér:** az eszköz-mappák (`.claude/`, `.agents/`, …) a célprojektben
> `worktree-setup.py:8` szerint **hol commitálva vannak, hol gitignore-olva** — projektfüggő.
> A CI tehát nem feltételezheti egyiket sem: a telepítést **mindig** el kell végezni.

## 7. Végrehajtási csomagok — VÁZLAT (a kör a `Q1`–`Q7` lezárásakor indul)

| csomag | mi | érinti |
|---|---|---|
| **A** | `L15-D1` — ciklus-feloldás az adapterben (`--resolve-cycle`, opcionális 2. argumentum, `BS_*` env-szerződés) | `prompts/scripts/ci-run-skill.sh` |
| **B** | `L15-D6`/`L15-D7` — a pipa kiírása API-n (GitHub Commit Status · Azure PR Status), `always()` bukás-ággal | **ÚJ:** `ci-status.sh` (vagy a `ci-run-skill.sh` új módja) |
| ~~**B′**~~ | ~~`L15-D2` — SHA-kötött frissesség~~ — **elhagyva**, az `L15-D6` kiváltotta; opcionálisan később | ~~`status-keys.json` → `09b-review.md` → `validate-gate-check.py`~~ |
| **C** | A pipeline-minták **átírása** a kombinált modellre (`L15-D4`–`L15-D8`) és kihelyezése (`Q1` szerint) + a `--selftest` bővítése a push-jog és a státusz-írási jog próbájával (`G7`) | a 3. szakasz mintái → új mappa + `ci-run-skill.sh` |
| **C′** | A gépi identitás beállítási receptje (`L15-D8`): GitHub App létrehozása + logó, Azure Build Service jogok, branch policy a státusznévre (`L15-D7`) | `docs/{hu,en}/platform-integration.md` |
| **D** | Azure DevOps szolgáltató (`Q2`) | `lang/{hu,en}/00-init-project.md`, `skills-{hu,en}/09a`, `09c` |
| **E** | Időkorlát és írás-hatókör (`G6`, `Q5`) | `ci-run-skill.sh` |
| **F** | `G8` + `G9` + `G10` kimondott szabályai (`Q6`) | `skills-{hu,en}/09c`, `09d`, `conventions.md` sablon |
| **G** | `auto-fix-loop` (`Q4` szerint: kiépítés **vagy** a mező visszavonása) | `00`, `09b`, `09c`, esetleg új script |
| **Z** | Átvezetés: **ÚJ, ÖNÁLLÓ témaoldal a docs-fában** (lásd `7.1`), `platform-integration.md`, `berki-spec-directory-structure.md`, `meta-improve-prompts.md`, `README*.md` | a docs-fa + a meta |


### 7.1 A dokumentációs teendő — ÖNÁLLÓ fejezet, külön fájlban

> **Felhasználói döntés (2026-09-23):** a központosított CI/CD működése **nem** a meglévő
> oldalakba szórva jelenjen meg, hanem **egy új, önálló fejezetként, saját fájlban**, a
> nyitólapról hivatkozva.

**Hova.** A `list14` háromrétegű docs-fájába: `docs/en/<név>.md` **és** `docs/hu/<név>.md`,
**azonos fájlnévvel**. Ma 14+14 témaoldal van; ez lenne a 15. **Javasolt név:**
`centralized-ci.md` (a meglévő nevek mintájára: `platform-integration.md`, `self-healing-loops.md`).

**Amit a `docs-tree-check.py` ezen számon kér** (`DG1`–`DG6`) — ez nem stílus-kérés, hanem kapu:

| kapu | mit kell teljesíteni |
|---|---|
| `DG1` | a fájl **mindkét** nyelvi ágon létezzen, azonos néven |
| `DG2` | a két fájl **fejléc-száma és mélység-sorrendje** egyezzen |
| `DG3` | minden relatív link létező fájlra mutasson |
| `DG4` | a `docs/en/README.md` **és** a `docs/hu/README.md` oldalindexe is tartalmazza |
| `DG5` | a gyökér-README-k maradjanak ≤ 400 sorosak — ma 298+298, tehát **csak hivatkozás** kerülhet beléjük, a fejezet maga nem |
| `DG6` | a ```mermaid blokkok száma fájlpáronként egyezzen |

**Javasolt fejezet-váz** (a `DG2` miatt a két nyelven azonos szerkezettel):

1. **Mi a központosított SDD** — a határvonal a PR feladásánál (`L13-D1`)
2. **A lánc végig** — a `1.1` ábra: `/bs-create-pr` → CI → pipa → policy-döntés
3. **A két szerep** — kódreview (ágens) és merge utáni tesztek (script), egy közös pipa (`L15-D5`)
4. **Amit a szolgáltatónál be kell állítani** — branch policy a **státusznévre** (`L15-D7`),
   gépi identitás és jogok (`L15-D8`), „branches up to date" (`L15-D4`)
5. **Titkok** — ágens-kulcs, értesítés, test manager; a név a `conventions.md`-ben, az érték env varban
6. **A pipeline-minták** — GitHub Actions és Azure DevOps (a 3. szakaszból, átírva)
7. **Hibakezelés** — bukott review, bukott tesztek, emberi döntés (`exit 2`), értesítés
8. **Korlátok és mért tények** — az Antigravity headless-hiánya, az Azure `pr:` trigger korlátja,
   a licenc-kérdés, a merge-commit checkout
9. **Hibakeresés** — a leggyakoribb bukások és a felismerésük

**Átvezetés a meglévő oldalakon** (a `Z` csomag része):
- `README.md` + `README-HU.md`: egy sor a parancstáblába/témalistába — **nem** fejezet;
- `docs/{en,hu}/README.md`: az oldalindex új bejegyzése (`DG4`);
- `docs/{en,hu}/platform-integration.md`: ma **ott** él az Antigravity CI-korlátja — el kell dönteni,
  **odaköltözik-e** az új fejezetbe, vagy marad és kereszthivatkozás készül. Duplán nem élhet.

**Kapu a csomag végén:**
```bash
python3 prompts/scripts/docs-tree-check.py
```

**Minden csomag zárása előtt** (a meta-prompt öt kapuja):
```bash
python3 prompts/scripts/lang-parity-check.py              # + --strict a kör végén
python3 prompts/scripts/sync-gemini-agents.py --check
python3 prompts/scripts/docs-tree-check.py
```
