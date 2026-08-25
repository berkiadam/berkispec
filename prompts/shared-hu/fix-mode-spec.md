<!-- Forrás-jegyzet: a 02-write-spec skill Fix-mód szekciója, kiemelve, hogy a
     spec-fixer subagent prompt build-time beemelhesse (BD14/b). Így a fixernek
     NEM kell beolvasnia a teljes 02-write-spec.md-t. Egy helyen szerkeszd. -->
## Fix-mód (analyze-hurok belépő)

> **Mikor aktív:** ezt a szekciót az `05-analyze` önjavító hurka indítja az `agents/spec-fixer.md` wrapperen keresztül — **nem** a normál spec-írás. A bemenet egy konkrét `<status:must_fix>` lista, nem teljes újrafutás.

> **Skill-beolvasás nem kell (D13):** a fix-módhoz szükséges összes szabály ebben a promptban van — a fázis „Minőségellenőrzés” szekciója is. **Fix-módban ne olvasd be a teljes fázis-skillt** (`02-write-spec.md`): felesleges, és a teljes fázis újrafuttatására csábít, holott a feladat egy szűk, célzott javítás.

A fix-mód egy **szűkített belépő:** a megadott `<status:must_fix>` megállapításokat javítod célzottan, **nem írod újra az egész specet**. A `*-input-from-prev.md` fájlokat fix-módban **teljesen figyelmen kívül hagyod** (sem nem olvasod, sem nem írod) — IP1/6. (Ellenkező esetben egy olcsóbb LLM hajlamos elölről kezdeni a fázist — ez tilos.) A normál flow minőségi kapui (a fázis „Minőségellenőrzés” szekciója) a javított részekre továbbra is érvényesek — **csak a javított részekre**, nem a teljes dokumentumra.

### Bemenet
- A spec-re szűrt `<status:must_fix>` lista (kategória + leírás + `fájl:hely`).
- A `spec.md` és a `spec-questions.md` aktuális állapota.

### Auto-javítható vs kérdezni kell (a határvonal)

| Magától javítsd (auto) | Kérdésbe tedd (`spec-questions.md` új `Knn`) |
|---|---|
| Lefedettségi rés szöveges pótlása, naming-egységesítés, megfogalmazás-pontosítás, duplikált követelmény összevonása | Spec-szintű ambiguitás, hiányzó vagy nem eldönthető elfogadási feltétel, meghatározatlan viselkedés, üzleti döntés |

A `<status:must_fix>`-et, amihez **valódi döntés** kell, **ne találd ki** — vedd fel új `Knn`-ként a `spec-questions.md` végére (a normál flow szerint), és **ne kérdezd közvetlenül a felhasználót** (fix-módban nincs interaktív csatornád). A kérdezést az orchestrátor (`05-analyze`) végzi, fázis-fejléccel.

### <field:f_status> (auto, `[analyze-loop]` marker)
A hurok a `spec.md` státuszát `[analyze-loop]` markerrel nyitotta vissza (pl. `<status:draft> [analyze-loop]`). Amíg a marker jelen van, **automatikusan** lépteted a státuszt, megerősítés-kérés nélkül (eltérően a normál flow „megerősítés a státuszváltás előtt" szabályától):
- van nyitott `[ ]` kérdés a `spec-questions.md`-ben → `<status:open_questions> [analyze-loop]`;
- minden kérdés `[x]` és a célzott javítás kész → `<status:ready_for_plan> [analyze-loop]`.

A marker fel- és levételét az orchestrátor kezeli; te csak a státusz-értéket lépteted, a markert változatlanul hagyod.

### Visszatérési összefoglaló (az orchestrátornak)
Adj vissza tömör összefoglalót: (a) mely `<status:must_fix>`-eket javítottad és hogyan, (b) milyen új `Knn` kérdéseket vettél fel a `spec-questions.md`-be (azonosítóval). A `spec.md`-t és a `spec-questions.md`-t te írod; az `analyze-report.md`-t **nem** — az az orchestrátoré.

> **🔴 Teljességi elszámolás — egy tétel sem tűnhet el némán.** A kapott `<status:must_fix>` lista **minden** tétele jelenjen meg az összefoglalódban **pontosan egy** ágon: vagy (a) — megjavítottad, és leírod hogyan —, vagy (b) — `Knn` kérdésként felvetted, mert valódi döntést igényel. Harmadik lehetőség nincs: a „nem fértem hozzá", a „majd a következő körben" és a csendes kihagyás **nem** elfogadható. Ha egy tételt sem javítani, sem kérdéssé alakítani nem tudsz, azt **mondd ki egy sorban, azonosítóval és indokkal** — az orchestrátornak erre külön ága van. A tételekre mindig a **kapott azonosítóval** hivatkozz (`AF-NN` / `AX-NN`), soha ne parafrazeáld a szövegüket: erre épül a hurok túlélés-szabálya.

- **`downstream-hatás:`** (D11) — kötelező mező: `nincs`, vagy `van — <mi változott, ami a következő fázist érinti>`. Ebből dönti el az orchestrátor, hogy kell-e egyáltalán elindítani a downstream fixereket. **Bizonytalanság esetén `van`**, a konkrét ok megnevezésével — a puszta „biztos, ami biztos” viszont nem ok.
