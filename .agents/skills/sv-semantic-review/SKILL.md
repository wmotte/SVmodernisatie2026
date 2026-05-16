---
name: sv-semantic-review
description: Kritische semantische beoordeling van een gemoderniseerde vers-range — in-context door het agent-model zelf, geen externe LLM. Detecteert false friends, idiomatische mismatches, concordantietwijfel, en spiegelt de modernisatie tegen HSV (Herziene Statenvertaling) om taalfouten / semantische missers / drempel-archaïsmen op te sporen die door bestaande linters niet worden gevangen. Vervangt de oude `scripts/semantic_review.py` (externe embeddings-aanroep). Roep aan binnen `sv-batch-orchestrate` Stap 3.6, of zelfstandig voor een ad-hocbeoordeling van een bestaande vers-range.
---

# sv-semantic-review — beoordelingsprotocol

Deze skill draait **in de orchestratorcontext** (het agent-model zelf). Geen
externe LLM-aanroep, geen netwerkronde per vers — het agent-model doet de redenering
zelf op basis van de modernisatietekst, het SV1657-origineel, de Griekse
brontekst, buurverzen, en concordantie-matches uit `sv-memory`.

Werkdirectory:
`/Users/wmotte/Desktop/projects/SVmodernisatie2026/`.

## Wanneer aanroepen

- **Binnen `sv-batch-orchestrate` Stap 3.6**: na validator + alle lints
  op een nieuwe batch van 3 verzen.
- **Zelfstandig**: gebruiker vraagt om kritische beoordeling van een
  bestaande vers-range — bv. "review LUK 1:11-13".

Niet voor introductie / epiloog (geen brontekst, geen kanttekeningen,
geen concordantie-as).

## Stap 1 — laad de te beoordelen verzen

Lees `output/<BOEK>/<BOEK>.<H>.json` **met de Read-tool** — niet via een
inline Bash-python-dump. De Read-tool houdt de JSON-inhoud uit de
stdout-stroom; een `python3 -c "... print(...)"` echoot het hele bestand
verbatim de orchestratorcontext in.

Pak per batch-vers: `verse_number`, `original`, `modernized`,
`source_text`. Lees daarnaast vers `N-1` en `N+1` voor idiomatische
continuïteit (mag ontbreken aan de randen van het hoofdstuk).

## Stap 2 — concordantie-context per vers

Voor elk vers in de range: query sv-memory met het SV-origineel, top-3
matches, eigen vers uitgesloten:

```bash
uv run python scripts/memory.py query \
    --from-output output/<BOEK>/<BOEK>.<H>.json --verse <V> \
    --k 3 --axis sv --terse > /tmp/svsr_mem_<V>.json
```

`--from-output ... --verse <V>` haalt het SV-origineel uit de output-JSON
en sluit het bevraagde vers zelf uit — **geen inline-python-extractie van
de zoek-tekst, geen shell-quoting** van kanttekeningen / quotes / `$refs$`.
`--terse` drop `source_text` (Griekse brontekst); de concordantie-bewijslast
zit in `sv` + `modern`.

**Redirect naar `/tmp/svsr_mem_<V>.json` en lees met de Read-tool** — zo
blijft de volledige query-JSON (3 volle verspaare per vers) uit de
orchestratorstdout. Uitvoer is JSON met
`{results: [{book, chapter, verse, sv, modern, similarity}, ...], total_in_db}`.
Bewaar de relevante matches in-context per vers — gebruikt in stap 3 als
feitelijke onderbouwing van concordantie-twijfel.

Foutgevallen:

- **Lege database / geen matches** (`total_in_db=0` of `results=[]`): ga door
  zonder concordantie. Concordantiebevindingen worden dan strikt
  overgeslagen — geen evidentie.
- **Query faalt** (bv. `GOOGLE_API_KEY` ontbreekt of API-fout): noteer
  in eindverslag dat concordantie-context niet beschikbaar was; doe
  alleen false-friend / idiomatic.

## Stap 2.5 — HSV-spiegel laden

