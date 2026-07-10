---
phase: 01
name: bs-add-cycles
description: "berkispec - 01. Használd az inicializálás után (Phase 01) fejlesztési ciklusok (roadmap) tervezéséhez, meglévők átütemezéséhez vagy új ciklus hozzáadásához — a feladatok logikai, önállóan tesztelhető egységekre bontása. Bemenet: 'conventions.md'. A 'specs/roadmap.md'-t hozza létre vagy frissíti 'Kész' státusszal."
prerequisites:
  - "conventions.md létezik"
output:
  - "specs/roadmap.md státusz: Kész"
prev: bs-init-project
next: bs-write-spec
subagents:
  - "agents/researcher.md"
---
# 01 — Ciklusok kezelése

Spec driven development-ben fejlesztünk szoftvert. A fejlesztés ciklusokra van bontva. Minden ciklus egy önállóan lefejleszthető, önállóan tesztelhető részegysége a teljes implementációnak.

Ez a fejlesztési folyamat **1-es fázisa (a 0–9 fázisokból)**:
0. projekt inicializálás (setup)
1. **ciklusok kezelése** ← most itt vagyunk
2. spec
3. plan
4. tasks
5. analyze
6. implement
7. validate
8. doc-sync
9. review & merge

---

## Előfeltétel

1. **`conventions.md` létezés-ellenőrzés:** olvasd be a projekt gyökerében a `conventions.md`-t. Ha nem létezik, STOP — térjenek vissza a `00` projekt inicializálás fázishoz.
2. **Munkafa ellenőrzés:** futtasd `git status --short`. Ha van commitálatlan változtatás, listázd, és kérdezd meg egy körben, hogy commitáljam-e most vagy folytassam — várj a válaszra. (A 01 roadmapet ír és ciklusmappát hoz létre; tiszta munkafáról induljon.)

---

## Folytatás megszakított futás után

Ha a 01 fázis félbeszakadt és új sessionban folytatódik:

```
1. Létezik specs/roadmap.md?
   → Olvasd be a státuszát és tartalmát.
   → Ha félig megírt (van [ ] nyitott kérdés, vagy hiányos ciklus blokk):
     folytasd az első hiányos résztől, ne kezdd újra.

2. Létrehozott, de hiányos ciklusmappa (mkdir megtörtént, de a roadmap
   blokk vagy a commit hiányzik)?
   → Fejezd be a hiányzó lépést (roadmap blokk, validáció, megerősítés, commit).

3. Félbeszakadt C. mód rekonstrukció (roadmap.md hiányzik, de a kísérlet
   elkezdődött)?
   → Kezdd újra a C. módot tiszta lappal.
```

---

## Mód detektálás — induláskor

**1. lépés:** Ellenőrizd a `specs/` könyvtár tartalmát (`ls specs/`).

**`specs/` üres vagy nem létezik** → tegyél fel **egy** kérdést:
> *"A `specs/` könyvtár üres. Mit szeretnél csinálni?*
> *A) Teljes roadmap tervezés — meghatározzuk az összes fejlesztési ciklust és létrehozzuk a `specs/roadmap.md`-t*
> *B) Egyetlen ciklus hozzáadása — csak egy új ciklust adunk a roadmap-hez"*

- Válasz **A** → folytasd az **A. móddal**
- Válasz **B** → folytasd a **B. móddal**

**`specs/`-ben vannak ciklus mappák**:
   **2. lépés:** Ellenőrizd, hogy létezik-e `specs/roadmap.md`.

   - **Ha létezik** → jelezd, és folytasd a **B. móddal**:
     > *"Találtam [N] meglévő ciklust: [cycle-01-xxx, cycle-02-xxx, ...]. Új ciklust adok a roadmap-hez."*

   - **Ha NEM létezik** → kérdezd meg:
     > *"Találtam [N] meglévő ciklust a `specs/` mappában, de nem találom a `specs/roadmap.md` fájlt. Szeretnéd, hogy a meglévő ciklus mappák és spec fájlok alapján rekonstruáljam a roadmap-et?"*
     - **Igen** → Kövesd a **C. mód — Roadmap rekonstrukció** lépéseit, majd a rekonstrukció után automatikusan folytasd a **B. móddal**.
     - **Nem** → Folytasd közvetlenül a **B. móddal**: az új ciklust hozzáadod, a roadmap többi része üres marad.

