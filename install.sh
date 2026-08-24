#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# BerkiSpec Installer
# Telepíti a BerkiSpec agent-eket és skill-eket a célprojektbe symlink-ekkel.
# Supports: Google Antigravity CLI, Claude Code, GitHub Copilot (CLI & IDE)
# ─────────────────────────────────────────────────────────────────────────────

# ── Színek és stílusok ──────────────────────────────────────────────────────
readonly RESET='\033[0m'
readonly BOLD='\033[1m'
readonly DIM='\033[2m'
readonly ITALIC='\033[3m'
readonly UNDERLINE='\033[4m'

readonly RED='\033[38;5;196m'
readonly GREEN='\033[38;5;82m'
readonly YELLOW='\033[38;5;220m'
readonly BLUE='\033[38;5;75m'
readonly CYAN='\033[38;5;45m'
readonly MAGENTA='\033[38;5;213m'
readonly ORANGE='\033[38;5;208m'
readonly WHITE='\033[38;5;255m'
readonly GRAY='\033[38;5;245m'

readonly BG_GREEN='\033[48;5;22m'
readonly BG_RED='\033[48;5;52m'
readonly BG_BLUE='\033[48;5;24m'

# ── BerkiSpec repo detekció ─────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_DIR

readonly HISTORY_FILE="${SCRIPT_DIR}/history"

# A prompt-forrásmappákat NEM itt oldjuk fel: a nyelvenkénti fát
# (`prompts/skills-<lang>` stb.) az install-helper.py `_lang_subdir()`-je
# választja ki. Korábban itt három konstans állt, de egyik sem volt használatban.

# Globális állapot változók
PROJECT_PATH=""
PLATFORM_CHOICE="" # "antigravity" vagy "claude" vagy "copilot"
INSTALL_STATUS=""  # "done" vagy "skipped" (ütközés esetén kihagyva)

# ── Segédfüggvények ─────────────────────────────────────────────────────────
info()    { echo -e "  ${CYAN}ℹ${RESET}  $*"; }

# ── Telepítési előzmény (`history` fájl) ────────────────────────────────────
# A legutóbbi célprojekt útvonalát a repo gyökerében lévő `history` fájlban
# tartjuk, hogy újrafuttatáskor ne kelljen újra begépelni (előre kitöltve
# jelenik meg, Enterrel elfogadható, nyilakkal szerkeszthető). A fájl GÉPFÜGGŐ
# — lokális útvonalat tartalmaz —, ezért a `.gitignore` kizárja.

load_last_project_path() {
  [[ -f "${HISTORY_FILE}" ]] || return 0
  local line
  line="$(grep -E '^LAST_PROJECT_PATH=' "${HISTORY_FILE}" 2>/dev/null | tail -n 1)"
  [[ -n "${line}" ]] || return 0
  printf '%s' "${line#LAST_PROJECT_PATH=}"
}

save_history() {
  local path="$1" platform="$2"
  {
    echo "# BerkiSpec telepítési előzmény — automatikusan generált, ne szerkeszd kézzel."
    echo "# Ebből tölti ki a telepítő az alapértelmezett célmappát újrafuttatáskor."
    echo "LAST_PROJECT_PATH=${path}"
    echo "LAST_PLATFORM=${platform}"
    echo "LAST_INSTALL=$(date '+%Y-%m-%d %H:%M:%S')"
  } > "${HISTORY_FILE}" 2>/dev/null || warn "A telepítési előzményt nem sikerült elmenteni (${HISTORY_FILE})."
}
success() { echo -e "  ${GREEN}✔${RESET}  $*"; }
warn()    { echo -e "  ${YELLOW}⚠${RESET}  $*"; }
error()   { echo -e "  ${RED}✖${RESET}  $*"; }
step()    { echo -e "\n  ${BLUE}▸${RESET} ${BOLD}$*${RESET}"; }

separator() {
  echo -e "  ${DIM}$(printf '─%.0s' {1..68})${RESET}"
}

