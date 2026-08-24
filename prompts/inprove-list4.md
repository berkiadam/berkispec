# Berkispec kétnyelvűsítés — végrehajtási terv

> **Ez a dokumentum önhordó.** Üres kontextusban is végrehajtható: az 1. szakasz megadja a
> szükséges orientációt, a 3. szakasz a lezárt döntéseket, az 5–15. szakasz a pipálható
> teendőket, a 16. szakasz az elfogadási kritériumokat, a 17. a sorrendet.
> **Semmit nem kell kikövetkeztetni** — ha valami mégis hiányzik, az a terv hibája; írd bele.

---

## 0. Hogyan használd ezt a dokumentumot

1. **Olvasd el az 1–4. szakaszt** (orientáció, cél, döntések, nyitott döntés). Ez kb. a
   dokumentum harmada, de nélküle a teendők félreérthetők.
2. **Ellenőrizd az 5. szakaszt** — mi van már kész a munkafában. Ott konkrét `grep` parancsok
   vannak; ne feltételezz, ellenőrizz.
3. **A 17.1 sorrend szerint haladj**, és keresd meg az **első kipipálatlan** teendőt.
4. **Egy teendő = egy lépés = egy verifikáció.** Minden pont után futtasd a hozzá tartozó
   ellenőrzést (16. szakasz), és **pipálj ebben a fájlban** (`- [ ]` → `- [x]`). Ne halmozz
   több pontot egy verifikáció nélküli blokkba.
5. **Ha döntést kell hozni, ami nincs a 3. szakaszban:** ne döntsd el csendben — írd be a
   4. szakaszba nyitott döntésként, kérdezd meg a felhasználót, majd rögzítsd `LG<n>`-ként.
6. **A mérési adatok reprodukálhatók** — az 1.6 szakasz megadja a recepteket. Ha egy szám nem
   egyezik a mérteddel, a repó változott: frissítsd a számot a tervben.

---

## 1. Orientáció

### 1.1 Mi a berkispec

A berkispec egy **spec-driven development (SDD) prompt-rendszer**: fázisonkénti instrukciókat
ad egy AI-agentnek, hogy egy-két fejlesztő és az agent együtt, következetes minőségben,
ciklusonként leszállítható egységekben fejlesszen szoftvert.

- A **skillek** (`prompts/skills/*.md`) a fázis-receptek. A teljes flow 10 fázis (`00`–`09`),
  plusz segédparancsok (`cycle-status`, `quick-flow`, `export-doc`, `brainstorm`).
- Az **agentek** (`prompts/agents/*.md`) specialista subagentek: read-only diagnoszták
  (`reviewer`, `analyzer`, `analyzer-exec`, `researcher`, `doc-sync-planner`) és fix-mód
  belépők (`spec-fixer`, `plan-fixer`, `tasks-fixer`, `implement-fixer`, `review-fixer`,
  `test-runner`).
- A **shared blokkok** (`prompts/shared/*.md`) több skillbe beemelt, közös szövegrészek.
- A **scriptek** (`prompts/scripts/*.py`) determinisztikus kapuk és futtatók: a nyers teszt-log,
  a Sonar-riport és a `git diff` **nem kerül LLM-kontextusba**, a kiértékelést script végzi.
- Egy projekt artefaktumai: `conventions.md` (projekt-konvenciók), `specs/roadmap.md`,
  `specs/cycle-NN-<name>/{spec,plan,tasks}.md`, `test-report/`, `docs-generated/`.

**Tervezési vezérelv, amit a kétnyelvűsítés során is tartani kell:** a rendszer
**olcsó/gyenge LLM-re optimalizált** — determinisztikus védőhálók, kötelező ellenőrzőlisták,
egyszerre egy kérdés, szűkített fix-mód belépők. Ami a gyenge modell dolgát könnyíti, azt nem
rontjuk el a fordítással.

### 1.2 A repó mai szerkezete

```
prompts/
├── skills/       14 × .md      # fázis-receptek + segédparancsok
├── agents/       11 × .md      # specialista subagentek
│   └── gemini-agent/           # 11 × <név>/agent.json — az Antigravity/Gemini tükör
├── shared/       16 × .md      # beemelt közös blokkok (a 7.6 után 17)
├── templates/                  # ÜRES (csak .gitkeep)
├── scripts/      *.py          # kapuk, futtatók, telepítő-helper
├── models.json                 # platformonkénti modell/effort tierek (nyelvfüggetlen)
├── meta-improve-prompts.md     # a rendszer meta-leírása prompt-fejlesztéshez
└── inprove-list*.md            # korábbi fejlesztési munkafájlok
install.sh / install.ps1        # telepítők (interaktív)
README.md                       # a rendszer teljes dokumentációja (~1500 sor)
src/index.mjs + berkispec       # ELHAGYOTT Node CLI — törlendő, lásd LG22
```

**Támogatott platformok (5):** `claude`, `codex`, `antigravity`, `cursor`, `copilot`.

### 1.3 A telepítési lánc

> **⚠️ A LEGKÖNNYEBBEN ELNÉZETT RÉSZLET:** öt platform van, de a skill-írás **két külön
> kódúton** történik. A `codex`, `antigravity`, `claude` és `cursor` a `write_markdown_skill()`
> függvényt hívja; a **`copilot` viszont saját ciklust futtat** a `process_copilot`-ban, és
> `.github/instructions/bs-<clean_name>.instructions.md`-t ír (a `clean_name` a `NN-` prefix
> nélküli fájlnév-stem). Ez a saját ciklus **maga** hívja az `inline_shared_includes()`-t és a
> `substitute_scripts_dir()`-t. Minden skill-írásra vonatkozó módosításnál (pl. a `description`
> behelyettesítés, 8.6) **mind a két kódutat kezelni kell**, különben a Copilot-telepítés
> csendben kimarad.

```
install.sh / install.ps1
   └── platform-választás (interaktív)
        └── python3 prompts/scripts/install-helper.py <platform> <src_dir> <dest_path>
             ├── write_markdown_skill()  → <dest>/<platform-skills-mappa>/bs-<stem>/SKILL.md
             ├── agent-feldolgozás       → platformonként más formátum:
             │     claude/cursor/copilot: markdown + modell-injektálás
             │     codex:                 .codex/agents/<n>.toml (developer_instructions)
             │     antigravity:           agent.json (a gemini-agent tükörből)
             └── copy_helper_scripts()   → <dest>/<platform-scripts-mappa>/*.py
```

**Két fontos részlet, amire a terv épít:**

- A telepített skill útvonala **`bs-<fájlnév-stem>/SKILL.md`** — vagyis a *fájlnévtől* függ,
  **nem a forrásmappa nevétől**. Ezért a forrásmappák átnevezése nem változtatja a telepített
  kimenetet (lásd 16.1 byte-azonossági kritérium).
- A **skillek szándékosan NEM kapnak modell-injektálást** egyetlen platformon sem (a skill-
  szintű `model` mező nem hat megbízhatóan). A modellválasztás csak agent-szinten él, a
  `models.json` alapján — ez **nyelvfüggetlen**, a kétnyelvűsítés nem érinti.

### 1.4 Az INCLUDE mechanizmus — ahogy MA működik

A skillek és agentek törzsében állhat `<!-- INCLUDE:shared/<fájl>.md -->` marker. A telepítő
**build-time** behelyettesíti a hivatkozott fájl tartalmát (a vezető magyarázó HTML-kommentet
levágva). Releváns tények:

- Feloldó: `_read_shared_include()` + `inline_shared_includes()` az `install-helper.py`-ban.
- A marker regexe: `_INCLUDE_MARKER_RE = re.compile(r'[ \t]*<!--\s*INCLUDE:\s*(?P<path>[^\s]+?)\s*-->[ \t]*')`
- **Rekurzív**, `_MAX_INCLUDE_DEPTH = 5` mélységig (a `shared/fix-mode-*.md` beemeli a hozzá
  tartozó `shared/quality-check-*.md`-t).
- **Nem létező fájl esetén a marker érintetlenül marad** — a telepítés nem törik meg.
- Ma **71 marker** van a `prompts/` alatt; a leggyakoribbak: `context-check.md` (12×),
  `python-cmd.md` (6×), `phase-commit.md` (6×), `input-from-prev.md` (6×).

### 1.5 Szakszavak, amikre a terv hivatkozik

| Fogalom | Mit jelent |
|---|---|
| **fázis** | a 00–09 folyamat egy lépése, egy skill vezérli |
| **kapu** (gate) | objektív, jellemzően scriptelt ellenőrzés, ami PASS/FAIL-t ad |
| **fix-mód** | egy fázis-skill szűkített belépője, amit egy fixer-subagent használ célzott javításra |
| **D13** | tervezési elv: a fix-mód belépő legyen **önhordó** (a szükséges szabályokat INCLUDE-dal kapja), és **ne olvassa be a teljes fázis-skillt** — az a teljes fázis újrafuttatására csábít |
| **tükör** | a `prompts/agents/gemini-agent/<n>/agent.json`, ami az `agents/<n>.md` törzsének szó szerinti másolatát tartalmazza JSON-ba ágyazva; a `sync-gemini-agents.py` tartja szinkronban |
| **szabály-ID** | `VD5`, `DS22`, `BS18` stílusú azonosító a promptokban; **nyelvfüggetlen**, ezért a paritás-ellenőrzés horgonya |
| **artefaktum** | a projektbe kerülő dokumentum (`spec.md`, `plan.md`, riport, `docs-generated/`) |

**Használt szabály-ID prefixek ma:** `VD TR DS TC BD TP IP PID KX CD AG RV BQ EX AV RD GC SC
PE KO DI BR BI PC RP PW KF IM SK LC BS`. **Ez a terv az `LG` prefixet használja.**

### 1.6 A terv méréseinek reprodukálása

A terv konkrét számokra hivatkozik. Így ellenőrizhetők (a repó gyökeréből):

```bash
# fájldarabszámok
ls prompts/skills/*.md | wc -l          # 14
ls prompts/agents/*.md | wc -l          # 11
ls prompts/shared/*.md | wc -l          # 16 (a 7.6 után 17)
ls prompts/agents/gemini-agent/*/agent.json | wc -l   # 11

# útvonal-hivatkozások (bináris-mentes, git nélkül)
grep -rIln "prompts/skills\|prompts/agents\|prompts/shared" . | grep -v "^./.git/" | grep -v inprove-list

# INCLUDE markerek
grep -rho "INCLUDE:[^ ]*" prompts/ | sort | uniq -c | sort -rn

# magyar idézetsorok (user-facing mondat-jelöltek) skillenként
python3 - <<'PYEOF'
import pathlib, re
q = re.compile(r'^\s*>.*„')
for f in sorted(pathlib.Path("prompts/skills").glob("*.md")):
    n = sum(1 for l in f.read_text(encoding="utf-8").splitlines() if q.match(l))
    print(f"{f.name:24s} {n}")
PYEOF
```

```bash
# a telepített korpusz mérete (INCLUDE feloldva)
python3 - <<'PYEOF'
import pathlib, importlib.util
spec = importlib.util.spec_from_file_location("ih", "prompts/scripts/install-helper.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
tot = 0
for f in sorted(pathlib.Path("prompts/skills").glob("*.md")):
    n = len(m.inline_shared_includes(f.read_text(encoding="utf-8"), pathlib.Path(".")))
    tot += n
    if n > 60000: print(f"{f.name:24s} {n:7d}")
print("ÖSSZES:", tot)
PYEOF
```

**Mért értékek (2026-08-24, a `cycle-status.md` átnevezése utáni munkafa):** telepített
korpusz ~651 940 karakter; `03-write-plan.md` 127 897; `07-validate.md` 94 027;
`08-doc-sync.md` 73 164; `02-write-spec.md` 64 253; `04-write-tasks.md` 61 140.
**Nincs CI és nincs pre-commit hook a repóban** (`.github/`, `.pre-commit-config.yaml` nem
létezik) — ez a paritás-kapu integrációját érinti (11.9).

---

## 2. A cél

### 2.1 Miért

A magyar szöveg tokenizálása drága: nagyjából **2,2–2,8 karakter/token**, szemben az angol
~4-tel, és ugyanaz a tartalom angolul karakterben is 10–15%-kal rövidebb. A ~654 000 karakteres
telepített korpusznál ez fázisonként tíz-ötvenezer input token; angol instrukcióval **35–50%-kal
kevesebb**. Ráadásul az angol utasításkövetés — különösen a tagadások (`TILOS`, `soha ne`), a
feltételes elágazások és a kapu-logika — **gyenge/olcsó modellen mérhetően pontosabb**, ami
egybevág a rendszer tervezési céljával (1.1).

**A fő kockázat: nyelvi átszivárgás.** Angol instrukció + magyar artefaktum esetén a modell
(különösen a gyengébb) angol szavakat szivárogtat a magyar dokumentumba, vagy az egész
artefaktumot angolul írja meg. Az ez elleni fő fegyver a 9. szakasz `output-language` blokkja.

### 2.2 A két nyelvi tengely

**Két független beállítás, mindkettő `hu` | `en`:**

| Tengely | Mit határoz meg | Mi tartozik hozzá |
|---|---|---|
| **prompt-nyelv** | milyen nyelven vannak az **instrukciók**, amiket az agent olvas | instrukciós próza, magyarázat, indoklás, garde, tiltás, ellenőrzőlista |
| **projekt-nyelv** | milyen nyelven készülnek az **artefaktumok**, és milyen nyelven **beszél az agent a felhasználóval** | szó szerint kimondandó mondatok, fájlba írt sablonok, artefaktum-szekció fejlécek, státusz-kulcsszavak, a frontmatter `description` |

**Mindkettő build-time beállítás** (LG2): a telepítéskor dől el, és **fizikailag beépül** a
telepített promptokba. Utólag egyik sem változtatható — csak újratelepítéssel.

**Fő use case:** prompt = `EN`, projekt = `HU` — a prompt tokenben olcsó, a leadandó magyar marad.

### 2.3 A négy kombináció

| Prompt | Projekt | Mikor | Megjegyzés |
|---|---|---|---|
| HU | HU | a mai állapot | a byte-azonossági kritérium referenciája (16.1) |
| **EN** | **HU** | **a fő use case** | itt a legnagyobb az átszivárgás-kockázat |
| EN | EN | angol nyelvű projekt/ügyfél | nincs nyelvváltás, legkisebb kockázat |
| HU | EN | magyar fejlesztő, angol leadandó | átszivárgás fordított irányban |

Mind a négy működjön a végállapotban.

### 2.4 Célszerkezet

```
prompts/
├── skills-hu/                  # 14 fájl        ─┐
├── skills-en/                  # 14 fájl         │  PROMPT-nyelv tengely
├── agents-hu/                  # 11 .md          │
│   └── gemini-agent/           # 11 × agent.json │
├── agents-en/                  # 11 .md          │
│   └── gemini-agent/           # 11 × agent.json │
├── shared-hu/                  # instrukciós blokkok
├── shared-en/                  # instrukciós blokkok  ─┘
├── lang/                                        ─┐
│   ├── hu/                     # projekt-nyelvi blokkok:
│   │   ├── <skill-név>.md      #   horgonyozott szekciók (14 fájl)
│   │   ├── <agent-név>.md      #   horgonyozott szekciók (11 fájl)
│   │   ├── <shared-blokk>.md   #   horgonyozott szekciók (a shared blokkokból, 9.2)
│   │   ├── output-language.md  #   az átszivárgás elleni blokk
│   │   └── descriptions.json   #   frontmatter description-ök name szerint
│   ├── en/                     # ugyanaz angolul  │  PROJEKT-nyelv tengely
│   └── status-keys.json        # státusz- és szekció-kulcsok nyelvenként
└── scripts/                                      ─┘
    ├── install-helper.py
    ├── lang-parity-check.py    # ÚJ — paritás-kapu
    ├── lang_keys.py            # ÚJ — a scriptek nyelvi betöltője
    └── ...
```

**A két mappa-család szétválasztása szándékos:**
- `skills-<L>/`, `agents-<L>/`, `shared-<L>/` — a **prompt-nyelv** szerint (`<L>` = `PROMPT_LANG`).
- `lang/<L>/` — a **projekt-nyelv** szerint (`<L>` = `PROJECT_LANG`).

A `lang/` **nem** a `shared-*/` alatt van, mert nem a prompt-nyelvvel mozog: a
`shared-hu/lang/` és a `shared-en/lang/` ugyanaz lenne, tehát duplikáció.

---

## 3. Rögzített döntések (LG1–LG22, LG24–LG34; az **LG23** a 4. szakaszban)

Ezek **lezárt irányválasztások**. A végrehajtás során ne nyisd újra őket; ha valamelyik
kivitelezhetetlennek bizonyul, állj meg és kérdezz, ne dönts át csendben.

- [x] **LG1 — Két független beállítás**, mindkettő `hu` | `en`, és **ortogonálisak**. Mind a
  4 kombináció támogatott a végállapotban (2.3).

- [x] **LG2 — Mindkét tengely build-time; a projekt-nyelv is BEDRÓTOZÓDIK.**
  A prompt-nyelv a forrás-fát választja meg, a projekt-nyelv azt, hogy melyik `lang/<L>/`
  blokkok inline-olódnak be. Mivel a szöveg fizikailag beépül a telepített promptba, **utólag
  nem változtatható**, tehát nincs runtime feloldás és nincs mit rögzíteni a projektben.
  **Maradék kockázat (tudatosan vállalt):** ha egy meglévő projektet más projekt-nyelvvel
  telepítenek újra, a promptok csendben átállnak, miközben a már meglévő artefaktumok a régi
  nyelven vannak — nincs kapu, ami ezt megfogná. Enyhítés: a telepítő záró összefoglalója
  hangosan kiírja mindkét nyelvet (12.3), és a scriptek melletti `lang-keys.json` (LG18)
  utólag is megmutatja, milyen nyelvre telepítettek.

- [x] **LG3 — A prompt-nyelv KÉT FORRÁS-FA, nem include-fragmentálás.** Az instrukciós prózát
  nem szedjük nyelvi blokkokra — az szétvágná és olvashatatlanná tenné a promptokat. A
  duplikációt **script őrzi** (11. szakasz), nem éberség; ugyanaz a minta, ahogy a
  `sync-gemini-agents.py --check` a gemini tükröket.

- [x] **LG4 — A projekt-nyelvi blokkok KI VANNAK EMELVE, horgonyos INCLUDE-dal.**
  Nem fájlonként-blokkonként külön fájl (az ~100 apró fájlt jelentene), hanem **fájlonként EGY**
  nyelvi fájl `## <horgony>` szekciókkal, és a marker horgonyra hivatkozik:
  `<!-- INCLUDE:lang/01-add-cycles.md#BD5-branch-prompt -->`.
  Így nyelvenként 14 + 11 + 1 nyelvi fájl keletkezik, nem száz.

- [x] **LG5 — TELJES SZIMMETRIA: mindkét nyelv prefixelt mappában él.** `skills-hu/` +
  `skills-en/`, `agents-hu/` + `agents-en/`, `shared-hu/` + `shared-en/`. **Nincs kitüntetett,
  suffix nélküli fa** — egyik nyelv sem „az alap".
  **Indok:** az aszimmetria csendes hibát szül — aki `skills-en`-t lát, azt feltételezi, hogy
  van `skills-hu` is, és egy `skills/`-be írt javítás úgy néz ki, mintha nyelvfüggetlen lenne.
  Az átnevezés **`git mv`-vel** történik (követhető history), és a kódmódosítással **egyetlen
  commitban** (7. szakasz).

- [x] **LG6 — A frontmatter `name:` mező NEM fordul.** A `name` a slash-parancs azonosítója
  (`bs-brainstorm`, `bs-add-cycles`); ha eltérne a két fában, a parancsok elválnának, és a
  `prev`/`next`/`called_by` kereszthivatkozások eltörnének. (A `description`-re lásd LG15.)

- [x] **LG7 — A telepítő defaultja: prompt = `EN`, projekt = `HU`.**

