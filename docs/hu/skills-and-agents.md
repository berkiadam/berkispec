# Skillek, agentek és a frontmatter séma

← [Vissza a főoldalra](../../README-HU.md) · [Oldalindex](README.md)

## 6. Skill-index

| Parancs | Fázis | Bemenet | Kimenet (záró státusz) |
|---|---|---|---|
| `/bs-init-project` | Projekt init | Projekt leírás | `conventions.md` |
| `/bs-add-cycles` | Ciklusok kezelése | HLD/LLD vagy leírás | `specs/roadmap.md` (`Kész`) |
| `/bs-write-spec` | Spec | Roadmap + ciklus neve | `spec.md` (`Tervezésre kész`) |
| `/bs-write-code-plan` | Plan — kód-fél (03a) | `spec.md` | `plan.md` kód-szekciói (`Teszt-tervezésre kész`): `Cél`, `Érintett komponensek`, `Környezeti koordináták` (KO1), `Tervezett módosítások` (céllal, WY1), `Új függőségek`, `Konfiguráció`, `Séma-artefaktumok`, `Fordított lefedettség` (SC1), `Kockázatok`. **Önhordó és csonkítás-mentes** (KX3); a lezárás előtt **Lezárási kapu (TP2-code)** + **mechanikus kapu** (`analyze-gate-check.py --plan-code-only`, M) |
| `/bs-write-test-plan` | Plan — teszt-fél (03b) | `plan.md` kód-fele + a spec teszt-szekciója és `DoD`-ja | ugyanannak a `plan.md`-nek a teszt-szekciói (`Task írásra kész`): `Tesztstratégia`, `Teszt-forgatókönyvek` (`TS-NN`, TS1–TS8), `Gépi futtatási tábla` (TP4/PH1 — a **séma kötelező** [`TP4/b`]: a `run-tests.py` fix oszlop-pozíciókkal olvas, egy saját sémájú tábla nem hibázik, hanem rossz cellákat használ), `E2E infrastruktúra` (TP3), `Regressziós érintettség`, `Teszt specifikáció` (TI1/TA1/`Spec-lefedettség`), `Végrehajtási sorrend`, `Ellenőrzési stratégia`. **Belépő kapu (D5):** maga futtatja a `--plan-code-only`-t; a lezárás előtt **Lezárási kapu (TP2-test)** + **mechanikus kapu** (`analyze-gate-check.py --plan-only`, M) |
| `/bs-write-tasks` | Tasks | `plan.md` | `tasks.md` (`Implementálásra kész`) — a lezárás előtt **mechanikus kapu** (`analyze-gate-check.py`, M): `Must Fix` esetén nincs státuszváltás |
| `/bs-analyze` | Analyze | ciklus mappa | `analyze/analyze-report.md` (PASS/FAIL) + `analyze/analyze-task.md` (a triázsban jóváhagyott javítási lista) — mechanikus kapu + **négy párhuzamos diagnoszta-kör** (`analyzer` × 3 hatókör az 1–5. kategóriára, `analyzer-exec` a 6.-ra); a két lefedettségi táblát a kapu **generálja**. FAIL esetén orchestrált önjavító hurok (fixer-subagentek, `max X=3`, iterációnként **egy** analyzer-kör) |
| `/bs-implement` | Implementálás | `tasks.md` | kód + `tasks.md` (`Validálásra kész`) + `test-report/implement/check-log.md` (a `[CHECK]` futások append-only naplója), és ha a projekt az `implement`-et riport-fázisnak deklarálta (TR6), a `test-report/implement/` teljes riport-készlete is — a task listát **egy futásban** dolgozza fel (IM1): a task-commit nem fázis-vég |
| `/bs-validate` | Validálás + kódreview | ciklus mappa | PASS/FAIL + `test-report/` (`validation-report.md`, `code-review.md`, `validate/round-NN/`); PASS → státuszok `Kész` — a tesztek/Sonar/E2E futtatását a `test-runner`, a diff átnézését a `reviewer` subagent végzi, a PASS/FAIL döntést és a DoD-ot az orchestrátor; FAIL esetén orchestrált önjavító hurok (`implement-fixer` / `review-fixer`, három leállási korlát, VD3a szerződés-kapu, VD5 eszkaláció) |
| `/bs-doc-sync` | Doc-sync | ciklus mappa + `docs-generated/` + `specs/test-conventions.md` | konzisztens `docs-generated/` (system-overview, architecture, CHANGELOG, design-drift, README mappa-index) + komponens README-k + `specs/test-conventions.md` (promóció / `Utolsó futás` bump / elavult tétel törlése, TC1–TC11) + `doc-sync-plan.md` — terv (`doc-sync-planner`) → mechanikus végrehajtás → objektív kapu (DS22, 3/4 pont a `ds22-gate-check.py` scripttel, LLM nélkül) + TC8 kapu a regiszterre (`tc8-gate-check.py`, teljesen szkriptelt); kapu-bukás → ember-vezérelt javítás (`doc-sync-questions.md`) |
| `/bs-review-and-merge` | Review and merge (09) | ciklus mappa, `conventions.md` | **PR nélküli út.** `main` behozása a ciklus ágába → `VP2` post-merge kör (`test-report/post-merge/`: tesztek + Sonar + riport-kapu) → merge kézi megerősítéssel (RD8) → ág-törlés **a verifikáció mögött** → lezárt roadmap + generált `cycle-status.md`. Nincs hurok és nincs subagent; a kapuk bukása visszairányít a `07`-re vagy a `08`-ra. `PR submission: yes` esetén **hibát ad** és a három lépéses láncra irányít |
| `/bs-create-pr` | Create PR (09a) | ciklus mappa, `conventions.md` | felküldött ciklus-ág + megnyitott PR (a description a `code-review.md`), frissített `cycle-status.md`; a roadmap még **nem** zárul le (`⏳ verifikációra vár`). A PR-t **nem** merge-eli |
| `/bs-review` | Review a PR-en (09b) | ciklus mappa + nyitott PR | `test-report/ci-code-review.md` — a `reviewer` subagent a **PR diffjén**, központosított SDD-ben gépi futtatásban; a `07` lokális `code-review.md`-jét **soha nem írja felül**. Nyitott `Must Fix` → értesítés, a PR nyitva marad; `auto-fix-loop` esetén a CI hurka indul a `07` korlátaival |
| `/bs-merge` | Merge (09c) | ciklus mappa, nyitott + **elfogadott** PR | `test-report/post-merge/` (`VP2`) → csak zöld után a PR beolvasztása; belépő kapu a **PR-állapot** (ez veszi át az RD8 szerepét) és **mindkét** review-jelentés (`validate-gate-check.py --review-only --require-ci-review`) |
| `/bs-dev-test` | Dev-teszt (09d, **opcionális**) | beolvasztott ciklus, `Dev deployment test: yes` | `test-report/dev-test/` (`VP3`) — deploy a `Dev deployment command`-dal egy integrált környezetbe, valódi e2e kör, test manager feltöltés (gyárilag ez a fázis tölt fel); zöld kör = a ciklus lezárása |
| `/bs-quick-flow` | **Egyszerűsített flow** (külön út) | feladat leírása, vagy `brainstorm: NN` | `spec-plan.md` (`Task írásra kész`) + `tasks.md` (`Implementálásra kész` → `Kész`) + implementáció — háromfázisú, kis feladatokhoz; státusz-mezők + RP1 útvonal-kapu; opcionális `researcher`/`analyzer`/`reviewer`; túlnövéskor átirányít a `/bs-add-cycles`-ra |
| `/bs-brainstorm` | **Ötletelés** (segédparancs, a flow előtt) | téma szabad szöveggel, vagy `folytassuk a NN-est` | `.bs-brainstorm/brainstorm-NN-<slug>.md` — perzisztens munkafájl (tények forrással, alternatívák trade-offokkal, döntések, nyitott kérdések, javasolt ciklus-vágás). Nem fázis, nem változtat státuszt; kódot és a mappán kívül semmit nem ír. Átadás: `/bs-add-cycles brainstorm: NN` (BS18) vagy `/bs-quick-flow`. |
| `/bs-export-doc` | **PDF export** (segédparancs) | markdown fájl(ok), opcionális — üresen a `docs-generated/architecture.md` és `system-overview.md` | `export/<név>-v<N>.pdf` — fájlonként független verziószám (utolsó + 1, v1-től); pandoc + `mermaid-filter` + xelatex, a ciklus a címlapon (`Lefedve: cycle-NN-ig · vN`). Nem fázis: nincs előfeltétele, nem változtat státuszt. |
| `/bs-run-tests` | **Cikluson kívüli teszt-futtatás** (segédparancs, bármikor) | kategória (opcionális), környezet (opcionális: `local` / `remote`) | `test-runs/<kategória>/<UTC-időbélyeg>/<env>/` — a `run-tests.py` `--table-source conventions` futásának eredménye: `results.json` (`"cycle": null`), riport-artefaktumok, és — ha van teszt-leltár — `<TL-NNN>/` alkönyvtárak a tételenkénti visszakereséshez. Plusz `test-runs/latest.json` (kategóriánként az utolsó futás). Bemenet: `conventions.md` → `## Teszt-futtatás` (KT1). **Bizonyíték-tűzfal (D8):** a `dod-check.py` és a `report-gate-check.py` a `test-runs/` alatti útvonalat `exit 2`-vel visszautasítja. Nem fázis: nem változtat ciklus-státuszt, ciklus-artefaktumot nem ír. |
| `/bs-manual-test-plan` | **Kézi tesztterv** (segédparancs, az 05 után bármikor) | ciklus mappa (opcionális), opcionálisan `mód: tervezett` / `mód: as-built` | `manual-test-plan.md` — komponens-indítás, tesztadatok, `TG-NN` tesztcsoportok (`curl` + `.http`, konkrét elvárt eredménnyel), kétirányú `DoD-NN` lefedettség és az automata teszteredmények helye. Előfeltétel: `analyze-report.md` = `PASS`, **vagy** — egyszerűsített ciklusban, ahol nincs `plan.md` — a `tasks.md` státusza `Implementálásra kész` / `Kész` (QF8). Determinisztikus kapu (`manual-test-gate-check.py`, MG1–MG10). Nem fázis: nem változtat ciklus-státuszt, újrafuttatáskor néma merge + `Változásnapló`. |
| `/bs-cycle-status` | **Státusz ellenőrző** | ciklus neve vagy elérési útja (opcionális) | Kimutatja a ciklusok státuszát (Kész/Folyamatban), és interaktív TUI vagy közvetlen módon részletesen listázza a fázisok előrehaladását (KÉSZ, KÉSZ*, FOLYAMATBAN, MÉG NEM FUTOTT) felismerve a flow típusát. |

