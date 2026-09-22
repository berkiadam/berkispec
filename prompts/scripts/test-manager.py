#!/usr/bin/env python3
"""Test manager integráció — FIX SZERZŐDÉS, cserélhető adapterrel (TM1–TM10).

A vendor-semlegességet NEM a szolgáltató-lista adja, hanem ez a szerződés:

    python3 test-manager.py --mode preflight|publish|selftest \
        --phase <implement|validate|post-merge|dev-test|ad-hoc> \
        --round-dir <a kör-mappa> [--category <kategória>] [--dry-run]

Bemenet: a kör-mappa, a `run-tests.py` `results.json`-ja (benne a futtatási
tábla `Eredményfájl`/`Formátum` cellájából másolt artefaktum és a futás
napló-vége), valamint a `conventions.md` `## <sec:cv_test_reporting>` hat
test manager mezője. **Új bemenetet nem vezetünk be**, és a plan futtatási
táblája nem kap új oszlopot.

Metaadat, amit minden adapter felküld: `cycle` · `phase` · `branch` · `commit` ·
`category` · `env`. Cikluson kívüli (`ad-hoc`) futásnál `cycle=none` — így a
`D8`/`KT6` bizonyíték-tűzfal a SZOLGÁLTATÓNÁL is látszik, és egy kényelmi futás
dashboard-linkje utólag sem téveszthető össze ciklus-bizonyítékkal.

Kimenet: a stdout UTOLSÓ sora gépiesen olvasható — `TEST_MANAGER_RUN_URL=<url>`.

Kilépő kódok:
  0 — feltöltve (vagy a preflight rendben)
  2 — konfigurációs/használati hiba (ismeretlen provider, hiányzó mező/env var)
  3 — KIHAGYVA (a fázis nincs a listán, vagy `Test manager: none`) — külön kód,
      nem `0`: a „nem volt bekapcsolva" és a „feltöltve" nem moshatók össze
  4 — a feltöltés lefutott, de bukott (hálózat, 401, 5xx) VAGY nem jelent meg
      futás-URL (L13-D26)

🔴 A FELTÖLTÉS NEM BIZONYÍTÉK (TM7). A ciklus egyetlen bizonyítéka a COMMITOLT
`test-report/<fázis>/` készlet; a futás-URL pointer, nem kapu-bemenet. A
`report-gate-check.py` egy URL-t tartalmazó, artefaktum nélküli riport-készletet
ugyanúgy elutasít, mint eddig.

🔴 A FELTÖLTÉS AKKOR ÉS CSAK AKKOR SZÁMÍT MEGTÖRTÉNTNEK, HA A FUTÁS-URL
MEGJELENT (L13-D26). A mérés (improve-list13 6.9) megmutatta: rossz tokennel a
Playwright `exit 0`-val, ZÖLDEN végez, miközben semmi nem töltődött fel — a
riporter csak kiír egy hibablokkot. A „zöld és feltöltve" tehát exit kódból nem
megkülönböztethető a „zöld és néma bukás"-tól.

🔴 A TITOK KIZÁRÓLAG ENV VARBAN. A regiszterben csak a NEVE áll, és ez a script
olvassa ki a környezetből — adapter SOHA nem kap tokent parancssorban (a parancs
szövege transzkriptbe, `check-log.md`-be és CI-naplóba kerül).
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from lang_keys import fld, sec

PHASES = ("implement", "validate", "post-merge", "dev-test", "ad-hoc")
PROVIDERS = ("none", "testdino", "reportportal", "qase", "command")
SHAPES = ("reporter", "import")

# Az adapterek KIPRÓBÁLTSÁGA — a dokumentációban és a kimenetben is kimondva
# (L13-D25): kipróbálatlan adaptert csendben beleírni nem szabad, mert a
# felhasználó éles PR-en tudná meg, hogy nem megy.
TRIED_OUT = {"testdino": True, "reportportal": False, "qase": False, "command": True}

# A `testdino` `reporter` ág felismerő-készlete (improve-list13 6.9 füstteszt)
TESTDINO_RUN_URL_RE = re.compile(r"https://app\.testdino\.com/\S+/test-runs/\S+")
TESTDINO_AUTH_FAIL = "Authentication failed"
TESTDINO_NO_TOKEN = "Token is required but not provided"
TESTDINO_DELIVERED = "run:end delivered"
TESTDINO_MIN_NODE = (22, 12)

# Általános URL-felismerés az `import` és a `command` ághoz
GENERIC_URL_RE = re.compile(r"https?://\S+")
RUN_URL_LINE_RE = re.compile(r"^TEST_MANAGER_RUN_URL=(\S*)\s*$", re.MULTILINE)

_FIELD_RE_TMPL = r"\*\*{}:\*\*\s*(?P<val>.*?)\s*$"


def read_reporting_section(conventions_path):
    """A `## <sec:cv_test_reporting>` szekció szövege (a következő `## ` fejlécig)."""
    try:
        text = Path(conventions_path).read_text(encoding="utf-8")
    except OSError:
        return ""
    want = sec("cv_test_reporting").strip().lower()
    for block in re.split(r"^##\s+", text, flags=re.MULTILINE)[1:]:
        head, _, body = block.partition("\n")
        if head.strip().lower() == want:
            return body
    return ""


def field(section_text, key):
    """Egy LOKALIZÁLT mezőnév értéke a szekcióból (`**Test manager:** testdino`)."""
    rx = re.compile(_FIELD_RE_TMPL.format(re.escape(fld(key))), re.MULTILINE)
    m = rx.search(section_text)
    if not m:
        return ""
    val = m.group("val").strip().strip("`")
    return "" if val in ("—", "-", "–", "n/a", "na") else val


def load_config(conventions_path):
    section = read_reporting_section(conventions_path)
    if not section:
        return {}
    return {
        "provider": (field(section, "f_test_manager") or "none").lower(),
        "shape": (field(section, "f_test_manager_shape") or "").lower(),
        "token_env": field(section, "f_test_manager_token_env"),
        "phases": [p.strip().lower() for p in
                   re.split(r"[,;/ ]+", field(section, "f_test_manager_phases")) if p.strip()],
        "required": (field(section, "f_test_manager_required") or "").lower()
                    in ("igen", "yes", "true"),
        "command": field(section, "f_test_manager_command"),
    }


def git(args):
    try:
        r = subprocess.run(["git"] + args, capture_output=True, text=True, timeout=5)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:                                   # noqa: BLE001
        return ""


def build_metadata(args, results):
    """A TM6 metaadat-készlete. `ad-hoc`-nál `cycle=none` (D8/KT6 a szolgáltatónál is)."""
    cycle = results.get("cycle") if isinstance(results, dict) else None
    if args.phase == "ad-hoc" or not cycle:
        cycle = "none"
    env_values = {e.get("kornyezet", "") for e in (results.get("results") or [])}
    env = "remote" if any(v and v.lower() not in
                          ("lokális", "lokalis", "local", "—", "-") for v in env_values) else "local"
    return {"cycle": cycle, "phase": args.phase, "branch": git(["rev-parse", "--abbrev-ref", "HEAD"]),
            "commit": git(["rev-parse", "--short", "HEAD"]),
            "category": args.category or "", "env": env}


def load_results(round_dir):
    path = Path(round_dir) / "results.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:                                   # noqa: BLE001
        return {}


def round_log_text(results, category=None):
    """A kör futtatási naplójának vége — ebből nyerjük ki a futás-URL-t (L13-D26)."""
    out = []
    for entry in results.get("results") or []:
        if category and entry.get("kategoria") != category:
            continue
        if entry.get("log_tail"):
            out.append(entry["log_tail"])
    return "\n".join(out)


def result_files(results, category=None):
    out = []
    for entry in results.get("results") or []:
        if category and entry.get("kategoria") != category:
            continue
        if entry.get("eredmeny"):
            out.append(entry["eredmeny"])
    return out


def node_version():
    try:
        r = subprocess.run(["node", "--version"], capture_output=True, text=True, timeout=10)
    except Exception:                                   # noqa: BLE001
        return None
    if r.returncode != 0:
        return None
    m = re.match(r"v(\d+)\.(\d+)", r.stdout.strip())
    return (int(m.group(1)), int(m.group(2))) if m else None


def record(round_dir, line, url=""):
    """A kimenet EGY SORA a kör riportjába és a `results.json`-ba (TM8).

    A `results.json` a gépi fogyasztóé (`cycle-status.py` → `TM10` pointer), a
    `test-manager.md` az emberé. Egyik sem bizonyíték — a bizonyíték a commitolt
    riport-készlet (TM7)."""
    rd = Path(round_dir)
    try:
        rd.mkdir(parents=True, exist_ok=True)
        (rd / "test-manager.md").write_text(line + "\n", encoding="utf-8")
    except OSError:
        pass
    path = rd / "results.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:                                   # noqa: BLE001
        return
    status = "uploaded" if line.startswith("test manager: uploaded") else (
        "skipped" if "skipped" in line else "FAILED")
    data["test_manager"] = {"status": status, "line": line, "url": url}
    try:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass


def emit(url=""):
    """A szerződés utolsó sora — MINDIG ez zárja a kimenetet."""
    print(f"TEST_MANAGER_RUN_URL={url}")


# ── adapterek ────────────────────────────────────────────────────────────────

def adapter_testdino(mode, cfg, args, results, meta):
    """`reporter` alak: a kliens a futtató reporter-láncában streamel futás közben.

    A keret NEM tölt fel — a `publish` a futás-URL-t nyeri ki a kör naplójából.
    A `preflight` viszont itt a FONTOSABB: token nélkül vagy rossz Node-on az
    egész e2e kör kárba vész."""
    token_env = cfg.get("token_env") or "TESTDINO_TOKEN"
    if mode in ("preflight", "selftest"):
        problems = []
        if not os.environ.get(token_env):
            problems.append(f"a(z) `{token_env}` env var nincs beállítva — a riporter "
                            f"hibablokkot ír, a tesztek lefutnak `exit 0`-val, és SEMMI "
                            f"nem töltődik fel (néma bukás)")
        nv = node_version()
        if nv is None:
            problems.append("a `node` nem elérhető — a `reporter` alakú kliens a teszt-futtató "
                            "folyamatában él, tehát Node nélkül nem tud betöltődni")
        elif nv < TESTDINO_MIN_NODE:
            problems.append(f"Node {nv[0]}.{nv[1]} — a `@testdino/playwright` "
                            f"**Node ≥ {TESTDINO_MIN_NODE[0]}.{TESTDINO_MIN_NODE[1]}**-t kér "
                            f"(CommonJS csomag ESM `chalk` függőséggel): régebbi Node-on a "
                            f"riporter be sem töltődik, és ezzel AZ EGÉSZ TESZT-FUTÁST MEGÖLI "
                            f"— nulla lefutott teszttel")
        if problems:
            for p in problems:
                print(f"  ✗ {p}", file=sys.stderr)
            return 2
        print(f"  ✓ preflight rendben: `{token_env}` beállítva, Node {nv[0]}.{nv[1]} "
              f"(≥ {TESTDINO_MIN_NODE[0]}.{TESTDINO_MIN_NODE[1]})")
        return 0

    # publish — a futás-URL kinyerése a kör naplójából (L13-D26)
    log = round_log_text(results, args.category)
    if TESTDINO_NO_TOKEN in log or TESTDINO_AUTH_FAIL in log:
        reason = ("hiányzó token" if TESTDINO_NO_TOKEN in log else "hitelesítési hiba")
        record(args.round_dir, f"test manager: FAILED ({reason} — a futás zöld lehetett, "
                               f"de semmi nem töltődött fel)")
        print(f"  ✗ a riporter {reason}-t jelzett a kör naplójában", file=sys.stderr)
        return 4
    urls = TESTDINO_RUN_URL_RE.findall(log)
    if not urls:
        record(args.round_dir, "test manager: FAILED (nincs futás-URL a kimeneten)")
        print("  ✗ nincs futás-URL a kör naplójában — a feltöltés NEM tekinthető "
              "megtörténtnek (L13-D26). A futtató exit kódja erre nem bizonyíték.",
              file=sys.stderr)
        return 4
    url = urls[-1].rstrip(".,)")
    delivered = TESTDINO_DELIVERED in log
    record(args.round_dir, f"test manager: uploaded {url}"
                           + ("" if delivered else " (a `run:end delivered` visszaigazolás "
                                                   "nem látszik a naplóban)"), url)
    print(f"  ✓ futás-URL: {url}" + ("  ·  run:end delivered" if delivered else ""))
    return 0


def adapter_import(provider, mode, cfg, args, results, meta):
    """`import` alak: a kész artefaktumot egy parancs UTÓLAG tolja fel.

    ⚠ A `reportportal` és a `qase` ág a végrehajtáskor KIPRÓBÁLATLAN volt (nem
    volt hozzájuk fiók) — ezt a script kimondja, nem hallgatja el (L13-D25).
    Kipróbálatlan adapter helyett a `command` ág a becsületes válasz."""
    token_env = cfg.get("token_env")
    if mode in ("preflight", "selftest"):
        if not token_env:
            print(f"  ✗ a(z) `{fld('f_test_manager_token_env')}` mező üres — a `{provider}` "
                  f"adapter token nélkül nem tud feltölteni", file=sys.stderr)
            return 2
        if not os.environ.get(token_env):
            print(f"  ✗ a(z) `{token_env}` env var nincs beállítva", file=sys.stderr)
            return 2
        if not TRIED_OUT.get(provider, False):
            print(f"  ⚠ a `{provider}` adapter KIPRÓBÁLATLAN (nem volt hozzá fiók a "
                  f"megvalósításkor) — éles használat előtt próbáld ki, vagy használd a "
                  f"`command` ágat a szolgáltató saját CLI-jével")
        print(f"  ✓ preflight rendben: `{token_env}` beállítva")
        return 0

    files = result_files(results, args.category)
    if not files:
        record(args.round_dir, "test manager: FAILED (nincs feltölthető eredményfájl a körben)")
        print("  ✗ a kör `results.json`-jában egyetlen kategóriának sincs `Eredményfájl`-ja — "
              "az `import` alak enélkül nem tud mit feltölteni (a futtatási tábla "
              "`Eredményfájl`/`Formátum` cellája hiányzik?)", file=sys.stderr)
        return 4
    print(f"  · {provider} ({provider in TRIED_OUT and 'import' or 'import'} alak) — "
          f"{len(files)} eredményfájl: {', '.join(files)}")
    if not TRIED_OUT.get(provider, False):
        print(f"  ⚠ a `{provider}` adapter KIPRÓBÁLATLAN — a feltöltő hívást a szolgáltató "
              f"aktuális CLI-jével kell validálni. Amíg ez nem történt meg, a `command` ág "
              f"a becsületes választás.")
    if args.dry_run:
        print("  · DRY-RUN: nem tölt fel.")
        emit_url = ""
        return 0
    # A tényleges feltöltés a szolgáltató CLI-jével megy, a `command` ág
    # mechanikájával — külön bedrótozott REST-hívás helyett, mert a CLI-k
    # gyorsan változnak, és egy elavult végpont némán rossz eredményt adna.
    command = cfg.get("command")
    if not command:
        record(args.round_dir, f"test manager: FAILED (a `{provider}` adapterhez nincs "
                               f"feltöltő parancs)")
        print(f"  ✗ a `{provider}` adapter feltöltő parancsa nincs megadva. Írd a "
              f"`{fld('f_test_manager_command')}` mezőbe a szolgáltató CLI-hívását "
              f"(a metaadatokat env varban kapja meg), vagy válts a `command` providerre.",
              file=sys.stderr)
        return 2
    return run_command_adapter(command, cfg, args, meta, files)


def run_command_adapter(command, cfg, args, meta, files):
    """A menekülő út: szó szerinti parancs, a TM6 metaadataival env varban.

    Ezzel TestRail, Xray, Allure TestOps, Currents vagy bármi más beköthető
    A KERET MÓDOSÍTÁSA NÉLKÜL — ugyanaz a minta, mint a `ci-run-skill.sh`
    `command` ágánál és a `notify.py`-nál."""
    env = dict(os.environ)
    env.update({f"BS_TM_{k.upper()}": str(v) for k, v in meta.items()})
    env["BS_TM_RESULT_FILES"] = os.pathsep.join(files)
    env["BS_TM_ROUND_DIR"] = str(args.round_dir)
    print(f"  · parancs: {command}")
    if args.dry_run:
        print("  · DRY-RUN: a parancs nem futott le.")
        return 0
    try:
        proc = subprocess.run(command, shell=True, env=env, capture_output=True,
                              text=True, timeout=600)
    except Exception as exc:                            # noqa: BLE001
        record(args.round_dir, f"test manager: FAILED (a parancs nem futtatható: {exc})")
        print(f"  ✗ a feltöltő parancs nem futtatható: {exc}", file=sys.stderr)
        return 4
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    if proc.returncode != 0:
        record(args.round_dir, f"test manager: FAILED (a feltöltő parancs exit "
                               f"{proc.returncode})")
        print(f"  ✗ a feltöltő parancs `exit {proc.returncode}`: {out.strip()[-400:]}",
              file=sys.stderr)
        return 4
    m = RUN_URL_LINE_RE.search(out)
    url = m.group(1) if m else ""
    if not url:
        urls = GENERIC_URL_RE.findall(out.strip().splitlines()[-1] if out.strip() else "")
        url = urls[-1].rstrip(".,)") if urls else ""
    if not url:
        record(args.round_dir, "test manager: FAILED (nincs futás-URL a kimeneten)")
        print("  ✗ a parancs lefutott, de nem adott futás-URL-t — a feltöltés NEM "
              "tekinthető megtörténtnek (L13-D26). A parancs utolsó sora legyen "
              "`TEST_MANAGER_RUN_URL=<url>`.", file=sys.stderr)
        return 4
    record(args.round_dir, f"test manager: uploaded {url}", url)
    print(f"  ✓ futás-URL: {url}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Test manager integráció fix szerződéssel (TM6).")
    parser.add_argument("--mode", required=True, choices=["preflight", "publish", "selftest"])
    parser.add_argument("--phase", default="ad-hoc", choices=list(PHASES))
    parser.add_argument("--round-dir", default="",
                        help="a kör-mappa (a `run-tests.py --round-dir`-jével AZONOS)")
    parser.add_argument("--category", default="", help="csak ez a teszt-kategória")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--conventions", default="conventions.md")
    args = parser.parse_args()

    cfg = load_config(args.conventions)
    if not cfg:
        print(f"HIBA: a `{args.conventions}` `## {sec('cv_test_reporting')}` szekciója nem "
              f"olvasható — a test manager konfigurációja ott él (TM3).", file=sys.stderr)
        emit()
        return 2
    provider = cfg["provider"]
    if provider not in PROVIDERS:
        print(f"HIBA: ismeretlen test manager provider: {provider!r} — a megengedett "
              f"értékek: {', '.join(PROVIDERS)}.", file=sys.stderr)
        emit()
        return 2

    print(f"test-manager.py — mód: {args.mode} · fázis: {args.phase} · provider: {provider}")

    if provider == "none":
        print("  · a test manager ki van kapcsolva (`none`) — nulla új lépés, nulla "
              "hálózati függés (TM1).")
        if args.mode == "publish":
            record(args.round_dir, "test manager: skipped (provider: none)")
        emit()
        return 3

    if args.mode != "selftest" and args.phase not in cfg["phases"]:
        print(f"  · a `{args.phase}` fázis nincs a `{fld('f_test_manager_phases')}` "
              f"listáján ({', '.join(cfg['phases']) or '—'}) — kihagyva.")
        if args.mode == "publish":
            record(args.round_dir, f"test manager: skipped ({args.phase} nincs a listán)")
        emit()
        return 3

    if args.mode == "publish" and not args.round_dir:
        print("HIBA: a `--publish` módhoz kötelező a `--round-dir` (a kör `results.json`-ja "
              "a bemenet).", file=sys.stderr)
        emit()
        return 2

    results = load_results(args.round_dir) if args.round_dir else {}
    meta = build_metadata(args, results)
    print(f"  · metaadat: " + " · ".join(f"{k}={v or '—'}" for k, v in meta.items()))

    if cfg["shape"] and cfg["shape"] not in SHAPES:
        print(f"HIBA: ismeretlen `{fld('f_test_manager_shape')}`: {cfg['shape']!r} — "
              f"a két alak: {', '.join(SHAPES)}.", file=sys.stderr)
        emit()
        return 2

    if provider == "testdino":
        code = adapter_testdino(args.mode, cfg, args, results, meta)
    elif provider in ("reportportal", "qase"):
        code = adapter_import(provider, args.mode, cfg, args, results, meta)
    elif provider == "command":
        command = cfg.get("command")
        if not command:
            print(f"HIBA: `{fld('f_test_manager')}: command`, de a "
                  f"`{fld('f_test_manager_command')}` mező üres.", file=sys.stderr)
            emit()
            return 2
        if args.mode in ("preflight", "selftest"):
            token_env = cfg.get("token_env")
            if token_env and not os.environ.get(token_env):
                print(f"  ✗ a(z) `{token_env}` env var nincs beállítva", file=sys.stderr)
                emit()
                return 2
            exe = command.split()[0] if command.split() else ""
            if exe and not shutil.which(exe) and not Path(exe).exists():
                print(f"  ✗ a parancs első eleme (`{exe}`) nem található a PATH-on — a "
                      f"`command` ág enélkül némán bukna", file=sys.stderr)
                emit()
                return 2
            print("  ✓ preflight rendben (parancs elérhető, env var beállítva)")
            code = 0
        else:
            code = run_command_adapter(command, cfg, args, meta,
                                       result_files(results, args.category))
    else:                                               # pragma: no cover
        code = 2

    # A futás-URL CSAK sikeres `publish`-ból származhat: egy korábbi kör URL-jét
    # visszaadni ugyanaz a hiba lenne, mint a feltöltést a hiány hiányából
    # következtetni (L13-D26).
    url = ""
    if args.mode == "publish" and code == 0 and args.round_dir:
        data = load_results(args.round_dir)
        url = (data.get("test_manager") or {}).get("url", "") if isinstance(data, dict) else ""
    if code == 4 and not cfg["required"]:
        print("  · a feltöltés bukott, de a `"
              + fld("f_test_manager_required") + "` mező nem `igen`: a fázis ettől "
              "NEM bukik (L13-D24). A bizonyíték a commitolt riport-készlet.")
    emit(url)
    return code


if __name__ == "__main__":
    sys.exit(main())
