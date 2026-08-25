---
phase: 00
name: bs-init-project
description: "berkispec - 00. Használd a projekt legelső indításakor (Phase 00), vagy ha a gyökér 'conventions.md' hiányzik/hiányos. A fejlesztővel közösen rögzíti a globális projektkonvenciókat (tech stack, teszt, fejlesztési flow, git merge stratégia) a 'conventions.md'-ben — ez minden további fázis előfeltétele."
prerequisites: []
output:
  - "conventions.md (projekt gyökér)"
prev: null
next: bs-add-cycles
subagents:
  - "agents/researcher.md"
shared:
  - "shared/git-preflight.md"
---
# 00 — Projekt inicializálás
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

Ez a prompt egyszer fut le, új projekt indulásakor. Célja a projekt konvencióinak rögzítése, amelyekre az összes fejlesztési ciklus (02–09) hivatkozni fog.

---

## Git-előkészítés — az init saját branch-en fut (BD12)

A `00-init-project` **maga is feature branch-en dolgozik**, alapértelmezett néven `feature/init-project`. **Csirke-tojás sorrend:** a git *elérhetőségét* már itt, az elején detektáld; a „van-e (és lesz-e) verziókezelő" formális rögzítése (BD11) lentebb, a kérdéseknél történik.

1. **Git-elérhetőség detektálása:** `git rev-parse --is-inside-work-tree` (vagy `git rev-parse --git-dir`).
   - **Ha nincs git / nem git-repo** → **ne** hozz branch-et, **ne** PR-ezz/merge-elj. Folytasd közvetlenül a konvenciók rögzítésével; a lenti VCS-kérdés (BD11) rögzíti a `conventions.md`-be a „NINCS VCS" flaget.
   - **Ha van git** → futtasd a branch-nyitó preflightet (lent), majd hozz létre és válts az init-branch-re:

<!-- INCLUDE:shared/git-preflight.md -->

2. **Branch létrehozása (csak git esetén):** a friss, tiszta `main` után `git switch -c feature/init-project`. Az init innentől ezen a branch-en dolgozik (a `conventions.md` írása, commit).
3. **Visszaintegrálás a futás végén:** lásd „Lezárás" — a `conventions.md`-be rögzített `## <sec:cv_merge_strategy>` (BD7/BD15) szerint PR vagy közvetlen merge `main`-be; ha nincs döntés/remote, a **default a közvetlen merge** (BQ7).

---

## Feladatod

Hozz létre egy `conventions.md` fájlt a projekt gyökerében az alábbi struktúra szerint. Minden szekciót a felhasználóval közösen töltötök ki — tegyél fel kérdéseket, ahol a döntés nem egyértelmű. A struktúrában szereplő technológiák (pl. Playwright, pytest) és beállítások **ajánlott default-ok**; ezeket a projekt tényleges tech stackje alapján testre kell szabni (pl. Node/Jest, Go/go test stb.).

Az alábbi szekcióknál **aktívan rá kell kérdezned** (nem elég csak pre-fillelni):

