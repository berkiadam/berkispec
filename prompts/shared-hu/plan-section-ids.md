<!-- Forrás-jegyzet: ezt a szekciót a 03a-write-code-plan.md ÉS a 03b-write-test-plan.md
     skill emeli be (build-time INCLUDE). Egy helyen szerkeszd. -->
### 🔴 Stabil szekció-azonosítók (PID1) — a tasks.md ezekre hivatkozik

**Minden végrehajtható terv-szekció címébe stabil azonosítót írsz**, közvetlenül a `###` után:

```md
### [P-CONFIG] Konfigurációs rendszer és config-fájlok
### [P-REDIS] Redis kapcsolódás kiterjesztése
### [P-E2E-UI] Playwright felületi E2E
```

| Szabály | Mechanika |
|---|---|
| **Formátum** | `[P-<NÉV>]` — nagybetűs, kötőjeles, 1–2 szó, a szekció tartalmára utal. Sorszám **nem** része (`[P-3-1]` tilos). |
| **Ki kap ID-t** | **Csak végrehajtható terv-szekció:** a `<sec:planned_changes>` és a `<sec:test_specification>` / `<sec:testing_strategy>` alszekciói — ahol az van leírva, **mit kell csinálni**. |
| **Ki NEM kap** | `<sec:goal_and_approach>`, `<sec:affected_components>` (leltár), `<sec:environment_coords>` (leltár), `<sec:execution_order>`, `<sec:risks>`, `<sec:new_dependencies>`, IP1-szekciók. Ezek **nem lehetnek** task-hivatkozás célpontjai (E). |
| **Egyediség** | Egy ID egyszer szerepelhet a plan-ben. |
| **Stabilitás** | Egy kiadott ID **soha nem változik** — akkor sem, ha a szekció sorszáma eltolódik, átnevezed, vagy a fejezet átkerül máshova. Törölt szekció ID-ja **nem használható újra**. Új szekció (pl. az analyze-hurok szúrta be) **új ID-t** kap. |
| **Miért** | A `tasks.md` sorszám helyett ID-re hivatkozik. Ha egy javítás beszúr egy `§3.10`-et, a sorszámok elcsúsznak, és a taskok **némán rossz szekcióra mutatnak** — az ID ezt kizárja. |
| **Ki adja ki** | A `<sec:planned_changes>` és a nem-teszt szekciók ID-jait a `03a`, a teszt-szekciókét a `03b`. A `03b` **soha nem nevez át és nem töröl** meglévő ID-t. |

_Sorszámot használhatsz a cím olvashatóságáért (`### 3.1 [P-CONFIG] …`), de a **hivatkozási kulcs mindig az ID**._