De HSV (Herziene Statenvertaling) is een externe parallel-modernisatie
van de SV. **Niet normatief** voor dit project (zie `MODERNISATIE.md
§2.7` en §3) — en bovendien **vrijer** dan onze modernisatie: HSV
heeft regelmatig exegese in de hoofdtekst (subject/object invullen,
verklarende bijvoeglijke naamwoorden), eigen kanttekeningen
(`<HSV: …>` / `<HSV-aant: …>`), incidentele eerbiedshoofdletters, en
herstructurering van latinate participia naar finiete werkwoord-
chains. Die keuzes nemen wij *niet* over.

De waarde van de HSV-spiegel is daarom **beperkter** dan een
formeel-equivalente parallel zou zijn: zij dient vooral om
drempel-archaïsmen te bevestigen die wij gemist hebben, en om
aantoonbare lexicale/grammaticale fouten in onze tekst te onthullen.
Stylistische afwijkingen van de HSV zijn standaard "HSV-keuze, geen
bewijs" en mogen geen bevinding opleveren.

### 2.5.1 Diff verversen

Vóór het lezen, regenereer de diff zodat hij de actuele
`output/<BOEK>/<BOEK>.<H>.json` reflecteert (de subagent kan zojuist
verzen geschreven hebben):

```bash
uv run python scripts/compare_hsv.py <BOEK> <H>
```

Schrijft `docs/diff_hsv_<BOEK>_<H>.json` op basis van onze output en
`hsv/<BOEK>/<BOEK>.<H>.json`. **Let op het `diff_hsv_`-prefix** —
verschilt van het SV2027-pad `docs/diff_<BOEK>_<H>.json`, dat (voor
Lucas) bestaat als post-hoc archief en hier *niet* gebruikt wordt.

### 2.5.2 Foutgevallen

- **`hsv/<BOEK>/<BOEK>.<H>.json` ontbreekt**: het script meldt dat
  fetch eerst nodig is. Sla HSV-spiegel volledig over voor deze batch;
  rapporteer in eindverslag dat de spiegel niet beschikbaar was. Géén
  blokker — beoordeling gaat door op false-friend / idiomatische /
  concordantie.
- **`hsv` is leeg-string voor één specifiek vers**: zou bij correct
  gefetchte HSV niet moeten voorkomen (HSV staat 1-op-1 per vers
  zonder bundeling of versnummer-prefix), maar als het toch gebeurt:
  sla dat ene vers over in de spiegel; vermeld in eindverslag.
- **`compare_hsv.py` non-zero exit / crash**: noteer in eindverslag,
  ga door zonder spiegel.
- **Intro / epiloog**: HSV heeft geen apart intro- of epiloog-veld;
  `compare_hsv.py` zet `hsv: null` met status `"no_hsv_equivalent"`.
  Dit is geen foutgeval — gewoon overslaan voor intro/epiloog
  (deze skill draait sowieso niet op intro/epiloog, zie sectie boven).

### 2.5.3 Inlezen

Lees `docs/diff_hsv_<BOEK>_<H>.json` **met de Read-tool** — niet via
`cat` / `python3 -c "... print"` / `jq` naar stdout; dat echoot de hele
diff de orchestratorcontext in. Per batch-vers extract
`{verse_number, sv2026, hsv, original}`. **Strip `<HSV: …>` en
`<HSV-aant: …>` blokken** uit het `hsv`-veld vóór vergelijking — dat zijn
HSV-vertalersaantekeningen (vergelijkbaar met onze
`<kanttekening>`-axis), géén vertaalde hoofdtekst. Findings die over
inhoud uit die blokken gaan, zijn ongeldig. Bewaar het opgeschoonde
HSV-vers in werkgeheugen voor Stap 3 (categorie 4).

## Stap 3 — review per vers

Voor elk vers: doorloop de checklist hieronder met de tekst zelf, het
vorige + volgende vers, en de top-3 concordantie-matches uit stap 2 in
het werkgeheugen.

### Herinnering aan de projectreikwijdte

Renovatie, géén hervertaling. SV-eigenheid blijft staan; alleen
archaïsche schil eraf. Niet NBV21- / HSV-stijl. Geen vlotte parafrases,
geen toevoegingen, geen weglatingen. Formele equivalentie t.o.v. de
Textus Receptus blijft leidend.

