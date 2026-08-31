<!-- Forrás-jegyzet: az útvonal-konvenció egyetlen definíciója. A 02/03/04 minőségi
     kapuja ÉS a hozzájuk tartozó fixer-agent is beemeli (build-time INCLUDE).
     Egy helyen szerkeszd — korábban a szabály három helyen, eltérő tartalommal élt. -->
**Útvonal-formátum (RP1) — kétféle hivatkozás, két szabály:**

| Mit hivatkozol | Formátum | Példa |
|---|---|---|
| **Kód- és fájl-hivatkozás** — érintett komponens, tervezett módosítás, `path:sor` horgony, parancs argumentuma | **a repó gyökeréhez képest relatív** | `src/token-store.ts`, `apps/web/src/index.ts:42`, `bash scripts/seed.sh` |
| **Dokumentum-link** — markdown link egy másik doksira | **a fájl saját könyvtárához képest relatív** (hogy kattintható legyen) | `[spec.md](./spec.md)`, `[architektúra](../../docs/architecture.md)` |

**Miért így:** a parancsok a **repó gyökerében** futnak (06-implement, 07-validate, `test-runner`), a `git` és a helper-szkriptek is így értelmezik az útvonalat, és a `05-analyze` mechanikus kapuja (`A2`/`V1` check) **ehhez oldja fel** a hivatkozásokat. Egy `../../src/app.ts` alakú kód-hivatkozás a kapuban feloldhatatlan, a parancsban pedig hibás — miközben a *dokumentum-linknél* épp a fájl-relatív alak a helyes, mert az a kattintható.

**Mindkét esetben tilos:**
- **abszolút útvonal** (`/home/adam/repos/projekt/src/app.ts`, `C:\Users\...\src\app.ts`, `/mnt/c/...`) — gép-specifikus, más gépen és CI-ben értelmetlen;
- **`file://` sémájú link** a dokumentum tartalmában (a *chat-válaszban* adott kattintható link más kérdés — az ott elvárt);
- **placeholder** útvonal (`<projekt>/src/...`, `/path/to/...`).

**Ami NEM fájl-útvonal, tehát nem érinti a szabály:** HTTP-endpoint útvonala (`/api/v1/token-exchange`), konténer-belső útvonal egy parancsban (`docker exec app cat /opt/app/config.yaml`), JSON-pointer, regex.

**Ha az eszközöd abszolút útvonalat ad vissza** (IDE-integráció, fájlkereső, `pwd`-vel összefűzött útvonal), a dokumentumba írás **előtt** vágd le a repó gyökerét. Abszolút útvonal a `spec.md`/`plan.md`/`tasks.md` szövegében akkor is hiba, ha a te gépeden helyes.

**Kötelező ellenőrzés a fázis lezárása előtt (RP1-kapu).** Ne szemre nézd át — futtasd:

```bash
python3 <platform-scripts-mappa>/analyze-gate-check.py specs/cycle-NN-<cycle-name> --paths-only
```

A kapu a ciklus mappájában **meglévő** tervezési dokumentumokat nézi (`spec.md`/`plan.md`/`tasks.md` — amelyik már létezik), tehát a `02` lezárásakor is fut, amikor a plan és a tasks még nincs meg. Nem `0` kilépő kód → a talált útvonalakat **javítsd ki**, és futtasd újra; a fázis `PASS` nélkül nem záródik. A `03`/`04` fázisban a teljes mechanikus kapu (`M`) ezt úgyis lefuttatja — ott ez a hívás csak akkor kell, ha előbb akarsz visszajelzést.

_A `05-analyze` mechanikus kapuja ugyanezt gépiesen ellenőrzi (`R1` check): `file://`, gép-specifikus, placeholder és abszolút repó-útvonal a tervezési dokumentumokban `<status:must_fix>`._
