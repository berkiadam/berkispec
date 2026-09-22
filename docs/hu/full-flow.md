# Teljes berki spec flow (00–09)

← [Vissza a főoldalra](../../README-HU.md) · [Oldalindex](README.md)

Ez a fejezet a **teljes, sokfázisú** fejlesztési utat írja le a folyamatábráival — a projekt-setuptól (00–01) a per-ciklus loopon át (02–09) a merge-ig, az önjavító hurkokkal együtt. A **másik utat**, az egyszerűsített háromfázisú flow-t lentebb, az „Egyszerűsített (lightweight) flow" fejezet részletezi.

> **Kód-jelölések:** a szövegben a `DS`/`VD`/`RD`/`LC`/`SK` + szám alakú kódok (pl. `DS22`, `RD6`, `LC1`) a skill-fájlok belső szabály-azonosítói. A részletes definíciójuk az adott skillben él; itt csak visszakereshető horgonyként szerepelnek, a README megértéséhez nem kell feloldani őket.

## 4.1 Magas szintű összefoglalás

Ez a diagram összefoglalja a 00–09 fázisok egymás utáni folyamatát, a kezdőpontokat, az interjú loopokat és a hibajavítási visszacsatolásokat.

```mermaid
flowchart TD
    %% Styling definitions
    classDef setup fill:#e0f2fe,stroke:#2563eb,stroke-width:2px,color:#1e293b;
    classDef design fill:#e0f2fe,stroke:#0d9488,stroke-width:2px,color:#1e293b;
    classDef dev fill:#e0f2fe,stroke:#16a34a,stroke-width:2px,color:#1e293b;
    classDef review fill:#f3e8ff,stroke:#8b5cf6,stroke-width:2px,color:#1e293b;
    classDef doc fill:#f3e8ff,stroke:#8b5cf6,stroke-width:2px,color:#1e293b;
    classDef start fill:#f1f5f9,stroke:#64748b,stroke-width:2px,color:#1e293b;
    classDef userInput fill:#ffedd5,stroke:#ea580c,stroke-width:2px,color:#7c2d12;

    %% Kezdőpontok
    Start1(["Kezdés üres projektben"]):::start
    Start2(["Új ciklus hozzáadása"]):::start
    BS(["<b>/bs-brainstorm</b> (opcionális)<br/>feltáró ötletelés a spec előtt<br/>.bs-brainstorm/brainstorm-NN.md"]):::userInput

    %% Fázisok dobozai
    0["<b>0. Project Setup</b><br/>(create conventions.md)"]:::setup
    1["<b>1. Init Cycles</b><br/>(create roadmap.md, cycle dir)"]:::setup
    2["<b>2. Create Spec</b><br/>(create spec.md)"]:::design
    3["<b>3. Create Plan</b><br/>(two steps: 03a code plan + 03b test plan → plan.md)"]:::design
    4["<b>4. Create Tasks</b><br/>(create tasks.md from plan.md)"]:::design
    5["<b>5. Analyze</b><br/>(cross-phase consistency check)"]:::design
    6["<b>6. Implement</b><br/>(create code from plan.md and tasks.md)"]:::dev
    7["<b>7. Validate</b><br/>(regression, sonar and E2E check)"]:::dev
    8["<b>8. Doc-sync</b><br/>(docs-generated/ konzisztencia + objektív kapu)"]:::doc
    9["<b>9. Review and Merge</b><br/>(isolated SDD — local review + merge)"]:::review
    9a["<b>9a. Create PR</b><br/>(centralized SDD)"]:::review
    9b["<b>9b. Review</b><br/>(machine-run on the CI)"]:::review
    9c["<b>9c. Merge</b><br/>(+ post-merge tests, VP2)"]:::review
    9d["<b>9d. Dev-test</b> — optional<br/>(deploy + real E2E, VP3)"]:::review
    End([Ciklus befejezve]):::start

    %% Tisztázó interjú csomópontok
    Int0(["Felhasználói interjú"]):::userInput
    Int1(["Felhasználói interjúk"]):::userInput
    Int2(["Felhasználói interjúk"]):::userInput
    Int3(["Felhasználói interjú"]):::userInput

    %% Kezdő kapcsolatok
    Start1 --> 0
    Start2 --> 1

    %% Opcionális előszoba: a brainstorm nem fázis — a munkafájlból desztillált
    %% cycle-design-input.md-n keresztül ad bemenetet a 00/01 fázisnak (BS18).
    BS -. "még nincs conventions.md" .-> 0
    BS -. "brainstorm: NN → cycle-design-input.md" .-> 1

    %% Fázisok közötti átmenetek és visszacsatolások
    0 --> 1
    0 <--> Int0

    1 --> 2
    1 <--> Int1

    2 --> 3
    2 <--> Int2

    3 --> 4
    3 <--> Int3

    4 --> 5

    %% Analyze önjavító hurok (05):
    %% FAIL esetén az orchestrátor a legkorábbi érintett fázis (02/03/04) fix-módját
    %% indítja (fixer-subagentek), majd a meglévő 2→3→4→5 forward úton re-deriválás
    %% (02→03→04) → újra-analyze, max X=3-ig.
    5 -. "FAIL → spec-fixer (02 fix-mód)" .-> 2
    5 -. "FAIL → plan-fixer (03 fix-mód)" .-> 3
    5 -. "FAIL → tasks-fixer (04 fix-mód)" .-> 4
    5 <--> Int5(["Felhasználói interjú<br/>(fixer nyitott kérdése → válasz → folytatás)"]):::userInput
    5 -- "max X elérve PASS nélkül → megáll + kérdez" --> StopAnalyze(["Hurok feladva — humán döntés"]):::userInput
    5 -- "PASS" --> 6

    6 --> 7

    %% Validate önjavító hurok (07) — tesztek ÉS kódreview egy hurokban (RV1):
    %% FAIL esetén az orchestrátor (07) az implement-fixer vagy a review-fixer
    %% subagentet (06 fix-mód) indítja → újra-validálás, amíg PASS — három leállási
    %% korláttal; tervezési hiba esetén felfelé eszkalál 03/02-re (VD5).
    7 -. "FAIL (teszt/Sonar/DoD vagy Must Fix)<br/>→ implement-fixer / review-fixer → re-validate" .-> 6
    7 <--> Int7(["Felhasználói interjú<br/>(3-próba STOP / eszkaláció)"]):::userInput
    7 -- "tervezési hiba → eszkaláció 03/02-re" --> StopValidateEsc(["Tervezési fázis (03/02) felülvizsgálat"]):::userInput
    7 -- "leállási korlát betelt PASS nélkül → megáll + kérdez" --> StopValidate(["Hurok megáll — humán döntés"]):::userInput
    7 -- "PASS" --> 8

    %% Doc-sync (08): terv (doc-sync-planner) → mechanikus végrehajtás → objektív kapu (DS22).
    %% NEM önjavító subagent-hurok; kapu-bukásnál ember-vezérelt javítás (doc-sync-questions.md).
    8 <--> Int8d(["Felhasználói interjú<br/>(kapu-bukás / döntési pont → doc-sync-questions.md)"]):::userInput
    %% A ciklusvég KÉT ÁGA — a `conventions.md` `## Review and merge` szekciója
    %% dönti el, melyik fut (a PR MEGLÉTE, nem az üzemmód).
    8 -- "isolated SDD (no PR)" --> 9
    8 -- "centralized SDD (PR required)" --> 9a

    %% Merge (09): nincs hurok és nincs subagent — a review már a 07-ben lefutott.
    %% Ha a 08 óta változott kód, előbb újra-doc-sync (DS23.2), majd KÉZI megerősítésű merge (RD8).
    9 -. "változott kód a 08 óta → újra-doc-sync (DS23.2)" .-> 8
    9 -. "kódváltozás a hurokban → újra 08-doc-sync" .-> 8
    9 -- "green VP2 → merge (manual confirmation, RD8)" --> End

    %% A központosított ág: a PR triggereli a CI/CD-t, a review és a merge gépi
    %% futtatásban megy. A VP2 a fő branch-re juttatás ELŐTTI kapu (L13-D14).
    9a --> 9b
    9b --> 9c
    9c -. "változott kód → újra 08-doc-sync" .-> 8
    9c -- "optional" --> 9d
    9c --> End
    9d --> End
