#!/usr/bin/env python3
"""Analyze mechanikus kapu — a ciklus tervezési dokumentumainak GÉPIESEN
eldönthető konzisztencia-ellenőrzései (05-analyze).

Miért kell: az `analyzer` subagent hat kategóriája közül több ellenőrzés
tisztán szöveg-mintázat kérdése (hivatkozás-egyeztetés, marker-jelenlét,
azonosító-duplikáció, kötelező táblák megléte). Ezeket LLM-mel futtatni
drága ÉS megbízhatatlan: egy olcsóbb modell hol kihagy, hol hamisan riaszt.
Ez a szkript ezt a réteget determinisztikussá teszi, így az analyzer a
SZEMANTIKAI kategóriákra koncentrálhat (ambiguitás, alulspecifikáció,
lefedettségi értelmezés, végrehajthatóság).

Mit ellenőriz:

  P1  plan-ID formátum és egyediség  — `[P-...]` a plan címsoraiban
  P2  task → plan hivatkozás megléte — minden `- [ ] Tnnn ...` sor végén `plan [P-...]`
  P3  task → nem létező plan-ID      — hivatkozás, amihez nincs plan-szekció
  P4  plan-ID → nincs hivatkozó task — és a `Plan-lefedettség` tábla sem említi
  P5  sorszámos hivatkozás           — `plan.md § 3.1` stílus `[P-...]` helyett
  T1  marker minden taskon           — `[RED]`/`[GREEN]`/`[CHECK]`/`[OPS]`
  T2  `[OPS]` fájl-útvonallal        — repo-fájlt szerkesztő task rossz markerrel
  T3  státusz-frissítő task          — spec/plan/tasks státuszát állító task
  T4  `⟂` szimmetria                 — `T012 ⟂ T013`, de `T013` nem hivatkozik vissza
  T5  placeholder a parancsban       — `{round}` alakú kitöltetlen hely egy
                                       `[CHECK]`/`[OPS]` task parancsában: az
                                       ágensnek találgatnia kellene, mit írjon
                                       oda (a `<valami>` alak csak javaslat)
  D1  `DoD-NN` azonosítók            — hiányzó vagy duplikált azonosító a specben
  D2  `DoD-NNb` alakú azonosító      — utólagos beszúrás betűs utótaggal (DI1 megsértése)
  S1  kötelező plan-táblák           — `Spec-lefedettség`, `Fordított lefedettség`,
                                       `Környezeti koordináták` (KO1),
                                       `Gépi futtatási tábla` (TP4)
  S2  kötelező tasks-tábla           — `Plan-lefedettség`
  A1  futtatott artefaktum (6.a)     — a `[CHECK]`/`[OPS]` taskok és a plan
                                       `Ellenőrzési stratégia` parancsai által
                                       futtatott fájl létezik, vagy van rá
                                       létrehozó task?
  A2  plan-horgony (6.g fájl-szint)  — a `path:sor` hivatkozás feloldható?
  A2b horgony-sorszám (javaslat)     — a sorszám a fájl hosszán belül van?
  A3  artefaktum-hang (6.h, javaslat)— kemény padló: `🔴` / „Tilos" forma
  S3  Fordított lefedettség sor-ID     — a sor viseli-e a `[P-…]` azonosítót.
                                       Ha nem, de a plan CÍMSORÁBÓL feloldható,
                                       csak javaslat (a régebbi, ID nélküli
                                       táblasorok így nem dobnak vissza egy
                                       futó ciklust); ha nem oldható fel,
                                       Must Fix — a lánc nem zárható.
  C1  DoD → plan lefedettség          — van plan-képesség, ami a DoD-pontra
                                       vezet vissza?
  C2  DoD → task lefedettség          — a DoD-t lefedő plan-szekcióhoz van task?
  C3  TP1                             — minden `DoD-NN` szerepel a plan
                                       `Spec-lefedettség` táblájában?
  C4  KF1                             — a `Konfiguráció-életút` táblában nincs
                                       üres cella?
  C6  KO1                             — a `Környezeti koordináták` szekcióban
                                       nincs placeholder és nincs üres cella?
  C5  task-határon átnyúló shell-változó — `VAR=` az egyik taskban, `$VAR` egy
                                       másikban: külön shell, üres változó,
                                       érvénytelen deploy/rollback (6.f)
  V1  csonkítás-mentesség (KX3)        — a spec szerződés-artefaktumai (OpenAPI,
                                       JSON/YAML/SQL blokk, payload, curl) szó
                                       szerint átkerültek-e a plan-be
  V2  teszt-szekció terjedelme (KX3)   — a plan teszt-szekciója nem kisebb-e a
                                       spec `Teszt specifikáció` szekciójánál
  TS1 van `Teszt-forgatókönyvek`      — a plan `Tesztelési stratégia` szekciója
                                       tartalmaz-e `TS-NN` forgatókönyveket
  TS2 a `TS-NN` blokk teljes           — Mit tesztelünk / Előfeltétel /
                                       lépés-tábla / Takarítás megvan-e
  TS3 lépésenkénti konkrétum           — a `Hívás` és az `Elvárt eredmény`
                                       cella kitöltött és KONKRÉT (backtickes
                                       érték vagy szám), nem „sikeresen lefut"
  TS4 placeholder-tilalom              — a `TS-NN` blokkokban nincs `<…>`/TODO
  TS5 kétirányú DoD-lefedettség        — minden `DoD-NN`-hez van `TS-NN`, és
                                       minden `TS-NN` létező DoD-ra hivatkozik
  TS6 `TS-NN` azonosítók               — egyediek és hézagmentesek
  TS8 `.http` alak a REST-hez     — ahol `curl` van a forgatókönyvben, ott
                                       ```http blokk is (és fordítva)
  GA1 kapu-bélyeg (javaslat)           — lezárt plan fejlécében ott a
                                       `Kapu:` sor a kapu-futás eredményével
  TI1 `TC-NN` azonosítók               — szigorú alak, hézagmentes számsor a
                                       plan teszt-tábláiban
  TI2 task → teszt hivatkozás          — a `— test [TC-01]` jelölés létező
                                       plan-teszt-azonosítóra mutat
  TX1 egy `[CHECK]` egy teszt          — a futtató checkbox pontosan egy
                                       teszt-azonosítót futtat
  TT1 teszt-lefedettség                — minden `TS-NN` és minden futtatási
                                       kategória kap gazdát a tasks.md
                                       `Teszt-lefedettség` táblájában
  T6  `[CHECK]` kimenet-ütközés        — két task `>`-tal ugyanabba a log-/
                                       riportfájlba ír: a második felülírja az
                                       elsőt, a bizonyíték eltűnik
  PH1 futtatási fázis                  — a gépi tábla `Fázis` oszlopának értékei
                                       érvényesek, és marad kategória a 07-re
  TS7 spec-teszteset → `TS-NN`         — a `Spec-lefedettség` tábla minden sora
                                       megnevez egy forgatókönyvet (vagy az
                                       indoklást, ha nem tesztelhető): a spec
                                       teszt-szekciójának SZERKEZETE nem
                                       másolható át prózaként
  TA1 teszt-artefaktum adatlap         — minden tesztfájl-fejléc alatt ott a
                                       futtató parancs, a fixture/tesztadat és a
                                       teszt-függvény → `TC-ID`/`TS-NN` leképezés
  WY1 a tervezett módosítás CÉLJA      — minden `[P-…]` bejegyzés megmondja, mit
                                       akarunk elérni és miért (spec-forrással)
  EV1 cél-környezet deklarálva         — a `Környezeti koordináták` szekcióban
                                       ott a `**Cél-környezet:**` mező
  EV2 kategóriánkénti `Környezet`      — a gépi futtatási tábla minden sora
                                       megmondja, hol fut
  EV3 a cél a PARANCSBAN van           — nem-lokális kategóriánál a parancs
                                       literálisan tartalmazza a cél-hostot,
                                       nem konfigfájlba rejtve
  EV4 cél-elérhetőségi probe           — nem-lokális kategóriánál az
                                       `Előfeltétel` ugyanarra a hostra hív
  EV5 nincs lokális cél távoli körben  — nem-lokális kategória parancsa és a
                                       `TS-NN` hívások nem mutathatnak
                                       localhostra
  EV8 hatókör-címke a `TS-NN`-en      — minden forgatókönyv fejléce hordoz
                                       `[local]` vagy `[remote]` címkét
                                       (nyelvfüggetlen literál)
  EV9 remote ciklusban remote teszt    — nem-lokális cél-környezetnél van
                                       legalább egy `[remote]` forgatókönyv
                                       (`REMOTE-N/A: <indok>` sorral felmenthető)
  EV10 címke ↔ gépi tábla              — `[remote]` forgatókönyv mellé kell
                                       nem-lokális kategória is a táblába
  R1  útvonal-formátum (RP1)           — `file://`, gép-specifikus (`/home/…`,
                                       `C:/Users/…`), placeholder és abszolút
                                       repó-útvonal a tervezési dokumentumokban
  A2c horgony-formátum (RP1, javaslat) — a `path:sor` horgony a plan MAPPÁJÁHOZ
                                       képest relatív, nem a repó gyökeréhez

A `--report-only` mód (a fentiektől FÜGGETLEN, a hurok LEZÁRÁSAKOR fut):

  RC1 tétel-megőrzés                   — az `analyze-task.md` minden tétele
                                       (nyitott ÉS elvetett) szó szerinti
                                       azonosítóval megjelenik-e az
                                       `analyze-report.md` „Javítandó tételek"
                                       listáján. Ez az őr arra az esetre, amikor
                                       a lezáráskor a riport ÖSSZEFOGLALÓVÁ
                                       zsugorodik: a részletes, emberi nyelvű
                                       diagnózis elvész, csak a puszta tény
                                       marad, hogy „minden javítva lett" (AR1
                                       megsértése).
  RC2 kötelező mező hiánya             — egy megmaradt tételnél a négy
                                       kötelező mező (`Az ellentmondás`,
                                       `Miért blokkol`, `Hogyan lenne helyes`,
                                       `Állapot`) valamelyike üres vagy
                                       placeholder maradt.
  RC3 lezáratlan tétel                 — a riport `Státusz` mezője `PASS`,
                                       de egy tétel `[ ]` (nyitva) maradt, vagy
                                       az `Állapot` mezője nem futott végállapotba.

Ezt a három utolsó checket korábban az `analyzer` subagent végezte, `Glob`/`Grep`
hívások sorozatával (AG3). Egy teljes analyze-futásban ez 20–50 soros
tool-körfordulót jelentett, futásonként újra — miközben mindhárom tisztán
fájllétezés- és regex-kérdés, tehát determinisztikusan és ingyen eldönthető.

A szkript ezen felül két nem-megállapítás blokkot is kiír:

  `## Lefedettségi mátrix (generált)` — a `DoD-NN → Fordított lefedettség →
  [P-…] → task` lánc tranzitívan zárt, tehát gépies (AG4). Eddig ez volt az
  `analyzer` legnagyobb munka- ÉS kimeneti blokkja, ráadásul a leginkább
  megerősítés-torzításra hajlamos része („keress hozzá taskot"). Az orchestrátor
  ezt szó szerint fűzi az `analyze-report.md`-be; az analyzernek a TARTALMI
  ítélet marad (lefedi-e a task a DoD szándékát).

  `## Leltár` — a horgonyzott sorok szövege, a futtatott artefaktumok állapota,
  a hang-gyanús sorok, valamint a 6.b (prózában ígért teszt) és 6.f (destruktív
  művelet) JELÖLTJEI. Ez az analyzerek BEMENETE: nem kell sem a repóban, sem a
  dokumentumokban célpontot keresniük — kapnak egy listát, és ítélnek.

  `analyze/slices/` (SH1, csak `--emit-slices` mellett) — a HÁROM szemantikai
  analyzer-kör (1+3., 2+5., 4. kategória) bemenete, a tervezési dokumentumok
  szó szerinti kimetszéseként. Enélkül a három párhuzamos kör mindegyike a
  teljes négyest olvasná: az eltelt idő csökkenne, a token-költség viszont
  megháromszorozódna. A mappa `.gitignore`-ral rejti magát, tehát a fázis-záró
  commit nem stage-eli.

Amit NEM csinál: nem értelmez ott, ahol ítélet kell (kinek szól egy mondat,
meglévő-e egy szimbólum), és nem javít.

Használat:
  analyze-gate-check.py specs/cycle-NN-<name> [--repo-root .] [--emit-slices]
  analyze-gate-check.py specs/cycle-NN-<name> --report-only   # a hurok lezárásakor

Kilépő kód: 0 = nincs BLOKKOLÓ megállapítás (javaslat és leltár lehet a stdout-on)
            1 = van Must Fix (a `## Must Fix` blokk a stdout-on, gépiesen olvasható)
            2 = használati hiba (hiányzó mappa vagy dokumentum)
"""
import argparse
import re
import sys
from pathlib import Path

from lang_keys import fld, lang, sec, st


PLAN_ID_IN_HEADING_RE = re.compile(r"^#{2,4}\s+.*?\[(P-[A-Za-z0-9][A-Za-z0-9-]*)\]", re.MULTILINE)
PLAN_ID_TOKEN_RE = re.compile(r"\[(P-[A-Za-z0-9][A-Za-z0-9-]*)\]")
BAD_PLAN_ID_RE = re.compile(r"\[(P-[^\]]*)\]")
TASK_LINE_RE = re.compile(r"^\s*-\s*\[[ xX]\]\s+(T[A-Z]*\d+)\b(.*)$")
GROUP_HEADING_RE = re.compile(r"^##\s+(.+)$")
MARKER_RE = re.compile(r"\[(RED|GREEN|CHECK|OPS)\]")
SECTION_REF_RE = re.compile(r"§\s*\d|plan\.md\s*§|plan\s*§")
PARALLEL_RE = re.compile(r"⟂\s*(T[A-Z]*\d+)")
FILE_PATH_RE = re.compile(r"`[^`]*\.[A-Za-z0-9]{1,5}`|\]\(file://[^)]+\)")
DOD_RE = re.compile(r"DoD-(\d+[a-z]?)")
DOD_BULLET_RE = re.compile(r"^\s*-\s*\[[ xX]\]\s*(.+)$")
STATUS_TASK_RE = re.compile(
    r"(állítsd|állítsa|frissítsd|frissítse|váltsd|váltsa).{0,60}"
    r"(státusz|statusz|állapot).{0,40}"
    r"|(spec|plan|tasks)\.md.{0,30}(státusz|statusz).{0,30}(kész|készre)",
    re.IGNORECASE | re.DOTALL,
)

REQUIRED_PLAN_TABLES = [
    (sec("spec_coverage"), "03", "a spec tesztesetei és DoD-pontjai leképezésének táblája (TP1)"),
    (sec("reverse_coverage"), "03", "a plan-képességek spec-forrásának táblája (SC1)"),
    (sec("environment_coords"), "03", "a ciklus konkrét koordinátái: URL-ek, portok, indító parancsok, példa REST hívások, teszt-/API-userek jelszóval, paraméterek (KO1)"),
    (sec("machine_run_table"), "03", "a `run-tests.py` gépi futtatási táblája (TP4) — enélkül a 07-validate a drágább `test-runner` subagentre esik vissza, és a nyers teszt-log LLM-kontextusba kerül"),
]
# A 03a-code-plan lezárásakor kötelező plan-táblák. A `spec_coverage` és a
# `machine_run_table` szándékosan NEM szerepel: azok a 03b-test-plan
# leszállítandói, és a teljes `--plan-only` mód méri őket. Tételesen kiírva
# (nem a REQUIRED_PLAN_TABLES indexeivel), hogy a lista átrendezése ne rontsa
# el némán a kód-oldali kaput.
REQUIRED_PLAN_CODE_TABLES = [
    (sec("reverse_coverage"), "03", "a plan-képességek spec-forrásának táblája (SC1)"),
    (sec("environment_coords"), "03", "a ciklus konkrét koordinátái: URL-ek, portok, indító parancsok, példa REST hívások, teszt-/API-userek jelszóval, paraméterek (KO1)"),
]
REQUIRED_TASKS_TABLES = [
    (sec("plan_coverage"), "04", "a plan-szekció → task fordított tábla (PID1)"),
]


CELL_SPLIT_RE = re.compile(r"(?<!\\)\|")


def split_cells(row_body):
    """Markdown-táblasor cellái. A `\\|` ESCAPE-elt függőleges vonal (tipikusan
    shell-pipe egy parancs-cellában), nem cellahatár — a naiv `split("|")`
    ilyenkor elcsúsztatja az oszlopokat, és a kapu rossz cellát ítél meg."""
    return [c.replace("\\|", "|").strip() for c in CELL_SPLIT_RE.split(row_body)]


class Findings:
    """Megállapítás-gyűjtő. A `must` tételek blokkolnak (exit 1), a `sugg`
    tételek nem; az `inventory` sorok nem megállapítások, hanem az `analyzer`
    subagent BEMENETE — azért készíti a szkript, hogy az analyzernek ne kelljen
    a repóban `Grep`/`Glob`/`Read` köröket futtatnia (AG3)."""

    def __init__(self):
        self.items = []
        self.suggestions = []
        self.inventory = []

    def add(self, code, phase, message):
        self.items.append((code, phase, message))

    def suggest(self, code, phase, message):
        self.suggestions.append((code, phase, message))

    def note(self, kind, message):
        self.inventory.append((kind, message))

    def __len__(self):
        return len(self.items)


def read(path):
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"HIBA: {path} nem olvasható ({exc})", file=sys.stderr)
        sys.exit(2)


def plan_ids(plan_text):
    """A plan címsoraiban kiadott `[P-...]` azonosítók, megjelenési sorrendben."""
    return PLAN_ID_IN_HEADING_RE.findall(plan_text)


def task_lines(tasks_text):
    """(sorszám, task-id, sor) hármasok a tasks.md task-sorairól."""
    out = []
    for lineno, line in enumerate(tasks_text.splitlines(), start=1):
        m = TASK_LINE_RE.match(line)
        if m:
            out.append((lineno, m.group(1), line))
    return out


def check_plan_ids(plan_text, f):
    ids = plan_ids(plan_text)
    seen = {}
    for pid in ids:
        seen[pid] = seen.get(pid, 0) + 1
    for pid, count in seen.items():
        if count > 1:
            f.add("P1", "03", f"a `[{pid}]` plan-azonosító {count} címsorban szerepel — az ID-nak egyedinek kell lennie")
    for raw in BAD_PLAN_ID_RE.findall(plan_text):
        if not re.fullmatch(r"P-[A-Za-z0-9][A-Za-z0-9-]*", raw):
            f.add("P1", "03", f"hibás formátumú plan-azonosító: `[{raw}]` (várt: `[P-NEV]`, nagybetűs, kötőjeles)")
    if not ids:
        f.add("P1", "03", "a plan egyetlen címsora sem visel `[P-...]` azonosítót (PID1) — a tasks.md nem tud rá stabilan hivatkozni")
    return set(ids)


def check_task_references(tasks_text, known_ids, f):
    referenced = set()
    for lineno, tid, line in task_lines(tasks_text):
        refs = PLAN_ID_TOKEN_RE.findall(line)
        if not refs:
            if SECTION_REF_RE.search(line):
                f.add("P5", "04", f"tasks.md:{lineno} `{tid}` sorszámos plan-hivatkozást használ `[P-...]` helyett — a sorszám elcsúszik, ha a plan bővül")
            else:
                f.add("P2", "04", f"tasks.md:{lineno} `{tid}` nem hivatkozik plan-szekcióra (hiányzik a `— plan [P-...]`)")
            continue
        for ref in refs:
            referenced.add(ref)
            if ref not in known_ids:
                f.add("P3", "04", f"tasks.md:{lineno} `{tid}` a `[{ref}]` azonosítóra hivatkozik, ami a plan-ben nem létezik (elgépelés vagy törölt szekció)")
    return referenced


