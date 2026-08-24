---
phase: 01
name: bs-add-cycles
description: "berkispec - 01. Használd az inicializálás után (Phase 01) fejlesztési ciklusok (roadmap) tervezéséhez, meglévők átütemezéséhez vagy új ciklus hozzáadásához — a feladatok logikai, önállóan tesztelhető egységekre bontása. Bemenet: 'conventions.md', opcionálisan egy brainstorm session ('brainstorm: NN' — a '/bs-brainstorm' munkafájljából desztillálja a 'cycle-design-input.md'-t, BS18). A 'specs/roadmap.md'-t hozza létre vagy frissíti 'Kész' státusszal."
prerequisites:
  - "conventions.md létezik"
output:
  - "specs/roadmap.md státusz: Kész"
  - "specs/cycle-NN-<name>/cycle-design-input.md (üres sablon, a felhasználó tölti ki — opcionális, CD1; brainstorm-bemenet esetén feltöltve, BS18)"
  - "specs/cycle-NN-<name>/spec-input-from-prev.md és/vagy plan-input-from-prev.md (csak ha van átadandó infó, IP1)"
prev: bs-init-project  # vagy bs-brainstorm (BS18 — brainstorm-bemenet)
next: bs-write-spec
subagents:
  - "agents/researcher.md"
shared:
  - "shared/git-preflight.md"
  - "shared/parallel-cycles.md"
  - "shared/input-from-prev.md"
---
# 01 — Ciklusok kezelése
<!-- INCLUDE:shared/context-check.md -->

---

Spec driven development-ben fejlesztünk szoftvert. A fejlesztés ciklusokra van bontva. Minden ciklus egy önállóan lefejleszthető, önállóan tesztelhető részegysége a teljes implementációnak.

Ez a folyamat **1. fázisa (0–9)**: 0-init · **1-ciklusok ←** · 2-spec · 3-plan · 4-tasks · 5-analyze · 6-implement · 7-validate · 8-doc-sync · 9-review.

---

## Előfeltétel

1. **`conventions.md` létezés-ellenőrzés:** olvasd be a projekt gyökerében a `conventions.md`-t. Ha nem létezik, STOP — térjenek vissza a `00` projekt inicializálás fázishoz.
2. **Git-preflight (közös leírás):** a 01 **branch-nyitó** fázis — a *teljes* preflight vonatkozik rá (no-VCS kapu + munkafa-ellenőrzés + branch-nyitó preflight: friss, tiszta `main`, illetve resume-felismerés). A tényleges `git switch -c`-t **nem** itt futtatod, hanem a ciklusszám + név meghatározása UTÁN, az adott mód (A/B/C) lezárásában (BD5).

<!-- INCLUDE:shared/git-preflight.md -->

<!-- INCLUDE:shared/parallel-cycles.md -->

> **Branch = ciklus (BD1–BD3).** A ciklus-branch **itt, a 01 fázisban** jön létre `main`-ről (nem a 06-ban), és a 02+ fázisok már ezen dolgoznak. A No-VCS ágon (a `conventions.md` szerint nincs verziókezelő) minden git-lépést kihagysz: csak a `specs/cycle-NN-<name>/` mappa és a roadmap készül el (BI8).

---

## Folytatás megszakított futás után

Ha a 01 fázis félbeszakadt és új sessionban folytatódik:

**Először a git-állapot (BQ3 — idempotencia, csak ha van verziókezelő).** A branch-nyitó preflight (fent) `git branch --show-current`-je ezt már eldönti; itt a következményei:

```
Milyen branch-en vagyunk?
1. main → normál friss flow: a ciklusszám/név után jön a `git switch -c` (BD5).
2. feature branch, ami az AKTUÁLIS ciklus várt branch-neve
   (a roadmap in-progress blokkja / a ciklus mappaneve alapján)
   → ez RESUME: a branch már létrejött. NE hozz új branch-et (`git switch -c` tilos),
     folytasd ezen a branch-en a lenti dokumentum-állapot szerint.
3. feature branch, ami NEM az aktuális ciklusé
   → BD6: figyelmeztetés (a jelenlegi branch merge/PR a `## Merge stratégia` szerint),
     majd kérd a felhasználót, hogy váltson main-re — ne válts automatikusan.
