<!-- Forrás-jegyzet: ezt a szekciót a 03-write-plan.md skill ÉS a hozzá tartozó
     fix-mode-* shared fájl is beemeli (build-time INCLUDE). Egy helyen szerkeszd. -->
## Minőségellenőrzés — plan lezárása előtt

Mielőtt \`Task írásra kész\` státuszra váltasz, tedd fel magadnak:

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
  | 10 | regressziós érintettség | a plan `Regressziós érintettség` táblája kitöltve vagy explicit „nincs" |

- **🔴 Környezeti koordináták szekció kész? (KO1)** — A `Környezeti koordináták` szekció **létezik és ki van töltve**: (a) minden komponensnél base URL, port(ok), health endpoint, **szó szerinti indító és leállító parancs**, repo-útvonal/image; (b) minden szükséges REST hívásnál ige + teljes URL + fejlécek + **konkrét request body** + elvárt válasz + a kinyerendő mező, a **token-beszerzést is beleértve**, másolható `curl` példával; (c) **minden teszt- és API-user felsorolva a jelszavával/credentialjével** (dev-hatókörű érték konkrétan, klaszter/registry/VPN/IAM/éles credential **pointerként**, TC5); (d) minden további fejlesztéshez/teszteléshez kellő paraméter (azonosítók, scope, client-id, namespace, timeout); (e) a hálózati/hozzáférési előfeltételek. **Placeholder és üres cella tilos** — ami hiányzik vagy elavult, az `Knn` kérdés a `plan-questions.md`-ben; ami nem értelmezhető, ott `—` áll. Ha egy koordináta a spec-ben, a `test-conventions.md`-ben vagy a beszélgetésben szerepel, de itt nem, a minőségellenőrzés **SIKERTELEN**.
- **Artefaktum-hang (AV1)?** — Nincs a plan-ben skill-hangú meta-utasítás (`🔴`, `[!CAUTION]`, „Tilos…", „kötelező…", „menj végig…")? Ami szabályból származik, az **döntésként** szerepel (pl. „az image tagje futásonként egyedi: `v1-<UTC időbélyeg>`"), az indoklás pedig a `Kockázatok és döntési pontok` szekcióban.
- **🔴 Eldöntetlen alternatíva tilalma.** A plan **nem tartalmazhat választást**: nincs benne „`X` **vagy** `Y`", „esetleg", „vagy az új …", két port/URL/azonosító ugyanarra a dologra, két lehetséges elvárt válasz. A terv **végrehajtási utasítás**, nem mérlegelés — ha valóban két opció van, az **`plan-questions.md` kérdés**, és a plan csak a **döntött**, konkrét változattal zárható le. (Tipikus előfordulás: teszt-azonosítók `data-testid` értékei, mock-portok, régi/új elemnevek átnevezéskor.)
- **Hivatkozott script/fájl létezik vagy tervezve van?** — Menj végig **minden** fájlon és scripten, amit a plan futtatni akar (`Ellenőrzési stratégia` parancsai, teszt-lépések, E2E indítás, `[CHECK]` jellegű ellenőrzések): mindegyik vagy **már létezik a repóban**, vagy szerepel a `Tervezett módosítások` közt **új fájlként**. Egy futtatandó, de sehol nem létrehozott script biztos bukás a végrehajtáskor.
  - **Belépési pont egyezése:** az ellenőrző parancs által futtatott **állomány** és a `Teszt specifikáció`-ban tervezett **teszt-artefaktum** ugyanaz legyen. Tipikus hiba: a terv egy `..._test.py` fájlt hoz létre, az ellenőrző parancs viszont egy `....sh` wrappert futtat, amit senki nem tervez meg — ilyenkor vagy a wrappert is fel kell venni a `Tervezett módosítások` közé (a projekt konvenciója szerinti névvel), vagy a parancsnak közvetlenül a megtervezett fájlt kell hívnia. **A kettő nem lóghat külön.**
- **Ígért teszt ↔ teszteset ↔ végrehajtási sorrend konzisztencia.** Ha a plan **bárhol szövegesen tesztelést ígér** — jellemzően a `Kockázatok és döntési pontok` „kezelés" mondataiban (pl. *„a fallback logikát egységteszttel igazoljuk"*) —, akkor annak (a) van konkrét **tesztesete** a `Teszt specifikáció`-ban, és (b) megjelenik a **`Végrehajtási sorrend`**-ben is. Ígéret teszteset nélkül lefedettségi rés.
- **Kereszt-dokumentum konzisztencia.** Ugyanaz az erőforrás **mindenhol ugyanazzal** az URL-lel, porttal, azonosítóval és útvonallal szerepel — a plan-en belül **és** a spec-hez képest is. Ha egy útvonal/host a spec-ben és a plan-ben eltér (vagy a plan két helyén más), az **egyikük hibás**: állítsd meg magad, és tisztázd (`plan-questions.md`), ne hagyd, hogy egy `[CHECK]` később bukjon el rajta.
- **`docs-generated/` nincs a tervezett módosítások közt? (DS4)** — A generált doksik a 08-doc-sync tulajdonai; ha bekerültek, töröld őket a `Tervezett módosítások`-ból. **Meglévő** komponens README-je szintén nem tervezhető be (az is a 08 dolga) — **csak új komponens első README-je** kerülhet ide.
- **Osztott környezetet érintő destruktív művelet teljes? (jóváhagyás + immutable azonosító + rollback)** — Ha a terv közös klasztert/registryt/adatbázist módosít, mindhárom megvan? Felülírt image-tag vagy konfiguráció esetén **nincs mihez visszaállni** — ez blokkoló hiányosság.
- **🔴 Minden integrációs és E2E tesztnél szerepel a lépésenkénti híváslánc?** — Menj végig **tesztesetenként**: minden lépésnél ott van a HTTP ige, a teljes végpont, a fejlécek (az `Authorization` típusa is), a **konkrét request body**, az elvárt státusz és a kulcs válasz-mezők? Browser E2E-nél a felhasználói interakció **és** a hozzá tartozó hálózati hívás **és** a látható eredmény? **Ha bárhol csak utalás van korábbi ciklusra, meglévő tesztfájlra vagy a spec szekvenciadiagramjára, a minőségellenőrzés SIKERTELEN** — fejtsd ki a lépéseket, majd futtasd újra.
- **Hivatkozás-feloldás megtörtént?** — Nincs a plan-ben olyan mondat, amely **scriptre, eljárásra, meglévő tesztre vagy külső API-ra hivatkozik** anélkül, hogy a belőle szükséges konkrétumot (parancs, URL, payload-séma, paraméter) kiírná? Ha a bemenet magas absztrakciós szinten fogalmazott, **te lementél a forrásig**?
- **Önteszt:** *„Ha valaki csak a `plan.md`-t és a `tasks.md`-t kapja meg — spec, kódbázis-ismeret és a beszélgetés nélkül —, le tudja fejleszteni és tesztelni?"* Ha bármelyik ponton vissza kellene kérdeznie vagy találgatnia, a plan hiányos.
- **Nincs tiltott megfogalmazás?** — „lásd a spec-et", „a szokásos módon", „a megfelelő végpontra", „futtasd a `build.sh`-t", „a korábbi ciklus paramétereivel", `<ide jön …>`, `TODO`.
- Hiányzik még valami a plan-ből?
- Van bármi, ami nem egyértelmű vagy kétértelmű?
- A végrehajtási sorrend valóban függőségek alapján rendezett?
- Minden érintett fájl szerepel a tervezett módosításokban?
- **Dokumentációk frissítése:** Minden, a változtatások által érintett leírás, README és diagram (pl. `.drawio` fájl) fel van-e tüntetve a tervezett módosítások között?
- **Kommentek és docstringek:** A tervezett módosítások figyelembe veszik-e a forráskódban lévő kommentek és leírások frissítését az új elnevezéseknek/működésnek megfelelően?
<!-- INCLUDE:shared/path-format.md -->
- A `Teszt specifikáció` szekció tartalmaz teszteseteket minden érintett komponenshez?
- **Szekció-ID-k (PID1):** minden végrehajtható terv-szekció visel egyedi `[P-…]` ID-t, a korábbiak változatlanok, leltár-szekció nem kapott ID-t?
- **Scope-kapu (SC1):** a `Fordított lefedettség` tábla kitöltve, minden plan-képességnek van spec-forrása (vagy Out of scope / kérdés)? Az első oszlop a szekció `[P-…]` azonosítóját viseli, a második a `DoD-NN`-t — ezen fut a 05 lefedettségi lánca (`S3`).
- **Konfiguráció-életút (KF1):** minden új/módosított paraméterhez van sor a táblában, **minden futtatási módra** kitöltve (lokális, teszt, konténer/compose, dev deploy) + a „ha hiányzik" viselkedés?
- **Horgony-verifikáció:** minden `fájl:hely` és „ez a szimbólum/asszertáció ott van" állítás Grep/Read-del visszaigazolva?
- **Érték-józanság:** portok, időegységek, URL-séma↔port, verziók, útvonalak átnézve (tipikus elgépelés: `433` a `443` helyett)?
- **A tesztek futtathatók a plan-ből egyedül? (TP3)** — Benne van a **token-beszerzés** teljes hívása (a konkrét teszt-userrel, a kinyerendő mezővel), a **stack indítása** (parancs + health check + takarítás), az **egyedi komponens** build–push–deploy–ellenőrzés–**rollback** lánca, a **seed** és a **hálózati előfeltétel** — mindez futtatható parancsként, sorrendben? Ha egy előfeltétel egy **korábbi ciklusban** épült ki és nincs a `test-conventions.md`-ben, áthoztad a korábbi ciklus planjéből (TP3/a)?
- **A kapu-konfiguráció együtt mozog? (GC1)** — Ha a ciklus a riport-struktúrát, a riport-parancsokat, a Sonar-konfigot, a teszt-parancsokat, a portokat vagy a merge-stratégiát érinti: a `conventions.md` **érintett szekciója szerepel a `Tervezett módosítások`-ban, konkrét új tartalommal**, és a 04 tud rá taskot írni? (A `specs/test-conventions.md` frissítése ezt **nem** helyettesíti — a TR3 kapu a `conventions.md`-t olvassa.)
- **A kidolgozott spec-artefaktumok CSONKÍTÁS NÉLKÜL jöttek át? (KX3)** — Menj végig a spec kód-blokkjain (OpenAPI/JSON/YAML/SQL/payload), hibamátrixain és többlépéses teszt-forgatókönyvein: mindegyik **szó szerint, teljes egészében** szerepel a plan-ben? Nincs összevont lépés, mezőnév-felsorolásra cserélt payload, prózára cserélt tábla, sem „lásd a spec-et" / „a többi eset hasonlóan" hivatkozás? **A plan érintett szekciója nem rövidebb a spec forrás-szekciójánál** — ha mégis, meg tudod nevezni, hova került át a többi?
- **A spec tesztesetei átjöttek? (TP1)** — A `Spec-lefedettség` tábla kitöltve, és a spec `Teszt specifikáció` minden esete + minden `DoD-NN` pont leképződik legalább egy plan-tesztesetre (vagy indoklással szerepel)? A spec szimbolikus koordinátái mellé bekerült a **konkrét érték**, a viselkedés-leírás mellé a **konkrét hívás** (ige, végpont, fejléc, body, elvárt válasz)? Ami itt kimarad, az a validáláskor nem fut le.
- **A `cycle-design-input.md` feldolgozva? (CD1)** — Ha a fájl létezik és van benne érdemi tartalom, beolvastad, és minden technikai/eljárás-jellegű tételének van követhető sorsa: **szó szerint, önhordóan** beépült a `plan.md`-be (nem hivatkozásként!), vagy átkerült a `tasks-`/`validate-input-from-prev.md`-be, vagy `Knn` kérdés lett, vagy a 02-be visszairányított spec-hiányosság. A fájlt **nem** írtad át?
- **A `plan-input-from-prev.md` minden tétele lezárva? (IP1)** — Ha a fájl létezik, nem maradhat benne `[ ]` tétel: mindegyik vagy beépült a `plan.md`-be (a megjegyzés mutatja, hova), vagy explicit indokkal elvetett.
- **A plan-ből kihagyott, de értékes infó át lett adva? (IP1)** — Task-szintű előkészítő lépés a `tasks-input-from-prev.md`-be, validálás-specifikus futtatási előfeltétel a `validate-input-from-prev.md`-be került?
- **A plan önhordó a beemelt teszt-receptekre (TC1/a)?** — Nincs olyan tesztelési lépés, amely a `specs/test-conventions.md` beolvasása nélkül nem végrehajtható (a `test-runner` azt a fájlt nem olvassa). Nincs placeholder, nincs adat helyett hivatkozás.
- Minden teszteset Elvárt kimenet oszlopa tartalmaz HTTP státuszt és errorCode-ot (ahol a spec hibamátrixa definiálja)?
- A unit tesztek a végrehajtási sorrendben az implementáció ELŐTT szerepelnek?
- Minden szükséges schema artifact azonosítva és a táblázatban szerepel?
- **Adatbázis módosítások:** Ha a ciklus sémaváltozást/új entitást hoz be, meg van-e tervezve és dokumentálva a migrációs és rollback (visszaállítási) forgatókönyv?
- Minden schema artifact státusza `Reviewed`? (Ha van `Review Required`, a plan nem zárható le.)
- **Constitution Check (SK4):** minden plan-döntés (tech stack, naming, struktúra, teszt eszköz, merge stratégia, biztonság) összhangban van a `conventions.md`-vel?
  - **Kis eltérés** (pl. egy elnevezés finomítása): vedd fel a `plan-questions.md`-be, és kérdezz rá a felhasználótól.
  - **Súlyos eltérés** (alapvetően ütközik a konvenciókkal): **STOP**, vissza a `02` vagy `00` fázishoz a konvenció felülvizsgálatára.

Ha bármelyikre nem teljesül a feltétel (vagy hiányzik valami), egészítsd ki a plan-t, mielőtt lezárod.

---

## Lezárási kapu — teszt-önhordóság, környezet-felkészítés és scope (TP2)

> **Ezt a listát (a `/`-jelű alpontokkal együtt) a `Task írásra kész` státusz ELŐTT, tételesen le kell futtatnod, és a válaszodban ki kell írnod a kipipált listát.** Nem „érzésre" — minden pontnál nevezd meg, **hol** teljesül (szekció, `TC-ID`), vagy hogy miért nem értelmezhető ebben a ciklusban. **Egyetlen `[ ]` maradék esetén a plan nem zárható le** — javítsd, és futtasd újra a listát.

```
<!-- INCLUDE:lang/quality-check-plan.md#TP2-lezarasi-kapu -->
```

**Az önteszt a 7–8. ponthoz:** *„Friss gépen, csak ezt a plant olvasva lefut a teszt?"* — ha bárhol azt kellene mondani, hogy „ezt már felhúztuk korábban", a plan hiányos: a `test-runner` minden futásnál a nulláról indul, és a korábbi ciklusok planjeit nem olvassa.

**Miért kapu ez, és nem checklist-sor:** a tapasztalat szerint a leggyakoribb 03-hiba nem a rossz terv, hanem az, hogy a **spec tesztesetei egyszerűen nem jutnak el a plan-be** — az ágens „túl részletesnek" ítéli őket a tervhez, és a 04-re vagy az implementációra hagyja. Csakhogy a `test-runner` sem a spec-et, sem a `test-conventions.md`-t nem olvassa: ami itt kimarad, az a validáláskor **nem fut le**, és a hiány csak a 07-ben derül ki, plan-hiányként (TR4) — a teljes ciklust visszadobva ide.