def check_plan_coverage(tasks_text, known_ids, referenced, f):
    """P4 — plan-ID, amire egy task sem hivatkozik. A `Plan-lefedettség` tábla
    említése (indoklással) elfogadható mentesítés."""
    coverage_mentions = set()
    inside = False
    for line in tasks_text.splitlines():
        if line.startswith("## "):
            inside = sec("plan_coverage") in line
            continue
        if inside:
            coverage_mentions.update(PLAN_ID_TOKEN_RE.findall(line))
    for pid in sorted(known_ids - referenced):
        if pid in coverage_mentions:
            continue
        f.add("P4", "04", f"a plan `[{pid}]` szekciójára egyetlen task sem hivatkozik, és a `Plan-lefedettség` tábla sem indokolja meg")


def check_markers(tasks_text, f):
    for lineno, tid, line in task_lines(tasks_text):
        m = MARKER_RE.search(line)
        if not m:
            f.add("T1", "04", f"tasks.md:{lineno} `{tid}` nem visel markert (`[RED]`/`[GREEN]`/`[CHECK]`/`[OPS]`)")
            continue
        if m.group(1) == "OPS" and FILE_PATH_RE.search(line):
            f.add("T2", "04", f"tasks.md:{lineno} `{tid}` `[OPS]` markerrel repo-fájlt szerkeszt — `[RED]`/`[GREEN]` a helyes marker")
        if STATUS_TASK_RE.search(line) and re.search(r"(spec|plan|tasks)\.md", line, re.IGNORECASE):
            f.add("T3", "04", f"tasks.md:{lineno} `{tid}` státusz-frissítő tasknak tűnik — a státusz-életciklus a 07-validate gépezete")


def check_parallel_symmetry(tasks_text, f):
    parallel = {}
    for lineno, tid, line in task_lines(tasks_text):
        peers = PARALLEL_RE.findall(line)
        if peers:
            parallel[tid] = (lineno, set(peers))
    for tid, (lineno, peers) in parallel.items():
        for peer in peers:
            back = parallel.get(peer)
            if back is None or tid not in back[1]:
                f.add("T4", "04", f"tasks.md:{lineno} `{tid} ⟂ {peer}`, de `{peer}` nem jelöli vissza `{tid}`-t — a párhuzamosítás egyoldalú jelölése hibás")


PLACEHOLDER_CURLY_RE = re.compile(r"(?<!\$)\{([A-Za-z][\w-]*)\}")
PLACEHOLDER_ANGLE_RE = re.compile(r"<([A-Za-z][\w.-]*)>")
BACKTICKED_RE = re.compile(r"`([^`]+)`")


def check_task_command_placeholders(tasks_text, f):
    """T5 — kitöltetlen placeholder egy futtatandó task-parancsban.

    A `[CHECK]`/`[OPS]` task parancsát a 06 SZÓ SZERINT adja ki. Ha maradt benne
    `{round}` / `{n}` alakú hely, az ágens kénytelen találgatni: vagy elhasal a
    parancs, vagy egy kitalált útvonalra ír — a bizonyíték pedig nem ott lesz,
    ahol a 07 keresi. A `${VAR}` és a `{a,b}` shell-alak nem placeholder.
    A `<valami>` alak csak javaslat: prózában legitim általános hivatkozás is
    lehet."""
    for lineno, tid, line in task_lines(tasks_text):
        m = MARKER_RE.search(line)
        if not m or m.group(1) not in ("CHECK", "OPS"):
            continue
        seen_curly, seen_angle = set(), set()
        for chunk in BACKTICKED_RE.findall(line):
            if " " not in chunk and "/" not in chunk:
                continue  # rövid azonosító, nem parancs
            for ph in PLACEHOLDER_CURLY_RE.findall(chunk):
                if ph in seen_curly:
                    continue
                seen_curly.add(ph)
                f.add("T5", "04",
                      f"tasks.md:{lineno} `{tid}` parancsában kitöltetlen `{{{ph}}}` placeholder maradt — "
                      f"a `[CHECK]`/`[OPS]` parancsnak szó szerint futtathatónak kell lennie")
            for ph in PLACEHOLDER_ANGLE_RE.findall(chunk):
                if ph in seen_angle:
                    continue
                seen_angle.add(ph)
                f.suggest("T5", "04",
                          f"tasks.md:{lineno} `{tid}` parancsában `<{ph}>` alakú hely szerepel — "
                          f"ha ez kitöltendő placeholder, a 06 találgatni fog; ha valódi shell-szintaxis, hagyd")


def check_dod(spec_text, f):
    inside = False
    numbers = []
    unlabeled = 0
    for line in spec_text.splitlines():
        if line.startswith("## "):
            inside = sec("definition_of_done") in line
            continue
        if not inside:
            continue
        m = DOD_BULLET_RE.match(line)
        if not m:
            continue
        found = DOD_RE.search(m.group(1))
        if found:
            numbers.append(found.group(1))
        else:
            unlabeled += 1
    if unlabeled:
        f.add("D1", "02", f"{unlabeled} DoD-pontnak nincs `DoD-NN` azonosítója — a 07-validate per-item leállító számlálója erre épül")
    seen = {}
    for n in numbers:
        seen[n] = seen.get(n, 0) + 1
    for n, count in sorted(seen.items()):
        if count > 1:
            f.add("D1", "02", f"`DoD-{n}` azonosító {count}-szor szerepel — az azonosítónak egyedinek kell lennie")
    for n in sorted(x for x in seen if not x.isdigit()):
        f.add("D2", "02", f"`DoD-{n}` betűs utótagot visel — utólag beszúrt DoD-pont a KÖVETKEZŐ SZABAD SZÁMOT kapja (DI1), nem `NNb` alakot; a 07 per-item számlálója így marad követhető")


def check_required_tables(text, required, f, doc):
    for title, phase, why in required:
        if title not in text:
            f.add("S1" if doc == "plan.md" else "S2", phase, f"a(z) `{doc}`-ból hiányzik a kötelező `{title}` szekció — {why}")



# ── A1/A2/A3 — a 6. kategória (végrehajthatóság) GÉPIES rétege (AG3) ──────────
# Ezek a checkek korábban az `analyzer` subagentben futottak, `Glob`/`Grep`
# hívások sorozatával: futtatott artefaktumok létezése (6.a), plan-horgonyok
# feloldása (6.g fájl-szintje), artefaktum-hang minták (6.h). Egy teljes
# analyze-futásban ez 20–50 SOROS tool-körfordulót jelentett, futásonként újra
# — miközben mindhárom tisztán fájllétezés- és regex-kérdés. Itt determinisztikus
# és gyakorlatilag ingyenes; az analyzernek csak ÍTÉLNIE kell a leltár alapján.

EXECUTABLE_EXT_RE = re.compile(
    r"(?<![\w./-])((?:[\w.-]+/)*[\w.-]+\.(?:sh|py|mjs|cjs|ps1|bat|sql))(?![\w/])"
)
COMPOSE_RE = re.compile(r"(?<![\w./-])((?:[\w.-]+/)*docker-compose[\w.-]*\.ya?ml)(?![\w/])")
CODE_SPAN_RE = re.compile(r"`([^`\n]+)`")
ANCHOR_RE = re.compile(r"`((?:[\w.-]+/)*[\w.-]+\.[A-Za-z0-9]{1,5}):(\d{1,6})`")
# Kemény padló (AV1): a forma önmagában elég a javaslathoz, tartalom-ítélet nélkül.
VOICE_HARD_RE = re.compile(r"🔴|(?<![\w])TILOS|(?<![\w])Tilos(?![\w])")
# Ítéletet igénylő minták: ezeket csak LELTÁRBA tesszük, a címzett szerint az
# analyzer dönt (a szkript nem tudja, kinek szól a mondat).
VOICE_SOFT_RES = [
    re.compile(r"kötelező ellenőriz", re.IGNORECASE),
    re.compile(r"menj végig", re.IGNORECASE),
    re.compile(r"ne felejtsd el", re.IGNORECASE),
    re.compile(r"SZIGORÚ SZABÁLY"),
    re.compile(r"a minőségellenőrzés bukik", re.IGNORECASE),
]
VOICE_MAX_PER_DOC = 15


def section_text(text, title_substr):
    """Egy `## <cím>` szekció törzse (a következő `## ` címsorig)."""
    out, inside = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = title_substr in line
            continue
        if inside:
            out.append(line)
    return "\n".join(out)


def _candidate_paths(text):
    """Futtatott fájl-jelöltek: csak inline code span-ekből és kódblokkokból
    szedünk útvonalat — a próza szövegében szereplő fájlnév nem parancs."""
    found = []
    for span in CODE_SPAN_RE.findall(text):
        for m in EXECUTABLE_EXT_RE.finditer(span):
            found.append(m.group(1))
        for m in COMPOSE_RE.finditer(span):
            found.append(m.group(1))
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            for m in EXECUTABLE_EXT_RE.finditer(line):
                found.append(m.group(1))
            for m in COMPOSE_RE.finditer(line):
                found.append(m.group(1))
    # sorrend-tartó egyedivé tétel
    seen, out = set(), []
    for x in found:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _resolve(repo_root, rel):
    """Létezik-e a hivatkozott fájl? Előbb pontos útvonal, aztán — ha az
    útvonal csak fájlnév — bárhol a repóban (a plan gyakran nem a gyökérhez
    képest ad meg egy scriptet)."""
    direct = repo_root / rel
    if direct.is_file():
        return direct
    if "/" not in rel:
        for hit in repo_root.glob(f"**/{rel}"):
            parts = set(hit.parts)
            if parts & {".git", "node_modules", "dist", "build", ".venv"}:
                continue
            if hit.is_file():
                return hit
    return None


def check_executed_artifacts(plan_text, tasks_text, repo_root, f, plan_only=False):
    """A1 (6.a) — a `[CHECK]` taskok és a plan `Ellenőrzési stratégia` parancsai
    által FUTTATOTT fájlok léteznek, vagy van rájuk létrehozó lépés?"""
    check_task_text = "\n".join(
        line for _, _, line in task_lines(tasks_text) if "[CHECK]" in line or "[OPS]" in line
    )
    candidates = _candidate_paths(check_task_text)
    for path in _candidate_paths(section_text(plan_text, sec("verification_strategy"))):
        if path not in candidates:
            candidates.append(path)
    if not candidates:
        return
    planned_section = section_text(plan_text, sec("planned_changes"))
    creating_tasks = "\n".join(
        line for _, _, line in task_lines(tasks_text) if "[RED]" in line or "[GREEN]" in line
    )
    for rel in candidates:
        base = rel.rsplit("/", 1)[-1]
        hit = _resolve(repo_root, rel)
        if hit is not None:
            f.note("ARTEFAKTUM", f"`{rel}` → létezik ({hit.as_posix()})")
            continue
        if base in creating_tasks:
            f.note("ARTEFAKTUM", f"`{rel}` → nem létezik, de van létrehozó task")
            continue
        if plan_only and base in planned_section:
            # A 03 lezárásakor még nincs `tasks.md` — a létrehozó taskot a 04 adja,
            # tehát a „nincs rá task" itt nem hiba, csak nyitott szál.
            f.note("ARTEFAKTUM", f"`{rel}` → nem létezik; a plan tervezi, a létrehozó task a 04 dolga")
            continue
        # A plan „tervezi" önmagában NEM elég: task nélkül a fájl nem jön létre.
        # A `Tervezett módosítások`-ban való szereplés csak a CÉLFÁZIST dönti el
        # (04 = a terv megvan, a task hiányzik; 03 = a plan sem tervezi).
        phase = "04" if base in planned_section else "03"
        why = (
            "a plan tervezi a fájlt, de nincs létrehozó task"
            if phase == "04"
            else "sem a repóban nincs meg, sem a plan nem tervezi a létrehozását"
        )
        f.add("A1", phase, f"futtatott artefaktum nem elérhető: `{rel}` — {why} (6.a: a lépés garantáltan bukik)")


def check_plan_anchors(plan_text, repo_root, f, cycle_dir=None):
    """A2 (6.g fájl-szintje) — a plan `path:sor` horgonyai feloldhatók-e, és a
    horgonyzott sor SZÖVEGÉT is kiírjuk: így az analyzer a szimbólum-ítéletet
    (meglévő vs. új) egyetlen tool-hívás nélkül meg tudja hozni."""
    seen = set()
    cycle_dir = cycle_dir or repo_root
    for lineno, line in enumerate(plan_text.splitlines(), start=1):
        for m in ANCHOR_RE.finditer(line):
            rel, num = m.group(1), int(m.group(2))
            key = (rel, num)
            if key in seen:
                continue
            seen.add(key)
            target = repo_root / rel
            if not target.is_file():
                alt = _resolve(repo_root, rel)
                if alt is None and rel.startswith("../"):
                    # Régi konvenció: a horgony a plan.md MAPPÁJÁHOZ képest relatív
                    # (`../../src/app.ts`). Ha így feloldható, a lánc rendben van —
                    # csak a formátum a régi, ezért javaslat, nem Must Fix (RP1).
                    candidate = (cycle_dir / rel).resolve()
                    if candidate.is_file():
                        rel_root = candidate.relative_to(Path.cwd()) if candidate.is_relative_to(Path.cwd()) else candidate
                        f.suggest("A2c", "03", f"plan.md:{lineno} a `{rel}:{num}` horgony a `plan.md` mappájához képest relatív; a kód-hivatkozás a repó gyökeréhez képest relatív legyen (`{rel_root}`) — a parancsok ott futnak, és a kapu is oda oldja fel (RP1)")
                        alt = candidate
                if alt is None:
                    f.add("A2", "03", f"plan.md:{lineno} a `{rel}:{num}` horgony nem oldható fel — a hivatkozott fájl nem létezik")
                    continue
                target = alt
            try:
                lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            if num > len(lines):
                f.suggest("A2b", "03", f"plan.md:{lineno} a `{rel}:{num}` horgony a fájl hosszán ({len(lines)} sor) túl mutat — elavult navigációs hivatkozás")
                continue
            snippet = lines[num - 1].strip()[:100]
            f.note("HORGONY", f"plan.md:{lineno} → `{rel}:{num}` = `{snippet}`")


def check_artifact_voice(docs, f):
    """A3 (6.h) — artefaktum-hang. A KEMÉNY PADLÓ (`🔴`, „Tilos") gépies:
    javaslat, tartalom-ítélet nélkül. A többi minta ítéletet igényel (kinek szól
    a mondat?), ezért csak leltárba kerül, és az analyzer dönt róla."""
    for doc, text, phase in docs:
        hard = soft = 0
        for lineno, line in enumerate(text.splitlines(), start=1):
            if VOICE_HARD_RE.search(line):
                hard += 1
                if hard <= VOICE_MAX_PER_DOC:
                    f.suggest("A3", phase, f"{doc}:{lineno} skill-hangú forma (`🔴` / „Tilos”) — átfogalmazás semleges, leíró hangnemre; a tartalom marad")
                continue
            if any(r.search(line) for r in VOICE_SOFT_RES):
                soft += 1
                if soft <= VOICE_MAX_PER_DOC:
                    f.note("HANG-GYANÚ", f"{doc}:{lineno} `{line.strip()[:90]}` — a CÍMZETT szerint dönts (implementálónak szóló tartalom = rendben)")
        if hard > VOICE_MAX_PER_DOC:
            f.suggest("A3", phase, f"{doc}: további {hard - VOICE_MAX_PER_DOC} kemény-padló találat (nem listázva)")
        if soft > VOICE_MAX_PER_DOC:
            f.note("HANG-GYANÚ", f"{doc}: további {soft - VOICE_MAX_PER_DOC} ítéletet igénylő találat (nem listázva)")


# ── C1–C5 + S3 — a lefedettségi lánc és a maradék gépies ellenőrzés (AG4) ─────
# A lefedettségi mátrix ("melyik DoD-pontot melyik task fedi le") eddig az
# `analyzer` legnagyobb MUNKA- és KIMENETI blokkja volt — miközben tranzitívan
# zárt, tehát gépies:
#
#   DoD-NN (spec)
#     → `Fordított lefedettség` tábla (plan-képesség ↔ spec-forrás)  → [P-…]
#       → task `— plan [P-…]` hivatkozások (tasks.md)                → Tnnn
#
# A lánc gépi zárásához egyetlen formátum-megkötés kell: a `Fordított
# lefedettség` tábla első oszlopa VISELJE a `[P-…]` azonosítót (S3). Ezért a
# szkript ezt is ellenőrzi. Ami marad az analyzernek: a TARTALMI ítélet — a
# megtalált task valóban lefedi-e a DoD-pont szándékát.

HEADING_RE = re.compile(r"^(#{2,4})\s+(.*)$")
TABLE_ROW_RE = re.compile(r"^\s*\|(.+)\|\s*$")
SEPARATOR_ROW_RE = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
PLACEHOLDER_CELL_RE = re.compile(r"^\s*(_.*_|\.\.\.|—|-{1,3}|<.*>)\s*$")
SHELL_ASSIGN_RE = re.compile(r"(?:^|[\s;`(&|])(?:export\s+)?([A-Z][A-Z0-9_]{2,})=")
SHELL_USE_RE = re.compile(r"\$\{?([A-Z][A-Z0-9_]{2,})")
# Környezeti/CI-változók: ezek nem task-ban keletkeznek, ezért a C5 kihagyja őket.
SHELL_ENV_WHITELIST = {"HOME", "PATH", "PWD", "USER", "SHELL", "TMPDIR", "CI"}
TEST_PROMISE_RE = re.compile(
    r"(egységteszttel|unit teszttel|teszttel (?:igazol|ellenőriz|fed)|"
    r"teszt igazolja|tesztel(?:jük|ni fogjuk)|lefedjük teszttel)", re.IGNORECASE
)
DESTRUCTIVE_RE = re.compile(
    r"(?<![\w-])(oc\s+(?:apply|delete|rollout|set)|kubectl\s+(?:apply|delete|rollout|set)|"
    r"docker\s+push|podman\s+push|helm\s+(?:upgrade|uninstall)|"
    r"DELETE\s+FROM|TRUNCATE|DROP\s+(?:TABLE|DATABASE)|flushall|FLUSHALL)",
    re.IGNORECASE,
)
INVENTORY_MAX = 12


def section_body(text, title_substr):
    """Egy címsor (`##`–`####`) törzse a következő, azonos vagy magasabb szintű
    címsorig. A `section_text`-nél általánosabb: a kötelező táblák `###` alatt
    élnek."""
    lines = text.splitlines()
    start = level = None
    for i, line in enumerate(lines):
        m = HEADING_RE.match(line)
        if not m:
            continue
        if start is None:
            if title_substr in m.group(2):
                start, level = i + 1, len(m.group(1))
            continue
        if len(m.group(1)) <= level:
            return "\n".join(lines[start:i])
    if start is None:
        return ""
    return "\n".join(lines[start:])


def table_rows(text, title_substr):
    """Az adott szekció ELSŐ markdown táblájának adatsorai, cellákra bontva.
    A fejlécsort, a szeparátort és a sablon-/példasorokat (dőlt vagy `...`
    cellák) kihagyja — azok a skill sablonjából maradnak vissza, nem adatok."""
    rows, seen_separator = [], False
    for line in section_body(text, title_substr).splitlines():
        m = TABLE_ROW_RE.match(line)
        if not m:
            if rows:
                break  # a tábla véget ért
            continue
        if SEPARATOR_ROW_RE.match(line):
            seen_separator = True
            continue
        if not seen_separator:
            continue  # fejlécsor
        cells = split_cells(m.group(1))
        if cells and all(PLACEHOLDER_CELL_RE.match(c) or not c for c in cells):
            continue  # sablonsor
        rows.append(cells)
    return rows


def table_header(text, title_substr):
    """Az adott szekció ELSŐ markdown táblájának FEJLÉC-cellái.

    A `table_rows` szándékosan kihagyja a fejlécet (adatsorokat ad); a TP4/b
    viszont pont a fejlécet ítéli meg. A fejléc az a táblasor, amelyet
    KÖZVETLENÜL elválasztó sor (`|---|---|…`) követ — ez nyelvfüggetlen.
    Üres lista = nincs felismerhető fejléc."""
    prev = None
    for line in section_body(text, title_substr).splitlines():
        m = TABLE_ROW_RE.match(line)
        if not m:
            prev = None
            continue
        if SEPARATOR_ROW_RE.match(line):
            return split_cells(prev.group(1)) if prev is not None else []
        prev = m
    return []


