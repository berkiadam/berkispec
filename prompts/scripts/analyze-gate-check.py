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
  D1  `DoD-NN` azonosítók            — hiányzó vagy duplikált azonosító a specben
  D2  `DoD-NNb` alakú azonosító      — utólagos beszúrás betűs utótaggal (DI1 megsértése)
  S1  kötelező plan-táblák           — `Spec-lefedettség`, `Fordított lefedettség`,
                                       `Környezeti koordináták` (KO1)
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
  R1  útvonal-formátum (RP1)           — `file://`, gép-specifikus (`/home/…`,
                                       `C:/Users/…`), placeholder és abszolút
                                       repó-útvonal a tervezési dokumentumokban
  A2c horgony-formátum (RP1, javaslat) — a `path:sor` horgony a plan MAPPÁJÁHOZ
                                       képest relatív, nem a repó gyökeréhez

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

Amit NEM csinál: nem értelmez ott, ahol ítélet kell (kinek szól egy mondat,
meglévő-e egy szimbólum), és nem javít.

Használat:
  analyze-gate-check.py specs/cycle-NN-<name> [--repo-root .]

Kilépő kód: 0 = nincs BLOKKOLÓ megállapítás (javaslat és leltár lehet a stdout-on)
            1 = van Must Fix (a `## Must Fix` blokk a stdout-on, gépiesen olvasható)
            2 = használati hiba (hiányzó mappa vagy dokumentum)