---

## A. mód — Teljes roadmap tervezés

### Feladatod

A HLD/LLD alapján határozd meg a fejlesztési ciklusokat, és írd le őket a `specs/roadmap.md` fájlba.

**A legfontosabb elv: vertikális vágás.** Ne réteg szerint vágj (pl. "Cycle 1: adatbázis, Cycle 2: API"), hanem feature szerint — minden ciklus végén legyen egy tesztelhető, end-to-end működő viselkedés.

**Ne írj spec-et, plan-t vagy implementációt.** Ez a lépés csak a ciklushatárokat és a sorrendet határozza meg.

### Output

**Fájl:** `specs/roadmap.md` a projekt gyökerében. Ha a `specs/` mappa nem létezik, hozd létre.

### Információgyűjtés — iteratív interjú

Mielőtt meghatározod a ciklusokat, elegendő információra van szükséged. Értékeld, mi áll rendelkezésre:

**Szükséges minimum:**
- A rendszer célja és határai egyértelműek
- A főbb komponensek és aktorok azonosítva vannak
- A kulcs user flow-k (belépéstől a főbb műveletekig) ismertek
- A külső rendszerekkel való integrációs pontok ismertek

**Ha bármely pont hiányzik:** tegyél fel **egy** célzott kérdést, várd meg a választ, majd értékeld újra. Addig ismételd, amíg a minimum teljesül. Ne tegyél fel egyszerre több kérdést.

Ha elegendő információ áll rendelkezésre, kezdd el a ciklus meghatározást.

### Vertikális vágás elvei

**Egy jó ciklus:**
- Egyetlen end-to-end viselkedést valósít meg (pl. "a felhasználó be tud lépni és lát egy tartalmat")
- Önállóan tesztelhető — a ciklus végén el lehet dönteni, hogy kész-e, anélkül hogy más ciklus kész lenne
- Minimális: csak annyit tartalmaz, amennyi a viselkedés demonstrálásához szükséges
- Mock-stratégiával kezeli a még nem kész függőségeket

**Rossz vágás jelei:**
- Csak egy rétegben dolgozik (csak backend, csak UI, csak konfiguráció)
- Nem tesztelhető önállóan — mindig szükség van valami másra
- Túl nagy: több mint 2-3 nap implementáció várható → bontsd tovább

### Roadmap struktúra

```md
# Fejlesztési Roadmap

**Státusz:** `Piszkozat` | `Nyitott kérdések vannak` | `Kész`

## Nyitott kérdések

- [ ] K01 — <kérdés szövege>
- [x] K02 — <kérdés szövege> → <döntés röviden>

## Cycle 01 — <cím>

**Viselkedés:** Mit tud a rendszer a ciklus végén? (1-2 mondat, felhasználói perspektívából)

**Érintett komponensek:** Mely rendszerrészek változnak?

**Előfeltétel:** — (vagy: Cycle NN)

**Mock stratégia:** Mit kell mock-olni a még nem kész komponensekből?

**Teszt kritérium:** Hogyan ellenőrizhető, hogy the ciklus kész? (konkrét, eldönthető állítás)

---

## Cycle 02 — <cím>

...
```

### Validációs ciklus — minden javasolt ciklus után

Mielőtt lezársz egy ciklus leírást, ellenőrizd:

1. **Tesztelhető-e önállóan?** Meg lehet-e mondani "kész / nem kész" a többi ciklus nélkül?
2. **Vertikális-e?** Átmegy-e az egész stacken, vagy csak egy réteget fed?
3. **Nem túl nagy-e?** Ha a várható implementáció több mint 2-3 munkanap, bontsd tovább.
4. **Egyértelműek-e a függőségek?** Ha egy ciklus feltételezi egy másik eredményét, ez jelölve van?

Ha bármely pontra "nem", módosítsd a ciklushatárt, mielőtt továbblépnél.

