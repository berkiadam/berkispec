# AI ügyek - Ádám blokk

## 4. dia kibontása - Hatékony használat skálázása

### Alapüzenet

Az AI-használat hatékonysága nem lineárisan nő attól, hogy többet használjuk az eszközt.
Az áttörést az hozza, amikor a felhasználó kilép az alkalmi, intuitív használatból, és
kontrollált agentic munkamódszerben kezd dolgozni.

Nem az a fő kérdés, hogy "használjuk-e az AI-t", hanem hogy milyen érettségi szinten használjuk:
chatként, vibe coding eszközként, vagy tudatos agentic workflow részeként.

---

## 4.1 Agentic felhasználói érettség

### Slide-ra kerülő tartalom

**Agentic felhasználói érettség lépései**

1. **Chatelünk az AI-val**
   - Kérdezünk, válaszokat másolunk, kódot ide-oda mozgatunk.
   - Gyorsíthat, de nem alakítja át érdemben a munkavégzést.
   - A tokenhasználat kevésbé kontrollált, de a kockázat is kisebb.

2. **Vibe coding agenttel**
   - Az agent már aktívan ír, módosít, próbálkozik.
   - Élvezetesebb és gördülékenyebb munkaérzetet ad.
   - Kontroll nélkül gyorsan tokenpazarló, minőségi kockázatos és frusztráló lehet.

3. **Agentic keretrendszerben dolgozunk**
   - Cél, scope, context, terv, ellenőrzés és döntési pontok vannak.
   - A munka reprodukálhatóbb, olcsóbb és jobb minőségű.
   - Itt kezd valódi szervezeti szinten skálázhatóvá válni az AI-használat.

### Beszélői jegyzet

Az első szint az, amikor az AI lényegében okosabb keresőként vagy konzultációs partnerként működik.
Ez hasznos, de a fejlesztői workflow magja nem változik: a user másolgat, értelmez, beilleszt,
ellenőriz. Ez lokálisan gyorsíthat, de nem hoz áttörést.

A második szint a klasszikus "vibe coding": az agent már dolgozik helyettünk, a fejlesztő pedig
irányít, javít, újrapróbál. Ez sokszor látványosan kényelmesebb, de módszertan nélkül nagyon gyorsan
égeti a tokeneket, és a minőség is hullámzó. Emiatt sok felhasználó rövid idő után csalódhat:
úgy érzi, "sokat dolgozott az AI", mégsem lett megbízható végeredmény.

A harmadik szinten az AI-t nem szabadon engedett kódszerzőként használjuk, hanem munkafolyamatba
tesszük. Ez a különbség a látványos demó és a napi szinten fenntartható hatékonyságnövekedés között.

---

## 4.2 Miért nem elég a "chatelünk az AI-val" működés?

### Slide-ra kerülő tartalom

**A chat alapú használat plafonja**

- A felhasználó marad a fő integrációs pont.
- A kód és a context kézzel mozog az eszközök között.
- Az AI nem látja stabilan a teljes feladatkörnyezetet.
- Sok döntés implicit marad: scope, elvárt minőség, tesztelés, határok.
- Jó válaszokat adhat, de nem épül be valódi delivery workflow-ba.

**Következmény**

Gyorsabb lehet az egyéni munka, de nem lesz belőle jól skálázható szervezeti képesség.

### Beszélői jegyzet

Ezen a szinten az AI főleg asszisztens: magyaráz, példát ad, refaktorjavaslatot ír, hibát értelmez.
Ez értékes, különösen tanulásnál vagy gyors ötletelésnél. De a tényleges munkafolyamat még mindig
emberközpontú és kézi: a user dönt arról, mit másol át, mit futtat, mit tart meg.

Ezért ez a szint nem elég, ha a cél nem csak az, hogy egy-egy ember kicsit gyorsabban dolgozzon,
hanem az, hogy egy csapat mérhetően és tartósan hatékonyabb legyen.

---

## 4.3 Miért kevés önmagában a vibe coding?

### Slide-ra kerülő tartalom

**A vibe coding erős, de kontroll nélkül drága**

- Növeli a fejlesztői munka gördülékenységét és élvezetességét.
- Gyorsan ad látható eredményt, ezért könnyű megszeretni.
- Nagy contexttel és sok újrapróbálással nagyon gyorsan fogyasztja a limitet.
- Az agent hajlamos lokálisan jó, de rendszerben rossz megoldást választani.
- Review, teszt és scope kontroll nélkül minőségi kockázatot termel.

**Következmény**

Jó belépési élmény, de módszertan nélkül nem megbízható skálázási stratégia.

### Beszélői jegyzet

A vibe coding önmagában nem rossz. Sőt, sok embernél ez adja meg az első valódi "aha" élményt:
az AI már nem csak válaszol, hanem ténylegesen viszi előre a munkát. A probléma akkor kezdődik,
amikor ez válik az egyetlen munkamódszerré.