```

## 4.2 Tesztelési pontok — hol tesztelünk, és mit bizonyít

A `bs` SDD-ben **három helyen tesztelünk, három különböző okból**. A három pont nem redundancia: mindegyik **mást** bizonyít, és a harmadikat a másik kettő nem tudja kiváltani.

1. **`validate` (07)** — az ágens által készített implementációt validáljuk **a spec ellenében**, a fejlesztő **lokális gépén**. Tipikusan unit és lokálisan futó komponens tesztek.
2. **post-merge teszt (`VP2`)** — a **fő branch-csel egyesítés után**. Hogy hol fut, az attól függ, milyen SDD-t használunk: lehet a **CI/CD folyamat része** és a **lokális gépen** is. CI/CD esetén unit tesztek, **Sonar**, és **konténerizált, mockolt** komponens tesztek. **A Sonar itt is kell — ugyanúgy, ahogy a `validate`-ben van:** az egyesítés olyan kódot hoz be, amit a `07` Sonar-köre sosem látott, és a statikus hibák ugyanúgy keletkezhetnek belőle, mint a futásidejűek. Ez nulla új gépezet: ugyanaz a `sonar-gate.py`, ugyanazokkal a `conventions.md` küszöbökkel.
3. **dev-teszt (`VP3`)** — egy **automatikus deploy után**, egy **valódi teszt rendszerben**, e2e tesztek. Csak központosított úton értelmes (`/bs-dev-test`).

**És mindhármat vissza kell csatornázni** — ez az ábra negyedik eleme, nem lábjegyzet: a riport a **ciklus útvonalára** kerül (`test-report/<fázis>/`, commitolva), megy az **értesítés**, és a bukás vagy a fejlesztőhöz megy vissza, vagy — ha be van kapcsolva — a CI **javító hurkába**.

```mermaid
flowchart LR
    classDef dev fill:#e0f2fe,stroke:#16a34a,stroke-width:2px,color:#1e293b;
    classDef review fill:#f3e8ff,stroke:#8b5cf6,stroke-width:2px,color:#1e293b;
    classDef fb fill:#ffedd5,stroke:#ea580c,stroke-width:2px,color:#7c2d12;

    VP1["<b>1. validate (07)</b><br/>local dev machine<br/>unit + local component tests<br/><i>proves: the implementation matches the spec</i>"]:::dev
    VP2["<b>2. post-merge test</b><br/>local machine OR CI/CD — depends on the SDD mode<br/>unit + <b>Sonar</b> (as in validate) + containerized, mocked component tests<br/><i>proves: it still works merged with master</i>"]:::dev
    VP3["<b>3. dev-test</b> — optional<br/>real test system, after an automatic deploy<br/>real E2E tests<br/><i>proves: it works in a real integrated environment</i>"]:::review
    FB(["<b>back-channel</b><br/>report into the cycle folder + branch · notification · fix loop"]):::fb

    VP1 --> VP2 --> VP3
    VP1 -. "FAIL" .-> FB
    VP2 -. "FAIL" .-> FB
    VP3 -. "FAIL" .-> FB