### Nyitott kérdések kezelése

**Alapszabály: a listából soha nem törlünk. Lezárt kérdést csak `[x]`-szel jelölünk — a szövege és a döntés megmarad.**

**Státusz átmenetek:**
- Roadmap írásának kezdetén: `Piszkozat`
- Ha van legalább egy `[ ]` kérdés: `Nyitott kérdések vannak`
- Ha minden kérdés `[x]` és a validációs ellenőrzés átment: `Kész`

**Iterációs szabályok:**
1. Ha ciklushatárok meghatározása során kérdés merül fel, add hozzá a `## Nyitott kérdések` listához `- [ ] Knn` formátumban, szekvenciális számozással.
2. Tegyél fel **egy** kérdést a felhasználónak, várd meg a választ. **Minden alkalommal, amikor kérdést teszel fel vagy jóváhagyást/véleményezést kérsz, a válaszod végén kötelezően helyezz el egy közvetlen, kattintható markdown linket az érintett fájlokra (pl. `[roadmap.md](file:///abszolút/útvonal/specs/roadmap.md)` formában).**
3. Ha a válasz megérkezett, jelöld `[x]`-szel és írj mellé egy soros összefoglalót (`→ döntés röviden`), majd vezesd át a döntést a roadmap-be.
4. Ha a válasz új kérdést nyit meg, add hozzá a lista végére a következő `Knn` számmal.
5. Addig iterálj, amíg minden kérdés `[x]` státuszban van.

Minden iteráció indítható új kontextussal: elég a `conventions.md` (ha létezik), a `specs/roadmap.md` aktuális állapota + ez a prompt.

### Megállási szabályok

- Ha a HLD/LLD egy komponens viselkedését nem definiálja egyértelműen és ez befolyásolja a ciklushatárokat: jelezd pontosan mi hiányzik, és kérj pontosítást. Ne találj ki viselkedést.
- Ha egy ciklus nem bontható tovább de még mindig nagy: jelezd a kockázatot és hagyj döntési lehetőséget a felhasználónak.
- Ha a ciklusok közötti függőségek körkörösek: jelezd, és kérj döntést a sorrendről.

Minden esetben csak **egy** problémát jelezz egyszerre.

### Státusz kezelés

Ha minden kérdés `[x]` és a validációs ellenőrzés átment, tedd fel a kérdést a felhasználónak:
*"A roadmap minőségellenőrzése átment és minden kérdés lezárt. Készen áll a roadmap? Ha megerősíted, átállítom `Kész` státuszra."* — Ne állítsd át a státuszt a megerősítés előtt. **A válasz végén helyezd el a `specs/roadmap.md` közvetlen, kattintható linkjét.**

Ha a felhasználó megerősíti:
- Állítsd a `specs/roadmap.md` státuszát `Kész`-re.
- Készíts git commitot a fázis befejezéséről:
  ```bash
  git add specs/roadmap.md
  git commit -m "cycle-NN: 01-cycles"
  ```
  ahol `NN` az éppen tervezett első ciklus száma (pl. `cycle-01: 01-cycles`).
- Jelezd: *"A roadmap kész. Folytathatjuk az 1. ciklus spec fázisával (02)."*

---

## B. mód — Új ciklus hozzáadása

### Előkészítés

1. Olvasd be a `specs/roadmap.md`-t (ha létezik) — kontextus és ciklusszám meghatározáshoz. Ha nem létezik, hozd létre az alap struktúrával (`# Fejlesztési Roadmap\n\n**Státusz:** Kész`).
2. Nézd meg a `specs/` könyvtárat — határozd meg a meglévő legmagasabb ciklusszámot (`ls specs/ | sort`). Az új ciklus száma: max + 1 (pl. ha van cycle-09, az új cycle-10). Ha nincs egy sem, az új cycle-01.
3. Jelezd a felhasználónak:
   > *"Meglévő ciklusok: [N db — cycle-01-xxx, ...]. Következő ciklusszám: [NN]."*

### Információgyűjtés

