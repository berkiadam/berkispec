#!/usr/bin/env python3
"""Szabványosított értesítés a ciklusvég bukásairól (CS6 / L13-D11).

A keret a MECHANIZMUST rögzíti, a csatornát a projekt választja. A konfiguráció
a `conventions.md` `## Review and merge` szekciójában él (ANGOL literálok):

    - **Notification channel:** slack | teams | command | none
    - **Notification secret (env var):** BS_NOTIFY_WEBHOOK
    - **Notification command:** _(csak ha a csatorna `command`)_

Két beépített backend + egy menekülő út:

  slack / teams — webhook POST egy JSON-nel (gyakorlatilag ugyanaz)
  command       — szabad parancs (msmtp, sendmail, Jira, PagerDuty, céges script)
  none          — LEGITIM, KIMONDOTT válasz (egyszemélyes PoC), de nem az, ami
                  hallgatásból következik

E-mail backend SZÁNDÉKOSAN nincs: az SMTP öt további mezőt kérne (host, port,
user, from, to) és enterprise relay-korlátokba fut, miközben a `command` lefedi.

🔴 A TITOK KÖRNYEZETI VÁLTOZÓBAN ÉL, ÉS EZ A SCRIPT OLVASSA KI — soha nem
parancssori argumentumként. Az ágens shell-parancsokat futtat, és a parancs
SZÖVEGE bekerül a transzkriptbe, a `check-log.md`-be és a CI-naplóba: egy
`--webhook https://hooks.slack.com/...` hívás három helyre szivárogtatná ki a
teljes hozzáférést, és onnan nem szedhető vissza. Ezért:

  · a `conventions.md`-be csak az env var NEVE kerül;
  · a hibaüzenetek MASZKOLJÁK a titkot;
  · ha a csatorna be van állítva, de az env var hiányzik, a script BESZÉDES
    hibával áll meg (`exit 2`) — a néma értesítő rosszabb, mint a semmi: a
    fejlesztő azt hiszi, értesülne, ha baj lenne.

Kilépő kódok:
  0 — elküldve (vagy `--dry-run`, vagy a csatorna `none`)
  1 — a küldés megkísérelve, de bukott (hálózat, HTTP hiba, parancs exit != 0)
  2 — konfigurációs/használati hiba (ismeretlen csatorna, hiányzó env var,
      hiányzó `Notification command`)
"""

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

RM_SECTION = "review and merge"
_FIELD_RE = re.compile(r"^\s*-?\s*\*\*(?P<key>[^:*]+):\*\*\s*(?P<val>.*?)\s*$", re.MULTILINE)
KNOWN_CHANNELS = ("slack", "teams", "command", "none")


def read_review_and_merge(conventions_path):
    """A `## Review and merge` szekció mezői {kisbetűs kulcs: érték} alakban."""
    try:
        text = Path(conventions_path).read_text(encoding="utf-8")
    except OSError:
        return {}
    section = None
    for block in re.split(r"^##\s+", text, flags=re.MULTILINE)[1:]:
        head, _, body = block.partition("\n")
        if head.strip().lower() == RM_SECTION:
            section = body
            break
    if section is None:
        return {}
    out = {}
    for m in _FIELD_RE.finditer(section):
        val = m.group("val").strip().strip("`")
        if "|" in val:          # a sablon kitöltetlen sora (`slack | teams | …`)
            continue
        out[m.group("key").strip().lower()] = val
    return out


def mask(text, secret):
    """A titok minden előfordulását maszkolja a kimenetben."""
    if not secret or len(secret) < 8:
        return text
    return text.replace(secret, secret[:6] + "…<masked>")


def build_payload(channel, title, body, run_url):
    lines = [body] if body else []
    if run_url:
        lines.append(f"Test manager run: {run_url}")
    text = "\n".join([f"*{title}*"] + lines) if title else "\n".join(lines)
    if channel == "teams":
        # Microsoft Teams incoming webhook (MessageCard) — a legszélesebb körben
        # elfogadott alak; a Power Automate workflow-URL is elnyeli.
        return {"@type": "MessageCard", "@context": "https://schema.org/extensions",
                "summary": title or "berkispec", "title": title or "berkispec",
                "text": "\n\n".join(lines) or "-"}
    return {"text": text or "-"}


def send_webhook(url, payload, timeout=15):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, resp.read().decode("utf-8", "replace")[:200]


