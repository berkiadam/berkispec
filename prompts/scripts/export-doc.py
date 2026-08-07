#!/usr/bin/env python3
"""Verziózott PDF export markdown doksikból (a /bs-export-doc skill futtató scriptje).

Bemenet nélkül a két kötelező generált doksiból készít PDF-et:
  docs-generated/architecture.md  →  export/architecture-v<N>.pdf
  docs-generated/system-overview.md → export/system-overview-v<N>.pdf

A verziószám fájlonként FÜGGETLEN: az `export/` mappában lévő `<név>-v<N>.pdf`
fájlok maximuma + 1, üres mappánál v1.

Mermaid ábrák: a `mermaid-filter` pandoc-filter rendereli (Chromiummal), így a
LaTeX/HTML motor már kész vektorgrafikát kap — a mermaid `foreignObject`
címkéi nem tűnnek el. A `MERMAID_FILTER_FORMAT` a motorhoz igazodik
(xelatex → pdf, pagedjs → svg).

Motorok:
  xelatex (default) — oldalszámozott TOC, tömör tördelés, nyomdai minőség
  pagedjs           — CSS-alapú formázás; könnyebb testreszabás, de lazább
                      tördelés és (a pagedjs-cli hibája miatt) hajlamos üres
                      oldalt beszúrni

A forrásfájlokat SOSEM módosítja: a build-mappába készít másolatot, arra teszi
rá a YAML fejlécet (title / subtitle / lang), és azt adja a pandocnak. A
`mermaid-filter` a cwd-be írja a `mermaid-filter.err`-t, ezért a pandoc a
build-mappában fut — így nem szemeteli a projekt gyökerét.

Kilépő kód: 0 = minden kért PDF elkészült, 1 = legalább egy hiba, 2 = használati
hiba vagy hiányzó függőség.
"""
import argparse
import datetime
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_SOURCES = [
    "docs-generated/architecture.md",
    "docs-generated/system-overview.md",
]

VERSION_RE_TEMPLATE = r"^{stem}-v(\d+)\.pdf$"
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
COVERAGE_RE = re.compile(r"\*\*Lefedve:\*\*\s*([^\s·|]+)")
YAML_FRONT_RE = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.DOTALL)
# A DS17 fejléc-blokk a fájl elején áll — csak eddig keresünk `Lefedve:` markert.
HEADER_SCAN_LINES = 10

# ── LaTeX header (a xelatex úthoz) ───────────────────────────────────────────
# Szándékosan a scriptbe ágyazva: a telepítő csak a `prompts/scripts/*.py`-t
# másolja a platform scripts-mappájába, a `prompts/templates/`-et nem — így a
# script önmagában teljes, és külön fájl nélkül is futtatható.
HEADER_TEX = r"""
\usepackage{xcolor}
\usepackage{titling}
\usepackage{xurl}
\usepackage{colortbl}
\usepackage[many]{tcolorbox}
\usepackage{etoolbox}
\usepackage{fvextra}
\usepackage{hyperref}
\usepackage[export]{adjustbox}

% Színek
\definecolor{codebg}{gray}{0.95}
\definecolor{framegray}{gray}{0.9}

% Cím stílus
\setlength{\droptitle}{-1.5cm}
\pretitle{\begin{center}\LARGE\bfseries}
\posttitle{\par\vskip 0.5em{\hrule}\end{center}}

% Linkek: kattinthatóak, de nyomtatásban is olvashatóak
\hypersetup{
  colorlinks=false,
  pdfborderstyle={/S/U/W 1},
  urlbordercolor=blue,
  linkbordercolor=blue
}

% Kódblokk: tördelés + speciális karakterek védelme (hosszú útvonalak!)
\fvset{breaklines=true, breakanywhere=true, commandchars=none}

% A pandoc Shaded/Highlighting környezete CSAK akkor létezik, ha a dokumentum
% tartalmaz kódblokkot. Guard nélkül a \renewenvironment „Environment Shaded
% undefined" hibával elbuktatná a kódblokk nélküli doksik exportját.
\makeatletter
\@ifundefined{Shaded}{}{%
  % Kiürítjük, hogy a tcolorbox-os dobozolással ne ütközzön.
  \renewenvironment{Shaded}{}{}%
}
\@ifundefined{Highlighting}{}{%
  % Kódblokkok dobozolása, oldalhatáron átvihetően.
  \BeforeBeginEnvironment{Highlighting}{%
    \begin{tcolorbox}[breakable, size=small, colback=codebg,
                      colframe=framegray, arc=0mm]}%
  \AfterEndEnvironment{Highlighting}{\end{tcolorbox}}%
}
\makeatother

% Széles ábrák leskálázása a szövegtükörre (a mermaid diagramok szélesek)
\let\origincludegraphics\includegraphics
\renewcommand{\includegraphics}[2][]{%
  \origincludegraphics[#1, max width=\linewidth, max height=0.85\textheight]{#2}}

\urlstyle{same}
"""

