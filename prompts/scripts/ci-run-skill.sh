#!/usr/bin/env bash
# ci-run-skill.sh — a központosított SDD adaptere (L13-D12 / L13-D13).
#
#   ci-run-skill.sh <skill-név> <ciklus-útvonal>
#   ci-run-skill.sh --selftest
#
#     → artefaktumok a lemezen (riport, cycle-status.md)
#     → exit 0 = zöld · exit 1 = bukás · exit 2 = emberi döntés kell
#
# A CI MINDIG ezt hívja; hogy mögötte melyik ágens fut, azt a `conventions.md`
# `## Review and merge` szekciójának `CI agent:` mezője dönti el. Egy új platform
# támogatása EGYETLEN FÁJL bővítése, és a skillek törzse változatlan marad.
#
# 🔴 A VERDIKT A DETERMINISZTIKUS KAPUKTÓL JÖN, NEM AZ ÁGENSTŐL. Az ágens kilépő
# kódja nem verdikt: a legtöbb CLI `0`-val lép ki akkor is, ha a munka rosszul
# sikerült. Ezért a kilépő kódot a `report-gate-check.py` / `validate-gate-check.py`
# adja — ugyanaz az elv, mint a `cycle-status.md`-nél: a tényt a bizonyítékból
# vezetjük le, nem önbevallásból. EZ TESZI A NÉGY PLATFORMOT VÁLLALHATÓVÁ: egy
# elavult kapcsoló így HANGOS bukást okoz, nem csendben rossz eredményt.
#
# 🔴 NEM-INTERAKTÍV SZERZŐDÉS: a kérdés = STOP. Ha a skill kérdezni akar, a kérdés
# a ciklusmappa `*-questions.md` fájljába kerül, megy az értesítés, és ez az
# adapter `exit 2`-vel tér vissza. A PR nyitva marad, a fejlesztő a saját gépén
# folytatja. Kitalált válasz gépi futtatásban észrevétlen marad — nincs ember a
# hurokban, aki észrevegye.
#
# A HÁROM NEHÉZ RÉSZ (ezek döntik el, hogy egy ágens tényleg futtatható-e CI-ben,
# nem a `-p` flag megléte):
#   1. Hitelesítés — előfizetéses, böngészős bejelentkezés CI-futtatón NEM
#      működik: API-kulcs vagy szolgáltatás-fiók kell, tokenenkénti költséggel.
#      Ez gyakran nem technikai, hanem beszerzési kérdés — a `00` tisztázza.
#   2. Engedély-modell — CI-ben nincs, aki jóváhagyja a shell-parancsokat:
#      előre engedélyezett eszköz-lista kell, platformonként más alakban.
#   3. A verdikt forrása — lásd fent.
#
# ⚠ A CLI-kapcsolók gyorsan változnak. Ezért van `--selftest`: a `00-init-project`
# futtatja a `CI agent:` mező kitöltésekor, hogy az elavulás a PROJEKT
# INDÍTÁSAKOR derüljön ki, ne éles PR-en.
#
# ── MÉRÉS (2026-09-22, éles CLI-kkel) ────────────────────────────────────────
#   claude-code  2.1.278       `claude -p "<prompt>" --permission-mode acceptEdits`
#                              ✓ nem-interaktív, mérve: a prompt lefut, exit 0
#   cursor       2026.08.11    `cursor-agent -p "<prompt>" --force`  (a `--yolo` alias)
#                              ✓ van print mód · ⚠ CI-ben `CURSOR_API_KEY` KELL, és
#                              🔴 HITELESÍTÉSI HIBA UTÁN IS `exit 0`-val lép ki
#                              („Authentication required…") — ez élőben igazolja,
#                              hogy az ágens exit kódja NEM verdikt (L13-D13)
#   copilot      1.0.80        `copilot -p "<prompt>" --allow-all-tools`
#                              ✓ nem-interaktív mód dokumentálva
#   antigravity  1.107.0       🔴 NINCS headless mód: a CLI egy VS Code-szerű
#                              szerkesztő, az `antigravity chat "<prompt>"` GUI
#                              chat-session-t NYIT. CI-futtatón (display nélkül)
#                              ez nem használható — ott a `CI agent: command` ág a
#                              becsületes válasz (pl. a platform saját, esemény-
#                              vezérelt integrációja a PR-en).

set -u

CONVENTIONS="${BS_CONVENTIONS:-conventions.md}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${BS_PYTHON:-python3}"

log()  { printf '%s\n' "$*"; }
warn() { printf '%s\n' "$*" >&2; }

usage() {
  cat <<'USAGE'
Használat:
  ci-run-skill.sh <skill-név> <ciklus-útvonal>
  ci-run-skill.sh --selftest

Skill-nevek: bs-create-pr | bs-review | bs-merge | bs-dev-test | bs-review-and-merge
Kilépő kód: 0 = zöld · 1 = bukás · 2 = emberi döntés kell (vagy használati hiba)
USAGE
}