- [x] **LG8 — Meglévő projektek migrációja: NINCS teendő.** A projekt-nyelv nem kerül a
  projektbe (LG2/LG17), tehát nincs pótolandó mező és nincs migrációs szabály a skillekben.
  Egy meglévő projekt egyszerűen újratelepül a választott két nyelvvel.

- [x] **LG9 — Státusz-kulcsszavak: `prompts/lang/status-keys.json`.** A `hu` értékek
  **byte-azonosak a maiakkal** (`Kész`, `Tervezésre kész`, `Task írásra kész`,
  `Implementálásra kész`, `Validálásra kész`) — ez a feltétele annak, hogy a létező projektek
  `spec.md`/`plan.md`/`tasks.md` fájljai érvényesek maradjanak.

- [x] **LG10 — A scriptek i18n-je csak a TEHERHORDÓ stringekre kötelező.** Három string-osztály
  van (10.1); a puszta konzol-üzenetek (`HIBA: nincs ilyen fájl`) fordítása **opcionális és
  utolsó** — az agent elolvassa őket, de nem illesztünk rájuk semmit.

- [x] **LG11 — A paritást script őrzi, nem review.** `prompts/scripts/lang-parity-check.py`,
  a `sync-gemini-agents.py --check` mintájára: exit 0 = szinkronban, exit 1 = eltérés.

- [x] **LG12 — Hiányzó nyelvi blokk esetén `hu` fallback HANGOS figyelmeztetéssel.** A fázisos
  migráció alatt a telepítés nem törik meg, de a vegyes nyelv nem marad csendben.

- [x] **LG13 — Nincs build-time gépi fordítás.** Az `en` fa **verziókezelt forrás**, nem
  generált artefaktum. Telepítéskor LLM-mel fordítani nem-determinisztikus lenne, ami egy
  prompt-rendszerben elfogadhatatlan.

- [x] **LG14 — A végállapot célja egy meglévő projekt TELJES újratelepítése** `EN` prompttal és
  `HU` projekt-nyelvvel. Nem pilot, nem részleges bevezetés.

- [x] **LG15 — A `description` a PROJEKT-nyelvet követi, build-time behelyettesítéssel.**
  Indok: a `description` az, amivel az agent **a felhasználó kérését** illeszti a skillhez — a
  felhasználó pedig a projekt nyelvén ír. `EN` prompt + `HU` projekt esetén tehát **magyar**
  `description` kell, különben kereszt-nyelvi illesztés történik, ami pont a gyenge modelleken
  romlik el. A frontmatterbe nem lehet INCLUDE-olni, ezért behelyettesítés (8.6).

- [x] **LG16 — A fixer-wrapperek runtime útvonal-hivatkozása megszűnik: a D13 minta
  kiterjesztése.** Az `implement-fixer.md` és a `review-fixer.md` ma azt írja, hogy olvassa be a
  `prompts/skills/06-implement.md`-t — ez a célprojektben érvénytelen útvonal (ott a telepített
  hely `.claude/skills/bs-06-implement/SKILL.md` vagy platformonként más). A 06 fix-mód
  szekciója **külön `shared-<L>/fix-mode-implement.md` blokkba** kerül, és a két fixer
  **INCLUDE-dal** emeli be, ahogy a `spec-fixer` / `plan-fixer` / `tasks-fixer` már ma is teszi.

- [x] **LG17 — A projekt-nyelv NEM kerül a `conventions.md`-be**, a `00-init-project` nem
  kérdez rá, és nincs runtime feloldás. Indok: a projekt-nyelvi betétek fizikailag beépülnek a
  telepített promptokba, tehát egy utólagos „átállítás" a `conventions.md`-ben hazugság lenne —
  a promptok attól nem változnának. Egy igazságforrás: a telepítés pillanatában választott nyelv.

- [x] **LG18 — A kapu-scriptek a mellettük lévő `lang-keys.json`-ból tudják a projekt nyelvét.**
  A telepítő a `prompts/lang/status-keys.json`-t a **választott nyelvre szűrve** kiírja a másolt
  scriptek mellé (`<platform-scripts-mappa>/lang-keys.json`), és a scriptek onnan olvassák.
  Nem mutálunk kódszöveget, hiányzó fájlnál `hu` fallback van, és ez a fájl egyben az utólag is
  látható nyoma annak, milyen nyelvre telepítettek.

- [x] **LG19 — A `prompts/scripts/init-project.sh` elavult.** Szimlink-alapú alternatív
  telepítési mód, amit soha nem használtunk, és amire semmi nem hivatkozik (csak a saját
  fejléc-kommentje). Jelöljük elavultnak, **nem nyelvesítjük**, az átnevezés utáni törését nem
  tekintjük regressziónak, és **nem töröljük**.

- [x] **LG20 — A telepítő kap minimális flag-alapú, nem-interaktív módot.**
  `--platform`, `--prompt-lang`, `--project-lang`, `--path`, `--help`; flag nélkül a mai
  interaktív út fut változatlanul. Indok: a 16.2 elfogadási kritérium 4 nyelvi kombináció ×
  5 platform = 20 futtatás, ami kézzel kivitelezhetetlen.

- [x] **LG21 — A migráció EGY feature branch-en készül, egy PR-ként** (nem inkrementális
  commitok a `main`-en). A `main` így a teljes migráció alatt működő állapotban marad. A
  branch-en belül a 17.1 lépései külön commitok, és a **szimmetrikus átnevezés saját, atomi
  commit**.

- [x] **LG22 — Az elhagyott Node CLI TÖRLENDŐ.** A `berkispec` launcher (7 sor) és a
  `src/index.mjs` (1176 sor) egy korábbi generáció: a `prompts/<language>/00-init.md`
  szerkezetet keresi, ami nem létezik (nincs `prompts/HU|EN/`, és a keresett fájlnevek —
  `00-init.md`, `01-project.md`, `01-write-spec.md`, `02-write-plan.md`, `03-write-tasks.md`,
  `04-implement-tasks.md`, `05-validate-cycle.md`, `01-modify-spec.md` — egyike sem található a
  repóban), és 2026-05-18 óta nem módosult, míg a `prompts/skills` ma is frissül.
  **Miért törlés és nem elavult-jelölés (szemben az LG19-cel):** ez a kód **saját HU/EN nyelvi
  logikát tartalmaz** (`prompts/<language>/`, `language === "EN" ? "## Status" : "## Állapot"`),
  tehát aktívan **félrevezeti** a terv végrehajtóját — összekeverhető a `lang/<L>/`
  célszerkezettel. Törlendő: `berkispec`, `src/`, és az üres `prompts/templates/`.

- [x] **LG30 — Az LG22 törlési köre kiegészül a `specification.md`-vel és a `.cursorrules`-zal.**
  Mindkettő az elhagyott Node CLI generációjához tartozik: a `specification.md` (471 sor) a
  CLI specifikációja (`./berkispec plan <cycle>`, `.berkispec/latest-prompt.md`, Codex CLI
  hívás), utolsó módosítása a repó 2. commitja; a `.cursorrules` pedig ezt jelöli meg „hiteles
  forrásként", és a törölt `src/`-re meg egy nem létező `plans/` mappára hivatkozik. Ugyanaz az
  indok, mint az LG22-nél: **aktívan félrevezeti** az üres kontextusban induló ágenst. **Mindkettő
  törlendő** (nem elavult-jelölés, nem átírás) — a gazda-projektre a `README.md` és a
  `prompts/meta-improve-prompts.md` a hiteles forrás.

- [x] **LG31 — Az LG16 minta KITERJESZTÉSE minden futásidejű repó-útvonalra.** A 7.4 maradék
  hivatkozásai ugyanabba a hibaosztályba tartoztak, mint az LG16 fixer-esete: a **telepített**
  prompt egy `prompts/…` repó-útvonalra küldte az ágenst, ami a célprojektben nem létezik (a
  gyenge modell megpróbálja beolvasni, elbukik, improvizál). Ezért az útvonal **eltűnik**, és a
  szöveg a **hívható néven** hivatkozik:
  - subagent → a neve (`analyzer`, `analyzer-exec`, `doc-sync-planner`, `researcher`, `reviewer`),
    „a platform telepített agent-definíciója" megjegyzéssel;
  - fázis-skill → a slash-parancsa (`/bs-02-write-spec`, `/bs-quick-flow`, `/bs-add-cycles`);
  - ahol tartalom kell (implement-/review-fixer), ott a 7.6 `shared-<L>/fix-mode-implement.md`
    INCLUDE adja meg, nem hivatkozás.
  **Következmény a 7.8-ra:** a „grep nulla találat" és a 16.1 byte-azonosság **nem tartható
  együtt** — a 7.4 szükségszerűen 6 skill tartalmát módosítja (00, 03, 05, 06, 08, quick-flow).
  A 7. szakasz ezért **két commit**: (a) tiszta átnevezés + kód, ahol a 16.1 byte-azonos; majd
  (b) a 7.4/7.6/7.7 tartalmi javítás, ahol a keretet újraalapozzuk és a diffet átnézzük.

- [x] **LG32 — A SZÖVEGKÖZI projekt-nyelvi literálok HELYŐRZŐ-TOKENT kapnak, build-time
  feloldással** (a `<platform-scripts-mappa>` / BD15 minta kiterjesztése).
  **A probléma:** a 9.1 az „artefaktum-szekció fejléc" és a „státusz-kulcsszó" osztályt
  projekt-nyelvinek (tehát kiemelendőnek) minősíti, de ezek **túlnyomó részben szövegközi,
  mondat belsejében álló hivatkozások** a magyar instrukciós prózában, nem kiemelhető blokkok.
  Mért felület (`skills-hu` + `agents-hu` + `shared-hu`): **~296** előfordulás 17
  szekciónévre, **~140** előfordulás 7 státusz-értékre/címkére — **összesen ~440**.
  Blokk-kiemeléssel nem kezelhető, literálként hagyva pedig csendes kapu-bukást okoz:
  `EN` prompt + `HU` projekt esetén az ágens `## Planned changes`-t írna, míg a kapu-scriptek
  a `lang-keys.json`-ból `## Tervezett módosítások`-at keresnek (16.6/c).
  **A döntés:** a prompt-forrásokban a literál helyére **ASCII helyőrző-token** kerül
  (`<sec:planned_changes>`, `<status:draft>`), amit a telepítő **build-time** a
  `status-keys.json` **PROJECT_LANG-szeletéből** old fel. Előnyök: egyetlen igazságforrás
  (a 10.4 automatikusan teljesül), szövegközi helyen is működik, a paritás-kapu a
  **token-halmazt** hasonlítja (11.12), a `hu` feloldás pedig **byte-azonos a maival** (LG9),
  tehát a 16.1 keret a teljes cserét fedi.
  **Miért ASCII, nem `<szekció:…>`:** a helyőrzőket nem fordítjuk (13.1), tehát a token a
  **`en` fába is átkerül** — egy ékezetes token ~440 szándékos kivételt kényszerítene a 16.5
  ékezet-grepre. A `<platform-scripts-mappa>` marad ékezetes (meglévő, egyetlen kivétel).
  **Következmények:** (1) új **9.7** szakasz a mechanizmusnak és a cserének; (2) a
  `status-keys.json` (10.3) **előrekerül** ide, mert a feloldás nélküle nem működik — a §10
  maradéka (a scriptek i18n-je) a helyén marad; (3) a 9.3 leltárban a szövegközi
  szekciónév/státusz **NEM kiemelési jelölt**, hanem **token-jelölt** — külön osztály;
  (4) a `lang/<L>/` blokkokban ezek a fejlécek **literálként** állnak (ott már nyelv-specifikus
  a fájl), és a 11.5 kapu ellenőrzi, hogy egyeznek a `status-keys.json`-nal.

- [x] **LG33 — Az ANGOLUL ÍRT projekt-nyelvi literálok is a `status-keys.json`-ba kerülnek,
  `hu` = `en` értékkel.** Érintettek: `Reviewed` / `Review Required` (schema artifact státusz a
  `plan.md`-ben), `Must Fix` / `Suggestion` (finding-súlyosság az `analyze-report.md`-ben és a
  `code-review.md`-ben), valamint a `dod-check.py` `VERDICT: PASS/FAIL/MANUAL` kulcsszava (10.2).
  Ezek **projekt-nyelviek** (artefaktumba íródnak és kapu-script illeszt rájuk), de a magyar
  értékük már ma is angol. Indok a felvételükre: (a) a szerződés így **egy helyen** van, és a
  11.5 kapu rájuk is érvényes; (b) a `hu` érték byte-azonos marad (LG9), tehát a 16.1 nem sérül;
  (c) ha egyszer mégis magyarítani kell őket, az egy JSON-érték átírása, nem 60 hely megkeresése.
  **A tokenizálás (9.7.4) rájuk is kiterjed** — `<status:reviewed>`, `<status:must_fix>` stb.

- [x] **LG34 — A 9.7.4 tokenizálás SZŰK KÖRŰ: a sablon-táblák OSZLOPFEJLÉCEI nem kapnak
  tokent.** A 9.7.2 leltár zárásakor derült ki, hogy a `03-write-plan.md` plan-sablonjában 12
  táblafejléc-sor áll, kb. 50 különböző oszlopnévvel (`| Komponens | Repo-útvonal / image |
  Base URL | … |`, `| Kategória | Típus | Előfeltétel | Parancs | … |`). **Ezek a prompt-nyelvvel
  mozognak** (a fordítás során angolra fordulnak). Indok: **egyetlen kapu-script sem illeszt
  rájuk** — a `run-tests.py` a *szekciócímre* illeszt (`^#+\s*Gépi futtatási tábla`), a sorokat
  utána **pozíció szerint** olvassa (`split("|")`), tehát az oszlopnév nyelve közömbös. A 9.1
  „artefaktum-szekció fejléce" osztálya a `##`/`###` címsorokra szűkül. **Amit tokenizálunk:**
  artefaktum-szekciófejléc, státusz-/címke-érték, és a `status-keys.json`-ban már meglévő
  mezőnevek (`Státusz`, `Mód`, `Lefedve`, …). **Elfogadott maradék-kockázat:** `EN` prompt +
  `HU` projekt esetén a plan.md tábláinak fejléce angol lehet (a modell az `output-language`
  blokk hatására gyakran magyarra fordítja) — gépi következménye nincs.

- [x] **LG24 — A rövidített úton (17.2) a 9.6 (`lang/en/`) BENNE MARAD, csak a 10. szakasz
  (script-i18n) halasztódik.** Indok: a `lang/en/` nélkül a paritás-kapu 11.1/11.3 pontja
  tartósan FAIL-t adna, tehát a 16.3 sosem teljesülne, és az `en/en` telepítés csendben
  `hu` fallbackre esne. A `lang/en/` a kiemelt (tehát már kis felületű) projekt-nyelvi
  blokkok fordítása — arányaiban olcsó. A halasztott §10 következménye: a **16.2 a rövidített
  úton `hu/hu` + `en/hu`-ra szűkül**, és a `lang-keys.json` követelmény a §10-hez csúszik.