def heading_id_map(plan_text):
    """A plan `[P-…]` azonosítót viselő címsorainak SZÖVEGE → ID. A `Fordított
    lefedettség` tábla régebbi (a `[P-…]`-szigorítás előtt írt) sorai a szekciót
    címmel vagy sorszámmal nevezik meg (`§3.2 Redis sentinel`); ha a sor szövege
    egy ilyen címsorra illeszkedik, a lánc feloldható, és az `S3` csak formai
    javaslat marad — nem kell egy futó ciklust emiatt visszadobni."""
    out = {}
    for m in re.finditer(r"^#{2,4}\s+(.*?)\[(P-[A-Za-z0-9][A-Za-z0-9-]*)\](.*)$", plan_text, re.MULTILINE):
        title = _normalize_label(m.group(1) + " " + m.group(3))
        if title:
            out[title] = m.group(2)
    return out


def _normalize_label(text):
    """Cím-egyeztetéshez: markup, sorszámozás és többes szóköz nélküli kisbetűs alak."""
    text = re.sub(r"[`*_]", "", text)
    text = re.sub(r"§\s*[\d.]+", " ", text)
    text = re.sub(r"[^0-9a-záéíóöőúüűA-ZÁÉÍÓÖŐÚÜŰ]+", " ", text)
    return " ".join(text.lower().split())


def _resolve_legacy_pid(label, headings):
    """Egy `[P-…]` nélküli tábla-sor feloldása a plan címsoraiból."""
    norm = _normalize_label(label)
    if not norm:
        return None
    for title, pid in headings.items():
        if norm and (norm in title or title in norm):
            return pid
    return None


def table_rows_by_header(text, required_headers):
    """Adatsorok abból a táblából, amelynek FEJLÉCE tartalmazza a megadott
    oszlopneveket. Azért kell a címsor-alapú kereséshez képest külön út, mert
    a `Konfiguráció-életút` (KF1) tábla nem saját címsor alatt él, hanem a
    `Konfiguráció és build változások` szekcióban, dőlt magyarázó szöveg után."""
    rows, in_table, matched = [], False, False
    for line in text.splitlines():
        m = TABLE_ROW_RE.match(line)
        if not m:
            if matched and rows:
                break
            in_table, matched = False, False
            continue
        cells = split_cells(m.group(1))
        if not in_table:
            in_table = True
            header = " ".join(cells).lower()
            matched = all(h.lower() in header for h in required_headers)
            continue
        if SEPARATOR_ROW_RE.match(line) or not matched:
            continue
        if cells and all(PLACEHOLDER_CELL_RE.match(c) or not c for c in cells):
            continue
        rows.append(cells)
    return rows


def dod_ids(spec_text):
    """A spec `Definition of done` szekciójának `DoD-NN` azonosítói, sorrendben."""
    out = []
    for line in section_body(spec_text, sec("definition_of_done")).splitlines():
        m = DOD_BULLET_RE.match(line)
        if not m:
            continue
        found = DOD_RE.search(m.group(1))
        if found and found.group(1) not in out:
            out.append(found.group(1))
    return out


def task_map(tasks_text, known_ids):
    """plan-ID → a rá hivatkozó task-ID-k (megjelenési sorrendben)."""
    mapping = {pid: [] for pid in known_ids}
    for _, tid, line in task_lines(tasks_text):
        for ref in PLAN_ID_TOKEN_RE.findall(line):
            if ref in mapping and tid not in mapping[ref]:
                mapping[ref].append(tid)
    return mapping


def check_coverage_chain(spec_text, plan_text, tasks_text, known_ids, f, plan_only=False):
    """C1/C2/C3 + S3 — a DoD → plan-szekció → task lánc gépi zárása, és a
    generált lefedettségi mátrix (K). A `Must Fix` tételek mellett a mátrixot
    LELTÁRKÉNT adjuk vissza: az orchestrátor ezt fűzi az `analyze-report.md`-be,
    az analyzernek nem kell újra levezetnie."""
    dods = dod_ids(spec_text)
    if not dods:
        return  # a D1 check már jelezte, hogy nincs azonosított DoD-pont

    # S3 — a Fordított lefedettség sorai azonosítsák a plan-szekciót ID-val
    reverse_rows = table_rows(plan_text, sec("reverse_coverage"))
    if not reverse_rows:
        # EGY aggregált megállapítás, nem DoD-onként egy: a gyökérok ugyanaz, és
        # egy 15 DoD-os ciklusban a per-DoD változat 15 azonos tételt szórna a
        # `Must Fix` listába (a fixer ugyanattól a hiánytól kapná meg 15-szer).
        if sec("reverse_coverage") in plan_text:
            f.add("C1", "03", f"a `Fordított lefedettség` tábla üres (vagy csak sablonsorokat tartalmaz) — enélkül a `DoD-NN → [P-…] → task` lefedettségi lánc nem zárható, és a lefedettségi mátrix nem generálható ({len(dods)} DoD-pont érintett)")
        # ha a tábla teljesen hiányzik, azt már az S1 jelezte — ne duplikáljuk
        return

    headings = heading_id_map(plan_text)
    dod_to_pids = {}
    for cells in reverse_rows:
        pids = PLAN_ID_TOKEN_RE.findall(cells[0]) if cells else []
        sources = DOD_RE.findall(cells[1]) if len(cells) > 1 else []
        if not pids:
            label = (cells[0] if cells else "").strip()
            legacy = _resolve_legacy_pid(label, headings)
            short = (label[:60] or "(üres sor)")
            if legacy:
                # A lánc feloldható: a formai hiányt javaslatként jelezzük.
                f.suggest("S3", "03", f"a `Fordított lefedettség` tábla `{short}` sora nem viseli a `[P-…]` azonosítót; a plan címsora alapján `[{legacy}]`-ra oldható fel — írd bele az ID-t, hogy a lefedettségi lánc ne egyezésen múljon (PID1)")
                pids = [legacy]
            else:
                f.add("S3", "03", f"a `Fordított lefedettség` tábla `{short}` sora nem viseli a plan-szekció `[P-…]` azonosítóját, és a plan címsoraiból sem oldható fel — enélkül a DoD → plan → task lefedettségi lánc nem zárható (PID1)")
                continue
        for src in sources:
            dod_to_pids.setdefault(src, []).extend(pids)

    # C3 (TP1) — minden DoD-pont szerepel a Spec-lefedettség tábla 1. oszlopában
    spec_cov_sources = set()
    for cells in table_rows(plan_text, sec("spec_coverage")):
        if cells:
            spec_cov_sources.update(DOD_RE.findall(cells[0]))
    for dod in dods:
        if dod not in spec_cov_sources:
            f.add("C3", "03", f"`DoD-{dod}` nem szerepel a plan `Spec-lefedettség` táblájában (TP1) — ami itt kimarad, azt a `test-runner` nem futtatja le")

    if plan_only:
        # A 03 lezárásakor a lánc plan-oldali fele ellenőrizhető: minden DoD-pontra
        # vezet-e vissza plan-képesség. A task-oldal (C2, mátrix, PID-tábla) a 04-re
        # marad — ott már van mihez hasonlítani.
        for dod in dods:
            if not dod_to_pids.get(dod):
                f.add("C1", "03", f"`DoD-{dod}`-ra egyetlen plan-képesség sem vezet vissza a `Fordított lefedettség` táblában — a plan nem fedi le ezt az elfogadási feltételt")
        return

    # C1/C2 + mátrix
    tmap = task_map(tasks_text, known_ids)
    orphan_ids = {pid for pid in known_ids if not tmap.get(pid)}
    matrix = []
    for dod in dods:
        pids = sorted(set(dod_to_pids.get(dod, [])))
        if not pids:
            f.add("C1", "03", f"`DoD-{dod}`-ra egyetlen plan-képesség sem vezet vissza a `Fordított lefedettség` táblában — a plan nem fedi le ezt az elfogadási feltételt")
            matrix.append((dod, "—", "—", "✗"))
            continue
        tasks, unknown = [], []
        for pid in pids:
            if pid not in known_ids:
                unknown.append(pid)
                continue
            tasks.extend(tmap.get(pid, []))
        if unknown:
            f.add("C1", "03", f"`DoD-{dod}` a `[{', '.join(unknown)}]` azonosítóra vezet vissza, ami a planben nem létező szekció")
        if not tasks:
            # A P4 már jelezte, ha az ID-nak egyáltalán nincs taskja — ott ne duplikáljunk.
            if not all(pid in orphan_ids for pid in pids):
                f.add("C2", "04", f"`DoD-{dod}` lefedő plan-szekciójához (`{', '.join(pids)}`) nincs task")
            matrix.append((dod, ", ".join(f"`[{p}]`" for p in pids), "—", "✗"))
            continue
        matrix.append((dod, ", ".join(f"`[{p}]`" for p in pids), ", ".join(sorted(set(tasks))), "✓"))

    f.note("MÁTRIX-FEJ", f"| DoD | {fld('f_plan_section')} | {fld('f_tasks')} | "
           f"{sec('covered_machine')} |")
    for dod, pids, tasks, ok in matrix:
        f.note("MÁTRIX", f"| `DoD-{dod}` | {pids} | {tasks} | {ok} |")

    # A második kötelező riport-tábla (plan-szekció ↔ task, PID1) ugyanebből az
    # adatból adódik — az orchestrátornak ezt sem kell kézzel összeírnia.
    coverage_mentions = set()
    inside = False
    for line in tasks_text.splitlines():
        if line.startswith("## "):
            inside = sec("plan_coverage") in line
            continue
        if inside:
            coverage_mentions.update(PLAN_ID_TOKEN_RE.findall(line))
    f.note("PID-FEJ", f"| {fld('f_plan_section_id')} | {fld('f_referring_tasks')} | "
           f"{fld('f_ok')} |")
    for pid in known_ids:
        tasks = tmap.get(pid, [])
        if tasks:
            f.note("PID", f"| `[{pid}]` | {', '.join(tasks)} | ✓ |")
        elif pid in coverage_mentions:
            f.note("PID", f"| `[{pid}]` | — (a `Plan-lefedettség` tábla indokolja) | ✓ |")
        else:
            f.note("PID", f"| `[{pid}]` | — | ✗ (lásd P4) |")


def check_config_lifecycle(plan_text, f):
    """C4 (KF1) — a `Konfiguráció-életút` tábla egyetlen cellája sem lehet üres:
    az utolsó oszlop (`Ha hiányzik`) kötelezően fail-fast vagy konkrét default."""
    rows = table_rows(plan_text, sec("config_lifecycle"))
    if not rows:
        rows = table_rows_by_header(plan_text, ["paraméter", "ha hiányzik"])
    for cells in rows:
        param = cells[0] if cells else "(üres sor)"
        empty = [i for i, c in enumerate(cells) if not c]
        if empty:
            f.add("C4", "03", f"a `Konfiguráció-életút` tábla `{param}` sorában {len(empty)} üres cella van (KF1) — az üres cella hiányzó terv: a paraméter valamelyik futtatási módban nem ér el a processzhez")


KO1_PLACEHOLDER_RE = re.compile(
    r"<[^>\n]*(?:ide\s+j|TODO|todo|kitölt|megadni|érték|url|URL|jelszó|password)[^>\n]*>"
    r"|(?<![\w-])(?:TODO|TBD|FIXME|XXX)(?![\w-])"
    r"|(?<![\w-])(?:pl\.\s*)?<\.\.\.>"
)


def check_env_coordinates(plan_text, f):
    """C6 (KO1) — a `Környezeti koordináták` szekció a plan önhordóságának
    alapja: itt él minden konkrét érték (URL, port, indító parancs, példa REST
    hívás, teszt-user + jelszó, paraméter). Két gépies hibája van: placeholder
    az érték helyén, és üres táblacella. Mindkettő azt jelenti, hogy a 04 és a
    `test-runner` egy hiányzó adattal fut neki — ezért blokkol."""
    body = section_body(plan_text, sec("environment_coords"))
    if not body.strip():
        return  # a szekció teljes hiányát az S1 jelezte
    for m in KO1_PLACEHOLDER_RE.finditer(body):
        f.add("C6", "03", f"a `Környezeti koordináták` szekcióban placeholder áll konkrét érték helyett: `{m.group(0)}` (KO1) — a hiányzó adat `plan-questions.md` kérdés, nem placeholder")
    seen_separator = False
    for line in body.splitlines():
        if not TABLE_ROW_RE.match(line):
            seen_separator = False
            continue
        if SEPARATOR_ROW_RE.match(line):
            seen_separator = True
            continue
        if not seen_separator:
            continue  # fejlécsor
        cells = split_cells(TABLE_ROW_RE.match(line).group(1))
        if all(PLACEHOLDER_CELL_RE.match(c) or not c for c in cells):
            continue  # sablon-/példasor
        empty = [i for i, c in enumerate(cells) if not c]
        if empty:
            f.add("C6", "03", f"a `Környezeti koordináták` tábla `{cells[0] or '(üres sor)'}` sorában {len(empty)} üres cella van (KO1) — ami erre a ciklusra nem értelmezhető, oda `—` kerül, üresen nem hagyható")


def check_rollback_state(tasks_text, f):
    """C5 — task-határon átnyúló shell-változó. Ha az egyik task állítja be
    (`VAR=…`), egy másik pedig felhasználja (`$VAR`), akkor a második task
    MÁS shellben fut: a változó üres lesz, és a deploy/rollback parancs
    érvénytelenné válik. Ez a 6.f leggyakrabban átcsúszó esete — és tisztán
    gépies, mert a bizonyíték a két task-ID."""
    assigned, used = {}, {}
    for _, tid, line in task_lines(tasks_text):
        for var in SHELL_ASSIGN_RE.findall(line):
            assigned.setdefault(var, []).append(tid)
        for var in SHELL_USE_RE.findall(line):
            used.setdefault(var, []).append(tid)
    for var, use_tids in used.items():
        if var in SHELL_ENV_WHITELIST or var not in assigned:
            continue
        producers = set(assigned[var])
        for tid in dict.fromkeys(use_tids):
            if tid in producers:
                continue  # ugyanabban a taskban áll be és használódik — rendben
            f.add("C5", "04", f"tasks.md `{tid}` a `${var}` változót használja, de azt a(z) `{', '.join(sorted(producers))}` task állítja be — külön shellben fut, tehát üres lesz; perzisztáld fájlba (pl. `.rollback-state`) vagy vond egy taskba")


def check_judgment_candidates(plan_text, tasks_text, f):
    """LELTÁR — a 6.b (prózában ígért teszt) és 6.f (destruktív művelet)
    JELÖLTJEIT a szkript szedi össze, hogy az analyzer ne szekciókat olvasson
    át célpont keresése végett, hanem egy listát ítéljen meg."""
    promises = 0
    for lineno, line in enumerate(plan_text.splitlines(), start=1):
        if TEST_PROMISE_RE.search(line):
            promises += 1
            if promises <= INVENTORY_MAX:
                f.note("TESZT-ÍGÉRET", f"plan.md:{lineno} `{line.strip()[:110]}` — van hozzá teszteset a `Teszt specifikáció`-ban ÉS task? (6.b)")
    if promises > INVENTORY_MAX:
        f.note("TESZT-ÍGÉRET", f"plan.md: további {promises - INVENTORY_MAX} találat (nem listázva)")

    destructive = 0
    for doc, text in (("plan.md", plan_text), ("tasks.md", tasks_text)):
        for lineno, line in enumerate(text.splitlines(), start=1):
            if DESTRUCTIVE_RE.search(line):
                destructive += 1
                if destructive <= INVENTORY_MAX:
                    f.note("DESZTRUKTÍV", f"{doc}:{lineno} `{line.strip()[:110]}` — jóváhagyás + immutable azonosító + rollback megvan? (6.f)")
    if destructive > INVENTORY_MAX:
        f.note("DESZTRUKTÍV", f"további {destructive - INVENTORY_MAX} találat (nem listázva)")


# ── V1/V2 — csonkítás-mentesség: a spec kidolgozott artefaktumai (KX3) ────────
# A 03 leggyakoribb tartalmi hibája nem a hiányzó terv, hanem hogy a spec-ben
# MÁR kidolgozott artefaktumot (OpenAPI-leíró, teljes payload, hibamátrix,
# többlépéses teszt-forgatókönyv) az ágens „tervvé absztrahálja": összevonja a
# lépéseket, a payloadot mezőnév-listára cseréli, a leírót „a spec részletesen
# definiálja" mondattal helyettesíti. Ez adatvesztés — és mivel a `test-runner`
# a spec-et NEM olvassa, ami itt kimarad, az nem fut le.
#
# Gépiesíthető rész: a spec kód-blokkjainak tartalma megjelenik-e a plan-ben
# (V1), és a plan teszt-szekciója nem zsugorodott-e a specé alá (V2).

FENCE_RE = re.compile(r"^\s*```([A-Za-z0-9_+-]*)\s*$")
CONTRACT_LANGS = {
    "yaml", "yml", "json", "jsonc", "json5", "http", "sql", "ddl", "xml",
    "proto", "graphql", "avsc", "avro", "openapi", "toml", "ini", "env", "dotenv",
}
ALNUM_RUN_RE = re.compile(r"[A-Za-z0-9_]{4,}")
V1_MIN_COVERAGE = 0.6
V1_MAX_ANCHORS = 12
V2_MIN_RATIO = 0.9


def fenced_blocks(text):
    """(nyelv, a tartalmazó címsor, kezdő sorszám, sorok) négyesek a markdown
    kód-blokkjairól."""
    out, lines = [], text.splitlines()
    heading, i = "", 0
    while i < len(lines):
        m = HEADING_RE.match(lines[i])
        if m:
            heading = m.group(2).strip()
            i += 1
            continue
        f = FENCE_RE.match(lines[i])
        if not f:
            i += 1
            continue
        lang, start, body = f.group(1).lower(), i + 1, []
        i += 1
        while i < len(lines) and not FENCE_RE.match(lines[i]):
            body.append(lines[i])
            i += 1
        i += 1
        out.append((lang, heading, start, body))
    return out


def _is_contract_block(lang, body):
    """Szerződés-artefaktum-e a blokk? Csak ezeket kérjük szó szerint: a
    forráskód-részletek (ts/js/java) nem tartoznak ide, azok a 06 dolga."""
    if lang in CONTRACT_LANGS:
        return True
    joined = "\n".join(body)
    if lang in ("bash", "sh", "shell", "console") and "curl" in joined:
        return True
    if not lang:  # jelöletlen blokk: JSON/YAML-szerű?
        if re.search(r'^\s*[{\[]', joined) or re.search(r'^\s*[\w"-]+\s*:\s+\S', joined, re.MULTILINE):
            return True
    return False


def _anchors(body):
    """A blokk jellegzetes sorai, amelyek a plan-ben KERESHETŐK. Rövid,
    szerkezeti sorokat (`{`, `}`, `---`) kihagyunk: azok mindenhol előfordulnak."""
    seen, out = set(), []
    for line in body:
        s = " ".join(line.split())
        if len(s) < 12 or not ALNUM_RUN_RE.search(s):
            continue
        if s in seen:
            continue
        seen.add(s)
        out.append(s)
    return out


def check_spec_artifact_transfer(spec_text, plan_text, f):
    """V1 (KX3) — a spec szerződés-artefaktumai szó szerint átkerültek-e."""
    plan_norm = " ".join(plan_text.split())
    for lang, heading, lineno, body in fenced_blocks(spec_text):
        if "out of scope" in heading.lower():
            continue  # a specben szándékosan kívül hagyott példa
        if not _is_contract_block(lang, body):
            continue
        anchors = _anchors(body)
        if len(anchors) < 3:
            continue  # túl rövid blokk: nincs mit mérni
        sample = anchors[:V1_MAX_ANCHORS]
        missing = [a for a in sample if " ".join(a.split()) not in plan_norm]
        found = len(sample) - len(missing)
        if found / len(sample) >= V1_MIN_COVERAGE:
            if missing:
                f.note("ARTEFAKTUM-ÁTVÉTEL", f"spec.md:{lineno} (`{heading}`, {lang or 'jelöletlen'}) → {found}/{len(sample)} horgony megvan; hiányzik: {missing[0][:70]}")
            continue
        preview = "; ".join(m[:60] for m in missing[:3])
        f.add("V1", "03", f"spec.md:{lineno} — a `{heading}` szekció kidolgozott {lang or 'kód'}-blokkja nem került át a plan-be (a {len(sample)} jellegzetes sorából csak {found} található meg). Hiányzik pl.: {preview}. A `plan.md` önhordó: a `test-runner` a spec-et nem olvassa, ezért a blokkot SZÓ SZERINT, csonkítás nélkül át kell venni (KX3)")


