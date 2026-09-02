<!--
  A `quality-check-plan` PROJEKT-NYELVI blokkjai (9.4 kiemelés).
  Ezt a fájlt a telepítő build-time emeli be az INCLUDE markerek helyére, a
  választott PROJEKT-nyelv (`PROJECT_LANG`) szerint; a marker alakja
  `lang/quality-check-plan.md#<horgony>`.
  A blokkok SZÓ SZERINT kerültek ide — ne fogalmazd át, ne egységesítsd.
  Az ANCHOR sorok NEM részei a beemelt szövegnek, csak határolók (8.9).
  FIGYELEM: ebbe a vezető jegyzetbe ne kerüljön komment-lezáró szekvencia.
-->

<!-- ANCHOR:TP2-lezarasi-kapu -->
[ ] 1. A `Spec-lefedettség` tábla kitöltve: a spec `Teszt specifikáció` MINDEN esete
       és MINDEN `DoD-NN` pontja legalább egy plan-tesztesetre képződik le (vagy
       indoklással szerepel). Nincs kihagyott sor.
[ ] 1/b. WY1 — CÉL MINDEN BEJEGYZÉSHEZ: a `Tervezett módosítások` MINDEN `[P-…]`
       szekciója visel `**<field:f_purpose>:**` sort, amely a változás UTÁNI
       viselkedést és a megszüntetett bajt mondja ki, és megnevezi a spec-forrást
       (`DoD-NN` vagy követelmény). Nincs olyan bejegyzés, ahol a cél a módosítás
       megismétlése vagy üres általánosság.
[ ] 2. A `specs/test-conventions.md` minden érintett receptjét (RXX/IXX) FIZIKAILAG
       bemásoltam (parancsok, URL-ek, payloadok, credential-pointerek) — nem csak
       hivatkozom rájuk. A plan a test-conventions.md nélkül is végrehajtható.
[ ] 3. Minden integrációs és E2E teszteset lépésről lépésre tartalmazza: HTTP ige ·
       teljes végpont · fejlécek (az Authorization TÍPUSÁVAL) · konkrét request body ·
       elvárt HTTP státusz · kulcs válasz-mezők. Browser E2E-nél: interakció +
       hálózati hívás + látható eredmény.
[ ] 3/b. TS7 — SPEC-TESZTESET → `TS-NN`: a spec MINDEN tesztesete önálló `TS-NN`
       blokká konvertálódott a `Teszt-forgatókönyvek` szekcióban, és a
       `Spec-lefedettség` tábla minden sora megnevez legalább egy `TS-NN`-t
       (vagy a nem tesztelhető eset indoklását). A spec teszt-szekciójának
       címsor-szerkezete NEM került át párhuzamos, saját nevű szekcióként.
[ ] 3/c. TA1 — TESZT-ARTEFAKTUM ADATLAP: minden `#### <tesztfájl path>` fejléc alatt
       ott a `<field:f_what_it_checks>` (mit ellenőriz a fájl — állításként, a
       `DoD-NN`-nel), a `Futtatás` (keret + az egy fájlra szűkített, szó szerint
       futtatható parancs), a `Fixture-ök és tesztadat` (útvonallal és
       tartalommal — az új fájlok a `Tervezett módosítások`-ban is) és a
       `Teszt-esetek` (teszt-függvény neve → `TC-ID` / `TS-NN`) sor.
