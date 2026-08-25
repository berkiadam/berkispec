<!--
  A `07-validate` PROJEKT-NYELVI blokkjai (9.4 kiemelés).
  Ezt a fájlt a telepítő build-time emeli be az INCLUDE markerek helyére, a
  választott PROJEKT-nyelv (`PROJECT_LANG`) szerint; a marker alakja
  `lang/07-validate.md#<horgony>`.
  A blokkok SZÓ SZERINT kerültek ide — ne fogalmazd át, ne egységesítsd.
  Az ANCHOR sorok NEM részei a beemelt szövegnek, csak határolók (8.9).
  FIGYELEM: ebbe a vezető jegyzetbe ne kerüljön komment-lezáró szekvencia.
-->

<!-- ANCHOR:validation-report-sablon -->
# Validálási riport — cycle-NN-<cycle-name>

**Jelenlegi státusz:** folyamatban | PASS | FAIL (megállt) | eszkalálva
**Körök száma:** N
**Utolsó frissítés:** YYYY-MM-DD HH:MM

_(Ezt a fejlécet minden kör végén frissíted — ez az egyetlen rész, amit felülírsz.)_

---

## Kör 1 — YYYY-MM-DD HH:MM — TELJES — FAIL

**Indító:** 07-validate első futás | önjavító hurok N. iterációja | megerősítő kör | megszakadt futás folytatása
**Riport-mappa:** `test-report/validate/round-01/` _(TR5 — a kör bizonyítékai; a mappanév száma = a kör száma)_

### Lépések (végrehajtási sorrendben)

| # | Idő | Lépés | Mit futtatott | Eredmény |
|---|---|---|---|---|
| 1 | 10:32 | gyors tesztek | `run-tests.py … --type gyors` | ✓ 43 passed / 0 failed / 0 skipped |
| 2 | 10:34 | Sonar Quality Gate (2/a) | `sonar-gate.py --out …/round-01/sonar-report.md` | ✓ exit 0 — QG PASS (MAJOR: 0, MINOR: 3) |
| 3 | 10:41 | kódreview (2/b, RV1) | `reviewer` subagent — diff `main…cycle-07` | ✗ 2 nyitott `Must Fix` (MF-01, MF-02) |
| 4 | — | nehéz tesztek | **kihagyva** — a statikus réteg bukott | — |
| 4b | — | E2E (opcionális sor) | **kihagyva** — plan-hiány (TR4): nincs leírva a Keycloak indítása | eszkaláció a 03-ra |
| 5 | 10:42 | teszt-riport kapu (TR3) | `report-gate-check.py conventions.md specs/cycle-NN-… --report-subdir test-report/validate/round-01` | ✓ exit 0 — `unit-report.html` (88 KB) |
| 6 | 10:42 | DoD-ellenőrzés | `dod-check.py … --apply` | ✗ DoD-03 nem teljesül |
| 7 | 10:43 | naplózás | `failure-counter.py --result FAIL --failed-item ...` | exit 0 — folytatható |

### Bukott elemek

- `MF-01` — a `verifyToken()` nem kezeli a lejárt kulcsot _(1/3 egymást követő, 1/5 összes)_
- `MF-02` — … _(1/3, 1/5)_
- `DoD-03` — a `/verify` végpont nem ad `correlationId`-t a válaszban _(1/3, 1/5)_

### Definition of done

| ID | Eredmény | Indoklás |
|---|---|---|
| DoD-01 | ✓ | a token-csere 200-at ad a `<scope>` scope-pal |
| DoD-03 | ✗ | a válaszból hiányzik a `correlationId` |

### Kódreview (RV1)

- **Futott:** igen (teljes kör, a gyors tesztek zöldek voltak) | inkrementálisan, csak a nyitott `MF-NN`-ekre (könnyű kör) | kihagyva — könnyű kör (VD10) | kihagyva — az 1. lépés bukott
- **Jelentés:** `test-report/code-review.md` — 2 nyitott `Must Fix`, 3 `Suggestion`
- **Nyitott findingok:** `MF-01` — a `verifyToken()` nem kezeli a lejárt kulcsot; `MF-02` — …
- **Direktben alkalmazott Suggestion:** `S-02` (scope-on belüli, kockázatmentes) — a következő kör teszteli
- _(re-review esetén: mely findingok zárultak le, és mi maradt nyitva)_

