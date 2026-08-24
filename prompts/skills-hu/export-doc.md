---
name: bs-export-doc
description: "berkispec - segédparancs. Verziózott PDF-et készít markdown doksikból (mermaid ábrákkal együtt) a projekt gyökerében lévő 'export/' mappába. Paraméter nélkül a 'docs-generated/architecture.md' és 'system-overview.md' fájlokból, egyébként a megnevezett fájl(ok)ból. A verziószám fájlonként független: az utolsó + 1, v1-től."
output:
  - "export/<név>-v<N>.pdf (fájlonként független verziószámmal)"
---
# Export doc — verziózott PDF a markdown doksikból

Ez **nem fázis**, hanem segédparancs: bármikor futtatható, nincs előfeltétele és nem változtat a ciklus állapotán. A tényleges munkát az `export-doc.py` script végzi — a te dolgod eldönteni, **miből** készüljön PDF, majd a scriptet meghívni és az eredményt visszajelezni.

---

## Mit csinál

- **Paraméter nélkül:** a két kötelező generált doksiból készít egy-egy PDF-et:
  - `docs-generated/architecture.md` → `export/architecture-v<N>.pdf`
  - `docs-generated/system-overview.md` → `export/system-overview-v<N>.pdf`
- **Paraméterrel:** a megnevezett fájl(ok)ból — ha a felhasználó azt kéri, hogy „még ebből is", akkor a két defaultból **és** a megnevezettekből.
- **Verziószám:** fájlonként **független** — az `export/` mappában lévő `<név>-v<N>.pdf` fájlok maximuma + 1, üres mappánál `v1`. Ezt a script számolja, **ne számold te**.
- A **ciklus** nem a fájlnévbe kerül, hanem a PDF **címlapjára** (`Lefedve: cycle-NN-ig · v3`) — a script olvassa ki a doksi fejléc-blokkjából.
- A forrásfájlokat **soha nem módosítja** (a `docs-generated/` gazdája a `08-doc-sync`).

---

## Feladatod

### 1. A bemenet feloldása

Nézd meg, mit adott meg a felhasználó a parancs hívásakor:

| A felhasználó azt írja… | Mit adsz át a scriptnek |
|---|---|
| semmit | **nincs fájl-argumentum** (a script a két defaultot használja) |
| konkrét fájl(oka)t (pl. `@docs-generated/architecture.md`) | pontosan azokat |
| „a specekből is", „a cycle-16 plan-jéből" — **szabad szöveg** | oldd fel konkrét fájl-útvonalakra, és **a beemelés előtt sorold fel a felhasználónak, mit fogsz exportálni** |
| „mindenből", „az összes doksiból" | ne találgass: kérdezz rá, mely mappára/fájlokra gondol (a `docs-generated/` egészére, vagy a `specs/` alá is?) |

**Ha egy megnevezett fájl nem létezik**, ne cseréld ki magadtól másra — jelezd, és kérdezz rá.

### 2. A script futtatása

Határozd meg a platform-specifikus script helyét a projekt gyökeréhez képest:

- **Claude Code:** `.claude/scripts/export-doc.py`
- **Google Antigravity CLI:** `.agents/scripts/export-doc.py`
- **Codex CLI:** `.codex/scripts/export-doc.py`
- **Cursor:** `.cursor/scripts/export-doc.py`
- **GitHub Copilot:** `.github/scripts/export-doc.py`

<!-- INCLUDE:shared/python-cmd.md -->

```bash
# paraméter nélkül (a két default doksi)
python3 <platform-script-path>

# konkrét fájl(ok)ból
python3 <platform-script-path> docs-generated/architecture.md specs/cycle-16-oidc/plan.md
```

**Opciók** (csak akkor add meg, ha a felhasználó kéri vagy a helyzet indokolja):

| Opció | Mikor |
|---|---|
| `--paper a3` | ha egy diagram A4-en olvashatatlanul kicsi lesz (széles szekvencia-diagramok) |
| `--engine pagedjs` | ha a felhasználó CSS-alapú formázást kér. **Default `xelatex`** — ez ad oldalszámozott tartalomjegyzéket és tömörebb tördelést; a pagedjs lazábban tördel és hajlamos üres oldalt beszúrni |
| `--check` | csak a függőségeket ellenőrzi (pandoc, mermaid-filter, xelatex + LaTeX csomagok), nem exportál |
| `--dry-run` | kiírja, mely fájlokból milyen verziószámú PDF készülne — nem futtat pandocot |
| `--export-dir <mappa>` | ha a felhasználó nem az `export/`-ba kéri |
| `--keep-build` | hibakereséshez: a build-mappa siker esetén is megmarad |

### 3. Az eredmény visszajelzése

Írd ki a script kimenetét, és a válaszod végén helyezd el az elkészült PDF-ek **közvetlen, kattintható linkjét**.

### 4. `export/` a verziókezelésből (egyszeri, csak VCS mellett)

Ha a projektben van verziókezelő, és az `export/` mappa **még nincs** kizárva (`git check-ignore -q export/` nem-nulla kilépő kóddal tér vissza), kérdezd meg **egyszer**:

<!-- INCLUDE:lang/export-doc.md#gitignore-felajanlas -->

Csak a felhasználó jóváhagyása után írj a `.gitignore`-ba. Ha nemet mond, ne kérdezd újra a további futásoknál.

---

## Hibakezelés

- **Hiányzó függőség (kilépő kód `2`):** a script kiírja, mi hiányzik és a telepítő parancsot (jellemzően `npm install -g mermaid-filter`). **Ne próbáld megkerülni** és ne generálj PDF-et mermaid-renderelés nélkül: a diagramok nélkül/hibásan a doksi használhatatlan. Add át a telepítő parancsot a felhasználónak, és állj meg.
- **Pandoc-hiba (kilépő kód `1`):** a script kiírja a pandoc stderr-jét, a `mermaid-filter.err`-t és az xelatex logot, és **megtartja a build-mappát**. Ha egy konkrét mermaid blokk szintaktikailag hibás, az a `docs-generated/` **forráshibája** — jelezd a felhasználónak, hogy a `08-doc-sync` fázisban javítandó, ne írd át magad a generált doksit.
- **Részleges siker:** ha több fájlt kértek és csak néhány készült el, sorold fel melyik sikerült és melyik nem — a script fájlonként jelzi.

---

## Amit NE tegyél

- **Ne módosítsd a forrás markdown fájlokat** — se a mermaid blokkokat, se a fejléc-blokkot. A script a build-mappában készít másolatot, arra teszi rá a YAML fejlécet.
- **Ne számold te a verziószámot** és ne nevezd át a kimenetet — a script determinisztikusan végzi.
- **Ne futtasd a pandocot közvetlenül** kézzel összeállított paraméterekkel. A motor-beállítások (`MERMAID_FILTER_FORMAT`, `header.tex`, `--resource-path`, széles ábrák skálázása) a scriptben vannak — kézi hívással ezek kimaradnak, és a diagramok minősége romlik vagy a címkék elvesznek.
- **Ne commitáld az `export/` mappát**, hacsak a felhasználó nem kéri: a PDF bináris, ciklusonként hízik, és bármikor újragenerálható a `docs-generated/`-ből (ami viszont verziókezelt).
