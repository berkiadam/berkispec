#!/usr/bin/env python3
"""PW4 — az agentic eszköz-mappák átmásolása egy friss `git worktree`-be.

Miért kell (PW3/B, párhuzamos tervezési ablak): a linked worktree a git
által KÖVETETT fájlokat kapja meg, az ignorált/nem követett tartalmat nem.
Az agentic eszközök konfigurációja (`.claude/`, `.agents/`, `.codex/`,
`.cursor/`, `.github/`, `AGENTS.md`, `CLAUDE.md`, …) projektenként hol
commitálva van, hol gitignore-olva — az utóbbi esetben a friss worktree-ben
NEM lesznek meg a `bs-*` skillek, a subagentek és a kapu-scriptek, tehát a
párhuzamosan indított ágens vakon áll. Ez a script pótolja őket.

Mit csinál:
  - a FŐ worktree gyökeréből (`git rev-parse --git-common-dir` szülője) másol
    a megadott cél-worktree gyökerébe;
  - csak a **hiányzó** fájlokat másolja: ami a célban már létezik (mert a git
    kicsekkolta, vagy egy korábbi futás létrehozta), azt SOHA nem írja felül
    és nem törli — a script idempotens és nem-destruktív;
  - a forrásban **git által követett** fájlt sosem másolja: azt a worktree a
    SAJÁT branch-e szerint kapja meg, a fő ág verziójának bemásolása untracked
    szemetet hagyna a `git status`-ban (tipikusan a commitált `.github/`-nál);
  - a listán kívüli, de agentic-nek látszó gyökérmappákat felismeri (`skills/bs-*`,
    `agents/`, kapu-script), hogy egy új platform ne maradjon ki csendben;
  - a `__pycache__`, `.venv`, `node_modules` és a `*.pyc` kimarad.

Használat:
    worktree-setup.py <cél-worktree-mappa> [--extra <útvonal> ...] [--dry-run]

Kilépő kód: 0 = kész (akkor is, ha nem volt mit másolni),
            1 = a cél nem ugyanennek a repónak a worktree-je / másolási hiba,
            2 = használati hiba.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Az ismert agentic eszköz-mappák és -fájlok a projekt gyökerében. A lista a
# telepítő (install-helper.py) ÖSSZES célmappáját lefedi — a BerkiSpec mind az
# öt támogatott platformját:
#   claude      → .claude/{agents,skills,scripts}
#   antigravity → .agents/{agents,skills,scripts}
#   codex       → .codex/{agents,scripts} + .agents/skills
#   copilot     → .github/{agents,instructions,scripts}
#   cursor      → .cursor/{agents,skills,scripts}
# A telepítő a projekt GYÖKERÉBE semmit nem ír, a lenti gyökér-fájlok (CLAUDE.md,
# AGENTS.md, …) az eszközök saját konvenciói — kényelmi kiegészítés.
# Ha egy platform később új gyökérmappát kap, a `discover_agent_dirs()`
# felismerő ága akkor is átviszi (a lista nem záródik be csendben).
AGENT_PATHS = [
    ".claude",      # Claude Code
    ".agents",      # Antigravity + Codex (skillek)
    ".codex",       # Codex CLI
    ".cursor",      # Cursor
    ".github",      # Copilot (jellemzően commitálva — ilyenkor nincs teendő)
    ".gemini",      # Gemini CLI
    "CLAUDE.md",
    "AGENTS.md",
    "GEMINI.md",
    ".mcp.json",
]

SKIP_NAMES = {"__pycache__", ".venv", "venv", "node_modules", ".pytest_cache"}

# A felismerő ág ezeket a gyökérmappákat sosem nézi agentic eszköznek.
DISCOVER_IGNORE = {".git", ".idea", ".vscode", ".gradle", ".mvn", ".bs-brainstorm",
                   ".specs", ".husky"} | SKIP_NAMES

# Egy ismeretlen `.<név>` gyökérmappa akkor agentic eszköz-mappa, ha a BerkiSpec
# telepítő nyomát viseli: `skills/bs-*`, `agents/`, vagy egy kapu-script.
def looks_like_agent_dir(path):
    if (path / "skills").is_dir() and any((path / "skills").glob("bs-*")):
        return True
    if (path / "agents").is_dir():
        return True
    if (path / "scripts" / "analyze-gate-check.py").exists():
        return True
    return False


def discover_agent_dirs(source, known):
    """Ismeretlen, de agentic-nek látszó gyökérmappák — hogy egy később
    hozzáadott platform ne maradjon csendben kimásolatlanul."""
    found = []
    for entry in sorted(source.iterdir()):
        if not entry.is_dir() or not entry.name.startswith("."):
            continue
        if entry.name in DISCOVER_IGNORE or entry.name in known:
            continue
        if looks_like_agent_dir(entry):
            found.append(entry.name)
    return found


def die(msg, code=1):
    print(f"HIBA: {msg}", file=sys.stderr)
    sys.exit(code)


def git(*args, cwd=None):
    res = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0:
        return None
    return res.stdout.strip()


def main_worktree_root():
    """A FŐ worktree gyökere: a közös git-mappa (`.../<fő>/.git`) szülője."""
    common = git("rev-parse", "--path-format=absolute", "--git-common-dir")
    if not common:
        die("nem git repóban futunk (`git rev-parse` sikertelen).")
    return Path(common).parent.resolve()


def tracked_files(source):
    """A fő worktree-ben git által KÖVETETT fájlok halmaza (gyökérhez relatív).
    Ezeket nem szabad másolni: a worktree a SAJÁT branch-e szerinti változatot
    kapja, és a fő ág verziójának bemásolása untracked szemetet hagyna a
    `git status`-ban (tipikusan a `.github/` esetén)."""
    out = git("-C", str(source), "ls-files", "-z")
    if out is None:
        return set()
    return {p for p in out.split("\0") if p}


def copy_tree_missing_only(src, dst, dry_run, source_root, tracked):
    """Rekurzív másolás, kizárólag a célban HIÁNYZÓ és a forrásban NEM követett
    fájlokra. Visszaadja a másolt fájlok listáját (a célhoz képest relatív
    útvonallal)."""
    copied = []
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in SKIP_NAMES]
        rel_root = Path(root).relative_to(src)
        for name in files:
            if name.endswith(".pyc"):
                continue
            src_file = Path(root) / name
            if str(src_file.relative_to(source_root)) in tracked:
                continue
            dst_file = dst / rel_root / name
            if dst_file.exists():
                continue
            if not dry_run:
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dst_file)
                if os.access(src_file, os.X_OK):
                    os.chmod(dst_file, os.stat(src_file).st_mode)
            copied.append(str((rel_root / name)).lstrip("./"))
    return copied


def main():
    ap = argparse.ArgumentParser(
        description="Agentic eszköz-mappák pótlása egy friss git worktree-ben (PW4).")
    ap.add_argument("target", help="a cél-worktree gyökere (pl. ../projekt-c30)")
    ap.add_argument("--extra", action="append", default=[],
                    help="további, a gyökérhez képest relatív útvonal (többször megadható)")
    ap.add_argument("--dry-run", action="store_true",
                    help="csak jelentés, másolás nélkül")
    args = ap.parse_args()

    target = Path(args.target).resolve()
    if not target.is_dir():
        die(f"a cél mappa nem létezik: {target}", 2)

    source = main_worktree_root()
    if target == source:
        print("A cél a FŐ worktree — nincs teendő.")
        return 0

    # A cél tényleg ugyanennek a repónak a worktree-je?
    target_common = git("rev-parse", "--path-format=absolute", "--git-common-dir", cwd=target)
    if not target_common:
        die(f"a cél nem git worktree: {target}")
    if Path(target_common).resolve() != (source / ".git").resolve():
        die("a cél egy MÁSIK repó worktree-je — a másolás kihagyva.")

    tracked = tracked_files(source)

    discovered = discover_agent_dirs(source, set(AGENT_PATHS) | set(args.extra))
    if discovered:
        print(f"  ! felismert, listán kívüli eszköz-mappa: {', '.join(discovered)}")

    total = 0
    for rel in AGENT_PATHS + args.extra + discovered:
        src_path = source / rel
        dst_path = target / rel
        if not src_path.exists():
            continue
        if src_path.is_file():
            if rel in tracked:
                print(f"  = {rel} (git követi — a worktree a saját verzióját kapja)")
                continue
            if dst_path.exists():
                print(f"  = {rel} (már megvan)")
                continue
            if not args.dry_run:
                shutil.copy2(src_path, dst_path)
            print(f"  + {rel}")
            total += 1
            continue
        copied = copy_tree_missing_only(src_path, dst_path, args.dry_run, source, tracked)
        if copied:
            print(f"  + {rel}/ — {len(copied)} fájl")
            total += len(copied)
        else:
            print(f"  = {rel}/ (nincs pótolni való)")

    prefix = "[dry-run] " if args.dry_run else ""
    if total:
        print(f"{prefix}WORKTREE-SETUP: {total} fájl pótolva itt: {target}")
    else:
        print(f"{prefix}WORKTREE-SETUP: nem volt mit pótolni ({target}).")
    print("Megjegyzés: meglévő fájlt a script sem felül nem ír, sem nem töröl.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
