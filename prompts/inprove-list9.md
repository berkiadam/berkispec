# „A teszt megmondja, HOL fut — és a bizonyíték ezt igazolja" — végrehajtási terv

> **Ez a dokumentum önhordó.** Üres kontextusban, `/clear` után is végrehajtható: az 1. szakasz
> megadja a repó-orientációt, a 2. a problémát és a mérést, a 3. a lezárt döntéseket, a 4–8. a
> tételes teendőket, a 9. a dokumentációt, a 10. a kapukat, a 11. a végrehajtási sorrendet.
> **Semmit nem kell kikövetkeztetni** — ha valami mégis hiányzik, az a terv hibája; írd bele.
>
> **Státusz:** végrehajtásra vár. A 3. szakasz döntései **lezártak** — nem kell rákérdezned.
> **Előzmény:** a `prompts/inprove-list8.md` (`RUN1` · `TP4/b` · `EV7` · `SK1`) **elkészült**, és
> elkészült a `dev` → `remote` környezet-címke egységesítés is (`25bf354`). Ez a terv arra a résre
> válaszol, amit a `list8` 11. szakasza nyitva hagyott: a bizonyíték ma **kategória-szintű**, és
> semmi nem mondja meg, hogy egy KONKRÉT teszt hol futott.

---

## 0. Hogyan használd ezt a dokumentumot

1. **Olvasd el az 1–2. szakaszt.** Az 1. mondja meg, milyen repóban dolgozol és milyen kézi
   kapuk kötelezők; a 2. adja az indoklást, ami nélkül a checkek önkényesnek tűnnek.
2. **A 3. szakasz döntéseit ne nyisd újra.** Ha valamelyik a végrehajtás közben tarthatatlannak
   bizonyul, **írd a 12. szakaszba, mi lett helyette és miért** — ne csendben térj el tőle.
3. **A 11. szakasz sorrendjében haladj**, és minden teendő után **pipálj ebben a fájlban**
   (`- [ ]` → `- [x]`).
4. **Kétnyelvű repó:** minden prompt-szerkesztés **hu ÉS en párban** megy (1.2). A
   `lang-parity-check.py` a szerkezeti eltérést megfogja, a jelentés-eltérést **nem** — azt neked
   kell átolvasnod.
5. **Nincs CI és nincs pre-commit hook** — a kapukat (10. szakasz) **kézzel futtasd le**, commit előtt.

---

## 1. Orientáció — mi ez a repó, és mi mozdul

### 1.1 A rendszer

A `berkispec` egy **spec-driven development keretrendszer promptokból**: fázis-skillek (`00`–`09`),
subagent-promptok és determinisztikus **kapu-scriptek**. A repó a **forrás**; egy célprojektbe az
`install.sh` / `install.ps1` telepíti (öt platform: claude, codex, antigravity, cursor, copilot).
A telepítő **build-time** oldja fel az `<!-- INCLUDE:shared/… -->` / `<!-- INCLUDE:lang/… -->`
markereket és a `<sec:…>` / `<field:…>` / `<status:…>` tokeneket.

Amit ez a terv érint:

| útvonal | mi ez |
|---|---|
| `prompts/skills-{hu,en}/03b-write-test-plan.md` | a teszt-terv fázis — itt születnek a `TS-NN` forgatókönyvek és a gépi tábla |
| `prompts/skills-{hu,en}/06-implement.md` | az implementáció — itt íródik meg a teszt és a naplózó fixture |
| `prompts/skills-{hu,en}/07-validate.md` | a validálási fázis orchestrátora |
| `prompts/shared-{hu,en}/quality-check-plan-test.md` | a `03b` minőségi kapuja (a `plan-fixer` is beemeli) |
| `prompts/lang/{hu,en}/00-init-project.md` | a `conventions.md` sablonja (TR3 riport-tábla, Környezetek-tábla) |
| `prompts/scripts/analyze-gate-check.py` | a tervezési dokumentumok mechanikus kapuja (`--plan-only`) |
| `prompts/scripts/validate-gate-check.py` | a `07` gyűjtőkapuja (`--stage start` / `close`) |

### 1.2 A két nyelvi tengely (LG2/LG5)

- **prompt-nyelv:** a `prompts/skills-hu/` vs. `prompts/skills-en/` fa (az ágens *instrukcióinak*
  nyelve). **Minden szerkesztés mindkét fán megy, párban.**
- **projekt-nyelv:** amit az ágens a célprojektbe *ír* — ezt a `prompts/lang/{hu,en}/` blokkok és a
  `status-keys.json` tokenjei adják. A **scriptekben soha ne írj magyar/angol literált**: a
  `lang_keys` modul `sec()` / `fld()` / `st()` függvényeit használd — **kivéve** ott, ahol a 3.
  szakasz kimondottan nyelvfüggetlen literált ír elő (D2).

### 1.3 Kötelező kézi kapuk (nincs CI, nincs pre-commit hook)

```bash
python3 prompts/scripts/lang-parity-check.py            # szerkezeti paritás  → 0
python3 prompts/scripts/lang-parity-check.py --strict   # fájlhalmaz-paritás  → 0
python3 prompts/scripts/sync-gemini-agents.py --check   # agent.json tükrök   → 0
```
Ha egy **agent-prompt** (`prompts/agents-{hu,en}/*.md`) változik, előbb írás módban regenerálj:
`python3 prompts/scripts/sync-gemini-agents.py`.

