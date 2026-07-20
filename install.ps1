# ─────────────────────────────────────────────────────────────────────────────
# BerkiSpec Installer (Windows PowerShell)
# Telepíti a BerkiSpec agent-eket és skill-eket a célprojektbe.
# Supports: Google Antigravity CLI, Claude Code, GitHub Copilot (CLI & IDE)
# ─────────────────────────────────────────────────────────────────────────────

# ── Színek és stílusok ──────────────────────────────────────────────────────
$ESC = [char]27
$RESET = "$ESC[0m"
$BOLD = "$ESC[1m"
$DIM = "$ESC[2m"
$ITALIC = "$ESC[3m"
$UNDERLINE = "$ESC[4m"

$RED = "$ESC[38;5;196m"
$GREEN = "$ESC[38;5;82m"
$YELLOW = "$ESC[38;5;220m"
$BLUE = "$ESC[38;5;75m"
$CYAN = "$ESC[38;5;45m"
$MAGENTA = "$ESC[38;5;213m"
$ORANGE = "$ESC[38;5;208m"
$WHITE = "$ESC[38;5;255m"
$GRAY = "$ESC[38;5;245m"

$BG_GREEN = "$ESC[48;5;22m"
$BG_RED = "$ESC[48;5;52m"
$BG_BLUE = "$ESC[48;5;24m"

# ── BerkiSpec repo detekció ─────────────────────────────────────────────────
$SCRIPT_DIR = $PSScriptRoot
if ([string]::IsNullOrEmpty($SCRIPT_DIR)) {
    $SCRIPT_DIR = Get-Location
}

$AGENTS_SRC_DIR = Join-Path $SCRIPT_DIR "prompts/agents"
$AGENTS_GEMINI_SRC = Join-Path $SCRIPT_DIR "prompts/agents/gemini-agent"
$SKILLS_SRC = Join-Path $SCRIPT_DIR "prompts/skills"

# Globális állapot változók
$PROJECT_PATH = ""
$PLATFORM_CHOICE = "" # "antigravity" vagy "claude" vagy "copilot" vagy "cursor"
$INSTALL_STATUS = ""  # "done" vagy "skipped"
$CONFLICT_ANSWER = 0
$PYTHON_CMD = ""

# ── Segédfüggvények ─────────────────────────────────────────────────────────
function Write-Info { param([string]$msg) Write-Host "  ${CYAN}ℹ${RESET}  $msg" }
function Write-Success { param([string]$msg) Write-Host "  ${GREEN}✔${RESET}  $msg" }
function Write-Warn { param([string]$msg) Write-Host "  ${YELLOW}⚠${RESET}  $msg" }
function Write-Error { param([string]$msg) Write-Host "  ${RED}✖${RESET}  $msg" }
function Write-Step { param([string]$msg) Write-Host "`n  ${BLUE}▸${RESET} ${BOLD}$msg${RESET}" }

function Write-Separator {
    Write-Host "  ${DIM}$("-" * 68)${RESET}"
}

# ── Logo ────────────────────────────────────────────────────────────────────
function Show-Logo {
    Write-Host ""
    Write-Host "${BOLD}${CYAN}"
    Write-Host "    ╔═══════════════════════════════════════════════════════════════════════╗"
    Write-Host "    ║                                                                       ║"
    Write-Host "    ║   ██████╗ ███████╗██████╗ ██╗  ██╗██╗███████╗██████╗ ███████╗ ██████╗ ║"
    Write-Host "    ║   ██╔══██╗██╔════╝██╔══██╗██║ ██╔╝██║██╔════╝██╔══██╗██╔════╝██╔════╝ ║"
    Write-Host "    ║   ██████╔╝█████╗  ██████╔╝█████╔╝ ██║███████╗██████╔╝█████╗  ██║      ║"
    Write-Host "    ║   ██╔══██╗██╔══╝  ██╔══██╗██╔═██╗ ██║╚════██║██╔═══╝ ██╔══╝  ██║      ║"
    Write-Host "    ║   ██████╔╝███████╗██║  ██║██║  ██╗██║███████║██║     ███████╗╚██████╗ ║"
    Write-Host "    ║   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚══════╝╚═╝     ╚══════╝ ╚═════╝ ║"
    Write-Host "    ║                                                                       ║"
    Write-Host "    ╚═══════════════════════════════════════════════════════════════════════╝"
    Write-Host "${RESET}"
    Write-Host "  ${DIM}${WHITE}Spec-Driven Development Framework${RESET}"
    Write-Host "  ${DIM}${GRAY}v1.2 · Telepítő${RESET}"
    Write-Host ""
    Write-Separator
}

