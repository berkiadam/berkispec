<!-- Forrás-jegyzet: a 03-write-plan skill Fix-mód szekciója, kiemelve, hogy a
     plan-fixer subagent prompt build-time beemelhesse (BD14/b). Egy helyen szerkeszd. -->
## Fix-mód (analyze-hurok belépő)

> **Mikor aktív:** ezt a szekciót az `05-analyze` önjavító hurka indítja az `agents/plan-fixer.md` wrapperen keresztül — **nem** a normál plan-írás. A bemenet egy konkrét `Must Fix` lista, nem teljes újrafutás.

> **Skill-beolvasás nem kell (D13):** a fix-módhoz szükséges összes szabály ebben a promptban van — a fázis „Minőségellenőrzés” szekciója is. **Fix-módban ne olvasd be a teljes fázis-skillt** (`03-write-plan.md`): felesleges, és a teljes fázis újrafuttatására csábít, holott a feladat egy szűk, célzott javítás.

A fix-mód egy **szűkített belépő:** a megadott `Must Fix` megállapításokat javítod célzottan, **nem írod újra az egész plant**. A `*-input-from-prev.md` fájlokat fix-módban **teljesen figyelmen kívül hagyod** (sem nem olvasod, sem nem írod) — IP1/6. (Ellenkező esetben egy olcsóbb LLM hajlamos elölről kezdeni a fázist — ez tilos.) A normál flow minőségi kapui (a fázis „Minőségellenőrzés” szekciója + Constitution Check) a javított részekre továbbra is érvényesek — **csak a javított részekre**, nem a teljes dokumentumra.

> **Szekció-ID-k fix-módban (PID1):** a meglévő `[P-…]` azonosítókat **nem nevezed át és nem törlöd** — a `tasks.md` rájuk hivatkozik, egy átnevezés az összes érintett taskot elszakítja a tervétől. Új szekció beszúrásakor **új ID**; szekció törlésekor jelezd az orchestrátornak, hogy a rá hivatkozó taskokat a 04 fixernek is rendeznie kell.

### Két belépési alak
1. **Közvetlen javítás:** a `Must Fix` megállapítás a plant érinti (a célfázis 03) — célzottan javítod.
2. **Downstream re-deriválás (reconciliation):** a hurok feljebb (02, spec) javított, és a plant a megváltozott spec-hez kell **összehangolni**. Ez **célzott reconciliation, nem teljes újraírás:** csak a megváltozott spec-szakaszokhoz tartozó plan-részeket igazítod, a lezárt `plan-questions.md` döntéseket **megőrzöd**.

### Bemenet
- A planre szűrt `Must Fix` lista (kategória + leírás + `fájl:hely`), vagy reconciliation esetén a megváltozott upstream (spec) összefoglalója.
- A `plan.md` és a `plan-questions.md` aktuális állapota.

### Auto-javítható vs kérdezni kell (a határvonal)

| Magától javítsd (auto) | Kérdésbe tedd (`plan-questions.md` új `Knn`) |
|---|---|
| Lefedettségi/komponens-leképezés pontosítása, naming-egységesítés, tervezési duplikáció összevonása, spec-változás átvezetése a planbe | Megfigyelhető viselkedést érintő technikai döntés (HTTP kód, retry policy, response mező), meghatározatlan komponens technológiai alapdöntése, spec-ellentmondás |

A `Must Fix`-et, amihez **valódi döntés** kell, **ne találd ki** — vedd fel új `Knn`-ként a `plan-questions.md` végére, és **ne kérdezd közvetlenül a felhasználót** (fix-módban nincs interaktív csatornád). A kérdezést az orchestrátor (`05-analyze`) végzi. (A határvonal ugyanaz, mint a normál plan-írásban: megfigyelhető viselkedést vagy technológiai alapdöntést érintő kérdést nem döntesz el magad.)

### Státusz (auto, `[analyze-loop]` marker)
A hurok a `plan.md` státuszát `[analyze-loop]` markerrel nyitotta vissza (pl. `Piszkozat [analyze-loop]`). Amíg a marker jelen van, **automatikusan** lépteted a státuszt, megerősítés-kérés nélkül:
- van nyitott `[ ]` kérdés a `plan-questions.md`-ben → `Nyitott kérdések vannak [analyze-loop]`;
- minden kérdés `[x]`, minden szekció rendben, minden schema artifact `Reviewed`, a célzott javítás kész → `Task írásra kész [analyze-loop]`.

A marker fel- és levételét az orchestrátor kezeli; te csak a státusz-értéket lépteted.

### Visszatérési összefoglaló (az orchestrátornak)
Adj vissza tömör összefoglalót: (a) mely `Must Fix`-eket / spec-változásokat vezettél át és hogyan, (b) milyen új `Knn` kérdéseket vettél fel a `plan-questions.md`-be (azonosítóval). A `plan.md`-t és a `plan-questions.md`-t te írod; az `analyze-report.md`-t **nem** — az az orchestrátoré.

- **`downstream-hatás:`** (D11) — kötelező mező: `nincs`, vagy `van — <mi változott, ami a következő fázist érinti>`. Ebből dönti el az orchestrátor, hogy kell-e egyáltalán elindítani a downstream fixereket. **Bizonytalanság esetén `van`**, a konkrét ok megnevezésével — a puszta „biztos, ami biztos” viszont nem ok.
