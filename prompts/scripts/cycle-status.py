#!/usr/bin/env python3
import os
import sys
import re
import subprocess
from pathlib import Path

# Színek ANSI escape kódokkal
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RED = "\033[91m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Közvetett bizonyíték: a fázis lefutott (a rákövetkező állapotokból következik),
# de a saját artefaktuma nem áll rendelkezésre az ellenőrzéshez.
INDIRECT = "KÉSZ*"

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
    # Próbáljuk a spec.md-ből beolvasni
    spec_file = cycle_path / "spec.md"
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
            if re.match(r'^[Ss]tátusz\s*:', line_clean):
                parts = line_clean.split(':', 1)
                if len(parts) > 1:
                    return parts[1].strip().lower()
    except Exception:
        pass
    return None

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
    """A roadmap.md-ben a ciklus le van-e zárva (09-merge: `✅` vagy `(kész)` a cím mellett)."""
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
            if '✅' in line or re.search(r'\((?:kész|done|lezárva)\)', line, re.IGNORECASE):
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

def analyze_cycle(cycle_path):
    # Ellenőrizzük a flow típusát
    plan_file = cycle_path / "plan.md"
    is_full_flow = plan_file.exists()
    
    phases = []
    
    spec_file = cycle_path / "spec.md"
    tasks_file = cycle_path / "tasks.md"
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
            if spec_status in ["tervezésre kész", "task írásra kész", "implementálásra kész", "validálásra kész", "kész"]:
                phases.append(("Specifikáció (spec.md)", "KÉSZ"))
            else:
                phases.append(("Specifikáció (spec.md)", "FOLYAMATBAN"))
        else:
            phases.append(("Specifikáció (spec.md)", "MÉG NEM FUTOTT"))

        # 2. Plan
        plan_status = get_status_from_file(plan_file)
        if plan_status:
            if plan_status in ["task írásra kész", "implementálásra kész", "validálásra kész", "kész"]:
                phases.append(("Tervezés (plan.md)", "KÉSZ"))
            else:
                phases.append(("Tervezés (plan.md)", "FOLYAMATBAN"))
        else:
            phases.append(("Tervezés (plan.md)", "MÉG NEM FUTOTT"))

        # 3. Tasks
        tasks_status = get_status_from_file(tasks_file)
        if tasks_status:
            if tasks_status in ["implementálásra kész", "validálásra kész", "kész"]:
                phases.append(("Task lista (tasks.md)", "KÉSZ"))
            else:
                phases.append(("Task lista (tasks.md)", "FOLYAMATBAN"))
        else:
            phases.append(("Task lista (tasks.md)", "MÉG NEM FUTOTT"))

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
            phases.append(("Konzisztencia (analyze-report.md)",
                           "KÉSZ" if analyze_done else "FOLYAMATBAN"))
        elif tasks_status in ["implementálásra kész", "validálásra kész", "kész"]:
            # nincs riport, de a tasks státusza már túllépett az analyze-on
            phases.append(("Konzisztencia (analyze-report.md)", INDIRECT))
        else:
            phases.append(("Konzisztencia (analyze-report.md)", "MÉG NEM FUTOTT"))

        # 5. Megvalósítás
        if tasks_status:
            if tasks_status in ["validálásra kész", "kész"]:
                phases.append(("Megvalósítás (kód írás)", "KÉSZ"))
            elif tasks_status == "implementálásra kész":
                phases.append(("Megvalósítás (kód írás)", "FOLYAMATBAN"))
            else:
                phases.append(("Megvalósítás (kód írás)", "MÉG NEM FUTOTT"))
        else:
            phases.append(("Megvalósítás (kód írás)", "MÉG NEM FUTOTT"))

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
                phases.append(("Validálás + review (test-report)", "KÉSZ"))
            else:
                phases.append(("Validálás + review (test-report)", "FOLYAMATBAN"))
        elif tasks_status == "kész":
            # nincs riport, de a 07 lezárta a ciklus státuszait
            phases.append(("Validálás + review (test-report)", INDIRECT))
        elif tasks_status == "validálásra kész":
            phases.append(("Validálás + review (test-report)", "FOLYAMATBAN"))
        else:
            phases.append(("Validálás + review (test-report)", "MÉG NEM FUTOTT"))

        # 7. Doc-sync — a terv-tételek pipái (DS10) a bizonyíték
        if doc_sync_file.exists():
            try:
                with open(doc_sync_file, 'r', encoding='utf-8') as f:
                    doc_content = f.read()
                # Ha van még befejezetlen checkbox
                doc_status = "FOLYAMATBAN" if "- [ ]" in doc_content else "KÉSZ"
            except Exception:
                doc_status = "FOLYAMATBAN"
        else:
            doc_status = "MÉG NEM FUTOTT"
        phases.append(("Dokumentáció (doc-sync-plan.md)", doc_status))

        # 8. Merge — a 09 tényleges kimeneteiből (roadmap-lezárás, beolvasztott ciklus-ág),
        # NEM a doc-sync-plan.md puszta létezéséből: az a terv legyártásakor jön létre,
        # üres checkboxokkal, tehát semmit nem mond a merge-ről.
        if tasks_status != "kész" or doc_status not in ("KÉSZ", INDIRECT):
            phases.append(("Merge", "MÉG NEM FUTOTT"))
        elif is_roadmap_cycle_closed(cycle_path.name):
            phases.append(("Merge", "KÉSZ"))
        else:
            merged = is_cycle_branch_merged(cycle_path.name)
            if merged is False:
                phases.append(("Merge", "FOLYAMATBAN"))
            elif merged is True:
                phases.append(("Merge", "KÉSZ"))
            else:
                phases.append(("Merge", INDIRECT))

    else:
        # --- SIMPLIFIED (LIGHTWEIGHT) FLOW ---
        # 1. Spec
        spec_status = get_status_from_file(spec_file)
        if spec_status:
            if tasks_file.exists():
                phases.append(("Specifikáció (spec.md)", "KÉSZ"))
            else:
                phases.append(("Specifikáció (spec.md)", "FOLYAMATBAN"))
        else:
            phases.append(("Specifikáció (spec.md)", "MÉG NEM FUTOTT"))

        # 2. Tasks
        tasks_status = get_status_from_file(tasks_file)
        if tasks_status:
            if tasks_status == "kész":
                phases.append(("Feladatlista (tasks.md)", "KÉSZ"))
            else:
                phases.append(("Feladatlista (tasks.md)", "FOLYAMATBAN"))
        else:
            phases.append(("Feladatlista (tasks.md)", "MÉG NEM FUTOTT"))

        # 3. Megvalósítás
        if tasks_status:
            if tasks_status == "kész":
                phases.append(("Megvalósítás (kód + doksi)", "KÉSZ"))
            else:
                phases.append(("Megvalósítás (kód + doksi)", "FOLYAMATBAN"))
        else:
            phases.append(("Megvalósítás (kód + doksi)", "MÉG NEM FUTOTT"))

    # Ciklus szintű összesített státusz meghatározása
    all_done = all(p[1] in ("KÉSZ", INDIRECT) for p in phases)
    any_started = any(p[1] in ("KÉSZ", INDIRECT, "FOLYAMATBAN") for p in phases)
    
    overall_status = "KÉSZ" if all_done else ("FOLYAMATBAN" if any_started else "MÉG NEM FUTOTT")
    
    return is_full_flow, phases, overall_status

