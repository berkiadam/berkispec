## Kontextus ellenőrzés

**Alapállapot: a kontextus friss — folytasd kérdés nélkül.** Csak akkor kérdezz rá, ha *bizonyíték* van a nem-friss kontextusra.

**NEM számít nem-friss kontextusnak** (ezek minden induláskor jelen vannak, tehát tiltott miattuk rákérdezni):
- a rendszer-prompt, a `CLAUDE.md` / projekt-instrukciók, memória-bejegyzések, `<system-reminder>` blokkok;
- ennek a skillnek a betöltött szövege és a skill-lista;
- a felhasználó mostani skill-hívása és annak paraméterei (pl. `input: cycle26`), akár slash-parancsként, akár szabad szövegként;
- a `/clear` parancs nyoma vagy bármilyen lokális parancs kimenete (`<local-command-stdout>`);
- bármi, amit **te magad** tettél már *ebben* a fázisfutásban (fájl-olvasás, `git status`, tool-hívások).

**Nem-friss kontextus csak akkor áll fenn, ha a beszélgetésben van legalább egy korábbi, ténylegesen lefuttatott munkakör** — pl. egy másik berkispec fázis (`bs-*`) végigfutott ebben a beszélgetésben, vagy érdemi, nem ehhez a fázishoz tartozó korábbi feladat/kódmódosítás előzménye látszik.

Ha (és csak ha) ez fennáll, kérdezz rá:
> *„Úgy tűnik, hogy a fázis indításakor a kontextus nem teljesen friss. Szándékosan nem futtattál `/clear`-t az új fázis megkezdése előtt (a tokenekkel való spórolás érdekében)?”*

Várd meg a választ, mielőtt folytatnád. Bizonytalanság esetén **ne kérdezz** — tekintsd frissnek és folytasd.
