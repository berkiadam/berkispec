#!/usr/bin/env bash
#
# init-project.sh — Skill és Agent integráció a támogatott ágensekhez
#
# CÉLJA
# -----
# A prompts/skills/ és prompts/agents/ tartalmát ágens-függően a helyükre
# másolja vagy symlinkkel csatolja, hogy minden támogatott AI-ágens (Claude
# Code, Cursor, Antigravity, Codex, OpenCode, stb.) natívan megtalálja a
# skilleket és specialista ágenseket.
#
# A SCRIPT MIT CSINÁL
# -------------------
# 1. **Ágens-függő integráció.** Minden támogatott ágenshez tudja, hova kell
#    a fájlokat tenni (pl. Claude Code → .claude/commands/ + .claude/agents/,
#    Cursor → .cursor/rules/, stb.). A felhasználó választja, melyik(ek)hez
#    integráljon (CLI paraméter vagy interaktív).
#
# 2. **A fájlokat csak akkor másolja/symlink-eli, ha még nincsenek a helyükön.**
#    Idempotens viselkedés: ha már megvan a symlink vagy másolat és helyes
#    forrásra mutat, nem csinál semmit (kiír egy „már megvan, kihagyva"
#    üzenetet). Ha eltér (pl. más célra mutat egy meglévő symlink), figyelmez-
#    tet és vagy felülírja vagy kihagyja a `--force` paramétertől függően.
#
# 3. **Minden fájlt egyszerre kezel** — a prompts/skills/ alatti összes
#    skill-fájlt és a prompts/agents/ alatti összes ágens-fájlt egy futás
#    alatt. Nem fájlonként kell indítani.
#
# 4. **Single source of truth megőrzése.** Az alapértelmezett mód SYMLINK
#    (a prompts/ alatti fájl marad az igazi forrás, a többi hely csak
#    hivatkozás). Ha symlink nem támogatott (pl. Windows, ami amúgy sincs
#    támogatva — `tanulságok.md`), `--copy` flag-gel fájl-másolásra vált.
#
# STATUS
# ------
# PLACEHOLDER. A teljes skill+agent refaktor (lásd prompts/inprove-list.md
# 6. fejezet) után implementálandó. A refaktor előtt nincs `prompts/skills/`
# és `prompts/agents/` mappa, amire mutatni lehetne.
#
# TERVEZETT MŰKÖDÉS RÉSZLETESEN (lásd inprove-list.md 6.9)
# --------------------------------------------------------
#
#   1. Előfeltétel-ellenőrzés:
#      - prompts/skills/ és prompts/agents/ léteznek-e?
#      - A repó gyökerében vagyunk-e?
#      Ha nem, hibajelzés + exit 1.
#
#   2. Ágens-választás (CLI paraméter vagy interaktív):
#      - claude-code → .claude/commands/ + .claude/agents/
#      - cursor      → .cursor/rules/
#      - antigravity → manuális útmutató kiírása (nincs natív hely)
#      - codex       → manuális útmutató kiírása
#      - opencode    → manuális útmutató kiírása
#      - all         → minden támogatott automatikus integráció
#
#   3. Minden választott ágenshez:
#      a) Cél-mappa létrehozása ha nincs (mkdir -p).
#      b) Minden forrás-fájl ellenőrzése: a célhelyen létezik-e már?
#         - Nem létezik → symlink (vagy copy --copy módban).
#         - Létezik és helyes → kihagy, kiír „már megvan".
#         - Létezik de eltér → --force esetén felülír, egyébként kihagy
#           figyelmeztetéssel.
#      c) Verifikáció: a célhely olvasható-e, érvényes-e?
#
#   4. Összefoglaló kiírása:
#      - Hány fájl került új helyre, hány maradt változatlanul.
#      - Manuális teendők (Antigravity / Codex / OpenCode esetén).
#
# HASZNÁLAT (terv)
# ----------------
#   ./prompts/scripts/init-project.sh                  # interaktív választás
#   ./prompts/scripts/init-project.sh claude-code      # célzott integráció
#   ./prompts/scripts/init-project.sh all              # minden támogatott
#   ./prompts/scripts/init-project.sh all --copy       # symlink helyett másolás
#   ./prompts/scripts/init-project.sh all --force      # felülír eltérő célt
#
# Futtatás előtt: chmod +x prompts/scripts/init-project.sh

set -euo pipefail

echo "init-project.sh: PLACEHOLDER — még nincs implementálva."
echo "Lásd: prompts/inprove-list.md 6. fejezet (Skill + Agent refaktor)."
exit 0