### NIET flaggen (al elders gevalideerd of bewuste keuze)

- Hoofdletter-keuzes (`Heere`, `Apostel`, `Geest`, `Christelijke Kerk`)
  — `sv-validate` dekt
- Kanttekening-conventies (`D.→dat is`, `Gr.→Grieks:`, `Hebr.→Hebreeuws:`,
  `Namelick→Namelijk`, `Ofte→Of`, `Siet→Zie`) — `sv-validate` dekt
- Bijbelref-formaat `$Boek H:V$` — `sv-bibref` dekt
- Spellings-modernisaties (`Ende→En`, `Godt→God`, `Sone→Zoon`,
  `daer→daar`, …) — validator-blacklist dekt
- Vierkante haken `[…]` (zelfde aantal en positie) — `sv-validate` dekt
- Plechtige maar herkenbare woorden (`zich verblijden`, `voorzeker`,
  `opdat`, `gewis`) — alleen flaggen als ze écht onbegrijpelijk zijn
  voor een 21e-eeuwse lezer
- `Heere` i.p.v. `Heer` — SV-keuze, niet voorstellen
- Stilistische variatie (bv. `hebben` vs. `er zal zijn` bij datief-bezit)
  — als de SV de gekozen constructie ook gebruikt, blijft die staan

### WEL flaggen (alleen high-confidence)

1. **False friends** — modern NL woord betekent iets anders dan
   SV1657 / Grieks:
   - `ontroerd` nu = geraakt door emotie; SV/Gr. `ταράσσω` = ontsteld
   - `vervolgens` nu = daarna; SV `καθεξῆς` = in volgorde / op een rij
   - `gemeen` nu = vulgair; SV = gewoon / algemeen
   - `dagorde` nu = agenda; SV = priesterafdeling / dienstbeurt
   - `rechten` nu = juridische rechten; SV `δικαιώματα` = verordeningen
   - `ergernis (geven)` nu = irritatie; SV `σκάνδαλον` = struikelblok

2. **Idiomatische mismatches** — letterlijke vertaling die in modern Nederlands
   onleesbaar/onnatuurlijk klinkt EN waarvoor een SV-conforme
   alternatieve verwoording bestaat. Voorbeelden:
   - dubbele negatie `geen X noch Y` ↔ `noch X noch Y`
   - latinate participium `wandelend in …` ↔ finiet `ze wandelden in …`

   2a. **Dynamische equivalentie sluipt erin** — datief-bezit zoals
   `u sal blijdtschap … zijn` mag NIET worden `u zult … hebben`
   (eigenaarsperspectief = NBV21-stijl, valt buiten de reikwijdte). Bewaar
   `voor u zal er … zijn`. Severity: hoog.

3. **Concordantie-twijfel** — modernisatie wijkt af van wat de SV
   elders voor hetzelfde Grieks gebruikt. **Onderbouw met de
   concordantie-matches uit Stap 2**; zonder match-evidentie géén
    bevinding.

