# Prompt fejlesztési lista — 2. munkafájl: nagy-flow bővítések

Ez a **munkafájl** a teljes berki spec flow két új bővítését követi nyomon, pipálható (checkbox) formában:

- **A. rész — Auto-run orchestrátor** (opt-in pipeline a `05→09` fölött).
- **B. rész — Retrospec skill** (terminális, önjavító tanulság-gépezet a ciklus végén).

---

## A. rész — Auto-run orchestrátor

Ez a szakasz a teljes berki spec flow fölé épülő, opt-in **auto-run orchestrátor** bevezetését követi.

**Mit ad hozzá?** Egy fázishatár-orchestrátort, amely a „zöld úton" magától lép `05 → 06 → 07 → 08 → 09`, és **megáll a valódi humán kapuknál**. Egy mondatban: *auto-advance on green, stop on gate.*

**Amit NEM ad hozzá:** loop engineeringet — az már megvan (05/07/09 önjavító hurkok, LC1–LC4). Ez **orchestráció / pipeline**, nem új hurok.

**Alapelvek (a teljes munka során tartandók):**
- Az orchestrátor a **top-level fő ágens**, NEM subagent (kell az interaktív csatorna a felhasználóhoz; a mélyen ágyazott Task-hívás törékeny).
- A fázisokon belüli subagentek (fixerek, `reviewer`, `analyzer`, `doc-sync-planner`) **változatlanul** futnak.
- A kézi, fázisonkénti paste-elés **megmarad** külön belépőként — ez egy *másik* belépő, nem váltja le.

---

## 0. Rögzített döntések

- [x] **AD1 — Scope / belépő:** Meddig „fagy be" a terv emberi kézzel, ahonnan az orchestrátor magától mehet?
  - **A:** `06→09` — a teljes tervezés (02→05) kézi.
  - **B (választott):** `05→09` — a tervdokumentumok kézzel készülnek (02→04), de az **analyze-hurkot (05) is az orchestrátor futtatja**. Indok: 05 már autonóm hurok, csak fixer-kérdésnél áll meg, így logikus belevenni.
  - **C:** `04→09` — több autonómia, de nagyobb green-but-wrong felület.
  - **Belépési előfeltétel:** `tasks.md` létezik „Implementálásra kész" státuszban (04 kész). Ha nem → az orchestrátor nem indul, visszairányít a kézi tervfázisra.

- [x] **AD2 — Állapot / resume forrás:** Honnan tudja az orchestrátor, melyik fázisban van, és hogyan resumel megszakítás után?
  - **A (választott):** **Dokumentum-státuszokból** — a meglévő `spec.md`/`plan.md`/`tasks.md` státusz-mezők + hurok-markerek a forrás. Nincs új state-fájl, egyetlen igazságforrás; a markerek + hurok-naplók (LC1/LC2) már adják a resume-ot.
  - **B:** Külön orchestráció-napló (új állapot, szinkronban tartandó).
  - **C:** Mindkettő.

---

## 1. Új skill — `prompts/skills/10-auto-run.md`

A meta-skill maga. Top-level fő ágens futtatja; a fázisokat **egy session-ön belül, inline, szekvenciálisan** hajtja végre (maga követi 05 utasításait, majd 06-ét, stb.).

