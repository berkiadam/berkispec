<!--
  KÖZÖS "artefaktum-hang" szabály (AV1) — a 02/03/04 fázisokhoz.
  Ez NEM önálló skill/agent, hanem megosztott szövegblokk, amelyet a telepítő
  (install-helper.py) build-time INLINE beágyaz a hivatkozó skill telepített
  változatába (a `<!-- INCLUDE:shared/artifact-voice.md -->` marker helyére).
  Hivatkozik rá: 02-write-spec, 03a-write-code-plan, 03b-write-test-plan, 04-write-tasks.
  Nincs frontmattere: a tartalma szó szerint bemásolódik. Itt szerkeszd.
-->

> **🔴 Artefaktum-hang (AV1) — a dokumentum az EMBERNEK szól, nem neked.** A `spec.md` / `plan.md` / `tasks.md` olvasója az implementáló (ember vagy ágens), **nem a te utasításaid címzettje**. Ezért a skill-szöveget **soha ne másold át** az artefaktumba:
>
> **A teszt a CÍMZETT, nem a formázás.** Tedd fel a kérdést: *„ha ezt a mondatot törlöm, elveszít-e az implementáló egy szükséges információt?"*
> - **Igen → marad** (legfeljebb átfogalmazva). Ilyen pl. egy gépi előfeltétel-lista („`oc` legyen bejelentkezve, namespace: `X`"), egy figyelmeztetés osztott környezetről, vagy egy sorrend-megkötés. **Ezeket kiemelheted** `[!IMPORTANT]` / `[!CAUTION]` blokkal — a kiemelés önmagában nem hiba, ha a tartalom az implementálónak szól.
> - **Nem, csak a rád vonatkozó szabályt ismétli → megy ki.**
>
> - **Ne vidd át a meta-utasításokat:** *„Tilos …"*, *„kötelező ellenőrizned …"*, *„menj végig …"*, *„ne felejtsd el …"*, *„a minőségellenőrzés bukik, ha …"*, *„SZIGORÚ SZABÁLY"*. Ezek a **te munkádra** vonatkoznak, nem a rendszer viselkedésére.
> **🔴 Kemény padló — a FORMA nem alku tárgya.** A címzett-teszt azt dönti el, hogy a **tartalom** marad-e; a **megfogalmazás** viszont akkor is átírandó, ha a tartalom jogos:
> - a **`🔴`** jelölés a skillek belső hangsúlyozása — artefaktumba **soha** nem kerül át (a semleges `[!IMPORTANT]`/`[!CAUTION]` igen);
> - a **„Tilos…" / „TILOS…"** imperatívusz artefaktumban **nem használható**, még akkor sem, ha a mögötte lévő megkötés valós.
>
> Ilyenkor **nem törlöd az információt, hanem átfogalmazod**: ❌ *„🔴 Tilos a statikus `:v1` tag használata"* → ✅ *„Az image tagje futásonként egyedi (`v1-<UTC időbélyeg>`); a statikus tag felülírása a rollbacket ellehetetlenítené."* Ugyanaz a tudás, semleges, leíró hangnemben.
> - **A szabályt DÖNTÉSSÉ fordítod.** Nem azt írod le, hogy mit tiltott meg neked a skill, hanem hogy **mi lett a döntés**. Példa:
>   - ❌ *„🔴 Tilos a statikus `:v1` tag használata, mert a rollback látszólagos lenne."*
>   - ✅ *„Az image tagje futásonként egyedi: `v1-<UTC időbélyeg>`."* — az indoklás pedig a `<sec:risks_and_decisions>` szekcióba kerül (a plan-ben), illetve a `<sec:risks>` szekcióba (a spec-ben).
>
> **Miért számít:** ezeket a dokumentumokat a downstream fázisok **gépiesen olvassák**. Egy bennmaradt imperatívusz félreérthető követelményként vagy taskként (ahogy egy „a spec.md állapotát frissíteni kell" DoD-pontból task lett), és a skill későbbi változásakor elavult másolatként ottmarad.
>
> **Ez nem a magyarázat tilalma:** az **indoklás** (miért így döntöttünk, mi a kockázat) továbbra is kell — csak a rá kijelölt szekcióban, **leíró** hangnemben.