4. **HSV-spiegel — taalfouten + drempel.** Voor elk vers waar
   `sv2026 ≠ hsv` (inhoudelijk, niet karakter-voor-karakter, en na
   het strippen van `<HSV: …>` / `<HSV-aant: …>` blokken in Stap
   2.5.3): vergelijk de twee en pas onderstaande beslisboom toe. De
   HSV is **geen autoriteit** en bovendien **vrijer** dan een
   formeel-equivalente parallel: haar afwijkingen *suggereren* een
   issue dat je onafhankelijk verifieert tegen SV1657 + Grieks.
    HSV-bewijs alleen is nooit genoeg om een wijziging te veroorzaken —
   altijd doortrekken naar SV1657 + Grieks om uit te sluiten dat de
    HSV exegetiseert of parafraseert waar wij correct conservatief
   blijven.

    **4a. Echte fout in onze modernisatie (flag met hoge zekerheid → wijziging).**
   HSV's keuze legt een fout in onze tekst bloot, EN die fout is ook
   onafhankelijk verifieerbaar tegen SV1657 / Grieks:

   - **Taalfout / grammaticaal**: getal-congruentie (enkelvoud/meervoud
     op werkwoord of pronomen), persoon-congruentie, naamval-fout in
     voornaamwoord, foute voegwoord-keuze die de zinsstructuur breekt,
     woordvolgorde die de zin onleesbaar maakt.
   - **Lexicale fout**: woord betekent in modern NL aantoonbaar iets
     anders dan SV1657 / Grieks bedoelde, en HSV kiest een
     semantisch-correct alternatief (overlap met false-friends-
     categorie 1, maar nu specifiek door HSV onthuld). Verifieer
      altijd: neem HSV's woord niet over als HSV een exegetische glosse
     toevoegt of een algemener begrip kiest dat de SV-specificiteit
     verliest.
   - **Semantische misinterpretatie**: subject/object verwisseld,
     ontkenning weggevallen of toegevoegd, tijd of modus van
     werkwoord veranderd t.o.v. SV1657.

   Drempel: ≥80% zeker dat het een fout is — niet "andere stijlkeuze".
    HSV-bewijs + onafhankelijke SV1657/Grieks-bevestiging zijn beide
   nodig. Bij twijfel: laat staan + documenteer in `notes`.

   **4b. Drempel-archaïsme dat HSV modern oplost (high-confidence
    flag → wijziging).** HSV vervangt een woord/constructie die volgens
   `MODERNISATIE.md §2.7` niet meer productief is in modern Nederlands,
   zonder zinsbouw of inhoud aan te tasten. Klassieke voorbeelden:
   `vertoefde` → `bleef`, `hoedanig` → `hoe`, `aanschouwers` →
   `getuigen`. Pas alleen aan als:

   - SV-zinsbouw blijft staan (geen herbouw rond een ander
     hoofdwerkwoord, geen HSV-stijl herstructurering),
   - inhoud verandert niet (geen toegevoegde of weggelaten betekenis,
      geen dynamische equivalentie, geen exegetische glosse die HSV
     vaak meebrengt),
   - de HSV-keuze valt binnen onze reikwijdte (zie 4c),
   - de productiviteits-test uit `MODERNISATIE.md §2.7` zelfstandig
     geldt voor het SV1657-woord — niet "HSV kiest moderner, dus ons
     woord moet weg".

   **4c. NIET overnemen van HSV — expliciet uitsluiten** (geen flag,
    geen wijziging, niet noteren). Deze keuzes zijn projectbeleid en
   blijven bewust afwijken. De lijst is **breder** dan voor SV2027,
   omdat HSV vrijer vertaalt:

   - **Hoofdletter-keuzes**: HSV draait of voegt soms
     eerbiedshoofdletters toe / haalt ze weg. Wij volgen het
     SV1657-patroon.
   - **Kanttekening-omvang**: HSV's eigen kanttekeningen
     (`<HSV: …>` / `<HSV-aant: …>`) zijn HSV-translator-aantekeningen,
      **geen bewijsbasis** voor onze SV-kanttekeningen. Negeren —
     ook als HSV daar precies het woord verklaart waar wij over
     twijfelen.
   - **Parafrase / dynamische equivalentie**: HSV herstructureert
     regelmatig SV-zinsbouw voor leesbaarheid (b.v. lange genitief-
     constructies opbreken in twee zinnen). Wij blijven formele
     equivalentie volgen — geen herstructurering.
    - **Exegese in de hoofdtekst**: HSV vult vaak het object of subject in
     dat in SV1657 elliptisch is, of voegt een verklarend bijvoeglijk
     naamwoord toe ("hij zocht Hem [Jezus]"). **Nooit overnemen** —
     dit is precies wat wij niet doen (zie `MODERNISATIE.md §3.4`).
   - **Structurele herbouw**: HSV zet latinate participia
     (`λέγων` / "zeggende") soms om naar een finiet werkwoord met
     nieuwe hoofdzin. Wij bewaren de participium-constructie als de
     SV dat doet (binnen §2.3-grenzen).
   - **Passief expliciteren waar SV-constructie modern werkt.** HSV
     maakt soms een Griekse passief expliciet ("genoemd worden") waar
     de SV een werkwoord koos dat in modern NL nog intransitief
     functioneert ("heten"). Niet overnemen — dat is hervertaling,
     geen renovatie. Voorbeeld: Lk. 1:60 SV `hy sal Ioannes heeten`
     → ons `hij zal Johannes heten`, niet HSV's `genoemd worden` (Gr.
     `κληθήσεται` is passief, maar modern `heten` is productief).
     Geldt ook als een naburig vers wél een expliciete passief heeft
     (v. 61 `genaemt wort` → `genoemd wordt`): SV's eigen variatie
     tussen naburige verzen bewaren we. Zie `MODERNISATIE.md §3.1a`.
   - **Moderner lexicaal register**: HSV gebruikt incidenteel een
     register-verlaging (`heel veel` waar SV `vele` heeft, `bang
     worden` waar SV `vervaard worden` heeft). Alleen aanpassen als
     het SV-woord zelf de productiviteits-test van §2.7 niet haalt,
     niet omdat HSV moderner klinkt.
   - **Vierkante haken `[…]`**: HSV's haken markeren *HSV-translator*-
     toevoegingen, niet SV1657-translator-toevoegingen. De positie en
     inhoud verschillen daarom systematisch. Wij bewaren onze haken
     byte-aanwezig op zelfde plekken als SV1657 — HSV-haken zijn
     irrelevant.
    - **Verwijzingsformaat / introstijl**: vallen onder eigen regelbestand
     (`sv-bibref`, `INTRO_EPILOOG.md`). HSV heeft sowieso geen aparte
     intro/epiloog (zie 2.5.2).

