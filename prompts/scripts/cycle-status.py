#!/usr/bin/env python3
import json
import os
import sys
import re
import subprocess
from pathlib import Path

from lang_keys import fld, st, ui

# A státusz-összehasonlítás mindenhol KISBETŰS, ezért a kulcsokat is így vesszük.
_S_DONE = st("done").lower()
_S_READY_PLAN = st("ready_for_plan").lower()
_S_READY_TEST_PLAN = st("ready_for_test_plan").lower()
_S_READY_TASKS = st("ready_for_tasks").lower()
_S_READY_IMPL = st("ready_for_implement").lower()
_S_READY_VALIDATE = st("ready_for_validate").lower()
_MTP_PLANNED = st("mtp_planned").lower()
_MTP_AS_BUILT = st("mtp_as_built").lower()

# Színek ANSI escape kódokkal
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RED = "\033[91m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"

# A fázis-állapotok BELSŐ, nyelvfüggetlen kódjai. A megjelenítés a `_S_LABEL`
# táblán át a projekt-nyelvre oldódik fel (`lang_keys.ui`) — az `L13-D15` óta a
# `cycle-status.md` COMMITOLT fájl, tehát egy angol projekt repójába nem mehet
# magyar címke.
DONE = "DONE"
# Közvetett bizonyíték: a fázis lefutott (a rákövetkező állapotokból következik),
# de a saját artefaktuma nem áll rendelkezésre az ellenőrzéshez.
INDIRECT = "DONE*"
IN_PROGRESS = "IN_PROGRESS"
NOT_RUN = "NOT_RUN"
NOT_APPLICABLE = "N/A"
MTP_PLANNED_STATE = "PLANNED"
MTP_AS_BUILT_STATE = "AS_BUILT"


def _s_label(state):
    """A belső állapot-kód → projekt-nyelvi megjelenítés."""
    return {
        DONE: ui("s_done"),
        INDIRECT: ui("s_done_indirect"),
        IN_PROGRESS: ui("s_in_progress"),
        NOT_RUN: ui("s_not_run"),
        NOT_APPLICABLE: ui("s_not_applicable"),
        MTP_PLANNED_STATE: ui("s_planned"),
        MTP_AS_BUILT_STATE: ui("s_as_built"),
    }.get(state, state)

def get_cycles():
    specs_dir = Path("specs")
    if not specs_dir.exists() or not specs_dir.is_dir():
        return []
    
    cycles = []
    # Keresünk minden cycle- sorszámmal rendelkező mappát
    for d in specs_dir.iterdir():
        if d.is_dir() and (d.name.startswith("cycle-") or "cycle" in d.name):
            cycles.append(d)
            
    # Sorszám szerinti rendezés (pl. cycle-01 -> cycle-02)
    def extract_num(path):
        match = re.search(r'cycle-(\d+)', path.name)
        return int(match.group(1)) if match else 999
        
    cycles.sort(key=extract_num)
    return cycles

