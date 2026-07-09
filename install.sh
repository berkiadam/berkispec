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

readonly AGENTS_SRC_DIR="${SCRIPT_DIR}/prompts/agents"
readonly AGENTS_GEMINI_SRC="${SCRIPT_DIR}/prompts/agents/gemini-agent"
readonly SKILLS_SRC="${SCRIPT_DIR}/prompts/skills"

# Globális állapot változók
PROJECT_PATH=""
PLATFORM_CHOICE="" # "antigravity" vagy "claude" vagy "copilot"

# ── Segédfüggvények ─────────────────────────────────────────────────────────
info()    { echo -e "  ${CYAN}ℹ${RESET}  $*"; }
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
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                            ║
    ║   ██████╗ ███████╗██████╗ ██╗  ██╗██╗███████╗██████╗ ███████╗ ██████╗║
    ║   ██╔══██╗██╔════╝██╔══██╗██║ ██╔╝██║██╔════╝██╔══██╗██╔════╝██╔════╝║
    ║   ██████╔╝█████╗  ██████╔╝█████╔╝ ██║███████╗██████╔╝█████╗  ██║     ║
    ║   ██╔══██╗██╔══╝  ██╔══██╗██╔═██╗ ██║╚════██║██╔═══╝ ██╔══╝  ██║     ║
    ║   ██████╔╝███████╗██║  ██║██║  ██╗██║███████║██║     ███████╗╚██████╗║
    ║   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚══════╝╚═╝     ╚══════╝ ╚═════╝║
    ║                                                            ║
    ╚══════════════════════════════════════════════════════════════╝
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
  while true; do
    echo -ne "  ${MAGENTA}❯${RESET} Projekt mappa: "
    read -e -r project_path

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
  echo -e "  ${CYAN}4)${RESET} ${GRAY}○${RESET} Cursor"
  echo -e "  ${CYAN}5)${RESET} ${GREEN}●${RESET} GitHub Copilot (CLI & IDE)"
  echo ""

  local choice=""
  while true; do
    echo -ne "  ${MAGENTA}❯${RESET} Választás [1-5]: "
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
      5)
        PLATFORM_CHOICE="copilot"
        break
        ;;
      2|4)
        echo ""
        separator
        echo ""
        echo -e "  ${ORANGE}🚧  Még nincs implementálva.${RESET}"
        echo ""
        echo -e "  ${GRAY}Jelenleg a ${GREEN}Google Antigravity CLI${GRAY}, a ${GREEN}Claude Code${GRAY} és a ${GREEN}GitHub Copilot${GRAY} támogatott."
        echo -e "  A többi platform hamarosan érkezik!${RESET}"
        echo ""
        separator
        echo ""
        exit 0
        ;;
      *)
        warn "Kérlek válassz 1-5 közötti számot."
        ;;
    esac
  done

  echo ""
  if [[ "${PLATFORM_CHOICE}" == "antigravity" ]]; then
    success "Platform: ${BOLD}Google Antigravity CLI${RESET}"
  elif [[ "${PLATFORM_CHOICE}" == "claude" ]]; then
    success "Platform: ${BOLD}Claude Code${RESET}"
  else
    success "Platform: ${BOLD}GitHub Copilot${RESET}"
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

# ── Google Antigravity Telepítés ──────────────────────────────
install_antigravity() {
  local agents_dest="${PROJECT_PATH}/.agents/agents"
  local skills_dest="${PROJECT_PATH}/.agents/skills"

  # ── .agents mappa létrehozás ──
  if [[ ! -d "${PROJECT_PATH}/.agents" ]]; then
    mkdir -p "${PROJECT_PATH}/.agents"
    success ".agents/ mappa létrehozva"
  fi

  # ── Agents & Skills ──
  echo ""
  echo -e "  ${BLUE}📦 Antigravity Agent-ek és Skill-ek telepítése${RESET}"
  separator

  info "Fájlok másolása és modellek konfigurálása..."
  if python3 "${SCRIPT_DIR}/prompts/scripts/install-helper.py" "antigravity" "${SCRIPT_DIR}" "${PROJECT_PATH}"; then
    success "Antigravity ágensek és skillek sikeresen konfigurálva és másolva!"
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

  # ── Agents & Skills ──
  echo ""
  echo -e "  ${BLUE}📦 Claude Agent-ek és Skill-ek telepítése (.claude/)${RESET}"
  separator

  info "Fájlok másolása és modellek konfigurálása..."
  if python3 "${SCRIPT_DIR}/prompts/scripts/install-helper.py" "claude" "${SCRIPT_DIR}" "${PROJECT_PATH}"; then
    success "Claude ágensek és skillek sikeresen konfigurálva és másolva!"
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

  # ── Agents & Skills ──
  echo ""
  echo -e "  ${BLUE}📦 Copilot Agent-ek és Utasítások telepítése (.github/)${RESET}"
  separator

  info "Fájlok másolása és modellek konfigurálása..."
  if python3 "${SCRIPT_DIR}/prompts/scripts/install-helper.py" "copilot" "${SCRIPT_DIR}" "${PROJECT_PATH}"; then
    success "Copilot ágensek és skillek sikeresen konfigurálva és másolva!"
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
  else
    install_copilot
  fi
}

# ── Összefoglaló ────────────────────────────────────────────────────────────
show_summary() {
  echo ""
  separator
  echo ""
  echo -e "  ${GREEN}${BOLD}🎉 Telepítés kész!${RESET}"
  echo ""
  echo -e "  ${WHITE}Projekt:${RESET}  ${BOLD}${PROJECT_PATH}${RESET}"
  
  if [[ "${PLATFORM_CHOICE}" == "antigravity" ]]; then
    echo -e "  ${WHITE}Platform:${RESET} ${BOLD}Google Antigravity CLI${RESET}"
    echo ""
    echo -e "  ${GRAY}A telepített struktúra:${RESET}"
    echo -e "  ${DIM}${PROJECT_PATH}/.agents/"
    echo -e "  ├── agents/        ${CYAN}(agent JSON fájlok modell-konfigurációval)${RESET}${DIM}"
    echo -e "  └── skills/        ${CYAN}(skill SKILL.md fájlok modell-konfigurációval)${RESET}"
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
    echo -e "  └── skills/        ${CYAN}(skill SKILL.md fájlok modell-konfigurációval)${RESET}"
    echo ""
    separator
    echo ""
    echo -e "  ${GRAY}Kezdéshez indítsd el a Claude Code-ot a projektedben,"
    echo -e "  és futtasd a ${CYAN}bs-init-project${GRAY} skillt.${RESET}"
  else
    echo -e "  ${WHITE}Platform:${RESET} ${BOLD}GitHub Copilot (CLI & IDE)${RESET}"
    echo ""
    echo -e "  ${GRAY}A telepített struktúra:${RESET}"
    echo -e "  ${DIM}${PROJECT_PATH}/.github/"
    echo -e "  ├── agents/        ${CYAN}(*.agent.md fájlok modell-konfigurációval)${RESET}${DIM}"
    echo -e "  └── instructions/  ${CYAN}(*.instructions.md fájlok modell-konfigurációval)${RESET}"
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
  show_summary
}

main "$@"
