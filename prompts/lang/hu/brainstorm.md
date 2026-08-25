<!--
  A `brainstorm` PROJEKT-NYELVI blokkjai (9.4 kiemelés).
  Ezt a fájlt a telepítő build-time emeli be az INCLUDE markerek helyére, a
  választott PROJEKT-nyelv (`PROJECT_LANG`) szerint; a marker alakja
  `lang/brainstorm.md#<horgony>`.
  A blokkok SZÓ SZERINT kerültek ide — ne fogalmazd át, ne egységesítsd.
  Az ANCHOR sorok NEM részei a beemelt szövegnek, csak határolók (8.9).
  FIGYELEM: ebbe a vezető jegyzetbe ne kerüljön komment-lezáró szekvencia.
-->

<!-- ANCHOR:BS4-gitignore-felajanlas -->
> *„A `.bs-brainstorm/` mappa most nincs kizárva a verziókezelésből. Ezek nyers, félbehagyott munkafájlok — nem leadandók, és a belőlük desztillált `cycle-design-input.md` amúgy is commitba kerül. Javaslom felvenni a `.gitignore`-ba a `.bs-brainstorm/*` bejegyzést. Felvegyem?"*

<!-- ANCHOR:BS2-munkafajl-csontvaz -->
# Brainstorm NN — <téma egy sorban>

Státusz: Folyamatban   ·   Indult: <YYYY-MM-DD>   ·   Utolsó frissítés: <YYYY-MM-DD>

## 1. Cél / kérdés

<Mit akarunk eldönteni ebben a sessionben, 2-4 sorban. Ha a téma menet közben
szűkül vagy tolódik, ezt a szekciót pontosítsd — de a régi megfogalmazást ne
töröld, tolj alá egy „Pontosítás:" sort.>

## 2. Feltárt tények

<Egy tény = egy sor, forrással. A forrás kód esetén `fájl:sor`, doksinál a
fájlnév. A bizonytalan állítás elé „(bizonytalan)".>

- ...

## 3. Alternatívák és trade-offok

<Opciónként: mi ez röviden · mit ad · mit adunk fel érte · mit érint a
rendszerben. Ha egy opció kiesett, ne töröld: jelöld „(elvetve: <miért>)".>

### A) ...

## 4. Döntések

<Mit döntöttünk el, és egy mondatban miért. Leíró hangnemben — ez lesz a
`cycle-design-input.md` teste.>

- ...

## 5. Nyitott kérdések

<Élő, pipálható lista. Ami eldőlt: pipa + a döntés a 4. szekcióba. A kipipált
tételt ne töröld.>

- [ ] ...

## 6. Javasolt ciklus-vágás

<Önállóan lefejleszthető és tesztelhető egységek, sorrendben, függőségekkel.
Egységenként: rövid cél + miből látszik, hogy kész. Ez a `01-add-cycles`
bemenete. Amíg nincs meg, hagyd a „(még nem érett meg)" jelölést.>

- ...

## 7. Napló

<Körönként 1-2 sor: mi történt, mi változott. Ide kerülnek a témán kívül
felnyílt, külön sessiont igénylő szálak is.>

- <YYYY-MM-DD> — ...
