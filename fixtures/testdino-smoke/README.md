# TestDino füstteszt-fixture (`TM1`–`TM10`, `improve-list13`)

**Mire való.** Ez a legkisebb működő Playwright projekt, amivel a **test manager integráció**
(`prompts/improve-list13.md` 5.b) adaptere fejleszthető és mérhető. **Nem a keret része**, nem
települ sehova, és a `lang-parity-check.py` sem nézi — fejlesztési próbapad.

**Miért van a repóban.** A `6.9` szakasz mérései ebből a projektből származnak; aki az `E8`/`E9`
taskot megírja, itt tudja **reprodukálni** őket, ahelyett hogy újra felderítené a szolgáltatót.

---

## Futtatás

```bash
nvm use 22                                   # ⚠ KÖTELEZŐ, lásd lent
npm install                                  # a package-lock.json pinnel
npx playwright install chromium              # ha még nincs böngésző
source ~/.config/berkispec/testdino.env      # → TESTDINO_TOKEN (a repóban NINCS kulcs)
npx playwright test
```

## 🔴 Node ≥ 22.12 kötelező

A `@testdino/playwright@2.6.2` **CommonJS** csomag, de `chalk@^5`-öt (ESM-only) `require`-öl, a
`commander@^15` függősége pedig `node >=22.12`-t kér. Node 20-on ezért:

```
Error [ERR_REQUIRE_ESM]: require() of ES Module …/chalk/source/index.js
    … at loadReporter … at createReporters
```

és ez **az egész teszt-futást megöli** — nulla lefutott teszt, `exit 1`. Ez a `TM1`
(„a külső SaaS soha nem lehet a ciklus futásának előfeltétele") egyetlen valódi sérülési pontja,
és ezért próbálja a `test-manager.py --mode preflight` a riporter **betölthetőségét**, nem csak
az env var meglétét.

## Mit bizonyít ez a fixture

A `playwright.config.ts` szándékosan **négy riportert** fűz egymás mellé
(`list` + `junit` + `html` + `@testdino/playwright`), a teszt-készlet pedig szándékosan
**vegyes**: 3 zöld · 1 bukó · 1 skipped.

| amit mér | eredmény (2026-09-22) |
|---|---|
| együtt él-e a keret JUnit/HTML riportja a test managerével | **igen** — `test-report/junit.xml` (5 testcase) és `test-report/html/` elkészül |
| hol a futás-URL | a stdout **utolsó nem üres sora**: `  View run  https://app.testdino.com/org_…/projects/project_…/test-runs/test_run_…` |
| befolyásolja-e a riporter az exit kódot | **nem** — az `exit 1` a bukó teszté |
| mi történik hiányzó tokennel | hibablokk a kimeneten, **a tesztek lefutnak, `exit 0`** |
| mi történik rossz tokennel | `Authentication failed - Invalid or expired token`, **a tesztek lefutnak, `exit 0`** — 🔴 a futás **zöldnek látszik, miközben semmi nem töltődött fel** |

Az utolsó sor miatt mondja ki az `L13-D26`, hogy **a feltöltés csak akkor számít megtörténtnek,
ha a futás-URL megjelent** — a futtató exit kódja erre nem bizonyíték.

## Amit az adapter írásához innen lehet venni

```python
# a futás-URL kinyerése a kör naplójából (L13-D26)
RUN_URL_RE = re.compile(r"https://app\.testdino\.com/\S+/test-runs/\S+")

# a néma bukás felismerése — ezek a riporter saját sorai, a futtató exit kódja 0 marad
AUTH_FAIL  = "Authentication failed"
NO_TOKEN   = "Token is required but not provided"
DELIVERED  = "run:end delivered"
```

Végpontok: a riporter a `https://reporter.testdino.com`-ra ír, a publikus API a
`https://api.testdino.com/api/v1/public`.

## Amit NEM szabad ide tenni

**Kulcsot.** A `TESTDINO_TOKEN` a `TC5` szerint osztott platform credential, ez a repó pedig
publikus — a kulcs a `~/.config/berkispec/testdino.env`-ben él, ide csak pointer jön. A
`node_modules/`, a `test-report/` és a `test-results/` gitignorált (futáskor keletkezik).
