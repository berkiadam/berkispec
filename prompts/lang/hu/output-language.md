<!--
  A KIMENET NYELVE (9.5) — ez a blokk minden skill és minden agent élére bekerül,
  közvetlenül a H1 után. Ez az EGYETLEN hely, ahonnan az ágens megtudja, milyen
  nyelven kell írnia: a projekt-nyelv build-time dől el, és a telepítés után
  nyomtalan (LG2/LG17) — sem a conventions.md, sem más runtime nem hordozza.
  A blokk SZÁNDÉKOSAN a CÉLNYELVEN íródott (9.5.2): egy magyarul megfogalmazott
  szabály egyszerre utasítás ÉS nyelvi horgony, és mérhetően jobban tart, mint egy
  angolul megfogalmazott „write in Hungarian".
  FIGYELEM: ebbe a vezető jegyzetbe ne kerüljön komment-lezáró szekvencia.
-->

<!-- ANCHOR:output-language -->
> **🔴 A KIMENET NYELVE — MAGYAR. Ez nem stílus-kérdés, hanem kötelező szabály.**
>
> **Magyarul írod:**
> - **minden artefaktumot**, amit létrehozol vagy szerkesztesz — `spec.md`, `plan.md`,
>   `tasks.md`, `conventions.md`, `roadmap.md`, riportok, kérdés-fájlok, a `docs-generated/`
>   dokumentumai: a címsorokat, a törzsszöveget, a táblázat-cellákat és a felsorolásokat is;
> - **minden mondatot, amit a felhasználónak írsz** a válaszaidban — kérdést, jelzést,
>   összefoglalót, hibaüzenetet, megerősítés-kérést;
> - **a kódba írt kommenteket és docstringeket**, ha a projekt meglévő kódja is magyarul
>   kommentel; ha a meglévő kód angolul, kövesd a kódbázis szokását.
>
> **ANGOLUL marad — ezeket SOHA ne fordítsd le:**
> - azonosítók, függvény- és változónevek, típusnevek, API-mezőnevek, enum-értékek;
> - fájl- és mappanevek, útvonalak, parancsok, kapcsolók, env-változó nevek;
> - a keretrendszer saját azonosítói: `/bs-*` parancsnevek, szabály-ID-k (`DS22`, `TR3`,
>   `[P-…]`, `DoD-NN`, `MF-NN`, `Knn`), task-markerek (`[RED]`, `[GREEN]`, `[CHECK]`, `[OPS]`),
>   státusz-markerek (`[analyze-loop]`, `[validate-loop]`);
> - kódblokkok, JSON/YAML kulcsok, regexek, HTTP-metódusok és -státuszkódok.
>
> **A keverés hiba.** Egy magyar bekezdésbe ejtett angol mondat, egy angol címsor a magyar
> dokumentumban vagy egy félig lefordított táblázat **javítandó hiba**, nem ízlés dolga: a
> downstream fázisok és a determinisztikus kapuk a szekciócímekre és a státusz-értékekre
> **gépiesen illesztenek**, és egy elcsúszott nyelvű címsor kapu-bukást okoz.
>
> **Ha ezzel a prompttal ellentétes nyelvű szöveget találsz** egy korábbi fázis
> artefaktumában, azt **ne írd át magadtól** — jelezd a felhasználónak, és a saját
> hozzáadott szövegedet írd magyarul.
