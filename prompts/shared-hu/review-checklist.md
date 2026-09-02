<!-- Forrás-jegyzet: ezt a szekciót KÉT hely emeli be (build-time INCLUDE):
     az agents-hu/reviewer.md (a subagent-ág) ÉS a skills-hu/07-validate.md
     reviewer-fallback blokkja (RV-FB1). A fallback definíció szerint nem olvassa
     a subagent promptját, ezért a szempontlistát FIZIKAILAG meg kell kapnia.
     Egy helyen szerkeszd. -->
## Ellenőrzési szempontok

- **Konvenciók betartása:** Fájl- és változónevek, importálási szabályok, architektúra rétegek tisztasága a `conventions.md` szerint.
- **Kódminőség:** Felesleges kódismétlések (DRY), túl bonyolult függvények, típusbiztonság (pl. TypeScript/Python típusok).
- **Scope fegyelem:** A kód nem tartalmaz-e a `plan.md`-ben nem szereplő, tervezetlen funkciókat (scope creep).
- **Spec eltérés:** A megvalósított viselkedés megfelel-e a `spec.md` követelményeinek? Eltérés a specifikációtól `<status:must_fix>`.
- **Hibakezelés:** Megfelelő hibaelkapás, specifikus hibakódok használata a specifikáció szerint.
- **Teszt lefedettség:** A tesztek tényleg az új logikát fedik-e le, a regressziós tesztek nem sérültek-e.
- **Üres teszt-törzs (TB1) — eldönthető kérdés:** Van-e a diffben olyan **új vagy módosított teszt-függvény**, amelynek törzsében **nincs a rendszer válaszához vagy állapotához kötött asszertáció** (csak `assert True`, `pass`, konstans összehasonlítás, vagy kizárólag a mock saját visszatérési értékének ellenőrzése)? Ha igen, az **<status:must_fix>** — a teszt zöld, de nem bizonyít semmit. Ez a pont **eldöntendő, nem mérlegelendő**: a törzsben vagy van ilyen asszertáció, vagy nincs. _(Miért kemény: egy éles ciklusban `assert True` vázak kerültek a tesztfájlba — a suite `X passed`-et jelentett, a DoD bizonyítékot kapott, és a validálás `PASS`-ra zárt anélkül, hogy bármit ellenőriztünk volna.)_
- **Elavult kommentek és docstringek (VD12):** a diffben módosított vagy újonnan létrehozott fájlokban a kommentek, JSDoc/TSDoc/docstring leírások **naprakészek-e** a végrehajtott változásokhoz képest (átnevezés, megváltozott paraméter, megváltozott hibakód, megszűnt ág)? Egy komment, amely a kód **korábbi** viselkedését írja le, félrevezetőbb, mint a hiánya. Besorolás: **`<status:must_fix>`**, ha a komment/docstring **aktívan hazudik** a jelenlegi viselkedésről (rossz paraméter, rossz visszatérési érték, megszűnt hibakód); **`<status:suggestion>`**, ha csak hiányos vagy pontatlanul fogalmaz. _(A 07 orchestrátor szándékosan **nem** olvassa végig a módosított fájlokat — ez a te dolgod, mert a diffet amúgy is végignézed.)_

## <status:must_fix> vs <status:suggestion> — a határvonal

A reviewer döntése bináris a 07-validate orchestrátor felé: blokkolja-e a PASS-t vagy sem.

- **<status:must_fix> = a validálás PASS-át blokkolja** (és ezzel a merge-et is). Ide tartozik: biztonsági rés, specifikáció-eltérés (a kód nem azt csinálja, amit a `spec.md` ír), konvenció-megszegés (`conventions.md`-vel ellentétes), hibás vagy hiányzó hibakezelés, sérült regressziós teszt, scope creep.
- **<status:suggestion> = nem blokkol.** Ide tartozik: refaktorálási ötlet, elnevezési tipp, tisztasági javaslat, opcionális egyszerűsítés. Pozitív hangnemű megjegyzés is ide kerülhet (pl. „ez jól sikerült, érdemes máshol is alkalmazni").

Kétség esetén: blokkol-e a hiba a helyes/biztonságos működésben? Ha igen → <status:must_fix>. Ha csak szebb/tisztább lenne → <status:suggestion>.
