<!-- Forrás-jegyzet: ezt a szekciót a 03a-write-code-plan.md skill ÉS a plan-fixer
     agent emeli be (build-time INCLUDE). Egy helyen szerkeszd. A teszt-oldali párja a
     quality-check-plan-test.md (D7). -->
## Minőségellenőrzés — a kód-terv lezárása előtt

Mielőtt `<status:ready_for_test_plan>` státuszra váltasz, tedd fel magadnak:

- **🔴 ÖNHORDÓSÁG-LELTÁR — menj végig tételesen.** Minden sorra vagy „megvan, konkrétan", vagy „erre a ciklusra nem értelmezhető" a válasz. „Majd az implementáló kitalálja" **nem** elfogadható válasz:

  | # | Kell-e a plan-ben? | Ellenőrzés |
  |---|---|---|
  | 1 | érintett fájlok **teljes útvonala** | nincs „a megfelelő modulban" jellegű utalás |
  | 2 | függvény-/osztálynevek, **szignatúrák, interfészváltozás** | a hívó oldal is tudja, mit hív és mit kap |
  | 3 | adatszerkezetek **konkrét mezőkkel**, példa request/response | nem csak mezőnevek felsorolása — **tényleges payload** |
  | 4 | hibaágak: feltétel → státusz + errorCode + body | minden spec-beli hibaesethez van megfelelője |
  | 5 | konfiguráció: env-változó **neve ÉS értéke**, hol állítódik | nincs „konfigurálandó" önmagában |
  | 6 | külső integráció: URL, port, realm/kliens/scope, teszt-user, példa `curl` | a hívás **átmásolható és lefuttatható** |
  | 7 | futtatható parancsok **szó szerint** (build, deploy, indítás, teszt) | nincs „futtasd a `build.sh`-t" jellegű utalás |
  | 8 | végrehajtási sorrend + előfeltételek | mi mitől függ, mi kell előtte |
  | 9 | migráció és rollback, ha sémaváltozás van | — |
- **🔴 <sec:environment_coords> szekció kész? (KO1)** — A `<sec:environment_coords>` szekció **létezik és ki van töltve**: (a) minden komponensnél base URL, port(ok), health endpoint, **szó szerinti indító és leállító parancs**, repo-útvonal/image; (b) minden szükséges REST hívásnál ige + teljes URL + fejlécek + **konkrét request body** + elvárt válasz + a kinyerendő mező, a **token-beszerzést is beleértve**, másolható `curl` példával; (c) **minden teszt- és API-user felsorolva a jelszavával/credentialjével** (dev-hatókörű érték konkrétan, klaszter/registry/VPN/IAM/éles credential **pointerként**, TC5); (d) minden további fejlesztéshez/teszteléshez kellő paraméter (azonosítók, scope, client-id, namespace, timeout); (e) a hálózati/hozzáférési előfeltételek. **Placeholder és üres cella tilos** — ami hiányzik vagy elavult, az `Knn` kérdés a `plan-questions.md`-ben; ami nem értelmezhető, ott `—` áll. Ha egy koordináta a spec-ben, a `test-conventions.md`-ben vagy a beszélgetésben szerepel, de itt nem, a minőségellenőrzés **SIKERTELEN**.
- **Artefaktum-hang (AV1)?** — Nincs a plan-ben skill-hangú meta-utasítás (`🔴`, `[!CAUTION]`, „Tilos…", „kötelező…", „menj végig…")? Ami szabályból származik, az **döntésként** szerepel (pl. „az image tagje futásonként egyedi: `v1-<UTC időbélyeg>`"), az indoklás pedig a `<sec:risks_and_decisions>` szekcióban.
- **🔴 Eldöntetlen alternatíva tilalma.** A plan **nem tartalmazhat választást**: nincs benne „`X` **vagy** `Y`", „esetleg", „vagy az új …", két port/URL/azonosító ugyanarra a dologra, két lehetséges elvárt válasz. A terv **végrehajtási utasítás**, nem mérlegelés — ha valóban két opció van, az **`plan-questions.md` kérdés**, és a plan csak a **döntött**, konkrét változattal zárható le. (Tipikus előfordulás: teszt-azonosítók `data-testid` értékei, mock-portok, régi/új elemnevek átnevezéskor.)
- **Hivatkozott script/fájl létezik vagy tervezve van?** — Menj végig **minden** fájlon és scripten, amit a plan futtatni akar (`<sec:verification_strategy>` parancsai, teszt-lépések, E2E indítás, `[CHECK]` jellegű ellenőrzések): mindegyik vagy **már létezik a repóban**, vagy szerepel a `<sec:planned_changes>` közt **új fájlként**. Egy futtatandó, de sehol nem létrehozott script biztos bukás a végrehajtáskor.
  - **Belépési pont egyezése:** az ellenőrző parancs által futtatott **állomány** és a `<sec:test_specification>`-ban tervezett **teszt-artefaktum** ugyanaz legyen. Tipikus hiba: a terv egy `..._test.py` fájlt hoz létre, az ellenőrző parancs viszont egy `....sh` wrappert futtat, amit senki nem tervez meg — ilyenkor vagy a wrappert is fel kell venni a `<sec:planned_changes>` közé (a projekt konvenciója szerinti névvel), vagy a parancsnak közvetlenül a megtervezett fájlt kell hívnia. **A kettő nem lóghat külön.**