def _content_line_count(text):
    """Érdemi sorok száma: üres sor, vízszintes vonal és tábla-szeparátor nélkül."""
    n = 0
    for line in text.splitlines():
        s = line.strip()
        if not s or set(s) <= set("-|: ") or s.startswith("<!--"):
            continue
        n += 1
    return n


def check_test_section_volume(spec_text, plan_text, f):
    """V2 (KX3) — a plan teszt-szekciója nem lehet kisebb a specénél. A plan
    ugyanazt a tartalmat kapja meg, PLUSZ a végrehajtási részleteket (parancs,
    fixture, környezet-felkészítés), tehát a zsugorodás gyakorlatilag mindig
    összevonást vagy elhagyást jelent."""
    spec_tests = section_body(spec_text, sec("test_specification"))
    if not spec_tests.strip():
        return
    plan_tests = (section_body(plan_text, sec("testing_strategy")) + "\n"
                  + section_body(plan_text, sec("test_specification")))
    s, pl = _content_line_count(spec_tests), _content_line_count(plan_tests)
    if s < 5:
        return  # túl kicsi minta
    if pl < s * V2_MIN_RATIO:
        f.add("V2", "03", f"a plan teszt-szekciói ({pl} érdemi sor) rövidebbek a spec `Teszt specifikáció` szekciójánál ({s} sor) — a plan a spec tartalmát PLUSZ a végrehajtási részleteket (parancs, fixture, környezet-felkészítés) hordozza, tehát a zsugorodás összevonást vagy elhagyást jelent (KX3). Ellenőrizd, hogy minden spec-teszteset minden lépése és elvárt eredménye átkerült-e")
    else:
        f.note("TESZT-TERJEDELEM", f"spec `Teszt specifikáció`: {s} érdemi sor → plan teszt-szekciók: {pl} sor (rendben)")


# ── T1–T6 — teszt-forgatókönyvek a planben (TS1–TS6) ─────────────────────────
# Miért kell: a `plan.md` ÖNHORDÓ (TC1/a) — a `test-runner` és a `bs-manual-test-plan`
# is kizárólag ebből dolgozik. A `Tesztelési stratégia` prózája viszont hagyta, hogy
# a fázis „nagy vonalakban" vegye át a spec teszteseteit: típus + érintett fájl, de
# lépés, hívás és elvárt eredmény nélkül. A V2 ezt nem fogta meg, mert AGGREGÁLT
# sorszámot mér — a gépi tábla és a bootstrapping hosszától az egyes esetek még
# lehettek egymondatosak. A `TS-NN` blokk ugyanaz a forma, amit a kézi tesztterv
# `TG-NN` csoportjai használnak: onnantól a `bs-manual-test-plan` tényleg ÖSSZESZEREL.

# A hatókör-címke (`[local]`/`[remote]`, EV8) OPCIONÁLIS a regexben, mert a régi,
# lezárt ciklusok planjei nem hordozzák (D9) — a meglétét az `EV8` méri, nem a parse.
# A címke NYELVFÜGGETLEN literál (D2): a kör REST-napló-mappájára joinol
# (`rest-logs/<local|remote>/<teszt>/`), és a mappanevek a keretben mindig angolul
# állnak. A kis/nagybetű-tűrés CSAK a címkére szól (`(?i:…)`), a `TS-` prefixre NEM:
# egy `ts-01` fejléc azonosítója a megállapítás-szövegekbe és a TS6 számozásba is
# beszivárogna.
TS_HEADING_RE = re.compile(
    r"^#{3,5}\s*(TS-(\d+))\s*(?:\[(?i:(local|remote))\])?\s*[—–-]\s*(.+?)\s*$")
# A fejléc DoD-hivatkozásai zárójelben: `#### TS-03 — Legacy login  (DoD-02, DoD-05)`
TS_CONCRETE_RE = re.compile(r"`[^`]+`|\d")
# A `Mit tesztelünk` sor tartalmi padlója (TD7): ennél rövidebb nem állítás.
TS_PURPOSE_MIN_CHARS = 45


def parse_ts_blocks(plan_text):
    """A `Teszt-forgatókönyvek` szekció `TS-NN` blokkjai → [{id, num, scope, cim, sorok}].

    A `scope` a fejléc hatókör-címkéje (`"local"` / `"remote"`), címke nélkül `None`.
    SZÁNDÉKOSAN itt születik, ebben az EGY parse-olóban: az `EV8`/`EV9`/`EV10` és a
    `07` oldali `RL2` mind ezt fogyasztja, tehát nincs második címke-értelmező."""
    body = section_body(plan_text, sec("plan_test_scenarios"))
    blocks, cur = [], None
    for line in body.splitlines():
        m = TS_HEADING_RE.match(line.strip())
        if m:
            cur = {"id": m.group(1), "num": int(m.group(2)),
                   "scope": (m.group(3) or "").lower() or None,
                   "cim": m.group(4), "lines": []}
            blocks.append(cur)
            continue
        if cur is not None:
            cur["lines"].append(line)
    return blocks


def _ts_step_rows(lines):
    """A blokk ELSŐ táblájának adatsorai. A sablonsorokat kihagyja."""
    rows, seen_separator = [], False
    for line in lines:
        m = TABLE_ROW_RE.match(line)
        if not m:
            if rows:
                break
            continue
        if SEPARATOR_ROW_RE.match(line):
            seen_separator = True
            continue
        if not seen_separator:
            continue
        cells = split_cells(m.group(1))
        if cells and all(PLACEHOLDER_CELL_RE.match(c) or not c for c in cells):
            continue
        rows.append(cells)
    return rows


def check_test_scenarios(spec_text, plan_text, f):
    """T1–T6 (TS1–TS6) — a plan teszt-forgatókönyvei végrehajtható részletességűek-e."""
    spec_tests = section_body(spec_text, sec("test_specification"))
    relevant = _content_line_count(spec_tests) >= 5
    blocks = parse_ts_blocks(plan_text)

    if not blocks:
        if relevant:
            f.add("TS1", "03", f"a plan `{sec('testing_strategy')}` szekciójában nincs "
                  f"`### {sec('plan_test_scenarios')}` alszekció egyetlen `TS-NN` blokkal sem (TS1) — "
                  "a spec teszt-specifikációja viszont nem üres. A `plan.md` önhordó: a `test-runner` "
                  "és a kézi tesztterv is CSAK ebből dolgozik, ezért minden tesztesetet forgatókönyvként "
                  "kell kifejteni (mit tesztelünk · előfeltétel · lépés-tábla konkrét hívással és "
                  "lépésenkénti elvárt eredménnyel · takarítás)")
        return

    # T6 — azonosítók
    nums = [b["num"] for b in blocks]
    dup = sorted({n for n in nums if nums.count(n) > 1})
    if dup:
        f.add("TS6", "03", f"ismétlődő `TS-NN` azonosító: {', '.join(f'TS-{n:02d}' for n in dup)} (TS6)")
    missing = [n for n in range(1, max(nums) + 1) if n not in nums]
    if missing:
        f.add("TS6", "03", f"hézag a `TS-NN` sorszámozásban: hiányzik "
              f"{', '.join(f'TS-{n:02d}' for n in missing)} (TS6)")

    known_dods = set(dod_ids(spec_text))
    covered = set()

    for b in blocks:
        body = "\n".join(b["lines"])
        # T5 — a fejléc DoD-hivatkozásai
        refs = set(DOD_RE.findall(b["cim"]))
        if not refs:
            f.add("TS5", "03", f"{b['id']} fejlécéből hiányzik a `DoD-NN` hivatkozás (TS5) — "
                  f"a forma: `#### {b['id']} — <név>  (DoD-02, DoD-05)`")
        for r in refs:
            if known_dods and r not in known_dods:
                f.add("TS5", "03", f"{b['id']} nem létező `DoD-{r}`-re hivatkozik (TS5)")
        covered |= refs

        # T2 — kötelező mezők
        for field_key in ("f_what_we_test", "f_prerequisite", "f_cleanup"):
            if f"**{fld(field_key)}:**" not in body:
                f.add("TS2", "03", f"{b['id']}: hiányzó sor: `**{fld(field_key)}:**` (TS2)")

        # T2/TD7 — a `Mit tesztelünk` sor NEM lehet a cím megismétlése: a
        # forgatókönyv célja állításként áll ott, különben egy bukott tesztről
        # nem eldönthető, hogy a kód romlott el vagy a teszt rossz.
        purpose = ""
        for line in b["lines"]:
            m = re.match(r"^\s*\*\*" + re.escape(fld("f_what_we_test")) + r":?\*\*:?\s*(.*)$", line)
            if m:
                purpose = m.group(1).strip()
                break
        if purpose:
            if len(purpose) < TS_PURPOSE_MIN_CHARS or _normalize_label(purpose) == _normalize_label(b["cim"]):
                f.add("TS2", "03", f"{b['id']}: a `{fld('f_what_we_test')}` sor a címet ismétli vagy "
                      f"töredék (`{purpose[:50]}`) — TD7: ide a viselkedés kerül ELDÖNTHETŐ "
                      "ÁLLÍTÁSKÉNT (mit bizonyít a forgatókönyv), és az elfogadási feltétel, "
                      "amit igazol. A téma megnevezése (\u201ekonkurencia-teszt\u201d) nem cél")

        # T4 — placeholder
        for m in KO1_PLACEHOLDER_RE.finditer(body):
            f.add("TS4", "03", f"{b['id']}: placeholder áll konkrét érték helyett: "
                  f"`{m.group(0)}` (TS4) — a hiányzó adat `plan-questions.md` kérdés, nem placeholder")

        # T2/T3 — lépés-tábla
        rows = _ts_step_rows(b["lines"])
        if not rows:
            f.add("TS2", "03", f"{b['id']}: nincs lépés-tábla adatsorral (TS2) — a kötelező "
                  "oszlopok: `#` · lépés · hívás · elvárt eredmény")
            continue
        for row in rows:
            if len(row) < 4:
                f.add("TS2", "03", f"{b['id']}: a lépés-tábla `{row[0] if row else '?'}` sorának "
                      f"{len(row)} oszlopa van a kötelező 4 helyett (TS2)")
                continue
            step, call, expect = row[1], row[2], row[3]
            if not call:
                f.add("TS3", "03", f"{b['id']} / {row[0]}. lépés (`{step[:40]}`): üres a hívás "
                      "oszlop (TS3) — ide a szó szerint futtatható hívás kerül (`curl …`, parancs, "
                      "UI-lépés), nem hivatkozás")
            if not expect:
                f.add("TS3", "03", f"{b['id']} / {row[0]}. lépés (`{step[:40]}`): üres az elvárt "
                      "eredmény oszlop (TS3)")
            elif not TS_CONCRETE_RE.search(expect):
                f.add("TS3", "03", f"{b['id']} / {row[0]}. lépés: az elvárt eredmény nem konkrét "
                      f"(`{expect[:60]}`) — TS3 kemény padlója: legalább egy backtickes érték vagy "
                      "szám (státuszkód, mezőnév, konkrét payload-részlet). A „sikeresen lefut\" "
                      "jellegű megfogalmazás nem ellenőrizhető")

    # T5 — a másik irány
    for d in sorted(known_dods - covered):
        f.add("TS5", "03", f"`DoD-{d}`-hez nem tartozik egyetlen `TS-NN` forgatókönyv sem (TS5) — "
              "vagy vedd fel a lefedő forgatókönyvbe a hivatkozást, vagy írj rá újat")

    steps = sum(len(_ts_step_rows(b["lines"])) for b in blocks)
    valid = covered & known_dods if known_dods else covered
    f.note("TESZT-FORGATÓKÖNYV", f"{len(blocks)} `TS-NN` blokk, összesen {steps} lépés; "
           f"lefedett DoD: {len(valid)}/{len(known_dods) or '?'}")


# ── WY1 — a tervezett módosítás CÉLJA ────────────────────────────────────────
# Miért kell: a `Tervezett módosítások` eddig azt írta le, MI változik. Hogy MIT
# akarunk elérni és MIÉRT, az csak a spec-ben állt — az implementáló, a reviewer
# és a 07 hurok fixere viszont a plan-ből dolgozik. Cél nélkül egy eltérő, de
# helyes megoldásról nem eldönthető, hogy jó-e, és nem eldönthető, mikor van kész
# a változtatás. A cél a spec-ből KÖVETKEZIK (a SC1 tükre): ugyanaz a `DoD-NN`,
# ami ehhez a `[P-…]`-hoz a `Fordított lefedettség` táblában áll.

WY1_MIN_CHARS = 60
# Egy `**Címke:**` alakú mezősor (listajel is állhat előtte).
BOLD_LABEL_RE = re.compile(r"^\s*[-*+]?\s*\*\*\s*([^*]+?)\s*:?\s*\*\*:?\s*(.*)$", re.MULTILINE)


def _pid_sections(plan_text, section_key):
    """Az adott szekció `[P-…]` azonosítót viselő alszekciói → [(id, cím, törzs)]."""
    body = section_body(plan_text, sec(section_key))
    out, cur = [], None
    for line in body.splitlines():
        m = HEADING_RE.match(line)
        if m:
            pid = PLAN_ID_TOKEN_RE.search(m.group(2))
            cur = {"id": pid.group(1), "cim": m.group(2), "lines": []} if pid else None
            if cur:
                out.append(cur)
            continue
        if cur is not None:
            cur["lines"].append(line)
    return out


def check_planned_change_purpose(plan_text, f):
    """WY1 — minden `[P-…]` bejegyzés megmondja, mit akarunk elérni és miért."""
    body = section_body(plan_text, sec("planned_changes"))
    if not body.strip():
        f.add("WY1", "03", f"a `plan.md`-ból hiányzik a kötelező `{sec('planned_changes')}` szekció "
              "(WY1) — a 04 kizárólag ennek a bejegyzéseiből ír taskot, tehát ami nincs itt, "
              "az nem valósul meg. A szekció más néven, saját szerkezetben nem pótolható")
        return
    entries = _pid_sections(plan_text, "planned_changes")
    if not entries:
        f.add("WY1", "03", f"a `{sec('planned_changes')}` szekcióban nincs egyetlen `[P-…]` "
              "azonosítót viselő bejegyzés sem (WY1/PID1) — a tasks.md ezekre hivatkozik, "
              "és a lefedettségi lánc ezeken fut")
        return
    # A mezőnevet SZAVANKÉNT illesztjük, nem szó szerint: a valós planekben a
    # címke gyakran díszített („Cél és üzleti indoklás (miért csináljuk)"), és
    # emiatt egy szó szerinti egyezés hamis hiányt jelentene.
    want = [w for w in re.findall(r"\w+", fld("f_purpose").lower(), re.UNICODE) if len(w) >= 3]
    for e in entries:
        found = None
        for i, line in enumerate(e["lines"]):
            m = BOLD_LABEL_RE.match(line)
            if m and all(w in m.group(1).lower() for w in want):
                rest = m.group(2).strip()
                # A mező tartalma a következő sorokban is folytatódhat (behúzott bekezdés).
                for nxt in e["lines"][i + 1:]:
                    if not nxt.strip() or HEADING_RE.match(nxt) or re.match(r"^\s*[-*+]?\s*\*\*", nxt):
                        break
                    rest += " " + nxt.strip()
                found = rest
                break
        if found is None:
            f.add("WY1", "03", f"a(z) `[{e['id']}]` bejegyzésből hiányzik a "
                  f"`**{fld('f_purpose')}:**` sor (WY1) — a plan azt is megmondja, MIT akarunk "
                  "elérni (a változás UTÁNI viselkedés) és MIÉRT (a megszüntetett hiányosság), "
                  "a spec-forrás megnevezésével (`DoD-NN`). A módosítás megismétlése nem cél")
        elif len(found) < WY1_MIN_CHARS:
            f.add("WY1", "03", f"a(z) `[{e['id']}]` bejegyzés `{fld('f_purpose')}` sora egy "
                  f"töredék (`{found[:50]}`) — WY1: a viselkedés, ami a változás UTÁN igaz lesz, "
                  "PLUSZ a baj, amit megszüntet, PLUSZ a spec-forrás")


# ── TS7 — spec-teszteset → `TS-NN` (a szerkezet-másolás ellen) ───────────────
# Miért kell: egy éles ciklusban a plan a spec teszt-szekciójának SAJÁT
# címsor-szerkezetét hozta át (`Teszteset 0..7`, „REST szekvencia", „Verifikáció"
# felsorolással), a `Teszt-forgatókönyvek` szekció pedig létre sem jött. A TS1
# ezt megfogja — de csak akkor, ha egyetlen `TS-NN` sincs. Ha a fázis ír néhány
# `TS-NN` blokkot ÉS mellette megtartja a spec prózáját, a lefedettségi rés
# láthatatlan marad: a `Spec-lefedettség` tábla `TC-…` azonosítókra mutat, amik
# csak tábla-sorok, nem végrehajtható forgatókönyvek.

TS_REF_RE = re.compile(r"\bTS-(\d+)\b")
# Indoklás, ami miatt egy spec-esethez nem tartozik forgatókönyv (hu + en).
TS7_EXEMPT_WORDS = (
    "nem tesztelhető", "nem automatizálható", "nem automatizalhato", "manuális", "manualis",
    "kézi", "kezi", "not testable", "cannot be tested", "cannot be automated",
    "not automatable", "manual", "n/a",
)


def check_spec_coverage_scenarios(plan_text, f):
    """TS7 — a `Spec-lefedettség` tábla minden sora megnevez egy `TS-NN`-t."""
    blocks = parse_ts_blocks(plan_text)
    if not blocks:
        return  # a TS1 már megállapította, hogy egyetlen forgatókönyv sincs
    known = {b["num"] for b in blocks}
    rows = table_rows(plan_text, sec("spec_coverage"))
    for row in rows:
        if len(row) < 2:
            continue
        source, cell = row[0], row[1]
        refs = [int(n) for n in TS_REF_RE.findall(cell)]
        if refs:
            for n in refs:
                if n not in known:
                    f.add("TS7", "03", f"a `{sec('spec_coverage')}` tábla `{source[:50]}` sora a nem "
                          f"létező `TS-{n:02d}` forgatókönyvre hivatkozik (TS7)")
            continue
        low = cell.lower()
        if any(w in low for w in TS7_EXEMPT_WORDS):
            f.note("TESZT-LEFEDETTSÉG", f"`{source[:50]}`: nincs `TS-NN`, indoklással — `{cell[:60]}`")
            continue
        f.add("TS7", "03", f"a `{sec('spec_coverage')}` tábla `{source[:50]}` sora egyetlen "
              f"`TS-NN` forgatókönyvet sem nevez meg (TS7) — a `TC-…` azonosító csak egy tábla-sor, "
              f"a `TS-NN` a végrehajtható forgatókönyv. Konvertáld a spec esetét `TS-NN` blokká a "
              f"`{sec('plan_test_scenarios')}` szekcióban, vagy írd be a cellába, miért nem "
              "tesztelhető ebben a ciklusban")


# ── TA1 — teszt-artefaktum adatlap ──────────────────────────────────────────
# Miért kell: a tesztfájl megtervezése nem ér véget a tesztesetek felsorolásával.
# Ha nincs kimondva, milyen kerettel készül, milyen PARANCCSAL futtatható
# önmagában, milyen fixture/mock/tesztadat kell hozzá (és hogy az új fájlként
# szerepel-e a Tervezett módosításokban), és melyik teszt-függvény melyik esetet
# fedi, akkor az implementáló találgat: a `[CHECK]` task más állományt futtat,
# mint a terv, vagy a teszt egyedül nem futtatható.