### Anti-hallucinatieprotocol — VERPLICHT

Voorkom hallucinaties met deze vier controles vóór elke bevinding:

1. **Citaat-controle.** Elke bevinding moet gekoppeld zijn aan een
   EXACTE substring uit de modernisatie (woord-voor-woord, inclusief
   hoofdletters/leestekens). Als je probleem of suggestie gaat over een
   woord/zinsdeel dat niet woord-letterlijk in de modernisatie
   voorkomt: laat het weg. Je leest dan iets dat er niet staat.

2. **SV-bevestiging.** Voor een idiomatic- of concordantie-suggestie
   die de modernisatie naar een andere constructie wil veranderen:
   verifieer dat jouw voorgestelde vorm NIET al in de SV-tekst zelf
   staat. Als de SV bv. zelf `sal hebben` gebruikt en jij wilt
   `zal hebben` veranderen in `zal zijn` — laat de bevinding weg. De
   modernisatie volgt dan de SV correct.

3. **Spelling-checks doen we niet.** Spelling van het type
   `voorgaende→voorgaande`, `gegaen→gegaan` is door de validator gedekt.
   Geef hier nooit bevindingen over.

4. **Twijfel = weglaten.** Eén scherpe bevinding > drie zachte. Streef
   naar nul bevindingen als de modernisatie correct is.

5. **Diff-citaat-controle (alleen voor categorie 4).** Bij elke 4a- of
   4b-bevinding: citeer zowel onze `sv2026` als HSV's `hsv` letterlijk
   uit `docs/diff_hsv_<BOEK>_<H>.json` (en in de quote van `hsv`:
   strip de `<HSV: …>` / `<HSV-aant: …>` blokken zoals in Stap 2.5.3,
   anders haal je translator-aantekeningen mee als bewijs). Als één
   van beide niet woordelijk in de diff staat: laat de bevinding
   weg. Voorkomt "ik dacht dat de HSV zou schrijven X"-hallucinaties.

**Kalibratie:** geef alleen bevindingen waar je ≥80% zeker bent dat ze
actie vereisen. "Geen actiepunten" is een volledig acceptabele —
sterker, gewenste — uitkomst.

## Stap 3.7 — flagarbitrage (validatoroverrides)

`scripts/validate.py` is een regex-laag. Twee categorieën hard-flags
zijn aantoonbaar **kwetsbaar voor false-positives** bij geldige
parafrase of register-context, en worden door geen andere LLM-pass
nagekeken:

1. **Hoofdletter-discipline** (`hoofdletter-discipline (hoofdtekst)` /
   `hoofdletter-discipline (kanttekening)` — hoofdletterwisseling = harde fout;
   `hoofdletter (...)` = soft warning). False-positief wanneer de SV-cap
   verdwijnt door bewuste herformulering die `SPELLING_EQUIV` niet
   overbrugt (4-letter-prefix-match + soft-substituties), niet door
   case-discipline-fout.