### 1.4 Amit ez a terv NEM érint (kimondott nem-célok)

- **Nem** nyúlunk a `Környezet` oszlop értékkészletéhez: szabad szöveg marad, `remote` az ajánlott
  címke (a `list8` utáni átnevezés lezárt döntése).
- **Nem** írunk teszt-kódot a célprojektbe. A keret **előír** és **kapuz**; a naplózó fixture-t a
  `06` implementálja a célprojektben.
- **Nem** vezetünk be új `plan.md`-szekciót. A címke meglévő fejlécbe kerül, a bizonyíték meglévő
  artefaktum-útvonal alá.
- **Nem** bántjuk a `run-tests.py` `EV6` forgalmi checkjét — az kategória-szinten marad, és
  változatlanul fut. Az itt születő checkek **teszt-szinten** mérnek, mellette.

---

## 2. A probléma és a mérés

### 2.1 A rés, amit a `list8` nyitva hagyott

A `list8` négy kapuja (`RUN1` · `TP4/b` · `EV7` · `SK1`) azt zárta le, hogy egy deklarált
**kategória** tényleg lefutott-e. Amit **egyik sem** tud megmondani: **egy konkrét teszt hol futott.**

A ma elérhető bizonyítékok szemcsézettsége:

| bizonyíték | szemcse | mit mond |
|---|---|---|
| `results.json` `kornyezet` mező | **kategória** | a *deklarált* környezet, nem a mért |
| `EV6` forgalmi check | **kategória** | a körben keletkezett napló tartalmazza-e a cél-hostot |
| JUnit XML | teszt | pass/fail/skip — **hostot nem rögzít** |
| `rest-logs/` | **lapos halom** | 50 fájl egy mappában, teszt-hozzárendelés nélkül |

Az utolsó sor a lényeg: a `cycle-30`-ban a `test-report/validate/round-01/e2e/rest-logs/` **50
naplófájlt** tartalmazott — mind korábbi körből örökölt, `127.0.0.1`-es. A mappa *telinek látszott*.
A `TR7` (mtime-padló) és az `EV6` (host-tartalom) ezt utólag megfogta, de csak **kategória-szinten**
és csak **utólag**. Azt továbbra sem lehet megmondani, hogy a `TS-03` forgatókönyv **melyik**
naplófájlokat termelte, és hogy azok hova mentek.

### 2.2 A második rés: a remote teszt hiánya nem hiány-jelzés

A `cycle-30`-ban a dev-re szánt tesztek **dev-módja meg sem íródott**. A `PH1` megfogja, ha egyetlen
kategória sem fut `validate` fázisban; az `EV1` megfogja, ha nincs kimondva a cél-környezet. De
**semmi nem kérdez rá arra, hogy egy remote cél-környezetű ciklusban van-e egyáltalán remote teszt.**
A tervező leírhat nyolc lokális forgatókönyvet egy OpenShiftre szóló ciklusban, és minden kapu zöld.

### 2.3 Amit a felhasználó kimondott (a terv kiindulópontja)

> „A write-test-plan úgy kéne megírja a plan-t, hogy megjelöli, hogy remote vagy local a teszt,
> amit leír. És fontos: ha van értelme az adott ciklusban, akkor mindig gondolnia kell arra a
> write-test-plan fázisnak, hogy rakjon be remote tesztet is. Ez legyen egy címke a teszt neve
> mellett: `[remote|local]` — persze ezt ellenőrizheti is a kapu."

És a `remote` definíciója (már bekerült a `03b`-be, `25bf354`):

> `remote` minden olyan futás, amely akár **egyetlen** olyan komponenst is hív, ami nem a lokális
> gépen fut — a saját gépen futó konténer még `lokális`.

### 2.4 A tervezési feszültség, és a feloldása

A keret alapelve (`7/g`, `EV5`): **a név nem bizonyíték, a cím az.** Egy puszta `[remote]` címke
önbevallás — pontosan az a hibaosztály, amit az `EV7` üldöz (`TEST_ENV=dev`, amit senki nem olvas).

A feloldás nem az, hogy elvetjük a címkét, hanem hogy **két külön dolgot csinálunk belőle**:

- a **címke = SZÁNDÉK**, a `03b` terméke, a `03b` kapuja méri (megvan-e, van-e egyáltalán remote);
- az **útvonal + tartalom = BIZONYÍTÉK**, a futás terméke, a `07` kapuja méri;
- **az érték a kettő JOINJÁBAN van:** egy `[remote]`-nak jelölt teszt, amelynek naplói `local/` alá
  kerültek — vagy amelynek egyáltalán nincs naplója —, **önellentmondás**. Ez a `cycle-30`
  szignatúrája, teszt-szinten, determinisztikusan.

### 2.5 A domain-név csapdája (amiért a cím önmagában sem elég)

A cím-alapú besorolás **mindkét irányban** téved:

| eset | a cím azt mutatja | valójában |
|---|---|---|
| `kubectl` / `oc port-forward` → `127.0.0.1:8080` | local | **remote** — a komponens a klaszterben fut |
| compose service-név (`http://keycloak:8080`) | remote | **local** — konténer a saját gépen |

A port-forward a veszélyesebb: pont azt a hibaosztályt rejti el, amit az `EV5` üldöz — a teszt
lokálisnak *látszik*, miközben osztott klasztert szólít meg. Ezért a naplózó **nem a címből**
sorol be (D3), hanem a teszt saját jelöléséből; a cím a **kapu** bemenete lesz, nem a naplózóé.

