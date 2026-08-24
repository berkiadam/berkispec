




# Sepc rész: 


- kell egy utasítás neki, hogy ne olvasson be mindig mindnet: 


- le kell írni a spec gyártás elején, hogy ez egy 5 lépéses folyamat első lépése. 
	1. spec
	2. plan
	3. task 
	4. imlement
	5. validate
	
- a spec íráshoz kell egy külön kritikus, boncolgató skill. 

- kell legyen státusza a spec.md-enk 
- kell egy nyitott kérdések szekció az md ájl elejére, és azokat sorba le kell zárni, addig kell a spec -en iternálni, amíg nem fogynak azok le. 
	- lehet hogy így lehet kontextuson spórolni? 
	- lehet hogy minden körben lehet új kontextussal menni és a promt-ba beletenni, hogy: 
		- ha van nyitott kérdés, tedd fel és tisztázzuk, ha tisztáztuk, töröld ki
		- ha új nyitott kérdés jön be, akkor tegyük bele. 

- kell egy out of scope szekció

- fontos, hogy ami nem spec-be való azt ki kell dobni 
- fontos, hogy kell hivatkozott fájlok szekció. 

- fontos, hogy újra és újra fel kell tenni a kérdést új kontextust-ban, hogy mit változtatnál és pontosítanál rajta, amíg nem jut el odáig hogy semmit. 


----------------------------------------





KÉne egy bs-prepar-plan fázis: 
- data-model md-t is csinált, amiben felsorolta az enum-okat, bármit ami modell és központ
- test-convension ciklus szinten, ahov bemásolja azösszes 


bs-manual-test-summar: 

- implementáció végén adjon egy manuális teszt javaslatot: (ez egy új )
  - mit hogy kell elindítani
  - és milyen hívást adjon
  - és milyen eredményt vársz


- bs-help skill
- mindig relatív útvonlakat használjunk
- a cycle-desing-input.md-t mindig létre kell hozni, nem csak akkor ha volt brainsorm. 