2. **Participium-discipline §2.3** (`§2.3-participium '...'` voor
   `PARTICIPLE_ALWAYS_BAD_ENDE`, `PARTICIPLE_CONTEXT_ENDE` met directe-
   volger-lookahead, of `PARTICIPLE_BAD_END_STEMS`). False-positief
   wanneer het participium een direct-rede-formule is (Gr. `λέγων`, SV
   "zeggende") of attributief gebruikt — geen adverbiale clause.

Andere validatorflags (kanttekeningaantal, vierkante haken, bijbelverwijzings-
formaat, archaïsme-blacklist, source_text-onveranderlijkheid) zijn **niet**
geschikt voor arbitrage — die zijn deterministisch en kennen geen geldige
parafrase-uitzondering.

### 3.7.1 Validator-output ophalen

De orchestrator heeft validator al gedraaid (orchestrator-Stap 3 item
2). Lees de in-context JSON-output. Niet aanwezig of onleesbaar?
Draai gericht opnieuw voor de batchverzen:

```bash
uv run python scripts/validate.py check \
    --input input.sv/<BOEK>/<BOEK>.<H>.json \
    --output output/<BOEK>/<BOEK>.<H>.json --verses <V_START>,...,<V_EIND>
```

Pak per vers de issues + warnings; filter op de twee arbitrage-prefixen
hierboven. Geen flags in die categorieën → sla 3.7 over (niets te doen).

### 3.7.2 Arbitrage-beslissing per flag

Voor elke arbitrage-eligible flag, beslis **op basis van de
modernisatie-tekst, het SV1657-origineel en de Griekse brontekst** of
de regex terecht of onterecht klaagt. Twee uitkomsten:

- **`confirmed`**: regex heeft gelijk. Geen verandering aan flag-status;
  pas de standaardfix toe (zie Stap 4) of laat de orchestrator over de blokker
  beslissen.
- **`overruled`**: regex heeft een false-positive. Documenteer met
  motivatie. De orchestrator behandelt overruled-flags **niet** als
  blokker (zie `sv-batch-orchestrate` Stap 3 item 2 + Stap 4).

Overridecriteria — restrictief:

- **Hoofdletter-flag overruled** alleen als: (a) het SV-cap-woord komt
  niet meer voor in de modernisatie omdat de zinsstructuur is
  herbouwd (bv. nominalisatie → werkwoord, of relatieve bijzin
  geherformuleerd), én (b) de informatie van het cap-woord is
  semantisch behouden in de moderne formulering, én (c) de
  modernisatie introduceert geen NIEUWE eerbiedshoofdletter elders.
  Niet overrulen als het simpelweg een spelling-variant is die
  `SPELLING_EQUIV` toevallig mist — dan: geen override, voeg de variant
  toe aan `SPELLING_EQUIV` (regelbestandfix in `validate.py`).
- **Participium-flag overruled** alleen als: (a) het participium staat
  in een direct-rede-introductie-formule (`λέγων` / `zeggende` /
  `antwoordende` als directe spraak-aankondiging) die SV-conform
  bewaard blijft, óf (b) attributief gebruikt (geen komma erna, geen
  voorzetsel, modificeert direct een NP) — voor categorie B/C waar de
  regex toch flagde. Niet overrulen voor PARTICIPLE_ALWAYS_BAD_ENDE
  (`zijnde`, `hebbende`, `wordende`, ...) — die zijn altijd
  buiten de reikwijdte van §2.3, ongeacht context.

### 3.7.3 Anti-hallucinatie — arbitrage-specifiek

- **Arbitrage kan alleen flags negeren, nooit nieuwe issues
  toevoegen.** Nieuwe semantische bevindingen horen bij Stap 3.1–3.6.
- **Citaat-controle**: noem in de motivatie het exacte woord uit de
  modernisatie (of, bij hoofdletter-overrule, het exacte woord uit het
  SV-origineel dat *niet* meer in de modernisatie staat).
