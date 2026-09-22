---
theme: seriph
title: Az Agentic AI a Nagyvállalati Környezetben
info: |
  ## Az Agentic AI Fejlesztés Kihívásai és Illúziói
  Kihívások és illúziók a szabályozott pénzintézeti szektorban.
class: text-center
transition: slide-left
mdc: true
---

# Az Agentic AI a Nagyvállalati Környezetben

## Kihívások és illúziók a szabályozott pénzintézeti szektorban

<div class="pt-12 opacity-70">
  Infrastruktúra · Architektúra · Folyamat · Compliance · Szervezet
</div>

---
layout: statement
---

# „Ferrari motor a lovaskocsiban"

Egy transzformálatlan, bürokratikus szervezetre ráhúzott autonóm AI **kontraproduktív**.

<div class="pt-8 opacity-80 text-xl">
Hiába írja meg az ágens a kódot másodpercek alatt, ha a technikai adósság,<br>
a silózott szervezet és az „emberi sebességre" optimalizált folyamatok<br>
<b>hónapokra megakasztják</b> a tényleges szállítást.
</div>

---

# Paradigmaváltás: a chat-korszak vége

<div class="grid grid-cols-2 gap-8 pt-8">
<div>

### 🗨️ Chat-korszak
- Kérdezz–felelek chatbotok
- Az ember tesz mindent
- Széleskörű kísérletezés

</div>
<div>

### 🤖 Agent-korszak
- Tool-használat, adatfeldolgozás
- **Valódi munkavégzés** autonóm módon
- Célzott workflow-automatizálás

</div>
</div>

<div class="pt-10 text-center opacity-80">
A kérdés már nem „mit tud az AI", hanem <b>„hogyan skálázzuk biztonságosan az enterprise-ban".</b>
</div>

---
layout: default
---

# Vezetői összefoglaló (TL;DR)

- 🚦 **A szűk keresztmetszet áttevődik** — nem a kódolás lassú, hanem a jóváhagyás, a manuális tesztelés és a környezet-vándorlás. Az AI önmagában nem gyorsít.
- 🧠 **A legnagyobb kockázat percepciós** — a vezetők a demót látják, nem a „last mile"-t. Maguknak is használniuk kell az eszközöket.
- 👥 **A csapatmodell átalakul** — 10–15 fős squad helyett 4–5 fős „SWAT-csapat"; nem a kódolók száma, hanem az absztrakciós megértés számít.
- 🔒 **A compliance nem opció** — on-prem modellek, PII-maszkolás, IAM, auditálható reasoning path, tisztázott jogi felelősség (RACI).
- 💸 **A költség és a vendor-kitettség menedzselendő** — kemény token-limitek, hibrid routing, modell-agnosztikus AI Gateway az első naptól.
- 🔄 **Nem „véglegesre" tervezünk** — a tech gyorsabban változik, mint az alkalmazkodás; folyamatos javító hurkokra kell berendezkedni.

---
layout: section
---

# I. A vezetői illúziók

---

# A vezetői illúziók anatómiája

<div class="grid grid-cols-3 gap-6 pt-6">
<div class="p-4 rounded bg-gray-400 bg-opacity-10">

### 🎯 Last Mile
A demó látható, a **„következő 10–20 lépés"** nem: verifikáció, integráció, code review, üzemeltetés. Az érték itt keletkezik.

</div>
<div class="p-4 rounded bg-gray-400 bg-opacity-10">

### 🧠 „AI-pszichózis"
A vezetők csak a „happy path"-t látják. A valóság mérhető: **~3× több hallucináció**, **~10× hosszabb** válaszidő. Tünet: hype-vezérelt leépítés.

</div>
<div class="p-4 rounded bg-gray-400 bg-opacity-10">

### 🔄 Mozgó célpont
A tervezési ciklus hónap, a tooling hét. Mire kész a folyamat, **már elavult**. Nem „véglegesre" optimalizálunk.