- **Kereszt-dokumentum konzisztencia.** Ugyanaz az erőforrás **mindenhol ugyanazzal** az URL-lel, porttal, azonosítóval és útvonallal szerepel — a plan-en belül **és** a spec-hez képest is. Ha egy útvonal/host a spec-ben és a plan-ben eltér (vagy a plan két helyén más), az **egyikük hibás**: állítsd meg magad, és tisztázd (`plan-questions.md`), ne hagyd, hogy egy `[CHECK]` később bukjon el rajta.
- **`docs-generated/` nincs a tervezett módosítások közt? (DS4)** — A generált doksik a 08-doc-sync tulajdonai; ha bekerültek, töröld őket a `<sec:planned_changes>`-ból. **Meglévő** komponens README-je szintén nem tervezhető be (az is a 08 dolga) — **csak új komponens első README-je** kerülhet ide.
- **Osztott környezetet érintő destruktív művelet teljes? (jóváhagyás + immutable azonosító + rollback)** — Ha a terv közös klasztert/registryt/adatbázist módosít, mindhárom megvan? Felülírt image-tag vagy konfiguráció esetén **nincs mihez visszaállni** — ez blokkoló hiányosság.
- **🔴 Minden `[P-…]` bejegyzés megmondja a CÉLT? (WY1)** — A `<sec:planned_changes>` **minden** `[P-…]` szekciója visel `**<field:f_purpose>:**` sort: mit akarunk elérni (a változás UTÁNI viselkedés), miért (a megszüntetett hiányosság vagy hiba), és melyik spec-forrásból (`DoD-NN` vagy követelmény — ugyanaz, ami a `<sec:reverse_coverage>` táblában áll ehhez az ID-hoz). **A módosítás megismétlése nem cél** („bevezetjük a `getX()` metódust"), és a fájlnév sem („frissítjük a configot"). Ha egy bejegyzéshez nem tudsz célt írni, az vagy scope-szivárgás (nincs spec-forrása), vagy `plan-questions.md` kérdés.
- **Hivatkozás-feloldás megtörtént?** — Nincs a plan-ben olyan mondat, amely **scriptre, eljárásra, meglévő tesztre vagy külső API-ra hivatkozik** anélkül, hogy a belőle szükséges konkrétumot (parancs, URL, payload-séma, paraméter) kiírná? Ha a bemenet magas absztrakciós szinten fogalmazott, **te lementél a forrásig**?
- **Nincs tiltott megfogalmazás?** — „lásd a spec-et", „a szokásos módon", „a megfelelő végpontra", „futtasd a `build.sh`-t", „a korábbi ciklus paramétereivel", `<ide jön …>`, `TODO`.
- Hiányzik még valami a plan-ből?
- Van bármi, ami nem egyértelmű vagy kétértelmű?
- Minden érintett fájl szerepel a tervezett módosításokban?
- **Dokumentációk frissítése:** Minden, a változtatások által érintett leírás, README és diagram (pl. `.drawio` fájl) fel van-e tüntetve a tervezett módosítások között?
- **Kommentek és docstringek:** A tervezett módosítások figyelembe veszik-e a forráskódban lévő kommentek és leírások frissítését az új elnevezéseknek/működésnek megfelelően?
<!-- INCLUDE:shared/path-format.md -->
- **Szekció-ID-k (PID1):** minden végrehajtható terv-szekció visel egyedi `[P-…]` ID-t, a korábbiak változatlanok, leltár-szekció nem kapott ID-t?
- **Scope-kapu (SC1):** a `<sec:reverse_coverage>` tábla kitöltve, minden plan-képességnek van spec-forrása (vagy <sec:out_of_scope> / kérdés)? Az első oszlop a szekció `[P-…]` azonosítóját viseli, a második a `DoD-NN`-t — ezen fut a 05 lefedettségi lánca (`S3`).
- **<sec:config_lifecycle> (KF1):** minden új/módosított paraméterhez van sor a táblában, **minden futtatási módra** kitöltve (lokális, teszt, konténer/compose, dev deploy) + a „ha hiányzik" viselkedés?
- **Horgony-verifikáció:** minden `fájl:hely` és „ez a szimbólum/asszertáció ott van" állítás Grep/Read-del visszaigazolva?
- **Érték-józanság:** portok, időegységek, URL-séma↔port, verziók, útvonalak átnézve (tipikus elgépelés: `433` a `443` helyett)?
- **A kapu-konfiguráció együtt mozog? (GC1)** — Ha a ciklus a riport-struktúrát, a riport-parancsokat, a Sonar-konfigot, a teszt-parancsokat, a portokat vagy a merge-stratégiát érinti: a `conventions.md` **érintett szekciója szerepel a `<sec:planned_changes>`-ban, konkrét új tartalommal**, és a 04 tud rá taskot írni? (A `specs/test-conventions.md` frissítése ezt **nem** helyettesíti — a TR3 kapu a `conventions.md`-t olvassa.)
- **A kidolgozott spec-artefaktumok CSONKÍTÁS NÉLKÜL jöttek át? (KX3)** — Menj végig a spec kód-blokkjain (OpenAPI/JSON/YAML/SQL/payload), hibamátrixain és többlépéses teszt-forgatókönyvein: mindegyik **szó szerint, teljes egészében** szerepel a plan-ben? Nincs összevont lépés, mezőnév-felsorolásra cserélt payload, prózára cserélt tábla, sem „lásd a spec-et" / „a többi eset hasonlóan" hivatkozás? **A plan érintett szekciója nem rövidebb a spec forrás-szekciójánál** — ha mégis, meg tudod nevezni, hova került át a többi?
- **A `cycle-design-input.md` feldolgozva? (CD1)** — Ha a fájl létezik és van benne érdemi tartalom, beolvastad, és minden technikai/eljárás-jellegű tételének van követhető sorsa: **szó szerint, önhordóan** beépült a `plan.md`-be (nem hivatkozásként!), vagy átkerült a `tasks-`/`validate-input-from-prev.md`-be, vagy `Knn` kérdés lett, vagy a 02-be visszairányított spec-hiányosság. A fájlt **nem** írtad át?
- **A `plan-input-from-prev.md` minden tétele lezárva? (IP1)** — Ha a fájl létezik, nem maradhat benne `[ ]` tétel: mindegyik vagy beépült a `plan.md`-be (a megjegyzés mutatja, hova), vagy explicit indokkal elvetett.
- **A plan-ből kihagyott, de értékes infó át lett adva? (IP1)** — Task-szintű előkészítő lépés a `tasks-input-from-prev.md`-be, validálás-specifikus futtatási előfeltétel a `validate-input-from-prev.md`-be került?
- Minden szükséges schema artifact azonosítva és a táblázatban szerepel?
- **Adatbázis módosítások:** Ha a ciklus sémaváltozást/új entitást hoz be, meg van-e tervezve és dokumentálva a migrációs és rollback (visszaállítási) forgatókönyv?
- Minden schema artifact státusza `<status:reviewed>`? (Ha van `<status:review_required>`, a plan nem zárható le.)
- **Constitution Check (SK4):** minden plan-döntés (tech stack, naming, struktúra, teszt eszköz, merge stratégia, biztonság) összhangban van a `conventions.md`-vel?
  - **Kis eltérés** (pl. egy elnevezés finomítása): vedd fel a `plan-questions.md`-be, és kérdezz rá a felhasználótól.
  - **Súlyos eltérés** (alapvetően ütközik a konvenciókkal): **STOP**, vissza a `02` vagy `00` fázishoz a konvenció felülvizsgálatára.