- [ ] **A1.1 — Fájl + frontmatter.** `prompts/skills/10-auto-run.md` létrehozása. A lightweight flow-hoz hasonló `name`/`description` alapú frontmatter (külön belépő/„külön út", nem klasszikus `prev`/`next` fázis). A `description` jelezze: opt-in auto-run a `05→09` szakaszra, megáll a humán kapuknál.

- [ ] **A1.2 — Belépési előfeltétel-ellenőrzés.** A skill elején: `tasks.md` létezik-e „Implementálásra kész" státuszban? Ha nem → ne induljon, jelezze a hiányzó tervfázist, és irányítson a kézi `02→04` / `01-add-cycles` felé.

- [ ] **A1.3 — Állapotgép (státuszból derivált fázis-pointer).** Minden lépés előtt olvassa ki a státuszokat + markereket, és ebből határozza meg az aktuális fázist (ez adja a resume-ot is):

  | Megfigyelt állapot | Aktuális fázis |
  |---|---|
  | `[analyze-loop]`/`[validate-loop]`/`[review-loop]` marker jelen | **folytatja az adott hurkot** (marker felülír) |
  | `tasks.md` = „Implementálásra kész", `analyze-report` hiányzik/FAIL | **05** |
  | `analyze-report` = PASS, `tasks.md` = „Implementálásra kész" | **06** |
  | `tasks.md` = „Validálásra kész" | **07** |
  | spec/plan/tasks = „Kész", `docs-generated/` nem konzisztens | **08** |
  | doc-sync kapu zöld, review nem tiszta | **09** |
  | review tiszta + zöld validálás | **halt a merge előtt (RD8)** |

- [ ] **A1.4 — Fázis-végrehajtás + kilépési jel kiolvasása.** Minden fázis után olvassa ki a jól definiált kimenetet (PASS/FAIL/STOP/ESCALATE), és döntsön: zöld → tovább; egyébként → halt + felhasználó.

- [ ] **A1.5 — Halt-térkép (ezeket NE automatizálja át).** Az orchestrátor mindegyiknél **megáll** és a fázis saját kérdés-csatornáján kérdez:

  | Kapu | Honnan | Mit tesz az orchestrátor |
  |---|---|---|
  | 05: `max X=3` PASS nélkül | analyze-loop | megáll, humán döntés |
  | 07: 3-próba STOP (VD4) | validate-loop | megáll, „hogyan tovább?" |
  | 07/09: eszkaláció 03/02-re (VD5/RD6b) | terv-hiba | **megáll** — visszanyitott tervfázis = interjú-nehéz, nem auto |
  | 08: nyitott `[ ]` doc-sync kérdés (DS10) | doc-sync | megáll, kérdez (`doc-sync-questions.md`) |
  | 09: 3-próba / max 5 (RD6c) | review-loop | megáll, humán |
  | **Merge (RD8)** | 09 vége | **mindig kézi megerősítés** — az orchestrátor a merge ELŐTT áll meg |

- [ ] **A1.6 — Eszkaláció = halt (kiemelt).** Amikor 07/09 visszadob 03/02-re, az újra interjú-nehéz terep: az orchestrátor itt **ne fusson át** a visszanyitott tervfázison — adja vissza a felhasználónak.

- [ ] **A1.7 — Végrehajtási modell explicit kimondása.** A skillben legyen leírva: a fázisokat a fő ágens inline, szekvenciálisan futtatja (nem subagentként); a fázisokon belüli subagentek változatlanul futnak; nincs új ágazási szint.

- [ ] **A1.8 — Halt UX + resume.** Halt esetén: tömör „auto-run paused at `<gate>`" üzenet + a szükséges döntés + link a fázis kérdés-dokumentumára + resume-utasítás (a skill újrahívása ugyanarra a ciklusra → státuszból újraderivál és folytat).

- [ ] **A1.9 — Kontextus-budget kezelése (üzemeltetési kockázat).** Jelezze a skill, hogy `05→09` egy menetben hosszú: a nehéz munka subagentekben fut, az orchestrátor főleg kis státusz-/report-fájlokat olvas; minden halt természetes checkpoint, ahonnan státuszból tisztán resumel.

- [ ] **A1.10 — Indító prompt.** `Kövesd a prompts/skills/10-auto-run.md utasításait. Input: specs/cycle-NN-<cycle-name>`

---

## 2. README frissítések — `prompts/README.md`

- [ ] **A2.1 — „Két fejlesztési út" → harmadik belépő.** Egészítsük ki egy opt-in auto-run belépővel a teljes flow fölött (vagy nevezzük át a szekciót/úgy fogalmazzunk, hogy a `10-auto-run` a teljes flow egy futtatási módja, nem negyedik módszertan).
- [ ] **A2.2 — Mappastruktúra.** `skills/` listába: `10-auto-run.md` sor + rövid leírás.
- [ ] **A2.3 — Folyamatábra.** Jelöljük, hogy az `05→09` szakasz opcionálisan auto-run orchestrátorral is futtatható, a meglévő halt-pontok megtartásával.
- [ ] **A2.4 — Indító promptok blokk.** Vegyük fel a `10-auto-run` copy-paste promptot.
- [ ] **A2.5 — Skill-index tábla.** Új sor a `skills/10-auto-run.md`-nek (Fázis: meta/orchestráció; Bemenet: ciklus mappa; Kimenet: végigvitt `05→09` a humán kapukig).
- [ ] **A2.6 — Frontmatter séma megjegyzés.** Ha a `10-auto-run` `name`/`description` frontmattert használ (mint a lightweight flow), a „Frontmatter séma" szekció jegyezze meg a kivételt.

---

## 3. Még nyitott / csiszolandó pontok (döntés a megírás előtt)

- [ ] **AO1 — Merge-en kívüli jóváhagyós checkpoint?** Legyen-e a merge-en túl további „dry-run"/megerősítős megállás (pl. a 06 implementáció indítása előtt egy „indulhat?" pont), vagy a definiált halt-térkép elég?
- [ ] **AO2 — Skill neve.** `10-auto-run` (javasolt, számozás-folytatás) vs. `orchestrate` / `pipeline`.
- [ ] **AO3 — Részleges scope futtatás.** Engedjük-e, hogy az orchestrátor a ciklus közepéről induljon (pl. csak `07→09`), ha a státuszok ezt mutatják, vagy mindig a derivált aktuális fázistól a merge-ig megy? (Jelenleg: a státuszból derivált aktuális fázistól indul — ez implicit részleges futás.)