# ── a `## Review and merge` szekció egy mezője (ANGOL literál, L13-D2) ────────
rm_field() {
  local key="$1"
  awk -v key="$key" '
    /^##[ \t]+/ { insec = (tolower($0) ~ /^##[ \t]+review and merge[ \t]*$/) }
    insec {
      line = $0
      if (match(tolower(line), "\\*\\*" tolower(key) ":\\*\\*")) {
        sub(/^.*\*\*[^*]*:\*\*[ \t]*/, "", line)
        gsub(/^[ \t`]+|[ \t`]+$/, "", line)
        if (line ~ /\|/) next          # a sablon kitöltetlen sora
        print line
        exit
      }
    }
  ' "$CONVENTIONS" 2>/dev/null
}

ci_agent()         { local v; v="$(rm_field "CI agent")";         printf '%s' "${v:-}"; }
ci_agent_command() { local v; v="$(rm_field "CI agent command")"; printf '%s' "${v:-}"; }

# ── az ágens indítása — platformonként MÁS, a szerződés AZONOS ───────────────
# A prompt szövegében a skill hívása áll: ugyanaz, mintha egy ember beírná, hogy
# `/bs-review input: @specs/cycle-NN-…` — csak a beírás helyett a parancs
# argumentuma hordozza.
agent_command_for() {
  local agent="$1" prompt="$2"
  case "$agent" in
    claude-code)
      printf 'claude -p %q --permission-mode acceptEdits' "$prompt" ;;
    cursor)
      printf 'cursor-agent -p %q --force' "$prompt" ;;
    copilot)
      printf 'copilot -p %q --allow-all-tools' "$prompt" ;;
    antigravity)
      # 🔴 MÉRVE (1.107.0): nincs headless mód — az `antigravity chat` GUI
      # chat-session-t nyit, tehát CI-futtatón nem futtatható. A parancsot
      # megépítjük (interaktív gépen használható), de a selftest KIMONDJA a
      # korlátot: kipróbálatlan/alkalmatlan ágenst csendben beleírni nem szabad.
      # (Az Antigravity allowlistje ráadásul PREFIX-ILLESZTÉSES, és a `$( )`
      # parancs-behelyettesítés NEM engedélyezhető — ezért nincs a keret
      # parancsaiban sem, lásd a merge-ág `HEAD..origin/main` alakját.)
      printf 'antigravity chat %q --mode agent' "$prompt" ;;
    command)
      local tmpl; tmpl="$(ci_agent_command)"
      if [ -z "$tmpl" ]; then
        warn 'HIBA: a CI agent mező értéke `command`, de a `CI agent command` mező üres (conventions.md).'
        return 2
      fi
      # A sablonban a `{prompt}` helyőrző a skill-hívás szövegére oldódik.
      printf '%s' "${tmpl//\{prompt\}/$prompt}" ;;
    *)
      warn "HIBA: ismeretlen CI agent: '${agent}'. Megengedett: claude-code | cursor | copilot | antigravity | command"
      return 2 ;;
  esac
}

