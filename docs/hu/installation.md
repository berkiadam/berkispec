# Installáció

← [Vissza a főoldalra](../../README-HU.md) · [Oldalindex](README.md)

A BerkiSpec keretrendszer beállítása a célprojektben rendkívül egyszerű és automatizált a mellékelt telepítő script segítségével.

> **⚠ Frissítés meglévő projektben — a ciklusvég családja NEM visszafelé kompatibilis.** A `09-merge` szétvált öt skillre (`bs-review-and-merge` · `bs-create-pr` · `bs-review` · `bs-merge` · `bs-dev-test`), és a keretnek **nincs verzió-fogalma**: nincs alias, nincs fallback a régi viselkedésre, nincs migrációs gépezet. A frissítés ezért **újratelepítés** (a telepítő a régi `bs-merge/` mappát is lecseréli), plusz a `conventions.md` új `## Review and merge` szekciójának felvétele — a `00-init-project` újrafuttatásával vagy kézzel (a sablon a `00` skillben áll). **Külön kérdés a projektben MÁR MEGLÉVŐ artefaktum-adat:** egy futó ciklus `plan.md`-jének `Fázis` oszlopában az üres cella és a `mindkettő` érték **olvasáskor továbbra is elfogadott** (a régi jelentéssel, WARN-nal) — de új plan már nem írhatja. Ezt az újratelepítés nem írja át.

## Telepítés lépései:
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

## Támogatott platformok és ágensek:
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

## Nyelvi beállítások — két független tengely

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

## Hogyan lehet használni?
A telepítés után az adott platform automatikusan beolvassa a symlinkelt definíciókat:
* **Google Antigravity CLI / Claude Code / Cursor Agent CLI / Codex CLI:** Indítsd el a CLI-t a célprojekt mappájában (Cursornál az `agent` paranccsal). A chat felületen a `/` (per) karakter leütésével előhívhatod a skillek listáját. Mindegyik skill egységesen a `berkispec - <fázis>: <leírás>` névvel fog megjelenni, így azonnal láthatod az SDD lépések sorrendjét és célját. Kezdéshez hívd meg a `bs-init-project` skillt! (Codexnél a subagenteket a `/agent` paranccsal listázhatod/válthatsz köztük.)
* **GitHub Copilot:** A Copilot Chat ablakában vagy a Copilot CLI-ben a `@` szimbólummal (pl. `@bs-init-project`) tudod közvetlenül aktiválni a kívánt fázis utasításait.

---