```

> **A ciklus akkor kész, ha az UTOLSÓ engedélyezett verifikáció zöld.** Melyik az utolsó, azt a `conventions.md` `## Review and merge` szekciója mondja meg (`Post-merge tests`, `Dev deployment test`). Addig a roadmap ciklus-sora `⏳ verifikációra vár` jelölést visel, és a generált `cycle-status.md` is ezt mutatja.

> *A korábbi, teljes részletes folyamatábra saját oldalon él tovább: [A részletes folyamatábra](process-diagram.md).*

## 4.7 Példa prompt-folyam (egy ciklus végigvezetése)

Egy konkrét ciklus, `cycle-02-oidc-login` végigvitele a promptok sorrendjében. A `00`/`01` **egyszeri** setup, a `02`–`09` **ciklusonként** ismétlődik. Minden fázist a saját indító promptjával, **új chat sessionban** indíts; a `<cycle-name>` és egyéb helyőrzőket cseréld ki. Az alábbi blokkban a `→` sorok a fázisban zajló interakciót (interjú, jóváhagyás, hurok) jelölik.

```
# ①  00 — Projekt inicializálás  (csak üres projektnél, egyszer)
Futtasd a parancsot: `/bs-init-project input: OIDC-alapú bejelentkezés a mobil-bank frontendhez`
   → az ágens végigkérdezi a konvenciókat (tech stack, teszt, merge stratégia) → conventions.md

# ②  01 — Ciklusok kezelése
Futtasd a parancsot: `/bs-add-cycles input: Új ciklus — OIDC login a mobil-bank frontendhez`
   → névjavaslat: cycle-02-oidc-login → "ok" → specs/roadmap.md (Kész) + ciklusmappa

# ③  02 — Spec írás
Futtasd a parancsot: `/bs-write-spec input: @specs/roadmap.md`
   → spec-questions.md kérdések egyenként → válaszok → "a spec kész, mehet" → spec.md (Tervezésre kész)

# ④  03a — Kód-terv írás
Futtasd a parancsot: `/bs-write-code-plan input: @specs/cycle-02-oidc-login/spec.md`
   → kötelező első kérdés: E2E teszt stratégia → válaszok → "jóváhagyom" → plan.md (Teszt-tervezésre kész)

# ⑤  /clear, majd 03b — Teszt-terv írás (ugyanabba a plan.md-be)
Futtasd a parancsot: `/bs-write-test-plan input: @specs/cycle-02-oidc-login/plan.md`
   → a fázis MAGA futtatja a kód-terv kapuját (D5) → TS-NN forgatókönyvek → "jóváhagyom" → plan.md (Task írásra kész)

# ⑥  04 — Tasks írás
Futtasd a parancsot: `/bs-write-tasks input: @specs/cycle-02-oidc-login/plan.md`
   → "mehet" → tasks.md (Implementálásra kész)

# ⑦  05 — Analyze
Futtasd a parancsot: `/bs-analyze input: @specs/cycle-02-oidc-login`
   → kereszt-fázisos ellenőrzés; a talált tételekből TE választod ki (triázs), mit javítson → önjavító hurok az analyze-task.md-n → analyze-report.md (PASS)

# ⑧  06 — Implementálás
Futtasd a parancsot: `/bs-implement input: @specs/cycle-02-oidc-login/tasks.md`
   → kód + tasks.md haladás → tasks.md (Validálásra kész)

# (bármikor az 05 után, nem számozott lépés) — kézi tesztterv
# Futtasd a parancsot: `/bs-manual-test-plan input: @specs/cycle-02-oidc-login`
#    → manual-test-plan.md (Tervezett vagy As-built módban) — nem fázis, nem változtat státuszt

# ⑨  07 — Validálás
Futtasd a parancsot: `/bs-validate input: @specs/cycle-02-oidc-login`
   → gyors tesztek → Sonar + kódreview (reviewer subagent) → nehéz tesztek + DoD;
     FAIL esetén önjavító hurok → PASS → spec/plan/tasks státusz: Kész

# ⑩  08 — Doc-sync
Futtasd a parancsot: `/bs-doc-sync input: @specs/cycle-02-oidc-login`
   → docs-generated/ frissítése + objektív kapu → konzisztens dokumentáció

# ⑪  09 — Review and merge  (PR nélküli út; PR esetén: /bs-create-pr → /bs-review → /bs-merge)
Futtasd a parancsot: `/bs-review-and-merge input: @specs/cycle-02-oidc-login`
   → kapuk (státusz + tiszta review + doc-sync) → main behozása → VP2 kör (tesztek + Sonar)
   → merge (kézi megerősítéssel) → roadmap-lezárás + cycle-status.md
```

A következő ciklus (`cycle-03-...`) ismét a `02`-vel indul — a `00`/`01` nem ismétlődik.
