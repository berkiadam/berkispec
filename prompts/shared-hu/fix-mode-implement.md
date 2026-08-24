<!-- Forrás-jegyzet: a 06-implement skill Fix-mód szekciója, kiemelve, hogy az
     implement-fixer és a review-fixer subagent prompt build-time beemelhesse
     (BD14/b, D13). Így a fixereknek NEM kell beolvasniuk a teljes
     06-implement.md-t — ami a célprojektben nem is létező útvonal volna.
     Egy helyen szerkeszd. -->
## Fix-mód (a 07 önjavító hurkának belépője)

> **Mikor aktív:** ezt a szekciót a `07-validate` önjavító hurka indítja egy fixer-subagenten keresztül — **nem** a normál implementáció. Két wrapper van, azonos mechanikával és **azonos markerrel** (`[validate-loop]`), csak a bemeneti szekció más:
> - **teszt-/Sonar-/DoD-hiba:** az `implement-fixer` subagent → bemenet a `tasks.md` `## <sec:validation_fixes>` taskjai;
> - **kódreview-finding:** a `review-fixer` subagent → bemenet a `tasks.md` `## <sec:review_fixes>` taskjai (a `test-report/code-review.md` `MF-NN` findingjai).
>
> Mindkét esetben egy **konkrét hibalista** célzott javítása a feladat, nem a teljes ciklus újra-implementálása.
> **Skill-beolvasás nem kell (D13):** a fix-módhoz szükséges összes szabály ebben a promptban van. **Fix-módban ne olvasd be a teljes fázis-skillt** (`06-implement`): felesleges, a célprojektben nincs is ilyen útvonal, és a teljes fázis újrafuttatására csábít, holott a feladat egy szűk, célzott javítás.

A fix-mód egy **szűkített belépő:** a megadott teszt-/Sonar-/DoD-hibákat javítod célzottan, **nem implementálod újra a ciklust** (2.2). (Ellenkező esetben egy olcsóbb LLM hajlamos elölről kezdeni a fázist — ez tilos.) A 06 normál végrehajtási és minőségi szabályai (a `[CHECK]` zöldre futtatása, kódkomment-frissítés, deep module) a javított részekre továbbra is érvényesek — **beleértve a `[CHECK]` futásnaplót is**: a fix-módban futtatott ellenőrzéseket ugyanúgy vezeted a `test-report/implement/check-log.md`-be, a **<field:f_mode>** oszlopban `validate-loop` jelöléssel. Így a javító körök `[CHECK]`-jei is nyomot hagynak, és a hurok utólag rekonstruálható.

> **Amit a fix-módban NEM írsz:** a `test-report/validate/` kör-mappákat — azok az orchestrátoré (07) és a `test-runner`-é. Te csak a `test-report/implement/check-log.md`-t bővíted (a kódon és a `tasks.md` javító-szekcióján felül).

### Bemenet
A hívótól függően a `tasks.md` végén lévő javító-szekció elvégzetlen `[GREEN]`/`[CHECK]` taskjai, a szekció elején lévő prerequisite hivatkozásokkal együtt:
- **teszt-/Sonar-/DoD-ág:** `## <sec:validation_fixes>` (a 07 vette fel a konkrét teszt-/Sonar-hibákból); prerequisite:
  - `specs/cycle-NN-<cycle-name>/test-report/validation-report.md` (a `# <sec:validation_history>` a hibák részleteivel),
  - ha Sonar hibázott: **az adott kör** Sonar-riportja — `specs/cycle-NN-<cycle-name>/test-report/validate/round-NN/sonar-report.md`. A konkrét kör-számot a szekció prerequisite-hivatkozása adja meg (TR5); **ne keresgélj más körök mappájában**, és ne a `test-report/` gyökerében — ott nincs Sonar-riport.
- **review-ág:** `## <sec:review_fixes>` (a 07 vette fel a `<status:must_fix>` findingokból); prerequisite:
  - `specs/cycle-NN-<cycle-name>/test-report/code-review.md` (a findingok `MF-NN` azonosítóval).
- A `tasks.md` aktuális állapota (`<status:ready_for_implement> [validate-loop]` státusz).