```

**Ezután a dokumentum-állapot:**

```
1. Létezik specs/roadmap.md?
   → Olvasd be a státuszát és tartalmát.
   → Ha félig megírt (van [ ] nyitott kérdés, vagy hiányos ciklus blokk):
     folytasd az első hiányos résztől, ne kezdd újra.

2. Létrehozott, de hiányos ciklusmappa (mkdir megtörtént, de a roadmap
   blokk vagy a commit hiányzik)?
   → Fejezd be a hiányzó lépést (roadmap blokk, validáció, megerősítés, commit).
     Ha a branch is hiányzik (VCS mellett), előbb a branch-nyitó preflight szerint
     állj friss main-re, majd hozd létre a branch-et, és rajta fejezd be.

3. Félbeszakadt C. mód (az aktuális ciklus roadmap-blokkja hiányos)?
   → Folytasd az adott ciklus blokkjának pótlását a ciklus feature branch-én
     (BQ5/BQ6 — per-ciklus javítás, nem teljes rekonstrukció).
```

---

## Mód detektálás — induláskor

> **0. lépés — brainstorm-bemenet (BS18).** Ha a hívás egy brainstorm sessionre utal (`brainstorm: 04`, *„a 04-es brainstormból"*), **először** a *„Brainstorm-bemenet (BS18)"* szekció szerint olvasd be a munkafájlt, és csak utána folytasd a mód detektálással. A brainstorm nem váltja ki a mód-választást — a bemenetet adja hozzá.

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
     > *"Találtam [N] meglévő ciklust a `specs/` mappában, de nem találom a `specs/roadmap.md` fájlt. Melyik ciklussal dolgozunk most? Az adott ciklus roadmap-blokkját pótolom (per-ciklus, a ciklus feature branch-én) — a többi ciklus a saját branch-én / a merge-elt main-roadmap-ben él."*
     - **Egy konkrét ciklus** → Kövesd a **C. mód — Egy ciklus roadmap-blokkjának pótlása** lépéseit arra az egy ciklusra (BQ5/BQ6). Ha utána új ciklust is fel akarsz venni, folytasd a **B. móddal**.
     - **Új ciklus felvétele** → Folytasd közvetlenül a **B. móddal**: az új ciklust hozzáadod, a roadmap többi része üres/hiányos maradhat.

---

## Ciklusszám meghatározása (közös — BQ2)

A következő ciklusszám (`NN`) meghatározásához **nem elég** a main `roadmap.md` + `ls specs/`, mert létezhet olyan ciklus, ami csak egy még nem merge-elt feature branch-en él. Ezért:

- **Verziókezelő mellett:** `NN = max(main `roadmap.md`/`ls specs/` ciklusszámai, a feature branch-ekben lévő `cycle-NN` számok) + 1`.
  - Feature-branch-scan: `git branch -a --list '*cycle-*'` (a `conventions.md` szerinti branch-prefixet, pl. `feature/cycle-*`, is lefedve), majd a branch-nevekből `cycle-(\d+)` kinyerése.
  - Frissesség: a branch-nyitó preflight `git pull`-ja a remote-ot is frissítette, így a scan friss `git branch -a` állapotot lát — külön `git fetch` jellemzően nem kell.
- **No-VCS ágon** (nincs verziókezelő): a scan kimarad, `NN = max(`ls specs/`/`roadmap.md` számai) + 1`.

Ez a formula minden módban (A/B/C) érvényes, ahol új ciklusszám kell — ne ütközz párhuzamosan nyitott, még nem merge-elt ciklusokkal.

---

## A. mód — Teljes roadmap tervezés

### Git-branch az A. módban (BQ1) — a tervezés ELŐTT

A teljes roadmap az **első ciklus feature branch-én** készül és commitolódik. Verziókezelő mellett, **mielőtt bármit a `specs/roadmap.md`-be írnál**:

1. Kérdezd meg a felhasználót, **mi legyen az első ciklus neve** (kebab-case). Ha nem ad nevet, a **default** branch: `feature/cycle-01` (név-suffix nélkül); ha ad, `feature/cycle-01-<name>`.
2. Futtasd a branch-nyitó preflightet (fent: friss, tiszta `main`, illetve resume-felismerés — BD6/BQ3/BQ4).
3. Hozd létre a branch-et: `git switch -c feature/cycle-01[-<name>]` (a `conventions.md` `## Git és branching konvenciók` **Branch-elnevezési stratégia** szerinti prefixszel; alapból `feature/`).
4. **A továbbiakban (interjú, roadmap-írás, commit) minden ezen a branch-en történik** — a `main` védett marad (BD4).