# ── Üdvözlés ────────────────────────────────────────────────────────────────
function Show-Welcome {
    Write-Host ""
    Write-Host "  ${WHITE}${BOLD}Üdvözöllek a BerkiSpec telepítőben!${RESET}"
    Write-Host ""
    Write-Host "  ${GRAY}Ez a script beállítja a BerkiSpec agent-eket és skill-eket"
    Write-Host "  a célprojektedben symlink-ek segítségével.${RESET}"
    Write-Host ""
    Write-Host "  ${DIM}BerkiSpec forrás: ${CYAN}${SCRIPT_DIR}${RESET}"
    Write-Host ""
    Write-Separator
}

# ── 1. lépés: Projekt mappa bekérése ────────────────────────────────────────
function Ask-ProjectPath {
    Write-Step "1. lépés: Projekt mappa"
    Write-Host ""
    Write-Host "  ${GRAY}Add meg a célprojekt gyökérmappáját."
    Write-Host "  ${DIM}💡 Tipp: Az útvonal megadása során használhatod a ${BOLD}Tab${RESET}${DIM} billentyűt"
    Write-Host "     az automatikus kiegészítéshez.${RESET}"
    Write-Host ""

    while ($true) {
        Write-Host -NoNewline "  ${MAGENTA}❯${RESET} Projekt mappa: "
        $project_path = Read-Host

        # Tilde kifejtés
        if ($project_path -like "~*") {
            $home_dir = $env:USERPROFILE
            if ($project_path -eq "~") {
                $project_path = $home_dir
            } else {
                $project_path = Join-Path $home_dir ($project_path.Substring(2))
            }
        }

        # Trailing slash eltávolítás
        if ($project_path.EndsWith("\") -or $project_path.EndsWith("/")) {
            $project_path = $project_path.Substring(0, $project_path.Length - 1)
        }

        if ([string]::IsNullOrWhiteSpace($project_path)) {
            Write-Warn "Kérlek adj meg egy útvonalat."
            continue
        }

        if (-not (Test-Path $project_path -PathType Container)) {
            Write-Error "A mappa nem létezik: ${project_path}"
            Write-Host "  ${GRAY}Kérlek adj meg egy létező mappát.${RESET}"
            continue
        }

        # Ellenőrzés: ne saját magát telepítse
        $real_project_path = [System.IO.Path]::GetFullPath($project_path)
        $real_script_dir = [System.IO.Path]::GetFullPath($SCRIPT_DIR)
        if ($real_project_path -eq $real_script_dir) {
            Write-Error "Nem telepítheted a BerkiSpec-et önmagába!"
            continue
        }

        Write-Host ""
        Write-Success "Célprojekt: ${BOLD}${project_path}${RESET}"
        break
    }

    $script:PROJECT_PATH = $project_path
}

# ── 2. lépés: Agent platform választó ───────────────────────────────────────
function Ask-AgentPlatform {
    Write-Step "2. lépés: Agent platform kiválasztása"
    Write-Host ""
    Write-Host "  ${GRAY}Melyik AI agent platformot használod?${RESET}"
    Write-Host ""
    Write-Host "  ${CYAN}1)${RESET} ${GREEN}●${RESET} Google Antigravity CLI"
    Write-Host "  ${CYAN}2)${RESET} ${GRAY}○${RESET} Google Gemini CLI"
    Write-Host "  ${CYAN}3)${RESET} ${GREEN}●${RESET} Claude Code"
    Write-Host "  ${CYAN}4)${RESET} ${GREEN}●${RESET} Cursor"
    Write-Host "  ${CYAN}5)${RESET} ${GREEN}●${RESET} GitHub Copilot (CLI & IDE)"
    Write-Host ""

    $choice = ""
    while ($true) {
        Write-Host -NoNewline "  ${MAGENTA}❯${RESET} Választás [1-5]: "
        $choice = Read-Host

        switch ($choice) {
            "1" {
                $script:PLATFORM_CHOICE = "antigravity"
                break
            }
            "3" {
                $script:PLATFORM_CHOICE = "claude"
                break
            }
            "4" {
                $script:PLATFORM_CHOICE = "cursor"
                break
            }
            "5" {
                $script:PLATFORM_CHOICE = "copilot"
                break
            }
            "2" {
                Write-Host ""
                Write-Separator
                Write-Host ""
                Write-Host "  ${ORANGE}🚧  Még nincs implementálva.${RESET}"
                Write-Host ""
                Write-Host "  ${GRAY}Jelenleg a ${GREEN}Google Antigravity CLI${GRAY}, a ${GREEN}Claude Code${GRAY}, a ${GREEN}Cursor${GRAY} és a ${GREEN}GitHub Copilot${GRAY} támogatott."
                Write-Host "  A többi platform hamarosan érkezik!${RESET}"
                Write-Host ""
                Write-Separator
                Write-Host ""
                exit 0
            }
            default {
                Write-Warn "Kérlek válassz 1-5 közötti számot."
            }
        }
        if ($script:PLATFORM_CHOICE) { break }
    }

    Write-Host ""
    if ($script:PLATFORM_CHOICE -eq "antigravity") {
        Write-Success "Platform: ${BOLD}Google Antigravity CLI${RESET}"
    } elseif ($script:PLATFORM_CHOICE -eq "claude") {
        Write-Success "Platform: ${BOLD}Claude Code${RESET}"
    } elseif ($script:PLATFORM_CHOICE -eq "cursor") {
        Write-Success "Platform: ${BOLD}Cursor${RESET}"
    } else {
        Write-Success "Platform: ${BOLD}GitHub Copilot${RESET}"
    }
}

# ── Ütközés kezelés ─────────────────────────────────────────────────────────
# Visszatérési értékek: 0=felülír, 1=kihagy, 2=abort
function Handle-Conflict {
    param(
        [string]$target,
        [string]$type
    )

    Write-Warn "Már létezik: ${DIM}${target}${RESET} (${type})"
    Write-Host -NoNewline "    ${YELLOW}?${RESET} Felülírás / Kihagyás / Megszakítás? [${BOLD}f${RESET}/${BOLD}k${RESET}/${BOLD}m${RESET}]: "
    $answer = Read-Host

    switch ($answer.ToLower()) {
        "f" { return 0 }
        "felülírás" { return 0 }
        "feluliras" { return 0 }
        "k" { return 1 }
        "kihagyás" { return 1 }
        "kihagyas" { return 1 }
        "m" { return 2 }
        "megszakítás" { return 2 }
        "megszakitas" { return 2 }
        default {
            Write-Warn "Nem értem, kihagyom."
            return 1
        }
    }
}

# Igaz, ha a megadott mappák közül legalább egy már létezik és nem üres.
function Has-ExistingContent {
    param(
        [string[]]$dirs
    )
    foreach ($dir in $dirs) {
        if (Test-Path $dir -PathType Container) {
            $items = Get-ChildItem -Path $dir -ErrorAction SilentlyContinue
            if ($items) {
                return $true
            }
        }
    }
    return $false
}

# Ütközés esetén rákérdez, és beállítja $CONFLICT_ANSWER-t (0=felülír, 1=kihagy, 2=megszakít).
function Ask-Conflict {
    param(
        [string]$target,
        [string]$type
    )

    $script:CONFLICT_ANSWER = Handle-Conflict $target $type
}

# ── Google Antigravity Telepítés ──────────────────────────────
function Install-Antigravity {
    $agents_dest = Join-Path $script:PROJECT_PATH ".agents/agents"
    $skills_dest = Join-Path $script:PROJECT_PATH ".agents/skills"

    # .agents mappa létrehozás
    $agents_folder = Join-Path $script:PROJECT_PATH ".agents"
    if (-not (Test-Path $agents_folder -PathType Container)) {
        New-Item -ItemType Directory -Path $agents_folder -Force | Out-Null
        Write-Success ".agents/ mappa létrehozva"
    }

    # Ütközés ellenőrzés
    if (Has-ExistingContent @($agents_dest, $skills_dest)) {
        Ask-Conflict ".agents/agents és .agents/skills" "mappa"
        switch ($script:CONFLICT_ANSWER) {
            1 {
                Write-Warn "Antigravity telepítés kihagyva, a meglévő fájlok érintetlenek."
                $script:INSTALL_STATUS = "skipped"
                return
            }
            2 {
                Write-Error "Telepítés megszakítva."
                exit 1
            }
        }
    }

    # Agents & Skills
    Write-Host ""
    Write-Host "  ${BLUE}📦 Antigravity Agent-ek és Skill-ek telepítése${RESET}"
    Write-Separator

    Write-Info "Fájlok másolása és modellek konfigurálása..."
    $helper_script = Join-Path $SCRIPT_DIR "prompts/scripts/install-helper.py"
    & $script:PYTHON_CMD $helper_script "antigravity" $SCRIPT_DIR $script:PROJECT_PATH
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Antigravity ágensek és skillek sikeresen konfigurálva és másolva!"
        $script:INSTALL_STATUS = "done"
    } else {
        Write-Error "Hiba történt a fájlok másolása során!"
        exit 1
    }
}

