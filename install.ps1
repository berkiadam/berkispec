# ─────────────────────────────────────────────────────────────────────────────
# BerkiSpec Installer (Windows PowerShell)
# Telepíti a BerkiSpec agent-eket és skill-eket a célprojektbe.
# Supports: Google Antigravity CLI, Claude Code, GitHub Copilot (CLI & IDE)
#
# Nem interaktív mód (LG20): ha EGYETLEN paramétert sem adsz meg, a régi
# interaktív út fut változatlanul. Részleges megadásnál a megadottakat
# használjuk, a többit interaktívan kérdezzük.
#   .\install.ps1 -Platform claude -PromptLang en -ProjectLang hu -Path C:\projekt
# ─────────────────────────────────────────────────────────────────────────────
param(
    [ValidateSet("claude", "codex", "antigravity", "cursor", "copilot")]
    [string]$Platform = "",

    # Az ágens INSTRUKCIÓINAK nyelve (default: en) — LG7
    [ValidateSet("hu", "en")]
    [string]$PromptLang = "",

    # Amit az ágens ÍR a projektbe és neked (default: hu) — LG7
    [ValidateSet("hu", "en")]
    [string]$ProjectLang = "",

    [string]$Path = "",

    # Ütközésnél felülír. Enélkül nem interaktív módban MEGÁLLUNK — a csendes
    # felülírás visszafordíthatatlan kárt okozhat egy scriptelt telepítésben.
    [switch]$Force,

    [switch]$Help
)

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
$HISTORY_FILE = Join-Path $SCRIPT_DIR "history"

# ── Telepitesi elozmeny (history fajl) ──────────────────────────────────────
# A legutobbi celprojekt utvonalat a repo gyokereben levo `history` fajlban
# taroljuk, hogy ujrafuttataskor ne kelljen ujra begepelni. A fajl GEPFUGGO
# (lokalis utvonalat tartalmaz), ezert a .gitignore kizarja.

function Get-LastProjectPath {
    if (-not (Test-Path $HISTORY_FILE -PathType Leaf)) { return "" }
    $line = Get-Content $HISTORY_FILE -ErrorAction SilentlyContinue |
        Where-Object { $_ -match '^LAST_PROJECT_PATH=' } | Select-Object -Last 1
    if ([string]::IsNullOrWhiteSpace($line)) { return "" }
    return $line -replace '^LAST_PROJECT_PATH=', ''
}