# ── Logo ────────────────────────────────────────────────────────────────────
show_logo() {
  echo ""
  echo -e "${BOLD}${CYAN}"
  cat << 'LOGO'
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║                                                                       ║
    ║   ██████╗ ███████╗██████╗ ██╗  ██╗██╗███████╗██████╗ ███████╗ ██████╗ ║
    ║   ██╔══██╗██╔════╝██╔══██╗██║ ██╔╝██║██╔════╝██╔══██╗██╔════╝██╔════╝ ║
    ║   ██████╔╝█████╗  ██████╔╝█████╔╝ ██║███████╗██████╔╝█████╗  ██║      ║
    ║   ██╔══██╗██╔══╝  ██╔══██╗██╔═██╗ ██║╚════██║██╔═══╝ ██╔══╝  ██║      ║
    ║   ██████╔╝███████╗██║  ██║██║  ██╗██║███████║██║     ███████╗╚██████╗ ║
    ║   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚══════╝╚═╝     ╚══════╝ ╚═════╝ ║
    ║                                                                       ║
    ╚═══════════════════════════════════════════════════════════════════════╝
LOGO
  echo -e "${RESET}"
  echo -e "  ${DIM}${WHITE}Spec-Driven Development Framework${RESET}"
  echo -e "  ${DIM}${GRAY}v1.2 · Telepítő${RESET}"
  echo ""
  separator
}

# ── Üdvözlés ────────────────────────────────────────────────────────────────
show_welcome() {
  echo ""
  echo -e "  ${WHITE}${BOLD}Üdvözöllek a BerkiSpec telepítőben!${RESET}"
  echo ""
  echo -e "  ${GRAY}Ez a script beállítja a BerkiSpec agent-eket és skill-eket"
  echo -e "  a célprojektedben symlink-ek segítségével.${RESET}"
  echo ""
  echo -e "  ${DIM}BerkiSpec forrás: ${CYAN}${SCRIPT_DIR}${RESET}"
  echo ""
  separator
}

# ── 1. lépés: Projekt mappa bekérése ────────────────────────────────────────
ask_project_path() {
  step "1. lépés: Projekt mappa"
  echo ""
  echo -e "  ${GRAY}Add meg a célprojekt gyökérmappáját."
  echo -e "  ${DIM}💡 Tipp: Az útvonal megadása során használhatod a ${BOLD}Tab${RESET}${DIM} billentyűt"
  echo -e "     az automatikus kiegészítéshez, vagy nyomd meg ${BOLD}kétszer a Tab-ot${RESET}${DIM}"
  echo -e "     az aktuális könyvtár tartalmának kilistázásához.${RESET}"
  echo ""

  local project_path=""
  local last_path
  last_path="$(load_last_project_path)"

  if [[ -n "${last_path}" ]]; then
    if [[ -d "${last_path}" ]]; then
      echo -e "  ${GRAY}Legutóbbi telepítés helye előre kitöltve — ${BOLD}Enter${RESET}${GRAY} = elfogadás, vagy írd át.${RESET}"
    else
      echo -e "  ${GRAY}A legutóbbi telepítési hely már nem létezik (${last_path}) — add meg az újat.${RESET}"
      last_path=""
    fi
    echo ""
  fi

  while true; do
    echo -ne "  ${MAGENTA}❯${RESET} Projekt mappa: "
    read -e -i "${last_path}" -r project_path

    # Tilde kifejtés
    project_path="${project_path/#\~/$HOME}"

    # Trailing slash eltávolítás
    project_path="${project_path%/}"

    if [[ -z "${project_path}" ]]; then
      warn "Kérlek adj meg egy útvonalat."
      continue
    fi

    if [[ ! -d "${project_path}" ]]; then
      error "A mappa nem létezik: ${project_path}"
      echo -e "  ${GRAY}Kérlek adj meg egy létező mappát.${RESET}"
      continue
    fi

    # Ellenőrzés: ne saját magát telepítse
    if [[ "$(realpath "${project_path}")" == "$(realpath "${SCRIPT_DIR}")" ]]; then
      error "Nem telepítheted a BerkiSpec-et önmagába!"
      continue
    fi

    echo ""
    success "Célprojekt: ${BOLD}${project_path}${RESET}"
    break
  done

  PROJECT_PATH="${project_path}"
}

