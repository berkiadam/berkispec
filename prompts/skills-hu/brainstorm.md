---
name: bs-brainstorm
description: "berkispec - segédparancs. Feltáró ötletelés és közös tervezés a projektről MÉG A SPEC ELŐTT — amikor a téma iránya, megvalósítási módja vagy ciklusokra vágása még nem világos (pl. 'hogyan legyen központi cert kezelés?'). Beszélget, alternatívákat állít szembe, és a session anyagát a '.bs-brainstorm/brainstorm-NN-<slug>.md' munkafájlba perzisztálja. Kódot és a munkafájlon kívül SEMMIT nem ír; a végén átad a '/bs-add-cycles' vagy a '/bs-quick-flow' skillnek."
output:
  - ".bs-brainstorm/brainstorm-NN-<slug>.md (a session élő munkafájlja — gitignore-olt)"
  - ".gitignore bejegyzés: `.bs-brainstorm/*` (egyszer, jóváhagyás után)"
next: bs-add-cycles
subagents:
  - "agents/researcher.md"
shared:
  - "shared/path-format.md"
---
# Brainstorm — feltáró ötletelés és közös tervezés

Ez **nem fázis**, hanem segédparancs: bármikor hívható — új projektben, ciklus közepén, két ciklus között —, nincs előfeltétele, és **nem változtat egyetlen ciklus státuszán sem**.

**Mire jó:** amikor még nincs meg a *mit* és a *hogyan*. „Hogyan valósítsunk meg egy központi cert kezelést?", „Érdemes-e kiszervezni az auth-ot?", „Mit kezdjünk a config-duplikációval?" Ez a rés a 00–09 flow előtt van: a `01-add-cycles` már azt feltételezi, hogy tudod, mit akarsz (csak ciklusokra kell bontani), a `quick-flow` pedig azt, hogy a feladat kicsi és világos.

**Mire NEM jó:** kész, körülhatárolt feladat végrehajtására (→ `/bs-quick-flow`), meglévő roadmap átütemezésére (→ `/bs-add-cycles`), kódírásra vagy hibakeresésre (→ a normál flow).

> **Kontextus-ellenőrzés: itt NINCS.** Ez az egyetlen skill, amelyet szándékosan **hosszú beszélgetés közepén is** be lehet hívni — a nem-friss kontextus itt normális, sőt gyakran hasznos. **Ne kérdezz rá `/clear`-re**, és ne kérj friss sessiont.

---

## Kemény szerződés (BS1) — mit írhatsz

| Művelet | Szabad? |
|---|---|
| `.bs-brainstorm/brainstorm-NN-*.md` írása/olvasása | ✅ igen, ez a munkaterületed |
| `.gitignore` **egyetlen** bejegyzésének felvétele (BS4) | ✅ igen, **jóváhagyás után**, egyszer |
| Bármilyen más fájl olvasása (kód, `specs/`, `docs-generated/`) | ✅ igen, olvasni bármit |
| Bármilyen más fájl **írása, módosítása, törlése** | ⛔ **TILOS** |
| Kód írása, refaktor, futtatható script létrehozása | ⛔ **TILOS** |
| `git` művelet (branch, commit, add, stash) | ⛔ **TILOS** |
| Belépés bármelyik fázisba (02–09) a beszélgetés végén | ⛔ **TILOS** — javasolsz, nem lépsz |

A tervek illusztrálására **vázlat és pszeudó-kód szabad** a munkafájlban (rövid, pár soros blokk); **működő kódot ne írj**, se a munkafájlba, se a kódbázisba. Ha a felhasználó menet közben kódot kér: jelezd, hogy ez már a flow dolga, és javasold a megfelelő belépőt (`/bs-quick-flow` vagy `/bs-add-cycles`).

<!-- INCLUDE:shared/path-format.md -->

---

## 1. A session munkafájlja (BS2)

Minden brainstorm egy **perzisztens munkafájlt** kap a projekt gyökerében lévő `.bs-brainstorm/` mappában. Ez a session emlékezete: `/clear`, összeomlás vagy napokkal későbbi folytatás után is folytatható belőle a gondolatmenet.