---

## 3. Lezárt döntések

- [x] **D1 — Öt check, két fázisban.** `03b` oldal (`analyze-gate-check.py`): `EV8` (címke
  megléte), `EV9` (remote-lefedettség), `EV10` (címke ↔ gépi tábla konzisztencia). `07` oldal
  (`validate-gate-check.py`): `RL1` (útvonal ↔ tartalom), `RL2` (címke ↔ bizonyíték join).
  Egyik sem előfeltétele a másiknak, **külön commitolhatók**.

- [x] **D2 — A címke és a mappanév NYELVFÜGGETLEN literál: `[local]` / `[remote]`.** Nem
  `<status:…>` token. **Indoklás:** a címke egyetlen célja, hogy **útvonalra joinoljon**
  (`rest-logs/remote/<teszt>/`); a mappanevek a keretben mindig angolul állnak (`round-01`,
  `results.json`, `test-report`). Ha a címke projekt-nyelvi lenne (`[lokális]`), a joinhoz
  fordítási réteg kellene a kapuban ÉS a naplózó fixture-ben — és a kettő csendben szétcsúszhatna.
  Ez ugyanaz a csapda, mint a `gyors`/`nehéz` a `--type` kapcsolónál, csak most **előre** kerüljük el.
  A címke tehát mindkét prompt-fán `[local]` / `[remote]`.

- [x] **D3 — A naplózó a teszt SAJÁT JELÖLÉSÉBŐL sorol be, nem a hívott címből.** A cím-alapú
  besorolás a port-forwardnál és a compose-service-névnél is téved (2.5). A teszt-kód jelölése
  (`@pytest.mark.remote`, Playwright `@remote` tag) tükrözi a plan címkéjét, és a fixture ebből
  választ mappát. **Következmény:** az útvonal a címkéből következik, tehát önmagában nem
  bizonyíték — a bizonyíték a mappa **TARTALMA** (`RL1`).

