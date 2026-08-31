---
name: bs-manual-test-plan
description: "berkispec - segédparancs. Kézi tesztterv összeállítása a ciklushoz: komponens-indítás, tesztadatok, kézi hívási szekvenciák (curl + .http), elvárt eredmények, és az automata tesztek eredményének helye. Előfeltétel: az analyze-report.md PASS. Nem fázis: a 00-09 folyamatnak nem része, bármikor hívható az analyze után, és bármikor újrafuttatható."
prerequisites:
  - "specs/cycle-NN-<cycle-name>/analyze/analyze-report.md <field:f_status>: PASS"
output:
  - "specs/cycle-NN-<cycle-name>/manual-test-plan.md — kézi tesztterv (<status:mtp_planned> vagy <status:mtp_as_built> módban)"
scripts:
  - "scripts/manual-test-gate-check.py — determinisztikus minőségi kapu"
shared:
  - "shared/phase-commit.md"
---
# Kézi tesztterv (`bs-manual-test-plan`) — segédparancs
<!-- INCLUDE:lang/output-language.md#output-language -->
<!-- INCLUDE:shared/context-check.md -->

---

Ez **nem fázis:** a `00–09` láncnak nem része, a ciklus státusz-láncához (`spec.md` / `plan.md` / `tasks.md`) **nem nyúl**, és bármikor újrafuttatható. Egyetlen dolgot állít elő: a `specs/cycle-NN-<cycle-name>/manual-test-plan.md`-t, amelyben egy **ember** végig tud menni a ciklus funkcionalitásán kézzel — elindítja a komponenseket, lefuttatja a hívási szekvenciákat, összeveti a kapottat az elvárttal, és tudja, hol keresse az automata tesztek eredményeit.

**Nem felderítesz, hanem összeszerelsz.** A tartalom ~90%-a már létező adat a ciklus dokumentumaiban — a te dolgod kigyűjteni, csonkítás nélkül átemelni és emberi végrehajtási sorrendbe rendezni.

---

## Cheat sheet

| Szekció | Egy mondatban |
|---|---|
| Előfeltétel (MT1) | `analyze-report.md` = `PASS`. Enélkül **STOP** és vissza az `05`-re — a `plan.md` <sec:environment_coords> kitöltöttségét az `05` mechanikus kapuja garantálja, és ez a fázis egyetlen valódi bemenete. |
| Két mód (MT3) | A `tasks.md` státuszából dől el: `<status:mtp_planned>` (még nincs kész kód) vagy `<status:mtp_as_built>` (validálás után). A felhasználó felülbírálhatja. |
| Lefedettség (MT6) | Minden tesztcsoport visszavezet egy `DoD-NN`-re vagy egy spec-tesztesetre, és minden `DoD-NN`-hez tartozik csoport **vagy** MT10-indoklás. **Új követelményt nem találsz ki.** |
| Kimenet (MT4) | **Kizárólag** a `manual-test-plan.md`. Nincs eredményfájl, nincs végrehajtás-napló, a `07` és a `09` nem kapuz rá. |
| Újrafuttatás (MT7) | Kérdés nélkül összefésül: a kézi tartalom megmarad, a generált szekciók frissülnek, a változás a <sec:mt_changelog>-ba kerül. |
| Kapu (MT5) | `manual-test-gate-check.py` — determinisztikus. `exit 0` → commit; `exit 1` → javítás (max 2 kör); `exit 2` → STOP. |
| Commit (MT9) | `cycle-NN: manual-test-plan`. **Hurok alatt path-scoped `git add`** — csak a `manual-test-plan.md`. |

---

## Mit állít elő — és miből