A fázis-skillek (`00–09`) **frontmattere** rögzíti az előfeltételeket, a kimenetet, a szomszédos fázisokat (`prev`/`next`) és a hívott subagenteket. Az egyszerűsített flow skill és a segédparancsok (`bs-brainstorm`, `bs-export-doc`, `bs-manual-test-plan`) ettől eltérő, `name`/`description` alapú frontmattert használnak (nem fázisok, lásd a „Két fejlesztési út" szekciót).

## 7. Agent-index

| Ágens | Hívja | Mit csinál | Kimenet |
|---|---|---|---|
| `agents/reviewer.md` | 07 | Git diff code review a validálási kör 2. lépéseként (statikus réteg — zöld gyors tesztek után, a nehéz tesztek előtt) | `test-report/code-review.md` (Must Fix + Suggestions) |
| `agents/analyzer.md` | 05 | Kereszt-fázisos **szemantikai** konzisztencia-diagnózis (read-only, **1–5. kategória**: duplikáció, ambiguitás, alulspecifikáció, konvenció-ütközés, a lefedettség **tartalmi** ítélete a kapu generált mátrixán). **Hatókör-paraméterrel három párhuzamos körben fut** (SH1), körönként a kapu által kimetszett szeletből. Repóhoz nem nyúl. **Az egyetlen agent a rendszerben, ami a legdrágább (`deep_reasoning_agent`, Opus-osztályú) tier-en fut** — lásd 4.3 | megállapítás-lista → `analyze-report.md` |
| `agents/analyzer-exec.md` | 05 | **Végrehajthatósági** diagnózis (read-only, **6. kategória**: prózában ígért teszt, artefaktum-tulajdon, destruktív művelet teljessége, horgony-szimbólum, artefaktum-hang) a `plan.md` + `tasks.md` + kapu-leltár hármasból. Az `analyzer`-rel **párhuzamosan** fut (E), `default` tieren: a leltár készen adja a jelölteket, tehát nem felfedez, hanem behatárolt listát ítél meg | megállapítás-lista + Végrehajthatósági leltár |
| `agents/researcher.md` | 00, 01, 02, 03, 06, `bs-brainstorm` | **Mód A** (03): forrásfájl-azonosítás + dokumentáció-kutatás a spec alapján. **Mód B** (00/01/02/06 + brainstorm): ad-hoc kódbázis-kutatás (modul/szimbólum/nagy fájl megértése egy konkrét kérdésre; brainstormban **párhuzamosan indítva**, leletet adva, nem ítéletet). Legolcsóbb (`research_agent`) tier — tiszta grep/glob/read fan-out, nincs benne tervezési ítélet | path-listák / tömör összefoglaló, soha nyers fájltartalom |
| `agents/test-runner.md` | 07 | Unit/integration/Sonar/E2E/regressziós tesztek lefuttatása, portütközés-elhárítás, ideiglenes erőforrás-takarítás — **tényszerű összegzést ad, nem dönt** PASS/FAIL-ről. `default` tier (szándékosan **nem** a legolcsóbb — a projektenként eltérő teszt-/Sonar-kimenet megbízható, konzisztens összegzése a 3-próba számláló miatt kritikus) | strukturált PASS/FAIL riport kategóriánként |
| `agents/doc-sync-planner.md` | 08 | A `docs-generated/` mappa + ciklus-diff **read-only** diagnózisa; per-fájl pipálható terv + DS22 kapu-leltár. **A csereszöveget is ő írja meg** (sebészi patch: cél-szekció + jelenlegi részlet + új szöveg) — így a fő ágensnek nem kell újraolvasnia/újrakomponálnia a doksikat, csak alkalmaz | `doc-sync-plan.md` tervjavaslat + csereszövegek + `doc-sync-questions.md` kérdések |
| `agents/spec-fixer.md` | 05 | Az önjavító hurok 02 fix-mód belépője (vékony wrapper → `/bs-write-spec` Fix-mód). `default` tier — az `analyzer` már pontos, előre azonosított hibalistát ad neki, nem kell felfedeznie a problémát. **Visszatérés előtt maga futtatja a mechanikus kaput** (GS1) | javított `spec.md` + új `spec-questions.md` `Knn`-ek |
| `agents/plan-fixer.md` | 05 | Az önjavító hurok 03 fix-mód belépője (vékony wrapper → a `/bs-write-code-plan` és a `/bs-write-test-plan` Fix-módja). **Mindkét felet javíthatja** ugyanabban a `plan.md`-ben, ezért mindkét minőségi kaput beemeli. `default` tier (ua. indoklás) | javított `plan.md` + új `plan-questions.md` `Knn`-ek |
| `agents/tasks-fixer.md` | 05 | Az önjavító hurok 04 fix-mód belépője (vékony wrapper → `/bs-write-tasks` Fix-mód). `default` tier (ua. indoklás) | javított `tasks.md` + új `tasks-questions.md` `Knn`-ek |
| `agents/implement-fixer.md` | 07 | A validate-hurok 06 fix-mód belépője (vékony wrapper → `/bs-implement` Fix-mód). `default` tier — a 06 anti-„teszt-csalás" garde-ja kifejezetten számol azzal, hogy olcsóbb LLM futtatja | javított kód + lezárt `## Validációs javítások` taskok (+ esetleges eszkalációs jelzés) |
| `agents/review-fixer.md` | 09 | A review-hurok 06 fix-mód belépője (vékony wrapper → `/bs-implement` Fix-mód, `## Review javítások` bemenet) | javított kód + lezárt `## Review javítások` taskok (+ esetleges eszkalációs jelzés) |

---

## 8. Frontmatter séma

**Skill (`skills/*.md`):**

```yaml
---
phase: 02
name: write-spec
prerequisites:
  - "specs/roadmap.md státusz: Kész"
output:
  - "specs/cycle-NN-<name>/spec.md státusz: Tervezésre kész"
prev: 01-add-cycles
next: 03a-write-code-plan
subagents: []        # Task tool-on hívott specialisták (agents/ alatti fájlok)
shared: []           # opcionális: shared/ alatti közös blokkok, amiket a telepítő build-time inline-ol (pl. a 00/01 shared/git-preflight.md-t)
---
```

**Ágens (`agents/*.md`):**

```yaml
---
name: reviewer
description: "Read-only kód-review diagnoszta (test-report/code-review.md). A 07-validate skill hívja."
role: "Kód-review specialista ágens"
called_by: ["skills/07-validate.md"]
inputs: [...]
outputs: [...]
tools: ["Read", "Bash", "Grep"]
---
```

- A **`description`** az ágens-regisztráció **kanonikus, kötelező** mezője: a Claude Code (és a Cursor) `name` + `description` alapján ismeri fel a subagentet és dönt a hívásáról, ezért „mit + mikor hívd" jellegű legyen. A `role` egy rövid emberi címke, amely megmarad; ha a `description` hiányozna, a telepítő a Codexnél/Cursornál erre esik vissza, de a Claude/Copilot frontmatterbe a `description` **kell**.
- A **`shared`** (skilleknél) a `shared/` alatti közös szövegblokkokat jelzi, amelyeket a skill `<!-- INCLUDE:shared/<fájl> -->` markerrel hivatkoz, és a telepítő **build-time inline** beágyaz. A `shared/context-check.md`-t **minden fázis-skill**, a `shared/python-cmd.md`-t minden szkriptet hívó skill (`03`, `04`, `05`, `07`, `08`, `10`, `export-doc`), a `shared/git-preflight.md`-t a `00`/`01` (branch-nyitó fázisok), a `shared/input-from-prev.md`-t a `01`/`02`/`03`/`04`/`07` (fázisok közötti átadás, IP1), a `shared/artifact-voice.md`-t a `02`/`03`/`04` (artefaktum-hang, AV1), a `shared/phase-commit.md`-t a `02`/`03`/`04`/`05`/`07` (fázis-záró commit, PC1), a `shared/path-format.md`-t a `02`/`03`/`04` minőségi kapuja (útvonal-konvenció, RP1), a `shared/conventions-change.md`-t a `03` (kapu-konfiguráció, GC1) hivatkozza. **A markert a subagent-promptok is használhatják** (`prompts/agents-hu/*.md` és a gemini `agent.json` `Instructions` szekciója), és a beemelt fájl maga is tartalmazhat markert (a telepítő rekurzívan oldja fel). Ezen múlik a D13: a `shared/quality-check-{spec,plan,tasks}.md` és a `shared/fix-mode-{spec,plan,tasks}.md` egyszerre kerül a fázis-skillbe és a hozzá tartozó fixer-agent promptjába, így a fixer **nem olvas fázis-skillt** a javításhoz.

A frontmatter egyébként **eszközfüggetlen** (saját séma, nem egy konkrét ágens-eszközhöz kötött); a telepítő fordítja a cél-platform natív formátumára (Claude/Cursor `.md`, Codex `.toml`, Copilot `.agent.md`, Antigravity `agent.json`).

**A `05-analyze` `subagents:` mezője** a két read-only diagnoszta-definíció (`analyzer` — három hatókörrel, párhuzamosan indítva —, `analyzer-exec`) mellett a három fixer-wrappert is felsorolja: `agents/spec-fixer.md`, `agents/plan-fixer.md`, `agents/tasks-fixer.md`. **A `07-validate` `subagents:` mezője** az `agents/test-runner.md`-t (tesztek/Sonar/E2E mechanikus futtatása, `default` tier), az `agents/reviewer.md`-t (read-only kód-diagnózis a kör 2. lépéseként) és a két fixer-wrappert — `agents/implement-fixer.md` (teszt/Sonar/DoD) és `agents/review-fixer.md` (Must Fix findingok) — tartalmazza. **A `08-doc-sync` `subagents:` mezője** az `agents/doc-sync-planner.md` read-only tervkészítő diagnosztát tartalmazza (a per-fájl `doc-sync-plan.md` szerzője; a doksik tényleges írása a fő ágensé — nincs fixer-wrapper, mert ez nem önjavító hurok). **A ciklusvég skilljei közül csak a `09b-review`-nak van `subagents:` mezője** (`agents/reviewer.md` — a PR diffjén futó, központosított úton gépi review, `test-report/ci-code-review.md`-be). A `09-review-and-merge` / `09a-create-pr` / `09c-merge` / `09d-dev-test` **subagent nélkül** fut: kapukat ellenőriznek, teszt-kört futtatnak és beolvasztanak — a lokális review továbbra is a `07` dolga (RV1). **A `00-init-project`, `01-add-cycles`, `02-write-spec` és `06-implement` `subagents:` mezője** az `agents/researcher.md`-t tartalmazza ad-hoc kódbázis-kutatáshoz (Mód B) — ugyanaz az ágens, amit a `03a-write-code-plan` a rendszerezett forrásfájl-azonosításhoz (Mód A) használ. Fontos a skill/agent szétválasztás megőrzése: **a fix-mód viselkedése egyetlen helyen él**, és a wrapper-agent csak belépő — nincs logika-duplikáció. Ennek **két megvalósítása** van:
- **02/03/04 (analyze-hurok, D13):** a fix-mód és a fázis minőségi kapuja a `prompts/shared-hu/{fix-mode,quality-check}-*.md` fájlokban él, és **build-time beemelődik a skillbe ÉS a fixer-wrapperbe is**. A fixer így **nem olvas fázis-skillt** — a promptja önhordó (a `plan-fixer` ~80 sor a 584 soros `03a-write-code-plan.md` + 683 soros `03b-write-test-plan.md` beolvasása helyett). **A `03` minőségi kapuja a hasítás óta KÉT shared fájlban él** (`quality-check-plan-code.md` + `quality-check-plan-test.md`): a `03a` az elsőt, a `03b` a másodikat emeli be, a `plan-fixer` **mindkettőt** — mert a fixer a `plan.md` mindkét felét javíthatja.
- **06 (a 07 önjavító hurka):** az `implement-fixer` és a `review-fixer` továbbra is a **`06-implement.md` „Fix-mód" szekciójának beolvasásával** delegál (`## Validációs javítások`, illetve `## Review javítások` bemeneti szekcióval, azonos mechanikával). Itt a kiemelés még nem történt meg — a 06 skill jóval rövidebb (294 sor), de a 07 hurka körönként hívja a fixert, tehát ugyanaz a megtakarítás elérhető, ha a szekció ugyanígy `shared/`-be kerül.

---