# ── 2. lépés: Agent platform választó ───────────────────────────────────────
ask_agent_platform() {
  step "2. lépés: Agent platform kiválasztása"
  echo ""
  echo -e "  ${GRAY}Melyik AI agent platformot használod?${RESET}"
  echo ""
  echo -e "  ${CYAN}1)${RESET} ${GREEN}●${RESET} Google Antigravity CLI"
  echo -e "  ${CYAN}2)${RESET} ${GRAY}○${RESET} Google Gemini CLI"
  echo -e "  ${CYAN}3)${RESET} ${GREEN}●${RESET} Claude Code"
  echo -e "  ${CYAN}4)${RESET} ${GREEN}●${RESET} Cursor"
  echo -e "  ${CYAN}5)${RESET} ${GREEN}●${RESET} GitHub Copilot (CLI & IDE)"
  echo -e "  ${CYAN}6)${RESET} ${GREEN}●${RESET} Codex CLI"
  echo ""

  local choice=""
  while true; do
    echo -ne "  ${MAGENTA}❯${RESET} Választás [1-6]: "
    read -r choice

    case "${choice}" in
      1)
        PLATFORM_CHOICE="antigravity"
        break
        ;;
      3)
        PLATFORM_CHOICE="claude"
        break
        ;;
      4)
        PLATFORM_CHOICE="cursor"
        break
        ;;
      5)
        PLATFORM_CHOICE="copilot"
        break
        ;;
      6)
        PLATFORM_CHOICE="codex"
        break
        ;;
      2)
        echo ""
        separator
        echo ""
        echo -e "  ${ORANGE}🚧  Még nincs implementálva.${RESET}"
        echo ""
        echo -e "  ${GRAY}Jelenleg a ${GREEN}Google Antigravity CLI${GRAY}, a ${GREEN}Claude Code${GRAY}, a ${GREEN}Cursor${GRAY}, a ${GREEN}GitHub Copilot${GRAY} és a ${GREEN}Codex CLI${GRAY} támogatott."
        echo -e "  A többi platform hamarosan érkezik!${RESET}"
        echo ""
        separator
        echo ""
        exit 0
        ;;
      *)
        warn "Kérlek válassz 1-6 közötti számot."
        ;;
    esac
  done

  echo ""
  if [[ "${PLATFORM_CHOICE}" == "antigravity" ]]; then
    success "Platform: ${BOLD}Google Antigravity CLI${RESET}"
  elif [[ "${PLATFORM_CHOICE}" == "claude" ]]; then
    success "Platform: ${BOLD}Claude Code${RESET}"
  elif [[ "${PLATFORM_CHOICE}" == "cursor" ]]; then
    success "Platform: ${BOLD}Cursor${RESET}"
  elif [[ "${PLATFORM_CHOICE}" == "codex" ]]; then
    success "Platform: ${BOLD}Codex CLI${RESET}"
  else
    success "Platform: ${BOLD}GitHub Copilot${RESET}"
  fi

  # ── Codex ↔ Antigravity kölcsönös kizárás — előzetes figyelmeztetés ──
  if [[ "${PLATFORM_CHOICE}" == "codex" || "${PLATFORM_CHOICE}" == "antigravity" ]]; then
    echo ""
    warn "A ${BOLD}Codex CLI${RESET} és a ${BOLD}Google Antigravity CLI${RESET} a közös ${BOLD}.agents/skills/${RESET} mappát használja."
    echo -e "  ${GRAY}Ezért egy projektbe gyakorlatilag csak az egyik telepíthető — ha ezt"
    echo -e "  telepíted, a másikat ugyanebbe a projektbe később már nem tudod.${RESET}"
  fi
}