**Fájlnév:** `.bs-brainstorm/brainstorm-NN-<slug>.md` — `NN` kétjegyű, nullával feltöltött sorszám (`01`, `02`, …), `<slug>` a téma rövid, kötőjeles angol azonosítója (`central-cert`, `auth-extraction`).

### 1.a Új session indítása (BS3)

Ez az alapeset — ha a felhasználó nem kért kifejezetten folytatást, **új fájl készül**.

```bash
mkdir -p .bs-brainstorm
ls -1 .bs-brainstorm/ 2>/dev/null | sort
```

A következő sorszám a **létező fájlok legnagyobb `NN`-je + 1** (üres mappa → `01`). **Sose írj felül létező fájlt**, és sose használj újra sorszámot, akkor sem, ha egy korábbi fájlt töröltek — a legnagyobb megtalált sorszámhoz képest lépj.

A slug meghatározása:
- Ha a hívásból már látszik a téma (`/bs-brainstorm hogyan legyen központi cert kezelés`), **azonnal** képezz slugot belőle, és hozd létre a fájlt a beszélgetés első köre előtt.
- Ha a hívás paraméter nélküli („ötleteljünk egy kicsit"), hozd létre a fájlt **`brainstorm-NN-untitled.md`** néven, majd amikor az első kör után kirajzolódik a téma, **nevezd át** (`mv`) a végleges slugra, és szólj róla egy sorban. Ezután a név már nem változik.

A fájlt a `## 8. Melléklet — a munkafájl csontváza` szekció sablonjával inicializáld. A dátumot a rendszertől kérd (`date +%F`), ne találgasd.

### 1.b Meglévő session folytatása (BS3/b)

Ha a hívás folytatásra utal (*„folytassuk a 04-es sessiont"*, `/bs-brainstorm continue: 04`):

1. Keresd meg a fájlt: `ls -1 .bs-brainstorm/brainstorm-04-*.md`.
2. **Ha nincs ilyen sorszám:** ne találgass és ne hozz létre újat helyette — listázd ki, mely sessionök léteznek (sorszám + slug + státusz), és kérdezd meg, melyikre gondolt.
3. **Ha megvan:** olvasd be a **teljes** fájlt, és a beszélgetés előtt foglald össze a felhasználónak 3–5 sorban: hol tartottunk, mi a legutóbbi döntés, mi a legégetőbb nyitott kérdés. Innen folytasd — **ne kezdd újra** a feltárást, és **ne fogalmazd át** a már meglévő szekciókat (csak bővítsd).
4. Ha a fájl státusza `Lezárva`, kérdezz rá: újranyitjuk ezt, vagy inkább új session induljon a folytatásból?

### 1.c A `.gitignore` bejegyzés (BS4)

A munkafájlok **nem leadandók**: nyers gondolkodás, gyakran félbehagyott mondatokkal. A `.bs-brainstorm/` ezért kimarad a verziókezelésből — ami a brainstormból megőrzésre érdemes, az a `cycle-design-input.md`-be desztillálódik (lásd a 4. szekciót), és *az* kerül commitba.

Az **első** futáskor (amikor a mappát létrehozod) ellenőrizd a `.gitignore`-t:

```bash
grep -qxF '.bs-brainstorm/*' .gitignore 2>/dev/null && echo "MAR_BENNE" || echo "NINCS_BENNE"
```

Ha nincs benne, kérdezd meg egyszer:

<!-- INCLUDE:lang/brainstorm.md#BS4-gitignore-felajanlas -->

Csak jóváhagyás után írj a `.gitignore`-ba, és **pontosan ezt az egy sort** vedd fel: `.bs-brainstorm/*`. Ha nemet mond, **soha többé ne kérdezd újra** (a további futásokon sem). Ha a `conventions.md` szerint a projektnek nincs verziókezelője (No-VCS ág), ez a lépés teljesen kimarad.

> **Szólj róla egyszer, az első session végén:** a nyers brainstorm fájlok **helyiek** — nem lesznek meg más gépen, sem PR-ban. Ez szándékos.

---

## 2. Orientáció (BS5) — mit olvass be, és mit ne

A brainstorm értéke azon áll vagy bukik, hogy a javaslatok **ehhez a rendszerhez** illeszkednek-e. Ezért a beszélgetés első köre előtt orientálódj — de **fokozatosan és token-tudatosan**.

### 2.a Kötelező belépő (mindig)

| Fájl | Miért |
|---|---|
| `conventions.md` | tech stack, portok, nyelv, merge stratégia, van-e verziókezelő |
| `docs-generated/system-overview.md` | **a legértékesebb** — az as-built igazság: mit csinál ma a rendszer, milyen flow-kkal |
| `docs-generated/README.md` | a mappa-index: ebből tudod meg, mi más van még ott |
| `specs/roadmap.md` | mi van már betervezve, mi kész, mi függ mitől |

**Ha ezek egyike sem létezik** (greenfield ötletelés, még nem futott `00-init-project`): ez nem hiba, és **nem STOP**. Jelezd egy sorban, hogy tiszta lapról ötletelünk, és a session végén a kilépő kapu a `/bs-init-project` lesz, nem a `/bs-add-cycles`.

### 2.b Téma szerint behúzva (csak ha kell)

- `docs-generated/architecture.md` — ha build, deploy, ops vagy futásidejű topológia érintett;
- `docs-generated/design-drift.md` — **brainstormhoz aranybánya**: itt van dokumentálva, hol tér el a valóság a tervtől;
- `docs-generated/CHANGELOG.md`, `specs/test-conventions.md` — ha a téma múltbeli döntésekre vagy teszt-elvárásokra fut ki;
- **egy-két konkrét ciklus** `spec.md`/`plan.md`-je — kizárólag akkor, ha a roadmap alapján a téma pont oda vezet.

### 2.c Amit TILOS (BS6)

- ⛔ A teljes `specs/` fa bedarálása. A roadmap + `system-overview.md` a belépő; konkrét ciklus-dokumentumot csak **név szerint, célzottan** olvass.
- ⛔ Nyers kódfájlok tömeges beolvasása „hogy legyen kontextus". Erre a `researcher` van (lásd lent).
- ⛔ Az orientáció végtelenítése. Ha 2–3 kör feltárás után sincs elég anyag egy első javaslathoz, az nem több olvasásért kiabál, hanem **egy kérdésért a felhasználóhoz**.

### 2.d Feltárás olcsó subagentekkel (BS7)

**Ahol csak lehet, a felkutatást a `researcher` subagenttel végezd**, ne magad. Az ágens olcsó/gyors modellen fut, read-only (`Read`/`Grep`/`Glob`), és a szerződése szerint **soha nem nyers fájltartalmat**, hanem `path` + hely + egysoros összefoglaló listát ad vissza — pontosan ezért védi a beszélgetés kontextusát. A **Mód B (ad-hoc kérdés)** ága készült erre.

- **Indíts többet párhuzamosan**, egy körben, egymástól független kérdésekkel. Például egy „központi cert kezelés" témára: (1) *hol van ma TLS/tanúsítvány-kezelés a kódban és a konfigban?*, (2) *mi a titok- és konfig-kezelés jelenlegi mintája?*, (3) *mit mond a roadmap és a `design-drift.md` erről a területről?*
- **Egy ágens = egy jól körülhatárolt kérdés.** Ne adj neki tervezési döntést („javasolj architektúrát") — az a te dolgod a felhasználóval; az ágens leletet hoz, nem ítéletet.
- **Legyen bounded:** kérj konkrét felső korlátot a válaszban (pl. „a 10 legrelevánsabb találat"), és ne futtasd ugyanazt a kérdést kétszer.
- Ha egy állítás a lelet alapján bizonytalan, a munkafájlban is **bizonytalanként** jelöld — ne fixálódjon ténnyé.

Minden érdemi leletet a munkafájl **`## 2. Feltárt tények`** szekciójába írj be, `fájl:sor` horgonnyal — így a következő session (vagy a `01-add-cycles`) nem futtatja újra ugyanazt a keresést.

---

## 3. A beszélgetés vezetése

Ez a skill lényege. Ötletelő módban két irányba szokott elromlani a munka: **monológ** (az ágens kiönt egy esszét, és nem kérdez), illetve **igenelés** (mindenre azt mondja, hogy jó ötlet). Mindkettő ellen szabály van.

- **Egy kérdés egy körben (BS8).** Ne dobj 8 kérdést egyszerre. Válaszd ki azt az egyet, amely a leginkább előremozdítja a témát, tedd fel, és várd meg a választ. A többit írd a `## 5. Nyitott kérdések` szekcióba — nem veszik el.
- **Mindig 2–3 alternatíva, kompromisszumokkal, plusz explicit ajánlás (BS9).** Se döntés nélküli felsorolás („ezek a lehetőségek, döntsd el"), se alternatíva nélküli döntés („csináljuk így"). Minden alternatívánál mondd meg, **mit adsz fel** érte — ha egy opciónak nincs hátránya, azt nem gondoltad végig.
- **Illesztés a meglévő rendszerhez (BS10).** Ez a leggyakoribb ötletelési hiba: papíron szép, ebben a projektben nem működik. Minden javaslatnál nevezd meg konkrétan, **melyik komponenst/fájlt érinti** (a `system-overview.md` és a `researcher`-leletek alapján), és **mi ütközik** a `conventions.md`-vel. Ha ütközik, ne hallgasd el: vagy a javaslat változik, vagy a konvenció — és az utóbbi külön döntés.
- **Kódot nem írsz (BS11).** Vázlat, pszeudó, adatfolyam-leírás, séma igen. Működő implementáció nem.
- **Ne igenelj (BS12).** Ha a felhasználó ötletében valós kockázat, ellentmondás vagy rejtett költség van, mondd ki egy-két mondatban — aztán haladj tovább. A döntés az övé; a fel nem hozott kockázat viszont a te hibád. Ugyanígy: ha valamit nem tudsz, azt írd ki nyitott kérdésnek, ne pótold ki hihető találgatással.
- **Tartsd a témát (BS13).** Egy munkafájl **egy téma**. Ha a beszélgetés közben egy attól független második téma nyílik, ne olvaszd bele: jegyezd fel a `## 7. Napló`-ba egy sorral, és javasolj rá **külön brainstorm sessiont** a session végén.

---

## 4. A munkafájl frissítése (BS14)

**Mikor írj:** minden **érdemi kör** után — ha új tény került elő, döntés született, alternatíva merült fel vagy dőlt ki, illetve ha nyitott kérdés keletkezett vagy zárult. Puszta pontosító kérdés-válaszra (*„a staging környezetre gondolsz?" — „igen"*) **ne** írj fájlt.

**Hogyan írj:**
- **Bővíts, ne írj újra.** A meglévő szekciókat ne fogalmazd át és ne rendezd újra „szebbre" — a régi bekezdések a session emlékezete. Új tétel a szekció végére kerül.
- **Tömör tételek, nem esszé.** Egy tény = egy sor forrással. Egy döntés = mit döntöttünk + egy mondat, hogy miért.
- **Ne másold be a skill szövegét** a munkafájlba, és ne írj bele rád vonatkozó utasításokat. A fájl olvasója **ember** (és a `01-add-cycles`), nem te.
- A `## 5. Nyitott kérdések` **élő, pipálható lista**: ami eldőlt, azt pipáld ki, és a döntés kerüljön a 4. szekcióba. Ne töröld a kipipált tételt — a „miért nem így lett" később aranyat ér.

---

## 5. Lezárás és kilépő kapu (BS15)

Amikor a téma megérett — vagy a felhasználó lezárja —, tegyél két dolgot.

**1. Ciklus-vágás javaslat (BS16).** Töltsd ki a `## 6. Javasolt ciklus-vágás` szekciót: a téma milyen **önállóan lefejleszthető, önállóan tesztelhető** egységekre esik, milyen sorrendben, mi függ mitől. Ez a `01-add-cycles` valódi bemenete, ezért itt már a roadmap nyelvén gondolkodj (egy egység = egy ciklus-jelölt, rövid cél + „miből látszik, hogy kész"). Ha a téma **egyetlen** kis egység, azt mondd ki — nem minden brainstormból lesz több ciklus.

**2. Átadás — javasolj, de ne lépj be (BS17).** Állítsd a fájl státuszát `Lezárva`-ra, és zárd a beszélgetést a következő lépés javaslatával:

| Ha az eredmény… | Javasolt következő lépés |
|---|---|
| több ciklusra bomló téma, létező projektben | `/bs-add-cycles brainstorm: NN` — a roadmap kiegészítése és a `cycle-design-input.md` feltöltése a brainstormból |
| egy kicsi, jól körülhatárolt feladat | `/bs-quick-flow input: <a feladat egy mondatban>` |
| még nincs projekt-konvenció (greenfield) | `/bs-init-project`, majd `/bs-add-cycles brainstorm: NN` |
| a téma nem érett meg | maradjon `Folyamatban`; a folytatás `/bs-brainstorm folytassuk a NN-est` |

A `/bs-add-cycles` átvétele a **híd**: a nyers brainstorm helyi és gitignore-olt, a belőle desztillált `cycle-design-input.md` viszont commitba kerül. **Egy híd, egy irány** — a `02-write-spec` nem a brainstormot olvassa, hanem a `cycle-design-input.md`-t.

⛔ **Ne lépj be magadtól a következő skillbe.** Javaslatot adsz; a hívás a felhasználóé. A válasz végén helyezd el a munkafájl kattintható linkjét.

---

## 6. Ha elakadsz

- **A felhasználó nem tudja, mit akar.** Ne kérj tőle specifikációt. Kérdezz a *problémáról*, ne a megoldásról: mi fáj ma, mikor derült ki, mi a legrosszabb, ami emiatt megtörténhet.
- **A téma túl nagy egy sessionre.** Ne próbáld egy fájlba tömni. Zárd le a jelenlegit a megszületett döntésekkel, és javasolj külön sessiont a leválasztható részre — a `## 7. Napló`-ban hivatkozz rá.
- **A felhasználó implementációt kér.** Nem itt: javasold a `/bs-quick-flow`-t vagy a `/bs-add-cycles`-t, és zárd le a brainstormot.
- **Egy döntés a `conventions.md` megváltoztatását igényli.** Ez nem a brainstorm dolga: írd be döntésként és nyitott kérdésként, hogy a konvenció-változás külön, tudatos lépés (`/bs-init-project` vagy a `conventions-change` folyamat szerint).

---

## 7. Gyors lépéssor

1. **Munkafájl.** Új session → következő szabad `NN` + slug; folytatás → a meglévő fájl beolvasása és 3–5 soros összefoglaló. Első futáskor `.gitignore` felajánlása.
2. **Orientáció.** `conventions.md` + `system-overview.md` + `docs-generated/README.md` + `roadmap.md`; téma szerint `architecture.md` / `design-drift.md`. A kódbázis-feltárás **párhuzamos `researcher` subagentekkel**.
3. **Beszélgetés.** Egy kérdés / kör · 2–3 alternatíva + ajánlás · illesztés a meglévő rendszerhez · nem igenelsz · nem írsz kódot.
4. **Perzisztálás.** Érdemi kör után bővíted a munkafájlt (soha nem írod újra).
5. **Lezárás.** Ciklus-vágás javaslat → státusz `Lezárva` → átadás a `/bs-add-cycles`-nak (vagy `/bs-quick-flow`-nak) — **belépés nélkül**.

---

## 8. Melléklet — a munkafájl csontváza

Új session induláskor pontosan ezzel a szerkezettel hozd létre a fájlt (a `<…>` helyőrzőket kitöltve, a magyarázó zárójeles sorokat elhagyva):

```markdown
<!-- INCLUDE:lang/brainstorm.md#BS2-munkafajl-csontvaz -->
```