TA1_HEADING_RE = re.compile(r"^#{3,5}\s+.*?`([^`]+\.[A-Za-z0-9]{1,6})`")
TA1_TEST_SECTIONS = ("unit_tests", "integration_tests", "e2e_tests")
TA1_FIELDS = ("f_what_it_checks", "f_test_run", "f_test_fixtures", "f_test_cases")


def _check_tc_table_header(block, f):
    """TD7 — a teszteset-tábla fejlécében ott a `Mit ellenőriz` oszlop."""
    label = fld("f_what_it_checks").lower()
    for line in block["lines"]:
        m = TABLE_ROW_RE.match(line)
        if not m or SEPARATOR_ROW_RE.match(line):
            continue
        cells = [c.lower() for c in split_cells(m.group(1))]
        if not any("tc-id" in c for c in cells):
            continue  # nem teszteset-tábla fejléce
        if not any(label in c for c in cells):
            f.add("TA1", "03", f"a(z) `{block['path']}` teszteset-táblájából hiányzik a "
                  f"`{fld('f_what_it_checks')}` oszlop (TD7) — minden esetnél ki kell mondani, "
                  "milyen viselkedést ellenőriz (állításként, a `DoD-NN`-nel), nem csak a "
                  "bemenetet és az elvárt kimenetet")
        return


def check_test_artifact_datasheet(plan_text, f):
    """TA1 — minden tesztfájl-fejléc alatt ott az adatlap három sora."""
    for key in TA1_TEST_SECTIONS:
        body = section_body(plan_text, sec(key))
        if not body.strip():
            continue
        cur, blocks = None, []
        for line in body.splitlines():
            m = TA1_HEADING_RE.match(line)
            if m:
                cur = {"path": m.group(1), "lines": []}
                blocks.append(cur)
                continue
            if HEADING_RE.match(line):
                cur = None
                continue
            if cur is not None:
                cur["lines"].append(line)
        for b in blocks:
            text = "\n".join(b["lines"])
            labels = [m.group(1).lower() for m in BOLD_LABEL_RE.finditer(text)]
            missing = []
            for k in TA1_FIELDS:
                want_k = [w for w in re.findall(r"\w+", fld(k).lower(), re.UNICODE) if len(w) >= 3]
                if not any(all(w in lab for w in want_k) for lab in labels):
                    missing.append(fld(k))
            _check_tc_table_header(b, f)
            if missing:
                f.add("TA1", "03", f"a(z) `{b['path']}` teszt-artefaktum adatlapjából hiányzik: "
                      + ", ".join(f"`**{name}:**`" for name in missing)
                      + " (TA1) — a keret és az EGY fájlra szűkített, szó szerint futtatható "
                        "parancs, a fixture/mock/tesztadat (útvonallal; ami új, az a "
                      f"`{sec('planned_changes')}`-ban is), és a teszt-függvény → `TC-ID`/`TS-NN` "
                        "leképezés nélkül a tesztet nem lehet a terv alapján megírni és lefuttatni")


# ── TI1/TI2/TX1 — teszt-azonosítók: a plan és a tasks közös névtere ──────────
# Miért kell: a `tasks.md` eddig CSAK a `[P-…]` terv-szekciókra hivatkozott, a
# tesztesetekre semmi — így egy „futtasd a unit teszteket" sorból nem derült ki,
# MELYIK plan-teszteset futott le, és egy bukásnál nem volt per-teszt bizonyíték.
# A plan két azonosító-családot ad (`TS-NN` forgatókönyv, `TC-NN` teszteset), a
# task pedig a `— test [TC-01]` jelöléssel hivatkozik rájuk. A `TX1` azt köti ki,
# hogy egy futtató `[CHECK]` pontosan EGY azonosítót futtasson: a pipa így
# azonosítóhoz kötött állítás lesz, nem gyűjtőnyugta.

TC_ID_RE = re.compile(r"\bTC-(\d+)\b")
TC_LOOSE_RE = re.compile(r"\bTC-([A-Za-z][A-Za-z0-9]*)-(\d+)\b")
TASK_TEST_REF_RE = re.compile(r"[—-]\s*test\s*\[([^\]]+)\]", re.IGNORECASE)
TEST_ID_RE = re.compile(r"\b(T[SC]-\d+)\b")
TEST_SECTION_KEYS = ("unit_tests", "integration_tests", "e2e_tests")


def plan_test_ids(plan_text):
    """A plan teszt-azonosítói: `TS-NN` (forgatókönyvek) + `TC-NN` (teszt-táblák)."""
    ts = [b["id"] for b in parse_ts_blocks(plan_text)]
    tc_nums = []
    for key in TEST_SECTION_KEYS:
        body = section_body(plan_text, sec(key))
        tc_nums += [int(n) for n in TC_ID_RE.findall(body)]
    return ts, sorted(set(tc_nums))


def check_test_ids(plan_text, f):
    """TI1 — a `TC-NN` azonosítók szigorú alakúak, egyediek és hézagmentesek."""
    loose = set()
    for key in TEST_SECTION_KEYS:
        body = section_body(plan_text, sec(key))
        for m in TC_LOOSE_RE.finditer(body):
            loose.add(m.group(0))
    for bad in sorted(loose):
        f.add("TI1", "03", f"a(z) `{bad}` teszt-azonosító nem a kötelező `TC-NN` alakot viseli "
              "(TI1) — a ciklusban EGY folytonos `TC-01`, `TC-02`, … számsor él, modul-tagolás "
              "nélkül: a `tasks.md` és a `07` naplója erre hivatkozik")
    _, tc = plan_test_ids(plan_text)
    if tc:
        missing = [n for n in range(1, max(tc) + 1) if n not in tc]
        if missing:
            f.add("TI1", "03", "hézag a `TC-NN` sorszámozásban: hiányzik "
                  + ", ".join(f"TC-{n:02d}" for n in missing) + " (TI1)")


def check_task_test_refs(plan_text, tasks_text, f):
    """TI2/TX1 — a task teszt-hivatkozásai léteznek, és egy `[CHECK]` egy tesztet futtat."""
    ts_ids, tc_nums = plan_test_ids(plan_text)
    if not ts_ids and not tc_nums:
        return
    known = set(ts_ids) | {f"TC-{n:02d}" for n in tc_nums} | {f"TC-{n}" for n in tc_nums}
    for lineno, tid, line in task_lines(tasks_text):
        m = TASK_TEST_REF_RE.search(line)
        if not m:
            continue
        refs = TEST_ID_RE.findall(m.group(1))
        if not refs:
            f.add("TI2", "04", f"{tid}: a `test [...]` hivatkozás nem tartalmaz érvényes "
                  f"azonosítót (`{m.group(1)[:40]}`) — a forma: `test [TC-01]` vagy `test [TS-03]`")
            continue
        for r in refs:
            norm = r.upper()
            alt = f"{norm[:3]}{int(norm[3:]):02d}" if norm[3:].isdigit() else norm
            if norm not in known and alt not in known:
                f.add("TI2", "04", f"{tid} a nem létező `{r}` teszt-azonosítóra hivatkozik (TI2) — "
                      "a plan `Teszt-forgatókönyvek` szekciójában és a teszt-tábláiban ilyen "
                      "azonosító nincs. Elgépelés, vagy a plan-t kell kiegészíteni")
        if "[CHECK]" in line and len(set(refs)) > 1:
            f.add("TX1", "04", f"{tid} egyetlen `[CHECK]`-ben {len(set(refs))} tesztet futtat "
                  f"({', '.join(sorted(set(refs)))}) — TX1: minden futtatandó teszt KÜLÖN "
                  "checkbox. Így egy bukásnál nem derül ki, melyik teszt bukott, és a pipa nem "
                  "azonosítóhoz kötött állítás. Bontsd külön sorokra, teszt-szűrős paranccsal "
                  "(`-t \"<név>\"`, `-k <minta>`)")


# ── GA1 — kapu-bélyeg a lezárt planben (javaslat) ────────────────────────────
# Miért kell: a `Task írásra kész` státuszt a 03 SAJÁT MAGÁNAK írja be. Egy éles
# ciklusban a plan ezzel a státusszal állt, miközben hét blokkoló megállapítás
# volt benne — a kaput nem futtatta le senki. A bélyeg nem véd a hamisítás
# ellen (a valódi védelem a 04 belépő kapuja, EG1), de láthatóvá teszi a
# kihagyást az embernek is.


def check_gate_stamp(plan_text, f, field="f_gate", status_key="ready_for_tasks",
                     mode="--plan-only"):
    """GA1 — lezárt plan → van-e nyoma a mechanikus kapu futásának.

    A 03 hasítása óta KÉT bélyeg van (D6): a `03a-code-plan` a
    `f_gate_code` mezőt írja a `ready_for_test_plan` státusz mellé, a
    `03b-test-plan` a `f_gate` mezőt a `ready_for_tasks` mellé. A check korán
    visszatér, ha a plan státusza nem a várt — ezért a `status_key`-t is
    paraméterezni KELL, különben `--plan-code-only` módban soha nem mérne
    semmit (a plan ott `ready_for_test_plan` státuszon áll).
    """
    head = "\n".join(plan_text.splitlines()[:20])
    status_m = re.search(r"\*\*" + re.escape(fld("f_status")) + r":\*\*\s*(.+)", head)
    if not status_m or st(status_key).lower() not in status_m.group(1).lower():
        return
    if re.search(r"\*\*" + re.escape(fld(field)) + r"[^*:]*:?\*\*", head):
        return
    f.suggest("GA1", "03", f"a `plan.md` `{st(status_key)}` státuszon áll, de a fejlécében "
              f"nincs `**{fld(field)}:**` bélyeg (GA1) — a státuszt a 03 saját magának írja be, "
              "a kapu tényleges lefutását ez a sor mutatja. A lezáráskor futtatott "
              f"`analyze-gate-check {mode}` összefoglaló sorát kell ide írni")


# ── TT1 — teszt-lefedettség: `TS-NN` / kategória → task ──────────────────────
# Miért kell: a lefedettségi lánc eddig `DoD-NN → [P-…] → task` volt — a tesztek
# NEM voltak benne. Egy éles ciklusban a plan nyolc tesztesetet írt le, a tasks
# lista pedig egyetlen `[RED]` taskba mosta össze őket („tesztfájl megírása 8
# tesztesettel"), a `[CHECK]`-ek meg a teljes suite-ot futtatták. Formailag
# minden lefedett volt, gyakorlatilag egyetlen forgatókönyvet sem lehetett
# visszakeresni. A `Teszt-lefedettség` tábla a hiányzó láncszem.

TT1_EXEMPT_WORDS = (
    "kézi", "kezi", "manuál", "manual", "nem automatizál", "nem automatizal",
    "07", "validate", "run table", "gépi tábla", "gepi tabla", "not automat",
)


def _tt1_expected(plan_text):
    """Amit a tasks.md `Teszt-lefedettség` táblájában el kell számolni."""
    ts_ids, tc_nums = plan_test_ids(plan_text)
    ts = ts_ids + [f"TC-{n:02d}" for n in tc_nums]
    cats = []
    for row in table_rows(plan_text, sec("machine_run_table")):
        cat = (row[0] if row else "").strip().strip("`*")
        if cat and cat.lower() not in ("kategória", "kategoria", "category"):
            cats.append(cat)
    return ts, cats


def check_test_task_coverage(plan_text, tasks_text, f):
    """TT1 — minden `TS-NN` és minden futtatási kategória kap gazdát a tasks.md-ben."""
    ts_ids, cats = _tt1_expected(plan_text)
    if not ts_ids and not cats:
        return  # a plan oldalán a TS1/TP4 már megállapította a hiányt
    body = section_body(tasks_text, sec("test_coverage"))
    if not body.strip():
        f.add("TT1", "04", f"a `tasks.md`-ból hiányzik a kötelező `{sec('test_coverage')}` "
              f"szekció (TT1) — a plan {len(ts_ids)} `TS-NN` forgatókönyvéhez és "
              f"{len(cats)} futtatási kategóriájához meg kell nevezni, melyik task hozza létre "
              "a teszt-artefaktumot és melyik futtatja (vagy indokolni, miért nincs ilyen). "
              "A `Plan-lefedettség` tábla ezt NEM fedi le: az a `[P-…]` szekciókat számolja el, "
              "a teszteseteket nem")
        return
    rows = table_rows(tasks_text, sec("test_coverage"))
    first_cells = [(row[0] if row else "") for row in rows]
    joined = "\n".join(first_cells).lower()
    for tid in ts_ids:
        if tid.lower() not in joined:
            f.add("TT1", "04", f"a `{sec('test_coverage')}` táblából hiányzik a `{tid}` "
                  "forgatókönyv sora (TT1) — melyik task írja meg a teszt-artefaktumát, és "
                  "melyik futtatja? Ha egyik sem (kézi ellenőrzés, vagy a 07 futtatja a gépi "
                  "táblából), az is sor, indoklással")
    for cat in cats:
        if cat.lower() not in joined:
            f.add("TT1", "04", f"a `{sec('test_coverage')}` táblából hiányzik a gépi futtatási "
                  f"tábla `{cat}` kategóriájának sora (TT1)")
    known_tasks = {tid for _, tid, _ in task_lines(tasks_text)}
    task_ref_re = re.compile(r"\b(T(?:REG)?\d+)\b")
    for row in rows:
        if len(row) < 3:
            continue
        name = row[0].strip()
        creator, runner = row[1].strip(), row[2].strip()
        for ref in set(task_ref_re.findall(creator + " " + runner)):
            if known_tasks and ref not in known_tasks:
                f.add("TT1", "04", f"a `{sec('test_coverage')}` tábla `{name[:40]}` sora a nem "
                      f"létező `{ref}` taskra hivatkozik (TT1) — a táblát a tasks lista LEZÁRÁSAKOR "
                      "kell kitölteni, a tényleges task-azonosítókkal")
        note = row[3].strip() if len(row) > 3 else ""
        if is_empty_cell(creator) and is_empty_cell(runner):
            if not note or not any(w in note.lower() for w in TT1_EXEMPT_WORDS):
                f.add("TT1", "04", f"a `{sec('test_coverage')}` tábla `{name[:40]}` sorához sem "
                      "létrehozó, sem futtató task nem tartozik, és a megjegyzés nem mondja meg, "
                      "miért (TT1) — pl. „kézi lépés, a T018 `[OPS]` taskja\" vagy "
                      "„`validate`-fázisú: a 07 futtatja a gépi táblából\"")


# ── T6 — két `[CHECK]` ugyanabba a fájlba ír ─────────────────────────────────
# Miért kell: négy csoport `[CHECK]`-je `npm test > …/implement/unit/tmp.log`
# alakban futott — mindegyik FELÜLÍRTA az előzőt, tehát öt futásból egyetlen log
# maradt bizonyítéknak. A `>` néma adatvesztés: a parancs zöld, a bizonyíték
# eltűnik.

REDIRECT_RE = re.compile(r"(?<!>)>(?!>)\s*([^\s`|;&]+)")


def check_check_output_collisions(tasks_text, f):
    """T6 — két teszt-futtató task nem irányíthat `>`-tal ugyanabba a fájlba."""
    targets = {}
    for lineno, tid, line in task_lines(tasks_text):
        if "[CHECK]" not in line and "[OPS]" not in line:
            continue
        for m in REDIRECT_RE.finditer(line):
            path = m.group(1).strip("`\"'")
            if not path or path.startswith("/dev/"):
                continue
            targets.setdefault(path, []).append(tid)
    for path, ids in targets.items():
        if len(ids) > 1:
            f.add("T6", "04", f"{', '.join(ids)} ugyanabba a fájlba ír `>`-tal (`{path}`) — "
                  "a későbbi futás FELÜLÍRJA a korábbit, tehát a fázis végén egyetlen log marad "
                  "bizonyítéknak. Adj kategóriánként külön fájlt (`…/unit/<modul>.log`), vagy "
                  "használj `>>`-t, ha tényleg egy gyűjtőfájlt akarsz")


# ── TS8 — `.http` alak a REST-forgatókönyvekhez ──────────────────────────────
# Miért kell: a lépés-tábla `Hívás` cellája a GÉPNEK szól (egysoros, futtatható
# `curl`), egy embernek viszont a fejlécekkel és a body-val együtt kell látnia a
# kérést, kattintható alakban. A `bs-manual-test-plan` ezt már megköveteli
# (MG9/MT11) — de ha a plan nem hordozza, a kézi tesztterv nem összeszerel,
# hanem kitalál. Ugyanaz a hívás, két közönségnek.

CURL_RE = re.compile(r"(?<![\w-])curl(?![\w-])")
HTTP_FENCE_RE = re.compile(r"^\s*```+\s*http\s*$", re.IGNORECASE)


def check_ts_http_blocks(plan_text, f):
    """TS8 — ahol `curl` van a forgatókönyvben, ott ```http blokk is (és fordítva)."""
    for b in parse_ts_blocks(plan_text):
        body = "\n".join(b["lines"])
        has_curl = CURL_RE.search(body) is not None
        has_http = any(HTTP_FENCE_RE.match(line) for line in b["lines"])
        if has_curl and not has_http:
            f.add("TS8", "03", f"{b['id']}: van `curl` hívás, de nincs ```http blokk (TS8) — "
                  "a REST-lépéseket a VSCode REST Client / IntelliJ `.http` alakjában is le kell "
                  "írni (ugyanazok az értékek, a lépés számára hivatkozva), különben a hívás "
                  "fejlécei és body-ja csak egysoros parancsba préselve léteznek, és a kézi "
                  "tesztterv (`bs-manual-test-plan`) nem összeszerel, hanem kitalál")
        if has_http and not has_curl:
            f.add("TS8", "03", f"{b['id']}: van ```http blokk, de a lépés-tábla `Hívás` "
                  "celláiban nincs futtatható `curl` (TS8) — a `.http` alak az embernek szól, "
                  "a táblacella a gépnek: a kettő együtt jár")


# ── PH1 — melyik FÁZIS futtatja a kategóriát ─────────────────────────────────
# Miért kell: a gépi tábla eddig csak a kör TÍPUSÁT mondta meg (gyors/nehéz),
# azt nem, hogy melyik FÁZIS futtatja. A `Fázis` oszlop ezt adja meg
# (`implement` / `validate` / `mindkettő`; az üres cella mindkettő — a hallgatás
# soha nem jelent kihagyást). A veszélyes eset az `implement`-only jelölés: a
# `dod-check.py` a VALIDÁLÁSI kör bizonyítékaiból joinol, tehát ami csak a
# 06-ban futott, arról a DoD-nak nincs bizonyítéka.

PH1_IMPLEMENT_WORDS = {"implement", "implementáció", "implementacio", "06"}
PH1_VALIDATE_WORDS = {"validate", "validálás", "validalas", "07"}
PH1_BOTH_WORDS = {"", "—", "-", "n/a", "na", "mindkettő", "mindketto", "both", "mind", "all"}


def _phase_set(value):
    raw = (value or "").strip().lower().strip("`*")
    if raw in PH1_BOTH_WORDS:
        return {"implement", "validate"}, True
    out = set()
    for part in re.split(r"[,;/+ ]+", raw):
        if not part:
            continue
        if part in PH1_IMPLEMENT_WORDS:
            out.add("implement")
        elif part in PH1_VALIDATE_WORDS:
            out.add("validate")
        elif part in PH1_BOTH_WORDS:
            out |= {"implement", "validate"}
        else:
            return set(), False
    return (out or {"implement", "validate"}), True


