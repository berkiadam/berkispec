# Két fejlesztési út

← [Vissza a főoldalra](../../README-HU.md) · [Oldalindex](README.md)

A felhasználónak **két útja** van; a feladat súlya dönti el, melyik a megfelelő:

1. **Teljes berki spec flow (00–09 fázis)** — a nagyobb, összetettebb fejlesztésekhez. Külön `spec.md` → `plan.md` → `tasks.md` dokumentumok, kereszt-fázisos `analyze`, `validate`, `doc-sync` és `review` minőségi kapukkal és önjavító hurkokkal. Üres projektnél a `00-init-project`, új ciklusnál a `01-add-cycles` skillel indul. Ezt írja le a README többi része.

2. **Egyszerűsített (lightweight) flow** — kis, jól körülhatárolt feladatokhoz, amelyek 3-4 lépésben megoldhatók (pl. **konfiguráció összeállítása**, **egyszerűbb script megírása**, kisebb javítás). Egyetlen háromfázisú recept: `spec-plan.md` → `tasks.md` → implementáció, a `/bs-quick-flow` skillben. Mindkét artefaktum **státusz-mezőt** hordoz, így a fázishatár commitolt tény (a `/bs-cycle-status` is ebből olvas). Nincs külön plan/bs-analyze/bs-validate/bs-doc-sync fázis; az opcionális ágenseket (`researcher`, `analyzer`, `reviewer`) csak akkor hívja, ha tényleg segítenek.

**Hogyan dönts?**

| Jellemző | Egyszerűsített flow | Teljes berki spec flow |
|---|---|---|
| Tipikus feladat | konfiguráció, egyszerű script, kisebb javítás | új funkció, több komponens, összetett logika |
| Méret | 3-4 lépésben megoldható | önálló, vertikálisan vágható ciklus(ok) |
| Dokumentumok | `spec-plan.md` + `tasks.md` (mindkettő státusz-mezővel) | `spec.md` + `plan.md` + `tasks.md` |
| Minőségi kapuk | inline + opcionális ágensek | `analyze` / `validate` / `doc-sync` / `review` hurkok |
| Belépő | `/bs-quick-flow` | `/bs-init-project` / `/bs-add-cycles` |

**Alapértelmezett flow:** a projekt jellegét a `00-init-project` fázisban tisztázzuk (termékfejlesztés vs. konfiguráció/scriptelés), és ez alapján egy **default flow** kerül a `conventions.md` `## Fejlesztési módszertan` szekciójának **Alapértelmezett flow** mezőjébe. Ez a kiindulópont — feladatonként felülbírálható.

A két út **átjárható**: ha az egyszerűsített flow közben kiderül, hogy a feladat túlnő rajta (nagyobb kódírás, több komponens, összetett tervezés), a skill megállítja a munkát és **átirányít a teljes folyamatra** (`01-add-cycles`). Fordítva is: a `01-add-cycles` és a `03a-write-code-plan` jelzi, ha a feladat túl egyszerű a teljes ciklushoz, és javasolja az egyszerűsített flow-t.

## 1.1 Mindkét út előtt (opcionális): `/bs-brainstorm`

A két út **közös előszobája** a `/bs-brainstorm` segédparancs — arra az esetre, amikor még nem a *méret* a kérdés, hanem az, hogy **mit és hogyan** akarunk egyáltalán. („Hogyan valósítsunk meg egy központi cert kezelést?", „Érdemes-e kiszervezni az auth-ot?") Ez a rés a `00–09` flow **előtt** van: a `01-add-cycles` már azt feltételezi, hogy tudod, mit akarsz (csak ciklusokra kell bontani), a `/bs-quick-flow` pedig azt, hogy a feladat kicsi és világos.

**Mit tesz:**
- **Orientálódik** a projektben: `conventions.md`, `docs-generated/system-overview.md` (as-built igazság), `docs-generated/README.md` (mappa-index), `specs/roadmap.md` — téma szerint az `architecture.md` és a `design-drift.md`. A teljes `specs/` fa bedarálása tilos (BS6).
- **A kódbázis-feltárást olcsó, párhuzamos `researcher` subagentekkel** végzi (Mód B, read-only, legolcsóbb tier, „soha nem nyers fájltartalom") — a beszélgetés kontextusát így egy leletlista terheli, nem fájlok tucatja (BS7).
- **Beszélget, nem monologizál:** egyszerre **egy** kérdés, minden javaslatnál **2–3 alternatíva trade-offokkal + explicit ajánlás**, kötelező illesztés a meglévő rendszerhez és a `conventions.md`-hez, és tilos az igenelés — a fel nem hozott kockázat az ágens hibája (BS8–BS13).
- **Perzisztál:** a session anyaga a `.bs-brainstorm/brainstorm-NN-<slug>.md` munkafájlba kerül, fix csontvázzal (*Cél · Feltárt tények forrással · Alternatívák · Döntések · Nyitott kérdések · Javasolt ciklus-vágás · Napló*). Minden érdemi kör után **bővül** — soha nem íródik újra (BS14). Így egy `/clear`, összeomlás vagy napokkal későbbi visszatérés után is folytatható: `/bs-brainstorm folytassuk a 04-est`.

**Kemény korlátok (BS1):** kódot nem ír, `git`-et nem futtat, és a `.bs-brainstorm/` mappán kívül **egyetlen fájlt sem** módosít — egyetlen kivétellel: az első futáskor felajánlja a `.bs-brainstorm/*` bejegyzés felvételét a `.gitignore`-ba (jóváhagyás után, egyszer). A végén **javasol**, de nem lép be a következő skillbe.

**A híd a flow felé (BS18):** a nyers munkafájl **helyi és gitignore-olt** (nyers gondolkodás, nem leadandó) — ami megőrzésre érdemes, az a ciklus `cycle-design-input.md`-jébe desztillálódik, és *az* kerül commitba:

```
/bs-brainstorm hogyan legyen központi cert kezelés
        ↓                      .bs-brainstorm/brainstorm-04-central-cert.md   (gitignore-olt)
/bs-add-cycles brainstorm: 04
        ↓                      specs/cycle-NN-<name>/cycle-design-input.md    (commitolt)
/bs-write-spec
```

A `01-add-cycles` a `## 6. Javasolt ciklus-vágás` szekciót a roadmap-javaslat kiindulásának veszi, a `## 5. Nyitott kérdések` kipipálatlan tételeit pedig **kérdésként** teszi fel — amit a munkafájl megválaszol, azt nem kérdezi meg újra. **Egy híd, egy irány:** a `02-write-spec` nem a brainstormot olvassa, hanem a `cycle-design-input.md`-t.
