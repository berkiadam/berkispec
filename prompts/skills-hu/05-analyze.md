---
phase: 05
name: bs-analyze
description: "berkispec - 05. Használd az implementáció előtt (Phase 05), ha a tasks.md 'Implementálásra kész'. Kereszt-fázisos konzisztencia-kapu a spec.md/plan.md/tasks.md között: subagentekkel (analyzer, *-fixer) azonosítja és automatikusan javítja az ellentmondásokat. Létrehozza az 'analyze-report.md'-t (PASS/FAIL)."
prerequisites:
  - "specs/cycle-NN-<name>/tasks.md státusz: Implementálásra kész"
output:
  - "specs/cycle-NN-<name>/analyze-report.md (PASS / FAIL)"
prev: bs-write-tasks
next: bs-implement
subagents:
  - "agents/analyzer.md"
  - "agents/analyzer-exec.md"
  - "agents/spec-fixer.md"
  - "agents/plan-fixer.md"
  - "agents/tasks-fixer.md"
shared:
  - "shared/phase-commit.md"
scripts:
  - "scripts/analyze-gate-check.py"
---
# 05 — Analyze (kereszt-fázisos konzisztencia ellenőrzés + önjavító hurok)
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

Spec driven development-ben fejlesztünk szoftvert. A fejlesztés ciklusokra van bontva. Minden ciklus egy önállóan lefejleszthető, önállóan tesztelhető részegysége a teljes implementációnak.

Ez a folyamat **5. fázisa (0–9)**: 0-init · 1-ciklusok · 2-spec · 3-plan · 4-tasks · **5-analyze ←** · 6-implement · 7-validate · 8-doc-sync · 9-review.

---

## Cheat sheet

| Szekció | Egy mondatban |
|---|---|
| Előfeltétel | `tasks.md` = `Implementálásra kész`, `conventions.md` létezik, tiszta munkafa. |
| Friss alap (BR1) | Ha a fő branch előrement a ciklus ága óta, a fázis **behozza** (rebase / merge a push-állapot szerint) az analyze ELŐTT — különben elavult fán validálna. Ha nem ment előre, az előzményhez nem nyúl. |
| Szereped | **Orchestrátor (read-only):** te magad tervezési dokumentumot nem szerkesztesz — vezényelsz, riportot írsz, kérdezel, státuszt fordítasz. |
| Mechanikus kapu | Minden futás előtt `analyze-gate-check.py` (plan-ID ↔ task-hivatkozás, marker, `⟂`, `DoD-NN`, kötelező táblák, **futtatott artefaktumok, plan-horgonyok, artefaktum-hang**) — a `Must Fix` találatai a szkript célfázisával mennek a hurokba, a `## Leltár` blokkja pedig az `analyzer` bemenete (AG3). |
| Analyzer subagentek | A read-only kereszt-vizsgálatot **két párhuzamos** subagent végzi: `agents/analyzer.md` (1–5. kategória) és az `analyzer-exec` subagent (6. kategória, végrehajthatóság) — te a két megállapítás-listát fésülöd össze (E). |
| Fixer-subagentek | A javítást a `agents/{spec,plan,tasks}-fixer.md` wrapperek végzik (= 02/03/04 fázis Fix-módja); ők írják a tervezési dokumentumokat. |
| Eredmény | `analyze-report.md` PASS vagy FAIL, súlyossági besorolással + Hurok-napló. |
| Egy analyzer-futás / iteráció | Az analyzer futása **mindig teljes**; a 2. futástól megkapja az előző `Must Fix` listát (verifikáció) és a `git diff`-et (navigáció) — de nem szűkíti rá magát (D10). A downstream re-deriválás **feltételes** (D11). |
| FAIL | **Önjavító hurok indul:** legkorábbi érintett célfázis → fixer-subagent → downstream re-deriválás (`02→03→04`) → újra-analyze, amíg PASS — `max X = 3` iterációval. |
| Kérdés-megállás | Ha a fixer nyitott kérdést jelentett: az orchestrátor (te) kérdezed a felhasználót `FÁZIS/Knn` fejléccel, beírod a választ, újraindítod a fixert — a hurok **folytatódik** (nem hiba). |
| PASS | Tovább a 06-implement fázisra. Commit: a hurok végén egyetlen `cycle-NN: 05-analyze`. |
| Fázis-záró commit | **Kötelező, minden lezáró ágon** (PASS és FAIL egyaránt) — a *Fázis-záró commit* szekció eljárása szerint (PC1). Commit nélkül a fázis nincs lezárva. |

---

## Szereped: orchestrátor (read-only invariáns)

A `05-analyze` egy **vezénylő** fázis. Két dolgot tarts észben végig:

1. **Te magad nem szerkesztesz tervezési dokumentumot** (`spec.md`, `plan.md`, `tasks.md`). Minden tartalmi javítást a fixer-subagentek (= a 02/03/04 fázisok Fix-módja) végeznek. Az egyetlen fájl, amit te írsz, az `analyze-report.md`, és az egyetlen közvetlen módosításod a tervezési dokumentumokon a **státusz-mező fordítása** (a `[analyze-loop]` marker fel- és levétele, lásd lent).
2. **A read-only diagnózis a `analyzer` subagenté.** Te a megállapítás-listáját olvasod és döntesz PASS / FAIL-ról, majd FAIL esetén levezényled a javító hurkot.

Így a fázis felelőssége tiszta: **diagnózis (analyzer) → vezénylés (te) → javítás (fixerek)**, mindegyik a maga helyén.

---

## Előfeltétel

0. **Ciklus-beazonosítás:** ha a felhasználó megadott ciklust/fájlt, azt használd; különben a legfrissebb `specs/cycle-*` mappát ajánld fel megerősítésre — <!-- INCLUDE:lang/common.md#ciklus-beazonositas --> — és várj a válaszra, mielőtt továbblépsz.