# ── Ütközés kezelés ─────────────────────────────────────────────────────────
# Visszatérési értékek: 0=felülír, 1=kihagy, 2=abort
handle_conflict() {
  local target="$1"
  local type="$2" # "mappa" vagy "symlink" vagy "fájl"

  warn "Már létezik: ${DIM}${target}${RESET} (${type})"
  echo -ne "    ${YELLOW}?${RESET} Felülírás / Kihagyás / Megszakítás? [${BOLD}f${RESET}/${BOLD}k${RESET}/${BOLD}m${RESET}]: "
  local answer=""
  read -r answer

  case "${answer,,}" in
    f|felülírás|feluliras)
      return 0
      ;;
    k|kihagyás|kihagyas)
      return 1
      ;;
    m|megszakítás|megszakitas)
      return 2
      ;;
    *)
      warn "Nem értem, kihagyom."
      return 1
      ;;
  esac
}

# Igaz, ha a megadott mappák közül legalább egy már létezik és nem üres.
has_existing_content() {
  local dir=""
  for dir in "$@"; do
    if [[ -d "${dir}" ]] && [[ -n "$(ls -A "${dir}" 2>/dev/null)" ]]; then
      return 0
    fi
  done
  return 1
}

# Ütközés esetén rákérdez, és beállítja $CONFLICT_ANSWER-t (0=felülír, 1=kihagy, 2=megszakít).
# A hívó felelőssége az exit / return / folytatás a válasz alapján.
ask_conflict() {
  local target="$1"
  local type="$2"

  CONFLICT_ANSWER=0
  handle_conflict "${target}" "${type}" || CONFLICT_ANSWER=$?
}

# ── Codex ↔ Antigravity kölcsönös kizárás ─────────────────────────────────────
# A Codex és az Antigravity UGYANAZT a .agents/skills/ mappát használja, ezért
# egy projektbe csak az egyik telepíthető értelmesen. Ha a másik platform egyedi
# markere (.codex/agents vagy .agents/agents) már létezik, figyelmeztet és rákérdez.
# Argumentumok: <másik-platform-marker-mappa> <másik-platform-neve>
check_mutual_exclusion() {
  local other_marker="$1"
  local other_name="$2"

  if has_existing_content "${other_marker}"; then
    echo ""
    warn "Úgy tűnik, a(z) ${BOLD}${other_name}${RESET} már telepítve van ebbe a projektbe."
    echo -e "  ${GRAY}A Codex és az Antigravity a közös ${BOLD}.agents/skills/${RESET}${GRAY} mappát használja,"
    echo -e "  ezért a folytatás felülírhatja a(z) ${other_name} skilljeit.${RESET}"
    echo -ne "    ${YELLOW}?${RESET} Biztosan folytatod? [${BOLD}i${RESET}/${BOLD}n${RESET}]: "
    local answer=""
    read -r answer
    case "${answer,,}" in
      i|igen)
        return 0
        ;;
      *)
        error "Telepítés megszakítva."
        exit 1
        ;;
    esac
  fi
}