**No-VCS ágon** (nincs verziókezelő) ez a lépés kimarad: a roadmap közvetlenül készül, branch/commit nélkül (BI8).

### Feladatod

A HLD/LLD alapján határozd meg a fejlesztési ciklusokat, és írd le őket a `specs/roadmap.md` fájlba.

**A legfontosabb elv: vertikális vágás.** Ne réteg szerint vágj (pl. "Cycle 1: adatbázis, Cycle 2: API"), hanem feature szerint — minden ciklus végén legyen egy tesztelhető, end-to-end működő viselkedés.

**Ne írj spec-et, plan-t vagy implementációt.** Ez a lépés csak a ciklushatárokat és a sorrendet határozza meg.

### Output

**Fájl:** `specs/roadmap.md` a projekt gyökerében. Ha a `specs/` mappa nem létezik, hozd létre.

### Fázisok közötti átadás (`*-input-from-prev.md`) — IP1

A ciklustervezés során rendszeresen elhangzik olyan információ, ami **nem a roadmap-be való** (a roadmap-bejegyzés rövid: viselkedés, érintett komponensek, előfeltételek, teszt kritérium), de a következő fázisoknak értékes. **Ne dobd el** — írd a ciklus mappájában lévő megfelelő átadó fájlba:

- **`spec-input-from-prev.md`** — a **02-write-spec**-nek: viselkedési részlet, konkrét hibaeset, adatmező, üzleti szabály, elfogadási feltétel, amit az interjú során a felhasználó elmondott, de a roadmap-bejegyzésbe nem fér bele.
- **`plan-input-from-prev.md`** — a **03-write-plan**-nek: technikai megkötés, meglévő komponens- vagy infrastruktúra-információ, ismert integrációs korlát, amit a felhasználó itt mondott el.

**A. módban** (teljes roadmap tervezés) a ciklus mappája még nem feltétlenül létezik — ilyenkor a tételt annak a ciklusnak a mappájába írd, amelyikre vonatkozik, a mappát létrehozva. Ha a tétel **több ciklust** érint, az nem ide tartozik: a `roadmap.md` megfelelő ciklus-bejegyzéseibe menjen.

<!-- INCLUDE:shared/input-from-prev.md -->

### Információgyűjtés — iteratív interjú

Mielőtt meghatározod a ciklusokat, elegendő információra van szükséged. Értékeld, mi áll rendelkezésre:

**Szükséges minimum:**
- A rendszer célja és határai egyértelműek
- A főbb komponensek és aktorok azonosítva vannak
- A kulcs user flow-k (belépéstől a főbb műveletekig) ismertek
- A külső rendszerekkel való integrációs pontok ismertek

**Ha bármely pont hiányzik:** tegyél fel **egy** célzott kérdést, várd meg a választ, majd értékeld újra. Addig ismételd, amíg a minimum teljesül. Ne tegyél fel egyszerre több kérdést.

> **Ha van brainstorm-bemenet (BS18):** a minimum jó része már megvan a munkafájlban (`## 1. Cél`, `## 2. Feltárt tények`, `## 4. Döntések`) — **azt ne kérdezd újra**. Az interjút a `## 5. Nyitott kérdések` kipipálatlan tételeivel kezdd, egyszerre eggyel.

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
- Hozd létre az **első ciklus** könyvtárát (`mkdir -p specs/cycle-01-<name>/`, ha még nem létezik) és benne a `cycle-design-input.md` sablont a *„Ciklus design input (CD1)"* szekció szerint. A többi ciklus mappáját **ne** hozd létre előre — azok a saját 01-futásukkor (B. mód) kapják meg a sajátjukat.
- Készíts git commitot a fázis befejezéséről — **a már létrehozott `feature/cycle-01[-<name>]` branch-en** (BD4/BQ1), nem `main`-en:
  ```bash
  git add specs/roadmap.md specs/cycle-01-<name>/cycle-design-input.md
  git commit -m "cycle-NN: 01-cycles"
  ```
  ahol `NN` az éppen tervezett első ciklus száma (pl. `cycle-01: 01-cycles`). **No-VCS ágon a commit kimarad** (BI8).
