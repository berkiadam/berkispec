#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# A kétnyelvűsítés elfogadási sora (a terv 16. szakasza) — MEGISMÉTELHETŐEN.
#
# Miért script: a 16.2 explicit „scriptelve" elvárás, a többi kritérium pedig
# amúgy is egy-egy parancs. Kézzel futtatva mindig kimarad valamelyik.
#
#   ./prompts/scripts/acceptance-check.sh            # 16.2–16.5
#   ./prompts/scripts/acceptance-check.sh --baseline # + a 16.1 alapfelvétel elkészítése
#
# A 16.1 byte-azonossághoz kell egy ALAPFELVÉTEL: futtasd `--baseline`-nal a
# módosítás ELŐTT, majd `--baseline` nélkül utána. A 16.1 két ELVÁRT kivétele
# (7.6 fixer-refaktor, 9.5 output-language beemelés) után újra kell alapozni.
#
# Kilépő kód: 0 = minden kritérium teljesült, 1 = legalább egy bukott.
# ─────────────────────────────────────────────────────────────────────────────
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
WORK="${TMPDIR:-/tmp}/berkispec-acceptance"
BASELINE="${WORK}/baseline"
mkdir -p "${WORK}"

ok=0; bad=0
say() { if [ "$1" = 0 ]; then echo "  ✓ $2"; ok=$((ok+1)); else echo "  ✗ $2"; bad=$((bad+1)); fi; }

# A telepített kimenet hash-listája: 5 platform × 14 skill, valamint az
# 5 platform × 11 agent `prepare_agent_content` kimenete.
snapshot() {
  local out="$1"
  python3 - "$out" <<'PYEOF'
import hashlib, importlib.util, pathlib, shutil, sys
spec = importlib.util.spec_from_file_location("ih", "prompts/scripts/install-helper.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
out = pathlib.Path(sys.argv[1]); shutil.rmtree(out, ignore_errors=True); out.mkdir(parents=True)
sums = []
for plat in ("claude", "codex", "antigravity", "cursor", "copilot"):
    dest = out / "_build" / plat
    for f in sorted(m.skills_src_dir(".").glob("*.md")):
        m.write_markdown_skill(f, dest, src_dir=pathlib.Path("."), platform=plat)
    for p in sorted(dest.rglob("SKILL.md")):
        sums.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  skill {plat}/{p.parent.name}")
    for f in sorted(m.agents_src_dir(".").glob("*.md")):
        c = m.prepare_agent_content(f, pathlib.Path("."), plat)
        sums.append(f"{hashlib.sha256(c.encode()).hexdigest()}  agent {plat}/{f.name}")
shutil.rmtree(out / "_build", ignore_errors=True)
(out / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")
print(len(sums))
PYEOF
}

if [ "${1:-}" = "--baseline" ]; then
  n="$(snapshot "${BASELINE}")"
  echo "16.1 alapfelvétel elkészült: ${n} hash → ${BASELINE}/SHA256SUMS"
  echo "Most végezd el a módosítást, majd futtasd újra a scriptet --baseline NÉLKÜL."
  exit 0
fi

echo "── 16.1 byte-azonossági keret (hu/hu regresszió)"
if [ -f "${BASELINE}/SHA256SUMS" ]; then
  n="$(snapshot "${WORK}/current")"
  diff -q "${BASELINE}/SHA256SUMS" "${WORK}/current/SHA256SUMS" >/dev/null
  say $? "${n} hash változatlan az alapfelvételhez képest"
else
  echo "  ⊘ nincs alapfelvétel — futtasd egyszer --baseline-nal (kihagyva)"
fi

echo "── 16.2 négy kombinációs próbatelepítés (a valódi install.sh-val)"
rm -rf "${WORK}/inst"; f=0
for pl in "hu hu" "en hu" "hu en" "en en"; do
  set -- $pl
  for plat in claude codex antigravity cursor copilot; do
    d="${WORK}/inst/$1-$2/${plat}"; mkdir -p "$d"
    ./install.sh --platform "${plat}" --prompt-lang "$1" --project-lang "$2" --path "$d" >/dev/null 2>&1 || f=1
  done
done
say $f "20 futás (4 nyelvkombináció × 5 platform) exit=0"
[ -z "$(grep -rl '<!-- INCLUDE:' "${WORK}/inst" 2>/dev/null)" ]; say $? "nincs feloldatlan INCLUDE marker"
[ -z "$(grep -rl '<sec:\|<field:\|<status:' "${WORK}/inst" 2>/dev/null)" ]; say $? "nincs feloldatlan nyelvi token"
total="$(find "${WORK}/inst" -name SKILL.md | wc -l)"
withdesc="$(grep -l '^description:' $(find "${WORK}/inst" -name SKILL.md) 2>/dev/null | wc -l)"
[ "${withdesc}" -eq "${total}" ]; say $? "minden telepített SKILL.md-ben van description (${withdesc}/${total})"

echo "── 16.3 nyelvi paritás-kapu"
python3 prompts/scripts/lang-parity-check.py --strict --check >/dev/null 2>&1
say $? "lang-parity-check.py --check --strict → exit 0"

echo "── 16.4 gemini agent.json tükrök"
python3 prompts/scripts/sync-gemini-agents.py --check >/dev/null 2>&1
say $? "sync-gemini-agents.py --check → exit 0 (minden prompt-nyelvre)"

echo "── 16.5 nyelvi tisztaság az en fákon"
[ -z "$(grep -rn '[áéíóöőúüűÁÉÍÓÖŐÚÜŰ]' prompts/skills-en prompts/agents-en prompts/shared-en prompts/lang/en 2>/dev/null)" ]
say $? "0 magyar ékezet a négy en fán"

echo ""
echo "  ÖSSZESEN: ${ok} teljesült · ${bad} bukott"
echo "  ⓘ A 16.6 (éles próba: egy valódi projekt teljes ciklusa) NEM automatizálható — kézzel futtatandó."
[ "${bad}" -eq 0 ]