- **Verziókezelő megléte (BD11 — KAPU, elsőként):** <!-- INCLUDE:lang/00-init-project.md#BD11-vcs-kerdes --> A git *elérhetőségét* már a „Git-előkészítés" lépésben detektáltad; itt a szándékot rögzíted. Ha **nincs és nem is lesz**, írd a `## <sec:cv_git_conventions>` szekcióba **explicit**: <!-- INCLUDE:lang/00-init-project.md#BD11-nincs-vcs-flag --> Ez a flag **kapuzza** a 01 (és a többi fázis) összes git-lépését: ott ekkor nincs `git switch -c`, nincs branch-figyelmeztetés, nincs commit — csak a `specs/cycle-NN-<name>/` mappa + roadmap készül.
- **<field:f_default_flow>:** kérdezz rá a feladatok jellegére, és ez alapján rögzíts egy default munkamódot: <!-- INCLUDE:lang/00-init-project.md#flow-kerdes --> A választ a `## <sec:cv_methodology>` szekció **<field:f_default_flow>** mezőjébe írd.
- **<sec:cv_test_framework>:** <!-- INCLUDE:lang/00-init-project.md#teszt-stack-kerdes -->
- **Teszt-riportolás (TR3 — KÖTELEZŐ kérdés, a teszt stack után):** <!-- INCLUDE:lang/00-init-project.md#TR3-riport-kerdes --> A választ a `## <sec:cv_test_reporting>` szekció **táblázatába** vezesd (kategória / eszköz / parancs / artefaktum). **Ezt a szekciót nem hagyhatod pre-fillelt default-tal** — vagy valós parancsok kerülnek bele, vagy a felhasználó explicit kimondja, hogy nincs riport-generálás, és akkor a `**<field:f_report_required>:**` mező `nem` + indoklás. Ha az eszköz többféle formátumot tud, **egyfájlos HTML-t javasolj** (a riport a ciklus git-diffjébe kerül).
- **Merge stratégia + visszaintegrálás (BD7/BD15):** kérdezd meg a git szolgáltatót (GitHub / Bitbucket Cloud / Bitbucket Server / GitLab / Lokális), majd **próbáld ki az access-t** a megfelelő paranccsal (lásd a Merge stratégia szekciónál). Ha az access teszt sikertelen, **ne zárd le a `conventions.md`-t** — kérd a token / URL / permissions javítását, vagy alternatív szolgáltató / lokális merge választását. Ez az **egyetlen igazságforrás** arra, hogyan kerül vissza `main`-be egy elkészült branch (PR vagy közvetlen merge) — ezt használja a 09 (ciklus-merge), a 01/00 branch-figyelmeztetés, és a 00 init-branch visszaintegrálása is. Ha nincs döntés/remote, a default a **közvetlen merge** (BQ7). _(Csak a `## <sec:cv_merge_strategy>` szekciót töltsd — ne vezess be új mezőt.)_
- **Branch-elnevezési stratégia (BD8 — csak ha van VCS):** kérdezd meg:
  - Kell-e **Jira-jegyszámot** a branch nevének elejére? (ha igen: milyen formátumban)
  - A feature branch-ek **`feature/` prefixszel** kezdődnek-e?
  - **Vagy** mutass rá egy dokumentumra, ahol ezek tisztázva vannak (onnan vesszük át a szabályt).
  A választ a `## <sec:cv_git_conventions>` **<field:f_branch_naming>** mezőjébe írd. **Default** (ha a felhasználó nem rendelkezik): `feature/cycle-NN-<name>` (a mappanév mindig prefix nélkül, tisztán `cycle-NN-<name>` — BD3). Kis branching-szabály (prefix, Jira-jegy) mehet **szó szerint** a `conventions.md`-be.