def main():
    parser = argparse.ArgumentParser(
        description="Értesítés a ciklusvég bukásairól (CS6/L13-D11).")
    parser.add_argument("--channel", choices=KNOWN_CHANNELS,
                        help="felülbírálja a conventions.md `Notification channel` mezőjét")
    parser.add_argument("--phase", default="",
                        help="melyik fázis szól (review / post-merge / dev-test)")
    parser.add_argument("--cycle", default="", help="a ciklus mappája")
    parser.add_argument("--status", default="fail", choices=["fail", "pass", "info"])
    parser.add_argument("--title", default="", help="az üzenet címe (alapból generált)")
    parser.add_argument("--body", default="", help="az üzenet törzse (alapból generált)")
    parser.add_argument("--run-url", default="",
                        help="a test manager futás-URL-je — így az értesítés KATTINTHATÓ "
                             "a bukott körre (TM10)")
    parser.add_argument("--conventions", default="conventions.md")
    parser.add_argument("--dry-run", action="store_true",
                        help="mindent ellenőriz és kiír, de NEM küld (a 00 próba-értesítése)")
    args = parser.parse_args()

    rm = read_review_and_merge(args.conventions)
    channel = (args.channel or rm.get("notification channel", "none")).strip().lower()
    if channel not in KNOWN_CHANNELS:
        print(f"HIBA: ismeretlen értesítési csatorna: {channel!r} — a megengedett értékek: "
              f"{', '.join(KNOWN_CHANNELS)} (conventions.md → `## Review and merge` → "
              f"`Notification channel`).", file=sys.stderr)
        return 2

    title = args.title or (f"berkispec — {args.phase or 'cycle'} {args.status.upper()}"
                           + (f" ({Path(args.cycle).name})" if args.cycle else ""))
    body = args.body or (
        f"Fázis: {args.phase or '—'}\nCiklus: {args.cycle or '—'}\nEredmény: {args.status}\n"
        f"A bizonyíték a ciklus mappájában van (test-report/), commitolva.")

    if channel == "none":
        print("Az értesítés ki van kapcsolva (`Notification channel: none`) — "
              "kimondott, legitim döntés, nem hallgatás.")
        return 0

    if channel == "command":
        command = rm.get("notification command", "").strip()
        if not command:
            print("HIBA: `Notification channel: command`, de a `Notification command` mező "
                  "üres (conventions.md → `## Review and merge`). A néma értesítő rosszabb, "
                  "mint a semmi — töltsd ki, vagy állítsd a csatornát `none`-ra.",
                  file=sys.stderr)
            return 2
        env = dict(os.environ)
        env.update({"BS_NOTIFY_TITLE": title, "BS_NOTIFY_BODY": body,
                    "BS_NOTIFY_PHASE": args.phase, "BS_NOTIFY_CYCLE": args.cycle,
                    "BS_NOTIFY_STATUS": args.status, "BS_NOTIFY_RUN_URL": args.run_url})
        print(f"Csatorna: command — {command}")
        if args.dry_run:
            print("DRY-RUN: a parancs nem futott le.")
            return 0
        try:
            proc = subprocess.run(command, shell=True, env=env, capture_output=True,
                                  text=True, timeout=120)
        except Exception as exc:                        # noqa: BLE001
            print(f"HIBA: az értesítő parancs nem futtatható: {exc}", file=sys.stderr)
            return 1
        out = (proc.stdout or "") + (proc.stderr or "")
        if proc.returncode != 0:
            print(f"HIBA: az értesítő parancs `exit {proc.returncode}` — {out.strip()[:300]}",
                  file=sys.stderr)
            return 1
        print("Az értesítés elküldve (command).")
        return 0

    # slack / teams — webhook POST
    env_name = rm.get("notification secret (env var)", "").strip()
    if not env_name:
        print(f"HIBA: a `Notification channel: {channel}` be van állítva, de a "
              f"`Notification secret (env var)` mező üres (conventions.md → "
              f"`## Review and merge`). A titok ÉRTÉKE soha nem kerül a fájlba — "
              f"csak a környezeti változó NEVE.", file=sys.stderr)
        return 2
    secret = os.environ.get(env_name, "")
    if not secret:
        print(f"HIBA: a(z) `{env_name}` környezeti változó nincs beállítva, pedig az "
              f"értesítési csatorna `{channel}`. A néma értesítő rosszabb, mint a semmi: "
              f"a fejlesztő azt hinné, értesülne, ha baj lenne. Lokálisan forrásold be a "
              f"gitignore-olt `.env`-et, CI-ben a titok-tár injektálja "
              f"(GitHub Actions secrets / GitLab CI variables / Jenkins credentials).",
              file=sys.stderr)
        return 2

    payload = build_payload(channel, title, body, args.run_url)
    print(f"Csatorna: {channel} — webhook a(z) `{env_name}` env varból "
          f"(az értéke nem kerül kiírásra).")
    if args.dry_run:
        print("DRY-RUN: a webhook nem lett meghívva. A payload:")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    try:
        status, body_text = send_webhook(secret, payload)
    except urllib.error.HTTPError as exc:
        print(f"HIBA: a webhook HTTP {exc.code} — "
              f"{mask(str(exc.reason), secret)}", file=sys.stderr)
        return 1
    except Exception as exc:                            # noqa: BLE001
        print(f"HIBA: a webhook hívása nem sikerült: {mask(str(exc), secret)}",
              file=sys.stderr)
        return 1
    if status >= 300:
        print(f"HIBA: a webhook HTTP {status} — {mask(body_text, secret)}", file=sys.stderr)
        return 1
    print(f"Az értesítés elküldve ({channel}, HTTP {status}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