1. Tegyél fel **egy** kérdést:
   > *"Mi az új ciklus célja? Röviden írd le, milyen viselkedést szeretnél megvalósítani."*

   > **Flow-méret ellenőrzés (a cél leírása után, a névjavaslat előtt):** Mérlegeld, hogy a feladat **nem túl kicsi-e** a teljes, többfázisú ciklushoz. Ha a cél 3-4 lépésben, egyetlen menetben megoldható — tipikusan **konfiguráció összeállítása/módosítása, egyszerűbb script megírása, kisebb javítás vagy lokális finomhangolás** —, akkor a teljes `02→…→09` flow túlméretezett. Ilyenkor **állj meg, és javasold az egyszerűsített flow-t**, mielőtt ciklust hoznál létre:
   >
   > > *„Ez a feladat elég kicsinek tűnik a teljes fejlesztési ciklushoz (külön spec/plan/tasks + analyze/validate/review). Javaslom helyette az egyszerűsített flow-t (`prompts/skills/sdd-lightweight-flow.md`): `spec.md` → `task.md` → implementáció, néhány lépésben. Mehetünk azzal, vagy mégis teljes ciklust szeretnél?"*
   >
   > A döntés a Felhasználóé: ha a teljes ciklust kéri, folytasd itt; ha az egyszerűsítettet, irányítsd át a `sdd-lightweight-flow` skillhez.

2. Ha megérkezett a cél leírása, készíts egy javaslatot a ciklus nevére **kebab-case** formátumban, tömören, a viselkedést tükrözve (pl. `performance-load-test`, `token-exchange`, `oidc-login`). Kérdezd rá:
   > *"A cél alapján a javasolt név: `[javasolt-név]`. Ez lesz a branch és a mappa neve is (pl. `cycle-NN-[javasolt-név]`). Megfelelő, vagy inkább mást szeretnél?"*

Ha a név nem felel meg, kérd a felhasználó saját javaslatát, azt használd.

Ha a leírás vagy a név alapján valamit tisztázni kell (pl. meglévő ciklusokkal való átfedés, függőség), tegyél fel még **egy** kérdést. Ne tegyél fel egyszerre többet.

### Az új ciklus megírása

Írd meg a ciklus leírását a standard struktúra szerint. Ez a leírás a `specs/roadmap.md` fájlba kerül, a meglévő ciklusok után beszúrva:

```md
## Cycle NN — <cím>

**Viselkedés:** Mit tud a rendszer a ciklus végén? (1-2 mondat, felhasználói perspektívából)

**Érintett komponensek:** Mely rendszerrészek változnak?

**Előfeltétel:** — (vagy: Cycle NN — a meglévők közül)

**Mock stratégia:** Mit kell mock-olni a még nem kész komponensekből?

**Teszt kritérium:** Hogyan ellenőrizhető, hogy a ciklus kész? (konkrét, eldönthető állítás)
```

### Validáció

Mielőtt hozzáfűzöd a `specs/roadmap.md`-hez, ellenőrizd:

1. **Nincs-e átfedés** meglévő ciklusokkal? (ugyanaz a viselkedés nem szerepel már?)
2. **Tesztelhető-e önállóan?**
3. **Vertikális-e?** (nem csak egy réteg)
4. **Nem túl nagy-e?** Ha igen, javasold a bontást, és kérj döntést.
5. **Előfeltételek pontosak-e?** (a hivatkozott ciklusok valóban szükségesek?)

Ha bármelyikre "nem": javítsd vagy kérdezz rá, mielőtt hozzáfűzöd.

### Hozzáfűzés és lezárás

1. Fűzd hozzá az új ciklus leírását a `specs/roadmap.md` végéhez, `---` elválasztóval a meglévők után. **Edge case:** ha a `roadmap.md` utolsó nem-üres sora nem `---`, először szúrj be egy `---`-t, mielőtt az új ciklust hozzáfűznéd — így minden ciklus blokk között garantáltan ott az elválasztó.
2. Mutasd meg a kész ciklus leírást, és kérj megerősítést:
   > *"Hozzáadtam a Cycle NN — [cím] leírást. Ha megerősíted, frissítem a roadmap státuszát `Kész`-re és létrehozom a ciklus könyvtárát."*
