```text
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                                                                      ║
    ║   ██████╗ ███████╗██████╗ ██╗  ██╗██╗███████╗██████╗ ███████╗ ██████╗║
    ║   ██╔══██╗██╔════╝██╔══██╗██║ ██╔╝██║██╔════╝██╔══██╗██╔════╝██╔════╝║
    ║   ██████╔╝█████╗  ██████╔╝█████╔╝ ██║███████╗██████╔╝█████╗  ██║     ║
    ║   ██╔══██╗██╔══╝  ██╔══██╗██╔═██╗ ██║╚════██║██╔═══╝ ██╔══╝  ██║     ║
    ║   ██████╔╝███████╗██║  ██║██║  ██╗██║███████║██║     ███████╗╚██████╗║
    ║   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚══════╝╚═╝     ╚══════╝ ╚═════╝║
    ║                                                                      ║
    ╚══════════════════════════════════════════════════════════════════════╝
```

**ENG version → [README.md](README.md)**

<!-- TOC -->

- [Berki-spec](#berki-spec)
  - [1. Két fejlesztési út — válassz a feladat mérete szerint](#1-két-fejlesztési-út--válassz-a-feladat-mérete-szerint)
    - [1.1 Mindkét út előtt (opcionális): /bs-brainstorm](#11-mindkét-út-előtt-opcionális-bs-brainstorm)
  - [2. Installáció](#2-installáció)
    - [Telepítés lépései:](#telepítés-lépései)
    - [Támogatott platformok és ágensek:](#támogatott-platformok-és-ágensek)
    - [Nyelvi beállítások — két független tengely](#nyelvi-beállítások--két-független-tengely)
    - [Hogyan lehet használni?](#hogyan-lehet-használni)
  - [3. Quick start](#3-quick-start)
    - [A keretrendszer működési elve:](#a-keretrendszer-működési-elve)
    - [Két fejlesztési út:](#két-fejlesztési-út)
    - [Alapvető parancsok (Slash Commands):](#alapvető-parancsok-slash-commands)
  - [4. Teljes berki spec flow (00–09)](#4-teljes-berki-spec-flow-0009)
    - [4.1 Magas szintű összefoglalás](#41-magas-szintű-összefoglalás)
    - [4.2 Tesztelési pontok — hol tesztelünk, és mit bizonyít](#42-tesztelési-pontok--hol-tesztelünk-és-mit-bizonyít)
    - [4.3 Modellek és effort-szintek automatikus választása](docs/hu/model-selection.md)
    - [4.4 Az 05-analyze önjavító hurok (részletes)](#44-az-05-analyze-önjavító-hurok-részletes)
    - [4.5 Az 07-validate önjavító hurok (részletes) — tesztek + kódreview](#45-az-07-validate-önjavító-hurok-részletes--tesztek--kódreview)
    - [4.6 Önjavító hurkok (analyze + validate) — közös konvenciók](#46-önjavító-hurkok-analyze--validate--közös-konvenciók)
    - [4.7 Példa prompt-folyam (egy ciklus végigvezetése)](#47-példa-prompt-folyam-egy-ciklus-végigvezetése)
  - [5. Egyszerűsített (lightweight) flow](#5-egyszerűsített-lightweight-flow)
    - [5.1 Folyamatábra](#51-folyamatábra)
    - [5.2 A három fázis röviden](#52-a-három-fázis-röviden)
    - [5.3 Két beépített kör-megszakító](#53-két-beépített-kör-megszakító)
    - [5.4 Opcionális ágensek (mind read-only, egyik sem kötelező)](#54-opcionális-ágensek-mind-read-only-egyik-sem-kötelező)
    - [5.5 Indító prompt (copy-paste)](#55-indító-prompt-copy-paste)
    - [5.6 Példa prompt](#56-példa-prompt)
  - [6. Skill-index](#6-skill-index)
  - [7. Agent-index](#7-agent-index)
  - [8. Frontmatter séma](#8-frontmatter-séma)
  - [9. conventions.md — Projekt konvenciók](#9-conventionsmd--projekt-konvenciók)
    - [Branching stratégia — ciklus = branch (a 01 fázisban)](#branching-stratégia--ciklus--branch-a-01-fázisban)
    - [Párhuzamos ciklusok — tervezési ablak worktree-vel (PW1/PW2, BD16)](#párhuzamos-ciklusok--tervezési-ablak-worktree-vel-pw1pw2-bd16)
    - [Friss alap az analyze előtt (BR1)](#friss-alap-az-analyze-előtt-br1)
    - [Integrációs frissítés a merge előtt (W2)](#integrációs-frissítés-a-merge-előtt-w2)
    - [Fázis-záró commit (PC1)](#fázis-záró-commit-pc1)
  - [10. Egy ciklus artifact fájljai](#10-egy-ciklus-artifact-fájljai)
    - [10.1 Fázisok közötti átadás (*-input-from-prev.md)](#101-fázisok-közötti-átadás--input-from-prevmd)
  - [11. docs-generated/ — élő dokumentáció (a 08-doc-sync gazdája)](#11-docs-generated--élő-dokumentáció-a-08-doc-sync-gazdája)
    - [11.1 specs/test-conventions.md — visszatérő teszt-elvárások és receptek (TC1–TC11)](#111-specstest-conventionsmd--visszatérő-teszt-elvárások-és-receptek-tc1tc11)
    - [11.2 export/ — verziózott PDF export (/bs-export-doc)](#112-export--verziózott-pdf-export-bs-export-doc)
    - [11.3 test-runs/ — cikluson kívüli teszt-futtatás (/bs-run-tests)](#113-test-runs--cikluson-kívüli-teszt-futtatás-bs-run-tests)
  - [12. Kérdéskezelés (spec-questions.md / plan-questions.md / tasks-questions.md / doc-sync-questions.md)](#12-kérdéskezelés-spec-questionsmd--plan-questionsmd--tasks-questionsmd--doc-sync-questionsmd)
  - [13. Egységes Kész státusz-lifecycle](#13-egységes-kész-státusz-lifecycle)
  - [14. Sonar minőségellenőrzés](#14-sonar-minőségellenőrzés)
  - [15. Döntési napló (imp-decision.md)](#15-döntési-napló-imp-decisionmd)
  - [16. Validációs riport (validation-report.md)](#16-validációs-riport-validation-reportmd)
  - [17. Reviewer agent (agents/reviewer.md)](#17-reviewer-agent-agentsreviewermd)
  - [18. Ágens-specifikus integráció](#18-ágens-specifikus-integráció)
  - [Függelék — A részletes folyamatábra](#függelék--a-részletes-folyamatábra)
    - [18.0 Platform-korlát: parancs-futtatás a subagentekben (EX1)](#180-platform-korlát-parancs-futtatás-a-subagentekben-ex1)
    - [18.1 Antigravity CLI (Google DeepMind)](#181-antigravity-cli-google-deepmind)
      - [18.1.1 Tervezési és naplózási folyamat (Planning Mode)](#1811-tervezési-és-naplózási-folyamat-planning-mode)
      - [18.1.2 Jogosultságok kezelése (Permissions)](#1812-jogosultságok-kezelése-permissions)
      - [18.1.3 Skillek és Ágensek indítása (TUI használat)](#1813-skillek-és-ágensek-indítása-tui-használat)
    - [18.2 Codex CLI (OpenAI)](#182-codex-cli-openai)

<!-- /TOC -->



# Berki-spec

**Berki-spec** egy **spec-driven development (SDD)** keretrendszer AI-ágensekkel való szoftverfejlesztéshez. A munkát önállóan tesztelhető **ciklusokra** bontja, és minden ciklust ugyanazon a fegyelmezett úton vezet végig — a követelmény rögzítésétől (`spec`) a technikai terven (`plan`) és a feladatlistán (`tasks`) át az implementációig, a validálásig és a merge-ig. A folyamat két építőelemből áll: **skillek** (fázis-receptek, amelyeket a fő ágens futtat) és **ágensek** (dedikált, `Task tool` subagentként hívott specialisták).

> **Státusz: alpha — még nincs stabil kiadás.** A prompt-kontraktusokat körönként keményítjük, ezért egy frissítés **töréses változást** hozhat egy már telepített projektben (átnevezett artefaktum vagy ciklusmappa, új kötelező kapu). Ha rögzített állapot kell, tagelt verzióról telepíts, vagy rögzíts egy commitot ahelyett, hogy a `main`-t követnéd.

**Mitől más, mint a piacon lévő SDD eszközök?**

A legtöbb SDD sablon egyetlen, merev „spec → terv → kód" fonalat ad. A Berki-spec ennél tovább megy — a különbség nem a fázisokban van, hanem abban, hogy **mi történik, amikor a valóság eltér a tervtől**:

- **Adaptív, kétsebességes flow.** Nagy feladatra a teljes (00–09) folyamat a minőségi kapuival; kis, jól körülhatárolt feladatra egy egyszerűsített háromfázisú út (`spec → task → implementáció`). A kettő **menet közben átjárható** — nincs felesleges ceremónia egy konfigurációs módosításhoz, és nincs alultervezés egy komplex funkciónál.
- **Önjavító minőségi hurkok, anti-„csalás" fegyelemmel.** Az `analyze`, `validate` és `review` fázis nemcsak *jelzi* a hibát, hanem levezényelt hurokban **automatikusan javítja** is. A kulcsszabály: a **kód igazodik a szerződéshez** (teszt / DoD / review-finding), **soha nem fordítva** — a hurok nem lazítja a tesztet, hogy zöld legyen. Ha valami csak a szerződés módosításával lenne megoldható, **felfelé eszkalál** a tervezési fázisba, ember elé.
- **Élő, „as-built" dokumentáció drift-követéssel.** A `docs-generated/` ciklusról ciklusra szinkronban marad a kóddal, egy **objektív konzisztencia-kapun** átvezetve, és külön nyilvántartja a megvalósult rendszer **eltéréseit a HLD/LLD szándéktól** (design-drift). A dokumentáció nem avul el csendben.
- **Megszakítás-biztos, bárhol folytatható.** Minden fázis fájlban tartja az állapotát és a nyitott kérdéseit (a listából **soha nem törlünk**, csak `[x]`-elünk), státusz-markerekkel — egy új session pontosan onnan folytatja, ahol abbamaradt.
- **Emberi kapuk a döntéseknél.** A fázisváltások **explicit jóváhagyáshoz** kötöttek: az ágens javasol és indokol, de nem „szalad el" — a scope- és irányválasztás a fejlesztőé marad.
- **Eszközfüggetlen, egyetlen forrásból.** Ugyanaz a skill/ágens definíció (single source of truth) fut Claude Code, Cursor, Antigravity és Codex alatt is.
- **Gyenge/olcsó modellekre optimalizálva.** Determinisztikus védőhálók (szűkített fix-mód belépők, kötelező ellenőrzőlisták, egyszerre egy kérdés) csökkentik a hibázás esélyét akkor is, ha nem a legerősebb modell hajtja.
- **Maximális token-megtakarítás — feladatarányos modell- és reasoning-szint-választás.** Minden lépés a hozzá **elégséges legolcsóbb ágensen** fut, **két független tengelyen** hangolva: a *modell* (melyik modell) és az *effort* (mennyi reasoning/thinking-token). A legdrágább (Opus-osztályú) modellt **egyetlen** pont kapja: a legkritikusabb reasoning, az `analyzer` konzisztencia-diagnózisa. A pontos hibalistát célzottan javító fixerek és a mechanikus futtatók **alacsony efforton** dolgoznak (a `default` modellen is), mert nekik nem kell felfedezniük a problémát. A kódkeresést, teszt-futtatást és a determinisztikus lépéseket olcsó subagentek és scriptek végzik, a fő kontextust óvva. A teljes leosztást lásd az [4.3 szekcióban](docs/hu/model-selection.md).

## 1. Két fejlesztési út — válassz a feladat mérete szerint

A felhasználónak **két útja** van; a feladat súlya dönti el, melyik a megfelelő:

1. **Teljes berki spec flow (00–09 fázis)** — a nagyobb, összetettebb fejlesztésekhez. Külön `spec.md` → `plan.md` → `tasks.md` dokumentumok, kereszt-fázisos `analyze`, `validate`, `doc-sync` és `review` minőségi kapukkal és önjavító hurkokkal. Üres projektnél a `00-init-project`, új ciklusnál a `01-add-cycles` skillel indul. Ezt írja le a README többi része.

2. **Egyszerűsített (lightweight) flow** — kis, jól körülhatárolt feladatokhoz, amelyek 3-4 lépésben megoldhatók (pl. **konfiguráció összeállítása**, **egyszerűbb script megírása**, kisebb javítás). Egyetlen háromfázisú recept: `spec-plan.md` → `tasks.md` → implementáció, a `/bs-quick-flow` skillben. Mindkét artefaktum **státusz-mezőt** hordoz, így a fázishatár commitolt tény (a `/bs-cycle-status` is ebből olvas). Nincs külön plan/bs-analyze/bs-validate/bs-doc-sync fázis; az opcionális ágenseket (`researcher`, `analyzer`, `reviewer`) csak akkor hívja, ha tényleg segítenek.

**Hogyan dönts?**

| Jellemző | Egyszerűsített flow | Teljes berki spec flow |
|---|---|---|
| Tipikus feladat | konfiguráció, egyszerű script, kisebb javítás | új funkció, több komponens, összetett logika |
| Méret | 3-4 lépésben megoldható | önálló, vertikálisan vágható ciklus(ok) |
| Dokumentumok | `spec-plan.md` + `tasks.md` (mindkettő státusz-mezővel) | `spec.md` + `plan.md` + `tasks.md` |
| Minőségi kapuk | inline + opcionális ágensek | `analyze` / `validate` / `doc-sync` / `review` hurkok |
| Belépő | `/bs-quick-flow` | `/bs-init-project` / `/bs-add-cycles` |

**Alapértelmezett flow:** a projekt jellegét a `00-init-project` fázisban tisztázzuk (termékfejlesztés vs. konfiguráció/scriptelés), és ez alapján egy **default flow** kerül a `conventions.md` `## Fejlesztési módszertan` szekciójának **Alapértelmezett flow** mezőjébe. Ez a kiindulópont — feladatonként felülbírálható.

A két út **átjárható**: ha az egyszerűsített flow közben kiderül, hogy a feladat túlnő rajta (nagyobb kódírás, több komponens, összetett tervezés), a skill megállítja a munkát és **átirányít a teljes folyamatra** (`01-add-cycles`). Fordítva is: a `01-add-cycles` és a `03a-write-code-plan` jelzi, ha a feladat túl egyszerű a teljes ciklushoz, és javasolja az egyszerűsített flow-t.

### 1.1 Mindkét út előtt (opcionális): `/bs-brainstorm`

A két út **közös előszobája** a `/bs-brainstorm` segédparancs — arra az esetre, amikor még nem a *méret* a kérdés, hanem az, hogy **mit és hogyan** akarunk egyáltalán. („Hogyan valósítsunk meg egy központi cert kezelést?", „Érdemes-e kiszervezni az auth-ot?") Ez a rés a `00–09` flow **előtt** van: a `01-add-cycles` már azt feltételezi, hogy tudod, mit akarsz (csak ciklusokra kell bontani), a `/bs-quick-flow` pedig azt, hogy a feladat kicsi és világos.

**Mit tesz:**
- **Orientálódik** a projektben: `conventions.md`, `docs-generated/system-overview.md` (as-built igazság), `docs-generated/README.md` (mappa-index), `specs/roadmap.md` — téma szerint az `architecture.md` és a `design-drift.md`. A teljes `specs/` fa bedarálása tilos (BS6).
- **A kódbázis-feltárást olcsó, párhuzamos `researcher` subagentekkel** végzi (Mód B, read-only, legolcsóbb tier, „soha nem nyers fájltartalom") — a beszélgetés kontextusát így egy leletlista terheli, nem fájlok tucatja (BS7).
- **Beszélget, nem monologizál:** egyszerre **egy** kérdés, minden javaslatnál **2–3 alternatíva trade-offokkal + explicit ajánlás**, kötelező illesztés a meglévő rendszerhez és a `conventions.md`-hez, és tilos az igenelés — a fel nem hozott kockázat az ágens hibája (BS8–BS13).
- **Perzisztál:** a session anyaga a `.bs-brainstorm/brainstorm-NN-<slug>.md` munkafájlba kerül, fix csontvázzal (*Cél · Feltárt tények forrással · Alternatívák · Döntések · Nyitott kérdések · Javasolt ciklus-vágás · Napló*). Minden érdemi kör után **bővül** — soha nem íródik újra (BS14). Így egy `/clear`, összeomlás vagy napokkal későbbi visszatérés után is folytatható: `/bs-brainstorm folytassuk a 04-est`.

**Kemény korlátok (BS1):** kódot nem ír, `git`-et nem futtat, és a `.bs-brainstorm/` mappán kívül **egyetlen fájlt sem** módosít — egyetlen kivétellel: az első futáskor felajánlja a `.bs-brainstorm/*` bejegyzés felvételét a `.gitignore`-ba (jóváhagyás után, egyszer). A végén **javasol**, de nem lép be a következő skillbe.

**A híd a flow felé (BS18):** a nyers munkafájl **helyi és gitignore-olt** (nyers gondolkodás, nem leadandó) — ami megőrzésre érdemes, az a ciklus `cycle-design-input.md`-jébe desztillálódik, és *az* kerül commitba:

```
/bs-brainstorm hogyan legyen központi cert kezelés
        ↓                      .bs-brainstorm/brainstorm-04-central-cert.md   (gitignore-olt)
/bs-add-cycles brainstorm: 04
        ↓                      specs/cycle-NN-<name>/cycle-design-input.md    (commitolt)
/bs-write-spec
```

A `01-add-cycles` a `## 6. Javasolt ciklus-vágás` szekciót a roadmap-javaslat kiindulásának veszi, a `## 5. Nyitott kérdések` kipipálatlan tételeit pedig **kérdésként** teszi fel — amit a munkafájl megválaszol, azt nem kérdezi meg újra. **Egy híd, egy irány:** a `02-write-spec` nem a brainstormot olvassa, hanem a `cycle-design-input.md`-t.

## 2. Installáció

A BerkiSpec keretrendszer beállítása a célprojektben rendkívül egyszerű és automatizált a mellékelt telepítő script segítségével.

> **⚠ Frissítés meglévő projektben — a ciklusvég családja NEM visszafelé kompatibilis.** A `09-merge` szétvált öt skillre (`bs-review-and-merge` · `bs-create-pr` · `bs-review` · `bs-merge` · `bs-dev-test`), és a keretnek **nincs verzió-fogalma**: nincs alias, nincs fallback a régi viselkedésre, nincs migrációs gépezet. A frissítés ezért **újratelepítés** (a telepítő a régi `bs-merge/` mappát is lecseréli), plusz a `conventions.md` új `## Review and merge` szekciójának felvétele — a `00-init-project` újrafuttatásával vagy kézzel (a sablon a `00` skillben áll). **Külön kérdés a projektben MÁR MEGLÉVŐ artefaktum-adat:** egy futó ciklus `plan.md`-jének `Fázis` oszlopában az üres cella és a `mindkettő` érték **olvasáskor továbbra is elfogadott** (a régi jelentéssel, WARN-nal) — de új plan már nem írhatja. Ezt az újratelepítés nem írja át.

### Telepítés lépései:
1. Nyiss meg egy terminált a `berkispec` repository gyökerében.
2. Futtasd a telepítő scriptet:
   * **Linux/macOS:**
     ```bash
     ./install.sh
     ```
   * **Windows (PowerShell):**
     ```powershell
     .\install.ps1
     ```
3. A script interaktív módon üdvözöl, és bekéri a célprojekted gyökérmappáját.
   * *Tipp:* Az útvonal beírása közben a **Tab** billentyűvel automatikusan kiegészítheted a mappaneveket, míg a **Tab kétszeri megnyomásával** kilistázhatod az aktuális könyvtár tartalmát.
   * **Újratelepítéskor a legutóbbi célmappa automatikusan fel van kínálva** — Linux/macOS-en előre kitöltve jelenik meg (Enter = elfogadás, nyilakkal szerkeszthető), Windowson a script kiírja és üres Enterre elfogadja. A telepítő ehhez a repo gyökerében lévő **`history`** fájlt használja (`LAST_PROJECT_PATH`, `LAST_PLATFORM`, `LAST_INSTALL`). A fájl gépfüggő, ezért a `.gitignore` kizárja; ha a benne tárolt mappa időközben megszűnt, a script jelzi és újat kér.
4. Válaszd ki az általad használt AI agent platformot (1–6).
5. Válaszd ki a **két nyelvet** — lásd a *Nyelvi beállítások* szekciót lentebb. Mindkettőnél van alapértelmezés, Enterrel elfogadható:
   * **Promptok nyelve** (amit az ágens *olvas*): `1) English [alapértelmezett]` / `2) Magyar`
   * **Projekt nyelve** (amit az ágens *ír*): `1) Magyar [alapértelmezett]` / `2) English`

**Nem interaktív (scriptelt) telepítés.** Ha **egyetlen** flaget sem adsz meg, a fenti interaktív út fut változatlanul. Flagekkel viszont automatizálható:

```bash
./install.sh --platform claude --prompt-lang en --project-lang hu --path ~/projekt
```

| Flag (`install.sh`) | PowerShell | Érték | Alapértelmezés |
|---|---|---|---|
| `--platform` | `-Platform` | `claude` \| `codex` \| `antigravity` \| `cursor` \| `copilot` | — (kérdezi) |
| `--prompt-lang` | `-PromptLang` | `hu` \| `en` | `en` |
| `--project-lang` | `-ProjectLang` | `hu` \| `en` | `hu` |
| `--path` | `-Path` | a célprojekt könyvtára | — (kérdezi) |
| `--force` | `-Force` | ütközésnél felülír | — |
| `--help` | `-Help` | súgó | — |

Részlegesen megadott flagek esetén a megadottakat használja, a többit interaktívan kérdezi. **Ütközésnél `--force` nélkül a nem interaktív mód MEGÁLL** — nem ír felül csendben.

### Támogatott platformok és ágensek:
A keretrendszer öt népszerű fejlesztő platformra képes beállítani a környezetet:

1. **Google Antigravity CLI:**
   * A projekt gyökerében létrehozza a `.agents/` konfigurációs mappát.
   * Az ágenseket a `.agents/agents/<név>/agent.json` mappaszerkezetbe, a skilleket pedig a `.agents/skills/bs-<név>/SKILL.md` könyvtárba linkeli be.
   * ⚠️ **Csak interaktív használatra.** Mérve 2026-09-22-én, az 1.107.0-s CLI-vel: **nincs headless mód** (az `antigravity chat "<prompt>"` GUI chat-session-t nyit), ezért az Antigravity **nem tudja CI-futtatón végigvinni a ciklust**. Ez kizárólag a **központosított SDD-t** érinti, ahol a CI hajtja a `bs-review`/`bs-merge`-öt: ott válaszd a `CI agent: command` ágat (lásd a 9. szakasz `## Review and merge` leírását). Lokális, interaktív munkára az Antigravity teljes értékű.
2. **Claude Code:**
   * A projekt gyökerében létrehozza a `.claude/` konfigurációs mappát.
   * Az ágenseket a `.claude/agents/<név>.md` (Markdown) formátumban linkeli be, a skilleket pedig a `.claude/skills/bs-<név>/SKILL.md` alá.
3. **Cursor (Agent CLI):**
   * A projekt gyökerében létrehozza a `.cursor/` konfigurációs mappát.
   * A subagenteket a `.cursor/agents/<név>.md` (Markdown) formátumban linkeli be (a read-only agentek `readonly: true`-t kapnak), a skilleket pedig a `.cursor/skills/bs-<név>/SKILL.md` alá.
4. **GitHub Copilot (CLI & IDE):**
   * A projekt gyökerében létrehozza a `.github/` konfigurációs mappát.
   * Az ágenseket a `.github/agents/<név>.agent.md` fájlként linkeli be, a skilleket pedig globális utasításokként a `.github/instructions/bs-<név>.instructions.md` fájlba rendezi.
5. **Codex CLI:**
   * A subagenteket a `.codex/agents/<név>.toml` **TOML** fájlokként hozza létre (natív `model` + `model_reasoning_effort` mezőkkel; a read-only agentek `sandbox_mode = "read-only"`-t kapnak).
   * A skilleket a `.agents/skills/bs-<név>/SKILL.md` alá helyezi — a Codex a projekt-szintű skilleket innen olvassa.
   * ⚠️ **Figyelem:** a Codex és az Antigravity **közös** `.agents/skills/` mappát használ, ezért egy projektbe a kettő közül csak az egyik telepíthető. A telepítő figyelmeztet és rákérdez, ha a másik már jelen van.

### Nyelvi beállítások — két független tengely

A keretrendszer **két, egymástól független** nyelvi beállítást ismer. Nem ugyanaz a kettő, és **nem is kell egyezniük**:

| Beállítás | Mit határoz meg | Alapértelmezés |
|---|---|---|
| **Prompt nyelve** | Milyen nyelven vannak az **instrukciók, amiket az ágens olvas** (a `skills-*` / `agents-*` / `shared-*` fa nyelve). A te dokumentumaidat nem érinti. | **English** |
| **Projekt nyelve** | Milyen nyelven **ír az ágens**: `spec.md`, `plan.md`, `tasks.md`, `conventions.md`, riportok, `docs-generated/` — és amit **neked válaszol** a chatben. | **Magyar** |

**A négy kombináció:**

| Prompt | Projekt | Mikor ez a jó |
|---|---|---|
| **EN** | **HU** | *Az alapértelmezés.* Magyar csapat, magyar leadandó dokumentáció — de az ágens angol instrukciót kap, ami olcsóbb tokenben és amit a gyengébb/olcsóbb modellek pontosabban követnek. |
| HU | HU | Ha a prompt-szöveget is magyarul akarod olvasni/karbantartani. |
| EN | EN | Nemzetközi projekt. |
| HU | EN | Ritka, de érvényes: magyar karbantartó, angol leadandó. |

**Mindkettő telepítéskor dől el, és BEDRÓTOZÓDIK a telepített promptokba.** A projektbe **semmilyen nyelvi mező nem kerül** — sem a `conventions.md`-be, sem máshova —, ezért:

- utólag **csak újratelepítéssel** változtatható;
- meglévő projektnél **nincs migrációs teendő**: amíg nem telepítesz újra, minden a régiben marad;
- a telepítő **záró összefoglalója kiírja mindkét nyelvet** — ez az egyetlen hely, ahol szembesülsz a választásoddal.

> **A fő kockázat: nyelvi átszivárgás.** Angol instrukció + magyar projekt esetén a modell (különösen a gyengébb) hajlamos angol szavakat szivárogtatni a magyar dokumentumba, vagy az egész artefaktumot angolul megírni. Az ez elleni fő fegyver az **`output-language` blokk**: minden skill és minden agent legelejére — közvetlenül a H1 után — bekerül egy blokk, amely **a projekt nyelvén** mondja ki, hogy mit kell azon a nyelven írni (artefaktumok, a felhasználónak szóló mondatok), mi marad angol (azonosítók, fájlnevek, parancsok, szabály-ID-k), és hogy **a keverés javítandó hiba**. A célnyelven megfogalmazott szabály egyszerre utasítás és nyelvi horgony — mérhetően jobban tart, mint egy angolul megfogalmazott „write in Hungarian".

> **A kapu-scriptek is követik a projekt nyelvét.** A determinisztikus kapuk (riport-kapu, DoD-ellenőrzés, kör-napló, analyze-kapu, TC8) nem hardcode-olt magyar szövegre illesztenek: a telepítő a választott projekt-nyelv szótárát a scriptek mellé írja (`lang-keys.json`), és a scriptek abból veszik a szekciócímeket, mezőneveket és státusz-értékeket. Amit *keresnek* és amit az artefaktumba *írnak*, tehát a projekt nyelvén van. A bemenetük ugyanakkor **nyelvfüggetlen**: mindkét nyelv alakját elfogadják, így egy magyarul indult projekt angol újratelepítés után sem esik ki.
>
> **⚠️ Egy maradék `projekt = English` mellett:** a kapu-scriptek **konzol-üzenetei** magyarok (ezek a futtatónak és az ágensnek szólnak, nem kerülnek artefaktumba). A telepítő ezt a választásnál külön jelzi.

### Hogyan lehet használni?
A telepítés után az adott platform automatikusan beolvassa a symlinkelt definíciókat:
* **Google Antigravity CLI / Claude Code / Cursor Agent CLI / Codex CLI:** Indítsd el a CLI-t a célprojekt mappájában (Cursornál az `agent` paranccsal). A chat felületen a `/` (per) karakter leütésével előhívhatod a skillek listáját. Mindegyik skill egységesen a `berkispec - <fázis>: <leírás>` névvel fog megjelenni, így azonnal láthatod az SDD lépések sorrendjét és célját. Kezdéshez hívd meg a `bs-init-project` skillt! (Codexnél a subagenteket a `/agent` paranccsal listázhatod/válthatsz köztük.)
* **GitHub Copilot:** A Copilot Chat ablakában vagy a Copilot CLI-ben a `@` szimbólummal (pl. `@bs-init-project`) tudod közvetlenül aktiválni a kívánt fázis utasításait.

---


## 3. Quick start

A BerkiSpec egy fegyelmezett, spec-driven development (SDD) keretrendszer AI-ágensekkel való páros programozáshoz.

### A keretrendszer működési elve:
* **Ciklusok (Cycles):** A fejlesztést jól körülhatárolt, egyértelmű céllal leírható, könnyen kézben tartható egységekre (ciklusokra) osztjuk. Minden új ciklus saját Git branch-et kap, és a ciklus összes tervezési és naplózási dokumentuma a projekt gyökerében lévő `specs/cycle-NN-<cycle-name>/` mappába kerül.
* **Fázisok (Phases):** Minden ciklus szigorú fázisokra van bontva, amelyek végigvezetik a folyamatot a követelményektől a megvalósításig és a merge-ig.

### Két fejlesztési út:
A feladat összetettségétől függően kétféle flow áll rendelkezésre:
1. **Teljes SDD Flow:** Részletes specifikációt (`spec.md`), technikai tervet (`plan.md`) és feladatlistát (`tasks.md`) készít, valamint automatikus önjavító minőségi hurkokat (analyze, validate, review) futtat.
2. **Könnyű (Lightweight) Flow:** Kisebb módosításokhoz, konfigurációkhoz vagy egyszerű scriptekhez. Egy lépésben fut le, nincs külön fázisbontása.

### Alapvető parancsok (Slash Commands):
A telepítés után a platform chat felületén a `/` karakter leütésével érheted el a skilleket:

* **`/bs-init-project`**: A projekt legelső inicializálása (létrehozza a `conventions.md` fájlt).
* **`/bs-add-cycles`**: Új fejlesztési ciklus hozzáadása az ütemtervhez (`roadmap.md`).
* **`/bs-write-spec`**: Követelmények rögzítése, új ciklus specifikációjának elkészítése (`spec.md` + `spec-questions.md`).
* **`/bs-write-code-plan`**: A technikai megvalósítási terv **kód-oldala** (`plan.md` kód-szekciói + `plan-questions.md`) — koordináták, tervezett módosítások, konfiguráció, séma.
* **`/bs-write-test-plan`**: Ugyanannak a `plan.md`-nek a **teszt-fele** — `TS-NN` forgatókönyvek, gépi futtatási tábla, környezet-felkészítés, tesztfájl-adatlapok.
* **`/bs-write-tasks`**: A technikai terv lebontása mérhető feladatokra (`tasks.md` + `tasks-questions.md`).
* **`/bs-analyze`**: Kereszt-fázisos konzisztencia-ellenőrzés és automatikus javítás (spec/plan/tasks egyezés).
* **`/bs-implement`**: Tényleges kódfejlesztés a feladatlista alapján, a haladás rögzítésével a `tasks.md`-ben.
* **`/bs-validate`**: Tesztek, lint, build **és kódreview** (reviewer agent) ellenőrzése egyetlen automatikus javító hurokban (sikeres futtatás után 'Kész' státusz).
* **`/bs-doc-sync`**: Az élő dokumentáció (`docs-generated/`) és README-k szinkronizálása a kódváltozásokkal, valamint a `specs/test-conventions.md` (visszatérő teszt-elvárások és receptek) karbantartása.
* **`/bs-review-and-merge`**: A ciklus lezárása **egy lépésben**, ha nincs PR feladás (`PR submission: no`): a fő branch behozása a ciklus ágába → **post-merge teszt-kör** (`VP2`: tesztek + Sonar) → beolvasztás kötelező felhasználói megerősítéssel (RD8). A kódreview már a `/bs-validate`-ben lefutott.
* **`/bs-create-pr` → `/bs-review` → `/bs-merge`**: ugyanez **három lépésben**, ha van PR feladás (`PR submission: yes`) — a PR megnyitása, a PR-en futó (központosított SDD-ben **gépi**) review, végül a beolvasztás a `VP2` kör után. A `VP2` mindkét úton a fő branch-re juttatás **előtti** kapu.
* **`/bs-dev-test`** *(opcionális, csak központosított úton)*: a sikeres merge után telepít egy integrált teszt-környezetbe, és **valódi e2e teszteket** futtat rá (`VP3`). Ha be van kapcsolva, a ciklus ennek a körnek a zöldjével zárul.
* **`/bs-cycle-status`**: Ciklusok státuszának ellenőrzése (interaktív TUI vagy parancssori státusz).
* **`/bs-brainstorm`**: Feltáró ötletelés és közös tervezés **a spec előtt** — perzisztens munkafájllal (`.bs-brainstorm/`), olcsó `researcher` feltárással; a végén átad a `/bs-add-cycles`-nak vagy a `/bs-quick-flow`-nak.
* **`/bs-quick-flow`**: Az egyszerűsített (lightweight) flow elindítása kis feladatokhoz (spec → task → implementáció).
* **`/bs-export-doc`**: Verziózott PDF export a markdown doksikból (mermaid ábrákkal együtt) az `export/` mappába — paraméter nélkül az `architecture.md`-ből és a `system-overview.md`-ből.
* **`/bs-manual-test-plan`**: **Kézi tesztterv** összeállítása a ciklushoz (`manual-test-plan.md`): komponens-indítás, tesztadatok, kézi hívási szekvenciák (`curl` + `.http`), elvárt eredmények és az automata tesztek eredményének helye. Két mód: `Tervezett` (implementáció előtt, a `plan.md` alapján) vagy `As-built` (validálás után, a kódhoz ellenőrizve). Előfeltétele az `analyze-report.md` `PASS` státusza; nem fázis, nem változtat ciklus-státuszt, és bármikor újrafuttatható (a kézi kiegészítéseket megőrzi).
* **`/bs-run-tests`**: **Teszt-futtatás cikluson kívül**, kategóriánként (`unit`, `rest-e2e`, `ui` — a projekt szótára szerint). A `conventions.md` `## Teszt-futtatás` szekciójának projekt-szintű táblájából futtat, és a gitignore-olt `test-runs/<kategória>/<UTC-időbélyeg>/<env>/` fába ír, kategóriánkénti `latest.json` mutatóval. Nem fázis, és az eredménye **soha nem ciklus-bizonyíték** — lásd a 11.3 szakaszt.

---