| Amit a kézi tesztterv igényel | Meglévő forrás |
|---|---|
| komponens indítása, port, health endpoint | `plan.md` → <sec:environment_coords> / <sec:components_endpoints> (KO1) |
| REST hívási szekvenciák, `curl` | `plan.md` → <sec:rest_calls_examples> |
| tesztadatok, userek, jelszavak | `plan.md` → <sec:test_api_users> + <sec:other_parameters> (TC5 titok-szabály) |
| hálózati előfeltételek | `plan.md` → <sec:network_access_prereqs> |
| **a tesztcsoportok maguk: lépések, hívások, elvárt eredmény** | **`plan.md` → <sec:plan_test_scenarios> (`TS-NN`) — ez a `TG-NN` csoportok elsődleges forrása** |
| mit tesztelünk egy csoporttal | `spec.md` → <sec:test_specification> + <sec:definition_of_done> (`DoD-NN`) |
| automata teszt-parancsok | `plan.md` → <sec:machine_run_table> |
| hova kerülnek az eredmények | `conventions.md` → `## <sec:cv_test_reporting>` (TR3 + a TR5 kör-mappa jelölő) |

---

## <field:f_prerequisite>

0. **Ciklus-beazonosítás:** ha a felhasználó megadott ciklust/fájlt, azt használd; különben a legfrissebb `specs/cycle-*` mappát ajánld fel megerősítésre — <!-- INCLUDE:lang/common.md#ciklus-beazonositas --> — és várj a válaszra, mielőtt továbblépsz.

1. **`conventions.md` létezés-ellenőrzés:** olvasd be a projekt gyökerében a `conventions.md`-t. Ha nem létezik, **STOP** — jelezd a felhasználónak, hogy térjenek vissza a `00` projekt inicializálás fázishoz, és ne folytasd.

2. **🔴 Analyze-kapu (MT1):** olvasd be a `specs/cycle-NN-<cycle-name>/analyze/analyze-report.md` fejlécének `<field:f_status>` mezőjét. _(Ha a fájl ott nincs meg, nézd meg a ciklus gyökerében lévő régi helyen is — `specs/cycle-NN-<cycle-name>/analyze-report.md`.)_ **Ha a fájl nem létezik, vagy a státusza nem `PASS`, STOP:**

   <!-- INCLUDE:lang/manual-test-plan.md#analyze-kapu-stop -->

   **Ne kezdj el tervet írni**, és ne próbáld a hiányzó koordinátákat kitalálni: `PASS` nélkül a <sec:environment_coords> kitöltöttsége nem garantált, a terv pedig pontosan attól használható, hogy konkrét értékekkel áll.

3. **Munkafa-ellenőrzés (csak VCS esetén):** futtasd: `git status --short`. Ha a `tasks.md` státusza `[analyze-loop]` vagy `[validate-loop]` markert visel, **ne ajánld fel commitra a ciklus mappáját** — jelezd egy sorban, hogy hurok fut, és a fázis-záró commit ezért path-scoped lesz (MT9). Egyébként a commitálatlan tételeket elég egy sorban jelezni: ez a parancs csak egy új fájlt ír, a meglévő munkát nem érinti. (No-VCS projektben a lépés kimarad.)

---

## Módválasztás (MT3)

A módot a `tasks.md` státusza dönti el:

| `tasks.md` státusz | Mód |
|---|---|
| `<status:ready_for_implement>` (vagy a fájl hiányzik, vagy `[analyze-loop]` markert visel) | `<status:mtp_planned>` |
| `<status:ready_for_validate>` vagy `<status:done>` (`[validate-loop]` markerrel is) | `<status:mtp_as_built>` |

A választott módot **egy sorban írd ki a felhasználónak**, indoklással, mielőtt dolgozni kezdesz:

<!-- INCLUDE:lang/manual-test-plan.md#mod-bejelentes -->

A felhasználó felülbírálhatja (`mód: tervezett` / `mód: as-built` inputtal) — ilyenkor az ő választása érvényes, és ezt is írd ki egy sorban.

---

## Bemenet-beolvasás (minimális kontextus)

**Csak** ezeket a szekciókat olvasd be, ne a teljes fájlokat:

- **`plan.md`:** <sec:environment_coords> (és alszekciói: <sec:components_endpoints>, <sec:rest_calls_examples>, <sec:test_api_users>, <sec:other_parameters>, <sec:network_access_prereqs>), <sec:testing_strategy>, <sec:machine_run_table>;
- **`spec.md`:** <sec:definition_of_done> (a `DoD-NN` azonosítókkal), <sec:test_specification>;
- **`conventions.md`:** `## <sec:cv_test_reporting>` (a TR5 `<field:f_artifact_path_base>` jelölővel együtt), `## <sec:cv_git_conventions>` (a No-VCS ág eldöntéséhez).

> **🔴 Csonkítás-mentes átemelés (KX2/KX3 analógia).** A <sec:environment_coords>-ból átvett `curl`-példák, payloadok, userek, jelszavak és parancsok **szó szerint, teljes értékkel** kerülnek át. **TILOS** zanzásítani, placeholderre cserélni (`<TOKEN>`, `...`), vagy „lásd a plan-t" hivatkozásra cserélni: a `manual-test-plan.md`-t egy **ember** olvassa, aki a `plan.md`-t nem nyitja meg. Az útvonalakra az RP1 konvenció érvényes — abszolút, gép-specifikus és `file://` alak a dokumentumban **TILOS**.

---

## As-built ellenőrzés — csak `<status:mtp_as_built>` módban

Minden átvett koordinátára (route, port, env-változó, konfig-kulcs) **keresd meg a valós forrást a kódban** (route-definíciók, konfigfájlok, compose/manifest). Eltérésnél:

- **a kód nyer** — a tervbe a valós érték kerül;
- az eltérés bekerül a <sec:mt_changelog>-ba `plan.md <sec:environment_coords>: <régi> → kód: <új>` alakban;
- a válaszodban **egy sorban jelezd** a felhasználónak, hogy a `plan.md` koordinátái elavultak — ez a `08-doc-sync` promóciójának is jelzés.

`<status:mtp_planned>` módban ez a lépés **kimarad**: ne olvass kódot és ne találgass, a fejléc-figyelmeztetés mondja ki, hogy a lépések valós kódon nem verifikáltak:

<!-- INCLUDE:lang/manual-test-plan.md#mod-tervezett-figyelmeztetes -->

---

## A dokumentum váza (MT11)

Elöl a közös kontextus (indítás, tesztadatok, automata tesztek), utána tesztcsoportonként egy **önhordó** blokk. Ezt a vázat kövesd:

<!-- INCLUDE:lang/manual-test-plan.md#dokumentum-sablon -->

**Kötött formai szabályok** (ezekre épül a kapu):

- a tesztcsoport-fejléc formája `### TG-NN — <név>  (DoD-NN[, DoD-NN...])`;
- a `TG-NN` azonosítók a fájlon belül **egyediek** és hézagmentesen sorszámozottak;
- felületi tesztnél a „Hívás / művelet" cella a **pontos URL**-t és a kattintási lépést tartalmazza; REST-nél `curl`-t, és a csoportnak van legalább egy `http` infostringes kódblokkja is (a VSCode REST Client / IntelliJ `.http` alak);
- minden lépés-sor `<field:f_expected_result>` cellája **konkrét** (státuszkód, mezőnév, képernyő-elem) — a „működik" és a „hibátlanul lefut" nem elfogadható;
- ami erre a ciklusra nem értelmezhető, oda `—` kerül; **üres cellát nem hagyhatsz**.

---

## Tesztcsoportok képzése (MT6 + MT10)