### Fix-mód ↔ normál implement elhatárolása (2.2)
- **Fókusz:** kizárólag az aktív javító-szekció taskjai (`## <sec:validation_fixes>` VAGY `## <sec:review_fixes>`) — a konkrét megbukott tesztek / Sonar-hibák / nem teljesült DoD-pontok / `<status:must_fix>` findingok javítása.
- **Nem teljes újra-implementáció:** a már zöld, lezárt taskokat (`[x]`) ne futtasd újra és ne írd át. Csak a hibalistára dolgozol.
- A 06 már ismeri mindkét belépést (lásd „Két forrásból érkezhet visszalépés ide" — a `## <sec:validation_fixes>` és a `## <sec:review_fixes>` ág); a fix-mód erre épül, nem duplikálja.

### <field:f_status> (auto, `[validate-loop]` marker)
A hurok a `tasks.md` státuszát a markerével nyitotta vissza (`<status:ready_for_implement> [validate-loop]`) — ugyanez a marker a teszt- és a review-javításnál is. Amíg a marker jelen van, **automatikusan** lépteted a státuszt, megerősítés-kérés nélkül (eltérően a normál „megerősítés a státuszváltás előtt" szabálytól) — a markert végig megtartva:
- javítás közben: `<status:implement_in_progress> [validate-loop]`;
- ha az aktív javító-szekció minden taskja `[x]` és a csoportzáró `[CHECK]` zöld: `<status:ready_for_validate> [validate-loop]`.

A marker fel- és levételét az orchestrátor (`07-validate`) kezeli; te csak a státusz-értéket lépteted.

### ⚠ Anti-„csalás" garde (VD3 / RD4 — kötelező)

**A fix-mód a KÓDOT igazítja a teszthez / Sonarhoz / DoD-hoz / a review-findinghoz — SOHA nem fordítva.** A teszt, a DoD és a reviewer `<status:must_fix>` findingja a **szerződés**, azt a fix-mód nem gyengítheti és nem némíthatja el.

**TILOS** a zöld/tiszta eredmény bármilyen kikényszerítése a szerződés megkerülésével:
- teszt assertion gyengítése, lazítása, vagy elvárt érték a kódból visszamásolása;
- teszt `skip`/`xfail`/kikommentezése/törlése;
- hardcode-olt „elvárt" érték, amely csak a tesztet zöldíti, de a valós viselkedést nem valósítja meg;
- a `spec.md` <sec:definition_of_done> pont leszállítása vagy átfogalmazása, hogy könnyebben teljesüljön;
- **(review-ág, VD3)** a `<status:must_fix>` finding **kozmetikai elnémítása** a gyökérok javítása nélkül (lint-suppress komment, a kifogásolt kód álcázása), vagy a `test-report/code-review.md` finding törlése/átfogalmazása javítás nélkül.

**Ha úgy ítéled meg, hogy egy hibát CSAK a szerződés (teszt/DoD/spec) megváltoztatásával vagy a finding elnémításával lehetne zöldre/tisztára vinni** — az **nem kód-fix**. **STOP**: ne nyúlj a szerződéshez, hanem add vissza az orchestrátornak a visszatérési összefoglalóban **eszkalációs jelzéssel** (lásd lent). Ez a felfelé menekülő ág bemenete — a 07 VD5 ága (a tervezési/szerződés-kérdést a 03/02 fázisban kell rendezni, nem itt).

### Visszatérési összefoglaló (az orchestrátornak)
A futásod végén adj tömör összefoglalót a hívó orchestrátornak (`07-validate`):
- **Elvégzett javítások:** mely javító-taskokat zártad le, és hogyan (hibánként/findingonként egy sor) — milyen kódváltozással lett zöld/kész.
- **Eszkalációs jelzés (ha van):** ha valamelyik hibát csak a szerződés (teszt/DoD/spec) módosításával vagy a finding elnémításával lehetne zöldre/tisztára vinni (VD3/RD4 tiltja) → jelezd egyértelműen: *„ESZKALÁCIÓ: [item] tervezési/szerződés-hibának tűnik — csak a szerződés módosításával vagy a finding elnémításával lenne zöld; nem javítottam."* Add meg, miért.
- **A `tasks.md` aktuális státusza** (a `[validate-loop]` markerrel).

A kódot és a `tasks.md` aktív javító-szekcióját (`## <sec:validation_fixes>` / `## <sec:review_fixes>`) te írod; a `validation-report.md`-t és a `test-report/code-review.md`-t **nem** — azok az orchestrátoré.