- **API-szabályzat / API design guideline (BD9):** <!-- INCLUDE:lang/00-init-project.md#BD9-api-guideline-kerdes --> A pointer a `## <sec:cv_references>` szekcióba kerül, hogy a 02–03 fázis ebből dolgozhasson.
- **Nagy külső szabály-dokumentumok (BD10 — hibrid: pointer + kivonat):** ha a felhasználó **nagy** dokumentumra mutat (API-guideline, terjedelmes branching-szabályzat), azt **NE** tedd be teljes szöveggel a `conventions.md`-be (minden fázis behúzná → token-duzzadás). Helyette: **(a)** pointer a `## <sec:cv_references>`-ba (forrás elérési útja/URL + egysoros leírás, mit szabályoz); **(b)** a `researcher` subagenttel (`agents/researcher.md`) **egyszer** olvastasd be, és hozass ki belőle egy tömör, normatív **szabály-checklistet** (konkrét do/don't pontok), ami a `conventions.md`-be kerül. A mély/ritka részleteket a fogyasztó fázis (branching → 01, API → 02–03) on-demand a `researcher`-rel olvassa. A pointer megőrzi a forrást, így a kivonat újragenerálható, ha a doksi változik.

Ne kezdj spec-et, plan-t vagy implementációt. Ez a lépés kizárólag a projekt konvencióit rögzíti.

---

## Kontextus betöltési szabályok

- Csak annyi információt gyűjts be a projektről, amennyi a `conventions.md` kitöltéséhez szükséges.
- Ha a projekt már létező kódot tartalmaz és egy komponens mélyebb megértése kell, hívd a `researcher` subagentet (`agents/researcher.md`, Mód B) — csak összefoglalót ad vissza, a nyers fájltartalom nem kerül be a fő kontextusba.

## Kérdezési szabályok

- Csak **egy** kérdést tegyél fel egyszerre.
- Ha a felhasználó válasza újabb kérdést nyit meg, add hozzá a listához.
- Addig iterálj, amíg minden szekció ki nem töltött.

## Megállási szabályok

- Ha a felhasználó válasza ellentmond a korábban rögzített konvencióknak, jelezd az ellentmondást és kérd pontosítását.
- Ha a felhasználó olyan technológiát választ, amelyről nincs információd, jelezd és kérd, hogy adjon referenciát vagy dokumentációt.

---

## conventions.md struktúra

```md
<!-- INCLUDE:lang/00-init-project.md#conventions-sablon -->
```

---

## Folytatás megszakított futás után

Ha a 00 fázis félbeszakadt és új sessionban folytatódik:

```
1. Létezik már conventions.md?
   → Olvasd be, és nézd meg, mely szekciók kitöltöttek.
   → Folytasd az első hiányos/üres szekciótól — ne kezdd elölről.

2. A conventions.md létezik, de hiányos (üres szekciók, kitöltetlen Merge
   stratégia, lefuttatlan access validáció)?
   → A conventions.md NEM tekinthető késznek, amíg minden szekció kitöltött
     ÉS a merge access validáció sikeres. Folytasd a hiányzó részekkel.

3. Nincs conventions.md?
   → Kezdd a "Feladatod" szerint.
```

---

## Lezárás

> **A `conventions.md` „kész" jelölése a puszta léte** — nincs külön státuszmező. Ezért a fájl csak akkor jöhet létre véglegesen (commitba kerülve), ha minden szekció kitöltött és a minőségellenőrzés átment. A 01–08 fázisok ezután csak létezés-ellenőrzést végeznek.

### Minőségellenőrzés — lezárás előtt

Mielőtt lezárod, ellenőrizd:
1. Minden szekció kitöltött (nincs üresen hagyott pre-fill placeholder)?
2. A Teszt keretrendszer a fejlesztővel egyeztetett (nem csak a default maradt megerősítés nélkül)?
2.a/b **Ki van töltve az `**<field:f_artifact_path_base>:**` mező (TR5/b)?** — új projektben `kör-mappa`. Enélkül a `07-validate` TR3 kapuja `exit 2`-vel megáll.
2.a **A `## <sec:cv_test_reporting>` szekció valós adatokkal kitöltött (TR3)?** — a táblázatban tényleges riport-generáló parancsok és artefaktum-nevek állnak, **vagy** a `**<field:f_report_required>:**` mező `nem` + indoklás. Sablon-placeholder (`<parancs>`, `<a választott futtató>`) nem maradhat benne: a `07-validate` kapuja ezt a táblát olvassa, és placeholder mellett minden ciklus bukna.
3. A Merge stratégia kitöltött, és az access validáció **sikeresen lefutott** (vagy a fejlesztő explicit lokális merge-et választott)?
4. A portok, env változók és Sonar (ha van) szekciók a projekt valóságát tükrözik?
5. A `## <sec:cv_methodology>` **<field:f_default_flow>** mezője a fejlesztővel egyeztetett értékre van állítva (`teljes` vagy `egyszerűsített`), nem maradt placeholder?
6. **A `## <sec:cv_git_conventions>` VCS-flagje beállítva (BD11):** vagy git, vagy explicit „NINCS verziókezelő …"?
7. **VCS mellett: a Branch-elnevezési stratégia mező kitöltött (BD8)** (default `feature/cycle-NN-<name>`, vagy a szervezeti szabály/pointer)?
8. **Ha a felhasználó API design guideline-t / nagy szabályzatot jelölt (BD9/BD10):** a `## <sec:cv_references>`-ban ott a pointer, és nagy doksinál a `researcher`-rel készített tömör szabály-checklist?

Ha bármelyikre nem, egészítsd ki, mielőtt lezárod.

### Commit, visszaintegrálás és jelzés

Ha a minőségellenőrzés átment:

1. **Commit (csak VCS esetén) — a `feature/init-project` branch-en** (BD12):
   ```bash
   git add conventions.md && git commit -m "cycle-NN: 00-init"
   ```
   _(A 00 fázis nem ciklusspecifikus; a `cycle-NN:` prefix az első ciklusra utal — pl. `cycle-01: 00-init`.)_
2. **Visszaintegrálás `main`-be (csak VCS esetén) — a `## <sec:cv_merge_strategy>` szerint (BD7/BD12):** a szekcióban rögzített szolgáltató alapján **PR feladás** vagy **közvetlen merge** `main`-be; ha nincs explicit döntés/remote, a default a **közvetlen merge** (BQ7). Destruktív lépés (merge/branch-törlés) előtt kérj felhasználói megerősítést.
3. **No-VCS ág (BD11):** ha a `conventions.md` szerint nincs verziókezelő, az 1–2. lépés kimarad — a `conventions.md` fájl puszta léte a „kész" jelölés, branch/commit/merge nélkül.
4. Jelezd a felhasználónak:

<!-- INCLUDE:lang/00-init-project.md#zaro-uzenet -->