# ── Claude Code Telepítés ─────────────────────────────────────
function Install-Claude {
    $agents_dest = Join-Path $script:PROJECT_PATH ".claude/agents"
    $skills_dest = Join-Path $script:PROJECT_PATH ".claude/skills"

    # .claude mappa létrehozás
    $claude_folder = Join-Path $script:PROJECT_PATH ".claude"
    if (-not (Test-Path $claude_folder -PathType Container)) {
        New-Item -ItemType Directory -Path $claude_folder -Force | Out-Null
        Write-Success ".claude/ mappa létrehozva"
    }

    # Ütközés ellenőrzés
    if (Has-ExistingContent @($agents_dest, $skills_dest)) {
        Ask-Conflict ".claude/agents és .claude/skills" "mappa"
        switch ($script:CONFLICT_ANSWER) {
            1 {
                Write-Warn "Claude telepítés kihagyva, a meglévő fájlok érintetlenek."
                $script:INSTALL_STATUS = "skipped"
                return
            }
            2 {
                Write-Error "Telepítés megszakítva."
                exit 1
            }
        }
    }

    # Agents & Skills
    Write-Host ""
    Write-Host "  ${BLUE}📦 Claude Agent-ek és Skill-ek telepítése (.claude/)${RESET}"
    Write-Separator

    Write-Info "Fájlok másolása és modellek konfigurálása..."
    $helper_script = Join-Path $SCRIPT_DIR "prompts/scripts/install-helper.py"
    & $script:PYTHON_CMD $helper_script "claude" $SCRIPT_DIR $script:PROJECT_PATH
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Claude ágensek és skillek sikeresen konfigurálva és másolva!"
        $script:INSTALL_STATUS = "done"
    } else {
        Write-Error "Hiba történt a fájlok másolása során!"
        exit 1
    }
}