### Teszt-riportok (TR3 / TR5)
- **Kör-mappa:** `test-report/validate/round-01/`
- `report-gate-check.py --report-subdir test-report/validate/round-01` → exit 0 / 1 / 2 — a kör-mappába került artefaktumok felsorolása mérettel (vagy: mi hiányzik)
- _(könnyű körben: „kapu kihagyva — könnyű kör (VD10)"; a ténylegesen legenerált gyors-teszt artefaktumokat ilyenkor is sorold fel)_

### Tasks elvégzettsége
- Minden task `[x]`: ✓ / ✗ (ha ✗: az elvégzetlen taskok felsorolása)

### Javító kör (ha volt)

- **Felvett javító-taskok:** T041 `[GREEN]` — …, T042 `[CHECK]` — … _(a `## Validációs javítások` szekcióba)_
- **`implement-fixer` indítva:** 10:45 — bemenet: `DoD-03`; **`review-fixer` indítva:** 10:52 — bemenet: `MF-01`, `MF-02` _(egy batch, egy VD3a kapu — VD13)_
- **A fixer visszajelzése:** 10:44 — „T041 lezárva: a rotáció most a `refreshToken()`-ben történik"; eszkalációs jelzés: nincs
- **Szerződés-integritás kapu (VD3a):** ✓ tiszta — a `git diff` nem érintett tesztfájlt / `spec.md`-t / Sonar-konfigot
  _(vagy: ✗ — `auth.spec.ts` módosítva (assertion lazítva) → `git checkout --` visszaállítva → eszkaláció)_

### A kör döntése

FAIL → új kör indul a javítás után. | PASS → a hurok konvergált, státuszok `Kész`-re. | STOP — [betelt korlát] → humán döntés. | Eszkaláció 03/02-re — [indok].

---

## Kör 2 — YYYY-MM-DD HH:MM — KÖNNYŰ — FAIL

_(ugyanaz a szerkezet; a lépés-táblában a nehéz tesztek és a Sonar sora „kihagyva — könnyű kör (VD10)")_

---

## Kör 3 — YYYY-MM-DD HH:MM — TELJES — PASS

_(megerősítő kör: minden lépés lefutott)_

---

## Összegzés

- **Végeredmény:** PASS — 3 kör után
- **Körök:** 3 összesen — ebből 2 teljes, 1 könnyű _(VD10 — a mérhetőség miatt kötelező sor)_
- **Újrafuttatott elemek:** `auth.spec.ts > refresh token rotation` (2 kör), `DoD-03` (2 kör)
- **Eszkaláció / humán beavatkozás:** nem volt
- **Ideiglenes környezeti módosítás:** [ha volt port-csere: melyik, és visszaállt-e]

# Validation History
_(ezt a szekciót a failure-counter.py írja — kézzel nem szerkeszted)_

<!-- ANCHOR:LC2-megallas-prefix -->
[VALIDATE · <Failed Item> · próba 3/3]                  ← per-item korlát
[VALIDATE · <Failed Item> · összes bukás 5/5]           ← per-item összes-korlát
[VALIDATE · divergáló hurok · FAIL-futások 5/5]         ← globális backstop

<!-- ANCHOR:zaro-uzenet -->
4. Jelezd: *"Validálás sikeres. Folytathatjuk a 8. lépéssel: dokumentáció szinkron (08-doc-sync). Az új fázis megkezdése előtt mindenképpen futtass egy `/clear` parancsot a kontextus kiürítéséhez, majd használd ezt a parancsot:*
   > ```
   > /bs-doc-sync input: @specs/cycle-NN-<cycle-name>
   > ```"*

<!-- ANCHOR:VD5-eszkalacio-uzenet -->
> **[VALIDATE · <Failed Item> · próba N/3]**
> *"A validáció során a(z) [Failed Item] tervezési hibának bizonyult: a kód csak a teszt vagy a Definition of done megváltoztatásával lenne zöld, amit a hurok nem tehet meg (anti-„teszt-csalás"). Ezért nem a 06-implementbe léptem vissza, hanem a tervezési fázishoz eszkalálok. A(z) [plan.md / spec.md] státuszát visszaállítottam, hogy a tervezési döntést rendezni lehessen. Folytasd a tervezés felülvizsgálatával:*
> ```
> /bs-write-plan (DoD-hiba esetén: /bs-write-spec) input: @specs/cycle-NN-<cycle-name>/plan.md (vagy spec.md)
> ```
> *A folyamat a tervezés rendezése után a 05→06→07 úton tér vissza ide."*
> **A válasz végén: kattintható link a `validation-report.md`-re.**
