<!-- Forrás-jegyzet: ezt a szekciót a 02-write-spec.md ÉS a 03-write-plan.md skill
     (és a hozzájuk tartozó fix-mode-* shared fájlok) is beemelik (build-time
     INCLUDE). Egy helyen szerkeszd. -->
## Teszt-forgatókönyv tervezése — dimenziók és megfigyelési pontok (TD1–TD7)

A környező szabályok (KX2, KX3, TS1–TS6) **megőrzik** a részletet, amit a bemenet tartalmaz — de egyik sem **hoz létre** forgatókönyvet. Ha a bemenet egy mondat („a token megújítása többpéldányos futásnál ne duplikálódjon"), a TS3 kemény padlója egyetlen lépéssel és egyetlen backtickes értékkel is teljesül: formailag kész teszt, ami a viselkedésből semmit nem igazol. Ez a blokk a hiányzó lépés: **kitöltendő kérdésekké** alakítja a teszt-tervezést, hogy ne következtetni kelljen rá.

**Hatókör — melyik fázisban meddig (TD0):** a `<sec:test_specification>` (spec) szekcióban az 1. és 2. lépés **viselkedés-szinten** fut: a dimenziók és a megfigyelési pontok megnevezése kötelező, a koordináta viszont szimbolikus marad, parancs pedig **TILOS** — az a `plan.md` dolga. A `<sec:plan_test_scenarios>` (plan) szekcióban ugyanez a hét szabály fut, de literál értékekkel és szó szerint futtatható hívásokkal.

### 1. Dimenzió-leltár — ez dönti el, HÁNY forgatókönyv kell (TD1)

Menj végig az alábbi hat dimenzión, és mindegyikhez írd ki, milyen értékei **relevánsak ebben a ciklusban**. Ahol kettő vagy több releváns érték van, ott a dimenzió **szorzódik**: minden értelmes kombináció **egy önálló forgatókönyv**.

| # | Dimenzió | Tipikus értékei | Példa |
|---|---|---|---|
| 1 | példányszám és párhuzamosság | 1 példány / N példány; 1 kérés / N egyidejű kérés | 3 pod, 5 egyszerre beérkező kérés |
| 2 | kiinduló állapot | üres / feltöltött / részlegesen feltöltött tároló | üres cache vs. meglévő bejegyzés |
| 3 | életciklus-sáv vagy állapotgép-állapot | érvényes / határhelyzet / lejárt / hiányzó | érvényes, ráhagyásos, keményen lejárt |
| 4 | erőforrás-hatókör | globális / entitáshoz kötött — **és a kettő keresztezése** | rendszerszintű vs. munkamenethez kötött |
| 5 | bemenet-osztály | érvényes / hiányzó / rosszul formált / jogosulatlan | — |
| 6 | sorrend és időzítés | előtte-utána / egyszerre / megszakítva | a birtokos példány elszáll félúton |

- **A szorzatot ki kell írni.** A forgatókönyv-lista előtt egy sorban jelenjen meg, miből származik a darabszám: pl. *„2 hatókör (globális, munkamenet) × 2 lejárati sáv (ráhagyásos, keményen lejárt) = 4 forgatókönyv"*. Ez az egyetlen ellenőrizhető nyoma annak, hogy a lista nem ötletszerű.
- **Összevonni csak indokkal szabad.** Ha két kombináció ugyanazt a kódutat járja, egy forgatókönyvbe vonhatók — de **írd le egy sorban, miért**. Indoklás nélküli összevonás lefedettségi rés.
- **🔴 Egyetlen forgatókönyv gyanús.** Ha a ciklus viselkedésének kettő vagy több dimenziója van, de a lista egy elemű, a leltár **nem futott le** — menj vissza az 1. lépésre.

### 1/b. Minden teszteset kimondja, MIT ellenőriz és MIÉRT (TD7)

A lépések attól még nem magyarázzák meg magukat, hogy konkrétak. Egy „5 párhuzamos kérés, mind `200`" lépéssor önmagában nem árulja el, hogy **melyik viselkedés** bizonyítására fut, és emiatt a következő fázisokban eldönthetetlen, hogy egy bukás valódi hiba-e vagy a teszt rossz — a javító pedig azt a legkönnyebb utat választja, ami zöldre viszi a lépést, nem azt, ami a viselkedést helyreállítja. Ezért **minden teszteset — forgatókönyv, unit-eset, integrációs flow, tesztfájl — a lépések ELŐTT kimondja:**

| Amit ki kell mondani | Mércéje |
|---|---|
| **mit ellenőriz** | a viselkedés egy állításként, amiről a futás után eldönthető, hogy igaz-e (nem a lépések összefoglalása, nem a teszt neve megismételve) |
| **miért fontos** | melyik elfogadási feltételt (`DoD-NN`) vagy kockázatot igazolja — mi romlana el észrevétlenül nélküle |
| **mi a bizonyíték** | melyik megfigyelés (a TD2 négyeséből) dönti el a kérdést |

- **A cím nem cél.** „Teszteset 3: konkurencia" — ez téma, nem állítás. Az állítás: *„öt egyidejű kérés közül pontosan egy újítja meg a tokent, a másik négy a meglévővel szolgál ki, és egyikük sem blokkolódik 2 s-nál tovább."*
- **Hatókör (TD0 szerint):** a spec-fázisban a `DoD-NN`-re hivatkozó, viselkedés-szintű mondat; a plan-fázisban ugyanez, de a hivatkozott konkrét értékekkel.
- **Ha nem tudod egy mondatban megmondani, mit ellenőriz, a teszteset nincs megtervezve** — vagy több esetet mos össze (bontsd szét a TD1 szorzata szerint), vagy nincs mögötte elfogadási feltétel (akkor a kérdés a fázis kérdés-fájljába megy).

### 2. Megfigyelési négyes — ez dönti el, MI legyen egy forgatókönyvben (TD2)

Egy forgatókönyv lépés-táblája nem kérés-válasz pár: a kiváltás mellett **négy** megfigyelési típusnak kell megjelennie, ahol értelmezhető. Az alsó három az, amit a puszta sablon-követés soha nem hoz létre — ezért kérdés formában áll:

| Típus | A kitöltendő kérdés | Amit a lépés-táblába ír |
|---|---|---|
| közvetlen válasz | mit ad vissza a hívott felület? | státuszkód **és** a válasz azonosítható mezője |
| megszámolt mellékhatás | mi az, amiből **pontosan ennyi** történik? (külső hívás, retry, log-bejegyzés, létrejött rekord) | egy sor, amiben az elvárt eredmény **szám** |
| közvetlenül kiolvasott állapot | melyik tárolt állapot olvasható ki a rendszer megkérdezése nélkül? (kulcs, DB-sor, fájl, metrika) | a tároló lekérdezése — a **név/kulcs literálisan** és az érték is |
| negatív kontroll | minek **NEM** szabad megtörténnie? | egy sor, aminek az elvárt eredménye a hatás **elmaradása** |

- **A kulcs nevét is ellenőrizni kell, nem csak a létét.** Egy elnevezési hiba (duplikált postfix, hibás prefix) a válaszból **nem látszik** — a kérés attól még 200-at ad. Ezért a kiolvasott állapot sorában a kulcs/mező neve szó szerint szerepel elvárt értékként.
- **Időbeli elvárás mért értékkel.** Ha az elvárás „nem blokkol" vagy „nincs késleltetés", akkor a lépéshez tartozik egy **mért érték és egy küszöb** (pl. a válaszidő a párhuzamos kérésekre `< 200 ms`). Küszöb nélkül az elvárás nem eldönthető.

### 3. Megszámolhatóság — ha nem mérhető, nem teszt (TD3)

A „pontosan egyszer" / „nem duplikálódik" / „nem termel logot" típusú elvárás **kizárólag számlálással** igazolható. Ezért minden ilyen elváráshoz meg kell nevezni a **számlálás forrását**: mock hívásnapló, kérés-számláló, alkalmazás-metrika, log-részhalmaz vagy a tároló lekérdezése. Ha a ciklusban nincs ilyen forrás, akkor vagy **be kell tervezni** (a plan tervezett módosításai közé), vagy a kérdés a fázis kérdés-fájljába kerül — a „feltehetően csak egyszer fut le" **nem** elvárt eredmény.

### 4. Negatív kontroll — az izoláció csak így igazolható (TD4)

Ha a ciklus **hatókört vagy izolációt** vállal (X csak Y-t érinti, Z-t nem), akkor az igazoláshoz **két** megfigyelés kell: hogy X megtörtént, és hogy Z-vel **közben** nem történt semmi. Egyetlen forgatókönyvben legyen olyan lépés, amely a védettnek szánt utat a hatás alatt gyakorolja, és az elvárt eredménye a **változatlanság** (a másik entitás kérése ugyanúgy lefut, a másik kulcs érintetlen). Izolációt vállaló elfogadási feltétel negatív kontroll nélkül **nincs lefedve**.

### 5. Kalibrációs minta — a sűrűség padlója (TD5)

Az alábbi blokk **nem** a te ciklusod tartalma: a **sűrűségét** és a **megfigyelési pontjait** másold, a témáját ne. Ennél kevesebb megfigyelési ponttal álló forgatókönyv gyanús.

```md
#### TS-01 — Hideg indítású konkurencia: globális token, 3 példány, 5 munkamenet  (DoD-01, DoD-07)

**<field:f_what_we_test>:** üres tárolóból induló, egyidejű kérés-rohamnál pontosan egy példány újítja meg a globális tokent, a többi arra vár, és a munkamenet-szintű út közben nem blokkolódik.
**<field:f_prerequisite>:** 3 futó példány ugyanazon a tárolón (indítás: `<sec:e2e_infrastructure>` 1–3. lépés), elérhetőségi probe zöld.

| # | Lépés | Hívás | Elvárt eredmény |
|---|---|---|---|
| 1 | tároló kiürítése | `redis-cli -h redis.dev.example.com -n 0 FLUSHDB` | `OK`, és a `KEYS ns01_tmp:*` üres listát ad |
| 2 | hívásnapló nullázása | `curl -s -X POST https://mock.dev.example.com/__admin/requests/reset` | `200` |
| 3 | 5 munkamenet előállítása | `for i in 1 2 3 4 5; do curl -s -X POST https://tmp.dev.example.com/login -H 'Content-Type: application/json' -d '{"username":"testuser@example.com","password":"Pass1234"}' -o sess-$i.json; done` | mind az 5 válasz `200`, és az 5 kinyert `sid` érték páronként **különböző** |
| 4 | 5 kérés egyidejű beküldése | `printf '%s\n' 1 2 3 4 5 \| xargs -P 5 -I{} curl -s -o out-{}.json -w '%{http_code} %{time_total}\n' -X POST https://tmp.dev.example.com/init-hash -H "Authorization: Bearer $(jq -r .access_token sess-{}.json)"` | mind az 5 sor `200`, és minden `out-N.json` tartalmaz `initHash` mezőt |
| 5 | megszámolt mellékhatás | `curl -s https://mock.dev.example.com/__admin/requests/count -d '{"method":"POST","url":"/token","bodyPatterns":[{"contains":"grant_type=client_credentials"}]}' \| jq .count` | `1` — pontosan egy megújítási hívás a 5 kérésre |
| 6 | kiolvasott állapot: kulcsnév és szerkezet | `redis-cli -h redis.dev.example.com --no-raw GET ns01_tmp:tokens:s2s \| jq 'keys'` | a kulcs neve pontosan `ns01_tmp:tokens:s2s` (nem `…:tokens:tokens:s2s`), a JSON mezői: `["accessToken","expiresAt","issuedAt"]` |
| 7 | kiolvasott állapot: a zár feloldva | `redis-cli -h redis.dev.example.com EXISTS ns01_tmp:tokens:s2s:lock` | `0` — a birtokos példány a művelet végén törölte |
| 8 | negatív kontroll | a 4. lépéssel **egyidejűleg**: `curl -s -o /dev/null -w '%{http_code} %{time_total}\n' https://tmp.dev.example.com/media/42 -H "Authorization: Bearer $(jq -r .access_token sess-1.json)"` | `200`, és a válaszidő `< 0.5` s — a munkamenet-szintű utat a globális token megújítása nem blokkolta |
| 9 | mért időbeli elvárás | a 4. lépés `%{time_total}` értékei | mindegyik `< 2.0` s — nincs a várakozási időkorláton túli beragadás |

**<field:f_cleanup>:** `rm -f sess-*.json out-*.json`; a példányszám visszaállítása 1-re; a tároló kiürítése.
```

### 6. Önteszt a szekció lezárása előtt (TD6)

- A dimenzió-szorzat **ki van írva**, és a forgatókönyvek száma megfelel neki (vagy minden összevonás indokolt egy sorban).
- Minden forgatókönyvben van **megszámolt mellékhatás** sor (szám az elvárt eredményben) — vagy egy sorban indokolva, miért nem értelmezhető.
- Minden forgatókönyvben van **közvetlenül kiolvasott állapot** sor, a kulcs/mező nevével együtt.
- Az izolációt vállaló elfogadási feltételekhez van **negatív kontroll** lépés.
- Minden „pontosan egyszer" / „nem duplikálódik" / „nem termel" elváráshoz meg van nevezve a **számlálás forrása**.
- Minden „nem blokkol" / „nincs késleltetés" elváráshoz tartozik **mért érték és küszöb**.
- **Minden teszteset kimondja, mit ellenőriz és miért** (TD7) — állításként, `DoD-NN` hivatkozással; a cím megismétlése nem elég.