# ── CSS (a pagedjs úthoz) ────────────────────────────────────────────────────
# A pagedjs alapból nem tesz oldalszámot; a @page margin-box ezt pótolja.
PAGEDJS_CSS_TEMPLATE = """
@page {{
  size: {paper};
  margin: 2cm;
  @bottom-center {{ content: counter(page); font-size: 9pt; color: #555; }}
}}
body {{ font-family: "DejaVu Serif", serif; line-height: 1.45; }}
h1, h2, h3 {{ break-after: avoid; }}
pre, table, svg, img {{ break-inside: avoid; }}
pre {{ background: #f5f5f5; padding: .6em; overflow-wrap: break-word;
      white-space: pre-wrap; }}
img, svg {{ max-width: 100%; height: auto; }}
code {{ overflow-wrap: anywhere; }}
"""

PAPER_LATEX = {"a4": "a4paper", "a3": "a3paper"}
PAPER_CSS = {"a4": "A4", "a3": "A3"}


# ── Függőség-ellenőrzés ──────────────────────────────────────────────────────
def check_dependencies(engine):
    """(hiányzó tételek listája) — mindegyikhez a telepítő paranccsal."""
    missing = []
    if not shutil.which("pandoc"):
        missing.append(("pandoc", "sudo dnf install pandoc  # vagy: apt install pandoc"))
    if not shutil.which("mermaid-filter"):
        missing.append(("mermaid-filter", "npm install -g mermaid-filter"))
    if engine == "xelatex":
        if not shutil.which("xelatex"):
            missing.append(("xelatex", "sudo dnf install texlive-xetex texlive-collection-latexrecommended"))
        if shutil.which("kpsewhich"):
            for sty in ("tcolorbox", "fvextra", "adjustbox", "xurl", "titling"):
                r = subprocess.run(["kpsewhich", f"{sty}.sty"], capture_output=True, text=True)
                if not r.stdout.strip():
                    missing.append((f"LaTeX csomag: {sty}",
                                    f"sudo dnf install 'tex({sty}.sty)'"))
    else:
        if not shutil.which("pagedjs-cli"):
            missing.append(("pagedjs-cli", "npm install -g pagedjs-cli"))
    return missing


# ── Verziószám ───────────────────────────────────────────────────────────────
def next_version(export_dir, stem):
    """A meglévő `<stem>-v<N>.pdf` fájlok maximuma + 1 (üresnél 1)."""
    pattern = re.compile(VERSION_RE_TEMPLATE.format(stem=re.escape(stem)))
    versions = []
    if export_dir.is_dir():
        for p in export_dir.iterdir():
            m = pattern.match(p.name)
            if m:
                versions.append(int(m.group(1)))
    return (max(versions) + 1) if versions else 1


# ── YAML fejléc ──────────────────────────────────────────────────────────────
def prettify(stem):
    return stem.replace("-", " ").replace("_", " ").strip().capitalize()