---

## B. rész — Retrospec skill (terminális önjavító tanulság-gépezet)

A ciklus **leges legvégén** (a 09 merge **után**) futó skill, amely a ciklusban előjött tanulságokat **kibányássza, kategorizálja, és ellenőrzött ütemben beépíti a tudásba**. A „gépezet" nem az őrizetlen önátírás, hanem a **tanulság-felhalmozás ciklusokon át**, magas blast-radiusú változásnál humán kapuval.

**Vezérelv:** *javasol, nem alkalmaz vakon.* Az őrizetlen self-edit a kanonikus módszertan-fájlokba a fő kockázat (egyszeri incidens → általános szabály, ellentmondás, bloat, csendes minőségromlás).

### B0. Rögzített döntések

- [x] **BD1 — Kapu-modell:** **Hibrid típus szerint.** A **projekt-tudás** automatikusan felhalmozódik a tudástárba (alacsony blast-radius); a **módszertan/skill-edit**-eket a retrospec CSAK javasolja, és **humán kapu** hagyja jóvá (magas blast-radius).
- [x] **BD2 — Tárolás szerkezete:** **Memória-stílus** — egy tanulság = egy fájl, frontmatterrel (`type`), központi indexszel, **dedup-before-add**-del + időnkénti konszolidációval. Skálázik, kevés bloat.
- [x] **BD3 — Tanulság-forrás:** **Automatikus bányászat a ciklus-artefaktokból** — a `*-questions.md`, a hurok-naplók (analyze/validate/review history), az eszkalációk (VD5/RD6) és a tervtől való eltérések elemzése. Már létező jelből dolgozik.
- [x] **BD4 — Magas-reasoning subagent:** A retrospec **ítélet-nehéz munkáját** (bányászat, kategorizálás, módszertan-javaslat tervezése) egy dedikált **`retrospector` subagent** végzi, amely a **legmagasabb reasoning-szintű elérhető modellt** használja. Eszközfüggetlen elv, per-eszköz leképezéssel: **Claude Code → Opus 4.8 (`claude-opus-4-8`)**, **Antigravity CLI → Gemini 3.1 pro**. Indok: a tanulság-szintézis és különösen a magas blast-radiusú módszertan-edit javaslata erős érvelést kíván.
- [x] **BD5 — Kvóta-tudatos, 2 tieres modell-konvenció (cheap-default):** A Pro előfizetés kvótája kicsi → drága modell csak ritkán használható (lásd memória: kvóta-korlát). Ezért:
  - **2 tier:** `standard` (default, olcsó) — Claude → **Sonnet**, Antigravity → **Gemini 3.5 Flash**; `high` — Claude → **Opus 4.8**, Antigravity → **Gemini 3.1 pro**.
  - **Minden `standard` alapból** (00, 01, 02, 03, 04, 06, 07, 08). A 02/03 tervezés is olcsó marad: túl hosszú + interaktív + gyakori lenne `high`-ban (kvótagyilkos), és ott amúgy is benne van az ember a loopban. Az 05-analyze is `standard` (a hurokban akár 3× ismétlődik → drágulna).
  - **`high` CSAK rövid, körülhatárolt, read-only diagnoszta-subagentnek:** `retrospector` (ciklusonként 1×, BD4) + **opcionálisan** `reviewer` (09, az utolsó merge-előtti kapu; ha a kvóta nagyon szűk, ez is levihető `standard`-ra).
  - **A `high` a subagentre vonatkozik, soha a fázisra/orchestrátorra** — az interaktív/hosszú részek végig olcsók.
  - **Graceful fallback:** a `high` **enhancement, nem hard requirement** — ha a drága modell kvótája elfogyott/nem elérhető, a subagent essen vissza `standard`-ra és fusson le olcsón.

### B1. Kétféle tanulság — útvonal blast-radius szerint (a központi modell)