# ── Google Antigravity Telepítés ──────────────────────────────
install_antigravity() {
  local agents_dest="${PROJECT_PATH}/.agents/agents"
  local skills_dest="${PROJECT_PATH}/.agents/skills"

  # ── Codex ↔ Antigravity kölcsönös kizárás ──
  check_mutual_exclusion "${PROJECT_PATH}/.codex/agents" "Codex CLI"

  # ── .agents mappa létrehozás ──
  if [[ ! -d "${PROJECT_PATH}/.agents" ]]; then
    mkdir -p "${PROJECT_PATH}/.agents"
    success ".agents/ mappa létrehozva"
  fi

  # ── Ütközés ellenőrzés ──
  if has_existing_content "${agents_dest}" "${skills_dest}"; then
    ask_conflict ".agents/agents és .agents/skills" "mappa"
    case "${CONFLICT_ANSWER}" in
      1)
        warn "Antigravity telepítés kihagyva, a meglévő fájlok érintetlenek."
        INSTALL_STATUS="skipped"
        return 0
        ;;
      2)
        error "Telepítés megszakítva."
        exit 1
        ;;
    esac
  fi

  # ── Agents & Skills ──
  echo ""
  echo -e "  ${BLUE}📦 Antigravity Agent-ek és Skill-ek telepítése${RESET}"
  separator

  info "Fájlok másolása és modellek konfigurálása..."
  if python3 "${SCRIPT_DIR}/prompts/scripts/install-helper.py" "antigravity" "${SCRIPT_DIR}" "${PROJECT_PATH}"; then
    success "Antigravity ágensek és skillek sikeresen konfigurálva és másolva!"
    INSTALL_STATUS="done"
  else
    error "Hiba történt a fájlok másolása során!"
    exit 1
  fi
}

# ── Claude Code Telepítés ─────────────────────────────────────
install_claude() {
  local agents_dest="${PROJECT_PATH}/.claude/agents"
  local skills_dest="${PROJECT_PATH}/.claude/skills"

  # ── .claude mappa létrehozás ──
  if [[ ! -d "${PROJECT_PATH}/.claude" ]]; then
    mkdir -p "${PROJECT_PATH}/.claude"
    success ".claude/ mappa létrehozva"
  fi

  # ── Ütközés ellenőrzés ──
  if has_existing_content "${agents_dest}" "${skills_dest}"; then
    ask_conflict ".claude/agents és .claude/skills" "mappa"
    case "${CONFLICT_ANSWER}" in
      1)
        warn "Claude telepítés kihagyva, a meglévő fájlok érintetlenek."
        INSTALL_STATUS="skipped"
        return 0
        ;;
      2)
        error "Telepítés megszakítva."
        exit 1
        ;;
    esac
  fi

  # ── Agents & Skills ──
  echo ""
  echo -e "  ${BLUE}📦 Claude Agent-ek és Skill-ek telepítése (.claude/)${RESET}"
  separator

  info "Fájlok másolása és modellek konfigurálása..."
  if python3 "${SCRIPT_DIR}/prompts/scripts/install-helper.py" "claude" "${SCRIPT_DIR}" "${PROJECT_PATH}"; then
    success "Claude ágensek és skillek sikeresen konfigurálva és másolva!"
    INSTALL_STATUS="done"
  else
    error "Hiba történt a fájlok másolása során!"
    exit 1
  fi
}

# ── GitHub Copilot Telepítés ──────────────────────────────────
install_copilot() {
  local agents_dest="${PROJECT_PATH}/.github/agents"
  local instructions_dest="${PROJECT_PATH}/.github/instructions"

  # ── .github mappa létrehozás ──
  if [[ ! -d "${PROJECT_PATH}/.github" ]]; then
    mkdir -p "${PROJECT_PATH}/.github"
    success ".github/ mappa létrehozva"
  fi

  # ── Ütközés ellenőrzés ──
  if has_existing_content "${agents_dest}" "${instructions_dest}"; then
    ask_conflict ".github/agents és .github/instructions" "mappa"
    case "${CONFLICT_ANSWER}" in
      1)
        warn "Copilot telepítés kihagyva, a meglévő fájlok érintetlenek."
        INSTALL_STATUS="skipped"
        return 0
        ;;
      2)
        error "Telepítés megszakítva."
        exit 1
        ;;
    esac
  fi

  # ── Agents & Skills ──
  echo ""
  echo -e "  ${BLUE}📦 Copilot Agent-ek és Utasítások telepítése (.github/)${RESET}"
  separator

  info "Fájlok másolása és modellek konfigurálása..."
  if python3 "${SCRIPT_DIR}/prompts/scripts/install-helper.py" "copilot" "${SCRIPT_DIR}" "${PROJECT_PATH}"; then
    success "Copilot ágensek és skillek sikeresen konfigurálva és másolva!"
    INSTALL_STATUS="done"
  else
    error "Hiba történt a fájlok másolása során!"
    exit 1
  fi
}