1. Minden csoport **egy koherens viselkedést** igazol, és a fejlécében felsorolja a lefedett `DoD-NN`-eket.
2. A csoport tartalma a `spec.md` <sec:test_specification> eseteiből és a `plan.md` <sec:rest_calls_examples> szekvenciáiból áll össze — **új követelményt nem találsz ki**, exploratív csoportot nem adsz hozzá.
3. Minden csoportnak van **tesztadata** (a 2. szekcióra hivatkozva vagy helyben) és **takarítása** (`<field:f_cleanup>`).
4. **Nem kézzel tesztelhető `DoD-NN` (MT10):** ami kézzel nem ellenőrizhető (belső refaktor, lint-szabály, coverage-küszöb, CI-konfiguráció), az a <sec:mt_not_manual> táblába kerül: `DoD-NN` + **egy mondat indoklás** + hogy melyik automata teszt vagy kapu fedi. Ne találj ki helyette értelmetlen kézi lépést.
5. A <sec:mt_coverage> tábla a `DoD-NN → TG-NN` párokat sorolja, és **egyeznie kell** a csoport-fejlécekkel.

---

## Automata tesztek és a teszteredmények helye

- A <sec:mt_automated_tests> tábla sorai a `plan.md` <sec:machine_run_table> sorai — a **parancs szó szerint** kerül át.
- Az eredmény helyét a `conventions.md` `## <sec:cv_test_reporting>` táblájából és a TR5 `<field:f_artifact_path_base>` jelölőjéből oldd fel.
- **`<field:f_test_results_so_far>`:**
  - `<status:mtp_planned>` módban a **leendő** útvonalak, `_(még nem létezik)_` jelöléssel;
  - `<status:mtp_as_built>` módban a **ténylegesen létező** fájlok (`test-report/implement/check-log.md`, és ha volt már validálás, `test-report/validate/round-NN/...`). **Csak azt sorold fel, ami tényleg ott van** — a kapu ezt ellenőrzi.

---

## Újrafuttatás — néma merge javítás-naplóval (MT7)

Ha a `manual-test-plan.md` már létezik, **kérdés nélkül** dolgozz, és jelezd egy sorban:

<!-- INCLUDE:lang/manual-test-plan.md#ujrafutas-bejelentes -->

- a generált szekciókat (1–5.) frissítsd;
- a bennük lévő **kézi kiegészítéseket** (olyan sor vagy bekezdés, ami a bemenetekre nem vezethető vissza) **tartsd meg**;
- a `TG-NN` azonosítókat **ne számozd újra** — a meglévők megmaradnak, az újak a sor végére kerülnek;
- írj egy <sec:mt_changelog> bejegyzést: dátum, mód, mit adtál hozzá / módosítottál / mi avult el és miért.

---

## Minőségellenőrzési lista (a kapu előtt)

- [ ] A fejléc `<field:f_status>` mezője a két megengedett érték egyike, és a `<field:f_mode>` mező indokolja.
- [ ] Mind a hat kötelező szekció megvan, és az 1–4. szekcióban **nincs placeholder és nincs üres tábla-cella**.
- [ ] Minden komponens-sorban van konkrét indító parancs.
- [ ] Minden `TG-NN` csoportnak van `<field:f_what_we_test>`, `<field:f_prerequisite>`, lépés-táblája és `<field:f_cleanup>`-ja, és minden lépésnek konkrét elvárt eredménye.
- [ ] Minden `DoD-NN` lefedett: csoport-fejlécben **vagy** a <sec:mt_not_manual> táblában, indoklással.
- [ ] Ahol `curl` van, ott `http` kódblokk is van.
- [ ] Nincs abszolút, gép-specifikus vagy `file://` útvonal (RP1).

---

## A determinisztikus kapu (`manual-test-gate-check.py`)

A prompt-szintű lista után a kapu futtatása **kötelező** — a fenti pontok gépiesen eldönthető részét ez méri, hamis riasztás nélkül:

<!-- INCLUDE:shared/python-cmd.md -->

```bash
python3 <platform-scripts-mappa>/manual-test-gate-check.py specs/cycle-NN-<cycle-name>
```

**Kilépő kód:**

