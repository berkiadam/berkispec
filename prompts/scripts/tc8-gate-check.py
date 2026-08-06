#!/usr/bin/env python3
"""TC8 kapu — determinisztikus, LLM-ítélet nélküli ellenőrzések a
`specs/test-conventions.md` regiszterre (08-doc-sync fázis).

A DS22 magkapu a `docs-generated/` mappára fut; a `test-conventions.md` azon
KÍVÜL él (a `specs/roadmap.md` mellett), ezért saját kapuja van. Kilenc check:

  1. Útvonal-létezés (TC8/1)  — a fájlban megnevezett repo-belső útvonalak
     (tesztfájl, script, compose fájl, komponens-mappa) tényleg léteznek-e.
  2. Lógó hivatkozás (TC8/2)  — a 2./3. szekció minden tétele létező 1.
     szekciós receptre (R-ID) hivatkozik-e, és van-e egyáltalán hivatkozása.
  3. Titok-check (TC8/3)      — nem került-e be TC5 szerint tiltott
     credential (klaszter/registry/VPN/IAM/token).
  4. `Utolsó futás` marker (TC4) — minden tételnek van-e markere, és melyik
     avult el (staleness → kérdés a `doc-sync-questions.md`-be).
  5. Kötelező riport-sor (TC9/TR3) — a 2. és 3. szekció elején ott van-e a
     `**Kötelező riport (TR3):**` sor (a ciklus `test-report/` mappájába kerülő
     riport-artefaktum + forrás-hivatkozás a `conventions.md`-re).
  6. Futtatható koordináták (TC11) — van-e minden receptnek `Indítás` mezője,
     van-e `Példa hívás` a végpontot érintőknek, és a 3. szekció környezeti
     előfeltételei hivatkoznak-e receptre (különben nem derül ki, HOGYAN).
  7. Önhordó tételek (TC10) — a 2./3. szekció leírásai nem hivatkozhatnak
     spec-szekció sorszámra vagy ciklusra: a regiszter magában is érthető.
  8. Tétel-részletezés (TC10/b) — a 2./3. szekció minden táblázat-tételéhez
     tartozik-e `### <ID>` részletező blokk (Cél / Lépések / Elvárt eredmény):
     a táblázatsor index, a blokk maga a reprodukálható teszteset.
  9. Koordináta-blokk (TC13) — a fájl elején ott van-e a `## 0. Koordináták`
     blokk (környezetek/végpontok, teszt-userek/kliensek, paraméterek), és
     van-e benne kitöltött — nem placeholder — adatsor.

FAIL (blokkoló) vs WARN (informatív, az ágensnek/embernek szól): a script csak
ott ad FAIL-t, ahol a jel egyértelmű. Bizonytalan esetben WARN — egy hamis
blokkolás rosszabb, mint egy emberi ránézés.

Kilépő kód: 0 = minden kemény check PASS (WARN megengedett),
            1 = legalább egy FAIL,
            2 = használati hiba.
A nem létező `test-conventions.md` NEM hiba (TC6: korai ciklusban a fájl
jogosan nincs meg) — ilyenkor a script 0-val, „kihagyva" jelzéssel tér vissza.
"""
import argparse
import re
import sys
from pathlib import Path

# ── Szekció-felismerés ────────────────────────────────────────────────────────
SECTION_RE = re.compile(r"^##\s*(\d)\.")
RECIPE_HEADING_RE = re.compile(r"^###\s*(R\d+)\b")
RECIPE_REF_RE = re.compile(r"\bR\d+\b")
LAST_RUN_RE = re.compile(r"Utolsó futás:\s*\**\s*(cycle-\d+)", re.IGNORECASE)
CYCLE_NUM_RE = re.compile(r"cycle-(\d+)")

# Backtick-idézett tokenek — csak ezekből keresünk útvonalat (a szabad szöveg
# nem ad megbízható jelet).
BACKTICK_RE = re.compile(r"`([^`\n]+)`")

# Ismert fájl-kiterjesztések, amelyeknél a token akkor is útvonal-jelölt, ha
# nincs benne `/` (pl. gyökérben lévő `docker-compose.e2e.yml`).
PATH_EXT_RE = re.compile(
    r"\.(py|sh|bash|ps1|ts|tsx|js|mjs|cjs|json|ya?ml|toml|ini|env|sql|md|"
    r"spec\.ts|test\.ts|feature|http|avsc|conf|cfg|properties|xml|gradle|"
    r"dockerfile|tf)$",
    re.IGNORECASE,
)
HOSTNAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*(\.[a-z0-9][a-z0-9-]*)+$", re.IGNORECASE)

