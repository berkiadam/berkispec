---
phase: 10
name: bs-cycle-status
description: "berkispec - 10. Ciklusok státuszának ellenőrzése. Kilistázza a projekt ciklusait (Kész/Folyamatban), és interaktív TUI felületen vagy argumentumként megadva részletesen mutatja a fázisaik előrehaladását (KÉSZ, FOLYAMATBAN, MÉG NEM FUTOTT)."
prerequisites: []
output: []
prev: ""
next: ""
subagents: []
---
# 10 — Ciklus státusz ellenőrző
<!-- INCLUDE:shared/context-check.md -->

---

Ez a parancs lehetővé teszi a projektben lévő összes ciklus státuszának gyors és interaktív ellenőrzését. Képes felismerni a Teljes (00-09) flow-t és a rövidített Egyszerűsített (Lightweight) flow-t is, és fázisonként megjeleníti az előrehaladást.

## Használati Útmutató

A parancs kétféleképpen használható:

1. **Interaktív (paraméter nélkül)**:
   Ha a felhasználó nem ad meg paramétert a parancs hívásakor, akkor az ágens elindítja az interaktív TUI (Terminal User Interface) alkalmazást, ahol a FEL/LE nyilakkal lehet navigálni a nem befejezett ciklusok között, és a jobb oldalon dinamikusan frissül az adott ciklus fázisainak listája. Az ENTER megnyomására kilép a TUI-ból és részletesen kiírja a kiválasztott ciklus státuszát.

2. **Közvetlen (konkrét ciklus megadásával)**:
   Megadható egy konkrét ciklus mappa neve (pl. `cycle-01-oidc-login` vagy a teljes elérési útja: `specs/cycle-01-oidc-login`). Ebben az esetben a TUI nem indul el, hanem az ágens azonnal kiírja a megadott ciklus státuszait.

---

## Feladatod az ágensként való futtatáskor

1. **Paraméter beolvasása**:
   - Vizsgáld meg, hogy a felhasználó megadott-e konkrét ciklust vagy útvonalat inputként a parancs indításakor (pl. `specs/cycle-01-...` vagy csak `cycle-01-...`).
   
2. **Script futtatása**:
   - Határozd meg a platform-specifikus futtató script helyét a projekt gyökeréhez képest:
     - **Google Antigravity CLI** esetén: `.agents/scripts/cycle-status.py`
     - **Claude Code** esetén: `.claude/scripts/cycle-status.py`
     - **Cursor** esetén: `.cursor/scripts/cycle-status.py`
     - **GitHub Copilot** esetén: `.github/scripts/cycle-status.py`
     - **Codex CLI** esetén: `.codex/scripts/cycle-status.py`
   
   - **Ha a felhasználó megadott egy ciklust (pl. `specs/cycle-01-oidc-login`)**:
     Futtasd a scriptet a megadott argumentummal:
     > **Python-parancs (platformfüggő):** a példákban `python3` szerepel (Linux/macOS). **Windowson** a `python3` gyakran nem létezik — vagy a Microsoft Store stubja, ami megnyitja a Store-t —, ezért ott `python` vagy `py -3` a helyes hívás. Ha a `python3` „command not found" / „not recognized" hibát ad, **próbáld újra `python`-nal, majd `py -3`-mal**, ugyanazokkal a paraméterekkel. Ez nem a szkript hibája, és nem kell miatta megállni.

     ```bash
     python3 <platform-script-path> <bemeneti-paraméter>
     ```
     
   - **Ha a felhasználó NEM adott meg paramétert (üresen hívta meg)**:
     Futtasd a scriptet interaktív módon (az ágens jóváhagyást kér a parancs futtatására a felhasználótól):
     ```bash
     python3 <platform-script-path>
     ```

3. **Kimenet megjelenítése**:
   - Mutasd meg a futás eredményét a felhasználónak a chatedben.