- **🔴 A kód-terv kapuja lefutott, és a nyoma bent van? (GS2/a)** — A lezárás előtt tényleg lefuttattad az `analyze-gate-check.py --plan-code-only`-t, `0`-t adott, és az eredménye **két helyen** látszik: a `plan.md` fejlécének `**<field:f_gate_code>:**` sorában és a fázis-záró válaszod `ANALYZE-GATE: …` sorában? A státusz-mező önbevallás — a `03b` belépő kapuja ugyanezt a kaput **újra lefuttatja** (D5), tehát a valótlan bélyeg egy fázissal később úgyis kiderül.
- **🔴 A teszt-szekciókat NEM te írod.** A `<sec:testing_strategy>`, a `<sec:plan_test_scenarios>`, a `<sec:machine_run_table>`, a `<sec:e2e_infrastructure>`, a `<sec:regression_impact>` és a `<sec:test_specification>` szekciót **meg sem nyitod**, és nem írsz `TS-NN` / `TC-NN` azonosítót. Ha a spec tesztesetei „kikéredzkednek", azok a `03b` bemenetei — a `<sec:reverse_coverage>` táblába felveheted a hozzájuk tartozó sort, a forgatókönyvet nem. **Miért kapu ez:** a fél-kész teszt-szekció **rosszabb az üresnél**, mert a `03b` `TS7`-konverziója egy már meglévő, hibás szerkezetet másolna tovább — pontosan azt a hibát, ami miatt ez a fázis kettéhasadt.

Ha bármelyikre nem teljesül a feltétel (vagy hiányzik valami), egészítsd ki a plan-t, mielőtt lezárod.

---

## Lezárási kapu — a kód-terv önhordósága, koordinátái és scope-ja (TP2-code)

> **Ezt a listát a `<status:ready_for_test_plan>` státusz ELŐTT, tételesen le kell futtatnod, és a válaszodban ki kell írnod a kipipált listát.** Nem „érzésre" — minden pontnál nevezd meg, **hol** teljesül (szekció, `[P-…]` ID), vagy hogy miért nem értelmezhető ebben a ciklusban. **Egyetlen `[ ]` maradék esetén a kód-terv nem zárható le** — javítsd, és futtasd újra a listát.

```
<!-- INCLUDE:lang/quality-check-plan.md#TP2-code -->
```

**Miért kapu ez, és nem checklist-sor:** a `03b` a te kimenetedből dolgozik, és a `TA1` adatlapok, a `TS-NN` hívások és a gépi futtatási tábla **literál értékei** innen jönnek. Egy hiányzó koordináta itt még egy sor; a teszt-tervben már egy egész forgatókönyv találgatásra épül — és a `03b` belépő kapuja (D5) úgyis visszaküld ide.