- Jelezd: *"A roadmap kész. Folytathatjuk az 1. ciklus spec fázisával (02). Létrehoztam a `specs/cycle-01-<name>/cycle-design-input.md` fájlt — ide leírhatod a saját szavaiddal az 1. ciklus specifikációját. Kitöltése nem kötelező, de ha írsz bele, a `bs-write-spec` figyelembe fogja venni."* — **a válasz végén helyezd el a `cycle-design-input.md` kattintható linkjét.**

---

## B. mód — Új ciklus hozzáadása

### Előkészítés

1. Olvasd be a `specs/roadmap.md`-t (ha létezik) — kontextus és ciklusszám meghatározáshoz. Ha nem létezik, hozd létre az alap struktúrával (`# Fejlesztési Roadmap\n\n**Státusz:** Kész`). _(A roadmap tényleges írása/commitja a ciklus feature branch-én történik — lásd „Branch létrehozása".)_
2. Határozd meg az új ciklusszámot a **„Ciklusszám meghatározása (BQ2)"** szerint — a main `roadmap.md`/`ls specs/` **és** a feature branch-ek `cycle-NN` számainak maximuma + 1 (VCS mellett). Ez a lépés még az induló branch-en (jellemzően `main`-en) fut.
3. Jelezd a felhasználónak:
   > *"Meglévő ciklusok: [N db — cycle-01-xxx, ...]. Következő ciklusszám: [NN]."*

### Információgyűjtés

1. Tegyél fel **egy** kérdést:
   > *"Mi az új ciklus célja? Röviden írd le, milyen viselkedést szeretnél megvalósítani."*

   > **Ha van brainstorm-bemenet (BS18):** ezt a kérdést **hagyd ki** — a célt a munkafájl `## 1. Cél / kérdés` és `## 6. Javasolt ciklus-vágás` szekciója már megválaszolja. Ehelyett foglald össze 2-3 sorban, mit értettél belőle, és **azt** hagyasd jóvá. Csak azt kérdezd meg, amire a fájlban nincs válasz (jellemzően a `## 5. Nyitott kérdések` nyitott tételei).

   > **Flow-méret ellenőrzés (a cél leírása után, a névjavaslat előtt):** Mérlegeld, hogy a feladat **nem túl kicsi-e** a teljes, többfázisú ciklushoz. Ha a cél 3-4 lépésben, egyetlen menetben megoldható — tipikusan **konfiguráció összeállítása/módosítása, egyszerűbb script megírása, kisebb javítás vagy lokális finomhangolás** —, akkor a teljes `02→…→09` flow túlméretezett. Ilyenkor **állj meg, és javasold az egyszerűsített flow-t**, mielőtt ciklust hoznál létre:
   >
   > > *„Ez a feladat elég kicsinek tűnik a teljes fejlesztési ciklushoz (külön spec/plan/tasks + analyze/validate/review). Javaslom helyette az egyszerűsített flow-t (`/bs-quick-flow`): `spec.md` → `task.md` → implementáció, néhány lépésben. Mehetünk azzal, vagy mégis teljes ciklust szeretnél?"*
   >
   > A döntés a Felhasználóé: ha a teljes ciklust kéri, folytasd itt; ha az egyszerűsítettet, irányítsd át a `/bs-quick-flow` skillhez.

2. Ha megérkezett a cél leírása, készíts egy javaslatot a ciklus nevére **kebab-case** formátumban, tömören, a viselkedést tükrözve (pl. `performance-load-test`, `token-exchange`, `oidc-login`). Kérdezd rá:
   > *"A cél alapján a javasolt név: `[javasolt-név]`. Ez lesz a branch és a mappa neve is (pl. `cycle-NN-[javasolt-név]`). Megfelelő, vagy inkább mást szeretnél?"*

Ha a név nem felel meg, kérd a felhasználó saját javaslatát, azt használd.

Ha a leírás vagy a név alapján valamit tisztázni kell (pl. meglévő ciklusokkal való átfedés, függőség), tegyél fel még **egy** kérdést. Ne tegyél fel egyszerre többet.

### Branch létrehozása (BD5/BI1) — a név jóváhagyása UTÁN, a roadmap-írás ELŐTT

A név jóváhagyása után, **mielőtt** a `specs/roadmap.md`-be írnál vagy mappát hoznál létre (BD5 sorrend), verziókezelő mellett:

1. Győződj meg róla, hogy a branch-nyitó preflight (fázis eleje) friss, tiszta `main`-re vitt — vagy hogy ez egy resume ugyanezen a ciklus-branch-en (BQ3). Resume esetén nincs teendő, folytatsz a meglévő branch-en.
2. `main`-en állva hozd létre és válts a ciklus branch-ére: `git switch -c feature/cycle-NN-<name>` (a `conventions.md` `## Git és branching konvenciók` **Branch-elnevezési stratégia** szerinti prefix/formátum; alapból `feature/`). A **mappanév** ettől függetlenül tisztán `cycle-NN-<name>` (BD3).
3. Innentől minden (roadmap-írás, `mkdir`, commit) **ezen a branch-en** történik; a `main` védett marad (BD4).

**No-VCS ágon** (nincs verziókezelő) ez kimarad: a roadmap-írás és a mappa-létrehozás közvetlenül történik, branch/commit nélkül (BI8).

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
3. Ha a felhasználó megerősíti (a `git switch -c` ekkor már megtörtént — lásd „Branch létrehozása"):
   - Állítsd a roadmap státuszát `Kész`-re.
   - Hozd létre a ciklus könyvtárát: `mkdir -p specs/cycle-NN-<cycle-name>/` (a **mappanév** prefix nélkül, tisztán `cycle-NN-<name>` — BD3).
   - Hozd létre a **ciklus design input sablont** a mappában: `specs/cycle-NN-<cycle-name>/cycle-design-input.md` — lásd a lenti *„Ciklus design input (CD1)"* szekciót.
   - Készíts git commitot a fázis befejezéséről — a **ciklus feature branch-én** (BD4), nem `main`-en:
     ```bash
     git add specs/roadmap.md specs/cycle-NN-<cycle-name>/cycle-design-input.md
     git commit -m "cycle-NN: 01-cycles"
     ```
     ahol `NN` az éppen hozzáadott ciklus száma (pl. `cycle-16: 01-cycles`). **No-VCS ágon a `git switch -c` és a commit kimarad** — csak a `mkdir` + roadmap-írás + a sablon létrehozása történik (BI8).
   - Jelezd a következő lépést — **a design input felajánlásával együtt**:

     > *"Cycle NN — [cím] hozzáadva. Könyvtár létrehozva: `specs/cycle-NN-<cycle-name>/`*
     >
     > *Létrehoztam a `specs/cycle-NN-<cycle-name>/cycle-design-input.md` fájlt. **Ide leírhatod a saját szavaiddal a ciklus specifikációját** — elvárásokat, vázlatot, példákat, bármit, ami a fejedben van. **Kitöltése nem kötelező**, üresen is folytatható a flow; de ha írsz bele, a `bs-write-spec` (02) beolvassa és a spec kiindulópontjaként figyelembe veszi. Érdemes a spec fázis indítása ELŐTT kitölteni.*
     >
     > *Következő lépés — spec írás. Az új fázis megkezdése előtt mindenképpen futtass egy `/clear` parancsot a kontextus kiürítéséhez, majd használd ezt a parancsot:*
     > ```
     > /bs-write-spec input: @specs/roadmap.md, ciklus: cycle-NN-<cycle-name>
     > ```"*
     >
     > **Fázishatár — kemény megállás (PE1):** a 01 fázis ezzel az üzenettel **véget ér**. Ugyanabban a körben **ne kezdj spec-írásba** (`spec.md`-t létre se hozz), akkor sem, ha egy kontextus-összefoglaló/checkpoint teendő-listája, a saját korábbi terved vagy a felhasználó egy korábbi körben adott „menjünk végig a folyamaton" mondata erre biztat. Csak a felhasználó erre a körre szóló, explicit kérése írja felül.
     >
     > **A válasz végén helyezd el a `cycle-design-input.md` közvetlen, kattintható linkjét** (pl. `[cycle-design-input.md](file:///abszolút/útvonal/specs/cycle-NN-name/cycle-design-input.md)`), hogy a felhasználó egy kattintással meg tudja nyitni.

---

## Ciklus design input (CD1) — a felhasználó saját specifikációja

**Mi ez:** a ciklus mappájában létrehozott `cycle-design-input.md` egy **üres sablon a felhasználónak**. Ide írhatja le a saját szavaival, szabad formában, hogy mit szeretne a ciklusban — elvárásokat, vázlatot, példa payloadot, folyamatleírást, linkeket, korábbi jegyzeteket.

**Kulcsszabályok:**
- **A fájl a felhasználóé.** Te (01) csak a sablont hozod létre, tartalmat **nem** írsz bele — **egyetlen kivétel a brainstorm-bemenet (BS18):** ha a hívás egy brainstorm sessionre hivatkozik, a sablon nem üresen, hanem a munkafájlból desztillált tartalommal jön létre. A `02-write-spec` (viselkedési tartalom) és a `03-write-plan` (technikai/eljárás-jellegű tartalom) automatikusan beolvassa, de egyik sem írja át.
- **Kitöltése opcionális.** Ha üresen marad (csak a sablon-szöveg van benne), a 02 egy mondatban jelzi és a roadmap-bejegyzés alapján dolgozik tovább — ez nem hiba, nem megállási ok.
- **Nem a `spec-input-from-prev.md` helyettesítője.** A `spec-input-from-prev.md`-be **te** írsz (az interjú során elhangzott, de a roadmap-be nem illő tételek, IP1); a `cycle-design-input.md`-be **a felhasználó** ír, a fázis lezárása után, saját tempójában.

**A létrehozandó sablon tartalma (szó szerint, `NN` az aktuális ciklusszámra behelyettesítve — pl. `# cycle 25 design input from user`):**

```md
# cycle NN design input from user

> **Ez a fájl a Tiéd.** Ide írhatod le a saját szavaiddal, hogy mit szeretnél ebben a ciklusban:
> elvárások, viselkedés-vázlat, példa kérés/válasz, folyamatleírás, korlátok, hivatkozások, jegyzetek.
>
> **Kitöltése nem kötelező** — üresen hagyva a flow változatlanul működik.
> Ha viszont írsz ide, két fázis is automatikusan beolvassa:
> - `bs-write-spec` (02) — a **viselkedési** tartalmat, a `spec.md` kiindulópontjaként (a `roadmap.md` bejegyzése mellett);
> - `bs-write-plan` (03) — a **technikai/eljárás-jellegű** tartalmat (parancsok, hostok, komponensek, korlátok) a `plan.md`-hez.
>
> Formátum nincs megkötve: folyó szöveg, felsorolás, táblázat, kódrészlet — bármi jó.
> Ezt a fájlt egyik fázis sem írja felül.

<!-- Írj ide. -->
```

---

## Brainstorm-bemenet (BS18) — a `/bs-brainstorm` session átvétele

**Mi ez:** a `/bs-brainstorm` segédparancs a spec előtti feltáró ötletelést a `.bs-brainstorm/brainstorm-NN-<slug>.md` munkafájlba perzisztálja (tények forrással, alternatívák trade-offokkal, döntések, nyitott kérdések, javasolt ciklus-vágás). Ha a felhasználó erre hivatkozik, ez a **hivatalos híd** a brainstorm és a flow között: a nyers munkafájl helyi és gitignore-olt, a belőle desztillált `cycle-design-input.md` viszont commitba kerül.

**Mikor aktiválódik:** ha a hívás sorszámmal utal egy sessionre — `/bs-add-cycles brainstorm: 04`, *„a 04-es brainstormból hozd létre a design inputot"*. Ha nem, **minden változatlan** (a `cycle-design-input.md` üres sablonként jön létre a CD1 szerint).

### Lépések

1. **Fájl megkeresése:** `ls -1 .bs-brainstorm/brainstorm-04-*.md`.
   - **Nincs ilyen sorszám:** ne találgass és ne dolgozz nélküle — listázd a létező sessionöket (sorszám + slug), és kérdezd meg, melyikre gondolt.
   - **Nincs `.bs-brainstorm/` mappa sem:** jelezd egy sorban, hogy nem találod (a mappa gitignore-olt, tehát más gépen nem is létezik), és kérdezd meg, folytassuk-e brainstorm-bemenet nélkül.
2. **Teljes beolvasás.** A munkafájl rövid; olvasd be egészben, ne szemelvényezz.
3. **Interjú-bemenet.** A `## 6. Javasolt ciklus-vágás` szekció a **roadmap-javaslat kiindulása** (egy egység = egy ciklus-jelölt), a `## 1. Cél` a ciklus célja, a `## 2. Feltárt tények` az érintett komponensek. **Amit a fájl megválaszol, azt ne kérdezd meg újra** — a felhasználó már egyszer végigbeszélte.
4. **A nyitott kérdések a te kérdéseid.** A `## 5. Nyitott kérdések` **kipipálatlan** tételei nyitottak: ezekből lesznek az interjú célzott kérdései (egyszerre **egy**), illetve — ha a ciklus scope-ján kívülre esnek — a roadmap `## Nyitott kérdések` szekciójának bejegyzései. **Soha ne vedd őket eldöntött ténynek.**
5. **A ciklus-vágás javaslat nem parancs.** A brainstorm javaslata jó kiindulás, de a vertikális vágás elveit (lásd a fenti szekciót) és a `## Validációs ciklus` ellenőrzését **ugyanúgy le kell futtatni** rá. Ha a javasolt vágás sérti az elveket (nem önállóan tesztelhető, túl nagy, körkörös függőség), mondd ki, és javasolj módosítást — a döntés a felhasználóé.

### A `cycle-design-input.md` feltöltése

A CD1 sablon fejléce és a magyarázó blokk **változatlanul** kerül a fájlba (a felhasználó ezután is ír bele); a `<!-- Írj ide. -->` helyére viszont a desztillátum jön:

- **Mit vigyél át:** a `## 4. Döntések` (ez a fő tartalom), a ciklust érintő `## 3. Alternatívák` közül a **megtartott** opció leírása, és a `## 2. Feltárt tények` azon sorai, amelyek erre a ciklusra vonatkoznak (a `fájl:sor` horgonyokkal együtt — azok navigációs értéke a 02/03 fázisban is megmarad).
- **Mit NE vigyél át:** a `## 7. Napló`-t, a lezárt/elvetett szálakat, a session meta-információit, és a `## 6. Javasolt ciklus-vágás` teljes listáját (abból csak **ennek** a ciklusnak a szelete tartozik ide — a többi a roadmap dolga).
- **Több ciklusra bomló brainstorm:** minden ciklus **csak a saját szeletét** kapja meg. A ciklusokon átívelő, közös döntések a roadmap ciklus-blokkjába, illetve a `spec-input-from-prev.md`-be kerülnek (IP1), nem ismétlődnek minden design inputban.
- **Hangnem:** leíró, az implementálónak szólva. A brainstormban szereplő beszélgetés-nyomokat (*„megbeszéltük, hogy…"*, *„te azt kérdezted…"*) fogalmazd át döntésre: *„A tanúsítványokat központi store kezeli; a komponensek csak referenciát kapnak."*
- **Ne hivatkozz a `.bs-brainstorm/` útvonalra** a commitált dokumentumban: a mappa gitignore-olt, a link más gépen és PR-ban halott. A származás jelzésére egy útvonal nélküli sor elég: `> Az NN. brainstorm session döntéseiből desztillálva.`
- **Ha a fájl már létezik és tartalmas** (a felhasználó már írt bele): **ne írd felül.** Fűzd a desztillátumot a végére egy `## Brainstorm-desztillátum` alcím alá, és szólj róla egy sorban.

### Lezárás

A szokásos CD1 visszajelzés helyett jelezd, hogy a fájl **nem üres**:

> *„Létrehoztam a `specs/cycle-NN-<name>/cycle-design-input.md` fájlt, és feltöltöttem a NN. brainstorm session döntéseivel. **Olvasd át** — ez lesz a `bs-write-spec` (02) kiindulópontja. Bátran javítsd, bővítsd vagy húzz ki belőle; a fájl a Tiéd, egyik fázis sem írja felül."*

A válasz végén itt is helyezd el a `cycle-design-input.md` kattintható linkjét.

---

## C. mód — Egy ciklus roadmap-blokkjának pótlása/javítása (per-ciklus — BQ5/BQ6)

### Mi változott (BQ6)

A klasszikus „**teljes** roadmap-rekonstrukció az összes ciklusmappából egyetlen `Piszkozat` dokumentumba" forgatókönyv **megszűnt**. A **branch = ciklus** modellben a teljes main-roadmap a ciklusok **merge-elésével** áll össze, nem egy nagy rekonstrukciós lépésben. Ezért a C. mód mostantól **csak az adott ciklus** roadmap-blokkját pótolja/javítja, **az adott ciklus feature branch-én** (BQ5) — így a védett `main` + a „branch = ciklus" invariáns megmarad, és nincs több-ciklust-egyszerre-commitoló rekonstrukciós branch. A C→B automatikus átmenet is megszűnik.

### Mikor fut

Akkor, ha az **aktuális ciklus** roadmap-blokkja hiányzik vagy hibás (a `specs/roadmap.md` nem tartalmazza, vagy hiányosan tartalmazza az adott `cycle-NN-<name>` blokkját), miközben a ciklus mappája már létezik. **Csak azzal az egy ciklussal** dolgozol — nem a teljes `specs/`-fel.

### Lépések

1. **Ciklus azonosítása:** melyik ciklusról van szó (a felhasználó megadta / a folyamatban lévő ciklus mappaneve). Ez az EGY ciklus, amit pótolsz.

2. **Branch (BQ5):** verziókezelő mellett dolgozz az adott **ciklus feature branch-én** — a B. mód „Branch létrehozása" mintája szerint: ha még nincs branch, a branch-nyitó preflight (friss, tiszta `main`) után `git switch -c feature/cycle-NN-<name>`; ha ez egy resume és már a ciklus branch-én vagy (BQ3), folytasd ott, `git switch -c` nélkül. **No-VCS ágon a git kimarad.**

3. **A hiányzó/hibás blokk pótlása:** ha a `specs/roadmap.md` nem létezik, hozd létre az alap struktúrával (`# Fejlesztési Roadmap\n\n**Státusz:** Kész`). Az adott ciklus `## Cycle NN — cím` blokkját a standard struktúra szerint pótold/javítsd, a ciklus `spec.md`-jéből (ha létezik). Ha az input sok, a `researcher` subagenttel (`agents/researcher.md`, Mód B) kérdezd le tömören (cím, `Célkitűzés` első mondata, érintett komponensek, `Teszt specifikáció`/`Definition of done` kulcspontjai) — a fő kontextust kímélve. **Csak ezt az egy blokkot** érintsd, a roadmap többi részét ne írd felül.

4. **Validáció + megerősítés:** mutasd meg a pótolt/javított blokkot, és kérj megerősítést:
   > *"A(z) `cycle-NN-<name>` roadmap-blokkját pótoltam/javítottam a `specs/roadmap.md`-ben. Kérlek nézd át. Ha rendben van és megerősíted, commitolom a ciklus branch-én."*
   > **A válasz végén helyezd el a `specs/roadmap.md` közvetlen, kattintható linkjét.** Ne lépj tovább a megerősítés előtt.

5. **Lezárás (megerősítés után):** commit a **ciklus feature branch-én** (BD4):
   ```bash
   git add specs/roadmap.md
   git commit -m "cycle-NN: 01-cycles"
   ```
   **No-VCS ágon a commit kimarad.** Ezután a ciklus folytatható a 02 spec fázissal (vagy, ha új ciklust is fel akarsz venni, a B. móddal).