- **`0`** → tiszta, mehet a commit.
- **`1`** → van `✗` sor: javítsd a kiírt pontokat, és futtasd újra. **Legfeljebb 2 javító próbálkozás**, utána **STOP**: írd ki a kapu kimenetét és kérdezz.
- **`2`** → használati vagy előfeltétel-hiba (nem létező ciklusmappa, hiányzó `manual-test-plan.md`, érvénytelen fejléc-státusz) → **STOP**, a pótlandó sorral. Ezt magadtól ne kerüld meg.

---

## Megállási szabályok

1. **Nincs `PASS` analyze-riport** (Előfeltétel 2.) → STOP, a `/bs-analyze` paranccsal.
2. A `plan.md` <sec:environment_coords> szekciójában **placeholder vagy üres cella** van, amit a kódból sem lehet feloldani → **STOP**, és jelezd, hogy a `03`-hoz kell visszamenni. (Az `05` kapuja ezt elvileg kizárja — ha mégis előfordul, az jelzésértékű.)
3. Egy `DoD-NN`-hez **sem kézi lépés, sem MT10-indoklás** nem képezhető → **kérdezz** (egy kérdés egyszerre, és várd meg a választ).
4. A kapu **kétszeri javítás után is bukik** → STOP, a kapu kimenetével.
5. A commit-ellenőrzés **kétszer bukik** (lásd a *Fázis-záró commit* blokk 4. lépését) → STOP.

---

## Fázis-záró commit (MT9)

A `<FÁZIS-TAG>` értéke: **`manual-test-plan`** — a commit üzenete tehát `cycle-NN: manual-test-plan`.

> **⛔ Hurok-őr — kötelező eltérés a közös blokktól.** Ha a `tasks.md` `[analyze-loop]` vagy `[validate-loop]` markert visel, a 3. lépés `git add`-je **kizárólag** ez lehet:
>
> ```bash
> git add specs/cycle-NN-<cycle-name>/manual-test-plan.md
> ```
>
> **SOHA** ne stage-eld a ciklus mappáját és **soha** ne használj `-A`-t: a `07-validate` VD8 szabálya szerint a hurok alatt **nincs** köztes commit — a `test-report/`, a `DoD-NN` pipák és a javító-taskok szándékosan commitálatlanul állnak, és a `07` megszakadás-kezelése ebből ismeri fel, hogy megszakadt hurkot folytat. Egy naiv `git add specs/cycle-NN-<cycle-name>/` **elrántaná a lábát a `07` alól**. Ilyenkor a 4. lépés `git status --short` ellenőrzése is csak erre az egy fájlra vonatkozik.

> **A közös blokk 2. lépése (státuszírás) itt a `manual-test-plan.md` SAJÁT `<field:f_status>` mezőjét jelenti** (`<status:mtp_planned>` / `<status:mtp_as_built>`) — **nem** a `spec.md` / `plan.md` / `tasks.md` státuszát. A ciklus státusz-láncához ez a parancs nem nyúl.

<!-- INCLUDE:shared/phase-commit.md -->

---

## Záró visszajelzés

A közös blokk PE1 szakasza (fázishatár + következő fázis parancsa) itt **nem értelmezett**: ez nem fázis, nincs „következő fázis". A parancs a záró üzenettel véget ér:

<!-- INCLUDE:lang/manual-test-plan.md#zaro-uzenet -->

---

## Amit NE tegyél

- **Ne írj eredményfájlt** (`manual-test-results.md`) és ne vezess pipálható végrehajtás-naplót (MT4) — a talált hibák sorsa a felhasználóé.
- **Ne nyúlj a ciklus státusz-láncához** és a `07` / `08` / `09` artefaktumaihoz.
- **Ne találj ki új követelményt** és ne adj hozzá exploratív tesztcsoportot (MT6).
- **Ne zanzásítsd** a plan-ből átvett `curl`-öket, payloadokat és parancsokat.
- **Ne írd bele a titkokat**: klaszter-, registry-, VPN-, IAM- és éles credential csak pointerként szerepel (TC5).
- **Ne kérdezz** újrafuttatáskor arról, hogy frissítsd-e a fájlt (MT7) — kérdés nélkül fésülj.
