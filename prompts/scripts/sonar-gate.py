#!/usr/bin/env python3
"""SonarQube Quality Gate kapu — az API-ból, nem a riportból (07-validate).

Miért kell: ma az orchestrátornak (vagy a test-runnernek) be kell olvasnia a
`sonar-report.md`/`.html`-t, és LLM-ben kell eldöntenie, hogy (a) átment-e a
Quality Gate, (b) van-e BLOCKER/CRITICAL/MAJOR finding, és (c) a kapu findingra
vagy küszöbre bukott-e (QG1 ág). Mindhárom kérdésre a Sonar Web API pontos,
gépi választ ad — a riport maradhat bizonyítéknak, de olvasni nem kell.

Két hívás:
  GET /api/qualitygates/project_status   → QG státusz + a BUKOTT feltételek
                                           (metrika, küszöb, tényleges érték)
  GET /api/issues/search                 → nyitott findingek súlyosság szerint

Kilépő kód — ez dönt, nem az LLM ítélete:
  0 = Quality Gate OK (a MINOR/INFO találatok nem blokkolnak)
  1 = QG FAIL **finding miatt** → van BLOCKER/CRITICAL/MAJOR; a kiírt lista
      lesz a `## Validációs javítások` javító-taskok forrása
  3 = QG FAIL **küszöb miatt, blokkoló finding NÉLKÜL** → ez a QG1 ág:
      TILOS üres hibalistával fixert indítani. A bukott feltétel (pl.
      `new_coverage 71.2% < 80%`) alapján vagy konkrét lefedettségi task
      készül, vagy STOP + humán (projekt-szintű küszöb).
  2 = használati hiba (hiányzó paraméter, elérhetetlen API, ismeretlen projekt)

Paraméterek: `--url`, `--project-key`, `--token`. Ha nincs megadva, a
`SONAR_HOST_URL` / `SONAR_PROJECT_KEY` / `SONAR_TOKEN` környezeti változókból
olvas, illetve megpróbálja a `conventions.md` `## Sonar minőségellenőrzés`
szekciójából és a `sonar-project.properties`-ből kiszedni.

A `--out <fájl>` megadásakor markdown összefoglalót is ír (a kör-mappába
`sonar-report.md` néven) — így a TR3 bizonyíték is megvan, LLM nélkül.
"""
import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from lang_keys import fld, sec

BLOCKING = ("BLOCKER", "CRITICAL", "MAJOR")
ALL_SEVERITIES = ("BLOCKER", "CRITICAL", "MAJOR", "MINOR", "INFO")


def api_get(base_url, path, params, token):
    url = f"{base_url.rstrip('/')}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url)
    if token:
        # A Sonar tokent user-névként, üres jelszóval is elfogadja (basic auth).
        raw = base64.b64encode(f"{token}:".encode()).decode()
        req.add_header("Authorization", f"Basic {raw}")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def from_conventions(path):
    """(url, project_key) best-effort a conventions.md Sonar szekciójából."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except Exception:
        return None, None
    m = re.search(r"^#+\s*Sonar.*$", text, re.MULTILINE | re.IGNORECASE)
    if not m:
        return None, None
    tail = text[m.end():]
    nxt = re.search(r"^#+\s", tail, re.MULTILINE)
    block = tail[: nxt.start()] if nxt else tail
    url = re.search(r"https?://[^\s`)>]+", block)
    key = re.search(r"(?:projectKey|project key|projekt kulcs)\s*[:=]\s*`?([\w.:\-]+)`?",
                    block, re.IGNORECASE)
    return (url.group(0) if url else None), (key.group(1) if key else None)


def from_properties(repo):
    p = Path(repo) / "sonar-project.properties"
    if not p.exists():
        return None, None
    text = p.read_text(encoding="utf-8", errors="replace")
    key = re.search(r"^sonar\.projectKey\s*=\s*(\S+)", text, re.MULTILINE)
    host = re.search(r"^sonar\.host\.url\s*=\s*(\S+)", text, re.MULTILINE)
    return (host.group(1) if host else None), (key.group(1) if key else None)


def fmt_condition(cond):
    metric = cond.get("metricKey", "?")
    actual = cond.get("actualValue", "?")
    op = {"GT": ">", "LT": "<"}.get(cond.get("comparator", ""), cond.get("comparator", ""))
    threshold = cond.get("errorThreshold", "?")
    return f"{metric}: {actual} (küszöb: {op} {threshold})"


def write_report(out_path, status, failed, counts, issues, project_key):
    lines = [f"# Sonar Quality Gate — {project_key}", "",
             f"**Quality Gate:** {status}", ""]
    if failed:
        lines += [f"## {sec('failed_conditions')}", ""]
        lines += [f"- {fmt_condition(c)}" for c in failed] + [""]
    lines += [f"## {sec('open_findings_by_sev')}", "",
              f"| {fld('f_severity')} | {fld('f_count')} |", "|---|---|"]
    lines += [f"| {sev} | {counts.get(sev, 0)} |" for sev in ALL_SEVERITIES]
    lines += [""]
    blocking = [i for i in issues if i.get("severity") in BLOCKING]
    if blocking:
        lines += [f"## {sec('blocking_findings')}", ""]
        for i in blocking:
            comp = i.get("component", "").split(":")[-1]
            line = i.get("line", "?")
            lines.append(f"- **{i.get('severity')}** — `{comp}:{line}` — "
                         f"{i.get('message', '')} _({i.get('rule', '')})_")
        lines += [""]
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))


def _force_utf8_output():
    """Windows-kompatibilitás: a konzol örökölt kódlapja (cp852 / cp1250 / cp1252)
    nem tudja megjeleníteni a kimenet tipográfiai és ékezetes karaktereit (✓, ✗, —, ő),
    és a `print()` ilyenkor `UnicodeEncodeError`-t dob. Ez azért veszélyes, mert a
    kivétel AZUTÁN keletkezne, hogy a szkript a fájlműveletet már elvégezte: a hívó
    ágens hibás kilépő kódot látna egy sikeres művelet után. Ezért a kimenetet
    UTF-8-ra kapcsoljuk, hibatűrő módban (Python 3.7+; régebbin csendben kimarad)."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