function Save-History {
    param([string]$Path, [string]$Platform)
    try {
        @(
            "# BerkiSpec telepitesi elozmeny - automatikusan generalt, ne szerkeszd kezzel.",
            "# Ebbol tolti ki a telepito az alapertelmezett celmappat ujrafuttataskor.",
            "LAST_PROJECT_PATH=$Path",
            "LAST_PLATFORM=$Platform",
            "LAST_INSTALL=$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        ) | Set-Content -Path $HISTORY_FILE -Encoding UTF8
    } catch {
        Write-Warn "A telepitesi elozmenyt nem sikerult elmenteni ($HISTORY_FILE)."
    }
}

# A prompt-forrásmappákat NEM itt oldjuk fel: a nyelvenkénti fát
# (`prompts/skills-<lang>` stb.) az install-helper.py `_lang_subdir()`-je
# választja ki. Korábban itt három változó állt, de egyik sem volt használatban.
# Globális állapot változók
$PROJECT_PATH = ""
$PLATFORM_CHOICE = "" # "antigravity" vagy "claude" vagy "copilot" vagy "cursor"
$INSTALL_STATUS = ""  # "done" vagy "skipped"
$CONFLICT_ANSWER = 0
$PYTHON_CMD = ""

# ── Nyelvi választás (LG1/LG7) ──────────────────────────────────────────────
# KÉT FÜGGETLEN tengely, mindkettő `hu` | `en`:
#   PROMPT_LANG_CHOICE  — milyen nyelvű INSTRUKCIÓT kap az ágens (default: en)
#   PROJECT_LANG_CHOICE — milyen nyelven ÍR a projektbe és a felhasználónak (default: hu)
# Mindkettő BUILD-TIME dől el és bedrótozódik a telepített promptba (LG2); a
# projektben semmilyen nyelvi mező nem marad (LG17), tehát utólag csak
# újratelepítéssel változtatható. Ezért írja ki a záró összefoglaló hangosan.
$PROMPT_LANG_CHOICE = ""
$PROJECT_LANG_CHOICE = ""
$NON_INTERACTIVE = $false
$FORCE_OVERWRITE = $false

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

    $last_path = Get-LastProjectPath
    if (-not [string]::IsNullOrWhiteSpace($last_path)) {
        if (Test-Path $last_path -PathType Container) {
            Write-Host "  ${GRAY}Legutóbbi telepítés helye: ${BOLD}${last_path}${RESET}"
            Write-Host "  ${GRAY}Nyomj ${BOLD}Enter${RESET}${GRAY}-t az elfogadásához, vagy adj meg másikat.${RESET}"
            Write-Host ""
        } else {
            Write-Host "  ${GRAY}A legutóbbi telepítési hely már nem létezik (${last_path}) — add meg az újat.${RESET}"
            Write-Host ""
            $last_path = ""
        }
    }

    while ($true) {
        Write-Host -NoNewline "  ${MAGENTA}❯${RESET} Projekt mappa: "
        $project_path = Read-Host

        # Üres bevitel = a legutóbbi telepítési hely elfogadása
        if ([string]::IsNullOrWhiteSpace($project_path) -and -not [string]::IsNullOrWhiteSpace($last_path)) {
            $project_path = $last_path
        }

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
    Write-Host "  ${CYAN}6)${RESET} ${GREEN}●${RESET} Codex CLI"
    Write-Host ""

    $choice = ""
    while ($true) {
        Write-Host -NoNewline "  ${MAGENTA}❯${RESET} Választás [1-6]: "
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
            "6" {
                $script:PLATFORM_CHOICE = "codex"
                break
            }
            "2" {
                Write-Host ""
                Write-Separator
                Write-Host ""
                Write-Host "  ${ORANGE}🚧  Még nincs implementálva.${RESET}"
                Write-Host ""
                Write-Host "  ${GRAY}Jelenleg a ${GREEN}Google Antigravity CLI${GRAY}, a ${GREEN}Claude Code${GRAY}, a ${GREEN}Cursor${GRAY}, a ${GREEN}GitHub Copilot${GRAY} és a ${GREEN}Codex CLI${GRAY} támogatott."
                Write-Host "  A többi platform hamarosan érkezik!${RESET}"
                Write-Host ""
                Write-Separator
                Write-Host ""
                exit 0
            }
            default {
                Write-Warn "Kérlek válassz 1-6 közötti számot."
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
    } elseif ($script:PLATFORM_CHOICE -eq "codex") {
        Write-Success "Platform: ${BOLD}Codex CLI${RESET}"
    } else {
        Write-Success "Platform: ${BOLD}GitHub Copilot${RESET}"
    }

    # ── Codex ↔ Antigravity kölcsönös kizárás — előzetes figyelmeztetés ──
    if ($script:PLATFORM_CHOICE -eq "codex" -or $script:PLATFORM_CHOICE -eq "antigravity") {
        Write-Host ""
        Write-Warn "A ${BOLD}Codex CLI${RESET} és a ${BOLD}Google Antigravity CLI${RESET} a közös ${BOLD}.agents/skills/${RESET} mappát használja."
        Write-Host "  ${GRAY}Ezért egy projektbe gyakorlatilag csak az egyik telepíthető — ha ezt"
        Write-Host "  telepíted, a másikat ugyanebbe a projektbe később már nem tudod.${RESET}"
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

# Nyelvi kód → ember-olvasható címke.
function Get-LangLabel {
    param([string]$code)
    switch ($code) {
        "en" { return "English" }
        "hu" { return "Magyar" }
        default { return $code }
    }
}

# ── 2/b. lépés: Nyelvi választás (LG1/LG7) ──────────────────────────────────
# A két tengely FÜGGETLEN. A default az `EN` prompt + `HU` projekt: az angol
# instrukció olcsóbb tokenben és a gyenge modellek pontosabban követik,
# miközben a leadott dokumentáció magyar marad.
function Ask-Languages {
    # Paraméterrel megadott értéket nem kérdezünk újra.
    if (-not [string]::IsNullOrWhiteSpace($script:PROMPT_LANG_CHOICE) -and
        -not [string]::IsNullOrWhiteSpace($script:PROJECT_LANG_CHOICE)) {
        return
    }

    Write-Step "2/b. lépés: Nyelvek kiválasztása"
    Write-Host ""
    Write-Host "  ${GRAY}Két külön beállítás — nem ugyanaz, és nem is kell egyezniük.${RESET}"
    Write-Host ""

    if ([string]::IsNullOrWhiteSpace($script:PROMPT_LANG_CHOICE)) {
        Write-Host "  ${WHITE}Milyen nyelvűek legyenek a PROMPTOK?${RESET}"
        Write-Host "  ${GRAY}(amit az ágens olvas — a te dokumentumaidat nem érinti)${RESET}"
        Write-Host ""
        Write-Host "  ${CYAN}1)${RESET} English ${GRAY}[alapértelmezett]${RESET}"
        Write-Host "  ${CYAN}2)${RESET} Magyar"
        Write-Host ""
        while ($true) {
            Write-Host -NoNewline "  ${MAGENTA}❯${RESET} Választás [1-2, Enter = 1]: "
            $choice = Read-Host
            if ([string]::IsNullOrWhiteSpace($choice) -or $choice -eq "1") { $script:PROMPT_LANG_CHOICE = "en"; break }
            if ($choice -eq "2") { $script:PROMPT_LANG_CHOICE = "hu"; break }
            Write-Warn "Kérlek válassz 1 vagy 2 közül."
        }
        Write-Host ""
    }

    if ([string]::IsNullOrWhiteSpace($script:PROJECT_LANG_CHOICE)) {
        Write-Host "  ${WHITE}Milyen nyelvű legyen a PROJEKT?${RESET}"
        Write-Host "  ${GRAY}(amit az ágens ÍR: spec.md, plan.md, riportok, és amit neked válaszol)${RESET}"
        Write-Host ""
        Write-Host "  ${CYAN}1)${RESET} Magyar ${GRAY}[alapértelmezett]${RESET}"
        Write-Host "  ${CYAN}2)${RESET} English"
        Write-Host ""
        while ($true) {
            Write-Host -NoNewline "  ${MAGENTA}❯${RESET} Választás [1-2, Enter = 1]: "
            $choice = Read-Host
            if ([string]::IsNullOrWhiteSpace($choice) -or $choice -eq "1") { $script:PROJECT_LANG_CHOICE = "hu"; break }
            if ($choice -eq "2") { $script:PROJECT_LANG_CHOICE = "en"; break }
            Write-Warn "Kérlek válassz 1 vagy 2 közül."
        }
        Write-Host ""
    }

    $pl = Get-LangLabel $script:PROMPT_LANG_CHOICE
    $jl = Get-LangLabel $script:PROJECT_LANG_CHOICE
    Write-Success "Prompt nyelve: ${BOLD}$pl${RESET} · Projekt nyelve: ${BOLD}$jl${RESET}"

    # A §10 óta a kapu-scriptek a `lang-keys.json`-ból illesztenek: az artefaktum-
    # oldal nyelvhelyes, csak a konzol-üzenet maradt magyar (LG10).
    if ($script:PROJECT_LANG_CHOICE -eq "en") {
        Write-Host ""
        Write-Warn "A projekt nyelve ${BOLD}English${RESET}: a kapu-scriptek ${BOLD}konzol-üzenetei${RESET} magyarok."
        Write-Host "  ${GRAY}Az artefaktumokat ez nem érinti — a kapuk a telepített lang-keys.json"
        Write-Host "  angol szekciónevei szerint illesztenek és írnak. Csak a futtatónak szóló"
        Write-Host "  kimenet marad magyar.${RESET}"
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

    # Nem interaktív módban NEM kérdezünk és NEM írunk felül csendben (LG20):
    # `-Force` nélkül megállunk.
    if ($script:NON_INTERACTIVE) {
        if ($script:FORCE_OVERWRITE) {
            $script:CONFLICT_ANSWER = 0
            Write-Warn "Felülírás (-Force): ${DIM}$target${RESET} ($type)"
        } else {
            Write-Error "Már létezik: $target ($type)."
            Write-Host "  ${GRAY}Nem interaktív módban nem írom felül. Adj meg ${BOLD}-Force${RESET}${GRAY}-ot,"
            Write-Host "  vagy futtasd a scriptet paraméterek nélkül, interaktív módban.${RESET}"
            exit 1
        }
        return
    }

    $script:CONFLICT_ANSWER = Handle-Conflict $target $type
}

# ── Codex ↔ Antigravity kölcsönös kizárás ─────────────────────────────────────
# A Codex és az Antigravity UGYANAZT a .agents/skills/ mappát használja, ezért
# egy projektbe csak az egyik telepíthető értelmesen. Ha a másik platform egyedi
# markere (.codex/agents vagy .agents/agents) már létezik, figyelmeztet és rákérdez.
function Check-MutualExclusion {
    param(
        [string]$other_marker,
        [string]$other_name
    )

    if (Has-ExistingContent @($other_marker)) {
        Write-Host ""
        Write-Warn "Úgy tűnik, a(z) ${BOLD}${other_name}${RESET} már telepítve van ebbe a projektbe."
        Write-Host "  ${GRAY}A Codex és az Antigravity a közös ${BOLD}.agents/skills/${RESET}${GRAY} mappát használja,"
        Write-Host "  ezért a folytatás felülírhatja a(z) ${other_name} skilljeit.${RESET}"
        if ($script:NON_INTERACTIVE) {
            if ($script:FORCE_OVERWRITE) {
                Write-Warn "Folytatás (-Force)."
                return
            }
            Write-Error "Nem interaktív módban megállok. Adj meg -Force-ot, ha tudatosan felülírod."
            exit 1
        }
        Write-Host -NoNewline "    ${YELLOW}?${RESET} Biztosan folytatod? [${BOLD}i${RESET}/${BOLD}n${RESET}]: "
        $answer = Read-Host
        switch ($answer.ToLower()) {
            "i" { return }
            "igen" { return }
            default {
                Write-Error "Telepítés megszakítva."
                exit 1
            }
        }
    }
}

# ── Google Antigravity Telepítés ──────────────────────────────
function Install-Antigravity {
    $agents_dest = Join-Path $script:PROJECT_PATH ".agents/agents"
    $skills_dest = Join-Path $script:PROJECT_PATH ".agents/skills"

    # Codex ↔ Antigravity kölcsönös kizárás
    Check-MutualExclusion (Join-Path $script:PROJECT_PATH ".codex/agents") "Codex CLI"

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
    & $script:PYTHON_CMD $helper_script "antigravity" $SCRIPT_DIR $script:PROJECT_PATH $script:PROMPT_LANG_CHOICE $script:PROJECT_LANG_CHOICE
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
    & $script:PYTHON_CMD $helper_script "claude" $SCRIPT_DIR $script:PROJECT_PATH $script:PROMPT_LANG_CHOICE $script:PROJECT_LANG_CHOICE
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
    & $script:PYTHON_CMD $helper_script "copilot" $SCRIPT_DIR $script:PROJECT_PATH $script:PROMPT_LANG_CHOICE $script:PROJECT_LANG_CHOICE
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
    & $script:PYTHON_CMD $helper_script "cursor" $SCRIPT_DIR $script:PROJECT_PATH $script:PROMPT_LANG_CHOICE $script:PROJECT_LANG_CHOICE
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Cursor rule-ok és command-ok sikeresen konfigurálva és másolva!"
        $script:INSTALL_STATUS = "done"
    } else {
        Write-Error "Hiba történt a fájlok másolása során!"
        exit 1
    }
}

# ── Codex CLI Telepítés ───────────────────────────────────────
function Install-Codex {
    $agents_dest = Join-Path $script:PROJECT_PATH ".codex/agents"
    $skills_dest = Join-Path $script:PROJECT_PATH ".agents/skills"

    # Codex ↔ Antigravity kölcsönös kizárás
    Check-MutualExclusion (Join-Path $script:PROJECT_PATH ".agents/agents") "Google Antigravity CLI"

    $codex_folder = Join-Path $script:PROJECT_PATH ".codex"

    # .codex létezik, de nem mappa (stray fájl/hivatkozás)
    if ((Test-Path $codex_folder) -and -not (Test-Path $codex_folder -PathType Container)) {
        Write-Warn "A ${DIM}$codex_folder${RESET} létezik, de nem mappa (fájl vagy hivatkozás)."
        Write-Host "  ${GRAY}A Codex telepítéshez ennek mappának kell lennie.${RESET}"
        Write-Host -NoNewline "    ${YELLOW}?${RESET} Eltávolítsam és mappaként hozzam létre? [${BOLD}i${RESET}/${BOLD}n${RESET}]: "
        $codex_rm = Read-Host
        switch ($codex_rm.ToLower()) {
            "i" { Remove-Item -Force $codex_folder }
            "igen" { Remove-Item -Force $codex_folder }
            default {
                Write-Error "Telepítés megszakítva. Töröld vagy nevezd át a .codex fájlt, majd futtasd újra."
                exit 1
            }
        }
    }

    # .codex mappa létrehozás
    if (-not (Test-Path $codex_folder -PathType Container)) {
        New-Item -ItemType Directory -Path $codex_folder -Force | Out-Null
        Write-Success ".codex/ mappa létrehozva"
    }

    # Ütközés ellenőrzés
    if (Has-ExistingContent @($agents_dest, $skills_dest)) {
        Ask-Conflict ".codex/agents és .agents/skills" "mappa"
        switch ($script:CONFLICT_ANSWER) {
            1 {
                Write-Warn "Codex telepítés kihagyva, a meglévő fájlok érintetlenek."
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
    Write-Host "  ${BLUE}📦 Codex Subagent-ek (.codex/agents/) és Skill-ek (.agents/skills/) telepítése${RESET}"
    Write-Separator

    Write-Info "Fájlok másolása és modellek konfigurálása..."
    $helper_script = Join-Path $SCRIPT_DIR "prompts/scripts/install-helper.py"
    & $script:PYTHON_CMD $helper_script "codex" $SCRIPT_DIR $script:PROJECT_PATH $script:PROMPT_LANG_CHOICE $script:PROJECT_LANG_CHOICE
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Codex subagentek (TOML) és skillek sikeresen konfigurálva és másolva!"
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
    } elseif ($script:PLATFORM_CHOICE -eq "codex") {
        Install-Codex
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

    # ── Nyelvi visszajelzés (12.3 / LG2) ──
    # Ez az EGYETLEN hely, ahol a felhasználó szembesül a nyelvi választásával:
    # a projektbe semmilyen nyelvi mező nem kerül (LG17).
    $pl = Get-LangLabel $script:PROMPT_LANG_CHOICE
    $jl = Get-LangLabel $script:PROJECT_LANG_CHOICE
    Write-Host "  ${WHITE}Prompt nyelve:${RESET}  ${BOLD}$pl${RESET} ${GRAY}(amit az ágens olvas)${RESET}"
    Write-Host "  ${WHITE}Projekt nyelve:${RESET} ${BOLD}$jl${RESET} ${GRAY}(amit az ágens ír: spec.md, plan.md, riportok, válaszok)${RESET}"
    Write-Host ""
    Write-Host "  ${YELLOW}⚠${RESET}  ${GRAY}Mindkét nyelv ${BOLD}bedrótozódott${RESET}${GRAY} a telepített promptokba."
    Write-Host "     A projektben nincs nyelvi beállítás, ezért a váltás csak ${BOLD}újratelepítéssel${RESET}${GRAY} lehetséges.${RESET}"

    if ($script:PLATFORM_CHOICE -eq "antigravity") {
        Write-Host "  ${WHITE}Platform:${RESET} ${BOLD}Google Antigravity CLI${RESET}"
        Write-Host ""
        Write-Host "  ${GRAY}A telepített struktúra:${RESET}"
        Write-Host "  ${DIM}$($script:PROJECT_PATH)/.agents/"
        Write-Host "  ├── agents/        ${CYAN}(agent JSON fájlok modell-konfigurációval)${RESET}${DIM}"
        Write-Host "  └── skills/        ${CYAN}(fázis-skillek, SKILL.md)${RESET}"
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
        Write-Host "  └── skills/        ${CYAN}(fázis-skillek, SKILL.md)${RESET}"
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
        Write-Host "  └── skills/        ${CYAN}(fázis-skillek, SKILL.md)${RESET}"
        Write-Host ""
        Write-Host "  ${DIM}${GRAY}Megjegyzés: a subagent \`model\` mezője natívan hat; az \`effort\`"
        Write-Host "  látható ajánlás (a Cursor a nem ismert frontmatter-kulcsot kihagyja).${RESET}"
        Write-Host ""
        Write-Separator
        Write-Host ""
        Write-Host "  ${GRAY}Kezdéshez indítsd el a Cursor Agent CLI-t (${CYAN}agent${GRAY}) a projektedben,"
        Write-Host "  és kérd a ${CYAN}bs-init-project${GRAY} skill futtatását.${RESET}"
    } elseif ($script:PLATFORM_CHOICE -eq "codex") {
        Write-Host "  ${WHITE}Platform:${RESET} ${BOLD}Codex CLI${RESET}"
        Write-Host ""
        Write-Host "  ${GRAY}A telepített struktúra:${RESET}"
        Write-Host "  ${DIM}$($script:PROJECT_PATH)/.codex/"
        Write-Host "  ├── agents/        ${CYAN}(subagent TOML fájlok model + reasoning-effort + sandbox konfigurációval)${RESET}${DIM}"
        Write-Host "  └── scripts/       ${CYAN}(helper scriptek)${RESET}${DIM}"
        Write-Host "  $($script:PROJECT_PATH)/.agents/"
        Write-Host "  └── skills/        ${CYAN}(skill SKILL.md fájlok — a Codex innen olvassa a projekt-skilleket)${RESET}"
        Write-Host ""
        Write-Host "  ${DIM}${GRAY}Megjegyzés: a subagent \`model\` és \`model_reasoning_effort\` mezője"
        Write-Host "  natívan hat. A skillek az Antigravity-vel KÖZÖS .agents/skills/ mappát"
        Write-Host "  használják — ugyanabba a projektbe a kettő közül csak az egyik telepíthető.${RESET}"
        Write-Host ""
        Write-Separator
        Write-Host ""
        Write-Host "  ${GRAY}Kezdéshez indítsd el a Codex CLI-t a projektedben,"
        Write-Host "  és kérd a ${CYAN}bs-init-project${GRAY} skill futtatását.${RESET}"
    } else {
        Write-Host "  ${WHITE}Platform:${RESET} ${BOLD}GitHub Copilot (CLI & IDE)${RESET}"
        Write-Host ""
        Write-Host "  ${GRAY}A telepített struktúra:${RESET}"
        Write-Host "  ${DIM}$($script:PROJECT_PATH)/.github/"
        Write-Host "  ├── agents/        ${CYAN}(*.agent.md fájlok modell-konfigurációval)${RESET}${DIM}"
        Write-Host "  └── instructions/  ${CYAN}(fázis-skillek, *.instructions.md)${RESET}"
        Write-Host ""
        Write-Separator
        Write-Host ""
        Write-Host "  ${GRAY}Kezdéshez a Copilot Chat ablakban vagy a Copilot CLI-ben"
        Write-Host "  használd a ${CYAN}@bs-init-project${GRAY} utasítást a kezdéshez!${RESET}"
    }
    Write-Host ""
}

# ── Főprogram ───────────────────────────────────────────────────────────────
# ── Használat (LG20) ────────────────────────────────────────────────────────
function Show-Usage {
    Write-Host @"
BerkiSpec telepito

Hasznalat:
  .\install.ps1                       interaktiv mod (valtozatlan, ez a default)
  .\install.ps1 [parameterek]         nem interaktiv / reszlegesen elore kitoltott mod

Parameterek:
  -Platform <nev>        claude | codex | antigravity | cursor | copilot
  -PromptLang <nyelv>    hu | en    - az agens INSTRUKCIOINAK nyelve   (default: en)
  -ProjectLang <nyelv>   hu | en    - amit az agens IR a projektbe     (default: hu)
  -Path <utvonal>        a celprojekt konyvtara
  -Force                 utkozesnel felulir (enelkul nem interaktiv modban MEGALL)
  -Help                  ez a sugo

Megjegyzes:
  Ha EGYETLEN parametert sem adsz meg, a regi interaktiv ut fut valtozatlanul.
  A ket nyelvi beallitas FUGGETLEN, es a telepitett promptokba BEDROTOZODIK -
  utolag csak ujratelepitessel valtoztathato.

Pelda:
  .\install.ps1 -Platform claude -PromptLang en -ProjectLang hu -Path C:\projekt
"@
}

# A param() blokk értékeinek átvétele a script-scope állapotba (LG20).
function Initialize-FromParams {
    if ($Help) { Show-Usage; exit 0 }

    if (-not [string]::IsNullOrWhiteSpace($Platform))    { $script:PLATFORM_CHOICE = $Platform;     $script:NON_INTERACTIVE = $true }
    if (-not [string]::IsNullOrWhiteSpace($PromptLang))  { $script:PROMPT_LANG_CHOICE = $PromptLang; $script:NON_INTERACTIVE = $true }
    if (-not [string]::IsNullOrWhiteSpace($ProjectLang)) { $script:PROJECT_LANG_CHOICE = $ProjectLang; $script:NON_INTERACTIVE = $true }
    if ($Force) { $script:FORCE_OVERWRITE = $true; $script:NON_INTERACTIVE = $true }

    if (-not [string]::IsNullOrWhiteSpace($Path)) {
        if (-not (Test-Path $Path -PathType Container)) {
            Write-Error "A megadott celprojekt nem letezik: $Path"
            exit 2
        }
        $script:PROJECT_PATH = (Resolve-Path $Path).Path
        $script:NON_INTERACTIVE = $true
    }

    # Nem interaktív módban a hiányzó nyelvi értékek a defaultra esnek (LG7).
    if ($script:NON_INTERACTIVE) {
        if ([string]::IsNullOrWhiteSpace($script:PROMPT_LANG_CHOICE))  { $script:PROMPT_LANG_CHOICE = "en" }
        if ([string]::IsNullOrWhiteSpace($script:PROJECT_LANG_CHOICE)) { $script:PROJECT_LANG_CHOICE = "hu" }
    }
}

function Main {
    Initialize-FromParams

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
    if ([string]::IsNullOrWhiteSpace($script:PROJECT_PATH)) { Ask-ProjectPath }
    if ([string]::IsNullOrWhiteSpace($script:PLATFORM_CHOICE)) { Ask-AgentPlatform }
    Ask-Languages
    Create-Symlinks
    # A célmappa megjegyzése a következő futtatáshoz (lásd `history` fájl).
    if (-not [string]::IsNullOrWhiteSpace($script:PROJECT_PATH)) {
        Save-History -Path $script:PROJECT_PATH -Platform $script:PLATFORM_CHOICE
    }
    Show-Summary
}

Main