A tanulságokat **kategória szerint külön útvonalra** kell vinni:

| Típus | Példa | Hova | Kapu |
|---|---|---|---|
| **Projekt-tudás** | „ebben a repóban a DB-hez port-forward kell" | projekt tudástár / `conventions.md` | auto (dedup-pal) |
| **Módszertan-tudás** | „a flow nem ellenőrizte a teszt-sorrendet" | `prompts/skills/*` (a metódus maga) | **humán kapu kötelező** |

- [ ] **B1.1** A retrospec minden tanulságot **besorol** (projekt vs módszertan), és ennek megfelelő útvonalra tesz.
- [ ] **B1.2** Módszertan-tanulság SOHA nem íródik őrizetlenül a `prompts/skills/*`-ba — csak javaslat + humán kapu (BD1).

### B2. Központi tudástár (memória-stílus)

- [ ] **B2.1 — Hely + struktúra.** Központi tudástár mappa (pl. `prompts/knowledge/` vagy a projekt szintű megfelelője), egy tanulság = egy fájl. Pontos hely eldöntendő (lásd BO2).
- [ ] **B2.2 — Frontmatter séma.** Pl. `type: project | methodology | testing | git | deploy | ...`, rövid `description` (relevancia-kereséshez), forrás-ciklus hivatkozás.
- [ ] **B2.3 — Index.** Központi index-fájl (egy soros pointer / tanulság), amely betölthető a releváns fázisokba.
- [ ] **B2.4 — Dedup-before-add.** Hozzáadás előtt ellenőrizze, lefedi-e már egy meglévő bejegyzés → frissítés, ne duplázás.
- [ ] **B2.5 — Konszolidáció.** Időnkénti összevonás/karbantartás a bloat ellen (elavult/téves tanulság törlése).
- [ ] **B2.6 — Migráció.** A ma szétszórt tanulságok beemelése: `sdd-lightweight-flow.md` §5 „Lessons Learned" + a releváns `inprove-list.md` pontok → a központi tárba (vagy hivatkozás rá).

### B3. A retrospec skill — `prompts/skills/<NN>-retrospective.md`

- [ ] **B3.1 — Fájl + frontmatter.** Terminális fázis-skill, a 09 **után** fut. Számozás eldöntendő (lásd BO1: retrospec = igazi 10. fázis, az auto-run kapjon nem-sorszámozott nevet → AO2 újranyitva).
- [ ] **B3.2 — Artefakt-bányászat.** Olvassa a ciklus jeleit: `*-questions.md` (visszatérő kérdés = rés), hurok-naplók (ismétlődő bukás = minta), eszkalációk (tervezési hiba), tervtől eltérés / „beragadtam" pontok.
- [ ] **B3.3 — A loop (gépezet).** `gyűjt → kategorizál (projekt/módszertan) → dedup a meglévő tudás ellen → javasol (projekt: tudástárba; módszertan: skill-edit tervezet) → humán kapu → alkalmaz → időnként konszolidál`.
- [ ] **B3.4 — Humán kapu UX.** A módszertan-javaslatokat tömör, jóváhagyható formában mutassa (mit, hova, miért), és csak jóváhagyás után írjon a `prompts/skills/*`-ba.
- [ ] **B3.5 — Idempotencia / újrafuttatás.** Kétszeri futtatás ne duplázzon (a dedup + a forrás-ciklus hivatkozás védi).
- [ ] **B3.6 — Top-level vs subagent szétválasztás (BD4).** A **bányászat + kategorizálás + javaslat-tervezés** a `retrospector` subagentben fut (read-only, magas-reasoning modell); a **humán kapu és a tényleges írás** a top-level fő ágensé (kell az interaktív csatorna). Ez pontosan a meglévő `analyzer`/`reviewer`/`doc-sync-planner` minta (read-only diagnoszta subagent → top-level dönt/kérdez).

### B3a. `retrospector` subagent + modell-konvenció (BD4)