def print_cycle_phases(cycle_path):
    name = cycle_path.name
    desc = get_cycle_title_and_desc(cycle_path)
    is_full_flow, phases, overall = analyze_cycle(cycle_path)
    
    flow_str = "Teljes (00-09) flow" if is_full_flow else "Egyszerűsített flow"
    print(f"\n{BOLD}{CYAN}=== CIKLUS STÁTUSZ: {name} ==={RESET}")
    print(f"{BOLD}Leírás:{RESET} {desc}")
    print(f"{BOLD}Típus:{RESET}  {flow_str}")
    
    status_color = GREEN if overall == "KÉSZ" else YELLOW
    print(f"{BOLD}Státusz:{RESET} {status_color}{overall}{RESET}\n")
    
    print(f"{BOLD}Fázisok részletesen:{RESET}")
    for phase_name, p_status in phases:
        if p_status == "KÉSZ":
            p_color = GREEN
        elif p_status == INDIRECT:
            p_color = GREEN + DIM
        elif p_status == "FOLYAMATBAN":
            p_color = YELLOW
        else:
            p_color = DIM
        print(f"  {p_color}● {phase_name:<35} → {p_status}{RESET}")
    if any(p[1] == INDIRECT for p in phases):
        print(f"  {DIM}* = közvetett bizonyíték: a fázis a rákövetkező állapotokból "
              f"lefutottnak tűnik, de a saját artefaktuma nem ellenőrizhető.{RESET}")
    print("")