def get_cycle_title_and_desc(cycle_path):
    # Próbáljuk a spec.md-ből beolvasni (quick-flow ciklusban: spec-plan.md)
    spec_file = cycle_path / "spec.md"
    if not spec_file.exists():
        spec_file = cycle_path / "spec-plan.md"
    if spec_file.exists():
        try:
            with open(spec_file, 'r', encoding='utf-8') as f:
                content = f.read()
            # Megkeressük az első H1-et vagy címsort
            title_match = re.search(r'^#\s+(.*)$', content, re.MULTILINE)
            if title_match:
                title = title_match.group(1).strip()
                # Eltávolítjuk a felesleges "Ciklus NN" sallangot
                clean_title = re.sub(r'^(Ciklus\s*\d+\s*[—-]\s*|Cycle\s*\d+\s*[—-]\s*)', '', title, flags=re.IGNORECASE)
                return clean_title
        except Exception:
            pass

    # Próbáljuk a roadmap.md-ből
    roadmap_file = Path("specs/roadmap.md")
    if roadmap_file.exists():
        try:
            with open(roadmap_file, 'r', encoding='utf-8') as f:
                roadmap_content = f.read()
            # Megkeressük a ciklus nevét a roadmap-ben
            pattern = rf'\|\s*`?{re.escape(cycle_path.name)}`?\s*\|\s*([^|]+)\|'
            match = re.search(pattern, roadmap_content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        except Exception:
            pass

    # Fallback
    name_parts = cycle_path.name.split('-')
    if len(name_parts) > 2:
        return " ".join(name_parts[2:]).capitalize()
    return cycle_path.name.capitalize()

def get_status_from_file(file_path):
    if not file_path.exists():
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Soronként elemezzük a fájlt, megtisztítva a markdown formázásoktól
        for line in content.splitlines():
            line_clean = line.strip().lstrip('-').strip().replace('**', '').replace('*', '').replace('`', '').strip()
            # Ha a megtisztított sor "Státusz:" vagy "státusz:" kezdetű
            if re.match(r'^' + re.escape(fld("f_status")) + r'\s*:', line_clean,
                        re.IGNORECASE):
                parts = line_clean.split(':', 1)
                if len(parts) > 1:
                    return parts[1].strip().lower()
    except Exception:
        pass
    return None

def count_checkboxes(file_path):
    """(kipipált, összes) markdown-checkbox a fájlban. A státusz-mező nélküli,
    régi quick-flow feladatlistákhoz (QF3): ott a pipák az egyetlen jel."""
    if not file_path.exists():
        return (0, 0)
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception:
        return (0, 0)
    boxes = re.findall(r'^\s*[-*]\s+\[([ xX])\]', content, re.MULTILINE)
    return (sum(1 for b in boxes if b in 'xX'), len(boxes))

def get_manual_test_plan_state(cycle_path):
    """A kézi tesztterv (`/bs-manual-test-plan`, MT8) állapota egyetlen
    megjelenítendő stringként.

    SZÁNDÉKOSAN nem az `analyze_cycle()` `phases` listájába megy (MT14): a
    ciklus összesített státusza a `phases` minden elemének KÉSZ-ségéből
    származik, tehát egy nem-fázis sor ott azt okozná, hogy egy lemergelt,
    lezárt ciklus is örökre FOLYAMATBAN maradjon (és visszakerüljön a nyitott
    ciklusok listájába). Ezért külön helper + külön kiírt sor."""
    plan_file = cycle_path / "manual-test-plan.md"
    if not plan_file.exists():
        return NOT_RUN
    status = get_status_from_file(plan_file)
    if status == _MTP_PLANNED:
        return MTP_PLANNED_STATE
    if status == _MTP_AS_BUILT:
        return MTP_AS_BUILT_STATE
    return IN_PROGRESS

def _git(args):
    """(returncode, stdout). returncode None, ha a git nem elérhető vagy ez nem repo."""
    try:
        r = subprocess.run(["git"] + args, capture_output=True, text=True, timeout=5)
        return r.returncode, r.stdout.strip()
    except Exception:
        return None, ""

def get_report_verdict(file_path, max_lines=40):
    """A riport fejlécében lévő státusz-sor értéke (pl. `**Jelenlegi státusz:** PASS`).
    None, ha a fájl nem létezik vagy nincs benne fejléc-státusz."""
    if not file_path.exists():
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()[:max_lines]
    except Exception:
        return None
    for line in lines:
        clean = line.strip().lstrip('-').strip().replace('**', '').replace('*', '').replace('`', '').strip()
        m = re.match(r'^(?:jelenlegi\s+|végleges\s+|összesített\s+)?státusz\s*:\s*(.+)$', clean, re.IGNORECASE)
        if m:
            return m.group(1).strip().lower()
    return None

def is_roadmap_cycle_closed(cycle_name):
    """A roadmap.md-ben a ciklus le van-e zárva (a merge-ág: `✅` vagy `(kész)` a cím mellett).

    A `⏳` jelölés (L13-D8: „verifikációra vár") NEM lezárás: a ciklus akkor kész,
    ha az UTOLSÓ engedélyezett verifikáció (`VP1`/`VP2`/`VP3`) zöld — a merge
    önmagában csak adminisztráció."""
    roadmap = Path("specs/roadmap.md")
    if not roadmap.exists():
        return False
    num_match = re.search(r'cycle-(\d+)', cycle_name)
    if not num_match:
        return False
    num = int(num_match.group(1))
    try:
        content = roadmap.read_text(encoding='utf-8')
    except Exception:
        return False
    for line in content.splitlines():
        if not line.lstrip().startswith('#'):
            continue
        if re.search(rf'cycle[-\s]*0*{num}\b', line, re.IGNORECASE):
            if '⏳' in line:
                return False          # verifikációra vár (L13-D8)
            if '✅' in line or re.search(r'\((?:kész|done|lezárva|closed)\)', line, re.IGNORECASE):
                return True
    return False

def is_cycle_branch_merged(cycle_name):
    """True/False, ha a ciklus ágának állapota megállapítható; None, ha nem
    (nincs git, nincs azonosítható alap-ág, vagy nincs ciklus-ág)."""
    rc, branches = _git(["for-each-ref", "--format=%(refname:short)", "refs/heads"])
    if rc != 0:
        return None
    names = branches.splitlines()
    base = next((b for b in ("main", "master", "develop", "trunk") if b in names), None)
    if base is None:
        return None
    cycle_branches = [b for b in names if cycle_name in b and b != base]
    if not cycle_branches:
        # nincs ciklus-ág: lehet merge utáni törlés, de az sem biztos, hogy létezett
        return None
    for b in cycle_branches:
        rc_anc, _ = _git(["merge-base", "--is-ancestor", b, base])
        if rc_anc != 0:
            return False  # létező, még be nem olvasztott ciklus-ág
    return True

# ── `## Review and merge` (RM8) — a ciklusvég kapcsolótáblája ────────────────
# A szekciónév, a mezőnevek és az értékek ANGOL LITERÁLOK (L13-D2), ezért itt
# nincs nyelvi feloldás: amit gép olvas, az nyelvfüggetlen.
_RM_FIELD_RE = re.compile(r"^\s*-?\s*\*\*(?P<key>[^:*]+):\*\*\s*(?P<val>.*?)\s*$", re.MULTILINE)


def read_review_and_merge(conventions_path=Path("conventions.md")):
    """A `## Review and merge` szekció mezői {kisbetűs kulcs: érték} alakban.

    Hiányzó szekció → üres dict: a régi (a `list13` előtt inicializált) projekt
    viselkedése változatlan marad, csak a VP2/VP3 sor nem jelenik meg."""
    try:
        text = conventions_path.read_text(encoding="utf-8")
    except OSError:
        return {}
    section = None
    for block in re.split(r"^##\s+", text, flags=re.MULTILINE)[1:]:
        head, _, body = block.partition("\n")
        if head.strip().lower() == "review and merge":
            section = body
            break
    if section is None:
        return {}
    out = {}
    for m in _RM_FIELD_RE.finditer(section):
        val = m.group("val").strip().strip("`")
        # a sablon kitöltetlen sora (`yes | no`) nem érték
        if "|" in val:
            continue
        out[m.group("key").strip().lower()] = val
    return out


def _flag_on(value):
    return (value or "").strip().lower() in ("yes", "igen", "true", "on")


def verification_round_state(cycle_path, phase_dir):
    """Egy merge utáni verifikációs kör állapota a COMMITOLT bizonyítékból.

    A `results.json` a `run-tests.py` gépi eredménye; a `skipped.md` a kimondott
    kihagyás nyoma (RM11). Önbevallást nem fogadunk el — ez ugyanaz az elv,
    mint a `D8` tűzfalnál: a tényt a bizonyítékból vezetjük le."""
    round_dir = cycle_path / "test-report" / phase_dir
    results = round_dir / "results.json"
    if results.exists():
        try:
            data = json.loads(results.read_text(encoding="utf-8"))
        except Exception:
            return IN_PROGRESS, str(results)
        entries = data.get("results", [])
        failed = [e for e in entries if str(e.get("status", "")).lower() not in ("pass", "ok", "passed")]
        return (IN_PROGRESS if failed else DONE), str(results)
    if (round_dir / "skipped.md").exists():
        return DONE, str(round_dir / "skipped.md")
    if round_dir.exists() and any(round_dir.iterdir()):
        return IN_PROGRESS, str(round_dir)
    return NOT_RUN, ""


def test_manager_run_url(cycle_path, phase_dir):
    """A test manager futás-URL-je POINTERKÉNT (TM10), ha a kör riportja hordozza.

    A hiánya NEM hiba (L13-D24): a feltöltés sosem bizonyíték, csak kényelem."""
    results = cycle_path / "test-report" / phase_dir / "results.json"
    try:
        data = json.loads(results.read_text(encoding="utf-8"))
    except Exception:
        return ""
    tm = data.get("test_manager") or {}
    return tm.get("url") or ""


def analyze_cycle(cycle_path):
    # Ellenőrizzük a flow típusát
    plan_file = cycle_path / "plan.md"
    is_full_flow = plan_file.exists()
    
    phases = []
    
    spec_file = cycle_path / "spec.md"
    # A quick-flow spec+terv összevont artefaktuma a `spec-plan.md`; a régi,
    # átnevezés előtt indult ciklusokban `spec.md` — mindkettőt elfogadjuk
    # (ugyanaz a visszafelé kompatibilitás, mint a `task.md` → `tasks.md` esetén).
    if not is_full_flow:
        quick_spec_file = cycle_path / "spec-plan.md"
        if quick_spec_file.exists() or not spec_file.exists():
            spec_file = quick_spec_file
    tasks_file = cycle_path / "tasks.md"
    # az aktuális hely a ciklus analyze/ almappája; a régi (ciklus-gyökér) hely
    # visszafelé kompatibilitásból marad
    analyze_file = cycle_path / "analyze" / "analyze-report.md"
    if not analyze_file.exists():
        analyze_file = cycle_path / "analyze-report.md"
    # az aktuális név a validation-report.md; a két korábbi név visszafelé kompatibilitásból marad
    validate_file_1 = cycle_path / "test-report/validation-report.md"
    validate_file_2 = cycle_path / "test-report/bs-validate-decision.md"
    validate_file_3 = cycle_path / "test-report/validate-decision.md"
    doc_sync_file = cycle_path / "doc-sync-plan.md"
    # a review a 07-validate 2. lépése (RV1) — a jelentés a test-report/ alatt él;
    # a ciklus gyökerében lévő régi útvonal visszafelé kompatibilitásból marad
    review_file = cycle_path / "test-report/code-review.md"
    review_file_legacy = cycle_path / "code-review.md"

    if is_full_flow:
        # --- FULL FLOW (00-09) ---
        # 1. Spec
        spec_status = get_status_from_file(spec_file)
        if spec_status:
            if spec_status in [_S_READY_PLAN, _S_READY_TASKS, _S_READY_IMPL,
                               _S_READY_VALIDATE, _S_DONE]:
                phases.append((ui("ph_spec"), DONE))
            else:
                phases.append((ui("ph_spec"), IN_PROGRESS))
        else:
            phases.append((ui("ph_spec"), NOT_RUN))

        # 2. Plan — a 03 hasítása óta KÉT sor, ugyanabból a státusz-mezőből (D11):
        # a `03a-write-code-plan` a kód-tervet zárja `ready_for_test_plan`-re, a
        # `03b-write-test-plan` a teszt-tervet `ready_for_tasks`-ra. Egy `done`
        # plan mindkettőt KÉSZ-re teszi, tehát az összesített ciklus-státusz
        # logikája nem sérül.
        plan_status = get_status_from_file(plan_file)
        _CODE_PLAN_DONE = [_S_READY_TEST_PLAN, _S_READY_TASKS, _S_READY_IMPL,
                           _S_READY_VALIDATE, _S_DONE]
        _TEST_PLAN_DONE = [_S_READY_TASKS, _S_READY_IMPL, _S_READY_VALIDATE, _S_DONE]
        if plan_status:
            if plan_status in _CODE_PLAN_DONE:
                phases.append((ui("ph_code_plan"), DONE))
            else:
                phases.append((ui("ph_code_plan"), IN_PROGRESS))
            if plan_status in _TEST_PLAN_DONE:
                phases.append((ui("ph_test_plan"), DONE))
            elif plan_status == _S_READY_TEST_PLAN:
                phases.append((ui("ph_test_plan"), IN_PROGRESS))
            else:
                phases.append((ui("ph_test_plan"), NOT_RUN))
        else:
            phases.append((ui("ph_code_plan"), NOT_RUN))
            phases.append((ui("ph_test_plan"), NOT_RUN))

        # 3. Tasks
        tasks_status = get_status_from_file(tasks_file)
        if tasks_status:
            if tasks_status in [_S_READY_IMPL, _S_READY_VALIDATE, _S_DONE]:
                phases.append((ui("ph_tasks"), DONE))
            else:
                phases.append((ui("ph_tasks"), IN_PROGRESS))
        else:
            phases.append((ui("ph_tasks"), NOT_RUN))

        # 4. Analyze — a fejléc státusz-sora a döntő. A puszta "PASS" előfordulás a
        # szövegtörzsben félrevezet (a körnaplóban a FAIL-körök is említik a PASS-t).
        if analyze_file.exists():
            verdict = get_report_verdict(analyze_file)
            if verdict is not None:
                analyze_done = "pass" in verdict
            else:
                # régi, fejléc nélküli riportok: visszaesés a korábbi heurisztikára
                try:
                    analyze_done = "PASS" in analyze_file.read_text(encoding='utf-8')
                except Exception:
                    analyze_done = False
            phases.append((ui("ph_analyze"),
                           DONE if analyze_done else IN_PROGRESS))
        elif tasks_status in [_S_READY_IMPL, _S_READY_VALIDATE, _S_DONE]:
            # nincs riport, de a tasks státusza már túllépett az analyze-on
            phases.append((ui("ph_analyze"), INDIRECT))
        else:
            phases.append((ui("ph_analyze"), NOT_RUN))

        # 5. Megvalósítás
        if tasks_status:
            if tasks_status in [_S_READY_VALIDATE, _S_DONE]:
                phases.append((ui("ph_implement"), DONE))
            elif tasks_status == _S_READY_IMPL:
                phases.append((ui("ph_implement"), IN_PROGRESS))
            else:
                phases.append((ui("ph_implement"), NOT_RUN))
        else:
            phases.append((ui("ph_implement"), NOT_RUN))

        # 6. Validálás (tesztek + kódreview — RV1)
        # Ha van riport, az dönt — a tasks.md státusza NEM írja felül (a 07 állítja `Kész`-re,
        # így önmagában körkörös bizonyíték lenne).
        val_file = next((f for f in (validate_file_1, validate_file_2, validate_file_3)
                         if f.exists()), None)
        review_open = False
        for rf in (review_file, review_file_legacy):
            if rf.exists():
                try:
                    review_open = "- [ ]" in rf.read_text(encoding='utf-8')
                except Exception:
                    review_open = False
                break
        if val_file is not None:
            verdict = get_report_verdict(val_file)
            if verdict is None:
                try:
                    verdict = "pass" if "PASS" in val_file.read_text(encoding='utf-8') else ""
                except Exception:
                    verdict = ""
            if "pass" in verdict and not review_open:
                phases.append((ui("ph_validate"), DONE))
            else:
                phases.append((ui("ph_validate"), IN_PROGRESS))
        elif tasks_status == _S_DONE:
            # nincs riport, de a 07 lezárta a ciklus státuszait
            phases.append((ui("ph_validate"), INDIRECT))
        elif tasks_status == _S_READY_VALIDATE:
            phases.append((ui("ph_validate"), IN_PROGRESS))
        else:
            phases.append((ui("ph_validate"), NOT_RUN))

        # 7. Doc-sync — a terv-tételek pipái (DS10) a bizonyíték
        if doc_sync_file.exists():
            try:
                with open(doc_sync_file, 'r', encoding='utf-8') as f:
                    doc_content = f.read()
                # Ha van még befejezetlen checkbox
                doc_status = IN_PROGRESS if "- [ ]" in doc_content else DONE
            except Exception:
                doc_status = IN_PROGRESS
        else:
            doc_status = NOT_RUN
        phases.append((ui("ph_doc_sync"), doc_status))

        # 8. Merge — a 09 tényleges kimeneteiből (roadmap-lezárás, beolvasztott ciklus-ág),
        # NEM a doc-sync-plan.md puszta létezéséből: az a terv legyártásakor jön létre,
        # üres checkboxokkal, tehát semmit nem mond a merge-ről.
        if tasks_status != _S_DONE or doc_status not in (DONE, INDIRECT):
            phases.append((ui("ph_merge"), NOT_RUN))
        elif is_roadmap_cycle_closed(cycle_path.name):
            phases.append((ui("ph_merge"), DONE))
        else:
            merged = is_cycle_branch_merged(cycle_path.name)
            if merged is False:
                phases.append((ui("ph_merge"), IN_PROGRESS))
            elif merged is True:
                phases.append((ui("ph_merge"), DONE))
            else:
                phases.append((ui("ph_merge"), INDIRECT))

        # 9. A merge utáni verifikációs pontok — CSAK ha a `## Review and merge`
        # szekció bekapcsolta őket (L13-D8: a ciklus az UTOLSÓ engedélyezett
        # verifikáció zöldjekor kész, nem a `07` PASS-nál).
        rm = read_review_and_merge()
        if _flag_on(rm.get("post-merge tests")):
            state, _ = verification_round_state(cycle_path, "post-merge")
            phases.append((ui("ph_post_merge"), state))
        if _flag_on(rm.get("dev deployment test (bs-dev-test)")) or _flag_on(rm.get("dev deployment test")):
            state, _ = verification_round_state(cycle_path, "dev-test")
            phases.append((ui("ph_dev_test"), state))

    else:
        # --- SIMPLIFIED (LIGHTWEIGHT) FLOW ---
        # QF3: a quick-flow második artefaktuma `tasks.md`; a `task.md` (egyes
        # szám) a QF2/QF3 előtti ciklusoké — a régi hely visszafelé
        # kompatibilitásból marad, ahogy az analyze/ és a test-report/ esetén is.
        if not tasks_file.exists():
            legacy_tasks_file = cycle_path / "task.md"
            if legacy_tasks_file.exists():
                tasks_file = legacy_tasks_file
        tasks_label = f'{ui("ph_tasks_light")} ({tasks_file.name})'
        spec_label = f'{ui("ph_spec_plan")} ({spec_file.name})'
        spec_status = get_status_from_file(spec_file)
        tasks_status = get_status_from_file(tasks_file)

        # 1. Spec
        if spec_status:
            if tasks_file.exists():
                phases.append((spec_label, DONE))
            else:
                phases.append((spec_label, IN_PROGRESS))
        elif spec_file.exists():
            # Státusz-mező nélküli (QF2 előtti) ciklus: a bizonyíték KÖZVETETT —
            # a spec megvan, és ha a feladatlista is elkészült belőle, a fázis lezárult.
            phases.append((spec_label,
                           INDIRECT if tasks_file.exists() else IN_PROGRESS))
        else:
            phases.append((spec_label, NOT_RUN))

        # 2. Tasks
        if tasks_status:
            if tasks_status == _S_DONE:
                phases.append((tasks_label, DONE))
            else:
                phases.append((tasks_label, IN_PROGRESS))
        elif tasks_file.exists():
            phases.append((tasks_label, INDIRECT))
        else:
            phases.append((tasks_label, NOT_RUN))

        # 3. Megvalósítás
        if tasks_status:
            if tasks_status == _S_DONE:
                phases.append((ui("ph_implement_light"), DONE))
            else:
                phases.append((ui("ph_implement_light"), IN_PROGRESS))
        elif tasks_file.exists():
            # Státusz nélkül a pipák az egyetlen jel (QF3 visszafelé-kompatibilitás).
            checked, total = count_checkboxes(tasks_file)
            if total and checked == total:
                phases.append((ui("ph_implement_light"), INDIRECT))
            elif checked:
                phases.append((ui("ph_implement_light"), IN_PROGRESS))
            else:
                phases.append((ui("ph_implement_light"), NOT_RUN))
        else:
            phases.append((ui("ph_implement_light"), NOT_RUN))

    # Ciklus szintű összesített státusz meghatározása
    all_done = all(p[1] in (DONE, INDIRECT) for p in phases)
    any_started = any(p[1] in (DONE, INDIRECT, IN_PROGRESS) for p in phases)
    
    overall_status = DONE if all_done else (IN_PROGRESS if any_started else NOT_RUN)
    
    return is_full_flow, phases, overall_status

# ── `--write` — a generált `cycle-status.md` (L13-D9 / L13-D15) ──────────────
# A fájl RENDERING, nem forrás: a bizonyítékból generáljuk, és KAPU SOHA NEM
# OLVASSA. A keret két dolgot kezel élesen külön: a DÖNTÉST perzisztálni kell
# (nem levezethető), a TÉNYT viszont levezetni a bizonyítékból, sosem
# önbevallásból. A „mi futott le" a második kategória — ha az ágens kézzel írná
# bele, hogy `VP2: PASS`, azzal a `report-gate-check.py` mellett egy önbevalló
# bizonyíték-csatorna nyílna. Egy hazudó státuszfájl rosszabb, mint a semmi.
_PHASE_EVIDENCE = [
    ("ph_spec", "spec.md"),
    ("ph_code_plan", "plan.md"),
    ("ph_test_plan", "plan.md"),
    ("ph_tasks", "tasks.md"),
    ("ph_analyze", "analyze/analyze-report.md"),
    ("ph_implement", "tasks.md"),
    ("ph_validate", "test-report/validation-report.md"),
    ("ph_doc_sync", "doc-sync-plan.md"),
    ("ph_merge", "specs/roadmap.md"),
    ("ph_post_merge", "test-report/post-merge/"),
    ("ph_dev_test", "test-report/dev-test/"),
    ("ph_spec_plan", "spec-plan.md"),
    ("ph_tasks_light", "tasks.md"),
    ("ph_implement_light", "tasks.md"),
]


def _evidence_for(label):
    for key, path in _PHASE_EVIDENCE:
        value = ui(key)
        if label == value or label.startswith(value + " ("):
            return path
    return ""


def render_cycle_status(cycle_path):
    """A `cycle-status.md` tartalma stringként."""
    is_full_flow, phases, overall = analyze_cycle(cycle_path)
    desc = get_cycle_title_and_desc(cycle_path)
    flow_str = ui("cs_flow_full") if is_full_flow else ui("cs_flow_light")

    lines = [f"# {ui('cs_title')} — {cycle_path.name}", ""]
    lines.append(f"> {ui('cs_generated_note')}")
    lines.append("")
    lines.append(f"**{ui('cs_description')}:** {desc}")
    lines.append(f"**{ui('cs_type')}:** {flow_str}")
    lines.append(f"**{fld('f_status')}:** {_s_label(overall)}")
    lines.append("")
    lines.append(f"| {ui('cs_phase_col')} | {fld('f_status')} | {ui('cs_evidence')} |")
    lines.append("|---|---|---|")
    for name, state in phases:
        ev = _evidence_for(name)
        lines.append(f"| {name} | {_s_label(state)} | {('`' + ev + '`') if ev else '—'} |")
    if is_full_flow:
        mtp = get_manual_test_plan_state(cycle_path)
        lines.append(f"| {ui('ph_manual_test')} | {_s_label(mtp)} | `manual-test-plan.md` |")
    lines.append("")

    for phase_dir in ("post-merge", "dev-test"):
        url = test_manager_run_url(cycle_path, phase_dir)
        if url:
            lines.append(f"**{ui('cs_test_manager_run')} ({phase_dir}):** {url}")
    if any(test_manager_run_url(cycle_path, d) for d in ("post-merge", "dev-test")):
        lines.append("")

    left = [name for name, state in phases if state not in (DONE, INDIRECT)]
    lines.append(f"## {ui('cs_whats_left')}")
    lines.append("")
    if left:
        lines.extend(f"- {name}" for name in left)
    else:
        lines.append(ui("cs_nothing_left"))
    if any(state == INDIRECT for _, state in phases):
        lines.append("")
        lines.append(f"`{ui('s_done_indirect')}` {ui('cs_indirect_note')}")
    lines.append("")
    return "\n".join(lines)


def write_cycle_status(cycle_path):
    """A `cycle-status.md` kiírása a ciklus mappájának GYÖKERÉBE.

    Miért nem a repó gyökerébe: a keret támogat párhuzamos ciklusokat külön
    worktree-kben (PW3/PW4) — egy közös fájlt két ciklus egyszerre írna, és
    minden merge-nél ütközne. Itt a fájl ütközésmentes, a ciklussal utazik, és
    a merge után ugyanazon a stabil útvonalon él a fő branch-en."""
    target = cycle_path / "cycle-status.md"
    target.write_text(render_cycle_status(cycle_path), encoding="utf-8")
    return target


def print_cycle_phases(cycle_path):
    name = cycle_path.name
    desc = get_cycle_title_and_desc(cycle_path)
    is_full_flow, phases, overall = analyze_cycle(cycle_path)
    
    flow_str = ui("cs_flow_full") if is_full_flow else ui("cs_flow_light")
    print(f"\n{BOLD}{CYAN}=== {ui('cs_title')}: {name} ==={RESET}")
    print(f"{BOLD}{ui('cs_description')}:{RESET} {desc}")
    print(f"{BOLD}{ui('cs_type')}:{RESET}  {flow_str}")

    status_color = GREEN if overall == DONE else YELLOW
    print(f"{BOLD}{fld('f_status')}:{RESET} {status_color}{_s_label(overall)}{RESET}\n")

    print(f"{BOLD}{ui('cs_phases')}:{RESET}")
    for phase_name, p_status in phases:
        if p_status == DONE:
            p_color = GREEN
        elif p_status == INDIRECT:
            p_color = GREEN + DIM
        elif p_status == IN_PROGRESS:
            p_color = YELLOW
        else:
            p_color = DIM
        print(f"  {p_color}● {phase_name:<35} → {_s_label(p_status)}{RESET}")
    if is_full_flow:
        # vizuálisan elkülönített sor (`·`, DIM), hogy ne tűnjön fázisnak
        mtp = get_manual_test_plan_state(cycle_path)
        label = ui("ph_manual_test")
        print(f"  {DIM}· {label:<35} → {_s_label(mtp)}{RESET}")
    if any(p[1] == INDIRECT for p in phases):
        print(f"  {DIM}* {ui('cs_indirect_note')}{RESET}")
    print("")

def text_fallback_menu(cycles):
    print(f"\n{BOLD}{CYAN}=== {ui('cs_list_title')} ==={RESET}\n")
    
    incomplete_cycles = []
    
    for i, cycle in enumerate(cycles):
        is_full_flow, phases, overall = analyze_cycle(cycle)
        desc = get_cycle_title_and_desc(cycle)
        
        status_color = GREEN if overall == DONE else YELLOW
        print(f"  {BOLD}{i+1}. {cycle.name:<25}{RESET} | {status_color}{_s_label(overall):<12}{RESET} | {desc}")
        
        if overall != DONE:
            incomplete_cycles.append(cycle)
            
    if not incomplete_cycles:
        print(f"\n{GREEN}{BOLD}Minden ciklus sikeresen befejeződött! 🎉{RESET}\n")
        sys.exit(0)
        
    print(f"\n{BOLD}Nem befejezett ciklusok fázis-áttekintése:{RESET}")
    print(f"{DIM}Válassz egy számot az áttekintéshez, vagy nyomj Enter-t a kilépéshez.{RESET}")
    for idx, cycle in enumerate(incomplete_cycles):
        print(f"  [{idx+1}] {cycle.name}")
        
    try:
        choice = input(f"\n{BOLD}Választás [1-{len(incomplete_cycles)}]: {RESET}").strip()
        if choice == "":
            print("Kilépés.")
            sys.exit(0)
        val = int(choice) - 1
        if 0 <= val < len(incomplete_cycles):
            print_cycle_phases(incomplete_cycles[val])
        else:
            print(f"{RED}Érvénytelen választás.{RESET}")
    except (ValueError, KeyboardInterrupt, EOFError):
        print("\nKilépés.")

def curses_menu(stdscr, cycles):
    import curses
    
    # Kurzor kikapcsolása
    curses.curs_set(0)
    
    # Színpárok definiálása
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)   # Zöld (KÉSZ)
    curses.init_pair(2, curses.COLOR_YELLOW, -1)  # Sárga (FOLYAMATBAN)
    curses.init_pair(3, curses.COLOR_CYAN, -1)    # Ciklon kék
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLUE) # Kiválasztott sor
    
    incomplete_cycles = []
    all_cycle_info = []
    
    for cycle in cycles:
        is_full_flow, phases, overall = analyze_cycle(cycle)
        desc = get_cycle_title_and_desc(cycle)
        all_cycle_info.append((cycle, is_full_flow, phases, overall, desc))
        if overall != DONE:
            incomplete_cycles.append((cycle, is_full_flow, phases, overall, desc))
            
    if not incomplete_cycles:
        return None  # Kilép, ha nincs nyitott ciklus
        
    current_row = 0
    
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        # Cím sor
        stdscr.attron(curses.A_BOLD | curses.color_pair(3))
        stdscr.addstr(1, 2, "=== BERKISPEC INTERAKTÍV CIKLUS STÁTUSZ ===")
        stdscr.attroff(curses.A_BOLD | curses.color_pair(3))
        stdscr.addstr(2, 2, "Használd a FEL/LE nyilakat a választáshoz, majd nyomj ENTER-t a kilépéshez.")
        
        # Bal oldali lista: Nem befejezett ciklusok
        col_width = min(40, width // 2 - 2)
        stdscr.addstr(4, 2, "NYITOTT CIKLUSOK:", curses.A_UNDERLINE | curses.A_BOLD)
        
        for idx, (cycle, is_ff, phases, overall, desc) in enumerate(incomplete_cycles):
            x = 2
            y = 5 + idx
            
            if y >= height - 3:
                break
                
            status_char = "●"
            # Szín választása
            color = curses.color_pair(2) # sárga folyamatban
            
            if idx == current_row:
                stdscr.attron(curses.color_pair(4))
                stdscr.addstr(y, x, f" {status_char} {cycle.name:<{col_width-5}} ")
                stdscr.attroff(curses.color_pair(4))
            else:
                stdscr.addstr(y, x, f" ")
                stdscr.attron(color)
                stdscr.addstr(status_char)
                stdscr.attroff(color)
                stdscr.addstr(f" {cycle.name:<{col_width-5}}")
                
        # Jobb oldali panel: A kiválasztott ciklus fázisai
        if incomplete_cycles:
            sel_cycle, sel_ff, sel_phases, sel_overall, sel_desc = incomplete_cycles[current_row]
            rx = width // 2
            
            stdscr.attron(curses.A_BOLD | curses.color_pair(3))
            stdscr.addstr(4, rx, f"RÉSZLETEK: {sel_cycle.name}")
            stdscr.attroff(curses.A_BOLD | curses.color_pair(3))
            
            flow_type = ui("cs_flow_full") if sel_ff else ui("cs_flow_light")
            stdscr.addstr(5, rx, f"{ui('cs_type')}:  {flow_type}")
            stdscr.addstr(6, rx, f"{ui('cs_description')}: {sel_desc[:width-rx-10]}")
            
            stdscr.addstr(8, rx, f"{ui('cs_phases')}:", curses.A_UNDERLINE | curses.A_BOLD)
            
            for p_idx, (phase_name, p_status) in enumerate(sel_phases):
                py = 10 + p_idx
                if py >= height - 3:
                    break
                    
                if p_status == DONE:
                    pc = curses.color_pair(1)
                elif p_status == INDIRECT:
                    pc = curses.color_pair(1) | curses.A_DIM
                elif p_status == IN_PROGRESS:
                    pc = curses.color_pair(2)
                else:
                    pc = curses.A_DIM
                    
                stdscr.attron(pc)
                stdscr.addstr(py, rx, f" ● {_s_label(p_status):<12}")
                stdscr.attroff(pc)
                stdscr.addstr(f" {phase_name}")

            if sel_ff:
                py = 10 + len(sel_phases)
                if py < height - 3:
                    stdscr.attron(curses.A_DIM)
                    stdscr.addstr(py, rx, f" · {_s_label(get_manual_test_plan_state(sel_cycle)):<12}")
                    stdscr.attroff(curses.A_DIM)
                    stdscr.addstr(" " + ui("ph_manual_test"))

        stdscr.refresh()
        
        # Billentyűzet olvasása
        key = stdscr.getch()
        
        if key == curses.KEY_UP:
            current_row = (current_row - 1) % len(incomplete_cycles)
        elif key == curses.KEY_DOWN:
            current_row = (current_row + 1) % len(incomplete_cycles)
        elif key in [curses.KEY_ENTER, 10, 13]: # Enter
            return incomplete_cycles[current_row][0]
        elif key == 27: # ESC
            return None

def main():
    args = [a for a in sys.argv[1:] if a != "--write"]
    write_mode = "--write" in sys.argv[1:]

    # Ha van argumentum (konkrét ciklus név vagy elérési út)
    if args:
        arg = args[0]
        # Ha elérési utat adtak meg (pl. specs/cycle-01-...)
        target_path = Path(arg)
        if not target_path.exists():
            # Ha csak nevet adtak meg (pl. cycle-01-...)
            target_path = Path("specs") / arg

        if target_path.exists() and target_path.is_dir():
            if write_mode:
                written = write_cycle_status(target_path)
                print(f"{GREEN}{ui('cs_written')}: {written}{RESET}")
            print_cycle_phases(target_path)
            sys.exit(0)
        else:
            print(f"\n{RED}Error: A megadott ciklus mappa nem létezik: {arg}{RESET}\n")
            sys.exit(1)

    if write_mode:
        print(f"\n{RED}Error: a `--write` módhoz meg kell adni a ciklust "
              f"(pl. `cycle-status.py specs/cycle-NN-<name> --write`).{RESET}\n")
        sys.exit(2)

    cycles = get_cycles()
    if not cycles:
        print(f"\n{RED}Error: Nem található egyetlen ciklus-mappa sem a `specs/` könyvtárban!{RESET}")
        print(f"{DIM}Kérlek ellenőrizd, hogy létezik-e a `specs/` mappa, és abban vannak-e cycle-NN mappák.{RESET}\n")
        sys.exit(1)
        
    # Ellenőrizzük, hogy terminálban vagyunk-e (interaktív TTY)
    if not sys.stdout.isatty():
        # Nem interaktív fallback: csak kilistázunk mindent
        print(f"\n{CYAN}=== {ui('cs_list_title')} ==={RESET}\n")
        for cycle in cycles:
            is_ff, phases, overall = analyze_cycle(cycle)
            desc = get_cycle_title_and_desc(cycle)
            status_color = GREEN if overall == DONE else YELLOW
            print(f"  ● {cycle.name:<25} | {status_color}{_s_label(overall):<12}{RESET} | {desc}")
        print("")
        sys.exit(0)
        
    # Próbáljuk a curses TUI-t futtatni
    try:
        import curses
        selected_cycle = curses.wrapper(curses_menu, cycles)
        if selected_cycle:
            # Kilépés után kiírjuk a kiválasztott ciklus részletes státuszát
            print_cycle_phases(selected_cycle)
    except Exception:
        # Ha a curses nem támogatott vagy meghiúsul (pl. nincs megfelelő TERM változó)
        text_fallback_menu(cycles)

if __name__ == "__main__":
    main()