Ha nincs előre tisztázott cél, nincs acceptance criteria, nincs context hygiene, nincs ellenőrzési
pont, akkor az agent sok kört fut. Ezek a körök tokenben drágák, és sokszor csak látszólag viszik
közelebb a feladatot a megoldáshoz. A végeredmény lehet működő, de nehezen review-zható,
nehezen karbantartható, vagy egyszerűen nem azt oldja meg, amit kellett volna.

---

## 4.4 Agentic keretrendszerek - mit érdemes bevezetni?

### Slide-ra kerülő tartalom

**Agentic keretrendszer = kontrollált AI-munkafolyamat**

- **Specifikációvezérelt fejlesztés:** cél, scope, acceptance criteria, edge case-ek.
- **Plan -> implement -> verify ciklus:** feltárás, terv, módosítás, ellenőrzés.
- **Context hygiene:** csak a releváns fájlok, logok, szabályok és döntések kerülnek be.
- **Token-sparing workflow:** nagy feladatok bontása kisebb, lezárt munkaszakaszokra.
- **Újrahasználható promptok és skillek:** visszatérő feladatokra standard minták.
- **Subagentek / szerepalapú bontás:** feltárás, implementáció, review külön szerepben.
- **Teszt- és review-kapuk:** az agent munkáját mérhető feltételekhez kötjük.

### Beszélői jegyzet

Itt a lényeg nem egy konkrét tool vagy framework neve, hanem az, hogy az agent ne kontroll nélkül
dolgozzon. A jó agentic workflow ugyanazt hozza be az AI-használatba, amit a jó fejlesztési
folyamatok általában is: tiszta célokat, korlátokat, visszacsatolást és ellenőrzést.

A specifikációvezérelt működés például megakadályozza, hogy az agent túl hamar implementálni kezdjen.
A plan -> implement -> verify ciklus csökkenti a vak próbálkozásokat. A context hygiene és a
token-sparing workflow közvetlenül limitet spórol. A skillek, promptok és sablonok pedig lehetővé
teszik, hogy ne minden felhasználó találja ki újra ugyanazt a munkamódszert.

---

## 4.5 Példák standard agentic workflow-kra

### Slide-ra kerülő tartalom

**Jól tanítható workflow példák**

- **Bugfix workflow**
  Reprodukció -> releváns fájlok -> hipotézis -> minimális javítás -> teszt.

- **Code review workflow**
  Kockázatok -> regressziók -> hiányzó tesztek -> konkrét file/line visszajelzés.

- **Feature workflow**
  Specifikáció -> acceptance criteria -> terv -> implementáció -> ellenőrzés.

- **Refaktor workflow**
  Jelenlegi viselkedés rögzítése -> kis lépések -> tesztkapu -> review.

- **Dokumentáció workflow**
  Forrásfeltárás -> célközönség -> vázlat -> pontosítás -> véglegesítés.

### Beszélői jegyzet

Ezek azért fontosak, mert a képzésnek nem általános "promptolási tippekből" kell állnia.
A valódi haszon ott jön, ha tipikus munkatípusokra adunk használható kereteket.

Egy bugfixnél például ne az legyen az első lépés, hogy "javítsd meg", hanem az, hogy reprodukáljuk
a hibát, azonosítjuk a releváns kódrészt, és csak utána kérünk célzott módosítást. Egy refaktornál
pedig különösen fontos, hogy előbb rögzítsük a jelenlegi viselkedést, különben az agent könnyen
"szebb" kódot készít, ami közben megváltoztatja a működést.

---

## 4.6 Mit kell skálázni szervezeti szinten?

### Slide-ra kerülő tartalom

**Nem toolhasználatot, hanem munkamódszert kell skálázni**

- Közös minimum: mikor melyik AI-eszközt használjuk.
- Közös workflow-k: bugfix, review, feature, refaktor, dokumentáció.
- Közös tokenhigiénia: context méret, session-kezelés, újrakezdési szabályok.
- Közös minőségi kapuk: teszt, review, acceptance criteria.
- Közös tudásbázis: promptok, skillek, példák, belső minták.

**Döntési pont**

Érdemes-e ebből rövid, célzott képzési / enablement csomagot készíteni?

### Beszélői jegyzet

Ez vezet át az 5. dia limit és eszközmix témájára. A limitprobléma nem csak kapacitáskérdés.
Ha a használat módszertan nélkül nő, akkor a limitek gyorsabban fogynak, a minőség hullámzóbb lesz,
és nehezebb megmondani, melyik eszköz mire való.

Ha viszont van közös munkamódszer, akkor ugyanaz a limit több értelmes munkára elég, és az
eszközmixről is racionálisabban lehet dönteni.
akk