- [ ] **B3a.1 — Új ágens-fájl.** `prompts/agents/retrospector.md` (read-only diagnoszta): bemenet a ciklus-mappa + központi tudástár-index; kimenet egy strukturált javaslat (projekt-tudás bejegyzések + módszertan-edit tervezetek). `called_by: ["skills/<NN>-retrospective.md"]`, `tools: ["Read", "Grep", "Bash"]` (read-only).
- [ ] **B3a.2 — Eszközfüggetlen modell-mező a frontmatterben.** A jelenlegi ágens-/skill-frontmatter (README „Frontmatter séma") **nincs `model` mezője** — vezessünk be egy eszközfüggetlent, pl. `reasoning: standard | high` (vagy `model_tier`), ami NEM köt konkrét modellt, csak a szintet jelzi. Alapértelmezett (mező nélkül): `standard`.
- [ ] **B3a.3 — Per-eszköz leképezés dokumentálása (BD5).** A README-ben egy leképező tábla a tier → konkrét modell fordításhoz:

  | Tier | Claude Code | Antigravity CLI |
  |---|---|---|
  | `standard` (default, olcsó) | Sonnet | Gemini 3.5 Flash |
  | `high` | Opus 4.8 (`claude-opus-4-8`), Agent tool `model: "opus"` | Gemini 3.1 pro |

- [ ] **B3a.4 — Skill `subagents:` mező.** A retrospec skill frontmatter `subagents:` listája tartalmazza az `agents/retrospector.md`-t (a meglévő konvenció szerint).
- [ ] **B3a.5 — Graceful fallback (kvóta).** A `high` enhancement, nem hard requirement: ha a drága modell nem elérhető/kvóta elfogyott, a subagent essen vissza `standard`-ra. Ezt a fallback-szabályt a `retrospector` ágens-fájl és a README tier-szekciója is mondja ki.
- [ ] **B3a.6 — Tier-besorolás a fázisokon (BD5).** Vezessük át a `reasoning:` mezőt a többi skill/agent frontmatterébe a BD5 szerint: minden `standard`, kivétel `retrospector` = `high` (és opcionálisan `reviewer` = `high`, lásd BO5).

### B4. Integráció

- [ ] **B4.1 — README.** A retrospec felvétele a folyamatábrába (terminális lépés a merge után), skill-index, indító prompt, mappastruktúra.
- [ ] **B4.2 — Auto-run kapcsolat.** Az A. rész auto-run orchestrátora a merge **után** opcionálisan a retrospecet is meghívhatja (a merge kézi megerősítés UTÁN). Eldöntendő, hogy az auto-run hatóköre kiterjedjen-e a retrospecre.
- [ ] **B4.3 — Tudás betöltése.** Hol/hogyan kerül vissza a felhalmozott tudás a flow-ba (mely fázisok olvassák a központi indexet) — pl. 02/03 a tervezésnél, 06 az implementációnál.

### B5. Még nyitott / csiszolandó pontok

- [ ] **BO1 — Számozás.** Retrospec = `10-retrospective` (igazi terminális fázis)? Ekkor az auto-run nem-sorszámozott nevet kap (újranyitja AO2-t).
- [ ] **BO2 — Tudástár helye.** `prompts/knowledge/` (módszertan-szintű, repón belül) vs. projekt-szintű hely (a fejlesztett projekt gyökerében) vs. a kettő szétválasztva (projekt-tudás a projektbe, módszertan-tudás a `prompts/`-ba). A B1 kétutas modell ezt erősen befolyásolja.
- [ ] **BO3 — Mikor fusson a konszolidáció (B2.5)?** Minden retrospec-futáskor, vagy külön karbantartó parancsra?
- [ ] **BO4 — Trigger.** A retrospec automatikusan induljon a merge után, vagy a felhasználó explicit hívja?
- [ ] **BO5 — `reviewer` tier (a maradék nyitott pont).** A BD5 szerint a tier-konvenció általános, default `standard`, és csak a `retrospector` = `high`. Az egyetlen nyitott kérdés: a **`reviewer` (09)** is `high` legyen-e (utolsó merge-előtti kapu, bounded read-only → jó leverage), vagy a kvóta miatt maradjon `standard`? Az 05-analyze és a 02/03 a BD5 szerint `standard` (eldöntve).

---

## Munkamenet

**A. rész (auto-run):** döntések rögzítve (AD1=B, AD2=A). Nyitott: AO1–AO3. Sorrend: `A.3` lezárása → `A.1` (skill) → `A.2` (README).

**B. rész (retrospec):** döntések rögzítve (BD1=hibrid, BD2=memória-stílus, BD3=auto-bányászat, BD4=magas-reasoning `retrospector` subagent). Nyitott: BO1–BO5. Sorrend: `B5` lezárása → `B2` (tudástár felállítása + migráció) → `B3` + `B3a` (skill + `retrospector` ágens) → `B4` (integráció).

**Függőség a két rész között:** BO1 (számozás) és AO2 (auto-run név) **összefügg** — együtt kell eldönteni. A B4.2 az auto-run és a retrospec találkozási pontja.