- **Twijfel = `confirmed`.** Uitgangspunt = de regex heeft gelijk. Override
  alleen bij ≥80% zekerheid dat het een geldige reikwijdte-uitzondering is.
- **Geen ketting-overrides**: één override per flag, geen
  meta-overrides van eerder gedocumenteerde arbitrage-resultaten.

### 3.7.4 Output

De arbitrage-resultaten gaan naar het eindverslag (Stap 5) als aparte
`Flag-arbitrage`-sectie. Format per regel:

```
- vers <N> [<flag-categorie>]: regex zegt "<exact-flag-citaat>".
  Arbiter: <confirmed|overruled> — <motivatie ≥40 tekens, met
  woordcitaat + reikwijdteverwijzing>.
```

## Stap 4 — actie per bevinding

| Type bevinding | Actie |
|---|---|
| False friend (hoge zekerheid, eenmalig) | Bewerk het vers in `output/<BOEK>/<BOEK>.<H>.json`. Bij een echt nieuw patroon: voeg het woord toe aan de False-friends-tabel in `ARCHAISMEN.md`. |
| False-friendpatroon dat ≥2× in deze batch voorkomt | Alle voorkomens corrigeren + `ARCHAISMEN.md` aanvullen + overweeg uitbreiding van `FALSE_FRIENDS` in `scripts/lint_false_friends.py`. |
| Idiomatische mismatch (hoge zekerheid) | Bewerk het vers. Bij binnensluipende dynamische equivalentie (2a): streng vasthouden aan datief-bezit-vorm. |
| Concordantietwijfel met match-bewijs | Bewerk het vers naar de SV-conforme woordkeuze uit de concordantiematch. |
| Concordantietwijfel zonder match-bewijs | Geen wijziging — bevinding wordt niet gerapporteerd. |
| Bewuste keuze die SV-concordantie breekt (bv. een false-friend-correctie elders) | Geen wijziging — documenteer in `notes`-veld van dat vers in de uitvoer-JSON. |
| 4a. HSV onthult taalfout / lexicale fout / semantische misser (eenmalig, EN onafhankelijk bevestigd tegen SV1657/Grieks) | Bewerk het vers; documenteer kort in `notes` met motivatie + verwijzing "HSV-spiegel". |
| 4a-patroon dat ≥2× voorkomt over batches | False friend → vermelding in de False-friends-tabel van `ARCHAISMEN.md` + woord toevoegen aan `FALSE_FRIENDS` in `scripts/lint_false_friends.py`. Grammaticaal patroon → korte aantekening in `MODERNISATIE.md §2.7` of de syntactische sectie van `ARCHAISMEN.md`. |
| 4b. Drempel-archaïsme dat HSV modern oplost (eenmalig) | Bewerk het vers. Documenteer in `notes` dat de wijziging door de HSV-spiegel is ingegeven (drempel-§2.7). |
| 4b-patroon dat ≥2× voorkomt over batches | Woord → blacklist-uitbreiding in `scripts/validate.py` + vermelding in de archaïsmetabel van `ARCHAISMEN.md` + terugwerkende linter via `lint_archaismen.py lint --root output/`. Constructiepatroon → kort voorbeeld in `MODERNISATIE.md §2.7` of `ARCHAISMEN.md §2.3b`. |
| 4c. HSV wijkt af op hoofdletters / kanttekening / parafrase / exegese in hoofdtekst / structurele herbouw / lexicaal register / vierkante haken | Geen actie. Niet noteren in `notes`; orchestrator-eindverslag mag het in aggregaat melden. |

Pas wijzigingen **direct toe** via de Edit-tool, géén tussen-JSON en
**géén inline `python3 -c "... json.dump ..."`-edit**. Een
Edit-tool-aanroep stuurt alleen de diff; een inline-python-edit echoot
het script verbatim de orchestratorcontext in én omzeilt de
Edit-tool-uniciteitscheck. Na elk gewijzigd vers:

1. Update `output/<BOEK>/<BOEK>.<H>.json` (vers + evt. `notes`).
2. Draai de validator opnieuw op het gewijzigde vers:
   ```bash
   uv run python scripts/validate.py check \
       --input input.sv/<BOEK>/<BOEK>.<H>.json \
       --output output/<BOEK>/<BOEK>.<H>.json --verses <N> --terse
   ```
   Hard issue → corrigeer; max 3 iteraties per vers.