def build_source_copy(src, build_dir, version, today):
    """A forrás másolata a build-mappában, YAML fejléccel. A forrást nem írjuk.

    Ha a forrásnak MÁR van YAML front mattere, azt tiszteletben tartjuk és nem
    injektálunk (a fájl szerzője tudatosan állította be)."""
    text = src.read_text(encoding="utf-8")
    dest = build_dir / src.name

    if YAML_FRONT_RE.match(text):
        dest.write_text(text, encoding="utf-8")
        return dest, None

    h1 = H1_RE.search(text)
    title = h1.group(1).strip() if h1 else prettify(src.stem)
    # A `Lefedve:` markert CSAK a fájl eleji fejléc-blokkban (DS17) keressük —
    # máskülönben egy lentebbi sablon-példa is beletalálna.
    cov = COVERAGE_RE.search("\n".join(text.splitlines()[:HEADER_SCAN_LINES]))
    subtitle = f"Lefedve: {cov.group(1)} · v{version}" if cov else f"v{version}"

    def esc(s):
        return s.replace('"', '\\"')

    front = (
        "---\n"
        f'title: "{esc(title)}"\n'
        f'subtitle: "{esc(subtitle)}"\n'
        f'date: "{today}"\n'
        'toc-title: "Tartalomjegyzék"\n'
        "lang: hu\n"
        "---\n\n"
    )
    dest.write_text(front + text, encoding="utf-8")
    return dest, subtitle


# ── Pandoc hívás ─────────────────────────────────────────────────────────────
def pandoc_cmd(engine, paper, src_copy, out_pdf, source_dir, build_dir):
    cmd = [
        "pandoc", src_copy.name,
        "-o", str(out_pdf.resolve()),
        "--filter", "mermaid-filter",
        "--toc", "--number-sections",
        "--highlight-style", "pygments",
        "--resource-path", f".{os.pathsep}{source_dir.resolve()}",
    ]
    if engine == "xelatex":
        cmd += [
            "--pdf-engine=xelatex",
            "--include-in-header=header.tex",
            "-V", f"geometry:{PAPER_LATEX[paper]}",
            "-V", "geometry:margin=2cm",
            "-V", "mainfont=DejaVu Serif",
            "--pdf-engine-opt=-interaction=nonstopmode",
        ]
    else:
        cmd += ["--pdf-engine=pagedjs-cli", "--css", "style.css"]
    return cmd


def tail(text, n=25):
    lines = [l for l in (text or "").splitlines() if l.strip()]
    return "\n".join(lines[-n:])


def export_one(src, export_dir, engine, paper, keep_build, dry_run, today):
    """Egy fájl exportja. Visszatérés: (ok, üzenet)."""
    if not src.exists():
        return False, f"nem létező forrásfájl: {src}"
    if src.suffix.lower() != ".md":
        return False, f"csak markdown fájl exportálható, ez nem: {src}"

    version = next_version(export_dir, src.stem)
    out_pdf = export_dir / f"{src.stem}-v{version}.pdf"

    if dry_run:
        return True, f"{src} → {out_pdf} (motor: {engine}, {paper}) [dry-run]"

    build_dir = export_dir / ".build" / src.stem
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)

    src_copy, subtitle = build_source_copy(src, build_dir, version, today)
    if engine == "xelatex":
        (build_dir / "header.tex").write_text(HEADER_TEX, encoding="utf-8")
    else:
        (build_dir / "style.css").write_text(
            PAGEDJS_CSS_TEMPLATE.format(paper=PAPER_CSS[paper]), encoding="utf-8")

    env = dict(os.environ)
    env["MERMAID_FILTER_FORMAT"] = "pdf" if engine == "xelatex" else "svg"
    # A puppeteer ne töltsön le még egy böngészőt, ha van rendszerszintű.
    if "PUPPETEER_EXECUTABLE_PATH" not in env:
        for browser in ("google-chrome", "chromium", "chromium-browser"):
            path = shutil.which(browser)
            if path:
                env["PUPPETEER_EXECUTABLE_PATH"] = path
                break

    cmd = pandoc_cmd(engine, paper, src_copy, out_pdf, src.parent, build_dir)
    proc = subprocess.run(cmd, cwd=build_dir, env=env,
                          capture_output=True, text=True)

    if proc.returncode != 0 or not out_pdf.exists():
        err = [f"a pandoc hibára futott ({src}), kilépő kód: {proc.returncode}"]
        if proc.stderr.strip():
            err.append("--- pandoc stderr ---\n" + tail(proc.stderr))
        mf_err = build_dir / "mermaid-filter.err"
        if mf_err.exists() and mf_err.stat().st_size:
            err.append("--- mermaid-filter.err ---\n" + tail(mf_err.read_text(errors="replace")))
        for log in build_dir.glob("*.log"):
            err.append(f"--- {log.name} ---\n" + tail(log.read_text(errors="replace")))
        err.append(f"A build-mappa megtartva a hibakereséshez: {build_dir}")
        return False, "\n".join(err)

    if not keep_build:
        shutil.rmtree(build_dir, ignore_errors=True)
        # Az üres `.build` szülőmappa se maradjon ott.
        try:
            build_dir.parent.rmdir()
        except OSError:
            pass  # más fájl exportja még használja, vagy nem üres

    size_kb = out_pdf.stat().st_size // 1024
    extra = f" · {subtitle}" if subtitle else ""
    return True, f"{out_pdf} ({size_kb} kB, motor: {engine}, {paper}){extra}"



