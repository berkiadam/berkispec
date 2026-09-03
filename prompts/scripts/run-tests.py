#!/usr/bin/env python3
"""Teszt-futtató a plan.md gépi táblájából — a nyers teszt-log soha nem kerül
LLM-kontextusba (07-validate, TR1/TR2).

Miért kell: ma a `test-runner` subagent minden körben újraolvassa a `plan.md`-t
(több száz sor) ÉS a nyers teszt-kimenetet (E2E-nél tíz-százezres nagyságrend),
hogy a végén egyetlen `X passed / Y failed / Z skipped` sort adjon vissza.
A futtatás és a számlálás gépi munka: ez a szkript elvégzi, és 10-20 sorban
válaszol. A bizonyíték (JUnit XML, HTML-riport) a kör-mappába kerül.

A parancsok forrása a `plan.md` `## Tesztelési stratégia` szekciójában lévő
**gépi futtatási tábla** — a próza megmarad embernek, ez a szkriptnek:

  ### Gépi futtatási tábla (run-tests.py)

  | Kategória | Típus | Előfeltétel | Parancs | Eredményfájl | Formátum | Takarítás | Környezet |
  |---|---|---|---|---|---|---|---|
  | unit | gyors | — | `npm test -- --run --reporter=junit --outputFile=junit.xml` | `junit.xml` | junit | — | lokális |
  | e2e  | nehéz | `curl -fsS https://app.dev.example/health` | `npx playwright test --reporter=junit` | `results.xml` | junit | `docker compose ... down -v` | dev |

  · **Környezet:** hol fut a kategória (`lokális` vagy a cél-környezet neve). A
    szkript naplózza a `results.json`-ba és a kimenetbe — így a bizonyítékból
    utólag is látszik, HOL volt zöld —, és megáll (exit 4), ha egy nem-lokális
    kategória lokális célra mutat. Régi, 7 oszlopos tábla változatlanul fut.

  · **Típus:** `gyors` (unit/integration/typecheck — könnyű körben is fut) vagy
    `nehéz` (E2E/regresszió — csak teljes körben, VD10).
  · **Fázis (PH1, opcionális 9. oszlop):** `implement` / `validate` / `mindkettő`.
    Megmondja, MELYIK FÁZIS futtatja a kategóriát: a 06 `--phase implement`-tel,
    a 07 `--phase validate`-tel hívja a szkriptet. **Az üres cella = mindkettő** —
    a hallgatás soha nem jelent kihagyást. Régi, 7-8 oszlopos tábla változatlanul
    fut, minden sora mindkét fázisban.
  · **Előfeltétel / Takarítás:** `;`-vel több parancs is megadható. A takarítás
    akkor is lefut, ha a futtatás elszállt.
  · **Eredményfájl:** a repóhoz képest relatív; a szkript a kör-mappába másolja.
  · **Formátum:** `junit` (alap) vagy `text` (a stdout-ból regexszel számol).
  · A `{round}` helyőrző a parancsban és az eredményfájlban a kör-mappára cserélődik.

Mit ad vissza: kategóriánként a **ténylegesen kiadott parancs** és a
`X passed / Y failed / Z skipped` darabszámok + a bukott tesztek nevei — pont
az, amit a TR1 bizonyíték-kötelezettség megkövetel, és amit a
`failure-counter.py --failed-item` szó szerint vár. A `--json` a `round-log.py`
és a hurok további lépéseinek gépi bemenete.

Kilépő kód: 0 = minden futtatott kategória zöld
            1 = legalább egy kategória bukott (vagy 0 tesztet futtatott — TR2)
            2 = használati hiba: nincs gépi tábla a planban, vagy a megadott
                kategória nem szerepel benne → **ilyenkor a hívó a `test-runner`
                subagentre esik vissza**, és jelzi a 03-nak a hiányzó táblát
            4 = a tábla KÖRNYEZET-hibás: egy nem-lokálisnak deklarált kategória
                lokális célra mutat (EV5) → **NEM szabad futtatni**: a zöld
                eredmény ilyenkor nem a telepített komponensről szólna
            3 = a tábla helyőrző-hibás: a behelyettesítés dupla útvonal-prefixet
                ad (`test-report/test-report/…` vagy `test-report/specs/…`) →
                **NEM szabad futtatni és NEM szabad subagentre visszaesni**, a
                `plan.md` táblája javítandó (TR5/c)

HELYŐRZŐK a táblában (TR5/c) — kettő van, két különböző bázissal:

  {round} → a repó gyökeréhez relatív TELJES kör-mappa
            (`specs/cycle-NN-<name>/test-report/validate/round-02`)
  {phase} → a `test-report/`-hoz relatív FÁZIS-mappa (`validate/round-02`) —
            ezt várják a projekt riport-parancsai `REPORT_PHASE_DIR` /
            `<phase-dir>` néven

A kettő összekeverése (`…/test-report/{round}`) rekurzív riport-fát épít; a
szkript ezt a futtatás ELŐTT megfogja és exit 3-mal megáll.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

from lang_keys import sec

TABLE_ROW_RE = re.compile(r"^\|(?!\s*-)(.+)\|\s*$")
SEPARATOR_ROW_RE = re.compile(r"^\|[\s:|-]+\|$")
# Másodlagos fejléc-felismerés (5.0): elválasztó sor NÉLKÜL, kézzel írt táblákra.
# Mindkét prompt-fa első oszlop-neve szerepel benne — a szerkezeti ág az elsődleges.
HEADER_FIRST_CELL_WORDS = ("kategória", "kategoria", "category")
EMPTY = ("", "-", "—", "n/a", "na", "nincs")


def strip_cell(cell):
    return cell.strip().strip("`").strip()


def parse_matrix(plan_text):
    """A gépi futtatási tábla sorai dict-ként. Üres lista = nincs tábla."""
    m = re.search(r"^#+\s*" + re.escape(sec("machine_run_table")) + r".*$",
                  plan_text, re.MULTILINE | re.IGNORECASE)
    if not m:
        return []
    tail = plan_text[m.end():]
    nxt = re.search(r"^#+\s", tail, re.MULTILINE)
    block = tail[: nxt.start()] if nxt else tail

    # A FEJLÉCSOR felismerése SZERKEZETBŐL, nem szóból (5.0). A korábbi
    # literál-lista (`kategória`/`kategoria`) csak a magyar projekt-nyelvre
    # illeszkedett: egy angol fejlécű (`| Category | Type | … |`) tábla ELSŐ
    # SORA adatsorként került a listába, és a szkript megpróbálta lefuttatni a
    # `Command` szót shell parancsként. A fejléc az a sor, amelyet KÖZVETLENÜL
    # elválasztó sor (`|---|---|…`) követ — ez nyelvfüggetlen. A literál-listát
    # másodlagos ágként megtartjuk, hogy az elválasztó nélkül, kézzel írt
    # táblák se törjenek el.
    lines = [l.strip() for l in block.splitlines()]
    header_idx = None
    for i, line in enumerate(lines):
        if SEPARATOR_ROW_RE.match(line) and i > 0 and TABLE_ROW_RE.match(lines[i - 1]):
            header_idx = i - 1
            break

    rows = []
    for i, line in enumerate(lines):
        if header_idx is not None and i == header_idx:
            continue
        mm = TABLE_ROW_RE.match(line)
        if not mm:
            continue
        cells = [strip_cell(c) for c in mm.group(1).split("|")]
        if not cells or cells[0].lower() in HEADER_FIRST_CELL_WORDS:
            continue
        while len(cells) < 9:
            cells.append("")
        rows.append({
            "kategoria": cells[0],
            "tipus": cells[1].lower(),
            "elofeltetel": cells[2],
            "parancs": cells[3],
            "eredmeny": cells[4],
            "formatum": (cells[5] or "junit").lower(),
            "takaritas": cells[6],
            "kornyezet": cells[7],
            "fazis": cells[8].strip().lower().strip("`*"),
        })
    return [r for r in rows if r["kategoria"] and r["parancs"] not in EMPTY]


PHASE_ALIASES = {
    "implement": "implement", "implementáció": "implement", "implementacio": "implement",
    "06": "implement",
    "validate": "validate", "validálás": "validate", "validalas": "validate", "07": "validate",
}
PHASE_BOTH_WORDS = {"", "—", "-", "n/a", "na", "mindkettő", "mindketto", "both", "mind", "all",
                    "implement+validate", "implement, validate", "implement/validate"}


def row_phases(row):
    """A sor FÁZIS cellája → a fázisok halmaza, amelyekben a kategória fut.

    Jelöletlen sor MINDEN fázisban fut (PH1): a hallgatás soha nem jelenthet
    kihagyást — egy véletlenül üresen hagyott cella nem tüntethet el tesztet a
    validálásból. Több érték `,` / `/` / `+` jellel is felsorolható."""
    raw = (row.get("fazis") or "").strip().lower()
    if raw in PHASE_BOTH_WORDS:
        return {"implement", "validate"}
    out = set()
    for part in re.split(r"[,;/+ ]+", raw):
        if not part:
            continue
        mapped = PHASE_ALIASES.get(part)
        if mapped:
            out.add(mapped)
    return out or {"implement", "validate"}


def is_empty(value):
    return (value or "").strip().lower() in EMPTY


def subst(value, round_dir, phase_dir=""):
    """Helyőrző-behelyettesítés (TR5/c) — KÉT helyőrző, két bázissal:

      {round} → a repó gyökeréhez relatív teljes kör-mappa
                (`specs/cycle-NN-<name>/test-report/validate/round-02`)
      {phase} → a `test-report/`-hoz relatív fázis-mappa (`validate/round-02`),
                azaz amit a projekt riport-parancsai `REPORT_PHASE_DIR` /
                `<phase-dir>` néven várnak

    A kettő összekeverése rekurzív `test-report/test-report/…` és
    `test-report/specs/…` fát hoz létre — ezt a `check_placeholder_collision`
    fogja meg, mielőtt bármi lefutna."""
    out = (value or "").replace("{round}", str(round_dir).replace("\\", "/"))
    return out.replace("{phase}", phase_dir)


COLLISION_RE = re.compile(r"test-report/(test-report|specs)/")
LOCAL_HOST_RE = re.compile(r"\b(?:localhost|127\.0\.0\.1|0\.0\.0\.0|\[::1\])\b")
LOCAL_ENV_WORDS = {"lokális", "lokalis", "local", "localhost", "helyi", "—", "-", "n/a", "na"}


def env_is_local(value):
    v = (value or "").strip().lower().strip("`*")
    return (not v) or all(w in LOCAL_ENV_WORDS for w in re.split(r"[,;/+ ]+", v) if w)


def check_environment_mismatch(rows):
    """EV5 futásidejű védőháló — nem-lokális kategória lokális célra mutat.

    Ez az a hibaosztály, ahol MINDEN teszt zöld lesz, miközben a telepített
    komponenst senki nem szólította meg: egy `…:dev-e2e` nevű script configjában
    `baseURL: "http://127.0.0.1:5178"` áll. A név nem bizonyíték, a cím az."""
    bad = []
    for row in rows:
        if env_is_local(row.get("kornyezet")):
            continue
        for field in ("parancs", "elofeltetel"):
            m = LOCAL_HOST_RE.search(row.get(field) or "")
            if m:
                bad.append((row["kategoria"], row["kornyezet"], field, m.group(0)))
    return bad


# ── EV7 — a parancs env-változói nem DEKORÁCIÓK ─────────────────────────────
# Miért kell: egy éles ciklus dev-kategóriájának parancsa `TEST_ENV=dev
# DEV_BASE_URL=…`-t állított. Mindkét változó NULLA találat volt a célprojekt
# `test/` fájában — a kód `TMP_BASE_URL`-t és `RUN_DEV_E2E`-t olvasott. Vagyis a
# „dev" futás bájtra ugyanaz volt, mint a lokális, miközben minden bizonyíték
# (a parancs, a `results.json` `kornyezet` mezője, a napló) devnek látszott.
# Az EV3 a cél-HOSTot méri a parancsban — az ott volt; ami hiányzott, az a
# változó és a KÓD közti kötés.
ENV_ASSIGN_RE = re.compile(r"(?:^|[\s;&|(])([A-Z][A-Z0-9_]{2,})=")
PATH_TOKEN_RE = re.compile(r"[\w.\-/]*[\w\-]/[\w.\-/]*|[\w.\-/]+\.(?:py|ts|tsx|js|mjs|cjs|jsx)")
CODE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".mjs", ".cjs", ".jsx", ".json",
                 ".yaml", ".yml", ".ini", ".cfg", ".toml"}
MAX_SCANNED_FILES = 400


def _code_candidates(parancs, repo_root):
    """A parancs által futtatott ÚTVONAL-jelöltek, amelyek léteznek is."""
    out = []
    for token in PATH_TOKEN_RE.findall(parancs or ""):
        token = token.strip("`\"'").rstrip("/")
        if not token or token.startswith("-"):
            continue
        path = Path(repo_root) / token
        if path.exists() and path not in out:
            out.append(path)
    return out


def _scan_files(candidates):
    """A jelölt fájlok/könyvtárak olvasandó szöveges állományai."""
    files = []
    for path in candidates:
        if path.is_file():
            if path.suffix.lower() in CODE_SUFFIXES or path.name.startswith(".env"):
                files.append(path)
            continue
        for sub in sorted(path.rglob("*")):
            if not sub.is_file():
                continue
            if sub.suffix.lower() in CODE_SUFFIXES or sub.name.startswith(".env"):
                files.append(sub)
            if len(files) >= MAX_SCANNED_FILES:
                return files
    return files


def check_env_binding(rows, repo_root):
    """EV7 — a NEM-lokális kategóriák parancsában beállított env-változók
    megjelennek-e a futtatott teszt-kódban.

    Visszaad: [(kategória, környezet, [nem kötött változók], típus, hány fájlt néztünk)]
    és külön a KIHAGYOTT sorok listáját (nem tudjuk, mit futtat a parancs)."""
    findings, skipped = [], []
    for row in rows:
        if env_is_local(row.get("kornyezet")):
            continue
        parancs = row.get("parancs") or ""
        variables = list(dict.fromkeys(ENV_ASSIGN_RE.findall(parancs)))
        if not variables:
            continue                # a cél-host kapcsolóban is lehet — azt az EV3 méri
        candidates = _code_candidates(parancs, repo_root)
        files = _scan_files(candidates)
        if not files:
            skipped.append((row["kategoria"], variables))
            continue
        blobs = []
        for path in files:
            try:
                blobs.append(path.read_text(encoding="utf-8", errors="ignore"))
            except OSError:
                continue
        haystack = "\n".join(blobs)
        unbound = [v for v in variables if v not in haystack]
        if unbound:
            findings.append((row["kategoria"], (row.get("kornyezet") or "—").strip(),
                             unbound, row.get("tipus", ""), len(files)))
    return findings, skipped


# ── EV6 (F3) — FORGALMI bizonyíték nem-lokális kategóriánál ─────────────────
# Az EV1–EV5 a CÉLPONTOT védi a futtatás ELŐTT (host a parancsban, elérhetőségi
# probe, localhost-tilalom). A lánc viszont egy lépéssel korábban is elszakad:
# ott nem az volt a kérdés, HOL futott a teszt, hanem hogy FUTOTT-E EGYÁLTALÁN
# forgalom. Egy éles ciklusban a dev E2E tesztek egyetlen dev kérést sem
# indítottak (a teszt-törzsek `assert True` vázak voltak), a kör mappájában mégis
# 50 REST-napló állt — mind korábbi körből örökölt, mind `127.0.0.1`-es.
# Ezért a futtatás UTÁN megnézzük: a körben KELETKEZETT bizonyítékok közt van-e
# olyan, amely a CÉL-HOSTot tartalmazza.
HOST_RE = re.compile(r"https?://([A-Za-z0-9._-]+(?::\d+)?)")
AUDIT_TEXT_SUFFIXES = {".log", ".txt", ".json", ".jsonl", ".ndjson", ".har", ".http", ".md",
                       ".xml", ".yaml", ".yml", ".csv"}


def _load_report_gate_module():
    """A `report-gate-check.py` betöltése modulként (a kötőjeles név miatt importlib).

    A TR3 tábla parse-olója ott él; **szándékosan nem írjuk meg másodszor** —
    egy harmadik táblaalak-értelmezés a két kapu csendes szétcsúszását adná.
    """
    import importlib.util
    path = Path(__file__).resolve().parent / "report-gate-check.py"
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location("_report_gate_check", path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception:
        return None
    return module


def audit_artifacts(conventions_path):
    """A TR3 táblában deklarált artefaktum-útvonalak (kör-mappán belüli relatív alakok).

    Visszatérés: (útvonalak listája, hiba-ok). Ha a `conventions.md` nincs meg vagy
    nincs benne TR3 tábla, `(None, ok)` — az EV6 ilyenkor KIMARAD (nem bukat).
    """
    if not conventions_path or not Path(conventions_path).exists():
        return None, f"nincs {conventions_path or 'conventions.md'}"
    module = _load_report_gate_module()
    if module is None:
        return None, "a report-gate-check.py nem betölthető (a TR3 parse-oló ott él)"
    section = module.extract_section(Path(conventions_path).read_text(encoding="utf-8"))
    if not section:
        return None, "a conventions.md-ben nincs teszt-riportolási (TR3) szekció"
    rows = module.parse_rows(section)
    paths = [r[3] for r in rows if r[3].lower() not in module.EMPTY_VALUES]
    if not paths:
        return None, "a TR3 tábla nem deklarál artefaktumot"
    return paths, None


def target_hosts(row):
    """A kategória cél-hostjai a `Parancs` és az `Előfeltétel` cellából (EV3 mintája)."""
    hosts = set()
    for field in ("parancs", "elofeltetel"):
        for host in HOST_RE.findall(row.get(field) or ""):
            if not LOCAL_HOST_RE.search(host):
                hosts.add(host.split(":")[0])
    return sorted(hosts)


def check_traffic_evidence(rows, round_dir, audit_paths, since):
    """EV6 — a körben keletkezett bizonyíték tartalmazza-e a cél-hostot.

    [(kategória, host, indoklás, erős-e)] a gyanús kategóriákra.

    A cél-host **hiánya önmagában gyenge jel**: sok projekt artefaktuma (Allure
    JSON, JUnit XML, Playwright trace) egyáltalán nem rögzít hostot — egy lezárt,
    rendben lévő ciklus is „hiányzó forgalomnak" tűnne, és egy kapu, ami a jó
    ciklust is bukatja, használhatatlan. Ezért:

      · a cél-host megvan a körben keletkezett audit-fájlban  → rendben;
      · nincs meg, DE a körben keletkezett bizonyíték **lokális** hostot
        tartalmaz (`localhost`, `127.0.0.1`) → **erős** jel: a forgalom máshová
        ment, mint a deklarált környezet → FAIL (ez a `cycle-30` szignatúrája:
        `rest-logs` tele `127.0.0.1:3028`-cal, dev kategóriánál);
      · nincs meg, és host egyáltalán nem szerepel → **javaslat** (BD5 óvatossági
        ág szellemében): az artefaktum nem rögzít hostot, ezt nem bukatjuk meg.

    `audit_paths` `None` (a TR3 tábla nem deklarál audit-artefaktumot) → minden
    találat javaslat.
    """
    problems = []
    for row in rows:
        if env_is_local(row.get("kornyezet")):
            continue
        hosts = target_hosts(row)
        if not hosts:
            continue                     # nincs miből host-ot kinyerni — nem találgatunk
        candidates = []
        for rel in (audit_paths or []):
            target = round_dir / rel
            if target.is_dir():
                candidates += [p for p in target.rglob("*") if p.is_file()]
            elif target.is_file():
                candidates.append(target)
        fresh = [p for p in candidates
                 if since is None or p.stat().st_mtime >= since]
        hit, local_hit = None, None
        for path in fresh:
            if path.suffix.lower() not in AUDIT_TEXT_SUFFIXES:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if any(h in text for h in hosts):
                hit = path
                break
            if local_hit is None and LOCAL_HOST_RE.search(text):
                local_hit = path
        if hit is None:
            if local_hit is not None:
                detail = (f"{len(fresh)} friss audit-fájl a körben; a cél-host egyikben sem "
                          f"szerepel, viszont a(z) `{local_hit.name}` LOKÁLIS címet tartalmaz "
                          "— a forgalom máshová ment")
                strong = True
            else:
                detail = (f"{len(fresh)} friss audit-fájl a körben, egyikben sem szerepel a "
                          "cél-host (és lokális cím sem — lehet, hogy ez az artefaktum nem "
                          "rögzít hostot)")
                strong = False
            problems.append((row["kategoria"], ", ".join(hosts), detail, strong))
    return problems


def check_placeholder_collision(rows, round_dir, phase_dir):
    """Dupla útvonal-prefix a behelyettesített parancsokban (TR5/c) → hibalista.

    Tipikus eset: a plan táblája `…/test-report/{round}`-ot ír, de a `{round}`
    már tartalmazza a `test-report/`-ot is. Ilyenkor `{phase}` a helyes helyőrző."""
    bad = []
    for row in rows:
        for field in ("parancs", "eredmeny", "elofeltetel", "takaritas"):
            text = subst(row.get(field), round_dir, phase_dir)
            if COLLISION_RE.search(text):
                bad.append((row["kategoria"], field, text))
    return bad


def normalize_round_dir(raw, cycle):
    """A kör-mappa háromféle alakját egyre hozza (TR5/c) → (teljes útvonal, fázis-mappa).

    Ugyanannak a fogalomnak három bázisa van a rendszerben, és a leggyakoribb hiba
    a bázisok összekeverése — a másik alak beragasztása rekurzív `test-report/…`
    fát hoz létre. Ezért mind a hármat elfogadjuk:

        specs/cycle-NN-<name>/test-report/validate/round-02   (repó-gyökér bázis)
        test-report/validate/round-02                         (ciklus-mappa bázis)
        validate/round-02                                     (test-report bázis — ez a fázis-mappa)

    A `teljes útvonal` a repó gyökeréhez relatív (ide írunk és ezt kapja a `{round}`),
    a `fázis-mappa` pedig az az alak, amit a projekt riport-parancsai várnak
    (`REPORT_PHASE_DIR` / `<phase-dir>` helyőrző)."""
    parts = [x for x in str(raw).replace("\\", "/").strip("/").split("/") if x and x != "."]
    if cycle.name in parts:
        parts = parts[parts.index(cycle.name) + 1:]
    if parts and parts[0] == "test-report":
        parts = parts[1:]
    phase_dir = "/".join(parts) or "validate/round-01"
    return cycle / "test-report" / phase_dir, phase_dir


def run_shell(cmd, cwd, timeout):
    started = time.time()
    try:
        # Az explicit utf-8 + errors='replace' azért kell, mert Windowson a
        # text=True a konzol kódlapjával dekódolna: egy UTF-8-at kiíró teszt-
        # futtató kimenete vagy elromlana, vagy UnicodeDecodeError-t dobna.
        proc = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True,
                              text=True, encoding='utf-8', errors='replace',
                              timeout=timeout)
        return proc.returncode, proc.stdout + proc.stderr, time.time() - started
    except subprocess.TimeoutExpired:
        return 124, f"IDŐTÚLLÉPÉS ({timeout}s) — a parancs nem fejeződött be.", time.time() - started


def parse_junit(path):
    """(passed, failed, skipped, [bukott tesztnevek]) egy JUnit XML-ből."""
    try:
        root = ET.parse(path).getroot()
    except Exception:
        return None
    suites = [root] if root.tag == "testsuite" else root.iter("testsuite")
    total = failures = errors = skipped = 0
    failed_names = []
    for suite in suites:
        total += int(suite.get("tests", 0) or 0)
        failures += int(suite.get("failures", 0) or 0)
        errors += int(suite.get("errors", 0) or 0)
        skipped += int(suite.get("skipped", 0) or 0)
        for case in suite.iter("testcase"):
            if case.find("failure") is not None or case.find("error") is not None:
                cls = case.get("classname", "")
                name = case.get("name", "")
                failed_names.append(f"{cls} > {name}".strip(" >") if cls else name)
    failed = failures + errors
    passed = max(total - failed - skipped, 0)
    return passed, failed, skipped, failed_names


def junit_zero_time(path):
    """(minden eset 0.000 s alatt futott?, esetek száma) egy JUnit XML-ből — TB3.

    KÜLÖN segédfüggvény, nem a `parse_junit()` visszatérési értékének bővítése:
    a `results.json` szerkezetét és a meglévő fogyasztókat (`dod-check.py`,
    `round-log.py`) nem törjük el egy heurisztika kedvéért.
    """
    try:
        root = ET.parse(path).getroot()
    except Exception:
        return None, 0
    cases = list(root.iter("testcase"))
    if not cases:
        return None, 0
    def zero(case):
        raw = case.get("time")
        if raw in (None, ""):
            return True
        try:
            return float(raw) == 0.0
        except ValueError:
            return False
    return all(zero(c) for c in cases), len(cases)


TEXT_PATTERNS = [
    (r"(\d+)\s+passed", "passed"),
    (r"(\d+)\s+failed", "failed"),
    (r"(\d+)\s+skipped", "skipped"),
    (r"Tests run:\s*(\d+)", "total"),
    (r"Failures:\s*(\d+)", "failed"),
    (r"ok\s+(\d+)", None),
]


def parse_text(output):
    got = {}
    for pattern, kind in TEXT_PATTERNS:
        if not kind:
            continue
        m = re.search(pattern, output, re.IGNORECASE)
        if m:
            got[kind] = int(m.group(1))
    if "total" in got and "passed" not in got:
        got["passed"] = got["total"] - got.get("failed", 0) - got.get("skipped", 0)
    if not got:
        return None
    return got.get("passed", 0), got.get("failed", 0), got.get("skipped", 0), []


def _force_utf8_output():
    """Windows-kompatibilitás: a konzol örökölt kódlapja (cp852 / cp1250 / cp1252)
    nem tudja megjeleníteni a kimenet tipográfiai és ékezetes karaktereit (✓, ✗, —, ő),
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
    parser = argparse.ArgumentParser(
        description="Tesztek futtatása a plan.md gépi táblájából, gépi összegzéssel.")
    parser.add_argument("plan_file", help="specs/cycle-NN-<name>/plan.md")
    parser.add_argument("--round-dir", required=True,
                        help="a kör riport-mappája; mind a három útvonal-alak elfogadott "
                             "(TR5/c): `specs/cycle-NN-<name>/test-report/validate/round-NN`, "
                             "`test-report/validate/round-NN` vagy `validate/round-NN`")
    parser.add_argument("--type", default="all", choices=["gyors", "nehez", "all"],
                        help="mely típusú kategóriák fussanak (VD10 kör-típus)")
    parser.add_argument("--phase", default="all", choices=["implement", "validate", "all"],
                        help="mely FÁZIS kategóriái fussanak (PH1) — a tábla `Fázis` oszlopa "
                             "alapján. A jelöletlen (üres) sor MINDEN fázisban fut, tehát a "
                             "hallgatás sosem jelent kihagyást. A 06 `--phase implement`-tel, "
                             "a 07 `--phase validate`-tel hívja")
    parser.add_argument("--only", action="append", default=[],
                        help="csak ezek a kategóriák fussanak (könnyű körben a bukott item)")
    parser.add_argument("--repo", default=".", help="a parancsok futtatási könyvtára")
    parser.add_argument("--conventions", default="conventions.md",
                        help="a projekt conventions.md-je — az EV6 forgalmi bizonyíték "
                             "checkhez (a TR3 tábla audit-artefaktumai). Ha nem létezik, "
                             "az EV6 kimarad egy `·` sorral (nem bukat)")
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--json", default=None, help="gépi eredmény ide (alap: <round-dir>/results.json)")
    parser.add_argument("--dry-run", action="store_true", help="csak a futtatandó parancsokat listázza")
    args = parser.parse_args()
    # A kör KEZDETE — a report-gate-check.py frissesség-padlója (TR7) ebből dolgozik:
    # a results.json a futás VÉGÉN íródik, tehát a saját mtime-ja padlóként
    # minden, a körben keletkezett artefaktumot elavultnak minősítene.
    started_at = time.time()

    plan = Path(args.plan_file)
    if not plan.exists():
        print(f"HIBA: nincs ilyen plan: {plan}", file=sys.stderr)
        return 2
    matrix = parse_matrix(plan.read_text(encoding="utf-8"))
    if not matrix:
        print("HIBA: a plan.md nem tartalmaz `### Gépi futtatási tábla` szekciót (TR4). "
              "Ez a 03 fázis hiánya — essen vissza a hívó a `test-runner` subagentre, "
              "és jelezze a plan kiegészítésének igényét.", file=sys.stderr)
        return 2

    matrix_all = matrix
    if args.phase != "all":
        matrix = [r for r in matrix if args.phase in row_phases(r)]
        if not matrix:
            print(f"MEGJEGYZÉS (PH1): a tábla egyetlen kategóriája sem fut a `{args.phase}` "
                  f"fázisban ({len(matrix_all)} sorból) — nincs mit futtatni.")
            return 0

    selected = matrix
    if args.only:
        wanted = {o.lower() for o in args.only}
        selected = [r for r in matrix if r["kategoria"].lower() in wanted]
        missing = wanted - {r["kategoria"].lower() for r in matrix}
        if missing:
            print(f"HIBA: ismeretlen kategória a táblában: {', '.join(sorted(missing))}",
                  file=sys.stderr)
            return 2
    elif args.type != "all":
        want = "gyors" if args.type == "gyors" else "nehéz"
        selected = [r for r in matrix
                    if r["tipus"].startswith(want[:4]) or r["tipus"].startswith("nehe" if want == "nehéz" else "gyor")]
    if not selected:
        print(f"HIBA: a táblában nincs `{args.type}` típusú kategória "
              f"(fázis-szűrő: {args.phase}).", file=sys.stderr)
        return 2

    round_dir, phase_dir = normalize_round_dir(args.round_dir, plan.parent)
    if str(round_dir).replace("\\", "/") != str(args.round_dir).replace("\\", "/").strip("/"):
        print(f"MEGJEGYZÉS (TR5/c): a --round-dir értéke `{args.round_dir}` volt, "
              f"a szkript repó-relatív alakra normalizálta: `{round_dir}`.")
    round_dir.mkdir(parents=True, exist_ok=True)
    print(f"REPORT_PHASE_DIR={phase_dir}   ← EZT az alakot várják a conventions.md "
          f"riport-parancsai (a `<phase-dir>` helyőrző / a környezeti változó); "
          f"soha ne a fenti teljes útvonalat.")

    sys.stdout.flush()
    mismatch = check_environment_mismatch(selected)
    if mismatch:
        print("HIBA (EV5) — nem-lokális kategória LOKÁLIS célra mutat:", file=sys.stderr)
        for kat, env, field, hit in mismatch:
            print(f"  ✗ {kat} [{env}] / {field}: `{hit}`", file=sys.stderr)
        print("\nEz az a hibaosztály, ahol minden teszt zöld lesz, miközben a telepített "
              "komponenst senki nem szólította meg. A parancs célpontját a deklarált "
              "környezethez kell igazítani (a plan.md gépi futtatási táblájában), vagy a "
              "kategória `Környezet` oszlopát kell `lokális`-ra javítani, ha tényleg ott fut.",
              file=sys.stderr)
        return 4

    # ── EV7 — env-változó kötés (JAVASLAT-szint, a futtatás ELŐTT) ──
    # A kilépő kódot SZÁNDÉKOSAN nem befolyásolja: egy szokatlan, de működő
    # kapcsoló-átadás (pl. `pytest.ini`-ből vagy conftest-ből olvasott név)
    # hamis pozitív lenne, és egy futást megállító hamis pozitív a legdrágább
    # hiba. A kimenetben viszont ott áll, és a `results.json` `suggestions`
    # tömbjébe is bekerül — a kör naplója így hordozza.
    env_findings, env_skipped = check_env_binding(selected, args.repo)
    ev7_notes = []
    for kat, kornyezet, unbound, tipus, n_files in env_findings:
        loud = len(unbound) == 1 and (tipus or "").startswith("neh")
        ev7_notes.append(
            ("🔴 " if loud else "") +
            f"[EV7] a `{kat}` ({kornyezet}) parancsa "
            + ", ".join(f"`{v}=…`" for v in unbound)
            + f"-t állít, de {'ez a változónév' if len(unbound) == 1 else 'ezek a változónevek'} "
              f"a futtatott teszt-kódban nem szerepel{'nek' if len(unbound) > 1 else ''} "
              f"({n_files} fájlt néztünk át) — a beállítás DEKORÁCIÓ: a futás ugyanaz, mint "
              f"lokálisan, miközben minden bizonyíték `{kornyezet}`-nek látszik. Vagy a kód "
              f"olvassa be a változót, vagy a parancs a TÉNYLEGES kapcsolót használja")
    for kat, variables in env_skipped:
        ev7_notes.append(
            f"[EV7] a `{kat}` parancsa " + ", ".join(f"`{v}`" for v in variables)
            + " változót állít, de a parancsból nem sikerült létező teszt-útvonalat "
              "kiolvasni — a kötés nem ellenőrizhető (a check kimarad)")
    for note in ev7_notes:
        print(f"  {'✗' if note.startswith('🔴') else '·'} {note}")
    sys.stdout.flush()

    collisions = check_placeholder_collision(selected, round_dir, phase_dir)
    if collisions:
        print("HIBA (TR5/c) — dupla útvonal-prefix a gépi futtatási tábla parancsaiban:",
              file=sys.stderr)
        for kat, field, text in collisions:
            print(f"  ✗ {kat} / {field}: {text}", file=sys.stderr)
        print("\nA `{round}` helyőrző a TELJES, repó-relatív kör-mappa "
              f"(`{round_dir}`) — nem szabad `test-report/` elé írni. Ha a parancs "
              "a `test-report/`-hoz relatív fázis-mappát várja, használd a `{phase}` "
              f"helyőrzőt (`{phase_dir}`). Javítsd a plan.md gépi tábláját, "
              "ne a szkriptet.", file=sys.stderr)
        return 3

    if args.dry_run:
        for row in selected:
            print(f"{row['kategoria']} [{row['tipus']}] @ {(row.get('kornyezet') or '—').strip()}: "
                  f"{subst(row['parancs'], round_dir, phase_dir)}")
        return 0

    results = []
    any_fail = False
    tb3_notes = []          # TB3 — futásidő-heurisztika, SOHA nem FAIL (BD12)
    for row in selected:
        cat = row["kategoria"]
        cmd = subst(row["parancs"], round_dir, phase_dir)
        entry = {"kategoria": cat, "tipus": row["tipus"], "fazis": sorted(row_phases(row)),
                 "parancs": cmd,
                 "kornyezet": (row.get("kornyezet") or "").strip() or "—",
                 "passed": 0, "failed": 0, "skipped": 0, "failed_items": [],
                 "eredmeny": None, "status": "FAIL"}

        if not is_empty(row["elofeltetel"]):
            for pre in row["elofeltetel"].split(";"):
                pre = subst(pre.strip(), round_dir, phase_dir)
                if not pre:
                    continue
                code, out, _ = run_shell(pre, args.repo, args.timeout)
                if code != 0:
                    entry["status"] = "FAIL"
                    entry["failed_items"] = [f"{cat}: előfeltétel-parancs bukott (`{pre}`)"]
                    entry["log_tail"] = out[-800:]
                    results.append(entry)
                    any_fail = True
                    break
            if entry["failed_items"]:
                continue

        code, output, elapsed = run_shell(cmd, args.repo, args.timeout)
        entry["exit_code"] = code
        entry["elapsed_s"] = round(elapsed, 1)

        parsed = None
        result_file = subst(row["eredmeny"], round_dir, phase_dir)
        if not is_empty(result_file):
            src = Path(args.repo) / result_file
            if not src.exists():
                src = Path(result_file)
            if src.exists():
                dest = round_dir / Path(result_file).name
                if src.resolve() != dest.resolve():
                    try:
                        shutil.copy(src, dest)
                    except Exception:
                        dest = src
                entry["eredmeny"] = str(dest)
                if row["formatum"].startswith("junit"):
                    parsed = parse_junit(dest)
                    all_zero, n_cases = junit_zero_time(dest)
                    if all_zero and n_cases:
                        tb3_notes.append(
                            f"[TB3] javaslat: a `{cat}` kategória minden tesztje 0.000 s alatt "
                            f"futott le ({n_cases} eset) — ha a kategória hálózati hívást, "
                            "konkurenciát vagy I/O-t tesztel, ez üres vázra utalhat. "
                            "Nem blokkol; a TB1/TB2 kapu a mérvadó.")
        if parsed is None:
            parsed = parse_text(output)

        if parsed is None:
            entry["status"] = "PASS" if code == 0 else "FAIL"
            entry["megjegyzes"] = ("nem sikerült darabszámot kinyerni — "
                                   "csak a kilépő kód áll rendelkezésre (TR1 gyenge bizonyíték)")
            if code != 0:
                entry["failed_items"] = [f"{cat}: a parancs {code} kilépő kóddal bukott"]
        else:
            passed, failed, skipped, names = parsed
            entry.update(passed=passed, failed=failed, skipped=skipped, failed_items=names)
            if passed + failed + skipped == 0:
                entry["status"] = "FAIL"
                entry["failed_items"] = [f"{cat}: 0 teszt futott"]
                entry["megjegyzes"] = "TR2 — a 0 futtatott teszt FAIL, nem PASS"
            elif failed > 0 or code != 0:
                entry["status"] = "FAIL"
                if not names:
                    entry["failed_items"] = [f"{cat}: {failed} teszt bukott"]
            else:
                entry["status"] = "PASS"

        if entry["status"] == "FAIL":
            any_fail = True
            entry["log_tail"] = output[-1500:]

        if not is_empty(row["takaritas"]):
            for post in row["takaritas"].split(";"):
                post = subst(post.strip(), round_dir, phase_dir)
                if post:
                    run_shell(post, args.repo, args.timeout)

        results.append(entry)

    # ── EV6 — forgalmi bizonyíték a futtatás UTÁN ──
    audit_paths, audit_skip = audit_artifacts(args.conventions)
    traffic = check_traffic_evidence(selected, round_dir, audit_paths, started_at)
    suggestions = list(ev7_notes) + list(tb3_notes)
    for kategoria, host, detail, strong in traffic:
        msg = (f"[EV6] a `{kategoria}` kategória nem-lokális környezetre szól, de a körben "
               f"keletkezett bizonyítékok egyike sem tartalmazza a `{host}` címet — "
               f"a teszt vagy nem futott, vagy nem oda futott ({detail})")
        if audit_paths is None or not strong:
            reason = audit_skip if audit_paths is None else "nincs ellenbizonyíték (lokális cím)"
            suggestions.append(msg + f" · a check csak JAVASLAT: {reason}")
        else:
            suggestions.append("[EV6-FAIL] " + msg)
            for entry in results:
                if entry["kategoria"] == kategoria:
                    entry["status"] = "FAIL"
                    entry.setdefault("failed_items", []).append(f"EV6: nincs forgalmi bizonyíték ({host})")
                    any_fail = True

    out_json = Path(args.json) if args.json else round_dir / "results.json"
    with open(out_json, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"started_at": started_at, "results": results,
                   "suggestions": suggestions}, fh, ensure_ascii=False, indent=2)

    print(f"Teszt-futtatás — kör-mappa: {round_dir}")
    for e in results:
        mark = "✓" if e["status"] == "PASS" else "✗"
        print(f"  {mark} {e['kategoria']} [{e['tipus']}] @ {e.get('kornyezet', '—')} — `{e['parancs']}` → "
              f"{e['passed']} passed / {e['failed']} failed / {e['skipped']} skipped"
              + (f"  ({e['elapsed_s']}s)" if e.get("elapsed_s") else ""))
        if e.get("megjegyzes"):
            print(f"      megjegyzés: {e['megjegyzes']}")
        for name in e["failed_items"][:15]:
            print(f"      ✗ {name}")
    for msg in suggestions:
        if msg in ev7_notes:
            continue            # már kiírtuk a futtatás ELŐTT (EV7)
        print(f"  {'✗' if msg.startswith('[EV6-FAIL]') else '·'} {msg}")
    print(f"  results.json: {out_json}")
    print("VERDICT: " + ("FAIL" if any_fail else "PASS"))
    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main())