# ── a VERDIKT: determinisztikus kapuk, nem az ágens exit kódja ───────────────
run_gates() {
  local skill="$1" cycle="$2" rc=0

  # Nem-interaktív szerződés: ha a skill kérdést hagyott a lemezen, EMBERI
  # DÖNTÉS kell — a kapuk eredményétől függetlenül (L13-D12).
  if ls "${cycle}"/*-questions.md >/dev/null 2>&1; then
    for q in "${cycle}"/*-questions.md; do
      if grep -q '^- \[ \]' "$q" 2>/dev/null || [ -s "$q" ]; then
        warn "A skill kérdést hagyott: ${q} — emberi döntés kell (exit 2)."
        return 2
      fi
    done
  fi

  case "$skill" in
    bs-review)
      "$PYTHON_BIN" "${SCRIPT_DIR}/validate-gate-check.py" "$cycle" \
        --review-only --require-ci-review || rc=1
      ;;
    bs-merge|bs-review-and-merge)
      "$PYTHON_BIN" "${SCRIPT_DIR}/validate-gate-check.py" "$cycle" --review-only || rc=1
      if [ -d "${cycle}/test-report/post-merge" ]; then
        "$PYTHON_BIN" "${SCRIPT_DIR}/report-gate-check.py" "$CONVENTIONS" "$cycle" \
          --report-subdir test-report/post-merge || rc=1
      else
        warn 'A test-report/post-merge/ kör-mappa nem jött létre — a VP2 kör nem futott le.'
        rc=1
      fi
      ;;
    bs-dev-test)
      if [ -d "${cycle}/test-report/dev-test" ]; then
        "$PYTHON_BIN" "${SCRIPT_DIR}/report-gate-check.py" "$CONVENTIONS" "$cycle" \
          --report-subdir test-report/dev-test || rc=1
      else
        warn 'A test-report/dev-test/ kör-mappa nem jött létre — a VP3 kör nem futott le.'
        rc=1
      fi
      ;;
    bs-create-pr)
      # A PR MEGLÉTE a bizonyíték. Ha nincs elérhető szolgáltató-CLI, ezt nem
      # tudjuk gépiesen eldönteni — ilyenkor emberi döntés kell, nem vaktában
      # zöld: a csendes átengedés itt a legdrágább hiba.
      if command -v gh >/dev/null 2>&1; then
        gh pr view --json state >/dev/null 2>&1 || rc=1
      elif command -v glab >/dev/null 2>&1; then
        glab mr view >/dev/null 2>&1 || rc=1
      else
        warn 'Nincs gh/glab a futtatón — a PR megléte gépiesen nem ellenőrizhető.'
        return 2
      fi
      ;;
    *)
      warn "HIBA: ismeretlen skill: '${skill}'"
      return 2 ;;
  esac
  return $rc
}

selftest() {
  local agent rc=0
  agent="$(ci_agent)"
  log "ci-run-skill.sh --selftest"
  log "  · conventions.md: ${CONVENTIONS}"
  if [ -z "$agent" ]; then
    warn '  ✗ a CI agent mező üres a ## Review and merge szekcióban — a központosított'
    warn "    úton a CI nem tudja, mit indítson. Töltsd ki a 00-init-project fázisban."
    return 2
  fi
  log "  · CI agent: ${agent}"

  local cmd
  cmd="$(agent_command_for "$agent" '/bs-review input: @specs/cycle-00-selftest')" || return 2
  log "  · a felépített parancs: ${cmd}"

  if [ "$agent" = "antigravity" ]; then
    warn '  ✗ az antigravity CLI (1.107.0) NEM ismer headless módot: az `antigravity chat`'
    warn '    GUI chat-session-t nyit, ami egy CI-futtatón (display nélkül) nem fut le.'
    warn '    Központosított úton válaszd a `CI agent: command` ágat, vagy a platform saját,'
    warn '    esemény-vezérelt PR-integrációját. Interaktív gépen a felépített parancs jó.'
    rc=2
  fi

  local exe="${cmd%% *}"
  if ! command -v "$exe" >/dev/null 2>&1; then
    warn "  ✗ a(z) '${exe}' parancs nem található a PATH-on."
    warn "    Ez a leggyakoribb bukási ok, és SZÁNDÉKOSAN itt derül ki, nem éles PR-en."
    rc=2
  else
    log "  ✓ a(z) '${exe}' elérhető: $(command -v "$exe")"
  fi

  # A kapu-scriptek megléte — a verdikt ezektől jön, nem az ágenstől.
  local missing=0
  for s in validate-gate-check.py report-gate-check.py; do
    if [ -f "${SCRIPT_DIR}/${s}" ]; then
      log "  ✓ kapu-script: ${s}"
    else
      warn "  ✗ hiányzó kapu-script: ${s} — enélkül a verdikt az ágens exit kódjára esne vissza"
      missing=1
    fi
  done
  [ "$missing" -eq 0 ] || rc=2

  case "$agent" in
    cursor)
      if [ -z "${CURSOR_API_KEY:-}" ]; then
        warn '  ⚠ a CURSOR_API_KEY nincs beállítva — a cursor-agent CI-ben enélkül'
        warn '    „Authentication required" hibát ír, DE `exit 0`-val lép ki (mérve).'
        warn '    A verdikt ezért jön a kapuktól, nem az ágenstől.'
      else
        log '  ✓ CURSOR_API_KEY beállítva'
      fi ;;
  esac

  log ""
  log "  ⚠ A hitelesítést ez a selftest NEM tudja ellenőrizni: egy előfizetéses,"
  log "    böngészős bejelentkezés a te gépeden működik, a CI-futtatón nem. Éles"
  log "    használat előtt futtasd le ezt a scriptet MAGÁN A CI-N is, egy próba-ciklussal."
  return $rc
}

main() {
  case "${1:-}" in
    --selftest) selftest; exit $? ;;
    -h|--help|"") usage; exit 2 ;;
  esac

  local skill="$1" cycle="${2:-}"
  if [ -z "$cycle" ]; then usage; exit 2; fi
  if [ ! -d "$cycle" ]; then warn "HIBA: nincs ilyen ciklusmappa: ${cycle}"; exit 2; fi

  local agent cmd
  agent="$(ci_agent)"
  if [ -z "$agent" ]; then
    warn 'HIBA: a CI agent mező üres a ## Review and merge szekcióban.'
    exit 2
  fi
  cmd="$(agent_command_for "$agent" "/${skill} input: @${cycle}")" || exit 2

  log "ci-run-skill.sh — skill: ${skill} · ciklus: ${cycle} · ágens: ${agent}"
  log "  · indítás: ${cmd}"
  set +e
  eval "$cmd"
  local agent_rc=$?
  set -e
  log "  · az ágens kilépő kódja: ${agent_rc} — EZ NEM VERDIKT (L13-D13)."

  run_gates "$skill" "$cycle"
  local rc=$?
  case $rc in
    0) log "  ✓ a determinisztikus kapuk zöldek — exit 0" ;;
    1) log "  ✗ kapu-bukás — exit 1" ;;
    2) log "  · emberi döntés kell — exit 2" ;;
  esac
  exit $rc
}

main "$@"