# ── GitHub Copilot Telepítés ──────────────────────────────────
function Install-Copilot {
    $agents_dest = Join-Path $script:PROJECT_PATH ".github/agents"
    $instructions_dest = Join-Path $script:PROJECT_PATH ".github/instructions"

    # .github mappa létrehozás
    $github_folder = Join-Path $script:PROJECT_PATH ".github"
    if (-not (Test-Path $github_folder -PathType Container)) {
        New-Item -ItemType Directory -Path $github_folder -Force | Out-Null
        Write-Success ".github/ mappa létrehozva"
    }

    # Ütközés ellenőrzés
    if (Has-ExistingContent @($agents_dest, $instructions_dest)) {
        Ask-Conflict ".github/agents és .github/instructions" "mappa"
        switch ($script:CONFLICT_ANSWER) {
            1 {
                Write-Warn "Copilot telepítés kihagyva, a meglévő fájlok érintetlenek."
                $script:INSTALL_STATUS = "skipped"
                return
            }
            2 {
                Write-Error "Telepítés megszakítva."
                exit 1
            }
        }
    }

    # Agents & Skills
    Write-Host ""
    Write-Host "  ${BLUE}📦 Copilot Agent-ek és Utasítások telepítése (.github/)${RESET}"
    Write-Separator

    Write-Info "Fájlok másolása és modellek konfigurálása..."
    $helper_script = Join-Path $SCRIPT_DIR "prompts/scripts/install-helper.py"
    & $script:PYTHON_CMD $helper_script "copilot" $SCRIPT_DIR $script:PROJECT_PATH
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Copilot ágensek és skillek sikeresen konfigurálva és másolva!"
        $script:INSTALL_STATUS = "done"
    } else {
        Write-Error "Hiba történt a fájlok másolása során!"
        exit 1
    }
}