# ── TP4/b — a gépi futtatási tábla SÉMÁJA ────────────────────────────────────
# Miért kell: az `S1` kapu csak azt nézi, hogy a szekció LÉTEZIK-e. Egy éles
# ciklus táblája `Recept | Kategória | Előfeltétel | Parancs | Időkorlát | …`
# fejléccel készült — átment az S1-en, de a `run-tests.py` FIX OSZLOP-POZÍCIÓKKAL
# olvas, tehát nem hibaüzenetet adott, hanem ROSSZ CELLÁKAT használt: a fejléc
# adatsorként futott volna, az `Eredményfájl` helyén `60s` időkorlát állt. Ezért
# a fázis kézi parancsokra esett vissza — ahol egyetlen `EV` kapu sem fut le, és
# ahonnan egy egész teszt-kategória nyom nélkül eltűnt.
#
# A tábla parserét SZÁNDÉKOSAN nem tesszük „okossá" (fejléc-alapú oszlop-
# felismerés): az elrejtené a hibát — egy idegen sémájú tábla akkor is rossz
# bizonyítékot termelne. A séma KÖTELEZŐ, és ott bukjon, ahol a tábla keletkezik.
#
# Az első hét oszlop neve a `03b` sablonjában LITERÁL (nem token), ezért itt is
# az; az utolsó kettő tokenből jön. A `Kategória`/`Category` szót ugyanúgy
# bilingvis literál-halmazként ismerjük fel, ahogy a `run-tests.py` teszi
# (`HEADER_FIRST_CELL_WORDS`) — egy szótár-kulcs bevezetése a két prompt-fa
# sablonjának átírását is jelentené, az pedig külön munka.
RUN_TABLE_FIRST_COLUMN_WORDS = {"kategória", "kategoria", "category"}
RUN_TABLE_COLUMNS = {
    "hu": ("Kategória", "Típus", "Előfeltétel", "Parancs", "Eredményfájl",
           "Formátum", "Takarítás"),
    "en": ("Category", "Type", "Prerequisite", "Command", "Result file",
           "Format", "Cleanup"),
}
# A `Típus` értékei NYELVFÜGGETLEN literálok: a `run-tests.py` a `--type`
# kapcsolót `gyors`/`nehez` értékekkel veszi, és PREFIX-illesztéssel szűr
# (`r["tipus"].startswith("gyor"/"nehe")`) — az angol prompt-fa is ezt írja elő.
# Ha itt új `status`-kulcsot vezetnénk be (`fast`/`heavy`), a kapu és a futtató
# szétcsúszna: a kapu `fast`-ot követelne, a futtató `gyor` prefixet keresne, és
# EGYETLEN kategóriát sem választana ki. Ezért: prefix-illesztés, pontosan úgy,
# ahogy a futtató.
RUN_TABLE_TYPE_PREFIXES = ("gyor", "neh")
DURATION_CELL_RE = re.compile(r"^\d+(?:[.,]\d+)?\s*(?:s|m|h|mp|perc|sec|min|ms)$", re.IGNORECASE)


def _run_table_schema_text():
    cols = RUN_TABLE_COLUMNS.get(lang() or "hu", RUN_TABLE_COLUMNS["hu"])
    return " · ".join(cols + (fld("f_environment"), fld("f_phase")))


def check_run_table_schema(plan_text, f):
    """TP4/b — a gépi futtatási tábla oszlopai a keret SÉMÁJÁT követik-e.

    Három, egymástól független megállapítás:
      1. a fejléc első cellája a `Kategória` (eltolt tábla → minden cella
         rossz mezőbe kerül a `run-tests.py`-ban);
      2. a `Típus` oszlop értéke `gyors`/`nehéz` (ez dönti el, mi fut a
         könnyű körben — VD10);
      3. az `Eredményfájl` oszlopban útvonal áll, nem időtartam.
    """
    header = table_header(plan_text, sec("machine_run_table"))
    rows = table_rows(plan_text, sec("machine_run_table"))
    if not header and not rows:
        return                      # nincs tábla — azt az S1 méri

    schema = _run_table_schema_text()

    # (1) fejléc-cella
    first = (header[0] if header else "").strip().strip("`*_").lower()
    if header and first not in RUN_TABLE_FIRST_COLUMN_WORDS:
        f.add("TP4/b", "03",
              f"a `{sec('machine_run_table')}` első oszlopa nem a `Kategória` "
              f"(`{header[0][:30]}`) — a `run-tests.py` FIX oszlop-pozíciókkal olvas, "
              f"tehát az eltolt tábla minden celláját rossz mezőbe teszi (a parancs "
              f"helyére időkorlát, az eredményfájl helyére környezet kerül), és a fázis "
              f"kézi parancsokra esik vissza, ahol egyetlen `EV` kapu sem fut le. "
              f"A kötelező oszlop-sorrend: {schema} (az utolsó kettő opcionális)")

    # (2) Típus-oszlop és (3) Eredményfájl-oszlop
    bad_types, bad_results, empty_types = [], [], []
    for row in rows:
        cat = (row[0] if row else "") or "(névtelen)"
        tipus = (row[1] if len(row) > 1 else "").strip().strip("`*_").lower()
        if is_empty_cell(tipus):
            empty_types.append(cat)
        elif not tipus.startswith(RUN_TABLE_TYPE_PREFIXES):
            bad_types.append(f"`{cat}` → `{tipus[:20]}`")
        eredmeny = (row[4] if len(row) > 4 else "").strip().strip("`*_")
        if is_empty_cell(eredmeny):
            continue
        if DURATION_CELL_RE.match(eredmeny):
            bad_results.append(f"`{cat}` → `{eredmeny}`")
        elif "/" not in eredmeny and "." not in eredmeny:
            bad_results.append(f"`{cat}` → `{eredmeny[:20]}`")

    if bad_types:
        f.add("TP4/b", "03",
              f"a `{sec('machine_run_table')}` `Típus` oszlopa csak `gyors` vagy `nehéz` "
              f"lehet — ez dönti el, mi fut a könnyű körben (VD10), és a `run-tests.py` "
              f"`--type` szűrője erre a két szó-prefixre illeszt. Eltérő érték: "
              + ", ".join(bad_types[:6])
              + f". A kategória NEVE az első oszlopba való. Kötelező sorrend: {schema}")
    if empty_types:
        f.suggest("TP4/b", "03",
                  f"a `{sec('machine_run_table')}` `Típus` cellája üres: "
                  + ", ".join(f"`{c}`" for c in empty_types[:6])
                  + " — az üres típus egyik `--type` szűrőre sem illeszkedik, tehát a "
                    "kategória sem a könnyű, sem a nehéz körben nem indul el")
    if bad_results:
        f.add("TP4/b", "03",
              f"a `{sec('machine_run_table')}` `Eredményfájl` oszlopában nem útvonal áll: "
              + ", ".join(bad_results[:6])
              + " (TP4/b) — a tábla oszlopai eltolódtak. A `run-tests.py` ezt a cellát "
                "fájlként nyitná meg, és a darabszámok kinyerése NÉMÁN elbukna: a "
                "`results.json`-ba `nem sikerült darabszámot kinyerni — csak a kilépő kód "
                "áll rendelkezésre (TR1 gyenge bizonyíték)` kerülne. Az oszlop értéke "
                f"útvonal vagy `—`. Kötelező sorrend: {schema}")


def check_run_table_phase(plan_text, f):
    """PH1 — a `Fázis` oszlop értékei érvényesek, és marad mit futtatni a 07-ben."""
    rows = table_rows(plan_text, sec("machine_run_table"))
    if not rows:
        return
    validate_rows = []
    for row in rows:
        cat = row[0] if row else "(névtelen)"
        cell = row[8] if len(row) > 8 else ""
        phases, ok = _phase_set(cell)
        if not ok:
            f.add("PH1", "03", f"a gépi futtatási tábla `{cat}` sorának `{fld('f_phase')}` "
                  f"értéke ismeretlen (`{cell[:30]}`) — a három megengedett érték: "
                  f"`{st('phase_implement')}`, `{st('phase_validate')}`, `{st('phase_both')}` "
                  "(az üres cella mindkettőt jelenti)")
            continue
        if "validate" in phases:
            validate_rows.append(cat)
        elif (row[1] if len(row) > 1 else "").lower().startswith("neh"):
            f.suggest("PH1", "03", f"a `{cat}` kategória `nehéz` típusú, mégis csak a "
                      f"`{st('phase_implement')}` fázisban fut — a nehéz teszt (E2E/regresszió) "
                      "bizonyítéka jellemzően a validálási körbe kell")
    if not validate_rows:
        f.add("PH1", "03", f"a gépi futtatási tábla egyetlen kategóriája sem fut a "
              f"`{st('phase_validate')}` fázisban (PH1) — a `07` így nem futtat egyetlen tesztet "
              f"sem, és a `dod-check.py` a validálási kör bizonyítékaiból joinol: minden "
              f"`DoD-NN` bizonyíték nélkül maradna. Legalább egy kategória legyen "
              f"`{st('phase_validate')}` vagy `{st('phase_both')}`")


# ── EV1–EV5 — teszt-cél környezet (EV) ────────────────────────────────────────
# Miért kell: egy éles ciklus a dev környezetre telepített, a tesztjei viszont
# LOKÁLIS célpontra futottak — egy `test:playwright:dev-e2e` nevű npm-script
# configjában `baseURL: "http://127.0.0.1:5178"` állt. Minden teszt zöld lett,
# és így nem derült ki, hogy a dev-re telepített komponens el sem indult.
# A zöld teszt önmagában NEM bizonyítja, HOL volt zöld: a JUnit XML és az Allure
# riport nem rögzíti a megcélzott hostot. Három dolgot kell kimondatni és mérni:
# a ciklus cél-környezetét, kategóriánként a futás környezetét, és azt, hogy a
# nem-lokális cél a PARANCSBAN legyen látható (ne konfigfájlban rejtve), egy
# elérhetőségi probe-bal az `Előfeltétel` oszlopban.

LOCAL_HOST_RE = re.compile(r"\b(?:localhost|127\.0\.0\.1|0\.0\.0\.0|\[::1\])\b")
REMOTE_URL_RE = re.compile(r"https?://([A-Za-z0-9.\-]+)(?::\d+)?")
LOCAL_ENV_WORDS = {"lokális", "lokalis", "local", "localhost", "helyi", "—", "-", "n/a", "na"}
EMPTY_CELL_VALUES = {"", "-", "–", "—", "n/a", "na", "nincs", "none"}


def is_empty_cell(value):
    return (value or "").strip().strip("`").lower() in EMPTY_CELL_VALUES


def _env_is_local(value):
    v = (value or "").strip().lower().strip("`*")
    return bool(v) and all(w in LOCAL_ENV_WORDS for w in re.split(r"[,;/+ ]+", v) if w)


def _remote_hosts(text):
    """A szövegben szereplő NEM lokális hostok."""
    return {h for h in REMOTE_URL_RE.findall(text or "")
            if not LOCAL_HOST_RE.search(h)}


def _target_env(plan_text):
    """(a ciklus cél-környezetének SZÖVEGE, kizárólag lokális-e).

    Az `EV1` és az `EV9` UGYANEZT a mezőt olvassa; két külön kiolvasás csendben
    szétcsúszna (az egyik `**Cél-környezet:**`-et keresne, a másik valami mást),
    és a két kapu ellentmondó ítéletet adna ugyanarra a planre."""
    coords = section_body(plan_text, sec("environment_coords"))
    m = re.search(r"\*\*" + re.escape(fld("f_target_env")) + r":\*\*\s*(.+)", coords or "")
    target = (m.group(1).strip() if m else "")
    return target, (_env_is_local(target) if target else False)


def check_target_environment(plan_text, f, code_only=False):
    """EV1–EV5 — a teszt tényleg ott fut-e, ahova a ciklus szól.

    `code_only=True` (03a-code-plan lezárása) esetén CSAK az `EV1` ág fut: a
    `**<field:f_target_env>:**` mező megléte és kitöltöttsége. Az `EV2`–`EV5`
    a gépi futtatási táblát méri, az pedig a `03b-test-plan` leszállítandója —
    ott a teljes `--plan-only` mód méri.
    """
    coords = section_body(plan_text, sec("environment_coords"))
    target, target_is_local_only = _target_env(plan_text)
    if not target:
        f.add("EV1", "03", f"a `{sec('environment_coords')}` szekcióból hiányzik a "
              f"`**{fld('f_target_env')}:**` mező (EV1) — ki kell mondani, MELY környezetre szól "
              "ez a ciklus (pl. `lokális`, `remote`, `lokális + remote`). Enélkül semmi nem köti a "
              "teszt-célpontot a ciklus szándékához: egy zöld futás nem bizonyítja, HOL volt zöld")
    if code_only:
        return
    known_remote = _remote_hosts(coords)

    rows = table_rows(plan_text, sec("machine_run_table"))
    for row in rows:
        cat = row[0] if row else "(névtelen)"
        env = row[7] if len(row) > 7 else ""
        pre = row[2] if len(row) > 2 else ""
        cmd = row[3] if len(row) > 3 else ""
        if not env.strip():
            f.add("EV2", "03", f"a gépi futtatási tábla `{cat}` sorából hiányzik a "
                  f"`{fld('f_environment')}` oszlop értéke (EV2) — minden kategória mondja meg, "
                  "hol fut (`lokális` / `remote`). A `run-tests.py` ezt naplózza a "
                  "kör bizonyítékába")
            continue
        if _env_is_local(env):
            continue

        # EV3 — a cél legyen a parancsban, ne konfigfájlba rejtve
        cmd_hosts = _remote_hosts(cmd)
        if not cmd_hosts:
            f.add("EV3", "03", f"a gépi futtatási tábla `{cat}` sora `{env}` környezetet deklarál, "
                  "de a parancsban nincs egyetlen nem-lokális host sem (EV3) — a célpontot a "
                  "PARANCSBAN kell láthatóvá tenni (env-változóval vagy kapcsolóval, pl. "
                  "`PLAYWRIGHT_BASE_URL=https://…`), nem egy konfigfájlba rejtve. Egy "
                  "`…:remote-e2e` nevű script configjában simán állhat `localhost` — a név nem bizonyíték")
        elif known_remote and not (cmd_hosts & known_remote):
            f.suggest("EV3", "03", f"a `{cat}` parancsának hostja ({', '.join(sorted(cmd_hosts))}) "
                      f"nem szerepel a `{sec('environment_coords')}` szekcióban — ellenőrizd, hogy "
                      "a célpont tényleg a ciklus koordinátái közül való")

        # EV5 — lokális host egy nem-lokális kategóriában
        if LOCAL_HOST_RE.search(cmd):
            f.add("EV5", "03", f"a gépi futtatási tábla `{cat}` sora `{env}` környezetet deklarál, "
                  f"de a parancsa lokális címre mutat (`{LOCAL_HOST_RE.search(cmd).group(0)}`) — EV5. "
                  "Ez pontosan az a hibaosztály, ahol minden teszt zöld lesz, miközben a telepített "
                  "komponenst senki nem szólította meg")

        # EV4 — elérhetőségi probe
        if is_empty_cell(pre):
            f.add("EV4", "03", f"a `{cat}` kategória `{env}` környezetben fut, de nincs "
                  f"`{fld('f_prerequisite')}` (EV4) — nem-lokális célnál kötelező egy "
                  "elérhetőségi probe a cél health/verzió végpontjára (pl. "
                  "`curl -fsS https://…/health`). A `run-tests.py` az előfeltételt futtatja, és "
                  "bukásakor a kategória FAIL: így egy le sem futó deploy nem tud zöldre pipálódni")
        elif cmd_hosts and not (_remote_hosts(pre) & cmd_hosts):
            f.add("EV4", "03", f"a `{cat}` kategória előfeltétele nem a parancs cél-hostjára hív "
                  f"({', '.join(sorted(cmd_hosts))}) — EV4. A probe-nak UGYANAZT a célt kell "
                  "ellenőriznie, amit a teszt megszólít, különben nem bizonyít semmit")

    # EV5 — a TS-NN forgatókönyvek hívásai
    if target and not target_is_local_only:
        for b in parse_ts_blocks(plan_text):
            for row in _ts_step_rows(b["lines"]):
                call = row[2] if len(row) > 2 else ""
                m = LOCAL_HOST_RE.search(call)
                if m and not re.search(r"\b(?:lokális|lokalis|local)\b", b["cim"], re.IGNORECASE):
                    f.add("EV5", "03", f"{b['id']} / {row[0]}. lépés lokális címre hív "
                          f"(`{m.group(0)}`), miközben a ciklus cél-környezete `{target}` (EV5) — "
                          "ha ez szándékosan lokális forgatókönyv, írd bele a nevébe")

    if rows:
        envs = sorted({(r[7] if len(r) > 7 else "—").strip() or "—" for r in rows})
        f.note("TESZT-KÖRNYEZET", f"cél-környezet: `{target or '—'}`; "
               f"a futtatási tábla környezetei: {', '.join(f'`{e}`' for e in envs)}")


# ── EV8–EV10 — a forgatókönyv megmondja, HOL fut ──────────────────────────────
# Miért kell: az `EV1`–`EV6` bizonyítéka KATEGÓRIA-szemcsés — a `results.json` a
# DEKLARÁLT környezetet írja, a JUnit XML hostot nem rögzít. Azt, hogy egy KONKRÉT
# forgatókönyv hol futott, semmi nem mondta meg. Egy éles ciklusban ezért fordulhatott
# elő, hogy a remote (OpenShift) cél-környezetre szóló ciklust nyolc lokális teszt
# igazolta, és minden kapu zöld maradt: a hiány ott HIÁNY-állítás („nincs remote
# teszt"), amit egy LLM-review szerkezetileg rosszul lát.
#
# A feloldás kettéválasztja a SZÁNDÉKOT és a BIZONYÍTÉKOT: a `TS-NN` fejléce
# `[local]`/`[remote]` címkét kap (szándék — ez a három check méri), a REST-napló
# pedig teszt-szerinti almappába megy (bizonyíték — azt a `07` `RL1`/`RL2`-je méri).
# Az érték a kettő JOINJÁBAN van: egy `[remote]`-nak jelölt teszt, amelynek naplói
# `local/` alá kerültek, önellentmondás.
#
# A címke NYELVFÜGGETLEN literál (`[local]`/`[remote]`), nem projekt-nyelvi status-kulcs: a
# kör REST-napló-mappájára joinol (`rest-logs/<local|remote>/<teszt>/`), és a
# mappanevek a keretben mindig angolul állnak. Projekt-nyelvi címke mellé fordítási
# réteg kellene a kapuban ÉS a naplózó fixture-ben — a kettő csendben szétcsúszna.
#
# A HALLGATÁS itt `local`-t jelent, és ez SZÁNDÉKOS eltérés a `PH1`-től (ott az üres
# cella „mindkettő", mert ott a hallgatás KIHAGYÁST okozna). Ha a hallgatás `remote`
# lenne, minden unit-teszt remote bizonyítékot követelne, és a kapu használhatatlan
# volna. A biztonságot nem a default adja, hanem az `EV8` (a fejléc KÖTELEZŐEN jelölt)
# és az `EV9` (remote ciklusban KELL remote forgatókönyv).

# `REMOTE-N/A: <indok>` — az `EV9` felmentése. KULCS NÉLKÜLI, EGÉSZ CIKLUSRA szóló sor,
# ezért nem a `<PREFIX>: <kulcs> — <indok>` alakú felmentés-parser (`_exemptions`) mintája.
REMOTE_NA_RE = re.compile(r"^\s*REMOTE-N/A:\s*(\S.*)$", re.MULTILINE)


