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

_A `05-analyze` mechanikus kapuja ezt gépiesen ellenőrzi (`R1` check): `file://`, gép-specifikus és abszolút repó-útvonal a tervezési dokumentumokban `<status:must_fix>`._