# ── Cursor Telepítés ──────────────────────────────────────────
function Install-Cursor {
    $agents_dest = Join-Path $script:PROJECT_PATH ".cursor/agents"
    $skills_dest = Join-Path $script:PROJECT_PATH ".cursor/skills"

    # .cursor mappa létrehozás
    $cursor_folder = Join-Path $script:PROJECT_PATH ".cursor"
    if (-not (Test-Path $cursor_folder -PathType Container)) {
        New-Item -ItemType Directory -Path $cursor_folder -Force | Out-Null
        Write-Success ".cursor/ mappa létrehozva"
    }

    # Ütközés ellenőrzés
    if (Has-ExistingContent @($agents_dest, $skills_dest)) {
        Ask-Conflict ".cursor/agents és .cursor/skills" "mappa"
        switch ($script:CONFLICT_ANSWER) {
            1 {
                Write-Warn "Cursor telepítés kihagyva, a meglévő fájlok érintetlenek."
                $script:INSTALL_STATUS = "skipped"
                return
            }
            2 {
                Write-Error "Telepítés megszakítva."
                exit 1
            }
        }
    }

    # Agents & Skills
    Write-Host ""
    Write-Host "  ${BLUE}📦 Cursor Subagent-ek és Skill-ek telepítése (.cursor/)${RESET}"
    Write-Separator

    Write-Info "Fájlok másolása és modellek konfigurálása..."
    $helper_script = Join-Path $SCRIPT_DIR "prompts/scripts/install-helper.py"
    & $script:PYTHON_CMD $helper_script "cursor" $SCRIPT_DIR $script:PROJECT_PATH
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Cursor rule-ok és command-ok sikeresen konfigurálva és másolva!"
        $script:INSTALL_STATUS = "done"
    } else {
        Write-Error "Hiba történt a fájlok másolása során!"
        exit 1
    }
}

# ── 3. lépés: Másolás és Konfigurálás (Orchestrator) ─────────────────────────
function Create-Symlinks {
    Write-Step "3. lépés: Telepítés"
    Write-Host ""

    if ($script:PLATFORM_CHOICE -eq "antigravity") {
        Install-Antigravity
    } elseif ($script:PLATFORM_CHOICE -eq "claude") {
        Install-Claude
    } elseif ($script:PLATFORM_CHOICE -eq "cursor") {
        Install-Cursor
    } else {
        Install-Copilot
    }
}