def check_scenario_scope(plan_text, f):
    """EV8–EV10 — a `TS-NN` fejléce megmondja-e, hol fut, és van-e remote teszt.

    `EV8`  — minden `TS-NN` fejléce hordoz `[local]` vagy `[remote]` címkét;
    `EV9`  — nem-lokális cél-környezetű ciklusban van legalább egy `[remote]`;
    `EV10` — ha van `[remote]` forgatókönyv, a gépi táblában van nem-lokális kategória.

    Ha a planban egyetlen `TS-NN` blokk sincs, a check KIMARAD: a hiányukat a `TS1`
    méri, és egy régi, lezárt ciklust bukató kapu használhatatlan.
    """
    blocks = parse_ts_blocks(plan_text)
    if not blocks:
        return

    # ── EV8 — a címke megléte ────────────────────────────────────────────────
    unlabelled = [b for b in blocks if not b["scope"]]
    for b in unlabelled:
        f.add("EV8", "03", f"a(z) {b['id']} forgatókönyv fejlécéből hiányzik a hatókör-címke "
              f"(EV8) — a forma: `#### {b['id']} [local] — …` vagy `[remote]` (nyelvfüggetlen "
              "literál). A címke mondja meg, HOL fut a forgatókönyv, és a `07` kapuja ebből "
              "joinol a kör REST-naplóira (`rest-logs/<local|remote>/<teszt>/`). `remote` minden "
              "olyan futás, amely akár EGYETLEN olyan komponenst is hív, ami nem a lokális gépen "
              "fut — a saját gépen futó konténer még `local`. **A cím önmagában nem dönt:** egy "
              "`oc port-forward` mögötti `127.0.0.1:8080` **remote**, egy compose service-név "
              "(`http://keycloak:8080`) pedig **local**")

    remote_blocks = [b for b in blocks if b["scope"] == "remote"]

    # ── EV9 — remote ciklusban van remote teszt ──────────────────────────────
    target, target_is_local_only = _target_env(plan_text)
    if target and not target_is_local_only and not remote_blocks:
        # A felmentés a `Tesztelési stratégia` szekcióban áll (a `Teszt-forgatókönyvek`
        # annak alszekciója, tehát a szekció-törzs mindkettőt lefedi).
        na = REMOTE_NA_RE.search(section_body(plan_text, sec("testing_strategy")) or "")
        message = (f"a ciklus cél-környezete `{target}` (nem kizárólag lokális), de a plan "
                   f"egyetlen `[remote]` forgatókönyvet sem tartalmaz (EV9) — a "
                   f"`{sec('plan_test_scenarios')}` mind a {len(blocks)} forgatókönyve `local` "
                   "(vagy címkézetlen, ami `local`-t jelent). Egy remote környezetre szóló "
                   "ciklus, amelyet csak lokális tesztek igazolnak, pontosan azt NEM bizonyítja, "
                   "amiért készült: hogy a TELEPÍTETT komponens működik. Írj legalább egy "
                   "`[remote]` forgatókönyvet — vagy ha ebben a ciklusban tényleg nincs értelme, "
                   f"indokold `REMOTE-N/A: <miért>` sorral a `{sec('testing_strategy')}` szekcióban")
        if na:
            f.suggest("EV9", "03", message + f". Felmentve: `REMOTE-N/A: {na.group(1).strip()}`")
        else:
            f.add("EV9", "03", message)

    # ── EV10 — a címke és a gépi tábla nem mondhat ellent ────────────────────
    # A join SZÁNDÉKOSAN durva: a forgatókönyv → kategória hozzárendelés a planben
    # nem explicit (a `TS-NN` nem nevezi meg a kategóriáját), és egy parancs-egyeztetésre
    # épülő, finomabb join törékeny lenne — a `TP4/b` tanulsága szerint egy törékeny
    # kapu rosszabb, mint egy durva.
    rows = table_rows(plan_text, sec("machine_run_table"))
    envs = [(row[7] if len(row) > 7 else "") for row in rows]
    if remote_blocks and envs and all(_env_is_local(e) for e in envs):
        f.add("EV10", "03", f"a plan {len(remote_blocks)} `[remote]` forgatókönyvet ír le "
              f"({', '.join(b['id'] for b in remote_blocks)}), de a "
              f"`{sec('machine_run_table')}` MINDEN kategóriájának "
              f"`{fld('f_environment')}` cellája lokális (EV10) — így a remote forgatókönyvet "
              "SEMMI nem futtatja le remote célpont ellen. Vagy a forgatókönyv címkéje téves, "
              "vagy hiányzik a nem-lokális kategória a táblából")

    if not unlabelled:
        f.note("TESZT-HATÓKÖR", f"{len(blocks)} `TS-NN` forgatókönyv címkézve: "
               f"{len(remote_blocks)} `[remote]`, {len(blocks) - len(remote_blocks)} `[local]`")


# ── R1 — útvonal-formátum (RP1) ───────────────────────────────────────────────
# A tervezési dokumentumokban a kód-/fájl-hivatkozás a REPÓ GYÖKERÉHEZ képest
# relatív (a parancsok ott futnak, és a kapu is oda oldja fel a horgonyokat), a
# dokumentum-link pedig a fájl saját könyvtárához képest. Abszolút, gép-specifikus
# és `file://` útvonal egyik esetben sem érvényes: más gépen és CI-ben értelmetlen.
# Ez a check csak a BIZTOSAN hibás alakokat jelzi — az endpoint-útvonalakat
# (`/api/v1/...`) és a konténer-belső útvonalakat nem bántja.

FILE_URI_RE = re.compile(r"file:///?[^\s`\)\]]+")
# Gép-specifikus gyökerek. Szándékosan NEM szerepel köztük a `/root/`, `/opt/`,
# `/workspace/`, `/srv/`: azok egy `docker exec`/`kubectl` parancsban jogos
# KONTÉNER-BELSŐ útvonalak lehetnek, és ez a minta kódblokkon belül is fut.
# Ami ezeken kívül esik (pl. a repó `/opt/projects/...` alatt), azt a
# repó-gyökér abszolút alakjának keresése fogja meg — lásd `repo_root_variants`.
MACHINE_PATH_RE = re.compile(
    r"(?<![\w.])(?:"
    r"/home/[\w.-]+"
    r"|/Users/[\w.-]+"
    r"|/mnt/[a-z]/[\w.-]+"
    r"|/cygdrive/[a-z]/[\w.-]+"
    r"|/c/Users/[\w.-]+"
    r"|[A-Za-z]:[\\/]{1,2}[\w.-]+"      # bármely Windows meghajtó-útvonal (C:\dev\…, D:/projects/…)
    r")[^\s`\)\]\|]*"
)
PLACEHOLDER_PATH_RE = re.compile(r"(?<![\w.])(?:/path/to/|<projekt>/|<project>/|/абс)[^\s`\)\]\|]*")
MD_ABS_LINK_RE = re.compile(r"\]\((/[^)\s]*|file://[^)\s]*|[A-Za-z]:[\\/][^)\s]*)\)")
ABS_REPO_PATH_RE = re.compile(r"(?<![\w.:/])/((?:[\w.-]+/)+[\w.-]+\.[A-Za-z0-9]{1,5})(?![\w/])")
R1_MAX_PER_DOC = 10


def repo_root_variants(repo_root):
    """A repó gyökerének abszolút alakjai (posix + Windows backslash). Ha egy
    tervezési dokumentum ezt tartalmazza, az BIZTOSAN hibás: gép-specifikus, és
    a hivatkozás relatív alakja triviálisan előáll belőle. Ez a check független
    a `MACHINE_PATH_RE` prefix-listájától, tehát bármilyen mappaszerkezetnél
    (pl. `/opt/projects/…`, `/data/repos/…`) is fog."""
    try:
        absolute = repo_root.resolve()
    except OSError:
        return []
    text = str(absolute)
    if text in (".", "/", ""):
        return []
    variants = {text, text.replace("\\", "/")}
    if "/" in text:
        variants.add(text.replace("/", "\\"))
    return [v for v in variants if len(v) > 1]


def check_path_format(docs, repo_root, f):
    """R1 (RP1) — abszolút / gép-specifikus / `file://` útvonal a tervezési
    dokumentumokban. A `file://`, a gép-specifikus és a placeholder alak
    mindenhol hiba (kódblokkban is); a „gyökér-abszolút repó-útvonal" alakot
    viszont csak kódblokkon KÍVÜL jelezzük, mert egy parancsban a konténer-belső
    `/opt/app/...` útvonal jogos lehet."""
    roots = repo_root_variants(repo_root)
    try:
        top_level = {e.name for e in repo_root.iterdir() if e.is_dir() and not e.name.startswith(".")}
    except OSError:
        top_level = set()

    for doc, text, phase in docs:
        hits, in_fence = 0, False
        for lineno, line in enumerate(text.splitlines(), start=1):
            if FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            found = []
            # A repó gyökerének abszolút alakja MINDIG hiba — kódblokkban is.
            for root in roots:
                if root in line:
                    found.append((root[:70], "a repó gyökerének abszolút útvonala"))
                    break
            for m in FILE_URI_RE.finditer(line):
                found.append((m.group(0)[:70], "`file://` sémájú link"))
            for m in MACHINE_PATH_RE.finditer(line):
                found.append((m.group(0)[:70], "gép-specifikus abszolút útvonal"))
            for m in PLACEHOLDER_PATH_RE.finditer(line):
                found.append((m.group(0)[:70], "placeholder útvonal"))
            if not in_fence:
                for m in MD_ABS_LINK_RE.finditer(line):
                    found.append((m.group(1)[:70], "abszolút markdown-link"))
                for m in ABS_REPO_PATH_RE.finditer(line):
                    # Hiba, ha a vezető `/` nélkül LÉTEZŐ repó-fájlra mutat, VAGY ha az
                    # első szegmense a repó egy létező gyökér-mappája — ez utóbbi a
                    # tervekben gyakori „még nem létező, de tervezett fájl" eset
                    # (`/src/auth/token-store.ts`), amit a puszta létezés-check nem fog.
                    # A konténer-belső `/opt/app/config.yaml` így sem sül el:
                    # `opt/` nem gyökér-mappája a repónak.
                    rel = m.group(1)
                    if (repo_root / rel).is_file() or rel.split("/", 1)[0] in top_level:
                        found.append((m.group(0)[:70], f"abszolút repó-útvonal (helyesen: `{rel}`)"))
            if found:
                # Egy sorra több minta is illeszkedhet (pl. `file://` + gép-specifikus
                # + abszolút markdown-link ugyanarra az útvonalra). A fixernek EGY
                # tétel kell soronként — a legspecifikusabb, a `found` sorrendje szerint.
                value, why = found[0]
                extra = f" (+{len(found) - 1} további illeszkedő minta ugyanezen a soron)" if len(found) > 1 else ""
                hits += 1
                if hits <= R1_MAX_PER_DOC:
                    f.add("R1", phase, f"{doc}:{lineno} {why}: `{value}`{extra} — a kód-/fájl-hivatkozás a repó gyökeréhez képest relatív, a dokumentum-link a fájl saját könyvtárához képest (RP1)")
        if hits > R1_MAX_PER_DOC:
            f.add("R1", phase, f"{doc}: további {hits - R1_MAX_PER_DOC} útvonal-formátum hiba (nem listázva)")


# ── G1 — a kapu-konfiguráció együtt mozog a struktúrával (GC1) ────────────────
# Valós hibamód: a ciklus átalakítja a `test-report/` szerkezetét (vagy a
# riport-parancsokat), és a `specs/test-conventions.md`-t frissíti — a
# `conventions.md` `## Teszt-riportolás` tábláját viszont nem. A 07 TR3 kapuja
# ezt a táblát olvassa, tehát a régi helyen keresi a riportot, és a validálás
# bukik: a hiba két fázissal a keletkezése UTÁN derül ki.
#
# Gépies jelzés: a `conventions.md`-ben deklarált riport-artefaktumok közül
# egyet sem nevezi meg a plan/tasks, MIKÖZBEN a ciklus a riport-struktúrához
# hozzáér — és a `conventions.md` nem szerepel a tervezett módosítások közt.

REPORT_SECTION_RE = re.compile(r"^##\s+" + re.escape(sec("cv_test_reporting")) + r"\s*$",
                               re.IGNORECASE | re.MULTILINE)
TEST_REPORT_PATH_RE = re.compile(r"test-report/[\w./-]*")
EMPTY_ARTIFACT_VALUES = {"", "-", "–", "—", "n/a", "na", "nincs", "none"}
CONVENTIONS_REF_RE = re.compile(r"(?<!test-)conventions\.md")


def declared_report_artifacts(conventions_text):
    """A `conventions.md` `## Teszt-riportolás` táblájának utolsó oszlopa."""
    body = section_body(conventions_text, sec("cv_test_reporting"))
    out = []
    for cells in (table_rows_by_header(body, [fld("f_test_category").lower()])
                  or table_rows(body, sec("cv_test_reporting"))):
        value = cells[-1].strip().strip("`").strip() if cells else ""
        if value and value.lower() not in EMPTY_ARTIFACT_VALUES:
            out.append(value)
    return out


def check_gate_config_moves(plan_text, tasks_text, conventions_path, f):
    """G1 (GC1) — ha a ciklus a riport-struktúrához hozzáér, a `conventions.md`
    érintett szekciója is a tervezett módosítások közt van-e."""
    if not conventions_path or not conventions_path.is_file():
        return
    conv = conventions_path.read_text(encoding="utf-8", errors="replace")
    if not REPORT_SECTION_RE.search(conv):
        return  # a 00 kötelező szekciója hiányzik — azt a 07 TR3 kapuja jelzi
    artifacts = declared_report_artifacts(conv)
    if not artifacts:
        return

    docs = plan_text + "\n" + tasks_text
    # Hozzáér-e a ciklus a riport-struktúrához? (a keretrendszer által amúgy is
    # használt útvonalak nem számítanak: azokat minden ciklus említi)
    framework_owned = ("test-report/implement/check-log.md", "test-report/validation-report.md",
                       "test-report/code-review.md")
    touches = [
        m.group(0) for m in TEST_REPORT_PATH_RE.finditer(docs)
        if not any(m.group(0).startswith(x) for x in framework_owned)
    ]
    if not touches:
        return

    plan_norm = " ".join(docs.split())
    missing = [a for a in artifacts if a.strip("/") not in plan_norm]
    if not missing:
        return
    # FIGYELEM: `"conventions.md" in "test-conventions.md"` IGAZ — a két regiszter
    # összekeverése épp az a hiba, amit ez a check keres, ezért a mintának
    # kizárnia kell a `test-` prefixet.
    plans_conventions = bool(
        CONVENTIONS_REF_RE.search(section_body(plan_text, sec("planned_changes"))))
    if plans_conventions:
        f.note("KAPU-KONFIG", f"a ciklus a riport-struktúrához hozzáér, és a `conventions.md` szerepel a tervezett módosítások közt — rendben (GC1). Nem hivatkozott deklarált artefaktum: {', '.join(missing[:3])}")
        return
    f.add("G1", "03", f"a ciklus a `test-report/` szerkezetét érinti ({touches[0]}), de a `conventions.md` `## Teszt-riportolás` táblájában deklarált artefaktum(ok)ról — {', '.join(f'`{a}`' for a in missing[:3])} — sem a plan, sem a tasks nem szól, és a `conventions.md` nem szerepel a `Tervezett módosítások`-ban. A 07 TR3 kapuja ezt a táblát olvassa: a régi helyen fog keresni, és a validálás bukik. A kapu-konfiguráció együtt mozog a struktúrával (GC1)")


def kind_is_table(kind):
    """A leltár tábla-sorai (MÁTRIX*, PID*) külön blokkban jelennek meg, ezért a
    `## Leltár` felsorolásból ki kell szűrni őket."""
    return kind.startswith("MÁTRIX") or kind.startswith("PID")


