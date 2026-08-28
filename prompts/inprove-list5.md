# `bs-manual-test-plan` — végrehajtási terv

> **Ez a dokumentum önhordó.** Üres kontextusban is végrehajtható: az 1. szakasz megadja az
> orientációt, a 2. a lezárt döntéseket, a 3–9. a pipálható teendőket, a 10. az elfogadási
> kritériumokat, a 11. a végrehajtási sorrendet.
> **Semmit nem kell kikövetkeztetni** — ha valami mégis hiányzik, az a terv hibája; írd bele.

---

## 0. Hogyan használd ezt a dokumentumot

1. **Olvasd el az 1–2. szakaszt** (orientáció + lezárt döntések). Enélkül a teendők félreérthetők.
2. **A 11. sorrend szerint haladj**, és keresd meg az első kipipálatlan teendőt.
3. **Egy teendő = egy lépés = egy verifikáció.** Minden pont után futtasd a hozzá tartozó
   ellenőrzést, és pipálj ebben a fájlban (`- [ ]` → `- [x]`).
4. **Ha döntést kell hozni, ami nincs a 2. szakaszban:** ne döntsd el csendben — írd be a
   2.9 nyitott listába, kérdezd meg a felhasználót, majd rögzítsd `MT<n>`-ként.
5. **⛔ A repó kétnyelvű.** Minden prompt-változtatás **mindkét fán** (`-hu` és `-en`)
   átvezetendő. Commit előtt kötelező:
   ```bash
   python3 prompts/scripts/lang-parity-check.py
   python3 prompts/scripts/sync-gemini-agents.py --check
   ```
6. **Minden parancs a repó gyökeréből fut** (`berkispec/`), nem a `prompts/` mappából.
7. **⛔ Amihez nem nyúlsz:** a `jegyzet.md` a felhasználó privát munkaterülete (verziókövetve
   van, de **nem a tiéd**) — ne olvasd, ne szerkeszd, és **soha ne commitold**. Emiatt a
   commit-lépésben (11./9.) **tilos a `git add -A`**; csak a felsorolt útvonalakat stage-eld.

### 0.1 Hol tart most a munka (állapot-szonda)

Futtasd le legelőször — ebből látod, mi van már kész, és hol kell felvenned a fonalat.
**Ne feltételezz, ellenőrizz:**

```bash
ls prompts/skills-hu/manual-test-plan.md prompts/skills-en/manual-test-plan.md \
   prompts/lang/hu/manual-test-plan.md prompts/lang/en/manual-test-plan.md \
   prompts/scripts/manual-test-gate-check.py 2>&1 | sed 's/^/  /'
python3 -c "
import json
k=json.load(open('prompts/lang/status-keys.json'))
print('  status-keys mt_* :', [x for x in k['hu']['sections'] if x.startswith('mt_')] or 'NINCS')
print('  status-keys mtp_*:', [x for x in k['hu']['status'] if x.startswith('mtp_')] or 'NINCS')
d=json.load(open('prompts/lang/hu/descriptions.json'))
print('  descriptions.json:', 'megvan' if 'bs-manual-test-plan' in d else 'NINCS')"
grep -c 'manual-test-plan' README.md prompts/meta-improve-prompts.md prompts/scripts/cycle-status.py
```

A terv írásakor (kiinduló állapot) **mind a öt fájl hiányzik, mindhárom kulcs-csoport
`NINCS`, és a `grep -c` mindhárom fájlra `0`** — ha nem ezt látod, valaki már elkezdte:
a 11. sorrend szerint keresd meg az első hiányzó darabot.

---

## 1. Orientáció

### 1.1 Mit vezetünk be

Egy új, **számozatlan segédparancsot**: `/bs-manual-test-plan`. Előállítja a
`specs/cycle-NN-<name>/manual-test-plan.md` fájlt, amelyben egy ember végig tud menni a
ciklus funkcionalitásán kézzel: elindítja a komponenseket, lefuttatja a hívási
szekvenciákat (REST: `curl` + VSCode `.http`; felület: URL + kattintási lépések),
összeveti a kapottat az elvárttal, és tudja, hol vannak az automata tesztek eredményei.

### 1.2 Miért olcsó ez a fázis

A kért tartalom **90%-ban már létező adat** a keretrendszerben — a skill nem felderít,
hanem **összeszerel**:

| Amit a kézi tesztterv igényel | Meglévő forrás |
|---|---|
| komponens indítása, port, health endpoint | `plan.md` → `<sec:environment_coords>` / `<sec:components_endpoints>` (KO1) |
| REST hívási szekvenciák, `curl` | `plan.md` → `<sec:rest_calls_examples>` (ige + teljes URL + fejlécek + konkrét body + elvárt válasz + kinyerendő mező, token-beszerzéssel) |
| tesztadatok, userek, jelszavak | `plan.md` → `<sec:test_api_users>` + `<sec:other_parameters>` (TC5 titok-szabály) |
| hálózati előfeltételek | `plan.md` → `<sec:network_access_prereqs>` |
| mit tesztelünk egy csoporttal | `spec.md` → `<sec:test_specification>` + `<sec:definition_of_done>` (`DoD-NN`) |
| automata teszt-parancsok | `plan.md` → `<sec:machine_run_table>` (TP4 — ezt olvassa a `run-tests.py`) |
| hova kerülnek az eredmények | `conventions.md` → `## <sec:cv_test_reporting>` (TR3 + TR5 kör-mappa jelölő) |

Mellékhatásként **őszinteség-teszt a KO1-re**: ami a plan-ből hiányzik vagy elavult, az itt
azonnal kiderül — ma ez csak a `test-runner`-nek fájna, ami gyakran nem is fut.

### 1.3 Mit NEM vezetünk be

- **Nem** új számozott fázis: a `00–09` lánc, a státusz-lánc és a `prev`/`next` gráf
  **érintetlen** marad.
- **Nem** visszacsatolás: nincs `manual-test-results.md`, a `07-validate` és a `09-merge`
  gépezetéhez **nem nyúlunk**.
- **Nem** subagent: nincs új ágens, nincs új `gemini-agent/*/agent.json` tükör.
- **Nem** doc-sync / export-doc integráció.

### 1.4 A repó releváns mechanizmusai (amit tudni kell hozzá)

- **A telepítő glob-alapú** — `install-helper.py`:
  - skillek: `skills_src.glob("*.md")` → a célmappa `bs-<fájlnév-stem>/SKILL.md`
    (`write_markdown_skill`, ~738. sor). Tehát a fájl neve **`manual-test-plan.md`** kell
    legyen, hogy `/bs-manual-test-plan` legyen belőle. **Az `install-helper.py`-t nem kell
    módosítani.**
  - scriptek: `copy_helper_scripts()` a `prompts/scripts/*.py` mindegyikét másolja, kivéve
    a három repó-karbantartó eszközt. **Az új gate-scriptet sem kell regisztrálni.**
- **A nyelvi tengelyek**: a szekciónevek / mezőnevek / státuszok a promptban `<sec:…>`,
  `<field:…>`, `<status:…>` tokenek, amiket a telepítő old fel a
  `prompts/lang/status-keys.json`-ból. **Új szekciónév → előbb kulcs a JSON mindkét
  szeletébe, csak utána token.** A user-facing mondatok és az artefaktum-sablon a
  `prompts/lang/<L>/<fájl>.md` horgonyaiban élnek,
  `<!-- INCLUDE:lang/<fájl>.md#<horgony> -->` markerrel behivatkozva.
- **A kapu-scriptek nyelvfüggetlenek**: a `lang_keys.py` (`sec()`, `fld()`, `st()`) a
  telepített `lang-keys.json`-ból olvas.
- **Számozatlan skill minta**: `brainstorm.md`, `cycle-status.md`, `export-doc.md`,
  `quick-flow.md` — `name`/`description` alapú frontmatter, nincs `phase`/`prev`/`next`.

### 1.5 Kötelező előolvasás (tiszta kontextusban)

Ez a terv **nem** helyettesíti a keretrendszer megértését. Mielőtt az első teendőhöz
nyúlnál, olvasd el:

1. **`prompts/meta-improve-prompts.md`** — a teljes rendszer leírása: a `00–09` flow, a
   kétnyelvű fastruktúra, a tervezési elvek (fáziskapu, minimális kontextus, egy kérdés
   egyszerre, scope-fegyelem, megállási szabályok, `RP1` útvonal-konvenció, `GC1`
   kapu-konfiguráció).