[ ] 3/d. TD7 — MINDEN TESZTESET MEGMONDJA, MIT ELLENŐRIZ: a `TS-NN` blokkok
       `<field:f_what_we_test>` sora, a unit-táblák `<field:f_what_it_checks>`
       oszlopa és minden számozott integrációs/E2E flow a viselkedést ÁLLÍTÁSKÉNT
       mondja ki, a `DoD-NN`-nel — a cím megismétlése („konkurencia-teszt") nem
       cél.
[ ] 3/d/b. TI1 — TESZT-AZONOSÍTÓK: a forgatókönyvek `TS-01`-től, a teszt-tábla
       esetei `TC-01`-től futnak, ciklus-szinten folytonosan, hézag nélkül; nincs
       `TC-<modul>-01` alakú, fájlonként újrakezdett számozás. A `tasks.md` és a
       07 naplója ezekre hivatkozik.
[ ] 3/e. TS8 — `.http` ALAK: minden REST-lépést tartalmazó `TS-NN` blokkban van
       `.http` kódblokk is, a `curl`-lel azonos értékekkel, teljes fejlécekkel és
       body-val (a kézi tesztterv ebből szerel össze).
[ ] 3/f. PH1 — FUTTATÁSI FÁZIS: a gépi futtatási tábla `<field:f_phase>` oszlopa
       minden sorban érvényes érték (`<status:phase_implement>` /
       `<status:phase_validate>` / `<status:phase_both>`; az üres cella
       mindkettő), és legalább egy kategória fut a `<status:phase_validate>`
       fázisban. `DoD-NN`-t bizonyító teszt nincs `<status:phase_implement>`-only.
[ ] 4. Minden hibaághoz szerepel a HTTP státusz, az errorCode (ahol a spec
       hibamátrixa definiálja) és a response body mintája.
[ ] 5. Nincs a teszt-szekcióban hivatkozás a lépések HELYÉN: „a cycle-XX mintájára",
       „mint a meglévő tesztben", „a spec szekvenciadiagramja szerint", „a szokásos
       fejlécekkel".
[ ] 6. Minden teszteset futtatható belépési pontja (script/tesztfájl) létezik a
       repóban VAGY szerepel a `Tervezett módosítások` közt új fájlként, és az
       `Ellenőrzési stratégia` parancsa pontosan ezt hívja.
[ ] 7. KÖRNYEZET-FELKÉSZÍTÉS (TP3): a plan tartalmazza szó szerinti parancsként a
       token-beszerzést (user és S2S külön, ha kell), a stack indítását +
       health checket + leállítást, az egyedi komponens (plugin/SPI/custom image)
       build–push–deploy–ellenőrzés–rollback láncát, a seedet és a hálózati
       előfeltételeket — a végrehajtási sorrendjükkel együtt.
[ ] 7/b. KO1 — KÖRNYEZETI KOORDINÁTÁK: a `Környezeti koordináták` szekció megvan
       és hiánytalan: MINDEN komponens base URL-je, portja(i), health endpointja,
       szó szerinti indító és leállító parancsa; MINDEN szükséges REST hívás
       példája (ige · teljes URL · fejlécek · konkrét body · elvárt válasz ·
       kinyert érték), a token-beszerzést is beleértve; MINDEN teszt- és API-user
       a JELSZAVÁVAL/credentialjével (dev-hatókörű érték konkrétan, klaszter/
       registry/VPN/IAM/éles credential pointerként — TC5); minden további
       paraméter (azonosítók, scope, client-id, namespace, timeout); a hálózati
       és hozzáférési előfeltételek. Placeholder és üres cella nincs; ami nem
       értelmezhető, ott `—` áll. Az `analyze-gate-check.py` `C6` checkje 0.
[ ] 8. Amit a teszt futtatása igényel, de sem a `test-conventions.md`-ben, sem ebben
       a planben nincs meg, azt a KORÁBBI CIKLUS planjéből áthoztam (TP3/a,
       researcher subagenttel, literál értékekkel, provenance-szal) — vagy
       `plan-questions.md` kérdés lett belőle. Nincs „ezt az előző ciklusban már
       megcsináltuk" típusú néma előfeltétel.
[ ] 8/c. GC1 — KAPU-KONFIGURÁCIÓ: ha a ciklus kapu-olvasott konvenciót érint
       (riport-artefaktum/útvonal-alap, Sonar, teszt-parancs, port, merge),
       a `conventions.md` érintett szekciója a `Tervezett módosítások`-ban van,
       konkrét új tartalommal. A `test-conventions.md` nem helyettesíti.
[ ] 8/b. KX3 — CSONKÍTÁS-MENTESSÉG: a spec MINDEN kidolgozott artefaktuma
       (OpenAPI/JSON/YAML/SQL blokk, teljes payload, hibamátrix, többlépéses
       teszt-forgatókönyv) szó szerint, hiánytalanul a plan-ben van. Nincs
       összevont lépés, nincs mezőnév-felsorolásra cserélt payload, nincs
       „lásd a spec-et" hivatkozás. A plan érintett szekciója nem rövidebb a
       spec forrás-szekciójánál.
[ ] 9. SCOPE-KAPU (SC1): a `Fordított lefedettség` tábla kitöltve, az első
       oszlopban `[P-…]` azonosítóval (a 05 lefedettségi lánca ezen fut) — minden
       plan-képességhez van spec-forrás (követelmény vagy DoD-NN), vagy explicit
       Out of scope, vagy nyitott kérdés. Spec-forrás nélküli képesség nincs.
[ ] 10. HORGONY-VERIFIKÁCIÓ: minden konkrét `fájl:hely` / „ez a szimbólum ebben a
       fájlban van" / „ez az asszertáció ebben a tesztfájlban van" állítást
       Grep/Read paranccsal VISSZAIGAZOLTAM. Emlékezetből vagy analógiából írt
       attribúció nincs.
[ ] 11. ÉRTÉK-JÓZANSÁG: átnéztem a plan MINDEN konkrét értékét — portok
       (80/443/8080/8443/6379/5432 elgépelés: `433`, `44`, `8O80`), időegység
       (ms vs s), URL-séma ↔ port egyezés (`https://` ↔ 443), verzió/tag,
       fájlútvonal. Ami gyanús, azt a forrásból ellenőriztem.
[ ] 12. SZEKCIÓ-ID (PID1): minden végrehajtható terv-szekció címe visel egyedi
       `[P-…]` azonosítót, és a korábban már kiadott ID-k VÁLTOZATLANOK (fix-módban
       különösen: ID átnevezése tilos, mert a tasks.md rá hivatkozik). Leltár- és
       összefoglaló szekció NEM kapott ID-t.