</div>
</div>

<div class="pt-10 text-center text-lg opacity-90">
A legolcsóbb ellenszer: a döntéshozók <b>maguk is intenzíven használják</b> az eszközöket.
</div>

---
layout: section
---

# II. Technológia & Architektúra

---

# Infrastrukturális béklyók

<div class="grid grid-cols-2 gap-8 pt-4">
<div>

### Az ágens-ökoszisztéma standardja
- **Linux/POSIX** — izolált, konténerizált futtatás
- **Python / TypeScript** — „day-zero" keretrendszer-támogatás

</div>
<div>

### A banki valóság
- Lezárt **Windows** image (adminjog, csomag, shell tiltva → WSL2)
- Monolitikus **Java** backend (késő community-támogatás)
- **Legacy mag**: mainframe / COBOL / batch

</div>
</div>

<div class="pt-8 opacity-80">
A súrlódás nem a nyelv képességéből fakad — a lezárt környezet felemészti az ágens sebességelőnyét.
</div>

---

# A „Headless" / API-first fordulat

- A jövő rendszere **headless**: az ágens nem GUI-n „kattintgat", hanem **API-kon** operál.
- Minden funkció programozottan elérhető — különben az ágens „vak" a folyamatokra.
- Új governance-réteg kell: *ki / melyik ágens / milyen scope / melyik rendszerhez*.

<div class="pt-4" />

### 🔌 MCP (Model Context Protocol)
Az ágens–eszköz integráció kialakuló *de facto* szabványa: egységes felület az eszközök felfedezésére és hívására.

> Kétélű: rendet tesz az ad-hoc integrációk helyett, **de** új támadási felület → minimális jogosultság + központi IAM alá kell vonni.

---
layout: section
---

# III. Folyamat & Csapat

---

# A csapatstruktúra felbomlása

<div class="text-sm">

```mermaid
graph TD
    subgraph Hagyományos [Hagyományos Squad · 10-15 fő]
        PM[Project Manager] --> ITBA[Üzleti Elemző]
        ITBA --> Arch[Architekt]
        Arch --> Backend[3-4 Backend Fejlesztő]
        Arch --> Frontend[2-3 Frontend Fejlesztő]
        Backend --> QA[2-3 Tesztelő]
        Frontend --> QA
    end

    subgraph SWAT [Agentic SWAT Team · 4-5 fő]
        ITBA2[Spec. Mérnök / ITBA] --> AgentNetwork{AI Ágens Hálózat}
        SME[Üzleti Szakértő] --> AgentNetwork
        Auditor[AI Auditor] --> AgentNetwork
        QA2[QA / Prompt Eval] --> AgentNetwork
        AgentNetwork -.-> Code(Backend Kód & Tesztek)
    end
```

</div>

<div class="text-center opacity-80">
Nem a kódolók száma számít, hanem a rendszer <b>absztrakciós megértése</b>.
</div>

---

# Az új SWAT-csapat szerepei

- **Specifikációs Mérnök / ITBA** — strukturált üzleti igény; tisztázza az ágens kérdéseit (`spec.md`).
- **AI Auditor** — nem szintaxist néz, hanem architektúrát, biztonságot, teljesítményt.
- **Domain Szakértő (SME)** — üzleti logika és banki compliance validálása.
- **QA / Prompt Eval Engineer** — az ágens-generálta teszt-szcenáriók és Evals minősége.
- **Frontend / UX Mérnök** — a „pixel-perfect" UI az AI gyengébb területe.

<div class="pt-6 p-3 rounded bg-amber-400 bg-opacity-10">

⚠️ **Két új kockázat:** a *tehetség-utánpótlás* (honnan lesz a következő szenior?) és az *automation complacency* (a felülvizsgálat gumibélyegzővé silányul).

</div>

---

# Az SDLC anakronizmusa