- [x] **LG25 — A `lang-parity-check.py` KÉT ÜZEMMÓDOT kap.**
  **Default („folyamatban"):** csak a **mindkét oldalon létező** fájlpárokra futtatja a
  11.3–11.10 ellenőrzéseket, a féloldalas fájlokat WARN-ként listázza, exit 0.
  **`--strict`:** a teljes fájlhalmaz-paritás (11.1) is kötelező.
  Indok: a 13. szakasz fájlonként halad, tehát a szigorú kapu a teljes fordítási szakasz alatt
  definíció szerint FAIL-t adna, ami arra tanít, hogy a FAIL-t ignoráljuk. A **16.3 és a PR
  zárása `--strict`-et követel**; a napi commit-előtti futás (17.3) a defaultot.

- [x] **LG26 — Az agent `role:` mező is PROJEKT-nyelvi, és a behelyettesítés MIND A NÉGY
  agent-kódúton lefut.** Indok: a `role` ugyanúgy a delegálás-illesztés felülete, mint a
  `description` (LG15) — sőt a markdown-agent kódút (claude/cursor/copilot) a `description`-t
  **felülírja a `role:` mezőből** (`install-helper.py:374–380`), a codex pedig
  `description or role`-ra esik vissza. Ezért:
  - a `lang/<L>/descriptions.json` értéke skillnél string, **agentnél objektum**:
    `{"reviewer": {"description": "…", "role": "…"}}`;
  - behelyettesítés: (1) markdown-agent út, (2) codex TOML (`_build_codex_agent_toml`),
    (3) **antigravity `agent.json`** `description` + `displayName` — ez ma a *prompt*-nyelvű
    gemini-tükörből jön, tehát build-time cserét igényel a `process_antigravity`-ban,
    (4) a copilot saját agent-ciklusa;
  - hiányzó kulcs → `sys.exit(1)`, mint a 8.6-ban.

- [x] **LG27 — A 11.8 kódblokk-paritás fence-alapú, explicit listákkal.**
  **Byte-azonos** (nem fordítjuk): `bash`, `sh`, `python`, `json`, `yaml`, `toml`, `regex`,
  `diff` — **és minden fel nem sorolt infostring** (biztonságos default).
  **Fordítható:** `md`, `text`, és a nyelv-jelölés nélküli fence.
  Indok: a 9.1 szerint az illusztratív, fájlba nem kerülő ` ```md `/` ```text ` példák
  prompt-nyelviek, tehát fordulnak — a byte-azonosság rájuk fals FAIL lenne.

- [x] **LG28 — A 16.1 byte-azonossági keret a 8.7 egyesítés után KÖTELEZŐEN kiterjed a
  copilot kódútra is** (56 → 70 fájl: 5 platform × 14 skill). Indok: a 9.4 kiemelés a terv
  legkockázatosabb lépése, a copilot pedig a divergens kódút (1.3) — épp ott ne legyen vak
  a védőháló.

- [x] **LG29 — A munkafa rendezése két commitban a `main`-en, a branch nyitása ELŐTT** (LG21
  „friss `main`" előfeltétele):
  1. a kétnyelvűsítéstől független tartalmi munka: `cycle-status.md` átnevezés,
     `08-doc-sync.md`, `context-check.md`, `cycle-status.py`, `README.md`, `jegyzet.md`;
  2. a kétnyelvűsítés előkészítése: az `install-helper.py` nyelvi vezetékezése (5.1–5.4) +
     ez a tervfájl.
  Így a `main` tiszta és működő, a terv a `main`-en is olvasható, a history pedig nem mossa
  össze a két munkát.

---

## 4. Az LG23 döntés részletei

- [x] **LG23 — A fordítás vegyes vágásban készül, fájlonkénti pipálható lista szerint.**
  A **fő ágens** fordítja azt, ami más fájlokba beemelődik (a hibája propagálódik), vagy
  **script-ellenőrzött szerződést** hordoz (kapu-szekciónevek, gépi táblák, fix-mód belépők);
  minden más **fájlonként bounded subagent**, a glosszárium (13.2.1) és a 13.2 szabályok
  átadásával. A konkrét, fájlonkénti hozzárendelés és a haladás követése: **13.3**.
  A munka így **részletekben, több sessionban** végezhető — minden fájl önálló egység, amit a
  paritás-kapu (11.) zár le.
  **Kiegészítő védőháló:** a 11.10 imperatívusz-kapu gépiesen fogja meg a fordítás legfőbb
  kockázatát (az utasítás-erősség gyengülését), tehát a delegálás nem vak.

---

## 5. Kiindulási állapot — mi van már kész

Az `install-helper.py`-ban **már benne van a nyelvi vezetékezés alapja**, commit nélkül a
munkafában. **Ne írd meg újra — ellenőrizd:**

```bash
grep -n "PROMPT_LANG\|PROJECT_LANG\|_lang_subdir\|_resolve_include_path" prompts/scripts/install-helper.py
git status --short
```

**Ha a `grep` semmit nem talál:** a módosítás nem került be (vagy visszaállították). Ekkor az
5.1–5.4 pontokat **magadnak kell megírnod** — a leírásuk elég részletes hozzá —, de már
**egyenesen a célállapotban** (5.5), tehát a `_lang_subdir` mindig prefixel, és a marker-feloldás
a `shared-<PROMPT_LANG>/` + `lang/<PROJECT_LANG>/` alakot használja. Ilyenkor az 5.1–5.4-et
kipipálatlannak tekintsd, és a 7. szakasszal egy commitban végezd.

Ami már ott van (ha a `grep` talált):

- [x] **5.1 — Modul-szintű nyelvi konfig:** `PROMPT_LANG = "hu"`, `PROJECT_LANG = "hu"`,
  `SUPPORTED_LANGS = ("hu", "en")`.
- [x] **5.2 — Forrásfa-feloldás:** `_lang_subdir(base, lang)`, `skills_src_dir(src_dir)`,
  `agents_src_dir(src_dir, gemini=False)`. A `process_codex` / `process_claude` /
  `process_antigravity` / `process_cursor` / `process_copilot` **9 helyen** ezekre hivatkozik a
  korábbi `Path(src_dir) / "prompts/skills"` alakok helyett.
- [x] **5.3 — `lang/` INCLUDE-prefix:** új `_resolve_include_path(src_dir, rel_path)`.
  Hiányzó projekt-nyelvi fájl esetén `hu` fallback + egyszeri figyelmeztetés (LG12). A
  `_shared_include_cache` kulcsa kiegészült a `PROJECT_LANG`-gal.
- [x] **5.4 — `main()` két opcionális argumentuma:**
  `install-helper.py <platform> <src_dir> <dest_path> [prompt_lang] [project_lang]` — hiányában
  `hu`/`hu`, tehát a **3-argumentumos régi hívás változatlanul működik**. Érvénytelen nyelvnél és
  nem létező prompt-forrásfánál `exit 1` beszédes hibával.

### 5.5 Amit ezen a kódon MÓDOSÍTANI kell

A jelenlegi kód három ponton **nem** a célállapot. Ezek a 7. szakasz teendői, és a `git mv`-vel
**egy commitban** kell landolniuk, különben a telepítő nem találja a forrásmappákat:

| Mi | Jelenleg | Célállapot |
|---|---|---|
| `_lang_subdir` | `hu` esetén suffix nélküli nevet ad (`skills`) | **mindig** prefixel (`skills-hu`) — LG5 |
| `shared/<f>` marker | fixen `prompts/shared/<f>` | `prompts/shared-<PROMPT_LANG>/<f>` |
| `lang/<f>` marker | `prompts/shared/lang/<PROJECT_LANG>/<f>` | `prompts/lang/<PROJECT_LANG>/<f>` |

- [x] **5.6 — A kódkomment átírása.** Az 5.1 konfig fölötti kommentblokk a projekt-nyelvet
  „runtime beállításként" írja le, amit a `conventions.md` rögzít. Ez **nem a célállapot**
  (LG2/LG17): mindkét tengely build-time, a különbség csak a hatókörük. A kommentet írd át.

---

## 6. Takarítás (LG22 + LG19)

Ezt végezd el **legelőször**: kevesebb fájl marad, aminek az útvonalát ellenőrizni kell, és
eltűnik a félrevezető `prompts/<language>/` minta. Nem funkcionális változás, saját commit.

- [x] **6.1 — Törlés:** `git rm -r src/ berkispec prompts/templates/ specification.md .cursorrules`
  *(a `prompts/templates/` csak egy `.gitkeep`-et tartalmaz; a két gyökér-fájl az LG30.)*
- [x] **6.2 — `README.md`:** a mappastruktúra-ábrából és minden hivatkozásból ki a `src/`, a
  `berkispec` launcher és a `prompts/templates/`. A TOC-ot is ellenőrizd.
- [x] **6.3 — `prompts/meta-improve-prompts.md`:** ugyanez, ha említi őket.
- [x] **6.4 — `init-project.sh` elavult-jelölése (LG19):** komment a fájl elejére, hogy elavult
  és az `install.sh` / `install.ps1` váltja ki; említés a `meta-improve-prompts.md`-ben. Az
  útvonalait **ne** javítsd, és **ne töröld** a fájlt.
- [x] **6.5 — Ellenőrzés:**
  `grep -rIn "index.mjs\|prompts/templates\|specification.md\|berkispec plan" . | grep -v "^./.git/"`
  → nulla találat (az `inprove-list*.md`-t leszámítva).

---

## 7. Szimmetrikus átnevezés (LG5) — EGYETLEN commit

Ez a lépés **atomi**: az átnevezés, a kódmódosítás és az összes útvonal-hivatkozás javítása
együtt megy, különben a repó egy commitban törött állapotban áll.

- [x] **7.1 — `git mv` a három fára:**
  ```bash
  git mv prompts/skills  prompts/skills-hu
  git mv prompts/agents  prompts/agents-hu
  git mv prompts/shared  prompts/shared-hu
  ```
  *(A `prompts/agents/gemini-agent/` együtt mozog az `agents-hu`-val.)*

- [x] **7.2 — `_lang_subdir` mindig prefixel.** A `hu` → suffix nélküli elágazás törlendő:
  `return f"{base}-{lang}"` mindkét nyelvre.

- [x] **7.3 — A `shared/` INCLUDE-prefix prompt-nyelv-tudatos lesz.** `shared/<f>` →
  `prompts/shared-<PROMPT_LANG>/<f>`. **A 71 meglévő marker szövege NEM változik** — csak a
  feloldó. Egyúttal a `lang/<f>` prefix célja `prompts/lang/<PROJECT_LANG>/<f>` lesz (2.4).

- [x] **7.4 — Útvonal-hivatkozások javítása.** Mért leltár (a `inprove-list*.md` nélkül):
  - **`prompts/skills` — 64 találat, 19 fájlban:** `install.sh`, `install.ps1`,
    `prompts/scripts/init-project.sh`, `prompts/scripts/install-helper.py`,
    `prompts/meta-improve-prompts.md`, `README.md`, `.claude/settings.local.json` (**nem
    verziókezelt, lokális engedély-lista — csak a saját gépeden érdemes javítani, a PR-be nem
    kerül**), az öt
    fixer-wrapper (`spec-fixer.md`, `plan-fixer.md`, `tasks-fixer.md`, `implement-fixer.md`,
    `review-fixer.md`) és a hozzájuk tartozó **öt gemini `agent.json`**, valamint
    `skills/00-init-project.md` és `skills/03-write-plan.md`.
  - **`prompts/agents` — 9 fájlban:** `install.sh`, `install.ps1`, `init-project.sh`,
    `meta-improve-prompts.md`, `sync-gemini-agents.py`, `README.md`, és a `quick-flow.md` /
    `05-analyze.md` / `08-doc-sync.md` skillek.
  - **`prompts/shared` — 3 fájlban:** `install-helper.py`, `meta-improve-prompts.md`, `README.md`.
  - **Kivétel:** az `init-project.sh` útvonalait **ne** javítsd (LG19).

- [x] **7.5 — `install.sh` / `install.ps1` konstansok — TÖRÖLVE, mert használaton kívül voltak.**
  *(Tény-korrekció a végrehajtás közben:* a `SKILLS_SRC`, `AGENTS_SRC_DIR` és `AGENTS_GEMINI_SRC`
  csak deklarálva volt, egyetlen hivatkozás sem volt rájuk sem a `sh`-ban, sem a `ps1`-ben —
  tehát nem kellett nyelv-tudatossá tenni, hanem törölni. A forrásfát az `install-helper.py`
  `_lang_subdir()`-je oldja fel.) Az `install-helper.py` hívások helye a §12-hez:
  sh 372/414/456/498/561, ps1 395/440/485/530/595.

- [x] **7.6 — A fixer-wrapperek runtime hivatkozásának megszüntetése (LG16).** Az
  `implement-fixer.md` és a `review-fixer.md` ma azt írja: *„Olvasd be és kövesd a
  `prompts/skills/06-implement.md` fájlt"*. Teendő:
  1. a `06-implement.md` „Fix-mód (validate-hurok belépő)" szekciója kerüljön ki egy
     `shared-<L>/fix-mode-implement.md` blokkba;
  2. a `06-implement.md` INCLUDE-olja be (hogy a szabály egy helyen éljen);
  3. az `implement-fixer.md` és a `review-fixer.md` **ugyanezt** a blokkot emelje be, és a
     runtime útvonal-hivatkozás **törlendő** a szövegükből;
  4. minta: `spec-fixer.md` (`INCLUDE:shared/fix-mode-spec.md` +
     `INCLUDE:shared/quality-check-spec.md`);
  5. a `review-fixer` a review-findingokra, az `implement-fixer` a teszt/Sonar/DoD-ra szűkített
     belépőt kapja (ez ma is így van, csak a forrás változik).
  **Figyelj:** ez tartalmi refaktor, tehát a 16.1 byte-azonosság **ezen a két agenten és a 06
  skillen nem fog teljesülni** — ez itt elvárt, nem hiba.

- [x] **7.7 — Mellékesen javítandó: 3 elavult `sdd-lightweight-flow` hivatkozás.** A
  `00-init-project.md` (46. és 145. sor) és a `03-write-plan.md` (111. sor) a nem létező
  `prompts/skills/sdd-lightweight-flow.md`-re hivatkozik; a skill ma `quick-flow.md` /
  `/bs-quick-flow`. Javítsd, de a commit-üzenetben **külön jelöld**, mert ez tartalmi javítás,
  nem átnevezés.

- [x] **7.8 — Verifikáció még a kétnyelvűsítés előtt:**
  ```bash
  grep -rIn "prompts/skills/\|prompts/agents/\|prompts/shared/" . \
    | grep -v "^./.git/" | grep -v -- "-hu/\|-en/" | grep -v inprove-list | grep -v init-project.sh
  ```
  → nulla találat *(a `.claude/settings.local.json` nem verziókezelt lokális engedély-lista,
  és az `init-project.sh` az LG19 miatt kivétel)*.
  **A 16.1-ről lásd az LG31-et:** a byte-azonosság az **átnevezés + kód** commitra teljesült
  (56/56 hash változatlan — ez fogta meg, hogy a `shared/` marker feloldása a `_lang_subdir`
  nélkül csendben feloldatlanul hagyta volna mind az 56 skill INCLUDE-jait). A 7.4/7.6/7.7
  tartalmi commit után a keret **újraalapozva**: ugyanaz az 56 fájl, és pontosan a 6 érintett
  skill hasha változott (00-init-project, 03-write-plan, 05-analyze, 06-implement, 08-doc-sync,
  quick-flow) — más nem.

---

## 8. Horgonyos INCLUDE + `description` behelyettesítés

- [x] **8.1 — A marker szintaxis kiterjesztése.** `<!-- INCLUDE:lang/<fájl>.md#<horgony> -->`
  A `_INCLUDE_MARKER_RE` `[^\s]+?`-t illeszt, tehát a `#horgony` **automatikusan bekerül** a
  `path` csoportba — a regexet nem kell módosítani, csak a feloldót.
  > **Buktató a 9.4-hez (mért viselkedés):** a regex a marker körüli vízszintes whitespace-t is
  > elfogyasztja (`[ \t]*…[ \t]*`), tehát egy **sor közepére** tett marker elnyeli az előtte
  > lévő szóközt (`A: <!-- … -->` → `A:<blokk>`). A markereket ezért **mindig önálló sorba** tedd.

- [x] **8.9 — ⚠ A 8.2 HORGONY-HATÁROLÓ KORRIGÁLVA: `## <horgony>` → `<!-- ANCHOR:<horgony> -->`.**
  A 8.2 `## ` alapú határolója a **fő használati esetre nem működik**, és ez csak a 9.4 első
  fájljánál derült ki (a 16.1 keret fogta meg): a kiemelt blokkok túlnyomó része
  **artefaktum-sablon** (`conventions.md`, `plan.md`, `validation-report.md`, kérdés-fájlok),
  amik maguk is tele vannak `## ` címsorral — a határoló ezért a sablon **első saját címsoránál**
  elvágta a blokkot. A `00-init-project` 197 soros `conventions.md`-sablonjából **1 sor** jött át.
  **Csendes hiba lett volna:** a telepítés lefut, a kimenet hiányos, és ez csak hetekkel később,
  egy csonka `conventions.md`-ben derül ki.
  A `<!-- ANCHOR:… -->` sor markdown-tartalomban nem fordul elő, tehát ütközésmentes határoló.
  A blokk a horgony-sortól a **következő `<!-- ANCHOR: -->` sorig** (vagy a fájl végéig) tart;
  a vezető forrás-jegyzet levágása az ANCHOR markert **nem** eszi meg. A `8.4` névkonvenció
  (`<szabály-ID>-<rövid-név>`) és a `8.3` hibakezelés változatlan. *(Mind a négy ág újratesztelve:
  `##`-t tartalmazó blokk átvitele, második horgony, hiányzó fájl → marker érintetlen, hiányzó
  horgony → `exit 1`.)*

- [x] **8.2 — Horgony-vágás a feloldóban.** A `rel_path`-ot `#`-nél bontsd `(fájl, horgony)`-ra.
  Horgony nélkül a mai viselkedés (teljes fájl, vezető HTML-komment levágva). Horgonnyal: a
  nyelvi fájlban keresd meg a horgony-sort, és add vissza a **következő horgony-sorig** tartó
  törzset, `strip('\n')`-nel. *(A határoló alakja a **8.9** szerint `<!-- ANCHOR:… -->`, nem
  `## <horgony>` — az eredeti megfogalmazás hibás volt.)* A `_shared_include_cache` kulcsa a horgonyt is
  tartalmazza.

- [x] **8.3 — Hibakezelés (a két eset szándékosan KÜLÖNBÖZIK).** *(Mind a három ág tesztelve:
  horgony-kivágás, hiányzó fájl → marker érintetlen, hiányzó horgony → `exit 1` beszédes hibával.)*
  - Nem létező **fájl** → a mai viselkedés: a marker érintetlenül marad, a telepítés nem törik.
  - Létező fájl + **nem létező horgony** → **`sys.exit(1)`** beszédes hibával. Csendben kihagyni
    egy user-facing mondatot vagy egy fájlba írandó sablont súlyosabb, mint megállni.
  Ezt a különbséget írd bele kommentbe is.

- [x] **8.4 — Horgony-név konvenció:** `<szabály-ID>-<rövid-név>`, kisbetűs, kötőjeles — pl.
  `BD5-branch-prompt`, `CD1-template`, `DS22-gate-fail-question`. A szabály-ID-vel kezdés azért
  fontos, mert a paritás-kapu és a kereszthivatkozások így nyelvfüggetlenül azonosíthatók.

- [x] **8.5 — A `_MAX_INCLUDE_DEPTH = 5` marad.** A nyelvi fájlok **ne** tartalmazzanak további
  INCLUDE markert — ezt a paritás-kapu ellenőrzi (11.3).

- [x] **8.6 — `description` (+ `role`) behelyettesítés (LG15/LG26).** *(A `prompts/lang/hu/descriptions.json`
  a mai frontmatterekből generálva: 25 kulcs = 14 skill + 11 agent; az agent-értékek objektumok.
  Ezért a `hu`/`hu` telepítés kimenete változatlan — a 16.1 keret byte-azonos maradt.)* A frontmatterbe nem lehet INCLUDE-olni,
  ezért a `description` a **projekt-nyelvből** kerül be behelyettesítéssel, a már működő
  `substitute_scripts_dir` mintájára:
  - forrás: `prompts/lang/<PROJECT_LANG>/descriptions.json` — `{"bs-brainstorm": "…", …}`,
    a kulcs a frontmatter `name` mezője (LG6 szerint nyelvfüggetlen, tehát stabil kulcs);
  - a frontmatter `description:` sorát a projekt-nyelvi értékre cseréljük, **közvetlenül az
    INCLUDE-feloldás előtt** — **MIND A KÉT skill-író kódúton** (`write_markdown_skill` ÉS a
    `process_copilot` saját ciklusa, lásd 1.3);
  - **hiányzó kulcs → `sys.exit(1)`**: egy skill leíró nélkül gyakorlatilag meghívhatatlan (nem
    triggerel), tehát a csendes átengedés súlyosabb, mint a megállás (ugyanaz a logika, mint 8.3);
  - **az agentek `description`-je ÉS `role:` mezője ugyanígy (LG26)** — mindkettő a hívó
    agent felé megjelenő illesztő-felület, és a markdown-agent kódút a `description`-t a
    `role`-ból írja felül (`install-helper.py:374–380`). Az agent-kulcs értéke ezért **objektum**:
    `{"reviewer": {"description": "…", "role": "…"}}`. A behelyettesítésnek **mind a négy**
    agent-kódúton le kell futnia: markdown (claude/cursor), codex TOML
    (`_build_codex_agent_toml`), **antigravity `agent.json`** (`description` + `displayName` —
    ez ma a prompt-nyelvű gemini-tükörből jön, tehát build-time csere kell a
    `process_antigravity`-ban), és a copilot saját agent-ciklusa;
  - a paritás-kapu (11.4) ellenőrzi, hogy a `descriptions.json` kulcskészlete **pontosan** a fa
    `name` mezőinek halmaza, mindkét nyelven.

- [x] **8.8 — A SOR KÖZEPÉN álló marker whitespace-helyes (a 9.4 előfeltétele).** A 8.1
  buktató-jegyzete („a markereket mindig önálló sorba tedd") **stílusszabály marad**, de nem
  tartható a 9.4-ben: a 9.3 leltár szerint a user-facing, szó szerint kimondandó mondatok
  (~69 db) **felsorolás-pontok KÖZEPÉN** állnak, körülöttük instrukcióval — ott a marker
  szükségszerűen sor közepére kerül, és a régi regex elnyelte volna az előtte lévő szóközt.
  Ezért a `lead` / `trail` whitespace **külön csoportba** került, és a `_marker_is_standalone()`
  dönti el, melyik viselkedés jár:
  - a **saját sorát kitöltő** marker esetén a behúzás és a sorvégi szóköz eltűnik (a mai,
    blokk-szintű viselkedés — változatlan);
  - a **sor közepén / elején / végén** álló marker esetén a whitespace **megmarad**.
  *(Mind a négy eset tesztelve. A 16.1 keret byte-azonos maradt — ma egyetlen inline marker
  sincs a fában, tehát a változás a jelenlegi kimenetet nem érinti.)*

- [x] **8.7 — A skill-írás egységesítése (a 8.6 hibaosztály megszüntetése).** A `description`
  behelyettesítés az a harmadik dolog, amit két helyen kell elvégezni (az INCLUDE-feloldás és a
  `substitute_scripts_dir` után) — ez előbb-utóbb elcsúszik. **Emeld ki egy közös
  `prepare_skill_content(skill_file, src_dir, platform)` függvénybe** az INCLUDE-feloldást, a
  scripts-mappa behelyettesítést és a `description` cserét, és hívja **mind a két kódút**
  (`write_markdown_skill` és `process_copilot`). Ezután minden jövőbeli skill-transzformáció
  automatikusan mind az 5 platformra érvényes.
  **Ez tartalmi refaktor a telepítőben, nem a promptokban — a 16.1 byte-azonosságnak
  teljesülnie KELL utána is** (a kimenet nem változik, csak a kód szerkezete).
  *(Elvégezve: `prepare_skill_content()` + `prepare_agent_content()`; mind a 8 hívási hely
  (5 platform skill- és agent-ciklusai) ezeket használja, és az antigravity `agent.json`
  `description`-je is a projekt-nyelvből jön. A 16.1 utána byte-azonos.)*

---

## 9. A projekt-nyelvi blokkok (kiemelés + `output-language`)

Ez a **legnagyobb kockázatú** szakasz, mert működő magyar promptokhoz nyúl. A védőháló a
byte-azonossági teszt (16.1): a kiemelés után a `hu`/`hu` telepítés kimenete **változatlan** kell
legyen — a szöveg nem íródik át, csak átkerül egy másik fájlba és INCLUDE-dal jön vissza.

### 9.1 Osztályozási szabály — mi számít projekt-nyelvinek

Egy szövegrész **projekt-nyelvi** (tehát kiemelendő), ha a **projektbe kerül** vagy **a
felhasználóhoz szól**:

| Kategória | Felismerés | Példa |
|---|---|---|
| **Szó szerint kimondandó mondat** | `>` idézetblokk, amit az agentnek el kell mondania | *„Ez a feladat elég kicsinek tűnik a teljes fejlesztési ciklushoz…"* |
| **Fájlba írt sablon** | ` ```md ` / ` ```text ` fence, aminek a tartalma artefaktumba kerül | a `cycle-design-input.md` teste, a roadmap ciklus-blokk, a `brainstorm-NN.md` csontváza |
| **Artefaktum-szekció fejléce** | a spec/plan/tasks/riport `## …` címsorai, amikre a kapuk illesztenek | `## Tervezett módosítások`, `## Környezeti koordináták` |
| **Státusz-kulcsszó** | státusz-mező értéke és címkéje | `Tervezésre kész`, `Státusz:` |

> **A két alsó osztály KÉTFÉLE kezelést kap (LG32).** Ha a literál egy **kiemelendő blokkon
> belül** áll (sablon-fence, idézetblokk), akkor a blokkal együtt megy a `lang/<L>/`-be, és ott
> **literál** marad. Ha **szövegközi hivatkozás** az instrukciós prózában (a túlnyomó rész,
> ~440 hely), akkor **NEM kiemelési jelölt**, hanem **token-jelölt**: `<sec:…>` / `<status:…>`
> helyőrzőt kap, build-time feloldással — lásd a **9.7** szakaszt. A 9.3 leltárban a kettőt
> **külön osztályként** jelöld.

**NEM projekt-nyelvi** (a prompt-nyelvvel mozog, marad helyben):
- minden instrukció, magyarázat, indoklás, garde, tiltás, ellenőrzőlista;
- a szabály-ID-k és a rájuk hivatkozó szövegek;
- illusztratív példák, amik **nem** kerülnek fájlba (✅/❌ párok);
- a `<platform-scripts-mappa>` helyőrző, parancsok, kódblokkok.

**Határeset-szabály:** kérdezd meg — *„ez a szöveg megjelenik-e valaha a projekt egy fájljában
vagy a felhasználó képernyőjén szó szerint?"* Ha igen → kiemelés; ha csak az agent olvassa → marad.

### 9.2 Leltár (kiindulási mérés)

Magyar idézetsorok (`>` + `„`) és fájlba írt sablon-fence-ek darabszáma:

| Fájl | idézetsor | sablon-blokk |
|---|---|---|
| `00-init-project.md` | 1 | 0 |
| `01-add-cycles.md` | 4 | 1 |
| `02-write-spec.md` | 2 | 0 |
| `03-write-plan.md` | 18 | 1 |
| `04-write-tasks.md` | 0 | 2 |
| `05-analyze.md` | 1 | 0 |
| `06-implement.md` | 3 | 1 |
| `07-validate.md` | 9 | 0 |
| `08-doc-sync.md` | 7 | 7 |
| `09-merge.md` | 1 | 0 |
| `cycle-status.md` | 1 | 0 |
| `brainstorm.md` | 1 | 0 |
| `export-doc.md` | 1 | 0 |
| `quick-flow.md` | 2 | 0 |
| `agents/*` | 2 | — |
| `shared/*` | 16 | — |
| **összesen** | **69** | **12** |

> **⚠️ EZ ALSÓ KORLÁT, NEM TELJES LISTA.** Csak a magyar nyitó idézőjelet (`„`) tartalmazó
> sorokat számolja. **Nem** szerepel benne: a `> *"…"*` alakú (ASCII-idézőjeles) blokk, a
> többsoros idézet, az artefaktum-szekció fejléc, és a szövegközi user-facing string. A valós
> szám ennek a duplája is lehet.

- [x] **9.3 — Pontos leltár fájlonként.** Minden skill/agent/shared fájlon menj végig, és a 9.1
  osztályozás szerint készíts jelöltlistát. **Ezt írd be IDE**, fájlonként pipálható listaként —
  ez a folytatás horgonya, ha a munka több sessionra oszlik. A leltár készítése önmagában is
  komoly munkamenet; ne siettesd, és ne helyettesítsd greppel (ítéletet kíván).

#### A leltár jelölései

| Jel | Osztály | Hova megy |
|---|---|---|
| **K** | **kiemelési** jelölt — összefüggő blokk (idézet, sablon-fence) | `lang/<L>/<fájl>.md#<horgony>` + INCLUDE marker (9.4) |
| **T** | **token**-jelölt — szövegközi literál (szekciónév, státusz) | `<sec:…>` / `<field:…>` / `<status:…>` helyben (9.7, LG32) |
| **—** | nincs jelölt | a fájl teljes egészében prompt-nyelvi |

A **T** oszlopban csak a **kulcs-jelölteket** soroljuk fel, nem az összes előfordulást — a
darabszámokat a 9.7.2 tartja. Ahol egy T-literál a `status-keys.json`-ban **még nem szereplő**
kulcsot igényel, ott **`(új kulcs)`** jelölés áll: ezeket a 9.7.1 kulcskészletébe fel kell venni.

#### 9.3.1 `shared-hu/` — 17 fájl · **leltár KÉSZ**

| ✓ | Fájl | K (kiemelési jelölt) | T (token-jelölt kulcsok) |
|---|---|---|---|
| [x] | `artifact-voice.md` | — | `Kockázatok és döntési pontok`, `Kockázatok` |
| [x] | `context-check.md` | **25. sor** — a „kontextus nem friss" kérdés, szó szerint kimondandó → `#kontextus-nem-friss` | — |
| [x] | `conventions-change.md` | — | `## Teszt-riportolás`, `## Sonar`, `## Teszt eszközök`, `## Merge stratégia`, `## Portok`, `## Env változók` *(mind `conventions.md`-fejléc, új kulcs)*, `Tervezett módosítások`, `Cél és megközelítés` (új kulcs) |
| [x] | `fix-mode-implement.md` | — | `## Validációs javítások`, `## Review javítások`, `Implementálásra kész`, `Implementálás folyamatban` (új kulcs), `Validálásra kész`, `Definition of done`, a `check-log.md` **`Mód`** oszlopfejléce (új kulcs) |
| [x] | `fix-mode-plan.md` | — | `Piszkozat`, `Nyitott kérdések vannak`, `Task írásra kész` |
| [x] | `fix-mode-spec.md` | — | `Piszkozat`, `Nyitott kérdések vannak`, `Tervezésre kész` |
| [x] | `fix-mode-tasks.md` | — | `Piszkozat`, `Implementálásra kész`, `Plan-lefedettség` |
| [x] | `git-preflight.md` | **28. sor** — *„Commitáljam ezeket most, vagy folytassam?"* → `#commit-vagy-folytas` | `## Git és branching konvenciók`, `## Merge stratégia`, `Fő branch` (új kulcs), `Branch-elnevezési stratégia` (új kulcs), **és a 20. sor no-VCS flag-mondata** („NINCS verziókezelő…") — ezt a `00` írja a `conventions.md`-be, tehát illesztő literál (új kulcs) |
| [x] | `input-from-prev.md` | **30–36. sor** — a tétel-formátum ` ```md ` fence (fájlba írt sablon) → `#tetel-formatum` | `Tervezett módosítások` *(a sablonon belül — ott **literál** marad)* |
| [x] | `parallel-cycles.md` | — | — |
| [x] | `path-format.md` | — | — |
| [x] | `phase-commit.md` | — | — *(a `cycle-NN: <FÁZIS-TAG>` commit-üzenet és a `Commit: <sha> — …` visszajelzés nyelv-semleges: azonosító + fázis-tag)* |
| [x] | `python-cmd.md` | — | — |
| [x] | `quality-check-plan.md` | **73–138. sor** — a „Lezárási kapu" checklist-fence. **⚠ Ítéleti jelölt:** a 71. sor kimondja, hogy a listát *„a válaszodban ki kell írnod"* → felhasználói képernyőre kerül, tehát a 9.1 címzett-tesztje szerint projekt-nyelvi. **Feszültség az LG27-tel** (nyelv-jelölés nélküli fence = fordítható) — itt a címzett-teszt az erősebb; a döntést a 9.4 előtt rögzítsd. → `#lezarasi-kapu` | `Task írásra kész`, `Környezeti koordináták`, `Tervezett módosítások`, `Ellenőrzési stratégia`, `Teszt specifikáció`, `Spec-lefedettség`, `Fordított lefedettség`, `Konfiguráció-életút`, `Regressziós érintettség` (új kulcs), `Kockázatok és döntési pontok`, `Végrehajtási sorrend` (új kulcs), `Out of scope` |
| [x] | `quality-check-spec.md` | — | `Definition of done`, `Out of scope`, `Hivatkozott fájlok`, `Kockázatok`, `Teszt specifikáció`, `Komponensek és viselkedés` |
| [x] | `quality-check-tasks.md` | — | `Plan-lefedettség`, `Tervezett módosítások`, `Ellenőrzési stratégia`, `Regressziós érintettség`, `Kockázatok`, `## Teszt-riportolás`, `Out of scope` |
| [x] | `questions-tasks.md` | **9–15. sor** — a `tasks-questions.md` csontváza ` ```md ` fence-ben → `#struktura` | `Implementálásra kész`, `Piszkozat` |

**A shared pass három átvihető tanulsága** (a 9.1-et pontosítja, a további fájlokra is áll):

1. **Az ágens→orchestrátor üzenet PROMPT-nyelvi.** A `fix-mode-*` visszatérési összefoglalói, a
   `downstream-hatás:` mező (`nincs` / `van — …`) és a `fix-mode-implement.md` 56. sorának
   *„ESZKALÁCIÓ: …"* mondata **nem** kerül a projektbe és **nem** a felhasználóhoz szól: két
   prompt-nyelvi fájl közötti szerződés, tehát a prompt-nyelvvel mozog. **Nem jelölt.**
2. **Az illusztratív ❌/✅ példapár prompt-nyelvi** (9.1), **akkor is**, ha artefaktum-mondatot
   idéz (`artifact-voice.md` 21–24. sor): a példa az ágens tanítására szolgál, nem másolódik be.
3. **A `conventions.md` fejlécei is T-jelöltek.** A 9.1 „artefaktum-szekció fejléce" kategóriája
   nem szűkül a ciklus-artefaktumokra: a `conventions.md` a **projekt** fájlja, a fejléceit
   kapu-script olvassa (10.2/a), tehát ugyanaz az osztály.

#### 9.3.2 `agents-hu/` — 11 fájl · **leltár KÉSZ**

> **A frontmatter `description:` / `role:` NEM tartozik ide** — azt a 8. szakasz már elvégezte
> (`lang/<L>/descriptions.json`, LG15/LG26). Az `inputs:` / `outputs:` / `called_by:` listák
> prompt-nyelviek (nem telepített felület, csak forrás-metaadat) — **nem jelöltek**.

| ✓ | Fájl | K (kiemelési jelölt) | T (token-jelölt kulcsok) |
|---|---|---|---|
| [x] | `test-runner.md` | — *(a 124–151. sor Output-fence a hívó skillnek szóló visszatérési formátum → prompt-nyelvi, 1. tanulság; ugyanígy a 101–107. sor `EX1` blokk)* | `## Teszt-riportolás`, `## Sonar minőségellenőrzés`, `Teszt keretrendszer`, `Teszt struktúra` *(mind `conventions.md`, új kulcs)*, `Tesztelési stratégia`, `Regressziós érintettség`, `E2E infrastruktúra` (új kulcs), `### Gépi futtatási tábla` (új kulcs), `Kész` |
| [x] | `analyzer.md` | — *(109–124. sor: a prompt kimondja, „ne írj fájlt" → a lista a skillnek megy)* | `## Lefedettségi mátrix (generált)` (új kulcs), `Lefedve (gépi)` (új kulcs), `Spec-lefedettség`, `Fordított lefedettség`, `Konfiguráció-életút`, `Környezeti koordináták`, `Komponensek és viselkedés`, `Teszt specifikáció`, `Tervezett módosítások`, `Out of scope` |
| [x] | `analyzer-exec.md` | — *(86–102. sor: ugyanaz, agent→skill)* | `## Leltár` (új kulcs) **és a leltár-sor markerei**: `[ARTEFAKTUM]`, `[HORGONY]`, `[HANG-GYANÚ]`, `[TESZT-ÍGÉRET]`, `[DESZTRUKTÍV]` — ezeket az `analyze-gate-check.py` **generálja** és az agent **illeszti**, tehát (a)+(b) osztály, mind új kulcs; továbbá `Kockázatok és döntési pontok`, `Teszt specifikáció`, `Tervezett módosítások`, `Érintett komponensek` (új kulcs), `Konfiguráció-életút`, `Környezeti koordináták`, `Kockázatok` |
| [x] | `doc-sync-planner.md` | — *(92–131. sor: a fő ágensnek visszaadott terv-struktúra; a `Csereszöveg` blokkok tartalma **dinamikus**, nem sablon)* | `## Projekt referenciák` (új kulcs), a `docs-generated/` fejléc-mezők: `Lefedve`, `Utolsó frissítés`, `Generátor/scope` (új kulcs), `Utolsó futás: cycle-NN`, `Csereszöveg` (új kulcs), a művelet-címkék `reconciliation` / `új` / `nincs teendő` — ezek a `doc-sync-plan.md`-be kerülnek (új kulcs), `Regressziós érintettség`, `Teszt specifikáció`, `Tesztelési stratégia`, `E2E infrastruktúra` |
| [x] | `reviewer.md` | **59–74. sor** — a `code-review.md` teljes csontváza ` ```md ` fence-ben. **Ez valódi K:** projekt-artefaktumba íródik, és a 07 gépiesen parszolja → `#code-review-formatum`. **84. sor** — a lezárás-jelölés (`- [x] **MF-01** — … ✅ javítva`) szintén artefaktum-formátum → ugyanabba a horgonyba vagy `#lezaras-jeloles` | `## Összefoglaló`, `## Kritikus javítandók (Must Fix)`, `## Javasolt fejlesztések (Suggestions)` (új kulcs), a `„Nincs."` üres-szekció literál (78. sor, új kulcs), `✅ javítva` (új kulcs) |
| [x] | `researcher.md` | — *(55–65. sor Output-fence: a hívó skillnek adott válasz-formátum, nem fájl → prompt-nyelvi)* | `Komponensek és viselkedés`, `Hivatkozott fájlok`, `Tervezett módosítások` |
| [x] | `review-fixer.md` | — *(a 35. sor `ESZKALÁCIÓ:` és a 47. sor `FUTTATÁS BLOKKOLVA (EX1)` mondata orchestrátornak szól → 1. tanulság)* | `## Review javítások`, `## Validációs javítások` |
| [x] | `implement-fixer.md` | — *(ua. — 33. és 45. sor)* | `## Validációs javítások` |
| [x] | `tasks-fixer.md` | — | `Piszkozat`, `Implementálásra kész` *(a jelöltek túlnyomó része a beemelt `shared-hu/` fájlokban van — ott már leltározva)* |
| [x] | `plan-fixer.md` | — | *(mind a beemelt `shared-hu/fix-mode-plan.md` + `quality-check-plan.md`-ben)* |
| [x] | `spec-fixer.md` | — | *(mind a beemelt `shared-hu/fix-mode-spec.md` + `quality-check-spec.md`-ben)* |

**Az agent pass két új tanulsága:**

4. **A kapu-script által GENERÁLT sor-markerek is T-jelöltek.** Az `analyzer-exec` bemenete a
   `## Leltár` blokk `[ARTEFAKTUM]` / `[HORGONY]` / `[HANG-GYANÚ]` / `[TESZT-ÍGÉRET]` /
   `[DESZTRUKTÍV]` soraival: a szkript **írja** (10.2/b), az agent **illeszti** (10.2/a).
   Ha a szkript angolra fordul, de a prompt magyarul keresi (vagy fordítva), az agent
   **csendben nem talál semmit** — nem hibázik, csak üres marad. Ez a 10.2 leltár **hiányzó
   tétele**: vedd fel a 9.7.1 kulcskészletbe.
5. **A `docs-generated/` fejléc-mezői (`Lefedve`, `Utolsó frissítés`, `Generátor/scope`) és a
   `doc-sync-plan.md` művelet-címkéi** ugyanígy projekt-nyelviek, és a 10.2-ben sem szerepelnek.

#### 9.3.3 `skills-hu/` — 14 fájl · **leltár KÉSZ**

> **Két visszatérő minta, amit a leltár készítése közben rögzítettünk** (mindkettő ítéleti, és
> mindkettő sokat spórol):
> - **A „Folytatás megszakított futás után" fence-ek (nyelv-jelölés nélkül) NEM K-jelöltek.** Ezek
>   az ágensnek szóló döntési fák (`00`:286–298, `02`:259–269, `03`:133–143, `05`:111–135) —
>   prompt-nyelviek, LG27 szerint fordulnak. A bennük álló státusz-literálok viszont **T**-jelöltek.
> - **A „Váz" ↔ „Kész példa" párokban csak a VÁZ K-jelölt** (`08-doc-sync`). A „Kész példa"
>   illusztráció, a 9.1 szerint prompt-nyelvi — nem másolódik fájlba.

| ✓ | Fájl | K (kiemelési jelölt — sor) | T (token-jelölt kulcsok) |
|---|---|---|---|
| **✔ KIEMELVE** | `00-init-project.md` | **82–278** — a teljes `conventions.md` **sablon** (a legnagyobb egyedi blokk a repóban; két beágyazott fence: 184/192) → `#conventions-sablon`. **A kérdés-mondatok** (45, 46, 47, 48, 55 … ~16 db, `*„…"*` alakban, bullet közepén): user-facing → soronkénti inline INCLUDE. **333+** — a záró jelzés. *(286–298: prompt-nyelvi, lásd fent)* | a `conventions.md` **összes `##` fejléce** (a sablonon belül literál marad, a prózában token): `## Projekt áttekintés`, `## Tech stack`, `## Projekt referenciák`, `## Projekt struktúra`, `## Fejlesztési módszertan`, `## Git és branching konvenciók`, `## Merge stratégia`, `## Teszt struktúra`, `## Teszt keretrendszer`, `## Teszt-riportolás`, `## Naming konvenciók`, `## Portok és service-ek`, `## Környezeti változók`, `## Sonar minőségellenőrzés`, `## Kockázatok és ismert korlátok` (mind új kulcs); mező-nevek: `Alapértelmezett flow`, `Fő branch`, `Branch-elnevezési stratégia`, `Verziókezelő`, `Artefaktum-útvonal alapja`, `Riport-generálás kötelező`, `kör-mappa` / `test-report` jelölő-értékek (mind új kulcs); a **no-VCS flag-mondat** („NINCS verziókezelő (se GIT, se más), és nem is lesz.") |
| [x] | `01-add-cycles.md` | **190–217** (roadmap ciklus-blokk sablon), **317–329**, **386–401** (`cycle-design-input.md` sablon) → három horgony. **Kérdés/jelzés-mondatok:** 90, 101, 104, 259, 270, 281, 286, 292, 297, 347, 360, 436, 461. *(50–60 és 64–79: prompt-nyelvi döntési fa/példa)* | `Kész`, `Piszkozat`, `Folyamatban` |
| [x] | `02-write-spec.md` | **304–310** — `spec-questions.md` csontváza → `#spec-questions-struktura`. **Kérdés/jelzés:** 35, 326, 343. *(a 77–84. sori ✅/❌ tábla és a 279–287. sori példa-kérdések **illusztratívak** — nem jelöltek)* | `Tervezésre kész`, `Nyitott kérdések vannak`, `Piszkozat`, `Kész`, `Teszt specifikáció`, `Komponensek és viselkedés`, `Hivatkozott fájlok`, `Out of scope`, `Kockázatok`, `Definition of done`, `Regressziós érintettség` |
| [x] | `03-write-plan.md` | **159–165** — `plan-questions.md` csontváza → `#plan-questions-struktura`. **Kérdés/jelzés:** 117, 184, 876. *(338–342: `[P-…]` példa-címsorok → illusztratív; 133–143: döntési fa)* | a plan `##`/`###` fejlécei: `Tervezett módosítások`, `Teszt specifikáció`, `Tesztelési stratégia`, `Ellenőrzési stratégia`, `Környezeti koordináták`, `Konfiguráció-életút`, `Spec-lefedettség`, `Fordított lefedettség`, `Regressziós érintettség`, `Kockázatok és döntési pontok`, `Végrehajtási sorrend`, `E2E infrastruktúra`, `### Gépi futtatási tábla`, `Érintett komponensek`, `Cél és megközelítés`; státuszok: `Task írásra kész`, `Piszkozat`, `Nyitott kérdések vannak`; `Reviewed` / `Review Required` schema-státusz (angol literál — **döntést kíván**, lásd lent) |
| [x] | `04-write-tasks.md` | **111–116**, **182–216** (a `tasks.md` csoport/task sablonja — a legnagyobb itt), **234–239**, **265–269** → négy horgony. **Kérdés/jelzés:** 37, 324, 339. *(244–261: prompt-nyelvi)* | `Implementálásra kész`, `Task írásra kész`, `Plan-lefedettség`, `Tervezett módosítások`, `Ellenőrzési stratégia`, `Regressziós érintettség`, a záró csoportok nevei: `Regressziós tesztek felülvizsgálata`, `Dokumentáció` (új kulcs). **A `[RED]`/`[GREEN]`/`[CHECK]`/`[OPS]`/`TREG`/`TLAST`/`⟂` markerek NEM jelöltek** — azonosító-jellegűek, angolul maradnak (13.1) |
| [x] | `05-analyze.md` | **357–431** — az `analyze-report.md` teljes struktúrája → `#analyze-report-struktura`. **Kérdés/jelzés:** 65, 466–467. *(111–135: döntési fa; **291: az `analyzer` subagentnek átadott fókusz-üzenet → prompt-nyelvi**, 1. tanulság)* | `## Lefedettségi mátrix (generált)`, `Lefedve (gépi)`, `## Leltár` + a leltár-markerek (lásd 9.3.2/4. tanulság), `Validált alap`, `Hurok-napló` (új kulcs), `Összefoglaló`, státuszok: `Piszkozat`, `Tervezésre kész`, `Task írásra kész`, `Implementálásra kész` |
| [x] | `06-implement.md` | **196–209**, **226–232** — a `check-log.md` sablonjai → két horgony. **Kérdés/jelzés:** 38, 39, 266. *(72–84: prompt-nyelvi)* | `Implementálásra kész`, `Implementálás folyamatban`, `Validálásra kész`, `Kész`, a `check-log.md` oszlopfejlécei (köztük `Mód`), `## Validációs javítások`, `## Review javítások` |
| [x] | `07-validate.md` | **525–619** — a `validation-report.md` teljes sablonja (a második legnagyobb blokk) → `#validation-report-sablon`. **764–768** — a `[VALIDATE · … · próba 3/3]` **user-facing** megállás-prefix → `#megallas-prefix`. **Kérdés/jelzés:** 49, 792, 840. *(162–167, 186–196, 802–832: ágensnek szóló ábra/checklist → prompt-nyelvi)* | `## Kör N`, `# Validation History`, `## Összegzés`, `### Lépések`, `### Bukott elemek`, `### A kör döntése`, `### Kódreview (RV1)`, `### Megjegyzések` *(a `round-log.py` írja — 10.2/b)*, `## Validációs javítások`, `## Review javítások`, `## Teszt-riportolás`, `Kész`, `Validálásra kész`, `Implementálásra kész`, a riport fejléc-mezői (`Jelenlegi státusz`, `Körök száma`, `Utolsó frissítés`) és értékeik (`folyamatban`, `eszkalálva`, `megállt`) — új kulcsok |
| [x] | `08-doc-sync.md` | **Vázak (K):** 410–422, 425–434 (`Nem promótált jelöltek` napló), 465–474 (recept-blokk), 611–617 (`doc-sync-questions.md`), 644–647, 649–653 *(vegyes: a 649–653 „Kész példa" — kizárandó)*, 658–660, 665–671, 683–701, 706–708, 710–716, 721–757 (`test-conventions.md` teljes váza), 823–829 → **~10 horgony**. **Kérdés/jelzés:** 55, 872–873. **A „Kész példa" fence-ek (673–679, 771–816, 833–842, 847–849, 851–856) NEM K-jelöltek** | `## 0. Koordináták`, `## Lezárt eltérések`, `Utolsó frissítés: cycle-NN`, `Utolsó futás: cycle-NN`, `Utolsó felülvizsgálat`, `Gazda`, `Lefedve`, `Generátor/scope`, `**Indítás:**`, `**Példa hívás:**`, `Cél` / `Előfeltétel` / `Lépések` / `Elvárt eredmény`, `Hatókör` + `lokális` / `osztott-remote` értékek, `Kötelező riport (TR3)`, a `doc-sync-plan.md` művelet-címkéi (`reconciliation` / `új` / `nincs teendő`), `## DS22 Réteg 1 …`, `## Összesített státusz: …`, `## TC8 kapu …` — **túlnyomó részt új kulcs**; ez a fájl adja a `status-keys.json` `sections` szeletének nagyját |
| [x] | `09-merge.md` | **Kérdés/jelzés:** 31, 130–131, 184–195 (a záró üzenet, a következő ciklus indító parancsaival) | `## Merge stratégia`, `## Git és branching konvenciók`, `Fő branch`, `Szolgáltató` (új kulcs), `Kész`, `Validálásra kész`, `Piszkozat`, `Kritikus javítandók (Must Fix)`, `Validált alap`, a roadmap lezárás-jelölése (`✅` / `(kész)` — új kulcs) |
| [x] | `brainstorm.md` | **205–258** — a brainstorm munkafájl teljes csontváza → `#munkafajl-csontvaz`. **Kérdés:** 87 (`.gitignore` felajánlás) | `Folyamatban`, `Lezárva` (a munkafájl státuszai — új kulcs), `Státusz:`, `Utolsó frissítés`, `Indult` (új kulcs), és a munkafájl szekciónevei, ahol a próza rájuk hivatkozik (132, 140, 145, 157, 165, 185): `## 2. Feltárt tények`, `## 3. Alternatívák és trade-offok`, `## 4. Döntések`, `## 5. Nyitott kérdések`, `## 6. Javasolt ciklus-vágás`, `## 7. Napló` (mind új kulcs) |
| [x] | `cycle-status.md` | — | — *(a TUI státusz-szavai — `Kész`/`Folyamatban`/`KÉSZ`/`KÉSZ*`/`FOLYAMATBAN`/`MÉG NEM FUTOTT` — **csak a `description`-ben** vannak, azt a 8. szakasz kezeli; a `cycle-status.py` oldalán a 10.2/a leltár)* |
| [x] | `export-doc.md` | **79** — a `.gitignore` felajánló kérdés | `Lefedve` (a 20. sorban idézett fejléc-mező: `Lefedve: cycle-NN-ig · v3`) |
| [x] | `quick-flow.md` | **31** — a flow-váltás javaslata (user-facing). *(a 73–80. sori `mermaid` fence: ábra a promptban, nem fájlba írt — **nem** jelölt; LG27 szerint a `mermaid` infostring a byte-azonos listán van)* | `Must Fix`, `Suggestion` |

**A skill pass három tanulsága / nyitott pontja:**

6. **A `00-init-project.md` `conventions.md`-sablonja a projekt-nyelvi felület GERINCE.** Ez az
   egyetlen blokk adja a `status-keys.json` `sections` kulcsainak nagy részét, és minden más
   fájl erre a fejléc-készletre hivatkozik. **A 9.4-et ezzel a fájllal kezdd**, és a 9.7.1
   kulcskészletet ebből vezesd le — így a többi fájl leltára már kész kulcsokra hivatkozik.
7. **A `Reviewed` / `Review Required` és a `Must Fix` / `Suggestion` — eldöntve (LG33).**
   Ma angol literálok egy egyébként magyar artefaktumban, de projekt-nyelviek (artefaktumba
   íródnak, kapu illeszt rájuk). **Bekerülnek a `status-keys.json`-ba `hu` = `en` = angol
   értékkel**, és a 9.7.4 tokenizálás rájuk is kiterjed.
8. **Két tartalmi hiba, amit a leltár felszínre hozott — NE javítsd itt (9.4 fegyelem), de
   jegyezd fel:**
   - a `cycle-status.md` 40. sora a `shared-hu/python-cmd.md` szövegét **szó szerint
     duplikálja** az INCLUDE marker helyett;
   - a `spec-questions.md` / `plan-questions.md` / `tasks-questions.md` csontváza **három helyen**
     él (`02`:304–310, `03`:159–165, `shared-hu/questions-tasks.md`:9–15) — a kiemeléskor ez
     **egyetlen** `lang/<L>/` horgonyba vonható, de az már tartalmi változás: külön kör.

- [x] **9.4 — Kiemelés fájlonként.** Minden fájlra:
  1. a jelölt blokkok átmozgatása a `prompts/lang/hu/<fájlnév>.md`-be `## <horgony>`
     szekcióként, **szó szerint**;
  2. a helyükre `<!-- INCLUDE:lang/<fájlnév>.md#<horgony> -->` marker;
  3. a byte-azonossági teszt futtatása (16.1) — **fájlonként, nem a végén.**

  **✅ A 9.4 KÉSZ — mind a 42 prompt-fájl feldolgozva.**
  **73 horgony · 80 marker · `prompts/lang/hu/` 20 fájl · 16.1: 125/125 byte-azonos.**

  | Fa | Fájl (blokk) |
  |---|---|
  | `skills-hu/` | `01-add-cycles` (16) · `08-doc-sync` (12) · `00-init-project` (8) · `04-write-tasks` (6) · `06-implement` (5) · `07-validate` (4) · `02-write-spec` (3) · `03-write-plan` (3) · `05-analyze` (2) · `09-merge` (2) · `brainstorm` (2) · `export-doc` (1) · `quick-flow` (1) · `cycle-status` (0) |
  | `agents-hu/` | `reviewer` (2) — a többi agent jelöltjei a beemelt `shared-hu/` fájlokban vannak |
  | `shared-hu/` | `context-check` · `git-preflight` · `input-from-prev` · `quality-check-plan` · `questions-tasks` (1–1) |
  | közös | `common.md#ciklus-beazonositas` — **8 skillből** hivatkozva |

  **Öt tanulság, ami a végrehajtás közben született (mind kódba/tervbe került):**
  1. **A ```-fence a skillben marad, csak a BELSEJE kerül ki** — így a fence-paritás (11.8)
     mindkét fában stimmel, és a skill olvasható marad.
  2. **A behúzás a NYELVI blokkba költözik.** Ha a kiemelt sor be volt húzva, a marker a saját
     sorába kerül, és a `_marker_is_standalone` elnyeli a behúzást (8.8) — a szóközöket a `lang/`
     blokk elejére kell tenni. Sortartomány-kiemelésnél ez automatikus.
  3. **A forrásfájl záró újsor-állapotát meg kell őrizni** — ha az utolsó blokk a fájl végéig ér,
     a marker sora egyébként újsort tenne oda, ahol nem volt (`09-merge`).
  4. **A TÖBB fájlban byte-azonosan előforduló user-facing mondat KÖZÖS horgonyt kap**
     (`lang/hu/common.md`). Nyolc külön másolat a fordításnál garantáltan szétcsúszna (13.2.1),
     és a paritás-kapu ezt **nem** venné észre: mindkét fában nyolc darab lenne, csak más szöveggel.
  5. **⚠ A 16.1 NEM fogja meg a KIMARADT kiemelést.** Egy vissza nem cserélt literál byte-azonos
     kimenetet ad — a keret definíció szerint néma rá. Két marker így is kimaradt (két `git
     checkout --` visszavonta a közös-mondat cseréjét), és csak a **horgony ↔ marker
     kereszt-ellenőrzés** mutatta ki. **Ez a 11.3 kapu dolga lesz** — addig fusson kézzel:

  ```python
  # horgony ↔ marker paritás (a 16.1 vak foltja)
  import re, pathlib, collections
  anchors, markers = collections.Counter(), collections.Counter()
  for f in pathlib.Path("prompts/lang/hu").glob("*.md"):
      for m in re.finditer(r'^<!-- ANCHOR:(\S+?) -->$', f.read_text(encoding="utf-8"), re.M):
          anchors[f"{f.name}#{m.group(1)}"] += 1
  for d in ("skills-hu", "agents-hu", "shared-hu"):
      for f in pathlib.Path("prompts", d).glob("*.md"):
          for m in re.finditer(r'<!-- INCLUDE:lang/(\S+?) -->', f.read_text(encoding="utf-8")):
              markers[m.group(1)] += 1
  assert not set(anchors) - set(markers), "árva horgony"
  assert not set(markers) - set(anchors), "hivatkozott, de nem létező horgony"
  ```

  > **A kiemelés SZÓ SZERINTI.** Ne javíts, ne fogalmazz át, ne egységesíts közben — az külön
  > kör. Ha hibát találsz, jegyezd fel, de ne javítsd itt: a byte-azonosság a védőháló, és
  > minden „apró javítás" elrontja.

### 9.5 `output-language` blokk — az átszivárgás elleni fő fegyver

Mivel a projekt-nyelv nem kerül a projektbe (LG17), **kizárólag ez a bedrótozott blokk** hordozza
az információt arról, milyen nyelven kell írni.

- [x] **9.5.1 — `prompts/lang/<L>/output-language.md`** megírása. Tartalmi minimum:
  - az artefaktumok nyelve;
  - a felhasználóhoz szóló mondatok nyelve;
  - hogy a **kód, azonosító, kapcsoló, fájlnév marad angol**;
  - hogy a nyelvi keverés hiba.
- [x] **9.5.2 — A blokk a CÉLNYELVEN legyen megírva.** `EN` prompt + `HU` projekt esetén a skill
  élén egy **magyar** bekezdés áll. A szabály így egyszerre utasítás **és nyelvi horgony** — ez
  mérhetően jobban tart, mint egy angolul megfogalmazott „write in Hungarian".
- [x] **9.5.3 — Minden skill és minden agent élére** kerüljön be, a `context-check.md` mintájára
  (`<!-- INCLUDE:lang/output-language.md -->`), közvetlenül a H1 után.
- [x] **9.5.4 — Az agentek se maradjanak ki.** A `reviewer`, `analyzer`, `analyzer-exec`,
  `doc-sync-planner` és a fixerek **artefaktumba írnak** (`code-review.md`, `analyze-report.md`,
  riportok), tehát nekik is kell.

> **✅ A 9.5 KÉSZ.** `prompts/lang/hu/output-language.md` (39 sor) · a marker **mind a 14 skill
> és mind a 11 agent** H1-je után · a `quick-flow.md` bedrótozott nyelv-mondata kivezetve.
> A 16.1 keret **mind a 125 bejegyzésen** változott — ez a 16.1-ben **előre jelzett, elvárt
> kivétel**; a keret újraalapozva. A telepített kimenetben **nincs feloldatlan marker**.

- [x] **9.5.5 — A BEDRÓTOZOTT nyelv-mondatok kivezetése (a 9.3 leltár találata).** A
  `quick-flow.md` **70. sora** ma szó szerint kimondja: *„A ciklus-dokumentumok … nyelve a
  projekt konvenciójához igazodva **magyar**"*. Ez a 9.5 blokk **konkurens, hardcode-olt
  változata**: `EN` prompt + `EN` projekt esetén az `en` fába lefordítva („Hungarian") **aktívan
  hazudna**, és pont az a hibaosztály, ami ellen a 9.5 készül. Ezért: a mondat **kikerül**, a
  helyére a 9.5.3 `output-language` INCLUDE lép. Grepeld végig a többi fájlt is ugyanerre a
  mintára (`nyelve`, `magyarul`, `magyar`), mielőtt a 9.6-ra lépsz.

- [x] **9.6 — A `lang/en/` blokkok.** A `lang/hu/` kész fájljainak fordítása `lang/en/`-be,
  **azonos fájlnevekkel és azonos horgonyokkal**. A státusz-kulcsszavak és az artefaktum-szekció
  fejlécek fordítását a 10. szakasz `status-keys.json`-jával kell egyeztetni — ugyanaz a string
  ne legyen két helyen kétféle (ezt a 11.5 kapu ellenőrzi).

  > **✅ A 9.6 KÉSZ (2026-08-25).** `prompts/lang/en/` — **21 `.md` + `descriptions.json`**,
  > a `lang/hu/` teljes tükre. **73 horgony**, fájlonként **azonos sorrendben**; a fence-,
  > táblázat- és címsorszám fájlonként egyezik (a 11.7/11.8 kapu előzetes kézi futtatása).
  >
  > **A `descriptions.json` is ide tartozik** (a `lang/hu/`-ban él, LG15/LG26): 25 bejegyzés
  > (14 skill string + 11 agent `description`+`role`), kulcs- és szerkezet-paritással.
  > Enélkül az `en` projekt-nyelvű telepítés `hu` leírókra esett vissza — a telepítő
  > figyelmeztetése ezt jelezte.
  >
  > **Verifikáció:** (a) magyar ékezet a `lang/en/` fán → **0 találat** (a 16.5 mintája);
  > (b) a `status-keys.json` `hu` → `en` érték-illesztés fájlonként ellenőrizve (a 11.5
  > előfutára) — a talált egyetlen valós eltérés (`Test specification` sortörésen át) javítva,
  > a maradék 10 találat mind részszó-egyezés (`Kör` a `körönkénti`-ben, `Kész` a `Készen`-ben);
  > (c) próbatelepítés **mind az 5 platformra `hu` prompt + `en` projekt** nyelvvel:
  > **0 LG12-figyelmeztetés, 0 feloldatlan token, 0 feloldatlan INCLUDE**, és a telepített
  > `description` mindenhol angol; (d) a `hu`/`hu` 16.1 keret **70/70 + 55/55 változatlan**.
  >
  > **⚠ Amit a 9.6 felszínre hozott a §10-nek** (a `lang/en/` blokkok angol artefaktum-stringeket
  > vezetnek be, amiket a kapu-scriptek MA magyarul keresnek — ezek a 10.2 leltár hiányzó
  > tételei): `report-gate-check.py` → `## Teszt-riportolás`, `**Riport-generálás kötelező:**`,
  > `**Artefaktum-útvonal alapja:**` + a `kör-mappa` / `test-report` jelölő-értékek;
  > `round-log.py` → `## Kör N` (`ROUND_RE`) és `**Körök száma:**`; `run-tests.py` → a
  > `### Gépi futtatási tábla` szekciócím és a `--type gyors` / `nehez` **CLI-értékek**, amik
  > a plan run-táblájának `Típus` oszlopában is állnak; `failure-counter.py` → a
  > `# Validation History` fejléc (ez angol, tehát nyelvfüggetlen).

### 9.7 Projekt-nyelvi helyőrző-tokenek (LG32)

> **Ez a szakasz a 9.4 UTÁN fut.** A blokk-kiemelés legyen kész, mert a `lang/<L>/`-be
> áthelyezett blokkokban a fejlécek **literálként** maradnak (a fájl ott már nyelv-specifikus) —
> tokent csak az a szöveg kap, ami a **prompt-fában marad**.

**A tokenek alakja** (ASCII, ékezet nélkül — LG32) — **három család, a `status-keys.json`
három csoportjának megfelelően**:

| Token | Csoport | Példa (hu → en) |
|---|---|---|
| `<sec:<kulcs>>` | `sections` — artefaktum-szekció **neve** | `<sec:planned_changes>` → `Tervezett módosítások` / `Planned changes` |
| `<field:<kulcs>>` | `fields` — mező- vagy oszlopnév | `<field:f_status>` → `Státusz` / `Status` |
| `<status:<kulcs>>` | `status` — státusz- vagy címke-**érték** | `<status:ready_for_plan>` → `Tervezésre kész` / `Ready for planning` |

**A token a CSUPASZ literált adja vissza, `##` prefix NÉLKÜL** — a prefix a promptban marad
(`## <sec:planned_changes>`). *(Ez eltér a szakasz első vázlatától, ahol a `<sec:…>` a teljes
fejlécet adta volna és külön `<secname:…>` kellett volna a csupasz névhez.) Indok: ugyanaz a
szekciónév `##`, `###` és **mondat közbeni** hivatkozásként is előfordul — a prefix nélküli
érték mindhárom helyen ugyanazzal a kulccsal használható, és a prompt olvasható marad.*

> **9.7.1 + 9.7.3 KÉSZ.** `prompts/lang/status-keys.json`: **129 kulcs** (73 `sections`,
> 27 `fields`, 29 `status`), `hu` és `en` szelettel. A feloldó (`load_status_keys()` +
> `resolve_lang_tokens()`) a `prepare_skill_content` / `prepare_agent_content` láncban fut,
> **az INCLUDE-feloldás UTÁN** — így a beemelt `lang/` és `shared/` blokkok tokenjei is
> feloldódnak. Ismeretlen kulcs → `exit 1`; hiányzó nyelvi szelet → `hu` tartalék +
> figyelmeztetés; hiányzó fájl → `exit 1`. Mindkét nyelv és a hibaág tesztelve; a 16.1
> **125/125 byte-azonos** (a feloldó inert, amíg nincs token a fákban).

- [x] **9.7.1 — `prompts/lang/status-keys.json` létrehozása** a 10.3 szerkezetével, **`hu` és
  `en` szelettel együtt**. A `hu` értékek **byte-azonosak a maiakkal** (LG9) — ez a 16.1 keret
  feltétele. A kulcskészlet forrása a 10.2 leltár (szekció-fejlécek + státusz-értékek) **plusz**
  a 9.7.2 mérésben előkerülő, kapu-script által nem olvasott, de artefaktumba írt fejlécek
  (`Out of scope`, `Kockázatok`, `Komponensek és viselkedés`, `Hivatkozott fájlok`,
  `Definition of done`). *Ezzel a 10.3 teendő teljesül — ott csak vissza kell hivatkozni.*

- [x] **9.7.2 — Pontos, kulcsonkénti előfordulás-leltár.** Kulcsonként a fájl:sor lista, hogy a
  csere ellenőrizhető legyen és a 9.7.4 után igazolható a nulla maradék. Kiindulási mérés
  (`grep -ro` a három `*-hu` fán, 2026-08-24):

  | Kulcs-jelölt | Előfordulás | | Kulcs-jelölt | Előfordulás |
  |---|---:|---|---|---:|
  | `Teszt specifikáció` | 34 | | `Piszkozat` | 32 |
  | `Teszt-riportolás` | 28 | | `Validációs javítások` | 28 |
  | `Tervezett módosítások` | 27 | | `Task írásra kész` | 26 |
  | `Tervezésre kész` | 24 | | `Implementálásra kész` | 24 |
  | `Review javítások` | 23 | | `Tesztelési stratégia` | 21 |
  | `Out of scope` | 17 | | `Környezeti koordináták` | 16 |
  | `Kockázatok` | 15 | | `Definition of done` | 15 |
  | `Nyitott kérdések vannak` | 14 | | `Spec-lefedettség` | 13 |
  | `Konfiguráció-életút` | 12 | | `Fordított lefedettség` | 12 |
  | `Komponensek és viselkedés` | 11 | | `Validálásra kész` | 11 |
  | `Hivatkozott fájlok` | 10 | | `Státusz:` | 9 |
  | `Ellenőrzési stratégia` | 7 | | `Plan-lefedettség` | 7 |

  **⚠️ Ez is alsó korlát:** a lista a 10.2-ből és a 9.2 mérésből indul, de nem teljes — a
  leltárt fájlonként végigolvasva kell zárni (ítéletet kíván, nem greppel helyettesíthető).

  > **✅ A LELTÁR ZÁRVA (2026-08-25).** A zárás **fájlonkénti végigolvasással** történt, két
  > gépi segédlettel: (a) a `status-keys.json` minden `hu` értékének **szóhatáros** keresése a
  > három `*-hu` fán (a puszta `grep` téves találatainak kiszűrésére — az `új`, `lokális`, `Kör`,
  > `Cél`, `Mód` szavak köznévi előfordulása a találatok ~90%-a volt), és (b) a **sablon-fence-ek
  > címsorainak** kigyűjtése (fence-állapot követéssel, az escape-elt ` \`\`\`md ` fence-eket is
  > beleértve). A (b) hozta a leltár **hiányzó tételeit**: a `02`/`03` artefaktum-sablonjai a 9.4
  > kiemelésekor a prompt-fában maradtak (mert instrukciós prózát is tartalmaznak), így a
  > címsoraik közül azok, amikre kapu nem illeszt, kimaradtak a 9.3 T-listájából.
  >
  > **13 új `sections` kulcs** (a 9.7.1 készlet 129 → **142** kulcsra nőtt): `objective`,
  > `architecture_flow` (`02` spec-sablon) · `components_endpoints`, `rest_calls_examples`,
  > `test_api_users`, `other_parameters`, `network_access_prereqs`, `new_dependencies`,
  > `config_build_changes`, `schema_artifacts`, `unit_tests`, `integration_tests`, `e2e_tests`
  > (`03` plan-sablon). Mind `hu` **és** `en` értékkel; a `hu` byte-azonos a maival (LG9).
  >
  > **A leltár zárásának két döntése:** a táblafejlécek **nem** kapnak tokent (**LG34**), és az
  > **agent→skill visszatérési formátumok** (`test-runner` Output-fence, `analyzer` /
  > `analyzer-exec` / `researcher` riport-vázai) továbbra sem jelöltek — ez a 9.3.2 **1.
  > tanulságának** közvetlen alkalmazása.

- [x] **9.7.3 — A feloldó az `install-helper.py`-ban.** A `<platform-scripts-mappa>` feloldó
  (`_SCRIPTS_DIR_PLACEHOLDER`, ~208–230. sor) **mintájára**, ugyanabban a transzformációs
  láncban (`prepare_skill_content()` — így mind az 5 platform kapja, LG28):
  - `_load_status_keys(src_dir)` — a `prompts/lang/status-keys.json` beolvasása, cache-elve;
  - `resolve_lang_tokens(content, src_dir)` — a `<sec:…>` / `<field:…>` / `<status:…>`
    tokenek cseréje a **`PROJECT_LANG` szeletéből**;
  - **ismeretlen kulcs → `sys.exit(1)`** beszédes hibával (a 8.6 / LG26 mintája). Csendes
    „marad a token" **tilos**: az a telepített promptba szivárogna, és a gyenge modell szó
    szerint kiírná a `<sec:...>`-t az artefaktumba;
  - hiányzó `PROJECT_LANG`-szelet → `hu` fallback + egyszeri figyelmeztetés (LG12);
  - **az agentekre is fusson le** (nem csak a skillekre) — a 9.5.4 indoka itt is áll: a
    `reviewer` / `analyzer` / `doc-sync-planner` / fixerek artefaktumba írnak.

- [x] **9.7.4 — A csere elvégzése a `*-hu` fákon**, fájlonként. A csere **mechanikus**
  (literál → token), tartalmi javítás nélkül — ugyanaz a fegyelem, mint a 9.4-ben.
  **Amit NEM cserélünk:**
  - a `lang/hu/` blokkokba már áthelyezett szöveg (ott literál a helyes — LG32/4);
  - a `status-keys.json` maga;
  - a **példa-szövegek**, amik nem az artefaktum fejlécére hivatkoznak, hanem a szót
    köznévként használják (pl. „a kockázatokat mérd fel") — **ítélet kell**, a 9.1
    határeset-szabálya szerint;
  - a `conventions.md` szekciónevei, **amíg** a 9.7.1 kulcskészlet nem tartalmazza őket
    (a `## Git és branching konvenciók`, `## Sonar`, `## Merge stratégia`, `## Portok` —
    ezek a **projekt-fájl** fejlécei, tehát a 10.2 (a) osztálya; ha bekerülnek a kulcskészletbe,
    ide is tartoznak).

  > **✅ A CSERE KÉSZ (2026-08-25).** **945 token · 121 külön kulcs · 38 fájl**
  > (`<sec:>` 457 · `<field:>` 111 · `<status:>` 377). A 16.1 byte-azonosság **fájlonként**
  > futott: **70/70 skill-hash + 55/55 agent-hash változatlan** (az agent-keret a
  > `prepare_agent_content` kimenetére készült — a skill-keret az agenteket nem fedi).
  >
  > **Az alkalmazott elhatárolás** (a 9.1 határeset-szabályának operatív alakja): tokent kap a
  > literál, ha **megnevezésként** áll — címsor, `backtick`, `„idézőjel"`, **félkövér** címke,
  > vagy sablon-mező —, és marad, ha **ragozott vagy köznévi prózába** ágyazódik
  > (*„a Teszt specifikációjában", „a Hurok-naplóját", „ne állítsd Tervezésre késznek"*).
  > A ragozott alakok tokenizálása szövegátírást igényelne, azt pedig a 9.4/9.7.4 fegyelme
  > tiltja (byte-azonosság) — **külön kör**, ha a 16.6 éles próba indokolja.
  >
  > **Egy kódhiba is kiderült és javítva lett:** a `process_antigravity` az agent.json
  > tükrökön **nem futtatta** a `resolve_lang_tokens`-t (csak az INCLUDE-ot és a
  > scripts-mappa helyőrzőt) — az Antigravity-telepítés feloldatlan `<sec:…>` tokent
  > szállított volna, amint a §14 szinkronizálja a tükröket. A hívás bekerült, a
  > `prepare_agent_content`-tel azonos sorrendben.
  >
  > **21 kulcs a készletben ma nem token-alakban él** — ezek a `lang/hu/` blokkokba kiemelt
  > sablonokban (a `conventions.md` fejlécei, a `code-review.md` váza, a `test-conventions.md`
  > váza) **literálként** állnak, illetve kapu-scriptek olvassák (`blocking_findings`,
  > `failed_conditions`). Ez **helyes** (LG32/4) — a 11.12 kapu tehát **ne** követelje meg
  > minden kulcs token-alakú használatát.

- [x] **9.7.5 — Verifikáció fájlonként:**
  1. **16.1 byte-azonosság** — a `hu`/`hu` feloldás után a 70 hash **változatlan**. Ez a csere
     legfőbb védőhálója: bármilyen elírás a tokenben vagy a kulcsban azonnal kiderül.
  2. **nulla maradék:** a 9.7.2 literálok grepje a `*-hu` fákon már csak a 9.7.4 kivétel-listán
     ad találatot;
  3. **nulla feloldatlan token** a telepített kimenetben: `grep -r "<sec:\|<field:\|<status:"`
     a próbatelepítés célmappáin → **0 találat** (16.2 kiegészítése).

  > **✅ Mind a három teljesül.** (1) 70/70 + 55/55 hash változatlan, minden lépés után.
  > (2) A maradék literálok mind a kivétel-listára esnek: `lang/hu/` blokkok, „Kész példa"
  > illusztrációk, agent→skill visszatérési formátumok, ragozott próza, frontmatter
  > `inputs:`/`outputs:` metaadat, és a **`gemini-agent/` tükrök** (ezek a §14 hatóköre — ma
  > amúgy is elcsúszottak, lásd 14.3: a `sync-gemini-agents.py --check` a 9.4/9.5 óta 11
  > agentre `exit 1`-et ad). (3) Próbatelepítés **mind az 5 platformra** (`hu`/`hu`):
  > 190 fájl, **0 feloldatlan nyelvi token, 0 feloldatlan INCLUDE marker**. Ráadásként
  > `hu` prompt + **`en` projekt** telepítés is lefutott: a tokenek az `en` szeletre oldódnak
  > fel (`Planned changes`, `Ready for tasks`), és csak a `lang/en/` hiányára jön a várt
  > LG12-figyelmeztetés (§9.6).

- [x] **9.7.6 — A 13.1 kiegészítése:** a `<sec:…>` / `<field:…>` / `<status:…>` tokenek
  **NEM fordulnak** (mint minden helyőrző) — a fordítás során **byte-azonosan** kerülnek át az
  `en` fába. Ez a fordítás legnagyobb kockázatát is csökkenti: a fordítónak nincs is mit
  elrontania a kapu-illesztő stringeken.

---

## 10. `status-keys.json` + a scriptek i18n-je

> **Ez a szakasz a `projekt-nyelv = en` előfeltétele.** Az LG14 fő use case-hez (projekt = HU)
> **nem kell hozzányúlni a scriptekhez** — ha a szűk cél a mielőbbi `EN`/`HU` újratelepítés, ez
> a szakasz elhalasztható (17.2). De az LG1 („mind a 4 kombináció") teljesüléséhez kötelező.

### 10.1 A három string-osztály

A `prompts/scripts/*.py`-ban **279 egyedi magyar string** van. Nem egyformák:

| Osztály | Mit tesz | Fordítás | Hogyan találod meg |
|---|---|---|---|
| **(a) Artefaktum-ILLESZTŐ** | a projekt fájljaiban keres szekciót/státuszt/mezőt | **kötelező** | `in` / `re.search` / `startswith` egy beolvasott artefaktum-szövegen |
| **(b) Artefaktum-ÍRÓ** | riport-szekciót ír a projektbe | **kötelező** | `write_text` / `f.write` / riport-összeállítás |
| **(c) Konzol-üzenet** | a futtatónak és az agentnek szól | opcionális (LG10) | `print(...)`, artefaktum-írás nélkül |

> **⚠ A 9.6 zárásakor felszínre került, MA HIÁNYZÓ tételek** (mind (a)+(b) osztály — a script
> írja ÉS illeszti; a `lang/en/` blokkok már az angol alakot hordozzák, tehát a §10 nélkül az
> `en` projekt ezeken a pontokon csendben elhasal):
> - `report-gate-check.py`: `## Teszt-riportolás` (`SECTION_RE`), `**Riport-generálás kötelező:**`
>   (`REQUIRED_FLAG_RE`), `**Artefaktum-útvonal alapja:**` (`PATH_BASE_RE`) + a `BASE_ROUND` /
>   `BASE_FLAT` **érték-halmazok** (`kör-mappa`, `körmappa`, `kör`, `gyökér` …);
> - `round-log.py`: `## Kör N` (`ROUND_RE`) és a `**Körök száma:**` fejléc-mező;
> - `run-tests.py`: a `### Gépi futtatási tábla` szekciócím **és** a `--type gyors|nehez`
>   **CLI-választék**, ami a plan run-táblájának `Típus` oszlop-értékeivel párban áll —
>   ez a kettő **együtt** fordul, vagy egyik sem;
> - `tc8-gate-check.py`: a `test-conventions.md` 0./1./2./3. szekciócímei és a `Cél` /
>   `Előfeltétel` / `Lépések` / `Elvárt eredmény` mezőnevek (TC10/b).
>
> **A `# Validation History` (failure-counter.py) NEM tétel** — ma is angol, tehát nyelvfüggetlen.

- [ ] **10.2 — Az (a) és (b) osztály leltárának véglegesítése.** Az alábbi lista a **biztosan
  teherhordó** találatokat tartalmazza; ellenőrizd és egészítsd ki.

  **Státusz-értékek (a):** `validate-gate-check.py` — `Validálásra kész`, `Task írásra kész`,
  `Tervezésre kész`, `Kész` (a 97., 224., 230. sor környékén); `cycle-status.py` — a kisbetűs
  formák **és a `Státusz:` címke** (81., 273. sor környékén).
  *(A többi kapu-script nem hardcode-ol státusz-értéket.)*

  **Artefaktum-szekció fejlécek (a):** `analyze-gate-check.py` — `## Tervezett módosítások`,
  `## Teszt specifikáció`, `## Tesztelési stratégia`, `## Ellenőrzési stratégia`,
  `## Környezeti koordináták`, `## Konfiguráció-életút`, `## Spec-lefedettség`,
  `## Plan-lefedettség`, `## Fordított lefedettség`; `report-gate-check.py` —
  `## Teszt-riportolás`; `validate-gate-check.py` és `contract-guard.py` —
  `## Validációs javítások`, `## Review javítások`; `tc8-gate-check.py` — `## 0. Koordináták`,
  `Utolsó futás: cycle-NN`, `**Indítás:**`, `**Példa hívás:**`, `Cél` / `Előfeltétel` /
  `Lépések` / `Elvárt eredmény`; `ds22-gate-check.py` — `## Lezárt eltérések`,
  `Utolsó frissítés: cycle-NN`.

  **Riport-írók (b):** `round-log.py` — `## Kör N`, `### Lépések`, `### Bukott elemek`,
  `### A kör döntése`, `### Kódreview (RV1)`, `### Megjegyzések`, `## Összegzés`;
  `sonar-gate.py` — `## Nyitott findingek súlyosság szerint`, `## Blokkoló findingek`,
  `## Bukott feltételek`; `ds22-gate-check.py` — `## DS22 Réteg 1 …`,
  `## Összesített státusz: …`; `tc8-gate-check.py` — `## TC8 kapu …`; `dod-check.py` —
  `VERDICT: PASS/FAIL/MANUAL` (az angol kulcsszó marad, a magyarázat fordul).

- [x] **10.3 — `prompts/lang/status-keys.json`.** *(Kész: a **9.7.1** hozta létre — LG32 —, a
  **9.7.2** zárása pedig 129 → **142** kulcsra bővítette. Az alábbi leírás a szerkezetet
  rögzíti.)* *(Ezt a fájlt a **9.7.1** hozza létre — LG32;
  itt csak a szerkezet referenciája áll. Ha a 9.7.1 kész, ez a pont automatikusan teljesül.)*
  Szerkezet:
  ```json
  {
    "hu": { "status": { "done": "Kész", "ready_for_plan": "Tervezésre kész",
                        "ready_for_tasks": "Task írásra kész",
                        "ready_for_implement": "Implementálásra kész",
                        "ready_for_validate": "Validálásra kész",
                        "status_label": "Státusz" },
            "sections": { "planned_changes": "## Tervezett módosítások", "…": "…" } },
    "en": { "status": { "…": "…" }, "sections": { "…": "…" } }
  }
  ```
  A `hu` értékek **byte-azonosak a maiakkal** (LG9) — ez a visszamenőleges kompatibilitás
  feltétele.

- [x] **10.4 — Egyetlen igazságforrás.** A 10.3 `sections` értékei és a `lang/<L>/` blokkokban
  szereplő ugyanazon fejlécek **nem csúszhatnak el**. A 11.5 kapu ezt gépiesen ellenőrzi.
  *(A **prompt-fában** ez az LG32 tokenizálás után szerkezetileg garantált: ott már nincs
  literál, csak `<sec:…>` token. Ez a pont így a `lang/<L>/` blokkokra és a scriptekre szűkül.)*

  > **✅ A 11.5 kapu leszállította a `lang/<L>/` felét (2026-08-25).** A szabály, amit
  > implementál: *ha egy kulcs értéke LITERÁLKÉNT szerepel az egyik nyelv blokkjában, akkor a
  > párjának is szerepelnie kell a másikéban* — **szóhatáros** kereséssel, mert a puszta
  > részszó-egyezés a találatok ~90%-át adta (`Kör` a `körönkénti`-ben, `Kész` a `Készen`-ben).
  > A **meg nem jelenő kulcs nem hiba**: 21 kulcs kizárólag `<sec:…>`/`<status:…>` token
  > alakban él (azt a 11.12 őrzi), kettőt pedig csak kapu-script olvas (`blocking_findings`,
  > `failed_conditions`). **A scriptek fele a 10.5–10.7-tel zárul.**

- [ ] **10.5 — Közös betöltő (LG18).** `prompts/scripts/lang_keys.py` (aláhúzós név, hogy
  importálható modul legyen, ne a kötőjeles CLI-mintát kövesse): `load_keys()` a **saját
  mappájában** lévő `lang-keys.json`-t olvassa (`Path(__file__).parent / "lang-keys.json"`),
  cache-elve. Hiányzó fájl → `hu` fallback + egyszeri figyelmeztetés a stderr-re. **Nincs
  `conventions.md`-olvasás és nincs kötelező CLI-flag** — a nyelv telepítéskor eldőlt (LG17).
  A `--project-lang` opcionális **felülbírálásként** megmaradhat fejlesztéshez és teszthez.

- [ ] **10.6 — A telepítő írja ki a `lang-keys.json`-t.** A `copy_helper_scripts` egészüljön ki:
  a `status-keys.json`-ból a **választott projekt-nyelv szeletét** írja a scriptek célmappájába
  `lang-keys.json` néven: `{"lang": "hu", "status": {…}, "sections": {…}}`. A `lang` mező azért
  kell, hogy utólag is látható legyen, milyen nyelvre telepítettek (LG2 maradék kockázat).
  **A hívó skilleket NEM kell módosítani** — se flag, se helyőrző. Ez a döntés fő haszna:
  nulla skill-felület.

- [ ] **10.7 — A hardcode-olt stringek cseréje** a `lang_keys.load_keys()` értékeire a 10.2
  leltár szerinti scriptekben.

---

## 11. `lang-parity-check.py` — a determinisztikus paritás-kapu

A `sync-gemini-agents.py` mintájára: `--check` módban `exit 1` eltérésnél, egyébként emberi
olvasásra formázott riport. **Ez a kapu tartja életben a kétnyelvűséget** — enélkül a két fa
csendben szétcsúszik. Amint létezik, minden további lépés után fusson.

> **✅ A 11. SZAKASZ KÉSZ (2026-08-25).** `prompts/scripts/lang-parity-check.py` — mind a 12
> ellenőrzés benne van, két üzemmóddal (LG25). Mai állapot: **default → exit 0** (21 fájlpár,
> 43 WARN: a még le nem fordított `*-en` fák és a féloldalas gemini-tükrök), **`--strict` →
> exit 1** (a 11.1 fájlhalmaz-paritás a §13 zárásáig definíció szerint bukik). A telepítő
> **nem másolja** a célprojektbe (a `copy_helper_scripts` kizárja, mint az
> `install-helper.py`-t és a `sync-gemini-agents.py`-t).
>
> **Hibainjektálással tesztelve** — mind kiderült: kihagyott szekció (11.7 + 11.5), eltűnt
> szabály-ID (11.6), ismeretlen token-kulcs (11.12), suffix nélküli `prompts/skills/` mappa
> (11.2), gyengített imperatívusz (11.10).
>
> **A kapu a saját munkánkban is talált egy valódi hibát:** a 9.6-ban írt
> `lang/en/output-language.md` a magyar **`SOHA` ne fordítsd le** mondatot kisbetűs
> *„never translate these"*-re fordította — pontosan az a gyengülés, ami ellen a 11.10
> készült. Javítva (`NEVER`).
>
> **Két ponton pontosítottuk a tervet a megvalósítás közben:**
> 1. **11.10 — a magyar `SOHA` ugyanabba az osztályba tartozik, mint a `NEVER`.** A 11.10
>    felsorolása ezt nem tartalmazta; enélkül minden `SOHA` → `NEVER` fordítás hamis FAIL
>    lett volna. A kapu csoportonként számol: `TILOS`/`SOHA`/`FORBIDDEN`/`NEVER` egy csoport.
> 2. **11.8 — a `lang/<L>/` blokkokban a fence TARTALMA is projekt-nyelvi** (az
>    infostring-sorozat viszont ott is kötelezően egyezik). Indok: a nyelvi blokkok definíció
>    szerint artefaktum-sablonok, és a bennük álló ` ```bash ` fence-ek **helyőrző-magyarázatot**
>    tartalmaznak (`<a környezet felhúzása: …>`), a beemelt slash-parancsok argumentum-címkéi
>    pedig fordulnak (`ciklus:` → `cycle:`). A byte-azonosság ott tehát rossz kérdés — a
>    prompt-fákon viszont változatlanul él (LG27 listája szerint).
>
> **Két féloldalas-állapot kezelés (LG25 szelleme), ami nélkül a kapu ma használhatatlan
> lenne:** (a) az **árva horgony** irány (11.3) csak akkor FAIL, ha az adott nyelvnek már van
> prompt-fája — különben a §13 alatt mind a 73 `lang/en/` horgony árvának látszana; (b) a
> `descriptions.json` kulcskészletét (11.4) a **referencia-fa** `name:` mezőihez mérjük, ha az
> adott nyelvnek még nincs fája — a `name` úgyis nyelvfüggetlen (LG6).

- [x] **11.1 — Fájllista-paritás.** `skills-hu/` ↔ `skills-en/`, `agents-hu/` ↔ `agents-en/`,
  `agents-hu/gemini-agent/` ↔ `agents-en/gemini-agent/`, `shared-hu/` ↔ `shared-en/`,
  `lang/hu/` ↔ `lang/en/`: azonos fájlnév-készlet. Hiányzó vagy extra fájl → FAIL.
  A pár-képzés a `_lang_subdir` logikáját tükrözze (`<base>-<lang>`), **ne** hardcode-olt
  mappaneveket — így egy jövőbeli harmadik nyelv sem igényel script-módosítást.
  **Ez a pont csak `--strict` módban kötelező (LG25).** Default módban a féloldalas fájlok
  WARN-ként listázódnak, és a 11.3–11.10 ellenőrzések csak a **mindkét oldalon létező**
  párokra futnak — így a kapu a fájlonként haladó 13. szakasz alatt is használható marad.

- [x] **11.2 — Aszimmetria-őr (LG5).** FAIL, ha létezik `prompts/skills`, `prompts/agents` vagy
  `prompts/shared` **suffix nélküli** mappa. Ez fogja meg, ha egy félbehagyott rebase vagy egy
  figyelmetlen commit visszahozza a régi szerkezetet.

- [x] **11.3 — INCLUDE-marker leltár.** *(A 9.4 tanulsága szerint ez a kapu **a `hu` fán belül** is
  kell: horgony ↔ marker kereszt-ellenőrzés mindkét irányban — a 16.1 a kimaradt kiemelésre vak.)*
  A markerek halmaza legyen azonos a nyelvi párokban;
  minden hivatkozott `lang/<fájl>#<horgony>` **létezzen mindkét nyelvi mappában**; a `lang/`
  fájlok **ne** tartalmazzanak INCLUDE markert (8.5).

- [x] **11.4 — Frontmatter-paritás.** `name:` **byte-azonos** (LG6); a `prerequisites`, `output`,
  `prev`, `next`, `subagents`, `shared`, `phase` kulcsok jelenléte és **elemszáma** azonos.
  A `description`-re: a `lang/<L>/descriptions.json` kulcskészlete **pontosan** a fa `name`
  mezőinek halmaza legyen, mindkét nyelven (8.6). Az **agent**-bejegyzések objektumok, és
  mindkét nyelven tartalmazzák a `description` **és** a `role` kulcsot (LG26).

- [x] **11.5 — Státusz- és szekció-kulcsok.** A `status-keys.json` minden nyelvén ugyanazok a
  kulcsok; és minden ott szereplő érték **elő is forduljon** a hozzá tartozó `lang/<L>/`
  blokkokban. Ez fogja meg a 10.4 kétigazság-hibát.

- [x] **11.6 — Szabály-ID leltár.** A `([A-Z]{2,3}\d+[a-z]?(?:/[a-z])?)` minta szerinti
  azonosítók halmaza legyen azonos a nyelvi párokban. Ez fogja meg, ha a fordításból kimarad egy
  szabály. (A használt prefixek listája: 1.5.)

- [x] **11.7 — Szekció-szerkezet.** A `##`/`###` címsorok **száma és sorrendje** fájlonként
  egyezzen. Ez a legjobb egyszerű detektora annak, hogy a fordító kihagyott vagy összevont egy
  szekciót.

- [x] **11.8 — Kódblokk-paritás (fence-alapú, LG27).** A ``` fence-ek **száma és
  infostring-sorozata** egyezzen. Tartalom-ellenőrzés az infostring szerint:
  - **byte-azonos:** `bash`, `sh`, `python`, `json`, `yaml`, `toml`, `regex`, `diff`, **és
    minden fel nem sorolt infostring** (biztonságos default) — parancsot nem fordítunk;
  - **fordítható (nincs tartalom-ellenőrzés):** `md`, `text`, és a nyelv-jelölés nélküli fence
    — ezek az illusztratív, fájlba nem kerülő példák (9.1), amik prompt-nyelviek.

- [x] **11.9 — Integráció.** A repóban **nincs CI és nincs pre-commit hook** (1.6). Ezért:
  dokumentáld a `meta-improve-prompts.md`-ben **kötelező kézi lépésként** a
  `sync-gemini-agents.py --check` mellett, és írd bele a 17.3 folytatási receptbe is.
  A commit-előtti futás a **default** módot használja, a PR zárása és a 16.3 a **`--strict`**-et
  (LG25).

- [x] **11.10 — Imperatívusz-kapu (a fordítás legfőbb kockázata, gépiesen).** A fordítás
  legvalószínűbb minőségi hibája, hogy **gyengül az utasítás-erősség** (`TILOS` → `should not`),
  ami pont a gyenge modellek dolgát rontja el (1.1). Ez **mérhető jelentés-értés nélkül**:
  számold meg a „kemény padló" jelöléseket mindkét nyelvi változatban, és követelj egyezést:
  `⛔`, `🔴`, `⚠️`, `TILOS` / `FORBIDDEN` / `NEVER`, `SZIGORÚ` / `STRICT`, `Must Fix`, `STOP`.
  Fájlonként, nem összesítve. Eltérés → FAIL, a fájl és a jelölés megnevezésével.
  *(Ha egy eltérés indokolt — pl. két magyar mondat egy angolba olvad —, azt a fordító
  jegyezze fel a 13.3 listában, és a kapu kapjon rá explicit kivétel-bejegyzést.)*

- [x] **11.12 — Nyelvi token-paritás (LG32).** A `<sec:…>` / `<field:…>` / `<status:…>`
  tokenek **halmaza és darabszáma** legyen azonos a nyelvi párokban (`skills-hu/X.md` ↔
  `skills-en/X.md`), és **minden előforduló kulcs létezzen** a `status-keys.json` mindkét
  nyelvi szeletében. Eltérés → FAIL. Ez a 11.5-nél erősebb: azt is megfogja, ha a fordító egy
  tokent véletlenül literálra oldott fel (a leggyakoribb várható fordítási hiba ezen a
  felületen), mert akkor a token eltűnik az `en` oldalról.

- [x] **11.11 — Amit NEM tud ellenőrizni.** Írd bele a script docstringjébe: a fordítás
  *jelentés*-helyességét nem ellenőrzi, azt csak emberi review. A kapu a szerkezeti és leltár-
  hibákat fogja meg.

---

## 12. A telepítő

- [ ] **12.1 — `install.sh`: két nyelvi kérdés.** A platform-választó mintájára (a *„Melyik AI
  agent platformot használod?"* blokk, ~180–200. sor), **a platform-kérdés után**:
  ```
  Milyen nyelvűek legyenek a promptok?   1) English [default]   2) Magyar
  Milyen nyelvű legyen a projekt?        1) Magyar [default]    2) English
  ```
  Két globális változó (`PROMPT_LANG_CHOICE`, `PROJECT_LANG_CHOICE`), default `en` / `hu` (LG7).
  Az `install-helper.py` **öt** hívása (372/414/456/498/561. sor) kapja meg őket 4. és 5.
  argumentumként.

- [ ] **12.2 — `install.ps1`: ugyanez** `Read-Host`-tal (minta: a ~210. sor környéki
  platform-választó). `$SKILLS_SRC` a 66. sorban; a helper-hívások a 395/440/485/530/595. sorban.

- [ ] **12.3 — Visszajelzés a telepítés végén (LG2 maradék kockázat).** A záró összefoglaló írja
  ki **hangosan mindkét nyelvet**, és jelezze, hogy ezek a telepített promptokba
  **bedrótozódtak**, tehát utólag csak újratelepítéssel változtathatók. Mivel a projektben
  semmilyen nyelvi mező nem él (LG17), ez az **egyetlen** hely, ahol a felhasználó szembesül a
  választásával — nem elhagyható kozmetika.

- [ ] **12.4 — Nem interaktív mód (LG20).** Ma nincs ilyen: se `getopts`, se `usage`, minden
  választ `read -r` kér be (a `.ps1`-ben `Read-Host`). Az új, minimális mód:
  - `--platform <claude|codex|antigravity|cursor|copilot>`, `--prompt-lang <hu|en>`,
    `--project-lang <hu|en>`, `--path <cél>`, `--help`;
  - **ha egyetlen flag sincs, a mai interaktív út fut változatlanul** — ez a visszafelé
    kompatibilitás feltétele;
  - részlegesen megadott flagek: a megadottakat használja, a többit interaktívan kérdezi;
  - a konfliktus-kezelés (`ask_conflict`) nem-interaktív módban `--force` nélkül **álljon meg**,
    ne írjon felül csendben;
  - ugyanez a `.ps1`-ben, `param(...)` blokkal.

- [ ] **12.5 — `00-init-project.md` takarítás.** Ne kérdezzen projekt-nyelvet, és a
  `conventions.md` sablonjába se generálj nyelvi mezőt (LG17). *(A 7.7 szerinti két elavult
  `sdd-lightweight-flow` hivatkozás javítása szintén ebben a fájlban van.)*

---

## 13. Az angol fordítás

> **A vágás és a haladás követése: 13.3.** Minden fájl önálló egység — a munka részletekben,
> több sessionban végezhető.

Ez a legnagyobb **mennyiségű**, de a legkisebb **kockázatú** rész — feltéve, hogy a 8–11.
szakasz megvan, mert akkor a fordítandó felület már csak az instrukciós próza.

### 13.1 Amit NEM fordítunk

- a frontmatter `name:` (LG6) és minden `bs-*` parancsnév;
- a szabály-ID-k (`VD5`, `DS22`, `BS18`) és a rájuk hivatkozó szövegek;
- fájl- és mappanevek (`spec.md`, `docs-generated/`, `cycle-NN-<name>`);
- parancsok, kódblokkok, JSON/YAML kulcsok, regexek (a 11.8 byte-azonosságot követel);
- a `<platform-scripts-mappa>` és minden helyőrző — **beleértve a `<sec:…>` / `<field:…>` /
  `<status:…>` projekt-nyelvi tokeneket** (LG32, 9.7.6): ezek **byte-azonosan** kerülnek át;
- a **kapu-scriptek CLI-értékei** a példa-parancsokban (`run-tests.py --type gyors|nehez`) —
  ezek a script `choices` listájából jönnek, a fordításuk a §10 dolga, nem a §13-é;
- az INCLUDE markerek (a *tartalmuk* lehet nyelvi, a *marker* nem).

### 13.2 Fordítási szabályok

- [x] **13.2.1 — Glosszárium ELŐBB, és IDE írd.** A fordítás megkezdése előtt készíts szótárat a
  visszatérő szakkifejezésekre, és **ebbe a fájlba** írd be (ne a fejedben tartsd).
  **Inkonzisztens szakszó-fordítás a leggyakoribb hibaforrás egy ilyen korpuszban.**

  > **A glosszárium a 9.6 (`lang/en/`) megkezdésekor készült, és a §13-ra is ez érvényes.**
  > Ahol a szó **artefaktum-felület** (szekciónév, státusz, mezőnév), ott **nem itt** dől el a
  > fordítás, hanem a `status-keys.json` `en` szeletében — a glosszárium a **prózára** vonatkozik.

  | Magyar | Angol | Megjegyzés |
  |---|---|---|
  | ciklus | cycle | a `cycle-NN-<name>` azonosító sosem fordul |
  | fázis | phase | `phase 03`, `phase-closing commit` |
  | kapu | gate | `mechanikus kapu` → *mechanical gate* |
  | hurok | loop | `önjavító hurok` → *self-healing loop* |
  | kör | round | `teljes kör` / `könnyű kör` → *full round* / *light round* |
  | bukás, bukott | failure, failed | `bukott elem` → *failed item* |
  | artefaktum | artifact | |
  | tervezési dokumentum | design document | a `spec.md`/`plan.md`/`tasks.md` gyűjtőneve |
  | lefedettség | coverage | `fordított lefedettség` → *reverse coverage* |
  | előfeltétel | prerequisite | |
  | kiemelés (9.4) | extraction | csak a tervben, promptban nem fordul elő |
  | horgony | anchor | az `ANCHOR:` marker neve sosem fordul |
  | helyőrző | placeholder | |
  | csereszöveg | replacement text | `<field:f_replacement_text>` |
  | eltérés (`design-drift`) | deviation | |
  | recept, regiszter | recipe, register | `test-conventions.md` = *recipe register* |
  | promótálás | promotion | `promótált tétel` → *promoted item* |
  | váz, csontváz | skeleton | |
  | minőségellenőrzés | quality check | a `## Sonar minőségellenőrzés` fejléc a kulcskészletből jön |
  | lezárási kapu | closing gate | |
  | kérdés-nyilvántartó | question register | a `*-questions.md` fájlok |
  | súlyosság | severity | |
  | hatókör | scope | `osztott-remote` → *shared-remote* (kulcskészlet) |
  | szerződés | contract | `szerződés-integritás` → *contract integrity* |
  | munkafa | working tree | `tiszta munkafa` → *clean working tree* |
  | visszaintegrálás | back-integration | |
  | eszkaláció | escalation | `ESZKALÁCIÓ:` prefix — prompt-nyelvi, fordul |
  | takarítás | cleanup | |
  | riport | report | |
  | jelölő, marker | marker | a `[analyze-loop]` / `[validate-loop]` marker maga sosem fordul |
  | megerősítés | confirmation | `explicit megerősítés` → *explicit confirmation* |
  | ütközés | conflict | |
  | számláló | counter | |
  | fejléc-blokk | header block | a `docs-generated/` doksik `Lefedve:` sora |
  | felhasználó | user | a promptban **Felhasználó**/**felhasználó** egyaránt → *user* |
  | `downstream-hatás:` | `downstream-effect:` | a fixer → orchestrátor szerződés-mező (D11); az `nincs`/`van —` értékek is fordulnak (`none`/`yes —`) |
  | `Knn` (kérdés-azonosító) | `Qnn` | a `*-questions.md` tételei; a `lang/en/` blokkok is `Qnn`-t használnak |
  | `<FÁZIS-TAG>` | `<PHASE-TAG>` | a commit-üzenet helyőrzője; a kitöltött érték (`02-spec`) nyelvfüggetlen |
- [ ] **13.2.2 — Az imperatívuszok erőssége nem gyengülhet.** `TILOS` → `FORBIDDEN` / `NEVER`,
  **nem** `should not`. A `⛔` és `🔴` jelölések maradnak. A gyenge modellek pont ezeken a
  pontokon romlanak el (1.1).
- [ ] **13.2.3 — Szerkezet-megőrzés.** Ugyanannyi `##`/`###` címsor, ugyanabban a sorrendben
  (11.7), ugyanannyi táblázat és kódblokk (11.8).
- [ ] **13.2.4 — Fájlonként fordíts, és fájlonként futtasd a paritás-kaput.** Ne halmozz.

### 13.3 Fájlonkénti fordítási lista

**A vágás elve (LG23):** a **fő ágens** fordítja azt, ami (a) más fájlokba beemelődik — tehát a
hibája propagálódik —, vagy (b) **script-ellenőrzött szerződést** hordoz (kapu-szekciónevek,
gépi táblák, fix-mód belépők). Minden más **fájlonként bounded subagent**, a 13.2.1 glosszárium
és a 13.2 szabályok átadásával, utána paritás-kapu (11.) + célzott átnézés.

Megoszlás: **fő ágens 28 fájl / ~453700 karakter · subagent 14 fájl / 219484 karakter.**
(A 28. a 7.6-ban létrejövő `shared-<L>/fix-mode-implement.md`.)

> **Ez a lista a folytatás horgonya.** Pipálj soronként, valós időben. Minden fájl után futtasd a
> `lang-parity-check.py --check`-et (11.), és a 13.2.4 szerint ne halmozz.

#### 13.3.1 `shared-hu/` → `shared-en/` — 17 fájl, ~87000 karakter

**Ez az első lépés**, mert minden skill beemeli: itt dől el a terminológia. A 13.2.1 glosszáriumot
**ezzel párhuzamosan** véglegesítsd — amit itt eldöntesz, azt a többi 25 fájl követi.

> **✅ A 13.3.1 KÉSZ (2026-08-25) — mind a 17 fájl.** `prompts/shared-en/`, fájlonként futtatott
> paritás-kapuval (13.2.4). Magyar ékezet a fán: **0 találat** (16.5). A `hu`/`hu` 16.1 keret
> változatlan. **A glosszárium három tétellel bővült** a fordítás közben: `downstream-hatás:` →
> `downstream-effect:` (fixer → orchestrátor szerződés-mező, D11), `Knn` → `Qnn`,
> `<FÁZIS-TAG>` → `<PHASE-TAG>` — ezeket a 05/07 skill fordításának **kötelezően követnie kell**,
> mert a fixerek és az orchestrátor ezeken a stringeken keresztül beszélnek.

| ✓ | Fájl | Karakter | Ki fordítja |
|---|---|---:|---|
| [x] | `quality-check-plan.md` | 18558 | **fő ágens** |
| [x] | `fix-mode-implement.md` | 6725 | **fő ágens** *(a 7.6-ban létrejött)* |
| [x] | `quality-check-tasks.md` | 11986 | **fő ágens** |
| [x] | `quality-check-spec.md` | 10716 | **fő ágens** |
| [x] | `phase-commit.md` | 5558 | **fő ágens** |
| [x] | `git-preflight.md` | 5033 | **fő ágens** |
| [x] | `fix-mode-tasks.md` | 4882 | **fő ágens** |
| [x] | `fix-mode-plan.md` | 4328 | **fő ágens** |
| [x] | `input-from-prev.md` | 4121 | **fő ágens** |
| [x] | `fix-mode-spec.md` | 3371 | **fő ágens** |
| [x] | `parallel-cycles.md` | 3258 | **fő ágens** |
| [x] | `artifact-voice.md` | 3082 | **fő ágens** |
| [x] | `conventions-change.md` | 2934 | **fő ágens** |
| [x] | `path-format.md` | 1987 | **fő ágens** |
| [x] | `questions-tasks.md` | 1434 | **fő ágens** |
| [x] | `context-check.md` | 1240 | **fő ágens** |
| [x] | `python-cmd.md` | 436 | **fő ágens** |

#### 13.3.2 `agents-hu/` → `agents-en/` — 11 fájl, 82603 karakter

Az 5 fixer a fő ágensnél: a D13 fix-mód szerződéseket hordozzák, és a 7.6 refaktor után a
`shared-<L>/fix-mode-*.md` blokkokra hivatkoznak. A 6 read-only agent delegálható.

| ✓ | Fájl | Karakter | Ki fordítja |
|---|---|---:|---|
| [ ] | `test-runner.md` | 15310 | subagent |
| [ ] | `analyzer.md` | 13769 | subagent |
| [ ] | `analyzer-exec.md` | 11495 | subagent |
| [ ] | `doc-sync-planner.md` | 10474 | subagent |
| [ ] | `reviewer.md` | 7022 | subagent |
| [ ] | `researcher.md` | 6202 | subagent |
| [x] | `review-fixer.md` | 4436 | **fő ágens** |
| [x] | `implement-fixer.md` | 4144 | **fő ágens** |
| [x] | `tasks-fixer.md` | 3657 | **fő ágens** |
| [x] | `plan-fixer.md` | 3218 | **fő ágens** |
| [x] | `spec-fixer.md` | 2876 | **fő ágens** |

#### 13.3.3 `skills-hu/` → `skills-en/` — 14 fájl, 503619 karakter

A hat fő ágenses skill mindegyike **script-ellenőrzött szekciónevekkel vagy gépi táblákkal**
dolgozik (`analyze-gate-check.py`, `validate-gate-check.py`, `report-gate-check.py`,
`ds22-gate-check.py`, `tc8-gate-check.py`, `run-tests.py`, `round-log.py`) — lásd a 10.2 leltárt.
Egy elmosott szekciónév itt **kapu-bukást** okoz, nem stílushibát.

| ✓ | Fájl | Karakter | Ki fordítja |
|---|---|---:|---|
| [ ] | `03-write-plan.md` | 87752 | **fő ágens** |
| [ ] | `07-validate.md` | 83455 | **fő ágens** |
| [ ] | `08-doc-sync.md` | 71567 | **fő ágens** |
| [ ] | `05-analyze.md` | 41157 | **fő ágens** |
| [ ] | `02-write-spec.md` | 36033 | **fő ágens** |
| [ ] | `01-add-cycles.md` | 32516 | subagent |
| [ ] | `quick-flow.md` | 28761 | subagent |
| [ ] | `04-write-tasks.md` | 28443 | **fő ágens** |
| [ ] | `06-implement.md` | 27886 | subagent |
| [ ] | `00-init-project.md` | 25944 | subagent |
| [ ] | `brainstorm.md` | 17171 | subagent |
| [ ] | `09-merge.md` | 13792 | subagent |
| [ ] | `export-doc.md` | 5997 | subagent |
| [ ] | `cycle-status.md` | 3145 | subagent |

---

## 14. Gemini `agent.json` tükrök

- [ ] **14.1 — `agents-en/gemini-agent/` létrehozása** — 11 × `agent.json`, az `agents-en/*.md`
  törzsével.
- [ ] **14.2 — `sync-gemini-agents.py` nyelv-tudatosítása.** Ma `prompts/agents/<n>.md` →
  `prompts/agents/gemini-agent/<n>/agent.json`. **Futtassa mindkét fát egymás után** (nem
  `--prompt-lang` flaggel), így egy futás mindkét nyelvet szinkronban tartja, és a `--check`
  egyszerre ellenőriz mindent.
- [ ] **14.3 — FIGYELEM: már ma is előfordul elcsúszás.** A tükrök a `.md` szerkesztésekor
  csendben elavulnak. **Futtasd a `--check`-et a munka elején és végén is.**

---

## 15. Dokumentáció

- [ ] **15.1 — `README.md`.** Új szekció a két nyelvi beállításról: a 4 kombináció táblázata
  (2.3), hogy **mindkettő telepítéskor dől el és bedrótozódik** (LG2/LG17 — utólag csak
  újratelepítéssel változtatható, és a projektben semmilyen nyelvi mező nem él), valamint az
  átszivárgás-kockázat + az `output-language` blokk mint válasz. A TOC-ot is frissítsd. A
  telepítés-szekció kapja meg a két új kérdést és a flag-alapú módot.
- [ ] **15.2 — `prompts/meta-improve-prompts.md`.** A prompt-fájlok táblája és a mappaszerkezet
  egészüljön ki a `skills-hu`/`skills-en` (stb.) szimmetrikus fákkal és a `lang/` mappával; a
  `lang-parity-check.py` kerüljön be kötelező ellenőrzési lépésként (11.9).
- [ ] **15.3 — Ez a munkafájl.** Végrehajtás közben pipálj **valós időben**, és a 9.3 pontos
  leltárát, valamint a 13.2.1 glosszáriumot **ide** írd — ezek a folytatás horgonyai.

---

## 16. Elfogadási kritériumok

- [ ] **16.1 — Byte-azonossági keret (`hu`/`hu` regresszió).** Ez a legfontosabb védőháló, és
  **minden kiemelési lépés után** (9.4) futtatandó. A pillanatfelvételt a módosítás **előtt**
  készítsd:

  ```python
  # a repó gyökeréből
  import pathlib, importlib.util, hashlib
  spec = importlib.util.spec_from_file_location("ih", "prompts/scripts/install-helper.py")
  m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
  snap = pathlib.Path("/tmp/snap-x"); sums = []
  for plat in ["claude", "codex", "antigravity", "cursor"]:
      dest = snap / plat
      for f in sorted(m.skills_src_dir(".").glob("*.md")):
          m.write_markdown_skill(f, dest, src_dir=pathlib.Path("."), platform=plat)
      for p in sorted(dest.rglob("SKILL.md")):
          sums.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(snap)}")
  (snap / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")
  ```

  **Kritérium:** 56 fájl (4 platform × 14 skill), a `SHA256SUMS` a módosítás előtt és után
  **azonos**.

  **Miért 4 platform és nem 5 — de csak a 8.7-ig:** a `copilot` ma nem a
  `write_markdown_skill`-t használja, hanem saját ciklust (1.3), ezért a keret induláskor nem
  fedi; addig a Copilot-utat a 16.2 teljes próbatelepítés ellenőrzi.
  **A 8.7 egységesítés után a keret KÖTELEZŐEN kiterjed a copilotra is (LG28):**
  a `prepare_skill_content()`-en át mind az 5 platform ugyanazt a transzformációt kapja, tehát
  a hash-lista **56 → 70 fájlra** nő (5 × 14). Indok: a 9.4 kiemelés a terv legkockázatosabb
  lépése, épp ott ne legyen vak a védőháló a divergens kódúton.

  **Miért működik az átnevezésre is (7. szakasz):** a telepített fájl útvonala
  `bs-<fájlnév-stem>/SKILL.md`, tehát a **forrásmappa neve nem jelenik meg** a kimenetben (1.3).
  Ezért az átnevezés előtt/után is ugyanaz az 56 hash kell — ha eltér, az átnevezés közben
  tartalom is változott. A `m.skills_src_dir(".")` hívás a `_lang_subdir`-en keresztül mindig a
  helyes fát találja meg.

  **A 9.7 tokenizálás NEM kivétel:** a `hu`/`hu` feloldás byte-azonos a mai literálokkal
  (LG9/LG32), tehát a keret a teljes ~440 elemű cserét fedi — ez a csere legfőbb védőhálója.

  **Két ismert, ELVÁRT kivétel:** a 7.6 fixer-refaktor (tartalmi változás a `06-implement.md`-n
  és a két fixeren) és a 9.5.3 `output-language` beemelés (minden skill élére új blokk).
  Ezeknél a hash **szükségszerűen** változik; a keretet ilyenkor újra kell alapozni.

- [ ] **16.2 — Négy kombinációs próbatelepítés, scriptelve (LG20).** `hu/hu`, `en/hu`, `hu/en`,
  `en/en` × 5 platform = 20 futtatás, a flag-alapú módon egy ciklusból, dobható célmappákba.
  **A 17.2 rövidített úton ez `hu/hu` + `en/hu`-ra szűkül (10 futtatás), és a `lang-keys.json`
  ellenőrzése a §10-hez csúszik (LG24).**
  Mind a 20 fusson le hibátlanul, és ellenőrizd:
  - **nincs feloldatlan `<!-- INCLUDE:` marker** a telepített fájlokban;
  - **nincs feloldatlan nyelvi token** (LG32): `grep -r "<sec:\|<field:\|<status:"` a
    célmappákon → **0 találat**;
  - **nincs `hu` fallback figyelmeztetés** (LG12) — ha van, hiányzik egy nyelvi blokk;
  - **minden telepített skill/agent frontmatterében van `description`**, és az a **projekt**
    nyelvén (LG15) — ez az egyik legkönnyebben elrontható pont;
  - a másolt scriptek mellett ott van a **`lang-keys.json`** a helyes `lang` értékkel (LG18).

- [ ] **16.3 — `lang-parity-check.py --check --strict` → exit 0** (LG25 — a záró futás a
  szigorú mód; a napi commit-előtti futás a defaultot használja).

- [ ] **16.4 — `sync-gemini-agents.py --check` → exit 0** mindkét prompt-nyelvre.

- [ ] **16.5 — Nyelvi tisztaság-ellenőrzés az `en` fákon.** Grep magyar ékezetekre:
  ```bash
  grep -rn "[áéíóöőúüűÁÉÍÓÖŐÚÜŰ]" prompts/skills-en prompts/agents-en prompts/shared-en
  ```
  → **nulla találat** (a szándékosan meghagyott tulajdonneveket kivéve). A magyar szöveg csak
  `lang/` INCLUDE-on keresztül jöhet be, a forrásban nem. Egyszerű és nagyon hatásos ellenőrzés
  a félbehagyott fordításra.

- [ ] **16.6 — Éles próba (LG14).** Egy meglévő projektben `EN`/`HU` telepítés, majd **egy teljes
  ciklus** végigvitele (vagy legalább `02` → `05`), és annak ellenőrzése, hogy
  (a) a `spec.md`/`plan.md` **magyar** lett, (b) a kapuk lefutottak, (c) nincs angol átszivárgás
  az artefaktumokban. **Ha (c) sérül, a 9.5 `output-language` blokk erősítendő** — ez a
  legvalószínűbb hibapont az egész tervben.

---

## 17. Végrehajtási sorrend

### 17.1 Teljes sorrend (az LG1 „mind a 4 kombináció" célhoz)

| # | Szakasz | Miért itt |
|---|---|---|
| 0 | **6.** Takarítás | kevesebb fájl az átnevezési sweepben, és eltűnik a félrevezető `prompts/<language>/` minta. Saját commit. |
| 1 | **7.** Szimmetrikus átnevezés | minden további lépés a végleges mappanevekre épül. **Atomi commit.** |
| 2 | **8.** Horgonyos INCLUDE + `description` | kis, önálló kód, azonnal tesztelhető |
| 3 | **9.1–9.4** Leltár + kiemelés | fájlonként, 16.1 byte-azonossággal |
| 4 | **9.5** `output-language` blokk | a kiemelés után, mert ugyanabba a `lang/` mappába megy |
| 4b | **9.7** projekt-nyelvi tokenek (LG32) | a 9.4 után (a `lang/` blokkokban literál marad), és a §11 ELŐTT, hogy a 11.12 kapu a végleges felületet lássa. Idehozza a `status-keys.json`-t (10.3). |
| 5 | **11.** `lang-parity-check.py` | ettől kezdve minden további lépés után fut (default mód; `--strict` a záráskor — LG25) |
| 6 | **13.** Az `en` fák | fájlonként, a 13.3 lista szerint (részletekben végezhető) |
| 7 | **9.6** `lang/en/` | a projekt-nyelvi blokkok angolul |
| 8 | **10.** `status-keys.json` + script-i18n | ettől lesz működőképes a `projekt = en` |
| 9 | **14.** Gemini tükrök | mindkét nyelven |
| 10 | **12.** A telepítő | a két kérdés + flag-mód |
| 11 | **15.** Dokumentáció | |
| 12 | **16.** A teljes elfogadási sor | |

### 17.2 Rövidített sorrend, ha a cél a MIELŐBBI `EN`/`HU` újratelepítés

Az LG14 szűk céljához (`EN` prompt + `HU` projekt) **a 10. szakasz (script-i18n)
elhalasztható** — a projekt magyar, tehát a kapu-scriptek magyar stringjei érintetlenül
helyesek. A **9.6 (`lang/en/`) viszont BENNE MARAD (LG24)**, különben a paritás-kapu
11.1/11.3 pontja tartósan FAIL-t adna, és az `en/en` telepítés csendben `hu` fallbackre esne.
Minimális út:

**6 → 7 → 8 → 9.1–9.6 → 9.7 → 11 → 13 → 14 → 12 → 15 → 16**

A **9.7 a rövidített úton is BENNE VAN** (LG32): nélküle az `EN` prompt magyar szekciónév-
literálokat hordozna (16.5 FAIL ~440 helyen), vagy angolra fordítva csendben megbuktatná a
kapukat a `HU` projekten (16.6/c). A `status-keys.json`-nak itt még **csak a `sections` /
`status` értékei** kellenek — a scriptek átállítása (10.5–10.7) továbbra is halasztható.

Amit ez a rövidítés módosít az elfogadási soron:
- **16.2** → csak `hu/hu` + `en/hu` (10 futtatás), a `lang-keys.json`-ellenőrzés a §10-hez csúszik;
- a telepítő a `projekt = English` opciónál **jelezze, hogy a kapu-scriptek üzenetei még
  magyarok** (az LG12 fallback figyelmeztetés önmagában kevés a felhasználó felé).

### 17.3 Commit- és branch-stratégia (LG21)

- [x] **Előfeltétel (LG29): a munkafa rendezése két commitban a `main`-en.**
  1. kétnyelvűsítéstől független tartalmi munka: `cycle-status.md` átnevezés, `08-doc-sync.md`,
     `context-check.md`, `cycle-status.py`, `README.md`, `jegyzet.md`;
  2. a kétnyelvűsítés előkészítése: az `install-helper.py` nyelvi vezetékezése (5.1–5.4) +
     ez a tervfájl.
- [x] Nyiss **egy feature branch-et friss `main`-ről** (`git switch main && git pull && git
  switch -c feature/bilingual-prompts`) — a `main` a teljes
  migráció alatt működő állapotban marad, és a végén **egy PR**-ként olvad be.
- [ ] A branch-en belül a 17.1 lépései **külön commitok**. A **7. szakasz átnevezés saját, atomi
  commit** (`git mv` + `_lang_subdir` + `shared/` prefix-feloldás + a 64/9/3 útvonal-javítás), és
  a commit-üzenetben **külön jelöld** a 7.7 tartalmi javítást, mert az nem átnevezés.
- [x] **Minden commit előtt** fusson a 16.1 byte-azonosság (ahol értelmezhető — lásd a 16.1 két
  elvárt kivételét) és — amint létezik — a `lang-parity-check.py --check` + a
  `sync-gemini-agents.py --check` (a paritás-kapu **default** módban; a PR zárásakor
  **`--strict`** — LG25). *(A 11.9 óta ez a recept a `prompts/meta-improve-prompts.md`
  „KÉTNYELVŰ REPÓ" blokkjában is ott áll, kimásolható parancsokkal.)*

### 17.4 Hogyan folytasd friss kontextusban

1. Olvasd el **ennek a fájlnak** az 1–5. szakaszát, és a `prompts/meta-improve-prompts.md`-t.
2. Állapotfelmérés:
   ```bash
   git status --short && git branch --show-current
   ls prompts/                    # megtörtént-e a 7. szakasz átnevezés?
   grep -n "PROMPT_LANG" prompts/scripts/install-helper.py   # kész-e az 5. szakasz?
   python3 prompts/scripts/sync-gemini-agents.py --check
   ```
3. Keresd meg az **első kipipálatlan** teendőt a 17.1 (vagy 17.2) sorrend szerint.
4. Egy teendő = egy lépés: megvalósítás → a hozzá tartozó verifikáció (16.) → **pipálás ebben a
   fájlban**.
5. A 9. szakaszban **fájlonként** dolgozz, és fájlonként futtasd a 16.1 byte-azonosságot.
6. Ha nem szereplő döntéshez érsz: **állj meg és kérdezz**, majd rögzítsd `LG<n>`-ként a 3.
   szakaszban.

### 17.5 Amit ez a terv tudatosan NEM tartalmaz

- **Nincs gépi fordítás build-time** (LG13) — az `en` fa verziókezelt forrás.
- **Nincs kitüntetett, suffix nélküli fa** (LG5) — a magyar is prefixelt.
- **Nem javítunk tartalmi hibát a kiemelés közben** (9.4) — az külön kör.
- **Nem fordítjuk a (c) osztályú konzol-üzeneteket** (LG10) az első körben.
- **A rövidített úton nem halasztjuk a `lang/en/`-t** (LG24) és a **9.7 tokenizálást** (LG32) —
  csak a scriptek átállítását (§10.5–10.7).
- **Nem élesztjük fel a Node CLI-t** (LG22) — törlendő.
- **Nem nyelvesítjük az `init-project.sh`-t** (LG19) — elavult.
- **Nincs nyelvi mező a `conventions.md`-ben** (LG17), és nincs migrációs szabály (LG8).