3. Draai `lint_false_friends.py lint --root output/ --terse` opnieuw om
   te bevestigen dat de regelbestandupdate niet met terugwerkende kracht
   eerdere verzen markeert.
4. Update memory voor het gewijzigde vers (upsert — overschrijft
   embedding + tekst):
   ```bash
   uv run python scripts/memory.py add \
       --from-output output/<BOEK>/<BOEK>.<H>.json --verse <N> --terse
   ```

## Stap 5 — eindverslag

Korte rapportage voor de orchestrator (3-6 regels, of langer als de
    HSV-spiegel regelbestandwijzigingen heeft veroorzaakt). Vermeld per vers wat
er is gedaan plus een HSV-spiegel-regel waar de spiegel actief was.
Sluit af met een `Flag-arbitrage`-blok als Stap 3.7 actief was
(arbitrage-eligible flags aanwezig); laat het blok weg als geen
hoofdletter- of participium-flags rapporteerden. Format:

```
Semantic-review LUK 1:11-13:
- vers 11: geen actiepunten; HSV-spiegel: geen issue
- vers 12: 1 false-friend correctie ('ontroerd' → 'ontsteld');
  ARCHAISMEN.md uitgebreid; HSV-spiegel: idem (bevestiging)
- vers 13: 1 HSV-gestuurde wijziging ('vertoefde' → 'bleef', drempel-§2.7);
  regelbestand: woord op validate.py-blacklist + ARCHAISMEN.md

Flag-arbitrage:
- vers 12 [§2.3-participium]: regex zegt "zeggende".
  Arbiter: overruled — direct-rede-introductie (λέγων), SV-conform
  bewaard; geen bijwoordelijke bepaling. Niet als blokker behandelen.
- vers 13 [hoofdletter-discipline]: regex zegt "Apostelen" hoofdletterwisseling.
  Arbiter: confirmed — modernisatie schrijft "apostelen" zonder
  herstructurering; hoofdletter hersteld in bovenstaande wijziging.
```

Of bij nul bevindingen over de hele range:

```
Semantic-review LUK 1:11-13: geen actiepunten over alle 3 verzen
(HSV-spiegel: geen issues).
```

Bij ontbrekende concordantie-context (memory leeg of API-fout):

```
Semantic-review LUK 1:11-13 (zonder concordantie — DB leeg):
- vers 11: geen actiepunten; HSV-spiegel: geen issue
- vers 12: 1 false-friend correctie ('ontroerd' → 'ontsteld')
- vers 13: geen actiepunten
```

Bij ontbrekende HSV-spiegel (bestand of script faalde):

```
Semantic-review LUK 1:11-13 (zonder HSV-spiegel —
hsv/LUK/LUK.1.json ontbreekt):
- vers 11: geen actiepunten
- ...
```

## Foutgevallen

- **Output-bestand ontbreekt**: stop met duidelijke melding aan
  orchestrator. Geen wijzigingen.
- **Vers buiten range bestaat niet in output**: rapporteer welke
  verzen wel/niet aanwezig zijn; review alleen de aanwezige.
- **Edit kan niet uniek matchen**: rapporteer als blokker — vermoedelijk
  rare staat van de output-JSON. Niet forceren met `replace_all`.
- **Validator faalt na correctie en blijft falen na 3 nieuwe pogingen**: noteer
  als harde blokker in eindverslag; orchestrator besluit over rollback /
  stop.
- **`compare_hsv.py` faalt of `hsv/<BOEK>/<BOEK>.<H>.json` ontbreekt**:
  sla de HSV-spiegel volledig over voor deze batch, vermeld in het
  eindverslag. Géén blokker — de overige beoordelingscategorieën
  (false-friend, idiomatic, concordantie) draaien gewoon.
- **HSV-wijziging zou een 4c-grens overschrijden** (hoofdletters, kanttekening,
  parafrase, exegese in de hoofdtekst, structurele herbouw, lexicaal
  register, vierkante haken): geen wijziging, geen bevinding. Zwijgend
  passeren — dat is bewust beleid.