# ── Cursor Telepítés ──────────────────────────────────────────
install_cursor() {
  local agents_dest="${PROJECT_PATH}/.cursor/agents"
  local skills_dest="${PROJECT_PATH}/.cursor/skills"

  # ── .cursor mappa létrehozás ──
  if [[ ! -d "${PROJECT_PATH}/.cursor" ]]; then
    mkdir -p "${PROJECT_PATH}/.cursor"
    success ".cursor/ mappa létrehozva"
  fi

  # ── Ütközés ellenőrzés ──
  if has_existing_content "${agents_dest}" "${skills_dest}"; then
    ask_conflict ".cursor/agents és .cursor/skills" "mappa"
    case "${CONFLICT_ANSWER}" in
      1)
        warn "Cursor telepítés kihagyva, a meglévő fájlok érintetlenek."
        INSTALL_STATUS="skipped"
        return 0
        ;;
      2)
        error "Telepítés megszakítva."
        exit 1
        ;;
    esac
  fi

  # ── Agents & Skills ──
  echo ""
  echo -e "  ${BLUE}📦 Cursor Subagent-ek és Skill-ek telepítése (.cursor/)${RESET}"
  separator

  info "Fájlok másolása és modellek konfigurálása..."
  if python3 "${SCRIPT_DIR}/prompts/scripts/install-helper.py" "cursor" "${SCRIPT_DIR}" "${PROJECT_PATH}"; then
    success "Cursor rule-ok és command-ok sikeresen konfigurálva és másolva!"
    INSTALL_STATUS="done"
  else
    error "Hiba történt a fájlok másolása során!"
    exit 1
  fi
}

# ── Codex CLI Telepítés ───────────────────────────────────────
install_codex() {
  local agents_dest="${PROJECT_PATH}/.codex/agents"
  local skills_dest="${PROJECT_PATH}/.agents/skills"

  # ── Codex ↔ Antigravity kölcsönös kizárás ──
  check_mutual_exclusion "${PROJECT_PATH}/.agents/agents" "Google Antigravity CLI"

  # ── .codex létezik, de nem mappa (stray fájl/hivatkozás) ──
  if [[ -e "${PROJECT_PATH}/.codex" && ! -d "${PROJECT_PATH}/.codex" ]]; then
    warn "A ${DIM}${PROJECT_PATH}/.codex${RESET} létezik, de nem mappa (fájl vagy hivatkozás)."
    echo -e "  ${GRAY}A Codex telepítéshez ennek mappának kell lennie.${RESET}"
    echo -ne "    ${YELLOW}?${RESET} Eltávolítsam és mappaként hozzam létre? [${BOLD}i${RESET}/${BOLD}n${RESET}]: "
    local codex_rm=""
    read -r codex_rm
    case "${codex_rm,,}" in
      i|igen)
        rm -f "${PROJECT_PATH}/.codex"
        ;;
      *)
        error "Telepítés megszakítva. Töröld vagy nevezd át a .codex fájlt, majd futtasd újra."
        exit 1
        ;;
    esac
  fi

  # ── .codex mappa létrehozás ──
  if [[ ! -d "${PROJECT_PATH}/.codex" ]]; then
    mkdir -p "${PROJECT_PATH}/.codex"
    success ".codex/ mappa létrehozva"
  fi

  # ── Ütközés ellenőrzés ──
  if has_existing_content "${agents_dest}" "${skills_dest}"; then
    ask_conflict ".codex/agents és .agents/skills" "mappa"
    case "${CONFLICT_ANSWER}" in
      1)
        warn "Codex telepítés kihagyva, a meglévő fájlok érintetlenek."
        INSTALL_STATUS="skipped"
        return 0
        ;;
      2)
        error "Telepítés megszakítva."
        exit 1
        ;;
    esac
  fi

  # ── Agents & Skills ──
  echo ""
  echo -e "  ${BLUE}📦 Codex Subagent-ek (.codex/agents/) és Skill-ek (.agents/skills/) telepítése${RESET}"
  separator

  info "Fájlok másolása és modellek konfigurálása..."
  if python3 "${SCRIPT_DIR}/prompts/scripts/install-helper.py" "codex" "${SCRIPT_DIR}" "${PROJECT_PATH}"; then
    success "Codex subagentek (TOML) és skillek sikeresen konfigurálva és másolva!"
    INSTALL_STATUS="done"
  else
    error "Hiba történt a fájlok másolása során!"
    exit 1
  fi
}