"""
import argparse
import re
import sys
from pathlib import Path


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
    ("Spec-lefedettség", "03", "a spec tesztesetei és DoD-pontjai leképezésének táblája (TP1)"),
    ("Fordított lefedettség", "03", "a plan-képességek spec-forrásának táblája (SC1)"),
    ("Környezeti koordináták", "03", "a ciklus konkrét koordinátái: URL-ek, portok, indító parancsok, példa REST hívások, teszt-/API-userek jelszóval, paraméterek (KO1)"),
]
REQUIRED_TASKS_TABLES = [
    ("Plan-lefedettség", "04", "a plan-szekció → task fordított tábla (PID1)"),
]


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
            inside = "Plan-lefedettség" in line
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


def check_dod(spec_text, f):
    inside = False
    numbers = []
    unlabeled = 0
    for line in spec_text.splitlines():
        if line.startswith("## "):
            inside = "Definition of done" in line
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
    for path in _candidate_paths(section_text(plan_text, "Ellenőrzési stratégia")):
        if path not in candidates:
            candidates.append(path)
    if not candidates:
        return
    planned_section = section_text(plan_text, "Tervezett módosítások")
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
        cells = [c.strip() for c in m.group(1).split("|")]
        if cells and all(PLACEHOLDER_CELL_RE.match(c) or not c for c in cells):
            continue  # sablonsor
        rows.append(cells)
    return rows


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
        cells = [c.strip() for c in m.group(1).split("|")]
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
    for line in section_body(spec_text, "Definition of done").splitlines():
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
    reverse_rows = table_rows(plan_text, "Fordított lefedettség")
    if not reverse_rows:
        # EGY aggregált megállapítás, nem DoD-onként egy: a gyökérok ugyanaz, és
        # egy 15 DoD-os ciklusban a per-DoD változat 15 azonos tételt szórna a
        # `Must Fix` listába (a fixer ugyanattól a hiánytól kapná meg 15-szer).
        if "Fordított lefedettség" in plan_text:
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
    for cells in table_rows(plan_text, "Spec-lefedettség"):
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

    f.note("MÁTRIX-FEJ", "| DoD | Plan szekció | Task(ok) | Lefedve (gépi) |")
    for dod, pids, tasks, ok in matrix:
        f.note("MÁTRIX", f"| `DoD-{dod}` | {pids} | {tasks} | {ok} |")

    # A második kötelező riport-tábla (plan-szekció ↔ task, PID1) ugyanebből az
    # adatból adódik — az orchestrátornak ezt sem kell kézzel összeírnia.
    coverage_mentions = set()
    inside = False
    for line in tasks_text.splitlines():
        if line.startswith("## "):
            inside = "Plan-lefedettség" in line
            continue
        if inside:
            coverage_mentions.update(PLAN_ID_TOKEN_RE.findall(line))
    f.note("PID-FEJ", "| Plan szekció (ID) | Hivatkozó taskok | Rendben |")
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
    rows = table_rows(plan_text, "Konfiguráció-életút")
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
    body = section_body(plan_text, "Környezeti koordináták")
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
        cells = [c.strip() for c in TABLE_ROW_RE.match(line).group(1).split("|")]
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
    spec_tests = section_body(spec_text, "Teszt specifikáció")
    if not spec_tests.strip():
        return
    plan_tests = section_body(plan_text, "Tesztelési stratégia") + "\n" + section_body(plan_text, "Teszt specifikáció")
    s, pl = _content_line_count(spec_tests), _content_line_count(plan_tests)
    if s < 5:
        return  # túl kicsi minta
    if pl < s * V2_MIN_RATIO:
        f.add("V2", "03", f"a plan teszt-szekciói ({pl} érdemi sor) rövidebbek a spec `Teszt specifikáció` szekciójánál ({s} sor) — a plan a spec tartalmát PLUSZ a végrehajtási részleteket (parancs, fixture, környezet-felkészítés) hordozza, tehát a zsugorodás összevonást vagy elhagyást jelent (KX3). Ellenőrizd, hogy minden spec-teszteset minden lépése és elvárt eredménye átkerült-e")
    else:
        f.note("TESZT-TERJEDELEM", f"spec `Teszt specifikáció`: {s} érdemi sor → plan teszt-szekciók: {pl} sor (rendben)")


# ── R1 — útvonal-formátum (RP1) ───────────────────────────────────────────────
# A tervezési dokumentumokban a kód-/fájl-hivatkozás a REPÓ GYÖKERÉHEZ képest
# relatív (a parancsok ott futnak, és a kapu is oda oldja fel a horgonyokat), a
# dokumentum-link pedig a fájl saját könyvtárához képest. Abszolút, gép-specifikus
# és `file://` útvonal egyik esetben sem érvényes: más gépen és CI-ben értelmetlen.
# Ez a check csak a BIZTOSAN hibás alakokat jelzi — az endpoint-útvonalakat
# (`/api/v1/...`) és a konténer-belső útvonalakat nem bántja.

FILE_URI_RE = re.compile(r"file:///?[^\s`\)\]]+")
MACHINE_PATH_RE = re.compile(
    r"(?<![\w.])(?:/home/[\w.-]+|/Users/[\w.-]+|/mnt/[a-z]/[\w.-]+|[A-Za-z]:[\\/]{1,2}Users[\\/])[^\s`\)\]\|]*"
)
PLACEHOLDER_PATH_RE = re.compile(r"(?<![\w.])(?:/path/to/|<projekt>/|<project>/|/абс)[^\s`\)\]\|]*")
MD_ABS_LINK_RE = re.compile(r"\]\((/[^)\s]*|file://[^)\s]*|[A-Za-z]:[\\/][^)\s]*)\)")
ABS_REPO_PATH_RE = re.compile(r"(?<![\w.:/])/((?:[\w.-]+/)+[\w.-]+\.[A-Za-z0-9]{1,5})(?![\w/])")
R1_MAX_PER_DOC = 10


def check_path_format(docs, repo_root, f):
    """R1 (RP1) — abszolút / gép-specifikus / `file://` útvonal a tervezési
    dokumentumokban. A `file://`, a gép-specifikus és a placeholder alak
    mindenhol hiba (kódblokkban is); a „gyökér-abszolút repó-útvonal" alakot
    viszont csak kódblokkon KÍVÜL jelezzük, mert egy parancsban a konténer-belső
    `/opt/app/...` útvonal jogos lehet."""
    for doc, text, phase in docs:
        hits, in_fence = 0, False
        for lineno, line in enumerate(text.splitlines(), start=1):
            if FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            found = []
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
                    # csak akkor hiba, ha a vezető `/` nélkül LÉTEZŐ repó-fájlra mutat
                    if (repo_root / m.group(1)).is_file():
                        found.append((m.group(0)[:70], f"abszolút repó-útvonal (helyesen: `{m.group(1)}`)"))
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

REPORT_SECTION_RE = re.compile(r"^##\s+Teszt-riportolás\s*$", re.IGNORECASE | re.MULTILINE)
TEST_REPORT_PATH_RE = re.compile(r"test-report/[\w./-]*")
EMPTY_ARTIFACT_VALUES = {"", "-", "–", "—", "n/a", "na", "nincs"}
CONVENTIONS_REF_RE = re.compile(r"(?<!test-)conventions\.md")


def declared_report_artifacts(conventions_text):
    """A `conventions.md` `## Teszt-riportolás` táblájának utolsó oszlopa."""
    body = section_body(conventions_text, "Teszt-riportolás")
    out = []
    for cells in table_rows_by_header(body, ["teszt-kategória"]) or table_rows(body, "Teszt-riportolás"):
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
    plans_conventions = bool(CONVENTIONS_REF_RE.search(section_body(plan_text, "Tervezett módosítások")))
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
        help="a 03-plan fázis lezárásához: csak a spec+plan checkek futnak (a tasks.md még nem létezik)",
    )
    args = parser.parse_args()

    cycle = Path(args.cycle_dir)
    if not cycle.is_dir():
        print(f"HIBA: {cycle} nem létező könyvtár", file=sys.stderr)
        return 2

    spec_path, plan_path, tasks_path = cycle / "spec.md", cycle / "plan.md", cycle / "tasks.md"
    required = (spec_path, plan_path) if args.plan_only else (spec_path, plan_path, tasks_path)
    for p in required:
        if not p.is_file():
            docs = "a spec.md-t és a plan.md-t" if args.plan_only else "a három tervezési dokumentumot"
            print(f"HIBA: {p} nem található — a kapu {docs} igényli", file=sys.stderr)
            return 2

    spec_text, plan_text = read(spec_path), read(plan_path)
    # `--plan-only` módban a tasks-oldalt üresként kezeljük: így a tasks.md-t
    # igénylő checkek nem adnak hamis találatot, a spec+plan oldal viszont a
    # 03 lezárásakor is lefut (shift-left: a hiba ott derül ki, ahol keletkezett).
    tasks_text = "" if args.plan_only else read(tasks_path)
    f = Findings()

    known_ids = check_plan_ids(plan_text, f)
    check_dod(spec_text, f)
    check_required_tables(plan_text, REQUIRED_PLAN_TABLES, f, "plan.md")
    check_config_lifecycle(plan_text, f)
    check_env_coordinates(plan_text, f)

    if not args.plan_only:
        referenced = check_task_references(tasks_text, known_ids, f)
        check_plan_coverage(tasks_text, known_ids, referenced, f)
        check_markers(tasks_text, f)
        check_parallel_symmetry(tasks_text, f)
        check_required_tables(tasks_text, REQUIRED_TASKS_TABLES, f, "tasks.md")
        check_rollback_state(tasks_text, f)

    check_coverage_chain(spec_text, plan_text, tasks_text, known_ids, f, plan_only=args.plan_only)
    check_spec_artifact_transfer(spec_text, plan_text, f)
    check_gate_config_moves(plan_text, tasks_text, Path(args.conventions), f)
    check_path_format(
        [("spec.md", spec_text, "02"), ("plan.md", plan_text, "03")]
        + ([] if args.plan_only else [("tasks.md", tasks_text, "04")]),
        Path(args.repo_root), f,
    )
    check_test_section_volume(spec_text, plan_text, f)
    check_judgment_candidates(plan_text, tasks_text, f)

    repo_root = Path(args.repo_root)
    check_executed_artifacts(plan_text, tasks_text, repo_root, f, plan_only=args.plan_only)
    check_plan_anchors(plan_text, repo_root, f, cycle_dir=cycle)
    check_artifact_voice(
        [("spec.md", spec_text, "02"), ("plan.md", plan_text, "03"), ("tasks.md", tasks_text, "04")], f
    )

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
        print("\n## Lefedettségi mátrix (generált — DoD → plan-szekció → task)")
        print("Az orchestrátor ezt SZÓ SZERINT fűzi az analyze-report.md megfelelő szekciójába;")
        print("az analyzernek nem kell újra levezetnie. A `Lefedve (gépi)` oszlop a LÁNC")
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

    if not f.items:
        print("\nNincs blokkoló mechanikus megállapítás.")
        return 0
    print("\nA Must Fix tételek a megadott célfázissal mennek a hurokba — az analyzer szemantikai megállapításai mellé.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
