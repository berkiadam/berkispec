<!-- Forrás-jegyzet: a 04-write-tasks skill Fix-mód szekciója, kiemelve, hogy a
     tasks-fixer subagent prompt build-time beemelhesse (BD14/b). Egy helyen szerkeszd. -->
## Fix-mód (analyze-hurok belépő)

> **Mikor aktív:** ezt a szekciót az `05-analyze` önjavító hurka indítja az `agents/tasks-fixer.md` wrapperen keresztül — **nem** a normál tasks-írás. A bemenet egy konkrét `<status:must_fix>` lista, nem teljes újrafutás.

> **Skill-beolvasás nem kell (D13):** a fix-módhoz szükséges összes szabály ebben a promptban van — a fázis „Minőségellenőrzés” szekciója is. **Fix-módban ne olvasd be a teljes fázis-skillt** (`04-write-tasks.md`): felesleges, és a teljes fázis újrafuttatására csábít, holott a feladat egy szűk, célzott javítás.

A fix-mód egy **szűkített belépő:** a megadott `<status:must_fix>` megállapításokat javítod célzottan (jellemzően lefedettségi rés vagy task-szintű duplikáció), **nem írod újra az egész listát**. A `*-input-from-prev.md` fájlokat fix-módban **teljesen figyelmen kívül hagyod** (sem nem olvasod, sem nem írod) — IP1/6. (Ellenkező esetben egy olcsóbb LLM hajlamos elölről kezdeni a fázist — ez tilos.) A normál flow minőségellenőrzése (a fázis „Minőségellenőrzés” szekciója) a javított részekre továbbra is érvényes — **csak a javított részekre**, nem a teljes listára.

### Két belépési alak
1. **Közvetlen javítás:** a `<status:must_fix>` a tasks listát érinti (lefedettségi rés, redundáns task — a célfázis 04).
2. **Downstream re-deriválás (reconciliation):** a hurok feljebb (02/03) javított, és a tasks listát a megváltozott planhez kell **összehangolni**. Célzott reconciliation, nem teljes újraírás: csak a megváltozott plan-szakaszokhoz tartozó taskokat igazítod.

### Bemenet
- A tasks-re szűrt `<status:must_fix>` lista (kategória + leírás + `fájl:hely`), vagy reconciliation esetén a megváltozott upstream (plan) összefoglalója.
- A `tasks.md` és a `tasks-questions.md` aktuális állapota.

### Auto-javítható vs kérdezni kell (a határvonal)

| Magától javítsd (auto) | Kérdésbe tedd (`tasks-questions.md` új `Knn`) |
|---|---|
| Lefedettségi rés pótlása (hiányzó task felvétele a planből), task-duplikáció összevonása, naming-egységesítés, plan-változás átvezetése a tasks listába | Olyan task, amely a planből nem vezethető le egyértelműen (a plan hiányos), körkörös task-függőség, feltételes/külső függőségtől függő task |

A `<status:must_fix>`-et, amihez **valódi döntés** kell (jellemzően ha a plan hiányosságát jelzi), **ne találd ki** — vedd fel új `Knn`-ként a `tasks-questions.md` végére, és **ne kérdezd közvetlenül a felhasználót** (fix-módban nincs interaktív csatornád). A kérdezést az orchestrátor (`05-analyze`) végzi, a user-felé `TASKS/Knn` prefixszel. (Ez a fix-mód megfelelője a normál flow „Megállási szabályok" pontjának: normál módban STOP + jelzés, fix-módban kérdés-gyűjtés a `tasks-questions.md`-be.)

### Amit fix-módban is KÖTELEZŐ megtartani (PID1)

Új vagy módosított task felvételekor a hivatkozási rend nem sérülhet — a hurok leggyakoribb csendes rombolása épp ez:

- **minden új task kap `— plan [P-…]` hivatkozást** (egy elsődleges ID; ha több task osztozik egy ID-n, részhatókör-jelöléssel);
- **a `<sec:plan_coverage>` táblát frissítsd** az új taskokkal — nem maradhat a régi állapotban;
- **a csoport-fejléc plan-ID listáját** egészítsd ki, ha új szekciót fedő task került a csoportba;
- ha a plan-fixer **új `[P-…]` szekciót** hozott létre, ahhoz kell hivatkozó task (vagy indokolt sor a táblában);
- **plan-ID-t soha nem találsz ki**: ha a taskhoz nem tudsz létező ID-t rendelni, az `tasks-questions.md` kérdés.

_(A mechanikus kapu — `analyze-gate-check.py` — ezeket a következő körben úgyis kimutatja; itt olcsóbb helyesen csinálni.)_

### <field:f_status> (auto, `[analyze-loop]` marker)
A hurok a `tasks.md` státuszát `[analyze-loop]` markerrel nyitotta vissza (pl. `<status:draft> [analyze-loop]`). Amíg a marker jelen van, **automatikusan** lépteted a státuszt, megerősítés-kérés nélkül:
- van nyitott `[ ]` kérdés a `tasks-questions.md`-ben → marad `<status:draft> [analyze-loop]`;
- minden kérdés `[x]` és a célzott javítás kész (a minőségellenőrzés átment) → `<status:ready_for_implement> [analyze-loop]`.

A marker fel- és levételét az orchestrátor kezeli; te csak a státusz-értéket lépteted.

### Visszatérési összefoglaló (az orchestrátornak)
Adj vissza tömör összefoglalót: (a) mely `<status:must_fix>`-eket / plan-változásokat vezettél át és hogyan, (b) milyen új `Knn` kérdéseket vettél fel a `tasks-questions.md`-be (azonosítóval). A `tasks.md`-t és a `tasks-questions.md`-t te írod; az `analyze-report.md`-t **nem** — az az orchestrátoré.

> **🔴 Teljességi elszámolás — egy tétel sem tűnhet el némán.** A kapott `<status:must_fix>` lista **minden** tétele jelenjen meg az összefoglalódban **pontosan egy** ágon: vagy (a) — megjavítottad, és leírod hogyan —, vagy (b) — `Knn` kérdésként felvetted, mert valódi döntést igényel. Harmadik lehetőség nincs: a „nem fértem hozzá", a „majd a következő körben" és a csendes kihagyás **nem** elfogadható. Ha egy tételt sem javítani, sem kérdéssé alakítani nem tudsz, azt **mondd ki egy sorban, azonosítóval és indokkal** — az orchestrátornak erre külön ága van. A tételekre mindig a **kapott azonosítóval** hivatkozz (`AF-NN` / `AX-NN`), soha ne parafrazeáld a szövegüket: erre épül a hurok túlélés-szabálya.

- **`downstream-hatás:`** (D11) — kötelező mező: `nincs`, vagy `van — <mi változott, ami a következő fázist érinti>`. Ebből dönti el az orchestrátor, hogy kell-e egyáltalán elindítani a downstream fixereket. **Bizonytalanság esetén `van`**, a konkrét ok megnevezésével — a puszta „biztos, ami biztos” viszont nem ok.