# ── Összefoglaló ────────────────────────────────────────────────────────────
function Show-Summary {
    Write-Host ""
    Write-Separator
    Write-Host ""

    if ($script:INSTALL_STATUS -eq "skipped") {
        Write-Host "  ${YELLOW}${BOLD}⚠ Telepítés kihagyva${RESET}"
        Write-Host ""
        Write-Host "  ${GRAY}A meglévő fájlokat nem módosítottam. Futtasd újra a scriptet"
        Write-Host "  és válaszd a ${BOLD}felülírás${GRAY} opciót, ha frissíteni szeretnéd őket.${RESET}"
        Write-Host ""
        return
    }

    Write-Host "  ${GREEN}${BOLD}🎉 Telepítés kész!${RESET}"
    Write-Host ""
    Write-Host "  ${WHITE}Projekt:${RESET}  ${BOLD}$($script:PROJECT_PATH)${RESET}"

    if ($script:PLATFORM_CHOICE -eq "antigravity") {
        Write-Host "  ${WHITE}Platform:${RESET} ${BOLD}Google Antigravity CLI${RESET}"
        Write-Host ""
        Write-Host "  ${GRAY}A telepített struktúra:${RESET}"
        Write-Host "  ${DIM}$($script:PROJECT_PATH)/.agents/"
        Write-Host "  ├── agents/        ${CYAN}(agent JSON fájlok modell-konfigurációval)${RESET}${DIM}"
        Write-Host "  └── skills/        ${CYAN}(skill SKILL.md fájlok modell-konfigurációval)${RESET}"
        Write-Host ""
        Write-Separator
        Write-Host ""
        Write-Host "  ${GRAY}Kezdéshez indítsd el az Antigravity CLI-t a projektedben,"
        Write-Host "  és kérd a ${CYAN}bs-init-project${GRAY} skill futtatását.${RESET}"
    } elseif ($script:PLATFORM_CHOICE -eq "claude") {
        Write-Host "  ${WHITE}Platform:${RESET} ${BOLD}Claude Code${RESET}"
        Write-Host ""
        Write-Host "  ${GRAY}A telepített struktúra:${RESET}"
        Write-Host "  ${DIM}$($script:PROJECT_PATH)/.claude/"
        Write-Host "  ├── agents/        ${CYAN}(agent MD fájlok modell-konfigurációval)${RESET}${DIM}"
        Write-Host "  └── skills/        ${CYAN}(skill SKILL.md fájlok modell-konfigurációval)${RESET}"
        Write-Host ""
        Write-Separator
        Write-Host ""
        Write-Host "  ${GRAY}Kezdéshez indítsd el a Claude Code-ot a projektedben,"
        Write-Host "  és futtasd a ${CYAN}bs-init-project${GRAY} skillt.${RESET}"
    } elseif ($script:PLATFORM_CHOICE -eq "cursor") {
        Write-Host "  ${WHITE}Platform:${RESET} ${BOLD}Cursor${RESET}"
        Write-Host ""
        Write-Host "  ${GRAY}A telepített struktúra:${RESET}"
        Write-Host "  ${DIM}$($script:PROJECT_PATH)/.cursor/"
        Write-Host "  ├── agents/        ${CYAN}(subagent MD fájlok model + effort + readonly konfigurációval)${RESET}${DIM}"
        Write-Host "  └── skills/        ${CYAN}(skill SKILL.md fájlok modell-konfigurációval)${RESET}"
        Write-Host ""
        Write-Host "  ${DIM}${GRAY}Megjegyzés: a subagent \`model\` mezője natívan hat; az \`effort\`"
        Write-Host "  látható ajánlás (a Cursor a nem ismert frontmatter-kulcsot kihagyja).${RESET}"
        Write-Host ""
        Write-Separator
        Write-Host ""
        Write-Host "  ${GRAY}Kezdéshez indítsd el a Cursor Agent CLI-t (${CYAN}agent${GRAY}) a projektedben,"
        Write-Host "  és kérd a ${CYAN}bs-init-project${GRAY} skill futtatását.${RESET}"
    } else {
        Write-Host "  ${WHITE}Platform:${RESET} ${BOLD}GitHub Copilot (CLI & IDE)${RESET}"
        Write-Host ""
        Write-Host "  ${GRAY}A telepített struktúra:${RESET}"
        Write-Host "  ${DIM}$($script:PROJECT_PATH)/.github/"
        Write-Host "  ├── agents/        ${CYAN}(*.agent.md fájlok modell-konfigurációval)${RESET}${DIM}"
        Write-Host "  └── instructions/  ${CYAN}(*.instructions.md fájlok modell-konfigurációval)${RESET}"
        Write-Host ""
        Write-Separator
        Write-Host ""
        Write-Host "  ${GRAY}Kezdéshez a Copilot Chat ablakban vagy a Copilot CLI-ben"
        Write-Host "  használd a ${CYAN}@bs-init-project${GRAY} utasítást a kezdéshez!${RESET}"
    }
    Write-Host ""
}

# ── Főprogram ───────────────────────────────────────────────────────────────
function Main {
    # Python detektálása
    $python_cmd = ""
    if (Get-Command "python" -ErrorAction SilentlyContinue) {
        $python_cmd = "python"
    } elseif (Get-Command "python3" -ErrorAction SilentlyContinue) {
        $python_cmd = "python3"
    } else {
        Write-Error "A Python nem található a rendszeren!"
        Write-Host "  ${GRAY}Kérlek telepítsd a Python-t (legalább 3-as verzió) a folytatáshoz!${RESET}"
        exit 1
    }
    $script:PYTHON_CMD = $python_cmd

    Show-Logo
    Show-Welcome
    Ask-ProjectPath
    Ask-AgentPlatform
    Create-Symlinks
    Show-Summary
}

Main