A szűk keresztmetszet áttevődik a kódolásról a **bürokratikus jóváhagyásra**:

- 🐢 **Lassú review-lánc** — napok/hetek, míg az ágens tucat iterációt tenne.
- 🖱️ **Manuális tesztelés túlélése** — Excel-alapú kattintgatás vs. percenkénti szállítás.
- 🧪 **Félreértett automatizálás** — utólagos, felületes (unit/API), hiányzó **E2E**.
- 🧫 **Tesztadat-probléma** — valósághű, de PII-mentes (szintetikus) adat kell.
- 🪜 **Environment Jumping** — Dev→Test→UAT→Pre-prod→Prod, CAB-kapukkal, hetekig.

<div class="pt-4 text-center opacity-80">
Ha az ágens 1 perc alatt javít, de az élesítés 6 hét → a hatékonyság <b>nullára esik</b>.
</div>

---

# Új CI/CD: a környezetek sűrítése

```mermaid
graph LR
    subgraph Régi [Lassú, Hagyományos CI/CD]
        A[Kódolás] --> B[Cross Review] --> C[CI Build] --> D[DEV] --> E[Manuális QA] --> F[UAT]
    end
    subgraph Új [AI-vezérelt · Sűrített]
        S1[spec.md] --> S2[Ágens Kódol] --> S3[Eldobható Sandbox] --> S4[AI CAB Audit] --> S5[PROD + Feature Flag]
    end
```

- **Eldobható Sandbox** — feature-enkénti izolált környezet, E2E Evals, majd megsemmisül.
- **AI-asszisztált Governance** — Governance Ágens előminősít; kritikusnál marad emberi pont.
- **Feature Flag Release** — Prodra kerül, de kapcsoló mögött; a *bekapcsolás* üzleti döntés.
- **Shift-Left Specifikáció** — strukturált `spec.md` (pl. `berkispec`) hajtja a pipeline-t.

---
layout: section
---

# IV. Biztonság, Compliance & Költség

---

# Adatvédelem, IAM & ágens-biztonság

<div class="grid grid-cols-2 gap-8 pt-2">
<div>

### 🛡️ Compliance (DORA, GDPR, EU AI Act, MNB)
- On-prem / private cloud LLM-ek (Llama, Mistral)
- PII / banktitok **maszkolás** prompt előtt
- Auditálhatóság, diszkriminációmentesség
- **Üzletmenet-folytonosság**: fallback, „degraded mode"

</div>
<div>

### 🔑 IAM & ágens-kockázatok
- „Nem emberi identitások" burjánzása → vault, rövid scope-olt token
- **Indirekt prompt injection** (pl. fertőzött PDF)
- **Least privilege** az eszközökre
- **Modell-ellátási lánc**: poisoned weights, provenance

</div>
</div>

---

# Költség & Token-ökonómia

<div class="grid grid-cols-2 gap-8 pt-4">
<div>

### 🔥 „Rogue Agent" kockázat
Végtelen ciklus → kontrollálatlan költség.

*Dokumentált esetek:*
- ~**félmilliárd \$** limit nélkül
- Uber: éves keret **4 hónap** alatt
- Microsoft: szolgáltatóváltás költség miatt

</div>
<div>

### 🎛️ Kontroll-mechanizmusok
- **Hard-limit**, token-keret, időkorlát
- **Tokenmaxxing** — tudatos adagolás, csak magas prioritásra
- **Hibrid routing** — olcsó modell rutinra, drága a komplexre

</div>
</div>

---
layout: section
---

# V. Irányítás & Kockázat

---

# Fokozatos autonómia (bizalmi létra)

```mermaid
stateDiagram-v2
    [*] --> Shadow
    Shadow: 1. Árnyék mód
    Shadow --> Advisory: megbízhatóság > küszöb
    Advisory: 2. Tanácsadó (human-in-the-loop)
    Advisory --> Controlled: gyakori egyetértés
    Controlled: 3. Szabályozott autonómia
    Controlled --> [*]
```