def main():
    _force_utf8_output()
    parser = argparse.ArgumentParser(description="Sonar Quality Gate determinisztikus kapu.")
    parser.add_argument("--url", default=os.environ.get("SONAR_HOST_URL"))
    parser.add_argument("--project-key", default=os.environ.get("SONAR_PROJECT_KEY"))
    parser.add_argument("--token", default=os.environ.get("SONAR_TOKEN"))
    parser.add_argument("--branch", default=None)
    parser.add_argument("--conventions", default="conventions.md")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--out", default=None, help="markdown összefoglaló ide (kör-mappa/sonar-report.md)")
    parser.add_argument("--max-issues", type=int, default=50)
    parser.add_argument("--fail-on", default=None,
                        help="vesszős súlyosság-lista (pl. BLOCKER vagy BLOCKER,CRITICAL): "
                             "ilyen nyitott finding esetén akkor is FAIL, ha a Quality Gate OK")
    args = parser.parse_args()

    url, key = args.url, args.project_key
    if not (url and key):
        c_url, c_key = from_conventions(args.conventions)
        p_url, p_key = from_properties(args.repo)
        url = url or c_url or p_url
        key = key or c_key or p_key
    if not url or not key:
        print("HIBA: hiányzik a Sonar URL vagy a projectKey. Add meg a --url / --project-key "
              "kapcsolóval, vagy a SONAR_HOST_URL / SONAR_PROJECT_KEY env-változóval.",
              file=sys.stderr)
        return 2

    params = {"projectKey": key}
    if args.branch:
        params["branch"] = args.branch
    try:
        qg = api_get(url, "/api/qualitygates/project_status", params, args.token)
    except urllib.error.HTTPError as e:
        print(f"HIBA: a Sonar API {e.code} választ adott ({e.reason}). "
              "Ellenőrizd a tokent és a projectKey-t.", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"HIBA: a Sonar API nem érhető el: {e}", file=sys.stderr)
        return 2

    status = qg.get("projectStatus", {}).get("status", "NONE")
    conditions = qg.get("projectStatus", {}).get("conditions", [])
    failed = [c for c in conditions if c.get("status") == "ERROR"]

    iparams = {"componentKeys": key, "resolved": "false", "ps": str(args.max_issues),
               "severities": ",".join(ALL_SEVERITIES)}
    if args.branch:
        iparams["branch"] = args.branch
    try:
        data = api_get(url, "/api/issues/search", iparams, args.token)
        issues = data.get("issues", [])
        facets_total = data.get("total", len(issues))
    except Exception as e:
        print(f"FIGYELEM: a findingek lekérése nem sikerült ({e}) — csak a QG státusz áll rendelkezésre.",
              file=sys.stderr)
        issues, facets_total = [], 0

    counts = {sev: sum(1 for i in issues if i.get("severity") == sev) for sev in ALL_SEVERITIES}
    blocking = [i for i in issues if i.get("severity") in BLOCKING]

    print(f"Sonar Quality Gate — {key}" + (f" (branch: {args.branch})" if args.branch else ""))
    print(f"  QG státusz: {status}")
    print("  Findingek: " + ", ".join(f"{s}={counts[s]}" for s in ALL_SEVERITIES)
          + (f" (összes nyitott: {facets_total})" if facets_total else ""))
    if failed:
        print("  Bukott feltételek:")
        for c in failed:
            print(f"    · {fmt_condition(c)}")
    if blocking:
        print("  Blokkoló findingek (javító-task jelöltek):")
        for i in blocking[:20]:
            comp = i.get("component", "").split(":")[-1]
            print(f"    · {i.get('severity')} — {comp}:{i.get('line', '?')} — {i.get('message', '')}")

    if args.out:
        write_report(args.out, status, failed, counts, issues, key)
        print(f"  Riport: {args.out}")

    if status == "OK":
        # A Quality Gate tipikusan CSAK az új kódot méri, ezért egy örökölt (vagy
        # baseline nélküli első elemzésből származó) BLOCKER mellett is OK lehet.
        # A --fail-on ezt a rést zárja be, ha a projekt így akarja.
        if args.fail_on:
            wanted = {s.strip().upper() for s in args.fail_on.split(",") if s.strip()}
            hits = [i for i in issues if i.get("severity") in wanted]
            if hits:
                print(f"VERDICT: FAIL-SEVERITY — a Quality Gate OK, de {len(hits)} nyitott "
                      f"{'/'.join(sorted(wanted))} finding van (--fail-on)")
                return 1
        print("VERDICT: PASS")
        return 0
    if blocking:
        print("VERDICT: FAIL-FINDING — a blokkoló findingek javító-taskként felvehetők")
        return 1
    print("VERDICT: FAIL-THRESHOLD (QG1) — a kaput küszöb buktatta, nem finding. "
          "TILOS üres hibalistával fixert indítani: vagy konkrét (pl. lefedettségi) task készül "
          "a bukott feltételre, vagy STOP + humán, ha a küszöb nem a ciklus hatókörében javítható.")
    return 3


if __name__ == "__main__":
    sys.exit(main())
