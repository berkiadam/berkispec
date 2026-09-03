<!--
  KÖZÖS leírás a FÁZISOK KÖZÖTTI ÁTADÁSRÓL (`*-input-from-prev.md`) — IP1.
  Ez NEM önálló skill/agent, hanem megosztott szövegblokk, amelyet a telepítő
  (install-helper.py) build-time INLINE beágyaz a hivatkozó skill telepített
  változatába (a `<!-- INCLUDE:shared/input-from-prev.md -->` marker helyére).
  Hivatkozik rá: 01-add-cycles, 02-write-spec, 03a-write-code-plan, 03b-write-test-plan, 04-write-tasks,
  07-validate. A quick-flow NEM (háromfázisú, egy kontextusban fut).
  A skill a marker KÖRÉ írja a saját, fázis-specifikus részét (mit olvas be,
  mely fájlokba írhat) — ez a blokk csak a közös szabályokat tartalmazza.
  Nincs frontmattere: a tartalma szó szerint bemásolódik. Itt szerkeszd.
-->

**Mire jó (IP1):** egy fázisban gyakran felszínre kerül olyan információ, ami **értékes, de nem oda tartozik** — túl technikai, túl részletes, vagy egyszerűen a következő fázis dolga. A skillek eddig ezt **törlésre** utasították (pl. a 02: „ha egy mondat technológiát, fájlnevet, függvényt nevez meg → az plan-be való, töröld a spec-ből"), vagyis az infó elveszett. Ezek a fájlok adnak neki célt a kuka helyett.

**A fájlok** — mind a ciklus mappájában (`specs/cycle-NN-<cycle-name>/`):

| Fájl | Ki írhat bele | Ki fogyasztja |
|---|---|---|
| `spec-input-from-prev.md` | 01-add-cycles | **02**-write-spec |
| `plan-input-from-prev.md` | 01, 02 | **03**-write-plan |
| `tasks-input-from-prev.md` | 02, 03 | **04**-write-tasks |
| `validate-input-from-prev.md` | 03, 04 | **07**-validate |

**Egy fázis több fájlba is írhat** ugyanabban a futásban, ha az infót szét kell szórni (pl. a 02-ben felmerülő technikai részlet a `plan-input`-ba, a belőle következő tesztelési előfeltétel a `validate-input`-ba megy).

> A **06-implement** szándékosan **nem** kap ilyen fájlt: az eleve beolvassa a `plan.md`-t és a `tasks.md`-t, tehát az implementációs részlet oda tartozik, nem külön csatornába.

**Tétel-formátum** (checkbox-lista, a kérdés-fájlok mintájára):

```md
<!-- INCLUDE:lang/input-from-prev.md#IP1-tetel-formatum -->
```

**Szabályok:**

1. **Sosem törlünk.** A lezárt tételt `[x]`-szel jelöljük, és egy soros megjegyzést írunk mellé (`→ beépítve: <hova>` vagy `→ elvetve: <miért>`). A szöveg és a döntés megmarad.
2. **Nem blokkol** — ellentétben a `*-questions.md` nyitott kérdéseivel, egy nyitott `[ ]` tétel **nem állítja meg** a fázist menet közben. **De a fázis lezárásakor nem maradhat nyitott tétel:** a minőségellenőrzés kötelező pontja, hogy minden tétel vagy **beépült**, vagy **explicit indokkal elvetett**. Csendben átlépni rajta tilos.
3. **Nem kérdez.** Határvonal a `*-questions.md`-hez: a **kérdés** = „nem tudom, döntsd el"; az **input-from-prev** = „tudom, de nem ide tartozik". Ha egy tétel eldöntendő kérdés **is**, akkor kérdésként vedd fel a saját fázisod `*-questions.md`-jébe — az input-fájl csak átad, nem kérdez.
4. **Üres vázat ne készíts.** A fájl **csak akkor jön létre**, ha van mit beleírni. Ha nincs átadandó infó, a fájl ne létezzen — a fogyasztó fázis a hiányát nem tekinti hibának.
   > **Egyetlen kivétel: a `spec-input-from-prev.md`-t a `01-add-cycles` MINDIG létrehozza**, üres sablonnal is. Indok: ez a lánc **első** átadó fájlja, és a 01 az egyetlen fázis, ami a ciklus mappáját nulláról építi — ha itt hiányzik, a 02 nem a „nincs átadandó infó" esetet látja, hanem azt, hogy a csatorna nem is létezik, és a 03-tól kezdve senki nem tudja, hogy egyáltalán lett volna hova írni. **A többi három fájlra (`plan-`, `tasks-`, `validate-input-from-prev.md`) a fenti szabály változatlanul érvényes.**
   > **Az üres váz nem felszólítás a kitöltésre:** ha nincs átadandó tétel, a lista maradjon üres — ne találj ki tételeket, hogy „ne legyen üres a fájl".
5. **Ami nem a következő fázisba, hanem egy későbbi CIKLUSBA tartozik**, az **nem ide megy**, hanem a `specs/roadmap.md`-be (új vagy meglévő ciklus bejegyzéséhez). Ezekbe a fájlokba kizárólag az **aktuális ciklus** további fázisainak szánt infó kerül.
6. **Az önjavító hurkok (05/07/09 fix-módjai) ezeket a fájlokat teljesen figyelmen kívül hagyják** — sem nem olvassák, sem nem írják. A fix-mód célzott javítás egy `<status:must_fix>` listára; az átadás-mechanizmus újrafuttatása ott csak költség és zaj lenne. (Az 05 **read-only diagnózisa** ettől külön dolog: az jelzi, ha egy tétel nyitva maradt — lásd az 05 skillt.)
7. **Ne írd át a másik fázis artefaktumát.** Ha a 02-ben plan-szintű részlet merül fel, azt a `plan-input-from-prev.md`-be írod — **nem** a `plan.md`-be (az még nem is létezik, vagy nem a te fázisod gazdálkodik vele).