def _force_utf8_output():
    """Windows-kompatibilitás: a konzol örökölt kódlapja (cp852 / cp1250 / cp1252)
    nem tudja megjeleníteni a kimenet tipográfiai és ékezetes karaktereit (—, →, ő, ű),
    és a `print()` ilyenkor `UnicodeEncodeError`-t dob. Ez azért veszélyes, mert a
    kivétel AZUTÁN keletkezne, hogy a szkript a fájlműveletet már elvégezte: a hívó
    ágens hibás kilépő kódot látna egy sikeres művelet után. Ezért a kimenetet
    UTF-8-ra kapcsoljuk, hibatűrő módban (Python 3.7+; régebbin csendben kimarad)."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

# ── Szeletelés (SH1) ─────────────────────────────────────────────────────────
# Miért kell: a szemantikai diagnózist HÁROM párhuzamos analyzer-kör viszi
# (1+3., 2+5. és 4. kategória). Ha mindhárom a teljes spec+plan+tasks+conventions
# négyest olvassa, a párhuzamosság eltelt időt nyer, de a token-költséget
# megháromszorozza. Ez a blokk determinisztikusan kimetszi minden körnek a SAJÁT
# bemenetét — ugyanaz az elv, mint a leltárnál (AG3): a subagent ne keressen,
# hanem ítéljen.
#
# A szelet-fájl FEJLÉCE szándékosan nyelvfüggetlen ASCII (`SOURCE-DOCS:`,
# `MISSING-SECTIONS:`, `SLICE-CUT`): ugyanez a script írja magyar és angol
# prompt-nyelv mellett is, a TÖRZSE pedig a projekt szövegének szó szerinti
# másolata — ott a projekt nyelve érvényesül, fordítás nélkül.
#
# A `*` érték = a TELJES dokumentum (nincs értelme szekcióra vágni).
SLICES = {
    "s1-dup-underspec": {
        "scope": "categories 1+3 (duplication, under-specification) — finding prefix: AF",
        "spec.md": ["components_behavior", "definition_of_done", "test_specification",
                    "schema_artifacts", "out_of_scope"],
        "plan.md": ["planned_changes", "affected_components", "schema_artifacts",
                    "new_dependencies", "test_specification", "testing_strategy",
                    "verification_strategy", "risks_and_decisions",
                    "spec_coverage", "reverse_coverage"],
        "tasks.md": ["*"],
        "conventions.md": [],
    },
    "s2-coverage": {
        "scope": "categories 2+5 (ambiguity/measurability, coverage interpretation) — finding prefix: AC",
        "spec.md": ["definition_of_done", "components_behavior", "test_specification",
                    "out_of_scope"],
        "plan.md": ["spec_coverage", "reverse_coverage", "test_specification",
                    "config_lifecycle", "environment_coords", "machine_run_table"],
        "tasks.md": ["*"],
        "conventions.md": [],
    },
    "s3-conventions": {
        "scope": "category 4 (convention conflict) — finding prefix: AN",
        "spec.md": [],
        "plan.md": ["goal_and_approach", "planned_changes", "new_dependencies",
                    "config_build_changes", "testing_strategy", "verification_strategy",
                    "machine_run_table", "environment_coords", "risks_and_decisions"],
        "tasks.md": [],
        "conventions.md": ["*"],
    },
}
# Az analízis MINDEN fájlja a ciklus `analyze/` almappájában él (analyze-report.md,
# analyze-task.md, slices/). A szeletek külön alkönyvtárba mennek, ami elrejti magát a git elől.
ANALYZE_DIR_NAME = "analyze"
SLICE_DIR_NAME = "slices"
SLICE_DOCS = ("spec.md", "plan.md", "tasks.md", "conventions.md")


def _slice_part(doc, text, key):
    """Egy szekció kimetszése a CÍMSORÁVAL együtt. Visszaad: (blokk, hiányzik?)."""
    if key == "*":
        return f"<!-- SLICE-CUT: {doc} (whole document) -->\n{text.strip()}\n", None
    title = sec(key)
    body = section_body(text, title)
    if not body.strip():
        return None, f"{doc} § {title}"
    return f"<!-- SLICE-CUT: {doc} § {title} -->\n## {title}\n{body.strip()}\n", None


def emit_slices(cycle, texts):
    """A három szemantikai analyzer-kör bemenetének kiírása.

    A mappa ÖNMAGÁT rejti el a git elől (`.gitignore` = `*`), ezért a fázis-záró
    `git add specs/cycle-NN-<name>/` nem stage-eli, és a munkafa tisztaság-
    ellenőrzését sem zavarja meg. Visszaad: [(név, útvonal, scope, hiányzók)]."""
    out_dir = cycle / ANALYZE_DIR_NAME / SLICE_DIR_NAME
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / ".gitignore").write_text("*\n", encoding="utf-8")

    written = []
    for name, spec_def in SLICES.items():
        parts, missing, used_docs = [], [], []
        for doc in SLICE_DOCS:
            keys = spec_def.get(doc) or []
            if not keys or not texts.get(doc, "").strip():
                continue
            used_docs.append(doc)
            for key in keys:
                block, gap = _slice_part(doc, texts[doc], key)
                if gap:
                    missing.append(gap)
                else:
                    parts.append(block)
        header = [
            f"# SLICE: {name}",
            f"# SCOPE: {spec_def['scope']}",
            f"# SOURCE-DOCS: {', '.join(used_docs) or '-'}",
            f"# ABSENT-SECTIONS: {'; '.join(missing) if missing else 'none'}",
            "# RULE: verbatim extract of the cycle's design documents. Judge from this file.",
            "#       An ABSENT section is either optional in this cycle, or already reported by",
            "#       the mechanical gate (S1/S2) — do NOT go hunting for it. Read from the source",
            "#       document only if you genuinely need it, and say so in your report.",
            "",
        ]
        path = out_dir / f"{name}.md"
        path.write_text("\n".join(header) + "\n".join(parts), encoding="utf-8")
        written.append((name, path, spec_def["scope"], missing))
    return written


# ── RC1–RC3 — a riport LEZÁRÁSAKOR (--report-only) ────────────────────────────
# Miért kell: az AR1 szabály prózában tiltja, hogy a hurok végén az
# `analyze-report.md` a részletes „Javítandó tételek" pipálólista helyett egy
# tömör összefoglalóvá zsugorodjon („ne írd újra nulláról"). Egy éles ciklusban
# ez mégis megtörtént: az `analyze-task.md` teli volt konkrét, ember által
# rögtön javítható tételekkel, a végleges riport viszont csak 4 bekezdésnyi
# próza volt — a diagnózis elveszett. A tiltás magában nem elég, mert épp az a
# modell ellenőrzi saját magát, akinek érdeke a tömör lezárás. Ez a réteg ezt
# teszi gépiessé: az `analyze-task.md` minden tétele szó szerinti azonosítóval
# visszaköszön-e a riportban, a megmaradt tételek viselik-e mind a négy
# kötelező mezőt, és `PASS` mellett egyik sem maradt-e `[ ]` állapotban.

ITEM_LINE_RE = re.compile(r"^\s*-\s*\[([ xX])\]\s+\*\*([A-Z]{1,4}-\d+)\*\*")
STATUS_HEADER_RE = re.compile(r"\*\*" + re.escape(fld("f_status")) + r":?\*\*\s*([A-Z_]+)")
FIELD_LINE_RE_TMPL = r"\*\*{label}:?\*\*:?\s*(.*)"
ITEM_REQUIRED_FIELDS = ("f_contradiction", "f_why_blocks", "f_how_correct", "f_state")
# A generikus PLACEHOLDER_ANGLE_RE csak SZÓKÖZ nélküli `<szo>` alakra illik (T5-höz
# elég); egy kitöltetlen mező tartalma viszont gyakran több szavas sablon-szöveg
# (`<ide jön a leírás>`), ezért itt a teljes érték `<…>`-be zártságát nézzük.
RC_PLACEHOLDER_RE = re.compile(r"^<.*>$")


def parse_checklist_items(text):
    """Pipálható tételek (`- [ ] **AF-01** ...`) a szöveg TELJES egészéből —
    a jelölt (`[x]`), az azonosító és a bullet utáni, a következő tételig vagy
    címsorig tartó törzs. A `### Suggestions` sima felsorolása (ID nélkül) nem
    illeszkedik, tehát természetesen kimarad."""
    items, cur = [], None
    for line in text.splitlines():
        m = ITEM_LINE_RE.match(line)
        if m:
            if cur is not None:
                items.append(cur)
            cur = {"id": m.group(2), "checked": m.group(1).lower() == "x", "body": [line]}
            continue
        if line.startswith("#"):
            if cur is not None:
                items.append(cur)
                cur = None
            continue
        if cur is not None:
            cur["body"].append(line)
    if cur is not None:
        items.append(cur)
    for it in items:
        it["body"] = "\n".join(it["body"])
    return items


def _field_value(body, field_key):
    label = fld(field_key)
    m = re.search(FIELD_LINE_RE_TMPL.format(label=re.escape(label)), body)
    return m.group(1).strip() if m else None


def check_report_closure(report_text, task_text, f):
    """RC1–RC3 — lásd a fenti fejléc-blokkot. `task_text` üres string, ha az
    `analyze-task.md` nem létezik (első futásra tiszta PASS, triázs sem volt)."""
    report_items = {it["id"]: it for it in parse_checklist_items(report_text)}
    task_items = parse_checklist_items(task_text) if task_text else []

    # RC1 — az analyze-task.md MINDEN tétele (nyitott és elvetett is) megvan-e
    # szó szerint a riportban. Ez fogja meg az „összefoglalóvá írt riport" hibát.
    for it in task_items:
        if it["id"] not in report_items:
            f.add("RC1", "05",
                  f"az `analyze-task.md` `{it['id']}` tétele hiányzik az `analyze-report.md` "
                  f"„{sec('items_to_fix')}\" listájából — a riportot valószínűleg összefoglalóvá "
                  "írták át a hurok lezárásakor, a részletes, ember által olvasható diagnózis helyett "
                  "(AR1: „ne írd újra nulláról\"). Állítsd vissza a tételt a hozzá tartozó három "
                  "kötelező mezővel")

    # RC2 — a riportban MEGMARADT tételek mind a négy kötelező mezőt viselik-e,
    # kitöltve (nem üres, nem placeholder).
    for it in report_items.values():
        for key in ITEM_REQUIRED_FIELDS:
            val = _field_value(it["body"], key)
            if not val or RC_PLACEHOLDER_RE.match(val.strip()):
                f.add("RC2", "05",
                      f"analyze-report.md `{it['id']}` tétele: hiányzik vagy placeholder maradt a "
                      f"kötelező `**{fld(key)}:**` mező — enélkül a tétel nem ember által azonnal "
                      "érthető, javítható diagnózis, csak egy sortöredék")

    # RC3 — PASS mellett egyik tétel sem maradhat nyitva ([ ]). A konkrét
    # végállapot-SZÓ (`megoldva` / `elvetve` / `resolved` / `dismissed`) nyelvenként
    # más — azt a `**Állapot:**` mező kitöltöttségét már az RC2 megköveteli,
    # ide csak a checkbox-jelölés számít, hogy ne kelljen újabb, a
    # `lang-parity-check`-kel ütköző szó-szótárt bevezetni.
    status_m = STATUS_HEADER_RE.search(report_text)
    status = status_m.group(1) if status_m else None
    if status == "PASS":
        for it in report_items.values():
            if not it["checked"]:
                state_val = _field_value(it["body"], "f_state") or "—"
                f.add("RC3", "05",
                      f"analyze-report.md `{it['id']}` tétele `PASS` mellett `[ ]` (nyitva) maradt "
                      f"(Állapot: `{state_val}`) — PASS csak akkor adható, ha minden tétel `[x]`-re "
                      "lezárt (AR1)")


def main():
    _force_utf8_output()
    parser = argparse.ArgumentParser(description="Analyze mechanikus kapu (05-analyze)")
    parser.add_argument("cycle_dir", help="a ciklus mappája, pl. specs/cycle-25-dynamic-routing")
    parser.add_argument("--repo-root", default=".", help="a projekt gyökere a létezés-ellenőrzésekhez (alap: az aktuális könyvtár)")
    parser.add_argument("--conventions", default="conventions.md",
                        help="a projekt conventions.md-je a kapu-konfiguráció ellenőrzéséhez (G1); ha nem létezik, a check kimarad")
    parser.add_argument(
        "--plan-only",
        action="store_true",
        help="a 03b-test-plan fázis lezárásához (a TELJES plan kapuja): csak a spec+plan "
             "checkek futnak, a tasks.md még nem létezik",
    )
    parser.add_argument(
        "--plan-code-only",
        action="store_true",
        help="a 03a-code-plan fázis lezárásához: csak a kód-terv checkjei futnak "
             "(a teszt-szekciók még nem léteznek; azokat a 03b lezárásakor a --plan-only méri)",
    )
    parser.add_argument(
        "--paths-only",
        action="store_true",
        help="csak az R1 útvonal-formátum (RP1) check fut, a meglévő tervezési "
             "dokumentumokra (spec/plan/tasks — amelyik létezik). A 02/03/04 fázis "
             "lezárása előtt futtatható, akkor is, ha a többi dokumentum még nincs meg.",
    )
    parser.add_argument(
        "--emit-slices",
        action="store_true",
        help="a 05-analyze-hoz: a három szemantikai analyzer-kör bemenetének kimetszése a "
             "<ciklus>/analyze/slices/ mappába (SH1). `--plan-only` mellett nem fut.",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="a hurok LEZÁRÁSAKOR (PASS/FAIL): kizárólag azt ellenőrzi, hogy az "
             "<ciklus>/analyze/analyze-report.md megtartotta-e az <ciklus>/analyze/analyze-task.md "
             "MINDEN tételét, a négy kötelező mezővel (RC1-RC3) — a spec/plan/tasks checkek nem futnak.",
    )
    args = parser.parse_args()

    # A `--plan-code-only` a `--plan-only` SZŰKEBB esete: örökli a szemantikáját
    # (a tasks.md-t üresként kezeli), és azon felül kihagyja a teszt-oldali
    # checkeket. A két flag együttes megadása NEM hiba.
    code_only = args.plan_code_only
    if code_only:
        args.plan_only = True

    # 11.8 — használati hiba. A `--report-only` és a `--paths-only` ÖNÁLLÓ,
    # minimál üzemmódok: lentebb korábban térnek vissza, mint ahol a plan-kapuk
    # egyáltalán lefutnának. Egy `--plan-code-only --report-only` hívás így
    # CSENDBEN mást csinálna, mint amit a hívó gondol — ezért explicit hiba.
    if (args.plan_only or code_only) and (args.report_only or args.paths_only):
        other = "--report-only" if args.report_only else "--paths-only"
        mode = "--plan-code-only" if code_only else "--plan-only"
        print(f"HIBA: a(z) {mode} és a(z) {other} nem kombinálható — az utóbbi önálló, "
              "minimál üzemmód, és a plan-checkek ilyenkor nem futnának le. "
              "Futtasd őket külön hívásban.", file=sys.stderr)
        return 2

    cycle = Path(args.cycle_dir)
    if not cycle.is_dir():
        print(f"HIBA: {cycle} nem létező könyvtár", file=sys.stderr)
        return 2

    # `--report-only`: a hurok lezárásának őre (RC1-RC3) — lásd a `check_report_closure`
    # fejléc-kommentjét. Önálló, minimál ág, mint a `--paths-only`: nem igényli a
    # spec/plan/tasks hármast, csak az analyze/ almappa két riportfájlját.
    if args.report_only:
        report_path = cycle / "analyze" / "analyze-report.md"
        task_path = cycle / "analyze" / "analyze-task.md"
        if not report_path.is_file():
            print(f"HIBA: {report_path} nem található", file=sys.stderr)
            return 2
        f = Findings()
        check_report_closure(read(report_path), read(task_path) if task_path.is_file() else "", f)
        print(f"REPORT-GATE: {len(f)} Must Fix")
        if f.items:
            print("\n## Must Fix")
            for code, phase, message in f.items:
                print(f"[{code}] (célfázis: {phase}) {message}")
            return 1
        print("Nincs blokkoló mechanikus megállapítás — a riport megtartotta a teljes tétel-listát.")
        return 0

    spec_path, plan_path, tasks_path = cycle / "spec.md", cycle / "plan.md", cycle / "tasks.md"

    # `--paths-only`: önálló, minimál üzemmód az R1-re. Azért van külön ága, hogy a
    # 02 lezárása előtt is futtatható legyen — ott a plan.md és a tasks.md még nem
    # létezik, tehát a teljes kapu (és a `--plan-only` is) elvérezne az
    # előfeltétel-ellenőrzésen. Shift-left: az abszolút útvonal ott derüljön ki,
    # ahol keletkezett, ne két fázissal később.
    if args.paths_only:
        present = [(name, path, phase) for name, path, phase in
                   (("spec.md", spec_path, "02"), ("plan.md", plan_path, "03"),
                    ("tasks.md", tasks_path, "04")) if path.is_file()]
        if not present:
            print(f"HIBA: {cycle} egyetlen tervezési dokumentumot sem tartalmaz", file=sys.stderr)
            return 2
        f = Findings()
        check_path_format([(name, read(path), phase) for name, path, phase in present],
                          Path(args.repo_root), f)
        names = ", ".join(name for name, _, _ in present)
        if f.items:
            print(f"R1 útvonal-formátum kapu (RP1) — ellenőrizve: {names}")
            print(f"PATHS-GATE: {len(f)} Must Fix\n")
            for code, phase, message in f.items:
                print(f"[{code}] (célfázis: {phase}) {message}")
            return 1
        print(f"R1 útvonal-formátum kapu (RP1): PASS — ellenőrizve: {names}")
        return 0

    required = (spec_path, plan_path) if args.plan_only else (spec_path, plan_path, tasks_path)
    for p in required:
        if not p.is_file():
            docs = "a spec.md-t és a plan.md-t" if args.plan_only else "a három tervezési dokumentumot"
            print(f"HIBA: {p} nem található — a kapu {docs} igényli", file=sys.stderr)
            return 2

    spec_text, plan_text = read(spec_path), read(plan_path)
    # `--plan-only` módban (a TELJES plan kapuja, a 03b lezárása) a tasks-oldalt
    # üresként kezeljük: így a tasks.md-t igénylő checkek nem adnak hamis
    # találatot, a spec+plan oldal viszont a 03 lezárásakor is lefut
    # (shift-left: a hiba ott derül ki, ahol keletkezett). A `--plan-code-only`
    # (a 03a lezárása) ezen felül a teszt-oldali checkeket is kihagyja.
    tasks_text = "" if args.plan_only else read(tasks_path)
    f = Findings()

    known_ids = check_plan_ids(plan_text, f)
    check_dod(spec_text, f)
    check_required_tables(
        plan_text,
        REQUIRED_PLAN_CODE_TABLES if code_only else REQUIRED_PLAN_TABLES,
        f, "plan.md",
    )
    check_config_lifecycle(plan_text, f)
    check_env_coordinates(plan_text, f)

    if not args.plan_only:
        referenced = check_task_references(tasks_text, known_ids, f)
        check_plan_coverage(tasks_text, known_ids, referenced, f)
        check_markers(tasks_text, f)
        check_parallel_symmetry(tasks_text, f)
        check_task_command_placeholders(tasks_text, f)
        check_required_tables(tasks_text, REQUIRED_TASKS_TABLES, f, "tasks.md")
        check_rollback_state(tasks_text, f)

    # `code_only` módban a lefedettségi lánc (C1/S3) NEM fut: egy kizárólag
    # teszttel igazolt `DoD-NN` a kód-fél lezárásakor még nem lehet lefedve —
    # a check ott hamis FAIL-t adna. A `03b` lezárásakor a `--plan-only` ezt
    # teljes egészében méri, tehát nem veszik el.
    if not code_only:
        check_coverage_chain(spec_text, plan_text, tasks_text, known_ids, f, plan_only=args.plan_only)
        check_spec_artifact_transfer(spec_text, plan_text, f)
    check_gate_config_moves(plan_text, tasks_text, Path(args.conventions), f)
    check_path_format(
        [("spec.md", spec_text, "02"), ("plan.md", plan_text, "03")]
        + ([] if args.plan_only else [("tasks.md", tasks_text, "04")]),
        Path(args.repo_root), f,
    )
    # A teszt-oldali checkek a `03b` lezárásának tárgyai — `code_only` módban
    # a mért szekciók (teszt-forgatókönyvek, gépi tábla, adatlapok) még nem
    # léteznek, tehát minden találatuk hamis lenne.
    if not code_only:
        check_test_section_volume(spec_text, plan_text, f)
        check_test_scenarios(spec_text, plan_text, f)
        check_scenario_scope(plan_text, f)
        check_spec_coverage_scenarios(plan_text, f)
        check_test_artifact_datasheet(plan_text, f)
        check_ts_http_blocks(plan_text, f)
        check_run_table_schema(plan_text, f)
        check_run_table_phase(plan_text, f)
        check_test_ids(plan_text, f)
    if code_only:
        check_gate_stamp(plan_text, f, field="f_gate_code",
                         status_key="ready_for_test_plan", mode="--plan-code-only")
    else:
        check_gate_stamp(plan_text, f)
    if not args.plan_only:
        check_test_task_coverage(plan_text, tasks_text, f)
        check_check_output_collisions(tasks_text, f)
        check_task_test_refs(plan_text, tasks_text, f)
    check_planned_change_purpose(plan_text, f)
    check_target_environment(plan_text, f, code_only=code_only)
    check_judgment_candidates(plan_text, tasks_text, f)

    repo_root = Path(args.repo_root)
    # A futtatott artefaktumok (teszt-parancsok belépési pontjai) a teszt-félben
    # keletkeznek — `code_only` módban nincs mit mérni.
    if not code_only:
        check_executed_artifacts(plan_text, tasks_text, repo_root, f, plan_only=args.plan_only)
    check_plan_anchors(plan_text, repo_root, f, cycle_dir=cycle)
    check_artifact_voice(
        [("spec.md", spec_text, "02"), ("plan.md", plan_text, "03"), ("tasks.md", tasks_text, "04")], f
    )

    if code_only:
        print("# mód: --plan-code-only (a teszt-oldali checkek nem futnak — "
              "azokat a 03b lezárása méri)")
    print(f"ANALYZE-GATE: {len(f)} Must Fix, {len(f.suggestions)} javaslat")

    if f.items:
        print("\n## Must Fix")
        for code, phase, message in f.items:
            print(f"[{code}] (célfázis: {phase}) {message}")

    if f.suggestions:
        print("\n## Javaslatok (nem blokkolnak, nem indítanak hurkot)")
        for code, phase, message in f.suggestions:
            print(f"[{code}] (célfázis: {phase}) {message}")

    matrix = [m for kind, m in f.inventory if kind.startswith("MÁTRIX")]
    pid_table = [m for kind, m in f.inventory if kind.startswith("PID")]
    rest = [(k, m) for k, m in f.inventory if not kind_is_table(k)]

    if matrix:
        print(f"\n## {sec('coverage_matrix')} — DoD → plan-szekció → task")
        print("Az orchestrátor ezt SZÓ SZERINT fűzi az analyze-report.md megfelelő szekciójába;")
        print(f"az analyzernek nem kell újra levezetnie. A `{sec('covered_machine')}` "
              f"oszlop a LÁNC")
        print("meglétét jelenti — a lefedés TARTALMI elégségességét az analyzer ítéli meg.")
        for row in matrix:
            print(row)

    if pid_table:
        print("\n## Plan-szekció ↔ task (generált — PID1)")
        print("Szintén szó szerint fűzhető az analyze-report.md megfelelő szekciójába.")
        for row in pid_table:
            print(row)

    if rest:
        print("\n## Leltár — az analyzer BEMENETE (nem megállapítás)")
        print("Ezt add át az analyzer subagenteknek: a végrehajthatósági és hang-ítéletet ebből")
        print("hozzák meg, így nem kell a repóban vagy a dokumentumokban célpontot keresniük.")
        for kind, message in rest:
            print(f"[{kind}] {message}")

    if args.emit_slices and not args.plan_only:
        written = emit_slices(cycle, {
            "spec.md": spec_text, "plan.md": plan_text, "tasks.md": tasks_text,
            "conventions.md": read(Path(args.conventions)) if Path(args.conventions).is_file() else "",
        })
        print(f"\n## Szeletek (SH1) — a szemantikai analyzer-körök BEMENETE")
        print("Minden körnek a SAJÁT szeletét add át; a szelet a dokumentumok szó szerinti")
        print("kimetszése, tehát a subagentnek nem kell a teljes négyest beolvasnia.")
        for name, path, scope, missing in written:
            print(f"[SZELET] {name} → {path} ({scope})")
            if missing:
                print(f"         nem talált szekció (opcionális vagy S1/S2 által már jelzett): "
                      f"{'; '.join(missing)}")
    elif args.emit_slices and args.plan_only:
        mode = "--plan-code-only" if code_only else "--plan-only"
        print(f"\nA --emit-slices `{mode}` mellett kimarad (a tasks.md még nem létezik).")

    if not f.items:
        print("\nNincs blokkoló mechanikus megállapítás.")
        return 0
    print("\nA Must Fix tételek a megadott célfázissal mennek a hurokba — az analyzer szemantikai megállapításai mellé.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