3. Ha a felhasználó megerősíti:
   - Állítsd a roadmap státuszát `Kész`-re.
   - Hozd létre a ciklus könyvtárát: `mkdir -p specs/cycle-NN-<cycle-name>/`
   - Készíts git commitot a fázis befejezéséről:
     ```bash
     git add specs/roadmap.md
     git commit -m "cycle-NN: 01-cycles"
     ```
     ahol `NN` az éppen hozzáadott ciklus száma (pl. `cycle-16: 01-cycles`).
   - Jelezd a következő lépést:

     > *"Cycle NN — [cím] hozzáadva. Könyvtár létrehozva: `specs/cycle-NN-<cycle-name>/`*
     >
     > *Következő lépés — spec írás. Használd ezt a parancsot:*
     > ```
     > /bs-write-spec input: @specs/roadmap.md, ciklus: cycle-NN-<cycle-name>
     > ```"*

---

## C. mód — Roadmap rekonstrukció meglévő ciklusokból

### Feladatod

A `specs/` mappában található ciklus mappák alapján hozd létre (vagy írd felül) a `specs/roadmap.md` fájlt. Ez akkor használandó, ha a `specs/roadmap.md` hiányzik, de a `specs/` már tartalmaz ciklusokat.

### Lépések

1. **Ciklusok azonosítása:** Listázd ki a ciklus mappákat (`ls -d specs/cycle-*/`), és rendezd őket szám szerint növekvő sorrendbe.

2. **Spec fájlok beolvasása:** ha sok ciklus van, ne olvasd be egyenként a saját kontextusodba — hívd a `researcher` subagentet (`agents/researcher.md`, Mód B) egy összesített kéréssel: minden `specs/cycle-NN-<name>/spec.md`-hez add vissza a címet (`Cycle NN: cím`), a `Célkitűzés` szekció első mondatát, az érintett komponenseket (a `Komponensek és viselkedés` szekcióból), valamint a `Teszt specifikáció` és `Definition of done` kulcspontjait, táblázatos formában. Ha a `spec.md` nem létezik egy ciklushoz, jelezze ezt is a mappanév alapján (viselkedés: mappanévből következtetve, komponensek: ismeretlen, teszt kritérium: nincs specifikálva). Néhány (2-3) ciklusnál egyszerűbb, ha közvetlenül olvasod be őket.

3. **Roadmap felépítése (piszkozatként):** Építsd fel a `specs/roadmap.md`-t a standard struktúra szerint (`# Fejlesztési Roadmap`, **`Státusz: Piszkozat`**, majd minden ciklus `## Cycle NN — cím` blokkja). **Ne állítsd `Kész`-re automatikusan** — a rekonstrukció felülírhat fontos tervezési állapotot, ezért emberi jóváhagyás kell.

4. **Felhasználói review és megerősítés:** Mutasd meg a rekonstruált roadmapet, és kérj megerősítést:
   > *"A meglévő spec fájlokból [N] ciklust rekonstruáltam a `specs/roadmap.md`-be (jelenleg `Piszkozat`). Kérlek nézd át. Ha rendben van és megerősíted, `Kész`-re állítom és commitolom."*
   > **A válasz végén helyezd el a `specs/roadmap.md` közvetlen, kattintható linkjét.** Ne lépj tovább a megerősítés előtt.

5. **Lezárás (megerősítés után):**
   - Állítsd a roadmap státuszát `Kész`-re.
   - Készíts git commitot:
     ```bash
     git add specs/roadmap.md
     git commit -m "cycle-NN: 01-cycles"
     ```
   - Jelezd: *"A roadmap rekonstrukció kész és commitolva. Folytathatjuk az új ciklus hozzáadásával."*

6. **Átmenet B. módba:** A megerősített rekonstrukció után automatikusan folytasd a **B. mód — Új ciklus hozzáadása** lépéseivel (az `### Előkészítés` ponttól kezdve: a roadmap most már létezik, olvasd be, határozd meg a következő ciklusszámot).