2. **Egy meglévő számozatlan skill mintaként** — `prompts/skills-hu/export-doc.md` (rövid,
   script-hívós) és `prompts/skills-hu/cycle-status.md`.
3. **Egy meglévő kapu-script mintaként** — `prompts/scripts/ds22-gate-check.py` vagy
   `prompts/scripts/report-gate-check.py` (a `lang_keys` használatára és a kimenet-formára).
4. **`prompts/shared-hu/phase-commit.md`** — a commit-blokk, amit a skill beemel (MT9).

### 1.6 A négy csendes buktató

Ezek olyan mechanizmusok, amelyek **hallgatólagosan** buktatják a bevezetést, ha nem
tudsz róluk. Mindegyikhez tartozik teendő a tervben:

| # | Mechanizmus | Következmény, ha kihagyod | Teendő |
|---|---|---|---|
| 1 | A frontmatter `description` mezője **build-time kicserélődik** a `prompts/lang/<PROJECT_LANG>/descriptions.json` `name`-hez tartozó értékére (`substitute_lang_frontmatter`, LG15/LG26) | **`sys.exit(1)`**: „a 'bs-manual-test-plan' nincs a projekt-nyelvi descriptions.json-ban" → a telepítés megáll | **3.3** |
| 2 | A `lang-parity-check.py` **11.4** checkje megköveteli, hogy a `descriptions.json` kulcskészlete **pontosan** a fa `name` mezőinek halmaza legyen, **mindkét nyelven** | `FAIL` a paritás-kapun | **3.3** |
| 3 | A **11.3/b** check: **minden horgonyt hivatkoznia kell** legalább egy `INCLUDE` markernek („árva horgony" = `FAIL`); és a nyelvi blokk maga **nem tartalmazhat** `INCLUDE` markert (8.5) | `FAIL` a paritás-kapun | **5.4** |
| 4 | A script-hívások elé a keretrendszer a `<!-- INCLUDE:shared/python-cmd.md -->` blokkot teszi (Windows `python` / `py -3` fallback), az útvonalban pedig a `<platform-scripts-mappa>` helyőrző áll (BD15), amit a telepítő old fel | Windowson elhasal a kapu-hívás, vagy rossz útvonalra mutat | **4.10** |

---

## 2. Lezárt döntések

- [x] **MT1 — Jelleg és kapu.** Számozatlan, bármikor hívható segédparancs (nem a `00–09`
  lánc része). **Előfeltétel:** `analyze-report.md` státusza `PASS`. Előtte a skill
  **elutasít** és visszairányít a `05`-re (`/bs-analyze input: @specs/cycle-NN-<name>`).
  Indok: az `05` mechanikus kapuja garantálja, hogy a `plan.md` KO1 szekciója placeholder
  nélkül, kitöltve áll — ez a terv egyetlen valódi bemenete.

- [x] **MT2 — Ciklus-beazonosítás.** A többi skill mintájára: ha a felhasználó megadott
  ciklust/fájlt, azt használja; különben a legfrissebb `specs/cycle-*` mappát ajánlja fel
  megerősítésre, és **vár a válaszra**.

- [x] **MT3 — Kétmódú működés, automatikus módválasztás.** A skill a `tasks.md` státuszából
  dönt:
  - **`Tervezett` mód** (`tasks.md` = `<status:ready_for_implement>`, azaz még nincs kész
    kód): kizárólag a `plan.md` KO1 + `spec.md` teszt-szekció/DoD + `conventions.md`
    alapján szerel össze. A fejléc kimondja, hogy a lépések **valós kódon nem
    verifikáltak**. A teszteredmény-szekció a **leendő** útvonalakat sorolja, explicit
    „még nem létezik" jelöléssel.
  - **`As-built` mód** (`tasks.md` = `<status:ready_for_validate>` vagy `<status:done>`):
    a valós route-okat, portokat, konfigokat **ellenőrzi a kódban**; eltérésnél **a kód
    nyer**, és az eltérés bekerül a `## Változásnapló`-ba. A teszteredmény-szekció a
    ténylegesen létező fájlokat listázza.

- [x] **MT4 — Nulla visszacsatolás.** A skill kizárólag a `manual-test-plan.md`-t állítja
  elő. Nincs eredményfájl, nincs pipálható végrehajtás-napló, a `07` és a `09` nem kapuz rá,
  a talált hibák sorsa a felhasználóra van bízva.

- [x] **MT5 — Fő ágens + determinisztikus kapu.** A skillt a fő ágens hajtja végre (nincs
  subagent), és egy új `prompts/scripts/manual-test-gate-check.py` zárja. Indok: kvóta-barát,
  és a gyenge modell hibamódjait (placeholder, hiányzó tesztadat, lefedetlen DoD) csak
  determinisztikusan lehet elkapni.

- [x] **MT6 — Lefedettségi szabály: csak a ciklus, DoD-hez kötve.** Minden tesztcsoport
  visszavezet egy `DoD-NN`-re vagy egy spec-tesztesetre, és minden `DoD-NN`-hez tartozik
  legalább egy csoport. **A fázis új követelményt nem talál ki**, exploratív csoportot nem
  ad hozzá. (A nem kézzel tesztelhető DoD-pontok kezelését lásd MT10.)

- [x] **MT7 — Újrafuttatás: néma merge, javítás-naplóval.** Kérdés nélkül összefésül: a
  **kézi (nem generált) tartalmat megőrzi**, a generált szekciókat frissíti, és a fájl végi
  `## Változásnapló` szekcióba ír egy bejegyzést arról, mit és miért változtatott.

- [x] **MT8 — Integráció: csak a `cycle-status.py`.** A `08-doc-sync`, az `export-doc`, a
  `07-validate` és a `09-merge` **érintetlen**. A `cycle-status.py` kimenetében megjelenik,
  hogy van-e már kézi tesztterv, és melyik módban.

- [x] **MT9 — Commit: `shared/phase-commit.md` szerint**, `<FÁZIS-TAG>` = `manual-test-plan`,
  azaz `git commit -m "cycle-NN: manual-test-plan"`.
  **Hurok-őr (kötelező eltérés a közös blokktól):** ha a `tasks.md` `[analyze-loop]` vagy
  `[validate-loop]` markert visel, a skill **kizárólag a `manual-test-plan.md` útvonalát**
  stage-eli (`git add specs/cycle-NN-<name>/manual-test-plan.md`), **soha nem** a ciklus
  mappáját és soha nem `-A`-t. Indok: a `07-validate` VD8 szabálya szerint a hurok alatt
  **nincs** köztes commit — a `test-report/`, a DoD-pipák és a javító-taskok szándékosan
  commitálatlanul állnak, és a `07` megszakadás-kezelése (a fáziseleji munkafa-ellenőrzés
  2. pontja) ebből ismeri fel, hogy megszakadt hurkot folytat. Egy naiv `git add
  specs/cycle-NN-<name>/` **elrántaná a lábát a `07` alól**.

- [x] **MT10 — Nem kézzel tesztelhető DoD.** Van olyan `DoD-NN`, amit kézzel nem lehet
  ellenőrizni (belső refaktor, lint-szabály, coverage-küszöb, CI-konfiguráció). Ezekre a
  dokumentum végén egy `### Nem kézzel tesztelhető` allista szolgál: `DoD-NN` + **egy
  mondat indoklás** + hogy melyik automata teszt/kapu fedi. A kapu a `DoD-NN`-t akkor
  tekinti lefedettnek, ha **vagy** szerepel egy tesztcsoport fejlécében, **vagy** itt
  szerepel indoklással. Enélkül az MT6 teljesíthetetlen lenne, és az ágens vagy hazudna,
  vagy kitalálna egy értelmetlen kézi lépést.

- [x] **MT11 — Dokumentum-váz: csoport-központú.** Elöl a közös kontextus (indítás,
  tesztadatok, automata tesztek), utána tesztcsoportonként egy **önhordó** blokk. Minden
  REST lépésnél **`curl` ÉS `.http` blokk is** kötelező. A pontos vázat a 3.2 rögzíti.

- [x] **MT12 — Nyelvi kezelés.** A skill mindkét prompt-nyelvi fára elkészül
  (`skills-hu/` + `skills-en/`), a dokumentum-sablon és a user-facing mondatok a
  `prompts/lang/hu/manual-test-plan.md` + `prompts/lang/en/manual-test-plan.md`
  horgonyaiba kerülnek, a szekciónevek és státuszok a `status-keys.json` **mindkét**
  szeletébe.

- [x] **MT13 — A kapu közös kódja: MÁSOLÁS, nem refaktor.** Az `MG3` (placeholder + üres
  cella) és az `MG8` (RP1) logikája megegyezik az `analyze-gate-check.py` `C6` és `R1`
  checkjeivel. A `manual-test-gate-check.py` a mintákat **átmásolja**, forrás-hivatkozó
  kommenttel — **nem** emeljük ki közös modulba. Indok: (a) a fájlnévben lévő kötőjel miatt
  az `analyze-gate-check.py` normál `import`-tal nem érhető el; (b) egy új `gate_common.py`
  bevezetése az `analyze-gate-check.py` (1200+ sor, az `05` kapuja) átírását jelentené,
  ami ehhez a feladathoz képest aránytalan regressziós kockázat. A pontos átveendő
  elemeket a 6.3 sorolja fel. *(Ha később egy harmadik kapunak is kellene, akkor érdemes
  kiemelni — akkor viszont külön, dedikált ciklusban.)*

- [x] **MT14 — A `cycle-status.py` bővítése NEM a `phases` listába megy.** A kézi tesztterv
  külön helper + külön kiírt sor; az `analyze_cycle()` visszatérési értéke és a `phases`
  lista **változatlan**. Indok: mérve, nem feltételezve — lásd 7.1.

- [x] **MT15 — Egy negyedik mezőkulcs (`f_test_results_so_far`) a 3.1.3-hoz.** A 3.2 sablon
  „A ciklus eddigi teszteredményei:" sora **nem maradhat literál**, mert az `MG7` as-built
  ága ezt a sort horgonyként keresi — a 6.4 nyelvfüggetlenségi szabály tehát kulcsot kíván.
  Felvéve a `status-keys.json` mindkét szeletébe; a sablon és mindkét skill a tokent
  használja. *(Végrehajtás közben hozott, mechanikus következmény-döntés — nem szűkíti és
  nem bővíti a hatókört.)*

- [x] **MT16 — Az `MG3` helyőrző-mintája szélesebb, mint a `KO1_PLACEHOLDER_RE`.** A 6.3
  szerint a `KO1_PLACEHOLDER_RE`-t szó szerint átvettük (a nyelvfüggő ággal és a
  forrás-hivatkozó kommenttel együtt), de az önmagában **nem fogja meg** a 6.2-ben
  felsorolt eseteket: a `<a csoport neve>` alakú helyőrzőt és a `...` / `…` cellát.
  Ezért az `MG3` két további, **nyelvsemleges** mintát is futtat
  (`ANGLE_PLACEHOLDER_RE`, `WORD_PLACEHOLDER_RE`, `ELLIPSIS_CELL_RE`). Az `ANGLE_…`
  szándékosan **csak** akkor jelez, ha a `<...>` tartalma szóközt tartalmaz, vagy csupa
  nagybetűs/aláhúzásos — így egy XML-payload `<user>` tagje nem bukik meg. A `...`/`…`
  csak **táblacellában** hiba, prózában nem (magyar szövegben legitim).

### 2.9 Nyitott döntések

*(Jelenleg nincs. Ha munka közben felmerül, ide írd, kérdezd meg, majd rögzítsd `MT<n>`-ként
a 2. szakaszban.)*

---

## 3. A dokumentum és a nyelvi kulcsok

### 3.1 Új kulcsok a `prompts/lang/status-keys.json`-ba

- [x] **3.1.1 — `sections` csoport, `hu` és `en` szelet egyaránt:**

  | kulcs | `hu` | `en` |
  |---|---|---|
  | `mt_environment` | Környezet és indítás | Environment and startup |
  | `mt_test_data` | Tesztadatok | Test data |
  | `mt_automated_tests` | Automata tesztek | Automated tests |
  | `mt_manual_groups` | Kézi tesztcsoportok | Manual test groups |
  | `mt_not_manual` | Nem kézzel tesztelhető | Not manually testable |
  | `mt_coverage` | Lefedettség | Coverage |
  | `mt_changelog` | Változásnapló | Change log |

- [x] **3.1.2 — `status` csoport, `hu` és `en` szelet egyaránt:**

  | kulcs | `hu` | `en` |
  |---|---|---|
  | `mtp_planned` | Tervezett | Planned |
  | `mtp_as_built` | As-built | As-built |

- [x] **3.1.3 — `fields` csoport (csak ami hiányzik):**

  | kulcs | `hu` | `en` |
  |---|---|---|
  | `f_what_we_test` | Mit tesztelünk | What we test |
  | `f_shutdown` | Leállítás | Shutdown |
  | `f_cleanup` | Takarítás | Cleanup |

  **Már létezik, ezeket használd újra, ne duplikáld:** `f_status`, `f_mode`, `f_goal`,
  `f_prerequisite`, `f_steps`, `f_expected_result`, `f_startup`, `f_example_call`,
  `f_result`, `f_reason`, `f_evidence`, `f_last_updated`.

  **Végrehajtás közben felvett negyedik kulcs (MT15):**

  | kulcs | `hu` | `en` |
  |---|---|---|
  | `f_test_results_so_far` | A ciklus eddigi teszteredményei | Test results of the cycle so far |

  Indok: a 3.2 sablonban ez a sor eredetileg **literál** volt, az `MG7` viszont as-built
  módban ezt a sort keresi meg, hogy alatta ellenőrizze az útvonalak létezését — literállal
  ez a 6.4 („semmilyen magyar/angol literál a scriptben") megsértése lett volna. A sablon
  és mindkét skill a tokent használja.

- [x] **3.1.4 — Verifikáció:**
  ```bash
  python3 -c "
  import json; d=json.load(open('prompts/lang/status-keys.json'))
  for g in ('sections','status','fields'):
      assert set(d['hu'][g]) == set(d['en'][g]), (g, set(d['hu'][g]) ^ set(d['en'][g]))
  print('kulcs-paritás OK')"
  ```

### 3.2 A `manual-test-plan.md` váza (jóváhagyott)

A sablon a `prompts/lang/<L>/manual-test-plan.md` `#dokumentum-sablon` horgonyába kerül; a
skill `<!-- INCLUDE:lang/manual-test-plan.md#dokumentum-sablon -->` markerrel hivatkozza be.

> **A sablon négy backtickes kerítésben áll**, mert maga is tartalmaz ```` ``` ```` blokkot
> (a `.http` példa). A nyelvi fájlba **a kerítés nélküli belső tartalom** kerül.

````markdown
# Kézi tesztterv — cycle-NN-<cycle-name>

**<field:f_status>:** <status:mtp_planned> | <status:mtp_as_built>
**<field:f_mode>:** <a módválasztás indoka egy sorban — pl. „tasks.md = Validálásra kész">
**Forrás:** plan.md <sec:environment_coords> · spec.md <sec:definition_of_done> · conventions.md
**Utolsó frissítés:** ÉÉÉÉ-HH-NN

> (csak <status:mtp_planned> módban) ⚠ Az implementáció még nem zárult le. A lépések a
> tervből származnak, valós kódon NEM verifikáltak — eltérés esetén a kód a mérvadó.

## 1. <sec:mt_environment>

| Komponens | Port | Health endpoint | <field:f_startup> | <field:f_shutdown> |
|---|---|---|---|---|
| … | … | … | `…` | `…` |

**<field:f_prerequisite>:** hálózati/hozzáférési előfeltételek, sorrend.

## 2. <sec:mt_test_data>

| Név | Érték | Hol keletkezik | <field:f_cleanup> |
|---|---|---|---|
| … | … | … | … |

(teszt-userek jelszóval, tokenek és beszerzésük, seed rekordok, azonosítók, scope-ok —
TC5 titok-szabály: dev-hatókörű érték konkrétan, klaszter/registry/VPN/IAM/éles
credential csak pointerként)

## 3. <sec:mt_automated_tests>

| Mit futtat | Parancs | Az eredmény helye |
|---|---|---|
| … | `…` | `…` |

**A ciklus eddigi teszteredményei:** <konkrét útvonalak, vagy „még nem létezik">

## 4. <sec:mt_manual_groups>

### TG-01 — <a csoport neve>  (DoD-03, DoD-07)

**<field:f_what_we_test>:** <egy-két mondat: milyen viselkedést igazol ez a csoport>
**<field:f_prerequisite>:** <mi álljon készen a csoport előtt>

| # | <field:f_steps> | Hívás / művelet | <field:f_expected_result> |
|---|---|---|---|
| 1 | token beszerzése | `curl -s -X POST …` | 200, a válasz `access_token` mezője nem üres |
| 2 | … | … | … |

```http
POST http://localhost:8080/api/…
Content-Type: application/json

{ … }
```

**<field:f_cleanup>:** <mit kell visszaállítani a csoport után>

### TG-02 — …

### <sec:mt_not_manual>

| DoD-NN | Miért nem tesztelhető kézzel | Mi fedi |
|---|---|---|
| DoD-05 | … | `…` automata teszt / Sonar kapu |

## 5. <sec:mt_coverage>

| DoD-NN | Tesztcsoport |
|---|---|
| DoD-03 | TG-01 |

## <sec:mt_changelog>

- **ÉÉÉÉ-HH-NN — <mód>:** <mit adott hozzá / mit módosított / mi avult el és miért>
````

**Kötött formai szabályok** (ezekre épül a kapu):
- a tesztcsoport-fejléc formája `### TG-NN — <név>  (DoD-NN[, DoD-NN…])`;
- a `TG-NN` azonosítók a fájlon belül **egyediek** és hézagmentesen sorszámozottak;
- felületi tesztnél a „Hívás / művelet" cella a **pontos URL**-t és a kattintási lépést
  tartalmazza, REST-nél `curl`-t, és a csoportnak van legalább egy ```` ```http ````
  blokkja is;
- útvonal-konvenció: RP1 (`prompts/shared-<lang>/path-format.md`) — abszolút, gép-specifikus
  és `file://` alak tilos.

### 3.3 A skill leírója — `prompts/lang/{hu,en}/descriptions.json` (KÖTELEZŐ)

> **Enélkül a telepítés `sys.exit(1)`-gyel megáll, és a paritás-kapu 11.4 checkje FAIL.**
> A `.md` frontmatterébe írt `description` csak **forrás/placeholder**: a telepítő
> build-time **kicseréli** a `descriptions.json` `name`-hez tartozó értékére, mert a
> leíró a **projekt** nyelvét követi (a felhasználó azon a nyelven kéri a skillt), nem a
> prompt-nyelvet.

- [x] **3.3.1 — Új kulcs `prompts/lang/hu/descriptions.json`-ba:**
  `"bs-manual-test-plan"` → a magyar leíró. Formája a többiét kövesse
  (`"berkispec - segédparancs. …"`), és tartalmazza: mit állít elő, mi az előfeltétele
  (analyze PASS), hogy nem fázis, és hogy bármikor újrafuttatható.

- [x] **3.3.2 — Ugyanaz a kulcs `prompts/lang/en/descriptions.json`-ba**, angol szöveggel.
  A **kulcs nem fordul** (`bs-manual-test-plan` mindkét fájlban azonos), csak az érték.

- [x] **3.3.3 — Verifikáció:**
  ```bash
  python3 -c "
  import json
  hu=json.load(open('prompts/lang/hu/descriptions.json'))
  en=json.load(open('prompts/lang/en/descriptions.json'))
  assert set(hu)==set(en), set(hu)^set(en)
  assert 'bs-manual-test-plan' in hu
  print('leíró-paritás OK')"
  ```

---

## 4. Az új skill — `prompts/skills-hu/manual-test-plan.md` + `-en/`

- [x] **4.1 — Fájl + frontmatter.** A számozatlan segédparancs-minta szerint
  (`cycle-status.md` / `export-doc.md`), `phase`/`prev`/`next` **nélkül**:
  ```yaml
  ---
  name: bs-manual-test-plan
  description: "berkispec - segédparancs. Kézi tesztterv összeállítása a ciklushoz …
    Előfeltétel: az analyze-report.md PASS. Nem fázis: a 00-09 folyamatnak nem része,
    bármikor hívható az analyze után, és bármikor újrafuttatható."
    # ⚠ ez az érték build-time KICSERÉLŐDIK a descriptions.json-ból (1.6/1., 3.3)
  prerequisites:
    - "specs/cycle-NN-<name>/analyze/analyze-report.md státusz: PASS"
  output:
    - "specs/cycle-NN-<name>/manual-test-plan.md — kézi tesztterv (Tervezett vagy As-built módban)"
  scripts:
    - "scripts/manual-test-gate-check.py — determinisztikus minőségi kapu"
  shared:
    - "shared/phase-commit.md"
  ---
  ```
  A fájlnév **kötött**: `manual-test-plan.md` → a telepítő ebből képzi a
  `bs-manual-test-plan` skill-mappát (1.4).

- [x] **4.2 — Fejléc-blokkok.** `<!-- INCLUDE:lang/output-language.md#output-language -->`
  és `<!-- INCLUDE:shared/context-check.md -->`, majd egy bekezdés: *ez nem fázis, nem
  változtatja a ciklus státuszát, bármikor újrafuttatható.*

- [x] **4.3 — Előfeltétel-szakasz (`## <field:f_prerequisite>`).**
  0. **Ciklus-beazonosítás** (MT2) — a többi skill szó szerinti mintájával, beleértve a
     `<!-- INCLUDE:lang/common.md#ciklus-beazonositas -->` markert.
  1. **`conventions.md` létezés-ellenőrzés** — ha nincs, STOP → `00`.
  2. **Analyze-kapu (MT1)** — `specs/cycle-NN-<name>/analyze/analyze-report.md` (fallback a
     ciklus-gyökérben lévő régi helyre, ahogy a `cycle-status.py` teszi). Ha nem létezik
     vagy a fejléc státusza nem `PASS` → **STOP**, egyértelmű mondattal + a
     `/bs-analyze input: @specs/cycle-NN-<cycle-name>` paranccsal. **Ne kezdj el tervet
     írni** — a KO1 kitöltöttsége ilyenkor nem garantált.
  3. **Munkafa-ellenőrzés** (csak VCS esetén) — `git status --short`. Ha a `tasks.md`
     `[analyze-loop]` vagy `[validate-loop]` markert visel, **ne ajánld fel commitra** a
     ciklus mappáját (MT9), csak jelezd egy sorban, hogy hurok fut, és a commit
     path-scoped lesz.

- [x] **4.4 — Módválasztás (MT3).** A `tasks.md` státuszából, egyetlen táblával a promptban:

  | `tasks.md` státusz | Mód |
  |---|---|
  | `<status:ready_for_implement>` (vagy hiányzik / `[analyze-loop]`) | `<status:mtp_planned>` |
  | `<status:ready_for_validate>` vagy `<status:done>` | `<status:mtp_as_built>` |

  A választott módot **írd ki a felhasználónak egy sorban**, indoklással, mielőtt dolgozni
  kezdesz. A felhasználó felülbírálhatja (`mód: tervezett` / `mód: as-built` inputtal).

- [x] **4.5 — Bemenet-beolvasás (minimális kontextus, 2. tervezési elv).** **Csak** ezek a
  szekciók olvasandók, nem a teljes fájlok:
  - `plan.md`: `<sec:environment_coords>` (és alszekciói: `<sec:components_endpoints>`,
    `<sec:rest_calls_examples>`, `<sec:test_api_users>`, `<sec:other_parameters>`,
    `<sec:network_access_prereqs>`), `<sec:testing_strategy>`, `<sec:machine_run_table>`;
  - `spec.md`: `<sec:definition_of_done>` (a `DoD-NN` azonosítókkal),
    `<sec:test_specification>`;
  - `conventions.md`: `## <sec:cv_test_reporting>` (a TR5 `<field:f_artifact_path_base>`
    jelölővel együtt), `## <sec:cv_git_conventions>` (No-VCS ág).

  > **🔴 Csonkítás-mentes átemelés (KX2/KX3 analógia).** A KO1-ből átvett `curl`-példák,
  > payloadok, userek és parancsok **szó szerint, teljes értékkel** kerülnek át. Tilos
  > zanzásítani, placeholderre cserélni (`<TOKEN>`, `…`), vagy „lásd a plan-t" hivatkozásra
  > cserélni: a `manual-test-plan.md`-t egy ember olvassa, aki a plant nem nyitja meg.

- [x] **4.6 — As-built ellenőrzés (csak `<status:mtp_as_built>` módban).** Minden átvett
  koordinátára (route, port, env-változó, konfig-kulcs) **keresd meg a valós forrást** a
  kódban (route-definíciók, konfigfájlok, compose/manifest). Eltérésnél:
  - **a kód nyer** — a tervbe a valós érték kerül;
  - az eltérés bekerül a `<sec:mt_changelog>`-ba: `plan.md KO1: <régi> → kód: <új>`;
  - a válaszodban **egy sorban jelezd** a felhasználónak, hogy a plan KO1-je elavult (ez a
    `08-doc-sync` promóciójának is jelzés).

  `<status:mtp_planned>` módban ez a lépés **kimarad** — ne találgass és ne olvass kódot.

- [x] **4.7 — Tesztcsoportok képzése (MT6 + MT10).**
  - Minden csoport **egy koherens viselkedést** igazol, és a fejlécében felsorolja a
    lefedett `DoD-NN`-eket.
  - A csoport tartalma a spec `<sec:test_specification>` eseteiből és a plan
    `<sec:rest_calls_examples>` szekvenciáiból áll össze — **új követelményt nem találsz ki**.
  - Minden lépésnek van **konkrét elvárt eredménye** (státuszkód, mező, képernyő-elem) —
    „működik", „hibátlanul lefut" nem elfogadható.
  - Minden csoportnak van **tesztadata** (2. szekcióra hivatkozva vagy helyben) és
    **takarítása**.
  - Ami kézzel nem tesztelhető → `<sec:mt_not_manual>` tábla, indoklással (MT10).

- [x] **4.8 — Automata tesztek szekció.** A `<sec:machine_run_table>` sorait vidd át
  (parancs szó szerint), az eredmény helyét a `conventions.md` `<sec:cv_test_reporting>`
  táblájából + a TR5 útvonal-alap jelölőből oldd fel. Az „eddigi teszteredmények":
  - `<status:mtp_planned>` módban a **leendő** útvonalak, `_(még nem létezik)_` jelöléssel;
  - `<status:mtp_as_built>` módban a **ténylegesen létező** fájlok listája
    (`test-report/implement/check-log.md`, és ha volt már validálás,
    `test-report/validate/round-NN/…`). Csak azt sorold fel, ami tényleg ott van.

- [x] **4.9 — Merge-logika újrafutásnál (MT7).** Ha a fájl létezik:
  - **kérdés nélkül** dolgozz;
  - a generált szekciókat (1–5.) frissítsd, a bennük lévő **kézi kiegészítéseket** (olyan
    sor/bekezdés, ami nem vezethető vissza a bemenetekre) **tartsd meg**;
  - a `TG-NN` azonosítókat **ne számozd újra** — a meglévők megmaradnak, az újak a sor
    végére kerülnek;
  - írj egy `<sec:mt_changelog>` bejegyzést: dátum, mód, mit adtál hozzá / módosítottál /
    mi avult el és miért.

- [x] **4.10 — Minőségellenőrzési lista + a kapu futtatása.** A prompt-szintű lista után
  **kötelező** a script. A hívás **pontos formája** (a `07-validate` mintája szerint):
  a parancs elé `<!-- INCLUDE:shared/python-cmd.md -->` (Windows `python` / `py -3`
  fallback), az útvonalban pedig a `<platform-scripts-mappa>` **helyőrző** (BD15), amit a
  telepítő old fel a platform tényleges scripts-mappájára — **ne írj konkrét útvonalat**:
  ```bash
  python3 <platform-scripts-mappa>/manual-test-gate-check.py specs/cycle-NN-<cycle-name>
  ```
  - `exit 0` → mehet a commit;
  - `exit 1` → javítsd a kiírt ✗ pontokat, és futtasd újra. **Legfeljebb 2 javító
    próbálkozás**, utána STOP: írd ki a kapu kimenetét és kérdezz.
  - `exit 2` → használati/előfeltétel-hiba (nincs `conventions.md` jelölő, hiányzó fájl) —
    STOP, a pótlandó sorral.

- [x] **4.11 — Megállási szabályok (explicit felsorolás a promptban).**
  1. Nincs `PASS` analyze-riport (4.3/2.);
  2. a `plan.md` KO1-jében **placeholder vagy üres cella** van, amit a kódból sem lehet
     feloldani → STOP, jelezd, hogy a `03`-hoz kell visszamenni (a `05` kapuja ezt
     elvileg kizárja — ha mégis előfordul, az jelzésértékű);
  3. egy `DoD-NN`-hez sem kézi lépés, sem MT10-indoklás nem képezhető → **kérdezz**
     (egy kérdés egyszerre, 3. tervezési elv);
  4. a kapu kétszeri javítás után is bukik (4.10);
  5. a commit-ellenőrzés kétszer bukik (`shared/phase-commit.md` 4. lépése).

- [x] **4.12 — Fázis-záró commit (MT9).** A `<FÁZIS-TAG>` = `manual-test-plan` deklarálása
  után `<!-- INCLUDE:shared/phase-commit.md -->`, **és közvetlenül a marker előtt** a
  hurok-őr kimondása:

  > **Hurok-őr:** ha a `tasks.md` `[analyze-loop]` vagy `[validate-loop]` markert visel, a
  > 3. lépés `git add`-je **kizárólag** `specs/cycle-NN-<cycle-name>/manual-test-plan.md`
  > lehet — a ciklus mappájának teljes stage-elése a futó hurok commitálatlan állapotát
  > (VD8) rántaná be a commitba, amiből a `07` a megszakadás-folytatást ismeri fel.
  > Ilyenkor a 4. lépés `git status --short` ellenőrzése is csak erre a fájlra vonatkozik.

  Megjegyzés: a `phase-commit.md` blokk **státuszírásról** is beszél (2. lépés) — itt ez a
  `manual-test-plan.md` saját `<field:f_status>` mezője (`<status:mtp_planned>` /
  `<status:mtp_as_built>`), **nem** a `spec.md`/`plan.md`/`tasks.md` státusza. Ezt a
  skillben mondd ki, hogy az ágens ne nyúljon a ciklus státusz-láncához.

- [x] **4.13 — Záró visszajelzés.** A válasz végén: a mód, a tesztcsoportok száma, a
  lefedett `DoD-NN`-ek, a commit azonosítója, és a `manual-test-plan.md` **kattintható
  linkje**. A `phase-commit.md` PE1 szakasza itt nem értelmezett (nincs „következő fázis") —
  a skill a link kiírásával véget ér.

- [x] **4.14 — Az angol pár (`prompts/skills-en/manual-test-plan.md`).** Szerkezetileg
  azonos: ugyanazok a címsorok, kódblokkok, INCLUDE-markerek, `MT<n>` szabály-ID-k, nyelvi
  tokenek és imperatívusz-darabszám. A paritás-kapu ezeket méri. **Amit konkrétan egyeztetni
  kell:**
  - a frontmatter lista-mezőinek (`prerequisites`, `output`, `shared`, …) **elemszáma**
    egyezzen (11.4 — a behúzott `- ` sorokat számolja, a tartalmat nem);
  - a `<sec:…>` / `<field:…>` / `<status:…>` tokenek **halmaza** egyezzen (11.12);
  - a nyelvfüggetlen tokenek (`/bs-…` parancsok, `[analyze-loop]`/`[validate-loop]`
    markerek, `*.md`/`*.py` útvonalak) **halmaza** egyezzen (11.13);
  - a „kemény padló" jelölések (`TILOS` ↔ `FORBIDDEN`/`NEVER`, `🔴`, `⛔`) **darabszáma**
    egyezzen (11.10).

---

## 5. A nyelvi blokkok — `prompts/lang/{hu,en}/manual-test-plan.md`

> **🔴 Két kemény szabály, amit a 11.3 kapu számon kér:**
> 1. **Nincs árva horgony.** Minden horgonyt **hivatkoznia kell** legalább egy
>    `<!-- INCLUDE:lang/manual-test-plan.md#<horgony> -->` markernek valamelyik prompt-fában.
>    Ha egy horgonyt megírsz, de a skillből nem hivatkozol rá → `FAIL`. Tehát: **csak annyi
>    horgonyt írj, amennyit a skill tényleg behivatkoz** — az 5.1 tábla ezért a skill 4.
>    szakaszának lépéseihez van kötve.
> 2. **A nyelvi blokk maga nem tartalmazhat `INCLUDE` markert** (8.5) — a `lang/<L>/*.md`
>    fájlokban csak horgonyok és tartalom lehet, beágyazott include nem.
>
> **A horgony pontos szintaxisa** (saját sorban, semmi más a sorban, **szóköz nélkül** a
> kettőspont után — a repó minden horgonya így néz ki, 75 db):
> `<!-- ANCHOR:dokumentum-sablon -->`
> - a horgonynév **nem fordul** — mindkét nyelvi fájlban azonos;
> - névkonvenció: `<szabály-ID>-<rövid-név>` ott, ahol van hozzá szabály-ID
>   (`DS10-doc-sync-plan-vaz`, `TC12-promocio-kerdes`), egyébként sima leíró név
>   (`zaro-uzenet`, `statusz-megerosites`);
> - **a blokk a következő `ANCHOR` sorig (vagy a fájl végéig) tart** — az `ANCHOR` sorok
>   maguk nem részei a beemelt szövegnek (8.9). Nincs záró marker;
> - **hivatkozott, de nem létező horgony → a telepítő `sys.exit(1)`** (a hiányzó *fájl*
>   ezzel szemben csendben átmegy — ezért a horgonynevet elgépelni drágább, mint hinnéd).

- [x] **5.1 — Horgonyok.** Pontosan ezek (mindegyiket hivatkozza a skill):

  | horgony | tartalom |
  |---|---|
  | `dokumentum-sablon` | a 3.2 váz teljes egészében |
  | `mod-tervezett-figyelmeztetes` | a `Tervezett` mód fejléc-figyelmeztetése |
  | `analyze-kapu-stop` | a STOP-üzenet szövege + a `/bs-analyze` parancs |
  | `mod-bejelentes` | „A ciklus … módban készül, mert …" |
  | `ujrafutas-bejelentes` | „Létező tesztterv frissítése — a kézi tartalom megmarad." |
  | `zaro-uzenet` | a 4.13 záró visszajelzés sablonja |

- [x] **5.2 — Az angol pár** ugyanezekkel a horgonynevekkel (a horgonynév **nem fordul**).

- [x] **5.3 — Verifikáció:**
  ```bash
  diff <(grep -o '<!-- *ANCHOR:[^>]*-->' prompts/lang/hu/manual-test-plan.md) \
       <(grep -o '<!-- *ANCHOR:[^>]*-->' prompts/lang/en/manual-test-plan.md) \
    && echo "horgony-paritás OK"
  ```

- [x] **5.4 — Árva-horgony ellenőrzés** (a 11.3/b kapu előfutára — futtasd, mielőtt a
  paritás-kaput hívnád):
  ```bash
  comm -23 \
    <(grep -o '<!-- *ANCHOR:[^>]*-->' prompts/lang/hu/manual-test-plan.md \
      | sed 's/.*ANCHOR: *//; s/ *-->//' | sort -u) \
    <(grep -rho 'INCLUDE:lang/manual-test-plan.md#[^ ]*' prompts/skills-hu prompts/skills-en \
      | sed 's/.*#//; s/ *-->$//' | sort -u)
  ```
  **Üres kimenet a helyes** — minden nem-hivatkozott horgony itt jelenik meg.

---

## 6. A kapu — `prompts/scripts/manual-test-gate-check.py`

Mintaként a `ds22-gate-check.py` és a `report-gate-check.py` szolgál (kisebbek, mint az
`analyze-gate-check.py`, és ugyanezt a szerkezetet követik).

- [x] **6.1 — Váz.** `#!/usr/bin/env python3`, `from lang_keys import fld, st, sec`,
  argparse: `cycle_path` pozicionális; opcionális `--mode {planned,as-built}` (default: a
  fájl `<field:f_status>` mezőjéből). Kimenet: fejléc + `✓`/`✗`/`·` sorok, a `✗` sorok
  mellett az ID (`MG<n>`) és a **pótlandó konkrétum**. Kilépő kód: `0` = tiszta,
  `1` = legalább egy `✗`, `2` = használati/előfeltétel-hiba.

- [x] **6.2 — Ellenőrzések.**

  | ID | Mit ellenőriz | Bukás esetén |
  |---|---|---|
  | `MG1` | a fájl létezik; a `<field:f_status>` értéke `<status:mtp_planned>` vagy `<status:mtp_as_built>` | `exit 2` — pótlandó fejléc-sor |
  | `MG2` | mind a 6 kötelező szekció megvan (`mt_environment`, `mt_test_data`, `mt_automated_tests`, `mt_manual_groups`, `mt_coverage`, `mt_changelog`) | a hiányzók felsorolása |
  | `MG3` | **placeholder- és üres-cella-tilalom** az 1–4. szekcióban (`<…>`, `TODO`, `TBD`, `xxx`, üres tábla-cella). Az `—` explicit „nem értelmezhető", elfogadott | fájl:sor + a talált minta |
  | `MG4` | minden `### TG-NN` csoportnál: van `<field:f_what_we_test>` sor, van `<field:f_prerequisite>` sor, van legalább 1 soros lépés-tábla, és **minden** lépés-sor `<field:f_expected_result>` cellája nem üres | a hiányos csoport ID-ja + mi hiányzik |
  | `MG5` | **kétirányú DoD-lefedettség:** minden `### TG-NN` fejlécében van legalább egy `DoD-NN`; és a `spec.md` `<sec:definition_of_done>` minden `DoD-NN`-je szerepel **vagy** egy csoport fejlécében, **vagy** a `<sec:mt_not_manual>` táblában indoklással | a lefedetlen `DoD-NN`-ek felsorolása |
  | `MG6` | az 1. szekció minden komponens-sorában van **nem üres, nem placeholder** indító parancs | a hiányos komponens neve |
  | `MG7` | a 3. szekció parancsai **halmazként lefedik** a `plan.md` `<sec:machine_run_table>` sorait; `as-built` módban a „ciklus eddigi teszteredményei" alatt felsorolt útvonalak **léteznek a lemezen** | a hiányzó parancs / a nem létező útvonal |
  | `MG8` | **RP1** — nincs abszolút útvonal, gép-specifikus prefix vagy `file://` a dokumentumban | fájl:sor |
  | `MG9` | minden olyan csoportnál, amelynek lépés-táblájában `curl` szerepel, van legalább egy ```` ```http ```` blokk is (és fordítva) | a csoport ID-ja |
  | `MG10` | a `TG-NN` azonosítók egyediek és hézagmentesek; a `<sec:mt_coverage>` tábla `DoD-NN → TG-NN` párjai megegyeznek a csoport-fejlécekkel | az eltérő sorok |

- [x] **6.3 — Kód-újrahasznosítás (MT13: másolás, forrás-hivatkozó kommenttel).**
  Az alábbiakat **szó szerint** vedd át az `analyze-gate-check.py`-ból, mindegyik fölé egy
  `# forrás: analyze-gate-check.py <név> (C6/R1)` kommenttel:

  | Amit átveszel | Sor (a terv írásakor) | Mire kell |
  |---|---|---|
  | `section_body(text, title_substr)` | 564 | szekció-törzs kimetszése (`##`–`####`, a következő azonos/magasabb szintű címsorig) |
  | `TABLE_ROW_RE` · `SEPARATOR_ROW_RE` | 544–545 | tábla-sorok felismerése |
  | `PLACEHOLDER_CELL_RE` | 546 | sablon-/példasor felismerése |
  | `KO1_PLACEHOLDER_RE` | 814 | placeholder az érték helyén (`MG3`) |
  | `FENCE_RE` | 907 | kódblokk-határ (`MG8`) |
  | `FILE_URI_RE` · `MACHINE_PATH_RE` · `PLACEHOLDER_PATH_RE` · `MD_ABS_LINK_RE` · `ABS_REPO_PATH_RE` · `R1_MAX_PER_DOC` | 1032–1038 | `MG8` útvonal-minták |
  | `check_path_format(docs, repo_root, f)` | 1042 | `MG8` teljes logikája — a `docs` egyetlen elemű: `[("manual-test-plan.md", text, "—")]` |

  **🔴 Két szemantikai csapda, amit pontosan úgy kell másolni, ahogy van** — különben a két
  kapu mást mond ugyanarra a szövegre:
  1. **A csupa-placeholder sor NEM hiba.** A `C6` így szűr: ha a sor **minden** cellája
     illeszkedik a `PLACEHOLDER_CELL_RE`-re (`_dőlt_`, `...`, `—`, `-`, `<...>`) **vagy**
     üres, akkor az **sablonsor**, `continue`. Csak az olyan sorban hiba az üres cella,
     amelyikben legalább egy valódi érték is áll. A `—` tehát **legális** „nem
     értelmezhető" jelölés, nem hiányzó adat.
  2. **A fejlécsor átugrása állapotgéppel megy** (`seen_separator`): amíg a `|---|---|`
     elválasztó nem jött, a sorokat nem vizsgáljuk. A `FENCE_RE`-t követő `in_fence`
     kapcsoló ugyanígy állapotgép — az `R1` a `file://`, gép-specifikus és placeholder
     alakot **kódblokkban is** hibázza, az abszolút markdown-linket és az abszolút
     repó-útvonalat viszont **csak kódblokkon kívül**.

  > **⚠ A `KO1_PLACEHOLDER_RE` nyelvfüggő** (magyar kulcsszavakra épül: `ide j`, `kitölt`,
  > `megadni`, `érték`, `url`, `jelszó`, `password`), csak a `TODO|TBD|FIXME|XXX` ága
  > nyelvsemleges. Angol projekt-nyelvnél tehát gyengébben fog. **Ne javítsd itt** — ez az
  > `05` kapujával közös, meglévő adósság, és az egyoldalú „javítás" pont a két kapu
  > eltéréséhez vezetne. Vedd át úgy, ahogy van, és írd a komment mellé:
  > `# nyelvfüggő ág — az analyze-gate-check.py C6-jával közös adósság`.

- [x] **6.4 — Nyelvfüggetlenség.** Semmilyen magyar/angol literál a scriptben — minden
  szekciónév/mezőnév/státusz a `lang_keys` `sec()`/`fld()`/`st()` hívásain keresztül.
  A `✓`/`✗` sorok user-facing szövege a `cycle-status.py` és a `ds22-gate-check.py`
  jelenlegi gyakorlatát követi.

- [x] **6.5 — Verifikáció.** Egy létező, lezárt ciklus mappáján futtatva ne dobjon
  tracebacket; hiányzó `manual-test-plan.md` esetén `exit 2` és értelmes üzenet.

---

## 7. `cycle-status.py` bővítés (MT8)

> **🔴 MIÉRT NEM a `phases` listába (MT14) — mérve, a kódban.** Az `analyze_cycle()` a
> `phases`-ből származtatja a ciklus összesített státuszát (352–355. sor):
> ```python
> all_done   = all(p[1] in ("KÉSZ", INDIRECT) for p in phases)
> any_started= any(p[1] in ("KÉSZ", INDIRECT, "FOLYAMATBAN") for p in phases)
> overall_status = "KÉSZ" if all_done else ("FOLYAMATBAN" if any_started else "MÉG NEM FUTOTT")
> ```
> Ha a listába beteszünk egy `MÉG NEM FUTOTT` sort, **egyetlen ciklus sem lesz soha `KÉSZ`** —
> egy lemergelt, lezárt ciklus is örökre `FOLYAMATBAN` marad. Ez nem kozmetika: a
> `text_fallback_menu()` és a `curses_menu()` az `overall != "KÉSZ"` feltétellel tölti az
> `incomplete_cycles` listát, tehát **minden befejezett ciklus visszakerülne a nyitottak
> közé**, és a „Minden ciklus sikeresen befejeződött! 🎉" ág soha nem futna le.
>
> Ezért: az `analyze_cycle()` **visszatérési értékéhez és a `phases` listához nem nyúlunk**
> (négy hívási helye van: 362, 394, 443, 566). A kézi tesztterv **külön helper + külön
> kiírt sor**.

- [x] **7.1 — Új helper: `get_manual_test_plan_state(cycle_path)`.** A
  `get_status_from_file()` mellé, ugyanazzal a mintával. Visszatérés: egyetlen
  megjelenítendő string.

  | észlelt állapot | visszatérés |
  |---|---|
  | nincs `manual-test-plan.md` | `MÉG NEM FUTOTT` |
  | létezik, `<field:f_status>` = `<status:mtp_planned>` | `TERVEZETT` |
  | létezik, `<field:f_status>` = `<status:mtp_as_built>` | `AS-BUILT` |
  | létezik, státusz nem olvasható | `FOLYAMATBAN` |

  A státusz-összehasonlítás **kisbetűs**, a fájl tetején lévő `_S_*` konstansok mintájára
  (`_MTP_PLANNED = st("mtp_planned").lower()`).

- [x] **7.2 — Megjelenítés két helyen, a `phases` listától függetlenül.**
  - **`print_cycle_phases()`** — a `for phase_name, p_status in phases:` ciklus **után**,
    az `INDIRECT` lábjegyzet **előtt**, egy vizuálisan elkülönített sor, hogy ne tűnjön
    fázisnak:
    ```python
    mtp = get_manual_test_plan_state(cycle_path)
    print(f"  {DIM}· {'Kézi tesztterv (nem fázis)':<35} → {mtp}{RESET}")
    ```
  - **`curses_menu()`** — a jobb oldali panel fázis-ciklusa után egy sor, a **meglévő
    `height - 3` túlcsordulás-őrrel** (a panel `10 + p_idx`-től ír, és `break`-el, ha
    kifutna):
    ```python
    py = 10 + len(sel_phases)
    if py < height - 3:
        stdscr.attron(curses.A_DIM)
        stdscr.addstr(py, rx, f" · {get_manual_test_plan_state(sel_cycle):<12}")
        stdscr.attroff(curses.A_DIM)
        stdscr.addstr(" Kézi tesztterv (nem fázis)")
    ```
  - A `text_fallback_menu()` **egysoros ciklus-listáját ne bővítsd** — ott csak az
    összesített státusz fér el.

- [x] **7.3 — Lightweight flow ág:** oda **ne** kerüljön be (ott nincs `plan.md` és nincs
  analyze — a skill kapuja eleve nem teljesülhet).

- [x] **7.4 — Ismert adósság, ne told tovább:** a `cycle-status.py` fázis-címkéi ma
  **hardcode-olt magyar** literálok (`"Specifikáció (spec.md)"`, `"MÉG NEM FUTOTT"`).
  Az új sort a **jelenlegi mintához igazítsd** (ne vezess be félmegoldást), és ezt a
  szakaszt hivatkozd, ha valaki később egységesíti.

- [x] **7.5 — Verifikáció:** `python3 prompts/scripts/cycle-status.py <egy-ciklus>` fut
  hiba nélkül a fájl megléte nélkül és meglétével is.

---

## 8. Dokumentáció

- [x] **8.1 — `README.md` / 3. Alapvető parancsok** (a `bs-cycle-status` sora mellé):
  egy `* **/bs-manual-test-plan**: …` bekezdés — mit ad, mi az előfeltétele, hogy
  bármikor újrafuttatható.

- [x] **8.2 — `README.md` / 7. Skill-index:** új sor a táblába (a `bs-export-doc` és
  `bs-cycle-status` mintájára), és az alatta lévő mondat kiegészítése — ma azt írja:
  *„a segédparancsok (`bs-brainstorm`, `bs-export-doc`) …"* → vedd fel közé a
  `bs-manual-test-plan`-t.

- [x] **8.3 — `README.md` / 4. Mappastruktúra:** a `manual-test-gate-check.py` sora a
  `prompts/scripts/` felsorolásba, és a `manual-test-plan.md` a ciklus-mappa tartalmához.

- [x] **8.4 — `prompts/meta-improve-prompts.md`:**
  - a „A workflow felépítése" szakaszban, a `bs-brainstorm` bekezdés mintájára egy
    **„A flow UTÁN / mellett (opcionális segédparancs)"** bekezdés a
    `bs-manual-test-plan`-ról (kapu: analyze PASS; kétmódú; nulla visszacsatolás);
  - a prompt-fájl táblába egy sor;
  - a „Tervezési elvek" végére **nem** kell új elv — a skill a meglévőket követi.

- [x] **8.5 — `README.md` / 5.7 példa prompt-folyam:** opcionálisan egy kommentsor a `⑦`
  (06) és `⑧` (07) közé: `# (bármikor az 05 után) /bs-manual-test-plan input: cycleNN`.
  **Ne** számozott lépésként — nem fázis.

---

## 9. Ismert korlátok (tudatosan vállalva)

- [x] **9.1 — A lightweight flow-ban nem használható.** Ott nincs `plan.md` és nincs
  `05-analyze`, tehát az MT1 kapu soha nem teljesül. Ez **elfogadott** — ha később kell,
  külön döntés (`MT<n>`) tárgya, nem ennek a tervnek a hatóköre. A skill STOP-üzenete
  legyen erre is érthető („nincs analyze-riport — ez a parancs a teljes flow-hoz készült").

- [x] **9.2 — `Tervezett` módban a terv elavulhat.** Ha az implementáció eltér, a terv
  hazudik, amíg valaki újra nem futtatja. Ezt a fejléc-figyelmeztetés (3.2) és az
  as-built újrafuttatás kezeli — **kapu nem** (MT4: nulla visszacsatolás).

- [x] **9.3 — Nincs promóció a `test-conventions.md`-be.** A visszatérő indítási és
  smoke-lépések nem kerülnek át a regiszterbe (MT8). Ha a gyakorlat azt mutatja, hogy
  ciklusonként újraírjuk ugyanazt, az a `08-doc-sync` bővítése lesz, külön döntéssel.

---

## 10. Elfogadási kritériumok

- [x] **10.1** — `python3 prompts/scripts/lang-parity-check.py --strict` → `exit 0`
  (a fájlhalmaz-paritás is teljesül: `skills-hu/manual-test-plan.md` ↔
  `skills-en/manual-test-plan.md`, `lang/hu/…` ↔ `lang/en/…`).
- [x] **10.2** — `python3 prompts/scripts/sync-gemini-agents.py --check` → `exit 0`
  (új agent nincs, tehát változatlan; ha mégis panaszkodik, az regresszió).
- [x] **10.3** — `status-keys.json` kulcs-paritás (3.1.4 parancs) → OK.
- [x] **10.3/b** — `descriptions.json` kulcs-paritás + a `bs-manual-test-plan` kulcs megléte
  (3.3.3 parancs) → OK.
- [x] **10.3/c** — Árva-horgony ellenőrzés (5.4 parancs) → üres kimenet.
- [x] **10.4** — Éles telepítés egy próbaprojektbe. *(Lefuttatva nem interaktívan, közvetlenül
  az `install-helper.py`-val — az `install.sh` csak a paraméter-bekérést adja hozzá:
  `claude hu hu`, `claude en en` és `antigravity en hu` kombinációval. Mindhárom `Success`,
  a skill-mappa és a script a helyén, a három `grep` üres. A `prompt EN + projekt HU`
  kombinációban a magyar sablon emelődik be az angol skillbe — helyes.)* És:
  - a `bs-manual-test-plan` skill megjelenik a platform skill-mappájában,
  - a `manual-test-gate-check.py` ott van a scripts mappában,
  - a telepített `SKILL.md`-ben **nincs feloldatlan** `<sec:…>` / `<field:…>` /
    `<status:…>` token és **nincs** maradék `<!-- INCLUDE: … -->` marker:
    ```bash
    grep -n '<\(sec\|field\|status\):' <dest>/.claude/skills/bs-manual-test-plan/SKILL.md
    grep -n 'INCLUDE:' <dest>/.claude/skills/bs-manual-test-plan/SKILL.md
    ```
    (mindkettő üres kell legyen)
- [ ] **10.5** — Éles próba egy valódi ciklusban, **mindkét módban**. ⛔ **NEM FUTTATHATÓ
  ebben a repóban:** itt nincs `specs/` mappa és nincs `PASS` analyze-riportú ciklus — ez
  egy valódi projektben, ágenssel végzendő próba. *(A kapu mindkét módban le van tesztelve
  szintetikus ciklus-mappán: `Tervezett` módban a nem létező eredmény-útvonal nem hiba,
  as-builtben igen; a `--mode` felülbírálás is működik.)*
  - `Tervezett` mód (analyze PASS, implementáció előtt) → a terv elkészül, a kapu zöld,
    a fejléc-figyelmeztetés ott van, a teszteredmény-útvonalak `_(még nem létezik)_`
    jelölést kapnak;
  - `As-built` mód (validálás után) → újrafuttatva a `<sec:mt_changelog>` bejegyzést kap,
    a kézi kiegészítések megmaradnak, a felsorolt eredmény-útvonalak léteznek.
- [ ] **10.6** — ⛔ **NEM FUTTATHATÓ ebben a repóban** (ágens-viselkedés valódi ciklusban) —
  **Hurok-őr próba (MT9):** `[validate-loop]` markeres `tasks.md` mellett
  futtatva a commit **csak** a `manual-test-plan.md`-t tartalmazza:
  ```bash
  git show --stat --name-only HEAD | grep -c . # csak a manual-test-plan.md útvonal
  git status --short specs/cycle-NN-<name>/    # a hurok commitálatlan állapota MEGMARAD
  ```
- [x] **10.7** — `python3 prompts/scripts/cycle-status.py` fut hiba nélkül, és a kézi
  tesztterv sora a várt értéket mutatja **mind a négy** állapotban (`MÉG NEM FUTOTT` /
  `TERVEZETT` / `AS-BUILT` / `FOLYAMATBAN`), a lightweight flow-ban pedig a sor **nem
  jelenik meg** (7.3). *(A `curses_menu()` ága headless környezetben nem futtatható —
  kódszinten a meglévő `height - 3` túlcsordulás-őrrel és `sel_ff` kapuval készült.)*
- [ ] **10.8** — ⛔ **NEM FUTTATHATÓ ebben a repóban** (ágens-viselkedés valódi ciklusban) —
  Negatív próba: **analyze PASS nélkül** hívva a skill **elutasít**, nem ír
  fájlt, és a `/bs-analyze` parancsot adja vissza.

---

## 11. Végrehajtási sorrend

1. **3.1** — kulcsok a `status-keys.json`-ba (mindkét szelet) + 3.1.4 verifikáció.
   *Ez az első, mert minden más ezekre a tokenekre épül.*
2. **5.** — `lang/hu/manual-test-plan.md` + `lang/en/…` horgonyok (benne a 3.2 sablon).
3. **4.** — `skills-hu/manual-test-plan.md`, majd **közvetlenül utána** a `-en` pár (4.14).
   Utána azonnal **3.3** (`descriptions.json` mindkét nyelven) + **5.4** árva-horgony
   ellenőrzés — a skill `name`-je és az INCLUDE-markerei csak ekkor véglegesek.
   *Ne halmozz több skill-szakaszt az angol pár nélkül — a paritás-kapu így fogja meg a
   csúszást a keletkezése helyén.*
4. **6.** — `manual-test-gate-check.py` + 6.5 verifikáció.
5. **7.** — `cycle-status.py` bővítés + 7.5 verifikáció.
6. **8.** — dokumentáció (README + meta-improve-prompts).
7. **10.1–10.4** — kapuk és telepítési próba.
8. **10.5–10.8** — éles próba mindkét módban + negatív és hurok-őr próba.
9. **Commit.** Egyetlen commit a teljes bevezetésről, a repó szokása szerint magyar
   commit-üzenettel (pl. `bs-manual-test-plan skill bevezetése (MT1–MT12)`).
   **⛔ Path-scoped `git add`, soha `-A`** (0./7.) — pontosan ezek az útvonalak:
   ```bash
   git add prompts/skills-hu/manual-test-plan.md prompts/skills-en/manual-test-plan.md \
           prompts/lang/hu/manual-test-plan.md prompts/lang/en/manual-test-plan.md \
           prompts/lang/hu/descriptions.json prompts/lang/en/descriptions.json \
           prompts/lang/status-keys.json \
           prompts/scripts/manual-test-gate-check.py prompts/scripts/cycle-status.py \
           README.md prompts/meta-improve-prompts.md prompts/inprove-list5.md
   git status --short   # a jegyzet.md és minden más NEM stage-elt marad
   ```