def _force_utf8_output():
    """Windows-kompatibilitás: a konzol örökölt kódlapja (cp852 / cp1250 / cp1252)
    nem tudja megjeleníteni a kimenet tipográfiai és ékezetes karaktereit (—, →, ő, ű),
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
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("sources", nargs="*", metavar="FÁJL",
                        help="exportálandó markdown fájlok; üresen a két default "
                             "(docs-generated/architecture.md, system-overview.md)")
    parser.add_argument("--engine", choices=["xelatex", "pagedjs"], default="xelatex",
                        help="PDF motor (default: xelatex)")
    parser.add_argument("--paper", choices=["a4", "a3"], default="a4",
                        help="lapméret; széles diagramokhoz a3 (default: a4)")
    parser.add_argument("--export-dir", default="export", metavar="MAPPA",
                        help="kimeneti mappa (default: export)")
    parser.add_argument("--keep-build", action="store_true",
                        help="a build-mappa megtartása siker esetén is (hibakereséshez)")
    parser.add_argument("--dry-run", action="store_true",
                        help="csak kiírja, mit készítene, nem futtat pandocot")
    parser.add_argument("--check", action="store_true",
                        help="csak a függőségeket ellenőrzi, majd kilép")
    args = parser.parse_args()

    print("## PDF export\n")

    missing = check_dependencies(args.engine)
    if missing:
        print(f"**Hiányzó függőség** (motor: {args.engine}):\n")
        for name, hint in missing:
            print(f"- `{name}` — telepítés: `{hint}`")
        print("\nA mermaid ábrák renderelése nélkül nem készül olvasható PDF, "
              "ezért az export megáll.")
        return 2
    if args.check:
        print(f"- Minden függőség megvan (motor: {args.engine}). ✓")
        return 0

    sources = [Path(s) for s in (args.sources or DEFAULT_SOURCES)]
    # Duplikátumok kiszűrése a sorrend megtartásával.
    seen, uniq = set(), []
    for s in sources:
        key = s.resolve() if s.exists() else s
        if key not in seen:
            seen.add(key)
            uniq.append(s)
    sources = uniq

    if not args.sources:
        print(f"- Bemenet nem lett megadva → a két default doksi.\n")

    export_dir = Path(args.export_dir)
    if not args.dry_run:
        export_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.date.today().isoformat()
    ok_count, results = 0, []
    for src in sources:
        ok, msg = export_one(src, export_dir, args.engine, args.paper,
                             args.keep_build, args.dry_run, today)
        results.append((ok, msg))
        if ok:
            ok_count += 1

    for ok, msg in results:
        print(("- ✓ " if ok else "- ✗ ") + msg)

    print(f"\n## Összesítés: {ok_count}/{len(sources)} elkészült")
    return 0 if ok_count == len(sources) else 1


if __name__ == "__main__":
    sys.exit(main())