1. **`conventions.md` létezés-ellenőrzés:** olvasd be a projekt gyökerében a `conventions.md`-t. Ha nem létezik, **STOP** — jelezd a felhasználónak, hogy térjenek vissza a `00` projekt inicializálás fázishoz, és ne folytasd.

2. **Tasks státusz:** olvasd be a `specs/cycle-NN-<cycle-name>/tasks.md` státuszát. **Ha nem `Implementálásra kész`, STOP** — a task lista még nem zárult le. Jelezd, és térjenek vissza a `04` tasks fázishoz. (Kivétel: ha a státusz `Implementálásra kész [analyze-loop]` markert visel, egy korábbi analyze-hurok szakadt meg — lásd „Folytatás megszakított futás után".)

3. **Munkafa-ellenőrzés (csak VCS esetén):** futtasd: `git status --short`. Ha van commitálatlan változtatás:
   - Listázd ki az érintett fájlokat.
   - Jelezd: *"Az analízis hurok módosíthatja a tervezési dokumentumokat; a tiszta munkafa megkönnyíti a visszakövetést."*
   - Kérdezd meg: *"Commitáljam ezeket most, vagy folytassam?"* — egy kérdés, várj a válaszra, majd folytasd. (No-VCS projektben kimarad.)

4. **🔴 Friss alap (BR1 — csak VCS esetén, feltételes):** az analyze értéke abból jön, hogy a tervet a **tényleges** kódbázishoz méri (horgonyok `path:sor`, futtatott artefaktumok létezése, plan↔kód konzisztencia). Ha a fő branch időközben előrement (másik ciklus merge-elődött, hotfix érkezett), akkor egy elavult fán validálnál — a zöld eredmény hamis. Ellenőrizd:

   ```bash
   git fetch origin
   git log --oneline $(git merge-base HEAD origin/main)..origin/main
   ```

   _Remote nélküli (csak lokális) repóban az `origin/main` helyett a lokális `main`-nel dolgozz, `git fetch` nélkül. A `main` helyére a `conventions.md` `## Git és branching konvenciók` **Fő branch** mezője kerül._

   - **Üres lista** → nincs teendő, folytasd. (A párhuzamos tervezési ablakban ez a normál eset: amíg a másik ciklus nincs merge-elve, a fő branch nem mozdul.)
   - **Nem üres** → hozd be a fő branch-et a ciklus ágába **az analyze ELŐTT**:
     - a branch **nincs pusholva / nincs rá PR** (`git rev-parse --verify origin/feature/cycle-NN-<cycle-name>` hibát ad) → `git rebase origin/main`,
     - a branch **pusholva van vagy PR nyitva** → `git merge origin/main` (a rebase force-push-t igényelne).

     A behozás **előtt** jegyezd fel a ciklus ágának csúcsát (`PRE=$(git rev-parse HEAD)`). Egy sorban jelezd, mit hoztál be (`git log --oneline` a behozott commitokról) — **külön engedélyt ne kérj**, a ciklus saját ágán dolgozol, ez nem destruktív. **Konfliktus esetén STOP**: listázd az ütköző fájlokat, és kérj döntést; a generált doksit (`docs-generated/`) és a `specs/test-conventions.md`-t **ne** kézzel oldd fel — az a `08` dolga.

   - **A behozás után állítsd elő a REBASE-FÁJLLISTÁT (BR1/a):**
     ```bash
     git diff --name-only "$PRE" HEAD -- . ':(exclude)specs/*'
     ```
     Ez a másik ciklusból/hotfixből érkezett **forrás-, teszt- és konfigfájlok** listája. Ha nem üres, **mindkét analyzer-subagent bemenetébe** be kell kerülnie (lásd *„A két analyzer-subagent"* → **Rebase-fájllista**). Ha üres (csak más ciklusok `specs/` mappái jöttek be), nincs teendő.
     _Fájllistát adj át, **ne a teljes diffet** — a subagent a szükséges részleteket maga olvassa be (AG3)._

   > **Ne rebase-elj feltétel nélkül.** Ha a fenti lista üres, a branch előzményéhez **nem nyúlsz** — az analyze önjavító hurokban többször is lefuthat, és a fölösleges előzmény-átírás pusholt ágon force-push-t provokálna.

   **Miért itt:** ez a fázis az **alap-konzisztencia kapuja**. A `06` párhuzamos-ciklus kapuja (PW2) ezért nem külön rebase-lépést ír elő, hanem azt, hogy a `06` előtt legyen **friss `05` `PASS`** — a behozást maga az `05` végzi el.

---

## Folytatás megszakított futás után

**A folytatás első analyze-futása verifikációs lista NÉLKÜL indul** — nem tudhatod, hol szakadt meg a javítás, így nincs értelmes „előző kör". A futás — mint mindig — teljes, és a mechanikus kapu (0. lépés) is fut.

Az analyze **diagnózisa** read-only, de a hurok már módosíthatta a tervezési dokumentumokat. A folytatást a `[analyze-loop]` státusz-marker, a `*-questions.md` nyitott kérdései és az `analyze-report.md` Hurok-naplója együtt teszi rekonstruálhatóvá. Döntési fa — **ebben a sorrendben**:

```
1. Visel valamelyik tervezési dokumentum (spec.md / plan.md / tasks.md)
   `[analyze-loop]` státusz-markert?
   → Igen → a hurok megszakadt. NE kezdj új analízist elölről.
     a) Olvasd be az analyze-report.md Hurok-napló szekcióját:
        melyik iterációnál és melyik fázisnál állt meg.
     b) Olvasd be az érintett *-questions.md-t: van-e nyitott [ ] kérdés?
        → Ha igen: a hurok kérdés-megállásnál állt. Tedd fel a kérdést a
          felhasználónak (fázis-fejléccel), vezesd át, majd folytasd a hurkot
          ugyanannál az iterációnál.
        → Ha nincs nyitott kérdés: a fixer befejezte a javítást, de a
          re-deriválás vagy az újra-analyze maradt el. Folytasd a downstream
          re-deriválással, majd futtasd újra az analyze-t.

2. Nincs [analyze-loop] marker, de létezik analyze-report.md.
   → Ha státusza PASS: az analízis lezárult, tovább a 06-ra.
   → Ha státusza FAIL és nincs marker sehol: a hurok lezárult max X feladással
     (lásd a report Hurok-naplóját). Jelezd a felhasználónak a megrekedt
     állapotot — ne indíts automatikusan új hurkot megerősítés nélkül.
   → Ha a report félbeszakadtnak tűnik (nincs minden kategória kitöltve) és
     nincs marker: töröld a részleges riportot, és kezdd elölről az analízist.

3. Nincs analyze-report.md és nincs marker.
   → Kezdd az analízist az "Feladatod" szerint.
```

---

## Feladatod

Ellenőrizd, hogy a ciklus tervezési dokumentumai (`spec.md`, `plan.md`, `tasks.md`) **konzisztensek egymással és a `conventions.md`-vel**, mielőtt az implementáció megkezdődne — és ha nem, **vezényeld le a javításukat** egy önjavító hurokban, amíg konzisztenssé válnak.

**Ne implementálj semmit.** Ez a sanity check (és szükség esetén javító hurok) az implementáció előtt.

A diagnózis **5 kategóriában** keres problémát (a `analyzer` subagent végzi):

1. **Duplikációk** — ugyanaz a döntés a plan-en belül többször; a `tasks.md` újra leírja a plan teszteset-lépéseit; redundáns task. **A spec kidolgozott artefaktumának szó szerinti átvétele a plan-be NEM duplikáció** (KX3) — az a kötelező önhordóság.
2. **Ambiguitás** — vágy fogalmak, hiányzó mérőszámok, nem mérhető elfogadási feltétel.
3. **Alulspecifikáció** — hiányzó elfogadási feltétel, meghatározatlan komponens, taskhoz nem rendelhető plan-szekció.
4. **Konvenció-ütközések** — a `conventions.md`-vel szembeni eltérés (tech stack, naming, teszt eszköz, merge stratégia, struktúra).
5. **Lefedettségi hiányok** — követelmény ↔ task egymáshoz rendelés: van-e spec-követelmény, amelyhez nem tartozik task, vagy task, amely nem vezethető vissza a planre.

---

## Kontextus betöltési szabályok

- A kereszt-vizsgálat sok fájl együttes olvasását igényli — **kötelező a két diagnózis-subagent indítása, egyetlen üzenetben, párhuzamosan** (E): az `analyzer` subagent (1–5. kategória, a `spec.md` + `plan.md` + `tasks.md` + `conventions.md` négyesen) és az `analyzer-exec` subagent (6. kategória, a `plan.md` + `tasks.md` + a kapu leltára hármasból). Mindkettő **kizárólag a strukturált megállapítás-listát adja vissza** (a nyers fájltartalom nem terheli a fő kontextust).
- A rendszerpromptjukat a platform **telepített agent-definíciója** adja (`analyzer`, `analyzer-exec`) — ezeket a neveken hívd, ne keresd őket fájlként a projektben.
- **Add át a kapu kimenetének megfelelő blokkját mindkét subagentnek, szó szerint:**
  - `analyzer-exec` → a **`## Leltár`** (`[ARTEFAKTUM]` / `[HORGONY]` / `[HANG-GYANÚ]` / `[TESZT-ÍGÉRET]` / `[DESZTRUKTÍV]`, AG3): ez váltja ki a repó- és dokumentum-felderítést, ami a 6. kategória fő költsége volt;
  - `analyzer` → a **`## Lefedettségi mátrix (generált)`** (AG4): a `DoD-NN → [P-…] → task` lánc készen, hogy ne vezesse le újra.
- A két subagent kimenetét te fésülöd össze (lásd „A két analyzer-subagent"), és ez alapján döntesz PASS / FAIL-ról.
- A javító fixer-subagenteket szintén Task tool subagent-ként indítod, a saját wrapper-promptjukkal (`agents/spec-fixer.md`, `agents/plan-fixer.md`, `agents/tasks-fixer.md`) — lásd „Az önjavító hurok".
- **A `*-input-from-prev.md` fájlok (IP1) is bemenetek:** a subagent beolvassa a ciklus mappájában lévő `spec-`/`plan-`/`tasks-input-from-prev.md` fájlokat (amelyik létezik), és **nyitott `[ ]` tételt lefedettségi hiányként** jelez. Indoklás: egy nyitott tétel azt jelenti, hogy egy korábbi fázis átadott egy információt, amit a fogyasztó fázis se be nem épített, se el nem vetett — ez ugyanolyan rés, mint egy task nélküli követelmény.

  > **A `validate-input-from-prev.md`-t az 05 NEM vizsgálja:** annak a fogyasztója a 07, ami az analyze után fut — ott jogosan nyitott még.
  >
  > **A hurok fix-módjai (a fixer-subagentek) ezeket a fájlokat továbbra sem olvassák és nem írják** (IP1/6). Ez a check tehát **diagnózis**: a `Must Fix` a `spec.md`/`plan.md`/`tasks.md` hiányosságát nevezi meg (mi maradt ki), nem az átadó fájl kipipálását kéri. A pipálás a normál (nem fix-módú) fázis-futás dolga.

---

## Súlyossági besorolás

Minden megállapítás **Must Fix** vagy **Suggestion**:

- **Must Fix** = blokkolja az implementációt (a hibás alapra épülő implementáció kockázatos): valódi duplikáció, lefedettségi rés, konvenció-ütközés, meghatározatlan komponens, nem eldönthető elfogadási feltétel.
- **Suggestion** = nem blokkol, csak javasolt finomítás (átfogalmazás, kisebb tisztázás).

**PASS feltétele:** nincs `Must Fix` megállapítás. Ha csak `Suggestion`-ök vannak, az eredmény PASS (a suggestion-öket a felhasználó eldöntheti, de nem indítanak hurkot).

---

## 0. lépés — mechanikus kapu (`analyze-gate-check.py`) — MINDEN analyze-futás előtt

A gépiesen eldönthető ellenőrzéseket **nem az `analyzer` subagent végzi**, hanem egy szkript — determinisztikusan, olcsón, hamis riasztás nélkül:

<!-- INCLUDE:shared/python-cmd.md -->

```bash
python3 <platform-scripts-mappa>/analyze-gate-check.py specs/cycle-NN-<cycle-name>
```

_(A projekt gyökeréből futtatva a `--repo-root .` és a `--conventions conventions.md` alapérték jó. Ha a `conventions.md` máshol van, add meg: `--conventions <útvonal>` — enélkül a `G1` kapu-konfiguráció check kimarad.)_

**Mit fed le:** plan-ID formátum/egyediség (P1), task→plan hivatkozás megléte (P2), nem létező ID-ra hivatkozás (P3), ID task nélkül (P4), sorszámos hivatkozás (P5), marker minden taskon (T1), `[OPS]` repo-fájlon (T2), státusz-frissítő task (T3), `⟂` szimmetria (T4), `DoD-NN` hiány/duplikáció (D1), `DoD-NNb` alakú utólagos azonosító (D2), kötelező táblák megléte (S1/S2) — **és a 6. kategória gépies rétege (AG3):** futtatott artefaktum létezése / létrehozó task (A1 = 6.a), plan-`path:sor` horgony feloldása (A2 = 6.g fájl-szintje), horgony-sorszám érvényessége (A2b, javaslat), artefaktum-hang kemény padlója (A3 = 6.h `🔴`/„Tilos", javaslat) — **továbbá:** a spec kidolgozott artefaktumainak átvétele (`V1`) és a teszt-szekciók terjedelme (`V2`, KX3), az útvonal-formátum (`R1`, RP1) és a horgony-formátum (`A2c`, javaslat), valamint a **kapu-konfiguráció együtt mozgása** (`G1`, GC1: a ciklus a riport-struktúrát érinti, de a `conventions.md` `## Teszt-riportolás` táblája nem mozdul → a 07 TR3 kapuja a régi helyen keresne).

**A kimenet három blokkja:**
- **`## Must Fix`** — soronként `[kód] (célfázis: NN) üzenet`. Mindegyik `Must Fix`, a szkript célfázisával — vedd fel őket az `analyze-report.md` listájába **szó szerint**. Ezeket ne kérdőjelezd meg és ne értékeld újra: gépi ellenőrzés eredményei.
- **`## Javaslatok`** — nem blokkolnak, nem indítanak hurkot; a riport `Suggestions` szekciójába kerülnek.
- **`## Leltár`** — **nem megállapítás, hanem az `analyzer` BEMENETE.** A horgonyzott sorok szövegét, a futtatott artefaktumok állapotát és az ítéletet igénylő hang-találatokat tartalmazza. **Add át szó szerint az `analyzer` subagentnek** — ettől nem kell a repóban `Grep`/`Glob` köröket futtatnia (ez a 6. kategória fő költsége volt).

**Kilépő kód:**
- **`0`** → nincs blokkoló mechanikus megállapítás (javaslat és leltár lehet a kimenetben); indítsd az `analyzer` subagentet a szemantikai kategóriákra, a leltárral együtt.
- **`1`** → van `Must Fix`; ugyanígy indítsd az analyzert, és a két megállapítás-listát együtt kezeld a hurokban.
- **`2`** → használati hiba (hiányzó ciklusmappa vagy dokumentum) → STOP, jelezd a felhasználónak.

**A kapu minden iterációban fut** (a javítás után is) — így a mechanikus regresszió nem tud átcsúszni.

> **Az `analyzer` ezekre már nem kap külön feladatot.** Ha mégis ilyen megállapítást ad vissza, az duplikátum: a szkript kimenete az irányadó.

---

## FAIL — kategória → célfázis leképezés

Egy olcsóbb LLM-nek konkrét célt kell adni, nem „vissza a megfelelő fázisba". A `Must Fix` megállapítás kategóriája határozza meg a javító célfázist (= melyik fixer-subagentet indítod):

| Kategória | Célfázis (fixer) | Indok |
|---|---|---|
| Duplikáció | 03 (tervezési szintű), 04 (task-szintű) | a redundancia forrásához |
| Ambiguitás | 03 (technikai döntés), 02 (viselkedési — ritka) | ahol a fogalmat tisztázni kell |
| Alulspecifikáció | 03 (meghatározatlan komponens), 02 (hiányzó elfogadási feltétel) | a hiányzó döntés szintjére |
| Konvenció-ütközés | 03 (enyhe), 00 (súlyos — `conventions.md` felülvizsgálat) | összhangban az SK4 logikájával |
| Konvenció-ütközés, ahol a ciklus **szándékosan** változtat konvenciót (GC1) | **03** — a plan tervezze meg a `conventions.md` frissítését (+ **04** a taskra) | a döntés már megvan; ez végrehajtás, nem konvenció-felülvizsgálat, tehát nem megy vissza a `00`-ra |
| Lefedettségi hiány | 04 (követelmény ↔ task újrarendelés) | a task lista a hiányos |
| Lefedettségi hiány — nyitott `*-input-from-prev.md` tétel (IP1) | a **fogyasztó** fázis (02 / 03 / 04 a fájl szerint) | ott maradt ki az átadott infó beépítése |
| Plan-hivatkozás hibája (PID1): hiányzó / nem létező `[P-…]` / sorszámos hivatkozás / `[P-…]`-hoz nincs task | **04** | a `tasks.md` hivatkozásai romlottak el |
| Végrehajtható plan-szekciónak nincs `[P-…]` azonosítója (PID1) | **03** | az ID kiadása a plan dolga |
| Scope-túlnyúlás (SC1): plan-képességnek nincs spec-forrása | **02** (ha kell a képesség → DoD-pont), **03** (ha nem kell → kivétel + `Out of scope`) | elfogadási feltétel nélkül nem fejleszthető |
| Konfiguráció-életút (KF1) hiányos vagy hiányzik | **03** | a paraméter propagációja terv-kérdés |
| Spec-teszteset nem képződött le plan-tesztesetre (TP1) / hiányzó környezet-felkészítés (TP3) | **03** | a `test-runner` csak a plant olvassa |
| Kötelező tábla hiánya (`Spec-lefedettség`, `Fordított lefedettség` → 03; `Plan-lefedettség` → 04) | a tábla gazdája | a kimaradt tábla = kihagyott kapu |
| Hiányzó/duplikált `DoD-NN` azonosító | **02** | a 07 per-item számlálója erre épül |
| Kidolgozott spec-artefaktum csonkítva / összevonva a plan-ben (KX3 — `V1`/`V2` vagy szemantikai) | **03** | a `test-runner` a spec-et nem olvassa: ami itt kimarad, nem fut le |
| Útvonal-formátum (RP1 — `R1`) | a dokumentum gazdája: **02 / 03 / 04** | abszolút/gép-specifikus útvonal más gépen és CI-ben értelmetlen |
| Kapu-konfiguráció nem mozog a struktúrával (GC1 — `G1`) | **03** (+ **04** a taskra) | a `conventions.md`-t olvasó kapu (TR3, Sonar) a régi értékkel futna → a 07 bukik |

**Legkorábbi érintett fázis nyer:** ha több kategória is FAIL és különböző célfázisokra mutat, a hurok a **legkorábbi érintett fázisra** ugrik (02 < 03 < 04), majd onnan deriválja le újra a downstream fázisokat — különben a későbbi fázisok hibás alapra épülnének. (Súlyos konvenció-ütközés `00`-ra mutat: ez emberi döntést igényel a `conventions.md` szintjén — ilyenkor a hurok megáll és kérdez, nem javít automatikusan.)

---

## Az önjavító hurok (orchestrátor-hurok)

FAIL esetén **nem** adod vissza egyszerűen a vezérlést a felhasználónak. Helyette levezényelsz egy iteratív javító hurkot, amíg PASS nem lesz, vagy amíg el nem éred a `max X` korlátot.

### A hurok egy iterációja

1. **Célfázis meghatározása.** A `Must Fix` lista kategóriáiból (a fenti leképezés szerint) határozd meg a **legkorábbi érintett célfázist** (02/03/04). Ez a fixer belépési pontja.
2. **Státusz-marker felvétele.** A célfázistól lefelé minden érintett dokumentum státuszát fordítsd a fázis-megfelelő nem-kész állapotra `[analyze-loop]` markerrel (pl. `Piszkozat [analyze-loop]`). A marker jelzi: fix-mód aktív → a fixerek automatikusan léptetik a státuszt (lásd D7), és megszakítás után jelzi, hogy a doksit a hurok nyitotta vissza.
3. **Fixer-subagent indítása** a célfázishoz tartozó wrapperrel (lásd „Fixer-subagent indítása").
4. **Kérdés-megállás kezelése.** Ha a fixer az összefoglalójában nyitott kérdéseket jelentett (új `Knn` bejegyzések a `*-questions.md`-ben): tedd fel őket a felhasználónak **egyesével**, fázis-fejléccel (lásd „Fázis-fejléces kérdésformátum"), vezesd át a választ a `*-questions.md`-be (`[x]` + döntés), majd **indítsd újra ugyanazt a fixert** a most már megválaszolt kérdéssel. Ez nem számít új analyze-iterációnak.
4.a **„Változott-e egyáltalán?" őrszem — N.** A fixer visszatérése után futtasd: `git diff --stat -- specs/cycle-NN-<cycle-name>/`.
   - **Ha a diff üres**, és a fixer **nem** vett fel új `Knn` kérdést sem, akkor a dokumentumok változatlanok — a következő analyzer-kör **bizonyosan ugyanazt a `Must Fix` listát** adná. Ilyenkor **ne indíts analyzer-futást**: állj meg, és kérdezd meg a felhasználót, hogyan folytassa (kézi javítás / a `Must Fix` tétel elvetése / a `conventions.md` felülvizsgálata) — a fázis-fejléces kérdésformátummal. Jegyezd fel a Hurok-naplóba: `a fixer nem hajtott végre változtatást`.
   - **Ha a diff nem üres** (vagy van új kérdés) → tovább a 4.b pontra.


4.b **Mechanikus visszacsatolás a fixer után — G.** Amint a fixer visszatért (és a kérdései meg vannak válaszolva), **futtasd le a mechanikus kaput** (0. lépés) — még az analyzer előtt.
   - **Csak mechanikus `Must Fix` van** (P/T/S/A/C/D kódok, tehát kizárólag a kapu kimenete) → **küldd vissza ugyanannak a fixernek** a kapu tételeit, szó szerint. Ez **nem új iteráció**, és **nem indít analyzer-futást**: a hurokszámláló nem nő.
   - **Nincs mechanikus `Must Fix`** → tovább az 5. pontra.
   - **Korlát:** ugyanezt a visszacsatolást **legfeljebb kétszer** futtasd egy iterációban. Ha a fixer harmadszorra is mechanikusan hibás dokumentumot ad vissza, kezeld normál iterációként (az 5. ponttól tovább), és a Hurok-naplóban jegyezd fel: `fixer mechanikus regressziója nem konvergált`.


5. **Downstream re-deriválás — FELTÉTELESEN (D11).** A felfelé javítás után a célfázis alatti fázisokat kell összehangolni (`02 → 03 → 04`) — **de csak akkor, ha a javításnak van downstream hatása.**
   - A fixer visszatérési összefoglalója kötelezően tartalmaz egy **`downstream-hatás:`** mezőt (lásd „Fixer-subagent indítása"): `nincs`, vagy `van — <mi változott, ami a következő fázist érinti>`.
   - **`nincs`** (tipikusan: megfogalmazás-pontosítás, duplikátum-összevonás, artefaktum-hang javítása, elgépelés) → **a downstream fixereket NE indítsd el.** Egy felesleges plan- vagy tasks-fixer futás teljes dokumentum-beolvasással jár, és új hibát is bevihet.
   - **`van`** → indítsd a downstream fixert, és **add át neki a `downstream-hatás` szövegét** — ez a reconciliation hatóköre. Ez **célzott reconciliation, nem teljes újraírás**: a lezárt `*-questions.md` döntéseket megőrzi.
   - Ha a fixer nem adta meg a mezőt, **kérdezd vissza tőle** egy mondatban — ne tippelj, és ne futtasd el „biztos, ami biztos" alapon a teljes láncot.
   - **Minden downstream fixer után is fut a 4.b mechanikus visszacsatolás** — a `tasks.md` hivatkozási rendjét jellemzően épp a reconciliation rontja el.
6. **Újra-analyze — EGY teljes kör, KÉT PÁRHUZAMOS subagenttel (D10/E).** Előbb futtasd a **mechanikus kaput** (0. lépés), majd indítsd az `analyzer` és az `analyzer-exec` subagentet **egyetlen üzenetben, párhuzamosan** (lásd „A két analyzer-subagent"). Mindkettő **egyszer** fut, teljes módban, és két extra bemenetet kap:
   - **az előző kör `Must Fix` listája** — az analyzer jelentésének **első blokkja** tételenként igazolja, hogy megoldódott-e;
   - **a tervezési dokumentumok változása**: `git diff -- specs/cycle-NN-<cycle-name>/` (a hurok alatt nincs commit, tehát a diff a hurok teljes változását mutatja) — ez **navigáció**: a megváltozott szakaszokat nézze meg először, mert ott a legvalószínűbb az új rés. A vizsgálat hatóköre viszont a **teljes dokumentum** marad.

   Az eredmény alapján:
   - **Nincs `Must Fix`** → a hurok konvergált, ugrás a „Státusz kezelés → PASS"-ra (itt kerül le a marker és történik az egyetlen commit).
   - **Van `Must Fix`** → új iteráció az 1. ponttól, a hurokszámláló +1.

   > **A `PASS` kizárólag teljes analyzer-futásból adható** — a `git diff` a fókuszt adja, nem a hatókört.

### A két analyzer-subagent (E) — párhuzamos indítás és összefésülés

A diagnózist **két subagent** végzi, egymástól független hatókörrel. **Egyetlen üzenetben indítsd őket, hogy párhuzamosan futhassanak** — a fázis eltelt ideje így a kettő közül a lassabbé, nem az összegük.

| Subagent | Hatókör | Bemenete |
|---|---|---|
| `agents/analyzer.md` | **1–5. kategória** (duplikáció, ambiguitás, alulspecifikáció, konvenció-ütközés, lefedettség **tartalmi** ítélete) | `spec.md` + `plan.md` + `tasks.md` + `conventions.md` + átadó fájlok + `cycle-design-input.md` + a kapu **generált mátrixa** |
| `agents/analyzer-exec.md` | **6. kategória** (prózában ígért teszt, artefaktum-tulajdon, destruktív művelet, horgony-szimbólum, artefaktum-hang) | `plan.md` + `tasks.md` + a kapu **`## Leltár`** blokkja |

_Mindkét subagent bemenete kiegészül a **rebase-fájllistával**, ha a BR1 behozta a fő branch-et (lásd lent)._

**Rebase-fájllista (BR1/a) — csak ha a BR1 behozott valamit.** Ilyenkor a **forrásfa** változott, nem a tervezési dokumentumok: az analyzer a saját `git diff`-navigációjából (D10) erről semmit nem lát. Ezért add át **mindkét** subagentnek a fájllistát, ezzel a felszólítással:

> *„Az alábbi fájlok a fő branch behozásával (rebase/merge) érkeztek a ciklus ágába, egy másik ciklus vagy hotfix eredményeként: `<fájllista>`. Nézd meg célzottan, hogy a `plan.md` és a `tasks.md` rájuk mutató hivatkozásai, horgonyai, szignatúra- és interfész-feltevései **állnak-e még** (átnevezett vagy áthelyezett szimbólum, megváltozott paraméterlista, eltűnt export, módosult konfigkulcs). A vizsgálat hatóköre ettől NEM szűkül — ez fókusz, nem hatókör."*

A fájllista **fókusz, nem szűkítés** (ugyanaz az elv, mint a dokumentum-diffnél, D10): a `PASS` továbbra is kizárólag teljes analyzer-futásból adható. A behozott változásokból eredő elcsúszás a szokásos úton megy tovább — `Must Fix` → legkorábbi célfázis → fixer —, **külön „rebase-javító kör" nincs**: az önjavító hurok maga a javító kör.

**Az összefésülés a te dolgod:**
1. A két `Must Fix` listát és a kapu `Must Fix` listáját **egy listába** fűzöd, majd a **legkorábbi érintett célfázist** ebből az egyesített listából határozod meg.
2. **Duplikátum-szűrés:** ha ugyanarra a `fájl:hely`-re mindkét subagent adott megállapítást, a **specifikusabbat** tartsd meg (jellemzően az `analyzer-exec` végrehajthatósági tételét), és a másikat ne vidd tovább a fixernek.
3. A riport `Végrehajthatósági leltár` szekciója az `analyzer-exec` kimenetéből jön, a `Lefedettségi mátrix` a **kapuból** (lásd lent), az `Érintett DoD-sorok` mindkettőből.
4. **Ha az egyik subagent hibára fut vagy nem ad értelmezhető listát**, ne minősítsd PASS-nak a kört: indítsd újra azt az egyet (ez nem új iteráció).

### Fixer-subagent indítása

- A fixer-subagent **rendszerpromptja** a célfázis fixer-wrappere: `agents/spec-fixer.md` (02), `agents/plan-fixer.md` (03), `agents/tasks-fixer.md` (04). A wrapper **tartalmazza** a fázis Fix-mód szekcióját és a fázis minőségi kapuját (közös forrásból, build-time beemelve) — nincs duplikált javító logika, és a fázis saját kapui automatikusan érvényesülnek.
- **A fixer nem olvas fázis-skillt (D13).** A wrapperben minden szabály benne van; ha egy fixer mégis a skill beolvasását jelenti be, az hiba (a teljes fázis újrafuttatására csábít egy célzott javítás helyett).
- **Bemenet** a subagentnek: a célfázisra szűrt `Must Fix` lista (kategória + leírás + `fájl:hely`) + a célfázis dokumentumai.
- **Kimenet** a subagenttől: (a) az elvégzett (mechanikus) javítások összefoglalója, (b) a **`downstream-hatás:`** mező (`nincs` / `van — <mi érinti a következő fázist>`, D11), és (c) a `*-questions.md`-be felvett **új** kérdések azonosítói — azoké a pontoké, amelyekhez valódi döntés kell. A subagent **nem kérdez közvetlenül a felhasználótól** (nincs interaktív csatornája); csak gyűjt és visszaad. A kérdezés a te dolgod (D2).

### `max X` hurokszámláló + leállás

- **Alapérték: `max X = 3`.**
- **`X` egysége: a teljes analyze-újrafutások száma.** Egy `FAIL → fix → re-deriv → re-analyze` ciklus = **1** iteráció, és **egy** analyzer-futás. A követő-kérdések miatti fixer-újraindítások és az egyes downstream fixer-hívások **nem** növelik `X`-et.
- **Két, egymástól független kilépési feltétel:**
  1. **Nyitott kérdés** → a hurok megáll, kérdez; a user válaszol; a hurok **folytatódik** (ez nem hiba, és nem fogyaszt iterációt).
  2. **`max X` elérve konvergencia nélkül** → a hurok feladja (lásd „Státusz kezelés → FAIL").

### `[analyze-loop]` státusz-marker (D7)

- **Formátum:** `[analyze-loop]` suffix a státusz-érték végén, pl. `Piszkozat [analyze-loop]`, `Nyitott kérdések vannak [analyze-loop]`.
- **Jelentése:** a dokumentumot az analyze-hurok nyitotta vissza, fix-mód aktív. Amíg a marker jelen van, a fixerek a státuszt **automatikusan** léptetik (megerősítés nélkül) — eltérően a 02/03/04 normál „megerősítés a státuszváltás előtt" szabályától. A felhasználó csak a **kérdéseknél** és a **végső PASS-nál** lép be.
- **Levétele:** PASS-kor (→ normál flow, a fixer a fázis valódi záró-státuszát adja) vagy `max X` feladáskor a vég-állapot szerint (lásd FAIL). A marker megléte egyúttal a megszakítás-utáni folytatás horgonya is.

### Commit-stratégia a hurokban (D9)

- **`analyze-loop`-ban nincs iterációnkénti commit** — zaj-mentes marad a történet.
- **Egyetlen commit a hurok lezárásakor** (PASS vagy `max X` feladás): `cycle-NN: 05-analyze`. Ez a commit **kötelező, mindkét ágon** — az eljárást (stage → commit → determinisztikus ellenőrzés → visszajelzés) lásd a *Fázis-záró commit* szekcióban (PC1).
- **Megszakítás-biztos:** a köztes commit hiányát a `[analyze-loop]` státusz-marker + a `*-questions.md` + a Hurok-napló pótolja — ezekből a folytatás rekonstruálható (lásd „Folytatás megszakított futás után").

---

## Fázis-fejléces kérdésformátum

Amikor a hurok közben kérdést teszel fel a felhasználónak, mindig jelezd, **hol jár** a hurok. A kérdés sablonja:

```
[<FÁZIS> · iter <n>/<max X> · <FÁZIS>/<Knn>]
<kérdés szövege>
```

- **Fázis:** `SPEC` / `PLAN` / `TASKS` (a célfázis, ahonnan a kérdés származik).
- **`iter n/max X`:** hányadik analyze-iterációnál tart a hurok.
- **`FÁZIS/Knn`:** a kérdés azonosítója fázis-prefixszel a párbeszédben (`SPEC/K07`, `PLAN/K03`, `TASKS/K02`). A **fájlokban** a kérdés sima `Knn` marad — a fájl helye (`spec-questions.md` / `plan-questions.md` / `tasks-questions.md`) kódolja a fázist.

Szabályok: **egyszerre egy kérdés**, várd meg a választ, és a válaszod végén helyezz el egy közvetlen, kattintható linket az érintett `*-questions.md`-re.

Példa:

> **[PLAN · iter 2/3 · PLAN/K05]**
> A `callLegacyVerify` timeout esetén retry-zzon, vagy azonnal 504-et adjon vissza? A spec nem rendelkezik róla.
> [plan-questions.md](file:///.../specs/cycle-NN-name/plan-questions.md)

---

## analyze-report.md struktúra

Hozd létre / frissítsd a `specs/cycle-NN-<cycle-name>/analyze-report.md` fájlt (relatív útvonal-formátum a dokumentum tartalmában, `file://` tilos):

```md
<!-- INCLUDE:lang/05-analyze.md#analyze-report-struktura -->
```

---

## Minőségellenőrzés — a jelentés lezárása előtt

Menj végig, mind a **6** kategória ténylegesen lefutott-e (az 1–5. az `analyzer`, a 6. az `analyzer-exec` kimenetében — **mindkettő megjött-e egyáltalán**). **A 6. kategóriánál külön ellenőrizd, hogy a subagent visszaadta-e a „Végrehajthatósági leltárt"** — enélkül a PASS nem fogadható el, mert épp azok a hibák maradnának rejtve, amelyeket a lefedettségi mátrix szerkezetileg nem lát:

1. **Duplikáció** — átnézve spec/plan/tasks redundanciára?
2. **Ambiguitás** — minden elfogadási feltétel mérhető/eldönthető?
3. **Alulspecifikáció** — minden komponens és feltétel meghatározott?
4. **Konvenció-ütközés** — minden tervezési döntés egyezik a `conventions.md`-vel?
5. **Lefedettség** — a kapu generált mátrixa bekerült a riportba, és az `analyzer` tartalmi ítélete (`Érintett DoD-sorok` + `DoD-NN`-en túli követelmények) át van vezetve rajta?
6. **Végrehajthatóság és artefaktum-tulajdon** — az `analyzer-exec` visszaadta a *Végrehajthatósági leltárt* (lásd fent), a **mechanikus kapu** (`analyze-gate-check.py`) lefutott ebben a körben, és a kapu blokkjait át is adtad a két subagentnek (AG3/AG4)?

Ha bármelyik kategória nem futott le, ne zárd le a jelentést. Ha a hurok futott, ellenőrizd azt is, hogy a **Hurok-napló** minden iterációt tartalmaz.

**A `Validált alap` mező kitöltve? (BR1)** — a riport fejlécében szerepel a fő branch neve és SHA-ja (`git rev-parse origin/main`), a ciklus ágának csúcsa (`git rev-parse HEAD`), és hogy a BR1 hozott-e be valamit. Ezt a `06` és a `09` **összeveti a saját futásakori állapottal**: ha időközben előrement a fő branch, az `analyze-report.md` `PASS`-a elavult alapon készült. Placeholder vagy hiányzó mező esetén a jelentés nem zárható le. (No-VCS projektben a mező értéke `—`.)

---

## Státusz kezelés

### PASS (a hurok konvergált, vagy első nekifutásra tiszta)

Nincs `Must Fix` megállapítás.

Teendők **sorban**:
1. Írd a `analyze-report.md` státuszát `PASS`-re, töltsd ki a `Hurok:` mezőt és a Hurok-naplót (ha volt iteráció).
2. **Vedd le a `[analyze-loop]` markert** minden érintett dokumentumról — a fixerek a fázis valódi záró-státuszát adták (`Tervezésre kész` / `Task írásra kész` / `Implementálásra kész`); ellenőrizd, hogy ez áll-e mindegyiken.
3. **Egyetlen lezáró commit** (a hurok alatt nem volt köztes commit) — a *Fázis-záró commit* szekció eljárása szerint, **kötelező**:
   ```bash
   git add specs/cycle-NN-<cycle-name>/
   git commit -m "cycle-NN: 05-analyze"
   ```
4. Jelezd a felhasználónak a következő lépést és a fázis indító parancsát:
<!-- INCLUDE:lang/05-analyze.md#zaro-uzenet -->
   > **A válasz végén helyezd el az `analyze-report.md` közvetlen, kattintható linkjét.**

### FAIL (`max X` elérve PASS nélkül)

A hurok `max X = 3` iteráció után sem konvergált.

Teendők **sorban**:
1. Írd a `analyze-report.md` státuszát `FAIL`-re, a `Hurok:` mezőbe `<max X>/<max X> (feladva)`, és a Hurok-naplóba a megrekedt állapotot (mely `Must Fix` maradt, melyik fázisnál).
2. **Hagyd rajta a `[analyze-loop]` markert** az érintett dokumentumokon — így a felhasználó (vagy egy következő session) látja, hogy a hurok nyitotta vissza őket, és hol akadt el.
3. **Egyetlen lezáró commit** — a *Fázis-záró commit* szekció eljárása szerint, **kötelező** (a FAIL ág sem kivétel):
   ```bash
   git add specs/cycle-NN-<cycle-name>/
   git commit -m "cycle-NN: 05-analyze"
   ```
4. Összefoglalás + kérdés a felhasználónak: foglald össze, melyik `Must Fix` nem oldódott meg és miért (pl. ismétlődő ambiguitás, amit a fixer nem tud eldönteni), és kérdezd meg, hogyan folytassák (kézi javítás az adott fázisban / döntés egy nyitott kérdésre / a `conventions.md` felülvizsgálata súlyos konvenció-ütközésnél).
   > **A válasz végén helyezd el az `analyze-report.md` közvetlen, kattintható linkjét.**

<!-- INCLUDE:shared/phase-commit.md -->

A fenti blokkban a `<FÁZIS-TAG>` értéke ebben a fázisban: **`05-analyze`**. A commit a **hurok lezárásakor, egyszer** történik — de **minden lezáró ágon** (PASS és `max X` FAIL egyaránt). A hurok alatt nincs köztes commit; a köztes állapotot a `[analyze-loop]` marker, a `*-questions.md` fájlok és a Hurok-napló őrzi.

> **Megállási szabály (PC1):** ha az `analyze-report.md` státusza `PASS` vagy `FAIL`, de a fázis-záró commit hiányzik (VCS-es projekt, `git log -1 --oneline` nem a `cycle-NN: 05-analyze` commitot mutatja), **STOP** — először commitolj, csak utána zárd le a fázist és add meg a következő lépést.

---

## Kérdezési szabályok

- Csak **egy** kérdést tegyél fel egyszerre, várd meg a választ.
- A hurok közbeni kérdéseknél használd a **fázis-fejléces kérdésformátumot** (`[FÁZIS · iter n/max X · FÁZIS/Knn]`).
- Minden alkalommal, amikor kérdést teszel fel vagy jóváhagyást kérsz, a válaszod végén kötelezően helyezz el egy közvetlen, kattintható markdown linket az érintett fájlra.