def text_fallback_menu(cycles):
    print(f"\n{BOLD}{CYAN}=== BERKISPEC CIKLUSOK LISTÁJA ==={RESET}\n")
    
    incomplete_cycles = []
    
    for i, cycle in enumerate(cycles):
        is_full_flow, phases, overall = analyze_cycle(cycle)
        desc = get_cycle_title_and_desc(cycle)
        
        status_color = GREEN if overall == "KÉSZ" else YELLOW
        print(f"  {BOLD}{i+1}. {cycle.name:<25}{RESET} | {status_color}{overall:<12}{RESET} | {desc}")
        
        if overall != "KÉSZ":
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
        if overall != "KÉSZ":
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
            
            flow_type = "Teljes (00-09) flow" if sel_ff else "Egyszerűsített flow"
            stdscr.addstr(5, rx, f"Típus:  {flow_type}")
            stdscr.addstr(6, rx, f"Leírás: {sel_desc[:width-rx-10]}")
            
            stdscr.addstr(8, rx, "FÁZISOK STÁTUSZA:", curses.A_UNDERLINE | curses.A_BOLD)
            
            for p_idx, (phase_name, p_status) in enumerate(sel_phases):
                py = 10 + p_idx
                if py >= height - 3:
                    break
                    
                if p_status == "KÉSZ":
                    pc = curses.color_pair(1)
                elif p_status == INDIRECT:
                    pc = curses.color_pair(1) | curses.A_DIM
                elif p_status == "FOLYAMATBAN":
                    pc = curses.color_pair(2)
                else:
                    pc = curses.A_DIM
                    
                stdscr.attron(pc)
                stdscr.addstr(py, rx, f" ● {p_status:<12}")
                stdscr.attroff(pc)
                stdscr.addstr(f" {phase_name}")
                
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
    # Ha van argumentum (konkrét ciklus név vagy elérési út)
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        # Ha elérési utat adtak meg (pl. specs/cycle-01-...)
        target_path = Path(arg)
        if not target_path.exists():
            # Ha csak nevet adtak meg (pl. cycle-01-...)
            target_path = Path("specs") / arg
            
        if target_path.exists() and target_path.is_dir():
            print_cycle_phases(target_path)
            sys.exit(0)
        else:
            print(f"\n{RED}Error: A megadott ciklus mappa nem létezik: {arg}{RESET}\n")
            sys.exit(1)

    cycles = get_cycles()
    if not cycles:
        print(f"\n{RED}Error: Nem található egyetlen ciklus-mappa sem a `specs/` könyvtárban!{RESET}")
        print(f"{DIM}Kérlek ellenőrizd, hogy létezik-e a `specs/` mappa, és abban vannak-e cycle-NN mappák.{RESET}\n")
        sys.exit(1)
        
    # Ellenőrizzük, hogy terminálban vagyunk-e (interaktív TTY)
    if not sys.stdout.isatty():
        # Nem interaktív fallback: csak kilistázunk mindent
        print(f"\n{CYAN}=== BERKISPEC CIKLUSOK LISTÁJA (Nem interaktív mód) ==={RESET}\n")
        for cycle in cycles:
            is_ff, phases, overall = analyze_cycle(cycle)
            desc = get_cycle_title_and_desc(cycle)
            status_color = GREEN if overall == "KÉSZ" else YELLOW
            print(f"  ● {cycle.name:<25} | {status_color}{overall:<12}{RESET} | {desc}")
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