- **Shadow** — fut és naplóz, de **nem cselekszik**; összevetés az emberi lépésekkel.
- **Advisory** — javasol és előkészít, de **ember hagyja jóvá**.
- **Controlled** — önállóan cselekszik, de kill switch + szűk scope + értékhatár mellett.

---

# Observability, döntéshozatal, tudás, jog

<div class="grid grid-cols-2 gap-6 text-sm pt-2">
<div>

### 👁️ Observability & AgentOps
- **Reasoning path** naplózása (miért döntött)
- Prompt-verziózás + Evals + rollback
- **Nem-determinizmus** → visszajátszhatóság

### 🏢 Döntéshozatal & változáskezelés
- A vezetői illúzió: „csak add oda" → **Harness Engineering**
- Improvement Loops (dedikált buffer)
- Belső **CoE**; **ROI** áramlás-metrikákkal (nem kódsor)

</div>
<div>

### 📚 Tudásbázis (Garbage In/Out)
- Elavult Confluence, szétesett API-k
- Tisztítás + belső **RAG** kell a hallucináció ellen

### ⚖️ Jogi felelősség
- Új **RACI** az AI-generált kódra/élesítésre
- **IP / licenc-provenance** (copyleft kontamináció) → SCA a pipeline-ban

</div>
</div>

---

# Beszállítói kitettség & modell-agnosztikusság

A piac (OpenAI, Anthropic, Google) gyorsan változik árban, képességben, szabályozásban. **Egyetlen gyártóhoz kötődni = a teljes pipeline kockázata.**

```mermaid
graph TD
    Internal[Banki AI Ágensek] --> Gateway{AI Gateway · pl. LiteLLM}
    Gateway -->|Routing / Fallback| OpenAI[OpenAI GPT]
    Gateway -->|Rate limit / Költségkeret| Anthropic[Anthropic Claude]
    Gateway -->|PII Masking| Local[Privát On-Premise LLM]
    style Gateway fill:#f9f,stroke:#333,stroke-width:2px
```

<div class="text-center opacity-80">
<b>AI Gateway / absztrakciós réteg az első naptól</b> — a „motor" leállás nélkül cserélhető.
</div>

---
layout: section
---

# Cselekvési ütemterv

---

# Fázisolt roadmap

```mermaid
graph LR
    P0[Fázis 0<br/>Alapozás] --> P1[Fázis 1<br/>Kontrollált Pilot] --> P2[Fázis 2<br/>Folyamat-sűrítés] --> P3[Fázis 3<br/>Skálázott Autonómia]
```

<div class="grid grid-cols-2 gap-6 text-sm pt-4">
<div>

**Fázis 0 — Alapozás**
RAG + tudásbázis, AI Gateway, IAM/secrets, RACI, CoE. *Enélkül minden instabil.*

**Fázis 1 — Kontrollált pilot**
1 alacsony kockázatú domain, SWAT-csapat, SDD, **Shadow mód**, Harness tréning.

</div>
<div>

**Fázis 2 — Folyamat-sűrítés**
Sandbox + E2E Evals, automatizált CAB, Feature Flag, **ROI-metrikák**.

**Fázis 3 — Skálázott autonómia**
Advisory → Controlled, több domain, headless/MCP kiterjesztés, folyamatos Evals.

</div>
</div>

---
layout: center
class: text-center
---

# Összefoglalva

Az Agentic AI **nem eszközkérdés, hanem szervezeti transzformáció**.

<div class="pt-6 text-xl opacity-80">
A kódolás megszűnt szűk keresztmetszet lenni —<br>
a verseny most a <b>folyamatok, a governance és a kultúra</b> átalakításán dől el.
</div>

<div class="pt-12 opacity-60">
Köszönöm a figyelmet!
</div>
