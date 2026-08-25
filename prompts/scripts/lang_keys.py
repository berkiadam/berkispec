#!/usr/bin/env python3
"""Közös nyelvi kulcs-betöltő a kapu-scripteknek (LG18 / 10.5).

A projekt nyelve **telepítéskor dőlt el** (LG2/LG17), ezért itt nincs
`conventions.md`-olvasás és nincs kötelező CLI-flag. A telepítő
(`install-helper.py` → `copy_helper_scripts`) a scriptek mellé kiírja a
választott projekt-nyelv szeletét `lang-keys.json` néven:

    {"lang": "hu", "sections": {...}, "fields": {...}, "status": {...}}

Feloldási sorrend:

1. `Path(__file__).parent / "lang-keys.json"` — a telepített eset.
2. `Path(__file__).parent.parent / "lang" / "status-keys.json"` `hu` szelete —
   a repóban futtatott eset (`prompts/scripts/` mellett ott a `prompts/lang/`).
3. Egyik sem → egyszeri figyelmeztetés a stderr-re, és a kulcs-lekérdezés
   beszédes hibával áll meg (csendben rossz nyelven illeszteni rosszabb lenne).

Használat:

    from lang_keys import sec, fld, st
    section_text(plan_text, sec("planned_changes"))
"""

import json
import sys
from pathlib import Path

_CACHE = None
_WARNED = False

_HERE = Path(__file__).resolve().parent
_INSTALLED = _HERE / "lang-keys.json"
_REPO_FALLBACK = _HERE.parent / "lang" / "status-keys.json"


def load_keys(project_lang=None):
    """A nyelvi kulcs-szeletet adja vissza; cache-elve.

    `project_lang` csak fejlesztéshez/teszthez való opcionális felülbírálás —
    ilyenkor a repó `status-keys.json`-jából olvasunk, és nem cache-elünk."""
    global _CACHE, _WARNED

    if project_lang:
        raw = json.loads(_REPO_FALLBACK.read_text(encoding="utf-8"))
        if project_lang not in raw:
            raise SystemExit(f"lang_keys: ismeretlen nyelv: {project_lang}")
        return dict(raw[project_lang], lang=project_lang)

    if _CACHE is not None:
        return _CACHE

    if _INSTALLED.is_file():
        _CACHE = json.loads(_INSTALLED.read_text(encoding="utf-8"))
    elif _REPO_FALLBACK.is_file():
        raw = json.loads(_REPO_FALLBACK.read_text(encoding="utf-8"))
        _CACHE = dict(raw["hu"], lang="hu")
    else:
        if not _WARNED:
            print(
                "⚠️  lang_keys: nincs `lang-keys.json` a scriptek mellett — "
                "telepítsd újra a projektet (install.sh / install.ps1).",
                file=sys.stderr,
            )
            _WARNED = True
        _CACHE = {"lang": None, "sections": {}, "fields": {}, "status": {}}

    return _CACHE


def lang():
    """A telepített projekt-nyelv kódja (`hu` / `en`), vagy `None`."""
    return load_keys().get("lang")


def _get(group, key):
    keys = load_keys()
    try:
        return keys[group][key]
    except KeyError:
        raise SystemExit(
            f"lang_keys: ismeretlen kulcs: {group}:{key} "
            f"(nyelv: {keys.get('lang')}) — a `lang-keys.json` elavult, telepíts újra."
        )


def sec(key):
    """Artefaktum-szekció fejlécének szövege (a `##` prefix NÉLKÜL)."""
    return _get("sections", key)


def fld(key):
    """Artefaktum-mezőnév (a `**…:**` keret NÉLKÜL)."""
    return _get("fields", key)


def st(key):
    """Státusz-érték vagy egyéb rögzített szókészlet-elem."""
    return _get("status", key)