# ── TC5 titok-minták ─────────────────────────────────────────────────────────
# STRONG: önmagában bizonyíték (FAIL).
STRONG_SECRET_PATTERNS = [
    ("GitHub PAT", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{16,}")),
    ("GitLab PAT", re.compile(r"\bglpat-[A-Za-z0-9_-]{16,}")),
    ("AWS access key", re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{12,}")),
    ("privát kulcs blokk", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("JWT literál", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.")),
    ("oc/kubectl login jelszóval",
     re.compile(r"\b(oc|kubectl)\s+login\b[^\n]*(--password|-p)\s*[=\s]\S", re.IGNORECASE)),
    ("registry login jelszóval",
     re.compile(r"\b(docker|podman|helm|skopeo)\s+(login|registry\s+login)\b[^\n]*"
                r"(--password(?!-stdin)|-p)\s*[=\s]\S", re.IGNORECASE)),
]

# WEAK: kockázatos platform-szó ÉS credential-szó egy sorban (WARN).
WEAK_PLATFORM_RE = re.compile(
    r"\b(openshift|\boc\b|kubectl|kubeconfig|cluster|klaszter|nexus|artifactory|"
    r"registry|harbor|quay|vpn|vault|aws|azure|gcp|gcloud|iam|"
    r"service[- ]account|jenkins|argo|bitbucket|gitlab|github)\b",
    re.IGNORECASE,
)
WEAK_CRED_RE = re.compile(
    r"\b(password|passwd|jelszó|secret|token|credential|api[- ]?key|apikey|"
    r"private[- ]key|access[- ]key)\b",
    re.IGNORECASE,
)
# Pointer-jelzés: a sor kimondja, hogy nem az érték van itt (TC5 pointer-forma).
POINTER_HINT_RE = re.compile(
    r"\b(pointer|szerezhető|nem itt|nincs itt|külön kezelt|vault-ban|"
    r"vaultban|jelszókezelő|nem kerül be)\b",
    re.IGNORECASE,
)


def split_sections(lines):
    """Sorindex -> szekciószám (0/1/2/3) leképezés. A fejléc előtti rész: None."""
    section_of = [None] * len(lines)
    current = None
    for i, line in enumerate(lines):
        m = SECTION_RE.match(line)
        if m:
            current = int(m.group(1))
        section_of[i] = current
    return section_of


def in_fence(lines):
    """Sorindex -> kódblokkban van-e (a fence-nyitó/záró sor is True)."""
    flags = [False] * len(lines)
    fence = None
    for i, line in enumerate(lines):
        m = re.match(r"^\s{0,3}(`{3,})(.*)$", line)
        if m:
            ticks, rest = m.group(1), m.group(2).strip()
            if fence is None:
                fence = len(ticks)
                flags[i] = True
                continue
            if len(ticks) >= fence and rest == "":
                fence = None
                flags[i] = True
                continue
        flags[i] = fence is not None
    return flags


# ── 1. Útvonal-létezés ───────────────────────────────────────────────────────
def path_candidates(lines):
    """Backtick-tokenekből útvonal-jelöltek kiszedése (sorszámmal)."""
    out = []
    for lineno, line in enumerate(lines, 1):
        for token in BACKTICK_RE.findall(line):
            tok = token.strip()
            if not tok or len(tok) > 200:
                continue
            if any(ch in tok for ch in " \t<>*|$\"'"):
                continue
            if "://" in tok or tok.startswith(("-", "@", "#")):
                continue
            # `/` kezdet + nincs kiterjesztés → HTTP endpoint (pl. `/health/ready`),
            # nem repo-útvonal. A repo-belső hivatkozás mindig relatív.
            if tok.startswith("/") and not PATH_EXT_RE.search(tok):
                continue
            has_slash = "/" in tok.strip("/")
            if not (has_slash or PATH_EXT_RE.search(tok)):
                continue
            first = tok.strip("/").split("/")[0]
            # Registry image-ref (`host/repo:tag`) és hostname-kezdet kizárása.
            if ":" in tok.rsplit("/", 1)[-1]:
                continue
            if has_slash and HOSTNAME_RE.match(first) and "." in first:
                continue
            out.append((lineno, tok.strip()))
    return out


def check_paths(lines, project_root):
    """Létezés-ellenőrzés. FAIL csak akkor, ha a jelölt első szegmense létező
    mappa (tehát repo-belső útvonal, de a cél eltűnt) — egyébként WARN."""
    results = []
    seen = set()
    for lineno, tok in path_candidates(lines):
        if tok in seen:
            continue
        seen.add(tok)
        target = project_root / tok
        if target.exists():
            results.append({"path": tok, "line": lineno, "status": "PASS"})
            continue
        first = tok.strip("/").split("/")[0]
        anchored = "/" in tok.strip("/") and (project_root / first).is_dir()
        results.append({
            "path": tok,
            "line": lineno,
            "status": "FAIL" if anchored else "WARN",
        })
    return results


# ── 2. Lógó hivatkozás ──────────────────────────────────────────────────────
def is_table_data_row(line):
    s = line.strip()
    if not (s.startswith("|") and s.count("|") >= 3):
        return False
    cells = [c.strip() for c in s.strip("|").split("|")]
    if not cells:
        return False
    # Fejléc-elválasztó (|---|---|) és fejléc-sor kiszűrése a hívó dönti el.
    if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
        return False
    return True


def check_dangling_refs(lines, section_of, fenced):
    defined = set()
    for i, line in enumerate(lines):
        if fenced[i] or section_of[i] != 1:
            continue
        m = RECIPE_HEADING_RE.match(line)
        if m:
            defined.add(m.group(1))

    rows = []
    for i, line in enumerate(lines):
        if fenced[i] or section_of[i] not in (2, 3):
            continue
        if not is_table_data_row(line):
            continue
        refs = set(RECIPE_REF_RE.findall(line))
        # Fejléc-sor: nincs benne R-ID és tipikusan szöveges — ezt a
        # "nincs hivatkozás" ág külön kezeli, de a táblázat fejlécét
        # (első sora a szekcióban, ami nem tartalmaz cycle-markert sem)
        # nem tekintjük adat-sornak.
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        looks_like_header = not refs and not LAST_RUN_RE.search(line) and \
            not CYCLE_NUM_RE.search(line) and \
            any(c.lower() in ("id", "mit ellenőriz", "recept", "utolsó futás",
                              "előfeltétel") for c in cells)
        if looks_like_header:
            continue
        rows.append({
            "line": i + 1,
            "section": section_of[i],
            "refs": sorted(refs),
            "text": line.strip()[:90],
        })

    findings = []
    for row in rows:
        if not row["refs"]:
            findings.append({**row, "status": "FAIL", "reason": "nincs recept-hivatkozás (R-ID)"})
            continue
        missing = [r for r in row["refs"] if r not in defined]
        if missing:
            findings.append({**row, "status": "FAIL",
                             "reason": f"nem definiált recept: {', '.join(missing)}"})
        else:
            findings.append({**row, "status": "PASS", "reason": ""})

    unused = sorted(defined - {r for row in rows for r in row["refs"]})
    return {"defined": sorted(defined), "rows": findings, "unused_recipes": unused}


# ── 3. Titok-check ──────────────────────────────────────────────────────────
def check_secrets(lines):
    findings = []
    for lineno, line in enumerate(lines, 1):
        strong_hit = False
        for label, pattern in STRONG_SECRET_PATTERNS:
            if pattern.search(line):
                findings.append({"line": lineno, "status": "FAIL", "label": label,
                                 "text": line.strip()[:120]})
                strong_hit = True
        # Ha a soron már van biztos találat, a heurisztikus WARN csak zaj.
        if strong_hit or POINTER_HINT_RE.search(line):
            continue
        if WEAK_PLATFORM_RE.search(line) and WEAK_CRED_RE.search(line):
            findings.append({"line": lineno, "status": "WARN",
                             "label": "platform-szó + credential-szó egy sorban",
                             "text": line.strip()[:120]})
    return findings


# ── 4. Utolsó futás marker ──────────────────────────────────────────────────
def check_last_run(lines, section_of, fenced, marker, stale_after):
    """Minden R-recept és 2./3. szekciós adat-sor kap-e `Utolsó futás` markert,
    és melyik avult el. Hiányzó marker: FAIL. Elavult: WARN (kérdés-trigger)."""
    current = None
    if marker:
        m = CYCLE_NUM_RE.search(marker)
        current = int(m.group(1)) if m else None

    items = []
    # Receptek: a heading utáni blokkban keressük a markert a következő
    # `###`/`##` fejlécig.
    recipe_start = None
    recipe_id = None
    for i, line in enumerate(lines + [""]):
        at_end = i == len(lines)
        starts_new = at_end or (not fenced[i] and re.match(r"^#{2,3}\s", line))
        if recipe_start is not None and starts_new:
            block = lines[recipe_start:i]
            found = None
            for bl in block:
                m = LAST_RUN_RE.search(bl)
                if m:
                    found = m.group(1)
                    break
            items.append({"kind": "recept", "id": recipe_id,
                          "line": recipe_start + 1, "marker": found})
            recipe_start, recipe_id = None, None
        if at_end:
            break
        if not fenced[i] and section_of[i] == 1:
            m = RECIPE_HEADING_RE.match(line)
            if m:
                recipe_id, recipe_start = m.group(1), i

    for i, line in enumerate(lines):
        if fenced[i] or section_of[i] not in (2, 3):
            continue
        if not is_table_data_row(line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if any(c.lower() in ("id", "mit ellenőriz", "recept", "utolsó futás",
                             "előfeltétel") for c in cells):
            continue
        m = CYCLE_NUM_RE.search(line)
        items.append({"kind": f"{section_of[i]}. szekció tétel",
                      "id": cells[0] if cells else "?",
                      "line": i + 1,
                      "marker": m.group(0) if m else None})

    results = []
    for it in items:
        if it["marker"] is None:
            results.append({**it, "status": "FAIL", "age": None})
            continue
        age = None
        if current is not None:
            m = CYCLE_NUM_RE.search(it["marker"])
            if m:
                age = current - int(m.group(1))
        if age is not None and stale_after is not None and age >= stale_after:
            results.append({**it, "status": "WARN", "age": age})
        else:
            results.append({**it, "status": "PASS", "age": age})
    return results


# ── 5. Kötelező riport-sor (TC9 / TR3) ──────────────────────────────────────
REPORT_LINE_RE = re.compile(r"\*\*Kötelező riport\s*\(TR3\):\*\*\s*(.*)$", re.IGNORECASE)
# Parancs-gyanús jelek a riport-sorban (a parancs a conventions.md dolga, TC1).
COMMAND_HINT_RE = re.compile(
    r"\b(npm|npx|yarn|pnpm|pytest|python3?|go|mvn|gradle|allure|playwright|"
    r"podman|docker|make|bash|sh)\b\s+\S", re.IGNORECASE)


def check_report_line(lines, section_of, fenced):
    """A 2. és 3. szekcióban ott van-e a `**Kötelező riport (TR3):**` sor.
    Hiány: FAIL. Parancsnak tűnő tartalom: WARN (duplikáció a conventions.md-vel)."""
    results = []
    for section in (2, 3):
        if not any(s == section for s in section_of):
            continue  # a szekció nem létezik — a szerkezeti figyelmeztetés máshol szól
        found = None
        for i, line in enumerate(lines):
            if fenced[i] or section_of[i] != section:
                continue
            m = REPORT_LINE_RE.search(line)
            if m:
                found = (i + 1, m.group(1).strip())
                break
        if found is None:
            results.append({"section": section, "status": "FAIL", "line": None, "value": None})
            continue
        line_no, value = found
        status = "WARN" if COMMAND_HINT_RE.search(value) else "PASS"
        results.append({"section": section, "status": status, "line": line_no, "value": value})
    return results


# ── 6. Futtatható koordináták (TC11) ────────────────────────────────────────
START_FIELD_RE = re.compile(r"\*\*Indítás:?\*\*", re.IGNORECASE)
CALL_FIELD_RE = re.compile(r"\*\*Példa hívás:?\*\*", re.IGNORECASE)
# Végpont-jel: a recept HTTP/CLI hívást érint → a példa hívás kötelező.
ENDPOINT_HINT_RE = re.compile(r"https?://|\bcurl\b|\bendpoint\b|\bREST\b|\bgRPC\b|\.http\b",
                              re.IGNORECASE)


def recipe_blocks(lines, section_of, fenced):
    """[(R-ID, kezdő sorindex, blokk sorai), ...] az 1. szekcióból."""
    blocks, start, rid = [], None, None
    for i, line in enumerate(lines + [""]):
        at_end = i == len(lines)
        new_heading = at_end or (not fenced[i] and re.match(r"^#{2,3}\s", line))
        if start is not None and new_heading:
            blocks.append((rid, start + 1, lines[start:i]))
            start, rid = None, None
        if at_end:
            break
        if not fenced[i] and section_of[i] == 1:
            m = RECIPE_HEADING_RE.match(line)
            if m:
                rid, start = m.group(1), i
    return blocks


def check_runnable(lines, section_of, fenced):
    """Minden receptnek van-e `Indítás` mezője, és — ha végpontot érint —
    `Példa hívás` blokkja (TC11)."""
    results = []
    for rid, lineno, block in recipe_blocks(lines, section_of, fenced):
        text = "\n".join(block)
        problems = []
        if not START_FIELD_RE.search(text):
            problems.append("hiányzik az `**Indítás:**` mező (ha nem kell környezet, "
                            "írd ki: `N/A — nem igényel futó környezetet`)")
        if ENDPOINT_HINT_RE.search(text) and not CALL_FIELD_RE.search(text):
            problems.append("végpontot érint, de nincs `**Példa hívás:**` blokkja "
                            "(teljes URL + header + payload + várt válasz)")
        results.append({"id": rid, "line": lineno,
                        "status": "FAIL" if problems else "PASS",
                        "problems": problems})
    return results


# ── 7. Önhordó tételek (TC10) ───────────────────────────────────────────────
# Spec-szekció sorszám a leírás elején: "1.2. ...", "2.3 ..."
SPEC_NUMBERING_RE = re.compile(r"^\d+\.\d+\.?\s")
CYCLE_REF_RE = re.compile(r"\bcycle[- ]?\d+\b", re.IGNORECASE)


def check_self_contained(lines, section_of, fenced):
    """A 2./3. szekció „Mit ellenőriz" cellája nem hivatkozhat spec-számozásra
    vagy ciklusra (TC10) — az ilyen leírás önmagában értelmezhetetlen."""
    results = []
    for i, line in enumerate(lines):
        if fenced[i] or section_of[i] not in (2, 3):
            continue
        if not is_table_data_row(line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        if any(c.lower() in ("id", "mit ellenőriz", "recept", "utolsó futás",
                             "előfeltétel", "bizonyíték") for c in cells):
            continue
        desc = cells[1]
        problems = []
        if SPEC_NUMBERING_RE.match(desc):
            problems.append("spec-szekció sorszámmal kezdődik (a másik dokumentum "
                            "számozása itt értelmezhetetlen)")
        if CYCLE_REF_RE.search(desc):
            problems.append("ciklusra hivatkozik a leírásban (a ciklus az `Utolsó futás` / "
                            "`Bizonyíték` oszlopba tartozik)")
        if problems:
            results.append({"line": i + 1, "section": section_of[i],
                            "id": cells[0], "desc": desc, "problems": problems})
    return results


# ── 8. Lógó előfeltétel (TC11) ──────────────────────────────────────────────
# „…fut”, „…aktív”, „…indítva” típusú előfeltétel R-ID hivatkozás nélkül.
PRECOND_ENV_RE = re.compile(r"\b(fut|futnia|aktív|indítva|elindítva|elérhető|feláll)\b",
                            re.IGNORECASE)


def check_dangling_preconditions(lines, section_of, fenced):
    """A 3. szekció `Előfeltétel` cellája környezeti feltételt említ, de nem
    hivatkozik receptre → nem derül ki, HOGYAN teljesítem (TC11)."""
    results = []
    for i, line in enumerate(lines):
        if fenced[i] or section_of[i] != 3:
            continue
        if not is_table_data_row(line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        if any(c.lower() in ("id", "mit ellenőriz", "recept", "utolsó futás",
                             "előfeltétel", "bizonyíték") for c in cells):
            continue
        precond = cells[3]
        if not precond or precond in ("-", "–", "—"):
            continue
        if PRECOND_ENV_RE.search(precond) and not RECIPE_REF_RE.search(precond):
            results.append({"line": i + 1, "id": cells[0], "text": precond})
    return results


# ── 9. Tétel-részletezés (TC10/b) ───────────────────────────────────────────
ITEM_HEADING_RE = re.compile(r"^###\s*([LI]\d+)\b")
ITEM_ID_RE = re.compile(r"^[LI]\d+$")
DETAIL_FIELDS = (
    ("Cél", re.compile(r"\*\*Cél:?\*\*", re.IGNORECASE)),
    ("Lépések", re.compile(r"\*\*Lépések:?\*\*", re.IGNORECASE)),
    ("Elvárt eredmény", re.compile(r"\*\*Elvárt eredmény:?\*\*", re.IGNORECASE)),
)


def check_item_details(lines, section_of, fenced):
    """Minden 2./3. szekciós táblázat-tételhez tartozik-e `### <ID>` részletező
    blokk, és megvannak-e benne a kötelező mezők (TC10/b)."""
    # Táblázat-tételek összegyűjtése
    row_ids = []
    for i, line in enumerate(lines):
        if fenced[i] or section_of[i] not in (2, 3):
            continue
        if not is_table_data_row(line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or not ITEM_ID_RE.match(cells[0]):
            continue
        row_ids.append((cells[0], section_of[i], i + 1))

    # Részletező blokkok összegyűjtése
    blocks = {}
    current, start = None, None
    for i, line in enumerate(lines + [""]):
        at_end = i == len(lines)
        new_heading = at_end or (not fenced[i] and re.match(r"^#{2,3}\s", line))
        if current is not None and new_heading:
            blocks[current] = (start + 1, "\n".join(lines[start:i]))
            current, start = None, None
        if at_end:
            break
        if not fenced[i]:
            m = ITEM_HEADING_RE.match(line)
            if m:
                current, start = m.group(1), i

    results = []
    for item_id, section, lineno in row_ids:
        if item_id not in blocks:
            results.append({"id": item_id, "section": section, "line": lineno,
                            "status": "FAIL",
                            "reason": "nincs `### %s — …` részletező blokk (a táblázatsor "
                                      "önmagában nem teszteset)" % item_id})
            continue
        bl_line, text = blocks[item_id]
        missing = [name for name, rx in DETAIL_FIELDS if not rx.search(text)]
        if missing:
            results.append({"id": item_id, "section": section, "line": bl_line,
                            "status": "FAIL",
                            "reason": "a részletező blokkból hiányzik: %s" % ", ".join(missing)})
        else:
            results.append({"id": item_id, "section": section, "line": bl_line,
                            "status": "PASS", "reason": ""})
    orphans = [b for b in blocks if b not in {r[0] for r in row_ids}]
    return results, orphans


# ── 10. Koordináta-blokk (TC13) ─────────────────────────────────────────────
# Placeholder-jel: kitöltetlen sablonsor (`<komponens>`, `<user>`, `PORT`).
PLACEHOLDER_RE = re.compile(r"<[^>]+>|\bPORT\b|\bVÁLTOZÓ\b|\bPARAMÉTER\b")


def check_coordinates(lines, section_of, fenced):
    """A `## 0. Koordináták` blokk létezik-e, a fájl ELEJÉN áll-e, és van-e
    benne legalább egy KITÖLTÖTT (nem placeholder) adatsor (TC13)."""
    zero_idx = None
    first_numbered = None
    for i, line in enumerate(lines):
        if fenced[i]:
            continue
        m = SECTION_RE.match(line)
        if not m:
            continue
        num = int(m.group(1))
        if num == 0 and zero_idx is None:
            zero_idx = i
        if num >= 1 and first_numbered is None:
            first_numbered = i
    if zero_idx is None:
        return {"status": "FAIL", "reason": "nincs `## 0. Koordináták` blokk a fájlban"}
    if first_numbered is not None and zero_idx > first_numbered:
        return {"status": "FAIL",
                "reason": f"a `## 0. Koordináták` blokk nem a fájl elején áll "
                          f"(sor {zero_idx + 1}, az `## 1.` szekció már a sor "
                          f"{first_numbered + 1}-nél kezdődik)"}
    filled, placeholders = 0, 0
    for i, line in enumerate(lines):
        if fenced[i] or section_of[i] != 0:
            continue
        if not is_table_data_row(line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if any(c.lower() in ("környezet", "komponens", "url / port", "health endpoint",
                             "név / azonosító", "titok", "scope / szerep", "név",
                             "érték / pointer", "hol használjuk") for c in cells):
            continue
        if PLACEHOLDER_RE.search(line):
            placeholders += 1
        else:
            filled += 1
    if filled == 0:
        return {"status": "FAIL",
                "reason": f"a `## 0. Koordináták` blokkban nincs kitöltött adatsor "
                          f"({placeholders} placeholder-sor) — a sablon önmagában nem koordináta"}
    return {"status": "PASS", "filled": filled, "placeholders": placeholders}


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("test_conventions", nargs="?", default="specs/test-conventions.md",
                        help="a test-conventions.md útvonala (default: specs/test-conventions.md)")
    parser.add_argument("--project-root", default=".", metavar="ÚTVONAL",
                        help="a projekt gyökere az útvonal-létezés ellenőrzéséhez (default: .)")
    parser.add_argument("--marker", default=None, metavar="cycle-NN",
                        help="az aktuális ciklus (az `Utolsó futás` staleness-számításhoz)")
    parser.add_argument("--stale-after", type=int, default=3, metavar="N",
                        help="ennyi vagy több ciklus eltérésnél a tétel elavult (default: 3)")
    args = parser.parse_args()

    tc_path = Path(args.test_conventions)
    project_root = Path(args.project_root)
    if not project_root.is_dir():
        print(f"HIBA: nem létező projekt-gyökér: {project_root}", file=sys.stderr)
        return 2

    print("## TC8 kapu — test-conventions.md ellenőrzés\n")

    if not tc_path.exists():
        print(f"- A `{tc_path}` nem létezik — **kihagyva** (TC6: korai ciklusban ez nem hiba, "
              "üres vázat nem hozunk létre).\n")
        print("## Összesített státusz: PASS (kihagyva)")
        return 0

    text = tc_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    section_of = split_sections(lines)
    fenced = in_fence(lines)

    if not any(s == 1 for s in section_of):
        print("- **FIGYELEM:** nem találtam `## 1.` … `## 3.` szekció-fejlécet — "
              "a szerkezet nem felel meg a TC2 sablonnak, a 2./4. check nem értelmezhető.\n")

    overall_pass = True
    warn_count = 0

    # 1.
    print("### 1. Útvonal-létezés (TC8/1)")
    path_results = check_paths(lines, project_root)
    if not path_results:
        print("- Nincs útvonal-jelölt a fájlban.")
    for r in path_results:
        if r["status"] == "PASS":
            continue
        if r["status"] == "FAIL":
            overall_pass = False
            print(f"- **FAIL** `{r['path']}` (sor {r['line']}) — a szülő-mappa létezik, "
                  "a cél nem: elavult tétel (TC4 → törlés vagy javítás)")
        else:
            warn_count += 1
            print(f"- WARN `{r['path']}` (sor {r['line']}) — nem oldható fel repo-belső "
                  "útvonalként (lehet külső hivatkozás vagy törölt komponens); nézd meg kézzel")
    ok_paths = sum(1 for r in path_results if r["status"] == "PASS")
    print(f"- Létező útvonal: {ok_paths}/{len(path_results)}\n")

    # 2.
    print("### 2. Lógó hivatkozás (TC8/2)")
    ref = check_dangling_refs(lines, section_of, fenced)
    print(f"- Definiált receptek (1. szekció): {', '.join(ref['defined']) or 'nincs'}")
    bad_rows = [r for r in ref["rows"] if r["status"] == "FAIL"]
    for r in bad_rows:
        overall_pass = False
        print(f"- **FAIL** {r['section']}. szekció, sor {r['line']} — {r['reason']}: "
              f"`{r['text']}`")
    if not bad_rows:
        print(f"- Minden tétel létező receptre hivatkozik ({len(ref['rows'])} tétel).")
    if ref["unused_recipes"]:
        warn_count += 1
        print(f"- WARN — a 2./3. szekció egyik tétele sem hivatkozik rá: "
              f"{', '.join(ref['unused_recipes'])} (fölösleges recept? vagy hiányzó tétel?)")
    print()

    # 3.
    print("### 3. Titok-check (TC8/3 — TC5 szabály)")
    secret_findings = check_secrets(lines)
    if not secret_findings:
        print("- Nem találtam tiltott credential-mintát.")
    for f in secret_findings:
        if f["status"] == "FAIL":
            overall_pass = False
            print(f"- **FAIL** sor {f['line']} — {f['label']}: `{f['text']}`")
        else:
            warn_count += 1
            print(f"- WARN sor {f['line']} — {f['label']}: `{f['text']}` "
                  "→ dev-hatókörű érték maradhat, osztott platform credential NEM (pointer!)")
    print()

    # 4.
    print("### 4. `Utolsó futás` marker (TC4)")
    if args.marker is None:
        print(f"- Nincs `--marker` — csak a marker LÉTÉT ellenőrzöm, staleness-t nem.")
    lr = check_last_run(lines, section_of, fenced, args.marker, args.stale_after)
    if not lr:
        print("- Nincs értelmezhető tétel.")
    for r in lr:
        if r["status"] == "FAIL":
            overall_pass = False
            print(f"- **FAIL** {r['kind']} `{r['id']}` (sor {r['line']}) — "
                  "hiányzik az `Utolsó futás: cycle-NN` marker")
        elif r["status"] == "WARN":
            warn_count += 1
            print(f"- WARN {r['kind']} `{r['id']}` (sor {r['line']}) — utoljára "
                  f"`{r['marker']}`-ben futott ({r['age']} ciklussal ezelőtt) → "
                  "kérdés a `doc-sync-questions.md`-be: még érvényes, vagy törlendő?")
    ok_markers = sum(1 for r in lr if r["status"] == "PASS")
    print(f"- Friss marker: {ok_markers}/{len(lr)}\n")

    # 5.
    print("### 5. Kötelező riport-sor (TC9 / TR3)")
    for r in check_report_line(lines, section_of, fenced):
        if r["status"] == "FAIL":
            overall_pass = False
            print(f"- **FAIL** {r['section']}. szekció — hiányzik a "
                  "`**Kötelező riport (TR3):**` sor. A ciklus `test-report/` mappájába "
                  "kerülő riport-artefaktum nevét és a `conventions.md → ## Teszt-riportolás` "
                  "forrás-hivatkozást kell tartalmaznia (TC9).")
        elif r["status"] == "WARN":
            warn_count += 1
            print(f"- WARN {r['section']}. szekció (sor {r['line']}) — a riport-sor "
                  "parancsnak tűnő részt tartalmaz; a generáló parancs a `conventions.md` "
                  "dolga, itt csak az artefaktum-név + forrás-hivatkozás álljon (TC1).")
        else:
            print(f"- PASS {r['section']}. szekció (sor {r['line']}) — `{r['value']}`")
    print()

    # 6.
    print("### 6. Futtatható koordináták (TC11)")
    run_results = check_runnable(lines, section_of, fenced)
    if not run_results:
        print("- Nincs recept az 1. szekcióban.")
    for r in run_results:
        if r["status"] == "FAIL":
            overall_pass = False
            for prob in r["problems"]:
                print(f"- **FAIL** `{r['id']}` (sor {r['line']}) — {prob}")
    ok_recipes = sum(1 for r in run_results if r["status"] == "PASS")
    if run_results:
        print(f"- Futtatható recept: {ok_recipes}/{len(run_results)}")
    dangling = check_dangling_preconditions(lines, section_of, fenced)
    for d in dangling:
        overall_pass = False
        print(f"- **FAIL** 3. szekció `{d['id']}` (sor {d['line']}) — az előfeltétel "
              f"(`{d['text']}`) környezeti állapotot vár, de nem hivatkozik receptre: "
              "nem derül ki, HOGYAN kell felhúzni. Hivatkozz `R-ID`-re, vagy vegyél fel "
              "új receptet az indítással (TC11).")
    if not dangling:
        print("- Minden környezeti előfeltétel receptre hivatkozik.")
    print()

    # 7.
    print("### 7. Önhordó tételek (TC10)")
    sc = check_self_contained(lines, section_of, fenced)
    if not sc:
        print("- Minden tétel-leírás önhordó (nincs spec-számozás / ciklus-hivatkozás).")
    for r in sc:
        overall_pass = False
        print(f"- **FAIL** {r['section']}. szekció `{r['id']}` (sor {r['line']}) — "
              f"„{r['desc']}” — {'; '.join(r['problems'])}. Írd át viselkedés-szintre: "
              "milyen bemenetre mi a helyes kimenet.")
    print()

    print("### 8. Tétel-részletezés (TC10/b)")
    details, orphans = check_item_details(lines, section_of, fenced)
    if not details:
        print("- Nincs tétel a 2./3. szekcióban.")
    for r in details:
        if r["status"] == "FAIL":
            overall_pass = False
            print(f"- **FAIL** {r['section']}. szekció `{r['id']}` (sor {r['line']}) — "
                  f"{r['reason']}. A promótált teszt reprodukálható leírása kötelező: "
                  "Cél / Előfeltétel / Lépések / Elvárt eredmény (TC10/b).")
    ok_details = sum(1 for r in details if r["status"] == "PASS")
    if details:
        print(f"- Részletezett tétel: {ok_details}/{len(details)}")
    for o in sorted(orphans):
        warn_count += 1
        print(f"- WARN `{o}` — van részletező blokk, de nincs hozzá táblázatsor "
              "(törölt tétel maradéka? vagy hiányzó sor?)")
    print()

    print("### 9. Koordináta-blokk (TC13)")
    coord = check_coordinates(lines, section_of, fenced)
    if coord["status"] == "FAIL":
        overall_pass = False
        print(f"- **FAIL** — {coord['reason']}. A `## 0. Koordináták` blokk kötelező: "
              "környezetek+végpontok, teszt-userek/kliensek/titkok, paraméterek+env-fájlok "
              "táblái, a fájl elején (TC13).")
    else:
        extra = f", {coord['placeholders']} kitöltetlen sablonsor" if coord["placeholders"] else ""
        print(f"- PASS — {coord['filled']} kitöltött koordináta-sor{extra}.")
    print()

    print(f"## Összesített státusz: {'PASS' if overall_pass else 'FAIL'}"
          f" ({warn_count} WARN — a WARN nem blokkol, de nézd át)")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