# ── 3. lépés: Másolás és Konfigurálás (Orchestrator) ─────────────────────────
create_symlinks() {
  step "3. lépés: Telepítés"
  echo ""

  if [[ "${PLATFORM_CHOICE}" == "antigravity" ]]; then
    install_antigravity
  elif [[ "${PLATFORM_CHOICE}" == "claude" ]]; then
    install_claude
  elif [[ "${PLATFORM_CHOICE}" == "cursor" ]]; then
    install_cursor
  elif [[ "${PLATFORM_CHOICE}" == "codex" ]]; then
    install_codex
  else
    install_copilot
  fi
}

# ── Összefoglaló ────────────────────────────────────────────────────────────
show_summary() {
  echo ""
  separator
  echo ""

  if [[ "${INSTALL_STATUS}" == "skipped" ]]; then
    echo -e "  ${YELLOW}${BOLD}⚠ Telepítés kihagyva${RESET}"
    echo ""
    echo -e "  ${GRAY}A meglévő fájlokat nem módosítottam. Futtasd újra a scriptet"
    echo -e "  és válaszd a ${BOLD}felülírás${GRAY} opciót, ha frissíteni szeretnéd őket.${RESET}"
    echo ""
    return 0
  fi

  echo -e "  ${GREEN}${BOLD}🎉 Telepítés kész!${RESET}"
  echo ""
  echo -e "  ${WHITE}Projekt:${RESET}  ${BOLD}${PROJECT_PATH}${RESET}"

  if [[ "${PLATFORM_CHOICE}" == "antigravity" ]]; then
    echo -e "  ${WHITE}Platform:${RESET} ${BOLD}Google Antigravity CLI${RESET}"
    echo ""
    echo -e "  ${GRAY}A telepített struktúra:${RESET}"
    echo -e "  ${DIM}${PROJECT_PATH}/.agents/"
    echo -e "  ├── agents/        ${CYAN}(agent JSON fájlok modell-konfigurációval)${RESET}${DIM}"
    echo -e "  └── skills/        ${CYAN}(fázis-skillek, SKILL.md)${RESET}"
    echo ""
    separator
    echo ""
    echo -e "  ${GRAY}Kezdéshez indítsd el az Antigravity CLI-t a projektedben,"
    echo -e "  és kérd a ${CYAN}bs-init-project${GRAY} skill futtatását.${RESET}"
  elif [[ "${PLATFORM_CHOICE}" == "claude" ]]; then
    echo -e "  ${WHITE}Platform:${RESET} ${BOLD}Claude Code${RESET}"
    echo ""
    echo -e "  ${GRAY}A telepített struktúra:${RESET}"
    echo -e "  ${DIM}${PROJECT_PATH}/.claude/"
    echo -e "  ├── agents/        ${CYAN}(agent MD fájlok modell-konfigurációval)${RESET}${DIM}"
    echo -e "  └── skills/        ${CYAN}(fázis-skillek, SKILL.md)${RESET}"
    echo ""
    separator
    echo ""
    echo -e "  ${GRAY}Kezdéshez indítsd el a Claude Code-ot a projektedben,"
    echo -e "  és futtasd a ${CYAN}bs-init-project${GRAY} skillt.${RESET}"
  elif [[ "${PLATFORM_CHOICE}" == "cursor" ]]; then
    echo -e "  ${WHITE}Platform:${RESET} ${BOLD}Cursor${RESET}"
    echo ""
    echo -e "  ${GRAY}A telepített struktúra:${RESET}"
    echo -e "  ${DIM}${PROJECT_PATH}/.cursor/"
    echo -e "  ├── agents/        ${CYAN}(subagent MD fájlok model + effort + readonly konfigurációval)${RESET}${DIM}"
    echo -e "  └── skills/        ${CYAN}(fázis-skillek, SKILL.md)${RESET}"
    echo ""
    echo -e "  ${DIM}${GRAY}Megjegyzés: a subagent \`model\` mezője natívan hat; az \`effort\`"
    echo -e "  látható ajánlás (a Cursor a nem ismert frontmatter-kulcsot kihagyja).${RESET}"
    echo ""
    separator
    echo ""
    echo -e "  ${GRAY}Kezdéshez indítsd el a Cursor Agent CLI-t (${CYAN}agent${GRAY}) a projektedben,"
    echo -e "  és kérd a ${CYAN}bs-init-project${GRAY} skill futtatását.${RESET}"
  elif [[ "${PLATFORM_CHOICE}" == "codex" ]]; then
    echo -e "  ${WHITE}Platform:${RESET} ${BOLD}Codex CLI${RESET}"
    echo ""
    echo -e "  ${GRAY}A telepített struktúra:${RESET}"
    echo -e "  ${DIM}${PROJECT_PATH}/.codex/"
    echo -e "  ├── agents/        ${CYAN}(subagent TOML fájlok model + reasoning-effort + sandbox konfigurációval)${RESET}${DIM}"
    echo -e "  └── scripts/       ${CYAN}(helper scriptek)${RESET}${DIM}"
    echo -e "  ${PROJECT_PATH}/.agents/"
    echo -e "  └── skills/        ${CYAN}(skill SKILL.md fájlok — a Codex innen olvassa a projekt-skilleket)${RESET}"
    echo ""
    echo -e "  ${DIM}${GRAY}Megjegyzés: a subagent \`model\` és \`model_reasoning_effort\` mezője"
    echo -e "  natívan hat. A skillek az Antigravity-vel KÖZÖS .agents/skills/ mappát"
    echo -e "  használják — ugyanabba a projektbe a kettő közül csak az egyik telepíthető.${RESET}"
    echo ""
    separator
    echo ""
    echo -e "  ${GRAY}Kezdéshez indítsd el a Codex CLI-t a projektedben,"
    echo -e "  és kérd a ${CYAN}bs-init-project${GRAY} skill futtatását.${RESET}"
  else
    echo -e "  ${WHITE}Platform:${RESET} ${BOLD}GitHub Copilot (CLI & IDE)${RESET}"
    echo ""
    echo -e "  ${GRAY}A telepített struktúra:${RESET}"
    echo -e "  ${DIM}${PROJECT_PATH}/.github/"
    echo -e "  ├── agents/        ${CYAN}(*.agent.md fájlok modell-konfigurációval)${RESET}${DIM}"
    echo -e "  └── instructions/  ${CYAN}(fázis-skillek, *.instructions.md)${RESET}"
    echo ""
    separator
    echo ""
    echo -e "  ${GRAY}Kezdéshez a Copilot Chat ablakban vagy a Copilot CLI-ben"
    echo -e "  használd a ${CYAN}@bs-init-project${GRAY} utasítást a kezdéshez!${RESET}"
  fi
  echo ""
}

# ── Főprogram ───────────────────────────────────────────────────────────────
main() {
  show_logo
  show_welcome
  ask_project_path
  ask_agent_platform
  create_symlinks
  # A célmappa megjegyzése a következő futtatáshoz (lásd `history` fájl).
  [[ -n "${PROJECT_PATH}" ]] && save_history "${PROJECT_PATH}" "${PLATFORM_CHOICE}"
  show_summary
}

main "$@"