- [x] **D4 — A besorolás a TESZT egészének tulajdonsága, nem a kérésé.** Ha egy teszt kilenc
  lokális és egy távoli hívást indít, az egész teszt `remote` (a felhasználó definíciója szerint:
  „akár egyetlen"). A fixture tehát nem tud kérésenként mappát váltani; a teszt jelölése dönt,
  egyszer.

- [x] **D5 — A címke helye a `TS-NN` fejléce.** `#### TS-01 [remote] — <a forgatókönyv neve>`.
  **Indoklás:** ez a tervezés egysége — itt dől el, hogy a forgatókönyv megszólít-e távoli
  komponenst —, és a `TS_HEADING_RE` (`analyze-gate-check.py`, ~1144. sor) már ma is parse-olja
  ezt a sort. A teszt-**függvény** a `<field:f_test_cases>` adatlap-soron át örökli a címkét
  (`\`test_foo\` → \`TC-01\``), tehát nem kell kétszer leírni. Egy tesztfájl vegyes hatóköre esetén
  a függvény szintjén felülírható: `` `test_foo` → `TC-01` [remote] ``.

- [x] **D6 — Unit-tábla sorai NEM kapnak címkét.** A `TC-NN` unit-esetek definíció szerint
  izoláltak (minden külső komponens mockolt), tehát mindig `local`. Címkét kérni tőlük zaj lenne,
  és a `TP4/b` tanulsága szerint egy kapu, ami zajt termel, kikapcsolásra ítéltetik. **Címke
  nélküli teszt alapértéke: `local`.**

- [x] **D7 — A hallgatás itt `local`-t jelent, és ez SZÁNDÉKOS eltérés a `PH1`-től.** A `PH1`-nél
  az üres cella „mindkettő", mert ott a hallgatás **kihagyást** okozna. Itt fordítva: ha a
  hallgatás `remote`-ot jelentene, minden unit-teszt remote bizonyítékot követelne, és a kapu
  használhatatlan lenne. A biztonságot nem a default adja, hanem az `EV8` (a `TS-NN` fejléce
  **kötelezően** jelölt) és az `EV9` (remote ciklusban **kell** remote forgatókönyv).

- [x] **D8 — `EV9` felmentése: `REMOTE-N/A: <indok>`** a `<sec:testing_strategy>` szekcióban.
  Van, amikor egy remote cél-környezetű ciklus tényleg nem tud remote tesztet adni (pl. a ciklus
  csak build-konfigurációt módosít). A felmentés a `_exemptions()` mintáját követi — a `list8`
  általánosította `key_re` paraméterrel —, de itt **kulcs nélküli**, egész ciklusra szóló sor,
  ezért saját, egyszerű regex.

- [x] **D9 — Régi ciklus nem bukhat.** Ha a planban nincs egyetlen `TS-NN` fejléc sem, vagy a
  kör-mappában nincs `local/`/`remote/` alszint (a konvenció nincs használatban), a checkek
  `info`-val kimaradnak. **Egy kapu, ami a jó, lezárt ciklust is bukatja, használhatatlan** — ez a
  `list8` D4 döntésének megismétlése, és a 10.7 hamis-pozitív próba erre méri.

- [x] **D10 — A port-forward DEKLARÁLT, nem kitalált.** A `conventions.md` `Környezetek és
  végpontok` táblájában egy sor jelöli a lokálisnak látszó, de távolra alagutazó címeket. Az `RL1`
  ezt beolvassa, és nem bukatja meg azt a `remote/` mappát, amelynek naplói ilyen címre mennek.
  **A deklaráció önmagában is érték:** ma teljesen láthatatlan, hogy egy „lokális" teszt klasztert hív.

---

## 4. `EV8` — a `TS-NN` forgatókönyv megmondja, hol fut

> **Mit mér:** minden `TS-NN` blokk fejléce hordoz-e `[local]` vagy `[remote]` címkét.

- [ ] **4.1 — A sablon bővítése (HU+EN).** `prompts/skills-{hu,en}/03b-write-test-plan.md`, a
  `#### TS-01 — <a forgatókönyv neve>  (DoD-02, DoD-05)` mintasor (~241. sor) →
  `#### TS-01 [remote] — <a forgatókönyv neve>  (DoD-02, DoD-05)`, alatta a kitöltési szabály:
  *„**A címke kötelező, és nyelvfüggetlen: `[local]` vagy `[remote]`.** `remote` minden olyan
  forgatókönyv, amely akár EGYETLEN olyan komponenst is megszólít, ami nem a lokális gépen fut —
  a saját gépen futó konténer még `local`. **A cím önmagában nem dönt:** egy `oc port-forward`
  mögötti `127.0.0.1:8080` **remote**, egy compose service-név (`http://keycloak:8080`) pedig
  **local**. A címke szabja meg, hova kerülnek a forgatókönyv REST-naplói a kör-mappában
  (`…/rest-logs/<local|remote>/<teszt>/`), és a `07` kapuja ebből joinol."*

- [ ] **4.2 — `TS_HEADING_RE` bővítése.** `analyze-gate-check.py`, ~1144. sor:
  ```python
  TS_HEADING_RE = re.compile(r"^#{3,5}\s*(TS-(\d+))\s*[—–-]\s*(.+?)\s*$")
  ```
  → a címke opcionális, a **3. csoport (a név) helye NE csússzon el**, mert több check használja
  (`check_test_scenarios`, `check_spec_coverage_scenarios`, `check_ts_http_blocks`):
  ```python
  TS_HEADING_RE = re.compile(
      r"^#{3,5}\s*(TS-(\d+))\s*(?:\[(local|remote)\])?\s*[—–-]\s*(.+?)\s*$", re.IGNORECASE)
  ```
  > **A csoport-indexek eltolódnak** (a név a 3.-ból a 4. lesz), de **egyetlen hívási hely van**:
  > a `parse_ts_blocks()` (~1151. sor), a `cur = {...}` értékadásban (~1158. sor). Ezt az EGY sort
  > kell igazítani, és a címkét mindjárt fel is venni a blokkba:
  > ```python
  > cur = {"id": m.group(1), "num": int(m.group(2)),
  >        "scope": (m.group(3) or "").lower() or None, "cim": m.group(4), "lines": []}
  > ```
  > **Miért mégis figyelmet érdemel:** a `parse_ts_blocks()` kimenetét **hat check fogyasztja**
  > (~1191, 1382, 1494, 1697, 1987. sor), tehát egy elrontott `cim` mező nem hibát ad, hanem
  > **rossz ítéletet** hat helyen. Ezért a 10.8 regresszió-próba kötelező — de a szerkesztés maga
  > egyetlen sor, nem hat.
  > **A `scope` mező a blokkban** azért jó, mert innentől a 4.3, az 5.1 és a 6.1 mind ugyanabból
  > az EGY parse-olóból dolgozik — nem lesz második címke-értelmező.

- [ ] **4.3 — Új check: `check_scenario_scope(plan_text, f)`.**
  Járd be a `TS-NN` fejléceket. Amelyiknek nincs címkéje → `f.add("EV8", "03", …)`:
  *„a `TS-NN` forgatókönyv fejlécéből hiányzik a hatókör-címke (EV8) — `#### TS-NN [local] — …`
  vagy `[remote]`. A címke mondja meg, hol fut a forgatókönyv, és a `07` kapuja ebből joinol a
  kör REST-naplóira. `remote` minden olyan futás, amely akár egyetlen nem a lokális gépen futó
  komponenst is hív; a cím önmagában nem dönt (port-forward)."*
  Hívás: az `analyze-gate-check.py` `main()` teszt-oldali blokkjában (`if not code_only:`), a
  `check_test_scenarios` **mellé**.

- [ ] **4.4 — Verifikáció.**
  - **bukás-próba:** címke nélküli `TS-01` fejléc → `EV8` megállapítás;
  - **átmegy:** `#### TS-01 [remote] — …` és `#### TS-02 [local] — …` → nincs `EV8`;
  - **🔴 regresszió-próba:** futtasd a `--plan-only` kaput egy TELJES, szabályos planre **a
    változtatás előtt és után**, és vesd össze a kimenetet: a `TS1–TS8`, `TA1`, `TI1` és
    `spec_coverage` megállapítások **száma és szövege bájtra egyezzen** — a `parse_ts_blocks()`
    kimenetét hat check fogyasztja, és egy elrontott `cim` mező mindegyiket csendben elrontja;
  - **hamis-pozitív próba:** olyan plan, amelyben nincs `TS-NN` fejléc → **nincs** `EV8` (D9).

---

## 5. `EV9` — remote ciklusban van remote teszt

> **Mit mér:** ha a ciklus cél-környezete nem kizárólag lokális, van-e legalább egy `[remote]`
> forgatókönyv. Ez a felhasználó „mindig gondolnia kell rá" követelményének gépi alakja.

- [ ] **5.1 — Az `EV9` ág a `check_scenario_scope`-ban.** A `check_target_environment`
  (`analyze-gate-check.py`, ~1917. sor) már kiszámolja azt, ami kell:
  ```python
  target_m = re.search(r"\*\*" + re.escape(fld("f_target_env")) + r":\*\*\s*(.+)", coords or "")
  target_is_local_only = _env_is_local(target) if target else False
  ```
  **Emeld ki ezt a két sort egy segédfüggvénybe** (`_target_env(plan_text)` → `(szöveg, lokális-e)`),
  és hívd mindkét helyről — ne másold. Ha a cél-környezet **nem** kizárólag lokális, ÉS egyetlen
  `TS-NN` sem `[remote]`, ÉS nincs `REMOTE-N/A:` felmentés → `f.add("EV9", "03", …)`:
  *„a ciklus cél-környezete `<érték>` (nem lokális), de a plan egyetlen `[remote]` forgatókönyvet
  sem tartalmaz (EV9) — a `<sec:plan_test_scenarios>` mind a N forgatókönyve `[local]`. Egy remote
  környezetre szóló ciklus, amelyet csak lokális tesztek igazolnak, pontosan azt nem bizonyítja,
  amiért készült: hogy a TELEPÍTETT komponens működik. Írj legalább egy `[remote]` forgatókönyvet
  — vagy ha ebben a ciklusban tényleg nincs értelme, indokold `REMOTE-N/A: <miért>` sorral a
  `<sec:testing_strategy>` szekcióban."*

- [ ] **5.2 — A felmentés parse-olása.** `REMOTE-N/A:` sor a `<sec:testing_strategy>` szekcióban,
  egyszerű regexszel (`^\s*REMOTE-N/A:\s*(\S.*)$`, `re.MULTILINE`) — **kulcs nélküli**, egész
  ciklusra szóló felmentés, ezért NEM a `_exemptions()` (az kulcs → indok párokat ad). Ha van
  ilyen sor, az `EV9` `f.suggest`-re vált (nyomot hagy, nem blokkol).

- [ ] **5.3 — A `03b` minőségi kapujának új pontja (HU+EN).**
  `prompts/shared-{hu,en}/quality-check-plan-test.md`, az `EV1–EV5`-ös pont **mellé**:
  *„**🔴 Minden forgatókönyv megmondja, HOL fut — és van remote teszt? (EV8/EV9)** — Minden
  `TS-NN` fejléce hordoz `[local]` vagy `[remote]` címkét (nyelvfüggetlen literál, mert a kör
  REST-napló-mappájára joinol). **`remote` minden olyan futás, amely akár egyetlen nem a lokális
  gépen futó komponenst is hív** — a saját gépen futó konténer még `local`, egy `oc port-forward`
  mögötti `127.0.0.1` viszont **remote**: a cím önmagában nem dönt. És ha a ciklus cél-környezete
  nem lokális, **legalább egy `[remote]` forgatókönyv kell**: egy remote környezetre szóló ciklus,
  amit csak lokális tesztek igazolnak, pontosan azt nem bizonyítja, amiért készült. Ha tényleg
  nincs értelme, `REMOTE-N/A: <miért>` sor a `<sec:testing_strategy>`-ben."*

- [ ] **5.4 — Verifikáció.**
  - **bukás-próba:** `<field:f_target_env>: remote`, minden `TS-NN` `[local]` → `EV9`;
  - **felmentés-próba:** ugyanez + `REMOTE-N/A: a ciklus csak build-konfigurációt módosít` →
    javaslat, nem Must Fix;
  - **hamis-pozitív próba 1:** `<field:f_target_env>: lokális`, minden `TS-NN` `[local]` → **nincs** `EV9`;
  - **hamis-pozitív próba 2:** `remote` cél-környezet + egy `[remote]` forgatókönyv → **nincs** `EV9`.

---

## 6. `EV10` — a címke és a gépi tábla nem mondhat ellent

> **Mit mér:** ha van `[remote]` forgatókönyv, a gépi futtatási táblában van-e egyáltalán
> nem-lokális kategória, amelyik lefuttathatná.

- [ ] **6.1 — Az `EV10` ág a `check_scenario_scope`-ban.** Ha van legalább egy `[remote]`
  forgatókönyv, de a gépi tábla **minden** sorának `Környezet` cellája lokális
  (`_env_is_local()` mindegyikre igaz) → `f.add("EV10", "03", …)`:
  *„a plan N `[remote]` forgatókönyvet ír le, de a gépi futtatási tábla minden kategóriája
  `lokális` (EV10) — így a remote forgatókönyvet SEMMI nem futtatja le remote célpont ellen. Vagy
  a forgatókönyv címkéje téves, vagy hiányzik a nem-lokális kategória a táblából."*
  > **Miért csak ilyen durva a join:** a forgatókönyv → kategória hozzárendelés a planban **nem
  > explicit** (a `TS-NN` nem nevezi meg a kategóriáját). Egy parancs-egyeztetésre épülő,
  > finomabb join törékeny lenne, és a `TP4/b` tanulsága szerint egy törékeny kapu rosszabb, mint
  > egy durva. **Ne találd ki a finomabb változatot** — ha kell, az külön tétel.

- [ ] **6.2 — Verifikáció.**
  - **bukás-próba:** egy `[remote]` `TS-NN` + csak `lokális` kategóriák a táblában → `EV10`;
  - **hamis-pozitív próba:** ugyanez, de a táblában van egy `remote` kategória → **nincs** `EV10`;
  - **hamis-pozitív próba 2:** nincs `[remote]` forgatókönyv → **nincs** `EV10`.

---

## 7. `RL1`/`RL2` — a REST-napló szerkezete és a join

> **Mit mér:** `RL1` — a `remote/` alatti napló tartalmaz-e valóban távoli címet (és a `local/`
> alatti nem tartalmaz-e csak távolit). `RL2` — minden `[remote]` forgatókönyv termelt-e
> egyáltalán remote naplót ebben a körben.

### 7.1 A konvenció (amit a projektnek elő kell állítania)

```
<kör-mappa>/<kategória>/rest-logs/<local|remote>/<teszt-név>/
```

Példák a felhasználó megfogalmazása szerint:

```
specs/cycle-30-…/test-report/validate/round-01/e2e/rest-logs/local/test_token_exchange_ok/
specs/cycle-30-…/test-report/validate/round-01/e2e/rest-logs/remote/test_dsp01_preflight/
specs/cycle-30-…/test-report/implement/s2s/rest-logs/remote/test_s2s_renewal/
```

> **🔴 A TR3 tábla és a két meglévő kapu NEM változik.** A `conventions.md` artefaktum-cellája
> marad `e2e/rest-logs/`; az új szintek **az alá** kerülnek. A `report-gate-check.py` (`:283`) és a
> `run-tests.py` `EV6` egyaránt `rglob("*")`-gal járja be a mappa-artefaktumot, tehát a beágyazott
> szerkezetet változtatás nélkül látják. Ez a döntés tudatos: a szerkezet **kiegészítés**, nem
> séma-váltás — így egyetlen meglévő projekt sem törik el.

- [ ] **7.2 — `conventions.md` sablon (HU+EN).** `prompts/lang/{hu,en}/00-init-project.md`, a TR3
  tábla „Alkalmazás-oldali audit / REST kérés-válasz" sorának kitöltési szabályai közé:
  *„**A REST-naplók teszt-szerinti almappákba mennek:** `<artefaktum>/<local|remote>/<teszt-név>/`.
  A `local`/`remote` szint **nyelvfüggetlen**, és a **teszt saját jelöléséből** következik (nem a
  hívott címből — egy `oc port-forward` mögötti `127.0.0.1` remote). A teszt-név a teszt-függvény
  neve, útvonal-biztosra normalizálva (`[^A-Za-z0-9._-]` → `-`). Enélkül a napló egy lapos halom,
  amelyből utólag nem állapítható meg, melyik teszt mit hívott — és egy korábbi körből örökölt
  fájlokkal teli mappa telinek látszik."*

- [ ] **7.3 — Port-forward deklaráció a Környezetek-táblában (HU+EN).** Ugyanott, a `Környezetek
  és végpontok` tábla kitöltési szabályai közé:
  *„**Ha egy cím lokálisnak látszik, de távolra visz** (`kubectl`/`oc port-forward`, SSH-alagút),
  azt **külön sorban, `remote` környezettel** kell felvenni, a valódi célt is megnevezve. Ez az
  egyetlen hely, ahol ez látszik: a `127.0.0.1:8080` a naplóban semmit nem árul el arról, hogy a
  másik végén egy osztott klaszter van."*

- [ ] **7.4 — `RL1` — útvonal ↔ tartalom.** Új check a `validate-gate-check.py`-ba,
  `check_rest_log_scope(cycle, rep, stage)`:
  1. `stage != "close"` → `return`.
  2. Az utolsó kör-mappát a **meglévő** `_last_round_dir(cycle)` adja (a `list8` írta, az `SK1`-hez).
  3. Keress `rest-logs/local/` és `rest-logs/remote/` alakú mappákat (`rglob`). Ha egy sincs →
     `rep.info(...)` + `return` (a konvenció nincs használatban — D9).
  4. Minden `remote/<teszt>/` mappára: ha a benne lévő szöveges fájlok **egyikében sem** szerepel
     nem-lokális host (a `run-tests.py` `LOCAL_HOST_RE` és `HOST_RE` mintáival), és a
     `conventions.md` nem deklarál port-forwardot → `rep.bad(...)`:
     *„a `<teszt>` teszt naplói a `remote/` mappában állnak, de egyik sem tartalmaz nem-lokális
     címet (RL1) — a „remote" futás lokális futás volt. Ha `port-forward` mögött fut, vedd fel a
     `conventions.md` Környezetek-táblájába."*
  5. Minden `local/<teszt>/` mappára: ha **minden** logolt host nem-lokális → `rep.bad(...)`
     (fordított tévedés: a teszt remote, de local-nak jelölték).
  6. Rendben: `rep.ok(...)` a mappák és tesztek számával.

- [ ] **7.5 — `RL2` — címke ↔ bizonyíték join.** Ugyanabban a checkben, a `RL1` után:
  1. Olvasd ki a plan `[remote]` forgatókönyveit (a 4.3 regexével — **közös segédfüggvényt**
     használj, ne harmadik parse-olót; a `list8` `_load_run_tests_module()` mintája szerint akár
     az `analyze-gate-check.py` is betölthető modulként).
  2. A `<field:f_test_cases>` leképezésből (a `list8` `_plan_test_case_map()`-je **már megvan**)
     szedd ki, mely teszt-függvények tartoznak `[remote]` forgatókönyvhöz.
  3. Ha egy ilyen függvényhez **nincs** `remote/<teszt>/` mappa a körben → `rep.bad(...)`:
     *„a `<teszt>` a plan `<TS-NN>` `[remote]` forgatókönyvéhez tartozik, de a `round-NN` körben
     nincs `rest-logs/remote/` naplója (RL2) — vagy nem futott le, vagy nem indított forgalmat.
     Felmentés: `SCOPE-EXEMPT: <teszt> — <indok>` a `check-log.md` `## <sec:notes>` szekciójában."*
  4. Felmentés: `_exemptions(text, "SCOPE-EXEMPT", key_re=r"[\w./:\[\]-]+")` — a `list8`
     általánosította a függvényt, itt **csak hívni kell**.

- [ ] **7.6 — A `06` szövege (HU+EN).** `prompts/skills-{hu,en}/06-implement.md`, az anti-stub
  garde mellé: *„**A teszt jelölése nem dekoráció (RL1).** Ha a plan `TS-NN` blokkja `[remote]`, a
  tesztnek hordoznia kell a megfelelő jelölést (`@pytest.mark.remote`, Playwright `@remote` tag), és
  a REST-naplózó fixture ebből választ mappát (`rest-logs/remote/<teszt>/`). **A besorolás a teszt
  EGÉSZÉNEK tulajdonsága:** ha a teszt akár egyetlen nem a lokális gépen futó komponenst is hív, az
  egész teszt `remote` — a fixture ezért a teardown-ban mozgat, nem kérésenként. A `07` kapuja
  megnézi, hogy a `remote/` mappában tényleg van-e nem-lokális cím: egy üresen maradt vagy csak
  `127.0.0.1`-et tartalmazó remote mappa bukás."*

- [ ] **7.7 — A `07` szövege (HU+EN).** A kör-lezáró kapu-blokk felsorolásába két sor az
  `RL1`/`RL2`-ről, a `RUN1`/`SK1` mintájára.

- [ ] **7.8 — Verifikáció.** Gyárts a scratchpadba egy kör-mappát:
  - **bukás-próba 1:** `rest-logs/remote/test_a/` csak `127.0.0.1`-es naplóval → `RL1` bukás;
  - **bukás-próba 2:** `[remote]` `TS-01` → `test_a`, de nincs `rest-logs/remote/test_a/` → `RL2` bukás;
  - **felmentés-próba:** `SCOPE-EXEMPT: test_a — nincs VPN ebben a körben` a `check-log.md`
    jegyzeteiben → átengedi;
  - **hamis-pozitív próba 1:** lapos, régi `rest-logs/*.log` (nincs `local/`/`remote/` alszint)
    → `info`, `exit 0`;
  - **hamis-pozitív próba 2:** `rest-logs/remote/test_a/` valódi távoli hosttal → **nem** szól;
  - **hamis-pozitív próba 3:** `rest-logs/local/test_b/` lokális címekkel → **nem** szól.

---

## 8. (fenntartva)

_Ez a szakasz szándékosan üres — a 4–7. a négy keményítés, a 9. a dokumentáció. A számozás a
`list8` szerkezetét követi, hogy a két terv egymás mellett olvasható legyen._

---

## 9. Dokumentáció

- [ ] **9.1 — `README-HU.md` + `README.md`.** Két helyen:
  - a `07-validate` determinisztikus rétegének táblájába egy sor: *„HOL futott ez a KONKRÉT
    teszt?" → `validate-gate-check.py` (`RL1`/`RL2`)*;
  - **új tanulság-bekezdés** a meglévők közé (a „A zöld kör nem bizonyítja…" bekezdés **után**),
    a 2. szakasz réseivel és az öt kapu táblájával.
- [ ] **9.2 — `berki-spec-directory-structure.md`.** Az `analyze-gate-check.py` sorának bővítése
  az `EV8`/`EV9`/`EV10`-zel, a `validate-gate-check.py` soráé az `RL1`/`RL2`-vel.
- [ ] **9.3 — `prompts/meta-improve-prompts.md`: új elv `7/n`**, a `7/m` után. Vázlat a meglévő
  elvek hangján:

  *A `7/l` a **teszt**, a `7/m` a **kategória** szintjén kérdezte meg, mi bizonyítja, hogy történt
  is valami. Maradt egy harmadik szint: **egy konkrét teszt HOL futott.** A bizonyíték eddig
  kategória-szemcsés volt — a `results.json` a deklarált környezetet írta, a JUnit XML hostot nem
  rögzít, a `rest-logs` pedig egy lapos halom volt, amelyből nem derült ki, melyik teszt mit hívott.
  Ezért egy remote környezetre szóló ciklusban semmi nem kérdezett rá arra, hogy van-e egyáltalán
  remote teszt. A feloldás **kettéválasztja a szándékot és a bizonyítékot**: a `TS-NN` fejléce
  `[local]`/`[remote]` címkét kap (szándék, a `03b` kapuja méri — `EV8`/`EV9`/`EV10`), a REST-napló
  pedig teszt-szerinti almappába megy (`rest-logs/<local|remote>/<teszt>/`, bizonyíték, a `07`
  kapuja méri — `RL1`/`RL2`). **Az érték a kettő JOINJÁBAN van:** egy `[remote]`-nak jelölt teszt,
  amelynek naplója `local/` alá került vagy hiányzik, önellentmondás. **Prompt-módosításnál két
  kérdés:** (a) ha egy bizonyíték **szemcsézettsége** durvább, mint a döntésé, amit alátámaszt
  (kategória-szintű bizonyíték egy teszt-szintű állításhoz), mi tölti ki a rést — vagy csak
  reméljük, hogy a durva bizonyíték a finom állításra is igaz? (b) ha egy szabály azt mondja, „ezt
  mindig **gondold** végig", mi bizonyítja, hogy végig lett gondolva — van-e olyan artefaktum,
  amiből a mulasztás **hiányként** kiolvasható?*

---

## 10. Kapuk és elfogadási kritériumok

- [ ] **10.1** `python3 prompts/scripts/lang-parity-check.py` → hiba nélkül.
- [ ] **10.2** `python3 prompts/scripts/lang-parity-check.py --strict` → 0.
- [ ] **10.3** `python3 prompts/scripts/sync-gemini-agents.py --check` → 0.
- [ ] **10.4** Mindkét érintett script szintaktikailag ép és a súgója fut:
  ```bash
  for s in analyze-gate-check validate-gate-check; do
    python3 -c "import ast;ast.parse(open('prompts/scripts/$s.py').read())" && echo "$s OK"
  done
  ```
- [ ] **10.5** Telepítési füstteszt legalább egy platformra, **hu és en** prompt-nyelven: a
  telepített `03b-write-test-plan`, `06-implement` és `07-validate` **`.md`** fájljaiban **nincs**
  feloldatlan `INCLUDE:` marker és `<sec:` / `<field:` / `<status:` token.
  > *(A `.py` scriptekben lévő token-literálok pre-existing állapot — négy script kommentjeiben
  > `18acadc` óta ott vannak, és az `acceptance-check.sh:80` emiatt már ma is piros. **Ebbe a
  > tervbe ne vedd bele** a javítását; ha zavar, vedd fel külön tételként.)*
- [ ] **10.6** Mind az öt check **célzott bukás-próbája** lefutott: 4.4, 5.4, 6.2, 7.8.
- [ ] **10.7 — Hamis-pozitív próba (kötelező).** Futtasd az öt checket **korábbi, sikeresen
  lezárt ciklusokra**. Ami itt bukik, azt **meg kell érteni**: vagy valódi rés volt ott is (akkor
  írd a 12. szakaszba), vagy a check túl agresszív (akkor szűkítsd). **Egy kapu, ami a jó ciklust
  is bukatja, használhatatlan.** Külön figyelj a `TS-NN` címke nélküli régi planekre (D9) és a
  lapos `rest-logs/` mappákra.
- [ ] **10.8 — 🔴 `TS_HEADING_RE` regresszió-próba.** A 4.4 harmadik pontja: egy teljes,
  szabályos plan `--plan-only` kimenete a változtatás **előtt és után** bájtra egyezzen a
  `TS`/`TA1`/`TI1`/`spec_coverage` megállapításokban. Ez a terv egyetlen olyan szerkesztése, amely
  **meglévő, működő checkeket** tud csendben elrontani.
- [ ] **10.9** Commit: `feat(prompts): teszt-hatókör címke és REST-napló bizonyíték — EV8-EV10, RL1, RL2`

---

## 11. Végrehajtási sorrend

1. **4.2** — `TS_HEADING_RE` bővítése + **10.8 regresszió-próba azonnal**. *Elöl, mert ez az
   egyetlen szerkesztés, ami meglévő checkeket ronthat el; ha itt baj van, minden más várhat.*
2. **4.1, 4.3, 4.4** `EV8` — a címke sablonja és kapuja. *A többi check erre épül.*
3. **5.** `EV9` — remote-lefedettség. *A felhasználó „mindig gondolnia kell rá" követelménye;
   a legnagyobb hozamú tervezési kapu.*
4. **6.** `EV10` — címke ↔ tábla konzisztencia. *Olcsó, és a `03b`-ben fogja meg az ellentmondást.*
5. **7.2, 7.3** — a `conventions.md` sablon és a port-forward deklaráció. *A `07` oldali checkek
   ezt feltételezik; a konvenciónak előbb kell léteznie, mint a kapunak.*
6. **7.4–7.8** `RL1`/`RL2` — a bizonyíték-oldal és a prompt-szövegek.
7. **10.6–10.8** A célzott bukás-próbák, a hamis-pozitív próba és a regresszió-próba.
8. **9.** Dokumentáció.
9. **10.1–10.5, 10.9** Kapuk, telepítési füstteszt, commit.

> **Miért a `TS_HEADING_RE` az első:** a `parse_ts_blocks()` kimenetét **hat meglévő check**
> fogyasztja. A szerkesztés egyetlen sor, de ha a csoport-indexek elcsúsznak, azok a checkek
> **nem hibáznak, hanem rossz értéket ítélnek** — pontosan az a hibaosztály, amit a `TP4/b` a gépi
> táblánál megfogott. A regresszió-próbát ezért nem a végén, hanem **közvetlenül a szerkesztés
> után** kell lefuttatni.

---

## 12. Tapasztalatok (a végrehajtás közben töltsd)

> Ide kerül a 10.7 hamis-pozitív próba eredménye (mely régi ciklus min bukott, és miért), a 10.8
> regresszió-próba eredménye, és minden olyan felismerés, ami a terv írásakor nem látszott. Ha egy
> döntés (3. szakasz) tarthatatlannak bizonyult, **írd ide, mi lett helyette és miért** — ez lesz a
> `meta-improve-prompts.md` `7/n` elv végleges szövegének forrása.

- _(még nincs bejegyzés)_
